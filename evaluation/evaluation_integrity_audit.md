# Evaluation Integrity Audit

This document audits the evaluation metrics used to assess the Trust-Aware Customer Support Agent, examining their source data, calculation methods, and whether they validly interpret the proposed evaluation rubric.

## 1. Stage 6 Response Quality Metrics

| Metric | Reported Value | Measurement Method | Valid Interpretation | Caveat |
|--------|----------------|--------------------|----------------------|--------|
| **Relevance** | 4.00/5 | Heuristic: `4 if len(resp) > 20 else 2` | **INVALID.** Length is not semantic relevance. | The score is a hardcoded function of text length and does not measure whether the response addresses the customer's actual issue. Semantic relevance was **not independently measured**. |
| **Historical Grounding** | 5.00/5 | Heuristic: Checks for string tokens (e.g. 'Direct Message') based on extracted action. | **INVALID.** This is an *Historical-action adherence proxy*, not true semantic grounding. | It checks if the template matches the extracted action class, but does not measure if the response accurately reflects the nuances of the retrieved historical text. |
| **Actionability** | 5.00/5 | Heuristic: Hardcoded to 5 for all templates. | **INVALID.** This is a deterministic template property. | It guarantees the template contains an instruction (e.g. "send a DM"), but does not evaluate whether that instruction is actually a useful next step for the specific customer problem. |
| **Unsupported Claims Safety** | 5.00/5 (0% rate) | Heuristic: Hardcoded to 5 (0%) based on generator construction. | **Valid (as a property guarantee)** | The deterministic generator strictly uses hardcoded safe templates, making hallucinations mathematically impossible. However, this is a property of the architecture, not an independent semantic evaluation. |
| **Tone** | 5.00/5 | Heuristic: Hardcoded to 5 for all templates. | **INVALID.** Conflicts with qualitative findings. | A hardcoded score of 5/5 ignores the qualitative failure mode ("Robotic Tone / Repetition") identified in Task 8. A robotic, identical template response is not a 5/5 customer support experience. |
| **Dominant Action Match** | 100% (was 93.9%) | Heuristic code change: Fallbacks were explicitly defined as matches if they contain "Direct Message". | **Valid (with caveat)** | The 93.9% → 100% jump was caused by a calculation change: the script was updated to classify the generic fallback (which asks for a DM) as a successful match for `routes_to_dm`. |
| **Mean Response Length** | 21.8 words | `len(resp.split())` | **Valid** | Accurate token/word count measurement. |

## 2. Stage 5 Trust & Routing Metrics

| Metric | Reported Value | Measurement Method | Valid Interpretation | Caveat |
|--------|----------------|--------------------|----------------------|--------|
| **Intent Accuracy** | 98.00% | Scikit-learn accuracy on Golden Set vs `assigned_intent` | **Valid** | Measures text routing accuracy against human-curated Golden labels. |
| **Auto-handle Rate** | 57.0% | `count(AUTO_HANDLE) / 200` | **Valid** | Accurate measurement of system routing output. |
| **Escalated Rate** | 43.0% | `count(ESCALATE_TO_HUMAN) / 200` | **Valid** | Accurate measurement of system routing output. |
| **False Automation Rate** | 6.0% | Proxy: Automated cases that were flagged as `is_ambiguous` or High-Risk Intent. | **Valid (as a proxy)** | Escalation ground truth does not exist in the raw dataset. This metric explicitly remains a proxy-based heuristic, not a validated human label. |

## 3. Golden Set Metrics

| Metric | Reported Value | Measurement Method | Valid Interpretation | Caveat |
|--------|----------------|--------------------|----------------------|--------|
| **Size & Leakage** | 200 examples | Programmatic dataset split | **Valid** | Fully verified by automated tests (`test_no_author_overlap_golden_train`). Authors are strictly isolated. |

## 4. Final Report Language Audit
The `FINAL_REPORT.md` correctly states that the LLM experiment was bypassed and does not present hypothetical results as actuals. However, the report presents the Relevance, Grounding, Actionability, and Tone scores as if they were genuine evaluations of response quality, when they are actually hardcoded heuristics or template properties.

### Conclusion
**CORRECTIONS REQUIRED BEFORE SUBMISSION**

The Stage 6 response quality metrics (Relevance, Grounding, Actionability, Tone) are systematically flawed because they substitute hardcoded properties and length heuristics for actual semantic evaluation.

**Required Corrections:**
1. In `evaluation/stage6_evaluate.py`, `evaluation/stage6_response_results.json`, and `evaluation/final_results.json`: Rename "Historical Grounding" to "Action Adherence Proxy".
2. In `FINAL_REPORT.md`: Explicitly state that semantic response relevance, actionability, and tone were **not independently measured**, and that the reported scores reflect deterministic template properties and heuristics, not human or LLM semantic judgments.
3. The discrepancy between the 4.00 Relevance score (length heuristic) and semantic relevance must be documented in the README or Final Report, preventing the 4.00 score from being misrepresented.
