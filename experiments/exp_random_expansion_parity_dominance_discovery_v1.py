"""RANDOM_EXPANSION_PARITY_DOMINANCE_DISCOVERY (v1): can a SINGLE random nonlinear expansion + learned linear
readout (the mixed-selectivity / reservoir mechanism) discover BOTH symmetric-PARITY and asymmetric-DOMINANCE --
the two relational structures that the TWO specialized binds each solve only ONE of?

REFRAMED PREMISE (corrected from the frontier VET, exp_interaction_nonadditive_discovery_v1):
  Parity/XOR is NOT an unsolved gap. A shared-code SYMMETRIC PRODUCT bind ALREADY discovers parity (~0.98 novel
  in the frontier cell) because parity is swap-symmetric. But that same symmetric bind CANNOT represent DOMINANCE
  (x0>x1) -- a swap-symmetric readout is order-blind. Conversely the ROLE-KEYED bilinear bind discovers DOMINANCE
  (role-keying supplies the order/asymmetry) but role-keying BREAKS swap-symmetry, so it FAILS parity. The open
  question is the ROLE-KEYING <-> SYMMETRY TENSION: each specialized bind does exactly ONE of {parity, dominance}
  and structurally cannot do the other. NEITHER specialized bind does BOTH.

MECHANISM UNDER TEST (brain-grounded; notes/drill_brain_nonadditive_interaction_relational_coding_bestinclass_2026-07-14.md
  ranks 2/3, Rigotti/Fusi 2013 "why neurons mix" + Rahimi/Recht 2007 random features + Marr-Albus expansion coding):
  A RANDOM NONLINEAR EXPANSION phi(x) = nonlin(R @ onehot(pos,level) + b) with R a FIXED random projection into
  dimensionality D_exp, followed by a plain LEARNED LINEAR READOUT (closed-form ridge). The one-hot(position,level)
  input is ROLE-PRESERVING (each constituent has its own dim-block) AND retains full level identity, so a
  high-dim random mixing keeps BOTH the symmetric-product structure (parity) AND the order/role structure
  (dominance) linearly extractable downstream -- the textbook resolution of a non-linearly-separable problem:
  expand nonlinearly (CONSTRUCT the expansion, random/unstructured), then read out linearly (LEARN only the readout).
  KEY DESIGN: SWEEP D_exp in {8,16,32,64,128,256,512}. The dimensionality argument predicts each target becomes
  linearly separable once D_exp is high enough -> we report accuracy-vs-D_exp so the threshold is visible.

ARMS (over shared ordinal constituents; glass-box, NO LLM at measurement time):
  RANDOM_EXP        random ReLU expansion (D-swept) + ridge readout           -- THE MECHANISM (does it do BOTH?)
  RANDOM_EXP_FOUR   random Fourier expansion at D_ref + ridge                 -- expansion-family robustness datapoint
  SYM_PROD          learned SHARED-code product (swap-symmetric)              -- parity-YES / dominance-NO specialist
  ROLE_BILINEAR     learned ROLE-KEYED low-rank bilinear (Pa)*(Qb) product   -- dominance-YES / parity-NO specialist
  ROLE_ADD          learned ROLE-KEYED sum (linear/additive)                  -- additive contrast (fails parity)
  FREQ_NULL         max(HOMOPHILY_COND, POP)                                  -- frequency baseline
  MEMORIZE          per-combo lookup (fails on NOVEL by construction)         -- memorization floor
  ORACLE            planted label (ceiling)

TARGET FAMILIES (planted, deterministic): PARITY + DOMINANCE are the HEADLINE; AND2 / MULT / ADD are CONTEXT.
MUST-FAILS (per family; LOAD-BEARING -- a high-D random expansion + linear readout CAN memorize):
  ARBITRARY = random class per unique FULL combo (no generalizable structure); SHUFFLE = label permutation (leak).
  On NOVEL (held-out) combos the mechanism must NOT beat FREQ_NULL (gap <= tol). NOVEL-combo generalization +
  arbitrary-at-chance are the REAL test that the expansion DISCOVERS structure rather than memorizing.

HEADLINE (NOVEL stratum, top-1 accuracy, multi-seed mean; RANDOM_EXP evaluated at D_ref=512, a FIXED pre-registered
  dimension -- NOT best-over-sweep, to avoid selection-on-test; the sweep curve is reported for the threshold):
  PARITY:    RANDOM_EXP_novel >> chance  AND  RANDOM_EXP_novel - ROLE_BILINEAR_novel >= gap  (beats the parity-failer)
  DOMINANCE: RANDOM_EXP_novel >> chance  AND  RANDOM_EXP_novel - SYM_PROD_novel     >= gap  (beats the dominance-failer)

PRE-REGISTERED BANDS (fixed BEFORE running; see the prereg .md):
  HARD_PASS_BOTH: parity_pass AND dominance_pass AND both must-fails fire (all families) AND ceiling sane.
  PARTIAL_PARITY_ONLY / PARTIAL_DOM_ONLY: exactly one family passes (random expansion inherits ONE specialist's
    limitation -- an informative partial). REFUTE_NEITHER: neither family passes (random expansion discovers
    NEITHER on novel combos -> an honest, valuable negative). INVALID_MUSTFAIL: a must-fail did not fire (the
    expansion memorized -> cell is not measuring generalization; HAND BACK, do not tier).

Glass-box CPU (sequential; arena is tiny K=4/L=4/N=220; ridge = single lstsq, learned arms = 500-epoch Adam on 48d).
Default invocation (no flag) = FULL run to completion. ASCII-only. No bare except; except SystemExit before
except Exception. Atomic metrics write. Start-marker + per-seed heartbeat + flushed progress logging.
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test): RANDOM_EXP/SYM_PROD/ROLE_BILINEAR/ROLE_ADD/HOM distinct
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: accuracy target has no Cramer-Rao noise floor; chance = majority-class rate is the honest floor (reported per family)
# - baseline_in_band at smoke (META_RULE_AG): FREQ_NULL on PARITY CLEAN not saturated (<=0.75); asserted in self_test
# - discriminator survives scale: arena is FIXED tiny size; smoke == full-scale on the discriminator (only #seeds grows)
# - HARD_PASS strictly above floor: gates use chance+GAP margins, not >= floor
# - real_code_path: self_test() exercises the ACTUAL _expand + _ridge + _train_learned functions the FULL run uses (no synthetic-only branch)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@; frontier sym~0.98 is CITED@coordinator-reframe (re-verified by our own smoke)

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

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "random_expansion_parity_dominance_discovery_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ---- arena (identical to the frontier cell so results are directly comparable) ----
K = 4               # constituents
L = 4               # ordinal levels per constituent (0..3)
N_ENT = 220         # sampled DISTINCT combos (combo space L^K = 256)
QUERY_FRAC = 0.45

# ---- families / regimes ----
PARITY = "PARITY"; AND2 = "AND2"; MULT = "MULT"; DOMINANCE = "DOMINANCE"; ADD = "ADD"
FAMILIES = [PARITY, DOMINANCE, AND2, MULT, ADD]
HEADLINE_FAMS = [PARITY, DOMINANCE]
NCLASS = {PARITY: 2, AND2: 2, MULT: 4, DOMINANCE: 2, ADD: 4}

CLEAN = "CLEAN"; ARBITRARY = "ARBITRARY"; SHUFFLE = "SHUFFLE"
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]

# ---- random-expansion mechanism config ----
D_SWEEP = [8, 16, 32, 64, 128, 256, 512]   # expansion dimensionality sweep (the dimensionality argument)
D_REF = 512                                  # FIXED reference dim for the HARD_PASS gates (NOT best-over-sweep)
RIDGE_LAM = 1.0                              # ridge regularization (controls memorization at high D_exp)
EXP_RELU = "relu"; EXP_FOUR = "fourier"

# ---- arm names ----
RE = "RANDOM_EXP"; RE_F = "RANDOM_EXP_FOUR"
SYM = "SYM_PROD"; BIL = "ROLE_BILINEAR"; ADDL = "ROLE_ADD"
HOM = "HOMOPHILY_COND"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"
LEARNED_ARMS = [SYM, BIL, ADDL]                                  # computed on CLEAN only (contrasts)
BASE_ARMS = [HOM, MEMO, POP, ORC]                                # computed all regimes
CANON_ARMS = [RE, RE_F, SYM, BIL, ADDL, HOM, MEMO, POP, ORC, FREQ]

# ---- learned-arm hyperparams (copied from frontier for direct comparability) ----
EMB_D = 48
EPOCHS = 500
LR = 0.05

# ---- pre-registered bands (fixed before running) ----
HP_GAP_CHANCE = 0.20     # RANDOM_EXP(D_ref) novel must be >= chance + this on parity AND dominance
HP_GAP_BEAT = 0.15       # RANDOM_EXP must beat, on each family, the specialist that fails there, by >= this
MUSTFAIL_TOL = 0.07      # RANDOM_EXP(D_ref) on ARBITRARY/SHUFFLE novel - FREQ_NULL must be <= this (all families)
THRESH_GAP = 0.20        # threshold def: smallest D_exp with RANDOM_EXP novel >= chance + this (reported per family)
CEIL_EPS = 1e-6


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return str(x)


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


def chance_of(family, y_all):
    """Majority-class rate = honest chance floor for accuracy on an imbalanced target."""
    c = np.bincount(y_all, minlength=NCLASS[family]).astype(np.float64)
    return float(c.max() / max(1.0, c.sum()))


# ===========================================================================
# ARENA + TARGET FAMILIES (deterministic, planted; glass-box) -- copied from the frontier cell
# ===========================================================================

def make_X(seed):
    rng = np.random.default_rng(seed * 100003 + 11)
    space = L ** K
    take = min(N_ENT, space)
    idx = rng.choice(space, size=take, replace=False)       # DISTINCT combos -> every query combo is NOVEL
    X = np.zeros((take, K), dtype=np.int64)
    for c in range(K):
        X[:, c] = (idx // (L ** c)) % L
    return X


def target(family, X):
    bits = (X >= (L // 2)).astype(np.int64)                 # top-half indicator per constituent
    if family == PARITY:
        return (bits.sum(1) % 2).astype(np.int64)           # swap-SYMMETRIC, high-order non-additive
    if family == AND2:
        return (bits[:, 0] & bits[:, 1]).astype(np.int64)
    if family == MULT:
        prod = X[:, 0] * X[:, 1]
        return np.digitize(prod, [2, 4, 6]).astype(np.int64)
    if family == DOMINANCE:
        return (X[:, 0] > X[:, 1]).astype(np.int64)         # ANTISYMMETRIC / order-sensitive (ties -> 0)
    if family == ADD:
        s = X.sum(1)
        edges = [K * (L - 1) * f for f in (0.30, 0.50, 0.70)]
        return np.digitize(s, edges).astype(np.int64)
    raise ValueError(family)


def plant_regime(X, y_clean, family, regime, seed):
    """Returns (y_used, y_oracle). ARBITRARY/SHUFFLE are must-fail controls (per-combo random / label permutation)."""
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100057 + (abs(hash((family, regime))) % 100000))
    if regime == CLEAN:
        return y_clean.copy(), y_clean.copy()
    if regime == ARBITRARY:
        nc = NCLASS[family]
        combo_label = {}
        y = np.empty(n, dtype=np.int64)
        for r in range(n):
            key = tuple(int(v) for v in X[r])
            if key not in combo_label:
                combo_label[key] = int(rng.integers(0, nc))
            y[r] = combo_label[key]
        return y, y.copy()
    if regime == SHUFFLE:
        y = y_clean[rng.permutation(n)].copy()
        return y, y.copy()
    raise ValueError(regime)


def split_novel(X, seed):
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100081 + 9)
    perm = rng.permutation(n)
    nq = int(round(QUERY_FRAC * n))
    q = np.sort(perm[:nq]); tr = np.sort(perm[nq:])
    train_combos = set(tuple(X[i].tolist()) for i in tr)
    novel = np.array([tuple(X[i].tolist()) not in train_combos for i in q], dtype=bool)
    return q, tr, novel


# ===========================================================================
# RANDOM NONLINEAR EXPANSION + LEARNED LINEAR READOUT (the mechanism under test)
# ===========================================================================

def _onehot(X):
    """Role-preserving one-hot(position, level). (n, K*L) float, block-centered so ReLU sees zero-mean input.
    Preserves BOTH full level identity AND position/role -> a random mixing keeps parity and dominance extractable."""
    n, k = X.shape
    U = np.zeros((n, k * L), dtype=np.float32)
    rows = np.arange(n)
    for i in range(k):
        U[rows, i * L + X[:, i]] = 1.0
    return U - (1.0 / L)


def _expand(Utr, Uq, D, kind, seed):
    """FIXED random projection R (same for train + query) then nonlinearity. CONSTRUCT the expansion (random)."""
    rng = np.random.default_rng((seed * 2654435761 + D * 40503 + (0 if kind == EXP_RELU else 1)) % (2 ** 63))
    d_in = Utr.shape[1]
    R = (rng.standard_normal((d_in, D)) / math.sqrt(d_in)).astype(np.float32)
    if kind == EXP_RELU:
        bJ = (rng.standard_normal(D) * 0.1).astype(np.float32)
        Ztr = np.maximum(Utr @ R + bJ, 0.0)
        Zq = np.maximum(Uq @ R + bJ, 0.0)
        return Ztr, Zq
    if kind == EXP_FOUR:
        ph = rng.uniform(0.0, 2.0 * math.pi, size=D).astype(np.float32)   # gamma=1 (baked into R scale)
        s = math.sqrt(2.0 / D)
        Ztr = (s * np.cos(Utr @ R + ph)).astype(np.float32)
        Zq = (s * np.cos(Uq @ R + ph)).astype(np.float32)
        return Ztr, Zq
    raise ValueError(kind)


def _ridge_fit_predict(Ztr, ytr, Zq, nclass, lam=RIDGE_LAM):
    """Plain LEARNED LINEAR readout: closed-form ridge one-hot regression -> argmax. Deterministic (no SGD tuning)."""
    n = Ztr.shape[0]
    Ztr = np.concatenate([Ztr, np.ones((n, 1), dtype=Ztr.dtype)], axis=1)   # bias column
    Zq = np.concatenate([Zq, np.ones((Zq.shape[0], 1), dtype=Zq.dtype)], axis=1)
    d = Ztr.shape[1]
    Y = np.zeros((n, nclass), dtype=np.float64)
    Y[np.arange(n), ytr] = 1.0
    A = Ztr.astype(np.float64).T @ Ztr.astype(np.float64) + lam * np.eye(d)
    W = np.linalg.solve(A, Ztr.astype(np.float64).T @ Y)
    return np.argmax(Zq.astype(np.float64) @ W, axis=1).astype(np.int64)


def arm_random_expand(Xtr, ytr, Xq, nclass, D, kind, seed):
    Utr = _onehot(Xtr); Uq = _onehot(Xq)
    Ztr, Zq = _expand(Utr, Uq, D, kind, seed)
    return _ridge_fit_predict(Ztr, ytr, Zq, nclass)


# ===========================================================================
# LEARNED SPECIALIST ARMS (plain SGD) -- copied verbatim in behavior from the frontier cell
#   'sym'      = SYM_PROD       (shared code, product, swap-SYMMETRIC): parity-YES / dominance-NO
#   'bilinear' = ROLE_BILINEAR  (role-keyed low-rank bilinear (Pa)*(Qb) product): dominance-YES / parity-NO
#   'add'      = ROLE_ADD       (role-keyed sum, additive): fails parity
# ===========================================================================

def _train_learned(Xtr, ytr, Xq, nclass, mode, seed):
    g = torch.Generator().manual_seed(seed * 7919 + {"add": 2, "sym": 3, "bilinear": 4}[mode])
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    k = Xtr.shape[1]
    product = (mode in ("sym", "bilinear"))
    params = []
    c_fixed = None; P = None; emb = None
    if mode == "bilinear":
        c_fixed = (1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))                        # FIXED level-code
        P = torch.nn.Parameter(torch.eye(EMB_D).unsqueeze(0).repeat(k, 1, 1)              # LEARNED, init=identity
                               + 0.02 * torch.randn(k, EMB_D, EMB_D, generator=g))
        params.append(P)
    elif mode == "sym":
        emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))          # SHARED (no role) -> symmetric
        params.append(emb)
    else:
        center = 1.0 if product else 0.0
        emb = torch.nn.Parameter(center + 0.2 * torch.randn(k, L, EMB_D, generator=g))    # role-keyed
        params.append(emb)
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, nclass, generator=g))
    b = torch.nn.Parameter(torch.zeros(nclass))
    params += [W, b]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def compose(Xi):
        if mode == "bilinear":
            cx = c_fixed[Xi]                                    # (n,k,D) fixed codes
            e = torch.einsum("nkd,kde->nke", cx, P)            # (n,k,D) role-projected (gain field)
            return e.prod(dim=1)
        if mode == "sym":
            e = emb[Xi]                                         # (n,k,D) shared table -> swap-symmetric
        else:
            e = emb[torch.arange(k).unsqueeze(0), Xi]           # (n,k,D) role-keyed
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
        pred = torch.argmax(logits_q, 1).numpy().astype(np.int64)
    return pred


# ===========================================================================
# baselines -- copied from the frontier cell
# ===========================================================================

def arm_homophily(family, Xtr, ytr, Xq):
    nc = NCLASS[family]
    per = [defaultdict(lambda: np.zeros(nc)) for _ in range(Xtr.shape[1])]
    for r in range(Xtr.shape[0]):
        for i in range(Xtr.shape[1]):
            per[i][int(Xtr[r, i])][int(ytr[r])] += 1.0
    marg = np.bincount(ytr, minlength=nc).astype(np.float64)
    preds = []
    for q in range(Xq.shape[0]):
        sc = np.zeros(nc)
        for i in range(Xq.shape[1]):
            sc = sc + per[i].get(int(Xq[q, i]), np.zeros(nc))
        if sc.sum() <= 0:
            sc = marg
        preds.append(int(np.argmax(sc)))
    return np.array(preds, dtype=np.int64)


def arm_memorize(family, Xtr, ytr, Xq, pop_label):
    combo = defaultdict(lambda: defaultdict(int))
    for r in range(Xtr.shape[0]):
        combo[tuple(Xtr[r].tolist())][int(ytr[r])] += 1
    preds = []
    for q in range(Xq.shape[0]):
        dd = combo.get(tuple(Xq[q].tolist()))
        preds.append(max(dd.items(), key=lambda kv: kv[1])[0] if dd else pop_label)
    return np.array(preds, dtype=np.int64)


def acc(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


# ===========================================================================
# per (family, regime, seed) scoring
# ===========================================================================

def score(family, regime, X, y_clean, seed):
    q, tr, novel = split_novel(X, seed)
    y_used, y_oracle = plant_regime(X, y_clean, family, regime, seed)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y_used[q], y_used[tr]
    nc = NCLASS[family]
    pop_label = int(np.argmax(np.bincount(ytr, minlength=nc)))

    preds = {}
    # RANDOM_EXP over the full D sweep (relu) + the canonical D_ref arm
    re_by_D = {}
    for D in D_SWEEP:
        re_by_D[D] = arm_random_expand(Xtr, ytr, Xq, nc, D, EXP_RELU, seed)
    preds[RE] = re_by_D[D_REF]
    preds[RE_F] = arm_random_expand(Xtr, ytr, Xq, nc, D_REF, EXP_FOUR, seed)
    # baselines (all regimes)
    preds[HOM] = arm_homophily(family, Xtr, ytr, Xq)
    preds[MEMO] = arm_memorize(family, Xtr, ytr, Xq, pop_label)
    preds[POP] = np.full(Xq.shape[0], pop_label, dtype=np.int64)
    preds[ORC] = y_oracle[q]
    # learned specialist contrasts: CLEAN only, and only for the HEADLINE families (PARITY/DOMINANCE) where the
    # symmetric-vs-role-keyed specialization is interpreted. Context families (AND2/MULT/ADD) report RE + baselines
    # only (compute-proportionality: the specialists are not the story there).
    if regime == CLEAN and family in HEADLINE_FAMS:
        preds[SYM] = _train_learned(Xtr, ytr, Xq, nc, "sym", seed)
        preds[BIL] = _train_learned(Xtr, ytr, Xq, nc, "bilinear", seed)
        preds[ADDL] = _train_learned(Xtr, ytr, Xq, nc, "add", seed)

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    out = {}
    for sname, m in (("novel", novel), ("all", np.ones(len(gold), bool))):
        d = {arm: round(a(preds[arm], m), 5) for arm in preds}
        d[FREQ] = round(max(d[HOM], d[POP]), 5)
        d["RE_curve"] = {int(D): round(a(re_by_D[D], m), 5) for D in D_SWEEP}
        d["n"] = int(m.sum())
        out[sname] = d
    # ARMS-MUST-DIFFER signatures (CLEAN headline families only, where learned arms exist)
    sigs = {}
    if regime == CLEAN and family in HEADLINE_FAMS:
        sigs = {arm: _sig(preds[arm]) for arm in (RE, SYM, BIL, ADDL, HOM)}
    return dict(strata=out, sigs=sigs, n_novel=int(novel.sum()), n_query=int(len(gold)))


# ===========================================================================
# defensive infra: start-marker + heartbeat + crash metrics
# ===========================================================================

def _write_start_marker(expected_n_units, run_mode):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode, expected_n_units=expected_n_units)
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUT_DIR, "_start_marker.json"))


def _heartbeat(unit_idx, total_units, elapsed_s):
    try:
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(ts_iso=datetime.now(timezone.utc).isoformat(),
                                    unit_idx=unit_idx, total_units=total_units,
                                    elapsed_s=round(elapsed_s, 2))) + "\n")
    except OSError:
        pass


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds=(7, 13, 17, 23, 29)):
    run_mode = "full" if len(seeds) >= 5 else "smoke"
    expected_n_units = len(FAMILIES) * len(REGIMES) * len(seeds)
    _write_start_marker(expected_n_units, run_mode)
    _log("%s run: %d families x %d regimes x %d seeds, arena K=%d L=%d N=%d D_sweep=%s D_ref=%d"
         % (run_mode.upper(), len(FAMILIES), len(REGIMES), len(seeds), K, L, N_ENT, D_SWEEP, D_REF))
    per = {fam: {reg: [] for reg in REGIMES} for fam in FAMILIES}
    chances = {}
    t0 = time.perf_counter()
    unit = 0
    for si, sd in enumerate(seeds):
        X = make_X(sd)
        for fam in FAMILIES:
            y_clean = target(fam, X)
            if sd == seeds[0]:
                chances[fam] = chance_of(fam, y_clean)
            for reg in REGIMES:
                per[fam][reg].append(score(fam, reg, X, y_clean, sd))
                unit += 1
        _heartbeat(unit, expected_n_units, time.perf_counter() - t0)
        _log("  seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))

    def mean_novel(fam, reg, arm):
        vals = [ps["strata"]["novel"][arm] for ps in per[fam][reg] if arm in ps["strata"]["novel"]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    def mean_curve(fam, reg):
        agg = {}
        for D in D_SWEEP:
            vals = [ps["strata"]["novel"]["RE_curve"][D] for ps in per[fam][reg]]
            vals = [v for v in vals if v == v]
            agg[D] = round(float(np.mean(vals)), 5) if vals else float("nan")
        return agg

    # per-family aggregate table (CLEAN novel) + must-fail gaps
    table = {}
    for fam in FAMILIES:
        table[fam] = {arm: round(mean_novel(fam, CLEAN, arm), 5) for arm in CANON_ARMS}
        table[fam]["chance"] = round(chances[fam], 5)
        table[fam]["RE_curve_clean"] = mean_curve(fam, CLEAN)
        table[fam]["arb_gap_RE"] = round(mean_novel(fam, ARBITRARY, RE) - mean_novel(fam, ARBITRARY, FREQ), 5)
        table[fam]["shuf_gap_RE"] = round(mean_novel(fam, SHUFFLE, RE) - mean_novel(fam, SHUFFLE, FREQ), 5)

    def threshold(fam):
        cur = table[fam]["RE_curve_clean"]; thr = chances[fam] + THRESH_GAP
        for D in D_SWEEP:
            if cur[D] == cur[D] and cur[D] >= thr:
                return D
        return None

    p = table[PARITY]; dmn = table[DOMINANCE]
    ch_p = chances[PARITY]; ch_d = chances[DOMINANCE]

    # ---- HEADLINE verdict: does ONE random-expansion mechanism do BOTH? ----
    parity_pass = bool(p[RE] >= ch_p + HP_GAP_CHANCE and (p[RE] - p[BIL]) >= HP_GAP_BEAT)   # beats parity-failer (bilinear)
    dom_pass = bool(dmn[RE] >= ch_d + HP_GAP_CHANCE and (dmn[RE] - dmn[SYM]) >= HP_GAP_BEAT)  # beats dominance-failer (symmetric)

    mustfail_ok = all(table[fam]["arb_gap_RE"] <= MUSTFAIL_TOL and table[fam]["shuf_gap_RE"] <= MUSTFAIL_TOL
                      for fam in FAMILIES)
    ceiling_ok = all(table[fam][ORC] >= table[fam][RE] - CEIL_EPS for fam in FAMILIES)

    # specialization sanity (the reframe's premise): sym solves parity/fails dom; bilinear solves dom/fails parity
    spec_confirmed = bool(p[SYM] >= ch_p + HP_GAP_CHANCE and p[BIL] <= ch_p + HP_GAP_BEAT
                          and dmn[BIL] >= ch_d + HP_GAP_CHANCE and dmn[SYM] <= ch_d + HP_GAP_BEAT)

    if not mustfail_ok:
        verdict = "INVALID_MUSTFAIL_EXPANSION_MEMORIZED"
    elif parity_pass and dom_pass and ceiling_ok:
        verdict = "HARD_PASS_BOTH_RANDOM_EXPANSION_UNIFIES_PARITY_AND_DOMINANCE"
    elif parity_pass and not dom_pass:
        verdict = "PARTIAL_PARITY_ONLY_RANDOM_EXPANSION"
    elif dom_pass and not parity_pass:
        verdict = "PARTIAL_DOMINANCE_ONLY_RANDOM_EXPANSION"
    else:
        verdict = "REFUTE_RANDOM_EXPANSION_DISCOVERS_NEITHER_ON_NOVEL"

    thr_p = threshold(PARITY); thr_d = threshold(DOMINANCE)
    msg = ("%s || PARITY(ch=%.2f): RE=%s (four=%s) SYM=%s BIL=%s ADD=%s MEMO=%s FREQ=%s ORC=%s "
           "(RE-BIL=%s) thr=%s | DOMINANCE(ch=%.2f): RE=%s (four=%s) SYM=%s BIL=%s ADD=%s MEMO=%s FREQ=%s ORC=%s "
           "(RE-SYM=%s) thr=%s | context_RE(AND2=%s MULT=%s ADD=%s) | "
           "pass(parity=%s dom=%s) spec_confirmed=%s mustfails(ok=%s parity_arb=%s dom_arb=%s) ceiling=%s"
           % (verdict, ch_p, _fmt(p[RE]), _fmt(p[RE_F]), _fmt(p[SYM]), _fmt(p[BIL]), _fmt(p[ADDL]),
              _fmt(p[MEMO]), _fmt(p[FREQ]), _fmt(p[ORC]), _fmt(p[RE] - p[BIL]), thr_p,
              ch_d, _fmt(dmn[RE]), _fmt(dmn[RE_F]), _fmt(dmn[SYM]), _fmt(dmn[BIL]), _fmt(dmn[ADDL]),
              _fmt(dmn[MEMO]), _fmt(dmn[FREQ]), _fmt(dmn[ORC]), _fmt(dmn[RE] - dmn[SYM]), thr_d,
              _fmt(table[AND2][RE]), _fmt(table[MULT][RE]), _fmt(table[ADD][RE]),
              parity_pass, dom_pass, spec_confirmed, mustfail_ok,
              _fmt(table[PARITY]["arb_gap_RE"]), _fmt(table[DOMINANCE]["arb_gap_RE"]), ceiling_ok))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode=run_mode,
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        arena=dict(K=K, L=L, N_ENT=N_ENT, query_frac=QUERY_FRAC), seeds=list(seeds),
        expansion=dict(D_sweep=D_SWEEP, D_ref=D_REF, ridge_lam=RIDGE_LAM, kinds=[EXP_RELU, EXP_FOUR],
                       input="onehot_position_level_block_centered"),
        emb_d=EMB_D, epochs=EPOCHS, lr=LR, chances=chances,
        table_clean_novel=table,
        thresholds=dict(parity_D=thr_p, dominance_D=thr_d, thresh_gap=THRESH_GAP),
        gates=dict(parity_pass=parity_pass, dom_pass=dom_pass, mustfail_ok=mustfail_ok, ceiling_ok=ceiling_ok,
                   spec_confirmed=spec_confirmed,
                   parity_re_chance_margin=round(p[RE] - ch_p, 5), dom_re_chance_margin=round(dmn[RE] - ch_d, 5),
                   parity_re_minus_bil=round(p[RE] - p[BIL], 5), dom_re_minus_sym=round(dmn[RE] - dmn[SYM], 5)),
        bands=dict(HP_GAP_CHANCE=HP_GAP_CHANCE, HP_GAP_BEAT=HP_GAP_BEAT, MUSTFAIL_TOL=MUSTFAIL_TOL,
                   THRESH_GAP=THRESH_GAP),
        per_family_regime_novel={fam: {reg: [ps["strata"]["novel"] for ps in per[fam][reg]] for reg in REGIMES}
                                 for fam in FAMILIES},
    )
    return metrics


# ===========================================================================
# SELF-TEST (exercises the REAL _expand + _ridge + _train_learned path on the real arena)
# ===========================================================================

def self_test():
    ok_all = True
    details = {}
    exercised = set()

    X = make_X(7)
    # --- PARITY (symmetric) ---
    yp = target(PARITY, X)
    ch_p = chance_of(PARITY, yp)
    rc_p = score(PARITY, CLEAN, X, yp, 7)["strata"]["novel"]        # exercises RE (expand+ridge) + learned arms
    ra_p = score(PARITY, ARBITRARY, X, yp, 7)["strata"]["novel"]    # exercises must-fail path
    exercised.update(["_expand", "_ridge_fit_predict", "_train_learned", "arm_random_expand"])
    re_p = rc_p[RE]; sym_p = rc_p[SYM]; bil_p = rc_p[BIL]; freq_p = rc_p[FREQ]
    arb_gap_p = ra_p[RE] - ra_p[FREQ]
    details.update(dict(parity_RE=re_p, parity_SYM=sym_p, parity_BIL=bil_p, parity_ADD=rc_p[ADDL],
                        parity_MEMO=rc_p[MEMO], parity_FREQ=freq_p, parity_ORC=rc_p[ORC],
                        parity_chance=round(ch_p, 4), parity_arb_gap_RE=round(arb_gap_p, 4),
                        parity_RE_curve=rc_p["RE_curve"], n_novel=rc_p["n"]))

    # --- DOMINANCE (antisymmetric) ---
    yd = target(DOMINANCE, X)
    ch_d = chance_of(DOMINANCE, yd)
    rc_d = score(DOMINANCE, CLEAN, X, yd, 7)["strata"]["novel"]
    ra_d = score(DOMINANCE, SHUFFLE, X, yd, 7)["strata"]["novel"]
    re_d = rc_d[RE]; sym_d = rc_d[SYM]; bil_d = rc_d[BIL]
    shuf_gap_d = ra_d[RE] - ra_d[FREQ]
    details.update(dict(dom_RE=re_d, dom_SYM=sym_d, dom_BIL=bil_d, dom_ADD=rc_d[ADDL], dom_MEMO=rc_d[MEMO],
                        dom_FREQ=rc_d[FREQ], dom_ORC=rc_d[ORC], dom_chance=round(ch_d, 4),
                        dom_shuf_gap_RE=round(shuf_gap_d, 4), dom_RE_curve=rc_d["RE_curve"]))

    # ARMS-MUST-DIFFER
    digs = score(PARITY, CLEAN, X, yp, 7)["sigs"]
    arms_differ = len(set(digs.values())) == len(digs)
    details["arms_differ_sig_count"] = len(set(digs.values()))
    details["exercised_entrypoints"] = sorted(exercised)

    checks = {
        # --- mechanism WORKS on the easy (role-preserving) family: dominance must be discoverable at D_ref ---
        "RE_solves_dominance_novel": re_d >= ch_d + 0.15,
        # --- specialization framing holds (reframe premise): symmetric solves parity; role-keyed solves dominance ---
        "SYM_solves_parity_novel": sym_p >= ch_p + 0.15,
        "BIL_solves_dominance_novel": bil_d >= ch_d + 0.10,
        # NOTE: RE-solves-PARITY is NOT gated -- parity generalization by a random expansion on NOVEL combos is the
        # OPEN question (could honestly REFUTE); it is REPORTED in details, not asserted.
        # --- LOAD-BEARING must-fails: a high-D random expansion + linear readout can memorize ---
        "arbitrary_mustfail_fires_parity": arb_gap_p <= 0.10,
        "shuffle_mustfail_fires_dominance": shuf_gap_d <= 0.10,
        # --- fairness / validity ---
        "freq_not_saturated_parity": freq_p <= 0.75,          # arena not trivially solvable by frequency (guard-vs-floor)
        "ceiling_sane_parity": rc_p[ORC] >= re_p - 1e-6,
        "enough_novel": rc_p["n"] >= 20,
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
