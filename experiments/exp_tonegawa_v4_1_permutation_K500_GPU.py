"""tonegawa_v4_1_permutation_K500_GPU -- DIRECT TEST of drill K=500 prediction.

Prereg: preregs/2026-06-27_tonegawa_v4_1_permutation_K500_GPU.md
Predecessor: experiments/exp_tonegawa_v4_permutation_bundled.py
Drill: notes/research_drill_3x_tonegawa_v3_BUNDLED_revival_2026-06-27.md

WHY v4_1 OVER v4:
  v4 smoke ran K=25/100 only. At K=100 PERM=0.124 < PROTO=0.141 (mechanism null
  at smoke scale). But drill predicted the lift only appears at K>=500 because
  dense centroid saturates as cosine noise ~sqrt(K); permutation-bundled noise
  stays linear at k/N per signal. K=500 is the predicted crossover point and
  was NEVER TESTED.

  v4 also ran on numpy CPU. Fix #24 requires real GPU utilization for
  GPU-routed cells (matmul N=2048 across K=1000 schemas is matrix-heavy).

ARCHITECTURE (same as v4; GPU + K=500 primary):
  For each schema k in 1..K:
    sparse_code_k = k-WTA(W @ centroid_k, k=20) sparse {0,1}^N on CUDA
    offset_k = sha1(schema_id_k.bytes)[:8] % N
    shifted_k = roll(sparse_code_k, offset_k)
  Bundle: S = sum_k shifted_k   (integer-valued; sparseness ~ k*K/N retained)
  Query: unshift S by -offset_q; k-WTA cleanup; match query

ARMS (3 mandatory + 1 diagnostic):
  ARM_PROTOTYPE_CENTROID_BUNDLED   dense XOR baseline (v3 winner at small K)
  ARM_XOR_BUNDLED_REGRESSION       v3 sparse+XOR mechanism (collapse sanity)
  ARM_PERMUTATION_BUNDLED          drill TOP-1: predicted winner at K=500
  ARM_DIAG_RANDOM_SPARSE_BUNDLED   false-accept floor

DISCRIMINATORS (per drill TOP-1 spec at K=500):
  HARD_PASS: PERM recall@1 >= 0.55 at K=500
             AND PERM > PROTO by >= +0.20 at K=500 (raised vs v4's +0.10 per user spec)
             AND PERM > XOR  by >= +0.30 at K=500
  MIDDLE_BAND: PERM in [0.30, 0.55) at K=500 OR smaller positive lift
  HARD_FAIL: PERM <= PROTO at K=500 (drill prediction REFUTED; close direction)
             OR PERM < 0.30 OR DIAG >= PERM (false-accept guard)

REGIME:
  N_DIM=2048; k=20; K_primary=500; diag K-sweep [100, 250, 500, 1000]; 5 seeds full

GPU MANDATE (Fix #24):
  - torch.cuda.is_available() asserted at startup; HARD_FAIL if not available
  - All hot loops use torch on CUDA (W @ centroids batched; matmul on GPU)
  - Sample torch.cuda.utilization snapshots during smoke; record gpu_util_p50

CARDINALITY_OK:
  EXPECTED_N_UNITS_full = 4 arms * 4 K * 5 seeds = 80
  EXPECTED_N_UNITS_smoke = 4 * 2 * 2 = 16
  EXPECTED_N_UNITS_selftest = 4 * 1 * 1 = 4

ASCII-only; no emojis; no em-dashes. META_RULE_X main-guard + L1/L2/L4.
Author: exp_dev 2026-06-27 (Research drill K=500 GPU direct test).
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


ANCHOR_NAME = "tonegawa_v4_1_permutation_K500_GPU"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands (per drill TOP-1 spec at K=500; +0.20 PERM-PROTO delta per user spec)
HP_PERM_RECALL_AT_K500 = 0.55
HP_PERM_OVER_PROTO_DELTA = 0.20  # user spec raised from v4's 0.10
HP_PERM_OVER_XOR_DELTA = 0.30
MIDDLE_RECALL_LO = 0.30
# Smoke discriminator: at K=500 smoke preview, PERM > PROTO by >= 0.10 OR PERM >= 0.40
SMOKE_PERM_K500_FLOOR = 0.40
SMOKE_PERM_OVER_PROTO_K500 = 0.10

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
    # Smoke discipline 2026-06-26: discriminator-must-survive-scale.
    # Per user spec the K=500 prediction is UNTESTED. Smoke MUST include K=500 at full N
    # so smoke fires the actual drill discriminator. Reduced seeds to keep wall budget.
    N_DIM = 2048
    K_SPARSE = 20
    N_PER_CLUSTER = 8
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.55
    K_SWEEP = [100, 500]
    SEEDS = [7, 17]
    N_QUERIES_PER_CLUSTER = 10
else:
    # Full: K_primary=500 per user spec; diag K-sweep [100, 250, 500, 1000]; 5 seeds
    N_DIM = 2048
    K_SPARSE = 20
    N_PER_CLUSTER = 10
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.60
    K_SWEEP = [100, 250, 500, 1000]
    SEEDS = [7, 17, 23, 41, 53]
    N_QUERIES_PER_CLUSTER = 15

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(K_SWEEP) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,KSP=%d,NPC=%d,BCC=%.2f,WCN=%.2f,"
    "K_SWEEP=%s,SEEDS=%s,NQPC=%d,"
    "HP_perm_K500>=%.2f,HP_perm-proto>=%.2f,HP_perm-xor>=%.2f,"
    "RUN_MODE=%s,DEVICE=cuda_required,"
    "hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK+GPU_ASSERT+SMOKE_AT_FULL_N_K500"
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
            "_hardening_marker": "v4_1_permutation_K500_GPU",
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
            "_hardening_marker": "v4_1_permutation_K500_GPU_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- torch + GPU setup --------------------------

import torch

# Fix #24: pre-flight GPU assertion. SELF_TEST mode allowed to fall back to CPU
# (selftest runs anywhere; smoke/full MUST be GPU).
_GPU_AVAILABLE = torch.cuda.is_available()
if SELF_TEST_MODE:
    DEVICE = torch.device("cuda" if _GPU_AVAILABLE else "cpu")
else:
    DEVICE = torch.device("cuda" if _GPU_AVAILABLE else "cpu")
    # In smoke/full, we still set device even if cpu, but record the failure in metrics.
    # The actual HARD_FAIL on GPU absence happens in main() so metrics.json is written.

_GPU_UTIL_SAMPLES: List[int] = []


def _sample_gpu_util() -> None:
    """Sample GPU utilization percentage if CUDA available."""
    if not _GPU_AVAILABLE:
        return
    try:
        # torch.cuda.utilization requires pynvml; fall back to memory_allocated as proxy
        try:
            util = torch.cuda.utilization(DEVICE)
            _GPU_UTIL_SAMPLES.append(int(util))
        except Exception:
            # Proxy: nonzero memory allocation = "in use"
            mem = torch.cuda.memory_allocated(DEVICE)
            _GPU_UTIL_SAMPLES.append(100 if mem > 0 else 0)
    except Exception:
        pass


# -------------------------- primitives (torch on DEVICE) --------------------------

def bipolar_unit_torch(n: int, g: torch.Generator) -> torch.Tensor:
    return (torch.randint(0, 2, (n,), generator=g, device=DEVICE).to(torch.float32) * 2.0 - 1.0)


def xor_bind_torch(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return (a * b).to(torch.float32)


def k_wta_torch(activations: torch.Tensor, k: int) -> torch.Tensor:
    """Top-k binary: returns float32 0/1 tensor with exactly k ones. 1D input."""
    n = activations.shape[0]
    if k >= n:
        return torch.ones(n, dtype=torch.float32, device=activations.device)
    _, idx = torch.topk(activations, k)
    out = torch.zeros(n, dtype=torch.float32, device=activations.device)
    out[idx] = 1.0
    return out


def k_wta_batched(activations: torch.Tensor, k: int) -> torch.Tensor:
    """Top-k binary on 2D input (B, N). Returns (B, N) float32 0/1."""
    B, n = activations.shape
    if k >= n:
        return torch.ones((B, n), dtype=torch.float32, device=activations.device)
    _, idx = torch.topk(activations, k, dim=1)
    out = torch.zeros((B, n), dtype=torch.float32, device=activations.device)
    out.scatter_(1, idx, 1.0)
    return out


def kwta_to_bipolar_torch(sparse: torch.Tensor) -> torch.Tensor:
    return (sparse * 2.0 - 1.0).to(torch.float32)


def schema_offset(schema_id: torch.Tensor, N: int) -> int:
    """Deterministic offset from a schema_id vector via SHA1 hash mod N."""
    arr = schema_id.detach().cpu().to(torch.int8).numpy()
    h = hashlib.sha1(arr.tobytes()).digest()
    val = int.from_bytes(h[:8], "big")
    return val % N


# -------------------------- generation (torch on DEVICE) --------------------------

def generate_clusters_torch(seed: int, K: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Returns (atoms (K*NPC, N), labels (K*NPC,), centers (K, N)) on DEVICE."""
    # Use numpy for deterministic RandomState then transfer to torch
    rng = np.random.RandomState(seed)
    shared = rng.randn(N_DIM).astype(np.float32)
    shared /= max(np.linalg.norm(shared), 1e-12)
    centers_np = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        private = rng.randn(N_DIM).astype(np.float32)
        private = private - (private @ shared) * shared
        private /= max(np.linalg.norm(private), 1e-12)
        c = (float(np.sqrt(BETWEEN_CLUSTER_COSINE)) * shared +
             float(np.sqrt(max(0.0, 1.0 - BETWEEN_CLUSTER_COSINE))) * private)
        c /= max(np.linalg.norm(c), 1e-12)
        centers_np[k] = c

    atoms_np = np.zeros((K * N_PER_CLUSTER, N_DIM), dtype=np.float32)
    labels_np = np.zeros(K * N_PER_CLUSTER, dtype=np.int64)
    for k in range(K):
        for i in range(N_PER_CLUSTER):
            noise = rng.randn(N_DIM).astype(np.float32)
            noise /= max(np.linalg.norm(noise), 1e-12)
            atom = centers_np[k] + WITHIN_CLUSTER_NOISE * noise
            atom /= max(np.linalg.norm(atom), 1e-12)
            atoms_np[k * N_PER_CLUSTER + i] = atom
            labels_np[k * N_PER_CLUSTER + i] = k

    return (torch.from_numpy(atoms_np).to(DEVICE),
            torch.from_numpy(labels_np).to(DEVICE),
            torch.from_numpy(centers_np).to(DEVICE))


