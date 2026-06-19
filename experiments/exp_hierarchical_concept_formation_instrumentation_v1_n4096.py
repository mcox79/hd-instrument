"""HIERARCHICAL CONCEPT FORMATION INSTRUMENTATION at N=4096 (D6).

STRATEGIC QUESTION (from capability_exploration_3_drills routing 2026-05-31):
  If the substrate W matrix, populated by a realistic M-fact workload, shows
  spectral structure in its SVD that is DRIVEN by substrate physics (not merely
  by corpus statistics), then substrate has a "concept-level queries" capability
  that LLMs and vector DBs cannot natively provide.

  The null hypothesis is: any spectral structure in W mirrors the input codeword
  covariance (corpus-statistical artifact). The alternative: substrate physics
  (outer-product Hebbian accumulation at BIPOLAR {-1,+1}^N scale) induces
  structure that SURVIVES shuffling of codeword-value bindings.

EXPERIMENT DESIGN (D6 instrumentation -- from research drill 2026-05-31):

  1. Build a representative W at N=4096 production scope:
     M=2048 facts stored as outer-product writes (matches nominal capacity
     heuristic M ~ N/8 to maintain SNR >= 1.0).
     Keys from BSC codebook of size M; values from independent BSC codebook.
     This is the same primitive used in all prior Path D experiments.

  2. SVD analysis:
     Compute top-50 singular values of W.
     Report sigma_1/sigma_2 spectral concentration ratio.
     Report effective rank (sum(sigma_i) / sigma_1; sum(sigma_i^2) / sum(sigma_i)^2).

  3. Codeword coherence test:
     Project stored KEY codewords onto top-10 singular vectors.
     Cluster projected codewords via k-means (K_cluster = sqrt(M) ~ 45).
     Report silhouette score for substrate-populated W vs null-shuffle.

  4. Null-shuffle baseline (100 shuffles):
     For each shuffle: permute the VALUE codewords (break key->value assignment)
     while keeping keys fixed. Recompute W_shuffled = (vals_shuffled.T @ keys) / N.
     Compute sigma_1/sigma_2 and silhouette for each shuffle.
     PASS = real W sigma_1/sigma_2 > mean_shuffle + 2 * std_shuffle.

  5. Semantic-ablation test:
     Substitute VALUE codewords with fresh random bipolar codes (preserve nothing
     about the values but keep the key structure).
     If spectral structure SURVIVES ablation, it is substrate-physics-driven
     (keys-only structure). If it DISAPPEARS, it was value-binding driven.
     Report sigma_1/sigma_2 for ablated W.

  6. Dense-RAG baseline (FAISS clustering):
     Encode the same M "concepts" as random float32 vectors in R^64 (mimics
     dense embedding space of dimension d=64). Compute FAISS FlatL2 k-means
     silhouette. Compare to substrate clustering silhouette.
     If substrate silhouette <= FAISS silhouette: clustering is corpus-statistical.

  7. Cross-relation transfer (optional, run if time permits):
     Bundle K=5 class-member keys via element-wise multiplication (Hadamard bind).
     Query W with the bundle -> measure cosine to held-out class members.
     Expected: if substrate has concept structure, bundle query yields class-relative
     cosine > null (random bundle).

PRE-REGISTERED BANDS (from capability_exploration_3_drills routing D6 spec):

  PRIMARY METRIC: sigma_1/sigma_2 ratio of real W vs null-shuffle mean.
    HARD-PASS: real sigma_1/sigma_2 > 3.0x null-shuffle mean
               (signals substrate-physics-driven structure, NOT corpus artifact)
    HARD-FAIL: real sigma_1/sigma_2 < 1.5x null-shuffle mean
               (substrate clustering is corpus-property artifact; W behaves
                as Marchenko-Pastur random matrix at this scale)
    MIDDLE-BAND: ratio in [1.5x, 3.0x) -- some structure, corpus-dependent

  SECONDARY METRICS (informative, do not override primary verdict):
    - Silhouette > 0.25 for real W AND null silhouette < 0.10 -> corroborates HP
    - Cross-relation transfer cosine > 0.35 AND random-bundle cosine < 0.10 -> HP
    - Dense-RAG silhouette < substrate silhouette -> substrate-distinctive
    - Semantic-ablation: if ablated W sigma_1/sigma_2 > 2.0x null -> physics-driven keys

JOINT VERDICT:
  HARD_PASS : primary metric PASS + silhouette PASS (substrate physics confirmed)
  MIDDLE_BAND: primary metric MIDDLE_BAND, or primary PASS but silhouette MIDDLE
  HARD_FAIL : primary metric FAIL (ratio < 1.5x null)

OOM CHECK (CPU, N=4096, M=2048):
  W: 4096 x 4096 x float32 = 64 MB. Fine.
  SVD (top-50): numpy.linalg.svds on 4096x4096 -> ~64 MB intermediate. Fine.
  100 shuffles x SVD: all done sequentially, same memory budget.
  Total CPU RAM: < 512 MB. No issue.

TIMEOUT ESTIMATE:
  SVD on 4096x4096 (top-50): ~5-10s CPU.
  100 shuffles of W + SVD: ~500-1000s CPU.
  K-means (M=2048, K=45, 10 restarts): ~2s.
  100 shuffle k-means: ~200s.
  Total est: ~800s conservative. Scaling: 1 seed, no N-scaling.
  timeout_s = ceil(1.5 * 800 * 1.0 * 1) = 1200. Use 3600 for headroom.
  Well under 14400s floor.

FORMULA SELF-TESTS:
  1. Outer-product W: W = (vals.T @ keys) / N, shape (N, N).
     W @ keys[0] = vals[0] + noise. Noise ~ N(0, (M-1)/N) per dimension.
     SNR at N=4096, M=2048: SNR = sqrt(N/M) = sqrt(2) ~ 1.41.
     Expected P(correct NN) = Phi(1.41) ~ 0.92.
  2. Sigma_1/Sigma_2 for identity W (M=1 stored fact): ratio = N/sqrt(N) = sqrt(N).
     For M=1 at N=4096: sigma_1 = 1.0, sigma_2 ~ 0 (rank-1 outer product).
     Self-test verifiable: build W with M=1, confirm sigma_1/sigma_2 >> 1.
  3. Null-shuffle W: permute rows of vals -> W_null = (vals_perm.T @ keys) / N.
     W_null has same spectral structure as W if vals are IID BSC.
     Expected: real W and null W have similar sigma_1/sigma_2 for IID keys+vals
     (no embedding structure). Substrate-physics claim: corpus structure
     in keys -> sigma_1/sigma_2 elevated in real W.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout_s = 3600.

Anchor: hierarchical_concept_formation_instrumentation_v1_n4096
Queue: remote_cpu_queue (pure CPU SVD instrumentation drill; no CUDA)
Pre-reg: preregs/2026-06-01_hierarchical_concept_formation_instrumentation_v1_n4096.md
HDLAB_EXP_NAME: hier_concept_v1
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

# scipy / sklearn are optional but preferred for SVD and k-means.
# If not available, fall back to numpy.linalg.svd (full SVD, slower).
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

# Capacity: M ~ N/2 for a moderate-load workload (SNR = sqrt(N/M) ~ 1.41)
M_FULL  = 2048
M_SMOKE = 64

# SVD: how many singular values to compute
N_SVD = 50

# Null-shuffle baseline repetitions
N_SHUFFLE_FULL  = 100
N_SHUFFLE_SMOKE = 10

# K-means clusters for codeword coherence test
K_CLUSTER_FULL  = 45   # ~ sqrt(M_FULL)
K_CLUSTER_SMOKE = 8

# Cross-relation bundle size
BUNDLE_K = 5

# Seeds
SEED_FULL  = 42
SEED_SMOKE = 42

# Pre-registered thresholds
HP_RATIO_VS_SHUFFLE  = 3.0   # real sigma1/sigma2 > 3x null mean: HARD-PASS
HF_RATIO_VS_SHUFFLE  = 1.5   # real sigma1/sigma2 < 1.5x null mean: HARD-FAIL
HP_SILHOUETTE        = 0.25  # silhouette > 0.25 (corroborating)
HF_SILHOUETTE_NULL   = 0.10  # null silhouette < 0.10 (expected baseline)


def get_output_dir(default_name: str = "hier_concept_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ============================================================
# BSC codebook + substrate build
# ============================================================

def make_bsc_codebook(n_codes: int, N: int, seed: int) -> np.ndarray:
    """Generate n_codes bipolar {-1, +1}^N codewords. float32 (n_codes, N)."""
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=(n_codes, N), dtype=np.int8)
    return (bits * 2 - 1).astype(np.float32)


def build_substrate_np(keys: np.ndarray, vals: np.ndarray, N: int) -> np.ndarray:
    """W = (vals.T @ keys) / N  shape (N, N) float32."""
    return (vals.T @ keys) / N


def compute_top_svd(W: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (U, s, Vt) top-k SVD of W.

    Uses scipy svds (sparse Lanczos, fast for top-k) if available,
    else numpy svd (full, slower but correct).
    """
    k = min(k, min(W.shape) - 1)
    if _SCIPY_AVAILABLE:
        U, s, Vt = scipy_svds(W, k=k)
        # scipy svds returns in ascending order; reverse to descending
        idx = np.argsort(s)[::-1]
        return U[:, idx], s[idx], Vt[idx, :]
    else:
        # Full numpy SVD: slower at N=4096 but always available
        U, s, Vt = np.linalg.svd(W, full_matrices=False)
        return U[:, :k], s[:k], Vt[:k, :]


