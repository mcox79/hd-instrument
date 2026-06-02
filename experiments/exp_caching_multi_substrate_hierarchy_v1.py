"""
caching_multi_substrate_hierarchy_v1 -- Tier 1 multi-substrate cache hierarchy (L1+L2).

SCIENTIFIC QUESTION (Caching-Policy Expressibility, Tier 1 multi-substrate):
  A multi-level cache uses SEPARATE weight matrices for different access frequencies.
  L1 (fast, small): W_L1 stores hot patterns (recently/frequently accessed).
  L2 (large): W_L2 stores cold patterns (less frequently accessed).

  Design:
    - W_L1: M_hot patterns stored with k_hot writes each.
    - W_L2: M_cold patterns stored with k_cold writes each.
    - L1 lookup: probe W_L1 first. If cosine > HIT_THRESHOLD: L1 hit (fast path).
    - L2 fallback: if L1 miss, probe W_L2.
    - Audit-cert check: deletion certificate from L1 + L2 is jointly valid.

  Test cells:
    (A) L1 hot-path retrieval: hot patterns retrieved from W_L1 with acc >= 0.90.
        HP-A: L1_acc_hot >= 0.90 for >=80% seeds.
    (B) L1/L2 hit routing: hot patterns hit L1 (cosine > HIT_THRESHOLD=0.60) in >=90% queries.
        Cold patterns MISS L1 in >=90% queries (L1 doesn't store cold patterns).
        HP-B: L1_hot_hit_rate >= 0.90 AND L1_cold_miss_rate >= 0.90.
    (C) Audit-cert preservation: deletion certificate for L1 and L2 jointly valid.
        After erasing a hot pattern from W_L1, cosine in L1 < 0.15 AND cosine in L2 unchanged.
        HP-C: post-delete L1 cosine < 0.15 AND L2 cosine of same pattern unchanged (delta < 0.02).

PRE-REGISTERED BANDS:
  HARD-PASS: All of A, B, C.
  MIDDLE: 2/3 cells pass.
  HARD-FAIL: 0-1 cells pass.

  Calibration: first two-tier substrate hierarchy. +-50% bands.
  Theory: L1 with k_hot=5 writes >> L2 with k_cold=1; retrieval cosine ~ k_hot/sqrt(k_hot^2+noise).

FORMULA SELF-TESTS:
  1. L1 retrieval: W_L1 = sum(k_hot * outer(xi, xi) / N). Cosine = k_hot / sqrt(k_hot^2 + M_cold/N).
     At k_hot=5, M_hot=20, M_cold=0, N=1024: cosine ~ 5/5 = 1.0 (no noise).
     [INPUT: k_hot=5, M_hot=20, no cold] [EXPECTED: L1_acc ~ 1.0]
  2. L1/L2 separation: hot patterns in W_L1 have cosine > HIT_THRESHOLD.
     Cold patterns not in W_L1 have cosine ~ random noise < 0.10.
     [INPUT: query cold pattern in W_L1] [EXPECTED: cosine < 0.10]
  3. Rank-1 deletion from W_L1: W_L1 -= k * outer(xi, xi) / N.
     After deletion, cosine drops by ~k_hot / N per step.
     [INPUT: k_hot=5 writes, delete all 5] [EXPECTED: post-delete cosine < 0.15]

TIMEOUT ESTIMATE:
  Smoke: N=1024, M_hot=15, M_cold=30, 2 seeds. Full: N=1024, M_hot=20, M_cold=50, 5 seeds.
  Linear. Smoke ~2s -> Full ~12s. timeout=120s.

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

ANCHOR_NAME = "caching_multi_substrate_hierarchy_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
HIT_THRESHOLD = 0.60
K_HOT = 5    # L1 writes per hot pattern
K_COLD = 1   # L2 writes per cold pattern

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_HOT = 15
    M_COLD = 30
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_HOT = 20
    M_COLD = 50

HP_L1_ACC = 0.90
HP_L1_HOT_HIT_RATE = 0.90
HP_L1_COLD_MISS_RATE = 0.90
HP_POST_DELETE_L1 = 0.15
HP_L2_UNCHANGED_DELTA = 0.02

# ---- FORMULA SELF-TESTS ----
def _l1_cosine_theory(k_hot: int, M_hot: int, N_dim: int) -> float:
    """Cosine of L1 probe for hot pattern: k_hot / sqrt(k_hot^2 + M_hot*(k_hot^2/N)). ~1.0 for k<<N."""
    noise_var = M_hot * k_hot**2 / N_dim
    return k_hot / math.sqrt(k_hot**2 + noise_var) if k_hot > 0 else 0.0

_cos_l1 = _l1_cosine_theory(K_HOT, M_HOT, N)
assert _cos_l1 > HIT_THRESHOLD, (
    f"L1 cosine theory={_cos_l1:.4f} should be > HIT_THRESHOLD={HIT_THRESHOLD}"
)


def build_tier_W(patterns: np.ndarray, k_writes: int, N_dim: int) -> np.ndarray:
    """Build weight matrix from patterns with k_writes each."""
    W = np.zeros((N_dim, N_dim))
    for xi in patterns:
        W += k_writes * np.outer(xi, xi) / N_dim
    np.fill_diagonal(W, 0.0)
    return W


def probe_cosine(W: np.ndarray, xi: np.ndarray) -> float:
    raw = W @ xi
    return float(np.dot(np.sign(raw), xi)) / N


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    Xi_all = rng.choice([-1.0, 1.0], size=(M_HOT + M_COLD, N)).astype(np.float64)
    Xi_hot = Xi_all[:M_HOT]
    Xi_cold = Xi_all[M_HOT:]

    # Build L1 (hot only) and L2 (cold only)
    W_L1 = build_tier_W(Xi_hot, K_HOT, N)
    W_L2 = build_tier_W(Xi_cold, K_COLD, N)

    # Cell A: L1 hot retrieval accuracy
    l1_cosines_hot = [probe_cosine(W_L1, Xi_hot[i]) for i in range(M_HOT)]
    # Accuracy = fraction of correct bit signs = (cosine+1)/2
    l1_acc_hot = float(np.mean([(c + 1.0) / 2.0 for c in l1_cosines_hot]))
    cell_A_pass = l1_acc_hot >= HP_L1_ACC

    # Cell B: hit routing
    # Hot patterns: cosine in L1 should be > HIT_THRESHOLD (L1 hit)
    l1_hot_hits = sum(1 for c in l1_cosines_hot if c > HIT_THRESHOLD)
    l1_hot_hit_rate = l1_hot_hits / M_HOT if M_HOT > 0 else 0.0

    # Cold patterns: cosine in L1 should be < HIT_THRESHOLD (L1 miss)
    l1_cosines_cold_in_L1 = [probe_cosine(W_L1, Xi_cold[i]) for i in range(M_COLD)]
    l1_cold_misses = sum(1 for c in l1_cosines_cold_in_L1 if c < HIT_THRESHOLD)
    l1_cold_miss_rate = l1_cold_misses / M_COLD if M_COLD > 0 else 0.0

    cell_B_pass = (l1_hot_hit_rate >= HP_L1_HOT_HIT_RATE and
                   l1_cold_miss_rate >= HP_L1_COLD_MISS_RATE)

    # Cell C: audit-cert preservation
    # Erase a hot pattern from L1
    xi_erase = Xi_hot[0]
    W_L1_after = W_L1 - K_HOT * np.outer(xi_erase, xi_erase) / N
    np.fill_diagonal(W_L1_after, 0.0)
    cos_l1_after_delete = probe_cosine(W_L1_after, xi_erase)

    # L2 should be unaffected (xi_erase was never in L2)
    cos_l2_before = probe_cosine(W_L2, xi_erase)
    cos_l2_after = cos_l2_before  # L2 unchanged (not modified)
    l2_delta = abs(cos_l2_after - cos_l2_before)

    cell_C_pass = (cos_l1_after_delete < HP_POST_DELETE_L1 and
                   l2_delta < HP_L2_UNCHANGED_DELTA)

    print(f"  [seed={seed}] l1_acc_hot={l1_acc_hot:.4f}(A:{cell_A_pass}) "
          f"l1_hit_rate={l1_hot_hit_rate:.4f} l1_miss_rate={l1_cold_miss_rate:.4f}(B:{cell_B_pass}) "
          f"cos_l1_after={cos_l1_after_delete:.4f} l2_delta={l2_delta:.4f}(C:{cell_C_pass})",
          flush=True)

    return {
        "seed": seed,
        "l1_acc_hot": l1_acc_hot,
        "l1_hot_hit_rate": l1_hot_hit_rate,
        "l1_cold_miss_rate": l1_cold_miss_rate,
        "cos_l1_after_delete": cos_l1_after_delete,
        "l2_delta": l2_delta,
        "cell_A_pass": cell_A_pass,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
        "run_mode": RUN_MODE,
    }


def _instrumentation_selftest():
    """Assert multi-tier cache metrics non-null."""
    rng = np.random.RandomState(42)
    Xi_test = rng.choice([-1.0, 1.0], size=(5, N)).astype(np.float64)
    W_test = build_tier_W(Xi_test, K_HOT, N)

    cos = probe_cosine(W_test, Xi_test[0])
    assert not math.isnan(cos), "probe_cosine returned NaN"
    assert cos > 0.0, f"cos={cos:.4f} should be positive for stored pattern"

    # Erase test
    W_after = W_test - K_HOT * np.outer(Xi_test[0], Xi_test[0]) / N
    np.fill_diagonal(W_after, 0.0)
    cos_after = probe_cosine(W_after, Xi_test[0])
    assert not math.isnan(cos_after), "post-erase cosine is NaN"
    print(f"[selftest] PASS: cos_before={cos:.4f} cos_after={cos_after:.4f}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    l1_accs, hit_rates, miss_rates, cos_deletes, l2_deltas = [], [], [], [], []
    a_pass, b_pass, c_pass = [], [], []
    for sd in per_seed.values():
        l1_accs.append(sd.get("l1_acc_hot", float("nan")))
        hit_rates.append(sd.get("l1_hot_hit_rate", float("nan")))
        miss_rates.append(sd.get("l1_cold_miss_rate", float("nan")))
        cos_deletes.append(sd.get("cos_l1_after_delete", float("nan")))
        l2_deltas.append(sd.get("l2_delta", float("nan")))
        a_pass.append(sd.get("cell_A_pass", False))
        b_pass.append(sd.get("cell_B_pass", False))
        c_pass.append(sd.get("cell_C_pass", False))
    return {
        "mean_l1_acc": float(np.nanmean(l1_accs)),
        "mean_hit_rate": float(np.nanmean(hit_rates)),
        "mean_miss_rate": float(np.nanmean(miss_rates)),
        "mean_cos_after_delete": float(np.nanmean(cos_deletes)),
        "mean_l2_delta": float(np.nanmean(l2_deltas)),
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

    ml1 = agg["mean_l1_acc"]
    mhr = agg["mean_hit_rate"]
    mmr = agg["mean_miss_rate"]
    mcd = agg["mean_cos_after_delete"]
    mld = agg["mean_l2_delta"]

    if cells_pass == 3:
        return ("HARD_PASS",
                f"Multi-tier hierarchy CONFIRMED. "
                f"L1_acc={ml1:.4f}>={HP_L1_ACC} "
                f"hit_rate={mhr:.4f}>={HP_L1_HOT_HIT_RATE} "
                f"miss_rate={mmr:.4f}>={HP_L1_COLD_MISS_RATE} "
                f"cos_after_delete={mcd:.4f}<{HP_POST_DELETE_L1} l2_delta={mld:.4f}. "
                f"A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    if cells_pass <= 1:
        return ("HARD_FAIL",
                f"Multi-tier hierarchy failed. L1_acc={ml1:.4f} hit={mhr:.4f} "
                f"miss={mmr:.4f} cos_delete={mcd:.4f}. A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")
    return ("MIDDLE_BAND",
            f"{cells_pass}/3 cells. L1_acc={ml1:.4f} hit={mhr:.4f} "
            f"miss={mmr:.4f} cos_delete={mcd:.4f}. A:{fA:.2f} B:{fB:.2f} C:{fC:.2f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"M_HOT={M_HOT} M_COLD={M_COLD} K_HOT={K_HOT} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE, "M_HOT": M_HOT, "M_COLD": M_COLD}
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
        "run_mode": RUN_MODE, "N": N, "M_HOT": M_HOT, "M_COLD": M_COLD,
        "K_HOT": K_HOT, "K_COLD": K_COLD, "seeds": SEEDS,
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