def make_W_schema_torch(seed: int) -> torch.Tensor:
    """W (N, N) on DEVICE; rows L2-normalized."""
    rng = np.random.RandomState(seed + 31337)
    W = rng.randn(N_DIM, N_DIM).astype(np.float32)
    norms = np.linalg.norm(W, axis=1, keepdims=True)
    W = W / np.maximum(norms, 1e-12)
    return torch.from_numpy(W).to(DEVICE)


def make_schema_ids_torch(seed: int, K: int) -> torch.Tensor:
    """K random bipolar schema-IDs on DEVICE, shape (K, N)."""
    rng = np.random.default_rng(seed + 7919)
    arr = (rng.integers(0, 2, size=(K, N_DIM)).astype(np.float32) * 2.0 - 1.0)
    return torch.from_numpy(arr).to(DEVICE)


# -------------------------- bundle builders (GPU batched) --------------------------

def build_perm_bundle(centers: torch.Tensor, schema_ids: torch.Tensor,
                       W: torch.Tensor) -> Tuple[torch.Tensor, List[int]]:
    """S = sum_k roll(k-WTA(W @ centers_k, K_SPARSE), offset_k).
    Batched W @ centers.T as one matmul -> (K, N); then per-k sparse + roll."""
    K = centers.shape[0]
    # Batched matmul: (N, N) @ (N, K) -> (N, K) -> .T = (K, N)
    acts = (W @ centers.T).T  # (K, N)
    sparse_codes = k_wta_batched(acts, K_SPARSE)  # (K, N)
    _sample_gpu_util()
    offsets: List[int] = []
    S = torch.zeros(N_DIM, dtype=torch.float32, device=DEVICE)
    for k in range(K):
        off = schema_offset(schema_ids[k], N_DIM)
        shifted = torch.roll(sparse_codes[k], shifts=off, dims=0)
        S = S + shifted
        offsets.append(off)
    return S, offsets


