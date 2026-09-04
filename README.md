# 🛡️ PayShield AI

### AI-Powered Fraud Prevention, Risk-Based Verification & Revenue Recovery

> **Razorpay AI Buildathon 2026 — AI Risk Manager + AI Revenue Recovery**

PayShield AI is an AI-powered payment security and recovery prototype built around one principle:

> **Don't treat every payment the same.**

It connects:

**ML fraud prediction → deterministic decisioning → risk-based verification → security intervention → failed-payment recovery → intelligent retry → operational explanation**

into one merchant-facing workflow.

---

# 🚀 Judge Quick Start

## 🌐 Live Demo

### 👉 [Launch PayShield AI](https://payshield-ai-iblc2arnq6ovzfecwi8tyq.streamlit.app/)

**No login or local installation is required.**

Open the live application and start testing the workflow immediately.

> **Prototype boundary:** Razorpay payment events are demonstrated through sandbox/webhook simulation. No real customer money is processed.

---

# ⚡ 3-Minute Judge Demo

## 1️⃣ Real AI Fraud Detection — ~45 sec

Select:

```text
🤖 AI Model
```

Run a transaction and show:

```text
Transaction
     ↓
🛡️ FraudShield ML
     ↓
Fraud Probability
     ↓
🧠 Decision Engine
     ↓
ALLOW / 2FA / HOLD
```

### What to evaluate

The ML model produces the fraud-risk signal.

The deterministic Decision Engine converts that signal into the operational payment action.

This separation keeps the final payment control predictable and auditable.

---

## 2️⃣ Medium-Risk Protection — ~30 sec

Demonstrate:

```text
🟠 MEDIUM
     ↓
🔐 2FA REQUIRED
     ↓
OTP GENERATED
     ↓
VERIFY OTP
     ↓
✅ PAYMENT APPROVED
```

This demonstrates **adaptive friction** rather than automatically rejecting every suspicious transaction.

---

## 3️⃣ High-Risk Response — ~30 sec

Demonstrate:

```text
🔴 HIGH
     ↓
⛔ HOLD
     ↓
🎫 SECURITY TICKET
     ↓
🤖 PaymentOps AI
```

Show the incident summary and recommended operational response.

---

## 4️⃣ Failed Payment Recovery — ~45 sec

Click:

```text
❌ Simulate Failed Payment
```

Then show:

```text
PAYMENT FAILED
      ↓
💰 PayRecover AI
      ↓
Recovery Probability
      ↓
⏰ Smart Retry AI
      ↓
Best Retry Window
      ↓
💳 Payment Method Recommendation
```

> This is a simulated recovery event for evaluation. It does not move real money.

---

## 5️⃣ AI Explanation — ~30 sec

Ask PaymentOps/Gemini:

```text
Why was this payment held and what should the merchant do?
```

Gemini provides the natural-language explanation while the **trained ML model + deterministic policy layer remain responsible for the core fraud decision**.

---

# 🎯 What Judges Can Evaluate

| Area               | Demonstrated Capability                   |
| ------------------ | ----------------------------------------- |
| 🛡️ Fraud          | ML-based fraud-risk prediction            |
| 🧠 Decisioning     | Deterministic ALLOW / 2FA / HOLD policy   |
| 🔐 Verification    | Risk-based OTP 2FA                        |
| 🎫 Security        | High-risk security ticketing              |
| 💰 Recovery        | Failed-payment recovery prediction        |
| ⏰ Retry            | Retry-window optimization                 |
| 💳 Payment Methods | Alternative payment-method recommendation |
| 🤖 Operations      | PaymentOps + Gemini explanations          |
| 🔌 Integration     | Razorpay sandbox/event simulation         |
| 📊 Evaluation      | Held-out PR-AUC / ROC-AUC                 |
| ⚠️ Risk Trade-offs | Explicit false-positive-cost methodology  |

---

# 🏆 Razorpay AI Buildathon Alignment

PayShield AI is primarily aligned with:

### Track 02 — AI Risk Manager

and secondarily with:

### Track 03 — AI Revenue Recovery

---

## 🛡️ Track 02 — AI Risk Manager

PayShield AI provides:

* A trained ML fraud-risk detector.
* Held-out test-set evaluation.
* Fraud probability prediction.
* A deterministic risk-policy layer.
* LOW / MEDIUM / HIGH risk classification.
* Risk-based 2FA for medium-risk transactions.
* HOLD + security ticketing for high-risk transactions.
* Explainable operational decisions.
* PR-AUC and ROC-AUC evaluation.
* Explicit consideration of false-positive costs.
* A defense-only security use case.

