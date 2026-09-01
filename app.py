
import os
import json
import random
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd
import streamlit as st


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

    # Recovery
    "recovery_result": None,
    "retry_result": None,
    "scheduled_retry": None,

    # IMPORTANT - correct names
    "method_changed": False,
    "pay_later_selected": False,

    # 2FA popup
    "show_2fa_popup": False,

    # Failed payment
    "failed_payment": False
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# PREMIUM UI CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* MAIN TITLE */
.title {
    font-size: 48px;
    font-weight: 900;
    letter-spacing: -1px;
}

.subtitle {
    font-size: 17px;
    color: #9ca3af;
    margin-top: -8px;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-weight: 800;
}

/* METRIC CARDS */
[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        rgba(255,255,255,0.06),
        rgba(255,255,255,0.02)
    );
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 16px;
    transition: all 0.25s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    border-color: rgba(79,140,255,0.55);
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

/* GENERAL CARDS */
.card {
    padding: 24px;
    border-radius: 18px;
    margin: 12px 0;
    border: 1px solid rgba(255,255,255,.12);
    background: linear-gradient(
        145deg,
        rgba(255,255,255,.06),
        rgba(255,255,255,.025)
    );
    transition: all .25s ease;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0,0,0,.25);
}

/* RISK CARDS */
.green-card {
    background: linear-gradient(
        145deg,
        rgba(20,130,65,.28),
        rgba(20,130,65,.08)
    );
    border: 1px solid #21c354;
}

.orange-card {
    background: linear-gradient(
        145deg,
        rgba(190,120,0,.28),
        rgba(190,120,0,.08)
    );
    border: 1px solid #ffa500;
}

.red-card {
    background: linear-gradient(
        145deg,
        rgba(190,20,20,.28),
        rgba(190,20,20,.08)
    );
    border: 1px solid #ff4b4b;
}

.blue-card {
    background: linear-gradient(
        145deg,
        rgba(40,100,180,.28),
        rgba(40,100,180,.08)
    );
    border: 1px solid #4f8cff;
}

/* BUTTONS */
.stButton > button {
    border-radius: 12px;
    min-height: 44px;
    font-weight: 700;
    transition: all .2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,.25);
}

/* PRIMARY ANALYZE BUTTON */
.stButton > button[kind="primary"] {
    border-radius: 14px;
    font-weight: 800;
}

/* INPUTS */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    border-radius: 10px;
}

/* PROGRESS BAR */
.stProgress > div > div > div {
    border-radius: 20px;
}

/* TICKET */
.ticket-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #ff4b4b;
    background: rgba(190,20,20,.12);
    margin-top: 15px;
}

/* OTP */
.otp-card {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #ffa500;
    background: linear-gradient(
        145deg,
        rgba(190,120,0,.20),
        rgba(190,120,0,.05)
    );
    margin-top: 15px;
    text-align: center;
}

/* SUCCESS */
.success-ticket {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #21c354;
    background: rgba(20,130,65,.15);
    margin-top: 15px;
}

/* TIMELINE */
.timeline {
    padding: 14px 18px;
    margin: 8px 0;
    border-left: 4px solid #4f8cff;
    border-radius: 8px;
    background: rgba(60,65,80,.45);
    transition: all .2s ease;
}

.timeline:hover {
    transform: translateX(5px);
    background: rgba(79,140,255,.12);
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* SECTION HEADERS */
h1, h2, h3 {
    font-weight: 800;
}

/* DIVIDERS */
hr {
    margin: 25px 0;
}

/* BADGES */
.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 800;
    margin: 3px;
}

.badge-green {
    background: rgba(33,195,84,.18);
    border: 1px solid #21c354;
}

.badge-orange {
    background: rgba(255,165,0,.18);
    border: 1px solid #ffa500;
}

.badge-red {
    background: rgba(255,75,75,.18);
    border: 1px solid #ff4b4b;
}

/* INFO BOX */
.info-panel {
    padding: 18px;
    border-radius: 16px;
    background: rgba(79,140,255,.08);
    border: 1px solid rgba(79,140,255,.3);
}

/* MOBILE */
@media (max-width: 768px) {
    .title {
        font-size: 34px;
    }

    .subtitle {
        font-size: 14px;
    }
}

