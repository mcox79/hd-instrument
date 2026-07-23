"""FAIR APPLES-TO-APPLES + BRAIN-FAITHFUL joint-reliability test -- does selectional knowledge help the
reader when added as a THIRD reliability-weighted constraint source ON TOP OF a base that ALREADY includes
V3's actual source of strength (a positional/adjacency prior), rather than being compared against a
DIFFERENT, WEAKER base (the flaw in exp_multipred_argstruct_earlyjoint_relweighted_v1)?

THE FLAW THIS CELL FIXES (VET-confirmed, this session): 29483's V3_INTEGRATED (F1=0.5738,
  CITED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json) and the prior EARLY cell's
  EARLY_RELWEIGHTED (F1=0.5492, CITED@data/exp_multipred_argstruct_earlyjoint_relweighted_v1/metrics.json)
  are NOT apples-to-apples: V3_INTEGRATED's dedup tie-break (when >=2 local candidates are independently
  labeled PATIENT) is, in practice, a POSITIONAL-FIRST rule -- V3_KNOWLEDGE_SCRAMBLE reproduces
  V3_INTEGRATED bit-for-bit (kept_hash identical, MEASURED@same metrics.json:arms.V3_KNOWLEDGE_SCRAMBLE.
  kept_hash == arms.V3_INTEGRATED.kept_hash) because the 29479 sparse table (579 pairs) is OOV for nearly
  every competing pair on this slice, so its own tie-break degenerates to "keep the leftmost candidate"
  regardless of the table's content. The EARLY cell's own structure-only control (EARLY_STRUCTURAL_ONLY,
  F1=0.4426) instead deduped by MAX-SOFTMAX-STRUCTURAL-CONFIDENCE alone (no positional term) -- a
  DIFFERENT and WEAKER criterion (54/70-ish correct picks vs V3's positional rule) -- so EARLY_RELWEIGHTED
  (0.5492) was knowledge-added-to-a-weak-base, not knowledge-added-to-V3's-actual-strength. The two cells'
  headline comparison therefore compared across TWO DIFFERENT bases, not one variable.

THE FAIR + BRAIN-FAITHFUL FIX: model the patient dedup decision as a RELIABILITY-WEIGHTED (Ernst & Banks
  2002) combination of THREE constraint sources (not a hard override of one by another; not a two-source
  comparison that omits V3's own real strength):
    S1 = structural softmax P(PATIENT) confidence (reused byte-identically from
         exp_multipred_argstruct_earlyjoint_relweighted_v1.structural_patient_source: value = softmax
         P(PATIENT|feats) under the SAME trained AveragedPerceptron; reliability = |2q-1| against the
         candidate's own best rival role).
    S2 = POSITIONAL-first cue (NEW, this cell -- the source this fix adds; encodes V3's actual empirical
         strength as a WEIGHTED constraint, not a hard argmax): value = 1.0 for the leftmost local patient
         candidate, 0.0 for all others; reliability = POSITIONAL_RELIABILITY, a FIXED, gold-blind DESIGNED
         prior (English canonical SVO word order: the direct object canonically immediately follows its
         verb -- a typological/structural fact about the language, not fit to this gold set) -- see
         `## Positional reliability calibration` below for how the constant was chosen (verified against
         V3_INTEGRATED's OWN F1 on a fresh same-run parse, NOT against this cell's own headline
         discriminator).
    S3 = selectional-knowledge plausibility (reused byte-identically from
         exp_multipred_argstruct_earlyjoint_relweighted_v1.selectional_patient_source +
         build_dense_sel_with_tier, over exp_multipred_argstruct_denseitem_v1's OWN 732-pair dense
         backoff-tiered table -- reliability = RELIABILITY_BY_TIER[tier], MEASURED per-decision from WHICH
         backoff tier answered THIS pair; a gold-blind, evidentiary-specificity-ordered prior, unchanged
         from the EARLY cell).
  ONE combined-decision function (reliability_weighted_combine, byte-identical reuse) takes a LIST of
  (value, reliability, meta) triples and returns the reliability-weighted average; adding S3 to a base of
  {S1, S2} is literally appending one triple to the list -- the combiner and the rest of the pipeline
  (parser training, candidate-to-predicate assignment, role-decision-that-fixes-membership, learned
  admissibility gate, scoring) are ALL byte-identical reuse of 29483/29486's own code.

ARMS (all computed in ONE shared structural traversal per (real-heads) pass -- by_pred / per-candidate
  roles / agents_local / patients_local are IDENTICAL inputs to every arm below; the ONLY thing that
  differs between ARM_BASE / ARM_PLUS_KNOW / ARM_PLUS_KNOW_SCRAMBLE is which triples feed
  reliability_weighted_combine for the dedup tie-break -- this makes "same base" a STRUCTURAL GUARANTEE of
  the code, not just a post-hoc hash check):
    ARM_BASE              = {S1, S2}, no knowledge. Expected to reproduce V3_INTEGRATED's ~0.5738 strength
                             (the FAIR baseline this cell verifies before trusting the headline comparison).
    ARM_PLUS_KNOW          = {S1, S2, S3}, real dense table. THE HEADLINE arm -- ONE variable (S3 present)
                             vs ARM_BASE.
    ARM_PLUS_KNOW_SCRAMBLE = {S1, S2, S3}, S3's dense table VALUES permuted (identical scramble convention
                             to exp_multipred_argstruct_earlyjoint_relweighted_v1.make_scrambled_table:
                             sorted keys, seeded rng.permutation). MUST-FAIL CONTROL (content): knowledge
                             CONTENT, not just the combiner's extra weight-mass, must be load-bearing.
    ARM_PLUS_KNOW_ARCSCRAMBLE = {S1, S2, S3}, real table, decoded head arcs deterministically scrambled
                             (M.scramble_heads, separate traversal -- heads differ, so by_pred differs;
                             this is the ONE arm NOT expected to share the same base). MUST-FAIL CONTROL
                             (structure): real parse structure must still matter more than the knowledge
                             addition alone.
  CITED (context only, NOT recomputed -- reported alongside for the early-vs-late framing the original
  task asked for, at zero extra compute cost): V3_INTEGRATED F1=0.5738 (the positional-tie-break base,
  this cell's ARM_BASE target), V5_INTEGRATED_DENSE F1=0.5328 (the LATE post-hoc dense-argmax gate on the
  SAME assign_fn+gate_fn base, HARD_FAILED against V3_INTEGRATED in denseitem_v1 -- the late-injection
  point this cell's S1+S2+S3 joint combination is contrasted against).

## Positional reliability calibration (done BEFORE the decisive FULL run; a base-reproduction check, NOT a
  discriminator-outcome fit): POSITIONAL_RELIABILITY is fixed at a single a-priori value (0.90) reflecting
  a strong-but-not-absolute structural prior. This is verified in self_test() by checking ARM_BASE's F1
  against V3_INTEGRATED's OWN F1 on the SAME smoke-trained W/clf/slice (both are knowledge-independent
  measurements of "how good is this particular dedup criterion" -- the check calibrates the POSITIONAL
  cue's weight against an independent invariant already measured by a DIFFERENT cell, not against this
  cell's OWN headline knowledge-helps/hurts question). If |F1(ARM_BASE) - F1(V3_INTEGRATED same-run)| is
  large at self-test, the self-test WARNs (does not silently pass) and the FULL run's own
  ARM_BASE-vs-V3_INTEGRATED gap is reported honestly in verdict_msg as a precondition check -- a
  base-mismatch demotes the run to MIDDLE_BAND regardless of the S3 comparison (see bands below).

PRE-REGISTERED BANDS (set BEFORE this run; grounded on the CITED V3_INTEGRATED F1=0.5738 anchor -- a tight
  decisive band per the task's own discriminator spec, NOT calibration-probe +/-50% widening, since the
  anchor is a prior empirical same-reader/gold/split measurement):
  PRECONDITION (checked first, gates interpretation of the headline comparison):
    base_reproduces_v3: abs(F1(ARM_BASE) - F1(V3_INTEGRATED_same_run)) <= 0.06.
    If base_reproduces_v3 is False: verdict = MIDDLE_BAND_BASE_MISMATCH regardless of the arms below (the
    positional prior did not actually reproduce V3's strength, so the S3 comparison is not yet
    apples-to-apples; report the gap for recalibration, do not claim either HARD_PASS or HARD_FAIL).
  HARD_PASS_JOINT_KNOWLEDGE_HELPS_ON_STRONG_BASE (requires base_reproduces_v3 True, ALL of):
    (a) F1(ARM_PLUS_KNOW) > F1(ARM_BASE) + 0.015  (knowledge adds on top of V3's own positional strength)
    (b) F1(ARM_PLUS_KNOW_SCRAMBLE) <= F1(ARM_PLUS_KNOW) - 0.02  (content causally load-bearing)
    (c) F1(ARM_PLUS_KNOW_ARCSCRAMBLE) <= F1(ARM_PLUS_KNOW) - 0.05  (structure still matters)
    (d) n_diff_tuples(ARM_PLUS_KNOW, ARM_PLUS_KNOW_SCRAMBLE) >= 1  (>=1 concrete decision flips under scramble)
  HARD_FAIL_KNOWLEDGE_STILL_REDUNDANT_ON_STRONG_BASE (requires base_reproduces_v3 True, ANY of):
    (a) F1(ARM_PLUS_KNOW) <= F1(ARM_BASE)  (knowledge adds nothing/negative even joint-combined onto the
        TRUE strong base -- the honest, now-fair, deep bound)
    (b) F1(ARM_PLUS_KNOW_SCRAMBLE) >= F1(ARM_PLUS_KNOW) - 0.01 AND
        n_diff_tuples(ARM_PLUS_KNOW, ARM_PLUS_KNOW_SCRAMBLE) == 0  (must-fail control never fires)
  MIDDLE_BAND: otherwise (including base_reproduces_v3 False) -- report which condition failed before
    escalating scope.

FAIRNESS: SAME reader/gold/split/parser-training-budget/clf/gate as 29483/29486/denseitem_v1/the EARLY
  cell (FULL_SLICE = L04/L05/L07/L08/L09/L10/L12; SMOKE_SLICE = L04/L05); gold =
  data/gold_mcguffey_lccp_argstruct_v1.json (independent, single-annotator; read only for scoring). ONE
  variable = presence of S3 (selectional knowledge) in the reliability-weighted combine; parser training /
  candidate-to-predicate assignment (V3.assign_candidates_to_predicates_fixed) / role-decision-that-fixes-
  candidate-membership (SAME clf.predict()) / learned admissibility gate / S1's own formula / S2's own
  formula / dense table contents / scoring pipeline ALL byte-identical reuse or held fixed across ARM_BASE
  and ARM_PLUS_KNOW. The by_pred/roles/agents_local/patients_local computation is SHARED CODE (one pass
  produces all three same-heads arms) -- "same base" is a structural code guarantee, not just a verified
  hash.

BRAIN-CHECK: MacDonald, Pearlmutter & Seidenberg (1994) constraint-based lexicalist account + Ernst & Banks
  (2002) optimal cue combination -- ALL available constraints (syntactic/positional structure, selectional
  plausibility) are combined AT THE POINT OF DECISION weighted by reliability, never as a late override of
  one fully-decided constraint by another. This cell's S2 (positional) source is itself a brain-plausible
  constraint (canonical word-order expectation is a well-attested real-time parsing cue, Bever 1970 NVN
  strategy / MacWhinney's Competition Model word-order cue) that the PRIOR two cells (V3, EARLY) each
  smuggled in asymmetrically -- V3 gave it reliability=1.0 (a hard override, disguised as "knowledge"
  because the sparse table was OOV-inert), EARLY gave it reliability=0.0 (omitted it entirely, comparing
  knowledge against a strictly weaker base). Modeling it explicitly, at a measured intermediate
  reliability, alongside S1 and S3 in the SAME combiner is the more brain-faithful (and more fair) test.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- reuses 29483's arc-eager parser
  training (~50-65s MEASURED) + per-clause greedy decode + AveragedPerceptron scoring (byte-identical
  reuse) + O(candidates) dict lookups + one softmax + one reliability-combine per candidate (O(1) each).
  NO matmul/storage/GPU-batchable primitive. Storage: no_storage. Runtime invariant: glass-box (from-
  scratch-trained transition parser + curated dicts + a build-time-authored dense knowledge dict + a fully
  inspectable reliability-weighted combiner, all LOCAL), NO LLM/network/autograd at inference. Determinism:
  OMP/MKL/OPENBLAS=1, fixed int SEED, numpy default_rng, sorted(keys); no hash()-seeded RNG. LOCAL-ONLY,
  foreground-to-completion. NO push / NO remote-persist / NO queue_add (routing task contract: inline-
  local FULL, pause-state ACTIVE, not banked -- skunkworks VETs separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash test; ARM_BASE vs ARM_PLUS_KNOW vs ARM_PLUS_KNOW_ARCSCRAMBLE
    MUST differ; ARM_PLUS_KNOW vs ARM_PLUS_KNOW_SCRAMBLE exempted at SMOKE scale ONLY per small-sample
    rationale established by 29483/the EARLY cell for their own analogous pairs)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(ARM_BASE) < 0.95)
  - discriminator fires at smoke: >=1 multi-patient competition instance exists at SMOKE_SLICE scale
    (n_competitions >= 1) AND knowledge changes >=1 pick vs ARM_BASE at smoke scale (WARN, not assert, if
    small-sample zero per established discipline) AND scramble changes >=1 pick vs real vs ARM_BASE (WARN)
  - scaffold-free witness (reused, both bypass the full pipeline -- direct unit calls to
    reliability_weighted_combine, same two witnesses the EARLY cell used, now exercised through THIS
    cell's THREE-source combine): (1) confident structure + leftmost positional AGREEING vs a
    sparse/backstop knowledge rating disagreeing -- combine stays close to the S1+S2 value (knowledge
    doesn't override); (2) a DENSE tier0_item knowledge rating disagreeing with an uncertain/toss-up
    structure AND a non-leftmost position -- combine can still flip toward knowledge's preferred candidate
    when S1+S2 are both weak/wrong, demonstrating S3 is genuinely live, not inert.
  - deterministic seeding (fixed int SEED; sorted(dict.keys()) for scramble permutations; numpy
    default_rng; no hash()-seeded RNG)
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (29483/denseitem_v1/EARLY cell metrics.json) /
    THEORETICAL@ (Ernst-Banks combination formula) / DESIGNED (POSITIONAL_RELIABILITY, RELIABILITY_BY_TIER
    -- gold-blind priors, never fit to gold) in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/precision measurement, no HD noise floor); N/A
    multi-seed for the arms (deterministic given fixed SEED; parser training is single-seed by design, a
    scope/wall-time tradeoff already stated+accepted upstream, not hidden here); N/A cardinality-sweep (no
    swept axis besides the fixed arm comparison)
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
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "multipred_argstruct_jointreliability_positional_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Reuse 29483 / 29486 / EARLY cell's OWN code VERBATIM.
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3               # noqa: E402
from experiments import exp_multipred_argstruct_earlyjoint_relweighted_v1 as E          # noqa: E402
from experiments import exp_multipred_argstruct_denseitem_v1 as D                      # noqa: E402
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M                # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L     # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC                 # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2          # noqa: E402

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260727

# ---- Pre-registered bands (set BEFORE this run; see docstring) ------------------------
POSITIONAL_RELIABILITY = 0.90          # DESIGNED, gold-blind prior (canonical SVO adjacency)
HP_KNOW_OVER_BASE_MIN = 0.015
HP_SCRAMBLE_MARGIN = 0.02
HP_ARCSCRAMBLE_MARGIN = 0.05
HP_MIN_DIFF_TUPLES_SCRAMBLE = 1
HF_SCRAMBLE_MARGIN = 0.01
BASE_REPRO_TOLERANCE = 0.06
CITED_V3_INTEGRATED_F1 = 0.5738   # CITED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1
CITED_V5_INTEGRATED_DENSE_F1 = 0.5328  # CITED@data/exp_multipred_argstruct_denseitem_v1/metrics.json:arms.V5_INTEGRATED_DENSE.f1
CITED_EARLY_RELWEIGHTED_F1 = 0.5492   # CITED@data/exp_multipred_argstruct_earlyjoint_relweighted_v1/metrics.json:arms.EARLY_RELWEIGHTED (flawed cross-base comparison this cell supersedes)
BASELINE_BAND = (0.05, 0.95)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# S2: positional-first constraint source (NEW, this cell). Value=1.0 for the leftmost local patient
# candidate, 0.0 otherwise; reliability = fixed DESIGNED prior (see docstring calibration section).
# =======================================================================================
def positional_patient_source(i, patients_local):
    is_leftmost = (i == min(patients_local))
    return (1.0 if is_leftmost else 0.0), POSITIONAL_RELIABILITY, dict(is_leftmost=is_leftmost)


# =======================================================================================
# ONE shared structural traversal producing MULTIPLE arm outputs (S1+S2 always present; S3 present iff
# sel_with_tier_fn is not None for that arm-name's entry). by_pred / roles / agents_local / patients_local
# are computed ONCE per clause and shared byte-identically across every arm in `arm_sel_fns` -- "same base"
# is therefore a code guarantee, not a post-hoc check.
# =======================================================================================
def clause_predicate_pass_joint(tagged, heads, clf, gate_fn, carried_agent_in, assign_fn,
                                 arm_sel_fns, base_fp_log=None, n_competitions_counter=None):
    lows = [t[1] for t in tagged]
    verb_positions = M.content_verb_indices(tagged)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    by_pred = assign_fn(tagged, heads, verb_positions)
    outs = {name: [] for name in arm_sel_fns}
    carried_agent = carried_agent_in
    evidence = {}
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
        for i in local_cand:
            if i > v0 and ORC.prev_prep(tagged, i) is None:
                evidence[vl] = True
        if base_fp_log is not None:
            base_fp_log.append((v0, tuple(sorted(agents_local)), tuple(sorted(patients_local))))
        if len(patients_local) >= 2 and n_competitions_counter is not None:
            n_competitions_counter[0] += 1
        s1s2 = {}
        for i in patients_local:
            p_patient, rel_struct, meta_struct = E.structural_patient_source(clf, feats_cache[i])
            val_pos, rel_pos, meta_pos = positional_patient_source(i, patients_local)
            s1s2[i] = [(p_patient, rel_struct, meta_struct), (val_pos, rel_pos, meta_pos)]
        gate_pass = gate_fn(vl)
        is_main = (v0 == main_idx)
        kind = M.predicate_kind(tagged, v0, is_main) if gate_pass else None
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
            if resolved_agent is not None and kept_patients and low not in ("has", "is") and gate_pass:
                for pi in kept_patients:
                    outs[name].append((low, resolved_agent, tagged[pi][1], v0, kind))
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]
    return outs, carried_agent, evidence


def build_parse_arm_joint(slice_lessons, W, clf, gate_fn, assign_fn, arm_sel_fns, scramble_arcs=False,
                           scramble_seed=None, collect_base_fp=False):
    order, sent_text, _reader_svo = L.load_slice_and_reader(slice_lessons)
    outs = {name: {} for name in arm_sel_fns}
    evidence_total = {}
    base_fp = [] if collect_base_fp else None
    n_competitions = [0]
    for sid in order:
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
            clause_outs, carried_agent, ev = clause_predicate_pass_joint(
                tagged, heads, clf, gate_fn, carried_agent, assign_fn, arm_sel_fns,
                base_fp_log=clause_fp, n_competitions_counter=n_competitions)
            if collect_base_fp:
                for entry in clause_fp:
                    base_fp.append((sid,) + entry)
            for name in arm_sel_fns:
                outs[name].setdefault(sid, []).extend([(t[0], t[1], t[2]) for t in clause_outs[name]])
            for lemma, val in ev.items():
                evidence_total[lemma] = evidence_total.get(lemma, False) or val
    return order, sent_text, outs, evidence_total, base_fp, n_competitions[0]


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
# Run all arms.
# =======================================================================================
def run_all_arms(slice_lessons, W, clf):
    dense_table = D.load_dense_table()
    scrambled_table = E.make_scrambled_table(dense_table, SEED + 13)
    sel_with_tier_real = E.build_dense_sel_with_tier(dense_table)
    sel_with_tier_scrambled = E.build_dense_sel_with_tier(scrambled_table)
    assign_fn = V3.assign_candidates_to_predicates_fixed

    # Pass 1: keepall (gate=True) to build evidence -> learned admissibility gate (byte-identical pattern
    # to V3.run_all_arms_v3's own first pass; single cheap traversal, no knowledge/positional needed).
    _, _, _keepall_outs, evidence, _fp0, _ncomp0 = build_parse_arm_joint(
        slice_lessons, W, clf, lambda v: True, assign_fn, {"KEEPALL": None})
    learned_gate_fixed = M.build_learned_admissibility(evidence)

    # Pass 2: SAME-heads traversal produces ARM_BASE / ARM_PLUS_KNOW / ARM_PLUS_KNOW_SCRAMBLE together --
    # by_pred/roles/agents_local/patients_local are IDENTICAL inputs to all three (structural guarantee).
    arm_sel_fns = {"ARM_BASE": None, "ARM_PLUS_KNOW": sel_with_tier_real,
                   "ARM_PLUS_KNOW_SCRAMBLE": sel_with_tier_scrambled}
    order, sent_text, same_base_outs, _ev2, base_fp, n_competitions = build_parse_arm_joint(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn, arm_sel_fns, collect_base_fp=True)

    # Pass 3: ARM_PLUS_KNOW_ARCSCRAMBLE -- separate traversal, scrambled heads (base MUST differ here).
    _, _, arcscr_outs, _ev3, _fp3, _ncomp3 = build_parse_arm_joint(
        slice_lessons, W, clf, learned_gate_fixed, assign_fn, {"ARM_PLUS_KNOW_ARCSCRAMBLE": sel_with_tier_real},
        scramble_arcs=True, scramble_seed=SEED + 7)

    all_kept = dict(same_base_outs)
    all_kept.update(arcscr_outs)

    gold, _gold_meta = L.load_gold(slice_lessons)
    scored = {}
    for name, kept in all_kept.items():
        rc, miss, npos, _m = M.recall_ceiling_of(kept, gold)
        sc = L.score_arm(M.to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, n_miss=miss, n_gold_pos=npos, score=sc,
                             kept_hash=M.arm_hash(kept), n_pred=sc["n_pred"])

    n_diff_scramble = n_diff_tuples(all_kept["ARM_PLUS_KNOW"], all_kept["ARM_PLUS_KNOW_SCRAMBLE"])
    n_diff_arcscramble = n_diff_tuples(all_kept["ARM_PLUS_KNOW"], all_kept["ARM_PLUS_KNOW_ARCSCRAMBLE"])
    n_diff_know_vs_base = n_diff_tuples(all_kept["ARM_PLUS_KNOW"], all_kept["ARM_BASE"])

    return dict(order=order, sent_text=sent_text, gold=gold, arms=all_kept, scored=scored,
                base_fp_hash=base_fp_hash(base_fp), n_competitions=n_competitions,
                n_diff_scramble=n_diff_scramble, n_diff_arcscramble=n_diff_arcscramble,
                n_diff_know_vs_base=n_diff_know_vs_base, evidence=evidence)


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

    print("[self-test] training arc-eager parser (smoke budget, reused 29483 code) ...")
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
        "DISCRIMINATOR DOES NOT FIRE: zero multi-patient competition instances at SMOKE_SLICE scale " \
        "(the dedup tie-break, and therefore the S1/S2/S3 combine, never engages)"

    prec_base = res["scored"]["ARM_BASE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], \
        f"ARM_BASE precision {prec_base} outside band {BASELINE_BAND}"
    print(f"[self-test] baseline_in_band: precision(ARM_BASE)={prec_base} in {BASELINE_BAND}")

    # Base-reproduction calibration check (against V3_INTEGRATED on the SAME smoke-trained W/clf/slice --
    # NOT against this cell's own headline discriminator; a base-invariant cross-check).
    sparse_table = V3.load_knowledge_table()
    res_v3 = V3.run_all_arms_v3(SMOKE_SLICE, W, clf, sparse_table)
    f1_v3_integrated_smoke = res_v3["scored"]["V3_INTEGRATED"]["score"]["f1"]
    f1_arm_base_smoke = res["scored"]["ARM_BASE"]["score"]["f1"]
    gap = abs(f1_arm_base_smoke - f1_v3_integrated_smoke)
    print(f"[self-test] base-reproduction check (SMOKE_SLICE, same W/clf): "
          f"F1(ARM_BASE)={f1_arm_base_smoke} vs F1(V3_INTEGRATED)={f1_v3_integrated_smoke} gap={gap}")
    if gap > BASE_REPRO_TOLERANCE:
        print(f"[self-test] WARN: base-reproduction gap {gap} exceeds tolerance {BASE_REPRO_TOLERANCE} at "
              f"SMOKE_SLICE scale (small-sample; the FULL run's own gap is the load-bearing precondition "
              f"check, re-verified there, not asserted fatal here)")
    else:
        print(f"[self-test] base-reproduction OK at SMOKE_SLICE scale (gap {gap} <= {BASE_REPRO_TOLERANCE})")

    # arms_differ_verified (META_RULE_AF). ONLY the true structural control (arc-scramble, which changes
    # decoded heads -> by_pred -> the whole base) is HARD-asserted to differ. ARM_BASE vs ARM_PLUS_KNOW and
    # ARM_PLUS_KNOW vs ARM_PLUS_KNOW_SCRAMBLE are BOTH small-sample-exemptable at SMOKE scale (the whole
    # point of this cell is that they CAN legitimately tie when few multi-patient competitions exist and/or
    # the scramble doesn't happen to flip a pick) -- the FULL run's aggregate F1 gap is the load-bearing
    # must-fail/must-differ check, not a smoke-scale hash.
    hashes = {name: v["kept_hash"] for name, v in res["scored"].items()}
    assert hashes["ARM_PLUS_KNOW"] != hashes["ARM_PLUS_KNOW_ARCSCRAMBLE"], \
        f"META_RULE_AF VIOLATION: ARM_PLUS_KNOW and ARM_PLUS_KNOW_ARCSCRAMBLE bit-identical: {hashes}"
    arms_differ_exempted = [("ARM_BASE", "ARM_PLUS_KNOW"), ("ARM_PLUS_KNOW", "ARM_PLUS_KNOW_SCRAMBLE")]
    if hashes["ARM_BASE"] == hashes["ARM_PLUS_KNOW"]:
        print("[self-test] WARN: ARM_BASE == ARM_PLUS_KNOW kept_hash at SMOKE_SLICE scale (small-sample; "
              "declared arms_differ_exempted; the FULL run's aggregate F1 gap is the load-bearing "
              "must-differ check, not this hash)")
    if hashes["ARM_PLUS_KNOW"] == hashes["ARM_PLUS_KNOW_SCRAMBLE"]:
        print("[self-test] WARN: ARM_PLUS_KNOW == ARM_PLUS_KNOW_SCRAMBLE kept_hash at SMOKE_SLICE scale "
              "(small-sample; declared arms_differ_exempted; the FULL run's aggregate F1 gap is the "
              "load-bearing must-fail check, not this hash)")
    print(f"[self-test] arms_differ_verified (arc-scramble vs real, HARD): "
          f"ARM_PLUS_KNOW={hashes['ARM_PLUS_KNOW']} ARM_PLUS_KNOW_ARCSCRAMBLE="
          f"{hashes['ARM_PLUS_KNOW_ARCSCRAMBLE']}; exempted (small-sample WARN-only): {arms_differ_exempted}")

    if res["scored"]["ARM_PLUS_KNOW"]["kept_hash"] == res["scored"]["ARM_BASE"]["kept_hash"]:
        print("[self-test] WARN: knowledge (S3) had ZERO measurable effect vs ARM_BASE at SMOKE_SLICE "
              "scale (small-sample; the FULL run has far more multi-patient competition instances)")
    else:
        print("[self-test] knowledge (S3) changes >=1 pick vs ARM_BASE at smoke scale (kept_hash differs)")

    # scaffold-free witness (1): THE FIX -- confident structure AND leftmost-position AGREEING vs a
    # sparse/backstop-tier knowledge rating disagreeing -- combine stays close to S1+S2 (knowledge doesn't
    # override a doubly-confident base).
    sources_agree = [(0.90, 0.95, {}), (1.0, POSITIONAL_RELIABILITY, {})]
    combined_no_know, _ = E.reliability_weighted_combine(sources_agree)
    sources_with_sparse_disagree = sources_agree + [(0.10, 0.03, {})]
    combined_with_sparse, _ = E.reliability_weighted_combine(sources_with_sparse_disagree)
    print(f"[self-test] witness1 (S1+S2 confident+leftmost agree, S3 sparse disagrees): "
          f"combine(S1+S2)={combined_no_know:.4f} combine(S1+S2+sparse_S3)={combined_with_sparse:.4f}")
    assert abs(combined_with_sparse - combined_no_know) < 0.05, \
        (f"WITNESS FAIL: a sparse/backstop-tier (reliability=0.03) knowledge rating moved the combine by "
         f">=0.05 despite a confident, positionally-agreeing S1+S2 base -- reliability-weighting is not "
         f"suppressing the unreliable cue as designed")
    print("[self-test] scaffold-free witness 1 PASS: sparse/backstop knowledge does not override a "
          "confident, positionally-agreeing structural base")

    # scaffold-free witness (2): a DENSE tier0_item knowledge rating disagreeing with an uncertain/toss-up
    # structure AND a non-leftmost position -- combine can still flip toward knowledge when S1+S2 are weak.
    sources_weak_wrong = [(0.50, 0.0, {}), (0.0, POSITIONAL_RELIABILITY, {})]  # toss-up structure, non-leftmost
    combined_weak_only, _ = E.reliability_weighted_combine(sources_weak_wrong)
    sources_weak_plus_dense = sources_weak_wrong + [(0.95, 0.90, {})]  # tier0_item, high value+reliability
    combined_weak_plus_dense, _ = E.reliability_weighted_combine(sources_weak_plus_dense)
    print(f"[self-test] witness2 (S1 toss-up + S2 non-leftmost, S3 dense/high disagrees): "
          f"combine(S1+S2 only)={combined_weak_only:.4f} combine(+dense_S3)={combined_weak_plus_dense:.4f}")
    assert combined_weak_plus_dense > combined_weak_only + 0.10, \
        (f"WITNESS FAIL: a dense tier0_item knowledge rating did not measurably raise the combine when "
         f"S1 is a toss-up (reliability=0) and S2 opposes (non-leftmost) -- S3 is not live")
    print("[self-test] scaffold-free witness 2 PASS: dense/high-reliability knowledge is live and can "
          "move the combine when structure+position are weak/opposed")

    # determinism: two identical runs produce identical kept-tuple hashes.
    res2 = run_all_arms(SMOKE_SLICE, W, clf)
    assert res["scored"]["ARM_PLUS_KNOW"]["kept_hash"] == res2["scored"]["ARM_PLUS_KNOW"]["kept_hash"], \
        "non-deterministic ARM_PLUS_KNOW output across identical runs"
    print("[self-test] deterministic (two ARM_PLUS_KNOW runs produce identical kept-tuple hash)")

    print(f"[self-test] base_fp_hash={res['base_fp_hash']} (ARM_BASE/ARM_PLUS_KNOW/ARM_PLUS_KNOW_SCRAMBLE "
          f"share ONE structural traversal -- same-base is a code guarantee)")
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

    # Same-run V3_INTEGRATED reference (fresh W/clf, true same-run fairness -- NOT the cross-run CITED
    # constant, though both are reported).
    sparse_table = V3.load_knowledge_table()
    res_v3 = V3.run_all_arms_v3(slice_lessons, W, clf, sparse_table)
    f1_v3_integrated_same_run = res_v3["scored"]["V3_INTEGRATED"]["score"]["f1"]

    f1_base = scored["ARM_BASE"]["score"]["f1"]
    f1_plusknow = scored["ARM_PLUS_KNOW"]["score"]["f1"]
    f1_scramble = scored["ARM_PLUS_KNOW_SCRAMBLE"]["score"]["f1"]
    f1_arcscramble = scored["ARM_PLUS_KNOW_ARCSCRAMBLE"]["score"]["f1"]

    base_gap = round(abs(f1_base - f1_v3_integrated_same_run), 4)
    base_reproduces_v3 = base_gap <= BASE_REPRO_TOLERANCE

    n_diff_scramble = res["n_diff_scramble"]
    n_diff_arcscramble = res["n_diff_arcscramble"]
    n_diff_know_vs_base = res["n_diff_know_vs_base"]

    hard_pass_conditions = dict(
        knowledge_beats_base=(f1_plusknow > f1_base + HP_KNOW_OVER_BASE_MIN),
        control_scramble=(f1_scramble <= f1_plusknow - HP_SCRAMBLE_MARGIN),
        control_arcscramble=(f1_arcscramble <= f1_plusknow - HP_ARCSCRAMBLE_MARGIN),
        scramble_flips_min_tuples=(n_diff_scramble >= HP_MIN_DIFF_TUPLES_SCRAMBLE),
    )
    hard_fail_reasons = []
    if f1_plusknow <= f1_base:
        hard_fail_reasons.append(f"F1(ARM_PLUS_KNOW) {f1_plusknow} <= F1(ARM_BASE) {f1_base} (knowledge "
                                  f"adds nothing/negative even joint-combined onto the TRUE strong base)")
    if f1_scramble >= f1_plusknow - HF_SCRAMBLE_MARGIN and n_diff_scramble == 0:
        hard_fail_reasons.append(f"F1(ARM_PLUS_KNOW_SCRAMBLE) {f1_scramble} >= F1(ARM_PLUS_KNOW) "
                                  f"{f1_plusknow} - {HF_SCRAMBLE_MARGIN} AND n_diff_tuples=0 (must-fail "
                                  f"content control never fires)")

    if not base_reproduces_v3:
        verdict = "MIDDLE_BAND_BASE_MISMATCH"
        vmsg = (f"MIDDLE_BAND_BASE_MISMATCH: F1(ARM_BASE)={f1_base} vs F1(V3_INTEGRATED same-run)="
                f"{f1_v3_integrated_same_run} (CITED cross-run={CITED_V3_INTEGRATED_F1}); gap={base_gap} "
                f"exceeds tolerance {BASE_REPRO_TOLERANCE}. The positional prior (reliability="
                f"{POSITIONAL_RELIABILITY}) did not reproduce V3's actual strength on this run, so the "
                f"ARM_PLUS_KNOW-vs-ARM_BASE comparison is not yet apples-to-apples -- recalibrate "
                f"POSITIONAL_RELIABILITY before trusting the headline comparison. For reference (NOT the "
                f"gated verdict): F1(ARM_PLUS_KNOW)={f1_plusknow} F1(ARM_PLUS_KNOW_SCRAMBLE)={f1_scramble} "
                f"F1(ARM_PLUS_KNOW_ARCSCRAMBLE)={f1_arcscramble}.")
    elif hard_fail_reasons:
        verdict = "HARD_FAIL_KNOWLEDGE_STILL_REDUNDANT_ON_STRONG_BASE"
        vmsg = ("HARD_FAIL: " + "; ".join(hard_fail_reasons) +
                f". F1 ARM_BASE={f1_base} (base_gap_vs_V3_INTEGRATED={base_gap}, reproduces=True) "
                f"ARM_PLUS_KNOW={f1_plusknow} ARM_PLUS_KNOW_SCRAMBLE={f1_scramble} "
                f"ARM_PLUS_KNOW_ARCSCRAMBLE={f1_arcscramble}. n_diff_tuples: know_vs_base="
                f"{n_diff_know_vs_base} scramble={n_diff_scramble} arcscramble={n_diff_arcscramble}. "
                f"HONEST DEFLATE: even joint-combined onto the TRUE strong (positional-inclusive) base, "
                f"selectional knowledge does not lift F1 for this reader at this scale -- a fair, deeper "
                f"redundancy bound, not an injection-point artifact. CITED context: V5_INTEGRATED_DENSE "
                f"(late post-hoc gate, SAME assign_fn/gate_fn base)={CITED_V5_INTEGRATED_DENSE_F1}; "
                f"prior flawed cross-base EARLY_RELWEIGHTED={CITED_EARLY_RELWEIGHTED_F1}.")
    elif all(hard_pass_conditions.values()):
        verdict = "HARD_PASS_JOINT_KNOWLEDGE_HELPS_ON_STRONG_BASE"
        vmsg = (f"HARD_PASS: F1 ARM_BASE={f1_base} (base_gap_vs_V3_INTEGRATED={base_gap}, reproduces=True) "
                f"-> ARM_PLUS_KNOW={f1_plusknow} (delta=+{round(f1_plusknow - f1_base, 4)}); controls fire "
                f"(ARM_PLUS_KNOW_SCRAMBLE={f1_scramble}, ARM_PLUS_KNOW_ARCSCRAMBLE={f1_arcscramble} both "
                f"collapse as required, n_diff_tuples scramble={n_diff_scramble}). Selectional knowledge "
                f"genuinely helps the reader when combined, reliability-weighted, ON TOP OF V3's actual "
                f"positional strength -- the fair, apples-to-apples reopening of the knowledge leg. CITED "
                f"context: V5_INTEGRATED_DENSE (late gate)={CITED_V5_INTEGRATED_DENSE_F1}.")
    else:
        verdict = "MIDDLE_BAND_PARTIAL"
        failing = [k for k, v in hard_pass_conditions.items() if not v]
        vmsg = (f"MIDDLE_BAND: base reproduces V3 (gap={base_gap}) but not all HARD_PASS conditions held "
                f"(failing: {failing}), and no HARD_FAIL trigger fired. F1 ARM_BASE={f1_base} "
                f"ARM_PLUS_KNOW={f1_plusknow} ARM_PLUS_KNOW_SCRAMBLE={f1_scramble} "
                f"ARM_PLUS_KNOW_ARCSCRAMBLE={f1_arcscramble}. n_diff_tuples: know_vs_base="
                f"{n_diff_know_vs_base} scramble={n_diff_scramble} arcscramble={n_diff_arcscramble}. "
                f"Genuine but partial signal; localize which condition failed before escalating scope.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: F1 ARM_BASE={f1_base} ARM_PLUS_KNOW={f1_plusknow} "
                 f"ARM_PLUS_KNOW_SCRAMBLE={f1_scramble} ARM_PLUS_KNOW_ARCSCRAMBLE={f1_arcscramble} | "
                 f"base_gap_vs_V3_INTEGRATED={base_gap} (reproduces={base_reproduces_v3}) | "
                 f"n_competitions={res['n_competitions']} | n_diff know_vs_base={n_diff_know_vs_base} "
                 f"scramble={n_diff_scramble} arcscramble={n_diff_arcscramble} | parser_uas="
                 f"{parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["order"]), positional_reliability=POSITIONAL_RELIABILITY,
        one_variable="presence of S3 (selectional knowledge, reliability-tiered over the 732-pair dense "
                     "table) in the reliability-weighted combine ON TOP OF a base already containing S1 "
                     "(structural softmax confidence) + S2 (positional-first cue, the source of V3's own "
                     "actual strength) -- parser training / candidate-to-predicate assignment / role-"
                     "decision membership / learned admissibility gate ALL byte-identical/held fixed",
        bands=dict(POSITIONAL_RELIABILITY=POSITIONAL_RELIABILITY, BASE_REPRO_TOLERANCE=BASE_REPRO_TOLERANCE,
                   HP_KNOW_OVER_BASE_MIN=HP_KNOW_OVER_BASE_MIN, HP_SCRAMBLE_MARGIN=HP_SCRAMBLE_MARGIN,
                   HP_ARCSCRAMBLE_MARGIN=HP_ARCSCRAMBLE_MARGIN,
                   HP_MIN_DIFF_TUPLES_SCRAMBLE=HP_MIN_DIFF_TUPLES_SCRAMBLE,
                   HF_SCRAMBLE_MARGIN=HF_SCRAMBLE_MARGIN,
                   CITED_V3_INTEGRATED_F1=CITED_V3_INTEGRATED_F1,
                   CITED_V5_INTEGRATED_DENSE_F1=CITED_V5_INTEGRATED_DENSE_F1,
                   CITED_EARLY_RELWEIGHTED_F1=CITED_EARLY_RELWEIGHTED_F1),
        f1_v3_integrated_same_run=f1_v3_integrated_same_run, base_gap_vs_v3_integrated=base_gap,
        base_reproduces_v3=base_reproduces_v3, base_fp_hash=res["base_fp_hash"],
        n_competitions=res["n_competitions"],
        arms={name: dict(recall_ceiling=v["recall_ceiling"], n_miss=v["n_miss"], n_gold_pos=v["n_gold_pos"],
                         precision=v["score"]["precision"], recall=v["score"]["recall"], f1=v["score"]["f1"],
                         n_pred=v["n_pred"], subcat_fp=v["score"]["subcat_fp"],
                         within_frame_fp=v["score"]["within_frame_fp"],
                         spurious_verb_fp=v["score"]["spurious_verb_fp"], kept_hash=v["kept_hash"])
              for name, v in scored.items()},
        hard_pass_conditions=hard_pass_conditions, hard_fail_reasons=hard_fail_reasons,
        n_diff_know_vs_base=n_diff_know_vs_base, n_diff_scramble=n_diff_scramble,
        n_diff_arcscramble=n_diff_arcscramble,
        cited_v3=dict(source="data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json",
                     f1_v3_integrated=CITED_V3_INTEGRATED_F1,
                     note="V3_INTEGRATED's dedup degenerates to a positional-leftmost rule on this slice "
                          "(V3_KNOWLEDGE_SCRAMBLE reproduced it bit-for-bit) -- this cell's ARM_BASE (S1+S2) "
                          "is the fair reconstruction of that same strength via an explicit, weighted "
                          "positional source rather than an accidental OOV-driven hard override."),
        cited_v5_late_gate=dict(source="data/exp_multipred_argstruct_denseitem_v1/metrics.json",
                                f1_v5_integrated_dense=CITED_V5_INTEGRATED_DENSE_F1,
                                note="LATE post-hoc dense-argmax gate on the SAME assign_fn/gate_fn base "
                                     "(HARD_FAILED vs V3_INTEGRATED); reported for the early-vs-late framing."),
        cited_early_flawed=dict(source="data/exp_multipred_argstruct_earlyjoint_relweighted_v1/metrics.json",
                                f1_early_relweighted=CITED_EARLY_RELWEIGHTED_F1,
                                f1_early_structural_only=0.4426,
                                note="SUPERSEDED cross-base comparison this cell fixes: EARLY_STRUCTURAL_ONLY "
                                     "(0.4426) omitted the positional source entirely, so EARLY_RELWEIGHTED "
                                     "(0.5492) was knowledge-added-to-a-weak-base, not knowledge-added-to-"
                                     "V3's-actual-strength."),
        parser_info=parser_info,
        scope_caveat=("Parser trained on UD-EWT (newswire/web/blog text) via a from-scratch dynamic-oracle "
                      "arc-eager model at a FOREGROUND-bounded training budget, byte-identical reuse of "
                      "29483's own training code; out-of-domain transfer to 19th-c. McGuffey narrative "
                      "prose is the SAME untested transfer flagged upstream. The dense knowledge table is "
                      "LLM-self-built (residual leakage-adjacent risk per denseitem_v1's own scope caveat); "
                      "an independent-KB replication remains the flagged rigor follow-up. "
                      "POSITIONAL_RELIABILITY=0.90 is a single fixed DESIGNED prior, not swept -- a "
                      "sensitivity sweep over this constant is a natural follow-up if the base-reproduction "
                      "gap is large. CLAIM-VET-pending; strategic read = HYPOTHESIS pending landed-VET."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=1))
    print("base_reproduces_v3:", base_reproduces_v3, "gap:", base_gap)
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
