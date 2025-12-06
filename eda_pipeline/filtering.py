from typing import Tuple

import numpy as np
import scipy.signal as sps


def resample_signal(signal: np.ndarray, orig_sr: float, target_sr: float) -> Tuple[np.ndarray, float]:
    """Resample signal to target_sr if needed."""

    if orig_sr <= 0 or target_sr <= 0 or abs(orig_sr - target_sr) < 1e-3:
        return signal, orig_sr
    duration = len(signal) / orig_sr
    new_len = int(duration * target_sr)
    resampled = sps.resample(signal, new_len)
    return resampled, target_sr


def lowpass(signal: np.ndarray, sr: float, cutoff: float, order: int = 4) -> np.ndarray:
    """Butterworth low-pass filter."""

    if sr <= 0 or cutoff <= 0:
        return signal
    nyq = 0.5 * sr
    norm = cutoff / nyq
    b, a = sps.butter(order, norm, btype="low", analog=False)
    return sps.filtfilt(b, a, signal)




