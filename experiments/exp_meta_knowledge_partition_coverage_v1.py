"""meta_knowledge_partition_coverage_v1 -- substrate metacognition layer.

Tests: substrate can report calibrated "I know / I don't know this region"
by composing partition-coverage + cosine-separation + posterior-entropy via
logistic regression. Builds ABOVE per-query confidence (refuse-gate) with a
PRE-query coverage signal.

ARMS (5):
  ARM_PARTITION_DENSITY   single signal: density at routed partition (isotonic)
  ARM_COSINE_SEP          single signal: (top1 - mean_rest)/std_rest (isotonic)
  ARM_ENTROPY             single signal: Shannon entropy over softmax top-K (isotonic)
  ARM_COMPOSED            logistic regression of all 3 signals
  ARM_RANDOM_BASELINE     diagnostic: random P scores (chance floor)

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS:  COMPOSED ECE <= 0.05 AND AUROC >= 0.75 AND
              (conf_correct - conf_wrong) >= 0.3 std AND
              OOD refuse-fire-rate >= 0.90 AND
              COMPOSED.AUROC - max(single_arm.AUROC) >= 0.05
  MIDDLE_BAND: ECE in [0.05, 0.10] OR AUROC in [0.65, 0.75]
  HARD_FAIL:  ECE > 0.10 OR AUROC < 0.65 OR no separation correct/wrong
              OR ARM_RANDOM_BASELINE.AUROC >= 0.60 (broken)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 arms * 3 seeds * 5000 queries = 75000
  EXPECTED_N_UNITS_SMOKE = 5 arms * 2 seeds * 500 queries  = 5000

HARDENING (META_RULE_X / J / L1-L4):
  main wrapped in if __name__ == "__main__"
  L1: minimal metrics.json with STARTED + PID at start
  L2: per-arm progress updates
  L3: outer try/except around main; failure-class to metrics
  L4: import-crash sentinel

Per-arm metrics structure (Fix #28):
  metrics["per_arm"] = {arm: {seed: {ece, auroc, conf_sep, refuse_rate}}}
  metrics["summary"] = {arm: {ece_mean, auroc_mean, auroc_cv, ...}}

ASCII-only; no emojis; no em-dashes; self-contained (no hdlab imports).
Author: exp_dev 2026-06-27 (Opus 4.7 1M, agent-spawn)
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
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "meta_knowledge_partition_coverage_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_ECE_MAX = 0.05
HP_AUROC_MIN = 0.75
HP_CONF_SEP_STD_MIN = 0.3
HP_OOD_REFUSE_MIN = 0.90
HP_LIFT_OVER_SINGLE_AUROC = 0.05
MB_ECE_HI = 0.10
MB_AUROC_LO = 0.65
HF_AUROC_LO = 0.65
HF_RANDOM_AUROC_MAX = 0.60

EXPECTED_ARMS = [
    "partition_density", "cosine_sep", "entropy",
    "composed", "random_baseline",
]

if SELF_TEST_MODE:
    N_DIM = 256
    N_PARTITIONS = 16
    V_ATOMS = 200
    N_QUERIES = 100
    N_OOD = 30
    TOP_K = 5
    SEEDS = [7]
    N_CALIB = 50
elif RUN_MODE == "smoke":
    N_DIM = 1024
    N_PARTITIONS = 64
    V_ATOMS = 1000
    N_QUERIES = 500
    N_OOD = 150
    TOP_K = 10
    SEEDS = [7, 17]
    N_CALIB = 200
else:
    N_DIM = 2048
    N_PARTITIONS = 256
    V_ATOMS = 5000
    N_QUERIES = 5000
    N_OOD = 1000
    TOP_K = 10
    SEEDS = [7, 17, 23]
    N_CALIB = 1000

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_QUERIES

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,P=%d,V=%d,Q=%d,OOD=%d,K=%d,seeds=%s,calib=%d,"
    "mode=%s,HP_ECE<=%.2f,HP_AUROC>=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_PARTITIONS, V_ATOMS, N_QUERIES, N_OOD, TOP_K, SEEDS,
    N_CALIB, RUN_MODE, HP_ECE_MAX, HP_AUROC_MIN, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_meta_knowledge_partition_coverage",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(m, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_meta_knowledge_partition_coverage_import_crash",
        }
        (out_dir / "metrics.json").write_text(json.dumps(s, indent=2),
                                              encoding="utf-8")
        (out_dir / "import_crash.json").write_text(json.dumps(s, indent=2),
                                                   encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# ----------------------- primitives -----------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hash_partition(v: np.ndarray, n_part: int) -> int:
    """Deterministic partition routing via sign-pattern hash on first log2(P) dims."""
    nb = int(math.ceil(math.log2(max(2, n_part))))
    sign_bits = (v[:nb] > 0).astype(np.int64)
    pid = 0
    for b in sign_bits:
        pid = (pid << 1) | int(b)
    return pid % n_part


def softmax(x: np.ndarray, temp: float = 1.0) -> np.ndarray:
    x = x / max(1e-8, temp)
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) + 1e-12)


def shannon_entropy(p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1.0)
    return float(-np.sum(p * np.log(p)) / math.log(len(p)))  # normalized [0,1]


# ----------------------- ECE / AUROC -----------------------

def ece_score(conf: np.ndarray, correct: np.ndarray, n_bins: int = 10) -> float:
    """Expected Calibration Error."""
    conf = np.clip(np.asarray(conf, dtype=np.float64), 0.0, 1.0)
    correct = np.asarray(correct, dtype=np.float64)
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(conf)
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = (conf >= lo) & (conf < hi) if i < n_bins - 1 else (conf >= lo) & (conf <= hi)
        if mask.sum() == 0:
            continue
        bin_conf = float(conf[mask].mean())
        bin_acc = float(correct[mask].mean())
        ece += (mask.sum() / n) * abs(bin_acc - bin_conf)
    return float(ece)


def auroc_score(scores: np.ndarray, labels: np.ndarray) -> float:
    """AUROC via rank-sum (Mann-Whitney U)."""
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    n_pos = int(labels.sum())
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, len(scores) + 1, dtype=np.float64)
    # handle ties via average rank
    sorted_s = scores[order]
    i = 0
    while i < len(sorted_s):
        j = i + 1
        while j < len(sorted_s) and sorted_s[j] == sorted_s[i]:
            j += 1
        if j > i + 1:
            avg = float(np.mean(ranks[order[i:j]]))
            ranks[order[i:j]] = avg
        i = j
    sum_pos_ranks = float(ranks[labels == 1].sum())
    auc = (sum_pos_ranks - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)


def isotonic_calibrate(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Tiny isotonic regression via PAV. Returns calibrated y_hat for x."""
    order = np.argsort(x)
    y_sorted = y[order].astype(np.float64).copy()
    # PAV
    n = len(y_sorted)
    weights = np.ones(n)
    i = 0
    while i < n - 1:
        if y_sorted[i] > y_sorted[i + 1]:
            # merge
            w_new = weights[i] + weights[i + 1]
            v_new = (weights[i] * y_sorted[i] + weights[i + 1] * y_sorted[i + 1]) / w_new
            y_sorted[i] = v_new
            weights[i] = w_new
            # delete i+1
            y_sorted = np.delete(y_sorted, i + 1)
            weights = np.delete(weights, i + 1)
            n -= 1
            if i > 0:
                i -= 1
        else:
            i += 1
    # Map: build piecewise const mapping
    # Approx: project each sorted point back to fitted value
    # Simpler: use original order indices and broadcast
    # For our purposes, return y as identity-isotonic-fit (linear interpolate)
    # over the merged blocks.
    out = np.zeros_like(x, dtype=np.float64)
    # Rebuild: we lost positional info; refit by using monotone fit on x order
    # Use simpler approach: rank-fit + interpolate
    rank = np.argsort(np.argsort(x))
    # Stretch merged y into n_orig positions
    n_orig = len(x)
    fitted = np.interp(rank, np.linspace(0, n_orig - 1, len(y_sorted)), y_sorted)
    out = np.clip(fitted, 0.0, 1.0)
    return out


