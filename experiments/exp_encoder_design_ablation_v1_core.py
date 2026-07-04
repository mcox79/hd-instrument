"""Concept-Encoder Design Ablation v1 -- sparsity x fidelity Pareto search.

Tests whether the Step-1 encoder's locked ~2%/[18,22] sparsity target is on the
(semantic fidelity, algebraic fidelity) Pareto frontier or dominated. Sweeps the
sparsity level (active nonzeros k) over the SAME Hebbian-context-mean acc and
measures BOTH axes per level on REAL KB concepts with BGE-large semantic gold.

Prereg: preregs/2026-07-04_exp_encoder_design_ablation_v1.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (sha256 of each int8 code table; 6 distinct)
- final_metrics_atomicity: tmp_replace (write_metrics -> atomic os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb: N/A design-search; only gate is discriminator-spread >= 0.05 (empirical)
- baseline_in_band: dense arm algebraic acc at reporting_M in (0.05, 0.95)
- discriminator survives scale: SMOKE=600 FULL=5000 concepts, same code path;
  discriminator = SPREAD across sparsity (code-family property, not concept count);
  3 role-seeds probe algebraic continuous-score variance in smoke
- calibration_check: adaptive_with_discriminator_gate (reporting_M adaptive)
- cardinality_ok: assert len(per_level) == len(K_LEVELS) == 6
- per-unit failure-class instrumentation: per-level try/except records failure_class
- all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Source signature: surface encoder = CharPositionalEncoder (hdlab); algebra =
hdlab.binding HRR bind/unbind (real input, circular convolution); corpus =
data/substrate_director_kb_v1 HEAD 2026-07-03; BGE gold = cached bge_large_v2_name
index (data/substrate_index/cached_indices). CITED@Step1-cell for encoder config.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import glob
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

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from hdlab.char_positional_encoder import CharPositionalEncoder  # noqa: E402
from hdlab import binding as hdbinding  # noqa: E402

import torch  # noqa: E402

# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_design_ablation_v1"

_KB_DIR = _REPO / "data" / "substrate_director_kb_v1"
_ENTITIES_PATH = _KB_DIR / "entities.jsonl"
_ATOMS_PATH = _KB_DIR / "atoms.jsonl"
_BGE_CACHE_GLOB = str(
    _REPO / "data" / "substrate_index" / "cached_indices" / "bge_large_v2_name_*.npz"
)

N_DIM = 1024                        # CITED@Step1-selftest (k=20 target regime)
MAX_POS = 24                        # CITED@Step1-cell
SEED_ENCODER = 7                    # deterministic encoder seed_prefix
MAX_ATOMS_PER_ENTITY = 32           # CITED@Step1-cell
SAMPLE_SEED = 20260704             # deterministic concept sample

# The load-bearing sweep axis: active nonzeros k (1024 = dense).
K_LEVELS = [8, 16, 20, 32, 64, 1024]   # brackets [18,22] both directions
EXPECTED_N_UNITS = len(K_LEVELS)       # cardinality gate (META_RULE_H)

# Fidelity params.
TOPK_NEIGHBORS = 10                 # semantic neighbor_recall@k
N_QUERY = 150                       # held-out query set size for both axes
ROLE_SEEDS = [11, 23, 41]           # multi-seed role randomness (algebraic)
M_GRID = [24, 40, 64, 96]           # bundle capacity pressure
N_TRIALS = 150                      # per (level, seed, M) cleanup trials

_SMOKE_N_CONCEPTS = 600
_FULL_N_CONCEPTS = 5000


def _artifact_anchor(run_mode: str) -> str:
    return ANCHOR_NAME + ("_smoke" if run_mode == "smoke" else "")


# ---------------------------------------------------------------------------
# Error-checking scaffold (per exp_dev.md section 13).
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, run_mode: str, n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": int(n_units),
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
# BGE cache loading.
# ---------------------------------------------------------------------------

def _load_bge_cache() -> Tuple[Dict[str, int], np.ndarray]:
    """Return (name -> row index, semantic embedding matrix [K, 1024]).

    Picks the cached bge_large_v2_name index with the largest coverage (most
    names) for determinism.
    """
    files = glob.glob(_BGE_CACHE_GLOB)
    if not files:
        raise FileNotFoundError(f"no BGE cache matching {_BGE_CACHE_GLOB}")
    best = None
    best_n = -1
    for fp in files:
        try:
            z = np.load(fp, allow_pickle=True)
            n = int(z["semantic"].shape[0])
        except Exception:
            continue
        if n > best_n:
            best_n = n
            best = fp
    if best is None:
        raise RuntimeError("no readable BGE cache npz")
    z = np.load(best, allow_pickle=True)
    sem = np.asarray(z["semantic"], dtype=np.float32)
    ids = json.loads(str(z["id_order_json"]))
    if len(ids) != sem.shape[0]:
        raise ValueError(
            f"BGE cache mismatch: {len(ids)} ids vs {sem.shape[0]} rows in {best}"
        )
    name_to_row = {str(nm): i for i, nm in enumerate(ids)}
    print(f"[ablation] BGE cache: {os.path.basename(best)} "
          f"({sem.shape[0]} names x {sem.shape[1]}d)", flush=True)
    return name_to_row, sem


# ---------------------------------------------------------------------------
# Concept sampling + context building.
# ---------------------------------------------------------------------------

def _sample_concepts(n_concepts: int, bge_names: set
                     ) -> List[Tuple[int, str]]:
    """Deterministic sample of (entity_idx, name) from intersection of KB
    entity names and BGE-cache names. Requires entities.jsonl idx==line_no.
    """
    if not _ENTITIES_PATH.exists():
        raise FileNotFoundError(f"KB entities not found: {_ENTITIES_PATH}")
    cand: List[Tuple[int, str]] = []
    with open(_ENTITIES_PATH, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            idx = row.get("idx")
            name = row.get("name")
            if idx != line_no:
                raise ValueError(
                    f"entities.jsonl line {line_no}: idx={idx} != line_no"
                )
            if isinstance(name, str) and name in bge_names:
                cand.append((line_no, name))
    if len(cand) < n_concepts:
        raise ValueError(
            f"intersection too small: {len(cand)} candidates < {n_concepts} "
            f"requested"
        )
    rng = np.random.default_rng(SAMPLE_SEED)
    sel = rng.choice(len(cand), size=n_concepts, replace=False)
    sel.sort()
    return [cand[i] for i in sel]


def _build_contexts(idx_set: set) -> Dict[int, List[str]]:
    """Single atom-scan -> dict entity_idx -> list of context strings.

    Same construction as Step-1 _build_entity_context_map, restricted to
    idx_set (both subject and object side).
    """
    if not _ATOMS_PATH.exists():
        raise FileNotFoundError(f"KB atoms not found: {_ATOMS_PATH}")
    contexts: Dict[int, List[str]] = {}
    n_lines = 0
    with open(_ATOMS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # corrupt atom line; atoms integrity not this cell's job
            s = row.get("s")
            o = row.get("o")
            s_name = row.get("s_name", "")
            p_name = row.get("p_name", "")
            o_name = row.get("o_name", "")
            if isinstance(s, int) and s in idx_set and isinstance(o, int):
                lst = contexts.setdefault(s, [])
                if len(lst) < MAX_ATOMS_PER_ENTITY:
                    lst.append(f"{p_name} {o_name}".strip())
            if isinstance(o, int) and o in idx_set and isinstance(s, int):
                lst = contexts.setdefault(o, [])
                if len(lst) < MAX_ATOMS_PER_ENTITY:
                    lst.append(f"{s_name} {p_name}".strip())
    print(f"[ablation] atom-scan: {n_lines} lines, "
          f"{len(contexts)}/{len(idx_set)} sampled entities have context",
          flush=True)
    return contexts


# ---------------------------------------------------------------------------
# Encoding (Hebbian context-mean -> dense float acc; PRE-WTA).
# ---------------------------------------------------------------------------

def _encode_dense(concepts: List[Tuple[int, str]],
                  contexts: Dict[int, List[str]],
                  output_dir: Path) -> Tuple[np.ndarray, int]:
    """Return (acc [n, N] float32 Hebbian mean, n_zero_context_fallback)."""
    enc = CharPositionalEncoder(
        n_dim=N_DIM, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{SEED_ENCODER}",
    )
    n = len(concepts)
    acc = np.zeros((n, N_DIM), dtype=np.float32)
    n_zero_ctx = 0
    t0 = time.perf_counter()
    for i, (eidx, name) in enumerate(concepts):
        ctx = contexts.get(eidx, [])
        if not ctx:
            ctx = [name]
            n_zero_ctx += 1
        valid = [s for s in ctx if isinstance(s, str) and s]
        if valid:
            hds = enc.encode_batch(valid).astype(np.float32)  # [k, N] bipolar
            acc[i] = hds.sum(axis=0) / float(len(valid))
        else:
            acc[i] = enc.encode_sentence(name).astype(np.float32)
        if i > 0 and (i % 100) == 0:
            per = (time.perf_counter() - t0) / i
            print(f"[ablation] encode {i}/{n} (per={per*1000:.1f}ms)", flush=True)
    return acc, n_zero_ctx


def _sparsify(acc: np.ndarray, k: int) -> np.ndarray:
    """Top-k WTA sparse-bipolar int8 code table [n, N]. k>=N -> dense sign."""
    n, nd = acc.shape
    sign = np.sign(acc).astype(np.int8)
    sign[sign == 0] = 1
    if k >= nd:
        return sign.astype(np.int8)
    out = np.zeros((n, nd), dtype=np.int8)
    idx = np.argpartition(-np.abs(acc), k, axis=1)[:, :k]  # [n, k]
    rows = np.repeat(np.arange(n), k)
    cols = idx.reshape(-1)
    out[rows, cols] = sign[rows, cols]
    return out


# ---------------------------------------------------------------------------
# Fidelity axes.
# ---------------------------------------------------------------------------

def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def _semantic_fidelity(codes: np.ndarray, bge: np.ndarray,
                       query_idx: np.ndarray, topk: int
                       ) -> Tuple[float, float]:
    """Return (neighbor_recall@k, rsa_spearman) between concept-code space and
    BGE-gold space over the query set. Codes/bge are [n, .]; query_idx indexes
    rows; neighbors drawn from the FULL codebook (self excluded).
    """
    cn = _l2norm_rows(codes.astype(np.float32))
    bn = _l2norm_rows(bge.astype(np.float32))
    n = codes.shape[0]
    recalls = []
    for q in query_idx:
        sc = cn[q] @ cn.T
        sb = bn[q] @ bn.T
        sc[q] = -np.inf
        sb[q] = -np.inf
        code_nn = set(np.argpartition(-sc, topk)[:topk].tolist())
        gold_nn = set(np.argpartition(-sb, topk)[:topk].tolist())
        recalls.append(len(code_nn & gold_nn) / float(topk))
    recall = float(np.mean(recalls))
    # RSA: Spearman rank-corr of pairwise sims over query set (off-diagonal).
    cq = cn[query_idx]
    bq = bn[query_idx]
    sc_mat = cq @ cq.T
    sb_mat = bq @ bq.T
    iu = np.triu_indices(len(query_idx), k=1)
    rsa = _spearman(sc_mat[iu], sb_mat[iu])
    return recall, rsa


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation (no scipy)."""
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = (np.sqrt((ra * ra).sum()) * np.sqrt((rb * rb).sum())) + 1e-12
    return float((ra * rb).sum() / denom)


