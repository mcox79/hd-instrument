"""INTERACTION_ASYMMETRIC_DIRECTED_OPERATORS (v1): do BRAIN-theorized DIRECTED/ASYMMETRIC-relation operators read
DOMINANCE (asymmetric non-additive) BETTER than role-keying, where the LEARNED BILINEAR failed?

PRIOR ARC (inlined; NO re-hunt):
  (1) exp_interaction_nonadditive_discovery_v1 (commit 59056b6d4): localized the ROLE-KEYING<->SYMMETRY TENSION.
  (2) exp_interaction_bilinear_wall_break_v1 (commit 29b53e63b) landed HARD_FAIL_BILINEAR_IS_ANOTHER_SPECIALIST_
      PARITY_ONLY (off-disk data/exp_interaction_bilinear_wall_break_v1/metrics.json): PARITY solved
      (HERO_R1=0.978 vs SYM=0.992) but DOMINANCE NOT (HERO_R1=0.485 vs role-keyed 1.000, vs SYM 0.477;
      hero_minus_sym_dom=+0.008, ties_elementwise=True). ROOT CAUSE (drill-pinned): the bilinear's final
      composition step is a COMMUTATIVE Hadamard product over K factors -- a(*)b(*)c(*)d is order-blind by
      construction; per-factor low-rank corrections cannot make a commutative fold order-sensitive. THE FIX MUST
      CHANGE THE FOLD, not re-parameterize the factors.

THIS CELL (design: notes/research_brain_asymmetric_directed_relation_operators_2026-07-15.md): head-to-head test of
  THREE brain-theorized asymmetric operators, each injecting order-sensitivity at a DIFFERENT point relative to the
  failed commutative fold:
    (1) TRANSITION_OP (favored) -- non-commutative matrix chaining (TEM W_a / grid-cell group-rep / already-validated
        GHRR matrix-vector bind). Order-sensitivity IN THE COMPOSITION OPERATOR ITSELF.
    (2) HETEROASSOC_OP -- one-shot Hebbian outer-product correlation-matrix memory, ZERO SGD. Order-sensitivity in
        the WRITE step. Literature-predicted LOOKUP-not-relation: high on SEEN, degrades on NOVEL (a falsifiable
        diagnostic negative, not a HARD-PASS candidate per its own literature).
    (3) PHASE_ORDER_OP -- FHRR complex-phase fixed per-role offsets. Order-sensitivity in the READOUT of phase.
        Weakest-grounded; a fixed role offset under COMMUTATIVE complex product is a role-TAG, not a
        non-commutative bind (mechanistic-honesty flag, section 3b of the design). PHASE_NO_OFFSET ablation checks it.

  BASELINES (re-run in the SAME seeds/units for a controlled comparison, NOT cross-cited): ROLE_KEYED =
  max(LEARN_INT, LEARN_ADD) (the incumbent asymmetric specialist), BILINEAR_REF = the failed LEARN_BILINEAR_RANK1,
  LEARN_SYM (symmetric/elementwise reference), FREQ_NULL (honest antisymmetric baseline), MEMORIZE/POP/ORACLE,
  INT_MATCH/MONO (arena construction sanity).

FAITHFUL-BUILD NOTE ON TRANSITION_OP GROUPING (load-bearing; cell-author functional-requirement check):
  The design writes s_i = M_i @ (s_{i-1} (*) e[x_i]). Read LITERALLY, the first step s_1 = M_1 @ (e[x_0] (*) e[x_1])
  combines slots 0 and 1 through a COMMUTATIVE Hadamard BEFORE any matrix distinguishes them -> s_1 is SYMMETRIC in
  (x_0,x_1) -> the whole op is symmetric in slots 0,1 -> it CANNOT represent antisymmetric DOMINANCE (y=1 iff
  x0>x1) by construction (a guaranteed non-informative HARD_FAIL). This cell therefore uses the grouping that
  realizes the STATED mechanism (TEM g_{t+1}=f(W_a, g_t): transform the running STATE by the action-matrix, THEN
  bind the new slot's content):
        s_0 = e[x_0]
        s_i = (M_i @ s_{i-1}) (*) e[x_i]      for i = 1..K-1
  This IS non-commutative and asymmetric in (x_0,x_1) [(M_1 e[x0])(*)e[x1] != (M_1 e[x1])(*)e[x0] for non-diagonal
  M_1], and at init M_i = I it reduces EXACTLY to the elementwise product prod_i e[x_i] == LEARN_SYM (clean
  baseline-equivalent init, mirroring the bilinear cell's P=I init). The self-test asserts BOTH facts. Documented
  as a design-faithful correction, not a silent deviation.

ARMS (glass-box CPU; NO LLM at measurement):
  Construction sanity (reused verbatim): INT_MATCH (family-matched, exercises REAL FHRR bind), MONO (additive).
  Learned baselines (reused verbatim): LEARN_SYM (shared code + product = symmetric), LEARN_INT (role-keyed
    product), LEARN_ADD (role-keyed sum), BILINEAR_REF (shared code + per-role rank-1 P=I+uv^T + product = the
    FAILED op).
  NEW candidates:
    TRANSITION_OP                  shared code + non-commutative matrix chain (mechanism 1).
    TRANSITION_OP_SHUFFLED_ORDER   SAME trained M_i, slot-processing order permuted at TEST time only (diagnostic).
    HETEROASSOC_OP                 one-shot Hebbian W = sum onehot(y) (x) rolefiller(X), zero SGD (mechanism 2).
    PHASE_ORDER_OP                 learned shared phasor code + fixed per-role phase offsets + FHRR product bind (3).
    PHASE_NO_OFFSET                same but theta_i = 0 (diagnostic; attribution control).
  Baselines: FREQ_NULL = max(HOMOPHILY_COND, POP); MEMORIZE; POP; ORACLE (ceiling).

TARGET FAMILIES (K=4 constituents, L=4 levels): PARITY (symmetric non-additive), DOMINANCE (antisymmetric / the
  discriminator), AND2/MULT (diagnostics), ADD (additive control, excluded from must-fail scope).

PRE-REGISTERED BANDS (fixed BEFORE running; TOL_SPEC=0.10, SAME constants as the landed bilinear cell). NOVEL CLEAN.
  For each candidate OP in {TRANSITION_OP, HETEROASSOC_OP, PHASE_ORDER_OP}:
    dominance_ok(OP) = OP_dom >= ROLE_KEYED_dom - 0.10 AND OP_dom - FREQ_dom >= 0.10 AND OP_dom - SYM_dom >= 0.15
    parity_ok(OP)    = OP_par >= SYM_par - 0.10 AND OP_par >= chance_p + 0.20 AND OP_par - LADD_par >= 0.15
                       AND OP_par - FREQ_par >= 0.15
    mustfail_ok(OP)  = arb_gap(OP) <= 0.10 AND shuf_gap(OP) <= 0.10 over CLAIM_FAMILIES (else fits noise -> void)
  HARD_PASS  = at least one OP clears dominance_ok AND mustfail_ok AND its attribution diagnostic (below).
  HARD_FAIL  = none of the three clears dominance_ok AND mustfail_ok (role-keying remains best asymmetric construct).
  MIDDLE_BAND = a candidate clears the raw dominance_ok+mustfail threshold but FAILS its attribution diagnostic
               (unattributed win); OR clears dominance_ok on SEEN but not NOVEL without heteroassoc_lookup_confirmed
               (under-diagnosed partial). Reported per-candidate; NOT averaged into one global number.
  REFUTE_IMPL = INT_MATCH cannot solve parity or dominance (arena/impl sanity; floor 0.90).
  BONUS (reported, not gating HARD_PASS): does a dominance-passing OP ALSO clear parity_ok (one code doing BOTH)?

  Attribution diagnostics (reported; gate MIDDLE vs HARD_PASS for a RAW passer):
    transition_order_confirmed     = TRANSITION_OP_dom - TRANSITION_OP_SHUFFLED_ORDER_dom >= 0.20
    phase_attribution_to_role_tag  = (PHASE_ORDER_OP_dom - PHASE_NO_OFFSET_dom) >= 0.20 AND
                                     |PHASE_ORDER_OP_dom - ROLE_KEYED_dom| <= 0.15
    heteroassoc_lookup_confirmed   = HETEROASSOC_seen_dom - HETEROASSOC_novel_dom >= 0.30 (positive even if HF)

Determinism: all RNG seeds from INTEGER indices (FAM_IDX/REG_IDX) + fixed generators, NEVER Python salted built-in
hashing (the false-REFUTE root cause found by the prior VET). Glass-box CPU. Default (no flag) = FULL run. ASCII-only.
No bare except; except SystemExit before except Exception. Atomic metrics write. flush=True progress.
"""

