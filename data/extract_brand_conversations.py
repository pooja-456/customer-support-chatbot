"""
data/extract_brand_conversations.py - AppleSupport Conversation Extraction Pipeline

Workflow:
twcs.csv -> AppleSupport filtering -> conversation/thread reconstruction ->
customer->brand interaction extraction -> cleaning -> deduplication -> structured output

Preserves all source tweet IDs so every training/evaluation example can be
audited and traced back to the original Kaggle Customer Support dataset.
"""

import os
import sys
import io
import time
import json
import re
from collections import defaultdict, Counter
import pandas as pd

# UTF-8 stdout encoding for Windows PowerShell
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DEFAULT_DATASET_PATH = r"C:\Users\itsme\.cache\kagglehub\datasets\thoughtvector\customer-support-on-twitter\versions\10\twcs\twcs.csv"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_TARGET = "AppleSupport"

def clean_text(text):
    """Clean tweet text while preserving URLs, punctuation, and case structure."""
    if not isinstance(text, str):
        return ""
    # Strip user mentions like @AppleSupport or @115854
    cleaned = re.sub(r"@\w+", "", text)
    # Normalize excessive whitespaces and tabs
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def extract_applesupport_data(dataset_path=DEFAULT_DATASET_PATH, output_dir=OUTPUT_DIR):
    print("=" * 80)
    print(f"EXTRACTING & RECONSTRUCTING {BRAND_TARGET} CONVERSATIONS")
    print(f"Dataset path: {dataset_path}")
    print(f"Output directory: {output_dir}")
    print("=" * 80)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    start_time = time.time()

    # -------------------------------------------------------------
    # PASS 1: Identify AppleSupport outbounds and all parent tweet IDs
    # -------------------------------------------------------------
    print("\n[Pass 1/2] Scanning dataset for AppleSupport replies and parent tweet IDs...")
    brand_outbounds = []
    parent_ids_needed = set()
    total_rows = 0

    usecols = ['tweet_id', 'author_id', 'inbound', 'created_at', 'text', 'response_tweet_id', 'in_response_to_tweet_id']

    for chunk in pd.read_csv(dataset_path, chunksize=300000, usecols=usecols, low_memory=False):
        total_rows += len(chunk)
        apple_replies = chunk[(chunk['inbound'] == False) & (chunk['author_id'] == BRAND_TARGET)]

        for _, row in apple_replies.iterrows():
            tid = int(row['tweet_id'])
            pid = int(row['in_response_to_tweet_id']) if pd.notna(row['in_response_to_tweet_id']) else None
            txt = str(row['text']) if pd.notna(row['text']) else ""

            brand_outbounds.append({
                'brand_tweet_id': tid,
                'in_response_to_tweet_id': pid,
                'brand_created_at': row['created_at'],
                'brand_text_raw': txt
            })
            if pid is not None:
                parent_ids_needed.add(pid)

        sys.stdout.write(f"\r  Scanned {total_rows:,} rows... Found {len(brand_outbounds):,} AppleSupport replies.")
        sys.stdout.flush()

    print(f"\n  Pass 1 complete. Found {len(brand_outbounds):,} replies and {len(parent_ids_needed):,} parent tweets to fetch.")

    # -------------------------------------------------------------
    # PASS 2: Retrieve customer parent tweets
    # -------------------------------------------------------------
    print("\n[Pass 2/2] Fetching customer parent tweets...")
    customer_tweets = {}
    grandparent_ids_needed = set()

    for chunk in pd.read_csv(dataset_path, chunksize=300000, usecols=['tweet_id', 'author_id', 'inbound', 'created_at', 'text', 'in_response_to_tweet_id'], low_memory=False):
        matching = chunk[chunk['tweet_id'].isin(parent_ids_needed)]
        for _, row in matching.iterrows():
            tid = int(row['tweet_id'])
            pid = int(row['in_response_to_tweet_id']) if pd.notna(row['in_response_to_tweet_id']) else None
            customer_tweets[tid] = {
                'customer_tweet_id': tid,
                'customer_author_id': str(row['author_id']),
                'inbound': bool(row['inbound']),
                'customer_created_at': row['created_at'],
                'customer_text_raw': str(row['text']) if pd.notna(row['text']) else "",
                'grandparent_id': pid
            }
            if pid is not None:
                grandparent_ids_needed.add(pid)

        sys.stdout.write(f"\r  Fetched {len(customer_tweets):,} / {len(parent_ids_needed):,} parent tweets...")
        sys.stdout.flush()

    print(f"\n  Pass 2 complete. Retrieved {len(customer_tweets):,} parent tweets in {time.time() - start_time:.1f}s.")

    # -------------------------------------------------------------
    # CONVERSATION RECONSTRUCTION & INTERACTION EXTRACTION
    # -------------------------------------------------------------
    print("\nReconstructing conversation threads, cleaning text, and deduplicating...")
    interactions = []
    seen_hashes = set()
    duplicate_count = 0
    short_skipped = 0

    thread_lengths = Counter()

    for b in brand_outbounds:
        pid = b['in_response_to_tweet_id']
        if not pid or pid not in customer_tweets:
            continue

        c = customer_tweets[pid]
        # Verify it is inbound customer message
        if not c['inbound']:
            continue

        c_raw = c['customer_text_raw']
        b_raw = b['brand_text_raw']

        c_clean = clean_text(c_raw)
        b_clean = clean_text(b_raw)

        # Quality filtering: skip extremely short or empty queries
        if len(c_clean) < 10 or len(b_clean) < 10:
            short_skipped += 1
            continue

        # Check deduplication on normalized text hash
        pair_key = (c_clean.lower(), b_clean.lower())
        if pair_key in seen_hashes:
            duplicate_count += 1
            continue
        seen_hashes.add(pair_key)

        is_initial = c['grandparent_id'] is None
        thread_turn = "2_turns (Initial Q&A)" if is_initial else "3+_turns (Follow-up Thread)"
        thread_lengths[thread_turn] += 1

        interaction_record = {
            'interaction_id': f"apple_{b['brand_tweet_id']}",
            'customer_tweet_id': c['customer_tweet_id'],
            'customer_author_id': c['customer_author_id'],
            'customer_created_at': c['customer_created_at'],
            'customer_text_raw': c_raw,
            'customer_text_clean': c_clean,
            'brand_tweet_id': b['brand_tweet_id'],
            'brand_created_at': b['brand_created_at'],
            'brand_text_raw': b_raw,
            'brand_text_clean': b_clean,
            'in_response_to_tweet_id': pid,
            'is_initial_turn': is_initial,
            'thread_type': thread_turn
        }
        interactions.append(interaction_record)

    print(f"Extraction complete:")
    print(f"  Total valid interactions extracted: {len(interactions):,}")
    print(f"  Exact duplicates removed:           {duplicate_count:,}")
    print(f"  Too short/empty skipped:            {short_skipped:,}")
    print(f"  Thread turn breakdown:              {dict(thread_lengths)}")

    # -------------------------------------------------------------
    # SAVE OUTPUTS
    # -------------------------------------------------------------
    interactions_df = pd.DataFrame(interactions)
    csv_file = os.path.join(output_dir, "applesupport_interactions.csv")
    jsonl_file = os.path.join(output_dir, "applesupport_conversations.jsonl")
    summary_file = os.path.join(output_dir, "extraction_summary.json")

    interactions_df.to_csv(csv_file, index=False, encoding='utf-8')
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for item in interactions:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    summary = {
        'target_brand': BRAND_TARGET,
        'total_brand_outbounds_scanned': len(brand_outbounds),
        'total_parent_tweets_retrieved': len(customer_tweets),
        'usable_interactions_extracted': len(interactions),
        'duplicates_removed': duplicate_count,
        'short_skipped': short_skipped,
        'thread_lengths': dict(thread_lengths),
        'csv_output': csv_file,
        'jsonl_output': jsonl_file,
        'elapsed_seconds': round(time.time() - start_time, 2)
    }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print(f"SAVED FILES TO {output_dir}:")
    print(f"  1. CSV:   {csv_file} ({os.path.getsize(csv_file):,} bytes)")
    print(f"  2. JSONL: {jsonl_file} ({os.path.getsize(jsonl_file):,} bytes)")
    print(f"  3. JSON:  {summary_file}")
    print("=" * 80)

    return interactions_df, summary

if __name__ == "__main__":
    extract_applesupport_data()