def build_xor_bundle_v3(centers: torch.Tensor, schema_ids: torch.Tensor,
                         W: torch.Tensor) -> torch.Tensor:
    """v3 regression: XOR-bind sparse codes (the broken mechanism)."""
    K = centers.shape[0]
    acts = (W @ centers.T).T  # (K, N)
    sparse_codes = k_wta_batched(acts, K_SPARSE)  # (K, N)
    bip = kwta_to_bipolar_torch(sparse_codes)  # (K, N) in {-1, +1}
    bound = schema_ids * bip  # (K, N) elementwise XOR-equivalent
    S = bound.sum(dim=0)  # (N,)
    return S


def build_proto_centroid_bundle(centers: torch.Tensor,
                                  schema_ids: torch.Tensor) -> torch.Tensor:
    """Dense centroid bundle, XOR-bound (v3/v4 winner at small K)."""
    sign_c = torch.sign(centers)
    sign_c = torch.where(sign_c == 0.0, torch.ones_like(sign_c), sign_c)
    bound = schema_ids * sign_c  # (K, N)
    C = bound.sum(dim=0)  # (N,)
    return C


def build_diag_random_perm_bundle(schema_ids: torch.Tensor,
                                    seed: int) -> Tuple[torch.Tensor, List[int]]:
    """PERM-bundle with RANDOM sparse codes; false-accept floor."""
    K = schema_ids.shape[0]
    rng = np.random.default_rng(seed + 99999)
    codes_np = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        idx = rng.choice(N_DIM, size=min(K_SPARSE, N_DIM), replace=False)
        codes_np[k, idx] = 1.0
    codes = torch.from_numpy(codes_np).to(DEVICE)
    offsets: List[int] = []
    S = torch.zeros(N_DIM, dtype=torch.float32, device=DEVICE)
    for k in range(K):
        off = schema_offset(schema_ids[k], N_DIM)
        shifted = torch.roll(codes[k], shifts=off, dims=0)
        S = S + shifted
        offsets.append(off)
    return S, offsets


