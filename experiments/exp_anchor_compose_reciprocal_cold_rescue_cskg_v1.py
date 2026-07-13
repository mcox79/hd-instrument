"""ANCHOR_COMPOSE RECIPROCAL COLD-RESCUE: bundle a held-out entity's HEAD edges via the ALREADY-TRAINED inverse
relation table -- the ONLY VSA-native lever that can move the COLD bucket (0 tail-support entities, currently BELOW
RANDOM).

CODE-VERIFIED DEFECT (CITED@notes/research_substrate_realizable_frontier_levers_inductive_map_builder_2026-07-13.md
HEADLINE 1): the confirmed ANCHOR_COMPOSE composer (build_anchor_compose_codes in
experiments/exp_anchor_compose_inductive_entity_cskg_v1.py) bundles ONLY a held-out entity's TAIL-support edges
(seen_head, r, held_ent). Edges where the held-out entity is the HEAD of a triple to a KNOWN tail (held_ent, r,
seen_tail) are SILENTLY DROPPED from the split (build_heldout_entity_split_ac: the `h_hold and not t_hold` branch is
never collected). This throws away half the available structure for exactly the degree-starved COLD population.

WHY IT MATTERS (MEASURED@data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json:anchor_mrr_by_support_degree,
CITED via research note Part A): the COLD bucket (entities whose single tail-edge is reserved as the query, leaving 0
tail-support) sits at anchor_mrr=0.000041, BELOW its own random_mrr=0.000524 and far below oracle_mrr=0.650751 -- the
mechanism is currently WORSE than chance there, and the composer's `mask = cnt > 0` guard means these entities never
get touched at all (they fall back to the raw untrained-random code). NO cleanup/weighting/decorrelation lever can move
COLD because there is nothing to aggregate. Only ADDING a usable edge can -- and the reciprocal head-edges are real,
present, and free.

ZERO-NEW-TRAINING MECHANISM: the shared additive scorer is ALREADY fit with reciprocal=True
(experiments/_kge_anchor1_fit.py: inverse relations occupy D[n_rel:2*n_rel], trained as a byproduct of Lacroix et al.
2018 reciprocal augmentation). For a held-out entity e in a HEAD edge (e, r, seen_tail), the trained inverse relation
gives a code estimate est_head = X[seen_tail] + D_inverse[r] (the reciprocal edge (seen_tail, r_inv, e) was trained to
satisfy X[seen_tail] + D_inverse[r] ~= X[e]). We AVERAGE these head estimates into the SAME per-entity bundle as the
forward tail estimates X[seen_head] + D[r] -- a bidirectional additive bundle. The held-out entity STILL receives ZERO
gradient steps; only the (already-computed) inverse-relation block is now read out. fit_kge_anchor1 gained a
backward-compatible return_inverse=True flag to expose that block (2-tuple return is bit-identical for every prior
caller; verified).

BRAIN-ANALOG (CITED@Kosko 1988, Bidirectional Associative Memories, IEEE Trans. SMC): a single associative matrix
trained on pattern pairs (A,B) supports recall in EITHER direction from the same Hebbian (symmetric) plasticity. Using
a learned relation in reverse to recover a concept seen only as a subject is the direct analog. Ties to the standing
relational-capability program spine (CITED@project_relational_capability_is_the_core_requirement_make_it_real_USER_
2026-07-10.md): reciprocal/bidirectional relational inference, not just forward composition.

ARMS (9; SHARDED per-entity codes; all scored PAIRED on the SAME held-out QUERY edges + candidate pool. The QUERY set
and the shared additive/rotate/oracle fits are BIT-IDENTICAL to the confirmed v1 -- head edges go ONLY to a NEW
head-support pool, never to train or query, so ANCHOR reproduces v1's 0.1282 as a Gate-D positive control):
  ANCHOR_COMPOSE        : TAIL-ONLY flat additive mean == the confirmed v1 baseline (Gate-D reproduce; the COLD-floor).
  ANCHOR_RECIP          : MECHANISM -- TAIL-support + HEAD-support (via trained inverse D_inverse) bidirectional mean.
  ANCHOR_RECIP_SCRAMBLE : must-fail for the reciprocal lever -- HEAD estimates use PERMUTED inverse-relation ids
                          (X[seen_tail] + D_inverse[perm[r]]); tail-support identical. Isolates whether the COLD lift
                          is RELATIONAL (the trained inverse operator) vs merely "more vectors in the average".
  ADDITIVE_TRANSE       : memorize control (SAME additive fit; held-out code stays random-init).
  ONESHOT_ROTATE        : 2nd memorize control (rotation fit; functional-form variety).
  RANDOM_CODES          : null (random X + random D + additive readout) -- the bar COLD currently sits BELOW.
  ANCHOR_SCRAMBLE       : v1 must-fail -- TAIL-support forward relation ids scrambled (D[perm[r]]); relation signal.
  ORACLE_ADDITIVE       : positive control / ceiling -- additive fit with held-out folded in (codes LEARNED). The COLD
                          oracle is high (~0.65 MEASURED-fork) so COLD IS answerable-in-principle when a code exists.
  BASELINE_POP          : frequency incumbent (fit-independence sanity; held-out tails have train-freq 0 -> ~floor).

PRIMARY QUESTION = the COLD bucket (stratified by ORIGINAL TAIL-support degree so COLD = 0 tail-support, directly
comparable to the ladder). Does reciprocal head-bundling lift COLD from ~random to above it? Secondary = overall gain
+ a hard NO-REGRESSION guard on the adequate-support buckets.

PRE-REG BANDS (picked BEFORE the run; primary metric = FILTERED MRR rank-vs-ALL, degree-unbiased; all HYPOTHESIZED
unless MEASURED@/CITED@; ceiling-aware):
  GATE-D REPRODUCE       : |ANCHOR_all - 0.1282| <= 0.03 (MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/
                           metrics.json:gates.heldout_mrr.ANCHOR_COMPOSE at the matched k=24/ep=500/k_core=12/
                           support_frac=0.5 regime). Off-tolerance -> INCONCLUSIVE (untrustworthy split/fit).
  ORACLE-FIRES (overall) : ORACLE_mrr >= 3x RANDOM_mrr AND ORACLE_mrr - RANDOM_mrr >= 0.003 (arena answerable).
  CONSTRUCTION-FIRED     : >= 8 COLD queries whose entity gained >= 1 reciprocal HEAD-support edge (else the COLD band
                           is INCONCLUSIVE_COLD_NO_RECIP_SUPPORT -- a graph-sparsity finding, redirect to multi-hop/
                           textual, NOT a mechanism HARD_FAIL).
  COLD HARD-PASS         : COLD-bucket ANCHOR_RECIP mrr >= 0.02 absolute (a ~40-500x rescue off the ~0.00004-0.0005
                           floor) AND (RECIP - ANCHOR)_cold >= 0.01 AND COLD scramble controlled
                           ((RECIP - RECIP_SCRAMBLE)_cold >= 0.5 * (RECIP - RANDOM)_cold AND RECIP_SCRAMBLE_cold within
                           0.005 of RANDOM_cold) AND NO-REGRESSION holds AND ORACLE fires AND Gate-D holds.
  COLD HARD-FAIL         : COLD-bucket ANCHOR_RECIP mrr < 0.0002 (order-of-magnitude unmoved) WITH construction fired
                           = genuine negative (CSKG COLD entities lack usable edges in either direction beyond the
                           single query edge; localize to multi-hop/textual fallback).
  COLD MIDDLE            : COLD lift present but < 0.02 -> sub-stratify by reciprocal-edge count (1 vs 2+); if lift
                           scales with reciprocal-edge-count the lever works but COLD is thin on reciprocal edges too.
  NO-REGRESSION (guard)  : overall AND every adequate bucket (d2_3/d4_7/d8plus) ANCHOR_RECIP mrr >= ANCHOR mrr - 0.005
                           (adding head estimates must not degrade the already-working populations).
  SECONDARY (reported)   : overall (RECIP - ANCHOR)_mrr gain (>= 0.005 = a good secondary, small since COLD is a
                           minority bucket -- the PER-BUCKET COLD rescue is the primary signal).

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes : ORACLE recovers planted held-out tails and clears RANDOM by the fire gate.
  (2) metric_moves            : COLD-bucket MRR MOVES across [RANDOM, ANCHOR(tail-only), ANCHOR_RECIP, ORACLE].
  (3) negative_control_margin : RANDOM + ANCHOR_RECIP_SCRAMBLE sit below ANCHOR_RECIP on the COLD bucket, det >= 2.
  (4) full_gates_exercised    : aggregate_and_verdict runs on the planted per-seed, firing every fail-closed gate.
ADVERSARIAL SELF-TEST DISCRIMINATOR (reciprocal lifts a planted COLD entity that has ONLY head edges): on a planted
TransE-consistent arena, a subset of held-out entities are COLD (exactly 1 tail-edge, reserved as query -> 0
tail-support) but DO emit head-edges to seen tails. ANCHOR_RECIP recovers their query tails GENUINELY better than the
tail-only ANCHOR (which leaves them at the random-init fallback) AND the relation-scrambled ANCHOR_RECIP_SCRAMBLE
collapses -- proving the COLD rescue is the trained inverse operator, not "more vectors in the bundle".

## Compute architecture
class (c) MIXED: split/partition/POP = sequential-CPU graph ops (no matmul); the 3 fits (additive+reciprocal-inverse,
rotate, additive-oracle) = minibatch SGD (batched, self-adversarial, neg-chunked on FULL) == the confirmed v1 fit
cost (MEASURED@v1 FULL elapsed_s=12073 for k=24/ep=500/3 seeds/3 fits); the FLAT tail + bidirectional recip E_derived
constructions = vectorized index_add segment ops (no training, seconds); readouts = query-chunked batched matmul (the
(nq,N) map is never materialized whole). Storage SHARDED (each entity its own code; the ONLY bundle is the per-ENTITY
bidirectional support mean). device=auto (cuda on the GPU host; overnight_queue); remote_cpu forces cpu. FULL fits are
fit-checkpointed (ckpt_every) so a timeout/outage resumes each arm from its last epoch. A multi-seed MEMSMOKE (FULL
memory footprint, 2 seeds IN-PROCESS, few epochs) validates no-OOM + per-seed empty_cache BEFORE the FULL; the
discriminator-fires proof is the self-test + analytical (a per-entity table cannot encode an unseen entity by
construction, so the memorize null persists at any N), NOT the memsmoke.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): 9 arms produce >= 6 distinct score signatures per seed.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: raw hits@10-vs-all-N has a ceiling; primary metric is FILTERED MRR + ceiling-aware ORACLE
#   fire gate; the COLD band is a low ABSOLUTE bar (0.02) off a MEASURED ~0.00004 floor (a 500x rescue) with the COLD
#   oracle (~0.65 MEASURED-fork) proving COLD is answerable-in-principle when a code exists.
# - baseline_in_band: ORACLE must fire (>=3x RANDOM AND headroom>=0.003); RANDOM/POP near the 1/N floor; Gate-D
#   reproduces the confirmed ANCHOR baseline within 0.03.
# - discriminator survives scale: the reciprocal COLD-rescue fires on the planted COLD-head-only arena in self-test;
#   on CSKG the CONSTRUCTION-FIRED gate guards against a vacuous COLD band (no reciprocal edges -> INCONCLUSIVE, not a
#   false HARD_FAIL). The must-fails fire deterministically at self-test scale.
# - HARD-PASS strictly above floor: COLD HP 0.02 clears COLD HF 0.0002 by 2 orders of magnitude + a relational-margin
#   + a scramble-controlled gate.
# - HP_SCOPE: the COLD-rescue HARD-PASS gates apply to ANCHOR_RECIP only. ORACLE = positive control (must fire);
#   RANDOM/ANCHOR_SCRAMBLE/ANCHOR_RECIP_SCRAMBLE = must-not-clear-bar controls; ADDITIVE_TRANSE/ONESHOT_ROTATE =
#   memorize head-to-heads; ANCHOR_COMPOSE = the tail-only baseline (Gate-D reproduce); POP = fit-independence sanity.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all 9 arms + >= 6 sigs.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- HELDOUT_ENTITY_FRAC/SUPPORT_FRAC + all COLD band absolutes
#   pre-registered, NOT tuned on real data; the COLD stratifier uses the ORIGINAL TAIL-support degree so COLD is the
#   same population the ladder measured.
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
from experiments._course_c_rotate_core_v1 import (  # noqa: E402
    fit_kge_rotate, rotate_direct_scores, additive_direct_scores, ROT_LR,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402

ANCHOR_NAME = "anchor_compose_reciprocal_cold_rescue_cskg_v1"

# ---- Arm names ----
ANCHOR = "ANCHOR_COMPOSE"              # TAIL-ONLY flat mean == confirmed v1 baseline (Gate-D reproduce; the COLD floor)
RECIP = "ANCHOR_RECIP"                 # MECHANISM: tail-support + head-support via trained inverse (bidirectional)
RECIPSCR = "ANCHOR_RECIP_SCRAMBLE"     # must-fail for the reciprocal lever: head estimates use PERMUTED inverse ids
ADDITIVE = "ADDITIVE_TRANSE"           # memorize control (same additive fit; held-out random-init)
ONESHOT = "ONESHOT_ROTATE"             # 2nd memorize control (rotation fit)
RANDOM = "RANDOM_CODES"                # null
SCRAMBLE = "ANCHOR_SCRAMBLE"           # v1 must-fail: TAIL-support forward relation ids scrambled
ORACLE = "ORACLE_ADDITIVE"             # positive control / ceiling (held-out folded in -> codes learned)
POP = "BASELINE_POP"                   # frequency incumbent (fit-independence sanity)

GEOM_ARMS = [ANCHOR, RECIP, RECIPSCR, ADDITIVE, ONESHOT, RANDOM, SCRAMBLE, ORACLE]
ALL_ARMS = GEOM_ARMS + [POP]

# ---- CEILING-AWARE, DEGREE-UNBIASED evaluation (identical protocol to confirmed v1) ----
EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"
PRIMARY_METRIC = "hits@%d" % PRIMARY_K   # legacy hits@10 (reported, NOT gated)

# ORACLE-fire gate (arena answerable under the primary metric).
ORACLE_FIRE_RATIO = 3.0
ORACLE_FIRE_ABS = 0.003

# ---- Gate-D reproduce (baseline reproduces the confirmed v1 at the matched regime) ----
GATED_REPRODUCE_TARGET = 0.1282   # MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json
GATED_REPRODUCE_TOL = 0.03        # |ANCHOR_all - target| <= this (else INCONCLUSIVE: untrustworthy split/fit)

# ---- COLD-bucket bands (pre-registered; NOT tuned on real data) ----
COLD_HP_MRR = 0.02          # COLD ANCHOR_RECIP mrr HARD-PASS absolute (a ~40-500x rescue off the ~0.00004-0.0005 floor)
COLD_HF_MRR = 0.0002        # COLD ANCHOR_RECIP mrr HARD-FAIL absolute (order-of-magnitude unmoved) WITH construction
COLD_RECIP_MARGIN = 0.01    # (RECIP - ANCHOR)_cold >= this (the lift over the tail-only baseline on COLD)
COLD_SCR_REL_FRAC = 0.5     # COLD scramble controlled: (RECIP - RECIP_SCRAMBLE)_cold >= this * (RECIP - RANDOM)_cold
COLD_SCR_NOISE = 0.005      # AND RECIP_SCRAMBLE_cold within this of RANDOM_cold (scramble collapses to ~noise)
MIN_COLD_Q = 20             # min COLD queries to gate the COLD bucket (else INCONCLUSIVE_TOO_FEW_COLD)
MIN_COLD_RECIP = 8          # min COLD queries whose entity gained >=1 reciprocal head-support edge (construction fired)

# ---- overall / no-regression bands ----
OVERALL_GAIN_MIN = 0.005    # SECONDARY (reported): overall (RECIP - ANCHOR)_mrr gain
NO_REGRESSION_EPS = 0.005   # adequate buckets + overall: RECIP mrr >= ANCHOR mrr - this
CONTROL_LOSE_EPS = 0.005    # broken-test guard base
MIN_HELDOUT = 20            # min held-out QUERY edges for a valid discriminator
MIN_STRAT_Q = 8             # min queries in a stratum to report its margin
SCRAMBLE_CEIL_FRAC = 0.25   # v1 ANCHOR_SCRAMBLE controlled: (SCRAMBLE - RANDOM) <= 0.25 * (ANCHOR - RANDOM)

# ---- Held-out-entity split knobs (pre-registered; matched to confirmed v1) ----
HELDOUT_ENTITY_FRAC = 0.15
SUPPORT_FRAC = 0.5

# ---- self-test planted thresholds (calibrated on the synthetic COLD-head arena, NOT real data) ----
SELFTEST_ORACLE_MRR_MIN = 0.30       # planted: ORACLE (learned held-out codes) mrr at least this
SELFTEST_COLD_RECIP_MRR_MIN = 0.10   # planted COLD bucket: ANCHOR_RECIP mrr at least this (reciprocal rescues COLD)
SELFTEST_COLD_MARGIN = 0.05          # planted COLD bucket: (RECIP - ANCHOR)_cold >= this (tail-only cannot touch COLD)
SELFTEST_COLD_SCR_MARGIN = 0.03      # planted COLD bucket: (RECIP - RECIP_SCRAMBLE)_cold >= this (relational)
SELFTEST_MIN_COLD = 6                # planted: minimum COLD queries with reciprocal head-support
SELFTEST_MIN_HO = 8                  # planted: minimum held-out QUERY edges

# ---- hardest relation tertile (weak-point-localization; carried from v1) ----
HARDEST_TERTILE_RELS = frozenset([
    "hascontext", "antonym", "mayhaveproperty", "locatednear", "xattr", "haslexicalunit", "hassubevent",
    "motivatedbygoal", "desires", "synonym", "usedfor", "similarto", "hasprerequisite", "xwant",
])

SCORE_CHUNK = 256

# Config profiles. SELFTEST/MEMSMOKE/FULL exercise the SAME split->fit->compose->score->verdict path.
SELFTEST_CFG = dict(k=12, epochs=350, n_neg=32, batch=4096,
                    heldout_entity_frac=0.2, support_frac=0.5, n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO)
# MEMSMOKE = FULL memory footprint (full N + k=24 + n_neg=128 + neg_chunk) but few epochs + 2 seeds. Proves no-OOM
# across the 3 fits (additive+reciprocal-inverse, rotate, oracle) + per-seed empty_cache BEFORE the FULL.
MEMSMOKE_CFG = dict(k=24, epochs=25, n_neg=128, batch=8192, neg_chunk=16,
                    heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                    cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                    n_heldout_eval=2000, min_heldout=10, seeds=[7, 13])
# FULL: k=24/ep=500/k_core=12/support_frac=0.5 = the confirmed v1 regime so ANCHOR_COMPOSE REPRODUCES 0.1282 (Gate-D).
# 3 seeds (matches v1) -> 3 fits x 3 seeds ~ 3.4h (MEASURED@v1 FULL elapsed_s=12073); ckpt_every makes each fit
# outage-resumable so a timeout resumes rather than restarts.
FULL_CFG = dict(k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, ckpt_every=20,
                heldout_entity_frac=HELDOUT_ENTITY_FRAC, support_frac=SUPPORT_FRAC,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_heldout_eval=3000, min_heldout=MIN_HELDOUT, seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.5f" % x) if (x == x) else "nan"


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
# Planted arena: TransE-consistent, RELATION operator NECESSARY. Every entity emits `deg` HEAD edges (h,r,nearest).
# A held-out COLD entity has exactly 1 tail-edge (reserved as query -> 0 tail-support) but DOES emit head-edges to
# seen tails -> the reciprocal lever has genuine material to recover. Deterministic.
# ---------------------------------------------------------------------------

def build_planted_transe_arena(seed, n_ent=400, n_rel=6, k_lat=8, deg=3, w_scale=1.0):
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
    return list(dict.fromkeys(edges))   # order-preserving dedup (cross-process determinism)


# ---------------------------------------------------------------------------
# Held-out-ENTITY split WITH a per-entity TAIL-SUPPORT / QUERY partition (IDENTICAL to v1 for the tail direction; the
# tail RNG streams are preserved so the QUERY set and the fit are bit-identical) PLUS a NEW HEAD-SUPPORT pool: edges
# where the held-out entity is the HEAD of a triple to a KNOWN (seen) tail. v1 DROPPED these; we retain them, ALL as
# head-support (never train, never query). No leakage: head-support edges involve a held-out entity so they are not in
# train, and they are structurally disjoint from the tail-direction query edges.
# ---------------------------------------------------------------------------

def build_heldout_entity_split_recip(pool_lbl, ent2i, frac, support_frac, seed):
    n_ent = len(ent2i)
    rng = np.random.default_rng(seed * 100003 + 7)            # SAME stream as v1 (hold_ids identical)
    n_hold = max(1, int(frac * n_ent))
    hold_ids = set(int(x) for x in rng.choice(n_ent, size=n_hold, replace=False))
    train_lbl = []
    held_by_tail = defaultdict(list)
    head_support_lbl = []                                     # NEW: (held_head, r, seen_tail) edges (v1 dropped these)
    for (h, r, t) in pool_lbl:
        hi = ent2i[h]; ti = ent2i[t]
        h_hold = hi in hold_ids; t_hold = ti in hold_ids
        if not h_hold and not t_hold:
            train_lbl.append((h, r, t))
        elif t_hold and not h_hold:
            held_by_tail[ti].append((h, r, t))
        elif h_hold and not t_hold:
            head_support_lbl.append((h, r, t))               # reciprocal head-support (bundled via inverse relation)
        # (both-held edges are dropped, same as v1: no seen anchor on either side)
    support_lbl, query_lbl = [], []
    n_cold = 0
    rng2 = np.random.default_rng(seed * 991 + 5)             # SAME stream as v1 (tail partition identical)
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
    return train_lbl, support_lbl, head_support_lbl, query_lbl, hold_ids, n_cold


# ---------------------------------------------------------------------------
# Bidirectional composer. E_derived[e] = mean over ( tail-support: X[h]+D[r] for (h,r,e) )
#                                              U ( head-support: X[t]+D_inv[r] for (e,r,t) ).
# ANCHOR = head_support empty. RECIP = both. RECIP_SCRAMBLE = inv_rel_perm on the head estimates. ANCHOR_SCRAMBLE =
# tail_rel_perm on the tail estimates (head empty). Returns patched table + tail-support degree + reciprocal (head)
# support degree per entity.
# ---------------------------------------------------------------------------

def build_recip_compose_codes(X, D, Dinv, tail_support_int, head_support_int, device,
                              tail_rel_perm=None, inv_rel_perm=None):
    N, k = X.shape[0], X.shape[1]
    Xp = X.clone()
    acc = torch.zeros(N, k, device=device, dtype=X.dtype)
    cnt = torch.zeros(N, device=device, dtype=X.dtype)
    tail_deg = np.zeros(N, dtype=np.int64)
    recip_deg = np.zeros(N, dtype=np.int64)

    if tail_support_int is not None and tail_support_int.shape[0] > 0:
        h = torch.from_numpy(tail_support_int[:, 0]).long().to(device)
        r_np = tail_support_int[:, 1].copy()
        if tail_rel_perm is not None:
            r_np = tail_rel_perm[r_np]
        r = torch.from_numpy(r_np).long().to(device)
        t = torch.from_numpy(tail_support_int[:, 2]).long().to(device)   # held-out tail = accumulation target
        est = X[h] + D[r]
        acc.index_add_(0, t, est)
        ones = torch.ones(t.shape[0], device=device, dtype=X.dtype)
        cnt.index_add_(0, t, ones)
        td = torch.zeros(N, device=device, dtype=X.dtype)
        td.index_add_(0, t, ones)
        tail_deg = td.detach().to("cpu").numpy().astype(np.int64)

    if head_support_int is not None and head_support_int.shape[0] > 0:
        hh = torch.from_numpy(head_support_int[:, 0]).long().to(device)  # held-out HEAD = accumulation target
        r_np = head_support_int[:, 1].copy()
        if inv_rel_perm is not None:
            r_np = inv_rel_perm[r_np]
        rr = torch.from_numpy(r_np).long().to(device)
        tt = torch.from_numpy(head_support_int[:, 2]).long().to(device)  # seen tail (trained code)
        est_h = X[tt] + Dinv[rr]                                          # trained inverse-relation estimate of X[hh]
        acc.index_add_(0, hh, est_h)
        ones = torch.ones(hh.shape[0], device=device, dtype=X.dtype)
        cnt.index_add_(0, hh, ones)
        rd = torch.zeros(N, device=device, dtype=X.dtype)
        rd.index_add_(0, hh, ones)
        recip_deg = rd.detach().to("cpu").numpy().astype(np.int64)

    mask = cnt > 0
    Xp[mask] = acc[mask] / cnt[mask].unsqueeze(1)
    return Xp, tail_deg, recip_deg


def _mk_ckpt(ckpt_dir, ckpt_every, tag, seed):
    if ckpt_dir is None or not ckpt_every:
        return None
    return FitCheckpoint(ckpt_dir, "%s_seed%d" % (tag, seed), ckpt_every)


def fit_and_score(train_int, tail_support_int, head_support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                  rel_tail_freq, all_true, ckpt_dir=None):
    k = cfg["k"]; epochs = cfg["epochs"]; n_neg = cfg["n_neg"]; batch = cfg["batch"]
    neg_chunk = cfg.get("neg_chunk"); ckpt_every = cfg.get("ckpt_every")

    def _ec():
        if getattr(device, "type", "") == "cuda":
            torch.cuda.empty_cache()

    # ADDITIVE fit WITH the trained inverse-relation block exposed (return_inverse=True). Shared by ANCHOR / RECIP /
    # RECIP_SCRAMBLE / ADDITIVE / ANCHOR_SCRAMBLE. The forward (Xa, Da) is bit-identical to v1 (return_inverse is an
    # additive-only change); Da_inv is the trained inverse block used ONLY by the reciprocal head-bundle.
    Xa, Da, Da_inv = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, reciprocal=True, lr=A1_LR,
                                     n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk, return_inverse=True,
                                     ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive", seed))
    _ec()
    PHI, THETA = fit_kge_rotate(train_int, N, n_rel, k, device, seed, epochs, lr=ROT_LR, n_neg=n_neg,
                                batch_size=batch, neg_chunk=neg_chunk,
                                ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "rotate_oneshot", seed))
    _ec()
    Xo, Do = fit_kge_anchor1(train_int, N, n_rel, k, device, seed, epochs, transductive_extra=hold_all,
                             reciprocal=True, lr=A1_LR, n_neg=n_neg, batch_size=batch, neg_chunk=neg_chunk,
                             ckpt=_mk_ckpt(ckpt_dir, ckpt_every, "additive_oracle", seed))
    _ec()
    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, k, generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, k, generator=gR) * 0.1).to(device)

    empty = np.zeros((0, 3), dtype=np.int64)
    tail_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)
    inv_perm = np.random.default_rng(seed * 5557 + 23).permutation(n_rel)

    # ANCHOR: tail-only (head empty). RECIP: tail + head. RECIP_SCRAMBLE: tail + head-with-permuted-inverse.
    # ANCHOR_SCRAMBLE: tail-only with permuted forward relations.
    Xanc, tail_deg, _ = build_recip_compose_codes(Xa, Da, Da_inv, tail_support_int, empty, device)
    Xrec, _, recip_deg = build_recip_compose_codes(Xa, Da, Da_inv, tail_support_int, head_support_int, device)
    Xrsc, _, _ = build_recip_compose_codes(Xa, Da, Da_inv, tail_support_int, head_support_int, device,
                                           inv_rel_perm=inv_perm)
    Xscr, _, _ = build_recip_compose_codes(Xa, Da, Da_inv, tail_support_int, empty, device, tail_rel_perm=tail_perm)

    arm_metric, arm_sig, arm_scores = {}, {}, {}
    for name, sc in [
        (ANCHOR, additive_direct_scores(Xanc, Da, query_int, device, chunk=SCORE_CHUNK)),
        (RECIP, additive_direct_scores(Xrec, Da, query_int, device, chunk=SCORE_CHUNK)),
        (RECIPSCR, additive_direct_scores(Xrsc, Da, query_int, device, chunk=SCORE_CHUNK)),
        (ADDITIVE, additive_direct_scores(Xa, Da, query_int, device, chunk=SCORE_CHUNK)),
        (ONESHOT, rotate_direct_scores(PHI, THETA, query_int, device, chunk=SCORE_CHUNK)),
        (SCRAMBLE, additive_direct_scores(Xscr, Da, query_int, device, chunk=SCORE_CHUNK)),
        (ORACLE, additive_direct_scores(Xo, Do, query_int, device, chunk=SCORE_CHUNK)),
        (RANDOM, additive_direct_scores(Xr, Dr, query_int, device, chunk=SCORE_CHUNK)),
    ]:
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = _sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        arm_scores[name] = sc
    pop_m, pop_rank_vec = pop_hits(rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = _sig(pop_rank_vec.astype(np.float64))

    del Xa, Da, Da_inv, PHI, THETA, Xo, Do, Xr, Dr, Xanc, Xrec, Xrsc, Xscr
    _ec()
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores,
                tail_deg=tail_deg, recip_deg=recip_deg)


# ---------------------------------------------------------------------------
# Weak-point localization: per TAIL-support-degree bin (COLD = 0 tail-support, the ladder-comparable population), plus
# a COLD sub-stratification by reciprocal (head) edge count.
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
ADEQUATE_BUCKETS = ["d2_3", "d4_7", "d8plus"]
REPORT_ARMS = [ANCHOR, RECIP, RECIPSCR, RANDOM, ORACLE]


def localize_weak_points(arm_scores, query_int, all_true, tail_deg, recip_deg, node_degree, rel_i2lbl,
                         rel_tail_freq, N):
    nq = query_int.shape[0]
    gold = query_int[:, 2]
    q_tail = np.array([tail_deg[int(g)] for g in gold], dtype=np.int64)          # ORIGINAL tail-support degree
    q_recip = np.array([recip_deg[int(g)] for g in gold], dtype=np.int64)        # reciprocal (head) edge count
    strat, tert = stratify_by_tail_degree(query_int, node_degree)

    def _by_mask(mask):
        out = {a: _hits_subset(arm_scores[a], query_int, all_true, mask) for a in REPORT_ARMS}
        out[POP] = _pop_subset(rel_tail_freq, query_int, all_true, N, mask)
        return out

    by_support = {}
    for lo, hi, name in SUPPORT_BINS:
        by_support[name] = _by_mask((q_tail >= lo) & (q_tail <= hi))

    # COLD sub-stratification by reciprocal-edge count (the mechanism-fires diagnostic for the MIDDLE band).
    cold_mask = (q_tail == 0)
    cold_recip = {
        "recip0": _by_mask(cold_mask & (q_recip == 0)),
        "recip1": _by_mask(cold_mask & (q_recip == 1)),
        "recip2plus": _by_mask(cold_mask & (q_recip >= 2)),
    }
    n_cold_recip = int((cold_mask & (q_recip >= 1)).sum())
    n_cold_q = int(cold_mask.sum())

    by_gdeg_tertile = {nm: _by_mask(strat == si) for si, nm in enumerate(["low", "mid", "high"])}
    return dict(by_support_degree=by_support, cold_by_recip_count=cold_recip,
                n_cold_q=n_cold_q, n_cold_with_recip=n_cold_recip,
                by_global_degree_tertile=by_gdeg_tertile,
                support_deg_hist={name: int(((q_tail >= lo) & (q_tail <= hi)).sum())
                                  for lo, hi, name in SUPPORT_BINS},
                recip_deg_hist={
                    "recip0": int((q_recip == 0).sum()), "recip1": int((q_recip == 1).sum()),
                    "recip2plus": int((q_recip >= 2).sum())},
                cold_recip_deg_hist={
                    "recip0": int((cold_mask & (q_recip == 0)).sum()),
                    "recip1": int((cold_mask & (q_recip == 1)).sum()),
                    "recip2plus": int((cold_mask & (q_recip >= 2)).sum())})


# ---------------------------------------------------------------------------
# One corpus run.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None, localize=True):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    rel_i2lbl = {v: k for k, v in rel2i.items()}
    train_lbl, support_lbl, head_support_lbl, query_lbl, hold_ids, n_cold = build_heldout_entity_split_recip(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total = len(query_lbl)

    if cfg.get("n_heldout_eval") and n_query_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_lbl = [query_lbl[i] for i in idx]

    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    tail_support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    head_support_int = _to_int_edges(head_support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    # ORACLE folds in ONLY the tail-direction held edges (support + query), matching v1 (the transductive ceiling for
    # the tail-prediction arena). Head-support edges are the reciprocal lever's input, not part of the tail arena.
    hold_all = np.concatenate([tail_support_int, query_int], axis=0) if query_int.shape[0] else tail_support_int
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, tail_support_int, query_int)

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_tail_support=int(tail_support_int.shape[0]),
                  n_head_support=int(head_support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    fs = fit_and_score(train_int, tail_support_int, head_support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                       gd.rel_tail_freq, all_true, ckpt_dir=ckpt_dir)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 5) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
    )
    if localize:
        result["localization"] = localize_weak_points(
            fs["arm_scores"], query_int, all_true, fs["tail_deg"], fs["recip_deg"], gd.node_degree, rel_i2lbl,
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


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def _sub(a, b):
    return (a - b) if (a == a and b == b) else float("nan")


def _bucket_mrr(per_seed, bucket, arm):
    """mean over seeds of the bucket's arm MRR (only seeds where the bucket has >= MIN_STRAT_Q queries)."""
    vals = []
    for ps in per_seed:
        cell = ps.get("localization", {}).get("by_support_degree", {}).get(bucket, {}).get(arm, {})
        if cell.get("n", 0) >= MIN_STRAT_Q:
            vals.append(cell.get("mrr", float("nan")))
    return _nm(vals)


