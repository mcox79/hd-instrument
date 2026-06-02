"""
write_around_routing_v1 -- Write-around routing uses same probe primitive as refusal-cert.

SCIENTIFIC QUESTION (Caching-Policy Expressibility, Tier 1 extension):
  Write-around routing: on a write request, decide whether to put new data in the
  cache (write-allocate) or bypass the cache entirely (write-around / bypass).
  The key insight: the same cosine-probe primitive used for refusal certificates
  (PP-31a) can identify whether a new pattern is already in the substrate
  (cache hit = write-allocate OK) vs not present (write-around candidate).

  Cross-primitive composition test:
    - Probe W with candidate pattern to get cosine similarity.
    - If sim > THRESHOLD_HIGH: pattern already in cache (write-allocate; redundant write).
    - If sim < THRESHOLD_LOW: pattern NOT in cache; use write-around to bypass.
    - Decision accuracy = how reliably does probe distinguish in-cache vs new patterns?

  PREDICTION: cross-primitive composition works.
  Probe primitive identifies in-substrate hits vs bypass routes with accuracy >= 0.90.

PRE-REGISTERED BANDS:
  HARD-PASS: routing accuracy >= 0.90 (correct hit/miss classification)
             AND false-positive rate (bypass when should cache) < 0.10.
  MIDDLE: accuracy 0.75-0.90 OR FPR 0.10-0.20.
  HARD-FAIL: accuracy < 0.75 OR FPR > 0.20.

FORMULA SELF-TESTS:
  1. Pattern stored in W: sim(W @ xi, xi) / ||W @ xi|| near 1.0 at M < M_max/2.
  2. Random unseen pattern: sim(W @ xi_new, xi_new) ~ 0 at M < M_max/3.
  3. Routing threshold THRESHOLD_HIGH = 0.7, THRESHOLD_LOW = 0.3.

TIMEOUT ESTIMATE:
  Smoke: N=1024, M=30, 2 seeds. Full: N=1024, M=50, 5 seeds.
  Linear. Smoke wall ~2s -> Full ~8s. timeout=60s.

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
from typing import Dict, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "write_around_routing_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 1024
ALPHA_C = 0.138
M_MAX = int(ALPHA_C * N)  # ~141

THRESHOLD_HIGH = 0.7   # above = in-cache (write-allocate)
THRESHOLD_LOW = 0.3    # below = not in cache (write-around)

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [20, 30]
    N_PROBES = 20  # number of probe patterns to classify per run
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [20, 40, 60]
    N_PROBES = 50

HP_ACC = 0.90
HF_ACC = 0.75
HP_FPR = 0.10
HF_FPR = 0.20


def hopfield_store(patterns: np.ndarray, N: int) -> np.ndarray:
    W = np.zeros((N, N), dtype=np.float64)
    for xi in patterns:
        W += np.outer(xi, xi) / N
    return W


def probe_similarity(W: np.ndarray, xi: np.ndarray) -> float:
    """Single-step probe: cosine sim of sign(W @ xi) with xi."""
    raw = W @ xi
    retrieved = np.sign(raw + 1e-12)
    nr = np.linalg.norm(retrieved)
    nx = np.linalg.norm(xi)
    if nr < 1e-12 or nx < 1e-12:
        return 0.0
    return float(np.dot(retrieved, xi) / (nr * nx))


def route_decision(sim: float) -> str:
    """Classify: in-cache / ambiguous / write-around based on sim."""
    if sim >= THRESHOLD_HIGH:
        return "in_cache"
    if sim <= THRESHOLD_LOW:
        return "write_around"
    return "ambiguous"


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results_by_M = {}

    for M in M_LIST:
        # Stored patterns
        stored = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        W = hopfield_store(stored, N)

        # Probe N_PROBES IN-cache patterns (should be classified as in_cache)
        in_cache_sims = []
        for i in range(min(N_PROBES, M)):
            xi = stored[i % M]
            sim = probe_similarity(W, xi)
            in_cache_sims.append(sim)

        # Probe N_PROBES OUT-of-cache patterns (should be write-around)
        out_sims = []
        for _ in range(N_PROBES):
            xi_new = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
            sim = probe_similarity(W, xi_new)
            out_sims.append(sim)

        # Routing accuracy: in_cache patterns above THRESHOLD_HIGH
        # write-around patterns below THRESHOLD_LOW
        in_cache_correct = sum(1 for s in in_cache_sims if s >= THRESHOLD_HIGH)
        write_around_correct = sum(1 for s in out_sims if s <= THRESHOLD_LOW)
        total = len(in_cache_sims) + len(out_sims)

        if total > 0:
            acc = (in_cache_correct + write_around_correct) / total
        else:
            acc = float("nan")

        # False positive rate: out-of-cache patterns misclassified as in-cache
        n_out = len(out_sims)
        fpr = sum(1 for s in out_sims if s >= THRESHOLD_HIGH) / n_out if n_out > 0 else 0.0

        print(f"  [seed={seed} M={M}] acc={acc:.3f} fpr={fpr:.3f} "
              f"in_cache_correct={in_cache_correct}/{len(in_cache_sims)} "
              f"wa_correct={write_around_correct}/{len(out_sims)}", flush=True)

        results_by_M[M] = {
            "M": M,
            "acc": acc,
            "fpr": fpr,
            "in_cache_correct": in_cache_correct,
            "write_around_correct": write_around_correct,
            "n_in_cache_probes": len(in_cache_sims),
            "n_out_probes": n_out,
        }

    return {"by_M": results_by_M, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert routing metrics non-null at small scale."""
    N_test = 256
    M_test = 20
    rng = np.random.RandomState(42)
    stored = rng.choice([-1.0, 1.0], size=(M_test, N_test)).astype(np.float64)
    W = hopfield_store(stored, N_test)

    # In-cache probe
    xi_in = stored[0]
    sim_in = probe_similarity(W, xi_in)
    assert not math.isnan(sim_in), "in-cache sim is NaN"
    assert sim_in >= 0.0, f"sim_in={sim_in:.3f} < 0"

    # Out-of-cache probe
    xi_out = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    sim_out = probe_similarity(W, xi_out)
    assert not math.isnan(sim_out), "out-of-cache sim is NaN"

    # At low load (M_test << M_max), in-cache sim should exceed out-of-cache
    print(f"[selftest] PASS: in_cache_sim={sim_in:.3f} out_sim={sim_out:.3f} "
          f"at N={N_test} M={M_test}", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify route_decision logic."""
    assert route_decision(0.8) == "in_cache", f"route_decision(0.8) != in_cache"
    assert route_decision(0.2) == "write_around", f"route_decision(0.2) != write_around"
    assert route_decision(0.5) == "ambiguous", f"route_decision(0.5) != ambiguous"
    print("[formula_selftests] PASS: route_decision logic verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    agg_by_M = {}
    for M in M_LIST:
        accs, fprs = [], []
        for sd in per_seed.values():
            row = sd["by_M"].get(M) or sd["by_M"].get(str(M))
            if row is None:
                continue
            accs.append(row["acc"])
            fprs.append(row["fpr"])
        agg_by_M[M] = {
            "mean_acc": float(np.mean(accs)) if accs else float("nan"),
            "mean_fpr": float(np.mean(fprs)) if fprs else float("nan"),
            "n_seeds": len(accs),
        }
    return {"by_M": agg_by_M}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_M = agg["by_M"]
    accs = [v["mean_acc"] for v in by_M.values()
            if not math.isnan(v.get("mean_acc", float("nan")))]
    fprs = [v["mean_fpr"] for v in by_M.values()
            if not math.isnan(v.get("mean_fpr", float("nan")))]

    if not accs:
        return ("HARD_FAIL", "No valid results.")

    min_acc = min(accs)
    max_fpr = max(fprs) if fprs else float("nan")

    if (min_acc >= HP_ACC and
            not math.isnan(max_fpr) and
            max_fpr < HP_FPR):
        return ("HARD_PASS",
                f"Write-around routing via probe confirmed. "
                f"min_acc={min_acc:.3f}>={HP_ACC} max_fpr={max_fpr:.3f}<{HP_FPR}. "
                f"Cross-primitive composition (probe=refusal-cert) works for routing.")
    if min_acc < HF_ACC or (not math.isnan(max_fpr) and max_fpr > HF_FPR):
        return ("HARD_FAIL",
                f"Write-around routing fails. "
                f"min_acc={min_acc:.3f}<HF={HF_ACC} OR max_fpr={max_fpr:.3f}>HF={HF_FPR}.")
    return ("MIDDLE_BAND",
            f"Partial routing accuracy. min_acc={min_acc:.3f}(hp={HP_ACC}) "
            f"max_fpr={max_fpr:.3f}(hp={HP_FPR}).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} M_LIST={M_LIST} "
          f"N_PROBES={N_PROBES} seeds={SEEDS}", flush=True)

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
        "M_LIST": M_LIST, "N_PROBES": N_PROBES,
        "THRESHOLD_HIGH": THRESHOLD_HIGH, "THRESHOLD_LOW": THRESHOLD_LOW,
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
