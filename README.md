# 🛡️ PayShield AI

### AI-Powered Fraud Prevention, Risk-Based Verification & Revenue Recovery

> **Razorpay AI Buildathon 2026 — AI Risk Manager + AI Revenue Recovery**

PayShield AI is a working payment-security and recovery prototype designed around one principle:

**Don't treat every payment the same.**

It combines machine-learning fraud detection, a deterministic decision layer, risk-based 2FA, security ticketing, failed-payment recovery, smart retry optimization, PaymentOps intelligence, and Gemini-powered explanations into one merchant-facing workflow.

## 🌐 Live Demo

🚀 **Try PayShield AI:**
https://payshield-ai-iblc2arnq6ovzfecwi8tyq.streamlit.app/

> **Note:** This is a buildathon prototype. Razorpay payment events are demonstrated using sandbox/webhook simulation and no real customer money is processed.


## 🏆 Razorpay AI Buildathon Alignment

PayShield AI is primarily aligned with **Track 02 — AI Risk Manager** and secondarily with **Track 03 — AI Revenue Recovery**.

### AI Risk Manager
- Working fraud-risk detector using trained ML.
- Risk is evaluated on a held-out test set.
- Final payment action is controlled by a deterministic policy layer.
- Medium-risk transactions require additional verification rather than immediate rejection.
- High-risk transactions are held and can create a security ticket.
- The project is strictly **defense-only**.
- Fraud model performance is reported with **PR-AUC and ROC-AUC**.
- False-positive cost is treated as a required evaluation metric rather than hidden behind accuracy.

### AI Revenue Recovery
- Detects a failed-payment recovery opportunity.
- Predicts recovery probability.
- Evaluates retry windows.
- Recommends a retry time and payment-method intervention.
- Demonstrates a bounded recovery workflow using simulated payment failures.
- Recovery actions are recommendations in the prototype; no real customer funds are moved automatically.

### Buildathon-safe product boundaries

The prototype uses **Razorpay sandbox/webhook simulation** for demonstration. It does not process real customer money and does not claim production authorization, production fraud guarantees, or autonomous movement of funds.

Razorpay's Buildathon explicitly emphasizes measurable risk performance, honest false-positive cost, defense-only work, measured recovery value, compliant escalation/stopping rules, and audit trails. PayShield's README therefore distinguishes **implemented prototype behavior** from **future production work**.


---

## 🖼️ Product Screenshots

> Add the final screenshots to `screenshots/` before submission.

| View | Screenshot |
|---|---|
| Merchant Dashboard | `screenshots/dashboard.png` |
| FraudShield + Decision Engine | `screenshots/fraudshield.png` |
| 2FA Verification | `screenshots/2fa.png` |
| PaymentOps + Security Ticket | `screenshots/paymentops.png` |
| PayRecover + Smart Retry | `screenshots/payrecover.png` |

## 🎯 Problem

Digital payment systems face two major challenges:

1. **Fraudulent transactions** can cause financial losses, chargebacks, and security incidents.
2. **Legitimate payment failures** can result in lost revenue and customer drop-off.

Traditional security systems may also introduce unnecessary friction by treating transactions too similarly.

PayShield AI addresses both problems through **adaptive, AI-driven payment decisions**.

---

# 💡 Solution

PayShield AI uses machine learning to evaluate transaction behavior and estimate fraud risk.

The risk score is then passed to a deterministic policy layer:

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
ALLOW     2FA       HOLD
                    +
                 SECURITY
                  TICKET
