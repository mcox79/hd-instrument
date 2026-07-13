"""ANCHOR_COMPOSE MAGNITUDE-OPTIMIZATION: two orthogonal levers on the VET-confirmed inductive map-builder.

STRATEGIC FRAME (USER OPTIMIZE-THEN-NATIVIZE): the VET-confirmed ANCHOR_COMPOSE inductive entity-generalizer
(held-out-ENTITY code = FLAT UNWEIGHTED additive mean over support-edge tail estimates) lands filtered-MRR 0.1282
(MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE), ~60-95%
of the commonsense-KG inductive SOTA band (InductivE/ConceptNet MRR ~0.18-0.21; CITED@notes/research_inductive_map_
builder_best_in_class_magnitude_levers_2026-07-13.md Part A). This cell finds the best-performing generalization
STRUCTURE by cleanly attributing per-lever lift, so whatever the OPTIMIZED structure turns out to be is what the
substrate is then required to realize natively.

TWO ORTHOGONAL LEVERS, run as a 2x2 factorial over {composer} x {scorer-fit} for isolated + combined attribution:
  LEVER A (composer; brain: theta-gamma sequential slotting + predictive-coding precision-weighting; field: SIC /
    resonator sequential decode, ~8x more components recovered vs flat readout, CITED@arXiv:2412.00354). Replace the
    FLAT unweighted mean with SIC-PEEL SEQUENTIAL CONSENSUS DECODE: round 0 = the flat mean; each round re-weights
    each support-edge estimate by its cosine agreement with the running consensus (segment-softmax, temperature tau)
    and re-forms the consensus -> outlier / low-agreement support edges are peeled DOWN, inlier edges dominate.
    Reduces EXACTLY to the flat mean at round 0 / when all estimates agree (never hurts the clean case). This is the
    substrate's own peel_sic_readout family (hdlab/cleanup_family.py) recast as a consensus composer over a SET OF
    NOISY ESTIMATES OF ONE TARGET (NOT a bundle-index recovery -- peel_sic_readout's index-decode contract is the
    wrong contract here; this is the "equivalent sequential composer" the drill authorized). Zero-training,
    deterministic, closed-form, fully vectorized (index_add segment ops).
  LEVER B (scorer-fit; field: KGE hard-negative / self-adversarial, +0.01-0.04 MRR, CITED@arXiv:1902.10197,2202.
    09606). The shared scorer (X,D additive fit) is currently self-adversarial-weighted over UNIFORM-RANDOM
    negatives. Lever B refits X,D with IN-BATCH HARD NEGATIVES (a fraction of negatives are real tails of other
    positives = structurally-plausible wrong tails), sharpening rank pressure against plausible confusors. The
    held-out entity STILL receives zero gradient steps -- only the SHARED scorer's fit changes -> the headline
    "zero-training for new entities" property is preserved.

## INFO-CEILING (load-bearing pre-reg insight; compute-the-test-ceiling-before-iterating discipline)
The MEASURED v1 transductive oracle (ORACLE_ADDITIVE, held-out folded in + LEARNED, best-possible IN-arena code
under the uniform scorer) is MRR 0.1373 (MEASURED@...v1/metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE). The
flat-mean baseline 0.1282 is ALREADY 93% of that ceiling. Therefore the COMPOSER lever (A, uniform fit) has only
~+0.009 absolute headroom against its own oracle -- the research note's +0.02 absolute HARD-PASS band is INFEASIBLE
for Lever A in isolation (that band computed headroom above RANDOM=0.137, NOT above ANCHOR=0.009). The SCORER lever
(B) is the one with real headroom because it LIFTS the ceiling itself (a hardneg fit's own oracle can exceed 0.137).
CONSEQUENCE (baked into the bands): Lever A is judged against its uniform-fit oracle headroom (ceiling-relative,
feasible); Lever B against its OWN hardneg-fit oracle; the combined arm's absolute MRR is reported vs the SOTA band.
This is a genuine, pre-registered structural finding: on CSKG the flat mean is near-ceiling for the current scorer,
so the scorer is the bottleneck, not the composer -- the 2x2 measures exactly that.

ARMS (12; all scored PAIRED on the SAME held-out QUERY edges + candidate pool; SHARDED per-entity codes):
  MECHANISM (2x2 composer x fit):
    ANCHOR_COMPOSE      : FLAT + UNIFORM fit == the CONFIRMED v1 baseline (Gate-D positive control: reproduce 0.128).
    ANCHOR_PEEL         : SIC-PEEL + UNIFORM fit  (Lever A isolated).
    ANCHOR_HARDNEG      : FLAT + HARDNEG fit      (Lever B isolated).
    ANCHOR_PEEL_HARDNEG : SIC-PEEL + HARDNEG fit  (combined).
  CONTROLS (on the UNIFORM/confirmed fit unless noted; preserve the confirmed comparison):
    ADDITIVE_TRANSE     : memorize control (uniform fit; held-out code stays random-init).
    RANDOM_CODES        : null (random X + random D).
    ANCHOR_SCRAMBLE     : must-fail (FLAT composer, support RELATION ids scrambled) -> relation signal, not confound.
    ANCHOR_PEEL_SCRAMBLE: must-fail for the NEW composer (PEEL on scrambled relations) -> peel lift is relational,
                          not a decode artifact.
    IDENTITY_SHUFFLE    : must-fail (a derangement donates each held entity a DIFFERENT held entity's composed code)
                          -> the win is entity-specific (CITED v2 identity-closure).
    ORACLE_ADDITIVE     : uniform-fit oracle ceiling (positive control; reproduces v1 0.137; the Lever-A ceiling).
    ORACLE_HARDNEG      : hardneg-fit oracle ceiling (the LIFTED ceiling; attributes how much Lever B raises the wall).
    BASELINE_POP        : frequency incumbent (fit-independence sanity; held-out tails have train-freq 0 -> ~floor).

PRE-REG BANDS (picked BEFORE the run; primary metric = FILTERED MRR rank-vs-ALL, degree-unbiased; b = measured
ANCHOR_COMPOSE baseline in-run; C_uni = ORACLE_ADDITIVE; C_hn = ORACLE_HARDNEG; all HYPOTHESIZED unless MEASURED@):
  GATE-D REPRODUCE (must hold or the whole run is untrustworthy): |b - 0.1282| <= 0.02 (baseline reproduces the
     confirmed v1 MEASURED@...v1 within tolerance at the matched regime k=24/ep=500/k_core=12/support_frac=0.5).
  ORACLE-FIRES : C_uni >= 3x RANDOM AND C_uni - RANDOM >= 0.003 (arena answerable; also required for C_hn).
  LEVER A (PEEL, uniform fit; ceiling-relative because near-ceiling by construction):
     headroom_A = C_uni - b.  HARD-PASS: (PEEL - b) >= max(0.50*headroom_A, MIN_SIG=0.002) AND controls intact.
     HARD-FAIL: (PEEL - b) < 0.20*headroom_A.  MIDDLE otherwise -> degree-stratify (SIC predicts lift concentrates
     at HIGHER support degree). Absolute-lift ALSO reported vs the research +0.02/+0.005 band with the INFEASIBILITY
     flag (headroom_A ~0.009 caps the absolute lift).
  LEVER B (HARDNEG, hardneg fit; the real-headroom lever): HARD-PASS: (HARDNEG - b) >= 0.02 absolute (research band;
     feasible iff the hardneg oracle lifts the ceiling: report C_hn - C_uni). HARD-FAIL: (HARDNEG - b) < 0.005.
     MIDDLE otherwise -> stratify by query-frequency tertile (KGE lit: hardneg gains concentrate on low-freq).
  COMBINED (PEEL_HARDNEG; ceiling C_hn): HARD-PASS: (PEEL_HARDNEG - b) >= 0.03 absolute AND >= max(PEEL-b,HARDNEG-b);
     report absolute MRR vs the InductivE SOTA band 0.18-0.22.
  MUST-FAILS (all required, else the run is BROKEN regardless of lever lift): ORACLE fires; SCRAMBLE controlled
     ((SCRAMBLE-RANDOM) <= 0.25*headroom_A_vsRandom); PEEL_SCRAMBLE controlled likewise vs PEEL; IDENTITY_SHUFFLE
     collapses (retains <= 0.20 of ANCHOR's margin-over-RANDOM); RANDOM/POP at floor; no control beats POP by the
     ceiling-relative broken margin; arms differ (>=8 distinct sigs).

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes : ORACLE_ADDITIVE recovers planted held-out tails + clears RANDOM by the fire gate.
  (2) metric_moves            : MRR MOVES across [RANDOM, ADDITIVE, ANCHOR(flat), ANCHOR_PEEL, ORACLE].
  (3) negative_control_margin : RANDOM + ANCHOR_SCRAMBLE + PEEL_SCRAMBLE + IDENTITY_SHUFFLE below their arm, det >=2.
  (4) full_gates_exercised    : aggregate_and_verdict runs on the planted per-seed, firing every fail-closed gate.
ADVERSARIAL SELF-TEST DISCRIMINATOR (Lever A fires): on a PLANTED arena with INJECTED OUTLIER support edges, SIC-PEEL
recovers held-out tails GENUINELY BETTER than the flat mean ((PEEL - ANCHOR) >= SELFTEST_PEEL_MARGIN) -- proving the
sequential composer works WHERE THERE IS HEADROOM (separating "peel mechanism correct" from "on CSKG flat is already
near-ceiling"). Lever B's win is a data-scale training effect (analytical justification per DISCRIMINATOR-SURVIVES-
SCALE option B); the self-test only asserts the hardneg fit RUNS + yields a distinct valid arm.

## Compute architecture
class (b/c) MIXED: split/partition/POP = sequential-CPU graph ops (no matmul); the 4 additive fits (uniform,
hardneg, uniform-oracle, hardneg-oracle) = minibatch SGD (batched, self-adversarial, neg-chunked on FULL); the FLAT
and SIC-PEEL E_derived constructions = vectorized index_add segment ops (no training, seconds; SIC-PEEL is
BATCHED-GPU-friendly, no Python loop over entities); readouts = query-chunked batched matmul. Storage SHARDED (each
entity its own code; the ONLY bundle is the per-ENTITY support consensus). device=auto (cuda on GPU host); remote_cpu
forces cpu. FULL fits are fit-checkpointed (ckpt_every) so a timeout/outage resumes each arm from its last epoch. A
multi-seed MEMSMOKE (FULL memory footprint, 2 seeds IN-PROCESS, few epochs) validates no-OOM + per-seed empty_cache
BEFORE the multi-hour FULL; the discriminator-fires proof is the self-test + analytical (B), NOT the memsmoke.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 12 arms produce >=8 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: the per-fit oracle IS the measured ceiling; Lever-A bands are ceiling-relative (fractions
#   of the MEASURED uniform-oracle headroom), Lever-B against its OWN measured hardneg-oracle -> every threshold is
#   feasible-by-construction (scales to whatever ceiling the FULL measures).
# - baseline_in_band: ORACLE must fire (>=3x RANDOM AND headroom>=0.003); RANDOM/POP near the 1/N floor; Gate-D
#   reproduces the confirmed baseline within 0.02.
# - discriminator survives scale: Lever A fires on the planted-OUTLIER arena in self-test; on CSKG the ceiling-
#   relative band self-scales. Lever B: analytical (B) -- hardneg is a data-scale training effect; the memsmoke
#   confirms it runs at full memory; the FULL measures it. The confirmed must-fails fire deterministically at
#   self-test scale.
# - HARD-PASS strictly above floor: Lever-A HP 0.50*headroom clears HARD-FAIL 0.20*headroom by 30% of headroom +
#   a MIN_SIG absolute floor; Lever-B HP 0.02 clears HARD-FAIL 0.005 by 0.015.
# - HP_SCOPE: Lever-A gates apply to ANCHOR_PEEL; Lever-B to ANCHOR_HARDNEG; combined to ANCHOR_PEEL_HARDNEG.
#   ORACLE_* = positive controls (must fire); RANDOM/SCRAMBLE/PEEL_SCRAMBLE/IDENTITY_SHUFFLE = must-not-clear-bar;
#   ADDITIVE_TRANSE = memorize head-to-head; POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 12 arms + >=8 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- PEEL_ROUNDS/PEEL_TAU/HARD_NEG_FRAC + all band fractions
#   pre-registered, NOT tuned on real data; the lever bands are FRACTIONS OF THE MEASURED per-fit oracle headroom.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
import json
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

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
    stratify_by_tail_degree, PRIMARY_K,
)
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402

ANCHOR_NAME = "anchor_compose_magnitude_opt_cskg_v1"

# ---- Arm names ----
ANCHOR = "ANCHOR_COMPOSE"            # FLAT + UNIFORM == confirmed v1 baseline (Gate-D reproduce)
PEEL = "ANCHOR_PEEL"                 # Lever A isolated: SIC-PEEL + UNIFORM
HARDNEG = "ANCHOR_HARDNEG"           # Lever B isolated: FLAT + HARDNEG
PEELHN = "ANCHOR_PEEL_HARDNEG"       # combined: SIC-PEEL + HARDNEG
ADDITIVE = "ADDITIVE_TRANSE"         # memorize control (uniform fit; held-out random-init)
RANDOM = "RANDOM_CODES"              # null
SCRAMBLE = "ANCHOR_SCRAMBLE"         # must-fail: FLAT on scrambled relations
PEELSCR = "ANCHOR_PEEL_SCRAMBLE"     # must-fail for the NEW composer: PEEL on scrambled relations
IDSHUF = "IDENTITY_SHUFFLE"          # must-fail: cross-entity donated composed code
ORACLE = "ORACLE_ADDITIVE"           # uniform-fit oracle ceiling (positive control; Lever-A ceiling)
ORACLEHN = "ORACLE_HARDNEG"          # hardneg-fit oracle ceiling (the lifted ceiling; Lever-B attribution)
POP = "BASELINE_POP"                 # frequency incumbent (fit-independence sanity)

MECH_ARMS = [ANCHOR, PEEL, HARDNEG, PEELHN]
GEOM_ARMS = [ANCHOR, PEEL, HARDNEG, PEELHN, ADDITIVE, RANDOM, SCRAMBLE, PEELSCR, IDSHUF, ORACLE, ORACLEHN]
ALL_ARMS = GEOM_ARMS + [POP]

# ---- CEILING-AWARE, DEGREE-UNBIASED evaluation (info-ceiling fix; identical protocol to confirmed v1/v2) ----
EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"
PRIMARY_METRIC = "hits@%d" % PRIMARY_K   # legacy hits@10 (reported, NOT gated)

# ORACLE-fire gate (arena answerable under the primary metric).
ORACLE_FIRE_RATIO = 3.0
ORACLE_FIRE_ABS = 0.003

# ---- Lever hyperparameters (pre-registered; NOT tuned on real data) ----
PEEL_ROUNDS = 6          # SIC-peel consensus rounds (round 0 == flat mean; IRLS converges to reject outliers)
PEEL_TAU = 0.5           # agreement softmax temperature (mild; tau->inf reduces to flat mean; low tau over-rejects)
HARD_NEG_FRAC = 0.5      # fraction of n_neg drawn as in-batch hard negatives in the hardneg fit

# ---- Per-lever bands (ceiling-relative where headroom is near-capped) ----
# b = measured ANCHOR_COMPOSE baseline; C_uni = ORACLE_ADDITIVE; C_hn = ORACLE_HARDNEG.
GATED_REPRODUCE_TARGET = 0.1282   # MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json
GATED_REPRODUCE_TOL = 0.02        # |b - target| <= this (Gate-D reproduce-at-test-regime)
A_HP_CEIL_FRAC = 0.50             # Lever A HARD-PASS: (PEEL-b) >= 0.50 * (C_uni - b)
A_HF_CEIL_FRAC = 0.20             # Lever A HARD-FAIL: (PEEL-b) < 0.20 * (C_uni - b)
MIN_SIG_MRR = 0.002               # absolute significance floor (Lever A HP must also clear this)
B_HP_ABS = 0.02                   # Lever B HARD-PASS: (HARDNEG-b) >= this absolute (research band)
B_HF_ABS = 0.005                  # Lever B HARD-FAIL: (HARDNEG-b) < this
COMBO_HP_ABS = 0.03               # combined HARD-PASS: (PEEL_HARDNEG-b) >= this absolute
SOTA_LO, SOTA_HI = 0.18, 0.22     # InductivE/ConceptNet commonsense-KG SOTA band (CITED research note Part A)
SCRAMBLE_CEIL_FRAC = 0.25         # (SCRAMBLE-RANDOM) <= 0.25 * (ANCHOR-RANDOM); same for PEEL_SCRAMBLE vs PEEL
IDSHUF_COLLAPSE_RATIO = 0.20      # IDENTITY_SHUFFLE retains <= 20% of ANCHOR's margin-over-RANDOM
CONTROL_LOSE_EPS = 0.005          # broken-test guard base
MIN_HELDOUT = 20                  # min held-out QUERY edges for a valid discriminator
MIN_STRAT_Q = 8                   # min queries in a stratum to report its margin

# ---- Held-out-entity split knobs (pre-registered; matched to confirmed v1/v2) ----
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5

# ---- self-test planted thresholds (calibrated on the synthetic outlier arena, NOT real data) ----
SELFTEST_ORACLE_MRR_MIN = 0.25
SELFTEST_ANCHOR_MRR_MIN = 0.10        # planted: ANCHOR (flat) still recovers (clean edges present)
SELFTEST_AC_BEATS_RANDOM_MRR = 0.05
SELFTEST_SCRAMBLE_MARGIN_MRR = 0.03
SELFTEST_PEEL_MARGIN = 0.02           # ADVERSARIAL: (PEEL - ANCHOR) >= this on the planted OUTLIER arena
SELFTEST_PEELSCR_MARGIN = 0.02        # (PEEL - PEEL_SCRAMBLE) >= this (peel lift is relational)
SELFTEST_IDSHUF_COLLAPSE_RATIO = 0.30
SELFTEST_MIN_HO = 8

# ---- hardest relation tertile (weak-point-localization target) ----
HARDEST_TERTILE_RELS = frozenset([
    "hascontext", "antonym", "mayhaveproperty", "locatednear", "xattr", "haslexicalunit", "hassubevent",
    "motivatedbygoal", "desires", "synonym", "usedfor", "similarto", "hasprerequisite", "xwant",
])

SCORE_CHUNK = 256

# Config profiles. SELFTEST/MEMSMOKE/FULL exercise the SAME split->fit->compose->score->verdict path.
# SELFTEST epochs=200: a MODERATELY-trained fit so clean support estimates are not razor-tight and the planted
# OUTLIER support edges materially drag the flat mean -> SIC-PEEL has genuine headroom to recover (the discriminator
# fires). At high epochs the fit reconciles cleanly and flat is already near-ceiling (peel margin ~0; this mirrors the
# CSKG near-ceiling situation the bands are designed for) -- the self-test's job is to prove the composer WORKS WHERE
# THERE IS HEADROOM, which the moderately-trained outlier arena provides.
SELFTEST_CFG = dict(k=12, epochs=200, n_neg=32, batch=4096,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO)
# MEMSMOKE = FULL memory footprint (full N + k=24 + n_neg=128 + neg_chunk) but few epochs + 2 seeds. Proves no-OOM
# across the 4 fits (uniform + hardneg + 2 oracles) + per-seed empty_cache BEFORE the multi-hour FULL.
MEMSMOKE_CFG = dict(k=24, epochs=25, n_neg=128, batch=8192, neg_chunk=16,
                    heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                    cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                    n_heldout_eval=2000, min_heldout=10, seeds=[7, 13])
# FULL: k=24/ep=500/k_core=12/support_frac=0.5 = the confirmed v1/v2 regime so ANCHOR_COMPOSE REPRODUCES 0.128
# (Gate-D positive control). 2 seeds (matches v2 identity-closure) -> 4 fits x 2 seeds ~ 3h; ckpt_every makes each
# fit outage-resumable so a timeout resumes rather than restarts.
FULL_CFG = dict(k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, ckpt_every=20,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_heldout_eval=3000, min_heldout=MIN_HELDOUT, seeds=[7, 13])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Planted arena (self-contained; adds OUTLIER support injection so FLAT is dragged but SIC-PEEL is robust).
# ---------------------------------------------------------------------------

def build_planted_transe_arena(seed, n_ent=300, n_rel=6, k_lat=8, deg=4, w_scale=1.0, outlier_per_node=2):
    """Planted TransE-consistent arena where the RELATION operator is necessary. Each entity h emits `deg` CLEAN
    edges (h,r,t) with t = argmin ||z - (z[h]+w[r])||. Then `outlier_per_node` OUTLIER in-edges (h_rand,r_rand,t)
    are injected per tail t: z[h_rand]+w[r_rand] is a random far position -> a per-edge estimate FAR from z[t].
    In a held-out t's SUPPORT set these outliers DRAG the flat mean but DISAGREE with the inlier consensus, so
    SIC-PEEL down-weights them -> peel recovers z[t] better than flat. Deterministic (default_rng + dedup)."""
    rng = np.random.default_rng(seed * 100019 + 3)
    z = rng.standard_normal((n_ent, k_lat))
    w = rng.standard_normal((n_rel, k_lat)) * w_scale
    edges = []
    for h in range(n_ent):
        rels = rng.choice(n_rel, size=deg, replace=False)
        for r in rels:
            target = z[h] + w[r]
            d = np.linalg.norm(z - target, axis=1)
            d[h] = np.inf
            t = int(np.argmin(d))
            edges.append(("e%d" % h, "r%d" % r, "e%d" % t))
    # inject outlier in-edges per tail (random head + random relation -> far estimate for that tail)
    for t_node in range(n_ent):
        for _ in range(int(outlier_per_node)):
            h2 = int(rng.integers(n_ent))
            r2 = int(rng.integers(n_rel))
            if h2 != t_node:
                edges.append(("e%d" % h2, "r%d" % r2, "e%d" % t_node))
    return list(dict.fromkeys(edges))   # order-preserving dedup (cross-process determinism)


def build_heldout_entity_split_ac(pool_lbl, ent2i, frac, support_frac, seed):
    n_ent = len(ent2i)
    rng = np.random.default_rng(seed * 100003 + 7)
    n_hold = max(1, int(frac * n_ent))
    hold_ids = set(int(x) for x in rng.choice(n_ent, size=n_hold, replace=False))
    train_lbl = []
    held_by_tail = defaultdict(list)
    for (h, r, t) in pool_lbl:
        hi = ent2i[h]; ti = ent2i[t]
        h_hold = hi in hold_ids; t_hold = ti in hold_ids
        if not h_hold and not t_hold:
            train_lbl.append((h, r, t))
        elif t_hold and not h_hold:
            held_by_tail[ti].append((h, r, t))
    support_lbl, query_lbl = [], []
    n_cold = 0
    rng2 = np.random.default_rng(seed * 991 + 5)
    for ti in sorted(held_by_tail.keys()):
        edges = held_by_tail[ti]
        d = len(edges)
        if d == 1:
            query_lbl.append(edges[0]); n_cold += 1
            continue
        order = rng2.permutation(d)
        n_sup = max(1, int(round(support_frac * d)))
        n_sup = min(n_sup, d - 1)
        sup_idx = set(int(x) for x in order[:n_sup].tolist())
        for j, e in enumerate(edges):
            (support_lbl if j in sup_idx else query_lbl).append(e)
    return train_lbl, support_lbl, query_lbl, hold_ids, n_cold


# ---------------------------------------------------------------------------
# Composers: FLAT (baseline), SIC-PEEL (Lever A), IDENTITY_SHUFFLE (must-fail). All zero-training, vectorized.
# ---------------------------------------------------------------------------

def _support_tensors(support_int, device, rel_perm=None):
    h = torch.from_numpy(support_int[:, 0]).long().to(device)
    r_np = support_int[:, 1].copy()
    if rel_perm is not None:
        r_np = rel_perm[r_np]
    r = torch.from_numpy(r_np).long().to(device)
    t = torch.from_numpy(support_int[:, 2]).long().to(device)
    return h, r, t


def build_flat_compose_codes(X, D, support_int, device, rel_perm=None):
    """FLAT unweighted additive mean over support-edge tail estimates (the CONFIRMED baseline composer)."""
    N, k = X.shape[0], X.shape[1]
    Xp = X.clone()
    support_deg = np.zeros(N, dtype=np.int64)
    if support_int.shape[0] == 0:
        return Xp, support_deg
    h, r, t = _support_tensors(support_int, device, rel_perm)
    est = X[h] + D[r]
    acc = torch.zeros(N, k, device=device, dtype=X.dtype)
    acc.index_add_(0, t, est)
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    cnt.index_add_(0, t, torch.ones(t.shape[0], device=device, dtype=X.dtype))
    mask = cnt > 0
    Xp[mask] = acc[mask] / cnt[mask].unsqueeze(1)
    support_deg = cnt.detach().to("cpu").numpy().astype(np.int64)
    return Xp, support_deg


def build_sic_peel_codes(X, D, support_int, device, rounds=PEEL_ROUNDS, tau=PEEL_TAU, rel_perm=None, eps=1e-12):
    """SIC-PEEL SEQUENTIAL CONSENSUS DECODE (Lever A). Round 0 = flat mean; each round re-weights each support-edge
    estimate by its cosine agreement with the running per-tail consensus (segment-softmax, temperature tau) and
    re-forms the consensus. Outlier/low-agreement estimates are peeled DOWN; reduces to the flat mean at round 0 or
    tau->inf. Fully vectorized index_add segment ops (batched-GPU-friendly; no Python loop over entities)."""
    N, k = X.shape[0], X.shape[1]
    Xp = X.clone()
    support_deg = np.zeros(N, dtype=np.int64)
    if support_int.shape[0] == 0:
        return Xp, support_deg
    h, r, t = _support_tensors(support_int, device, rel_perm)
    est = X[h] + D[r]                                        # (S,k)
    S = est.shape[0]
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    cnt.index_add_(0, t, torch.ones(S, device=device, dtype=X.dtype))
    mask = cnt > 0
    acc = torch.zeros(N, k, device=device, dtype=X.dtype)
    acc.index_add_(0, t, est)
    mu = torch.zeros(N, k, device=device, dtype=X.dtype)
    mu[mask] = acc[mask] / cnt[mask].unsqueeze(1)            # round-0 consensus == flat mean
    en = est / (est.norm(dim=1, keepdim=True) + eps)         # unit estimates (fixed across rounds)
    for _ in range(int(rounds)):
        mu_at = mu[t]                                        # (S,k) consensus for each edge's tail
        mn = mu_at / (mu_at.norm(dim=1, keepdim=True) + eps)
        c = (en * mn).sum(dim=1)                             # (S,) cosine agreement in [-1,1]
        wexp = torch.exp(c / float(tau))                     # (S,)
        denom = torch.zeros(N, device=device, dtype=X.dtype)
        denom.index_add_(0, t, wexp)
        wseg = wexp / (denom[t] + eps)                       # (S,) segment-softmax weight (sums to 1 per tail)
        acc2 = torch.zeros(N, k, device=device, dtype=X.dtype)
        acc2.index_add_(0, t, est * wseg.unsqueeze(1))
        mu = torch.zeros(N, k, device=device, dtype=X.dtype)
        mu[mask] = acc2[mask]                                # weighted consensus (weights already normalized)
    Xp[mask] = mu[mask]
    support_deg = cnt.detach().to("cpu").numpy().astype(np.int64)
    return Xp, support_deg


def build_identity_shuffle_codes(Xa, Xcompose, support_deg, device, seed):
    """CROSS-ENTITY IDENTITY-SHUFFLE must-fail: a single-cycle derangement donates each support-bearing held entity
    a DIFFERENT held entity's composed code. If the win survives, the anchor IDENTITY does not matter."""
    Xid = Xa.clone()
    present = np.where(support_deg > 0)[0]
    n = present.shape[0]
    if n >= 2:
        rng = np.random.default_rng(seed * 5557 + 23)
        order = rng.permutation(n)
        recipient = present[order]
        donor = present[order[(np.arange(n) + 1) % n]]
        r_idx = torch.from_numpy(recipient).long().to(device)
        d_idx = torch.from_numpy(donor).long().to(device)
        Xid[r_idx] = Xcompose[d_idx]
    return Xid


