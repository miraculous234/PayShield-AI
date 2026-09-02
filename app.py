import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime


# ================================================================
# PAGE CONFIGURATION
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


# ================================================================
# LOAD MODELS
# ================================================================

@st.cache_resource
def load_models():

    fraud = joblib.load(FRAUD_MODEL)

    recovery = joblib.load(
        RECOVERY_MODEL
    )

    retry = joblib.load(
        RETRY_MODEL
    )

    return fraud, recovery, retry


fraud_model, recovery_model, retry_model = load_models()


# ================================================================
# LOAD FEATURES
# ================================================================

with open(FRAUD_FEATURES) as f:
    fraud_features = json.load(f)

with open(RECOVERY_FEATURES) as f:
    recovery_features = json.load(f)

with open(RETRY_FEATURES) as f:
    retry_features = json.load(f)


# ================================================================
# LOAD DATA
# ================================================================

@st.cache_data
def load_data():

    fraud = pd.read_csv(
        FRAUD_DATA
    )

    recovery = pd.read_csv(
        RECOVERY_DATA
    )

    return fraud, recovery


fraud_data, recovery_data = load_data()


# ================================================================
# SESSION STATE
# ================================================================

if "tickets" not in st.session_state:
    st.session_state.tickets = []

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

if "ticket_message" not in st.session_state:
    st.session_state.ticket_message = ""


# ================================================================
# CUSTOM CSS
# ================================================================

st.markdown("""
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

.timeline {
    padding: 13px;
    margin: 7px 0;
    border-left: 4px solid #4f8cff;
    border-radius: 6px;
    background: rgba(60,65,80,.5);
}

.big-number {
    font-size: 30px;
    font-weight: 800;
}

</style>
""", unsafe_allow_html=True)


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
# 📊 RISK STATISTICS
# ================================================================

st.header("📊 Risk Statistics")

total_transactions = len(
    fraud_data
)


if "is_fraud" in fraud_data.columns:

    fraud_count = int(
        fraud_data["is_fraud"].sum()
    )

else:

    fraud_count = 0


safe_count = (
    total_transactions -
    fraud_count
)


if "recovery_success" in recovery_data.columns:

    recovered_count = int(
        recovery_data["recovery_success"].sum()
    )

else:

    recovered_count = 0


risk_rate = (
    fraud_count /
    max(total_transactions, 1)
) * 100


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
# 🛡️ SECURITY OPERATIONS CENTER
# ================================================================

st.header("🛡️ Security Operations Center")


active_tickets = len([
    x for x in st.session_state.tickets
    if x["Status"] == "🔴 UNDER REVIEW"
])


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


st.info("""
🟢 LOW RISK → ALLOW

🟠 MEDIUM RISK → 2FA VERIFICATION

🔴 HIGH RISK → HOLD + SECURITY TICKET

❌ FAILED PAYMENT → PAYRECOVER AI → SMART RETRY AI
""")


# ================================================================
# 📜 TRANSACTION HISTORY
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


# ================================================================
# 🔍 LIVE AI FRAUD DETECTION
# ================================================================

st.header("🔍 AI Fraud Detection")


