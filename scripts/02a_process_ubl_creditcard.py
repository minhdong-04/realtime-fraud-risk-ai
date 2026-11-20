"""
{
    script : 02a_process_ubl_creditcard.py
    desc   : Xu ly ULB CreditCard dataset:
             - Scale Amount va Time (V1-V28 da scale boi PCA)
             - Time-based split 60/20/20
             - Luu train/val/test parquet va config JSON
    input  : data/raw/ubl_creditcard/creditcard.csv
    output : data/processed/ubl_creditcard/{train,val,test}.parquet
             data/splits/creditcard_split_config.json
    loop   : 1 loop — luu 3 splits
    run    : python scripts/02a_process_ubl_creditcard.py
}
"""

import os
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler

RAW_PATH = "data/raw/ubl_creditcard/creditcard.csv"
PROCESSED_DIR = "data/processed/ubl_creditcard"
SPLITS_DIR = "data/splits"

def load_and_scale(path: str) -> pd.DataFrame:
    """
    {
        func   : load_and_scale
        desc   : Load creditcard.csv, scale Amount va Time, doi ten Class -> isFraud
        input  : path (str)
        output : pd.DataFrame
        loop   : 0 loops
    }
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Khong tim thay file dataset: {path}")

    df = pd.read_csv(path)
    # { rename: dong nhat label column voi IEEE-CIS }
    df = df.rename(columns={"Class": "isFraud"})

    scaler = StandardScaler()
    # { scale: chi Amount va Time, V1-V28 da duoc PCA-scaled san }
    df["Amount_scaled"] = scaler.fit_transform(df[["Amount"]])
    df["Time_scaled"] = scaler.fit_transform(df[["Time"]])
    df = df.drop(columns=["Amount", "Time"])

    print(f"[INFO] ULB Loaded: {df.shape}, fraud rate: {df['isFraud'].mean():.4f}")
    return df

def time_based_split(
    df: pd.DataFrame,
    train_ratio: float = 0.60,
    val_ratio: float = 0.20,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    {
        func   : time_based_split
        desc   : Split theo thu tu thoi gian Time_scaled
        input  : df (pd.DataFrame), train_ratio (float), val_ratio (float)
        output : tuple(train, val, test)
        loop   : 0 loops
    }
    """
    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train = df.iloc[:train_end].copy()
    val = df.iloc[train_end:val_end].copy()
    test = df.iloc[val_end:].copy()
    return train, val, test

def main():
    """
    {
        func   : main
        desc   : Ham dieu phoi pipeline xu ly ULB CreditCard
        input  : None
        output : None
        loop   : 1 loop — luu cac file parquet
    }
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(SPLITS_DIR, exist_ok=True)

    df = load_and_scale(RAW_PATH)
    train, val, test = time_based_split(df)

    config = {
        "dataset": "ULB Credit Card Fraud Detection",
        "split_strategy": "time_based_row_order",
        "split_column": "Time (row order — already sorted)",
        "train_ratio": 0.60,
        "val_ratio": 0.20,
        "test_ratio": 0.20,
        "train_rows": len(train),
        "val_rows": len(val),
        "test_rows": len(test),
        "total_rows": len(df),
        "fraud_rate_train": float(train["isFraud"].to_numpy().mean()),
        "fraud_rate_val": float(val["isFraud"].to_numpy().mean()),
        "fraud_rate_test": float(test["isFraud"].to_numpy().mean()),
        "features": [c for c in df.columns if c != "isFraud"],
        "label_column": "isFraud",
        "note": "V1-V28 da PCA-scaled. Chi Amount_scaled va Time_scaled duoc StandardScaler.",
    }

    # { loop-1: luu 3 splits train/val/test dinh dang parquet }
    for name, split_df in [("train", train), ("val", val), ("test", test)]:
        path = f"{PROCESSED_DIR}/{name}.parquet"
        split_df.to_parquet(path, index=False, compression="snappy")
        print(f"  [SAVED] {path} — {len(split_df):,} rows | fraud: {split_df['isFraud'].sum()}")

    config_path = f"{SPLITS_DIR}/creditcard_split_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"[SUCCESS] ULB CreditCard processed xong! Config luu tai {config_path}")

if __name__ == "__main__":
    main()
