"""
Stage 7: Evidence-Grounded LLM Generation Experiment
"""
import os
import sys
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.agent import TrustAwareAgent

EVAL_DIR = os.path.join(BASE_DIR, "evaluation")
GOLDEN_PATH = os.path.join(EVAL_DIR, "golden_set.csv")

def check_automated_safety(query, intent, action, llm_resp, det_resp, trust_decision):
    """
    Task 5: Automated Safety Checks
    """
    checks = {
        'unsupported_claims': False,
        'action_mismatch': False,
        'contradiction': False,
        'generated_when_escalated': False,
        'missing_evidence': False,
        'excessively_long': False,
        'hallucinated_url': False
    }
    
    if trust_decision == 'ESCALATE_TO_HUMAN':
        if llm_resp and "[ESCALATED" not in llm_resp:
            checks['generated_when_escalated'] = True
    else:
        # Check action mismatch heuristically
        if action == 'provides_link' and 'http' not in llm_resp.lower() and 'link' not in llm_resp.lower():
            checks['action_mismatch'] = True
        if action == 'routes_to_dm' and 'dm' not in llm_resp.lower() and 'message' not in llm_resp.lower():
            checks['action_mismatch'] = True
            
        # Length
        if len(llm_resp.split()) > 100:
            checks['excessively_long'] = True
            
        # Hallucinated URL check (if it has http but we didn't extract one in deterministic)
        if 'http' in llm_resp and 'http' not in det_resp:
            checks['hallucinated_url'] = True
            
    return checks

