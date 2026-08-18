import numpy as np

def rule_scores(df):
    score = (np.minimum(df.amount_vs_user_avg.clip(lower=1), 8)-1)*5
    score += np.minimum(df.amount_zscore_user.clip(lower=0), 8)*4
    score += df.is_new_receiver*12 + df.is_new_device*12 + df.is_night*8 + df.city_changed*10
    score += np.minimum(df.txn_count_last_10min, 5)*4 + np.minimum(df.amount_sum_last_1hour / 10000, 5)*3
    return np.clip(score, 0, 100)

def combine_scores(fraud_probability, anomaly_score, rule_score):
    return np.clip(.5*np.asarray(fraud_probability)*100 + .3*np.asarray(anomaly_score) + .2*np.asarray(rule_score), 0, 100)

def risk_level(score, medium=35, high=65):
    return "HIGH" if score >= high else "MEDIUM" if score >= medium else "LOW"

def explain(row):
    reasons = []
    if row.get("amount_vs_user_avg", 1) >= 3: reasons.append(f"Transaction amount is {row['amount_vs_user_avg']:.1f}x the user's historical average")
    if row.get("is_new_receiver", 0): reasons.append("First payment to this receiver")
    if row.get("is_new_device", 0): reasons.append("First transaction from this device")
    if row.get("is_night", 0): reasons.append("Transaction occurred during unusual late-night hours")
    if row.get("city_changed", 0): reasons.append("Current city differs from previous transaction activity")
    if row.get("txn_count_last_10min", 0) >= 3: reasons.append(f"{int(row['txn_count_last_10min'])} prior transactions occurred within the last 10 minutes")
    return reasons or ["No strong behavioral risk indicator was triggered"]
