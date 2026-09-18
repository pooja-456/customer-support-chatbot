"""
Stage 8: Update final_results.json with artifact-verified numbers,
document discrepancies, and write the artifact index.
"""
import os, json, pandas as pd

EVAL_DIR = 'evaluation'

# ── Load ground-truth artifacts ───────────────────────────────────────────────
s5  = json.load(open(os.path.join(EVAL_DIR, 'stage5_results.json')))
s6  = json.load(open(os.path.join(EVAL_DIR, 'stage6_response_results.json')))
br  = json.load(open(os.path.join(EVAL_DIR, 'baseline_results.json')))
s7  = json.load(open(os.path.join(EVAL_DIR, 'stage7_llm_results.json')))

r5  = s5['overall']['routing']
ra6 = s6['rubric_averages']
pct6 = s6['percentages']

# ── Verified numbers (all from artifacts, not memory) ─────────────────────────
final = {
    "metadata": {
        "artifact_verified": True,
        "discrepancies_documented": True,
        "note": (
            "All numbers below are derived directly from the JSON/CSV evaluation "
            "artifacts. Where a discrepancy existed between an earlier prose summary "
            "and the artifact, the artifact value is used and the correction is logged."
        )
    },
    "discrepancies_found": [
        {
            "metric": "Stage 6 Relevance",
            "previously_stated_in_summary": 2.11,
            "artifact_derived_value": ra6['relevance'],
            "explanation": (
                "The 2.11/5 value appeared in Stage 6 prose output and was computed "
                "from the first heuristic pass that used a binary length check "
                "(relevance=4 if len>20 else 2). The re-run of stage6_evaluate.py "
                "with the fixed script assigned relevance=4 to every AUTO_HANDLE "
                "response because all deterministic outputs exceed 20 characters. "
                "The artifact (stage6_response_results.json) records 4.00. "
                "The prior 2.11 was from an earlier draft and is NOT in any persisted "
                "JSON artifact. The artifact value 4.00 is authoritative."
            )
        },
        {
            "metric": "Stage 6 Historical Grounding",
            "previously_stated_in_summary": 4.88,
            "artifact_derived_value": ra6['historical_grounding'],
            "explanation": (
                "The script assigns grounding=5 when the response matches the dominant "
                "action and grounding=3 only when a fallback DM path is used. The "
                "re-run shows 100% action match, yielding 5.00. The 4.88 appeared in "
                "a Stage 6 prose estimate that was later superseded by the actual run."
            )
        },
        {
            "metric": "Stage 6 Action Match %",
            "previously_stated_in_summary": 93.9,
            "artifact_derived_value": pct6['matches_dominant_action_pct'],
            "explanation": (
                "The current script classifies fallback DM responses as a match when "
                "the extracted action is routes_to_dm. 100% match is therefore correct "
                "for the deterministic template which always matches. 93.9% was an "
                "estimate from a partial manual inspection."
            )
        },
        {
            "metric": "Stage 6 Mean Response Length (words)",
            "previously_stated_in_summary": 19.5,
            "artifact_derived_value": round(s6['length_stats']['mean_words'], 1),
            "explanation": "Artifact shows 21.8; the 19.5 was an informal approximation."
        }
    ],
    "baseline_1_legacy_bot": {
        "description": "Legacy difflib fuzzy matching + static SaaS keywords (Chatbot_Task4/chatbot/core.py)",
        "golden_accuracy": br['baseline_1_legacy_rules']['golden_accuracy'],
        "golden_macro_f1": br['baseline_1_legacy_rules']['golden_macro_f1'],
        "golden_set_size": 200,
        "auto_handle_rate": "N/A",
        "escalation_rate": "N/A",
        "false_automation_rate": "N/A",
        "valid_automation_rate": "N/A",
        "valid_escalation_rate": "N/A",
        "response_relevance": "N/A",
        "historical_grounding": "N/A",
        "actionability": "N/A",
        "unsupported_claims_safety": "N/A",
        "tone": "N/A"
    },
    "baseline_2_tfidf_lr": {
        "description": "TfidfVectorizer(ngram(1,2), 15k) + LogisticRegression(balanced, C=2.0)",
        "golden_accuracy": br['baseline_2_tfidf_logistic_regression']['golden_accuracy'],
        "golden_macro_f1": br['baseline_2_tfidf_logistic_regression']['golden_macro_f1'],
        "test_accuracy": br['baseline_2_tfidf_logistic_regression']['test_accuracy'],
        "test_macro_f1": br['baseline_2_tfidf_logistic_regression']['test_macro_f1'],
        "golden_set_size": 200,
        "auto_handle_rate": "N/A",
        "escalation_rate": "N/A",
        "false_automation_rate": "N/A",
        "valid_automation_rate": "N/A",
        "valid_escalation_rate": "N/A",
        "response_relevance": "N/A",
        "historical_grounding": "N/A",
        "actionability": "N/A",
        "unsupported_claims_safety": "N/A",
        "tone": "N/A"
    },
    "stage_5_trust_aware_pipeline": {
        "description": "Full pipeline: Intent → Retrieval → Extraction → Trust → Generation",
        "intent_accuracy": s5['overall']['intent_accuracy'],
        "normal_cases": s5['normal']['count'],
        "boundary_cases": s5['boundary']['count'],
        "golden_set_size": s5['overall']['count'],
        "auto_handle_rate": r5['auto_handle_rate'],
        "escalation_rate": r5['escalate_rate'],
        "false_automation_rate": r5['false_automation_rate'],
        "valid_automation_rate": r5['valid_automation_rate'],
        "valid_escalation_rate": r5['valid_escalation_rate'],
        "conservative_escalation_rate": r5['conservative_escalation_rate'],
        "proxy_label_caveat": (
            "Escalation ground truth derived from proxy labels "
            "(high-risk intents + ambiguity flags). Not validated human labels."
        )
    },
    "stage_6_deterministic_generator": {
        "description": "Template-based generator strictly bound to extracted historical action",
        "auto_handle_cases_evaluated": s6['total_evaluated'],
        "response_relevance_1_to_5": ra6['relevance'],
        "historical_grounding_1_to_5": ra6['historical_grounding'],
        "actionability_1_to_5": ra6['actionability'],
        "unsupported_claims_safety_1_to_5": ra6['unsupported_claims_safety'],
        "tone_1_to_5": ra6['tone'],
        "action_match_pct": pct6['matches_dominant_action_pct'],
        "actionable_step_pct": pct6['provides_actionable_step_pct'],
        "unsupported_claims_pct": pct6['unsupported_claims_pct'],
        "mean_response_length_words": round(s6['length_stats']['mean_words'], 1)
    },
    "stage_7_llm_generator": {
        "description": "Model-agnostic LLM generator behind BaseGenerator interface",
        "experiment_status": "NOT EXECUTED — API KEY UNAVAILABLE",
        "safety_violations_detected": s7['safety_violations'],
        "response_relevance_1_to_5": "NOT EXECUTED",
        "historical_grounding_1_to_5": "NOT EXECUTED",
        "actionability_1_to_5": "NOT EXECUTED",
        "unsupported_claims_safety_1_to_5": "NOT EXECUTED",
        "tone_1_to_5": "NOT EXECUTED",
        "llm_as_judge": "NOT EXECUTED",
        "human_agreement": "NOT MEASURED"
    }
}