def aggregate_and_verdict(per_seed):
    m = {a: _nm([_m(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    # ---- overall gates ----
    oracle_headroom = _sub(m[ORACLE], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])
    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    gate_d_reproduce = bool(m[ANCHOR] == m[ANCHOR] and abs(m[ANCHOR] - GATED_REPRODUCE_TARGET) <= GATED_REPRODUCE_TOL)

    # v1 must-fail (tail-scramble) controlled + broken-test guard
    d_anchor_random = _sub(m[ANCHOR], m[RANDOM])
    d_scramble = _sub(m[SCRAMBLE], m[RANDOM])
    scramble_ceiling = (SCRAMBLE_CEIL_FRAC * d_anchor_random if d_anchor_random == d_anchor_random else float("nan"))
    scramble_controlled = bool(d_scramble == d_scramble and scramble_ceiling == scramble_ceiling
                               and d_scramble <= scramble_ceiling)
    broken_margin = max(CONTROL_LOSE_EPS, SCRAMBLE_CEIL_FRAC * oracle_headroom) if oracle_headroom == oracle_headroom \
        else CONTROL_LOSE_EPS
    broken = bool((m[RANDOM] == m[RANDOM] and m[POP] == m[POP] and (m[RANDOM] - m[POP]) > broken_margin)
                  or (m[RECIPSCR] == m[RECIPSCR] and m[POP] == m[POP] and (m[RECIPSCR] - m[POP]) > broken_margin))

    # ---- overall RECIP vs ANCHOR (secondary + no-regression) ----
    overall_gain = _sub(m[RECIP], m[ANCHOR])
    no_regress_overall = bool(overall_gain == overall_gain and overall_gain >= -NO_REGRESSION_EPS)
    adequate_regress = {}
    no_regress_adequate = True
    for b in ADEQUATE_BUCKETS:
        a_anc = _bucket_mrr(per_seed, b, ANCHOR)
        a_rec = _bucket_mrr(per_seed, b, RECIP)
        diff = _sub(a_rec, a_anc)
        adequate_regress[b] = dict(anchor=(round(a_anc, 6) if a_anc == a_anc else None),
                                   recip=(round(a_rec, 6) if a_rec == a_rec else None),
                                   diff=(round(diff, 6) if diff == diff else None))
        if diff == diff and diff < -NO_REGRESSION_EPS:
            no_regress_adequate = False
    no_regression = bool(no_regress_overall and no_regress_adequate)

    # ---- COLD bucket (the primary question) ----
    cold_anchor = _bucket_mrr(per_seed, "cold", ANCHOR)
    cold_recip = _bucket_mrr(per_seed, "cold", RECIP)
    cold_recipscr = _bucket_mrr(per_seed, "cold", RECIPSCR)
    cold_random = _bucket_mrr(per_seed, "cold", RANDOM)
    cold_oracle = _bucket_mrr(per_seed, "cold", ORACLE)
    n_cold_q = int(sum(ps.get("localization", {}).get("n_cold_q", 0) for ps in per_seed))
    n_cold_recip = int(sum(ps.get("localization", {}).get("n_cold_with_recip", 0) for ps in per_seed))

    cold_lift_vs_anchor = _sub(cold_recip, cold_anchor)
    cold_recip_vs_random = _sub(cold_recip, cold_random)
    cold_scr_margin = _sub(cold_recip, cold_recipscr)
    cold_scr_rel_target = (COLD_SCR_REL_FRAC * cold_recip_vs_random
                           if cold_recip_vs_random == cold_recip_vs_random else float("nan"))
    cold_scr_noise_ok = bool(_sub(cold_recipscr, cold_random) == _sub(cold_recipscr, cold_random)
                             and abs(cold_recipscr - cold_random) <= COLD_SCR_NOISE) \
        if (cold_recipscr == cold_recipscr and cold_random == cold_random) else False
    cold_scr_controlled = bool(cold_scr_margin == cold_scr_margin and cold_scr_rel_target == cold_scr_rel_target
                               and cold_scr_margin >= cold_scr_rel_target and cold_scr_noise_ok)

    enough_cold = bool(n_cold_q >= MIN_COLD_Q)
    construction_fired = bool(n_cold_recip >= MIN_COLD_RECIP)

    cold_hard_pass = bool(cold_recip == cold_recip and cold_recip >= COLD_HP_MRR
                          and cold_lift_vs_anchor == cold_lift_vs_anchor and cold_lift_vs_anchor >= COLD_RECIP_MARGIN
                          and cold_scr_controlled)
    cold_hard_fail = bool(cold_recip == cold_recip and cold_recip < COLD_HF_MRR and construction_fired)

    # ---- verdict resolution (fail-closed order) ----
    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken:
        verdict = "BROKEN_TEST_CONTROL_BEATS_POP"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif not gate_d_reproduce:
        verdict = "INCONCLUSIVE_BASELINE_NOT_REPRODUCED"
    elif not enough_cold:
        verdict = "INCONCLUSIVE_TOO_FEW_COLD"
    elif not construction_fired:
        verdict = "INCONCLUSIVE_COLD_NO_RECIP_SUPPORT"
    elif cold_hard_pass and no_regression and scramble_controlled:
        verdict = "HARD_PASS_RECIPROCAL_COLD_RESCUE"
    elif cold_hard_pass and not (no_regression and scramble_controlled):
        verdict = "MIDDLE_BAND_COLD_RESCUE_WITH_REGRESSION_OR_CONFOUND"
    elif cold_hard_fail:
        verdict = "HARD_FAIL_COLD_NO_RECIPROCAL_TRANSFER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_COLD_RESCUE"

    verdict_msg = (
        "%s || COLD-bucket MRR [n_cold=%d n_cold_recip=%d]: ANCHOR=%s RECIP=%s RECIP_SCR=%s RANDOM=%s ORACLE=%s "
        "|| cold_lift(RECIP-ANCHOR)=%s (HP>=%.3f abs & lift>=%.3f) cold_scr_margin=%s (>=%.2f*cold_headroom & scr "
        "within %.3f of random=%s) construction_fired=%s "
        "|| OVERALL MRR: ANCHOR=%s RECIP=%s gain=%s (secondary>=%.3f) no_regression=%s "
        "|| oracle_fires=%s gate_d_reproduce(ANCHOR=%s vs %.4f+-%.3f)=%s scramble_controlled=%s broken=%s "
        "|| frac=%.2f support_frac=%.2f seeds=%d"
        % (
            verdict, n_cold_q, n_cold_recip, _fmt(cold_anchor), _fmt(cold_recip), _fmt(cold_recipscr),
            _fmt(cold_random), _fmt(cold_oracle), _fmt(cold_lift_vs_anchor), COLD_HP_MRR, COLD_RECIP_MARGIN,
            _fmt(cold_scr_margin), COLD_SCR_REL_FRAC, COLD_SCR_NOISE, cold_scr_noise_ok, construction_fired,
            _fmt(m[ANCHOR]), _fmt(m[RECIP]), _fmt(overall_gain), OVERALL_GAIN_MIN, no_regression,
            oracle_fires, _fmt(m[ANCHOR]), GATED_REPRODUCE_TARGET, GATED_REPRODUCE_TOL, gate_d_reproduce,
            scramble_controlled, broken,
            _nm([ps["heldout_entity_frac"] for ps in per_seed]),
            _nm([ps["support_frac"] for ps in per_seed]), len(per_seed)))

    def _rnd(x, nd=6):
        return round(x, nd) if x == x else None

    gates = dict(
        verdict=verdict,
        ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        cold_bucket=dict(anchor=_rnd(cold_anchor), recip=_rnd(cold_recip), recip_scramble=_rnd(cold_recipscr),
                         random=_rnd(cold_random), oracle=_rnd(cold_oracle),
                         lift_recip_vs_anchor=_rnd(cold_lift_vs_anchor),
                         recip_vs_random=_rnd(cold_recip_vs_random), scramble_margin=_rnd(cold_scr_margin),
                         n_cold_q=n_cold_q, n_cold_with_recip=n_cold_recip),
        overall=dict(anchor=_rnd(m[ANCHOR]), recip=_rnd(m[RECIP]), gain=_rnd(overall_gain),
                     no_regression_overall=no_regress_overall),
        no_regression_adequate_buckets=adequate_regress,
        oracle_headroom=_rnd(oracle_headroom),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        scramble_margin_vs_random=_rnd(d_scramble),
        n_query_scored=n_query,
        bands=dict(CEIL_METRIC=CEIL_METRIC, COLD_HP_MRR=COLD_HP_MRR, COLD_HF_MRR=COLD_HF_MRR,
                   COLD_RECIP_MARGIN=COLD_RECIP_MARGIN, COLD_SCR_REL_FRAC=COLD_SCR_REL_FRAC,
                   COLD_SCR_NOISE=COLD_SCR_NOISE, MIN_COLD_Q=MIN_COLD_Q, MIN_COLD_RECIP=MIN_COLD_RECIP,
                   OVERALL_GAIN_MIN=OVERALL_GAIN_MIN, NO_REGRESSION_EPS=NO_REGRESSION_EPS,
                   ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   GATED_REPRODUCE_TARGET=GATED_REPRODUCE_TARGET, GATED_REPRODUCE_TOL=GATED_REPRODUCE_TOL,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough_heldout, oracle_fires=oracle_fires, gate_d_reproduce=gate_d_reproduce,
        enough_cold=enough_cold, construction_fired=construction_fired,
        cold_scr_controlled=cold_scr_controlled, scramble_controlled=scramble_controlled,
        no_regression=no_regression, broken=broken,
        cold_hard_pass=cold_hard_pass, cold_hard_fail=cold_hard_fail,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test. Planted arena with COLD-head-only entities: ANCHOR_RECIP rescues the COLD bucket that the
# tail-only ANCHOR cannot touch; ANCHOR_RECIP_SCRAMBLE collapses; ORACLE fires; arms differ.
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
    pool = build_planted_transe_arena(7, n_ent=400, n_rel=6, k_lat=8, deg=3)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, device, 7, "PLANTED_TRANSE_COLD_HEAD", localize=True)
    loc = res.get("localization", {})
    out = dict(n_grid_entities=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_tail_support=res.get("n_tail_support"), n_head_support=res.get("n_head_support"),
               n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"),
               n_cold_q=loc.get("n_cold_q"), n_cold_with_recip=loc.get("n_cold_with_recip"),
               support_deg_hist=loc.get("support_deg_hist"), cold_recip_deg_hist=loc.get("cold_recip_deg_hist"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%s)" % res.get("n_query_scored")
        return False, out

    n_cold_recip = int(loc.get("n_cold_with_recip", 0) or 0)
    if n_cold_recip < SELFTEST_MIN_COLD:
        out["fail"] = ("planted grid produced too few COLD entities with reciprocal head-support (%d < %d) -- the "
                       "adversarial discriminator cannot fire" % (n_cold_recip, SELFTEST_MIN_COLD))
        return False, out

    ah = res["arm_hits"]
    m = {a: ah[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))

    # COLD-bucket arm MRRs (the adversarial discriminator target)
    cold = loc.get("by_support_degree", {}).get("cold", {})
    cold_anchor = cold.get(ANCHOR, {}).get("mrr", float("nan"))
    cold_recip = cold.get(RECIP, {}).get("mrr", float("nan"))
    cold_recipscr = cold.get(RECIPSCR, {}).get("mrr", float("nan"))
    cold_random = cold.get(RANDOM, {}).get("mrr", float("nan"))

    oracle_margin = _sub(m[ORACLE], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])
    oracle_recovers = bool(m[ORACLE] == m[ORACLE] and m[ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)

    cold_recip_recovers = bool(cold_recip == cold_recip and cold_recip >= SELFTEST_COLD_RECIP_MRR_MIN)
    cold_recip_beats_anchor = bool(_sub(cold_recip, cold_anchor) == _sub(cold_recip, cold_anchor)
                                   and _sub(cold_recip, cold_anchor) >= SELFTEST_COLD_MARGIN)
    cold_scramble_fails = bool(_sub(cold_recip, cold_recipscr) == _sub(cold_recip, cold_recipscr)
                               and _sub(cold_recip, cold_recipscr) >= SELFTEST_COLD_SCR_MARGIN)
    pop_at_floor = bool(m[POP] == m[POP] and m[POP] <= max(m[RANDOM], 0.02) + CONTROL_LOSE_EPS)
    arms_differ = bool(n_sigs >= 6)

    # VACUOUS-SMOKE guard: the tail-only ANCHOR must NOT already reach ANCHOR_RECIP on the COLD bucket (else the
    # reciprocal lever is not the thing being measured / the COLD bucket is not answerable via reciprocal edges).
    recip_reached_by_anchor = bool(_sub(cold_recip, cold_anchor) <= SELFTEST_COLD_MARGIN)
    assert_discriminator_fires(recip_reached_by_anchor, control_name=ANCHOR,
                               headline_name="reciprocal_lifts_cold_over_tail_only_anchor", run_mode="self_test",
                               extra="tail-only ANCHOR reached ANCHOR_RECIP on the planted COLD bucket -> reciprocal "
                                     "head-bundle is not the discriminating lever / COLD not answerable via head edges")

    st_verdict, st_msg, st_gates = aggregate_and_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": "ORACLE_ADDITIVE", "headline_name": "oracle_beats_random_heldout_mrr",
         "extra": "planted grid: ORACLE (learned held-out codes) recovers held-out tails and clears RANDOM by the "
                  "ceiling-aware ratio+abs fire gate -> the arena is answerable when a code exists"},
        {"kind": "metric_moves", "metric_name": "cold_bucket_mrr",
         "values": [cold_random, cold_anchor, cold_recip, m[ORACLE]],
         "extra": "COLD-bucket MRR RANDOM=%.3f ANCHOR(tail-only)=%.3f RECIP=%.3f ORACLE=%.3f: the reciprocal "
                  "head-bundle moves the COLD population the tail-only composer leaves at the random floor"
                  % (cold_random, cold_anchor, cold_recip, m[ORACLE])},
        {"kind": "negative_control_margin", "control_scores": [cold_random, cold_recipscr],
         "headline_threshold": cold_recip, "higher_is_pass": True, "margin": SELFTEST_COLD_SCR_MARGIN,
         "n_repeats_min": 2, "control_name": "RANDOM_and_RECIP_SCRAMBLE_below_recip_on_cold",
         "extra": "RANDOM + inverse-relation-scrambled ANCHOR_RECIP_SCRAMBLE must sit below ANCHOR_RECIP on the COLD "
                  "bucket by the MRR margin -> the COLD rescue is the TRAINED inverse operator, not more vectors"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "gate_d_reproduce", "enough_cold",
                                    "construction_fired", "cold_scr_controlled", "no_regression"],
         "exercised_gates": ["arms_differ", "oracle_fires", "gate_d_reproduce", "enough_cold",
                             "construction_fired", "cold_scr_controlled", "no_regression"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % st_verdict},
    ], run_mode="self_test")

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    out.update(
        heldout_mrr={a: round(m[a], 5) for a in ALL_ARMS},
        heldout_metric_spectrum={a: {mk: round(ah[a].get(mk, float("nan")), 5) for mk in metric_keys}
                                 for a in ALL_ARMS},
        cold_bucket_mrr=dict(anchor=round(cold_anchor, 5) if cold_anchor == cold_anchor else None,
                             recip=round(cold_recip, 5) if cold_recip == cold_recip else None,
                             recip_scramble=round(cold_recipscr, 5) if cold_recipscr == cold_recipscr else None,
                             random=round(cold_random, 5) if cold_random == cold_random else None,
                             n=cold.get(RECIP, {}).get("n", 0)),
        n_distinct_sigs=n_sigs,
        oracle_margin=round(oracle_margin, 5) if oracle_margin == oracle_margin else None,
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires,
        cold_recip_recovers=cold_recip_recovers, cold_recip_beats_anchor=cold_recip_beats_anchor,
        cold_scramble_fails=cold_scramble_fails, pop_at_floor=pop_at_floor, arms_differ=arms_differ,
        selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(oracle_recovers and oracle_fires and cold_recip_recovers and cold_recip_beats_anchor
              and cold_scramble_fails and pop_at_floor and arms_differ)
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

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s epochs=%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["epochs"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s cold_recip=%s cold_anchor=%s cold_scr_fails=%s oracle_fires=%s vp_ok=%s "
         "n_cold_recip=%s" %
         (st_ok, st_res.get("cold_bucket_mrr", {}).get("recip"), st_res.get("cold_bucket_mrr", {}).get("anchor"),
          st_res.get("cold_scramble_fails"), st_res.get("oracle_fires"), st_res.get("validity_preflight_ok"),
          st_res.get("n_cold_with_recip")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (reciprocal did not rescue COLD / did not beat tail-only ANCHOR, "
                        "or scramble did not collapse, or ORACLE did not fire, or POP not at floor, or arms not "
                        "distinct): %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS reciprocal cold-rescue: the trained-inverse head-bundle lifts a planted COLD "
                        "entity (only head edges) over the tail-only ANCHOR; relation-scramble collapses; ORACLE "
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
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY_RECIP", ckpt_dir=out_dir, localize=True)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 6:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            loc = res.get("localization", {})
            cold = loc.get("by_support_degree", {}).get("cold", {})
            _log("seed=%d nq=%d n_tail_sup=%d n_head_sup=%d n_cold=%d n_cold_recip=%s | COLD mrr ANCHOR=%s RECIP=%s "
                 "RECIP_SCR=%s RANDOM=%s (%.1fs)" %
                 (seed, res["n_query_scored"], res["n_tail_support"], res["n_head_support"], res["n_cold"],
                  loc.get("n_cold_with_recip"),
                  _fmt(cold.get(ANCHOR, {}).get("mrr", float("nan"))), _fmt(cold.get(RECIP, {}).get("mrr", float("nan"))),
                  _fmt(cold.get(RECIPSCR, {}).get("mrr", float("nan"))), _fmt(cold.get(RANDOM, {}).get("mrr", float("nan"))),
                  time.time() - ts))
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