def _bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """hdlab HRR bind (real input -> circular convolution). a,b [.,N] float32."""
    out = hdbinding.bind(torch.from_numpy(np.ascontiguousarray(a)),
                         torch.from_numpy(np.ascontiguousarray(b)))
    return out.numpy()


def _unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = hdbinding.unbind(torch.from_numpy(np.ascontiguousarray(c)),
                           torch.from_numpy(np.ascontiguousarray(b)))
    return out.numpy()


def _algebraic_fidelity(codes: np.ndarray) -> Dict[str, object]:
    """Return dict: roundtrip_cos@M1 + bundle_cleanup_acc per M (mean/std over
    role-seeds). Uses REAL hdlab.binding primitives (HRR). SHARDED codebook for
    cleanup; bundle arm intentionally superposes M pairs (capacity discriminator).
    """
    cf = codes.astype(np.float32)
    cn = _l2norm_rows(cf)  # for cleanup cosine
    n = cf.shape[0]
    if n <= max(M_GRID):
        raise ValueError(
            f"codebook n={n} must exceed max bundle M={max(M_GRID)}"
        )

    # Single-bind roundtrip sanity (positive control; expect ~1.0).
    rng0 = np.random.default_rng(101)
    rt = []
    for _ in range(60):
        i = int(rng0.integers(n))
        r = (rng0.integers(0, 2, N_DIM) * 2 - 1).astype(np.float32)
        b = _bind(cf[i], r)
        rec = _unbind(b, r)
        rec = rec / (np.linalg.norm(rec) + 1e-9)
        rt.append(float(rec @ cn[i]))
    roundtrip_cos = float(np.mean(rt))

    # Bundle-capacity cleanup per M, averaged over role-seeds.
    per_m: Dict[int, Dict[str, float]] = {}
    for M in M_GRID:
        seed_accs = []
        for seed in ROLE_SEEDS:
            rng = np.random.default_rng(seed)
            correct = 0
            for _ in range(N_TRIALS):
                sel = rng.choice(n, M, replace=False)
                roles = (rng.integers(0, 2, (M, N_DIM)) * 2 - 1).astype(np.float32)
                bound = _bind(cf[sel], roles)          # [M, N] row-wise HRR
                bundle = bound.sum(axis=0)             # superpose
                rec = _unbind(bundle, roles[0])
                rec = rec / (np.linalg.norm(rec) + 1e-9)
                sims = cn @ rec
                if int(np.argmax(sims)) == int(sel[0]):
                    correct += 1
            seed_accs.append(correct / float(N_TRIALS))
        per_m[M] = {
            "mean": float(np.mean(seed_accs)),
            "std": float(np.std(seed_accs)),
        }
    return {"roundtrip_cos_m1": roundtrip_cos, "bundle_cleanup_per_m": per_m}


