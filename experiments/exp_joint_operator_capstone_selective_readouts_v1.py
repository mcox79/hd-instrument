r"""JOINT_OPERATOR_CAPSTONE_SELECTIVE_READOUTS (v1): the operator capstone. Does ONE shared content code, read by
TWO SELECTIVE readouts built from the TWO VET'd operators, solve BOTH symmetric (PARITY) AND asymmetric
(DOMINANCE) on NOVEL combos WITHOUT the cross-channel interference that left the prior joint-dual at MIDDLE?

WHY (this arc, all MEASURED@disk, no re-hunt):
  (1) exp_interaction_bilinear_wall_break_v1 (commit 29b53e63b): LEARN_SYM is the PARITY specialist
      (PARITY novel=0.9919) but a symmetric/product op provably FAILS DOMINANCE (0.4768; swap-invariant readout
      cannot represent x0>x1). A rank-1 low-rank bilinear ties elementwise on dominance.
  (2) exp_interaction_asymmetric_directed_operators_v1 (commit 290400320): TRANSITION_OP (non-commutative matrix
      chain s_i=(M_i@s_{i-1})*e[x_i]) reads DOMINANCE novel=1.0000, ORDER-ATTRIBUTED (std-vs-shuffled gap=0.4222,
      HARD_PASS_BRAIN_ASYMMETRIC_OP_READS_DOMINANCE_TRANSITION_OP).
  (3) exp_joint_dual_channel_readout_v1 (commit 947d8c913) landed MIDDLE: a role-keyed bundle + TWO lens readouts
      discovered BOTH (PARITY JD_CONFIG=0.8162, DOMINANCE JD_ORDER=1.0) but with CROSS-CHANNEL INTERFERENCE OVER
      TOLERANCE on the PARITY channel (rel_drop=0.1636 vs SYM_PROD 0.9758). Root of that cost: the parity signal
      was recovered through a LOSSY product-of-unbinds lens on a linearly-superposed bundle, NOT through the parity
      specialist's native op. (Its pure dual-head cost, CFG_SOLO dualhead_drop, was only 0.0288 -- the lens +
      superposition, not shared coding, carried the interference.)
  (4) rank drill (notes/research_rank_vs_dimensionality_brain_check_2026-07-15.md, P_deflated 0.42): the SYM
      rank-1-diagonal readout degrades with interaction rank (0.975->0.693 rank1->rank4); the cheap CP-identity fix
      is a LEARNED rank-R bilinear (R in {2,4,8}), NOT blind expansion. So the symmetric/config readout = learned
      rank-R (defaults R=4; ablation sweeps R and a higher-rank symmetric COUNT target).

THE JOINT CODE (brain design: Bernardi/Fusi/Salzman 2020 -- one shared mixed-selectivity population, DIFFERENT
  selective linear readouts extract DIFFERENT task variables). Here the SHARED code is a single REAL content table
  emb (L,D). BOTH validated operators read that SAME emb through their OWN native composition:
    CONFIG readout (symmetric, for PARITY): z_sym = prod_i emb[x_i]  (commutative product fold == LEARN_SYM);
      feats = [ z_sym ,  rank-R CP quad terms (z_sym@A_r)(z_sym@B_r) ] -> linear head. The LINEAR z_sym carries the
      product SIGN (= parity); the rank-R quad terms add higher-order symmetric capacity (a pure quadratic is
      sign-blind, so the linear term is retained -- design-critical). Provably swap-invariant -> structurally
      cannot read DOMINANCE (head-discrimination is GUARANTEED in this direction).
    ORDER readout (asymmetric, for DOMINANCE): s = TRANSITION chain on the SAME emb (M init ~ I; at init the chain
      == prod_i emb[x_i] EXACTLY == CONFIG's z_sym) -> linear head. Non-commutative once M leaves I.
  The two readouts are trained JOINTLY on DIFFERENT targets (config->parity, order->dominance) over the SAME X and
  the SAME shared emb -> the ONLY interference channel is the shared content code (both ops are native/lossless on
  emb -- no unbind lens, no superposition). HYPOTHESIS: this removes the prior MIDDLE's interference source and the
  parity channel lands within tolerance of its specialist. If interference persists anyway, the joint-dual MIDDLE
  stands and the both-solver still costs.

ARMS (glass-box CPU; NO LLM at measurement):
  JOINT_CONFIG   config readout (rank-R) on the SHARED emb -> parity.
  JOINT_ORDER    transition readout on the SHARED emb -> dominance.
  JOINT_ORDER_SHUF  joint order readout, slot-order deranged at TEST time only (order attribution on the joint code).
  SYM_RANKR_SPEC parity specialist: DEDICATED emb + the SAME config rank-R readout, parity only (interference ref).
  TRANSITION_SPEC dominance specialist: DEDICATED emb + M + linear, dominance only (interference ref) + its shuffle.
  HEADDISC_CONFIG_ON_DOM  linear probe of CONFIG features -> dominance (must ~freq; structural swap-invariance).
  HEADDISC_ORDER_ON_PAR   linear probe of ORDER features -> parity   (must ~chance; MEASURED, not assumed).
  RANK sweep (reported): config readout R in {1,2,4,8} on PARITY and on COUNT (# top-half bits, symmetric 5-class).
  Baselines per family/regime: FREQ_NULL=max(HOMOPHILY_COND,POP); MEMORIZE; POP; ORACLE (ceiling).
MUST-FAILS (per claim direction): ARBITRARY (random class per unique combo) + SHUFFLE (label permutation) planted on
  BOTH parity and dominance labels. Neither joint readout may beat its FREQ_NULL on these NOVEL sets (gap<=TOL).
Determinism: all RNG seeds from INTEGER indices + fixed generators; NEVER the salted builtin hasher / list(set()).

PRE-REGISTERED BANDS (fixed BEFORE running; full rationale in the prereg .md). NOVEL CLEAN, multi-seed mean:
  HARD_PASS_JOINT_OPERATOR_CAPSTONE = ALL of:
    G1 parity_solved:   JOINT_CONFIG(parity) >= 0.88                     (near SYM spec ~0.99; clears prior 0.816)
    G2 dom_solved:      JOINT_ORDER(dom)    >= 0.90 AND >= FREQ_dom+0.10  (near 1.0; FREQ_dom~0.778)
    G3 parity_no_interf:parity_rel_drop_vs_SYM_RANKR_SPEC   <= 0.10       (BEATS prior joint-dual 0.164 / 0.15 tol)
    G4 dom_no_interf:   dom_rel_drop_vs_TRANSITION_SPEC      <= 0.10
    G5 config_headdisc: HEADDISC_CONFIG_ON_DOM <= FREQ_dom + 0.07         (wrong readout fails dominance; structural)
    G6 order_headdisc:  HEADDISC_ORDER_ON_PAR  <= chance_p + 0.15         (wrong readout fails parity; MEASURED)
    G7 order_attributed:JOINT_ORDER - JOINT_ORDER_SHUF >= 0.20            (order non-commutativity is load-bearing)
    G8 mustfails fire on BOTH readouts (arb_gap<=0.10 AND shuf_gap<=0.10 for both channels); G9 oracle ceiling ok.
  MIDDLE_BAND = both solved + head-disc clean + order attributed, but interference on EITHER channel in (0.10,0.30]
    (the both-solver still costs; joint-dual MIDDLE stands but is IMPROVED-not-beaten). Reported per-channel.
  REFUTE = a channel dead (JOINT_CONFIG(parity)<=0.60 OR JOINT_ORDER(dom)<=FREQ_dom) OR interference>0.30 on either
    OR head-disc fails hard (HEADDISC_CONFIG_ON_DOM>FREQ_dom+0.15 OR HEADDISC_ORDER_ON_PAR>chance_p+0.25) OR order
    NOT attributed (gap<0.05) OR mustfail breach.
  RANK ablation (REPORTED, NOT gating HARD_PASS): rank_recovers_count = COUNT_acc(R=8) - COUNT_acc(R=1) >= 0.05
    (higher R recovers a higher-rank symmetric target); parity is expected ~flat in R (product sign is rank-1 in z).

HONEST FRAMING: this tests the ENGINEERING claim (can two native validated operators share one content code and
  each stay near its specialist), not the neuroscience locus. CONSTRUCTION note: at init both readouts read the same
  product fold; the self-test asserts that identity + the swap-invariance of the config channel.

Glass-box CPU. Default invocation (no flag) = FULL run to completion (runner calls `python -u <script>`).
ASCII-only. No bare except; except SystemExit before except Exception. Atomic metrics write. flush=True progress.
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
# Used ONLY in the construction-sanity self-test (parity via the real substrate bind fold). The joint operators
# themselves are REAL-valued torch (product fold + non-commutative matmul chain), matching the two VET'd cells.
# Import the long-stable `bind` only (present on both local + remote runner); no newer siblings (remote drift).

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline (defense in depth)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "joint_operator_capstone_selective_readouts_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ---- arena (VERBATIM from the VET-clean discovery/bilinear/transition arena) ----
K = 4               # constituents
L = 4               # ordinal levels per constituent (0..3)
N_ENT = 220         # sampled entities (combo space L^K = 256)
QUERY_FRAC = 0.45

# ---- families / regimes ----
PARITY = "PARITY"; DOMINANCE = "DOMINANCE"; COUNT = "COUNT"
CLEAN = "CLEAN"; ARBITRARY = "ARBITRARY"; SHUFFLE = "SHUFFLE"
REGIMES = [CLEAN, ARBITRARY, SHUFFLE]
NCLASS = {PARITY: 2, DOMINANCE: 2, COUNT: K + 1}
# Deterministic integer indices for RNG seeding (NEVER the salted builtin hasher; PROT-023 static scan).
FAM_IDX = {PARITY: 0, DOMINANCE: 1, COUNT: 2}
REG_IDX = {r: i for i, r in enumerate(REGIMES)}

# ---- arm names ----
JOINT_CONFIG = "JOINT_CONFIG"; JOINT_ORDER = "JOINT_ORDER"; JOINT_ORDER_SHUF = "JOINT_ORDER_SHUF"
SYM_SPEC = "SYM_RANKR_SPEC"; TRANS_SPEC = "TRANSITION_SPEC"; TRANS_SPEC_SHUF = "TRANSITION_SPEC_SHUF"
HD_CONFIG_ON_DOM = "HEADDISC_CONFIG_ON_DOM"; HD_ORDER_ON_PAR = "HEADDISC_ORDER_ON_PAR"
HOM = "HOMOPHILY_COND"; MEMO = "MEMORIZE"; POP = "POP"; ORC = "ORACLE"; FREQ = "FREQ_NULL"

# ---- mechanism hyperparams (fixed BEFORE running; MATCH the two VET'd operator cells for comparability) ----
EMB_D = 48
EPOCHS = 500
LR = 0.05
RANK_R = 4                 # config CP rank-R (safety margin per rank drill); ablation sweeps RANK_SWEEP
RANK_SWEEP = (1, 2, 4, 8)
TRANS_INIT_NOISE = 0.05    # M init = I + this*randn -> at init the chain == the config product fold EXACTLY
TRANS_REG = 1.0e-5         # tiny L2 on M: numerical stability only (NOT regularized toward identity); calib=default
PROBE_EPOCHS = 400         # head-disc linear probe fit epochs (light)

# ---- pre-registered bands (fixed before running) ----
HP_PARITY_FLOOR = 0.88         # G1
HP_DOM_FLOOR = 0.90            # G2 (also must clear FREQ_dom + margin)
DOM_FREQ_MARGIN = 0.10         # G2
INTERFERENCE_REL_TOL = 0.10    # G3/G4 HARD_PASS interference (BEATS prior joint-dual 0.164 / its 0.15 tol)
MIDDLE_INTERFERENCE_REL = 0.30 # MIDDLE upper bound; > this => REFUTE (destructive)
HEADDISC_DOM_MARGIN = 0.07     # G5 config->dom <= FREQ_dom + this
HEADDISC_PAR_MARGIN = 0.15     # G6 order->par  <= chance_p + this
REFUTE_HEADDISC_DOM = 0.15     # config->dom > FREQ_dom + this => channels not separable
REFUTE_HEADDISC_PAR = 0.25     # order->par  > chance_p + this => channels not separable
ORDER_ATTR_GAP = 0.20          # G7 JOINT_ORDER - JOINT_ORDER_SHUF >= this
REFUTE_ORDER_ATTR = 0.05       # order gap < this => order not load-bearing (refute)
REFUTE_PARITY_FLOOR = 0.60     # JOINT_CONFIG(parity) <= this => config channel dead
MUSTFAIL_TOL = 0.10            # joint readout - FREQ_NULL on ARBITRARY/SHUFFLE novel must be <= this
RANK_RECOVER_MARGIN = 0.05     # reported: COUNT_acc(R=8) - COUNT_acc(R=1) >= this => higher R recovers higher rank

EXPECTED_N_UNITS = len(REGIMES)  # joint runs per seed (one dual-target run per regime); cardinality sanity


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return str(x)


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


def chance_of(nclass, y_all):
    c = np.bincount(y_all, minlength=nclass).astype(np.float64)
    return float(c.max() / max(1.0, c.sum()))


def _write_start_marker(expected_units, run_mode):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_units, host=platform.node())
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
    if family == DOMINANCE:
        return (X[:, 0] > X[:, 1]).astype(np.int64)
    if family == COUNT:
        return bits.sum(1).astype(np.int64)     # # top-half bits: symmetric, higher-order (K+1 classes)
    raise ValueError(family)


def plant_regime(X, y_clean, family, regime, seed):
    """Returns (y_used, y_oracle). ARBITRARY/SHUFFLE are must-fail controls (deterministic)."""
    n = X.shape[0]
    nc = NCLASS[family]
    rng = np.random.default_rng(seed * 100057 + FAM_IDX[family] * 131 + REG_IDX[regime] * 17)
    if regime == CLEAN:
        return y_clean.copy(), y_clean.copy()
    if regime == ARBITRARY:
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


def _fixed_derangement(k, seed):
    """No-fixed-point permutation of slot indices (deterministic; maximal order change)."""
    rng = np.random.default_rng(seed * 100103 + 3)
    base = np.arange(k); perm = base.copy()
    for _ in range(1000):
        rng.shuffle(perm)
        if not np.any(perm == base):
            return perm.tolist()
    return list(reversed(range(k)))


# ===========================================================================
# OPERATOR PRIMITIVES (REAL torch; identical algebra to the two VET'd cells)
# ===========================================================================

def _product_fold(emb, Xi):
    """emb (L,D); Xi (n,K) long. Symmetric commutative product fold prod_i emb[x_i] -> (n,D). == LEARN_SYM z."""
    return emb[Xi].prod(dim=1)


def _transition_fold(emb, M, Xi, order):
    """emb (L,D); M (K,D,D); Xi (n,K); order = slot-index list. s_0=e[order0]; s_i=(M_i@s)*e[order_i] -> (n,D).
    Non-commutative once M leaves I; at M=I reduces EXACTLY to _product_fold (order-invariant). (TEM g=f(W_a,g).)"""
    e = emb[Xi]                                   # (n,K,D)
    s = e[:, order[0], :]
    for j in range(1, len(order)):
        s = torch.matmul(s, M[j].t()) * e[:, order[j], :]
    return s


def _config_feats(z, A, B):
    """CONFIG readout features: linear product-fold z (carries parity SIGN) + rank-R CP quad terms (sign-blind).
    z (n,D); A,B (D,R). Returns (n, D+R)."""
    q = (z @ A) * (z @ B)                         # (n,R) rank-R CP quad (sum-of-rank-1 bilinear terms)
    return torch.cat([z, q], dim=1)


def _norm_fit(feat):
    mu = feat.mean(0, keepdim=True); sd = feat.std(0, keepdim=True) + 1e-3
    return mu, sd


# ===========================================================================
# JOINT model: ONE shared emb; CONFIG readout (rank-R) -> parity; ORDER readout (transition) -> dominance.
# Trained JOINTLY on the two DIFFERENT targets. Returns preds + features (for head-disc probes) + order-shuffle.
# ===========================================================================

def _train_joint(Xtr, y_par_tr, y_dom_tr, Xq, seed, rank=RANK_R, epochs=EPOCHS):
    g = torch.Generator().manual_seed(seed * 7919 + 101)
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    ypt = torch.from_numpy(y_par_tr).long(); ydt = torch.from_numpy(y_dom_tr).long()
    D = EMB_D; k = Xtr.shape[1]
    emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, D, generator=g))                    # SHARED content code
    eye = torch.eye(D).unsqueeze(0).repeat(k, 1, 1)
    M = torch.nn.Parameter(eye + TRANS_INIT_NOISE * torch.randn(k, D, D, generator=g))      # transition matrices
    A = torch.nn.Parameter(0.1 * torch.randn(D, rank, generator=g))                         # config CP factors
    B = torch.nn.Parameter(0.1 * torch.randn(D, rank, generator=g))
    Wc = torch.nn.Parameter(0.1 * torch.randn(D + rank, NCLASS[PARITY], generator=g)); bc = torch.nn.Parameter(torch.zeros(NCLASS[PARITY]))
    Wo = torch.nn.Parameter(0.1 * torch.randn(D, NCLASS[DOMINANCE], generator=g)); bo = torch.nn.Parameter(torch.zeros(NCLASS[DOMINANCE]))
    opt = torch.optim.Adam([emb, M, A, B, Wc, bc, Wo, bo], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    std_order = list(range(k))

    for _ in range(epochs):
        opt.zero_grad()
        z = _product_fold(emb, Xt)
        fc = _config_feats(z, A, B)
        s = _transition_fold(emb, M, Xt, std_order)
        mc, sc = _norm_fit(fc); mo, so = _norm_fit(s)
        lc = ((fc - mc) / sc) @ Wc + bc
        lo = ((s - mo) / so) @ Wo + bo
        loss = lossf(lc, ypt) + lossf(lo, ydt) + TRANS_REG * M.pow(2).sum()
        loss.backward()
        opt.step()

    with torch.no_grad():
        z_tr = _product_fold(emb, Xt); fc_tr = _config_feats(z_tr, A, B)
        s_tr = _transition_fold(emb, M, Xt, std_order)
        mc, sc = _norm_fit(fc_tr); mo, so = _norm_fit(s_tr)
        z_q = _product_fold(emb, Xu); fc_q = _config_feats(z_q, A, B)
        s_q = _transition_fold(emb, M, Xu, std_order)
        cfg_par_pred = torch.argmax(((fc_q - mc) / sc) @ Wc + bc, 1).numpy().astype(np.int64)
        ord_dom_pred = torch.argmax(((s_q - mo) / so) @ Wo + bo, 1).numpy().astype(np.int64)
        perm = _fixed_derangement(k, seed)
        s_qs = _transition_fold(emb, M, Xu, perm)
        ord_dom_pred_shuf = torch.argmax(((s_qs - mo) / so) @ Wo + bo, 1).numpy().astype(np.int64)
        # raw (unnormalized) features for head-disc probes (probe refits its own normalization)
        feats = dict(cfg_tr=fc_tr.numpy(), cfg_q=fc_q.numpy(), ord_tr=s_tr.numpy(), ord_q=s_q.numpy())
    return dict(cfg_par_pred=cfg_par_pred, ord_dom_pred=ord_dom_pred, ord_dom_pred_shuf=ord_dom_pred_shuf,
                feats=feats)


def _train_config_solo(Xtr, y_tr, Xq, nclass, seed, rank=RANK_R, epochs=EPOCHS):
    """DEDICATED emb + config rank-R readout, single target. Parity specialist (interference ref) + rank sweep."""
    g = torch.Generator().manual_seed(seed * 7919 + 211 + rank * 13 + nclass * 3)
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(y_tr).long()
    D = EMB_D
    emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, D, generator=g))
    A = torch.nn.Parameter(0.1 * torch.randn(D, rank, generator=g))
    B = torch.nn.Parameter(0.1 * torch.randn(D, rank, generator=g))
    W = torch.nn.Parameter(0.1 * torch.randn(D + rank, nclass, generator=g)); b = torch.nn.Parameter(torch.zeros(nclass))
    opt = torch.optim.Adam([emb, A, B, W, b], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    for _ in range(epochs):
        opt.zero_grad()
        f = _config_feats(_product_fold(emb, Xt), A, B)
        mu, sd = _norm_fit(f)
        loss = lossf(((f - mu) / sd) @ W + b, yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        f_tr = _config_feats(_product_fold(emb, Xt), A, B); mu, sd = _norm_fit(f_tr)
        f_q = _config_feats(_product_fold(emb, Xu), A, B)
        pred = torch.argmax(((f_q - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
    return pred


def _train_transition_solo(Xtr, y_tr, Xq, nclass, seed, epochs=EPOCHS):
    """DEDICATED emb + M + linear, single target. Dominance specialist (interference ref) + test-time shuffle."""
    g = torch.Generator().manual_seed(seed * 7919 + 311)
    Xt = torch.from_numpy(Xtr).long(); Xu = torch.from_numpy(Xq).long()
    yt = torch.from_numpy(y_tr).long()
    D = EMB_D; k = Xtr.shape[1]
    emb = torch.nn.Parameter(1.0 + 0.2 * torch.randn(L, D, generator=g))
    eye = torch.eye(D).unsqueeze(0).repeat(k, 1, 1)
    M = torch.nn.Parameter(eye + TRANS_INIT_NOISE * torch.randn(k, D, D, generator=g))
    W = torch.nn.Parameter(0.1 * torch.randn(D, nclass, generator=g)); b = torch.nn.Parameter(torch.zeros(nclass))
    opt = torch.optim.Adam([emb, M, W, b], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    std_order = list(range(k))
    for _ in range(epochs):
        opt.zero_grad()
        h = _transition_fold(emb, M, Xt, std_order)
        mu, sd = _norm_fit(h)
        loss = lossf(((h - mu) / sd) @ W + b, yt) + TRANS_REG * M.pow(2).sum()
        loss.backward()
        opt.step()
    with torch.no_grad():
        h_tr = _transition_fold(emb, M, Xt, std_order); mu, sd = _norm_fit(h_tr)
        h_q = _transition_fold(emb, M, Xu, std_order)
        pred = torch.argmax(((h_q - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
        perm = _fixed_derangement(k, seed)
        h_qs = _transition_fold(emb, M, Xu, perm)
        pred_shuf = torch.argmax(((h_qs - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
    return pred, pred_shuf


def _fit_linear_probe(feat_tr, y_tr, feat_q, nclass, seed, epochs=PROBE_EPOCHS):
    """Light linear (logistic) probe: can this feature space linearly decode the (WRONG-channel) target? Fresh head."""
    g = torch.Generator().manual_seed(seed * 7919 + 409 + nclass)
    ft = torch.from_numpy(np.asarray(feat_tr, dtype=np.float32))
    fq = torch.from_numpy(np.asarray(feat_q, dtype=np.float32))
    yt = torch.from_numpy(np.asarray(y_tr, dtype=np.int64))
    mu = ft.mean(0, keepdim=True); sd = ft.std(0, keepdim=True) + 1e-3
    W = torch.nn.Parameter(0.1 * torch.randn(ft.shape[1], nclass, generator=g)); b = torch.nn.Parameter(torch.zeros(nclass))
    opt = torch.optim.Adam([W, b], lr=0.05)
    lossf = torch.nn.CrossEntropyLoss()
    ftn = (ft - mu) / sd
    for _ in range(epochs):
        opt.zero_grad()
        loss = lossf(ftn @ W + b, yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        pred = torch.argmax(((fq - mu) / sd) @ W + b, 1).numpy().astype(np.int64)
    return pred


# ===========================================================================
# baselines -- REUSED VERBATIM (per-family freq null)
# ===========================================================================

def arm_homophily(nclass, Xtr, ytr, Xq):
    per = [defaultdict(lambda: np.zeros(nclass)) for _ in range(Xtr.shape[1])]
    for r in range(Xtr.shape[0]):
        for i in range(Xtr.shape[1]):
            per[i][int(Xtr[r, i])][int(ytr[r])] += 1.0
    marg = np.bincount(ytr, minlength=nclass).astype(np.float64)
    preds = []
    for qq in range(Xq.shape[0]):
        sc = np.zeros(nclass)
        for i in range(Xq.shape[1]):
            sc = sc + per[i].get(int(Xq[qq, i]), np.zeros(nclass))
        if sc.sum() <= 0:
            sc = marg
        preds.append(int(np.argmax(sc)))
    return np.array(preds, dtype=np.int64)


def arm_memorize(nclass, Xtr, ytr, Xq, pop_label):
    combo = defaultdict(lambda: defaultdict(int))
    for r in range(Xtr.shape[0]):
        combo[tuple(Xtr[r].tolist())][int(ytr[r])] += 1
    preds = []
    for qq in range(Xq.shape[0]):
        dd = combo.get(tuple(Xq[qq].tolist()))
        preds.append(max(dd.items(), key=lambda kv: kv[1])[0] if dd else pop_label)
    return np.array(preds, dtype=np.int64)


def acc(pred, gold):
    if pred is None or len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


def _freq_null(nclass, Xtr, ytr, Xq, gold, m):
    pop_label = int(np.argmax(np.bincount(ytr, minlength=nclass)))
    hom = arm_homophily(nclass, Xtr, ytr, Xq)
    pop = np.full(Xq.shape[0], pop_label, dtype=np.int64)
    hom_a = acc(hom[m], gold[m]) if m.sum() > 0 else float("nan")
    pop_a = acc(pop[m], gold[m]) if m.sum() > 0 else float("nan")
    return float(max(hom_a, pop_a)), pop_label


# ===========================================================================
# per-seed measurement (dual-target joint run per regime; specialists + head-disc + rank sweep on CLEAN)
# ===========================================================================

def score_seed(X, seed, do_extras, epochs=EPOCHS):
    q, tr, novel = split_novel(X, seed)
    Xq, Xtr = X[q], X[tr]
    yp_clean = target(PARITY, X); yd_clean = target(DOMINANCE, X)

    out = {"regimes": {}, "n_novel": int(novel.sum()), "n_query": int(len(q))}

    for reg in REGIMES:
        yp_used, _ = plant_regime(X, yp_clean, PARITY, reg, seed)
        yd_used, _ = plant_regime(X, yd_clean, DOMINANCE, reg, seed)
        yp_tr, yp_q = yp_used[tr], yp_used[q]
        yd_tr, yd_q = yd_used[tr], yd_used[q]
        j = _train_joint(Xtr, yp_tr, yd_tr, Xq, seed, RANK_R, epochs)

        cfg_par_novel = acc(j["cfg_par_pred"][novel], yp_q[novel])
        ord_dom_novel = acc(j["ord_dom_pred"][novel], yd_q[novel])
        freq_par, _ = _freq_null(NCLASS[PARITY], Xtr, yp_tr, Xq, yp_q, novel)
        freq_dom, _ = _freq_null(NCLASS[DOMINANCE], Xtr, yd_tr, Xq, yd_q, novel)
        rd = dict(cfg_par=round(cfg_par_novel, 5), ord_dom=round(ord_dom_novel, 5),
                  freq_par=round(freq_par, 5), freq_dom=round(freq_dom, 5),
                  cfg_par_gap=round(cfg_par_novel - freq_par, 5), ord_dom_gap=round(ord_dom_novel - freq_dom, 5))
        if reg == CLEAN:
            rd["ord_dom_shuf"] = round(acc(j["ord_dom_pred_shuf"][novel], yd_q[novel]), 5)
        out["regimes"][reg] = rd

    if do_extras:
        # ---- CLEAN dual-target features for head-disc (from the CLEAN joint model) ----
        yp_tr, yp_q = yp_clean[tr], yp_clean[q]
        yd_tr, yd_q = yd_clean[tr], yd_clean[q]
        jc = _train_joint(Xtr, yp_tr, yd_tr, Xq, seed, RANK_R, epochs)
        # config features -> DOMINANCE (must fail; swap-invariant); order features -> PARITY (measured)
        hd_cfg_dom = _fit_linear_probe(jc["feats"]["cfg_tr"], yd_tr, jc["feats"]["cfg_q"], NCLASS[DOMINANCE], seed)
        hd_ord_par = _fit_linear_probe(jc["feats"]["ord_tr"], yp_tr, jc["feats"]["ord_q"], NCLASS[PARITY], seed)
        out["headdisc_config_on_dom_novel"] = round(acc(hd_cfg_dom[novel], yd_q[novel]), 5)
        out["headdisc_order_on_par_novel"] = round(acc(hd_ord_par[novel], yp_q[novel]), 5)

        # ---- specialists (dedicated emb; interference references) ----
        sym_par = _train_config_solo(Xtr, yp_tr, Xq, NCLASS[PARITY], seed, RANK_R, epochs)
        trans_dom, trans_dom_shuf = _train_transition_solo(Xtr, yd_tr, Xq, NCLASS[DOMINANCE], seed, epochs)
        out["sym_spec_par_novel"] = round(acc(sym_par[novel], yp_q[novel]), 5)
        out["trans_spec_dom_novel"] = round(acc(trans_dom[novel], yd_q[novel]), 5)
        out["trans_spec_dom_shuf_novel"] = round(acc(trans_dom_shuf[novel], yd_q[novel]), 5)

        # ---- rank sweep (reported): config R in RANK_SWEEP on PARITY and COUNT ----
        yc_clean = target(COUNT, X); yc_tr, yc_q = yc_clean[tr], yc_clean[q]
        rank_par = {}; rank_cnt = {}
        for R in RANK_SWEEP:
            pp = _train_config_solo(Xtr, yp_tr, Xq, NCLASS[PARITY], seed, R, epochs)
            cc = _train_config_solo(Xtr, yc_tr, Xq, NCLASS[COUNT], seed, R, epochs)
            rank_par[str(R)] = round(acc(pp[novel], yp_q[novel]), 5)
            rank_cnt[str(R)] = round(acc(cc[novel], yc_q[novel]), 5)
        out["rank_sweep_parity"] = rank_par
        out["rank_sweep_count"] = rank_cnt

        # ---- ARMS-MUST-DIFFER (META_RULE_AF). STRICT set = the two JOINT readouts (read DIFFERENT targets off the
        # SAME shared code -> bit-identical would be an impl bug). EXEMPTED (declared): (JOINT_ORDER, TRANS_SPEC) and
        # (JOINT_CONFIG, SYM_SPEC) -- a specialist legitimately equals the joint readout when the family is solved to
        # the oracle (perfect dominance preds == gold == identical vectors); that coincidence is the intended result.
        out["sigs"] = {JOINT_CONFIG: _sig(jc["cfg_par_pred"]), JOINT_ORDER: _sig(jc["ord_dom_pred"])}
        out["sigs_reported"] = {SYM_SPEC: _sig(sym_par), TRANS_SPEC: _sig(trans_dom)}
    return out


# ===========================================================================
# full measurement
# ===========================================================================

def run_measurement(seeds=(7, 13, 17, 23, 29), run_mode="full", epochs=EPOCHS):
    total = EXPECTED_N_UNITS * len(seeds)
    _write_start_marker(total, run_mode)
    _log("%s run: %d seeds x %d regimes, arena K=%d L=%d N=%d D=%d epochs=%d rank_R=%d"
         % (run_mode, len(seeds), len(REGIMES), K, L, N_ENT, EMB_D, epochs, RANK_R))
    per = []
    ch_par = chance_of(NCLASS[PARITY], target(PARITY, make_X(seeds[0])))
    ch_dom = chance_of(NCLASS[DOMINANCE], target(DOMINANCE, make_X(seeds[0])))
    t0 = time.perf_counter()
    n_units = 0
    for si, sd in enumerate(seeds):
        X = make_X(sd)
        s = score_seed(X, sd, do_extras=True, epochs=epochs)
        per.append(s)
        n_units += EXPECTED_N_UNITS
        _heartbeat(n_units, total, time.perf_counter() - t0, extra={"seed": sd})
        _log("  seed %d/%d done (units=%d/%d elapsed=%.1fs)" % (si + 1, len(seeds), n_units, total, time.perf_counter() - t0))
    cardinality_ok = bool(n_units == total)

    def mean_over(key_fn):
        vals = [key_fn(s) for s in per]
        vals = [v for v in vals if v is not None and v == v]
        return float(np.mean(vals)) if vals else float("nan")

    # headline (NOVEL CLEAN, multi-seed mean)
    cfg_par = mean_over(lambda s: s["regimes"][CLEAN]["cfg_par"])
    ord_dom = mean_over(lambda s: s["regimes"][CLEAN]["ord_dom"])
    ord_dom_shuf = mean_over(lambda s: s["regimes"][CLEAN]["ord_dom_shuf"])
    freq_par = mean_over(lambda s: s["regimes"][CLEAN]["freq_par"])
    freq_dom = mean_over(lambda s: s["regimes"][CLEAN]["freq_dom"])
    sym_spec = mean_over(lambda s: s["sym_spec_par_novel"])
    trans_spec = mean_over(lambda s: s["trans_spec_dom_novel"])
    trans_spec_shuf = mean_over(lambda s: s["trans_spec_dom_shuf_novel"])
    hd_cfg_dom = mean_over(lambda s: s["headdisc_config_on_dom_novel"])
    hd_ord_par = mean_over(lambda s: s["headdisc_order_on_par_novel"])

    def rel_drop(joint_v, spec_v):
        return 0.0 if (spec_v is None or spec_v != spec_v or spec_v <= 1e-9) else float((spec_v - joint_v) / spec_v)
    parity_rel_drop = rel_drop(cfg_par, sym_spec)
    dom_rel_drop = rel_drop(ord_dom, trans_spec)

    # rank sweep means
    rank_par = {str(R): mean_over(lambda s, R=R: s["rank_sweep_parity"][str(R)]) for R in RANK_SWEEP}
    rank_cnt = {str(R): mean_over(lambda s, R=R: s["rank_sweep_count"][str(R)]) for R in RANK_SWEEP}
    rank_recover_count = float(rank_cnt[str(RANK_SWEEP[-1])] - rank_cnt[str(RANK_SWEEP[0])])
    rank_recover_par = float(rank_par[str(RANK_SWEEP[-1])] - rank_par[str(RANK_SWEEP[0])])
    rank_recovers = bool(rank_recover_count >= RANK_RECOVER_MARGIN)

    # must-fails (both readouts, both must-fail regimes)
    def mf_gap(reg, key):
        return mean_over(lambda s: s["regimes"][reg][key])
    mustfail_ok = True
    mf = {}
    for reg in (ARBITRARY, SHUFFLE):
        gp = mf_gap(reg, "cfg_par_gap"); gd = mf_gap(reg, "ord_dom_gap")
        mf["%s_cfg_gap" % reg] = round(gp, 5); mf["%s_ord_gap" % reg] = round(gd, 5)
        if not (gp <= MUSTFAIL_TOL and gd <= MUSTFAIL_TOL):
            mustfail_ok = False

    ceiling_ok = bool(cfg_par <= 1.0 + 1e-6 and ord_dom <= 1.0 + 1e-6)  # oracle = 1.0 on CLEAN by construction

    # ---- gates ----
    parity_solved = bool(cfg_par >= HP_PARITY_FLOOR)                                     # G1
    dom_solved = bool(ord_dom >= HP_DOM_FLOOR and (ord_dom - freq_dom) >= DOM_FREQ_MARGIN)  # G2
    parity_no_interf = bool(parity_rel_drop <= INTERFERENCE_REL_TOL)                     # G3
    dom_no_interf = bool(dom_rel_drop <= INTERFERENCE_REL_TOL)                           # G4
    config_headdisc = bool(hd_cfg_dom <= freq_dom + HEADDISC_DOM_MARGIN)                 # G5
    order_headdisc = bool(hd_ord_par <= ch_par + HEADDISC_PAR_MARGIN)                    # G6
    order_attributed = bool((ord_dom - ord_dom_shuf) >= ORDER_ATTR_GAP)                  # G7
    # G8 mustfail_ok, G9 ceiling_ok

    hard_pass = bool(parity_solved and dom_solved and parity_no_interf and dom_no_interf
                     and config_headdisc and order_headdisc and order_attributed and mustfail_ok and ceiling_ok)

    refute_dead = bool(cfg_par <= REFUTE_PARITY_FLOOR or ord_dom <= freq_dom)
    refute_interf = bool(parity_rel_drop > MIDDLE_INTERFERENCE_REL or dom_rel_drop > MIDDLE_INTERFERENCE_REL)
    refute_hd = bool(hd_cfg_dom > freq_dom + REFUTE_HEADDISC_DOM or hd_ord_par > ch_par + REFUTE_HEADDISC_PAR)
    refute_order = bool((ord_dom - ord_dom_shuf) < REFUTE_ORDER_ATTR)
    refute = bool(refute_dead or refute_interf or refute_hd or refute_order or (not mustfail_ok))

    if hard_pass:
        verdict = "HARD_PASS_JOINT_OPERATOR_CAPSTONE_BOTH_SOLVED_NO_INTERFERENCE_HEADDISC_CLEAN"
    elif refute:
        tags = []
        if refute_dead:
            tags.append("CHANNEL_DEAD")
        if refute_interf:
            tags.append("DESTRUCTIVE_INTERFERENCE")
        if refute_hd:
            tags.append("HEADS_NOT_SEPARABLE")
        if refute_order:
            tags.append("ORDER_NOT_LOAD_BEARING")
        if not mustfail_ok:
            tags.append("MUSTFAIL_BREACH")
        verdict = "REFUTE_" + "_".join(tags)
    else:
        both = parity_solved and dom_solved
        hd_clean = config_headdisc and order_headdisc
        if both and hd_clean and order_attributed:
            verdict = "MIDDLE_BOTH_SOLVED_HEADDISC_CLEAN_INTERFERENCE_OVER_TOL"
        elif parity_solved and not dom_solved:
            verdict = "PARTIAL_CONFIG_ONLY_PARITY"
        elif dom_solved and not parity_solved:
            verdict = "PARTIAL_ORDER_ONLY_DOMINANCE"
        else:
            verdict = "MIDDLE_BAND"

    msg = ("%s || PARITY(ch=%.2f): JOINT_CONFIG=%s SYM_SPEC=%s (rel_drop=%s no_interf=%s) HEADDISC_ord_on_par=%s | "
           "DOMINANCE(freq=%s): JOINT_ORDER=%s TRANS_SPEC=%s (rel_drop=%s no_interf=%s) SHUF=%s (attr_gap=%s) "
           "HEADDISC_cfg_on_dom=%s | gates[G1par=%s G2dom=%s G3parI=%s G4domI=%s G5cfgHD=%s G6ordHD=%s G7attr=%s "
           "G8mf=%s G9ceil=%s] | RANK count R1=%s R8=%s (recover=%s) parity R1=%s R8=%s | card=%s"
           % (verdict, ch_par, _fmt(cfg_par), _fmt(sym_spec), _fmt(parity_rel_drop), parity_no_interf, _fmt(hd_ord_par),
              _fmt(freq_dom), _fmt(ord_dom), _fmt(trans_spec), _fmt(dom_rel_drop), dom_no_interf, _fmt(ord_dom_shuf),
              _fmt(ord_dom - ord_dom_shuf), _fmt(hd_cfg_dom),
              parity_solved, dom_solved, parity_no_interf, dom_no_interf, config_headdisc, order_headdisc,
              order_attributed, mustfail_ok, ceiling_ok,
              _fmt(rank_cnt[str(RANK_SWEEP[0])]), _fmt(rank_cnt[str(RANK_SWEEP[-1])]), rank_recovers,
              _fmt(rank_par[str(RANK_SWEEP[0])]), _fmt(rank_par[str(RANK_SWEEP[-1])]), cardinality_ok))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode=run_mode,
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        arena=dict(K=K, L=L, N_ENT=N_ENT, query_frac=QUERY_FRAC), seeds=list(seeds),
        emb_d=EMB_D, epochs=epochs, lr=LR, rank_r=RANK_R, rank_sweep_values=list(RANK_SWEEP),
        chance_parity=round(ch_par, 5), chance_dominance=round(ch_dom, 5),
        headline=dict(cfg_par=round(cfg_par, 5), ord_dom=round(ord_dom, 5), ord_dom_shuf=round(ord_dom_shuf, 5),
                      freq_par=round(freq_par, 5), freq_dom=round(freq_dom, 5),
                      sym_spec_par=round(sym_spec, 5), trans_spec_dom=round(trans_spec, 5),
                      trans_spec_dom_shuf=round(trans_spec_shuf, 5),
                      parity_rel_drop=round(parity_rel_drop, 5), dom_rel_drop=round(dom_rel_drop, 5),
                      headdisc_config_on_dom=round(hd_cfg_dom, 5), headdisc_order_on_par=round(hd_ord_par, 5),
                      order_attr_gap=round(ord_dom - ord_dom_shuf, 5)),
        gates=dict(hard_pass=hard_pass, refute=refute, parity_solved=parity_solved, dom_solved=dom_solved,
                   parity_no_interf=parity_no_interf, dom_no_interf=dom_no_interf,
                   config_headdisc=config_headdisc, order_headdisc=order_headdisc,
                   order_attributed=order_attributed, mustfail_ok=mustfail_ok, ceiling_ok=ceiling_ok,
                   cardinality_ok=cardinality_ok,
                   refute_dead=refute_dead, refute_interf=refute_interf, refute_hd=refute_hd, refute_order=refute_order),
        rank_sweep=dict(parity=rank_par, count=rank_cnt, recover_count=round(rank_recover_count, 5),
                        recover_parity=round(rank_recover_par, 5), rank_recovers_count=rank_recovers),
        mustfails=mf,
        bands=dict(HP_PARITY_FLOOR=HP_PARITY_FLOOR, HP_DOM_FLOOR=HP_DOM_FLOOR, DOM_FREQ_MARGIN=DOM_FREQ_MARGIN,
                   INTERFERENCE_REL_TOL=INTERFERENCE_REL_TOL, MIDDLE_INTERFERENCE_REL=MIDDLE_INTERFERENCE_REL,
                   HEADDISC_DOM_MARGIN=HEADDISC_DOM_MARGIN, HEADDISC_PAR_MARGIN=HEADDISC_PAR_MARGIN,
                   ORDER_ATTR_GAP=ORDER_ATTR_GAP, MUSTFAIL_TOL=MUSTFAIL_TOL, RANK_RECOVER_MARGIN=RANK_RECOVER_MARGIN),
        per_seed=per,
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (exercises the REAL operators + construction facts; MEASURES the open interference/head-disc question)
# ===========================================================================

def self_test():
    ok_all = True
    details = {}
    ep = 250   # reduced epochs -> fast gate; checks are DIRECTIONAL (discriminator fires), not full-precision

    # (1) REAL FHRR bind homomorphism (proves the substrate complex bind path is live).
    gnp = np.random.default_rng(31)
    m = gnp.integers(1, max(2, L), size=32).astype(np.float64)
    jj = np.arange(L, dtype=np.float64)[:, None]
    Ycode = torch.from_numpy(np.exp(1j * (2.0 * np.pi / L) * (jj * m[None, :])).astype(np.complex64))
    bound = hd_bind(Ycode[torch.tensor([1, 2])], Ycode[torch.tensor([2, 3])])
    homo_ok = torch.argmax((bound @ Ycode.conj().T.contiguous()).real, 1).tolist() == [3 % L, 5 % L]
    details["fhrr_homomorphism_ok"] = homo_ok

    # (2) CONSTRUCTION: at M=I the transition fold == the config product fold EXACTLY (shared-code identity at init).
    g = torch.Generator().manual_seed(7)
    emb = 1.0 + 0.2 * torch.randn(L, EMB_D, generator=g)
    Mi = torch.eye(EMB_D).unsqueeze(0).repeat(K, 1, 1)
    Xi = torch.tensor([[0, 2, 1, 3], [3, 1, 2, 0]])
    z_prod = _product_fold(emb, Xi)
    s_trans = _transition_fold(emb, Mi, Xi, list(range(K)))
    init_identity = bool(torch.allclose(z_prod, s_trans, atol=1e-5))
    details["transition_at_M_eye_equals_product_fold"] = init_identity

    # (3) CONSTRUCTION: config product fold is SWAP-INVARIANT (slot0<->slot1) -> structurally cannot read dominance.
    Xa = torch.tensor([[0, 2, 1, 3]]); Xb = torch.tensor([[2, 0, 1, 3]])
    swap_delta = float((_product_fold(emb, Xa) - _product_fold(emb, Xb)).abs().max().item())
    config_swap_invariant = bool(swap_delta < 1e-5)
    details["config_swap_delta_max"] = round(swap_delta, 8)

    # (4) MECHANISM MEASURE (reduced-epoch, single seed): joint solves BOTH; head-disc directions; specialists.
    X = make_X(7)
    s = score_seed(X, 7, do_extras=True, epochs=ep)
    cfg_par = s["regimes"][CLEAN]["cfg_par"]; ord_dom = s["regimes"][CLEAN]["ord_dom"]
    ord_shuf = s["regimes"][CLEAN]["ord_dom_shuf"]; freq_dom = s["regimes"][CLEAN]["freq_dom"]
    sym_spec = s["sym_spec_par_novel"]; trans_spec = s["trans_spec_dom_novel"]
    hd_cfg_dom = s["headdisc_config_on_dom_novel"]; hd_ord_par = s["headdisc_order_on_par_novel"]
    ch_par = chance_of(NCLASS[PARITY], target(PARITY, X))
    arb = s["regimes"][ARBITRARY]
    details.update(dict(cfg_par=cfg_par, ord_dom=ord_dom, ord_shuf=ord_shuf, sym_spec=sym_spec,
                        trans_spec=trans_spec, freq_dom=freq_dom, hd_cfg_dom=hd_cfg_dom, hd_ord_par=hd_ord_par,
                        n_novel=s["n_novel"], arb_cfg_gap=arb["cfg_par_gap"], arb_ord_gap=arb["ord_dom_gap"],
                        rank_count=s["rank_sweep_count"]))

    # (5) ARMS-MUST-DIFFER
    arms_differ = len(set(s["sigs"].values())) == len(s["sigs"])
    details["arms_differ_sig_count"] = len(set(s["sigs"].values()))

    checks = {
        "fhrr_homomorphism": homo_ok,
        "transition_at_M_eye_equals_product_fold": init_identity,      # shared-code identity at init (CONSTRUCTION)
        "config_swap_invariant": config_swap_invariant,               # config channel provably order-blind
        # --- both channels solve their family (discriminator fires; reduced-epoch loose floors) ---
        "joint_config_solves_parity": cfg_par >= 0.80,
        "joint_order_solves_dominance": ord_dom >= freq_dom + 0.10,
        # --- specialists reproduce prior-arc capability at this regime (positive control) ---
        "sym_spec_reproduces_parity": sym_spec >= 0.85,
        "trans_spec_reproduces_dominance": trans_spec >= 0.90,
        # --- order attribution (transition non-commutativity is load-bearing) ---
        "joint_order_attributed": (ord_dom - ord_shuf) >= 0.15,
        # --- head-discrimination: config CANNOT read dominance (structural). order->parity MEASURED (not asserted) ---
        "config_headdisc_fails_dominance": hd_cfg_dom <= freq_dom + 0.10,
        # --- fairness / integrity ---
        "arena_freq_dom_not_saturated": freq_dom <= 0.85,
        "arbitrary_mustfail_fires_both": arb["cfg_par_gap"] <= 0.10 and arb["ord_dom_gap"] <= 0.10,
        "enough_novel": s["n_novel"] >= 20,
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
        m = run_measurement(seeds=(7, 13), run_mode="smoke", epochs=300)
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
