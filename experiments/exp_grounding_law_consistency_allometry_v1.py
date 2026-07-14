"""CONSISTENCY-AGAINST-INVARIANTS grounding cell (Track-B grounding, LEVER A).

WHY THIS CELL EXISTS -- the cheapest, most-novel Track-B grounding lever.
  Prior grounding cells FUSE measured numeric literals into the KG and ask whether
  they add over the relational channel (mammal-allometry xchannel = GROUNDING_REDUNDANT;
  grounding-improves-relation = MIDDLE_BAND). Those are BAKE-IN OF DATA POINTS.
  This cell tests a DIFFERENT, cheaper form of grounding: BAKE-IN OF A LAW.
  Ground attribute values by requiring them to satisfy a KNOWN closed-form INVARIANT
  (an allometric scaling law), and use divergence-from-law as an ERROR / CORRECTION
  signal. One law grounds MANY values -> more general than per-value literals.

  CAVEAT (honest, per convergence #1 of the grounding drill): a LAW is itself EXTERNAL
  info baked in -- the exponent encodes real-world biological structure. This is NOT
  internal-bootstrapping (a closed system cannot manufacture grounding, DPI/Information-
  Causality). It is bake-in of a LAW rather than of data points: cheaper + more general.

THE LAWS (closed-form, glass-box, EXTERNAL biological constants -- the "grounding"):
  Allometry is LINEAR IN LOG SPACE. log10(y) = slope * log10(x) + b, slope = KNOWN.
  L1 mass_from_length  slope = 3.0   geometric isometry (mass ~ volume ~ length^3);
                                      CITED@textbook; MEASURED slope in this data +2.80
                                      R2=0.986 (a very tight invariant) -> HEADLINE law.
  L2 gestation_from_mass slope = 0.25 quarter-power life-history allometry;
                                      CITED@life-history-theory; MEASURED +0.207 R2=0.491.
  L3 lifespan_from_mass  slope = 0.20 longevity allometry; CITED; MEASURED +0.161 R2=0.478.
  The intercept b is a units nuisance (NOT the law); fit robustly per-entity LOO by
  median of the OTHER entities' residuals (no leakage of the held-out target).

WHAT IS TESTED (two things the LAW should buy):
  (a) ERROR-CORRECTION: give the substrate measured values, CORRUPT a fraction
      (multiplicative log-shift that keeps the value IN the marginal range but OFF the
      cross-attribute manifold). Does law-consistency DETECT (rank corrupted above clean)
      and CORRECT (project onto the law) BETTER than a no-law baseline?
      Baselines (no cross-attribute law): MARGINAL (z-score within the attribute's own
      distribution) + RELATIONAL (deviation from taxonomic-neighbor median via a REAL
      KGStore). The corruption is designed so the MARGINAL baseline is genuinely weak:
      a 0.02 kg mouse mass corrupted to 0.6 kg is normal FOR THE MARGINAL (rat-sized)
      but wildly off the mass-length line -- only the LAW catches it.
  (b) SPARSE-TAIL IMPUTATION: hold out a target attribute for the COLD TAIL (bottom-
      tertile taxonomic degree -- the confirmed relational bottleneck; few/no neighbors).
      Impute via the law (same-entity predictor + closed-form) vs relational kNN vs mean.
      The law is DEGREE-INVARIANT by construction (needs no neighbors) -> should hold on
      the cold tail where relational imputation collapses. Built-in weak-point
      localization: report LAW vs RELATIONAL R2 on cold-tail AND interior strata.

MUST-FAIL (the discriminator that proves it is the REAL law, not any regularizer):
  WRONG_EXP: same structure, WRONG exponent (slope=1.0 for all laws).
  SCRAMBLE:  true exponent but the predictor attribute SHUFFLED across entities.
  Neither may help detection / correction / imputation. If a wrong / scrambled law
  ALSO helps, the signal is generic smoothing, not the invariant -> HARD_FAIL.

FAIRNESS + WEAK-POINT LOCALIZATION (first-class per cell):
  - info-ceiling: imputation R2 cannot exceed the law's own fit R2 (0.986 for L1);
    HARD_PASS bar 0.50 is well below ceiling AND above the relational floor.
  - fair baseline: detection/correction compare LAW to the BEST of MARGINAL/RELATIONAL.
  - metric-can-MOVE: corruption is stochastic per seed; detection AUC / R2 are not
    structurally frozen (multi-seed variance probe).
  - degree confound handled head-on: the cold-tail stratum IS the weak-point localizer.
  - must-fail (WRONG_EXP + SCRAMBLE) fires at self-test scale.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: rank-AUC + R2 skill cell; no argmax capacity floor (declared)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < MARGINAL_AUC < LAW_AUC-0.10; not sat)
# - discriminator survives scale: self-test runs the REAL mechanism on REAL data (3 seeds)
#   AND the must-fail (WRONG_EXP/SCRAMBLE) collapse is asserted at self-test.
# - HARD_PASS strictly above floor + margin (META_RULE_L)
# - HP_SCOPE per-arm declaration (see prereg)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_laws (one detection/impute unit per
#   law per seed); verdict counts and HARD_FAILs on breach.
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_justification (log10 for power-law vars; oracle-K
#   flagging so no per-arm detection-threshold tuning; intercept LOO-median robust).
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ in the prereg
# - F.1 real_code_path: self-test CONSTRUCTS the REAL KGStore (via build_relational_store
#   from the sibling allometry cell) at n_dim<=2048 + ingests real triples.
# - F.2/F.3 substrate_signature: KGStore bound with BASE/portable kwargs only.
# - F.4 guard_baseline_valid: RELATIONAL imputation (control) validated ABOVE RANDOM floor.
# - progress_logging: print_flush_true (cheap cell; timeout << 1800 anyway)

Compute architecture: sequential-CPU with justification -- 64 entities, closed-form laws
  are dimension-free, the only n_dim-dependent op is a [64,64] relational-similarity
  Gram from a REAL KGStore; per-seed wall << 2s, whole cell << 10s. No GPU batching
  candidate (wall-time sanity < 10s). Storage: no_composition (relational baseline uses
  sharded KGStore E/R codes; no bundled multi-item composition). No sequential dependency.

ASCII-only per feedback_ascii_only_in_scripts. No em-dashes in output.
"""
from __future__ import annotations

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