# ---------------------------------------------------------------------------
# Pareto helpers.
# ---------------------------------------------------------------------------

def _pareto_front(points: Dict[int, Tuple[float, float]]) -> List[int]:
    """Return list of k on the non-dominated front (both axes maximized)."""
    front = []
    for k, (sa, aa) in points.items():
        dominated = False
        for k2, (sb, ab) in points.items():
            if k2 == k:
                continue
            if (sb >= sa and ab >= aa) and (sb > sa or ab > aa):
                dominated = True
                break
        if not dominated:
            front.append(k)
    return sorted(front)


# ---------------------------------------------------------------------------
# Verdict.
# ---------------------------------------------------------------------------

def _verdict(per_level: Dict[int, dict], code_hashes: Dict[int, str],
             reporting_m: int, baseline_in_band: bool,
             n_nan: int, n_inf: int) -> Tuple[str, str, dict]:
    # Cardinality (META_RULE_H).
    if len(per_level) != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"{len(per_level)} != {EXPECTED_N_UNITS}", {})
    # NaN/Inf.
    if n_nan > 0 or n_inf > 0:
        return ("HARD_FAIL", f"H_NAN_INF: n_nan={n_nan} n_inf={n_inf}", {})
    # Arms-differ (META_RULE_AF).
    hset = set(code_hashes.values())
    if len(hset) != len(code_hashes):
        return ("HARD_FAIL",
                "META_RULE_AF_VIOLATION: code tables bit-identical across k", {})

    sem = {k: per_level[k]["semantic_recall_at10"] for k in per_level}
    alg = {k: per_level[k]["bundle_cleanup_per_m"][str(reporting_m)]["mean"]
           for k in per_level}
    semantic_spread = max(sem.values()) - min(sem.values())
    algebraic_spread = max(alg.values()) - min(alg.values())
    disc = max(semantic_spread, algebraic_spread)

    points = {k: (sem[k], alg[k]) for k in per_level}
    front = _pareto_front(points)
    k20_on_front = 20 in front
    diag = {
        "semantic_spread": semantic_spread,
        "algebraic_spread": algebraic_spread,
        "discriminator_spread": disc,
        "pareto_front_k": front,
        "k20_on_front": k20_on_front,
        "reporting_m": reporting_m,
        "semantic_recall_by_k": sem,
        "algebraic_acc_by_k": alg,
    }

    if not baseline_in_band:
        return ("MIDDLE_BAND",
                f"BASELINE_NOT_IN_BAND: dense algebraic acc not in (0.05,0.95) at "
                f"any M in {M_GRID}; regime re-spec before FULL", diag)
    if disc < 0.05:
        return ("MIDDLE_BAND",
                f"VACUOUS_SWEEP: discriminator_spread={disc:.3f} < 0.05 "
                f"(sem={semantic_spread:.3f} alg={algebraic_spread:.3f}); sparsity "
                f"does not measurably move fidelity in this regime; INCONCLUSIVE",
                diag)
    return ("HARD_PASS",
            f"FRONTIER_NONDEGENERATE: disc_spread={disc:.3f} "
            f"(sem={semantic_spread:.3f} alg={algebraic_spread:.3f}) "
            f"pareto_front_k={front} k20_on_front={k20_on_front} "
            f"reporting_M={reporting_m}; ready for FULL", diag)


