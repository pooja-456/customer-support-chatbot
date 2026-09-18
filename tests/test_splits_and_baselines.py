"""
tests/test_splits_and_baselines.py — Stage 3 Pipeline Integrity Tests

Covers:
  a) Row counts for train / val / test / golden splits
  b) All 7 leakage assertions (no author overlap across splits and golden set)
  c) Baseline 1 produces non-null predictions for all 200 golden rows
  d) Baseline 2 model loads from joblib and produces valid predictions

Run:
    python -m pytest tests/test_splits_and_baselines.py -v
  or:
    python tests/test_splits_and_baselines.py
"""

import os
import sys
import json

# ---------------------------------------------------------------------------
# Path setup — all paths resolved relative to the project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPLITS_DIR   = os.path.join(PROJECT_ROOT, "data", "splits")
EVAL_DIR     = os.path.join(PROJECT_ROOT, "evaluation")
BASELINES_DIR = os.path.join(PROJECT_ROOT, "baselines")

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, BASELINES_DIR)

import pandas as pd

# ---------------------------------------------------------------------------
# Fixtures / data loaded once
# ---------------------------------------------------------------------------
_df_train  = None
_df_val    = None
_df_test   = None
_df_golden = None

def _load_splits():
    global _df_train, _df_val, _df_test, _df_golden
    if _df_train is None:
        _df_train  = pd.read_csv(os.path.join(SPLITS_DIR, "train.csv"))
        _df_val    = pd.read_csv(os.path.join(SPLITS_DIR, "validation.csv"))
        _df_test   = pd.read_csv(os.path.join(SPLITS_DIR, "test.csv"))
        _df_golden = pd.read_csv(os.path.join(EVAL_DIR,   "golden_set.csv"))
    return _df_train, _df_val, _df_test, _df_golden


# ===========================================================================
# (a) Row-count tests
# ===========================================================================

def test_train_row_count():
    """Train split must have ~72,862 rows (±5% tolerance)."""
    df, _, _, _ = _load_splits()
    assert 69_000 <= len(df) <= 77_000, \
        f"Train size {len(df):,} outside expected range [69k, 77k]"

def test_val_row_count():
    """Validation split must have ~15,596 rows (±5% tolerance)."""
    _, df, _, _ = _load_splits()
    assert 14_800 <= len(df) <= 16_400, \
        f"Val size {len(df):,} outside expected range [14.8k, 16.4k]"

def test_test_row_count():
    """Test split must have ~15,587 rows (±5% tolerance)."""
    _, _, df, _ = _load_splits()
    assert 14_800 <= len(df) <= 16_400, \
        f"Test size {len(df):,} outside expected range [14.8k, 16.4k]"

def test_golden_row_count():
    """Golden evaluation set must have exactly 200 rows."""
    _, _, _, df = _load_splits()
    assert len(df) == 200, f"Golden set has {len(df)} rows; expected exactly 200"

def test_golden_all_7_intents_represented():
    """All 7 intent classes must appear at least once in the golden set."""
    _, _, _, df = _load_splits()
    expected = {
        "GENERAL_CHITCHAT_OR_FEEDBACK",
        "SOFTWARE_OS_UPDATE",
        "BATTERY_AND_POWER",
        "CONNECTIVITY_AND_SYNC",
        "ACCOUNT_AND_SECURITY",
        "HARDWARE_AND_AUDIO_SCREEN",
        "BILLING_AND_SUBSCRIPTIONS",
    }
    found = set(df["assigned_intent"].unique())
    missing = expected - found
    assert not missing, f"Missing intents in golden set: {missing}"


# ===========================================================================
# (b) Leakage assertions — no author_id shared across splits
# ===========================================================================

def _get_author_col(df):
    """Return the author-ID column regardless of split vs golden naming."""
    if "customer_author_id" in df.columns:
        return set(df["customer_author_id"].dropna().astype(str))
    return set()

def test_no_author_overlap_train_val():
    df_train, df_val, _, _ = _load_splits()
    overlap = _get_author_col(df_train) & _get_author_col(df_val)
    assert len(overlap) == 0, \
        f"Author leakage: {len(overlap)} IDs appear in both train AND val"

def test_no_author_overlap_train_test():
    df_train, _, df_test, _ = _load_splits()
    overlap = _get_author_col(df_train) & _get_author_col(df_test)
    assert len(overlap) == 0, \
        f"Author leakage: {len(overlap)} IDs appear in both train AND test"

def test_no_author_overlap_val_test():
    _, df_val, df_test, _ = _load_splits()
    overlap = _get_author_col(df_val) & _get_author_col(df_test)
    assert len(overlap) == 0, \
        f"Author leakage: {len(overlap)} IDs appear in both val AND test"

def test_no_author_overlap_golden_train():
    df_train, _, _, df_golden = _load_splits()
    g_authors = set(df_golden["customer_author_id"].dropna().astype(str))
    t_authors = _get_author_col(df_train)
    overlap = g_authors & t_authors
    assert len(overlap) == 0, \
        f"Author leakage: {len(overlap)} golden authors appear in train"

def test_no_author_overlap_golden_val():
    _, df_val, _, df_golden = _load_splits()
    g_authors = set(df_golden["customer_author_id"].dropna().astype(str))
    v_authors = _get_author_col(df_val)
    overlap = g_authors & v_authors
    assert len(overlap) == 0, \
        f"Author leakage: {len(overlap)} golden authors appear in val"