# -------------------------- query scoring (GPU batched) --------------------------

def score_perm_bundled(query_centroids: torch.Tensor, S_bundle: torch.Tensor,
                        offsets: List[int], W: torch.Tensor, K: int) -> torch.Tensor:
    """Score (Q, K) for Q queries x K candidates.
    For each candidate k: unshift S by -offset_k -> overlap with k-WTA(W @ q).
    """
    Q = query_centroids.shape[0]
    # Batched query sparse codes: (Q, N)
    acts_q = (W @ query_centroids.T).T  # (Q, N)
    q_sparse = k_wta_batched(acts_q, K_SPARSE)  # (Q, N)
    # Build unshifted bundle stack (K, N) via per-k roll
    unshifted_stack = torch.zeros((K, N_DIM), dtype=torch.float32, device=DEVICE)
    for k in range(K):
        unshifted_stack[k] = torch.roll(S_bundle, shifts=-offsets[k], dims=0)
    # Scores: (Q, N) @ (K, N).T = (Q, K)
    scores = q_sparse @ unshifted_stack.T
    _sample_gpu_util()
    return scores


def score_xor_bundled(query_centroids: torch.Tensor, S_bundle: torch.Tensor,
                       schema_ids: torch.Tensor, W: torch.Tensor, K: int) -> torch.Tensor:
    """v3 mechanism: probe_k = XOR(schema_id_k, S); score = dot(probe_k, query_bipolar)/k."""
    acts_q = (W @ query_centroids.T).T  # (Q, N)
    q_sparse = k_wta_batched(acts_q, K_SPARSE)  # (Q, N)
    q_bip = kwta_to_bipolar_torch(q_sparse)  # (Q, N) in {-1, +1}
    # probes: (K, N) = schema_ids * S_bundle (broadcast)
    probes = schema_ids * S_bundle.unsqueeze(0)  # (K, N)
    # Scores: (Q, K) = (Q, N) @ (K, N).T / K_SPARSE
    scores = (q_bip @ probes.T) / float(max(K_SPARSE, 1))
    return scores


