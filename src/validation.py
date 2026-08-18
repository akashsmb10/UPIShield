import pandas as pd

REQUIRED_COLUMNS = {"transaction_id", "timestamp", "user_id", "receiver_id", "amount", "device_id", "city", "is_fraud"}

def validate_transactions(df):
    errors = []
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing: errors.append(f"Missing required columns: {sorted(missing)}")
    if missing: return errors
    if df.transaction_id.duplicated().any(): errors.append("Transaction IDs must be unique")
    if df[list(REQUIRED_COLUMNS - {"timestamp"})].isna().any().any(): errors.append("Critical columns contain null values")
    if (pd.to_numeric(df.amount, errors="coerce") <= 0).any(): errors.append("Amounts must be positive")
    if not set(df.is_fraud.dropna().unique()).issubset({0, 1}): errors.append("Labels must be binary")
    ts = pd.to_datetime(df.timestamp, errors="coerce")
    if ts.isna().any(): errors.append("Timestamps must be valid")
    if not ts.is_monotonic_increasing: errors.append("Transactions must be chronological")
    return errors

def require_valid_transactions(df):
    errors = validate_transactions(df)
    if errors: raise ValueError("; ".join(errors))
