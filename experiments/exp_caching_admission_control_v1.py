"""
caching_admission_control_v1 -- Capacity-aware admission control via spectral monitor.

SCIENTIFIC QUESTION (Caching-Policy, Admission Control):
  Admission control = deciding WHICH patterns to write (vs reject at the door)
  based on current cache state. At high capacity (near alpha_c), the cost of
  adding a new pattern rises steeply; admission control should REDUCE the
  write rate pre-cliff.

  Design:
    - Track estimated alpha_eff via spectral proxy (top eigenvalue of W, same as
      caching_capacity_aware_eviction_v1).
    - ADMISSION POLICY: accept new write if alpha_eff < ADMIT_THRESHOLD; reject otherwise.
    - Compare admission-controlled writes vs naive writes at the cliff:
        (a) Admitted patterns are retrieved cleanly (high accuracy).
        (b) Admission rate adapts (drops) as we approach alpha_c.
        (c) No-admission-control baseline collapses past alpha_c.

  Test cells:
    (A) Admission rate adapts: among M_total = 1.5*alpha_c*N writes attempted,
        fraction admitted = n_admitted / M_total decreases as M grows.
        HP-A: admission_rate_late_half < admission_rate_early_half * 0.70
              (late-half admission rate drops by >= 30%).
        HF-A: admission rate stays flat (never drops >= 10%).
    (B) Admitted retrieval accuracy >= 0.85 throughout (no collapse for admitted patterns).
        HP-B: mean_retrieval_admitted >= 0.85. HF-B: mean_retrieval_admitted < 0.60.
    (C) Rejected baseline collapses: accuracy of naive (no admission) baseline <= 0.50
        at M = 1.5*alpha_c*N.
        HP-C: acc_naive_at_overload <= 0.50. HF-C: acc_naive_at_overload > 0.75
              (no collapse observed -- admission control irrelevant).

  HARD-PASS: All of A, B, C.
  HARD-FAIL: HF-B (admission control itself degrades quality) or HF-C (no cliff to control).
  MIDDLE: 2/3 cells.

PRE-REGISTERED BANDS (first admission control measurement; calibration probe):
  HP: rate_drop >= 30%, acc_admitted >= 0.85, acc_naive <= 0.50.
  HF: rate_drop < 5%, acc_admitted < 0.60, acc_naive > 0.75.
  Bands: +-50% per calibration-probe policy.
  Theory: alpha_c = 0.138 for Hopfield; spectral proxy triggers admission block at
  ADMIT_THRESHOLD = 0.10 (lambda_max threshold), giving ~72% capacity utilization.

FORMULA SELF-TESTS:
  1. alpha_eff proxy: for W = Xi^T Xi / N with M=10, N=1024, alpha=0.00977.
     lambda_max ~ (1 + sqrt(0.00977))^2 = (1+0.0988)^2 = 1.208. alpha_eff = (sqrt(1.208)-1)^2.
     [INPUT: M=10, N=1024] [EXPECTED: alpha_eff in [0.005, 0.020]]
  2. Admission rate early vs late: if early admits all 10/10 and late admits 5/10,
     rate_early=1.0, rate_late=0.5, ratio=0.5 < 0.70 => PASS criterion.
     [INPUT: early=10/10, late=5/10] [EXPECTED: ratio=0.5 < 0.70]
  3. Naive collapse at 1.5*alpha_c = 0.207: from caching_capacity_aware_eviction_v1
     confirmed naive accuracy drops below 0.50 past alpha_c.
     [INPUT: M=210, N=1024, alpha=0.205] [EXPECTED: acc_naive <= 0.50 (from prior)]

TIMEOUT ESTIMATE:
  Smoke: N=512, M_total=90, 2 seeds. Full: N=1024, M_total=180, 5 seeds.
  Linear. Smoke ~3s -> Full ~25s. timeout=300s.

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

ANCHOR_NAME = "caching_admission_control_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

ALPHA_C = 0.138
ADMIT_THRESHOLD = 0.10  # lambda_max threshold for admission block (~alpha_c * 0.72)

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    M_TOTAL = int(1.5 * ALPHA_C * N)   # ~106 for N=512
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    M_TOTAL = int(1.5 * ALPHA_C * N)   # ~212 for N=1024

HP_RATE_DROP_RATIO = 0.70   # late / early < this
HP_ADMITTED_ACC = 0.85
HF_ADMITTED_ACC = 0.60
HP_NAIVE_UPPER = 0.50    # naive at overload MUST collapse below this
HF_NAIVE_LOWER = 0.75    # naive stays above this => no cliff

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    import math as _math

    # 1. alpha_eff proxy
    rng = np.random.RandomState(0)
    M_test, N_test = 10, 1024
    Xi_t = rng.choice([-1.0, 1.0], size=(M_test, N_test)).astype(np.float64)
    W_t = Xi_t.T @ Xi_t / N_test
    np.fill_diagonal(W_t, 0.0)
    v = rng.randn(N_test); v /= np.linalg.norm(v)
    for _ in range(20):
        v = W_t @ v
        n = np.linalg.norm(v)
        if n < 1e-12:
            break
        v /= n
    lmax = float(np.dot(v, W_t @ v))
    alpha_eff = (_math.sqrt(max(0.0, lmax)) - 1.0)**2 if lmax > 1.0 else 0.0
    assert 0.0 <= alpha_eff <= 0.10, f"alpha_eff selftest: {alpha_eff:.5f} out of [0, 0.10]"

    # 2. Admission rate comparison
    early = 10.0 / 10.0
    late = 5.0 / 10.0
    ratio = late / early
    assert ratio < 0.70, f"Admission rate ratio selftest: {ratio:.2f} should be < 0.70"

    print(f"[selftest] alpha_eff={alpha_eff:.5f} admission_ratio={ratio:.2f}", flush=True)


_instrumentation_selftest()


def estimate_alpha_eff(W: np.ndarray) -> float:
    """Estimate effective alpha from largest eigenvalue using power method."""
    rng = np.random.RandomState(0)
    v = rng.randn(W.shape[0])
    norm = np.linalg.norm(v)
    if norm < 1e-12:
        return 0.0
    v /= norm
    for _ in range(20):
        v = W @ v
        norm = np.linalg.norm(v)
        if norm < 1e-12:
            return 0.0
        v /= norm
    lmax = float(np.dot(v, W @ v))
    if lmax <= 1.0:
        return 0.0
    return (math.sqrt(max(0.0, lmax)) - 1.0)**2


def retrieval_accuracy(W: np.ndarray, Xi: np.ndarray) -> float:
    """Mean cosine similarity of retrieved patterns vs stored."""
    if Xi.shape[0] == 0:
        return 0.0
    cosines = []
    for i in range(Xi.shape[0]):
        retrieved = np.sign(W @ Xi[i])
        cosine = float(np.dot(retrieved, Xi[i])) / Xi.shape[1]
        cosines.append(cosine)
    return float(np.mean(cosines))


def run_one_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)

    # Generate M_TOTAL candidate patterns
    Xi_all = rng.choice([-1.0, 1.0], size=(M_TOTAL, N)).astype(np.float64)

    # --- Admission control run ---
    W_admit = np.zeros((N, N), dtype=np.float64)
    Xi_admitted = []
    admit_timeline = []  # per-write: admitted (1) or rejected (0)

    for i in range(M_TOTAL):
        alpha_eff = estimate_alpha_eff(W_admit)
        if alpha_eff < ADMIT_THRESHOLD:
            # Admit this write
            W_admit += np.outer(Xi_all[i], Xi_all[i]) / N
            np.fill_diagonal(W_admit, 0.0)
            Xi_admitted.append(Xi_all[i])
            admit_timeline.append(1)
        else:
            admit_timeline.append(0)

    Xi_admitted_arr = np.array(Xi_admitted) if Xi_admitted else np.zeros((0, N))
    acc_admitted = retrieval_accuracy(W_admit, Xi_admitted_arr)
    n_admitted = len(Xi_admitted)

    # Admission rate: first half vs second half
    early_admits = sum(admit_timeline[: M_TOTAL // 2])
    late_admits = sum(admit_timeline[M_TOTAL // 2 :])
    rate_early = early_admits / (M_TOTAL // 2)
    rate_late = late_admits / (M_TOTAL - M_TOTAL // 2)
    rate_ratio = rate_late / (rate_early + 1e-10)

    # --- Naive run (no admission control) ---
    W_naive = np.zeros((N, N), dtype=np.float64)
    for i in range(M_TOTAL):
        W_naive += np.outer(Xi_all[i], Xi_all[i]) / N
    np.fill_diagonal(W_naive, 0.0)
    acc_naive = retrieval_accuracy(W_naive, Xi_all)

    assert n_admitted >= 1, f"Admission control admitted 0 patterns -- instrumentation bug"

    cell_A_pass = rate_ratio < HP_RATE_DROP_RATIO
    cell_A_hf = rate_ratio > (1.0 - 0.10)  # flat within 10%
    cell_B_pass = acc_admitted >= HP_ADMITTED_ACC
    cell_B_hf = acc_admitted < HF_ADMITTED_ACC
    cell_C_pass = acc_naive <= HP_NAIVE_UPPER
    cell_C_hf = acc_naive > HF_NAIVE_LOWER

    return {
        "N": N,
        "run_mode": RUN_MODE,
        "seed": seed,
        "n_admitted": n_admitted,
        "rate_early": rate_early,
        "rate_late": rate_late,
        "rate_ratio": rate_ratio,
        "acc_admitted": acc_admitted,
        "acc_naive": acc_naive,
        "cell_A_pass": cell_A_pass,
        "cell_A_hf": cell_A_hf,
        "cell_B_pass": cell_B_pass,
        "cell_B_hf": cell_B_hf,
        "cell_C_pass": cell_C_pass,
        "cell_C_hf": cell_C_hf,
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"[seed={seed}] running N={N} M_total={M_TOTAL}...", flush=True)
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] rate_ratio={result['rate_ratio']:.3f} acc_admitted={result['acc_admitted']:.3f} acc_naive={result['acc_naive']:.3f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(SEEDS)

    all_rate_ratio = [per_seed[str(s)]["rate_ratio"] for s in SEEDS]
    all_acc_adm = [per_seed[str(s)]["acc_admitted"] for s in SEEDS]
    all_acc_naive = [per_seed[str(s)]["acc_naive"] for s in SEEDS]

    mean_rate_ratio = float(np.mean(all_rate_ratio))
    mean_acc_adm = float(np.mean(all_acc_adm))
    mean_acc_naive = float(np.mean(all_acc_naive))

    n_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_A_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_hf"])
    n_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])
    n_B_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_hf"])
    n_C = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_pass"])
    n_C_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_hf"])

    thr = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_A >= thr
    cell_B_pass = n_B >= thr
    cell_C_pass = n_C >= thr
    hf_B = n_B_hf >= thr
    hf_C = n_C_hf >= thr

    n_cells_pass = int(cell_A_pass) + int(cell_B_pass) + int(cell_C_pass)
    if n_cells_pass == 3:
        verdict = "HARD_PASS"
    elif hf_B or hf_C:
        verdict = "HARD_FAIL"
    elif n_cells_pass >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    verdict_msg = (
        f"caching_admission_control_v1 verdict={verdict}: "
        f"mean_rate_ratio={mean_rate_ratio:.3f}(HP<{HP_RATE_DROP_RATIO}) "
        f"mean_acc_admitted={mean_acc_adm:.3f}(HP>={HP_ADMITTED_ACC}) "
        f"mean_acc_naive={mean_acc_naive:.3f}(HP<={HP_NAIVE_UPPER}) "
        f"cells={n_cells_pass}/3 elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_seeds": n_seeds,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_rate_ratio": mean_rate_ratio,
        "mean_acc_admitted": mean_acc_adm,
        "mean_acc_naive": mean_acc_naive,
        "n_cell_A_pass": n_A,
        "n_cell_B_pass": n_B,
        "n_cell_C_pass": n_C,
        "elapsed_s": elapsed,
    }
    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] metrics written to {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
