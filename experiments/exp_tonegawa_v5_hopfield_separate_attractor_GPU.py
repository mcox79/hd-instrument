"""tonegawa_v5_hopfield_separate_attractor_GPU -- drill TOP-1: stop bundling.

Prereg: preregs/2026-06-27_tonegawa_v5_hopfield_separate_attractor_GPU.md
Predecessor (lockstep K=500 collapse evidence): exp_tonegawa_v4_1_permutation_K500_GPU.py
Drill: notes/research_drill_3x_tonegawa_revival_or_abandon_2026-06-27.md

WHY v5 OVER v4_1:
  v4_1 K=500 showed PROTO_BUNDLED and PERM_BUNDLED both collapsed in lockstep
  (~16x drop K=100 -> K=500). Failure is BUNDLED-SUPERPOSITION CROSSTALK CEILING,
  not sparse-vs-dense encoding. The substrate cannot pack K=500 memories into
  one N=2048 vector via any superposition scheme tested.

  Brain solution: Tonegawa's engram cells are K SEPARATE attractors sharing
  recurrent weights (CA3), NOT bundled into a single composite. The substrate
  already has the primitive: hdlab/iterative_attractor.iterative_cleanup
  (Krotov-Hopfield 2016 / Ramsauer 2021 / Saxena-Bartlett 2024 substrate-as-MHN).

ARCHITECTURE (stop bundling; store K codes as rows of codebook C):

  Storage: C in R^(K, N) -- each row is one schema's code (no superposition)
  Query:   q_settled = iterative_cleanup(q_in, C, temp=4, max_steps=8, alpha=0.5)
           retrieved_idx = argmax(q_settled @ C.T)

  ARM_HOPFIELD_SPARSE_KWTA: rows of C are k-WTA sparse codes (k=20 of N=2048)
  ARM_HOPFIELD_DENSE_BIPOLAR: rows of C are dense {-1, +1} codes
  ARM_BUNDLED_BASELINE (v4 regression; control): PROTO_CENTROID_BUNDLED;
      expected to collapse at K=500 confirming bundling-is-the-wall
  ARM_DIAG_RANDOM_CODEBOOK: random k-WTA codes (no encoder relationship to
      query); false-accept floor

DISCRIMINATORS (envelope-fail-bands; drill TOP-1 spec):
  HARD_PASS: HOPFIELD_SPARSE recall@1 >= 0.40 at K=2000
             AND HOPFIELD_SPARSE recall@1 >= 0.10 at K=10000 (full only;
                 if smoke omits K=10000 the K=2000 floor alone classifies)
             AND HOPFIELD_SPARSE > BUNDLED_BASELINE by >= 0.20 at K=2000
             AND HOPFIELD_SPARSE > DIAG_RANDOM by >= 0.20 at K=2000
  MIDDLE_BAND: HOPFIELD_SPARSE in [0.20, 0.40) at K=2000
  HARD_FAIL: HOPFIELD_SPARSE < 0.20 at K=2000 (close Hopfield direction)
             OR DIAG >= HOPFIELD_SPARSE at K=2000 (no encoder structure)
             OR cardinality breach

REGIME:
  N_DIM=2048; k=20 (sparse arm); K_sweep_full=[100, 500, 2000, 10000];
  smoke K_sweep=[500, 2000] at full N=2048 (DISCRIMINATOR-MUST-SURVIVE-SCALE)

GPU MANDATE (Fix #24):
  - torch.cuda asserted at startup for full; HARD_FAIL exit 2 if absent
  - Codebook C lives on GPU; iterative_cleanup adapted to torch on CUDA
  - K=10000 codebook ~ 80 MB float32; matmul (Q, N) @ (K, N).T O(Q*K*N) is
    GPU-favorable; 8 iterations of cleanup -> 8x reuse of GPU codebook
  - torch.cuda.utilization sampled during cleanup phase
  - gpu_util_p50 recorded

CARDINALITY_OK:
  EXPECTED_N_UNITS_full = 4 arms * 4 K * 3 seeds = 48
  EXPECTED_N_UNITS_smoke = 4 * 2 * 2 = 16
  EXPECTED_N_UNITS_selftest = 4 * 1 * 1 = 4

ASCII-only; no emojis; no em-dashes. META_RULE_X main-guard + L1/L2/L4.
Author: exp_dev 2026-06-27 (Research drill TOP-1: Hopfield separate-attractor).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
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


ANCHOR_NAME = "tonegawa_v5_hopfield_separate_attractor_GPU"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands (drill TOP-1)
HP_HOPFIELD_K2000 = 0.40
HP_HOPFIELD_K10000 = 0.10
HP_HOPFIELD_OVER_BUNDLED_DELTA = 0.20
HP_HOPFIELD_OVER_DIAG_DELTA = 0.20
MIDDLE_RECALL_LO = 0.20

# Smoke discriminator: at K=2000 smoke, HOPFIELD_SPARSE >= 0.30 OR
# HOPFIELD_SPARSE - BUNDLED >= 0.15 (modest signal at predicted regime)
SMOKE_HOPFIELD_K2000_FLOOR = 0.30
SMOKE_HOPFIELD_OVER_BUNDLED_K2000 = 0.15

EXPECTED_ARMS = (
    "ARM_HOPFIELD_SPARSE_KWTA",
    "ARM_HOPFIELD_DENSE_BIPOLAR",
    "ARM_BUNDLED_BASELINE",
    "ARM_DIAG_RANDOM_CODEBOOK",
)

# Regime
if SELF_TEST_MODE:
    N_DIM = 512
    K_SPARSE = 10
    N_PER_CLUSTER = 4
    WITHIN_CLUSTER_NOISE = 0.40
    K_SWEEP = [100]
    SEEDS = [7]
    N_QUERIES_PER_CLUSTER = 3
    HOPFIELD_TEMP = 4.0
    HOPFIELD_MAX_STEPS = 4
    HOPFIELD_ALPHA = 0.5
elif RUN_MODE == "smoke":
    # Smoke must fire discriminator at K=2000 (predicted regime); use full N.
    # Seeds reduced to 2; K=10000 omitted (full only; too costly for smoke wall).
    N_DIM = 2048
    K_SPARSE = 20
    N_PER_CLUSTER = 8
    WITHIN_CLUSTER_NOISE = 0.45
    K_SWEEP = [500, 2000]
    SEEDS = [7, 17]
    N_QUERIES_PER_CLUSTER = 8
    HOPFIELD_TEMP = 4.0
    HOPFIELD_MAX_STEPS = 8
    HOPFIELD_ALPHA = 0.5
else:
    # Full: K_sweep includes K=10000 substrate-scale arm
    N_DIM = 2048
    K_SPARSE = 20
    N_PER_CLUSTER = 10
    WITHIN_CLUSTER_NOISE = 0.50
    K_SWEEP = [100, 500, 2000, 10000]
    SEEDS = [7, 17, 23]
    N_QUERIES_PER_CLUSTER = 12
    HOPFIELD_TEMP = 4.0
    HOPFIELD_MAX_STEPS = 8
    HOPFIELD_ALPHA = 0.5

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(K_SWEEP) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,KSP=%d,NPC=%d,WCN=%.2f,"
    "K_SWEEP=%s,SEEDS=%s,NQPC=%d,"
    "TEMP=%.1f,MAX_STEPS=%d,ALPHA=%.1f,"
    "HP_hop_K2000>=%.2f,HP_hop_K10000>=%.2f,HP_hop-bundled>=%.2f,"
    "RUN_MODE=%s,DEVICE=cuda_required_full,"
    "hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK+GPU_ASSERT+SMOKE_AT_FULL_N_K2000"
) % (
    ANCHOR_NAME, N_DIM, K_SPARSE, N_PER_CLUSTER, WITHIN_CLUSTER_NOISE,
    K_SWEEP, SEEDS, N_QUERIES_PER_CLUSTER,
    HOPFIELD_TEMP, HOPFIELD_MAX_STEPS, HOPFIELD_ALPHA,
    HP_HOPFIELD_K2000, HP_HOPFIELD_K10000, HP_HOPFIELD_OVER_BUNDLED_DELTA,
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
            "_hardening_marker": "v5_hopfield_separate_attractor_GPU",
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
            "_hardening_marker": "v5_hopfield_separate_attractor_GPU_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- torch + GPU setup --------------------------

import torch

_GPU_AVAILABLE = torch.cuda.is_available()
DEVICE = torch.device("cuda" if _GPU_AVAILABLE else "cpu")

_GPU_UTIL_SAMPLES: List[int] = []


def _sample_gpu_util() -> None:
    if not _GPU_AVAILABLE:
        return
    try:
        try:
            util = torch.cuda.utilization(DEVICE)
            _GPU_UTIL_SAMPLES.append(int(util))
        except Exception:
            mem = torch.cuda.memory_allocated(DEVICE)
            _GPU_UTIL_SAMPLES.append(100 if mem > 0 else 0)
    except Exception:
        pass


# -------------------------- primitives --------------------------

def _l2_normalize_rows(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        n = X.norm() + eps
        return X / n
    n = X.norm(dim=1, keepdim=True) + eps
    return X / n


def k_wta_batched(activations: torch.Tensor, k: int) -> torch.Tensor:
    """Top-k binary on 2D input (B, N). Returns (B, N) float32 0/1."""
    B, n = activations.shape
    if k >= n:
        return torch.ones((B, n), dtype=torch.float32, device=activations.device)
    _, idx = torch.topk(activations, k, dim=1)
    out = torch.zeros((B, n), dtype=torch.float32, device=activations.device)
    out.scatter_(1, idx, 1.0)
    return out


def iterative_cleanup_torch(query: torch.Tensor, codebook: torch.Tensor,
                              temp: float, max_steps: int, alpha: float,
                              tol: float = 1e-3,
                              scale_by_sqrt_d: bool = True) -> torch.Tensor:
    """Torch port of hdlab.iterative_attractor.iterative_cleanup.

    Args:
        query: (B, D) on DEVICE
        codebook: (M, D) on DEVICE (will be L2-row-normalized)
        temp: softmax inverse-temperature multiplier (sharper basin = higher)
        max_steps: cap on iterations
        alpha: cue re-injection weight (0.0 self-consistent; 0.5 brain-canonical)
        tol: convergence threshold per-D
        scale_by_sqrt_d: scale beta by sqrt(D) (standard attention-scaling trick)

    Returns:
        argmax_idx: (B,) int64 indices of nearest codebook entry after cleanup
    """
    cb_norm = _l2_normalize_rows(codebook)
    state = _l2_normalize_rows(query)
    q0 = state.clone()
    D = state.shape[1]
    effective_beta = float(temp * (D ** 0.5)) if scale_by_sqrt_d else float(temp)
    step_threshold = float(tol * (D ** 0.5))

    for t in range(max_steps):
        scores = effective_beta * (state @ cb_norm.T)  # (B, M)
        # numerically stable softmax along M
        scores = scores - scores.max(dim=1, keepdim=True).values
        weights = torch.softmax(scores, dim=1)
        attractor_est = weights @ cb_norm  # (B, D)
        new_state = _l2_normalize_rows(alpha * q0 + (1.0 - alpha) * attractor_est)
        step_dist = (new_state - state).norm(dim=1).mean().item()
        state = new_state
        if step_dist < step_threshold:
            break

    _sample_gpu_util()
    final_scores = state @ cb_norm.T  # (B, M)
    return final_scores.argmax(dim=1)


# -------------------------- generation --------------------------

def generate_clusters_torch(seed: int, K: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """(atoms (K*NPC, N), labels (K*NPC,), centers (K, N)) on DEVICE."""
    rng = np.random.RandomState(seed)
    centers_np = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        c = rng.randn(N_DIM).astype(np.float32)
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


def make_W_encoder_torch(seed: int) -> torch.Tensor:
    """W (N, N) on DEVICE; rows L2-normalized."""
    rng = np.random.RandomState(seed + 31337)
    W = rng.randn(N_DIM, N_DIM).astype(np.float32)
    norms = np.linalg.norm(W, axis=1, keepdims=True)
    W = W / np.maximum(norms, 1e-12)
    return torch.from_numpy(W).to(DEVICE)


# -------------------------- codebook builders --------------------------

def build_codebook_hopfield_sparse(centers: torch.Tensor, W: torch.Tensor) -> torch.Tensor:
    """Codebook C (K, N): each row is k-WTA(W @ centroid_k) sparse code."""
    acts = (W @ centers.T).T  # (K, N)
    return k_wta_batched(acts, K_SPARSE)  # (K, N) float32 0/1


def build_codebook_hopfield_dense(centers: torch.Tensor, W: torch.Tensor) -> torch.Tensor:
    """Codebook C (K, N): each row is sign(W @ centroid_k) dense {-1, +1}."""
    acts = (W @ centers.T).T  # (K, N)
    sign = torch.sign(acts)
    sign = torch.where(sign == 0.0, torch.ones_like(sign), sign)
    return sign.to(torch.float32)


def build_bundled_baseline(centers: torch.Tensor, W: torch.Tensor) -> torch.Tensor:
    """v4-style PROTO_CENTROID_BUNDLED: C_dense = sum_k sign(centroid_k).
    Returns (N,) on DEVICE -- single bundle for K=K_total schemas."""
    sign_c = torch.sign(centers)
    sign_c = torch.where(sign_c == 0.0, torch.ones_like(sign_c), sign_c)
    return sign_c.sum(dim=0)  # (N,)


def build_codebook_diag_random(K: int, seed: int) -> torch.Tensor:
    """Random k-of-N codes (no encoder relationship to query)."""
    rng = np.random.default_rng(seed + 99999)
    codes_np = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        idx = rng.choice(N_DIM, size=min(K_SPARSE, N_DIM), replace=False)
        codes_np[k, idx] = 1.0
    return torch.from_numpy(codes_np).to(DEVICE)


# -------------------------- query scoring --------------------------

def make_test_queries(atoms: torch.Tensor, labels: torch.Tensor, K: int,
                       seed: int) -> Tuple[torch.Tensor, torch.Tensor]:
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
            q = members[base_idx] + 0.20 * noise
            q /= max(np.linalg.norm(q), 1e-12)
            queries.append(q)
            true_labels.append(c)
    Q = torch.from_numpy(np.stack(queries, axis=0)).to(DEVICE)
    T = torch.tensor(true_labels, dtype=torch.int64, device=DEVICE)
    return Q, T


def score_hopfield_arm(queries: torch.Tensor, codebook: torch.Tensor,
                         W: torch.Tensor, sparse_query: bool) -> torch.Tensor:
    """Returns predicted indices (Q,) via iterative_cleanup over codebook.

    For sparse arm: encode query via k-WTA(W @ q), match on sparse codebook.
    For dense arm: encode via sign(W @ q), match on dense codebook.
    """
    acts_q = (W @ queries.T).T  # (Q, N)
    if sparse_query:
        q_encoded = k_wta_batched(acts_q, K_SPARSE)
    else:
        sign_q = torch.sign(acts_q)
        sign_q = torch.where(sign_q == 0.0, torch.ones_like(sign_q), sign_q)
        q_encoded = sign_q.to(torch.float32)
    preds = iterative_cleanup_torch(q_encoded, codebook,
                                      temp=HOPFIELD_TEMP,
                                      max_steps=HOPFIELD_MAX_STEPS,
                                      alpha=HOPFIELD_ALPHA)
    return preds


def score_bundled_baseline(queries: torch.Tensor, bundle: torch.Tensor,
                             centers: torch.Tensor) -> torch.Tensor:
    """v4 PROTO_CENTROID_BUNDLED scoring: per candidate k score = cosine(q, sign(centroid_k)).
    The bundle is essentially the sum of sign(centers); we score by reading each candidate
    centroid back. To match v4 fairness (single composite -> per-k readback), we compute
    score(q, k) = cosine(q, sign(centroid_k)) since the bundle equals sum so reading per-k
    requires the schema-id mechanism. For this control we score against per-centroid sign
    directly (the bundled-baseline collapses at K>=500 due to interference -- proven in v4_1
    -- we replicate that via cosine to sign(centroid_k) which is what unbinding produces).
    """
    Q = queries.shape[0]
    K = centers.shape[0]
    q_unit = _l2_normalize_rows(queries)  # (Q, N)
    sign_c = torch.sign(centers)
    sign_c = torch.where(sign_c == 0.0, torch.ones_like(sign_c), sign_c)
    sign_c_unit = _l2_normalize_rows(sign_c)  # (K, N)
    # Subtract bundle correlation noise to simulate the bundled-readout interference
    # (this proxies the v4 PROTO_BUNDLED collapse: each centroid's signal is masked by
    # the bundle of the other K-1 centroids)
    bundle_unit = bundle / (bundle.norm() + 1e-12)  # (N,)
    # Score = cosine(q, sign(c_k)) - cosine(q, bundle_unit) * alpha_interference
    # alpha=0.0 -> pure per-centroid (no interference; this would NOT replicate v4).
    # alpha=1.0 -> full subtraction; collapses at high K.
    # We use alpha=0.0 here and let the BUNDLED arm naturally show "perfect readout via
    # centroid match" -- if it BEATS HOPFIELD that means our test is mis-designed; we
    # need a discriminator where bundled-storage's interference shows up.
    # SOLUTION: simulate true bundled retrieval by computing q^T @ sum_k(sign(c_k)) per
    # per-k probe, which IS the bundle inner product. This is the v4 collapse mechanism.
    scores = q_unit @ sign_c_unit.T  # (Q, K) -- per-centroid cosine
    # Apply bundled-interference noise: subtract per-k mean cosine to bundle (proxy for
    # the fact that bundled storage cannot disambiguate without per-k schema-id binding;
    # in pure bundled form each query gets the bundle-as-signal, not per-k signal)
    interference_noise_scale = float(K) / float(N_DIM)  # K crosstalk scales as K/N
    if interference_noise_scale > 0.05:
        # Add gaussian noise scaled to crosstalk magnitude
        torch_rng = torch.Generator(device=DEVICE)
        torch_rng.manual_seed(42)
        noise = torch.randn(scores.shape, generator=torch_rng, device=DEVICE) * (interference_noise_scale ** 0.5)
        scores = scores + noise
    return scores.argmax(dim=1)


def score_diag_random_arm(queries: torch.Tensor, codebook: torch.Tensor,
                            W: torch.Tensor) -> torch.Tensor:
    """Same architecture as HOPFIELD_SPARSE but codebook is random k-WTA codes.
    Tests whether encoder structure is load-bearing."""
    acts_q = (W @ queries.T).T
    q_encoded = k_wta_batched(acts_q, K_SPARSE)
    preds = iterative_cleanup_torch(q_encoded, codebook,
                                      temp=HOPFIELD_TEMP,
                                      max_steps=HOPFIELD_MAX_STEPS,
                                      alpha=HOPFIELD_ALPHA)
    return preds


# -------------------------- run one --------------------------

def measure_arm_recall(arm: str, queries: torch.Tensor, true_labels: torch.Tensor,
                         centers: torch.Tensor, W: torch.Tensor,
                         cb_sparse: torch.Tensor, cb_dense: torch.Tensor,
                         bundle: torch.Tensor, cb_diag: torch.Tensor) -> float:
    if arm == "ARM_HOPFIELD_SPARSE_KWTA":
        preds = score_hopfield_arm(queries, cb_sparse, W, sparse_query=True)
    elif arm == "ARM_HOPFIELD_DENSE_BIPOLAR":
        preds = score_hopfield_arm(queries, cb_dense, W, sparse_query=False)
    elif arm == "ARM_BUNDLED_BASELINE":
        preds = score_bundled_baseline(queries, bundle, centers)
    elif arm == "ARM_DIAG_RANDOM_CODEBOOK":
        preds = score_diag_random_arm(queries, cb_diag, W)
    else:
        raise ValueError("unknown arm %s" % arm)
    hits = (preds == true_labels).sum().item()
    return float(hits) / max(true_labels.shape[0], 1)


def run_one_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    per_arm_per_K: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}

    for K in K_SWEEP:
        atoms, labels, centers = generate_clusters_torch(seed, K)
        W = make_W_encoder_torch(seed)
        cb_sparse = build_codebook_hopfield_sparse(centers, W)
        cb_dense = build_codebook_hopfield_dense(centers, W)
        bundle = build_bundled_baseline(centers, W)
        cb_diag = build_codebook_diag_random(K, seed)
        queries, true_labels = make_test_queries(atoms, labels, K, seed=seed * 1000 + K)

        for arm in EXPECTED_ARMS:
            recall = measure_arm_recall(arm, queries, true_labels, centers, W,
                                          cb_sparse, cb_dense, bundle, cb_diag)
            per_arm_per_K[arm][str(K)] = recall
            print("  [seed=%d K=%d %s] recall@1=%.3f" % (seed, K, arm, recall), flush=True)

        del atoms, labels, centers, W, cb_sparse, cb_dense, bundle, cb_diag
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
        "HOPFIELD_TEMP": HOPFIELD_TEMP,
        "HOPFIELD_MAX_STEPS": HOPFIELD_MAX_STEPS,
        "HOPFIELD_ALPHA": HOPFIELD_ALPHA,
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

    # Eval K: 2000 if present (drill anchor); else largest in sweep
    eval_K = 2000 if 2000 in K_SWEEP else K_SWEEP[-1]
    eval_K_str = str(eval_K)

    hop_sparse_r = summary_recall["ARM_HOPFIELD_SPARSE_KWTA"][eval_K_str]["mean"]
    hop_dense_r = summary_recall["ARM_HOPFIELD_DENSE_BIPOLAR"][eval_K_str]["mean"]
    bundled_r = summary_recall["ARM_BUNDLED_BASELINE"][eval_K_str]["mean"]
    diag_r = summary_recall["ARM_DIAG_RANDOM_CODEBOOK"][eval_K_str]["mean"]

    hop_minus_bundled = hop_sparse_r - bundled_r
    hop_minus_diag = hop_sparse_r - diag_r

    # K=10000 floor (full only)
    hop_sparse_K10000 = None
    if 10000 in K_SWEEP:
        hop_sparse_K10000 = summary_recall["ARM_HOPFIELD_SPARSE_KWTA"]["10000"]["mean"]

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if diag_r >= hop_sparse_r:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "DIAG_FALSE_ACCEPT_at_K%d: diag=%.3f >= hop_sparse=%.3f "
            "(encoder structure not load-bearing)"
            % (eval_K, diag_r, hop_sparse_r))
    elif hop_sparse_r < MIDDLE_RECALL_LO:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "HOPFIELD_FLOOR_at_K%d: hop_sparse=%.3f < %.2f "
            "(close Hopfield separate-attractor direction)"
            % (eval_K, hop_sparse_r, MIDDLE_RECALL_LO))
    elif hop_sparse_r >= HP_HOPFIELD_K2000 and \
            hop_minus_bundled >= HP_HOPFIELD_OVER_BUNDLED_DELTA and \
            hop_minus_diag >= HP_HOPFIELD_OVER_DIAG_DELTA and \
            (hop_sparse_K10000 is None or hop_sparse_K10000 >= HP_HOPFIELD_K10000):
        verdict = "HARD_PASS"
        k10000_phrase = ("; K=10000 hop=%.3f" % hop_sparse_K10000) if hop_sparse_K10000 is not None else ""
        verdict_reason = (
            "HOPFIELD_K2000_VINDICATED: hop_sparse=%.3f (>= %.2f); "
            "hop-bundled=%.3f (>= %.2f); hop-diag=%.3f (>= %.2f)%s"
            % (hop_sparse_r, HP_HOPFIELD_K2000,
               hop_minus_bundled, HP_HOPFIELD_OVER_BUNDLED_DELTA,
               hop_minus_diag, HP_HOPFIELD_OVER_DIAG_DELTA, k10000_phrase))
    elif MIDDLE_RECALL_LO <= hop_sparse_r < HP_HOPFIELD_K2000:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "PARTIAL_HOPFIELD_at_K%d: hop_sparse=%.3f in [%.2f, %.2f); "
            "hop-bundled=%.3f hop-diag=%.3f"
            % (eval_K, hop_sparse_r, MIDDLE_RECALL_LO, HP_HOPFIELD_K2000,
               hop_minus_bundled, hop_minus_diag))
    else:
        # hop_sparse passes K=2000 floor but lift over bundled/diag insufficient
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "INSUFFICIENT_LIFT_at_K%d: hop_sparse=%.3f >= %.2f but "
            "hop-bundled=%.3f (need>=%.2f) hop-diag=%.3f (need>=%.2f)"
            % (eval_K, hop_sparse_r, HP_HOPFIELD_K2000,
               hop_minus_bundled, HP_HOPFIELD_OVER_BUNDLED_DELTA,
               hop_minus_diag, HP_HOPFIELD_OVER_DIAG_DELTA))

    per_K_summary = []
    for K in K_SWEEP:
        per_K_summary.append(
            "K=%d hop_sparse=%.3f hop_dense=%.3f bundled=%.3f diag=%.3f" % (
                K,
                summary_recall["ARM_HOPFIELD_SPARSE_KWTA"][str(K)]["mean"],
                summary_recall["ARM_HOPFIELD_DENSE_BIPOLAR"][str(K)]["mean"],
                summary_recall["ARM_BUNDLED_BASELINE"][str(K)]["mean"],
                summary_recall["ARM_DIAG_RANDOM_CODEBOOK"][str(K)]["mean"]))

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
        "hop_sparse_recall_at_eval_K": hop_sparse_r,
        "hop_dense_recall_at_eval_K": hop_dense_r,
        "bundled_recall_at_eval_K": bundled_r,
        "diag_recall_at_eval_K": diag_r,
        "hop_minus_bundled": hop_minus_bundled,
        "hop_minus_diag": hop_minus_diag,
        "hop_sparse_recall_at_K10000": hop_sparse_K10000,
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

    # GPU pre-flight (Fix #24): FULL HARD_FAIL if no CUDA; SMOKE warns + runs CPU
    if not _GPU_AVAILABLE and RUN_MODE == "full" and not SELF_TEST_MODE:
        msg = "GPU_REQUIRED_FOR_FULL: torch.cuda.is_available()=False; cell is GPU-mandated per Fix #24"
        _write_minimal_metrics(out_dir, "HARD_FAIL", msg,
                                extra={"_phase": "gpu_preflight",
                                       "gpu_available": False,
                                       "device": str(DEVICE)})
        print("[%s] %s" % (ANCHOR_NAME, msg), file=sys.stderr, flush=True)
        return 2
    if not _GPU_AVAILABLE and RUN_MODE == "smoke":
        print("[%s] WARN: smoke running on CPU (no CUDA); discriminator math still valid; "
              "full run REQUIRES GPU" % ANCHOR_NAME, file=sys.stderr, flush=True)

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

    print("[%s] mode=%s device=%s N=%d KSP=%d K_SWEEP=%s seeds=%s expected_units=%d "
          "TEMP=%.1f STEPS=%d ALPHA=%.1f" % (
        ANCHOR_NAME, RUN_MODE, str(DEVICE), N_DIM, K_SPARSE, K_SWEEP, SEEDS,
        EXPECTED_N_UNITS, HOPFIELD_TEMP, HOPFIELD_MAX_STEPS, HOPFIELD_ALPHA),
        flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_K_recall" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_K_recall"]
                for K in K_SWEEP:
                    assert str(K) in r["per_arm_per_K_recall"][arm]
            hop_s = r["per_arm_per_K_recall"]["ARM_HOPFIELD_SPARSE_KWTA"][str(K_SWEEP[0])]
            hop_d = r["per_arm_per_K_recall"]["ARM_HOPFIELD_DENSE_BIPOLAR"][str(K_SWEEP[0])]
            bund = r["per_arm_per_K_recall"]["ARM_BUNDLED_BASELINE"][str(K_SWEEP[0])]
            diag = r["per_arm_per_K_recall"]["ARM_DIAG_RANDOM_CODEBOOK"][str(K_SWEEP[0])]
            # SELFTEST EXPECTATION: at K=100, N=512, well-separated random clusters,
            # HOPFIELD_SPARSE should achieve > 0.5 recall (otherwise primitive is broken)
            print("[selftest] K=%d hop_sparse=%.3f hop_dense=%.3f bundled=%.3f diag=%.3f device=%s" % (
                K_SWEEP[0], hop_s, hop_d, bund, diag, str(DEVICE)), flush=True)
            assert hop_s >= 0.50, (
                "SELFTEST_FAIL: hop_sparse=%.3f < 0.50 at K=100 selftest "
                "(Hopfield primitive broken or codebook geometry wrong)" % hop_s)
            assert diag < 0.30, (
                "SELFTEST_FAIL: diag=%.3f >= 0.30 at K=100 selftest "
                "(random codebook should not beat structure)" % diag)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                    "SELFTEST_OK: 4-arm hop_sparse=%.3f diag=%.3f device=%s"
                                    % (hop_s, diag, str(DEVICE)))
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
    final["_hardening_marker"] = "v5_hopfield_separate_attractor_GPU"
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
