"""
caching_lfu_lru_arc_tier0_unified_n8192_v1 -- Caching Tier 0 unified at N=8192.

SCIENTIFIC QUESTION (Caching Tier 0 unified policy battery at production envelope):
  Prior caching tests at N=1024-4096 confirmed substrate's score-based eviction
  correlates with LRU, LFU, and hybrid policies. This anchor validates that the
  same unified substrate score metric works at production envelope N=8192,
  which doubles the vector dimensionality from prior confirmed results.

  Three policies tested together:
  (a) LFU-correlated eviction: substrate score correlates with frequency of access.
      Spearman rho(substrate_score, access_frequency) >= 0.60.
  (b) LRU-correlated eviction: substrate score correlates with recency of access.
      Spearman rho(substrate_score, access_recency) >= 0.60.
  (c) ARC-like balance: substrate score correlates with combined LFU+LRU balance
      (ARC policy adapts between LRU and LFU based on workload).
      Spearman rho(substrate_score, arc_hybrid_score) >= 0.60.

  KEY CLAIM: substrate's single eigenvalue contribution score xi^T W xi / N
  captures ALL THREE policies simultaneously -- this is the "Tier 0 unified"
  property: no separate tracking data structures needed.

PRE-REGISTERED HARD-PASS:
  HP-LFU: rho(substrate_score, access_freq) >= 0.60 in >= 4/5 seeds
  HP-LRU: rho(substrate_score, access_recency) >= 0.60 in >= 4/5 seeds
  HP-ARC: rho(substrate_score, arc_hybrid) >= 0.60 in >= 4/5 seeds

PRE-REGISTERED HARD-FAIL:
  HF-LFU: rho(substrate_score, access_freq) < 0.20 (score blind to frequency)
  HF-LRU: rho(substrate_score, access_recency) < 0.20 (score blind to recency)

MIDDLE BAND:
  any rho in [0.20, 0.60) OR only 2/3 policies pass

P_deflated: 0.65 (caching_lru_lfu_hybrid_v1 at N=1024 completed; N=8192 is 8x
  larger -- same theory applies but numerical scaling test; calibration bands wider)

FORMULA SELF-TESTS:
  1. Substrate score: xi^T W xi / N measures self-energy in W.
     For M writes of xi_k, score[k] = (1 + (M_k-1)*overlap^2)/N_contrib.
     [INPUT: N=1024, xi written 3x vs 1x] [EXPECTED: 3x pattern has higher score]
  2. Spearman rho of perfect ranking: rho([1,2,3], [1,2,3]) = 1.0.
     [INPUT: perfect rank lists] [EXPECTED: rho=1.0]
  3. N=8192 capacity check: at alpha=0.05, N=8192*0.05=410 patterns, well within
     alpha_c=0.138.
     [INPUT: N=8192, M=200] [EXPECTED: alpha=0.0244 < alpha_c]

PROT-018: anchor has _n8192 -> N MUST = 8192.
PROT-021: run_config includes N, M_PATTERNS, run_mode.
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "caching_lfu_lru_arc_tier0_unified_n8192_v1"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

ALPHA_C = 0.138

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_PATTERNS = 50    # 50 distinct patterns in the "cache"
    MAX_WRITES = 200   # total write events (some patterns written multiple times)
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_PATTERNS = 200   # 200 distinct cache items at production
    MAX_WRITES = 800   # total writes (4 per pattern on average; mix of hot/cold)

HP_RHO = 0.60
HF_RHO = 0.20


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    n = len(x)
    if n < 3:
        return 0.0
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    d = rx - ry
    return float(1.0 - 6.0 * float(np.sum(d**2)) / (n * (n * n - 1)))


# ---- FORMULA SELF-TESTS ----
def _selftest_substrate_score():
    """Pattern written 3x has higher score than pattern written 1x."""
    N_t = 1024
    rng = np.random.RandomState(0)
    xi_hot = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    xi_cold = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W = np.zeros((N_t, N_t), dtype=np.float64)
    # Write hot 3x, cold 1x
    for _ in range(3):
        W += np.outer(xi_hot, xi_hot) / float(N_t)
    W += np.outer(xi_cold, xi_cold) / float(N_t)
    np.fill_diagonal(W, 0.0)
    score_hot = float(np.dot(xi_hot, W @ xi_hot)) / N_t
    score_cold = float(np.dot(xi_cold, W @ xi_cold)) / N_t
    assert score_hot > score_cold, f"hot score {score_hot:.4f} <= cold {score_cold:.4f}"
    return score_hot, score_cold


def _selftest_spearman():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    rho = spearman_rho(x, x)
    assert abs(rho - 1.0) < 1e-10, f"spearman_rho selftest: {rho:.4f}"
    return rho


def _selftest_capacity():
    alpha = M_PATTERNS / N
    assert alpha < ALPHA_C, f"alpha={alpha:.4f} >= alpha_c"
    return alpha


def _instrumentation_selftest():
    sh, sc = _selftest_substrate_score()
    rho = _selftest_spearman()
    alpha = _selftest_capacity()
    print(
        f"[selftest] PASS: score_hot={sh:.4f} score_cold={sc:.4f} "
        f"spearman_self={rho:.4f} alpha={alpha:.4f} N={N} M={M_PATTERNS}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)

    # Generate M_PATTERNS distinct cache items
    Xi = rng.choice([-1.0, 1.0], size=(M_PATTERNS, N)).astype(np.float64)

    # Generate access pattern: mixed hot/cold and recent/old
    # Hot patterns: top 20% accessed 5x; cold: bottom 40% accessed 1x
    # Recency: later accesses = more recent
    n_hot = max(1, M_PATTERNS // 5)
    n_cold = max(1, M_PATTERNS * 2 // 5)
    hot_indices = list(range(n_hot))
    cold_indices = list(range(M_PATTERNS - n_cold, M_PATTERNS))

    # Build access schedule
    access_times = {k: [] for k in range(M_PATTERNS)}
    rng_schedule = np.random.RandomState(seed + 100)
    t_current = 0
    for _ in range(MAX_WRITES):
        # Sample: 50% hot, 30% random, 20% cold
        r = rng_schedule.random()
        if r < 0.50:
            k = hot_indices[rng_schedule.randint(0, len(hot_indices))]
        elif r < 0.80:
            k = rng_schedule.randint(0, M_PATTERNS)
        else:
            k = cold_indices[rng_schedule.randint(0, len(cold_indices))]
        access_times[k].append(t_current)
        t_current += 1

    # Build W from access schedule
    W = np.zeros((N, N), dtype=np.float64)
    for k, times in access_times.items():
        for _ in times:
            W += np.outer(Xi[k], Xi[k]) / float(N)
    np.fill_diagonal(W, 0.0)

    # Compute substrate score per pattern
    substrate_scores = np.array([
        float(np.dot(Xi[k], W @ Xi[k])) / N
        for k in range(M_PATTERNS)
    ])

    # Compute ground-truth metrics per pattern
    access_freqs = np.array([float(len(access_times[k])) for k in range(M_PATTERNS)])
    # Recency: last access time (0 if never accessed)
    access_recency = np.array([
        float(max(access_times[k])) if access_times[k] else 0.0
        for k in range(M_PATTERNS)
    ])
    # ARC hybrid: 0.5 * recency_normalized + 0.5 * freq_normalized
    freq_norm = access_freqs / (access_freqs.max() + 1e-12)
    rec_norm = access_recency / (access_recency.max() + 1e-12)
    arc_scores = 0.5 * freq_norm + 0.5 * rec_norm

    # Filter to patterns with at least 1 access (non-zero score)
    valid = access_freqs > 0
    if valid.sum() < 3:
        valid = np.ones(M_PATTERNS, dtype=bool)

    rho_lfu = spearman_rho(substrate_scores[valid], access_freqs[valid])
    rho_lru = spearman_rho(substrate_scores[valid], access_recency[valid])
    rho_arc = spearman_rho(substrate_scores[valid], arc_scores[valid])

    hp_lfu = rho_lfu >= HP_RHO
    hp_lru = rho_lru >= HP_RHO
    hp_arc = rho_arc >= HP_RHO

    hf_lfu = rho_lfu < HF_RHO
    hf_lru = rho_lru < HF_RHO

    n_valid = int(valid.sum())
    elapsed = time.time() - t0
    print(
        f"  [seed={seed} N={N} M={M_PATTERNS} valid={n_valid}] "
        f"rho_lfu={rho_lfu:.4f}(HP>={HP_RHO}) "
        f"rho_lru={rho_lru:.4f}(HP>={HP_RHO}) "
        f"rho_arc={rho_arc:.4f}(HP>={HP_RHO}) "
        f"hp=[lfu:{int(hp_lfu)},lru:{int(hp_lru)},arc:{int(hp_arc)}] "
        f"elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed, "N": N, "M_PATTERNS": M_PATTERNS, "run_mode": RUN_MODE,
        "rho_lfu": float(rho_lfu), "rho_lru": float(rho_lru), "rho_arc": float(rho_arc),
        "n_valid": int(n_valid),
        "hp_lfu": bool(hp_lfu), "hp_lru": bool(hp_lru), "hp_arc": bool(hp_arc),
        "hf_lfu": bool(hf_lfu), "hf_lru": bool(hf_lru),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_lfu = float(np.mean([r["rho_lfu"] for r in results]))
    mean_lru = float(np.mean([r["rho_lru"] for r in results]))
    mean_arc = float(np.mean([r["rho_arc"] for r in results]))
    lfu_n = sum(1 for r in results if r["hp_lfu"])
    lru_n = sum(1 for r in results if r["hp_lru"])
    arc_n = sum(1 for r in results if r["hp_arc"])
    hf_lfu_any = any(r["hf_lfu"] for r in results)
    hf_lru_any = any(r["hf_lru"] for r in results)

    summary = (
        f"n_seeds={n} rho_lfu={mean_lfu:.4f}(HP>={HP_RHO}) "
        f"rho_lru={mean_lru:.4f}(HP>={HP_RHO}) rho_arc={mean_arc:.4f} "
        f"hp_lfu={lfu_n}/{n} hp_lru={lru_n}/{n} hp_arc={arc_n}/{n}"
    )

    if hf_lfu_any:
        return ("HARD_FAIL", f"HARD_FAIL HF-LFU: score blind to access frequency. {summary}")
    if hf_lru_any:
        return ("HARD_FAIL", f"HARD_FAIL HF-LRU: score blind to access recency. {summary}")

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [lfu_n, lru_n, arc_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 3 policies pass in >={min_threshold}/{n} seeds. {summary}")

    n_hp_conds = sum([lfu_n >= min_threshold, lru_n >= min_threshold, arc_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 policies pass. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 policies pass. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_PATTERNS": M_PATTERNS, "MAX_WRITES": MAX_WRITES, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
    f"(N={N} M={M_PATTERNS} mode={RUN_MODE})",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] caching_lfu_lru_arc_tier0_unified N={N} M={M_PATTERNS}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M_PATTERNS": M_PATTERNS,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed_s,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "rho_lfu": r.get("rho_lfu"), "rho_lru": r.get("rho_lru"),
            "rho_arc": r.get("rho_arc"),
            "hp_lfu": r.get("hp_lfu"), "hp_lru": r.get("hp_lru"),
            "hp_arc": r.get("hp_arc"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
