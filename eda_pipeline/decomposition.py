from typing import Dict

import neurokit2 as nk
import numpy as np


def decompose_eda(signal: np.ndarray, sr: float, method: str = "cvxeda") -> Dict[str, np.ndarray]:
    """Split signal into tonic/phasic components using neurokit2."""

    if len(signal) == 0 or sr <= 0:
        return {"eda_clean": np.array([]), "tonic": np.array([]), "phasic": np.array([]), "scr_peaks": np.array([])}

    eda_clean = nk.eda_clean(signal, sampling_rate=sr, method="neurokit")
    phasic_info = nk.eda_phasic(eda_clean, sampling_rate=sr, method=method)
    scrs, _ = nk.eda_peaks(phasic_info["EDA_Phasic"], sampling_rate=sr)

    return {
        "eda_clean": np.asarray(eda_clean),
        "tonic": phasic_info["EDA_Tonic"].to_numpy(),
        "phasic": phasic_info["EDA_Phasic"].to_numpy(),
        "scr_peaks": scrs["SCR_Peaks"].to_numpy(),
    }


