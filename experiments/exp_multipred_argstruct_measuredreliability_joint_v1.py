"""THE CLEAN FAIR TEST -- closes the loophole in exp_multipred_argstruct_jointreliability_positional_v1
(HARD_FAIL, but INCONCLUSIVE): that cell fixed POSITIONAL_RELIABILITY at a hand-picked DESIGNED constant
(0.90). This SATURATED the reliability-weighted combiner against S3 (selectional knowledge) -- the tell:
the knowledge-scramble control produced ~0 pick changes (MEASURED@data/exp_multipred_argstruct_
jointreliability_positional_v1/metrics.json:n_diff_scramble), which means knowledge never had a real say,
so the HARD_FAIL verdict ("knowledge is redundant") was not yet trustworthy -- a saturated combiner would
report the SAME verdict regardless of what the knowledge table contained.

THE FIX: every reliability in the joint combine is now MEASURED FROM DATA, not designed/hand-set:
  S1 (structural softmax P(PATIENT) confidence): UNCHANGED from
    exp_multipred_argstruct_earlyjoint_relweighted_v1.structural_patient_source -- reliability = |2q-1|
    where q = P(PATIENT)/(P(PATIENT)+P(best rival role)), MEASURED PER-DECISION from the trained
    AveragedPerceptron's own softmax confidence (already data-derived, already varies per decision --
    explicitly accepted as a valid "MEASURED calibration" form by this task's own spec; not the flaw).
  S2 (positional-first cue, THE FIX): reliability = MEASURED empirical accuracy of "leftmost local-patient
    candidate == gold patient" via LEAVE-ONE-LESSON-OUT cross-validation over the 7 FULL_SLICE lessons --
    for each lesson L, POSITIONAL_RELIABILITY[L] is measured ONLY from the gold-determinable multi-patient
    competition instances in the OTHER 6 lessons (clf.predict()-only hard-label competitions, collected in
    ONE calibration traversal BEFORE any S1/S2/S3 combine happens -- no circularity: the thing being
    measured, "is leftmost right", never consults the combiner or the dedup decision it will later feed).
    L's OWN decisions are scored using a reliability value that never saw L's own gold -- gold-blind on
    the test set, satisfied per-lesson, while still evaluating over the SAME 7-lesson FULL_SLICE this
    reader's other cells (V3/EARLY/JOINTRELIABILITY) all score against (apples-to-apples aggregate F1).
    A GLOBAL fallback (all-lessons leftmost-accuracy) covers any fold with zero gold-determinable
    training competitions (small-sample edge case, only expected at SMOKE_SLICE's 2-lesson LOLO).
  S3 (selectional knowledge): UNCHANGED from exp_multipred_argstruct_earlyjoint_relweighted_v1's OWN
    approach (RELIABILITY_BY_TIER = coverage x evidentiary-specificity per (verb,noun) backoff tier --
    item-exact=0.90, class-avg=0.45, verb-avg=0.20, global=0.03) -- this task's own spec explicitly names
    this "already the EARLY cell's approach", i.e. accepted as-is (already MEASURED per-decision via
    WHICH tier answered the pair, a data-derived signal, not a single global constant).
  ONE shared reliability_weighted_combine (Ernst & Banks 2002, byte-identical reuse) takes the (value,
  reliability, meta) triples; the ONLY code-level change from the prior cell is that S2's reliability
  argument is now looked up per-lesson from a MEASURED dict instead of a single hard-coded float.

ARMS (ONE shared structural traversal per (real-heads) pass produces ARM_BASE / ARM_PLUS_KNOW /
  ARM_PLUS_KNOW_SCRAMBLE together -- by_pred/roles/agents_local/patients_local IDENTICAL inputs to all
  three, "same base" a structural code guarantee):
    ARM_BASE               = {S1, S2-measured}, no knowledge.
    ARM_PLUS_KNOW           = {S1, S2-measured, S3}, real dense table. THE HEADLINE arm.
    ARM_PLUS_KNOW_SCRAMBLE  = {S1, S2-measured, S3}, S3's dense table VALUES permuted (identical scramble
                              convention to E.make_scrambled_table: sorted keys, seeded rng.permutation).
                              MUST-FAIL CONTROL (content) -- THE loophole-closer this cell exists to fire.
    ARM_PLUS_KNOW_ARCSCRAMBLE = {S1, S2-measured, S3}, real table, M.scramble_heads-scrambled decoded arcs
                              (separate traversal -- heads differ, by_pred differs). MUST-FAIL CONTROL
                              (structure).

HARD PRECONDITIONS (checked BEFORE interpreting the headline comparison; both must hold or the run is
  reported INCONCLUSIVE, per this task's own explicit instruction -- no ex-post redundancy claim without
  them):
  P1 (base_reproduces_v3): |F1(ARM_BASE) - F1(V3_INTEGRATED, same-run)| <= 0.06. If False ->
    MIDDLE_BAND_BASE_MISMATCH regardless of the arms below.
  P2 (scramble_control_fires): n_diff_tuples(ARM_PLUS_KNOW, ARM_PLUS_KNOW_SCRAMBLE) >= 3. If P1 holds but
    P2 does NOT -> verdict = INCONCLUSIVE_COMBINER_SATURATED (do NOT bank a redundancy bound -- the
    combiner is still saturated against S3 even with a MEASURED S2 reliability; report honestly, do not
    claim HARD_FAIL).

PRE-REGISTERED BANDS (set BEFORE running; valid ONLY if P1 AND P2 both hold):
  HARD_PASS_JOINT_KNOWLEDGE_HELPS_ON_STRONG_BASE, ALL of:
    (a) F1(ARM_PLUS_KNOW) > F1(ARM_BASE) + 0.015
    (b) F1(ARM_PLUS_KNOW_SCRAMBLE) <= F1(ARM_PLUS_KNOW) - 0.02
    (c) F1(ARM_PLUS_KNOW_ARCSCRAMBLE) <= F1(ARM_PLUS_KNOW) - 0.05
  HARD_FAIL_KNOWLEDGE_STILL_REDUNDANT_ON_STRONG_BASE (P2 already guarantees knowledge has a genuine say):
    F1(ARM_PLUS_KNOW) <= F1(ARM_BASE)
  MIDDLE_BAND_PARTIAL: P1+P2 hold, neither HARD_PASS nor HARD_FAIL condition set is fully met (e.g. beats
    base but a control margin is short) -- report which condition failed.
  ALSO REPORTED regardless of verdict (this task's own most-direct test, sidesteps combiner-weighting
  entirely): on the subset of gold-determinable competitions where ARM_BASE's pick != gold ("structure
  wrong"), what fraction does ARM_PLUS_KNOW pick correctly ("does knowledge rescue where structure
  fails?"). ALSO REPORTED: a sensitivity sweep of the MEASURED S2 reliability over scale factors
  {0.7, 1.0, 1.3} (clipped to (0.01, 0.99)) -- is the knowledge-helps/hurts verdict stable or knife-edge
  under a +/-30% perturbation of the measured positional-reliability estimate?

FAIRNESS: SAME reader/gold/split/parser-training-budget/clf/gate/dense-table as
  V3/EARLYJOINT/JOINTRELIABILITY (FULL_SLICE = L04/L05/L07/L08/L09/L10/L12; SMOKE_SLICE = L04/L05); gold =
  data/gold_mcguffey_lccp_argstruct_v1.json (independent, single-annotator; read only for scoring AND for
  the LOLO reliability measurement -- the LOLO fold structure is what keeps this gold-blind per lesson at
  scoring time, exactly analogous to a train/test split, not a leak). ONE variable vs the prior
  (jointreliability_positional_v1) cell = S2's reliability is now MEASURED (LOLO) instead of a DESIGNED
  constant; everything else (parser training / candidate-to-predicate assignment / role-decision-that-
  fixes-candidate-membership / learned admissibility gate / S1's own formula / S3's own formula / dense
  table contents / scoring pipeline) is byte-identical reuse or held fixed.

BRAIN-CHECK: Ernst & Banks (2002) optimal cue combination assumes cue reliabilities are themselves LEARNED
  from experience (e.g. visual-haptic recalibration studies show the brain updates its estimate of each
  modality's reliability from feedback/statistics, it does not use a fixed a-priori weight). Hand-setting
  POSITIONAL_RELIABILITY=0.90 was the least brain-faithful part of the prior cell's design -- an organism's
  confidence in a structural/word-order cue is itself tuned by how often that cue has been right, i.e.
  exactly the LOLO measurement this cell performs. MacDonald, Pearlmutter & Seidenberg (1994) constraint-
  based lexicalist account is otherwise unchanged from the prior two cells' brain-check.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- reuses V3/EARLYJOINT's arc-eager
  parser training (~50-65s MEASURED@prior cells) + per-clause greedy decode + AveragedPerceptron scoring
  (byte-identical reuse) + O(candidates) dict lookups + one softmax + one reliability-combine per
  candidate (O(1) each) + a cheap LOLO aggregation over cached (sid, vlemma, cand_heads) competition
  records (O(n_competitions) dict lookups, no re-parse). NO matmul/storage/GPU-batchable primitive.
  Storage: no_storage. Runtime invariant: glass-box (from-scratch-trained transition parser + curated
  dicts + a build-time-authored dense knowledge dict + a fully inspectable reliability-weighted combiner,
  all LOCAL), NO LLM/network/autograd at inference. Determinism: OMP/MKL/OPENBLAS=1, fixed int SEED, numpy
  default_rng, sorted(keys); no hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion. NO push / NO
  remote-persist / NO queue_add (routing task contract: inline-local FULL, pause-state ACTIVE, not banked
  -- skunkworks VETs separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell; N/A items stated
  explicitly per META_RULE_AC):
  - arms_differ_verified at smoke gate (hash test; ARM_PLUS_KNOW vs ARM_PLUS_KNOW_ARCSCRAMBLE MUST differ
    HARD; ARM_BASE vs ARM_PLUS_KNOW and ARM_PLUS_KNOW vs ARM_PLUS_KNOW_SCRAMBLE exempted at SMOKE scale
    ONLY, small-sample rationale established by the prior 2 cells for their own analogous pairs)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(ARM_BASE) < 0.95)
  - discriminator fires at smoke: n_competitions >= 1 at SMOKE_SLICE (multi-patient competition instances
    exist, so the S1/S2/S3 combine engages at all)
  - calibration_check: "adaptive_with_discriminator_gate" -- S2's reliability is now DATA-ADAPTIVE (LOLO
    measured, not a fixed default); the discriminator-still-fires verification is P2 itself (the
    scramble-control-fires precondition), logged in metrics as n_diff_scramble + the
    INCONCLUSIVE_COMBINER_SATURATED escape hatch if it does not fire -- this IS the adaptive-calibration
    discipline's own required "discriminator still fires" check, applied to the reliability estimate
    itself rather than to a downstream cosine threshold.
  - scaffold-free witnesses (TWO, reused structure from the prior cell, now parameterized by the MEASURED
    global positional reliability rather than a hardcoded constant): (1) confident structure + leftmost
    positional AGREEING vs a sparse/backstop-tier knowledge rating disagreeing -- combine stays close to
    the S1+S2 value; (2) a DENSE tier0_item knowledge rating disagreeing with an uncertain/toss-up
    structure AND a non-leftmost position -- combine can still flip toward knowledge.
  - deterministic seeding (fixed int SEED; sorted(dict.keys()) for scramble permutations and LOLO fold
    iteration; numpy default_rng; no hash()-seeded RNG)
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (V3/EARLYJOINT/JOINTRELIABILITY metrics.json) /
    THEORETICAL@ (Ernst-Banks combination formula) / DESIGNED (RELIABILITY_BY_TIER -- S3's gold-blind
    prior, unchanged, this task's spec explicitly accepts it as-is) in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/precision measurement, no HD noise floor); N/A
    multi-seed for the arms (deterministic given fixed SEED; parser training is single-seed by design,
    accepted upstream); N/A cardinality-sweep (no swept parameter axis besides the fixed arm comparison +
    the LOLO fold loop, which is a calibration procedure not a pre-registered sweep axis); N/A heartbeat
    (foreground <10min inline-local measurement cell, no remote-runner zombie risk, same precedent as the
    2 prior cells this one extends)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "multipred_argstruct_measuredreliability_joint_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Reuse V3 / EARLYJOINT / JOINTRELIABILITY / M / L / ORC / V2 / D's OWN code VERBATIM.
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3               # noqa: E402
from experiments import exp_multipred_argstruct_earlyjoint_relweighted_v1 as E          # noqa: E402
from experiments import exp_multipred_argstruct_denseitem_v1 as D                      # noqa: E402
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M                # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L     # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC                 # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2          # noqa: E402

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260728

# ---- Pre-registered bands (set BEFORE this run; see docstring) ------------------------
HP_KNOW_OVER_BASE_MIN = 0.015
HP_SCRAMBLE_MARGIN = 0.02
HP_ARCSCRAMBLE_MARGIN = 0.05
BASE_REPRO_TOLERANCE = 0.06
P2_MIN_SCRAMBLE_FLIPS = 3   # THE loophole-closer: knowledge must demonstrably have a say (>=3 of ~76 flips)
CITED_V3_INTEGRATED_F1 = 0.5738    # CITED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1
CITED_JOINTREL_ARM_BASE_F1 = None  # filled from disk if available (context only, not gating)
BASELINE_BAND = (0.05, 0.95)
SENSITIVITY_SCALES = [0.7, 1.0, 1.3]


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# S2: positional-first constraint source. Value=1.0 for the leftmost local patient candidate, 0.0
# otherwise; reliability is now an ARGUMENT (MEASURED per-lesson via leave-one-lesson-out, see below) --
# the ONLY code-level change vs exp_multipred_argstruct_jointreliability_positional_v1's fixed constant.
# =======================================================================================
def positional_patient_source(i, patients_local, reliability):
    is_leftmost = (i == min(patients_local))
    return (1.0 if is_leftmost else 0.0), reliability, dict(is_leftmost=is_leftmost)


# =======================================================================================
# Calibration pass: ONE traversal, structural-only (clf.predict() hard labels, NO S1/S2/S3 combine
# anywhere in this function) -- builds (a) evidence for the learned admissibility gate (byte-identical
# logic to the prior cells' own "keepall" pass) and (b) the raw multi-patient competition list used to
# MEASURE S2's reliability. Because this pass never touches reliability_weighted_combine, the
# measurement cannot be circular with the thing it will later feed.
# =======================================================================================
def clause_pass_calibration(tagged, heads, clf, carried_agent_in, assign_fn, sid, lesson,
                             competition_log, evidence):
    lows = [t[1] for t in tagged]
    verb_positions = M.content_verb_indices(tagged)
    by_pred = assign_fn(tagged, heads, verb_positions)
    carried_agent = carried_agent_in
    for v0 in verb_positions:
        v1 = v0 + 1
        low = tagged[v0][1]
        passive = M._detect_passive(tagged, v0, lows)
        local_cand = sorted(by_pred.get(v1, []))
        first_cand = local_cand[0] if local_cand else None
        vl = L.lemma_verb(low)
        roles = {}
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
            roles[i] = clf.predict(feats)
        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        for i in local_cand:
            if i > v0 and ORC.prev_prep(tagged, i) is None:
                evidence[vl] = True
        if len(patients_local) >= 2:
            competition_log.append(dict(sid=sid, lesson=lesson, vlemma=vl,
                                         cand_heads=[tagged[i][1] for i in patients_local]))
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]
    return carried_agent


def build_calibration_pass(slice_lessons, W, clf, assign_fn):
    order, sent_text, _reader_svo = L.load_slice_and_reader(slice_lessons)
    evidence = {}
    competition_log = []
    for sid in order:
        lesson = sid.split("_")[0]
        raw = sent_text[sid]
        carried_agent = None
        for clause_i, clause_text in enumerate(ORC.split_sentences(raw)):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            carried_agent = clause_pass_calibration(tagged, heads, clf, carried_agent, assign_fn,
                                                      sid, lesson, competition_log, evidence)
    return order, sent_text, evidence, competition_log


def measure_positional_reliability_loo(competition_log, gold):
    """Leave-one-LESSON-out: POSITIONAL_RELIABILITY[lesson] = leftmost-accuracy MEASURED ONLY over
    gold-determinable competitions from lessons != lesson (never touches that lesson's own gold at
    scoring time -- the gold-blind-per-fold discipline). "__global__" fallback (all-lessons-together
    leftmost-accuracy) is used only if a fold's OWN training set has zero gold-determinable competitions
    (small-sample edge case; expected only at SMOKE_SLICE's 2-lesson LOLO)."""
    lessons = sorted(set(c["lesson"] for c in competition_log))

    def _acc(comps):
        n_det = 0
        n_correct = 0
        for c in comps:
            gp = D.gold_patient_lookup(gold, c["sid"], c["vlemma"])
            if gp is None:
                continue
            n_det += 1
            if c["cand_heads"][0] in gp:
                n_correct += 1
        return n_correct, n_det

    n_correct_all, n_det_all = _acc(competition_log)
    global_rel = (n_correct_all / n_det_all) if n_det_all > 0 else 0.5

    per_lesson = {}
    per_lesson_detail = {}
    for lesson in lessons:
        train_comps = [c for c in competition_log if c["lesson"] != lesson]
        n_c, n_d = _acc(train_comps)
        if n_d == 0:
            per_lesson[lesson] = global_rel
            per_lesson_detail[lesson] = dict(n_correct=n_c, n_det=n_d, source="FALLBACK_GLOBAL_zero_train_determinable")
        else:
            per_lesson[lesson] = round(n_c / n_d, 4)
            per_lesson_detail[lesson] = dict(n_correct=n_c, n_det=n_d, source="LOLO_measured")
    per_lesson["__global__"] = round(global_rel, 4)
    return per_lesson, per_lesson_detail, n_correct_all, n_det_all


# =======================================================================================
# ONE shared structural traversal producing MULTIPLE arm outputs (S1+S2-measured always present; S3
# present iff sel_fn is not None for that arm-name's entry). analysis_log caches per-competition raw
# picks (ARM_BASE vs ARM_PLUS_KNOW) for the post-hoc "does knowledge rescue where structure fails" test.
# =======================================================================================
def clause_predicate_pass_joint(tagged, heads, clf, gate_fn, carried_agent_in, assign_fn,
                                 arm_sel_fns, sid, lesson, pos_rel_by_lesson,
                                 base_fp_log=None, n_competitions_counter=None, analysis_log=None):
    lows = [t[1] for t in tagged]
    verb_positions = M.content_verb_indices(tagged)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    by_pred = assign_fn(tagged, heads, verb_positions)
    outs = {name: [] for name in arm_sel_fns}
    carried_agent = carried_agent_in
    pos_reliability = pos_rel_by_lesson.get(lesson, pos_rel_by_lesson.get("__global__", 0.5))
    for v0 in verb_positions:
        v1 = v0 + 1
        low = tagged[v0][1]
        passive = M._detect_passive(tagged, v0, lows)
        local_cand = sorted(by_pred.get(v1, []))
        first_cand = local_cand[0] if local_cand else None
        vl = L.lemma_verb(low)
        roles = {}
        feats_cache = {}
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
            feats_cache[i] = feats
            roles[i] = clf.predict(feats)
        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent
        if base_fp_log is not None:
            base_fp_log.append((v0, tuple(sorted(agents_local)), tuple(sorted(patients_local))))
        if len(patients_local) >= 2 and n_competitions_counter is not None:
            n_competitions_counter[0] += 1
        s1s2 = {}
        s3_real = {}
        know_fn_real = arm_sel_fns.get("ARM_PLUS_KNOW")
        for i in patients_local:
            p_patient, rel_struct, meta_struct = E.structural_patient_source(clf, feats_cache[i])
            val_pos, rel_pos, meta_pos = positional_patient_source(i, patients_local, pos_reliability)
            s1s2[i] = [(p_patient, rel_struct, meta_struct), (val_pos, rel_pos, meta_pos)]
            if know_fn_real is not None:
                know_val, rel_know, meta_know = E.selectional_patient_source(know_fn_real, vl, tagged[i][1])
                s3_real[i] = (know_val, rel_know, meta_know)
        gate_pass = gate_fn(vl)
        is_main = (v0 == main_idx)
        kind = M.predicate_kind(tagged, v0, is_main) if gate_pass else None
        picks_this_clause = {}
        for name, sel_fn in arm_sel_fns.items():
            kept_patients = patients_local
            if len(patients_local) >= 2:
                def _combined(i, sel_fn=sel_fn):
                    sources = list(s1s2[i])
                    if sel_fn is not None:
                        know_val, rel_know, meta_know = E.selectional_patient_source(sel_fn, vl, tagged[i][1])
                        sources.append((know_val, rel_know, meta_know))
                    combined, _bd = E.reliability_weighted_combine(sources)
                    return combined
                best_i = max(patients_local, key=lambda i: (_combined(i), -i))
                kept_patients = [best_i]
                picks_this_clause[name] = tagged[best_i][1]
            if resolved_agent is not None and kept_patients and low not in ("has", "is") and gate_pass:
                for pi in kept_patients:
                    outs[name].append((low, resolved_agent, tagged[pi][1], v0, kind))
        if len(patients_local) >= 2 and analysis_log is not None:
            analysis_log.append(dict(
                sid=sid, vlemma=vl, lesson=lesson, cand_heads=[tagged[i][1] for i in patients_local],
                pos_reliability_used=round(pos_reliability, 4),
                pick_base=picks_this_clause.get("ARM_BASE"),
                pick_plusknow=picks_this_clause.get("ARM_PLUS_KNOW"),
            ))
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]
    return outs, carried_agent


