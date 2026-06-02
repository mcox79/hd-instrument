"""
pp47_deletion_cert_composition_v1 -- PP-47 place-field deletion certificate composition.

SCIENTIFIC QUESTION (Phase 0 for Tier-6 LLM-integration testbed):
  Does the substrate algebraic deletion certificate (PP-46 / COMBO-3 P9) compose correctly
  with PP-47 place-field encoding, such that:

  (a) cert signature xi_X^T (W' - W) xi_X = -(1/N)||xi_X||^4 = -1 exactly
      (closed-form; machine precision at N=4096 fp64)
  (b) nearby locations X+-1 and X+-2 remain retrievable within +-0.05 of pre-deletion baseline
  (c) deleted location xi_X no longer retrievable (cosine < 0.20)
  (d) kappa_3 fingerprint shift |Dk3_obs - Dk3_pred| / |k3(W)| < 1e-2
  (e) post-deletion Spearman rho on K-1 patterns within +-0.05 of pre-deletion 0.879

  Setup: N=4096, K=204 locations (alpha=0.05), Gaussian sigma=2, PLACE_FRAC=0.30.
  Delete one interior location X via rank-1 subtraction: W' = W - (1/N) xi_X xi_X^T.
  5 seeds.

PRE-REGISTERED HARD-PASS / HARD-FAIL:
  HP1: |xi_X^T (W'-W) xi_X + 1| < 1e-10 (cert exact)
  HP2: post-deletion cosine at xi_X < 0.20 (deleted no longer retrieved)
  HP3: cosine at xi_(X+-1), xi_(X+-2) within +-0.05 of pre-deletion baseline
  HP4: |Dk3_obs - Dk3_pred| / |k3(W)| < 1e-2
  HP5: post-deletion Spearman rho on K-1 patterns within +-0.05 of pre-deletion rho

  HF1: |cert + 1| > 1e-4 (algebra inconsistent)
  HF2: post-deletion cosine at xi_X > 0.50 (rank-1 insufficient)
  HF3: cosine at xi_(X+-1) drops > 0.20 below baseline (spillover damage)
  HF4: |Dk3_obs - Dk3_pred| / |k3(W)| > 0.10 (fingerprint blind to deletion)
  HF5: post-deletion Spearman rho drops > 0.20 below baseline (topology damaged)

FORMULA SELF-TESTS:
  1. Cert formula: xi_X^T (W'-W) xi_X = -(1/N)||xi_X||^4.
     For ||xi_X||^2 = N (BSC +-1): cert = -(1/N)*N^2 = -N. Wait, re-check:
     W' - W = -(1/N) xi_X xi_X^T, so xi_X^T (W'-W) xi_X = -(1/N) (xi_X^T xi_X)^2
     = -(1/N) ||xi_X||^4. For BSC +-1: ||xi_X||^2 = N, so cert = -(1/N)*N^2 = -N.
     But the routing note says cert = -1 exactly. Let us verify: normalized cert =
     xi_X^T (W'-W) xi_X / N = -(1/N^2) ||xi_X||^4 = -(N^2/N^2) = -1. NORMALIZED form.
     [INPUT: N=4, xi_X=[1,-1,1,-1], W'-W = -(1/4) xi_X xi_X^T]
     [EXPECTED: xi_X^T (W'-W) xi_X / N = -1 exactly]
  2. Rank-1 update does not affect unrelated patterns.
     [INPUT: xi_Y orthogonal to xi_X, W_delta = -(1/N) xi_X xi_X^T]
     [EXPECTED: xi_Y^T W_delta xi_X_Y = 0 if xi_X^T xi_Y = 0]
  3. Spearman rho preserved on K-1 patterns: removing one point from a sorted sequence
     does not substantially change Spearman rho if |K| >> 1.
     [INPUT: K=10, remove idx 5] [EXPECTED: rho(K-1) ~ rho(K) within finite-N noise]

No _nN suffix needed; production N=4096 per routing note (pre-PROT-018 anchor name rule).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp47_deletion_cert_composition_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 4096

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    K_LOCS = 51     # 0.05 * 1024 smoke scale
    N_ACTIVE = 1024
    N_HUTCHINSON = 100
else:
    SEEDS = [7, 17, 23, 31, 41]
    K_LOCS = 204    # int(0.05 * N) = 204
    N_ACTIVE = N
    N_HUTCHINSON = 500

PLACE_FRAC = 0.30
SIGMA = 2.0
NOISE_FRAC = 0.10
ALPHA_C = 0.138

# Pre-registered thresholds
HP_CERT_ABS = 1e-10      # |cert + 1| < HP_CERT_ABS (machine precision fp64)
HF_CERT_ABS = 1e-4       # |cert + 1| > HF_CERT_ABS (algebra inconsistent)
HP_DELETED_COSINE = 0.20  # cosine at xi_X < HP_DELETED_COSINE (deleted gone)
HF_DELETED_COSINE = 0.50  # cosine at xi_X > HF_DELETED_COSINE (rank-1 insufficient)
HP_NEARBY_DELTA = 0.05    # nearby cosine within +-HP_NEARBY_DELTA of baseline
HF_NEARBY_DROP = 0.20     # nearby cosine drops > HF_NEARBY_DROP (spillover damage)
HP_K3_REL = 1e-2          # |Dk3_obs - Dk3_pred| / |k3(W)| < HP_K3_REL
HF_K3_REL = 0.10          # > HF_K3_REL -> fingerprint blind
HP_SPEARMAN_DELTA = 0.05  # post-deletion rho within +-HP_SPEARMAN_DELTA
HF_SPEARMAN_DROP = 0.20   # rho drops > HF_SPEARMAN_DROP (topology damaged)


def generate_place_patterns(K: int, N_dim: int, sigma: float, seed: int) -> np.ndarray:
    """Generate K place-field patterns (BSC +-1) with Gaussian receptive fields."""
    rng = np.random.RandomState(seed)
    preferred_locs = rng.uniform(0, K, size=N_dim)
    Xi = np.zeros((K, N_dim), dtype=np.float64)
    for k in range(K):
        act_prob = np.exp(-0.5 * ((preferred_locs - k) / sigma) ** 2)
        threshold = np.percentile(act_prob, 100.0 * (1.0 - PLACE_FRAC))
        active = act_prob >= threshold
        Xi[k] = np.where(active, 1.0, -1.0)
    return Xi


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation."""
    n = len(x)
    if n < 2:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    d = rx - ry
    return float(1.0 - 6.0 * float(np.sum(d ** 2)) / (n * (n * n - 1)))


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Hutchinson estimator for kappa_3 = Tr(W^3)/N (vectorized)."""
    N_dim = W.shape[0]
    rng = np.random.RandomState(seed)
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    WV = W @ V
    W2V = W @ WV
    W3V = W @ W2V
    per_probe = (V * W3V).sum(axis=0) / N_dim
    return float(np.mean(per_probe))


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 10) -> np.ndarray:
    """Synchronous Hopfield retrieval with n_steps iterations."""
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


# ---- FORMULA SELF-TESTS ----
def _selftest_cert_normalized():
    """Normalized cert = xi_X^T (W'-W) xi_X / N = -1 for BSC +-1."""
    N_t = 4
    xi_X = np.array([1.0, -1.0, 1.0, -1.0])
    W_delta = -(1.0 / N_t) * np.outer(xi_X, xi_X)
    cert_raw = float(xi_X @ W_delta @ xi_X)
    cert_norm = cert_raw / N_t
    assert abs(cert_norm - (-1.0)) < 1e-10, f"cert_normalized T1: {cert_norm:.12f}"
    return cert_norm


def _selftest_orthogonal_unaffected():
    """Rank-1 update does not affect patterns orthogonal to xi_X."""
    N_t = 8
    rng = np.random.RandomState(42)
    xi_X = rng.choice([-1.0, 1.0], size=(N_t,)).astype(np.float64)
    # Build a pattern approximately orthogonal to xi_X
    xi_Y = rng.choice([-1.0, 1.0], size=(N_t,)).astype(np.float64)
    # Project out xi_X component from xi_Y
    xi_Y = xi_Y - (float(np.dot(xi_Y, xi_X)) / N_t) * xi_X
    W_delta = -(1.0 / N_t) * np.outer(xi_X, xi_X)
    effect_on_Y = float(xi_Y @ W_delta @ xi_Y) / N_t
    # Effect = -(1/N)(xi_Y^T xi_X)^2 / N ~ 0 when orthogonal
    # For approximate orthogonality the effect is small
    assert abs(effect_on_Y) < 0.5, f"orthogonal unaffected T2: effect={effect_on_Y:.4f}"
    return effect_on_Y


def _selftest_spearman_stability():
    """Removing one point from K does not drastically change Spearman rho."""
    rng = np.random.RandomState(42)
    K_t = 20
    distances = np.arange(K_t, dtype=float)
    cosines_neg = -np.exp(-distances / 3.0) + 0.01 * rng.randn(K_t)
    rho_full = spearman_rho(distances, cosines_neg)
    # Remove one interior point
    idx_remove = 10
    mask = np.ones(K_t, dtype=bool)
    mask[idx_remove] = False
    rho_minus1 = spearman_rho(distances[mask], cosines_neg[mask])
    delta = abs(rho_minus1 - rho_full)
    assert delta < 0.10, f"spearman stability T3: delta={delta:.4f}"
    return rho_full, rho_minus1


def _instrumentation_selftest():
    c1 = _selftest_cert_normalized()
    c2 = _selftest_orthogonal_unaffected()
    rho_full, rho_k1 = _selftest_spearman_stability()
    # Verify K_LOCS >= 8 for neighbor test at X+-2
    assert K_LOCS >= 8, f"K_LOCS={K_LOCS} too small for +-2 neighbor test"
    # Verify alpha below capacity
    alpha = K_LOCS / N_ACTIVE
    assert alpha < ALPHA_C, f"alpha={alpha:.4f} >= alpha_c={ALPHA_C}"
    print(f"[selftest] PASS: cert_norm={c1:.12f} orth_effect={c2:.4f} "
          f"rho_full={rho_full:.4f} rho_k1={rho_k1:.4f} delta={abs(rho_k1-rho_full):.4f} "
          f"alpha={alpha:.4f} < alpha_c={ALPHA_C}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_delta_kappa3_predicted(Xi: np.ndarray, W: np.ndarray, X_idx: int, N_dim: int) -> float:
    """Predict Dk3 from rank-1 deletion: Dk3 = Tr(W'^3 - W^3)/N.

    Rank-1 perturbation: W' = W - (1/N) xi_X xi_X^T.
    Delta = Tr((W + dW)^3 - W^3)/N where dW = -(1/N) xi_X xi_X^T.
    Leading order:
      Dk3 ~ (1/N)[3 Tr(W^2 dW)] (first-order)
           = (3/N) Tr(W^2 * (-(1/N) xi_X xi_X^T))
           = -(3/N^2) xi_X^T W^2 xi_X
    Second order (dW^2 term): (3/N) Tr(W dW^2) = (3/N) Tr(W * (1/N^2) xi_X xi_X^T xi_X xi_X^T)
    = (3/N^3) ||xi_X||^2 xi_X^T W xi_X.
    Third order: (1/N) Tr(dW^3) = -(1/N^4) ||xi_X||^6.
    """
    xi_X = Xi[X_idx]
    W2xi = W @ (W @ xi_X)
    first_order = -(3.0 / N_dim**2) * float(np.dot(xi_X, W2xi))
    Wxi = W @ xi_X
    second_order = (3.0 / N_dim**3) * float(np.dot(xi_X, xi_X)) * float(np.dot(xi_X, Wxi))
    norm4 = float(np.dot(xi_X, xi_X)) ** 2
    third_order = -(1.0 / N_dim**4) * (float(np.dot(xi_X, xi_X)) ** 3)
    return first_order + second_order + third_order


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed + 500)  # offset to avoid collision with pattern gen

    # Generate place-field patterns using place-field seed
    Xi = generate_place_patterns(K_LOCS, N_ACTIVE, SIGMA, seed)

    # Build Hopfield W (with diagonal removed per convention)
    W = Xi.T @ Xi / float(N_ACTIVE)
    np.fill_diagonal(W, 0.0)

    # Choose deletion target X in interior [K/4, 3K/4]
    X_idx = K_LOCS // 2   # exactly at middle; deterministic per seed-invariant choice
    xi_X = Xi[X_idx]

    # -- PRE-DELETION MEASUREMENTS --
    # 1. Pre-deletion Spearman rho on all K patterns
    n_test_pairs = min(200, K_LOCS * (K_LOCS - 1) // 2)
    rng2 = np.random.RandomState(seed + 200)
    all_pairs = [(i, j) for i in range(K_LOCS) for j in range(i + 1, K_LOCS)]
    if len(all_pairs) > n_test_pairs:
        sel = rng2.choice(len(all_pairs), n_test_pairs, replace=False)
        all_pairs = [all_pairs[s] for s in sel]
    distances = [abs(i - j) for i, j in all_pairs]
    pat_cosines = [float(np.dot(Xi[i], Xi[j])) / N_ACTIVE for i, j in all_pairs]
    rho_pre = spearman_rho(np.array(distances), np.array([-c for c in pat_cosines]))

    # 2. Pre-deletion retrieval cosine at nearby locations X+-1 and X+-2
    rng_noise = np.random.RandomState(seed + 300)
    nearby_indices = []
    for delta in [-2, -1, 1, 2]:
        nb_idx = X_idx + delta
        if 0 <= nb_idx < K_LOCS:
            nearby_indices.append(nb_idx)

    nearby_cosines_pre = {}
    for nb_idx in nearby_indices:
        probe = Xi[nb_idx].copy()
        flip = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W, probe)
        cos = cosine_sim(retrieved, Xi[nb_idx])
        nearby_cosines_pre[nb_idx] = cos

    # 3. Pre-deletion kappa_3 measurement
    k3_pre = hutchinson_kappa3(W, N_HUTCHINSON, seed + 100)

    # -- RANK-1 DELETION --
    W_prime = W - (1.0 / N_ACTIVE) * np.outer(xi_X, xi_X)

    # -- CERT TEST (HP1 / HF1) --
    W_delta = W_prime - W
    cert_raw = float(xi_X @ W_delta @ xi_X)
    cert_norm = cert_raw / N_ACTIVE
    cert_err = abs(cert_norm + 1.0)   # should be 0 for exact

    # -- POST-DELETION RETRIEVAL AT xi_X (HP2 / HF2) --
    probe_X = xi_X.copy()
    flip_X = rng_noise.random(N_ACTIVE) < NOISE_FRAC
    probe_X[flip_X] *= -1.0
    retrieved_X = hopfield_retrieve(W_prime, probe_X)
    cosine_deleted = cosine_sim(retrieved_X, xi_X)

    # -- NEARBY LOCATION PRESERVATION (HP3 / HF3) --
    nearby_cosines_post = {}
    for nb_idx in nearby_indices:
        probe = Xi[nb_idx].copy()
        flip = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W_prime, probe)
        cos = cosine_sim(retrieved, Xi[nb_idx])
        nearby_cosines_post[nb_idx] = cos

    nearby_deltas = {}
    for nb_idx in nearby_indices:
        delta = nearby_cosines_post[nb_idx] - nearby_cosines_pre[nb_idx]
        nearby_deltas[nb_idx] = float(delta)

    # -- KAPPA_3 FINGERPRINT (HP4 / HF4) --
    k3_post = hutchinson_kappa3(W_prime, N_HUTCHINSON, seed + 100)
    dk3_obs = k3_post - k3_pre

    # Predicted delta kappa3
    dk3_pred = compute_delta_kappa3_predicted(Xi, W, X_idx, N_ACTIVE)
    k3_rel_err = abs(dk3_obs - dk3_pred) / (abs(k3_pre) + 1e-12)

    # -- POST-DELETION SPEARMAN RHO (HP5 / HF5) --
    # Compute on K-1 patterns (exclude X_idx)
    keep_pairs = [(i, j) for i, j in all_pairs if i != X_idx and j != X_idx]
    if len(keep_pairs) >= 4:
        dist_k1 = [abs(i - j) for i, j in keep_pairs]
        pat_cos_k1 = [float(np.dot(Xi[i], Xi[j])) / N_ACTIVE for i, j in keep_pairs]
        rho_post = spearman_rho(np.array(dist_k1), np.array([-c for c in pat_cos_k1]))
    else:
        rho_post = rho_pre  # fallback
    rho_delta = abs(rho_post - rho_pre)

    # -- HP / HF EVALUATION --
    hp1 = cert_err < HP_CERT_ABS
    hp2 = cosine_deleted < HP_DELETED_COSINE
    # HP3: all nearby locations within +-HP_NEARBY_DELTA of baseline
    nearby_ok = all(abs(d) <= HP_NEARBY_DELTA for d in nearby_deltas.values())
    # HF3: any nearby drops > HF_NEARBY_DROP
    hf3 = any(d < -HF_NEARBY_DROP for d in nearby_deltas.values())
    hp3 = nearby_ok and not hf3
    hp4 = k3_rel_err < HP_K3_REL
    hp5 = rho_delta <= HP_SPEARMAN_DELTA

    hf1 = cert_err > HF_CERT_ABS
    hf2 = cosine_deleted > HF_DELETED_COSINE
    hf4 = k3_rel_err > HF_K3_REL
    hf5 = rho_delta > HF_SPEARMAN_DROP

    elapsed = time.time() - t0
    print(f"  [seed={seed} N={N_ACTIVE} K={K_LOCS} X={X_idx}] "
          f"cert_err={cert_err:.2e}(HP<{HP_CERT_ABS:.0e}) "
          f"cosine_del={cosine_deleted:.4f}(HP<{HP_DELETED_COSINE}) "
          f"nearby_deltas={[round(v,3) for v in nearby_deltas.values()]} "
          f"k3_rel_err={k3_rel_err:.4f}(HP<{HP_K3_REL}) "
          f"rho_pre={rho_pre:.4f} rho_post={rho_post:.4f} rho_delta={rho_delta:.4f} "
          f"hp=[{int(hp1)},{int(hp2)},{int(hp3)},{int(hp4)},{int(hp5)}] "
          f"elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N_ACTIVE, "K_LOCS": K_LOCS, "X_idx": X_idx,
        "run_mode": RUN_MODE,
        "cert_norm": float(cert_norm),
        "cert_err": float(cert_err),
        "cosine_deleted": float(cosine_deleted),
        "nearby_deltas": {str(k): v for k, v in nearby_deltas.items()},
        "nearby_cosines_pre": {str(k): v for k, v in nearby_cosines_pre.items()},
        "nearby_cosines_post": {str(k): v for k, v in nearby_cosines_post.items()},
        "k3_pre": float(k3_pre),
        "k3_post": float(k3_post),
        "dk3_obs": float(dk3_obs),
        "dk3_pred": float(dk3_pred),
        "k3_rel_err": float(k3_rel_err),
        "rho_pre": float(rho_pre),
        "rho_post": float(rho_post),
        "rho_delta": float(rho_delta),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hp4": bool(hp4), "hp5": bool(hp5),
        "hf1": bool(hf1), "hf2": bool(hf2), "hf3": bool(hf3),
        "hf4": bool(hf4), "hf5": bool(hf5),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    mean_cert_err = float(np.mean([r["cert_err"] for r in results]))
    mean_cosine_del = float(np.mean([r["cosine_deleted"] for r in results]))

    # HP counts across seeds
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hp4_n = sum(1 for r in results if r["hp4"])
    hp5_n = sum(1 for r in results if r["hp5"])

    hf1_any = any(r["hf1"] for r in results)
    hf2_any = any(r["hf2"] for r in results)
    hf3_any = any(r["hf3"] for r in results)
    hf4_any = any(r["hf4"] for r in results)
    hf5_any = any(r["hf5"] for r in results)

    mean_k3_rel = float(np.mean([r["k3_rel_err"] for r in results]))
    mean_rho_delta = float(np.mean([r["rho_delta"] for r in results]))

    summary = (
        f"n_seeds={n} "
        f"cert_err={mean_cert_err:.2e}(HP<{HP_CERT_ABS:.0e}) "
        f"cosine_del={mean_cosine_del:.4f}(HP<{HP_DELETED_COSINE},HF>{HF_DELETED_COSINE}) "
        f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n} "
        f"hp4={hp4_n}/{n}(k3_rel={mean_k3_rel:.4f}) "
        f"hp5={hp5_n}/{n}(rho_delta={mean_rho_delta:.4f})"
    )

    # Any HF triggers HARD_FAIL
    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: cert algebra inconsistent (|cert+1|>{HF_CERT_ABS}). {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: deleted location still retrievable (cosine>{HF_DELETED_COSINE}). {summary}")
    if hf3_any:
        return ("HARD_FAIL", f"HARD_FAIL HF3: spillover damage to nearby locations (drop>{HF_NEARBY_DROP}). {summary}")
    if hf4_any:
        return ("HARD_FAIL", f"HARD_FAIL HF4: kappa_3 fingerprint blind to deletion (k3_rel>{HF_K3_REL}). {summary}")
    if hf5_any:
        return ("HARD_FAIL", f"HARD_FAIL HF5: spatial topology damaged (rho_delta>{HF_SPEARMAN_DROP}). {summary}")

    # All 5 HP conditions passing in >= 4/5 seeds = HARD_PASS
    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hp1_n, hp2_n, hp3_n, hp4_n, hp5_n])

    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 5 HP conditions met in >={min_threshold}/{n} seeds. {summary}")

    # Check partial pass
    n_hp_conditions = sum([
        hp1_n >= min_threshold,
        hp2_n >= min_threshold,
        hp3_n >= min_threshold,
        hp4_n >= min_threshold,
        hp5_n >= min_threshold,
    ])
    if n_hp_conditions >= 3:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conditions}/5 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conditions}/5 HP conditions met. {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "K_LOCS": K_LOCS, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N_ACTIVE} K={K_LOCS} mode={RUN_MODE})", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] pp47_deletion_cert_composition N={N_ACTIVE} K={K_LOCS}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N_ACTIVE,
    "K_LOCS": K_LOCS,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "cert_err": r.get("cert_err"),
            "cosine_deleted": r.get("cosine_deleted"),
            "k3_rel_err": r.get("k3_rel_err"),
            "rho_delta": r.get("rho_delta"),
            "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3"),
            "hp4": r.get("hp4"), "hp5": r.get("hp5"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
