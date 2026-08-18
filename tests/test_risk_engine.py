import pandas as pd
from src.risk_engine import rule_scores,combine_scores,risk_level,explain
def row(**kw):
    d=dict(amount_vs_user_avg=1,amount_zscore_user=0,is_new_receiver=0,is_new_device=0,is_night=0,city_changed=0,txn_count_last_10min=0,amount_sum_last_1hour=0); d.update(kw); return d
def test_bounds(): assert 0<=combine_scores([2],[200],[200])[0]<=100
def test_levels(): assert [risk_level(x) for x in [1,40,80]]==["LOW","MEDIUM","HIGH"]
def test_suspicious_higher(): assert rule_scores(pd.DataFrame([row(amount_vs_user_avg=8,is_new_device=1)]))[0]>rule_scores(pd.DataFrame([row()]))[0]
def test_reasons_supported(): assert "First payment to this receiver" in explain(row(is_new_receiver=1))
