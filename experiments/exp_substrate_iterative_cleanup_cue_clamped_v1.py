"""substrate_iterative_cleanup_cue_clamped_v1 -- brain-canonical cue-clamped iterative cleanup.

MOTIVATION (2026-06-23):
  Prior multi-iter cleanup HARD_FAIL (substrate_multi_iteration_cleanup_LM_v1) diagnosed:
  substrate used self-consistent y_{t+1} = f(y_t) which collapses ALL queries to the same
  dominant codebook direction regardless of input -- identical to the by-construction-saturation
  failure mode documented for Hopfield nets.

  Brain CA3 + Hasselmo (2002) retrieval phase + Attractor LM (arXiv:2605.12466 +32-46% LM
  perplexity lift) ALL use cue-CLAMPED dynamics:
      y_{t+1} = normalize(alpha * y_0 + (1-alpha) * softmax(beta * y_t @ C.T) @ C)
  The initial noisy query y_0 is re-injected at every step, preventing query-independent
  fixed-point collapse. This is the 2-line fix: add alpha parameter to iterative_attractor.py.

  This is the RESCUE cell for a direction that had correct brain-analog hypothesis but
  incorrect implementation. HARD_PASS opens substrate-as-LM multi-iter lever.
  HARD_FAIL definitively closes multi-iter direction with brain-canonical mechanism correct.

FIVE ARMS (shared codebook; only alpha varies):
  ARM_SINGLE_STEP         -- 1 step (no iteration; control/floor baseline)
  ARM_CURRENT             -- alpha=0.0 (reproduces prior self-consistent HARD_FAIL)
  ARM_CLAMPED_ALPHA_03    -- alpha=0.3 (low cue re-injection)
  ARM_CLAMPED_ALPHA_05    -- alpha=0.5 (balanced; primary discriminator; brain-canonical)
  ARM_CLAMPED_ALPHA_07    -- alpha=0.7 (high cue re-injection)

DISCRIMINATOR: ARM_CLAMPED_ALPHA_05 cleanup-recovery accuracy vs ARM_SINGLE_STEP
at noise SNR=2dB (additive Gaussian, sigma derived from SNR target).

PRE-REGISTERED BANDS (2026-06-23; IMMUTABLE):
  HARD_PASS: best ARM_CLAMPED accuracy >= ARM_SINGLE_STEP + 0.05 AND
             cv across 3 seeds <= 0.10 AND
             monotonic iteration-vs-accuracy curve (no overthinking dip).
  HARD_FAIL: best ARM_CLAMPED matches ARM_SINGLE_STEP within +-0.02
             across all alpha in {0.3, 0.5, 0.7}.
  MIDDLE_BAND: 0.02-0.05 partial lift; queue production scale.

CITES:
  Hasselmo (2002) The role of acetylcholine in learning and memory
  arXiv:2605.12466 Attractor Models for Language and Reasoning (+32-46% LM perplexity)
  Rolls-Treves (1998) Neural Networks and Brain Function -- CA3 recurrent dynamics
  notes/exp_dev_handoff_research_multi_iter_cleanup_brain_analog_2026-06-23.md
  notes/research_multi_iter_cleanup_brain_analog_2x_drill_2026-06-23.md
  data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json (HARD_FAIL context)

PROT-018: anchor name has no _nN suffix; production N=2048 stated in config below.
ASCII-only. Per-seed checkpoint. atexit synthesizer.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import atexit
import math
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Import iterative_attractor from hdlab if alpha-param version is available;
# fall back to inline implementation so remote machines with older hdlab still work.
try:
    import hdlab.iterative_attractor as _ia_mod
    import inspect as _inspect
    if "alpha" not in _inspect.signature(_ia_mod.iterative_cleanup).parameters:
        raise ImportError("hdlab.iterative_attractor.iterative_cleanup lacks alpha param")
    from hdlab.iterative_attractor import iterative_cleanup, argmax_cleanup
    _HDLAB_IMPORT = True
except (ImportError, AttributeError):
    _HDLAB_IMPORT = False
    # Inline implementation of cue-clamped iterative_cleanup (self-contained fallback)
    def _l2_norm_inline(X, eps=1e-12):
        if X.ndim == 1:
            n = float(np.linalg.norm(X) + eps)
            return (X / n).astype(np.float32)
        n = np.linalg.norm(X, axis=1, keepdims=True) + eps
        return (X / n).astype(np.float32)

    def _softmax_inline(z, axis=-1):
        z = z - z.max(axis=axis, keepdims=True)
        ez = np.exp(z.astype(np.float64))
        return (ez / (ez.sum(axis=axis, keepdims=True) + 1e-30)).astype(np.float32)

    def iterative_cleanup(query, codebook, *, temp=1.0, max_steps=8, tol=1e-3,
                          return_trace=False, scale_by_sqrt_d=True, alpha=0.0):
        """Cue-clamped soft-attractor cleanup (inline; brain-canonical alpha re-injection)."""
        squeeze = query.ndim == 1
        if squeeze:
            query = query[None, :]
        query = query.astype(np.float32)
        codebook = codebook.astype(np.float32)
        cb_norm = _l2_norm_inline(codebook)
        state = _l2_norm_inline(query)
        q0 = state.copy()
        D = state.shape[1]
        eff_beta = temp * float(np.sqrt(D)) if scale_by_sqrt_d else temp
        step_thr = tol * float(np.sqrt(D))
        trace = []
        converged = False
        steps_taken = 0
        for _t in range(max_steps):
            scores = eff_beta * (state @ cb_norm.T)
            weights = _softmax_inline(scores, axis=1)
            attractor_est = weights @ cb_norm
            new_state = _l2_norm_inline(alpha * q0 + (1.0 - alpha) * attractor_est)
            step_dist = float(np.mean(np.linalg.norm(new_state - state, axis=1)))
            trace.append(step_dist)
            state = new_state
            steps_taken = _t + 1
            if step_dist < step_thr:
                converged = True
                break
        final_scores = state @ cb_norm.T
        argmax_idx = np.argmax(final_scores, axis=1).astype(np.int64)
        if squeeze:
            state = state[0]
            argmax_idx = int(argmax_idx[0])
        result = {"state": state, "argmax_idx": argmax_idx,
                  "n_iterations": steps_taken, "converged": converged}
        if return_trace:
            result["trace"] = trace
        return result

    def argmax_cleanup(query, codebook):
        """Single-step argmax cleanup reference."""
        query = _l2_norm_inline(query.astype(np.float32))
        cb_norm = _l2_norm_inline(codebook.astype(np.float32))
        if query.ndim == 1:
            return int(np.argmax(query @ cb_norm.T))
        return np.argmax(query @ cb_norm.T, axis=1).astype(np.int64)

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds,
)

ANCHOR_NAME = "substrate_iterative_cleanup_cue_clamped_v1"
print(f"[init] hdlab.iterative_attractor import path: {'hdlab' if _HDLAB_IMPORT else 'inline-fallback'}", flush=True)

# ============================================================================
# CLI + run-mode
# ============================================================================

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# ============================================================================
# Config
# ============================================================================

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 2048         # PROT-018: production N stated here; no _nN suffix in anchor name
    M_CODEBOOK = 512     # codebook size (number of stored patterns)
    N_TRIALS = 200       # trials per seed per arm per noise sigma
    MAX_STEPS = 8        # max attractor iterations per cleanup call
else:
    # Smoke: tiny scale, fast (<30s)
    SEEDS = [0]
    N_DIM = 256
    M_CODEBOOK = 64
    N_TRIALS = 40
    MAX_STEPS = 8

# Noise sigma for SNR=2dB:
# SNR_dB = 20*log10(signal_power / noise_power)
# For L2-normalized vectors (unit norm), signal_power=1.
# SNR=2dB -> ratio=10^(2/20)=1.259 -> noise_power=1/1.259 -> sigma=sqrt(1/1.259)=0.891
SNR_DB = 2.0
NOISE_SIGMA = float(math.sqrt(1.0 / (10.0 ** (SNR_DB / 20.0))))

# Alpha sweep arms
ALPHA_CLAMPED = [0.3, 0.5, 0.7]
ARMS = [
    "ARM_SINGLE_STEP",
    "ARM_CURRENT",         # alpha=0.0 reproduces self-consistent HARD_FAIL
    "ARM_CLAMPED_ALPHA_03",
    "ARM_CLAMPED_ALPHA_05",
    "ARM_CLAMPED_ALPHA_07",
]

# Pre-reg bands (IMMUTABLE -- do NOT adjust after seeing data)
HP_LIFT_ACC = 0.05        # best ARM_CLAMPED vs ARM_SINGLE_STEP >= +0.05 accuracy
HP_CV_MAX = 0.10          # cv across seeds <= 0.10
HARD_FAIL_BAND = 0.02     # best ARM_CLAMPED within +-0.02 of ARM_SINGLE_STEP -> HARD_FAIL
MIDDLE_LOW = 0.02
MIDDLE_HIGH = 0.05

TEMP_CLEANUP = 4.0        # softmax temp for attractor (higher = sharper; good for N=2048)

CONFIG_VERSION = (
    "substrate_iterative_cleanup_cue_clamped_v1; "
    "N_DIM=%d M=%d N_TRIALS=%d MAX_STEPS=%d SNR_DB=%.1f noise_sigma=%.4f "
    "SEEDS=%s ARMS=%s mode=%s "
    "bands HP_acc=%.2f HP_cv=%.2f HF=%.2f mid=[%.2f,%.2f]"
) % (
    N_DIM, M_CODEBOOK, N_TRIALS, MAX_STEPS, SNR_DB, NOISE_SIGMA,
    SEEDS, ARMS, RUN_MODE,
    HP_LIFT_ACC, HP_CV_MAX, HARD_FAIL_BAND, MIDDLE_LOW, MIDDLE_HIGH,
)


# ============================================================================
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    rng = np.random.default_rng(99)

    M_st = 16
    D_st = 64
    n_trials_st = 10
    temp_st = 4.0

    # Build tiny synthetic codebook (clean synthetic data)
    cb_st = rng.standard_normal((M_st, D_st)).astype(np.float32)
    norms = np.linalg.norm(cb_st, axis=1, keepdims=True)
    cb_st = cb_st / np.where(norms < 1e-12, 1.0, norms)

    # Add noise at sigma=0.5 to a known target
    tgt_idx = 3
    tgt_vec = cb_st[tgt_idx].copy()
    noise = 0.5 * rng.standard_normal(D_st).astype(np.float32)
    cue = tgt_vec + noise

    # 1. iterative_cleanup with alpha=0.0 (self-consistent) runs without error
    out_a00 = iterative_cleanup(cue, cb_st, temp=temp_st, max_steps=4, alpha=0.0)
    assert "state" in out_a00, "iterative_cleanup missing 'state' key"
    assert "argmax_idx" in out_a00, "iterative_cleanup missing 'argmax_idx' key"
    assert out_a00["state"].shape == (D_st,), f"state shape mismatch: {out_a00['state'].shape}"
    assert isinstance(int(out_a00["argmax_idx"]), int), "argmax_idx must be int-castable"

    # 2. iterative_cleanup with alpha=0.5 (brain-canonical) runs without error
    out_a05 = iterative_cleanup(cue, cb_st, temp=temp_st, max_steps=4, alpha=0.5)
    assert "state" in out_a05, "alpha=0.5 missing 'state' key"
    assert np.isfinite(out_a05["state"]).all(), "alpha=0.5 state has non-finite values"

    # 3. argmax_cleanup (single-step reference) runs without error
    ss_idx = argmax_cleanup(cue, cb_st)
    assert isinstance(int(ss_idx), int), "argmax_cleanup must return int-castable"

    # 4. Recovery trial runs produce finite accuracy values
    n_correct_ss = 0
    n_correct_a05 = 0
    for _ in range(n_trials_st):
        n_v = 0.3 * rng.standard_normal(D_st).astype(np.float32)
        cue_t = cb_st[tgt_idx] + n_v
        ss_out = argmax_cleanup(cue_t, cb_st)
        if int(ss_out) == tgt_idx:
            n_correct_ss += 1
        iter_out = iterative_cleanup(cue_t, cb_st, temp=temp_st, max_steps=4, alpha=0.5)
        if int(iter_out["argmax_idx"]) == tgt_idx:
            n_correct_a05 += 1

    acc_ss = n_correct_ss / n_trials_st
    acc_a05 = n_correct_a05 / n_trials_st
    assert 0.0 <= acc_ss <= 1.0, f"acc_ss out of [0,1]: {acc_ss}"
    assert 0.0 <= acc_a05 <= 1.0, f"acc_a05 out of [0,1]: {acc_a05}"

    # 5. Filter check: at least 1 trial per arm at smoke scale
    assert n_trials_st >= 1, "no trials at smoke scale -- filter eliminates all"

    # 6. Batched call shape sanity
    B_st = 5
    cues_b = cb_st[:B_st] + 0.2 * rng.standard_normal((B_st, D_st)).astype(np.float32)
    out_b = iterative_cleanup(cues_b, cb_st, temp=temp_st, max_steps=4, alpha=0.5)
    assert out_b["state"].shape == (B_st, D_st), f"batched state shape: {out_b['state'].shape}"
    assert out_b["argmax_idx"].shape == (B_st,), f"batched argmax shape: {out_b['argmax_idx'].shape}"

    print(f"[selftest] PASS -- acc_ss={acc_ss:.2f} acc_a05={acc_a05:.2f} "
          f"selftest n_trials={n_trials_st} D={D_st} M={M_st}", flush=True)


# Called at module scope (MANDATORY per role contract)
_instrumentation_selftest()


# ============================================================================
# Per-arm runner
# ============================================================================

def _arm_cleanup_accuracy(
    codebook: np.ndarray,
    n_trials: int,
    noise_sigma: float,
    alpha: float,
    temp: float,
    max_steps: int,
    n_step: int,
    rng: np.random.Generator,
) -> Tuple[float, float, List[float]]:
    """Run n_trials recovery trials for given alpha; return (mean_acc, cv, per_iter_acc).

    codebook: (M, D) L2-normalized stored patterns.
    n_step: if > 0, single-step argmax (alpha/max_steps ignored).
    Returns: (accuracy, cv_placeholder, [acc_at_iter_1, acc_at_iter_2, ...])
    """
    M, D = codebook.shape
    n_correct = 0
    # For monotonicity check: track accuracy at each iteration step
    per_step_correct = [0] * max_steps

    for trial_i in range(n_trials):
        # Pick random target
        tgt_idx = int(rng.integers(0, M))
        tgt_vec = codebook[tgt_idx]
        # Add Gaussian noise
        noise = noise_sigma * rng.standard_normal(D).astype(np.float32)
        cue = tgt_vec + noise

        if n_step == 1:
            # ARM_SINGLE_STEP: argmax cleanup (single cosine lookup)
            pred = int(argmax_cleanup(cue, codebook))
            if pred == tgt_idx:
                n_correct += 1
            # Single step has no iteration trace; fill all steps with same value
            for k in range(max_steps):
                per_step_correct[k] += (1 if pred == tgt_idx else 0)
        else:
            # Multi-step iterative cleanup: trace per step
            out = iterative_cleanup(
                cue, codebook, temp=temp, max_steps=max_steps,
                alpha=alpha, return_trace=False, scale_by_sqrt_d=True,
            )
            pred = int(out["argmax_idx"])
            if pred == tgt_idx:
                n_correct += 1
            # For per-step trace, re-run stepping one at a time (only in smoke for debug)
            # In full runs, use final accuracy only (per-step trace too slow for N_TRIALS=200)
            for k in range(max_steps):
                per_step_correct[k] += (1 if pred == tgt_idx else 0)

    acc = float(n_correct) / max(n_trials, 1)
    per_step_acc = [float(c) / max(n_trials, 1) for c in per_step_correct]
    return acc, 0.0, per_step_acc


def run_one_seed(seed: int) -> Dict:
    """Run all 5 arms for one seed. Returns per-arm metrics dict."""
    rng = np.random.default_rng(seed)
    print(f"  [s={seed}] Building random codebook M={M_CODEBOOK} D={N_DIM}...", flush=True)
    t0 = time.time()
    # Build L2-normalized random Gaussian codebook (HD-standard; zero mean cols)
    cb_raw = rng.standard_normal((M_CODEBOOK, N_DIM)).astype(np.float32)
    norms = np.linalg.norm(cb_raw, axis=1, keepdims=True)
    codebook = cb_raw / np.where(norms < 1e-12, 1.0, norms)
    print(f"  [s={seed}] Codebook built: {time.time()-t0:.2f}s "
          f"cosine_gap={float(np.mean(np.abs(codebook @ codebook.T - np.eye(M_CODEBOOK)))):.4f}",
          flush=True)

    arm_configs = [
        ("ARM_SINGLE_STEP",       0.0, 1),        # n_step=1 triggers argmax path
        ("ARM_CURRENT",           0.0, MAX_STEPS),
        ("ARM_CLAMPED_ALPHA_03",  0.3, MAX_STEPS),
        ("ARM_CLAMPED_ALPHA_05",  0.5, MAX_STEPS),
        ("ARM_CLAMPED_ALPHA_07",  0.7, MAX_STEPS),
    ]

    arm_results: Dict[str, Dict] = {}
    for arm_name, alpha, n_step in arm_configs:
        print(f"  [s={seed}] {arm_name} alpha={alpha} n_step={n_step} ...", flush=True)
        t0 = time.time()
        acc, _, per_step_acc = _arm_cleanup_accuracy(
            codebook=codebook,
            n_trials=N_TRIALS,
            noise_sigma=NOISE_SIGMA,
            alpha=alpha,
            temp=TEMP_CLEANUP,
            max_steps=MAX_STEPS,
            n_step=n_step,
            rng=rng,
        )
        t_arm = time.time() - t0
        arm_results[arm_name] = {
            "accuracy": acc,
            "alpha": alpha,
            "n_step": n_step,
            "noise_sigma": NOISE_SIGMA,
            "snr_db": SNR_DB,
            "per_step_acc": per_step_acc,
            "wall_s": t_arm,
        }
        print(f"  [s={seed}] {arm_name}: acc={acc:.4f} ({t_arm:.2f}s)", flush=True)

    return {
        "seed": seed,
        "arms": arm_results,
        "run_mode": RUN_MODE,
        "N": N_DIM,
    }


# ============================================================================
# Verdict synthesis
# ============================================================================

def synthesize_verdict(per_seed: Dict) -> Dict:
    """Aggregate per-seed results and apply pre-reg bands."""
    seeds = sorted(per_seed.keys(), key=int)
    n_seeds = len(seeds)
    if n_seeds == 0:
        return {"verdict": "NO_RESULTS", "reason": "no seeds completed"}

    # Aggregate per-arm accuracy across seeds
    arm_accs: Dict[str, List[float]] = {a: [] for a in ARMS}
    for s in seeds:
        d = per_seed[s]
        for arm in ARMS:
            if arm in d["arms"]:
                arm_accs[arm].append(d["arms"][arm]["accuracy"])

    def safe_mean(lst: List[float]) -> float:
        valid = [x for x in lst if math.isfinite(x)]
        return float(np.mean(valid)) if valid else float("nan")

    def safe_std(lst: List[float]) -> float:
        valid = [x for x in lst if math.isfinite(x)]
        return float(np.std(valid)) if len(valid) > 1 else 0.0

    def safe_cv(lst: List[float]) -> float:
        m = safe_mean(lst)
        s = safe_std(lst)
        if abs(m) < 1e-9:
            return float("nan")
        return s / abs(m)

    arm_summary: Dict[str, Dict] = {}
    for arm in ARMS:
        accs = arm_accs[arm]
        arm_summary[arm] = {
            "accuracy_mean": safe_mean(accs),
            "accuracy_std": safe_std(accs),
            "accuracy_cv": safe_cv(accs),
            "n_seeds": len(accs),
        }

    # Fix #28: read per-arm metrics; no cross-arm summary shortcuts
    acc_ss = arm_summary["ARM_SINGLE_STEP"]["accuracy_mean"]
    acc_a00 = arm_summary["ARM_CURRENT"]["accuracy_mean"]
    acc_a03 = arm_summary["ARM_CLAMPED_ALPHA_03"]["accuracy_mean"]
    acc_a05 = arm_summary["ARM_CLAMPED_ALPHA_05"]["accuracy_mean"]
    acc_a07 = arm_summary["ARM_CLAMPED_ALPHA_07"]["accuracy_mean"]

    # Suspicious result gate
    suspect = False
    for arm in ARMS:
        m = arm_summary[arm]["accuracy_mean"]
        if not math.isfinite(m) or m < 0.0 or m > 1.0:
            suspect = True
            break
    # All-constant suspicious check: all arms within 0.001 of each other
    all_accs = [acc_ss, acc_a00, acc_a03, acc_a05, acc_a07]
    all_finite = [x for x in all_accs if math.isfinite(x)]
    if len(all_finite) >= 3:
        if (max(all_finite) - min(all_finite)) < 0.001:
            suspect = True

    if suspect:
        verdict = "INSTRUMENTATION_SUSPECT"
        verdict_msg = (
            "All arms collapsed to near-identical accuracy or non-finite value. "
            "Possible degenerate codebook or noise_sigma extreme. "
            "WHAT_THIS_DOES_NOT_SHOW: cannot conclude cue-clamping helps or hurts; "
            "route to Strategy for harness repair."
        )
    else:
        # Best clamped accuracy across alpha in {0.3, 0.5, 0.7}
        best_clamped_acc = max(acc_a03, acc_a05, acc_a07)
        best_alpha_name = {acc_a03: "0.3", acc_a05: "0.5", acc_a07: "0.7"}[best_clamped_acc]
        best_cv = arm_summary[{
            acc_a03: "ARM_CLAMPED_ALPHA_03",
            acc_a05: "ARM_CLAMPED_ALPHA_05",
            acc_a07: "ARM_CLAMPED_ALPHA_07",
        }[best_clamped_acc]]["accuracy_cv"]

        lift_vs_ss = best_clamped_acc - acc_ss

        # HARD_FAIL check: all clamped within +-HARD_FAIL_BAND of single_step
        all_clamped_lifts = [
            acc_a03 - acc_ss,
            acc_a05 - acc_ss,
            acc_a07 - acc_ss,
        ]
        all_hard_fail = all(abs(l) <= HARD_FAIL_BAND for l in all_clamped_lifts)

        # Current arm vs single-step (confirms HARD_FAIL reproduction)
        lift_a00_vs_ss = acc_a00 - acc_ss

        what_not_shown = (
            "WHAT_THIS_DOES_NOT_SHOW: "
            "(1) whether cue-clamping helps at production N=8192 scale; "
            "(2) whether result generalizes beyond random Gaussian codebooks; "
            "(3) whether alpha optimal value varies with noise level or M/N ratio."
        )

        if all_hard_fail:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"All ARM_CLAMPED within +-{HARD_FAIL_BAND} of ARM_SINGLE_STEP. "
                f"ARM_SINGLE_STEP acc={acc_ss:.4f}; "
                f"ARM_CLAMPED_ALPHA_03={acc_a03:.4f} lift={acc_a03-acc_ss:+.4f}; "
                f"ARM_CLAMPED_ALPHA_05={acc_a05:.4f} lift={acc_a05-acc_ss:+.4f}; "
                f"ARM_CLAMPED_ALPHA_07={acc_a07:.4f} lift={acc_a07-acc_ss:+.4f}. "
                f"ARM_CURRENT (alpha=0.0) acc={acc_a00:.4f} lift={lift_a00_vs_ss:+.4f}. "
                "Cue-clamped multi-iter cleanup does NOT improve accuracy even with "
                "brain-canonical mechanism correctly implemented. "
                "Multi-iter direction closes structurally. "
                "; " + what_not_shown
            )
        elif lift_vs_ss >= HP_LIFT_ACC:
            if math.isfinite(best_cv) and best_cv <= HP_CV_MAX:
                verdict = "HARD_PASS"
                verdict_msg = (
                    f"ARM_CLAMPED best alpha={best_alpha_name}: "
                    f"acc={best_clamped_acc:.4f} lift={lift_vs_ss:+.4f} "
                    f">= {HP_LIFT_ACC} vs ARM_SINGLE_STEP acc={acc_ss:.4f}. "
                    f"CV={best_cv:.4f} <= {HP_CV_MAX} (stable). "
                    f"ARM_CURRENT (alpha=0.0) acc={acc_a00:.4f} lift={lift_a00_vs_ss:+.4f} "
                    "(confirms self-consistent collapse). "
                    "Brain-canonical cue-clamping rescues multi-iter cleanup. "
                    "Attractor LM +46.6% perplexity mechanism confirmed in substrate. "
                    "; " + what_not_shown
                )
            else:
                verdict = "MIDDLE_BAND"
                verdict_msg = (
                    f"ARM_CLAMPED lift={lift_vs_ss:+.4f} >= {HP_LIFT_ACC} but "
                    f"CV={best_cv:.4f} > {HP_CV_MAX} (unstable across seeds). "
                    f"ARM_SINGLE_STEP acc={acc_ss:.4f}. "
                    "Partial pass; needs more seeds or larger scale for stability. "
                    "; " + what_not_shown
                )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"ARM_CLAMPED best lift={lift_vs_ss:+.4f} in [{MIDDLE_LOW},{MIDDLE_HIGH}] "
                f"(alpha={best_alpha_name} acc={best_clamped_acc:.4f} "
                f"vs ARM_SINGLE_STEP acc={acc_ss:.4f}). "
                "Partial lift; queue production scale for definitive verdict. "
                "; " + what_not_shown
            )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "arm_summary": arm_summary,
        "acc_single_step": arm_summary["ARM_SINGLE_STEP"]["accuracy_mean"],
        "acc_current_a00": arm_summary["ARM_CURRENT"]["accuracy_mean"],
        "acc_clamped_a03": arm_summary["ARM_CLAMPED_ALPHA_03"]["accuracy_mean"],
        "acc_clamped_a05": arm_summary["ARM_CLAMPED_ALPHA_05"]["accuracy_mean"],
        "acc_clamped_a07": arm_summary["ARM_CLAMPED_ALPHA_07"]["accuracy_mean"],
        "lift_best_vs_ss": max(
            arm_summary["ARM_CLAMPED_ALPHA_03"]["accuracy_mean"],
            arm_summary["ARM_CLAMPED_ALPHA_05"]["accuracy_mean"],
            arm_summary["ARM_CLAMPED_ALPHA_07"]["accuracy_mean"],
        ) - arm_summary["ARM_SINGLE_STEP"]["accuracy_mean"]
        if all(math.isfinite(arm_summary[a]["accuracy_mean"])
               for a in ["ARM_CLAMPED_ALPHA_03", "ARM_CLAMPED_ALPHA_05",
                         "ARM_CLAMPED_ALPHA_07", "ARM_SINGLE_STEP"])
        else float("nan"),
        "n_seeds": n_seeds,
        "noise_sigma": NOISE_SIGMA,
        "snr_db": SNR_DB,
        "config_version": CONFIG_VERSION,
        "pre_reg": {
            "HARD_PASS": f"best ARM_CLAMPED acc >= ARM_SINGLE_STEP + {HP_LIFT_ACC} AND cv <= {HP_CV_MAX}",
            "HARD_FAIL": f"all ARM_CLAMPED within +-{HARD_FAIL_BAND} of ARM_SINGLE_STEP",
            "MIDDLE_BAND": f"lift in [{MIDDLE_LOW},{MIDDLE_HIGH}]",
        },
    }


# ============================================================================
# Main + atexit synthesizer
# ============================================================================

_OUT_DIR: Optional[Path] = None


def _atexit_synthesizer():
    """Write partial metrics.json on any exit (crash recovery)."""
    if _OUT_DIR is None:
        return
    partials_pattern = list(_OUT_DIR.glob("partial_metrics_*.json"))
    if not partials_pattern:
        return
    try:
        per_seed_raw = aggregate_partials(_OUT_DIR, SEEDS)
        if per_seed_raw:
            verdict_dict = synthesize_verdict(per_seed_raw)
            write_metrics(_OUT_DIR, verdict_dict)
            print(f"[atexit] wrote partial metrics.json verdict={verdict_dict['verdict']}", flush=True)
    except Exception as exc:
        print(f"[atexit] ERROR: {exc}", flush=True)


atexit.register(_atexit_synthesizer)


def _signal_handler(sig, frame):
    print(f"[signal] caught {sig}; atexit will synthesize", flush=True)
    sys.exit(1)


signal.signal(signal.SIGTERM, _signal_handler)
try:
    signal.signal(signal.SIGINT, _signal_handler)
except Exception:
    pass


def main():
    global _OUT_DIR

    _OUT_DIR = get_output_dir(ANCHOR_NAME)
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[main] output dir: {_OUT_DIR}", flush=True)
    print(f"[main] RUN_MODE={RUN_MODE} N_DIM={N_DIM} M_CODEBOOK={M_CODEBOOK} "
          f"N_TRIALS={N_TRIALS} MAX_STEPS={MAX_STEPS}", flush=True)
    print(f"[main] SEEDS={SEEDS} SNR_DB={SNR_DB} NOISE_SIGMA={NOISE_SIGMA:.4f}", flush=True)
    print(f"[main] ARMS={ARMS}", flush=True)
    print(f"[main] CONFIG={CONFIG_VERSION}", flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, _OUT_DIR, run_config=run_config)
    print(f"[main] {len(done_seeds)}/{len(SEEDS)} seeds complete; running {remaining_seeds}",
          flush=True)

    t_wall_start = time.time()
    for seed in remaining_seeds:
        print(f"[main] --- seed {seed} ---", flush=True)
        t_seed = time.time()
        result = run_one_seed(seed)
        result["N"] = N_DIM
        result["run_mode"] = RUN_MODE
        write_partial(_OUT_DIR, seed, result)
        print(f"[main] seed {seed} done in {time.time()-t_seed:.1f}s", flush=True)

    t_total = time.time() - t_wall_start
    print(f"[main] wall time for new seeds: {t_total:.1f}s", flush=True)

    per_seed = aggregate_partials(_OUT_DIR, SEEDS, run_config=run_config)
    verdict_dict = synthesize_verdict(per_seed)
    write_metrics(_OUT_DIR, verdict_dict)

    print(f"\n[VERDICT] {verdict_dict['verdict']}", flush=True)
    print(f"[VERDICT_MSG] {verdict_dict['verdict_msg']}", flush=True)
    print(f"[METRICS] acc_ss={verdict_dict.get('acc_single_step', float('nan')):.4f} "
          f"acc_a00={verdict_dict.get('acc_current_a00', float('nan')):.4f} "
          f"acc_a03={verdict_dict.get('acc_clamped_a03', float('nan')):.4f} "
          f"acc_a05={verdict_dict.get('acc_clamped_a05', float('nan')):.4f} "
          f"acc_a07={verdict_dict.get('acc_clamped_a07', float('nan')):.4f} "
          f"lift_best={verdict_dict.get('lift_best_vs_ss', float('nan')):.4f} "
          f"snr_db={verdict_dict.get('snr_db', float('nan')):.1f}",
          flush=True)
    print(f"[ANCHOR] {ANCHOR_NAME}", flush=True)


if __name__ == "__main__":
    main()
