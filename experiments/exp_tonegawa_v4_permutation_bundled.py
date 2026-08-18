"""tonegawa_v4_permutation_bundled -- TOP-1 from 3x drill 2026-06-27.

Prereg: preregs/2026-06-27_tonegawa_v4_permutation_bundled.md
Drill: notes/research_drill_3x_tonegawa_v3_BUNDLED_revival_2026-06-27.md

ROOT CAUSE OF v3 HARD_FAIL:
  v3 used XOR-bind on sparse k-WTA codes. XOR(dense_schema_id, sparse_code) FLOODS
  the sparse channel (output has Hamming weight ~N/2, not ~k). Sparseness destroyed
  in the bound representation. Theoretical K_max <= 3 SNR cap REGARDLESS of N.
  Result: total collapse at K=100 was inevitable from theory.

FIX (Plate 1995 + Kanerva BSC for sparse codes):
  Permutation-bind via cyclic shift. PRESERVES sparseness exactly. No Gaussian-noise
  floor from dense superposition. Theoretical capacity ~ N/(k*log N) ~ 13,000 at our
  N=2048, k=20.

ARCHITECTURE:
  For each schema k in 1..K:
    sparse_code_k = k-WTA(W @ centroid_k, k=20) sparse {0,1}^N
    offset_k = hash(schema_id_k) % N
    shifted_k = roll(sparse_code_k, offset_k)        # cyclic permutation
  Bundle: S = sum_k shifted_k        # integer-valued sum, sparseness ~k*K/N retained
  Query (given schema_q expected): unshift S by -offset_q; k-WTA cleanup; match query

ARMS (4 = 3 mandatory + 1 diagnostic):
  ARM_PROTOTYPE_CENTROID_BUNDLED   dense baseline (v3 winner at small K)
  ARM_XOR_BUNDLED_REGRESSION       v3 sparse+XOR mechanism (regression-sanity for collapse)
  ARM_PERMUTATION_BUNDLED          TOP-1: sparse + cyclic-shift bind (predicted winner)
  ARM_DIAG_RANDOM_SPARSE_BUNDLED   false-accept floor (random codes, permutation bind)

DISCRIMINATORS (per drill spec):
  HARD_PASS: PERM recall@1 >= 0.55 at K=500
             AND PERM > PROTO by >= +0.10 at K=500
             AND PERM > XOR  by >= +0.30 at K=500   (proves perm fixes XOR collapse)
  MIDDLE_BAND: PERM recall in [0.30, 0.55) at K=500 OR smaller positive lift
  HARD_FAIL: PERM <= PROTO at K=500 (mechanism doesn't beat dense centroid)

REGIME:
  N_DIM=2048; k=20; K in {25, 100, 500, 2000}; 5 seeds full

SMOKE DISCIPLINE (META_RULE_K + 2026-06-26 discriminator-must-survive-scale):
  Smoke spans K=25 (saturation regime) + K=100 (where XOR collapse fires; where
  PERM lift should emerge per Angle C prediction PERM~0.95, XOR~0.0, PROTO~0.50).
  If smoke at K=100 doesn't show PERM > XOR by >= +0.30, DO NOT dispatch full.

CARDINALITY_OK:
  EXPECTED_N_UNITS_full = 4 arms * 4 K * 5 seeds = 80
  EXPECTED_N_UNITS_smoke = 4 * 2 * 2 = 16
  EXPECTED_N_UNITS_selftest = 4 * 1 * 1 = 4

ASCII-only; no emojis; no em-dashes. META_RULE_X main-guard + L1/L2/L4 hardening.
Author: exp_dev 2026-06-27 (Research-drill TOP-1 dispatch).
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
    from experiments._seed_checkpoint import (
        write_partial_key,
    )
except Exception:
    # Fallback inline if helper not available
    def write_partial_key(out_dir: Path, seed: int, payload: Dict[str, Any]) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / ("partial_seed_%d.json" % seed)).write_text(
            json.dumps(payload, indent=2), encoding="utf-8")


ANCHOR_NAME = "tonegawa_v4_permutation_bundled"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands (per drill TOP-1 spec)
HP_PERM_RECALL_AT_K500 = 0.55
HP_PERM_OVER_PROTO_DELTA = 0.10
HP_PERM_OVER_XOR_DELTA = 0.30
MIDDLE_RECALL_LO = 0.30
SMOKE_PERM_OVER_XOR_AT_K100 = 0.30  # smoke discriminator must fire

EXPECTED_ARMS = (
    "ARM_PROTOTYPE_CENTROID_BUNDLED",
    "ARM_XOR_BUNDLED_REGRESSION",
    "ARM_PERMUTATION_BUNDLED",
    "ARM_DIAG_RANDOM_SPARSE_BUNDLED",
)

# Regime
if SELF_TEST_MODE:
    N_DIM = 512
    K_SPARSE = 10
    N_PER_CLUSTER = 4
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.50
    K_SWEEP = [25]
    SEEDS = [7]
    N_QUERIES_PER_CLUSTER = 3
elif RUN_MODE == "smoke":
    # Smoke MUST FIRE DISCRIMINATOR: K=100 is where XOR collapses (per theory)
    # and PERM should show clear lift. K=25 is saturation-regime sanity.
    N_DIM = 1024
    K_SPARSE = 16
    N_PER_CLUSTER = 6
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.50
    K_SWEEP = [25, 100]
    SEEDS = [7, 17]
    N_QUERIES_PER_CLUSTER = 8
else:
    # Full: drill spec N=2048, k=20, K-sweep [25,100,500,2000], 5 seeds
    N_DIM = 2048
    K_SPARSE = 20
    N_PER_CLUSTER = 10
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.60
    K_SWEEP = [25, 100, 500, 2000]
    SEEDS = [7, 17, 23, 41, 53]
    N_QUERIES_PER_CLUSTER = 15

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(K_SWEEP) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,KSP=%d,NPC=%d,BCC=%.2f,WCN=%.2f,"
    "K_SWEEP=%s,SEEDS=%s,NQPC=%d,"
    "HP_perm_K500>=%.2f,HP_perm-proto>=%.2f,HP_perm-xor>=%.2f,"
    "RUN_MODE=%s,hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK+SMOKE_FIRES_DISCRIMINATOR"
) % (
    ANCHOR_NAME, N_DIM, K_SPARSE, N_PER_CLUSTER,
    BETWEEN_CLUSTER_COSINE, WITHIN_CLUSTER_NOISE,
    K_SWEEP, SEEDS, N_QUERIES_PER_CLUSTER,
    HP_PERM_RECALL_AT_K500, HP_PERM_OVER_PROTO_DELTA, HP_PERM_OVER_XOR_DELTA,
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
            "_hardening_marker": "v4_permutation_bundled",
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
            "_hardening_marker": "v4_permutation_bundled_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar_unit(n: int, g: np.random.Generator) -> np.ndarray:
    return (g.integers(0, 2, size=n).astype(np.float32) * 2.0 - 1.0)


def xor_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """XOR-binding for bipolar vectors: elementwise multiply."""
    return (a * b).astype(np.float32)


def k_wta(activations: np.ndarray, k: int) -> np.ndarray:
    """Top-k binary: returns float32 0/1 vector with exactly k ones."""
    n = activations.shape[0]
    if k >= n:
        return np.ones(n, dtype=np.float32)
    top_k_idx = np.argpartition(-activations, k)[:k]
    out = np.zeros(n, dtype=np.float32)
    out[top_k_idx] = 1.0
    return out


def kwta_to_bipolar(sparse: np.ndarray) -> np.ndarray:
    return (sparse * 2.0 - 1.0).astype(np.float32)


def schema_offset(schema_id: np.ndarray, N: int) -> int:
    """Deterministic offset from a schema_id vector via SHA1 hash mod N."""
    # Hash the bytes of the schema_id (signs only -> bytes), modulo N
    h = hashlib.sha1(schema_id.astype(np.int8).tobytes()).digest()
    # Take first 8 bytes -> big-endian int -> mod N
    val = int.from_bytes(h[:8], "big")
    return val % N


# -------------------------- generation --------------------------

def generate_clusters(seed: int, K: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate K clusters; returns (atoms, labels, centers).
    Centers L2-normalized; atoms = center + within-cluster noise then L2-normalized.
    """
    rng = np.random.RandomState(seed)
    shared = rng.randn(N_DIM).astype(np.float64)
    shared /= max(np.linalg.norm(shared), 1e-12)
    centers = np.zeros((K, N_DIM), dtype=np.float64)
    for k in range(K):
        private = rng.randn(N_DIM).astype(np.float64)
        private = private - (private @ shared) * shared
        private /= max(np.linalg.norm(private), 1e-12)
        c = (float(np.sqrt(BETWEEN_CLUSTER_COSINE)) * shared +
             float(np.sqrt(max(0.0, 1.0 - BETWEEN_CLUSTER_COSINE))) * private)
        c /= max(np.linalg.norm(c), 1e-12)
        centers[k] = c

    atoms = np.zeros((K * N_PER_CLUSTER, N_DIM), dtype=np.float64)
    labels = np.zeros(K * N_PER_CLUSTER, dtype=np.int64)
    for k in range(K):
        for i in range(N_PER_CLUSTER):
            noise = rng.randn(N_DIM).astype(np.float64)
            noise /= max(np.linalg.norm(noise), 1e-12)
            atom = centers[k] + WITHIN_CLUSTER_NOISE * noise
            atom /= max(np.linalg.norm(atom), 1e-12)
            atoms[k * N_PER_CLUSTER + i] = atom
            labels[k * N_PER_CLUSTER + i] = k
    return atoms, labels, centers


