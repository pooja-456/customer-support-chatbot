# Hiver SDE Intern Take-Home: Trust-Aware Customer Support Agent

This project upgrades an existing Rule-Based Chatbot into a **Trust-Aware AI Pipeline** that classifies customer intents, retrieves historical precedent, extracts actions, and explicitly decides whether to `AUTO_HANDLE` or `ESCALATE` the request based on measurable confidence and evidence.

## Architecture
`Query -> Intent (LR) -> Retrieval (TF-IDF) -> Extraction (Regex) -> Trust Layer -> Generation`

## Requirements
- Python 3.9+
- `pandas`, `numpy`, `scikit-learn`, `joblib`
- (Optional) `google-generativeai` or `openai` for LLM experiments.

## Installation
```bash
pip install pandas numpy scikit-learn joblib
```

## Dataset Setup
The AppleSupport interaction dataset splits and models are already precomputed and located in `data/splits/` and `baselines/`. No data downloading is required to run the evaluations.

## How to Run Core Reproducible Evaluations
All scripts are located in the `evaluation/` folder.

**1. Golden Set Trust-Aware Pipeline Evaluation (Stage 5)**
Runs the 200 Golden Set examples through the Trust Layer.
```bash
python evaluation/stage5_evaluate.py
```
*Outputs: `stage5_report.md`, `golden_predictions.csv`*

**2. Response Quality Evaluation (Stage 6)**
Evaluates the deterministic fallback generator against the rubric.
```bash
python evaluation/stage6_evaluate.py
```
*Outputs: `stage6_response_report.md`, `response_quality_predictions.csv`*

## Expected Headline Numbers

**MEASURED:**
- Intent Classification Accuracy: 98.00% (Baseline 2 / Stage 5)
- Auto-Handle Rate: 57.0%
- False Automation Proxy Rate: 6.0% (Proxy-based trust evaluation)
- Deterministic Template Construction Safety: Does not dynamically generate novel claims (construction property, not a semantic hallucination score).

**NOT MEASURED:**
- Human semantic response quality (Relevance, Grounding, Actionability, Tone)
- Human/LLM judge agreement
- Empirical LLM generation quality

## Test Command
To verify pipeline integrity, run the test suite:
```bash
python tests/test_stage4_pipeline.py
python tests/test_stage6_generation.py
python tests/test_stage7_llm_generation.py
```

## OPTIONAL: LLM Setup
An LLM generator experiment is fully implemented behind the `BaseGenerator` interface. To run it, simply export an API key:
```bash
export OPENAI_API_KEY="your-key"
# or
export GEMINI_API_KEY="your-key"
```
Then run the Stage 7 evaluation:
```bash
python evaluation/stage7_llm_evaluate.py
```
*(If no key is exported, the pipeline gracefully falls back to deterministic generation and logs that the experiment was bypassed).*

## Known Limitations
- Generates unresolvable `t.co` links.
- Trust thresholds (0.35 similarity, 0.60 consistency) are heuristic.
- High-risk policy unconditionally escalates all billing queries.
