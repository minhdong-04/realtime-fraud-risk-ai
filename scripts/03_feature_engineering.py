"""
{
    script : 03_feature_engineering.py
    desc   : Feature engineering pipeline offline cho IEEE-CIS va cac datasets theo 05_DATA_ARCHITECTURE.md
    input  : data/processed/{dataset}/{train,val,test}_merged.parquet
    output : data/features/{dataset}/{train,val,test}_features.parquet
    loop   : 1 loop — xu ly tung split
    run    : python scripts/03_feature_engineering.py --dataset ieee_cis
}
"""

import os
import argparse
import pandas as pd
import numpy as np

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    {
        func   : extract_features
        desc   : Chuyen doi cac cot dac trung, fill NA va encode
        input  : df (pd.DataFrame)
        output : pd.DataFrame
        loop   : 0 loops
    }
    """
    features_df = pd.DataFrame(index=df.index)

    # 1. Amount features
    if "TransactionAmt" in df.columns:
        features_df["amount"] = df["TransactionAmt"].fillna(0.0)
        features_df["amount_log"] = np.log1p(np.maximum(0, features_df["amount"]))
    elif "amount" in df.columns:
        features_df["amount"] = df["amount"].fillna(0.0)
        features_df["amount_log"] = np.log1p(np.maximum(0, features_df["amount"]))

    # 2. Card / Identifier features
    for col in ["card1", "card2", "card3", "card5"]:
        if col in df.columns:
            features_df[col] = df[col].fillna(-1.0).astype("float32")

    # 3. Categorical encoding
    for col in ["ProductCD", "card4", "card6"]:
        if col in df.columns:
            features_df[col] = df[col].astype("category").cat.codes.astype("int16")

    # 4. Count / Dist features
    for col in ["C1", "C2", "C13", "D1", "D15"]:
        if col in df.columns:
            features_df[col] = df[col].fillna(0.0).astype("float32")

    # 5. Label
    if "isFraud" in df.columns:
        features_df["isFraud"] = df["isFraud"].astype("int8")

    return features_df

def main():
    """
    {
        func   : main
        desc   : Dieu phoi feature extraction cho cac tap du lieu
        input  : None
        output : None
        loop   : 1 loop — xu ly train, val, test
    }
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="ieee_cis", help="Dataset name")
    args = parser.parse_args()

    processed_dir = f"data/processed/{args.dataset}"
    features_dir = f"data/features/{args.dataset}"
    os.makedirs(features_dir, exist_ok=True)

    # { loop-1: xu ly tung split train, val, test }
    for split in ["train", "val", "test"]:
        in_path = f"{processed_dir}/{split}_merged.parquet"
        if not os.path.exists(in_path):
            in_path = f"{processed_dir}/{split}.parquet"

        if os.path.exists(in_path):
            print(f"[INFO] Processing features for {in_path}...")
            df = pd.read_parquet(in_path)
            feats = extract_features(df)
            out_path = f"{features_dir}/{split}_features.parquet"
            feats.to_parquet(out_path, index=False, compression="snappy")
            print(f"  [SAVED] {out_path} — shape {feats.shape}")

    print(f"[SUCCESS] Feature engineering cho {args.dataset} hoan tat!")

if __name__ == "__main__":
    main()
