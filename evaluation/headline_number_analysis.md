# What is Missing About the Headline Number?

**Headline Metric:** 98.00% Intent Accuracy on Golden Set (Baseline 2 / Stage 5)

While a 98% accuracy score appears outstanding, treating it as proof that the support agent is "98% effective" is highly dangerous in a customer support context. Here is what this headline number hides:


### 98% = Intent Classification Accuracy
It is critical to clarify that 98% represents intent classification accuracy only.
It does NOT mean:
- 98% response quality
- 98% automation safety
- 98% customer satisfaction

Intent accuracy measures routing correctness only. The project deliberately reports response-quality dimensions as unmeasured rather than converting template properties into semantic quality scores.

### 2. Intent Correctness ≠ Historical Grounding
An intent classifier only knows categories. It doesn't know *what Apple actually does* when a customer has a battery issue (e.g., do they replace it, ask for a DM, or send a link?). True support requires historical grounding, which intent models cannot provide on their own.

### 3. Intent Correctness ≠ Safe Automation
The classifier confidently assigned an intent to 100% of queries, but confidently answering a legal threat or a complex refund request is catastrophic. The Trust Layer revealed that **43%** of queries actually required escalation due to low historical similarity, conflicting precedent, or high-risk topics. 

### 4. The Golden Set is Small
200 examples is statistically insufficient to guarantee safety across the massive long-tail of edge cases in a 3-million-tweet dataset. A 98% score on 200 cases is a signal, not a guarantee.

### 5. Proxy Labels and Uncalibrated Thresholds
Our False Automation Rate (6.0%) was measured against *proxy labels* (High Risk Intents + Ambiguity Flag). This assumes all other queries *should* be automated. In reality, many "easy" intents require nuanced troubleshooting. Furthermore, our thresholds (0.35 similarity, 0.60 consistency) are educated heuristics that require rigorous calibration against a separate validation set.

### 6. Missing Human & LLM Validation
We have not yet established a baseline for how often humans agree with our deterministic rubric scores. Furthermore, the LLM experiment was bypassed due to missing API credentials, leaving the generative pipeline's true potential empirically unevaluated.

**Conclusion:** The 98% intent accuracy proves we have a solid foundation for routing. However, the system's actual customer-facing quality is governed entirely by the Trust Layer and the Generator, both of which require significantly more calibration and empirical testing before production deployment.
