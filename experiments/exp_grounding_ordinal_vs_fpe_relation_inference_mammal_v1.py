"""GROUNDING ORDINAL-vs-FPE ENCODING: is an ORDINAL (thermometer / level) code of the grounded
attributes as strong as, cheaper than, and more bundling-robust than the ABSOLUTE fractional-power
(FPE) encoding we have used, while carrying the same held-out-relation grounding signal?

WHY THIS CELL EXISTS -- Thrust-B Lever B from the grounding drills
  (notes/research_grounding_topicB_synthesis_and_next_levers_2026-07-14.md):
  measurement-theory + Piaget seriation say ORDINAL ("A > B") is developmentally + structurally PRIOR
  to absolute/cardinal values, needs only a DIFFERENCE-DETECTOR (no calibration), and dodges FPE's
  bundling-degradation. Our grounding cells all used ABSOLUTE FPE random-Fourier features of the
  measured attributes. This cell re-runs the SAME gated-fusion relation-inference arena (the mammal
  taxonomy KG + convex-gate machinery from exp_grounding_gated_fusion_relation_inference_mammal_v1)
  and ONLY swaps the grounded-attribute ENCODING: FPE  ->  ORDINAL THERMOMETER / LEVEL code.

  ORDINAL scheme = THERMOMETER (level) code, glass-box + inspectable: for each normalized attribute v
  in [0,1] and n_levels equally-spaced thresholds t_j, bit_j = 1[v >= t_j]. Each column is literally
  "is attribute k above ordinal level j" -- a pure COMPARISON. NO absolute value column is carried
  (the strongest form of the ordinal claim: comparisons ALONE, no calibrated magnitude). Dim is
  MATCHED to the FPE feature (5 attrs * n_levels == 5 * (1 + 2*n_freq)) so the head-to-head is a fair
  same-dimension comparison; cost differs only in ops per feature (a COMPARE vs a transcendental
  cos/sin RFF eval), so ordinal is cheaper BY CONSTRUCTION (no transcendentals).

MECHANISM (unchanged from gated-fusion; the ONLY swap is the grounded-attribute encoder):
  grounded code = ridge-map(attribute-features) -> learned relational latent (fit on SEEN entities).
  GATED head code = (1-lambda)*relational_bundle + lambda*grounded_code, lambda a single glass-box
  scalar learned per seed on a DISJOINT val split (pure-grounding endpoint lambda=1 is in the grid, so
  the gate cannot underperform grounding on VAL -- recovers, does not dilute). We run the gate over the
  ORDINAL grounded code (mechanism, GATED_ORDINAL) AND over the FPE grounded code (reference recipe,
  GATED_FPE) head-to-head on the SAME held-out queries, plus grounded-only variants of each.

PRIMARY QUESTION (contract): does ORDINAL-encoded grounding MATCH or BEAT absolute-FPE grounding on
  held-out-relation inference, at LOWER encoding cost + MORE bundling-robustness?

PRIMARY METRIC = HELD-OUT RELATION inference (filtered MRR, rank-vs-all, KGE standard, degree-unbiased
  -- NO sampled-negative pool). PAIRED ablation on the SAME held-out-relation queries. Multi-seed.

BUNDLING-ROBUSTNESS PROBE (first-class DIAGNOSTIC, glass-box, matched-dim, self-contained): the
  classic bundle-capacity test -- superpose (sum) B distinct entities' grounded-attribute codes, then
  test whether each member is still individually detectable (cosine to the bundle beats every
  distractor). Sweep bundle depth B and report the member-detection accuracy curve + AUC for BOTH
  encodings. The Lever-B claim is that ordinal degrades LESS with depth. This is REPORTED (booleans +
  AUCs + curves) and informs the HARD_PASS/MIDDLE split narrative but does NOT gate HARD_PASS by
  itself (the contract asks the bundling check be INCLUDED; the HARD_PASS is the arena match/beat).

PRE-REGISTERED BANDS (BOTH sides picked BEFORE the run; RELATIVE deltas -- absolute MRR shifts with the
  small mammal train pool but match/recovery are RELATIVE claims):
  ORDINAL_MATCHES_OR_BEATS_FPE (HARD_PASS): ALL of:
    (a) MATCH: mean GROUNDED_ORDINAL_ONLY_mrr >= mean GROUNDED_FPE_ONLY_mrr - MATCH_TOL   AND
              mean GATED_ORDINAL_mrr        >= mean GATED_FPE_mrr        - MATCH_TOL
              (ordinal grounding matches/beats FPE grounding standalone AND gated)
    (b) RECOVER: mean (GATED_ORDINAL - RELATIONAL)_mrr >= HP_RECOVER_GAIN  (ordinal carries real signal)
    (c) RIGHT-ATTRS: mean (GATED_ORDINAL - SCRAMBLE_ORDINAL)_mrr >= SCR_ABS_MARGIN
    (d) CONSISTENCY: per-seed (GATED_ORDINAL - RELATIONAL) > 0 in >= SEED_CONSISTENCY_FRAC of seeds
    (e) ARENA VALID: ORACLE fires AND RELATIONAL above RANDOM AND not broken.
    (cost + bundling-robustness reported as supporting diagnostics: ordinal_cheaper by construction;
     ordinal_more_bundling_robust from the probe.)
  ORDINAL_GROUNDS_BUT_BELOW_FPE (MIDDLE_BAND): mean (GATED_ORDINAL - RELATIONAL)_mrr >= MB_PARTIAL_GAIN
    AND arena valid, BUT the MATCH (a) fails (ordinal below FPE by > MATCH_TOL) OR scramble/consistency
    fails. Ordinal carries grounding but does not match the FPE recipe.
  ORDINAL_FAILS_TO_GROUND (HARD_FAIL): mean (GATED_ORDINAL - RELATIONAL)_mrr < MB_PARTIAL_GAIN with
    ORACLE firing (the ordinal encoding does not carry the grounding signal).
  INCONCLUSIVE if ORACLE does not fire, too few held-out queries, RELATIONAL at the RANDOM floor, or a
    null beats the relational baseline.

MUST-FAIL: SCRAMBLE_ORDINAL = the SAME ordinal-gate pipeline but attributes SHUFFLED across entities
  (lambda re-learned on VAL). Scrambled ordinal attributes must NOT beat real ordinal attributes through
  the gate (GATED_ORDINAL - SCRAMBLE_ORDINAL >= SCR_ABS_MARGIN). RANDOM null must stay at floor.

## Compute architecture
class (b) sequential-CPU: the 65-entity mammal taxonomy KG (N ~ 125 incl symbols); train/val/test
  entity split; a few tiny additive-KGE fits per seed (ADDITIVE + ORACLE) via minibatch SGD reused from
  _kge_anchor1_fit + closed-form ridge grounding maps (ordinal + FPE + scramble) + three lambda
  grid-searches (11 pts) over tiny (nq,N) cdist score matrices on VAL. Plus a cheap bundling probe
  (small unit-norm matmuls). Seconds/seed on CPU (N,nq tiny); GPU buys nothing. Storage SHARDED (each
  entity its own code; relations = per-TYPE additive displacements; only bundle is the per-ENTITY
  anchor mean + the diagnostic superposition probe). device forced cpu on remote_cpu_queue.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 8 geom arms, >=5 distinct sig floor.
#   EXEMPTED collapses (correct by construction, not bugs): (GATED_ORDINAL, GROUNDED_ORDINAL_ONLY) at
#   lambda_ord==1; (GATED_FPE, GROUNDED_FPE_ONLY) at lambda_fpe==1; (SCRAMBLE_ORDINAL, RELATIONAL_ONLY)
#   at lambda_scr==0. Min distinct = 5 (RELATIONAL, RANDOM, ORACLE, GROUNDED_ORDINAL, GROUNDED_FPE).
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: match/recovery framed RELATIVE to the MEASURED FPE reference + RELATIONAL;
#   ORACLE=1.0 saturates and is used ONLY as the arena-answerable gate.
# - baseline_in_band: ORACLE must fire (>=3x RANDOM AND headroom>=ABS); RANDOM near 1/N; REL above RANDOM.
# - discriminator survives scale: PAIRED delta on the SAME queries; planted self-test fires ORDINAL
#   grounding recovers + no dilution + scramble-fails + oracle deterministically.
# - HARD_PASS strictly above floor: match + recovery + scramble margin + consistency.
# - HP_SCOPE: match/recovery gates apply to GATED_ORDINAL vs RELATIONAL/GATED_FPE/GROUNDED_*_ONLY. ORACLE
#   = positive control; RANDOM/SCRAMBLE_ORDINAL = must-not-explain controls; GROUNDED_FPE_ONLY/GATED_FPE
#   = the reference being matched/beaten; POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce 8 arms + >=5 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- every lambda is LEARNED ON VAL, never on test;
#   split fractions + band FRACTIONS pre-registered, NOT tuned on the real test queries.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - F.1 real_code_path: self-test CALLS the REAL fit_kge_anchor1 + filtered_hits_from_scores + fit_ridge
#   + ordinal_ground_features + fpe_ground_features + the bundling probe.
# - F.2/F.3 substrate_signature: fit_kge_anchor1 bound with BASE/portable kwargs only.
# - F.4 guard_baseline_valid: RELATIONAL_ONLY validated above the RANDOM floor before it anchors deltas.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).

ASCII-only. No em-dashes in output. No bare except; except SystemExit before except Exception.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# Reused proven leaf primitives (attribute wiring + additive fit + ceiling-aware eval) + the arena.
from experiments.exp_grounding_mammal_allometry_xchannel_fpe_v1 import (  # noqa: E402
    _PROP_NAMES,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    filtered_hits_from_scores, build_true_by_hr_int, pop_hits,
)
from experiments.exp_grounding_improves_relation_inference_mammal_v1 import (  # noqa: E402
    build_mammal_kg, build_planted_kg, fpe_ground_features, fit_ridge,
    grounded_codes, build_relational_bundle, additive_scores, GAMMA,
)
from experiments.exp_grounding_gated_fusion_relation_inference_mammal_v1 import (  # noqa: E402
    build_train_val_test_split, _gated_table, _equal_sum_table, learn_lambda,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402

ANCHOR_NAME = "grounding_ordinal_vs_fpe_relation_inference_mammal_v1"

# ---- Arm names ----
RELATIONAL = "RELATIONAL_ONLY"        # ablation baseline: anchor-compose bundle only (no grounding)
GATED_ORD = "GATED_ORDINAL"           # MECHANISM: gate over ORDINAL thermometer grounded code
GATED_FPE = "GATED_FPE"               # REFERENCE: gate over ABSOLUTE FPE grounded code (existing recipe)
GROUND_ORD = "GROUNDED_ORDINAL_ONLY"  # ordinal grounded estimate only
GROUND_FPE = "GROUNDED_FPE_ONLY"      # FPE grounded estimate only (reference standalone)
SCRAMBLE = "SCRAMBLE_ORDINAL"         # must-fail: ordinal gate over SHUFFLED attributes (lambda re-learn)
RANDOM = "RANDOM_CODES"               # null
ORACLE = "ORACLE_ADDITIVE"            # positive control: held-out folded into the fit = ceiling
POP = "BASELINE_POP"                  # frequency incumbent (fit-independence sanity)
GEOM_ARMS = [RELATIONAL, GATED_ORD, GATED_FPE, GROUND_ORD, GROUND_FPE, SCRAMBLE, RANDOM, ORACLE]
ALL_ARMS = GEOM_ARMS + [POP]

EVAL_KS = (1, 3, 10)
CEIL_METRIC = "mrr"

# ---- arena-answerable gate (ORACLE = held-out folded in; near-saturates by construction) ----
ORACLE_FIRE_RATIO = 3.0            # ORACLE_mrr >= 3x RANDOM_mrr (scale-free clear separation)
ORACLE_FIRE_ABS = 0.05            # AND ORACLE_mrr - RANDOM_mrr >= this (non-noise absolute floor)
REL_ABOVE_RANDOM_MIN = 0.02      # RELATIONAL_ONLY must beat RANDOM by this (a real reasoning baseline)

# ---- RELATIVE bands (pre-registered; NOT tuned on real test data) ----
MATCH_TOL = 0.03               # HARD_PASS (a): ordinal within MATCH_TOL below FPE == "match or beat"
HP_RECOVER_GAIN = 0.10         # HARD_PASS (b): mean (GATED_ORDINAL - RELATIONAL)_mrr >= this
SCR_ABS_MARGIN = 0.05          # HARD_PASS (c): (GATED_ORDINAL - SCRAMBLE_ORDINAL)_mrr >= this
SEED_CONSISTENCY_FRAC = 0.75   # HARD_PASS (d): fraction of seeds with per-seed (GATED_ORD-REL) gain > 0
MB_PARTIAL_GAIN = 0.03         # MIDDLE_BAND floor: ordinal gate at least beats RELATIONAL by this
BROKEN_EPS = 0.01              # broken: a null (RANDOM) beats RELATIONAL by more than this
MIN_HELDOUT = 15              # min held-out TEST QUERY edges per seed for a valid discriminator
DISTINCT_SIG_FLOOR = 5        # >=5 distinct arm-score signatures (legit lambda collapses allowed)

# ---- bundling-robustness probe (reported diagnostic) ----
BUNDLE_DEPTHS = [1, 2, 4, 8, 16, 24]   # superposition depth sweep
BUNDLE_N_DISTRACT = 20                 # distractors per detection trial
BUNDLE_N_TRIALS = 60                   # trials per depth (averaged)
ROBUST_MARGIN = 0.03                   # ordinal_auc >= fpe_auc + this => ordinal_more_bundling_robust

# ---- encoding knobs (pre-registered; NOT tuned on real data) ----
N_FPE_FREQ = 4                # FPE random-Fourier frequencies per attribute (reuses fpe_encode)
FPE_FREQ_STD = 2.15           # matches the proven mammal-allometry FPE bandwidth
ORDINAL_LEVELS = 9            # thermometer levels per attribute: 5*9 == 5*(1+2*4) == FPE dim (matched)
RIDGE_LAM = 1.0               # grounding ridge regularization

# ---- split knobs (pre-registered; NOT tuned on real data; match the gated-fusion arena) ----
HELDOUT_ENTITY_FRAC = 0.28
VAL_ENTITY_FRAC = 0.16
SUPPORT_FRAC = 0.34
LAMBDA_GRID = [round(x, 3) for x in np.linspace(0.0, 1.0, 11).tolist()]

# ---- self-test planted thresholds (calibrated on the synthetic latent-consistent arena, NOT real) ----
SELFTEST_ORACLE_MRR_MIN = 0.20     # planted: ORACLE (learned held-out codes) mrr at least this
SELFTEST_GATED_BEATS_REL = 0.02    # planted: (GATED_ORDINAL - RELATIONAL)_mrr >= this (ordinal recovers)
SELFTEST_GATED_NO_DILUTE = 0.05    # planted: GATED_ORDINAL >= GROUNDED_ORDINAL_ONLY - this (no dilution)
SELFTEST_GATED_BEATS_SCR = 0.015   # planted: (GATED_ORDINAL - SCRAMBLE_ORDINAL)_mrr >= this
SELFTEST_GROUND_BEATS_RAND = 0.02  # planted: (GROUNDED_ORDINAL_ONLY - RANDOM)_mrr >= this (ordinal info)
SELFTEST_MIN_HO = 20               # planted: minimum held-out TEST QUERY edges

# ---- configs (SELFTEST planted; SMOKE + FULL on the mammal KG) ----
SELFTEST_CFG = dict(k=12, epochs=200, n_neg=32, batch=2048,
                    heldout_entity_frac=0.30, val_entity_frac=0.16, support_frac=0.34)
SMOKE_CFG = dict(k=16, epochs=120, n_neg=32, batch=1024,
                 heldout_entity_frac=HELDOUT_ENTITY_FRAC, val_entity_frac=VAL_ENTITY_FRAC,
                 support_frac=SUPPORT_FRAC, seeds=[7, 13, 17])
FULL_CFG = dict(k=16, epochs=300, n_neg=48, batch=1024,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, val_entity_frac=VAL_ENTITY_FRAC,
                support_frac=SUPPORT_FRAC, seeds=[7, 13, 17, 23, 29, 31, 37, 41])

SUPPORT_BINS = [(0, 0, "cold"), (1, 1, "d1"), (2, 3, "d2_3")]


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# ORDINAL (thermometer / level) grounded-attribute encoder -- the ONLY new    #
# primitive. Glass-box: bit_j = 1[v >= t_j] for equally-spaced interior       #
# thresholds t_j. Pure COMPARISON; NO absolute value column carried. Dim       #
# 5*n_levels is MATCHED to the FPE feature dim 5*(1+2*n_freq) for a fair       #
# same-dimension head-to-head. Cheaper by construction (compares, no trig).    #
# --------------------------------------------------------------------------- #
def ordinal_ground_features(attr, n_levels):
    """Phi [N, n_attr*n_levels] real thermometer code: per attribute, n_levels monotone comparison
    bits 1[v >= t_j] for equally spaced interior thresholds t_j in (0,1). NaN -> all-zero (below all).
    """
    thr = torch.linspace(1.0 / (n_levels + 1), n_levels / (n_levels + 1), n_levels, dtype=torch.float64)
    cols = []
    for k in range(attr.shape[1]):
        v = attr[:, k].to(torch.float64)
        v = torch.nan_to_num(v, nan=-1.0).view(-1, 1)          # NaN -> below every threshold
        therm = (v >= thr.view(1, -1)).to(torch.float64)       # [N, n_levels]
        cols.append(therm)
    return torch.cat(cols, dim=1)                              # [N, n_attr*n_levels]


def encoding_cost(n_attr, n_levels, n_freq):
    """THEORETICAL op accounting per entity (glass-box cost comparison). Ordinal = comparisons only;
    FPE = the same feature dim but each RFF feature needs a transcendental cos/sin + a multiply."""
    ord_dim = n_attr * n_levels
    fpe_dim = n_attr * (1 + 2 * n_freq)
    ord_ops = dict(compares=n_attr * n_levels, mults=0, transcendentals=0, dim=ord_dim)
    fpe_ops = dict(compares=0, mults=n_attr * n_freq, transcendentals=n_attr * n_freq * 2, dim=fpe_dim)
    cheaper = bool(ord_ops["transcendentals"] < fpe_ops["transcendentals"]
                   and ord_ops["mults"] <= fpe_ops["mults"] and ord_dim == fpe_dim)
    return dict(ordinal=ord_ops, fpe=fpe_ops, dims_matched=bool(ord_dim == fpe_dim),
                ordinal_cheaper=cheaper)


# --------------------------------------------------------------------------- #
# Bundling-robustness probe: superpose (sum) B distinct entities' grounded-    #
# attribute codes, test each member is still detectable (cosine to bundle      #
# beats every distractor). Sweep depth B. Matched-dim ordinal vs FPE.          #
# --------------------------------------------------------------------------- #
def _unit_rows(M):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n = np.where(n <= 0.0, 1.0, n)
    return M / n


def _member_detect_acc(codes_unit, elig_idx, depth, n_distract, n_trials, rng):
    """Fraction of bundled members whose cosine to the (unit) bundle beats every distractor's."""
    E = elig_idx.shape[0]
    need = depth + n_distract
    if E < need or depth < 1:
        return float("nan")
    hits = tot = 0
    for _ in range(n_trials):
        pick = rng.choice(E, size=need, replace=False)
        members = elig_idx[pick[:depth]]
        distract = elig_idx[pick[depth:]]
        mem = codes_unit[members]                              # [B, F] unit rows
        dis = codes_unit[distract]                             # [D, F] unit rows
        bundle = mem.sum(axis=0)
        bn = np.linalg.norm(bundle)
        if bn <= 0.0:
            continue
        bundle = bundle / bn
        sim_mem = mem @ bundle                                 # [B]
        sim_dis = dis @ bundle                                 # [D]
        best_dis = float(sim_dis.max()) if sim_dis.shape[0] else -1e9
        for sm in sim_mem:
            tot += 1
            if float(sm) > best_dis:
                hits += 1
    return (hits / tot) if tot > 0 else float("nan")


