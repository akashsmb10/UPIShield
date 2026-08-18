"""Leakage-safe behavioral features; every historical value is shifted/prior-only."""
from collections import defaultdict, deque
import numpy as np
import pandas as pd

from .config import MODEL_FEATURES

def build_features(transactions):
    df = transactions.copy().sort_values("timestamp", kind="stable").reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df.timestamp)
    history, devices, receivers, last_city, windows = defaultdict(list), defaultdict(lambda: defaultdict(int)), defaultdict(lambda: defaultdict(list)), {}, defaultdict(deque)
    records = []
    for row in df.itertuples(index=False):
        amounts = history[row.user_id]; prior_n = len(amounts)
        avg = float(np.mean(amounts)) if amounts else 0.0
        median = float(np.median(amounts)) if amounts else 0.0
        std = float(np.std(amounts)) if len(amounts) > 1 else 0.0
        pair = receivers[row.user_id][row.receiver_id]
        q = windows[row.user_id]
        while q and (row.timestamp - q[0][0]).total_seconds() > 86400: q.popleft()
        c10 = sum(t >= row.timestamp - pd.Timedelta(minutes=10) for t, _ in q)
        c1h = sum(t >= row.timestamp - pd.Timedelta(hours=1) for t, _ in q)
        s1h = sum(a for t, a in q if t >= row.timestamp - pd.Timedelta(hours=1))
        s24 = sum(a for _, a in q)
        prev_time = q[-1][0] if q else None
        rec = {"log_amount": np.log1p(row.amount), "hour": row.timestamp.hour, "day_of_week": row.timestamp.dayofweek,
            "is_weekend": int(row.timestamp.dayofweek >= 5), "is_night": int(row.timestamp.hour < 6),
            "previous_user_txn_count": prior_n, "previous_user_avg_amount": avg, "previous_user_median_amount": median,
            "previous_user_amount_std": std, "amount_vs_user_avg": row.amount / avg if avg else 1.0,
            "amount_zscore_user": (row.amount - avg) / std if std > 1 else 0.0,
            "minutes_since_previous_transaction": (row.timestamp-prev_time).total_seconds()/60 if prev_time else 10080.0,
            "device_seen_before": int(devices[row.user_id][row.device_id] > 0), "is_new_device": int(devices[row.user_id][row.device_id] == 0),
            "previous_device_txn_count": devices[row.user_id][row.device_id], "receiver_seen_before_by_user": int(bool(pair)),
            "is_new_receiver": int(not pair), "previous_transactions_to_receiver": len(pair),
            "previous_amount_to_receiver_avg": float(np.mean(pair)) if pair else 0.0,
            "previous_city": last_city.get(row.user_id, "UNKNOWN"), "city_changed": int(row.user_id in last_city and last_city[row.user_id] != row.city),
            "txn_count_last_10min": c10, "txn_count_last_1hour": c1h, "amount_sum_last_1hour": s1h, "amount_sum_last_24h": s24}
        records.append(rec)
        amounts.append(row.amount); devices[row.user_id][row.device_id] += 1; pair.append(row.amount); last_city[row.user_id] = row.city; q.append((row.timestamp, row.amount))
    return pd.concat([df, pd.DataFrame(records)], axis=1)

def model_matrix(feature_df):
    assert not {"is_fraud", "fraud_scenario", "transaction_id"}.intersection(MODEL_FEATURES)
    return feature_df[MODEL_FEATURES].replace([np.inf, -np.inf], 0).fillna(0)

def temporal_split(df):
    n = len(df); a, b = int(n*.70), int(n*.85)
    return df.iloc[:a].copy(), df.iloc[a:b].copy(), df.iloc[b:].copy()
