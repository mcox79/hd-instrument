"""
exp_rank_matched_readout_tunable_plant_v1 -- CLOSE the flagged rank-R operator gap.

CONTEXT (why this cell exists):
  The joint-code VET (exp_joint_operator_capstone_selective_readouts_v1, commit a23cfd71) flagged the LEARNED
  RANK-R lever as SATURATED/UNTESTED on that arena (the count target solved already at R=1, so R was never
  exercised). The detection decider found SYM is a RANK-1 DIAGONAL readout that degrades monotonically with
  interaction rank (measured elsewhere: rank1 0.975 -> rank4 0.693). The rank-vs-dimensionality drill concluded
  the FIX = explicit LEARNED rank-R (tax-free, not blind expansion). This cell CLOSES that cleanly with a
  CONSTRUCTION-GRADE synthetic validation of the rank-matching lever, isolating the rank mechanism the noisy
  real-data dense cell could not.

WHAT IS BUILT (glass-box, deterministic, noise-free):
  A TUNABLE-INTERACTION-RANK synthetic plant. Two roles a,b each draw a fixed CONSTITUENT CODE from a vocabulary
  (phi_a, psi_b in R^m, centered so the plant carries ZERO additive/main-effect signal). The interaction target
  is a rank-R_plant BILINEAR FORM on the two codes:
        score(a,b) = phi_a^T M psi_b,   M = U_plant diag(sigma) V_plant^T, rank(M) = R_plant, sigma == 1 (EQUAL)
        y = 1[ score > median(score) ]  (balanced binary)
  EQUAL singular values are deliberate: no dominant component for a low-rank readout to hide behind, so matching
  the readout rank to R_plant is NECESSARY (Eckart-Young). R_plant in {1,2,4,8}. SEEN-vs-NOVEL held-out by pairing
  (readout reads the GIVEN code vector -> generalization is a genuine form-recovery test, not a lookup).

ARMS (readouts that read the two constituent codes):
  LEARN_RANK_R (R in {1,2,4,8,16}) low-rank bilinear pooling (Kim et al. 2016): z = (phi.U)(*)(psi.V) [R-dim],
                logits = z.W + b. Learned U,V (m x R). R=1 == the rank-1 diagonal SYM readout (the current lever).
  LEARN_BIND_DIAG the LITERAL substrate elementwise bind readout: z = phi (*) psi [m-dim], logits = z.w + b.
                "the current bind" verbatim (FHRR bind restricted to real == elementwise product; self-test ties
                it to hd_bind). Diagonal coupling; reported.
  LEARN_ADD     additive (no interaction): logits = phi.Wa + psi.Wb + b. The additive floor (~chance by design).
  ORACLE        true score thresholded at train-median -> ceiling sanity (arena separable).
  SCRAMBLE      rank-16 readout on SHUFFLED train labels -> chance on novel. MUST-FAIL.
  FREQ / POP    majority class -> chance.

THE CLAIM (measured in FULL, gated by the pre-registered bands below; NOT asserted in self-test):
  (a) DEGRADATION: rank-1 (R=1) accuracy degrades as R_plant rises (reproduce 0.97 -> ~0.6x). Perturbing R_plant
      moves rank-1 accuracy = the telemetry-sensitivity control.
  (b) RECOVERY: learned rank-R with R >= R_plant recovers to the ORACLE ceiling (matches specialist).
  (c) MONOTONE + SATURATION: accuracy rises monotonically in R up to R = R_plant then plateaus (under-rank fails,
      matching-rank recovers, over-rank R=16 does not hurt much). "Match the readout rank to the interaction rank."

  HARD_PASS = recovery(G1) AND rank-1 degradation reproduced(G2) AND monotone+saturation(G3) AND controls fire(G4).
  HARD_FAIL = rank-R does NOT recover (rank isn't the lever) OR rank-1 does NOT degrade (no rank effect).
  MIDDLE    = partial recovery / partial monotonicity.

HONEST SCOPE: synthetic construction-grade isolation of the rank mechanism. Not a real-data capability win.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; ARMS-MUST-DIFFER hash-test over readout preds)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (noise-free plant; ceiling ~1.0 via Eckart-Young; bands set below THEORETICAL predictions)
# - baseline_in_band at self-test (META_RULE_AG; baselines LEARN_ADD/FREQ in (0.05,0.95))
# - discriminator survives scale: EQUAL-sigma rank gap is m-independent for m>=R_plant (analytical) + smoke preview
# - HARD_PASS strictly above floor (recovery gap >= 0.15 vs theoretical 0.30 at R_plant=4)
# - HP_SCOPE per-arm declared in pre-reg (ceiling gates -> ORACLE; must-fail -> SCRAMBLE; recovery -> LEARN_RANK_R)
# - cardinality_ok (EXPECTED_N_UNITS = len(R_PLANT_GRID) per seed)
# - per-unit failure-class: no bare except; except Exception only; crash -> CELL_CRASHED metrics
# - calibration_check = default_ok_for_this_regime (all hyperparams fixed a priori)
# - all numbers in comments tagged THEORETICAL@ (Eckart-Young + Gaussian-threshold) / CITED@ (Kim 2016)
# - real substrate bind exercised: hd_bind tie-check in self-test (LEARN_BIND_DIAG == elementwise bind)
# - deterministic seeding: np.random.default_rng(int) + torch manual_seed(int); NO hash()/list(set())
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
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.binding import bind as hd_bind      # noqa: E402  # REAL FHRR bind (long-stable; local+remote parity).
# Used only to CERTIFY (self-test) that LEARN_BIND_DIAG's elementwise product == the substrate bind on real codes
# embedded as complex64 (imag=0). Do NOT import newer siblings (remote hdlab/binding.py drift).

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)  # progress_logging: flush on newline (defense in depth)
    except (ValueError, OSError):
        pass

ANCHOR_NAME = "rank_matched_readout_tunable_plant_v1"
OUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)

# ===========================================================================
# CONFIG (all fixed a priori; calibration_check=default_ok_for_this_regime)
# ===========================================================================
M_DIM = 64                      # constituent code dimensionality
L_VOCAB = 48                    # codes per role (SEEN vocabulary)
R_PLANT_GRID = [1, 2, 4, 8]     # tunable interaction rank of the plant
READOUT_R_GRID = [1, 2, 4, 8, 16]   # learned readout rank sweep (1 == rank-1 diagonal SYM)
SEEDS_FULL = (7, 13, 17, 23, 29)
SEEDS_SMOKE = (7, 13, 17)
QUERY_FRAC = 0.35               # held-out NOVEL pairings
NCLASS = 2                      # balanced binary target
EPOCHS = 400
LR = 0.03
WD = 1.0e-3                     # weight-decay on U,V -> Occam bias toward low rank (over-rank stays honest)

EXPECTED_N_UNITS = len(R_PLANT_GRID)    # per seed (one arm-table per plant rank); cardinality sanity

# ---- pre-registered bands (fixed BEFORE running) ----
# THEORETICAL@Eckart-Young + Gaussian-threshold: for equal sigma, acc(R_plant,R) ~= 0.5 + arcsin(sqrt(R/R_plant))/pi
# for R<R_plant, ~ceiling for R>=R_plant. Predicted rank-1 staircase: R_plant=1 ->~0.97, =2 ->0.75, =4 ->0.667,
# =8 ->0.615. Predicted matched-rank recovery gap at R_plant=4: ceiling-0.667 ~= 0.30. Bands below sit under these.
CHANCE = 0.5
RECOVERY_TO_CEIL = 0.10         # G1: acc[Rp][R=Rp] >= ORACLE_ceil - this (rank-matched recovers to ceiling)
RECOVERY_OVER_RANK1 = 0.15      # G1: acc[Rp][R=Rp] - acc[Rp][R=1] >= this for Rp in {2,4,8} (recovers the miss)
RANK1_SOLVES_R1 = 0.90          # G2: acc[Rp=1][R=1] >= this (rank-1 solves rank-1 plant)
RANK1_DEGRADE = 0.15            # G2: acc[Rp=1][R=1] - acc[Rp=4][R=1] >= this (rank-1 degrades on rank-4 plant)
RANK1_ABOVE_CHANCE = 0.55       # G2: acc[Rp=4][R=1] >= this (degraded but above chance, matching 0.693)
MONO_TOL = 0.03                 # G3: acc[Rp][R] non-decreasing in R up to Rp within this tolerance
OVER_RANK_TOL = 0.05            # G3: acc[Rp][R=16] >= acc[Rp][R=Rp] - this (over-rank doesn't hurt much)
ORACLE_CEIL_MIN = 0.90          # G4: ORACLE >= this (arena separable / ceiling sanity)
SCRAMBLE_MAX = 0.55             # G4: SCRAMBLE novel <= this (must-fail fires)
ADD_FLOOR_MAX = 0.60            # G4: LEARN_ADD <= this (additive floor near chance; pure interaction, no main effect)

# ---- arm names ----
def rank_arm(r):
    return "LEARN_RANK_%d" % r
RANK_ARMS = [rank_arm(r) for r in READOUT_R_GRID]
BIND_DIAG = "LEARN_BIND_DIAG"; LEARN_ADD = "LEARN_ADD"; ORACLE = "ORACLE"; SCRAMBLE = "SCRAMBLE"
FREQ = "FREQ"; POP = "POP"
ARM_NAMES = RANK_ARMS + [BIND_DIAG, LEARN_ADD, ORACLE, SCRAMBLE, FREQ, POP]


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    try:
        return ("%.4f" % x) if (x == x) else "nan"
    except (TypeError, ValueError):
        return str(x)


def _sig(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int64).tobytes()).hexdigest()[:16]


def _write_start_marker(expected_n_units, run_mode):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(OUT_DIR, "_start_marker.json"))


# ===========================================================================
# PLANT (deterministic; tunable interaction rank; zero additive signal)
# ===========================================================================

def make_vocab(m, seed):
    """Centered Gaussian constituent codes for the two roles. Centering -> plant carries no main effect."""
    rng = np.random.default_rng(seed * 100003 + 11)
    A = rng.standard_normal((L_VOCAB, m)) / math.sqrt(m)
    B = rng.standard_normal((L_VOCAB, m)) / math.sqrt(m)
    A = A - A.mean(0, keepdims=True)      # sum_a phi_a = 0 -> E_a[score]=0
    B = B - B.mean(0, keepdims=True)      # sum_b psi_b = 0 -> E_b[score]=0
    return A.astype(np.float64), B.astype(np.float64)


def make_plant_M(m, r_plant, seed):
    """Rank-r_plant bilinear coupling with EQUAL singular values (hardest rank story)."""
    rng = np.random.default_rng(seed * 100057 + r_plant * 131 + 7)
    U, _ = np.linalg.qr(rng.standard_normal((m, r_plant)))   # orthonormal columns
    V, _ = np.linalg.qr(rng.standard_normal((m, r_plant)))
    sigma = np.ones(r_plant)                                  # EQUAL singular values
    M = (U * sigma[None, :]) @ V.T                            # m x m, rank r_plant
    return M


def build_pairs(A, B, M, seed):
    """All (a,b) combos; balanced-binary target via global median; deterministic novel-pairing split."""
    la, lb = A.shape[0], B.shape[0]
    aa, bb = np.meshgrid(np.arange(la), np.arange(lb), indexing="ij")
    aidx = aa.reshape(-1); bidx = bb.reshape(-1)
    phi = A[aidx]; psi = B[bidx]                              # (P,m) each
    score = np.einsum("pi,ij,pj->p", phi, M, psi)            # phi_a^T M psi_b
    thr = float(np.median(score))
    y = (score > thr).astype(np.int64)
    n = aidx.shape[0]
    rng = np.random.default_rng(seed * 100081 + 9)
    perm = rng.permutation(n)
    nq = int(round(QUERY_FRAC * n))
    q = np.sort(perm[:nq]); tr = np.sort(perm[nq:])
    train_combos = set((int(aidx[i]), int(bidx[i])) for i in tr)
    novel = np.array([(int(aidx[i]), int(bidx[i])) not in train_combos for i in q], dtype=bool)
    return dict(phi=phi, psi=psi, score=score, y=y, q=q, tr=tr, novel=novel)


# ===========================================================================
# READOUT ARMS (torch SGD; the DISCOVERY of the interaction FORM)
# ===========================================================================

def _standardize(z_tr, z_q):
    mu = z_tr.mean(0, keepdim=True); sd = z_tr.std(0, keepdim=True) + 1e-3
    return (z_tr - mu) / sd, (z_q - mu) / sd


def fit_lowrank_bilinear(phi_tr, psi_tr, ytr, phi_q, psi_q, m, R, nclass, seed):
    """Kim 2016 low-rank bilinear pooling readout: z=(phi.U)(*)(psi.V) [R-dim] -> logits. R=1 == rank-1 SYM."""
    g = torch.Generator().manual_seed(seed * 7919 + R * 1000 + 3)
    pt = torch.from_numpy(phi_tr).double(); qt = torch.from_numpy(phi_q).double()
    st = torch.from_numpy(psi_tr).double(); sq = torch.from_numpy(psi_q).double()
    yt = torch.from_numpy(ytr).long()
    U = torch.nn.Parameter(0.1 * torch.randn(m, R, generator=g, dtype=torch.float64))
    V = torch.nn.Parameter(0.1 * torch.randn(m, R, generator=g, dtype=torch.float64))
    W = torch.nn.Parameter(0.1 * torch.randn(R, nclass, generator=g, dtype=torch.float64))
    b = torch.nn.Parameter(torch.zeros(nclass, dtype=torch.float64))
    opt = torch.optim.Adam([U, V, W, b], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()

    def compose(P, S):
        return (P @ U) * (S @ V)      # (n,R) low-rank bilinear pooling

    for _ in range(EPOCHS):
        opt.zero_grad()
        z = compose(pt, st)
        zn = (z - z.mean(0, keepdim=True)) / (z.std(0, keepdim=True) + 1e-3)
        loss = lossf(zn @ W + b, yt) + WD * (U.pow(2).sum() + V.pow(2).sum())
        loss.backward(); opt.step()
    with torch.no_grad():
        z_tr = compose(pt, st); z_q = compose(qt, sq)
        z_trn, z_qn = _standardize(z_tr, z_q)
        pred = torch.argmax(z_qn @ W + b, 1).numpy().astype(np.int64)
    return pred


def fit_bind_diag(phi_tr, psi_tr, ytr, phi_q, psi_q, m, nclass, seed):
    """LITERAL substrate elementwise bind readout: z = phi (*) psi [m-dim] -> logits. 'the current bind'."""
    g = torch.Generator().manual_seed(seed * 7919 + 91)
    pt = torch.from_numpy(phi_tr).double(); qt = torch.from_numpy(phi_q).double()
    st = torch.from_numpy(psi_tr).double(); sq = torch.from_numpy(psi_q).double()
    yt = torch.from_numpy(ytr).long()
    W = torch.nn.Parameter(0.1 * torch.randn(m, nclass, generator=g, dtype=torch.float64))
    b = torch.nn.Parameter(torch.zeros(nclass, dtype=torch.float64))
    opt = torch.optim.Adam([W, b], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    z_tr = pt * st; z_q = qt * sq                    # elementwise bind (== hd_bind on real codes; self-test verifies)
    z_trn, z_qn = _standardize(z_tr, z_q)
    for _ in range(EPOCHS):
        opt.zero_grad()
        loss = lossf(z_trn @ W + b, yt); loss.backward(); opt.step()
    with torch.no_grad():
        pred = torch.argmax(z_qn @ W + b, 1).numpy().astype(np.int64)
    return pred


def fit_additive(phi_tr, psi_tr, ytr, phi_q, psi_q, m, nclass, seed):
    """Additive (no interaction) floor: logits = phi.Wa + psi.Wb + b."""
    g = torch.Generator().manual_seed(seed * 7919 + 271)
    pt = torch.from_numpy(phi_tr).double(); qt = torch.from_numpy(phi_q).double()
    st = torch.from_numpy(psi_tr).double(); sq = torch.from_numpy(psi_q).double()
    yt = torch.from_numpy(ytr).long()
    Wa = torch.nn.Parameter(0.1 * torch.randn(m, nclass, generator=g, dtype=torch.float64))
    Wb = torch.nn.Parameter(0.1 * torch.randn(m, nclass, generator=g, dtype=torch.float64))
    b = torch.nn.Parameter(torch.zeros(nclass, dtype=torch.float64))
    opt = torch.optim.Adam([Wa, Wb, b], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    for _ in range(EPOCHS):
        opt.zero_grad()
        loss = lossf(pt @ Wa + st @ Wb + b, yt); loss.backward(); opt.step()
    with torch.no_grad():
        pred = torch.argmax(qt @ Wa + sq @ Wb + b, 1).numpy().astype(np.int64)
    return pred


def acc(pred, gold):
    if len(pred) == 0:
        return float("nan")
    return float((np.asarray(pred) == np.asarray(gold)).mean())


# ===========================================================================
# per (R_plant, seed) scoring -- runs the full readout-rank sweep + controls
# ===========================================================================

def score_unit(r_plant, seed, m=M_DIM, epochs=None):
    A, B = make_vocab(m, seed)
    M = make_plant_M(m, r_plant, seed)
    P = build_pairs(A, B, M, seed)
    tr, q, novel = P["tr"], P["q"], P["novel"]
    phi_tr, psi_tr = P["phi"][tr], P["psi"][tr]
    phi_q, psi_q = P["phi"][q], P["psi"][q]
    ytr, gold = P["y"][tr], P["y"][q]
    score_q = P["score"][q]
    thr_tr = float(np.median(P["score"][tr]))
    pop_label = int(np.argmax(np.bincount(ytr, minlength=NCLASS)))

    preds = {}
    for r in READOUT_R_GRID:
        preds[rank_arm(r)] = fit_lowrank_bilinear(phi_tr, psi_tr, ytr, phi_q, psi_q, m, r, NCLASS, seed)
    preds[BIND_DIAG] = fit_bind_diag(phi_tr, psi_tr, ytr, phi_q, psi_q, m, NCLASS, seed)
    preds[LEARN_ADD] = fit_additive(phi_tr, psi_tr, ytr, phi_q, psi_q, m, NCLASS, seed)
    preds[ORACLE] = (score_q > thr_tr).astype(np.int64)
    # SCRAMBLE: strongest readout (rank-16) on SHUFFLED train labels -> chance on novel (must-fail).
    rng = np.random.default_rng(seed * 100103 + r_plant * 17 + 5)
    ytr_shuf = ytr[rng.permutation(len(ytr))]
    preds[SCRAMBLE] = fit_lowrank_bilinear(phi_tr, psi_tr, ytr_shuf, phi_q, psi_q, m, max(READOUT_R_GRID), NCLASS, seed)
    preds[POP] = np.full(len(gold), pop_label, dtype=np.int64)

    out = {}
    for sname, mask in (("novel", novel), ("seen", ~novel), ("all", np.ones(len(gold), bool))):
        d = {arm: round(acc(np.asarray(preds[arm])[mask], gold[mask]), 5) if mask.sum() > 0 else float("nan")
             for arm in preds}
        d[FREQ] = d[POP]      # majority-class baseline == chance for balanced binary
        d["n"] = int(mask.sum())
        out[sname] = d
    # ARMS-MUST-DIFFER (META_RULE_AF): learned readouts + controls mutually distinct (catches impl bugs).
    # ORACLE excluded (a fully-recovered readout legitimately equals the oracle).
    sig_arms = RANK_ARMS + [BIND_DIAG, LEARN_ADD, SCRAMBLE]
    sigs = {arm: _sig(preds[arm]) for arm in sig_arms}
    return dict(strata=out, sigs=sigs, chance=CHANCE, n_novel=int(novel.sum()), n_query=int(len(gold)))


# ===========================================================================
# full measurement + verdict
# ===========================================================================

def run_measurement(seeds=SEEDS_FULL, m=M_DIM, run_mode="full"):
    _write_start_marker(EXPECTED_N_UNITS * len(seeds), run_mode)
    _log("%s run: R_plant=%s x readout_R=%s x %d seeds, m=%d L=%d (EXPECTED_N_UNITS/seed=%d)"
         % (run_mode, R_PLANT_GRID, READOUT_R_GRID, len(seeds), m, L_VOCAB, EXPECTED_N_UNITS))
    t0 = time.perf_counter()
    per = {rp: [] for rp in R_PLANT_GRID}
    n_units = 0
    for si, sd in enumerate(seeds):
        for rp in R_PLANT_GRID:
            per[rp].append(score_unit(rp, sd, m=m))
            n_units += 1
        _log("  seed %d/%d done (elapsed=%.1fs)" % (si + 1, len(seeds), time.perf_counter() - t0))
    cardinality_ok = bool(n_units == EXPECTED_N_UNITS * len(seeds))

    def mean_novel(rp, arm):
        vals = [u["strata"]["novel"][arm] for u in per[rp]]
        vals = [v for v in vals if v == v]
        return float(np.mean(vals)) if vals else float("nan")

    # acc table: table[rp][arm] = mean novel accuracy
    table = {rp: {arm: round(mean_novel(rp, arm), 5) for arm in (ARM_NAMES + [FREQ])} for rp in R_PLANT_GRID}
    # rank curve: rankacc[rp][R]
    rankacc = {rp: {r: table[rp][rank_arm(r)] for r in READOUT_R_GRID} for rp in R_PLANT_GRID}
    oracle_ceil = float(np.mean([table[rp][ORACLE] for rp in R_PLANT_GRID]))

    # ---- G4 controls ----
    scramble_max = max(table[rp][SCRAMBLE] for rp in R_PLANT_GRID)
    add_max = max(table[rp][LEARN_ADD] for rp in R_PLANT_GRID)
    oracle_min = min(table[rp][ORACLE] for rp in R_PLANT_GRID)
    controls_ok = bool(oracle_min >= ORACLE_CEIL_MIN and scramble_max <= SCRAMBLE_MAX and add_max <= ADD_FLOOR_MAX)

    # ---- G2 rank-1 degradation (reproduce 0.975 -> 0.6x; telemetry-sensitivity of R_plant on rank-1) ----
    r1 = {rp: rankacc[rp][1] for rp in R_PLANT_GRID}
    rank1_solves_r1 = bool(r1[1] >= RANK1_SOLVES_R1)
    rank1_degrades = bool((r1[1] - r1[4]) >= RANK1_DEGRADE and r1[4] >= RANK1_ABOVE_CHANCE)
    # monotone decreasing rank-1 acc as R_plant rises (perturbing R_plant moves rank-1 acc)
    r1_seq = [r1[rp] for rp in R_PLANT_GRID]
    rank1_monotone_down = all(r1_seq[i] >= r1_seq[i + 1] - MONO_TOL for i in range(len(r1_seq) - 1))
    rank1_span = round(r1[1] - r1[max(R_PLANT_GRID)], 5)
    degradation_ok = bool(rank1_solves_r1 and rank1_degrades and rank1_monotone_down)

    # ---- G1 recovery (rank-matched recovers what rank-1 misses) ----
    recovery_flags = {}
    for rp in R_PLANT_GRID:
        matched = rankacc[rp][rp]                 # readout rank == plant rank
        rec_to_ceil = matched >= (table[rp][ORACLE] - RECOVERY_TO_CEIL)
        if rp == 1:
            over_r1 = True                        # rp=1: rank-1 already recovers (no gap to require)
        else:
            over_r1 = (matched - rankacc[rp][1]) >= RECOVERY_OVER_RANK1
        recovery_flags[rp] = bool(rec_to_ceil and over_r1)
    recovery_ok = all(recovery_flags.values())

    # ---- G3 monotone-in-R up to R_plant + over-rank does not hurt ----
    mono_flags = {}; overrank_flags = {}
    for rp in R_PLANT_GRID:
        rs = [r for r in READOUT_R_GRID if r <= rp]
        seq = [rankacc[rp][r] for r in rs]
        mono_flags[rp] = all(seq[i] <= seq[i + 1] + MONO_TOL for i in range(len(seq) - 1))
        overrank_flags[rp] = rankacc[rp][max(READOUT_R_GRID)] >= (rankacc[rp][rp] - OVER_RANK_TOL)
    monotone_ok = all(mono_flags.values()) and all(overrank_flags.values())

    # ---- verdict ----
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not controls_ok:
        verdict = "HARD_FAIL_CONTROLS_DID_NOT_FIRE"
    elif not degradation_ok:
        verdict = "HARD_FAIL_NO_RANK_EFFECT_RANK1_DID_NOT_DEGRADE"
    elif not recovery_ok:
        verdict = "HARD_FAIL_RANK_NOT_THE_LEVER_NO_RECOVERY"
    elif recovery_ok and degradation_ok and monotone_ok:
        verdict = "HARD_PASS_RANK_MATCHING_RECOVERS_HIGHER_RANK_INTERACTION"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_RECOVERY_OR_NONMONOTONE"

    msg = ("%s || rank1 curve (by R_plant %s): %s (span=%s solves_r1=%s degrades=%s mono_down=%s) | "
           "matched-rank recovery %s (ceil=%s) | monotone_in_R=%s overrank_ok=%s | "
           "ORACLE[min=%s] SCRAMBLE[max=%s] ADD[max=%s] controls=%s | cardinality_ok=%s"
           % (verdict, R_PLANT_GRID, {rp: _fmt(r1[rp]) for rp in R_PLANT_GRID}, _fmt(rank1_span),
              rank1_solves_r1, rank1_degrades, rank1_monotone_down,
              {rp: recovery_flags[rp] for rp in R_PLANT_GRID}, _fmt(oracle_ceil),
              {rp: mono_flags[rp] for rp in R_PLANT_GRID}, {rp: overrank_flags[rp] for rp in R_PLANT_GRID},
              _fmt(oracle_min), _fmt(scramble_max), _fmt(add_max), controls_ok, cardinality_ok))

    metrics = dict(
        verdict=verdict, verdict_msg=msg, summary=msg[:200], run_mode=run_mode,
        elapsed_s=round(time.perf_counter() - t0, 2), anchor_name=ANCHOR_NAME,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        config=dict(m_dim=m, l_vocab=L_VOCAB, r_plant_grid=R_PLANT_GRID, readout_r_grid=READOUT_R_GRID,
                    seeds=list(seeds), query_frac=QUERY_FRAC, nclass=NCLASS, epochs=EPOCHS, lr=LR, wd=WD,
                    equal_singular_values=True),
        acc_table_novel=table, rank_curve_novel=rankacc, oracle_ceil=round(oracle_ceil, 5),
        gates=dict(cardinality_ok=cardinality_ok, controls_ok=controls_ok, degradation_ok=degradation_ok,
                   recovery_ok=recovery_ok, monotone_ok=monotone_ok,
                   rank1_by_plant={rp: round(r1[rp], 5) for rp in R_PLANT_GRID},
                   rank1_span=rank1_span, rank1_solves_r1=rank1_solves_r1, rank1_degrades=rank1_degrades,
                   rank1_monotone_down=rank1_monotone_down,
                   recovery_flags={rp: recovery_flags[rp] for rp in R_PLANT_GRID},
                   mono_flags={rp: mono_flags[rp] for rp in R_PLANT_GRID},
                   overrank_flags={rp: overrank_flags[rp] for rp in R_PLANT_GRID},
                   oracle_min=round(oracle_min, 5), scramble_max=round(scramble_max, 5), add_max=round(add_max, 5)),
        bands=dict(CHANCE=CHANCE, RECOVERY_TO_CEIL=RECOVERY_TO_CEIL, RECOVERY_OVER_RANK1=RECOVERY_OVER_RANK1,
                   RANK1_SOLVES_R1=RANK1_SOLVES_R1, RANK1_DEGRADE=RANK1_DEGRADE, RANK1_ABOVE_CHANCE=RANK1_ABOVE_CHANCE,
                   MONO_TOL=MONO_TOL, OVER_RANK_TOL=OVER_RANK_TOL, ORACLE_CEIL_MIN=ORACLE_CEIL_MIN,
                   SCRAMBLE_MAX=SCRAMBLE_MAX, ADD_FLOOR_MAX=ADD_FLOOR_MAX, EXPECTED_N_UNITS_PER_SEED=EXPECTED_N_UNITS),
        per_seed_novel={rp: [u["strata"]["novel"] for u in per[rp]] for rp in R_PLANT_GRID},
    )
    return metrics


def _write_metrics(metrics):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=float)
    os.replace(tmp, os.path.join(OUT_DIR, "metrics.json"))


# ===========================================================================
# SELF-TEST (exercises the REAL readout code path at tiny scale; asserts CONSTRUCTION facts + machinery, NOT the
# open rank-matching claim -- that is MEASURED in FULL and gated by the pre-reg bands, not asserted here)
# ===========================================================================

def _bind_diag_equals_substrate_bind():
    """LEARN_BIND_DIAG's elementwise product == the REAL FHRR bind on real codes embedded as complex64 (imag=0)."""
    g = np.random.default_rng(5)
    phi = g.standard_normal((6, 16)).astype(np.float32)
    psi = g.standard_normal((6, 16)).astype(np.float32)
    bound = hd_bind(torch.from_numpy(phi).to(torch.complex64), torch.from_numpy(psi).to(torch.complex64))
    return bool(np.allclose(bound.real.numpy(), phi * psi, atol=1e-5))