</style>
""", unsafe_allow_html=True)
    
# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="title">🛡️ PayShield AI</div>
    <div class="subtitle">
        AI-Powered Payment Protection • FraudShield •
        PayRecover AI • Smart Retry • PaymentOps
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        margin-top:18px;
        padding:12px 18px;
        border-radius:12px;
        background:rgba(33,195,84,.08);
        border:1px solid rgba(33,195,84,.25);
    ">
        🟢 <b>PAYMENT SECURITY SYSTEM ONLINE</b>
        &nbsp;&nbsp;•&nbsp;&nbsp;
        FraudShield ACTIVE
        &nbsp;&nbsp;•&nbsp;&nbsp;
        PayRecover ACTIVE
        &nbsp;&nbsp;•&nbsp;&nbsp;
        PaymentOps ACTIVE
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# LOAD MODELS
# ============================================================

@st.cache_resource
def load_models():
    fraud = joblib.load(FRAUD_MODEL)
    recovery = joblib.load(RECOVERY_MODEL)
    retry = joblib.load(RETRY_MODEL)
    return fraud, recovery, retry


# ============================================================
# LOAD FEATURES
# ============================================================

@st.cache_data
def load_features():

    with open(FRAUD_FEATURES, "r") as f:
        fraud = json.load(f)

    with open(RECOVERY_FEATURES, "r") as f:
        recovery = json.load(f)

    with open(RETRY_FEATURES, "r") as f:
        retry = json.load(f)

    return fraud, recovery, retry


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    fraud = pd.read_csv(FRAUD_DATA)
    recovery = pd.read_csv(RECOVERY_DATA)

    return fraud, recovery


# ============================================================
# SAFE FEATURE LOADER
# ============================================================

def clean_features(features):

    if isinstance(features, list):
        return features

    if isinstance(features, dict):

        for key in [
            "features",
            "columns",
            "feature_names",
            "selected_features"
        ]:

            if key in features:
                return features[key]

    return list(features)


# ============================================================
# LOAD EVERYTHING
# ============================================================

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

    st.info(
        "Check that models/, config/, and data/ are present "
        "inside your GitHub repository."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎛️ Payment Simulator")

st.sidebar.caption(
    "Configure a transaction and run PayShield AI."
)

amount = st.sidebar.number_input(
    "Transaction Amount (₹)",
    min_value=100.0,
    max_value=1000000.0,
    value=5000.0,
    step=500.0
)

monthly_spend = st.sidebar.number_input(
    "Customer Monthly Spend (₹)",
    min_value=500.0,
    value=10000.0
)

merchant_risk = st.sidebar.slider(
    "Merchant Risk Score",
    0.0,
    1.0,
    0.25
)

ip_risk = st.sidebar.slider(
    "IP Risk Score",
    0.0,
    1.0,
    0.30
)

txn_1h = st.sidebar.number_input(
    "Transactions in 1 Hour",
    min_value=0,
    max_value=1000,
    value=2
)

txn_24h = st.sidebar.number_input(
    "Transactions in 24 Hours",
    min_value=0,
    max_value=5000,
    value=5
)

failed_24h = st.sidebar.number_input(
    "Failed Transactions (24h)",
    min_value=0,
    max_value=1000,
    value=1
)

international = st.sidebar.selectbox(
    "International Transaction",
    ["No", "Yes"]
)

payment_channel = st.sidebar.selectbox(
    "Payment Channel",
    ["UPI", "CARD", "WALLET", "NETBANKING"]
)

device_type = st.sidebar.selectbox(
    "Device Type",
    ["Mobile", "Desktop", "Tablet"]
)

geo_distance = st.sidebar.number_input(
    "Geo Distance From Last Txn",
    min_value=0.0,
    value=10.0
)

amount_deviation = st.sidebar.number_input(
    "Amount Deviation From User Mean",
    min_value=0.0,
    value=500.0
)

customer_avg_amount = st.sidebar.number_input(
    "Customer Average Amount",
    min_value=0.0,
    value=1200.0
)

customer_txn_before = st.sidebar.number_input(
    "Customer Transactions Before",
    min_value=0.0,
    value=10.0
)

customer_failed_rate = st.sidebar.slider(
    "Customer Failed Rate",
    0.0,
    1.0,
    0.10
)

merchant_txn_before = st.sidebar.number_input(
    "Merchant Transactions Before",
    min_value=0.0,
    value=100.0
)

merchant_avg_amount = st.sidebar.number_input(
    "Merchant Average Amount",
    min_value=0.0,
    value=2000.0
)

merchant_fraud_rate = st.sidebar.slider(
    "Merchant Fraud Rate",
    0.0,
    1.0,
    0.02
)

post_auth_risk = st.sidebar.slider(
    "Post-Auth Risk Score",
    0.0,
    1.0,
    0.20
)


analyze = st.sidebar.button(
    "🔍 ANALYZE PAYMENT",
    type="primary",
    use_container_width=True
)


# ============================================================
# RISK STATISTICS
# ============================================================

st.header("📊 Risk Statistics")

total_transactions = len(fraud_data)

if "is_fraud" in fraud_data.columns:
    fraud_count = int(
        fraud_data["is_fraud"].fillna(0).sum()
    )
else:
    fraud_count = 0

safe_count = max(
    total_transactions - fraud_count,
    0
)

if "recovery_success" in recovery_data.columns:
    recovered_count = int(
        recovery_data["recovery_success"]
        .fillna(0)
        .sum()
    )
else:
    recovered_count = 0


a, b, c, d = st.columns(4)

a.metric("📊 Transactions", f"{total_transactions:,}")
b.metric("🟢 Low Risk", f"{safe_count:,}")
c.metric("🔴 Fraud / High Risk", f"{fraud_count:,}")
d.metric("💰 Recovered", f"{recovered_count:,}")

st.divider()


# ============================================================
# SECURITY OPERATIONS CENTER
# ============================================================

st.header("🛡️ Security Operations Center")

active_tickets = sum(
    1
    for ticket in st.session_state.tickets
    if ticket.get("Status") == "🔴 UNDER REVIEW"
)

soc1, soc2, soc3, soc4 = st.columns(4)

soc1.metric("🟢 LOW", "ALLOW")
soc2.metric("🟠 MEDIUM", "2FA")
soc3.metric("🔴 HIGH", "HOLD")
soc4.metric("🎫 ACTIVE TICKETS", active_tickets)

st.markdown(
    """
    <div class="info-panel">

    <h3>🛡️ Security Decision Protocol</h3>

    <span class="badge badge-green">🟢 LOW → ALLOW</span>

    <span class="badge badge-orange">🟠 MEDIUM → 2FA</span>

    <span class="badge badge-red">🔴 HIGH → HOLD</span>

    <br><br>

    ❌ Failed Payment
    &nbsp;→&nbsp;
    💰 PayRecover AI
    &nbsp;→&nbsp;
    ⏰ Smart Retry AI

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TRANSACTION HISTORY
# ============================================================

