# Trust-Aware Customer Support Agent

An evidence-grounded customer support system designed to determine:

1. What the customer is asking
2. How similar issues were historically resolved
3. Whether there is sufficient evidence to respond automatically
4. When the request should be escalated to a human

The system combines:
- Data-derived intent classification
- Historical support evidence retrieval
- Resolution/action extraction
- Trust-aware automation
- Human escalation
- Evidence-constrained response generation
- Reproducible evaluation

## Overview
This project upgrades an original rule-based chatbot into a Trust-Aware AI Pipeline that classifies customer intents, retrieves historical precedent, extracts actions, and explicitly decides whether to `AUTO_HANDLE` or `ESCALATE` the request based on measurable confidence and evidence.

## Problem
Customer support automation is fundamentally about trust. Customers on social platforms express noisy, informal, and complex multi-turn issues. Predicting an intent is insufficient. The agent must know *what historical resolution* applies and, crucially, *when it does not have enough evidence to safely automate*.

## Approach
The system enforces strict historical grounding: it refuses to dynamically generate unsupported claims. Before responding, the agent retrieves semantically similar interactions from a training corpus, extracts the dominant action taken by human support agents (e.g., providing a link, requesting a DM, or troubleshooting), and relies on a Trust Layer to evaluate whether the evidence is strong enough to proceed without a human.

## Architecture
```text
[Customer Query]
       ↓
[Intent Classification] (TF-IDF + Logistic Regression)
       ↓
[Historical Evidence Retrieval] (TF-IDF + Cosine Similarity on Training Set)
       ↓
[Resolution / Action Extraction] (Regex heuristics on retrieved brand text)
       ↓
[Trust / Risk Layer] (Evaluates confidence, similarity, consistency, risk)
       ↓
  ┌────────┴────────┐
[ESCALATE]    [AUTO-HANDLE]
                  ↓
   [Response Generation] (Deterministic Templates / Optional LLM)
```

## Dataset
- **Source**: Customer Support on Twitter (`twcs.csv`).
- **Extraction**: Extracted 104,405 valid interactions specific to the AppleSupport domain.
- **Leakage Prevention**: Strictly enforced author-level `GroupShuffleSplit` across Train/Val/Test. During evaluation, queried interaction IDs are explicitly excluded from the retrieval index to prevent "answer key" leakage.

## Intent Taxonomy
An empirically derived 7-class taxonomy based on the dataset:
`GENERAL_CHITCHAT_OR_FEEDBACK`, `SOFTWARE_OS_UPDATE`, `BATTERY_AND_POWER`, `CONNECTIVITY_AND_SYNC`, `HARDWARE_AND_AUDIO_SCREEN`, `ACCOUNT_AND_SECURITY`, `BILLING_AND_SUBSCRIPTIONS`.

## Project Evolution
The project began as a rule-based customer support chatbot using:
- Pattern matching
- Fuzzy similarity
- Keyword fallback
- Predefined responses

It was subsequently extended into an evidence-grounded support system with:
- Data-derived intent classification
- Historical evidence retrieval
- Resolution extraction
- Trust-aware automation
- Human escalation
- Model-agnostic generation

## Evaluation Snapshot
| Component | Result |
|---|---:|
| Golden evaluation set | 200 examples |
| Legacy rule-based baseline | 22.0% accuracy |
| TF-IDF + Logistic Regression | 98.0% Golden accuracy |
| Held-out test accuracy | 98.51% |
| Held-out test Macro-F1 | 0.9739 |
| AUTO_HANDLE | 57.0% |
| ESCALATE | 43.0% |
| Valid automation | 51.0% |
| False automation proxy rate | 6.0% |

*Note: Response semantic quality was not independently measured through human or LLM evaluation. Template-level safety and action-adherence checks are therefore reported as proxies rather than semantic quality scores.*

## Failure Modes
Qualitative inspection revealed the following primary failure modes:
1. **Opaque links**: Outputting dead or opaque shortened links straight from the dataset.
2. **Generic Acknowledgments**: Templates lack entity-awareness.
3. **Extraction Errors**: Misinterpreting rhetorical questions.
4. **Evidence Conflict**: Broad queries pulling disparate historical actions.
5. **High-Risk Blanket Policy**: Unconditionally escalating simple password reset queries due to rigid policy heuristics.

## Reproducibility
The dataset splits and baseline models are already precomputed. No raw data downloading is required to run the core evaluations.

## Installation
```bash
pip install pandas numpy scikit-learn joblib
```

## Running the System
```bash
# Launch the Tkinter Legacy UI
python main.py
```

## Running Evaluation
All evaluation scripts are located in `evaluation/`.
```bash
# Evaluate the full Trust-Aware Pipeline
python evaluation/stage5_evaluate.py

# Evaluate deterministic generation
python evaluation/stage6_evaluate.py
```

## Optional LLM Generation
An LLM generator experiment is implemented behind the `BaseGenerator` interface. To run it, supply API credentials (if unavailable, the system safely falls back to deterministic generation):
```bash
export OPENAI_API_KEY="your-key"
python evaluation/stage7_llm_evaluate.py
```

## Limitations
- Generates unresolvable `t.co` links.
- Trust Layer thresholds (e.g., 0.35 similarity, 0.60 consistency) are uncalibrated heuristics.
- High-risk policy unconditionally escalates all billing queries without nuance.

## Future Work
- Collect human response-quality labels.
- Execute the controlled LLM generation experiment.
- Measure LLM judge vs human agreement.
- Calibrate the Trust Layer thresholds on the Validation split.
- Improve resolution extraction using a lightweight classifier instead of regex.

## Project Structure
- `Chatbot_Task4/chatbot/` & `main.py`: Original legacy rule-based application.
- `pipeline/`: Core trust-aware pipeline components.
- `baselines/`: Trained models and baseline wrappers.
- `data/`: Extracted datasets and taxonomy.
- `evaluation/`: Scripts and output artifacts.
- `tests/`: Integrity test suite.
