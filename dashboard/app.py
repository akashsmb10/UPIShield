import os, sqlite3
from pathlib import Path
import pandas as pd
import requests
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
API_URL=os.getenv("UPISHIELD_API_URL","http://127.0.0.1:8000").rstrip("/")
st.set_page_config(page_title="UPIShield",layout="wide")
st.title("UPIShield — Behavioral Transaction Risk")
db=ROOT/"data"/"upishield.db"
if db.exists():
    with sqlite3.connect(db) as conn: scores=pd.read_sql("SELECT * FROM risk_scores",conn)
    scores["timestamp"]=pd.to_datetime(scores.timestamp); scores["risk_level"]=pd.cut(scores.risk_score,[-1,35,65,101],labels=["LOW","MEDIUM","HIGH"])
    cols=st.columns(4); cols[0].metric("Transactions",len(scores)); cols[1].metric("High risk",int((scores.risk_level=="HIGH").sum())); cols[2].metric("Fraud rate",f"{scores.is_fraud.mean():.2%}"); cols[3].metric("Average risk",f"{scores.risk_score.mean():.1f}")
    st.line_chart(scores.set_index("timestamp").risk_score); st.bar_chart(scores.risk_level.value_counts()); st.dataframe(scores.nlargest(20,"risk_score"),use_container_width=True)
st.subheader("Score a transaction")
with st.form("score"):
    c1,c2,c3=st.columns(3); user=c1.text_input("User ID","U0102"); receiver=c2.text_input("Receiver ID","R0911"); amount=c3.number_input("Amount",min_value=1.0,value=27500.0)
    device=c1.text_input("Device ID","DEV120"); city=c2.text_input("City","Hyderabad"); tx_type=c3.selectbox("Transaction type",["P2P","P2M","BillPay","Recharge"]); submitted=st.form_submit_button("Score")
if submitted:
    payload={"user_id":user,"receiver_id":receiver,"amount":amount,"timestamp":pd.Timestamp.now().isoformat(),"sender_bank":"Bank_A","receiver_bank":"Bank_B","device_id":device,"device_type":"Android","city":city,"state":"Telangana","transaction_type":tx_type,"merchant_category":"Other"}
    try:
        response=requests.post(f"{API_URL}/score",json=payload,timeout=15); response.raise_for_status(); result=response.json()
        st.metric("Risk score",f"{result['risk_score']}/100"); st.subheader(result["risk_level"]); st.write(f"Anomaly: {result['anomaly_score']} · Fraud probability: {result['fraud_probability']:.1%}"); st.write(result["reasons"])
    except requests.RequestException as exc: st.error(f"API unavailable at {API_URL}: {exc}")
