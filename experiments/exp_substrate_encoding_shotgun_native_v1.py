"""substrate_encoding_shotgun_native_v1 -- 6 encoders x 4 substrate-native tasks.

Lane 1 (substrate-native capability) apples-to-apples encoder comparison.

ENCODERS (E1..E6):
    E1 sparse-bipolar f=0.02      (ternary +/-/0; density 0.02)
    E2 sparse-bipolar f=0.05      (ternary +/-/0; density 0.05; current default)
    E3 dense bipolar              (+/-1 sign Bernoulli; density 1.0)
    E4 k-WTA-VQ                   (Gaussian -> top-k abs sign-quant; k=0.05*N)
    E5 dense Gaussian             (continuous N(0, 1/N))
    E6 Hadamard                   (orthogonal-by-construction; sign-permuted Hadamard rows)

TASKS (T1..T4):
    T1 STORAGE-RETRIEVAL    M=500 bound pairs; top-1 recall@1 over value codebook
    T2 COMPOSITION          M=300 pairs; normalized unbind-cosine in-vs-out separation
    T3 CAPACITY-AT-SCALE    M-sweep; capacity M* where recall@1 >= 0.95
    T4 CROSSTALK            at M=1600; mean cosine of unbound vec to off-target atoms

PRE-REG bands per preregs/2026-06-24_substrate_encoding_shotgun_native_v1.md.

Pure numpy. CPU-only. ASCII-only. Per-seed checkpoint. atexit synthesizer.
NO corpus / NO word2vec / NO statistical-LM baseline. Synthetic concept ids only.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import atexit
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_metrics,
    write_partial_key,
)

ANCHOR_NAME = "substrate_encoding_shotgun_native_v1"

# ----------------------------------------------------------------------------
# CLI + run mode
# ----------------------------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get(
    "HDLAB_RUN_MODE", "full"
)

# ----------------------------------------------------------------------------
# Config (FULL and smoke)
# ----------------------------------------------------------------------------
N_DIM = 8192

ENCODER_NAMES = ["E1_sparse_f002", "E2_sparse_f005", "E3_dense_bipolar",
                 "E4_kwta_vq", "E5_dense_gaussian", "E6_hadamard"]
TASK_NAMES = ["T1_storage_retrieval", "T2_composition",
              "T3_capacity_at_scale", "T4_crosstalk"]

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [7]

# T1 storage retrieval
T1_M_FULL = 500
T1_M_SMOKE = 100

# T2 composition
T2_M_FULL = 300
T2_M_SMOKE = 80
T2_PROBES = 200  # in-set probes; matched n_out_set probes for separation

# T3 capacity sweep
T3_M_GRID_FULL = [100, 200, 400, 800, 1600, 3200, 6400]
T3_M_GRID_SMOKE = [50, 100]
T3_CAPACITY_THRESHOLD = 0.95

# T4 crosstalk
T4_M_FULL = 1600
T4_M_SMOKE = 100
T4_N_PROBES = 100

# Sparse density parameters
SPARSE_F_E1 = 0.02
SPARSE_F_E2 = 0.05
KWTA_FRAC = 0.05

# Pre-reg HARD bands
PASS_T1 = 0.95
PASS_T2 = 0.30
PASS_T3 = 1000
PASS_T4 = 0.05

CONFIG_VERSION = (
    f"v1-N{N_DIM}-T1M{T1_M_FULL}-T2M{T2_M_FULL}-T3GRID{','.join(str(x) for x in T3_M_GRID_FULL)}"
    f"-T4M{T4_M_FULL}-seeds{','.join(str(s) for s in SEEDS_FULL)}-encoders6-tasks4"
)


def _smoke_overrides():
    """Apply smoke-config overrides in place."""
    global T1_M, T2_M, T3_M_GRID, T4_M, SEEDS, T4_N_P
    if RUN_MODE == "smoke":
        T1_M = T1_M_SMOKE
        T2_M = T2_M_SMOKE
        T3_M_GRID = T3_M_GRID_SMOKE
        T4_M = T4_M_SMOKE
        T4_N_P = 50
        SEEDS = SEEDS_SMOKE
    else:
        T1_M = T1_M_FULL
        T2_M = T2_M_FULL
        T3_M_GRID = T3_M_GRID_FULL
        T4_M = T4_M_FULL
        T4_N_P = T4_N_PROBES
        SEEDS = SEEDS_FULL


_smoke_overrides()


# ----------------------------------------------------------------------------
# Output dir + atexit synthesizer
# ----------------------------------------------------------------------------
OUT_DIR = get_output_dir(ANCHOR_NAME)
OUT_DIR.mkdir(parents=True, exist_ok=True)
_T_START = time.time()


def _build_metrics(per_seed_dict: Dict[str, dict]) -> dict:
    """Aggregate per-seed dicts into the final metrics shape.

    per_seed[seed]['matrix'][encoder][task] = primary_metric_float
    """
    if not per_seed_dict:
        return {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials produced",
            "summary": "no per-seed partials produced",
            "elapsed_s": time.time() - _T_START,
            "run_mode": RUN_MODE,
            "n_seeds": 0,
            "config_version": CONFIG_VERSION,
        }

    seed_keys = sorted(per_seed_dict.keys(), key=lambda s: int(s))
    per_seed_list = [per_seed_dict[s] for s in seed_keys]

    # Aggregate matrix mean across seeds
    agg_matrix: Dict[str, Dict[str, float]] = {e: {} for e in ENCODER_NAMES}
    agg_matrix_cv: Dict[str, Dict[str, float]] = {e: {} for e in ENCODER_NAMES}
    for e in ENCODER_NAMES:
        for t in TASK_NAMES:
            vals = []
            for ps in per_seed_list:
                v = ps.get("matrix", {}).get(e, {}).get(t)
                if v is not None and (isinstance(v, (int, float)) and math.isfinite(v)):
                    vals.append(float(v))
            if vals:
                m = float(np.mean(vals))
                s = float(np.std(vals))
                agg_matrix[e][t] = m
                agg_matrix_cv[e][t] = float(s / max(abs(m), 1e-9))
            else:
                agg_matrix[e][t] = float("nan")
                agg_matrix_cv[e][t] = float("nan")

    # PASS per (encoder, task)
    pass_matrix: Dict[str, Dict[str, bool]] = {e: {} for e in ENCODER_NAMES}
    for e in ENCODER_NAMES:
        v_t1 = agg_matrix[e]["T1_storage_retrieval"]
        v_t2 = agg_matrix[e]["T2_composition"]
        v_t3 = agg_matrix[e]["T3_capacity_at_scale"]
        v_t4 = agg_matrix[e]["T4_crosstalk"]
        pass_matrix[e]["T1_storage_retrieval"] = bool(math.isfinite(v_t1) and v_t1 >= PASS_T1)
        pass_matrix[e]["T2_composition"] = bool(math.isfinite(v_t2) and v_t2 >= PASS_T2)
        pass_matrix[e]["T3_capacity_at_scale"] = bool(math.isfinite(v_t3) and v_t3 >= PASS_T3)
        pass_matrix[e]["T4_crosstalk"] = bool(math.isfinite(v_t4) and v_t4 <= PASS_T4)

    # Best encoder per task
    best_per_task: Dict[str, str] = {}
    for t in TASK_NAMES:
        if t == "T4_crosstalk":
            # lower is better
            best_e = min(ENCODER_NAMES, key=lambda e: agg_matrix[e][t] if math.isfinite(agg_matrix[e][t]) else float("inf"))
        else:
            best_e = max(ENCODER_NAMES, key=lambda e: agg_matrix[e][t] if math.isfinite(agg_matrix[e][t]) else float("-inf"))
        best_per_task[t] = best_e

    # Top-2 across all tasks
    encoder_ranks: Dict[str, List[int]] = {e: [] for e in ENCODER_NAMES}
    for t in TASK_NAMES:
        if t == "T4_crosstalk":
            ranked = sorted(ENCODER_NAMES, key=lambda e: agg_matrix[e][t] if math.isfinite(agg_matrix[e][t]) else float("inf"))
        else:
            ranked = sorted(ENCODER_NAMES, key=lambda e: -(agg_matrix[e][t] if math.isfinite(agg_matrix[e][t]) else float("-inf")))
        for i, e in enumerate(ranked):
            encoder_ranks[e].append(i + 1)  # 1-indexed
    top2_all = [e for e in ENCODER_NAMES if all(r <= 2 for r in encoder_ranks[e])]

    # Encoders that PASS all 4 tasks
    pass_all = [e for e in ENCODER_NAMES if all(pass_matrix[e][t] for t in TASK_NAMES)]
    pass_any_t1 = [e for e in ENCODER_NAMES if pass_matrix[e]["T1_storage_retrieval"]]

    # Verdict
    if pass_all:
        verdict = "HARD_PASS"
        vmsg = (
            f"OPTIMAL_ENCODER_FOUND encoders_pass_all={pass_all} "
            f"top2_all_tasks={top2_all} best_per_task={best_per_task} run_mode={RUN_MODE}"
        )
    elif not pass_any_t1:
        verdict = "HARD_FAIL"
        vmsg = (
            f"NO_ENCODER_PASSES_T1 (storage-retrieval failed for all; substrate-side bug suspected) "
            f"matrix={agg_matrix} run_mode={RUN_MODE}"
        )
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (
            f"NO_SINGLE_ENCODER_DOMINATES best_per_task={best_per_task} top2_all={top2_all} "
            f"pass_any_t1={pass_any_t1} pass_all=[] run_mode={RUN_MODE}"
        )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "elapsed_s": time.time() - _T_START,
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed_list),
        "config_version": CONFIG_VERSION,
        "corpus_provenance": "synthetic",
        "lane": "Lane_1_substrate_native_capability",
        "encoders": ENCODER_NAMES,
        "tasks": TASK_NAMES,
        "pass_thresholds": {
            "T1_storage_retrieval": PASS_T1,
            "T2_composition": PASS_T2,
            "T3_capacity_at_scale": PASS_T3,
            "T4_crosstalk": PASS_T4,
        },
        "per_seed": per_seed_list,
        "aggregate": {
            "matrix_mean": agg_matrix,
            "matrix_cv": agg_matrix_cv,
            "pass_matrix": pass_matrix,
            "best_per_task": best_per_task,
            "top2_all_tasks": top2_all,
            "pass_all_tasks": pass_all,
            "encoder_ranks": encoder_ranks,
        },
    }
    return metrics


def _atexit_synthesize() -> None:
    """If metrics.json missing, synthesize from any partials present."""
    metrics_path = OUT_DIR / "metrics.json"
    if metrics_path.exists():
        return
    try:
        run_cfg = {"N": N_DIM, "run_mode": RUN_MODE}
        ps = aggregate_partials(OUT_DIR, run_config=run_cfg)
        m = _build_metrics(ps)
        m["summary"] = (m.get("summary") or "") + " (synthesized_atexit)"
        write_metrics(OUT_DIR, m)
        print(f"[atexit] synthesized metrics.json from {len(ps)} partials", flush=True)
    except Exception as e:
        # Last resort: emit a minimal metrics.json so the runner can record SOMETHING
        try:
            stub = {
                "anchor_name": ANCHOR_NAME,
                "verdict": "UNKNOWN",
                "verdict_msg": f"atexit_synthesis_failed: {type(e).__name__}: {e}",
                "summary": "atexit_synthesis_failed",
                "elapsed_s": time.time() - _T_START,
                "run_mode": RUN_MODE,
                "n_seeds": 0,
                "config_version": CONFIG_VERSION,
            }
            (OUT_DIR / "metrics.json").write_text(json.dumps(stub, indent=2), encoding="utf-8")
        except Exception:
            pass


atexit.register(_atexit_synthesize)


# ----------------------------------------------------------------------------
# Encoders
# ----------------------------------------------------------------------------
def _l2_normalize(X: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(X, axis=-1, keepdims=True)
    norms = np.where(norms > 1e-12, norms, 1.0)
    return X / norms


def enc_sparse_bipolar(rng: np.random.Generator, n_atoms: int, n_dim: int, f: float) -> np.ndarray:
    """Ternary sparse-bipolar: each coord is 0 with prob (1-f), +1/-1 each with prob f/2."""
    u = rng.random((n_atoms, n_dim))
    out = np.zeros((n_atoms, n_dim), dtype=np.float32)
    pos = u < f / 2.0
    neg = (u >= f / 2.0) & (u < f)
    out[pos] = 1.0
    out[neg] = -1.0
    return _l2_normalize(out)


def enc_dense_bipolar(rng: np.random.Generator, n_atoms: int, n_dim: int) -> np.ndarray:
    out = (rng.integers(0, 2, size=(n_atoms, n_dim)) * 2 - 1).astype(np.float32)
    return _l2_normalize(out)


def enc_kwta_vq(rng: np.random.Generator, n_atoms: int, n_dim: int, frac: float) -> np.ndarray:
    """Random Gaussian -> top-k absolute values, sign-quantize, others zero."""
    raw = rng.standard_normal((n_atoms, n_dim)).astype(np.float32)
    k = max(1, int(round(frac * n_dim)))
    out = np.zeros_like(raw)
    abs_raw = np.abs(raw)
    # top-k along last axis
    # argpartition for efficiency
    idx = np.argpartition(-abs_raw, kth=k - 1, axis=-1)[:, :k]
    rows = np.repeat(np.arange(n_atoms), k)
    cols = idx.reshape(-1)
    signs = np.sign(raw[rows, cols])
    out[rows, cols] = signs
    return _l2_normalize(out)


def enc_dense_gaussian(rng: np.random.Generator, n_atoms: int, n_dim: int) -> np.ndarray:
    out = (rng.standard_normal((n_atoms, n_dim)) / math.sqrt(n_dim)).astype(np.float32)
    return _l2_normalize(out)


def enc_hadamard(rng: np.random.Generator, n_atoms: int, n_dim: int) -> np.ndarray:
    """Random sign-permuted Hadamard rows. Requires n_dim power of 2.

    Construction: build H_n via Sylvester recursion; pick random rows (with
    replacement if n_atoms > n_dim); apply per-vector random sign flips so
    different atoms remain effectively-distinct.
    """
    # Build Hadamard
    log2_n = int(round(math.log2(n_dim)))
    assert 2 ** log2_n == n_dim, f"Hadamard requires n_dim power of 2; got {n_dim}"
    H = np.array([[1]], dtype=np.float32)
    for _ in range(log2_n):
        H = np.block([[H, H], [H, -H]])
    # Pick rows (with replacement if needed) + per-atom random sign flip
    row_idx = rng.integers(0, n_dim, size=n_atoms)
    sign_flips = rng.integers(0, 2, size=(n_atoms, n_dim)) * 2 - 1
    out = (H[row_idx] * sign_flips.astype(np.float32))
    return _l2_normalize(out)


def make_encoder(name: str, rng: np.random.Generator, n_atoms: int, n_dim: int) -> np.ndarray:
    if name == "E1_sparse_f002":
        return enc_sparse_bipolar(rng, n_atoms, n_dim, SPARSE_F_E1)
    if name == "E2_sparse_f005":
        return enc_sparse_bipolar(rng, n_atoms, n_dim, SPARSE_F_E2)
    if name == "E3_dense_bipolar":
        return enc_dense_bipolar(rng, n_atoms, n_dim)
    if name == "E4_kwta_vq":
        return enc_kwta_vq(rng, n_atoms, n_dim, KWTA_FRAC)
    if name == "E5_dense_gaussian":
        return enc_dense_gaussian(rng, n_atoms, n_dim)
    if name == "E6_hadamard":
        return enc_hadamard(rng, n_atoms, n_dim)
    raise ValueError(f"unknown encoder: {name}")


# ----------------------------------------------------------------------------
# HRR bind/unbind (FFT-based circular convolution; pure numpy)
# ----------------------------------------------------------------------------
def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Real-vector HRR bind: ifft(fft(a) * fft(b)).real, batched."""
    fa = np.fft.fft(a, axis=-1)
    fb = np.fft.fft(b, axis=-1)
    return np.fft.ifft(fa * fb, axis=-1).real.astype(np.float32)