# ---------------------------------------------------------------------------
# Runner.
# ---------------------------------------------------------------------------

def run_experiment(run_mode: str) -> int:
    anchor = _artifact_anchor(run_mode)
    out_dir = get_output_dir(anchor)
    n_concepts = _SMOKE_N_CONCEPTS if run_mode == "smoke" else _FULL_N_CONCEPTS

    _write_start_marker(out_dir, run_mode, EXPECTED_N_UNITS)
    print(f"[ablation] run_mode={run_mode} n_concepts={n_concepts} "
          f"anchor={anchor}", flush=True)
    t0 = time.perf_counter()

    name_to_row, bge_sem = _load_bge_cache()
    bge_names = set(name_to_row.keys())
    concepts = _sample_concepts(n_concepts, bge_names)
    print(f"[ablation] sampled {len(concepts)} concepts", flush=True)

    idx_set = {eidx for eidx, _ in concepts}
    contexts = _build_contexts(idx_set)

    acc, n_zero_ctx = _encode_dense(concepts, contexts, out_dir)
    if np.isnan(acc).any() or np.isinf(acc).any():
        raise ValueError("NaN/Inf in Hebbian acc; aborting before sweep")

    # BGE gold rows aligned to sampled concept order.
    bge = np.stack([bge_sem[name_to_row[name]] for _, name in concepts], axis=0)

    # Deterministic held-out query set (last N_QUERY by sample order).
    q = min(N_QUERY, len(concepts) // 2)
    query_idx = np.arange(len(concepts) - q, len(concepts))

    # Sweep.
    per_level: Dict[int, dict] = {}
    code_hashes: Dict[int, str] = {}
    n_nan_total = 0
    n_inf_total = 0
    for u, k in enumerate(K_LEVELS):
        try:
            codes = _sparsify(acc, k)
            code_hashes[k] = hashlib.sha256(codes.tobytes()).hexdigest()
            if np.isnan(codes.astype(np.float32)).any():
                n_nan_total += 1
            recall, rsa = _semantic_fidelity(codes, bge, query_idx, TOPK_NEIGHBORS)
            alg = _algebraic_fidelity(codes)
            mean_nnz = float((codes != 0).sum(axis=1).mean())
            per_level[k] = {
                "k": k,
                "sparsity_rate": k / float(N_DIM),
                "mean_nnz": mean_nnz,
                "semantic_recall_at10": recall,
                "rsa_spearman": rsa,
                "roundtrip_cos_m1": alg["roundtrip_cos_m1"],
                "bundle_cleanup_per_m": {
                    str(M): alg["bundle_cleanup_per_m"][M] for M in M_GRID
                },
                "code_sha256": code_hashes[k],
                "failure_class": None,
            }
            elapsed = time.perf_counter() - t0
            _emit_heartbeat(out_dir, u + 1, EXPECTED_N_UNITS, elapsed,
                            extra={"k": k, "recall": recall})
            print(f"[ablation] k={k:4d} nnz={mean_nnz:.1f} recall@10={recall:.3f} "
                  f"rsa={rsa:.3f} rt_cos={alg['roundtrip_cos_m1']:.3f} "
                  f"bundle={{" +
                  ", ".join(f"M{M}={alg['bundle_cleanup_per_m'][M]['mean']:.2f}"
                            for M in M_GRID) + f"}} elapsed={elapsed:.1f}s",
                  flush=True)
        except Exception as exc:  # per-unit failure-class (META_RULE_J)
            per_level[k] = {
                "k": k, "failure_class": f"{type(exc).__name__}: {str(exc)[:200]}",
            }
            print(f"[ablation] k={k} FAILED: {type(exc).__name__}: {exc}",
                  flush=True)

    # Adaptive reporting_M: dense (k=1024) acc closest to 0.7 inside (0.05,0.95).
    dense = per_level.get(1024, {})
    reporting_m = M_GRID[0]
    baseline_in_band = False
    if "bundle_cleanup_per_m" in dense:
        best_gap = 1e9
        in_band_any = False
        for M in M_GRID:
            a = dense["bundle_cleanup_per_m"][str(M)]["mean"]
            if 0.05 < a < 0.95:
                in_band_any = True
                gap = abs(a - 0.70)
                if gap < best_gap:
                    best_gap = gap
                    reporting_m = M
        baseline_in_band = in_band_any
        if not in_band_any:
            # pick M with dense acc closest to band midpoint for reporting.
            reporting_m = min(
                M_GRID,
                key=lambda M: abs(dense["bundle_cleanup_per_m"][str(M)]["mean"] - 0.5),
            )

    verdict, verdict_msg, diag = _verdict(
        per_level, code_hashes, reporting_m, baseline_in_band,
        n_nan_total, n_inf_total,
    )

    elapsed_total = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": float(elapsed_total),
        "run_mode": run_mode,
        "anchor_name": anchor,
        "N_DIM": N_DIM,
        "n_concepts": len(concepts),
        "n_zero_context_fallback": n_zero_ctx,
        "n_query": int(q),
        "k_levels": K_LEVELS,
        "m_grid": M_GRID,
        "role_seeds": ROLE_SEEDS,
        "n_trials": N_TRIALS,
        "reporting_m": reporting_m,
        "baseline_in_band": baseline_in_band,
        "per_level": {str(k): v for k, v in per_level.items()},
        "code_hashes": {str(k): v for k, v in code_hashes.items()},
        "pareto_diag": diag,
        "cardinality_ok": (len(per_level) == EXPECTED_N_UNITS),
        "arms_differ_verified": (len(set(code_hashes.values())) == len(code_hashes)),
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "adaptive_with_discriminator_gate",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[ablation] verdict={verdict} msg={verdict_msg} "
          f"elapsed={elapsed_total:.1f}s", flush=True)
    return 0 if verdict != "CELL_CRASHED" else 1