def bundling_robustness_probe(attr, eligible_mask, seed):
    """Matched-dim ordinal-vs-FPE member-detection accuracy over bundle depths. Returns curves + AUCs."""
    Phi_ord = ordinal_ground_features(attr, ORDINAL_LEVELS).numpy()
    Phi_fpe = fpe_ground_features(attr, N_FPE_FREQ, FPE_FREQ_STD, seed).numpy()
    ord_u = _unit_rows(Phi_ord.astype(np.float64))
    fpe_u = _unit_rows(Phi_fpe.astype(np.float64))
    elig_idx = np.nonzero(eligible_mask)[0].astype(np.int64)
    rng = np.random.default_rng(seed * 7919 + 11)
    ord_curve, fpe_curve = {}, {}
    for B in BUNDLE_DEPTHS:
        r1 = np.random.default_rng(seed * 101 + B)             # SAME member/distractor draws per encoding
        r2 = np.random.default_rng(seed * 101 + B)
        ord_curve[B] = _member_detect_acc(ord_u, elig_idx, B, BUNDLE_N_DISTRACT, BUNDLE_N_TRIALS, r1)
        fpe_curve[B] = _member_detect_acc(fpe_u, elig_idx, B, BUNDLE_N_DISTRACT, BUNDLE_N_TRIALS, r2)

    def _auc(curve):
        vals = [curve[B] for B in BUNDLE_DEPTHS if curve[B] == curve[B]]
        return float(np.mean(vals)) if vals else float("nan")

    ord_auc, fpe_auc = _auc(ord_curve), _auc(fpe_curve)
    more_robust = bool(ord_auc == ord_auc and fpe_auc == fpe_auc and ord_auc >= fpe_auc + ROBUST_MARGIN)
    deepest = BUNDLE_DEPTHS[-1]
    return dict(depths=list(BUNDLE_DEPTHS), dim=int(ord_u.shape[1]), fpe_dim=int(fpe_u.shape[1]),
                ordinal_curve={int(b): (round(ord_curve[b], 5) if ord_curve[b] == ord_curve[b] else None)
                               for b in BUNDLE_DEPTHS},
                fpe_curve={int(b): (round(fpe_curve[b], 5) if fpe_curve[b] == fpe_curve[b] else None)
                           for b in BUNDLE_DEPTHS},
                ordinal_auc=round(ord_auc, 5) if ord_auc == ord_auc else None,
                fpe_auc=round(fpe_auc, 5) if fpe_auc == fpe_auc else None,
                ordinal_acc_deepest=(round(ord_curve[deepest], 5) if ord_curve[deepest] == ord_curve[deepest]
                                     else None),
                fpe_acc_deepest=(round(fpe_curve[deepest], 5) if fpe_curve[deepest] == fpe_curve[deepest]
                                 else None),
                ordinal_more_bundling_robust=more_robust)


