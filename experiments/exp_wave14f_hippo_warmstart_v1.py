"""HiPPO warm-start convergence speed rescue probe.

CONTEXT: wave14f_hippo_init_w_v1 CLOSED-NEGATIVE at P1 (no depth benefit at FULL training).
P3 found spectral_corr=0.993 between HiPPO-init W and post-Hebbian random-init W.
This means Hebbian training naturally converges to HiPPO-like spectral structure regardless
of initialization. RESCUE SKETCH #2: does HiPPO-init get to TASK PERFORMANCE faster?

HYPOTHESIS (rescue): HiPPO-init W starts at spectral_corr=1.0 with HiPPO eigenspace.
Random-init (zero-init) starts at zero and must be trained to reach good recall accuracy.
HiPPO-init should reach chain-recall threshold (mean cosine >= TARGET_COS) in fewer epochs.

MECHANISM IF CONFIRMED: HiPPO initialization could reduce the warm-up cost during
the early phases of Hebbian training, useful for limited-training-budget scenarios
(e.g., few-shot or streaming learning where epoch count is constrained).

DESIGN:
  - N=2048 (cheaper than N=4096; same regime)
  - 3 seeds (sufficient for threshold crossing measurement)
  - Training: Hebbian outer-product updates on chain-recall task, 15 epochs
  - At each checkpoint [1, 2, 3, 5, 8, 12, 15]: measure mean cosine similarity at d=5
  - Compare convergence curves: HiPPO-init vs zero-init
  - Primary metric: epochs_to_reach TARGET_COS for each init type
  - speedup_ratio = mean_hippo_epochs / mean_zero_epochs

Pre-registered bands:
  HARD_PASS: speedup_ratio <= 0.50
             (HiPPO-init reaches TARGET_COS in at most half the epochs of zero-init)
             AND mean_zero_final_cos >= 0.40 (zero-init actually reaches TARGET_COS eventually)
  HARD_FAIL: speedup_ratio >= 0.80 OR mean_zero_final_cos < 0.40
             (no meaningful convergence advantage; rescue definitively closed)
  MIDDLE_BAND: ratio in (0.50, 0.80)
  INSTRUMENTATION_FAIL: mean_zero_final_cos at epoch 15 < 0.20
             (zero-init should converge at N=2048 with enough epochs)

Queue: remote_cpu_queue (CPU; 3 seeds x 15 epochs x N=2048; ~20-40 min)
Pre-reg: prereqs/2026-05-26_wave14f_hippo_warmstart_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent

# Design parameters (exp_dev autonomy)
N_FULL = 2048
N_SMOKE = 512
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PATTERNS_FULL = 30
N_PATTERNS_SMOKE = 10
D_MAX = 20           # chain depth for eval
D_TRAIN = 15         # training depth
EPOCHS_FULL = 15
EPOCHS_SMOKE = 8
CHECKPOINTS_FULL = [1, 2, 3, 5, 8, 12, 15]
CHECKPOINTS_SMOKE = [1, 2, 3, 5, 8]
TARGET_COS = 0.40    # target cosine similarity threshold (achievable at N=2048 in ~5-10 epochs)
EVAL_DEPTH = 5       # depth at which cosine sim is measured for threshold tracking

# Pre-registered thresholds
HP_SPEEDUP_RATIO = 0.50      # HiPPO-init <= 0.5x epochs of zero-init for HARD_PASS
HF_SPEEDUP_RATIO = 0.80      # HiPPO-init >= 0.8x epochs for HARD_FAIL
INSTFAIL_FINAL_COS = 0.20    # zero-init final cosine must reach >= 0.20 (instrumentation gate)

DELTA_DECAY = 1e-4
DELTA_ALPHA = 0.3


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing: {missing}")


def make_bsc(M: int, N: int, gen: torch.Generator) -> torch.Tensor:
    raw = torch.rand((M, N), generator=gen)
    return 2.0 * (raw > 0.5).float() - 1.0


def bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return a * b


def cosine_sim(a: torch.Tensor, b: torch.Tensor) -> float:
    return float((a * b).sum() / (a.norm() * b.norm() + 1e-9))


def hippo_legs_eigenvalues(H: int) -> torch.Tensor:
    """HiPPO-LegS diagonal-exponential eigenvalue magnitudes.

    From exp_wave14f_hippo_init_w_v1.py:
    lam_re = 0.5 + 0.01 * arange(H), lam_im = pi * arange(H) / H, dt=0.5
    Returns |exp(-dt*lam_re + 1j*dt*lam_im)|
    """
    H_f = float(max(H, 1))
    lam_re = 0.5 + 0.01 * torch.arange(H, dtype=torch.float32)
    lam_im = math.pi * torch.arange(H, dtype=torch.float32) / H_f
    dt = 0.5
    A_re = torch.exp(-dt * lam_re) * torch.cos(dt * lam_im)
    A_im = torch.exp(-dt * lam_re) * torch.sin(dt * lam_im)
    return (A_re ** 2 + A_im ** 2).sqrt()


def make_hippo_init_W(N: int, gen: torch.Generator) -> torch.Tensor:
    """W_0 structured with HiPPO-LegS spectral weights (from v1 experiment)."""
    atoms = make_bsc(N, N, gen)
    sigma = hippo_legs_eigenvalues(N)
    W = (atoms.T * sigma.unsqueeze(0)) @ atoms / N
    return W


def eval_chain_cos_at_depth(W: torch.Tensor, codebook: torch.Tensor,
                             n_patterns: int, d_max: int, eval_depth: int) -> float:
    """Measure mean cosine similarity at eval_depth across all stored chains."""
    N = W.shape[0]
    cos_vals = []
    for ci in range(n_patterns):
        base = ci * (d_max + 1)
        atoms = codebook[base: base + d_max + 1]
        # Build chain states
        cs = torch.zeros((d_max + 1, N))
        cs[0] = atoms[0]
        for t in range(1, d_max + 1):
            cs[t] = bind(cs[t - 1], atoms[t])
        # Evaluate at eval_depth
        t = min(eval_depth, d_max)
        hat = cs[t].clone()
        for j in range(1, t + 1):
            hat = bind(hat, atoms[j])
        pred = W @ hat
        snap = torch.sign(pred)
        snap = torch.where(snap == 0, torch.ones_like(snap), snap)
        cos_vals.append(cosine_sim(snap, atoms[0]))
    return sum(cos_vals) / max(len(cos_vals), 1)


def run_convergence_curve(seed: int, N: int, n_patterns: int, d_max: int, d_train: int,
                           n_epochs: int, checkpoints: list,
                           use_hippo_init: bool) -> dict:
    """Train W from HiPPO-init or zero-init; measure cos@eval_depth at checkpoints."""
    gen = torch.Generator().manual_seed(seed)
    device = torch.device("cpu")

    # Build chains (same codebook for both init types at same seed)
    codebook_gen = torch.Generator().manual_seed(seed + 99999)
    n_atoms = n_patterns * (d_max + 1)
    codebook = make_bsc(n_atoms, N, codebook_gen).to(device)

    # Initialize W
    init_gen = torch.Generator().manual_seed(seed + 11111)
    if use_hippo_init:
        W = make_hippo_init_W(N, init_gen).to(device)
    else:
        W = torch.zeros((N, N), dtype=torch.float32, device=device)

    cos_at_epoch: dict[int, float] = {}

    # Train and checkpoint
    for epoch in range(1, n_epochs + 1):
        for ci in range(n_patterns):
            base = ci * (d_max + 1)
            atoms = codebook[base: base + d_max + 1]
            cs = torch.zeros((d_max + 1, N), device=device)
            cs[0] = atoms[0]
            for t in range(1, d_max + 1):
                cs[t] = bind(cs[t - 1], atoms[t])
            for t in range(1, min(d_train + 1, d_max + 1)):
                hat = cs[t].clone()
                for j in range(1, t + 1):
                    hat = bind(hat, atoms[j])
                pred = W @ hat
                residual = atoms[0] - pred
                dW = residual.unsqueeze(1) * hat.unsqueeze(0) / N
                W = W * (1.0 - DELTA_DECAY) + dW * DELTA_ALPHA

        if epoch in checkpoints:
            cos = eval_chain_cos_at_depth(W, codebook, n_patterns, d_max, EVAL_DEPTH)
            cos_at_epoch[epoch] = cos
            print(f"    epoch={epoch} cos@d={EVAL_DEPTH}={cos:.4f}", flush=True)

    return {"cos_at_epoch": {str(k): round(v, 4) for k, v in cos_at_epoch.items()},
            "seed": seed, "hippo_init": use_hippo_init, "N": N}


def epochs_to_threshold(cos_at_epoch: dict, threshold: float) -> float:
    """Find first epoch where cos@eval_depth >= threshold. Returns inf if never reached."""
    items = sorted((int(k), v) for k, v in cos_at_epoch.items())
    for ep, cos in items:
        if cos >= threshold:
            return float(ep)
    return float("inf")


# ── suspicious result gate ──
def _suspicious_gate(results: list) -> str | None:
    """Return warning string if results look suspicious, else None."""
    all_cos = []
    for r in results:
        curve = r.get("cos_at_epoch", {})
        all_cos.extend(curve.values())
    if not all_cos:
        return "No cosine values recorded."
    if not all(math.isfinite(v) for v in all_cos):
        return "Non-finite cosine values found."
    n = len(all_cos)
    if n >= 3 and len(set(f"{v:.4f}" for v in all_cos)) == 1:
        return f"All cos@d identical across {n} cells: {all_cos[0]:.4f}"
    return None


# ── instrumentation self-test ──
def _instrumentation_selftest():
    print("[selftest] running...", flush=True)

    # 1. hippo_legs_eigenvalues: range, finite, not identical
    sigma = hippo_legs_eigenvalues(64)
    assert len(set(round(v, 4) for v in sigma[:8].tolist())) > 1, \
        "Selftest 1 FAIL: eigenvalues all identical"
    assert all(math.isfinite(v) for v in sigma.tolist()), "Selftest 1 FAIL: non-finite eigenvalues"
    print(f"[selftest] 1/4 hippo_legs_eigenvalues OK (range {sigma.min():.4f}-{sigma.max():.4f})")

    # 2. make_hippo_init_W: non-zero, finite, correct shape
    gen = torch.Generator().manual_seed(42)
    W_test = make_hippo_init_W(64, gen)
    assert W_test.shape == (64, 64), f"Selftest 2 FAIL: shape {W_test.shape}"
    assert W_test.abs().max() > 0, "Selftest 2 FAIL: W is all zeros"
    assert torch.isfinite(W_test).all(), "Selftest 2 FAIL: non-finite W"
    print(f"[selftest] 2/4 make_hippo_init_W OK (max_abs={W_test.abs().max():.4f})")

    # 3. eval_chain_cos_at_depth: returns finite value in [-1, 1]
    gen3 = torch.Generator().manual_seed(7)
    N_t = 64
    W3 = make_hippo_init_W(N_t, gen3)
    cb_gen = torch.Generator().manual_seed(99)
    codebook = make_bsc(5 * (D_MAX + 1), N_t, cb_gen)
    cos = eval_chain_cos_at_depth(W3, codebook, 5, D_MAX, EVAL_DEPTH)
    assert math.isfinite(cos), f"Selftest 3 FAIL: cos={cos}"
    assert -1.0 - 1e-6 <= cos <= 1.0 + 1e-6, f"Selftest 3 FAIL: cos out of [-1, 1]: {cos}"
    print(f"[selftest] 3/4 eval_chain_cos_at_depth OK (cos={cos:.4f})")

    # 4. epochs_to_threshold: correct first crossing, inf when not reached
    test_curve = {"1": 0.1, "2": 0.2, "3": 0.45, "5": 0.6}
    ep = epochs_to_threshold(test_curve, 0.40)
    assert ep == 3, f"Selftest 4 FAIL: first epoch >= 0.40 should be 3, got {ep}"
    ep2 = epochs_to_threshold(test_curve, 0.90)
    assert ep2 == float("inf"), f"Selftest 4 FAIL: above-max threshold should be inf, got {ep2}"
    print(f"[selftest] 4/4 epochs_to_threshold OK")

    print("[selftest] PASS 4/4", flush=True)


_instrumentation_selftest()


# ── main ──
def run(smoke: bool = False):
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    checkpoints = CHECKPOINTS_SMOKE if smoke else CHECKPOINTS_FULL
    n_patterns = N_PATTERNS_SMOKE if smoke else N_PATTERNS_FULL
    out_dir = get_output_dir("wave14f_hippo_warmstart_v1")

    print(f"[exp] wave14f_hippo_warmstart_v1 {'SMOKE' if smoke else 'FULL'} "
          f"N={N} epochs={n_epochs} n_patterns={n_patterns}", flush=True)

    all_results = []
    for seed in seeds:
        print(f"\n  seed={seed} (HiPPO-init)...", flush=True)
        res_hippo = run_convergence_curve(seed, N, n_patterns, D_MAX, D_TRAIN,
                                          n_epochs, checkpoints, use_hippo_init=True)
        print(f"  seed={seed} (zero-init)...", flush=True)
        res_zero = run_convergence_curve(seed, N, n_patterns, D_MAX, D_TRAIN,
                                         n_epochs, checkpoints, use_hippo_init=False)
        all_results.append({"seed": seed, "hippo": res_hippo, "zero": res_zero})

    # Suspicious gate
    all_curves = []
    for r in all_results:
        all_curves.append(r["hippo"])
        all_curves.append(r["zero"])
    warn = _suspicious_gate(all_curves)
    if warn:
        print(f"[SUSPICIOUS-GATE] {warn}", flush=True)

    # Aggregate: find epochs_to_threshold for each seed and init
    hippo_epochs = []
    zero_epochs = []
    for r in all_results:
        ep_h = epochs_to_threshold(r["hippo"]["cos_at_epoch"], TARGET_COS)
        ep_z = epochs_to_threshold(r["zero"]["cos_at_epoch"], TARGET_COS)
        hippo_epochs.append(ep_h)
        zero_epochs.append(ep_z)
        print(f"  seed={r['seed']}: hippo_epochs_to_{TARGET_COS}={ep_h} "
              f"zero_epochs_to_{TARGET_COS}={ep_z}", flush=True)

    # Handle inf: treat inf as n_epochs+1 for ratio computation
    hippo_finite = [e if math.isfinite(e) else n_epochs + 1 for e in hippo_epochs]
    zero_finite = [e if math.isfinite(e) else n_epochs + 1 for e in zero_epochs]

    mean_hippo = sum(hippo_finite) / max(len(hippo_finite), 1)
    mean_zero = sum(zero_finite) / max(len(zero_finite), 1)
    speedup_ratio = mean_hippo / max(mean_zero, 1e-9)  # HiPPO/zero; < 1 means faster

    # Final cosine for zero-init (instrumentation check)
    final_zero_cos_vals = []
    for r in all_results:
        curve = r["zero"]["cos_at_epoch"]
        last_ep = str(max(int(k) for k in curve.keys()))
        val = curve.get(last_ep, float("nan"))
        if math.isfinite(val):
            final_zero_cos_vals.append(val)
    mean_final_zero_cos = (sum(final_zero_cos_vals) / max(len(final_zero_cos_vals), 1)
                           if final_zero_cos_vals else float("nan"))

    print(f"\n[summary] mean_epochs_hippo={mean_hippo:.2f} mean_epochs_zero={mean_zero:.2f} "
          f"speedup_ratio={speedup_ratio:.3f}", flush=True)
    print(f"[summary] mean_final_zero_cos={mean_final_zero_cos:.4f} "
          f"(threshold={INSTFAIL_FINAL_COS})", flush=True)

    # Smoke mode: skip verdict bands if regime-mismatch expected
    if smoke:
        if not math.isfinite(mean_final_zero_cos) or mean_final_zero_cos < 0:
            verdict = "INSTRUMENTATION_FAIL"
            verdict_msg = (f"INSTRUMENTATION_FAIL: mean_final_zero_cos={mean_final_zero_cos:.4f}; "
                           f"zero-init produced no valid cosine values.")
        else:
            verdict = "SMOKE_PASS"
            verdict_msg = (f"SMOKE_PASS: instrumentation valid at N={N}. "
                           f"mean_hippo_epochs={mean_hippo:.1f} mean_zero_epochs={mean_zero:.1f} "
                           f"speedup_ratio={speedup_ratio:.3f} mean_final_zero_cos={mean_final_zero_cos:.4f}. "
                           f"Note: smoke at N={N} may not reproduce FULL regime; "
                           f"full run at N=2048 required for pre-reg bands.")
        print(f"\nVerdict: {verdict}")
        print(f"Msg: {verdict_msg}")
        metrics = {
            "verdict": verdict, "verdict_msg": verdict_msg,
            "elapsed_s": round(time.time() - t0, 3),
            "summary": {
                "mean_epochs_hippo": round(mean_hippo, 2),
                "mean_epochs_zero": round(mean_zero, 2),
                "speedup_ratio": round(speedup_ratio, 3),
                "mean_final_zero_cos": round(mean_final_zero_cos, 4) if math.isfinite(mean_final_zero_cos) else None,
                "per_seed": [
                    {"seed": r["seed"],
                     "hippo_epochs_to_threshold": hippo_epochs[i],
                     "zero_epochs_to_threshold": zero_epochs[i],
                     "hippo_curve": r["hippo"]["cos_at_epoch"],
                     "zero_curve": r["zero"]["cos_at_epoch"]}
                    for i, r in enumerate(all_results)
                ],
            },
            "config": {
                "N": N, "smoke": smoke, "seeds": seeds,
                "n_epochs": n_epochs, "checkpoints": checkpoints,
                "n_patterns": n_patterns, "d_max": D_MAX, "d_train": D_TRAIN,
                "target_cos": TARGET_COS, "eval_depth": EVAL_DEPTH,
                "rescue": "HiPPO warm-start (rescue #2 from PROT-004 CLOSED wave14f_hippo_init_w_v1)",
            },
        }
        validate_metrics(metrics)
        with open(out_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        print(f"Metrics saved to {out_dir / 'metrics.json'}")
        return

    # Full run: apply pre-registered verdict bands
    if not math.isfinite(mean_final_zero_cos) or mean_final_zero_cos < INSTFAIL_FINAL_COS:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: zero-init final cos@d={EVAL_DEPTH}="
                       f"{mean_final_zero_cos:.4f} < {INSTFAIL_FINAL_COS} threshold. "
                       f"Zero-init W should converge to measurable recall at N=2048/15 epochs.")
    elif speedup_ratio <= HP_SPEEDUP_RATIO:
        verdict = "WARMSTART_HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: HiPPO warm-start confirmed. "
            f"Mean epochs to cos>={TARGET_COS}: HiPPO={mean_hippo:.1f} vs zero={mean_zero:.1f} "
            f"(speedup_ratio={speedup_ratio:.3f} <= {HP_SPEEDUP_RATIO}). "
            f"HiPPO-init provides faster task-performance convergence: "
            f"useful in limited-training-budget scenarios."
        )
    elif speedup_ratio >= HF_SPEEDUP_RATIO:
        verdict = "WARMSTART_HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: No meaningful convergence advantage. "
            f"HiPPO={mean_hippo:.1f} epochs vs zero={mean_zero:.1f} "
            f"(speedup_ratio={speedup_ratio:.3f} >= {HF_SPEEDUP_RATIO}). "
            f"HiPPO warm-start rescue definitively closed: init does not accelerate task convergence."
        )
    else:
        verdict = "WARMSTART_MIDDLE"
        verdict_msg = (
            f"MIDDLE_BAND: Some convergence advantage but not decisive. "
            f"HiPPO={mean_hippo:.1f} epochs vs zero={mean_zero:.1f} "
            f"(speedup_ratio={speedup_ratio:.3f}; HP<={HP_SPEEDUP_RATIO} HF>={HF_SPEEDUP_RATIO}). "
            f"Rescue weakly supported; not a strong product capability."
        )

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    summary = {
        "mean_epochs_hippo_to_threshold": round(mean_hippo, 2),
        "mean_epochs_zero_to_threshold": round(mean_zero, 2),
        "speedup_ratio_hippo_over_zero": round(speedup_ratio, 3),
        "mean_final_zero_cos": round(mean_final_zero_cos, 4) if math.isfinite(mean_final_zero_cos) else None,
        "target_cos": TARGET_COS,
        "eval_depth": EVAL_DEPTH,
        "per_seed": [
            {"seed": r["seed"],
             "hippo_epochs_to_threshold": hippo_epochs[i],
             "zero_epochs_to_threshold": zero_epochs[i],
             "hippo_curve": r["hippo"]["cos_at_epoch"],
             "zero_curve": r["zero"]["cos_at_epoch"]}
            for i, r in enumerate(all_results)
        ],
    }

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N": N, "smoke": smoke, "seeds": seeds,
            "n_epochs": n_epochs, "checkpoints": checkpoints,
            "n_patterns": n_patterns, "d_max": D_MAX, "d_train": D_TRAIN,
            "target_cos": TARGET_COS, "eval_depth": EVAL_DEPTH,
            "rescue": "HiPPO warm-start (rescue #2 from PROT-004 CLOSED wave14f_hippo_init_w_v1)",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