def build_parse_arm_joint(slice_lessons, W, clf, gate_fn, assign_fn, arm_sel_fns, pos_rel_by_lesson,
                           scramble_arcs=False, scramble_seed=None, collect_base_fp=False,
                           analysis_log=None):
    order, sent_text, _reader_svo = L.load_slice_and_reader(slice_lessons)
    outs = {name: {} for name in arm_sel_fns}
    base_fp = [] if collect_base_fp else None
    n_competitions = [0]
    for sid in order:
        lesson = sid.split("_")[0]
        raw = sent_text[sid]
        carried_agent = None
        for clause_i, clause_text in enumerate(ORC.split_sentences(raw)):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            if scramble_arcs:
                heads = M.scramble_heads(heads, (scramble_seed or SEED) + M.hash_stable(sid) + clause_i)
            clause_fp = [] if collect_base_fp else None
            clause_outs, carried_agent = clause_predicate_pass_joint(
                tagged, heads, clf, gate_fn, carried_agent, assign_fn, arm_sel_fns, sid, lesson,
                pos_rel_by_lesson, base_fp_log=clause_fp, n_competitions_counter=n_competitions,
                analysis_log=analysis_log)
            if collect_base_fp:
                for entry in clause_fp:
                    base_fp.append((sid,) + entry)
            for name in arm_sel_fns:
                outs[name].setdefault(sid, []).extend([(t[0], t[1], t[2]) for t in clause_outs[name]])
    return order, sent_text, outs, base_fp, n_competitions[0]