def make_W_schema(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 31337)
    W = rng.randn(N_DIM, N_DIM).astype(np.float64)
    norms = np.linalg.norm(W, axis=1, keepdims=True)
    W = W / np.maximum(norms, 1e-12)
    return W


def make_schema_ids(seed: int, K: int) -> np.ndarray:
    """K random bipolar schema-IDs, shape (K, N_DIM). Used for XOR arms + hash for PERM."""
    g = np.random.default_rng(seed + 7919)
    out = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        out[k] = bipolar_unit(N_DIM, g)
    return out


# -------------------------- bundle builders --------------------------

def build_perm_bundle(centers: np.ndarray, schema_ids: np.ndarray,
                       W: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray], List[int]]:
    """TOP-1: permutation-bind sparse codes.
       S = sum_k roll(sparse_code_k, offset_k)
    Returns (S, sparse_codes, offsets)."""
    K = centers.shape[0]
    S = np.zeros(N_DIM, dtype=np.float32)
    codes: List[np.ndarray] = []
    offsets: List[int] = []
    for k in range(K):
        acts = W @ centers[k]
        sparse = k_wta(acts, K_SPARSE)
        off = schema_offset(schema_ids[k], N_DIM)
        shifted = np.roll(sparse, off).astype(np.float32)
        S = S + shifted
        codes.append(sparse)
        offsets.append(off)
    return S, codes, offsets