# --------------------------------------------------------------------------- #
# One corpus run: fit -> learn ordinal/FPE/scramble gates on VAL -> apply to   #
# TEST -> score PAIRED on the SAME held-out-relation queries.                  #
# --------------------------------------------------------------------------- #
def run_corpus(kg, cfg, device, seed):
    N, n_rel = kg["N"], kg["n_rel"]
    sp = build_train_val_test_split(kg, cfg["heldout_entity_frac"], cfg["val_entity_frac"],
                                    cfg["support_frac"], seed)
    train = sp["train"]
    test_support, test_query = sp["test_support"], sp["test_query"]
    val_support, val_query = sp["val_support"], sp["val_query"]
    combined_support = sp["combined_support"]
    test_hold_all = (np.concatenate([test_support, test_query], axis=0)
                     if test_query.shape[0] else test_support)

    result = dict(seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train.shape[0]),
                  n_test_heldout=len(sp["test_ids"]), n_val_heldout=len(sp["val_ids"]),
                  n_support=int(test_support.shape[0]), n_query_scored=int(test_query.shape[0]),
                  n_val_query=int(val_query.shape[0]), n_cold=int(sp["n_cold"]),
                  n_dropped=int(sp["n_dropped"]),
                  heldout_entity_frac=cfg["heldout_entity_frac"], val_entity_frac=cfg["val_entity_frac"],
                  support_frac=cfg["support_frac"])
    if test_query.shape[0] < 1 or train.shape[0] < 1:
        result["empty"] = True
        return result

    k = cfg["k"]
    X, D = fit_kge_anchor1(train, N, n_rel, k, device, seed, cfg["epochs"], reciprocal=True, lr=A1_LR,
                           n_neg=cfg["n_neg"], batch_size=cfg["batch"])
    Xo, Do = fit_kge_anchor1(train, N, n_rel, k, device, seed, cfg["epochs"],
                             transductive_extra=test_hold_all, reciprocal=True, lr=A1_LR,
                             n_neg=cfg["n_neg"], batch_size=cfg["batch"])
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    elig = kg["eligible"].numpy()
    test_ids = np.array(sorted(sp["test_ids"]), dtype=np.int64)
    val_ids = np.array(sorted(sp["val_ids"]), dtype=np.int64)
    held_all_ids = set(sp["test_ids"]) | set(sp["val_ids"])
    train_species = np.array([i for i in np.nonzero(elig)[0] if i not in held_all_ids], dtype=np.int64)

    Xp_rel_all, support_deg = build_relational_bundle(X, D, combined_support, N, device)

    # ORDINAL grounded code (real attrs), FPE grounded code (real attrs), scrambled-ORDINAL grounded code.
    Phi_ord = ordinal_ground_features(kg["attr"], ORDINAL_LEVELS)
    Phi_fpe = fpe_ground_features(kg["attr"], N_FPE_FREQ, FPE_FREQ_STD, seed)
    g_ord = grounded_codes(Phi_ord, X, train_species, held_all_ids, RIDGE_LAM)
    g_fpe = grounded_codes(Phi_fpe, X, train_species, held_all_ids, RIDGE_LAM)

    gS = np.random.default_rng(seed * 4441 + 17)
    elig_ids = np.nonzero(elig)[0]
    perm = elig_ids.copy()
    gS.shuffle(perm)
    attr_scr = kg["attr"].clone()
    attr_scr[elig_ids] = kg["attr"][perm]
    Phi_scr = ordinal_ground_features(attr_scr, ORDINAL_LEVELS)
    g_scr = grounded_codes(Phi_scr, X, train_species, held_all_ids, RIDGE_LAM)

    # learn each gate on VAL (ordinal / FPE / scramble get their own lambda).
    all_true_val = build_true_by_hr_int(train, val_support, val_query)
    lam_ord, val_mrr_ord, curve_ord, fb_ord = learn_lambda(
        X, Xp_rel_all, g_ord, val_ids, support_deg, D, val_query, all_true_val, device, LAMBDA_GRID)
    lam_fpe, val_mrr_fpe, curve_fpe, fb_fpe = learn_lambda(
        X, Xp_rel_all, g_fpe, val_ids, support_deg, D, val_query, all_true_val, device, LAMBDA_GRID)
    lam_scr, val_mrr_scr, curve_scr, fb_scr = learn_lambda(
        X, Xp_rel_all, g_scr, val_ids, support_deg, D, val_query, all_true_val, device, LAMBDA_GRID)

    # build TEST arm code tables (patch ONLY test held rows).
    Xp_rel = Xp_rel_all
    Xp_gated_ord = _gated_table(X, Xp_rel_all, g_ord, test_ids.tolist(), support_deg, lam_ord)
    Xp_gated_fpe = _gated_table(X, Xp_rel_all, g_fpe, test_ids.tolist(), support_deg, lam_fpe)
    Xp_scr = _gated_table(X, Xp_rel_all, g_scr, test_ids.tolist(), support_deg, lam_scr)
    Xp_ground_ord = X.clone(); Xp_ground_ord[test_ids] = g_ord[test_ids]
    Xp_ground_fpe = X.clone(); Xp_ground_fpe[test_ids] = g_fpe[test_ids]

    all_true_test = build_true_by_hr_int(train, test_support, test_query)
    rel_tail_freq = {}
    for i in range(train.shape[0]):
        rr = int(train[i, 1]); tt = int(train[i, 2])
        rel_tail_freq.setdefault(rr, Counter())[tt] += 1

    arm_tables = {RELATIONAL: (Xp_rel, D), GATED_ORD: (Xp_gated_ord, D), GATED_FPE: (Xp_gated_fpe, D),
                  GROUND_ORD: (Xp_ground_ord, D), GROUND_FPE: (Xp_ground_fpe, D),
                  SCRAMBLE: (Xp_scr, D), RANDOM: (Xr, Dr), ORACLE: (Xo, Do)}
    arm_scores, arm_hits, arm_sig = {}, {}, {}
    for a in GEOM_ARMS:
        Xt, Dt = arm_tables[a]
        arm_scores[a] = additive_scores(Xt, Dt, test_query, device)
        arm_hits[a] = filtered_hits_from_scores(arm_scores[a], test_query, all_true_test, ks=EVAL_KS)
        arm_sig[a] = _sig(arm_scores[a].numpy()[:min(64, arm_scores[a].shape[0])].ravel())
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, test_query, all_true_test, N, ks=EVAL_KS)
    arm_hits[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    # support-degree stratified recovery delta (weak-point localization) for the ORDINAL mechanism.
    q_sup = np.array([support_deg[int(test_query[i, 0])] for i in range(test_query.shape[0])],
                     dtype=np.int64)
    by_support = {}
    for lo, hi, nm in SUPPORT_BINS:
        mask = (q_sup >= lo) & (q_sup <= hi)
        idx = np.nonzero(mask)[0]
        if idx.size < 3:
            by_support[nm] = dict(n=int(idx.size), gated_ord=None, gated_fpe=None, relational=None, gain=None)
            continue
        go = filtered_hits_from_scores(arm_scores[GATED_ORD][idx], test_query[idx], all_true_test, ks=(1,))
        gf = filtered_hits_from_scores(arm_scores[GATED_FPE][idx], test_query[idx], all_true_test, ks=(1,))
        rh = filtered_hits_from_scores(arm_scores[RELATIONAL][idx], test_query[idx], all_true_test, ks=(1,))
        by_support[nm] = dict(n=int(idx.size), gated_ord=round(go["mrr"], 5), gated_fpe=round(gf["mrr"], 5),
                              relational=round(rh["mrr"], 5), gain=round(go["mrr"] - rh["mrr"], 5))

    result.update(arm_hits={a: {kk: round(vv, 6) for kk, vv in arm_hits[a].items() if kk != "n"}
                            for a in ALL_ARMS},
                  arm_n={a: arm_hits[a]["n"] for a in ALL_ARMS}, arm_sigs=arm_sig,
                  lambda_ordinal=lam_ord, lambda_fpe=lam_fpe, lambda_scramble=lam_scr,
                  val_mrr_ordinal=round(val_mrr_ord, 5) if val_mrr_ord == val_mrr_ord else None,
                  val_mrr_fpe=round(val_mrr_fpe, 5) if val_mrr_fpe == val_mrr_fpe else None,
                  lambda_fallback=bool(fb_ord or fb_fpe or fb_scr),
                  lambda_curve_ordinal=curve_ord, lambda_curve_fpe=curve_fpe,
                  by_support_degree=by_support,
                  support_deg_hist={nm: int(((q_sup >= lo) & (q_sup <= hi)).sum())
                                    for lo, hi, nm in SUPPORT_BINS})
    return result


# --------------------------------------------------------------------------- #
# Aggregate + verdict (pre-registered BOTH bands).                            #
# --------------------------------------------------------------------------- #
def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def aggregate_and_verdict(per_seed, bundling=None, cost=None):
    m = {a: _nm([_m(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    H = _sub(m[ORACLE], m[RANDOM])
    recover_gain = _sub(m[GATED_ORD], m[RELATIONAL])           # ordinal recovers over relational?
    match_ground = _sub(m[GROUND_ORD], m[GROUND_FPE])          # ordinal-vs-FPE standalone (>= -MATCH_TOL)
    match_gated = _sub(m[GATED_ORD], m[GATED_FPE])             # ordinal-vs-FPE gated (>= -MATCH_TOL)
    scr_margin = _sub(m[GATED_ORD], m[SCRAMBLE])               # RIGHT-attributes margin
    scr_vs_rel = _sub(m[SCRAMBLE], m[RELATIONAL])
    ground_info = _sub(m[GROUND_ORD], m[RANDOM])
    rel_above_random = _sub(m[RELATIONAL], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    per_seed_gain = [_sub(_m(ps, GATED_ORD), _m(ps, RELATIONAL)) for ps in per_seed]
    valid_gains = [g for g in per_seed_gain if g == g]
    frac_pos = (float(np.mean([1.0 if g > 0 else 0.0 for g in valid_gains])) if valid_gains else float("nan"))

    enough = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(H == H and H >= ORACLE_FIRE_ABS and oracle_ratio == oracle_ratio
                        and oracle_ratio >= ORACLE_FIRE_RATIO)
    rel_valid = bool(rel_above_random == rel_above_random and rel_above_random >= REL_ABOVE_RANDOM_MIN)
    broken = bool(m[RANDOM] == m[RANDOM] and m[RELATIONAL] == m[RELATIONAL]
                  and (m[RANDOM] - m[RELATIONAL]) > BROKEN_EPS)

    consistent = bool(frac_pos == frac_pos and frac_pos >= SEED_CONSISTENCY_FRAC)
    matches_fpe = bool(match_ground == match_ground and match_gated == match_gated
                       and match_ground >= -MATCH_TOL and match_gated >= -MATCH_TOL)
    scr_ok = bool(scr_margin == scr_margin and scr_margin >= SCR_ABS_MARGIN)
    ord_cheaper = bool(cost["ordinal_cheaper"]) if cost else False
    ord_robust = bool(bundling["ordinal_more_bundling_robust"]) if bundling else False

    recovers = bool(recover_gain == recover_gain and recover_gain >= HP_RECOVER_GAIN
                    and matches_fpe and scr_ok and consistent
                    and oracle_fires and rel_valid and not broken)
    partial = bool(recover_gain == recover_gain and recover_gain >= MB_PARTIAL_GAIN
                   and oracle_fires and rel_valid and not broken)
    ord_fails = bool(recover_gain == recover_gain and recover_gain < MB_PARTIAL_GAIN
                     and oracle_fires and rel_valid and not broken)

    if not enough:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"; failure_mode = "TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_NULL_BEATS_RELATIONAL"; failure_mode = "NULL_BEATS_RELATIONAL"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"; failure_mode = "ARENA_NOT_ANSWERABLE"
    elif not rel_valid:
        verdict = "INCONCLUSIVE_RELATIONAL_BASELINE_AT_FLOOR"; failure_mode = "RELATIONAL_BASELINE_AT_FLOOR"
    elif recovers:
        verdict = "HARD_PASS_ORDINAL_MATCHES_OR_BEATS_FPE"; failure_mode = "ORDINAL_MATCHES_OR_BEATS_FPE"
    elif partial:
        verdict = "MIDDLE_BAND_ORDINAL_GROUNDS_BUT_BELOW_FPE"; failure_mode = "ORDINAL_GROUNDS_BUT_BELOW_FPE"
    else:
        verdict = "HARD_FAIL_ORDINAL_FAILS_TO_GROUND"; failure_mode = "ORDINAL_FAILS_TO_GROUND"

    verdict_msg = (
        "%s || HELD-OUT-RELATION MRR [nq=%d]: RELATIONAL=%s | ORDINAL gated=%s ground=%s | FPE gated=%s "
        "ground=%s | match(ord-fpe) ground=%s gated=%s >=-%.3f? %s | recover(ord-rel)=%s>=%.3f? %s "
        "seeds_pos=%s>=%.2f? %s | SCRAMBLE=%s (margin=%s>=%.3f? %s) | RANDOM=%s ORACLE=%s POP=%s || "
        "lambda ord=%s fpe=%s scr=%s | arena: oracle_hd=%s ratio=%sx fires=%s rel>rand=%s? %s broken=%s "
        "|| ordinal_cheaper=%s | ordinal_more_bundling_robust=%s (ord_auc=%s fpe_auc=%s) | fm=%s"
        % (verdict, n_query, _fmt(m[RELATIONAL]), _fmt(m[GATED_ORD]), _fmt(m[GROUND_ORD]),
           _fmt(m[GATED_FPE]), _fmt(m[GROUND_FPE]), _fmt(match_ground), _fmt(match_gated), MATCH_TOL,
           matches_fpe, _fmt(recover_gain), HP_RECOVER_GAIN, recovers, _fmt(frac_pos),
           SEED_CONSISTENCY_FRAC, consistent, _fmt(m[SCRAMBLE]), _fmt(scr_margin), SCR_ABS_MARGIN, scr_ok,
           _fmt(m[RANDOM]), _fmt(m[ORACLE]), _fmt(m[POP]),
           str([ps.get("lambda_ordinal") for ps in per_seed]),
           str([ps.get("lambda_fpe") for ps in per_seed]),
           str([ps.get("lambda_scramble") for ps in per_seed]),
           _fmt(H), (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"), oracle_fires,
           _fmt(rel_above_random), rel_valid, broken, ord_cheaper, ord_robust,
           (bundling.get("ordinal_auc") if bundling else None),
           (bundling.get("fpe_auc") if bundling else None), failure_mode))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, failure_mode=failure_mode, ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        oracle_headroom=_rnd(H), oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio
                                               and oracle_ratio != float("inf")) else None),
        recover_gain_ordinal_minus_relational=_rnd(recover_gain),
        match_ground_ordinal_minus_fpe=_rnd(match_ground),
        match_gated_ordinal_minus_fpe=_rnd(match_gated), matches_fpe=matches_fpe,
        scramble_margin=_rnd(scr_margin), scramble_minus_relational=_rnd(scr_vs_rel),
        grounded_ordinal_minus_random=_rnd(ground_info), relational_minus_random=_rnd(rel_above_random),
        per_seed_gain=[_rnd(g) for g in per_seed_gain], frac_seeds_gain_positive=_rnd(frac_pos, 3),
        lambda_ordinal_per_seed=[ps.get("lambda_ordinal") for ps in per_seed],
        lambda_fpe_per_seed=[ps.get("lambda_fpe") for ps in per_seed],
        lambda_scramble_per_seed=[ps.get("lambda_scramble") for ps in per_seed],
        ordinal_cheaper=ord_cheaper, ordinal_more_bundling_robust=ord_robust,
        encoding_cost=cost, bundling_robustness=bundling,
        bands=dict(ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   MATCH_TOL=MATCH_TOL, HP_RECOVER_GAIN=HP_RECOVER_GAIN, SCR_ABS_MARGIN=SCR_ABS_MARGIN,
                   SEED_CONSISTENCY_FRAC=SEED_CONSISTENCY_FRAC, MB_PARTIAL_GAIN=MB_PARTIAL_GAIN,
                   REL_ABOVE_RANDOM_MIN=REL_ABOVE_RANDOM_MIN, MIN_HELDOUT=MIN_HELDOUT,
                   ORDINAL_LEVELS=ORDINAL_LEVELS, N_FPE_FREQ=N_FPE_FREQ, ROBUST_MARGIN=ROBUST_MARGIN,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, VAL_ENTITY_FRAC=VAL_ENTITY_FRAC,
                   SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough, oracle_fires=oracle_fires, rel_valid=rel_valid, broken=broken,
        consistent=consistent, scramble_ok=scr_ok, recovers=recovers, partial=partial,
        n_query_scored=n_query,
        by_support_degree={ps["seed"]: ps.get("by_support_degree") for ps in per_seed},
    )
    return verdict, verdict_msg, gates


# --------------------------------------------------------------------------- #
# Mechanism self-test: planted latent-consistent arena (deg=3 -> multi-support).#
# The ORDINAL grounding channel MUST recover on the planted arena.             #
# --------------------------------------------------------------------------- #
def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    kg = build_planted_kg(7)
    cost = encoding_cost(len(_PROP_NAMES), ORDINAL_LEVELS, N_FPE_FREQ)
    bundling = bundling_robustness_probe(kg["attr"], kg["eligible"].numpy(), 7)
    res = run_corpus(kg, dict(SELFTEST_CFG), device, 7)
    out = dict(N=res.get("N"), n_test_heldout=res.get("n_test_heldout"),
               n_val_heldout=res.get("n_val_heldout"), n_support=res.get("n_support"),
               n_query=res.get("n_query_scored"), n_val_query=res.get("n_val_query"),
               n_cold=res.get("n_cold"), n_dropped=res.get("n_dropped"),
               lambda_ordinal=res.get("lambda_ordinal"), lambda_fpe=res.get("lambda_fpe"),
               lambda_scramble=res.get("lambda_scramble"),
               encoding_cost=cost, bundling_robustness=bundling)
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted arena produced too few held-out queries (%s)" % res.get("n_query_scored")
        return False, out

    m = {a: res["arm_hits"][a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    gain = m[GATED_ORD] - m[RELATIONAL]
    dilution = m[GROUND_ORD] - m[GATED_ORD]
    scr_margin = m[GATED_ORD] - m[SCRAMBLE]
    ground_info = m[GROUND_ORD] - m[RANDOM]
    oracle_margin = m[ORACLE] - m[RANDOM]
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])
    n_sigs = len(set(res["arm_sigs"].values()))

    oracle_recovers = bool(m[ORACLE] == m[ORACLE] and m[ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    gated_beats_rel = bool(gain == gain and gain >= SELFTEST_GATED_BEATS_REL)
    gated_no_dilute = bool(dilution == dilution and dilution <= SELFTEST_GATED_NO_DILUTE)
    gated_beats_scr = bool(scr_margin == scr_margin and scr_margin >= SELFTEST_GATED_BEATS_SCR)
    ground_carries = bool(ground_info == ground_info and ground_info >= SELFTEST_GROUND_BEATS_RAND)
    rel_above_random = bool((m[RELATIONAL] - m[RANDOM]) >= REL_ABOVE_RANDOM_MIN)
    arms_differ = bool(n_sigs >= DISTINCT_SIG_FLOOR)
    dims_matched = bool(cost["dims_matched"])
    bundling_ran = bool(bundling.get("ordinal_auc") is not None and bundling.get("fpe_auc") is not None)

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res], bundling=bundling, cost=cost)

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["fit_kge_anchor1", "filtered_hits_from_scores", "fit_ridge",
                                        "ordinal_ground_features", "fpe_ground_features",
                                        "bundling_robustness_probe"],
         "exercised_entrypoints": ["fit_kge_anchor1", "filtered_hits_from_scores", "fit_ridge",
                                   "ordinal_ground_features", "fpe_ground_features",
                                   "bundling_robustness_probe"]},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 1, "device": None, "seed": 0, "epochs": 1}},
        {"kind": "guard_baseline_valid", "baseline_score": m[RELATIONAL], "floor_score": max(m[RANDOM], 0.0),
         "guard_name": "ablation_needs_nonfloor_relational", "baseline_name": RELATIONAL,
         "floor_name": RANDOM, "eps": 0.005},
        # POSITIVE control: on the planted arena the ORDINAL-encoded grounding MUST recover -> GATED_ORDINAL
        # beats RELATIONAL, does not dilute below GROUNDED_ORDINAL, beats SCRAMBLE, ORACLE fires.
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(gated_beats_rel and gated_no_dilute
                                                        and gated_beats_scr and oracle_fires),
         "control_name": "PLANTED_ordinal_gate(GATED_ORDINAL recovers; beats REL & SCRAMBLE; no dilution)",
         "headline_name": "ordinal_grounding_recovers_heldout_relation_mrr"},
        {"kind": "metric_moves", "metric_name": "heldout_relation_mrr",
         "values": [m[RANDOM], m[RELATIONAL], m[GATED_ORD], m[GROUND_ORD], m[ORACLE]]},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[SCRAMBLE]],
         "headline_threshold": m[GATED_ORD], "higher_is_pass": True, "margin": SELFTEST_GATED_BEATS_SCR,
         "n_repeats_min": 2, "control_name": "RANDOM_and_SCRAMBLE_below_gated_ordinal_mrr"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "rel_valid", "broken_guard",
                                    "enough_heldout", "recovery_gain_gate", "match_fpe_gate",
                                    "scramble_margin_gate"],
         "exercised_gates": ["arms_differ", "oracle_fires", "rel_valid", "broken_guard",
                             "enough_heldout", "recovery_gain_gate", "match_fpe_gate",
                             "scramble_margin_gate"]},
    ], run_mode="self_test")

    out.update(heldout_mrr={a: round(m[a], 5) for a in ALL_ARMS}, gain=round(gain, 5),
               dilution=round(dilution, 5), scramble_margin=round(scr_margin, 5),
               grounded_info=round(ground_info, 5), oracle_margin=round(oracle_margin, 5),
               oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio
                            and oracle_ratio != float("inf")) else None),
               n_distinct_sigs=n_sigs, oracle_recovers=oracle_recovers, oracle_fires=oracle_fires,
               gated_beats_rel=gated_beats_rel, gated_no_dilute=gated_no_dilute,
               gated_beats_scr=gated_beats_scr, ground_carries=ground_carries,
               rel_above_random=rel_above_random, arms_differ=arms_differ, dims_matched=dims_matched,
               bundling_ran=bundling_ran, ordinal_cheaper=bool(cost["ordinal_cheaper"]),
               selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok))
    ok = bool(oracle_recovers and oracle_fires and gated_beats_rel and gated_no_dilute and gated_beats_scr
              and ground_carries and rel_above_random and arms_differ and dims_matched and bundling_ran
              and bool(cost["ordinal_cheaper"]))
    return ok, out


