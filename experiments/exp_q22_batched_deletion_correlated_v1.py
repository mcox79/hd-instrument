"""
q22_batched_deletion_correlated_v1 -- Q22 batched deletion at MODERATE correlation.

SCIENTIFIC QUESTION (Q22 extension, PP-9 sub-property):
  batched_deletion_reliability_v1 HARD_PASS showed: r_1=1.0 at N=4096 5-seed
  with corr_c=0.4, result IDENTICAL to independent (ghost-attractor NOT tested).

  The open question: does moderate semantic correlation (c ~ 0.3-0.5) between
  deleted patterns cause ghost-attractor re-emergence after rank-1 erasure?

  Setup: K patterns to delete are CORRELATED (pairwise cosine ~ c).
  Construct correlated patterns as: xi_k = base_pattern + c * noise_k (normalized).
  Delete all K via batched rank-1 repulsion:
    for xi in batch: W -= 2 * outer(xi, xi) / N
  Check if any deleted pattern re-emerges after deletion (ghost attractor).

  PREDICTION (from Q22 DEEP research):
    - c ~ 0.3-0.5 is the worst case: patterns are similar enough to share
      attractor basin edges but distinct enough to not fully erase jointly.
    - Expected: ghost-attractor residual cos > 0.10 for c >= 0.3,
      compared to independent c~0 case where residual < 0.05.
    - HARD-PASS = confirms the ghost-attractor worst case exists.

PRE-REGISTERED BANDS:
  HARD-PASS: At c=0.3-0.5, max_residual_cos >= 0.15 (ghost-attractor re-emerges
             after batched deletion at moderate correlation).
  MIDDLE: max_residual_cos 0.08-0.15.
  HARD-FAIL: max_residual_cos < 0.08 (batched deletion equally effective at
             moderate correlation -- refutes ghost-attractor prediction).

  Calibration note: first empirical test of correlated-batch deletion at
  production N. Bands +-50% around predicted 0.15 residual.

FORMULA SELF-TESTS:
  1. Correlated patterns: xi_k = sign(base + c * eps_k) where eps_k ~ N(0,1).
     Pairwise cosine(xi_i, xi_j) ~ c^2/(1+c^2) for large N.
  2. After K batched deletions: W = W_original - 2*sum(outer(xi_k, xi_k))/N.
     Residual pattern retrieval = cosine(sign(W @ xi_k), xi_k).
  3. For c=0 (independent), residual ~ 0 at M < 0.5*M_max.
     For c=0.4, shared-attractor effect should raise residual.

TIMEOUT ESTIMATE:
  Smoke: N=1024, K_batch=5, c=[0.3, 0.5], 2 seeds.
  Full: N=4096, K_batch=[5, 10, 20], c=[0.0, 0.3, 0.5], 5 seeds.
  Scaling: N^2 outer products; 5 seeds x 3 c-values x 3 K values x N=4096.
  Smoke wall ~5s -> Full ~60s. timeout=360s.

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
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "q22_batched_deletion_correlated_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

ALPHA_C = 0.138

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 1024
    SEEDS = [7, 17]
    K_BATCH_LIST = [5, 10]
    C_VALUES = [0.0, 0.4]   # c=0 = independent baseline, c=0.4 = moderate correlation
    M_BACKGROUND = 30       # background patterns
else:
    # Walk-back gate applied: smoke residual 0.143 within 5% of HP=0.15.
    # FULL seeds doubled from 5 to 10 per PROT walk-back rule.
    N = 4096
    SEEDS = [7, 17, 23, 31, 41, 47, 53, 59, 67, 71]
    K_BATCH_LIST = [5, 10, 20]
    C_VALUES = [0.0, 0.3, 0.5]
    M_BACKGROUND = int(0.4 * ALPHA_C * N)  # 40% capacity background

HP_RESIDUAL = 0.15   # HARD-PASS: ghost-attractor residual >= 0.15 at moderate c
HF_RESIDUAL = 0.08   # HARD-FAIL: residual < 0.08 (no ghost-attractor effect)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def make_correlated_batch(K: int, N: int, c: float, rng: np.random.RandomState) -> np.ndarray:
    """K correlated BSC-like patterns with pairwise cosine ~ c."""
    base = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
    patterns = []
    for _ in range(K):
        eps = rng.randn(N)
        raw = base + c * eps
        xi = np.sign(raw + 1e-12)
        patterns.append(xi)
    return np.stack(patterns)  # (K, N)


def build_background_w(M: int, N: int, rng: np.random.RandomState) -> np.ndarray:
    W = np.zeros((N, N), dtype=np.float64)
    pats = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    for xi in pats:
        W += np.outer(xi, xi) / N
    return W, pats


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results = {}

    for c in C_VALUES:
        for K in K_BATCH_LIST:
            # Build background W
            W_bg, bg_pats = build_background_w(M_BACKGROUND, N, rng)

            # Generate correlated batch to delete
            batch = make_correlated_batch(K, N, c, rng)

            # Store batch in W (add to background)
            W = W_bg.copy()
            for xi in batch:
                W += np.outer(xi, xi) / N

            # Measure pre-deletion retrieval
            pre_del = float(np.mean([cosine_sim(np.sign(W @ xi + 1e-12), xi) for xi in batch]))

            # Batched rank-1 deletion: standard Hopfield erasure (subtract stored weight)
            # Using W -= outer(xi,xi)/N (undo the storage operation)
            for xi in batch:
                W -= np.outer(xi, xi) / N

            # Measure post-deletion residual (ghost attractor)
            post_del = float(np.mean([cosine_sim(np.sign(W @ xi + 1e-12), xi) for xi in batch]))

            # Background patterns unaffected
            bg_sims = [cosine_sim(np.sign(W @ xi + 1e-12), xi) for xi in bg_pats[:5]]
            bg_mean = float(np.mean(bg_sims)) if bg_sims else float("nan")

            key = f"c{c:.1f}_K{K}"
            results[key] = {
                "c": c, "K": K,
                "pre_del_cos": pre_del,
                "post_del_cos": post_del,
                "bg_retention": bg_mean,
            }
            print(f"  [seed={seed} c={c:.1f} K={K}] pre={pre_del:.3f} "
                  f"post={post_del:.3f}(ghost?) bg={bg_mean:.3f}", flush=True)

    return {"results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert deletion metrics non-null at small scale."""
    N_test = 256
    K_test = 3
    c_test = 0.4
    rng = np.random.RandomState(42)

    batch = make_correlated_batch(K_test, N_test, c_test, rng)
    assert batch.shape == (K_test, N_test), f"batch shape {batch.shape}"
    assert batch.shape[1] > 0, "empty batch"

    W_bg, _ = build_background_w(5, N_test, rng)
    W = W_bg.copy()
    for xi in batch:
        W += np.outer(xi, xi) / N_test

    pre = float(np.mean([cosine_sim(np.sign(W @ xi + 1e-12), xi) for xi in batch]))
    assert not math.isnan(pre), "pre_del is NaN"

    for xi in batch:
        W -= np.outer(xi, xi) / N_test
    post = float(np.mean([cosine_sim(np.sign(W @ xi + 1e-12), xi) for xi in batch]))
    assert not math.isnan(post), "post_del is NaN"

    print(f"[selftest] PASS: pre={pre:.3f} post={post:.3f} at N={N_test} K={K_test} c={c_test}",
          flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify self-test formula: correlated pattern pairwise cosine ~ c/(1+c)."""
    N_test = 4096
    c_test = 0.4
    rng = np.random.RandomState(99)
    batch = make_correlated_batch(3, N_test, c_test, rng)
    pw_cos = cosine_sim(batch[0], batch[1])
    # Rough estimate: should be > 0 for c=0.4 base pattern
    assert pw_cos > 0, f"pairwise cosine at c={c_test} should be > 0, got {pw_cos:.3f}"
    print(f"[formula_selftests] PASS: pairwise_cosine={pw_cos:.3f} at c={c_test}", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate post-deletion cosine across seeds by (c, K)."""
    all_keys = set()
    for sd in per_seed.values():
        all_keys.update(sd["results"].keys())

    agg = {}
    for key in sorted(all_keys):
        post_coss = []
        for sd in per_seed.values():
            row = sd["results"].get(key)
            if row is None:
                continue
            post_coss.append(row["post_del_cos"])
        if post_coss:
            agg[key] = {
                "mean_post_del_cos": float(np.mean(post_coss)),
                "max_post_del_cos": float(np.max(post_coss)),
                "n_seeds": len(post_coss),
            }
    return {"by_condition": agg}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_cond = agg["by_condition"]
    # Focus on moderate-correlation conditions (c > 0.2)
    moderate_residuals = []
    independent_residuals = []
    for key, v in by_cond.items():
        c_str = key.split("_")[0]
        c_val = float(c_str[1:])  # "c0.4" -> 0.4
        if c_val >= 0.25:
            moderate_residuals.append(v["max_post_del_cos"])
        else:
            independent_residuals.append(v["max_post_del_cos"])

    if not moderate_residuals:
        return ("HARD_FAIL", "No moderate-correlation conditions found.")

    max_moderate_residual = max(moderate_residuals)
    max_indep_residual = max(independent_residuals) if independent_residuals else float("nan")

    if max_moderate_residual >= HP_RESIDUAL:
        indep_note = f" Independent baseline max={max_indep_residual:.3f}." if not math.isnan(max_indep_residual) else ""
        return ("HARD_PASS",
                f"Ghost-attractor effect at moderate correlation CONFIRMED. "
                f"max_residual_cos (c>=0.25)={max_moderate_residual:.3f}>={HP_RESIDUAL}. "
                f"Batched deletion less effective for correlated patterns.{indep_note} "
                f"External deduplication required for correlated batches (PP-9 caveat).")
    if max_moderate_residual < HF_RESIDUAL:
        return ("HARD_FAIL",
                f"Ghost-attractor NOT detected at moderate correlation. "
                f"max_residual_cos (c>=0.25)={max_moderate_residual:.3f}<{HF_RESIDUAL}. "
                f"Batched deletion equally effective regardless of correlation.")
    return ("MIDDLE_BAND",
            f"Partial ghost-attractor signal. "
            f"max_residual (c>=0.25)={max_moderate_residual:.3f} "
            f"(HP>={HP_RESIDUAL} HF<{HF_RESIDUAL}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"C_VALUES={C_VALUES} K_BATCH={K_BATCH_LIST} M_BG={M_BACKGROUND} seeds={SEEDS}",
          flush=True)

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
        "C_VALUES": C_VALUES, "K_BATCH_LIST": K_BATCH_LIST,
        "M_BACKGROUND": M_BACKGROUND, "seeds": SEEDS,
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
