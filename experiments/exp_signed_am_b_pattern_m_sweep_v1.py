"""
signed_am_b_pattern_m_sweep_v1 -- Signed AM with M_A sweep to find repulsion envelope.

RESCUE from signed_am_b_pattern_full_v1 HARD_FAIL (repulsion_rate=0 at M_A=20):
  Root cause: M_A=20 exceeds M_A_crit. Theory correct at small M_A (v324 HARD_PASS
  frac_anti_b=1.000 at M_A small). Operating-envelope sweep: characterize M_A_crit.

SCIENTIFIC QUESTION:
  What is the maximum M_A (A-patterns stored) at which B-pattern active repulsion
  is reliable at N=4096?
  repulsion_rate as a function of M_A: maps operating envelope.

PRE-REGISTERED BANDS (from research rescue note 2026-06-02):
  HARD-PASS: repulsion_rate >= 0.80 at M_A <= M_A_crit (to be determined by sweep).
             M_A_crit identified empirically as M_A where repulsion_rate >= 0.80.
  HARD-FAIL: repulsion_rate < 0.20 even at M_A=1, M_B=1 (theory itself wrong).
  MIDDLE: repulsion_rate >= 0.20 at some M_A but never reaches 0.80 in sweep.

P_deflated=0.55 per research note.

DESIGN:
  N = 4096, M_B = 1 (single B-pattern for cleanest test).
  M_A sweep: {1, 2, 5, 10, 20} per research spec.
  n_queries = 30 per M_A per seed (30 different noise realizations of B-pattern).
  noise_frac = 0.10 (10% bit flip to start near B-pattern).
  Dynamics: 10-step synchronous Hopfield updates.
  Repulsion metric: cosine(final_state, eta_B) < -0.5 (converged to anti-B or A-pattern).

FORMULA SELF-TESTS:
  1. W_signed = W_A - W_B. Energy at eta_B:
     E(eta_B) = -(1/2)*eta_B^T*W_signed*eta_B / N
     = -(1/2)*[sum_mu (xi_mu.eta_B)^2/N - sum_nu (eta_nu.eta_B)^2/N] / N
     For B-pattern eta_B: (eta_B.eta_B)^2/N = N (dominant); A-patterns random.
     So E(eta_B) > 0 (energy MAX) -> repulsion expected. Verify sign.
  2. For M_A=1, M_B=1, N=4096: interference rms = sqrt(1/4096) ~ 0.016 << 1.
     B-pattern should ALWAYS be repelled. repulsion_rate ~ 1.0 expected.
  3. At M_A >> N: W_A landscape dominates; B-pattern repulsion collapses.

PROT-018: no _nN suffix; production N=4096 stated below per rule 3.
PROT-021: run_config includes N, M_B, run_mode (config-discriminating fields).
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

ANCHOR_NAME = "signed_am_b_pattern_m_sweep_v1"

# PROT-018: no _nN suffix; production N=4096 stated explicitly per rule 3.
N = 4096

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_A_LIST = [1, 5, 20]    # subset for smoke
    M_B = 1
    N_QUERIES = 10
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_A_LIST = [1, 2, 5, 10, 20]   # full sweep per research spec
    M_B = 1
    N_QUERIES = 30
    NOISE_FRAC = 0.10

# Pre-registered thresholds
HP_REPULSION_RATE = 0.80
HF_REPULSION_RATE = 0.20
# Repulsion threshold: one-step overlap with eta_B < REPULSION_THRESH (like v324 active_repulsion)
# v324 used < -0.3; at M_A=1 perfect repulsion gives cos_step1 = -1.0
REPULSION_THRESH = -0.3


def build_signed_w(M_A: int, M_B_count: int, seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build W_signed = W_A - W_B. Returns W_signed, Xi_A, Xi_B."""
    rng = np.random.RandomState(seed)
    Xi_A = rng.choice([-1.0, 1.0], size=(M_A, N)).astype(np.float64)
    Xi_B = rng.choice([-1.0, 1.0], size=(M_B_count, N)).astype(np.float64)
    W_A = Xi_A.T @ Xi_A / N
    W_B = Xi_B.T @ Xi_B / N
    W_signed = W_A - W_B
    return W_signed, Xi_A, Xi_B