def hrr_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Inverse: ifft(fft(c) * conj(fft(b))).real."""
    fc = np.fft.fft(c, axis=-1)
    fb = np.fft.fft(b, axis=-1)
    return np.fft.ifft(fc * np.conj(fb), axis=-1).real.astype(np.float32)


def cosine_to_codebook(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Cosine similarity: query (M, N) vs codebook (V, N) -> (M, V)."""
    q = _l2_normalize(query)
    cb = _l2_normalize(codebook)
    return q @ cb.T


# ----------------------------------------------------------------------------
# Tasks
# ----------------------------------------------------------------------------
def task_t1_storage_retrieval(K: np.ndarray, V: np.ndarray) -> float:
    """Bundle sum_i bind(K_i, V_i), then unbind with K_q and cosine-cleanup over V codebook.

    K, V: (M, N). Returns top1 recall (fraction of queries where argmax-cosine == true V idx).
    """
    M, N = K.shape
    bound = hrr_bind(K, V)
    bundle = bound.sum(axis=0, keepdims=True)  # (1, N)
    # query all K_i
    unbound = hrr_unbind(np.tile(bundle, (M, 1)), K)  # (M, N)
    sims = cosine_to_codebook(unbound, V)  # (M, M)
    top1 = np.argmax(sims, axis=1)
    correct = (top1 == np.arange(M)).sum()
    return float(correct) / float(M)


