"""
Stage 6 Tests for Generator Interface and Fallbacks
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from pipeline.generator import BaseGenerator
from pipeline.retriever import HistoricalEvidenceRetriever
from pipeline.agent import TrustAwareAgent

def test_deterministic_generator_fallback():
    # Even if we request LLM, if no API key is present, it falls back cleanly
    # We explicitly remove the env vars if they exist for this test
    original_openai = os.environ.get("OPENAI_API_KEY")
    original_gemini = os.environ.get("GEMINI_API_KEY")
    if "OPENAI_API_KEY" in os.environ: del os.environ["OPENAI_API_KEY"]
    if "GEMINI_API_KEY" in os.environ: del os.environ["GEMINI_API_KEY"]
    
    generator = BaseGenerator(use_llm=True)
    res_agg = {'dominant_action': 'routes_to_dm', 'is_consistent': True}
    
    reply = generator.generate("hello", "GENERAL_CHITCHAT_OR_FEEDBACK", 0.9, [], res_agg)
    
    # Assert it gracefully fell back to the deterministic template
    assert "Direct Message" in reply
    
    # Restore
    if original_openai: os.environ["OPENAI_API_KEY"] = original_openai
    if original_gemini: os.environ["GEMINI_API_KEY"] = original_gemini

def test_escalation_produces_no_automated_response():
    # If the Trust Layer says ESCALATE, the agent should not output a generated response
    model_path = os.path.join(BASE_DIR, "baselines", "baseline2_model.joblib")
    train_path = os.path.join(BASE_DIR, "data", "splits", "train.csv")
    agent = TrustAwareAgent(model_path, train_path)
    
    # Force a high risk intent to trigger escalation
    out = agent.handle_message("I need to cancel my subscription and get a refund")
    
    assert out['trust_signal']['decision'] == 'ESCALATE_TO_HUMAN'
    assert out['generated_response'] == "[ESCALATED - NO AUTOMATED RESPONSE GENERATED]"

def test_evaluated_example_is_excluded_from_retrieval():
    train_path = os.path.join(BASE_DIR, "data", "splits", "train.csv")
    retriever = HistoricalEvidenceRetriever(train_path)
    
    q = "my screen is unresponsive"
    # First get the normal top result
    res1 = retriever.retrieve(q, top_k=1)
    if not res1:
        return # Skip if empty
    top_id = res1[0]['customer_tweet_id']
    
    # Now retrieve excluding that ID
    res2 = retriever.retrieve(q, top_k=1, exclude_tweet_ids=[top_id])
    assert res2[0]['customer_tweet_id'] != top_id

def test_evidence_is_passed_to_generator():
    # Verify the BaseGenerator signature accepts evidence
    generator = BaseGenerator(use_llm=False)
    # This shouldn't throw an exception
    generator.generate(
        customer_message="test",
        intent="SOFTWARE_OS_UPDATE",
        confidence=0.9,
        evidence=[{'customer_message': 'a', 'brand_response': 'b'}],
        resolution_agg={'dominant_action': 'requests_info', 'is_consistent': True}
    )

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
