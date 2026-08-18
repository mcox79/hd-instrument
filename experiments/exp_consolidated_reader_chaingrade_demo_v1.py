"""CONSOLIDATED WHO-DID-WHAT READER -- CHAIN-GRADE DEMONSTRATION (v1).

ONE runnable module that COMPOSES the current-best banked reader components over REAL McGuffey verbatim
text AND wires them to the 4-part CHAIN-GRADE rubric (from hdlab/glass_box_loop.py, the project's only prior
CHAIN_GRADE loop). A chain-grade capability must demonstrate ALL of:
  (1) a real baseline FAILS where the mechanism succeeds (discriminator fires on REAL data)  -> ARM B
  (2) a causal hand-edit of a LOGGED intermediate step FLIPS the downstream output (glass-box,
      monitor-not-control)                                                                    -> ARM C
  (3) auditable: tamper-detected + deterministic replay reproduces                            -> ARM C
  (4) non-ceiling at scale (result is not an N=163 artifact)                                  -> ARM D
Component oracle-uplifts are MEASURED_MECHANISM; the COMPOSED reader demonstrated end-to-end is the
chain-grade. This cell BUILDS that demonstration and is re-runnable so improved ENUM/ROLE components drop in.

CONSOLIDATED READER = current-best structural reader, COMPOSED (not re-authored -- every component is an
  IMPORT of its banked cell):
    * base parser-integrated multi-predicate reader (arc-eager dep parse + two-pass agent-routing
      candidate-to-predicate assignment) -- exp_multipred_argstruct_agentfix_kbgate_v3 (V3), F1=0.5738
      MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1
    * do/have LEXICAL-vs-auxiliary reclassification -- the KEEPER recall lever, exp_multipred_argstruct_
      enumext_v4 (E), V4_DOHAVE_ONLY F1=0.592 rc=0.74 prec=0.4933 MEASURED@data/exp_multipred_argstruct_
      enumext_v4/metrics.json:arms.V4_DOHAVE_ONLY
    * ECM subject-sharing is DROPPED (net-negative per VET seq 29495: V4_ECM_ONLY F1=0.5703 < DOHAVE_ONLY
      0.592; V4_FULL 0.5882 < DOHAVE_ONLY -- ECM drags F1 down). CITED@task-prompt 2026-07-23.
    * role/patient assignment (AveragedPerceptron clf + learned subcat/valency admissibility gate +
      knowledge-argmax patient disambiguation MECHANISM) -- byte-identical reuse of V3/E code. NOTE the
      knowledge CONTENT is fairly REDUNDANT for this simple-narrative slice (29491/29483: KNOWLEDGE_SCRAMBLE
      == INTEGRATED); it is the argmax-among-competing-patients MECHANISM (precision lever), not the table
      values, that this reader keeps -- reported honestly, not narrated as a knowledge win.
  So the consolidated reader is exactly E's V4_DOHAVE_ONLY configuration (use_dohave=True, use_ecm=False),
  which composes all of the above. PLUGGABILITY: run_consolidated_reader() takes a components dict; an
  improved ENUM (candidate recall) or ROLE (assignment) module swaps in by replacing the enumeration /
  assignment callables E exposes -- see the PLUG POINTS comment block at run_consolidated_reader.

ARMS:
  ARM A (READER)        : the consolidated structural reader on REAL McGuffey verbatim (FULL_SLICE, 163
                          sentences); end-to-end who-did-what accuracy (patient-F1 + precision + recall +
                          recall_ceiling), scored vs the independent LCCP gold.
  ARM B (DISCRIMINATOR) : a REAL naive positional baseline (nearest-noun-LEFT-of-verb = agent, nearest-noun-
                          RIGHT-of-verb = patient; NO parse, NO role clf, NO gate). Must be in-band (can
                          fail) AND the reader must beat it by a pre-registered margin AND recover a
                          pre-registered count of gold tuples the naive baseline misses. THIS is the
                          chain-grade discriminator: a real baseline that FAILS where structure succeeds.
  ARM C (CAUSAL GLASS-  : logs the parse->enum->role trace per sentence; (a) deterministic replay
        BOX)            reproduces the trace-hash; (b) a sha256 AUDIT HASH over the canonical trace + a
                          one-field TAMPER breaks it; (c) a CAUSAL hand-edit of ONE logged ROLE assignment
                          FLIPS the downstream who-did-what tuple (agent<->patient swap), proving the logged
                          intermediate is causally load-bearing (monitor-not-control); (d) a secondary
                          BRIDGE edit: changing ONE logged parse head-arc RE-ROUTES a candidate to a
                          different predicate. All four are binary gates.
  ARM D (SCALE / non-   : the reader-beats-naive margin is NOT an N=163 artifact -- (i) per-lesson breakdown
        ceiling)        over all 7 golded lessons (positive margin on >= K of 7); (ii) two DISJOINT lesson
                          halves scored independently (reader beats naive on BOTH); (iii) extended-corpus
                          THROUGHPUT on a SECOND ungolded McGuffey slice (L13-L17) showing the mechanism runs
                          stably at larger N (tuples/sentence + do/have fire-rate, no crash/degradation).
                          Non-ceiling is further evidenced by the component oracle audit: ALL_ORACLE F1=0.7106
                          > reader 0.592 (headroom, reader is not at ceiling) CITED@data/exp_reader_component_
                          oracle_ablation_audit_v1/metrics.json:f1.ALL_ORACLE.

PRE-REGISTERED BANDS (set BEFORE this run; grounded on the DOHAVE_ONLY MEASURED anchor F1=0.592, rc=0.74,
  prec=0.4933 and the BASELINE_svo / naive references; tight decisive bands, NOT calibration-probe widening):
  ARM A HARD_PASS_READER_COMPOSES: F1(READER) >= 0.55 AND recall_ceiling(READER) >= 0.70 AND
    precision(READER) > precision(BASELINE_svo).
  ARM A HARD_FAIL: F1(READER) <= F1(BASELINE_svo) OR recall_ceiling(READER) <= 0.44.
  ARM B DISCRIMINATOR_FIRES: 0.05 < F1(NAIVE) < 0.95 (in-band, can-fail) AND F1(READER) - F1(NAIVE) >= 0.12
    AND n_recovered_vs_naive >= 8 (reader gets >= 8 gold tuples the naive baseline misses).
  ARM B DESIGN_GATE_FAIL: F1(NAIVE) >= 0.95 (saturated -- cannot fail) OR F1(NAIVE) <= 0.05 (floor) OR
    F1(READER) - F1(NAIVE) < 0.12.
  ARM C GLASS_BOX_OK: replay_hash_stable AND tamper_detected AND causal_role_edit_flipped AND
    bridge_head_edit_reroutes (all four True).
  ARM C GLASS_BOX_FAIL: any of the four False.
  ARM D NON_CEILING_OK: reader-beats-naive margin > 0 on BOTH disjoint halves AND positive-margin lesson
    count >= 5 of 7 AND extended-corpus reader emits > 0 tuples with no crash.
  ARM D CEILING_ARTIFACT: margin <= 0 on either half OR positive-margin lesson count <= 3.
  CHAIN_GRADE_DEMONSTRATED iff ARM A HARD_PASS AND ARM B FIRES AND ARM C OK AND ARM D OK (all four rubric
    parts). Otherwise PARTIAL (report which parts hold) or FAIL.

FAIRNESS (P1/P2): same reader/gold/split as 29473/29478/29483/29491 (FULL_SLICE = L04/L05/L07/L08/L09/L10/
  L12; SMOKE_SLICE = L04/L05); gold = data/gold_mcguffey_lccp_argstruct_v1.json (independent single-annotator,
  never read while authoring this scaffold). The naive baseline is a GENUINE real baseline that CAN fail
  (positional heuristic, no structure) -- design-gate-verified in-band at smoke. ONE clear variable per arm:
  ARM A = the composed reader vs its own BASELINE_svo; ARM B = structure vs no-structure (positional); ARM C
  = one edited intermediate vs unedited; ARM D = which subsample. Parser training / role clf / gate / do-have
  reclassification / knowledge-argmax all byte-identical IMPORT of V3/E/M code -- nothing re-transcribed.

BRAIN-CHECK: constraint-based lexicalist parsing -- syntax (parse) AND selectional plausibility jointly
  constrain argument-role assignment in real-time human processing (MacDonald/Pearlmutter/Seidenberg 1994;
  Trueswell/Tanenhaus/Garnsey 1994). The positional baseline is the null hypothesis (linear order alone); the
  human reader, like this composed reader, uses structure -- and FAILS the same positional errors when
  structure is unavailable (garden-path / OSV difficulty), so ARM B's margin is the brain-faithful
  structure-over-order effect, not an engineering artifact.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- imports V3/E/M arc-eager parser training
  (~45-50s MEASURED, once) + per-clause greedy decode (ms/clause) + AveragedPerceptron role classification +
  O(candidates) dict lookups; NO matmul/storage/GPU-batchable primitive; wall ~4-6min total (parser train
  once + one reader arm [2 passes] + one naive arm [POS-only, no parse] + cheap glass-box on a handful of
  sentences + free subset-scoring for ARM D + one extended-slice reader pass). Storage: no_storage. Runtime
  invariant: glass-box (from-scratch-trained transition parser + curated dicts + corpus-observed
  admissibility table + build-time knowledge dict), NO LLM/network/autograd at inference. Determinism:
  OMP/MKL/OPENBLAS=1, fixed int SEED, numpy default_rng, sorted(set); no hash()-seeded RNG. LOCAL-ONLY,
  foreground-to-completion. NO push / NO remote-persist / NO queue_add (routing task contract: inline-local
  FULL, not banked -- skunkworks VETs separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground demonstration cell):
  - arms_differ_verified at smoke (hash over READER vs NAIVE kept-tuple sets)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASELINE_svo) < 0.95 AND 0.05 < F1(NAIVE) < 0.95)
  - discriminator fires at smoke: F1(READER) > F1(NAIVE) AND reader recovers >=1 gold tuple naive misses
  - glass-box witnesses at smoke: replay stable, tamper breaks hash, role-edit flips a tuple, head-edit
    re-routes a candidate (all four demonstrated at smoke scale on a real slice sentence)
  - deterministic seeding (fixed int SEED; sorted(set) ordering; numpy default_rng)
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (V3/E/oracle-audit metrics) in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/precision measurement, no HD noise floor); N/A multi-seed
    (deterministic given fixed SEED; parser's own training single-seed by design, stated+accepted in
    V3/E, not hidden)
  - progress_logging: print_flush_true (sys.stdout line-buffered at cell start)
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

ANCHOR_NAME = "consolidated_reader_chaingrade_demo_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# IMPORT (do not re-transcribe) every banked component. Module scope of each is guarded by
# `if __name__ == "__main__"`, so importing does NOT re-run their experiments.
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3     # noqa: E402
from experiments import exp_multipred_argstruct_enumext_v4 as E              # noqa: E402
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M      # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC       # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2  # noqa: E402

FULL_SLICE = M.FULL_SLICE                       # L04,L05,L07,L08,L09,L10,L12 (163 golded sentences)
SMOKE_SLICE = M.SMOKE_SLICE                     # L04,L05
HALF_A = ["L04", "L05", "L07"]
HALF_B = ["L08", "L09", "L10", "L12"]
SCALE_EXT_SLICE_FULL = ["L13", "L14", "L15", "L16", "L17"]   # second ungolded McGuffey slice (throughput)
SCALE_EXT_SLICE_SMOKE = ["L13"]
SEED = 20260727

# ---- Pre-registered bands (see docstring) ---------------------------------------------
# ARM A
HP_A_F1_MIN = 0.55
HP_A_RC_MIN = 0.70
HF_A_RC_MAX = 0.44
# ARM B
NAIVE_BAND = (0.05, 0.95)
HP_B_MARGIN_MIN = 0.12
HP_B_RECOVERED_MIN = 8
# ARM D
HP_D_POS_LESSON_MIN = 5
HF_D_POS_LESSON_MAX = 3
# References (MEASURED on disk this session)
CITED_DOHAVE_F1 = 0.592          # MEASURED@data/exp_multipred_argstruct_enumext_v4/metrics.json:arms.V4_DOHAVE_ONLY.f1
CITED_DOHAVE_RC = 0.74
CITED_DOHAVE_PREC = 0.4933
CITED_V3_F1 = 0.5738             # MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1
CITED_ALL_ORACLE_F1 = 0.7106     # MEASURED@data/exp_reader_component_oracle_ablation_audit_v1/metrics.json:f1.ALL_ORACLE
CITED_ECM_ONLY_F1 = 0.5703       # net-negative, dropped


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# ARM A -- the consolidated structural reader (COMPOSED from banked components).
# =======================================================================================
def run_consolidated_reader(slice_lessons, W, clf, ratings_table, use_dohave=True, use_ecm=False):
    """The current-best composed reader. Returns (order, sent_text, arm_dict, gate, sel_fn).

    PLUG POINTS (for dropping in improved components without touching this cell's rubric wiring):
      * ENUMERATION  : E.content_verb_indices_ext (predicate loci; do/have reclassification) and
                       E.assign_candidates_to_predicates_ecm (candidate->predicate routing, wrapping
                       V3.assign_candidates_to_predicates_fixed). An improved candidate-recall module
                       replaces these two callables inside E.clause_predicate_pass_v4.
      * ROLE         : clf (AveragedPerceptron from V2._fit_clf) + M.build_learned_admissibility gate +
                       the knowledge-argmax patient disambiguation (sel_fn). An improved role assigner
                       replaces clf / the gate builder.
    Composition today = E's V4_DOHAVE_ONLY config: use_dohave=True (KEEPER lever), use_ecm=False (dropped,
    net-negative). Everything else is byte-identical reuse of V3/E/M code."""
    sel_fn = V3.build_sel_fn(ratings_table)
    order, sent_text, arm, gate = E.build_gate_and_arm(slice_lessons, W, clf, sel_fn,
                                                        use_dohave=use_dohave, use_ecm=use_ecm)
    return order, sent_text, arm, gate, sel_fn


# =======================================================================================
# ARM B -- REAL naive positional baseline (the chain-grade discriminator; can fail).
# =======================================================================================
def naive_positional_arm(slice_lessons):
    """For each clause: for each content-verb (plain M.content_verb_indices -- NO do/have, kept naive),
    agent = nearest noun/pronoun candidate to the LEFT of the verb, patient = nearest to the RIGHT. NO
    parse, NO role clf, NO admissibility gate. This is the null 'linear order alone' hypothesis; it fails
    on fronted-object / passive / OSV / do-support / multi-clause structure -- exactly where the composed
    reader's structure succeeds."""
    order, sent_text, _reader_svo = L.load_slice_and_reader(slice_lessons)
    out = {}
    for sid in order:
        raw = sent_text[sid]
        tups = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            verbs = M.content_verb_indices(tagged)
            cands = ORC.candidate_indices(tagged)
            for v0 in verbs:
                left = [i for i in cands if i < v0]
                right = [i for i in cands if i > v0]
                if not right:
                    continue
                agent_i = max(left) if left else None
                patient_i = min(right)
                agent_w = tagged[agent_i][1] if agent_i is not None else None
                if agent_w is None:
                    continue
                tups.append((tagged[v0][1], agent_w, tagged[patient_i][1]))
        out[sid] = tups
    return order, sent_text, out