# --------------------------------------------------------------------------- #
# I/O helpers (start-marker / atomic metrics / crash diagnostic).             #
# --------------------------------------------------------------------------- #
def _out_dir():
    name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    return os.path.join("data", "exp_" + name)


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_metrics(out_dir, metrics):
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(out_dir, diag)


def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    if (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue"):
        return torch.device("cpu")
    want = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want and torch.cuda.is_available()) else "cpu")


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def core_main(run_mode, device):
    out_dir = _out_dir()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s gain=%s dilution=%s scr_margin=%s lam_ord=%s lam_fpe=%s oracle_fires=%s "
         "ordinal_cheaper=%s ordinal_more_bundling_robust=%s vp_ok=%s heldout_mrr=%s"
         % (st_ok, st_res.get("gain"), st_res.get("dilution"), st_res.get("scramble_margin"),
            st_res.get("lambda_ordinal"), st_res.get("lambda_fpe"), st_res.get("oracle_fires"),
            st_res.get("ordinal_cheaper"),
            st_res.get("bundling_robustness", {}).get("ordinal_more_bundling_robust"),
            st_res.get("validity_preflight_ok"), st_res.get("heldout_mrr")))

    if run_mode == "self_test":
        _write_start_marker(out_dir, run_mode, 1)
        if not st_ok:
            _write_metrics(out_dir, dict(
                verdict="HARD_FAIL", run_mode="self_test",
                verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res.get("fail", st_res),
                summary="mechanism selftest failed", elapsed_s=0.0, mechanism_selftest=st_res))
            raise SystemExit(1)
        _write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS ordinal-grounding: planted GATED_ORDINAL beats RELATIONAL, no "
                        "dilution below GROUNDED_ORDINAL, beats SCRAMBLE on held-out-relation MRR; ORACLE "
                        "fires; dims matched to FPE; ordinal cheaper; bundling probe ran",
            summary="SELFTEST_PASS", elapsed_s=0.0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS")
        return
    if not st_ok:
        _write_start_marker(out_dir, run_mode, 1)
        _write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (do not trust the real-data result): %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=0.0, mechanism_selftest=st_res))
        raise SystemExit(1)

    cfg = dict(SMOKE_CFG if run_mode == "smoke" else FULL_CFG)
    seeds = cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    _log("device=%s run_mode=%s seeds=%s k=%s epochs=%s" % (device, run_mode, seeds, cfg["k"], cfg["epochs"]))

    kg = build_mammal_kg()
    _log("mammal KG: N=%d (species=%d) rels=%d edges=%d" % (kg["N"], kg["n_species"], kg["n_rel"],
                                                            kg["edges"].shape[0]))
    cost = encoding_cost(len(_PROP_NAMES), ORDINAL_LEVELS, N_FPE_FREQ)
    bundling = bundling_robustness_probe(kg["attr"], kg["eligible"].numpy(), seeds[0])
    _log("encoding_cost=%s" % json.dumps(cost))
    _log("bundling_robustness: ordinal_auc=%s fpe_auc=%s more_robust=%s ord_curve=%s fpe_curve=%s"
         % (bundling.get("ordinal_auc"), bundling.get("fpe_auc"),
            bundling.get("ordinal_more_bundling_robust"), bundling.get("ordinal_curve"),
            bundling.get("fpe_curve")))

    t0 = time.perf_counter()
    per_seed, seed_failures = [], []
    for seed in seeds:
        try:
            res = run_corpus(kg, cfg, device, seed)
            if res.get("empty") or res["n_query_scored"] < MIN_HELDOUT:
                raise RuntimeError("held-out query edges too few (%d < %d)"
                                   % (res.get("n_query_scored", 0), MIN_HELDOUT))
            if len(set(res["arm_sigs"].values())) < DISTINCT_SIG_FLOOR:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d sigs (< %d)"
                                   % (seed, len(set(res["arm_sigs"].values())), DISTINCT_SIG_FLOOR))
            per_seed.append(res)
            ah = res["arm_hits"]
            _log("seed=%d nq=%d nvq=%d n_sup=%d n_cold=%d lam_ord=%s lam_fpe=%s | MRR REL=%s ORD_g=%s ORD_G=%s "
                 "FPE_g=%s FPE_G=%s SCR=%s RAND=%s ORA=%s POP=%s (%.1fs)"
                 % (seed, res["n_query_scored"], res["n_val_query"], res["n_support"], res["n_cold"],
                    res["lambda_ordinal"], res["lambda_fpe"], _fmt(ah[RELATIONAL]["mrr"]),
                    _fmt(ah[GATED_ORD]["mrr"]), _fmt(ah[GROUND_ORD]["mrr"]), _fmt(ah[GATED_FPE]["mrr"]),
                    _fmt(ah[GROUND_FPE]["mrr"]), _fmt(ah[SCRAMBLE]["mrr"]), _fmt(ah[RANDOM]["mrr"]),
                    _fmt(ah[ORACLE]["mrr"]), _fmt(ah[POP]["mrr"]), time.perf_counter() - t0))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            seed_failures.append(dict(seed=seed, failure_class=type(e).__name__, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))

    elapsed = time.perf_counter() - t0
    if len(per_seed) < expected_n_units:
        _write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=round(elapsed, 3), seed_failures=seed_failures,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, bundling=bundling, cost=cost)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=round(elapsed, 3), anchor_name=ANCHOR_NAME, n_seeds=len(per_seed), seeds=seeds,
                   config=cfg, gates=gates, mechanism_selftest=st_res, seed_failures=seed_failures,
                   per_seed=per_seed, ts_iso=datetime.now(timezone.utc).isoformat(), host=platform.node(),
                   device=str(device))
    _write_metrics(out_dir, metrics)
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % elapsed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    if not args.self_test and not args.smoke and args.run_mode == "full":
        env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if env_mode in ("self_test", "smoke", "full"):
            run_mode = env_mode
    device = _resolve_device(args.device)
    out_dir = _out_dir()
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