```

For failed legitimate payments:

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

# 🚀 Key Features

## 🛡️ FraudShield AI

FraudShield is the core machine-learning fraud detection layer.

It provides:

* AI-based fraud probability prediction
* Transaction risk scoring
* LOW / MEDIUM / HIGH classification
* Transaction behavior analysis
* Customer and merchant risk analysis
* Payment-channel and device analysis
* Velocity and failure-pattern analysis

### Fraud Detection Signals

The fraud engine considers signals such as:

* Transaction amount
* Customer monthly spending
* Merchant risk score
* IP risk score
* Transaction velocity
* Failed transactions
* Payment channel
* Device type
* Geographic distance
* Customer transaction history
* Customer failure rate
* Merchant transaction history
* Merchant fraud rate
* Transaction timing
* Amount deviation from user behavior

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

The ML model predicts risk, while the deterministic policy layer controls the final action.

This separation makes the payment decision **predictable, auditable, and explainable**.

---

# 🔐 2FA Verification

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

* OTP generation
* OTP expiry
* OTP verification
* Failed-attempt tracking
* Maximum attempt protection
* Payment approval after successful verification

> OTP credentials are configured for demonstration purposes and should not be treated as production authentication credentials.

---

# 🎫 Security Ticketing

High-risk transactions are placed on HOLD and can generate a security ticket.

Each ticket can contain:

* Ticket ID
* Transaction ID
* Transaction amount
* Fraud risk score
* Risk level
* Payment action
* Creation time
* Ticket status
* Security recommendation

This gives security teams an operational response instead of only a fraud score.

---

# 💰 PayRecover AI

Payment fraud prevention is only one side of payment operations.

When a legitimate payment fails, **PayRecover AI** evaluates the payment context and predicts the probability of successful recovery.

It considers factors such as:

* Failure reason
* Payment method
* Retry count
* Time since failure
* Customer success rate
* Payment-method success rate
* Previous failures
* Device type
* Transaction timing

The prototype includes a **Simulate Failed Payment** feature so judges can observe the complete recovery workflow without processing real money.

---

# ⏰ Smart Retry AI

Smart Retry AI determines **when a failed payment should be retried**.

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

The trained model predicts the success probability for each interval and recommends the best option.

Example:

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

The highest-probability interval becomes the recommended retry window.

---

# 💳 Change Payment Method

Smart recovery can also evaluate alternative payment methods.

The system can compare:

* UPI
* CARD
* WALLET
* NETBANKING

It then identifies the payment method with the strongest predicted recovery potential based on the available recovery model.

This allows PayShield to recommend not only:

> **“Try again later.”**

but also:

> **“Try again later using a better payment method.”**

---

# 🤖 PaymentOps AI + Gemini

PaymentOps AI acts as the intelligent operational layer of PayShield.

It converts technical payment signals into merchant-friendly explanations.

For a security incident, PaymentOps can provide:

### 📋 Incident Summary

Transaction ID, amount, risk level, and decision.

### 🔍 Problem Detected

What caused the payment to require intervention.

### 📊 Business Impact

How the payment decision can protect the merchant from potential loss.

### 🎯 Recommended Action

The next operational action for the merchant or security team.

### 🧠 AI Assessment

A natural-language interpretation of the incident.

Gemini is used for **explanations and operational intelligence**, while the FraudShield ML model and deterministic Decision Engine remain responsible for the core fraud decision.

---

# 💬 Gemini AI Assistant

PayShield includes a Gemini-powered assistant that allows merchants and security analysts to ask questions about:

* Current transaction risk
* Fraud decisions
* 2FA
* Payment recovery
* Smart Retry
* PaymentOps
* Security recommendations

Example:

```text
User:
Why was this payment held?