def build_xor_bundle_v3(centers: np.ndarray, schema_ids: np.ndarray,
                         W: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
    """v3 regression arm: XOR-bind sparse codes (the BROKEN mechanism)."""
    K = centers.shape[0]
    S = np.zeros(N_DIM, dtype=np.float32)
    codes: List[np.ndarray] = []
    for k in range(K):
        acts = W @ centers[k]
        sparse = k_wta(acts, K_SPARSE)
        bip = kwta_to_bipolar(sparse)
        bound = xor_bind(schema_ids[k], bip)
        S = S + bound
        codes.append(sparse)
    return S, codes


def build_proto_centroid_bundle(centers: np.ndarray,
                                 schema_ids: np.ndarray) -> np.ndarray:
    """Dense centroid bundle, XOR-bound (v3 winner at small K).
       C = sum_k XOR(schema_id_k, sign(centroid_k))"""
    K = centers.shape[0]
    C = np.zeros(N_DIM, dtype=np.float32)
    for k in range(K):
        c_bip = np.sign(centers[k]).astype(np.float32)
        c_bip = np.where(c_bip == 0.0, 1.0, c_bip)
        bound = xor_bind(schema_ids[k], c_bip)
        C = C + bound
    return C


def build_diag_random_perm_bundle(schema_ids: np.ndarray,
                                    seed: int) -> Tuple[np.ndarray, List[np.ndarray], List[int]]:
    """Diagnostic: PERM-bundle with RANDOM sparse codes (no structure).
       Tests false-accept floor for the permutation mechanism."""
    K = schema_ids.shape[0]
    g = np.random.default_rng(seed + 99999)
    S = np.zeros(N_DIM, dtype=np.float32)
    codes: List[np.ndarray] = []
    offsets: List[int] = []
    for k in range(K):
        idx = g.choice(N_DIM, size=min(K_SPARSE, N_DIM), replace=False)
        sparse = np.zeros(N_DIM, dtype=np.float32)
        sparse[idx] = 1.0
        off = schema_offset(schema_ids[k], N_DIM)
        shifted = np.roll(sparse, off).astype(np.float32)
        S = S + shifted
        codes.append(sparse)
        offsets.append(off)
    return S, codes, offsets


# -------------------------- query scoring (FAIRNESS: all read same way) --------------------------

def score_perm_bundled(query_centroid: np.ndarray, S_bundle: np.ndarray,
                        schema_ids: np.ndarray, offsets: List[int],
                        W: np.ndarray, K: int) -> np.ndarray:
    """For each candidate k: unshift S by -offset_k -> expected sparse_code_k + noise.
    Score by overlap with query's k-WTA sparse code (dot-product on 0/1)."""
    acts_q = W @ query_centroid
    q_sparse = k_wta(acts_q, K_SPARSE)  # {0,1}^N
    scores = np.zeros(K, dtype=np.float32)
    for k in range(K):
        unshifted = np.roll(S_bundle, -offsets[k])  # expected: sparse_code_k + noise
        # Score = sum of unshifted at query's active bits (overlap)
        scores[k] = float(np.sum(unshifted * q_sparse))
    return scores


def score_xor_bundled(query_centroid: np.ndarray, S_bundle: np.ndarray,
                       schema_ids: np.ndarray, W: np.ndarray, K: int) -> np.ndarray:
    """v3 mechanism: probe = XOR(schema_id_k, S); score = dot(probe, query_bipolar)."""
    acts_q = W @ query_centroid
    q_sparse = k_wta(acts_q, K_SPARSE)
    q_bip = kwta_to_bipolar(q_sparse)
    scores = np.zeros(K, dtype=np.float32)
    for k in range(K):
        probe = xor_bind(schema_ids[k], S_bundle)
        scores[k] = float(np.sum(probe * q_bip)) / float(max(K_SPARSE, 1))
    return scores


def score_proto_centroid_bundled(query_centroid: np.ndarray, C_bundle: np.ndarray,
                                   schema_ids: np.ndarray, K: int) -> np.ndarray:
    """Dense baseline: probe = XOR(schema_id_k, C); cosine to query centroid."""
    q_unit = query_centroid / (np.linalg.norm(query_centroid) + 1e-8)
    scores = np.zeros(K, dtype=np.float32)
    for k in range(K):
        probe = xor_bind(schema_ids[k], C_bundle)
        p_bip = np.sign(probe).astype(np.float32)
        p_bip = np.where(p_bip == 0.0, 1.0, p_bip)
        p_unit = p_bip / (np.linalg.norm(p_bip) + 1e-8)
        scores[k] = float(np.dot(p_unit, q_unit))
    return scores


def score_diag_random_perm_bundled(query_centroid: np.ndarray, S_bundle: np.ndarray,
                                     offsets: List[int], W: np.ndarray, K: int) -> np.ndarray:
    """Same surface as PERM but bundle was built from random codes (no structure)."""
    acts_q = W @ query_centroid
    q_sparse = k_wta(acts_q, K_SPARSE)
    scores = np.zeros(K, dtype=np.float32)
    for k in range(K):
        unshifted = np.roll(S_bundle, -offsets[k])
        scores[k] = float(np.sum(unshifted * q_sparse))
    return scores


# -------------------------- run one --------------------------

def make_test_query(atom: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    noise = rng.randn(N_DIM).astype(np.float64)
    noise /= max(np.linalg.norm(noise), 1e-12)
    q = atom + 0.30 * noise
    q /= max(np.linalg.norm(q), 1e-12)
    return q.astype(np.float32)


def measure_recall_at_top1(arm: str, K: int, seed: int,
                            atoms: np.ndarray, labels: np.ndarray,
                            centers: np.ndarray, schema_ids: np.ndarray,
                            W: np.ndarray,
                            S_perm: np.ndarray, offsets_perm: List[int],
                            S_xor: np.ndarray,
                            C_proto: np.ndarray,
                            S_diag: np.ndarray, offsets_diag: List[int]) -> float:
    hits = 0
    n_q = 0
    for c in range(K):
        members = atoms[labels == c]
        for q_i in range(N_QUERIES_PER_CLUSTER):
            base_idx = q_i % len(members)
            q = make_test_query(members[base_idx], seed=seed + c * 100 + q_i)
            if arm == "ARM_PERMUTATION_BUNDLED":
                scores = score_perm_bundled(q, S_perm, schema_ids, offsets_perm, W, K)
            elif arm == "ARM_XOR_BUNDLED_REGRESSION":
                scores = score_xor_bundled(q, S_xor, schema_ids, W, K)
            elif arm == "ARM_PROTOTYPE_CENTROID_BUNDLED":
                scores = score_proto_centroid_bundled(q, C_proto, schema_ids, K)
            elif arm == "ARM_DIAG_RANDOM_SPARSE_BUNDLED":
                scores = score_diag_random_perm_bundled(q, S_diag, offsets_diag, W, K)
            else:
                raise ValueError("unknown arm %s" % arm)
            pred = int(np.argmax(scores))
            if pred == c:
                hits += 1
            n_q += 1
    return hits / max(n_q, 1)


def run_one_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    per_arm_per_K: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}

    for K in K_SWEEP:
        atoms, labels, centers = generate_clusters(seed, K)
        W = make_W_schema(seed)
        schema_ids = make_schema_ids(seed, K)
        S_perm, codes_perm, offs_perm = build_perm_bundle(centers, schema_ids, W)
        S_xor, codes_xor = build_xor_bundle_v3(centers, schema_ids, W)
        C_proto = build_proto_centroid_bundle(centers, schema_ids)
        S_diag, codes_diag, offs_diag = build_diag_random_perm_bundle(schema_ids, seed)

        for arm in EXPECTED_ARMS:
            recall = measure_recall_at_top1(
                arm, K, seed, atoms, labels, centers, schema_ids, W,
                S_perm, offs_perm, S_xor, C_proto, S_diag, offs_diag)
            per_arm_per_K[arm][str(K)] = recall
            print("  [seed=%d K=%d %s] recall@1=%.3f" % (seed, K, arm, recall),
                  flush=True)

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_DIM,
        "K_SWEEP": K_SWEEP,
        "K_SPARSE": K_SPARSE,
        "N_PER_CLUSTER": N_PER_CLUSTER,
        "BETWEEN_CLUSTER_COSINE": BETWEEN_CLUSTER_COSINE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_K_recall": per_arm_per_K,
        "elapsed_s": elapsed,
    }


