"""
{
    module : test_data_quality.py
    desc   : Kiem thu Data Quality Checklist cho 3 datasets theo 05_DATA_ARCHITECTURE.md Muc 10
}
"""

import os
import json
import pytest
import pandas as pd

def test_ulb_creditcard_data_quality():
    """DQ-01: Kiem tra chat luong dataset ULB CreditCard"""
    raw_path = "data/raw/ubl_creditcard/creditcard.csv"
    if not os.path.exists(raw_path):
        pytest.skip(f"Khong tim thay {raw_path}")

    df = pd.read_csv(raw_path, nrows=1000)
    assert "Class" in df.columns or "isFraud" in df.columns
    assert "Amount" in df.columns
    assert "Time" in df.columns

def test_ulb_split_config_exists():
    """DQ-02: Kiem tra file cau hinh split creditcard_split_config.json"""
    config_path = "data/splits/creditcard_split_config.json"
    if not os.path.exists(config_path):
        pytest.skip(f"Chua tao {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    assert cfg["dataset"] == "ULB Credit Card Fraud Detection"
    assert cfg["train_ratio"] == 0.60
    assert cfg["total_rows"] > 0
    assert 0.0 < cfg["fraud_rate_train"] < 0.05

def test_ieee_cis_raw_files_exist():
    """DQ-03: Kiem tra cac file nguon IEEE-CIS tren dia"""
    raw_dir = "data/raw/ieee_cis"
    txn_file = os.path.join(raw_dir, "train_transaction.csv")
    if not os.path.exists(txn_file):
        pytest.skip(f"Khong tim thay {txn_file}")

    assert os.path.exists(txn_file)
    assert os.path.getsize(txn_file) > 100_000_000

def test_paysim_raw_files_exist():
    """DQ-04: Kiem tra file nguon PaySim tren dia"""
    raw_dir = "data/raw/paysim"
    ps_file = os.path.join(raw_dir, "PS_log.csv")
    ps_alt = os.path.join(raw_dir, "PS_20174392719_1491204439457_log.csv")
    exists = os.path.exists(ps_file) or os.path.exists(ps_alt)
    if not exists:
        pytest.skip("Chua tai dataset PaySim")
    assert exists

def test_data_folders_structure():
    """DQ-05: Kiem tra toan bo cau truc thu muc data/ theo 05_DATA_ARCHITECTURE.md"""
    required_dirs = [
        "data/raw/ieee_cis",
        "data/raw/ubl_creditcard",
        "data/raw/paysim",
        "data/processed/ieee_cis",
        "data/processed/ubl_creditcard",
        "data/processed/paysim",
        "data/features/ieee_cis",
        "data/features/ubl_creditcard",
        "data/features/paysim",
        "data/splits",
        "data/labels",
    ]
    if not os.path.isdir("data"):
        pytest.skip("Dataset khong nam trong repo (xem README) - bo qua kiem tra thu muc data/")
    for d in required_dirs:
        assert os.path.isdir(d), f"Thieu thu muc bat buoc: {d}"
