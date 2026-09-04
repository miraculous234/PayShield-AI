# 🛡️ PayShield AI

### Autonomous Payment Protection, Operations & Revenue Recovery

> **Razorpay AI Buildathon 2026 — AI Risk Manager + AI Revenue Recovery**

PayShield AI is an end-to-end payment intelligence system that combines **FraudShield, PaymentOps, PayRecover, and Smart Retry** into one merchant-facing workflow.

Instead of treating fraud, payment failures, and operational incidents as separate problems, PayShield connects them across the payment lifecycle:

```text
DETECT → DECIDE → RESPOND → RECOVER
```

### The core idea

> **Don't treat every payment the same.**

A low-risk transaction should move smoothly.

A medium-risk transaction should receive additional verification.

A high-risk transaction should be stopped and escalated.

And when a legitimate payment fails, the system should determine whether the revenue can still be recovered and choose an intelligent retry strategy.

---

# 🚀 Judge Quick Start

## 🌐 Live Demo

### 👉 [Launch PayShield AI](https://payshield-ai-iblc2arnq6ovzfecwi8tyq.streamlit.app/)

**No login is required.**

The application is a public buildathon prototype using sandbox/simulated payment events. It does not process real customer money.

---

# ⚡ What PayShield AI Does

PayShield combines four major capabilities:

### 🛡️ FraudShield

Detects transaction risk using machine-learning signals.

### 🧠 Decision Engine

Converts the ML risk probability into a bounded operational action:

```text
LOW       → ALLOW
MEDIUM    → 2FA
HIGH      → HOLD + SECURITY TICKET
```

### 🚨 PaymentOps

Turns security and payment signals into an operational incident briefing, recommended action, and merchant-friendly explanation.

### 💰 PayRecover + Smart Retry

When a legitimate payment fails:

```text
PAYMENT FAILED
      ↓
PAYRECOVER AI
      ↓
RECOVERY PROBABILITY
      ↓
SMART RETRY AI
      ↓
BEST RETRY WINDOW
      ↓
PAYMENT METHOD
      ↓
RECOVERY RECOMMENDATION
```

---

# 🎯 The Complete Payment Lifecycle

```text
                    PAYMENT
                       │
                       ▼
              🛡️ FRAUDSHIELD AI
                       │
                       ▼
                FRAUD PROBABILITY
                       │
                       ▼
                🧠 DECISION ENGINE
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
         🟢 LOW     🟠 MEDIUM    🔴 HIGH
            │          │          │
         ALLOW        2FA        HOLD
                       │          │
                       ▼          ▼
                  VERIFY OTP   SECURITY TICKET
                       │          │
                       └────┬─────┘
                            ▼
                      PAYMENT OPS
                            │
                            │
                IF PAYMENT FAILS
                            ▼
                    💰 PAYRECOVER
                            │
                            ▼
                   RECOVERY PROBABILITY
                            │
                            ▼
                    ⏰ SMART RETRY
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
             RETRY TIME          PAYMENT METHOD
                 │                     │
                 └──────────┬──────────┘
                            ▼
                  RECOVERY RECOMMENDATION
```

This is the central concept behind PayShield AI.

---

# 🛡️ FraudShield AI

FraudShield is the machine-learning risk detection layer.

It evaluates transaction and behavioral signals including:

* Transaction amount
* Customer monthly spending
* Merchant risk score
* IP risk score
* Transaction velocity
* Failed transaction history
* Payment channel
* Device type
* Geographic distance
* Customer transaction history
* Customer failure rate
* Merchant transaction history
* Merchant fraud rate
* Transaction timing
* Amount deviation from normal customer behavior

The model produces a fraud-risk probability.

However, the ML model does **not** independently control the final payment action.

---

# 🧠 Deterministic Decision Engine

The Decision Engine sits between prediction and payment action.

```text
FraudShield ML
      ↓
Fraud Probability
      ↓
Deterministic Policy
      ↓
┌────────────┬─────────────┬──────────────┐
│ LOW        │ MEDIUM      │ HIGH         │
│ 0–39       │ 40–69       │ 70–100       │
│            │             │              │
│ ALLOW      │ 2FA         │ HOLD         │
│            │             │ +            │
│            │             │ SECURITY     │
│            │             │ TICKET       │
└────────────┴─────────────┴──────────────┘
```

This separation makes the security workflow:

**Predictable + Bounded + Auditable**

The ML model predicts risk.

The deterministic policy controls the response.

---

# 🔐 Risk-Based 2FA

Medium-risk transactions trigger step-up verification instead of being immediately blocked.

```text
MEDIUM RISK
     ↓
2FA REQUIRED
     ↓
OTP GENERATED
     ↓
OTP VERIFICATION
     ↓
PAYMENT APPROVED
```

The prototype includes:

* OTP generation
* OTP expiry
* OTP verification
* Failed-attempt tracking
* Maximum-attempt protection
* Approval after successful verification

The 2FA mechanism is intended for demonstration and is not presented as production authentication infrastructure.

---

# 🔴 High-Risk Intervention