st.header("📜 Transaction History")

history_columns = [
    "transaction_id",
    "transaction_time",
    "customer_id",
    "merchant_id",
    "transaction_amount",
    "payment_channel",
    "device_type",
    "is_fraud"
]

history_columns = [
    col for col in history_columns
    if col in fraud_data.columns
]

if history_columns:

    history_table = fraud_data[
        history_columns
    ].head(15).copy()

    if "is_fraud" in history_table.columns:

        history_table["Risk"] = (
            history_table["is_fraud"]
            .map({
                0: "🟢 LOW",
                1: "🔴 HIGH"
            })
        )

    st.dataframe(
        history_table,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Transaction history columns are not available."
    )


# ============================================================
# ANALYZE PAYMENT
# ============================================================

if analyze:

    now = datetime.now()

    hour = now.hour
    day = now.weekday()

    international_value = int(
        international == "Yes"
    )

    amount_to_monthly_spend = (
        amount / max(monthly_spend, 1)
    )

    failure_rate_24h = (
        failed_24h / max(txn_24h, 1)
    )

    velocity_ratio = (
        txn_1h / max(txn_24h, 1)
    )

    is_weekend = int(day >= 5)

    is_night = int(
        hour < 6 or hour >= 22
    )


    # ========================================================
    # FRAUD INPUT
    # ========================================================

    fraud_input = pd.DataFrame([{

        "account_age_days": 1000,
        "credit_score_band": 3,
        "kyc_level": 2,
        "avg_monthly_spend": monthly_spend,
        "merchant_risk_score": merchant_risk,
        "transaction_amount": amount,
        "payment_channel": payment_channel,
        "device_type": device_type,
        "is_international": international_value,
        "ip_risk_score": ip_risk,
        "txn_count_1h": txn_1h,
        "txn_count_24h": txn_24h,
        "failed_txn_count_24h": failed_24h,
        "geo_distance_from_last_txn": geo_distance,
        "amount_deviation_from_user_mean": amount_deviation,
        "post_auth_risk_score": post_auth_risk,
        "transaction_hour": hour,
        "day_of_week": day,
        "is_weekend": is_weekend,
        "is_night": is_night,
        "amount_to_monthly_spend": amount_to_monthly_spend,
        "failure_rate_24h": failure_rate_24h,
        "velocity_ratio": velocity_ratio,
        "customer_txn_count_before": customer_txn_before,
        "customer_avg_amount_before": customer_avg_amount,
        "customer_failed_rate_before": customer_failed_rate,
        "merchant_txn_count_before": merchant_txn_before,
        "merchant_avg_amount_before": merchant_avg_amount,
        "merchant_fraud_rate_before": merchant_fraud_rate

    }])


    try:

        fraud_input = fraud_input.reindex(
            columns=fraud_features
        )

    except Exception as e:

        st.error(
            "❌ Fraud feature configuration error."
        )

        st.code(str(e))
        st.stop()


    # ========================================================
    # FRAUD PREDICTION
    # ========================================================

    try:

        fraud_probability = float(
            fraud_model.predict_proba(
                fraud_input
            )[0, 1]
        )

    except Exception as e:

        st.error(
            "❌ Fraud model prediction failed."
        )

        st.code(str(e))
        st.stop()


    risk_score = fraud_probability * 100


    # ========================================================
    # DEMO 2FA MODE
    # ========================================================
    #
    # For the Razorpay Buildathon demo:
    # Every Analyze click goes to MEDIUM → 2FA.
    #
    # Remove these 3 lines if you want the real model
    # to decide LOW / MEDIUM / HIGH.
    # ========================================================

    risk_level = "MEDIUM"
    action = "2FA"
    icon = "🟠"


    # ========================================================
    # RESET SECURITY
    # ========================================================

    st.session_state.generated_otp = None
    st.session_state.otp_expiry = None
    st.session_state.otp_verified = False
    st.session_state.otp_attempts = 0
    st.session_state.ticket_details = None

    st.session_state.scheduled_retry = None
    st.session_state.method_changed = False
    st.session_state.pay_later_selected = False

    # OPEN 2FA POPUP
    st.session_state.show_2fa_popup = True


    # ========================================================
    # GENERATE OTP IMMEDIATELY
    # ========================================================

    otp = str(
        random.randint(
            100000,
            999999
        )
    )

    st.session_state.generated_otp = otp

    st.session_state.otp_expiry = (
        datetime.now() +
        timedelta(minutes=5)
    )


    # ========================================================
    # ANALYSIS ID
    # ========================================================

    analysis_id = (
        "TXN-"
        + now.strftime("%Y%m%d%H%M%S")
        + "-"
        + str(random.randint(100, 999))
    )


    result = {

        "analysis_id": analysis_id,

        "risk": risk_score,

        "level": risk_level,

        "action": action,

        "amount": amount,

        "merchant_risk": merchant_risk,

        "ip_risk": ip_risk,

        "failed_24h": failed_24h,

        "amount_to_monthly_spend":
            amount_to_monthly_spend,

        "failure_rate_24h":
            failure_rate_24h,

        "velocity_ratio":
            velocity_ratio,

        "time":
            now.strftime("%H:%M:%S"),

        "datetime":
            now.strftime("%Y-%m-%d %H:%M:%S")
    }


    st.session_state.last_result = result


    # ========================================================
    # FORCE RERUN TO SHOW POPUP
    # ========================================================

    st.rerun()


