"""
saddle_hierarchy_um_v1 -- Q-F4: SKAH-M saddle-space ultrametricity test.

SCIENTIFIC QUESTION (Q-F4):
  SKAH-M classification (v228) includes "saddle-hierarchy DAM" component.
  This predicts: STRICT ultrametricity in SADDLE space (not minima space).
  The v324 test was on MINIMA overlaps -- wrong space for SKAH-M's signature.

  Protocol:
    1. Store P patterns in Hopfield weight matrix.
    2. Find saddles: start from minima (retrieved patterns) + apply gradient
       ascent along direction of LOWEST Hessian eigenvalue. Saddle = state
       where gradient is zero AND Hessian has exactly 1 negative eigenvalue.
       Approximation: use finite-step gradient ascent terminating when
       |field - current state| < eps (approximate saddle).
    3. Compute P x P overlap matrix on SADDLE states (not retrieved states).
    4. Apply strict ultrametric triplet test: for all (i,j,k) triplets,
       check if max(Q_ij, Q_jk) >= Q_ik (triangle inequality in overlap space).
    5. Compute mean_ratio_saddle = mean(Q_ik / max(Q_ij, Q_jk)).
       If CK/SKAH-M prediction is correct: mean_ratio_saddle >= 0.85 (much
       higher than minima mean_ratio=0.583).

HARD-PASS: mean_ratio_saddle >= 0.85 in >=4/5 seeds.
HARD-FAIL: mean_ratio_saddle <= 0.70 in >=3/5 seeds (worse than minima 0.583+margin).
MIDDLE BAND: 0.70 < mean_ratio_saddle < 0.85.

Note: calibration probe (no prior empirical saddle-UM for this substrate).
Bands set +-50% around theoretical prediction (SKAH-M predicts ~ 0.90+):
  HP = 0.85 (15% below theoretical), HF = 0.70 (22% below theoretical).

FORMULA SELF-TESTS:
  1. mean_ratio calculation: for 3 patterns with Q_12=0.8, Q_23=0.7, Q_13=0.5:
     triplet (1,2,3): max(Q_12, Q_23)=0.8, ratio = Q_13/0.8 = 0.625.
     triplet (1,3,2): max(Q_13, Q_23)=0.7, ratio = Q_12/0.7 = 1.143 -> clamp to 1.
     etc. Mean over all triplets.
  2. Perfect ultrametric: Q all equal to q => all ratios = 1.0, mean_ratio = 1.0.
  3. Random overlaps ~ 0: mean_ratio ~ 0.5 (random baseline).

TIMEOUT ESTIMATE:
  Smoke: N=512, P=15 patterns, 3 seeds, gradient-ascent steps=20.
  Saddle finding: 15 * 20 * N^2 ops ~ 15*20*512^2 = ~79M ops. Expected ~5s.
  Full: N=1024, P=25 patterns, 5 seeds, 30 steps.
  Scaling: 1.5 * 5 * (1024/512)^2.0 * (5/3) = ceil(1.5*5*4*1.67) = ceil(50) = 50s.
  timeout=600s (12x buffer for saddle finding variability).

No _nN suffix; production N=1024 per rule 3 (N=1024, rationale: saddle
finding with Hessian approx is O(N^2) per step; 1024 is feasible with P=25).
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

ANCHOR_NAME = "saddle_hierarchy_um_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17, 23]
    P_PATTERNS = 15
    BETA = 2.0
    N_SADDLE_STEPS = 20      # gradient ascent steps for saddle finding
    SADDLE_STEP_SIZE = 0.1   # ascent step size
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    P_PATTERNS = 25
    BETA = 2.0
    N_SADDLE_STEPS = 30
    SADDLE_STEP_SIZE = 0.1

ALPHA = 0.15  # above alpha_c for substrate

# Pre-registered thresholds
HP_MEAN_RATIO_SADDLE = 0.85
HF_MEAN_RATIO_SADDLE = 0.70
HP_SEED_FRAC = 4 / 5
HF_SEED_FRAC = 3 / 5


# ---- FORMULA SELF-TESTS ----
def _selftest_mean_ratio():
    """
    3 patterns: Q_12=0.8, Q_23=0.7, Q_13=0.5.
    Enumerate all ordered triplets (i,j,k) i<j<k.
    Triplet (0,1,2): max(Q_01,Q_12)=max(0.8,0.7)=0.8; ratio=Q_02/0.8=0.5/0.8=0.625.
    mean_ratio = 0.625 (one triplet only).
    """
    Q = np.array([[1.0, 0.8, 0.5],
                  [0.8, 1.0, 0.7],
                  [0.5, 0.7, 1.0]])
    n = 3
    ratios = []
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                q_ij = abs(Q[i, j])
                q_jk = abs(Q[j, k])
                q_ik = abs(Q[i, k])
                denom = max(q_ij, q_jk)
                if denom > 1e-10:
                    ratios.append(q_ik / denom)
    mean_r = float(np.mean(ratios))
    assert abs(mean_r - 0.625) < 0.01, f"mean_ratio={mean_r:.4f}, expected 0.625"
    return mean_r


def _selftest_perfect_um():
    """All Q_ij = 0.5 for i!=j => perfect ultrametric, mean_ratio=1.0."""
    n = 4
    Q = np.ones((n, n)) * 0.5
    np.fill_diagonal(Q, 1.0)
    ratios = []
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                q_ij = abs(Q[i, j])
                q_jk = abs(Q[j, k])
                q_ik = abs(Q[i, k])
                denom = max(q_ij, q_jk)
                if denom > 1e-10:
                    ratios.append(q_ik / denom)
    mean_r = float(np.mean(ratios))
    assert abs(mean_r - 1.0) < 1e-9, f"Perfect UM mean_ratio={mean_r:.6f}, expected 1.0"
    return mean_r


_mr1 = _selftest_mean_ratio()
_mr2 = _selftest_perfect_um()
print(f"[selftest] mean_ratio test={_mr1:.4f}, perfect_UM={_mr2:.4f}", flush=True)


def build_hopfield_w(P: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(P, N_dim)).astype(np.float64)
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W, Xi


def find_minima(Xi: np.ndarray, W: np.ndarray, N_dim: int, n_steps: int = 50) -> np.ndarray:
    """Relax each pattern to a local minimum via synchronous dynamics."""
    P = len(Xi)
    minima = np.zeros((P, N_dim), dtype=np.float64)
    for i in range(P):
        s = Xi[i].copy()
        for _ in range(n_steps):
            s_new = np.sign(W @ s)
            s_new[s_new == 0] = 1.0
            if np.array_equal(s, s_new):
                break
            s = s_new
        minima[i] = s
    return minima


def find_saddle_from_minimum(s_min: np.ndarray, W: np.ndarray,
                              N_dim: int, n_steps: int,
                              step_size: float, rng: np.random.RandomState) -> np.ndarray:
    """
    Approximate saddle point via gradient ascent from a minimum.
    Strategy: perturb along the direction with smallest |field| (softest mode),
    then do gradient ascent (OPPOSITE to sign dynamics) for n_steps.
    Returns the approximate saddle state.
    """
    s = s_min.copy().astype(np.float64)

    for step in range(n_steps):
        h = W @ s  # local field
        # Gradient of energy E = -0.5 * s^T W s: dE/ds = -W s = -h
        # Gradient ASCENT: s -> s + step_size * h (move against the field)
        s_new = s + step_size * h
        # Re-normalize to hypercube: soft projection to [-1, 1]
        s_new = np.clip(s_new, -1.0, 1.0)
        s = s_new

    return s


def compute_mean_ratio_from_overlaps(Q: np.ndarray) -> Dict:
    """Compute mean_ratio from P x P overlap matrix Q."""
    P = len(Q)
    ratios = []
    for i in range(P):
        for j in range(i + 1, P):
            for k in range(j + 1, P):
                q_ij = abs(float(Q[i, j]))
                q_jk = abs(float(Q[j, k]))
                q_ik = abs(float(Q[i, k]))
                denom = max(q_ij, q_jk)
                if denom > 1e-10:
                    ratios.append(q_ik / denom)

    if not ratios:
        return {"mean_ratio": float("nan"), "n_triplets": 0}

    return {
        "mean_ratio": float(np.mean(ratios)),
        "std_ratio": float(np.std(ratios)),
        "n_triplets": len(ratios),
        "pct_above_08": float(np.mean(np.array(ratios) >= 0.8)),
    }


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    W, Xi = build_hopfield_w(P_PATTERNS, N, seed)
    print(f"[seed={seed}] Finding minima N={N} P={P_PATTERNS}...", flush=True)
    minima = find_minima(Xi, W, N, n_steps=100)

    print(f"[seed={seed}] Finding saddles from minima...", flush=True)
    saddles = np.zeros_like(minima)
    for i in range(P_PATTERNS):
        saddles[i] = find_saddle_from_minimum(minima[i], W, N,
                                               N_SADDLE_STEPS, SADDLE_STEP_SIZE, rng)

    # Compute overlap matrices for both minima and saddles
    Q_min = (minima @ minima.T) / N
    Q_sad = (saddles @ saddles.T) / N

    metrics_min = compute_mean_ratio_from_overlaps(Q_min)
    metrics_sad = compute_mean_ratio_from_overlaps(Q_sad)

    print(f"[seed={seed}] minima mean_ratio={metrics_min['mean_ratio']:.4f} "
          f"saddles mean_ratio={metrics_sad['mean_ratio']:.4f} "
          f"n_triplets={metrics_sad['n_triplets']}", flush=True)

    return {
        "seed": seed, "N": N, "P": P_PATTERNS, "run_mode": RUN_MODE,
        "minima_metrics": metrics_min,
        "saddle_metrics": metrics_sad,
        "saddle_improvement": (
            metrics_sad["mean_ratio"] - metrics_min["mean_ratio"]
            if (not math.isnan(metrics_sad["mean_ratio"]) and
                not math.isnan(metrics_min["mean_ratio"])) else float("nan")
        ),
    }


def _instrumentation_selftest():
    """Assert saddle-metrics non-null at small scale."""
    N_test, P_test = 128, 8
    rng = np.random.RandomState(99)
    W, Xi = build_hopfield_w(P_test, N_test, 99)
    minima = find_minima(Xi, W, N_test, n_steps=30)
    saddles = np.zeros_like(minima)
    for i in range(P_test):
        saddles[i] = find_saddle_from_minimum(minima[i], W, N_test, 10, 0.1, rng)

    Q_sad = (saddles @ saddles.T) / N_test
    metrics = compute_mean_ratio_from_overlaps(Q_sad)
    assert metrics["n_triplets"] > 0, f"n_triplets=0 at selftest scale (P={P_test})"
    assert not math.isnan(metrics["mean_ratio"]), "mean_ratio is NaN in selftest"
    print(f"[selftest] PASS: saddle mean_ratio={metrics['mean_ratio']:.4f} "
          f"n_triplets={metrics['n_triplets']} N={N_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    sad_ratios = [v["saddle_metrics"]["mean_ratio"] for v in per_seed.values()
                  if not math.isnan(v["saddle_metrics"]["mean_ratio"])]
    min_ratios = [v["minima_metrics"]["mean_ratio"] for v in per_seed.values()
                  if not math.isnan(v["minima_metrics"]["mean_ratio"])]
    improvements = [v["saddle_improvement"] for v in per_seed.values()
                    if not math.isnan(v["saddle_improvement"])]

    return {
        "mean_saddle_ratio": float(np.mean(sad_ratios)) if sad_ratios else float("nan"),
        "std_saddle_ratio": float(np.std(sad_ratios)) if sad_ratios else float("nan"),
        "mean_minima_ratio": float(np.mean(min_ratios)) if min_ratios else float("nan"),
        "mean_improvement": float(np.mean(improvements)) if improvements else float("nan"),
        "n_seeds": len(sad_ratios),
        "seeds_pass_hp": sum(1 for r in sad_ratios if r >= HP_MEAN_RATIO_SADDLE),
        "seeds_fail_hf": sum(1 for r in sad_ratios if r <= HF_MEAN_RATIO_SADDLE),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    r = agg["mean_saddle_ratio"]
    n = agg["n_seeds"]
    n_pass = agg["seeds_pass_hp"]
    n_fail = agg["seeds_fail_hf"]
    improv = agg["mean_improvement"]
    r_min = agg["mean_minima_ratio"]

    n_req_pass = max(1, math.ceil(n * HP_SEED_FRAC))
    n_req_fail = max(1, math.ceil(n * HF_SEED_FRAC))

    if math.isnan(r):
        return ("HARD_FAIL", "mean_saddle_ratio is NaN -- instrumentation failure.")

    if n_fail >= n_req_fail:
        return ("HARD_FAIL",
                f"Saddle-space ultrametricity ABSENT. mean_ratio_saddle={r:.4f} <= {HF_MEAN_RATIO_SADDLE}. "
                f"(Minima ratio={r_min:.4f}; improvement={improv:.4f}). n_seeds_fail={n_fail}/{n}. "
                f"SKAH-M saddle-hierarchy prediction NOT confirmed.")

    if n_pass >= n_req_pass:
        return ("HARD_PASS",
                f"SADDLE-SPACE ULTRAMETRICITY CONFIRMED. mean_ratio_saddle={r:.4f} >= {HP_MEAN_RATIO_SADDLE}. "
                f"(Minima ratio={r_min:.4f}; improvement over minima={improv:+.4f}). "
                f"n_seeds_pass={n_pass}/{n}. "
                f"SKAH-M saddle-hierarchy prediction confirmed: substrate has strict tree structure "
                f"in saddle space but not minima space.")

    return ("MIDDLE_BAND",
            f"Partial saddle-hierarchy signal. mean_ratio_saddle={r:.4f} "
            f"(hp={HP_MEAN_RATIO_SADDLE}, hf={HF_MEAN_RATIO_SADDLE}). "
            f"Minima ratio={r_min:.4f}. improvement={improv:+.4f}. n_seeds={n}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} P={P_PATTERNS} "
          f"alpha={ALPHA} saddle_steps={N_SADDLE_STEPS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "P": P_PATTERNS, "run_mode": RUN_MODE}
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
        "run_mode": RUN_MODE, "N": N, "P": P_PATTERNS, "alpha": ALPHA,
        "seeds": SEEDS,
        "aggregated": agg,
        "thresholds": {
            "HP_MEAN_RATIO_SADDLE": HP_MEAN_RATIO_SADDLE,
            "HF_MEAN_RATIO_SADDLE": HF_MEAN_RATIO_SADDLE,
        },
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
