from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_PATH = DATA_DIR / "processed" / "transactions.csv"
SAMPLE_PATH = DATA_DIR / "sample" / "sample_transactions.csv"
ARTIFACT_DIR = ROOT / "artifacts"
REPORT_DIR = ROOT / "reports"
FIGURE_DIR = REPORT_DIR / "figures"
DB_PATH = DATA_DIR / "upishield.db"
SEED = 42
N_TRANSACTIONS = 50_000
N_USERS = 2_000
MODEL_FEATURES = [
    "log_amount", "hour", "day_of_week", "is_weekend", "is_night",
    "previous_user_txn_count", "previous_user_avg_amount",
    "previous_user_amount_std", "amount_vs_user_avg", "amount_zscore_user",
    "minutes_since_previous_transaction", "is_new_device",
    "previous_device_txn_count", "is_new_receiver",
    "previous_transactions_to_receiver", "previous_amount_to_receiver_avg",
    "city_changed", "txn_count_last_10min", "txn_count_last_1hour",
    "amount_sum_last_1hour", "amount_sum_last_24h",
]

def ensure_dirs():
    for path in [PROCESSED_PATH.parent, SAMPLE_PATH.parent, ARTIFACT_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