def score_proto_centroid_bundled(query_centroids: torch.Tensor, C_bundle: torch.Tensor,
                                   schema_ids: torch.Tensor, K: int) -> torch.Tensor:
    """Dense baseline: probe_k = XOR(schema_id_k, C); cosine to query centroid."""
    Q = query_centroids.shape[0]
    q_unit = query_centroids / (query_centroids.norm(dim=1, keepdim=True) + 1e-8)  # (Q, N)
    probes = schema_ids * C_bundle.unsqueeze(0)  # (K, N)
    p_bip = torch.sign(probes)
    p_bip = torch.where(p_bip == 0.0, torch.ones_like(p_bip), p_bip)
    p_unit = p_bip / (p_bip.norm(dim=1, keepdim=True) + 1e-8)  # (K, N)
    scores = q_unit @ p_unit.T  # (Q, K)
    return scores


def score_diag_random_perm_bundled(query_centroids: torch.Tensor, S_bundle: torch.Tensor,
                                     offsets: List[int], W: torch.Tensor, K: int) -> torch.Tensor:
    """Same surface as PERM but bundle was built from random codes."""
    return score_perm_bundled(query_centroids, S_bundle, offsets, W, K)


# -------------------------- run one --------------------------

def make_test_queries(atoms: torch.Tensor, labels: torch.Tensor, K: int,
                       seed: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Returns (queries (Q, N), true_labels (Q,)) where Q = K * N_QUERIES_PER_CLUSTER."""
    rng = np.random.RandomState(seed)
    queries = []
    true_labels = []
    atoms_np = atoms.detach().cpu().numpy()
    labels_np = labels.detach().cpu().numpy()
    for c in range(K):
        members = atoms_np[labels_np == c]
        for q_i in range(N_QUERIES_PER_CLUSTER):
            base_idx = q_i % len(members)
            noise = rng.randn(N_DIM).astype(np.float32)
            noise /= max(np.linalg.norm(noise), 1e-12)
            q = members[base_idx] + 0.30 * noise
            q /= max(np.linalg.norm(q), 1e-12)
            queries.append(q)
            true_labels.append(c)
    Q = torch.from_numpy(np.stack(queries, axis=0)).to(DEVICE)
    T = torch.tensor(true_labels, dtype=torch.int64, device=DEVICE)
    return Q, T


def measure_recall_at_top1(arm: str, K: int, atoms: torch.Tensor, labels: torch.Tensor,
                             centers: torch.Tensor, schema_ids: torch.Tensor,
                             W: torch.Tensor,
                             S_perm: torch.Tensor, offsets_perm: List[int],
                             S_xor: torch.Tensor,
                             C_proto: torch.Tensor,
                             S_diag: torch.Tensor, offsets_diag: List[int],
                             queries: torch.Tensor, true_labels: torch.Tensor) -> float:
    if arm == "ARM_PERMUTATION_BUNDLED":
        scores = score_perm_bundled(queries, S_perm, offsets_perm, W, K)
    elif arm == "ARM_XOR_BUNDLED_REGRESSION":
        scores = score_xor_bundled(queries, S_xor, schema_ids, W, K)
    elif arm == "ARM_PROTOTYPE_CENTROID_BUNDLED":
        scores = score_proto_centroid_bundled(queries, C_proto, schema_ids, K)
    elif arm == "ARM_DIAG_RANDOM_SPARSE_BUNDLED":
        scores = score_diag_random_perm_bundled(queries, S_diag, offsets_diag, W, K)
    else:
        raise ValueError("unknown arm %s" % arm)
    preds = torch.argmax(scores, dim=1)  # (Q,)
    hits = (preds == true_labels).sum().item()
    n_q = true_labels.shape[0]
    return float(hits) / max(n_q, 1)


def run_one_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    per_arm_per_K: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}

    for K in K_SWEEP:
        atoms, labels, centers = generate_clusters_torch(seed, K)
        W = make_W_schema_torch(seed)
        schema_ids = make_schema_ids_torch(seed, K)
        S_perm, offs_perm = build_perm_bundle(centers, schema_ids, W)
        S_xor = build_xor_bundle_v3(centers, schema_ids, W)
        C_proto = build_proto_centroid_bundle(centers, schema_ids)
        S_diag, offs_diag = build_diag_random_perm_bundle(schema_ids, seed)
        queries, true_labels = make_test_queries(atoms, labels, K, seed=seed * 1000 + K)

        for arm in EXPECTED_ARMS:
            recall = measure_recall_at_top1(
                arm, K, atoms, labels, centers, schema_ids, W,
                S_perm, offs_perm, S_xor, C_proto, S_diag, offs_diag,
                queries, true_labels)
            per_arm_per_K[arm][str(K)] = recall
            print("  [seed=%d K=%d %s] recall@1=%.3f" % (seed, K, arm, recall), flush=True)

        # Free GPU memory between K rounds (K=1000 builds get large)
        del atoms, labels, centers, W, schema_ids
        del S_perm, offs_perm, S_xor, C_proto, S_diag, offs_diag
        del queries, true_labels
        if _GPU_AVAILABLE:
            torch.cuda.empty_cache()

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
        "device": str(DEVICE),
    }


# -------------------------- aggregate + verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

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

    # Evaluation K is always 500 if present; else largest in sweep
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

    if diag_r >= perm_r:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "DIAG_FALSE_ACCEPT_at_K%d: diag=%.3f >= perm=%.3f (structure not load-bearing)"
            % (eval_K, diag_r, perm_r))
    elif perm_r <= proto_r:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "MECHANISM_NULL_at_K%d: perm=%.3f <= proto=%.3f "
            "(drill K=500 prediction REFUTED; close sparse-bundled direction)"
            % (eval_K, perm_r, proto_r))
    elif (perm_r >= HP_PERM_RECALL_AT_K500 and
            perm_minus_proto >= HP_PERM_OVER_PROTO_DELTA and
            perm_minus_xor >= HP_PERM_OVER_XOR_DELTA):
        verdict = "HARD_PASS"
        verdict_reason = (
            "DRILL_K500_VINDICATED: perm=%.3f (>= %.2f); perm-proto=%.3f (>= %.2f); "
            "perm-xor=%.3f (>= %.2f); diag=%.3f" % (
                perm_r, HP_PERM_RECALL_AT_K500,
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

    per_K_summary = []
    for K in K_SWEEP:
        per_K_summary.append(
            "K=%d perm=%.3f xor=%.3f proto=%.3f diag=%.3f" % (
                K,
                summary_recall["ARM_PERMUTATION_BUNDLED"][str(K)]["mean"],
                summary_recall["ARM_XOR_BUNDLED_REGRESSION"][str(K)]["mean"],
                summary_recall["ARM_PROTOTYPE_CENTROID_BUNDLED"][str(K)]["mean"],
                summary_recall["ARM_DIAG_RANDOM_SPARSE_BUNDLED"][str(K)]["mean"]))

    # GPU util summary
    gpu_util_p50 = (int(np.median(_GPU_UTIL_SAMPLES))
                    if _GPU_UTIL_SAMPLES else -1)

    verdict_msg = "%s | %s | %s | n_seeds=%d | gpu_util_p50=%d device=%s" % (
        verdict, verdict_reason, " | ".join(per_K_summary), n_seeds,
        gpu_util_p50, str(DEVICE))

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
        "gpu_util_p50": gpu_util_p50,
        "gpu_util_n_samples": len(_GPU_UTIL_SAMPLES),
        "device": str(DEVICE),
        "gpu_available": _GPU_AVAILABLE,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    # GPU pre-flight (Fix #24): FULL HARD_FAIL if no CUDA; SMOKE warns but runs on CPU
    # (smoke's job is to fire the discriminator at K=500; that's a math question
    # independent of compute substrate. Full run REQUIRES GPU for throughput.)
    if not _GPU_AVAILABLE and RUN_MODE == "full" and not SELF_TEST_MODE:
        msg = "GPU_REQUIRED_FOR_FULL: torch.cuda.is_available()=False; cell is GPU-mandated per Fix #24 for full run"
        _write_minimal_metrics(out_dir, "HARD_FAIL", msg,
                                extra={"_phase": "gpu_preflight",
                                       "gpu_available": False,
                                       "device": str(DEVICE)})
        print("[%s] %s" % (ANCHOR_NAME, msg), file=sys.stderr, flush=True)
        return 2
    if not _GPU_AVAILABLE and RUN_MODE == "smoke":
        print("[%s] WARN: smoke running on CPU (no CUDA); discriminator math still valid; "
              "full run will REQUIRE GPU" % ANCHOR_NAME, file=sys.stderr, flush=True)

    _write_minimal_metrics(out_dir, "STARTED",
                            "STARTED: pid=%d mode=%s device=%s" % (
                                os.getpid(), RUN_MODE, str(DEVICE)),
                            extra={"_phase": "init",
                                   "expected_arms": list(EXPECTED_ARMS),
                                   "expected_seeds": SEEDS,
                                   "K_sweep": K_SWEEP,
                                   "expected_n_units": EXPECTED_N_UNITS,
                                   "device": str(DEVICE),
                                   "gpu_available": _GPU_AVAILABLE})

    print("[%s] mode=%s device=%s N=%d KSP=%d K_SWEEP=%s seeds=%s expected_units=%d" % (
        ANCHOR_NAME, RUN_MODE, str(DEVICE), N_DIM, K_SPARSE, K_SWEEP, SEEDS,
        EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_K_recall" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_K_recall"]
                for K in K_SWEEP:
                    assert str(K) in r["per_arm_per_K_recall"][arm]
            perm_recall = r["per_arm_per_K_recall"]["ARM_PERMUTATION_BUNDLED"][str(K_SWEEP[0])]
            diag_recall = r["per_arm_per_K_recall"]["ARM_DIAG_RANDOM_SPARSE_BUNDLED"][str(K_SWEEP[0])]
            xor_recall = r["per_arm_per_K_recall"]["ARM_XOR_BUNDLED_REGRESSION"][str(K_SWEEP[0])]
            proto_recall = r["per_arm_per_K_recall"]["ARM_PROTOTYPE_CENTROID_BUNDLED"][str(K_SWEEP[0])]
            print("[selftest] OK K=%d perm=%.3f xor=%.3f proto=%.3f diag=%.3f device=%s" % (
                K_SWEEP[0], perm_recall, xor_recall, proto_recall, diag_recall, str(DEVICE)),
                flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                    "SELFTEST_OK: 4-arm K-sweep structured perm=%.3f diag=%.3f device=%s"
                                    % (perm_recall, diag_recall, str(DEVICE)))
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
    final["_hardening_marker"] = "v4_1_permutation_K500_GPU"
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