def kept_tuple_set(kept_dict):
    s = set()
    for sid, tups in kept_dict.items():
        for (v, a, p) in tups:
            s.add((sid, v, a, p))
    return s


def n_diff_tuples(kept_a, kept_b):
    return len(kept_tuple_set(kept_a) ^ kept_tuple_set(kept_b))


def base_fp_hash(base_fp):
    b = json.dumps(base_fp, sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()[:16]


# =======================================================================================
# Direct test (sidesteps combiner-weighting entirely): on the subset of gold-determinable competitions
# where ARM_BASE's pick != gold ("structure wrong"), does ARM_PLUS_KNOW's pick match gold?
# =======================================================================================
def structure_wrong_rescue_analysis(analysis_log, gold):
    n_subset = 0
    n_base_correct_subset = 0  # must be 0 by construction; a non-zero value is an instrumentation bug
    n_plusknow_correct_subset = 0
    examples = []
    for c in analysis_log:
        gp = D.gold_patient_lookup(gold, c["sid"], c["vlemma"])
        if gp is None:
            continue
        base_pick = c["pick_base"]
        know_pick = c["pick_plusknow"]
        if base_pick is None:
            continue
        if base_pick in gp:
            continue  # not in the "structure wrong" subset
        n_subset += 1
        if base_pick in gp:
            n_base_correct_subset += 1
        if know_pick is not None and know_pick in gp:
            n_plusknow_correct_subset += 1
            if len(examples) < 10:
                examples.append(dict(sid=c["sid"], vlemma=c["vlemma"], base_pick=base_pick,
                                      know_pick=know_pick, gold=sorted(gp)))
    rescue_rate = round(n_plusknow_correct_subset / n_subset, 4) if n_subset > 0 else None
    return dict(n_subset=n_subset, n_base_correct_subset=n_base_correct_subset,
                n_plusknow_correct_subset=n_plusknow_correct_subset, rescue_rate=rescue_rate,
                examples=examples)


# =======================================================================================
# Sensitivity sweep: does the knowledge-helps/hurts verdict survive a +/-30% perturbation of the
# MEASURED S2 reliability? Cheap -- re-runs ONLY the arm-scoring traversal (no re-training) per scale.
# =======================================================================================
def sensitivity_sweep(slice_lessons, W, clf, learned_gate_fixed, assign_fn, sel_with_tier_real,
                       pos_rel_by_lesson, gold, scales):
    results = {}
    for scale in scales:
        scaled = {lesson: (round(min(0.99, max(0.01, rel * scale)), 4) if lesson != "__global__" else rel)
                  for lesson, rel in pos_rel_by_lesson.items()}
        arm_sel_fns = {"ARM_BASE": None, "ARM_PLUS_KNOW": sel_with_tier_real}
        _o, _s, kept, _fp, _nc = build_parse_arm_joint(
            slice_lessons, W, clf, learned_gate_fixed, assign_fn, arm_sel_fns, scaled)
        f1_base = L.score_arm(M.to_kept_list(kept["ARM_BASE"]), gold)["f1"]
        f1_plusknow = L.score_arm(M.to_kept_list(kept["ARM_PLUS_KNOW"]), gold)["f1"]
        results[str(scale)] = dict(scale=scale, f1_base=round(f1_base, 4), f1_plusknow=round(f1_plusknow, 4),
                                    delta=round(f1_plusknow - f1_base, 4),
                                    knowledge_helps=bool(f1_plusknow > f1_base + HP_KNOW_OVER_BASE_MIN))
    return results


# =======================================================================================
# Run all arms.
# =======================================================================================
def run_all_arms(slice_lessons, W, clf):
    dense_table = D.load_dense_table()
    scrambled_table = E.make_scrambled_table(dense_table, SEED + 13)
    sel_with_tier_real = E.build_dense_sel_with_tier(dense_table)
    sel_with_tier_scrambled = E.build_dense_sel_with_tier(scrambled_table)
    assign_fn = V3.assign_candidates_to_predicates_fixed

    # Calibration pass: ONE traversal, structural-only (no combine), builds evidence for the learned gate
    # AND the raw competition list used to MEASURE S2's reliability.
    _order0, _sent0, evidence, competition_log = build_calibration_pass(slice_lessons, W, clf, assign_fn)
    learned_gate_fixed = M.build_learned_admissibility(evidence)

    gold, _gold_meta = L.load_gold(slice_lessons)
    pos_rel_by_lesson, pos_rel_detail, n_correct_all, n_det_all = measure_positional_reliability_loo(
        competition_log, gold)

    # Pass 2: SAME-heads traversal produces ARM_BASE / ARM_PLUS_KNOW / ARM_PLUS_KNOW_SCRAMBLE together.
    arm_sel_fns = {"ARM_BASE": None, "ARM_PLUS_KNOW": sel_with_tier_real,
                   "ARM_PLUS_KNOW_SCRAMBLE": sel_with_tier_scrambled}
    analysis_log = []
    order, sent_text, same_base_outs, base_fp, n_competitions = build_parse_arm_joint(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn, arm_sel_fns, pos_rel_by_lesson,
        collect_base_fp=True, analysis_log=analysis_log)

    # Pass 3: ARM_PLUS_KNOW_ARCSCRAMBLE -- separate traversal, scrambled heads (base MUST differ here).
    _, _, arcscr_outs, _fp3, _ncomp3 = build_parse_arm_joint(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn,
        {"ARM_PLUS_KNOW_ARCSCRAMBLE": sel_with_tier_real}, pos_rel_by_lesson,
        scramble_arcs=True, scramble_seed=SEED + 7)

    all_kept = dict(same_base_outs)
    all_kept.update(arcscr_outs)

    scored = {}
    for name, kept in all_kept.items():
        rc, miss, npos, _m = M.recall_ceiling_of(kept, gold)
        sc = L.score_arm(M.to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, n_miss=miss, n_gold_pos=npos, score=sc,
                             kept_hash=M.arm_hash(kept), n_pred=sc["n_pred"])

    n_diff_scramble = n_diff_tuples(all_kept["ARM_PLUS_KNOW"], all_kept["ARM_PLUS_KNOW_SCRAMBLE"])
    n_diff_arcscramble = n_diff_tuples(all_kept["ARM_PLUS_KNOW"], all_kept["ARM_PLUS_KNOW_ARCSCRAMBLE"])
    n_diff_know_vs_base = n_diff_tuples(all_kept["ARM_PLUS_KNOW"], all_kept["ARM_BASE"])

    rescue = structure_wrong_rescue_analysis(analysis_log, gold)
    sensitivity = sensitivity_sweep(slice_lessons, W, clf, learned_gate_fixed, assign_fn,
                                     sel_with_tier_real, pos_rel_by_lesson, gold, SENSITIVITY_SCALES)

    return dict(order=order, sent_text=sent_text, gold=gold, arms=all_kept, scored=scored,
                base_fp_hash=base_fp_hash(base_fp), n_competitions=n_competitions,
                n_diff_scramble=n_diff_scramble, n_diff_arcscramble=n_diff_arcscramble,
                n_diff_know_vs_base=n_diff_know_vs_base, evidence=evidence,
                pos_rel_by_lesson=pos_rel_by_lesson, pos_rel_detail=pos_rel_detail,
                n_correct_all=n_correct_all, n_det_all=n_det_all,
                rescue=rescue, sensitivity=sensitivity)


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


# =======================================================================================
# Self-test (design-gate; smoke scale = SMOKE_SLICE).
# =======================================================================================
def self_test():
    print("[self-test] loading SMOKE_SLICE reader + gold + dense table ...")
    order, sent_text, reader_svo = L.load_slice_and_reader(SMOKE_SLICE)
    assert len(order) >= 20, f"expected >=20 sentences in SMOKE_SLICE, got {len(order)}"
    clf = V2._fit_clf()
    dense_table = D.load_dense_table()
    assert len(dense_table) > 100, f"dense table suspiciously small: {len(dense_table)}"

    print("[self-test] training arc-eager parser (smoke budget, reused code) ...")
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"
    print(f"[self-test] parser trained: {parser_info}")

    res = run_all_arms(SMOKE_SLICE, W, clf)
    for name in ("ARM_BASE", "ARM_PLUS_KNOW", "ARM_PLUS_KNOW_SCRAMBLE", "ARM_PLUS_KNOW_ARCSCRAMBLE"):
        assert name in res["scored"], f"arm {name} missing from smoke run"
    print(f"[self-test] arms ran on SMOKE_SLICE F1: "
          f"{ {k: v['score']['f1'] for k, v in res['scored'].items()} }")
    print(f"[self-test] n_competitions (multi-patient instances) at SMOKE_SLICE: {res['n_competitions']}")
    assert res["n_competitions"] >= 1, \
        "DISCRIMINATOR DOES NOT FIRE: zero multi-patient competition instances at SMOKE_SLICE scale"

    print(f"[self-test] MEASURED positional reliability (LOLO, SMOKE_SLICE 2-lesson fold): "
          f"{res['pos_rel_by_lesson']} detail={res['pos_rel_detail']} "
          f"(global leftmost-accuracy n_correct={res['n_correct_all']}/n_det={res['n_det_all']})")

    prec_base = res["scored"]["ARM_BASE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], \
        f"ARM_BASE precision {prec_base} outside band {BASELINE_BAND}"
    print(f"[self-test] baseline_in_band: precision(ARM_BASE)={prec_base} in {BASELINE_BAND}")

    # Base-reproduction calibration check (against V3_INTEGRATED on the SAME smoke-trained W/clf/slice).
    sparse_table = V3.load_knowledge_table()
    res_v3 = V3.run_all_arms_v3(SMOKE_SLICE, W, clf, sparse_table)
    f1_v3_integrated_smoke = res_v3["scored"]["V3_INTEGRATED"]["score"]["f1"]
    f1_arm_base_smoke = res["scored"]["ARM_BASE"]["score"]["f1"]
    gap = abs(f1_arm_base_smoke - f1_v3_integrated_smoke)
    print(f"[self-test] P1 base-reproduction check (SMOKE_SLICE): F1(ARM_BASE)={f1_arm_base_smoke} vs "
          f"F1(V3_INTEGRATED)={f1_v3_integrated_smoke} gap={gap}")
    if gap > BASE_REPRO_TOLERANCE:
        print(f"[self-test] WARN: P1 gap {gap} exceeds tolerance {BASE_REPRO_TOLERANCE} at SMOKE_SLICE "
              f"(small-sample, 2-lesson LOLO; the FULL run's own P1 gap is the load-bearing check)")
    else:
        print(f"[self-test] P1 OK at SMOKE_SLICE scale (gap {gap} <= {BASE_REPRO_TOLERANCE})")

    print(f"[self-test] P2 scramble-fires check (SMOKE_SLICE): n_diff_scramble={res['n_diff_scramble']} "
          f"(need >= {P2_MIN_SCRAMBLE_FLIPS} at FULL; small-sample WARN-only here)")
    if res["n_diff_scramble"] < P2_MIN_SCRAMBLE_FLIPS:
        print("[self-test] WARN: P2 does not fire at SMOKE_SLICE scale (small-sample; the FULL run's own "
              "P2 check is the load-bearing precondition, not this smoke count)")

    print(f"[self-test] rescue analysis (SMOKE_SLICE): {res['rescue']}")
    print(f"[self-test] sensitivity sweep (SMOKE_SLICE): {res['sensitivity']}")

    # arms_differ_verified (META_RULE_AF). Only the true structural control (arc-scramble) is HARD-asserted.
    hashes = {name: v["kept_hash"] for name, v in res["scored"].items()}
    assert hashes["ARM_PLUS_KNOW"] != hashes["ARM_PLUS_KNOW_ARCSCRAMBLE"], \
        f"META_RULE_AF VIOLATION: ARM_PLUS_KNOW and ARM_PLUS_KNOW_ARCSCRAMBLE bit-identical: {hashes}"
    arms_differ_exempted = [("ARM_BASE", "ARM_PLUS_KNOW"), ("ARM_PLUS_KNOW", "ARM_PLUS_KNOW_SCRAMBLE")]
    if hashes["ARM_BASE"] == hashes["ARM_PLUS_KNOW"]:
        print("[self-test] WARN: ARM_BASE == ARM_PLUS_KNOW kept_hash at SMOKE_SLICE (small-sample; "
              "declared arms_differ_exempted)")
    if hashes["ARM_PLUS_KNOW"] == hashes["ARM_PLUS_KNOW_SCRAMBLE"]:
        print("[self-test] WARN: ARM_PLUS_KNOW == ARM_PLUS_KNOW_SCRAMBLE kept_hash at SMOKE_SLICE "
              "(small-sample; declared arms_differ_exempted)")
    print(f"[self-test] arms_differ_verified (arc-scramble vs real, HARD): "
          f"ARM_PLUS_KNOW={hashes['ARM_PLUS_KNOW']} ARM_PLUS_KNOW_ARCSCRAMBLE="
          f"{hashes['ARM_PLUS_KNOW_ARCSCRAMBLE']}; exempted (small-sample WARN-only): {arms_differ_exempted}")

    global_pos_rel = res["pos_rel_by_lesson"]["__global__"]

    # scaffold-free witness (1): confident structure + leftmost positional AGREEING vs a sparse/backstop
    # knowledge rating disagreeing -- combine stays close to S1+S2 (parameterized by the MEASURED global
    # positional reliability rather than a hardcoded constant).
    sources_agree = [(0.90, 0.95, {}), (1.0, global_pos_rel, {})]
    combined_no_know, _ = E.reliability_weighted_combine(sources_agree)
    sources_with_sparse_disagree = sources_agree + [(0.10, E.RELIABILITY_BY_TIER["tier3_global"], {})]
    combined_with_sparse, _ = E.reliability_weighted_combine(sources_with_sparse_disagree)
    print(f"[self-test] witness1 (S1+S2 confident+leftmost agree [pos_rel={global_pos_rel}], S3 sparse "
          f"disagrees): combine(S1+S2)={combined_no_know:.4f} combine(S1+S2+sparse_S3)={combined_with_sparse:.4f}")
    assert abs(combined_with_sparse - combined_no_know) < 0.05, \
        (f"WITNESS FAIL: a sparse/backstop-tier knowledge rating moved the combine by >=0.05 despite a "
         f"confident, positionally-agreeing S1+S2 base -- reliability-weighting is not suppressing the "
         f"unreliable cue as designed")
    print("[self-test] scaffold-free witness 1 PASS: sparse/backstop knowledge does not override a "
          "confident, positionally-agreeing structural base")

    # scaffold-free witness (2): a DENSE tier0_item knowledge rating disagreeing with an uncertain/toss-up
    # structure AND a non-leftmost position -- combine can still flip toward knowledge.
    sources_weak_wrong = [(0.50, 0.0, {}), (0.0, global_pos_rel, {})]  # toss-up structure, non-leftmost
    combined_weak_only, _ = E.reliability_weighted_combine(sources_weak_wrong)
    sources_weak_plus_dense = sources_weak_wrong + [(0.95, 0.90, {})]  # tier0_item, high value+reliability
    combined_weak_plus_dense, _ = E.reliability_weighted_combine(sources_weak_plus_dense)
    print(f"[self-test] witness2 (S1 toss-up + S2 non-leftmost [pos_rel={global_pos_rel}], S3 dense/high "
          f"disagrees): combine(S1+S2 only)={combined_weak_only:.4f} combine(+dense_S3)={combined_weak_plus_dense:.4f}")
    assert combined_weak_plus_dense > combined_weak_only + 0.10, \
        (f"WITNESS FAIL: a dense tier0_item knowledge rating did not measurably raise the combine when "
         f"S1 is a toss-up and S2 opposes (non-leftmost) -- S3 is not live")
    print("[self-test] scaffold-free witness 2 PASS: dense/high-reliability knowledge is live and can "
          "move the combine when structure+position are weak/opposed")

    # determinism: two identical runs produce identical kept-tuple hashes AND identical LOLO reliability.
    res2 = run_all_arms(SMOKE_SLICE, W, clf)
    assert res["scored"]["ARM_PLUS_KNOW"]["kept_hash"] == res2["scored"]["ARM_PLUS_KNOW"]["kept_hash"], \
        "non-deterministic ARM_PLUS_KNOW output across identical runs"
    assert res["pos_rel_by_lesson"] == res2["pos_rel_by_lesson"], \
        "non-deterministic LOLO positional-reliability measurement across identical runs"
    print("[self-test] deterministic (two runs produce identical kept-tuple hash AND identical LOLO reliability)")

    print(f"[self-test] base_fp_hash={res['base_fp_hash']}")
    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    _write_start_marker(output_dir, run_mode, expected_n_units=len(slice_lessons))
    clf = V2._fit_clf()
    W, parser_info = M.train_dep_parser(run_mode)
    res = run_all_arms(slice_lessons, W, clf)
    scored = res["scored"]

    # Same-run V3_INTEGRATED reference (fresh W/clf, true same-run fairness).
    sparse_table = V3.load_knowledge_table()
    res_v3 = V3.run_all_arms_v3(slice_lessons, W, clf, sparse_table)
    f1_v3_integrated_same_run = res_v3["scored"]["V3_INTEGRATED"]["score"]["f1"]

    f1_base = scored["ARM_BASE"]["score"]["f1"]
    f1_plusknow = scored["ARM_PLUS_KNOW"]["score"]["f1"]
    f1_scramble = scored["ARM_PLUS_KNOW_SCRAMBLE"]["score"]["f1"]
    f1_arcscramble = scored["ARM_PLUS_KNOW_ARCSCRAMBLE"]["score"]["f1"]

    base_gap = round(abs(f1_base - f1_v3_integrated_same_run), 4)
    base_reproduces_v3 = base_gap <= BASE_REPRO_TOLERANCE   # P1

    n_diff_scramble = res["n_diff_scramble"]
    n_diff_arcscramble = res["n_diff_arcscramble"]
    n_diff_know_vs_base = res["n_diff_know_vs_base"]
    scramble_fires = n_diff_scramble >= P2_MIN_SCRAMBLE_FLIPS   # P2

    hard_pass_conditions = dict(
        knowledge_beats_base=(f1_plusknow > f1_base + HP_KNOW_OVER_BASE_MIN),
        control_scramble=(f1_scramble <= f1_plusknow - HP_SCRAMBLE_MARGIN),
        control_arcscramble=(f1_arcscramble <= f1_plusknow - HP_ARCSCRAMBLE_MARGIN),
    )

    sensitivity = res["sensitivity"]
    sensitivity_helps_flags = [v["knowledge_helps"] for v in sensitivity.values()]
    sensitivity_stable = len(set(sensitivity_helps_flags)) == 1

    if not base_reproduces_v3:
        verdict = "MIDDLE_BAND_BASE_MISMATCH"
        vmsg = (f"MIDDLE_BAND_BASE_MISMATCH (P1 FAILED): F1(ARM_BASE)={f1_base} vs F1(V3_INTEGRATED "
                f"same-run)={f1_v3_integrated_same_run} (CITED cross-run={CITED_V3_INTEGRATED_F1}); "
                f"gap={base_gap} exceeds tolerance {BASE_REPRO_TOLERANCE}. The MEASURED (LOLO) positional "
                f"reliability did not reproduce V3's actual strength on this run -- the ARM_PLUS_KNOW-vs-"
                f"ARM_BASE comparison is not yet apples-to-apples. For reference (NOT the gated verdict): "
                f"F1(ARM_PLUS_KNOW)={f1_plusknow} F1(ARM_PLUS_KNOW_SCRAMBLE)={f1_scramble} "
                f"F1(ARM_PLUS_KNOW_ARCSCRAMBLE)={f1_arcscramble} n_diff_scramble={n_diff_scramble}.")
    elif not scramble_fires:
        verdict = "INCONCLUSIVE_COMBINER_SATURATED"
        vmsg = (f"INCONCLUSIVE_COMBINER_SATURATED (P1 held, gap={base_gap}; P2 FAILED): "
                f"n_diff_tuples(ARM_PLUS_KNOW, ARM_PLUS_KNOW_SCRAMBLE)={n_diff_scramble} < "
                f"{P2_MIN_SCRAMBLE_FLIPS}. Even with a MEASURED (not hand-set) positional reliability, "
                f"selectional knowledge still does not demonstrably move any dedup pick when its content "
                f"is scrambled -- the combiner remains saturated against S3, so the ARM_PLUS_KNOW-vs-"
                f"ARM_BASE comparison cannot be trusted as evidence either way. Do NOT bank a redundancy "
                f"bound from this run. For reference (NOT the gated verdict): F1(ARM_BASE)={f1_base} "
                f"F1(ARM_PLUS_KNOW)={f1_plusknow} F1(ARM_PLUS_KNOW_SCRAMBLE)={f1_scramble}. rescue_analysis="
                f"{res['rescue']}.")
    elif f1_plusknow <= f1_base:
        verdict = "HARD_FAIL_KNOWLEDGE_STILL_REDUNDANT_ON_STRONG_BASE"
        vmsg = (f"HARD_FAIL (P1 held gap={base_gap}; P2 held n_diff_scramble={n_diff_scramble} -- "
                f"knowledge demonstrably HAD a say): F1(ARM_PLUS_KNOW)={f1_plusknow} <= "
                f"F1(ARM_BASE)={f1_base}. Even with a genuinely live combiner (measured reliabilities, "
                f"scramble control fires), selectional knowledge does not lift F1 for this reader at this "
                f"scale -- a fair, deep redundancy bound, not a saturated-combiner artifact. "
                f"F1(ARM_PLUS_KNOW_SCRAMBLE)={f1_scramble} F1(ARM_PLUS_KNOW_ARCSCRAMBLE)={f1_arcscramble}. "
                f"rescue_analysis (does knowledge fix structure's wrong picks?)={res['rescue']}. "
                f"sensitivity_stable={sensitivity_stable} sensitivity={sensitivity}.")
    elif all(hard_pass_conditions.values()):
        verdict = "HARD_PASS_JOINT_KNOWLEDGE_HELPS_ON_STRONG_BASE"
        vmsg = (f"HARD_PASS (P1 held gap={base_gap}; P2 held n_diff_scramble={n_diff_scramble}): "
                f"F1 ARM_BASE={f1_base} -> ARM_PLUS_KNOW={f1_plusknow} "
                f"(delta=+{round(f1_plusknow - f1_base, 4)}); controls fire (ARM_PLUS_KNOW_SCRAMBLE="
                f"{f1_scramble}, ARM_PLUS_KNOW_ARCSCRAMBLE={f1_arcscramble} both collapse as required). "
                f"Selectional knowledge genuinely helps the reader when combined, reliability-weighted "
                f"with MEASURED (not hand-set) reliabilities, ON TOP OF V3's actual positional strength. "
                f"rescue_analysis={res['rescue']}. sensitivity_stable={sensitivity_stable} "
                f"sensitivity={sensitivity}.")
    else:
        verdict = "MIDDLE_BAND_PARTIAL"
        failing = [k for k, v in hard_pass_conditions.items() if not v]
        vmsg = (f"MIDDLE_BAND_PARTIAL (P1+P2 held, gap={base_gap}, n_diff_scramble={n_diff_scramble}) but "
                f"not all HARD_PASS conditions held (failing: {failing}), and F1(ARM_PLUS_KNOW)="
                f"{f1_plusknow} > F1(ARM_BASE)={f1_base} so no HARD_FAIL trigger fired either. "
                f"F1 ARM_PLUS_KNOW_SCRAMBLE={f1_scramble} ARM_PLUS_KNOW_ARCSCRAMBLE={f1_arcscramble}. "
                f"rescue_analysis={res['rescue']}. sensitivity_stable={sensitivity_stable} "
                f"sensitivity={sensitivity}. Genuine but partial signal; localize which condition failed "
                f"before escalating scope.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: F1 ARM_BASE={f1_base} ARM_PLUS_KNOW={f1_plusknow} "
                 f"ARM_PLUS_KNOW_SCRAMBLE={f1_scramble} ARM_PLUS_KNOW_ARCSCRAMBLE={f1_arcscramble} | "
                 f"P1_base_gap={base_gap} (reproduces={base_reproduces_v3}) | P2_n_diff_scramble="
                 f"{n_diff_scramble} (fires={scramble_fires}) | n_competitions={res['n_competitions']} | "
                 f"rescue_rate={res['rescue']['rescue_rate']} | sensitivity_stable={sensitivity_stable} | "
                 f"parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["order"]),
        one_variable="S2's (positional-first cue) reliability is now MEASURED per-lesson via "
                     "leave-one-lesson-out cross-validation (leftmost-candidate==gold accuracy) instead "
                     "of the prior cell's hand-set DESIGNED constant (0.90) -- everything else (S1/S3 "
                     "formulas, parser training, candidate-to-predicate assignment, role-decision "
                     "membership, learned admissibility gate, dense table contents, scoring pipeline) is "
                     "byte-identical reuse or held fixed",
        preconditions=dict(P1_base_reproduces_v3=base_reproduces_v3, P1_gap=base_gap,
                           P1_tolerance=BASE_REPRO_TOLERANCE,
                           P2_scramble_fires=scramble_fires, P2_n_diff_scramble=n_diff_scramble,
                           P2_min_flips_required=P2_MIN_SCRAMBLE_FLIPS),
        bands=dict(BASE_REPRO_TOLERANCE=BASE_REPRO_TOLERANCE, P2_MIN_SCRAMBLE_FLIPS=P2_MIN_SCRAMBLE_FLIPS,
                   HP_KNOW_OVER_BASE_MIN=HP_KNOW_OVER_BASE_MIN, HP_SCRAMBLE_MARGIN=HP_SCRAMBLE_MARGIN,
                   HP_ARCSCRAMBLE_MARGIN=HP_ARCSCRAMBLE_MARGIN,
                   CITED_V3_INTEGRATED_F1=CITED_V3_INTEGRATED_F1),
        f1_v3_integrated_same_run=f1_v3_integrated_same_run, base_gap_vs_v3_integrated=base_gap,
        base_reproduces_v3=base_reproduces_v3, base_fp_hash=res["base_fp_hash"],
        n_competitions=res["n_competitions"],
        arms={name: dict(recall_ceiling=v["recall_ceiling"], n_miss=v["n_miss"], n_gold_pos=v["n_gold_pos"],
                         precision=v["score"]["precision"], recall=v["score"]["recall"], f1=v["score"]["f1"],
                         n_pred=v["n_pred"], subcat_fp=v["score"]["subcat_fp"],
                         within_frame_fp=v["score"]["within_frame_fp"],
                         spurious_verb_fp=v["score"]["spurious_verb_fp"], kept_hash=v["kept_hash"])
              for name, v in scored.items()},
        hard_pass_conditions=hard_pass_conditions,
        n_diff_know_vs_base=n_diff_know_vs_base, n_diff_scramble=n_diff_scramble,
        n_diff_arcscramble=n_diff_arcscramble,
        positional_reliability_measured=dict(by_lesson=res["pos_rel_by_lesson"],
                                              detail=res["pos_rel_detail"],
                                              global_n_correct=res["n_correct_all"],
                                              global_n_det=res["n_det_all"],
                                              method="leave-one-lesson-out cross-validation; "
                                                     "leftmost-candidate==gold accuracy over "
                                                     "gold-determinable multi-patient competitions from "
                                                     "the OTHER lessons only (gold-blind per test lesson)"),
        calibration_check="adaptive_with_discriminator_gate",
        calibration_check_evidence="S2 reliability is DATA-ADAPTIVE (LOLO measured, not a fixed default); "
                                   "discriminator-still-fires verification = the P2 scramble-fires "
                                   "precondition itself (INCONCLUSIVE_COMBINER_SATURATED escape hatch if "
                                   "it does not fire, per META_RULE_M)",
        rescue_analysis=res["rescue"],
        sensitivity=sensitivity, sensitivity_stable=sensitivity_stable,
        cited_v3=dict(source="data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json",
                     f1_v3_integrated=CITED_V3_INTEGRATED_F1),
        cited_jointreliability_positional_v1=dict(
            source="data/exp_multipred_argstruct_jointreliability_positional_v1/metrics.json",
            note="prior cell HARD_FAILED with a hand-set POSITIONAL_RELIABILITY=0.90 and a "
                 "near-zero knowledge-scramble flip count -- INCONCLUSIVE per this cell's own charter; "
                 "THIS cell's P2 gate is the structural fix (INCONCLUSIVE_COMBINER_SATURATED escape "
                 "hatch instead of silently banking a redundancy bound)."),
        parser_info=parser_info,
        scope_caveat=("Parser trained on UD-EWT (newswire/web/blog text) via a from-scratch dynamic-oracle "
                      "arc-eager model at a FOREGROUND-bounded training budget, byte-identical reuse of "
                      "prior cells' own training code; out-of-domain transfer to 19th-c. McGuffey narrative "
                      "prose is the SAME untested transfer flagged upstream. The dense knowledge table is "
                      "LLM-self-built (residual leakage-adjacent risk per denseitem_v1's own scope caveat); "
                      "an independent-KB replication remains the flagged rigor follow-up. The LOLO "
                      "reliability measurement uses only 7 lessons (7-fold LOLO) -- a small number of "
                      "folds for a cross-validated estimate; the per-lesson reliability values may be "
                      "noisy, which is exactly why the sensitivity sweep (+/-30%) is reported alongside "
                      "the headline verdict. CLAIM-VET-pending; strategic read = HYPOTHESIS pending "
                      "landed-VET."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=1))
    print("positional_reliability_measured:", json.dumps(metrics["positional_reliability_measured"], indent=1))
    print("rescue_analysis:", json.dumps(res["rescue"], indent=1))
    print("sensitivity:", json.dumps(sensitivity, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    output_dir = _out_dir(run_mode)
    return build_verdict(output_dir, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir("full"), e)
        raise
