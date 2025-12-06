import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import yaml


@dataclass
class EDAConfig:
    """Container for configurable parameters."""

    data_dir: Path
    output_dir: Path
    resample_hz: int = 100
    lowpass_hz: float = 1.0
    lowpass_order: int = 4
    min_conductance: float = 0.1  # µS
    max_conductance: float = 25.0  # µS
    rapid_change_thresh: float = 5.0  # µS/sec
    tonic_cutoff_hz: float = 0.05
    phasic_cutoff_hz: float = 0.5
    snr_window_sec: int = 30
    artifact_percent_warn: float = 30.0
    unit_assumed: str = "S"
    participant_prefix: str = "participant"
    plots_format: str = "png"
    report_format: str = "pdf"
    neurokit_method: str = "cvxeda"
    save_intermediates: bool = True
    file_glob: str = "*.mat"
    channel_titles: List[str] = field(default_factory=list)
    cvxeda_tau0: float = 2.0
    cvxeda_tau1: float = 0.7

    @staticmethod
    def from_yaml(path: Path) -> "EDAConfig":
        with open(path, "r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        raw["data_dir"] = Path(raw["data_dir"])
        raw["output_dir"] = Path(raw["output_dir"])
        return EDAConfig(**raw)

    def to_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.__dict__, indent=2), encoding="utf-8")





