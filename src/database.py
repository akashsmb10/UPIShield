import sqlite3
from .config import DB_PATH

def prepare_database(transactions, scored):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        transactions.tail(5000).to_sql("transactions", conn, if_exists="replace", index=False)
        scored.tail(5000).to_sql("risk_scores", conn, if_exists="replace", index=False)

def user_history(user_id, limit=500):
    if not DB_PATH.exists(): return []
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(x) for x in conn.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY timestamp LIMIT ?", (user_id, limit))]