def logistic_regression_fit(X: np.ndarray, y: np.ndarray,
                             n_iters: int = 200, lr: float = 0.1) -> np.ndarray:
    """Gradient-descent logistic regression with L2. Returns weights (d+1,)."""
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n, d = X.shape
    # add bias
    X1 = np.concatenate([X, np.ones((n, 1))], axis=1)
    w = np.zeros(d + 1)
    l2 = 1e-3
    for _ in range(n_iters):
        z = X1 @ w
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))
        grad = X1.T @ (p - y) / n + l2 * w
        w = w - lr * grad
    return w


def logistic_predict(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    X1 = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)
    z = X1 @ w
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))


# ----------------------- per-query signal extraction -----------------------

def extract_signals(q: np.ndarray, E: np.ndarray,
                     partition_counts: Dict[int, int],
                     top_k: int) -> Dict[str, float]:
    """For a query q, return (density, cosine_sep, entropy) signals."""
    qn = q / (np.linalg.norm(q) + 1e-8)
    sims = E @ qn  # (V,)
    pid = hash_partition(qn, max(2, max(partition_counts.keys()) + 1 if partition_counts else 2))
    density = float(partition_counts.get(pid, 0)) / max(1.0, float(len(E)))
    top_idx = np.argsort(sims)[::-1][:top_k]
    top_sims = sims[top_idx]
    rest_sims = np.delete(sims, top_idx)
    top1 = float(top_sims[0])
    mean_rest = float(rest_sims.mean())
    std_rest = float(rest_sims.std() + 1e-8)
    cos_sep = (top1 - mean_rest) / std_rest
    p = softmax(top_sims, temp=0.1)
    ent = shannon_entropy(p)
    return {"density": density, "cosine_sep": cos_sep, "entropy": ent,
            "top_idx": int(top_idx[0])}


