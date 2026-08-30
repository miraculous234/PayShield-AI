# 🛡️ PayShield AI

### AI-Powered Payment Protection, Fraud Detection & Payment Recovery Platform

PayShield AI is an intelligent payment security and recovery platform designed to protect digital payments from fraud and improve the success rate of failed transactions.

It combines **FraudShield AI, 2FA Verification, Security Ticketing, PayRecover AI, Smart Retry AI and PaymentOps AI** into one platform.

---

## 🚀 Key Features

### 🛡️ FraudShield AI
- AI-based fraud probability prediction
- Transaction risk scoring
- LOW / MEDIUM / HIGH risk classification
- Real-time payment decision

### 🔐 2FA Verification
Medium-risk transactions trigger an additional verification step.

**Demo OTP:**
`123456`

### 🎫 Security Ticketing
High-risk transactions are automatically placed on HOLD and can generate a security ticket containing:

- Ticket ID
- Transaction amount
- Risk score
- Risk level
- Action
- Creation time
- Ticket status

### 💰 PayRecover AI
Analyzes failed payments and predicts the probability of successful recovery.

### ⏰ Smart Retry AI
Evaluates different retry intervals and recommends the retry time with the highest predicted success probability.

### 🤖 PaymentOps AI
Combines fraud detection and payment recovery into a single payment decision workflow.

---

# 🔄 Payment Decision Flow

```text
PAYMENT RECEIVED
       ↓
🛡️ FRAUDSHIELD AI
       ↓
RISK ASSESSMENT
       ↓
🟢 LOW RISK
       ↓
ALLOW PAYMENT

🟠 MEDIUM RISK
       ↓
2FA VERIFICATION
       ↓
PAYMENT APPROVAL

🔴 HIGH RISK
       ↓
HOLD PAYMENT
       ↓
SECURITY TICKET
       ↓
SECURITY REVIEW

       ↓
❌ PAYMENT FAILURE
       ↓
💰 PAYRECOVER AI
       ↓
⏰ SMART RETRY AI
       ↓
⭐ OPTIMAL RETRY TIME



🧠 Machine Learning Models

PayShield AI uses three trained machine-learning models:

Model	Purpose
fraud_model.pkl	Fraud risk prediction
recovery_model.pkl	Failed-payment recovery prediction
retry_model.pkl	Optimal retry success prediction

📊 Fraud Detection Features

The fraud engine considers factors such as:

Transaction amount
Merchant risk
IP risk
Transaction velocity
Failed transactions
Device type
Payment channel
Geographic distance
Customer transaction history
Customer failure rate
Merchant fraud rate
Transaction timing
💰 Payment Recovery

When a payment fails, PayRecover AI evaluates:

Failure reason
Payment method
Retry count
Minutes since failure
Customer success rate
Payment-method success rate
Previous failures
Device type
Transaction timing
⏰ Smart Retry

The system evaluates retry intervals including:

5 minutes
15 minutes
30 minutes
60 minutes
120 minutes
240 minutes
480 minutes
1440 minutes

The interval with the highest predicted success probability is recommended.

🛠️ Technology Stack
Python
Streamlit
Pandas
NumPy
Scikit-learn
Joblib
XGBoost
Machine Learning
📁 Project Structure
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


▶️ Run Locally

Clone the repository:

git clone https://github.com/YOUR_USERNAME/PayShield-AI.git
cd PayShield-AI

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py

The application will open in your browser.

🌐 Deployment

The application can be deployed using Streamlit Community Cloud.

Deployment flow:

GitHub Repository
       ↓
Streamlit Community Cloud
       ↓
app.py
       ↓
Public PayShield AI URL
🎯 Project Goal

PayShield AI aims to create an intelligent payment protection layer that can:

Detect fraud → Verify users → Hold suspicious payments → Create security tickets → Recover failed payments → Optimize retries