# ============================================================
# 2FA POPUP
# ============================================================

if st.session_state.show_2fa_popup:

    @st.dialog("🟠 Two-Factor Authentication")
    def two_factor_popup():

        st.warning(
            "🟠 MEDIUM-RISK PAYMENT — 2FA REQUIRED"
        )

        st.write(
            "PayShield AI detected a medium-risk transaction."
        )

        st.write(
            "Customer verification is required before "
            "the payment can be approved."
        )

        st.divider()

        st.markdown(
            f"""
<div class="otp-card">

<h3>📲 OTP GENERATED</h3>

<p>For this Buildathon demonstration, your OTP is:</p>

<h1>🔐 {st.session_state.generated_otp}</h1>

<p>OTP expires in 5 minutes.</p>

</div>
""",
            unsafe_allow_html=True
        )

        st.divider()

        otp_input = st.text_input(
            "Enter 6-digit OTP",
            max_chars=6,
            key="popup_otp_input"
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "🔐 VERIFY 2FA",
                type="primary",
                use_container_width=True
            ):

                if (
                    st.session_state.otp_expiry
                    and
                    datetime.now()
                    >
                    st.session_state.otp_expiry
                ):

                    st.error(
                        "⏰ OTP expired."
                    )

                elif (
                    otp_input ==
                    st.session_state.generated_otp
                ):

                    st.session_state.otp_verified = True
                    st.session_state.show_2fa_popup = False

                    st.success(
                        "✅ 2FA VERIFIED — PAYMENT APPROVED"
                    )

                    st.balloons()

                    st.rerun()

                else:

                    st.session_state.otp_attempts += 1

                    st.error(
                        "❌ INVALID OTP"
                    )

                    st.warning(
                        f"Attempts: "
                        f"{st.session_state.otp_attempts}"
                    )

        with c2:

            if st.button(
                "🔄 RESEND OTP",
                use_container_width=True
            ):

                new_otp = str(
                    random.randint(
                        100000,
                        999999
                    )
                )

                st.session_state.generated_otp = new_otp

                st.session_state.otp_expiry = (
                    datetime.now()
                    +
                    timedelta(minutes=5)
                )

                st.session_state.otp_attempts = 0

                st.rerun()


    two_factor_popup()


# ============================================================
# DISPLAY CURRENT RESULT
# ============================================================

result = st.session_state.last_result


