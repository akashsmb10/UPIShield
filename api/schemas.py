from datetime import datetime
from pydantic import BaseModel, Field

class TransactionRequest(BaseModel):
    user_id: str = Field(min_length=1)
    receiver_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    timestamp: datetime
    sender_bank: str
    receiver_bank: str
    device_id: str
    device_type: str
    city: str
    state: str
    transaction_type: str
    merchant_category: str

class ScoreResponse(BaseModel):
    risk_score: float
    risk_level: str
    anomaly_score: float
    fraud_probability: float
    rule_score: float
    reasons: list[str]