# -------------------------- aggregate + verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    # Aggregate per-arm per-K recall (mean + std across seeds)
    summary_recall: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        summary_recall[arm] = {}
        for K in K_SWEEP:
            vals = [float(per_seed[s]["per_arm_per_K_recall"][arm].get(str(K), 0.0))
                    for s in seeds_sorted]
            summary_recall[arm][str(K)] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)) if n_seeds > 1 else 0.0,
                "per_seed": vals,
            }

    # Choose evaluation K: K=500 if present (full), else largest K in sweep (smoke)
    eval_K = 500 if 500 in K_SWEEP else K_SWEEP[-1]
    eval_K_str = str(eval_K)

    perm_r = summary_recall["ARM_PERMUTATION_BUNDLED"][eval_K_str]["mean"]
    xor_r = summary_recall["ARM_XOR_BUNDLED_REGRESSION"][eval_K_str]["mean"]
    proto_r = summary_recall["ARM_PROTOTYPE_CENTROID_BUNDLED"][eval_K_str]["mean"]
    diag_r = summary_recall["ARM_DIAG_RANDOM_SPARSE_BUNDLED"][eval_K_str]["mean"]

    perm_minus_proto = perm_r - proto_r
    perm_minus_xor = perm_r - xor_r

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # HARD_FAIL: diag false-accept (random matches structure) -- false positive guard
    if diag_r >= perm_r:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "DIAG_FALSE_ACCEPT_at_K%d: diag_recall=%.3f >= perm_recall=%.3f "
            "(structure not load-bearing)" % (eval_K, diag_r, perm_r))
    # HARD_FAIL: mechanism null
    elif perm_r <= proto_r:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "MECHANISM_NULL_at_K%d: perm_recall=%.3f <= proto_recall=%.3f "
            "(permutation doesn't beat dense centroid)" % (eval_K, perm_r, proto_r))
    # HARD_PASS: all three discriminators fire
    elif (perm_r >= HP_PERM_RECALL_AT_K500 and
            perm_minus_proto >= HP_PERM_OVER_PROTO_DELTA and
            perm_minus_xor >= HP_PERM_OVER_XOR_DELTA):
        verdict = "HARD_PASS"
        verdict_reason = (
            "PERM_BUNDLED_LIFT_at_K%d: perm=%.3f (>= %.2f); perm-proto=%.3f (>= %.2f); "
            "perm-xor=%.3f (>= %.2f); diag=%.3f" % (
                eval_K, perm_r, HP_PERM_RECALL_AT_K500,
                perm_minus_proto, HP_PERM_OVER_PROTO_DELTA,
                perm_minus_xor, HP_PERM_OVER_XOR_DELTA, diag_r))
    elif MIDDLE_RECALL_LO <= perm_r < HP_PERM_RECALL_AT_K500:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "PARTIAL_LIFT_at_K%d: perm=%.3f in [%.2f, %.2f); perm-proto=%.3f perm-xor=%.3f"
            % (eval_K, perm_r, MIDDLE_RECALL_LO, HP_PERM_RECALL_AT_K500,
               perm_minus_proto, perm_minus_xor))
    elif perm_r < MIDDLE_RECALL_LO:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "PERM_FLOOR_at_K%d: perm=%.3f < %.2f (mechanism unable at this scale)"
            % (eval_K, perm_r, MIDDLE_RECALL_LO))

    # Build readable verdict_msg with per-K compact summary
    per_K_summary = []
    for K in K_SWEEP:
        per_K_summary.append(
            "K=%d perm=%.3f xor=%.3f proto=%.3f diag=%.3f" % (
                K,
                summary_recall["ARM_PERMUTATION_BUNDLED"][str(K)]["mean"],
                summary_recall["ARM_XOR_BUNDLED_REGRESSION"][str(K)]["mean"],
                summary_recall["ARM_PROTOTYPE_CENTROID_BUNDLED"][str(K)]["mean"],
                summary_recall["ARM_DIAG_RANDOM_SPARSE_BUNDLED"][str(K)]["mean"]))
    verdict_msg = "%s | %s | %s | n_seeds=%d" % (
        verdict, verdict_reason, " | ".join(per_K_summary), n_seeds)

    completed_units = n_seeds * len(EXPECTED_ARMS) * len(K_SWEEP)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm_per_K_recall_summary": summary_recall,
        "eval_K": eval_K,
        "perm_recall_at_eval_K": perm_r,
        "xor_recall_at_eval_K": xor_r,
        "proto_recall_at_eval_K": proto_r,
        "diag_recall_at_eval_K": diag_r,
        "perm_minus_proto": perm_minus_proto,
        "perm_minus_xor": perm_minus_xor,
        "n_seeds_complete": n_seeds,
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init",
                                  "expected_arms": list(EXPECTED_ARMS),
                                  "expected_seeds": SEEDS,
                                  "K_sweep": K_SWEEP,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d KSP=%d K_SWEEP=%s seeds=%s expected_units=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, K_SPARSE, K_SWEEP, SEEDS, EXPECTED_N_UNITS),
        flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_K_recall" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_K_recall"]
                for K in K_SWEEP:
                    assert str(K) in r["per_arm_per_K_recall"][arm]
            # Structural assertion: PERM should NOT be dominated by DIAG at smallest K (selftest sanity)
            perm_recall = r["per_arm_per_K_recall"]["ARM_PERMUTATION_BUNDLED"][str(K_SWEEP[0])]
            diag_recall = r["per_arm_per_K_recall"]["ARM_DIAG_RANDOM_SPARSE_BUNDLED"][str(K_SWEEP[0])]
            print("[selftest] OK K=%d perm=%.3f xor=%.3f proto=%.3f diag=%.3f" % (
                K_SWEEP[0], perm_recall,
                r["per_arm_per_K_recall"]["ARM_XOR_BUNDLED_REGRESSION"][str(K_SWEEP[0])],
                r["per_arm_per_K_recall"]["ARM_PROTOTYPE_CENTROID_BUNDLED"][str(K_SWEEP[0])],
                diag_recall), flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: 4-arm perm-bundled K-sweep structured perm=%.3f diag=%.3f"
                                   % (perm_recall, diag_recall))
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
                               "RUNNING: seed=%d (%d/%d) K_SWEEP=%s" % (
                                   seed, i + 1, len(SEEDS), K_SWEEP),
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
    final["_hardening_marker"] = "v4_permutation_bundled"
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