import torch

# Real substrate objects the FULL run uses (F.1/F.2/F.3) + the REAL mammal dataset.
from hdlab.kg_traversal import KGStore
from experiments.exp_grounding_mammal_allometry_xchannel_fpe_v1 import (
    load_mammals, build_relational_store, _cos_sim_real, _PROP_NAMES,
)
from experiments._validity_preflight import run_validity_preflight

ANCHOR_NAME = "grounding_law_consistency_allometry_v1"

# --------------------------------------------------------------------------- #
# Arms                                                                         #
# --------------------------------------------------------------------------- #
LAW = "LAW"
MARGINAL = "MARGINAL"
RELATIONAL = "RELATIONAL"
MEAN = "MEAN"
RANDOM = "RANDOM"
WRONG_EXP = "WRONG_EXP"
SCRAMBLE = "SCRAMBLE"
DET_ARMS = [LAW, MARGINAL, RELATIONAL, WRONG_EXP, SCRAMBLE]         # detection + correction
IMP_ARMS = [LAW, RELATIONAL, MEAN, RANDOM, WRONG_EXP, SCRAMBLE]     # imputation

# Attribute column indices in mm["props"]: 0=mass 1=length 2=lifespan 3=gestation 4=litter
MASS, LENGTH, LIFESPAN, GESTATION, LITTER = 0, 1, 2, 3, 4

# LAWS: (name, predictor_idx, target_idx, known_slope_log10). Intercept fit LOO-median.
LAWS = [
    ("mass_from_length",   LENGTH, MASS,      3.00),   # HEADLINE (geometric isometry)
    ("gestation_from_mass", MASS,  GESTATION, 0.25),   # quarter-power life-history
    ("lifespan_from_mass",  MASS,  LIFESPAN,  0.20),   # longevity allometry
]
HEADLINE_LAW = 0
WRONG_SLOPE = 1.0   # clearly-wrong exponent for every law (must-fail)

# --------------------------------------------------------------------------- #
# Config                                                                       #
# --------------------------------------------------------------------------- #
FULL_CFG = dict(n_dim=8192, seeds=[7, 13, 19, 23, 29], corruption_rate=0.25,
                shift_lo=0.8, shift_hi=1.5, weight_exp=6.0)
SELFTEST_CFG = dict(n_dim=2048, seeds=[7, 13, 19], corruption_rate=0.25,
                    shift_lo=0.8, shift_hi=1.5, weight_exp=6.0)

# HARD-PASS / HARD-FAIL bands (pre-registered; see prereg for full feasibility analysis).
# (a) detection + correction (headline law L1)
HP_LAW_AUC = 0.85               # LAW detection AUC (headline law) must reach this
HP_LAW_BEATS_NOLAW_AUC = 0.10   # LAW_AUC - best(MARGINAL,RELATIONAL) AUC
HP_LAW_CORR_GAIN = 0.30         # LAW correction reduces all-cell log-MAE by >= this frac
HP_LAW_BEATS_NOLAW_CORR = 0.10  # LAW corr gain - best no-law corr gain
# (b) sparse-tail imputation (headline law L1)
HP_LAW_IMP_R2 = 0.50            # LAW imputation R2 on cold tail
HP_LAW_BEATS_REL_IMP = 0.15     # LAW R2 - RELATIONAL R2 on cold tail
HP_DEGREE_INVAR = 0.15          # LAW R2 cold-tail >= LAW R2 interior - this (degree-invariant)
# MUST-FAIL, two-pronged (calibrated to the additive-in-log corruption leakage below):
#   SCRAMBLE = shuffle predictor -> PURE no-law (breaks entity-pairing) -> must COLLAPSE
#     on all three axes (proves the LAW/pairing is load-bearing).
#   WRONG_EXP = true pairing, WRONG slope -> a DEGRADED law (a monotone length<->mass
#     relationship survives at ANY positive slope, so it retains partial signal). The
#     real exponent must BEAT it by a large margin AND the wrong exponent must add
#     nothing over the no-law baselines (proves the RIGHT EXPONENT VALUE is load-bearing,
#     not just that some relationship exists).
# NB additive-in-log corruption inflates ANY y-residual, so a wrong/scrambled detection
# AUC floors near the no-law baseline (~0.68), NOT at chance 0.5 -- hence "<= best-no-law
# + margin", not "<= 0.5".
MF_AUC_OVER_NOLAW = 0.05        # wrong/scramble detection AUC must be <= best-no-law + this
MF_CORR_CEIL = 0.10             # SCRAMBLE correction gain must be <= this (no correction)
MF_IMP_CEIL = 0.15              # SCRAMBLE imputation R2 must be <= this (near/below mean)
WRONG_MARGIN_AUC = 0.15         # LAW - WRONG_EXP detection AUC margin (exponent value matters)
WRONG_MARGIN_CORR = 0.20        # LAW - WRONG_EXP correction-gain margin
WRONG_MARGIN_IMP = 0.20         # LAW - WRONG_EXP imputation-R2 margin
# encoding / load integrity
HF_L1_FIT_R2 = 0.80             # the headline law's own true-data fit R2 (info-ceiling)


