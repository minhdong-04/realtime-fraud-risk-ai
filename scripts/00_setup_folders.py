"""
{
    script : 00_setup_folders.py
    desc   : Khoi tao toan bo cau truc thu muc du lieu chuan theo 05_DATA_ARCHITECTURE.md
    run    : python scripts/00_setup_folders.py
}
"""

import os
import shutil

DATA_DIRS = [
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

def setup_data_architecture():
    """
    {
        func   : setup_data_architecture
        desc   : Tao cac thu muc cau truc du lieu theo 05_DATA_ARCHITECTURE.md
        input  : None
        output : None
        loop   : 1 loop — tao cac thu muc trong danh sach
    }
    """
    print("[INFO] Khoi tao cau truc thu muc chuan theo 05_DATA_ARCHITECTURE.md...")
    # { loop-1: duyet va tao tung thu muc neu chua ton tai }
    for path in DATA_DIRS:
        os.makedirs(path, exist_ok=True)
        gitkeep = os.path.join(path, ".gitkeep")
        if not os.path.exists(gitkeep):
            with open(gitkeep, "w") as f:
                pass

    # Chuan hoa ten file PaySim neu co file ten dai
    paysim_long = "data/raw/paysim/PS_20174392719_1491204439457_log.csv"
    paysim_short = "data/raw/paysim/PS_log.csv"
    if os.path.exists(paysim_long) and not os.path.exists(paysim_short):
        shutil.copyfile(paysim_long, paysim_short)
        print(f"  [OK] Sao chep {paysim_long} -> {paysim_short}")

    print("[SUCCESS] Hoan tat thiet lap cau truc thu muc data/")

if __name__ == "__main__":
    setup_data_architecture()
