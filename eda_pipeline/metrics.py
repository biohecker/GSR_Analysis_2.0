from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class QualityMetrics:
    median_scl: float
    scl_range: float
    scl_slope: float
    scl_variability: float
    scr_count: int
    scr_median_amp: float
    scr_frequency_per_min: float
    artifact_percent: float
    snr: float
    stability: float


def compute_snr(signal: np.ndarray, cleaned: np.ndarray) -> float:
    if len(signal) == 0 or len(cleaned) == 0:
        return 0.0
    noise = signal - cleaned
    denom = np.std(noise) if np.std(noise) > 0 else 1e-6
    return float(np.std(cleaned) / denom)


def compute_quality_metrics(
    tonic: np.ndarray,
    phasic: np.ndarray,
    scr_peaks: np.ndarray,
    sr: float,
    artifact_percent: float,
    cleaned: np.ndarray,
    raw: np.ndarray,
) -> QualityMetrics:
    duration_min = len(tonic) / (sr * 60) if sr > 0 else 0.0
    scr_count = int(np.nansum(scr_peaks)) if scr_peaks.size else 0
    scr_median_amp = float(np.nanmedian(phasic[scr_peaks.astype(bool)])) if scr_count else 0.0
    scr_freq = scr_count / duration_min if duration_min > 0 else 0.0

    # Tonic metrics using medians
    median_scl = float(np.nanmedian(tonic)) if tonic.size else 0.0
    scl_range = float(np.nanpercentile(tonic, 95) - np.nanpercentile(tonic, 5)) if tonic.size else 0.0
    scl_slope = float((tonic[-1] - tonic[0]) / duration_min) if duration_min > 0 and tonic.size else 0.0
    scl_variability = float(np.nanmedian(np.abs(np.diff(tonic)))) if tonic.size > 1 else 0.0
    snr = compute_snr(raw, cleaned)
    stability = float(np.nanmedian(np.abs(np.diff(tonic)))) if tonic.size > 1 else 0.0

    return QualityMetrics(
        median_scl=median_scl,
        scl_range=scl_range,
        scl_slope=scl_slope,
        scl_variability=scl_variability,
        scr_count=scr_count,
        scr_median_amp=scr_median_amp,
        scr_frequency_per_min=scr_freq,
        artifact_percent=artifact_percent,
        snr=snr,
        stability=stability,
    )




