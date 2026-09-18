# Trust-Aware Customer Support Agent

## 1. Problem Framing
The customer support automation problem is fundamentally about trust. Customers on social platforms express noisy, informal, and complex multi-turn issues. We selected the **AppleSupport** dataset because empirical profiling revealed a massive volume of outbound replies (106k), a highly actionable interaction rate (89.6%), and a low deflection rate (1.5%). However, simply predicting an intent is insufficient. The agent must know *what historical resolution* applies and, crucially, *when it does not have enough evidence to safely automate*.

## 2. What "Good" Means
In this project, "Good" means:
- **Correct Intent**: Routing the customer to the correct domain (e.g. Battery vs Software).
- **Evidence-Backed Resolution**: Only suggesting actions (links, DMs, restarts) that human agents historically took.
- **Useful Response**: Providing actionable next steps.
- **No Unsupported Claims**: Zero hallucinations of policies, refunds, or false guarantees.
- **Appropriate Automation/Escalation**: Escalating to a human when the request is high-risk, ambiguous, or lacks consistent historical precedent.

## 3. System Architecture
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

## 4. Dataset & Taxonomy
- **Dataset**: `twcs.csv` (Customer Support on Twitter).
- **Extraction**: Extracted 104,405 valid AppleSupport interactions.
- **Taxonomy**: We empirically derived 7 intent classes (`GENERAL`, `SOFTWARE`, `BATTERY`, `CONNECTIVITY`, `HARDWARE`, `ACCOUNT`, `BILLING`). This is a working data-derived hypothesis, not an absolute ground truth.
- **Golden Set**: Curated 200 examples explicitly containing 26 boundary cases.
- **Leakage Prevention**: Strictly enforced author-level `GroupShuffleSplit` across Train/Val/Test. Furthermore, during evaluation, the queried tweet ID is excluded from historical retrieval to prevent the agent from retrieving the "answer key."

## 5. Baselines
We preserved the existing Tkinter Chatbot logic as our Legacy Rule Bot baseline.
- **Legacy Rule Bot**: 22.00% Accuracy | 0.1286 Macro-F1
- **TF-IDF + Logistic Regression**: 98.00% Accuracy | 0.9771 Macro-F1

The massive jump in performance proves the classical ML approach effectively solved the routing problem without requiring deep learning at this stage.

## 6. Trust-Aware Pipeline Results
Running the 200 Golden Set examples through the full Trust-Aware Pipeline yielded:
- **Intent Accuracy**: 98.00%
- **Auto-handled**: 57.0%
- **Escalated**: 43.0%
- **False Automation Proxy Rate**: 6.0% (Critical safety failure measured against proxy labels)
- **Valid Automation**: 51.0%
- **Valid Escalation**: 20.5%
- **Conservative Escalation**: 22.5%

*Note on Proxy Limitations*: Escalation ground truth does not exist in the raw dataset. We defined proxies (high-risk intents and ambiguity flags). A 6% false automation rate means the agent automated 12 queries that our heuristics flagged for human review.

## 7. Response Quality
Response-quality evaluation exposed an important measurement limitation. The deterministic generator was checked using template-level and heuristic proxies, but semantic response relevance, historical grounding, actionability, and tone were not independently measured by human reviewers or an LLM judge. Therefore, these dimensions are reported as N/A rather than assigning heuristic scores that could be mistaken for true quality measurements.

**Construction & Proxy Properties (Not Semantic Measurements):**
- **Action-Adherence Proxy**: The generator perfectly matched the extracted action type (e.g. producing a template with a link when the extraction was `provides_link`).
- **Template Construction Safety**: Because the deterministic generator uses fixed templates, it does not dynamically generate novel factual claims. This is a construction property, not a semantic hallucination evaluation.

**Qualitative Failure Observations:**
Despite the construction safety, qualitative inspection revealed severe semantic limitations:
- **Generic responses**: Templates lack entity-awareness (ignoring specifics like "Apple Music" or "iPhone X").
- **Opaque t.co links**: Providing shortened links straight from the dataset offers a terrible user experience.
- **Action extraction errors**: Misinterpreting rhetorical questions as information requests.
- **Evidence conflict**: Pulling disparate historical actions for broad queries and defaulting to generic answers.
- **Repetitive/robotic phrasing**: The exact same polite template feels robotic over multiple turns.

## 8. LLM Experiment
- **LLM pathway implemented.** The `BaseGenerator` was updated to accept an LLM prompt strictly bound by the extracted historical action.
- **Actual experiment NOT executed** because API credentials (`OPENAI_API_KEY`, `GEMINI_API_KEY`) were unavailable in the CI/CD environment.
- **LLM-as-judge NOT executed.**
- **Human agreement NOT measured.**
*(No hypothetical outcomes are presented as results).*

## 9. Top 5 Failure Modes
From the `evaluation/final_failure_analysis.md`:
1. **Opaque t.co Links**: Outputting dead or opaque shortened links straight from the dataset.
2. **Overly Generic Acknowledgments**: Templates lack entity-awareness (e.g. ignoring "Apple Music").
3. **Wrong Action Extraction**: Regex misinterpreting rhetorical questions as information requests.
4. **Evidence Conflict**: Broad queries pulling disparate historical actions.
5. **High-Risk Blanket Policy**: Unconditionally escalating simple password reset queries due to the Billing/Account policy.

## 10. What Is Missing About the Headline Number?
98% Intent Accuracy does not mean 98% effective support. Intent correctness does not equal response correctness or historical grounding. The classifier is just a router. True effectiveness relies on the Trust Layer (currently using uncalibrated heuristics) and the Response Generator.

## 11. What We Did NOT Build
The following were intentionally out of scope for this project phase:
- **Production Deployment / AWS Infrastructure**: Focused purely on algorithmic and pipeline logic.
- **Real-Time Social Ingestion**: Focused on historical dataset processing.
- **Fully Calibrated Trust Thresholds**: Used educated heuristics (0.35 sim, 0.60 consistency) rather than validation-set grid search.
- **Human-Validated Escalation Labels**: Relied on proxy labels.
- **External URL Resolution**: Links remain as opaque short-urls.

## 12. Future Work
1. Collect human response-quality labels using the generated annotation template.
2. Run the controlled LLM generation experiment by supplying API credentials.
3. Measure LLM judge vs human agreement to establish an automated evaluation loop.
4. Calibrate the Trust Layer thresholds on the Validation split.
5. Improve resolution extraction (replace regex with a lightweight classifier).
6. Resolve/validate historical links.
7. Integrate the finalized pipeline deeply into the UI.
