
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

FRAUD_MODEL = os.path.join(
    BASE_DIR, "models", "fraud_model.pkl"
)

RECOVERY_MODEL = os.path.join(
    BASE_DIR, "models", "recovery_model.pkl"
)

RETRY_MODEL = os.path.join(
    BASE_DIR, "models", "retry_model.pkl"
)

FRAUD_FEATURES = os.path.join(
    BASE_DIR, "config", "fraud_features.json"
)

RECOVERY_FEATURES = os.path.join(
    BASE_DIR, "config", "recovery_features.json"
)

RETRY_FEATURES = os.path.join(
    BASE_DIR, "config", "retry_features.json"
)

FRAUD_DATA = os.path.join(
    BASE_DIR, "data", "fraud_test.csv"
)

RECOVERY_DATA = os.path.join(
    BASE_DIR, "data", "recovery_full.csv"
)


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
    "change_method": False,
    "pay_later": False,
}


for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.title {
    font-size: 45px;
    font-weight: 800;
}

.subtitle {
    font-size: 17px;
    color: #9ca3af;
}

.card {
    padding: 20px;
    border-radius: 16px;
    margin: 10px 0;
    border: 1px solid rgba(255,255,255,.12);
}

.green-card {
    background: rgba(20,130,65,.20);
    border: 1px solid #21c354;
}

.orange-card {
    background: rgba(190,120,0,.20);
    border: 1px solid #ffa500;
}

.red-card {
    background: rgba(190,20,20,.20);
    border: 1px solid #ff4b4b;
}

.blue-card {
    background: rgba(40,100,180,.18);
    border: 1px solid #4f8cff;
}

.ticket-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #ff4b4b;
    background: rgba(190,20,20,.12);
    margin-top: 15px;
}

.otp-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #ffa500;
    background: rgba(190,120,0,.12);
    margin-top: 15px;
}

.success-ticket {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #21c354;
    background: rgba(20,130,65,.15);
    margin-top: 15px;
}

