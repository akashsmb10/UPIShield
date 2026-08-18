import pandas as pd
from src.generate_data import generate_transactions
from src.validation import validate_transactions

def test_deterministic():
    a=generate_transactions(100,20); b=generate_transactions(100,20); pd.testing.assert_frame_equal(a,b)
def test_required_and_valid():
    df=generate_transactions(200,30); assert not validate_transactions(df)
def test_positive_amounts(): assert (generate_transactions(100,20).amount>0).all()
def test_binary_labels(): assert set(generate_transactions(100,20).is_fraud.unique()) <= {0,1}
def test_unique_ids(): assert generate_transactions(100,20).transaction_id.is_unique