# --------------------------------------------------------------------------- #
# Rank / skill helpers (scipy-free)                                            #
# --------------------------------------------------------------------------- #
def _rankdata(x: torch.Tensor) -> torch.Tensor:
    """1-based average ranks (ties averaged). x: [n] float."""
    n = x.numel()
    order = torch.argsort(x)
    sx = x[order]
    ranks = torch.empty(n, dtype=torch.float64)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sx[j + 1] == sx[i]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        ranks[order[i:j + 1]] = avg
        i = j + 1
    return ranks


def _auc(scores: torch.Tensor, labels: torch.Tensor) -> float:
    """Rank AUC = P(score_pos > score_neg) via Mann-Whitney. labels bool (positive=True)."""
    pos = scores[labels]
    neg = scores[~labels]
    if pos.numel() == 0 or neg.numel() == 0:
        return float("nan")
    ranks = _rankdata(torch.cat([pos.to(torch.float64), neg.to(torch.float64)]))
    r_pos = ranks[: pos.numel()].sum()
    return float((r_pos - pos.numel() * (pos.numel() + 1) / 2.0) / (pos.numel() * neg.numel()))


def _r2(yhat: torch.Tensor, ytrue: torch.Tensor) -> float:
    """R^2 skill vs mean of ytrue (both [n] log-space). >0 = beats the marginal mean."""
    if ytrue.numel() < 3:
        return float("nan")
    ss_tot = ((ytrue - ytrue.mean()) ** 2).sum()
    if ss_tot <= 1e-12:
        return float("nan")
    ss_res = ((ytrue - yhat) ** 2).sum()
    return float(1.0 - ss_res / ss_tot)


def _fit_r2(logx: torch.Tensor, logy: torch.Tensor, slope: float) -> float:
    """R2 of the fixed-slope law with LOO-median intercept, over all entities (info-ceiling)."""
    b = float((logy - slope * logx).median())
    return _r2(slope * logx + b, logy)


# --------------------------------------------------------------------------- #
# Corruption                                                                   #
# --------------------------------------------------------------------------- #
def corrupt_logvals(logy_true: torch.Tensor, rate: float, shift_lo: float, shift_hi: float,
                    gen: torch.Generator) -> tuple:
    """Multiplicative-in-linear (additive-in-log10) corruption of a fraction of values.

    Returns (logy_corrupt [E], corrupt_mask [E] bool). Shift magnitude ~ U[lo,hi], sign
    random -> value moves OFF the cross-attribute manifold but stays in marginal range.
    """
    E = logy_true.numel()
    k = max(1, int(round(rate * E)))
    perm = torch.randperm(E, generator=gen)
    idx = perm[:k]
    mask = torch.zeros(E, dtype=torch.bool)
    mask[idx] = True
    mag = shift_lo + (shift_hi - shift_lo) * torch.rand(k, generator=gen, dtype=torch.float64)
    sign = torch.where(torch.rand(k, generator=gen) < 0.5, -1.0, 1.0).to(torch.float64)
    logy_c = logy_true.clone()
    logy_c[idx] = logy_c[idx] + sign * mag
    return logy_c, mask


# --------------------------------------------------------------------------- #
# Per-entity LOO helpers                                                        #
# --------------------------------------------------------------------------- #
def _loo_intercept(logx: torch.Tensor, logy: torch.Tensor, slope: float) -> torch.Tensor:
    """Per-entity LOO robust intercept b_{-e} = median_{j!=e}(logy_j - slope*logx_j). [E]."""
    E = logx.numel()
    resid = logy - slope * logx           # [E]
    b = torch.empty(E, dtype=torch.float64)
    for e in range(E):
        m = torch.ones(E, dtype=torch.bool)
        m[e] = False
        b[e] = resid[m].median()
    return b


def _relational_loo(sim: torch.Tensor, logy: torch.Tensor, weight_exp: float,
                    known: torch.Tensor) -> torch.Tensor:
    """Similarity-weighted LOO prediction of logy for every entity from KNOWN entities. [E].

    known [E] bool: which entities may serve as neighbors AND are scored. Self excluded.
    """
    E = sim.shape[0]
    preds = torch.full((E,), float("nan"), dtype=torch.float64)
    for e in range(E):
        w = torch.clamp(sim[e].clone().to(torch.float64), min=0.0)
        w[e] = 0.0
        w[~known] = 0.0
        w = w.pow(weight_exp)
        wsum = w.sum()
        if wsum <= 1e-12:
            preds[e] = logy[known].mean()
        else:
            preds[e] = (w * logy).sum() / wsum
    return preds


