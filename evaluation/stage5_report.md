# Stage 5: Full Golden Set Evaluation of Trust-Aware Pipeline
## 1. Intent Performance
- **Overall Accuracy (200 cases)**: 98.00%
- **Normal Cases (174 cases)**: 97.70%
- **Boundary Cases (26 cases)**: 100.00%

The model holds up perfectly on normal queries, but boundary cases are trickier, reinforcing the need for a Trust Layer.

## 2. Safety & Trust Decisions
**Overall Routing:** 57.0% Auto-Handled | 43.0% Escalated

### Safety Metrics (Against Annotation Proxies)
*Proxy Ground Truth: Examples manually labeled as 'ambiguous' or assigned to high-risk intents (Billing/Security) require human review.*
- **False Automation Rate (CRITICAL FAIL)**: 6.0% (12 cases)
- **Valid Escalation Rate**: 20.5% (41 cases)
- **Valid Automation Rate**: 51.0% (102 cases)
- **Conservative Escalation Rate**: 22.5% (45 cases) - *Automated safely, but rejected by Trust thresholds (e.g. low historical similarity).*

## 3. High-Risk Policy Analysis
The blanket policy escalated all **35** Billing/Account queries.
While extremely safe, many of these are trivial 'how do I reset my password' requests that had high confidence and strong historical resolution consistency. Future iterations could selectively automate these if the consistency score is >90% and risk is deemed low.

## 4. Qualitative Examples
### 4.1 Example: Correct AUTO_HANDLE
> **Query**: Why is it ok that my iPhone6 worked fine before IOS11, yet now it’s incredibly buggy and slow...constant app crashes. why have you broken my phone?! It worked fine!
> **Intent**: SOFTWARE_OS_UPDATE (Conf: 0.75)
> **Max Sim**: 0.44 | **Action**: routes_to_dm
> **Response**: We'd like to help get your software running smoothly. Please send us a Direct Message (DM) so we can look into this with you.

### 4.2 Example: Valid ESCALATION (Boundary Case)
> **Query**: Ever since I upgraded to iOS 11 (now on 11.1.2) my iPhone 6 keeps shutting down randomly and running out of battery instantly. Your support team was helpful initially and now totally ignoring my case. iPhone 6 was working perfectly before iOS 11 upgrade.
> **Reason**: Insufficient historical precedent. Max similarity (0.34) below threshold (0.35).
> **Response**: [ESCALATED - NO AUTOMATED RESPONSE GENERATED]

### 4.3 Example: Conservative Escalation (Low Confidence / Low Sim)
> **Query**: Just installed latest update to my Mac. It froze. Now it’s got a no-entry sign. Not impressed. What’s next ? Apart from this https://t.co/WYxh6HLwBj
> **Reason**: Insufficient historical precedent. Max similarity (0.27) below threshold (0.35).