### Core principle

The generative AI layer does **not** independently decide whether a payment is fraudulent.

```text
ML MODEL
   ↓
FRAUD PROBABILITY
   ↓
DETERMINISTIC POLICY
   ↓
ALLOW / 2FA / HOLD
```

This keeps the security control bounded and auditable.

---

# 💰 Track 03 — AI Revenue Recovery

PayShield AI also demonstrates a revenue-recovery workflow for failed payments.

It includes:

* Failed-payment classification.
* Recovery probability prediction.
* Smart retry optimization.
* Multiple retry-window evaluation.
* Payment-method recommendation.
* Simulated payment-failure events.
* Recovery recommendations.
* Operational explanations.

The prototype does not claim real-money recovery during the demo.

---

# ⚠️ Safety & Evaluation Boundary

PayShield AI is a **buildathon prototype**, not a production payment authorization system.

The project does **not** claim:

* Production fraud guarantees.
* Unrestricted autonomous payment approval.
* Unrestricted autonomous movement of funds.
* Real-money recovery through the demo.
* Production-grade Razorpay webhook ingestion.
* Production-grade audit infrastructure.

These capabilities are identified separately as future production scope.

---

# 🎯 Problem

Digital payment systems face two major challenges:

### 1. Fraud

Fraudulent transactions can result in:

* Financial losses.
* Chargebacks.
* Security incidents.
* Merchant risk.
* Customer trust issues.

### 2. Payment Failure

Legitimate payment failures can result in:

* Lost revenue.
* Customer drop-off.
* Repeated failed attempts.
* Poor payment experiences.

Traditional systems can also introduce unnecessary friction by treating transactions too similarly.

PayShield AI addresses both problems through **adaptive payment-risk and recovery workflows**.

---

# 💡 Solution

PayShield evaluates payment behavior using machine learning and then applies a deterministic policy layer.

```text
PAYMENT RECEIVED
       ↓
🛡️ FRAUDSHIELD AI
       ↓
FRAUD PROBABILITY
       ↓
🧠 DECISION ENGINE
       ↓
 ┌─────────┬───────────┬──────────┐
 ↓         ↓           ↓
🟢 LOW   🟠 MEDIUM   🔴 HIGH
 ↓         ↓           ↓
ALLOW     2FA        HOLD
                     +
                  SECURITY
                   TICKET
```

For failed payments:

```text
❌ PAYMENT FAILED
       ↓
💰 PAYRECOVER AI
       ↓
RECOVERY PROBABILITY
       ↓
⏰ SMART RETRY AI
       ↓
RETRY TIME + PAYMENT METHOD
       ↓
⭐ RECOVERY RECOMMENDATION
```

---

# 🛡️ FraudShield AI

FraudShield is the core machine-learning fraud detection layer.

It provides:

* AI-based fraud probability prediction.
* Transaction risk scoring.
* LOW / MEDIUM / HIGH classification.
* Transaction behavior analysis.
* Customer risk analysis.
* Merchant risk analysis.
* Payment-channel analysis.
* Device analysis.
* Velocity analysis.
* Failure-pattern analysis.

## Fraud Detection Signals

The fraud engine uses signals including:

* Transaction amount.
* Customer monthly spending.
* Merchant risk score.
* IP risk score.
* Transaction velocity.
* Failed transactions.
* Payment channel.
* Device type.
* Geographic distance.
* Customer transaction history.
* Customer failure rate.
* Merchant transaction history.
* Merchant fraud rate.
* Transaction timing.
* Amount deviation from user behavior.

---

# 🧠 PayShield Decision Engine

The Decision Engine converts the FraudShield ML probability into an operational payment control.

```text
FraudShield ML
      ↓
Risk Probability
      ↓
Policy Layer
      ↓
┌────────────┬──────────────┬───────────────┐
│ LOW        │ MEDIUM       │ HIGH          │
│ 0–39       │ 40–69        │ 70–100        │
│            │              │               │
│ ALLOW      │ 2FA          │ HOLD          │
│            │              │ +             │
│            │              │ SECURITY      │
│            │              │ TICKET        │
└────────────┴──────────────┴───────────────┘
```

The ML model predicts risk.

The deterministic policy layer controls the final action.

This makes the payment decision:

**Predictable + Auditable + Explainable**

---

# 🔐 Risk-Based 2FA

Medium-risk transactions trigger an additional verification step.

