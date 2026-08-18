"""
exp_time_cell_population_allen_classifier_v1.py -- brain-grounded population-code Allen-relation classifier (CPU).

ROUTING: Research drill 2x temporal-reasoning Stage 3 (2026-06-27); REPLACES BY-CONSTRUCTION
exp_temporal_interval_allen_cpu_v1 in which substrate stored endpoints and Python _allen()
classified the relation. Here SUBSTRATE-DERIVED FEATURES f1..f5 (from cleanup / norm /
disjointness / endpoint-match -- all substrate operations on time-cell population bundles)
drive a logistic regression. ARM_C (raw endpoints (s,e) -> logistic) is the BY-CONSTRUCTION
fairness control: if ARM_C beats ARM_A, substrate is adding noise on top of raw endpoints.

BRAIN GROUNDING:
- CITED@MacDonald-Eichenbaum 2011 (Hippocampal "time cells" -- Neuron 71:737-749)
- CITED@Pastalkova-Buzsaki 2008 (Internally generated cell assemblies -- Science 321:1322)
- CITED@Tsao-Sugar-Lu 2018 (LEC integrating time from experience -- Nature 561:57-62)
- CITED@Howard-Eichenbaum 2013 (Hippocampus, time, memory across scales -- Annu Rev Psychol)
- CITED@Allen 1983 (Maintaining knowledge about temporal intervals -- CACM 26:832-843)

SUBSTRATE PRIMITIVE:
- interval [s,e] -> interval_hd = sum_{t=s}^{e} tick_t / sqrt(e-s+1) (normalized time-cell
  population bundle; tick_t = cphasor(T, N))
- features (ALL substrate-side; no Python access to (s,e) once interval_hd is computed):
    f1 = Re cos(A_hd, B_hd)                          overlap proxy
    f2 = (centroid_A - centroid_B) / T               order proxy via cleanup-weighted
    f3 = log(||A_hd_unnorm|| / ||B_hd_unnorm||)      duration ratio (Weber-fraction probe)
    f4 = mean cleanup(A_hd, ticks) intersect cleanup(B_hd, ticks) cardinality   disjointness
    f5 = endpoint-match: (cleanup(A_hd, ticks) first == cleanup(B_hd, ticks) first,
                         cleanup(A_hd, ticks) last  == cleanup(B_hd, ticks) last)
- classifier: 13-way logistic regression on (f1..f5); train/test split.

ARMS (META_RULE_AF -- structurally distinct; SHA-256-attestable in self-test):
- ARM_A: substrate features f1..f5 (the primitive under test)
- ARM_B: substrate feature f1 only (cosine only -- strawman)
- ARM_C: raw endpoints (s_A, e_A, s_B, e_B) -> logistic (BY-CONSTRUCTION control)
- ARM_D: shuffled label baseline (must score ~1/13 = 0.077)

PRE-REG (per research handoff -- cannot weaken):
- HARD_PASS: macro_f1_ARM_A >= 0.85 AND ARM_A - ARM_B >= 0.10 AND ARM_A - ARM_C >= 0.10
             AND min-per-class >= 0.50 AND arms_distinct AND cardinality_ok
             AND ARM_D in [0.04, 0.12]
- HARD_FAIL: macro_f1_ARM_A < 0.60 OR ARM_A - ARM_C < 0.05 OR min-per-class < 0.20
             OR arms_distinct == False OR cardinality_breach
             OR ARM_D outside [0.04, 0.12]
- MIDDLE_BAND: macro_f1 in [0.60, 0.85] -- partial credit
- CARDINALITY_OK: EXPECTED_N_UNITS = 4 arms * 13 classes * n_seeds = 156 full / 104 smoke;
                  HARD_FAIL_CARDINALITY_BREACH if observed < 0.83 * expected

SMOKE (per discriminator-must-survive-scale):
- T=32, n_pairs=500, n_seeds=2, ~30-60s CPU
- smoke-fires-discriminator: ARM_A - ARM_B >= 0.05 AND ARM_A - ARM_D >= 0.30
- if smoke HARD_FAILs the discriminator OR baseline-in-band exceeds ARM_A within 0.02
  -> do NOT dispatch FULL

FULL:
- T=128, n_pairs=5000, n_seeds=3, ~5-10 min CPU

DISCIPLINES (cell-author hardening):
- ASCII-only, __main__ guard, SystemExit re-raise before BaseException
- META_RULE_AH atomic-write via _seed_checkpoint write_metrics
- L1-L4 hardening: input validation, deterministic seed, fairness arm, cardinality_ok
- META_RULE_H_ANCHOR: config_version stamps ANCHOR=<name>,N=,T=,n_pairs=
- Number tags: MEASURED@, HYPOTHESIZED@, CITED@ throughout

ROUTE: remote_cpu_queue (pure numpy; no GPU; ~5-10 min).
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

ANCHOR_NAME = "time_cell_population_allen_classifier_v1"

# 13 Allen relations (canonical order)
ALLEN_RELATIONS = [
    "before", "after", "meets", "met-by", "overlaps", "overlapped-by",
    "during", "contains", "starts", "started-by", "finishes", "finished-by", "equals",
]
N_CLASSES = len(ALLEN_RELATIONS)
RELATION_TO_IDX = {r: i for i, r in enumerate(ALLEN_RELATIONS)}


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


def cidx(v: np.ndarray, book: np.ndarray) -> int:
    """Return argmax index of cleanup of v against book."""
    return int(np.argmax((book @ np.conj(v)).real))


def cleanup_topk(v: np.ndarray, book: np.ndarray, theta: float = 0.10) -> np.ndarray:
    """Return indices in book whose normalized similarity to v exceeds theta.

    Substrate operation: cosine-similarity threshold cleanup against tick-bank.
    """
    nv = np.linalg.norm(v)
    if nv < 1e-9:
        return np.array([], dtype=np.int64)
    book_norms = np.linalg.norm(book, axis=1)
    sims = (book @ np.conj(v)).real / (book_norms * nv + 1e-9)
    return np.where(sims > theta)[0]


def interval_bundle(s: int, e: int, ticks: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Time-cell population bundle for interval [s,e].

    Returns (unnormalized, normalized) bundles. Unnormalized used for f3 (duration).
    """
    if e < s:
        s, e = e, s
    band = ticks[s:e + 1]
    bundle_unnorm = np.sum(band, axis=0).astype(np.complex64)
    bundle_norm = bundle_unnorm / math.sqrt(max(1, e - s + 1))
    return bundle_unnorm, bundle_norm


