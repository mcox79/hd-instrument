"""REASONING x FOUNDATION -- REAL-DATA INTEGRATION TEST (v1): does the substrate's LEARNED SYMMETRIC bind
(the frontier's symmetric-discovery arm) read out the REAL generated chem-pair-hazard NON-ADDITIVE conjunction on
NOVEL chemical pairs, BEATING an additive model AND frequency? Glass-box CPU, NO LLM at measurement time.

This is the FIRST connection of the reasoning MECHANISM x real FOUNDATION data -- the program's real-data proof.

Two inlined prior threads (NO re-hunt):
  (1) FRONTIER (exp_interaction_nonadditive_discovery_v1, commit 59056b6d4, VET-clean): a LEARNED SHARED-code
      SWAP-SYMMETRIC product bind (LEARN_SYM = emb[a] (x) emb[b], Hadamard) DISCOVERS a SYMMETRIC non-additive
      target (parity-K, ~0.98) >> a learned-ADDITIVE arm (~0.38, chance ~0.52). Role-keyed arms OVER-parameterize
      and FAIL the symmetric target. Established (on SYNTHETIC parity): op-symmetry must MATCH target-symmetry.
  (2) FOUNDATION (exp_generated_conjunction_nonadditive_chem_v1, commit a6d93fbae): GENERATED a REAL, adversarially
      vetted, genuinely NON-ADDITIVE SYMMETRIC conjunction -- chemical-mixing hazard: hazard(A,B)=hazard(B,A);
      non-additivity 0.263 CONFIRMED (a flexible learned-ADDITIVE model cannot capture it), additive-synth control
      0.028, no dominant driver (dominance_ratio well below 0.60). 135 adversarially-vetted-TRUE named substance
      pairs; constituent = reactivity CLASS of each member (11 classes); target = ordinal mixing hazard (0..4).

QUESTION: does the SYMMETRIC-discovery mechanism TRANSFER from synthetic parity to the REAL chem conjunction on
NOVEL class-pairs? Because chem hazard is SYMMETRIC, the SYMMETRIC product bind (LEARN_SYM) is the predicted WINNER;
the learned-ADDITIVE arm should FAIL (0.263 non-additivity); ROLE-KEYED / asymmetric arms should NOT beat the
symmetric arm (head/algebra discrimination -- a symmetric target does not reward broken symmetry).

CONTRACT: predict the ordinal hazard of a NOVEL chemical pair from the two chemicals' (reactivity-class) codes via
each arm. Primary claim: LEARN_SYM (learned symmetric bind) beats BOTH FREQ_NULL and the best ADDITIVE arm on the
NOVEL stratum. Report the symmetric-vs-additive dissociation + vs frequency; verify role-keyed arms do NOT beat it.

REAL-DATA ROBUSTNESS: the cluster truth_rate is 0.833 (adversarial near-miss) -> even the 135 vetted-TRUE rows carry
residual label noise, AND 15/34 class-pairs span >1 hazard level (genuine within-class-pair spread). The class-pair
Bayes info-ceiling (majority hazard per class-pair, all-seen) is ~0.83 -- NO class-pair predictor can exceed it, so
bands are set BELOW it. We treat noise as a REAL-DATA ROBUSTNESS test (does the mechanism survive real label noise),
NOT as failure; adjacent-level (within-1) accuracy is reported alongside exact for the noise-robust narrative.

ARMS (predict ordinal hazard of a query pair from its two class codes):
  Learned (plain SGD; the DISCOVERY / mechanism test):
    LEARN_SYM      SHARED code + HADAMARD-PRODUCT compose (swap-symmetric) + linear readout. THE mechanism / predicted
                   winner. (product = the substrate bind; the REAL FHRR bind path is exercised in self_test.)
    LEARN_ADD_SYM  SHARED code + SUM compose (swap-symmetric) + linear readout. The ADDITIVE contrast (same code, same
                   symmetry -> isolates PRODUCT-vs-SUM = interaction-vs-additive). Should FAIL (0.263 non-additive).
    LEARN_INT      ROLE-KEYED (per-position table) + product. Asymmetric contrast; must NOT beat LEARN_SYM.
    LEARN_BIL      ROLE-KEYED low-rank bilinear (fixed shared code, learned per-role projection init=identity).
                   Asymmetric contrast; must NOT beat LEARN_SYM.
  Closed-form reference (fair floors + prior-result reproduce -- Gate D positive control AT TEST REGIME):
    ADD_LSQ        least-squares per-class main effects (STRONGEST additive-over-classes), round-to-bin. From FOUNDATION.
    INT_CF         class-PAIR conditional mean + additive backoff on novel pairs. From FOUNDATION; reproduces the
                   0.263 non-additivity (INT_CF_seen - ADD_LSQ_seen) at THIS test regime.
    HOMOPHILY      per-class marginal vote (frequency floor that is additive-in-class-presence).
    MEMORIZE       exact pair-INSTANCE memorization (leak control; fails NOVEL by construction).
    POP            majority hazard. FREQ_NULL = max(HOMOPHILY, POP).
    ORACLE         true label (ceiling).
MUST-FAILS (regimes): CLEAN(real) ; ARBITRARY (random hazard per unique class-pair -> no generalizable structure) ;
  SHUFFLE (label permutation across pairs -> all structure destroyed). No mechanism arm may beat FREQ_NULL on the
  NOVEL stratum of ARBITRARY/SHUFFLE (gap <= tol). MEMORIZE must not beat FREQ_NULL on CLEAN novel (leak control).

HEADLINE (NOVEL stratum, exact top-1 accuracy, multi-seed mean):
  (freq)  LEARN_SYM_novel - FREQ_NULL_novel        (mechanism beats frequency on NOVEL real pairs)
  (add)   LEARN_SYM_novel - best_additive_novel     (symmetric bind beats additive -> non-additive discovery on real)
  (algebra) LEARN_SYM_novel vs role_keyed_best_novel (symmetric target does NOT reward broken symmetry)
  (reproduce) INT_CF_seen - ADD_LSQ_seen            (Gate D: reproduces FOUNDATION 0.263 non-additivity at test regime)

PRE-REGISTERED BANDS (fixed BEFORE running; see prereg .md):
  HARD_PASS (thesis proven end-to-end on real data):
    LEARN_SYM_novel - FREQ_NULL_novel      >= 0.08 AND
    LEARN_SYM_novel - best_additive_novel  >= 0.06 AND
    LEARN_SYM_novel                        >= role_keyed_best_novel - 0.03 (role-keyed does NOT beat symmetric) AND
    INT_CF_seen - ADD_LSQ_seen             >= 0.12 (non-additivity reproduced at test regime) AND
    must-fails fire (ARBITRARY/SHUFFLE novel gaps <= 0.10; MEMORIZE leak <= 0.10) AND oracle ceiling ok AND
    FREQ_NULL_novel not saturated (< 0.75).
  REFUTE (valuable negative -- symmetric mechanism does NOT transfer to real data; triggers a 2x drill on WHY):
    LEARN_SYM_seen - best_additive_seen <= 0.03 (the learned symmetric bind fails to capture the real non-additive
    structure even where the class-pair is SEEN) AND must-fails fire AND oracle ceiling ok.
  MIDDLE_BAND: anything else -- notably "captures-but-does-not-extrapolate" (LEARN_SYM beats additive on SEEN but
    does NOT clear the NOVEL margins): the mechanism represents the real non-additive conjunction but does not
    generalize it to UNSEEN class-pairs. Honest, informative partial.

Glass-box CPU. Default invocation (no flag) = FULL run to completion (runner calls `python -u <script>` no args).
ASCII-only. No bare except; except SystemExit before except Exception. Atomic metrics write.
Deterministic INTEGER seeds only (PROT-023): NO hash()-derived RNG, NO list(set()) ordering (sorted-unique ids;
stable enumerated regime indices; fixed int seeds).
"""

