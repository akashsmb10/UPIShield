from src.config import ensure_dirs, PROCESSED_PATH, SAMPLE_PATH
from src.generate_data import generate_transactions
from src.validation import require_valid_transactions

def main():
    ensure_dirs(); df = generate_transactions(); require_valid_transactions(df)
    df.to_csv(PROCESSED_PATH, index=False); df.sample(750, random_state=42).sort_values("timestamp").to_csv(SAMPLE_PATH, index=False)
    print(f"Generated {len(df):,} transactions; {df.user_id.nunique():,} users; fraud={df.is_fraud.mean():.2%}")
    return df

if __name__ == "__main__": main()