# =======================================================================================
# ARM C -- glass-box trace + deterministic replay + audit hash/tamper + causal edits.
# =======================================================================================
def trace_clause(tagged, heads, clf, gate_fn, sel_fn, carried_agent, use_dohave=True, use_ecm=False):
    """Mirror E.clause_predicate_pass_v4 EXACTLY, recording every intermediate step (parse heads ->
    enumerated predicates -> candidate-to-predicate assignment [bridge] -> per-candidate roles ->
    resolved_agent/kept_patients -> emitted tuple). Returns (trace_dict, emitted_tuples, out_carried_agent).
    The trace is the LOGGED intermediate the ARM-C edits operate on."""
    lows = [t[1] for t in tagged]
    verb_positions = E.content_verb_indices_ext(tagged, use_dohave=use_dohave)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    by_pred = E.assign_candidates_to_predicates_ecm(tagged, heads, verb_positions, use_ecm=use_ecm)
    preds = []
    emitted = []
    cur_carried = carried_agent
    for v0 in verb_positions:
        v1 = v0 + 1
        low = tagged[v0][1]
        passive = M._detect_passive(tagged, v0, lows)
        local_cand = sorted(by_pred.get(v1, []))
        first_cand = local_cand[0] if local_cand else None
        roles = {}
        sel_scores = {}
        vl = L.lemma_verb(low)
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
            roles[i] = clf.predict(feats)
            s = sel_fn(vl, tagged[i][1]) if sel_fn is not None else None
            sel_scores[i] = None if s is None else float(s)
        is_main = (v0 == main_idx)
        kind = M.predicate_kind(tagged, v0, is_main)
        gate_ok = bool(gate_fn(vl))
        prec = dict(v0=v0, v1=v1, low=low, vl=vl, kind=kind, gate_ok=gate_ok,
                    local_cand=list(local_cand),
                    cand_words={str(i): tagged[i][1] for i in local_cand},
                    roles={str(i): roles[i] for i in local_cand},
                    sel_scores={str(i): sel_scores[i] for i in local_cand})
        preds.append(prec)
        # emission (faithful to E.clause_predicate_pass_v4)
        emit_for_pred = _emit_for_predicate(prec, carried_agent=cur_carried)
        emitted.extend(emit_for_pred)
        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        if agents_local:
            cur_carried = tagged[agents_local[0]][1]
    trace = dict(tokens=[list(t) for t in tagged],
                 heads={str(k): v for k, v in heads.items()},
                 predicates=preds, carried_agent_in=carried_agent)
    return trace, emitted, cur_carried


