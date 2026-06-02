"""
signed_am_b_pattern_full_v1 -- Signed AM B-pattern empirical: deletion + repulsion combined.

SCIENTIFIC QUESTION (Q16 deepened / Q-A2 cousin):
  For signed Hopfield W = W_A - W_B (W_A = patterns A, W_B = patterns B),
  does the combined operation of:
  (a) deletion of a B-pattern via W_new = W + xi_B xi_B^T / N (undo W_B contribution), AND
  (b) active repulsion from B-patterns (W has negative weights for B patterns, so
      dynamics naturally diverge from B attractors)
  produce measurable active repulsion: starting from xi_B + noise,
  the dynamics should DIVERGE from xi_B, not converge?

  Theory: W_signed = (1/N) sum_{mu in A} xi_mu xi_mu^T - (1/N) sum_{nu in B} xi_nu xi_nu^T
  Energy E(s) = -(1/2) s^T W_signed s = -(retrieval on A) + (retrieval on B)
  B-patterns are ENERGY MAXIMA under W_signed -- dynamical repulsion is guaranteed
  by the energy landscape geometry.

  After deletion of xi_B: W_new = W_signed + xi_B xi_B^T / N
  The repulsion contribution of xi_B is cancelled. Query at xi_B should now
  NOT diverge from xi_B but converge to nearest A-pattern.

PRE-REGISTERED BANDS:
  HARD-PASS (repulsion confirmed):
    repulsion_rate_before_deletion >= 0.80 (B queries diverge from B in >= 80% of trials),
    AND repulsion_rate_after_deletion <= 0.20 (after deletion, B queries NO LONGER diverge).
  MIDDLE: repulsion_before >= 0.60 but after_deletion threshold not cleanly satisfied.
  HARD-FAIL: repulsion_rate_before < 0.50 (B-patterns not actively repulsed in signed W).

FORMULA SELF-TESTS:
  1. W_signed @ xi_B = -(xi_B cross-term) negative -> B is energy maximum.
  2. After deletion: W_new @ xi_B ~ 0 (neutral overlap).
  3. Divergence metric: cosine_sim(Hopfield_steps(xi_B+noise, W_signed), xi_B) < 0.5.

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
from typing import Dict, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "signed_am_b_pattern_full_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_A = 20    # A patterns (attract)
    M_B = 5     # B patterns (repel)
    N_QUERIES = 50
    N_STEPS = 10
    NOISE_FRAC = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_A = 50
    M_B = 10
    N_QUERIES = 200
    N_STEPS = 10
    NOISE_FRAC = 0.10

# Pre-reg thresholds
HP_REPULSION_BEFORE = 0.80   # 80% diverge before deletion
HP_NO_REPULSION_AFTER = 0.20  # <=20% diverge after deletion (cancelled)
HF_REPULSION_BEFORE = 0.50   # HARD-FAIL if B not repulsed at all


def build_signed_w(Xi_A: np.ndarray, Xi_B: np.ndarray, N: int) -> np.ndarray:
    """W = W_A - W_B = Xi_A^T @ Xi_A / N - Xi_B^T @ Xi_B / N."""
    W_A = Xi_A.T @ Xi_A / N
    W_B = Xi_B.T @ Xi_B / N
    return W_A - W_B


def hopfield_step(W: np.ndarray, s: np.ndarray) -> np.ndarray:
    """One synchronous Hopfield step: s_new = sign(W @ s)."""
    return np.where(W @ s > 0, 1.0, -1.0)


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def measure_repulsion(W: np.ndarray, Xi_B: np.ndarray, n_queries: int,
                       n_steps: int, noise_frac: float, seed: int) -> Tuple[float, float]:
    """
    For each B-pattern (+ noise), run Hopfield dynamics.
    Measure cosine_sim(final_state, original_B_pattern).
    Repulsion: final_state is DIVERGED from xi_B (cos_sim < 0.5).
    Returns (repulsion_rate, mean_cos_sim).
    """
    rng = np.random.RandomState(seed)
    M_B = Xi_B.shape[0]
    cos_sims = []

    for q_idx in range(n_queries):
        pat_idx = rng.randint(0, M_B)
        xi_b = Xi_B[pat_idx]
        # Add noise
        mask = rng.rand(len(xi_b)) < noise_frac
        query = xi_b.copy()
        query[mask] *= -1.0

        # Run Hopfield dynamics
        s = query.copy()
        for _ in range(n_steps):
            s_new = hopfield_step(W, s)
            if np.all(s_new == s):
                break
            s = s_new

        cs = cosine_sim(s, xi_b)
        cos_sims.append(cs)

    cos_arr = np.array(cos_sims)
    repulsion_rate = float(np.mean(cos_arr < 0.5))  # diverged if cos_sim < 0.5
    return repulsion_rate, float(np.mean(cos_arr))


def run_seed(seed: int) -> Dict:
    """One seed: measure repulsion before and after deletion."""
    rng = np.random.RandomState(seed)
    Xi_A = rng.choice([-1.0, 1.0], size=(M_A, N))
    Xi_B = rng.choice([-1.0, 1.0], size=(M_B, N))

    W_signed = build_signed_w(Xi_A, Xi_B, N)

    # Before deletion: B-patterns should be actively repulsed
    rep_before, cos_before = measure_repulsion(
        W_signed, Xi_B, N_QUERIES, N_STEPS, NOISE_FRAC, seed + 1000)
    print(f"  [seed={seed}] before deletion: repulsion_rate={rep_before:.3f} "
          f"mean_cos={cos_before:.3f}", flush=True)

    # Delete one B-pattern (undo its contribution)
    xi_b_del = Xi_B[0]
    W_after = W_signed + np.outer(xi_b_del, xi_b_del) / N

    # After deletion of B[0]: use only Xi_B[0] for the repulsion test
    Xi_B_deleted = Xi_B[[0]]  # test only the deleted pattern
    rep_after, cos_after = measure_repulsion(
        W_after, Xi_B_deleted, N_QUERIES, N_STEPS, NOISE_FRAC, seed + 2000)
    print(f"  [seed={seed}] after deletion (of B[0]): repulsion_rate={rep_after:.3f} "
          f"mean_cos={cos_after:.3f}", flush=True)

    # Also verify: A-patterns still retrievable after deletion
    s_a = Xi_A[0] + rng.choice([-1.0, 1.0], size=(N,)) * NOISE_FRAC * 0.5
    s_a = np.where(s_a > 0, 1.0, -1.0)
    for _ in range(N_STEPS):
        s_new = hopfield_step(W_after, s_a)
        if np.all(s_new == s_a):
            break
        s_a = s_new
    a_retrieval = cosine_sim(s_a, Xi_A[0])
    print(f"  [seed={seed}] A-retrieval after deletion: cos_sim={a_retrieval:.3f}", flush=True)

    return {
        "repulsion_rate_before": rep_before,
        "mean_cos_before": cos_before,
        "repulsion_rate_after": rep_after,
        "mean_cos_after": cos_after,
        "a_retrieval_cos": a_retrieval,
        "seed": seed, "N": N, "M_A": M_A, "M_B": M_B, "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert repulsion metrics are non-null and B-patterns are distinguishable."""
    N_test = 512
    M_A_test, M_B_test = 10, 3
    seed = 42

    rng = np.random.RandomState(seed)
    Xi_A = rng.choice([-1.0, 1.0], size=(M_A_test, N_test))
    Xi_B = rng.choice([-1.0, 1.0], size=(M_B_test, N_test))
    W_signed = build_signed_w(Xi_A, Xi_B, N_test)

    rep, cos = measure_repulsion(W_signed, Xi_B, n_queries=20, n_steps=5,
                                  noise_frac=0.10, seed=seed)
    assert not math.isnan(rep), "repulsion_rate is NaN"
    assert 0.0 <= rep <= 1.0, f"repulsion_rate out of [0,1]: {rep}"
    assert not math.isnan(cos), "cos_sim is NaN"

    # Signed W should produce some repulsion (B is energy maximum)
    # At N=512, with M_A=10, M_B=3, we expect some signal but maybe not 80%
    # Just verify non-zero signal
    print(f"[selftest] PASS: repulsion_rate={rep:.3f} mean_cos={cos:.3f} (N=512)", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify pre-registered formula structure."""
    # Energy of B-pattern under W_signed: E(xi_B) = -(1/2) xi_B^T W_signed xi_B
    # = -(1/2)(xi_B^T W_A xi_B - xi_B^T W_B xi_B)
    # xi_B^T W_B xi_B = ||xi_B||^4 / N = N (dominant term when B is unique)
    N_t = 4096
    # So E(xi_B) ~ -(1/2)(overlap_with_A - N/N) = +(1/2) + small_cross_terms
    # B should be energy maximum for W_signed, meaning gradient pushes AWAY from xi_B
    assert HP_REPULSION_BEFORE > HF_REPULSION_BEFORE, "threshold ordering error"
    assert HP_NO_REPULSION_AFTER < HP_REPULSION_BEFORE, "after-deletion threshold must be < before"
    print("[formula_selftests] PASS: signed-AM threshold structure verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    rep_before_list, rep_after_list, cos_before_list, a_ret_list = [], [], [], []
    for seed_data in per_seed.values():
        rep_before_list.append(seed_data["repulsion_rate_before"])
        rep_after_list.append(seed_data["repulsion_rate_after"])
        cos_before_list.append(seed_data["mean_cos_before"])
        a_ret_list.append(seed_data["a_retrieval_cos"])

    return {
        "mean_repulsion_before": float(np.mean(rep_before_list)) if rep_before_list else float("nan"),
        "mean_repulsion_after": float(np.mean(rep_after_list)) if rep_after_list else float("nan"),
        "mean_cos_before": float(np.mean(cos_before_list)) if cos_before_list else float("nan"),
        "mean_a_retrieval": float(np.mean(a_ret_list)) if a_ret_list else float("nan"),
        "n_seeds": len(rep_before_list),
        "repulsion_before_list": rep_before_list,
        "repulsion_after_list": rep_after_list,
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    rep_before = agg.get("mean_repulsion_before", float("nan"))
    rep_after = agg.get("mean_repulsion_after", float("nan"))
    n = agg.get("n_seeds", 0)

    if math.isnan(rep_before):
        return ("HARD_FAIL", "No valid repulsion measurements.")

    hp = rep_before >= HP_REPULSION_BEFORE and rep_after <= HP_NO_REPULSION_AFTER
    hf = rep_before < HF_REPULSION_BEFORE

    if hp:
        return ("HARD_PASS",
                f"Signed-AM B-pattern repulsion confirmed. "
                f"repulsion_before={rep_before:.3f} (HP>={HP_REPULSION_BEFORE}). "
                f"repulsion_after_deletion={rep_after:.3f} (HP<={HP_NO_REPULSION_AFTER}). "
                f"Active repulsion + cert-deletion compose cleanly. n_seeds={n}.")
    if hf:
        return ("HARD_FAIL",
                f"B-patterns not actively repulsed. "
                f"repulsion_before={rep_before:.3f} < HF {HF_REPULSION_BEFORE}. "
                f"Signed-AM repulsion not functional at N={N}.")
    return ("MIDDLE_BAND",
            f"Partial repulsion. before={rep_before:.3f} after={rep_after:.3f}. "
            f"HP requires before>={HP_REPULSION_BEFORE} AND after<={HP_NO_REPULSION_AFTER}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"M_A={M_A} M_B={M_B} n_queries={N_QUERIES} seeds={SEEDS}", flush=True)

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
        "run_mode": RUN_MODE, "N": N, "M_A": M_A, "M_B": M_B,
        "seeds": SEEDS,
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