def task_t2_composition(S: np.ndarray, O: np.ndarray, n_probes: int, rng: np.random.Generator) -> float:
    """Bundle bind(S_i, O_i) for M pairs. Score normalized separation:
    in-set: unbind(bundle, S_i) cosine to O_i (true).
    out-set: unbind(bundle, S_j) cosine to O_k where (j, k) is a freshly-sampled NON-stored pair.
    Returns (in_mean - out_mean) / (in_std + out_std + eps).
    """
    M, N = S.shape
    bundle = hrr_bind(S, O).sum(axis=0, keepdims=True)  # (1, N)

    n_in = min(n_probes, M)
    idx_in = rng.choice(M, size=n_in, replace=False)
    unbound_in = hrr_unbind(np.tile(bundle, (n_in, 1)), S[idx_in])
    # cosine of unbound_in to O[idx_in]  -- per-pair scalar
    a = _l2_normalize(unbound_in)
    b = _l2_normalize(O[idx_in])
    in_sims = (a * b).sum(axis=1)

    # out-set: random (S_j, O_k) where the pair was NOT in the stored set
    # We use S_j from S, but O_k from a fresh non-stored vector with same encoder distribution
    # is hard; instead: sample (j, k) from M with j != k. This is the "off-target" composition
    # which was definitely NOT stored (we stored only (i, i) pairs).
    n_out = n_in
    j = rng.integers(0, M, size=n_out)
    k = rng.integers(0, M, size=n_out)
    same = (j == k)
    # fix any j==k
    if same.any():
        k[same] = (k[same] + 1) % M
    unbound_out = hrr_unbind(np.tile(bundle, (n_out, 1)), S[j])
    a2 = _l2_normalize(unbound_out)
    b2 = _l2_normalize(O[k])
    out_sims = (a2 * b2).sum(axis=1)

    in_mean = float(in_sims.mean())
    out_mean = float(out_sims.mean())
    in_std = float(in_sims.std())
    out_std = float(out_sims.std())
    sep = (in_mean - out_mean) / (in_std + out_std + 1e-9)
    return float(sep)