# ---------------------------------------------------------------------------
# Fit the 4 arms (uniform, hardneg, uniform-oracle, hardneg-oracle) + build codes + score PAIRED.
# ---------------------------------------------------------------------------

def _mk_ckpt(ckpt_dir, ckpt_every, tag, seed):
    if ckpt_dir is None or not ckpt_every:
        return None
    return FitCheckpoint(ckpt_dir, "%s_seed%d" % (tag, seed), ckpt_every)


def fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                  rel_tail_freq, all_true, ckpt_dir=None):
    k = cfg["k"]; epochs = cfg["epochs"]; n_neg = cfg["n_neg"]; batch = cfg["batch"]
    neg_chunk = cfg.get("neg_chunk"); ckpt_every = cfg.get("ckpt_every")

    def _ec():
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    # (1) UNIFORM additive fit (confirmed): shared by ANCHOR/PEEL/ADDITIVE/SCRAMBLE/PEELSCR/IDSHUF.
    Xu, Du = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                             n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "uniform", seed))
    _ec()
    # (2) HARDNEG additive fit (Lever B): shared by HARDNEG/PEELHN.
    Xh, Dh = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                             n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk, hard_neg_frac=HARD_NEG_FRAC,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "hardneg", seed))
    _ec()
    # (3) UNIFORM oracle (held-out folded in) = Lever-A ceiling / confirmed positive control.
    Xou, Dou = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold_all,
                               reciprocal=True, lr=A1_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                               ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "oracle_uniform", seed))
    _ec()
    # (4) HARDNEG oracle (held-out folded in + hardneg) = Lever-B lifted ceiling.
    Xoh, Doh = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold_all,
                               reciprocal=True, lr=A1_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                               hard_neg_frac=HARD_NEG_FRAC,
                               ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "oracle_hardneg", seed))
    _ec()
    # RANDOM codes (random X + random D + additive readout) = the null.
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    # composed codes (zero-training) on each fit
    Xflat_u, support_deg = build_flat_compose_codes(Xu, Du, support_int, device)          # ANCHOR (flat+uniform)
    Xpeel_u, _ = build_sic_peel_codes(Xu, Du, support_int, device)                        # PEEL (peel+uniform)
    Xflat_h, _ = build_flat_compose_codes(Xh, Dh, support_int, device)                    # HARDNEG (flat+hardneg)
    Xpeel_h, _ = build_sic_peel_codes(Xh, Dh, support_int, device)                        # PEELHN (peel+hardneg)
    Xscr, _ = build_flat_compose_codes(Xu, Du, support_int, device, rel_perm=rel_perm)    # SCRAMBLE
    Xpeelscr, _ = build_sic_peel_codes(Xu, Du, support_int, device, rel_perm=rel_perm)    # PEEL_SCRAMBLE
    Xid = build_identity_shuffle_codes(Xu, Xflat_u, support_deg, device, seed)            # IDENTITY_SHUFFLE

    def _sc(X, D):
        return additive_direct_scores(X, D, query_int, device, chunk=SCORE_CHUNK)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    for name, sc in [
        (ANCHOR, _sc(Xflat_u, Du)),
        (PEEL, _sc(Xpeel_u, Du)),
        (HARDNEG, _sc(Xflat_h, Dh)),
        (PEELHN, _sc(Xpeel_h, Dh)),
        (ADDITIVE, _sc(Xu, Du)),
        (SCRAMBLE, _sc(Xscr, Du)),
        (PEELSCR, _sc(Xpeelscr, Du)),
        (IDSHUF, _sc(Xid, Du)),
        (ORACLE, _sc(Xou, Dou)),
        (ORACLEHN, _sc(Xoh, Doh)),
        (RANDOM, _sc(Xr, Dr)),
    ]:
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    del Xu, Du, Xh, Dh, Xou, Dou, Xoh, Doh, Xr, Dr, Xflat_u, Xpeel_u, Xflat_h, Xpeel_h, Xscr, Xpeelscr, Xid
    _ec()
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, support_deg=support_deg)


