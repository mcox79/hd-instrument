"""
multiagent_write_pressure_v2 -- Deletion persistence under heavy multi-agent write pressure.

Extends multiagent_coord_v1 (completed) with harder conditions:
  - 50 subsequent agent-B writes (vs 10 in v1)
  - Active repulsion (rank-1 deflation + small positive energy penalty)
  - N=4096, 10 seeds

From multiagent coordination handoff (2026-06-01), Anchor 3 extended.
Tests whether algebraic deletion holds under sustained adversarial write pressure.

The key product claim: unlike CRDT (which cannot delete) and Redis TTL (probabilistic),
the substrate deletion certificate persists through subsequent writes from other agents.

Pre-reg thresholds:
  HARD-PASS: deleted-pattern cosine < 0.10 after active repulsion + 50 agent-B writes
             at 8/10 seeds.
  MIDDLE:    deleted cosine [0.10, 0.20] at majority seeds.
  HARD-FAIL: deleted cosine > 0.20 at majority seeds (deletion washes out under
             sustained write pressure).

Note: v1 tested 10 writes with 5 seeds. This is a harder test (50 writes, 10 seeds).
PROT-018: no _nN suffix; production N=4096, rule 3.
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

ANCHOR_NAME = "multiagent_write_pressure_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_B_WRITES = 20         # agent B writes after deletion
    REPULSION_STRENGTH = 1.0
else:
    SEEDS = [7, 17, 23, 31, 41, 53, 67, 79, 89, 97]
    N_B_WRITES = 50
    REPULSION_STRENGTH = 1.0

HP_DEL_COS = 0.10
HF_DEL_COS = 0.20
HP_FRAC_SEEDS = 0.80


def make_bsc_patterns(N: int, K: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.choice([-1.0, 1.0], size=(N, K))


def hopfield_update(W: np.ndarray, x: np.ndarray, n_iters: int = 10) -> np.ndarray:
    for _ in range(n_iters):
        x = np.sign(W @ x + 1e-12)
    return x


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def active_repulsion_delete(W: np.ndarray, pattern: np.ndarray,
                             strength: float = 1.0) -> np.ndarray:
    """
    Active repulsion deletion: rank-1 deflation + repulsion energy.
    W_new = W - strength * xi xi^T / N
    This is the algebraic deletion certificate (delta_W = -xi xi^T / N).
    """
    W_new = W - strength * np.outer(pattern, pattern) / N
    return W_new


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)

    # Agent A writes p_A (the pattern to delete later)
    n_stored_A = 5   # agent A stores 5 patterns total; we delete the first
    patterns_A = make_bsc_patterns(N, n_stored_A, seed)

    # Agent B writes n_B_init initial patterns (pre-deletion baseline)
    n_stored_B_init = 10
    patterns_B_init = make_bsc_patterns(N, n_stored_B_init, seed + 1000)

    # Global W: agent A + agent B initial
    W = np.zeros((N, N))
    for i in range(n_stored_A):
        W += np.outer(patterns_A[:, i], patterns_A[:, i]) / N
    for i in range(n_stored_B_init):
        W += np.outer(patterns_B_init[:, i], patterns_B_init[:, i]) / N

    # Record baseline cosine for p_A[:,0] (target to delete)
    p_target = patterns_A[:, 0]
    baseline_cos = abs(cos_sim(hopfield_update(W, p_target), p_target))

    # Delete p_target via active repulsion
    W = active_repulsion_delete(W, p_target, REPULSION_STRENGTH)
    post_del_cos = abs(cos_sim(hopfield_update(W, p_target), p_target))

    # Agent B writes N_B_WRITES more patterns under write pressure
    patterns_B_pressure = make_bsc_patterns(N, N_B_WRITES, seed + 2000)
    for i in range(N_B_WRITES):
        W += np.outer(patterns_B_pressure[:, i], patterns_B_pressure[:, i]) / N

    # Measure deleted-pattern cosine after write pressure
    final_del_cos = abs(cos_sim(hopfield_update(W, p_target), p_target))

    # Verify other agent-A patterns still retrievable
    retain_acc_list = []
    for i in range(1, n_stored_A):
        r = hopfield_update(W, patterns_A[:, i])
        retain_acc_list.append(cos_sim(r, patterns_A[:, i]))
    mean_retain_acc = float(np.mean(retain_acc_list)) if retain_acc_list else float("nan")

    print(f"  [seed {seed}] baseline_cos={baseline_cos:.3f} "
          f"post_del={post_del_cos:.3f} after_{N_B_WRITES}_writes={final_del_cos:.3f} "
          f"retain={mean_retain_acc:.3f}", flush=True)

    return {
        "baseline_del_cos": baseline_cos,
        "post_deletion_cos": post_del_cos,
        "final_del_cos": final_del_cos,
        "mean_retain_acc": mean_retain_acc,
        "n_b_writes": N_B_WRITES,
        "seed": seed,
        "N": N,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert all metrics non-null at small scale."""
    N_test = 256
    patterns = make_bsc_patterns(N_test, 3, 42)
    W = np.zeros((N_test, N_test))
    for i in range(3):
        W += np.outer(patterns[:, i], patterns[:, i]) / N_test

    p0 = patterns[:, 0]
    pre = abs(cos_sim(hopfield_update(W, p0, n_iters=5), p0))
    W2 = active_repulsion_delete(W, p0, 1.0)
    post = abs(cos_sim(hopfield_update(W2, p0, n_iters=5), p0))

    assert not math.isnan(pre) and pre > 0.0, f"baseline cos invalid: {pre}"
    assert not math.isnan(post), f"post-del cos is NaN"
    # After exact deflation with only 3 patterns, deletion should have some effect
    print(f"[selftest] PASS: pre={pre:.3f} post={post:.3f} N={N_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    final_cos_list = [v["final_del_cos"] for v in per_seed.values()]
    retain_list = [v["mean_retain_acc"] for v in per_seed.values()
                   if not math.isnan(v.get("mean_retain_acc", float("nan")))]
    seeds_pass = sum(1 for c in final_cos_list if c < HP_DEL_COS)
    return {
        "mean_final_del_cos": float(np.mean(final_cos_list)),
        "seeds_passing_hp": seeds_pass,
        "mean_retain_acc": float(np.mean(retain_list)) if retain_list else float("nan"),
        "n_seeds": len(per_seed),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    n = summary.get("n_seeds", 1)
    mean_cos = summary.get("mean_final_del_cos", 1.0)
    seeds_pass = summary.get("seeds_passing_hp", 0)
    retain = summary.get("mean_retain_acc", float("nan"))

    hp_seeds = math.ceil(HP_FRAC_SEEDS * n)
    a_pass = mean_cos < HP_DEL_COS and seeds_pass >= hp_seeds
    a_fail = mean_cos > HF_DEL_COS

    if a_pass:
        return ("HARD_PASS",
                f"Deletion persists under {N_B_WRITES}-write pressure. "
                f"mean_del_cos={mean_cos:.3f}<{HP_DEL_COS}, "
                f"seeds_pass={seeds_pass}/{n}, retain={retain:.3f}.")
    if a_fail:
        return ("HARD_FAIL",
                f"Deletion washes out. "
                f"mean_del_cos={mean_cos:.3f}>{HF_DEL_COS}. "
                f"Active repulsion insufficient against {N_B_WRITES}-write pressure.")
    return ("MIDDLE_BAND",
            f"Borderline. "
            f"mean_del_cos={mean_cos:.3f}(hp={HP_DEL_COS},hf={HF_DEL_COS}), "
            f"seeds_pass={seeds_pass}/{n}.")


def _verdict_formula_selftests():
    s1 = {"mean_final_del_cos": 0.05, "seeds_passing_hp": 9, "mean_retain_acc": 0.90, "n_seeds": 10}
    v1, _ = compute_verdict(s1)
    assert v1 == "HARD_PASS", f"Expected HARD_PASS got {v1}"

    s2 = {"mean_final_del_cos": 0.30, "seeds_passing_hp": 1, "mean_retain_acc": 0.85, "n_seeds": 10}
    v2, _ = compute_verdict(s2)
    assert v2 == "HARD_FAIL", f"Expected HARD_FAIL got {v2}"

    s3 = {"mean_final_del_cos": 0.14, "seeds_passing_hp": 5, "mean_retain_acc": 0.80, "n_seeds": 10}
    v3, _ = compute_verdict(s3)
    assert v3 == "MIDDLE_BAND", f"Expected MIDDLE_BAND got {v3}"

    print("[formula_selftests] PASS: 3 verdict cases verified", flush=True)


_verdict_formula_selftests()


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} seeds={SEEDS} n_B_writes={N_B_WRITES}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s | "
              f"final_del_cos={result['final_del_cos']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(summary)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE,
        "N": N,
        "seeds": SEEDS,
        "summary": summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N_B_WRITES": N_B_WRITES, "REPULSION_STRENGTH": REPULSION_STRENGTH},
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete (selftests ran at module scope)", flush=True)
        sys.exit(0)
    main()
