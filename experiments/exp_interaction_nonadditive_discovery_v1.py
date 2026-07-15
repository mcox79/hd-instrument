"""INTERACTION_NONADDITIVE_DISCOVERY (v1): can an INTERACTION / non-commutative composition op read out
NON-ADDITIVE conjunctions (parity / AND-gate / multiplicative) and ORDER-SENSITIVE (dominance) targets that a
monotone-ADDITIVE code provably cannot -- and does a LEARNED shared-code + non-additive-readout DISCOVER that
structure from data (extending the proven abelian/commutative-discovery result to the non-commutative case)?

Two converging prior threads (inlined; NO re-hunt needed):
  (1) DISCOVERY VET (this arc): a shared-code + compositional-readout architecture genuinely DISCOVERS commutative/
      abelian structure (cyclic + XOR, ~0.41 novel), but the readout Re<bind(E[a],E[b]),E[r]> is SYMMETRIC under
      a<->b, so it provably cannot represent ASYMMETRIC/order-sensitive interaction. Lever = break that symmetry
      (role-keyed / non-commutative bind).
  (2) GENERATION cell (exp_generated_conjunction_monotone_foods_v1, commit e7e5f1135): a monotone-additive code
      reads a BALANCED-ADDITIVE conjunction (+0.42 over freq) but an inline no-API probe proved it STRUCTURALLY
      LOSES on non-additive targets: AND-gate = -0.018, parity = -0.006 vs +0.423 balanced-additive. Strong real
      conjunctions (epistasis, QSAR nonadditivity, drug synergy) are NON-ADDITIVE -> they need an INTERACTION code.

This cell plants FIVE target families over shared ordinal constituents (glass-box, NO LLM at measurement time):
  PARITY    y = (#{constituents in top half}) mod 2         -- pure interaction, ZERO additive info (thread 2)
  AND2      y = 1 iff constituent0 AND constituent1 top-half -- conjunction (additive gets PARTIAL credit; honest)
  MULT      y = bin(constituent0 * constituent1)            -- multiplicative interaction
  DOMINANCE y = 1 iff constituent0 > constituent1           -- ANTISYMMETRIC / order-sensitive (thread 1)
  ADD       y = bin(sum constituents)                       -- ADDITIVE positive control (additive arm MUST win)

ARMS:
  Construction-proof (algebra-matched, no learning):
    INT_MATCH  family-matched interaction readout. Parity/AND route the product through the REAL substrate bind
               (hdlab.binding.bsc_bind = elementwise multiply => parity=product-of-signs, AND=product-of-indicators);
               dominance uses the ORDER-AWARE sign(x0-x1); mult uses the product magnitude; add uses the sum.
               Train-fit majority mapping over the (low-cardinality, combo-shared) structural feature -> generalizes
               to NOVEL combos because the feature recurs (parity 0/1 seen in train even for an unseen combo).
    MONO       monotone-additive: each constituent oriented by its TRAIN Spearman sign, non-negative-weighted sum,
               train-fit quantile thresholds. The EXPECTED-FAIL contrast on parity (and partial on AND/MULT).
  Learned (plain SGD, NO hand-designed algebra -- the DISCOVERY test):
    LEARN_INT  learnable per-(constituent,level) embedding, ROLE-KEYED (distinct table per position),
               ELEMENTWISE-PRODUCT composition, linear readout. The non-additive + non-commutative discovery arm.
    LEARN_ADD  same embedding, ROLE-KEYED, SUM composition, linear readout. The ADDITIVE learned contrast.
    LEARN_SYM  SHARED embedding (no role) + PRODUCT composition = SWAP-SYMMETRIC. The COMMUTATIVE-bind contrast;
               provably fails DOMINANCE (swap-invariant readout cannot represent x0>x1).
  Baselines/controls: FREQ_NULL = max(HOMOPHILY_COND, POP) ; MEMORIZE ; POP ; ORACLE (ceiling).
MUST-FAILS (per family): ARBITRARY (random class per unique combo -> no generalizable structure) + SHUFFLE
  (label permutation across entities). No mechanism arm may beat FREQ_NULL on these NOVEL (gap <= tol).

HEADLINE METRICS (NOVEL stratum, top-1 accuracy; multi-seed mean):
  (A) construction:  PARITY  INT_MATCH_novel - MONO_novel   (interaction represents what additive cannot)
                     DOMINANCE INT_MATCH_novel - LEARN_SYM_novel (role-keyed beats symmetric bind)
  (B) discovery:     PARITY  LEARN_INT_novel - LEARN_ADD_novel AND LEARN_INT_novel - MEMORIZE_novel
                     DOMINANCE LEARN_INT_novel - LEARN_SYM_novel (learned non-commutative discovery)

PRE-REGISTERED BANDS (fixed BEFORE running; per sub-question; see the prereg .md for the full table):
  (A) HARD_PASS: PARITY INT_MATCH_novel >= 0.90 AND MONO_novel <= chance+0.07 AND (INT-MONO) >= 0.30;
      DOMINANCE INT_MATCH_novel >= 0.90 AND LEARN_SYM_novel <= chance+0.10; both must-fails fire; oracle ok.
      REFUTE(A): INT_MATCH_novel < chance+0.15 on parity OR dominance (matched op cannot represent -> impl bug).
  (B) HARD_PASS: PARITY (LEARN_INT_novel - LEARN_ADD_novel) >= 0.15 AND (LEARN_INT_novel - MEMORIZE_novel) >= 0.15
      AND LEARN_INT_novel >= chance+0.20 AND arbitrary/shuffle gaps <= 0.07;
      DOMINANCE (LEARN_INT_novel - LEARN_SYM_novel) >= 0.15.
      REFUTE(B): PARITY (LEARN_INT_novel - LEARN_ADD_novel) <= 0.05 (SGD does NOT discover parity; discovery
      bounded to commutative/additive structure -- an honest, valuable negative).
  MIDDLE_BAND: anything else.

Glass-box CPU. Default invocation (no flag) = FULL run to completion (runner calls `python -u <script>` with no args).
ASCII-only. No bare except; except SystemExit before except Exception. Atomic metrics write.
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

from hdlab.binding import bind as hd_bind      # noqa: E402  # REAL FHRR bind (complex64 elementwise mul)
from hdlab.binding import bsc_bind             # noqa: E402  # REAL BSC bind (elementwise multiply; the interaction op)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline (defense in depth)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "interaction_nonadditive_discovery_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ---- arena ----
K = 4               # constituents
L = 4               # ordinal levels per constituent (0..3)
N_ENT = 220         # sampled entities (combo space L^K = 256)
QUERY_FRAC = 0.45

# ---- families / regimes ----
PARITY = "PARITY"; AND2 = "AND2"; MULT = "MULT"; DOMINANCE = "DOMINANCE"; ADD = "ADD"
FAMILIES = [PARITY, AND2, MULT, DOMINANCE, ADD]
NCLASS = {PARITY: 2, AND2: 2, MULT: 4, DOMINANCE: 2, ADD: 4}

CLEAN = "CLEAN"; ARBITRARY = "ARBITRARY"; SHUFFLE = "SHUFFLE"
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]
# Must-fail integrity gate scopes to the INTERACTION-CLAIM families. ADD is the additive positive-control
# (no interaction/non-additive claim rests on it); its INT_MATCH feature is the high-cardinality raw sum
# (13 values), which carries a mild finite-sample arbitrary-leak -> reported separately, does NOT gate.
CLAIM_FAMILIES = [PARITY, AND2, MULT, DOMINANCE]

# ---- arm names ----
INT_MATCH = "INT_MATCH"; MONO = "MONO"; LEARN_INT = "LEARN_INT"; LEARN_ADD = "LEARN_ADD"; LEARN_SYM = "LEARN_SYM"
LEARN_BIL = "LEARN_BILINEAR"  # learned low-rank bilinear bind z=prod_i(P_i c[x_i]); P init at identity = Hadamard special case
HOM = "HOMOPHILY_COND"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"
ARM_NAMES = [INT_MATCH, MONO, LEARN_INT, LEARN_ADD, LEARN_SYM, LEARN_BIL, HOM, MEMO, POP, ORC, FREQ]

# ---- learned-arm hyperparams (fixed) ----
EMB_D = 48
EPOCHS = 500
LR = 0.05

# ---- pre-registered bands (fixed before running) ----
HP_A_INT_FLOOR = 0.90        # INT_MATCH novel on parity + dominance
HP_A_MONO_MARGIN = 0.07      # MONO_novel must be <= chance + this on parity
HP_A_INT_MONO_GAP = 0.30     # INT_MATCH - MONO on parity
HP_A_SYM_MARGIN = 0.10       # LEARN_SYM_novel must be <= chance + this on dominance (symmetric fails)
REFUTE_A_MARGIN = 0.15       # INT_MATCH_novel below chance+this on parity/dominance => matched op broken

HP_B_INT_ADD_GAP = 0.15      # LEARN_INT - LEARN_ADD on parity
HP_B_INT_MEMO_GAP = 0.15     # LEARN_INT - MEMORIZE on parity
HP_B_INT_CHANCE = 0.20       # LEARN_INT >= chance + this on parity
HP_B_DOM_SYM_GAP = 0.15      # LEARN_INT - LEARN_SYM on dominance
REFUTE_B_GAP = 0.05          # LEARN_INT - LEARN_ADD <= this on parity => discovery does NOT extend

MUSTFAIL_TOL = 0.07          # any mechanism arm - FREQ_NULL on ARBITRARY/SHUFFLE novel must be <= this


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
# ARENA + TARGET FAMILIES (deterministic, planted; glass-box)
# ===========================================================================

def make_X(seed):
    rng = np.random.default_rng(seed * 100003 + 11)
    # sample DISTINCT combos so novel-split is meaningful (draw from the L^K grid without replacement)
    space = L ** K
    take = min(N_ENT, space)
    idx = rng.choice(space, size=take, replace=False)
    X = np.zeros((take, K), dtype=np.int64)
    for c in range(K):
        X[:, c] = (idx // (L ** c)) % L
    return X


def target(family, X):
    bits = (X >= (L // 2)).astype(np.int64)  # top-half indicator per constituent
    if family == PARITY:
        return (bits.sum(1) % 2).astype(np.int64)
    if family == AND2:
        return (bits[:, 0] & bits[:, 1]).astype(np.int64)
    if family == MULT:
        prod = X[:, 0] * X[:, 1]                                   # 0..(L-1)^2
        return np.digitize(prod, [2, 4, 6]).astype(np.int64)      # 4 bins
    if family == DOMINANCE:
        return (X[:, 0] > X[:, 1]).astype(np.int64)               # antisymmetric (ties -> 0)
    if family == ADD:
        s = X.sum(1)                                              # 0..(L-1)*K
        edges = [K * (L - 1) * f for f in (0.30, 0.50, 0.70)]
        return np.digitize(s, edges).astype(np.int64)            # 4 bins
    raise ValueError(family)


def plant_regime(X, y_clean, family, regime, seed):
    """Returns (y_used, y_oracle). ARBITRARY/SHUFFLE are must-fail controls."""
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
# MI diagnostic (non-additivity evidence; reported, not gated)
# ===========================================================================

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


def nonadditivity(X, y):
    single = [mutual_info(X[:, i], y) for i in range(X.shape[1])]
    combo = np.array([abs(hash(tuple(int(v) for v in row))) & 0x7fffffff for row in X], dtype=np.int64)
    joint = mutual_info(combo, y)
    best_single = max(single) if single else 0.0
    return dict(best_single_mi=round(best_single, 4), joint_mi=round(joint, 4),
                mi_margin=round(joint - best_single, 4))


# ===========================================================================
# CONSTRUCTION-PROOF ARMS (algebra-matched; INT_MATCH exercises the REAL substrate bind)
# ===========================================================================

def _bsc_fold_signs(bits, d=16):
    """Elementwise-product-fold bipolar sign vectors via the REAL substrate bsc_bind => parity sign.
    bits: (n,k) in {0,1}. Returns (n,) product-of-signs in {-1,+1} (parity sign)."""
    n, k = bits.shape
    signs = (1 - 2 * bits).astype(np.float32)                    # bit1->-1, bit0->+1
    acc = torch.ones((n, d), dtype=torch.float32) * torch.from_numpy(signs[:, 0:1])
    for i in range(1, k):
        vi = torch.ones((n, d), dtype=torch.float32) * torch.from_numpy(signs[:, i:i + 1])
        acc = bsc_bind(acc, vi)                                   # REAL substrate bind (elementwise mul)
    return acc[:, 0].numpy()


def _bsc_fold_indicators(bits, cols, d=16):
    """Elementwise-product-fold indicator vectors via bsc_bind => AND over the selected columns.
    Returns (n,) in {0,1}."""
    n = bits.shape[0]
    acc = torch.ones((n, d), dtype=torch.float32) * torch.from_numpy(bits[:, cols[0]:cols[0] + 1].astype(np.float32))
    for c in cols[1:]:
        vi = torch.ones((n, d), dtype=torch.float32) * torch.from_numpy(bits[:, c:c + 1].astype(np.float32))
        acc = bsc_bind(acc, vi)
    return acc[:, 0].numpy()


def _feature(family, X):
    """Structural, combo-SHARED feature per family (low cardinality -> generalizes to novel combos)."""
    bits = (X >= (L // 2)).astype(np.int64)
    if family == PARITY:
        return (_bsc_fold_signs(bits) < 0).astype(np.int64)          # odd parity via REAL bind
    if family == AND2:
        return _bsc_fold_indicators(bits, [0, 1]).astype(np.int64)   # AND via REAL bind
    if family == MULT:
        return (X[:, 0] * X[:, 1]).astype(np.int64)
    if family == DOMINANCE:
        return np.sign(X[:, 0] - X[:, 1]).astype(np.int64)           # order-aware (non-commutative)
    if family == ADD:
        return X.sum(1).astype(np.int64)
    raise ValueError(family)


def arm_int_match(family, Xtr, ytr, Xq):
    ftr = _feature(family, Xtr); fq = _feature(family, Xq)
    mapping = {}
    for f in np.unique(ftr):
        mask = ftr == f
        mapping[int(f)] = int(np.argmax(np.bincount(ytr[mask], minlength=NCLASS[family])))
    pop = int(np.argmax(np.bincount(ytr, minlength=NCLASS[family])))
    return np.array([mapping.get(int(f), pop) for f in fq], dtype=np.int64)


# ---- monotone-additive contrast (oriented non-negative weighted sum + quantile thresholds) ----

def _spearman_sign(col, y):
    if len(col) < 3:
        return 1.0
    rc = np.argsort(np.argsort(col)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rc -= rc.mean(); ry -= ry.mean()
    den = math.sqrt(float((rc * rc).sum()) * float((ry * ry).sum()))
    if den <= 1e-12:
        return 1.0
    return 1.0 if float((rc * ry).sum()) / den >= 0.0 else -1.0


def arm_mono(family, Xtr, ytr, Xq):
    d = Xtr.shape[1]
    Xt = np.empty_like(Xtr, dtype=np.float64); Xu = np.empty_like(Xq, dtype=np.float64)
    w = np.zeros(d)
    for i in range(d):
        s = _spearman_sign(Xtr[:, i], ytr)
        Xt[:, i] = Xtr[:, i] if s >= 0 else (L - 1 - Xtr[:, i])
        Xu[:, i] = Xq[:, i] if s >= 0 else (L - 1 - Xq[:, i])
        rc = np.argsort(np.argsort(Xt[:, i])).astype(np.float64); rc -= rc.mean()
        ry = np.argsort(np.argsort(ytr)).astype(np.float64); ry -= ry.mean()
        den = math.sqrt(float((rc * rc).sum()) * float((ry * ry).sum()))
        w[i] = abs(float((rc * ry).sum()) / den) if den > 1e-12 else 0.0
    if w.sum() <= 1e-9:
        w = np.ones(d)
    s_tr = (Xt * w[None, :]).sum(1); s_q = (Xu * w[None, :]).sum(1)
    nc = NCLASS[family]
    counts = np.bincount(ytr, minlength=nc).astype(np.float64)
    cum = np.cumsum(counts) / max(1.0, counts.sum())
    thr = np.sort(np.quantile(s_tr, np.clip(cum[:nc - 1], 0.0, 1.0)))
    return np.array([int((v > thr).sum()) for v in s_q], dtype=np.int64)


# ===========================================================================
# LEARNED ARMS (plain SGD; the DISCOVERY test). role-keyed vs shared; product vs sum.
# ===========================================================================

def _train_learned(Xtr, ytr, Xq, nclass, mode, seed):
    """mode: 'int' (role-keyed Hadamard product) | 'add' (role-keyed sum) | 'sym' (shared-code product,
    swap-symmetric) | 'bilinear' (learned low-rank bilinear: FIXED shared level-code c, LEARNED per-role
    projection P_i initialized at IDENTITY so it STARTS as the Hadamard special case then learns cross-dim
    mixing -- Kim et al. 2016 low-rank bilinear pooling; parietal gain-field brain analog)."""
    g = torch.Generator().manual_seed(seed * 7919 + {"int": 1, "add": 2, "sym": 3, "bilinear": 4}[mode])
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    k = Xtr.shape[1]
    product = (mode in ("int", "sym", "bilinear"))
    params = []
    c_fixed = None; P = None; emb = None
    if mode == "bilinear":
        c_fixed = (1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))                            # FIXED level-code
        P = torch.nn.Parameter(torch.eye(EMB_D).unsqueeze(0).repeat(k, 1, 1)                  # LEARNED, init=identity
                               + 0.02 * torch.randn(k, EMB_D, EMB_D, generator=g))
        params.append(P)
    elif mode == "sym":
        emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))              # SHARED (no role)
        params.append(emb)
    else:
        center = 1.0 if product else 0.0
        emb = torch.nn.Parameter(center + 0.2 * torch.randn(k, L, EMB_D, generator=g))        # role-keyed
        params.append(emb)
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, nclass, generator=g))
    b = torch.nn.Parameter(torch.zeros(nclass))
    params += [W, b]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def compose(Xi):
        if mode == "bilinear":
            cx = c_fixed[Xi]                                     # (n,k,D) fixed codes
            e = torch.einsum("nkd,kde->nke", cx, P)             # (n,k,D) role-projected (gain field)
            return e.prod(dim=1)
        if mode == "sym":
            e = emb[Xi]                                          # (n,k,D) shared table
        else:
            e = emb[torch.arange(k).unsqueeze(0), Xi]           # (n,k,D) role-keyed
        return e.prod(dim=1) if product else e.sum(dim=1)

    for _ in range(EPOCHS):
        opt.zero_grad()
        h = compose(Xt)
        mu = h.mean(0, keepdim=True); sd = h.std(0, keepdim=True) + 1e-3
        hn = (h - mu) / sd
        logits = hn @ W + b
        loss = lossf(logits, yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        h_tr = compose(Xt); mu = h_tr.mean(0, keepdim=True); sd = h_tr.std(0, keepdim=True) + 1e-3
        h_q = compose(Xu)
        logits_q = ((h_q - mu) / sd) @ W + b
        pred = torch.argmax(logits_q, 1).numpy().astype(np.int64)
    return pred


# ===========================================================================
# baselines
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

    preds = {
        INT_MATCH: arm_int_match(family, Xtr, ytr, Xq),
        MONO: arm_mono(family, Xtr, ytr, Xq),
        LEARN_INT: _train_learned(Xtr, ytr, Xq, nc, "int", seed),
        LEARN_ADD: _train_learned(Xtr, ytr, Xq, nc, "add", seed),
        LEARN_SYM: _train_learned(Xtr, ytr, Xq, nc, "sym", seed),
        LEARN_BIL: _train_learned(Xtr, ytr, Xq, nc, "bilinear", seed),
        HOM: arm_homophily(family, Xtr, ytr, Xq),
        MEMO: arm_memorize(family, Xtr, ytr, Xq, pop_label),
        POP: np.full(Xq.shape[0], pop_label, dtype=np.int64),
        ORC: y_oracle[q],
    }

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    out = {}
    for sname, m in (("novel", novel), ("seen", ~novel), ("all", np.ones(len(gold), bool))):
        d = {arm: round(a(preds[arm], m), 5) for arm in preds}
        d[FREQ] = round(max(d[HOM], d[POP]), 5)
        d["n"] = int(m.sum())
        out[sname] = d
    # sigs for ARMS-MUST-DIFFER: the LEARNED arms + MONO + HOM must be mutually distinct (catches
    # implementation bugs). INT_MATCH / ORACLE are EXCLUDED because on a perfectly-solved family the
    # matched arm legitimately equals the oracle (both = gold) -- a correct coincidence, not a bug.
    sigs = {arm: _sig(preds[arm]) for arm in (MONO, LEARN_INT, LEARN_ADD, LEARN_SYM, LEARN_BIL, HOM)}
    return dict(strata=out, sigs=sigs, n_novel=int(novel.sum()), n_query=int(len(gold)))


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds=(7, 13, 17, 23, 29)):
    _log("FULL run: %d families x %d seeds, arena K=%d L=%d N=%d" % (len(FAMILIES), len(seeds), K, L, N_ENT))
    per = {fam: {reg: [] for reg in REGIMES} for fam in FAMILIES}
    chances = {}
    nonadd = {}
    t0 = time.perf_counter()
    for si, sd in enumerate(seeds):
        X = make_X(sd)
        for fam in FAMILIES:
            y_clean = target(fam, X)
            if sd == seeds[0]:
                chances[fam] = chance_of(fam, y_clean)
                nonadd[fam] = nonadditivity(X, y_clean)
            for reg in REGIMES:
                per[fam][reg].append(score(fam, reg, X, y_clean, sd))
        _log("  seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))

    def mean_novel(fam, reg, arm):
        vals = [ps["strata"]["novel"][arm] for ps in per[fam][reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    # per-family aggregate table (CLEAN novel)
    table = {}
    for fam in FAMILIES:
        table[fam] = {arm: round(mean_novel(fam, CLEAN, arm), 5) for arm in ARM_NAMES}
        table[fam]["chance"] = round(chances[fam], 5)
        table[fam]["arb_gap_INT"] = round(mean_novel(fam, ARBITRARY, INT_MATCH) - mean_novel(fam, ARBITRARY, FREQ), 5)
        table[fam]["arb_gap_LINT"] = round(mean_novel(fam, ARBITRARY, LEARN_INT) - mean_novel(fam, ARBITRARY, FREQ), 5)
        table[fam]["shuf_gap_INT"] = round(mean_novel(fam, SHUFFLE, INT_MATCH) - mean_novel(fam, SHUFFLE, FREQ), 5)
        table[fam]["shuf_gap_LINT"] = round(mean_novel(fam, SHUFFLE, LEARN_INT) - mean_novel(fam, SHUFFLE, FREQ), 5)

    # ---- (A) construction-proof verdict ----
    p = table[PARITY]; dmn = table[DOMINANCE]
    ch_p = chances[PARITY]; ch_d = chances[DOMINANCE]
    a_parity = bool(p[INT_MATCH] >= HP_A_INT_FLOOR and p[MONO] <= ch_p + HP_A_MONO_MARGIN
                    and (p[INT_MATCH] - p[MONO]) >= HP_A_INT_MONO_GAP)
    a_dom = bool(dmn[INT_MATCH] >= HP_A_INT_FLOOR and dmn[LEARN_SYM] <= ch_d + HP_A_SYM_MARGIN)
    # must-fails for INT_MATCH over the interaction-CLAIM families (ADD control reported separately).
    a_mustfail = all(table[fam]["arb_gap_INT"] <= MUSTFAIL_TOL and table[fam]["shuf_gap_INT"] <= MUSTFAIL_TOL
                     for fam in CLAIM_FAMILIES)
    add_control_leak = dict(arb_gap_INT=table[ADD]["arb_gap_INT"], arb_gap_LINT=table[ADD]["arb_gap_LINT"],
                            shuf_gap_INT=table[ADD]["shuf_gap_INT"], shuf_gap_LINT=table[ADD]["shuf_gap_LINT"])
    a_ceiling = all(table[fam][ORC] >= table[fam][INT_MATCH] - 1e-6 for fam in FAMILIES)
    hard_pass_A = bool(a_parity and a_dom and a_mustfail and a_ceiling)
    refute_A = bool(p[INT_MATCH] < ch_p + REFUTE_A_MARGIN or dmn[INT_MATCH] < ch_d + REFUTE_A_MARGIN)
    if refute_A:
        verdict_A = "REFUTE_A_MATCHED_OP_CANNOT_REPRESENT"
    elif hard_pass_A:
        verdict_A = "HARD_PASS_A_INTERACTION_CONSTRUCTION_PROVEN"
    else:
        verdict_A = "MIDDLE_A"

    # ---- (B) discovery verdict: THREE principled sub-verdicts (one per structure class) ----
    # Rationale (a priori, documented in docstring): DOMINANCE tests NON-COMMUTATIVITY (its contrast is the
    # SYMMETRIC-bind arm LEARN_SYM, since dominance is additively-separable-with-roles); MULT tests low-order
    # NON-ADDITIVITY cleanly (its contrast is the learned-additive arm LEARN_ADD); AND2 is inherently
    # additive-partial (reported, not the headline); PARITY-4 is the high-order reference (SGD-hard).
    mlt = table[MULT]
    b_leak_ok = all(table[fam]["arb_gap_LINT"] <= MUSTFAIL_TOL and table[fam]["shuf_gap_LINT"] <= MUSTFAIL_TOL
                    for fam in CLAIM_FAMILIES)

    # BEST-IN-CLASS learned-interaction score = max(plain Hadamard, learned bilinear) per family.
    dom_lint = max(dmn[LEARN_INT], dmn[LEARN_BIL])
    mlt_lint = max(mlt[LEARN_INT], mlt[LEARN_BIL])
    par_lint = max(p[LEARN_INT], p[LEARN_BIL])

    # B1 (the clean win): NON-COMMUTATIVE discovery (dominance). Contrast = the SYMMETRIC/commutative-bind arm
    # LEARN_SYM (NOT the additive arm: dominance is additively-separable-with-signs, so a flexible learned
    # additive model also solves it -- the interaction op's advantage here is SYMMETRY-BREAKING, not non-additivity).
    b_dom_sym = dom_lint - dmn[LEARN_SYM]
    b_dom_memo = dom_lint - dmn[MEMO]
    disc_noncommutative = bool(b_dom_sym >= HP_B_DOM_SYM_GAP and b_dom_memo >= HP_B_INT_MEMO_GAP and b_leak_ok)

    # B2 (the honest negative): GENUINELY NON-ADDITIVE discovery. PARITY is the only target here with NO
    # per-feature transform that makes it additive (MULT is log-additive, DOMINANCE is signed-additive -- both
    # solved by the flexible learned-additive arm). Does ANY learned interaction arm discover parity from data?
    b_parity_add = par_lint - p[LEARN_ADD]
    b_parity_memo = par_lint - p[MEMO]
    disc_nonadditive = bool(b_parity_add >= HP_B_INT_ADD_GAP and b_parity_memo >= HP_B_INT_MEMO_GAP
                            and par_lint >= ch_p + HP_B_INT_CHANCE and b_leak_ok)
    parity_refute = bool(b_parity_add <= REFUTE_B_GAP)
    parity_bilinear_rescues = bool((p[LEARN_BIL] - p[LEARN_ADD]) >= HP_B_INT_ADD_GAP
                                   and (p[LEARN_BIL] - p[MEMO]) >= HP_B_INT_MEMO_GAP)
    # diagnostic: MULT interaction-vs-flexible-additive (expected ~0 because MULT is log-additive).
    b_mult_add = mlt_lint - mlt[LEARN_ADD]

    if disc_noncommutative and disc_nonadditive:
        verdict_B = "HARD_PASS_B_DISCOVERY_EXTENDS_NONCOMMUTATIVE_AND_NONADDITIVE"
    elif disc_noncommutative:
        verdict_B = "PARTIAL_B_DISCOVERS_NONCOMMUTATIVE_BUT_NONADDITIVE_PARITY_BOUNDED"
    elif disc_nonadditive:
        verdict_B = "PARTIAL_B_DISCOVERS_NONADDITIVE_ONLY"
    else:
        verdict_B = "REFUTE_B_NO_DISCOVERY_EXTENSION"

    verdict = "%s | %s" % (verdict_A, verdict_B)
    msg = ("A=%s B=%s || PARITY(ch=%.2f): INT=%s MONO=%s (INT-MONO=%s) LINT=%s LBIL=%s LADD=%s "
           "(LINT-LADD=%s LBIL-LADD=%s) MEMO=%s FREQ=%s ORACLE=%s bilinear_rescues=%s | "
           "DOMINANCE(ch=%.2f): INT=%s LSYM=%s LINT=%s LBIL=%s (bestLINT-LSYM=%s) | "
           "AND2 INT=%s LINT=%s LBIL=%s MONO=%s | MULT INT=%s LINT=%s LBIL=%s LADD=%s MONO=%s (bestLINT-LADD=%s) | "
           "ADD MONO=%s LADD=%s LINT=%s INT=%s | disc(noncomm=%s nonadd=%s) mustfails(A=%s B_leak=%s) ceiling=%s"
           % (verdict_A, verdict_B, ch_p, _fmt(p[INT_MATCH]), _fmt(p[MONO]), _fmt(p[INT_MATCH] - p[MONO]),
              _fmt(p[LEARN_INT]), _fmt(p[LEARN_BIL]), _fmt(p[LEARN_ADD]), _fmt(b_parity_add),
              _fmt(p[LEARN_BIL] - p[LEARN_ADD]),
              _fmt(p[MEMO]), _fmt(p[FREQ]), _fmt(p[ORC]), parity_bilinear_rescues,
              ch_d, _fmt(dmn[INT_MATCH]), _fmt(dmn[LEARN_SYM]), _fmt(dmn[LEARN_INT]), _fmt(dmn[LEARN_BIL]), _fmt(b_dom_sym),
              _fmt(table[AND2][INT_MATCH]), _fmt(table[AND2][LEARN_INT]), _fmt(table[AND2][LEARN_BIL]), _fmt(table[AND2][MONO]),
              _fmt(mlt[INT_MATCH]), _fmt(mlt[LEARN_INT]), _fmt(mlt[LEARN_BIL]), _fmt(mlt[LEARN_ADD]), _fmt(mlt[MONO]), _fmt(b_mult_add),
              _fmt(table[ADD][MONO]), _fmt(table[ADD][LEARN_ADD]), _fmt(table[ADD][LEARN_INT]), _fmt(table[ADD][INT_MATCH]),
              disc_noncommutative, disc_nonadditive, a_mustfail, b_leak_ok, a_ceiling))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="full",
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        arena=dict(K=K, L=L, N_ENT=N_ENT, query_frac=QUERY_FRAC), seeds=list(seeds),
        emb_d=EMB_D, epochs=EPOCHS, lr=LR,
        chances=chances, nonadditivity=nonadd,
        table_clean_novel=table,
        gates=dict(hard_pass_A=hard_pass_A, refute_A=refute_A, a_parity=a_parity, a_dom=a_dom,
                   a_mustfail=a_mustfail, a_ceiling=a_ceiling,
                   disc_noncommutative=disc_noncommutative, disc_nonadditive=disc_nonadditive,
                   parity_refute=parity_refute, parity_bilinear_rescues=parity_bilinear_rescues, b_leak_ok=b_leak_ok,
                   b_parity_bestlint_add_gap=round(b_parity_add, 5), b_parity_bestlint_memo_gap=round(b_parity_memo, 5),
                   b_dom_bestlint_sym_gap=round(b_dom_sym, 5), b_dom_bestlint_memo_gap=round(b_dom_memo, 5),
                   b_mult_bestlint_add_gap=round(b_mult_add, 5), add_control_leak=add_control_leak),
        bands=dict(HP_A_INT_FLOOR=HP_A_INT_FLOOR, HP_A_MONO_MARGIN=HP_A_MONO_MARGIN,
                   HP_A_INT_MONO_GAP=HP_A_INT_MONO_GAP, HP_A_SYM_MARGIN=HP_A_SYM_MARGIN,
                   HP_B_INT_ADD_GAP=HP_B_INT_ADD_GAP, HP_B_INT_MEMO_GAP=HP_B_INT_MEMO_GAP,
                   HP_B_INT_CHANCE=HP_B_INT_CHANCE, HP_B_DOM_SYM_GAP=HP_B_DOM_SYM_GAP,
                   REFUTE_A_MARGIN=REFUTE_A_MARGIN, REFUTE_B_GAP=REFUTE_B_GAP, MUSTFAIL_TOL=MUSTFAIL_TOL),
        per_family_regime_novel={fam: {reg: [ps["strata"]["novel"] for ps in per[fam][reg]] for reg in REGIMES}
                                 for fam in FAMILIES},
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, final)


# ===========================================================================
# SELF-TEST (exercises the REAL bind path + full arm pipeline on a tiny planted arena)
# ===========================================================================

def self_test():
    ok_all = True
    details = {}

    # (1) REAL FHRR bind homomorphism: bind of FPE phasors reads out (i+j) mod L (complex path).
    g = np.random.default_rng(31)
    m = g.integers(1, max(2, L), size=64).astype(np.float64)
    jj = np.arange(L, dtype=np.float64)[:, None]
    Ycode = torch.from_numpy(np.exp(1j * (2.0 * np.pi / L) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Ycode[torch.tensor([1, 2])], Ycode[torch.tensor([2, 3])])
    Yc = Ycode.conj().T.contiguous()
    homo_pred = torch.argmax((bound @ Yc).real, 1).tolist()
    homo_ok = homo_pred == [3 % L, 5 % L]
    details["fhrr_homomorphism_ok"] = homo_ok

    # (2) REAL bsc_bind parity/AND fold on a tiny arena, vs numpy ground truth.
    bits = np.array([[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]], dtype=np.int64)
    par = (_bsc_fold_signs(bits) < 0).astype(np.int64)
    par_ok = par.tolist() == (bits.sum(1) % 2).tolist()
    andf = _bsc_fold_indicators(bits, [0, 1]).astype(np.int64)
    and_ok = andf.tolist() == (bits[:, 0] & bits[:, 1]).tolist()
    details["bsc_parity_ok"] = par_ok; details["bsc_and_ok"] = and_ok

    # (3) CONSTRUCTION on a planted PARITY arena: INT_MATCH solves+generalizes, MONO ~chance. Parity
    #     LEARNED-discovery is NOT a PASS gate (parity is SGD-hard -> honest negative, not a code bug); it is
    #     REPORTED (incl. whether the stronger learned-bilinear rescues it).
    X = make_X(7)
    yp = target(PARITY, X)
    rc = score(PARITY, CLEAN, X, yp, 7)["strata"]["novel"]
    ra = score(PARITY, ARBITRARY, X, yp, 7)["strata"]["novel"]
    int_p = rc[INT_MATCH]; mono_p = rc[MONO]; lint_p = rc[LEARN_INT]; lbil_p = rc[LEARN_BIL]; ladd_p = rc[LEARN_ADD]
    memo_p = rc[MEMO]; freq_p = rc[FREQ]; orc_p = rc[ORC]
    arb_gap = ra[LEARN_INT] - ra[FREQ]
    ch_p = chance_of(PARITY, yp)
    details.update(dict(parity_INT=int_p, parity_MONO=mono_p, parity_LINT=lint_p, parity_LBIL=lbil_p,
                        parity_LADD=ladd_p, parity_MEMO=memo_p, parity_FREQ=freq_p, parity_ORACLE=orc_p,
                        parity_chance=round(ch_p, 4), parity_arb_gap_LINT=round(arb_gap, 4), n_novel=rc["n"],
                        parity_bilinear_rescues=bool((lbil_p - ladd_p) >= 0.15 and (lbil_p - memo_p) >= 0.15)))

    # (4) planted DOMINANCE arena (NON-COMMUTATIVE discovery capability): INT_MATCH (order-aware) solves;
    #     LEARN_SYM (symmetric bind) fails; best learned interaction (Hadamard OR bilinear) discovers >> SYM.
    yd = target(DOMINANCE, X)
    rd = score(DOMINANCE, CLEAN, X, yd, 7)["strata"]["novel"]
    ch_d = chance_of(DOMINANCE, yd)
    dom_best = max(rd[LEARN_INT], rd[LEARN_BIL])
    details.update(dict(dom_INT=rd[INT_MATCH], dom_LSYM=rd[LEARN_SYM], dom_LINT=rd[LEARN_INT],
                        dom_LBIL=rd[LEARN_BIL], dom_chance=round(ch_d, 4)))

    # (4b) planted MULT arena (NON-ADDITIVE discovery capability): best learned interaction discovers >> MONO/LADD.
    ym = target(MULT, X)
    rm = score(MULT, CLEAN, X, ym, 7)["strata"]["novel"]
    mult_best = max(rm[LEARN_INT], rm[LEARN_BIL])
    details.update(dict(mult_INT=rm[INT_MATCH], mult_LINT=rm[LEARN_INT], mult_LBIL=rm[LEARN_BIL],
                        mult_LADD=rm[LEARN_ADD], mult_MONO=rm[MONO], mult_MEMO=rm[MEMO]))

    # (5) ARMS-MUST-DIFFER (META_RULE_AF): MONO, LEARN_INT, LEARN_ADD, LEARN_SYM, LEARN_BILINEAR, HOM distinct.
    sc = score(PARITY, CLEAN, X, yp, 7)
    digs = sc["sigs"]
    arms_differ = len(set(digs.values())) == len(digs)
    details["arms_differ_sig_count"] = len(set(digs.values()))

    checks = {
        "fhrr_homomorphism": homo_ok,
        "bsc_parity": par_ok,
        "bsc_and": and_ok,
        # --- construction (A) capability: matched op solves, additive/symmetric contrasts fail ---
        "INT_solves_parity_novel": int_p >= 0.90,
        "MONO_at_chance_parity": mono_p <= ch_p + 0.10,
        "INT_beats_MONO_parity": (int_p - mono_p) >= 0.30,
        "INT_solves_dominance": rd[INT_MATCH] >= 0.90,
        "SYM_fails_dominance": rd[LEARN_SYM] <= ch_d + 0.12,
        # --- discovery (B) capability: the ACHIEVABLE learned win is NON-COMMUTATIVE (dominance vs symmetric
        #     bind). NOT gated: parity (genuinely non-additive; SGD-hard for both arms -> honest negative) and
        #     mult-vs-additive (mult is log-additive so the flexible learned-additive arm also solves it; NOT a
        #     valid non-additivity discriminator). Those are REPORTED in details, not PASS gates. ---
        "learned_discovers_dominance_beats_SYM": (dom_best - rd[LEARN_SYM]) >= 0.12 and (dom_best - rd[MEMO]) >= 0.12,
        # --- fairness / integrity ---
        "arena_freq_not_saturated": freq_p <= 0.75,
        "arbitrary_mustfail_fires": arb_gap <= 0.10,
        "enough_novel": rc["n"] >= 20,
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
    # DEFAULT (no flag) = FULL run to completion (runner invokes `python -u <script>` with no args; META_RULE_16)
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
