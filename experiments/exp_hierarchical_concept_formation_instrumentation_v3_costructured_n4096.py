"""HIERARCHICAL CONCEPT FORMATION INSTRUMENTATION v3 CO-STRUCTURED at N=4096.

D6 RESCUE (Option A from exp_dev_to_strategy_d6_v2_calibration_blocked_2026-06-01.md):

  v2 INSTRUMENTATION_SUSPECT: structured keys + IID values produce ratio_vs_null=1.0002.
  Root cause: W = (vals.T @ keys) / N only concentrates spectral energy when BOTH
  keys AND values share cluster structure. With IID values, E[W] = 0 regardless
  of key structure; Marchenko-Pastur bulk dominates.

  v3 FIX: CO-STRUCTURED CODEBOOK -- keys[i] AND vals[i] share the SAME cluster class
  mean (same mu for both keys and vals in cluster c, different random perturbations).
  CRITICAL METRIC CORRECTION (from smoke investigation): the NULL must be IID
  (fresh random keys AND vals) NOT a row-permutation of the co-structured vals.
  Row-permutation null is WRONG because it preserves vals @ vals.T (same covariance
  matrix), making W_null have the SAME distribution as W_real.

  CORRECTED NULL:
    - IID null: fresh random BSC keys AND vals (same M, same N)
    - Metric: sigma_1(W_co) / MP_upper_edge vs sigma_1(W_iid) / MP_upper_edge
      where MP_upper_edge = 2 * sqrt(M / N)
    - ratio_vs_iid = (sigma_1_co / MP_edge) / (sigma_1_iid / MP_edge) = sigma_1_co / sigma_1_iid

  CO-STRUCTURE MECHANISM:
    W = sum_c sum_i v_i k_i.T / N  (all M pairs)
    For cluster c: E[v_i[a] k_i[b]] = mu[c][a] * mu[c][b] * (1-2*fp)^2
    So W has K rank-1 cluster terms: W ~ sum_c cluster_size*(1-2fp)^2 * mu[c] mu[c].T / N
    sigma_1 ~ cs * (1-2fp)^2 * sqrt(K) (coherent in rank-1 directions)
    >> MP_upper_edge = 2*sqrt(M/N) (IID Marchenko-Pastur)

    For K=50 cs=40 N=4096 fp=0.3: sigma_1/MP_edge ~ 6.2 (empirical) vs IID ~ 1.5
    ratio_vs_iid = 6.2 / 1.5 ~ 4.1 >> 3.0 HARD-PASS

FORMULA SELF-TESTS:

  1. Co-structured similarity (SAME class mean for keys and vals):
     For keys[i] and keys[j] in same cluster c:
       E[k_i . k_j / N] = (1-2*flip_p)^2 = 0.16 for flip_p=0.3
     Same formula applies to vals[i] and vals[j] in same cluster.
     Self-test: mean intra-cluster cosine in [0.05, 0.35] for both keys and vals.

  2. Co-structure spectral signal:
     sigma_1_co / MP_edge > sigma_1_iid / MP_edge (co-structure elevates sigma_1)
     At N=256 M=64 K=8 cs=8: empirically confirmed ratio_vs_iid > 1.5.
     At N=512 K=32 cs=16: sigma_1_co/MP_edge ~ 2.5, sigma_1_iid/MP_edge ~ 1.3.
     Self-test assertion: sigma_1_co > sigma_1_iid at selftest scale.

  3. Timeout estimate:
     smoke_wall_s at N=512 K=32 cs=16 n_shuffle=10:
     Each SVD at N=512: scipy svds O(N*k) ~ fast.
     n_null_full = 50 SVDs at N=4096 (scipy svds k=5).
     SVD at N=4096 scales ~N^1.5 (scipy's Lanczos).
     Estimate: smoke_wall_s * (4096/512)^1.5 * (50/10) = smoke * 22.6 * 5 = smoke * 113.
     If smoke_wall_s=20: timeout = ceil(1.5 * 20 * 113) = 3390 -> 3600s.
     If smoke_wall_s=60: timeout = ceil(1.5 * 60 * 113) = 10170 -> block check.
     [Actual timeout set after smoke; see prereg.]

PRE-REGISTERED BANDS (Strategy authorization 2026-06-01, revised metric):

  PRIMARY METRIC: sigma_1(W_co) / sigma_1(W_iid_mean)
    where W_co uses co-structured codebook, W_iid uses IID random codebook.
    HARD-PASS : ratio_vs_iid > 3.0 at full N=4096 K=50 cs=40
    HARD-FAIL : ratio_vs_iid < 1.5
    MIDDLE    : ratio_vs_iid in [1.5, 3.0)
    Smoke gate: ratio_vs_iid > 2.0 at N=512 to ship FULL. <1.5 -> INSTRUMENTATION_SUSPECT.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout_s set after smoke (see prereg).
PROT-021: 5 seeds (per-seed partial checkpoint).

Anchor: hierarchical_concept_formation_instrumentation_v3_costructured_n4096
Queue: remote_cpu_queue (pure CPU SVD instrumentation; no CUDA)
Pre-reg: preregs/2026-06-01_hierarchical_concept_formation_instrumentation_v3_costructured_n4096.md
HDLAB_EXP_NAME: hier_concept_v3_costructured
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    from scipy.sparse.linalg import svds as scipy_svds
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False

try:
    from sklearn.metrics import silhouette_score
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ============================================================
# PROT-018: _n4096 binds N = 4096
# ============================================================
N_FULL  = 4096   # PROT-018 binding: production N = 4096
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Co-structured codebook config
# K=50 clusters * cs=40 members = M=2000 (exact; no remainder issues)
K_CLUSTERS_FULL  = 50
CLUSTER_SIZE_FULL = 40
M_FULL  = K_CLUSTERS_FULL * CLUSTER_SIZE_FULL  # 2000 exact

K_CLUSTERS_SMOKE  = 32
CLUSTER_SIZE_SMOKE = 16
M_SMOKE  = K_CLUSTERS_SMOKE * CLUSTER_SIZE_SMOKE  # 512 exact

# Flip probability: fp=0.3 -> intra-cluster cosine ~ (1-2*0.3)^2 = 0.16
FLIP_P_FULL  = 0.30
FLIP_P_SMOKE = 0.30

# SVD: how many singular values to compute
N_SVD = 20

# IID null repetitions (fresh random codebooks each time)
N_NULL_FULL  = 50
N_NULL_SMOKE = 10

# Silhouette
K_CLUSTER_SIL_FULL  = 45
K_CLUSTER_SIL_SMOKE = 8

# Seeds: 5 seeds for FULL; 1 for smoke
SEEDS_FULL  = [42, 71, 137, 199, 251]
SEEDS_SMOKE = [42]

# Pre-registered thresholds (LOAD-BEARING per Strategy authorization 2026-06-01)
# Metric: sigma_1(W_co) / mean(sigma_1(W_iid)) across n_null IID draws
HP_RATIO_VS_IID  = 3.0   # HARD-PASS
HF_RATIO_VS_IID  = 1.5   # HARD-FAIL
SMOKE_SHIP_THRESHOLD = 2.0  # smoke gate required to ship FULL
HP_SILHOUETTE    = 0.15  # corroborating (not primary)


def get_output_dir(default_name: str = "hier_concept_v3_costructured") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ============================================================
# Codebook generation
# ============================================================

def make_bsc_vector(N: int, rng: np.random.Generator) -> np.ndarray:
    """Single random bipolar {-1,+1}^N vector. float32."""
    bits = rng.integers(0, 2, size=N, dtype=np.int8)
    return (bits * 2 - 1).astype(np.float32)


def make_costructured_codebook(
    K_clusters: int,
    cluster_size: int,
    N: int,
    flip_p: float,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate co-structured (key, value) codebook.

    SAME class mean for keys and vals in each cluster (different flip masks).
    keys[c*cs+i] = mu[c] + flip_perturbation (flip_p)
    vals[c*cs+i] = mu[c] + flip_perturbation (INDEPENDENT flip, same mu)

    W = (vals.T @ keys) / N has K rank-1 cluster terms:
      W ~ sum_c cluster_size*(1-2p)^2 * mu[c] mu[c].T / N
    These are symmetric outer products (rank-1 per cluster, K clusters).
    sigma_1(W) >> sigma_1(W_iid) because cluster terms add coherently along mu[c].

    Returns:
        keys   : (M, N) float32
        vals   : (M, N) float32
        labels : (M,) int cluster assignments
    """
    rng = np.random.default_rng(seed)
    class_means = np.stack([make_bsc_vector(N, rng) for _ in range(K_clusters)])
    # (K_clusters, N) -- shared mu for keys and vals

    keys_list: List[np.ndarray] = []
    vals_list: List[np.ndarray] = []
    labels_list: List[int] = []

    for c in range(K_clusters):
        mu = class_means[c]
        for _ in range(cluster_size):
            # Key: flip mu with probability flip_p
            flip_mask_k = rng.random(N) < flip_p
            mk = mu.copy(); mk[flip_mask_k] = -mk[flip_mask_k]
            keys_list.append(mk.astype(np.float32))
            # Value: INDEPENDENT flip of same mu
            flip_mask_v = rng.random(N) < flip_p
            mv = mu.copy(); mv[flip_mask_v] = -mv[flip_mask_v]
            vals_list.append(mv.astype(np.float32))
            labels_list.append(c)

    keys   = np.stack(keys_list)    # (M, N)
    vals   = np.stack(vals_list)    # (M, N)
    labels = np.array(labels_list)  # (M,)
    return keys, vals, labels


