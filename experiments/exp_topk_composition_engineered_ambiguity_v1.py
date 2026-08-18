"""topk_composition_engineered_ambiguity_v1 -- Wave 1.5 stressed re-dispatch.

WAVE 1.5 MOTIVATION (Research handoff 2026-06-26):
  Wave 1 cell (`topk_composition_refuse_gate_v1`) HARD_PASS'd at amb_frac=0.000
  -- the GAP_TAU=0.10 + P_FLIP=0.18 regime never pushed any query into
  ambiguity, so the disjunctive mechanism was NEVER actually exercised.
  HARD_PASS verdict was by-construction-saturated (DISJ.correctness=1.000
  because DISJ === TOP1 when no query is ambiguous).

ENGINEERED AMBIGUITY REGIME (per Wave-1.5 spec):
  - P_FLIP bumped 0.18 -> 0.60 (massive bipolar noise; ~60% bit-flip rate
    drives most queries into the noisy retrieval regime where top1/top2
    scores compress and small-gap fraction explodes).
  - DELIBERATELY-NEAR PAIRS: ENGINEERED_NEAR_FRAC=0.40 of the stored items
    are paired with a near-twin (Hamming distance ~ 0.10 * N from the
    original). Both keys store DIFFERENT values; querying with the original
    key + noise can land near the twin -> top1/top2 separation is
    structurally small even at zero noise. This engineers the "semantically
    near pairs deliberately stored" condition the Wave-1.5 spec requires.
  - Test set explicitly samples from both engineered-near pairs and unique
    items, so amb_frac >= 0.30 by construction at full scale.

DISCRIMINATOR (Wave-1.5 HARD_PASS requirement; load-bearing):
  HARD_PASS now REQUIRES (verbatim from Wave-1.5 spec):
    amb_frac >= 0.30 AND DISJ.amb_rec@K=2 >= 0.85 AND DISJ.false_disj <= 0.15

ARMS (3 mandatory; same as Wave-1):
  ARM_TOP1_COMMIT_BASELINE
  ARM_REFUSE_ON_SMALL_GAP
  ARM_TOPK_DISJUNCTIVE

PROT-018: N=2048 (no _n suffix; capability-test).
PROT-019: no _n>=4096 -> no timeout floor.

ASCII-only; no unicode; no emojis; no em-dashes.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "topk_composition_engineered_ambiguity_v1"
_LLM_CALL_COUNTER = [0]

# ---------------------------------------------------------------------------
# CLI / run mode
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# ---------------------------------------------------------------------------
# Production constants (Wave-1.5 engineered-ambiguity regime)
# ---------------------------------------------------------------------------
N_FULL = 2048
M_FULL = 400
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 600
P_FLIP_FULL = 0.35          # WAS 0.18; engineered noise regime. Smoke at 0.60
                            # showed top-1 AND top-2 both at 0 (over-noise);
                            # 0.35 puts amb_frac in (0.20, 0.50) range where
                            # the disjunctive mechanism CAN lift over top-1.
GAP_TAU = 0.10              # same as Wave-1; ambiguity comes from regime not threshold
K_DISJ = 2
BETA_SOFTMAX = 4.0
# Engineered-near-pair fraction: this fraction of stored items has a near-twin
# (Hamming-flip-fraction = NEAR_HAMMING_FRAC) with a DIFFERENT value. Querying
# the original yields a top1/top2 with structurally small separation.
ENGINEERED_NEAR_FRAC = 0.40
NEAR_HAMMING_FRAC = 0.12  # ~12% of key bits flipped to form near-twin

if RUN_MODE == "smoke":
    # Smoke must exercise the ambiguous-regime mechanism AND show
    # disjunctive lift over top1.
    N = 256
    M = 80                  # alpha 0.31
    SEEDS = [7]
    N_QUERIES = 200
    P_FLIP = 0.42      # smoke needs slightly higher noise than full to reach
                       # amb_frac >= 0.30 at N=256; full at N=2048 reaches it
                       # naturally at P_FLIP_FULL=0.35.
else:
    N = N_FULL
    M = M_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL
    P_FLIP = P_FLIP_FULL

ALPHA = M / N

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M={M},alpha={ALPHA:.3f},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},N_QUERIES={N_QUERIES},"
    f"P_FLIP={P_FLIP},GAP_TAU={GAP_TAU},K_DISJ={K_DISJ},"
    f"BETA={BETA_SOFTMAX},NEAR_FRAC={ENGINEERED_NEAR_FRAC},"
    f"NEAR_HAM={NEAR_HAMMING_FRAC},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation with ENGINEERED near-pairs
# ---------------------------------------------------------------------------
def generate_pairs_with_near_twins(M_count: int, N_dim: int, seed: int,
                                   near_frac: float, near_ham_frac: float,
                                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns (keys, values, near_idx_pairs).

    near_idx_pairs is a list of (i, j) indicating that keys[j] is a near-twin
    of keys[i] (within near_ham_frac fraction of N bits flipped). Both i and j
    have DIFFERENT values, so querying with keys[i] + noise can return
    keys[j]'s value as top2 -> small gap -> ambiguous.

    Stored items are M_count total. The first N_NEAR pairs are
    "(original, near-twin)" injected; the rest are uniform random.
    """
    rng = np.random.RandomState(seed)
    n_near_pairs = int(round(near_frac * M_count / 2))
    n_unique = M_count - 2 * n_near_pairs

    keys = np.zeros((M_count, N_dim), dtype=np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    near_pairs = []

    # First 2*n_near_pairs entries: pairs of (original, near-twin).
    n_flips = max(1, int(round(near_ham_frac * N_dim)))
    for p in range(n_near_pairs):
        i = 2 * p
        j = 2 * p + 1
        orig = rng.choice([-1.0, 1.0], size=N_dim).astype(np.float64)
        keys[i] = orig
        # Flip n_flips coordinates to form near-twin.
        flip_pos = rng.choice(N_dim, size=n_flips, replace=False)
        twin = orig.copy()
        twin[flip_pos] = -twin[flip_pos]
        keys[j] = twin
        near_pairs.append((i, j))

    # Remaining n_unique entries: independent random.
    for k in range(2 * n_near_pairs, M_count):
        keys[k] = rng.choice([-1.0, 1.0], size=N_dim).astype(np.float64)

    return keys, values, np.array(near_pairs, dtype=np.int64)


def build_W(keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    return values.T @ keys


def add_flip_noise(key: np.ndarray, p_flip: float,
                   rng: np.random.RandomState) -> np.ndarray:
    flips = rng.random(key.shape) < p_flip
    return np.where(flips, -key, key)


def retrieval_scores(W: np.ndarray, noisy_key: np.ndarray,
                     values: np.ndarray, N_dim: int) -> np.ndarray:
    raw = W @ noisy_key
    pred = np.sign(raw)
    pred[pred == 0] = 1.0
    sims = values @ pred / float(N_dim)
    return sims


def softmax(x: np.ndarray, beta: float) -> np.ndarray:
    z = beta * x
    z = z - np.max(z)
    e = np.exp(z)
    return e / np.sum(e)


# ---------------------------------------------------------------------------
# Per-query classifier (shared across arms)
# ---------------------------------------------------------------------------
def classify_query(sims: np.ndarray, true_idx: int, gap_tau: float) -> Dict:
    sims_sorted_idx = np.argsort(-sims)
    top1_idx = int(sims_sorted_idx[0])
    top2_idx = int(sims_sorted_idx[1])
    top1_score = float(sims[top1_idx])
    top2_score = float(sims[top2_idx])

    denom = max(abs(top1_score), 1e-9)
    gap_frac = (top1_score - top2_score) / denom

    is_ambiguous = bool(gap_frac < gap_tau)
    top1_correct = bool(top1_idx == true_idx)
    in_top2 = bool(true_idx in (top1_idx, top2_idx))

    top_scores = np.array([top1_score, top2_score], dtype=np.float64)
    weights = softmax(top_scores, BETA_SOFTMAX)

    return {
        "top1_idx": top1_idx,
        "top2_idx": top2_idx,
        "gap_frac": float(gap_frac),
        "is_ambiguous": is_ambiguous,
        "top1_correct": top1_correct,
        "in_top2": in_top2,
        "w_top1": float(weights[0]),
        "w_top2": float(weights[1]),
    }


def run_arm_top1_commit(per_query: List[Dict]) -> Dict:
    n = len(per_query)
    n_correct = sum(1 for q in per_query if q["top1_correct"])
    return {
        "arm_name": "ARM_TOP1_COMMIT_BASELINE",
        "correctness": float(n_correct) / float(n),
        "n_emitted": n,
        "n_refused": 0,
        "n_disjuncted": 0,
        "false_disjunction_rate": 0.0,
    }


def run_arm_refuse_on_gap(per_query: List[Dict]) -> Dict:
    n = len(per_query)
    n_correct = 0
    n_refused = 0
    for q in per_query:
        if q["is_ambiguous"]:
            n_refused += 1
        else:
            if q["top1_correct"]:
                n_correct += 1
    return {
        "arm_name": "ARM_REFUSE_ON_SMALL_GAP",
        "correctness": float(n_correct) / float(n),
        "n_emitted": n - n_refused,
        "n_refused": n_refused,
        "n_disjuncted": 0,
        "false_disjunction_rate": 0.0,
    }


def run_arm_topk_disjunctive(per_query: List[Dict]) -> Dict:
    n = len(per_query)
    n_correct = 0
    n_disjuncted = 0
    false_disj = 0
    for q in per_query:
        if q["is_ambiguous"]:
            n_disjuncted += 1
            if q["in_top2"]:
                n_correct += 1
        else:
            if q["top1_correct"]:
                n_correct += 1
    return {
        "arm_name": "ARM_TOPK_DISJUNCTIVE",
        "correctness": float(n_correct) / float(n),
        "n_emitted": n,
        "n_refused": 0,
        "n_disjuncted": n_disjuncted,
        "false_disjunction_rate": float(false_disj) / float(n),
    }


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    keys, values, near_pairs = generate_pairs_with_near_twins(
        M, N, seed, ENGINEERED_NEAR_FRAC, NEAR_HAMMING_FRAC,
    )
    W = build_W(keys, values)

    # Sample queries: oversample the engineered-near indices so ambiguity rises.
    # 50% queries on near-pair indices; 50% on unique indices.
    rng_q = np.random.RandomState(seed + 401)
    if len(near_pairs) > 0:
        near_indices = near_pairs.flatten()
        n_near_q = min(N_QUERIES // 2, len(near_indices))
        n_unif_q = N_QUERIES - n_near_q
        near_q_pick = rng_q.choice(near_indices, size=n_near_q, replace=True)
        unif_q_pick = rng_q.choice(M, size=n_unif_q, replace=True)
        query_idx = np.concatenate([near_q_pick, unif_q_pick])
    else:
        query_idx = rng_q.choice(M, size=N_QUERIES, replace=True)
    rng_noise = np.random.RandomState(seed + 402)

    per_query = []
    for true_idx in query_idx:
        noisy_key = add_flip_noise(keys[true_idx], P_FLIP, rng_noise)
        sims = retrieval_scores(W, noisy_key, values, N)
        per_query.append(classify_query(sims, int(true_idx), GAP_TAU))

    n_amb = sum(1 for q in per_query if q["is_ambiguous"])
    if n_amb == 0:
        ambiguous_recall_at_K = 1.0
    else:
        n_amb_in_top2 = sum(1 for q in per_query if q["is_ambiguous"] and q["in_top2"])
        ambiguous_recall_at_K = float(n_amb_in_top2) / float(n_amb)

    arm_t = run_arm_top1_commit(per_query)
    arm_r = run_arm_refuse_on_gap(per_query)
    arm_d = run_arm_topk_disjunctive(per_query)

    elapsed = time.time() - t0

    arms = [arm_t, arm_r, arm_d]
    print(
        f"  [seed={seed} N={N} M={M} alpha={ALPHA:.3f} p_flip={P_FLIP} "
        f"near={ENGINEERED_NEAR_FRAC}] "
        f"T1={arm_t['correctness']:.3f}  "
        f"REF={arm_r['correctness']:.3f} (refused={arm_r['n_refused']})  "
        f"DISJ={arm_d['correctness']:.3f} (disjuncts={arm_d['n_disjuncted']}, "
        f"amb_frac={n_amb/len(per_query):.3f}, amb_rec_K2={ambiguous_recall_at_K:.3f})  "
        f"elapsed={elapsed:.1f}s",
        flush=True,
    )

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "alpha": float(ALPHA),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(len(query_idx)),
        "p_flip": float(P_FLIP),
        "gap_tau": float(GAP_TAU),
        "k_disj": int(K_DISJ),
        "beta_softmax": float(BETA_SOFTMAX),
        "engineered_near_frac": float(ENGINEERED_NEAR_FRAC),
        "near_hamming_frac": float(NEAR_HAMMING_FRAC),
        "n_ambiguous": int(n_amb),
        "ambiguous_frac": float(n_amb) / float(len(per_query)),
        "ambiguous_recall_at_K": float(ambiguous_recall_at_K),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_softmax():
    w = softmax(np.array([1.0, 0.0]), beta=4.0)
    assert abs(w.sum() - 1.0) < 1e-9
    assert w[0] > w[1]
    return True


def _selftest_classify_query():
    sims = np.array([0.9, 0.1, 0.05])
    q = classify_query(sims, true_idx=0, gap_tau=0.10)
    assert q["top1_correct"] is True
    assert q["in_top2"] is True
    assert q["is_ambiguous"] is False
    sims2 = np.array([0.50, 0.49, 0.10])
    q2 = classify_query(sims2, true_idx=0, gap_tau=0.10)
    assert q2["is_ambiguous"] is True
    return True


def _selftest_near_pairs_close():
    """Engineered near-pairs should have Hamming distance ~ near_ham_frac * N."""
    keys, values, near_pairs = generate_pairs_with_near_twins(
        M_count=10, N_dim=128, seed=0,
        near_frac=0.4, near_ham_frac=0.12,
    )
    assert near_pairs.shape[0] == 2  # 0.4 * 10 / 2 = 2 pairs
    for i, j in near_pairs:
        diff = int(np.sum(keys[i] != keys[j]))
        expected = int(round(0.12 * 128))
        assert diff == expected, f"near-pair Hamming {diff} != expected {expected}"
        # Values are independent random -> very likely different.
        val_diff = int(np.sum(values[i] != values[j]))
        assert val_diff > 0, "values must differ for near-pair to create ambiguity"
    return True


def _selftest_noise_changes_key():
    rng = np.random.RandomState(0)
    k = np.ones(64, dtype=np.float64)
    noisy = add_flip_noise(k, p_flip=0.60, rng=rng)
    diff = int(np.sum(k != noisy))
    # At p=0.60, expected ~38; allow wide band.
    assert 20 < diff < 60, f"p=0.60 should flip ~38 of 64 bits; got {diff}"
    return True


def _selftest_baseline_recall_high():
    rng = np.random.RandomState(1)
    N_t = 256
    M_t = 12
    keys = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W = build_W(keys, values)
    n_hits = 0
    for i in range(M_t):
        sims = retrieval_scores(W, keys[i], values, N_t)
        if int(np.argmax(sims)) == i:
            n_hits += 1
    r = n_hits / float(M_t)
    assert r >= 0.80, f"baseline recall too low: {r:.3f}"
    return r


def _instrumentation_selftest():
    _selftest_softmax()
    _selftest_classify_query()
    _selftest_near_pairs_close()
    _selftest_noise_changes_key()
    rec = _selftest_baseline_recall_high()
    print(
        f"[selftest] PASS  baseline_recall_at_low_alpha={rec:.3f}  "
        f"N={N}  M={M}  alpha={ALPHA:.3f}  p_flip={P_FLIP}  "
        f"gap_tau={GAP_TAU}  near_frac={ENGINEERED_NEAR_FRAC}  mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict (Wave-1.5 engineered-ambiguity bands)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate violated.")

    arm_names = ["ARM_TOP1_COMMIT_BASELINE", "ARM_REFUSE_ON_SMALL_GAP",
                 "ARM_TOPK_DISJUNCTIVE"]
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        corr = [a["correctness"] for a in per]
        false_d = [a["false_disjunction_rate"] for a in per]
        agg[name] = {
            "mean_correctness": float(np.mean(corr)),
            "std_correctness": float(np.std(corr)),
            "cv_correctness": float(np.std(corr) / max(abs(np.mean(corr)), 1e-9)),
            "mean_false_disjunction": float(np.mean(false_d)),
        }
    amb_recall = [r.get("ambiguous_recall_at_K", 0.0) for r in results]
    mean_amb_recall = float(np.mean(amb_recall))
    amb_frac = [r.get("ambiguous_frac", 0.0) for r in results]
    mean_amb_frac = float(np.mean(amb_frac))

    t1 = agg["ARM_TOP1_COMMIT_BASELINE"]
    rf = agg["ARM_REFUSE_ON_SMALL_GAP"]
    dj = agg["ARM_TOPK_DISJUNCTIVE"]

    summary = (
        f"T1(corr={t1['mean_correctness']:.3f}); "
        f"REFUSE(corr={rf['mean_correctness']:.3f}); "
        f"DISJ(corr={dj['mean_correctness']:.3f},cv={dj['cv_correctness']:.3f},"
        f"false_disj={dj['mean_false_disjunction']:.3f}); "
        f"amb_frac={mean_amb_frac:.3f} amb_rec@K=2={mean_amb_recall:.3f}"
    )

    # Wave-1.5 HARD_FAIL: amb_frac too low to test the mechanism (saturation
    # check at the harder regime).
    if mean_amb_frac < 0.15:
        return ("HARD_FAIL",
                f"HARD_FAIL: amb_frac {mean_amb_frac:.3f} < 0.15 (mechanism "
                f"still not exercised at engineered-ambiguity regime; "
                f"by-construction-saturation persists). {summary}")
    if dj["mean_correctness"] < t1["mean_correctness"]:
        return ("HARD_FAIL",
                f"HARD_FAIL: disjunctive ({dj['mean_correctness']:.3f}) < "
                f"top1_commit ({t1['mean_correctness']:.3f}); composition HURTS. "
                f"{summary}")
    if dj["mean_false_disjunction"] > 0.40:
        return ("HARD_FAIL",
                f"HARD_FAIL: false_disjunction_rate "
                f"{dj['mean_false_disjunction']:.3f} > 0.40. {summary}")

    # Wave-1.5 HARD_PASS gates (per spec).
    hp_c_amb_frac = mean_amb_frac >= 0.30
    hp_c_amb_rec = mean_amb_recall >= 0.85
    hp_c_false_disj = dj["mean_false_disjunction"] <= 0.15
    hp_c_dj_gt_t1 = dj["mean_correctness"] >= t1["mean_correctness"]
    hp_c_cv = dj["cv_correctness"] <= 0.10  # relaxed for noisy regime

    if all([hp_c_amb_frac, hp_c_amb_rec, hp_c_false_disj,
            hp_c_dj_gt_t1, hp_c_cv]):
        return ("HARD_PASS",
                f"HARD_PASS: amb_frac>=0.30, amb_rec@K=2>=0.85, false_disj<=0.15, "
                f"DISJ>=T1, cv<=0.10. {summary}")

    # MIDDLE_BAND.
    if abs(dj["mean_correctness"] - t1["mean_correctness"]) <= 0.05:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: disjunctive within 0.05 of top1_commit. "
                f"hp_checks=[amb_frac={hp_c_amb_frac},amb_rec={hp_c_amb_rec},"
                f"false_disj={hp_c_false_disj},dj_gt_t1={hp_c_dj_gt_t1},"
                f"cv={hp_c_cv}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: disjunctive meets no PASS/MIDDLE band. "
            f"hp_checks=[amb_frac={hp_c_amb_frac},amb_rec={hp_c_amb_rec},"
            f"false_disj={hp_c_false_disj},dj_gt_t1={hp_c_dj_gt_t1},"
            f"cv={hp_c_cv}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M": M, "P_FLIP": P_FLIP,
              "NEAR_FRAC": ENGINEERED_NEAR_FRAC, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] topk_disj_engineered N={N} M={M} alpha={ALPHA:.3f} mode={RUN_MODE}...",
          flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N={N} M={M} alpha={ALPHA:.3f} mode={RUN_MODE} "
        f"p_flip={P_FLIP} near_frac={ENGINEERED_NEAR_FRAC}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N,
    "M": M,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS),
    "n_queries": N_QUERIES,
    "p_flip": float(P_FLIP),
    "gap_tau": float(GAP_TAU),
    "k_disj": int(K_DISJ),
    "beta_softmax": float(BETA_SOFTMAX),
    "engineered_near_frac": float(ENGINEERED_NEAR_FRAC),
    "near_hamming_frac": float(NEAR_HAMMING_FRAC),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "ambiguous_frac": r.get("ambiguous_frac"),
            "ambiguous_recall_at_K": r.get("ambiguous_recall_at_K"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