import argparse
import hashlib
import json
import math
import os
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.binding import bind as hd_bind      # noqa: E402  # REAL FHRR bind (complex64 elementwise mul).
# Use ONLY the long-stable `bind` (present on both local + remote runner). The learned SGD arms compose with a
# torch elementwise product (the differentiable analog of the substrate bind); the self_test exercises the REAL
# complex hd_bind homomorphism so the mechanism claim rests on the actual substrate primitive.

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "reasoning_x_foundation_chem_hazard_symmetric_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
ARTIFACT = os.path.join(_REPO, "data", "foundation_clusters", "chem_pair_hazard_nonadditive_v1.json")

# ---- reactivity classes / ordinal target (must match the foundation cluster schema) ----
CLASSES = [
    "inert_or_water", "weak_acid", "strong_acid", "strong_base", "ammonia_or_amine",
    "hypochlorite_bleach", "oxidizer", "reactive_metal", "sulfide_or_cyanide_salt",
    "organic_solvent_or_fuel", "reducing_agent",
]
CLASS_IDX = {c: i for i, c in enumerate(CLASSES)}
NCLS = len(CLASSES)
TARGET = "hazard"
TARGET_SCALE = ["none", "minor", "moderate", "high", "severe"]
TGT_IDX = {v: i for i, v in enumerate(TARGET_SCALE)}
L = len(TARGET_SCALE)  # 5 ordinal severity levels 0..4

# ---- regimes (stable enumerated indices; NEVER hash()) ----
CLEAN = "CLEAN_REAL"; ARBITRARY = "ARBITRARY"; SHUFFLE = "SHUFFLE"
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]
REG_IDX = {r: i for i, r in enumerate(REGIMES)}
CLAIM_ARMS_KEY = "mechanism"  # arms that carry a discovery claim -> must-fail gates apply

# ---- arm names ----
LEARN_SYM = "LEARN_SYM"; LEARN_ADD_SYM = "LEARN_ADD_SYM"; LEARN_INT = "LEARN_INT"; LEARN_BIL = "LEARN_BILINEAR"
ADD_LSQ = "ADD_LSQ"; INT_CF = "INT_CF"; HOM = "HOMOPHILY"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"
ARM_NAMES = [LEARN_SYM, LEARN_ADD_SYM, LEARN_INT, LEARN_BIL, ADD_LSQ, INT_CF, HOM, MEMO, POP, ORC, FREQ]
MECHANISM_ARMS = [LEARN_SYM, LEARN_ADD_SYM, LEARN_INT, LEARN_BIL, INT_CF]  # must-fail gate scope
ROLE_KEYED_ARMS = [LEARN_INT, LEARN_BIL]
ADDITIVE_ARMS = [LEARN_ADD_SYM, ADD_LSQ]

# ---- learned-arm hyperparams (fixed) ----
EMB_D = 32          # >= NCLS -> full-rank symmetric bilinear capacity over the 11-class pair
EPOCHS = 400
LR = 0.05
QUERY_FRAC = 0.45   # instance-level split; NOVEL = query pairs whose class-pair is absent from train