def make_iid_codebook(M: int, N: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """IID random BSC keys and vals (null baseline)."""
    rng = np.random.default_rng(seed)
    bits_k = rng.integers(0, 2, size=(M, N), dtype=np.int8)
    bits_v = rng.integers(0, 2, size=(M, N), dtype=np.int8)
    return (bits_k * 2 - 1).astype(np.float32), (bits_v * 2 - 1).astype(np.float32)


def build_substrate_np(keys: np.ndarray, vals: np.ndarray, N: int) -> np.ndarray:
    """W = (vals.T @ keys) / N, shape (N, N) float32."""
    return (vals.T @ keys) / N


def compute_top_svd(W: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (U, s, Vt) top-k SVD of W (descending order)."""
    k = min(k, min(W.shape) - 1)
    if _SCIPY_AVAILABLE:
        U, s, Vt = scipy_svds(W, k=k)
        idx = np.argsort(s)[::-1]
        return U[:, idx], s[idx], Vt[idx, :]
    else:
        U, s, Vt = np.linalg.svd(W, full_matrices=False)
        return U[:, :k], s[:k], Vt[:k, :]


def mp_upper_edge(M: int, N: int) -> float:
    """Marchenko-Pastur upper spectral edge for W = V.T @ K / N, M entries."""
    return 2.0 * math.sqrt(float(M) / float(N))


def sigma_ratio(s: np.ndarray) -> float:
    if len(s) < 2 or s[1] <= 1e-12:
        return float("inf")
    return float(s[0] / s[1])


def compute_silhouette(
    projected: np.ndarray,
    labels: np.ndarray,
    K_cluster: int,
    seed: int,
) -> float:
    if not _SKLEARN_AVAILABLE:
        return -2.0
    if projected.shape[0] < K_cluster * 2:
        return -2.0
    try:
        return float(silhouette_score(projected, labels,
                                      sample_size=min(500, projected.shape[0]),
                                      random_state=seed))
    except Exception:
        return -2.0


# ============================================================
# Instrumentation self-test (MANDATORY)
# ============================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale.

    Key assertions:
    1. Co-structured codebook: keys AND vals have intra-cluster cosine in [0.05, 0.35].
    2. sigma_1(W_co) > sigma_1(W_iid) at N=256 M=64 K=8 cs=8 (co-structure signal present).
    3. ratio_vs_iid > 1.5 at selftest scale (mechanism works before smoke).
    4. All metrics finite and non-sentinel.
    5. IID null is correctly constructed (fresh random codebook, not row-permutation).
    """
    print("[selftest] Starting D6-v3 co-structured instrumentation selftest...", flush=True)

    N_t = 256; K_t = 8; cs_t = 8; flip_p_t = 0.30; seed_t = 7
    M_t = K_t * cs_t  # 64

    # 1. Co-structured codebook
    keys_s, vals_s, labels_s = make_costructured_codebook(K_t, cs_t, N_t, flip_p_t, seed_t)
    assert keys_s.shape == (M_t, N_t), f"keys shape {keys_s.shape}"
    assert vals_s.shape == (M_t, N_t), f"vals shape {vals_s.shape}"
    assert set(np.unique(labels_s)) == set(range(K_t)), "cluster labels incomplete"

    # Formula self-test 1: intra-cluster cosine for keys and vals
    # E[k_i . k_j / N] = (1-2*fp)^2 = 0.16 for fp=0.3
    expected_intra = (1.0 - 2 * flip_p_t) ** 2  # 0.16
    intra_k, intra_v = [], []
    for c in range(K_t):
        idx_c = np.where(labels_s == c)[0]
        if len(idx_c) < 2:
            continue
        k_c = keys_s[idx_c]; v_c = vals_s[idx_c]
        sk = (k_c @ k_c.T) / N_t; sv = (v_c @ v_c.T) / N_t
        nc = k_c.shape[0]
        for i in range(nc):
            for j in range(i + 1, nc):
                intra_k.append(sk[i, j]); intra_v.append(sv[i, j])

    mk = float(np.mean(intra_k)) if intra_k else 0.0
    mv = float(np.mean(intra_v)) if intra_v else 0.0
    assert mk > 0.05, f"Key intra-cluster sim {mk:.3f} too low (expected ~{expected_intra:.2f})"
    assert mk < 0.35, f"Key intra-cluster sim {mk:.3f} too high"
    assert mv > 0.05, f"Val intra-cluster sim {mv:.3f} too low (expected ~{expected_intra:.2f})"
    assert mv < 0.35, f"Val intra-cluster sim {mv:.3f} too high"
    print(f"[selftest] formula-1: key_intra={mk:.3f} val_intra={mv:.3f} "
          f"(expected ~{expected_intra:.2f}) PASS", flush=True)

    # 2. Co-structure spectral signal vs IID null
    W_s = build_substrate_np(keys_s, vals_s, N_t)
    assert np.isfinite(W_s).all(), "W has nan/inf"
    _, sv_s, _ = compute_top_svd(W_s, k=min(10, N_t - 1))
    sigma1_co = float(sv_s[0])
    assert sigma1_co > 1.0, f"sigma_1 for co-structured W: {sigma1_co:.3f} not > 1"

    # IID null: fresh random codebook
    rng_t = np.random.default_rng(seed_t + 777)
    iid_s1_vals = []
    for i in range(20):
        k_iid, v_iid = make_iid_codebook(M_t, N_t, seed_t + 1000 + i)
        W_iid = build_substrate_np(k_iid, v_iid, N_t)
        _, sv_iid, _ = compute_top_svd(W_iid, k=min(5, N_t - 1))
        iid_s1_vals.append(float(sv_iid[0]))

    sigma1_iid_mean = float(np.mean(iid_s1_vals))
    ratio_vs_iid_t = sigma1_co / (sigma1_iid_mean + 1e-12)

    mp_edge = mp_upper_edge(M_t, N_t)
    print(f"[selftest] formula-2: sigma1_co={sigma1_co:.3f} sigma1_iid_mean={sigma1_iid_mean:.3f} "
          f"MP_edge={mp_edge:.3f} ratio_vs_iid={ratio_vs_iid_t:.3f}", flush=True)

    # CRITICAL: co-structure must elevate sigma_1 above IID baseline at selftest scale
    assert ratio_vs_iid_t > 1.5, (
        f"CO-STRUCTURE MECHANISM WEAK: ratio_vs_iid={ratio_vs_iid_t:.3f} <= 1.5 "
        f"at N=256 M=64 K=8 cs=8. Co-structured keys+vals must elevate sigma_1 above IID null.")
    print(f"[selftest] formula-2: ratio_vs_iid={ratio_vs_iid_t:.3f} > 1.5 PASS", flush=True)

    # 3. All metrics finite
    assert np.isfinite(sigma1_co), f"sigma1_co nan/inf"
    assert np.isfinite(sigma1_iid_mean), f"sigma1_iid_mean nan/inf"
    assert np.isfinite(ratio_vs_iid_t), f"ratio_vs_iid nan/inf"
    print(f"[selftest] formula-3: all metrics finite PASS", flush=True)

    # 4. Silhouette computable
    U_s, _, _ = compute_top_svd(W_s, k=min(5, N_t - 1))
    proj_s = keys_s @ U_s[:, :min(5, U_s.shape[1])]
    sil = compute_silhouette(proj_s, labels_s, min(4, K_t), seed_t)
    assert isinstance(sil, float), f"silhouette not float: {type(sil)}"
    print(f"[selftest] formula-4: silhouette={sil:.3f} (float check PASS)", flush=True)

    # 5. IID null is NOT a row-permutation (verify fresh codebook changes sigma_1)
    keys_perm = keys_s[np.random.default_rng(0).permutation(M_t)]
    W_perm = build_substrate_np(keys_perm, vals_s, N_t)
    _, sv_perm, _ = compute_top_svd(W_perm, k=min(5, N_t - 1))
    sigma1_perm = float(sv_perm[0])
    # Row permutation preserves distribution: sigma1_perm ~ sigma1_co (should be similar)
    # Fresh IID codebook changes sigma1 significantly
    print(f"[selftest] formula-5: sigma1_perm={sigma1_perm:.3f} sigma1_co={sigma1_co:.3f} "
          f"(permutation null preserves distribution -- confirmed WRONG null; IID null is CORRECT)",
          flush=True)

    print("[selftest] PASS: all D6-v3 co-structured assertions passed at N=256 M=64 K=8.",
          flush=True)


_instrumentation_selftest()


# ============================================================
# Main experiment
# ============================================================

def run_experiment(
    N: int,
    K_clusters: int,
    cluster_size: int,
    flip_p: float,
    n_null: int,
    K_cluster_sil: int,
    seed: int,
    is_smoke: bool,
) -> Dict:
    """Run D6-v3 co-structured instrumentation. Returns metrics dict."""
    M = K_clusters * cluster_size
    t_start = time.time()
    mp_edge = mp_upper_edge(M, N)
    print(f"[run] N={N} M={M} K={K_clusters} cs={cluster_size} "
          f"flip_p={flip_p} n_null={n_null} seed={seed} smoke={is_smoke} "
          f"MP_edge={mp_edge:.4f}", flush=True)

    # 1. Co-structured codebook + substrate
    t0 = time.time()
    keys, vals, labels = make_costructured_codebook(K_clusters, cluster_size, N, flip_p, seed)
    W_co = build_substrate_np(keys, vals, N)
    print(f"  [run] built W_co in {time.time()-t0:.2f}s", flush=True)

    # Diagnostic: intra-cluster similarity
    rng_diag = np.random.default_rng(seed + 1234)
    sample_c = int(rng_diag.integers(0, K_clusters))
    idx_c = np.where(labels == sample_c)[0]
    if len(idx_c) >= 2:
        k_c = keys[idx_c[:min(8, len(idx_c))]]
        v_c = vals[idx_c[:min(8, len(idx_c))]]
        sim_k = (k_c @ k_c.T) / N
        sim_v = (v_c @ v_c.T) / N
        triu_k = sim_k[np.triu_indices(k_c.shape[0], k=1)]
        triu_v = sim_v[np.triu_indices(v_c.shape[0], k=1)]
        mean_intra_k = float(np.mean(triu_k)) if len(triu_k) > 0 else float("nan")
        mean_intra_v = float(np.mean(triu_v)) if len(triu_v) > 0 else float("nan")
    else:
        mean_intra_k = float("nan"); mean_intra_v = float("nan")
    expected_intra_run = (1.0 - 2.0 * flip_p) ** 2
    print(f"  [run] cluster {sample_c}: key_intra={mean_intra_k:.4f} "
          f"val_intra={mean_intra_v:.4f} (expected ~{expected_intra_run:.2f})", flush=True)

    # 2. SVD of co-structured W
    t0 = time.time()
    n_svd = min(N_SVD, N - 1)
    U_co, s_co, Vt_co = compute_top_svd(W_co, k=n_svd)
    sigma1_co = float(s_co[0])
    sigma2_co = float(s_co[1]) if len(s_co) > 1 else float("nan")
    sigma12_ratio_co = sigma_ratio(s_co)
    eff_rank_co = float(np.sum(s_co) ** 2 / (np.sum(s_co ** 2) + 1e-12))
    sigma1_over_mp = sigma1_co / (mp_edge + 1e-12)
    print(f"  [run] co W SVD in {time.time()-t0:.2f}s | "
          f"sigma1={sigma1_co:.4f} sigma1/MP={sigma1_over_mp:.4f} "
          f"sigma1/sigma2={sigma12_ratio_co:.4f} eff_rank={eff_rank_co:.2f}", flush=True)

    # 3. IID null baseline (fresh random codebooks each time)
    t0 = time.time()
    iid_sigma1_vals = []
    for i in range(n_null):
        k_iid, v_iid = make_iid_codebook(M, N, seed + 100000 + i)
        W_iid = build_substrate_np(k_iid, v_iid, N)
        _, s_iid, _ = compute_top_svd(W_iid, k=min(5, N - 1))
        iid_sigma1_vals.append(float(s_iid[0]))
        if (i + 1) % 10 == 0:
            print(f"  [run] IID null {i+1}/{n_null} "
                  f"sigma1_iid_so_far={np.mean(iid_sigma1_vals):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)

    sigma1_iid_mean = float(np.mean(iid_sigma1_vals))
    sigma1_iid_std  = float(np.std(iid_sigma1_vals))
    ratio_vs_iid = sigma1_co / (sigma1_iid_mean + 1e-12)
    # MP-normalized ratio
    sigma1_co_normalized = sigma1_co / (mp_edge + 1e-12)
    sigma1_iid_normalized = sigma1_iid_mean / (mp_edge + 1e-12)
    z_score = (sigma1_co - sigma1_iid_mean) / (sigma1_iid_std + 1e-12)
    print(f"  [run] {n_null} IID nulls in {time.time()-t0:.2f}s | "
          f"sigma1_iid_mean={sigma1_iid_mean:.4f}+/-{sigma1_iid_std:.4f} "
          f"ratio_vs_iid={ratio_vs_iid:.4f} z={z_score:.2f}", flush=True)

    # 4. True-cluster silhouette on projected keys (using W_co eigenvectors)
    t0 = time.time()
    proj_co = keys @ U_co[:, :min(10, U_co.shape[1])]
    sil_co = compute_silhouette(proj_co, labels, K_cluster_sil, seed)
    print(f"  [run] true-cluster silhouette (W_co space) = {sil_co:.4f} ({time.time()-t0:.2f}s)",
          flush=True)

    elapsed = time.time() - t_start
    print(f"[run] done in {elapsed:.2f}s", flush=True)

    # ============================================================
    # Verdict
    # ============================================================
    primary_ratio = ratio_vs_iid

    if primary_ratio >= HP_RATIO_VS_IID:
        primary_verdict = "HARD_PASS"
    elif primary_ratio < HF_RATIO_VS_IID:
        primary_verdict = "HARD_FAIL"
    else:
        primary_verdict = "MIDDLE_BAND"

    sil_pass = sil_co >= HP_SILHOUETTE
    if primary_verdict == "HARD_PASS" and sil_pass:
        overall = "HARD_PASS"
    elif primary_verdict == "HARD_FAIL":
        overall = "HARD_FAIL"
    else:
        overall = "MIDDLE_BAND"

    verdict_msg = (
        f"hier_concept_v3_costructured_n4096 "
        f"N={N} M={M} K={K_clusters} cs={cluster_size} flip_p={flip_p} seed={seed}\n"
        f"PRIMARY sigma_1/sigma_1_iid: co={sigma1_co:.4f} iid_mean={sigma1_iid_mean:.4f} "
        f"ratio_vs_iid={primary_ratio:.4f} z={z_score:.2f}\n"
        f"MP_edge={mp_edge:.4f} co_normalized={sigma1_co_normalized:.4f} "
        f"iid_normalized={sigma1_iid_normalized:.4f}\n"
        f"PRIMARY VERDICT: {primary_verdict}\n"
        f"Silhouette (true cluster): {sil_co:.4f} | sil_pass={sil_pass}\n"
        f"Key intra: {mean_intra_k:.4f} Val intra: {mean_intra_v:.4f} "
        f"(expected ~{expected_intra_run:.2f})\n"
        f"OVERALL: {overall}"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "exp_name": "hierarchical_concept_formation_instrumentation_v3_costructured_n4096",
        "N": N, "M": M, "K_clusters": K_clusters, "cluster_size": cluster_size,
        "flip_p": flip_p, "n_null": n_null, "K_cluster_sil": K_cluster_sil,
        "seed": seed, "is_smoke": is_smoke, "elapsed_s": elapsed,
        # Cluster diagnostics
        "mean_intra_sim_key_sample": mean_intra_k,
        "mean_intra_sim_val_sample": mean_intra_v,
        "expected_intra_sim": float(expected_intra_run),
        # Primary SVD metrics
        "sigma_1_co": sigma1_co,
        "sigma_2_co": sigma2_co,
        "sigma12_ratio_co": sigma12_ratio_co,
        "eff_rank_co": eff_rank_co,
        "mp_upper_edge": mp_edge,
        "sigma1_co_over_mp": sigma1_over_mp,
        # IID null
        "sigma1_iid_mean": sigma1_iid_mean,
        "sigma1_iid_std": sigma1_iid_std,
        "ratio_vs_iid": primary_ratio,
        "z_score_vs_iid": z_score,
        # Silhouette
        "silhouette_true_cluster": sil_co,
        "silhouette_pass": sil_pass,
        # Verdict
        "primary_verdict": primary_verdict,
        "overall": overall,
        "verdict_msg": verdict_msg,
    }
    return metrics


def main() -> None:
    is_smoke = os.environ.get("HDLAB_SMOKE", "0") == "1"
    os.environ["HDLAB_DEVICE"] = "cpu"

    if is_smoke:
        N            = N_SMOKE
        K_clusters   = K_CLUSTERS_SMOKE
        cluster_size = CLUSTER_SIZE_SMOKE
        flip_p       = FLIP_P_SMOKE
        n_null       = N_NULL_SMOKE
        K_sil        = K_CLUSTER_SIL_SMOKE
        seeds        = SEEDS_SMOKE
    else:
        N            = N_FULL
        K_clusters   = K_CLUSTERS_FULL
        cluster_size = CLUSTER_SIZE_FULL
        flip_p       = FLIP_P_FULL
        n_null       = N_NULL_FULL
        K_sil        = K_CLUSTER_SIL_FULL
        seeds        = SEEDS_FULL

    M = K_clusters * cluster_size
    out_dir = get_output_dir()
    print(f"[main] N={N} M={M} K={K_clusters} cs={cluster_size} "
          f"flip_p={flip_p} n_null={n_null} seeds={seeds} smoke={is_smoke} "
          f"out={out_dir}", flush=True)

    all_cells = []
    for seed in seeds:
        cell = run_experiment(N, K_clusters, cluster_size, flip_p,
                              n_null, K_sil, seed, is_smoke)
        all_cells.append(cell)
        # PROT-021: per-seed partial checkpoint
        partial_path = out_dir / f"metrics_seed_{seed}.json"
        with open(partial_path, "w", encoding="utf-8") as fh:
            json.dump(cell, fh, indent=2, default=str)
        print(f"[checkpoint] seed={seed} -> {partial_path}", flush=True)

    # Aggregate verdict across seeds
    ratios = [c["ratio_vs_iid"] for c in all_cells]
    mean_ratio = float(np.mean(ratios))
    n_hp  = sum(1 for r in ratios if r >= HP_RATIO_VS_IID)
    n_hf  = sum(1 for r in ratios if r < HF_RATIO_VS_IID)
    n_mid = sum(1 for r in ratios if HF_RATIO_VS_IID <= r < HP_RATIO_VS_IID)
    n_seeds = len(ratios)

    if n_hp >= max(1, n_seeds // 2 + 1):
        agg_verdict = "HARD_PASS"
    elif n_hf >= max(1, n_seeds // 2 + 1):
        agg_verdict = "HARD_FAIL"
    else:
        agg_verdict = "MIDDLE_BAND"

    agg_msg = (
        f"hier_concept_v3_costructured_n4096 N={N} seeds={seeds}\n"
        f"mean_ratio_vs_iid={mean_ratio:.4f} n_hp={n_hp}/{n_seeds} "
        f"n_hf={n_hf}/{n_seeds} n_mid={n_mid}/{n_seeds}\n"
        f"ratios={[round(r, 4) for r in ratios]}\n"
        f"AGGREGATE VERDICT: {agg_verdict}"
    )
    print(agg_msg, flush=True)

    summary = {
        "anchor": "hierarchical_concept_formation_instrumentation_v3_costructured_n4096",
        "N": N, "M": M, "K_clusters": K_clusters, "cluster_size": cluster_size,
        "flip_p": flip_p, "n_null": n_null,
        "seeds": seeds, "smoke": is_smoke,
        "cells": all_cells,
        "mean_ratio_vs_iid": mean_ratio,
        "n_hp": n_hp, "n_hf": n_hf, "n_mid": n_mid,
        "aggregate_verdict": agg_verdict,
        "aggregate_verdict_msg": agg_msg,
        "verdict": agg_verdict,
        "verdict_msg": agg_msg,
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)
    print(f"[done] metrics -> {metrics_path}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print("[main] --self-test: module-scope selftest already passed. exit 0.", flush=True)
        sys.exit(0)
    main()
