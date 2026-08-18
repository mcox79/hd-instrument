"""tonegawa_v5_k_density_sweep_semi_sparse -- drill TOP-2: density sweep.

Prereg: preregs/2026-06-27_tonegawa_v5_k_density_sweep_semi_sparse.md
Predecessor: exp_tonegawa_v4_1_permutation_K500_GPU.py (v4 PERM-BUNDLED architecture)
Drill: notes/research_drill_3x_tonegawa_revival_or_abandon_2026-06-27.md

WHY THIS CELL:
  v4 used k=20-of-2048 = 1% density. Substrate may prefer semi-sparse
  (5-25% density) which retains some sparse-cleanup benefit while utilizing
  more of N's dimensions per code. Tests whether density (not encoding scheme)
  is the lever for sparse-bundled to beat dense PROTOTYPE_CENTROID_BUNDLED.

  Same v4 permutation-bundled architecture; ONLY k varies. CPU-bound pure
  bundling math (no GPU benefit from attractor cleanup as in v5 TOP-1).

ARCHITECTURE (same as v4):
  For each schema k_idx in 1..K:
    sparse_code = k-WTA(W @ centroid_k_idx, k=K_DENSITY) sparse {0, 1}^N
    offset = sha1(schema_id.bytes)[:8] % N
    shifted = roll(sparse_code, offset)
  S = sum over schemas of shifted_code
  Query: unshift S by -offset_q; score = k-WTA(W @ q) DOT unshifted

ARMS (3 mandatory):
  ARM_PERM_K_VARIED: PERM_TONEGAWA at swept k (the mechanism sweep)
  ARM_PROTOTYPE_DENSE: PROTO_CENTROID_BUNDLED at full density (constant baseline)
  ARM_DIAG_RANDOM: PERM-bundle of random k-of-N codes (false-accept floor)

DISCRIMINATORS:
  HARD_PASS: exists k* such that
    PERM(k*) - PROTO >= 0.10 AND PERM(k*) >= 0.30 at K=100
    OR PERM(k*) - PROTO >= 0.05 AND PERM(k*) >= 0.05 at K=500
  MIDDLE_BAND: PERM(k*) - PROTO in [0.02, 0.10) at K=100
  HARD_FAIL: no k achieves PERM > PROTO at K=100 AND no k achieves PERM > PROTO at K=500
             (substrate prefers fully dense; closes sparse-bundled direction)

REGIME:
  N_DIM=2048; k_sweep_full=[20, 50, 100, 200, 500, 1024]; K_full=[100, 500];
  smoke k_sweep=[20, 100, 500], K=[100, 500] at full N (DISCRIMINATOR-MUST-SURVIVE-SCALE)

CPU-eligible; routes to remote_cpu_queue.

CARDINALITY_OK:
  EXPECTED_N_UNITS_full = 3 arms * 6 k * 2 K * 3 seeds = 108
  EXPECTED_N_UNITS_smoke = 3 * 3 * 2 * 2 = 36
  EXPECTED_N_UNITS_selftest = 3 * 1 * 1 * 1 = 3

ASCII-only; no emojis; no em-dashes. META_RULE_X main-guard + L1/L2/L4.
Author: exp_dev 2026-06-27 (Research drill TOP-2: k-density sweep).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    from experiments._seed_checkpoint import write_partial_key
except Exception:
    def write_partial_key(out_dir: Path, seed: int, payload: Dict[str, Any]) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / ("partial_seed_%d.json" % seed)).write_text(
            json.dumps(payload, indent=2), encoding="utf-8")


ANCHOR_NAME = "tonegawa_v5_k_density_sweep_semi_sparse"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands (drill TOP-2 spec)
HP_PERM_OVER_PROTO_K100 = 0.10
HP_PERM_FLOOR_K100 = 0.30
HP_PERM_OVER_PROTO_K500 = 0.05
HP_PERM_FLOOR_K500 = 0.05
MIDDLE_PERM_OVER_PROTO = 0.02

EXPECTED_ARMS = (
    "ARM_PERM_K_VARIED",
    "ARM_PROTOTYPE_DENSE",
    "ARM_DIAG_RANDOM",
)

# Regime
if SELF_TEST_MODE:
    N_DIM = 512
    K_DENSITY_SWEEP = [10]
    N_PER_CLUSTER = 4
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.50
    K_SCHEMA_SWEEP = [50]
    SEEDS = [7]
    N_QUERIES_PER_CLUSTER = 3
elif RUN_MODE == "smoke":
    # Smoke at K=100 + K=500 with k in {20, 100, 500} (covers the predicted
    # crossover regime per drill TOP-2). Discriminator must FIRE at K=100
    # (the regime where lift is most likely).
    N_DIM = 2048
    K_DENSITY_SWEEP = [20, 100, 500]
    N_PER_CLUSTER = 8
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.55
    K_SCHEMA_SWEEP = [100, 500]
    SEEDS = [7, 17]
    N_QUERIES_PER_CLUSTER = 8
else:
    # Full: 6 k values * 2 K values * 3 seeds = 108 units
    N_DIM = 2048
    K_DENSITY_SWEEP = [20, 50, 100, 200, 500, 1024]
    N_PER_CLUSTER = 10
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.60
    K_SCHEMA_SWEEP = [100, 500]
    SEEDS = [7, 17, 23]
    N_QUERIES_PER_CLUSTER = 12

# Cardinality: arms * k_density * K_schema * seeds
# But PROTOTYPE_DENSE and DIAG_RANDOM don't vary across k_density -- they run once per K_schema.
# We re-evaluate them at each k_density for fairness (constant baseline) but identity-cache.
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(K_DENSITY_SWEEP) * len(K_SCHEMA_SWEEP) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,NPC=%d,BCC=%.2f,WCN=%.2f,"
    "K_DENS_SWEEP=%s,K_SCH_SWEEP=%s,SEEDS=%s,NQPC=%d,"
    "HP_perm-proto_K100>=%.2f,HP_perm_floor_K100>=%.2f,"
    "HP_perm-proto_K500>=%.2f,HP_perm_floor_K500>=%.2f,"
    "RUN_MODE=%s,DEVICE=cpu,"
    "hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK+SMOKE_AT_FULL_N_K500"
) % (
    ANCHOR_NAME, N_DIM, N_PER_CLUSTER, BETWEEN_CLUSTER_COSINE, WITHIN_CLUSTER_NOISE,
    K_DENSITY_SWEEP, K_SCHEMA_SWEEP, SEEDS, N_QUERIES_PER_CLUSTER,
    HP_PERM_OVER_PROTO_K100, HP_PERM_FLOOR_K100,
    HP_PERM_OVER_PROTO_K500, HP_PERM_FLOOR_K500,
    RUN_MODE,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v5_k_density_sweep_semi_sparse",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v5_k_density_sweep_semi_sparse_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives (numpy CPU) --------------------------

def k_wta_batched_np(activations: np.ndarray, k: int) -> np.ndarray:
    """Top-k binary on 2D input (B, N). Returns (B, N) float32 0/1."""
    B, n = activations.shape
    if k >= n:
        return np.ones((B, n), dtype=np.float32)
    idx = np.argpartition(-activations, kth=k - 1, axis=1)[:, :k]
    out = np.zeros((B, n), dtype=np.float32)
    rows = np.arange(B)[:, None]
    out[rows, idx] = 1.0
    return out


def k_wta_1d_np(activations: np.ndarray, k: int) -> np.ndarray:
    n = activations.shape[0]
    if k >= n:
        return np.ones(n, dtype=np.float32)
    idx = np.argpartition(-activations, kth=k - 1)[:k]
    out = np.zeros(n, dtype=np.float32)
    out[idx] = 1.0
    return out


def schema_offset(schema_id: np.ndarray, N: int) -> int:
    arr = schema_id.astype(np.int8)
    h = hashlib.sha1(arr.tobytes()).digest()
    val = int.from_bytes(h[:8], "big")
    return val % N


# -------------------------- generation --------------------------

def generate_clusters(seed: int, K: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    shared = rng.randn(N_DIM).astype(np.float32)
    shared /= max(np.linalg.norm(shared), 1e-12)
    centers = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        private = rng.randn(N_DIM).astype(np.float32)
        private = private - (private @ shared) * shared
        private /= max(np.linalg.norm(private), 1e-12)
        c = (float(np.sqrt(BETWEEN_CLUSTER_COSINE)) * shared +
             float(np.sqrt(max(0.0, 1.0 - BETWEEN_CLUSTER_COSINE))) * private)
        c /= max(np.linalg.norm(c), 1e-12)
        centers[k] = c

    atoms = np.zeros((K * N_PER_CLUSTER, N_DIM), dtype=np.float32)
    labels = np.zeros(K * N_PER_CLUSTER, dtype=np.int64)
    for k in range(K):
        for i in range(N_PER_CLUSTER):
            noise = rng.randn(N_DIM).astype(np.float32)
            noise /= max(np.linalg.norm(noise), 1e-12)
            atom = centers[k] + WITHIN_CLUSTER_NOISE * noise
            atom /= max(np.linalg.norm(atom), 1e-12)
            atoms[k * N_PER_CLUSTER + i] = atom
            labels[k * N_PER_CLUSTER + i] = k
    return atoms, labels, centers


def make_W_schema(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 31337)
    W = rng.randn(N_DIM, N_DIM).astype(np.float32)
    norms = np.linalg.norm(W, axis=1, keepdims=True)
    return (W / np.maximum(norms, 1e-12)).astype(np.float32)


def make_schema_ids(seed: int, K: int) -> np.ndarray:
    rng = np.random.default_rng(seed + 7919)
    return (rng.integers(0, 2, size=(K, N_DIM)).astype(np.float32) * 2.0 - 1.0)


# -------------------------- bundle builders --------------------------

def build_perm_bundle(centers: np.ndarray, schema_ids: np.ndarray,
                       W: np.ndarray, k_density: int) -> Tuple[np.ndarray, List[int]]:
    """S = sum_k roll(k-WTA(W @ centers_k, k_density), offset_k)."""
    K = centers.shape[0]
    acts = (W @ centers.T).T  # (K, N)
    sparse_codes = k_wta_batched_np(acts, k_density)  # (K, N)
    offsets: List[int] = []
    S = np.zeros(N_DIM, dtype=np.float32)
    for k in range(K):
        off = schema_offset(schema_ids[k], N_DIM)
        S = S + np.roll(sparse_codes[k], off)
        offsets.append(off)
    return S, offsets


def build_proto_centroid_bundle(centers: np.ndarray,
                                  schema_ids: np.ndarray) -> np.ndarray:
    sign_c = np.sign(centers)
    sign_c[sign_c == 0.0] = 1.0
    bound = schema_ids * sign_c  # (K, N)
    return bound.sum(axis=0)


def build_diag_random_perm_bundle(schema_ids: np.ndarray,
                                    seed: int, k_density: int) -> Tuple[np.ndarray, List[int]]:
    K = schema_ids.shape[0]
    rng = np.random.default_rng(seed + 99999)
    codes = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        idx = rng.choice(N_DIM, size=min(k_density, N_DIM), replace=False)
        codes[k, idx] = 1.0
    offsets: List[int] = []
    S = np.zeros(N_DIM, dtype=np.float32)
    for k in range(K):
        off = schema_offset(schema_ids[k], N_DIM)
        S = S + np.roll(codes[k], off)
        offsets.append(off)
    return S, offsets


# -------------------------- query scoring --------------------------

def make_test_queries(atoms: np.ndarray, labels: np.ndarray, K: int,
                       seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    queries = []
    true_labels = []
    for c in range(K):
        members = atoms[labels == c]
        for q_i in range(N_QUERIES_PER_CLUSTER):
            base_idx = q_i % len(members)
            noise = rng.randn(N_DIM).astype(np.float32)
            noise /= max(np.linalg.norm(noise), 1e-12)
            q = members[base_idx] + 0.30 * noise
            q /= max(np.linalg.norm(q), 1e-12)
            queries.append(q)
            true_labels.append(c)
    return np.stack(queries, axis=0), np.array(true_labels, dtype=np.int64)


def score_perm_bundled(queries: np.ndarray, S_bundle: np.ndarray,
                        offsets: List[int], W: np.ndarray, K: int,
                        k_density: int) -> np.ndarray:
    """Returns scores (Q, K)."""
    acts_q = (W @ queries.T).T  # (Q, N)
    q_sparse = k_wta_batched_np(acts_q, k_density)  # (Q, N)
    unshifted = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        unshifted[k] = np.roll(S_bundle, -offsets[k])
    return q_sparse @ unshifted.T  # (Q, K)


def score_proto_centroid_bundled(queries: np.ndarray, C_bundle: np.ndarray,
                                    schema_ids: np.ndarray, K: int) -> np.ndarray:
    q_norm = queries / (np.linalg.norm(queries, axis=1, keepdims=True) + 1e-8)
    probes = schema_ids * C_bundle[None, :]  # (K, N)
    p_bip = np.sign(probes)
    p_bip[p_bip == 0.0] = 1.0
    p_norm = p_bip / (np.linalg.norm(p_bip, axis=1, keepdims=True) + 1e-8)
    return q_norm @ p_norm.T  # (Q, K)


def measure_arm_recall(arm: str, K: int, k_density: int, queries: np.ndarray,
                         true_labels: np.ndarray, centers: np.ndarray,
                         schema_ids: np.ndarray, W: np.ndarray,
                         S_perm: np.ndarray, offsets_perm: List[int],
                         C_proto: np.ndarray,
                         S_diag: np.ndarray, offsets_diag: List[int]) -> float:
    if arm == "ARM_PERM_K_VARIED":
        scores = score_perm_bundled(queries, S_perm, offsets_perm, W, K, k_density)
    elif arm == "ARM_PROTOTYPE_DENSE":
        scores = score_proto_centroid_bundled(queries, C_proto, schema_ids, K)
    elif arm == "ARM_DIAG_RANDOM":
        scores = score_perm_bundled(queries, S_diag, offsets_diag, W, K, k_density)
    else:
        raise ValueError("unknown arm %s" % arm)
    preds = np.argmax(scores, axis=1)
    hits = int((preds == true_labels).sum())
    return float(hits) / max(true_labels.shape[0], 1)


# -------------------------- run one --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    # Nested: per_arm[k_density][K_schema] = recall
    per_arm: Dict[str, Dict[str, Dict[str, float]]] = {
        arm: {str(kd): {} for kd in K_DENSITY_SWEEP} for arm in EXPECTED_ARMS
    }

    for K in K_SCHEMA_SWEEP:
        atoms, labels, centers = generate_clusters(seed, K)
        W = make_W_schema(seed)
        schema_ids = make_schema_ids(seed, K)
        C_proto = build_proto_centroid_bundle(centers, schema_ids)
        queries, true_labels = make_test_queries(atoms, labels, K, seed=seed * 1000 + K)

        for k_density in K_DENSITY_SWEEP:
            S_perm, offs_perm = build_perm_bundle(centers, schema_ids, W, k_density)
            S_diag, offs_diag = build_diag_random_perm_bundle(schema_ids, seed, k_density)

            for arm in EXPECTED_ARMS:
                recall = measure_arm_recall(arm, K, k_density, queries, true_labels,
                                              centers, schema_ids, W,
                                              S_perm, offs_perm, C_proto,
                                              S_diag, offs_diag)
                per_arm[arm][str(k_density)][str(K)] = recall
                print("  [seed=%d K=%d k=%d %s] recall@1=%.3f" % (
                    seed, K, k_density, arm, recall), flush=True)

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_DIM,
        "K_DENSITY_SWEEP": K_DENSITY_SWEEP,
        "K_SCHEMA_SWEEP": K_SCHEMA_SWEEP,
        "N_PER_CLUSTER": N_PER_CLUSTER,
        "BETWEEN_CLUSTER_COSINE": BETWEEN_CLUSTER_COSINE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_k_K_recall": per_arm,
        "elapsed_s": elapsed,
        "device": "cpu",
    }


# -------------------------- aggregate + verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    # summary[arm][k_density_str][K_schema_str] = {mean, std, per_seed}
    summary: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    for arm in EXPECTED_ARMS:
        summary[arm] = {}
        for kd in K_DENSITY_SWEEP:
            summary[arm][str(kd)] = {}
            for K in K_SCHEMA_SWEEP:
                vals = [float(per_seed[s]["per_arm_k_K_recall"][arm][str(kd)].get(str(K), 0.0))
                        for s in seeds_sorted]
                summary[arm][str(kd)][str(K)] = {
                    "mean": float(np.mean(vals)),
                    "std": float(np.std(vals)) if n_seeds > 1 else 0.0,
                    "per_seed": vals,
                }

    # Find best k* at K=100 and K=500 for PERM arm
    best = {}
    for K in K_SCHEMA_SWEEP:
        perm_vals = [(kd, summary["ARM_PERM_K_VARIED"][str(kd)][str(K)]["mean"])
                     for kd in K_DENSITY_SWEEP]
        proto_val = summary["ARM_PROTOTYPE_DENSE"][str(K_DENSITY_SWEEP[0])][str(K)]["mean"]
        diag_max = max(summary["ARM_DIAG_RANDOM"][str(kd)][str(K)]["mean"]
                       for kd in K_DENSITY_SWEEP)
        best_kd, best_perm = max(perm_vals, key=lambda x: x[1])
        best[str(K)] = {
            "best_k_density": int(best_kd),
            "best_perm_recall": float(best_perm),
            "proto_recall": float(proto_val),
            "perm_minus_proto": float(best_perm - proto_val),
            "diag_max_recall": float(diag_max),
        }

    perm_K100 = best["100"]["best_perm_recall"] if "100" in best else 0.0
    proto_K100 = best["100"]["proto_recall"] if "100" in best else 0.0
    diag_K100 = best["100"]["diag_max_recall"] if "100" in best else 0.0
    delta_K100 = best["100"]["perm_minus_proto"] if "100" in best else -1.0
    best_kd_K100 = best["100"]["best_k_density"] if "100" in best else -1

    perm_K500 = best["500"]["best_perm_recall"] if "500" in best else 0.0
    proto_K500 = best["500"]["proto_recall"] if "500" in best else 0.0
    diag_K500 = best["500"]["diag_max_recall"] if "500" in best else 0.0
    delta_K500 = best["500"]["perm_minus_proto"] if "500" in best else -1.0
    best_kd_K500 = best["500"]["best_k_density"] if "500" in best else -1

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # HARD_FAIL early: diag dominates
    if diag_K100 >= perm_K100 and diag_K500 >= perm_K500:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "DIAG_FALSE_ACCEPT: diag_K100=%.3f >= perm_K100=%.3f AND "
            "diag_K500=%.3f >= perm_K500=%.3f (structure not load-bearing)"
            % (diag_K100, perm_K100, diag_K500, perm_K500))
    elif (perm_K100 >= HP_PERM_FLOOR_K100 and delta_K100 >= HP_PERM_OVER_PROTO_K100) or \
            (perm_K500 >= HP_PERM_FLOOR_K500 and delta_K500 >= HP_PERM_OVER_PROTO_K500):
        verdict = "HARD_PASS"
        verdict_reason = (
            "SEMI_SPARSE_FOUND: K=100 best_k=%d perm=%.3f proto=%.3f delta=%.3f; "
            "K=500 best_k=%d perm=%.3f proto=%.3f delta=%.3f"
            % (best_kd_K100, perm_K100, proto_K100, delta_K100,
               best_kd_K500, perm_K500, proto_K500, delta_K500))
    elif delta_K100 >= MIDDLE_PERM_OVER_PROTO or delta_K500 >= MIDDLE_PERM_OVER_PROTO:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "WEAK_DENSITY_PREFERENCE: K=100 delta=%.3f (best_k=%d) K=500 delta=%.3f (best_k=%d); "
            "below HARD_PASS thresholds"
            % (delta_K100, best_kd_K100, delta_K500, best_kd_K500))
    else:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "NO_DENSITY_LIFT: K=100 best_perm=%.3f <= proto=%.3f AND "
            "K=500 best_perm=%.3f <= proto=%.3f (substrate prefers dense; close sparse-bundled)"
            % (perm_K100, proto_K100, perm_K500, proto_K500))

    # Per-(k, K) summary string
    summary_lines = []
    for K in K_SCHEMA_SWEEP:
        line = "K=%d:" % K
        for kd in K_DENSITY_SWEEP:
            perm = summary["ARM_PERM_K_VARIED"][str(kd)][str(K)]["mean"]
            line += " k%d=%.3f" % (kd, perm)
        proto = summary["ARM_PROTOTYPE_DENSE"][str(K_DENSITY_SWEEP[0])][str(K)]["mean"]
        line += " proto=%.3f" % proto
        summary_lines.append(line)

    verdict_msg = "%s | %s | %s | n_seeds=%d" % (
        verdict, verdict_reason, " | ".join(summary_lines), n_seeds)

    completed_units = (n_seeds * len(EXPECTED_ARMS) *
                       len(K_DENSITY_SWEEP) * len(K_SCHEMA_SWEEP))
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm_k_K_recall_summary": summary,
        "best_per_K_summary": best,
        "n_seeds_complete": n_seeds,
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
        "device": "cpu",
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                            "STARTED: pid=%d mode=%s device=cpu" % (
                                os.getpid(), RUN_MODE),
                            extra={"_phase": "init",
                                   "expected_arms": list(EXPECTED_ARMS),
                                   "expected_seeds": SEEDS,
                                   "K_density_sweep": K_DENSITY_SWEEP,
                                   "K_schema_sweep": K_SCHEMA_SWEEP,
                                   "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d k_density=%s K_schema=%s seeds=%s expected_units=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, K_DENSITY_SWEEP, K_SCHEMA_SWEEP, SEEDS,
        EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_k_K_recall" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_k_K_recall"]
                for kd in K_DENSITY_SWEEP:
                    assert str(kd) in r["per_arm_k_K_recall"][arm]
                    for K in K_SCHEMA_SWEEP:
                        assert str(K) in r["per_arm_k_K_recall"][arm][str(kd)]
            kd0 = K_DENSITY_SWEEP[0]
            K0 = K_SCHEMA_SWEEP[0]
            perm = r["per_arm_k_K_recall"]["ARM_PERM_K_VARIED"][str(kd0)][str(K0)]
            proto = r["per_arm_k_K_recall"]["ARM_PROTOTYPE_DENSE"][str(kd0)][str(K0)]
            diag = r["per_arm_k_K_recall"]["ARM_DIAG_RANDOM"][str(kd0)][str(K0)]
            print("[selftest] K=%d k=%d perm=%.3f proto=%.3f diag=%.3f" % (
                K0, kd0, perm, proto, diag), flush=True)
            # Selftest discriminator: at K=50, well-separated, PROTO should dominate
            # (small K = dense baseline trivially wins). PERM and DIAG roughly similar.
            # The KEY discriminator: PROTO > DIAG (sanity check architecture)
            assert proto > diag, (
                "SELFTEST_FAIL: proto=%.3f <= diag=%.3f at K=50 (architecture broken)"
                % (proto, diag))
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                    "SELFTEST_OK: 3-arm perm=%.3f proto=%.3f diag=%.3f"
                                    % (perm, proto, diag))
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                    "SELFTEST_FAIL: %s" % e,
                                    extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    per_seed_results: Dict[str, Dict[str, Any]] = {}
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                                "RUNNING: seed=%d (%d/%d)" % (
                                    seed, i + 1, len(SEEDS)),
                                extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        per_seed_results[str(seed)] = result
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v5_k_density_sweep_semi_sparse"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