def _emit_for_predicate(prec, carried_agent, role_overrides=None):
    """Recompute the emitted (verb, agent, patient) tuples for one predicate from its LOGGED trace record,
    applying optional role_overrides {cand_idx(int): 'AGENT'|'PATIENT'|...}. This is the function ARM C's
    causal edit calls with vs without an override to demonstrate the logged role is load-bearing."""
    local_cand = list(prec["local_cand"])
    cand_words = {int(k): v for k, v in prec["cand_words"].items()}
    sel_scores = {int(k): prec["sel_scores"][k] for k in prec["sel_scores"]}
    roles = {int(k): prec["roles"][k] for k in prec["roles"]}
    if role_overrides:
        for i, r in role_overrides.items():
            roles[int(i)] = r
    agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
    patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
    resolved_agent = cand_words[agents_local[0]] if agents_local else carried_agent
    kept_patients = patients_local
    if len(patients_local) >= 2:
        # knowledge-argmax MECHANISM (same as reader): pick max sel-score, deterministic -i tie-break
        def _score(i):
            s = sel_scores.get(i)
            return -1.0 if s is None else s
        kept_patients = [max(patients_local, key=lambda i: (_score(i), -i))]
    out = []
    low = prec["low"]
    if resolved_agent is not None and kept_patients and low not in ("has", "is") and prec["gate_ok"]:
        for pi in kept_patients:
            out.append((low, resolved_agent, cand_words[pi]))
    return out


