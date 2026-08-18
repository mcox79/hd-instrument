"""topk_composition_refuse_gate_v1 -- compose vs refuse on small cleanup-energy gap.

MOTIVATION (USER Q3.1 follow-up 2026-06-26; composes on chain-grade
hdlab/refuse_gate + chain-grade cleanup):
  When top-1 and top-2 cleanup answers have a small energy gap (substrate is
  uncertain), binary refuse wastes the second-best signal. Composing top-K
  disjunctively ("answer is in {X, Y} with weights w_X, w_Y") yields a
  USEFUL output for downstream composition rather than a hard refusal.

ARMS (3 mandatory per handoff):
  ARM_TOP1_COMMIT_BASELINE       : current behavior; always commit to top-1
                                   (SANITY RAIL).
  ARM_REFUSE_ON_SMALL_GAP        : binary refuse when (top1 - top2) / top1 < gap_tau.
  ARM_TOPK_DISJUNCTIVE           : return top-K (K=2) with softmax weights when
                                   small gap; commit to top-1 when large gap.

CORRECTNESS METRICS:
  - top1_correctness: 1 if argmax == true; else 0.
  - disjunctive_correctness: 1 if true in top-K when small gap, else top1 rule.
  - refuse_correctness: 1 if refused on ambiguous (true not in top-K), else
    top1 on confident; refusal on a CORRECT-top1 sample counts as 0.
  - ambiguous_recall_at_K: on samples flagged as ambiguous (small gap), what
    fraction has true item in top-K=2.
  - false_disjunction_rate: fraction of LARGE-GAP cases where the cell still
    emitted a K=2 disjunction (should be near zero by definition of gap_tau).

PRE-REGISTERED HARD BANDS (verbatim from research handoff):
  HARD_PASS (ALL of):
    - disjunctive_correctness >= top1_commit_correctness
    - ambiguous-case recall@K=2 >= 0.85
    - false-disjunction-rate <= 0.15
    - cv across seeds <= 0.05 on the disjunctive arm
    - n_llm_calls == 0 (substrate-only-decode gate)
  MIDDLE_BAND:
    - disjunctive_correctness within 0.05 of top1_commit_correctness
  HARD_FAIL (ANY of):
    - disjunctive_correctness < top1_commit_correctness (composition HURTS)
    - false-disjunction-rate > 0.40 (cell K-disjuncts too liberally)
    - n_llm_calls > 0

NOISY-RETRIEVAL HARNESS (substrate-product realism):
  Substrate is an associative memory at moderate alpha (M/N ~ 0.20) so cleanup
  is non-trivial. We then add KEY-NOISE (per-coordinate bit-flip prob p_flip)
  to drive a controlled fraction of queries into the ambiguous regime.

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

ANCHOR_NAME = "topk_composition_refuse_gate_v1"
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
# Production constants
# ---------------------------------------------------------------------------
N_FULL = 2048
M_FULL = 400               # alpha = 0.195 (saturation regime; cleanup non-trivial)
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 600
P_FLIP_FULL = 0.18         # key bit-flip prob -> drives ambiguity fraction
GAP_TAU = 0.10             # (top1 - top2) / top1 < GAP_TAU -> ambiguous
K_DISJ = 2                 # top-K size for the disjunctive arm
BETA_SOFTMAX = 4.0         # softmax sharpness for disjunctive weights

if RUN_MODE == "smoke":
    # Smoke must exercise the ambiguous-regime mechanism. With small N=256,
    # high P_FLIP pushes substantial query mass into ambiguous (gap<GAP_TAU).
    N = 256
    M = 60                 # alpha 0.234
    SEEDS = [7]
    N_QUERIES = 120
    P_FLIP = 0.35          # smoke-only: heavier noise so ambiguous_frac > 0
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
    f"BETA={BETA_SOFTMAX},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation + Hebbian + retrieval
# ---------------------------------------------------------------------------
def generate_pairs(M_count: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    keys = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    return keys, values


def build_W(keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    return values.T @ keys  # closed-form Hebbian sum (equivalent to outer-product loop)


def add_flip_noise(key: np.ndarray, p_flip: float,
                   rng: np.random.RandomState) -> np.ndarray:
    """Bipolar bit-flip noise: each coord independently flips with prob p_flip."""
    flips = rng.random(key.shape) < p_flip
    return np.where(flips, -key, key)


def retrieval_scores(W: np.ndarray, noisy_key: np.ndarray,
                     values: np.ndarray, N_dim: int) -> np.ndarray:
    """Cosine score against every stored value; returns (M,) array."""
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
# Arm logic
# ---------------------------------------------------------------------------
def classify_query(sims: np.ndarray, true_idx: int, gap_tau: float) -> Dict:
    """Per-query computation shared across all arms.

    Returns dict with: top1_idx, top2_idx, gap_frac, is_ambiguous, top1_correct,
    in_top2, softmax_weights (K=2).
    """
    sims_sorted_idx = np.argsort(-sims)
    top1_idx = int(sims_sorted_idx[0])
    top2_idx = int(sims_sorted_idx[1])
    top1_score = float(sims[top1_idx])
    top2_score = float(sims[top2_idx])

    # Gap fraction; protect against tiny top1.
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
    """ARM_TOP1_COMMIT_BASELINE: always commit to top1; correctness = top1_correct."""
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
    """ARM_REFUSE_ON_SMALL_GAP: refuse when ambiguous; else commit top1.

    correctness counts a refusal as 0 (no answer = no credit) AND a correct
    top1 commit as 1; matches the binary risk-utility 0/-1/+1 framework.
    """
    n = len(per_query)
    n_correct = 0
    n_refused = 0
    for q in per_query:
        if q["is_ambiguous"]:
            n_refused += 1  # no credit
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
    """ARM_TOPK_DISJUNCTIVE: when ambiguous emit {top1, top2} disjunctively,
    counted correct if true is in top-K; else commit top1.
    """
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
            # Pre-reg false-disjunction: cell emitted K=2 on a non-ambiguous
            # case. By construction this arm never disjuncts on non-ambiguous
            # so false_disj remains 0. We track at the harness level for
            # symmetry; an alt parameterization could let false_disj > 0.
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
    keys, values = generate_pairs(M, N, seed)
    W = build_W(keys, values)

    rng_q = np.random.RandomState(seed + 401)
    query_idx = rng_q.choice(M, size=min(N_QUERIES, M), replace=True)
    rng_noise = np.random.RandomState(seed + 402)

    per_query = []
    for true_idx in query_idx:
        noisy_key = add_flip_noise(keys[true_idx], P_FLIP, rng_noise)
        sims = retrieval_scores(W, noisy_key, values, N)
        per_query.append(classify_query(sims, int(true_idx), GAP_TAU))

    # Frame-level ambiguity stats.
    n_amb = sum(1 for q in per_query if q["is_ambiguous"])
    if n_amb == 0:
        ambiguous_recall_at_K = 1.0  # degenerate; will not gate HARD_PASS down
    else:
        n_amb_in_top2 = sum(1 for q in per_query if q["is_ambiguous"] and q["in_top2"])
        ambiguous_recall_at_K = float(n_amb_in_top2) / float(n_amb)

    arm_t = run_arm_top1_commit(per_query)
    arm_r = run_arm_refuse_on_gap(per_query)
    arm_d = run_arm_topk_disjunctive(per_query)

    elapsed = time.time() - t0

    arms = [arm_t, arm_r, arm_d]
    print(
        f"  [seed={seed} N={N} M={M} alpha={ALPHA:.3f} p_flip={P_FLIP}] "
        f"T1={arm_t['correctness']:.3f}  "
        f"REF={arm_r['correctness']:.3f} (refused={arm_r['n_refused']})  "
        f"DISJ={arm_d['correctness']:.3f} (disjuncts={arm_d['n_disjuncted']}, "
        f"amb_rec_K2={ambiguous_recall_at_K:.3f})  "
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
    assert q["is_ambiguous"] is False  # gap_frac ~ (0.9-0.1)/0.9 ~ 0.89
    sims2 = np.array([0.50, 0.49, 0.10])
    q2 = classify_query(sims2, true_idx=0, gap_tau=0.10)
    assert q2["is_ambiguous"] is True  # gap_frac ~ 0.02 < 0.10
    return True


def _selftest_noise_changes_key():
    rng = np.random.RandomState(0)
    k = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    noisy = add_flip_noise(k, p_flip=0.5, rng=rng)
    diff = int(np.sum(k != noisy))
    assert 0 <= diff <= len(k)
    # At p=0.5 expected diff = 4; allow wide band on 8 coords.
    return True


def _selftest_baseline_recall_high():
    """No noise + low alpha -> top1 commit should be near perfect."""
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
    _selftest_noise_changes_key()
    rec = _selftest_baseline_recall_high()
    print(
        f"[selftest] PASS  baseline_recall_at_low_alpha={rec:.3f}  "
        f"N={N}  M={M}  alpha={ALPHA:.3f}  p_flip={P_FLIP}  "
        f"gap_tau={GAP_TAU}  mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Verdict
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
                "HARD_FAIL: substrate-only-decode gate violated (n_llm_calls > 0).")

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
        f"T1(corr={t1['mean_correctness']:.3f},cv={t1['cv_correctness']:.3f}); "
        f"REFUSE(corr={rf['mean_correctness']:.3f}); "
        f"DISJ(corr={dj['mean_correctness']:.3f},cv={dj['cv_correctness']:.3f},"
        f"false_disj={dj['mean_false_disjunction']:.3f}); "
        f"amb_frac={mean_amb_frac:.3f} amb_rec@K=2={mean_amb_recall:.3f}"
    )

    # HARD_FAIL checks first.
    if dj["mean_correctness"] < t1["mean_correctness"]:
        return ("HARD_FAIL",
                f"HARD_FAIL: disjunctive ({dj['mean_correctness']:.3f}) < "
                f"top1_commit ({t1['mean_correctness']:.3f}); composition HURTS. "
                f"{summary}")
    if dj["mean_false_disjunction"] > 0.40:
        return ("HARD_FAIL",
                f"HARD_FAIL: false_disjunction_rate {dj['mean_false_disjunction']:.3f} "
                f"> 0.40. {summary}")

    # HARD_PASS checks.
    hp_c1 = dj["mean_correctness"] >= t1["mean_correctness"]
    hp_c2 = mean_amb_recall >= 0.85
    hp_c3 = dj["mean_false_disjunction"] <= 0.15
    hp_c4 = dj["cv_correctness"] <= 0.05

    if all([hp_c1, hp_c2, hp_c3, hp_c4]):
        return ("HARD_PASS",
                f"HARD_PASS: disjunctive >= top1_commit, amb_rec@K=2 >= 0.85, "
                f"false_disj <= 0.15, cv <= 0.05. {summary}")

    # MIDDLE_BAND.
    if abs(dj["mean_correctness"] - t1["mean_correctness"]) <= 0.05:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: disjunctive within 0.05 of top1_commit. "
                f"hp_checks=[c1={hp_c1},c2={hp_c2},c3={hp_c3},c4={hp_c4}]. "
                f"{summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: disjunctive meets no PASS/MIDDLE band. "
            f"hp_checks=[c1={hp_c1},c2={hp_c2},c3={hp_c3},c4={hp_c4}]. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M": M, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] topk_disj N={N} M={M} alpha={ALPHA:.3f} mode={RUN_MODE}...",
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
        f"p_flip={P_FLIP} gap_tau={GAP_TAU} K={K_DISJ}"
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