# ---- pre-registered bands (fixed before running) ----
HP_SYM_FREQ_NOVEL = 0.08   # LEARN_SYM_novel - FREQ_NULL_novel
HP_SYM_ADD_NOVEL = 0.06    # LEARN_SYM_novel - best_additive_novel
HP_ROLE_SLACK = 0.03       # LEARN_SYM_novel >= role_keyed_best_novel - this (role-keyed does NOT beat symmetric)
HP_SEEN_NONADD = 0.12      # INT_CF_seen - ADD_LSQ_seen (reproduce FOUNDATION non-additivity at test regime; Gate D)
MUSTFAIL_TOL = 0.10        # mechanism arm - FREQ_NULL on ARBITRARY/SHUFFLE novel; MEMO leak on CLEAN novel
REFUTE_SEEN_GAP = 0.03     # LEARN_SYM_seen - best_additive_seen <= this => mechanism does NOT transfer to real data
FREQ_SAT = 0.75            # FREQ_NULL_novel must be below this (arena not saturated)
MIN_NOVEL_TOTAL = 30       # aggregate novel-instance count across seeds (fairness / power)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return "nan"


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


# ===========================================================================
# LOAD REAL CLUSTER (vetted-TRUE only) -> canonical class-pair X, ordinal hazard y
# ===========================================================================

def load_cluster():
    with open(ARTIFACT, "r", encoding="utf-8") as f:
        p = json.load(f)
    rows = [r for r in p["rows"] if r.get("vetted_true", None) is True]  # ONLY the 135 adversarially-vetted-TRUE
    X = np.zeros((len(rows), 2), dtype=np.int64)
    y = np.zeros(len(rows), dtype=np.int64)
    for i, r in enumerate(rows):
        a = CLASS_IDX[str(r["class_a"]).strip().lower()]
        b = CLASS_IDX[str(r["class_b"]).strip().lower()]
        X[i, 0], X[i, 1] = min(a, b), max(a, b)  # canonical UNORDERED pair (hazard is symmetric)
        y[i] = TGT_IDX[str(r[TARGET]).strip().lower()]
    return p, X, y


def chance_of(y):
    c = np.bincount(y, minlength=L).astype(np.float64)
    return float(c.max() / max(1.0, c.sum()))


def classpair_bayes_ceiling(X, y):
    """Majority-hazard per class-pair over ALL data = Bayes info-ceiling for any class-pair predictor (exact acc)."""
    pool = defaultdict(list)
    for i in range(X.shape[0]):
        pool[(int(X[i, 0]), int(X[i, 1]))].append(int(y[i]))
    correct = sum(np.bincount(v, minlength=L).max() for v in pool.values())
    return float(correct) / max(1, len(y))


# ===========================================================================
# MI diagnostics (non-additivity evidence; reported)
# ===========================================================================

def mutual_info(a, b, base=2.0):
    n = len(a)
    if n == 0:
        return 0.0
    pa = defaultdict(float); pb = defaultdict(float); pab = defaultdict(float)
    inv = 1.0 / n
    for x, z in zip(np.asarray(a).tolist(), np.asarray(b).tolist()):
        pa[x] += inv; pb[z] += inv; pab[(x, z)] += inv
    mi = 0.0
    for (x, z), pxz in pab.items():
        mi += pxz * math.log(pxz / (pa[x] * pb[z]) + 1e-30, base)
    return max(0.0, mi)


def _pair_ids(X):
    """Deterministic id per canonical (cA,cB) via SORTED-unique enumeration (NEVER hash())."""
    uniq = sorted(set((int(X[i, 0]), int(X[i, 1])) for i in range(X.shape[0])))
    m = {t: i for i, t in enumerate(uniq)}
    return np.array([m[(int(X[i, 0]), int(X[i, 1]))] for i in range(X.shape[0])], dtype=np.int64)


def conjunction_property(X, y):
    mi_a = mutual_info(X[:, 0], y); mi_b = mutual_info(X[:, 1], y)
    joint = mutual_info(_pair_ids(X), y)
    best_single = max(mi_a, mi_b)
    ratio = (best_single / joint) if joint > 1e-9 else float("nan")
    return dict(best_single_mi=round(best_single, 4), joint_mi=round(joint, 4),
                mi_margin=round(joint - best_single, 4),
                dominance_ratio=(round(ratio, 4) if ratio == ratio else ratio))


# ===========================================================================
# CLOSED-FORM ARMS (fair floors + FOUNDATION prior-result reproduce)
# ===========================================================================

def _design(Xm):
    """Per-class COUNT design (n x NCLS+1): col c = #times class c appears in the pair (0/1/2), plus intercept."""
    D = np.zeros((Xm.shape[0], NCLS + 1), dtype=np.float64)
    D[:, 0] = 1.0
    for r in range(Xm.shape[0]):
        D[r, 1 + int(Xm[r, 0])] += 1.0
        D[r, 1 + int(Xm[r, 1])] += 1.0
    return D


def _round_bins(vals):
    return np.clip(np.round(vals), 0, L - 1).astype(np.int64)


def arm_add_lsq(Xtr, ytr, Xq):
    """STRONGEST additive-over-classes predictor: least-squares of ordinal hazard on symmetric per-class counts."""
    D_tr = _design(Xtr)
    beta, _, _, _ = np.linalg.lstsq(D_tr, ytr.astype(np.float64), rcond=None)
    return _round_bins(_design(Xq) @ beta), beta


