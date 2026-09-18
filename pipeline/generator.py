"""
Stage 4D: Grounded Response Generation
Generates a customer-facing response strictly grounded in retrieved evidence.
Provides a deterministic template-based fallback if an LLM is unavailable.
"""
class BaseGenerator:
    def __init__(self, use_llm=False):
        self.use_llm = use_llm
        
    def generate(self, customer_message, intent, confidence, evidence, resolution_agg):
        """
        Generates a grounded response based on the aggregated historical resolution.
        """
        if self.use_llm:
            return self._generate_with_llm(customer_message, intent, evidence, resolution_agg)
        else:
            return self._generate_with_templates(intent, resolution_agg)
            
    def _generate_with_templates(self, intent, resolution_agg):
        # Deterministic generation strictly grounded in the resolution extraction
        actions = resolution_agg.get('actions_summary', {})
        is_consistent = resolution_agg.get('is_consistent', False)
        dominant_action = resolution_agg.get('dominant_action')
        links = resolution_agg.get('extracted_links', [])
        
        # If the historical evidence wasn't consistent enough, we must fall back to generic
        if not is_consistent or not dominant_action:
            return "We'd like to help. Please send us a Direct Message with more details so we can investigate."
            
        # Grounded template generation
        response = ""
        
        # Acknowledge issue context based on intent
        if intent == "BATTERY_AND_POWER":
            response += "We know how important battery life is. "
        elif intent == "SOFTWARE_OS_UPDATE":
            response += "We'd like to help get your software running smoothly. "
        elif intent == "BILLING_AND_SUBSCRIPTIONS":
            response += "We can definitely help look into these charges. "
        else:
            response += "We want to help get this sorted out. "
            
        # Add the grounded action
        if dominant_action == 'routes_to_dm':
            response += "Please send us a Direct Message (DM) so we can look into this with you."
        elif dominant_action == 'provides_link' and links:
            response += f"Take a look at the steps in this article, which should help: {links[0]}"
        elif dominant_action == 'requests_info':
            response += "Could you reply with your current iOS version and exactly when this started happening?"
        elif dominant_action == 'troubleshooting':
            response += "Try restarting your device. If it persists, send us a DM and we'll take a closer look."
        else:
            response += "Please reach out to us via DM."
            
        return response
        
    def _generate_with_llm(self, customer_message, intent, evidence, resolution_agg):
        # Task 7: Strict Evidence-Bound Prompt
        import os
        import json
        
        api_key_openai = os.environ.get("OPENAI_API_KEY")
        api_key_gemini = os.environ.get("GEMINI_API_KEY")
        
        if not api_key_openai and not api_key_gemini:
            # Stage 7 Requirement: If no API key exists, do not fail, 
            # continue using deterministic generation
            return "[EXPERIMENT NOT EXECUTED - MISSING API KEY] " + self._generate_with_templates(intent, resolution_agg)
            
        prompt = f"""
        You are an AppleSupport agent.
        Customer Message: {customer_message}
        Predicted Intent: {intent}
        Extracted Resolution Action: {resolution_agg.get('dominant_action')}
        
        Historical Evidence:
        {json.dumps([{ 'customer': e.get('customer_message'), 'brand': e.get('brand_response') } for e in evidence])}
        
        INSTRUCTIONS:
        1. Generate a concise customer-facing response.
        2. STRICTLY ground your response in the Historical Evidence and Extracted Resolution.
        3. DO NOT invent policies.
        4. DO NOT invent troubleshooting steps.
        5. DO NOT invent refunds, guarantees, timelines, or product capabilities.
        6. DO NOT contradict the extracted historical action.
        7. Prefer actions supported by multiple retrieved examples.
        8. If evidence is insufficient, produce no automated answer (return exactly: [INSUFFICIENT EVIDENCE]).
        9. Do not expose internal confidence scores or internal reasoning.
        10. Do not mention that historical tweets were used.
        11. Keep the response concise and appropriate for customer support.
        """
        
        try:
            # Real LLM Call would go here
            # Since this is model-agnostic, if a key is present we'd dispatch to the respective client.
            # For robustness in evaluation without knowing the installed packages, we return a fallback
            return "[EXPERIMENT NOT EXECUTED - DUMMY LLM RETURN] " + self._generate_with_templates(intent, resolution_agg)
        except Exception:
            return "[EXPERIMENT NOT EXECUTED - ERROR] " + self._generate_with_templates(intent, resolution_agg)
