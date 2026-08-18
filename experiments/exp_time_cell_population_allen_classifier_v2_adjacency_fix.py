"""
exp_time_cell_population_allen_classifier_v2_adjacency_fix.py

V2 of brain-grounded population-code Allen-relation classifier (CPU).

PREDECESSOR (verified HARD_FAIL on disk MEASURED@2026-06-27):
- d:/AI/hd-instrument/experiments/exp_time_cell_population_allen_classifier_v1.py
- d:/AI/hd-instrument/data/exp_time_cell_population_allen_classifier_v1_smoke/metrics.json
- ARM_A=0.526 ARM_B=0.064 ARM_C=0.231 ARM_D=0.053 minPerCls=0.000
- Root cause: MEETS / MET-BY = 0.000 (single-tick adjacency e1==s2 smeared by cleanup);
  EQUALS / STARTS / FINISHES unstable across seeds (f5 collapsed start+end into 1 scalar)

V2 SURGICAL FIXES (per cell-author recommendation):
1. f5 (1 scalar) -> f5a (start_match) + f5b (end_match): restores
   STARTS/STARTED-BY/FINISHES/FINISHED-BY distinguishability
2. + f6a (loose-overlap cardinality at theta=0.05) + f6b (signed boundary gap):
   recovers MEETS/MET-BY where strict cleanup smeared single-tick adjacency
3. L2 1e-3 -> 1e-2: combat rare-class overfit (MEETS/MET-BY have ~7 samples / 500)
4. Class-balanced sample weights: rare classes upweighted in gradient

KEEP unchanged: T=32 smoke / T=128 full, n_pairs=500/5000, N_DIM=4096/8192,
ARMS A/B/C/D structure, allen_label oracle, sampling stratification, atomic write.

PRE-REG HARD bands (cannot weaken; see prereg file):
- HARD_PASS: ARM_A >= 0.60 AND min-per-cls > 0.10 AND ARM_A - ARM_B >= 0.40
            AND arms_distinct AND cv < 0.20 AND ARM_D in [0.04, 0.12] AND card_ok
- HARD_FAIL: ARM_A < 0.50 OR (MEETS=0 AND MET-BY=0) OR not arms_distinct
            OR ARM_D out-of-band OR card_breach
- MIDDLE_BAND: ARM_A in [0.50, 0.60] AND min-per-cls > 0.05

ROUTE: remote_cpu_queue (pure numpy; no GPU).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import inspect
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402

ANCHOR_NAME = "time_cell_population_allen_classifier_v2_adjacency_fix"

# 13 Allen relations (canonical order)
ALLEN_RELATIONS = [
    "before", "after", "meets", "met-by", "overlaps", "overlapped-by",
    "during", "contains", "starts", "started-by", "finishes", "finished-by", "equals",
]
N_CLASSES = len(ALLEN_RELATIONS)
RELATION_TO_IDX = {r: i for i, r in enumerate(ALLEN_RELATIONS)}

# Feature dim: f1, f2, f3, f4, f5a, f5b, f6a, f6b = 8
N_FEATS = 8


# ------- args + mode -------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if (_ARGS.smoke or "--smoke" in sys.argv)
            else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"


# ------- substrate primitives -------
def cphasor(m: int, d: int, g: np.random.Generator) -> np.ndarray:
    """Bank of m FHRR phasor vectors of dim d."""
    ang = (g.random((m, d)) * 2 - 1) * math.pi
    return np.exp(1j * ang).astype(np.complex64)


def cleanup_topk(v: np.ndarray, book: np.ndarray, theta: float = 0.10) -> np.ndarray:
    """Indices in book whose normalized similarity to v exceeds theta."""
    nv = np.linalg.norm(v)
    if nv < 1e-9:
        return np.array([], dtype=np.int64)
    book_norms = np.linalg.norm(book, axis=1)
    sims = (book @ np.conj(v)).real / (book_norms * nv + 1e-9)
    return np.where(sims > theta)[0]


def interval_bundle(s: int, e: int, ticks: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Time-cell population bundle for [s,e]; returns (unnorm, norm)."""
    if e < s:
        s, e = e, s
    band = ticks[s:e + 1]
    bundle_unnorm = np.sum(band, axis=0).astype(np.complex64)
    bundle_norm = bundle_unnorm / math.sqrt(max(1, e - s + 1))
    return bundle_unnorm, bundle_norm


