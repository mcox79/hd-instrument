"""Shared core for substrate_seqbind_cleanup_family_phase_diagram_v1 siblings.

FOURTH COMPONENT-SUBSTITUTION phase diagram (after encoder-family for PC +
encoder-family for sequence-binding + cleanup-family for PC). USER directive
2026-06-28 (Research): systematic phase-diagram coverage across COMPONENTS.

PC cleanup-family (sister cell) landed FULL 3-seed MIDDLE_BAND convergent --
substrate handles cleanup family-invariant at PC scale. Different primitive
may show different cleanup family dependencies. Target primitive here:
SEQUENCE BINDING K-cliff (chain-grade via K_cliff per Kanerva theory).

Cleanup families (OUTER axis) -- substituted at READOUT after unbind:
    modern_hopfield      : Q_t+1 = sign(softmax(beta * Q_t @ X.T) @ X)
    classical_hopfield   : Q_t+1 = sign(Q_t @ W) where W = X.T @ X / M (Hebbian)
    iterative_cosine     : Q_t+1 = X[argmax(Q_t @ X.T)] (SEQBIND v2 DEFAULT;
                                                          POSITIVE CONTROL)
    soft_energy_attractor: Q_t+1 = sign(Q_t + alpha*(softmax(...) @ X - Q_t))

Cleanup mechanism FIXED at READOUT step (after unbind, before top1 readout).
The unbind itself stays FFT-circular-convolution + complex-conjugate
(seqbind v2 mechanism). Only the codeword-snap step varies.

Inner axes: K (3) x N (3) at Q_noise=2.
4 cleanups x 3 K x 3 N = 36 phase points per seed FULL.
4 cleanups x 1 K x 2 N = 8 corner points per seed SMOKE.

ENCODER FIXED: bipolar codebook (seqbind v2 default; non-L2-normalized).
Q_noise FIXED: 2 (effective tag_density = 0.2; mid-load).
N_QUERIES: 100 full, 4 smoke.

PRE-REG: preregs/2026-06-28_substrate_seqbind_cleanup_family_phase_diagram_v1.md

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    CLEANUP_FAMILIES,
    K_SWEEP_FULL, N_SWEEP_FULL, K_SWEEP_SMOKE, N_SWEEP_SMOKE,
    Q_LEVEL, N_QUERIES_FULL, N_QUERIES_SMOKE,
    EXPECTED_N_UNITS_FULL, EXPECTED_N_UNITS_SMOKE

ASCII-only. No unicode. CPU-natural (numpy primary; seqbind v2 idiom).

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import torch
    _TORCH_OK = True
    _CUDA_OK = bool(torch.cuda.is_available())
except Exception:
    _TORCH_OK = False
    _CUDA_OK = False

ANCHOR_PREFIX = "substrate_seqbind_cleanup_family_phase_diagram_v1"

# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
# Cleanup families (OUTER axis)
CLEANUP_FAMILIES = ("modern_hopfield", "classical_hopfield",
                    "iterative_cosine", "soft_energy_attractor")

# Sweep axes (inner)
K_SWEEP_FULL = [20, 100, 500]
N_SWEEP_FULL = [1024, 4096, 8192]
K_SWEEP_SMOKE = [20]
N_SWEEP_SMOKE = [4096, 8192]

# Fixed: noise multiplier (Q=2 -> tag_density 0.2; mid-load)
Q_LEVEL = 2
BASE_TAG_DENSITY = 0.1  # Q=1 -> 0.1 effective

# Per-point query count
N_QUERIES_FULL = 100
N_QUERIES_SMOKE = 4

# Codebook sizes (must be >= max K)
V_ITEMS = 1000
V_POS = 1000

# Cleanup mechanism hyperparameters
BETA = 8.0
ALPHA_SOFT = 0.5
CLEANUP_ITERS = 1  # T=1 (mirrors seqbind v2 idiom; cleanup family is the
                   # discriminator, iters are NOT swept here)

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(CLEANUP_FAMILIES) * len(K_SWEEP_FULL)
                         * len(N_SWEEP_FULL))  # 36
EXPECTED_N_UNITS_SMOKE = (len(CLEANUP_FAMILIES) * len(K_SWEEP_SMOKE)
                          * len(N_SWEEP_SMOKE))  # 8

# Pre-reg bands (per-point; LOCKED)
BAND_SAT = 0.90
BAND_MB_LO = 0.30
BAND_MB_HI = 0.70
BAND_FLOOR = 0.10
HP_DISCRIMINATOR = 0.30  # arms_diff (mechanism - max(R,S)) >= 0.30 for HP
MB_DISCRIMINATOR = 0.15  # >= 0.15 for MB

# Positive control: iterative_cosine (seqbind v2 default) at K=20, N=8192, Q=2
# should reproduce seqbind v2 chain-grade evidence (top1 >= 0.50). Smoke variant
# uses same point at N=8192 too (which IS in smoke).
POSITIVE_CONTROL = {
    "cleanup_family": "iterative_cosine",
    "K": 20,
    "N": 8192,
    "Q_level": Q_LEVEL,
    "top1_floor": 0.50,
}
POSITIVE_CONTROL_SMOKE = {
    "cleanup_family": "iterative_cosine",
    "K": 20,
    "N": 8192,
    "Q_level": Q_LEVEL,
    "top1_floor": 0.40,  # 4 queries; coarser
}

# Cell-level verdict thresholds (FULL)
HP_MIN_DISCRIMINATING = 12  # >= 12 of 36 in HARD_PASS+MIDDLE_BAND
HP_ARMS_DIFF_MIN = 0.15  # avg(SUBSTRATE - max(R,S)) >= 0.15
MB_MIN_DISCRIMINATING = 6

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Backend label
# ---------------------------------------------------------------------------
def get_backend_label() -> str:
    if _CUDA_OK:
        return "torch.cuda"
    if _TORCH_OK:
        return "torch.cpu"
    return "numpy.cpu"


# ---------------------------------------------------------------------------
# Theoretical K-cliff prediction (Kanerva matched-filter for K-bound bundle)
# ---------------------------------------------------------------------------
def kanerva_K_cliff_prediction(N: int, V_items: int = V_ITEMS,
                                noise_scale: float = 0.2) -> float:
    """Approximate K at which SUBSTRATE_top1 drops below SAT band (0.90).

    For random bipolar bundle of K bound (pos, item) pairs, unbind produces
    signal ~ 1 codeword + noise of std ~ sqrt(K-1)/sqrt(N). The argmax-cleanup
    succeeds when signal_mag > sqrt(2 log V_items) * noise_std. Crude:

        K_cliff_approx ~ N / (2 * log(V_items))
    """
    if N <= 0 or V_items <= 1:
        return 0.0
    return N / (2.0 * math.log(V_items))


# ---------------------------------------------------------------------------
# HRR primitives (numpy; seqbind v2 idiom)
# ---------------------------------------------------------------------------
def _bipolar_codebook(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar +/-1 codebook (V, N) float32. NO L2 normalization (Plate HRR)."""
    return (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)


