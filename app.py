import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import random
from datetime import datetime

# ================================================================
# PAGE CONFIG
# ================================================================

st.set_page_config(
    page_title="PayShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# PATHS
# ================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRAUD_MODEL = os.path.join(BASE_DIR, "models", "fraud_model.pkl")
RECOVERY_MODEL = os.path.join(BASE_DIR, "models", "recovery_model.pkl")
RETRY_MODEL = os.path.join(BASE_DIR, "models", "retry_model.pkl")

FRAUD_FEATURES = os.path.join(BASE_DIR, "config", "fraud_features.json")
RECOVERY_FEATURES = os.path.join(BASE_DIR, "config", "recovery_features.json")
RETRY_FEATURES = os.path.join(BASE_DIR, "config", "retry_features.json")

FRAUD_DATA = os.path.join(BASE_DIR, "data", "fraud_test.csv")
RECOVERY_DATA = os.path.join(BASE_DIR, "data", "recovery_full.csv")

# ================================================================
# LOAD MODELS
# ================================================================

@st.cache_resource
def load_models():
    fraud = joblib.load(FRAUD_MODEL)
    recovery = joblib.load(RECOVERY_MODEL)
    retry = joblib.load(RETRY_MODEL)
    return fraud, recovery, retry


@st.cache_data
def load_features():

    with open(FRAUD_FEATURES) as f:
        fraud = json.load(f)

    with open(RECOVERY_FEATURES) as f:
        recovery = json.load(f)

    with open(RETRY_FEATURES) as f:
        retry = json.load(f)

    return fraud, recovery, retry


@st.cache_data
def load_data():

    fraud = pd.read_csv(FRAUD_DATA)
    recovery = pd.read_csv(RECOVERY_DATA)

    return fraud, recovery


# ================================================================
# INITIALIZE MODELS
# ================================================================

try:

    fraud_model, recovery_model, retry_model = load_models()

    fraud_features, recovery_features, retry_features = load_features()

    fraud_data, recovery_data = load_data()

except Exception as e:

    st.error("❌ PayShield could not load the required files.")

    st.code(str(e))

    st.info(
        "Check models/, config/, and data/ in your GitHub repository."
    )

    st.stop()


# ================================================================
# SESSION STATE
# ================================================================

defaults = {

    "tickets": [],

    "history": [],

    "last_result": None,

    "current_transaction": None,

    "generated_otp": None,

    "otp_verified": False,

    "otp_input": "",

    "ticket_details": None,

    "ticket_raised": False,

    "failed_payment": False

}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ================================================================
# CALLBACKS
# ================================================================

def send_otp():

    st.session_state.generated_otp = str(
        random.randint(100000, 999999)
    )

    st.session_state.otp_verified = False
    st.session_state.otp_input = ""


def verify_otp():

    entered = str(
        st.session_state.get("otp_input", "")
    ).strip()

    generated = st.session_state.get(
        "generated_otp"
    )

    if generated and entered == generated:

        st.session_state.otp_verified = True

    else:

        st.session_state.otp_verified = False


def raise_ticket():

    transaction = st.session_state.current_transaction

    if transaction is None:
        return

    ticket_id = (
        "PS-"
        + datetime.now().strftime("%Y%m%d%H%M%S")
        + "-"
        + str(np.random.randint(100, 999))
    )

    ticket = {

        "Ticket ID": ticket_id,

        "Created": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "Amount": f"₹{transaction['amount']:,.2f}",

        "Risk Score": f"{transaction['risk_score']:.2f}%",

        "Risk Level": "🔴 HIGH",

        "Action": "HOLD",

        "Status": "🔴 UNDER REVIEW"

    }

    st.session_state.tickets.append(ticket)

    st.session_state.ticket_details = ticket

    st.session_state.ticket_raised = True


def resolve_ticket(index):

    st.session_state.tickets[index]["Status"] = "🟢 RESOLVED"


# ================================================================
# CSS
# ================================================================

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
    margin: 8px 0;
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
    padding: 22px;
    border-radius: 15px;
    border: 1px solid #ff4b4b;
    background: rgba(190,20,20,.12);
    margin-top: 15px;
}

.success-ticket {
    padding: 22px;
    border-radius: 15px;
    border: 2px solid #21c354;
    background: rgba(20,130,65,.15);
    margin-top: 15px;
}

.otp-card {
    padding: 22px;
    border-radius: 15px;
    border: 2px solid #ffa500;
    background: rgba(190,120,0,.12);
    margin-top: 15px;
}