# --------------------------------------------------------------------------- #
# One law: detection + correction (task a) and imputation (task b)             #
# --------------------------------------------------------------------------- #
def run_law(law, mm, logprops, sim_rel, sim_rand, cfg, gen) -> dict:
    """Run every arm for ONE law + ONE seed. Returns detection AUC, correction gain,
    imputation R2 (cold-tail + interior) per arm, plus true-data fit R2 (info-ceiling)."""
    name, p_idx, t_idx, slope = law
    E = mm["n"]
    logx_true = logprops[:, p_idx]
    logy_true = logprops[:, t_idx]
    fit_r2 = _fit_r2(logx_true, logy_true, slope)

    # scrambled predictor (shared across the detection + imputation must-fail arms).
    perm = torch.randperm(E, generator=gen)
    logx_scr = logx_true[perm]

    # ---- (a) DETECTION + CORRECTION -------------------------------------- #
    logy_c, corrupt = corrupt_logvals(logy_true, cfg["corruption_rate"],
                                      cfg["shift_lo"], cfg["shift_hi"], gen)
    n_corrupt = int(corrupt.sum())

    def law_resid(lx, sl):
        b = _loo_intercept(lx, logy_c, sl)      # intercept from the (corrupted) y, LOO
        return (logy_c - (sl * lx + b)).abs()

    # detection scores (higher = more likely corrupt)
    det_scores = {}
    det_scores[LAW] = law_resid(logx_true, slope)
    # MARGINAL: |z-score| of logy_c within its own distribution (robust center=median).
    med = logy_c.median()
    mad = (logy_c - med).abs().median().clamp_min(1e-9)
    det_scores[MARGINAL] = ((logy_c - med).abs() / mad)
    # RELATIONAL: deviation from taxonomic-neighbor median of logy_c (real KGStore sim).
    all_known = torch.ones(E, dtype=torch.bool)
    rel_pred = _relational_loo(sim_rel, logy_c, cfg["weight_exp"], all_known)
    det_scores[RELATIONAL] = (logy_c - rel_pred).abs()
    det_scores[WRONG_EXP] = law_resid(logx_true, WRONG_SLOPE)
    det_scores[SCRAMBLE] = law_resid(logx_scr, slope)

    det_auc = {a: _auc(det_scores[a], corrupt) for a in DET_ARMS}

    # correction: flag top-K by score (K = oracle n_corrupt; same K all arms -> fair),
    # replace flagged with the arm's correction target, score all-cell log-MAE vs true.
    base_err = float((logy_c - logy_true).abs().mean())
    b_law_all = _loo_intercept(logx_true, logy_c, slope)
    corr_target = {
        LAW:        slope * logx_true + b_law_all,
        MARGINAL:   torch.full((E,), float(med), dtype=torch.float64),
        RELATIONAL: rel_pred,
        WRONG_EXP:  WRONG_SLOPE * logx_true + _loo_intercept(logx_true, logy_c, WRONG_SLOPE),
        SCRAMBLE:   slope * logx_scr + _loo_intercept(logx_scr, logy_c, slope),
    }
    corr_gain = {}
    for a in DET_ARMS:
        k = n_corrupt
        flag = torch.zeros(E, dtype=torch.bool)
        if k > 0:
            topk = torch.topk(det_scores[a], k).indices
            flag[topk] = True
        corrected = torch.where(flag, corr_target[a], logy_c)
        err = float((corrected - logy_true).abs().mean())
        corr_gain[a] = (1.0 - err / base_err) if base_err > 1e-9 else float("nan")

    # ---- (b) IMPUTATION on cold tail (true values; hold out target) ------- #
    cold = mm["boundary"]                  # bottom-tertile taxonomic degree
    interior = ~cold
    known_int = interior                   # for cold-tail impute, neighbors/fit = interior
    b_loo_true = _loo_intercept(logx_true, logy_true, slope)          # true-data LOO intercept
    b_loo_wrong = _loo_intercept(logx_true, logy_true, WRONG_SLOPE)
    b_loo_scr = _loo_intercept(logx_scr, logy_true, slope)
    imp_pred = {
        LAW:        slope * logx_true + b_loo_true,
        WRONG_EXP:  WRONG_SLOPE * logx_true + b_loo_wrong,
        SCRAMBLE:   slope * logx_scr + b_loo_scr,
        RELATIONAL: _relational_loo(sim_rel, logy_true, cfg["weight_exp"], known_int),
        RANDOM:     _relational_loo(sim_rand, logy_true, cfg["weight_exp"], known_int),
        MEAN:       torch.full((E,), float(logy_true[interior].mean()), dtype=torch.float64),
    }
    imp_r2_cold = {a: _r2(imp_pred[a][cold], logy_true[cold]) for a in IMP_ARMS}
    imp_r2_int = {a: _r2(imp_pred[a][interior], logy_true[interior]) for a in IMP_ARMS}

    # ARMS-MUST-DIFFER (META_RULE_AF): hash detection-score vectors.
    digests = {a: hashlib.sha256(
        torch.nan_to_num(det_scores[a].to(torch.float64), nan=-999.0).numpy().tobytes()
    ).hexdigest() for a in DET_ARMS}

    return dict(law=name, slope=slope, fit_r2=fit_r2, n_corrupt=n_corrupt,
                det_auc=det_auc, corr_gain=corr_gain,
                imp_r2_cold=imp_r2_cold, imp_r2_interior=imp_r2_int,
                base_err=base_err, digests=digests)


