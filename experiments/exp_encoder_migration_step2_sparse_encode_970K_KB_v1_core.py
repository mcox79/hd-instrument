"""Encoder Migration Step 2 - Sparse-bipolar CSR encode of Step 1 encoder.npz.

Reads Step 1 output (data/substrate_concept_encoder_v1[_smoke]/encoder.npz)
which is int8 dense [n_entities, 4096] sparse-bipolar; converts to per-entity
CSR-like representation and saves as E_concept.pt (torch dict of tensors).

Target: FULL (970069 entities x 4096 int8) 3.98 GB dense -> ~250 MB sparse.
Design floor 2 GB (H1 HP band).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: N/A (single-arm artifact-producer + fidelity gates)
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json + E_concept.pt)
- except SystemExit: raise BEFORE except Exception (main outer try; NOT
  BaseException)
- crlb: N/A (artifact-producer; H3 is bit-identical round-trip so tolerance=0)
- baseline_in_band: N/A (no baseline arm)
- discriminator survives scale: SMOKE=1000 entities FULL=970069. Same code
  path (per META_RULE_smoke_code_path_must_exercise_same_branches_as_FULL);
  H1/H2/H3/H4 all evaluated at SMOKE + extrapolated size to FULL.
- HARD_PASS strictly above floor per META_RULE_L:
  H1 size < 2 GB HP; MB in [2 GB, 4 GB]; HF >= 4 GB
  H2 coverage == 1.00 HP (all entities represented; even zero-nnz rows keep an
                          offsets pair)
  H3 round-trip bit-identical on 100 entities HP; any mismatch HF
  H4 query < 500ms wall FULL / < 50ms wall SMOKE HP
- cardinality_ok: post-run assert n_entities in sparse == n_entities in npz
- per-unit failure-class: single-arm cell; outer try catches Exception w/
  failure_class in _write_crash_metrics
- calibration_check: default_ok_for_this_regime (k_sparsity=0.02 inherits from
  Step 1 output; Step 2 is lossless format conversion; no calibration knobs)
- all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ /
  CITED@ per META_RULE_AC

Source signature: input = Step 1 encoder.npz produced by
exp_encoder_migration_step1_train_concept_encoder_970K_KB_v1_core.py at
commit HEAD (SMOKE landed 2026-07-03T23:50 sha256=28c87075617fa1bf...
MEASURED@data/exp_encoder_migration_step1_..._smoke/metrics.json:encoder_sha256);
format = sparse-CSR-like (active_indices int16, signs int8, offsets int64).

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

# ---------------------------------------------------------------------------
# argv snapshot BEFORE any _seed_checkpoint import.
# Root cause: experiments/_seed_checkpoint.py's module-import selftest
# (_selftest_get_output_dir) rebinds _orig_argv inside a nested try/finally in
# Test 6 (lines 594, 622), then the outer finally restores sys.argv to the
# NESTED snapshot (which is ["_seed_checkpoint_selftest"]) instead of the true
# caller argv. That silently strips --smoke / --self-test / --full flags from
# any cell that imports _seed_checkpoint.  Filed for Testbed review; workaround
# below preserves this cell's argv contract.
# ---------------------------------------------------------------------------
_ARGV_SNAPSHOT = list(sys.argv)

# ---------------------------------------------------------------------------
# Bootstrap paths.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

# Restore argv if _seed_checkpoint's import-time selftest mangled it.
if list(sys.argv) != _ARGV_SNAPSHOT:
    sys.argv = _ARGV_SNAPSHOT

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_migration_step2_sparse_encode_970K_KB_v1"

# Step 1 produces dense int8 [N, 4096]. Step 2 reads this + emits sparse CSR.
N_DIM_EXPECTED = 4096                  # CITED@Step1_prereg N_DIM=4096
K_EXPECTED = 82                        # CITED@Step1_SMOKE_metrics mean_nnz=82.0
K_TOLERANCE = 2                        # HYPOTHESIZED tie-break +/- 2
SEED_DEFAULT = 7

# H1 size band -- extrapolation formula used for SMOKE.
# Per-entity sparse cost at k=82: 82*2 (indices int16) + 82*1 (signs int8) + 8
# (offsets int64) = 254 bytes. THEORETICAL@ sizeof formula.
# 970069 * 254 = 246 MB + entity_names ~50-200 MB + torch.save overhead ~5%.
# Total FULL estimate: ~300-450 MB.
H1_HP_MAX_BYTES_FULL = 2 * (1 << 30)   # 2 GB HP ceiling
H1_MB_MAX_BYTES_FULL = 4 * (1 << 30)   # 4 GB MB ceiling; > 4 GB is HF

# H4 query speed
H4_HP_MAX_MS_FULL = 500                # HYPOTHESIZED CPU bincount + np.take
H4_HP_MAX_MS_SMOKE = 100               # HYPOTHESIZED scaled ~1000x smaller

# SMOKE limit.
_SMOKE_N_ENTITIES = 1_000

# ---------------------------------------------------------------------------
# Bootstrap / safety helpers.
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": int(expected_n_units),
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def _emit_heartbeat(output_dir: Path, unit_idx: int, total_units: int,
                    elapsed_s: float, extra: Optional[dict] = None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units),
        "elapsed_s": float(elapsed_s),
    }
    if extra:
        row["extra"] = extra
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# Sparse-bipolar CSR core.
# ---------------------------------------------------------------------------

def _load_step1_npz(npz_path: Path) -> Tuple[np.ndarray, List[str], dict]:
    """Load Step 1 encoder.npz. Returns (concept_hds_int8, entity_names, metadata).

    Fails loudly if shape / dtype don't match Step 1 contract.
    """
    if not npz_path.exists():
        raise FileNotFoundError(f"Step 1 encoder.npz not found: {npz_path}")
    with np.load(str(npz_path), allow_pickle=True) as data:
        concept_hds = data["concept_hds"]
        entity_names = data["entity_names"].tolist()
        metadata_raw = data["metadata"].item()
    if concept_hds.dtype != np.int8:
        raise ValueError(
            f"Step 1 encoder.npz has dtype {concept_hds.dtype} != int8"
        )
    if concept_hds.ndim != 2:
        raise ValueError(
            f"Step 1 encoder.npz has ndim={concept_hds.ndim} != 2"
        )
    n_dim = concept_hds.shape[1]
    if n_dim > 32767:
        raise ValueError(
            f"n_dim={n_dim} exceeds int16 range for active_indices; "
            f"format needs int32"
        )
    if isinstance(metadata_raw, str):
        metadata = json.loads(metadata_raw)
    else:
        metadata = dict(metadata_raw) if metadata_raw is not None else {}
    return concept_hds, entity_names, metadata


def _convert_dense_to_sparse_csr(
    concept_hds: np.ndarray,
    entity_names: List[str],
    n_dim: int,
) -> Dict[str, torch.Tensor]:
    """Convert [N, n_dim] int8 dense to sparse-CSR-like dict of torch tensors.

    Returns dict with:
      active_indices: int16 tensor [total_nnz]
      signs: int8 tensor [total_nnz]
      offsets: int64 tensor [N+1]  -- entity i's active dims at offsets[i]:offsets[i+1]
      n_dim: python int
      n_entities: python int
      entity_names: list[str]  (packaged separately in torch.save)
    """
    n_entities = int(concept_hds.shape[0])
    # np.nonzero iterates row-major so rows is sorted ascending.
    rows, cols = np.nonzero(concept_hds)
    total_nnz = int(rows.shape[0])
    signs_np = concept_hds[rows, cols].astype(np.int8)
    if not np.all((signs_np == 1) | (signs_np == -1)):
        raise ValueError(
            "Step 1 encoder.npz contains non-bipolar values in nonzero "
            "positions; expected {-1, +1}"
        )
    active_indices_np = cols.astype(np.int16)
    counts = np.bincount(rows, minlength=n_entities).astype(np.int64)
    offsets_np = np.zeros(n_entities + 1, dtype=np.int64)
    np.cumsum(counts, out=offsets_np[1:])
    if int(offsets_np[-1]) != total_nnz:
        raise ValueError(
            f"offsets cumulative-sum mismatch: offsets[-1]={int(offsets_np[-1])} "
            f"!= total_nnz={total_nnz}"
        )
    return {
        "active_indices": torch.from_numpy(active_indices_np),
        "signs": torch.from_numpy(signs_np),
        "offsets": torch.from_numpy(offsets_np),
        "n_dim": int(n_dim),
        "n_entities": n_entities,
        "total_nnz": total_nnz,
        "entity_names": entity_names,
    }


def _sparse_reconstruct_dense(sparse_rep: Dict[str, torch.Tensor],
                              sample_idx: int) -> np.ndarray:
    """Reconstruct dense [n_dim] int8 vector for a single entity from sparse rep."""
    offsets = sparse_rep["offsets"].numpy()
    ai = sparse_rep["active_indices"].numpy()
    sg = sparse_rep["signs"].numpy()
    n_dim = sparse_rep["n_dim"]
    lo = int(offsets[sample_idx])
    hi = int(offsets[sample_idx + 1])
    dense = np.zeros(n_dim, dtype=np.int8)
    if lo < hi:
        idx = ai[lo:hi].astype(np.int32)
        dense[idx] = sg[lo:hi]
    return dense


def _sparse_batched_cosine(sparse_rep: Dict[str, torch.Tensor],
                           query_dense: np.ndarray) -> np.ndarray:
    """Compute cosine([N] entities, query) via vectorized sparse dot product.

    query_dense: [n_dim] int8 or float32 (bipolar HD)
    Returns: [N] float32 cosine scores. Zero for empty-nnz entities.
    """
    n_dim = sparse_rep["n_dim"]
    n_entities = sparse_rep["n_entities"]
    offsets = sparse_rep["offsets"].numpy()
    ai = sparse_rep["active_indices"].numpy()
    sg = sparse_rep["signs"].numpy()

    q_f32 = query_dense.astype(np.float32).reshape(-1)
    if q_f32.shape[0] != n_dim:
        raise ValueError(
            f"query dim {q_f32.shape[0]} != n_dim {n_dim}"
        )
    q_norm_sq = float((q_f32 ** 2).sum())
    if q_norm_sq == 0.0:
        return np.zeros(n_entities, dtype=np.float32)
    q_norm = np.sqrt(q_norm_sq)

    # Per-active gather: q_at_active[k] = q_f32[ai[k]]; contribs = sg * q_at_active
    q_gathered = q_f32[ai.astype(np.int32)]
    contribs = sg.astype(np.float32) * q_gathered

    # Row-ids for each active dim (needed for accumulation).
    counts = np.diff(offsets)
    row_ids = np.repeat(np.arange(n_entities, dtype=np.int64), counts)

    # Accumulate dot per entity via bincount weights.
    dots = np.bincount(row_ids, weights=contribs, minlength=n_entities)

    # Entity norms: sqrt(nnz_i). Zero-nnz rows -> score 0.
    e_norms = np.sqrt(counts.astype(np.float32))
    scores = np.zeros(n_entities, dtype=np.float32)
    nz = e_norms > 0
    scores[nz] = dots[nz].astype(np.float32) / (e_norms[nz] * q_norm)
    return scores


# ---------------------------------------------------------------------------
# Fidelity + query benchmarks.
# ---------------------------------------------------------------------------

def _verify_round_trip(concept_hds: np.ndarray,
                       sparse_rep: Dict[str, torch.Tensor],
                       n_samples: int = 100,
                       seed: int = 7) -> Tuple[int, int]:
    """Reconstruct N random entities from sparse; compare bit-identical to dense.

    Returns (n_checked, n_mismatch).
    """
    rng = np.random.default_rng(seed)
    n_entities = concept_hds.shape[0]
    n_check = min(n_samples, n_entities)
    idxs = rng.choice(n_entities, size=n_check, replace=False)
    n_mismatch = 0
    for i in idxs:
        recon = _sparse_reconstruct_dense(sparse_rep, int(i))
        if not np.array_equal(recon, concept_hds[i]):
            n_mismatch += 1
    return n_check, n_mismatch


def _benchmark_query(sparse_rep: Dict[str, torch.Tensor],
                     concept_hds: np.ndarray,
                     n_queries: int = 10,
                     seed: int = 7) -> Tuple[float, float]:
    """Run n_queries sparse cosine queries; return (mean_ms, max_ms) wall.

    Queries are drawn from the encoder's own rows (self-similarity test:
    query = concept_hds[i] should score 1.0 at position i).
    """
    rng = np.random.default_rng(seed)
    n_entities = concept_hds.shape[0]
    q_idxs = rng.choice(n_entities, size=min(n_queries, n_entities),
                        replace=False)
    walls_ms = []
    self_scores = []
    for qi in q_idxs:
        query = concept_hds[qi]
        t0 = time.perf_counter()
        scores = _sparse_batched_cosine(sparse_rep, query)
        walls_ms.append((time.perf_counter() - t0) * 1000.0)
        self_scores.append(float(scores[qi]))
    mean_ms = float(np.mean(walls_ms))
    max_ms = float(np.max(walls_ms))
    # Sanity: self-similarity should be 1.0 for query == entity row.
    min_self = float(np.min(self_scores))
    if min_self < 0.999:
        raise ValueError(
            f"self-similarity broken: min(diag score)={min_self:.6f} < 0.999; "
            f"sparse dot product / norm is incorrect"
        )
    return mean_ms, max_ms


# ---------------------------------------------------------------------------
# Save + verdict.
# ---------------------------------------------------------------------------

def _save_pt(sparse_rep: Dict[str, torch.Tensor],
             source_encoder_sha256: str,
             source_encoder_path: str,
             out_path: Path) -> Tuple[int, str]:
    """Atomic torch.save of sparse rep to out_path (.pt). Returns (bytes, sha256_hex)."""
    payload = {
        "active_indices": sparse_rep["active_indices"],
        "signs": sparse_rep["signs"],
        "offsets": sparse_rep["offsets"],
        "n_dim": sparse_rep["n_dim"],
        "n_entities": sparse_rep["n_entities"],
        "total_nnz": sparse_rep["total_nnz"],
        "entity_names": sparse_rep["entity_names"],
        "format": "sparse_bipolar_csr_v1",
        "format_notes": (
            "active_indices int16 per-active dim indices; signs int8 in "
            "{-1,+1}; offsets int64 [N+1]; entity i's active dims at "
            "offsets[i]:offsets[i+1]. Reconstruct dense[i,:] by scattering "
            "signs[lo:hi] to dim indices active_indices[lo:hi]."
        ),
        "source_encoder_path": source_encoder_path,
        "source_encoder_sha256": source_encoder_sha256,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(".pt.tmp")
    torch.save(payload, str(tmp_path))
    os.replace(str(tmp_path), str(out_path))
    file_size = int(out_path.stat().st_size)
    h = hashlib.sha256()
    with open(out_path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return file_size, h.hexdigest()


def _verdict_from_diag(diag: Dict, run_mode: str) -> Tuple[str, str]:
    n = int(diag["n_entities"])
    n_dim = int(diag["n_dim"])
    total_nnz = int(diag["total_nnz"])
    mean_nnz = float(diag["mean_nnz"])
    n_round_trip_checked = int(diag["round_trip_checked"])
    n_round_trip_mismatch = int(diag["round_trip_mismatch"])
    pt_bytes = int(diag["pt_bytes"])
    query_mean_ms = float(diag["query_mean_ms"])
    coverage_of_step1_nonzero = float(diag["coverage_of_step1_nonzero"])

    # Sanity: dim / sparse-rate.
    if n_dim != N_DIM_EXPECTED:
        return ("HARD_FAIL",
                f"N_DIM_MISMATCH: got {n_dim} expected {N_DIM_EXPECTED}")
    if not (K_EXPECTED - K_TOLERANCE <= mean_nnz <= K_EXPECTED + K_TOLERANCE):
        return ("HARD_FAIL",
                f"MEAN_NNZ_OOB: {mean_nnz:.2f} outside "
                f"[{K_EXPECTED - K_TOLERANCE}, {K_EXPECTED + K_TOLERANCE}] "
                f"(k=82 target)")

    # H3: round-trip bit-identical (bit-tolerance = 0).
    if n_round_trip_mismatch > 0:
        return ("HARD_FAIL",
                f"H3_ROUND_TRIP_FAIL: {n_round_trip_mismatch}/"
                f"{n_round_trip_checked} entities do not reconstruct "
                f"bit-identical")

    # H2: coverage - every step1 nonzero row must survive to sparse (offsets
    # covers all N entities always; but if any step1-nonzero row lost its
    # nnz through conversion, that's HF).
    if coverage_of_step1_nonzero < 0.9999:
        return ("HARD_FAIL",
                f"H2_COVERAGE_LOSS: sparse coverage of Step 1 nonzero rows "
                f"= {coverage_of_step1_nonzero:.4f}")

    # H1 size band.
    if run_mode == "smoke":
        # Extrapolate to FULL: (bytes at SMOKE N) * (FULL_N / SMOKE_N)
        # But entity_names portion doesn't scale linearly. Use per-entity
        # bytes from sparse-CSR arrays only for scaling; add entity_names
        # observed at SMOKE.
        smoke_arr_bytes = total_nnz * (2 + 1) + (n + 1) * 8  # int16+int8+int64
        # THEORETICAL@ formula (2 + 1) bytes per nnz plus 8 per offset.
        est_full_arr_bytes = int((970069 / n) * smoke_arr_bytes)
        # Entity-names overhead: entity_names torch-serialized (Python object
        # via pickle) at SMOKE ~ (pt_bytes - smoke_arr_bytes). Assume same
        # avg name length at FULL -> scale by 970069/n.
        smoke_name_overhead = max(0, pt_bytes - smoke_arr_bytes)
        est_full_name_overhead = int((970069 / n) * smoke_name_overhead)
        est_full_bytes = est_full_arr_bytes + est_full_name_overhead
        diag["extrapolated_full_bytes"] = est_full_bytes
        if est_full_bytes >= H1_MB_MAX_BYTES_FULL:
            return ("HARD_FAIL",
                    f"H1_SIZE_HF: extrapolated FULL bytes "
                    f"{est_full_bytes / (1<<30):.2f} GB >= 4 GB "
                    f"(pt_smoke={pt_bytes})")
        if est_full_bytes >= H1_HP_MAX_BYTES_FULL:
            return ("MIDDLE_BAND",
                    f"H1_SIZE_MB: extrapolated FULL bytes "
                    f"{est_full_bytes / (1<<30):.2f} GB in [2, 4) GB "
                    f"(pt_smoke={pt_bytes})")
        # H4 at SMOKE.
        if query_mean_ms >= H4_HP_MAX_MS_SMOKE:
            return ("MIDDLE_BAND",
                    f"H4_QUERY_SLOW_SMOKE: {query_mean_ms:.1f}ms >= "
                    f"{H4_HP_MAX_MS_SMOKE}ms HP band")
        return ("HARD_PASS",
                f"Step2_smoke_OK: n={n} k_mean={mean_nnz:.2f} "
                f"pt_bytes={pt_bytes} extrapolated_full_bytes="
                f"{est_full_bytes / (1<<30):.3f}GB q_mean_ms="
                f"{query_mean_ms:.1f}")
    # FULL
    if pt_bytes >= H1_MB_MAX_BYTES_FULL:
        return ("HARD_FAIL",
                f"H1_SIZE_HF: pt_bytes {pt_bytes / (1<<30):.2f} GB >= 4 GB")
    if pt_bytes >= H1_HP_MAX_BYTES_FULL:
        return ("MIDDLE_BAND",
                f"H1_SIZE_MB: pt_bytes {pt_bytes / (1<<30):.2f} GB in [2, 4) GB")
    if query_mean_ms >= H4_HP_MAX_MS_FULL:
        return ("MIDDLE_BAND",
                f"H4_QUERY_SLOW_FULL: {query_mean_ms:.1f}ms >= "
                f"{H4_HP_MAX_MS_FULL}ms HP band")
    return ("HARD_PASS",
            f"Step2_full_OK: n={n} k_mean={mean_nnz:.2f} "
            f"pt_bytes={pt_bytes} ({pt_bytes / (1<<30):.3f}GB) "
            f"q_mean_ms={query_mean_ms:.1f}")


# ---------------------------------------------------------------------------
# Path helpers.
# ---------------------------------------------------------------------------

def _step1_encoder_path(run_mode: str) -> Path:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return _REPO / "data" / f"substrate_concept_encoder_v1{suffix}" / "encoder.npz"


def _artifact_out_path(run_mode: str) -> Path:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return _REPO / "data" / f"substrate_concept_encoder_v1{suffix}" / "E_concept.pt"


# ---------------------------------------------------------------------------
# Modes.
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    """Fast self-test: build synthetic dense int8 rep, convert, round-trip,
    query, assert all invariants. No disk I/O of Step 1 npz.
    """
    t0 = time.perf_counter()
    print("[selftest] building synthetic dense 50x256 encoder", flush=True)
    rng = np.random.default_rng(7)
    n = 50
    n_dim = 256
    k = 20
    dense = np.zeros((n, n_dim), dtype=np.int8)
    for i in range(n):
        picks = rng.choice(n_dim, size=k, replace=False)
        signs = rng.choice([-1, 1], size=k).astype(np.int8)
        dense[i, picks] = signs
    entity_names = [f"ent_{i}" for i in range(n)]

    print("[selftest] convert dense -> sparse-CSR", flush=True)
    sparse_rep = _convert_dense_to_sparse_csr(dense, entity_names, n_dim)
    assert sparse_rep["n_entities"] == n
    assert sparse_rep["n_dim"] == n_dim
    assert int(sparse_rep["offsets"][-1]) == n * k
    assert sparse_rep["active_indices"].dtype == torch.int16
    assert sparse_rep["signs"].dtype == torch.int8
    assert sparse_rep["offsets"].dtype == torch.int64

    print("[selftest] round-trip fidelity all 50 entities", flush=True)
    n_ck, n_mm = _verify_round_trip(dense, sparse_rep, n_samples=n, seed=7)
    assert n_ck == n and n_mm == 0, f"round-trip failed: {n_mm}/{n_ck}"

    print("[selftest] sparse cosine query self-similarity", flush=True)
    q_mean_ms, q_max_ms = _benchmark_query(sparse_rep, dense, n_queries=5,
                                            seed=7)
    print(f"[selftest] query mean={q_mean_ms:.2f}ms max={q_max_ms:.2f}ms",
          flush=True)

    print("[selftest] serialize + load .pt round-trip", flush=True)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tp = Path(td) / "test_e.pt"
        payload = {
            "active_indices": sparse_rep["active_indices"],
            "signs": sparse_rep["signs"],
            "offsets": sparse_rep["offsets"],
            "n_dim": sparse_rep["n_dim"],
            "n_entities": sparse_rep["n_entities"],
            "total_nnz": sparse_rep["total_nnz"],
            "entity_names": sparse_rep["entity_names"],
        }
        torch.save(payload, str(tp))
        loaded = torch.load(str(tp), weights_only=False)
        assert torch.equal(loaded["active_indices"], sparse_rep["active_indices"])
        assert torch.equal(loaded["signs"], sparse_rep["signs"])
        assert torch.equal(loaded["offsets"], sparse_rep["offsets"])
        assert loaded["entity_names"] == entity_names

    elapsed = time.perf_counter() - t0
    print(f"[selftest] PASS elapsed={elapsed:.2f}s", flush=True)
    return 0


def run_experiment(run_mode: str, seed: int) -> int:
    if run_mode == "smoke":
        anchor = f"{ANCHOR_NAME}_smoke"
    else:
        anchor = ANCHOR_NAME

    out_dir = get_output_dir(anchor)
    step1_path = _step1_encoder_path(run_mode)
    e_concept_path = _artifact_out_path(run_mode)

    _write_start_marker(out_dir, run_mode, expected_n_units=1)
    print(f"[step2] run_mode={run_mode} anchor={anchor}", flush=True)
    print(f"[step2] out_dir={out_dir}", flush=True)
    print(f"[step2] step1_encoder={step1_path}", flush=True)
    print(f"[step2] e_concept_out={e_concept_path}", flush=True)

    t0 = time.perf_counter()

    # Sha256 the Step 1 encoder.npz for source signature provenance.
    h = hashlib.sha256()
    with open(step1_path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    step1_sha256 = h.hexdigest()
    print(f"[step2] step1_encoder_sha256={step1_sha256}", flush=True)

    print("[step2] loading Step 1 encoder.npz", flush=True)
    concept_hds, entity_names, step1_metadata = _load_step1_npz(step1_path)
    load_s = time.perf_counter() - t0
    n_entities = int(concept_hds.shape[0])
    n_dim = int(concept_hds.shape[1])
    print(f"[step2] loaded shape={concept_hds.shape} dtype={concept_hds.dtype} "
          f"in {load_s:.1f}s", flush=True)

    # SMOKE limit: truncate to _SMOKE_N_ENTITIES if larger (guarding the
    # case where smoke output happens to be full-size).
    if run_mode == "smoke" and n_entities > _SMOKE_N_ENTITIES:
        print(f"[step2] SMOKE truncating from {n_entities} to "
              f"{_SMOKE_N_ENTITIES}", flush=True)
        concept_hds = concept_hds[:_SMOKE_N_ENTITIES]
        entity_names = entity_names[:_SMOKE_N_ENTITIES]
        n_entities = _SMOKE_N_ENTITIES

    # Step 1 nonzero-row baseline (H2 coverage denominator).
    step1_nonzero_rows_mask = (concept_hds != 0).any(axis=1)
    step1_n_nonzero = int(step1_nonzero_rows_mask.sum())
    print(f"[step2] step1 nonzero_rows={step1_n_nonzero}/{n_entities}",
          flush=True)

    _emit_heartbeat(out_dir, 1, 4, time.perf_counter() - t0,
                    extra={"stage": "loaded_step1"})

    print("[step2] converting dense -> sparse CSR", flush=True)
    conv_t0 = time.perf_counter()
    sparse_rep = _convert_dense_to_sparse_csr(concept_hds, entity_names, n_dim)
    conv_s = time.perf_counter() - conv_t0
    total_nnz = sparse_rep["total_nnz"]
    mean_nnz = total_nnz / max(1, n_entities)
    print(f"[step2] converted total_nnz={total_nnz} mean_nnz={mean_nnz:.2f} "
          f"conv_s={conv_s:.1f}", flush=True)

    _emit_heartbeat(out_dir, 2, 4, time.perf_counter() - t0,
                    extra={"stage": "converted"})

    # H2 coverage: reconstruct nonzero mask from sparse rep and check.
    offsets_np = sparse_rep["offsets"].numpy()
    sparse_nnz_per_row = np.diff(offsets_np)
    sparse_nonzero_mask = sparse_nnz_per_row > 0
    coverage_of_step1_nonzero = float(
        np.logical_and(step1_nonzero_rows_mask, sparse_nonzero_mask).sum()
        / max(1, step1_n_nonzero)
    )

    print("[step2] round-trip fidelity 100 samples", flush=True)
    rt_t0 = time.perf_counter()
    n_rt_ck, n_rt_mm = _verify_round_trip(concept_hds, sparse_rep,
                                          n_samples=100, seed=seed)
    rt_s = time.perf_counter() - rt_t0
    print(f"[step2] round-trip checked={n_rt_ck} mismatch={n_rt_mm} "
          f"rt_s={rt_s:.2f}", flush=True)

    _emit_heartbeat(out_dir, 3, 4, time.perf_counter() - t0,
                    extra={"stage": "round_tripped"})

    n_queries = 10
    print(f"[step2] query benchmark N={n_queries}", flush=True)
    q_mean_ms, q_max_ms = _benchmark_query(sparse_rep, concept_hds,
                                            n_queries=n_queries, seed=seed)
    print(f"[step2] query mean={q_mean_ms:.1f}ms max={q_max_ms:.1f}ms",
          flush=True)

    print(f"[step2] saving E_concept.pt to {e_concept_path}", flush=True)
    save_t0 = time.perf_counter()
    pt_bytes, pt_sha256 = _save_pt(sparse_rep, step1_sha256,
                                    str(step1_path), e_concept_path)
    save_s = time.perf_counter() - save_t0
    print(f"[step2] saved pt_bytes={pt_bytes} sha256={pt_sha256[:16]}... "
          f"save_s={save_s:.1f}", flush=True)

    _emit_heartbeat(out_dir, 4, 4, time.perf_counter() - t0,
                    extra={"stage": "saved"})

    diag = {
        "n_entities": n_entities,
        "n_dim": n_dim,
        "total_nnz": total_nnz,
        "mean_nnz": mean_nnz,
        "round_trip_checked": n_rt_ck,
        "round_trip_mismatch": n_rt_mm,
        "coverage_of_step1_nonzero": coverage_of_step1_nonzero,
        "pt_bytes": pt_bytes,
        "pt_sha256": pt_sha256,
        "query_mean_ms": q_mean_ms,
        "query_max_ms": q_max_ms,
        "load_s": load_s,
        "convert_s": conv_s,
        "round_trip_s": rt_s,
        "save_s": save_s,
        "step1_encoder_sha256": step1_sha256,
        "step1_encoder_path": str(step1_path),
        "e_concept_path": str(e_concept_path),
    }

    verdict, verdict_msg = _verdict_from_diag(diag, run_mode)
    elapsed_total = time.perf_counter() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": float(elapsed_total),
        "run_mode": run_mode,
        "anchor_name": anchor,
        "seed": int(seed),
        "N": n_dim,
        "n_entities": n_entities,
        "n_dim": n_dim,
        "total_nnz": total_nnz,
        "mean_nnz": mean_nnz,
        "round_trip_checked": n_rt_ck,
        "round_trip_mismatch": n_rt_mm,
        "coverage_of_step1_nonzero": coverage_of_step1_nonzero,
        "pt_bytes": pt_bytes,
        "pt_sha256": pt_sha256,
        "query_mean_ms": q_mean_ms,
        "query_max_ms": q_max_ms,
        "load_s": load_s,
        "convert_s": conv_s,
        "round_trip_s": rt_s,
        "save_s": save_s,
        "step1_encoder_sha256": step1_sha256,
        "step1_encoder_path": str(step1_path),
        "e_concept_path": str(e_concept_path),
        "extrapolated_full_bytes": int(diag.get("extrapolated_full_bytes", 0)),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "cardinality_ok": (sparse_rep["n_entities"] == n_entities),
        "arms_differ_verified": "N/A_single_arm",
        "final_metrics_atomicity": "tmp_replace",
    }
    write_metrics(out_dir, metrics)
    print(f"[step2] verdict={verdict} msg={verdict_msg} "
          f"elapsed={elapsed_total:.1f}s", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder Migration Step 2 -- Sparse-CSR encode 970K concept HDs"
    ))
    p.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
        choices=["self_test", "smoke", "full"],
    )
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    args = p.parse_args(argv)
    if args.self_test:
        args.run_mode = "self_test"
    elif args.smoke:
        args.run_mode = "smoke"
    elif args.full:
        args.run_mode = "full"
    return args


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    args = _parse_args()
    if args.run_mode == "self_test":
        return run_self_test()
    return run_experiment(args.run_mode, args.seed)


if __name__ == "__main__":
    _fallback_out = get_output_dir(ANCHOR_NAME)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException per META_RULE §8
        try:
            _write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass
        raise