```text
MEDIUM RISK
     ↓
2FA REQUIRED
     ↓
OTP GENERATED
     ↓
VERIFY OTP
     ↓
PAYMENT APPROVED
```

The prototype includes:

* OTP generation.
* OTP expiry.
* OTP verification.
* Failed-attempt tracking.
* Maximum-attempt protection.
* Payment approval after successful verification.

The 2FA mechanism is intended for demonstration and should not be treated as production authentication infrastructure.

---

# 🎫 Security Ticketing

High-risk transactions can be placed on HOLD and generate a security ticket.

Tickets can contain:

* Ticket ID.
* Transaction ID.
* Transaction amount.
* Fraud risk score.
* Risk level.
* Payment action.
* Creation time.
* Ticket status.
* Security recommendation.

This gives security teams an operational response instead of only producing a fraud score.

---

# 💰 PayRecover AI

Fraud prevention is only one side of payment operations.

When a legitimate payment fails, PayRecover AI evaluates the payment context and predicts the probability of successful recovery.

It considers signals such as:

* Failure reason.
* Payment method.
* Retry count.
* Time since failure.
* Customer success rate.
* Payment-method success rate.
* Previous failures.
* Device type.
* Transaction timing.

The application includes:

```text
❌ Simulate Failed Payment
```

so judges can observe the recovery workflow without processing real money.

---

# ⏰ Smart Retry AI

Smart Retry AI determines when a failed payment should be retried.

The system evaluates multiple retry windows:

```text
5 min
15 min
30 min
60 min
120 min
240 min
480 min
1440 min
```

The trained model predicts the expected success probability for each interval.

The highest-probability option becomes the recommended retry window.

Example interface:

```text
Retry Time       Predicted Success
-----------------------------------
5 min                 XX%
15 min                XX%
30 min                XX%
60 min                XX%
120 min               XX%
240 min               XX%
480 min               XX%
1440 min              XX%
```

The displayed values are generated by the trained model for the transaction being evaluated.

---

# 💳 Payment Method Recommendation

PayShield can evaluate alternative payment methods including:

* UPI.
* CARD.
* WALLET.
* NETBANKING.

The recovery workflow can recommend an alternative payment method based on the available recovery model.

Instead of simply recommending:

> **Try again later.**

PayShield can provide:

> **Try again later using a better payment method.**

---

# 🤖 PaymentOps AI + Gemini

PaymentOps AI acts as the operational intelligence layer of PayShield.

It converts technical payment signals into merchant-friendly explanations.

For security incidents, PaymentOps can provide:

### 📋 Incident Summary

Transaction information, amount, risk level, and decision.

### 🔍 Problem Detected

The signals contributing to the intervention.

### 📊 Business Impact

The potential operational impact of the payment decision.

### 🎯 Recommended Action

The recommended next step for the merchant or security team.

### 🧠 AI Assessment

A natural-language interpretation of the incident.

Gemini is used for **explanation and operational intelligence**.

The FraudShield ML model and deterministic Decision Engine remain responsible for the core fraud decision.

---

# 💬 Gemini AI Assistant

PayShield includes a Gemini-powered assistant for questions about:

* Current transaction risk.
* Fraud decisions.
* 2FA.
* Payment recovery.
* Smart Retry.
* PaymentOps.
* Security recommendations.

Example:

```text
User:
Why was this payment held?

AI:
The transaction received a high fraud-risk score.
The configured security policy therefore placed
the payment on hold for security review.
```

Gemini is an **assistance and explanation layer**, not the sole authority for approving or blocking payments.

---

# 🔌 Razorpay Sandbox / Webhook Simulation

PayShield includes a Razorpay sandbox/event simulation layer.

Example:

```text
payment.failed
       ↓
Razorpay Event
       ↓
PayShield
       ↓
PayRecover AI
       ↓
Smart Retry AI
```

The prototype demonstrates how payment events can enter the PayShield workflow.

> **Important:** The integration shown in the buildathon demo is a sandbox/simulation workflow. It does not process real customer payments.

---

# 📊 Model Performance

PayShield evaluates its models using held-out test data rather than relying on accuracy alone.

| Model       | Purpose                            |    PR-AUC |   ROC-AUC |
| ----------- | ---------------------------------- | --------: | --------: |
| FraudShield | Fraud-risk prediction              | **0.333** | **0.811** |
| PayRecover  | Failed-payment recovery prediction | **0.461** | **0.704** |
| Smart Retry | Retry-success prediction           | **0.574** | **0.707** |

