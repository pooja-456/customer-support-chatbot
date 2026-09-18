"""
baselines/baseline1_fuzzy_rules.py - Baseline 1: Preserved Legacy Rule/Fuzzy Chatbot

This wrapper preserves and exposes the exact, unmodified legacy chatbot logic
from `Chatbot_Task4/chatbot/core.py` (which uses difflib.SequenceMatcher with a 0.8
threshold and static keyword fallbacks into 4 categories).

It serves as the mandatory TRIVIAL BASELINE for the Hiver assignment.
No new AppleSupport data is used to improve this baseline, ensuring an honest,
unbiased representation of the old system's performance.
"""

import os
import sys
import io
import re
import difflib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
LEGACY_CHATBOT_DIR = os.path.join(PROJECT_ROOT, "Chatbot_Task4")

sys.path.insert(0, LEGACY_CHATBOT_DIR)
from chatbot.core import CustomerSupportBot

TARGET_INTENTS = [
    "BATTERY_AND_POWER",
    "SOFTWARE_OS_UPDATE",
    "ACCOUNT_AND_SECURITY",
    "BILLING_AND_SUBSCRIPTIONS",
    "CONNECTIVITY_AND_SYNC",
    "HARDWARE_AND_AUDIO_SCREEN",
    "GENERAL_CHITCHAT_OR_FEEDBACK"
]

class LegacyFuzzyBaseline:
    """Wraps the unmodified legacy CustomerSupportBot and maps its internal decisions to target intents."""
    def __init__(self):
        self.bot = CustomerSupportBot()

    def predict_intent(self, text):
        cleaned = self.bot.preprocess_input(text)

        # 1. Check direct pattern matches
        best_score = 0
        best_pattern = None
        for pattern in self.bot.responses.keys():
            score = self.bot.calculate_pattern_score(cleaned, pattern)
            if score > best_score:
                best_score = score
                best_pattern = pattern

        if best_score > 0.5:
            # Map legacy pattern to closest intent
            if any(w in best_pattern for w in ['password', 'login', 'account', 'locked', 'logout']):
                return "ACCOUNT_AND_SECURITY"
            elif any(w in best_pattern for w in ['payment', 'billing', 'refund', 'subscription', 'pricing', 'plans', 'cost']):
                return "BILLING_AND_SUBSCRIPTIONS"
            elif any(w in best_pattern for w in ['crash', 'slow', 'sync', 'app', 'link', 'submission']):
                return "SOFTWARE_OS_UPDATE"
            elif any(w in best_pattern for w in ['hello', 'hi', 'hey', 'help', 'support', 'quit', 'bye', 'exit']):
                return "GENERAL_CHITCHAT_OR_FEEDBACK"
            else:
                return "SOFTWARE_OS_UPDATE"

        # 2. Check keyword variations
        keywords = self.bot.find_keyword_matches(cleaned)
        if keywords:
            if any(kw in ['password', 'login', 'account', 'locked'] for kw in keywords):
                return "ACCOUNT_AND_SECURITY"
            elif any(kw in ['app', 'crash', 'slow', 'sync'] for kw in keywords):
                return "SOFTWARE_OS_UPDATE"
            elif any(kw in ['payment', 'billing', 'refund', 'subscription'] for kw in keywords):
                return "BILLING_AND_SUBSCRIPTIONS"

        # 3. Final default fallback of the old bot
        return "GENERAL_CHITCHAT_OR_FEEDBACK"

    def evaluate(self, df, text_col="customer_text", label_col="assigned_intent"):
        preds = [self.predict_intent(str(t)) for t in df[text_col]]
        y_true = df[label_col].tolist()

        acc = accuracy_score(y_true, preds)
        macro_f1 = f1_score(y_true, preds, average='macro', zero_division=0)
        report = classification_report(y_true, preds, labels=TARGET_INTENTS, output_dict=True, zero_division=0)
        cm = confusion_matrix(y_true, preds, labels=TARGET_INTENTS).tolist()

        results = {
            'model_name': 'Baseline 1: Legacy Fuzzy / Keyword Rules',
            'sample_count': len(df),
            'accuracy': round(float(acc), 4),
            'macro_f1': round(float(macro_f1), 4),
            'per_intent_metrics': {intent: {k: round(v, 4) for k, v in report[intent].items()} for intent in TARGET_INTENTS if intent in report},
            'confusion_matrix': cm,
            'target_labels': TARGET_INTENTS
        }
        return results, preds

if __name__ == "__main__":
    golden_csv = os.path.join(PROJECT_ROOT, "evaluation", "golden_set.csv")
    if os.path.exists(golden_csv):
        df_golden = pd.read_csv(golden_csv)
        baseline = LegacyFuzzyBaseline()
        res, _ = baseline.evaluate(df_golden)
        print("=" * 80)
        print("BASELINE 1 EVALUATION ON GOLDEN EVALUATION SET (200 EXAMPLES)")
        print(f"Accuracy: {res['accuracy'] * 100:.2f}%")
        print(f"Macro-F1: {res['macro_f1']:.4f}")
        print("=" * 80)
        for intent in TARGET_INTENTS:
            m = res['per_intent_metrics'].get(intent, {})
            print(f"  {intent:30s} Precision: {m.get('precision', 0):.3f} | Recall: {m.get('recall', 0):.3f} | F1: {m.get('f1-score', 0):.3f}")
