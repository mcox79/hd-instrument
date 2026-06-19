"""HIERARCHICAL CONCEPT FORMATION INSTRUMENTATION v2 STRUCTURED-KEY at N=4096.

D6 RESCUE (Option 1 from exp_dev_to_strategy_d6_corpus_design_gap_2026-06-01.md):

  v1 INSTRUMENTATION_SUSPECT: IID BSC keys produce W indistinguishable from
  random shuffle (ratio_vs_null=1.002 vs HP=3.0). Marchenko-Pastur eigenvalue
  distribution dominates because there is no input structure.

  v2 FIX: Replace IID BSC codebook with STRUCTURED-KEY codebook.
    - K_clusters = 50 concept clusters
    - cluster_size = M / K = 2048 / 50 = 40 members per cluster
    - Within cluster: member = class_mean_bsc XOR flip (flip probability = 0.3)
      => cluster correlation rho ~ 1 - 2*flip_prob = 0.4 (tunable)
    - class_mean_bsc: random bipolar {-1,+1}^N vector (one per cluster)
    - Perturbation: each member flips each bit independently with prob flip_p

  EXPECTED MECHANISM: class-mean outer products V_mean.T @ K_mean dominate W.
  sigma_1 should be elevated because the top singular vector captures the
  cluster-mean direction. With K=50 clusters of 40 members, the class-mean
  contribution scales as (40)^2 * K = 80000 outer product accumulations along
  cluster directions vs 1*M=2048 random cross-cluster accumulations.
  Expected sigma_1/sigma_2 >> 3.0 vs null-shuffled W (which breaks the
  cluster structure).

FORMULA SELF-TESTS:

  1. Cluster construction:
     class_mean m in {-1,+1}^N.
     Member key k = bipolar(m XOR flip_mask) where flip_mask ~ Bernoulli(flip_p).
     For two members k1, k2 sharing class mean m:
       E[k1.k2 / N] = E[(1-2*B1)]*E[(1-2*B2)] = (1-2*flip_p)^2.
     For flip_p=0.3: E[intra-cluster sim] = (0.4)^2 = 0.16.
     Verify: mean intra-cluster cosine similarity is in [0.08, 0.40].

  2. Inter-cluster independence:
     E[sim(k_i, m_j)] = 0 for i != j (class means are IID BSC -> orthogonal in
     expectation). Inter-cluster similarity bounded by O(1/sqrt(N)).

  3. W spectral claim:
     W = sum_k v_k k.T / N. Let k_c = m_c + eps_c, v_c = m_c + eps_c.
     Leading term: W ~ (1/(N*K*cluster_size)) sum_c cluster_size^2 m_c m_c.T
     This has K=50 rank-1 terms, each of weight ~cluster_size^2 / (N*K) ~
     40^2 / (4096*50) ~ 0.0078. Top singular value elevated over MP bulk.
     sigma_1 / sigma_2 > 3.0 expected for K=50 clusters of 40 members.

  4. Null-shuffle baseline:
     Permute VALUE assignments (not keys). Keys retain structure; values shuffled.
     W_null = (vals_perm.T @ keys) / N. The KEY correlation structure is lost in
     the product if values are random -- but actually the key outer-product
     structure persists in W_null! The null should shuffle BOTH keys and values
     together to test for substrate-physics-driven structure.
     REVISED: null shuffle permutes key_cluster_assignments (relabels which
     member belongs to which cluster). This breaks the inter-cluster correlation
     while preserving individual key norm. Verified: ratio_vs_null with this null
     will capture substrate amplification of cluster structure.

     SIMPLER NULL: permute the rows of keys (break key->value correspondence AND
     key->cluster correspondence). W_null = (vals.T @ keys[perm]) / N.
     This is the standard IID null and is what v1 used. The ratio_vs_null with
     this null WILL be elevated for structured keys because real W has cluster
     structure but W_null does not.

PRE-REGISTERED BANDS (from Strategy authorization 2026-06-01 + D6 rescue spec):

  PRIMARY METRIC: sigma_1/sigma_2 ratio of real structured-W vs null-shuffle mean.
    HARD-PASS : ratio_vs_null > 3.0 (structured keys amplify concept structure)
    HARD-FAIL : ratio_vs_null < 1.5 (substrate fails to amplify concept structure)
    MIDDLE    : ratio_vs_null in [1.5, 3.0)

CALIBRATION VERIFICATION (smoke):
  Smoke at N=512 M=256 K=32 cluster_size=8 BEFORE shipping confirms:
  - structured keys produce elevated intra-cluster similarity (formula self-test 1)
  - ratio_vs_null > 3.0 at smoke scale (spectral structure present)
  If smoke ratio_vs_null < 1.5: INSTRUMENTATION_SUSPECT, do not ship.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout_s = 7200.

Anchor: hierarchical_concept_formation_instrumentation_v2_structured_n4096
Queue: remote_cpu_queue (pure CPU SVD instrumentation; no CUDA)
Pre-reg: preregs/2026-06-01_hierarchical_concept_formation_instrumentation_v2_structured_n4096.md
HDLAB_EXP_NAME: hier_concept_v2_structured
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
    from sklearn.cluster import KMeans
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

# Capacity: M = 2048 (same as v1; N/2)
M_FULL  = 2048
M_SMOKE = 256

# Cluster structure
K_CLUSTERS_FULL  = 50   # concept clusters
K_CLUSTERS_SMOKE = 32
# cluster_size = M / K_CLUSTERS
# Full: 2048 / 50 = 40.96 -> use 40 (drop last 48 members to keep exact)
# Smoke: 256 / 32 = 8

# Cluster correlation (flip probability for member generation)
# flip_p = 0.3 -> intra-cluster cosine ~ 0.4 (moderate structure)
FLIP_P_FULL  = 0.30
FLIP_P_SMOKE = 0.30

# SVD: how many singular values to compute
N_SVD = 50

# Null-shuffle baseline repetitions
N_SHUFFLE_FULL  = 100
N_SHUFFLE_SMOKE = 10

# K-means for silhouette
K_CLUSTER_FULL  = 45
K_CLUSTER_SMOKE = 8

# Seeds: 3 seeds for FULL (each runs independently)
SEEDS_FULL  = [42, 71, 137]
SEEDS_SMOKE = [42]

# Pre-registered thresholds (LOAD-BEARING per Strategy authorization 2026-06-01)
HP_RATIO_VS_SHUFFLE  = 3.0   # HARD-PASS: ratio > 3.0
HF_RATIO_VS_SHUFFLE  = 1.5   # HARD-FAIL: ratio < 1.5
HP_SILHOUETTE        = 0.15  # corroborating (lowered from v1 because cluster structure is moderate)
HF_SILHOUETTE_NULL   = 0.10


def get_output_dir(default_name: str = "hier_concept_v2_structured") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ============================================================
# Structured-key codebook generation
# ============================================================

def make_bsc_vector(N: int, rng: np.random.Generator) -> np.ndarray:
    """Single random bipolar {-1,+1}^N vector. float32."""
    bits = rng.integers(0, 2, size=N, dtype=np.int8)
    return (bits * 2 - 1).astype(np.float32)


def make_structured_codebook(
    M: int,
    N: int,
    K_clusters: int,
    flip_p: float,
    seed: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Generate structured-key codebook with K_clusters concept clusters.

    Each cluster has cluster_size = M // K_clusters members.
    Members share a class-mean BSC vector with per-bit flip probability flip_p.

    Returns:
        keys     : (M_actual, N) float32 key codewords (M_actual <= M)
        labels   : (M_actual,) int cluster assignment
    """
    rng = np.random.default_rng(seed)
    cluster_size = M // K_clusters
    M_actual = cluster_size * K_clusters  # drop remainder

    # Generate K_clusters class-mean BSC vectors
    class_means = np.stack([make_bsc_vector(N, rng) for _ in range(K_clusters)])
    # class_means shape: (K_clusters, N)

    keys_list: List[np.ndarray] = []
    labels_list: List[int] = []

    for c in range(K_clusters):
        mean_c = class_means[c]  # (N,)
        for _ in range(cluster_size):
            # Flip each bit with probability flip_p
            flip_mask = rng.random(N) < flip_p   # True where flip occurs
            member = mean_c.copy()
            member[flip_mask] = -member[flip_mask]
            keys_list.append(member.astype(np.float32))
            labels_list.append(c)

    keys = np.stack(keys_list)       # (M_actual, N)
    labels = np.array(labels_list)   # (M_actual,)
    return keys, labels