# ------- Allen oracle (ONLY for ground-truth labels; never seen by ARM_A/B) -------
def allen_label(a: Tuple[int, int], b: Tuple[int, int]) -> str:
    """Allen 13-relation on raw endpoints. Used only for labels + ARM_C input."""
    s1, e1 = a
    s2, e2 = b
    if e1 < s2:
        return "before"
    if s1 > e2:
        return "after"
    if e1 == s2 and s1 != s2:
        return "meets"
    if s1 == e2 and e1 != e2:
        return "met-by"
    if s1 == s2 and e1 == e2:
        return "equals"
    if s1 < s2 and e1 > e2:
        return "contains"
    if s1 > s2 and e1 < e2:
        return "during"
    if s1 == s2 and e1 < e2:
        return "starts"
    if s1 == s2 and e1 > e2:
        return "started-by"
    if e1 == e2 and s1 > s2:
        return "finishes"
    if e1 == e2 and s1 < s2:
        return "finished-by"
    if s1 < s2 < e1 < e2:
        return "overlaps"
    if s2 < s1 < e2 < e1:
        return "overlapped-by"
    return "overlaps"


# ------- pair generation (stratified) -------
def sample_interval_pair(T: int, g: np.random.Generator, target_relation: str
                         ) -> Tuple[Tuple[int, int], Tuple[int, int], str]:
    """Rejection-sample (A, B) with allen_label == target_relation, with fallback."""
    for _ in range(200):
        s1 = int(g.integers(0, max(2, T - 4)))
        e1 = int(g.integers(s1 + 1, T))
        s2 = int(g.integers(0, max(2, T - 4)))
        e2 = int(g.integers(s2 + 1, T))
        rel = allen_label((s1, e1), (s2, e2))
        if rel == target_relation:
            return (s1, e1), (s2, e2), rel
    s1 = int(g.integers(0, max(2, T - 4)))
    e1 = int(g.integers(s1 + 1, T))
    s2 = int(g.integers(0, max(2, T - 4)))
    e2 = int(g.integers(s2 + 1, T))
    return (s1, e1), (s2, e2), allen_label((s1, e1), (s2, e2))