import argparse
import hashlib
import json
import math
import os
import platform
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
# Use ONLY the long-stable `bind` (present on both local + remote runner). Do NOT import newer siblings.

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline (defense in depth)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "interaction_asymmetric_directed_operators_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ---- arena (SAME as the VET-clean discovery/bilinear arena) ----
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
FAM_IDX = {f: i for i, f in enumerate(FAMILIES)}
REG_IDX = {r: i for i, r in enumerate(REGIMES)}

# ---- arm names ----
INT_MATCH = "INT_MATCH"; MONO = "MONO"
LEARN_INT = "LEARN_INT"; LEARN_ADD = "LEARN_ADD"; LEARN_SYM = "LEARN_SYM"
BILINEAR_REF = "BILINEAR_REF"                        # reused failed op (LEARN_BILINEAR_RANK1)
TRANSITION_OP = "TRANSITION_OP"
TRANS_SHUF = "TRANSITION_OP_SHUFFLED_ORDER"
HETERO = "HETEROASSOC_OP"
PHASE = "PHASE_ORDER_OP"
PHASE_NO = "PHASE_NO_OFFSET"
HOM = "HOMOPHILY_COND"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"
ARM_NAMES = [INT_MATCH, MONO, LEARN_INT, LEARN_ADD, LEARN_SYM, BILINEAR_REF,
             TRANSITION_OP, TRANS_SHUF, HETERO, PHASE, PHASE_NO, HOM, MEMO, POP, ORC, FREQ]
CANDIDATES = [TRANSITION_OP, HETERO, PHASE]          # the three NEW brain-mechanism candidates gated for HARD_PASS

# ---- learned-arm hyperparams (fixed a priori; MATCH the prior VET-clean cell for fairness/comparability) ----
EMB_D = 48
EPOCHS = 500
LR = 0.05
RANK1 = 1
BIL_REG = 1.0e-3          # bilinear low-rank weight-decay (reused verbatim from the landed cell)
TRANS_REG = 1.0e-5        # TINY L2 on the transition matrices: numerical stability ONLY, NOT regularized toward
#                           identity (per design). Negligible over 500 epochs; documented calibration_check=default.
TRANS_INIT_NOISE = 0.05   # M_i init = I + this*randn -> at init the chain == elementwise product (LEARN_SYM).
HETERO_D = 2048           # heteroassociative code dim (feature dim = 2*HETERO_D). Sized so capacity >> the ~121
#                           train combos (classical ~0.14*dim analog) -> SEEN in-sample recall is near-MEMORIZE,
#                           isolating NOVEL generalization failure as the clean lookup-not-relation signal (a
#                           capacity-starved memory failing would be uninformative; a well-provisioned one failing
#                           on NOVEL while acing SEEN is the design's intended informative negative).

# ---- pre-registered bands (fixed before running; SAME constants as the landed bilinear cell) ----
TOL_SPEC = 0.10
PAR_CHANCE_MARGIN = 0.20
PAR_ADD_GAP = 0.15
PAR_FREQ_GAP = 0.15
DOM_FREQ_MARGIN = 0.10
DOM_SYM_GAP = 0.15
REFUTE_INT_FLOOR = 0.90
MUSTFAIL_TOL = 0.10
# attribution diagnostics
TRANS_ORDER_GAP = 0.20    # TRANSITION_OP - SHUFFLED >= this -> order-non-commutativity is load-bearing
PHASE_ATTR_GAP = 0.20     # PHASE_ORDER - PHASE_NO_OFFSET >= this -> the phase offset (role-tag) is doing the work
PHASE_ROLE_CLOSE = 0.15   # |PHASE_ORDER - ROLE_KEYED| <= this -> the win is role-tag-magnitude, not something new
HETERO_LOOKUP_GAP = 0.30  # HETEROASSOC seen - novel >= this -> lookup-not-relation confirmed (informative negative)