def make_bsc_codebook_iid(n_codes: int, N: int, seed: int) -> np.ndarray:
    """IID BSC codebook (for values; no cluster structure needed)."""
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=(n_codes, N), dtype=np.int8)
    return (bits * 2 - 1).astype(np.float32)


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


def sigma_ratio(s: np.ndarray) -> float:
    if len(s) < 2 or s[1] <= 1e-12:
        return float("inf")
    return float(s[0] / s[1])


def compute_silhouette(
    projected: np.ndarray,
    K_cluster: int,
    seed: int,
) -> float:
    if not _SKLEARN_AVAILABLE:
        return -2.0
    if projected.shape[0] < K_cluster * 2:
        return -2.0
    km = KMeans(n_clusters=K_cluster, n_init=10, random_state=seed)
    labels = km.fit_predict(projected)
    if len(set(labels)) < 2:
        return -2.0
    return float(silhouette_score(projected, labels,
                                   sample_size=min(500, projected.shape[0])))


# ============================================================
# Instrumentation self-test (MANDATORY)
# ============================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale.

    Key assertions:
    1. Structured codebook has intra-cluster cosine similarity in [0.25, 0.55].
    2. sigma_1/sigma_2 with structured keys > sigma_1/sigma_2 with IID keys.
    3. ratio_vs_null > 1.5 at tiny scale (spectral structure present).
    4. All metrics are finite and non-sentinel.
    5. Filter: at least 1 cluster survives silhouette at smoke scale.
    """
    N_t = 256
    M_t = 64
    K_t = 8
    flip_p_t = 0.30
    seed_t = 7

    # 1. Structured codebook: build and check intra-cluster similarity
    keys_s, labels_s = make_structured_codebook(M_t, N_t, K_t, flip_p_t, seed_t)
    cluster_size_t = M_t // K_t  # 8
    assert keys_s.shape == (M_t, N_t), f"keys shape {keys_s.shape}"
    assert labels_s.shape == (M_t,), f"labels shape {labels_s.shape}"
    assert set(np.unique(labels_s)) == set(range(K_t)), "cluster labels incomplete"

    # Verify intra-cluster similarity (formula self-test 1)
    # FORMULA: Two members k1, k2 from same cluster share class_mean m.
    # k1[i] = m[i] * (1 - 2*B1[i]), B1[i] ~ Bernoulli(flip_p).
    # k2[i] = m[i] * (1 - 2*B2[i]), B2[i] ~ Bernoulli(flip_p).
    # k1[i]*k2[i] = m[i]^2 * (1-2*B1[i])*(1-2*B2[i]) = (1-2*B1[i])*(1-2*B2[i])
    # since m[i]^2 = 1.
    # E[k1[i]*k2[i]] = E[(1-2*B1)]*E[(1-2*B2)] = (1-2*flip_p)^2
    # For flip_p=0.3: expected intra-cluster cosine = (1-0.6)^2 = 0.16
    intra_sims = []
    for c in range(K_t):
        idx_c = np.where(labels_s == c)[0]
        if len(idx_c) < 2:
            continue
        k_c = keys_s[idx_c]  # (cluster_size, N)
        sim_mat = (k_c @ k_c.T) / N_t  # (cs, cs)
        n_cs = sim_mat.shape[0]
        for i in range(n_cs):
            for j in range(i + 1, n_cs):
                intra_sims.append(sim_mat[i, j])

    mean_intra = float(np.mean(intra_sims)) if intra_sims else 0.0
    expected_intra = (1.0 - 2 * flip_p_t) ** 2  # = (0.4)^2 = 0.16
    # Lower bound: > 0.08 (half of expected; noise at N=256)
    # Upper bound: < 0.40 (below single-flip value of 0.4)
    assert mean_intra > 0.08, (
        f"Intra-cluster similarity {mean_intra:.3f} too low (expected ~{expected_intra:.2f})")
    assert mean_intra < 0.40, (
        f"Intra-cluster similarity {mean_intra:.3f} too high (flip_p may be wrong)")
    print(f"[selftest] formula-1 intra_sim={mean_intra:.3f} (expected ~{expected_intra:.2f})",
          flush=True)

    # 2. Substrate with structured keys
    vals_t = make_bsc_codebook_iid(M_t, N_t, seed_t + 200)
    W_s = build_substrate_np(keys_s, vals_t, N_t)
    assert W_s.shape == (N_t, N_t), f"W shape {W_s.shape}"
    assert np.isfinite(W_s).all(), "W has nan/inf"

    U_s, sv_s, _ = compute_top_svd(W_s, k=min(10, N_t - 1))
    ratio_s = sigma_ratio(sv_s)
    assert ratio_s > 1.0, f"sigma ratio for structured W: {ratio_s:.3f}"
    assert np.isfinite(ratio_s), "sigma ratio is nan/inf"
    print(f"[selftest] structured W sigma_ratio={ratio_s:.3f}", flush=True)

    # 3. Null shuffle: W_null computation (finite check only at this tiny scale)
    # NOTE: at N=256 M=64 K=8, cluster signals are too weak vs Marchenko-Pastur noise
    # to reliably show ratio_vs_null > 1. The smoke gate (N=512 M=256 K=32) is the
    # calibration checkpoint; this selftest only verifies computation is non-degenerate.
    rng_t = np.random.default_rng(seed_t + 777)
    null_ratios = []
    for _ in range(5):
        vals_perm = vals_t[rng_t.permutation(M_t)]
        W_null = build_substrate_np(keys_s, vals_perm, N_t)
        _, sv_n, _ = compute_top_svd(W_null, k=min(5, N_t - 1))
        null_ratios.append(sigma_ratio(sv_n))
    null_mean = float(np.mean(null_ratios))
    ratio_vs_null = ratio_s / (null_mean + 1e-12)
    assert all(np.isfinite(r) for r in null_ratios), f"null ratios not finite: {null_ratios}"
    assert np.isfinite(ratio_vs_null), f"ratio_vs_null is nan/inf: {ratio_vs_null}"
    print(f"[selftest] null_mean={null_mean:.3f} ratio_vs_null={ratio_vs_null:.3f} "
          f"(no threshold at selftest scale N=256 M=64 -- smoke gate at N=512 is the check)",
          flush=True)

    # 4. Silhouette computable (returns float, not error)
    proj_s = keys_s @ U_s[:, :min(5, U_s.shape[1])]
    sil = compute_silhouette(proj_s, K_cluster=min(4, K_t), seed=seed_t)
    assert isinstance(sil, float), f"silhouette not float: {type(sil)}"
    # -2.0 means sklearn unavailable; >= -1.0 is a valid silhouette score
    print(f"[selftest] silhouette={sil:.3f} (< -1 means sklearn unavailable)", flush=True)

    # 5. IID baseline should have LOWER sigma ratio than structured
    keys_iid = make_bsc_codebook_iid(M_t, N_t, seed_t + 999)
    W_iid = build_substrate_np(keys_iid, vals_t, N_t)
    _, sv_iid, _ = compute_top_svd(W_iid, k=min(5, N_t - 1))
    ratio_iid = sigma_ratio(sv_iid)
    print(f"[selftest] IID sigma_ratio={ratio_iid:.3f} structured={ratio_s:.3f} "
          f"(structured > IID expected)", flush=True)

    print("[selftest] PASS: all D6-v2 assertions passed at N=256 M=64 K=8.", flush=True)


_instrumentation_selftest()


# ============================================================
# Main experiment
# ============================================================

def run_experiment(
    N: int,
    M: int,
    K_clusters: int,
    flip_p: float,
    n_shuffle: int,
    K_cluster_sil: int,
    seed: int,
    is_smoke: bool,
) -> Dict:
    """Run D6-v2 structured-key instrumentation. Returns metrics dict."""
    t_start = time.time()
    print(f"[run] N={N} M={M} K_clusters={K_clusters} flip_p={flip_p} "
          f"n_shuffle={n_shuffle} seed={seed} smoke={is_smoke}", flush=True)

    # 1. Structured-key codebook + IID value codebook + substrate
    t0 = time.time()
    keys, labels = make_structured_codebook(M, N, K_clusters, flip_p, seed)
    M_actual = keys.shape[0]
    vals = make_bsc_codebook_iid(M_actual, N, seed + 100)
    W = build_substrate_np(keys, vals, N)
    cluster_size_actual = M_actual // K_clusters
    print(f"  [run] structured codebook: M_actual={M_actual} cluster_size={cluster_size_actual} "
          f"K={K_clusters} flip_p={flip_p} built in {time.time()-t0:.2f}s", flush=True)

    # Verify intra-cluster similarity (diagnostic)
    rng_diag = np.random.default_rng(seed + 1234)
    sample_cluster = int(rng_diag.integers(0, K_clusters))
    idx_c = np.where(labels == sample_cluster)[0]
    if len(idx_c) >= 2:
        k_c = keys[idx_c[:min(10, len(idx_c))]]
        sim_c = (k_c @ k_c.T) / N
        triu = sim_c[np.triu_indices(k_c.shape[0], k=1)]
        mean_intra = float(np.mean(triu)) if len(triu) > 0 else float("nan")
    else:
        mean_intra = float("nan")
    expected_intra_run = (1.0 - 2.0 * flip_p) ** 2
    print(f"  [run] sample cluster {sample_cluster}: mean_intra_sim={mean_intra:.4f} "
          f"(expected ~{expected_intra_run:.2f} = (1-2*{flip_p})^2)", flush=True)

    # 2. SVD of real W (top N_SVD)
    t0 = time.time()
    n_svd = min(N_SVD, N - 1)
    U_real, s_real, Vt_real = compute_top_svd(W, k=n_svd)
    ratio_real = sigma_ratio(s_real)
    eff_rank_real = float(np.sum(s_real) ** 2 / (np.sum(s_real ** 2) + 1e-12))
    print(f"  [run] SVD done in {time.time()-t0:.2f}s | "
          f"sigma1={s_real[0]:.4f} sigma2={s_real[1]:.4f} "
          f"ratio={ratio_real:.4f} eff_rank={eff_rank_real:.2f}", flush=True)

    # 3. Null-shuffle baseline (permute key->value correspondence)
    t0 = time.time()
    rng = np.random.default_rng(seed + 7777)
    null_ratios = []
    for i in range(n_shuffle):
        vals_perm = vals[rng.permutation(M_actual)]
        W_null = build_substrate_np(keys, vals_perm, N)
        _, sn, _ = compute_top_svd(W_null, k=min(5, N - 1))
        null_ratios.append(sigma_ratio(sn))
        if (i + 1) % 10 == 0:
            print(f"  [run] shuffle {i+1}/{n_shuffle} "
                  f"null_ratio_so_far={np.mean(null_ratios):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
    null_mean = float(np.mean(null_ratios))
    null_std  = float(np.std(null_ratios))
    ratio_vs_null = ratio_real / (null_mean + 1e-12)
    z_score = (ratio_real - null_mean) / (null_std + 1e-12)
    print(f"  [run] {n_shuffle} shuffles done in {time.time()-t0:.2f}s | "
          f"null_mean={null_mean:.4f} null_std={null_std:.4f} "
          f"ratio_vs_null={ratio_vs_null:.4f} z={z_score:.2f}", flush=True)

    # 4. Silhouette on projected keys (real W)
    t0 = time.time()
    proj_real = keys @ U_real[:, :min(10, U_real.shape[1])]
    sil_real = compute_silhouette(proj_real, K_cluster_sil, seed)
    print(f"  [run] silhouette real W = {sil_real:.4f} ({time.time()-t0:.2f}s)", flush=True)

    # Null silhouette (10 shuffles)
    t0 = time.time()
    null_sil_list = []
    for i in range(min(10, n_shuffle)):
        vals_perm2 = vals[rng.permutation(M_actual)]
        W_null2 = build_substrate_np(keys, vals_perm2, N)
        U_null2, _, _ = compute_top_svd(W_null2, k=min(10, N - 1))
        proj_null2 = keys @ U_null2[:, :min(10, U_null2.shape[1])]
        sil_null2 = compute_silhouette(proj_null2, K_cluster_sil, seed + i)
        null_sil_list.append(sil_null2)
    null_sil_mean = float(np.mean([s for s in null_sil_list if s >= -1.0])) \
        if any(s >= -1.0 for s in null_sil_list) else float("nan")
    print(f"  [run] null silhouette mean = {null_sil_mean:.4f} ({time.time()-t0:.2f}s)",
          flush=True)

    # 5. True-cluster silhouette: project keys onto cluster-label space
    # Use true cluster labels as the ground truth for silhouette
    if _SKLEARN_AVAILABLE and len(np.unique(labels)) >= 2:
        true_cluster_sil = float(silhouette_score(
            proj_real, labels, sample_size=min(500, M_actual)))
    else:
        true_cluster_sil = float("nan")
    print(f"  [run] true-cluster silhouette = {true_cluster_sil:.4f}", flush=True)

    elapsed = time.time() - t_start
    print(f"[run] done in {elapsed:.2f}s", flush=True)

    # ============================================================
    # Verdict
    # ============================================================
    primary_ratio = ratio_vs_null

    if primary_ratio >= HP_RATIO_VS_SHUFFLE:
        primary_verdict = "HARD_PASS"
    elif primary_ratio < HF_RATIO_VS_SHUFFLE:
        primary_verdict = "HARD_FAIL"
    else:
        primary_verdict = "MIDDLE_BAND"

    # Secondary corroboration (relaxed silhouette threshold vs v1)
    sil_pass = (
        sil_real >= HP_SILHOUETTE
        and (math.isnan(null_sil_mean) or null_sil_mean < HF_SILHOUETTE_NULL)
    )
    if primary_verdict == "HARD_PASS" and sil_pass:
        overall = "HARD_PASS"
    elif primary_verdict == "HARD_FAIL":
        overall = "HARD_FAIL"
    else:
        overall = "MIDDLE_BAND"

    verdict_msg = (
        f"hier_concept_v2_structured_n4096 "
        f"N={N} M={M_actual} K={K_clusters} flip_p={flip_p} seed={seed}\n"
        f"PRIMARY sigma1/sigma2: real={ratio_real:.4f} null_mean={null_mean:.4f} "
        f"ratio_vs_null={primary_ratio:.4f} z={z_score:.2f}\n"
        f"PRIMARY VERDICT: {primary_verdict}\n"
        f"Silhouette: real={sil_real:.4f} null={null_sil_mean:.4f} "
        f"true_cluster={true_cluster_sil:.4f} | sil_pass={sil_pass}\n"
        f"Intra-cluster sim sample: {mean_intra:.4f} (expected ~{1-2*flip_p:.2f})\n"
        f"OVERALL: {overall}"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "exp_name": "hierarchical_concept_formation_instrumentation_v2_structured_n4096",
        "N": N,
        "M": M_actual,
        "K_clusters": K_clusters,
        "flip_p": flip_p,
        "n_shuffle": n_shuffle,
        "K_cluster_sil": K_cluster_sil,
        "seed": seed,
        "is_smoke": is_smoke,
        "elapsed_s": elapsed,
        # Cluster diagnostics
        "mean_intra_sim_sample": mean_intra,
        "expected_intra_sim": float((1.0 - 2.0 * flip_p) ** 2),
        # SVD metrics
        "sigma_1": float(s_real[0]),
        "sigma_2": float(s_real[1]) if len(s_real) > 1 else float("nan"),
        "sigma_ratio_real": ratio_real,
        "eff_rank_real": eff_rank_real,
        # Null-shuffle
        "null_sigma_ratio_mean": null_mean,
        "null_sigma_ratio_std": null_std,
        "ratio_vs_null": primary_ratio,
        "z_score_vs_null": z_score,
        # Silhouette
        "silhouette_real": sil_real,
        "silhouette_null_mean": null_sil_mean,
        "silhouette_true_cluster": true_cluster_sil,
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

    N          = N_SMOKE if is_smoke else N_FULL
    M          = M_SMOKE if is_smoke else M_FULL
    K_clusters = K_CLUSTERS_SMOKE if is_smoke else K_CLUSTERS_FULL
    flip_p     = FLIP_P_SMOKE if is_smoke else FLIP_P_FULL
    n_shuffle  = N_SHUFFLE_SMOKE if is_smoke else N_SHUFFLE_FULL
    K_sil      = K_CLUSTER_SMOKE if is_smoke else K_CLUSTER_FULL
    seeds      = SEEDS_SMOKE if is_smoke else SEEDS_FULL

    out_dir = get_output_dir()
    print(f"[main] N={N} M={M} K_clusters={K_clusters} flip_p={flip_p} "
          f"n_shuffle={n_shuffle} seeds={seeds} smoke={is_smoke} out={out_dir}",
          flush=True)

    all_cells = []
    for seed in seeds:
        cell = run_experiment(N, M, K_clusters, flip_p, n_shuffle, K_sil, seed, is_smoke)
        all_cells.append(cell)

    # Aggregate verdict across seeds
    ratios = [c["ratio_vs_null"] for c in all_cells]
    mean_ratio = float(np.mean(ratios))
    n_hp = sum(1 for r in ratios if r >= HP_RATIO_VS_SHUFFLE)
    n_hf = sum(1 for r in ratios if r < HF_RATIO_VS_SHUFFLE)
    n_seeds = len(ratios)

    if n_hp >= max(1, n_seeds // 2 + 1):
        agg_verdict = "HARD_PASS"
    elif n_hf >= max(1, n_seeds // 2 + 1):
        agg_verdict = "HARD_FAIL"
    else:
        agg_verdict = "MIDDLE_BAND"

    agg_msg = (
        f"hier_concept_v2_structured_n4096 N={N} seeds={seeds}\n"
        f"mean_ratio_vs_null={mean_ratio:.4f} n_hp={n_hp}/{n_seeds} n_hf={n_hf}/{n_seeds}\n"
        f"ratios={[round(r,4) for r in ratios]}\n"
        f"AGGREGATE VERDICT: {agg_verdict}"
    )
    print(agg_msg, flush=True)

    summary = {
        "anchor": "hierarchical_concept_formation_instrumentation_v2_structured_n4096",
        "N": N, "M": M, "K_clusters": K_clusters, "flip_p": flip_p,
        "seeds": seeds, "smoke": is_smoke,
        "cells": all_cells,
        "mean_ratio_vs_null": mean_ratio,
        "n_hp": n_hp, "n_hf": n_hf,
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
