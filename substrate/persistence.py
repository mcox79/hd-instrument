"""
substrate.persistence -- disk-backed substrate state.

Used by shards.py, inverted.py, kv_memory.py to persist numpy arrays + metadata.

Pattern:
    data/substrate_state/
        <shard_id>/
            vectors.npy       (float32 / complex64 codebook or memory matrix)
            metadata.json     (entity list, dimension, variant, last_update)

Vectors are saved with `np.save` (full file load) for now; switch to `np.memmap` in W2
if individual-shard memory pressure becomes an issue at 10M+ facts.
"""
from __future__ import annotations
import json
import shutil
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass
class ShardMetadata:
    shard_id: str
    dim: int
    variant: str                          # "phasor" or "bipolar"
    entity_list: list[str] = field(default_factory=list)  # ordered names; row N = entity_list[N]
    created_at: float = field(default_factory=time.time)
    last_update_at: float = 0.0
    fact_count: int = 0


def shard_dir(state_dir: Path, shard_id: str) -> Path:
    return state_dir / shard_id


def save_shard(state_dir: Path, shard_id: str, vectors: np.ndarray, metadata: ShardMetadata) -> None:
    d = shard_dir(state_dir, shard_id)
    d.mkdir(parents=True, exist_ok=True)
    metadata.last_update_at = time.time()
    np.save(d / "vectors.npy", vectors, allow_pickle=False)
    (d / "metadata.json").write_text(json.dumps(asdict(metadata), indent=2))


def load_shard(state_dir: Path, shard_id: str) -> Optional[tuple[np.ndarray, ShardMetadata]]:
    d = shard_dir(state_dir, shard_id)
    vec_path = d / "vectors.npy"
    meta_path = d / "metadata.json"
    if not (vec_path.exists() and meta_path.exists()):
        return None
    vectors = np.load(vec_path, allow_pickle=False)
    meta_d = json.loads(meta_path.read_text())
    return vectors, ShardMetadata(**meta_d)


def list_shards(state_dir: Path) -> list[str]:
    if not state_dir.exists():
        return []
    return sorted(p.name for p in state_dir.iterdir() if p.is_dir() and (p / "metadata.json").exists())


def delete_shard(state_dir: Path, shard_id: str) -> bool:
    d = shard_dir(state_dir, shard_id)
    if d.exists():
        shutil.rmtree(d)
        return True
    return False


def _self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        state = Path(tmp)
        vec = np.random.default_rng(0).standard_normal((4, 64)).astype(np.float32)
        meta = ShardMetadata(shard_id="alpha", dim=64, variant="phasor", entity_list=["a", "b", "c", "d"], fact_count=4)
        save_shard(state, "alpha", vec, meta)
        assert "alpha" in list_shards(state)
        result = load_shard(state, "alpha")
        assert result is not None
        loaded_vec, loaded_meta = result
        assert np.allclose(loaded_vec, vec)
        assert loaded_meta.entity_list == ["a", "b", "c", "d"]
        assert delete_shard(state, "alpha")
        assert "alpha" not in list_shards(state)
    print("[substrate.persistence] self-test PASS")


if __name__ == "__main__":
    _self_test()