AI:
The transaction received a high fraud-risk score.
The configured security policy therefore placed the
payment on hold for security review.
```

Gemini is used as an **explanation and assistance layer**, not as the sole authority for approving or blocking payments.

---

# 🔌 Razorpay Sandbox / Webhook Simulation

PayShield includes a Razorpay Sandbox event simulation layer.

Example event:

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

### Important

This is a **buildathon prototype**.

The sandbox/webhook simulator is used to demonstrate the integration concept without processing real customer payments.

---

# 📖 PayShield Manual

The application includes an interactive manual explaining:

* FraudShield
* Risk levels
* 2FA
* Security tickets
* PayRecover
* Smart Retry
* Payment-method optimization
* PaymentOps
* Razorpay Sandbox

This allows merchants, security analysts, and judges to understand the platform directly from the application.

---

# 🔊 Security Feedback

PayShield includes interactive security feedback for important payment decisions.

The application can provide audio/voice feedback alongside visual security states, making the dashboard more interactive during demonstrations.

---

# 📊 Model Performance

PayShield reports performance on held-out test data rather than relying on a single accuracy number.

| Model | Purpose | PR-AUC | ROC-AUC |
|---|---|---:|---:|
| FraudShield | Fraud-risk prediction | **0.333** | **0.811** |
| PayRecover | Failed-payment recovery prediction | **0.461** | **0.704** |
| Smart Retry | Retry-success prediction | **0.574** | **0.707** |

### False-positive cost

For the **AI Risk Manager** track, false positives matter because a legitimate payment can be unnecessarily challenged or held.

PayShield separates:
- **False-positive rate / precision-recall behavior** for model evaluation.
- **Challenge cost** for legitimate transactions sent to 2FA.
- **Potential blocked legitimate transaction value** for legitimate transactions sent to HOLD.

The README intentionally does **not invent a rupee-denominated false-positive cost**. The final submission should report the measured value from the held-out test set using the actual transaction amounts and the chosen operating threshold.

# 🧠 Machine Learning Models

PayShield uses three trained models:

| Model                | Purpose                            |
| -------------------- | ---------------------------------- |
| `fraud_model.pkl`    | Fraud risk prediction              |
| `recovery_model.pkl` | Failed-payment recovery prediction |
| `retry_model.pkl`    | Retry success prediction           |

Model configuration and feature definitions are stored separately in the `config/` directory.

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

The PayShield dashboard provides:

* Total fraud blocked
* Revenue recovered
* Smart Retry performance
* Agentic security tickets
* Risk statistics
* Transaction history
* Security Operations Center
* Current payment decision
* Explainable AI
* PaymentOps analysis

---

# 🛠️ Technology Stack

### Application

* Python
* Streamlit
* Pandas
* NumPy

### Machine Learning

* Scikit-learn
* XGBoost
* Joblib
* Feature engineering
* Predictive modeling

### Generative AI

* Google Gemini API
* Gemini-powered PaymentOps
* Gemini AI Assistant

### Payment Integration

* Razorpay Sandbox
* Razorpay webhook event simulation

### Security

* Authentication
* OTP-based 2FA
* Risk-based payment controls
* Security ticketing

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

The deployment uses the following dependencies:

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

Run the application:

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 👩‍⚖️ Judge Access

### Live application

Use the live Streamlit demo listed above.

### Login

```text
Username: merchant_admin
Password: Provided separately for buildathon evaluation
```

For a public GitHub repository, the judge password is intentionally **not committed to the repository**. Deployment secrets are used for authentication.

### Recommended judge path

1. Login as `merchant_admin`.
2. Select **🤖 AI Model** to evaluate the real ML-driven decision path.
3. Demonstrate a **LOW** transaction → ALLOW.
4. Demonstrate a **MEDIUM** transaction → 2FA → OTP verification.
5. Demonstrate a **HIGH** transaction → HOLD → Security Ticket → PaymentOps analysis.
6. Click **Simulate Failed Payment** → PayRecover AI → Smart Retry AI.
7. Open the manual/AI Assistant to inspect the reasoning and workflow.

> The demo scenario selector exists only for predictable control testing. It should not be presented as the ML model itself.

# 🔐 Configuration

Sensitive credentials should **not** be stored in the GitHub repository.

Configure secrets through your deployment environment.

Example Streamlit secrets:

```toml
AUTH_USERNAMES = "merchant_admin,analyst"
AUTH_PASSWORDS = "your_password_1,your_password_2"
COOKIE_KEY = "your_random_cookie_key"
GEMINI_API_KEY = "your_gemini_api_key"
```

Never commit real passwords, API keys, cookie keys, or other secrets to GitHub.

---

# 🌐 Deployment

PayShield AI is deployed using **Streamlit Community Cloud**.

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

**https://payshield-ai-iblc2arnq6ovzfecwi8tyq.streamlit.app/**

---

# 🎬 Recommended Demo Flow

For the buildathon presentation:

### 1️⃣ AI Fraud Detection

Select:

```text
🤖 AI Model
```

Run a transaction and demonstrate:

```text
Transaction
   ↓