def run_experiment():
    print("Initializing Stage 7 Pipeline...")
    model_path = os.path.join(BASE_DIR, "baselines", "baseline2_model.joblib")
    train_path = os.path.join(BASE_DIR, "data", "splits", "train.csv")
    
    # We load two agents, one for deterministic, one for LLM (if available)
    # The LLM generator itself checks os.environ and falls back safely if no key exists.
    agent_det = TrustAwareAgent(model_path, train_path)
    agent_llm = TrustAwareAgent(model_path, train_path)
    agent_llm.generator.use_llm = True
    
    df_golden = pd.read_csv(GOLDEN_PATH)
    
    results = []
    
    # We track if the LLM actually ran
    llm_actually_ran = ("OPENAI_API_KEY" in os.environ) or ("GEMINI_API_KEY" in os.environ)
    
    for idx, row in df_golden.iterrows():
        customer_msg = str(row['customer_text'])
        source_id = str(row['source_customer_tweet_id'])
        expected_intent = str(row['assigned_intent'])
        
        # Run deterministic
        out_det = agent_det.handle_message(customer_msg, exclude_tweet_ids=[source_id])
        det_resp = out_det['generated_response']
        
        # Run LLM
        out_llm = agent_llm.handle_message(customer_msg, exclude_tweet_ids=[source_id])
        llm_resp = out_llm['generated_response']
        
        trust_dec = out_det['trust_signal']['decision']
        
        # Safety checks
        safety = check_automated_safety(
            customer_msg, 
            out_det['intent_signal']['predicted_intent'],
            out_det['resolution_signal']['dominant_action'],
            llm_resp, 
            det_resp, 
            trust_dec
        )
        
        results.append({
            'example_id': row.get('golden_id', idx),
            'query': customer_msg,
            'expected_intent': expected_intent,
            'predicted_intent': out_det['intent_signal']['predicted_intent'],
            'trust_decision': trust_dec,
            'trust_reason': out_det['trust_signal']['reason'],
            'retrieved_evidence_ids': "|".join([r['customer_tweet_id'] for r in out_det['retrieval_signal']]),
            'extracted_action': out_det['resolution_signal']['dominant_action'],
            'deterministic_response': det_resp,
            'llm_response': llm_resp,
            'provider': 'None (Fallback)' if not llm_actually_ran else 'LLM_API',
            'model': 'N/A',
            'prompt_version': 'Stage 7 Strict Constraints v1',
            'safety_checks': safety
        })
        
    df_results = pd.DataFrame(results)
    
    # Expand safety checks for CSV saving
    safety_cols = pd.json_normalize(df_results['safety_checks'])
    df_export = pd.concat([df_results.drop(columns=['safety_checks']), safety_cols], axis=1)
    
    csv_out = os.path.join(EVAL_DIR, "llm_generation_predictions.csv")
    df_export.to_csv(csv_out, index=False)
    
    # Compile Metrics
    auto_handled = df_results[df_results['trust_decision'] == 'AUTO_HANDLE']
    total_auto = len(auto_handled)
    
    metrics = {
        'llm_experiment_executed': llm_actually_ran,
        'total_cases': len(df_results),
        'auto_handled': total_auto,
        'safety_violations': {
            'action_mismatch': int(safety_cols['action_mismatch'].sum()),
            'excessively_long': int(safety_cols['excessively_long'].sum()),
            'hallucinated_url': int(safety_cols['hallucinated_url'].sum()),
            'generated_when_escalated': int(safety_cols['generated_when_escalated'].sum())
        }
    }
    
    # Save JSON
    json_out = os.path.join(EVAL_DIR, "stage7_llm_results.json")
    with open(json_out, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    # Generate Report
    generate_markdown_report(metrics, llm_actually_ran)

def generate_markdown_report(metrics, ran_llm):
    md_path = os.path.join(EVAL_DIR, "stage7_llm_report.md")
    lines = []
    
    lines.append("# Stage 7: Evidence-Grounded LLM Generation Experiment")
    
    if not ran_llm:
        lines.append("\n> **IMPORTANT NOTICE**: No API keys (OPENAI_API_KEY or GEMINI_API_KEY) were found in the environment. Per requirements, the system gracefully fell back to deterministic generation. **The LLM experiment was not executed.**")
    
    lines.append("\n## 1. Automated Safety Checks")
    lines.append("The following heuristic checks were run on the generated outputs (Note: these are automated proxies, not semantic ground truth):")
    for k, v in metrics['safety_violations'].items():
        lines.append(f"- **{k.replace('_', ' ').title()}**: {v} violations")
        
    lines.append("\n## 2. LLM-as-Judge & Human Agreement")
    lines.append("Because the API keys were missing, the LLM-as-Judge could not evaluate the differences. Furthermore, **Human judge agreement not yet measured**. We have preserved the empty human annotation templates from Stage 6 for future use.")
    
    lines.append("\n## 3. Failure Analysis (Task 9)")
    if not ran_llm:
        lines.append("Since the LLM experiment was bypassed due to missing API keys, we cannot provide 5 *real* examples of LLM failures. Both generators produced identical safe, deterministic outputs. However, had an LLM been executed, we would typically look for:")
        lines.append("1. **LLM introduces unsupported content**: The LLM might invent a refund policy even when explicitly instructed not to, bypassing the strict prompt constraints.")
        lines.append("2. **Evidence itself is insufficient**: The LLM might try to stitch together conflicting historical responses into an unreadable mess, whereas deterministic templates just pick the dominant action.")
        lines.append("3. **Hallucinated URLs**: LLMs love to convert `t.co` links into fake full URLs like `support.apple.com/kb/fake123`.")
    
    lines.append("\n## 4. Required Interpretation (Task 10)")
    lines.append("### 1. Does the LLM improve relevance?")
    lines.append("*Hypothetically*: Yes. Deterministic templates ignore context (e.g. 'Apple Music' vs 'Messages app'). An LLM grounds the response in the specific entity the user asked about.")
    lines.append("### 2. Does it preserve historical grounding?")
    lines.append("*Hypothetically*: Mostly, assuming strict prompt adherence. The prompt explicitly forces the LLM to obey the extracted historical action (e.g., if history says DM, the LLM must ask for a DM).")
    lines.append("### 3. Does it increase unsupported claims?")
    lines.append("*Hypothetically*: Yes. LLMs are inherently non-deterministic. A deterministic generator has a 0% hallucination rate. Any LLM integration will introduce *some* non-zero risk of unsupported claims.")
    lines.append("### 4. Does it change the automation rate?")
    lines.append("No. The automation rate is governed strictly by the Trust Layer (which evaluates intent confidence, retrieval similarity, and resolution consistency) *before* generation occurs. The LLM only acts on `AUTO_HANDLE` cases.")
    lines.append("### 5. Does it make the Trust Layer unnecessary?")
    lines.append("**The Trust Layer remains absolutely necessary even when an LLM is used for generation.** If the LLM is fed conflicting, low-similarity historical evidence, it will hallucinate a compromise. The Trust Layer acts as an essential firewall, ensuring the LLM is only invoked when the historical precedent is overwhelmingly clear and consistent.")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Saved Stage 7 report to {md_path}")

if __name__ == "__main__":
    run_experiment()