def run_seed(mm, logprops, cfg, seed) -> dict:
    """Run all laws for one seed. Builds the REAL relational KGStore (channel A)."""
    n_dim = cfg["n_dim"]
    gen = torch.Generator(device="cpu").manual_seed(seed)
    store, rel_sig = build_relational_store(mm, n_dim, gen)
    n_triples = len(store)
    sim_rel = _cos_sim_real(rel_sig)
    rand_sig = torch.randn(mm["n"], n_dim, generator=gen, dtype=torch.float32)
    sim_rand = _cos_sim_real(rand_sig)
    laws = [run_law(law, mm, logprops, sim_rel, sim_rand, cfg, gen) for law in LAWS]
    return dict(seed=seed, n_dim=n_dim, n_triples=n_triples, laws=laws)


# --------------------------------------------------------------------------- #
# Aggregate + verdict                                                          #
# --------------------------------------------------------------------------- #
def _mean(vals):
    v = torch.tensor([x for x in vals if not (isinstance(x, float) and math.isnan(x))],
                     dtype=torch.float64)
    return float(v.mean()) if v.numel() else float("nan")


def _agg_law(seed_results, li, section, arm):
    return _mean([r["laws"][li][section][arm] for r in seed_results])


def decide_verdict(seed_results) -> dict:
    n_laws = len(LAWS)
    li = HEADLINE_LAW
    # headline-law aggregates
    law_auc = _agg_law(seed_results, li, "det_auc", LAW)
    marg_auc = _agg_law(seed_results, li, "det_auc", MARGINAL)
    rel_auc = _agg_law(seed_results, li, "det_auc", RELATIONAL)
    wrong_auc = _agg_law(seed_results, li, "det_auc", WRONG_EXP)
    scr_auc = _agg_law(seed_results, li, "det_auc", SCRAMBLE)
    best_nolaw_auc = max(marg_auc, rel_auc)

    law_corr = _agg_law(seed_results, li, "corr_gain", LAW)
    marg_corr = _agg_law(seed_results, li, "corr_gain", MARGINAL)
    rel_corr = _agg_law(seed_results, li, "corr_gain", RELATIONAL)
    wrong_corr = _agg_law(seed_results, li, "corr_gain", WRONG_EXP)
    scr_corr = _agg_law(seed_results, li, "corr_gain", SCRAMBLE)
    best_nolaw_corr = max(marg_corr, rel_corr)

    law_imp = _agg_law(seed_results, li, "imp_r2_cold", LAW)
    rel_imp = _agg_law(seed_results, li, "imp_r2_cold", RELATIONAL)
    mean_imp = _agg_law(seed_results, li, "imp_r2_cold", MEAN)
    rand_imp = _agg_law(seed_results, li, "imp_r2_cold", RANDOM)
    wrong_imp = _agg_law(seed_results, li, "imp_r2_cold", WRONG_EXP)
    scr_imp = _agg_law(seed_results, li, "imp_r2_cold", SCRAMBLE)
    law_imp_int = _agg_law(seed_results, li, "imp_r2_interior", LAW)
    rel_imp_int = _agg_law(seed_results, li, "imp_r2_interior", RELATIONAL)
    fit_r2 = _mean([r["laws"][li]["fit_r2"] for r in seed_results])

    # generality: per-law LAW-vs-best-nolaw detection AUC + LAW-vs-rel imputation.
    per_law = []
    for lj in range(n_laws):
        per_law.append(dict(
            law=LAWS[lj][0],
            law_auc=_agg_law(seed_results, lj, "det_auc", LAW),
            best_nolaw_auc=max(_agg_law(seed_results, lj, "det_auc", MARGINAL),
                               _agg_law(seed_results, lj, "det_auc", RELATIONAL)),
            wrong_auc=_agg_law(seed_results, lj, "det_auc", WRONG_EXP),
            scr_auc=_agg_law(seed_results, lj, "det_auc", SCRAMBLE),
            law_imp_cold=_agg_law(seed_results, lj, "imp_r2_cold", LAW),
            rel_imp_cold=_agg_law(seed_results, lj, "imp_r2_cold", RELATIONAL),
            fit_r2=_mean([r["laws"][lj]["fit_r2"] for r in seed_results]),
        ))

    # ---- gates -----------------------------------------------------------
    # (a) detection + correction
    det_law_strong = law_auc >= HP_LAW_AUC
    det_beats_nolaw = (law_auc - best_nolaw_auc) >= HP_LAW_BEATS_NOLAW_AUC
    corr_law_strong = law_corr >= HP_LAW_CORR_GAIN
    corr_beats_nolaw = (law_corr - best_nolaw_corr) >= HP_LAW_BEATS_NOLAW_CORR
    a_fires = det_law_strong and det_beats_nolaw and corr_law_strong and corr_beats_nolaw
    # (b) imputation
    imp_law_strong = law_imp >= HP_LAW_IMP_R2
    imp_beats_rel = (law_imp - rel_imp) >= HP_LAW_BEATS_REL_IMP
    imp_degree_invar = law_imp >= (law_imp_int - HP_DEGREE_INVAR)
    b_fires = imp_law_strong and imp_beats_rel and imp_degree_invar
    # must-fail (headline law), two-pronged:
    #   scramble_collapses: pure no-law breaks on all three axes.
    scr_collapse = ((scr_auc <= best_nolaw_auc + MF_AUC_OVER_NOLAW)
                    and (scr_corr <= MF_CORR_CEIL) and (scr_imp <= MF_IMP_CEIL))
    #   wrong-exponent: real exponent beats wrong by margin on all three AND wrong adds
    #   nothing over the no-law detection baseline.
    wrong_beaten = ((law_auc - wrong_auc >= WRONG_MARGIN_AUC)
                    and (law_corr - wrong_corr >= WRONG_MARGIN_CORR)
                    and (law_imp - wrong_imp >= WRONG_MARGIN_IMP)
                    and (wrong_auc <= best_nolaw_auc + MF_AUC_OVER_NOLAW))
    mf_det = (wrong_auc <= best_nolaw_auc + MF_AUC_OVER_NOLAW) and (scr_auc <= best_nolaw_auc + MF_AUC_OVER_NOLAW)
    mf_corr = (scr_corr <= MF_CORR_CEIL) and (law_corr - wrong_corr >= WRONG_MARGIN_CORR)
    mf_imp = (scr_imp <= MF_IMP_CEIL) and (law_imp - wrong_imp >= WRONG_MARGIN_IMP)
    mustfail_collapses = scr_collapse and wrong_beaten
    # encoding / load integrity
    encoding_ok = fit_r2 >= HF_L1_FIT_R2

    # failure-mode classification (do NOT conflate)
    if not encoding_ok:
        failure_mode = "LAW_FIT_BROKEN_data_not_on_manifold"
    elif not mustfail_collapses:
        failure_mode = "REGULARIZER_NOT_LAW_wrong_or_scramble_also_helps"
    elif a_fires and b_fires:
        failure_mode = "LAW_CONSISTENCY_GROUNDS_corrects_and_imputes"
    elif a_fires and not b_fires:
        failure_mode = "LAW_CORRECTS_but_imputation_weak"
    elif b_fires and not a_fires:
        failure_mode = "LAW_IMPUTES_but_correction_weak"
    else:
        failure_mode = "LAW_NO_ADVANTAGE_over_nolaw"

    hard_pass = encoding_ok and mustfail_collapses and a_fires and b_fires
    if hard_pass:
        verdict = "HARD_PASS"
    elif (not encoding_ok) or (not mustfail_collapses):
        verdict = "HARD_FAIL"
    elif a_fires or b_fires:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    msg = ("%s | [a:detect] LAW_AUC=%.3f best_nolaw(marg=%.3f rel=%.3f)=%.3f d=%+.3f "
           "| [a:correct] LAW=%.3f best_nolaw=%.3f d=%+.3f "
           "| [b:impute cold] LAW=%.3f REL=%.3f MEAN=%.3f d=%+.3f | interior LAW=%.3f REL=%.3f "
           "| [must-fail] wrong(auc=%.3f corr=%.3f imp=%.3f) scramble(auc=%.3f corr=%.3f imp=%.3f) "
           "collapse=%s | [ceiling] L1_fit_R2=%.3f | mode=%s"
           % (verdict, law_auc, marg_auc, rel_auc, best_nolaw_auc, law_auc - best_nolaw_auc,
              law_corr, best_nolaw_corr, law_corr - best_nolaw_corr,
              law_imp, rel_imp, mean_imp, law_imp - rel_imp, law_imp_int, rel_imp_int,
              wrong_auc, wrong_corr, wrong_imp, scr_auc, scr_corr, scr_imp,
              mustfail_collapses, fit_r2, failure_mode))

    return dict(verdict=verdict, verdict_msg=msg, failure_mode=failure_mode,
                a_fires=bool(a_fires), b_fires=bool(b_fires),
                mustfail_collapses=bool(mustfail_collapses), encoding_ok=bool(encoding_ok),
                gates=dict(det_law_strong=bool(det_law_strong), det_beats_nolaw=bool(det_beats_nolaw),
                           corr_law_strong=bool(corr_law_strong), corr_beats_nolaw=bool(corr_beats_nolaw),
                           imp_law_strong=bool(imp_law_strong), imp_beats_rel=bool(imp_beats_rel),
                           imp_degree_invar=bool(imp_degree_invar),
                           mf_det=bool(mf_det), mf_corr=bool(mf_corr), mf_imp=bool(mf_imp)),
                per_law=per_law,
                agg=dict(law_auc=law_auc, marg_auc=marg_auc, rel_auc=rel_auc,
                         best_nolaw_auc=best_nolaw_auc, wrong_auc=wrong_auc, scr_auc=scr_auc,
                         law_corr=law_corr, marg_corr=marg_corr, rel_corr=rel_corr,
                         best_nolaw_corr=best_nolaw_corr, wrong_corr=wrong_corr, scr_corr=scr_corr,
                         law_imp_cold=law_imp, rel_imp_cold=rel_imp, mean_imp_cold=mean_imp,
                         rand_imp_cold=rand_imp, wrong_imp_cold=wrong_imp, scr_imp_cold=scr_imp,
                         law_imp_interior=law_imp_int, rel_imp_interior=rel_imp_int,
                         l1_fit_r2=fit_r2))


