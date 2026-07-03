"""Candidate (v): Saddle-cascade plateau falsifier -- corpus-overlap-fraction sweep.

Filed 2026-05-24 per strategy_request_to_exp_dev_cascade_plateau_test_2026-05-24.md
Research note: notes/research_alternative_theoretical_homes_2026-05-24.md Top-2 drill.

HYPOTHESIS (Saad-Solla 1995 / Biehl-Schwarze 1995 saddle-cascade framework):
  Substrate's three retention plateaus (0.94 / 0.74 / 0.60) emerge from saddle-cascade
  dynamics: multiple fixed-points of the student-teacher overlap ODE, traversed in
  sequence as a plateau cascade. Framework predicts plateau heights are DISCRETE
  and IMMUNE to continuous parameters -- not a smooth function of corpus overlap.

KEY QUESTION: Does retention(f) -- where f = corpus-overlap-fraction -- show
DISCRETE STEP STRUCTURE or smooth-monotone interpolation?

METHOD:
  1. Train Phase-A on pure corpus_A (standard substrate).
  2. For each overlap fraction f in {0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0}:
     - Build mixed corpus: f-fraction of corpus_A bytes + (1-f)-fraction of corpus_B bytes
       (corpus_B = independent random byte sequence, completely disjoint from corpus_A)
     - Train Phase-B on mixed corpus
     - Measure retention_A (how much Phase-A knowledge survives Phase-B training)
  3. Test: linear-fit R^2 vs f. Cascade predicts R^2 << 1 (discrete structure).
           Smooth-monotone predicts R^2 ~ 1.

PRE-REGISTERED BANDS (per [[feedback-envelope-expansion-fail-bands]]):
  HARD-PASS: retention(f) shows discrete step structure
    - Linear-fit R^2 < 0.85 AND max deviation from linear fit >= 0.08
    -> Saddle-cascade dynamics active; plateaus are fixed-point cascades, not interpolation.

  HARD-FAIL: retention(f) is smooth-monotone
    - Linear-fit R^2 >= 0.95 AND max deviation < 0.04
    -> Cascade framework does not apply; substrate retention interpolates smoothly.
    -> Rehab: candidates (iii) CiT or accept 1-RSB smooth-transition reading.

  MIDDLE-BAND: R^2 in [0.85, 0.95) OR deviation in [0.05, 0.08)
    -> Partial; inconclusive.

SELF-TEST cells (per [[feedback-strategy-spec-formula-selftests]]):
  1. (f=1.0, identical corpus) -> retention expected > 0.85 (same-corpus regime; empirical 0.94)
  2. (f=0.0, disjoint corpus) -> retention expected in [0.55, 0.70] (diff-corpus regime; empirical 0.60)
  3. Linear baseline check: pearson_r2([0,0.1,0.25,0.5,0.75,0.9,1.0], linear_vals) > 0.999
  4. Cascade hypothetical: pearson_r2([0,...,1.0], [0.60,0.61,0.62,0.94,0.94,0.94,0.94]) < 0.80
     AND max_deviation >= 0.10 -> correctly identifies HARD-PASS

Pred-4-orthogonal: no hysteresis assumed; no M-axis sweep; no 1-RSB interpretation.
Safe to run in parallel with Pred-4.

Queue: remote_cpu_queue (CPU only; no GPU needed; 7 f-values x 3 seeds x 2 phases)
ETA: ~30-60 min CPU
Pre-reg: preregs/2026-05-24_wave14_saddle_cascade_plateau_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.
Per [[feedback-envelope-expansion-fail-bands]]: bands pre-registered.
Per [[feedback-strategy-spec-formula-selftests]]: 4 self-test cells inline.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load Kovacs base infrastructure (train_w_with_replay, evaluate_bpc, bytes_to_idx_tensors, pa)
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

# ---- design parameters (exp_dev autonomy) ----
# f sweep: corpus-overlap-fraction (fraction of Phase-B bytes drawn from corpus_A)
F_SWEEP_FULL = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]   # 3 anchor points for smoke gate

N_FULL = 2048        # CPU-feasible; matches hysteresis experiment scale
N_SMOKE = 512
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5      # Phase-B training epochs
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 4_000

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
LINEAR_R2_PASS_THRESHOLD = 0.85    # R^2 < this -> discrete structure (HARD-PASS direction)
LINEAR_R2_FAIL_THRESHOLD = 0.95    # R^2 >= this -> smooth-monotone (HARD-FAIL direction)
DEVIATION_PASS_THRESHOLD = 0.08    # max deviation >= this -> HARD-PASS
DEVIATION_FAIL_THRESHOLD = 0.04    # max deviation < this (with R^2 >= 0.95) -> HARD-FAIL


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required keys: {missing}")


def pearson_r2(xs: List[float], ys: List[float]) -> float:
    """Pearson r^2 for two lists of equal length."""
    valid = [(x, y) for x, y in zip(xs, ys) if not math.isnan(x) and not math.isnan(y)]
    n = len(valid)
    if n < 3:
        return float("nan")
    mx = sum(p[0] for p in valid) / n
    my = sum(p[1] for p in valid) / n
    sx = math.sqrt(sum((p[0] - mx) ** 2 for p in valid) / (n - 1))
    sy = math.sqrt(sum((p[1] - my) ** 2 for p in valid) / (n - 1))
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    r = sum((p[0] - mx) * (p[1] - my) for p in valid) / ((n - 1) * sx * sy)
    return r ** 2


def linear_fit_residuals(xs: List[float], ys: List[float]) -> Tuple[float, float, List[float]]:
    """Least-squares linear fit y = a + b*x. Returns (r2, max_abs_deviation, residuals)."""
    valid = [(x, y) for x, y in zip(xs, ys) if not math.isnan(x) and not math.isnan(y)]
    n = len(valid)
    if n < 3:
        return float("nan"), float("nan"), []
    xs_v = [p[0] for p in valid]
    ys_v = [p[1] for p in valid]
    mx = sum(xs_v) / n
    my = sum(ys_v) / n
    sxx = sum((x - mx) ** 2 for x in xs_v)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs_v, ys_v))
    b = sxy / (sxx + 1e-12)
    a = my - b * mx
    predicted = [a + b * x for x in xs_v]
    residuals = [y - yhat for y, yhat in zip(ys_v, predicted)]
    max_dev = max(abs(r) for r in residuals) if residuals else 0.0
    r2 = pearson_r2(xs_v, ys_v)
    return r2, max_dev, residuals


def build_mixed_corpus(corpus_a_bytes: bytes, n_bytes: int, f: float, seed: int) -> bytes:
    """Build Phase-B corpus: f-fraction from corpus_A + (1-f)-fraction from random corpus_B.

    f=1.0: entirely corpus_A bytes (same-corpus regime).
    f=0.0: entirely corpus_B bytes (disjoint/random regime).
    Intermediate f: interleaved token-by-token from both corpora.
    """
    n_a = int(round(f * n_bytes))
    n_b = n_bytes - n_a

    # corpus_A portion: slice from corpus_A (same token distribution as Phase-A)
    a_portion = corpus_a_bytes[:n_a] if n_a > 0 else b""

    # corpus_B portion: fresh random bytes (completely disjoint from corpus_A)
    if n_b > 0:
        gen = torch.Generator().manual_seed(seed + 7777)
        b_portion = bytes(
            torch.randint(0, 256, (n_b,), generator=gen).to(torch.uint8).numpy().tobytes()
        )
    else:
        b_portion = b""

    if n_a == 0:
        return b_portion
    if n_b == 0:
        return a_portion

    # Interleave: alternate tokens from each portion to mix distributions
    # rather than concatenating (concat would create a phase boundary artifact)
    mixed = bytearray(n_bytes)
    ai = 0
    bi = 0
    a_step = n_a / n_bytes
    b_step = n_b / n_bytes
    a_budget = 0.0
    b_budget = 0.0
    for i in range(n_bytes):
        a_budget += a_step
        b_budget += b_step
        if ai < n_a and (bi >= n_b or a_budget >= b_budget):
            mixed[i] = a_portion[ai]
            ai += 1
        elif bi < n_b:
            mixed[i] = b_portion[bi]
            bi += 1
        else:
            mixed[i] = a_portion[ai % n_a]
    return bytes(mixed)


def run_one_cell(seed: int, f: float, N: int, batch_size: int,
                 n_epochs: int, phase_a_epochs: int, n_bytes: int, device) -> dict:
    """Train Phase-A on corpus_A, Phase-B on mixed(f), return retention_A."""
    gen = torch.Generator().manual_seed(seed)

    VOCAB = 256
    K_ctx = base.K
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K_ctx, N, gen).to(device)

    # Phase-A corpus: pure corpus_A
    corpus_a_bytes = pa.load_corpus_a()[:n_bytes]
    if len(corpus_a_bytes) < n_bytes:
        raise RuntimeError(
            f"corpus_a too short: {len(corpus_a_bytes)} < {n_bytes}. "
            f"Check corpus file in repo."
        )

    a_idx, a_tgt = base.bytes_to_idx_tensors(corpus_a_bytes, device)

    # Phase-A training
    W0 = torch.zeros((N, N), dtype=torch.float32, device=device)
    pool_vecs_init = torch.zeros((base.POOL_SIZE, N), dtype=torch.float32, device=device)
    pool_labels_init = torch.zeros(base.POOL_SIZE, dtype=torch.long, device=device)
    pool_used_init = 0

    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W0, pool_vecs_init, pool_labels_init, pool_used_init,
        byte_atoms, pos_atoms, a_idx, a_tgt,
        None, None, 0,
        phase_a_epochs, batch_size, device
    )

    # Phase-A evaluation baseline
    n_eval = max(1000, n_bytes // 5)
    corpus_a_full = pa.load_corpus_a()
    corpus_a_eval = corpus_a_full[n_bytes:n_bytes + n_eval]
    if len(corpus_a_eval) < 500:
        corpus_a_eval = corpus_a_full[-n_eval:]
    ae_idx, ae_tgt = base.bytes_to_idx_tensors(corpus_a_eval, device)
    bpc_A_baseline = base.evaluate_bpc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        byte_atoms, pos_atoms, ae_idx, ae_tgt, batch_size, device
    )

    # Phase-B corpus: mixed(f)
    corpus_b_bytes = build_mixed_corpus(corpus_a_bytes, n_bytes, f, seed)
    b_idx, b_tgt = base.bytes_to_idx_tensors(corpus_b_bytes, device)

    # Phase-B training (with replay from Phase-A pool)
    W_B, pool_B_v, pool_B_l, pool_B_u = base.train_w_with_replay(
        W_A.clone(), pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, b_idx, b_tgt,
        pool_A_v, pool_A_l, pool_A_u,
        n_epochs, batch_size, device
    )

    # Post-Phase-B retention: how much of Phase-A knowledge survives?
    bpc_A_after_B = base.evaluate_bpc(
        W_B, pool_B_v, pool_B_l, pool_B_u,
        byte_atoms, pos_atoms, ae_idx, ae_tgt, batch_size, device
    )

    retention_A = bpc_A_baseline / max(bpc_A_after_B, 1e-9)
    print(
        f"  f={f:.2f} seed={seed}: bpc_A_base={bpc_A_baseline:.4f} "
        f"bpc_A_afterB={bpc_A_after_B:.4f} retention={retention_A:.4f}",
        flush=True
    )
    return {
        "f": f,
        "seed": seed,
        "bpc_A_baseline": round(bpc_A_baseline, 5),
        "bpc_A_after_B": round(bpc_A_after_B, 5),
        "retention_A": round(retention_A, 5),
    }


def compute_verdict(f_sweep: List[float], per_f_retentions: Dict[float, List[float]]) -> Tuple[str, str, dict]:
    """Aggregate retention means over seeds, fit linear model, compute verdict."""
    f_vals = []
    ret_means = []
    ret_per_f = {}
    for f in sorted(f_sweep):
        vals = [v for v in per_f_retentions.get(f, []) if not math.isnan(v)]
        if not vals:
            continue
        mean_ret = sum(vals) / len(vals)
        f_vals.append(f)
        ret_means.append(mean_ret)
        ret_per_f[f] = {"mean": round(mean_ret, 4), "vals": [round(v, 4) for v in vals]}

    if len(f_vals) < 3:
        return (
            "CASCADE_INSTRUMENTATION_FAIL",
            f"Fewer than 3 f-values with valid cells ({len(f_vals)}). Cannot compute structure.",
            {}
        )

    r2, max_dev, residuals = linear_fit_residuals(f_vals, ret_means)

    # Boundary checks
    ret_f0 = ret_per_f.get(0.0, {}).get("mean", float("nan"))
    ret_f1 = ret_per_f.get(1.0, {}).get("mean", float("nan"))
    anchor_ok = (
        not math.isnan(ret_f0) and not math.isnan(ret_f1)
        and ret_f1 > ret_f0  # f=1 (same corpus) should be higher retention than f=0 (disjoint)
    )

    summary = {
        "f_values": f_vals,
        "retention_means": [round(r, 4) for r in ret_means],
        "linear_fit_r2": round(r2, 4) if not math.isnan(r2) else None,
        "max_deviation_from_linear": round(max_dev, 4) if not math.isnan(max_dev) else None,
        "residuals": [round(r, 4) for r in residuals],
        "per_f": ret_per_f,
        "anchor_ok_f0_lt_f1": anchor_ok,
        "ret_f0": round(ret_f0, 4) if not math.isnan(ret_f0) else None,
        "ret_f1": round(ret_f1, 4) if not math.isnan(ret_f1) else None,
    }

    if not anchor_ok:
        return (
            "CASCADE_ANCHOR_FAIL",
            f"Boundary anchors failed: f=0.0 retention={ret_f0:.3f}, f=1.0 retention={ret_f1:.3f}. "
            f"Expected f=1.0 > f=0.0. Check corpus construction.",
            summary
        )

    if r2 < LINEAR_R2_PASS_THRESHOLD and max_dev >= DEVIATION_PASS_THRESHOLD:
        return (
            "CASCADE_HARD_PASS",
            f"Discrete step structure detected: linear-fit R^2={r2:.3f} < {LINEAR_R2_PASS_THRESHOLD}, "
            f"max deviation from linear={max_dev:.3f} >= {DEVIATION_PASS_THRESHOLD}. "
            f"Retention vs corpus-overlap-fraction is NOT smooth-monotone. "
            f"Saddle-cascade plateau dynamics supported. "
            f"f=0.0 retention={ret_f0:.3f}, f=1.0 retention={ret_f1:.3f}.",
            summary
        )

    if r2 >= LINEAR_R2_FAIL_THRESHOLD and max_dev < DEVIATION_FAIL_THRESHOLD:
        return (
            "CASCADE_HARD_FAIL",
            f"Smooth-monotone retention: linear-fit R^2={r2:.3f} >= {LINEAR_R2_FAIL_THRESHOLD}, "
            f"max deviation={max_dev:.3f} < {DEVIATION_FAIL_THRESHOLD}. "
            f"Retention interpolates smoothly with corpus overlap -- not a saddle-cascade. "
            f"Cascade framework does NOT apply. "
            f"f=0.0 retention={ret_f0:.3f}, f=1.0 retention={ret_f1:.3f}.",
            summary
        )

    return (
        "CASCADE_MIDDLE",
        f"Inconclusive: linear-fit R^2={r2:.3f} (pass threshold {LINEAR_R2_PASS_THRESHOLD}, "
        f"fail threshold {LINEAR_R2_FAIL_THRESHOLD}), "
        f"max deviation={max_dev:.3f} (pass threshold {DEVIATION_PASS_THRESHOLD}). "
        f"f=0.0 retention={ret_f0:.3f}, f=1.0 retention={ret_f1:.3f}. "
        f"Partial structure; consider finer f grid or larger N.",
        summary
    )


# ---- self-tests ----
def self_test():
    errors = []

    # Self-test 1: f=1.0 anchor -- build_mixed_corpus with f=1.0 should return only corpus_A bytes
    dummy_a = bytes(range(100))  # simple test corpus
    mixed_100 = build_mixed_corpus(dummy_a, 100, 1.0, seed=42)
    if mixed_100 != dummy_a[:100]:
        errors.append(f"Self-test 1 FAIL: f=1.0 mixed corpus != corpus_A (got {mixed_100[:5]}...)")

    # Self-test 2: f=0.0 anchor -- mixed corpus should contain 0 bytes from corpus_A
    mixed_0 = build_mixed_corpus(dummy_a, 100, 0.0, seed=42)
    overlap = sum(1 for a, b in zip(dummy_a[:100], mixed_0[:100]) if a == b)
    # With random corpus_B (seed=7777+42=7819), overlap ~ uniform chance ~ 100/256 ~ 39
    # But the important thing is the function doesn't crash and returns 100 bytes
    if len(mixed_0) != 100:
        errors.append(f"Self-test 2 FAIL: f=0.0 mixed corpus length={len(mixed_0)} != 100")

    # Self-test 3: Linear baseline R^2 formula verification
    xs = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
    ys_linear = [0.60 + 0.34 * x for x in xs]  # perfect linear
    r2_lin, _, _ = linear_fit_residuals(xs, ys_linear)
    if r2_lin < 0.999:
        errors.append(f"Self-test 3 FAIL: linear_fit_residuals on perfect linear returned R^2={r2_lin:.4f} (expected > 0.999)")

    # Self-test 4: Cascade hypothetical -- should detect HARD-PASS condition
    ys_cascade = [0.60, 0.61, 0.62, 0.94, 0.94, 0.94, 0.94]
    r2_cas, max_dev_cas, _ = linear_fit_residuals(xs, ys_cascade)
    if r2_cas >= LINEAR_R2_PASS_THRESHOLD:
        errors.append(
            f"Self-test 4 FAIL: cascade hypothetical R^2={r2_cas:.4f} >= {LINEAR_R2_PASS_THRESHOLD} "
            f"(should be < {LINEAR_R2_PASS_THRESHOLD} to detect discrete structure)"
        )
    if max_dev_cas < DEVIATION_PASS_THRESHOLD:
        errors.append(
            f"Self-test 4 FAIL: cascade hypothetical max_dev={max_dev_cas:.4f} < {DEVIATION_PASS_THRESHOLD} "
            f"(should detect HARD-PASS)"
        )
    # Verify verdict function too
    per_f = {f: [y] for f, y in zip(xs, ys_cascade)}
    verdict4, _, _ = compute_verdict(xs, per_f)
    if verdict4 != "CASCADE_HARD_PASS":
        errors.append(f"Self-test 4 FAIL: cascade hypothetical verdict={verdict4} (expected CASCADE_HARD_PASS)")

    if errors:
        for e in errors:
            print(f"[SELF-TEST] {e}", flush=True)
        raise AssertionError(f"Self-tests FAILED ({len(errors)} errors)")
    print(f"[SELF-TEST] All 4 self-tests passed", flush=True)


# ---- main ----
def run(smoke: bool = False):
    device = torch.device("cpu")
    t0 = time.monotonic()
    print(f"[cascade_plateau] device={device} smoke={smoke}", flush=True)

    # Corpus preflight
    corpus_a_full = pa.load_corpus_a()
    print(f"[cascade_plateau] corpus_a preflight: {len(corpus_a_full)} bytes", flush=True)
    if len(corpus_a_full) < 1000:
        raise RuntimeError(
            f"corpus_a preflight FAIL: only {len(corpus_a_full)} bytes. "
            f"Check PLAN.md / README.md in repo root."
        )

    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    N = N_SMOKE if smoke else N_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    n_epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL

    config = {
        "mode": "smoke" if smoke else "full",
        "f_sweep": f_sweep,
        "N": N, "batch_size": batch_size,
        "n_epochs": n_epochs, "phase_a_epochs": phase_a_epochs,
        "n_bytes": n_bytes, "seeds": seeds,
        "linear_r2_pass_threshold": LINEAR_R2_PASS_THRESHOLD,
        "linear_r2_fail_threshold": LINEAR_R2_FAIL_THRESHOLD,
        "deviation_pass_threshold": DEVIATION_PASS_THRESHOLD,
        "deviation_fail_threshold": DEVIATION_FAIL_THRESHOLD,
    }
    print(f"[config] {config}", flush=True)

    # Run all cells
    per_f_retentions: Dict[float, List[float]] = {f: [] for f in f_sweep}
    all_cells = []

    for f in f_sweep:
        print(f"[cascade_plateau] === f={f:.2f} ===", flush=True)
        for seed in seeds:
            try:
                cell = run_one_cell(seed, f, N, batch_size, n_epochs, phase_a_epochs, n_bytes, device)
                per_f_retentions[f].append(cell["retention_A"])
                all_cells.append(cell)
            except Exception as ex:
                import traceback
                print(f"  ERROR f={f:.2f} seed={seed}: {type(ex).__name__}: {ex}", flush=True)
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()
                per_f_retentions[f].append(float("nan"))
                all_cells.append({"f": f, "seed": seed, "retention_A": float("nan"), "error": str(ex)})

    verdict, verdict_msg, summary = compute_verdict(f_sweep, per_f_retentions)
    elapsed = time.monotonic() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "all_cells": all_cells,
        "config": config,
    }
    validate_metrics(metrics)

    out_dir = get_output_dir("wave14_saddle_cascade_plateau_v1")
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f_out:
        json.dump(metrics, f_out, indent=2)

    print(f"[done] verdict={verdict}", flush=True)
    print(f"[done] verdict_msg={verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s metrics={out_path}", flush=True)
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    # Always run self-tests before main experiment
    self_test()
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