FraudShield ML
   ↓
Fraud Probability
   ↓
Decision Engine
   ↓
AI Recommendation
```

### 2️⃣ Medium-Risk Transaction

Demonstrate:

```text
MEDIUM
   ↓
2FA
   ↓
OTP Verification
   ↓
PAYMENT APPROVED
```

### 3️⃣ High-Risk Transaction

Demonstrate:

```text
HIGH
   ↓
HOLD
   ↓
SECURITY TICKET
   ↓
PaymentOps AI
```

### 4️⃣ Failed Payment Recovery

Click:

```text
❌ Simulate Failed Payment
```

Then demonstrate:

```text
PayRecover AI
   ↓
Recovery Probability
   ↓
Smart Retry
   ↓
Retry-Time Graph
   ↓
Payment Method Recommendation
```

### 5️⃣ Gemini PaymentOps

Ask:

```text
Why was this payment held and what should the merchant do?
```

Gemini converts the payment signals into a clear operational explanation.

---

# 🏆 Why PayShield AI?

PayShield is not simply a fraud classifier and it is not a chatbot placed on top of payments.

It connects **prediction → policy → verification → intervention → recovery → explanation**.

### What makes it different

| Capability | PayShield AI |
|---|---|
| Fraud prediction | Trained ML model |
| Final payment control | Deterministic Decision Engine |
| Customer friction | Risk-based 2FA |
| High-risk response | HOLD + security ticket |
| Failed-payment recovery | Recovery probability model |
| Retry optimization | Smart Retry model |
| Payment-method intervention | Recovery recommendation |
| Operational intelligence | PaymentOps + Gemini |
| Explainability | Risk signals + AI explanation |
| Evaluation | Held-out metrics + explicit FP-cost methodology |
| Safety boundary | Sandbox/simulation, no real-money movement |

The generative AI layer does **not** get unrestricted authority to approve or block payments. The core fraud decision remains with the trained model and deterministic policy layer.



PayShield AI is designed around a simple principle:

> **Don't treat every payment the same.**

Instead:

```text
LOW RISK
   → Minimal friction

MEDIUM RISK
   → Additional verification

HIGH RISK
   → Strong security intervention

FAILED PAYMENT
   → Intelligent recovery
```

This creates a payment-security layer that balances:

**Security + Customer Experience + Revenue Recovery + Merchant Operations**

---

# 🎯 Project Goal

PayShield AI aims to create an intelligent payment protection layer that can:

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

---

# 🔮 Future Scope

The following are intentionally identified as future production improvements rather than claimed as completed functionality:

- Real-time production Razorpay webhook ingestion.
- Production payment-gateway integration.
- Measured batch-level recovered revenue on real/sandbox payment outcomes.
- Explicit compliant escalation and stopping rules for automated recovery.
- Production-grade audit logging for every money-related action.
- Advanced fraud graph and behavioral anomaly models.
- Real-time model monitoring and threshold calibration.
- Automated merchant alerts.
- Continuous model retraining with drift monitoring.
- Multi-agent PaymentOps automation with bounded permissions.



Potential future improvements include:

* Real-time production Razorpay webhook ingestion
* Real payment gateway integration
* Advanced fraud graph models
* Behavioral anomaly detection
* Real-time model monitoring
* Automated merchant alerts
* More sophisticated recovery strategies
* Multi-agent PaymentOps automation
* Adaptive risk thresholds
* Continuous model retraining
* Production-grade audit logging

---

## 🛡️ PayShield AI

### **Prevent Fraud. Reduce Friction. Recover Revenue.**

Built as an AI-powered payment security and recovery prototype for the Razorpay Buildathon.