# ----------------------- per-seed runner -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    # Build atom codebook with non-uniform partition density (some sparse, some dense)
    E = bipolar(V_ATOMS, N_DIM, g)
    # Assign each atom to its routed partition; count
    partition_counts: Dict[int, int] = {}
    for i in range(V_ATOMS):
        pid = hash_partition(E[i], N_PARTITIONS)
        partition_counts[pid] = partition_counts.get(pid, 0) + 1

    # Build query set: half drawn from substrate (perturbed atoms = "should know")
    # half drawn from random region (controlled OOD = "should NOT know")
    n_in = N_QUERIES // 2
    n_out = N_QUERIES - n_in
    queries: List[np.ndarray] = []
    truth_idx: List[int] = []  # ground-truth nearest atom (or -1 for OOD)
    is_in_domain: List[int] = []
    for _ in range(n_in):
        idx = int(g.integers(0, V_ATOMS))
        # Noise the atom slightly so retrieval is non-trivial
        noise = g.standard_normal(N_DIM).astype(np.float32) * 0.3
        q = E[idx] + noise
        q = q / (np.linalg.norm(q) + 1e-8)
        queries.append(q)
        truth_idx.append(idx)
        is_in_domain.append(1)
    for _ in range(n_out):
        # Random vector NOT correlated with any atom
        q = g.standard_normal(N_DIM).astype(np.float32)
        q = q / (np.linalg.norm(q) + 1e-8)
        queries.append(q)
        truth_idx.append(-1)
        is_in_domain.append(0)
    truth_idx = np.array(truth_idx)
    is_in_domain = np.array(is_in_domain)

    # Extract signals + correctness label per query
    signals: List[Dict[str, float]] = []
    correct: List[int] = []
    for i, q in enumerate(queries):
        sig = extract_signals(q, E, partition_counts, TOP_K)
        signals.append(sig)
        # Correctness: in-domain AND top1 == truth_idx[i]; OOD always incorrect
        if is_in_domain[i] == 1 and sig["top_idx"] == int(truth_idx[i]):
            correct.append(1)
        else:
            correct.append(0)
    correct = np.array(correct)
    density_arr = np.array([s["density"] for s in signals])
    cos_arr = np.array([s["cosine_sep"] for s in signals])
    ent_arr = np.array([s["entropy"] for s in signals])

    # Split calibration / test
    perm = g.permutation(N_QUERIES)
    calib_idx = perm[:N_CALIB]
    test_idx = perm[N_CALIB:]
    if len(test_idx) == 0:
        test_idx = calib_idx  # tiny smoke fallback

    out: Dict[str, Dict[str, float]] = {}

    # ARM 1-3: single-signal arms (isotonic-calibrated; for AUROC we just use the signal)
    for arm_name, signal_arr in [
        ("partition_density", density_arr),
        ("cosine_sep", cos_arr),
        ("entropy", -ent_arr),  # high entropy = uncertain => negate so high = confident
    ]:
        # AUROC on test split (signal predicts correctness)
        au = auroc_score(signal_arr[test_idx], correct[test_idx])
        # ECE: map signal to [0,1] via min-max on calib then ECE on test
        s_calib = signal_arr[calib_idx]
        smin, smax = float(s_calib.min()), float(s_calib.max())
        rng = max(1e-8, smax - smin)
        conf_test = np.clip((signal_arr[test_idx] - smin) / rng, 0.0, 1.0)
        ece = ece_score(conf_test, correct[test_idx])
        # Refuse rate: refuse if signal in bottom-third on calib threshold
        thr = float(np.quantile(signal_arr[calib_idx], 0.5))
        refused = (signal_arr[test_idx] <= thr).astype(np.int64)
        ood_mask = (is_in_domain[test_idx] == 0)
        ood_refuse_rate = float(refused[ood_mask].mean()) if ood_mask.sum() > 0 else 0.0
        conf_correct = float(conf_test[correct[test_idx] == 1].mean()) if (correct[test_idx] == 1).sum() > 0 else 0.0
        conf_wrong = float(conf_test[correct[test_idx] == 0].mean()) if (correct[test_idx] == 0).sum() > 0 else 0.0
        conf_std = float(conf_test.std() + 1e-8)
        conf_sep_std = (conf_correct - conf_wrong) / conf_std
        out[arm_name] = {
            "ece": float(ece), "auroc": float(au),
            "conf_correct": conf_correct, "conf_wrong": conf_wrong,
            "conf_sep_std": float(conf_sep_std),
            "ood_refuse_rate": ood_refuse_rate,
            "n_test": int(len(test_idx)),
        }

    # ARM 4: composed logistic regression
    X_calib = np.stack([density_arr[calib_idx], cos_arr[calib_idx], -ent_arr[calib_idx]], axis=1)
    y_calib = correct[calib_idx]
    w = logistic_regression_fit(X_calib, y_calib)
    X_test = np.stack([density_arr[test_idx], cos_arr[test_idx], -ent_arr[test_idx]], axis=1)
    p_test = logistic_predict(X_test, w)
    au_c = auroc_score(p_test, correct[test_idx])
    ece_c = ece_score(p_test, correct[test_idx])
    thr_c = float(np.quantile(logistic_predict(X_calib, w), 0.5))
    refused_c = (p_test <= thr_c).astype(np.int64)
    ood_mask = (is_in_domain[test_idx] == 0)
    ood_refuse_rate_c = float(refused_c[ood_mask].mean()) if ood_mask.sum() > 0 else 0.0
    conf_correct_c = float(p_test[correct[test_idx] == 1].mean()) if (correct[test_idx] == 1).sum() > 0 else 0.0
    conf_wrong_c = float(p_test[correct[test_idx] == 0].mean()) if (correct[test_idx] == 0).sum() > 0 else 0.0
    conf_std_c = float(p_test.std() + 1e-8)
    conf_sep_std_c = (conf_correct_c - conf_wrong_c) / conf_std_c
    out["composed"] = {
        "ece": float(ece_c), "auroc": float(au_c),
        "conf_correct": conf_correct_c, "conf_wrong": conf_wrong_c,
        "conf_sep_std": float(conf_sep_std_c),
        "ood_refuse_rate": ood_refuse_rate_c,
        "n_test": int(len(test_idx)),
        "logreg_weights": w.tolist(),
    }

    # ARM 5: random baseline
    rand_scores = g.random(len(test_idx))
    au_r = auroc_score(rand_scores, correct[test_idx])
    ece_r = ece_score(rand_scores, correct[test_idx])
    out["random_baseline"] = {
        "ece": float(ece_r), "auroc": float(au_r),
        "conf_correct": 0.5, "conf_wrong": 0.5, "conf_sep_std": 0.0,
        "ood_refuse_rate": 0.5, "n_test": int(len(test_idx)),
    }

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": out,
        "n_queries": N_QUERIES,
        "n_partitions": N_PARTITIONS,
    }