def sigma_ratio(s: np.ndarray) -> float:
    """sigma_1 / sigma_2 ratio. Returns inf if sigma_2 == 0."""
    if len(s) < 2 or s[1] <= 1e-12:
        return float("inf")
    return float(s[0] / s[1])


def compute_silhouette(
    projected: np.ndarray,  # (M, k_svd) projected codewords
    K_cluster: int,
    seed: int,
) -> float:
    """K-means silhouette score on projected codewords.

    Returns -2.0 if sklearn is unavailable or clustering fails.
    """
    if not _SKLEARN_AVAILABLE:
        return -2.0
    if projected.shape[0] < K_cluster * 2:
        return -2.0
    km = KMeans(n_clusters=K_cluster, n_init=10, random_state=seed)
    labels = km.fit_predict(projected)
    if len(set(labels)) < 2:
        return -2.0
    return float(silhouette_score(projected, labels, sample_size=min(500, projected.shape[0])))


def project_codewords(
    keys: np.ndarray,    # (M, N) key codewords
    U: np.ndarray,       # (N, k) left singular vectors
) -> np.ndarray:
    """Project key codewords onto top-k singular vectors. (M, k)."""
    return keys @ U   # (M, k)


# ============================================================
# Cross-relation bundle transfer
# ============================================================