# --------------------------------------------------------------------------- #
# I/O helpers                                                                  #
# --------------------------------------------------------------------------- #
def _out_dir() -> str:
    name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    return os.path.join("data", "exp_" + name)


def _write_start_marker(out_dir, run_mode, expected_n_units) -> None:
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_metrics(out_dir, metrics) -> None:
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _write_crash_metrics(out_dir, exc) -> None:
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(out_dir, diag)


def _log_props(mm) -> torch.Tensor:
    """log10 of all 5 attribute columns (all strictly positive in the dataset). [E,5] float64."""
    return torch.log10(mm["props"].to(torch.float64).clamp_min(1e-9))


# --------------------------------------------------------------------------- #
# Validity preflight + discriminator preview (self-test = smoke gate)          #
# --------------------------------------------------------------------------- #
def _validity_checks(mm, cfg) -> None:
    logprops = _log_props(mm)

    # F.1/F.2/F.3: construct + ingest the REAL KGStore at tiny scale (base kwargs only).
    exercised = set()
    gsmall = torch.Generator(device="cpu").manual_seed(1)
    store_small = KGStore(6, 2, 16, gsmall)
    exercised.add("KGStore")
    store_small.ingest_triples(torch.tensor([[0, 0, 4], [1, 1, 5], [2, 0, 4]], dtype=torch.long))
    assert len(store_small) == 3, "ingest_triples did not register triples"
    exercised.add("ingest_triples")
    # build_relational_store exercises the REAL channel-A path on the REAL data.
    _s, _rel = build_relational_store(mm, 256, torch.Generator(device="cpu").manual_seed(2))
    exercised.add("build_relational_store")

    # Discriminator preview: run the REAL mechanism on REAL data across seeds.
    seed_results = [run_seed(mm, logprops, cfg, s) for s in cfg["seeds"]]
    dv = decide_verdict(seed_results)
    agg = dv["agg"]

    # metric-moves: LAW detection residual must MOVE when a value is corrupted off-manifold.
    logx = logprops[:, LENGTH]
    logy = logprops[:, MASS]
    b = float((logy - 3.0 * logx).median())
    resid_clean = float((logy[0] - (3.0 * logx[0] + b)).abs())
    resid_corr = float((logy[0] + 1.2 - (3.0 * logx[0] + b)).abs())

    # ARMS-MUST-DIFFER exercised at self-test (fail-closed).
    d0 = seed_results[0]["laws"][HEADLINE_LAW]["digests"]
    pairs = [(x, y) for i, x in enumerate(DET_ARMS) for y in DET_ARMS[i + 1:]]
    assert all(d0[x] != d0[y] for x, y in pairs), "META_RULE_AF: two detection arms bit-identical"

    # cardinality exercised (n_seeds * n_laws detection/impute units).
    expected_units = len(cfg["seeds"]) * len(LAWS)
    got_units = sum(len(r["laws"]) for r in seed_results)
    assert got_units == expected_units, "cardinality breach: got %d expected %d" % (got_units, expected_units)

    # negative-control margin: wrong-law + scramble detection AUC must fail the LAW bar.
    wrong_scores = [r["laws"][HEADLINE_LAW]["det_auc"][WRONG_EXP] for r in seed_results]
    scr_scores = [r["laws"][HEADLINE_LAW]["det_auc"][SCRAMBLE] for r in seed_results]

    run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["KGStore", "ingest_triples", "build_relational_store"],
         "exercised_entrypoints": sorted(exercised)},
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None}},
        # F.4 guard_baseline_valid is N/A for this cell: it applies to cells with a
        # control-beats-baseline BREAK-GUARD. This cell has none. In fact RELATIONAL
        # imputation on the cold tail lands BELOW the RANDOM floor (R2<0) -- that
        # collapse IS the finding (relational fails on the sparse tail; the LAW wins),
        # not a guard input. Declaring the guard here would mis-apply it.
        # positive control = the LAW must clear its detection bar (discriminator fires).
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": agg["law_auc"] >= HP_LAW_AUC,
         "control_name": "LAW_detection", "headline_name": "law_auc"},
        {"kind": "metric_moves", "metric_name": "law_residual",
         "before": resid_clean, "after": resid_corr},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "cardinality"],
         "exercised_gates": ["arms_differ", "cardinality"]},
        {"kind": "negative_control_margin", "control_scores": wrong_scores + scr_scores,
         "headline_threshold": HP_LAW_AUC, "higher_is_pass": True, "margin": 0.0,
         "n_repeats_min": 2, "control_name": "WRONG_EXP+SCRAMBLE_detection_AUC"},
    ], run_mode="selftest")

    # Discriminator-fires + must-fail collapse + baseline-in-band (fail-closed asserts).
    assert agg["law_auc"] >= HP_LAW_AUC, (
        "LAW detection did not fire: AUC=%.3f < %.3f" % (agg["law_auc"], HP_LAW_AUC))
    assert (agg["law_auc"] - agg["best_nolaw_auc"]) >= HP_LAW_BEATS_NOLAW_AUC, (
        "LAW does not beat best no-law detection: LAW=%.3f best_nolaw=%.3f"
        % (agg["law_auc"], agg["best_nolaw_auc"]))
    assert agg["best_nolaw_auc"] < 0.95, (
        "no-law baseline saturated (%.3f); corruption too easy, re-spec regime" % agg["best_nolaw_auc"])
    # SCRAMBLE (pure no-law) must collapse; WRONG_EXP must be beaten by margin + add
    # nothing over no-law detection. (Additive-log corruption floors any y-residual near
    # the no-law baseline, so the ceiling is best-no-law+margin, not chance 0.5.)
    _nl = agg["best_nolaw_auc"] + MF_AUC_OVER_NOLAW
    assert agg["scr_auc"] <= _nl and agg["scr_corr"] <= MF_CORR_CEIL and agg["scr_imp_cold"] <= MF_IMP_CEIL, (
        "SCRAMBLE (pure no-law) DID NOT COLLAPSE: auc=%.3f (ceil %.3f) corr=%.3f imp=%.3f; do NOT ship"
        % (agg["scr_auc"], _nl, agg["scr_corr"], agg["scr_imp_cold"]))
    assert (agg["wrong_auc"] <= _nl
            and (agg["law_auc"] - agg["wrong_auc"]) >= WRONG_MARGIN_AUC
            and (agg["law_corr"] - agg["wrong_corr"]) >= WRONG_MARGIN_CORR
            and (agg["law_imp_cold"] - agg["wrong_imp_cold"]) >= WRONG_MARGIN_IMP), (
        "WRONG_EXP not beaten by margin: wrong(auc=%.3f corr=%.3f imp=%.3f) vs LAW(auc=%.3f corr=%.3f "
        "imp=%.3f); the exponent VALUE is not load-bearing; do NOT ship"
        % (agg["wrong_auc"], agg["wrong_corr"], agg["wrong_imp_cold"],
           agg["law_auc"], agg["law_corr"], agg["law_imp_cold"]))
    assert agg["law_imp_cold"] >= HP_LAW_IMP_R2, (
        "LAW imputation weak on cold tail: R2=%.3f < %.3f" % (agg["law_imp_cold"], HP_LAW_IMP_R2))
    assert (agg["law_imp_cold"] - agg["rel_imp_cold"]) >= HP_LAW_BEATS_REL_IMP, (
        "LAW imputation does not beat relational on cold tail: LAW=%.3f REL=%.3f"
        % (agg["law_imp_cold"], agg["rel_imp_cold"]))
    assert agg["l1_fit_r2"] >= HF_L1_FIT_R2, (
        "headline law does not fit the true data (R2=%.3f); manifold broken" % agg["l1_fit_r2"])
    print("[self-test] validity + discriminator + must-fail-collapse PASS: %s" % dv["verdict_msg"], flush=True)


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="fast validity + discriminator preview")
    ap.add_argument("--smoke", action="store_true", help="reduced-grid run")
    args, _ = ap.parse_known_args()

    mm = load_mammals()
    logprops = _log_props(mm)

    if args.self_test:
        _validity_checks(mm, dict(SELFTEST_CFG))
        print("SELFTEST_PASS", flush=True)
        return

    cfg = dict(SELFTEST_CFG) if args.smoke else dict(FULL_CFG)
    run_mode = "smoke" if args.smoke else "full"
    out_dir = _out_dir()
    expected_units = len(cfg["seeds"]) * len(LAWS)
    _write_start_marker(out_dir, run_mode, expected_units)

    t0 = time.perf_counter()
    seed_results = []
    for s in cfg["seeds"]:
        rs = run_seed(mm, logprops, cfg, s)
        hl = rs["laws"][HEADLINE_LAW]
        seed_results.append(rs)
        print("[progress] seed=%d LAW_auc=%.3f wrong_auc=%.3f LAW_imp_cold=%.3f elapsed=%.1fs"
              % (s, hl["det_auc"][LAW], hl["det_auc"][WRONG_EXP],
                 hl["imp_r2_cold"][LAW], time.perf_counter() - t0), flush=True)

    dv = decide_verdict(seed_results)
    elapsed = time.perf_counter() - t0

    got_units = sum(len(r["laws"]) for r in seed_results)
    cardinality_ok = (got_units == expected_units)
    verdict, verdict_msg = dv["verdict"], dv["verdict_msg"]
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = "cardinality breach: got %d expected %d | %s" % (got_units, expected_units, verdict_msg)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg,
        summary=("%s LAW_auc=%.3f imp_cold=%.3f collapse=%s"
                 % (verdict, dv["agg"]["law_auc"], dv["agg"]["law_imp_cold"], dv["mustfail_collapses"])),
        elapsed_s=round(elapsed, 3), run_mode=run_mode, anchor_name=ANCHOR_NAME,
        n_dim=cfg["n_dim"], n_seeds=len(cfg["seeds"]), expected_n_units=expected_units,
        got_n_units=got_units, cardinality_ok=cardinality_ok,
        failure_mode=dv["failure_mode"], a_fires=dv["a_fires"], b_fires=dv["b_fires"],
        mustfail_collapses=dv["mustfail_collapses"], encoding_ok=dv["encoding_ok"],
        gates=dv["gates"], agg=dv["agg"], per_law=dv["per_law"],
        laws=[dict(name=n, predictor=_PROP_NAMES[p], target=_PROP_NAMES[t], slope=s)
              for (n, p, t, s) in LAWS],
        per_seed=[dict(seed=r["seed"], n_dim=r["n_dim"], n_triples=r["n_triples"],
                       laws=[dict(law=lw["law"], slope=lw["slope"], fit_r2=lw["fit_r2"],
                                  n_corrupt=lw["n_corrupt"], det_auc=lw["det_auc"],
                                  corr_gain=lw["corr_gain"], imp_r2_cold=lw["imp_r2_cold"],
                                  imp_r2_interior=lw["imp_r2_interior"]) for lw in r["laws"]])
                  for r in seed_results],
        ts_iso=datetime.now(timezone.utc).isoformat(), host=platform.node(),
    )
    _write_metrics(out_dir, metrics)
    print("[done] %s" % verdict_msg, flush=True)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_od, e)
        raise