.timeline {
    padding: 13px;
    margin: 7px 0;
    border-left: 4px solid #4f8cff;
    border-radius: 6px;
    background: rgba(60,65,80,.5);
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">🛡️ PayShield AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Payment Protection • FraudShield • '
    'PayRecover AI • Smart Retry • PaymentOps'
    '</div>',
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


a.metric(
    "📊 Transactions",
    f"{total_transactions:,}"
)


b.metric(
    "🟢 Low Risk",
    f"{safe_count:,}"
)


c.metric(
    "🔴 Fraud / High Risk",
    f"{fraud_count:,}"
)


d.metric(
    "💰 Recovered",
    f"{recovered_count:,}"
)


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


soc1.metric(
    "🟢 LOW",
    "ALLOW"
)


soc2.metric(
    "🟠 MEDIUM",
    "2FA"
)


soc3.metric(
    "🔴 HIGH",
    "HOLD"
)


soc4.metric(
    "🎫 ACTIVE TICKETS",
    active_tickets
)


st.info(
    """
🟢 LOW RISK → ALLOW

🟠 MEDIUM RISK → 2FA VERIFICATION

🔴 HIGH RISK → HOLD + SECURITY TICKET

❌ FAILED PAYMENT → PAYRECOVER AI → SMART RETRY AI
"""
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
    col
    for col in history_columns
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

    st.info("Transaction history columns are not available.")


# ============================================================
# ANALYZE PAYMENT
# ============================================================

if analyze:

    # --------------------------------------------------------
    # CURRENT TIME
    # --------------------------------------------------------

    now = datetime.now()

    hour = now.hour

    day = now.weekday()


    # --------------------------------------------------------
    # DERIVED FEATURES
    # --------------------------------------------------------

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


    is_weekend = int(
        day >= 5
    )


    is_night = int(
        hour < 6 or hour >= 22
    )


    # --------------------------------------------------------
    # FRAUD INPUT
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # ALIGN FEATURES
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # FRAUD PREDICTION
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    if risk_score >= 70:

        risk_level = "HIGH"

        action = "HOLD"

        icon = "🔴"

    elif risk_score >= 40:

        risk_level = "MEDIUM"

        action = "2FA"

        icon = "🟠"

    else:

        risk_level = "LOW"

        action = "ALLOW"

        icon = "🟢"


    # --------------------------------------------------------
    # RESET SECURITY FOR NEW ANALYSIS
    # --------------------------------------------------------

    st.session_state.generated_otp = None

    st.session_state.otp_expiry = None

    st.session_state.otp_verified = False

    st.session_state.otp_attempts = 0

    st.session_state.ticket_details = None

    st.session_state.scheduled_retry = None

    st.session_state.change_method = False

    st.session_state.pay_later = False


    # --------------------------------------------------------
    # SAVE COMPLETE RESULT
    # --------------------------------------------------------

    analysis_id = (
        "TXN-" +
        now.strftime("%Y%m%d%H%M%S") +
        "-" +
        str(random.randint(100, 999))
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

    if risk_level == "HIGH":

        st.markdown(
            f"""
<div class="card red-card">

<h2>🔴 HIGH-RISK PAYMENT</h2>

<p>Payment has been placed on HOLD.</p>

<p><b>Transaction ID:</b> {result["analysis_id"]}</p>

<p><b>Risk Score:</b> {risk_score:.2f}%</p>

<p><b>Action:</b> HOLD + SECURITY REVIEW</p>

</div>
""",
            unsafe_allow_html=True
        )


    elif risk_level == "MEDIUM":

        st.markdown(
            f"""
<div class="card orange-card">

<h2>🟠 MEDIUM-RISK PAYMENT</h2>

<p>Additional customer verification required.</p>

<p><b>Transaction ID:</b> {result["analysis_id"]}</p>

<p><b>Risk Score:</b> {risk_score:.2f}%</p>

<p><b>Action:</b> 2FA</p>

</div>
""",
            unsafe_allow_html=True
        )


    else:

        st.markdown(
            f"""
<div class="card green-card">

<h2>🟢 LOW-RISK PAYMENT</h2>

<p>Transaction appears safe.</p>

<p><b>Transaction ID:</b> {result["analysis_id"]}</p>

<p><b>Risk Score:</b> {risk_score:.2f}%</p>

<p><b>Action:</b> ALLOW</p>

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


    if risk_level == "HIGH":

        recommendation = (
            "Hold this payment and create a security "
            "ticket because the fraud risk is high."
        )

    elif risk_level == "MEDIUM":

        recommendation = (
            "Require 2FA verification before approving "
            "this payment because the fraud risk is medium."
        )

    else:

        recommendation = (
            "Allow this payment because the detected "
            "fraud risk is low."
        )


    st.info(
        "🤖 PayShield recommends: " +
        recommendation
    )


    # ========================================================
    # SECURITY CENTER
    # ========================================================

    st.header("🔐 Security Center")


    # ========================================================
    # MEDIUM RISK — 2FA
    # ========================================================

    if risk_level == "MEDIUM":

        st.warning(
            "🟠 MEDIUM RISK — 2FA REQUIRED"
        )

        st.subheader(
            "🟠 Two-Factor Authentication"
        )

        st.write(
            "Customer verification is required "
            "before payment approval."
        )


        # ----------------------------------------------------
        # SEND OTP
        # ----------------------------------------------------

        if st.session_state.generated_otp is None:

            if st.button(
                "📲 SEND OTP",
                key="send_otp",
                type="primary",
                use_container_width=True
            ):

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

                st.session_state.otp_verified = False

                st.session_state.otp_attempts = 0

                st.rerun()


        # ----------------------------------------------------
        # OTP DISPLAY
        # ----------------------------------------------------

        if st.session_state.generated_otp:

            expiry = st.session_state.otp_expiry


            st.markdown(
                f"""
<div class="otp-card">

<h3>📲 OTP SENT SUCCESSFULLY</h3>

<p>
For this Buildathon demonstration,
the OTP is displayed on screen.
</p>

<h1>🔐 {st.session_state.generated_otp}</h1>

<p><b>OTP expires in 5 minutes.</b></p>

</div>
""",
                unsafe_allow_html=True
            )


            # ------------------------------------------------
            # VERIFIED
            # ------------------------------------------------

            if st.session_state.otp_verified:

                st.success(
                    "✅ 2FA VERIFIED — PAYMENT APPROVED"
                )

                st.success(
                    "🟢 Customer identity successfully verified."
                )

                st.info(
                    "Payment has been approved after successful 2FA verification."
                )


            # ------------------------------------------------
            # VERIFY
            # ------------------------------------------------

            else:

                otp_input = st.text_input(
                    "Enter the 6-digit OTP",
                    max_chars=6,
                    key="otp_input"
                )


                if st.button(
                    "🔐 VERIFY 2FA",
                    key="verify_2fa",
                    type="primary",
                    use_container_width=True
                ):

                    # Check expiry

                    if (
                        st.session_state.otp_expiry
                        and
                        datetime.now()
                        >
                        st.session_state.otp_expiry
                    ):

                        st.error(
                            "⏰ OTP expired. Please send a new OTP."
                        )

                        st.session_state.generated_otp = None

                    elif otp_input == st.session_state.generated_otp:

                        st.session_state.otp_verified = True

                        st.success(
                            "✅ 2FA VERIFIED — PAYMENT APPROVED"
                        )

                        st.balloons()

                        st.rerun()

                    else:

                        st.session_state.otp_attempts += 1

                        st.error(
                            "❌ INVALID OTP — PAYMENT BLOCKED"
                        )

                        st.warning(
                            f"Attempts: "
                            f"{st.session_state.otp_attempts}"
                        )


                # --------------------------------------------
                # RESEND OTP
                # --------------------------------------------

                if st.button(
                    "🔄 RESEND OTP",
                    key="resend_otp",
                    use_container_width=True
                ):

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

                    st.session_state.otp_verified = False

                    st.session_state.otp_attempts = 0

                    st.rerun()


    # ========================================================
    # HIGH RISK — SECURITY TICKET
    # ========================================================

    elif risk_level == "HIGH":

        st.error(
            "🔴 HIGH RISK — PAYMENT UNDER REVIEW"
        )

        st.subheader(
            "🎫 Security Ticket"
        )

        st.write(
            "This payment is on HOLD. "
            "Create a security ticket for the security team."
        )


        # ----------------------------------------------------
        # RAISE TICKET
        # ----------------------------------------------------

        if st.session_state.ticket_details is None:

            if st.button(
                "🎫 RAISE SECURITY TICKET",
                key="raise_live_ticket",
                type="primary",
                use_container_width=True
            ):

                ticket_id = (
                    "PS-" +
                    datetime.now().strftime(
                        "%Y%m%d%H%M%S"
                    ) +
                    "-" +
                    str(
                        random.randint(
                            100,
                            999
                        )
                    )
                )


                created_time = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )


                new_ticket = {

                    "Ticket ID":
                        ticket_id,

                    "Transaction ID":
                        result["analysis_id"],

                    "Created":
                        created_time,

                    "Amount":
                        f"₹{amount:,.2f}",

                    "Risk Score":
                        f"{risk_score:.2f}%",

                    "Risk Level":
                        "🔴 HIGH",

                    "Action":
                        "HOLD",

                    "Status":
                        "🔴 UNDER REVIEW"

                }


                st.session_state.tickets.append(
                    new_ticket
                )


                st.session_state.ticket_details = (
                    new_ticket
                )


                st.rerun()


        # ----------------------------------------------------
        # TICKET DETAILS
        # ----------------------------------------------------

        if st.session_state.ticket_details:

            ticket = (
                st.session_state.ticket_details
            )


            st.markdown(
                f"""
<div class="success-ticket">

<h2>✅ TICKET RAISED SUCCESSFULLY</h2>

<p><b>🎫 Ticket ID:</b> {ticket["Ticket ID"]}</p>

<p><b>🧾 Transaction ID:</b> {ticket["Transaction ID"]}</p>

<p><b>📅 Created:</b> {ticket["Created"]}</p>

<p><b>💰 Amount:</b> {ticket["Amount"]}</p>

<p><b>📊 Risk Score:</b> {ticket["Risk Score"]}</p>

<p><b>🚨 Risk Level:</b> {ticket["Risk Level"]}</p>

<p><b>🛡️ Action:</b> {ticket["Action"]}</p>

<p><b>📌 Status:</b> {ticket["Status"]}</p>

</div>
""",
                unsafe_allow_html=True
            )


            st.success(
                "🎫 Security team has received the payment review ticket."
            )


    # ========================================================
    # LOW RISK
    # ========================================================

    else:

        st.success(
            "🟢 SECURITY CHECK PASSED"
        )

        st.write(
            "No additional customer verification is required."
        )


    # ========================================================
    # TRANSACTION SUMMARY
    # ========================================================

    st.header("📋 Transaction Summary")


    if risk_level == "MEDIUM":

        two_fa_status = (
            "✅ VERIFIED"
            if st.session_state.otp_verified
            else "🔐 REQUIRED"
        )

    else:

        two_fa_status = "NO"


    if risk_level == "HIGH":

        ticket_status = (
            "🎫 RAISED"
            if st.session_state.ticket_details
            else "NOT RAISED"
        )

    else:

        ticket_status = "NOT REQUIRED"


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

            ticket_status,

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

        f"✓ Risk Level: {icon} {risk_level}",

        f"✓ Decision: {action}"

    ]


    if risk_level == "HIGH":

        timeline.extend([

            "🔴 Payment placed on HOLD",

            (
                "🎫 Security ticket raised"
                if st.session_state.ticket_details
                else "🎫 Security ticket required"
            ),

            "🛡️ Security Operations review initiated"

        ])


    elif risk_level == "MEDIUM":

        timeline.extend([

            "🟠 Additional verification required",

            (
                "✅ 2FA verification successful"
                if st.session_state.otp_verified
                else "🔐 OTP verification required"
            )

        ])


    else:

        timeline.extend([

            "🟢 Security check passed",

            "✓ Payment approved"

        ])


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


    st.subheader(
        "🔧 Ticket Management"
    )


    for index, ticket in enumerate(
        st.session_state.tickets
    ):

        t1, t2, t3 = st.columns(
            [2, 4, 2]
        )


        t1.write(
            f"🎫 **{ticket['Ticket ID']}**"
        )


        t2.write(
            f"{ticket['Status']} | "
            f"{ticket['Amount']} | "
            f"{ticket['Risk Score']}"
        )


        if ticket["Status"] == "🔴 UNDER REVIEW":

            if t3.button(
                "✅ RESOLVE",
                key=f"resolve_ticket_{index}",
                use_container_width=True
            ):

                ticket["Status"] = "🟢 RESOLVED"

                st.session_state.tickets[
                    index
                ] = ticket


                if (
                    st.session_state.ticket_details
                    and
                    st.session_state.ticket_details[
                        "Ticket ID"
                    ]
                    ==
                    ticket["Ticket ID"]
                ):

                    st.session_state.ticket_details = (
                        ticket
                    )


                st.rerun()

        else:

            t3.success(
                "RESOLVED"
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

    x1, x2, x3 = st.columns(3)


    if x1.button(
        "🔄 SCHEDULE RETRY",
        key="schedule_retry",
        use_container_width=True
    ):

        scheduled_time = (
            datetime.now()
            +
            timedelta(minutes=best_time)
        )


        st.session_state.scheduled_retry = (
            scheduled_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )


        st.success(
            f"Retry scheduled after "
            f"{best_time} minutes."
        )


    if x2.button(
        "💳 CHANGE METHOD",
        key="change_method",
        use_container_width=True
    ):

        st.session_state.change_method = True


        st.info(
            "Payment method change selected."
        )


    if x3.button(
        "🕐 PAY LATER",
        key="pay_later",
        use_container_width=True
    ):

        st.session_state.pay_later = True


        st.info(
            "Pay Later option selected."
        )


    if st.session_state.scheduled_retry:

        st.info(
            "⏰ Scheduled retry: "
            +
            st.session_state.scheduled_retry
        )


    if st.session_state.change_method:

        st.success(
            "💳 Alternative payment method selected."
        )


    if st.session_state.pay_later:

        st.success(
            "🕐 Pay Later option selected."
        )


# ============================================================
# PAYMENTOPS AI
# ============================================================

st.divider()

st.header("🤖 PaymentOps AI")


op1, op2, op3, op4 = st.columns(4)


op1.metric(
    "🛡️ FraudShield",
    "ACTIVE"
)


op2.metric(
    "💰 PayRecover",
    "ACTIVE"
)


op3.metric(
    "⏰ Smart Retry",
    "ACTIVE"
)


op4.metric(
    "🛡️ PaymentOps",
    "ACTIVE"
)


st.markdown(
    """
<div class="card blue-card">

<h3>🤖 PaymentOps Decision Flow</h3>

Payment received

↓

🛡️ <b>FraudShield AI</b>

↓

🚦 <b>Risk Assessment</b>

↓

🟢 LOW → ALLOW

🟠 MEDIUM → 2FA

🔴 HIGH → HOLD + SECURITY TICKET

↓

❌ Failed Payment

↓

💰 <b>PayRecover AI</b>

↓

⏰ <b>Smart Retry AI</b>

↓

⭐ Recommended Retry Time

</div>
""",
    unsafe_allow_html=True
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
