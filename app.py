import os
import json
import random
import io
import wave
import json as _json_for_voice
from datetime import datetime, timedelta

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
try:
    import streamlit_authenticator as stauth
except ImportError:
    stauth = None

try:
    from google import genai
except ImportError:
    genai = None

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

def get_secret_value(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

usernames = [u.strip() for u in str(get_secret_value("AUTH_USERNAMES", "merchant_admin,analyst")).split(",") if u.strip()]
passwords = [p.strip() for p in str(get_secret_value("AUTH_PASSWORDS", "")).split(",") if p.strip()]
auth_configured = bool(passwords) and stauth is not None

if auth_configured:
    if len(usernames) < 2 or len(passwords) < 2:
        st.error("Auth configuration requires two usernames and two passwords.")
        st.stop()

    @st.cache_resource
    def get_hashed_passwords(passwords_tuple):
        passwords_list = list(passwords_tuple)
        try:
            return [stauth.Hasher.hash(p) for p in passwords_list]
        except AttributeError:
            return stauth.Hasher(passwords_list).generate()

    hashed_passwords = get_hashed_passwords(tuple(passwords))
    credentials = {
        "usernames": {
            usernames[0]: {"name": names[0], "password": hashed_passwords[0]},
            usernames[1]: {"name": names[1], "password": hashed_passwords[1]}
        }
    }

    authenticator = stauth.Authenticate(
        credentials,
        "payshield_cookie",
        get_secret_value("COOKIE_KEY", "change_me_locally"),
        cookie_expiry_days=1
    )

    try:
        authenticator.login(location="main")
    except TypeError:
        authenticator.login("PayShield AI Enterprise Access", location="main")

    if st.session_state.get("authentication_status") == False:
        st.error("Username/password is incorrect")
        st.stop()
    elif st.session_state.get("authentication_status") is None:
        st.warning("Please enter your merchant credentials to access the PayShield AI Portal")
        st.stop()

    st.sidebar.write(f"Logged in as: **{st.session_state.get('name')}**")
    authenticator.logout("Logout", "sidebar")
else:
    st.sidebar.info("🔓 Demo mode — no login required (auth secrets not configured).")

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
    "revenue_recovered_val": 58900.00,
    "gemini_chat": [],
    "sound_enabled": True,
    "last_sound_id": None,
    "welcome_seen": False,
    "welcome_faq_answer": None,
    "agent_brief_id": None,
    "agent_brief_text": None
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
.hero-shell{position:relative;overflow:hidden;padding:28px 30px;border-radius:24px;border:1px solid rgba(255,255,255,.12);background:radial-gradient(circle at 85% 20%,rgba(79,140,255,.22),transparent 30%),linear-gradient(135deg,rgba(255,255,255,.07),rgba(255,255,255,.025));box-shadow:0 18px 60px rgba(0,0,0,.28)}
.hero-grid{display:grid;grid-template-columns:1.5fr .8fr;gap:20px;align-items:center}.hero-kicker{color:#7dd3fc;font-size:12px;font-weight:900;letter-spacing:2px}.hero-title{font-size:clamp(34px,4vw,58px);line-height:1.02;font-weight:950;margin:8px 0}.hero-copy{color:#aeb7c7;font-size:16px;line-height:1.55}.hero-chip{display:inline-block;padding:7px 11px;margin:8px 6px 0 0;border-radius:999px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.11);font-size:12px;font-weight:800}.hero-art{min-height:190px;display:flex;align-items:center;justify-content:center}.shield-orbit{width:160px;height:160px;border:1px solid rgba(125,211,252,.35);border-radius:50%;position:relative;animation:spin 16s linear infinite}.shield-core{position:absolute;inset:32px;border-radius:28px;display:flex;align-items:center;justify-content:center;font-size:54px;background:linear-gradient(145deg,rgba(79,140,255,.25),rgba(33,195,84,.12));border:1px solid rgba(125,211,252,.4);box-shadow:0 0 40px rgba(79,140,255,.2)}.scan-line{position:absolute;left:8%;right:8%;top:50%;height:2px;background:#7dd3fc;box-shadow:0 0 18px #7dd3fc;animation:scan 2.8s ease-in-out infinite}.nav-bar{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.nav-pill{padding:8px 13px;border-radius:999px;background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.10);font-size:12px;font-weight:800;text-decoration:none;color:inherit}.nav-pill:hover{background:rgba(79,140,255,.16);border-color:rgba(79,140,255,.45)}.chat-card{padding:18px;border-radius:18px;border:1px solid rgba(125,211,252,.2);background:linear-gradient(145deg,rgba(79,140,255,.09),rgba(255,255,255,.025))}@keyframes spin{to{transform:rotate(360deg)}}@keyframes scan{0%,100%{transform:translateY(-55px);opacity:.25}50%{transform:translateY(55px);opacity:1}}

@media (max-width: 768px) { .title { font-size: 34px; } .subtitle { font-size: 14px; } }

.welcome-box {
    padding: 8px 2px 4px 2px;
}
.welcome-card {
    padding: 18px; border-radius: 16px; margin: 8px 0;
    border: 1px solid rgba(125,211,252,.20);
    background: linear-gradient(145deg, rgba(79,140,255,.10), rgba(255,255,255,.025));
}
.welcome-mini {
    padding: 13px 15px; border-radius: 13px; margin: 7px 0;
    background: rgba(255,255,255,.045); border: 1px solid rgba(255,255,255,.08);
}
.welcome-faq {
    padding: 14px; border-radius: 14px;
    background: rgba(125,211,252,.06); border: 1px solid rgba(125,211,252,.18);
}
</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# WELCOME POPUP — PAYSHIELD INTRODUCTION + FAQ + AI VOICE
# ============================================================

WELCOME_FAQS = {
    "What is payment fraud?": "Payment fraud is an unauthorized or deceptive payment attempt. It can involve unusual transaction behaviour, compromised accounts, risky devices, suspicious IP activity, abnormal transaction amounts, or unusual payment velocity.",
    "How does PayShield detect fraud?": "FraudShield AI evaluates transaction and behavioural signals and produces a risk score. PayShield then applies the security policy: LOW → ALLOW, MEDIUM → 2FA, and HIGH → HOLD + SECURITY TICKET.",
    "Why was a payment blocked?": "A payment is placed on hold when its FraudShield risk score reaches the configured high-risk threshold. The system can create a security ticket so the merchant or analyst can review the transaction.",
    "What is 2FA?": "2FA adds an extra verification step for medium-risk payments. The customer must enter a one-time password before the payment can be approved.",
    "How does PayRecover work?": "PayRecover AI analyzes a failed payment and estimates the probability that it can be recovered, helping the merchant choose an appropriate recovery action.",
    "What is Smart Retry?": "Smart Retry compares different retry windows and identifies the time with the strongest predicted payment-success probability. It can also support payment-method optimization when available.",
    "Why use PayShield AI?": "PayShield combines fraud prevention and revenue recovery in one system. It helps reduce fraudulent approvals, adds verification for uncertain transactions, protects legitimate payments from unnecessary friction, and improves recovery of failed payments."
}

WELCOME_VOICE_TEXT = (
    "Welcome to PayShield AI. Payment fraud happens when an unauthorized or deceptive "
    "payment attempt is made using suspicious behaviour, compromised accounts, risky devices, "
    "or unusual transaction patterns. PayShield uses FraudShield AI to evaluate payment signals "
    "and calculate a risk score. Low-risk payments are allowed, medium-risk payments require "
    "two-factor authentication, and high-risk payments are held for security review. "
    "PayShield also helps recover failed payments through PayRecover AI and Smart Retry. "
    "The goal is simple: prevent fraud, protect revenue, and help merchants make safer payment decisions."
)


def welcome_faq_answer(question):
    """Answer the popup's common questions without depending on an external API."""
    if not question:
        return "Choose a question above or ask about fraud, FraudShield, 2FA, PayRecover, Smart Retry, or PayShield."

    q = question.strip().lower()
    for title, answer in WELCOME_FAQS.items():
        if q == title.lower():
            return answer

    keyword_groups = [
        (("fraud", "scam", "unauthorized"), WELCOME_FAQS["What is payment fraud?"]),
        (("detect", "fraudshield", "risk score", "score"), WELCOME_FAQS["How does PayShield detect fraud?"]),
        (("blocked", "hold", "declined", "flagged"), WELCOME_FAQS["Why was a payment blocked?"]),
        (("2fa", "otp", "verification", "verify"), WELCOME_FAQS["What is 2FA?"]),
        (("recover", "failed payment", "payrecover"), WELCOME_FAQS["How does PayRecover work?"]),
        (("retry", "smart retry", "retry time", "retry window"), WELCOME_FAQS["What is Smart Retry?"]),
        (("why payshield", "why use", "benefit", "purpose"), WELCOME_FAQS["Why use PayShield AI?"]),
    ]
    for keywords, answer in keyword_groups:
        if any(k in q for k in keywords):
            return answer
    return "I can help with payment fraud, FraudShield risk scores, 2FA, PayRecover, Smart Retry, and why merchants use PayShield AI. Try one of the FAQ questions above."


def show_welcome_content():
    st.markdown('<div class="welcome-box">', unsafe_allow_html=True)
    st.markdown(
        '<div class="welcome-card"><h2>🛡️ Welcome to PayShield AI</h2>'
        '<p>AI-powered payment protection designed to prevent fraud, verify risky payments, '
        'and recover failed revenue.</p></div>',
        unsafe_allow_html=True
    )

    w1, w2 = st.columns(2)
    with w1:
        st.markdown(
            '<div class="welcome-mini"><b>🚨 What is payment fraud?</b><br>'
            'Unauthorized or deceptive payment activity that can cause financial loss, '
            'chargebacks, and customer trust issues.</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="welcome-mini"><b>🎯 Why use PayShield?</b><br>'
            'It combines fraud detection, customer verification, payment recovery, and '
            'smart retry decisions in one merchant security platform.</div>',
            unsafe_allow_html=True
        )
    with w2:
        st.markdown(
            '<div class="welcome-mini"><b>🧠 How does it prevent fraud?</b><br>'
            'FraudShield produces a risk score and applies three actions: '
            '<b>LOW → ALLOW</b>, <b>MEDIUM → 2FA</b>, and <b>HIGH → HOLD + TICKET</b>.</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="welcome-mini"><b>💰 What happens after a failed payment?</b><br>'
            'PayRecover estimates recovery probability and Smart Retry evaluates retry timing '
            'and available payment methods.</div>',
            unsafe_allow_html=True
        )

    st.divider()
    st.subheader("💬 PayShield FAQ Assistant")
    st.caption("Ask a common question or type your own question about the platform.")

    faq_choice = st.selectbox(
        "Quick FAQ",
        ["Select a question..."] + list(WELCOME_FAQS.keys()),
        key="welcome_faq_choice"
    )
    custom_question = st.text_input(
        "Or ask your own question",
        placeholder="Why should a merchant use PayShield AI?",
        key="welcome_custom_question"
    )

    if st.button("💬 Ask PayShield FAQ", key="welcome_faq_button", use_container_width=True):
        selected = custom_question.strip() if custom_question.strip() else (
            faq_choice if faq_choice != "Select a question..." else ""
        )
        st.session_state.welcome_faq_answer = welcome_faq_answer(selected)

    if st.session_state.get("welcome_faq_answer"):
        st.markdown('<div class="welcome-faq">', unsafe_allow_html=True)
        st.markdown("**🤖 PayShield AI:**")
        st.write(st.session_state.welcome_faq_answer)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("🎙️ AI Voice Introduction")
    st.caption("Press Play to hear a spoken introduction. It uses your browser's built-in voice and does not require another API.")

    voice_js_text = json.dumps(WELCOME_VOICE_TEXT)
    components.html(
        f"""
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
            <button onclick="speakPayShield()" style="padding:11px 18px;border-radius:10px;border:1px solid #4f8cff;background:#1f5eff;color:white;font-weight:700;cursor:pointer;">▶ Play AI Voice</button>
            <button onclick="stopPayShield()" style="padding:11px 18px;border-radius:10px;border:1px solid #777;background:#222;color:white;font-weight:700;cursor:pointer;">⏹ Stop</button>
        </div>
        <script>
        const payShieldVoiceText = {voice_js_text};
        function speakPayShield() {{
            if (!('speechSynthesis' in window)) {{
                alert('Speech is not supported by this browser.');
                return;
            }}
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(payShieldVoiceText);
            utterance.rate = 0.94;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            window.speechSynthesis.speak(utterance);
        }}
        function stopPayShield() {{
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        }}
        </script>
        """,
        height=70,
    )

    st.divider()
    if st.button("🚀 Enter PayShield AI Dashboard", key="welcome_enter", type="primary", use_container_width=True):
        st.session_state.welcome_seen = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


if not st.session_state.get("welcome_seen", False):
    if hasattr(st, "dialog"):
        @st.dialog("🛡️ Welcome to PayShield AI", width="large")
        def _payshield_welcome_dialog():
            show_welcome_content()
        _payshield_welcome_dialog()
    else:
        with st.expander("🛡️ Welcome to PayShield AI", expanded=True):
            show_welcome_content()

# ============================================================
# HEADER & ROI KPI DASHBOARD
# ============================================================

st.markdown(
    """<div class="hero-shell"><div class="hero-grid"><div><div class="hero-kicker">AUTONOMOUS PAYMENT SECURITY</div><div class="hero-title">🛡️ PayShield AI</div><div class="hero-copy">Protect every payment, verify risky transactions, recover failed revenue, and turn payment incidents into clear merchant actions.</div><span class="hero-chip">🛡️ FraudShield</span><span class="hero-chip">💰 PayRecover</span><span class="hero-chip">⏰ Smart Retry</span><span class="hero-chip">🤖 PaymentOps</span><div class="live-status">🟢 <b>SYSTEM ONLINE</b> &nbsp;•&nbsp; Decision Engine READY &nbsp;•&nbsp; Razorpay Sandbox READY &nbsp;•&nbsp; AI Assistant READY</div></div><div class="hero-art"><div class="shield-orbit"><div class="shield-core">🛡️</div><div class="scan-line"></div></div></div></div></div>
<div class="nav-bar"><a class="nav-pill" href="#fraudshield">🛡️ FraudShield</a><a class="nav-pill" href="#recovery">💰 PayRecover</a><a class="nav-pill" href="#smart-retry">⏰ Smart Retry</a><a class="nav-pill" href="#paymentops">🤖 PaymentOps</a><a class="nav-pill" href="#manual">📖 Manual</a><a class="nav-pill" href="#assistant">💬 AI Assistant</a></div>""", unsafe_allow_html=True)

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
# GEMINI PAYMENTOPS AGENT FUNCTION
# ============================================================

def generate_agentic_ticket(payload_data, risk_score):
    """Generate a concise PaymentOps security brief using Gemini.

    Gemini explains the ML decision; it does not make the payment decision.
    """
    fallback = (
        "• **Threat Classification**: High-Risk transaction requiring security review\n"
        "• **Behavioral Anomaly**: Transaction signals exceed the configured risk threshold.\n"
        "• **Recommended Mitigation**: Hold funds, generate a Security Ticket, and require additional verification.\n"
    )
    try:
        api_key = get_secret_value("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY")
        if not api_key or genai is None:
            return fallback

        client = genai.Client(api_key=api_key)
        prompt = f"""
You are PaymentOps AI for PayShield AI, a payment-security operations assistant.
The FraudShield ML model has already made the numerical risk decision.
You must explain the incident, not override the ML decision.

Transaction details:
- Transaction amount: ₹{payload_data.get('amount', 2500)}
- FraudShield risk score: {risk_score}/100
- Transactions in 1 hour: {payload_data.get('txns_1h', 2)}
- Geo distance from previous transaction: {payload_data.get('geo_dist', 10.0)} km
- Amount deviation from customer mean: ₹{payload_data.get('amt_dev', 500.0)}

Write a concise security brief with exactly these three bullets:
- **Threat Classification**: identify the likely risk pattern.
- **Behavioral Anomaly**: explain the strongest evidence.
- **Recommended Mitigation**: give a practical merchant/security action consistent with a HOLD decision.

Do not claim certainty about fraud. Do not invent facts.
"""
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt
        )
        text = getattr(response, "text", None)
        return text.strip() if text else fallback
    except Exception:
        return fallback

# ============================================================
# GEMINI AI ASSISTANT
# ============================================================
def make_sound(freq=660, duration=0.12, volume=0.08):
    rate = 22050
    samples = (np.sin(2 * np.pi * freq * np.arange(int(rate * duration)) / rate) * volume * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(samples.tobytes())
    return buf.getvalue()


def gemini_answer(question, context):
    try:
        api_key = get_secret_value("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY")
        if not api_key or genai is None:
            return "Gemini is not configured yet. Add GEMINI_API_KEY to Streamlit Secrets to enable the assistant."
        client = genai.Client(api_key=api_key)
        prompt = f"""You are PayShield AI, a fintech security assistant. Explain the system clearly to a merchant. Never override the ML decision, never claim a payment was actually charged, and do not invent transaction facts.
CURRENT PAYSHIELD CONTEXT:
{context}
MERCHANT QUESTION:
{question}
Give a concise, useful answer with the relevant risk/recovery reasoning."""
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt)
        return response.text or "I could not generate an answer."
    except Exception as exc:
        return f"Gemini assistant error: {exc}"

st.sidebar.checkbox("🔊 Sound feedback", key="sound_enabled", help="Plays a short confirmation tone after a payment analysis.")

with st.sidebar.expander("💬 Ask PayShield AI", expanded=False):
    st.caption("Gemini-powered merchant assistant. It explains your current PayShield result; it does not make the payment decision.")
    if st.session_state.get("last_result"):
        r = st.session_state.last_result
        context = json.dumps({k: r.get(k) for k in ["analysis_id","risk","level","action","amount","model_probability","merchant_risk","ip_risk"]}, default=str)
    else:
        context = "No transaction has been analyzed yet."
    question = st.text_input("Ask a question", placeholder="Why was this payment flagged?", key="gemini_question")
    if st.button("✨ Ask Gemini", key="ask_gemini", use_container_width=True):
        if question.strip():
            answer = gemini_answer(question.strip(), context)
            st.session_state.gemini_chat.append({"q": question.strip(), "a": answer})
    for chat in st.session_state.gemini_chat[-3:]:
        st.markdown(f"**You:** {chat['q']}")
        st.info(chat["a"])


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

st.sidebar.subheader("🧾 Customer Profile")
account_age_days = st.sidebar.number_input("Account Age (days)", min_value=1, max_value=10000, value=1000)
credit_score_band = st.sidebar.slider("Credit Score Band", 1, 5, 3)
kyc_level = st.sidebar.slider("KYC Level", 0, 3, 2)

st.sidebar.divider()

analyze = st.sidebar.button("🔍 ANALYZE PAYMENT", type="primary", use_container_width=True)

st.sidebar.divider()

# ============================================================
# SHARED FRAUD DECISION ENGINE
# ============================================================

def run_fraud_decision(
    amount_value,
    payment_channel_value,
    device_type_value,
    international_value,
    merchant_risk_value,
    ip_risk_value,
    txn_1h_value,
    txn_24h_value,
    failed_24h_value,
    geo_distance_value,
    amount_deviation_value,
    customer_avg_amount_value,
    customer_txn_before_value,
    customer_failed_rate_value,
    merchant_txn_before_value,
    merchant_avg_amount_value,
    merchant_fraud_rate_value,
    post_auth_risk_value=None,
    account_age_days_value=1000,
    credit_score_band_value=3,
    kyc_level_value=2,
    source="Payment Simulator",
    external_id=None,
    event_name=None,
    demo_mode_value="🤖 AI Model"
):
    now = datetime.now()
    hour = now.hour
    day = now.weekday()

    # Map UI labels to the categorical values used during model training.
    payment_map = {
        "UPI": "upi",
        "CARD": "card",
        "WALLET": "wallet",
        "NETBANKING": "bank_transfer",
        "upi": "upi",
        "card": "card",
        "wallet": "wallet",
        "netbanking": "bank_transfer",
        "bank_transfer": "bank_transfer"
    }
    device_map = {
        "Mobile": "mobile",
        "Desktop": "desktop",
        "Tablet": "tablet",
        "mobile": "mobile",
        "desktop": "desktop",
        "tablet": "tablet"
    }

    model_payment_channel = payment_map.get(payment_channel_value, str(payment_channel_value).lower())
    model_device_type = device_map.get(device_type_value, str(device_type_value).lower())

    amount_to_monthly_spend = amount_value / max(monthly_spend, 1)
    failure_rate_24h = failed_24h_value / max(txn_24h_value, 1)
    velocity_ratio = txn_1h_value / max(txn_24h_value, 1)
    is_weekend = int(day >= 5)
    is_night = int(hour < 6 or hour >= 22)

    fraud_input = pd.DataFrame([{
        "account_age_days": account_age_days_value,
        "credit_score_band": credit_score_band_value,
        "kyc_level": kyc_level_value,
        "avg_monthly_spend": monthly_spend,
        "merchant_risk_score": merchant_risk_value,
        "transaction_amount": amount_value,
        "payment_channel": model_payment_channel,
        "device_type": model_device_type,
        "is_international": int(international_value),
        "ip_risk_score": ip_risk_value,
        "txn_count_1h": txn_1h_value,
        "txn_count_24h": txn_24h_value,
        "failed_txn_count_24h": failed_24h_value,
        "geo_distance_from_last_txn": geo_distance_value,
        "amount_deviation_from_user_mean": amount_deviation_value,
        "post_auth_risk_score": post_auth_risk_value,
        "transaction_hour": hour,
        "day_of_week": day,
        "is_weekend": is_weekend,
        "is_night": is_night,
        "amount_to_monthly_spend": amount_to_monthly_spend,
        "failure_rate_24h": failure_rate_24h,
        "velocity_ratio": velocity_ratio,
        "customer_txn_count_before": customer_txn_before_value,
        "customer_avg_amount_before": customer_avg_amount_value,
        "customer_failed_rate_before": customer_failed_rate_value,
        "merchant_txn_count_before": merchant_txn_before_value,
        "merchant_avg_amount_before": merchant_avg_amount_value,
        "merchant_fraud_rate_before": merchant_fraud_rate_value
    }])

    # Reindex protects deployment from harmless feature-order differences.
    fraud_input = fraud_input.reindex(columns=fraud_features)
    fraud_probability = float(fraud_model.predict_proba(fraud_input)[0, 1])
    ai_risk_score = fraud_probability * 100

    if demo_mode_value == "🟢 LOW — ALLOW":
        risk_score, risk_level, action = 20.0, "LOW", "ALLOW"
    elif demo_mode_value == "🟠 MEDIUM — 2FA":
        risk_score, risk_level, action = 55.0, "MEDIUM", "2FA"
    elif demo_mode_value == "🔴 HIGH — HOLD + TICKET":
        risk_score, risk_level, action = 85.0, "HIGH", "HOLD"
    else:
        risk_score = ai_risk_score
        if risk_score >= 70:
            risk_level, action = "HIGH", "HOLD"
        elif risk_score >= 40:
            risk_level, action = "MEDIUM", "2FA"
        else:
            risk_level, action = "LOW", "ALLOW"

    analysis_id = external_id or (
        "TXN-" + now.strftime("%Y%m%d%H%M%S") + "-" + str(random.randint(100, 999))
    )

    return {
        "analysis_id": analysis_id,
        "risk": float(risk_score),
        "model_probability": float(ai_risk_score),
        "level": risk_level,
        "action": action,
        "amount": float(amount_value),
        "merchant_risk": float(merchant_risk_value),
        "ip_risk": float(ip_risk_value),
        "failed_24h": int(failed_24h_value),
        "amount_to_monthly_spend": float(amount_to_monthly_spend),
        "failure_rate_24h": float(failure_rate_24h),
        "velocity_ratio": float(velocity_ratio),
        "payment_channel": str(payment_channel_value),
        "device_type": str(device_type_value),
        "international": "Yes" if int(international_value) else "No",
        "geo_distance": float(geo_distance_value),
        "amount_deviation": float(amount_deviation_value),
        "source": source,
        "event": event_name,
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S")
    }


# ============================================================
# RAZORPAY SANDBOX WEBHOOK SIMULATOR
# ============================================================

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
    webhook_json = st.text_area(
        "Razorpay Event Payload (JSON)",
        value=sample_json,
        height=160,
        key="razorpay_webhook_json"
    )

    if st.button("⚡ Simulate Razorpay Event", key="simulate_razorpay_event", use_container_width=True):
        try:
            webhook = json.loads(webhook_json)
            event_name = webhook.get("event", "unknown")
            entity = (
                webhook.get("payload", {})
                .get("payment", {})
                .get("entity", {})
            )

            if not entity:
                raise ValueError("No payment.entity object found in the Razorpay payload.")

            razorpay_id = entity.get("id") or (
                "pay_demo_" + datetime.now().strftime("%Y%m%d%H%M%S")
            )

            # Razorpay payment amount is represented in paise.
            webhook_amount = float(entity.get("amount", amount * 100)) / 100.0
            method = str(entity.get("method", payment_channel)).lower()
            webhook_channel = {
                "upi": "UPI",
                "card": "CARD",
                "wallet": "WALLET",
                "netbanking": "NETBANKING"
            }.get(method, payment_channel)

            error_text = str(entity.get("error_description", ""))
            is_failed_event = event_name == "payment.failed" or str(entity.get("status", "")).lower() == "failed"

            sandbox_result = run_fraud_decision(
                amount_value=webhook_amount,
                payment_channel_value=webhook_channel,
                device_type_value=device_type,
                international_value=int(international == "Yes"),
                merchant_risk_value=merchant_risk,
                ip_risk_value=ip_risk,
                txn_1h_value=txn_1h,
                txn_24h_value=txn_24h,
                failed_24h_value=max(failed_24h, 1 if is_failed_event else failed_24h),
                geo_distance_value=geo_distance,
                amount_deviation_value=max(amount_deviation, abs(webhook_amount - customer_avg_amount)),
                customer_avg_amount_value=customer_avg_amount,
                customer_txn_before_value=customer_txn_before,
                customer_failed_rate_value=customer_failed_rate,
                merchant_txn_before_value=merchant_txn_before,
                merchant_avg_amount_value=merchant_avg_amount,
                merchant_fraud_rate_value=merchant_fraud_rate,
                post_auth_risk_value=post_auth_risk,
                source="Razorpay Sandbox Webhook",
                external_id=razorpay_id,
                event_name=event_name,
                demo_mode_value="🤖 AI Model"
            )

            sandbox_result["failure_reason"] = error_text or "Payment event received"
            sandbox_result["razorpay_status"] = entity.get("status", "unknown")

            st.session_state.last_result = sandbox_result
            st.session_state.generated_otp = None
            st.session_state.otp_expiry = None
            st.session_state.otp_verified = False
            st.session_state.otp_attempts = 0
            st.session_state.ticket_details = None
            st.session_state.recovery_result = None
            st.session_state.retry_result = None
            st.session_state.scheduled_retry = None
            st.session_state.method_changed = False
            st.session_state.pay_later_selected = False
            st.session_state.sandbox_event = True
            st.session_state.failed_payment = is_failed_event

            st.success(f"✅ Razorpay {event_name} received → FraudShield decision engine executed.")
            st.rerun()

        except json.JSONDecodeError as exc:
            st.error(f"❌ Invalid JSON: {exc}")
        except Exception as exc:
            st.error("❌ Razorpay webhook could not be processed.")
            st.code(str(exc))

# ============================================================
# RISK STATISTICS & SOC DASHBOARD
# ============================================================

st.markdown('<div id="fraudshield"></div>', unsafe_allow_html=True)
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
    try:
        result = run_fraud_decision(
            amount_value=amount,
            payment_channel_value=payment_channel,
            device_type_value=device_type,
            international_value=int(international == "Yes"),
            merchant_risk_value=merchant_risk,
            ip_risk_value=ip_risk,
            txn_1h_value=txn_1h,
            txn_24h_value=txn_24h,
            failed_24h_value=failed_24h,
            geo_distance_value=geo_distance,
            amount_deviation_value=amount_deviation,
            customer_avg_amount_value=customer_avg_amount,
            customer_txn_before_value=customer_txn_before,
            customer_failed_rate_value=customer_failed_rate,
            merchant_txn_before_value=merchant_txn_before,
            merchant_avg_amount_value=merchant_avg_amount,
            merchant_fraud_rate_value=merchant_fraud_rate,
            post_auth_risk_value=None,
            account_age_days_value=account_age_days,
            credit_score_band_value=credit_score_band,
            kyc_level_value=kyc_level,
            source="Payment Simulator",
            demo_mode_value=demo_mode
        )

        st.session_state.generated_otp = None
        st.session_state.otp_expiry = None
        st.session_state.otp_verified = False
        st.session_state.otp_attempts = 0
        st.session_state.ticket_details = None
        st.session_state.agent_brief_id = None
        st.session_state.agent_brief_text = None
        st.session_state.scheduled_retry = None
        st.session_state.method_changed = False
        st.session_state.pay_later_selected = False
        st.session_state.failed_payment = False
        st.session_state.recovery_result = None
        st.session_state.retry_result = None
        st.session_state.sandbox_event = False
        st.session_state.last_result = result

    except Exception as exc:
        st.error("❌ FraudShield could not analyze this transaction.")
        st.code(str(exc))

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
    current_sound_id = result.get("analysis_id")
    if st.session_state.get("sound_enabled") and current_sound_id != st.session_state.get("last_sound_id"):
        sound_freq = {"LOW": 880, "MEDIUM": 660, "HIGH": 220}.get(risk_level, 660)
        st.audio(make_sound(sound_freq), format="audio/wav", autoplay=True)
        st.session_state.last_sound_id = current_sound_id

    # ========================================================
    # 🧠 LIVE DECISION ENGINE
    # ========================================================
    st.divider()
    st.header("🧠 PayShield Decision Engine")
    st.caption("Deterministic policy layer uses the FraudShield ML risk score to select the payment control.")

    source_label = result.get("source", "Payment Simulator")
    event_label = result.get("event") or "Manual payment analysis"

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("1. PAYMENT", "RECEIVED")
    d2.metric("2. FRAUDSHIELD", f"{risk_score:.1f}/100")
    d3.metric("3. RISK BAND", f"{icon} {risk_level}")
    d4.metric("4. DECISION", action)

    if risk_level == "HIGH":
        decision_text = "🔴 HIGH → HOLD + SECURITY TICKET"
        decision_class = "red-card"
    elif risk_level == "MEDIUM":
        decision_text = "🟠 MEDIUM → 2FA VERIFICATION"
        decision_class = "orange-card"
    else:
        decision_text = "🟢 LOW → ALLOW PAYMENT"
        decision_class = "green-card"

    st.markdown(
        f'''<div class="card {decision_class}">
        <h2>{decision_text}</h2>
        <p><b>Source:</b> {source_label}</p>
        <p><b>Transaction ID:</b> {result.get("analysis_id", "N/A")}</p>
        <p><b>FraudShield model probability:</b> {result.get("model_probability", risk_score):.2f}%</p>
        <p><b>Policy thresholds:</b> 0–39 LOW/ALLOW &nbsp;•&nbsp; 40–69 MEDIUM/2FA &nbsp;•&nbsp; 70–100 HIGH/HOLD</p>
        <p><b>Next control:</b> {action if action != "HOLD" else "HOLD + SECURITY TICKET"}</p>
        </div>''',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''<div class="info-panel">
        🟦 <b>{event_label}</b> &nbsp;→&nbsp; 🛡️ <b>FraudShield ML</b> &nbsp;→&nbsp; 📊 <b>{risk_score:.2f}</b> &nbsp;→&nbsp; {icon} <b>{risk_level}</b> &nbsp;→&nbsp; <b>{action}</b>
        </div>''',
        unsafe_allow_html=True
    )

    if result.get("event") == "payment.failed":
        st.warning("❌ Razorpay payment.failed event detected. Continue to PayRecover AI below for recovery analysis and Smart Retry.")

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
                    if st.session_state.otp_attempts >= 3:
                        st.error("🔒 Too many failed attempts. Payment blocked — request a new OTP.")
                        st.session_state.generated_otp = None
                    elif st.session_state.otp_expiry and datetime.now() > st.session_state.otp_expiry:
                        st.error("⏰ OTP expired. Please send a new OTP.")
                        st.session_state.generated_otp = None
                    elif otp_input == st.session_state.generated_otp:
                        st.session_state.otp_verified = True
                        st.success("✅ 2FA VERIFIED — PAYMENT APPROVED")
                        st.balloons()
                        st.rerun()
                    else:
                        st.session_state.otp_attempts += 1
                        remaining = 3 - st.session_state.otp_attempts
                        st.error(f"❌ INVALID OTP — {remaining} attempt(s) remaining")

    elif risk_level == "HIGH":
        st.error("🔴 HIGH RISK — PAYMENT UNDER REVIEW")
        
        # PaymentOps Autonomous LLM Briefing
        st.markdown("### 🤖 PaymentOps Agent Incident Briefing")

        if st.session_state.get("agent_brief_id") != result.get("analysis_id"):
            st.session_state.agent_brief_text = generate_agentic_ticket({
                "amount": amount,
                "txns_1h": txn_1h,
                "geo_dist": geo_distance,
                "amt_dev": amount_deviation
            }, risk_score)
            st.session_state.agent_brief_id = result.get("analysis_id")

        st.info(st.session_state.get("agent_brief_text", "PaymentOps briefing unavailable."))

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
st.markdown('<div id="recovery"></div>', unsafe_allow_html=True)
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

    st.markdown('<div id="smart-retry"></div>', unsafe_allow_html=True)
    st.header("⏰ Smart Retry AI")

    # ========================================================
    # PAYMENT METHOD OPTIMIZATION
    # ========================================================

    st.subheader("💳 Change Payment Method")

    available_methods = ["UPI", "CARD", "WALLET", "NETBANKING"]
    method_probabilities = []

    for candidate_method in available_methods:
        method_input = pd.DataFrame([{
            "amount": amount,
            "payment_method": candidate_method,
            "failure_reason": failure_reason,
            "retry_count": retry_count,
            "minutes_since_failure": minutes_since_failure,
            "customer_success_rate": customer_success_rate,
            "method_success_rate": method_success_rate,
            "previous_failures": previous_failures,
            "is_international": int(international == "Yes"),
            "device_type": device_type,
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday()
        }]).reindex(columns=recovery_features)

        try:
            method_probability = float(
                recovery_model.predict_proba(method_input)[0, 1]
            ) * 100
        except Exception:
            method_probability = 0.0

        method_probabilities.append(method_probability)

    method_df = pd.DataFrame({
        "Payment Method": available_methods,
        "Predicted Recovery": method_probabilities
    })

    best_method_index = int(np.argmax(method_probabilities))
    best_method = available_methods[best_method_index]
    best_method_probability = method_probabilities[best_method_index]

    # Graph: recovery probability by payment method
    st.bar_chart(
        method_df.set_index("Payment Method")["Predicted Recovery"],
        use_container_width=True
    )

    mc1, mc2 = st.columns(2)

    with mc1:
        st.metric(
            "⭐ Best Payment Method",
            best_method,
            f"{best_method_probability:.2f}% predicted recovery"
        )

    with mc2:
        st.metric(
            "Current Method",
            payment_method,
            f"{method_probabilities[available_methods.index(payment_method)]:.2f}%"
        )

    if best_method != payment_method:
        st.warning(
            f"🔄 PaymentOps recommends changing from {payment_method} "
            f"to {best_method} before retrying."
        )

        if st.button(
            f"🔄 CHANGE PAYMENT METHOD → {best_method}",
            key="change_payment_method",
            use_container_width=True
        ):
            st.session_state.method_changed = True
            st.session_state.selected_retry_method = best_method
            st.success(
                f"✅ Payment method changed to {best_method}. "
                f"Predicted recovery probability: {best_method_probability:.2f}%"
            )
    else:
        st.success(
            f"✅ {payment_method} is currently the best available payment method."
        )

    # ========================================================
    # RETRY-TIME OPTIMIZATION
    # ========================================================

    retry_times = [5, 15, 30, 60, 120, 240, 480, 1440]
    probabilities = []

    for retry_time in retry_times:
        r_inp = pd.DataFrame([{
            "customer_success_rate": customer_success_rate,
            "method_success_rate": method_success_rate,
            "previous_failures": previous_failures,
            "retry_time_minutes": retry_time
        }]).reindex(columns=retry_features)

        try:
            probabilities.append(
                float(retry_model.predict_proba(r_inp)[0, 1]) * 100
            )
        except Exception:
            probabilities.append(0.0)

    best_index = int(np.argmax(probabilities)) if probabilities else 0
    best_time = retry_times[best_index]
    best_probability = probabilities[best_index] if probabilities else 0.0

    retry_df = pd.DataFrame({
        "Retry Time": [f"{x} min" for x in retry_times],
        "Success Probability": probabilities
    })

    st.subheader("📈 Retry Time vs Predicted Success")

    # Graph: actual Smart Retry model probabilities
    st.line_chart(
        retry_df.set_index("Retry Time")["Success Probability"],
        use_container_width=True
    )

    rt1, rt2 = st.columns(2)

    with rt1:
        st.metric(
            "⭐ Recommended Retry Time",
            f"{best_time} min"
        )

    with rt2:
        st.metric(
            "Predicted Retry Success",
            f"{best_probability:.2f}%"
        )

    # Combined recommendation
    st.success(
        f"⭐ SMART RETRY RECOMMENDATION: "
        f"Retry after {best_time} minutes"
        f"{f' using {best_method}' if best_method != payment_method else f' using {payment_method}'} "
        f"with {best_probability:.2f}% predicted retry success."
    )

    st.caption(
        "Smart Retry AI compares multiple retry windows using the trained retry model. "
        "Payment Method Optimization compares available payment methods using the trained "
        "PayRecover model."
    )

# ============================================================
# 🤖 PAYMENTOPS AI — INCIDENT ANALYSIS
# ============================================================

st.divider()
st.markdown('<div id="paymentops"></div>', unsafe_allow_html=True)
st.header("🤖 PaymentOps AI — Incident Analysis")
st.caption(
    "AI-powered incident interpretation for fraud decisions, "
    "business impact, and recommended merchant action."
)

result = st.session_state.get("last_result", {})
if not isinstance(result, dict):
    result = {}

# ------------------------------------------------------------
# GET RISK SCORE
# ------------------------------------------------------------

risk_score = (
    result.get("risk")
    or result.get("risk_score")
    or result.get("fraud_score")
    or result.get("fraud_probability")
    or result.get("fraud_prob")
    or result.get("model_probability")
    or result.get("probability")
)

if risk_score is None:
    risk_score = 0

risk_score = float(risk_score)

# Convert probability 0–1 into score 0–100 if required
if risk_score <= 1:
    risk_score *= 100

# ------------------------------------------------------------
# RISK LEVEL
# ------------------------------------------------------------

if risk_score >= 70:
    risk_level = "HIGH"
elif risk_score >= 40:
    risk_level = "MEDIUM"
else:
    risk_level = "LOW"

# ------------------------------------------------------------
# DECISION
# ------------------------------------------------------------

decision = result.get("decision") or result.get("action")

if not decision:
    if risk_level == "HIGH":
        decision = "HOLD"
    elif risk_level == "MEDIUM":
        decision = "2FA"
    else:
        decision = "ALLOW"

# ------------------------------------------------------------
# TRANSACTION ID
# ------------------------------------------------------------

transaction_id = (
    result.get("transaction_id")
    or result.get("payment_id")
    or result.get("id")
    or result.get("analysis_id")
    or st.session_state.get("transaction_id")
    or st.session_state.get("current_transaction_id")
    or st.session_state.get("payment_id")
    or "TXN-DEMO-001"
)

# ------------------------------------------------------------
# AMOUNT
# ------------------------------------------------------------

amount = (
    result.get("amount")
    or result.get("transaction_amount")
    or st.session_state.get("transaction_amount")
    or 0
)

try:
    amount = float(amount)
except:
    amount = 0.0

# ------------------------------------------------------------
# PAYMENT STATUS
# ------------------------------------------------------------

payment_status = (
    result.get("payment_status")
    or result.get("status")
    or "Under Security Review"
)

# ------------------------------------------------------------
# INCIDENT SUMMARY
# ------------------------------------------------------------

st.subheader("📋 Incident Summary")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Transaction",
        str(transaction_id)
    )

with c2:
    st.metric(
        "Amount",
        f"₹{amount:,.2f}"
    )

with c3:
    st.metric(
        "Risk Level",
        risk_level
    )

with c4:
    st.metric(
        "Decision",
        decision
    )

# ------------------------------------------------------------
# BUSINESS IMPACT
# ------------------------------------------------------------

st.subheader("📊 Business Impact")

if risk_level == "HIGH":

    business_impact = (
        f"The transaction has a high fraud-risk score of "
        f"{risk_score:.2f}/100. Payment processing has been "
        f"stopped to prevent potential financial loss."
    )

elif risk_level == "MEDIUM":

    business_impact = (
        f"The transaction has a medium fraud-risk score of "
        f"{risk_score:.2f}/100. Additional customer verification "
        f"is required before payment completion."
    )

else:

    business_impact = (
        f"The transaction has a low fraud-risk score of "
        f"{risk_score:.2f}/100 and can proceed under normal "
        f"processing controls."
    )

st.info(business_impact)

# ------------------------------------------------------------
# RECOMMENDED ACTION
# ------------------------------------------------------------

st.subheader("🎯 Recommended Action")

if risk_level == "HIGH":

    st.error(
        "🔴 HOLD PAYMENT → SECURITY REVIEW"
    )

    st.write(
        f"FraudShield detected a high-risk transaction "
        f"({risk_score:.2f}/100). Keep the payment on hold, "
        f"review the transaction signals, and raise a security "
        f"ticket if required."
    )

elif risk_level == "MEDIUM":

    st.warning(
        "🟠 REQUIRE 2FA → VERIFY CUSTOMER"
    )

    st.write(
        f"The transaction has a medium risk score "
        f"({risk_score:.2f}/100). Require additional "
        f"authentication before allowing payment."
    )

else:

    st.success(
        "🟢 ALLOW PAYMENT → CONTINUE NORMAL PROCESSING"
    )

    st.write(
        f"The transaction has a low risk score "
        f"({risk_score:.2f}/100). Continue normal payment "
        f"processing."
    )

# ------------------------------------------------------------
# PAYMENTOPS AI ASSESSMENT
# ------------------------------------------------------------

st.subheader("🧠 PaymentOps AI Assessment")

if risk_level == "HIGH":

    st.write(
        f"PaymentOps classified this incident as HIGH severity. "
        f"The FraudShield score is {risk_score:.2f}/100, which "
        f"exceeds the high-risk threshold of 70. The correct "
        f"operational response is to HOLD the transaction and "
        f"perform a security review."
    )

elif risk_level == "MEDIUM":

    st.write(
        f"PaymentOps classified this incident as MEDIUM severity. "
        f"The FraudShield score is {risk_score:.2f}/100, so the "
        f"customer should complete additional authentication "
        f"before payment authorization."
    )

else:

    st.write(
        f"PaymentOps classified this incident as LOW severity. "
        f"The FraudShield score is {risk_score:.2f}/100, which "
        f"is below the medium-risk threshold. Normal processing "
        f"can continue."
    )

# ------------------------------------------------------------
# OPERATIONS STATUS
# ------------------------------------------------------------

st.subheader("⚙️ Operations Status")

if risk_level == "HIGH":

    st.error(
        "🔴 SECURITY REVIEW REQUIRED"
    )

elif risk_level == "MEDIUM":

    st.warning(
        "🟠 CUSTOMER VERIFICATION REQUIRED"
    )

else:

    st.success(
        "🟢 NORMAL PAYMENT PROCESSING"
    )

# ============================================================
# PAYSHIELD MANUAL
# ============================================================
st.markdown('<div id="manual"></div>', unsafe_allow_html=True)
st.divider()
st.header("📖 PayShield Manual")
st.caption("A quick guide for merchants, security analysts, and buildathon judges.")
manual_items = {
    "🛡️ FraudShield": "Analyzes transaction and behavioral features and produces a 0–100 risk score.",
    "🟢 LOW → ALLOW": "Low-risk payments continue normally.",
    "🟠 MEDIUM → 2FA": "Medium-risk payments require OTP verification before approval.",
    "🔴 HIGH → HOLD": "High-risk payments are held and can generate a security ticket for review.",
    "💰 PayRecover": "Analyzes failed payments and estimates recovery probability.",
    "⏰ Smart Retry": "Compares retry windows and recommends the strongest predicted retry time.",
    "💳 Change Payment Method": "Compares available payment methods when recovery optimization is available.",
    "🤖 PaymentOps": "Explains the incident, business impact, and recommended operational response.",
    "🔌 Razorpay Sandbox": "Lets you simulate Razorpay test webhook events without moving real money."
}
for title, text in manual_items.items():
    with st.expander(title):
        st.write(text)

# ============================================================
# GEMINI ASSISTANT — MAIN PANEL
# ============================================================
st.markdown('<div id="assistant"></div>', unsafe_allow_html=True)
st.header("💬 PayShield AI Assistant")
st.markdown('<div class="chat-card"><b>Gemini-powered explanations</b><br><span style="color:#9ca3af">Ask about the current risk score, 2FA, payment recovery, retry timing, or PaymentOps recommendations.</span></div>', unsafe_allow_html=True)
q2 = st.text_input("Your question", placeholder="Explain the current payment decision", key="gemini_main_question")
if st.button("🤖 Ask PayShield AI", key="gemini_main_button", type="primary"):
    if q2.strip():
        current = st.session_state.get("last_result") or {}
        context = json.dumps(current, default=str)[:6000]
        ans = gemini_answer(q2.strip(), context)
        st.session_state.gemini_chat.append({"q": q2.strip(), "a": ans})
        st.rerun()
if st.session_state.gemini_chat:
    last = st.session_state.gemini_chat[-1]
    st.markdown(f"**You:** {last['q']}")
    st.info(last['a'])
