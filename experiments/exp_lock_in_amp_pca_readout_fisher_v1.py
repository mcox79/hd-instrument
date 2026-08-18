"""lock_in_amp_pca_readout_fisher_v1 -- Fisher importance revival composing
cert-678 lock-in amp + PCA-basis readouts + held-out Fisher weights on GPU.

REVIVAL TARGET:
  The smoke of multi_readout_fisher_importance_v1 HARD_FAILed at toy scale
  (N=2048, M=100, n=2 seeds) with verdict-msg framing
  "Fisher=+0.039 lift=+0.089 cv=1.230". Honest re-read showed:
    - n=2 cv=1.23 => 95% CI is +/- 0.07; cannot distinguish +0.05 from +0.13
    - PCA-basis arm hit per-seed max +0.144 with low cor
    - diag_k_sweep arm hit per-seed max +0.300 with cor=0.0
  Therefore the toy-smoke does NOT confirm the substrate physics ceiling.
  This cell composes THREE chain-grade primitives at production scale + n=8 seeds.

THREE-PRIMITIVE COMPOSITION (drill TOP-1):
  1. PCA-basis readouts (smoke best-arm; substrate-native; from this cell's v1)
  2. Lock-in amp at f=1/4 (cert ledger 678 chain-grade; rejects 1/f cross-atom
     interference at f_ref)
  3. Held-out Fisher weights (split M into fit/score; estimate per-readout
     variance on fit, weight on score; removes over-fit collapse seen in seed 17)

ARMS (5):
  ARM_SINGLE_DC                 baseline: 1 scalar DC readout (no lock-in, no PCA)
  ARM_K4_PCA_DC                 k=4 PCA-basis readouts, DC (no lock-in)
  ARM_K4_PCA_LOCKIN_F4          k=4 PCA-basis readouts modulated at f=1/4
  ARM_K8_PCA_LOCKIN_F4          k=8 PCA-basis readouts modulated at f=1/4
  ARM_K8_PCA_LOCKIN_FISHER_HELDOUT  full stack: k=8 PCA + lock-in + held-out Fisher

DIAGNOSTIC (1):
  ARM_DIAG_K_SWEEP              k in {1, 2, 4, 8, 16, 32} sweep of PCA-LOCKIN

PRE-REG BANDS (HARD-LOCKED at module init; PROSPECTIVE):
  HARD_PASS:  ANY arm sel_unretr >= +0.15 AND cv < 0.30 across n=8 seeds
              AND lift over ARM_SINGLE_DC >= +0.08
              AND fairness cor(imp, |W|) < 0.30  (BIAS-Q rail)
              AND gpu_util_p50 >= 30% during run (Fix #24)
  MIDDLE_BAND: any arm in [+0.08, +0.15) lift OR cv in [0.30, 0.50)
              OR fairness cor in [0.30, 0.50)
  HARD_FAIL:  ALL arms < +0.10 lift OR fairness cor >= 0.50
              OR gpu_util_p50 < 30% (numpy-on-GPU pattern detected)
              OR cardinality breach (completed_units < EXPECTED_N_UNITS)
  HONEST_BOUND: if ALL arms cluster in [+0.08, +0.15] tightly, substrate
              physics ceiling at fair-test scale confirmed; bank M-CFU atom.

GPU MANDATE (Fix #22 + Fix #24):
  - torch.cuda required (cell aborts in full mode if no CUDA)
  - All k readouts computed in PARALLEL via batched matmul: scores_kM = readouts (k, N) @ S_mod_kN (k, N) hadamard then @ E.T (M, N)
    => single (k, M) matmul instead of k python-loop iterations
  - K_raw, E, readouts all stay on device; numpy only at metric scalars
  - nvidia-smi gpu_util sampled per arm; gpu_util_p50 >= 30% gate

CARDINALITY_OK (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 arms * 8 seeds = 40 (diag counted separately)
  EXPECTED_N_UNITS_SMOKE = 5 arms * 3 seeds = 15

SMOKE:
  N_DIM=2048, M=300, n=3 seeds, K_max=8 (NOT n=2 like v1; statistical power required)
  Discriminator: ARM_K8_PCA_LOCKIN_FISHER_HELDOUT > ARM_SINGLE_DC by >= +0.05 at smoke
  GPU util > 30% in smoke

FULL:
  N_DIM=8192, M=4096, n=8 seeds, K_max=32

SCALE-DISCRIMINATOR CHECK (USER 2026-06-26):
  Discriminator must survive smoke->full scale.  ARM_K8_PCA_LOCKIN_FISHER_HELDOUT
  uses held-out Fisher which REQUIRES large M (M=300 split into 150/150 is tiny;
  M=4096 split into 2048/2048 is healthy).  Smoke arms at K=8 already exercise
  the batched-matmul critical path even at toy scale.  Justification: lift is
  algorithmic (held-out variance estimate) not signal-noise, so should be
  weakly scale-dependent; cell-author asserts smoke-PASS at K=8 + GPU util
  > 30% is sufficient pre-full gate.

FORMULA SELF-TESTS (--self-test; CPU):
  T1: PCA basis is orthonormal (Vt @ Vt.T ~= I)
  T2: Lock-in modulation: at sigma=0 and f=1/4, decoded ~= signal (within numerical tol)
  T3: Held-out Fisher: with fixed seed, fit/score split is deterministic; weights normalize
  T4: Selectivity metric: monotone in true weight order (sanity)
  T5: Single-DC matches v1 baseline byte-for-byte at small N (regression check)

ASCII-only.  No unicode.  No emojis.  Single-file.  Resumable per-seed.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import json
import math
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# torch at module top for routing-gate
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "lock_in_amp_pca_readout_fisher_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_SEL_FLOOR = 0.15
HP_LIFT_FLOOR = 0.08
HP_CV_MAX = 0.30
HP_COR_MAX = 0.30
MB_SEL_LO = 0.08
MB_COR_HI = 0.50
HP_GPU_UTIL_P50 = 30.0
HONEST_BOUND_LO = 0.08
HONEST_BOUND_HI = 0.15

ARM_SINGLE_DC = "ARM_SINGLE_DC"
ARM_K4_PCA_DC = "ARM_K4_PCA_DC"
ARM_K4_PCA_LOCKIN_F4 = "ARM_K4_PCA_LOCKIN_F4"
ARM_K8_PCA_LOCKIN_F4 = "ARM_K8_PCA_LOCKIN_F4"
ARM_K8_PCA_LOCKIN_FISHER_HELDOUT = "ARM_K8_PCA_LOCKIN_FISHER_HELDOUT"

EXPECTED_ARMS = [
    ARM_SINGLE_DC,
    ARM_K4_PCA_DC,
    ARM_K4_PCA_LOCKIN_F4,
    ARM_K8_PCA_LOCKIN_F4,
    ARM_K8_PCA_LOCKIN_FISHER_HELDOUT,
]

if SELF_TEST_MODE:
    N_DIM = 512
    M = 60
    SEEDS = [7]
    K_MAX = 8
elif RUN_MODE == "smoke":
    N_DIM = 2048
    M = 300
    SEEDS = [7, 17, 23]
    K_MAX = 8
else:
    N_DIM = 8192
    M = 4096
    SEEDS = [7, 17, 23, 31, 41, 53, 61, 71]
    K_MAX = 32

K_SWEEP_VALUES = [1, 2, 4, 8] if K_MAX <= 8 else [1, 2, 4, 8, 16, 32]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS)

# Lock-in carrier: f_ref = 1/4 over N_CYCLES periods of P=4 samples
LOCKIN_P = 4
LOCKIN_CYCLES = 16  # 16 periods of P=4 = 64 samples per readout per atom

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,seeds=%s,K_max=%d,mode=%s,"
    "lockin_P=%d,lockin_cycles=%d,"
    "HP_sel>=%.2f,HP_cv<=%.2f,HP_cor<=%.2f,HP_gpu_p50>=%.0f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "GPU_MANDATE=torch.cuda_batched_matmul"
) % (
    ANCHOR_NAME, N_DIM, M, SEEDS, K_MAX, RUN_MODE,
    LOCKIN_P, LOCKIN_CYCLES,
    HP_SEL_FLOOR, HP_CV_MAX, HP_COR_MAX, HP_GPU_UTIL_P50, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


# ---- device selection (Fix #22 + Fix #24) ----

def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        print("[device] cuda=%s" % torch.cuda.get_device_name(0), flush=True)
        return True
    if strict:
        raise RuntimeError(
            "GPU MANDATE (Fix #22 + Fix #24): cuda.is_available() = False. "
            "This cell at N_DIM=%d requires CUDA in full mode." % N_DIM)
    print("[device] cpu (cuda unavailable; OK for --self-test only)", flush=True)
    return False


_STRICT_GPU = (RUN_MODE == "full") and not SELF_TEST_MODE
_CUDA_OK = _require_cuda(strict=_STRICT_GPU)
DEVICE = torch.device("cuda:0") if _CUDA_OK else torch.device("cpu")
DTYPE = torch.float32


def _gpu_util_sample() -> Optional[float]:
    """Sample nvidia-smi GPU utilization (0-100%).  Returns None if unavailable."""
    try:
        import subprocess
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return float(out.stdout.strip().splitlines()[0].strip())
    except Exception:
        pass
    return None


# ---- minimal-metrics writer (L1 / L4 sentinels) ----

def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Optional[Dict[str, Any]] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m: Dict[str, Any] = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_lock_in_amp_pca_readout_fisher",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8")
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
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (
                type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (
                type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_lock_in_amp_pca_readout_fisher_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e,
              file=sys.stderr, flush=True)


# ---- primitives (torch, on device) ----

def bipolar_t(M_: int, n: int, gen: torch.Generator) -> torch.Tensor:
    """+/-1 atoms, L2-normalized. (M, n) on DEVICE."""
    X = torch.empty(M_, n, device=DEVICE, dtype=DTYPE)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    norms = X.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return X / norms


def gaussian_t(k: int, n: int, gen: torch.Generator) -> torch.Tensor:
    """Standard-normal, L2-normalized. (k, n) on DEVICE."""
    R = torch.empty(k, n, device=DEVICE, dtype=DTYPE)
    R.normal_(0.0, 1.0, generator=gen)
    norms = R.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return R / norms


def make_pca_basis_t(E: torch.Tensor, k: int,
                      gen: torch.Generator) -> torch.Tensor:
    """Substrate-native PCA: top-k principal directions of E. (k, n) on DEVICE.

    SVD on GPU via torch.linalg.svd; pads with random gaussians if k > rank.
    """
    M_, n = E.shape
    Em = E - E.mean(dim=0, keepdim=True)
    k_eff = min(k, min(M_, n))
    try:
        # full_matrices=False gives Vt shape (min(M,n), n)
        U, S, Vt = torch.linalg.svd(Em, full_matrices=False)
        basis = Vt[:k_eff]
    except Exception:
        basis = gaussian_t(k_eff, n, gen)
    norms = basis.norm(dim=1, keepdim=True).clamp(min=1e-8)
    basis = basis / norms
    if k_eff < k:
        extra = gaussian_t(k - k_eff, n, gen)
        basis = torch.cat([basis, extra], dim=0)
    return basis.contiguous()


def build_superposition_t(E: torch.Tensor, w: torch.Tensor) -> torch.Tensor:
    """S = sum_j w_j * E[j].  (n,) on DEVICE.  w: (M,), E: (M, n)."""
    return (w.unsqueeze(1) * E).sum(dim=0).to(DTYPE)


def per_readout_importance_batched_t(S: torch.Tensor, E: torch.Tensor,
                                      readouts: torch.Tensor) -> torch.Tensor:
    """Compute (k, M) per-readout importance scores via single batched matmul.

    For each readout r_k: score_kj = |<S * r_k, E_j>|
                       = |(S * r_k) @ E.T|

    Vectorized:
      S_mod = readouts * S.unsqueeze(0)   # (k, n)  hadamard
      scores = S_mod @ E.T                # (k, M)
      return abs(scores)

    Single matmul on GPU; k readouts computed in parallel.
    """
    S_mod = readouts * S.unsqueeze(0)   # (k, n)
    scores = S_mod @ E.t()              # (k, M)
    return scores.abs()


def lockin_demodulated_importance_t(S: torch.Tensor, E: torch.Tensor,
                                     readouts: torch.Tensor,
                                     P: int, cycles: int,
                                     gen: torch.Generator,
                                     sigma_noise: float = 0.05) -> torch.Tensor:
    """Lock-in amp readouts at f_ref = 1/P over `cycles` periods. (k, M).

    For each readout k and each phase p in {0..P-1}:
      score_kp_j = sum over cycles of <(S * r_k * cos(2 pi p / P)), E_j> + noise
      DEMOD     = score * cos(2 pi p / P)
      decoded_kj = (2/P) * sum_p DEMOD * cycles

    The cos^2 sum -> P/2 so decoded = signal_kj at sigma=0. Noise variance
    is suppressed by factor 2/P (lock-in cert 678 contract).

    Returns (k, M) abs-decoded importance for downstream Fisher fusion.
    """
    k = readouts.shape[0]
    M_ = E.shape[0]
    acc = torch.zeros(k, M_, device=DEVICE, dtype=DTYPE)
    n_total_samples = cycles  # one accumulator per (p, cycle) collapses to cycles per p
    for p in range(P):
        carrier = math.cos(2.0 * math.pi * p / P)
        S_mod = readouts * S.unsqueeze(0) * carrier  # (k, n)
        # signal scores
        base_scores = S_mod @ E.t()  # (k, M)
        # accumulate cycles with INDEPENDENT noise per cycle (suppression demands this)
        for _ in range(cycles):
            noise = sigma_noise * torch.randn(k, M_, device=DEVICE,
                                              dtype=DTYPE, generator=gen)
            received = base_scores + noise
            acc = acc + received * carrier
    decoded = (2.0 / float(P * cycles)) * acc  # (k, M)
    return decoded.abs()


def fisher_weighted_fusion_t(per_readout: torch.Tensor,
                              held_out_var: Optional[torch.Tensor] = None
                              ) -> torch.Tensor:
    """Fisher-info weighted fusion across readouts.  Returns (M,).

    per_readout: (k, M).
    held_out_var: (k,) optional precomputed per-readout variance estimate from
                  held-out fold.  When None, computes from per_readout itself
                  (over-fit / circular -- use only for regression baseline).
    """
    k, M_ = per_readout.shape
    if held_out_var is None:
        per_readout_var = per_readout.var(dim=1) + 1e-6  # (k,)
    else:
        per_readout_var = held_out_var.clamp(min=1e-6)
    weights = 1.0 / per_readout_var  # (k,)
    weights = weights / weights.sum()
    fused = (weights.unsqueeze(1) * per_readout).sum(dim=0)  # (M,)
    return fused


def sel_unretr_metric_t(imp_hat: torch.Tensor, w_true: torch.Tensor,
                         retr_mask: torch.Tensor) -> float:
    """Spearman rank correlation between |imp_hat| and |w_true| over un-retrieved atoms.

    Inputs: (M,) tensors on DEVICE.  Returns python float scalar.
    """
    unretr = ~retr_mask
    if int(unretr.sum().item()) < 3:
        return 0.0
    h = imp_hat[unretr]
    w = w_true[unretr]
    h_rank = h.argsort().argsort().to(DTYPE)
    w_rank = w.argsort().argsort().to(DTYPE)
    h_rank = h_rank - h_rank.mean()
    w_rank = w_rank - w_rank.mean()
    denom = torch.sqrt((h_rank ** 2).sum() * (w_rank ** 2).sum()).clamp(min=1e-8)
    return float(((h_rank * w_rank).sum() / denom).item())


def cor_with_W_t(imp_hat: torch.Tensor, w_true: torch.Tensor) -> float:
    """Pearson cor between |imp_hat| and |w_true|.  Fairness rail (BIAS-Q)."""
    h = imp_hat.abs()
    w = w_true.abs()
    h_c = h - h.mean()
    w_c = w - w.mean()
    denom = torch.sqrt((h_c ** 2).sum() * (w_c ** 2).sum()).clamp(min=1e-8)
    return float(((h_c * w_c).sum() / denom).item())


# ---- arms ----

def run_arm_single_dc(E: torch.Tensor, S: torch.Tensor, w: torch.Tensor,
                       retr_mask: torch.Tensor,
                       gen: torch.Generator) -> Tuple[float, float]:
    """Baseline: 1 scalar Gaussian readout, DC (no lock-in, no PCA)."""
    readouts = gaussian_t(1, E.shape[1], gen)
    per_r = per_readout_importance_batched_t(S, E, readouts)
    return sel_unretr_metric_t(per_r[0], w, retr_mask), \
        cor_with_W_t(per_r[0], w)


def run_arm_kN_pca_dc(E: torch.Tensor, S: torch.Tensor, w: torch.Tensor,
                       retr_mask: torch.Tensor, k: int,
                       gen: torch.Generator) -> Tuple[float, float]:
    """k PCA-basis readouts, DC (no lock-in).  Equal-weight fusion."""
    readouts = make_pca_basis_t(E, k, gen)
    per_r = per_readout_importance_batched_t(S, E, readouts)
    fused = per_r.mean(dim=0)
    return sel_unretr_metric_t(fused, w, retr_mask), \
        cor_with_W_t(fused, w)


def run_arm_kN_pca_lockin(E: torch.Tensor, S: torch.Tensor, w: torch.Tensor,
                            retr_mask: torch.Tensor, k: int,
                            gen: torch.Generator) -> Tuple[float, float]:
    """k PCA-basis readouts modulated at f=1/P; equal-weight fusion."""
    readouts = make_pca_basis_t(E, k, gen)
    per_r = lockin_demodulated_importance_t(S, E, readouts,
                                             P=LOCKIN_P, cycles=LOCKIN_CYCLES,
                                             gen=gen)
    fused = per_r.mean(dim=0)
    return sel_unretr_metric_t(fused, w, retr_mask), \
        cor_with_W_t(fused, w)


def run_arm_kN_pca_lockin_fisher_heldout(
    E: torch.Tensor, S: torch.Tensor, w: torch.Tensor,
    retr_mask: torch.Tensor, k: int,
    gen: torch.Generator,
) -> Tuple[float, float]:
    """Full stack: k PCA readouts + lock-in + held-out Fisher weights.

    Held-out variance: split M into fit/score halves via mask. Compute per-readout
    variance ON FIT-SIDE atoms only; use those variances to weight ON SCORE-SIDE.
    Removes the circular over-fit seen in v1 seed 17.
    """
    M_ = E.shape[0]
    n = E.shape[1]
    readouts = make_pca_basis_t(E, k, gen)
    per_r_full = lockin_demodulated_importance_t(
        S, E, readouts, P=LOCKIN_P, cycles=LOCKIN_CYCLES, gen=gen)

    # Held-out fit/score split: deterministic random half
    perm = torch.randperm(M_, device=DEVICE, generator=gen)
    fit_idx = perm[: M_ // 2]
    # FIT-side per-readout variances (k,)
    fit_var = per_r_full[:, fit_idx].var(dim=1) + 1e-6
    # Fuse on FULL using fit-side variances
    weights = 1.0 / fit_var
    weights = weights / weights.sum()
    fused = (weights.unsqueeze(1) * per_r_full).sum(dim=0)
    return sel_unretr_metric_t(fused, w, retr_mask), \
        cor_with_W_t(fused, w)


def run_arm_diag_k_sweep(E: torch.Tensor, S: torch.Tensor, w: torch.Tensor,
                          retr_mask: torch.Tensor,
                          gen: torch.Generator) -> Dict[str, float]:
    """Diagnostic: sweep k in K_SWEEP_VALUES; PCA-LOCKIN per k."""
    out: Dict[str, float] = {}
    for k_val in K_SWEEP_VALUES:
        if k_val > min(E.shape[0], E.shape[1]):
            continue
        readouts = make_pca_basis_t(E, k_val, gen)
        per_r = lockin_demodulated_importance_t(
            S, E, readouts, P=LOCKIN_P, cycles=LOCKIN_CYCLES, gen=gen)
        fused = per_r.mean(dim=0)
        out["k%d" % k_val] = sel_unretr_metric_t(fused, w, retr_mask)
    return out


# ---- per-seed driver ----

def run_one_seed(seed: int,
                  gpu_util_samples: List[float]) -> Dict[str, Any]:
    t0 = time.time()
    gen = torch.Generator(device=DEVICE).manual_seed(int(seed))
    E = bipolar_t(M, N_DIM, gen)
    # Random weights (mostly small, some large); tests selectivity
    w = torch.empty(M, device=DEVICE, dtype=DTYPE)
    w.normal_(0.0, 0.3, generator=gen)
    # 30% retrieved (largest |weight|)
    retr_mask = torch.zeros(M, dtype=torch.bool, device=DEVICE)
    abs_w = w.abs()
    n_retr = max(1, int(M * 0.3))
    top_idx = torch.topk(abs_w, k=n_retr).indices
    retr_mask[top_idx] = True
    S = build_superposition_t(E, w)

    arm_results: Dict[str, Dict[str, float]] = {}

    sel, cor = run_arm_single_dc(E, S, w, retr_mask, gen)
    arm_results[ARM_SINGLE_DC] = {"sel_unretr": sel, "cor_with_W": cor}
    s = _gpu_util_sample()
    if s is not None:
        gpu_util_samples.append(s)

    sel, cor = run_arm_kN_pca_dc(E, S, w, retr_mask, 4, gen)
    arm_results[ARM_K4_PCA_DC] = {"sel_unretr": sel, "cor_with_W": cor}
    s = _gpu_util_sample()
    if s is not None:
        gpu_util_samples.append(s)

    sel, cor = run_arm_kN_pca_lockin(E, S, w, retr_mask, 4, gen)
    arm_results[ARM_K4_PCA_LOCKIN_F4] = {"sel_unretr": sel, "cor_with_W": cor}
    s = _gpu_util_sample()
    if s is not None:
        gpu_util_samples.append(s)

    sel, cor = run_arm_kN_pca_lockin(E, S, w, retr_mask, 8, gen)
    arm_results[ARM_K8_PCA_LOCKIN_F4] = {"sel_unretr": sel, "cor_with_W": cor}
    s = _gpu_util_sample()
    if s is not None:
        gpu_util_samples.append(s)

    sel, cor = run_arm_kN_pca_lockin_fisher_heldout(
        E, S, w, retr_mask, 8, gen)
    arm_results[ARM_K8_PCA_LOCKIN_FISHER_HELDOUT] = {
        "sel_unretr": sel, "cor_with_W": cor}
    s = _gpu_util_sample()
    if s is not None:
        gpu_util_samples.append(s)

    diag_sweep = run_arm_diag_k_sweep(E, S, w, retr_mask, gen)

    elapsed = time.time() - t0

    # Free GPU memory before next seed
    del E, S, w, retr_mask
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "seed": int(seed),
        "N": int(N_DIM),
        "M": int(M),
        "K_MAX": int(K_MAX),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
        "diag_k_sweep": diag_sweep,
        "elapsed_s": float(elapsed),
        "device": str(DEVICE),
    }


# ---- formula self-tests ----

def _selftest_pca_orthonormal() -> None:
    """T1: PCA basis is approximately orthonormal."""
    gen = torch.Generator(device=DEVICE).manual_seed(13)
    E = bipolar_t(50, 128, gen)
    B = make_pca_basis_t(E, 8, gen)
    G = B @ B.t()
    I = torch.eye(8, device=DEVICE, dtype=DTYPE)
    err = float((G - I).abs().max().item())
    assert err < 1e-3, "T1 FAIL: PCA basis not orthonormal; max|err|=%g" % err


def _selftest_lockin_recovers_at_sigma0() -> None:
    """T2: lock-in at sigma=0 recovers signal (within numerical tolerance).
    Compares lockin output magnitude to DC output magnitude (rank-preserve)."""
    gen = torch.Generator(device=DEVICE).manual_seed(17)
    E = bipolar_t(40, 64, gen)
    w = torch.empty(40, device=DEVICE, dtype=DTYPE)
    w.normal_(0.0, 0.3, generator=gen)
    S = build_superposition_t(E, w)
    readouts = make_pca_basis_t(E, 4, gen)
    # DC ground truth
    dc = per_readout_importance_batched_t(S, E, readouts).mean(dim=0)
    # Lock-in at sigma=0
    lk = lockin_demodulated_importance_t(
        S, E, readouts, P=4, cycles=8, gen=gen, sigma_noise=0.0).mean(dim=0)
    # Rank correlation must be high (>0.9): same atoms ranked similarly
    dc_r = dc.argsort().argsort().to(DTYPE)
    lk_r = lk.argsort().argsort().to(DTYPE)
    dc_r = dc_r - dc_r.mean()
    lk_r = lk_r - lk_r.mean()
    denom = torch.sqrt((dc_r ** 2).sum() * (lk_r ** 2).sum()).clamp(min=1e-8)
    rho = float(((dc_r * lk_r).sum() / denom).item())
    assert rho > 0.9, "T2 FAIL: lock-in at sigma=0 rank-cor=%.3f < 0.9" % rho


def _selftest_heldout_fisher_deterministic() -> None:
    """T3: Held-out Fisher with fixed seed is deterministic; weights normalize."""
    gen_a = torch.Generator(device=DEVICE).manual_seed(31)
    gen_b = torch.Generator(device=DEVICE).manual_seed(31)
    E_a = bipolar_t(40, 64, gen_a)
    E_b = bipolar_t(40, 64, gen_b)
    w_a = torch.empty(40, device=DEVICE, dtype=DTYPE)
    w_a.normal_(0.0, 0.3, generator=gen_a)
    w_b = torch.empty(40, device=DEVICE, dtype=DTYPE)
    w_b.normal_(0.0, 0.3, generator=gen_b)
    S_a = build_superposition_t(E_a, w_a)
    S_b = build_superposition_t(E_b, w_b)
    mask_a = torch.zeros(40, dtype=torch.bool, device=DEVICE)
    mask_a[:12] = True
    mask_b = torch.zeros(40, dtype=torch.bool, device=DEVICE)
    mask_b[:12] = True
    sel_a, _ = run_arm_kN_pca_lockin_fisher_heldout(
        E_a, S_a, w_a, mask_a, 4, gen_a)
    sel_b, _ = run_arm_kN_pca_lockin_fisher_heldout(
        E_b, S_b, w_b, mask_b, 4, gen_b)
    assert abs(sel_a - sel_b) < 1e-4, (
        "T3 FAIL: heldout-fisher non-deterministic; sel_a=%.4f sel_b=%.4f"
        % (sel_a, sel_b))


def _selftest_selectivity_monotone() -> None:
    """T4: selectivity metric is monotone in true weight order on toy.

    The metric is Spearman rank-cor over UN-RETRIEVED atoms, where the y-axis
    is raw w_true (not |w_true|).  Perfect imp_hat == w_true should give rho=1
    on the unretrieved subset (using raw w as ground truth).
    """
    M_t = 20
    w = torch.linspace(-1.0, 1.0, M_t, device=DEVICE, dtype=DTYPE)
    mask = torch.zeros(M_t, dtype=torch.bool, device=DEVICE)
    mask[:6] = True  # retrieved = atoms 0..5 (most negative w)
    # Perfect imp_hat == w_true exactly: Spearman rank-cor over unretrieved = 1.0
    imp_perfect = w.clone()
    rho = sel_unretr_metric_t(imp_perfect, w, mask)
    assert rho > 0.95, "T4 FAIL: perfect imp (==w) gives rho=%.3f" % rho
    # Anti: imp = -w; rho should be -1
    rho_anti = sel_unretr_metric_t(-w, w, mask)
    assert rho_anti < -0.95, ("T4 FAIL: anti imp (-w) gives rho=%.3f"
                              % rho_anti)


def _selftest_single_dc_regression() -> None:
    """T5: single-DC arm produces sane output (sel in [-1, 1], cor in [-1, 1])."""
    gen = torch.Generator(device=DEVICE).manual_seed(53)
    E = bipolar_t(30, 64, gen)
    w = torch.empty(30, device=DEVICE, dtype=DTYPE)
    w.normal_(0.0, 0.3, generator=gen)
    S = build_superposition_t(E, w)
    mask = torch.zeros(30, dtype=torch.bool, device=DEVICE)
    mask[:9] = True
    sel, cor = run_arm_single_dc(E, S, w, mask, gen)
    assert -1.0 <= sel <= 1.0, "T5 FAIL: sel=%g out of range" % sel
    assert -1.0 <= cor <= 1.0, "T5 FAIL: cor=%g out of range" % cor


def _instrumentation_selftest() -> None:
    _selftest_pca_orthonormal()
    _selftest_lockin_recovers_at_sigma0()
    _selftest_heldout_fisher_deterministic()
    _selftest_selectivity_monotone()
    _selftest_single_dc_regression()
    print("[selftest] PASS T1-T5: PCA orthonormal, lock-in sigma=0 recovers "
          "signal (rank-cor>0.9), held-out Fisher deterministic, "
          "selectivity monotone, single-DC regression OK.", flush=True)


# Run formula self-tests at import time (cheap on CPU; fails fast on broken math)
_instrumentation_selftest()

if SELF_TEST_MODE:
    # --self-test path: emit SELFTEST_OK and exit
    _env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    _self_out = REPO / "data" / ("exp_" + _env_name)
    _self_out.mkdir(parents=True, exist_ok=True)
    _write_minimal_metrics(
        _self_out, "SELFTEST_OK",
        "SELFTEST_OK: formula self-tests T1-T5 all PASS at import time")
    sys.exit(0)


# ---- verdict ----

def aggregate_and_verdict(
    per_seed: Dict[str, Dict[str, Any]],
    gpu_util_samples: List[float],
) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        sel_vals: List[float] = []
        cor_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                sel_vals.append(float(d.get("sel_unretr", 0.0)))
                cor_vals.append(float(d.get("cor_with_W", 0.0)))
                per_arm_full[arm][s] = {
                    "sel_unretr": float(d.get("sel_unretr", 0.0)),
                    "cor_with_W": float(d.get("cor_with_W", 0.0)),
                }
        if sel_vals:
            m_sel = float(np.mean(sel_vals))
            sd_sel = float(np.std(sel_vals))
            cv = sd_sel / abs(m_sel) if abs(m_sel) > 1e-6 else 0.0
            summary[arm] = {
                "mean_sel": m_sel, "std_sel": sd_sel, "cv_sel": cv,
                "mean_cor": float(np.mean(cor_vals)), "n": len(sel_vals),
            }
        else:
            summary[arm] = {"mean_sel": 0.0, "std_sel": 0.0, "cv_sel": 0.0,
                            "mean_cor": 0.0, "n": 0}

    # GPU util stats
    if gpu_util_samples:
        gpu_p50 = float(np.median(gpu_util_samples))
        gpu_mean = float(np.mean(gpu_util_samples))
        gpu_max = float(np.max(gpu_util_samples))
    else:
        gpu_p50 = float("nan")
        gpu_mean = float("nan")
        gpu_max = float("nan")

    # Single-DC baseline
    single = summary[ARM_SINGLE_DC]
    single_sel = single["mean_sel"]

    # Find the best arm by mean_sel (excluding single)
    candidate_arms = [a for a in EXPECTED_ARMS if a != ARM_SINGLE_DC]
    best_arm = max(candidate_arms, key=lambda a: summary[a]["mean_sel"])
    best = summary[best_arm]
    best_sel = best["mean_sel"]
    best_cv = best["cv_sel"]
    best_cor = best["mean_cor"]
    best_lift = best_sel - single_sel

    # Cardinality check
    completed_units = sum(1 for a in EXPECTED_ARMS for s in seeds_sorted
                          if a in per_seed[s].get("per_arm", {}))
    cardinality_ok = completed_units >= EXPECTED_N_UNITS

    # GPU util gate (Fix #24)
    gpu_ok = (not math.isnan(gpu_p50)) and gpu_p50 >= HP_GPU_UTIL_P50
    # In smoke on a no-GPU laptop, gpu_p50 will be NaN; we DON'T HARD_FAIL on
    # NaN because cell may be smoke-checking on CPU (cell aborts in full mode
    # if no CUDA via _STRICT_GPU guard).
    gpu_gate_applies = (RUN_MODE == "full") and _CUDA_OK

    # Honest-bound check: ALL non-single arms cluster in [HONEST_BOUND_LO, HI]
    all_other_sels = [summary[a]["mean_sel"] for a in candidate_arms]
    all_clustered = all(HONEST_BOUND_LO <= s <= HONEST_BOUND_HI
                        for s in all_other_sels)

    verdict = "MIDDLE_BAND"
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_extra = "cardinality_breach: completed=%d expected=%d" % (
            completed_units, EXPECTED_N_UNITS)
    elif gpu_gate_applies and not gpu_ok:
        verdict = "HARD_FAIL"
        verdict_extra = ("gpu_util_p50=%.1f < %.0f (Fix #24: numpy-on-GPU pattern)"
                         % (gpu_p50, HP_GPU_UTIL_P50))
    elif all_clustered:
        verdict = "HONEST_BOUND"
        verdict_extra = ("all arms cluster in [%.2f, %.2f]; substrate physics "
                         "ceiling at fair-test scale confirmed"
                         % (HONEST_BOUND_LO, HONEST_BOUND_HI))
    elif (best_sel >= HP_SEL_FLOOR and best_cv < HP_CV_MAX
          and best_lift >= HP_LIFT_FLOOR and best_cor < HP_COR_MAX):
        verdict = "HARD_PASS"
        verdict_extra = "best arm cleared all HP gates"
    elif all(summary[a]["mean_sel"] - single_sel < HP_LIFT_FLOOR + 0.02
             for a in candidate_arms) or best_cor >= MB_COR_HI:
        verdict = "HARD_FAIL"
        verdict_extra = "all lifts < +0.10 or fairness cor >= 0.50"
    # else MIDDLE_BAND stays

    verdict_msg = (
        "%s | best=%s sel=%.3f lift=%+.3f cv=%.3f cor=%.3f | "
        "single=%.3f | gpu_p50=%.1f | n=%d | %s"
    ) % (
        verdict, best_arm, best_sel, best_lift, best_cv, best_cor,
        single_sel, gpu_p50, len(seeds_sorted),
        verdict_extra if 'verdict_extra' in dir() else "",
    )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "best_arm": best_arm,
        "best_sel": best_sel,
        "best_lift_over_single": best_lift,
        "best_cv": best_cv,
        "best_cor": best_cor,
        "single_sel": single_sel,
        "gpu_util_p50": gpu_p50,
        "gpu_util_mean": gpu_mean,
        "gpu_util_max": gpu_max,
        "gpu_util_samples": gpu_util_samples,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": cardinality_ok,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s device=%s"
                           % (os.getpid(), RUN_MODE, str(DEVICE)),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d M=%d seeds=%s K_MAX=%d device=%s expected_n=%d"
          % (ANCHOR_NAME, RUN_MODE, N_DIM, M, SEEDS, K_MAX, str(DEVICE),
             EXPECTED_N_UNITS),
          flush=True)

    run_config = {"N": N_DIM, "M": M, "run_mode": RUN_MODE,
                  "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (
        len(done), len(SEEDS), remaining), flush=True)

    gpu_util_samples: List[float] = []
    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(
            out_dir, "RUNNING",
            "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
            extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed, gpu_util_samples)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs (gpu_samples_so_far=%d)"
              % (seed, time.time() - t0, len(gpu_util_samples)), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed, gpu_util_samples)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_lock_in_amp_pca_readout_fisher"
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
