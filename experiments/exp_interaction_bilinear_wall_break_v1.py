"""INTERACTION_BILINEAR_WALL_BREAK (v1): does a LEARNED LOW-RANK BILINEAR bind break the COMMUTATIVITY WALL?

PRIOR ARC (inlined; NO re-hunt):
  (1) exp_interaction_nonadditive_discovery_v1 (commit 59056b6d4) localized the ROLE-KEYING<->SYMMETRY TENSION:
      the SYMMETRIC-product bind (shared code, elementwise product) DISCOVERS symmetric PARITY (~0.98 vs additive
      ~0.38) but provably FAILS antisymmetric DOMINANCE (swap-invariant readout cannot represent x0>x1); a
      ROLE-KEYED bind does DOMINANCE but OVER-parameterizes and FAILS PARITY on NOVEL combos. NO single FIXED
      composition op discovers both.
  (2) exp_joint_dual_channel_readout_v1 (commit 947d8c913) landed MIDDLE: a joint code + TWO selective readout
      heads discovers BOTH (PARITY JD_CONFIG=0.816 vs SYM_PROD specialist 0.976; DOMINANCE JD_ORDER=1.0 vs
      ROLE_KEY 0.998), but with CROSS-CHANNEL INTERFERENCE OVER TOLERANCE -- the two-head design pays an
      inherent joint-coding cost. That is the two-head lever.
  (3) brain-nonadditive drill (a48d3739, notes/drill_brain_nonadditive_interaction_relational_coding_bestinclass_
      2026-07-14.md): #1 substrate recommendation = a LEARNED LOW-RANK BILINEAR / gated-multiplicative bind
      z = (P a) (*) (Q b) with P,Q LEARNED (Kim et al. 2016 low-rank bilinear pooling; parietal gain-field
      analog). Our elementwise bind is the P=Q=I special case, so learning P,Q is a MINIMAL learnable upgrade
      (not a construct). Substrate already has GHRR matrix-vector bind (non-commutative) as a cheaper precedent.

THE QUESTION (this cell): a MINIMAL learnable upgrade of the elementwise/symmetric bind -- a per-role LOW-RANK
  bilinear projection P_i = I + U_i V_i^T (rank R, U_i,V_i ZERO-init so at init P_i=I and the op is EXACTLY the
  elementwise/symmetric-product LEARN_SYM special case) on a SHARED learnable code, folded by product. When the
  learned P_i stay ~equal across roles the op is swap-symmetric (parity-capable); when they differentiate per
  role the op becomes order-sensitive (dominance-capable). Can ONE such learned op discover BOTH parity AND
  dominance on NOVEL combos -- each within tolerance of the RESPECTIVE specialist (symmetric-product for parity,
  role-keyed for dominance) -- WITHOUT the role-keying<->symmetry tension? That would BREAK the commutativity
  wall with a single enriched operator (cheaper than the joint-code + two-head design).

ARMS (glass-box CPU; NO LLM at measurement):
  Construction-proof (algebra-matched, no learning; reused from prior arc):
    INT_MATCH  family-matched interaction readout (parity/AND via the REAL substrate FHRR bind = complex
               elementwise mul; dominance via order-aware sign(x0-x1)). SANITY that the arena is solvable.
    MONO       monotone-additive (oriented non-negative weighted sum + quantile thresholds). Additive contrast.
  Learned (plain Adam SGD; the DISCOVERY test):
    LEARN_SYM  SHARED code + PRODUCT composition = swap-SYMMETRIC = the ELEMENTWISE (P=Q=I) baseline + the
               PARITY specialist. HERO must MATCH this on parity.
    LEARN_INT  ROLE-KEYED code + PRODUCT composition. Asymmetric specialist.
    LEARN_ADD  ROLE-KEYED code + SUM composition. Additive learned contrast; the DOMINANCE specialist (dominance
               is additively-separable-given-roles). HERO must MATCH max(role-keyed) on dominance.
    LEARN_BILINEAR_RANK1  *** HERO *** SHARED code + per-role RANK-1 bilinear P_i=I+u_i v_i^T (u,v zero-init) +
               PRODUCT composition. At init == LEARN_SYM (P=Q=I). The minimal learnable commutativity-break lever.
    LEARN_BILINEAR_RANK4  diagnostic: same, rank-4 (rank-effect; REPORTED, NOT gated).
  Baselines/controls: FREQ_NULL=max(HOMOPHILY_COND,POP); MEMORIZE; POP; ORACLE (ceiling).
MUST-FAILS (per family): ARBITRARY (random class per unique combo) + SHUFFLE (label permutation). The HERO must
  NOT beat FREQ_NULL on these NOVEL (gap <= MUSTFAIL_TOL) -- else it is fitting noise, not structure.

TARGET FAMILIES over shared ordinal constituents (K=4 constituents, L=4 levels):
  PARITY    y = (#{constituents top-half}) mod 2   SYMMETRIC non-additive (ZERO additive info) -> SYM specialist
  DOMINANCE y = 1 iff x0 > x1                       ANTISYMMETRIC / order-sensitive -> role-keyed specialist
  AND2/MULT                                         transform-additive diagnostics (REPORTED, not gated)
  ADD       y = bin(sum)                            additive positive control (must-fail scope excludes ADD)

HEADLINE (NOVEL stratum, CLEAN, top-1 accuracy, multi-seed mean): the WALL-BREAK head-to-head --
  PARITY:    HERO(RANK1) vs LEARN_SYM (specialist) vs LEARN_ADD (additive floor) vs FREQ_NULL
  DOMINANCE: HERO(RANK1) vs max(role-keyed) (specialist) vs LEARN_SYM (elementwise) vs FREQ_NULL

PRE-REGISTERED BANDS (fixed BEFORE running; see the prereg .md). All on NOVEL CLEAN. TOL_SPEC=0.10.
  parity_ok    = HERO_par >= SYM_par - TOL_SPEC AND HERO_par >= chance_p + 0.20 AND HERO_par - LADD_par >= 0.15
                 AND HERO_par - FREQ_par >= 0.15
  dominance_ok = HERO_dom >= role_spec_dom - TOL_SPEC AND HERO_dom - FREQ_dom >= 0.10 AND HERO_dom - SYM_dom >= 0.15
  HARD_PASS_WALL_BROKEN = parity_ok AND dominance_ok AND mustfails_fire AND ceiling_ok   (ONE learned op does BOTH)
  HARD_FAIL_ANOTHER_SPECIALIST = exactly ONE of {parity_ok, dominance_ok}  (the wall holds; still a specialist)
  HARD_FAIL_TIES_ELEMENTWISE   = neither solved AND HERO_dom - SYM_dom < 0.05 (no gain over elementwise; joint-
                                 code two-head design remains necessary)
  HARD_FAIL_MUSTFAIL_BREACH    = HERO beats FREQ_NULL on ARBITRARY/SHUFFLE (fitting noise) -- invalidates claims
  REFUTE_IMPL = INT_MATCH cannot solve parity or dominance (arena/impl broken; downstream untrusted)
  MIDDLE_BAND = anything else (e.g. both fail but not a clean tie -> inconclusive / under-trained)

Determinism: all RNG seeds from INTEGER indices (FAM_IDX/REG_IDX), NEVER Python salted built-in hashing (the
false-REFUTE root cause found by the prior VET). Glass-box CPU. Default (no flag) = FULL run. ASCII-only. No bare except;
except SystemExit before except Exception. Atomic metrics write.
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
# NOTE: use ONLY the long-stable `bind` (present on both local + remote runner). The multiplicative interaction
# fold routes through hd_bind on COMPLEX64 tensors -> hits bind's `a.is_complex() -> a*b` elementwise path.
# Do NOT import newer siblings -- remote hdlab/binding.py drift.

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline (defense in depth)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "interaction_bilinear_wall_break_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ---- arena (SAME as the VET-clean discovery arena exp_interaction_nonadditive_discovery_v1) ----
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
CLAIM_FAMILIES = [PARITY, AND2, MULT, DOMINANCE]  # ADD is the additive control; excluded from must-fail scope
# Deterministic integer indices for RNG seeding (NEVER Python built-in hashing -- salted per-process = nondeterministic).
FAM_IDX = {f: i for i, f in enumerate(FAMILIES)}
REG_IDX = {r: i for i, r in enumerate(REGIMES)}

# ---- arm names ----
INT_MATCH = "INT_MATCH"; MONO = "MONO"
LEARN_INT = "LEARN_INT"; LEARN_ADD = "LEARN_ADD"; LEARN_SYM = "LEARN_SYM"
LEARN_BR1 = "LEARN_BILINEAR_RANK1"     # HERO: shared code + per-role rank-1 P=I+uv^T (zero-init) + product
LEARN_BR4 = "LEARN_BILINEAR_RANK4"     # diagnostic: rank-4 (reported, not gated)
HOM = "HOMOPHILY_COND"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"
ARM_NAMES = [INT_MATCH, MONO, LEARN_INT, LEARN_ADD, LEARN_SYM, LEARN_BR1, LEARN_BR4, HOM, MEMO, POP, ORC, FREQ]

# ---- learned-arm hyperparams (fixed a priori; MATCH the prior VET-clean cell to avoid design-to-pass) ----
EMB_D = 48
EPOCHS = 500
LR = 0.05
RANK1 = 1
RANK4 = 4
BIL_REG = 1.0e-3    # modest weight-decay on the low-rank factors -> Occam bias toward the elementwise (P=I)
#                     special case unless the data demands asymmetry. FIXED a priori (calibration_check=default).

# ---- pre-registered bands (fixed before running) ----
TOL_SPEC = 0.10             # HERO within this of the RESPECTIVE specialist on each family
PAR_CHANCE_MARGIN = 0.20    # HERO_par >= chance_p + this
PAR_ADD_GAP = 0.15          # HERO_par - LEARN_ADD (beats the additive floor)
PAR_FREQ_GAP = 0.15         # HERO_par - FREQ_NULL
DOM_FREQ_MARGIN = 0.10      # HERO_dom - FREQ_NULL (HONEST antisymmetric baseline)
DOM_SYM_GAP = 0.15          # HERO_dom - LEARN_SYM (beats the elementwise/symmetric arm = breaks commutativity)
TIE_ELEMENTWISE_EPS = 0.05  # |HERO_dom - SYM_dom| below this AND dom unsolved = ties elementwise (no gain)
REFUTE_INT_FLOOR = 0.90     # INT_MATCH must solve parity + dominance (arena sanity); else REFUTE_IMPL
MUSTFAIL_TOL = 0.10         # HERO - FREQ_NULL on ARBITRARY/SHUFFLE novel must be <= this (matches prior cell)

EXPECTED_N_UNITS = len(FAMILIES) * len(REGIMES)  # per seed; cardinality sanity (not a sweep-axis cell)


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
    c = np.bincount(y_all, minlength=NCLASS[family]).astype(np.float64)
    return float(c.max() / max(1.0, c.sum()))


# ===========================================================================
# ARENA + TARGET FAMILIES (deterministic, planted; glass-box)
# ===========================================================================

def make_X(seed):
    rng = np.random.default_rng(seed * 100003 + 11)
    space = L ** K
    take = min(N_ENT, space)
    idx = rng.choice(space, size=take, replace=False)
    X = np.zeros((take, K), dtype=np.int64)
    for c in range(K):
        X[:, c] = (idx // (L ** c)) % L
    return X


def target(family, X):
    bits = (X >= (L // 2)).astype(np.int64)
    if family == PARITY:
        return (bits.sum(1) % 2).astype(np.int64)
    if family == AND2:
        return (bits[:, 0] & bits[:, 1]).astype(np.int64)
    if family == MULT:
        prod = X[:, 0] * X[:, 1]
        return np.digitize(prod, [2, 4, 6]).astype(np.int64)
    if family == DOMINANCE:
        return (X[:, 0] > X[:, 1]).astype(np.int64)
    if family == ADD:
        s = X.sum(1)
        edges = [K * (L - 1) * f for f in (0.30, 0.50, 0.70)]
        return np.digitize(s, edges).astype(np.int64)
    raise ValueError(family)


def plant_regime(X, y_clean, family, regime, seed):
    n = X.shape[0]
    rng = np.random.default_rng(seed * 100057 + FAM_IDX[family] * 131 + REG_IDX[regime] * 17)  # deterministic
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
# non-additivity diagnostic (reported, not gated)
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
    combo = np.array([int(sum(int(v) * (L ** i) for i, v in enumerate(row))) for row in X], dtype=np.int64)
    joint = mutual_info(combo, y)
    best_single = max(single) if single else 0.0
    return dict(best_single_mi=round(best_single, 4), joint_mi=round(joint, 4),
                mi_margin=round(joint - best_single, 4))


# ===========================================================================
# CONSTRUCTION-PROOF ARMS (algebra-matched; INT_MATCH exercises the REAL substrate bind)
# ===========================================================================

def _mult_fold_signs(bits, d=16):
    """Product-fold bipolar signs through the REAL FHRR bind (complex path) => parity sign. (n,)->{-1,+1}."""
    n, k = bits.shape
    signs = (1 - 2 * bits).astype(np.float32)
    acc = torch.ones((n, d), dtype=torch.complex64) * torch.from_numpy(signs[:, 0:1]).to(torch.complex64)
    for i in range(1, k):
        vi = torch.ones((n, d), dtype=torch.complex64) * torch.from_numpy(signs[:, i:i + 1]).to(torch.complex64)
        acc = hd_bind(acc, vi)
    return acc[:, 0].real.numpy()


def _mult_fold_indicators(bits, cols, d=16):
    """Product-fold indicators through the REAL FHRR bind (complex path) => AND over cols. (n,)->{0,1}."""
    n = bits.shape[0]
    acc = (torch.ones((n, d), dtype=torch.complex64)
           * torch.from_numpy(bits[:, cols[0]:cols[0] + 1].astype(np.float32)).to(torch.complex64))
    for c in cols[1:]:
        vi = torch.ones((n, d), dtype=torch.complex64) * torch.from_numpy(bits[:, c:c + 1].astype(np.float32)).to(torch.complex64)
        acc = hd_bind(acc, vi)
    return acc[:, 0].real.numpy()


def _feature(family, X):
    bits = (X >= (L // 2)).astype(np.int64)
    if family == PARITY:
        return (_mult_fold_signs(bits) < 0).astype(np.int64)
    if family == AND2:
        return np.rint(_mult_fold_indicators(bits, [0, 1])).astype(np.int64)
    if family == MULT:
        return (X[:, 0] * X[:, 1]).astype(np.int64)
    if family == DOMINANCE:
        return np.sign(X[:, 0] - X[:, 1]).astype(np.int64)
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
# LEARNED ARMS (plain Adam SGD; the DISCOVERY test)
#   mode 'int'  = role-keyed product        (asymmetric specialist)
#   mode 'add'  = role-keyed sum            (additive learned contrast / dominance specialist)
#   mode 'sym'  = shared-code product       (swap-symmetric = ELEMENTWISE P=Q=I = parity specialist)
#   mode 'bilinear' (rank R) = shared code + per-role LOW-RANK P_i = I + U_i V_i^T (U,V zero-init) + product.
#       At init (U=V=0) P_i=I -> z=prod_i(emb[x_i]) EXACTLY == the 'sym' op (the elementwise/symmetric special
#       case). Learned P_i equal-across-roles -> stays swap-symmetric (parity); differentiated -> order-sensitive
#       (dominance). Kim et al. 2016 low-rank bilinear pooling; parietal gain-field analog. THE HERO / diagnostic.
# ===========================================================================

def _train_learned(Xtr, ytr, Xq, nclass, mode, seed, rank=None):
    mode_key = {"int": 1, "add": 2, "sym": 3, "bilinear": 4}[mode] + (rank or 0) * 1000
    g = torch.Generator().manual_seed(seed * 7919 + mode_key)
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    k = Xtr.shape[1]
    product = (mode in ("int", "sym", "bilinear"))
    params = []
    emb = None; U = None; V = None
    if mode == "bilinear":
        emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))         # SHARED code (like sym)
        U = torch.nn.Parameter(torch.zeros(k, EMB_D, rank))                              # low-rank, ZERO-init
        V = torch.nn.Parameter(torch.zeros(k, EMB_D, rank))                              # -> P_i = I at init
        params += [emb, U, V]
    elif mode == "sym":
        emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))         # SHARED (no role)
        params.append(emb)
    else:
        center = 1.0 if product else 0.0
        emb = torch.nn.Parameter(center + 0.2 * torch.randn(k, L, EMB_D, generator=g))   # role-keyed
        params.append(emb)
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, nclass, generator=g))
    b = torch.nn.Parameter(torch.zeros(nclass))
    params += [W, b]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def compose(Xi):
        if mode == "bilinear":
            e_base = emb[Xi]                                    # (n,k,D) shared code
            proj = torch.einsum("nkd,kdr->nkr", e_base, V)      # (n,k,R)  V_i^T e
            delta = torch.einsum("nkr,kdr->nkd", proj, U)       # (n,k,D)  U_i (V_i^T e)
            e = e_base + delta                                  # P_i e = e + U_i V_i^T e (rank-R gain field)
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
        if mode == "bilinear":
            loss = loss + BIL_REG * (U.pow(2).sum() + V.pow(2).sum())   # Occam bias toward P=I (elementwise)
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
        LEARN_BR1: _train_learned(Xtr, ytr, Xq, nc, "bilinear", seed, rank=RANK1),
        LEARN_BR4: _train_learned(Xtr, ytr, Xq, nc, "bilinear", seed, rank=RANK4),
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
    # ARMS-MUST-DIFFER (META_RULE_AF): the LEARNED arms + MONO + HOM mutually distinct (catches impl bugs).
    # INT_MATCH / ORACLE excluded (a correctly-solved family legitimately equals the oracle).
    sigs = {arm: _sig(preds[arm]) for arm in (MONO, LEARN_INT, LEARN_ADD, LEARN_SYM, LEARN_BR1, LEARN_BR4, HOM)}
    return dict(strata=out, sigs=sigs, n_novel=int(novel.sum()), n_query=int(len(gold)))


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds=(7, 13, 17, 23, 29)):
    _log("FULL run: %d families x %d seeds, arena K=%d L=%d N=%d (EXPECTED_N_UNITS/seed=%d)"
         % (len(FAMILIES), len(seeds), K, L, N_ENT, EXPECTED_N_UNITS))
    per = {fam: {reg: [] for reg in REGIMES} for fam in FAMILIES}
    chances = {}; nonadd = {}
    t0 = time.perf_counter()
    n_units = 0
    for si, sd in enumerate(seeds):
        X = make_X(sd)
        for fam in FAMILIES:
            y_clean = target(fam, X)
            if sd == seeds[0]:
                chances[fam] = chance_of(fam, y_clean)
                nonadd[fam] = nonadditivity(X, y_clean)
            for reg in REGIMES:
                per[fam][reg].append(score(fam, reg, X, y_clean, sd))
                n_units += 1
        _log("  seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))
    cardinality_ok = bool(n_units == EXPECTED_N_UNITS * len(seeds))

    def mean_novel(fam, reg, arm):
        vals = [ps["strata"]["novel"][arm] for ps in per[fam][reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    table = {}
    for fam in FAMILIES:
        table[fam] = {arm: round(mean_novel(fam, CLEAN, arm), 5) for arm in ARM_NAMES}
        table[fam]["chance"] = round(chances[fam], 5)
        for tag, arm in (("INT", INT_MATCH), ("BR1", LEARN_BR1), ("SYM", LEARN_SYM), ("INTk", LEARN_INT)):
            table[fam]["arb_gap_%s" % tag] = round(mean_novel(fam, ARBITRARY, arm) - mean_novel(fam, ARBITRARY, FREQ), 5)
            table[fam]["shuf_gap_%s" % tag] = round(mean_novel(fam, SHUFFLE, arm) - mean_novel(fam, SHUFFLE, FREQ), 5)

    p = table[PARITY]; dmn = table[DOMINANCE]
    ch_p = chances[PARITY]; ch_d = chances[DOMINANCE]

    # ---- REFUTE guard: arena/impl sanity (INT_MATCH matched op must solve both) ----
    refute_impl = bool(p[INT_MATCH] < REFUTE_INT_FLOOR or dmn[INT_MATCH] < REFUTE_INT_FLOOR)

    # ---- WALL-BREAK head-to-head (all on NOVEL CLEAN) ----
    hero_par = p[LEARN_BR1]; hero_dom = dmn[LEARN_BR1]
    sym_par = p[LEARN_SYM]; sym_dom = dmn[LEARN_SYM]
    add_par = p[LEARN_ADD]; freq_par = p[FREQ]; freq_dom = dmn[FREQ]
    role_spec_dom = max(dmn[LEARN_INT], dmn[LEARN_ADD])   # role-keyed dominance specialist

    parity_ok = bool(hero_par >= sym_par - TOL_SPEC and hero_par >= ch_p + PAR_CHANCE_MARGIN
                     and (hero_par - add_par) >= PAR_ADD_GAP and (hero_par - freq_par) >= PAR_FREQ_GAP)
    dominance_ok = bool(hero_dom >= role_spec_dom - TOL_SPEC and (hero_dom - freq_dom) >= DOM_FREQ_MARGIN
                        and (hero_dom - sym_dom) >= DOM_SYM_GAP)

    # must-fails for the HERO over interaction-CLAIM families (ADD control reported separately).
    hero_mustfail_ok = all(table[fam]["arb_gap_BR1"] <= MUSTFAIL_TOL and table[fam]["shuf_gap_BR1"] <= MUSTFAIL_TOL
                           for fam in CLAIM_FAMILIES)
    ceiling_ok = all(table[fam][ORC] >= table[fam][LEARN_BR1] - 1e-6 for fam in FAMILIES)
    add_control_leak = dict(arb_gap_BR1=table[ADD]["arb_gap_BR1"], shuf_gap_BR1=table[ADD]["shuf_gap_BR1"])

    n_solved = int(parity_ok) + int(dominance_ok)
    ties_elementwise = bool((not dominance_ok) and abs(hero_dom - sym_dom) < TIE_ELEMENTWISE_EPS)

    if refute_impl:
        verdict = "REFUTE_IMPL_MATCHED_OP_CANNOT_SOLVE_ARENA"
    elif not hero_mustfail_ok:
        verdict = "HARD_FAIL_MUSTFAIL_BREACH_HERO_FITS_NOISE"
    elif n_solved == 2 and ceiling_ok:
        verdict = "HARD_PASS_WALL_BROKEN_ONE_LEARNED_OP_DOES_BOTH"
    elif n_solved == 1:
        which = "PARITY_ONLY" if parity_ok else "DOMINANCE_ONLY"
        verdict = "HARD_FAIL_BILINEAR_IS_ANOTHER_SPECIALIST_%s" % which
    elif n_solved == 0 and ties_elementwise:
        verdict = "HARD_FAIL_BILINEAR_TIES_ELEMENTWISE_NO_GAIN"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    # diagnostics (NOT gates)
    b_mult_add = round(max(table[MULT][LEARN_INT], table[MULT][LEARN_BR1]) - table[MULT][LEARN_ADD], 5)
    b_and2_add = round(max(table[AND2][LEARN_INT], table[AND2][LEARN_BR1]) - table[AND2][LEARN_ADD], 5)
    rank_effect_par = round(p[LEARN_BR4] - p[LEARN_BR1], 5)
    rank_effect_dom = round(dmn[LEARN_BR4] - dmn[LEARN_BR1], 5)

    msg = ("%s || PARITY(ch=%.2f,SYMM): HERO_R1=%s SYM=%s(spec) LADD=%s FREQ=%s (R1-SYM=%s R1-LADD=%s) parity_ok=%s | "
           "DOMINANCE(ch=%.2f,freq=%s,ANTISYM): HERO_R1=%s roleSpec=%s SYM=%s (R1-role=%s R1-SYM=%s R1-FREQ=%s) dom_ok=%s | "
           "n_solved=%d ties_elem=%s | INT_MATCH par=%s dom=%s (refute=%s) | "
           "rank4 par=%s dom=%s (R4-R1 par=%s dom=%s) | AND2 int-add=%s MULT int-add=%s | "
           "hero_mustfail_ok=%s ceiling=%s cardinality_ok=%s | ADDleak=%s"
           % (verdict, ch_p, _fmt(hero_par), _fmt(sym_par), _fmt(add_par), _fmt(freq_par),
              _fmt(hero_par - sym_par), _fmt(hero_par - add_par), parity_ok,
              ch_d, _fmt(freq_dom), _fmt(hero_dom), _fmt(role_spec_dom), _fmt(sym_dom),
              _fmt(hero_dom - role_spec_dom), _fmt(hero_dom - sym_dom), _fmt(hero_dom - freq_dom), dominance_ok,
              n_solved, ties_elementwise, _fmt(p[INT_MATCH]), _fmt(dmn[INT_MATCH]), refute_impl,
              _fmt(p[LEARN_BR4]), _fmt(dmn[LEARN_BR4]), _fmt(rank_effect_par), _fmt(rank_effect_dom),
              _fmt(b_and2_add), _fmt(b_mult_add), hero_mustfail_ok, ceiling_ok, cardinality_ok,
              json.dumps(add_control_leak)))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="full",
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        arena=dict(K=K, L=L, N_ENT=N_ENT, query_frac=QUERY_FRAC), seeds=list(seeds),
        emb_d=EMB_D, epochs=EPOCHS, lr=LR, rank1=RANK1, rank4=RANK4, bil_reg=BIL_REG,
        chances=chances, nonadditivity=nonadd, table_clean_novel=table,
        gates=dict(refute_impl=refute_impl, parity_ok=parity_ok, dominance_ok=dominance_ok,
                   n_solved=n_solved, ties_elementwise=ties_elementwise,
                   hero_mustfail_ok=hero_mustfail_ok, ceiling_ok=ceiling_ok, cardinality_ok=cardinality_ok,
                   hero_par=round(hero_par, 5), hero_dom=round(hero_dom, 5),
                   sym_par=round(sym_par, 5), sym_dom=round(sym_dom, 5),
                   role_spec_dom=round(role_spec_dom, 5), freq_par=round(freq_par, 5), freq_dom=round(freq_dom, 5),
                   hero_minus_sym_par=round(hero_par - sym_par, 5), hero_minus_sym_dom=round(hero_dom - sym_dom, 5),
                   hero_minus_role_dom=round(hero_dom - role_spec_dom, 5),
                   rank_effect_par=rank_effect_par, rank_effect_dom=rank_effect_dom,
                   b_mult_int_add_gap=b_mult_add, b_and2_int_add_gap=b_and2_add,
                   add_control_leak=add_control_leak),
        bands=dict(TOL_SPEC=TOL_SPEC, PAR_CHANCE_MARGIN=PAR_CHANCE_MARGIN, PAR_ADD_GAP=PAR_ADD_GAP,
                   PAR_FREQ_GAP=PAR_FREQ_GAP, DOM_FREQ_MARGIN=DOM_FREQ_MARGIN, DOM_SYM_GAP=DOM_SYM_GAP,
                   TIE_ELEMENTWISE_EPS=TIE_ELEMENTWISE_EPS, REFUTE_INT_FLOOR=REFUTE_INT_FLOOR,
                   MUSTFAIL_TOL=MUSTFAIL_TOL, EXPECTED_N_UNITS_PER_SEED=EXPECTED_N_UNITS),
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
# SELF-TEST (exercises the REAL bind path + full arm pipeline; asserts CONSTRUCTION facts + machinery, NOT the
# open wall-break hypothesis -- that is MEASURED in the FULL run and gated by the pre-reg bands, not asserted here)
# ===========================================================================

def _bilinear_reduces_to_elementwise():
    """At U=V=0 the rank-R bilinear op P_i=I recovers the elementwise (P=Q=I) product exactly."""
    g = torch.Generator().manual_seed(123)
    emb = 1.0 + 0.2 * torch.randn(L, EMB_D, generator=g)
    U = torch.zeros(K, EMB_D, RANK1); V = torch.zeros(K, EMB_D, RANK1)
    Xi = torch.tensor([[0, 1, 2, 3], [3, 2, 1, 0]])
    e_base = emb[Xi]
    proj = torch.einsum("nkd,kdr->nkr", e_base, V)
    delta = torch.einsum("nkr,kdr->nkd", proj, U)
    z_bil = (e_base + delta).prod(dim=1)
    z_elem = emb[Xi].prod(dim=1)
    return bool(torch.allclose(z_bil, z_elem, atol=1e-6))


def self_test():
    ok_all = True
    details = {}

    # (1) REAL FHRR bind homomorphism (complex path): bind of FPE phasors reads out (i+j) mod L.
    g = np.random.default_rng(31)
    m = g.integers(1, max(2, L), size=64).astype(np.float64)
    jj = np.arange(L, dtype=np.float64)[:, None]
    Ycode = torch.from_numpy(np.exp(1j * (2.0 * np.pi / L) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Ycode[torch.tensor([1, 2])], Ycode[torch.tensor([2, 3])])
    Yc = Ycode.conj().T.contiguous()
    homo_ok = torch.argmax((bound @ Yc).real, 1).tolist() == [3 % L, 5 % L]
    details["fhrr_homomorphism_ok"] = homo_ok

    # (2) REAL FHRR-bind parity/AND fold vs numpy ground truth.
    bits = np.array([[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]], dtype=np.int64)
    par_ok = (_mult_fold_signs(bits) < 0).astype(np.int64).tolist() == (bits.sum(1) % 2).tolist()
    and_ok = np.rint(_mult_fold_indicators(bits, [0, 1])).astype(np.int64).tolist() == (bits[:, 0] & bits[:, 1]).tolist()
    details["bsc_parity_ok"] = par_ok; details["bsc_and_ok"] = and_ok

    # (3) HERO machinery: rank-R bilinear at U=V=0 recovers elementwise product EXACTLY (the P=Q=I special case).
    bil_reduces = _bilinear_reduces_to_elementwise()
    details["bilinear_reduces_to_elementwise"] = bil_reduces

    # (4) PARITY arena (SYMMETRIC non-additive). CONSTRUCTION: INT_MATCH solves, MONO ~chance. Specialist SYM
    #     discovers parity (contrast reference). HERO measured but NOT asserted (open question).
    X = make_X(7)
    yp = target(PARITY, X)
    rc = score(PARITY, CLEAN, X, yp, 7)["strata"]["novel"]
    ra = score(PARITY, ARBITRARY, X, yp, 7)["strata"]["novel"]
    ch_p = chance_of(PARITY, yp)
    int_p = rc[INT_MATCH]; mono_p = rc[MONO]; sym_p = rc[LEARN_SYM]; add_p = rc[LEARN_ADD]
    br1_p = rc[LEARN_BR1]; br4_p = rc[LEARN_BR4]; freq_p = rc[FREQ]
    hero_arb_gap = ra[LEARN_BR1] - ra[FREQ]
    details.update(dict(parity_INT=int_p, parity_MONO=mono_p, parity_SYM=sym_p, parity_LADD=add_p,
                        parity_HERO_R1=br1_p, parity_HERO_R4=br4_p, parity_FREQ=freq_p,
                        parity_chance=round(ch_p, 4), parity_hero_arb_gap=round(hero_arb_gap, 4), n_novel=rc["n"]))

    # (5) DOMINANCE arena (ANTISYMMETRIC). CONSTRUCTION: INT_MATCH (order-aware) solves; LEARN_SYM (symmetric)
    #     fails. role-keyed specialist discovers. HERO measured but NOT asserted.
    yd = target(DOMINANCE, X)
    rd = score(DOMINANCE, CLEAN, X, yd, 7)["strata"]["novel"]
    ch_d = chance_of(DOMINANCE, yd)
    role_spec_d = max(rd[LEARN_INT], rd[LEARN_ADD])
    details.update(dict(dom_INT=rd[INT_MATCH], dom_SYM=rd[LEARN_SYM], dom_LINT=rd[LEARN_INT],
                        dom_LADD=rd[LEARN_ADD], dom_HERO_R1=rd[LEARN_BR1], dom_HERO_R4=rd[LEARN_BR4],
                        dom_roleSpec=round(role_spec_d, 4), dom_FREQ=rd[FREQ], dom_chance=round(ch_d, 4)))

    # (6) ARMS-MUST-DIFFER (META_RULE_AF): MONO, LEARN_INT/ADD/SYM, HERO R1/R4, HOM mutually distinct.
    digs = score(PARITY, CLEAN, X, yp, 7)["sigs"]
    arms_differ = len(set(digs.values())) == len(digs)
    details["arms_differ_sig_count"] = len(set(digs.values()))
    details["arms_expected"] = len(digs)

    checks = {
        "fhrr_homomorphism": homo_ok,
        "bsc_parity": par_ok,
        "bsc_and": and_ok,
        "bilinear_reduces_to_elementwise": bil_reduces,      # HERO op at init == elementwise special case
        # --- CONSTRUCTION (arena solvable by the matched op; specialists behave as expected) ---
        "INT_solves_parity_novel": int_p >= 0.90,
        "MONO_at_chance_parity": mono_p <= ch_p + 0.10,
        "INT_beats_MONO_parity": (int_p - mono_p) >= 0.30,
        "INT_solves_dominance": rd[INT_MATCH] >= 0.90,
        "SYM_specialist_discovers_parity": (sym_p - add_p) >= 0.15 and sym_p >= ch_p + 0.20,
        "role_specialist_discovers_dominance": (role_spec_d - rd[FREQ]) >= 0.10 and (role_spec_d - rd[LEARN_SYM]) >= 0.12,
        "SYM_fails_dominance": rd[LEARN_SYM] <= ch_d + 0.12,
        # --- FAIRNESS / INTEGRITY (the arena must exercise the discriminator honestly) ---
        "arena_freq_not_saturated": freq_p <= 0.75,
        "hero_arbitrary_mustfail_fires": hero_arb_gap <= 0.10,   # HERO does NOT beat freq on arbitrary (fires)
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