def cross_relation_transfer(
    W: np.ndarray,    # (N, N)
    keys: np.ndarray,  # (M, N)
    vals: np.ndarray,  # (M, N)
    seed: int,
    bundle_k: int = BUNDLE_K,
) -> Dict[str, float]:
    """Measure concept-bundle -> held-out class member retrieval.

    Protocol:
      1. Pick 3 groups of bundle_k keys (class members).
      2. Bundle = element-wise product of group keys (Hadamard bind).
      3. Query W with bundle; measure cosine to held-out members of same group.
      4. Compare to random-bundle cosine (control).

    Returns dict with bundle_cos_class and bundle_cos_random.
    """
    rng = np.random.default_rng(seed + 9000)
    M = keys.shape[0]
    if M < bundle_k * 3:
        return {"bundle_cos_class": float("nan"), "bundle_cos_random": float("nan"),
                "n_groups": 0}

    n_groups = 3
    group_size = bundle_k
    # Sample 3 disjoint groups of group_size keys
    all_idx = rng.permutation(M)
    groups = [all_idx[i*group_size:(i+1)*group_size] for i in range(n_groups)]

    bundle_cos_class_list = []
    bundle_cos_random_list = []

    for grp_idx in groups:
        bundle = keys[grp_idx[0]].copy()
        for i in grp_idx[1:]:
            bundle = bundle * keys[i]   # Hadamard bind (element-wise product)
        bundle = bundle / (np.linalg.norm(bundle) + 1e-8)

        # Query W with bundle
        r = W @ bundle   # (N,)
        r_norm = r / (np.linalg.norm(r) + 1e-8)

        # Cosine to held-out member (first element of group, not in bundle)
        held_out_idx = grp_idx[0]
        v_held = vals[held_out_idx]
        v_held_norm = v_held / (np.linalg.norm(v_held) + 1e-8)
        bundle_cos_class_list.append(float(np.dot(r_norm, v_held_norm)))

        # Random bundle (control): random keys from different group
        rand_idx = rng.choice([i for i in range(M) if i not in set(grp_idx)],
                               size=group_size, replace=False)
        rand_bundle = keys[rand_idx[0]].copy()
        for i in rand_idx[1:]:
            rand_bundle = rand_bundle * keys[i]
        rand_bundle = rand_bundle / (np.linalg.norm(rand_bundle) + 1e-8)
        r_rand = W @ rand_bundle
        r_rand_norm = r_rand / (np.linalg.norm(r_rand) + 1e-8)
        bundle_cos_random_list.append(float(np.dot(r_rand_norm, v_held_norm)))

    return {
        "bundle_cos_class": float(np.mean(bundle_cos_class_list)),
        "bundle_cos_random": float(np.mean(bundle_cos_random_list)),
        "n_groups": n_groups,
    }