def _bind_bundle(positions: np.ndarray, items: np.ndarray,
                  tag_noise: np.ndarray) -> np.ndarray:
    """Bind K (pos, item) pairs + sum-bundle. Returns (N,) normalized bundle."""
    items_noisy = items + tag_noise
    items_noisy = items_noisy / (np.linalg.norm(items_noisy, axis=-1,
                                                 keepdims=True) + 1e-8)
    P = np.fft.rfft(positions, axis=-1)
    I = np.fft.rfft(items_noisy, axis=-1)
    PROD = P * I
    bound = np.fft.irfft(PROD, n=positions.shape[-1], axis=-1).astype(np.float32)
    bundle = bound.sum(axis=0)
    n = np.linalg.norm(bundle) + 1e-8
    return bundle / n


def _unbind_batch(c: np.ndarray, queries: np.ndarray) -> np.ndarray:
    """Batched unbind: unbind each query vector from bundle c.
    c: (N,) float32; queries: (Q, N); returns (Q, N)."""
    C = np.fft.rfft(c)
    A = np.fft.rfft(queries, axis=-1)
    R = C[np.newaxis, :] * np.conj(A)
    return np.fft.irfft(R, n=c.shape[-1], axis=-1).astype(np.float32)


# ---------------------------------------------------------------------------
# Cleanup families -- run on the UNBIND OUTPUT (Q, N) against items_book
# Returns: top1 predictions (Q,) int, cleaned vectors (Q, N) for hash
# ---------------------------------------------------------------------------
def _sign_op(V: np.ndarray) -> np.ndarray:
    out = np.sign(V).astype(np.float32)
    out[out == 0.0] = 1.0
    return out


def _modern_hopfield_cleanup(unbind_out: np.ndarray, items_book: np.ndarray,
                              T: int, beta: float
                              ) -> Tuple[np.ndarray, np.ndarray]:
    """T-step modern Hopfield: Q_t+1 = sign(softmax(beta * Q_t @ X.T) @ X).

    Returns:
        top1_idx: (Q,) argmax codeword index of FINAL cleaned vector vs items
        cleaned:  (Q, N) final cleaned bipolar vector
    """
    Q = unbind_out.copy()
    for _ in range(max(0, T)):
        sims = Q @ items_book.T  # (Q, V_ITEMS)
        # Softmax in numpy
        sims_shift = sims - sims.max(axis=1, keepdims=True)
        exp_s = np.exp(beta * sims_shift)
        p = exp_s / (exp_s.sum(axis=1, keepdims=True) + 1e-12)
        Q_new = p @ items_book  # (Q, N) mixture
        Q = _sign_op(Q_new)
    # Final readout
    final_sims = Q @ items_book.T
    top1_idx = final_sims.argmax(axis=1)
    return top1_idx, Q