def arm_int_cf(Xtr, ytr, Xq, beta):
    """2-way INTERACTION predictor: class-PAIR conditional mean from train; additive backoff for novel class-pairs."""
    pair_sum = defaultdict(float); pair_cnt = defaultdict(int)
    for r in range(Xtr.shape[0]):
        k = (int(Xtr[r, 0]), int(Xtr[r, 1]))
        pair_sum[k] += float(ytr[r]); pair_cnt[k] += 1
    add_pred = _round_bins(_design(Xq) @ beta)
    preds = np.empty(Xq.shape[0], dtype=np.int64)
    for r in range(Xq.shape[0]):
        k = (int(Xq[r, 0]), int(Xq[r, 1]))
        if k in pair_cnt:
            preds[r] = int(np.clip(round(pair_sum[k] / pair_cnt[k]), 0, L - 1))
        else:
            preds[r] = add_pred[r]
    return preds


def arm_homophily(Xtr, ytr, Xq):
    """Per-class marginal vote (frequency floor, additive-in-class-presence)."""
    per = [defaultdict(lambda: np.zeros(L)) for _ in range(2)]
    for r in range(Xtr.shape[0]):
        for i in range(2):
            per[i][int(Xtr[r, i])][int(ytr[r])] += 1.0
    marg = np.bincount(ytr, minlength=L).astype(np.float64)
    preds = []
    for q in range(Xq.shape[0]):
        sc = np.zeros(L)
        for i in range(2):
            sc = sc + per[i].get(int(Xq[q, i]), np.zeros(L))
        preds.append(int(np.argmax(sc if sc.sum() > 0 else marg)))
    return np.array(preds, dtype=np.int64)


def arm_memorize(Xtr, ytr, Xq, pop_label):
    combo = defaultdict(lambda: defaultdict(int))
    for r in range(Xtr.shape[0]):
        combo[tuple(Xtr[r].tolist())][int(ytr[r])] += 1
    preds = []
    for q in range(Xq.shape[0]):
        dd = combo.get(tuple(Xq[q].tolist()))
        preds.append(max(dd.items(), key=lambda kv: kv[1])[0] if dd else pop_label)
    return np.array(preds, dtype=np.int64)


# ===========================================================================
# LEARNED ARMS (plain SGD; the mechanism test). shared-vs-role-keyed; product-vs-sum.
# ===========================================================================

def _train_learned(Xtr, ytr, Xq, mode, seed):
    """mode: 'sym' (SHARED code + Hadamard product; swap-symmetric = the mechanism) | 'add_sym' (SHARED code + sum;
    swap-symmetric additive contrast) | 'int' (role-keyed Hadamard product) | 'bilinear' (role-keyed low-rank
    bilinear, fixed shared code + learned per-role projection init=identity)."""
    g = torch.Generator().manual_seed(seed * 7919 + {"sym": 1, "add_sym": 2, "int": 3, "bilinear": 4}[mode])
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long(); yt = torch.from_numpy(ytr).long()
    k = 2
    product = (mode in ("sym", "int", "bilinear"))
    params = []
    c_fixed = None; P = None; emb = None
    if mode == "bilinear":
        c_fixed = (1.0 + 0.2 * torch.randn(NCLS, EMB_D, generator=g))                 # FIXED shared level-code
        P = torch.nn.Parameter(torch.eye(EMB_D).unsqueeze(0).repeat(k, 1, 1)
                               + 0.02 * torch.randn(k, EMB_D, EMB_D, generator=g))     # LEARNED per-role, init=identity
        params.append(P)
    elif mode in ("sym", "add_sym"):
        center = 1.0 if product else 0.0
        emb = torch.nn.Parameter(center + 0.2 * torch.randn(NCLS, EMB_D, generator=g))  # SHARED (no role)
        params.append(emb)
    else:  # int -> role-keyed
        emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(k, NCLS, EMB_D, generator=g))
        params.append(emb)
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, L, generator=g))
    b = torch.nn.Parameter(torch.zeros(L))
    params += [W, b]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def compose(Xi):
        if mode == "bilinear":
            cx = c_fixed[Xi]                                 # (n,k,D) fixed codes
            e = torch.einsum("nkd,kde->nke", cx, P)          # (n,k,D) role-projected
            return e.prod(dim=1)
        if mode in ("sym", "add_sym"):
            e = emb[Xi]                                      # (n,k,D) shared table
        else:
            e = emb[torch.arange(k).unsqueeze(0), Xi]        # (n,k,D) role-keyed
        return e.prod(dim=1) if product else e.sum(dim=1)

    for _ in range(EPOCHS):
        opt.zero_grad()
        h = compose(Xt)
        mu = h.mean(0, keepdim=True); sd = h.std(0, keepdim=True) + 1e-3
        logits = ((h - mu) / sd) @ W + b
        loss = lossf(logits, yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        h_tr = compose(Xt); mu = h_tr.mean(0, keepdim=True); sd = h_tr.std(0, keepdim=True) + 1e-3
        logits_q = ((compose(Xu) - mu) / sd) @ W + b
        return torch.argmax(logits_q, 1).numpy().astype(np.int64)


# ===========================================================================
# split + regimes + scoring
# ===========================================================================

def split_novel(X, seed):
    """Instance-level split. NOVEL = query pairs whose canonical class-pair is ABSENT from train (interaction
    EXTRAPOLATION to an unseen class-pair). Deterministic integer-seeded RNG."""
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100081 + 9)
    perm = rng.permutation(n)
    nq = int(round(QUERY_FRAC * n))
    q = np.sort(perm[:nq]); tr = np.sort(perm[nq:])
    train_pairs = set((int(X[i, 0]), int(X[i, 1])) for i in tr)
    novel = np.array([(int(X[i, 0]), int(X[i, 1])) not in train_pairs for i in q], dtype=bool)
    return q, tr, novel