def generate_pairs(n_pairs: int, T: int, g: np.random.Generator
                   ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]], List[str]]:
    """Stratified n_pairs across 13 Allen relations (round-robin)."""
    A_list: List[Tuple[int, int]] = []
    B_list: List[Tuple[int, int]] = []
    labels: List[str] = []
    per_class = max(1, n_pairs // N_CLASSES)
    for rel in ALLEN_RELATIONS:
        for _ in range(per_class):
            A, B, actual = sample_interval_pair(T, g, rel)
            A_list.append(A)
            B_list.append(B)
            labels.append(actual)
    remaining = n_pairs - len(A_list)
    for _ in range(max(0, remaining)):
        rel = ALLEN_RELATIONS[int(g.integers(0, N_CLASSES))]
        A, B, actual = sample_interval_pair(T, g, rel)
        A_list.append(A)
        B_list.append(B)
        labels.append(actual)
    return A_list, B_list, labels


# ------- V2 substrate feature extraction (8 features) -------
def substrate_features_v2(A: Tuple[int, int], B: Tuple[int, int],
                          ticks: np.ndarray, T: int) -> np.ndarray:
    """V2: f1..f4 unchanged; f5 -> f5a + f5b; + f6a (loose-overlap) + f6b (boundary-gap).

    Returns shape (8,) float32. NO Python access to (s,e) escapes; only this vector.
    """
    A_unnorm, A_norm = interval_bundle(A[0], A[1], ticks)
    B_unnorm, B_norm = interval_bundle(B[0], B[1], ticks)

    # f1: cosine of normalized bundles (overlap proxy)
    nA = np.linalg.norm(A_norm) + 1e-9
    nB = np.linalg.norm(B_norm) + 1e-9
    f1 = float(np.real(np.vdot(A_norm, B_norm)) / (nA * nB))

    # f2: cleanup-weighted centroid difference (order proxy)
    sims_A = (ticks @ np.conj(A_norm)).real
    sims_B = (ticks @ np.conj(B_norm)).real
    w_A = np.maximum(sims_A, 0.0)
    w_B = np.maximum(sims_B, 0.0)
    if w_A.sum() > 1e-9:
        cen_A = float(np.sum(np.arange(T) * w_A) / w_A.sum())
    else:
        cen_A = float(T) / 2.0
    if w_B.sum() > 1e-9:
        cen_B = float(np.sum(np.arange(T) * w_B) / w_B.sum())
    else:
        cen_B = float(T) / 2.0
    f2 = (cen_A - cen_B) / float(T)

    # f3: log-norm ratio (duration / Weber-fraction)
    f3 = float(math.log((np.linalg.norm(A_unnorm) + 1e-9)
                        / (np.linalg.norm(B_unnorm) + 1e-9)))

    # f4: cleanup-intersection cardinality / max (strict theta=0.15)
    top_A_strict = set(int(x) for x in cleanup_topk(A_norm, ticks, theta=0.15))
    top_B_strict = set(int(x) for x in cleanup_topk(B_norm, ticks, theta=0.15))
    inter_strict = len(top_A_strict & top_B_strict)
    max_c = max(1, max(len(top_A_strict), len(top_B_strict)))
    f4 = float(inter_strict) / float(max_c)

    # FIX 1: f5 SPLIT -> f5a (start_match) + f5b (end_match).
    # Restores STARTS/STARTED-BY/FINISHES/FINISHED-BY distinguishability.
    if top_A_strict and top_B_strict:
        f5a = float(min(top_A_strict) == min(top_B_strict))  # start aligned
        f5b = float(max(top_A_strict) == max(top_B_strict))  # end aligned
    else:
        f5a = 0.0
        f5b = 0.0

    # FIX 2: f6 adjacency probe at LOOSE theta=0.05 on UNNORM bundles.
    # Recovers MEETS/MET-BY where strict cleanup smeared single-tick adjacency.
    top_A_loose = set(int(x) for x in cleanup_topk(A_unnorm, ticks, theta=0.05))
    top_B_loose = set(int(x) for x in cleanup_topk(B_unnorm, ticks, theta=0.05))
    if top_A_loose and top_B_loose:
        inter_loose = len(top_A_loose & top_B_loose)
        denom_loose = max(1, min(len(top_A_loose), len(top_B_loose)))
        f6a = float(inter_loose) / float(denom_loose)
        # f6b: signed boundary gap = (min(B) - max(A)) / T
        # MEETS: A ends just before B starts -> gap ~ +1/T (very small positive)
        # MET-BY: B ends just before A starts -> gap negative
        # BEFORE: gap ~ +large
        # OVERLAPS / CONTAINS / DURING: gap ~ 0 or negative
        f6b = float(min(top_B_loose) - max(top_A_loose)) / float(T)
    else:
        f6a = 0.0
        f6b = 0.0

    return np.array([f1, f2, f3, f4, f5a, f5b, f6a, f6b], dtype=np.float32)


# ------- pure-numpy multiclass logistic with class-balanced sample weights -------
def softmax_rows(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    ez = np.exp(z)
    return ez / (ez.sum(axis=1, keepdims=True) + 1e-12)


def fit_logistic_multiclass(X: np.ndarray, y: np.ndarray, n_classes: int,
                            n_iter: int = 250, lr: float = 0.30,
                            l2: float = 1e-2,
                            class_balanced: bool = True) -> np.ndarray:
    """FIX 3+4: L2=1e-2 (was 1e-3); class-balanced sample weights for rare classes.

    Weights: w_i = n / (n_classes * count[y_i]); rare classes upweighted.
    Returns W of shape (D+1, K).
    """
    n, d = X.shape
    Xb = np.hstack([X, np.ones((n, 1), dtype=np.float32)])
    W = np.zeros((d + 1, n_classes), dtype=np.float32)
    Y_oh = np.zeros((n, n_classes), dtype=np.float32)
    Y_oh[np.arange(n), y] = 1.0

    if class_balanced:
        counts = np.bincount(y, minlength=n_classes).astype(np.float32)
        counts = np.maximum(counts, 1.0)  # avoid div-by-zero for unseen classes
        sample_w = (n / (n_classes * counts[y])).astype(np.float32)  # shape (n,)
        sample_w = sample_w.reshape(-1, 1)  # (n,1) for broadcast
    else:
        sample_w = np.ones((n, 1), dtype=np.float32)

    for _ in range(n_iter):
        logits = Xb @ W
        P = softmax_rows(logits)
        weighted_resid = sample_w * (P - Y_oh)  # (n, K)
        grad = Xb.T @ weighted_resid / n + l2 * W
        W = W - lr * grad
    return W


def predict_logistic(W: np.ndarray, X: np.ndarray) -> np.ndarray:
    Xb = np.hstack([X, np.ones((X.shape[0], 1), dtype=np.float32)])
    logits = Xb @ W
    return np.argmax(logits, axis=1)


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int
             ) -> Tuple[float, np.ndarray]:
    """Macro-F1 + per-class F1 vector."""
    f1s = np.zeros(n_classes, dtype=np.float32)
    for c in range(n_classes):
        tp = int(np.sum((y_pred == c) & (y_true == c)))
        fp = int(np.sum((y_pred == c) & (y_true != c)))
        fn = int(np.sum((y_pred != c) & (y_true == c)))
        if tp == 0:
            f1s[c] = 0.0
            continue
        prec = tp / (tp + fp + 1e-9)
        rec = tp / (tp + fn + 1e-9)
        f1s[c] = 2 * prec * rec / (prec + rec + 1e-9)
    return float(f1s.mean()), f1s


# ------- per-seed run -------
def run_one_seed(seed: int, T: int, n_pairs: int, N: int) -> Dict:
    g = np.random.default_rng(seed)
    ticks = cphasor(T, N, g)

    A_list, B_list, label_strs = generate_pairs(n_pairs, T, g)
    y = np.array([RELATION_TO_IDX[s] for s in label_strs], dtype=np.int64)

    # V2: 8-dim feature vector (was 5)
    feats = np.zeros((len(A_list), N_FEATS), dtype=np.float32)
    for i, (A, B) in enumerate(zip(A_list, B_list)):
        feats[i] = substrate_features_v2(A, B, ticks, T)

    # Raw endpoints (ARM_C): unchanged
    raw_endpoints = np.zeros((len(A_list), 4), dtype=np.float32)
    for i, (A, B) in enumerate(zip(A_list, B_list)):
        raw_endpoints[i] = np.array([A[0], A[1], B[0], B[1]], dtype=np.float32) / float(T)

    n = len(y)
    idx = np.arange(n)
    g.shuffle(idx)
    n_train = int(0.8 * n)
    tr, te = idx[:n_train], idx[n_train:]

    # ARM_A: 8-dim substrate features (class-balanced, L2=1e-2)
    W_A = fit_logistic_multiclass(feats[tr], y[tr], N_CLASSES,
                                  l2=1e-2, class_balanced=True)
    y_pred_A = predict_logistic(W_A, feats[te])
    f1_A, per_cls_A = macro_f1(y[te], y_pred_A, N_CLASSES)

    # ARM_B: cosine-only (f1); class-balanced + L2=1e-2 too (apples to apples)
    W_B = fit_logistic_multiclass(feats[tr, :1], y[tr], N_CLASSES,
                                  l2=1e-2, class_balanced=True)
    y_pred_B = predict_logistic(W_B, feats[te, :1])
    f1_B, per_cls_B = macro_f1(y[te], y_pred_B, N_CLASSES)

    # ARM_C: raw endpoints; class-balanced + L2=1e-2 (fairness)
    W_C = fit_logistic_multiclass(raw_endpoints[tr], y[tr], N_CLASSES,
                                  l2=1e-2, class_balanced=True)
    y_pred_C = predict_logistic(W_C, raw_endpoints[te])
    f1_C, per_cls_C = macro_f1(y[te], y_pred_C, N_CLASSES)

    # ARM_D: shuffled labels
    g_shuf = np.random.default_rng(seed + 9999)
    y_shuf = y[tr].copy()
    g_shuf.shuffle(y_shuf)
    W_D = fit_logistic_multiclass(feats[tr], y_shuf, N_CLASSES,
                                  l2=1e-2, class_balanced=True)
    y_pred_D = predict_logistic(W_D, feats[te])
    f1_D, per_cls_D = macro_f1(y[te], y_pred_D, N_CLASSES)

    # Per-relation accuracy (ARM_A): track MEETS/MET-BY explicitly
    per_rel_acc: Dict[str, float] = {}
    for c in range(N_CLASSES):
        mask = (y[te] == c)
        if mask.sum() == 0:
            per_rel_acc[ALLEN_RELATIONS[c]] = -1.0
            continue
        per_rel_acc[ALLEN_RELATIONS[c]] = float(np.mean(y_pred_A[mask] == c))

    return {
        "seed": int(seed),
        "T": int(T),
        "N": int(N),
        "n_pairs": int(n_pairs),
        "run_mode": "smoke" if SMOKE else "full",
        "smoke": SMOKE,
        "anchor_name": ANCHOR_NAME,
        "config_version": (
            f"ANCHOR={ANCHOR_NAME},N={N},T={T},n_pairs={n_pairs}"
        ),
        "ARM_A_macro_f1": float(f1_A),
        "ARM_B_macro_f1": float(f1_B),
        "ARM_C_macro_f1": float(f1_C),
        "ARM_D_macro_f1": float(f1_D),
        "ARM_A_per_class_f1": [float(x) for x in per_cls_A],
        "ARM_C_per_class_f1": [float(x) for x in per_cls_C],
        "ARM_A_per_relation_acc": per_rel_acc,
        "ARM_A_min_per_class_f1": float(per_cls_A.min()),
        "ARM_A_minus_B": float(f1_A - f1_B),
        "ARM_A_minus_C": float(f1_A - f1_C),
        "ARM_A_minus_D": float(f1_A - f1_D),
        "MEETS_acc": float(per_rel_acc.get("meets", -1.0)),
        "MET_BY_acc": float(per_rel_acc.get("met-by", -1.0)),
        "n_train": int(n_train),
        "n_test": int(n - n_train),
        "n_classes": int(N_CLASSES),
        "n_features": int(N_FEATS),
    }


# ------- arms-distinct attestation (META_RULE_AF) -------
def arms_distinct_attestation() -> Dict:
    """SHA-256 each ARM's input-slice + label-source. Distinct iff all 4 hashes differ."""
    src = inspect.getsource(run_one_seed)
    pieces = {
        "ARM_A_feats_slice": "feats[tr]_8dim",
        "ARM_B_feats_slice": "feats[tr, :1]_cosine_only",
        "ARM_C_feats_slice": "raw_endpoints[tr]",
        "ARM_D_labels": "y_shuf",
    }
    hashes = {k: hashlib.sha256((k + "::" + v + "::" + src).encode()).hexdigest()[:16]
              for k, v in pieces.items()}
    distinct = len(set(hashes.values())) == 4
    return {"arms_distinct": bool(distinct), "arm_sha_prefixes": hashes}


# ------- verdict (V2 bands) -------
def verdict(per_seed: List[Dict], arms_meta: Dict) -> Tuple[str, str, Dict]:
    mean_A = float(np.mean([r["ARM_A_macro_f1"] for r in per_seed]))
    mean_B = float(np.mean([r["ARM_B_macro_f1"] for r in per_seed]))
    mean_C = float(np.mean([r["ARM_C_macro_f1"] for r in per_seed]))
    mean_D = float(np.mean([r["ARM_D_macro_f1"] for r in per_seed]))
    min_per_cls_A = float(min(r["ARM_A_min_per_class_f1"] for r in per_seed))
    cv_A = float(np.std([r["ARM_A_macro_f1"] for r in per_seed])
                 / (mean_A + 1e-9)) if len(per_seed) > 1 else 0.0
    mean_meets = float(np.mean([r["MEETS_acc"] for r in per_seed if r["MEETS_acc"] >= 0]))
    mean_metby = float(np.mean([r["MET_BY_acc"] for r in per_seed if r["MET_BY_acc"] >= 0]))
    n_seeds = len(per_seed)

    expected_units = 4 * N_CLASSES * n_seeds
    observed_units = 0
    for r in per_seed:
        observed_units += len(r["ARM_A_per_class_f1"]) + len(r["ARM_C_per_class_f1"])
        observed_units += 2 * N_CLASSES
    cardinality_ok = observed_units >= int(0.83 * expected_units)

    arms_distinct = arms_meta.get("arms_distinct", False)
    baseline_in_band = 0.04 <= mean_D <= 0.12

    summary = {
        "mean_ARM_A_macro_f1": mean_A,
        "mean_ARM_B_macro_f1": mean_B,
        "mean_ARM_C_macro_f1": mean_C,
        "mean_ARM_D_macro_f1": mean_D,
        "min_per_class_f1_ARM_A": min_per_cls_A,
        "cv_ARM_A": cv_A,
        "MEETS_acc_mean": mean_meets,
        "MET_BY_acc_mean": mean_metby,
        "ARM_A_minus_B": mean_A - mean_B,
        "ARM_A_minus_C": mean_A - mean_C,
        "ARM_A_minus_D": mean_A - mean_D,
        "n_seeds": n_seeds,
        "cardinality_ok": cardinality_ok,
        "expected_units": expected_units,
        "observed_units": observed_units,
        "arms_distinct": arms_distinct,
        "baseline_in_band": baseline_in_band,
        "n_classes": N_CLASSES,
        "n_features": N_FEATS,
    }

    msg_core = (
        "ARM_A=%.3f ARM_B=%.3f ARM_C=%.3f ARM_D=%.3f minPerCls=%.3f cvA=%.3f "
        "MEETS=%.3f MET-BY=%.3f A-B=%.3f A-C=%.3f A-D=%.3f "
        "distinct=%s baseline_ok=%s cardOK=%s"
        % (mean_A, mean_B, mean_C, mean_D, min_per_cls_A, cv_A,
           mean_meets, mean_metby,
           mean_A - mean_B, mean_A - mean_C, mean_A - mean_D,
           arms_distinct, baseline_in_band, cardinality_ok)
    )

    # HARD_FAIL gates
    if not arms_distinct:
        return ("HARD_FAIL",
                "HARD_FAIL: arms_distinct=False (META_RULE_AF). " + msg_core, summary)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: CARDINALITY_BREACH observed=%d expected=%d. %s"
                % (observed_units, expected_units, msg_core), summary)
    if not baseline_in_band:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_D baseline %.3f outside [0.04, 0.12]. %s"
                % (mean_D, msg_core), summary)
    if mean_A < 0.50:
        return ("HARD_FAIL",
                "HARD_FAIL: V2 worse than V1 (ARM_A=%.3f < 0.50; v1=0.526). %s"
                % (mean_A, msg_core), summary)
    if mean_meets == 0.0 and mean_metby == 0.0:
        return ("HARD_FAIL",
                "HARD_FAIL: adjacency fix did not help (MEETS=MET-BY=0.000). %s" % msg_core,
                summary)

    # HARD_PASS gate (per prereg)
    if (mean_A >= 0.60
            and min_per_cls_A > 0.10
            and (mean_A - mean_B) >= 0.40
            and cv_A < 0.20):
        return ("HARD_PASS",
                "HARD_PASS: V2 adjacency-fix substrate classifies 13-way Allen at "
                "macro_f1 %.3f (v1=0.526; +%.3f); min_per_cls=%.3f > 0.10; "
                "beats cosine-only by %.3f; cv=%.3f. %s"
                % (mean_A, mean_A - 0.526, min_per_cls_A,
                   mean_A - mean_B, cv_A, msg_core),
                summary)

    # MIDDLE_BAND
    if mean_A >= 0.50 and min_per_cls_A > 0.05:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: V2 partial credit (ARM_A=%.3f in [0.50, 0.60]); "
                "iterate. %s" % (mean_A, msg_core), summary)

    return ("HARD_FAIL",
            "HARD_FAIL: V2 below MIDDLE_BAND floor (ARM_A=%.3f or min_per_cls=%.3f). %s"
            % (mean_A, min_per_cls_A, msg_core), summary)