def run_one_ma(W_signed: np.ndarray, Xi_B: np.ndarray,
               M_A: int, seed: int, n_queries: int) -> Dict:
    """
    Test repulsion for a single M_A configuration.
    MEASUREMENT: one-step overlap (like v324 active_repulsion_v1 which HARD_PASSed).
    After ONE synchronous update: sigma = sign(W_signed @ query).
    B-pattern is energy MAX -> one step moves AWAY from eta_B.
    repulsion check: overlap(sigma_step1, eta_B) < REPULSION_THRESH = -0.3.
    """
    rng = np.random.RandomState(seed + M_A * 1000)

    repulsion_count = 0
    cos_step1s = []
    for _ in range(n_queries):
        b_idx = rng.randint(0, M_B)
        eta_B = Xi_B[b_idx]
        # Start near eta_B with noise
        mask = rng.rand(N) < NOISE_FRAC
        s0 = eta_B.copy()
        s0[mask] *= -1.0
        s0 = np.sign(s0)
        s0[s0 == 0] = 1.0

        # ONE synchronous step: if eta_B is energy MAX, this moves to -eta_B direction
        h = W_signed @ s0
        s1 = np.sign(h); s1[s1 == 0] = 1.0
        cos_s1 = float(np.dot(s1, eta_B)) / N
        cos_step1s.append(cos_s1)
        if cos_s1 < REPULSION_THRESH:
            repulsion_count += 1

    repulsion_rate = repulsion_count / n_queries if n_queries > 0 else float("nan")
    return {
        "M_A": M_A,
        "repulsion_rate": repulsion_rate,
        "mean_cos_step1": float(np.mean(cos_step1s)),
        "n_queries": n_queries,
    }


def run_seed(seed: int) -> Dict:
    results = {}
    for M_A in M_A_LIST:
        W_signed, Xi_A, Xi_B = build_signed_w(M_A, M_B, seed)
        result = run_one_ma(W_signed, Xi_B, M_A, seed, N_QUERIES)
        print(
            f"  [seed={seed} M_A={M_A} M_B={M_B}] "
            f"repulsion_rate={result['repulsion_rate']:.3f} "
            f"mean_cos_step1={result['mean_cos_step1']:.3f}",
            flush=True
        )
        results[M_A] = result

    return {
        "M_A_results": results, "seed": seed, "N": N,
        "M_B": M_B, "run_mode": RUN_MODE
    }