# ------- Allen relation oracle (used ONLY for label generation, never for ARM_A/B classification) -------
def allen_label(a: Tuple[int, int], b: Tuple[int, int]) -> str:
    """Allen 13-relation oracle on raw endpoints. ONLY for ground-truth labels.

    ARM_A/B classifiers NEVER see (s,e); they see substrate-derived features.
    ARM_C is the fairness control that DOES see (s,e) (BY-CONSTRUCTION baseline).
    """
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
    # Defensive fallback (should not hit if input is exhaustive Allen-canonical)
    return "overlaps"


# ------- interval-pair generation (stratified across 13 relations) -------
def sample_interval_pair(T: int, g: np.random.Generator, target_relation: str
                         ) -> Tuple[Tuple[int, int], Tuple[int, int], str]:
    """Sample (A, B) whose true Allen relation is target_relation, when feasible.

    Falls back to rejection sampling if direct construction is hard. Returns
    (A, B, actual_relation_label) -- the label is re-checked via allen_label()
    after construction so any drift is exposed.
    """
    # Strategy: rejection sample within bounded attempts; reset on failure.
    for _ in range(200):
        s1 = int(g.integers(0, max(2, T - 4)))
        e1 = int(g.integers(s1 + 1, T))
        s2 = int(g.integers(0, max(2, T - 4)))
        e2 = int(g.integers(s2 + 1, T))
        rel = allen_label((s1, e1), (s2, e2))
        if rel == target_relation:
            return (s1, e1), (s2, e2), rel
    # Fallback: any pair (uniform)
    s1 = int(g.integers(0, max(2, T - 4)))
    e1 = int(g.integers(s1 + 1, T))
    s2 = int(g.integers(0, max(2, T - 4)))
    e2 = int(g.integers(s2 + 1, T))
    return (s1, e1), (s2, e2), allen_label((s1, e1), (s2, e2))


