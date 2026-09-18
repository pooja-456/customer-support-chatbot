"""
Stage 4E: Trust & Escalation Layer
Evaluates signals from all previous pipeline stages to make a safe
routing decision: AUTO_HANDLE or ESCALATE_TO_HUMAN.
"""
class TrustEvaluator:
    def __init__(self, min_confidence=0.60, min_similarity=0.35):
        # Documented Heuristics
        self.min_confidence = min_confidence
        self.min_similarity = min_similarity
        
        # High-risk intents that should always route to human initially
        # until the LLM generation is deeply validated in Stage 5.
        self.high_risk_intents = {
            "BILLING_AND_SUBSCRIPTIONS",
            "ACCOUNT_AND_SECURITY"
        }

    def evaluate(self, intent_signal, retrieval_signal, resolution_signal):
        """
        Takes outputs from Stage 4A, 4B, 4C and returns a Trust Decision.
        """
        intent = intent_signal.get('predicted_intent')
        confidence = intent_signal.get('confidence', 0.0)
        is_ambiguous = intent_signal.get('is_ambiguous', False)
        
        # Retrieval checks
        max_sim = 0.0
        if retrieval_signal:
            max_sim = max([r.get('similarity_score', 0.0) for r in retrieval_signal])
            
        # Resolution checks
        is_consistent = resolution_signal.get('is_consistent', False)
        
        # 1. High Risk Check
        if intent in self.high_risk_intents:
            return {
                'decision': 'ESCALATE_TO_HUMAN',
                'reason': f"High risk intent class ({intent}) requires human review."
            }
            
        # 2. Intent Confidence & Ambiguity
        if confidence < self.min_confidence:
            return {
                'decision': 'ESCALATE_TO_HUMAN',
                'reason': f"Intent confidence ({confidence:.2f}) is below the threshold ({self.min_confidence})."
            }
        if is_ambiguous:
            margin = intent_signal.get('margin', 0.0)
            return {
                'decision': 'ESCALATE_TO_HUMAN',
                'reason': f"Intent classification is ambiguous (top classes margin {margin:.2f} is too close)."
            }
            
        # 3. Historical Precedent
        if max_sim < self.min_similarity:
            return {
                'decision': 'ESCALATE_TO_HUMAN',
                'reason': f"Insufficient historical precedent. Max similarity ({max_sim:.2f}) below threshold ({self.min_similarity})."
            }
            
        # 4. Action Consistency
        if not is_consistent:
            return {
                'decision': 'ESCALATE_TO_HUMAN',
                'reason': "Historical actions for this query are conflicting; cannot safely automate."
            }
            
        # 5. Passed all trust gates
        return {
            'decision': 'AUTO_HANDLE',
            'reason': f"Strong intent confidence, solid historical match ({max_sim:.2f}), and consistent historical resolution."
        }