def test_no_author_overlap_golden_test():
    _, _, df_test, df_golden = _load_splits()
    g_authors = set(df_golden["customer_author_id"].dropna().astype(str))
    t_authors = _get_author_col(df_test)
    overlap = g_authors & t_authors
    assert len(overlap) == 0, \
        f"Author leakage: {len(overlap)} golden authors appear in test"

def test_all_splits_non_empty():
    """Each split must have at least 1 row (sanity guard)."""
    df_train, df_val, df_test, df_golden = _load_splits()
    for name, df in [("train", df_train), ("val", df_val),
                     ("test", df_test), ("golden", df_golden)]:
        assert len(df) > 0, f"Split '{name}' is empty!"


# ===========================================================================
# (c) Baseline 1 — non-null predictions on all 200 golden rows
# ===========================================================================

def test_baseline1_predicts_all_golden():
    """Baseline 1 (legacy fuzzy bot) must return a non-None prediction for every golden row."""
    from baseline1_fuzzy_rules import LegacyFuzzyBaseline
    _, _, _, df_golden = _load_splits()
    b1 = LegacyFuzzyBaseline()
    results, predictions = b1.evaluate(df_golden)
    assert len(predictions) == len(df_golden), \
        f"Baseline 1 produced {len(predictions)} predictions for {len(df_golden)} golden rows"
    none_count = sum(1 for p in predictions if p is None)
    assert none_count == 0, f"Baseline 1 returned {none_count} None predictions"

def test_baseline1_accuracy_reasonable():
    """Baseline 1 accuracy must be > 5% (i.e., non-trivially bad, but we expect ~22%)."""
    from baseline1_fuzzy_rules import LegacyFuzzyBaseline
    _, _, _, df_golden = _load_splits()
    b1 = LegacyFuzzyBaseline()
    results, _ = b1.evaluate(df_golden)
    assert results['accuracy'] > 0.05, \
        f"Baseline 1 accuracy {results['accuracy']:.4f} seems implausibly low (< 5%)"


# ===========================================================================
# (d) Baseline 2 — model loads and predicts correctly
# ===========================================================================

def test_baseline2_model_exists():
    """The serialised Baseline 2 joblib file must exist on disk."""
    model_path = os.path.join(BASELINES_DIR, "baseline2_model.joblib")
    assert os.path.isfile(model_path), f"Baseline 2 model not found at {model_path}"

def test_baseline2_model_loads_and_predicts():
    """Baseline 2 model must load from joblib and produce a valid prediction."""
    import joblib
    model_path = os.path.join(BASELINES_DIR, "baseline2_model.joblib")
    pipe = joblib.load(model_path)
    sample_texts = [
        "my iphone battery dies after 2 hours",
        "cannot connect to wifi keeps dropping",
        "forgot apple id password need to reset",
        "screen cracked need repair options",
        "how do I update to ios 16",
    ]
    preds = pipe.predict(sample_texts)
    assert len(preds) == len(sample_texts), "Model returned wrong number of predictions"
    valid_intents = {
        "GENERAL_CHITCHAT_OR_FEEDBACK", "SOFTWARE_OS_UPDATE", "BATTERY_AND_POWER",
        "CONNECTIVITY_AND_SYNC", "ACCOUNT_AND_SECURITY",
        "HARDWARE_AND_AUDIO_SCREEN", "BILLING_AND_SUBSCRIPTIONS"
    }
    for pred in preds:
        assert pred in valid_intents, f"Unexpected intent label: '{pred}'"

def test_baseline2_golden_accuracy():
    """Baseline 2 must achieve ≥85% accuracy on the golden set (we observed ~98%)."""
    import joblib
    model_path = os.path.join(BASELINES_DIR, "baseline2_model.joblib")
    pipe = joblib.load(model_path)
    _, _, _, df_golden = _load_splits()
    X = df_golden["customer_text"].astype(str)
    y = df_golden["assigned_intent"]
    preds = pipe.predict(X)
    correct = sum(p == t for p, t in zip(preds, y))
    accuracy = correct / len(y)
    assert accuracy >= 0.85, \
        f"Baseline 2 golden accuracy {accuracy:.4f} is below the 85% floor"

def test_baseline_results_json_exists():
    """evaluation/baseline_results.json must exist and contain all 3 baseline keys."""
    json_path = os.path.join(EVAL_DIR, "baseline_results.json")
    assert os.path.isfile(json_path), f"baseline_results.json not found at {json_path}"
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    for key in ("baseline_1_legacy_rules",
                "baseline_2_tfidf_logistic_regression",
                "baseline_2b_tfidf_linearsvc"):
        assert key in data, f"Missing key '{key}' in baseline_results.json"


# ===========================================================================
# Simple runner (pytest is preferred, but can run standalone)
# ===========================================================================
if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed, failed = 0, []
    for fn in tests:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
            failed.append(fn.__name__)
        except Exception as e:
            print(f"  ERROR {fn.__name__}: {type(e).__name__}: {e}")
            failed.append(fn.__name__)

    print(f"\n{passed}/{passed + len(failed)} tests passed.")
    if failed:
        print("Failed:", failed)
        sys.exit(1)
    else:
        print("All tests passed.")
