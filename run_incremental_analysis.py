#!/usr/bin/env python3
"""
Incremental EDA Analysis Script
- Only processes NEW .mat files (skips already processed)
- Updates comparison metrics with new data
- Preserves existing results
"""

import argparse
import json
from pathlib import Path
from typing import Set

import pandas as pd
from tqdm import tqdm
import numpy as np

from dataclasses import asdict

from eda_pipeline.config import EDAConfig
# Import helpers from the main pipeline so we can run per-file processing
from eda_pipeline.pipeline import (
    process_channel,
    _prepare_output_dirs,
    plot_overview,
    plot_scr_peaks,
    save_quality_report,
)
from eda_pipeline.io_utils import load_mat_file, _sanitize_label


def get_processed_participants(output_dir: Path) -> Set[str]:
    """Get list of already processed participant folders"""
    processed = set()
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir() and item.name != "summary":
                # Check if it has metrics.json (indicates complete processing)
                if (item / "metrics.json").exists():
                    processed.add(item.name)
    return processed


def filter_mat_files_to_process(cfg: EDAConfig, processed: Set[str]) -> tuple:
    """
    Check which .mat files need processing.
    Returns (all_files, new_files)
    """
    mat_files = sorted(Path(cfg.data_dir).glob(cfg.file_glob))
    
    # Files that need processing (don't have corresponding processed output)
    new_files = []
    for mat_path in mat_files:
        # Extract participant ID from filename using the same sanitizer as loader
        stem = _sanitize_label(mat_path.stem)
        # Check if any processed folder starts with this name
        needs_processing = True
        for proc in processed:
            if stem in proc.lower() or proc.lower() in stem:
                needs_processing = False
                break
        if needs_processing:
            new_files.append(mat_path)
    
    return mat_files, new_files


