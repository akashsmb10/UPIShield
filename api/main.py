from contextlib import asynccontextmanager
import joblib, numpy as np, pandas as pd
from fastapi import FastAPI, HTTPException
from src.config import ARTIFACT_DIR, PROCESSED_PATH
from src.features import build_features, model_matrix
from src.risk_engine import rule_scores, combine_scores, risk_level, explain
from .schemas import TransactionRequest, ScoreResponse

STATE = {}

def load_assets():
    path=ARTIFACT_DIR/"risk_bundle.joblib"
    if not path.exists(): return
    STATE["bundle"]=joblib.load(path)
    STATE["history"]=pd.read_csv(PROCESSED_PATH,parse_dates=["timestamp"])

@asynccontextmanager
async def lifespan(app):
    load_assets(); yield

app=FastAPI(title="UPIShield",version="1.0.0",lifespan=lifespan)

@app.get("/health")
def health(): return {"status":"ok","model_loaded":"bundle" in STATE}

@app.get("/model-info")
def model_info():
    return STATE.get("bundle",{}).get("metadata",{"status":"run python scripts/run_pipeline.py first"})

@app.post("/score",response_model=ScoreResponse)
def score(req: TransactionRequest):
    if "bundle" not in STATE: raise HTTPException(503,"Model artifacts unavailable; run the pipeline")
    d=req.model_dump(); d["transaction_id"]="API_TXN"; d["is_fraud"]=0; d["fraud_scenario"]="none"; d["transaction_status"]="SUCCESS"
    history=STATE["history"]; user=history[(history.user_id==req.user_id)&(history.timestamp<pd.Timestamp(req.timestamp))].tail(1000)
    combined=pd.concat([user,pd.DataFrame([d])],ignore_index=True); row=build_features(combined).iloc[-1]
    X=model_matrix(pd.DataFrame([row])); b=STATE["bundle"]
    prob=float(b["model"].predict_proba(X)[:,1][0]); raw=float(-b["isolation_forest"].score_samples(b["scaler"].transform(X))[0])
    anomaly=float(np.clip((raw-b["anomaly_low"])/(b["anomaly_high"]-b["anomaly_low"])*100,0,100)); rule=float(rule_scores(pd.DataFrame([row]))[0])
    risk=float(combine_scores([prob],[anomaly],[rule])[0]); thresholds=b["metadata"]["risk_thresholds"]
    return ScoreResponse(risk_score=round(risk,2),risk_level=risk_level(risk,thresholds["medium"],thresholds["high"]),anomaly_score=round(anomaly,2),fraud_probability=round(prob,4),rule_score=round(rule,2),reasons=explain(row))