## Why PR-AUC?

Fraud datasets are typically imbalanced, so PR-AUC provides a more informative view of positive-class performance than accuracy alone.

---

# ⚠️ False-Positive Cost

For the AI Risk Manager track, false positives matter because legitimate transactions can be unnecessarily challenged or held.

PayShield therefore separates:

* **False-positive rate / precision-recall behavior** for model evaluation.
* **Challenge cost** for legitimate transactions sent to 2FA.
* **Potential blocked legitimate transaction value** for legitimate transactions sent to HOLD.

The project intentionally does **not invent a rupee-denominated false-positive cost**.

The final operating-point analysis should use the actual held-out transaction amounts and the selected decision threshold.

---

# 🧠 Machine Learning Models

PayShield uses three trained models:

| Model                | Purpose                            |
| -------------------- | ---------------------------------- |
| `fraud_model.pkl`    | Fraud-risk prediction              |
| `recovery_model.pkl` | Failed-payment recovery prediction |
| `retry_model.pkl`    | Retry-success prediction           |

Feature definitions and model configuration are stored separately in the `config/` directory.

---

# 🔄 Complete Payment Operations Flow

```text
                 PAYMENT RECEIVED
                       │
                       ▼
               🛡️ FRAUDSHIELD AI
                       │
                       ▼
                 RISK PROBABILITY
                       │
                       ▼
              🧠 DECISION ENGINE
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      🟢 LOW       🟠 MEDIUM      🔴 HIGH
          │            │            │
       ALLOW          2FA          HOLD
                       │             │
                       ▼             ▼
                    VERIFY      SECURITY TICKET
                       │             │
                       └──────┬──────┘
                              │
                              ▼
                    PAYMENT OPERATIONS


             FAILED LEGITIMATE PAYMENT
                       │
                       ▼
                 💰 PAYRECOVER AI
                       │
                       ▼
                RECOVERY PROBABILITY
                       │
                       ▼
                 ⏰ SMART RETRY AI
                       │
              ┌────────┴────────┐
              ▼                 ▼
         RETRY TIME       PAYMENT METHOD
              │                 │
              └────────┬────────┘
                       ▼
              ⭐ BEST RECOVERY ACTION
```

---

# 📈 Merchant Security Dashboard

The dashboard provides visibility into:

* Fraud-risk decisions.
* Fraud statistics.
* Revenue-recovery workflow.
* Smart Retry recommendations.
* Security tickets.
* Transaction history.
* Security Operations Center.
* Current payment decision.
* Explainable AI.
* PaymentOps analysis.
* AI assistant interactions.

---

# 📖 PayShield Manual

The application includes an interactive manual explaining:

* FraudShield.
* Risk levels.
* Decision Engine.
* 2FA.
* Security tickets.
* PayRecover.
* Smart Retry.
* Payment-method optimization.
* PaymentOps.
* Razorpay sandbox/event simulation.

This allows judges and users to understand the system directly from the application.

---

# 🔊 Security Feedback

PayShield includes interactive security feedback for important payment decisions.

The application can provide audio/voice feedback alongside visual security states to make the dashboard more interactive during demonstrations.

---

# 🛠️ Technology Stack

## Application

* Python
* Streamlit
* Pandas
* NumPy

## Machine Learning

* Scikit-learn
* XGBoost
* Joblib
* Feature engineering
* Predictive modeling

## Generative AI

* Google Gemini API
* Gemini-powered PaymentOps
* Gemini AI Assistant

## Payment Integration Concept

* Razorpay Sandbox
* Razorpay webhook/event simulation

## Security

* Risk-based payment controls
* OTP-based 2FA
* Security ticketing
* Deterministic decision policy

---

# 📁 Project Structure

```text
PayShield-AI/
│
├── app.py
├── requirements.txt
├── README.md
│
├── models/
│   ├── fraud_model.pkl
│   ├── recovery_model.pkl
│   └── retry_model.pkl
│
├── config/
│   ├── fraud_features.json
│   ├── recovery_features.json
│   ├── retry_features.json
│   └── model_metrics.json
│
└── data/
    ├── fraud_test.csv
    └── recovery_full.csv
```

---

# 📦 Requirements

```txt
streamlit
joblib
numpy<2.0.0
pandas
scikit-learn==1.5.2
xgboost
streamlit-authenticator==0.2.3
bcrypt
google-genai
```

> Some dependencies may remain in the deployment environment even if a particular optional component is not used in the current public demo.