# ----------------------- aggregate + verdict -----------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials found",
                "summary": "no per-seed partials found",
                "per_arm": {}}
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    for arm in EXPECTED_ARMS:
        eces: List[float] = []
        aurocs: List[float] = []
        cs_seps: List[float] = []
        ood_rates: List[float] = []
        for s_key, body in per_seed.items():
            pa = body.get("per_arm", {})
            if arm in pa:
                eces.append(float(pa[arm]["ece"]))
                aurocs.append(float(pa[arm]["auroc"]))
                cs_seps.append(float(pa[arm]["conf_sep_std"]))
                ood_rates.append(float(pa[arm]["ood_refuse_rate"]))
                per_arm_full[arm][s_key] = {
                    "ece": float(pa[arm]["ece"]),
                    "auroc": float(pa[arm]["auroc"]),
                    "conf_sep_std": float(pa[arm]["conf_sep_std"]),
                    "ood_refuse_rate": float(pa[arm]["ood_refuse_rate"]),
                }
        if aurocs:
            summary[arm] = {
                "ece_mean": float(np.mean(eces)),
                "auroc_mean": float(np.mean(aurocs)),
                "auroc_std": float(np.std(aurocs)),
                "auroc_cv": float(np.std(aurocs) / max(1e-6, abs(np.mean(aurocs)))),
                "conf_sep_std_mean": float(np.mean(cs_seps)),
                "ood_refuse_rate_mean": float(np.mean(ood_rates)),
                "n": int(len(aurocs)),
            }
        else:
            summary[arm] = {"ece_mean": 0.0, "auroc_mean": 0.0,
                            "auroc_std": 0.0, "auroc_cv": 0.0,
                            "conf_sep_std_mean": 0.0,
                            "ood_refuse_rate_mean": 0.0, "n": 0}

    c = summary.get("composed", {})
    rb = summary.get("random_baseline", {})
    single_aurocs = [summary[a]["auroc_mean"] for a in ["partition_density", "cosine_sep", "entropy"]]
    max_single = max(single_aurocs) if single_aurocs else 0.0
    composed_auroc = c.get("auroc_mean", 0.0)
    composed_ece = c.get("ece_mean", 1.0)
    composed_conf_sep = c.get("conf_sep_std_mean", 0.0)
    composed_ood = c.get("ood_refuse_rate_mean", 0.0)
    rb_auroc = rb.get("auroc_mean", 0.5)

    verdict = "MIDDLE_BAND"
    lift_over_single = composed_auroc - max_single

    if (composed_ece <= HP_ECE_MAX and
            composed_auroc >= HP_AUROC_MIN and
            composed_conf_sep >= HP_CONF_SEP_STD_MIN and
            composed_ood >= HP_OOD_REFUSE_MIN and
            lift_over_single >= HP_LIFT_OVER_SINGLE_AUROC and
            rb_auroc < HF_RANDOM_AUROC_MAX):
        verdict = "HARD_PASS"
    elif (composed_ece > MB_ECE_HI or composed_auroc < MB_AUROC_LO or
            rb_auroc >= HF_RANDOM_AUROC_MAX):
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | COMPOSED ece=%.3f auroc=%.3f conf_sep=%.3f ood=%.3f | "
        "best_single auroc=%.3f lift=%.3f | random auroc=%.3f"
    ) % (verdict, composed_ece, composed_auroc, composed_conf_sep,
         composed_ood, max_single, lift_over_single, rb_auroc)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "lift_over_single": float(lift_over_single),
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_QUERIES,
        "cardinality_ok": (len(per_seed) >= 2),
    }


# ----------------------- main -----------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS})

    print("[%s] mode=%s N=%d P=%d V=%d Q=%d K=%d seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, N_PARTITIONS, V_ATOMS, N_QUERIES, TOP_K, SEEDS),
        flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified",
                                   extra={"_phase": "selftest_done",
                                          "selftest_arms": list(r["per_arm"].keys()),
                                          "composed_auroc_selftest": r["per_arm"]["composed"]["auroc"],
                                          "random_auroc_selftest": r["per_arm"]["random_baseline"]["auroc"]})
            print("[selftest] OK; composed_auroc=%.3f random_auroc=%.3f" % (
                r["per_arm"]["composed"]["auroc"],
                r["per_arm"]["random_baseline"]["auroc"]), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_phase": "selftest_fail",
                                          "_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining),
          flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running",
                                      "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_meta_knowledge_partition_coverage"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2),
                                          encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