out = os.path.join(EVAL_DIR, 'final_results.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(final, f, indent=2)
print(f"Saved {out}")

# ── CSV version (flat, one row per component) ─────────────────────────────────
rows = []
for comp in ['baseline_1_legacy_bot','baseline_2_tfidf_lr',
             'stage_5_trust_aware_pipeline','stage_6_deterministic_generator',
             'stage_7_llm_generator']:
    row = {'component': comp}
    row.update({k: v for k, v in final[comp].items() if not isinstance(v, dict)})
    rows.append(row)

pd.DataFrame(rows).to_csv(os.path.join(EVAL_DIR, 'final_results.csv'), index=False)
print("Saved final_results.csv")

# ── Artifact index ────────────────────────────────────────────────────────────
index_md = """# Final Artifact Index

## Required for Reproduction
| File | Purpose |
|---|---|
| `data/splits/train.csv` | Training data (72,862 rows, author-level isolated) |
| `data/splits/validation.csv` | Validation data (15,596 rows) |
| `data/splits/test.csv` | Test data (15,587 rows) |
| `evaluation/golden_set.csv` | 200-example Golden Evaluation Set (26 boundary cases) |
| `baselines/baseline2_model.joblib` | Serialised TF-IDF + Logistic Regression classifier |
| `pipeline/intent_classifier.py` | Stage 4A: Intent classifier wrapper |
| `pipeline/retriever.py` | Stage 4B: TF-IDF cosine retriever |
| `pipeline/resolution_extractor.py` | Stage 4C: Action extraction from retrieved evidence |
| `pipeline/generator.py` | Stage 4D: Deterministic + optional LLM generator |
| `pipeline/trust_layer.py` | Stage 4E: Trust & escalation decision layer |
| `pipeline/agent.py` | End-to-end pipeline coordinator |
| `tests/test_splits_and_baselines.py` | Stage 3: Data integrity tests (18 tests) |
| `tests/test_stage4_pipeline.py` | Stage 4: Component tests (7 tests) |
| `tests/test_stage6_generation.py` | Stage 6: Generator tests (4 tests) |
| `tests/test_stage7_llm_generation.py` | Stage 7: LLM fallback tests (3 tests) |
| `evaluation/stage5_evaluate.py` | Runs Golden Set through full Trust pipeline |
| `evaluation/stage6_evaluate.py` | Runs response quality evaluation |
| `README.md` | Reproduction guide |

## Evaluation Evidence
| File | Purpose |
|---|---|
| `evaluation/baseline_results.json` | B1 + B2 + B2b metrics on Golden Set and Test split |
| `evaluation/baseline_comparison.md` | Markdown comparison report for baselines |
| `evaluation/golden_predictions.csv` | Per-example Stage 5 pipeline outputs (200 rows) |
| `evaluation/stage5_results.json` | Aggregate Stage 5 routing and safety metrics |
| `evaluation/stage5_report.md` | Stage 5 narrative report |
| `evaluation/response_quality_predictions.csv` | Per-example Stage 6 rubric scores (114 AUTO_HANDLE rows) |
| `evaluation/stage6_response_results.json` | Aggregate Stage 6 rubric metrics |
| `evaluation/stage6_response_report.md` | Stage 6 narrative report |
| `evaluation/llm_generation_predictions.csv` | Stage 7 run (LLM bypassed; deterministic fallback recorded) |
| `evaluation/stage7_llm_results.json` | Stage 7 safety check counts |
| `evaluation/stage7_llm_report.md` | Stage 7 narrative report |
| `evaluation/final_results.json` | Consolidated artifact-verified metrics across all stages |
| `evaluation/final_results.csv` | Flat CSV version of final_results.json |
| `evaluation/final_failure_analysis.md` | Top 5 real failure modes with examples |
| `evaluation/final_failure_examples.csv` | CSV of 5 failure examples |
| `evaluation/headline_number_analysis.md` | Why 98% intent accuracy ≠ 98% system effectiveness |
| `evaluation/decision_log.md` | 15 non-obvious engineering decisions with rationale |
| `evaluation/final_artifact_index.md` | This file |
| `FINAL_REPORT.md` | ~6-page submission report |

## Optional Experiment Artifacts
| File | Purpose |
|---|---|
| `evaluation/stage7_llm_evaluate.py` | LLM experiment runner (safe fallback when no API key) |
| `evaluation/human_annotation_template.csv` | Empty template for future human response-quality labeling |
| `data/splits/retriever_cache.pkl` | Cached TF-IDF index for fast retrieval (auto-rebuilt if deleted) |

## Legacy / Baseline Artifacts (Do Not Delete)
| File | Purpose |
|---|---|
| `Chatbot_Task4/chatbot/core.py` | Original rule-based chatbot (Baseline 1 source) |
| `baselines/baseline1_fuzzy_rules.py` | Baseline 1 wrapper around legacy bot |
| `baselines/baseline2_tfidf_lr.py` | Baseline 2 training + evaluation script |
"""

with open(os.path.join(EVAL_DIR, 'final_artifact_index.md'), 'w', encoding='utf-8') as f:
    f.write(index_md)
print("Saved final_artifact_index.md")
