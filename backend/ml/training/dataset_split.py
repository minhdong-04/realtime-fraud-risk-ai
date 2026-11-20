"""
{
    module : dataset_split.py
    desc   : Phân chia tập dữ liệu huấn luyện theo trình tự thời gian (Chronological Train/Val/Test Split).
}
"""

import numpy as np

def chronological_split(
    data: np.ndarray,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    {
        func   : chronological_split
        desc   : Chia tập dữ liệu theo thứ tự thời gian nghiêm ngặt (Train < Val < Test) chống Data Leakage
        input  : data (np.ndarray), train_ratio (float), val_ratio (float)
        output : tuple[np.ndarray, np.ndarray, np.ndarray] — (train, val, test)
        loop   : 0 loops
    }
    """
    n = len(data)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_set = data[:train_end]
    val_set = data[train_end:val_end]
    test_set = data[val_end:]

    return train_set, val_set, test_set
