"""Persistence helpers for SubstrateMemory state.

Layout under testbed_data/substrate_state/<config_name>/:
  W.npy             - float32 weight matrix, shape (N, N)
  codebook.npy      - float32 codebook, shape (C, N)
  key_registry.json - dict mapping key_id -> codebook row index (int)
  value_registry.json - dict mapping key_id -> (value_str, value_atom_row_index)
  config.yaml       - dict of init kwargs serialized as YAML

W is loaded back as np.memmap so reload is O(file open). Materialize a copy via
np.array(memmap) when edit/delete are needed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def save_W(W: np.ndarray, path: Path) -> None:
    """Persist W as a .npy file. Caller passes the full file path (W.npy)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, W.astype(np.float32, copy=False))


def load_W_memmap(path: Path) -> np.memmap:
    """Open W.npy as a read-only memmap. Cheap reload at scale.

    np.load with mmap_mode='r' returns a memmap-backed ndarray.
    """
    path = Path(path)
    arr = np.load(path, mmap_mode="r")
    return arr


def save_registry(registry: dict, path: Path) -> None:
    """Write a JSON-serializable dict (key_registry or value_registry)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, sort_keys=True)


def load_registry(path: Path) -> dict:
    """Read a JSON-serialized dict."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict, path: Path) -> None:
    """Serialize an init-kwargs dict.

    Stored as JSON for zero-dependency robustness (yaml-compatible subset for the
    flat key/scalar configs this testbed uses). File suffix is preserved as-is.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_jsonify(config), f, indent=2, sort_keys=True)


def load_config(path: Path) -> dict:
    """Read an init-kwargs dict from disk."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _jsonify(obj: Any) -> Any:
    """Coerce non-JSON-safe scalars (numpy / Path) to JSON primitives."""
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    return obj


if __name__ == "__main__":
    import gc
    import shutil
    import tempfile
    td_path = Path(tempfile.mkdtemp())
    try:
        W = np.random.randn(16, 16).astype(np.float32)
        save_W(W, td_path / "W.npy")
        W2 = load_W_memmap(td_path / "W.npy")
        assert W2.shape == (16, 16) and W2.dtype == np.float32
        assert np.allclose(np.array(W2), W)
        save_registry({"a": 0, "b": 1}, td_path / "key_registry.json")
        reg = load_registry(td_path / "key_registry.json")
        assert reg == {"a": 0, "b": 1}
        save_config({"N": 128, "kind": "bsc"}, td_path / "config.yaml")
        cfg = load_config(td_path / "config.yaml")
        assert cfg["N"] == 128 and cfg["kind"] == "bsc"
        # Release the memmap before cleanup (Windows holds file lock otherwise).
        del W2
        gc.collect()
    finally:
        shutil.rmtree(td_path, ignore_errors=True)
    print("persistence self-test OK")