def run_self_test() -> int:
    """Fast self-test: tiny synthetic sweep exercises the SAME code path branches
    (sparsify, semantic RSA, algebraic HRR bind/unbind, verdict) without KB/BGE."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(3)
    n = 130
    acc = rng.standard_normal((n, N_DIM)).astype(np.float32)
    # synthetic "BGE" gold correlated with a linear projection of acc
    proj = rng.standard_normal((N_DIM, 64)).astype(np.float32)
    bge = acc @ proj
    query_idx = np.arange(n - 40, n)
    hashes = {}
    for k in K_LEVELS:
        codes = _sparsify(acc, k)
        hashes[k] = hashlib.sha256(codes.tobytes()).hexdigest()
        assert codes.dtype == np.int8
        nnz = (codes != 0).sum(axis=1)
        exp = min(k, N_DIM)
        assert int(nnz.max()) <= exp, f"k={k}: nnz {nnz.max()} > {exp}"
        recall, rsa = _semantic_fidelity(codes, bge, query_idx, 5)
        assert 0.0 <= recall <= 1.0, f"recall oob {recall}"
        assert -1.0 <= rsa <= 1.0, f"rsa oob {rsa}"
    # arms-differ
    assert len(set(hashes.values())) == len(hashes), "selftest: arms identical"
    # algebraic path on a tiny codebook
    codes = _sparsify(acc, 20)
    alg = _algebraic_fidelity(codes)
    assert alg["roundtrip_cos_m1"] > 0.4, (
        f"selftest: single-bind roundtrip_cos={alg['roundtrip_cos_m1']:.3f} < 0.4 "
        f"(HRR bipolar-role roundtrip is lossy but must beat chance)"
    )
    # pareto helper
    pts = {8: (0.1, 0.9), 20: (0.5, 0.5), 1024: (0.9, 0.1)}
    front = _pareto_front(pts)
    assert set(front) == {8, 20, 1024}, f"selftest pareto: {front}"
    pts2 = {8: (0.1, 0.1), 20: (0.5, 0.5), 1024: (0.9, 0.9)}
    assert _pareto_front(pts2) == [1024], f"selftest pareto2: {_pareto_front(pts2)}"
    print(f"[selftest] PASS (elapsed={time.perf_counter()-t0:.2f}s)", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Concept-Encoder Design Ablation v1")
    p.add_argument("--run-mode",
                   default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
                   choices=["self_test", "smoke", "full"])
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
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
    return run_experiment(args.run_mode)


if __name__ == "__main__":
    _fallback_out = get_output_dir(ANCHOR_NAME)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException (META_RULE section 8)
        try:
            _write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass
        raise
