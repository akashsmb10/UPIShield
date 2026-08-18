"""Reproducible synthetic UPI-like transaction generator for education."""
import numpy as np
import pandas as pd

from .config import N_TRANSACTIONS, N_USERS, SEED

CITIES = [("Hyderabad", "Telangana"), ("Bengaluru", "Karnataka"), ("Mumbai", "Maharashtra"),
          ("Delhi", "Delhi"), ("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu"),
          ("Kolkata", "West Bengal"), ("Jaipur", "Rajasthan")]
BANKS = ["Bank_A", "Bank_B", "Bank_C", "Bank_D", "Bank_E"]
CATEGORIES = ["Groceries", "Food", "Travel", "Utilities", "Shopping", "Healthcare", "Other"]
TYPES = ["P2P", "P2M", "BillPay", "Recharge"]

def generate_transactions(n_transactions=N_TRANSACTIONS, n_users=N_USERS, seed=SEED):
    rng = np.random.default_rng(seed)
    users = np.array([f"U{i:04d}" for i in range(n_users)])
    weights = rng.pareto(1.8, n_users) + .15
    chosen = rng.choice(users, n_transactions, p=weights / weights.sum())
    start = pd.Timestamp("2026-01-01")
    timestamps = start + pd.to_timedelta(np.sort(rng.uniform(0, 90 * 86400, n_transactions)), unit="s")
    profiles = {}
    for user in users:
        city_i = int(rng.integers(len(CITIES)))
        profiles[user] = dict(median=float(rng.lognormal(6.2, .75)), city=city_i,
                             hour=int(rng.choice([8, 10, 12, 14, 18, 20, 22])),
                             devices=[f"D{user[1:]}_{j}" for j in range(1, int(rng.integers(2, 4)))],
                             receivers=[f"R{int(x):04d}" for x in rng.choice(4000, int(rng.integers(3, 12)), replace=False)])
    rows = []
    recent_fraud = {}
    for i, (ts, user) in enumerate(zip(timestamps, chosen)):
        p = profiles[user]
        fraud = rng.random() < .022
        scenario = "none"
        amount = float(rng.lognormal(np.log(max(p["median"], 50)), .72))
        city_i, device, receiver = p["city"], rng.choice(p["devices"]), rng.choice(p["receivers"])
        hour = int(ts.hour)
        if rng.random() < .08: amount *= rng.uniform(3, 9)  # legitimate overlap
        if rng.random() < .05: city_i = int(rng.integers(len(CITIES)))
        if rng.random() < .04: device = f"NEW_{rng.integers(100000)}"
        if rng.random() < .08: receiver = f"R{rng.integers(4000, 6000):04d}"
        if fraud:
            scenario = rng.choice(["high_amount", "new_receiver_amount", "new_device", "location_change", "velocity", "mixed", "subtle"])
            if scenario == "high_amount": amount *= rng.uniform(4, 10)
            elif scenario == "new_receiver_amount": receiver = f"R{rng.integers(4000, 6000):04d}"; amount *= rng.uniform(2, 6)
            elif scenario == "new_device": device = f"NEW_{rng.integers(100000)}"; amount *= rng.uniform(1.3, 4)
            elif scenario == "location_change": city_i = (p["city"] + int(rng.integers(1, len(CITIES)))) % len(CITIES)
            elif scenario == "velocity": recent_fraud[user] = 3
            elif scenario == "mixed": amount *= rng.uniform(1.8, 4); device = f"NEW_{rng.integers(100000)}"; city_i = int(rng.integers(len(CITIES)))
        if recent_fraud.get(user, 0) > 0:
            scenario = "velocity" if fraud else scenario
            recent_fraud[user] -= 1
        city, state = CITIES[city_i]
        rows.append({"transaction_id": f"T{i+1:07d}", "timestamp": ts.floor("s"), "user_id": user,
            "receiver_id": receiver, "amount": round(max(amount, 1), 2), "sender_bank": rng.choice(BANKS),
            "receiver_bank": rng.choice(BANKS), "device_id": device, "device_type": rng.choice(["Android", "iOS"], p=[.78,.22]),
            "city": city, "state": state, "transaction_type": rng.choice(TYPES, p=[.48,.34,.1,.08]),
            "merchant_category": rng.choice(CATEGORIES), "transaction_status": rng.choice(["SUCCESS","FAILED"], p=[.96,.04]),
            "is_fraud": int(fraud), "fraud_scenario": scenario})
    return pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