if analyze:

    now = datetime.now()

    hour = now.hour

    day = now.weekday()

    international_value = int(
        international == "Yes"
    )


    amount_to_monthly_spend = (
        amount /
        max(monthly_spend, 1)
    )


    failure_rate_24h = (
        failed_24h /
        max(txn_24h, 1)
    )


    velocity_ratio = (
        txn_1h /
        max(txn_24h, 1)
    )


    is_weekend = int(
        day >= 5
    )


    is_night = int(
        hour < 6 or hour >= 22
    )


    # ============================================================
    # BUILD MODEL INPUT
    # ============================================================

    fraud_input = pd.DataFrame([{

        "account_age_days":
            1000,

        "credit_score_band":
            3,

        "kyc_level":
            2,

        "avg_monthly_spend":
            monthly_spend,

        "merchant_risk_score":
            merchant_risk,

        "transaction_amount":
            amount,

        "payment_channel":
            payment_channel,

        "device_type":
            device_type,

        "is_international":
            international_value,

        "ip_risk_score":
            ip_risk,

        "txn_count_1h":
            txn_1h,

        "txn_count_24h":
            txn_24h,

        "failed_txn_count_24h":
            failed_24h,

        "geo_distance_from_last_txn":
            geo_distance,

        "amount_deviation_from_user_mean":
            amount_deviation,

        "post_auth_risk_score":
            post_auth_risk,

        "transaction_hour":
            hour,

        "day_of_week":
            day,

        "is_weekend":
            is_weekend,

        "is_night":
            is_night,

        "amount_to_monthly_spend":
            amount_to_monthly_spend,

        "failure_rate_24h":
            failure_rate_24h,

        "velocity_ratio":
            velocity_ratio,

        "customer_txn_count_before":
            customer_txn_before,

        "customer_avg_amount_before":
            customer_avg_amount,

        "customer_failed_rate_before":
            customer_failed_rate,

        "merchant_txn_count_before":
            merchant_txn_before,

        "merchant_avg_amount_before":
            merchant_avg_amount,

        "merchant_fraud_rate_before":
            merchant_fraud_rate

    }])


    fraud_input = fraud_input[
        fraud_features
    ]


    # ============================================================
    # REAL FRAUD MODEL
    # ============================================================

    fraud_probability = (
        fraud_model
        .predict_proba(
            fraud_input
        )[0, 1]
    )


    risk_score = (
        fraud_probability * 100
    )


    # ============================================================
    # DECISION
    # ============================================================

    if risk_score >= 70:

        risk_level = "HIGH"

        action = "HOLD"

        icon = "🔴"

    elif risk_score >= 30:

        risk_level = "MEDIUM"

        action = "2FA"

        icon = "🟠"

    else:

        risk_level = "LOW"

        action = "ALLOW"

        icon = "🟢"


    # ============================================================
    # RESET SECURITY STATE FOR NEW TRANSACTION
    # ============================================================

    st.session_state.otp_verified = False
    st.session_state.ticket_message = ""

    transaction_id = (
        "TXN-"
        + datetime.now().strftime("%Y%m%d%H%M%S")
        + "-"
        + str(np.random.randint(100, 999))
    )

    # ============================================================
    # SAVE RESULT
    # ============================================================

    st.session_state.last_result = {

        "analysis_id": transaction_id,

        "risk": risk_score,

        "level": risk_level,

        "action": action,

        "amount": amount,

        "time": datetime.now().strftime(
            "%H:%M:%S"
        )

    }


    # ============================================================
    # 🚦 LIVE RISK METER
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
                max(
                    risk_score,
                    0
                ),
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

            <p>
            Payment has been placed on HOLD.
            </p>

            <p>
            <b>Risk Score:</b>
            {risk_score:.2f}%
            </p>

            <p>
            <b>Action:</b>
            HOLD + SECURITY REVIEW
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    elif risk_level == "MEDIUM":

        st.markdown(
            f"""
            <div class="card orange-card">

            <h2>🟠 MEDIUM-RISK PAYMENT</h2>

            <p>
            Additional customer verification required.
            </p>

            <p>
            <b>Risk Score:</b>
            {risk_score:.2f}%
            </p>

            <p>
            <b>Action:</b>
            2FA
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    else:

        st.markdown(
            f"""
            <div class="card green-card">

            <h2>🟢 LOW-RISK PAYMENT</h2>

            <p>
            Transaction appears safe.
            </p>

            <p>
            <b>Risk Score:</b>
            {risk_score:.2f}%
            </p>

            <p>
            <b>Action:</b>
            ALLOW
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ============================================================
    # 🧠 EXPLAINABLE AI
    # ============================================================

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
            "⚠️ Transaction amount is high relative to monthly spending."
        )

    else:

        reasons.append(
            "✅ Transaction amount is consistent with customer spending."
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


    # ============================================================
    # 🤖 AI RECOMMENDATION
    # ============================================================

    st.header("🤖 AI Recommendation")


    if risk_level == "HIGH":

        recommendation = (
            "Hold this payment and create a "
            "security ticket because the fraud risk is high."
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
    # 🔐 SECURITY CENTER
    # ============================================================

    st.header("🔐 Security Center")

    # ------------------------------------------------------------
    # MEDIUM RISK — 2FA
    # ------------------------------------------------------------

    if risk_level == "MEDIUM":

        st.warning(
            "🟠 MEDIUM RISK — 2FA REQUIRED"
        )

        st.subheader(
            "🟠 Two-Factor Authentication"
        )

        st.write(
            "Customer verification is required before payment approval."
        )

        st.info(
            "🔐 Demo OTP: 123456"
        )

        otp = st.text_input(
            "Enter 6-digit OTP",
            type="password",
            max_chars=6,
            key="live_otp"
        )

        if st.button(
            "🔐 VERIFY & APPROVE PAYMENT",
            key="verify_2fa",
            type="primary",
            use_container_width=True
        ):

            if otp.strip() == "123456":

                st.session_state.otp_verified = True

                # Update the saved transaction decision.
                if st.session_state.last_result:
                    st.session_state.last_result["action"] = "APPROVED"

                st.success(
                    "✅ 2FA VERIFIED — PAYMENT APPROVED"
                )

                st.balloons()

                st.rerun()

            else:

                st.session_state.otp_verified = False

                st.error(
                    "❌ INVALID OTP — PAYMENT REMAINS BLOCKED"
                )

        if st.session_state.otp_verified:

            st.success(
                "🟢 Customer identity verified. Payment approved."
            )

    # ------------------------------------------------------------
    # HIGH RISK — HOLD + TICKET
    # ------------------------------------------------------------

    elif risk_level == "HIGH":

        st.error(
            "🔴 HIGH RISK — PAYMENT ON HOLD"
        )

        st.subheader(
            "🎫 Security Operations"
        )

        st.write(
            "This payment is on HOLD. Raise a security ticket "
            "for investigation and review."
        )

        # Do not create duplicate tickets for the same transaction.
        existing_ticket = next(
            (
                ticket for ticket in st.session_state.tickets
                if ticket.get("Transaction ID") == transaction_id
            ),
            None
        )

        if existing_ticket:

            st.warning(
                f"🎫 Ticket {existing_ticket.get('Ticket ID', 'N/A')} "
                "already exists for this transaction."
            )

        else:

            if st.button(
                "🎫 RAISE SECURITY TICKET",
                key="raise_live_ticket",
                type="primary",
                use_container_width=True
            ):

                ticket_id = (
                    "PS-"
                    + datetime.now().strftime("%Y%m%d%H%M%S")
                    + "-"
                    + str(np.random.randint(100, 999))
                )

                new_ticket = {

                    "Ticket ID": ticket_id,

                    "Transaction ID": transaction_id,

                    "Created": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    "Amount": f"₹{amount:,.2f}",

                    "Risk Score": f"{risk_score:.2f}%",

                    "Risk Level": "🔴 HIGH",

                    "Action": "HOLD",

                    "Status": "🔴 UNDER REVIEW",

                    "Payment Channel": payment_channel,

                    "Device": device_type,

                    "IP Risk": f"{ip_risk:.2f}",

                    "Merchant Risk": f"{merchant_risk:.2f}",

                    "Failed Transactions": failed_24h,

                    "International": international,

                    "Reason": (
                        "High fraud risk detected by FraudShield AI. "
                        "Payment placed on hold for security review."
                    )
                }

                st.session_state.tickets.append(
                    new_ticket
                )

                st.session_state.ticket_message = (
                    f"🎫 Ticket {ticket_id} created successfully."
                )

                st.rerun()

        if st.session_state.ticket_message:

            st.success(
                st.session_state.ticket_message
            )

    # ------------------------------------------------------------
    # LOW RISK — ALLOW
    # ------------------------------------------------------------

    else:

        st.success(
            "🟢 SECURITY CHECK PASSED — PAYMENT ALLOWED"
        )

        st.write(
            "No additional customer verification is required."
        )


    # ============================================================
    # 📋 TRANSACTION SUMMARY
    # ============================================================

    st.header("📋 Transaction Summary")


    summary = pd.DataFrame({

        "Field": [

            "Amount",

            "Risk Score",

            "Risk Level",

            "Fraud Action",

            "2FA",

            "Recovery",

            "Best Retry",

            "Retry Success"

        ],


        "Value": [

            f"₹{amount:,.2f}",

            f"{risk_score:.2f}%",

            f"{icon} {risk_level}",

            action,

            (
                "✅ VERIFIED"
                if st.session_state.otp_verified
                else ("🔐 REQUIRED" if risk_level == "MEDIUM" else "NO")
            ),

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
    # 🧠 LIVE DECISION TIMELINE
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

            "🎫 Security ticket required",

            "🛡️ Security Operations review initiated"

        ]


    elif risk_level == "MEDIUM":

        timeline += [

            "🟠 Additional verification required",

            "🔐 2FA challenge generated"

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
# 🎫 SECURITY OPERATIONS CENTER — LIVE TICKETS
# ================================================================

st.divider()

st.header("🎫 Live Security Tickets")

if st.session_state.ticket_message:

    st.success(
        st.session_state.ticket_message
    )

if st.session_state.tickets:

    st.subheader(
        f"📊 {len(st.session_state.tickets)} Security Ticket(s)"
    )

    for index, ticket in enumerate(st.session_state.tickets):

        status = ticket.get(
            "Status",
            "🔴 UNDER REVIEW"
        )

        if status == "🔴 UNDER REVIEW":

            st.markdown(
                f"""
                <div class="card red-card">
                    <h3>🎫 {ticket.get('Ticket ID', 'N/A')}</h3>
                    <p><b>Status:</b> 🔴 UNDER REVIEW</p>
                    <p><b>Transaction:</b> {ticket.get('Transaction ID', 'N/A')}</p>
                    <p><b>Risk:</b> 🔴 HIGH — {ticket.get('Risk Score', 'N/A')}</p>
                    <p><b>Amount:</b> {ticket.get('Amount', 'N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="card green-card">
                    <h3>🎫 {ticket.get('Ticket ID', 'N/A')}</h3>
                    <p><b>Status:</b> 🟢 RESOLVED</p>
                    <p><b>Transaction:</b> {ticket.get('Transaction ID', 'N/A')}</p>
                    <p><b>Amount:</b> {ticket.get('Amount', 'N/A')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with st.expander(
            "🔍 View Complete Ticket Details",
            expanded=False
        ):

            d1, d2 = st.columns(2)

            with d1:
                st.write(f"**🎫 Ticket ID:** {ticket.get('Ticket ID', 'N/A')}")
                st.write(f"**💳 Transaction ID:** {ticket.get('Transaction ID', 'N/A')}")
                st.write(f"**💰 Amount:** {ticket.get('Amount', 'N/A')}")
                st.write(f"**📊 Risk Score:** {ticket.get('Risk Score', 'N/A')}")
                st.write(f"**🚦 Risk Level:** {ticket.get('Risk Level', 'N/A')}")
                st.write(f"**⚡ Action:** {ticket.get('Action', 'N/A')}")
                st.write(f"**📡 Payment Channel:** {ticket.get('Payment Channel', 'N/A')}")

            with d2:
                st.write(f"**📱 Device:** {ticket.get('Device', 'N/A')}")
                st.write(f"**🌐 IP Risk:** {ticket.get('IP Risk', 'N/A')}")
                st.write(f"**🏪 Merchant Risk:** {ticket.get('Merchant Risk', 'N/A')}")
                st.write(f"**❌ Failed Transactions:** {ticket.get('Failed Transactions', 'N/A')}")
                st.write(f"**🌍 International:** {ticket.get('International', 'N/A')}")
                st.write(f"**🕐 Created:** {ticket.get('Created', 'N/A')}")

            st.info(
                f"🔎 **Reason for Review:** {ticket.get('Reason', 'N/A')}"
            )

        if status == "🔴 UNDER REVIEW":

            if st.button(
                "✅ RESOLVE TICKET",
                key=f"resolve_ticket_{index}",
                type="primary",
                use_container_width=True
            ):

                st.session_state.tickets[index][
                    "Status"
                ] = "🟢 RESOLVED"

                st.session_state.ticket_message = (
                    f"✅ Ticket {ticket.get('Ticket ID', 'N/A')} "
                    "resolved successfully."
                )

                st.rerun()

        else:

            st.success("🟢 TICKET RESOLVED")

else:

    st.info(
        "🟢 No security tickets yet. A ticket will appear here "
        "when a high-risk transaction is placed on hold."
    )


# ================================================================
# 💰 PAYRECOVER AI
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


    # ============================================================
    # RECOVERY MODEL
    # ============================================================

    recovery_input = pd.DataFrame([{

        "amount":
            amount,

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
            int(
                international == "Yes"
            ),

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

        recovery_model
        .predict_proba(
            recovery_input
        )[0, 1]

        * 100

    )


    # ============================================================
    # 💰 RECOVERY VISUALIZATION
    # ============================================================

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


    # ============================================================
    # ⏰ SMART RETRY AI
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

            retry_model
            .predict_proba(
                retry_input
            )[0, 1]

            * 100

        )


        probabilities.append(
            probability
        )


    # ============================================================
    # RETRY VISUALIZATION
    # ============================================================

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


    # ============================================================
    # BEST RETRY
    # ============================================================

    best_index = int(
        np.argmax(
            probabilities
        )
    )


    best_time = retry_times[
        best_index
    ]


    best_probability = probabilities[
        best_index
    ]


    st.success(
        f"⭐ PayRecover AI recommends retrying "
        f"after {best_time} minutes with "
        f"{best_probability:.2f}% predicted success."
    )


    # ============================================================
    # RECOVERY SUMMARY
    # ============================================================

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


    # ============================================================
    # RECOVERY ACTIONS
    # ============================================================

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
# 🤖 PAYMENTOPS AI
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


st.markdown("""
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
""", unsafe_allow_html=True)


# ================================================================
# 🧠 FINAL DECISION ENGINE
# ================================================================

st.divider()

st.header(
    "🧠 PayShield Decision Engine"
)


st.markdown("""
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
""", unsafe_allow_html=True)


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
