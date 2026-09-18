"""
Stage 4 Full Pipeline Agent
Combines A (Intent), B (Retrieval), C (Extraction), D (Generation), E (Trust)
"""
import os
import sys

# Ensure pipeline is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.intent_classifier import ProductionIntentClassifier
from pipeline.retriever import HistoricalEvidenceRetriever
from pipeline.resolution_extractor import HistoricalResolutionExtractor
from pipeline.generator import BaseGenerator
from pipeline.trust_layer import TrustEvaluator

class TrustAwareAgent:
    def __init__(self, model_path, train_csv_path):
        print("Initializing Stage 4 Pipeline Components...")
        self.classifier = ProductionIntentClassifier(model_path)
        self.retriever = HistoricalEvidenceRetriever(train_csv_path)
        self.extractor = HistoricalResolutionExtractor()
        self.generator = BaseGenerator(use_llm=False)
        self.trust = TrustEvaluator(min_confidence=0.60, min_similarity=0.35)
        print("Agent ready.")
        
    def handle_message(self, customer_message, exclude_tweet_ids=None):
        """End-to-End Pipeline Execution."""
        
        # 1. Intent (Stage 4A)
        intent_signal = self.classifier.predict(customer_message)
        
        # 2. Retrieval (Stage 4B)
        retrieval_signal = self.retriever.retrieve(
            customer_message, top_k=5, exclude_tweet_ids=exclude_tweet_ids
        )
        
        # 3. Extraction (Stage 4C)
        resolution_signal = self.extractor.aggregate_resolutions(retrieval_signal)
        
        # 4. Trust Evaluation (Stage 4E) - evaluated before Generation to avoid wasted compute
        trust_signal = self.trust.evaluate(intent_signal, retrieval_signal, resolution_signal)
        
        # 5. Generation (Stage 4D)
        if trust_signal['decision'] == 'AUTO_HANDLE':
            # Generate grounded response
            response = self.generator.generate(
                customer_message,
                intent_signal['predicted_intent'],
                intent_signal['confidence'],
                retrieval_signal,
                resolution_signal
            )
        else:
            response = "[ESCALATED - NO AUTOMATED RESPONSE GENERATED]"
            
        return {
            'input': customer_message,
            'intent_signal': intent_signal,
            'retrieval_signal': retrieval_signal,
            'resolution_signal': resolution_signal,
            'trust_signal': trust_signal,
            'generated_response': response
        }

if __name__ == "__main__":
    import json
    model_path = os.path.join(BASE_DIR, "baselines", "baseline2_model.joblib")
    train_path = os.path.join(BASE_DIR, "data", "splits", "train.csv")
    
    agent = TrustAwareAgent(model_path, train_path)
    
    test_msgs = [
        "My iPhone 7 battery is dying so fast after iOS 11 update",
        "Can you help me reset my apple id password I forgot it completely",
        "I need a refund for an app store purchase it charged me twice",
    ]
    
    print("\n" + "="*50)
    for msg in test_msgs:
        print(f"\n[CUSTOMER]: {msg}")
        out = agent.handle_message(msg)
        print(f"[INTENT]:   {out['intent_signal']['predicted_intent']} ({out['intent_signal']['confidence']:.2f})")
        print(f"[EVIDENCE]: {len(out['retrieval_signal'])} cases retrieved. Max Sim: {out['retrieval_signal'][0]['similarity_score']:.2f}")
        print(f"[ACTION]:   {out['resolution_signal']['dominant_action']} (Consistent: {out['resolution_signal']['is_consistent']})")
        print(f"[TRUST]:    {out['trust_signal']['decision']} - {out['trust_signal']['reason']}")
        print(f"[BOT]:      {out['generated_response']}")