When a transaction crosses the configured high-risk threshold:

```text
HIGH RISK
    ↓
HOLD
    ↓
SECURITY TICKET
    ↓
PAYMENTOPS
    ↓
INCIDENT ANALYSIS
```

The security ticket can contain:

* Ticket ID
* Transaction ID
* Transaction amount
* Fraud probability
* Risk level
* Payment action
* Creation time
* Ticket status
* Security recommendation

This turns a model prediction into an operational security response.

---

# 🚨 PaymentOps AI

PaymentOps is the operational intelligence layer connecting the ML decision to merchant action.

It answers:

> **What happened? Why did it happen? What should the merchant do next?**

PaymentOps can organize information into:

### Incident Summary

What happened to the transaction.

### Problem Detected

The signals associated with the intervention.

### Business Impact

The potential operational impact.

### Recommended Action

What the merchant or security team should do.

### AI Assessment

A natural-language explanation of the incident.

---

# 🤖 Gemini's Role

PayShield uses Gemini for **explanation and operational intelligence**.

Gemini is not the sole authority for approving or blocking payments.

The critical security path remains:

```text
ML MODEL
   ↓
RISK PROBABILITY
   ↓
DETERMINISTIC POLICY
   ↓
ALLOW / 2FA / HOLD
```

This separation is intentional.

---

# 🌙 What Happens If Something Breaks at 2 AM?

PayShield is designed around failure handling rather than only the happy path.

Potential failures include:

* LLM unavailable
* Unexpected webhook fields
* Invalid model input
* OTP expiry
* Too many OTP attempts
* Payment failure
* Runtime/interface mismatch

The LLM is separated from the core fraud decision, so an LLM failure does not have to become a payment-security failure.

During development, a runtime issue was encountered involving a mismatch between the function interface and the arguments being passed to it. The issue was traced through the error, the interface was corrected, the model input was verified, and the application was redeployed.

This reinforced an important design principle:

> **A payment system has to handle failure, not just success.**

---

# 💰 PayRecover AI

Fraud prevention protects the payment system, but legitimate payment failures can still create revenue loss.

PayRecover AI addresses the second side of the problem.

When a payment fails, it evaluates the payment context and estimates the probability that the payment can still be recovered.

The prototype can simulate:

```text
PAYMENT FAILED
      ↓
FAILURE ANALYSIS
      ↓
RECOVERY PROBABILITY
      ↓
RECOVERY RECOMMENDATION
```

The demo uses simulated/sandbox events and does not move real money.

---

# ⏰ Smart Retry AI

Retrying immediately is not always the best strategy.

Smart Retry evaluates multiple retry windows:

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

The trained model predicts the expected success probability for each option.

The strongest predicted option becomes the recommended retry window.

The interface can show:

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

The values are generated by the trained model for the transaction being evaluated.

---

# 💳 Payment Method Recommendation

PayShield can work with payment-method categories such as:

* UPI
* Card
* Wallet
* Netbanking

Instead of simply recommending:

> **Try again later.**

the recovery workflow can recommend:

> **Try again later using a more suitable payment method.**

---

# 🔌 Razorpay Sandbox / Webhook Simulation

PayShield includes a sandbox/event simulation layer demonstrating how payment events can enter the system.

Example:

```text
Razorpay Event
     ↓
payment.failed
     ↓
PayShield
     ↓
PayRecover AI
     ↓
Smart Retry AI
     ↓
Recovery Recommendation
```

The buildathon demo does not process real customer payments.

---

# 📊 Model Performance

The models were evaluated using held-out test data.

| Model       | Purpose                            |    PR-AUC |   ROC-AUC |
| ----------- | ---------------------------------- | --------: | --------: |
| FraudShield | Fraud-risk prediction              | **0.333** | **0.811** |
| PayRecover  | Failed-payment recovery prediction | **0.461** | **0.704** |
| Smart Retry | Retry-success prediction           | **0.574** | **0.707** |

### Why PR-AUC?

Fraud datasets are imbalanced, so PR-AUC is useful for evaluating positive-class performance rather than relying on accuracy alone.

---

# ⚠️ False-Positive Cost

For fraud prevention, false positives matter.

A legitimate customer can experience:

* An unnecessary 2FA challenge
* A delayed payment
* A payment being placed on HOLD

PayShield therefore separates:

* Model precision/recall behavior
* Challenge cost for legitimate transactions
* Potential value affected by legitimate transactions sent to HOLD

The project intentionally does **not invent a rupee-denominated false-positive cost**.

The selected operating point should be evaluated using actual held-out transaction amounts and the configured decision threshold.

---

# 🏆 Razorpay Buildathon Alignment

## Track 02 — AI Risk Manager

PayShield demonstrates:

* ML-based fraud-risk prediction
* Held-out evaluation
* Fraud probability scoring
* Deterministic decisioning
* LOW / MEDIUM / HIGH risk classification
* Risk-based 2FA
* HOLD + security ticketing
* Explainable operational decisions
* PR-AUC and ROC-AUC evaluation
* False-positive-cost methodology
* Defense-only security use case

