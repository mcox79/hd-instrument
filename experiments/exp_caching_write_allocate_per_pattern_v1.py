"""
caching_write_allocate_per_pattern_v1 -- Write-allocate cost per pattern.

SCIENTIFIC QUESTION (Caching-Policy Expressibility, Tier 1):
  Caching semantic: write-allocate = on a write request for a MISS, bring the
  pattern into the substrate (W) and mark it as allocated.
  Key product question: what is the overhead of ONE write-allocate cycle?

  In substrate terms:
    - Write-allocate for pattern xi: W += outer(xi, xi) / N (one rank-1 update).
    - The overhead is the time and SNR cost of this rank-1 update.
    - THEORY: rank-1 update is O(N) if only W*xi used; O(N^2) if W stored densely.
    - But: the SUBSTRATE OVERHEAD (cost to existing patterns' retrieval) should
      be measured, not just the write latency.

  Empirical test:
    (A) Zero-overhead confirmation: after write-allocating a NEW pattern, retrieval
        accuracy of EXISTING patterns does not decrease > epsilon.
        HP-A: delta_acc <= 0.02 (per-pattern write-allocate is essentially free).
    (B) Idempotency: write-allocating the SAME pattern twice gives same W as once
        (modulo scaling), so retrieval accuracy is identical.
        HP-B: |acc_after_1x - acc_after_2x| <= 0.01 (idempotent up to scale).
    (C) Write-allocate does not degrade NEWLY-written pattern retrieval:
        acc_new >= 0.80 immediately after write-allocate.
        HP-C: new pattern cosine >= 0.80.

PRE-REGISTERED BANDS:
  HARD-PASS: ALL of A, B, C.
  MIDDLE: 2/3 cells pass.
  HARD-FAIL: 0-1 cells pass.

  Calibration: first direct write-allocate cost measurement. +-50% bands.

FORMULA SELF-TESTS:
  1. delta_acc = acc(W) - acc(W + outer(xi_new, xi_new)/N).
     At M << M_max, delta_acc ~ 1/N per new write (small). At N=1024, delta ~ 0.001.
     [INPUT: N=1024, M=50 existing, 1 new write] [EXPECTED: delta_acc < 0.02]
  2. Idempotency: W_1x = W + outer(xi, xi)/N. W_2x = W + 2*outer(xi,xi)/N.
     acc(W_2x) on EXISTING patterns should be near acc(W_1x) (extra xi-reinforcement
     doesn't meaningfully affect other patterns).
     [INPUT: 2x vs 1x write of same pattern] [EXPECTED: |delta| < 0.01]
  3. New pattern acc: sign(W_new @ xi) . xi / N ~ (1 + M/N * noise).
     At M=50, N=1024: SNR ~ 1/(50/1024)^0.5 ~ 4.5. Cosine >= 0.80.

TIMEOUT ESTIMATE:
  Smoke: N=1024, M=30, 2 seeds. Full: N=1024, M=[20,40,60,80], 5 seeds.
  Linear. Smoke ~1s -> Full ~15s. timeout=120s.

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

ANCHOR_NAME = "caching_write_allocate_per_pattern_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
ALPHA_C = 0.138
M_MAX = int(ALPHA_C * N)  # ~141

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [30, 60]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [20, 40, 60, 80]

HP_DELTA_ACC = 0.02       # A: write-allocate overhead per pattern
HP_IDEMPOTENT = 0.01      # B: idempotency tolerance
HP_NEW_COSINE = 0.80      # C: new pattern retrieval

# ---- FORMULA SELF-TESTS ----
# Test: at N=1024, M=50, one rank-1 write should change retrieval by ~1/(N-M) ~ 0.001
# Just verify the formula order of magnitude
_expected_delta_approx = 1.0 / (N - 50)
assert _expected_delta_approx < HP_DELTA_ACC, (
    f"Expected delta {_expected_delta_approx:.5f} should be < HP {HP_DELTA_ACC}"
)


def build_w_from_patterns(Xi: np.ndarray) -> np.ndarray:
    """Build Hopfield W from pattern matrix Xi (M x N)."""
    M, N_dim = Xi.shape
    W = Xi.T @ Xi / N_dim
    np.fill_diagonal(W, 0.0)
    return W


def retrieval_cosine(W: np.ndarray, Xi: np.ndarray) -> List[float]:
    """Cosine similarity of sign(W @ xi) with xi for each pattern."""
    cosines = []
    for i in range(Xi.shape[0]):
        xi = Xi[i]
        raw = W @ xi
        retrieved = np.sign(raw)
        cos = float(np.dot(retrieved, xi)) / N
        cosines.append(cos)
    return cosines


def run_one_cell(M: int, seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    Xi_existing = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    xi_new = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)

    # W before write-allocate
    W_before = build_w_from_patterns(Xi_existing)
    acc_before = np.mean(retrieval_cosine(W_before, Xi_existing))

    # Write-allocate: single rank-1 update
    W_1x = W_before + np.outer(xi_new, xi_new) / N
    np.fill_diagonal(W_1x, 0.0)
    acc_after_1x = np.mean(retrieval_cosine(W_1x, Xi_existing))

    # Cell A: delta_acc for existing patterns
    delta_acc = float(acc_before - acc_after_1x)

    # Cell B: idempotency (2x write vs 1x write)
    W_2x = W_before + 2.0 * np.outer(xi_new, xi_new) / N
    np.fill_diagonal(W_2x, 0.0)
    acc_after_2x = np.mean(retrieval_cosine(W_2x, Xi_existing))
    idempotent_delta = float(abs(acc_after_1x - acc_after_2x))

    # Cell C: new pattern retrieval immediately after write-allocate
    raw_new = W_1x @ xi_new
    retrieved_new = np.sign(raw_new)
    new_cosine = float(np.dot(retrieved_new, xi_new)) / N

    cell_A_pass = delta_acc <= HP_DELTA_ACC
    cell_B_pass = idempotent_delta <= HP_IDEMPOTENT
    cell_C_pass = new_cosine >= HP_NEW_COSINE

    print(f"  [M={M} seed={seed}] delta_acc={delta_acc:.4f}(A:{cell_A_pass}) "
          f"idempotent_delta={idempotent_delta:.4f}(B:{cell_B_pass}) "
          f"new_cosine={new_cosine:.4f}(C:{cell_C_pass})", flush=True)

    return {
        "M": M, "seed": seed, "N": N,
        "acc_before": float(acc_before),
        "acc_after_1x": float(acc_after_1x),
        "delta_acc": delta_acc,
        "idempotent_delta": idempotent_delta,
        "new_cosine": new_cosine,
        "cell_A_pass": cell_A_pass,
        "cell_B_pass": cell_B_pass,
        "cell_C_pass": cell_C_pass,
        "run_mode": RUN_MODE,
    }


def run_seed(seed: int) -> Dict:
    results = {}
    for M in M_LIST:
        results[str(M)] = run_one_cell(M, seed)
    return {"by_M": results, "seed": seed}


def _instrumentation_selftest():
    """Assert write-allocate metrics non-null at small scale."""
    N_test = 256
    Xi_test = np.random.RandomState(42).choice([-1.0, 1.0], size=(10, N_test)).astype(np.float64)
    xi_new = np.random.RandomState(99).choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)

    W_before = build_w_from_patterns(Xi_test)
    acc_before = float(np.mean(retrieval_cosine(W_before, Xi_test)))
    assert not math.isnan(acc_before), "acc_before is NaN"
    assert acc_before > 0.0, f"acc_before={acc_before} not positive"

    W_after = W_before + np.outer(xi_new, xi_new) / N_test
    np.fill_diagonal(W_after, 0.0)
    new_cosine = float(np.dot(np.sign(W_after @ xi_new), xi_new)) / N_test
    assert not math.isnan(new_cosine), "new_cosine is NaN"
    assert -1.0 <= new_cosine <= 1.0, f"new_cosine={new_cosine} out of range"

    print(f"[selftest] PASS: acc_before={acc_before:.4f} new_cosine={new_cosine:.4f} "
          f"at N={N_test}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for M in M_LIST:
        deltas, idems, cosines = [], [], []
        a_pass, b_pass, c_pass = [], [], []
        for sd in per_seed.values():
            row = sd["by_M"].get(str(M))
            if row is None:
                continue
            deltas.append(row["delta_acc"])
            idems.append(row["idempotent_delta"])
            cosines.append(row["new_cosine"])
            a_pass.append(row["cell_A_pass"])
            b_pass.append(row["cell_B_pass"])
            c_pass.append(row["cell_C_pass"])
        agg[M] = {
            "mean_delta_acc": float(np.mean(deltas)) if deltas else float("nan"),
            "mean_idempotent": float(np.mean(idems)) if idems else float("nan"),
            "mean_new_cosine": float(np.mean(cosines)) if cosines else float("nan"),
            "frac_A_pass": float(np.mean(a_pass)) if a_pass else float("nan"),
            "frac_B_pass": float(np.mean(b_pass)) if b_pass else float("nan"),
            "frac_C_pass": float(np.mean(c_pass)) if c_pass else float("nan"),
            "n_seeds": len(deltas),
        }
    return {"by_M": agg}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_M = agg["by_M"]
    if not by_M:
        return ("HARD_FAIL", "No cells computed.")

    all_A = [v["frac_A_pass"] for v in by_M.values() if not math.isnan(v.get("frac_A_pass", float("nan")))]
    all_B = [v["frac_B_pass"] for v in by_M.values() if not math.isnan(v.get("frac_B_pass", float("nan")))]
    all_C = [v["frac_C_pass"] for v in by_M.values() if not math.isnan(v.get("frac_C_pass", float("nan")))]

    mean_A = float(np.mean(all_A)) if all_A else float("nan")
    mean_B = float(np.mean(all_B)) if all_B else float("nan")
    mean_C = float(np.mean(all_C)) if all_C else float("nan")

    mean_delta = float(np.nanmean([v["mean_delta_acc"] for v in by_M.values()]))
    mean_idem = float(np.nanmean([v["mean_idempotent"] for v in by_M.values()]))
    mean_cos = float(np.nanmean([v["mean_new_cosine"] for v in by_M.values()]))

    hp_A = mean_A >= 0.80
    hp_B = mean_B >= 0.80
    hp_C = mean_C >= 0.80

    if hp_A and hp_B and hp_C:
        return ("HARD_PASS",
                f"Write-allocate cost NEAR-ZERO confirmed. "
                f"delta_acc={mean_delta:.4f}(A:{mean_A:.2f}) "
                f"idempotent_delta={mean_idem:.4f}(B:{mean_B:.2f}) "
                f"new_cosine={mean_cos:.4f}(C:{mean_C:.2f}). "
                f"Rank-1 write-allocate is O(1) overhead per existing pattern.")
    cells_pass = sum([hp_A, hp_B, hp_C])
    if cells_pass == 0:
        return ("HARD_FAIL",
                f"Write-allocate has significant cost. "
                f"delta_acc={mean_delta:.4f} idempotent={mean_idem:.4f} "
                f"new_cosine={mean_cos:.4f}. A:{mean_A:.2f} B:{mean_B:.2f} C:{mean_C:.2f}.")
    return ("MIDDLE_BAND",
            f"{cells_pass}/3 cells pass. "
            f"A={mean_A:.2f} B={mean_B:.2f} C={mean_C:.2f}. "
            f"delta_acc={mean_delta:.4f} idem={mean_idem:.4f} new_cos={mean_cos:.4f}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_LIST={M_LIST} seeds={SEEDS}",
          flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE, "M_LIST": M_LIST}
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
        "run_mode": RUN_MODE, "N": N, "M_LIST": M_LIST, "seeds": SEEDS,
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
