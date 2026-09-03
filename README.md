# 🛡️ PayShield AI

### AI-Powered Payment Protection, Fraud Detection & Revenue Recovery Platform

**PayShield AI** is an intelligent payment security and revenue recovery platform designed to help merchants **prevent payment fraud, reduce unnecessary payment friction, and recover legitimate revenue from failed transactions**.

It combines **FraudShield AI, a deterministic Decision Engine, 2FA Verification, Security Ticketing, PayRecover AI, Smart Retry AI, PaymentOps AI, Gemini, and Razorpay Sandbox event simulation** into one unified payment-operations platform.

---

## 🌐 Live Demo

🚀 **Try PayShield AI:**
https://payshield-ai-iblc2arnq6ovzfecwi8tyq.streamlit.app/

> **Note:** This is a buildathon prototype. Razorpay payment events are demonstrated using sandbox/webhook simulation and no real customer money is processed.

---

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

PayShield uses three trained machine-learning models.

| Model       | Purpose                  |    PR-AUC |   ROC-AUC |
| ----------- | ------------------------ | --------: | --------: |
| FraudShield | Fraud risk prediction    | **0.333** | **0.811** |
| PayRecover  | Failed-payment recovery  | **0.461** | **0.704** |
| Smart Retry | Retry success prediction | **0.574** | **0.707** |

These metrics demonstrate that the project uses trained predictive models rather than relying only on generative AI.

---

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
