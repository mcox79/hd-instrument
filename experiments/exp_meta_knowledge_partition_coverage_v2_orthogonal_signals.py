"""meta_knowledge_partition_coverage_v2_orthogonal_signals -- revival of v1.

V1 (HARD_FAIL): COMPOSED ECE=0.152 AUROC=0.860 lift_over_best_single = -0.000.
Single signals cosine_sep + entropy both reached AUROC=0.86 (chain-grade on
their own) but the composed logistic regression added NOTHING -- because
cosine_sep and entropy are *correlated* signals (both read off the same top-K
similarity vector). Combining correlated signals can't lift over the best one.

V2 FIX (per cell author 2026-06-27): replace correlated trio (density / cos_sep
/ entropy) with ORTHOGONAL signals:
  - MARGIN          (top1 - top2)  -- single-pair separation (NOT a fn of the whole top-K
                                    distribution like entropy/cos_sep)
  - PERTURBATION    cos(top1(q), top1(q + eta)) where eta is small noise --
                    stability under input perturbation (a different physical
                    information channel: query-locality not codebook-shape)
  - PARTITION_DENSITY  same as v1 (kept for ablation continuity; was AUROC=0.49 in v1
                       i.e. near chance -- orthogonal because uninformative not
                       because of channel separation)

ARMS (4):
  ARM_SINGLE_BEST         entropy alone (v1 chain-grade reference; AUROC=0.86)
  ARM_COMPOSED_OLD        correlated trio (density + cos_sep + entropy); v1 baseline
  ARM_COMPOSED_ORTHOGONAL margin + perturbation + density (new fix)
  ARM_RANDOM_CONTROL      chance floor

PRE-REG BANDS (LOCKED at module init; PROSPECTIVE):
  HARD_PASS:   ORTHOGONAL.AUROC - SINGLE_BEST.AUROC >= 0.05 AND
               ORTHOGONAL.AUROC - OLD.AUROC          >= 0.05 AND
               ORTHOGONAL.ECE                         <= 0.10 AND
               RANDOM_CONTROL.AUROC                   <  0.60
  MIDDLE_BAND: ORTHOGONAL.AUROC - SINGLE_BEST.AUROC in [0.02, 0.05)
  HARD_FAIL:   ORTHOGONAL.AUROC - SINGLE_BEST.AUROC <= 0.00 OR
               ORTHOGONAL.ECE > 0.15 OR
               RANDOM_CONTROL.AUROC >= 0.60 (discriminator broken)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 4 arms * 3 seeds * 5000 queries = 60000
  EXPECTED_N_UNITS_SMOKE = 4 arms * 2 seeds * 500  queries = 4000
  Discriminator-survives-scale: smoke at N_DIM=1024 (matches v1 smoke).

HARDENING (META_RULE_X / J / L1-L4): L1 STARTED early; L2 per-arm; L3 outer try;
L4 import-crash sentinel.
Per-arm metrics: metrics["per_arm"] = {arm: {seed: {ece, auroc, ...}}}; Fix #28.

ASCII-only; no emojis; no em-dashes; self-contained.
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

ANCHOR_NAME = "meta_knowledge_partition_coverage_v2_orthogonal_signals"

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
HP_LIFT_OVER_SINGLE = 0.05
HP_LIFT_OVER_OLD = 0.05
HP_ECE_MAX = 0.10
HP_RANDOM_MAX = 0.60
MB_LIFT_OVER_SINGLE_LO = 0.02
HF_ECE_MAX = 0.15
HF_RANDOM_MIN = 0.60

EXPECTED_ARMS = ["single_best_entropy", "composed_old_correlated",
                 "composed_orthogonal", "random_control"]

if SELF_TEST_MODE:
    N_DIM = 256
    N_PARTITIONS = 16
    V_ATOMS = 200
    N_QUERIES = 100
    N_OOD = 30
    TOP_K = 5
    SEEDS = [7]
    N_CALIB = 50
    PERT_NOISE = 0.1
elif RUN_MODE == "smoke":
    N_DIM = 1024
    N_PARTITIONS = 64
    V_ATOMS = 1000
    N_QUERIES = 500
    N_OOD = 150
    TOP_K = 10
    SEEDS = [7, 17]
    N_CALIB = 200
    PERT_NOISE = 0.1
else:
    N_DIM = 2048
    N_PARTITIONS = 256
    V_ATOMS = 5000
    N_QUERIES = 5000
    N_OOD = 1000
    TOP_K = 10
    SEEDS = [7, 17, 23]
    N_CALIB = 1000
    PERT_NOISE = 0.1

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_QUERIES

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,P=%d,V=%d,Q=%d,K=%d,seeds=%s,calib=%d,pert=%.2f,"
    "mode=%s,HP_lift_single>=%.2f,HP_lift_old>=%.2f,HP_ECE<=%.2f,"
    "expected_n=%d,hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, N_PARTITIONS, V_ATOMS, N_QUERIES, TOP_K, SEEDS,
    N_CALIB, PERT_NOISE, RUN_MODE,
    HP_LIFT_OVER_SINGLE, HP_LIFT_OVER_OLD, HP_ECE_MAX, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(), "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v2_orthogonal_signals_partition_coverage",
        }
        if extra:
            m.update(extra)
        (out_dir / "metrics.json").write_text(json.dumps(m, indent=2),
                                              encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME, "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v2_orthogonal_signals_partition_coverage_import_crash",
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
    return float(-np.sum(p * np.log(p)) / math.log(len(p)))


# ----------------------- ECE / AUROC -----------------------

def ece_score(conf: np.ndarray, correct: np.ndarray, n_bins: int = 10) -> float:
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
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    n_pos = int(labels.sum())
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, len(scores) + 1, dtype=np.float64)
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


def logistic_regression_fit(X: np.ndarray, y: np.ndarray,
                             n_iters: int = 200, lr: float = 0.1) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n, d = X.shape
    # standardize features so logistic gradient is well-scaled across heterogeneous signals
    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-8
    Xs = (X - mu) / sd
    X1 = np.concatenate([Xs, np.ones((n, 1))], axis=1)
    w = np.zeros(d + 1)
    l2 = 1e-3
    for _ in range(n_iters):
        z = X1 @ w
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))
        grad = X1.T @ (p - y) / n + l2 * w
        w = w - lr * grad
    return np.concatenate([w, mu, sd])  # pack mu/sd into weights tail


def logistic_predict(X: np.ndarray, packed: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    d = X.shape[1]
    w = packed[:d + 1]
    mu = packed[d + 1: 2 * d + 1]
    sd = packed[2 * d + 1:]
    Xs = (X - mu) / (sd + 1e-8)
    X1 = np.concatenate([Xs, np.ones((Xs.shape[0], 1))], axis=1)
    z = X1 @ w
    return 1.0 / (1.0 + np.exp(-np.clip(z, -50, 50)))


# ----------------------- per-query signal extraction (V2: ORTHOGONAL) -----------------------

def extract_signals(q: np.ndarray, E: np.ndarray,
                     partition_counts: Dict[int, int],
                     top_k: int, n_part: int,
                     pert_noise: float, g: np.random.Generator) -> Dict[str, float]:
    """V2 returns BOTH old (correlated) signals AND new (orthogonal) signals.

    OLD (correlated): density, cosine_sep, entropy
    NEW (orthogonal): margin, perturbation, density (density shared)

    Margin    = top1 - top2  (pair separation; NOT a fn of full top-K distribution)
    Perturbation = cos(top1_neighbour(q + eta*noise), top1_neighbour(q))
                 measures whether identity of best match SHIFTS under input perturbation
                 (different physical info: query-locality, not codebook-shape).
    """
    qn = q / (np.linalg.norm(q) + 1e-8)
    sims = E @ qn
    pid = hash_partition(qn, n_part)
    density = float(partition_counts.get(pid, 0)) / max(1.0, float(len(E)))
    order = np.argsort(sims)[::-1]
    top_idx = order[:top_k]
    top_sims = sims[top_idx]
    rest_sims = sims[order[top_k:]] if top_k < len(sims) else np.array([0.0])
    top1 = float(top_sims[0])
    top2 = float(top_sims[1]) if len(top_sims) > 1 else float(top_sims[0])
    margin = top1 - top2
    mean_rest = float(rest_sims.mean()) if len(rest_sims) > 0 else 0.0
    std_rest = float(rest_sims.std() + 1e-8) if len(rest_sims) > 0 else 1.0
    cos_sep = (top1 - mean_rest) / std_rest
    p = softmax(top_sims, temp=0.1)
    ent = shannon_entropy(p)
    # Perturbation: small noise added to q; does top1 identity change?
    eta = g.standard_normal(q.shape[0]).astype(np.float32) * pert_noise
    qp = qn + eta
    qp = qp / (np.linalg.norm(qp) + 1e-8)
    sims_p = E @ qp
    top1_p = int(np.argmax(sims_p))
    pert_stability = 1.0 if top1_p == int(top_idx[0]) else 0.0
    # Continuous version: cosine of the top1 vector pre vs post (more graded)
    pert_cos = float(E[top1_p] @ E[int(top_idx[0])])  # 1.0 if same; lower if shifted
    return {
        "density": density, "cosine_sep": cos_sep, "entropy": ent,
        "margin": float(margin), "perturbation_cos": pert_cos,
        "perturbation_disc": pert_stability,
        "top_idx": int(top_idx[0]),
    }


# ----------------------- per-seed runner -----------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    E = bipolar(V_ATOMS, N_DIM, g)
    partition_counts: Dict[int, int] = {}
    for i in range(V_ATOMS):
        pid = hash_partition(E[i], N_PARTITIONS)
        partition_counts[pid] = partition_counts.get(pid, 0) + 1

    n_in = N_QUERIES // 2
    n_out = N_QUERIES - n_in
    queries: List[np.ndarray] = []
    truth_idx: List[int] = []
    is_in_domain: List[int] = []
    for _ in range(n_in):
        idx = int(g.integers(0, V_ATOMS))
        noise = g.standard_normal(N_DIM).astype(np.float32) * 0.3
        q = E[idx] + noise
        q = q / (np.linalg.norm(q) + 1e-8)
        queries.append(q)
        truth_idx.append(idx)
        is_in_domain.append(1)
    for _ in range(n_out):
        q = g.standard_normal(N_DIM).astype(np.float32)
        q = q / (np.linalg.norm(q) + 1e-8)
        queries.append(q)
        truth_idx.append(-1)
        is_in_domain.append(0)
    truth_idx = np.array(truth_idx)
    is_in_domain = np.array(is_in_domain)

    signals: List[Dict[str, float]] = []
    correct: List[int] = []
    for i, q in enumerate(queries):
        sig = extract_signals(q, E, partition_counts, TOP_K, N_PARTITIONS,
                              PERT_NOISE, g)
        signals.append(sig)
        if is_in_domain[i] == 1 and sig["top_idx"] == int(truth_idx[i]):
            correct.append(1)
        else:
            correct.append(0)
    correct = np.array(correct)

    density_arr = np.array([s["density"] for s in signals])
    cos_arr = np.array([s["cosine_sep"] for s in signals])
    ent_arr = np.array([s["entropy"] for s in signals])  # high entropy = uncertain
    margin_arr = np.array([s["margin"] for s in signals])
    pert_arr = np.array([s["perturbation_cos"] for s in signals])

    # Split calibration / test
    perm = g.permutation(N_QUERIES)
    calib_idx = perm[:N_CALIB]
    test_idx = perm[N_CALIB:]
    if len(test_idx) == 0:
        test_idx = calib_idx

    out: Dict[str, Dict[str, float]] = {}

    def _arm_metrics(scores: np.ndarray, name: str) -> Dict[str, float]:
        # Map scores -> [0,1] via min-max on calib then ECE on test
        au = auroc_score(scores[test_idx], correct[test_idx])
        smin = float(scores[calib_idx].min())
        smax = float(scores[calib_idx].max())
        rng = max(1e-8, smax - smin)
        conf_test = np.clip((scores[test_idx] - smin) / rng, 0.0, 1.0)
        ece = ece_score(conf_test, correct[test_idx])
        thr = float(np.quantile(scores[calib_idx], 0.5))
        refused = (scores[test_idx] <= thr).astype(np.int64)
        ood_mask = (is_in_domain[test_idx] == 0)
        ood_refuse_rate = float(refused[ood_mask].mean()) if ood_mask.sum() > 0 else 0.0
        conf_correct = float(conf_test[correct[test_idx] == 1].mean()) if (correct[test_idx] == 1).sum() > 0 else 0.0
        conf_wrong = float(conf_test[correct[test_idx] == 0].mean()) if (correct[test_idx] == 0).sum() > 0 else 0.0
        conf_std = float(conf_test.std() + 1e-8)
        conf_sep_std = (conf_correct - conf_wrong) / conf_std
        return {
            "ece": float(ece), "auroc": float(au),
            "conf_correct": conf_correct, "conf_wrong": conf_wrong,
            "conf_sep_std": float(conf_sep_std),
            "ood_refuse_rate": ood_refuse_rate,
            "n_test": int(len(test_idx)),
        }

    # ARM 1: SINGLE_BEST_ENTROPY -- v1 reference (entropy alone, sign-flipped so high = confident)
    out["single_best_entropy"] = _arm_metrics(-ent_arr, "single_best_entropy")

    # ARM 2: COMPOSED_OLD (correlated trio from v1)
    X_calib_old = np.stack([density_arr[calib_idx], cos_arr[calib_idx], -ent_arr[calib_idx]], axis=1)
    y_calib = correct[calib_idx]
    packed_old = logistic_regression_fit(X_calib_old, y_calib)
    X_test_old = np.stack([density_arr[test_idx], cos_arr[test_idx], -ent_arr[test_idx]], axis=1)
    p_test_old = logistic_predict(X_test_old, packed_old)
    # Build a full-length score array so _arm_metrics indexing works
    full_old = np.zeros(N_QUERIES)
    # We need to express via signals/indexing; refit a function that returns full-length:
    X_full_old = np.stack([density_arr, cos_arr, -ent_arr], axis=1)
    p_full_old = logistic_predict(X_full_old, packed_old)
    out["composed_old_correlated"] = _arm_metrics(p_full_old, "composed_old_correlated")

    # ARM 3: COMPOSED_ORTHOGONAL (margin + perturbation + density)
    X_calib_orth = np.stack([margin_arr[calib_idx], pert_arr[calib_idx],
                              density_arr[calib_idx]], axis=1)
    packed_orth = logistic_regression_fit(X_calib_orth, y_calib)
    X_full_orth = np.stack([margin_arr, pert_arr, density_arr], axis=1)
    p_full_orth = logistic_predict(X_full_orth, packed_orth)
    out["composed_orthogonal"] = _arm_metrics(p_full_orth, "composed_orthogonal")

    # ARM 4: RANDOM_CONTROL
    rand_full = g.random(N_QUERIES)
    out["random_control"] = _arm_metrics(rand_full, "random_control")

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": out,
        "n_queries": N_QUERIES,
        "n_partitions": N_PARTITIONS,
        "_signal_correlation_diag": {
            "corr_cos_ent": float(np.corrcoef(cos_arr, -ent_arr)[0, 1]),
            "corr_cos_margin": float(np.corrcoef(cos_arr, margin_arr)[0, 1]),
            "corr_margin_pert": float(np.corrcoef(margin_arr, pert_arr)[0, 1]),
            "corr_margin_density": float(np.corrcoef(margin_arr, density_arr)[0, 1]),
        },
    }


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials found",
                "summary": "no per-seed partials found",
                "per_arm": {}}
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {arm: {} for arm in EXPECTED_ARMS}
    for arm in EXPECTED_ARMS:
        eces, aurocs, cs_seps, ood_rates = [], [], [], []
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
            summary[arm] = {"ece_mean": 0.0, "auroc_mean": 0.0, "auroc_std": 0.0,
                            "auroc_cv": 0.0, "conf_sep_std_mean": 0.0,
                            "ood_refuse_rate_mean": 0.0, "n": 0}

    sb = summary.get("single_best_entropy", {})
    od = summary.get("composed_old_correlated", {})
    orth = summary.get("composed_orthogonal", {})
    rc = summary.get("random_control", {})

    orth_auroc = orth.get("auroc_mean", 0.0)
    sb_auroc = sb.get("auroc_mean", 0.0)
    od_auroc = od.get("auroc_mean", 0.0)
    orth_ece = orth.get("ece_mean", 1.0)
    rc_auroc = rc.get("auroc_mean", 0.5)

    lift_over_single = orth_auroc - sb_auroc
    lift_over_old = orth_auroc - od_auroc

    verdict = "MIDDLE_BAND"
    if rc_auroc >= HF_RANDOM_MIN or orth_ece > HF_ECE_MAX:
        verdict = "HARD_FAIL"
    elif lift_over_single <= 0.0:
        verdict = "HARD_FAIL"
    elif (lift_over_single >= HP_LIFT_OVER_SINGLE and
            lift_over_old >= HP_LIFT_OVER_OLD and
            orth_ece <= HP_ECE_MAX and
            rc_auroc < HP_RANDOM_MAX):
        verdict = "HARD_PASS"
    elif lift_over_single < MB_LIFT_OVER_SINGLE_LO:
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | ORTH auroc=%.3f ece=%.3f | SINGLE auroc=%.3f | OLD auroc=%.3f | "
        "RANDOM auroc=%.3f | lift_single=%.3f lift_old=%.3f"
    ) % (verdict, orth_auroc, orth_ece, sb_auroc, od_auroc, rc_auroc,
         lift_over_single, lift_over_old)

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "per_arm": per_arm_full, "per_arm_summary": summary,
        "lift_over_single": float(lift_over_single),
        "lift_over_old_correlated": float(lift_over_old),
        "n_seeds_complete": len(per_seed),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(per_seed) * len(EXPECTED_ARMS) * N_QUERIES,
        "cardinality_ok": (len(per_seed) >= 2),
    }


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
                                          "orth_auroc_selftest": r["per_arm"]["composed_orthogonal"]["auroc"],
                                          "single_auroc_selftest": r["per_arm"]["single_best_entropy"]["auroc"]})
            print("[selftest] OK; orth_auroc=%.3f single_auroc=%.3f" % (
                r["per_arm"]["composed_orthogonal"]["auroc"],
                r["per_arm"]["single_best_entropy"]["auroc"]), flush=True)
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
                               extra={"_phase": "seed_running", "_current_seed": seed})
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
    final["_hardening_marker"] = "v2_orthogonal_signals_partition_coverage"
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
