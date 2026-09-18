"""
Stage 4 Evaluation & Integrity Tests
Tests the components of the core Trust-Aware Agent pipeline:
Intent, Retrieval, Resolution Extraction, and Trust Layer.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from pipeline.intent_classifier import ProductionIntentClassifier
from pipeline.retriever import HistoricalEvidenceRetriever
from pipeline.resolution_extractor import HistoricalResolutionExtractor
from pipeline.trust_layer import TrustEvaluator

# Fixtures
_classifier = None
_retriever = None
_extractor = None
_trust = None

def _setup():
    global _classifier, _retriever, _extractor, _trust
    if _classifier is None:
        model_path = os.path.join(BASE_DIR, "baselines", "baseline2_model.joblib")
        train_path = os.path.join(BASE_DIR, "data", "splits", "train.csv")
        
        _classifier = ProductionIntentClassifier(model_path)
        _retriever = HistoricalEvidenceRetriever(train_path)
        _extractor = HistoricalResolutionExtractor()
        _trust = TrustEvaluator()

def test_intent_ambiguity():
    _setup()
    # 4A - Ensure ambiguity logic catches tight margins
    res = _classifier.predict("it froze") # Usually generic or hardware
    assert 'is_ambiguous' in res
    assert 'margin' in res

def test_retrieval_quality_and_leakage():
    _setup()
    # 4B - Test retrieval and leakage prevention
    query = "my screen is broken and frozen"
    
    # Normal retrieval
    res_normal = _retriever.retrieve(query, top_k=5)
    assert len(res_normal) <= 5
    assert res_normal[0]['similarity_score'] > 0
    
    # Test leakage prevention by excluding the top result's ID
    top_id = res_normal[0]['customer_tweet_id']
    res_excluded = _retriever.retrieve(query, top_k=5, exclude_tweet_ids={top_id})
    assert top_id not in [r['customer_tweet_id'] for r in res_excluded], "Leakage prevention failed!"

def test_resolution_extraction():
    _setup()
    # 4C - Extract resolutions correctly
    evidence = [
        {'brand_response': 'DM us to look into this.'},
        {'brand_response': 'Please send a DM.'},
        {'brand_response': 'Try restarting your device.'}
    ]
    res = _extractor.aggregate_resolutions(evidence)
    assert res['dominant_action'] == 'routes_to_dm'
    assert res['consistency_score'] == (2/3)
    assert res['is_consistent'] == True # 66% >= 60%

def test_resolution_inconsistent():
    _setup()
    # 4C - Extract resolutions correctly
    evidence = [
        {'brand_response': 'DM us to look into this.'},
        {'brand_response': 'Here is a link https://t.co/abc'},
        {'brand_response': 'Try restarting your device.'}
    ]
    res = _extractor.aggregate_resolutions(evidence)
    assert res['is_consistent'] == False # 33% < 60%

def test_trust_layer_high_risk():
    _setup()
    # 4E - Trust should escalate high risk intents regardless of other signals
    i_signal = {'predicted_intent': 'BILLING_AND_SUBSCRIPTIONS', 'confidence': 0.99, 'is_ambiguous': False}
    r_signal = [{'similarity_score': 0.99}]
    res_signal = {'is_consistent': True}
    
    t = _trust.evaluate(i_signal, r_signal, res_signal)
    assert t['decision'] == 'ESCALATE_TO_HUMAN'
    assert 'High risk' in t['reason']

def test_trust_layer_low_sim():
    _setup()
    # 4E - Low similarity should escalate
    i_signal = {'predicted_intent': 'SOFTWARE_OS_UPDATE', 'confidence': 0.99, 'is_ambiguous': False}
    r_signal = [{'similarity_score': 0.10}] # Very low
    res_signal = {'is_consistent': True}
    
    t = _trust.evaluate(i_signal, r_signal, res_signal)
    assert t['decision'] == 'ESCALATE_TO_HUMAN'
    assert 'Insufficient historical precedent' in t['reason']

def test_trust_layer_auto_handle():
    _setup()
    # 4E - Good signals should automate
    i_signal = {'predicted_intent': 'BATTERY_AND_POWER', 'confidence': 0.95, 'is_ambiguous': False}
    r_signal = [{'similarity_score': 0.85}]
    res_signal = {'is_consistent': True}
    
    t = _trust.evaluate(i_signal, r_signal, res_signal)
    assert t['decision'] == 'AUTO_HANDLE'

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS: {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {fn.__name__} - {e}")
            
    print(f"\n{passed}/{len(tests)} tests passed.")
