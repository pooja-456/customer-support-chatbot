# Baseline Benchmark & Comparison Report
## Stage 3 Deliverable for Hiver SDE Intern Take-Home Assignment

> **Objective**: Establish rigorous, honest performance baselines on both the 15,587-sample Test split and the 200-sample hand-labelled Golden Evaluation Set before introducing the main AI Trust-Aware Agent.

### 1. High-Level Performance Comparison

| Baseline Model | Architecture | Training Data | Golden Set Accuracy | Golden Set Macro-F1 | Test Split Accuracy | Test Split Macro-F1 |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Baseline 1** | Legacy `difflib` + Canned SaaS Rules | None (Static) | **22.00%** | **0.1286** | N/A | N/A |
| **Baseline 2 (Primary)** | TF-IDF (1-2 gram) + Logistic Regression | 72,862 Train rows | **98.00%** | **0.9771** | **98.51%** | **0.9739** |
| **Baseline 2b (Comparator)** | TF-IDF (1-2 gram) + LinearSVC | 72,862 Train rows | **99.00%** | **0.9883** | -- | -- |

### 2. Per-Intent Breakdown on Golden Evaluation Set (200 Examples)

| Intent Class | B1 Precision | B1 Recall | B1 F1 | B2 Precision | B2 Recall | B2 F1 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `BATTERY_AND_POWER` | 0.000 | 0.000 | 0.000 | **1.000** | **1.000** | **1.000** |
| `SOFTWARE_OS_UPDATE` | 0.268 | 0.422 | 0.328 | **1.000** | **1.000** | **1.000** |
| `ACCOUNT_AND_SECURITY` | 0.162 | 0.300 | 0.210 | **1.000** | **0.950** | **0.974** |
| `BILLING_AND_SUBSCRIPTIONS` | 0.062 | 0.067 | 0.065 | **1.000** | **0.867** | **0.929** |
| `CONNECTIVITY_AND_SYNC` | 0.000 | 0.000 | 0.000 | **1.000** | **0.960** | **0.980** |
| `HARDWARE_AND_AUDIO_SCREEN` | 0.000 | 0.000 | 0.000 | **1.000** | **1.000** | **1.000** |
| `GENERAL_CHITCHAT_OR_FEEDBACK` | 0.237 | 0.400 | 0.297 | **0.918** | **1.000** | **0.957** |

### 3. Key Analytical Findings & Taxonomy Validation

#### 3.1 Failure Modes of Baseline 1 (Legacy Rule Bot)
- **Zero Recall on Domain-Specific Classes**: Baseline 1 scores **0.000 F1** on `BATTERY_AND_POWER`, `CONNECTIVITY_AND_SYNC`, and `HARDWARE_AND_AUDIO_SCREEN`. The legacy bot possessed zero knowledge of hardware components, cellular antennas, or battery chemistry.
- **Heavy Misclassification to Fallback**: The legacy bot dumps almost all customer queries into `GENERAL_CHITCHAT_OR_FEEDBACK` (40% recall, 0.237 precision) or misattributes app freezing to generic `SOFTWARE_OS_UPDATE`.

#### 3.2 Performance of Baseline 2 (TF-IDF + Logistic Regression)
- **Solid Domain Generalization**: Baseline 2 jumps to **98.00% accuracy** and **0.9771 Macro-F1** on the Golden Evaluation Set, and **98.51% accuracy** on the large 15.5k-sample Test split.
- **Handling Cross-Intent Ambiguities**: Performance on boundary cases (e.g. `BATTERY_AND_POWER` post-update) demonstrates that n-gram features successfully capture symptom keywords (`battery`, `drain`, `dying`) even when trigger words (`ios`, `update`) are present.

#### 3.3 Discovered Taxonomy Difficulties
1. **Update as Trigger vs. Update as Symptom**: When a customer tweets *'since updated to iOS 11 my battery dies in 2 hours'*, the bag-of-words model receives strong signals for both `SOFTWARE_OS_UPDATE` and `BATTERY_AND_POWER`. Balanced class weighting helps prioritize the rarer symptom class, but a calibrated Trust Layer will be essential to catch these split-probability decisions.
2. **Hardware Screen vs. OS Freezing**: Queries stating *'screen is unresponsive'* without mentioning touch glass damage can be confused between software freezing and hardware digitizer failure.