from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class ArtifactResult:
    clean_mask: np.ndarray
    segments: List[Tuple[int, int, str]]
    percent_artifact: float


def detect_artifacts(signal: np.ndarray, sr: float, min_uS: float, max_uS: float, rapid_thresh: float) -> ArtifactResult:
    """Detect extreme values and rapid shifts. Returns mask of valid samples."""

    n = len(signal)
    if n == 0:
        return ArtifactResult(clean_mask=np.array([]), segments=[], percent_artifact=100.0)

    mask = np.ones(n, dtype=bool)
    segments: List[Tuple[int, int, str]] = []

    # Extreme conductance limits
    bad_extremes = (signal < min_uS) | (signal > max_uS)
    if bad_extremes.any():
        mask &= ~bad_extremes
        idx = np.where(bad_extremes)[0]
        segments.append((idx[0], idx[-1], "extreme_value"))

    # Rapid changes per second
    if sr > 0:
        diff = np.abs(np.diff(signal, prepend=signal[0])) * sr
        rapid = diff > rapid_thresh
        if rapid.any():
            mask &= ~rapid
            idx = np.where(rapid)[0]
            segments.append((idx[0], idx[-1], "rapid_change"))

    # Median absolute deviation outliers
    med = float(np.median(signal[mask])) if mask.any() else 0.0
    mad = float(np.median(np.abs(signal[mask] - med))) if mask.any() else 0.0
    if mad > 0:
        z = 0.6745 * (signal - med) / mad
        outliers = np.abs(z) > 6
        if outliers.any():
            mask &= ~outliers
            idx = np.where(outliers)[0]
            segments.append((idx[0], idx[-1], "mad_outlier"))

    percent_bad = 100 * (1 - mask.sum() / n)
    return ArtifactResult(clean_mask=mask, segments=segments, percent_artifact=percent_bad)