# ---------------------------------------------------------------------------
# Weak-point localization: per anchor-support-degree bin (the load-bearing stratifier per VET), per global-degree
# tertile, per relation-tertile -- reporting per-degree LIFT for all 4 mechanism arms.
# ---------------------------------------------------------------------------

def _hits_subset(scores, query_int, all_true, mask, k=PRIMARY_K):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), mrr=float("nan"), n=0)
    sub = filtered_hits_from_scores(scores[idx], query_int[idx], all_true, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 5), mrr=round(sub["mrr"], 6), n=int(idx.size))


def _pop_subset(rel_tail_freq, query_int, all_true, n_ent, mask, k=PRIMARY_K):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return dict(hits=float("nan"), mrr=float("nan"), n=0)
    sub, _ = pop_hits(rel_tail_freq, query_int[idx], all_true, n_ent, ks=(k,))
    return dict(hits=round(sub["hits@%d" % k], 5), mrr=round(sub["mrr"], 6), n=int(idx.size))


SUPPORT_BINS = [(0, 0, "cold"), (1, 1, "d1"), (2, 3, "d2_3"), (4, 7, "d4_7"), (8, 10 ** 9, "d8plus")]


def localize_weak_points(arm_scores, query_int, all_true, support_deg, node_degree, rel_i2lbl,
                         rel_tail_freq, N):
    nq = query_int.shape[0]
    gold = query_int[:, 2]
    q_support = np.array([support_deg[int(g)] for g in gold], dtype=np.int64)
    strat, tert = stratify_by_tail_degree(query_int, node_degree)
    q_hardest = np.array([rel_i2lbl.get(int(query_int[i, 1]), "") in HARDEST_TERTILE_RELS
                          for i in range(nq)], dtype=bool)
    report_arms = [ANCHOR, PEEL, HARDNEG, PEELHN, ADDITIVE, RANDOM, IDSHUF, ORACLE, ORACLEHN]

    def _by_mask(mask):
        out = {a: _hits_subset(arm_scores[a], query_int, all_true, mask) for a in report_arms}
        out[POP] = _pop_subset(rel_tail_freq, query_int, all_true, N, mask)
        return out

    by_support = {}
    for lo, hi, name in SUPPORT_BINS:
        by_support[name] = _by_mask((q_support >= lo) & (q_support <= hi))
    by_gdeg_tertile = {nm: _by_mask(strat == si) for si, nm in enumerate(["low", "mid", "high"])}
    fair_lowmid = _by_mask((strat == 0) | (strat == 1))
    by_reltertile = dict(hardest=_by_mask(q_hardest), rest=_by_mask(~q_hardest))
    return dict(by_support_degree=by_support, by_global_degree_tertile=by_gdeg_tertile,
                fair_low_mid=fair_lowmid, by_relation_tertile=by_reltertile,
                global_degree_tertile_bounds=tert,
                support_deg_hist={name: int(((q_support >= lo) & (q_support <= hi)).sum())
                                  for lo, hi, name in SUPPORT_BINS})


