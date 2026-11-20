"""
{
    module : drift_service.py
    desc   : Application Service theo doi va tinh toan do troi dac trung
             (Feature Population Stability Index - PSI) thuc te.
}
"""

import numpy as np
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def compute_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """
    {
        func   : compute_psi
        desc   : Tinh toan PSI thuc te giua hai phan bo du lieu
        input  : expected (np.ndarray), actual (np.ndarray), bins (int)
        output : (float) — gia tri PSI
        loop   : 0 loops
    }
    """
    if expected.size == 0 or actual.size == 0:
        return 0.0

    expected_hist, bin_edges = np.histogram(expected, bins=bins)
    actual_hist, _ = np.histogram(actual, bins=bin_edges)

    # Laplace smoothing de tranh chia cho 0
    expected_pct = (expected_hist + 1) / (expected_hist.sum() + bins)
    actual_pct = (actual_hist + 1) / (actual_hist.sum() + bins)

    psi_val = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return round(float(psi_val), 4)


class DriftService:
    """
    {
        class  : DriftService
        desc   : Service tinh toan chi so PSI de phat hien hien tuong Data Drift
    }
    """

    def __init__(self, db: Session, psi_threshold: float = 0.2) -> None:
        self._db = db
        self._threshold = psi_threshold

    def calculate_psi(self, expected: np.ndarray, actual: np.ndarray) -> float:
        """
        {
            func   : calculate_psi
            desc   : Tinh toan chi so PSI giua phan bo chuan va thuc te
            input  : expected (np.ndarray), actual (np.ndarray)
            output : (float) — gia tri PSI
            loop   : 0 loops
        }
        """
        return compute_psi(expected, actual)

    def check_drift(self, expected: np.ndarray, actual: np.ndarray) -> dict:
        """
        {
            func   : check_drift
            desc   : Kiem tra drift va tra ve ket qua chi tiet
            input  : expected (np.ndarray), actual (np.ndarray)
            output : dict — psi, is_drifted, threshold
            loop   : 0 loops
        }
        """
        psi = compute_psi(expected, actual)
        is_drifted = psi > self._threshold
        if is_drifted:
            logger.warning("Phat hien Data Drift: PSI=%.4f > threshold=%.2f", psi, self._threshold)
        return {
            "psi": psi,
            "is_drifted": is_drifted,
            "threshold": self._threshold,
        }
