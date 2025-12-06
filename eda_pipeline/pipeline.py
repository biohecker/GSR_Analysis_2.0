import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from tqdm import tqdm

from .artifacts import detect_artifacts
from .config import EDAConfig
from .decomposition import decompose_eda
from .filtering import lowpass, resample_signal
from .io_utils import ChannelData, load_mat_file
from .metrics import QualityMetrics, compute_quality_metrics
from .plotting import plot_overview, plot_scr_peaks
from .reporting import save_quality_report


def _conductance_from_unit(data: np.ndarray, unit: str) -> np.ndarray:
    """Convert to µS if needed."""

    unit = (unit or "").strip().lower()
    if unit in {"s", "µs", "us"}:
        return data * 1e6 if unit == "s" else data
    if "ohm" in unit or "ω" in unit:
        # Assume megaohms; avoid divide by zero
        data_mohm = np.clip(data, 1e-9, None)
        return 1.0 / data_mohm
    # Fallback assume Siemens already in µS scale
    return data


def _prepare_output_dirs(base: Path, participant: str) -> Dict[str, Path]:
    participant_dir = base / participant
    participant_dir.mkdir(parents=True, exist_ok=True)
    return {
        "participant_dir": participant_dir,
        "raw_csv": participant_dir / "raw_data.csv",
        "tonic_csv": participant_dir / "tonic_component.csv",
        "phasic_csv": participant_dir / "phasic_component.csv",
        "metrics_json": participant_dir / "metrics.json",
        "overview_plot": participant_dir / "overview.png",
        "scr_plot": participant_dir / "scr_peaks.png",
        "report": participant_dir / "quality_report.pdf",
        "pickle": participant_dir / "processed.pkl",
    }


def process_channel(channel: ChannelData, cfg: EDAConfig) -> Dict:
    data_uS = _conductance_from_unit(channel.data, channel.unit)

    # Artifact detection
    artifacts = detect_artifacts(
        data_uS, sr=channel.samplerate, min_uS=cfg.min_conductance, max_uS=cfg.max_conductance, rapid_thresh=cfg.rapid_change_thresh
    )
    cleaned = data_uS.copy()
    cleaned[~artifacts.clean_mask] = np.nan
    # Replace NaN with median to preserve length
    median_val = float(np.nanmedian(cleaned)) if np.isfinite(np.nanmedian(cleaned)) else 0.0
    cleaned = np.nan_to_num(cleaned, nan=median_val)

    # Filtering
    filtered = lowpass(cleaned, channel.samplerate, cfg.lowpass_hz, order=cfg.lowpass_order)
    # Resample
    resampled, resampled_sr = resample_signal(filtered, channel.samplerate, cfg.resample_hz)

    # Decomposition
    decomp = decompose_eda(resampled, resampled_sr, method=cfg.neurokit_method)
    metrics = compute_quality_metrics(
        tonic=decomp["tonic"],
        phasic=decomp["phasic"],
        scr_peaks=decomp["scr_peaks"],
        sr=resampled_sr,
        artifact_percent=artifacts.percent_artifact,
        cleaned=resampled,
        raw=resampled,
    )

    return {
        "channel": channel,
        "data_uS": data_uS,
        "cleaned": cleaned,
        "filtered": filtered,
        "resampled": resampled,
        "resampled_sr": resampled_sr,
        "decomp": decomp,
        "artifacts": artifacts,
        "metrics": metrics,
    }


def save_outputs(result: Dict, out_paths: Dict[str, Path]) -> None:
    channel = result["channel"]
    decomp = result["decomp"]
    metrics: QualityMetrics = result["metrics"]

    # Save CSVs
    pd.DataFrame({"time_s": np.arange(len(channel.data)) / channel.samplerate, "conductance_uS": result["data_uS"]}).to_csv(
        out_paths["raw_csv"], index=False
    )
    pd.DataFrame({"time_s": np.arange(len(decomp["tonic"])) / result["resampled_sr"], "tonic_uS": decomp["tonic"]}).to_csv(
        out_paths["tonic_csv"], index=False
    )
    pd.DataFrame({"time_s": np.arange(len(decomp["phasic"])) / result["resampled_sr"], "phasic_uS": decomp["phasic"]}).to_csv(
        out_paths["phasic_csv"], index=False
    )

    # Save pickle
    pd.to_pickle(
        {
            "channel": channel,
            "data_uS": result["data_uS"],
            "cleaned": result["cleaned"],
            "filtered": result["filtered"],
            "resampled": result["resampled"],
            "resampled_sr": result["resampled_sr"],
            "decomp": decomp,
            "artifacts": result["artifacts"],
            "metrics": metrics,
        },
        out_paths["pickle"],
    )

    # Save metrics
    out_paths["metrics_json"].write_text(json.dumps(asdict(metrics), indent=2), encoding="utf-8")


def run_pipeline(cfg: EDAConfig) -> Dict[str, QualityMetrics]:
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    participant_summary: Dict[str, QualityMetrics] = {}

    mat_files = sorted(Path(cfg.data_dir).glob(cfg.file_glob))
    for mat_path in tqdm(mat_files, desc="files"):
        channels = load_mat_file(mat_path)
        for ch in channels:
            result = process_channel(ch, cfg)
            out_paths = _prepare_output_dirs(cfg.output_dir, ch.participant_id)
            save_outputs(result, out_paths)
            plot_overview(
                raw=result["data_uS"],
                cleaned=result["filtered"],
                tonic=result["decomp"]["tonic"],
                phasic=result["decomp"]["phasic"],
                sr=result["resampled_sr"],
                artifacts=result["artifacts"].segments,
                out=out_paths["overview_plot"],
            )
            plot_scr_peaks(result["decomp"]["phasic"], result["decomp"]["scr_peaks"], result["resampled_sr"], out_paths["scr_plot"])
            save_quality_report(
                metrics=asdict(result["metrics"]),
                plots={out_paths["overview_plot"]: "EDA Overview", out_paths["scr_plot"]: "SCR Peaks"},
                out_path=out_paths["report"],
                interpretation="Higher tonic levels suggest sympathetic arousal; SCR frequency reflects reactivity.",
                recommendations="Inspect high-artifact segments; ensure electrode contact; align with meal times for insulin analysis.",
            )
            participant_summary[ch.participant_id] = result["metrics"]
    # Write overall summary
    summary_path = cfg.output_dir / "summary" / "comparison_metrics.csv"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for pid, metrics in participant_summary.items():
        row = asdict(metrics)
        row["participant"] = pid
        rows.append(row)
    if rows:
        pd.DataFrame(rows).to_csv(summary_path, index=False)
    return participant_summary




