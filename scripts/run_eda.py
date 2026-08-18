import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
import pandas as pd
from src.config import PROCESSED_PATH, FIGURE_DIR, ensure_dirs

def main():
    ensure_dirs(); df=pd.read_csv(PROCESSED_PATH,parse_dates=["timestamp"])
    plots=[("amount_distribution",lambda:df.amount.clip(upper=df.amount.quantile(.99)).hist(bins=50)),
      ("class_distribution",lambda:df.is_fraud.value_counts().sort_index().plot.bar()),
      ("transactions_by_hour",lambda:df.timestamp.dt.hour.value_counts().sort_index().plot()),
      ("fraud_rate_by_hour",lambda:df.assign(hour=df.timestamp.dt.hour).groupby("hour").is_fraud.mean().plot()),
      ("fraud_by_type",lambda:df.groupby("transaction_type").is_fraud.mean().plot.bar()),
      ("fraud_by_category",lambda:df.groupby("merchant_category").is_fraud.mean().sort_values().plot.barh())]
    for name,fn in plots: plt.figure(figsize=(8,4)); fn(); plt.tight_layout(); plt.savefig(FIGURE_DIR/f"{name}.png"); plt.close()

if __name__=="__main__":main()