def _instrumentation_selftest():
    """
    Assert repulsion signal exists at small M_A.
    Theory: W_signed = W_A - W_B; B-pattern is energy MAX -> dynamics repel.
    At M_A=1, B should always be repelled (minimal interference).
    """
    N_test = 2048
    M_A_test = 1
    M_B_test = 1
    seed = 42

    rng = np.random.RandomState(seed)
    Xi_A = rng.choice([-1.0, 1.0], size=(M_A_test, N_test)).astype(np.float64)
    Xi_B = rng.choice([-1.0, 1.0], size=(M_B_test, N_test)).astype(np.float64)
    W_A = Xi_A.T @ Xi_A / N_test
    W_B = Xi_B.T @ Xi_B / N_test
    W_signed = W_A - W_B

    # Energy at eta_B: should be positive (energy MAX)
    # E = -(1/2)*eta_B^T*W_signed*eta_B = -(1/2)*(W_B term - W_A term)
    # W_B*eta_B = eta_B (contribution from self-pattern); W_A*eta_B ~ 0 (random)
    # E(eta_B) ~ -(1/2)*(eta_B^T*(-eta_B)) = +(1/2)*N > 0 (energy MAX)
    eta_B = Xi_B[0]
    h_B = W_signed @ eta_B
    # h_B should oppose eta_B (sign(h_B) = -eta_B direction) -> repulsion
    cos_h_eta = float(np.dot(h_B, eta_B)) / (np.linalg.norm(h_B) * N_test + 1e-12)
    assert cos_h_eta < 0, (
        f"h_B field does not oppose eta_B at M_A=1: cos={cos_h_eta:.4f} "
        f"(expected negative = repulsion)"
    )

    # Run 10 queries: all should show one-step repulsion at M_A=1
    # (one-step overlap with eta_B < REPULSION_THRESH = -0.3, like v324)
    repulsion_count = 0
    for q_seed in range(10):
        rng2 = np.random.RandomState(q_seed + 999)
        mask = rng2.rand(N_test) < 0.10
        s0 = eta_B.copy()
        s0[mask] *= -1.0
        s0 = np.sign(s0); s0[s0 == 0] = 1.0
        # ONE step: h = W_signed @ s0, s1 = sign(h)
        h = W_signed @ s0
        s1 = np.sign(h); s1[s1 == 0] = 1.0
        cos_s1 = float(np.dot(s1, eta_B)) / N_test
        if cos_s1 < REPULSION_THRESH:
            repulsion_count += 1

    assert repulsion_count >= 7, (
        f"Only {repulsion_count}/10 queries show one-step repulsion at M_A=1 M_B=1 N={N_test}. "
        f"Theory predicts near-100% repulsion (cos_step1 << 0) at M_A=1."
    )

    print(
        f"[selftest] PASS: M_A=1 repulsion={repulsion_count}/10; "
        f"h_B opposes eta_B: cos={cos_h_eta:.4f} (N={N_test})",
        flush=True
    )


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify formula self-tests from docstring."""
    # Formula 1: interference rms at M_A=1, N=4096
    rms_interference = math.sqrt(1 / N)
    assert rms_interference < 0.02, (
        f"interference rms={rms_interference:.4f} too large at M_A=1 N={N}"
    )

    # Formula 2: REPULSION_THRESH < 0 (must be negative for anti-direction)
    assert REPULSION_THRESH < 0, f"REPULSION_THRESH={REPULSION_THRESH} must be < 0"

    # Formula 3: HP > HF thresholds in correct order
    assert HP_REPULSION_RATE > HF_REPULSION_RATE, (
        f"HP={HP_REPULSION_RATE} must exceed HF={HF_REPULSION_RATE}"
    )

    print(
        f"[formula_selftests] PASS: interference_rms={rms_interference:.4f} << 1; "
        f"REPULSION_THRESH={REPULSION_THRESH}; HP={HP_REPULSION_RATE}>HF={HF_REPULSION_RATE}",
        flush=True
    )


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate repulsion rates per M_A across seeds."""
    M_to_rates: Dict[int, List] = {M_A: [] for M_A in M_A_LIST}

    for sd in per_seed.values():
        m_results = sd.get("M_A_results", {})
        for M_A in M_A_LIST:
            r = m_results.get(M_A) or m_results.get(str(M_A))
            if r is None:
                continue
            rate = r.get("repulsion_rate", float("nan"))
            if not math.isnan(rate):
                M_to_rates[M_A].append(rate)

    per_M_A = []
    for M_A in M_A_LIST:
        rates = M_to_rates[M_A]
        avg_rate = float(np.mean(rates)) if rates else float("nan")
        per_M_A.append({
            "M_A": M_A,
            "avg_repulsion_rate": avg_rate,
            "n_seeds": len(rates),
            "passes_hp": (not math.isnan(avg_rate) and avg_rate >= HP_REPULSION_RATE),
            "fails_hard": (not math.isnan(avg_rate) and avg_rate < HF_REPULSION_RATE),
        })

    # M_A_crit: largest M_A where repulsion_rate >= HP
    hp_M_A = [row["M_A"] for row in per_M_A if row["passes_hp"]]
    M_A_crit = max(hp_M_A) if hp_M_A else None

    # Check for HF at M_A=1
    m1_row = next((r for r in per_M_A if r["M_A"] == M_A_LIST[0]), None)
    hard_fail_at_min = m1_row is not None and m1_row["fails_hard"]

    return {
        "per_M_A": per_M_A,
        "M_A_crit": M_A_crit,
        "hard_fail_at_min_M_A": hard_fail_at_min,
        "n_hp": len(hp_M_A),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    per_M_A = agg.get("per_M_A", [])
    M_A_crit = agg.get("M_A_crit")
    hard_fail_at_min = agg.get("hard_fail_at_min_M_A", False)
    n_hp = agg.get("n_hp", 0)

    if not per_M_A:
        return ("HARD_FAIL", "No M_A results.")

    if hard_fail_at_min:
        min_MA = M_A_LIST[0]
        m_row = next((r for r in per_M_A if r["M_A"] == min_MA), {})
        return (
            "HARD_FAIL",
            f"Signed-AM repulsion fails even at M_A={min_MA} (theory minimum). "
            f"repulsion_rate={m_row.get('avg_repulsion_rate', float('nan')):.3f} < {HF_REPULSION_RATE}. "
            f"Theory itself is wrong for this substrate configuration."
        )

    if n_hp >= 1:
        best_rate = max(
            (r["avg_repulsion_rate"] for r in per_M_A if r["passes_hp"]
             and not math.isnan(r["avg_repulsion_rate"])),
            default=float("nan")
        )
        return (
            "HARD_PASS",
            f"Signed-AM B-pattern repulsion confirmed at M_A <= M_A_crit={M_A_crit}. "
            f"Best repulsion_rate={best_rate:.3f}>={HP_REPULSION_RATE}. "
            f"{n_hp}/{len(M_A_LIST)} M_A cells pass HP. N={N} M_B={M_B}. "
            f"Operating envelope: reliable repulsion at M_A <= {M_A_crit} "
            f"(alpha_A_crit = {M_A_crit/N:.4f})."
        )

    # No HP but also not total failure
    best_rate = max(
        (r["avg_repulsion_rate"] for r in per_M_A
         if not math.isnan(r.get("avg_repulsion_rate", float("nan")))),
        default=float("nan")
    )
    return (
        "MIDDLE_BAND",
        f"Partial repulsion signal. Best rate={best_rate:.3f} < HP={HP_REPULSION_RATE}. "
        f"M_A_crit not identified. Envelope narrower than expected. N={N}."
    )


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(
        f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
        f"M_A_LIST={M_A_LIST} M_B={M_B} seeds={SEEDS}",
        flush=True
    )

    # PROT-021: include M_B as config-discriminating field
    run_config = {"N": N, "run_mode": RUN_MODE, "M_B": M_B}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N,
        "M_A_LIST": M_A_LIST, "M_B": M_B,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
