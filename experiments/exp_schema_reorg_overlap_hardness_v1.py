"""exp_schema_reorg_overlap_hardness_v1 -- the honest hard version of the schema-reorg trigger-detection problem.

CLOSES the reorg thread. The prior cell (exp_schema_reorg_distractor_detection_cost_v1, commit b7eecdd1c)
showed a K-consecutive confirmation gate cleanly separates genuine reorganizations (sustained AGENT run >=6)
from distractor wobbles (transient AGENT run <=3). Its VET (a86a37c6) flagged that separation as BAKED INTO
the corpus: wobbler and genuine sustain-lengths were disjoint by construction, so precision was trivially
recoverable. Revival criterion: does the gate survive when the genuine-vs-distractor SUSTAIN-LENGTH
DISTRIBUTIONS OVERLAP (separation NOT guaranteed)?

WHAT WE BUILD (glass-box, local numpy, NO LLM/atoms/push):
  * The DISCRIMINATING STATISTIC is the online SUSTAIN-RUN: the number of consecutive touches on which an
    entity reads AGENT (subj_count > obj_count). Per the prior cell's mechanism, peak-margin is coupled 1:1 to
    this run, so the K-consecutive confirmation gate IS a threshold on sustain-run length. At the moment the gate
    must decide (run reaches K), a genuine reorg and a distractor wobble that have reached the SAME run length
    are INDISTINGUISHABLE -- the only signal is the length itself. That is the honest hard case.
  * A PARAMETERIZED corpus: genuine sustain-lengths L_g ~ clipped discretized Gaussian(mu_g, sigma); distractor
    transient-run lengths L_d ~ Gaussian(mu_d, sigma) with mu_d < mu_g, followed by a STRONG revert (obj-run of
    fixed strength REVERT_STRENGTH) so the distractor's net/final type is UNCHANGED (PATIENT) -- a genuine
    transient wobble. Sweeping mu_g toward mu_d slides the two length distributions from DISJOINT (baked-in
    separable, prior-cell regime) to HEAVY OVERLAP. We report the MEASURED overlap coefficient per sweep point
    (OVL = sum_l min(p_g(l), p_d(l))) so the overlap is verified real, not assumed.
  * THREE gate candidates, contrasted:
      - IRREVERSIBLE hard-K: once an entity is confirmed+reindexed PATIENT->AGENT it is frozen (models a
        committed consolidation that cannot cheaply undo). A distractor that reaches run K falsely commits and
        STAYS wrong -> permanent false positive. precision/recall ROC is bounded by the length-overlap.
      - COST-WEIGHTED K*: pick the confirmation threshold minimizing expected cost C_fp*FP + C_fn*FN for a stated
        cost ratio. This is OPERATING-POINT SELECTION on the identical irreversible ROC -- we VERIFY its (P,R)
        lands on the swept-K frontier, so it CANNOT extend the usable-overlap envelope (Neyman-Pearson: a monotone
        rule on the same statistic traces the same ROC). It only relocates the point under asymmetric costs.
      - REVERSIBLE gate (substrate-native affordance: glass-box exact un-reindex): symmetric K-confirmation both
        directions. A falsely-committed distractor, once its strong revert is K-confirmed, is un-reindexed back to
        PATIENT -> END-STATE precision recovers. But at a PRICE: extra re-file WRITES (thrash) and a TRANSIENT
        MIS-FILING window (queries during the wobble hit the wrong partition = stale-steps). We report end-state
        precision/recall AND thrash AND stale-steps AND the min achievable total cost vs overlap -- the reversible
        gate does NOT manufacture separability, it CONVERTS the correctness wall into a cost curve.
  * A compact VSA CONSTRUCTION-PROOF (reuses the prior cell's VSAStore + FHRR SVO encode/decode): at a separable
    setting, confirm no_reorg leaves genuine typed-retrieval STALE and the gated (reversible) targeted arm
    RECOVERS it -- grounding the abstract integer sweep in real substrate retrieval.

METRICS (reported SEPARATELY, never blobbed):
  (a) irreversible hard-K: precision + recall of the BEST operating point AS A FUNCTION OF overlap fraction; the
      full per-K curve at each overlap; the max OVL at which some K gives BOTH precision>=0.80 AND recall>=0.80
      (the usable-overlap envelope) and the OVL where NO threshold does (the fundamental-hardness boundary).
  (b) cost-weighted K*: (P,R) at K*, VERIFIED on the hard-K ROC; the usable envelope is IDENTICAL to (a) ->
      cost-weighting selects an operating point, does NOT extend separability.
  (c) reversible gate: end-state precision/recall (recovers), thrash writes, transient stale-steps, and min total
      cost, each vs overlap -- does substrate-native reversibility extend the USABLE-OVERLAP range, and at what
      cost? (Report honestly; do NOT over-read a cost-shift as 'solved'.)

PRE-REG (envelope-fail-bands; I own the bands; verdict at the FULL seed set):
  HARD_PASS (a principled hard gate is ROBUST to MODERATE overlap):
    - separable control reproduces the prior cell: at OVL <= 0.10, best-K gives both precision>=0.90 & recall>=0.90
    - robustness: at a MODERATE overlap (measured OVL in [0.28, 0.45]), some K gives both precision>=0.80 &
      recall>=0.80  -> reorg trigger is robust to moderate overlap, not just baked-in separation
    - the usable-overlap envelope is WELL-DEFINED (monotone: a clean breaking boundary exists) AND
    - cost-weighted K* verified ON the hard-K ROC (usable envelope identical -> no false separability-extension).
  HARD_FAIL (trigger-detection is fundamentally hard the moment distributions overlap):
    - the gate breaks at LOW overlap: NO K gives both precision>=0.80 & recall>=0.80 already at measured OVL<=0.15
      (usable only in the near-separable baked-in regime) -> the reorg fix works ONLY under the sustained-vs-
      transient separation assumption; an honest STRUCTURAL BOUND on the trigger half of the native-edit advantage.
  MIDDLE otherwise: the gate holds only up to MILD overlap (breaks in (0.15, 0.28)); characterize the envelope.
    (The reversible gate's end-state recovery + its thrash/stale cost curve are reported in ALL tiers; a reversible
     cost-shift is NEVER counted as a hard-K pass.)

HONEST NOTE (reported regardless of tier): the sustain-run is the ONLY online signal at decision time; when the
  genuine/distractor length distributions overlap, no gate on that statistic can separate what the signal does not
  -- this is a Neyman-Pearson bound, not an engineering shortfall. Substrate-native reversibility (cheap exact
  un-reindex, an affordance the brain's committed cortical consolidation lacks) does not beat the bound; it moves
  the hardness from irrecoverable-error to write-thrash + transient-mis-filing, whose cost grows with overlap.
  BRAIN CHECK: the brain faces exactly 'is this a real change or noise?' and answers it with a FAST reversible
  hippocampal trace + SLOW confirmation-gated cortical consolidation (systems consolidation waits for repeated,
  sleep-spaced corroboration before committing schema edits) plus prediction-error / surprise weighting -- i.e. a
  two-timescale reversible+confirmed architecture, exactly the fast-reversible + slow-confirmed pair contrasted
  here. The overlap hardness is REAL and the brain's answer is not separation-by-magic but reversibility + delay.

Local numpy, NO queue/GPU/atoms/push. ASCII-only. FHRR = complex128 unit phasors (reused from the SVO probe).
Sequential-CPU (genuine sequential dependency: the store grows fact-by-fact; belief + confirmation state depend on
the accumulated stream). Storage: SHARDED (one exact VSA vector per fact) + cached type-partition. Compute: <=5
seeds, 7 overlap points, 10 K values, ~80 boundary entities/seed pure-integer detector + one small VSA arm ->
wall < 20s. progress_logging=print_flush_true.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; irreversible vs reversible detector outputs differ under
#     overlap; VSA no_reorg vs targeted partition-hash differ).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor. precision/recall/cost are exact integer bookkeeping over sampled
#     sustain-lengths; the ROC is set by the discrete length histograms (reported), not a signal-noise CRLB.
# - baseline_in_band at smoke: NAIVE gate (K=1) precision under overlap in (0.05, 0.95) (distractors false-trigger
#     -> the overlap control FIRES); and best-K precision > naive at low overlap (the gate is the discriminator).
# - discriminator survives scale: the overlap SWEEP is the discriminator; it MUST cross the usable/unusable
#     boundary (>=1 overlap point PASSES both>=0.80 and >=1 FAILS). Vacuous (all pass or all fail) -> re-spec.
# - HARD_PASS strictly above floors; margins declared in prereg JSON.
# - real_code_path (F.1): self_test constructs the REAL objects (imported make_phasors/encode_meaning/unbind/
#     cleanup + VSAStore + the detector + overlap sweep) at tiny scale and asserts (not a synthetic-only branch).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab; np.random.default_rng(seed) only; NO
#     hash()/list(set()) for seeds/splits.
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import hashlib
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "schema_reorg_overlap_hardness_v1"
N_DIM = 1024

# reuse the proven FHRR primitives (same stable imports the v1 reorg cell used) + the prior cell's VSAStore.
from experiments.exp_nativelang_svo_vsa_probe_v1 import (
    make_phasors as _make_phasors,
    encode_meaning as _encode_meaning,
    unbind as _unbind,
    cleanup as _cleanup,
)
from experiments.exp_schema_reorg_distractor_detection_cost_v1 import VSAStore, AGENT, PATIENT

SUBJ, VERB, OBJ = 0, 1, 2

# fixed patient pools (pure objects; never subjects -> robustly PATIENT). sorted for determinism.
FOODS = sorted(["seed", "worm", "grass", "bread", "apple", "berry", "kibble", "nut"])
PLACES = sorted(["barn", "nest", "pond", "tree", "field", "den", "burrow", "reef"])
PREY = sorted(["mouse", "rabbit", "minnow", "cricket", "moth", "vole", "shrew", "gnat"])
VERBS = ("eats", "lives_in", "chases")

# ---- overlap-distribution knobs (I own these) ----------------------------------------------------------------
# The DISCRIMINATING STATISTIC is the effective consecutive-AGENT run the gate sees. A genuine reorg that reaches
# and HOLDS margin g occupies g such touches (commits iff g>=K). A transient wobble that PEAKS at margin m and then
# reverts occupies ~2m-1 such touches (m up + m-1 unwinding while subj still > obj) -- the peak MUST unwind through
# the AGENT zone, that is physical for a count-difference belief. So we draw the genuine run g and the distractor
# PEAK MARGIN m from their own distributions, and measure overlap on the EFFECTIVE runs: genuine g vs distractor
# 2m-1. Sliding mu_g toward the distractor effective mean (2*MU_M-1) slides the two from disjoint to overlapping.
MU_M = 2.5                 # distractor peak-margin mean -> distractor effective-run mean = 2*MU_M-1 = 4.0
SIGMA_M = 0.75             # distractor peak-margin spread -> effective-run spread ~ 2*SIGMA_M = 1.5
SIGMA = 1.5                # genuine run spread
REVERT_STRENGTH = 12       # distractor's post-wobble PATIENT-run length (>= max K -> revert always K-confirmable)
N_GENUINE = 40             # genuine shifters per seed
N_DISTRACTOR = 40          # distractor wobblers per seed
N_STABLE = 20              # pure-agent padding (grows the store; robustly AGENT, never scored)
# overlap sweep: slide mu_g toward MU_D. delta = mu_g - MU_D in {6,4,3,2,1.5,1,0.5}.
# THEORETICAL OVL for equal-sigma Gaussians = 2*Phi(-delta/(2*sigma)); measured OVL reported per point.
MU_G_SWEEP = [10.0, 8.0, 7.0, 6.5, 6.25, 6.0, 5.5, 5.0, 4.5]
K_SWEEP = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
USABLE_P = 0.80            # usable precision floor
USABLE_R = 0.80            # usable recall floor
SEP_OVL = 0.10             # "separable" control: OVL at/below this must reproduce prior cell (both>=0.90)
MODERATE_LO, MODERATE_HI = 0.28, 0.45   # "moderate overlap" band for the HARD_PASS robustness bar
LOW_OVL = 0.15             # HARD_FAIL if the gate already breaks at/below this


# ---------------------------------------------------------------------------
# sustain-length draws + overlap measurement.
# ---------------------------------------------------------------------------
def draw_lengths(rng, n, mu, sigma, lmin=1):
    """n integer sustain-lengths ~ round(Normal(mu, sigma)) clipped to >= lmin. Deterministic given rng."""
    raw = rng.normal(mu, sigma, size=n)
    return [int(max(lmin, round(x))) for x in raw]


def overlap_coefficient(lens_g, lens_d):
    """Empirical overlap coefficient of two integer-length samples: sum_l min(p_g(l), p_d(l)) in [0,1].
    0 = disjoint supports, 1 = identical histograms."""
    def hist(xs):
        h = defaultdict(float)
        for x in xs:
            h[x] += 1.0 / len(xs)
        return h
    hg, hd = hist(lens_g), hist(lens_d)
    keys = set(hg) | set(hd)
    return float(sum(min(hg.get(k, 0.0), hd.get(k, 0.0)) for k in keys))


# ---------------------------------------------------------------------------
# corpus: parameterized boundary-entity scripts with drawn sustain-lengths.
# ---------------------------------------------------------------------------
def build_overlap_corpus(seed, mu_g):
    """Deterministic typed corpus. genuine entity e: 2 obj-appearances then (g+2) subject facts -> effective
    consecutive-AGENT run = g, final type AGENT (SHOULD reindex). distractor entity e: 2 obj-appearances, (m+2)
    subject facts (peak margin m), then a STRONG obj revert (length m+REVERT_STRENGTH) -> the peak unwinds through
    the AGENT zone giving effective run 2m-1, final type PATIENT, net UNCHANGED (should NOT reindex). Returns
    (facts, genuine_set, distractor_set, truetype, concepts, eff_g, eff_d) where eff_* are the EFFECTIVE runs the
    gate sees (used for the honest overlap measurement)."""
    rng = np.random.default_rng(seed)
    runs_g = draw_lengths(rng, N_GENUINE, mu_g, SIGMA)          # genuine effective run = g
    margins_d = draw_lengths(rng, N_DISTRACTOR, MU_M, SIGMA_M)  # distractor peak margin m
    eff_g = list(runs_g)
    eff_d = [2 * m - 1 for m in margins_d]                      # distractor effective run

    stable = [f"anml{i:03d}" for i in range(N_STABLE)]
    genuine = [f"gshift{i:03d}" for i in range(N_GENUINE)]
    distract = [f"wobble{i:03d}" for i in range(N_DISTRACTOR)]

    truetype = {}
    for a in stable:
        truetype[a] = AGENT
    for pool in (FOODS, PLACES, PREY):
        for p in pool:
            truetype[p] = PATIENT
    for e in genuine:
        truetype[e] = AGENT
    for e in distract:
        truetype[e] = PATIENT

    facts = []
    obj_cursor = [0]

    def emit_obj(e, si):
        a = stable[(si + obj_cursor[0]) % N_STABLE]
        obj_cursor[0] += 1
        facts.append((a, "eats", e))

    def emit_subj(e, s_idx, si):
        pool = (FOODS, PLACES, PREY)[s_idx % 3]
        filler = pool[(si + s_idx) % len(pool)]
        facts.append((e, VERBS[s_idx % 3], filler))

    for i, e in enumerate(genuine):
        emit_obj(e, i); emit_obj(e, i)                 # 2 obj -> belief PATIENT baseline
        for j in range(runs_g[i] + 2):                 # (g+2) subject facts -> effective AGENT run = g
            emit_subj(e, j, i)
    for i, e in enumerate(distract):
        si = i + 500
        emit_obj(e, si); emit_obj(e, si)
        for j in range(margins_d[i] + 2):              # (m+2) subject facts -> peak margin m
            emit_subj(e, j, si)
        for _ in range(margins_d[i] + REVERT_STRENGTH):    # strong revert -> unwind (run 2m-1) then final PATIENT
            emit_obj(e, si)
    # stable padding (pure subjects -> robustly AGENT; never wobble, not scored).
    for i, a in enumerate(stable):
        facts.append((a, "eats", FOODS[i % len(FOODS)]))
        facts.append((a, "lives_in", PLACES[i % len(PLACES)]))
        facts.append((a, "chases", PREY[i % len(PREY)]))

    relations = sorted(set(r for (_, r, _) in facts))
    concepts = sorted(set(stable) | set(genuine) | set(distract)
                      | set(FOODS) | set(PLACES) | set(PREY) | set(relations))
    return facts, set(genuine), set(distract), truetype, concepts, eff_g, eff_d


def _infer_type(subj_c, obj_c, e):
    return AGENT if subj_c[e] > obj_c[e] else PATIENT


# ---------------------------------------------------------------------------
# pure-integer streaming detector with the K-consecutive confirmation gate.
#   mode="irreversible": once reindexed PATIENT->AGENT, the entity is FROZEN (committed consolidation).
#   mode="reversible":   symmetric K-confirmation both directions; a confirmed revert un-reindexes (thrash+stale).
# ---------------------------------------------------------------------------
def run_detector(facts, genuine_set, distract_set, truetype, K, mode, H=0):
    subj_c, obj_c = defaultdict(int), defaultdict(int)
    belief = {}
    cand = {}                          # e -> (candidate_type, consecutive_count)
    frozen = set()                     # irreversible: entities committed to AGENT (no further flips)
    subj_facts = defaultdict(int)      # count of e's own subject-facts (records that move on reindex)
    ever_agent = set()                 # entities committed to AGENT at any point
    writes = 0                         # reindex + un-reindex record-move events (thrash proxy)
    scored = genuine_set | distract_set

    def commit(e, new_t):
        nonlocal writes
        belief[e] = new_t
        cand[e] = (None, 0)
        writes += subj_facts[e]        # move e's filed subject-facts to the new partition
        if new_t == AGENT:
            ever_agent.add(e)

    for (s, r, o) in facts:
        subj_c[s] += 1
        obj_c[o] += 1
        subj_facts[s] += 1
        for e in (s, o):
            if e not in belief:
                belief[e] = _infer_type(subj_c, obj_c, e)   # belief set on first touch
                continue
            if e in frozen:
                continue
            new_t = _infer_type(subj_c, obj_c, e)
            margin = abs(subj_c[e] - obj_c[e])
            if new_t != belief[e] and margin >= H:
                ct, cc = cand.get(e, (None, 0))
                ct, cc = (ct, cc + 1) if ct == new_t else (new_t, 1)
                cand[e] = (ct, cc)
                if cc >= K:
                    commit(e, new_t)
                    if mode == "irreversible" and new_t == AGENT:
                        frozen.add(e)                        # committed consolidation: cannot undo
            else:
                cand[e] = (None, 0)

    # stale-steps: entity-touches (over scored entities) where the running belief != truetype.
    # recompute cheaply by a second pass tracking belief evolution would double work; instead approximate the
    # END-STATE mis-filing (permanent for irreversible false commits; ~0 for reversible w/ strong revert) plus the
    # detector already reflects transient thrash via `writes`. We report end-state correctness + writes.
    final_agent = set(e for e in scored if belief.get(e) == AGENT)
    detected = ever_agent & scored if mode == "irreversible" else final_agent
    tp = len(detected & genuine_set)
    fp = len(detected & distract_set)
    fn = len(genuine_set - detected)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    return {
        "precision": precision, "recall": recall, "tp": tp, "fp": fp, "fn": fn,
        "writes": writes, "n_ever_agent_distract": len(ever_agent & distract_set),
        "n_final_agent_distract": len(final_agent & distract_set),
    }


# ---------------------------------------------------------------------------
# stale-steps: a dedicated pass tracking belief-vs-truetype per touch for the reversible arm (the transient
# mis-filing cost). Kept separate so the ROC detector stays lean.
# ---------------------------------------------------------------------------
def reversible_stale_steps(facts, scored, truetype, K, H=0):
    subj_c, obj_c = defaultdict(int), defaultdict(int)
    belief = {}
    cand = {}
    stale = 0
    for (s, r, o) in facts:
        subj_c[s] += 1
        obj_c[o] += 1
        touched = []
        for e in (s, o):
            if e not in belief:
                belief[e] = _infer_type(subj_c, obj_c, e)
                touched.append(e)
                continue
            new_t = _infer_type(subj_c, obj_c, e)
            margin = abs(subj_c[e] - obj_c[e])
            if new_t != belief[e] and margin >= H:
                ct, cc = cand.get(e, (None, 0))
                ct, cc = (ct, cc + 1) if ct == new_t else (new_t, 1)
                cand[e] = (ct, cc)
                if cc >= K:
                    belief[e] = new_t
                    cand[e] = (None, 0)
            else:
                cand[e] = (None, 0)
            touched.append(e)
        for e in touched:
            if e in scored and belief.get(e) is not None and belief[e] != truetype[e]:
                stale += 1
    return stale


# ---------------------------------------------------------------------------
# sweep: per overlap point, per K, average precision/recall/writes across seeds. + usable envelope.
# ---------------------------------------------------------------------------
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def sweep_overlap(seeds, mu_g_list):
    """For each mu_g: build corpus per seed, measure OVL, run irreversible + reversible detectors across K."""
    points = []
    for mu_g in mu_g_list:
        ovl_s, corpora = [], []
        for s in seeds:
            facts, gen, dis, tt, concepts, lg, ld = build_overlap_corpus(s, mu_g)
            ovl_s.append(overlap_coefficient(lg, ld))
            corpora.append((facts, gen, dis, tt))
        ovl = _mean(ovl_s)

        irr_curve, rev_curve = [], []
        for K in K_SWEEP:
            ip, ir, iw = [], [], []
            rp, rr, rw, rstale = [], [], [], []
            for (facts, gen, dis, tt) in corpora:
                scored = gen | dis
                ri = run_detector(facts, gen, dis, tt, K, "irreversible")
                rv = run_detector(facts, gen, dis, tt, K, "reversible")
                ip.append(ri["precision"]); ir.append(ri["recall"]); iw.append(ri["writes"])
                rp.append(rv["precision"]); rr.append(rv["recall"]); rw.append(rv["writes"])
                rstale.append(reversible_stale_steps(facts, scored, tt, K))
            irr_curve.append({"K": K, "precision": _mean(ip), "recall": _mean(ir), "writes": _mean(iw)})
            rev_curve.append({"K": K, "precision": _mean(rp), "recall": _mean(rr),
                              "writes": _mean(rw), "stale_steps": _mean(rstale)})
        points.append({"mu_g": mu_g, "overlap": ovl, "irreversible": irr_curve, "reversible": rev_curve})
    return points


def usable_at(curve):
    """best operating point: is there a K with precision>=USABLE_P AND recall>=USABLE_R? return (usable, best_K,
    best_precision, best_recall) maximizing min(precision,recall) among usable, else the max-min point."""
    usable_ks = [c for c in curve if c["precision"] is not None and c["recall"] is not None
                 and c["precision"] >= USABLE_P and c["recall"] >= USABLE_R]
    if usable_ks:
        best = max(usable_ks, key=lambda c: min(c["precision"], c["recall"]))
        return True, best["K"], best["precision"], best["recall"]
    valid = [c for c in curve if c["precision"] is not None and c["recall"] is not None]
    if not valid:
        return False, None, None, None
    best = max(valid, key=lambda c: min(c["precision"], c["recall"]))
    return False, best["K"], best["precision"], best["recall"]


def cost_weighted_k(curve, n_gen, n_dis, c_fp, c_fn):
    """pick K* minimizing expected cost c_fp*FP + c_fn*FN over the swept-K frontier. FP = (1-precision-driven)...
    reconstruct counts from precision/recall + class sizes. Returns (K*, precision, recall, cost)."""
    best = None
    for c in curve:
        if c["precision"] is None or c["recall"] is None:
            continue
        tp = c["recall"] * n_gen
        fn = n_gen - tp
        fp = (tp * (1.0 - c["precision"]) / c["precision"]) if c["precision"] > 0 else n_dis
        cost = c_fp * fp + c_fn * fn
        if best is None or cost < best["cost"]:
            best = {"K": c["K"], "precision": c["precision"], "recall": c["recall"], "cost": cost}
    return best


# ---------------------------------------------------------------------------
# VSA construction-proof (reuses the prior cell's VSAStore): separable setting; gated targeted recovers staleness.
# ---------------------------------------------------------------------------
def vsa_construction_proof(seeds, mu_g=10.0, K=4):
    """Small separable corpus -> confirm no_reorg leaves genuine typed-retrieval STALE and gated targeted
    (reversible symmetric-K) RECOVERS it. Reuses VSAStore + FHRR encode/decode."""
    def one(seed, mode):
        facts, gen, dis, tt, concepts, lg, ld = build_overlap_corpus(seed, mu_g)
        cid = {c: i for i, c in enumerate(concepts)}
        rng = np.random.default_rng(seed * 131 + 7)
        C = _make_phasors(rng, len(concepts), N_DIM)
        roles = _make_phasors(rng, 3, N_DIM)
        store = VSAStore(C, roles, cid, 0, K, mode)
        for f in facts:
            store.ingest(f)
        store.finalize()
        subj_facts = sorted(set((s, r, o) for (s, r, o) in store.store_T if tt.get(s) == AGENT))
        shifted = [(s, r, o) for (s, r, o) in subj_facts if s in gen]
        stable_q = [(s, r, o) for (s, r, o) in subj_facts if s not in (gen | dis)]

        def acc(qs):
            return float(np.mean([store.retrieve_typed(*q) for q in qs])) if qs else None
        return {"shifted_acc": acc(shifted), "stable_acc": acc(stable_q),
                "records_touched": store.records_touched, "partition_hash": store.partition_hash()}

    def avg(mode):
        runs = [one(s, mode) for s in seeds]
        return {"shifted_acc": _mean([r["shifted_acc"] for r in runs]),
                "stable_acc": _mean([r["stable_acc"] for r in runs]),
                "records_touched": _mean([r["records_touched"] for r in runs]),
                "partition_hash": runs[0]["partition_hash"]}
    return {"no_reorg": avg("no_reorg"), "targeted": avg("targeted")}


# ---------------------------------------------------------------------------
# verdict.
# ---------------------------------------------------------------------------
def compute_verdict(points, vsa, n_gen, n_dis):
    # per-overlap best irreversible operating point + usable flag.
    rows = []
    for p in points:
        u_irr, k_irr, pi, ri = usable_at(p["irreversible"])
        u_rev, k_rev, pr, rr = usable_at(p["reversible"])
        cw_sym = cost_weighted_k(p["irreversible"], n_gen, n_dis, 1.0, 1.0)
        cw_asym = cost_weighted_k(p["irreversible"], n_gen, n_dis, 1.0, 3.0)
        # reversible min total cost (writes as thrash proxy) at its usable/best K.
        rev_best = next((c for c in p["reversible"] if c["K"] == k_rev), None) if k_rev is not None else None
        rows.append({
            "mu_g": p["mu_g"], "overlap": p["overlap"],
            "irr_usable": u_irr, "irr_best_K": k_irr, "irr_precision": pi, "irr_recall": ri,
            "rev_usable": u_rev, "rev_best_K": k_rev, "rev_precision": pr, "rev_recall": rr,
            "rev_writes_at_bestK": (rev_best["writes"] if rev_best else None),
            "rev_stale_at_bestK": (rev_best["stale_steps"] if rev_best else None),
            "costw_sym_K": cw_sym["K"], "costw_sym_precision": cw_sym["precision"], "costw_sym_recall": cw_sym["recall"],
            "costw_asym_K": cw_asym["K"], "costw_asym_precision": cw_asym["precision"], "costw_asym_recall": cw_asym["recall"],
        })
    rows_sorted = sorted(rows, key=lambda r: r["overlap"])

    # separable control (lowest OVL) must reproduce the prior cell (both>=0.90).
    sep_row = rows_sorted[0]
    sep_curve = next(p["irreversible"] for p in points if p["mu_g"] == sep_row["mu_g"])
    sep_strong = any(c["precision"] is not None and c["recall"] is not None
                     and c["precision"] >= 0.90 and c["recall"] >= 0.90 for c in sep_curve)
    separable_reproduces = sep_row["overlap"] <= SEP_OVL and sep_strong

    # usable-overlap envelope: max OVL at which irreversible is usable.
    usable_ovls = [r["overlap"] for r in rows_sorted if r["irr_usable"]]
    unusable_ovls = [r["overlap"] for r in rows_sorted if not r["irr_usable"]]
    max_usable_ovl = max(usable_ovls) if usable_ovls else 0.0
    min_unusable_ovl = min(unusable_ovls) if unusable_ovls else None
    # crossing: at least one usable AND one unusable point (discriminator fires across the transition).
    crosses = len(usable_ovls) >= 1 and len(unusable_ovls) >= 1
    # monotone envelope: every usable OVL below every unusable OVL (clean boundary).
    monotone = (min_unusable_ovl is None) or (max_usable_ovl <= min_unusable_ovl + 1e-9)

    # robustness at moderate overlap: a usable point in [MODERATE_LO, MODERATE_HI].
    robust_moderate = any(r["irr_usable"] and MODERATE_LO <= r["overlap"] <= MODERATE_HI for r in rows_sorted)

    # cost-weighted verified ON the ROC (its (P,R) is a swept-K point by construction) AND identical usable
    # envelope: for every overlap, cost-weighted-sym usable iff best-K usable.
    cw_envelope_identical = True
    for p, r in zip([pp for pp in sorted(points, key=lambda x: x["overlap"])], rows_sorted):
        cw = cost_weighted_k(p["irreversible"], n_gen, n_dis, 1.0, 1.0)
        cw_usable = (cw["precision"] >= USABLE_P and cw["recall"] >= USABLE_R)
        if cw_usable != r["irr_usable"]:
            # a symmetric-cost optimum can under-shoot a usable point only if the usable point isn't cost-min;
            # both live on the SAME swept-K set, so separability (exists-usable-K) is what matters, not which K
            # cost picks. We check the ENVELOPE claim: cost-weighting does not create usability where none exists.
            if cw_usable and not r["irr_usable"]:
                cw_envelope_identical = False   # would mean cost-weighting invented separability (impossible)
    # reversible extends END-STATE usability beyond irreversible? (report; never a hard-K pass)
    rev_extends = any(r["rev_usable"] and not r["irr_usable"] for r in rows_sorted)

    hp = (separable_reproduces and robust_moderate and crosses and monotone and cw_envelope_identical)
    hf = (not any(r["irr_usable"] and r["overlap"] > LOW_OVL for r in rows_sorted)) and \
         (not robust_moderate)
    tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")

    notes = []
    if not separable_reproduces:
        notes.append(f"SEPARABLE CONTROL did not reproduce prior cell (OVL={sep_row['overlap']:.2f}, "
                     f"strong_both>=0.90={sep_strong}) -> low-overlap regime not clean")
    if not crosses:
        notes.append("VACUOUS SWEEP: overlap sweep did not cross the usable/unusable boundary (all pass or all "
                     "fail) -> re-spec the overlap range")
    if not robust_moderate:
        notes.append(f"gate NOT robust to moderate overlap: no usable point in OVL[{MODERATE_LO},{MODERATE_HI}] "
                     f"-> trigger-detection fragile once distributions overlap (structural bound on the trigger half)")
    if rev_extends:
        notes.append("reversible gate extends END-STATE usability beyond irreversible (un-reindex recovers false "
                     "commits) -- a COST-SHIFT (thrash+stale), NOT a hard-K separability win; do not over-read")
    notes.append(f"cost-weighted K* rides the SAME ROC (envelope_identical={cw_envelope_identical}) -> "
                 "operating-point selection, not separability extension")

    msg = (f"{tier} | separable-control(OVL={sep_row['overlap']:.2f}) reproduces_prior={separable_reproduces} | "
           f"usable-overlap envelope: irreversible usable up to OVL={max_usable_ovl:.2f}"
           + (f", breaks at OVL={min_unusable_ovl:.2f}" if min_unusable_ovl is not None else "")
           + f" (crosses={crosses} monotone={monotone}) | robust_to_moderate_overlap[{MODERATE_LO},{MODERATE_HI}]="
           f"{robust_moderate} | cost-weighted rides same ROC={cw_envelope_identical} | "
           f"reversible end-state recovers (extends_usable={rev_extends}) at thrash+stale cost | "
           f"VSA: no_reorg_shifted={vsa['no_reorg']['shifted_acc']:.2f} targeted_shifted={vsa['targeted']['shifted_acc']:.2f}"
           f" | {'; '.join(notes)}")

    summ = {
        "separable_control_overlap": sep_row["overlap"], "separable_reproduces_prior": separable_reproduces,
        "max_usable_overlap_irreversible": max_usable_ovl, "min_unusable_overlap_irreversible": min_unusable_ovl,
        "sweep_crosses_boundary": crosses, "envelope_monotone": monotone,
        "robust_to_moderate_overlap": robust_moderate, "moderate_band": [MODERATE_LO, MODERATE_HI],
        "cost_weighted_rides_same_roc": cw_envelope_identical,
        "reversible_extends_endstate_usability": rev_extends,
        "usable_precision_floor": USABLE_P, "usable_recall_floor": USABLE_R,
        "per_overlap": rows_sorted,
        "vsa_no_reorg_shifted": vsa["no_reorg"]["shifted_acc"], "vsa_no_reorg_stable": vsa["no_reorg"]["stable_acc"],
        "vsa_targeted_shifted": vsa["targeted"]["shifted_acc"], "vsa_targeted_stable": vsa["targeted"]["stable_acc"],
        "notes": notes,
    }
    return tier, msg, summ


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = (f"exp_{ANCHOR_NAME}" if run_mode == "full" else
           (f"exp_{ANCHOR_NAME}_smoke" if run_mode == "smoke" else f"exp_{ANCHOR_NAME}_selftest"))
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the overlap discriminator FIRES + arms differ.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (make_phasors/encode/decode + detector + VSAStore + sweep)...",
          flush=True)
    exercised = set()
    # FHRR round-trip on the real primitives.
    rng = np.random.default_rng(3)
    C = _make_phasors(rng, 8, 256); exercised.add("make_phasors")
    roles = _make_phasors(rng, 3, 256)
    M = _encode_meaning((1, 4, 6), C, roles); exercised.add("encode_meaning")
    oi = _cleanup(_unbind(M, roles[OBJ]), C); exercised.add("unbind_cleanup")
    assert oi == 6, f"FHRR SVO round-trip failed: obj={oi}"

    seeds = [7, 13]
    # corpus at low overlap (separable) and high overlap must actually differ in OVL.
    _, gen, dis, tt, _, lg_sep, ld_sep = build_overlap_corpus(7, 10.0); exercised.add("build_overlap_corpus")
    ovl_sep = overlap_coefficient(lg_sep, ld_sep)
    _, _, _, _, _, lg_hi, ld_hi = build_overlap_corpus(7, 4.5)
    ovl_hi = overlap_coefficient(lg_hi, ld_hi)
    assert ovl_sep < 0.15, f"separable corpus not separable: OVL={ovl_sep:.2f}"
    assert ovl_hi > 0.45, f"high-overlap corpus not overlapping: OVL={ovl_hi:.2f}"
    assert ovl_hi > ovl_sep + 0.3, f"overlap sweep does not move OVL: {ovl_sep:.2f}->{ovl_hi:.2f}"
    assert len(gen) >= 10 and len(dis) >= 10, f"too few boundary entities: gen={len(gen)} dis={len(dis)}"

    # OVERLAP DISCRIMINATOR MUST FIRE: separable -> gate usable (both>=0.90); heavy overlap -> gate NOT usable.
    pts = sweep_overlap(seeds, [10.0, 4.5]); exercised.add("sweep_overlap")
    sep = next(p for p in pts if p["mu_g"] == 10.0)
    hi = next(p for p in pts if p["mu_g"] == 4.5)
    u_sep, k_sep, p_sep, r_sep = usable_at(sep["irreversible"])
    u_hi, k_hi, p_hi, r_hi = usable_at(hi["irreversible"])
    assert u_sep, f"separable regime NOT usable (gate broken even when separable): best P={p_sep} R={r_sep}"
    assert p_sep >= 0.90 and r_sep >= 0.90, f"separable regime weak: P={p_sep} R={r_sep}"
    assert not u_hi, f"VACUOUS: heavy-overlap regime STILL usable (OVL={hi['overlap']:.2f}) -> criterion too lax"

    # NAIVE (K=1) precision under overlap must FIRE (distractors false-trigger -> precision < 0.95).
    naive_hi = next(c for c in hi["irreversible"] if c["K"] == 1)
    assert naive_hi["precision"] < 0.95, f"overlap control VACUOUS: naive K=1 precision={naive_hi['precision']:.2f}"

    # ARMS-MUST-DIFFER (META_RULE_AF): irreversible vs reversible outputs differ under overlap.
    ri = run_detector(*_corpus_tuple(7, 5.0), K=2, mode="irreversible"); exercised.add("run_detector")
    rv = run_detector(*_corpus_tuple(7, 5.0), K=2, mode="reversible")
    assert (ri["fp"], ri["writes"]) != (rv["fp"], rv["writes"]), \
        f"META_RULE_AF: irreversible vs reversible bit-identical under overlap: {ri} == {rv}"
    # reversible recovers end-state precision (un-reindex) relative to irreversible under overlap.
    assert rv["n_final_agent_distract"] <= ri["n_ever_agent_distract"], \
        "reversible did not reduce final false-AGENT distractors vs irreversible ever-committed"

    # cost-weighted rides the swept-K set (its K is one of K_SWEEP).
    cw = cost_weighted_k(hi["irreversible"], N_GENUINE, N_DISTRACTOR, 1.0, 3.0); exercised.add("cost_weighted_k")
    assert cw["K"] in K_SWEEP, f"cost-weighted K* not on swept ROC: {cw['K']}"

    # VSA construction-proof: no_reorg leaves genuine stale; targeted recovers.
    vsa = vsa_construction_proof(seeds, mu_g=10.0, K=4); exercised.add("vsa_construction_proof")
    assert vsa["no_reorg"]["shifted_acc"] < vsa["no_reorg"]["stable_acc"] - 0.05, \
        f"no_reorg staleness did not fire: shifted={vsa['no_reorg']['shifted_acc']} stable={vsa['no_reorg']['stable_acc']}"
    assert vsa["targeted"]["shifted_acc"] >= vsa["no_reorg"]["shifted_acc"] + 0.10, \
        f"targeted did NOT recover: targ={vsa['targeted']['shifted_acc']} noreorg={vsa['no_reorg']['shifted_acc']}"
    assert vsa["no_reorg"]["partition_hash"] != vsa["targeted"]["partition_hash"], \
        "META_RULE_AF: VSA no_reorg vs targeted partition-hash identical"

    for ep in ["make_phasors", "encode_meaning", "unbind_cleanup", "build_overlap_corpus", "sweep_overlap",
               "run_detector", "cost_weighted_k", "vsa_construction_proof"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"
    print(f"[self_test] PASS | OVL sep={ovl_sep:.2f}->hi={ovl_hi:.2f} | separable usable(K={k_sep}) P={p_sep:.2f} "
          f"R={r_sep:.2f} | heavy-overlap usable={u_hi} (best P={p_hi:.2f} R={r_hi:.2f}) | naive_hi_prec="
          f"{naive_hi['precision']:.2f} | irr.fp={ri['fp']} rev.fp={rv['fp']} rev.writes>{ri['writes']} | "
          f"VSA noreorg_shifted={vsa['no_reorg']['shifted_acc']:.2f} targ={vsa['targeted']['shifted_acc']:.2f}",
          flush=True)
    return True


def _corpus_tuple(seed, mu_g):
    """helper: (facts, genuine, distract, truetype) for run_detector."""
    facts, gen, dis, tt, _, _, _ = build_overlap_corpus(seed, mu_g)
    return facts, gen, dis, tt


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    seeds = [7, 13] if run_mode == "smoke" else [7, 13, 29, 41, 53]
    mu_g_list = [10.0, 6.25, 4.5] if run_mode == "smoke" else MU_G_SWEEP
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * len(mu_g_list) * len(K_SWEEP) * 2   # 2 detector modes
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[overlap] run_mode={run_mode} seeds={seeds} mu_g_list={mu_g_list} K_SWEEP={K_SWEEP}", flush=True)

    points = sweep_overlap(seeds, mu_g_list)
    for p in points:
        u, k, pp, rr = usable_at(p["irreversible"])
        print(f"[overlap] mu_g={p['mu_g']:.1f} OVL={p['overlap']:.2f} irr_usable={u} bestK={k} "
              f"P={pp:.2f} R={rr:.2f}", flush=True)
    vsa = vsa_construction_proof(seeds, mu_g=10.0, K=4)
    print(f"[overlap] VSA proof: no_reorg_shifted={vsa['no_reorg']['shifted_acc']:.2f} "
          f"targeted_shifted={vsa['targeted']['shifted_acc']:.2f}", flush=True)

    tier, msg, summ = compute_verdict(points, vsa, N_GENUINE, N_DISTRACTOR)
    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:300], "run_mode": run_mode,
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "mu_g_list": mu_g_list, "K_SWEEP": K_SWEEP, "expected_n_units": expected_n_units,
        "verdict_summary": summ,
        "metric_a_overlap_sweep": points,
        "metric_c_vsa_construction_proof": vsa,
        "prereg": {
            "hard_pass": "separable(OVL<=0.10) reproduces prior (both>=0.90) & robust at moderate overlap "
                         "(usable both>=0.80 for some K at OVL in [0.28,0.45]) & envelope crosses+monotone & "
                         "cost-weighted rides same ROC",
            "hard_fail": "gate breaks at low overlap: NO K gives both>=0.80 already at OVL<=0.15 AND not robust to "
                         "moderate overlap -> trigger-detection fundamentally hard under overlap (structural bound)",
            "middle": "gate holds only up to mild overlap (breaks in (0.15,0.28)); characterize envelope",
            "compute_architecture": "sequential-CPU (store grows fact-by-fact; belief+confirmation state depend on "
                                     "the accumulated stream)",
            "storage_strategy": "sharded (one exact VSA vector per fact) + type-partition index (cached derivative)",
            "final_metrics_atomicity": "tmp_replace", "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "overlap_knob": f"genuine effective run g~N(mu_g,{SIGMA}); distractor peak margin m~N({MU_M},{SIGMA_M}) "
                            f"-> distractor effective run 2m-1 (mean {2*MU_M-1}); sweep mu_g in {MU_G_SWEEP}; "
                            f"measured OVL=sum_l min(p_g,p_d) on EFFECTIVE runs reported per point; revert_strength="
                            f"{REVERT_STRENGTH}",
            "gates": "IRREVERSIBLE hard-K (frozen on commit) | COST-WEIGHTED K* (op-point on same ROC) | REVERSIBLE "
                     "symmetric-K (un-reindex; end-state recovers at thrash+stale cost)",
            "honest_note": "sustain-run is the ONLY online signal at decision time; overlapping length distributions "
                           "-> Neyman-Pearson bound, no gate separates what the signal doesn't. Reversibility (a "
                           "substrate-native affordance the brain's committed cortical consolidation lacks) does NOT "
                           "beat the bound; it converts irrecoverable-error into write-thrash + transient mis-filing "
                           "whose cost grows with overlap. Brain answers ambiguous triggers with fast-reversible "
                           "(hippocampal) + slow-confirmed (cortical, sleep-spaced) two-timescale consolidation.",
            "real_code_path_exercised": ["make_phasors", "encode_meaning", "unbind", "cleanup",
                                         "build_overlap_corpus", "sweep_overlap", "run_detector",
                                         "cost_weighted_k", "vsa_construction_proof"],
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[overlap] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[overlap] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