def _lowrank_pooling_numeric_identity():
    """rank-1 pooling z=(phi.u)(psi.v) equals the outer-product bilinear form phi^T (u v^T) psi."""
    g = torch.Generator().manual_seed(9)
    phi = torch.randn(5, 12, generator=g, dtype=torch.float64)
    psi = torch.randn(5, 12, generator=g, dtype=torch.float64)
    u = torch.randn(12, 1, generator=g, dtype=torch.float64)
    v = torch.randn(12, 1, generator=g, dtype=torch.float64)
    z_pool = ((phi @ u) * (psi @ v)).squeeze(1)
    M = u @ v.T
    z_form = torch.einsum("pi,ij,pj->p", phi, M, psi)
    return bool(torch.allclose(z_pool, z_form, atol=1e-9))


def self_test():
    ok_all = True
    details = {}

    details["bind_diag_equals_substrate_bind"] = _bind_diag_equals_substrate_bind()
    details["lowrank_pooling_numeric_identity"] = _lowrank_pooling_numeric_identity()

    # tiny-scale REAL arm pipeline (exercises fit_lowrank_bilinear / fit_bind_diag / fit_additive / ORACLE / SCRAMBLE)
    m_t = 16
    # plant rank exactly = r_plant (construction check)
    M1 = make_plant_M(m_t, 1, 7); M4 = make_plant_M(m_t, 4, 7)
    details["plant_rank_1"] = int(np.linalg.matrix_rank(M1))
    details["plant_rank_4"] = int(np.linalg.matrix_rank(M4))

    u1 = score_unit(1, 7, m=m_t)["strata"]["novel"]
    u4 = score_unit(4, 7, m=m_t)["strata"]["novel"]
    details["r_plant1_R1"] = u1[rank_arm(1)]
    details["r_plant4_R1"] = u4[rank_arm(1)]
    details["r_plant4_R4"] = u4[rank_arm(4)]
    details["r_plant4_ORACLE"] = u4[ORACLE]
    details["r_plant4_SCRAMBLE"] = u4[SCRAMBLE]
    details["r_plant4_ADD"] = u4[LEARN_ADD]
    details["r_plant4_FREQ"] = u4[FREQ]
    details["n_novel"] = u4["n"]

    # ARMS-MUST-DIFFER (META_RULE_AF)
    digs = score_unit(4, 7, m=m_t)["sigs"]
    arms_differ = len(set(digs.values())) == len(digs)
    details["arms_differ_sig_count"] = len(set(digs.values()))
    details["arms_expected"] = len(digs)

    checks = {
        # --- machinery ---
        "bind_diag_equals_substrate_bind": details["bind_diag_equals_substrate_bind"],
        "lowrank_pooling_numeric_identity": details["lowrank_pooling_numeric_identity"],
        "plant_M1_is_rank_1": details["plant_rank_1"] == 1,
        "plant_M4_is_rank_4": details["plant_rank_4"] == 4,
        # --- CONSTRUCTION: arena is solvable + the rank discriminator FIRES at tiny scale (not the full claim) ---
        "oracle_separable": details["r_plant4_ORACLE"] >= 0.85,
        "rank1_solves_rank1_plant": details["r_plant1_R1"] >= 0.80,
        "rank_discriminator_fires": (details["r_plant4_R4"] - details["r_plant4_R1"]) >= 0.10,
        # --- CONTROLS fire (META_RULE_AG baseline_in_band + saturation-vacuous guard) ---
        "scramble_mustfail_fires": details["r_plant4_SCRAMBLE"] <= 0.65,
        "additive_floor_in_band": details["r_plant4_ADD"] <= 0.70,
        "freq_baseline_in_band": 0.05 < details["r_plant4_FREQ"] < 0.95,
        "enough_novel": details["n_novel"] >= 20,
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
        # reduced grid + m; multi-seed on the discriminator (continuous-score cell); still fires rank-matching gap.
        global R_PLANT_GRID, READOUT_R_GRID
        R_PLANT_GRID = [1, 4]
        READOUT_R_GRID = [1, 4, 8]
        m = run_measurement(seeds=SEEDS_SMOKE, m=32, run_mode="smoke")
        _write_metrics(m)
        _log("SMOKE " + m["verdict_msg"])
        return
    # DEFAULT (no flag) = FULL run to completion (runner invokes `python -u <script>`; META_RULE_16)
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