---

# 🔐 Configuration

Sensitive credentials must **never** be committed to GitHub.

The application uses deployment secrets for services such as Gemini.

Example:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
```

Never commit:

* API keys.
* Passwords.
* Authentication secrets.
* Cookie keys.
* Private credentials.

---

# ▶️ Run Locally

Clone the repository:

```bash
git clone https://github.com/miraculous234/PayShield-AI.git
cd PayShield-AI
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 🌐 Deployment

PayShield AI is deployed using Streamlit Community Cloud.

```text
GitHub Repository
        ↓
Streamlit Community Cloud
        ↓
app.py
        ↓
PayShield AI
        ↓
Public Demo
```

### Live Application

👉 [Launch PayShield AI](https://payshield-ai-iblc2arnq6ovzfecwi8tyq.streamlit.app/)

---

# 🎬 Recommended Demo Flow

For the buildathon presentation:

### 1. AI Fraud Detection

```text
Transaction
   ↓
FraudShield ML
   ↓
Fraud Probability
   ↓
Decision Engine
   ↓
ALLOW / 2FA / HOLD
```

### 2. Medium-Risk Transaction

```text
MEDIUM
   ↓
2FA
   ↓
OTP Verification
   ↓
PAYMENT APPROVED
```

### 3. High-Risk Transaction

```text
HIGH
   ↓
HOLD
   ↓
SECURITY TICKET
   ↓
PaymentOps AI
```

### 4. Failed Payment Recovery

```text
Payment Failed
   ↓
PayRecover AI
   ↓
Recovery Probability
   ↓
Smart Retry
   ↓
Retry Window
   ↓
Payment Method
   ↓
Recovery Recommendation
```

### 5. Gemini PaymentOps

Ask:

```text
Why was this payment held and what should the merchant do?
```

Gemini converts the payment signals into a clear operational explanation.

---

# 🏆 Why PayShield AI?

PayShield AI is not simply a fraud classifier and not a chatbot placed on top of payments.

It connects:

```text
PREDICTION
    ↓
POLICY
    ↓
VERIFICATION
    ↓
INTERVENTION
    ↓
RECOVERY
    ↓
EXPLANATION
```

## What makes it different?

| Capability                  | PayShield AI                               |
| --------------------------- | ------------------------------------------ |
| Fraud prediction            | Trained ML model                           |
| Final payment control       | Deterministic Decision Engine              |
| Customer friction           | Risk-based 2FA                             |
| High-risk response          | HOLD + security ticket                     |
| Failed-payment recovery     | Recovery probability model                 |
| Retry optimization          | Smart Retry model                          |
| Payment-method intervention | Recovery recommendation                    |
| Operational intelligence    | PaymentOps + Gemini                        |
| Explainability              | Risk signals + AI explanation              |
| Evaluation                  | Held-out metrics + FP-cost methodology     |
| Safety boundary             | Sandbox/simulation, no real-money movement |

The generative AI layer does **not** have unrestricted authority to approve or block payments.

The core fraud decision remains with the trained ML model and deterministic policy layer.

---

# 🎯 Project Goal

PayShield AI aims to create an intelligent payment protection and recovery layer that can:

```text
Detect Fraud
     ↓
Assess Risk
     ↓
Verify Users
     ↓
Allow / Hold Payments
     ↓
Create Security Tickets
     ↓
Explain Incidents
     ↓
Recover Failed Revenue
     ↓
Optimize Retry Timing
     ↓
Optimize Payment Method
```

The goal is to balance:

**Security + Customer Experience + Revenue Recovery + Merchant Operations**

---

# 🔮 Future Scope

The following are intentionally identified as future production improvements rather than claimed as completed functionality:

* Real-time production Razorpay webhook ingestion.
* Production payment-gateway integration.
* Measured batch-level recovered revenue on real/sandbox payment outcomes.
* Explicit compliant escalation and stopping rules for automated recovery.
* Production-grade audit logging for every money-related action.
* Advanced fraud graph and behavioral anomaly models.
* Real-time model monitoring and threshold calibration.
* Automated merchant alerts.
* Continuous model retraining with drift monitoring.
* Multi-agent PaymentOps automation with bounded permissions.
* Adaptive risk thresholds.
* More sophisticated recovery strategies.

---

# 🛡️ PayShield AI

### **Prevent Fraud. Reduce Friction. Recover Revenue.**

Built as an AI-powered payment security and recovery prototype for the **Razorpay AI Buildathon 2026**.