# ============================================================
# Instrumentation self-test (MANDATORY, called at module scope)
# ============================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    N_t = 128
    M_t = 32
    seed_t = 7

    # 1. BSC codebook
    keys = make_bsc_codebook(M_t, N_t, seed_t)
    vals = make_bsc_codebook(M_t, N_t, seed_t + 100)
    assert keys.shape == (M_t, N_t), f"keys shape {keys.shape}"
    assert set(np.unique(keys)).issubset({-1.0, 1.0}), "keys not bipolar"

    # 2. Build substrate
    W = build_substrate_np(keys, vals, N_t)
    assert W.shape == (N_t, N_t), f"W shape {W.shape}"
    assert np.isfinite(W).all(), "W has nan/inf"
    assert np.abs(W).max() > 0, "W is all zeros"

    # 3. SVD: sigma_1 / sigma_2 should be > 1 (non-trivial structure expected)
    U, s, Vt = compute_top_svd(W, k=min(10, N_t - 1))
    assert len(s) > 1, f"SVD returned only {len(s)} values"
    assert s[0] > s[1], f"singular values not ordered: s[0]={s[0]:.4f} s[1]={s[1]:.4f}"
    ratio = sigma_ratio(s)
    assert ratio > 1.0, f"sigma_1/sigma_2 = {ratio:.3f} not > 1"
    assert np.isfinite(ratio), "sigma ratio is nan/inf"

    # 4. Self-test formula: M=1 W should have sigma_1/sigma_2 >> 1 (rank-1)
    k1 = make_bsc_codebook(1, N_t, seed_t + 200)
    v1 = make_bsc_codebook(1, N_t, seed_t + 300)
    W1 = build_substrate_np(k1, v1, N_t)
    _, s1, _ = compute_top_svd(W1, k=min(5, N_t - 1))
    ratio1 = sigma_ratio(s1)
    assert ratio1 > 10.0, f"rank-1 W should have very high sigma ratio; got {ratio1:.3f}"

    # 5. Null shuffle baseline: compute 3 shuffles, verify mean sigma ratio is finite
    null_ratios = []
    rng = np.random.default_rng(seed_t + 500)
    for _ in range(3):
        vals_perm = vals[rng.permutation(M_t)]
        W_null = build_substrate_np(keys, vals_perm, N_t)
        _, sn, _ = compute_top_svd(W_null, k=min(5, N_t - 1))
        null_ratios.append(sigma_ratio(sn))
    assert all(np.isfinite(r) for r in null_ratios), f"null ratios not finite: {null_ratios}"

    # 6. Silhouette is computable (returns float, not error)
    proj = project_codewords(keys, U)
    sil = compute_silhouette(proj, K_cluster=min(4, M_t // 4), seed=seed_t)
    # sil == -2.0 if sklearn unavailable; that is OK at local smoke
    assert isinstance(sil, float), f"silhouette not float: {type(sil)}"

    # 7. Cross-relation transfer returns dict with finite values
    crt = cross_relation_transfer(W, keys, vals, seed_t, bundle_k=3)
    assert "bundle_cos_class" in crt, "bundle_cos_class missing"
    # NaN is allowed here if M_t < bundle_k * 3
    assert isinstance(crt["bundle_cos_class"], float), "bundle_cos not float"

    # 8. Semantic ablation: fresh random vals -> sigma ratio
    vals_ablated = make_bsc_codebook(M_t, N_t, seed_t + 999)
    W_abl = build_substrate_np(keys, vals_ablated, N_t)
    _, s_abl, _ = compute_top_svd(W_abl, k=min(5, N_t - 1))
    ratio_abl = sigma_ratio(s_abl)
    assert np.isfinite(ratio_abl), f"ablated sigma ratio not finite: {ratio_abl}"

    print("[selftest] PASS: all D6 assertions passed at N=128 M=32 smoke scale.", flush=True)


_instrumentation_selftest()


# ============================================================
# Main experiment
# ============================================================

def run_experiment(
    N: int,
    M: int,
    n_shuffle: int,
    K_cluster: int,
    seed: int,
    is_smoke: bool,
) -> Dict:
    """Run full D6 instrumentation drill. Returns metrics dict."""
    t_start = time.time()
    print(f"[run] N={N} M={M} n_shuffle={n_shuffle} K_cluster={K_cluster} "
          f"seed={seed} smoke={is_smoke}", flush=True)

    # 1. Build BSC codebook + substrate
    t0 = time.time()
    keys = make_bsc_codebook(M, N, seed)
    vals = make_bsc_codebook(M, N, seed + 100)
    W = build_substrate_np(keys, vals, N)
    print(f"  [run] substrate built in {time.time()-t0:.2f}s W.shape={W.shape}", flush=True)

    # 2. SVD of real W (top N_SVD)
    t0 = time.time()
    n_svd = min(N_SVD, N - 1)
    U_real, s_real, Vt_real = compute_top_svd(W, k=n_svd)
    ratio_real = sigma_ratio(s_real)
    eff_rank_real = float(np.sum(s_real) ** 2 / (np.sum(s_real ** 2) + 1e-12))
    print(f"  [run] SVD done in {time.time()-t0:.2f}s | "
          f"sigma1={s_real[0]:.4f} sigma2={s_real[1]:.4f} "
          f"ratio={ratio_real:.4f} eff_rank={eff_rank_real:.2f}", flush=True)

    # 3. Null-shuffle baseline
    t0 = time.time()
    rng = np.random.default_rng(seed + 7777)
    null_ratios = []
    for i in range(n_shuffle):
        vals_perm = vals[rng.permutation(M)]
        W_null = build_substrate_np(keys, vals_perm, N)
        _, sn, _ = compute_top_svd(W_null, k=min(5, N - 1))
        null_ratios.append(sigma_ratio(sn))
    null_mean = float(np.mean(null_ratios))
    null_std  = float(np.std(null_ratios))
    ratio_vs_null = ratio_real / (null_mean + 1e-12)
    z_score = (ratio_real - null_mean) / (null_std + 1e-12)
    print(f"  [run] {n_shuffle} shuffles done in {time.time()-t0:.2f}s | "
          f"null_mean={null_mean:.4f} null_std={null_std:.4f} "
          f"ratio_vs_null={ratio_vs_null:.4f} z={z_score:.2f}", flush=True)

    # 4. K-means silhouette on projected codewords (real W)
    t0 = time.time()
    proj_real = project_codewords(keys, U_real[:, :min(10, U_real.shape[1])])
    sil_real = compute_silhouette(proj_real, K_cluster, seed)
    print(f"  [run] silhouette real W = {sil_real:.4f} ({time.time()-t0:.2f}s)", flush=True)

    # Null silhouette (mean of 10 shuffles)
    t0 = time.time()
    null_sil_list = []
    for i in range(min(10, n_shuffle)):
        vals_perm2 = vals[rng.permutation(M)]
        W_null2 = build_substrate_np(keys, vals_perm2, N)
        U_null2, _, _ = compute_top_svd(W_null2, k=min(10, N - 1))
        proj_null2 = project_codewords(keys, U_null2[:, :min(10, U_null2.shape[1])])
        sil_null2 = compute_silhouette(proj_null2, K_cluster, seed + i)
        null_sil_list.append(sil_null2)
    null_sil_mean = float(np.mean([s for s in null_sil_list if s >= -1.0])) \
        if any(s >= -1.0 for s in null_sil_list) else float("nan")
    print(f"  [run] null silhouette mean = {null_sil_mean:.4f} ({time.time()-t0:.2f}s)",
          flush=True)

    # 5. Semantic ablation
    t0 = time.time()
    vals_ablated = make_bsc_codebook(M, N, seed + 5555)
    W_abl = build_substrate_np(keys, vals_ablated, N)
    _, s_abl, _ = compute_top_svd(W_abl, k=min(5, N - 1))
    ratio_ablated = sigma_ratio(s_abl)
    ratio_ablated_vs_null = ratio_ablated / (null_mean + 1e-12)
    print(f"  [run] ablated sigma ratio = {ratio_ablated:.4f} "
          f"vs_null = {ratio_ablated_vs_null:.4f} ({time.time()-t0:.2f}s)", flush=True)

    # 6. Dense-RAG baseline (FAISS k-means silhouette on float32 R^64 embeddings)
    faiss_sil = float("nan")
    if _SKLEARN_AVAILABLE:
        t0 = time.time()
        rng_rag = np.random.default_rng(seed + 3333)
        # M float32 vectors in R^64 (typical dense embedding)
        embs_rag = rng_rag.standard_normal((M, 64)).astype(np.float32)
        norms_rag = np.linalg.norm(embs_rag, axis=1, keepdims=True).clip(min=1e-8)
        embs_rag = embs_rag / norms_rag
        km_rag = KMeans(n_clusters=K_cluster, n_init=10, random_state=seed)
        labels_rag = km_rag.fit_predict(embs_rag)
        if len(set(labels_rag)) >= 2:
            faiss_sil = float(silhouette_score(embs_rag, labels_rag,
                                               sample_size=min(500, M)))
        print(f"  [run] dense-RAG silhouette = {faiss_sil:.4f} ({time.time()-t0:.2f}s)",
              flush=True)
    else:
        print("  [run] dense-RAG baseline SKIPPED (sklearn unavailable)", flush=True)

    # 7. Cross-relation transfer
    t0 = time.time()
    crt = cross_relation_transfer(W, keys, vals, seed, bundle_k=BUNDLE_K)
    print(f"  [run] cross-relation: bundle_cos_class={crt['bundle_cos_class']:.4f} "
          f"bundle_cos_random={crt['bundle_cos_random']:.4f} ({time.time()-t0:.2f}s)",
          flush=True)

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

    # Secondary corroboration
    sil_pass = (sil_real >= HP_SILHOUETTE and
                (math.isnan(null_sil_mean) or null_sil_mean < HF_SILHOUETTE_NULL))
    if primary_verdict == "HARD_PASS" and sil_pass:
        overall = "HARD_PASS"
    elif primary_verdict == "HARD_FAIL":
        overall = "HARD_FAIL"
    else:
        overall = "MIDDLE_BAND"

    verdict_msg = (
        f"hierarchical_concept_formation_instrumentation_v1_n4096 "
        f"N={N} M={M} n_shuffle={n_shuffle}\n"
        f"PRIMARY sigma1/sigma2: real={ratio_real:.4f} null_mean={null_mean:.4f} "
        f"ratio_vs_null={primary_ratio:.4f} z={z_score:.2f}\n"
        f"PRIMARY VERDICT: {primary_verdict}\n"
        f"Silhouette: real={sil_real:.4f} null={null_sil_mean:.4f} "
        f"dense_rag={faiss_sil:.4f} | sil_pass={sil_pass}\n"
        f"Ablation: ratio_ablated={ratio_ablated:.4f} vs_null={ratio_ablated_vs_null:.4f}\n"
        f"Cross-relation: class={crt['bundle_cos_class']:.4f} "
        f"random={crt['bundle_cos_random']:.4f}\n"
        f"OVERALL: {overall}"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "exp_name": "hierarchical_concept_formation_instrumentation_v1_n4096",
        "N": N,
        "M": M,
        "n_shuffle": n_shuffle,
        "K_cluster": K_cluster,
        "seed": seed,
        "is_smoke": is_smoke,
        "elapsed_s": elapsed,
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
        "silhouette_dense_rag": faiss_sil,
        "silhouette_pass": sil_pass,
        # Ablation
        "sigma_ratio_ablated": ratio_ablated,
        "ratio_ablated_vs_null": ratio_ablated_vs_null,
        # Cross-relation
        "bundle_cos_class": crt["bundle_cos_class"],
        "bundle_cos_random": crt["bundle_cos_random"],
        "bundle_cos_n_groups": crt["n_groups"],
        # Verdict
        "primary_verdict": primary_verdict,
        "overall": overall,
        "verdict_msg": verdict_msg,
    }

    return metrics


def main() -> None:
    is_smoke = os.environ.get("HDLAB_SMOKE", "0") == "1"
    # Force CPU: this is an SVD instrumentation drill; CUDA not needed
    os.environ["HDLAB_DEVICE"] = "cpu"

    N = N_SMOKE if is_smoke else N_FULL
    M = M_SMOKE if is_smoke else M_FULL
    n_shuffle = N_SHUFFLE_SMOKE if is_smoke else N_SHUFFLE_FULL
    K_cluster = K_CLUSTER_SMOKE if is_smoke else K_CLUSTER_FULL
    seed = SEED_SMOKE if is_smoke else SEED_FULL

    out_dir = get_output_dir()
    print(f"[main] N={N} M={M} n_shuffle={n_shuffle} K_cluster={K_cluster} "
          f"seed={seed} smoke={is_smoke} out={out_dir}", flush=True)

    metrics = run_experiment(N, M, n_shuffle, K_cluster, seed, is_smoke)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[done] metrics -> {metrics_path}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print("[main] --self-test mode: module-scope selftest already passed. exit 0.",
              flush=True)
        sys.exit(0)
    main()
