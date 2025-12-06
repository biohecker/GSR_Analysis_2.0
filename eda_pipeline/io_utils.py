import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import scipy.io as sio


@dataclass
class ChannelData:
    """Container for a single participant-channel recording."""

    participant_id: str
    channel_id: str
    label: str
    data: np.ndarray
    samplerate: float
    unit: str
    file_source: Path
    starts: List[int]
    ends: List[int]


def _sanitize_label(label: str) -> str:
    return re.sub(r"[^0-9a-zA-Z]+", "_", label).strip("_").lower() or "channel"


def _ensure_2d(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 0:
        return arr.reshape(1, 1)
    if arr.ndim == 1:
        return arr.reshape(1, -1)
    return arr


def _guess_participant(label: str, file_stem: str, idx: int) -> str:
    clean = _sanitize_label(label)
    if clean and "channel" not in clean:
        return clean
    return f"{file_stem}_p{idx+1}"


def _resolve_unit(unittext, unittextmap, channel_idx: int) -> str:
    if unittext is None:
        return "unknown"
    try:
        unit_array = np.array(unittext).reshape(-1)
        map_array = _ensure_2d(np.array(unittextmap))
        mapped_idx = int(map_array[channel_idx, 0]) - 1 if map_array.ndim > 1 else int(map_array[0]) - 1
        if 0 <= mapped_idx < len(unit_array):
            return str(unit_array[mapped_idx]).strip()
    except Exception:
        pass
    return str(unittext).strip()


def _extract_channel_signal(
    data: np.ndarray, start_idxs: np.ndarray, end_idxs: np.ndarray
) -> Tuple[np.ndarray, List[int], List[int]]:
    starts, ends, segments = [], [], []
    for s, e in zip(start_idxs, end_idxs):
        if np.isnan(s) or np.isnan(e) or e <= 0:
            continue
        s_i, e_i = int(s) - 1, int(e)
        starts.append(s_i)
        ends.append(e_i)
        segments.append(data[s_i:e_i])
    if not segments:
        return np.array([]), starts, ends
    return np.concatenate(segments), starts, ends


def load_mat_file(path: Path) -> List[ChannelData]:
    """Load a .mat file and return per-channel data with unique identifiers."""

    raw = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
    titles = raw.get("titles", [])
    data = raw["data"]
    datastart = _ensure_2d(np.array(raw["datastart"]))
    dataend = _ensure_2d(np.array(raw["dataend"]))
    samplerate = _ensure_2d(np.array(raw["samplerate"]))
    unittext = raw.get("unittext")
    unittextmap = raw.get("unittextmap")

    if hasattr(titles, "shape") and titles.shape:
        n_channels = titles.shape[0]
    elif isinstance(titles, (list, tuple)):
        n_channels = len(titles)
        titles = np.array(titles)
    else:
        n_channels = 1
        titles = np.array([str(titles)])

    # Correct orientation if needed
    if datastart.shape[0] != n_channels and datastart.shape[1] == n_channels:
        datastart = datastart.T
        dataend = dataend.T
        samplerate = samplerate.T if samplerate.shape == datastart.shape else samplerate

    channel_list: List[ChannelData] = []
    file_stem = _sanitize_label(path.stem)
    for idx in range(n_channels):
        label = str(titles[idx]).strip()
        participant = _guess_participant(label, file_stem, idx)
        start_idxs = datastart[idx] if datastart.ndim > 1 else datastart
        end_idxs = dataend[idx] if dataend.ndim > 1 else dataend
        signal, starts, ends = _extract_channel_signal(data, np.atleast_1d(start_idxs), np.atleast_1d(end_idxs))
        sr_vals = samplerate[idx] if samplerate.ndim > 1 else samplerate
        sr = float(np.median(sr_vals)) if np.size(sr_vals) else 0.0
        unit = _resolve_unit(unittext, unittextmap, idx)
        channel_id = f"{file_stem}_ch{idx+1}_{_sanitize_label(label)}"
        channel_list.append(
            ChannelData(
                participant_id=participant,
                channel_id=channel_id,
                label=label,
                data=signal.astype(float),
                samplerate=sr,
                unit=unit,
                file_source=path,
                starts=starts,
                ends=ends,
            )
        )
    return channel_list