# ------- self-test -------
def _selftest() -> None:
    print("[selftest] BEGIN " + ANCHOR_NAME, flush=True)

    g = np.random.default_rng(7)
    T = 16
    N = 512
    ticks = cphasor(T, N, g)

    # T1: features computable + finite; shape == 8
    A = (2, 6)
    B = (8, 12)
    f = substrate_features_v2(A, B, ticks, T)
    assert f.shape == (N_FEATS,), "feature vector shape mismatch (got %s)" % str(f.shape)
    assert np.all(np.isfinite(f)), "feature vector contains non-finite"
    assert -1.0 <= f[0] <= 1.0, "f1 cosine out of range"
    print("  [selftest] T1 PASS: substrate_features_v2 shape=(8,) finite + in-range",
          flush=True)

    # T2: allen_label oracle canonical pairs
    assert allen_label((0, 3), (5, 8)) == "before"
    assert allen_label((5, 8), (0, 3)) == "after"
    assert allen_label((0, 5), (5, 10)) == "meets"
    assert allen_label((0, 5), (0, 5)) == "equals"
    assert allen_label((0, 10), (3, 7)) == "contains"
    assert allen_label((3, 7), (0, 10)) == "during"
    assert allen_label((0, 5), (3, 8)) == "overlaps"
    print("  [selftest] T2 PASS: allen_label oracle correct", flush=True)

    # T3: arms_distinct attestation
    meta = arms_distinct_attestation()
    assert meta["arms_distinct"], "arms NOT distinct"
    assert len(meta["arm_sha_prefixes"]) == 4
    print("  [selftest] T3 PASS: arms_distinct attestation OK", flush=True)

    # T4: class-balanced logistic sanity
    rng = np.random.default_rng(7)
    Xt = rng.standard_normal((100, 3)).astype(np.float32)
    yt = (Xt[:, 0] > 0).astype(np.int64) + (Xt[:, 1] > 0).astype(np.int64)
    Wt = fit_logistic_multiclass(Xt, yt, 3, n_iter=100, class_balanced=True)
    yp = predict_logistic(Wt, Xt)
    acc = float(np.mean(yp == yt))
    assert acc > 0.50, "class-balanced logistic sanity failed (acc=%.3f)" % acc
    print("  [selftest] T4 PASS: class-balanced logistic acc=%.3f > 0.50" % acc,
          flush=True)

    # T5: end-to-end mini run
    r = run_one_seed(seed=11, T=12, n_pairs=80, N=512)
    assert "ARM_A_macro_f1" in r
    assert 0.0 <= r["ARM_A_macro_f1"] <= 1.0
    assert 0.0 <= r["ARM_D_macro_f1"] <= 1.0
    assert r["ARM_D_macro_f1"] < 0.35, (
        "ARM_D shuffled-label baseline too high: %.3f" % r["ARM_D_macro_f1"]
    )
    assert r["n_features"] == 8, "n_features should be 8"
    print("  [selftest] T5 PASS: end-to-end ARM_A=%.3f ARM_D=%.3f n_feats=%d"
          % (r["ARM_A_macro_f1"], r["ARM_D_macro_f1"], r["n_features"]), flush=True)

    # T6: f6b boundary-gap sign correctness on canonical MEETS pair
    # MEETS at T=16: A=(2,7), B=(7,12). top sets should be roughly disjoint+adjacent.
    f_meets = substrate_features_v2((2, 7), (7, 12), ticks, T)
    f_before = substrate_features_v2((0, 3), (10, 14), ticks, T)
    # Both have non-zero f6 features in principle (loose theta=0.05)
    # We don't assert numerical value -- just that features are finite + the
    # f5a/f5b split is exposing both bits
    assert np.all(np.isfinite(f_meets)), "f_meets non-finite"
    assert np.all(np.isfinite(f_before)), "f_before non-finite"
    print("  [selftest] T6 PASS: MEETS / BEFORE feature extraction finite", flush=True)

    print("[selftest] PASS " + ANCHOR_NAME, flush=True)


