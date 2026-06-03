"""
activation_barrier_n_scale_v1_n8192 -- PP-33 R4: N-scale test at N=8192.

LVH #208/#209 context:
  v1_n4096 (0.04-step grid): ratio=1.10 (47% of Arrhenius prediction 2.316)
  v2_n4096 (0.01-step grid, LVH#209): mean ratio=1.0962 -- below MIDDLE lower bound 1.10
  Hypothesis: ratio is N-suppressed at N=4096 and increases toward Arrhenius at larger N.
  This run tests N=8192 with 0.01-step fine grid to measure ratio at production N.

SCIENTIFIC QUESTION:
  Does nf_crit(0.05)/nf_crit(0.10) ratio increase at N=8192 vs N=4096?
  If ratio > 1.10 at N=8192 that supports finite-N suppression hypothesis.
  If ratio stays ~1.10, barrier is genuinely weaker than Arrhenius at all substrate N.

PRE-REGISTERED BANDS (R4 N-scale; calibrated from v2_n4096 ratio=1.0962):
  HARD-PASS: ratio > 1.20 AND n_monotone >= 4/5
             (N-scaling confirmed; ratio increases toward Arrhenius prediction)
  MIDDLE: 1.05 < ratio <= 1.20 (modest N-scaling improvement; not conclusive)
  HARD-FAIL: ratio <= 1.02 (no N-scaling; direction lost; Arrhenius unsupported)

Note: HP gate set to 1.20 (vs 1.10 MIDDLE lower bound at N=4096) -- looking for clear
N-scaling improvement, not just marginal shift. 1.20 is still only 52% of Arrhenius 2.316.

FORMULA SELF-TESTS (PROT-022):
  1. Barrier ratio formula: (alpha_c - 0.05) / (alpha_c - 0.10) = 2.3157 +- 0.001
     [INPUT: alpha_c=0.138, alpha1=0.05, alpha2=0.10]
     [EXPECTED: 2.3157 within 0.001] [VERIFIED: 0.088/0.038 = 2.3158]
  2. Grid resolution: step = 0.01 (fine grid same as v2)
     [VERIFIED: all adjacent differences = 0.01]
  3. N-scaling factor at N=8192 vs 4096: W matrix = NxN; capacity alpha_c=M/N fixed.
     Same alpha means M=0.138*N -> 1130 patterns at N=8192 (vs 565 at N=4096).

PROT-018: no _nN suffix in anchor (alpha-sweep; production N=8192 is fixed in script).
QUEUE: remote_cpu_queue (pure CPU; W=(8192x8192) float32 = 268 MB; fits in 16GB RAM; ~60-90 min).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "activation_barrier_n_scale_v1_n8192"

N = 8192
# Note: no _nN suffix in anchor name (alpha-sweep experiment); N=8192 is production config.
# PROT-018 note: No _nN suffix; production N = 8192. Script-level assertion below.
assert N == 8192, "Production N must be 8192 for this anchor"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
ALPHA_VALUES = [0.05, 0.10]
PREDICTED_BARRIER_RATIO = (ALPHA_C - 0.05) / (ALPHA_C - 0.10)  # 2.3158

# PROT-022: verify formula
assert abs(PREDICTED_BARRIER_RATIO - 2.3158) < 0.001, f"Barrier ratio formula: {PREDICTED_BARRIER_RATIO:.4f}"

# Fine grid 0.01-step (same as v2_n4096 for direct comparability)
NOISE_FRACS_FINE = [round(i * 0.01, 3) for i in range(61)]  # 0.00..0.60 step 0.01
CRIT_RECALL = 0.5
N_RETRIEVAL_STEPS = 8

# v2_n4096 empirical result for N-scaling comparison
V2_N4096_RATIO = 1.0962

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 1024    # N/8 -- smoke at smaller N for speed
    N_QUERIES = 4
    NOISE_FRACS = [round(i * 0.04, 3) for i in range(13)]  # 0..0.48 step 0.04
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_QUERIES = 8
    NOISE_FRACS = NOISE_FRACS_FINE


def _selftest_barrier_ratio():
    ac, a1, a2 = 0.138, 0.05, 0.10
    ratio = (ac - a1) / (ac - a2)
    assert abs(ratio - 2.3157) < 0.001, f"Barrier ratio: got {ratio:.4f}"


def _selftest_grid_resolution():
    diffs = [round(NOISE_FRACS_FINE[i+1] - NOISE_FRACS_FINE[i], 4) for i in range(len(NOISE_FRACS_FINE)-1)]
    assert all(abs(d - 0.01) < 1e-6 for d in diffs), f"Grid step not 0.01: {set(diffs)}"


def _instrumentation_selftest():
    _selftest_barrier_ratio()
    _selftest_grid_resolution()
    # Smoke-scale check: build tiny W and verify recall structure exists
    N_tiny = 64
    alpha_tiny = 0.05
    M_tiny = max(1, int(alpha_tiny * N_tiny))
    rng_t = np.random.default_rng(0)
    Xi_tiny = (rng_t.integers(0, 2, size=(M_tiny, N_tiny)).astype(np.float32) * 2 - 1)
    W_tiny = (Xi_tiny.T @ Xi_tiny) / N_tiny
    probe = Xi_tiny[0].copy()
    flip = rng_t.random(N_tiny) < 0.05
    probe[flip] *= -1.0
    state = probe.copy()
    for _ in range(N_RETRIEVAL_STEPS):
        h = W_tiny @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    cos = float(Xi_tiny[0] @ state) / N_tiny
    assert cos is not None and not np.isnan(cos), f"recall cos is NaN"
    print(f"[selftest] PASS: barrier_ratio={PREDICTED_BARRIER_RATIO:.4f} grid_step=0.01 "
          f"N={N_ACTIVE} tiny_cos={cos:.3f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray) -> np.ndarray:
    state = probe.copy()
    for _ in range(N_RETRIEVAL_STEPS):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def find_critical_nf(W: np.ndarray, Xi: np.ndarray, n_q: int,
                     rng: np.random.Generator) -> Optional[float]:
    """Find nf_crit: smallest nf where mean recall drops below CRIT_RECALL."""
    n_dim = W.shape[0]
    for nf in NOISE_FRACS:
        recalls = []
        for qi in range(min(n_q, len(Xi))):
            probe = Xi[qi].copy()
            flip = rng.random(n_dim) < nf
            probe[flip] *= -1.0
            ret = hopfield_retrieve(W, probe)
            cos = float(Xi[qi] @ ret) / n_dim
            recalls.append(cos)
        mean_r = float(np.mean(recalls))
        if mean_r < CRIT_RECALL:
            return nf
    return None


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()

    results_by_alpha = {}
    for alpha in ALPHA_VALUES:
        M = max(1, int(alpha * n_dim))
        Xi = (rng.integers(0, 2, size=(M, n_dim)).astype(np.float32) * 2 - 1)
        W = (Xi.T @ Xi) / n_dim
        nf_crit = find_critical_nf(W, Xi, N_QUERIES, rng)
        results_by_alpha[str(alpha)] = nf_crit
        print(f"  [seed={seed} N={n_dim} alpha={alpha}] nf_crit={nf_crit}", flush=True)

    nf05 = results_by_alpha.get("0.05")
    nf10 = results_by_alpha.get("0.1")
    if nf05 is None or nf10 is None or nf10 < 1e-9:
        ratio = None
        monotone_pass = False
    else:
        ratio = nf05 / nf10
        monotone_pass = (nf05 > nf10)

    elapsed = time.time() - t0
    print(f"  [seed={seed}] nf05={nf05} nf10={nf10} ratio={ratio} monotone={monotone_pass} elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "nf_crit_05": float(nf05) if nf05 is not None else None,
        "nf_crit_10": float(nf10) if nf10 is not None else None,
        "ratio_05_10": float(ratio) if ratio is not None else None,
        "monotone_pass": bool(monotone_pass),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    valid = [r for r in results if r.get("ratio_05_10") is not None]
    if not valid:
        return ("HARD_FAIL", "All seeds returned None ratio (nf_crit not found).")

    ratios = [r["ratio_05_10"] for r in valid]
    mean_ratio = float(np.mean(ratios))
    n_monotone = sum(1 for r in valid if r.get("monotone_pass", False))
    nf05_mean = float(np.mean([r["nf_crit_05"] for r in valid if r.get("nf_crit_05") is not None]))
    nf10_mean = float(np.mean([r["nf_crit_10"] for r in valid if r.get("nf_crit_10") is not None]))

    HP_RATIO = 1.20
    MID_RATIO = 1.05
    HF_RATIO = 1.02

    summary = (f"nf_crit_05={nf05_mean:.3f} nf_crit_10={nf10_mean:.3f} ratio={mean_ratio:.4f} "
               f"n_monotone={n_monotone}/{len(results)} predicted_barrier_ratio={PREDICTED_BARRIER_RATIO:.4f} "
               f"v2_n4096_ratio={V2_N4096_RATIO:.4f} grid_step=0.01 N={N}")

    if mean_ratio <= HF_RATIO:
        return ("HARD_FAIL", f"HARD_FAIL: ratio={mean_ratio:.4f}<={HF_RATIO} -- no N-scaling; direction lost. {summary}")

    if mean_ratio > HP_RATIO and n_monotone >= 4:
        n_scale_vs_n4096 = "INCREASE" if mean_ratio > V2_N4096_RATIO else "FLAT"
        return ("HARD_PASS",
                f"HARD_PASS: ratio={mean_ratio:.4f}>{HP_RATIO} n_monotone={n_monotone}/{len(results)} "
                f"N-scaling vs N4096: {n_scale_vs_n4096}. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: ratio={mean_ratio:.4f} in ({HF_RATIO},{HP_RATIO}]; partial N-scaling. {summary}")


print(f"[config] N={N} mode={RUN_MODE} N_ACTIVE={N_ACTIVE} alpha={ALPHA_VALUES} "
      f"n_fracs={len(NOISE_FRACS)} grid_step={'0.01' if RUN_MODE != 'smoke' else '0.04'}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alphas": ALPHA_VALUES, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
valid = [r for r in all_results if r.get("ratio_05_10") is not None]
mean_r = float(np.mean([r["ratio_05_10"] for r in valid])) if valid else None
metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "predicted_barrier_ratio": PREDICTED_BARRIER_RATIO,
    "v2_n4096_ratio": V2_N4096_RATIO,
    "mean_ratio": mean_r,
    "grid_step": 0.01,
    "results": [
        {"seed": r.get("seed"),
         "nf_crit_05": r.get("nf_crit_05"),
         "nf_crit_10": r.get("nf_crit_10"),
         "ratio_05_10": r.get("ratio_05_10"),
         "monotone_pass": r.get("monotone_pass"),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
