"""
Stage 4A: Main Intent Classifier
Wraps the validated Baseline 2 (TF-IDF + Logistic Regression) model.
Provides intent prediction, confidence probabilities, top-K candidates,
and calculates an ambiguity signal (e.g. for boundary cases).
"""
import os
import joblib
import numpy as np

class ProductionIntentClassifier:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        self.model = joblib.load(model_path)
        self.classes_ = self.model.classes_

    def predict(self, text):
        """
        Returns a rich dictionary containing:
        - predicted_intent: str
        - confidence: float
        - top_k: list of dicts [{'intent': str, 'prob': float}]
        - is_ambiguous: bool (True if margin between top 1 and 2 is small, or max prob is low)
        - margin: float
        """
        if not text or not isinstance(text, str):
            text = ""

        # Get probabilities
        probas = self.model.predict_proba([text])[0]
        
        # Sort indices by descending probability
        sorted_indices = np.argsort(probas)[::-1]
        
        top_k = []
        for idx in sorted_indices[:3]: # Get top 3
            top_k.append({
                'intent': self.classes_[idx],
                'prob': float(probas[idx])
            })
            
        top_1_prob = top_k[0]['prob']
        top_2_prob = top_k[1]['prob'] if len(top_k) > 1 else 0.0
        
        # Ambiguity heuristics:
        # 1. Highest confidence is below 50%
        # 2. Difference between top 1 and top 2 is less than 15% (boundary case conflict)
        margin = top_1_prob - top_2_prob
        is_ambiguous = (top_1_prob < 0.50) or (margin < 0.15)
        
        return {
            'predicted_intent': top_k[0]['intent'],
            'confidence': top_1_prob,
            'top_k': top_k,
            'is_ambiguous': is_ambiguous,
            'margin': margin
        }

if __name__ == "__main__":
    # Quick validation
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, "baselines", "baseline2_model.joblib")
    classifier = ProductionIntentClassifier(model_path)
    
    # Boundary case tests
    test_queries = [
        "since updated to iOS 11 my battery dies in 2 hours", # Battery vs Software
        "wifi keeps dropping after the new update",           # Connectivity vs Software
        "screen is unresponsive and frozen",                  # Hardware vs Software
        "how do I change my billing address?",                # Clear Billing
    ]
    
    print("--- Stage 4A: Intent Classifier Validation ---")
    for q in test_queries:
        res = classifier.predict(q)
        print(f"\nQuery: '{q}'")
        print(f"Predicted: {res['predicted_intent']} (Conf: {res['confidence']:.2f})")
        print(f"Ambiguous: {res['is_ambiguous']} (Margin: {res['margin']:.2f})")
        print(f"Top 3: {[(k['intent'], round(k['prob'],2)) for k in res['top_k']]}")