def run_incremental_analysis(cfg: EDAConfig, force_all: bool = False, plots_only: bool = False) -> None:
    """
    Run analysis only on NEW files.
    
    Args:
        cfg: EDA configuration
        force_all: If True, reprocess all files regardless of existence
    """
    processed = get_processed_participants(cfg.output_dir)
    
    print("\n" + "="*70)
    print("  EDA/GSR Incremental Analysis")
    print("="*70)
    print(f"\nWorkspace: {cfg.data_dir}")
    print(f"Output directory: {cfg.output_dir}")
    print(f"Already processed: {len(processed)} participant(s)")
    if processed:
        print(f"  - {', '.join(sorted(list(processed)[:5]))}")
        if len(processed) > 5:
            print(f"  - ... and {len(processed) - 5} more")
    
    mat_files, new_files = filter_mat_files_to_process(cfg, processed)

    print(f"\nTotal .mat files found: {len(mat_files)}")
    print(f"New files detected: {len(new_files)}")

    if len(new_files) == 0 and not force_all:
        print("\n✓ No new files to process. All .mat files have been analyzed.")
        print("  Use --force to reprocess all files or --plots-only to regenerate plots")
        return

    # Decide which files to process
    if force_all:
        files_to_process = mat_files
        print(f"\n⚠ Forcing reprocessing of all {len(mat_files)} files...")
    else:
        files_to_process = new_files

    print("\n" + "-"*70)
    print("Starting analysis for chosen files...")
    print("-"*70 + "\n")

    participant_summary = {}

    for mat_path in files_to_process:
        print(f"Processing file: {mat_path.name}")
        channels = load_mat_file(mat_path)
        for ch in channels:
            # If plots-only requested and existing processed pickle/CSVs present, load them instead
            if plots_only:
                # Attempt to load existing pickle first
                pkl = cfg.output_dir / ch.participant_id / "processed.pkl"
                if pkl.exists():
                    import pandas as _pd
                    data = _pd.read_pickle(pkl)
                    # Re-run plotting only
                    out_paths = _prepare_output_dirs(cfg.output_dir, ch.participant_id)
                    plot_overview(
                        raw=data.get("data_uS"),
                        cleaned=data.get("filtered"),
                        tonic=data.get("decomp")["tonic"],
                        phasic=data.get("decomp")["phasic"],
                        sr=data.get("resampled_sr"),
                        artifacts=data.get("artifacts").segments,
                        out=out_paths["overview_plot"],
                    )
                    plot_scr_peaks(data.get("decomp")["phasic"], data.get("decomp")["scr_peaks"], data.get("resampled_sr"), out_paths["scr_plot"])
                    print(f"  → Plots regenerated for {ch.participant_id}")
                    continue
                else:
                    print(f"  → No processed pickle found for {ch.participant_id}; performing full processing")

            # Full per-channel processing (reuse pipeline helpers)
            result = process_channel(ch, cfg)
            out_paths = _prepare_output_dirs(cfg.output_dir, ch.participant_id)
            # Save CSVs, pickle and metrics by reusing pipeline save logic
            # The pipeline's save_outputs function is internal; replicate minimal saving here
            import pandas as _pd
            _pd.DataFrame({"time_s": np.arange(len(ch.data)) / ch.samplerate, "conductance_uS": result["data_uS"]}).to_csv(
                out_paths["raw_csv"], index=False
            )
            _pd.DataFrame({"time_s": np.arange(len(result["decomp"]["tonic"])) / result["resampled_sr"], "tonic_uS": result["decomp"]["tonic"]}).to_csv(
                out_paths["tonic_csv"], index=False
            )
            _pd.DataFrame({"time_s": np.arange(len(result["decomp"]["phasic"])) / result["resampled_sr"], "phasic_uS": result["decomp"]["phasic"]}).to_csv(
                out_paths["phasic_csv"], index=False
            )
            # Save pickle
            _pd.to_pickle(
                {
                    "channel": ch,
                    "data_uS": result["data_uS"],
                    "cleaned": result["cleaned"],
                    "filtered": result["filtered"],
                    "resampled": result["resampled"],
                    "resampled_sr": result["resampled_sr"],
                    "decomp": result["decomp"],
                    "artifacts": result["artifacts"],
                    "metrics": result["metrics"],
                },
                out_paths["pickle"],
            )
            # Save metrics JSON
            out_paths["metrics_json"].write_text(json.dumps(asdict(result["metrics"]), indent=2), encoding="utf-8")

            # Plots and report
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

    # Append new metrics to summary CSV (preserve existing rows)
    summary_path = cfg.output_dir / "summary" / "comparison_metrics.csv"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    new_rows = []
    for pid, metrics in participant_summary.items():
        row = asdict(metrics)
        row["participant"] = pid
        new_rows.append(row)

    if new_rows:
        if summary_path.exists():
            existing = pd.read_csv(summary_path)
            appended = pd.DataFrame(new_rows)
            combined = pd.concat([existing, appended], ignore_index=True)
            # Drop duplicates by participant, keep last (new)
            combined = combined.sort_values(by=["participant"]).drop_duplicates(subset=["participant"], keep="last")
            combined.to_csv(summary_path, index=False)
        else:
            pd.DataFrame(new_rows).to_csv(summary_path, index=False)

    print("\n" + "="*70)
    print("  Analysis Complete")
    print("="*70)
    print(f"Newly processed: {len(participant_summary)} participant(s)")
    print(f"Total processed (existing folders): {len(get_processed_participants(cfg.output_dir))}")
    if summary_path.exists():
        df = pd.read_csv(summary_path)
        print(f"\n✓ Comparison metrics updated: {len(df)} rows")
        print(f"  Location: {summary_path}")
    print("\n" + "="*70 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Incremental EDA analysis: process only NEW .mat files"
    )
    parser.add_argument(
        "--config", 
        type=Path, 
        default=Path("config.yaml"), 
        help="Path to YAML config file"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Reprocess ALL files, even if already analyzed"
    )
    args = parser.parse_args()

    cfg = EDAConfig.from_yaml(args.config)
    run_incremental_analysis(cfg, force_all=args.force)


if __name__ == "__main__":
    main()
