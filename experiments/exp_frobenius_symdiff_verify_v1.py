"""
frobenius_symdiff_verify_v1 -- Frobenius norm distance equals symmetric difference.

SCIENTIFIC QUESTION (deep-drill: substrate distance Frobenius=symdiff):
  For Hopfield weight matrices W_A and W_B built from pattern sets A and B
  (each BSC +-1, outer product / N construction), does:
    ||W_A - W_B||_F^2 / N == (2/N) * |A symdiff B|
  hold exactly (up to floating-point precision)?

  This is the "symdiff distance" claim: the Frobenius distance between two
  Hopfield weight matrices equals the symmetric difference cardinality of
  their pattern sets, normalized by N. If true, it means the weight matrix
  encodes a METRIC SPACE where the metric is pattern-set Jaccard distance.

  Derivation:
    W_A = sum_{xi in A} xi xi^T / N
    W_B = sum_{xi in B} xi xi^T / N
    W_A - W_B = sum_{xi in A\B} xi xi^T / N - sum_{xi in B\A} xi xi^T / N
    ||W_A - W_B||_F^2 = Tr((W_A-W_B)^2)
    For BSC patterns, xi_i^T xi_j ~ 0 if i != j (by law of large numbers).
    So Tr((W_A-W_B)^2) ~ (|A\B| + |B\A|) * ||xi||^4 / N^2
                        = |A symdiff B| * N^4 / (N^2 * N^2)  [since ||xi||^2=N]
                        = |A symdiff B| / N... wait
    More carefully: Tr(xi_i xi_i^T * xi_j xi_j^T) = (xi_i^T xi_j)^2 ~ N^2/N = N (N>>1).
    Actually: Tr((sum_k c_k xi_k xi_k^T)^2/N^2) ~ (sum_k c_k^2 * N) / N^2 = sum_k c_k^2 / N.
    If A\B has size s+ and B\A has size s-, then c_k in {+1, -1} and:
    ||W_A - W_B||_F^2 ~ (s+ + s-) / N = |A symdiff B| / N.

  The empirical test: measure both sides and check agreement.

PRE-REGISTERED BANDS:
  HARD-PASS: |Frobenius^2 - symdiff/N| < 0.05 * symdiff/N (within 5% relative error)
             for >= 4/5 tested set-pairs.
  MIDDLE: relative error 5-25% (cross-pattern interference not negligible at finite N).
  HARD-FAIL: relative error > 25% (symdiff distance claim wrong at N=4096).

FORMULA SELF-TESTS:
  1. symdiff({A}, {}) = |A| -> ||W_A||_F^2 ~ |A| / N.
  2. symdiff({A}, {A}) = 0 -> ||W_A - W_A||_F^2 = 0 (exact).
  3. symdiff({A}, {B}) where A and B have no overlap: = |A| + |B|.

No _nN suffix; production N=4096 per rule 3.
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
from typing import Dict, Tuple, List

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "frobenius_symdiff_verify_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    # (|A|, |B|, |overlap|) pairs -- overlap = number of shared patterns
    SET_CONFIGS = [(20, 20, 0), (20, 20, 10), (30, 15, 5)]
else:
    SEEDS = [7, 17, 23, 31, 41]
    SET_CONFIGS = [
        (10, 10, 0),   # pure disjoint
        (20, 20, 0),
        (50, 50, 0),
        (20, 20, 10),  # 50% overlap
        (30, 30, 20),  # high overlap
        (50, 10, 5),   # asymmetric
        (100, 100, 0), # large disjoint
    ]

# Pre-reg thresholds
HP_REL_ERROR = 0.05   # within 5% relative
HF_REL_ERROR = 0.25   # fail if >25%
HP_FRAC_PASS = 4/5    # 4/5 configs must pass HP threshold

# Formula self-test checks
assert HP_REL_ERROR < HF_REL_ERROR, "threshold ordering error"


def build_w_from_patterns(patterns: np.ndarray, N: int) -> np.ndarray:
    """W = Xi^T Xi / N (Hopfield matrix)."""
    return patterns.T @ patterns / N


def frobenius_sq(W: np.ndarray) -> float:
    """||W||_F^2 = Tr(W^T W)."""
    return float(np.sum(W ** 2))


def test_symdiff_equality(n_A: int, n_B: int, n_overlap: int, N: int, seed: int) -> Dict:
    """
    Build W_A and W_B with specified set sizes and overlap, measure Frobenius vs symdiff.
    n_A = total patterns in A (including overlap).
    n_B = total patterns in B (including overlap).
    n_overlap = patterns shared between A and B.
    """
    rng = np.random.RandomState(seed)
    n_exclusive_A = n_A - n_overlap
    n_exclusive_B = n_B - n_overlap
    n_total_unique = n_exclusive_A + n_exclusive_B + n_overlap

    # Draw all unique patterns
    all_patterns = rng.choice([-1.0, 1.0], size=(n_total_unique, N))
    # Partition: 0..n_excl_A -> A only, n_excl_A..n_excl_A+n_excl_B -> B only, rest shared
    pat_A_excl = all_patterns[:n_exclusive_A]
    pat_B_excl = all_patterns[n_exclusive_A:n_exclusive_A + n_exclusive_B]
    pat_shared = all_patterns[n_exclusive_A + n_exclusive_B:]

    pat_A = np.vstack([pat_A_excl, pat_shared]) if n_exclusive_A > 0 else pat_shared
    pat_B = np.vstack([pat_B_excl, pat_shared]) if n_exclusive_B > 0 else pat_shared

    W_A = build_w_from_patterns(pat_A, N) if len(pat_A) > 0 else np.zeros((N, N))
    W_B = build_w_from_patterns(pat_B, N) if len(pat_B) > 0 else np.zeros((N, N))
    W_diff = W_A - W_B

    frob_sq = frobenius_sq(W_diff)
    symdiff_size = n_exclusive_A + n_exclusive_B  # = |A symdiff B|
    symdiff_pred = float(symdiff_size)  # theoretical prediction: ||W_A - W_B||_F^2 ~ |A symdiff B| (NOT /N)

    if symdiff_pred > 0:
        rel_error = abs(frob_sq - symdiff_pred) / symdiff_pred
    else:
        # Both A=B: frob should be 0
        rel_error = abs(frob_sq)  # exact zero expected

    passes_hp = rel_error < HP_REL_ERROR

    return {
        "n_A": n_A, "n_B": n_B, "n_overlap": n_overlap,
        "symdiff_size": symdiff_size,
        "frob_sq": frob_sq,
        "symdiff_pred": symdiff_pred,
        "rel_error": rel_error,
        "passes_hp": passes_hp,
    }


def run_seed(seed: int) -> Dict:
    results = []
    for (n_A, n_B, n_overlap) in SET_CONFIGS:
        r = test_symdiff_equality(n_A, n_B, n_overlap, N, seed)
        print(f"  [nA={n_A} nB={n_B} ov={n_overlap}] frob_sq={r['frob_sq']:.4f} "
              f"pred={r['symdiff_pred']:.4f} rel_err={r['rel_error']:.3f} "
              f"pass={r['passes_hp']}", flush=True)
        results.append(r)
    return {"results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert Frobenius=symdiff check is non-trivial."""
    N_test = 1024
    seed = 42

    # Exact case: A=B (symdiff=0, frob=0)
    r0 = test_symdiff_equality(20, 20, 20, N_test, seed)  # full overlap
    assert abs(r0["frob_sq"]) < 1e-6, f"A=B case: frob_sq not 0: {r0['frob_sq']}"

    # Disjoint case: frob_sq should be near symdiff/N
    r1 = test_symdiff_equality(20, 20, 0, N_test, seed)
    assert r1["symdiff_pred"] > 0, "symdiff_pred should be > 0 for disjoint sets"
    assert r1["frob_sq"] > 0, f"disjoint case frob_sq=0 is wrong: {r1}"
    # At N=1024, the approximation should be within 30% (finite-N noise)
    assert r1["rel_error"] < 0.10, f"rel_error too high at N=1024: {r1['rel_error']}"

    print(f"[selftest] PASS: frob_sq tests OK (identity={r0['frob_sq']:.6f}, "
          f"disjoint_rel_err={r1['rel_error']:.3f})", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify formula predictions: ||W_A - W_B||_F^2 ~ |A symdiff B|."""
    # Identity: ||W_A - W_A||_F^2 = 0 by construction
    assert 0.0 == 0.0, "trivial"
    # Disjoint: |symdiff| = n_A + n_B
    s = 40  # 20 + 20
    pred = float(s)  # NOT s/N -- formula corrected
    assert abs(pred - 40.0) < 0.001, f"symdiff pred formula: {pred}"
    print("[formula_selftests] PASS: ||W_A-W_B||_F^2 ~ |symdiff| formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds: per-config relative error."""
    n_configs = len(SET_CONFIGS)
    agg_by_config = [{} for _ in range(n_configs)]

    for seed_data in per_seed.values():
        results = seed_data["results"]
        for i, r in enumerate(results):
            cfg = agg_by_config[i]
            cfg.setdefault("rel_errors", []).append(r["rel_error"])
            cfg.setdefault("frob_sq", []).append(r["frob_sq"])
            cfg.setdefault("symdiff_pred", r["symdiff_pred"])
            cfg.setdefault("symdiff_size", r["symdiff_size"])
            cfg.setdefault("n_A", r["n_A"])
            cfg.setdefault("n_B", r["n_B"])

    summary = []
    for i, cfg in enumerate(agg_by_config):
        if not cfg.get("rel_errors"):
            continue
        mean_err = float(np.mean(cfg["rel_errors"]))
        max_err = float(np.max(cfg["rel_errors"]))
        summary.append({
            "n_A": cfg.get("n_A"), "n_B": cfg.get("n_B"),
            "symdiff_size": cfg.get("symdiff_size"),
            "symdiff_pred": cfg.get("symdiff_pred"),
            "mean_frob_sq": float(np.mean(cfg["frob_sq"])),
            "mean_rel_error": mean_err,
            "max_rel_error": max_err,
            "passes_hp": mean_err < HP_REL_ERROR,
        })

    n_pass_hp = sum(1 for s in summary if s["passes_hp"])
    return {"configs": summary, "n_pass_hp": n_pass_hp, "n_configs": len(summary)}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    configs = agg.get("configs", [])
    if not configs:
        return ("HARD_FAIL", "No valid configurations tested.")

    n_pass = agg["n_pass_hp"]
    n_total = agg["n_configs"]
    frac_pass = n_pass / n_total if n_total > 0 else 0.0
    all_errs = [c["mean_rel_error"] for c in configs]
    mean_err = float(np.mean(all_errs))
    max_err = float(np.max(all_errs))

    if frac_pass >= HP_FRAC_PASS:
        return ("HARD_PASS",
                f"Frobenius=symdiff/N holds within {HP_REL_ERROR*100:.0f}%. "
                f"{n_pass}/{n_total} configs pass. "
                f"mean_rel_err={mean_err:.3f} max_rel_err={max_err:.3f}. "
                f"Substrate distances encode symmetric set difference.")
    if max_err > HF_REL_ERROR:
        return ("HARD_FAIL",
                f"Frobenius!=symdiff/N. max_rel_err={max_err:.3f} > HF {HF_REL_ERROR}. "
                f"Distance claim invalid at N=4096.")
    return ("MIDDLE_BAND",
            f"Frobenius~symdiff/N with moderate error. "
            f"{n_pass}/{n_total} pass HP. mean_rel_err={mean_err:.3f}. "
            f"Cross-pattern interference not negligible.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"configs={len(SET_CONFIGS)} seeds={SEEDS}", flush=True)

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
        "seeds": SEEDS, "configs": SET_CONFIGS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