.verified-card {
    padding: 22px;
    border-radius: 15px;
    border: 2px solid #21c354;
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


# ================================================================
# HEADER
# ================================================================

st.markdown(
    '<div class="title">🛡️ PayShield AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Payment Protection • FraudShield • '
    'PayRecover AI • PaymentOps'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ================================================================
# SIDEBAR
# ================================================================

st.sidebar.title("🎛️ Payment Simulator")

st.sidebar.caption(
    "Configure a transaction and run the AI decision engine."
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


# ================================================================
# RISK STATISTICS
# ================================================================

st.header("📊 Risk Statistics")

total_transactions = len(fraud_data)

if "is_fraud" in fraud_data.columns:

    fraud_count = int(
        fraud_data["is_fraud"].sum()
    )

else:

    fraud_count = 0

safe_count = total_transactions - fraud_count

if "recovery_success" in recovery_data.columns:

    recovered_count = int(
        recovery_data["recovery_success"].sum()
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


# ================================================================
# SECURITY OPERATIONS CENTER
# ================================================================

st.header("🛡️ Security Operations Center")

active_tickets = len(
    [
        x for x in st.session_state.tickets
        if x["Status"] == "🔴 UNDER REVIEW"
    ]
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


# ================================================================
# TRANSACTION HISTORY
# ================================================================

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
    x for x in history_columns
    if x in fraud_data.columns
]

history_table = fraud_data[
    history_columns
].head(15).copy()

if "is_fraud" in history_table.columns:

    history_table["Risk"] = (
        history_table["is_fraud"].map({
            0: "🟢 LOW",
            1: "🔴 HIGH"
        })
    )

st.dataframe(
    history_table,
    use_container_width=True,
    hide_index=True
)


# ================================================================
# ANALYZE PAYMENT
# ================================================================

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

    fraud_input = fraud_input[
        fraud_features
    ]

    fraud_probability = (
        fraud_model.predict_proba(
            fraud_input
        )[0, 1]
    )

    risk_score = fraud_probability * 100

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

    # New transaction = reset security controls
    st.session_state.generated_otp = None
    st.session_state.otp_verified = False
    st.session_state.otp_input = ""

    st.session_state.ticket_details = None
    st.session_state.ticket_raised = False

    result = {

        "risk_score": risk_score,

        "risk_level": risk_level,

        "action": action,

        "amount": amount,

        "time": datetime.now().strftime(
            "%H:%M:%S"
        )

    }

    st.session_state.last_result = result

    st.session_state.current_transaction = result

    st.session_state.history.append(result)


# ================================================================
# SHOW LIVE RESULT
# ================================================================

if st.session_state.last_result:

    result = st.session_state.last_result

    risk_score = result["risk_score"]

    risk_level = result["risk_level"]

    action = result["action"]

    amount = result["amount"]

    icon = {
        "LOW": "🟢",
        "MEDIUM": "🟠",
        "HIGH": "🔴"
    }[risk_level]

    # ============================================================
    # RISK METER
    # ============================================================

    st.header("🚦 Live Risk Meter")

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
                max(risk_score, 0),
                100
            )
        )
    )

    # ============================================================
    # RESULT CARD
    # ============================================================

    if risk_level == "HIGH":

        st.markdown(
            f"""
<div class="card red-card">

<h2>🔴 HIGH-RISK PAYMENT</h2>

<p>Payment has been placed on HOLD.</p>

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

<p><b>Risk Score:</b> {risk_score:.2f}%</p>

<p><b>Action:</b> ALLOW</p>

</div>
""",
            unsafe_allow_html=True
        )


    # ============================================================
    # EXPLAINABLE AI
    # ============================================================

   # ============================================================
# EXPLAINABLE AI
# ============================================================

st.header("🧠 Explainable AI")

# Calculate safely
amount_to_monthly_spend = amount / max(monthly_spend, 1)

reasons = []

if merchant_risk >= 0.6:
    reasons.append("⚠️ Merchant risk score is elevated.")
else:
    reasons.append("✅ Merchant risk is within normal range.")

if amount_to_monthly_spend > 0.5:
    reasons.append(
        "⚠️ Transaction amount is high relative to monthly spending."
    )
else:
    reasons.append(
        "✅ Transaction amount is consistent with customer spending."
    )

if failed_24h > 3:
    reasons.append("⚠️ Multiple failed transactions detected.")
else:
    reasons.append("✅ Recent transaction failure activity is low.")

if ip_risk >= 0.6:
    reasons.append("⚠️ IP risk score is elevated.")
else:
    reasons.append("✅ IP risk is within normal range.")

for reason in reasons:
    st.write(reason)


    # ============================================================
    # AI RECOMMENDATION
    # ============================================================

    st.header("🤖 AI Recommendation")

    if risk_level == "HIGH":

        recommendation = (
            "Hold this payment and create a security ticket "
            "because the fraud risk is high."
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
        "🤖 PayShield recommends: "
        + recommendation
    )


    # ============================================================
    # SECURITY CENTER
    # ============================================================

    st.header("🔐 Security Center")


    # ============================================================
    # MEDIUM RISK — 2FA
    # ============================================================

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

        # --------------------------------------------------------
        # SEND OTP
        # --------------------------------------------------------

        if st.session_state.generated_otp is None:

            st.button(
                "📲 SEND OTP",
                key="send_otp",
                type="primary",
                use_container_width=True,
                on_click=send_otp
            )

        # --------------------------------------------------------
        # OTP DISPLAY
        # --------------------------------------------------------

        if st.session_state.generated_otp:

            st.markdown(
                f"""
<div class="otp-card">

<h2>📲 OTP SENT SUCCESSFULLY</h2>

<p>
For this Razorpay Buildathon demonstration,
the generated OTP is displayed below.
</p>

<h1>🔐 {st.session_state.generated_otp}</h1>

<p>Enter this OTP below to verify the payment.</p>

</div>
""",
                unsafe_allow_html=True
            )

            st.text_input(
                "Enter 6-Digit OTP",
                max_chars=6,
                key="otp_input",
                placeholder="Enter OTP"
            )

            st.button(
                "🔐 VERIFY 2FA",
                key="verify_2fa",
                type="primary",
                use_container_width=True,
                on_click=verify_otp
            )

        # --------------------------------------------------------
        # VERIFIED
        # --------------------------------------------------------

        if st.session_state.otp_verified:

            st.markdown(
                """
<div class="verified-card">

<h2>✅ 2FA VERIFIED SUCCESSFULLY</h2>

<p>
Customer identity has been verified.
</p>

<p>
🟢 Payment is APPROVED after successful
two-factor authentication.
</p>

</div>
""",
                unsafe_allow_html=True
            )

            st.success(
                "🟢 SECURITY CHECK PASSED — PAYMENT APPROVED"
            )

            st.balloons()

        elif (
            st.session_state.generated_otp
            and st.session_state.otp_input
            and not st.session_state.otp_verified
        ):

            st.error(
                "❌ OTP not verified. Enter the correct OTP and click VERIFY 2FA."
            )


    # ============================================================
    # HIGH RISK — SECURITY TICKET
    # ============================================================

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

        # --------------------------------------------------------
        # RAISE TICKET
        # --------------------------------------------------------

        if not st.session_state.ticket_raised:

            st.button(
                "🎫 RAISE SECURITY TICKET",
                key="raise_security_ticket",
                type="primary",
                use_container_width=True,
                on_click=raise_ticket
            )

        # --------------------------------------------------------
        # TICKET DETAILS
        # --------------------------------------------------------

        if st.session_state.ticket_raised:

            ticket = st.session_state.ticket_details

            st.markdown(
                f"""
<div class="success-ticket">

<h2>✅ TICKET RAISED SUCCESSFULLY</h2>

<p><b>🎫 Ticket ID:</b> {ticket["Ticket ID"]}</p>

<p><b>📅 Created:</b> {ticket["Created"]}</p>

<p><b>💰 Transaction Amount:</b> {ticket["Amount"]}</p>

<p><b>📊 Risk Score:</b> {ticket["Risk Score"]}</p>

<p><b>🚨 Risk Level:</b> {ticket["Risk Level"]}</p>

<p><b>🛡️ Action:</b> {ticket["Action"]}</p>

<p><b>📌 Status:</b> {ticket["Status"]}</p>

</div>
""",
                unsafe_allow_html=True
            )

            st.success(
                f"🎫 Security team has received ticket "
                f"{ticket['Ticket ID']}."
            )

            st.info(
                "Payment remains on HOLD until the security "
                "team resolves the ticket."
            )


    # ============================================================
    # LOW RISK
    # ============================================================

    else:

        st.success(
            "🟢 SECURITY CHECK PASSED"
        )

        st.write(
            "No additional customer verification is required."
        )


    # ============================================================
    # TRANSACTION SUMMARY
    # ============================================================

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
            if st.session_state.ticket_raised
            else "NOT RAISED"
        )

    else:

        ticket_status = "NOT REQUIRED"

    summary = pd.DataFrame({

        "Field": [

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


    # ============================================================
    # DECISION TIMELINE
    # ============================================================

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

        timeline += [

            "🔴 Payment placed on HOLD",

            (
                "🎫 Security ticket raised"
                if st.session_state.ticket_raised
                else "🎫 Security ticket required"
            ),

            "🛡️ Security Operations review initiated"

        ]

    elif risk_level == "MEDIUM":

        timeline += [

            "🟠 Additional verification required",

            (
                "✅ 2FA verification successful"
                if st.session_state.otp_verified
                else "🔐 OTP verification required"
            )

        ]

    else:

        timeline += [

            "🟢 Security check passed",

            "✓ Payment approved"

        ]

    for item in timeline:

        st.markdown(
            f'<div class="timeline">{item}</div>',
            unsafe_allow_html=True
        )


# ================================================================
# LIVE SECURITY TICKETS
# ================================================================

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

            st.button(
                "✅ RESOLVE",
                key=f"resolve_ticket_{index}",
                use_container_width=True,
                on_click=resolve_ticket,
                args=(index,)
            )

        else:

            t3.success(
                "RESOLVED"
            )

else:

    st.info(
        "No active security tickets."
    )


# ================================================================
# PAYRECOVER AI
# ================================================================

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
            ]
        )

        payment_method = st.selectbox(
            "Payment Method",
            [
                "UPI",
                "CARD",
                "WALLET",
                "NETBANKING"
            ]
        )

        retry_count = st.number_input(
            "Previous Retry Count",
            min_value=0,
            max_value=20,
            value=0
        )

    with f2:

        minutes_since_failure = st.number_input(
            "Minutes Since Failure",
            min_value=0,
            max_value=10000,
            value=5
        )

        customer_success_rate = st.slider(
            "Customer Success Rate",
            0.0,
            1.0,
            0.70
        )

        method_success_rate = st.slider(
            "Method Success Rate",
            0.0,
            1.0,
            0.65
        )

        previous_failures = st.number_input(
            "Previous Failures",
            min_value=0,
            max_value=100,
            value=1
        )

    # ------------------------------------------------------------
    # RECOVERY MODEL
    # ------------------------------------------------------------

    recovery_input = pd.DataFrame([{

        "amount": amount,

        "payment_method": payment_method,

        "failure_reason": failure_reason,

        "retry_count": retry_count,

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

    recovery_input = recovery_input[
        recovery_features
    ]

    recovery_probability = (
        recovery_model.predict_proba(
            recovery_input
        )[0, 1] * 100
    )

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
                max(recovery_probability, 0),
                100
            )
        )
    )


    # ============================================================
    # SMART RETRY AI
    # ============================================================

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

        retry_input = retry_input[
            retry_features
        ]

        probability = (
            retry_model.predict_proba(
                retry_input
            )[0, 1] * 100
        )

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

    best_index = int(
        np.argmax(probabilities)
    )

    best_time = retry_times[best_index]

    best_probability = probabilities[best_index]

    st.success(
        f"⭐ PayRecover AI recommends retrying "
        f"after {best_time} minutes with "
        f"{best_probability:.2f}% predicted success."
    )

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

    x1, x2, x3 = st.columns(3)

    if x1.button(
        "🔄 SCHEDULE RETRY",
        key="schedule_retry",
        use_container_width=True
    ):

        st.success(
            f"Retry scheduled after {best_time} minutes."
        )

    if x2.button(
        "💳 CHANGE METHOD",
        key="change_method",
        use_container_width=True
    ):

        st.info(
            "Payment method change selected."
        )

    if x3.button(
        "🕐 PAY LATER",
        key="pay_later",
        use_container_width=True
    ):

        st.info(
            "Pay Later option selected."
        )


# ================================================================
# PAYMENTOPS AI
# ================================================================

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


# ================================================================
# FINAL DECISION ENGINE
# ================================================================

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


# ================================================================
# FOOTER
# ================================================================

st.divider()

st.caption(
    "🛡️ PayShield AI • FraudShield + PayRecover AI + PaymentOps"
)

st.caption(
    "AI-powered payment protection and recovery platform"
)

st.caption(
    "Razorpay Buildathon Demonstration"
)
