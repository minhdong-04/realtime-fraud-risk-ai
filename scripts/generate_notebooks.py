"""
{
    script : generate_notebooks.py
    desc   : Runner tao 5 Jupyter Notebooks thuc nghiem theo chuan hoc thuat.
    output : notebooks/03_baseline_models.ipynb .. 07_shap.ipynb
}
"""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.notebook_templates_base import build_nb_03_baseline, build_nb_04_imbalanced
from scripts.notebook_templates_advanced import (
    build_nb_05_threshold,
    build_nb_06_hybrid,
    build_nb_07_shap,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"


def create_notebook(cells: list[dict]) -> dict:
    """
    {
        func   : create_notebook
        desc   : Dong goi danh sach cell vao cau truc JSON chuan Jupyter v4
        input  : cells (list[dict])
        output : dict
        loop   : 0 loops
    }
    """
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def generate_all_notebooks() -> None:
    """
    {
        func   : generate_all_notebooks
        desc   : Xuat toan bo 5 notebooks ra thu muc notebooks/
        input  : None
        output : None
        loop   : 1 loop — duyet qua 5 notebook templates
    }
    """
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
    mapping = {
        "03_baseline_models.ipynb": build_nb_03_baseline(),
        "04_imbalanced.ipynb": build_nb_04_imbalanced(),
        "05_threshold.ipynb": build_nb_05_threshold(),
        "06_hybrid.ipynb": build_nb_06_hybrid(),
        "07_shap.ipynb": build_nb_07_shap(),
    }
    # { loop-1: ghi tung file notebook }
    for name, cells in mapping.items():
        out_path = NOTEBOOKS_DIR / name
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(create_notebook(cells), f, ensure_ascii=False, indent=2)
        print(f" -> Da xuat {name} ({out_path.stat().st_size / 1024:.2f} KB)")


if __name__ == "__main__":
    generate_all_notebooks()
