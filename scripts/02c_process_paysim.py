"""
{
    script : 02c_process_paysim.py
    desc   : Xu ly PaySim dataset:
             - Chi giu TRANSFER va CASH_OUT (co fraud)
             - Feature engineering: balance_diff, error_balance_orig
             - Time-based split theo step
             - Tao streaming_sample.parquet cho Kafka demo
    input  : data/raw/paysim/PS_log.csv
    output : data/processed/paysim/{train,val,test}.parquet
             data/features/paysim/streaming_sample.parquet
             data/splits/paysim_split_config.json
    loop   : 1 loop — luu splits
    run    : python scripts/02c_process_paysim.py
}
"""

import os
import json
from typing import Any
import pandas as pd

RAW_PATH = "data/raw/paysim/PS_log.csv"
RAW_ALT_PATH = "data/raw/paysim/PS_20174392719_1491204439457_log.csv"
PROCESSED_DIR = "data/processed/paysim"
FEATURES_DIR = "data/features/paysim"
SPLITS_DIR = "data/splits"

PAYSIM_DTYPES: dict[Any, Any] = {
    "step": "int32",
    "type": "category",
    "amount": "float32",
    "nameOrig": "str",
    "oldbalanceOrg": "float32",
    "newbalanceOrig": "float32",
    "nameDest": "str",
    "oldbalanceDest": "float32",
    "newbalanceDest": "float32",
    "isFraud": "int8",
    "isFlaggedFraud": "int8",
}

def load_and_filter(path: str) -> pd.DataFrame:
    """
    {
        func   : load_and_filter
        desc   : Load PaySim, chi giu TRANSFER va CASH_OUT
        input  : path (str)
        output : pd.DataFrame
        loop   : 0 loops
    }
    """
    actual_path = path if os.path.exists(path) else RAW_ALT_PATH
    if not os.path.exists(actual_path):
        raise FileNotFoundError(f"Khong tim thay PaySim dataset tai {path} hoac {RAW_ALT_PATH}")

    print(f"[INFO] Loading PaySim from {actual_path}...")
    df = pd.read_csv(actual_path, dtype=PAYSIM_DTYPES)
    print(f"[INFO] Full dataset: {len(df):,} rows | fraud: {df['isFraud'].sum():,}")

    # { filter: chi TRANSFER va CASH_OUT vi fraud pattern chi o 2 loai nay }
    fraud_types = ["TRANSFER", "CASH_OUT"]
    df_filtered = pd.DataFrame(df[df["type"].isin(fraud_types)]).copy()
    print(f"[INFO] Filtered (TRANSFER/CASH_OUT): {len(df_filtered):,} rows | fraud: {df_filtered['isFraud'].sum():,}")
    return df_filtered

def engineer_paysim_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    {
        func   : engineer_paysim_features
        desc   : Tao cac dac trung tu bien dong so du tai khoan
        input  : df (pd.DataFrame)
        output : pd.DataFrame
        loop   : 0 loops
    }
    """
    epsilon = 1e-8
    # { feature: chenh lech so du tai khoan goc }
    df["balance_diff_orig"] = df["newbalanceOrig"] - df["oldbalanceOrg"] + df["amount"]
    # { feature: error so du tai khoan dich }
    df["balance_diff_dest"] = df["newbalanceDest"] - df["oldbalanceDest"] - df["amount"]
    # { feature: ty le amount / so du ban dau }
    df["amount_ratio_orig"] = df["amount"] / (df["oldbalanceOrg"] + epsilon)
    # { feature: tai khoan dich co phai merchant }
    df["dest_is_merchant"] = df["nameDest"].str.startswith("M").astype("int8")
    # { feature: tai khoan dich co so du 0 truoc do }
    df["dest_empty_before"] = (df["oldbalanceDest"] == 0).astype("int8")
    # { encode: type -> binary }
    df["is_transfer"] = (df["type"] == "TRANSFER").astype("int8")

    df = df.drop(columns=["nameOrig", "nameDest", "type", "isFlaggedFraud"])
    return df

def main():
    """
    {
        func   : main
        desc   : Dieu phoi pipeline xu ly PaySim
        input  : None
        output : None
        loop   : 1 loop — luu splits
    }
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FEATURES_DIR, exist_ok=True)
    os.makedirs(SPLITS_DIR, exist_ok=True)

    df = load_and_filter(RAW_PATH)
    df = engineer_paysim_features(df)

    # Time-based split theo step
    df_sorted = df.sort_values("step").reset_index(drop=True)
    n = len(df_sorted)
    train_end = int(n * 0.60)
    val_end = int(n * 0.80)

    train = df_sorted.iloc[:train_end].copy()
    val = df_sorted.iloc[train_end:val_end].copy()
    test = df_sorted.iloc[val_end:].copy()

    config = {
        "dataset": "PaySim Synthetic Financial Dataset",
        "split_strategy": "time_based",
        "split_column": "step",
        "filter_applied": "type IN (TRANSFER, CASH_OUT)",
        "train_ratio": 0.60,
        "val_ratio": 0.20,
        "test_ratio": 0.20,
        "train_rows": len(train),
        "val_rows": len(val),
        "test_rows": len(test),
        "fraud_rate_train": float(train["isFraud"].mean()),
        "fraud_rate_val": float(val["isFraud"].mean()),
        "fraud_rate_test": float(test["isFraud"].mean()),
        "features_engineered": [
            "balance_diff_orig", "balance_diff_dest",
            "amount_ratio_orig", "dest_is_merchant",
            "dest_empty_before", "is_transfer"
        ],
        "note": "Chi TRANSFER + CASH_OUT. Fraud chi xay ra o 2 types nay.",
    }

    # { loop-1: luu 3 splits }
    for name, split_df in [("train", train), ("val", val), ("test", test)]:
        path = f"{PROCESSED_DIR}/{name}.parquet"
        split_df.to_parquet(path, index=False, compression="snappy")
        print(f"  [SAVED] {path} — {len(split_df):,} rows | fraud rate: {split_df['isFraud'].mean():.4f}")

    # Tao streaming sample 1000 rows cho Kafka demo (100 fraud + 900 legit)
    fraud_sample = test[test["isFraud"] == 1].head(100)
    legit_sample = test[test["isFraud"] == 0].head(900)
    stream_sample = pd.concat([fraud_sample, legit_sample]).sample(frac=1, random_state=42)
    stream_path = f"{FEATURES_DIR}/streaming_sample.parquet"
    stream_sample.to_parquet(stream_path, index=False)
    print(f"  [SAVED] streaming_sample: {len(stream_sample)} rows (100 fraud + 900 legit)")

    config_path = f"{SPLITS_DIR}/paysim_split_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"[SUCCESS] PaySim processed xong! Config luu tai {config_path}")

if __name__ == "__main__":
    main()
