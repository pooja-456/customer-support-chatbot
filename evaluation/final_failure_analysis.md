# Final Failure Analysis

The following 5 failure modes represent real weaknesses observed during the Stage 6 Deterministic Generation evaluation.

### Example ID: golden_45
- **Query**: How do I turn off autocorrect on iOS 11?
- **Intent**: SOFTWARE_OS_UPDATE
- **Extracted Action**: provides_link
- **Generated Response**: We'd like to help get your software running smoothly. Take a look at the steps in this article, which should help: https://t.co/abcde
- **What went wrong**: The link is an opaque t.co URL, providing a terrible UX. The introductory text is also overly generic.
- **Likely Cause**: Deterministic fallback generator blindly passing the shortened URL from the raw Twitter dataset without resolving it. The generic prefix is hardcoded to the SOFTWARE_OS_UPDATE intent.
- **Potential Improvement**: Integrate a URL resolution step during data preprocessing, or use an LLM to generate context-aware lead-in text for the link.

### Example ID: golden_12
- **Query**: My apple music won't load my playlists.
- **Intent**: SOFTWARE_OS_UPDATE
- **Extracted Action**: routes_to_dm
- **Generated Response**: We'd like to help get your software running smoothly. Please send us a Direct Message (DM) so we can look into this with you.
- **What went wrong**: The response completely ignores the "Apple Music" and "playlists" context, sounding robotic.
- **Likely Cause**: The deterministic template only switches on the 7 high-level intents. It lacks entity-level awareness.
- **Potential Improvement**: Use an evidence-grounded LLM generator (Stage 7, pending API key) to weave the specific entities (Apple Music) into the response while strictly adhering to the DM action.

### Example ID: golden_89
- **Query**: Is the new iPhone X waterproof?
- **Intent**: HARDWARE_AND_AUDIO_SCREEN
- **Extracted Action**: requests_info
- **Generated Response**: We want to help get this sorted out. Could you reply with your current iOS version and exactly when this started happening?
- **What went wrong**: The generator asked for an iOS version instead of answering a simple hardware specification question.
- **Likely Cause**: The regex extraction misinterpreted the rhetorical question in the historical evidence as `requests_info`, triggering the hardcoded "Could you reply with your current iOS version" template.
- **Potential Improvement**: Replace regex-based action extraction with a small classification model or strict LLM extraction that distinguishes rhetorical from literal questions.

### Example ID: golden_112
- **Query**: Phone is broken, what do I do?
- **Intent**: HARDWARE_AND_AUDIO_SCREEN
- **Extracted Action**: routes_to_dm
- **Generated Response**: We want to help get this sorted out. Please send us a Direct Message (DM) so we can look into this with you.
- **What went wrong**: Automated safely, but the historical evidence was highly conflicted (similarity was just above threshold, consistency exactly at 60%). The response is a coin flip.
- **Likely Cause**: The query is too broad. The TF-IDF retriever pulls a random assortment of generic "broken phone" responses.
- **Potential Improvement**: Raise the consistency threshold to 0.75 for non-specific queries, forcing an escalation so a human can ask clarifying questions.

### Example ID: golden_156
- **Query**: How do I cancel my Apple TV+ trial?
- **Intent**: BILLING_AND_SUBSCRIPTIONS
- **Extracted Action**: provides_link
- **Generated Response**: [ESCALATED - NO AUTOMATED RESPONSE GENERATED]
- **What went wrong**: A perfectly safe, high-confidence query was escalated unnecessarily, wasting human agent time.
- **Likely Cause**: The blanket high-risk policy unconditionally escalates all BILLING queries, regardless of safety signals.
- **Potential Improvement**: Refine the Trust Layer to automate BILLING queries IF the extracted action is strictly `provides_link` and consistency is > 90%.

