from fastapi.testclient import TestClient
from api.main import app

def payload(): return {"user_id":"UNKNOWN","receiver_id":"R9999","amount":2000,"timestamp":"2026-04-01T02:40:00","sender_bank":"Bank_A","receiver_bank":"Bank_B","device_id":"NEW","device_type":"Android","city":"Hyderabad","state":"Telangana","transaction_type":"P2P","merchant_category":"Other"}
def test_health():
    with TestClient(app) as c: assert c.get("/health").status_code==200
def test_model_info():
    with TestClient(app) as c: assert c.get("/model-info").status_code==200
def test_valid_score():
    with TestClient(app) as c: assert c.post("/score",json=payload()).status_code==200
def test_unknown_user_does_not_crash():
    with TestClient(app) as c: assert c.post("/score",json=payload()).json()["risk_level"] in ["LOW","MEDIUM","HIGH"]
def test_known_user_with_history_does_not_crash():
    p=payload(); p["user_id"]="U0102"; p["timestamp"]="2026-08-19T02:20:00"
    with TestClient(app) as c: assert c.post("/score",json=p).status_code==200
def test_zero_rejected():
    p=payload();p["amount"]=0
    with TestClient(app) as c: assert c.post("/score",json=p).status_code==422
def test_negative_rejected():
    p=payload();p["amount"]=-1
    with TestClient(app) as c: assert c.post("/score",json=p).status_code==422
def test_malformed_rejected():
    with TestClient(app) as c: assert c.post("/score",json={}).status_code==422
