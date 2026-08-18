"""UPIShield Streamlit dashboard."""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]


def api_url():
    value = os.getenv("UPISHIELD_API_URL")
    if not value:
        try:
            value = st.secrets.get("UPISHIELD_API_URL")
        except FileNotFoundError:
            value = None
    return (value or "http://127.0.0.1:8000").rstrip("/")


API_URL = api_url()
st.set_page_config(page_title="UPIShield", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.stApp{background:#f5f7fb;color:#132238}[data-testid="stSidebar"]{background:linear-gradient(180deg,#071b33,#0b3152)}
[data-testid="stSidebar"] *{color:#f5fbff!important}.block-container{padding-top:1.7rem;padding-bottom:3rem;max-width:1320px}
.hero{padding:2rem 2.2rem;border-radius:22px;color:white;background:linear-gradient(120deg,#082847 0%,#0b6e75 62%,#13a37f 100%);box-shadow:0 16px 38px rgba(8,40,71,.18);margin-bottom:1.4rem}
.hero h1{font-size:2.6rem;margin:0 0 .45rem;letter-spacing:-.04em}.hero p{font-size:1.05rem;margin:0;opacity:.88;max-width:760px}.eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;opacity:.75}
.metric-card{background:white;border:1px solid #e2e8f0;border-radius:16px;padding:1.1rem 1.25rem;box-shadow:0 5px 18px rgba(15,35,60,.05);min-height:112px}.metric-label{color:#64748b;font-size:.82rem;font-weight:650;text-transform:uppercase;letter-spacing:.04em}.metric-value{color:#0f2740;font-size:1.75rem;font-weight:750;margin-top:.35rem}
.risk-box{border-radius:20px;padding:1.6rem;color:white;text-align:center;margin:.5rem 0 1rem}.risk-low{background:linear-gradient(130deg,#087f5b,#20a879)}.risk-medium{background:linear-gradient(130deg,#b96b00,#f0a11c)}.risk-high{background:linear-gradient(130deg,#9f1239,#e03b52)}.risk-score{font-size:3rem;font-weight:800;line-height:1;margin:.4rem 0}
.reason{background:#f8fafc;border-left:4px solid #0f8b8d;padding:.72rem .9rem;border-radius:8px;margin:.5rem 0;color:#263a50}div[data-testid="stForm"]{background:white;border:1px solid #dfe7ef;border-radius:18px;padding:1.2rem}
.stButton>button,.stFormSubmitButton>button{border:0;border-radius:10px;font-weight:700;background:linear-gradient(100deg,#0b6e75,#10a37f);color:white;min-height:44px}.status-ok{color:#2dd4a4;font-weight:700}.status-bad{color:#fb7185;font-weight:700}#MainMenu,footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_metrics():
    with open(ROOT / "reports" / "metrics.json", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data(ttl=30)
def check_api():
    try:
        response = requests.get(f"{API_URL}/health", timeout=8)
        response.raise_for_status()
        return bool(response.json().get("model_loaded"))
    except requests.RequestException:
        return False


@st.cache_data
def load_demo_scores():
    path = ROOT / "data" / "upishield.db"
    if not path.exists():
        return pd.DataFrame()
    with sqlite3.connect(path) as connection:
        frame = pd.read_sql("SELECT * FROM risk_scores", connection)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame["risk_level"] = pd.cut(frame.risk_score, [-1, 35, 65, 101], labels=["LOW", "MEDIUM", "HIGH"])
    return frame


def metric_cards(items):
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items):
        column.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)


metrics = load_metrics()
dataset = metrics["dataset"]
scores = load_demo_scores()

with st.sidebar:
    st.markdown("## 🛡️ UPIShield")
    st.caption("Behavioral Risk Intelligence")
    page = st.radio("Navigation", ["Transaction scoring", "Risk overview", "Model performance"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**System status**")
    online = check_api()
    state = '<span class="status-ok">● API & model online</span>' if online else '<span class="status-bad">● API unavailable</span>'
    st.markdown(state, unsafe_allow_html=True)
    st.caption(API_URL)
    if st.button("Refresh status", width="stretch"):
        check_api.clear()
        st.rerun()
    st.markdown("---")
    st.caption("Synthetic UPI-like data generated solely for educational purposes. Not a production fraud-decision system.")

st.markdown("""
<div class="hero"><div class="eyebrow">Behavioral anomaly detection</div><h1>UPIShield</h1>
<p>Understand how unusual a payment is compared with prior user behavior—using supervised ML, anomaly detection and transparent risk rules.</p></div>
""", unsafe_allow_html=True)

if page == "Transaction scoring":
    metric_cards([("Training transactions", f"{dataset['transactions']:,}"), ("Behavioral users", f"{dataset['users']:,}"),
                  ("Observed fraud rate", f"{dataset['fraud_percentage']:.2f}%"),
                  ("Selected model", metrics["selected_supervised_model"].replace("_", " ").title())])
    st.markdown("### Evaluate a transaction")
    st.caption("Enter transaction context. UPIShield compares it with available prior behavior and returns an explainable score.")
    with st.form("score_transaction"):
        a, b, c = st.columns(3)
        user = a.text_input("User ID", "U0102", help="Sender identifier used to retrieve prior behavior")
        receiver = b.text_input("Receiver ID", "R0911")
        amount = c.number_input("Amount (₹)", min_value=1.0, value=27500.0, step=100.0)
        device = a.text_input("Device ID", "DEV120")
        city = b.selectbox("City", ["Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Pune", "Chennai", "Kolkata", "Jaipur"])
        transaction_type = c.selectbox("Transaction type", ["P2P", "P2M", "BillPay", "Recharge"])
        category = a.selectbox("Merchant category", ["Other", "Groceries", "Food", "Travel", "Utilities", "Shopping", "Healthcare"])
        device_type = b.selectbox("Device type", ["Android", "iOS"])
        submitted = st.form_submit_button("Analyse transaction →", width="stretch")

    if submitted:
        payload = {"user_id": user, "receiver_id": receiver, "amount": amount, "timestamp": datetime.now().isoformat(),
            "sender_bank": "Bank_A", "receiver_bank": "Bank_B", "device_id": device, "device_type": device_type,
            "city": city, "state": "India", "transaction_type": transaction_type, "merchant_category": category}
        try:
            with st.spinner("Analysing behavioral signals..."):
                response = requests.post(f"{API_URL}/score", json=payload, timeout=30)
                response.raise_for_status()
            st.session_state["last_result"] = response.json()
        except requests.RequestException as exc:
            st.error(f"The scoring API could not complete this request. Check the API status and try again.\n\n{exc}")

    if result := st.session_state.get("last_result"):
        level = result["risk_level"]
        left, right = st.columns([1, 1.45])
        left.markdown(f'<div class="risk-box risk-{level.lower()}"><div class="eyebrow">Final risk assessment</div><div class="risk-score">{result["risk_score"]}</div><div>{level} RISK · OUT OF 100</div></div>', unsafe_allow_html=True)
        with left:
            st.progress(min(float(result["risk_score"]) / 100, 1.0))
        with right:
            st.markdown("#### Score composition")
            metric_cards([("Fraud probability", f"{result['fraud_probability']:.1%}"), ("Anomaly score", f"{result['anomaly_score']:.1f}"), ("Rule score", f"{result['rule_score']:.1f}")])
            st.markdown("#### Why this score?")
            for reason in result["reasons"]:
                st.markdown(f'<div class="reason">✓ {reason}</div>', unsafe_allow_html=True)

elif page == "Risk overview":
    metric_cards([("Transactions", f"{dataset['transactions']:,}"), ("Users", f"{dataset['users']:,}"),
                  ("Fraud records", f"{dataset['fraud_count']:,}"), ("Test records", f"{dataset['test_size']:,}")])
    if scores.empty:
        st.info("Detailed transaction charts appear after running `python scripts/run_pipeline.py` where persistent local storage is available.")
    else:
        metric_cards([("Scored demo rows", f"{len(scores):,}"), ("High risk", f"{(scores.risk_level == 'HIGH').sum():,}"),
                      ("Average risk", f"{scores.risk_score.mean():.1f}"), ("Maximum risk", f"{scores.risk_score.max():.1f}")])
        c1, c2 = st.columns([1.6, 1])
        with c1:
            st.markdown("#### Risk score over time")
            st.line_chart(scores.set_index("timestamp")["risk_score"], color="#0b8f83")
        with c2:
            st.markdown("#### Risk distribution")
            st.bar_chart(scores.risk_level.value_counts(), color="#0b8f83")
        st.markdown("#### Recent highest-risk transactions")
        st.dataframe(scores.nlargest(20, "risk_score"), width="stretch", hide_index=True)

else:
    metric_cards([("Temporal train", f"{dataset['train_size']:,}"), ("Validation", f"{dataset['validation_size']:,}"),
                  ("Held-out test", f"{dataset['test_size']:,}"), ("Hybrid F1", f"{metrics['hybrid']['f1']:.3f}")])
    rows = []
    for key, label in [("rule_baseline", "Rule baseline"), ("isolation_forest", "Isolation Forest"),
                       ("supervised", "Random Forest"), ("hybrid", "Hybrid engine")]:
        rows.append({"Model": label, **{name.upper().replace("_", " "): metrics[key][name]
            for name in ["precision", "recall", "f1", "pr_auc", "roc_auc", "false_positive_rate"]}})
    st.markdown("### Held-out test performance")
    st.dataframe(pd.DataFrame(rows).set_index("Model"), width="stretch")
    c1, c2 = st.columns(2)
    for column, filename, title in [(c1, "hybrid_precision_recall.png", "Precision–recall curve"),
                                    (c2, "feature_importance.png", "Selected-model feature importance")]:
        with column:
            st.markdown(f"#### {title}")
            st.image(ROOT / "reports" / "figures" / filename, width="stretch")
    st.info("Historical features use prior transactions only. Validation selects models and thresholds; test data is reserved for final evaluation.")

st.markdown("---")
st.caption("UPIShield · Educational fintech ML portfolio project · Synthetic data only · No affiliation with NPCI, banks or payment applications")