## Track 03 — AI Revenue Recovery

PayShield demonstrates:

* Failed-payment classification
* Recovery probability prediction
* Smart retry optimization
* Multiple retry-window evaluation
* Payment-method recommendation
* Simulated payment-failure events
* Recovery recommendations
* Operational explanations

### Prototype boundary

The current project does not claim:

* Real-money recovery
* Production payment authorization
* Unrestricted autonomous movement of funds
* Production-grade webhook infrastructure
* Production-grade audit infrastructure

These are future production requirements.

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

### Payment Integration Concept

* Razorpay sandbox/event simulation
* Webhook-style payment events

### Security

* Risk-based controls
* OTP-based 2FA
* Security ticketing
* Deterministic decision policy

---

# 📁 Project Structure

```text
PayShield-AI/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
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
├── data/
│   ├── fraud_test.csv
│   └── recovery_full.csv
│
└── .devcontainer/
    └── ...
```

### Repository organization

```text
app.py
    ↓
Main Streamlit application

models/
    ↓
Trained ML models

config/
    ↓
Feature definitions + evaluation metrics

data/
    ↓
Datasets used by the prototype

README.md
    ↓
Project documentation

requirements.txt
    ↓
Python dependencies
```

Large training datasets and temporary/generated files should not be committed unless they are intentionally required by the deployed application.

---

# 📦 Requirements

Use the same scikit-learn version that was used to create the trained model.

```txt
streamlit
joblib
numpy<2.0.0
pandas
scikit-learn==1.6.1
xgboost
streamlit-authenticator==0.2.3
bcrypt
google-genai
```

> `streamlit-authenticator` and `bcrypt` may remain in the environment from earlier development, although the current public demo does not require a login.

---

# 🔐 Configuration

Sensitive credentials must never be committed to GitHub.

For example:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
```

Never commit:

* API keys
* Passwords
* Authentication secrets
* Cookie keys
* Private credentials

---

# ▶️ Run Locally

```bash
git clone https://github.com/miraculous234/PayShield-AI.git
cd PayShield-AI
pip install -r requirements.txt
streamlit run app.py
```

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

👉 https://payshield-ai-iblc2arnq6ovzfecwi8tyq.streamlit.app/

---

# 🎬 Recommended Buildathon Demo

For the 5-minute presentation:

```text
1. Dashboard
      ↓
2. FraudShield AI
      ↓
3. 55% MEDIUM transaction
      ↓
4. 2FA verification
      ↓
5. HIGH-risk HOLD + security ticket
      ↓
6. PaymentOps incident briefing
      ↓
7. “What happens at 2 AM?”
      ↓
8. Simulate Failed Payment
      ↓
9. PayRecover AI
      ↓
10. Smart Retry AI
      ↓
11. Model metrics
      ↓
12. Closing
```

---

# 💡 Why PayShield AI?

PayShield AI is not simply a fraud classifier.

It is not simply a recovery model.

And it is not a chatbot placed on top of payments.

It connects specialized intelligence across the payment lifecycle:

```text
              PAYSHIELD AI
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   FRAUDSHIELD  PAYMENTOPS  PAYRECOVER
       │           │           │
       ▼           ▼           ▼
     RISK       RESPOND      RECOVER
       │                       │
       ▼                       ▼
 DECISION ENGINE          SMART RETRY
       │                       │
       └───────────┬───────────┘
                   ▼
          PAYMENT INTELLIGENCE
```

### The four questions PayShield answers

**FraudShield:**

> Should I trust this transaction?

**Decision Engine:**

> What should I do about the risk?

**PaymentOps:**

> What happened and what should the operations team do?

**PayRecover + Smart Retry:**

> Can this failed revenue be recovered, and what is the best way to retry?

That is why PayShield AI is designed as **one payment intelligence system rather than four disconnected features.**

---

# 🎯 Project Goal

PayShield AI aims to balance:

**Security + Customer Experience + Revenue Recovery + Merchant Operations**

The complete objective is:

```text
Detect Fraud
     ↓
Assess Risk
     ↓
Make a Bounded Decision
     ↓
Verify or Hold
     ↓
Create Operational Response
     ↓
Understand Payment Failure
     ↓
Estimate Recovery
     ↓
Optimize Retry
     ↓
Recommend Recovery Action
```

---

# 🔮 Future Scope

Future production improvements include:

* Real-time Razorpay webhook ingestion
* Production payment-gateway integration
* Batch-level measured recovered revenue
* Compliant automated recovery stopping rules
* Production-grade audit logging
* Advanced fraud graph/anomaly models
* Real-time model monitoring
* Threshold calibration
* Automated merchant alerts
* Model drift monitoring
* Continuous retraining
* Bounded multi-agent PaymentOps automation
* Adaptive risk thresholds
* More advanced recovery strategies

---

# 🛡️ PayShield AI

### **Prevent Fraud. Reduce Friction. Recover Revenue.**

Built as an AI-powered payment security, operations, and revenue-recovery prototype for the **Razorpay AI Buildathon 2026**.