def _classical_hopfield_cleanup(unbind_out: np.ndarray, items_book: np.ndarray,
                                 T: int, beta: float
                                 ) -> Tuple[np.ndarray, np.ndarray]:
    """T-step classical Hopfield: Q_t+1 = sign(Q_t @ W) where W = X.T @ X / M."""
    V_it, N = items_book.shape
    W = (items_book.T @ items_book) / float(V_it)  # (N, N)
    np.fill_diagonal(W, 0.0)
    Q = unbind_out.copy()
    for _ in range(max(0, T)):
        h = Q @ W  # (Q, N)
        Q = _sign_op(h)
    final_sims = Q @ items_book.T
    top1_idx = final_sims.argmax(axis=1)
    return top1_idx, Q


def _iterative_cosine_cleanup(unbind_out: np.ndarray, items_book: np.ndarray,
                               T: int, beta: float
                               ) -> Tuple[np.ndarray, np.ndarray]:
    """T-step iterative cosine snap: Q_t+1 = X[argmax(Q_t @ X.T)].

    For sequence-binding readout, this is the SEQBIND v2 default (POSITIVE
    CONTROL). At T=1, top1_idx is the direct argmax of the unbind output --
    identical to seqbind v2 readout.
    """
    Q = unbind_out.copy()
    last_idx = None
    for _ in range(max(0, T)):
        sims = Q @ items_book.T
        idx = sims.argmax(axis=1)
        Q = items_book[idx]
        last_idx = idx
    if last_idx is None:
        # T == 0 fallback: direct argmax on unbind_out
        sims = Q @ items_book.T
        last_idx = sims.argmax(axis=1)
    return last_idx, Q


def _soft_energy_attractor_cleanup(unbind_out: np.ndarray, items_book: np.ndarray,
                                    T: int, beta: float
                                    ) -> Tuple[np.ndarray, np.ndarray]:
    """T-step soft-energy gradient: damped move toward modern_hopfield target."""
    Q = unbind_out.copy()
    alpha = ALPHA_SOFT
    for _ in range(max(0, T)):
        sims = Q @ items_book.T
        sims_shift = sims - sims.max(axis=1, keepdims=True)
        exp_s = np.exp(beta * sims_shift)
        p = exp_s / (exp_s.sum(axis=1, keepdims=True) + 1e-12)
        target = p @ items_book  # (Q, N) modern-Hopfield target
        Q_new = Q + alpha * (target - Q)
        Q = _sign_op(Q_new)
    final_sims = Q @ items_book.T
    top1_idx = final_sims.argmax(axis=1)
    return top1_idx, Q


_CLEANUP_REGISTRY = {
    "modern_hopfield": _modern_hopfield_cleanup,
    "classical_hopfield": _classical_hopfield_cleanup,
    "iterative_cosine": _iterative_cosine_cleanup,
    "soft_energy_attractor": _soft_energy_attractor_cleanup,
}


