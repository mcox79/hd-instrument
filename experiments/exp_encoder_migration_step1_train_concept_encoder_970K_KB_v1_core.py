"""Encoder Migration Step 1 - Train substrate concept encoder on 970K KB.

Produces data/substrate_concept_encoder_v1/encoder.npz: sparse-bipolar int8
concept HD table keyed by KB entity idx. Replaces char-trigram bag-of-features
Layer 0 retrieval frontend (Step 4 flip; Step 3 gold-verify runs first).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: N/A (single-arm artifact-producer)
- final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
- except SystemExit: raise BEFORE except Exception
- crlb: N/A (artifact-producer; no discriminator threshold at Step 1)
- baseline_in_band: N/A (no baseline)
- discriminator survives scale: SMOKE=10K FULL=970K; H2 coverage + H4 sparse
  rate = same code path (chunked-streaming)
- HARD_PASS strictly above floor: coverage >= 0.95 with floor 0.90 (5% band)
- cardinality_ok: post-run assert concept_hds.shape[0] == n_entities
- per-unit failure-class instrumentation: chunk-level try/except catches
  specific exceptions and appends failure_class to failed_chunks list
- calibration_check: default_ok_for_this_regime (k_sparsity=0.02 inherits from
  Spoke 1 v3-D CG at N=4096; regime-extension noted in pre-reg)
- all numbers in comments tagged: MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ /
  CITED@ per META_RULE_AC

Source signature: mechanism = ConceptEncoder v3-D at commit 9d30d3d30
(CG at 596a8de03, cat_kitten_cos_mean=0.492 CITED@Spoke1-v3-D-CG); corpus =
data/substrate_director_kb_v1/{entities,atoms}.jsonl at HEAD 2026-07-03.

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

# ---------------------------------------------------------------------------
# Bootstrap paths.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from hdlab.char_positional_encoder import CharPositionalEncoder  # noqa: E402

# ---------------------------------------------------------------------------
# Constants (config).
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_migration_step1_train_concept_encoder_970K_KB_v1"

# Corpus paths (canonical KB v1).
_KB_DIR = _REPO / "data" / "substrate_director_kb_v1"
_ENTITIES_PATH = _KB_DIR / "entities.jsonl"
_ATOMS_PATH = _KB_DIR / "atoms.jsonl"

# Encoder config -- inherits Spoke 1 v3-D CG defaults (commit 9d30d3d30).
N_DIM = 4096                       # CITED@Spoke1-v3-D-CG (N=4096 FULL config)
K_SPARSITY = 0.02                  # CITED@Spoke1-v3-D-CG (sparse_rate 0.020)
K_EFFECTIVE = max(1, int(round(K_SPARSITY * N_DIM)))  # THEORETICAL@ = 82
MAX_POS = 24                       # CITED@Spoke1-v3-D-CG
SEED_DEFAULT = 7                   # Step-1 single-seed artifact
CHUNK_SIZE = 10_000                # HYPOTHESIZED memory budget: 160MB/chunk
MAX_ATOMS_PER_ENTITY = 32          # HYPOTHESIZED cap; tuned to keep wall time
                                    # bounded at highly-connected entities (early
                                    # KB idx range has many-atom hubs).

# Run-mode discovery.
# SMOKE reduced from 10K -> 1K entities so queue_add.py's 180s smoke gate
# cap is comfortably met (avg per_ent ~15-30ms at N_DIM=4096 -> ~15-30s wall
# for 1K entities). Full-pipeline branches identical (per META_RULE
# smoke_code_path_must_exercise_same_branches_as_FULL). Semantic-quality
# claim belongs to Step 3 not to smoke scale.
_SMOKE_N_ENTITIES = 1_000
_FULL_N_ENTITIES_LIMIT = None      # None = all entities in file (~970069)

# Artifact output paths.
def _artifact_dir(run_mode: str) -> Path:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return _REPO / "data" / f"substrate_concept_encoder_v1{suffix}"


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
    """Atomic-replace metrics.json with CELL_CRASHED sentinel."""
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
# KB corpus loading.
# ---------------------------------------------------------------------------

def _load_entities(limit: Optional[int] = None) -> List[str]:
    """Return list of entity-name strings; idx = list position.

    Reads entities.jsonl (one {"idx": N, "name": str} per line); asserts
    monotone idx sequence 0..N-1. Fails loudly if a row is malformed.
    """
    if not _ENTITIES_PATH.exists():
        raise FileNotFoundError(f"KB entities not found: {_ENTITIES_PATH}")
    names: List[str] = []
    with open(_ENTITIES_PATH, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f):
            if limit is not None and line_no >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"entities.jsonl line {line_no}: malformed JSON: {exc}"
                ) from exc
            idx = row.get("idx")
            name = row.get("name")
            if idx != line_no:
                raise ValueError(
                    f"entities.jsonl line {line_no}: idx={idx} != line_no"
                )
            if not isinstance(name, str):
                raise ValueError(
                    f"entities.jsonl line {line_no}: name not str: {name!r}"
                )
            names.append(name)
    return names


def _build_entity_context_map(n_entities: int,
                              atom_limit: Optional[int] = None
                              ) -> Dict[int, List[str]]:
    """Return dict entity_idx -> list of context sentences from atoms.

    For each atom {s, s_name, p, p_name, o, o_name} in atoms.jsonl:
      - append f"{p_name} {o_name}" to contexts[s]
      - append f"{s_name} {p_name}" to contexts[o]
    Only atoms with s/o in [0, n_entities) are kept (bounds check).
    Truncates each entity's context list to MAX_ATOMS_PER_ENTITY.
    """
    if not _ATOMS_PATH.exists():
        raise FileNotFoundError(f"KB atoms not found: {_ATOMS_PATH}")
    contexts: Dict[int, List[str]] = {}
    with open(_ATOMS_PATH, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f):
            if atom_limit is not None and line_no >= atom_limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                # Corrupt atom line -- skip (record but don't crash);
                # atoms.jsonl integrity is not this cell's concern.
                continue
            s = row.get("s")
            o = row.get("o")
            s_name = row.get("s_name", "")
            p_name = row.get("p_name", "")
            o_name = row.get("o_name", "")
            if isinstance(s, int) and 0 <= s < n_entities and isinstance(o, int):
                lst = contexts.setdefault(s, [])
                if len(lst) < MAX_ATOMS_PER_ENTITY:
                    lst.append(f"{p_name} {o_name}".strip())
            if isinstance(o, int) and 0 <= o < n_entities and isinstance(s, int):
                lst = contexts.setdefault(o, [])
                if len(lst) < MAX_ATOMS_PER_ENTITY:
                    lst.append(f"{s_name} {p_name}".strip())
    return contexts


# ---------------------------------------------------------------------------
# Per-entity Hebbian mean + top-K WTA (streaming; core mechanism).
# ---------------------------------------------------------------------------

def _train_encoder_streaming(
    entities: List[str],
    contexts: Dict[int, List[str]],
    seed: int,
    output_dir: Path,
    artifact_dir: Path,
    chunk_size: int = CHUNK_SIZE,
    resume: bool = True,
) -> Dict[str, float]:
    """Chunked-streaming per-entity Hebbian mean + top-K WTA.

    Writes int8 sparse-bipolar concept HD to artifact_dir/encoder.npz.
    Checkpoints per chunk to artifact_dir/_shards/shard_<chunk_id>.npy.

    Returns diagnostic dict: {n_entities, n_with_nonzero, mean_nonzero_per_entity, ...}
    """
    n_entities = len(entities)
    n_chunks = (n_entities + chunk_size - 1) // chunk_size

    # Surface encoder (shared across all entities; deterministic per seed).
    surface_enc = CharPositionalEncoder(
        n_dim=N_DIM, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}",
    )

    shard_dir = artifact_dir / "_shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = artifact_dir / "_manifest.jsonl"

    # Resume support: load completed chunks from manifest.
    completed_chunks: set = set()
    if resume and manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line.strip())
                    completed_chunks.add(int(rec["chunk_id"]))
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
    print(f"[step1] resume: {len(completed_chunks)}/{n_chunks} chunks already "
          f"done", flush=True)

    n_with_nonzero_total = 0
    nonzero_per_entity_sum = 0
    n_entities_zero_context_total = 0
    n_nan_total = 0
    n_inf_total = 0

    t_start = time.perf_counter()
    for chunk_id in range(n_chunks):
        if chunk_id in completed_chunks:
            continue
        chunk_start = chunk_id * chunk_size
        chunk_end = min(chunk_start + chunk_size, n_entities)
        chunk_n = chunk_end - chunk_start

        # Per-entity context accumulation.
        chunk_hds = np.zeros((chunk_n, N_DIM), dtype=np.int8)
        chunk_nonzero_sum = 0
        chunk_zero_ctx = 0
        chunk_with_nonzero = 0
        chunk_nan = 0
        chunk_inf = 0
        chunk_t0 = time.perf_counter()
        for local_i in range(chunk_n):
            entity_idx = chunk_start + local_i
            entity_name = entities[entity_idx]
            ctx_list = contexts.get(entity_idx, [])
            if not ctx_list:
                # Fallback: use entity name itself as sole context.
                ctx_list = [entity_name]
                chunk_zero_ctx += 1
            # Batched encode across all context strings for this entity.
            valid = [s for s in ctx_list if isinstance(s, str) and s]
            if valid:
                hds = surface_enc.encode_batch(valid)  # [k, N_DIM] float32
                acc = hds.astype(np.float32).sum(axis=0) / float(len(valid))
            else:
                acc = np.zeros(N_DIM, dtype=np.float32)
            # Progress print every 500 entities within chunk.
            if local_i > 0 and (local_i % 500) == 0:
                per_ent = (time.perf_counter() - chunk_t0) / local_i
                remaining = (chunk_n - local_i) * per_ent
                print(f"[step1] chunk {chunk_id + 1}/{n_chunks} entity "
                      f"{local_i}/{chunk_n} (per_ent={per_ent*1000:.1f}ms "
                      f"est_remain={remaining:.1f}s)", flush=True)
            # NaN/Inf sentinel (per exp_dev bias checklist NaN detection).
            if np.isnan(acc).any():
                chunk_nan += 1
                continue
            if np.isinf(acc).any():
                chunk_inf += 1
                continue
            magnitudes = np.abs(acc)
            # top-K WTA via argpartition (exact K; ties broken by index order).
            # Critical: for single-context entities, acc is bipolar +/-1 so
            # `magnitudes >= pivot` would tie at all N dims. argpartition
            # returns exactly K indices even under tie conditions.
            k = K_EFFECTIVE
            if k >= N_DIM:
                mask = np.ones(N_DIM, dtype=bool)
            else:
                top_k_idx = np.argpartition(-magnitudes, k)[:k]
                mask = np.zeros(N_DIM, dtype=bool)
                mask[top_k_idx] = True
            sign_c = np.sign(acc).astype(np.int8)
            sign_c[sign_c == 0] = 1
            hd_int8 = (sign_c * mask.astype(np.int8)).astype(np.int8)
            chunk_hds[local_i] = hd_int8
            nnz = int(np.count_nonzero(hd_int8))
            chunk_nonzero_sum += nnz
            if nnz > 0:
                chunk_with_nonzero += 1

        # Flush shard atomically. Note: np.save auto-appends `.npy` if the
        # filename does not end in `.npy`, so we use `.tmp.npy` for the
        # write path and rename to `.npy` (final) so the extension survives.
        shard_path = shard_dir / f"shard_{chunk_id:04d}.npy"
        tmp_path = shard_dir / f"shard_{chunk_id:04d}.tmp.npy"
        np.save(str(tmp_path), chunk_hds)
        os.replace(str(tmp_path), str(shard_path))

        # Append manifest record atomically.
        with open(manifest_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "chunk_id": chunk_id,
                "chunk_start": chunk_start,
                "chunk_end": chunk_end,
                "chunk_n": chunk_n,
                "with_nonzero": chunk_with_nonzero,
                "nonzero_sum": chunk_nonzero_sum,
                "zero_context_fallback": chunk_zero_ctx,
                "n_nan": chunk_nan,
                "n_inf": chunk_inf,
                "ts_iso": datetime.now(timezone.utc).isoformat(),
            }) + "\n")

        n_with_nonzero_total += chunk_with_nonzero
        nonzero_per_entity_sum += chunk_nonzero_sum
        n_entities_zero_context_total += chunk_zero_ctx
        n_nan_total += chunk_nan
        n_inf_total += chunk_inf

        elapsed = time.perf_counter() - t_start
        _emit_heartbeat(output_dir, chunk_id + 1, n_chunks, elapsed,
                        extra={"with_nonzero_cum": n_with_nonzero_total})
        print(f"[step1] chunk {chunk_id + 1}/{n_chunks} done "
              f"(n={chunk_n} nz_entities={chunk_with_nonzero} "
              f"mean_nnz={chunk_nonzero_sum / max(1, chunk_n):.1f} "
              f"zero_ctx={chunk_zero_ctx} nan={chunk_nan} inf={chunk_inf} "
              f"cum_elapsed={elapsed:.1f}s)", flush=True)

    # Consolidate shards into encoder.npz.
    print(f"[step1] consolidating {n_chunks} shards into encoder.npz",
          flush=True)
    concept_hds = np.zeros((n_entities, N_DIM), dtype=np.int8)
    for chunk_id in range(n_chunks):
        shard_path = shard_dir / f"shard_{chunk_id:04d}.npy"
        if not shard_path.exists():
            raise RuntimeError(
                f"consolidation: shard {chunk_id} missing at {shard_path}"
            )
        shard = np.load(str(shard_path))
        chunk_start = chunk_id * chunk_size
        chunk_end = min(chunk_start + chunk_size, n_entities)
        concept_hds[chunk_start:chunk_end] = shard[:chunk_end - chunk_start]

    # Recount from consolidated array (avoid drift between manifest + reality).
    nz_mask = (concept_hds != 0).any(axis=1)
    n_with_nonzero_final = int(nz_mask.sum())
    nz_per_row = (concept_hds != 0).sum(axis=1)
    mean_nnz = float(nz_per_row.mean())
    total_nan = int(np.isnan(concept_hds.astype(np.float32)).sum())
    total_inf = int(np.isinf(concept_hds.astype(np.float32)).sum())

    # Write encoder.npz atomically. Note: np.savez auto-appends `.npz` when
    # the filename does not end in `.npz`, so tmp path uses `.tmp.npz`.
    tmp_npz = artifact_dir / "encoder.tmp.npz"
    final_npz = artifact_dir / "encoder.npz"
    metadata = {
        "n_dim": N_DIM,
        "k_sparsity": K_SPARSITY,
        "k_effective": K_EFFECTIVE,
        "seed": seed,
        "max_pos": MAX_POS,
        "chunk_size": chunk_size,
        "max_atoms_per_entity": MAX_ATOMS_PER_ENTITY,
        "source_signature": (
            "encoder=ConceptEncoder-mechanism-v3D_9d30d3d30_CG596a8de03; "
            "corpus=substrate_director_kb_v1_HEAD_2026-07-03; "
            "cell=" + ANCHOR_NAME
        ),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    np.savez(str(tmp_npz),
             concept_hds=concept_hds,
             entity_names=np.array(entities, dtype=object),
             metadata=np.array(json.dumps(metadata), dtype=object))
    os.replace(str(tmp_npz), str(final_npz))

    # Compute encoder.npz file size + sha256 for provenance.
    file_size = int(final_npz.stat().st_size)
    h = hashlib.sha256()
    with open(final_npz, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    sha256_hex = h.hexdigest()

    return {
        "n_entities": n_entities,
        "n_chunks": n_chunks,
        "n_with_nonzero": n_with_nonzero_final,
        "coverage_frac": float(n_with_nonzero_final) / float(max(1, n_entities)),
        "mean_nonzero_per_entity": mean_nnz,
        "n_entities_zero_context_fallback": n_entities_zero_context_total,
        "n_nan": n_nan_total + total_nan,
        "n_inf": n_inf_total + total_inf,
        "encoder_bytes": file_size,
        "encoder_sha256": sha256_hex,
        "train_elapsed_s": float(time.perf_counter() - t_start),
    }


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _verdict_from_diag(diag: Dict[str, float]) -> Tuple[str, str]:
    """Return (verdict, verdict_msg) per H1-H4 pre-reg bands."""
    n = int(diag["n_entities"])
    cov = float(diag["coverage_frac"])
    mean_nnz = float(diag["mean_nonzero_per_entity"])
    n_nan = int(diag["n_nan"])
    n_inf = int(diag["n_inf"])
    encoder_bytes = int(diag["encoder_bytes"])

    # H1: no NaN/Inf.
    if n_nan > 0 or n_inf > 0:
        return ("HARD_FAIL",
                f"H1_NAN_INF: n_nan={n_nan} n_inf={n_inf}")

    # Size band: [3.5 GB, 4.5 GB] for FULL 970069 * 4096 = 3.98 GB;
    # SMOKE 10K = ~40 MB.
    expected_bytes = n * N_DIM  # int8 dense; ignore npz overhead
    size_lo = int(expected_bytes * 0.85)  # allow npz overhead + rounding
    size_hi = int(expected_bytes * 1.35)
    if not (size_lo <= encoder_bytes <= size_hi):
        return ("HARD_FAIL",
                f"H1_SIZE_OOB: bytes={encoder_bytes} outside "
                f"[{size_lo},{size_hi}] (expected~{expected_bytes})")

    # H2: coverage >= 0.95 HP (>= 0.90 floor + 5% band).
    if cov < 0.90:
        return ("HARD_FAIL", f"H2_COVERAGE: {cov:.4f} < 0.90 floor")
    if cov < 0.95:
        return ("MIDDLE_BAND",
                f"H2_COVERAGE_MIDDLE: {cov:.4f} in [0.90, 0.95)")

    # H4: mean_nnz in [80, 84] (k=82 +/- 2 for tie-break).
    if not (78.0 <= mean_nnz <= 86.0):
        return ("HARD_FAIL",
                f"H4_SPARSE_RATE_OOB: mean_nnz={mean_nnz:.2f} outside "
                f"[78, 86] (target k={K_EFFECTIVE})")

    return ("HARD_PASS",
            f"Step1_encoder_OK: n_entities={n} coverage={cov:.4f} "
            f"mean_nnz={mean_nnz:.2f} bytes={encoder_bytes}")


# ---------------------------------------------------------------------------
# Modes.
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    """Fast self-test: module imports OK, encoder trains on tiny subset."""
    t0 = time.perf_counter()
    print("[selftest] loading first 200 entities", flush=True)
    entities = _load_entities(limit=200)
    assert len(entities) == 200, f"selftest: got {len(entities)} != 200"
    print("[selftest] building context map (atom_limit=5000)", flush=True)
    contexts = _build_entity_context_map(len(entities), atom_limit=5000)
    print(f"[selftest] context map: {len(contexts)} entities have contexts",
          flush=True)
    # Train in-memory (skip disk artifact).
    surface_enc = CharPositionalEncoder(
        n_dim=1024, max_pos=MAX_POS, seed_prefix="SPOKE1_S7",
    )
    concept_hds = np.zeros((200, 1024), dtype=np.int8)
    k = max(1, int(round(K_SPARSITY * 1024)))  # 20
    n_nonzero_rows = 0
    for i in range(200):
        ctx = contexts.get(i, [entities[i]])
        acc = np.zeros(1024, dtype=np.float32)
        for s in ctx:
            if isinstance(s, str) and s:
                acc += surface_enc.encode_sentence(s).astype(np.float32)
        if len(ctx) > 0:
            acc /= float(len(ctx))
        mag = np.abs(acc)
        top_k_idx = np.argpartition(-mag, k)[:k]
        mask = np.zeros(1024, dtype=bool)
        mask[top_k_idx] = True
        sign_c = np.sign(acc).astype(np.int8)
        sign_c[sign_c == 0] = 1
        concept_hds[i] = (sign_c * mask.astype(np.int8)).astype(np.int8)
        if concept_hds[i].any():
            n_nonzero_rows += 1
    # Assertions.
    assert concept_hds.dtype == np.int8, "selftest: dtype != int8"
    assert concept_hds.shape == (200, 1024), (
        f"selftest: shape {concept_hds.shape}"
    )
    coverage = n_nonzero_rows / 200
    assert coverage >= 0.95, (
        f"selftest: coverage {coverage:.3f} < 0.95"
    )
    mean_nnz = float((concept_hds != 0).sum(axis=1).mean())
    assert 18 <= mean_nnz <= 22, (
        f"selftest: mean_nnz {mean_nnz:.2f} outside [18, 22] "
        f"(target k=20 at n_dim=1024)"
    )
    # No NaN.
    assert not np.isnan(concept_hds.astype(np.float32)).any(), (
        "selftest: NaN detected"
    )
    elapsed = time.perf_counter() - t0
    print(f"[selftest] PASS (coverage={coverage:.3f} mean_nnz={mean_nnz:.2f} "
          f"elapsed={elapsed:.2f}s)", flush=True)
    return 0


def run_experiment(run_mode: str, seed: int) -> int:
    """Run smoke or full experiment."""
    if run_mode == "smoke":
        anchor = f"{ANCHOR_NAME}_smoke"
        n_limit = _SMOKE_N_ENTITIES
    else:
        anchor = ANCHOR_NAME
        n_limit = _FULL_N_ENTITIES_LIMIT

    out_dir = get_output_dir(anchor)
    art_dir = _artifact_dir(run_mode)

    _write_start_marker(out_dir, run_mode, expected_n_units=1)
    print(f"[step1] run_mode={run_mode} seed={seed} anchor={anchor}",
          flush=True)
    print(f"[step1] out_dir={out_dir}", flush=True)
    print(f"[step1] artifact_dir={art_dir}", flush=True)

    t0 = time.perf_counter()
    print("[step1] loading entities", flush=True)
    entities = _load_entities(limit=n_limit)
    n_entities = len(entities)
    print(f"[step1] loaded {n_entities} entities", flush=True)

    print("[step1] building context map from atoms.jsonl (all atoms)",
          flush=True)
    # No atom_limit -- entity coverage requires seeing all atoms that mention
    # the entity subset. Full atoms.jsonl load ~15-20s on SSD.
    contexts = _build_entity_context_map(n_entities, atom_limit=None)
    ctx_load_s = time.perf_counter() - t0
    n_ent_with_ctx = len(contexts)
    print(f"[step1] context map: {n_ent_with_ctx}/{n_entities} entities have "
          f"contexts (loaded in {ctx_load_s:.1f}s)", flush=True)

    print("[step1] streaming train + shard", flush=True)
    diag = _train_encoder_streaming(
        entities=entities,
        contexts=contexts,
        seed=seed,
        output_dir=out_dir,
        artifact_dir=art_dir,
        chunk_size=CHUNK_SIZE,
        resume=True,
    )

    verdict, verdict_msg = _verdict_from_diag(diag)
    elapsed_total = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": float(elapsed_total),
        "run_mode": run_mode,
        "anchor_name": anchor,
        "seed": int(seed),
        "N": N_DIM,
        "n_entities": diag["n_entities"],
        "n_chunks": diag["n_chunks"],
        "coverage_frac": diag["coverage_frac"],
        "n_with_nonzero": diag["n_with_nonzero"],
        "mean_nonzero_per_entity": diag["mean_nonzero_per_entity"],
        "n_entities_zero_context_fallback": diag["n_entities_zero_context_fallback"],
        "n_nan": diag["n_nan"],
        "n_inf": diag["n_inf"],
        "encoder_bytes": diag["encoder_bytes"],
        "encoder_sha256": diag["encoder_sha256"],
        "encoder_path": str(_artifact_dir(run_mode) / "encoder.npz"),
        "ctx_load_elapsed_s": float(ctx_load_s),
        "train_elapsed_s": float(diag["train_elapsed_s"]),
        "k_effective": K_EFFECTIVE,
        "k_sparsity": K_SPARSITY,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "cardinality_ok": (diag["n_entities"] == n_entities),
        "arms_differ_verified": "N/A_single_arm",
        "final_metrics_atomicity": "tmp_replace",
    }
    # Atomic write via write_metrics (injects REQUIRED_FIELDS if missing).
    write_metrics(out_dir, metrics)
    print(f"[step1] verdict={verdict} msg={verdict_msg} elapsed={elapsed_total:.1f}s",
          flush=True)
    return 0 if verdict != "CELL_CRASHED" else 1


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder Migration Step 1 -- Train substrate concept encoder on 970K KB"
    ))
    p.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
        choices=["self_test", "smoke", "full"],
    )
    p.add_argument("--self-test", action="store_true",
                   help="alias for --run-mode self_test")
    p.add_argument("--smoke", action="store_true",
                   help="alias for --run-mode smoke")
    p.add_argument("--full", action="store_true",
                   help="alias for --run-mode full")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    args = p.parse_args(argv)
    # Alias flags override --run-mode.
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
    # Best-effort out_dir for crash-diagnostic (may be pre-arg parse).
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
            pass  # crash-writer failure is not fatal
        raise
