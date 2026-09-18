# Golden Evaluation Set Labeling Guide & Boundary Rules
## AppleSupport 7-Class Intent Taxonomy for Customer Support Intent Taxonomy

### Overview
This document defines the boundary rules used to assign intent labels to the **200-example Golden Evaluation Set** ([golden_set.csv](golden_set.csv)). The goal is to provide an objective, independently reviewable standard for human evaluation and LLM-as-a-judge comparison.

---

### Core Working Intents & Boundary Rules

#### 1. `BATTERY_AND_POWER`
- **In-Scope**: Queries reporting fast battery drain, device shutting down with remaining charge, slow/failed charging, overheating device, battery health decline, or charging accessories (cables/bricks).
- **Boundary with `SOFTWARE_OS_UPDATE`**:
  - *Rule*: If the customer reports that battery drain started *after an update*, classify as `BATTERY_AND_POWER` if the primary complaint is battery drain, but set `ambiguity_flag = True`.
  - *Rationale*: The actionable troubleshooting pathway for battery issues is *Settings > Battery > Battery Health*, not OS reinstallation.

#### 2. `SOFTWARE_OS_UPDATE`
- **In-Scope**: Failed iOS/macOS update installations, boot loops, stuck on Apple logo, app crashing/freezing, keyboard glitches, and general system slowness post-update.
- **Boundary with `HARDWARE_AND_AUDIO_SCREEN`**:
  - *Rule*: If the screen freezes or touch stops responding following a software update, classify as `SOFTWARE_OS_UPDATE` if UI elements are frozen, or `HARDWARE_AND_AUDIO_SCREEN` if the physical digitizer is damaged. Flag as ambiguous if unspecified.

#### 3. `ACCOUNT_AND_SECURITY`
- **In-Scope**: Forgotten Apple ID passwords, disabled/locked accounts, 2-Factor Authentication (2FA) verification codes not arriving, iCloud keychain sync issues, and Activation Lock.
- **Boundary with `BILLING_AND_SUBSCRIPTIONS`**:
  - *Rule*: If an account is locked due to an unpaid balance, classify under `ACCOUNT_AND_SECURITY` if the user's primary barrier is logging in, but flag ambiguous with `BILLING_AND_SUBSCRIPTIONS`.

#### 4. `BILLING_AND_SUBSCRIPTIONS`
- **In-Scope**: Unrecognized App Store / iTunes charges, double billing, subscription cancellation requests, free trial renewals, and refund requests.
- **Boundary with `ACCOUNT_AND_SECURITY`**:
  - *Rule*: Focuses strictly on financial transactions, credit cards, invoices, and bank charges.

#### 5. `CONNECTIVITY_AND_SYNC`
- **In-Scope**: Wi-Fi dropping/disconnecting, Bluetooth pairing failure, 'No Service' cellular errors, SIM card failures, and AirDrop dropouts.
- **Boundary with `SOFTWARE_OS_UPDATE`**:
  - *Rule*: When network errors occur post-update, classify as `CONNECTIVITY_AND_SYNC` with `ambiguity_flag = True` because resolution requires *Reset Network Settings*.

#### 6. `HARDWARE_AND_AUDIO_SCREEN`
- **In-Scope**: Physical hardware damage, cracked display glass, distorted speaker sound, dead microphone, unresponsive physical buttons (home/power/volume), and camera lens issues.
- **Boundary with `SOFTWARE_OS_UPDATE`**:
  - *Rule*: If physical hardware failure is suspected without a software event, classify as `HARDWARE_AND_AUDIO_SCREEN`.

#### 7. `GENERAL_CHITCHAT_OR_FEEDBACK`
- **In-Scope**: Greetings ("hello", "good morning"), expressions of frustration without actionable details ("apple sucks", "worst phone ever"), compliments, and image-only/media-only tweets with no textual inquiry.
- **Boundary Rule**: Acts as the catch-all out-of-scope class for queries that lack diagnostic specifics.

---

### Ambiguity Flagging Protocol
Each Golden Set item includes an `ambiguity_flag` (True/False). If a query spans multiple intents (e.g. *"Updated to iOS 11 and now Wi-Fi drops and battery drains"*), the primary intent is assigned based on the first actionable symptom, `ambiguity_flag` is set to `True`, and competing intents are recorded.