# ---------------------------------------------------------------------------
# Per-phase-point evaluation
# ---------------------------------------------------------------------------
def _eval_phase_point(g: np.random.Generator, cleanup_family: str,
                       K: int, N: int, Q_level: int, n_queries: int,
                       point_seed: int) -> Dict[str, Any]:
    """Run one (cleanup, K, N) point with 3 arms (SUBSTRATE / RANDOM / SHUFFLE).

    Cleanup family is substituted at the READOUT step (after unbind).
    """
    if cleanup_family not in _CLEANUP_REGISTRY:
        raise ValueError(f"unknown cleanup_family={cleanup_family!r}")
    cleanup_fn = _CLEANUP_REGISTRY[cleanup_family]

    t0 = time.time()
    noise_scale = float(BASE_TAG_DENSITY * Q_level)

    # Codebooks (rebuilt per point since N varies; same g state => same when
    # point_seed repeats for different cleanups, ensuring apples-to-apples)
    pt_g = np.random.default_rng(point_seed)
    positions_book = _bipolar_codebook(V_POS, N, pt_g)
    items_book = _bipolar_codebook(V_ITEMS, N, pt_g)

    pos_idx = pt_g.choice(V_POS, size=K, replace=False)
    item_idx = pt_g.choice(V_ITEMS, size=K, replace=False)
    positions = positions_book[pos_idx]
    items = items_book[item_idx]

    tag_noise = pt_g.standard_normal((K, N)).astype(np.float32) * noise_scale

    S_substrate = _bind_bundle(positions, items, tag_noise)

    # Pick query positions (subset of K)
    if n_queries > K:
        q_local = pt_g.choice(K, size=n_queries, replace=True)
    else:
        q_local = pt_g.choice(K, size=n_queries, replace=False)
    q_pos_idx = pos_idx[q_local]
    q_true_item_idx = item_idx[q_local]
    q_positions = positions_book[q_pos_idx]

    # ARM_SUBSTRATE: unbind correct query, cleanup, score
    unbind_sub = _unbind_batch(S_substrate, q_positions)
    sub_pred, sub_cleaned = cleanup_fn(unbind_sub, items_book, CLEANUP_ITERS, BETA)
    sub_recall = float(np.mean(sub_pred == q_true_item_idx))

    # ARM_RANDOM: random unit vector through SAME cleanup pipeline
    rand_unbind = pt_g.standard_normal((n_queries, N)).astype(np.float32)
    rand_unbind = rand_unbind / (np.linalg.norm(rand_unbind, axis=-1,
                                                  keepdims=True) + 1e-8)
    rand_pred, rand_cleaned = cleanup_fn(rand_unbind, items_book, CLEANUP_ITERS,
                                          BETA)
    rand_recall = float(np.mean(rand_pred == q_true_item_idx))

    # ARM_SHUFFLE: unbind WRONG (shuffled) query positions from same bundle S
    shuffled_local = pt_g.permutation(K)[:n_queries] if n_queries <= K \
        else pt_g.choice(K, size=n_queries, replace=True)
    n_fix = 0
    while np.any(shuffled_local == q_local) and n_fix < 50:
        m = shuffled_local == q_local
        shuffled_local[m] = pt_g.choice(K, size=int(m.sum()), replace=True)
        n_fix += 1
    shuf_pos_idx = pos_idx[shuffled_local]
    shuf_positions = positions_book[shuf_pos_idx]
    unbind_shuf = _unbind_batch(S_substrate, shuf_positions)
    shuf_pred, shuf_cleaned = cleanup_fn(unbind_shuf, items_book, CLEANUP_ITERS,
                                          BETA)
    shuf_recall = float(np.mean(shuf_pred == q_true_item_idx))

    # Output bytes hash for cleanup-distinctness check
    mech_output_hash = hashlib.sha256(
        sub_cleaned.astype(np.float32).tobytes()).hexdigest()[:16]
    rnd_output_hash = hashlib.sha256(
        rand_cleaned.astype(np.float32).tobytes()).hexdigest()[:16]

    floor = max(rand_recall, shuf_recall)
    discriminator = sub_recall - floor

    if sub_recall >= BAND_SAT:
        tier = "SATURATED"
    elif (BAND_MB_LO <= sub_recall <= BAND_MB_HI
            and discriminator >= MB_DISCRIMINATOR):
        tier = "MIDDLE_BAND"
    elif sub_recall <= BAND_FLOOR:
        tier = "FLOOR"
    elif sub_recall > BAND_MB_HI and discriminator >= HP_DISCRIMINATOR:
        tier = "HARD_PASS"
    else:
        tier = "TRANSITION"

    return {
        "cleanup_family": cleanup_family,
        "K": int(K),
        "N": int(N),
        "Q_level": int(Q_level),
        "tag_density_effective": noise_scale,
        "n_queries": int(n_queries),
        "SUBSTRATE_top1_recall": sub_recall,
        "RANDOM_top1_recall": rand_recall,
        "SHUFFLE_top1_recall": shuf_recall,
        "arms_diff": discriminator,
        "band": tier,
        "mech_output_hash": mech_output_hash,
        "rnd_output_hash": rnd_output_hash,
        "kanerva_K_cliff_pred": round(kanerva_K_cliff_prediction(N), 1),
        "elapsed_per_point_s": round(time.time() - t0, 3),
    }


