"""
{
    script : 02b_merge_ieee_cis.py
    desc   : Merge IEEE-CIS transaction + identity, toi uu memory dtypes,
             time-based split va luu parquet theo 05_DATA_ARCHITECTURE.md
    input  : data/raw/ieee_cis/{train,test}_{transaction,identity}.csv
    output : data/processed/ieee_cis/{train,val,test}_merged.parquet
             data/splits/ieee_cis_split_config.json
    loop   : 1 loop — xu ly train va test
    run    : python scripts/02b_merge_ieee_cis.py
}
"""

import os
import json
import pandas as pd

RAW_DIR = "data/raw/ieee_cis"
PROCESSED_DIR = "data/processed/ieee_cis"
SPLITS_DIR = "data/splits"
START_DATE = pd.Timestamp("2017-12-01")

TRANSACTION_DTYPES = {
    "TransactionID": "int32",
    "isFraud": "int8",
    "TransactionDT": "int32",
    "TransactionAmt": "float32",
    "ProductCD": "category",
    "card1": "int16",
    "card2": "float32",
    "card3": "float32",
    "card4": "category",
    "card5": "float32",
    "card6": "category",
    "addr1": "float32",
    "addr2": "float32",
    **{f"C{i}": "float32" for i in range(1, 15)},
    **{f"D{i}": "float32" for i in range(1, 16)},
    **{f"M{i}": "category" for i in range(1, 10)},
}

def load_and_merge(split: str) -> pd.DataFrame:
    """
    {
        func   : load_and_merge
        desc   : Load transaction + identity CSV, LEFT JOIN tren TransactionID
        input  : split (str) — 'train' hoac 'test'
        output : pd.DataFrame
        loop   : 0 loops
    }
    """
    dtypes = TRANSACTION_DTYPES.copy()
    if split == "test":
        dtypes.pop("isFraud", None)

    txn_path = f"{RAW_DIR}/{split}_transaction.csv"
    id_path = f"{RAW_DIR}/{split}_identity.csv"

    if not os.path.exists(txn_path):
        raise FileNotFoundError(f"Khong tim thay: {txn_path}")

    print(f"[{split.upper()}] Loading transaction from {txn_path}...")
    txn = pd.read_csv(txn_path, dtype=dtypes)

    if os.path.exists(id_path):
        print(f"[{split.upper()}] Loading identity from {id_path}...")
        identity = pd.read_csv(id_path)
        print(f"[{split.upper()}] Merging (LEFT JOIN)...")
        merged = txn.merge(identity, on="TransactionID", how="left")
    else:
        print(f"[{split.upper()}] Identity file not found, using transaction only...")
        merged = txn

    # { convert: TransactionDT (delta seconds) -> timestamp uoc tinh }
    merged["transaction_ts"] = START_DATE + pd.to_timedelta(
        merged["TransactionDT"], unit="s"
    )
    print(f"[{split.upper()}] Done — shape: {merged.shape}")
    return merged

def time_based_split_ieee(
    df: pd.DataFrame,
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    {
        func   : time_based_split_ieee
        desc   : Split theo TransactionDT (da sort ascending)
        input  : df (pd.DataFrame), ratios
        output : tuple(train, val, test)
        loop   : 0 loops
    }
    """
    df_sorted = df.sort_values("TransactionDT").reset_index(drop=True)
    n = len(df_sorted)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    return (
        df_sorted.iloc[:train_end].copy(),
        df_sorted.iloc[train_end:val_end].copy(),
        df_sorted.iloc[val_end:].copy(),
    )

def main():
    """
    {
        func   : main
        desc   : Dieu phoi merge va split dataset IEEE-CIS
        input  : None
        output : None
        loop   : 2 loops — load/merge va luu split files
    }
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(SPLITS_DIR, exist_ok=True)

    # { loop-1: merge train va test rieng }
    for split in ["train", "test"]:
        if os.path.exists(f"{RAW_DIR}/{split}_transaction.csv"):
            merged = load_and_merge(split)
            out = f"{PROCESSED_DIR}/{split}_merged.parquet"
            merged.to_parquet(out, index=False, compression="snappy")
            size_mb = os.path.getsize(out) / 1e6
            print(f"  [SAVED] {out} — {size_mb:.1f} MB")

    # Time-based split tren tap train
    train_full = pd.read_parquet(f"{PROCESSED_DIR}/train_merged.parquet")
    train, val, test = time_based_split_ieee(train_full)

    config = {
        "dataset": "IEEE-CIS Fraud Detection",
        "split_strategy": "time_based",
        "split_column": "TransactionDT",
        "train_ratio": 0.60,
        "val_ratio": 0.20,
        "test_ratio": 0.20,
        "train_rows": len(train),
        "val_rows": len(val),
        "test_rows": len(test),
        "fraud_rate_train": float(train["isFraud"].mean()),
        "fraud_rate_val": float(val["isFraud"].mean()),
        "fraud_rate_test": float(test["isFraud"].mean()),
        "train_dt_min": int(train["TransactionDT"].min()),
        "train_dt_max": int(train["TransactionDT"].max()),
        "val_dt_min": int(val["TransactionDT"].min()),
        "val_dt_max": int(val["TransactionDT"].max()),
        "test_dt_min": int(test["TransactionDT"].min()),
        "test_dt_max": int(test["TransactionDT"].max()),
        "note": "Time-based split. test_merged.parquet tu Kaggle (khong co label).",
    }

    # { loop-2: luu 3 splits }
    for name, split_df in [("train", train), ("val", val), ("test", test)]:
        path = f"{PROCESSED_DIR}/{name}_merged.parquet"
        split_df.to_parquet(path, index=False, compression="snappy")
        fraud_rate = split_df.get("isFraud", pd.Series([0])).mean()
        print(f"  [SAVED] {path} — {len(split_df):,} rows | fraud rate: {fraud_rate:.4f}")

    config_path = f"{SPLITS_DIR}/ieee_cis_split_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"[SUCCESS] IEEE-CIS processed xong! Config luu tai {config_path}")

if __name__ == "__main__":
    main()
