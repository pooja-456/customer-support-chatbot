"""
Stage 4B: Historical Evidence Retriever
Indexes the training split using TF-IDF and uses Cosine Similarity to retrieve
the most relevant historical customer-brand interactions.
Prevents evaluation leakage by optionally excluding specific tweet IDs.
"""
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

class HistoricalEvidenceRetriever:
    def __init__(self, train_csv_path, force_rebuild=False):
        self.train_csv_path = train_csv_path
        
        # We can cache the vectorizer and TF-IDF matrix for speed, but for this task 
        # fitting in memory is extremely fast. We'll do it on initialization if cache doesn't exist.
        self.cache_path = os.path.join(os.path.dirname(train_csv_path), "retriever_cache.pkl")
        
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        
        self._load_or_build_index(force_rebuild)

    def _load_or_build_index(self, force_rebuild):
        if not force_rebuild and os.path.exists(self.cache_path):
            print("Loading retriever index from cache...")
            with open(self.cache_path, 'rb') as f:
                cache = pickle.load(f)
                self.df = cache['df']
                self.vectorizer = cache['vectorizer']
                self.tfidf_matrix = cache['tfidf_matrix']
        else:
            print("Building retriever index from training split...")
            self.df = pd.read_csv(self.train_csv_path)
            # Ensure no NaNs in text
            self.df['customer_text_clean'] = self.df['customer_text_clean'].fillna('')
            
            # Build TF-IDF
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
            self.tfidf_matrix = self.vectorizer.fit_transform(self.df['customer_text_clean'])
            
            # Cache it
            with open(self.cache_path, 'wb') as f:
                pickle.dump({
                    'df': self.df,
                    'vectorizer': self.vectorizer,
                    'tfidf_matrix': self.tfidf_matrix
                }, f)

    def retrieve(self, query_text, top_k=5, exclude_tweet_ids=None):
        """
        Retrieves Top-K historically similar interactions.
        exclude_tweet_ids: list/set of tweet IDs to ignore (prevents evaluation leakage)
        """
        if not query_text:
            return []
            
        # Vectorize query
        query_vec = self.vectorizer.transform([query_text])
        
        # Calculate cosine similarity with all training examples
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Sort descending
        sorted_indices = np.argsort(similarities)[::-1]
        
        results = []
        if exclude_tweet_ids is None:
            exclude_tweet_ids = set()
        else:
            exclude_tweet_ids = set(exclude_tweet_ids)
            
        for idx in sorted_indices:
            if len(results) >= top_k:
                break
                
            sim_score = float(similarities[idx])
            
            # Early stop if similarity drops to 0
            if sim_score == 0.0:
                break
                
            row = self.df.iloc[idx]
            tweet_id = str(row.get('customer_tweet_id', ''))
            
            if tweet_id in exclude_tweet_ids:
                continue
                
            results.append({
                'customer_tweet_id': tweet_id,
                'customer_message': row.get('customer_text_raw', ''),
                'brand_response': row.get('brand_text_raw', ''),
                'similarity_score': sim_score,
                'intent': row.get('intent', 'UNKNOWN'),
                'thread_type': row.get('thread_type', 'UNKNOWN')
            })
            
        return results

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_path = os.path.join(base_dir, "data", "splits", "train.csv")
    
    retriever = HistoricalEvidenceRetriever(train_path)
    
    test_q = "My iphone battery dies in 2 hours since I updated to iOS 11"
    print(f"\nQuery: {test_q}\n")
    
    results = retriever.retrieve(test_q, top_k=3)
    for i, r in enumerate(results):
        print(f"--- Rank {i+1} (Sim: {r['similarity_score']:.3f}) ---")
        print(f"Customer: {r['customer_message']}")
        print(f"Brand:    {r['brand_response']}")
        print(f"Intent:   {r['intent']}\n")
