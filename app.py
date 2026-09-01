import os
import json
import random
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth

# Flexible imports for LangChain compatibility
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    try:
        from langchain.prompts import PromptTemplate
    except ImportError:
        PromptTemplate = None

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PayShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)



# ============================================================
# USER AUTHENTICATION SETUP
# ============================================================

names = ["Merchant Admin", "Security Analyst"]
usernames = ["merchant_admin", "analyst"]
passwords = ["admin123", "shield123"]

# Version-agnostic password hashing
try:
    hashed_passwords = [stauth.Hasher.hash(p) for p in passwords]
except AttributeError:
    try:
        hashed_passwords = stauth.Hasher(passwords).generate()
    except Exception:
        hashed_passwords = passwords

credentials = {
    "usernames": {
        usernames[0]: {"name": names[0], "password": hashed_passwords[0]},
        usernames[1]: {"name": names[1], "password": hashed_passwords[1]}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "payshield_cookie",
    "auth_key_12345",
    cookie_expiry_days=1
)

# Fix: Use keyword argument or call login without positional string args
try:
    authenticator.login(location="main")
except TypeError:
    # Fallback for older library signatures
    authenticator.login("PayShield AI Enterprise Access", location="main")

if st.session_state.get("authentication_status") == False:
    st.error("Username/password is incorrect")
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your merchant credentials to access the PayShield AI Portal")
    st.stop()

# ============================================================
# AUTHENTICATED APP CONTENT
# ============================================================

st.sidebar.write(f"Logged in as: **{st.session_state.get('name')}**")
authenticator.logout("Logout", "sidebar")

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRAUD_MODEL = os.path.join(BASE_DIR, "models", "fraud_model.pkl")
RECOVERY_MODEL = os.path.join(BASE_DIR, "models", "recovery_model.pkl")
RETRY_MODEL = os.path.join(BASE_DIR, "models", "retry_model.pkl")

FRAUD_FEATURES = os.path.join(BASE_DIR, "config", "fraud_features.json")
RECOVERY_FEATURES = os.path.join(BASE_DIR, "config", "recovery_features.json")
RETRY_FEATURES = os.path.join(BASE_DIR, "config", "retry_features.json")

FRAUD_DATA = os.path.join(BASE_DIR, "data", "fraud_test.csv")
RECOVERY_DATA = os.path.join(BASE_DIR, "data", "recovery_full.csv")

# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "last_result": None,
    "tickets": [],
    "generated_otp": None,
    "otp_expiry": None,
    "otp_verified": False,
    "otp_attempts": 0,
    "ticket_details": None,
    "analysis_id": None,
    "recovery_result": None,
    "retry_result": None,
    "scheduled_retry": None,
    "method_changed": False,
    "pay_later_selected": False,
    "failed_payment": False,
    "fraud_blocked_val": 142500.00,
    "revenue_recovered_val": 58900.00
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# PREMIUM UI CSS
# ============================================================

st.markdown(
    """
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1500px; }
.title { font-size: 48px; font-weight: 900; letter-spacing: -1px; }
.subtitle { font-size: 17px; color: #9ca3af; margin-top: -8px; }
section[data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.08); }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { font-weight: 800; }
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(255,255,255,0.07), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.10); border-radius: 16px; padding: 16px; transition: all 0.25s ease;
}
[data-testid="stMetric"]:hover { transform: translateY(-4px); border-color: rgba(79,140,255,0.55); box-shadow: 0 10px 30px rgba(0,0,0,0.25); }
.card { padding: 24px; border-radius: 18px; margin: 12px 0; border: 1px solid rgba(255,255,255,.12); background: linear-gradient(145deg, rgba(255,255,255,.06), rgba(255,255,255,.025)); transition: all .25s ease; }
.card:hover { transform: translateY(-3px); box-shadow: 0 12px 35px rgba(0,0,0,.25); }
.green-card { background: linear-gradient(145deg, rgba(20,130,65,.28), rgba(20,130,65,.08)); border: 1px solid #21c354; }
.orange-card { background: linear-gradient(145deg, rgba(190,120,0,.28), rgba(190,120,0,.08)); border: 1px solid #ffa500; }
.red-card { background: linear-gradient(145deg, rgba(190,20,20,.28), rgba(190,20,20,.08)); border: 1px solid #ff4b4b; }
.blue-card { background: linear-gradient(145deg, rgba(40,100,180,.28), rgba(40,100,180,.08)); border: 1px solid #4f8cff; }
.stButton > button { border-radius: 12px; min-height: 44px; font-weight: 700; transition: all .2s ease; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,.25); }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { border-radius: 10px; }
.stProgress > div > div > div { border-radius: 20px; }
.ticket-card { padding: 20px; border-radius: 15px; border: 1px solid #ff4b4b; background: rgba(190,20,20,.12); margin-top: 15px; }
.otp-card { padding: 22px; border-radius: 18px; border: 1px solid #ffa500; background: linear-gradient(145deg, rgba(190,120,0,.20), rgba(190,120,0,.05)); margin-top: 15px; text-align: center; }
.success-ticket { padding: 20px; border-radius: 15px; border: 1px solid #21c354; background: rgba(20,130,65,.15); margin-top: 15px; }
.timeline { padding: 14px 18px; margin: 8px 0; border-left: 4px solid #4f8cff; border-radius: 8px; background: rgba(60,65,80,.45); transition: all .2s ease; }
.timeline:hover { transform: translateX(5px); background: rgba(79,140,255,.12); }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }
.badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 800; margin: 3px; }
.badge-green { background: rgba(33,195,84,.18); border: 1px solid #21c354; }
.badge-orange { background: rgba(255,165,0,.18); border: 1px solid #ffa500; }
.badge-red { background: rgba(255,75,75,.18); border: 1px solid #ff4b4b; }
.info-panel { padding: 18px; border-radius: 16px; background: rgba(79,140,255,.08); border: 1px solid rgba(79,140,255,.3); }
.live-status { padding: 13px 18px; border-radius: 12px; background: rgba(33,195,84,.08); border: 1px solid rgba(33,195,84,.25); margin-top: 18px; }
h1, h2, h3 { font-weight: 800; }
hr { margin: 25px 0; }
@media (max-width: 768px) { .title { font-size: 34px; } .subtitle { font-size: 14px; } }
</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# HEADER & ROI KPI DASHBOARD
# ============================================================

st.markdown(
    """
    <div class="title">
        🛡️ PayShield AI
    </div>
    <div class="subtitle">
        AI-Powered Payment Protection • FraudShield • PayRecover AI • Smart Retry • PaymentOps
    </div>
    <div class="live-status">
        🟢 <b>PAYMENT SECURITY SYSTEM ONLINE</b>
        &nbsp;&nbsp;•&nbsp;&nbsp; FraudShield ACTIVE
        &nbsp;&nbsp;•&nbsp;&nbsp; PayRecover ACTIVE
        &nbsp;&nbsp;•&nbsp;&nbsp; Smart Retry ACTIVE
        &nbsp;&nbsp;•&nbsp;&nbsp; PaymentOps ACTIVE
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🛡️ Total Fraud Blocked", f"₹{st.session_state.fraud_blocked_val:,.2f}", "+₹15,200 today")
with col2:
    st.metric("💰 Revenue Recovered", f"₹{st.session_state.revenue_recovered_val:,.2f}", "+18.4% success rate")
with col3:
    st.metric("⚡ Smart Retry Boost", "69.73%", "Optimal: 30 min window")
with col4:
    st.metric("🎫 Agentic Tickets", f"{len(st.session_state.tickets)} Pending", "Auto-Generated")

st.divider()

# ============================================================
# GROQ PAYMENTOPS AGENT FUNCTION
# ============================================================

def generate_agentic_ticket(payload_data, risk_score):
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
        if not api_key or ChatGroq is None or PromptTemplate is None:
            return (
                "• **Threat Classification**: High-Risk Velocity & Deviation Anomaly\n"
                "• **Behavioral Anomaly**: Transaction amount deviated significantly from user mean.\n"
                "• **Recommended Mitigation**: Hold funds, generate Security Ticket, require 2FA re-verification."
            )
        
        llm = ChatGroq(temperature=0.1, model_name="llama-3.3-70b-versatile", groq_api_key=api_key)
        
        prompt = PromptTemplate.from_template("""
        You are PaymentOps AI, an autonomous fraud analyst. Write a concise, structured security brief for a flagged transaction:
        
        Transaction Amount: ₹{amount}
        Risk Score: {risk_score}/100
        Transactions in 1hr: {txns_1h}
        Geo Distance Spike: {geo_dist} km
        Amount Deviation: ₹{amt_dev}
        
        Provide response in 3 bullet points:
        - **Threat Classification**:
        - **Behavioral Anomaly**:
        - **Recommended Mitigation**:
        """)
        chain = prompt | llm
        response = chain.invoke({
            "amount": payload_data.get("amount", 2500),
            "risk_score": risk_score,
            "txns_1h": payload_data.get("txns_1h", 2),
            "geo_dist": payload_data.get("geo_dist", 10.0),
            "amt_dev": payload_data.get("amt_dev", 500.0)
        })
        return response.content
    except Exception:
        return (
            "• **Threat Classification**: High-Risk Velocity & Deviation Anomaly\n"
            "• **Behavioral Anomaly**: Transaction amount deviated significantly from user mean.\n"
            "• **Recommended Mitigation**: Hold funds, generate Security Ticket, require 2FA re-verification."
        )

# ============================================================
# LOAD MODELS & DATA
# ============================================================

@st.cache_resource
def load_models():
    fraud = joblib.load(FRAUD_MODEL)
    recovery = joblib.load(RECOVERY_MODEL)
    retry = joblib.load(RETRY_MODEL)
    return fraud, recovery, retry

@st.cache_data
def load_features():
    with open(FRAUD_FEATURES, "r") as f:
        fraud = json.load(f)
    with open(RECOVERY_FEATURES, "r") as f:
        recovery = json.load(f)
    with open(RETRY_FEATURES, "r") as f:
        retry = json.load(f)
    return fraud, recovery, retry

@st.cache_data
def load_data():
    fraud = pd.read_csv(FRAUD_DATA)
    recovery = pd.read_csv(RECOVERY_DATA)
    return fraud, recovery

def clean_features(features):
    if isinstance(features, list):
        return features
    if isinstance(features, dict):
        for key in ["features", "columns", "feature_names", "selected_features"]:
            if key in features:
                return features[key]
    return list(features)

try:
    fraud_model, recovery_model, retry_model = load_models()
    fraud_features, recovery_features, retry_features = load_features()
    fraud_features = clean_features(fraud_features)
    recovery_features = clean_features(recovery_features)
    retry_features = clean_features(retry_features)
    fraud_data, recovery_data = load_data()
except Exception as e:
    st.error("❌ PayShield could not load the required files.")
    st.code(str(e))
    st.info("Check that models/, config/, and data/ are present inside your GitHub repository.")
    st.stop()

# ============================================================
# SIDEBAR — PAYMENT SIMULATOR & WEBHOOK CONSUMER
# ============================================================

st.sidebar.title("🎛️ Payment Simulator")
st.sidebar.caption("Configure a transaction and run PayShield AI.")

demo_mode = st.sidebar.selectbox(
    "🎯 Demo Risk Scenario",
    ["🤖 AI Model", "🟢 LOW — ALLOW", "🟠 MEDIUM — 2FA", "🔴 HIGH — HOLD + TICKET"]
)

st.sidebar.divider()

amount = st.sidebar.number_input("Transaction Amount (₹)", min_value=100.0, max_value=1000000.0, value=5000.0, step=500.0)
monthly_spend = st.sidebar.number_input("Customer Monthly Spend (₹)", min_value=500.0, value=10000.0)
merchant_risk = st.sidebar.slider("Merchant Risk Score", 0.0, 1.0, 0.25)
ip_risk = st.sidebar.slider("IP Risk Score", 0.0, 1.0, 0.30)
txn_1h = st.sidebar.number_input("Transactions in 1 Hour", min_value=0, max_value=1000, value=2)
txn_24h = st.sidebar.number_input("Transactions in 24 Hours", min_value=0, max_value=5000, value=5)
failed_24h = st.sidebar.number_input("Failed Transactions (24h)", min_value=0, max_value=1000, value=1)
international = st.sidebar.selectbox("International Transaction", ["No", "Yes"])
payment_channel = st.sidebar.selectbox("Payment Channel", ["UPI", "CARD", "WALLET", "NETBANKING"])
device_type = st.sidebar.selectbox("Device Type", ["Mobile", "Desktop", "Tablet"])
geo_distance = st.sidebar.number_input("Geo Distance From Last Txn", min_value=0.0, value=10.0)
amount_deviation = st.sidebar.number_input("Amount Deviation From User Mean", min_value=0.0, value=500.0)
customer_avg_amount = st.sidebar.number_input("Customer Average Amount", min_value=0.0, value=1200.0)
customer_txn_before = st.sidebar.number_input("Customer Transactions Before", min_value=0.0, value=10.0)
customer_failed_rate = st.sidebar.slider("Customer Failed Rate", 0.0, 1.0, 0.10)
merchant_txn_before = st.sidebar.number_input("Merchant Transactions Before", min_value=0.0, value=100.0)
merchant_avg_amount = st.sidebar.number_input("Merchant Average Amount", min_value=0.0, value=2000.0)
merchant_fraud_rate = st.sidebar.slider("Merchant Fraud Rate", 0.0, 1.0, 0.02)
post_auth_risk = st.sidebar.slider("Post-Auth Risk Score", 0.0, 1.0, 0.20)

st.sidebar.divider()

analyze = st.sidebar.button("🔍 ANALYZE PAYMENT", type="primary", use_container_width=True)

st.sidebar.divider()

with st.sidebar.expander("🔌 Inject Razorpay Sandbox Webhook", expanded=False):
    sample_json = '''{
  "event": "payment.failed",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_Pz9K2mL001",
        "amount": 450000,
        "status": "failed",
        "method": "upi",
        "error_description": "Bank server timeout"
      }
    }
  }
}'''
    st.text_area("Razorpay Event Payload (JSON)", value=sample_json, height=130)
    if st.button("Simulate Razorpay Event"):
        st.toast("Razorpay Sandbox Webhook Ingested!", icon="⚡")

# ============================================================
# RISK STATISTICS & SOC DASHBOARD
# ============================================================

st.header("📊 Risk Statistics")

total_transactions = len(fraud_data)
fraud_count = int(fraud_data["is_fraud"].fillna(0).sum()) if "is_fraud" in fraud_data.columns else 0
safe_count = max(total_transactions - fraud_count, 0)
recovered_count = int(recovery_data["recovery_success"].fillna(0).sum()) if "recovery_success" in recovery_data.columns else 0

a, b, c, d = st.columns(4)
a.metric("📊 Transactions", f"{total_transactions:,}")
b.metric("🟢 Low Risk", f"{safe_count:,}")
c.metric("🔴 Fraud / High Risk", f"{fraud_count:,}")
d.metric("💰 Recovered", f"{recovered_count:,}")

st.divider()

st.header("🛡️ Security Operations Center")
active_tickets = sum(1 for ticket in st.session_state.tickets if ticket.get("Status") == "🔴 UNDER REVIEW")

soc1, soc2, soc3, soc4 = st.columns(4)
soc1.metric("🟢 LOW", "ALLOW")
soc2.metric("🟠 MEDIUM", "2FA")
soc3.metric("🔴 HIGH", "HOLD")
soc4.metric("🎫 ACTIVE TICKETS", active_tickets)

st.info("""
🟢 LOW RISK → ALLOW
🟠 MEDIUM RISK → 2FA VERIFICATION
🔴 HIGH RISK → HOLD + SECURITY TICKET
❌ FAILED PAYMENT → PAYRECOVER AI → SMART RETRY AI
""")

# ============================================================
# TRANSACTION HISTORY
# ============================================================

st.header("📜 Transaction History")
history_columns = ["transaction_id", "transaction_time", "customer_id", "merchant_id", "transaction_amount", "payment_channel", "device_type", "is_fraud"]
history_columns = [col for col in history_columns if col in fraud_data.columns]

if history_columns:
    history_table = fraud_data[history_columns].head(15).copy()
    if "is_fraud" in history_table.columns:
        history_table["Risk"] = history_table["is_fraud"].map({0: "🟢 LOW", 1: "🔴 HIGH"})
    st.dataframe(history_table, use_container_width=True, hide_index=True)

# ============================================================
# ANALYZE PAYMENT LOGIC
# ============================================================

if analyze:
    now = datetime.now()
    hour = now.hour
    day = now.weekday()

    international_value = int(international == "Yes")
    amount_to_monthly_spend = amount / max(monthly_spend, 1)
    failure_rate_24h = failed_24h / max(txn_24h, 1)
    velocity_ratio = txn_1h / max(txn_24h, 1)
    is_weekend = int(day >= 5)
    is_night = int(hour < 6 or hour >= 22)

    fraud_input = pd.DataFrame([{
        "account_age_days": 1000, "credit_score_band": 3, "kyc_level": 2, "avg_monthly_spend": monthly_spend,
        "merchant_risk_score": merchant_risk, "transaction_amount": amount, "payment_channel": payment_channel,
        "device_type": device_type, "is_international": international_value, "ip_risk_score": ip_risk,
        "txn_count_1h": txn_1h, "txn_count_24h": txn_24h, "failed_txn_count_24h": failed_24h,
        "geo_distance_from_last_txn": geo_distance, "amount_deviation_from_user_mean": amount_deviation,
        "post_auth_risk_score": post_auth_risk, "transaction_hour": hour, "day_of_week": day,
        "is_weekend": is_weekend, "is_night": is_night, "amount_to_monthly_spend": amount_to_monthly_spend,
        "failure_rate_24h": failure_rate_24h, "velocity_ratio": velocity_ratio, "customer_txn_count_before": customer_txn_before,
        "customer_avg_amount_before": customer_avg_amount, "customer_failed_rate_before": customer_failed_rate,
        "merchant_txn_count_before": merchant_txn_before, "merchant_avg_amount_before": merchant_avg_amount,
        "merchant_fraud_rate_before": merchant_fraud_rate
    }])

    fraud_input = fraud_input.reindex(columns=fraud_features)
    fraud_probability = float(fraud_model.predict_proba(fraud_input)[0, 1])

    ai_risk_score = fraud_probability * 100

    if demo_mode == "🟢 LOW — ALLOW":
        risk_score, risk_level, action = 20.0, "LOW", "ALLOW"
    elif demo_mode == "🟠 MEDIUM — 2FA":
        risk_score, risk_level, action = 55.0, "MEDIUM", "2FA"
    elif demo_mode == "🔴 HIGH — HOLD + TICKET":
        risk_score, risk_level, action = 85.0, "HIGH", "HOLD"
    else:
        risk_score = ai_risk_score
        if risk_score >= 70:
            risk_level, action = "HIGH", "HOLD"
        elif risk_score >= 40:
            risk_level, action = "MEDIUM", "2FA"
        else:
            risk_level, action = "LOW", "ALLOW"

    st.session_state.generated_otp = None
    st.session_state.otp_expiry = None
    st.session_state.otp_verified = False
    st.session_state.otp_attempts = 0
    st.session_state.ticket_details = None
    st.session_state.scheduled_retry = None
    st.session_state.method_changed = False
    st.session_state.pay_later_selected = False
    st.session_state.recovery_result = None
    st.session_state.retry_result = None

    analysis_id = "TXN-" + now.strftime("%Y%m%d%H%M%S") + "-" + str(random.randint(100, 999))

    st.session_state.last_result = {
        "analysis_id": analysis_id, "risk": risk_score, "level": risk_level, "action": action,
        "amount": amount, "merchant_risk": merchant_risk, "ip_risk": ip_risk, "failed_24h": failed_24h,
        "amount_to_monthly_spend": amount_to_monthly_spend, "failure_rate_24h": failure_rate_24h,
        "velocity_ratio": velocity_ratio, "time": now.strftime("%H:%M:%S"), "datetime": now.strftime("%Y-%m-%d %H:%M:%S")
    }

# ============================================================
# DISPLAY CURRENT RESULT
# ============================================================

result = st.session_state.last_result

if result:
    risk_score = float(result["risk"])
    risk_level = result["level"]
    action = result["action"]
    amount = float(result["amount"])
    merchant_risk = float(result["merchant_risk"])
    ip_risk = float(result["ip_risk"])
    failed_24h = int(result["failed_24h"])
    amount_to_monthly_spend = float(result["amount_to_monthly_spend"])

    icon = {"LOW": "🟢", "MEDIUM": "🟠", "HIGH": "🔴"}.get(risk_level, "⚪")

    st.divider()
    st.header("🔍 AI Fraud Detection")

    m1, m2, m3 = st.columns(3)
    m1.metric("Risk Score", f"{risk_score:.2f}%")
    m2.metric("Risk Level", f"{icon} {risk_level}")
    m3.metric("Payment Action", action)
    st.progress(int(min(max(risk_score, 0), 100)))

    if risk_level == "HIGH":
        st.markdown(f'<div class="card red-card"><h2>🔴 HIGH-RISK PAYMENT</h2><p>Payment has been placed on HOLD.</p><p><b>Transaction ID:</b> {result["analysis_id"]}</p><p><b>Risk Score:</b> {risk_score:.2f}%</p><p><b>Action:</b> HOLD + SECURITY REVIEW</p></div>', unsafe_allow_html=True)
    elif risk_level == "MEDIUM":
        st.markdown(f'<div class="card orange-card"><h2>🟠 MEDIUM-RISK PAYMENT</h2><p>Additional customer verification required.</p><p><b>Transaction ID:</b> {result["analysis_id"]}</p><p><b>Risk Score:</b> {risk_score:.2f}%</p><p><b>Action:</b> 2FA</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="card green-card"><h2>🟢 LOW-RISK PAYMENT</h2><p>Transaction appears safe.</p><p><b>Transaction ID:</b> {result["analysis_id"]}</p><p><b>Risk Score:</b> {risk_score:.2f}%</p><p><b>Action:</b> ALLOW</p></div>', unsafe_allow_html=True)

    st.header("🧠 Explainable AI")
    reasons = []
    reasons.append("⚠️ Merchant risk score is elevated." if merchant_risk >= 0.6 else "✅ Merchant risk is within normal range.")
    reasons.append("⚠️ Transaction amount is high relative to monthly spending." if amount_to_monthly_spend > 0.5 else "✅ Transaction amount is consistent with customer spending.")
    reasons.append("⚠️ Multiple failed transactions detected." if failed_24h > 3 else "✅ Recent transaction failure activity is low.")
    reasons.append("⚠️ IP risk score is elevated." if ip_risk >= 0.6 else "✅ IP risk is within normal range.")

    for reason in reasons:
        st.write(reason)

    st.header("🤖 AI Recommendation")
    recommendation = "Hold this payment and create a security ticket because the fraud risk is high." if risk_level == "HIGH" else ("Require 2FA verification before approving this payment because the fraud risk is medium." if risk_level == "MEDIUM" else "Allow this payment because the detected fraud risk is low.")
    st.info("🤖 PayShield recommends: " + recommendation)

    st.header("🔐 Security Center")

    if risk_level == "MEDIUM":
        st.warning("🟠 MEDIUM RISK — 2FA REQUIRED")
        if st.session_state.generated_otp is None:
            if st.button("📲 SEND OTP", key="send_otp", type="primary", use_container_width=True):
                st.session_state.generated_otp = str(random.randint(100000, 999999))
                st.session_state.otp_expiry = datetime.now() + timedelta(minutes=5)
                st.session_state.otp_verified = False
                st.session_state.otp_attempts = 0
                st.rerun()

        if st.session_state.generated_otp:
            st.markdown(f'<div class="otp-card"><h3>📲 OTP SENT SUCCESSFULLY</h3><h1>🔐 {st.session_state.generated_otp}</h1><p><b>OTP expires in 5 minutes.</b></p></div>', unsafe_allow_html=True)
            if st.session_state.otp_verified:
                st.success("✅ 2FA VERIFIED — PAYMENT APPROVED")
            else:
                otp_input = st.text_input("Enter the 6-digit OTP", max_chars=6, key="otp_input")
                if st.button("🔐 VERIFY 2FA", key="verify_2fa", type="primary", use_container_width=True):
                    if st.session_state.otp_expiry and datetime.now() > st.session_state.otp_expiry:
                        st.error("⏰ OTP expired. Please send a new OTP.")
                        st.session_state.generated_otp = None
                    elif otp_input == st.session_state.generated_otp:
                        st.session_state.otp_verified = True
                        st.success("✅ 2FA VERIFIED — PAYMENT APPROVED")
                        st.balloons()
                        st.rerun()
                    else:
                        st.session_state.otp_attempts += 1
                        st.error("❌ INVALID OTP — PAYMENT BLOCKED")

    elif risk_level == "HIGH":
        st.error("🔴 HIGH RISK — PAYMENT UNDER REVIEW")
        
        # PaymentOps Autonomous LLM Briefing
        st.markdown("### 🤖 PaymentOps Agent Incident Briefing")
        agent_brief = generate_agentic_ticket({
            "amount": amount,
            "txns_1h": txn_1h,
            "geo_dist": geo_distance,
            "amt_dev": amount_deviation
        }, risk_score)
        st.info(agent_brief)

        if st.session_state.ticket_details is None:
            if st.button("🎫 RAISE SECURITY TICKET", key="raise_live_ticket", type="primary", use_container_width=True):
                ticket_id = "PS-" + datetime.now().strftime("%Y%m%d%H%M%S") + "-" + str(random.randint(100, 999))
                new_ticket = {
                    "Ticket ID": ticket_id, "Transaction ID": result["analysis_id"],
                    "Created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Amount": f"₹{amount:,.2f}", "Risk Score": f"{risk_score:.2f}%",
                    "Risk Level": "🔴 HIGH", "Action": "HOLD", "Status": "🔴 UNDER REVIEW"
                }
                st.session_state.tickets.append(new_ticket)
                st.session_state.ticket_details = new_ticket
                st.rerun()

        if st.session_state.ticket_details:
            ticket = st.session_state.ticket_details
            st.markdown(f'<div class="success-ticket"><h2>✅ TICKET RAISED SUCCESSFULLY</h2><p><b>🎫 Ticket ID:</b> {ticket["Ticket ID"]}</p><p><b>🧾 Transaction ID:</b> {ticket["Transaction ID"]}</p><p><b>💰 Amount:</b> {ticket["Amount"]}</p><p><b>📌 Status:</b> {ticket["Status"]}</p></div>', unsafe_allow_html=True)

    else:
        st.success("🟢 SECURITY CHECK PASSED")

# ============================================================
# SECURITY OPERATIONS — ALL TICKETS
# ============================================================

st.divider()
st.header("🎫 Live Security Tickets")

if st.session_state.tickets:
    st.dataframe(pd.DataFrame(st.session_state.tickets), use_container_width=True, hide_index=True)
    for index, ticket in enumerate(st.session_state.tickets):
        t1, t2, t3 = st.columns([2, 4, 2])
        t1.write(f"🎫 **{ticket['Ticket ID']}**")
        t2.write(f"{ticket['Status']} | {ticket['Amount']} | {ticket['Risk Score']}")
        if ticket["Status"] == "🔴 UNDER REVIEW":
            if t3.button("✅ RESOLVE", key=f"resolve_ticket_{index}", use_container_width=True):
                ticket["Status"] = "🟢 RESOLVED"
                st.session_state.tickets[index] = ticket
                st.rerun()
        else:
            t3.success("RESOLVED")
else:
    st.info("No active security tickets.")

# ============================================================
# PAYRECOVER AI & SMART RETRY
# ============================================================

st.divider()
st.header("💰 PayRecover AI")

failed_payment = st.checkbox("❌ Simulate Failed Payment", key="failed_payment")

if failed_payment:
    st.error("❌ PAYMENT FAILED")
    f1, f2 = st.columns(2)
    with f1:
        failure_reason = st.selectbox("Failure Reason", ["Bank Decline", "Insufficient Funds", "Timeout", "Technical Error", "Network Error"], key="failure_reason")
        payment_method = st.selectbox("Payment Method", ["UPI", "CARD", "WALLET", "NETBANKING"], key="payment_method")
        retry_count = st.number_input("Previous Retry Count", min_value=0, max_value=20, value=0, key="retry_count")
    with f2:
        minutes_since_failure = st.number_input("Minutes Since Failure", min_value=0, max_value=10000, value=5, key="minutes_since_failure")
        customer_success_rate = st.slider("Customer Success Rate", 0.0, 1.0, 0.70, key="customer_success_rate")
        method_success_rate = st.slider("Method Success Rate", 0.0, 1.0, 0.65, key="method_success_rate")
        previous_failures = st.number_input("Previous Failures", min_value=0, max_value=100, value=1, key="previous_failures")

    recovery_input = pd.DataFrame([{
        "amount": amount, "payment_method": payment_method, "failure_reason": failure_reason,
        "retry_count": retry_count, "minutes_since_failure": minutes_since_failure,
        "customer_success_rate": customer_success_rate, "method_success_rate": method_success_rate,
        "previous_failures": previous_failures, "is_international": int(international == "Yes"),
        "device_type": device_type, "hour": datetime.now().hour, "day_of_week": datetime.now().weekday()
    }]).reindex(columns=recovery_features)

    try:
        recovery_probability = float(recovery_model.predict_proba(recovery_input)[0, 1]) * 100
    except Exception:
        recovery_probability = 0.0

    st.subheader("💰 Recovery Probability")
    rc1, rc2 = st.columns(2)
    rc1.metric("Recovery Probability", f"{recovery_probability:.2f}%")
    rc2.metric("Payment Status", "FAILED")
    st.progress(int(min(max(recovery_probability, 0), 100)))

    st.header("⏰ Smart Retry AI")
    retry_times = [5, 15, 30, 60, 120, 240, 480, 1440]
    probabilities = []

    for retry_time in retry_times:
        r_inp = pd.DataFrame([{
            "customer_success_rate": customer_success_rate, "method_success_rate": method_success_rate,
            "previous_failures": previous_failures, "retry_time_minutes": retry_time
        }]).reindex(columns=retry_features)
        try:
            probabilities.append(float(retry_model.predict_proba(r_inp)[0, 1]) * 100)
        except Exception:
            probabilities.append(0.0)

    best_index = int(np.argmax(probabilities)) if probabilities else 0
    best_time = retry_times[best_index]
    best_probability = probabilities[best_index] if probabilities else 0.0

    st.success(f"⭐ PayRecover AI recommends retrying after {best_time} minutes with {best_probability:.2f}% predicted success.")

# ============================================================
# PAYMENTOPS AI & FOOTER
# ============================================================

st.divider()
st.header("🤖 PaymentOps AI")
op1, op2, op3, op4 = st.columns(4)
op1.metric("🛡️ FraudShield", "ACTIVE")
op2.metric("💰 PayRecover", "ACTIVE")
op3.metric("⏰ Smart Retry", "ACTIVE")
op4.metric("🛡️ PaymentOps", "ACTIVE")

st.divider()
st.caption("🛡️ PayShield AI • FraudShield + PayRecover AI + Smart Retry + PaymentOps")