def task_t3_capacity_sweep(encoder_name: str, n_dim: int, m_grid: List[int],
                           seed: int) -> int:
    """Sweep M; return largest M where T1 recall >= threshold. Returns 0 if even smallest M fails."""
    capacity = 0
    for M in m_grid:
        rng = np.random.default_rng(seed * 1009 + M)  # decorrelate
        K = make_encoder(encoder_name, rng, M, n_dim)
        V = make_encoder(encoder_name, rng, M, n_dim)
        r = task_t1_storage_retrieval(K, V)
        if r >= T3_CAPACITY_THRESHOLD:
            capacity = M
        else:
            break  # monotone-decreasing in M (typical); stop early
    return int(capacity)


def task_t4_crosstalk(K: np.ndarray, V: np.ndarray, n_probes: int, rng: np.random.Generator) -> float:
    """At saturation: store M pairs, query K_i, measure mean cosine of unbound to V_j for j!=i.

    Returns mean off-target cosine (lower = better).
    """
    M, N = K.shape
    bundle = hrr_bind(K, V).sum(axis=0, keepdims=True)
    n_p = min(n_probes, M)
    idx = rng.choice(M, size=n_p, replace=False)
    unbound = hrr_unbind(np.tile(bundle, (n_p, 1)), K[idx])  # (n_p, N)
    sims = cosine_to_codebook(unbound, V)  # (n_p, M)
    # zero out target diagonal
    sims_arr = sims.copy()
    for row, i in enumerate(idx):
        sims_arr[row, i] = 0.0
    # mean of absolute off-target cosine
    # off-target count per row = M - 1 (we zeroed self)
    off_sum = np.abs(sims_arr).sum(axis=1)
    off_mean = float((off_sum / max(M - 1, 1)).mean())
    return off_mean