EXPECTED_N_UNITS = len(FAMILIES) * len(REGIMES)  # per seed; cardinality sanity


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


def _write_start_marker(expected_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  expected_n_units=expected_units, host=platform.node())
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUT_DIR, "_start_marker.json"))


def _heartbeat(unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=datetime.now(timezone.utc).isoformat(), unit_idx=int(unit_idx),
               total_units=int(total_units), elapsed_s=round(float(elapsed_s), 2))
    if extra:
        row["extra"] = extra
    try:
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


# ===========================================================================
# ARENA + TARGET FAMILIES (deterministic, planted; glass-box) -- REUSED VERBATIM
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
# non-additivity diagnostic (reported, not gated) -- REUSED VERBATIM
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
# CONSTRUCTION-PROOF ARMS (algebra-matched; INT_MATCH exercises the REAL substrate bind) -- REUSED VERBATIM
# ===========================================================================

def _mult_fold_signs(bits, d=16):
    n, k = bits.shape
    signs = (1 - 2 * bits).astype(np.float32)
    acc = torch.ones((n, d), dtype=torch.complex64) * torch.from_numpy(signs[:, 0:1]).to(torch.complex64)
    for i in range(1, k):
        vi = torch.ones((n, d), dtype=torch.complex64) * torch.from_numpy(signs[:, i:i + 1]).to(torch.complex64)
        acc = hd_bind(acc, vi)
    return acc[:, 0].real.numpy()


def _mult_fold_indicators(bits, cols, d=16):
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
# LEARNED BASELINE ARMS (plain Adam SGD) -- REUSED VERBATIM (int / add / sym / bilinear)
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
        emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))
        U = torch.nn.Parameter(torch.zeros(k, EMB_D, rank))
        V = torch.nn.Parameter(torch.zeros(k, EMB_D, rank))
        params += [emb, U, V]
    elif mode == "sym":
        emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))
        params.append(emb)
    else:
        center = 1.0 if product else 0.0
        emb = torch.nn.Parameter(center + 0.2 * torch.randn(k, L, EMB_D, generator=g))
        params.append(emb)
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, nclass, generator=g))
    b = torch.nn.Parameter(torch.zeros(nclass))
    params += [W, b]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def compose(Xi):
        if mode == "bilinear":
            e_base = emb[Xi]
            proj = torch.einsum("nkd,kdr->nkr", e_base, V)
            delta = torch.einsum("nkr,kdr->nkd", proj, U)
            e = e_base + delta
            return e.prod(dim=1)
        if mode == "sym":
            e = emb[Xi]
        else:
            e = emb[torch.arange(k).unsqueeze(0), Xi]
        return e.prod(dim=1) if product else e.sum(dim=1)

    for _ in range(EPOCHS):
        opt.zero_grad()
        h = compose(Xt)
        mu = h.mean(0, keepdim=True); sd = h.std(0, keepdim=True) + 1e-3
        hn = (h - mu) / sd
        logits = hn @ W + b
        loss = lossf(logits, yt)
        if mode == "bilinear":
            loss = loss + BIL_REG * (U.pow(2).sum() + V.pow(2).sum())
        loss.backward()
        opt.step()
    with torch.no_grad():
        h_tr = compose(Xt); mu = h_tr.mean(0, keepdim=True); sd = h_tr.std(0, keepdim=True) + 1e-3
        h_q = compose(Xu)
        logits_q = ((h_q - mu) / sd) @ W + b
        pred = torch.argmax(logits_q, 1).numpy().astype(np.int64)
    return pred


# ===========================================================================
# (1) TRANSITION_OP -- non-commutative matrix chain (mechanism 1). NEW.
#     s_0 = e[x_0];  s_i = (M_i @ s_{i-1}) (*) e[x_i]   for i = 1..K-1.  (TEM g_{t+1}=f(W_a,g_t) form; see docstring.)
#     Returns BOTH the standard-order pred and the TEST-TIME SHUFFLED-ORDER pred from the SAME trained model
#     (M_i, e, readout identical) -- the shuffled arm is the order-non-commutativity attribution diagnostic.
# ===========================================================================

def _transition_compose(emb, M, Xi, order):
    """emb (L,D); M (k,D,D); Xi (n,k) long; order = list of slot indices. Returns (n,D)."""
    e = emb[Xi]                                   # (n,k,D)
    s = e[:, order[0], :]                         # (n,D)  seed slot: no matrix
    for j in range(1, len(order)):
        s = torch.matmul(s, M[j].t()) * e[:, order[j], :]   # (M_j @ s) (*) e[slot]
    return s


def _fixed_derangement(k, seed):
    rng = np.random.default_rng(seed * 100103 + 3)
    base = np.arange(k)
    perm = base.copy()
    for _ in range(1000):
        rng.shuffle(perm)
        if not np.any(perm == base):             # no fixed point -> maximal order change
            return perm.tolist()
    return list(reversed(range(k)))              # fallback: reversal (a derangement for k>=2 except middle-fixed odd)