# ---------------------------------------------------------------------------
# One corpus run.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None, localize=True):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    rel_i2lbl = {v: k for k, v in rel2i.items()}
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = build_heldout_entity_split_ac(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total = len(query_lbl)

    if cfg.get("n_heldout_eval") and n_query_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_lbl = [query_lbl[i] for i in idx]

    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    hold_all = np.concatenate([support_int, query_int], axis=0) if query_int.shape[0] else support_int
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, support_int, query_int)

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    fs = fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                       gd.rel_tail_freq, all_true, ckpt_dir=ckpt_dir)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 5) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
    )
    if localize:
        result["localization"] = localize_weak_points(
            fs["arm_scores"], query_int, all_true, fs["support_deg"], gd.node_degree, rel_i2lbl,
            gd.rel_tail_freq, N)
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def _h10(ps, arm):
    return ps["arm_hits"][arm].get(PRIMARY_METRIC, float("nan"))


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def _sub(a, b):
    return (a - b) if (a == a and b == b) else float("nan")


def _per_support_lift(per_seed):
    """Per anchor-support-degree bin: mean MRR per mechanism arm + lift over ANCHOR (the load-bearing stratifier)."""
    out = {}
    for lo, hi, name in SUPPORT_BINS:
        arm_mrr = {}
        for a in MECH_ARMS:
            vals = []
            ns = []
            for ps in per_seed:
                cell = ps.get("localization", {}).get("by_support_degree", {}).get(name, {}).get(a, {})
                if cell.get("n", 0) >= 1 and cell.get("mrr", float("nan")) == cell.get("mrr", float("nan")):
                    vals.append(cell["mrr"]); ns.append(cell["n"])
            arm_mrr[a] = (round(_nm(vals), 6) if vals else None)
        b = arm_mrr.get(ANCHOR)
        lift = {a: (round(arm_mrr[a] - b, 6) if (arm_mrr[a] is not None and b is not None) else None)
                for a in [PEEL, HARDNEG, PEELHN]}
        n_tot = int(_nm([ps.get("localization", {}).get("support_deg_hist", {}).get(name, 0) for ps in per_seed]))
        out[name] = dict(arm_mrr=arm_mrr, lift_over_anchor=lift, n=n_tot)
    return out