# ----------------------------------------------------------------------------
# Per-seed runner
# ----------------------------------------------------------------------------
def run_one_seed(seed: int) -> dict:
    rng = np.random.default_rng(seed)
    matrix: Dict[str, Dict[str, float]] = {e: {} for e in ENCODER_NAMES}
    timing: Dict[str, Dict[str, float]] = {e: {} for e in ENCODER_NAMES}

    for e_name in ENCODER_NAMES:
        # T1
        t0 = time.time()
        rng_t1 = np.random.default_rng(seed * 31 + 1)
        K = make_encoder(e_name, rng_t1, T1_M, N_DIM)
        V = make_encoder(e_name, rng_t1, T1_M, N_DIM)
        r1 = task_t1_storage_retrieval(K, V)
        matrix[e_name]["T1_storage_retrieval"] = r1
        timing[e_name]["T1_storage_retrieval"] = time.time() - t0

        # T2
        t0 = time.time()
        rng_t2 = np.random.default_rng(seed * 31 + 2)
        S = make_encoder(e_name, rng_t2, T2_M, N_DIM)
        O = make_encoder(e_name, rng_t2, T2_M, N_DIM)
        # smoke skips heavy tasks (T3/T4) per pre-reg
        sep = task_t2_composition(S, O, T2_PROBES if RUN_MODE == "full" else 50, rng_t2)
        matrix[e_name]["T2_composition"] = sep
        timing[e_name]["T2_composition"] = time.time() - t0

        if RUN_MODE == "smoke":
            matrix[e_name]["T3_capacity_at_scale"] = float("nan")
            matrix[e_name]["T4_crosstalk"] = float("nan")
            timing[e_name]["T3_capacity_at_scale"] = 0.0
            timing[e_name]["T4_crosstalk"] = 0.0
            continue

        # T3
        t0 = time.time()
        cap = task_t3_capacity_sweep(e_name, N_DIM, T3_M_GRID, seed)
        matrix[e_name]["T3_capacity_at_scale"] = float(cap)
        timing[e_name]["T3_capacity_at_scale"] = time.time() - t0

        # T4
        t0 = time.time()
        rng_t4 = np.random.default_rng(seed * 31 + 4)
        K4 = make_encoder(e_name, rng_t4, T4_M, N_DIM)
        V4 = make_encoder(e_name, rng_t4, T4_M, N_DIM)
        xt = task_t4_crosstalk(K4, V4, T4_N_P, rng_t4)
        matrix[e_name]["T4_crosstalk"] = xt
        timing[e_name]["T4_crosstalk"] = time.time() - t0

    return {
        "_ckpt_key": str(seed),
        "seed": seed,
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "matrix": matrix,
        "timing": timing,
        "config_version": CONFIG_VERSION,
    }


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------
def _self_test() -> int:
    """1-second mechanism check.

    Asserts:
      - each encoder produces L2-normalized vectors of shape (n, N_DIM)
      - HRR bind+unbind round-trip yields cosine to target > cosine to non-target on M=10
      - selftest expected values are computed BEFORE the assertion (Fix #28 discipline)
    """
    rng = np.random.default_rng(7)
    n = 10
    N_test = 1024  # small for selftest speed
    for e_name in ENCODER_NAMES:
        X = make_encoder(e_name, rng, n, N_test)
        assert X.shape == (n, N_test), f"{e_name} shape {X.shape}"
        # L2 normalized
        norms = np.linalg.norm(X, axis=-1)
        assert np.allclose(norms, 1.0, atol=1e-4), f"{e_name} L2 norms {norms[:3]}"
        # Density sanity
        nz_frac = float((X != 0).sum()) / float(X.size)
        if e_name == "E1_sparse_f002":
            assert 0.005 <= nz_frac <= 0.05, f"E1 density {nz_frac}"
        elif e_name == "E2_sparse_f005":
            assert 0.02 <= nz_frac <= 0.10, f"E2 density {nz_frac}"
        elif e_name == "E3_dense_bipolar":
            assert nz_frac > 0.99, f"E3 density {nz_frac}"
        elif e_name == "E4_kwta_vq":
            # k = round(0.05 * 1024) = 51 -> ~0.0498
            assert 0.04 <= nz_frac <= 0.07, f"E4 density {nz_frac}"
        elif e_name == "E5_dense_gaussian":
            assert nz_frac > 0.99, f"E5 density {nz_frac}"
        elif e_name == "E6_hadamard":
            assert nz_frac > 0.99, f"E6 density {nz_frac}"

    # HRR round-trip: bundle of M=5 bound pairs, unbind a key, target value cosine
    # should be >> non-target on average.
    M_rt = 5
    for e_name in ENCODER_NAMES:
        rng_rt = np.random.default_rng(11)
        K = make_encoder(e_name, rng_rt, M_rt, N_test)
        V = make_encoder(e_name, rng_rt, M_rt, N_test)
        bundle = hrr_bind(K, V).sum(axis=0, keepdims=True)
        # query K[0]
        unbound = hrr_unbind(bundle, K[0:1])  # (1, N)
        sims = cosine_to_codebook(unbound, V).flatten()  # (M_rt,)
        # target sim should be the max (typically)
        assert int(np.argmax(sims)) == 0, f"{e_name} HRR round-trip failed: sims={sims}"

    print("[self-test] PASS: 6 encoders + HRR round-trip OK", flush=True)
    return 0


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main() -> int:
    if _ARGS.self_test:
        return _self_test()

    print(f"[main] anchor={ANCHOR_NAME} run_mode={RUN_MODE} N={N_DIM} "
          f"encoders={len(ENCODER_NAMES)} tasks={len(TASK_NAMES)} seeds={SEEDS}", flush=True)
    print(f"[main] config_version={CONFIG_VERSION}", flush=True)

    run_cfg = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, OUT_DIR, run_config=run_cfg)
    print(f"[ckpt] {len(done)} done / {len(remaining)} remaining: {remaining}", flush=True)

    for seed in remaining:
        t_seed = time.time()
        print(f"[seed {seed}] start", flush=True)
        result = run_one_seed(seed)
        write_partial_key(OUT_DIR, seed, result)
        print(f"[seed {seed}] done in {time.time()-t_seed:.1f}s", flush=True)

    ps = aggregate_partials(OUT_DIR, seeds=SEEDS, run_config=run_cfg)
    # Re-key by str(seed) to match _build_metrics expectation
    metrics = _build_metrics(ps)
    write_metrics(OUT_DIR, metrics)

    print(f"[main] verdict={metrics['verdict']} elapsed_s={metrics['elapsed_s']:.1f}", flush=True)
    print(f"[main] {metrics['verdict_msg'][:300]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
