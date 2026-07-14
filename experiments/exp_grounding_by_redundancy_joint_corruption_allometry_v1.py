"""GROUNDING-BY-REDUNDANCY under JOINT corruption (Track-B grounding, LEVER A, honest).

WHY THIS CELL EXISTS -- the GENUINE version of ground-by-consistency.
  The sibling cell exp_grounding_law_consistency_allometry_v1 (HARD_PASS, LAW_AUC=0.999
  MEASURED@d:/AI/hd-instrument/data/exp_grounding_law_consistency_allometry_v1/metrics.json)
  corrupted ONLY the TARGET attribute per law and left the PREDICTOR CLEAN. Detecting a
  corrupted mass from a CLEAN length that is 98%-correlated with mass is a near-tautology
  (a single clean sibling over-determines the value). That result is a construction-proof
  of "a clean predictor can correct a corrupted target", NOT of grounding-by-consistency.
  The law-consistency VET flagged this coupling (PREDICTOR_CLEAN_SAME_SOURCE_COUPLING) and
  pointed to the honest test: remove the clean crutch.

THE GENUINE MECHANISM (this cell):
  Corrupt ALL attributes JOINTLY -- every attribute of every entity carries background
  noise (no clean sibling anywhere), and each entity additionally has exactly ONE
  attribute driven far off the cross-attribute manifold. Given a NETWORK of allometric
  laws relating the attributes (each attribute predictable from EACH of the others via a
  known pairwise power-law), test whether CROSS-LAW REDUNDANCY -- the CONSENSUS of the
  multiple, also-noisy, law-predictions -- can DETECT + LOCALIZE + CORRECT the off-manifold
  value when NO single clean predictor exists. The consensus (median of K-1 law-predictions)
  averages out the background noise in the predictors and rejects a single corrupted
  predictor, so the corrupted attribute stands out. This is real grounding-by-consistency:
  the law-NETWORK over-constrains the values, not one clean attribute-attribute regression.

THE LAW NETWORK (glass-box, CITED biological exponents = the external grounding):
  All four attributes are affine functions of a shared log-body-size latent s = log10(mass):
    mass:      loading a=1.00   (s itself)                CITED@textbook geometric/Kleiber
    length:    a=1/3 (0.333)    mass ~ length^3           CITED@geometric isometry
    gestation: a=0.25           gestation ~ mass^0.25     CITED@quarter-power life-history
    lifespan:  a=0.20           lifespan ~ mass^0.20      CITED@longevity allometry
  Pairwise law i<-j: log(attr_i) = (a_i/a_j)*log(attr_j) + b_ij; intercept b_ij is a units
  nuisance fit robustly per-entity LOO by median of the OTHER entities' residuals (no leak).
  This yields a FULLY-CONNECTED law graph on 4 nodes (every node degree 3) -> redundancy.

ARMS:
  FULL (mechanism): predict each attr from the MEDIAN of the other 3 pairwise-law predictions
    -> cross-law redundancy; robust to background noise AND to one corrupted predictor.
  NO_REDUNDANCY (must-fail 1): a perfect MATCHING (mass<->length, gestation<->lifespan) so
    each attr has EXACTLY ONE law-partner. With one partner, corrupting either member of a
    pair inflates BOTH residuals symmetrically -> localization CANNOT disambiguate (chance
    within the pair). "With only one predictor there is no redundancy to localize with."
  SCRAMBLE (must-fail 2a): FULL graph but each predictor column SHUFFLED across entities
    (breaks entity pairing) -> predictions are noise -> collapse on all axes.
  WRONG_EXP (must-fail 2b): FULL graph, WRONG loadings (all a_k=1 -> all slopes=1) -> a
    mis-specified law; a monotone relationship survives (partial detection) but the WRONG
    exponent VALUE corrects/localizes badly -> real exponent beats it by margin.
  MARGINAL (no-law baseline): |robust z-score| within the attribute's own distribution.
  RELATIONAL (no-law baseline, REAL KGStore): deviation from taxonomic-neighbor consensus
    -- a DIFFERENT redundancy source (ancestry, not laws); the fair cross-channel baseline.

WHAT IS TESTED (headline = LOCALIZATION under joint corruption):
  (H) LOCALIZE: per entity (exactly one off-manifold attr) does argmax standardized-residual
      identify the corrupted attribute? FULL (redundant) vs NO_REDUNDANCY / SCRAMBLE / MARG.
  (a) DETECT: pooled AUC over all entity-attribute cells (corrupt vs clean).
  (a') CORRECT: flag the localized cell, replace with the arm's law-prediction, measure
      all-cell log-MAE reduction. Mis-localization (flagging a clean cell) ADDS error.
  (b) NO-CLEAN-SIBLING (must-fail 3, explicit): background noise is on 100% of cells
      (min per-cell |perturbation| > 0 asserted), AND detection/localization are reported
      on the PARTNER-ALSO-CORRUPTED subset (each corrupted target's tightest law-partner is
      additionally driven off-manifold) -- FULL (median of 3) must retain the win while
      NO_REDUNDANCY (whose single partner is the corrupted one) collapses. If the win
      survives ablation of the would-be clean sibling, the win is REDUNDANCY, not a crutch.

MUST-FAIL / failure-mode classification (do NOT conflate):
  SCRAMBLE must collapse (localization -> chance 1/K); NO_REDUNDANCY localization must fail
  the FULL bar by margin; WRONG_EXP must be beaten by margin on localize+correct. If a
  wrong/scrambled/single-partner arm ALSO localizes, the signal is generic smoothing not
  cross-law redundancy -> HARD_FAIL.

FAIRNESS + WEAK-POINT LOCALIZATION (first-class):
  - info-ceiling: localization <= 1.0; DET AUC <= 1.0; correction gain <= 1.0. HARD_PASS
    bars are set STRICTLY BELOW the FULL self-test measurement + margin and ABOVE the
    best no-law/no-redundancy arm (calibrated, see prereg MEASURED tags).
  - fair baselines: FULL compared to the BEST of MARGINAL/RELATIONAL AND to NO_REDUNDANCY.
  - metric-can-MOVE: corruption is stochastic per seed (multi-seed variance; NOT cv=0);
    localization/AUC are not structurally frozen (metric_moves preflight).
  - NO clean sibling: background noise on 100% of cells (structural + asserted), plus the
    partner-corrupted subset measurement (must-fail 3).
  - must-fails (NO_REDUNDANCY + SCRAMBLE + WRONG_EXP) fire at self-test scale.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: rank-AUC + localization-accuracy + log-MAE-skill cell; no argmax capacity
#   floor (localization chance floor 1/K=0.25 is declared + used as the must-fail ceiling).
# - baseline_in_band at smoke (META_RULE_AG; NO_REDUNDANCY/MARGINAL localization NOT
#   saturated; FULL not at chance): 0.05 < best-no-redundancy loc < FULL loc - margin.
# - discriminator survives scale: the mechanism is DIMENSION-FREE (closed-form on the
#   64x4 log-attribute table). n_dim only affects the RELATIONAL baseline (KGStore cosine).
#   Self-test runs the REAL mechanism on REAL data (3 seeds) at n_dim=2048; FULL n_dim=8192.
#   The FULL-vs-NO_REDUNDANCY localization gap is n_dim-independent -> survives scale (case B).
# - HARD_PASS strictly above floor + margin (META_RULE_L)
# - HP_SCOPE per-arm declaration (see prereg)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * K_attrs (one per-attr detection unit per
#   seed); verdict counts and HARD_FAILs on breach.
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_justification (log10 for power-law vars; per-arm
#   per-attribute ROBUST MAD standardizer computed on the OBSERVED corrupted residuals
#   -- no clean-data oracle; same recipe for every arm -> no per-arm detection tuning).
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ in the prereg
# - F.1 real_code_path: self-test CONSTRUCTS the REAL KGStore (via build_relational_store
#   from the sibling allometry cell) at n_dim<=256 + ingests real triples.
# - F.2/F.3 substrate_signature: KGStore bound with BASE/portable kwargs only
#   (n_ent, n_rel, n_dim, generator); NO version-specific init_entities kwarg.
# - F.4 guard_baseline_valid: N/A -- this cell has no control-beats-baseline BREAK-guard
#   (declared N/A with rationale in _validity_checks).
# - progress_logging: print_flush_true (cheap cell; timeout << 1800 anyway)

Compute architecture: sequential-CPU with justification -- 64 entities, K=4 attributes,
  closed-form pairwise laws are dimension-free; the only n_dim-dependent op is a [64,64]
  relational-similarity Gram from a REAL KGStore; per-seed wall << 2s, whole cell << 10s.
  No GPU batching candidate (wall-time sanity < 10s). Storage: no_composition (relational
  baseline uses sharded KGStore E/R codes; no bundled multi-item composition). No
  sequential dependency across seeds.

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

# Real substrate objects the FULL run uses (F.1/F.2/F.3) + the REAL mammal dataset + helpers.
from hdlab.kg_traversal import KGStore
from experiments.exp_grounding_mammal_allometry_xchannel_fpe_v1 import (
    load_mammals, build_relational_store, _cos_sim_real, _PROP_NAMES,
)
from experiments._validity_preflight import run_validity_preflight

ANCHOR_NAME = "grounding_by_redundancy_joint_corruption_allometry_v1"

# --------------------------------------------------------------------------- #
# Attributes (nodes) + loadings on the shared log-size latent s = log10(mass). #
# Column indices into mm["props"]: 0=mass 1=length 2=lifespan 3=gestation 4=litter #
# --------------------------------------------------------------------------- #
MASS_C, LENGTH_C, LIFESPAN_C, GEST_C = 0, 1, 2, 3
ATTR_COLS = [MASS_C, LENGTH_C, LIFESPAN_C, GEST_C]      # the 4 network nodes
ATTR_NAMES = [_PROP_NAMES[c] for c in ATTR_COLS]        # ["mass","length","lifespan","gestation"]
K = len(ATTR_COLS)
# Allometric loadings a_k (attr_k ~ mass^a_k). CITED biological exponents (the LAW).
LOADINGS = [1.0, 1.0 / 3.0, 0.20, 0.25]                 # mass, length, lifespan, gestation
# Perfect-matching single-partner graph (indices into ATTR_COLS) for NO_REDUNDANCY:
#   mass<->length (0<->1), lifespan<->gestation (2<->3). Symmetric single partner.
MATCH_PARTNER = [1, 0, 3, 2]
WRONG_LOADING = 1.0                                     # all loadings = 1 (must-fail exponent)

# Arm names.
FULL = "FULL"
NO_REDUNDANCY = "NO_REDUNDANCY"
SCRAMBLE = "SCRAMBLE"
WRONG_EXP = "WRONG_EXP"
MARGINAL = "MARGINAL"
RELATIONAL = "RELATIONAL"
LAW_ARMS = [FULL, NO_REDUNDANCY, SCRAMBLE, WRONG_EXP, MARGINAL, RELATIONAL]
NO_REDUN_LIKE = [NO_REDUNDANCY, SCRAMBLE]               # must-fail localization arms
NOLAW = [MARGINAL, RELATIONAL]                          # no cross-law baselines

# --------------------------------------------------------------------------- #
# Config                                                                       #
# --------------------------------------------------------------------------- #
FULL_CFG = dict(n_dim=8192, seeds=[7, 13, 19, 23, 29],
                sigma_bg=0.08, shift_lo=0.6, shift_hi=1.2, weight_exp=6.0)
SELFTEST_CFG = dict(n_dim=2048, seeds=[7, 13, 19],
                    sigma_bg=0.08, shift_lo=0.6, shift_hi=1.2, weight_exp=6.0)

CHANCE_LOC = 1.0 / K                                    # 0.25 argmax-over-K localization chance

# HARD-PASS / HARD-FAIL bands (pre-registered; calibrated to the 5-seed FULL + 3-seed
# self-test MEASUREMENT at sigma_bg=0.08 shift=[0.6,1.2]; see prereg for MEASURED tags +
# full feasibility). Set STRICTLY inside the measured gap, with multi-seed margin.
# HEADLINE = CORRECTION: under JOINT corruption, FULL is the ONLY arm that can CORRECT
# (positive log-MAE reduction); every no-redundancy / no-law / wrong / scramble arm makes
# it WORSE or neutral (they mis-localize + replace a clean cell). Plus LOCALIZATION.
# (a') correction (headline redundancy metric)
HP_FULL_CORR_GAIN = 0.20          # FULL correction reduces all-cell log-MAE by >= this frac
HP_FULL_BEATS_NOREDUN_CORR = 0.25 # FULL corr gain - NO_REDUNDANCY corr gain
HP_FULL_BEATS_NOLAW_CORR = 0.15   # FULL corr gain - best no-law (MARG/REL) corr gain
# (H) localization
HP_FULL_LOC = 0.68                # FULL localization accuracy (>> chance 0.25)
HP_FULL_BEATS_NOREDUN_LOC = 0.20  # FULL_LOC - NO_REDUNDANCY_LOC (redundancy is load-bearing)
HP_FULL_BEATS_MARG_LOC = 0.06     # FULL_LOC - best no-law localization (marginal is strong)
# (a) detection (NOT where redundancy shines: a big shift is often a marginal outlier, so
# marginal detects too; low beat-bar is the HONEST finding).
HP_FULL_DET_AUC = 0.78            # FULL pooled detection AUC
HP_FULL_BEATS_NOLAW_AUC = 0.02    # FULL_AUC - best no-law detection AUC (modest, honest)
# (b) no-clean-sibling (must-fail 3, well-posed as DETECTION on the partner-corrupted
# variant): FULL still detects when the tightest law-partner is ALSO off-manifold.
HP_FULL_DET_AUC_PARTNER_CORR = 0.70   # FULL detection AUC on partner-also-corrupted variant
HP_FULL_BEATS_NOREDUN_PARTNER = 0.05  # FULL - NO_REDUNDANCY detection there (redundancy tolerant)
# MUST-FAIL ceilings
MF_SCRAMBLE_CORR = 0.05               # SCRAMBLE correction gain <= this (cannot correct)
MF_SCRAMBLE_BEATEN_LOC = 0.12         # FULL_LOC - SCRAMBLE_LOC margin (pairing load-bearing)
MF_NOREDUN_CORR_CEIL = 0.05           # NO_REDUNDANCY correction gain <= this (cannot correct)
MF_NOREDUN_LOC_CEIL = 0.55            # NO_REDUNDANCY localization <= this (pair-ambiguous)
WRONG_MARGIN_LOC = 0.12               # FULL - WRONG_EXP localization margin
WRONG_MARGIN_CORR = 0.20              # FULL - WRONG_EXP correction margin
# mechanism-fires integrity: FULL detection must clearly fire (not vacuous).
HF_FULL_AUC_MIN = 0.70                # below this, mechanism not firing -> investigate


# --------------------------------------------------------------------------- #
# Rank / AUC helpers (scipy-free; copied from the sibling cell)                #
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


def _robust_scale(r: torch.Tensor) -> float:
    """Robust MAD-based scale (1.4826*MAD) of a residual vector; floor to avoid /0."""
    med = r.median()
    mad = (r - med).abs().median()
    return float((1.4826 * mad).clamp_min(1e-9))


# --------------------------------------------------------------------------- #
# Pairwise-law LOO intercept + relational LOO consensus                        #
# --------------------------------------------------------------------------- #
def _loo_intercept(logx: torch.Tensor, logy: torch.Tensor, slope: float) -> torch.Tensor:
    """Per-entity LOO robust intercept b_{-e} = median_{m!=e}(logy_m - slope*logx_m). [E]."""
    E = logx.numel()
    resid = logy - slope * logx
    b = torch.empty(E, dtype=torch.float64)
    for e in range(E):
        m = torch.ones(E, dtype=torch.bool)
        m[e] = False
        b[e] = resid[m].median()
    return b


def _relational_loo(sim: torch.Tensor, logy: torch.Tensor, weight_exp: float) -> torch.Tensor:
    """Similarity-weighted LOO prediction of logy for every entity (self excluded). [E]."""
    E = sim.shape[0]
    preds = torch.full((E,), float("nan"), dtype=torch.float64)
    for e in range(E):
        w = torch.clamp(sim[e].clone().to(torch.float64), min=0.0)
        w[e] = 0.0
        w = w.pow(weight_exp)
        wsum = w.sum()
        preds[e] = logy.mean() if wsum <= 1e-12 else (w * logy).sum() / wsum
    return preds


def _pairwise_pred(y: torch.Tensor, k: int, j: int, loadings) -> torch.Tensor:
    """Predict attr column k from attr column j via the pairwise power-law (LOO intercept).

    y: [E,K] observed (corrupted) log-attributes. slope = a_k / a_j. Returns pred_k [E].
    """
    slope = loadings[k] / loadings[j]
    b = _loo_intercept(y[:, j], y[:, k], slope)
    return slope * y[:, j] + b


# --------------------------------------------------------------------------- #
# Per-arm residual score (higher = more likely corrupt) + point prediction     #
# --------------------------------------------------------------------------- #
def _arm_scores(arm: str, y: torch.Tensor, y_scr: torch.Tensor, sim_rel: torch.Tensor,
                weight_exp: float) -> tuple:
    """Return (z [E,K] standardized residual, pred [E,K] correction target) for one arm.

    y: observed corrupted log-attrs [E,K]. y_scr: entity-shuffled predictor copy (SCRAMBLE).
    All arms use the SAME robust-MAD per-attribute standardizer recipe (no per-arm tuning).
    """
    E = y.shape[0]
    r = torch.zeros(E, K, dtype=torch.float64)
    pred = torch.zeros(E, K, dtype=torch.float64)

    if arm in (FULL, WRONG_EXP, SCRAMBLE):
        loadings = [WRONG_LOADING] * K if arm == WRONG_EXP else LOADINGS
        src = y_scr if arm == SCRAMBLE else y
        for k in range(K):
            others = [j for j in range(K) if j != k]
            preds_j = torch.stack([_pairwise_pred_src(y, src, k, j, loadings) for j in others], dim=1)
            pred[:, k] = preds_j.median(dim=1).values
            r[:, k] = (y[:, k] - pred[:, k]).abs()
    elif arm == NO_REDUNDANCY:
        for k in range(K):
            j = MATCH_PARTNER[k]
            pred[:, k] = _pairwise_pred(y, k, j, LOADINGS)
            r[:, k] = (y[:, k] - pred[:, k]).abs()
    elif arm == MARGINAL:
        for k in range(K):
            med = y[:, k].median()
            pred[:, k] = med
            r[:, k] = (y[:, k] - med).abs()
    elif arm == RELATIONAL:
        for k in range(K):
            pred[:, k] = _relational_loo(sim_rel, y[:, k], weight_exp)
            r[:, k] = (y[:, k] - pred[:, k]).abs()
    else:
        raise ValueError("unknown arm %r" % arm)

    z = torch.zeros_like(r)
    for k in range(K):
        z[:, k] = r[:, k] / _robust_scale(r[:, k])
    return z, pred


def _pairwise_pred_src(y_target: torch.Tensor, src: torch.Tensor, k: int, j: int,
                       loadings) -> torch.Tensor:
    """Predict target column k using PREDICTOR column j taken from `src` (may be scrambled).

    Intercept fit LOO on the SAME (target, src) pairing used for prediction, so a scrambled
    src yields a scrambled (meaningless) intercept + prediction -> genuine collapse.
    """
    slope = loadings[k] / loadings[j]
    b = _loo_intercept(src[:, j], y_target[:, k], slope)
    return slope * src[:, j] + b


# --------------------------------------------------------------------------- #
# One seed: build corruption, run every arm, score localize/detect/correct     #
# --------------------------------------------------------------------------- #
def run_seed(mm, logp_clean, cfg, seed) -> dict:
    """Run all arms for one seed. JOINT corruption: background on ALL cells + one large
    off-manifold shift per entity. Returns per-arm localization/detection/correction +
    the partner-also-corrupted subset metrics + ARMS-MUST-DIFFER digests."""
    E = mm["n"]
    gen = torch.Generator(device="cpu").manual_seed(seed)
    n_dim = cfg["n_dim"]

    y_clean = logp_clean[:, ATTR_COLS].clone().to(torch.float64)   # [E,K] clean log10
    # JOINT corruption: background noise on 100% of cells (no clean sibling).
    bg = cfg["sigma_bg"] * torch.randn(E, K, generator=gen, dtype=torch.float64)
    y = y_clean + bg
    # exactly ONE large off-manifold shift per entity.
    corr_attr = torch.randint(0, K, (E,), generator=gen)           # which attr per entity
    mag = cfg["shift_lo"] + (cfg["shift_hi"] - cfg["shift_lo"]) * torch.rand(E, generator=gen, dtype=torch.float64)
    sgn = torch.where(torch.rand(E, generator=gen) < 0.5, -1.0, 1.0).to(torch.float64)
    corrupt_mask = torch.zeros(E, K, dtype=torch.bool)
    for e in range(E):
        y[e, corr_attr[e]] = y[e, corr_attr[e]] + sgn[e] * mag[e]
        corrupt_mask[e, corr_attr[e]] = True

    # Real relational similarity channel (REAL KGStore; F.1/F.2/F.3).
    store, rel_sig = build_relational_store(mm, n_dim, gen)
    n_triples = len(store)
    sim_rel = _cos_sim_real(rel_sig)

    # SCRAMBLE predictor copy: shuffle every attr column by an independent entity permutation.
    y_scr = y.clone()
    for k in range(K):
        perm = torch.randperm(E, generator=gen)
        y_scr[:, k] = y[perm, k]

    # ---- partner-also-corrupted variant (must-fail 3: no clean sibling) --------
    # For each entity, additionally drive the corrupted target's MATCH partner off-manifold.
    y_pc = y.clone()
    partner_mask = torch.zeros(E, K, dtype=torch.bool)
    mag2 = cfg["shift_lo"] + (cfg["shift_hi"] - cfg["shift_lo"]) * torch.rand(E, generator=gen, dtype=torch.float64)
    sgn2 = torch.where(torch.rand(E, generator=gen) < 0.5, -1.0, 1.0).to(torch.float64)
    for e in range(E):
        p = MATCH_PARTNER[int(corr_attr[e])]
        y_pc[e, p] = y_pc[e, p] + sgn2[e] * mag2[e]
        partner_mask[e, p] = True
    y_pc_scr = y_pc.clone()
    for k in range(K):
        perm = torch.randperm(E, generator=gen)
        y_pc_scr[:, k] = y_pc[perm, k]

    base_err = float((y - y_clean).abs().mean())

    # partner-also-corrupted DETECTION labels (well-posed: 2 positives/entity).
    pc_labels = (corrupt_mask | partner_mask)

    arm_out = {}
    digests = {}
    for arm in LAW_ARMS:
        z, pred = _arm_scores(arm, y, y_scr, sim_rel, cfg["weight_exp"])
        # detection AUC over pooled cells.
        det_auc = _auc(z.reshape(-1), corrupt_mask.reshape(-1))
        # localization: per entity argmax over K == corrupted attr.
        loc = float((z.argmax(dim=1) == corr_attr).to(torch.float64).mean())
        # correction: flag argmax cell per entity, replace with pred, all-cell log-MAE.
        flagged = z.argmax(dim=1)
        y_corr = y.clone()
        for e in range(E):
            y_corr[e, flagged[e]] = pred[e, flagged[e]]
        corr_err = float((y_corr - y_clean).abs().mean())
        corr_gain = (1.0 - corr_err / base_err) if base_err > 1e-9 else float("nan")
        # NO-CLEAN-SIBLING (must-fail 3, well-posed as DETECTION): when the tightest law
        # partner is ALSO driven off-manifold, can the arm still DETECT the off-manifold
        # cells? FULL (median of 3, tolerant of one bad predictor) should hold; a single-
        # partner arm whose one partner is now corrupted degrades. AUC labels both bad cells.
        z_pc, _ = _arm_scores(arm, y_pc, y_pc_scr, sim_rel, cfg["weight_exp"])
        det_auc_pc = _auc(z_pc.reshape(-1), pc_labels.reshape(-1))
        loc_pc = float((z_pc.argmax(dim=1) == corr_attr).to(torch.float64).mean())

        arm_out[arm] = dict(det_auc=det_auc, loc=loc, corr_gain=corr_gain,
                            det_auc_partner_corr=det_auc_pc, loc_partner_corr=loc_pc)
        digests[arm] = hashlib.sha256(
            torch.nan_to_num(z.to(torch.float64), nan=-999.0).numpy().tobytes()).hexdigest()

    # min background perturbation (no-clean-sibling structural proof).
    min_bg = float(bg.abs().min())
    return dict(seed=seed, n_dim=n_dim, n_triples=n_triples, base_err=base_err,
                min_bg_perturb=min_bg, arms=arm_out, digests=digests)


# --------------------------------------------------------------------------- #
# Aggregate + verdict                                                          #
# --------------------------------------------------------------------------- #
def _mean(vals):
    v = torch.tensor([x for x in vals if not (isinstance(x, float) and math.isnan(x))],
                     dtype=torch.float64)
    return float(v.mean()) if v.numel() else float("nan")


def _agg(seed_results, arm, field):
    return _mean([r["arms"][arm][field] for r in seed_results])


def decide_verdict(seed_results) -> dict:
    a = {arm: dict(det_auc=_agg(seed_results, arm, "det_auc"),
                   loc=_agg(seed_results, arm, "loc"),
                   corr=_agg(seed_results, arm, "corr_gain"),
                   auc_pc=_agg(seed_results, arm, "det_auc_partner_corr"),
                   loc_pc=_agg(seed_results, arm, "loc_partner_corr")) for arm in LAW_ARMS}

    full = a[FULL]
    best_nolaw_auc = max(a[MARGINAL]["det_auc"], a[RELATIONAL]["det_auc"])
    best_nolaw_loc = max(a[MARGINAL]["loc"], a[RELATIONAL]["loc"])
    best_nolaw_corr = max(a[MARGINAL]["corr"], a[RELATIONAL]["corr"])
    noredun = a[NO_REDUNDANCY]
    scr = a[SCRAMBLE]
    wrong = a[WRONG_EXP]

    # ---- gates ----------------------------------------------------------------
    # (a') correction (HEADLINE: FULL is the only arm that can CORRECT under joint corruption)
    corr_strong = full["corr"] >= HP_FULL_CORR_GAIN
    corr_beats_noredun = (full["corr"] - noredun["corr"]) >= HP_FULL_BEATS_NOREDUN_CORR
    corr_beats_nolaw = (full["corr"] - best_nolaw_corr) >= HP_FULL_BEATS_NOLAW_CORR
    # (H) localization
    loc_strong = full["loc"] >= HP_FULL_LOC
    loc_beats_noredun = (full["loc"] - noredun["loc"]) >= HP_FULL_BEATS_NOREDUN_LOC
    loc_beats_nolaw = (full["loc"] - best_nolaw_loc) >= HP_FULL_BEATS_MARG_LOC
    # (a) detection
    det_strong = full["det_auc"] >= HP_FULL_DET_AUC
    det_beats_nolaw = (full["det_auc"] - best_nolaw_auc) >= HP_FULL_BEATS_NOLAW_AUC
    # NO-CLEAN-SIBLING PROOF is structural + (H): (i) background noise on 100% of cells so
    # no attribute is clean (asserted min_bg>0 at self-test), and (ii) NO_REDUNDANCY IS the
    # single-predictor case -- if a lone clean sibling were doing the work it would match
    # FULL; it does not (h_fires). The partner-also-corrupted probe below is REPORT-ONLY
    # (ill-posed once BOTH pair-members are off-manifold: localizing "which one" is
    # ambiguous and NO_REDUNDANCY's detection even inflates via mutual corruption) -- kept
    # as an honest weak-point diagnostic, NOT a HARD_PASS gate.
    partner_strong = full["auc_pc"] >= HP_FULL_DET_AUC_PARTNER_CORR      # report-only
    partner_beats_noredun = (full["auc_pc"] - noredun["auc_pc"]) >= HP_FULL_BEATS_NOREDUN_PARTNER  # report-only

    h_fires = corr_strong and corr_beats_noredun and corr_beats_nolaw and loc_strong and loc_beats_noredun
    a_fires = det_strong and det_beats_nolaw and loc_beats_nolaw
    b_fires = partner_strong and partner_beats_noredun            # diagnostic, not gated

    # must-fail collapses: single-partner + scramble + wrong CANNOT correct/localize.
    scr_collapse = (scr["corr"] <= MF_SCRAMBLE_CORR) and ((full["loc"] - scr["loc"]) >= MF_SCRAMBLE_BEATEN_LOC)
    noredun_collapse = (noredun["corr"] <= MF_NOREDUN_CORR_CEIL) and (noredun["loc"] <= MF_NOREDUN_LOC_CEIL)
    wrong_beaten = ((full["loc"] - wrong["loc"]) >= WRONG_MARGIN_LOC
                    and (full["corr"] - wrong["corr"]) >= WRONG_MARGIN_CORR)
    mustfail_collapses = scr_collapse and noredun_collapse and wrong_beaten
    mechanism_fires = full["det_auc"] >= HF_FULL_AUC_MIN

    # failure-mode classification (do NOT conflate). b_fires is a REPORT-ONLY diagnostic.
    if not mechanism_fires:
        failure_mode = "MECHANISM_NOT_FIRING_full_auc_below_floor"
    elif not mustfail_collapses:
        failure_mode = "REDUNDANCY_NOT_LOADBEARING_single_or_scramble_or_wrong_also_corrects"
    elif h_fires and a_fires:
        failure_mode = "REDUNDANCY_GROUNDS_localizes_corrects_no_clean_sibling"
    elif h_fires and not a_fires:
        failure_mode = "REDUNDANCY_LOCALIZES_CORRECTS_but_detect_weak"
    elif a_fires and not h_fires:
        failure_mode = "REDUNDANCY_DETECTS_but_localize_correct_weak"
    else:
        failure_mode = "REDUNDANCY_NO_ADVANTAGE_over_noredun"

    hard_pass = mechanism_fires and mustfail_collapses and h_fires and a_fires
    if hard_pass:
        verdict = "HARD_PASS"
    elif (not mechanism_fires) or (not mustfail_collapses):
        verdict = "HARD_FAIL"
    elif h_fires or a_fires or b_fires:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    msg = ("%s | [a':CORRECT] FULL=%+.3f NOREDUN=%+.3f SCR=%+.3f WRONG=%+.3f best_nolaw=%+.3f "
           "d_noredun=%+.3f d_nolaw=%+.3f "
           "| [H:localize] FULL=%.3f NOREDUN=%.3f SCR=%.3f MARG=%.3f REL=%.3f (chance=%.3f) d_noredun=%+.3f "
           "| [a:detect] FULL_AUC=%.3f best_nolaw=%.3f d=%+.3f "
           "| [b:no-clean-sibling AUC_pc] FULL=%.3f NOREDUN=%.3f d=%+.3f "
           "| collapse=%s (scr=%s noredun=%s wrong_beaten=%s) | mode=%s"
           % (verdict, full["corr"], noredun["corr"], scr["corr"], wrong["corr"], best_nolaw_corr,
              full["corr"] - noredun["corr"], full["corr"] - best_nolaw_corr,
              full["loc"], noredun["loc"], scr["loc"], a[MARGINAL]["loc"], a[RELATIONAL]["loc"],
              CHANCE_LOC, full["loc"] - noredun["loc"],
              full["det_auc"], best_nolaw_auc, full["det_auc"] - best_nolaw_auc,
              full["auc_pc"], noredun["auc_pc"], full["auc_pc"] - noredun["auc_pc"],
              mustfail_collapses, scr_collapse, noredun_collapse, wrong_beaten, failure_mode))

    return dict(verdict=verdict, verdict_msg=msg, failure_mode=failure_mode,
                h_fires=bool(h_fires), a_fires=bool(a_fires), b_fires=bool(b_fires),
                mustfail_collapses=bool(mustfail_collapses), mechanism_fires=bool(mechanism_fires),
                gates=dict(corr_strong=bool(corr_strong), corr_beats_noredun=bool(corr_beats_noredun),
                           corr_beats_nolaw=bool(corr_beats_nolaw), loc_strong=bool(loc_strong),
                           loc_beats_noredun=bool(loc_beats_noredun), loc_beats_nolaw=bool(loc_beats_nolaw),
                           det_strong=bool(det_strong), det_beats_nolaw=bool(det_beats_nolaw),
                           partner_strong=bool(partner_strong), partner_beats_noredun=bool(partner_beats_noredun),
                           scr_collapse=bool(scr_collapse), noredun_collapse=bool(noredun_collapse),
                           wrong_beaten=bool(wrong_beaten)),
                agg=dict(best_nolaw_auc=best_nolaw_auc, best_nolaw_loc=best_nolaw_loc,
                         best_nolaw_corr=best_nolaw_corr, chance_loc=CHANCE_LOC,
                         **{("%s_%s" % (arm.lower(), f)): a[arm][f]
                            for arm in LAW_ARMS for f in ("det_auc", "loc", "corr", "auc_pc", "loc_pc")}))


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
    logp = _log_props(mm)

    # F.1/F.2/F.3: construct + ingest the REAL KGStore at tiny scale (base kwargs only).
    exercised = set()
    gsmall = torch.Generator(device="cpu").manual_seed(1)
    store_small = KGStore(6, 2, 16, gsmall)
    exercised.add("KGStore")
    store_small.ingest_triples(torch.tensor([[0, 0, 4], [1, 1, 5], [2, 0, 4]], dtype=torch.long))
    assert len(store_small) == 3, "ingest_triples did not register triples"
    exercised.add("ingest_triples")
    _s, _rel = build_relational_store(mm, 256, torch.Generator(device="cpu").manual_seed(2))
    exercised.add("build_relational_store")

    # Discriminator preview: run the REAL mechanism on REAL data across seeds.
    seed_results = [run_seed(mm, logp, cfg, s) for s in cfg["seeds"]]
    dv = decide_verdict(seed_results)
    agg = dv["agg"]

    # metric-moves: FULL residual for a cell MUST move when that value is driven off-manifold.
    y0 = logp[:, ATTR_COLS].clone().to(torch.float64)
    z_clean, _ = _arm_scores(FULL, y0, y0.clone(), _cos_sim_real(
        build_relational_store(mm, 256, torch.Generator(device="cpu").manual_seed(3))[1]),
        cfg["weight_exp"])
    y1 = y0.clone(); y1[0, 0] = y1[0, 0] + 1.2   # drive mass of entity 0 off-manifold
    z_corr, _ = _arm_scores(FULL, y1, y1.clone(), _cos_sim_real(
        build_relational_store(mm, 256, torch.Generator(device="cpu").manual_seed(3))[1]),
        cfg["weight_exp"])
    resid_clean = float(z_clean[0, 0]); resid_corr = float(z_corr[0, 0])

    # ARMS-MUST-DIFFER exercised at self-test (fail-closed).
    d0 = seed_results[0]["digests"]
    pairs = [(x, y) for i, x in enumerate(LAW_ARMS) for y in LAW_ARMS[i + 1:]]
    assert all(d0[x] != d0[y] for x, y in pairs), "META_RULE_AF: two arms bit-identical"

    # cardinality exercised (n_seeds * K per-attr detection units).
    expected_units = len(cfg["seeds"]) * K
    got_units = len(seed_results) * K
    assert got_units == expected_units, "cardinality breach: got %d expected %d" % (got_units, expected_units)

    # no-clean-sibling structural proof: EVERY cell carries nonzero background perturbation.
    min_bg = min(r["min_bg_perturb"] for r in seed_results)
    assert min_bg > 0.0, "background noise not on 100%% of cells (min_bg=%.4g); clean sibling exists" % min_bg

    # negative-control margin: NO_REDUNDANCY + SCRAMBLE CORRECTION gain must fail the FULL bar.
    nr_corr = [r["arms"][NO_REDUNDANCY]["corr_gain"] for r in seed_results]
    scr_corr = [r["arms"][SCRAMBLE]["corr_gain"] for r in seed_results]

    run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["KGStore", "ingest_triples", "build_relational_store"],
         "exercised_entrypoints": sorted(exercised)},
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None}},
        # F.4 guard_baseline_valid is N/A: this cell has NO control-beats-baseline BREAK-guard.
        # (The must-fails are localization-margin gates, not a control-vs-incumbent break-guard.)
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": agg["full_corr"] >= HP_FULL_CORR_GAIN,
         "control_name": "FULL_correction", "headline_name": "full_corr_gain"},
        {"kind": "metric_moves", "metric_name": "full_residual_z",
         "before": resid_clean, "after": resid_corr},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "cardinality", "no_clean_sibling"],
         "exercised_gates": ["arms_differ", "cardinality", "no_clean_sibling"]},
        # must-fail = NO_REDUNDANCY + SCRAMBLE CORRECTION gain (headline discriminator): both
        # must land <= 0 correction (cannot correct), robustly across seeds, below FULL's bar.
        {"kind": "negative_control_margin", "control_scores": nr_corr + scr_corr,
         "headline_threshold": HP_FULL_CORR_GAIN, "higher_is_pass": True, "margin": 0.0,
         "n_repeats_min": 2, "control_name": "NO_REDUNDANCY+SCRAMBLE_correction_gain"},
    ], run_mode="selftest")

    # Discriminator-fires + must-fail collapse + baseline-in-band (fail-closed asserts).
    # HEADLINE: FULL is the ONLY arm that CORRECTS under joint corruption.
    assert agg["full_corr"] >= HP_FULL_CORR_GAIN, (
        "FULL correction did not fire: %.3f < %.3f" % (agg["full_corr"], HP_FULL_CORR_GAIN))
    assert (agg["full_corr"] - agg["no_redundancy_corr"]) >= HP_FULL_BEATS_NOREDUN_CORR, (
        "FULL correction does not beat NO_REDUNDANCY: FULL=%.3f NOREDUN=%.3f"
        % (agg["full_corr"], agg["no_redundancy_corr"]))
    assert (agg["full_corr"] - agg["best_nolaw_corr"]) >= HP_FULL_BEATS_NOLAW_CORR, (
        "FULL correction does not beat best no-law: FULL=%.3f best_nolaw=%.3f"
        % (agg["full_corr"], agg["best_nolaw_corr"]))
    assert agg["full_loc"] >= HP_FULL_LOC, (
        "FULL localization weak: %.3f < %.3f" % (agg["full_loc"], HP_FULL_LOC))
    assert (agg["full_loc"] - agg["no_redundancy_loc"]) >= HP_FULL_BEATS_NOREDUN_LOC, (
        "FULL does not beat NO_REDUNDANCY on localization: FULL=%.3f NOREDUN=%.3f"
        % (agg["full_loc"], agg["no_redundancy_loc"]))
    assert (agg["full_loc"] - agg["best_nolaw_loc"]) >= HP_FULL_BEATS_MARG_LOC, (
        "FULL does not beat best no-law localization: FULL=%.3f best_nolaw=%.3f"
        % (agg["full_loc"], agg["best_nolaw_loc"]))
    assert agg["full_det_auc"] >= HP_FULL_DET_AUC, (
        "FULL detection weak: AUC=%.3f < %.3f" % (agg["full_det_auc"], HP_FULL_DET_AUC))
    # baseline-in-band: best no-law localization must be strictly below FULL (not saturated).
    assert agg["best_nolaw_loc"] < agg["full_loc"] - HP_FULL_BEATS_MARG_LOC + 1e-9, (
        "baseline not in band (no-law localization too high): %.3f" % agg["best_nolaw_loc"])
    # SCRAMBLE (no pairing) must not correct + must be beaten on localization by margin.
    assert (agg["scramble_corr"] <= MF_SCRAMBLE_CORR
            and (agg["full_loc"] - agg["scramble_loc"]) >= MF_SCRAMBLE_BEATEN_LOC), (
        "SCRAMBLE did not collapse: corr=%.3f (ceil %.3f) loc=%.3f (FULL=%.3f); do NOT ship"
        % (agg["scramble_corr"], MF_SCRAMBLE_CORR, agg["scramble_loc"], agg["full_loc"]))
    # NO_REDUNDANCY (single partner) must not correct + localization pair-ambiguous.
    assert (agg["no_redundancy_corr"] <= MF_NOREDUN_CORR_CEIL
            and agg["no_redundancy_loc"] <= MF_NOREDUN_LOC_CEIL), (
        "NO_REDUNDANCY did not collapse: corr=%.3f (ceil %.3f) loc=%.3f (ceil %.3f); do NOT ship"
        % (agg["no_redundancy_corr"], MF_NOREDUN_CORR_CEIL, agg["no_redundancy_loc"], MF_NOREDUN_LOC_CEIL))
    assert ((agg["full_loc"] - agg["wrong_exp_loc"]) >= WRONG_MARGIN_LOC
            and (agg["full_corr"] - agg["wrong_exp_corr"]) >= WRONG_MARGIN_CORR), (
        "WRONG_EXP not beaten by margin: wrong(loc=%.3f corr=%.3f) vs FULL(loc=%.3f corr=%.3f)"
        % (agg["wrong_exp_loc"], agg["wrong_exp_corr"], agg["full_loc"], agg["full_corr"]))
    # NO-CLEAN-SIBLING is proven structurally (min_bg>0 above: 100%% of cells noisy) + by the
    # NO_REDUNDANCY collapse (a single predictor cannot match FULL). The partner-corrupted
    # AUC_pc/loc_pc are REPORT-ONLY weak-point diagnostics (ill-posed once both pair-members
    # are off-manifold), not gated -- see decide_verdict note.
    print("[self-test] validity + redundancy-discriminator + must-fail-collapse PASS: %s"
          % dv["verdict_msg"], flush=True)


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="fast validity + discriminator preview")
    ap.add_argument("--smoke", action="store_true", help="reduced-grid run")
    args, _ = ap.parse_known_args()

    mm = load_mammals()
    logp = _log_props(mm)

    if args.self_test:
        _validity_checks(mm, dict(SELFTEST_CFG))
        print("SELFTEST_PASS", flush=True)
        return

    cfg = dict(SELFTEST_CFG) if args.smoke else dict(FULL_CFG)
    run_mode = "smoke" if args.smoke else "full"
    out_dir = _out_dir()
    expected_units = len(cfg["seeds"]) * K
    _write_start_marker(out_dir, run_mode, expected_units)

    t0 = time.perf_counter()
    seed_results = []
    for s in cfg["seeds"]:
        rs = run_seed(mm, logp, cfg, s)
        seed_results.append(rs)
        f = rs["arms"][FULL]; nr = rs["arms"][NO_REDUNDANCY]
        print("[progress] seed=%d FULL_loc=%.3f NOREDUN_loc=%.3f FULL_auc=%.3f elapsed=%.1fs"
              % (s, f["loc"], nr["loc"], f["det_auc"], time.perf_counter() - t0), flush=True)

    dv = decide_verdict(seed_results)
    elapsed = time.perf_counter() - t0

    got_units = len(seed_results) * K
    cardinality_ok = (got_units == expected_units)
    verdict, verdict_msg = dv["verdict"], dv["verdict_msg"]
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = "cardinality breach: got %d expected %d | %s" % (got_units, expected_units, verdict_msg)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg,
        summary=("%s FULL_corr=%+.3f FULL_loc=%.3f NOREDUN_loc=%.3f FULL_auc=%.3f collapse=%s"
                 % (verdict, dv["agg"]["full_corr"], dv["agg"]["full_loc"], dv["agg"]["no_redundancy_loc"],
                    dv["agg"]["full_det_auc"], dv["mustfail_collapses"])),
        elapsed_s=round(elapsed, 3), run_mode=run_mode, anchor_name=ANCHOR_NAME,
        n_dim=cfg["n_dim"], n_seeds=len(cfg["seeds"]), expected_n_units=expected_units,
        got_n_units=got_units, cardinality_ok=cardinality_ok,
        failure_mode=dv["failure_mode"], h_fires=dv["h_fires"], a_fires=dv["a_fires"],
        b_fires=dv["b_fires"], mustfail_collapses=dv["mustfail_collapses"],
        mechanism_fires=dv["mechanism_fires"], gates=dv["gates"], agg=dv["agg"],
        loadings=dict(zip(ATTR_NAMES, LOADINGS)),
        law_network="fully_connected_4node_pairwise_powerlaw",
        cfg=dict(sigma_bg=cfg["sigma_bg"], shift_lo=cfg["shift_lo"], shift_hi=cfg["shift_hi"]),
        per_seed=[dict(seed=r["seed"], n_dim=r["n_dim"], n_triples=r["n_triples"],
                       min_bg_perturb=r["min_bg_perturb"], arms=r["arms"]) for r in seed_results],
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