def aggregate_and_verdict(per_seed):
    m = {a: _nm([_m(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    h10 = {a: _nm([_h10(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    b = m[ANCHOR]                                              # confirmed baseline (in-run)
    C_uni = m[ORACLE]; C_hn = m[ORACLEHN]
    rand = m[RANDOM]

    # ---- Gate-D reproduce (baseline reproduces confirmed v1 within tolerance) ----
    reproduce_ok = bool(b == b and abs(b - GATED_REPRODUCE_TARGET) <= GATED_REPRODUCE_TOL)

    # ---- ORACLE-fire gate (uniform oracle answerable) ----
    oracle_headroom = _sub(C_uni, rand)
    oracle_ratio = _ratio(C_uni, rand)
    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)

    # ---- per-lever lift ----
    lift_peel = _sub(m[PEEL], b)
    lift_hardneg = _sub(m[HARDNEG], b)
    lift_combo = _sub(m[PEELHN], b)
    ceiling_lift_B = _sub(C_hn, C_uni)                         # how much Lever B raises the wall

    # ---- Lever A ceiling-relative bands (headroom vs the uniform oracle) ----
    headroom_A = _sub(C_uni, b)
    a_hp_target = (max(A_HP_CEIL_FRAC * headroom_A, MIN_SIG_MRR) if headroom_A == headroom_A else float("nan"))
    a_hf_target = (A_HF_CEIL_FRAC * headroom_A if headroom_A == headroom_A else float("nan"))
    peel_hard_pass = bool(lift_peel == lift_peel and a_hp_target == a_hp_target and lift_peel >= a_hp_target)
    peel_hard_fail = bool(lift_peel == lift_peel and a_hf_target == a_hf_target and lift_peel < a_hf_target)
    peel_middle = bool(lift_peel == lift_peel and not peel_hard_pass and not peel_hard_fail)

    # ---- Lever B absolute bands (real headroom via the lifted ceiling) ----
    hardneg_hard_pass = bool(lift_hardneg == lift_hardneg and lift_hardneg >= B_HP_ABS)
    hardneg_hard_fail = bool(lift_hardneg == lift_hardneg and lift_hardneg < B_HF_ABS)
    hardneg_middle = bool(lift_hardneg == lift_hardneg and not hardneg_hard_pass and not hardneg_hard_fail)

    # ---- combined ----
    best_isolated = max((v for v in (lift_peel, lift_hardneg) if v == v), default=float("nan"))
    combo_hard_pass = bool(lift_combo == lift_combo and lift_combo >= COMBO_HP_ABS
                           and best_isolated == best_isolated and lift_combo >= best_isolated)
    best_arm = max(MECH_ARMS, key=lambda a: (m[a] if m[a] == m[a] else -1.0))
    best_abs_mrr = m[best_arm]
    reaches_sota = bool(best_abs_mrr == best_abs_mrr and best_abs_mrr >= SOTA_LO)

    # ---- must-fail controls ----
    d_scramble = _sub(m[SCRAMBLE], rand)
    d_peelscr = _sub(m[PEELSCR], rand)
    scramble_ceiling = (SCRAMBLE_CEIL_FRAC * _sub(b, rand)) if _sub(b, rand) == _sub(b, rand) else float("nan")
    peelscr_ceiling = (SCRAMBLE_CEIL_FRAC * _sub(m[PEEL], rand)) if _sub(m[PEEL], rand) == _sub(m[PEEL], rand) else float("nan")
    scramble_controlled = bool(d_scramble == d_scramble and scramble_ceiling == scramble_ceiling
                               and d_scramble <= scramble_ceiling)
    peelscr_controlled = bool(d_peelscr == d_peelscr and peelscr_ceiling == peelscr_ceiling
                              and d_peelscr <= peelscr_ceiling)
    anchor_margin = _sub(b, rand)
    idshuf_margin = _sub(m[IDSHUF], rand)
    idshuf_collapse_ratio = _ratio(idshuf_margin, anchor_margin)
    idshuf_collapses = bool(idshuf_collapse_ratio == idshuf_collapse_ratio
                            and idshuf_collapse_ratio <= IDSHUF_COLLAPSE_RATIO)
    broken_margin = max(CONTROL_LOSE_EPS, SCRAMBLE_CEIL_FRAC * headroom_A) if headroom_A == headroom_A else CONTROL_LOSE_EPS
    broken = bool((m[RANDOM] == m[RANDOM] and m[POP] == m[POP] and (m[RANDOM] - m[POP]) > broken_margin)
                  or (m[SCRAMBLE] == m[SCRAMBLE] and m[POP] == m[POP] and (m[SCRAMBLE] - m[POP]) > broken_margin))

    all_sigs = set()
    for ps in per_seed:
        all_sigs |= set(ps.get("arm_sigs", {}).values())
    arms_differ = bool(len(all_sigs) >= 8)

    must_fails_ok = bool(oracle_fires and scramble_controlled and peelscr_controlled and idshuf_collapses
                         and not broken and arms_differ)

    # ---- overall verdict ----
    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif not reproduce_ok:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_REPRODUCE_v1"
    elif broken:
        verdict = "BROKEN_TEST_CONTROL_BEATS_POP"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif not (scramble_controlled and peelscr_controlled and idshuf_collapses and arms_differ):
        verdict = "BROKEN_MUST_FAIL_CONTROL_FIRED"
    else:
        tags = []
        tags.append("PEEL_HP" if peel_hard_pass else ("PEEL_HF" if peel_hard_fail else "PEEL_MID"))
        tags.append("HARDNEG_HP" if hardneg_hard_pass else ("HARDNEG_HF" if hardneg_hard_fail else "HARDNEG_MID"))
        if combo_hard_pass:
            tags.append("COMBO_HP")
        if reaches_sota:
            tags.append("REACHES_SOTA")
        any_lever = peel_hard_pass or hardneg_hard_pass or combo_hard_pass
        head = "MAGNITUDE_OPT_LEVER_LIFT" if any_lever else "MAGNITUDE_OPT_NO_LEVER_LIFT"
        verdict = head + "__" + "_".join(tags)

    verdict_msg = (
        "%s || HELD-OUT MRR [nq=%d]: baseline ANCHOR=%s (reproduce v1 0.1282 ok=%s) | PEEL=%s HARDNEG=%s "
        "PEEL_HARDNEG=%s | ADDITIVE=%s RANDOM=%s | SCRAMBLE=%s PEEL_SCRAMBLE=%s IDSHUF=%s | ORACLE_uni=%s "
        "ORACLE_hn=%s POP=%s || LEVER-A(PEEL) lift=%s vs HP>=%s(=0.50*headroom_A=%s|min%.3f) HF<%s | "
        "LEVER-B(HARDNEG) lift=%s vs HP>=%.3f HF<%.3f | ceiling_lift_B(C_hn-C_uni)=%s | COMBO lift=%s vs HP>=%.3f | "
        "best_arm=%s abs_mrr=%s (SOTA[%.2f-%.2f] reached=%s) | oracle_fires=%s scramble_ok=%s peelscr_ok=%s "
        "idshuf_collapse=%s(ratio=%s<=%.2f) broken=%s arms_differ=%s(sigs=%d) | seeds=%d"
        % (
            verdict, n_query, _fmt(b), reproduce_ok, _fmt(m[PEEL]), _fmt(m[HARDNEG]), _fmt(m[PEELHN]),
            _fmt(m[ADDITIVE]), _fmt(rand), _fmt(m[SCRAMBLE]), _fmt(m[PEELSCR]), _fmt(m[IDSHUF]),
            _fmt(C_uni), _fmt(C_hn), _fmt(m[POP]),
            _fmt(lift_peel), _fmt(a_hp_target), _fmt(headroom_A), MIN_SIG_MRR, _fmt(a_hf_target),
            _fmt(lift_hardneg), B_HP_ABS, B_HF_ABS, _fmt(ceiling_lift_B), _fmt(lift_combo), COMBO_HP_ABS,
            best_arm, _fmt(best_abs_mrr), SOTA_LO, SOTA_HI, reaches_sota,
            oracle_fires, scramble_controlled, peelscr_controlled, idshuf_collapses,
            (_fmt(idshuf_collapse_ratio) if idshuf_collapse_ratio != float("inf") else "inf"),
            IDSHUF_COLLAPSE_RATIO, broken, arms_differ, len(all_sigs), len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        heldout_hits_at_10={a: _rnd(h10[a], 5) for a in ALL_ARMS},
        primary_k=PRIMARY_K, n_query_scored=n_query,
        baseline_reproduce=dict(measured=_rnd(b), target=GATED_REPRODUCE_TARGET, tol=GATED_REPRODUCE_TOL,
                                ok=reproduce_ok),
        lever_A_peel=dict(lift=_rnd(lift_peel), headroom_A=_rnd(headroom_A), hp_target=_rnd(a_hp_target),
                          hf_target=_rnd(a_hf_target), hard_pass=peel_hard_pass, hard_fail=peel_hard_fail,
                          middle=peel_middle, abs_lift_vs_research_002=_rnd(lift_peel),
                          research_band_feasible=bool(headroom_A == headroom_A and headroom_A >= B_HP_ABS)),
        lever_B_hardneg=dict(lift=_rnd(lift_hardneg), hp_target=B_HP_ABS, hf_target=B_HF_ABS,
                             ceiling_lift=_rnd(ceiling_lift_B), hard_pass=hardneg_hard_pass,
                             hard_fail=hardneg_hard_fail, middle=hardneg_middle),
        combined=dict(lift=_rnd(lift_combo), hp_target=COMBO_HP_ABS, hard_pass=combo_hard_pass,
                      best_isolated=_rnd(best_isolated), best_arm=best_arm, best_abs_mrr=_rnd(best_abs_mrr),
                      sota_lo=SOTA_LO, sota_hi=SOTA_HI, reaches_sota=reaches_sota),
        oracle_uniform=dict(mrr=_rnd(C_uni), headroom_vs_random=_rnd(oracle_headroom),
                            ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
                            fires=oracle_fires),
        oracle_hardneg=dict(mrr=_rnd(C_hn)),
        must_fails=dict(scramble_margin=_rnd(d_scramble), scramble_ceiling=_rnd(scramble_ceiling),
                        scramble_controlled=scramble_controlled, peelscr_margin=_rnd(d_peelscr),
                        peelscr_ceiling=_rnd(peelscr_ceiling), peelscr_controlled=peelscr_controlled,
                        idshuf_margin=_rnd(idshuf_margin), anchor_margin=_rnd(anchor_margin),
                        idshuf_collapse_ratio=(round(idshuf_collapse_ratio, 4) if (idshuf_collapse_ratio == idshuf_collapse_ratio and idshuf_collapse_ratio != float("inf")) else None),
                        idshuf_collapses=idshuf_collapses, broken=broken, broken_margin=_rnd(broken_margin),
                        arms_differ=arms_differ, n_distinct_sigs=len(all_sigs), must_fails_ok=must_fails_ok),
        per_support_degree_lift=_per_support_lift(per_seed),
        bands=dict(CEIL_METRIC=CEIL_METRIC, PEEL_ROUNDS=PEEL_ROUNDS, PEEL_TAU=PEEL_TAU,
                   HARD_NEG_FRAC=HARD_NEG_FRAC, A_HP_CEIL_FRAC=A_HP_CEIL_FRAC, A_HF_CEIL_FRAC=A_HF_CEIL_FRAC,
                   B_HP_ABS=B_HP_ABS, B_HF_ABS=B_HF_ABS, COMBO_HP_ABS=COMBO_HP_ABS, MIN_SIG_MRR=MIN_SIG_MRR,
                   ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   IDSHUF_COLLAPSE_RATIO=IDSHUF_COLLAPSE_RATIO, SCRAMBLE_CEIL_FRAC=SCRAMBLE_CEIL_FRAC,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough_heldout, reproduce_ok=reproduce_ok, oracle_fires=oracle_fires,
        must_fails_ok=must_fails_ok,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test on a PLANTED OUTLIER arena (Lever A discriminator fires: PEEL beats FLAT).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    pool = build_planted_transe_arena(7, n_ent=300, n_rel=6, k_lat=8, deg=4, outlier_per_node=3)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, device, 7, "PLANTED_OUTLIER_HELDOUT_ENTITY", localize=True)
    out = dict(n_grid_entities=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    ah = res["arm_hits"]
    m = {a: ah[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    h10 = {a: ah[a].get(PRIMARY_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))

    anchor_margin = m[ANCHOR] - m[RANDOM]
    scramble_margin = m[ANCHOR] - m[SCRAMBLE]
    peel_margin = m[PEEL] - m[ANCHOR]                          # ADVERSARIAL discriminator (Lever A fires)
    peelscr_margin = m[PEEL] - m[PEELSCR]
    oracle_margin = m[ORACLE] - m[RANDOM]
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])
    idshuf_margin = m[IDSHUF] - m[RANDOM]
    idshuf_collapse_ratio = (idshuf_margin / anchor_margin) if (anchor_margin > 0) else float("inf")

    oracle_recovers = bool(m[ORACLE] == m[ORACLE] and m[ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    anchor_recovers = bool(m[ANCHOR] == m[ANCHOR] and m[ANCHOR] >= SELFTEST_ANCHOR_MRR_MIN)
    anchor_beats_random = bool(anchor_margin == anchor_margin and anchor_margin >= SELFTEST_AC_BEATS_RANDOM_MRR)
    scramble_fails = bool(scramble_margin == scramble_margin and scramble_margin >= SELFTEST_SCRAMBLE_MARGIN_MRR)
    peel_beats_flat = bool(peel_margin == peel_margin and peel_margin >= SELFTEST_PEEL_MARGIN)
    peel_beats_peelscr = bool(peelscr_margin == peelscr_margin and peelscr_margin >= SELFTEST_PEELSCR_MARGIN)
    idshuf_collapses = bool(idshuf_collapse_ratio == idshuf_collapse_ratio
                            and idshuf_collapse_ratio <= SELFTEST_IDSHUF_COLLAPSE_RATIO)
    hardneg_valid = bool(m[HARDNEG] == m[HARDNEG] and m[HARDNEG] >= 0.0)   # runs + finite (data-scale lever)
    pop_at_floor = bool(m[POP] == m[POP] and m[POP] <= max(m[RANDOM], 0.02) + CONTROL_LOSE_EPS)
    arms_differ = bool(n_sigs >= 8)

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]

    # VACUOUS-SMOKE guard: RANDOM must NOT reach ANCHOR; and the Lever-A discriminator (PEEL>FLAT) MUST fire.
    assert_discriminator_fires(bool(anchor_margin <= SELFTEST_AC_BEATS_RANDOM_MRR), control_name=RANDOM,
                               headline_name="anchor_beats_random_heldout", run_mode="self_test",
                               extra="RANDOM reached ANCHOR on the planted arena -> arena not answerable")
    assert_discriminator_fires(bool(peel_margin < SELFTEST_PEEL_MARGIN), control_name="FLAT_ANCHOR",
                               headline_name="sic_peel_beats_flat_mean_on_planted_outlier_arena",
                               run_mode="self_test",
                               extra="SIC-PEEL did not beat the flat mean on the planted OUTLIER arena by %.3f -> "
                                     "the sequential composer does not recover more than flat readout" % SELFTEST_PEEL_MARGIN)

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": "ORACLE_ADDITIVE", "headline_name": "oracle_beats_random_heldout_mrr",
         "extra": "planted grid: ORACLE recovers held-out tails and clears RANDOM by the fire gate"},
        {"kind": "metric_moves", "metric_name": "heldout_mrr",
         "values": [m[RANDOM], m[ADDITIVE], m[ANCHOR], m[PEEL], m[ORACLE]],
         "extra": "MRR RANDOM=%.3f ADDITIVE=%.3f ANCHOR=%.3f PEEL=%.3f ORACLE=%.3f"
                  % (m[RANDOM], m[ADDITIVE], m[ANCHOR], m[PEEL], m[ORACLE])},
        {"kind": "negative_control_margin",
         "control_scores": [m[RANDOM], m[SCRAMBLE], m[PEELSCR], m[IDSHUF]],
         "headline_threshold": m[PEEL], "higher_is_pass": True, "margin": SELFTEST_SCRAMBLE_MARGIN_MRR,
         "n_repeats_min": 2, "control_name": "RANDOM_SCRAMBLE_PEELSCR_IDSHUF_below_peel_mrr",
         "extra": "RANDOM + relation-scrambled (flat + peel) + identity-shuffled must sit below the PEEL arm"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "peelscr_controlled",
                                    "idshuf_collapses", "reproduce_or_planted", "peel_discriminator"],
         "exercised_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "peelscr_controlled",
                             "idshuf_collapses", "reproduce_or_planted", "peel_discriminator"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
    ], run_mode="self_test")

    out.update(
        heldout_mrr={a: round(m[a], 5) for a in ALL_ARMS},
        heldout_hits_at_10={a: round(h10[a], 5) for a in ALL_ARMS},
        heldout_metric_spectrum={a: {mk: round(ah[a].get(mk, float("nan")), 5) for mk in metric_keys}
                                 for a in ALL_ARMS},
        n_distinct_sigs=n_sigs, anchor_margin=round(anchor_margin, 5), scramble_margin=round(scramble_margin, 5),
        peel_margin=round(peel_margin, 5), peelscr_margin=round(peelscr_margin, 5),
        oracle_margin=round(oracle_margin, 5),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        idshuf_collapse_ratio=(round(idshuf_collapse_ratio, 4) if (idshuf_collapse_ratio == idshuf_collapse_ratio and idshuf_collapse_ratio != float("inf")) else None),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, anchor_recovers=anchor_recovers,
        anchor_beats_random=anchor_beats_random, scramble_fails=scramble_fails, peel_beats_flat=peel_beats_flat,
        peel_beats_peelscr=peel_beats_peelscr, idshuf_collapses=idshuf_collapses, hardneg_valid=hardneg_valid,
        pop_at_floor=pop_at_floor, arms_differ=arms_differ, selftest_verdict=st_verdict,
        validity_preflight_ok=bool(vp_ok),
        support_deg_hist=res.get("localization", {}).get("support_deg_hist"),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(oracle_recovers and oracle_fires and anchor_recovers and anchor_beats_random and scramble_fails
              and peel_beats_flat and peel_beats_peelscr and idshuf_collapses and hardneg_valid
              and pop_at_floor and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s epochs=%s peel_rounds=%s tau=%s hardneg_frac=%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["epochs"], PEEL_ROUNDS, PEEL_TAU,
          HARD_NEG_FRAC))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s anchor_margin=%s peel_margin=%s peelscr_margin=%s scramble_margin=%s "
         "oracle_fires=%s idshuf_collapse=%s vp_ok=%s" %
         (st_ok, st_res.get("anchor_margin"), st_res.get("peel_margin"), st_res.get("peelscr_margin"),
          st_res.get("scramble_margin"), st_res.get("oracle_fires"), st_res.get("idshuf_collapse_ratio"),
          st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (peel did not beat flat / must-fails did not fire / oracle "
                        "underfit / arms not distinct): %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS magnitude-opt: SIC-PEEL beats flat mean on the planted OUTLIER arena; "
                        "hardneg fit runs; relation-scramble (flat+peel) fails; identity-shuffle collapses; ORACLE "
                        "fires; POP at floor; 4 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                    prov["n_rel_tokens"], len(pool)))
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY", ckpt_dir=out_dir, localize=True)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 8:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            ah = res["arm_hits"]
            _log("seed=%d nq=%d n_sup=%d n_cold=%d | MRR ANCHOR=%s PEEL=%s HARDNEG=%s PEELHN=%s | RANDOM=%s "
                 "SCRAMBLE=%s IDSHUF=%s ORACLE=%s ORACLEHN=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_support"], res["n_cold"],
                  _fmt(ah[ANCHOR]["mrr"]), _fmt(ah[PEEL]["mrr"]), _fmt(ah[HARDNEG]["mrr"]), _fmt(ah[PEELHN]["mrr"]),
                  _fmt(ah[RANDOM]["mrr"]), _fmt(ah[SCRAMBLE]["mrr"]), _fmt(ah[IDSHUF]["mrr"]),
                  _fmt(ah[ORACLE]["mrr"]), _fmt(ah[ORACLEHN]["mrr"]), time.time() - ts))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--memsmoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("memsmoke" if args.memsmoke else args.run_mode)
    if not args.self_test and not args.memsmoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
            run_mode = _env_mode
    device = _resolve_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