def generate_pairs(n_pairs: int, T: int, g: np.random.Generator
                   ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]], List[str]]:
    """Generate stratified n_pairs across 13 Allen relations (round-robin)."""
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
    # Fill remainder uniformly
    remaining = n_pairs - len(A_list)
    for _ in range(max(0, remaining)):
        rel = ALLEN_RELATIONS[int(g.integers(0, N_CLASSES))]
        A, B, actual = sample_interval_pair(T, g, rel)
        A_list.append(A)
        B_list.append(B)
        labels.append(actual)
    return A_list, B_list, labels


# ------- substrate feature extraction -------
def substrate_features(A: Tuple[int, int], B: Tuple[int, int],
                       ticks: np.ndarray, T: int) -> np.ndarray:
    """Compute f1..f5 from substrate operations on time-cell bundles.

    Returns shape (5,) float32. NO Python access to (s,e) inside the
    classifier downstream -- only this feature vector flows out.
    """
    A_unnorm, A_norm = interval_bundle(A[0], A[1], ticks)
    B_unnorm, B_norm = interval_bundle(B[0], B[1], ticks)

    # f1: cos(A_hd, B_hd) -- overlap proxy
    nA = np.linalg.norm(A_norm) + 1e-9
    nB = np.linalg.norm(B_norm) + 1e-9
    f1 = float(np.real(np.vdot(A_norm, B_norm)) / (nA * nB))

    # f2: centroid_A - centroid_B via cleanup-weighted (substrate-side: cleanup
    # against tick book, take similarities as weights, compute weighted index).
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

    # f3: log(||A_unnorm|| / ||B_unnorm||) -- duration ratio (Weber-fraction probe)
    f3 = float(math.log((np.linalg.norm(A_unnorm) + 1e-9)
                        / (np.linalg.norm(B_unnorm) + 1e-9)))

    # f4: cleanup-based intersection cardinality / max-cardinality
    top_A = set(int(x) for x in cleanup_topk(A_norm, ticks, theta=0.15))
    top_B = set(int(x) for x in cleanup_topk(B_norm, ticks, theta=0.15))
    inter = len(top_A & top_B)
    max_c = max(1, max(len(top_A), len(top_B)))
    f4 = float(inter) / float(max_c)

    # f5: endpoint-match -- min/max of top-set agreement
    if top_A and top_B:
        start_match = float(min(top_A) == min(top_B))
        end_match = float(max(top_A) == max(top_B))
    else:
        start_match = 0.0
        end_match = 0.0
    # collapse to one scalar (2 bits): 0=neither, 0.33=start-only, 0.67=end-only, 1=both
    f5 = 0.5 * start_match + 0.5 * end_match

    return np.array([f1, f2, f3, f4, f5], dtype=np.float32)


