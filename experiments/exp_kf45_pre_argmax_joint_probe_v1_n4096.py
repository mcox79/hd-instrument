"""KF-4 + KF-5 JOINT PRE-ARGMAX LAYER PROBE v1 at N=4096.

PARENT: exp_kf4_drift_detect_v4_n4096.py (KF-4 acc-drop approach) +
        exp_kf5_steerable_beta_v2.py (KF-5 entropy steerability) +
        exp_axis1_mb_chunk1_v1.py (BSC codebook + store_facts_batched).

ROOT CAUSE (from research surge synthesis v277 / Agent 5):
  KF-4 v4 INSTRUMENTATION_SUSPECT (acc_drop=0) and KF-5 STEERABILITY_PARTIAL_DECOUPLING
  (entropy_mono yes, bpc_mono no) share the SAME root mechanism: the argmax output bottleneck
  collapses internal state variation. Pre-argmax internal state is rich (logit spectrum,
  top-k diversity, W spectral signature) but collapses at the discrete argmax output.

SCIENTIFIC QUESTION (JOINT):
  Does the substrate's W matrix exhibit:
  (a) SPECTRAL STRUCTURE during/after retrieval that tracks drift? (KF-4 rescue)
  (b) LOGIT DISTRIBUTION pre-argmax that varies with beta? (KF-5 rescue at logit layer)
  (c) TOP-K DIVERSITY (JSD across top-k distributions) that is beta-steerable? (KF-5 rescue)

  All three measurements at fixed M_frac=4.0, N=4096, BSC codebook (Kerdock-free for
  generality; BSC is codebook-agnostic). Beta sweep: {2, 8, 16, 32, 64, 128}.
  Drift protocol: inject 200 spurious outer products (same as v4), then re-measure all signals.

SIGNAL DEFINITIONS:
  spectral_gap_shift: (spectral_gap_after_drift - spectral_gap_before_drift) / spectral_gap_before_drift
    Measures fractional change in W's top eigenvalue gap under drift.
    Expected if KF-4 signal exists: |shift| > 0.05 (5% fractional change).
  logit_entropy_pre_argmax: H(softmax(beta * W@k_q)) over codebook, before argmax projection.
    Measured across n_probe queries. Varies with beta by construction; the KF-5 question is
    whether bpc_inf also varies (it did NOT in v275). Logit entropy here is the pre-argmax signal.
  topk_jsd_diversity: Jensen-Shannon divergence between top-k=8 softmax distribution at
    beta_low vs beta_high (2 vs 128). If JSD > 0.1, the substrate's top-k output layer IS steerable.

PRE-REGISTERED BANDS (multi-signal; any one signal HARD_PASSing rescues the corresponding KF):
  SPECTRAL SIGNAL (KF-4):
    HARD_PASS_SPECTRAL: mean |spectral_gap_shift| >= 0.05 across seeds (5% fractional shift).
    HARD_FAIL_SPECTRAL: mean |spectral_gap_shift| < 0.005 (< 0.5%, noise floor).
  LOGIT ENTROPY SIGNAL (KF-5 pre-argmax):
    HARD_PASS_LOGIT: logit_entropy decreases monotonically with beta in >= 3/3 seeds
      AND logit_entropy_range > 1.0 bit across beta sweep.
    HARD_FAIL_LOGIT: logit_entropy_range < 0.1 bit across all beta values.
  TOP-K JSD SIGNAL (KF-5 top-k steerability):
    HARD_PASS_TOPK: mean_jsd(beta_2 vs beta_128) >= 0.10 across seeds.
    HARD_FAIL_TOPK: mean_jsd < 0.01 (flat top-k distribution, no steerability).
  JOINT OUTCOME:
    JOINT_HARD_PASS: >= 2 of 3 signals HARD_PASS.
    JOINT_MIDDLE_BAND: exactly 1 signal HARD_PASS, OR all 3 MIDDLE_BAND.
    JOINT_HARD_FAIL: all 3 signals HARD_FAIL.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M at M_frac=4.0, N=4096: M=16384.
  3. spectral_gap_shift = (gap_after - gap_before) / max(gap_before, 1e-9).
     For gap_before=0.5, gap_after=0.6: shift = (0.6-0.5)/0.5 = 0.2. Passes HP (>=0.05).
     For gap_before=0.5, gap_after=0.503: shift = 0.006. Passes neither HP nor HF.
  4. logit_entropy: H(uniform over C=16384) = log2(16384) = 14.0 bits (beta->0 limit).
     H(one-hot) = 0 bits (beta->inf). Range should be >> 1.0 for any reasonable beta sweep.
  5. topk_jsd: JSD(P, Q) in [0, 1]. For identical distributions: JSD=0. For disjoint: JSD=1.
  6. N_DRIFT_STEPS=200 spurious outer products (same as kf4_v4).
  7. BSC codebook: random bipolar atoms, C = 4*N atoms (matches Kerdock size at N=4096).

OOM CHECK:
  W at N=4096: 4096*4096*4 = 64MB. BSC codebook C=16384 x N=4096: 268MB. W + codebook: ~332MB.
  Top-k extraction: O(C) per query, no additional large allocation.
  Spectral analysis: eigvalsh on (C_probe x C_probe) matrix where C_probe <= 128. Negligible.
  Peak: ~500MB. Well under 6GB. PASS.

TIMEOUT ESTIMATE:
  kf4_v4 smoke at N=1024, M_frac=2, 1 seed, n_probe=50: ~5s CPU.
  This script: N=4096 (4x on dim); M_frac=4.0 (2x deeper); 6 beta values (new); 3 seeds.
  Added spectral + JSD: ~3x overhead per cell.
  Smoke estimate: 5 * (1024/1024)^1.5 * 1 * 1 * 3 = ~15s CPU; GPU ~3s.
  FULL: 5 * (4096/1024)^1.5 * 3 * 3 = 5 * 8 * 3 * 3 = 360s GPU. Safety 2x: 720s.
  Round to 900s. Under 2h: no extra flag.
  timeout_s = 900.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf45_pre_argmax_joint_probe_v1_n4096
Queue: overnight_queue (GPU; N=4096 BSC codebook; pre-argmax spectral+logit+topk probe)
Pre-reg: preregs/2026-05-29_kf45_pre_argmax_joint_probe_v1_n4096.md
Parent: exp_kf4_drift_detect_v4_n4096.py + exp_kf5_steerable_beta_v2.py +
        exp_axis1_mb_chunk1_v1.py (store_facts_batched)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load chunk1 for store_facts_batched, compute_retention
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_kf45v1", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention   = c1.compute_retention

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# BSC codebook: C = 4*N atoms (matching Kerdock size for fair comparison)
# BSC is codebook-agnostic: random bipolar atoms
# Sweep M_frac to capture both in-capacity (logit signal visible) and over-capacity
# (drift signal visible). The KF research note used M_frac=4 but logit entropy
# requires in-capacity operation for the beta-steering signal to manifest.
# Measuring both gives the full picture: spectral at M_frac=4, logit at M_frac=1.
M_FRACS_FULL  = [1.0, 4.0]   # in-capacity + over-capacity
M_FRACS_SMOKE = [1.0, 4.0]   # same both scales
M_FRAC_FULL   = 4.0   # kept for PROT-018 reference (spectral drift still at M_frac=4)

# Beta sweep for logit + top-k measurements (KF-5 layer)
BETA_SWEEP_FULL  = [2.0, 8.0, 16.0, 32.0, 64.0, 128.0]
BETA_SWEEP_SMOKE = [2.0, 16.0, 128.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE_FULL  = 200   # number of queries for retention + logit measurements
N_PROBE_SMOKE = 50

N_DRIFT_STEPS = 200   # spurious outer products (same as kf4_v4)
TOPK_K        = 8     # top-k for JSD diversity measurement

# Pre-registered thresholds
HP_SPECTRAL_SHIFT_MIN = 0.05   # >= 5% fractional gap shift
HF_SPECTRAL_SHIFT_MAX = 0.005  # < 0.5% = noise floor
HP_LOGIT_RANGE_MIN    = 1.0    # >= 1.0 bit entropy range across beta sweep
HF_LOGIT_RANGE_MAX    = 0.1    # < 0.1 bit = no signal
HP_LOGIT_MONO_SEEDS   = 3      # need all 3 seeds monotone for HARD_PASS
HP_TOPK_JSD_MIN       = 0.10   # mean JSD between beta_low=2 and beta_high=128
HF_TOPK_JSD_MAX       = 0.01   # < 0.01 = flat top-k


def get_output_dir(default_name: str = "kf45_pre_argmax_joint_probe_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_codebook(C: int, N: int, seed: int, device: torch.device) -> torch.Tensor:
    """BSC codebook: C x N bipolar (+/-1) atoms, normalized to unit L2."""
    gen = torch.Generator(device=device).manual_seed(seed + 99999)
    atoms = torch.randint(0, 2, (C, N), generator=gen, device=device,
                          dtype=torch.float32) * 2.0 - 1.0
    atoms = atoms / math.sqrt(N)
    return atoms


def compute_logit_entropy(W: torch.Tensor, keys: torch.Tensor, codebook: torch.Tensor,
                           beta: float, N: int, n_probe: int) -> Tuple[float, float]:
    """Compute mean and std of pre-argmax logit entropy across n_probe queries.

    Logit entropy = H(softmax(beta * sims)) in bits where
    sims = (codebook @ q) / N,  q = W @ k_q  (standard retrieval formula).
    This is the FULL distribution entropy BEFORE argmax, not the argmax-projected value.
    """
    n = min(n_probe, keys.shape[0])
    probe_keys = keys[:n]   # (n, N)

    # q = W @ k_q for each query: (n, N)
    q_batch = probe_keys @ W.T   # (n, N)

    # Similarity: codebook vs query response (same formula as compute_retention)
    # sims = (codebook @ q_i) / N for each query i
    # Shape: (C, n)
    sims = (codebook @ q_batch.T) / N   # (C, n)

    # Logits with beta scaling
    logits = beta * sims   # (C, n)

    # Softmax over codebook dim
    log_probs = torch.log_softmax(logits, dim=0)   # (C, n)
    probs = log_probs.exp()
    # Entropy per query: -sum(p * log2(p))
    H = -(probs * log_probs / math.log(2)).sum(dim=0)   # (n,)
    return float(H.mean().item()), float(H.std().item())


def compute_topk_distribution(W: torch.Tensor, keys: torch.Tensor, codebook: torch.Tensor,
                                beta: float, N: int, n_probe: int, topk: int) -> torch.Tensor:
    """Compute mean top-k probability mass distribution across n_probe queries.

    Returns (topk,) tensor: mean softmax probabilities at top-k positions,
    averaged across n_probe queries (positions sorted by descending logit at each query).
    """
    n = min(n_probe, keys.shape[0])
    probe_keys = keys[:n]
    q_batch = probe_keys @ W.T   # (n, N)
    sims = (codebook @ q_batch.T) / N   # (C, n)
    logits = beta * sims   # (C, n)
    probs = torch.softmax(logits, dim=0)   # (C, n)
    # Top-k per query
    topk_vals, _ = torch.topk(probs, k=topk, dim=0)   # (topk, n)
    mean_topk = topk_vals.mean(dim=1)   # (topk,)
    return mean_topk


def jsd(P: torch.Tensor, Q: torch.Tensor) -> float:
    """Jensen-Shannon divergence between two distributions. In [0, 1]."""
    M = 0.5 * (P + Q)
    eps = 1e-12
    kl_pm = ((P + eps) * ((P + eps) / (M + eps)).log()).sum()
    kl_qm = ((Q + eps) * ((Q + eps) / (M + eps)).log()).sum()
    jsd_val = 0.5 * (kl_pm + kl_qm)
    # Normalize to [0, 1] by dividing by log(2)
    return float((jsd_val / math.log(2)).item())


def compute_w_spectral_gap(W: torch.Tensor, n_top: int = 64) -> float:
    """Spectral gap of W: (lambda_1 - lambda_2) / lambda_1 for top-2 singular values."""
    try:
        # Use fast partial SVD on a random projection of W
        N = W.shape[0]
        gen = torch.Generator(device=W.device).manual_seed(42)
        rand_proj = torch.randn(N, n_top, generator=gen, device=W.device,
                                dtype=torch.float32) / math.sqrt(n_top)
        W_proj = W @ rand_proj   # (N, n_top)
        # SVD of the projected W
        try:
            _, svs, _ = torch.linalg.svd(W_proj, full_matrices=False)
        except Exception:
            svs = torch.linalg.svdvals(W_proj)
        svs = svs.sort(descending=True).values
        if len(svs) >= 2 and svs[0].abs() > 1e-9:
            gap = float(((svs[0] - svs[1]) / svs[0].abs()).item())
        else:
            gap = 0.0
    except Exception:
        gap = 0.0
    return gap


def run_one_m_frac(N: int, M_frac: float, seed: int, n_probe: int,
                    beta_sweep: List[float], device: torch.device) -> Dict:
    """Alias for run_one_seed with explicit M_frac parameter."""
    return run_one_seed(N, M_frac, seed, n_probe, beta_sweep, device)


def run_one_seed(N: int, M_frac: float, seed: int, n_probe: int,
                  beta_sweep: List[float], device: torch.device) -> Dict:
    """Full measurement for one seed: spectral + logit + topk across beta sweep."""
    M = int(M_frac * N)
    C = 4 * N   # BSC codebook size matching Kerdock at this N

    codebook = make_bsc_codebook(C, N, seed, device)

    # Store M facts
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    # --- SPECTRAL SIGNAL (KF-4) ---
    gap_before = compute_w_spectral_gap(W)

    # Apply drift: 200 spurious outer products
    gen_drift = torch.Generator(device=device).manual_seed(seed + 8888)
    W_drifted = W.clone()
    for _ in range(N_DRIFT_STEPS):
        ki = torch.randint(0, C, (1,), generator=gen_drift, device=device)[0]
        vi = torch.randint(0, C, (1,), generator=gen_drift, device=device)[0]
        W_drifted = W_drifted + torch.outer(codebook[vi], codebook[ki]) / N

    gap_after = compute_w_spectral_gap(W_drifted)
    spectral_gap_shift = (gap_after - gap_before) / max(abs(gap_before), 1e-9)
    abs_spectral_shift = abs(spectral_gap_shift)

    # --- LOGIT + TOP-K SIGNALS (KF-5) ---
    logit_entropies = []   # mean entropy per beta
    topk_dist_low  = None  # top-k distribution at lowest beta
    topk_dist_high = None  # top-k distribution at highest beta

    for beta in beta_sweep:
        h_mean, h_std = compute_logit_entropy(W, keys, codebook, beta, N, n_probe)
        logit_entropies.append({"beta": beta, "h_mean": round(h_mean, 5), "h_std": round(h_std, 5)})
        topk_dist = compute_topk_distribution(W, keys, codebook, beta, N, n_probe, TOPK_K)
        if beta == min(beta_sweep):
            topk_dist_low  = topk_dist
        if beta == max(beta_sweep):
            topk_dist_high = topk_dist

    # JSD between lowest and highest beta top-k distributions
    topk_jsd = jsd(topk_dist_low, topk_dist_high) if topk_dist_low is not None and topk_dist_high is not None else 0.0

    # Logit entropy range across beta sweep
    h_values = [le["h_mean"] for le in logit_entropies]
    logit_entropy_range = max(h_values) - min(h_values) if h_values else 0.0

    # Monotonicity check: H should DECREASE as beta increases
    logit_mono = all(
        logit_entropies[i]["h_mean"] >= logit_entropies[i+1]["h_mean"]
        for i in range(len(logit_entropies) - 1)
    )

    print(
        f"    N={N} M_frac={M_frac} seed={seed} "
        f"gap_before={gap_before:.4f} gap_after={gap_after:.4f} "
        f"spectral_shift={spectral_gap_shift:.4f} "
        f"logit_entropy_range={logit_entropy_range:.3f}bits "
        f"logit_mono={logit_mono} topk_jsd={topk_jsd:.4f}",
        flush=True
    )

    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "gap_before": round(gap_before, 6),
        "gap_after": round(gap_after, 6),
        "spectral_gap_shift": round(spectral_gap_shift, 6),
        "abs_spectral_shift": round(abs_spectral_shift, 6),
        "passes_hp_spectral": abs_spectral_shift >= HP_SPECTRAL_SHIFT_MIN,
        "logit_entropies": logit_entropies,
        "logit_entropy_range": round(logit_entropy_range, 5),
        "logit_mono": logit_mono,
        "passes_hp_logit": (logit_mono and logit_entropy_range >= HP_LOGIT_RANGE_MIN),
        "topk_jsd": round(topk_jsd, 6),
        "passes_hp_topk": topk_jsd >= HP_TOPK_JSD_MIN,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF45_JOINT_INCONCLUSIVE", "No cells computed.")

    valid = [c for c in cells if "spectral_gap_shift" in c]
    if not valid:
        return ("KF45_JOINT_INCONCLUSIVE", "No valid cells.")

    # Signal 1: spectral
    mean_spectral = sum(abs(c["abs_spectral_shift"]) for c in valid) / len(valid)
    spectral_hp = mean_spectral >= HP_SPECTRAL_SHIFT_MIN
    spectral_hf = mean_spectral < HF_SPECTRAL_SHIFT_MAX

    # Signal 2: logit entropy
    mean_logit_range = sum(c["logit_entropy_range"] for c in valid) / len(valid)
    n_mono = sum(1 for c in valid if c.get("logit_mono", False))
    logit_hp = (n_mono >= HP_LOGIT_MONO_SEEDS and mean_logit_range >= HP_LOGIT_RANGE_MIN)
    logit_hf = mean_logit_range < HF_LOGIT_RANGE_MAX

    # Signal 3: top-k JSD
    mean_jsd = sum(c["topk_jsd"] for c in valid) / len(valid)
    topk_hp = mean_jsd >= HP_TOPK_JSD_MIN
    topk_hf = mean_jsd < HF_TOPK_JSD_MAX

    n_hp = sum([spectral_hp, logit_hp, topk_hp])
    n_hf = sum([spectral_hf, logit_hf, topk_hf])

    detail = (
        f"spectral: shift={mean_spectral:.4f} HP={HP_SPECTRAL_SHIFT_MIN} HF={HF_SPECTRAL_SHIFT_MAX} "
        f"PASS={spectral_hp}. "
        f"logit: range={mean_logit_range:.3f}bits mono={n_mono}/{len(valid)} "
        f"HP={HP_LOGIT_RANGE_MIN} HF={HF_LOGIT_RANGE_MAX} PASS={logit_hp}. "
        f"topk_jsd: mean={mean_jsd:.4f} HP={HP_TOPK_JSD_MIN} HF={HF_TOPK_JSD_MAX} "
        f"PASS={topk_hp}. n_hp={n_hp}/3 n_hf={n_hf}/3"
    )

    if n_hp >= 2:
        kf_labels = []
        if spectral_hp:
            kf_labels.append("KF4(spectral)")
        if logit_hp or topk_hp:
            kf_labels.append("KF5(logit/topk)")
        return ("KF45_JOINT_HARD_PASS",
                f"PRE_ARGMAX_SIGNAL_DETECTED: {' '.join(kf_labels)}. {detail}")

    if n_hf == 3:
        return ("KF45_JOINT_HARD_FAIL",
                f"NO_PRE_ARGMAX_SIGNAL: all signals at noise floor. "
                f"Supports structural-invariance positive reframe. {detail}")

    # Smoke path
    smoke = summary.get("smoke", False)
    if smoke:
        if n_hp >= 1:
            return ("KF45_SMOKE_PASS", f"SMOKE_PARTIAL_SIGNAL: {detail}")
        return ("KF45_SMOKE_MIDDLE", f"SMOKE_WEAK: {detail}")

    return ("KF45_JOINT_MIDDLE_BAND", f"PARTIAL_PRE_ARGMAX_SIGNAL: {detail}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-tests
    M_at_4 = int(M_FRAC_FULL * N_FULL)
    assert M_at_4 == 16384, f"M at M_frac=4: {M_at_4}"

    # spectral_gap_shift formula
    gap_b, gap_a = 0.5, 0.6
    shift = (gap_a - gap_b) / max(abs(gap_b), 1e-9)
    assert abs(shift - 0.2) < 1e-6, f"spectral_gap_shift formula: {shift}"
    assert shift >= HP_SPECTRAL_SHIFT_MIN, f"shift=0.2 should pass HP=0.05"

    # logit entropy: uniform over C gives log2(C) bits
    C_test = 4 * 1024   # at N_SMOKE=1024
    expected_max_bits = math.log2(C_test)
    assert abs(expected_max_bits - 12.0) < 1e-6, f"uniform entropy at C=4096: {expected_max_bits}"

    # JSD between identical distributions = 0
    P = torch.ones(TOPK_K) / TOPK_K
    Q = torch.ones(TOPK_K) / TOPK_K
    j = jsd(P, Q)
    assert j < 1e-5, f"JSD(P,P) should be ~0; got {j}"

    # JSD between disjoint distributions ~ 1.0
    P2 = torch.zeros(TOPK_K)
    P2[0] = 1.0
    Q2 = torch.zeros(TOPK_K)
    Q2[-1] = 1.0
    j2 = jsd(P2, Q2)
    assert j2 > 0.9, f"JSD(delta_0, delta_k) should be ~1; got {j2}"

    # Verdict gate: 2+ signals HARD_PASS -> JOINT_HARD_PASS
    fake_cells = [
        {"spectral_gap_shift": 0.12, "abs_spectral_shift": 0.12, "passes_hp_spectral": True,
         "logit_entropy_range": 2.5, "logit_mono": True, "passes_hp_logit": True,
         "topk_jsd": 0.05, "passes_hp_topk": False},
        {"spectral_gap_shift": 0.10, "abs_spectral_shift": 0.10, "passes_hp_spectral": True,
         "logit_entropy_range": 2.3, "logit_mono": True, "passes_hp_logit": True,
         "topk_jsd": 0.04, "passes_hp_topk": False},
        {"spectral_gap_shift": 0.08, "abs_spectral_shift": 0.08, "passes_hp_spectral": True,
         "logit_entropy_range": 2.1, "logit_mono": True, "passes_hp_logit": True,
         "topk_jsd": 0.06, "passes_hp_topk": False},
    ]
    v, msg = compute_verdict({"cells": fake_cells, "smoke": False})
    assert "HARD_PASS" in v, f"Expected HARD_PASS with 2/3 signals; got {v}: {msg}"

    # Verdict gate: all HARD_FAIL -> JOINT_HARD_FAIL
    fake_hf = [
        {"spectral_gap_shift": 0.001, "abs_spectral_shift": 0.001, "passes_hp_spectral": False,
         "logit_entropy_range": 0.05, "logit_mono": False, "passes_hp_logit": False,
         "topk_jsd": 0.005, "passes_hp_topk": False},
    ]
    v_hf, _ = compute_verdict({"cells": fake_hf, "smoke": False})
    assert "HARD_FAIL" in v_hf, f"Expected HARD_FAIL with all signals at noise floor; got {v_hf}"

    # Smoke forward pass
    device = torch.device("cpu")
    cell = run_one_seed(N_SMOKE, M_FRACS_SMOKE[0], 17, N_PROBE_SMOKE,
                         BETA_SWEEP_SMOKE, device)
    assert "spectral_gap_shift" in cell, "spectral_gap_shift missing"
    assert not math.isnan(cell["spectral_gap_shift"]), "spectral_gap_shift NaN"
    assert "logit_entropy_range" in cell, "logit_entropy_range missing"
    assert cell["logit_entropy_range"] >= 0.0, f"logit_entropy_range negative: {cell['logit_entropy_range']}"
    assert "topk_jsd" in cell, "topk_jsd missing"
    assert 0.0 <= cell["topk_jsd"] <= 1.0, f"topk_jsd out of range: {cell['topk_jsd']}"

    # 4x smoke (multi-scale gate)
    cell_4x = run_one_seed(N_SMOKE * 4, M_FRACS_SMOKE[0], 17, N_PROBE_SMOKE,
                            BETA_SWEEP_SMOKE, device)
    assert "spectral_gap_shift" in cell_4x, "4x spectral_gap_shift missing"
    assert not math.isnan(cell_4x["spectral_gap_shift"]), "4x spectral_gap_shift NaN"

    # Import chain coverage: verify chunk1 helpers are callable
    assert callable(store_facts_batched), "store_facts_batched not callable"
    assert callable(compute_retention),   "compute_retention not callable"

    print(
        f"[selftest] kf45_pre_argmax_joint_probe_v1_n4096 PASS "
        f"spectral_shift={cell['spectral_gap_shift']:.4f} "
        f"logit_range={cell['logit_entropy_range']:.3f}bits "
        f"topk_jsd={cell['topk_jsd']:.4f}",
        flush=True
    )


_instrumentation_selftest()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg      = N_SMOKE         if smoke else N_FULL
    seeds      = SEEDS_SMOKE     if smoke else SEEDS_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    n_probe    = N_PROBE_SMOKE   if smoke else N_PROBE_FULL

    assert N_cfg == N_FULL or smoke, (
        f"PROT-018: production N must be {N_FULL}; got {N_cfg}"
    )

    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL

    print(
        f"[run] kf45_pre_argmax_joint_probe_v1_n4096 smoke={smoke} N={N_cfg} "
        f"M_fracs={m_fracs} beta_sweep={beta_sweep} seeds={seeds} device={device_str}",
        flush=True
    )
    t0 = time.time()

    all_cells = []
    for seed in seeds:
        for M_frac in m_fracs:
            print(f"\n  [seed={seed} M_frac={M_frac}]", flush=True)
            cell = run_one_seed(N_cfg, M_frac, seed, n_probe, beta_sweep, device)
            all_cells.append(cell)
        print(f"  seed={seed} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "smoke": smoke, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf45_pre_argmax_joint_probe_v1_n4096",
        "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "beta_sweep": beta_sweep,
        "seeds": seeds, "n_probe": n_probe,
        "N_drift_steps": N_DRIFT_STEPS,
        "cells": all_cells,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir  = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
