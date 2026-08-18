import pandas as pd
from src.features import build_features, temporal_split, model_matrix

def base():
    return pd.DataFrame([{"transaction_id":f"T{i}","timestamp":f"2026-01-01 00:0{i}:00","user_id":"U1","receiver_id":r,"amount":a,"device_id":d,"city":c,"is_fraud":0,"fraud_scenario":"none"} for i,(a,r,d,c) in enumerate([(100,"R1","D1","A"),(200,"R1","D1","A"),(300,"R2","D2","B")])])
def test_first_has_no_history(): assert build_features(base()).iloc[0].previous_user_txn_count==0
def test_prior_average(): assert build_features(base()).iloc[2].previous_user_avg_amount==150
def test_new_entities():
    f=build_features(base()); assert f.iloc[0].is_new_receiver==1 and f.iloc[1].is_new_receiver==0 and f.iloc[2].is_new_device==1
def test_velocity(): assert build_features(base()).iloc[2].txn_count_last_10min==2
def test_future_does_not_change_past():
    a=build_features(base().iloc[:2]); b=build_features(base()); assert a.iloc[1].previous_user_avg_amount==b.iloc[1].previous_user_avg_amount
def test_no_target_features(): assert "is_fraud" not in model_matrix(build_features(base())).columns
def test_temporal_split():
    a,b,c=temporal_split(build_features(pd.concat([base()]*10,ignore_index=True))); assert len(a)+len(b)+len(c)==30
