"""GROUNDING GATED-FUSION: recover grounding's standalone strength via a GLASS-BOX learned gate.

WHY THIS CELL EXISTS -- a direct follow-up to exp_grounding_improves_relation_inference_mammal_v1.
  That cell PROVED (landed-VET) grounding carries genuine leak-free signal on held-out relation
  inference: GROUNDED_ONLY mrr=0.618 >> RELATIONAL_ONLY mrr=0.387, and grounding beat POP on 8/8
  seeds. BUT the naive equal-weight fusion (alpha=beta=1, a literal SUM of the relational bundle code
  and the grounded code in the additive-KGE latent) DILUTED grounding down to relational level:
  GROUNDED_FUSED(1:1) mrr=0.398 ~= RELATIONAL, drowning the 0.618 grounding signal.
  MEASURED@d:/AI/hd-instrument/data/exp_grounding_improves_relation_inference_mammal_v1/metrics.json:
    gates.heldout_mrr = {RELATIONAL_ONLY:0.386723, GROUNDED_FUSED:0.397608, GROUNDED_ONLY:0.617996,
                         SCRAMBLE_FUSED:0.360892, RANDOM_CODES:0.023934, ORACLE_ADDITIVE:1.0,
                         BASELINE_POP:0.471661}.
  DIAGNOSIS (VET banked): the fusion failure is a DILUTION / magnitude artifact of the equal-weight
  SUM -- adding two properly-scaled codes doubles the latent magnitude and shifts the head off both
  manifolds, and the relational bundle (larger effective norm) dominates the sum, so grounding is
  drowned. This cell REPLACES the naive average with a GLASS-BOX learned convex gate.

MECHANISM (glass-box, low-dim, interpretable):
  GATED_FUSED head code = (1-lambda) * relational_bundle + lambda * grounded_code   (CONVEX; weights
  sum to 1 so magnitude stays on-manifold, unlike the alpha=beta=1 SUM). lambda in [0,1] is a SINGLE
  learned scalar per seed, chosen by grid-search to MAXIMIZE MRR on a disjoint VALIDATION held-out
  entity split (train / val / test entity partition; ridge grounding map + KGE fit see ONLY train;
  lambda is fit on VAL; GATED is applied to TEST). One inspectable number per seed (reported as
  lambda_star). The KEY property that makes this principled: the pure-grounding endpoint (lambda=1)
  is IN the gate's family, so on VAL the gate can never do worse than GROUNDED_ONLY -- it RECOVERS
  grounding's strength (and adds a relational component only where VAL says it helps), rather than
  diluting it. Cold (0-support) held-out entities have no relational bundle -> pure grounding.

  SCRAMBLE_GATED = the SAME gate pipeline but the grounded code is fit from attributes SHUFFLED across
  entities; its lambda is RE-LEARNED on VAL. Because scrambled grounding hurts VAL MRR, the gate
  should learn lambda_scr -> low (favor relational) -> SCRAMBLE_GATED ~= RELATIONAL and does NOT help.
  This is the must-fail: the learned gate REFUSES useless attributes.

  FUSED_EQUAL_1TO1 = the OLD diluting equal-weight SUM (alpha=beta=1), carried as a diagnostic arm so
  the metrics DIRECTLY show GATED_FUSED beats the naive fusion it replaces.

SCOPE (honest, per VET framing): all held-out queries in this mammal arena are d1 (exactly 1 support
  edge) -- the relational channel is STARVED. This cell rescues low-support entity PLACEMENT via the
  grounded similarity signal; it is NOT a multi-hop-reasoning result. Report it that way.

PRIMARY METRIC = HELD-OUT RELATION inference (filtered MRR + hits@{1,3,10} rank-vs-all, KGE standard,
  degree-unbiased -- NO sampled-negative pool). PAIRED ablation on the SAME held-out-relation queries.

PRE-REGISTERED BANDS (BOTH sides picked BEFORE the run; primary metric filtered MRR; RELATIVE to the
  measured GROUNDED_ONLY reference and RELATIONAL baseline -- ABSOLUTE MRR shifts with the smaller
  train pool but the recovery is a RELATIVE claim so relative bands are robust):
  GATED_FUSION_RECOVERS_GROUNDING (HARD_PASS): the gate recovers grounding's standalone strength
      without diluting below it. ALL of:
        (a) mean (GATED_FUSED - RELATIONAL_ONLY)_mrr >= 0.10   (real recovery, >> the +0.03 dilution
            bar the naive fusion failed; grounding standalone lead was ~0.23 so 0.10 is a strict-but-
            reachable recovery target)
        (b) mean GATED_FUSED_mrr >= GROUNDED_ONLY_mrr - 0.03   (NO dilution below grounding)
        (c) mean (GATED_FUSED - SCRAMBLE_GATED)_mrr >= 0.05    (the RIGHT attributes, not added dims)
        (d) per-seed (GATED - RELATIONAL) > 0 in >= 75% of seeds (multi-seed consistency)
        (e) ORACLE fires AND RELATIONAL_ONLY above RANDOM AND not broken.
  PARTIAL_RECOVERY (MIDDLE_BAND): mean (GATED - RELATIONAL)_mrr >= 0.03 (the gate helps over the pure
      relational baseline) BUT it still falls below GROUNDED_ONLY-0.03 (residual dilution) OR fails the
      scramble-margin / consistency check. The gate improves on the naive fusion but does not fully
      recover grounding.
  GATE_FAILS_TO_RECOVER (HARD_FAIL): mean (GATED - RELATIONAL)_mrr < 0.03 (the learned gate did not
      beat the pure relational baseline -- no recovery), with ORACLE firing.
  Gated INCONCLUSIVE if ORACLE does not fire, too few held-out queries, RELATIONAL at the RANDOM floor,
  or a null (RANDOM) beats the relational baseline (broken readout).

MUST-FAIL: the RIGHT-attributes control is the GATED_FUSED - SCRAMBLE_GATED margin (>= SCR_ABS_MARGIN):
  real attributes must beat SHUFFLED attributes through the same gate. NOTE (pre-registered scope
  clarification): scrambled attributes CAN still lift above the STARVED d1 relational baseline because
  a ridge-placed grounded code is a plausible typical-entity prior that beats a single noisy relational
  estimate -- this is NOT an "added-channel dimensionality" artifact (every arm shares the SAME k-dim
  latent; grounding BLENDS the head code, it does not concatenate extra dims), so the scramble-vs-
  relational delta is REPORTED as a diagnostic (scramble_artifact flag) but does NOT gate HARD_PASS.
  The attribute-specificity claim rests on the GATED - SCRAMBLE margin, the standard KGE real-vs-scramble
  ablation.

## Compute architecture
class (b) sequential-CPU: a 65-entity taxonomy KG (N ~ 125 incl symbols); train/val/test entity split;
  a few tiny additive KGE fits (ADDITIVE scaffold + ORACLE, per seed) via minibatch SGD reused from
  _kge_anchor1_fit + a closed-form ridge grounding map + a lambda grid-search (11 points) over (nq,N)
  cdist score matrices on the VAL queries. Seconds/seed on CPU (N,nq tiny); GPU buys nothing. Storage
  SHARDED (each entity its own code; relations = per-TYPE additive displacements; the only bundle is
  the per-ENTITY anchor mean). device forced cpu on remote_cpu_queue.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 8 arms, >=6 distinct score signatures.
#   EXEMPTED pairs (identical by CORRECT construction, not a bug): (GATED_FUSED, GROUNDED_ONLY) when
#   learned lambda_star==1.0 (pure-grounding endpoint), (SCRAMBLE_GATED, RELATIONAL_ONLY) when
#   lambda_scr==0.0 (pure-relational endpoint). Neither collapses the >=6-distinct floor.
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: recovery is framed RELATIVE to the MEASURED GROUNDED_ONLY reference (0.618 in
#   v1) and RELATIONAL baseline; ORACLE=1.0 saturates and is used ONLY as the arena-answerable gate.
# - baseline_in_band: ORACLE must fire (>=3x RANDOM_mrr AND headroom>=ABS); RANDOM near 1/N floor;
#   RELATIONAL above RANDOM.
# - discriminator survives scale: the ablation is a PAIRED delta on the SAME queries; the planted
#   self-test fires GATED-beats-RELATIONAL + GATED>=GROUNDED-tol + scramble-fails deterministically.
# - HARD_PASS strictly above floor: +0.10 recovery + no-dilution + scramble margin + consistency.
# - HP_SCOPE: the recovery gates apply to GATED_FUSED vs RELATIONAL_ONLY/GROUNDED_ONLY only. ORACLE =
#   positive control (must fire); RANDOM/SCRAMBLE_GATED = must-not-explain controls; GROUNDED_ONLY =
#   the recovery TARGET (reference); FUSED_EQUAL_1TO1 = the diluting-baseline being replaced; POP =
#   fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 8 arms + >=6 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- lambda is LEARNED ON VAL (never on test);
#   split fractions + band FRACTIONS pre-registered, NOT tuned on the real test queries.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - F.1 real_code_path: self-test CALLS the REAL fit_kge_anchor1 + filtered_hits_from_scores + fit_ridge.
# - F.2/F.3 substrate_signature: fit_kge_anchor1 bound with BASE/portable kwargs only.
# - F.4 guard_baseline_valid: RELATIONAL_ONLY (the ablation baseline) validated above RANDOM floor.
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

# Reused proven leaf primitives (attribute wiring + additive fit + ceiling-aware eval) + the v1 arena.
from experiments.exp_grounding_mammal_allometry_xchannel_fpe_v1 import (  # noqa: E402
    load_mammals, _norm_prop, fpe_encode, _PROP_LOG, _PROP_NAMES,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    filtered_hits_from_scores, build_true_by_hr_int, pop_hits,
)
from experiments.exp_grounding_improves_relation_inference_mammal_v1 import (  # noqa: E402
    build_mammal_kg, build_planted_kg, fpe_ground_features, fit_ridge,
    grounded_codes, build_relational_bundle, additive_scores, GAMMA,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402

ANCHOR_NAME = "grounding_gated_fusion_relation_inference_mammal_v1"

# ---- Arm names ----
RELATIONAL = "RELATIONAL_ONLY"      # ablation baseline: anchor-compose bundle only (no grounding)
GATED = "GATED_FUSED"               # mechanism: convex (1-lam)*rel + lam*grd, lam learned on VAL
GROUND_ONLY = "GROUNDED_ONLY"      # recovery TARGET / reference: grounded estimate only
FUSED_EQ = "FUSED_EQUAL_1TO1"      # diagnostic: the OLD diluting equal-weight SUM (alpha=beta=1)
SCRAMBLE = "SCRAMBLE_GATED"        # must-fail: gate over SHUFFLED attributes (lambda re-learned)
RANDOM = "RANDOM_CODES"            # null
ORACLE = "ORACLE_ADDITIVE"         # positive control: held-out folded into the fit = ceiling
POP = "BASELINE_POP"               # frequency incumbent (fit-independence sanity)
GEOM_ARMS = [RELATIONAL, GATED, GROUND_ONLY, FUSED_EQ, SCRAMBLE, RANDOM, ORACLE]
ALL_ARMS = GEOM_ARMS + [POP]

# ---- Relation ids ----
REL_NAMES = ["HAS_ORDER", "HAS_FAMILY", "HAS_CLADE"]
N_REL = 3

EVAL_KS = (1, 3, 10)
CEIL_METRIC = "mrr"

# ---- arena-answerable gate (ORACLE = held-out folded in; near-saturates by construction) ----
ORACLE_FIRE_RATIO = 3.0            # ORACLE_mrr >= 3x RANDOM_mrr (scale-free clear separation)
ORACLE_FIRE_ABS = 0.05            # AND ORACLE_mrr - RANDOM_mrr >= this (non-noise absolute floor)
REL_ABOVE_RANDOM_MIN = 0.02      # RELATIONAL_ONLY must beat RANDOM by this (a real reasoning baseline)

# ---- RELATIVE recovery bands (pre-registered; NOT tuned on real test data) ----
HP_RECOVER_GAIN = 0.10           # HARD_PASS: mean (GATED - RELATIONAL)_mrr >= this (real recovery)
DILUTION_TOL = 0.03             # HARD_PASS: mean GATED_mrr >= GROUNDED_ONLY_mrr - this (no dilution)
SCR_ABS_MARGIN = 0.05           # HARD_PASS: (GATED - SCRAMBLE)_mrr >= this (RIGHT attributes)
SEED_CONSISTENCY_FRAC = 0.75    # HARD_PASS: fraction of seeds with per-seed (GATED-REL) gain > 0
MB_PARTIAL_GAIN = 0.03         # MIDDLE_BAND floor: gate at least beats RELATIONAL by this
SCR_ARTIFACT_MAX = 0.05        # scramble-artifact flag: (SCRAMBLE - RELATIONAL)_mrr > this = suspicious
BROKEN_EPS = 0.01             # broken: a null (RANDOM) beats the RELATIONAL baseline by more than this
MIN_HELDOUT = 15             # min held-out TEST QUERY edges per seed for a valid discriminator
MIN_VAL_QUERY = 8            # min VAL QUERY edges to learn lambda; below this -> fallback lambda=1.0

# ---- split / grounding knobs (pre-registered; NOT tuned on real data) ----
HELDOUT_ENTITY_FRAC = 0.28   # fraction of SPECIES withheld as the TEST held-out set
VAL_ENTITY_FRAC = 0.16       # fraction of SPECIES withheld as the disjoint VAL set (lambda fit only)
SUPPORT_FRAC = 0.34          # fraction of a held-out species' edges reserved as SUPPORT (build bundle)
N_FPE_FREQ = 4               # FPE random-Fourier frequencies per attribute (reuses fpe_encode)
FPE_FREQ_STD = 2.15          # matches the proven mammal-allometry FPE bandwidth
RIDGE_LAM = 1.0              # grounding ridge regularization
LAMBDA_GRID = [round(x, 3) for x in np.linspace(0.0, 1.0, 11).tolist()]  # 0.0,0.1,...,1.0

# ---- self-test planted thresholds (calibrated on the synthetic latent-consistent arena, NOT real) ----
SELFTEST_ORACLE_MRR_MIN = 0.20      # planted: ORACLE (learned held-out codes) mrr at least this
SELFTEST_GATED_BEATS_REL = 0.02     # planted: (GATED - RELATIONAL)_mrr >= this (gate recovers)
SELFTEST_GATED_NO_DILUTE = 0.05     # planted: GATED >= GROUNDED_ONLY - this (no dilution below ground)
SELFTEST_GATED_BEATS_SCR = 0.015    # planted: (GATED - SCRAMBLE)_mrr >= this (RIGHT attributes)
SELFTEST_GROUND_BEATS_RAND = 0.02   # planted: (GROUNDED_ONLY - RANDOM)_mrr >= this (grounding info)
SELFTEST_MIN_HO = 20                # planted: minimum held-out TEST QUERY edges

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
# TRAIN / VAL / TEST held-out-HEAD split. VAL and TEST entity sets are         #
# disjoint and BOTH withheld from every train edge. lambda is fit ONLY on VAL. #
# Each held entity's edges partition into SUPPORT (build bundle) + QUERY.      #
# DROP query edges whose tail symbol is absent from train (unanswerable).      #
# --------------------------------------------------------------------------- #
def _partition_heldout(held_by_head, train_tail_symbols, support_frac, rng):
    support, query = [], []
    n_cold = n_dropped = 0
    for h in sorted(held_by_head.keys()):
        es = held_by_head[h]
        d = len(es)
        order = rng.permutation(d)
        if d == 1:
            n_sup = 0
        else:
            n_sup = max(1, int(round(support_frac * d)))
            n_sup = min(n_sup, d - 1)   # always leave >=1 query edge
        sup_idx = set(int(x) for x in order[:n_sup].tolist())
        if n_sup == 0:
            n_cold += 1
        for j, e in enumerate(es):
            if j in sup_idx:
                support.append(e)
            else:
                if e[2] in train_tail_symbols:
                    query.append(e)
                else:
                    n_dropped += 1
    sup = np.array(support, dtype=np.int64) if support else np.zeros((0, 3), dtype=np.int64)
    qry = np.array(query, dtype=np.int64) if query else np.zeros((0, 3), dtype=np.int64)
    return sup, qry, n_cold, n_dropped


def build_train_val_test_split(kg, test_frac, val_frac, support_frac, seed):
    edges = kg["edges"]
    elig = np.nonzero(kg["eligible"].numpy())[0]
    rng = np.random.default_rng(seed * 100003 + 7)
    perm = rng.permutation(elig)
    n_test = max(1, int(round(test_frac * elig.shape[0])))
    n_val = max(1, int(round(val_frac * elig.shape[0])))
    test_ids = set(int(x) for x in perm[:n_test].tolist())
    val_ids = set(int(x) for x in perm[n_test:n_test + n_val].tolist())

    train, test_by_head, val_by_head = [], {}, {}
    for i in range(edges.shape[0]):
        h, r, t = int(edges[i, 0]), int(edges[i, 1]), int(edges[i, 2])
        if h in test_ids:
            test_by_head.setdefault(h, []).append((h, r, t))
        elif h in val_ids:
            val_by_head.setdefault(h, []).append((h, r, t))
        else:
            train.append((h, r, t))
    train = np.array(train, dtype=np.int64) if train else np.zeros((0, 3), dtype=np.int64)
    train_tail_symbols = set(int(t) for t in train[:, 2].tolist())

    rng2 = np.random.default_rng(seed * 991 + 5)
    t_sup, t_qry, t_cold, t_drop = _partition_heldout(test_by_head, train_tail_symbols, support_frac, rng2)
    rng3 = np.random.default_rng(seed * 977 + 3)
    v_sup, v_qry, v_cold, v_drop = _partition_heldout(val_by_head, train_tail_symbols, support_frac, rng3)

    all_sup = [s for s in (t_sup, v_sup) if s.shape[0]]
    combined_support = np.concatenate(all_sup, axis=0) if all_sup else np.zeros((0, 3), dtype=np.int64)
    return dict(train=train, test_support=t_sup, test_query=t_qry, test_ids=test_ids,
                val_support=v_sup, val_query=v_qry, val_ids=val_ids,
                combined_support=combined_support, n_cold=t_cold, n_dropped=t_drop,
                n_val_cold=v_cold, n_val_dropped=v_drop)


# --------------------------------------------------------------------------- #
# Gate: convex (1-lam)*rel + lam*grd on held rows (cold -> pure grd).          #
# --------------------------------------------------------------------------- #
def _gated_table(X, rel_codes, grd_codes, held_ids, support_deg, lam):
    Xp = X.clone()
    for s in held_ids:
        if support_deg[s] > 0:
            Xp[s] = (1.0 - lam) * rel_codes[s] + lam * grd_codes[s]
        else:
            Xp[s] = grd_codes[s]
    return Xp


def _equal_sum_table(X, rel_codes, grd_codes, held_ids, support_deg):
    """The OLD diluting fusion: alpha=beta=1 SUM (rel + grd) on supported rows; cold -> pure grd."""
    Xp = X.clone()
    for s in held_ids:
        if support_deg[s] > 0:
            Xp[s] = rel_codes[s] + grd_codes[s]
        else:
            Xp[s] = grd_codes[s]
    return Xp


def learn_lambda(X, rel_codes, grd_codes, val_ids, support_deg, D, val_query, all_true_val, device, grid):
    """Grid-search lambda in [0,1] maximizing VAL held-out-relation MRR. Returns (lam*, val_mrr*, curve).

    The pure-grounding endpoint lambda=1.0 is in the grid, so val_mrr* >= GROUNDED_ONLY val MRR by
    construction -> the gate cannot underperform grounding on VAL (recovery, not dilution)."""
    if val_query.shape[0] < MIN_VAL_QUERY:
        return 1.0, float("nan"), {}, True  # fallback: pure grounding (recovers, no dilution)
    best_lam, best_mrr, curve = 1.0, -1.0, {}
    for lam in grid:
        Xp = _gated_table(X, rel_codes, grd_codes, val_ids, support_deg, lam)
        sc = additive_scores(Xp, D, val_query, device)
        mrr = filtered_hits_from_scores(sc, val_query, all_true_val, ks=EVAL_KS)["mrr"]
        curve[lam] = round(float(mrr), 5)
        if mrr > best_mrr:
            best_mrr, best_lam = float(mrr), lam
    return best_lam, best_mrr, curve, False


# --------------------------------------------------------------------------- #
# One corpus run: fit -> learn gate on VAL -> apply to TEST -> score PAIRED.   #
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
    # ADDITIVE scaffold (shared) + ORACLE (test held-out folded in = ceiling).
    X, D = fit_kge_anchor1(train, N, n_rel, k, device, seed, cfg["epochs"], reciprocal=True, lr=A1_LR,
                           n_neg=cfg["n_neg"], batch_size=cfg["batch"])
    Xo, Do = fit_kge_anchor1(train, N, n_rel, k, device, seed, cfg["epochs"],
                             transductive_extra=test_hold_all, reciprocal=True, lr=A1_LR,
                             n_neg=cfg["n_neg"], batch_size=cfg["batch"])
    # RANDOM null codes + readout.
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    elig = kg["eligible"].numpy()
    test_ids = np.array(sorted(sp["test_ids"]), dtype=np.int64)
    val_ids = np.array(sorted(sp["val_ids"]), dtype=np.int64)
    held_all_ids = set(sp["test_ids"]) | set(sp["val_ids"])
    train_species = np.array([i for i in np.nonzero(elig)[0] if i not in held_all_ids], dtype=np.int64)

    # relational bundles for BOTH val + test supported heads (cold rows keep untrained X).
    Xp_rel_all, support_deg = build_relational_bundle(X, D, combined_support, N, device)

    # grounded codes (real attributes) + scrambled attributes (shuffle eligible rows).
    Phi = fpe_ground_features(kg["attr"], N_FPE_FREQ, FPE_FREQ_STD, seed)
    g_real = grounded_codes(Phi, X, train_species, held_all_ids, RIDGE_LAM)
    gS = np.random.default_rng(seed * 4441 + 17)
    elig_ids = np.nonzero(elig)[0]
    perm = elig_ids.copy()
    gS.shuffle(perm)
    attr_scr = kg["attr"].clone()
    attr_scr[elig_ids] = kg["attr"][perm]
    Phi_scr = fpe_ground_features(attr_scr, N_FPE_FREQ, FPE_FREQ_STD, seed)
    g_scr = grounded_codes(Phi_scr, X, train_species, held_all_ids, RIDGE_LAM)

    # learn the gate on VAL (real + scrambled grounding each get their own lambda).
    all_true_val = build_true_by_hr_int(train, val_support, val_query)
    lam_real, val_mrr_real, curve_real, fb_real = learn_lambda(
        X, Xp_rel_all, g_real, val_ids, support_deg, D, val_query, all_true_val, device, LAMBDA_GRID)
    lam_scr, val_mrr_scr, curve_scr, fb_scr = learn_lambda(
        X, Xp_rel_all, g_scr, val_ids, support_deg, D, val_query, all_true_val, device, LAMBDA_GRID)

    # build TEST arm code tables (patch ONLY test held rows).
    Xp_rel = Xp_rel_all  # supported test rows = bundle; cold = untrained X (val rows unused for test scoring)
    Xp_gated = _gated_table(X, Xp_rel_all, g_real, test_ids.tolist(), support_deg, lam_real)
    Xp_eq = _equal_sum_table(X, Xp_rel_all, g_real, test_ids.tolist(), support_deg)
    Xp_scr = _gated_table(X, Xp_rel_all, g_scr, test_ids.tolist(), support_deg, lam_scr)
    Xp_ground = X.clone()
    Xp_ground[test_ids] = g_real[test_ids]

    all_true_test = build_true_by_hr_int(train, test_support, test_query)
    rel_tail_freq = {}
    for i in range(train.shape[0]):
        rr = int(train[i, 1]); tt = int(train[i, 2])
        rel_tail_freq.setdefault(rr, Counter())[tt] += 1

    arm_tables = {RELATIONAL: (Xp_rel, D), GATED: (Xp_gated, D), GROUND_ONLY: (Xp_ground, D),
                  FUSED_EQ: (Xp_eq, D), SCRAMBLE: (Xp_scr, D), RANDOM: (Xr, Dr), ORACLE: (Xo, Do)}
    arm_scores, arm_hits, arm_sig = {}, {}, {}
    for a in GEOM_ARMS:
        Xt, Dt = arm_tables[a]
        arm_scores[a] = additive_scores(Xt, Dt, test_query, device)
        arm_hits[a] = filtered_hits_from_scores(arm_scores[a], test_query, all_true_test, ks=EVAL_KS)
        arm_sig[a] = _sig(arm_scores[a].numpy()[:min(64, arm_scores[a].shape[0])].ravel())
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, test_query, all_true_test, N, ks=EVAL_KS)
    arm_hits[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    # support-degree stratified recovery delta (weak-point localization).
    q_sup = np.array([support_deg[int(test_query[i, 0])] for i in range(test_query.shape[0])],
                     dtype=np.int64)
    by_support = {}
    for lo, hi, nm in SUPPORT_BINS:
        mask = (q_sup >= lo) & (q_sup <= hi)
        idx = np.nonzero(mask)[0]
        if idx.size < 3:
            by_support[nm] = dict(n=int(idx.size), gated=None, relational=None, grounded=None, gain=None)
            continue
        gh = filtered_hits_from_scores(arm_scores[GATED][idx], test_query[idx], all_true_test, ks=(1,))
        rh = filtered_hits_from_scores(arm_scores[RELATIONAL][idx], test_query[idx], all_true_test, ks=(1,))
        ndh = filtered_hits_from_scores(arm_scores[GROUND_ONLY][idx], test_query[idx], all_true_test, ks=(1,))
        by_support[nm] = dict(n=int(idx.size), gated=round(gh["mrr"], 5), relational=round(rh["mrr"], 5),
                              grounded=round(ndh["mrr"], 5), gain=round(gh["mrr"] - rh["mrr"], 5))

    result.update(arm_hits={a: {kk: round(vv, 6) for kk, vv in arm_hits[a].items() if kk != "n"}
                            for a in ALL_ARMS},
                  arm_n={a: arm_hits[a]["n"] for a in ALL_ARMS}, arm_sigs=arm_sig,
                  lambda_star=lam_real, lambda_scramble=lam_scr,
                  val_mrr_at_lambda=round(val_mrr_real, 5) if val_mrr_real == val_mrr_real else None,
                  lambda_fallback=bool(fb_real), lambda_curve=curve_real, lambda_scr_curve=curve_scr,
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


def aggregate_and_verdict(per_seed):
    m = {a: _nm([_m(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    H = _sub(m[ORACLE], m[RANDOM])                            # arena-answerable headroom (saturates)
    recover_gain = _sub(m[GATED], m[RELATIONAL])             # the recovery delta (does the gate recover)
    dilution = _sub(m[GROUND_ONLY], m[GATED])               # >0 means gate fell below grounding
    scr_margin = _sub(m[GATED], m[SCRAMBLE])                 # RIGHT-attributes margin
    scr_vs_rel = _sub(m[SCRAMBLE], m[RELATIONAL])           # scramble-artifact check
    vs_equal = _sub(m[GATED], m[FUSED_EQ])                  # improvement over the naive diluting fusion
    ground_info = _sub(m[GROUND_ONLY], m[RANDOM])
    rel_above_random = _sub(m[RELATIONAL], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    per_seed_gain = [_sub(_m(ps, GATED), _m(ps, RELATIONAL)) for ps in per_seed]
    valid_gains = [g for g in per_seed_gain if g == g]
    frac_pos = (float(np.mean([1.0 if g > 0 else 0.0 for g in valid_gains])) if valid_gains else float("nan"))
    lambdas = [ps.get("lambda_star") for ps in per_seed]

    enough = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(H == H and H >= ORACLE_FIRE_ABS and oracle_ratio == oracle_ratio
                        and oracle_ratio >= ORACLE_FIRE_RATIO)
    rel_valid = bool(rel_above_random == rel_above_random and rel_above_random >= REL_ABOVE_RANDOM_MIN)
    broken = bool(m[RANDOM] == m[RANDOM] and m[RELATIONAL] == m[RELATIONAL]
                  and (m[RANDOM] - m[RELATIONAL]) > BROKEN_EPS)

    consistent = bool(frac_pos == frac_pos and frac_pos >= SEED_CONSISTENCY_FRAC)
    no_dilution = bool(dilution == dilution and dilution <= DILUTION_TOL)
    scr_ok = bool(scr_margin == scr_margin and scr_margin >= SCR_ABS_MARGIN)
    # scramble_artifact is a REPORTED DIAGNOSTIC, NOT a pass-blocker (see prereg note). The fair must-fail
    # is the RIGHT-attributes margin GATED - SCRAMBLE (scr_ok); scrambled attributes lifting above the
    # STARVED d1 relational baseline is the EXPECTED typical-entity-prior effect, and cannot be an
    # "added-channel dimensionality" artifact because every arm shares the SAME k-dim latent (grounding
    # BLENDS the head code, it does not concatenate extra dimensions).
    scramble_artifact = bool(scr_vs_rel == scr_vs_rel and scr_vs_rel > SCR_ARTIFACT_MAX)

    recovers = bool(recover_gain == recover_gain and recover_gain >= HP_RECOVER_GAIN
                    and no_dilution and scr_ok and consistent
                    and oracle_fires and rel_valid and not broken)
    partial = bool(recover_gain == recover_gain and recover_gain >= MB_PARTIAL_GAIN
                   and oracle_fires and rel_valid and not broken)
    gate_fails = bool(recover_gain == recover_gain and recover_gain < MB_PARTIAL_GAIN
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
        verdict = "HARD_PASS_GATED_FUSION_RECOVERS_GROUNDING"; failure_mode = "GATED_FUSION_RECOVERS_GROUNDING"
    elif partial:
        verdict = "MIDDLE_BAND_PARTIAL_RECOVERY"; failure_mode = "PARTIAL_RECOVERY"
    else:
        verdict = "HARD_FAIL_GATE_FAILS_TO_RECOVER"; failure_mode = "GATE_FAILS_TO_RECOVER"

    verdict_msg = (
        "%s || HELD-OUT-RELATION MRR [nq=%d]: RELATIONAL=%s GATED=%s (recover_gain=%s>=%.3f? %s; "
        "seeds_pos=%s>=%.2f? %s) | GROUNDED_ONLY=%s (dilution=%s<=%.3f? %s) FUSED_EQ(1:1)=%s (gate_vs_equal=%s) "
        "| SCRAMBLE=%s (gated_margin=%s>=%.3f? %s; scr_vs_rel=%s artifact? %s) | RANDOM=%s ORACLE=%s POP=%s "
        "|| lambda*=%s | arena: oracle_hd=%s ratio=%sx fires=%s | rel_above_random=%s? %s | broken=%s "
        "| failure_mode=%s"
        % (verdict, n_query, _fmt(m[RELATIONAL]), _fmt(m[GATED]), _fmt(recover_gain), HP_RECOVER_GAIN, recovers,
           _fmt(frac_pos), SEED_CONSISTENCY_FRAC, consistent, _fmt(m[GROUND_ONLY]), _fmt(dilution), DILUTION_TOL,
           no_dilution, _fmt(m[FUSED_EQ]), _fmt(vs_equal), _fmt(m[SCRAMBLE]), _fmt(scr_margin), SCR_ABS_MARGIN,
           scr_ok, _fmt(scr_vs_rel), scramble_artifact, _fmt(m[RANDOM]), _fmt(m[ORACLE]), _fmt(m[POP]),
           str(lambdas), _fmt(H), (_fmt(oracle_ratio) if oracle_ratio != float("inf") else "inf"), oracle_fires,
           _fmt(rel_above_random), rel_valid, broken, failure_mode))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, failure_mode=failure_mode, ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        oracle_headroom=_rnd(H), oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio
                                               and oracle_ratio != float("inf")) else None),
        recover_gain_gated_minus_relational=_rnd(recover_gain),
        dilution_grounded_minus_gated=_rnd(dilution),
        gated_minus_equalfusion=_rnd(vs_equal),
        scramble_margin_gated_minus_scramble=_rnd(scr_margin),
        scramble_minus_relational=_rnd(scr_vs_rel), scramble_artifact=scramble_artifact,
        grounded_only_minus_random=_rnd(ground_info),
        relational_minus_random=_rnd(rel_above_random),
        per_seed_gain=[_rnd(g) for g in per_seed_gain], frac_seeds_gain_positive=_rnd(frac_pos, 3),
        lambda_star_per_seed=lambdas, lambda_scramble_per_seed=[ps.get("lambda_scramble") for ps in per_seed],
        bands=dict(ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   HP_RECOVER_GAIN=HP_RECOVER_GAIN, DILUTION_TOL=DILUTION_TOL, SCR_ABS_MARGIN=SCR_ABS_MARGIN,
                   SEED_CONSISTENCY_FRAC=SEED_CONSISTENCY_FRAC, MB_PARTIAL_GAIN=MB_PARTIAL_GAIN,
                   SCR_ARTIFACT_MAX=SCR_ARTIFACT_MAX, REL_ABOVE_RANDOM_MIN=REL_ABOVE_RANDOM_MIN,
                   MIN_HELDOUT=MIN_HELDOUT, HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC,
                   VAL_ENTITY_FRAC=VAL_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough, oracle_fires=oracle_fires, rel_valid=rel_valid, broken=broken,
        consistent=consistent, no_dilution=no_dilution, scramble_ok=scr_ok,
        recovers=recovers, partial=partial, n_query_scored=n_query,
        by_support_degree={ps["seed"]: ps.get("by_support_degree") for ps in per_seed},
    )
    return verdict, verdict_msg, gates


# --------------------------------------------------------------------------- #
# Mechanism self-test: planted latent-consistent arena (deg=3 -> multi-support).#
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
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(kg, cfg, device, 7)
    out = dict(N=res.get("N"), n_test_heldout=res.get("n_test_heldout"),
               n_val_heldout=res.get("n_val_heldout"), n_support=res.get("n_support"),
               n_query=res.get("n_query_scored"), n_val_query=res.get("n_val_query"),
               n_cold=res.get("n_cold"), n_dropped=res.get("n_dropped"),
               lambda_star=res.get("lambda_star"), lambda_scramble=res.get("lambda_scramble"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted arena produced too few held-out queries (%s)" % res.get("n_query_scored")
        return False, out

    m = {a: res["arm_hits"][a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    gain = m[GATED] - m[RELATIONAL]
    dilution = m[GROUND_ONLY] - m[GATED]
    scr_margin = m[GATED] - m[SCRAMBLE]
    ground_info = m[GROUND_ONLY] - m[RANDOM]
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
    arms_differ = bool(n_sigs >= 6)

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["fit_kge_anchor1", "filtered_hits_from_scores", "fit_ridge"],
         "exercised_entrypoints": ["fit_kge_anchor1", "filtered_hits_from_scores", "fit_ridge"]},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 1, "device": None, "seed": 0, "epochs": 1}},
        {"kind": "guard_baseline_valid", "baseline_score": m[RELATIONAL], "floor_score": max(m[RANDOM], 0.0),
         "guard_name": "ablation_needs_nonfloor_relational", "baseline_name": RELATIONAL,
         "floor_name": RANDOM, "eps": 0.005},
        # POSITIVE control: on the planted arena where attributes carry the latent, the learned gate MUST
        # recover grounding -> GATED beats RELATIONAL, does not dilute below GROUNDED, beats SCRAMBLE.
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(gated_beats_rel and gated_no_dilute
                                                        and gated_beats_scr and oracle_fires),
         "control_name": "PLANTED_gate(GATED recovers grounding; beats REL & SCRAMBLE; no dilution)",
         "headline_name": "gated_fusion_recovers_grounding_heldout_relation_mrr"},
        {"kind": "metric_moves", "metric_name": "heldout_relation_mrr",
         "values": [m[RANDOM], m[RELATIONAL], m[GATED], m[GROUND_ONLY], m[ORACLE]]},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[SCRAMBLE]],
         "headline_threshold": m[GATED], "higher_is_pass": True, "margin": SELFTEST_GATED_BEATS_SCR,
         "n_repeats_min": 2, "control_name": "RANDOM_and_SCRAMBLE_below_gated_mrr"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "rel_valid", "broken_guard",
                                    "enough_heldout", "recovery_gain_gate", "no_dilution_gate",
                                    "scramble_margin_gate"],
         "exercised_gates": ["arms_differ", "oracle_fires", "rel_valid", "broken_guard",
                             "enough_heldout", "recovery_gain_gate", "no_dilution_gate",
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
               rel_above_random=rel_above_random, arms_differ=arms_differ, selftest_verdict=st_verdict,
               validity_preflight_ok=bool(vp_ok))
    ok = bool(oracle_recovers and oracle_fires and gated_beats_rel and gated_no_dilute and gated_beats_scr
              and ground_carries and rel_above_random and arms_differ)
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
    _log("mechanism_selftest ok=%s gain=%s dilution=%s scr_margin=%s lambda*=%s oracle_fires=%s vp_ok=%s heldout_mrr=%s"
         % (st_ok, st_res.get("gain"), st_res.get("dilution"), st_res.get("scramble_margin"),
            st_res.get("lambda_star"), st_res.get("oracle_fires"), st_res.get("validity_preflight_ok"),
            st_res.get("heldout_mrr")))

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
            verdict_msg="SELFTEST_PASS gated-fusion-recovers-grounding: planted GATED beats RELATIONAL, "
                        "does not dilute below GROUNDED, beats SCRAMBLE on held-out-relation MRR; ORACLE fires",
            summary="SELFTEST_PASS", elapsed_s=0.0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS")
        return
    if not st_ok:
        _write_start_marker(out_dir, run_mode, 1)
        _write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (do not trust the real-data recovery): %s" % st_res.get("fail", ""),
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
    t0 = time.perf_counter()
    per_seed, seed_failures = [], []
    for seed in seeds:
        try:
            res = run_corpus(kg, cfg, device, seed)
            if res.get("empty") or res["n_query_scored"] < MIN_HELDOUT:
                raise RuntimeError("held-out query edges too few (%d < %d)"
                                   % (res.get("n_query_scored", 0), MIN_HELDOUT))
            if len(set(res["arm_sigs"].values())) < 6:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d sigs"
                                   % (seed, len(set(res["arm_sigs"].values()))))
            per_seed.append(res)
            ah = res["arm_hits"]
            _log("seed=%d nq=%d nvq=%d n_sup=%d n_cold=%d lam*=%s | MRR REL=%s GATED=%s GND=%s EQ=%s SCR=%s RAND=%s ORA=%s POP=%s (%.1fs)"
                 % (seed, res["n_query_scored"], res["n_val_query"], res["n_support"], res["n_cold"],
                    res["lambda_star"], _fmt(ah[RELATIONAL]["mrr"]), _fmt(ah[GATED]["mrr"]),
                    _fmt(ah[GROUND_ONLY]["mrr"]), _fmt(ah[FUSED_EQ]["mrr"]), _fmt(ah[SCRAMBLE]["mrr"]),
                    _fmt(ah[RANDOM]["mrr"]), _fmt(ah[ORACLE]["mrr"]), _fmt(ah[POP]["mrr"]),
                    time.perf_counter() - t0))
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

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
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
