# Final Decision Log

### 1. Selecting AppleSupport after Dataset Profiling
- **Decision**: Analyzed the full Kaggle dataset and selected AppleSupport based on empirical metrics (106k outbound replies, 89.6% actionable rate, 1.5% deflection rate).
- **Why**: To ensure the brand had high-quality historical evidence, rather than assuming a famous brand would work.
- **Alternative**: Randomly picking a MAANG company.
- **Why Not**: Might have led to a brand with purely deflecting responses ("Call this number"), ruining the retrieval stage.
- **Evidence**: Data profiles generated in Stage 2.

### 2. Preserving the Legacy Bot as Baseline 1
- **Decision**: Wrapped the existing `Chatbot_Task4/chatbot/core.py` without modifying its logic.
- **Why**: To establish an honest starting point representing the system *before* our upgrades.
- **Alternative**: Deleting it and writing a new dummy baseline.
- **Why Not**: Destroys the baseline metric and violates the requirement to upgrade the *existing* chatbot.
- **Consequence**: Baseline 1 scored 22% accuracy, proving the massive ROI of the new pipeline.

### 3. Seven-Class Taxonomy
- **Decision**: Discovered and locked in a 7-class taxonomy (`BATTERY_AND_POWER`, `SOFTWARE_OS_UPDATE`, etc.).
- **Why**: Based on empirical n-gram clustering of actual AppleSupport tweets.
- **Alternative**: Using generic predefined classes (e.g., "Complaint", "Question").
- **Why Not**: Apple support agents need domain-specific routing (hardware vs software).
- **Consequence**: Allowed the TF-IDF model to achieve 98% accuracy.

### 4. Author-Level Train/Validation/Test Isolation
- **Decision**: GroupShuffleSplit by `author_id` rather than random row splitting.
- **Why**: To prevent data leakage where a customer's multi-turn thread is split across train and test.
- **Alternative**: Standard random train/test split.
- **Why Not**: Artificial metric inflation due to memorization of user quirks.
- **Evidence**: Test suite confirmed 0 overlapping authors.

### 5. 200-Example Golden Set
- **Decision**: Manually curated a 200-example Golden Evaluation Set separate from the Test split.
- **Why**: To allow for meticulous human review of edge cases and trust decisions.
- **Alternative**: Relying solely on the 15k Test split.
- **Why Not**: Cannot manually verify actionability and tone on 15,000 examples.

### 6. Explicitly Including Boundary Cases
- **Decision**: Stratified the Golden Set to include exactly 26 (13%) known ambiguous/boundary cases.
- **Why**: To stress-test the Trust Layer's escalation logic.
- **Alternative**: Random sampling.
- **Why Not**: Random sampling might miss rare boundary cases entirely.

### 7. TF-IDF + Logistic Regression Baseline
- **Decision**: Used TF-IDF (1-2 gram, 15k features) + Logistic Regression (C=2.0, balanced weights).
- **Why**: Fast, highly interpretable classical ML benchmark that performs exceptionally well on short text.
- **Alternative**: Immediately jumping to BERT/Transformers.
- **Why Not**: Violates the principle of establishing strong, simple baselines first.
- **Consequence**: Achieved 98% accuracy, proving deep learning is not strictly required for the routing phase.

### 8. Retrieval Before Generation (RAG architecture)
- **Decision**: Built a TF-IDF cosine-similarity retriever against the training set.
- **Why**: To ground responses in actual historical precedent, preventing the agent from inventing company policies.
- **Alternative**: Feeding just the intent to a generator.
- **Why Not**: The agent would hallucinate troubleshooting steps.

### 9. Resolution Extraction via Regex Heuristics
- **Decision**: Mapped retrieved historical text to structured actions (`routes_to_dm`, `provides_link`) using regex.
- **Why**: To calculate historical consistency mathematically before generation.
- **Alternative**: Asking an LLM to read the history and generate an answer directly.
- **Why Not**: Impossible to guarantee consistency or measure conflict without a structured intermediate step.

### 10. Separate Trust Layer
- **Decision**: Placed a distinct Trust Layer *between* extraction and generation.
- **Why**: To block generation entirely if evidence is weak or conflicting, preventing hallucinations before they happen.
- **Alternative**: Letting the generator output "I don't know."
- **Why Not**: Wastes compute and lacks deterministic control over escalation.

### 11. Similarity Threshold (0.35)
- **Decision**: Escalates if the max retrieved similarity is < 0.35.
- **Why**: Educated heuristic to ensure the historical evidence is actually relevant to the query.
- **Alternative**: Top-K regardless of similarity.
- **Why Not**: Could retrieve completely unrelated tweets if the query is unique.

### 12. Consistency Threshold (0.60)
- **Decision**: Escalates if < 60% of retrieved examples agree on the same dominant action.
- **Why**: Prevents the bot from randomly guessing when historical agents were inconsistent.
- **Alternative**: Always take the top result.
- **Why Not**: Dangerous if the top result was a rogue agent or edge case.

### 13. Blanket High-Risk Escalation Policy
- **Decision**: Unconditionally escalates `BILLING_AND_SUBSCRIPTIONS` and `ACCOUNT_AND_SECURITY`.
- **Why**: To prioritize absolute safety in V1 over automation efficiency.
- **Alternative**: Automating password resets.
- **Why Not**: Massive security and legal liability without deeper authentication systems.

### 14. Deterministic Fallback Generator
- **Decision**: Created strict template-based responses mapped to the extracted actions.
- **Why**: Guarantees 0% hallucinations and keeps the pipeline runnable without API keys.
- **Alternative**: Forcing LLM usage.
- **Why Not**: Makes the project un-runnable for reviewers without API access.

### 15. Model-Agnostic LLM Interface
- **Decision**: Wrapped the LLM experiment behind a generic interface that falls back if `GEMINI_API_KEY` and `OPENAI_API_KEY` are missing.
- **Why**: To satisfy the experiment requirement without breaking CI/CD or local execution.