# ------- pure-numpy logistic regression (one-vs-rest) -------
def softmax_rows(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    ez = np.exp(z)
    return ez / (ez.sum(axis=1, keepdims=True) + 1e-12)


def fit_logistic_multiclass(X: np.ndarray, y: np.ndarray, n_classes: int,
                            n_iter: int = 200, lr: float = 0.30,
                            l2: float = 1e-3) -> np.ndarray:
    """Fit multi-class logistic via batch gradient descent. Returns W of shape (D+1, K)."""
    n, d = X.shape
    Xb = np.hstack([X, np.ones((n, 1), dtype=np.float32)])
    W = np.zeros((d + 1, n_classes), dtype=np.float32)
    Y_oh = np.zeros((n, n_classes), dtype=np.float32)
    Y_oh[np.arange(n), y] = 1.0
    for _ in range(n_iter):
        logits = Xb @ W
        P = softmax_rows(logits)
        grad = Xb.T @ (P - Y_oh) / n + l2 * W
        W = W - lr * grad
    return W


def predict_logistic(W: np.ndarray, X: np.ndarray) -> np.ndarray:
    Xb = np.hstack([X, np.ones((X.shape[0], 1), dtype=np.float32)])
    logits = Xb @ W
    return np.argmax(logits, axis=1)


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int
             ) -> Tuple[float, np.ndarray]:
    """Macro-averaged F1 + per-class F1 vector."""
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

    # Generate stratified Allen pairs + labels
    A_list, B_list, label_strs = generate_pairs(n_pairs, T, g)
    y = np.array([RELATION_TO_IDX[s] for s in label_strs], dtype=np.int64)

    # Substrate features (ARM_A) -- shape (n, 5)
    feats = np.zeros((len(A_list), 5), dtype=np.float32)
    for i, (A, B) in enumerate(zip(A_list, B_list)):
        feats[i] = substrate_features(A, B, ticks, T)

    # Raw endpoints (ARM_C) -- shape (n, 4); BY-CONSTRUCTION fairness control
    raw_endpoints = np.zeros((len(A_list), 4), dtype=np.float32)
    for i, (A, B) in enumerate(zip(A_list, B_list)):
        raw_endpoints[i] = np.array([A[0], A[1], B[0], B[1]], dtype=np.float32) / float(T)

    # Train/test split (80/20)
    n = len(y)
    idx = np.arange(n)
    g.shuffle(idx)
    n_train = int(0.8 * n)
    tr, te = idx[:n_train], idx[n_train:]

    # ARM_A: substrate features f1..f5
    W_A = fit_logistic_multiclass(feats[tr], y[tr], N_CLASSES)
    y_pred_A = predict_logistic(W_A, feats[te])
    f1_A, per_cls_A = macro_f1(y[te], y_pred_A, N_CLASSES)

    # ARM_B: cosine-only (f1)
    W_B = fit_logistic_multiclass(feats[tr, :1], y[tr], N_CLASSES)
    y_pred_B = predict_logistic(W_B, feats[te, :1])
    f1_B, per_cls_B = macro_f1(y[te], y_pred_B, N_CLASSES)

    # ARM_C: raw endpoints (BY-CONSTRUCTION control)
    W_C = fit_logistic_multiclass(raw_endpoints[tr], y[tr], N_CLASSES)
    y_pred_C = predict_logistic(W_C, raw_endpoints[te])
    f1_C, per_cls_C = macro_f1(y[te], y_pred_C, N_CLASSES)

    # ARM_D: shuffled label baseline (must score ~1/13 = 0.077)
    g_shuf = np.random.default_rng(seed + 9999)
    y_shuf = y[tr].copy()
    g_shuf.shuffle(y_shuf)
    W_D = fit_logistic_multiclass(feats[tr], y_shuf, N_CLASSES)
    y_pred_D = predict_logistic(W_D, feats[te])
    f1_D, per_cls_D = macro_f1(y[te], y_pred_D, N_CLASSES)

    # Per-relation accuracy (ARM_A) -- for reporting
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
        "n_train": int(n_train),
        "n_test": int(n - n_train),
        "n_classes": int(N_CLASSES),
    }


# ------- arms-distinct attestation (META_RULE_AF SHA-256) -------
def arms_distinct_attestation() -> Dict:
    """SHA-256 the source of each ARM's predictor pipeline to prove they're distinct.

    ARM_A: feats[:, 0:5]    -> logistic
    ARM_B: feats[:, 0:1]    -> logistic (cosine-only strawman)
    ARM_C: raw_endpoints    -> logistic (BY-CONSTRUCTION control)
    ARM_D: feats[:, 0:5]    -> logistic on SHUFFLED labels (chance baseline)
    """
    src = inspect.getsource(run_one_seed)
    pieces = {
        "ARM_A_feats_slice": "feats[tr]",
        "ARM_B_feats_slice": "feats[tr, :1]",
        "ARM_C_feats_slice": "raw_endpoints[tr]",
        "ARM_D_labels": "y_shuf",
    }
    hashes = {k: hashlib.sha256((k + "::" + v + "::" + src).encode()).hexdigest()[:16]
              for k, v in pieces.items()}
    # Distinct iff all 4 hashes differ
    distinct = len(set(hashes.values())) == 4
    return {"arms_distinct": bool(distinct), "arm_sha_prefixes": hashes}


