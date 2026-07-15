"""ORDINAL_MAGNITUDE_ENCODING_VS_COMBINATION (encoding-gap vs combination-rule-gap fork resolver).

CONTEXT (self-contained; prior results inlined so no cross-cell import is needed -> portable to the remote runner):
  A real 191-animal ordinal cluster (metabolic_rate target, 4 constituent scales) was shown to be readable by a
  MONOTONE constructable code (thermometer/additive compose + TRAIN-fit quantile-threshold readout) at CLEAN-novel
  top1 ~0.573 with LEARNED non-negative per-constituent weights (equal-weight ~0.395), vs a FREQ/HOMOPHILY null of
  ~0.511 -- i.e. the monotone code reads the ordinal conjunction but beats frequency only MODESTLY (+0.062). The
  encoding is crude in one documented way: it bins magnitude LINEAR-UNIFORM, whereas every biological magnitude axis
  surveyed (parietal LIP summation coding, human IPS log-Gaussian tuning, the mental number line) is LOG/Weber-Fechner
  COMPRESSIVE. Separately, the combiner uses FIXED learned global weights, whereas the brain's default magnitude
  combiner is reliability-weighted linear averaging (Ernst & Banks 2002 Bayesian cue integration).

FORK THIS CELL RESOLVES: is the residual bottleneck the ENCODING (uniform vs log/Weber-compressed level spacing) or
the COMBINATION RULE (fixed learned weights vs per-cue reliability weighting)? We hold the mechanism, the split, the
FREQ_NULL fair baseline, the ARBITRARY/SHUFFLE must-fails, and the seeds IDENTICAL, and change ONLY (Anchor 1) the
per-level magnitude spacing of the encoding, or (Anchor 2) the combination rule, so each delta isolates one lever.

ANCHOR 1 (ENCODING): re-run the LEARNED-WEIGHT monotone arm with the ordinal LEVELS mapped through a compressive
value function before additive composition, replacing the linear uniform spacing {0,1,2,3,4}. Because a nonlinear
per-level map changes the ordering of MULTI-constituent composed sums (e.g. log: (2,2) outranks (4,0) though the
linear sum ties), this is a genuine encoding-density change, not an absorbed monotone reparameterization. Headline
encoding = LOG (Weber-Fechner v_k=log(1+k)); POWER (Stevens v_k=k^0.5) and QUANTILE (train-empirical density) are
reported as diagnostic siblings (all pre-registered by the handoff as "log-spaced / empirical-quantile / Weber-
scaled"). We do NOT iterate further bin variants beyond this fixed set.

ANCHOR 2 (COMBINATION): replace the fixed learned global weights with per-instance reliability-weighted linear cue
integration (Ernst-Banks). Each constituent i emits a per-level estimate mu[i,l]=E_train[y|X_i=l] with reliability
r[i,l]=1/(Var_train[y|X_i=l]+prior); the composed estimate is the inverse-variance-weighted average
sum_i r[i,x_i] mu[i,x_i] / sum_i r[i,x_i], read out through the IDENTICAL quantile-threshold family (uniform level
encoding held fixed, so the delta isolates the combination rule). Localization: does it CLOSE a specific subset of
the learned-weight arm's failure cases (net localized improvement), or just move the global average?

ARMS: MONO_WEIGHT (learned non-neg weights; the 0.573 baseline reproduced under uniform encoding) x {uniform, log,
power, quantile} encodings ; MONO_THERM (equal weight, uniform) ; RELIABILITY (Anchor 2) ; FREQ_NULL =
max(HOMOPHILY_COND, POP) ; MEMORIZE ; POP ; ORACLE.
MUST-FAILS: ARBITRARY (random non-monotone table over the 4 constituents) + SHUFFLE (freq-preserving label
permutation) -- neither may lift ANY monotone/reliability arm above FREQ_NULL (gap <= tol).
HEADLINE (NOVEL stratum, top1 acc; chance=1/L=0.20; NOT tuned): Anchor1 = MONO_WEIGHT_log_novel - MONO_WEIGHT_uniform
_novel (on animals; foods reported too). Anchor2 = fraction of learned-weight failure cases closed by RELIABILITY.

PRE-REGISTERED BANDS (fixed BEFORE running; from notes/exp_dev_handoff_research_ordinal_magnitude_coding_bestinclass
_2026-07-14.md, diffed against the 0.573 learned-weight baseline):
  ANCHOR 1 (log encoding vs uniform baseline):
    HARD_PASS : MONO_WEIGHT_log_novel improves by >= 0.05 absolute over MONO_WEIGHT_uniform_novel (animals >= ~0.62),
                with must-fails still firing (ARB/SHUF gap <= 0.05). Genuine encoding improvement.
    MIDDLE_BAND: delta in [0.02, 0.05) -- real but modest refinement, not a headline win.
    HARD_FAIL : delta < 0.02 (either direction) -- linear-uniform binning was NOT the active bottleneck; do NOT
                iterate further bin-edge variants; the additive regime is (data/frequency)-capped on this axis.
  ANCHOR 2 (reliability weighting vs fixed learned weights):
    HARD_PASS : closes >= 30% of the learned-weight arm's CLEAN-novel failure cases with no net new failures
                (new_failures <= closed), must-fails firing. Net LOCALIZED improvement.
    MIDDLE_BAND: global-average novel acc improves by >= 0.02 but closed_frac < 0.30 (diffuse gain).
    HARD_FAIL : closed_frac <= 0.10 (failure-case overlap with baseline >= 90%) -- fixed weights were not the
                bottleneck; the gap is upstream in the per-constituent encoding.
  CORRECTNESS GATES (non-negotiable, gate any PASS): baseline MONO_WEIGHT_uniform on animals reproduces 0.573 +/- 0.06
    (else REPRODUCTION_MISMATCH) ; ARBITRARY + SHUFFLE must-fails fire for every real arm ; ORACLE ceiling >= arm.

Glass-box, NO LLM at measurement time. CPU-only. ASCII-only. Deterministic given seed (fixed per-regime salts; no
PYTHONHASHSEED-dependent hashing). No bare except; except SystemExit before except Exception. Reuses on-disk clusters
(data/foundation_clusters/{animals,foods}_ordinal_conjunction_v1.json); NO generation.
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

from hdlab.binding import bind as hd_bind  # noqa: E402  # REAL substrate FHRR bind (exercised in self-test only)

ANCHOR_NAME = "ordinal_magnitude_encoding_vs_combination_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
CLUSTER_DIR = os.path.join(_REPO, "data", "foundation_clusters")
CLUSTERS = {
    "animals": os.path.join(CLUSTER_DIR, "animals_ordinal_conjunction_v1.json"),
    "foods": os.path.join(CLUSTER_DIR, "foods_ordinal_conjunction_v1.json"),
}
# reproduction anchor: prior-session animals CLEAN-novel learned-weight top1
REPRO_TARGET_ANIMALS = 0.573
REPRO_TOL = 0.06

L = 5  # ordinal levels per attribute (0..4); both clusters use L=5

# ---- regimes ----
CLEAN = "CLEAN_REAL"
ARBITRARY = "ARBITRARY"
SHUFFLE = "SHUFFLE"
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]
REG_SALT = {CLEAN: 0, ARBITRARY: 1, SHUFFLE: 2}  # deterministic (no PYTHONHASHSEED-dependent hash(regime))

ENCODINGS = ["uniform", "log", "power", "quantile"]

# ---- pre-registered bands ----
A1_HARD_PASS = 0.05
A1_MIDDLE = 0.02
A2_CLOSE_FRAC = 0.30
A2_MIDDLE_GLOBAL = 0.02
A2_OVERLAP_FAIL = 0.10   # closed_frac <= this => HARD_FAIL
MUSTFAIL_TOL = 0.05
SEEDS = (7, 13, 17, 23, 29)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


# ===========================================================================
# CLUSTER LOADING (generic; reads scales/target from the artifact itself)
# ===========================================================================

def load_cluster(path):
    with open(path, "r", encoding="utf-8") as f:
        p = json.load(f)
    scales = p["scales"]
    constituents = list(scales.keys())
    target = p["target"]
    target_scale = p["target_scale"]
    rows = p["rows"]
    idx = {k: {v: i for i, v in enumerate(scales[k])} for k in constituents}
    tidx = {v: i for i, v in enumerate(target_scale)}
    X = np.array([[idx[k][r[k]] for k in constituents] for r in rows], dtype=np.int64)
    y = np.array([tidx[r[target]] for r in rows], dtype=np.int64)
    meta = dict(constituents=constituents, target=target, n_entities=p.get("n_entities", len(rows)),
                truth_rate=p.get("truth_rate", float("nan")), Lc=int(p.get("L", L)))
    return meta, X, y


def mutual_info(a, b, base=2.0):
    n = len(a)
    if n == 0:
        return 0.0
    pa = defaultdict(float); pb = defaultdict(float); pab = defaultdict(float)
    for x, z in zip(a, b):
        pa[x] += 1.0 / n; pb[z] += 1.0 / n; pab[(x, z)] += 1.0 / n
    mi = 0.0
    for (x, z), pxz in pab.items():
        mi += pxz * math.log(pxz / (pa[x] * pb[z]) + 1e-30, base)
    return max(0.0, mi)


def conjunction_property(X, y, Lv):
    """Single-relation MI(y;X_i) vs joint MI(y; full combo). Deterministic combo id = sum_i x_i * Lv^i."""
    single = [mutual_info(X[:, i], y) for i in range(X.shape[1])]
    weights = (Lv ** np.arange(X.shape[1], dtype=np.int64))
    combo = (X * weights[None, :]).sum(axis=1)
    joint = mutual_info(combo, y)
    best_single = max(single) if single else 0.0
    ratio = (best_single / joint) if joint > 1e-9 else float("nan")
    return dict(single_mi=[round(s, 4) for s in single], best_single_mi=round(best_single, 4),
                joint_mi=round(joint, 4), mi_margin=round(joint - best_single, 4),
                dominance_ratio=round(ratio, 4) if ratio == ratio else ratio)


# ===========================================================================
# ENCODING (per-level magnitude value function; the Anchor-1 lever)
# ===========================================================================

def level_value_map(mode, Lv, Xtr=None):
    """Return a length-Lv vector mapping ordinal level k -> composed magnitude value.
    'uniform' = linear {0..Lv-1} (the baseline); 'log'/'power'/'quantile' are compressive (Weber-shaped).
    Normalized to [0, Lv-1] by a GLOBAL affine (cosmetic; the encoding acts only through its nonlinear SHAPE)."""
    k = np.arange(Lv, dtype=np.float64)
    if mode == "uniform":
        v = k.copy()
    elif mode == "log":                 # Weber-Fechner compressive
        v = np.log1p(k)
    elif mode == "power":               # Stevens compressive exponent 0.5
        v = np.power(k, 0.5)
    elif mode == "quantile":            # train-empirical density-equalizing (pooled over constituents; no leakage)
        if Xtr is None:
            raise ValueError("quantile encoding requires Xtr")
        cnt = np.bincount(Xtr.reshape(-1), minlength=Lv).astype(np.float64)
        cum = np.cumsum(cnt) / max(1.0, cnt.sum())
        prev = np.concatenate([[0.0], cum[:-1]])
        v = (prev + cum) / 2.0          # midpoint cumulative frequency
    else:
        raise ValueError(mode)
    v = v - v.min()
    mx = v.max()
    if mx > 1e-12:
        v = v * ((Lv - 1) / mx)
    return v


def encode(X, vmap):
    return vmap[X].astype(np.float64)


# ===========================================================================
# MONOTONE ARMS (constructable code + TRAIN-fit quantile-threshold readout)
# Ported verbatim from the prior-session harness so the 0.573 baseline reproduces exactly under 'uniform'.
# ===========================================================================

def _quantile_thresholds(s_tr, y_tr, Lv):
    order = np.argsort(s_tr, kind="stable")
    s_sorted = s_tr[order]
    counts = np.bincount(y_tr, minlength=Lv).astype(np.float64)
    frac = np.cumsum(counts) / max(1.0, counts.sum())
    n = len(s_sorted)
    thr = []
    for lv in range(Lv - 1):
        q = frac[lv]
        idx = min(n - 1, int(round(q * n)))
        thr.append(s_sorted[idx])
    return np.array(thr, dtype=np.float64)


def _predict_thresh(s, thr):
    return np.array([int((si >= thr).sum()) for si in s], dtype=np.int64)


def arm_mono_therm(Xq_enc, Xtr_enc, ytr, Lv):
    """Equal-weight monotone: composed magnitude = SUM of encoded levels; quantile-threshold readout."""
    s_tr = Xtr_enc.sum(axis=1)
    s_q = Xq_enc.sum(axis=1)
    thr = _quantile_thresholds(s_tr, ytr, Lv)
    return _predict_thresh(s_q, thr)


def arm_mono_weight(Xq_enc, Xtr_enc, ytr, Lv, n_iter=300, lr=0.15):
    """Learned non-negative per-constituent weights (softplus), fit on TRAIN to maximize corr(composed, target rank),
    then quantile-threshold readout. Deterministic (seeded). This is the 0.573 baseline arm under 'uniform' encoding."""
    d = Xtr_enc.shape[1]
    rng = np.random.default_rng(0)
    raw = rng.normal(0.0, 0.1, size=d)
    Xtrf = Xtr_enc.astype(np.float64)
    yr = (ytr.astype(np.float64) - ytr.mean())
    yr = yr / (yr.std() + 1e-9)
    for _ in range(n_iter):
        sig = 1.0 / (1.0 + np.exp(-raw))
        g_s = -(yr) / len(yr)
        g_w = Xtrf.T @ g_s
        raw = raw - lr * (g_w * sig)
    w = np.log1p(np.exp(raw))
    s_tr = Xtrf @ w
    s_q = Xq_enc.astype(np.float64) @ w
    thr = _quantile_thresholds(s_tr, ytr, Lv)
    return _predict_thresh(s_q, thr), w


# ===========================================================================
# ANCHOR-2 ARM: reliability-weighted linear cue integration (Ernst-Banks)
# ===========================================================================

def arm_reliability(Xq, Xtr, ytr, Lv):
    """Per-(constituent, level) estimate mu=E_train[y|X_i=l] with inverse-variance reliability r=1/(Var+prior).
    Composed estimate = sum_i r[i,x_i]*mu[i,x_i] / sum_i r[i,x_i]; quantile-threshold readout (uniform level indices;
    the encoding is HELD FIXED so the delta isolates the combination rule)."""
    d = Xtr.shape[1]
    yg_mean = float(ytr.mean())
    yg_var = float(ytr.var())
    prior = 0.25  # Bayesian variance floor (levels 0..4 -> unit spacing; ~0.5 sd prior)
    mu = np.zeros((d, Lv), dtype=np.float64)
    rel = np.zeros((d, Lv), dtype=np.float64)
    for i in range(d):
        for l in range(Lv):
            m = (Xtr[:, i] == l)
            c = int(m.sum())
            if c >= 2:
                yi = ytr[m].astype(np.float64)
                mu[i, l] = yi.mean()
                rel[i, l] = 1.0 / (yi.var() + prior)
            elif c == 1:
                mu[i, l] = float(ytr[m][0])
                rel[i, l] = 1.0 / (yg_var + prior)
            else:
                mu[i, l] = yg_mean
                rel[i, l] = 1.0 / (yg_var + 1.0)  # unseen level: low reliability

    def est(Xset):
        num = np.zeros(Xset.shape[0], dtype=np.float64)
        den = np.zeros(Xset.shape[0], dtype=np.float64)
        for i in range(d):
            ri = rel[i, Xset[:, i]]
            mi = mu[i, Xset[:, i]]
            num += ri * mi
            den += ri
        return num / np.maximum(den, 1e-9)

    e_tr = est(Xtr)
    e_q = est(Xq)
    thr = _quantile_thresholds(e_tr, ytr, Lv)
    return _predict_thresh(e_q, thr)


# ===========================================================================
# FREQ / HOMOPHILY null + memorize + pop  (fair baseline; ported verbatim)
# ===========================================================================

def arm_homophily_cond(Xq, Xtr, ytr, Lv):
    """FREQUENCY/HOMOPHILY null scores: score(y)=sum_i count_train(X_i==xq_i, y). Subsumes factorized P(y|X_i)."""
    per = [defaultdict(lambda: np.zeros(Lv)) for _ in range(Xtr.shape[1])]
    for r in range(Xtr.shape[0]):
        for i in range(Xtr.shape[1]):
            per[i][int(Xtr[r, i])][int(ytr[r])] += 1.0
    marg = np.bincount(ytr, minlength=Lv).astype(np.float64)
    out = np.zeros((Xq.shape[0], Lv), dtype=np.float64)
    for q in range(Xq.shape[0]):
        sc = np.zeros(Lv)
        for i in range(Xq.shape[1]):
            sc = sc + per[i].get(int(Xq[q, i]), np.zeros(Lv))
        if sc.sum() <= 0:
            sc = marg
        out[q] = sc
    return out  # (nq, Lv) scores


def acc_from_scores(scores, gold, msk):
    """Tie-averaged top1 accuracy from a (nq,Lv) score matrix over a boolean mask."""
    if msk.sum() == 0:
        return float("nan")
    s = scores[msk]
    g = gold[msk].astype(np.int64)
    gs = s[np.arange(s.shape[0]), g]
    greater = (s > gs[:, None]).sum(axis=1)
    equal = (s == gs[:, None]).sum(axis=1)
    rank = greater.astype(np.float64) + (equal.astype(np.float64) + 1.0) / 2.0
    return float((rank <= 1.0).mean())


def arm_memorize(Xq, Xtr, ytr, pop_label):
    combo = defaultdict(lambda: defaultdict(int))
    for r in range(Xtr.shape[0]):
        combo[tuple(Xtr[r].tolist())][int(ytr[r])] += 1
    preds = []
    for q in range(Xq.shape[0]):
        d = combo.get(tuple(Xq[q].tolist()))
        preds.append(max(d.items(), key=lambda kv: kv[1])[0] if d else pop_label)
    return np.asarray(preds, dtype=np.int64)


def acc_labels(pred, gold, msk):
    if msk.sum() == 0:
        return float("nan")
    return float((np.asarray(pred)[msk] == gold[msk]).mean())


# ===========================================================================
# REGIMES / SPLIT  (deterministic; ported)
# ===========================================================================

def plant_regime_target(X, y_real, regime, seed, Lv):
    n = X.shape[0]
    d = X.shape[1]
    rng = np.random.default_rng(seed * 100057 + REG_SALT[regime])
    if regime == CLEAN:
        return y_real.copy(), y_real.copy()
    if regime == ARBITRARY:
        table = rng.integers(0, Lv, size=tuple([Lv] * d))
        y = np.array([table[tuple(int(v) for v in X[r])] for r in range(n)], dtype=np.int64)
        return y, y.copy()
    if regime == SHUFFLE:
        return y_real[rng.permutation(n)].copy(), y_real.copy()
    raise ValueError(regime)


def split_novel(X, seed, query_frac=0.45):
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100081 + 9)
    perm = rng.permutation(n)
    nq = int(round(query_frac * n))
    q = np.sort(perm[:nq]); tr = np.sort(perm[nq:])
    train_combos = set(tuple(X[i].tolist()) for i in tr)
    novel = np.array([tuple(X[i].tolist()) not in train_combos for i in q], dtype=bool)
    return q, tr, novel


# ===========================================================================
# PER-SEED SCORING
# ===========================================================================

def score_regime(X, y_real, regime, seed, Lv):
    q, tr, novel = split_novel(X, seed)
    y, oracle = plant_regime_target(X, y_real, regime, seed, Lv)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y[q], y[tr]
    pop_label = int(np.argmax(np.bincount(ytr, minlength=Lv)))

    # encoded monotone arms (learned weight) across encodings + equal-weight uniform
    preds = {}
    weights = {}
    for enc in ENCODINGS:
        vmap = level_value_map(enc, Lv, Xtr=Xtr)
        Xtr_e = encode(Xtr, vmap)
        Xq_e = encode(Xq, vmap)
        mw, w = arm_mono_weight(Xq_e, Xtr_e, ytr, Lv)
        preds["MONO_WEIGHT_%s" % enc] = mw
        weights[enc] = [round(float(x), 4) for x in w]
    vmap_u = level_value_map("uniform", Lv)
    preds["MONO_THERM_uniform"] = arm_mono_therm(encode(Xq, vmap_u), encode(Xtr, vmap_u), ytr, Lv)

    # Anchor 2
    preds["RELIABILITY"] = arm_reliability(Xq, Xtr, ytr, Lv)

    # fair baseline + controls
    hom = arm_homophily_cond(Xq, Xtr, ytr, Lv)
    pop = np.full(Xq.shape[0], pop_label, dtype=np.int64)
    memo = arm_memorize(Xq, Xtr, ytr, pop_label)
    orc = oracle[q]

    strata = {}
    for sname, m in (("novel", novel), ("seen", ~novel), ("all", np.ones(len(gold), bool))):
        fn = max(acc_from_scores(hom, gold, m), acc_labels(pop, gold, m))
        row = dict(FREQ_NULL=round(fn, 5), HOMOPHILY_COND=round(acc_from_scores(hom, gold, m), 5),
                   POP=round(acc_labels(pop, gold, m), 5), MEMORIZE=round(acc_labels(memo, gold, m), 5),
                   ORACLE=round(acc_labels(orc, gold, m), 5), n=int(m.sum()))
        for k, pr in preds.items():
            row[k] = round(acc_labels(pr, gold, m), 5)
        strata[sname] = row

    # per-instance CLEAN-novel correctness masks for Anchor-2 localization (baseline learned-wt uniform vs reliability)
    detail = None
    if regime == CLEAN:
        base_ok = (preds["MONO_WEIGHT_uniform"][novel] == gold[novel])
        rel_ok = (preds["RELIABILITY"][novel] == gold[novel])
        detail = dict(base_ok=base_ok.astype(np.int64).tolist(), rel_ok=rel_ok.astype(np.int64).tolist())

    return dict(regime=regime, strata=strata, weights=weights, n_novel=int(novel.sum()), detail=detail,
                sigs=dict(MONO_WEIGHT_uniform=_sig(preds["MONO_WEIGHT_uniform"]),
                          MONO_WEIGHT_log=_sig(preds["MONO_WEIGHT_log"]), RELIABILITY=_sig(preds["RELIABILITY"])))


# ===========================================================================
# CLUSTER-LEVEL AGGREGATION + VERDICT
# ===========================================================================

def run_cluster(name, path, seeds, Lv):
    meta, X, y = load_cluster(path)
    conj = conjunction_property(X, y, Lv)
    per_seed = []
    for sd in seeds:
        per_seed.append({reg: score_regime(X, y, reg, sd, Lv) for reg in REGIMES})

    def mean_novel(reg, arm):
        vals = [ps[reg]["strata"]["novel"][arm] for ps in per_seed]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    base_u = mean_novel(CLEAN, "MONO_WEIGHT_uniform")
    fn = mean_novel(CLEAN, "FREQ_NULL")
    orc = mean_novel(CLEAN, "ORACLE")
    mt = mean_novel(CLEAN, "MONO_THERM_uniform")
    memo = mean_novel(CLEAN, "MEMORIZE")

    enc_novel = {enc: mean_novel(CLEAN, "MONO_WEIGHT_%s" % enc) for enc in ENCODINGS}
    enc_delta = {enc: enc_novel[enc] - base_u for enc in ENCODINGS}
    log_delta = enc_delta["log"]

    # must-fails (learned-uniform, learned-log, reliability) must not lift above freq
    def gap(reg, arm):
        return mean_novel(reg, arm) - mean_novel(reg, "FREQ_NULL")
    mustfail_arms = ["MONO_WEIGHT_uniform", "MONO_WEIGHT_log", "RELIABILITY"]
    arb_gaps = {a: gap(ARBITRARY, a) for a in mustfail_arms}
    shuf_gaps = {a: gap(SHUFFLE, a) for a in mustfail_arms}
    mustfails_fire = all(v <= MUSTFAIL_TOL for v in list(arb_gaps.values()) + list(shuf_gaps.values()))
    ceiling_ok = bool(orc >= max(base_u, enc_novel["log"], mean_novel(CLEAN, "RELIABILITY")) - 1e-6)

    # ---- Anchor 1 verdict (headline: log encoding) ----
    if not mustfails_fire:
        a1 = "INVALID_MUSTFAIL_LEAK"
    elif log_delta >= A1_HARD_PASS:
        a1 = "HARD_PASS"
    elif log_delta >= A1_MIDDLE:
        a1 = "MIDDLE_BAND"
    else:
        a1 = "HARD_FAIL"

    # ---- Anchor 2 localization (pool CLEAN-novel instances across seeds) ----
    base_ok = []
    rel_ok = []
    for ps in per_seed:
        det = ps[CLEAN]["detail"]
        if det:
            base_ok.extend(det["base_ok"])
            rel_ok.extend(det["rel_ok"])
    base_ok = np.array(base_ok, dtype=bool)
    rel_ok = np.array(rel_ok, dtype=bool)
    n_pool = len(base_ok)
    n_base_fail = int((~base_ok).sum())
    closed = int((~base_ok & rel_ok).sum())              # baseline wrong -> reliability right
    new_fail = int((base_ok & ~rel_ok).sum())            # baseline right -> reliability wrong
    closed_frac = (closed / n_base_fail) if n_base_fail > 0 else float("nan")
    rel_novel = mean_novel(CLEAN, "RELIABILITY")
    global_delta = rel_novel - base_u

    if not mustfails_fire:
        a2 = "INVALID_MUSTFAIL_LEAK"
    elif closed_frac == closed_frac and closed_frac >= A2_CLOSE_FRAC and new_fail <= closed:
        a2 = "HARD_PASS"
    elif global_delta >= A2_MIDDLE_GLOBAL:
        a2 = "MIDDLE_BAND"
    elif closed_frac == closed_frac and closed_frac <= A2_OVERLAP_FAIL:
        a2 = "HARD_FAIL"
    else:
        a2 = "HARD_FAIL"

    repro = None
    if name == "animals":
        repro = dict(target=REPRO_TARGET_ANIMALS, measured=round(base_u, 5),
                     delta=round(base_u - REPRO_TARGET_ANIMALS, 5),
                     ok=bool(abs(base_u - REPRO_TARGET_ANIMALS) <= REPRO_TOL))

    return dict(
        name=name, n_entities=meta["n_entities"], truth_rate=meta["truth_rate"], constituents=meta["constituents"],
        conjunction=conj,
        clean_novel=dict(mono_weight_uniform=round(base_u, 5), mono_therm_uniform=round(mt, 5),
                         freq_null=round(fn, 5), oracle=round(orc, 5), memorize=round(memo, 5),
                         reliability=round(rel_novel, 5),
                         enc_novel={k: round(v, 5) for k, v in enc_novel.items()},
                         enc_delta={k: round(v, 5) for k, v in enc_delta.items()}),
        anchor1=dict(verdict=a1, log_delta=round(log_delta, 5),
                     power_delta=round(enc_delta["power"], 5), quantile_delta=round(enc_delta["quantile"], 5)),
        anchor2=dict(verdict=a2, reliability_novel=round(rel_novel, 5), global_delta=round(global_delta, 5),
                     n_pool=n_pool, n_base_fail=n_base_fail, closed=closed, new_fail=new_fail,
                     closed_frac=round(closed_frac, 5) if closed_frac == closed_frac else None),
        mustfails=dict(fire=mustfails_fire, arb_gaps={k: round(v, 5) for k, v in arb_gaps.items()},
                       shuf_gaps={k: round(v, 5) for k, v in shuf_gaps.items()}),
        ceiling_ok=ceiling_ok, reproduction=repro,
        weights_clean_seed0={enc: per_seed[0][CLEAN]["weights"][enc] for enc in ENCODINGS},
        per_seed_novel=[{reg: per_seed[i][reg]["strata"]["novel"] for reg in REGIMES} for i in range(len(seeds))],
    )


def run_measurement(seeds=SEEDS, cluster_names=("animals", "foods")):
    results = {}
    for nm in cluster_names:
        path = CLUSTERS[nm]
        if not os.path.exists(path):
            results[nm] = dict(name=nm, error="ARTIFACT_MISSING", path=path)
            _log("WARN: cluster artifact missing: %s" % path)
            continue
        results[nm] = run_cluster(nm, path, seeds, L)

    # overall verdict = headline anchors on animals if present, else foods
    head = "animals" if ("animals" in results and "error" not in results["animals"]) else None
    if head is None:
        for nm in cluster_names:
            if nm in results and "error" not in results[nm]:
                head = nm
                break

    if head is None:
        verdict = "CELL_ERROR_NO_CLUSTER"
        msg = "no cluster artifact loaded"
    else:
        h = results[head]
        a1 = h["anchor1"]["verdict"]
        a2 = h["anchor2"]["verdict"]
        repro_ok = (h.get("reproduction") is None) or h["reproduction"]["ok"]
        if not repro_ok:
            verdict = "REPRODUCTION_MISMATCH"
        elif a1 == "INVALID_MUSTFAIL_LEAK" or a2 == "INVALID_MUSTFAIL_LEAK":
            verdict = "INVALID_MUSTFAIL_LEAK"
        else:
            verdict = "ANCHOR1_%s__ANCHOR2_%s" % (a1, a2)
        msg = ("[%s] ANCHOR1(encoding log-vs-uniform)=%s log_delta=%s (power=%s quantile=%s) | base_uniform=%s "
               "log=%s freq_null=%s oracle=%s | ANCHOR2(reliability)=%s closed_frac=%s (closed=%d/%d new_fail=%d) "
               "global_delta=%s | mustfails_fire=%s repro_ok=%s"
               % (head, a1, _fmt(h["anchor1"]["log_delta"]), _fmt(h["anchor1"]["power_delta"]),
                  _fmt(h["anchor1"]["quantile_delta"]), _fmt(h["clean_novel"]["mono_weight_uniform"]),
                  _fmt(h["clean_novel"]["enc_novel"]["log"]), _fmt(h["clean_novel"]["freq_null"]),
                  _fmt(h["clean_novel"]["oracle"]), a2,
                  _fmt(h["anchor2"]["closed_frac"]) if h["anchor2"]["closed_frac"] is not None else "nan",
                  h["anchor2"]["closed"], h["anchor2"]["n_base_fail"], h["anchor2"]["new_fail"],
                  _fmt(h["anchor2"]["global_delta"]), h["mustfails"]["fire"], repro_ok))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="local_measure", elapsed_s=0.0,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        seeds=list(seeds), L=L,
        bands=dict(A1_HARD_PASS=A1_HARD_PASS, A1_MIDDLE=A1_MIDDLE, A2_CLOSE_FRAC=A2_CLOSE_FRAC,
                   A2_MIDDLE_GLOBAL=A2_MIDDLE_GLOBAL, A2_OVERLAP_FAIL=A2_OVERLAP_FAIL, MUSTFAIL_TOL=MUSTFAIL_TOL,
                   REPRO_TARGET_ANIMALS=REPRO_TARGET_ANIMALS, REPRO_TOL=REPRO_TOL),
        clusters=results,
    )
    return metrics


def _write_metrics(metrics, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


# ===========================================================================
# SELF-TEST (exercises the REAL arm code paths + REAL hd_bind; 4 validity disciplines inline)
# ===========================================================================

def self_test():
    Lv = 5
    n_dim = 256
    rng = np.random.default_rng(7)
    n = 320
    X = rng.integers(0, Lv, size=(n, 4)).astype(np.int64)
    # BALANCED strongly-conjunctive MONOTONE arena: all 4 contribute, no single dominant driver, non-modular.
    w_true = np.array([0.9, 1.0, 1.1, 1.0])
    s = (X.astype(np.float64) * w_true[None, :]).sum(1)
    edges = np.quantile(s, [0.2, 0.4, 0.6, 0.8])
    y_add = np.array([int((v > edges).sum()) for v in s], dtype=np.int64)

    # (1) POSITIVE CONTROL + real arm path: learned-weight arm must solve + generalize on NOVEL and beat freq.
    r = score_regime(X, y_add, CLEAN, 7, Lv)
    nov = r["strata"]["novel"]
    base = nov["MONO_WEIGHT_uniform"]
    fn = nov["FREQ_NULL"]
    rel = nov["RELIABILITY"]
    mono_gap = base - fn
    # (2) METRIC MOVES: the log encoding must change the composed ordering (not an absorbed reparameterization).
    #     Compare per-instance predictions uniform-vs-log on the SAME split -> must differ somewhere.
    q, tr, novel = split_novel(X, 7)
    Xq, Xtr = X[q], X[tr]
    ytr = y_add[tr]
    vmap_u = level_value_map("uniform", Lv)
    vmap_l = level_value_map("log", Lv, Xtr=Xtr)
    pu, _ = arm_mono_weight(encode(Xq, vmap_u), encode(Xtr, vmap_u), ytr, Lv)
    pl, _ = arm_mono_weight(encode(Xq, vmap_l), encode(Xtr, vmap_l), ytr, Lv)
    enc_changes_order = int((pu != pl).sum())
    # explicit ordering witness: log makes a balanced pair outrank an extreme pair that ties under uniform.
    order_witness = (vmap_l[2] + vmap_l[2]) > (vmap_l[4] + vmap_l[0]) and (vmap_u[2] + vmap_u[2]) == (vmap_u[4] + vmap_u[0])
    # (3) NEGATIVE CONTROL fires with margin: ARBITRARY must-fail must not lift the learned arm above freq.
    ra = score_regime(X, y_add, ARBITRARY, 7, Lv)
    arb_gap = ra["strata"]["novel"]["MONO_WEIGHT_uniform"] - ra["strata"]["novel"]["FREQ_NULL"]
    # (4) DETERMINISM: re-run identical scoring -> identical signatures.
    r2 = score_regime(X, y_add, CLEAN, 7, Lv)
    deterministic = (r["sigs"] == r2["sigs"])
    # reliability arm sanity: runs + beats freq on this balanced arena (down-weights nothing, but valid integration).
    rel_gap = rel - fn
    # REAL substrate bind homomorphism (live hd_bind signature): bind of FPE codes reads (i+j) mod L.
    g = np.random.default_rng(31 * 100003 + 17)
    m = g.integers(1, max(2, Lv), size=n_dim).astype(np.float64)
    j = np.arange(Lv, dtype=np.float64)[:, None]
    Yt = torch.from_numpy(np.exp(1j * (2.0 * np.pi / Lv) * (j * m[None, :])).astype(np.complex64))
    bound = hd_bind(Yt[torch.tensor([1, 2])], Yt[torch.tensor([2, 3])])
    Yc = Yt.conj().T.contiguous()
    homo_pred = torch.argmax((bound @ Yc).real, 1).tolist()
    homo_ok = homo_pred == [3 % Lv, 5 % Lv]

    conj = conjunction_property(X, y_add, Lv)

    ok = bool(
        base >= 0.50                      # positive control: learned arm solves + generalizes on novel
        and mono_gap >= 0.15              # clearly beats freq (real lift, not saturation)
        and fn <= 0.85                    # guard-vs-arena-floor: freq not saturated
        and enc_changes_order >= 1        # metric-moves: encoding lever is live (changes >=1 novel prediction)
        and order_witness                 # explicit compressive-ordering witness
        and arb_gap <= 0.10               # negative control fires with margin
        and deterministic                 # determinism self-guard
        and rel_gap >= 0.10               # reliability arm is a valid integrator (beats freq on planted)
        and homo_ok                       # real FHRR bind homomorphism intact (live signature)
        and conj["mi_margin"] >= 0.30     # planted arena is a genuine conjunction
        and conj["dominance_ratio"] == conj["dominance_ratio"] and conj["dominance_ratio"] <= 0.55
        and r["n_novel"] >= 8
    )
    out = dict(base_novel=round(base, 4), freq_null=round(fn, 4), mono_gap=round(mono_gap, 4),
               reliability_novel=round(rel, 4), rel_gap=round(rel_gap, 4), enc_changes_order=enc_changes_order,
               order_witness=bool(order_witness), arb_gap=round(arb_gap, 4), deterministic=bool(deterministic),
               homomorphism_ok=bool(homo_ok), mi_margin=conj["mi_margin"], dominance_ratio=conj["dominance_ratio"],
               n_novel=r["n_novel"], passed=ok)
    print("[SELFTEST] %s" % json.dumps(out), flush=True)
    return ok, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="quick local gate: animals only, 3 seeds")
    args = ap.parse_args()

    if args.self_test:
        ok, _ = self_test()
        sys.exit(0 if ok else 1)
    if args.smoke:
        t0 = time.perf_counter()
        m = run_measurement(seeds=(7, 13, 17), cluster_names=("animals",))
        m["elapsed_s"] = time.perf_counter() - t0
        m["run_mode"] = "smoke"
        _write_metrics(m, out_dir=OUT_DIR + "_smoke")
        _log(m["verdict_msg"])
        return
    if args.run:
        t0 = time.perf_counter()
        m = run_measurement()
        m["elapsed_s"] = time.perf_counter() - t0
        _write_metrics(m)
        _log(m["verdict_msg"])
        return
    ap.print_help()


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
            with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as f:
                json.dump(crash, f, indent=2)
        except Exception:
            pass
        raise
