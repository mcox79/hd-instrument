"""
substrate_metric_norm_axioms_v1 -- Verify Frobenius distance satisfies all 4 norm axioms.

SCIENTIFIC QUESTION (PP-41 support):
  Does ||W1 - W2||_F satisfy all 4 metric/norm axioms over substrate pairs?
  Axioms:
    1. Positivity: ||W1 - W2||_F >= 0
    2. Definiteness: ||W1 - W2||_F = 0 iff W1 = W2
    3. Homogeneity (norm axiom): ||c*(W1-W2)||_F = |c| * ||W1-W2||_F
    4. Triangle inequality: ||W1-W3||_F <= ||W1-W2||_F + ||W2-W3||_F

  PP-41 (v327): substrate Frobenius distance = algebraic readout of symmetric
  set-difference; foundational diff-and-merge primitive for PP-12/PP-9/PP-28.
  This experiment validates the mathematical foundation for that claim.

PRE-REGISTERED BANDS:
  HARD-PASS: All 4 axioms pass numerically at all tested (W1, W2, W3) triples
             (max violation < 1e-8 for positivity/definiteness/homogeneity,
             max relative triangle violation < 1e-8 where LHS - RHS < 0).
  MIDDLE: 3/4 axioms pass, or max violation 1e-8 to 1e-4.
  HARD-FAIL: 2 or fewer axioms pass, OR definiteness fails (||W-W||_F > 1e-6).

  Note: for exact float64 arithmetic, all axioms should pass to machine epsilon.
  Any failure here indicates numerical implementation error.

FORMULA SELF-TESTS:
  1. ||W - W||_F = 0 exactly (definiteness).
  2. ||W1 - W2||_F = ||W2 - W1||_F (symmetry, consequence of norm).
  3. ||c*(W1-W2)||_F = |c| * ||W1-W2||_F for c in {2, -3, 0.5} (homogeneity).
  4. For W1 = I/N, W2 = 0, W3 = W1/2:
     ||W1-W3||_F = ||W1/2||_F = ||W1||_F/2 <= ||W1-W2||_F + ||W2-W3||_F
     = ||W1||_F + ||W1/2||_F = 1.5 * ||W1||_F. Check: 0.5*||W1||_F <= 1.5*||W1||_F (trivially true).

TIMEOUT ESTIMATE:
  Pure numpy arithmetic. N=1024, M=10 patterns, 50 random triples.
  Smoke: ~0.5s. Full: ~2s. timeout=30s.

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

ANCHOR_NAME = "substrate_metric_norm_axioms_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_TRIPLES = 10
    M_LIST = [5, 20]
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_TRIPLES = 50
    M_LIST = [5, 20, 50, 100]

HP_MAX_VIOLATION = 1e-8
HF_MAX_VIOLATION = 1e-4


def build_substrate_w(M: int, N: int, rng: np.random.RandomState) -> np.ndarray:
    """W = Xi^T Xi / N with M random BSC patterns."""
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    return Xi.T @ Xi / N


def frobenius_distance(W1: np.ndarray, W2: np.ndarray) -> float:
    """||W1 - W2||_F = sqrt(sum((W1-W2)^2))."""
    return float(np.linalg.norm(W1 - W2, "fro"))


def check_axioms(W1: np.ndarray, W2: np.ndarray, W3: np.ndarray) -> Dict:
    """Check all 4 norm axioms for the triple (W1, W2, W3)."""
    d12 = frobenius_distance(W1, W2)
    d23 = frobenius_distance(W2, W3)
    d13 = frobenius_distance(W1, W3)
    d11 = frobenius_distance(W1, W1)
    d22 = frobenius_distance(W2, W2)
    d33 = frobenius_distance(W3, W3)

    # Axiom 1: positivity (all distances >= 0)
    ax1_pass = (d12 >= 0 and d23 >= 0 and d13 >= 0)
    ax1_max_violation = max(0.0, -d12, -d23, -d13)

    # Axiom 2: definiteness (||W - W||_F = 0)
    ax2_max_violation = max(abs(d11), abs(d22), abs(d33))
    ax2_pass = ax2_max_violation < HP_MAX_VIOLATION

    # Axiom 3: homogeneity -- test c in {2, -3, 0.5}
    c_vals = [2.0, -3.0, 0.5]
    hom_violations = []
    for c in c_vals:
        lhs = frobenius_distance(c * W1, c * W2)
        rhs = abs(c) * d12
        hom_violations.append(abs(lhs - rhs))
    ax3_max_violation = max(hom_violations)
    ax3_pass = ax3_max_violation < HP_MAX_VIOLATION

    # Axiom 4: triangle inequality ||W1-W3||_F <= ||W1-W2||_F + ||W2-W3||_F
    tri_violation = d13 - (d12 + d23)  # should be <= 0
    ax4_pass = tri_violation <= HP_MAX_VIOLATION
    ax4_max_violation = max(0.0, tri_violation)

    n_pass = sum([ax1_pass, ax2_pass, ax3_pass, ax4_pass])
    return {
        "ax1_positivity_pass": ax1_pass,
        "ax1_max_violation": ax1_max_violation,
        "ax2_definiteness_pass": ax2_pass,
        "ax2_max_violation": ax2_max_violation,
        "ax3_homogeneity_pass": ax3_pass,
        "ax3_max_violation": ax3_max_violation,
        "ax4_triangle_pass": ax4_pass,
        "ax4_max_violation": ax4_max_violation,
        "n_axioms_pass": n_pass,
        "d12": d12, "d23": d23, "d13": d13,
    }


def run_seed(seed: int) -> Dict:
    """Test axioms on N_TRIPLES random triples per M in M_LIST."""
    rng = np.random.RandomState(seed)
    results_by_M = {}
    for M in M_LIST:
        triple_results = []
        for t in range(N_TRIPLES):
            W1 = build_substrate_w(M, N, rng)
            W2 = build_substrate_w(M, N, rng)
            W3 = build_substrate_w(M, N, rng)
            r = check_axioms(W1, W2, W3)
            triple_results.append(r)

        # Aggregate over triples
        n_all_pass = sum(1 for r in triple_results if r["n_axioms_pass"] == 4)
        max_violation = max(
            max(r["ax1_max_violation"], r["ax2_max_violation"],
                r["ax3_max_violation"], r["ax4_max_violation"])
            for r in triple_results
        )
        ax_pass_counts = {i: sum(1 for r in triple_results if r[f"ax{i}_{['positivity','definiteness','homogeneity','triangle'][i-1]}_pass"]) for i in range(1, 5)}
        results_by_M[M] = {
            "n_triples": N_TRIPLES,
            "n_all_axioms_pass": n_all_pass,
            "max_violation": max_violation,
            "ax_pass_counts": ax_pass_counts,
        }
        print(f"  [seed={seed} M={M}] all_pass={n_all_pass}/{N_TRIPLES} "
              f"max_viol={max_violation:.2e} "
              f"ax=[{ax_pass_counts[1]},{ax_pass_counts[2]},{ax_pass_counts[3]},{ax_pass_counts[4]}]",
              flush=True)

    return {"by_M": results_by_M, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert all 4 axioms pass on a small known case."""
    N_test = 128
    M_test = 10
    rng = np.random.RandomState(42)
    W1 = build_substrate_w(M_test, N_test, rng)
    W2 = build_substrate_w(M_test, N_test, rng)
    W3 = build_substrate_w(M_test, N_test, rng)

    r = check_axioms(W1, W2, W3)
    assert r["ax2_definiteness_pass"], f"Definiteness failed: max_viol={r['ax2_max_violation']:.2e}"
    assert r["ax3_homogeneity_pass"], f"Homogeneity failed: max_viol={r['ax3_max_violation']:.2e}"
    assert r["ax4_triangle_pass"], f"Triangle inequality failed: viol={r['ax4_max_violation']:.2e}"
    assert r["n_axioms_pass"] == 4, f"Only {r['n_axioms_pass']}/4 axioms pass at selftest"

    # Also verify definiteness directly
    d_self = frobenius_distance(W1, W1)
    assert abs(d_self) < 1e-10, f"||W-W||_F = {d_self:.2e} not 0"

    print(f"[selftest] PASS: 4/4 axioms verified at N={N_test} M={M_test}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify axiom-4 self-test in docstring."""
    N_t = 64
    W1 = np.eye(N_t) / N_t
    W2 = np.zeros((N_t, N_t))
    W3 = W1 / 2.0
    d12 = frobenius_distance(W1, W2)  # = ||W1||_F
    d23 = frobenius_distance(W2, W3)  # = ||W1/2||_F = ||W1||_F/2
    d13 = frobenius_distance(W1, W3)  # = ||W1/2||_F = ||W1||_F/2
    # Triangle: d13 = 0.5*||W1||_F <= d12 + d23 = 1.5*||W1||_F
    assert d13 <= d12 + d23 + 1e-12, f"Triangle self-test failed: {d13:.6f} > {d12+d23:.6f}"
    print("[formula_selftests] PASS: triangle inequality docstring example verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds."""
    agg_by_M = {}
    for M in M_LIST:
        all_max_viol = []
        all_n_pass = []
        for sd in per_seed.values():
            row = sd["by_M"].get(M) or sd["by_M"].get(str(M))
            if row is None:
                continue
            all_max_viol.append(row["max_violation"])
            all_n_pass.append(row["n_all_axioms_pass"])
        agg_by_M[M] = {
            "mean_max_violation": float(np.mean(all_max_viol)) if all_max_viol else float("nan"),
            "overall_max_violation": float(np.max(all_max_viol)) if all_max_viol else float("nan"),
            "mean_n_all_pass": float(np.mean(all_n_pass)) if all_n_pass else float("nan"),
            "n_seeds": len(all_max_viol),
        }
    return {"by_M": agg_by_M}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_M = agg["by_M"]
    all_max_viol = [v["overall_max_violation"] for v in by_M.values()
                    if not math.isnan(v.get("overall_max_violation", float("nan")))]
    all_n_pass = [v["mean_n_all_pass"] for v in by_M.values()
                  if not math.isnan(v.get("mean_n_all_pass", float("nan")))]

    if not all_max_viol:
        return ("HARD_FAIL", "No valid results.")

    global_max_viol = max(all_max_viol)
    mean_n_pass = float(np.mean(all_n_pass)) if all_n_pass else 0.0

    if global_max_viol < HP_MAX_VIOLATION:
        return ("HARD_PASS",
                f"All 4 Frobenius norm axioms confirmed at N={N}. "
                f"max_violation={global_max_viol:.2e} < {HP_MAX_VIOLATION:.0e}. "
                f"mean_triples_all_pass={mean_n_pass:.1f}/{N_TRIPLES}. "
                f"PP-41 mathematical foundation validated.")
    if global_max_viol >= HF_MAX_VIOLATION:
        return ("HARD_FAIL",
                f"Frobenius norm axiom violation detected. max_violation={global_max_viol:.2e} "
                f">= HF threshold {HF_MAX_VIOLATION:.0e}. Numerical implementation error.")
    return ("MIDDLE_BAND",
            f"Marginal axiom violations. max_violation={global_max_viol:.2e} "
            f"(HP<{HP_MAX_VIOLATION:.0e} HF>={HF_MAX_VIOLATION:.0e}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_LIST={M_LIST} "
          f"N_TRIPLES={N_TRIPLES} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
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
        "M_LIST": M_LIST, "N_TRIPLES": N_TRIPLES,
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