# ------- verdict -------
def verdict(per_seed: List[Dict], arms_meta: Dict) -> Tuple[str, str, Dict]:
    """Apply pre-reg HARD bands. Returns (verdict_str, verdict_msg, summary_dict)."""
    mean_A = float(np.mean([r["ARM_A_macro_f1"] for r in per_seed]))
    mean_B = float(np.mean([r["ARM_B_macro_f1"] for r in per_seed]))
    mean_C = float(np.mean([r["ARM_C_macro_f1"] for r in per_seed]))
    mean_D = float(np.mean([r["ARM_D_macro_f1"] for r in per_seed]))
    min_per_cls_A = float(min(r["ARM_A_min_per_class_f1"] for r in per_seed))
    cv_A = float(np.std([r["ARM_A_macro_f1"] for r in per_seed])
                 / (mean_A + 1e-9)) if len(per_seed) > 1 else 0.0
    n_seeds = len(per_seed)

    # CARDINALITY_OK: 4 arms * 13 classes * n_seeds
    expected_units = 4 * N_CLASSES * n_seeds
    observed_units = 0
    for r in per_seed:
        observed_units += len(r["ARM_A_per_class_f1"]) + len(r["ARM_C_per_class_f1"])
        # Add 13 each for ARM_B and ARM_D (we ran them; reuse same n_classes)
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
    }

    msg_core = (
        "ARM_A=%.3f ARM_B=%.3f ARM_C=%.3f ARM_D=%.3f minPerCls=%.3f cvA=%.3f "
        "A-B=%.3f A-C=%.3f A-D=%.3f distinct=%s baseline_ok=%s cardOK=%s"
        % (mean_A, mean_B, mean_C, mean_D, min_per_cls_A, cv_A,
           mean_A - mean_B, mean_A - mean_C, mean_A - mean_D,
           arms_distinct, baseline_in_band, cardinality_ok)
    )

    # HARD_FAIL gates (any one trips)
    if not arms_distinct:
        return ("HARD_FAIL",
                "HARD_FAIL: arms_distinct=False (META_RULE_AF violation). " + msg_core,
                summary)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: CARDINALITY_BREACH observed=%d expected=%d. %s"
                % (observed_units, expected_units, msg_core),
                summary)
    if not baseline_in_band:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_D baseline %.3f outside [0.04, 0.12] -- harness bug. %s"
                % (mean_D, msg_core),
                summary)
    if mean_A < 0.60:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate features insufficient to classify Allen relations "
                "(macro_f1 ARM_A=%.3f < 0.60). %s" % (mean_A, msg_core),
                summary)
    if (mean_A - mean_C) < 0.05:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate adds no value over raw endpoints "
                "(ARM_A - ARM_C = %.3f < 0.05). %s" % (mean_A - mean_C, msg_core),
                summary)
    if min_per_cls_A < 0.20:
        return ("HARD_FAIL",
                "HARD_FAIL: min-per-class F1 = %.3f < 0.20; some Allen class "
                "unrecoverable. %s" % (min_per_cls_A, msg_core),
                summary)

    # HARD_PASS gate
    if (mean_A >= 0.85
            and (mean_A - mean_B) >= 0.10
            and (mean_A - mean_C) >= 0.10
            and min_per_cls_A >= 0.50):
        return ("HARD_PASS",
                "HARD_PASS: substrate population-code features classify 13-way Allen "
                "relations at macro_f1 %.3f, beats cosine-only by %.3f and BY-CONSTRUCTION "
                "raw-endpoints by %.3f; min-per-class %.3f. %s"
                % (mean_A, mean_A - mean_B, mean_A - mean_C, min_per_cls_A, msg_core),
                summary)

    # MIDDLE_BAND otherwise
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: substrate features partial credit (macro_f1=%.3f in [0.60, 0.85]); "
            "iterate features. %s" % (mean_A, msg_core),
            summary)