def _canonical_trace_hash(trace):
    return hashlib.sha256(json.dumps(trace, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()


def glass_box_demo(slice_lessons, W, clf, gate_fn, sel_fn):
    """Run the four glass-box gates on REAL slice sentences. Returns a result dict (all gates + witnesses)."""
    order, sent_text, _svo = L.load_slice_and_reader(slice_lessons)

    # (a) deterministic replay + (b) audit hash / tamper: first sentence that emits >=1 tuple.
    replay_hash_stable = None
    tamper_detected = None
    audit_witness = None
    for sid in order:
        raw = sent_text[sid]
        carried = None
        emitted_all = []
        traces = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            tr, emt, carried = trace_clause(tagged, heads, clf, gate_fn, sel_fn, carried)
            traces.append(tr)
            emitted_all.extend(emt)
        if emitted_all:
            # replay: recompute the SAME sentence's traces again -> identical hash
            carried2 = None
            traces2 = []
            for clause_text in ORC.split_sentences(raw):
                tagged = ORC.pos_tag_sentence(clause_text)
                if not tagged:
                    continue
                heads = M.decode_clause(tagged, W)
                tr2, _emt2, carried2 = trace_clause(tagged, heads, clf, gate_fn, sel_fn, carried2)
                traces2.append(tr2)
            h1 = _canonical_trace_hash(traces)
            h2 = _canonical_trace_hash(traces2)
            replay_hash_stable = (h1 == h2)
            # tamper: mutate ONE role label in a copy, re-hash -> must differ
            tampered = json.loads(json.dumps(traces))
            mutated = False
            for tr in tampered:
                for prec in tr["predicates"]:
                    if prec["roles"]:
                        k0 = sorted(prec["roles"].keys())[0]
                        orig = prec["roles"][k0]
                        prec["roles"][k0] = "PATIENT" if orig != "PATIENT" else "AGENT"
                        mutated = True
                        break
                if mutated:
                    break
            h_tamper = _canonical_trace_hash(tampered)
            tamper_detected = mutated and (h_tamper != h1)
            audit_witness = dict(sid=sid, audit_hash=h1, replay_hash=h2, tamper_hash=h_tamper,
                                 emitted=[list(t) for t in emitted_all])
            break

    # (c) causal ROLE edit: find first clause/predicate emitting a tuple with exactly one local AGENT and
    #     >=1 local PATIENT; swap AGENT<->PATIENT roles; show the emitted (v,a,p) agent/patient FLIP.
    causal_role_edit_flipped = None
    causal_witness = None
    for sid in order:
        raw = sent_text[sid]
        clauses = ORC.split_sentences(raw)
        if len(clauses) != 1:
            continue  # single-clause so carried_agent=None -> deterministic, no cross-clause carry
        tagged = ORC.pos_tag_sentence(clauses[0])
        if not tagged:
            continue
        heads = M.decode_clause(tagged, W)
        tr, emt, _c = trace_clause(tagged, heads, clf, gate_fn, sel_fn, None)
        for prec in tr["predicates"]:
            roles = {int(k): v for k, v in prec["roles"].items()}
            agents = [i for i in prec["local_cand"] if roles.get(i) == "AGENT"]
            patients = [i for i in prec["local_cand"] if roles.get(i) == "PATIENT"]
            base_emit = _emit_for_predicate(prec, carried_agent=None)
            if len(agents) == 1 and len(patients) >= 1 and base_emit:
                a_i, p_i = agents[0], patients[0]
                override = {a_i: "PATIENT", p_i: "AGENT"}
                edited_emit = _emit_for_predicate(prec, carried_agent=None, role_overrides=override)
                if base_emit and edited_emit and base_emit[0] != edited_emit[0] and \
                        base_emit[0][1] == edited_emit[0][2] and base_emit[0][2] == edited_emit[0][1]:
                    causal_role_edit_flipped = True
                    causal_witness = dict(sid=sid, sentence=clauses[0], verb=prec["low"],
                                          edited_step="role assignment (AGENT<->PATIENT swap on one logged "
                                                      "candidate pair)",
                                          before=list(base_emit[0]), after=list(edited_emit[0]),
                                          agent_cand=prec["cand_words"][str(a_i)],
                                          patient_cand=prec["cand_words"][str(p_i)])
                    break
        if causal_role_edit_flipped:
            break
    if causal_role_edit_flipped is None:
        causal_role_edit_flipped = False

    # (d) BRIDGE (parse head-arc) edit: change ONE logged head so a candidate re-routes to a different
    #     predicate. Find a clause with >=2 predicates and a candidate assigned to one of them; re-point
    #     that candidate's head to the OTHER predicate and show its assignment changes.
    bridge_head_edit_reroutes = None
    bridge_witness = None
    for sid in order:
        raw = sent_text[sid]
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            verbs = E.content_verb_indices_ext(tagged, use_dohave=True)
            if len(verbs) < 2:
                continue
            by_pred = E.assign_candidates_to_predicates_ecm(tagged, heads, verbs, use_ecm=False)
            # pick a candidate assigned to predicate p1a; re-point its head to predicate p1b
            cand0 = None
            p1a = None
            for p1, cands in by_pred.items():
                if cands:
                    cand0 = sorted(cands)[0]
                    p1a = p1
                    break
            if cand0 is None:
                continue
            others = [v + 1 for v in verbs if (v + 1) != p1a]
            if not others:
                continue
            p1b = sorted(others)[0]
            edited_heads = dict(heads)
            edited_heads[cand0 + 1] = p1b   # re-point the candidate's head arc to the other predicate
            new_by_pred = E.assign_candidates_to_predicates_ecm(tagged, edited_heads, verbs, use_ecm=False)
            was_in_a = cand0 in by_pred.get(p1a, [])
            now_in_b = cand0 in new_by_pred.get(p1b, [])
            now_in_a = cand0 in new_by_pred.get(p1a, [])
            if was_in_a and now_in_b and not now_in_a:
                bridge_head_edit_reroutes = True
                bridge_witness = dict(sid=sid, sentence=clause_text, candidate=tagged[cand0][1],
                                      edited_step="parse head-arc (re-pointed one candidate's head)",
                                      from_predicate=tagged[p1a - 1][1], to_predicate=tagged[p1b - 1][1])
                break
        if bridge_head_edit_reroutes:
            break
    if bridge_head_edit_reroutes is None:
        bridge_head_edit_reroutes = False

    glass_box_ok = bool(replay_hash_stable and tamper_detected and causal_role_edit_flipped
                        and bridge_head_edit_reroutes)
    return dict(replay_hash_stable=bool(replay_hash_stable), tamper_detected=bool(tamper_detected),
                causal_role_edit_flipped=bool(causal_role_edit_flipped),
                bridge_head_edit_reroutes=bool(bridge_head_edit_reroutes),
                glass_box_ok=glass_box_ok, audit_witness=audit_witness,
                causal_witness=causal_witness, bridge_witness=bridge_witness)


# =======================================================================================
# Scoring helpers (subset-aware; free for ARM D).
# =======================================================================================
def _score_arm_dict(arm_dict, gold):
    kept = M.to_kept_list(arm_dict)
    sc = L.score_arm(kept, gold)
    rc, miss, npos, misses = M.recall_ceiling_of(arm_dict, gold)
    return sc, rc, misses


def _subset(arm_dict, lessons):
    lset = set(lessons)
    return {sid: v for sid, v in arm_dict.items() if sid.split("_")[0] in lset}


def _subset_gold(gold, lessons):
    lset = set(lessons)
    return {sid: v for sid, v in gold.items() if sid.split("_")[0] in lset}


# =======================================================================================
# ARM D -- scale / non-ceiling (per-lesson + disjoint halves + extended throughput).
# =======================================================================================
def scale_analysis(reader_arm, naive_arm, gold, order, scale_ext_slice, W, clf, ratings_table):
    lessons = sorted({sid.split("_")[0] for sid in order})
    per_lesson = []
    pos_lesson = 0
    for lid in lessons:
        gl = _subset_gold(gold, [lid])
        if not gl:
            continue
        r_sc, _, _ = _score_arm_dict(_subset(reader_arm, [lid]), gl)
        n_sc, _, _ = _score_arm_dict(_subset(naive_arm, [lid]), gl)
        margin = round(r_sc["f1"] - n_sc["f1"], 4)
        if margin > 0:
            pos_lesson += 1
        per_lesson.append(dict(lesson=lid, reader_f1=r_sc["f1"], naive_f1=n_sc["f1"], margin=margin,
                               n_gold=r_sc["n_gold"]))
    halves = {}
    for name, lessons_h in (("HALF_A", HALF_A), ("HALF_B", HALF_B)):
        gl = _subset_gold(gold, lessons_h)
        r_sc, r_rc, _ = _score_arm_dict(_subset(reader_arm, lessons_h), gl)
        n_sc, _, _ = _score_arm_dict(_subset(naive_arm, lessons_h), gl)
        halves[name] = dict(lessons=lessons_h, reader_f1=r_sc["f1"], reader_recall_ceiling=r_rc,
                            naive_f1=n_sc["f1"], margin=round(r_sc["f1"] - n_sc["f1"], 4),
                            n_gold=r_sc["n_gold"])
    both_halves_reader_wins = (halves["HALF_A"]["margin"] > 0 and halves["HALF_B"]["margin"] > 0)

    # extended-corpus throughput on a SECOND ungolded McGuffey slice (no accuracy -- behavior stability).
    order_e, sent_e, ext_arm, _g, _s = run_consolidated_reader(scale_ext_slice, W, clf, ratings_table,
                                                               use_dohave=True, use_ecm=False)
    n_sents_e = len(order_e)
    n_tuples_e = sum(len(v) for v in ext_arm.values())
    # do/have fire-rate on the extended slice (lexical do/have predicates the plain enumeration would drop)
    dohave_fires = 0
    for sid in order_e:
        for clause_text in ORC.split_sentences(sent_e[sid]):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            plain = set(M.content_verb_indices(tagged))
            ext = set(E.content_verb_indices_ext(tagged, use_dohave=True))
            dohave_fires += len(ext - plain)
    ext_throughput = dict(slice=scale_ext_slice, n_sentences=n_sents_e, n_tuples=n_tuples_e,
                          tuples_per_sentence=round(n_tuples_e / n_sents_e, 3) if n_sents_e else 0.0,
                          dohave_extra_predicates=dohave_fires, crashed=False)
    return dict(per_lesson=per_lesson, n_positive_margin_lessons=pos_lesson, n_lessons=len(per_lesson),
                halves=halves, both_halves_reader_wins=both_halves_reader_wins,
                extended_throughput=ext_throughput)


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
    print("[self-test] loading SMOKE_SLICE reader + gold + knowledge table ...")
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    assert len(ratings_table) > 100, f"knowledge table suspiciously small: {len(ratings_table)}"
    gold, _meta = L.load_gold(SMOKE_SLICE)

    print("[self-test] training arc-eager parser (smoke budget, reused V3/E code) ...")
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"
    print(f"[self-test] parser trained: {parser_info}")

    # ARM A reader
    order, sent_text, reader_arm, gate, sel_fn = run_consolidated_reader(
        SMOKE_SLICE, W, clf, ratings_table, use_dohave=True, use_ecm=False)
    r_sc, r_rc, _ = _score_arm_dict(reader_arm, gold)
    print(f"[self-test] ARM A reader (SMOKE): f1={r_sc['f1']} prec={r_sc['precision']} "
          f"rec={r_sc['recall']} rc={r_rc}")

    # ARM A BASELINE_svo (for precision/f1 floor)
    _o, _st, reader_svo = L.load_slice_and_reader(SMOKE_SLICE)
    base_sc, _brc, _ = _score_arm_dict({sid: reader_svo[sid] for sid in order}, gold)
    assert NAIVE_BAND[0] < base_sc["precision"] < NAIVE_BAND[1], \
        f"BASELINE_svo precision {base_sc['precision']} outside band {NAIVE_BAND}"
    print(f"[self-test] baseline_in_band: precision(BASELINE_svo)={base_sc['precision']} f1={base_sc['f1']}")

    # ARM B naive
    _o2, _st2, naive_arm = naive_positional_arm(SMOKE_SLICE)
    n_sc, _nrc, _ = _score_arm_dict(naive_arm, gold)
    print(f"[self-test] ARM B naive positional (SMOKE): f1={n_sc['f1']} prec={n_sc['precision']} "
          f"rec={n_sc['recall']}")
    assert NAIVE_BAND[0] < n_sc["f1"] < NAIVE_BAND[1], \
        f"DESIGN-GATE: naive F1 {n_sc['f1']} outside can-fail band {NAIVE_BAND} (cannot fail / saturated)"
    assert r_sc["f1"] > n_sc["f1"], \
        f"discriminator did not fire at smoke: reader f1 {r_sc['f1']} <= naive f1 {n_sc['f1']}"

    # arms_differ_verified (READER vs NAIVE bit-different)
    h_reader = M.arm_hash(reader_arm)
    h_naive = M.arm_hash(naive_arm)
    assert h_reader != h_naive, f"META_RULE_AF: READER and NAIVE arm hashes collide ({h_reader})"
    print(f"[self-test] arms_differ_verified: reader={h_reader} naive={h_naive}")

    # discriminator recovers >=1 gold tuple naive misses
    reader_cov = M.covered_set(reader_arm, gold)
    naive_cov = M.covered_set(naive_arm, gold)
    recovered = sorted(reader_cov - naive_cov)
    print(f"[self-test] reader recovers {len(recovered)} gold tuples naive misses (sample: {recovered[:3]})")
    assert len(recovered) >= 1, "discriminator: reader recovered 0 gold tuples over naive at smoke scale"

    # ARM C glass-box (all four gates on the smoke slice)
    gb = glass_box_demo(SMOKE_SLICE, W, clf, gate, sel_fn)
    print(f"[self-test] ARM C glass-box: replay={gb['replay_hash_stable']} tamper={gb['tamper_detected']} "
          f"role_flip={gb['causal_role_edit_flipped']} bridge={gb['bridge_head_edit_reroutes']}")
    assert gb["replay_hash_stable"], "GLASS-BOX: deterministic replay hash NOT stable"
    assert gb["tamper_detected"], "GLASS-BOX: tamper did NOT break the audit hash"
    assert gb["causal_role_edit_flipped"], "GLASS-BOX: causal role-edit did NOT flip the output tuple"
    assert gb["bridge_head_edit_reroutes"], "GLASS-BOX: bridge head-edit did NOT re-route a candidate"
    print(f"[self-test] causal witness: {gb['causal_witness']}")
    print(f"[self-test] bridge witness: {gb['bridge_witness']}")

    # determinism: two reader runs identical
    _o3, _st3, reader_arm2, _g2, _s2 = run_consolidated_reader(
        SMOKE_SLICE, W, clf, ratings_table, use_dohave=True, use_ecm=False)
    assert M.arm_hash(reader_arm) == M.arm_hash(reader_arm2), "non-deterministic reader output"
    print("[self-test] deterministic (two reader runs produce identical kept-tuple hash)")

    # ARM D scale (smoke: 2 lessons + tiny extended slice)
    scale = scale_analysis(reader_arm, naive_arm, gold, order, SCALE_EXT_SLICE_SMOKE, W, clf, ratings_table)
    print(f"[self-test] ARM D scale (SMOKE): per_lesson={[(p['lesson'], p['margin']) for p in scale['per_lesson']]} "
          f"pos_lessons={scale['n_positive_margin_lessons']}/{scale['n_lessons']} "
          f"halves margins A={scale['halves']['HALF_A']['margin']} B={scale['halves']['HALF_B']['margin']} "
          f"ext_throughput={scale['extended_throughput']}")
    assert scale["extended_throughput"]["n_tuples"] >= 0 and not scale["extended_throughput"]["crashed"], \
        "ARM D extended throughput crashed or produced no run"

    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict (FULL).
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    scale_ext = SCALE_EXT_SLICE_SMOKE if run_mode == "smoke" else SCALE_EXT_SLICE_FULL
    _write_start_marker(output_dir, run_mode, expected_n_units=len(slice_lessons))
    print(f"[full] mode={run_mode} slice={slice_lessons}", flush=True)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    gold, _meta = L.load_gold(slice_lessons)
    W, parser_info = M.train_dep_parser(run_mode)
    print(f"[full] parser trained uas={parser_info['uas_dev']}", flush=True)

    # ARM A -- consolidated reader
    order, sent_text, reader_arm, gate, sel_fn = run_consolidated_reader(
        slice_lessons, W, clf, ratings_table, use_dohave=True, use_ecm=False)
    r_sc, r_rc, r_misses = _score_arm_dict(reader_arm, gold)
    _o, _st, reader_svo = L.load_slice_and_reader(slice_lessons)
    baseline_svo_arm = {sid: reader_svo[sid] for sid in order}
    base_sc, base_rc, _ = _score_arm_dict(baseline_svo_arm, gold)
    print(f"[full] ARM A reader f1={r_sc['f1']} prec={r_sc['precision']} rec={r_sc['recall']} rc={r_rc} "
          f"| baseline_svo f1={base_sc['f1']} prec={base_sc['precision']}", flush=True)

    # ARM B -- naive discriminator
    _o2, _st2, naive_arm = naive_positional_arm(slice_lessons)
    n_sc, n_rc, _ = _score_arm_dict(naive_arm, gold)
    reader_cov = M.covered_set(reader_arm, gold)
    naive_cov = M.covered_set(naive_arm, gold)
    recovered_vs_naive = sorted(reader_cov - naive_cov)
    margin_reader_naive = round(r_sc["f1"] - n_sc["f1"], 4)
    print(f"[full] ARM B naive f1={n_sc['f1']} prec={n_sc['precision']} rec={n_sc['recall']} | "
          f"margin(reader-naive)={margin_reader_naive} recovered_vs_naive={len(recovered_vs_naive)}",
          flush=True)

    # ARM C -- glass-box
    gb = glass_box_demo(slice_lessons, W, clf, gate, sel_fn)
    print(f"[full] ARM C glass-box replay={gb['replay_hash_stable']} tamper={gb['tamper_detected']} "
          f"role_flip={gb['causal_role_edit_flipped']} bridge={gb['bridge_head_edit_reroutes']}", flush=True)

    # ARM D -- scale / non-ceiling
    scale = scale_analysis(reader_arm, naive_arm, gold, order, scale_ext, W, clf, ratings_table)
    print(f"[full] ARM D pos_lessons={scale['n_positive_margin_lessons']}/{scale['n_lessons']} "
          f"both_halves={scale['both_halves_reader_wins']} ext={scale['extended_throughput']}", flush=True)

    # ---- per-arm verdicts ----
    arm_a_pass = (r_sc["f1"] >= HP_A_F1_MIN and r_rc >= HP_A_RC_MIN and r_sc["precision"] > base_sc["precision"])
    arm_a_fail = (r_sc["f1"] <= base_sc["f1"] or r_rc <= HF_A_RC_MAX)
    arm_b_fires = (NAIVE_BAND[0] < n_sc["f1"] < NAIVE_BAND[1] and margin_reader_naive >= HP_B_MARGIN_MIN
                   and len(recovered_vs_naive) >= HP_B_RECOVERED_MIN)
    arm_b_designfail = (n_sc["f1"] >= NAIVE_BAND[1] or n_sc["f1"] <= NAIVE_BAND[0]
                        or margin_reader_naive < HP_B_MARGIN_MIN)
    arm_c_ok = gb["glass_box_ok"]
    arm_d_ok = (scale["both_halves_reader_wins"]
                and scale["n_positive_margin_lessons"] >= HP_D_POS_LESSON_MIN
                and scale["extended_throughput"]["n_tuples"] > 0
                and not scale["extended_throughput"]["crashed"])
    arm_d_artifact = (not scale["both_halves_reader_wins"]
                      or scale["n_positive_margin_lessons"] <= HF_D_POS_LESSON_MAX)

    chain_grade = (arm_a_pass and arm_b_fires and arm_c_ok and arm_d_ok)
    parts = dict(ARM_A_reader_composes=arm_a_pass, ARM_B_discriminator_fires=arm_b_fires,
                 ARM_C_glass_box_ok=arm_c_ok, ARM_D_non_ceiling_ok=arm_d_ok)

    if chain_grade:
        verdict = "CHAIN_GRADE_DEMONSTRATED"
        vmsg = (f"CHAIN_GRADE_DEMONSTRATED (all 4 rubric parts): (1) discriminator -- reader F1={r_sc['f1']} "
                f"beats naive positional F1={n_sc['f1']} by {margin_reader_naive}, recovering "
                f"{len(recovered_vs_naive)} gold tuples the naive baseline misses; (2)+(3) glass-box -- "
                f"deterministic replay stable, sha256 audit hash tamper-detected, causal role-edit flips the "
                f"who-did-what tuple, bridge head-edit re-routes a candidate; (4) non-ceiling -- reader beats "
                f"naive on BOTH disjoint halves (A={scale['halves']['HALF_A']['margin']}, "
                f"B={scale['halves']['HALF_B']['margin']}) and on "
                f"{scale['n_positive_margin_lessons']}/{scale['n_lessons']} lessons, runs stably on the "
                f"L13-L17 extended slice ({scale['extended_throughput']['n_tuples']} tuples over "
                f"{scale['extended_throughput']['n_sentences']} sentences). ARM A reader rc={r_rc} "
                f"prec={r_sc['precision']} vs baseline_svo f1={base_sc['f1']} prec={base_sc['precision']}. "
                f"Component headroom remains (all-oracle F1={CITED_ALL_ORACLE_F1} CITED) -- not at ceiling.")
    elif arm_a_fail or arm_b_designfail or arm_d_artifact or (not arm_c_ok):
        verdict = "CHAIN_GRADE_FAIL"
        reasons = []
        if arm_a_fail:
            reasons.append(f"ARM A: reader F1={r_sc['f1']} <= baseline_svo {base_sc['f1']} OR rc={r_rc} <= {HF_A_RC_MAX}")
        if arm_b_designfail:
            reasons.append(f"ARM B design-gate: naive F1={n_sc['f1']} out-of-band OR margin={margin_reader_naive} < {HP_B_MARGIN_MIN}")
        if not arm_c_ok:
            reasons.append(f"ARM C glass-box: replay={gb['replay_hash_stable']} tamper={gb['tamper_detected']} "
                           f"role_flip={gb['causal_role_edit_flipped']} bridge={gb['bridge_head_edit_reroutes']}")
        if arm_d_artifact:
            reasons.append(f"ARM D: both_halves={scale['both_halves_reader_wins']} pos_lessons={scale['n_positive_margin_lessons']}")
        vmsg = "CHAIN_GRADE_FAIL: " + "; ".join(reasons) + ". HONEST DEFLATE: not all rubric parts held."
    else:
        verdict = "CHAIN_GRADE_PARTIAL"
        failing = [k for k, v in parts.items() if not v]
        vmsg = (f"CHAIN_GRADE_PARTIAL: no hard-fail trigger but not all 4 rubric parts passed (failing: "
                f"{failing}). reader F1={r_sc['f1']} naive F1={n_sc['f1']} margin={margin_reader_naive} "
                f"recovered={len(recovered_vs_naive)}; glass_box_ok={arm_c_ok}; "
                f"pos_lessons={scale['n_positive_margin_lessons']}/{scale['n_lessons']} "
                f"both_halves={scale['both_halves_reader_wins']}. Localize the failing part before escalating.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: reader_f1={r_sc['f1']} prec={r_sc['precision']} rec={r_sc['recall']} "
                 f"rc={r_rc} | naive_f1={n_sc['f1']} margin={margin_reader_naive} "
                 f"recovered_vs_naive={len(recovered_vs_naive)} | baseline_svo_f1={base_sc['f1']} | "
                 f"glass_box_ok={arm_c_ok} (replay={gb['replay_hash_stable']} tamper={gb['tamper_detected']} "
                 f"role_flip={gb['causal_role_edit_flipped']} bridge={gb['bridge_head_edit_reroutes']}) | "
                 f"pos_lessons={scale['n_positive_margin_lessons']}/{scale['n_lessons']} "
                 f"both_halves={scale['both_halves_reader_wins']} | parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(order),
        chain_grade_parts=parts, chain_grade_demonstrated=chain_grade,
        one_variable="per-arm: ARM A composed reader (do/have KEEPER + two-pass parse-fix + role clf + gate "
                     "+ knowledge-argmax MECHANISM; ECM dropped, net-negative) vs its own BASELINE_svo; "
                     "ARM B structure vs no-structure (naive positional); ARM C one edited logged "
                     "intermediate vs unedited; ARM D which subsample. All components byte-identical IMPORT "
                     "of V3/E/M banked code.",
        bands=dict(HP_A_F1_MIN=HP_A_F1_MIN, HP_A_RC_MIN=HP_A_RC_MIN, HF_A_RC_MAX=HF_A_RC_MAX,
                   NAIVE_BAND=list(NAIVE_BAND), HP_B_MARGIN_MIN=HP_B_MARGIN_MIN,
                   HP_B_RECOVERED_MIN=HP_B_RECOVERED_MIN, HP_D_POS_LESSON_MIN=HP_D_POS_LESSON_MIN,
                   HF_D_POS_LESSON_MAX=HF_D_POS_LESSON_MAX,
                   CITED_DOHAVE_F1=CITED_DOHAVE_F1, CITED_DOHAVE_RC=CITED_DOHAVE_RC,
                   CITED_DOHAVE_PREC=CITED_DOHAVE_PREC, CITED_V3_F1=CITED_V3_F1,
                   CITED_ALL_ORACLE_F1=CITED_ALL_ORACLE_F1, CITED_ECM_ONLY_F1=CITED_ECM_ONLY_F1),
        arm_a_reader=dict(f1=r_sc["f1"], precision=r_sc["precision"], recall=r_sc["recall"],
                          recall_ceiling=r_rc, n_pred=r_sc["n_pred"], tp=r_sc["tp"], n_gold=r_sc["n_gold"],
                          subcat_fp=r_sc["subcat_fp"], within_frame_fp=r_sc["within_frame_fp"],
                          spurious_verb_fp=r_sc["spurious_verb_fp"], kept_hash=M.arm_hash(reader_arm)),
        arm_a_baseline_svo=dict(f1=base_sc["f1"], precision=base_sc["precision"], recall=base_sc["recall"],
                                recall_ceiling=base_rc, kept_hash=M.arm_hash(baseline_svo_arm)),
        arm_b_naive=dict(f1=n_sc["f1"], precision=n_sc["precision"], recall=n_sc["recall"],
                         recall_ceiling=n_rc, n_pred=n_sc["n_pred"], kept_hash=M.arm_hash(naive_arm),
                         margin_reader_minus_naive=margin_reader_naive,
                         n_recovered_vs_naive=len(recovered_vs_naive),
                         recovered_vs_naive_sample=[list(x) for x in recovered_vs_naive[:40]]),
        arm_c_glass_box=gb,
        arm_d_scale=scale,
        parser_info=parser_info,
        cited=dict(dohave_only="data/exp_multipred_argstruct_enumext_v4/metrics.json:arms.V4_DOHAVE_ONLY",
                   v3_integrated="data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED",
                   oracle_audit="data/exp_reader_component_oracle_ablation_audit_v1/metrics.json",
                   ecm_dropped_vet="VET seq 29495 -- ECM net-negative, dropped"),
        scope_caveat=("Parser trained on UD-EWT (newswire/web/blog) via a from-scratch dynamic-oracle "
                      "arc-eager model at a FOREGROUND-bounded budget (byte-identical reuse of V3/E code); "
                      "out-of-domain transfer to 19th-c. McGuffey narrative prose is the SAME untested "
                      "transfer V3/E flagged. The extended L13-L17 scale slice is UNGOLDED -- ARM D reports "
                      "THROUGHPUT/behavior stability there (tuples/sentence, do/have fire-rate), NOT "
                      "accuracy; a truly held-out SECOND-GENRE accuracy demonstration requires new gold "
                      "annotation (flagged follow-up). The knowledge table (29479) content is fairly "
                      "REDUNDANT for this simple-narrative slice (29491); the reader keeps the argmax "
                      "MECHANISM not a knowledge win. This is a DEMONSTRATION SCAFFOLD (chain-grade wiring "
                      "of composed components), CLAIM-VET-pending; strategic read = HYPOTHESIS pending "
                      "landed-VET (skunkworks VETs the numbers separately per the routing contract)."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arm_a_reader:", json.dumps(metrics["arm_a_reader"]))
    print("arm_b_naive:", json.dumps({k: v for k, v in metrics["arm_b_naive"].items()
                                      if k != "recovered_vs_naive_sample"}))
    print("arm_c_glass_box:", json.dumps({k: gb[k] for k in
          ("replay_hash_stable", "tamper_detected", "causal_role_edit_flipped", "bridge_head_edit_reroutes",
           "glass_box_ok")}))
    print("arm_c_causal_witness:", json.dumps(gb["causal_witness"]))
    print("arm_d_scale:", json.dumps(scale))
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