if result:

    risk_score = float(
        result["risk"]
    )

    risk_level = result["level"]

    action = result["action"]

    amount = float(
        result["amount"]
    )

    merchant_risk = float(
        result["merchant_risk"]
    )

    ip_risk = float(
        result["ip_risk"]
    )

    failed_24h = int(
        result["failed_24h"]
    )

    amount_to_monthly_spend = float(
        result["amount_to_monthly_spend"]
    )

    icon = {
        "LOW": "🟢",
        "MEDIUM": "🟠",
        "HIGH": "🔴"
    }.get(
        risk_level,
        "⚪"
    )


    # ========================================================
    # LIVE FRAUD DETECTION
    # ========================================================

    st.divider()

    st.header("🔍 AI Fraud Detection")

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Risk Score",
        f"{risk_score:.2f}%"
    )

    m2.metric(
        "Risk Level",
        f"{icon} {risk_level}"
    )

    m3.metric(
        "Payment Action",
        action
    )

    st.progress(
        int(
            min(
                max(
                    risk_score,
                    0
                ),
                100
            )
        )
    )


    # ========================================================
    # RESULT CARD
    # ========================================================

    st.markdown(
        f"""
<div class="card orange-card">

<h2>🟠 MEDIUM-RISK PAYMENT</h2>

<p>Additional customer verification is required.</p>

<p><b>Transaction ID:</b>
{result["analysis_id"]}</p>

<p><b>Risk Score:</b>
{risk_score:.2f}%</p>

<p><b>Action:</b> 2FA VERIFICATION</p>

</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # EXPLAINABLE AI
    # ========================================================

    st.header("🧠 Explainable AI")

    reasons = []

    if merchant_risk >= 0.6:
        reasons.append(
            "⚠️ Merchant risk score is elevated."
        )
    else:
        reasons.append(
            "✅ Merchant risk is within normal range."
        )

    if amount_to_monthly_spend > 0.5:
        reasons.append(
            "⚠️ Transaction amount is high relative "
            "to monthly spending."
        )
    else:
        reasons.append(
            "✅ Transaction amount is consistent "
            "with customer spending."
        )

    if failed_24h > 3:
        reasons.append(
            "⚠️ Multiple failed transactions detected."
        )
    else:
        reasons.append(
            "✅ Recent transaction failure activity is low."
        )

    if ip_risk >= 0.6:
        reasons.append(
            "⚠️ IP risk score is elevated."
        )
    else:
        reasons.append(
            "✅ IP risk is within normal range."
        )

    for reason in reasons:
        st.write(reason)


    # ========================================================
    # AI RECOMMENDATION
    # ========================================================

    st.header("🤖 AI Recommendation")

    st.info(
        "🤖 PayShield recommends: "
        "Require 2FA verification before approving "
        "this payment because the fraud risk is medium."
    )


    # ========================================================
    # SECURITY CENTER
    # ========================================================

    st.header("🔐 Security Center")

    if st.session_state.otp_verified:

        st.success(
            "✅ 2FA VERIFIED — PAYMENT APPROVED"
        )

        st.success(
            "🟢 Customer identity successfully verified."
        )

        st.info(
            "Payment has been approved after successful "
            "2FA verification."
        )

    else:

        st.warning(
            "🟠 MEDIUM RISK — 2FA REQUIRED"
        )

        st.info(
            "Click ANALYZE PAYMENT again if you want to "
            "restart the 2FA verification."
        )


    # ========================================================
    # TRANSACTION SUMMARY
    # ========================================================

    st.header("📋 Transaction Summary")

    two_fa_status = (
        "✅ VERIFIED"
        if st.session_state.otp_verified
        else "🔐 REQUIRED"
    )

    summary = pd.DataFrame({

        "Field": [

            "Transaction ID",
            "Amount",
            "Risk Score",
            "Risk Level",
            "Fraud Action",
            "2FA",
            "Security Ticket",
            "Recovery",
            "Best Retry",
            "Retry Success"

        ],

        "Value": [

            result["analysis_id"],
            f"₹{amount:,.2f}",
            f"{risk_score:.2f}%",
            f"{icon} {risk_level}",
            action,
            two_fa_status,
            "NOT REQUIRED",
            "Available after payment failure",
            "Available after payment failure",
            "Available after payment failure"

        ]
    })

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # DECISION TIMELINE
    # ========================================================

    st.header(
        "🧠 Decision Engine — Live Decision Timeline"
    )

    timeline = [

        "✓ Payment received",
        "✓ Customer behaviour evaluated",
        "✓ Merchant risk evaluated",
        "✓ Device and IP risk evaluated",
        "✓ FraudShield AI executed",
        f"✓ Risk Score: {risk_score:.2f}%",
        "✓ Risk Level: 🟠 MEDIUM",
        "✓ Decision: 2FA"

    ]

    if st.session_state.otp_verified:

        timeline.append(
            "✅ 2FA verification successful"
        )

        timeline.append(
            "🟢 Payment approved"
        )

    else:

        timeline.append(
            "🔐 OTP verification required"
        )

    for item in timeline:

        st.markdown(
            f'<div class="timeline">{item}</div>',
            unsafe_allow_html=True
        )


# ============================================================
# SECURITY OPERATIONS — ALL TICKETS
# ============================================================

st.divider()

st.header("🎫 Live Security Tickets")

if st.session_state.tickets:

    ticket_df = pd.DataFrame(
        st.session_state.tickets
    )

    st.dataframe(
        ticket_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No active security tickets."
    )


# ============================================================
# PAYRECOVER AI
# ============================================================

st.divider()

st.header("💰 PayRecover AI")

failed_payment = st.checkbox(
    "❌ Simulate Failed Payment",
    key="failed_payment"
)


if failed_payment:

    st.error(
        "❌ PAYMENT FAILED"
    )


    f1, f2 = st.columns(2)


    with f1:

        failure_reason = st.selectbox(
            "Failure Reason",
            [
                "Bank Decline",
                "Insufficient Funds",
                "Timeout",
                "Technical Error",
                "Network Error"
            ],
            key="failure_reason"
        )

        payment_method = st.selectbox(
            "Payment Method",
            [
                "UPI",
                "CARD",
                "WALLET",
                "NETBANKING"
            ],
            key="payment_method"
        )

        retry_count = st.number_input(
            "Previous Retry Count",
            min_value=0,
            max_value=20,
            value=0,
            key="retry_count"
        )


    with f2:

        minutes_since_failure = st.number_input(
            "Minutes Since Failure",
            min_value=0,
            max_value=10000,
            value=5,
            key="minutes_since_failure"
        )

        customer_success_rate = st.slider(
            "Customer Success Rate",
            0.0,
            1.0,
            0.70,
            key="customer_success_rate"
        )

        method_success_rate = st.slider(
            "Method Success Rate",
            0.0,
            1.0,
            0.65,
            key="method_success_rate"
        )

        previous_failures = st.number_input(
            "Previous Failures",
            min_value=0,
            max_value=100,
            value=1,
            key="previous_failures"
        )


    # ========================================================
    # RECOVERY INPUT
    # ========================================================

    recovery_input = pd.DataFrame([{

        "amount": amount,

        "payment_method":
            payment_method,

        "failure_reason":
            failure_reason,

        "retry_count":
            retry_count,

        "minutes_since_failure":
            minutes_since_failure,

        "customer_success_rate":
            customer_success_rate,

        "method_success_rate":
            method_success_rate,

        "previous_failures":
            previous_failures,

        "is_international":
            int(international == "Yes"),

        "device_type":
            device_type,

        "hour":
            datetime.now().hour,

        "day_of_week":
            datetime.now().weekday()

    }])


    recovery_input = recovery_input.reindex(
        columns=recovery_features
    )


    try:

        recovery_probability = float(
            recovery_model.predict_proba(
                recovery_input
            )[0, 1]
        ) * 100

    except Exception as e:

        st.error(
            "❌ Recovery model prediction failed."
        )

        st.code(str(e))

        recovery_probability = 0.0


    st.session_state.recovery_result = (
        recovery_probability
    )


    # ========================================================
    # RECOVERY VISUALIZATION
    # ========================================================

    st.subheader(
        "💰 Recovery Probability"
    )

    rc1, rc2 = st.columns(2)

    rc1.metric(
        "Recovery Probability",
        f"{recovery_probability:.2f}%"
    )

    rc2.metric(
        "Payment Status",
        "FAILED"
    )

    st.progress(
        int(
            min(
                max(
                    recovery_probability,
                    0
                ),
                100
            )
        )
    )


    # ========================================================
    # SMART RETRY AI
    # ========================================================

    st.header(
        "⏰ Smart Retry AI"
    )

    retry_times = [
        5,
        15,
        30,
        60,
        120,
        240,
        480,
        1440
    ]

    probabilities = []


    for retry_time in retry_times:

        retry_input = pd.DataFrame([{

            "customer_success_rate":
                customer_success_rate,

            "method_success_rate":
                method_success_rate,

            "previous_failures":
                previous_failures,

            "retry_time_minutes":
                retry_time

        }])


        retry_input = retry_input.reindex(
            columns=retry_features
        )


        try:

            probability = float(
                retry_model.predict_proba(
                    retry_input
                )[0, 1]
            ) * 100

        except Exception:

            probability = 0.0


        probabilities.append(
            probability
        )


    retry_df = pd.DataFrame({

        "Retry Time": [
            f"{x} min"
            for x in retry_times
        ],

        "Success Probability (%)": [
            round(x, 2)
            for x in probabilities
        ]

    })


    st.dataframe(
        retry_df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # GRAPH
    # ========================================================

    st.subheader(
        "📈 Retry Probability Graph"
    )

    graph_df = pd.DataFrame({

        "Predicted Success (%)":
            probabilities

    })

    graph_df.index = [
        f"{x} min"
        for x in retry_times
    ]

    st.line_chart(
        graph_df
    )


    # ========================================================
    # BEST RETRY
    # ========================================================

    if probabilities:

        best_index = int(
            np.argmax(probabilities)
        )

        best_time = retry_times[
            best_index
        ]

        best_probability = probabilities[
            best_index
        ]

    else:

        best_time = 30
        best_probability = 0.0


    st.session_state.retry_result = {

        "best_time":
            best_time,

        "best_probability":
            best_probability,

        "probabilities":
            probabilities
    }


    st.success(
        f"⭐ PayRecover AI recommends retrying "
        f"after {best_time} minutes with "
        f"{best_probability:.2f}% predicted success."
    )


    # ========================================================
    # RECOVERY SUMMARY
    # ========================================================

    st.subheader(
        "📋 Recovery Summary"
    )

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Recovery Probability",
        f"{recovery_probability:.2f}%"
    )

    r2.metric(
        "Recommended Retry",
        f"{best_time} min"
    )

    r3.metric(
        "Retry Success",
        f"{best_probability:.2f}%"
    )


    # ========================================================
    # RECOVERY ACTIONS
    # ========================================================

    st.subheader("⚡ Recovery Actions")

    x1, x2, x3 = st.columns(3)


    # --------------------------------------------------------
    # SCHEDULE RETRY
    # --------------------------------------------------------

    with x1:

        if st.button(
            "🔄 SCHEDULE RETRY",
            key="schedule_retry_btn",
            use_container_width=True
        ):

            scheduled_time = (
                datetime.now()
                +
                timedelta(
                    minutes=best_time
                )
            )

            st.session_state.scheduled_retry = (
                scheduled_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            st.success(
                f"✅ Retry scheduled after "
                f"{best_time} minutes."
            )


    # --------------------------------------------------------
    # CHANGE METHOD
    # --------------------------------------------------------

    with x2:

        if st.button(
            "💳 CHANGE METHOD",
            key="change_method_btn",
            use_container_width=True
        ):

            st.session_state.method_changed = True

            st.success(
                "💳 Alternative payment method selected."
            )


    # --------------------------------------------------------
    # PAY LATER
    # --------------------------------------------------------

    with x3:

        if st.button(
            "🕐 PAY LATER",
            key="pay_later_btn",
            use_container_width=True
        ):

            st.session_state.pay_later_selected = True

            st.success(
                "🕐 Pay Later option selected."
            )


    # ========================================================
    # DISPLAY SELECTED ACTIONS
    # ========================================================

    if st.session_state.scheduled_retry:

        st.info(
            "⏰ Scheduled retry: "
            +
            st.session_state.scheduled_retry
        )


    if st.session_state.method_changed:

        st.success(
            "💳 Alternative payment method selected."
        )


    if st.session_state.pay_later_selected:

        st.success(
            "🕐 Pay Later option selected."
        )


# ============================================================
# PAYMENTOPS AI
# ============================================================
# ============================================================
# PAYMENTOPS AI
# ============================================================

st.divider()

st.header("🤖 PaymentOps AI")

st.caption(
    "Intelligent orchestration layer for the complete payment lifecycle"
)

# ============================================================
# PAYMENTOPS DESCRIPTION
# ============================================================

st.markdown(
    """
    <div class="card blue-card">

        <h2>🤖 Intelligent Payment Operations</h2>

        <p>
        <b>PaymentOps AI</b> is the central orchestration layer
        of PayShield AI. It connects fraud detection, customer
        authentication, security operations, payment recovery,
        and intelligent retry into one unified payment workflow.
        </p>

        <p>
        PaymentOps continuously monitors the payment journey and
        determines what action should happen next based on the
        output of the AI systems.
        </p>

        <h3>🔄 How PaymentOps Works</h3>

        <p>
        🛡️ <b>1. FraudShield AI</b><br>
        Analyzes transaction behaviour, merchant risk, device
        signals, IP risk and transaction velocity to calculate
        the transaction risk score.
        </p>

        <p>
        🔐 <b>2. Security Decision</b><br>
        Based on the risk level, PaymentOps determines whether
        the transaction should be allowed, sent for 2FA
        verification, or placed on hold.
        </p>

        <p>
        🎫 <b>3. Security Operations</b><br>
        High-risk transactions can be placed under review and
        a security ticket can be raised for investigation.
        </p>

        <p>
        💰 <b>4. PayRecover AI</b><br>
        If a payment fails, PayRecover AI analyzes the failure,
        customer behaviour and payment method to estimate the
        probability of successful recovery.
        </p>

        <p>
        ⏰ <b>5. Smart Retry AI</b><br>
        Smart Retry evaluates different retry intervals and
        recommends the time with the highest predicted payment
        success probability.
        </p>

        <h3>🎯 PaymentOps Objective</h3>

        <p>
        PaymentOps aims to balance <b>security and payment
        success</b> — preventing fraudulent transactions while
        reducing unnecessary declines and maximizing recovery
        of failed payments.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LIVE SYSTEM STATUS
# ============================================================

st.subheader("📡 PaymentOps System Status")

op1, op2, op3, op4 = st.columns(4)

with op1:
    st.metric(
        "🛡️ FraudShield",
        "ACTIVE"
    )

with op2:
    st.metric(
        "💰 PayRecover",
        "ACTIVE"
    )

with op3:
    st.metric(
        "⏰ Smart Retry",
        "ACTIVE"
    )

with op4:
    st.metric(
        "🤖 PaymentOps",
        "ACTIVE"
    )


# ============================================================
# LIVE PAYMENTOPS STATUS
# ============================================================

if st.session_state.last_result:

    ops_result = st.session_state.last_result

    ops_risk = float(
        ops_result["risk"]
    )

    ops_level = ops_result["level"]

    ops_action = ops_result["action"]

    if ops_level == "LOW":

        ops_icon = "🟢"
        ops_status = "PAYMENT ALLOWED"
        ops_message = (
            "Transaction risk is low. PaymentOps has "
            "authorized the payment."
        )

    elif ops_level == "MEDIUM":

        ops_icon = "🟠"
        ops_status = "2FA VERIFICATION"
        ops_message = (
            "Additional customer verification is required "
            "before payment approval."
        )

    else:

        ops_icon = "🔴"
        ops_status = "PAYMENT ON HOLD"
        ops_message = (
            "Transaction requires security review."
        )


    st.subheader("⚡ Live PaymentOps Decision")

    st.markdown(
        f"""
        <div class="card">

            <h2>
            {ops_icon} {ops_level}
            </h2>

            <p>
            <b>Transaction ID:</b>
            {ops_result["analysis_id"]}
            </p>

            <p>
            <b>Risk Score:</b>
            {ops_risk:.2f}%
            </p>

            <p>
            <b>Current Action:</b>
            {ops_action}
            </p>

            <p>
            <b>PaymentOps Status:</b>
            {ops_status}
            </p>

            <p>
            {ops_message}
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.info(
        "💡 Analyze a payment to activate the live "
        "PaymentOps decision monitor."
    )


# ============================================================
# PAYMENTOPS DECISION FLOW
# ============================================================

st.subheader("🔄 PaymentOps Decision Flow")

st.markdown(
    """
    <div class="card blue-card">

        <h3>END-TO-END PAYMENT ORCHESTRATION</h3>

        <div class="timeline">
        🟦 <b>PAYMENT RECEIVED</b>
        </div>

        <div class="timeline">
        🛡️ <b>FRAUDSHIELD AI</b><br>
        Transaction risk analysis
        </div>

        <div class="timeline">
        🚦 <b>RISK ASSESSMENT</b><br>
        Fraud probability + behavioural signals
        </div>

        <div class="timeline">
        🟢 <b>LOW RISK → ALLOW PAYMENT</b>
        </div>

        <div class="timeline">
        🟠 <b>MEDIUM RISK → 2FA VERIFICATION</b>
        </div>

        <div class="timeline">
        🔴 <b>HIGH RISK → HOLD + SECURITY TICKET</b>
        </div>

        <div class="timeline">
        ❌ <b>PAYMENT FAILURE</b>
        </div>

        <div class="timeline">
        💰 <b>PAYRECOVER AI</b><br>
        Recovery probability analysis
        </div>

        <div class="timeline">
        📈 <b>RECOVERY PROBABILITY</b>
        </div>

        <div class="timeline">
        ⏰ <b>SMART RETRY AI</b><br>
        Retry timing optimization
        </div>

        <div class="timeline">
        ⭐ <b>RECOMMENDED RETRY TIME</b>
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LIVE RECOVERY INTEGRATION
# ============================================================

if st.session_state.recovery_result is not None:

    st.subheader("💰 PaymentOps Recovery Intelligence")

    recovery_probability = float(
        st.session_state.recovery_result
    )

    rec1, rec2, rec3 = st.columns(3)

    rec1.metric(
        "Recovery Probability",
        f"{recovery_probability:.2f}%"
    )

    if st.session_state.retry_result:

        best_time = st.session_state.retry_result[
            "best_time"
        ]

        best_probability = st.session_state.retry_result[
            "best_probability"
        ]

        rec2.metric(
            "Recommended Retry",
            f"{best_time} min"
        )

        rec3.metric(
            "Retry Success",
            f"{best_probability:.2f}%"
        )

        st.success(
            f"⭐ PaymentOps recommendation: Retry after "
            f"{best_time} minutes with an estimated "
            f"{best_probability:.2f}% success probability."
        )

    else:

        rec2.metric(
            "Recommended Retry",
            "Calculating"
        )

        rec3.metric(
            "Retry Success",
            "Calculating"
        )


# ============================================================
# PAYMENTOPS SUMMARY
# ============================================================

st.subheader("📋 PaymentOps Summary")

summary_data = {
    "Component": [
        "FraudShield AI",
        "Security System",
        "Payment Recovery",
        "Smart Retry",
        "PaymentOps"
    ],

    "Function": [
        "Fraud & risk detection",
        "2FA / Hold / Security Ticket",
        "Failed payment recovery",
        "Retry optimization",
        "Central orchestration"
    ],

    "Status": [
        "🟢 ACTIVE",
        "🟢 ACTIVE",
        "🟢 ACTIVE",
        "🟢 ACTIVE",
        "🟢 ACTIVE"
    ]
}

paymentops_summary = pd.DataFrame(
    summary_data
)

st.dataframe(
    paymentops_summary,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# FINAL DECISION ENGINE
# ============================================================

st.divider()

st.header(
    "🧠 PayShield Decision Engine"
)

st.markdown(
    """
<div class="card">

<h3>LIVE PAYMENT DECISION PIPELINE</h3>

🟦 PAYMENT RECEIVED

↓

🛡️ FRAUDSHIELD AI

↓

📊 RISK SCORE

↓

🟢 LOW → <b>ALLOW</b>

🟠 MEDIUM → <b>2FA</b>

🔴 HIGH → <b>HOLD + SECURITY TICKET</b>

↓

❌ IF PAYMENT FAILS

↓

💰 PAYRECOVER AI

↓

📈 RECOVERY PROBABILITY

↓

⏰ SMART RETRY AI

↓

⭐ OPTIMAL RETRY TIME

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🛡️ PayShield AI • FraudShield + PayRecover AI + "
    "Smart Retry + PaymentOps"
)

st.caption(
    "AI-powered payment protection and recovery platform"
)
