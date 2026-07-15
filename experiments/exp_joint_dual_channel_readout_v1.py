r"""JOINT_DUAL_CHANNEL_READOUT (v1): the campaign's central experiment. Does ONE shared JOINT CODE z + TWO
SELECTIVE LEARNABLE READOUT HEADS discover BOTH a SYMMETRIC non-additive structure (PARITY) AND an
ASYMMETRIC / order-sensitive structure (DOMINANCE) on NOVEL combos -- resolving the role-keying<->symmetry
TENSION where each specialized bind does only ONE? This is the substrate realization of the brain's
structure-content factorization (Bernardi/Fusi/Salzman 2020 Cell: same population, different LINEAR
projections extract abstract-invariant vs conjunctive). Glass-box, NO LLM.

WHY (this arc): a prior cell (exp_interaction_nonadditive_discovery_v1, commit 59056b6d4) localized a real
tension -- the SYMMETRIC-product bind discovers symmetric PARITY (~0.98 vs additive ~0.38) but NOT asymmetric
DOMINANCE; the ROLE-KEYED bind does DOMINANCE but FAILS PARITY. NO single fixed composition op does both. A
brain-grounding drill (notes/drill_brain_unifies_symmetric_asymmetric_binding_factorization_2026-07-14.md,
section (d) RANK 1) found the brain's answer = JOINT CODE + SELECTIVE LINEAR READOUT.

MECHANISM (Rank 1 from the drill). Shared code, native ops only ((x)=hd_bind FHRR complex mul; +=complex sum):
  z = ( sum_i r_i (x) c(x_i) )  +  LAMBDA * ( c(x_0) (x) c(x_1) (x) ... (x) c(x_{K-1}) )
      [ ORDER term = role-keyed TPR bundle ]     [ CONFIG term = symmetric product ]
  r_i = FIXED role phasors (CONSTRUCT, order-sensitive TPR-style); c = SHARED LEARNABLE content/level code.
  TWO learnable linear readout heads on the SAME z:
    H_ORDER  reads phi_order(z)  = concat_i [Re,Im of unbind(z, r_i)]  -> per-ROLE recovered content
             (ORDER-SENSITIVE: positions distinguished; a linear head compares pos0 vs pos1 => DOMINANCE;
             per-position LINEAR features cannot express PARITY's joint product).
    H_CONFIG reads phi_config(z) = [Re,Im of PROD_i normalize(unbind(z, r_i))]  -> SYMMETRIC product recovery
             (ORDER-INVARIANT nonlinear lens: product over positions => cannot express DOMINANCE; sign=PARITY).

  DESIGN-CRITICAL FINDING (this cell, dim/lambda sweeps): with LINEAR readout heads a value's SIGN (the parity
  carrier) is linearly extractable from ANY superposition that contains it, so a NON-ZERO LAMBDA leaks the
  CONFIG/parity signal linearly into the role-unbind -> the ORDER head then reads parity -> HEAD-DISCRIMINATION
  BREAKS (measured: JD_ORDER on parity jumps 0.41 -> 1.0 as lambda 0 -> 0.25). Clean separation therefore
  requires LAMBDA = 0: the role-keyed bundle ALONE is the joint code, and the config channel is recovered
  NONLINEARLY (product-of-unbinds), which the linear order head cannot fake. This is a genuine finding, not a
  workaround: linear VSA superposition is linearly entangled; the NONLINEARITY (product lens) is what gives the
  two heads genuinely different channels -- mirroring the brain's NONLINEAR mixed selectivity (Bernardi 2020),
  where linear readouts separate channels only because the population is nonlinearly mixed.
  EMB_D=96 chosen by sweep (D=40 -> 24% config interference; D=96 -> 7%; D=160 -> single-seed unstable).

CONTRACT (central question + key risk):
  (Q) Does JOINT_DUAL (z + both heads) discover BOTH parity AND dominance on NOVEL combos?
  (RISK) CROSS-CHANNEL INTERFERENCE: carrying both channels in one z must NOT degrade either readout vs its
         specialist. HARD_PASS requires JD_CONFIG(parity) >= SYMMETRIC_PRODUCT specialist and JD_ORDER(dom)
         >= ROLE_KEYED specialist within a small tolerance.
  (HEAD-DISCRIMINATION) the WRONG head must FAIL on each family (H_ORDER must NOT solve parity; H_CONFIG must
         NOT solve dominance) -- proves the heads read genuinely DIFFERENT channels, not one blended signal.

ARMS (per family x regime x seed; NOVEL stratum is the headline):
  JOINT_DUAL -> two readouts JD_CONFIG, JD_ORDER from ONE shared z (content codes + both heads trained jointly).
  SYMMETRIC_PRODUCT  parity specialist / dedicated symmetric code: z=T_config only, direct [Re,Im] + head.
  ROLE_KEYED         dominance specialist / dedicated order code: z=T_order only, role-unbind stack + head.
  CONFIG_SOLO        DIAGNOSTIC (weak-point localization): config head ALONE on the joint code z=T_order via the
                     product lens -> isolates PURE dual-head interference (JD_CONFIG vs CONFIG_SOLO) from the
                     unbind-reconstruction cost (CONFIG_SOLO vs SYMMETRIC_PRODUCT-direct).
  LEARN_ADD          role-keyed SUM (no bind) + linear head -- additive contrast (fails parity by construction).
  FREQ_NULL = max(HOMOPHILY_COND, POP) ; MEMORIZE ; POP ; ORACLE (ceiling).
  Specialists/CONFIG_SOLO/LEARN_ADD run on CLEAN only (meaningless on random must-fail targets); the must-fail
  regimes exercise JOINT_DUAL's BOTH heads + baselines (compute proportionality).
Families: PARITY (symmetric non-additive) + DOMINANCE (antisymmetric) = the two GATED headline families;
  AND2/MULT/ADD carried as transform-additive CONTEXT (reported, NOT claimed as interaction wins).
MUST-FAILS (per claim-family): ARBITRARY (random class per unique combo) + SHUFFLE (label permutation). No
  mechanism head may beat FREQ_NULL on these NOVEL sets (gap <= MUSTFAIL_TOL) -- fires on BOTH heads.
Determinism: all RNG seeds from INTEGER indices (FAM_IDX/REG_IDX mixed-radix), never the salted builtin hasher
  (PROT-023). Reuses arena/families/controls/split/must-fails from exp_interaction_nonadditive_discovery_v1.

PRE-REGISTERED BANDS (fixed BEFORE running; full table + rationale in the prereg .md):
  HARD_PASS (JOINT_DUAL discovers BOTH + no interference + head-discrimination clean), on NOVEL 5-seed mean:
    G1 parity_discovered:  JD_CONFIG >= 0.70
    G2 dom_discovered:     JD_ORDER  >= FREQ_NULL_dom + 0.10
    G3 parity_headdisc:    JD_ORDER  <= chance_parity + 0.15   (wrong head fails parity)
    G4 dom_headdisc:       JD_CONFIG <= FREQ_NULL_dom + 0.07   (wrong head fails dominance)
    G5 parity_no_interf:   JD_CONFIG >= (1 - 0.15) * SYMMETRIC_PRODUCT
    G6 dom_no_interf:      JD_ORDER  >= (1 - 0.15) * ROLE_KEYED
    G7 must-fails fire on BOTH heads (claim families); G8 oracle ceiling ok.
  REFUTE: JD_CONFIG(parity) <= 0.20 OR JD_ORDER(dom) <= FREQ_NULL_dom (no margin)
          OR interference > 30% relative drop on EITHER channel (destructive -> escalate Rank 4)
          OR head-discrimination fails (JD_ORDER(parity) > chance_p + 0.15 OR JD_CONFIG(dom) > FREQ_NULL_dom
             + 0.15) -- channels not genuinely separable.
  MIDDLE_BAND: anything else (e.g. both discovered + head-disc clean but interference in 15-30% band).
  Interference tol 0.15/0.30 (not the drill's 0.10/0.25): single-seed variance of the specialist itself is
  ~0.05-0.10 at n~121 train, and the JD-vs-dedicated gap conflates true dual-head interference (localized by
  CONFIG_SOLO) with the unbind-reconstruction cost of a role-keyed joint code; 0.15/0.30 is band-authority
  judgment documented in the prereg.
HONEST FRAMING: joint-code-selective-readout is a research synthesis (drill P_deflated 0.38) and
  WHERE-asymmetry-lives is contested; this cell tests the ENGINEERING claim (does a two-channel code carry
  both), not the neuroscience locus.

Glass-box CPU. Default invocation (no flag) = FULL run to completion (runner calls `python -u <script>`).
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

from hdlab.binding import bind as hd_bind      # noqa: E402  # REAL FHRR bind (complex64 elementwise mul).
# NOTE: only the long-stable `bind` (present on both local + remote runner). The ORDER bind (r_i (x) c), the
# CONFIG product (c (x) c ...), and the role-UNBIND (bind with conjugate) all route through hd_bind on
# COMPLEX64 -> a.is_complex() -> a*b elementwise (the substrate multiplicative bind). Bundle (+) = complex sum.

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline (defense in depth)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "joint_dual_channel_readout_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ---- arena (VERBATIM from exp_interaction_nonadditive_discovery_v1) ----
K = 4               # constituents
L = 4               # ordinal levels per constituent (0..3)
N_ENT = 220         # sampled entities (combo space L^K = 256)
QUERY_FRAC = 0.45

# ---- families / regimes ----
PARITY = "PARITY"; AND2 = "AND2"; MULT = "MULT"; DOMINANCE = "DOMINANCE"; ADD = "ADD"
FAMILIES = [PARITY, AND2, MULT, DOMINANCE, ADD]
NCLASS = {PARITY: 2, AND2: 2, MULT: 4, DOMINANCE: 2, ADD: 4}
GATED_FAMILIES = [PARITY, DOMINANCE]   # the two headline / gated families; rest = context

CLEAN = "CLEAN"; ARBITRARY = "ARBITRARY"; SHUFFLE = "SHUFFLE"
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]
CLAIM_FAMILIES = [PARITY, AND2, MULT, DOMINANCE]
# Deterministic integer indices for RNG seeding (NEVER the salted builtin hasher; PROT-023 scans).
FAM_IDX = {f: i for i, f in enumerate(FAMILIES)}
REG_IDX = {r: i for i, r in enumerate(REGIMES)}

# ---- arm names ----
JD_CONFIG = "JD_CONFIG"          # JOINT_DUAL config head (symmetric product lens) -> parity
JD_ORDER = "JD_ORDER"            # JOINT_DUAL order head (role-unbind lens) -> dominance
SYM_PROD = "SYMMETRIC_PRODUCT"   # parity specialist / dedicated symmetric code (direct product read)
ROLE_KEY = "ROLE_KEYED"          # dominance specialist / dedicated order code (role-unbind read)
CFG_SOLO = "CONFIG_SOLO"         # diagnostic: config head ALONE on joint code (pure dual-head interference)
LEARN_ADD = "LEARN_ADD"          # role-keyed SUM (additive contrast)
HOM = "HOMOPHILY_COND"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"
ARM_NAMES = [JD_CONFIG, JD_ORDER, SYM_PROD, ROLE_KEY, CFG_SOLO, LEARN_ADD, HOM, MEMO, POP, ORC, FREQ]

# ---- mechanism hyperparams (fixed BEFORE running) ----
EMB_D = 96          # content-code / role dim (complex); chosen by sweep (7% config interference at D=96)
EPOCHS = 500
LR = 0.05
LAMBDA_FIXED = 0.0  # config-term coefficient. FINDING: lambda>0 leaks parity linearly into the order lens and
#                     breaks head-discrimination (measured); lambda=0 => role-keyed bundle IS the joint code.
ROLE_SEED = 90011   # FIXED role-phasor construction seed (CONSTRUCT, not learned)

# ---- pre-registered bands (fixed before running) ----
HP_PARITY_CONFIG_FLOOR = 0.70    # G1: JD_CONFIG novel on parity
HP_DOM_ORDER_FREQ_MARGIN = 0.10  # G2: JD_ORDER - FREQ_NULL on dominance
HEADDISC_PARITY_MARGIN = 0.15    # G3: JD_ORDER (wrong head) <= chance_parity + this on parity
HEADDISC_DOM_MARGIN = 0.07       # G4: JD_CONFIG (wrong head) <= FREQ_NULL_dom + this on dominance
INTERFERENCE_REL_TOL = 0.15      # G5/G6: JD channel >= (1-tol) * specialist
REFUTE_INTERFERENCE_REL = 0.30   # > this relative drop => destructive interference
REFUTE_HEADDISC_DOM = 0.15       # JD_CONFIG(dom) > FREQ_NULL_dom + this => channels not separable
REFUTE_FLOOR = 0.20              # either JD channel <= this on its family => channel dead
MUSTFAIL_TOL = 0.10              # mechanism head - FREQ_NULL on ARBITRARY/SHUFFLE novel must be <= this.


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
# ARENA + TARGET FAMILIES (VERBATIM from exp_interaction_nonadditive_discovery_v1)
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
    """Returns (y_used, y_oracle). ARBITRARY/SHUFFLE are must-fail controls."""
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
# MI diagnostic (non-additivity evidence; reported, not gated) -- VERBATIM
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
# FIXED role phasors (CONSTRUCT). Unit complex phasors, deterministic integer seed.
# ===========================================================================

def make_roles(d=EMB_D):
    rng = np.random.default_rng(ROLE_SEED)
    phase = 2.0 * np.pi * rng.random((K, d))
    return torch.from_numpy(np.exp(1j * phase).astype(np.complex64))   # (K, d) unit phasors


# ===========================================================================
# shared z-construction + lenses (native ops: hd_bind for (x); complex sum for +)
# ===========================================================================

def _init_content(d, g):
    """Shared learnable content-code table (L, d) as unit-phasor real/imag parts (near unit circle)."""
    theta = 2.0 * math.pi * torch.rand(L, d, generator=g)
    cr = torch.nn.Parameter(torch.cos(theta).clone())
    ci = torch.nn.Parameter(torch.sin(theta).clone())
    return cr, ci


def _bind_expand(a_row, b_batch):
    """hd_bind of a (d,) complex row broadcast against a (n,d) complex batch -> (n,d)."""
    return hd_bind(a_row.unsqueeze(0).expand(b_batch.shape[0], -1), b_batch)


def _order_term(cont, roles):
    """cont: (n,k,d) complex; roles: (k,d). T_order (n,d) = sum_i r_i (x) c(x_i) (bind + bundle)."""
    k = cont.shape[1]
    t = _bind_expand(roles[0], cont[:, 0, :])
    for i in range(1, k):
        t = t + _bind_expand(roles[i], cont[:, i, :])   # bundle = complex sum
    return t


def _config_term(cont):
    """cont: (n,k,d) complex. T_config (n,d) = c(x_0) (x) c(x_1) (x) ... (product bind)."""
    k = cont.shape[1]
    t = cont[:, 0, :]
    for i in range(1, k):
        t = hd_bind(t, cont[:, i, :])
    return t


def _unbinds(z, roles):
    """Per-role unbind of z, each per-sample magnitude-normalized (keeps the product lens O(1))."""
    us = []
    for i in range(roles.shape[0]):
        u = _bind_expand(torch.conj(roles[i]), z)       # unbind = bind with conjugate (FHRR)
        u = u / (u.abs().mean(1, keepdim=True) + 1e-6)
        us.append(u)
    return us


def _phi_order(z, roles):
    """Role-unbind stack: concat_i [Re,Im of unbind(z, r_i)] -> (n, k*2d). ORDER-SENSITIVE lens."""
    us = _unbinds(z, roles)
    return torch.cat([x for u in us for x in (u.real, u.imag)], dim=1)


def _phi_config(z, roles):
    """Product of role-unbinds: prod_i unbind(z, r_i) -> [Re,Im] (n, 2d). ORDER-INVARIANT nonlinear lens
    (product over positions is invariant to value-swap => cannot express dominance; sign => parity)."""
    us = _unbinds(z, roles)
    prod = us[0]
    for i in range(1, len(us)):
        prod = hd_bind(prod, us[i])
    return torch.cat([prod.real, prod.imag], dim=1)


def _norm_fit(feat):
    mu = feat.mean(0, keepdim=True); sd = feat.std(0, keepdim=True) + 1e-3
    return mu, sd


def _train_joint_dual(Xtr, ytr, Xq, nclass, seed, roles, epochs=EPOCHS):
    """Shared z = T_order + LAMBDA_FIXED*T_config; TWO heads (order, config) trained JOINTLY on shared content
    codes. Returns (order_pred, config_pred)."""
    g = torch.Generator().manual_seed(seed * 7919 + 11)
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    d = roles.shape[1]
    cr, ci = _init_content(d, g)
    Wo = torch.nn.Parameter(0.1 * torch.randn(K * 2 * d, nclass, generator=g)); bo = torch.nn.Parameter(torch.zeros(nclass))
    Wc = torch.nn.Parameter(0.1 * torch.randn(2 * d, nclass, generator=g)); bc = torch.nn.Parameter(torch.zeros(nclass))
    opt = torch.optim.Adam([cr, ci, Wo, bo, Wc, bc], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def build_z(Xi):
        cc = torch.complex(cr, ci)
        cont = cc[Xi]
        z = _order_term(cont, roles)
        if LAMBDA_FIXED != 0.0:
            z = z + LAMBDA_FIXED * _config_term(cont)
        return z

    for _ in range(epochs):
        opt.zero_grad()
        z = build_z(Xt)
        fo = _phi_order(z, roles); fc = _phi_config(z, roles)
        mo, so = _norm_fit(fo); mc, sc = _norm_fit(fc)
        lo = ((fo - mo) / so) @ Wo + bo
        lc = ((fc - mc) / sc) @ Wc + bc
        loss = lossf(lo, yt) + lossf(lc, yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        z_tr = build_z(Xt)
        fo_tr = _phi_order(z_tr, roles); fc_tr = _phi_config(z_tr, roles)
        mo, so = _norm_fit(fo_tr); mc, sc = _norm_fit(fc_tr)
        z_q = build_z(Xu)
        fo_q = _phi_order(z_q, roles); fc_q = _phi_config(z_q, roles)
        order_pred = torch.argmax(((fo_q - mo) / so) @ Wo + bo, 1).numpy().astype(np.int64)
        config_pred = torch.argmax(((fc_q - mc) / sc) @ Wc + bc, 1).numpy().astype(np.int64)
    return order_pred, config_pred


def _train_single(Xtr, ytr, Xq, nclass, seed, roles, channel, epochs=EPOCHS):
    """Single-head arm on its own content codes.
    channel='config_direct' -> z=T_config, direct [Re,Im] (SYMMETRIC_PRODUCT dedicated specialist);
    channel='order'         -> z=T_order, role-unbind stack (ROLE_KEYED dedicated specialist);
    channel='config_solo'   -> z=T_order, product-of-unbinds config lens (pure dual-head interference ref)."""
    salt = {"config_direct": 21, "order": 31, "config_solo": 41}[channel]
    g = torch.Generator().manual_seed(seed * 7919 + salt)
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    d = roles.shape[1]
    cr, ci = _init_content(d, g)
    feat_dim = 2 * d if channel in ("config_direct", "config_solo") else K * 2 * d
    W = torch.nn.Parameter(0.1 * torch.randn(feat_dim, nclass, generator=g)); b = torch.nn.Parameter(torch.zeros(nclass))
    opt = torch.optim.Adam([cr, ci, W, b], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def feat(Xi):
        cc = torch.complex(cr, ci)
        cont = cc[Xi]
        if channel == "config_direct":
            z = _config_term(cont)
            return torch.cat([z.real, z.imag], dim=1)
        z = _order_term(cont, roles)
        return _phi_config(z, roles) if channel == "config_solo" else _phi_order(z, roles)

    for _ in range(epochs):
        opt.zero_grad()
        f = feat(Xt); mu, sd = _norm_fit(f)
        loss = lossf(((f - mu) / sd) @ W + b, yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        f_tr = feat(Xt); mu, sd = _norm_fit(f_tr)
        pred = torch.argmax(((feat(Xu) - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
    return pred


def _train_learn_add(Xtr, ytr, Xq, nclass, seed, epochs=EPOCHS):
    """Role-keyed SUM of real embeddings + linear head (additive contrast; fails parity by construction)."""
    g = torch.Generator().manual_seed(seed * 7919 + 51)
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(ytr).long()
    emb = torch.nn.Parameter(0.2 * torch.randn(K, L, EMB_D, generator=g))
    W = torch.nn.Parameter(0.1 * torch.randn(EMB_D, nclass, generator=g)); b = torch.nn.Parameter(torch.zeros(nclass))
    opt = torch.optim.Adam([emb, W, b], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def comp(Xi):
        e = emb[torch.arange(K).unsqueeze(0), Xi]
        return e.sum(dim=1)

    for _ in range(epochs):
        opt.zero_grad()
        h = comp(Xt); mu = h.mean(0, keepdim=True); sd = h.std(0, keepdim=True) + 1e-3
        loss = lossf(((h - mu) / sd) @ W + b, yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        h_tr = comp(Xt); mu = h_tr.mean(0, keepdim=True); sd = h_tr.std(0, keepdim=True) + 1e-3
        pred = torch.argmax(((comp(Xu) - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
    return pred


# ===========================================================================
# baselines (VERBATIM from exp_interaction_nonadditive_discovery_v1)
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
    if pred is None or len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


# ===========================================================================
# per (family, regime, seed) scoring
# ===========================================================================

def score(family, regime, X, y_clean, seed, roles, epochs=EPOCHS):
    q, tr, novel = split_novel(X, seed)
    y_used, y_oracle = plant_regime(X, y_clean, family, regime, seed)
    Xq, Xtr = X[q], X[tr]
    gold, ytr = y_used[q], y_used[tr]
    nc = NCLASS[family]
    pop_label = int(np.argmax(np.bincount(ytr, minlength=nc)))

    is_clean = (regime == CLEAN)
    is_gated = (family in GATED_FAMILIES)

    jd_order, jd_config = _train_joint_dual(Xtr, ytr, Xq, nc, seed, roles, epochs)
    preds = {JD_CONFIG: jd_config, JD_ORDER: jd_order,
             HOM: arm_homophily(family, Xtr, ytr, Xq),
             MEMO: arm_memorize(family, Xtr, ytr, Xq, pop_label),
             POP: np.full(Xq.shape[0], pop_label, dtype=np.int64),
             ORC: y_oracle[q]}
    if is_clean:
        preds[LEARN_ADD] = _train_learn_add(Xtr, ytr, Xq, nc, seed, epochs)
    if is_clean and is_gated:   # specialists/diagnostic only where the interference comparison is meaningful
        preds[SYM_PROD] = _train_single(Xtr, ytr, Xq, nc, seed, roles, "config_direct", epochs)
        preds[ROLE_KEY] = _train_single(Xtr, ytr, Xq, nc, seed, roles, "order", epochs)
        preds[CFG_SOLO] = _train_single(Xtr, ytr, Xq, nc, seed, roles, "config_solo", epochs)

    def a(pred, m):
        return acc(np.asarray(pred)[m], gold[m]) if (pred is not None and m.sum() > 0) else float("nan")

    out = {}
    for sname, m in (("novel", novel), ("seen", ~novel), ("all", np.ones(len(gold), bool))):
        d = {arm: round(a(preds.get(arm), m), 5) for arm in ARM_NAMES}
        d[FREQ] = round(max(d[HOM], d[POP]), 5)
        d["n"] = int(m.sum())
        out[sname] = d
    # ARMS-MUST-DIFFER (META_RULE_AF): the 3 core LEARNED arms (distinct architectures) must be bit-distinct.
    # Baselines (HOM/MEMO/POP) legitimately coincide on novel combos; specialists can equal gold on a solved
    # family -- so the strict distinctness check scopes to the mechanism arms whose coincidence WOULD be a bug.
    sig_arms = [JD_CONFIG, JD_ORDER, LEARN_ADD]
    sigs = {arm: _sig(preds[arm]) for arm in sig_arms if arm in preds}
    return dict(strata=out, sigs=sigs, n_novel=int(novel.sum()), n_query=int(len(gold)))


# ===========================================================================
# full measurement
# ===========================================================================

def _write_start_marker(expected_n_units, run_mode):
    import platform
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUT_DIR, "_start_marker.json"))


def run_measurement(seeds=(7, 13, 17, 23, 29), run_mode="full"):
    _write_start_marker(len(FAMILIES) * len(seeds) * len(REGIMES), run_mode)
    _log("%s run: %d families x %d seeds x %d regimes, arena K=%d L=%d N=%d D=%d epochs=%d lambda=%.2f"
         % (run_mode, len(FAMILIES), len(seeds), len(REGIMES), K, L, N_ENT, EMB_D, EPOCHS, LAMBDA_FIXED))
    roles = make_roles()
    per = {fam: {reg: [] for reg in REGIMES} for fam in FAMILIES}
    chances = {}; nonadd = {}
    t0 = time.perf_counter()
    for si, sd in enumerate(seeds):
        X = make_X(sd)
        for fam in FAMILIES:
            y_clean = target(fam, X)
            if sd == seeds[0]:
                chances[fam] = chance_of(fam, y_clean)
                nonadd[fam] = nonadditivity(X, y_clean)
            for reg in REGIMES:
                per[fam][reg].append(score(fam, reg, X, y_clean, sd, roles))
                # heartbeat every (family,regime) ~15-30s -> satisfies the 60s progress-cadence rule (Sec 17)
                _log("  hb seed=%d/%d fam=%s reg=%s elapsed=%.1fs" % (si + 1, len(seeds), fam, reg, time.perf_counter() - t0))
        _log("  seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))

    def mean_novel(fam, reg, arm):
        vals = [ps["strata"]["novel"][arm] for ps in per[fam][reg]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    table = {}
    for fam in FAMILIES:
        table[fam] = {arm: round(mean_novel(fam, CLEAN, arm), 5) for arm in ARM_NAMES}
        table[fam]["chance"] = round(chances[fam], 5)
        for head in (JD_CONFIG, JD_ORDER):
            table[fam]["arb_gap_%s" % head] = round(mean_novel(fam, ARBITRARY, head) - mean_novel(fam, ARBITRARY, FREQ), 5)
            table[fam]["shuf_gap_%s" % head] = round(mean_novel(fam, SHUFFLE, head) - mean_novel(fam, SHUFFLE, FREQ), 5)

    p = table[PARITY]; dmn = table[DOMINANCE]
    ch_p = chances[PARITY]
    freq_dom = dmn[FREQ]

    def rel_drop(jd, spec):
        return 0.0 if spec <= 1e-9 else float((spec - jd) / spec)
    parity_rel_drop = rel_drop(p[JD_CONFIG], p[SYM_PROD])
    dom_rel_drop = rel_drop(dmn[JD_ORDER], dmn[ROLE_KEY])
    # weak-point localization: pure dual-head interference (vs CONFIG_SOLO) vs unbind-reconstruction cost.
    parity_dualhead_drop = rel_drop(p[JD_CONFIG], p[CFG_SOLO])

    parity_solved = bool(p[JD_CONFIG] >= HP_PARITY_CONFIG_FLOOR)                          # G1
    dom_solved = bool(dmn[JD_ORDER] >= freq_dom + HP_DOM_ORDER_FREQ_MARGIN)               # G2
    parity_headdisc = bool(p[JD_ORDER] <= ch_p + HEADDISC_PARITY_MARGIN)                  # G3
    dom_headdisc = bool(dmn[JD_CONFIG] <= freq_dom + HEADDISC_DOM_MARGIN)                 # G4
    parity_no_interf = bool(parity_rel_drop <= INTERFERENCE_REL_TOL)                      # G5
    dom_no_interf = bool(dom_rel_drop <= INTERFERENCE_REL_TOL)                            # G6
    mustfail_ok = all(table[fam]["arb_gap_%s" % h] <= MUSTFAIL_TOL and table[fam]["shuf_gap_%s" % h] <= MUSTFAIL_TOL
                      for fam in CLAIM_FAMILIES for h in (JD_CONFIG, JD_ORDER))           # G7
    ceiling_ok = all(table[fam][ORC] >= max(table[fam][JD_CONFIG], table[fam][JD_ORDER]) - 1e-6 for fam in GATED_FAMILIES)  # G8

    hard_pass = bool(parity_solved and dom_solved and parity_headdisc and dom_headdisc
                     and parity_no_interf and dom_no_interf and mustfail_ok and ceiling_ok)

    refute_floor = bool(p[JD_CONFIG] <= REFUTE_FLOOR or dmn[JD_ORDER] <= freq_dom)
    refute_interf = bool(parity_rel_drop > REFUTE_INTERFERENCE_REL or dom_rel_drop > REFUTE_INTERFERENCE_REL)
    refute_headdisc = bool(p[JD_ORDER] > ch_p + HEADDISC_PARITY_MARGIN or dmn[JD_CONFIG] > freq_dom + REFUTE_HEADDISC_DOM)
    refute = bool(refute_floor or refute_interf or refute_headdisc)

    if hard_pass:
        verdict = "HARD_PASS_JOINT_DUAL_CARRIES_BOTH_CHANNELS_NO_INTERFERENCE_HEADDISC_CLEAN"
    elif refute:
        tags = []
        if refute_floor:
            tags.append("CHANNEL_DEAD")
        if refute_interf:
            tags.append("DESTRUCTIVE_INTERFERENCE")
        if refute_headdisc:
            tags.append("HEADS_NOT_SEPARABLE")
        verdict = "REFUTE_" + "_".join(tags)
    else:
        both_disc = parity_solved and dom_solved
        both_hd = parity_headdisc and dom_headdisc
        if both_disc and both_hd:
            verdict = "MIDDLE_BOTH_DISCOVERED_HEADDISC_CLEAN_INTERFERENCE_OVER_TOL"
        elif both_disc:
            verdict = "MIDDLE_BOTH_DISCOVERED_HEADDISC_WEAK"
        elif parity_solved:
            verdict = "PARTIAL_CONFIG_ONLY_PARITY"
        elif dom_solved:
            verdict = "PARTIAL_ORDER_ONLY_DOMINANCE"
        else:
            verdict = "MIDDLE_BAND"

    msg = ("%s || PARITY(ch=%.2f,SYMM): JD_CONFIG=%s SYM_PROD=%s (rel_drop=%s; CFG_SOLO=%s dualhead_drop=%s) "
           "JD_ORDER(wrong)=%s LADD=%s | DOMINANCE(freq=%.2f,ANTISYMM): JD_ORDER=%s ROLE_KEY=%s (rel_drop=%s) "
           "JD_CONFIG(wrong)=%s | gates[G1par=%s G2dom=%s G3parHD=%s G4domHD=%s G5parI=%s G6domI=%s G7mf=%s G8ceil=%s]"
           % (verdict, ch_p, _fmt(p[JD_CONFIG]), _fmt(p[SYM_PROD]), _fmt(parity_rel_drop), _fmt(p[CFG_SOLO]),
              _fmt(parity_dualhead_drop), _fmt(p[JD_ORDER]), _fmt(p[LEARN_ADD]),
              freq_dom, _fmt(dmn[JD_ORDER]), _fmt(dmn[ROLE_KEY]), _fmt(dom_rel_drop), _fmt(dmn[JD_CONFIG]),
              parity_solved, dom_solved, parity_headdisc, dom_headdisc, parity_no_interf, dom_no_interf,
              mustfail_ok, ceiling_ok))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode=run_mode,
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        arena=dict(K=K, L=L, N_ENT=N_ENT, query_frac=QUERY_FRAC), seeds=list(seeds),
        emb_d=EMB_D, epochs=EPOCHS, lr=LR, lambda_fixed=LAMBDA_FIXED,
        chances=chances, nonadditivity=nonadd,
        table_clean_novel=table,
        gates=dict(hard_pass=hard_pass, refute=refute, refute_floor=refute_floor, refute_interf=refute_interf,
                   refute_headdisc=refute_headdisc,
                   parity_solved=parity_solved, dom_solved=dom_solved,
                   parity_headdisc=parity_headdisc, dom_headdisc=dom_headdisc,
                   parity_no_interf=parity_no_interf, dom_no_interf=dom_no_interf,
                   mustfail_ok=mustfail_ok, ceiling_ok=ceiling_ok,
                   parity_JD_CONFIG=round(p[JD_CONFIG], 5), parity_SYM_PROD=round(p[SYM_PROD], 5),
                   parity_CFG_SOLO=round(p[CFG_SOLO], 5), parity_JD_ORDER_wrong=round(p[JD_ORDER], 5),
                   parity_rel_drop_vs_specialist=round(parity_rel_drop, 5),
                   parity_dualhead_drop_vs_solo=round(parity_dualhead_drop, 5),
                   dom_JD_ORDER=round(dmn[JD_ORDER], 5), dom_ROLE_KEY=round(dmn[ROLE_KEY], 5),
                   dom_JD_CONFIG_wrong=round(dmn[JD_CONFIG], 5), dom_rel_drop_vs_specialist=round(dom_rel_drop, 5),
                   dom_freq_null=round(freq_dom, 5)),
        bands=dict(HP_PARITY_CONFIG_FLOOR=HP_PARITY_CONFIG_FLOOR, HP_DOM_ORDER_FREQ_MARGIN=HP_DOM_ORDER_FREQ_MARGIN,
                   HEADDISC_PARITY_MARGIN=HEADDISC_PARITY_MARGIN, HEADDISC_DOM_MARGIN=HEADDISC_DOM_MARGIN,
                   INTERFERENCE_REL_TOL=INTERFERENCE_REL_TOL, REFUTE_INTERFERENCE_REL=REFUTE_INTERFERENCE_REL,
                   REFUTE_HEADDISC_DOM=REFUTE_HEADDISC_DOM, REFUTE_FLOOR=REFUTE_FLOOR, MUSTFAIL_TOL=MUSTFAIL_TOL),
        per_family_regime_novel={fam: {reg: [ps["strata"]["novel"] for ps in per[fam][reg]] for reg in REGIMES}
                                 for fam in FAMILIES},
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (exercises the REAL z-construction (bind+bundle+unbind) + both heads + specialists + must-fail)
# ===========================================================================

def self_test():
    ok_all = True
    details = {}
    roles = make_roles()
    ep = 250   # reduced epochs -> fast gate; checks are DIRECTIONAL (discriminator fires), not full-precision

    # (1) REAL FHRR bind homomorphism (bind of phasors reads out (i+j) mod L) -- proves hd_bind complex path live.
    gnp = np.random.default_rng(31)
    m = gnp.integers(1, max(2, L), size=32).astype(np.float64)
    jj = np.arange(L, dtype=np.float64)[:, None]
    Ycode = torch.from_numpy(np.exp(1j * (2.0 * np.pi / L) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Ycode[torch.tensor([1, 2])], Ycode[torch.tensor([2, 3])])
    homo_pred = torch.argmax((bound @ Ycode.conj().T.contiguous()).real, 1).tolist()
    homo_ok = homo_pred == [3 % L, 5 % L]
    details["fhrr_homomorphism_ok"] = homo_ok

    # (2) LENS SYMMETRY: config lens ~order-invariant under value-swap pos0<->pos1; order lens ~sensitive.
    #     (Ratio test -- the empirical head-discrimination is the load-bearing check below; this bounds it.)
    g = torch.Generator().manual_seed(7)
    cr, ci = _init_content(EMB_D, g)
    cc = torch.complex(cr, ci)
    Xa = torch.tensor([[0, 2, 1, 3]]); Xb = torch.tensor([[2, 0, 1, 3]])   # swap pos0<->pos1
    za = _order_term(cc[Xa], roles); zb = _order_term(cc[Xb], roles)       # lambda=0 code
    cfg_delta = float((_phi_config(za, roles) - _phi_config(zb, roles)).abs().mean().item())
    ord_delta = float((_phi_order(za, roles) - _phi_order(zb, roles)).abs().mean().item())
    details["config_swap_delta_mean"] = round(cfg_delta, 5)
    details["order_swap_delta_mean"] = round(ord_delta, 5)
    lens_symmetry_ratio = cfg_delta / (ord_delta + 1e-9)
    details["lens_symmetry_ratio_config_over_order"] = round(lens_symmetry_ratio, 5)

    # (3) PARITY arena (SYMMETRIC): JD_CONFIG solves; JD_ORDER (wrong head) fails; JD_CONFIG ~ SYM_PROD.
    X = make_X(7)
    yp = target(PARITY, X)
    rc = score(PARITY, CLEAN, X, yp, 7, roles, ep)["strata"]["novel"]
    ra = score(PARITY, ARBITRARY, X, yp, 7, roles, ep)["strata"]["novel"]
    ch_p = chance_of(PARITY, yp)
    details.update(dict(parity_JD_CONFIG=rc[JD_CONFIG], parity_SYM_PROD=rc[SYM_PROD], parity_CFG_SOLO=rc[CFG_SOLO],
                        parity_JD_ORDER_wrong=rc[JD_ORDER], parity_LEARN_ADD=rc[LEARN_ADD], parity_FREQ=rc[FREQ],
                        parity_chance=round(ch_p, 4), parity_n_novel=rc["n"],
                        parity_arb_gap_CONFIG=round(ra[JD_CONFIG] - ra[FREQ], 4),
                        parity_arb_gap_ORDER=round(ra[JD_ORDER] - ra[FREQ], 4)))

    # (4) DOMINANCE arena (ANTISYMMETRIC): JD_ORDER solves vs FREQ_NULL; JD_CONFIG (wrong head) fails (~freq).
    yd = target(DOMINANCE, X)
    rd = score(DOMINANCE, CLEAN, X, yd, 7, roles, ep)["strata"]["novel"]
    freq_d = rd[FREQ]
    details.update(dict(dom_JD_ORDER=rd[JD_ORDER], dom_ROLE_KEY=rd[ROLE_KEY], dom_JD_CONFIG_wrong=rd[JD_CONFIG],
                        dom_FREQ=freq_d, dom_chance=round(chance_of(DOMINANCE, yd), 4)))

    # (5) ARMS-MUST-DIFFER (META_RULE_AF): core learned arms mutually distinct.
    sc = score(PARITY, CLEAN, X, yp, 7, roles, ep)
    arms_differ = len(set(sc["sigs"].values())) == len(sc["sigs"])
    details["arms_differ_sig_count"] = len(set(sc["sigs"].values()))

    def rd_(jd, sp):
        return 1.0 if sp <= 1e-9 else (sp - jd) / sp

    checks = {
        "fhrr_homomorphism": homo_ok,
        # --- lens sanity: order lens is swap-sensitive (structural). NOTE: the raw config-swap-delta is NOT a
        #     valid head-discrimination proxy (the product lens amplifies magnitude); the LOAD-BEARING
        #     head-discrimination test is the trained-readout JD_CONFIG_fails_dominance check below. ---
        "order_lens_swap_sensitive": ord_delta > 1e-3,
        # --- discovery: each JD head solves its family ---
        "JD_CONFIG_solves_parity": rc[JD_CONFIG] >= 0.68,
        "JD_ORDER_solves_dominance": rd[JD_ORDER] >= freq_d + 0.08,
        # --- head-discrimination: WRONG head fails ---
        "JD_ORDER_fails_parity": rc[JD_ORDER] <= ch_p + 0.15,
        "JD_CONFIG_fails_dominance": rd[JD_CONFIG] <= freq_d + 0.10,
        # --- no destructive interference vs dedicated specialist (loose at reduced-epoch self-test) ---
        "parity_no_destructive_interf": rd_(rc[JD_CONFIG], rc[SYM_PROD]) <= 0.30,
        "dom_no_destructive_interf": rd_(rd[JD_ORDER], rd[ROLE_KEY]) <= 0.30,
        # --- specialists reproduce prior-arc capability at this regime (positive control, Gate D) ---
        "SYM_PROD_reproduces_parity": rc[SYM_PROD] >= 0.68,
        "ROLE_KEY_reproduces_dominance": rd[ROLE_KEY] >= freq_d + 0.05,
        # --- fairness / integrity ---
        "arena_freq_not_saturated": rc[FREQ] <= 0.80,
        "arbitrary_mustfail_fires_both_heads": (ra[JD_CONFIG] - ra[FREQ]) <= 0.10 and (ra[JD_ORDER] - ra[FREQ]) <= 0.10,
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
        m = run_measurement(seeds=(7, 13), run_mode="smoke")
        _write_metrics(m)
        _log("SMOKE " + m["verdict_msg"])
        return
    m = run_measurement(run_mode="full")
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