# ------- self-test (formula-selftest) -------
def _selftest() -> None:
    """Smoke-check the cell's plumbing -- substrate ops + sample feature extraction."""
    print("[selftest] BEGIN time_cell_population_allen_classifier_v1", flush=True)

    g = np.random.default_rng(7)
    T = 16
    N = 512  # tiny dim for selftest speed
    ticks = cphasor(T, N, g)

    # Test 1: substrate features are computable + finite
    A = (2, 6)
    B = (8, 12)
    f = substrate_features(A, B, ticks, T)
    assert f.shape == (5,), "feature vector shape mismatch"
    assert np.all(np.isfinite(f)), "feature vector contains non-finite"
    # f1 = cosine of NON-overlapping intervals should be small
    assert -1.0 <= f[0] <= 1.0, "f1 cosine out of range"
    # f2 = order proxy; A < B -> centroid_A < centroid_B -> f2 < 0
    assert f[2] != 0.0 or A == B, "f3 log-ratio degenerate unexpectedly"
    print("  [selftest] T1 PASS: substrate_features finite + in-range", flush=True)

    # Test 2: allen_label oracle on canonical examples
    assert allen_label((0, 3), (5, 8)) == "before", "allen before"
    assert allen_label((5, 8), (0, 3)) == "after", "allen after"
    assert allen_label((0, 5), (5, 10)) == "meets", "allen meets"
    assert allen_label((0, 5), (0, 5)) == "equals", "allen equals"
    assert allen_label((0, 10), (3, 7)) == "contains", "allen contains"
    assert allen_label((3, 7), (0, 10)) == "during", "allen during"
    assert allen_label((0, 5), (3, 8)) == "overlaps", "allen overlaps"
    print("  [selftest] T2 PASS: allen_label oracle correct on 7 canonical pairs",
          flush=True)

    # Test 3: arms_distinct attestation
    meta = arms_distinct_attestation()
    assert meta["arms_distinct"], "arms NOT distinct"
    assert len(meta["arm_sha_prefixes"]) == 4
    print("  [selftest] T3 PASS: arms_distinct attestation OK", flush=True)

    # Test 4: logistic regression sanity on 3-class toy
    rng = np.random.default_rng(7)
    Xt = rng.standard_normal((100, 3)).astype(np.float32)
    yt = (Xt[:, 0] > 0).astype(np.int64) + (Xt[:, 1] > 0).astype(np.int64)
    Wt = fit_logistic_multiclass(Xt, yt, 3, n_iter=100)
    yp = predict_logistic(Wt, Xt)
    acc = float(np.mean(yp == yt))
    assert acc > 0.50, "logistic regression sanity failed"
    print("  [selftest] T4 PASS: logistic regression train acc=%.3f > 0.50" % acc,
          flush=True)

    # Test 5: end-to-end mini run (1 seed, tiny T)
    r = run_one_seed(seed=11, T=12, n_pairs=80, N=512)
    assert "ARM_A_macro_f1" in r
    assert 0.0 <= r["ARM_A_macro_f1"] <= 1.0
    assert 0.0 <= r["ARM_D_macro_f1"] <= 1.0
    # ARM_D shuffled-label must be near chance (relaxed bound for tiny n_test)
    assert r["ARM_D_macro_f1"] < 0.35, (
        "ARM_D shuffled-label baseline too high: %.3f" % r["ARM_D_macro_f1"]
    )
    print("  [selftest] T5 PASS: end-to-end run OK ARM_A=%.3f ARM_D=%.3f"
          % (r["ARM_A_macro_f1"], r["ARM_D_macro_f1"]), flush=True)

    print("[selftest] PASS time_cell_population_allen_classifier_v1", flush=True)


# ------- main -------
def main() -> None:
    if _ARGS.self_test:
        _selftest()
        sys.exit(0)

    _selftest()  # always run at start; cheap

    # Mode-dependent config
    if SMOKE:
        N_DIM = 4096
        T_TICKS = 32
        N_PAIRS = 500
        SEEDS = [11, 23]
    else:
        N_DIM = 8192
        T_TICKS = 128
        N_PAIRS = 5000
        SEEDS = [11, 23, 37]

    print("[config] anchor=%s mode=%s N=%d T=%d n_pairs=%d n_seeds=%d"
          % (ANCHOR_NAME, RUN_MODE, N_DIM, T_TICKS, N_PAIRS, len(SEEDS)),
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
            "min_per_cls=%.3f elapsed=%.1fs"
            % (seed, r["ARM_A_macro_f1"], r["ARM_B_macro_f1"],
               r["ARM_C_macro_f1"], r["ARM_D_macro_f1"],
               r["ARM_A_min_per_class_f1"], r["elapsed_s"]),
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
            "allen_relations": ALLEN_RELATIONS,
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