def _train_transition(Xtr, ytr, Xq, nclass, seed):
    g = torch.Generator().manual_seed(seed * 7919 + 5)
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    k = Xtr.shape[1]
    emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, EMB_D, generator=g))            # SHARED code (like sym)
    eye = torch.eye(EMB_D).unsqueeze(0).repeat(k, 1, 1)
    M = torch.nn.Parameter(eye + TRANS_INIT_NOISE * torch.randn(k, EMB_D, EMB_D, generator=g))  # init ~ identity
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, nclass, generator=g))
    b = torch.nn.Parameter(torch.zeros(nclass))
    params = [emb, M, W, b]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    std_order = list(range(k))

    for _ in range(EPOCHS):
        opt.zero_grad()
        h = _transition_compose(emb, M, Xt, std_order)
        mu = h.mean(0, keepdim=True); sd = h.std(0, keepdim=True) + 1e-3
        logits = ((h - mu) / sd) @ W + b
        loss = lossf(logits, yt) + TRANS_REG * M.pow(2).sum()          # tiny L2: numerical stability only
        loss.backward()
        opt.step()

    with torch.no_grad():
        h_tr = _transition_compose(emb, M, Xt, std_order)
        mu = h_tr.mean(0, keepdim=True); sd = h_tr.std(0, keepdim=True) + 1e-3
        h_q = _transition_compose(emb, M, Xu, std_order)
        pred_std = torch.argmax(((h_q - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
        perm = _fixed_derangement(k, seed)                            # TEST-time permutation ONLY (same params)
        h_qs = _transition_compose(emb, M, Xu, perm)
        pred_shuf = torch.argmax(((h_qs - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
    return pred_std, pred_shuf


# ===========================================================================
# (2) HETEROASSOC_OP -- one-shot Hebbian correlation-matrix memory, ZERO SGD (mechanism 2). NEW.
#     Fixed random UNIT-MODULUS phasor codes: shared value table c[l], role table r[i]. Role-filler bind
#     (product of phasors = sum of angles) then bundle (sum) over slots -> a distributed, ORDER-PRESERVING combo
#     key (needed so the memory can even represent DOMINANCE on SEEN). feature keys the FULL K-slot combo so
#     novelty granularity matches split_novel (a novel combo = an unseen key -> the literature-predicted lookup
#     miss). W = onehot(y)^T @ feature (correlation-matrix write). score = feature_q @ W^T ; argmax. No epochs.
#     NOTE ON DESIGN TEXT: the design illustrates feature(x0,x1); this cell binds ALL K slots (full-combo key) so
#     the SEEN/NOVEL lookup diagnostic is coherent AND no arm is handed which-slots-matter (fairness).
# ===========================================================================

def _hetero_feature(Xnp, val_ang, role_ang):
    Xi = torch.from_numpy(Xnp).long()
    n = Xi.shape[0]; d = val_ang.shape[1]
    acc_re = torch.zeros(n, d); acc_im = torch.zeros(n, d)
    for i in range(Xi.shape[1]):
        a = role_ang[i].view(1, -1) + val_ang[Xi[:, i]]           # role (x) value  (phasor product = angle sum)
        acc_re = acc_re + torch.cos(a); acc_im = acc_im + torch.sin(a)   # bundle (sum) over slots
    F = torch.cat([acc_re, acc_im], dim=1)                        # (n, 2d) real/imag split
    F = F / (F.norm(dim=1, keepdim=True) + 1e-8)                  # unit-norm -> cosine-vote readout
    return F.numpy()


def arm_heteroassoc(Xtr, ytr, Xq, nclass, seed):
    g = torch.Generator().manual_seed(seed * 7919 + 9)
    val_ang = 2.0 * math.pi * torch.rand(L, HETERO_D, generator=g)     # shared value phasor codes (FIXED)
    role_ang = 2.0 * math.pi * torch.rand(K, HETERO_D, generator=g)    # role phasor codes (FIXED)
    Ftr = _hetero_feature(Xtr, val_ang, role_ang)
    Fq = _hetero_feature(Xq, val_ang, role_ang)
    Y = np.eye(nclass, dtype=np.float64)[ytr]                          # (ntr, nclass) one-hot
    Wmat = Y.T @ Ftr                                                   # (nclass, 2d)  = sum onehot (x) feature
    scores = Fq @ Wmat.T                                              # (nq, nclass)
    return np.argmax(scores, axis=1).astype(np.int64)


# ===========================================================================
# (3) PHASE_ORDER_OP -- learned shared phasor code + fixed per-role phase offsets + FHRR product bind (mechanism 3).
#     p_i(x_i) = exp(i*(phi[x_i] + theta_i)),  theta_i = i*(2pi/K) fixed;  z = prod_i p_i = exp(i*sum_i(phi+theta)).
#     Product of unit-modulus FHRR phasors == exp(i * sum of phases) (EXACT, computed directly for differentiability;
#     equivalent to chaining hd_bind). Readout: learned linear head on [z.real, z.imag]. use_offset=False =>
#     theta_i=0 (PHASE_NO_OFFSET attribution control, trained separately).
#     MECHANISTIC HONESTY FLAG (pre-registered, section 3b of design): complex product is COMMUTATIVE, so any
#     order-sensitivity here is a fixed per-role phase TAG, NOT the bind becoming non-commutative. Under a linear
#     readout a data-independent additive phase (sum_i theta_i is constant) is a fixed rotation and is ABSORBED by
#     the readout -> PHASE_ORDER is expected to ~= PHASE_NO_OFFSET. This is the predicted, informative outcome.
# ===========================================================================

def _train_phase(Xtr, ytr, Xq, nclass, seed, use_offset):
    g = torch.Generator().manual_seed(seed * 7919 + (7 if use_offset else 8))
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    k = Xtr.shape[1]
    phi = torch.nn.Parameter(2.0 * math.pi * torch.rand(L, EMB_D, generator=g))          # learned shared phasor code
    if use_offset:
        theta = (2.0 * math.pi / k) * torch.arange(k, dtype=torch.float32)               # fixed per-role offsets
    else:
        theta = torch.zeros(k, dtype=torch.float32)
    W = torch.nn.Parameter(0.1 * torch.randn(2 * EMB_D, nclass, generator=g))
    b = torch.nn.Parameter(torch.zeros(nclass))
    params = [phi, W, b]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def compose(Xi):
        ang = phi[Xi] + theta.view(1, k, 1)          # (n,k,D)  per-slot phasor angle
        z = ang.sum(dim=1)                           # (n,D)    product of phasors == sum of angles
        feat = torch.cat([torch.cos(z), torch.sin(z)], dim=1)   # (n, 2D)  [real, imag]
        return feat

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
        h_q = compose(Xu)
        pred = torch.argmax(((h_q - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
    return pred


# ===========================================================================
# baselines -- REUSED VERBATIM
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

    trans_std, trans_shuf = _train_transition(Xtr, ytr, Xq, nc, seed)
    preds = {
        INT_MATCH: arm_int_match(family, Xtr, ytr, Xq),
        MONO: arm_mono(family, Xtr, ytr, Xq),
        LEARN_INT: _train_learned(Xtr, ytr, Xq, nc, "int", seed),
        LEARN_ADD: _train_learned(Xtr, ytr, Xq, nc, "add", seed),
        LEARN_SYM: _train_learned(Xtr, ytr, Xq, nc, "sym", seed),
        BILINEAR_REF: _train_learned(Xtr, ytr, Xq, nc, "bilinear", seed, rank=RANK1),
        TRANSITION_OP: trans_std,
        TRANS_SHUF: trans_shuf,
        HETERO: arm_heteroassoc(Xtr, ytr, Xq, nc, seed),
        PHASE: _train_phase(Xtr, ytr, Xq, nc, seed, use_offset=True),
        PHASE_NO: _train_phase(Xtr, ytr, Xq, nc, seed, use_offset=False),
        HOM: arm_homophily(family, Xtr, ytr, Xq),
        MEMO: arm_memorize(family, Xtr, ytr, Xq, pop_label),
        POP: np.full(Xq.shape[0], pop_label, dtype=np.int64),
        ORC: y_oracle[q],
    }

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if m.sum() > 0 else float("nan")

    # NOTE: make_X samples all-UNIQUE combos, so every query combo is disjoint from train -> the query "seen"
    # stratum is ALWAYS empty. The heteroassoc lookup-not-relation diagnostic therefore uses SEEN = IN-SAMPLE
    # (train-row) recall of the one-shot Hebbian memory (built from train) vs NOVEL = out-of-sample query. This is
    # the literature's own framing (recall stored pairs vs generalize to unseen pairs).
    hetero_train_pred = arm_heteroassoc(Xtr, ytr, Xtr, nc, seed)
    hetero_seen_acc = float((np.asarray(hetero_train_pred) == np.asarray(ytr)).mean()) if len(ytr) else float("nan")

    out = {}
    for sname, m in (("novel", novel), ("all", np.ones(len(gold), bool))):
        d = {arm: round(a(preds[arm], m), 5) for arm in preds}
        d[FREQ] = round(max(d[HOM], d[POP]), 5)
        d["n"] = int(m.sum())
        out[sname] = d
    # ARMS-MUST-DIFFER (META_RULE_AF): the genuinely-distinct mechanism arms are mutually distinct.
    # EXEMPTED pairs (declared): (TRANSITION_OP, TRANSITION_OP_SHUFFLED_ORDER) [same model; identical iff the
    # mechanism is order-invariant -- that equality IS the diagnostic]; (PHASE_ORDER_OP, PHASE_NO_OFFSET) [the
    # per-role offset is provably absorbed by the linear readout -> equal output is the predicted attribution
    # result]; (LEARN_INT, LEARN_ADD) [both dominance specialists, may both saturate to the oracle].
    af_arms = (MONO, LEARN_SYM, BILINEAR_REF, TRANSITION_OP, HETERO, PHASE, HOM)
    sigs = {arm: _sig(preds[arm]) for arm in af_arms}
    return dict(strata=out, sigs=sigs, hetero_seen_acc=round(hetero_seen_acc, 5),
                n_novel=int(novel.sum()), n_query=int(len(gold)))


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds=(7, 13, 17, 23, 29)):
    _write_start_marker(EXPECTED_N_UNITS * len(seeds))
    _log("FULL run: %d families x %d regimes x %d seeds, arena K=%d L=%d N=%d"
         % (len(FAMILIES), len(REGIMES), len(seeds), K, L, N_ENT))
    per = {fam: {reg: [] for reg in REGIMES} for fam in FAMILIES}
    chances = {}; nonadd = {}
    t0 = time.perf_counter()
    n_units = 0
    total = EXPECTED_N_UNITS * len(seeds)
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
            _heartbeat(n_units, total, time.perf_counter() - t0, extra={"seed": sd, "family": fam})
            _log("  seed %d/%d family=%s done (units=%d/%d elapsed=%.1fs)"
                 % (si + 1, len(seeds), fam, n_units, total, time.perf_counter() - t0))
    cardinality_ok = bool(n_units == total)

    def mean_stratum(fam, reg, arm, stratum):
        vals = [ps["strata"][stratum][arm] for ps in per[fam][reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    def mn(fam, reg, arm):
        return mean_stratum(fam, reg, arm, "novel")

    def mean_hetero_seen(fam, reg):
        vals = [ps["hetero_seen_acc"] for ps in per[fam][reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    table = {}
    for fam in FAMILIES:
        table[fam] = {arm: round(mn(fam, CLEAN, arm), 5) for arm in ARM_NAMES}
        table[fam]["chance"] = round(chances[fam], 5)
        # SEEN dominance stratum for the lookup diagnostic = heteroassoc IN-SAMPLE (train-row) recall on CLEAN
        table[fam]["seen_" + HETERO] = round(mean_hetero_seen(fam, CLEAN), 5)
        # must-fail gaps for the three gated candidates
        for arm in CANDIDATES:
            table[fam]["arb_gap_%s" % arm] = round(mn(fam, ARBITRARY, arm) - mn(fam, ARBITRARY, FREQ), 5)
            table[fam]["shuf_gap_%s" % arm] = round(mn(fam, SHUFFLE, arm) - mn(fam, SHUFFLE, FREQ), 5)

    p = table[PARITY]; dmn = table[DOMINANCE]
    ch_p = chances[PARITY]

    refute_impl = bool(p[INT_MATCH] < REFUTE_INT_FLOOR or dmn[INT_MATCH] < REFUTE_INT_FLOOR)

    role_dom = max(dmn[LEARN_INT], dmn[LEARN_ADD])
    sym_dom = dmn[LEARN_SYM]; freq_dom = dmn[FREQ]
    sym_par = p[LEARN_SYM]; add_par = p[LEARN_ADD]; freq_par = p[FREQ]

    # per-candidate gates (all on NOVEL CLEAN)
    cand = {}
    for op in CANDIDATES:
        op_dom = dmn[op]; op_par = p[op]
        dominance_ok = bool(op_dom >= role_dom - TOL_SPEC and (op_dom - freq_dom) >= DOM_FREQ_MARGIN
                            and (op_dom - sym_dom) >= DOM_SYM_GAP)
        parity_ok = bool(op_par >= sym_par - TOL_SPEC and op_par >= ch_p + PAR_CHANCE_MARGIN
                         and (op_par - add_par) >= PAR_ADD_GAP and (op_par - freq_par) >= PAR_FREQ_GAP)
        mustfail_ok = all(table[fam]["arb_gap_%s" % op] <= MUSTFAIL_TOL
                          and table[fam]["shuf_gap_%s" % op] <= MUSTFAIL_TOL for fam in CLAIM_FAMILIES)
        cand[op] = dict(dom=round(op_dom, 5), par=round(op_par, 5),
                        dominance_ok=dominance_ok, parity_ok=parity_ok, mustfail_ok=mustfail_ok)

    # attribution diagnostics
    trans_order_confirmed = bool((dmn[TRANSITION_OP] - dmn[TRANS_SHUF]) >= TRANS_ORDER_GAP)
    phase_attr = bool((dmn[PHASE] - dmn[PHASE_NO]) >= PHASE_ATTR_GAP and abs(dmn[PHASE] - role_dom) <= PHASE_ROLE_CLOSE)
    hetero_seen = table[DOMINANCE]["seen_" + HETERO]
    hetero_lookup_confirmed = bool((hetero_seen - dmn[HETERO]) >= HETERO_LOOKUP_GAP)
    attribution_ok = {TRANSITION_OP: trans_order_confirmed, PHASE: phase_attr, HETERO: True}

    ceiling_ok = all(table[fam][ORC] >= table[fam][op] - 1e-6 for fam in FAMILIES for op in CANDIDATES)

    raw_passers = [op for op in CANDIDATES if cand[op]["dominance_ok"] and cand[op]["mustfail_ok"]]
    clean_passers = [op for op in raw_passers if attribution_ok[op]]
    unattributed = [op for op in raw_passers if not attribution_ok[op]]
    # SEEN-passing-but-NOVEL-failing partials (under-diagnosed unless lookup_confirmed for HETERO)
    seen_partial = []
    for op in CANDIDATES:
        seen_dom = table[DOMINANCE].get("seen_" + op, float("nan")) if op == HETERO else None
        if op == HETERO and (not cand[op]["dominance_ok"]):
            if (hetero_seen >= role_dom - TOL_SPEC) and (not hetero_lookup_confirmed):
                seen_partial.append(op)

    bonus_parity = [op for op in clean_passers if cand[op]["parity_ok"]]

    if refute_impl:
        verdict = "REFUTE_IMPL_MATCHED_OP_CANNOT_SOLVE_ARENA"
    elif clean_passers:
        verdict = "HARD_PASS_BRAIN_ASYMMETRIC_OP_READS_DOMINANCE_%s" % ("+".join(clean_passers))
    elif unattributed:
        verdict = "MIDDLE_BAND_RAW_PASS_UNATTRIBUTED_%s" % ("+".join(unattributed))
    elif seen_partial:
        verdict = "MIDDLE_BAND_SEEN_ONLY_UNDER_DIAGNOSED_%s" % ("+".join(seen_partial))
    else:
        verdict = "HARD_FAIL_NO_BRAIN_OP_BEATS_ROLE_KEYING_ON_DOMINANCE"

    msg = ("%s || DOMINANCE(role=%s freq=%s sym=%s ch=%.2f): TRANS=%s(dom_ok=%s mf=%s) HETERO=%s(seen=%s dom_ok=%s mf=%s) "
           "PHASE=%s(dom_ok=%s mf=%s) BILINEAR_REF=%s | attrib: trans_order=%s(TRANS-SHUF=%s) phase_role=%s(PH-NOOFF=%s) "
           "hetero_lookup=%s(seen-novel=%s) | PARITY bonus passers=%s | clean_passers=%s ceiling=%s cardinality=%s | "
           "INT_MATCH par=%s dom=%s (refute=%s)"
           % (verdict, _fmt(role_dom), _fmt(freq_dom), _fmt(sym_dom), chances[DOMINANCE],
              _fmt(dmn[TRANSITION_OP]), cand[TRANSITION_OP]["dominance_ok"], cand[TRANSITION_OP]["mustfail_ok"],
              _fmt(dmn[HETERO]), _fmt(hetero_seen), cand[HETERO]["dominance_ok"], cand[HETERO]["mustfail_ok"],
              _fmt(dmn[PHASE]), cand[PHASE]["dominance_ok"], cand[PHASE]["mustfail_ok"], _fmt(dmn[BILINEAR_REF]),
              trans_order_confirmed, _fmt(dmn[TRANSITION_OP] - dmn[TRANS_SHUF]),
              phase_attr, _fmt(dmn[PHASE] - dmn[PHASE_NO]),
              hetero_lookup_confirmed, _fmt(hetero_seen - dmn[HETERO]),
              bonus_parity, clean_passers, ceiling_ok, cardinality_ok,
              _fmt(p[INT_MATCH]), _fmt(dmn[INT_MATCH]), refute_impl))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode="full",
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        arena=dict(K=K, L=L, N_ENT=N_ENT, query_frac=QUERY_FRAC), seeds=list(seeds),
        emb_d=EMB_D, epochs=EPOCHS, lr=LR, trans_reg=TRANS_REG, trans_init_noise=TRANS_INIT_NOISE,
        hetero_d=HETERO_D, bil_reg=BIL_REG,
        chances=chances, nonadditivity=nonadd, table_clean_novel=table,
        gates=dict(refute_impl=refute_impl, role_dom=round(role_dom, 5), freq_dom=round(freq_dom, 5),
                   sym_dom=round(sym_dom, 5), per_candidate=cand,
                   trans_order_confirmed=trans_order_confirmed, phase_attribution_to_role_tag=phase_attr,
                   hetero_lookup_confirmed=hetero_lookup_confirmed,
                   trans_minus_shuf_dom=round(dmn[TRANSITION_OP] - dmn[TRANS_SHUF], 5),
                   phase_minus_nooffset_dom=round(dmn[PHASE] - dmn[PHASE_NO], 5),
                   hetero_seen_minus_novel_dom=round(hetero_seen - dmn[HETERO], 5),
                   raw_passers=raw_passers, clean_passers=clean_passers, unattributed=unattributed,
                   seen_partial=seen_partial, bonus_parity_passers=bonus_parity,
                   ceiling_ok=ceiling_ok, cardinality_ok=cardinality_ok),
        bands=dict(TOL_SPEC=TOL_SPEC, PAR_CHANCE_MARGIN=PAR_CHANCE_MARGIN, PAR_ADD_GAP=PAR_ADD_GAP,
                   PAR_FREQ_GAP=PAR_FREQ_GAP, DOM_FREQ_MARGIN=DOM_FREQ_MARGIN, DOM_SYM_GAP=DOM_SYM_GAP,
                   REFUTE_INT_FLOOR=REFUTE_INT_FLOOR, MUSTFAIL_TOL=MUSTFAIL_TOL,
                   TRANS_ORDER_GAP=TRANS_ORDER_GAP, PHASE_ATTR_GAP=PHASE_ATTR_GAP,
                   PHASE_ROLE_CLOSE=PHASE_ROLE_CLOSE, HETERO_LOOKUP_GAP=HETERO_LOOKUP_GAP,
                   EXPECTED_N_UNITS_PER_SEED=EXPECTED_N_UNITS),
        per_family_regime_strata={fam: {reg: [ps["strata"] for ps in per[fam][reg]] for reg in REGIMES}
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
# SELF-TEST (exercises the REAL bind path + all NEW operators; asserts CONSTRUCTION facts + machinery, NOT the
# open head-to-head hypothesis -- that is MEASURED in the FULL run and gated by the pre-reg bands, not asserted here)
# ===========================================================================

def _transition_asymmetry_check():
    """(M_i @ s)(*)e[x] is asymmetric in slots 0,1 (dominance-capable); at M=I it reduces to elementwise product."""
    g = torch.Generator().manual_seed(123)
    emb = 1.0 + 0.2 * torch.randn(L, EMB_D, generator=g)
    M_rand = torch.eye(EMB_D).unsqueeze(0).repeat(K, 1, 1) + 0.3 * torch.randn(K, EMB_D, EMB_D, generator=g)
    Xa = torch.tensor([[0, 3, 1, 2]]); Xb = torch.tensor([[3, 0, 1, 2]])   # swap slots 0,1 only
    za = _transition_compose(emb, M_rand, Xa, [0, 1, 2, 3])
    zb = _transition_compose(emb, M_rand, Xb, [0, 1, 2, 3])
    asym_ok = not bool(torch.allclose(za, zb, atol=1e-5))                 # MUST differ -> antisymmetric-capable
    M_id = torch.eye(EMB_D).unsqueeze(0).repeat(K, 1, 1)
    z_id = _transition_compose(emb, M_id, Xa, [0, 1, 2, 3])
    z_elem = emb[Xa].prod(dim=1)
    reduces_ok = bool(torch.allclose(z_id, z_elem, atol=1e-5))           # init M=I == elementwise product (== SYM)
    # order-shuffle changes output under non-identity M (order-non-commutativity is real)
    z_shuf = _transition_compose(emb, M_rand, Xa, [3, 1, 2, 0])
    shuf_ok = not bool(torch.allclose(za, z_shuf, atol=1e-5))
    return asym_ok, reduces_ok, shuf_ok


def _phase_offset_absorbed_check():
    """Adding fixed per-role offsets shifts the summed phasor angle by a DATA-INDEPENDENT constant (absorbed)."""
    g = torch.Generator().manual_seed(7)
    phi = 2.0 * math.pi * torch.rand(L, EMB_D, generator=g)
    Xi = torch.tensor([[0, 1, 2, 3], [3, 2, 1, 0]])
    theta = (2.0 * math.pi / K) * torch.arange(K, dtype=torch.float32)
    ang_off = (phi[Xi] + theta.view(1, K, 1)).sum(dim=1)
    ang_no = phi[Xi].sum(dim=1)
    diff = ang_off - ang_no                                              # should be a constant across rows
    const_ok = bool(torch.allclose(diff, diff[0:1].expand_as(diff), atol=1e-5))
    return const_ok


def _heteroassoc_mechanism_check():
    """The outer-product correlation-matrix READOUT is correct on well-separated (near-orthogonal) keys:
    W = onehot(y)^T F ; argmax(F W^T) == y. Isolates mechanism correctness from arena key-similarity crosstalk."""
    g = torch.Generator().manual_seed(1)
    P = 40; D = 2 * HETERO_D; nclass = 4
    F = torch.randn(P, D, generator=g); F = F / F.norm(dim=1, keepdim=True)
    y = torch.randint(0, nclass, (P,), generator=g).numpy()
    Y = np.eye(nclass, dtype=np.float64)[y]
    Fnp = F.numpy(); W = Y.T @ Fnp
    pred = np.argmax(Fnp @ W.T, axis=1)
    return float((pred == y).mean())


def _heteroassoc_seen_recall_check():
    """One-shot Hebbian memory recalls SEEN combos (construction sanity floor for the lookup diagnostic).
    NOTE: bounded well below 1.0 by design -- role-filler-bundled keys inherit combo-similarity, so similar
    combos with conflicting labels crosstalk (a distributed memory cannot exact-recall overlapping keys the way
    an exact-hash MEMORIZE arm can). Floor is set above chance (0.5), not near 1.0."""
    rng = np.random.default_rng(5)
    Xtr = rng.integers(0, L, size=(60, K)).astype(np.int64)
    # unique combos only, deterministic labels by combo-id parity of slot0>slot1 (an ordered relation)
    seen = {}
    rows = []
    for r in range(Xtr.shape[0]):
        key = tuple(Xtr[r].tolist())
        if key not in seen:
            seen[key] = int(Xtr[r, 0] > Xtr[r, 1])
            rows.append(r)
    Xu = Xtr[rows]
    ytr = np.array([seen[tuple(Xtr[r].tolist())] for r in range(Xtr.shape[0])], dtype=np.int64)
    yq = np.array([seen[tuple(Xu[i].tolist())] for i in range(Xu.shape[0])], dtype=np.int64)
    pred = arm_heteroassoc(Xtr, ytr, Xu, 2, seed=3)
    return float((pred == yq).mean())


def self_test():
    ok_all = True
    details = {}

    # (1) REAL FHRR bind homomorphism (complex path) -- REUSED.
    g = np.random.default_rng(31)
    m = g.integers(1, max(2, L), size=64).astype(np.float64)
    jj = np.arange(L, dtype=np.float64)[:, None]
    Ycode = torch.from_numpy(np.exp(1j * (2.0 * np.pi / L) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Ycode[torch.tensor([1, 2])], Ycode[torch.tensor([2, 3])])
    Yc = Ycode.conj().T.contiguous()
    homo_ok = torch.argmax((bound @ Yc).real, 1).tolist() == [3 % L, 5 % L]
    details["fhrr_homomorphism_ok"] = homo_ok

    # (2) REAL FHRR-bind parity/AND fold vs numpy ground truth -- REUSED.
    bits = np.array([[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1]], dtype=np.int64)
    par_ok = (_mult_fold_signs(bits) < 0).astype(np.int64).tolist() == (bits.sum(1) % 2).tolist()
    and_ok = np.rint(_mult_fold_indicators(bits, [0, 1])).astype(np.int64).tolist() == (bits[:, 0] & bits[:, 1]).tolist()
    details["bsc_parity_ok"] = par_ok; details["bsc_and_ok"] = and_ok

    # (3) NEW operator machinery.
    trans_asym, trans_reduces, trans_shuf_diff = _transition_asymmetry_check()
    phase_absorbed = _phase_offset_absorbed_check()
    hetero_mech = _heteroassoc_mechanism_check()
    hetero_seen_recall = _heteroassoc_seen_recall_check()
    details.update(dict(transition_asymmetric_in_slots01=trans_asym,
                        transition_init_reduces_to_elementwise=trans_reduces,
                        transition_order_shuffle_changes_output=trans_shuf_diff,
                        phase_offset_is_absorbed_constant=phase_absorbed,
                        heteroassoc_mechanism_recall=round(hetero_mech, 4),
                        heteroassoc_combo_seen_recall=round(hetero_seen_recall, 4)))

    # (4) PARITY arena (SYMMETRIC). CONSTRUCTION: INT_MATCH solves, MONO ~chance, SYM specialist discovers.
    X = make_X(7)
    yp = target(PARITY, X)
    rc = score(PARITY, CLEAN, X, yp, 7)["strata"]["novel"]
    ra = score(PARITY, ARBITRARY, X, yp, 7)["strata"]["novel"]
    ch_p = chance_of(PARITY, yp)
    int_p = rc[INT_MATCH]; mono_p = rc[MONO]; sym_p = rc[LEARN_SYM]; add_p = rc[LEARN_ADD]; freq_p = rc[FREQ]
    trans_arb_gap = ra[TRANSITION_OP] - ra[FREQ]
    details.update(dict(parity_INT=int_p, parity_MONO=mono_p, parity_SYM=sym_p, parity_LADD=add_p,
                        parity_TRANS=rc[TRANSITION_OP], parity_HETERO=rc[HETERO], parity_PHASE=rc[PHASE],
                        parity_FREQ=freq_p, parity_chance=round(ch_p, 4),
                        parity_trans_arb_gap=round(trans_arb_gap, 4), n_novel=rc["n"]))

    # (5) DOMINANCE arena (ANTISYMMETRIC). CONSTRUCTION: INT_MATCH solves; SYM fails; role-keyed discovers.
    yd = target(DOMINANCE, X)
    sd_res = score(DOMINANCE, CLEAN, X, yd, 7)
    rd = sd_res["strata"]["novel"]; hetero_seen = sd_res["hetero_seen_acc"]
    ch_d = chance_of(DOMINANCE, yd)
    role_spec_d = max(rd[LEARN_INT], rd[LEARN_ADD])
    details.update(dict(dom_INT=rd[INT_MATCH], dom_SYM=rd[LEARN_SYM], dom_LINT=rd[LEARN_INT],
                        dom_LADD=rd[LEARN_ADD], dom_TRANS=rd[TRANSITION_OP], dom_TRANS_SHUF=rd[TRANS_SHUF],
                        dom_HETERO_novel=rd[HETERO], dom_HETERO_seen=hetero_seen, dom_PHASE=rd[PHASE],
                        dom_PHASE_NO=rd[PHASE_NO], dom_BILINEAR=rd[BILINEAR_REF],
                        dom_roleSpec=round(role_spec_d, 4), dom_FREQ=rd[FREQ], dom_chance=round(ch_d, 4)))

    # (6) ARMS-MUST-DIFFER (META_RULE_AF) on DOMINANCE-clean-novel over the distinct mechanism arms.
    digs = score(DOMINANCE, CLEAN, X, yd, 7)["sigs"]
    arms_differ = len(set(digs.values())) == len(digs)
    details["arms_differ_sig_count"] = len(set(digs.values()))
    details["arms_expected"] = len(digs)

    checks = {
        "fhrr_homomorphism": homo_ok,
        "bsc_parity": par_ok,
        "bsc_and": and_ok,
        # --- NEW operator construction (the load-bearing functional-requirement checks) ---
        "transition_asymmetric_in_slots01": trans_asym,          # CAN represent antisymmetric dominance
        "transition_init_reduces_to_elementwise": trans_reduces,  # init M=I == LEARN_SYM (clean baseline-equiv init)
        "transition_order_shuffle_changes_output": trans_shuf_diff,  # order non-commutativity is real
        "phase_offset_is_absorbed_constant": phase_absorbed,     # honest: offset is a fixed rotation (role-tag)
        "heteroassoc_mechanism_correct": hetero_mech >= 0.95,    # outer-product readout correct on separable keys
        "heteroassoc_recalls_seen_above_chance": hetero_seen_recall >= 0.70,  # memory functions (crosstalk-bounded)
        # --- arena solvable by the matched op; specialists behave as expected (REUSED) ---
        "INT_solves_parity_novel": int_p >= 0.90,
        "MONO_at_chance_parity": mono_p <= ch_p + 0.10,
        "INT_beats_MONO_parity": (int_p - mono_p) >= 0.30,
        "INT_solves_dominance": rd[INT_MATCH] >= 0.90,
        "SYM_specialist_discovers_parity": (sym_p - add_p) >= 0.15 and sym_p >= ch_p + 0.20,
        "role_specialist_discovers_dominance": (role_spec_d - rd[FREQ]) >= 0.10 and (role_spec_d - rd[LEARN_SYM]) >= 0.12,
        "SYM_fails_dominance": rd[LEARN_SYM] <= ch_d + 0.12,
        # --- fairness / integrity ---
        "arena_freq_not_saturated_parity": freq_p <= 0.75,
        "transition_arbitrary_mustfail_fires": trans_arb_gap <= 0.10,   # candidate does NOT beat freq on arbitrary
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