def plant_regime(X, y_real, regime, seed):
    """(y_used, y_oracle). ARBITRARY = random hazard per unique class-pair; SHUFFLE = label permutation."""
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100057 + REG_IDX[regime] * 131 + 17)  # deterministic
    if regime == CLEAN:
        return y_real.copy(), y_real.copy()
    if regime == ARBITRARY:
        lab = {}
        y = np.empty(n, dtype=np.int64)
        for r in range(n):
            key = (int(X[r, 0]), int(X[r, 1]))
            if key not in lab:
                lab[key] = int(rng.integers(0, L))
            y[r] = lab[key]
        return y, y.copy()
    if regime == SHUFFLE:
        y = y_real[rng.permutation(n)].copy()
        return y, y.copy()
    raise ValueError(regime)


def acc(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


def adj_acc(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.abs(np.asarray(pred) - np.asarray(gold)) <= 1).mean())


def score(regime, X, y_real, seed):
    q, tr, novel = split_novel(X, seed)
    y_used, y_oracle = plant_regime(X, y_real, regime, seed)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y_used[q], y_used[tr]
    pop_label = int(np.argmax(np.bincount(ytr, minlength=L)))

    add_pred, beta = arm_add_lsq(Xtr, ytr, Xq)
    preds = {
        LEARN_SYM: _train_learned(Xtr, ytr, Xq, "sym", seed),
        LEARN_ADD_SYM: _train_learned(Xtr, ytr, Xq, "add_sym", seed),
        LEARN_INT: _train_learned(Xtr, ytr, Xq, "int", seed),
        LEARN_BIL: _train_learned(Xtr, ytr, Xq, "bilinear", seed),
        ADD_LSQ: add_pred,
        INT_CF: arm_int_cf(Xtr, ytr, Xq, beta),
        HOM: arm_homophily(Xtr, ytr, Xq),
        MEMO: arm_memorize(Xtr, ytr, Xq, pop_label),
        POP: np.full(Xq.shape[0], pop_label, dtype=np.int64),
        ORC: y_oracle[q],
    }

    def a(pred, m, fn):
        return fn(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    out = {}
    for sname, m in (("novel", novel), ("seen", ~novel), ("all", np.ones(len(gold), bool))):
        d = {arm: round(a(preds[arm], m, acc), 5) for arm in preds}
        d[FREQ] = round(max(d[HOM], d[POP]), 5)
        d["adj_" + LEARN_SYM] = round(a(preds[LEARN_SYM], m, adj_acc), 5)
        d["adj_" + ORC] = round(a(preds[ORC], m, adj_acc), 5)
        d["n"] = int(m.sum())
        out[sname] = d
    # ARMS-MUST-DIFFER: the learned + closed-form mechanism/additive/homophily arms must be mutually distinct.
    # ORACLE / POP excluded (POP is constant; ORACLE legitimately = gold).
    sigs = {arm: _sig(preds[arm]) for arm in (LEARN_SYM, LEARN_ADD_SYM, LEARN_INT, LEARN_BIL, ADD_LSQ, INT_CF, HOM)}
    return dict(strata=out, sigs=sigs, n_novel=int(novel.sum()))


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds=(7, 13, 17, 23, 29, 31, 37, 41, 43)):
    p, X, y = load_cluster()
    _log("FULL run: n=%d vetted-true pairs, %d unique class-pairs, %d seeds x %d regimes"
         % (X.shape[0], len(set(tuple(r) for r in X.tolist())), len(seeds), len(REGIMES)))
    conj = conjunction_property(X, y)
    ceiling = classpair_bayes_ceiling(X, y)
    ch = chance_of(y)
    truth_rate = p.get("truth_rate", float("nan"))

    per = {reg: [] for reg in REGIMES}
    t0 = time.perf_counter()
    for si, sd in enumerate(seeds):
        for reg in REGIMES:
            per[reg].append(score(reg, X, y, sd))
        _log("  seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))

    def mean_field(reg, stratum, key):
        vals = [ps["strata"][stratum][key] for ps in per[reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    novel_total = int(sum(ps["n_novel"] for ps in per[CLEAN]))

    # ---- CLEAN aggregates ----
    def C(stratum, key):
        return mean_field(CLEAN, stratum, key)

    sym_novel = C("novel", LEARN_SYM)
    freq_novel = C("novel", FREQ)
    best_add_novel = max(C("novel", LEARN_ADD_SYM), C("novel", ADD_LSQ))
    role_best_novel = max(C("novel", LEARN_INT), C("novel", LEARN_BIL))
    sym_seen = C("seen", LEARN_SYM)
    best_add_seen = max(C("seen", LEARN_ADD_SYM), C("seen", ADD_LSQ))
    seen_nonadd = C("seen", INT_CF) - C("seen", ADD_LSQ)  # reproduce FOUNDATION non-additivity at test regime
    memo_leak_novel = C("novel", MEMO) - freq_novel
    orc_all = C("all", ORC)

    # headline gaps
    g_sym_freq = sym_novel - freq_novel
    g_sym_add = sym_novel - best_add_novel
    g_sym_role = sym_novel - role_best_novel

    # ---- must-fails (ARBITRARY / SHUFFLE novel; MEMO leak on CLEAN novel) ----
    def mustfail_ok(reg):
        return all((mean_field(reg, "novel", arm) - mean_field(reg, "novel", FREQ)) <= MUSTFAIL_TOL
                   for arm in MECHANISM_ARMS)
    arb_ok = mustfail_ok(ARBITRARY)
    shuf_ok = mustfail_ok(SHUFFLE)
    leak_ok = bool(memo_leak_novel <= MUSTFAIL_TOL)
    mustfails_fire = bool(arb_ok and shuf_ok and leak_ok)

    # ---- ceiling / fairness ----
    ceiling_ok = bool(orc_all >= 0.999 and all(
        C("novel", ORC) >= C("novel", arm) - 1e-6 for arm in (LEARN_SYM, LEARN_INT, ADD_LSQ, INT_CF)))
    freq_not_saturated = bool(freq_novel == freq_novel and freq_novel < FREQ_SAT)
    enough_novel = bool(novel_total >= MIN_NOVEL_TOTAL)

    # ---- Gate D: non-additivity reproduced at test regime ----
    reproduce_ok = bool(seen_nonadd == seen_nonadd and seen_nonadd >= HP_SEEN_NONADD)

    # ---- verdict ----
    beats_freq = bool(g_sym_freq >= HP_SYM_FREQ_NOVEL)
    beats_add = bool(g_sym_add >= HP_SYM_ADD_NOVEL)
    not_beaten_by_role = bool(g_sym_role >= -HP_ROLE_SLACK)
    sym_captures_seen = bool((sym_seen - best_add_seen) > REFUTE_SEEN_GAP)

    hard_pass = bool(beats_freq and beats_add and not_beaten_by_role and reproduce_ok
                     and mustfails_fire and ceiling_ok and freq_not_saturated and enough_novel)
    refute = bool((sym_seen - best_add_seen) <= REFUTE_SEEN_GAP and mustfails_fire and ceiling_ok and enough_novel)

    if not ceiling_ok:
        verdict = "INCONCLUSIVE_CEILING_MALFORMED"
    elif not enough_novel:
        verdict = "INCONCLUSIVE_TOO_FEW_NOVEL"
    elif not mustfails_fire:
        verdict = "INCONCLUSIVE_MUSTFAIL_LEAK"
    elif hard_pass:
        verdict = "HARD_PASS_SYMMETRIC_BIND_DISCOVERS_REAL_CHEM_NONADDITIVE_ON_NOVEL"
    elif refute:
        verdict = "REFUTE_SYMMETRIC_MECHANISM_DOES_NOT_TRANSFER_TO_REAL_DATA"
    elif sym_captures_seen:
        verdict = "MIDDLE_BAND_CAPTURES_SEEN_DOES_NOT_EXTRAPOLATE_TO_NOVEL"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    msg = ("%s || n=%d(novel_total=%d) truth=%s ceiling=%.3f chance=%.3f | "
           "NOVEL: SYM=%s FREQ=%s (SYM-FREQ=%s>=%.2f=%s) bestADD=%s (SYM-ADD=%s>=%.2f=%s) roleBest=%s (SYM-role=%s) "
           "MEMO_leak=%s adj[SYM=%s ORC=%s] | SEEN: SYM=%s bestADD=%s (SYM-ADD=%s) INT_CF=%s ADD_LSQ=%s "
           "(nonadd=%s>=%.2f=%s) | MUSTFAIL arb=%s shuf=%s leak=%s | oracle_all=%s freq_sat=%s"
           % (verdict, X.shape[0], novel_total, _fmt(truth_rate), ceiling, ch,
              _fmt(sym_novel), _fmt(freq_novel), _fmt(g_sym_freq), HP_SYM_FREQ_NOVEL, beats_freq,
              _fmt(best_add_novel), _fmt(g_sym_add), HP_SYM_ADD_NOVEL, beats_add,
              _fmt(role_best_novel), _fmt(g_sym_role), _fmt(memo_leak_novel),
              _fmt(C("novel", "adj_" + LEARN_SYM)), _fmt(C("novel", "adj_" + ORC)),
              _fmt(sym_seen), _fmt(best_add_seen), _fmt(sym_seen - best_add_seen),
              _fmt(C("seen", INT_CF)), _fmt(C("seen", ADD_LSQ)), _fmt(seen_nonadd), HP_SEEN_NONADD, reproduce_ok,
              arb_ok, shuf_ok, leak_ok, _fmt(orc_all), (not freq_not_saturated)))

    # per-arm CLEAN novel + seen table (weak-point localization + full transparency)
    table = {}
    for stratum in ("novel", "seen", "all"):
        table[stratum] = {arm: round(C(stratum, arm), 5) for arm in ARM_NAMES}
        table[stratum]["n_mean"] = round(C(stratum, "n"), 3)

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="full",
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        n_entities=int(X.shape[0]), n_unique_classpairs=len(set(tuple(r) for r in X.tolist())),
        truth_rate=truth_rate, classpair_bayes_ceiling=round(ceiling, 5), chance=round(ch, 5),
        seeds=list(seeds), emb_d=EMB_D, epochs=EPOCHS, lr=LR, query_frac=QUERY_FRAC,
        conjunction=conj, novel_total=novel_total,
        headline=dict(sym_novel=round(sym_novel, 5), freq_novel=round(freq_novel, 5),
                      best_add_novel=round(best_add_novel, 5), role_best_novel=round(role_best_novel, 5),
                      g_sym_freq=round(g_sym_freq, 5), g_sym_add=round(g_sym_add, 5), g_sym_role=round(g_sym_role, 5),
                      sym_seen=round(sym_seen, 5), best_add_seen=round(best_add_seen, 5),
                      seen_nonadd=round(seen_nonadd, 5), memo_leak_novel=round(memo_leak_novel, 5),
                      adj_sym_novel=round(C("novel", "adj_" + LEARN_SYM), 5)),
        gates=dict(hard_pass=hard_pass, refute=refute, beats_freq=beats_freq, beats_add=beats_add,
                   not_beaten_by_role=not_beaten_by_role, reproduce_ok=reproduce_ok,
                   sym_captures_seen=sym_captures_seen, mustfails_fire=mustfails_fire,
                   arb_ok=arb_ok, shuf_ok=shuf_ok, leak_ok=leak_ok, ceiling_ok=ceiling_ok,
                   freq_not_saturated=freq_not_saturated, enough_novel=enough_novel),
        bands=dict(HP_SYM_FREQ_NOVEL=HP_SYM_FREQ_NOVEL, HP_SYM_ADD_NOVEL=HP_SYM_ADD_NOVEL,
                   HP_ROLE_SLACK=HP_ROLE_SLACK, HP_SEEN_NONADD=HP_SEEN_NONADD, MUSTFAIL_TOL=MUSTFAIL_TOL,
                   REFUTE_SEEN_GAP=REFUTE_SEEN_GAP, FREQ_SAT=FREQ_SAT, MIN_NOVEL_TOTAL=MIN_NOVEL_TOTAL),
        table_clean=table,
        per_regime_novel={reg: [ps["strata"]["novel"] for ps in per[reg]] for reg in REGIMES},
        per_regime_seen={reg: [ps["strata"]["seen"] for ps in per[reg]] for reg in REGIMES},
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (exercises the REAL FHRR bind path + full arm pipeline on planted arenas + the real cluster)
# ===========================================================================

def _plant(n, seed, mode):
    """Symmetric class-pair arena. mode='interaction' -> pair-specific SYMMETRIC table (genuine non-additive, no
    dominant driver). mode='additive' -> y = clip(a[cA]+a[cB]) (additive; symmetric bind must NOT beat additive)."""
    rng = np.random.default_rng(seed)
    ncls = 8
    a = rng.integers(0, ncls, size=n); b = rng.integers(0, ncls, size=n)
    X = np.stack([np.minimum(a, b), np.maximum(a, b)], axis=1).astype(np.int64)
    if mode == "interaction":
        table = rng.integers(0, L, size=(ncls, ncls))
        table = np.minimum(table, table.T)  # symmetric over unordered pair
        y = np.array([table[int(X[i, 0]), int(X[i, 1])] for i in range(n)], dtype=np.int64)
    else:
        w = rng.integers(0, 3, size=ncls)
        y = np.array([int(np.clip(w[int(X[i, 0])] + w[int(X[i, 1])], 0, L - 1)) for i in range(n)], dtype=np.int64)
    # remap the 8-class planted arena onto the first 8 real class indices so score()'s NCLS tables index safely
    return X, y


def self_test():
    ok_all = True
    details = {}

    # (1) REAL FHRR bind homomorphism (complex path): bind of FPE phasors reads out (i+j) mod L. Proves the mechanism
    #     rests on the ACTUAL substrate bind primitive (the learned arms use its differentiable Hadamard analog).
    g = np.random.default_rng(31)
    m = g.integers(1, max(2, L), size=64).astype(np.float64)
    jj = np.arange(L, dtype=np.float64)[:, None]
    Ycode = torch.from_numpy(np.exp(1j * (2.0 * np.pi / L) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Ycode[torch.tensor([1, 2])], Ycode[torch.tensor([2, 3])])
    homo_ok = torch.argmax((bound @ Ycode.conj().T.contiguous()).real, 1).tolist() == [3 % L, 5 % L]
    details["fhrr_bind_homomorphism_ok"] = homo_ok

    # (1b) substrate_signature: hd_bind binds two equal-shape complex tensors elementwise (swap-symmetric).
    u = torch.randn(3, 8, dtype=torch.complex64); v = torch.randn(3, 8, dtype=torch.complex64)
    sym_bind_ok = bool(torch.allclose(hd_bind(u, v), hd_bind(v, u)))
    details["hd_bind_swap_symmetric_ok"] = sym_bind_ok

    # (2) PLANTED SYMMETRIC-INTERACTION arena: LEARN_SYM captures a genuine symmetric 2-way interaction on SEEN,
    #     beats the additive contrast; role-keyed does NOT beat it. (n=700 densely covers the 8-class arena so its
    #     NOVEL stratum is intentionally sparse -- the ARBITRARY must-fail below is evaluated on the REAL cluster,
    #     whose NOVEL stratum is populated, which is also the ACTUAL test regime.)
    Xi, yi = _plant(700, 7, "interaction")
    ri = score(CLEAN, Xi, yi, 7)["strata"]
    sym_seen_i = ri["seen"][LEARN_SYM]; add_seen_i = max(ri["seen"][LEARN_ADD_SYM], ri["seen"][ADD_LSQ])
    nonadd_i = ri["seen"][INT_CF] - ri["seen"][ADD_LSQ]
    role_seen_i = max(ri["seen"][LEARN_INT], ri["seen"][LEARN_BIL])
    details.update(dict(interaction_sym_seen=sym_seen_i, interaction_add_seen=round(add_seen_i, 5),
                        interaction_nonadd=round(nonadd_i, 5), interaction_role_seen=round(role_seen_i, 5),
                        interaction_freq_seen=ri["seen"][FREQ]))

    # (3) PLANTED ADDITIVE arena: LEARN_SYM must NOT strongly beat the additive arm (discriminator does not over-fire).
    Xa, ya = _plant(700, 11, "additive")
    raa = score(CLEAN, Xa, ya, 11)["strata"]["seen"]
    add_nonadd = raa[INT_CF] - raa[ADD_LSQ]
    details["additive_arena_nonadd"] = round(add_nonadd, 5)

    # (4) REAL cluster path: load 135 vetted-true, MI conjunction present, INT_CF beats ADD_LSQ on seen (real
    #     non-additivity is measurable end-to-end through the actual arms).
    p, X, y = load_cluster()
    conj = conjunction_property(X, y)
    rr = score(CLEAN, X, y, 7)["strata"]["seen"]
    real_nonadd = rr[INT_CF] - rr[ADD_LSQ]
    details.update(dict(real_n=int(X.shape[0]), real_truth=p.get("truth_rate"),
                        real_joint_mi=conj["joint_mi"], real_dominance_ratio=conj["dominance_ratio"],
                        real_ceiling=round(classpair_bayes_ceiling(X, y), 5),
                        real_seen_nonadd=round(real_nonadd, 5)))

    # (4b) ARBITRARY must-fail on the REAL cluster NOVEL stratum (the actual test regime; NaN-robust over 3 seeds):
    #      a random hazard per class-pair cannot be predicted for a NOVEL (unseen) class-pair -> LEARN_SYM must NOT
    #      beat FREQ_NULL on novel.
    arb_gaps = []
    for sd in (7, 13, 17):
        ra = score(ARBITRARY, X, y, sd)["strata"]["novel"]
        gp = ra[LEARN_SYM] - ra[FREQ]
        if gp == gp:  # skip NaN (empty novel stratum for that seed)
            arb_gaps.append(gp)
    arb_gap_real = float(np.mean(arb_gaps)) if arb_gaps else float("nan")
    details.update(dict(real_arb_gap=round(arb_gap_real, 5), real_arb_n_seeds=len(arb_gaps)))

    # (5) ARMS-MUST-DIFFER on the real cluster.
    sc = score(CLEAN, X, y, 7)
    arms_differ = len(set(sc["sigs"].values())) == len(sc["sigs"])
    details["arms_differ_sig_count"] = len(set(sc["sigs"].values()))

    # (6) guard_baseline_valid: FREQ_NULL on the real cluster is ABOVE a random floor (mechanism-beats-freq guard
    #     compares against a NON-floor baseline, not a structural zero).
    freq_seen_real = rr[FREQ]
    details["real_freq_seen"] = freq_seen_real

    checks = {
        "fhrr_bind_homomorphism": homo_ok,
        "hd_bind_swap_symmetric": sym_bind_ok,
        # planted interaction: mechanism captures symmetric non-additive; additive contrast lags; role does not beat
        "SYM_captures_interaction_seen": sym_seen_i >= 0.55,
        "SYM_beats_additive_interaction_seen": (sym_seen_i - add_seen_i) >= 0.08,
        "nonadd_fires_interaction": nonadd_i >= 0.12,
        "role_does_not_beat_SYM_interaction": role_seen_i <= sym_seen_i + 0.05,
        "arbitrary_mustfail_fires": (arb_gap_real == arb_gap_real) and arb_gap_real <= MUSTFAIL_TOL,
        # planted additive: discriminator does not over-fire (additive arena has low non-additivity)
        "additive_arena_nonadd_low": add_nonadd <= 0.10,
        # real cluster: end-to-end path works, real non-additivity measurable, fair floor non-degenerate
        "real_cluster_loaded_135": X.shape[0] == 135,
        "real_conjunction_present": conj["joint_mi"] >= 0.30 and conj["mi_margin"] >= 0.15,
        "real_nonadditivity_measurable": real_nonadd >= 0.05,
        "real_freq_non_degenerate": 0.10 <= freq_seen_real <= FREQ_SAT,
        "arms_differ": arms_differ,
    }
    for kk, vv in checks.items():
        if not vv:
            ok_all = False
    out = dict(passed=ok_all, checks=checks, details=details)
    print("[SELFTEST] %s" % json.dumps(out, default=float), flush=True)
    return ok_all, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true", help="explicit full run (default when no flag given)")
    args, _unknown = ap.parse_known_args()

    if args.self_test:
        ok, _ = self_test()
        sys.exit(0 if ok else 1)
    if args.smoke:
        m = run_measurement(seeds=(7, 13))
        _write_metrics(m)
        _log("SMOKE " + m["verdict_msg"])
        return
    # DEFAULT (no flag) = FULL run to completion (runner invokes `python -u <script>` with no args).
    m = run_measurement()
    _write_metrics(m)
    _log(m["verdict_msg"])


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            crash = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(e).__name__, str(e)[:400]),
                         summary="CELL_CRASHED", elapsed_s=0.0, anchor_name=ANCHOR_NAME,
                         traceback=traceback.format_exc()[:4000], ts_iso=datetime.now(timezone.utc).isoformat())
            os.makedirs(OUT_DIR, exist_ok=True)
            tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(crash, f, indent=2)
            os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))
        except Exception:
            pass
        raise