# ---------------------------------------------------------------------------
# Selftest (cleanup mechanism sanity + cardinality + CRLB)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Cleanup mechanism sanity + cardinality + distinctness check.

    For each cleanup family at N=512, V_items=20, query a clean codeword:
      - At input == codeword: top1 == that codeword (identity)
      - At input ~ codeword + low_noise: top1 == that codeword (recovery)

    Then verify 4 cleanups produce DISTINCT output byte hashes at a
    contested input (K-cliff regime simulated by a sum of 3 codewords).
    """
    msgs: List[str] = []
    try:
        # 1. Cardinality math
        if EXPECTED_N_UNITS_FULL != 36:
            return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 36"
        if EXPECTED_N_UNITS_SMOKE != 8:
            return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 8"
        msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
                    f"SMOKE={EXPECTED_N_UNITS_SMOKE}")

        # 2. Kanerva K-cliff formula sanity
        kc_1024 = kanerva_K_cliff_prediction(1024)
        kc_8192 = kanerva_K_cliff_prediction(8192)
        if not (kc_8192 > kc_1024):
            return False, (f"K-cliff should grow with N: "
                           f"N=1024->{kc_1024:.1f} N=8192->{kc_8192:.1f}")
        msgs.append(f"K-cliff pred N=1024 ~ {kc_1024:.1f}; "
                    f"N=8192 ~ {kc_8192:.1f}")

        # 3. Per-cleanup mechanism sanity at N=512, V_items=20
        N_san = 512
        V_san = 20
        g = np.random.default_rng(seed)
        items_san = _bipolar_codebook(V_san, N_san, g)
        # Identity test: feed exact codeword 0, top1 must be 0
        for fam in CLEANUP_FAMILIES:
            cleanup_fn = _CLEANUP_REGISTRY[fam]
            inp = items_san[0:1].copy()  # (1, N) -- exact codeword
            pred, _ = cleanup_fn(inp, items_san, 1, BETA)
            if int(pred[0]) != 0:
                return False, (f"identity FAIL {fam}: clean codeword 0 -> "
                                f"pred {pred[0]}")
            # Noisy recovery test: codeword 0 + small gaussian noise
            noise = g.standard_normal((1, N_san)).astype(np.float32) * 0.3
            inp_noisy = items_san[0:1] + noise
            pred2, _ = cleanup_fn(inp_noisy, items_san, 1, BETA)
            if int(pred2[0]) != 0:
                return False, (f"recovery FAIL {fam}: noisy codeword 0 -> "
                                f"pred {pred2[0]}")
            msgs.append(f"sanity {fam} OK")

        # 4. Cleanup distinctness at a CONTESTED input where softmax-mix
        # diverges from argmax-snap. At beta=8 and well-separated argmax,
        # modern_hopfield collapses to iterative_cosine (softmax ~= one-hot).
        # To force divergence: use SMALL beta so softmax stays soft, AND make
        # similarities genuinely close (top-2 within 1/N of each other).
        # Strategy: feed a vector that is exactly halfway between two
        # codewords (X[0] + X[1])/2 + small noise. Then:
        #   - argmax breaks tie by float order -> iterative_cosine picks one
        #   - softmax with small beta mixes both -> modern_hopfield differs
        #   - classical_hopfield uses Hebbian weight -> different
        #   - soft_energy is alpha*modern + (1-alpha)*input -> different
        # Use beta_test=1.0 (smaller than BETA=8) so softmax mixes here only.
        N_diff = 1024
        V_diff = 50
        g2 = np.random.default_rng(seed + 31)
        items_diff = _bipolar_codebook(V_diff, N_diff, g2)
        # halfway between codeword 0 and 1
        mix = 0.5 * items_diff[0] + 0.5 * items_diff[1]
        mix = mix.reshape(1, -1)
        # Use small beta so softmax mixes meaningfully (not collapse to argmax)
        beta_test = 1.0
        hashes = {}
        for fam in CLEANUP_FAMILIES:
            cleanup_fn = _CLEANUP_REGISTRY[fam]
            _, cleaned = cleanup_fn(mix, items_diff, 1, beta_test)
            h = hashlib.sha256(cleaned.astype(np.float32).tobytes()
                                ).hexdigest()[:16]
            hashes[fam] = h
        if len(set(hashes.values())) != len(CLEANUP_FAMILIES):
            return False, (f"cleanup outputs NOT distinct at contested input: "
                            f"{hashes}; some cleanups identical at "
                            f"beta_test={beta_test}")
        msgs.append(f"cleanup distinctness OK at beta_test={beta_test}: "
                    f"{hashes}")

        return True, "; ".join(msgs)
    except Exception as e:
        return False, (f"selftest EXC: {type(e).__name__}: {e}\n"
                        f"{traceback.format_exc()}")


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str,
                                smoke_corners: bool = False) -> Dict[str, Any]:
    """Run all (cleanup, K, N) phase points for one seed."""
    is_smoke = (run_mode == "smoke" or smoke_corners)
    if run_mode == "selftest":
        # selftest just returns 2 cleanup points to give the harness something
        K_sweep = [20]
        N_sweep = [4096]
        n_queries = 4
        fams = ("iterative_cosine", "modern_hopfield")
    elif is_smoke:
        K_sweep = K_SWEEP_SMOKE
        N_sweep = N_SWEEP_SMOKE
        n_queries = N_QUERIES_SMOKE
        fams = CLEANUP_FAMILIES
    else:
        K_sweep = K_SWEEP_FULL
        N_sweep = N_SWEEP_FULL
        n_queries = N_QUERIES_FULL
        fams = CLEANUP_FAMILIES

    expected_n = len(fams) * len(K_sweep) * len(N_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} "
          f"cleanups={fams} K={K_sweep} N={N_sweep} Q={Q_LEVEL} "
          f"queries={n_queries} expected_n={expected_n}", flush=True)

    crlb_preds = {f"N{N}": round(kanerva_K_cliff_prediction(N), 1)
                  for N in N_sweep}
    print(f"[kanerva-K-cliff] {crlb_preds}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for fam in fams:
        for N in N_sweep:
            for K in K_sweep:
                # Per-point seed = stable across cleanup arms (same data per
                # (K, N) regardless of cleanup), so apples-to-apples
                point_seed = seed * 100000 + N * 10 + K
                print(f"[point] seed={seed} cleanup={fam} K={K} N={N} ...",
                      flush=True)
                pt = _eval_phase_point(np.random.default_rng(point_seed), fam,
                                        K, N, Q_LEVEL, n_queries, point_seed)
                phase_map.append(pt)
                print(f"  -> sub={pt['SUBSTRATE_top1_recall']:.3f} "
                      f"rnd={pt['RANDOM_top1_recall']:.3f} "
                      f"shuf={pt['SHUFFLE_top1_recall']:.3f} "
                      f"diff={pt['arms_diff']:.3f} band={pt['band']} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - started
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # Per-cleanup hashes (META_RULE_AF: 4 cleanups must produce distinct
    # mechanism hashes at the cell-level)
    cleanup_mech_hashes: Dict[str, str] = {}
    arms_differ_per_cl: Dict[str, Dict[str, Any]] = {}
    for fam in fams:
        fam_pts = [p for p in phase_map if p["cleanup_family"] == fam]
        if not fam_pts:
            continue
        sub_payload = json.dumps([p["mech_output_hash"] for p in fam_pts],
                                 sort_keys=True).encode("utf-8")
        rnd_payload = json.dumps([p["rnd_output_hash"] for p in fam_pts],
                                 sort_keys=True).encode("utf-8")
        sub_h = hashlib.sha256(sub_payload).hexdigest()
        rnd_h = hashlib.sha256(rnd_payload).hexdigest()
        cleanup_mech_hashes[fam] = sub_h
        arms_differ_per_cl[fam] = {
            "mechanism_hash": sub_h,
            "random_hash": rnd_h,
            "differ": sub_h != rnd_h,
        }

    # Pairwise distinctness
    pairs_differ = {}
    fams_list = list(fams)
    for i in range(len(fams_list)):
        for j in range(i + 1, len(fams_list)):
            k = f"{fams_list[i]}_vs_{fams_list[j]}"
            pairs_differ[k] = (cleanup_mech_hashes.get(fams_list[i])
                                != cleanup_mech_hashes.get(fams_list[j]))
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)

    # Positive control
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["cleanup_family"] == pc_target["cleanup_family"]
                  and p["K"] == pc_target["K"]
                  and p["N"] == pc_target["N"]
                  and p["Q_level"] == pc_target["Q_level"]]
    if pc_matches:
        pc_top1 = pc_matches[0]["SUBSTRATE_top1_recall"]
        pc_pass = pc_top1 >= pc_target["top1_floor"]
    else:
        pc_top1 = -1.0
        pc_pass = False
    positive_control_result = {
        "target": pc_target,
        "measured_top1": pc_top1,
        "pass": pc_pass,
    }

    # Per-cleanup summary
    per_cleanup_summary: Dict[str, Dict[str, Any]] = {}
    for fam in fams:
        fam_pts = [p for p in phase_map if p["cleanup_family"] == fam]
        if not fam_pts:
            per_cleanup_summary[fam] = {"top1_mean": 0.0, "tier_counts": {},
                                         "K_cliff": {}}
            continue
        top1s = [p["SUBSTRATE_top1_recall"] for p in fam_pts]
        n_sat = sum(1 for p in fam_pts if p["band"] == "SATURATED")
        n_hp = sum(1 for p in fam_pts if p["band"] == "HARD_PASS")
        n_mb = sum(1 for p in fam_pts if p["band"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in fam_pts if p["band"] == "FLOOR")
        n_trans = sum(1 for p in fam_pts if p["band"] == "TRANSITION")
        # K-cliff locator: smallest K where SUBSTRATE_top1 drops below SAT
        K_cliff: Dict[str, int] = {}
        for N in N_sweep:
            cliff_K = -1
            for K in K_sweep:
                matches = [p for p in fam_pts if p["K"] == K and p["N"] == N]
                if matches and matches[0]["SUBSTRATE_top1_recall"] < BAND_SAT:
                    cliff_K = K
                    break
            K_cliff[f"N{N}"] = cliff_K
        per_cleanup_summary[fam] = {
            "top1_mean": round(float(np.mean(top1s)), 4),
            "tier_counts": {"SAT": n_sat, "HARD_PASS": n_hp, "MIDDLE_BAND": n_mb,
                             "FLOOR": n_floor, "TRANSITION": n_trans},
            "K_cliff": K_cliff,
        }

    # Cleanup tier (DOMINANT / COMPETITIVE / DOMINATED)
    means = {fam: per_cleanup_summary[fam]["top1_mean"] for fam in fams}
    best = max(means.values()) if means else 0.0
    cleanup_tiers: Dict[str, str] = {}
    for fam in fams:
        m = means[fam]
        if m >= best - 0.05:
            others = [v for k, v in means.items() if k != fam]
            next_best = max(others) if others else 0.0
            if m == best and (m - next_best) > 0.10:
                cleanup_tiers[fam] = "DOMINANT_CLEANUP"
            else:
                cleanup_tiers[fam] = "COMPETITIVE_CLEANUP"
        else:
            cleanup_tiers[fam] = "DOMINATED_CLEANUP"

    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "cleanup_families": list(fams),
        "K_sweep": K_sweep,
        "N_sweep": N_sweep,
        "Q_level": Q_LEVEL,
        "n_queries_per_point": n_queries,
        "N": max(N_sweep),  # PROT-021 N stamp
        "phase_map": phase_map,
        "per_cleanup_summary": per_cleanup_summary,
        "cleanup_tiers": cleanup_tiers,
        "cleanup_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_cleanup": arms_differ_per_cl,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "kanerva_K_cliff_predictions": crlb_preds,
        "backend": get_backend_label(),
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_cleanup", {})
    pairs_differ = body.get("cleanup_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    fams = body.get("cleanup_families", list(CLEANUP_FAMILIES))

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, (f"cardinality_breach: expected {expected_n} "
                       f"got {len(phase_map)}")

    # 2. arms_differ for ALL cleanups
    for fam in fams:
        ad = arms_differ.get(fam, {})
        if not ad.get("differ"):
            return False, (f"arms_identical_cleanup_{fam}: mech and "
                           f"random hashes match")

    # 3. 4 distinct cleanup mechanism hashes (all pairs differ)
    n_pairs = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < n_pairs:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (f"cleanup_collapse: {n_distinct}/{n_pairs} pairs "
                       f"distinct; identical: {collapsed}")

    # 4. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                       f"measured={pc_result.get('measured_top1')}; "
                       f"test rig broken")

    # 5. Cliff observable: at least 1 point per cleanup in (FLOOR, SAT) gap
    for fam in fams:
        fam_pts = [p for p in phase_map if p["cleanup_family"] == fam]
        any_cliff = any(BAND_FLOOR < p["SUBSTRATE_top1_recall"] < BAND_SAT
                        for p in fam_pts)
        if not any_cliff:
            tops = [(p["K"], p["N"], p["SUBSTRATE_top1_recall"])
                    for p in fam_pts]
            return False, (f"discriminator_fails_scale_{fam}: no cliff-edge "
                           f"points in (FLOOR={BAND_FLOOR}, SAT={BAND_SAT}); "
                           f"points: {tops}; ABORT FULL DISPATCH")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ(4 cleanups) "
                  f"+ 4-distinct-cleanups + positive_control_pass + "
                  f"cliff_observable_per_cleanup")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                          run_mode: str) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "HARD_FAIL", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_cleanup", {})
    pairs_differ = body.get("cleanup_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    pc_result = body.get("positive_control_result", {})
    per_cl_summary = body.get("per_cleanup_summary", {})
    cleanup_tiers = body.get("cleanup_tiers", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)
    fams = body.get("cleanup_families", list(CLEANUP_FAMILIES))

    # Tier counts
    n_hp = sum(1 for p in phase_map if p["band"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["band"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["band"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["band"] == "FLOOR")
    n_trans = sum(1 for p in phase_map if p["band"] == "TRANSITION")
    n_disc = n_hp + n_mb

    # avg arms_diff
    diffs = [p["arms_diff"] for p in phase_map]
    avg_arm_diff = float(np.mean(diffs)) if diffs else 0.0

    common = {
        "phase_map": phase_map,
        "per_cleanup_summary": per_cl_summary,
        "cleanup_tiers": cleanup_tiers,
        "cleanup_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_cleanup": arms_differ,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                         "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                         "TRANSITION": n_trans},
        "n_discriminating": n_disc,
        "avg_arms_diff": avg_arm_diff,
        "kanerva_K_cliff_predictions": body.get("kanerva_K_cliff_predictions",
                                                {}),
        "backend": body.get("backend"),
        "beta": BETA,
        "alpha_soft": ALPHA_SOFT,
        "cleanup_iters": CLEANUP_ITERS,
        "encoder_fixed": "bipolar_seqbind_v2_idiom",
        "Q_level": Q_LEVEL,
        "tag_density_effective": BASE_TAG_DENSITY * Q_LEVEL,
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} "
                    f"trans={n_trans}; 4-cleanup-distinct; positive_control"
                    f"@iterative_cosine top1={pc_result.get('measured_top1')}; "
                    f"avg_arm_diff={avg_arm_diff:.3f}; "
                    f"cleanup_tiers={cleanup_tiers}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} "
                    f"mb={n_mb} floor={n_floor} trans={n_trans}")
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif any(not ad.get("differ") for ad in arms_differ.values()):
        bad = [fam for fam in fams
               if not arms_differ.get(fam, {}).get("differ")]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_IDENTICAL: cleanups with mech==random: {bad}"
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CONTROL_FAIL: positive_control "
                f"{pc_result.get('target')} measured top1="
                f"{pc_result.get('measured_top1')}; test rig broken; "
                f"any cleanup-discrimination framing UNTRUSTED")
    elif n_pairs_differ == 0:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_NULL_CLEANUP_INVARIANCE: all {len(fams)} "
                f"cleanups produced identical mechanism hashes; cleanup is "
                f"NOT a discriminating lever for SEQBIND in this regime; "
                f"honest negative; n_disc={n_disc}/{observed_n}")
    elif (n_disc >= HP_MIN_DISCRIMINATING
            and avg_arm_diff >= HP_ARMS_DIFF_MIN
            and n_pairs_differ >= 2):
        # Cliff observable check
        any_cliff = False
        for fam in fams:
            summ = per_cl_summary.get(fam, {})
            for ck, kv in summ.get("K_cliff", {}).items():
                if 0 < kv < max(K_SWEEP_FULL):
                    any_cliff = True
                    break
            if any_cliff:
                break
        if any_cliff:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_CLEANUP_DISCRIMINATION_SEQBIND: "
                    f"{observed_n}/{expected_n} pts; sat={n_sat} hp={n_hp} "
                    f"mb={n_mb} floor={n_floor} trans={n_trans}; "
                    f"n_pairs_differ={n_pairs_differ}/{len(pairs_differ)}; "
                    f"avg_arm_diff={avg_arm_diff:.3f}; "
                    f"cleanup_tiers={cleanup_tiers}; positive_control_pass")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_CLEANUP_DIFFERS_BUT_NO_K_CLIFF: cleanups "
                    f"distinguish but no interior K-cliff at any cleanup; "
                    f"n_disc={n_disc}/{observed_n}; "
                    f"n_pairs_differ={n_pairs_differ}/{len(pairs_differ)}")
    elif n_disc >= MB_MIN_DISCRIMINATING:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_CLEANUP_DIFFERS_PARTIAL: n_disc={n_disc}/"
                f"{observed_n} (HP gate >= {HP_MIN_DISCRIMINATING}); "
                f"n_pairs_differ={n_pairs_differ}/{len(pairs_differ)}; "
                f"avg_arm_diff={avg_arm_diff:.3f} "
                f"(HP gate >= {HP_ARMS_DIFF_MIN}); "
                f"cleanup_tiers={cleanup_tiers}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_SPARSE: n_disc={n_disc}/{observed_n}; "
                f"n_pairs_differ={n_pairs_differ}/{len(pairs_differ)}; "
                f"sat={n_sat} floor={n_floor} trans={n_trans}; "
                f"cleanup_tiers={cleanup_tiers}")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "CLEANUP_FAMILIES", "K_SWEEP_FULL", "N_SWEEP_FULL", "K_SWEEP_SMOKE",
    "N_SWEEP_SMOKE", "Q_LEVEL", "N_QUERIES_FULL", "N_QUERIES_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "BAND_SAT", "BAND_MB_LO", "BAND_MB_HI", "BAND_FLOOR",
    "HP_DISCRIMINATOR", "MB_DISCRIMINATOR",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "BETA", "ALPHA_SOFT", "CLEANUP_ITERS",
    "V_ITEMS", "V_POS", "ANCHOR_PREFIX", "REQUIRED_FIELDS",
    "get_backend_label", "kanerva_K_cliff_prediction",
    "run_one_seed_phase_diagram", "smoke_gate_predicate",
    "aggregate_and_verdict", "selftest",
]
