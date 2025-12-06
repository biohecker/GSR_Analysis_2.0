from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np


def plot_overview(raw: np.ndarray, cleaned: np.ndarray, tonic: np.ndarray, phasic: np.ndarray, sr: float, artifacts, out: Path):
    t_raw = np.arange(len(raw)) / sr if sr > 0 else np.arange(len(raw))
    t_clean = np.arange(len(cleaned)) / sr if sr > 0 else np.arange(len(cleaned))
    t_tonic = np.arange(len(tonic)) / sr if sr > 0 else np.arange(len(tonic))
    t_phasic = np.arange(len(phasic)) / sr if sr > 0 else np.arange(len(phasic))

    fig, axes = plt.subplots(4, 1, figsize=(14, 10))
    
    # Plot 1: Raw signal with artifacts
    axes[0].plot(t_raw, raw, label="Raw", alpha=0.7, linewidth=0.8)
    if len(artifacts) > 0:
        for s, e, label in artifacts:
            axes[0].axvspan(s / sr, e / sr, color="red", alpha=0.2)
        # Add single artifact label
        axes[0].patches[0].set_label("Artifact") if len(axes[0].patches) > 0 else None
    axes[0].set_ylabel("µS", fontsize=10)
    axes[0].set_title("Raw Signal + Artifacts", fontsize=11, fontweight="bold")
    axes[0].legend(loc="upper right", fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim(t_raw[0], t_raw[-1])

    # Plot 2: Filtered signal
    axes[1].plot(t_clean, cleaned, label="Filtered", color="tab:orange", linewidth=0.8)
    axes[1].set_ylabel("µS", fontsize=10)
    axes[1].set_title("Low-Pass Filtered Signal (1 Hz)", fontsize=11, fontweight="bold")
    axes[1].legend(loc="upper right", fontsize=9)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim(t_clean[0], t_clean[-1])

    # Plot 3: Tonic component (normalized for visibility)
    # Tonic should be in valid range; clip extreme values if needed
    tonic_clean = np.clip(tonic, np.percentile(tonic, 1), np.percentile(tonic, 99))
    axes[2].plot(t_tonic, tonic_clean, label="Tonic (SCL)", color="tab:green", linewidth=0.8)
    axes[2].set_ylabel("µS", fontsize=10)
    axes[2].set_title("Tonic Component (Baseline/SCL)", fontsize=11, fontweight="bold")
    axes[2].legend(loc="upper right", fontsize=9)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim(t_tonic[0], t_tonic[-1])

    # Plot 4: Phasic component
    axes[3].plot(t_phasic, phasic, label="Phasic (SCR)", color="tab:purple", linewidth=0.8)
    axes[3].set_xlabel("Time (s)", fontsize=10)
    axes[3].set_ylabel("µS", fontsize=10)
    axes[3].set_title("Phasic Component (Responses/SCR)", fontsize=11, fontweight="bold")
    axes[3].legend(loc="upper right", fontsize=9)
    axes[3].grid(True, alpha=0.3)
    axes[3].set_xlim(t_phasic[0], t_phasic[-1])

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_scr_peaks(phasic: np.ndarray, scr_peaks: np.ndarray, sr: float, out: Path):
    t = np.arange(len(phasic)) / sr if sr > 0 else np.arange(len(phasic))
    fig, ax = plt.subplots(figsize=(14, 5))
    
    ax.plot(t, phasic, label="Phasic (SCR)", color="tab:purple", linewidth=0.8)
    
    if scr_peaks.sum() > 0:
        peak_indices = np.where(scr_peaks.astype(bool))[0]
        peak_times = t[peak_indices]
        peak_values = phasic[peak_indices]
        ax.scatter(peak_times, peak_values, color="red", s=50, label=f"SCR Peaks (n={len(peak_indices)})", zorder=5)
    
    ax.set_xlabel("Time (s)", fontsize=10)
    ax.set_ylabel("µS", fontsize=10)
    ax.set_title("Phasic Component with SCR Peak Detection", fontsize=11, fontweight="bold")
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(t[0], t[-1])
    
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)





