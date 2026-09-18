# Final Artifact Index

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
| `evaluation/stage6_response_results.json` | Deprecated Stage 6 heuristic metrics (See Audit) |
| `evaluation/stage6_response_report.md` | Stage 6 narrative report (Historical Audit Trail) |
| `evaluation/llm_generation_predictions.csv` | Stage 7 run (LLM bypassed; deterministic fallback recorded) |
| `evaluation/stage7_llm_results.json` | Stage 7 safety check counts |
| `evaluation/stage7_llm_report.md` | Stage 7 narrative report |
| `evaluation/final_results.json` | Consolidated artifact-verified metrics across all stages |
| `evaluation/final_results.csv` | Flat CSV version of final_results.json |
| `evaluation/final_failure_analysis.md` | Top 5 real failure modes with examples |
| `evaluation/final_failure_examples.csv` | CSV of 5 failure examples |
| `evaluation/headline_number_analysis.md` | Why 98% intent accuracy ≠ 98% system effectiveness |
| `evaluation/decision_log.md` | 15 non-obvious engineering decisions with rationale |
| `evaluation/evaluation_integrity_audit.md` | **Audit Artifact**: Evaluation methodology corrections |
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