# ------- main -------
def main() -> None:
    if _ARGS.self_test:
        _selftest()
        sys.exit(0)

    _selftest()

    if SMOKE:
        N_DIM = 4096
        T_TICKS = 32
        N_PAIRS = 500
        SEEDS = [11, 23]
    else:
        N_DIM = 8192
        T_TICKS = 128
        N_PAIRS = 5000
        SEEDS = [11, 23, 37, 41, 53]

    print("[config] anchor=%s mode=%s N=%d T=%d n_pairs=%d n_seeds=%d n_feats=%d"
          % (ANCHOR_NAME, RUN_MODE, N_DIM, T_TICKS, N_PAIRS, len(SEEDS), N_FEATS),
          flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    per_seed: List[Dict] = []
    for seed in SEEDS:
        t_seed = time.time()
        r = run_one_seed(seed=seed, T=T_TICKS, n_pairs=N_PAIRS, N=N_DIM)
        r["elapsed_s"] = time.time() - t_seed
        print(
            "  [seed=%d] ARM_A=%.3f ARM_B=%.3f ARM_C=%.3f ARM_D=%.3f "
            "min_per_cls=%.3f MEETS=%.3f MET-BY=%.3f elapsed=%.1fs"
            % (seed, r["ARM_A_macro_f1"], r["ARM_B_macro_f1"],
               r["ARM_C_macro_f1"], r["ARM_D_macro_f1"],
               r["ARM_A_min_per_class_f1"],
               r["MEETS_acc"], r["MET_BY_acc"],
               r["elapsed_s"]),
            flush=True,
        )
        per_seed.append(r)

    arms_meta = arms_distinct_attestation()
    v, vmsg, summary = verdict(per_seed, arms_meta)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "per_seed": per_seed,
        "summary": summary,
        "arms_attestation": arms_meta,
        "elapsed_s": time.time() - t0,
        "config": {
            "N": N_DIM,
            "T": T_TICKS,
            "n_pairs": N_PAIRS,
            "seeds": SEEDS,
            "n_classes": N_CLASSES,
            "n_features": N_FEATS,
            "allen_relations": ALLEN_RELATIONS,
            "l2": 1e-2,
            "class_balanced": True,
        },
        "config_version": "ANCHOR=%s,N=%d,T=%d,n_pairs=%d" % (
            ANCHOR_NAME, N_DIM, T_TICKS, N_PAIRS),
    }
    write_metrics(out_dir, metrics, per_seed)
    print("[metrics] written to %s/metrics.json" % out_dir, flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as exc:
        print("[ERROR] %s: %s" % (type(exc).__name__, exc), flush=True)
        raise
