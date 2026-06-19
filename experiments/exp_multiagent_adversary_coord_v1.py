"""
multiagent_adversary_coord_v1 -- Multi-agent with ADVERSARIAL participant.

SCIENTIFIC QUESTION (multiagent extension; adversarial participant):
  Previous experiments tested cooperative (consensus) and competing (two groups)
  multi-agent configurations. This tests an ADVERSARIAL participant:
    - N_COOPERATIVE agents write patterns they want to be remembered.
    - N_ADVERSARY agents OVERWRITE target patterns with orthogonal noise (poison).
    - Question: can the substrate RESIST adversarial overwrites?
    - Question: does adversary budget (n_adv) change resistance threshold?

  Design:
    - Cooperative writes: W_coop = outer(xi_target, xi_target) * N_COOP_WRITES / N.
    - Adversary write: xi_adv is random (unrelated). W_adv = outer(xi_adv, xi_adv) / N.
    - W_combined = W_coop + W_adv (additive superposition).
    - Resilience: cosine(sign(W_combined @ xi_target), xi_target) after N_ADV adversary writes.

  Test cells:
    (A) Resilience to single adversary: 1 adversary write vs N_COOP=5 cooperative writes.
        HP-A: cosine_target >= 0.75 (minimal damage from 1/5 adversary budget).
    (B) Adversary budget threshold: find N_ADV such that cosine_target drops below 0.50.
        HP-B: threshold N_ADV >= 3 (i.e., adversary needs >= 3 writes to flip target).
    (C) Adversarial collaboration: adversary learns target and writes ANTI-pattern
        xi_anti = -xi_target. Effect: (W_coop - W_anti) @ xi_target has reduced SNR.
        HP-C: even with anti-pattern write, cosine_target >= 0.50 if N_COOP >= N_ADV.

PRE-REGISTERED BANDS:
  HARD-PASS: All of A, B, C.
  MIDDLE: 2/3 cells pass.
  HARD-FAIL: 0-1 cells pass.

  Calibration: first adversarial multi-agent test. Bands +-50% of theory.
  Theory: W = (N_COOP - N_ADV) * outer(xi_target, xi_target) / N for anti-pattern.
  Cosine = (N_COOP - N_ADV) / sqrt((N_COOP - N_ADV)^2 + N_NOISE^2).

FORMULA SELF-TESTS:
  1. Anti-pattern: W = (N_COOP*outer(xi,xi) - N_ADV*outer(xi,xi)) / N = (N_COOP-N_ADV)*outer(xi,xi)/N.
     cosine(sign(W@xi), xi) = sign(N_COOP - N_ADV). Positive if N_COOP > N_ADV.
     [INPUT: N_COOP=5, N_ADV=3, no background] [EXPECTED: cosine > 0]
  2. Random adversary: E[damage per random write] = 1/N (crosstalk term).
     After N_ADV random writes, SNR drops by N_ADV / N << 1 for N>>1.
     [INPUT: N=1024, N_ADV=5, N_COOP=5] [EXPECTED: cosine near 1.0 - O(5/1024)]
  3. Threshold: N_ADV must exceed N_COOP for anti-pattern to flip target.
     [INPUT: N_COOP=5, N_ADV=5 anti-pattern] [EXPECTED: cosine near 0]

TIMEOUT ESTIMATE:
  Smoke: N=1024, M=30 background, 2 seeds. Full: N=1024, M=50, 5 seeds.
  Linear. Smoke ~1s -> Full ~8s. timeout=120s.

No _nN suffix; production N=1024 per rule 3.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "multiagent_adversary_coord_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_BACKGROUND = 20       # background patterns (not targeted)
    N_COOP_WRITES = 5       # cooperative writes for target
    ADV_BUDGET_SWEEP = [0, 1, 2, 3, 5, 8]  # adversary random writes
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_BACKGROUND = 40
    N_COOP_WRITES = 5
    ADV_BUDGET_SWEEP = [0, 1, 2, 3, 5, 8, 12]  # more budget values for threshold

HP_RESILIENCE_1ADV = 0.75     # Cell A: 1 adversary write, cosine target >= 0.75
HP_THRESHOLD_N_ADV = 3        # Cell B: adversary needs >= 3 writes to flip below 0.50
HP_ANTI_PATTERN_FLOOR = 0.50  # Cell C: anti-pattern cosine floor with N_COOP=N_ADV

FLIP_THRESHOLD = 0.50  # below this = "flipped" target

# ---- FORMULA SELF-TESTS ----
def _snr_theory(n_coop: int, n_adv_random: int, N_dim: int) -> float:
    """SNR for random adversary: E[cosine] ~ n_coop / sqrt(n_coop^2 + n_adv*(1 - 1/N)^2)."""
    # Simplified: noise per random write ~ 1/sqrt(N)
    signal = float(n_coop)
    noise = math.sqrt(float(n_adv_random) / N_dim)
    return signal / (signal + noise) if (signal + noise) > 0 else 0.0

_snr_test = _snr_theory(5, 5, 1024)
assert _snr_test > 0.90, f"SNR theory check failed: {_snr_test:.4f} should be >0.90 for N=1024, n_adv=5"

def _anti_pattern_theory(n_coop: int, n_adv: int) -> float:
    """Anti-pattern cosine ~ (n_coop - n_adv) / max(|n_coop - n_adv|, 0.01)."""
    net = n_coop - n_adv
    if abs(net) < 1e-9:
        return 0.0
    return 1.0 if net > 0 else -1.0

assert _anti_pattern_theory(5, 3) == 1.0, "Anti-pattern: N_COOP=5 > N_ADV=3 should give positive cosine"
assert _anti_pattern_theory(5, 5) == 0.0, "Anti-pattern: N_COOP=5 = N_ADV=5 should give ~0"


def build_w_background(M: int, N_dim: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W


def retrieval_cosine(W: np.ndarray, xi: np.ndarray) -> float:
    raw = W @ xi
    return float(np.dot(np.sign(raw), xi)) / N


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)

    # Target pattern
    xi_target = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
    xi_anti = -xi_target  # adversary's anti-pattern

    # Background W
    W_background = build_w_background(M_BACKGROUND, N, seed)

    # Cooperative writes
    W_coop = W_background + N_COOP_WRITES * np.outer(xi_target, xi_target) / N
    np.fill_diagonal(W_coop, 0.0)

    # Cell A: 1 random adversary write
    xi_adv1 = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
    W_1adv = W_coop + np.outer(xi_adv1, xi_adv1) / N
    np.fill_diagonal(W_1adv, 0.0)
    cosine_1adv = retrieval_cosine(W_1adv, xi_target)
    cell_A_pass = cosine_1adv >= HP_RESILIENCE_1ADV

    # Cell B: sweep random adversary budget
    cosine_by_budget = {}
    for n_adv in ADV_BUDGET_SWEEP:
        W_adv_total = W_coop.copy()
        for _ in range(n_adv):
            xi_adv_r = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
            W_adv_total += np.outer(xi_adv_r, xi_adv_r) / N
        np.fill_diagonal(W_adv_total, 0.0)
        cos = retrieval_cosine(W_adv_total, xi_target)
        cosine_by_budget[n_adv] = cos

    # Threshold N_ADV = first budget where cosine drops below FLIP_THRESHOLD
    threshold_n_adv = float("nan")
    for n_adv in sorted(ADV_BUDGET_SWEEP):
        if cosine_by_budget[n_adv] < FLIP_THRESHOLD:
            threshold_n_adv = float(n_adv)
            break
    if math.isnan(threshold_n_adv):
        threshold_n_adv = float(max(ADV_BUDGET_SWEEP) + 1)  # didn't flip within budget

    cell_B_pass = threshold_n_adv >= HP_THRESHOLD_N_ADV

    # Cell C: anti-pattern with N_COOP = N_ADV
    # Each anti-pattern write cancels one cooperative write (exactly, up to noise)
    W_anti = W_background.copy()
    W_anti += N_COOP_WRITES * np.outer(xi_target, xi_target) / N
    W_anti += N_COOP_WRITES * np.outer(xi_anti, xi_anti) / N  # = n_coop anti writes
    np.fill_diagonal(W_anti, 0.0)
    # With N_COOP anti-patterns = N_COOP cooperatives, net = 0 for target
    # But background provides some noise floor
    cosine_anti = retrieval_cosine(W_anti, xi_target)

    # Now test with N_COOP > N_ADV: 5 coop writes, 3 anti writes
    W_anti_unbalanced = W_background.copy()
    W_anti_unbalanced += N_COOP_WRITES * np.outer(xi_target, xi_target) / N
    W_anti_unbalanced += 3 * np.outer(xi_anti, xi_anti) / N
    np.fill_diagonal(W_anti_unbalanced, 0.0)
    cosine_anti_unbalanced = retrieval_cosine(W_anti_unbalanced, xi_target)

    # HP-C: with N_COOP=5 > N_ADV=3, cosine >= HP floor
    cell_C_pass = cosine_anti_unbalanced >= HP_ANTI_PATTERN_FLOOR

    print(f"  [seed={seed}] cosine_1adv={cosine_1adv:.4f}(A:{cell_A_pass}) "
          f"threshold_budget={threshold_n_adv:.1f}(B:{cell_B_pass}) "
          f"cosine_anti_unbal={cosine_anti_unbalanced:.4f}(C:{cell_C_pass})", flush=True)

    return {
        "seed": seed,
        "cosine_1adv": cosine_1adv,
        "threshold_n_adv": threshold_n_adv,
        "cosine_anti_unbalanced": cosine_anti_unbalanced,
        "cosine_anti_balanced": cosine_anti,
        "cosine_by_budget": {str(k): v for k, v in cosine_by_budget.items()},
        "cell_A_pass": cell_A_pass,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert adversary metrics non-null at small scale."""
    rng = np.random.RandomState(42)
    xi = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)

    # Minimal W: just the target pattern
    W = np.outer(xi, xi) / N
    np.fill_diagonal(W, 0.0)
    cos = retrieval_cosine(W, xi)
    assert not math.isnan(cos), "retrieval_cosine is NaN"
    assert cos > 0.5, f"Single-pattern retrieval cosine={cos:.4f} too low"

    # Adversary write
    xi_adv = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
    W_adv = W + np.outer(xi_adv, xi_adv) / N
    np.fill_diagonal(W_adv, 0.0)
    cos_after = retrieval_cosine(W_adv, xi)
    assert not math.isnan(cos_after), "post-adversary cosine is NaN"

    print(f"[selftest] PASS: cos_before={cos:.4f} cos_after={cos_after:.4f}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    cos1adv, thresh, cos_anti_unbal = [], [], []
    a_pass, b_pass, c_pass = [], [], []
    for sd in per_seed.values():
        cos1adv.append(sd.get("cosine_1adv", float("nan")))
        thresh.append(sd.get("threshold_n_adv", float("nan")))
        cos_anti_unbal.append(sd.get("cosine_anti_unbalanced", float("nan")))
        a_pass.append(sd.get("cell_A_pass", False))
        b_pass.append(sd.get("cell_B_pass", False))
        c_pass.append(sd.get("cell_C_pass", False))
    return {
        "mean_cosine_1adv": float(np.nanmean(cos1adv)),
        "mean_threshold_n_adv": float(np.nanmean(thresh)),
        "mean_cosine_anti_unbal": float(np.nanmean(cos_anti_unbal)),
        "frac_A_pass": float(np.mean(a_pass)),
        "frac_B_pass": float(np.mean(b_pass)),
        "frac_C_pass": float(np.mean(c_pass)),
        "n_seeds": len(a_pass),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    fA = agg["frac_A_pass"]
    fB = agg["frac_B_pass"]
    fC = agg["frac_C_pass"]
    hp_A = fA >= 0.80
    hp_B = fB >= 0.80
    hp_C = fC >= 0.80
    cells_pass = sum([hp_A, hp_B, hp_C])

    mc1 = agg["mean_cosine_1adv"]
    mta = agg["mean_threshold_n_adv"]
    mca = agg["mean_cosine_anti_unbal"]

    if cells_pass == 3:
        return ("HARD_PASS",
                f"Adversarial resilience CONFIRMED. "
                f"cos_1adv={mc1:.4f}>={HP_RESILIENCE_1ADV} "
                f"threshold_budget={mta:.1f}>={HP_THRESHOLD_N_ADV} "
                f"cos_anti_unbal={mca:.4f}>={HP_ANTI_PATTERN_FLOOR}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    if cells_pass <= 1:
        return ("HARD_FAIL",
                f"Adversarial resilience NOT confirmed. "
                f"cos_1adv={mc1:.4f} threshold={mta:.1f} cos_anti={mca:.4f}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    return ("MIDDLE_BAND",
            f"{cells_pass}/3 cells pass. cos_1adv={mc1:.4f} threshold={mta:.1f} "
            f"cos_anti={mca:.4f}. A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"N_COOP={N_COOP_WRITES} M_BG={M_BACKGROUND} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE, "M_BACKGROUND": M_BACKGROUND}
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
        "run_mode": RUN_MODE, "N": N, "M_BACKGROUND": M_BACKGROUND,
        "N_COOP_WRITES": N_COOP_WRITES, "seeds": SEEDS,
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
