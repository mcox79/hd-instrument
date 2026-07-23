"""COMPONENT-LEVEL ORACLE-ABLATION AUDIT of the best current who-did-what reader (V3_INTEGRATED arm of
exp_multipred_argstruct_agentfix_kbgate_v3.py, landed end-to-end patient-F1=0.5738, MEASURED@data/
exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1). DIAGNOSTIC cell (not a
capability claim): for EACH separable pipeline stage (PARSE routing, CANDIDATE/PREDICATE ENUMERATION,
ROLE/PATIENT ASSIGNMENT), rerun the SAME end-to-end reader with ONLY that stage's output replaced by the
GOLD/ORACLE value (everything else real), and measure the end-to-end patient-F1 uplift vs the all-real
baseline. ALL-ORACLE = all three stages oracle simultaneously = the reader's own composition-LOGIC
ceiling given perfect inputs. Ranks components by end-to-end oracle-uplift = the prioritized
underperformer list for the chain-grade-each-component effort.

PIPELINE STAGES AUDITED (glass-box, all reused byte-identical from the reader's own modules):
  tokenization -> POS (ORC.pos_tag_sentence, NLTK PerceptronTagger) -> PARSE (M.decode_clause, the
  from-scratch arc-eager transition parser trained on UD-EWT, CITED@exp_depparse_transition_arceager_
  cpu_v1.py atom 29451, ~0.79-0.81 UAS) -> CANDIDATE/PREDICATE ENUMERATION (ORC.candidate_indices +
  M.content_verb_indices) -> PARSE-DRIVEN ASSIGNMENT (candidate-to-predicate routing via the decoded head
  chain, V3.assign_candidates_to_predicates_fixed two-pass mechanism) -> ROLE/PATIENT ASSIGNMENT
  (AveragedPerceptron clf.predict AGENT/PATIENT + the 29479 knowledge-gated patient argmax-disambiguation
  when a predicate has >=2 PATIENT-labeled local candidates) -> the learned subcat/valency admissibility
  gate (held REAL and IDENTICAL across every arm in this audit -- it is built ONCE from a REAL
  keepall-evidence pass exactly as V3 does, and is NOT one of the 3 audited stages; it is part of the
  "everything else stays real" scaffolding common to all arms).

ORACLE DESIGN PER STAGE (glass-box; "oracle" = gold-informed override at that ONE stage, REAL everywhere
  else; the gold source is data/gold_mcguffey_lccp_argstruct_v1.json, single-annotator, independent,
  SAME gold/split as 29473/29478/29483):

  (A) CANDIDATE/PREDICATE ENUMERATION ORACLE (`oracle_enum`): force the enumerated candidate set to
      include every gold pos-entry's agent/patient/coref-ref surface word (matched by exact lowercased
      token match against the sentence's OWN tokens -- i.e. this can only recover a gold-argument token
      that IS PRESENT in the sentence text, never invents one), UNION the real ORC.candidate_indices(tagged)
      set. Force the enumerated predicate set to include every token whose lemma_verb matches a gold
      verb-lemma (pos OR nopat) AND whose POS tag starts with VB, UNION the real M.content_verb_indices(
      tagged) set. This directly reuses the SAME "oracle mention gate" concept ORC.candidate_indices_mode
      already implements (mention_mode="oracle": `if low in gold_heads`) -- generalized here to also cover
      predicate-locus misses (the OTHER half of "enumeration," which ORC's existing oracle mode does not
      cover since it assumes find_main_verb's single-predicate frame, not multi-predicate).
      DOWNSTREAM STAYS REAL: routing (parse-driven, oracle_parse=False) and role labeling
      (clf.predict/knowledge-gate, oracle_role=False) still operate on this enumeration-oracle set exactly
      as they do on the real set -- isolating enumeration's OWN end-to-end cost from routing/labeling error.

  (B) PARSE-DRIVEN ASSIGNMENT ORACLE (`oracle_parse`): for each enumerated candidate token, if its
      lowercased surface form matches the agent/patient/ref of a gold pos-entry for SOME enumerated
      predicate in the sentence, route it DIRECTLY to the NEAREST (by token distance) such predicate
      -- bypassing the decoded head-chain walk entirely for that candidate. A candidate with no gold match
      falls back to the REAL two-pass routing (`V3.assign_candidates_to_predicates_fixed` when the
      candidate/predicate sets are the REAL ones; a generalized re-implementation of the SAME two-pass
      algorithm, `route_candidates_generalized`, when enumeration is ALSO oracle so the routing function
      must operate over an explicit candidate/predicate list rather than recomputing them internally).
      This isolates the PARSE stage's OWN contribution: "if every candidate that DOES appear in gold were
      routed to its correct predicate (bypassing whatever the ~0.79-0.81-UAS out-of-domain parser decoded),
      how much end-to-end F1 is recovered?" -- with enumeration and role-labeling unchanged (real).

  (C) ROLE/PATIENT ASSIGNMENT ORACLE (`oracle_role`): for each ROUTED local candidate at a predicate
      (routing stays REAL: whatever the real two-pass parse-driven assignment produced), if the candidate's
      surface word matches that predicate's gold entry's patient -> label PATIENT; if it matches the
      agent/coref-ref -> label AGENT; else fall back to the REAL AveragedPerceptron clf.predict. Because a
      gold-matched patient is unambiguous (exactly one patient per gold pos-entry), the knowledge-gated
      argmax-disambiguation only still fires among any RESIDUAL (non-gold-matched) PATIENT-labeled
      candidates competing with a gold-labeled one -- same mechanism, reused unchanged. This isolates the
      classifier+knowledge-gate stage's OWN contribution given REAL enumeration and REAL routing.

  ALL-ORACLE (`oracle_enum and oracle_parse and oracle_role` simultaneously) = the reader's own
  composition-LOGIC ceiling given perfect candidate/predicate coverage, perfect routing, and perfect role
  labels -- everything downstream of gold matching (the admissibility gate, the "has"/"is" copula
  suppression, the multi-patient tie-break) is UNCHANGED mechanism. If this ceiling is near 1.0, the F1 gap
  is components-bound (fix POS/PARSE/ENUM/ROLE and the reader approaches gold); if it is well below 1.0,
  the reader's OWN assembly logic (the gate, the tuple-emission conditions, the scoring's strict (v_lemma,
  patient) match) is itself a distinct, separate bound -- reported honestly as its own finding.

POS STAGE -- HONEST SCOPE-CUT (NOT separately oracle-run this cycle; approximated + flagged, not swept
  under the rug): no UD/gold-POS treebank exists for McGuffey 19th-c. narrative prose (the UD-EWT gold the
  routing task pointed to is a DIFFERENT corpus -- newswire/web/blog -- used only to TRAIN/eval the
  dependency parser, never to POS-tag or gold-check THIS text). Constructing an independent, stronger POS
  oracle for this exact corpus (a second tagger + a treebank-quality gold pass) is out of scope for an
  INLINE-LOCAL FOREGROUND-bounded diagnostic (compute-proportionality: this is a measurement question, not
  a POS-tagger-improvement claim). Two structural facts bound how much this scope-cut can be hiding:
  (1) the CANDIDATE/PREDICATE ENUMERATION oracle above ALREADY force-includes any gold-argument/verb token
  regardless of its assigned POS tag (a POS-tag error that would have EXCLUDED a gold token from
  enumeration is therefore already counted inside the ENUM row's uplift, not hidden); (2) a POS error that
  corrupts the PARSER's own UPOS-derived features (rather than the enumeration filter) would show up as
  parser mis-decodes, which is bounded by the PARSE oracle row (routing bypasses the decoded arcs entirely
  for gold-matched candidates). What is NOT captured: a POS error's effect on the ROLE classifier's own
  features (ORC.candidate_features uses the PTB tag directly for some cues) for candidates NOT gold-matched
  -- a second-order residual, reported as an explicit caveat, not a zero claim. STANDALONE reference (POS):
  this reader uses NLTK's PerceptronTagger (pretrained averaged perceptron, WSJ-trained; in-domain accuracy
  is the commonly-cited ~0.97 CITED@Petrov/Das/McDonald-era taggers general reputation, not independently
  re-measured on THIS corpus this cycle). The routing task's "substrate ~0.906 vs classical ~0.97" figures
  are CITED@task-prompt (2026-07-23 routing note) -- NOT independently re-verified on disk this cycle (a
  disk grep across notes/ for "0.906" this cycle found zero hits); reported as HYPOTHESIZED/CITED-pending,
  not re-confirmed MEASURED, per the honesty discipline. PARSE STANDALONE reference: ~0.79-0.81 UAS is
  MEASURED (this run reports the trained parser's own uas_dev directly) and separately mapped as a
  DISTRIBUTED/SEMANTIC ceiling (search + valency both HARD_FAIL to break it per notes/reader_space_MAP_
  and_deep_lessons_SESSION_SYNTHESIS_2026-07-23.md line 15) -- MAPPED-BOUND, not obviously closable by more
  engineering on the SAME feature family.

FAIRNESS: SAME reader code (byte-identical reuse of exp_multipred_argstruct_agentfix_kbgate_v3.py's own
  V3.assign_candidates_to_predicates_fixed / V3.build_sel_fn / V3.load_knowledge_table,
  exp_multipred_depparse_argstruct_recall_v2.py's own M.content_verb_indices / M.decode_clause /
  M.train_dep_parser / M._detect_passive / M.predicate_kind / M.build_learned_admissibility,
  exp_oracle_mention_upperbound_reader_v1.py's own ORC.pos_tag_sentence / ORC.candidate_indices /
  ORC.candidate_features / ORC.find_main_verb / ORC.prev_prep / ORC.split_sentences,
  exp_learned_argstruct_parser_lccp_independent_gold_v1.py's own L.lemma_verb / L.score_arm /
  L.load_slice_and_reader / L.load_gold), SAME gold (data/gold_mcguffey_lccp_argstruct_v1.json), SAME
  split (FULL_SLICE = L04/L05/L07/L08/L09/L10/L12, SMOKE_SLICE = L04/L05, verbatim from M/V3). The learned
  admissibility gate is built ONCE (from a REAL keepall-evidence pass) and held FIXED+IDENTICAL across
  every arm -- it is scaffolding shared by all arms, not one of the 3 audited stages, exactly mirroring how
  V3 itself builds and reuses ONE learned_gate_fixed across its own 6 arms.

PRE-REGISTERED SANITY GATE (set BEFORE this run -- this is a MEASUREMENT/diagnostic cell, not a capability
  claim; the "pass/fail" below gates the AUDIT'S OWN VALIDITY, not a substrate capability tier):
  AUDIT_SANITY_OK requires ALL of:
    (1) reproduction: abs(f1_real_baseline - 0.5738) <= 0.02 (CITED_BASELINE_F1, MEASURED@data/
        exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1)
    (2) f1_all_oracle > f1_real_baseline (the mechanism ceiling must exceed the real baseline -- if not,
        the audit's own gold-matching/scoring has a bug, not a substrate finding)
    (3) at least one of {parse, enum, role}-oracle uplift > 0.02 (discriminator-fires: SOME stage must show
        a measurable end-to-end cost, or this diagnostic measured nothing)
  AUDIT_SANITY_FAIL if ANY of:
    abs(f1_real_baseline - 0.5738) > 0.05 (reproduction failed -- reader drifted or wiring bug)
    f1_all_oracle <= f1_real_baseline (oracle mechanism did not even help -- scoring/matching bug)
    max(parse_uplift, enum_uplift, role_uplift) <= 0.0 (vacuous audit -- no stage shows any uplift)
  otherwise MIDDLE_BAND_PARTIAL_SANITY (reproduces + all-oracle improves, but no stage clears the 0.02
  discriminator-fires floor -- report numbers honestly, do not force a tier).

BRAIN-CHECK: N/A for a diagnostic measurement cell (no new mechanism proposed; this audits component
  cost-attribution of an EXISTING reader, the standard ablation-study methodology used throughout
  computational-linguistics pipeline error analysis, e.g. Manning & Schutze error-propagation analysis of
  cascaded NLP pipelines).

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- reuses M.train_dep_parser's existing
  arc-eager training pass (ONE parser trained, ~50-65s at FULL per V3's own docstring) + per-clause greedy
  decode (ms/clause) + per-predicate role classification (existing AveragedPerceptron) + O(candidates) dict
  lookups (routing + gold-string-matching); NO matmul/storage/GPU-batchable primitive. 6 pipeline passes
  over FULL_SLICE (1 keepall-evidence pass to build the shared gate + REAL/PARSE_ORACLE/ENUM_ORACLE/
  ROLE_ORACLE/ALL_ORACLE = 5 scored arms), strictly FEWER passes than V3's own 6-arm-plus-learning-curve
  cell (which itself completes in ~7min per its own docstring) -- estimated wall < 5min total. Storage:
  no_storage. Runtime invariant: glass-box (from-scratch-trained transition parser + curated dict lookups +
  a build-time-authored knowledge dict), NO LLM/network/autograd at inference. Determinism: OMP/MKL/
  OPENBLAS_NUM_THREADS=1, fixed int SEED, no hash()-seeded RNG, sorted()/deterministic dict iteration only.
  LOCAL-ONLY, foreground-to-completion, NOT banked (skunkworks VETs the numbers separately), NO queue_add.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground diagnostic measurement cell, mirroring
  what exp_multipred_argstruct_agentfix_kbgate_v3.py itself scoped down to):
  - arms_differ_verified at smoke gate (hash test over the 5 scored arms' kept-tuple sets)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(REAL) < 0.95)
  - discriminator fires at smoke: at least one oracle stage recovers >=1 additional gold-covered item vs
    REAL at SMOKE_SLICE scale (small-sample WARN permitted, same discipline as V3's own self-test, if the
    smoke slice is too small for a particular stage to bite)
  - deterministic seeding (fixed int SEED; no hash()-seeded RNG; dict/set iteration via sorted() where order
    matters)
  - all numbers tagged MEASURED@ / CITED@ / HYPOTHESIZED@ in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/precision measurement, no HD noise floor); N/A
    multi-seed (deterministic given fixed SEED + the parser's own single-seed training budget, an
    already-accepted scope/wall-time tradeoff per V3/M's own docstrings, not hidden here)
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

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "reader_component_oracle_ablation_audit_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse the reader's OWN modules verbatim (module-scope guarded by `if __name__ == "__main__"` in each,
# so importing does NOT re-run those cells' own experiments).
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M              # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L   # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC               # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2        # noqa: E402
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3            # noqa: E402

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260726

# ---- Pre-registered sanity gate (see docstring) ----------------------------------------------
CITED_BASELINE_F1 = 0.5738  # MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1
REPRO_TOL_OK = 0.02
REPRO_TOL_FAIL = 0.05
DISCRIMINATOR_FLOOR = 0.02
BASELINE_BAND = (0.05, 0.95)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# Gold-lookup helpers (per-sentence gold pos-entries -> oracle heads / verb lemmas / role maps).
# =======================================================================================
def gold_heads_for_rec(rec):
    """Set of every gold pos-entry's agent/patient/coref-ref surface word for this sentence."""
    heads = set()
    for g in rec.get("pos", []):
        heads.add(g["agent"])
        heads.add(g["patient"])
        heads |= set(g["refs"])
    return heads


def gold_verb_lemmas_for_rec(rec):
    return set(rec.get("pos_verbs", set())) | set(rec.get("nopat", set()))


def gold_pos_map_for_rec(rec):
    m = defaultdict(list)
    for g in rec.get("pos", []):
        m[g["v"]].append(g)
    return m


# =======================================================================================
# Generalized REAL routing (byte-identical ALGORITHM to V3.assign_candidates_to_predicates_fixed,
# generalized to an EXPLICIT candidate/predicate list so oracle-enum-injected candidates/predicates can
# also be routed via the REAL two-pass parse-chain walk when oracle_parse=False).
# =======================================================================================
def route_candidates_generalized(tagged, heads, predicates, candidates):
    pred_1based = set(p + 1 for p in predicates)
    n = len(tagged)
    children = defaultdict(list)
    for tok, h in heads.items():
        if h != 0:
            children[h].append(tok)
    route = {}
    for c0 in candidates:
        c1 = c0 + 1
        if c1 in pred_1based:
            continue
        chain = [c1]
        cur = c1
        guard = 0
        found = None
        while guard < n + 2:
            h = heads.get(cur, 0)
            if h == 0:
                break
            if h in pred_1based:
                found = h
                break
            cur = h
            chain.append(cur)
            guard += 1
        if found is None:
            for node in chain:
                for ch in children.get(node, []):
                    if ch in pred_1based:
                        found = ch
                        break
                if found is not None:
                    break
        if found is not None:
            route[c0] = found
    return route


def real_route(tagged, heads, predicates, candidates, enum_is_oracle):
    """enum_is_oracle=False -> byte-identical reuse of V3's OWN routing function (guarantees exact
    reproduction of the real reader). enum_is_oracle=True -> the generalized re-implementation (same
    algorithm) operating over the oracle-expanded candidate/predicate lists."""
    if not enum_is_oracle:
        by_pred = V3.assign_candidates_to_predicates_fixed(tagged, heads, predicates)
        route = {}
        for p1, cs in by_pred.items():
            for c0 in cs:
                route[c0] = p1
        return route
    return route_candidates_generalized(tagged, heads, predicates, candidates)


# =======================================================================================
# ONE clause pass with 3 independent oracle-injection flags (oracle_enum / oracle_parse / oracle_role).
# All-False reproduces V3.clause_predicate_pass_v3 exactly (same gate_fn/sel_fn/assign mechanism).
# =======================================================================================
def clause_predicate_pass_audit(tagged, heads, clf, gate_fn, carried_agent_in, sel_fn, gold_rec,
                                 oracle_enum, oracle_parse, oracle_role):
    lows = [t[1] for t in tagged]
    real_predicates = M.content_verb_indices(tagged)
    real_candidates = ORC.candidate_indices(tagged)
    gold_heads = gold_heads_for_rec(gold_rec) if gold_rec else set()
    gold_verbs = gold_verb_lemmas_for_rec(gold_rec) if gold_rec else set()

    if oracle_enum and gold_rec:
        extra_pred = {i for i, (s, low, pos) in enumerate(tagged)
                      if pos.startswith("VB") and L.lemma_verb(low) in gold_verbs}
        predicates = sorted(set(real_predicates) | extra_pred)
        extra_cand = {i for i, (s, low, pos) in enumerate(tagged) if low in gold_heads}
        candidates = sorted(set(real_candidates) | extra_cand)
    else:
        predicates = real_predicates
        candidates = real_candidates

    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    route = real_route(tagged, heads, predicates, candidates, oracle_enum)

    # gold pos-entry per enumerated predicate occurrence (positional-order alignment per verb lemma;
    # scoring is order-independent over (v_lemma, patient) so misalignment on repeated-lemma sentences,
    # rare in this corpus, cannot inflate the audit -- it can only under-credit an oracle stage).
    gold_pos_map = gold_pos_map_for_rec(gold_rec) if gold_rec else {}
    verb_gold_entry = {}
    if gold_rec:
        occ_idx = defaultdict(int)
        for v0 in predicates:
            vl = L.lemma_verb(tagged[v0][1])
            entries = gold_pos_map.get(vl, [])
            k = occ_idx[vl]
            verb_gold_entry[v0 + 1] = entries[k] if k < len(entries) else None
            occ_idx[vl] += 1

    pred_1based = set(p + 1 for p in predicates)
    by_pred = defaultdict(list)
    for c0 in candidates:
        c1 = c0 + 1
        if c1 in pred_1based:
            continue
        target = None
        if oracle_parse and gold_rec:
            word = tagged[c0][1]
            matches = [p1 for p1, g in verb_gold_entry.items()
                       if g is not None and (word == g["agent"] or word == g["patient"] or word in g["refs"])]
            if matches:
                target = min(matches, key=lambda p1: abs(p1 - c1))
        if target is None:
            target = route.get(c0)
        if target is not None:
            by_pred[target].append(c0)

    out = []
    carried_agent = carried_agent_in
    evidence = {}
    for v0 in predicates:
        v1 = v0 + 1
        low = tagged[v0][1]
        passive = M._detect_passive(tagged, v0, lows)
        local_cand = sorted(by_pred.get(v1, []))
        first_cand = local_cand[0] if local_cand else None
        vl = L.lemma_verb(low)
        g = verb_gold_entry.get(v1) if gold_rec else None
        roles = {}
        for i in local_cand:
            word = tagged[i][1]
            if oracle_role and g is not None and word == g["patient"]:
                roles[i] = "PATIENT"
            elif oracle_role and g is not None and (word == g["agent"] or word in g["refs"]):
                roles[i] = "AGENT"
            else:
                feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
                roles[i] = clf.predict(feats)
        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent
        for i in local_cand:
            if i > v0 and ORC.prev_prep(tagged, i) is None:
                evidence[vl] = True
        kept_patients = patients_local
        if sel_fn is not None and len(patients_local) >= 2:
            def _score(i):
                s = sel_fn(vl, tagged[i][1])
                return -1.0 if s is None else s
            best_i = max(patients_local, key=lambda i: (_score(i), -i))
            kept_patients = [best_i]
        if resolved_agent is not None and kept_patients and low not in ("has", "is"):
            if gate_fn(vl):
                is_main = (v0 == main_idx)
                kind = M.predicate_kind(tagged, v0, is_main)
                for pi in kept_patients:
                    out.append((low, resolved_agent, tagged[pi][1], v0, kind))
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]
    return out, carried_agent, evidence


def build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold, oracle_enum=False, oracle_parse=False,
                     oracle_role=False, collect_evidence=False):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    out = {}
    evidence_total = {}
    for sid in order:
        raw = sent_text[sid]
        carried_agent = None
        tups = []
        gold_rec = gold.get(sid)
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            clause_tups, carried_agent, ev = clause_predicate_pass_audit(
                tagged, heads, clf, gate_fn, carried_agent, sel_fn, gold_rec,
                oracle_enum, oracle_parse, oracle_role)
            tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
            if collect_evidence:
                for lemma, val in ev.items():
                    evidence_total[lemma] = evidence_total.get(lemma, False) or val
        out[sid] = tups
    if collect_evidence:
        return order, out, evidence_total
    return order, out


ARM_FLAGS = {
    "REAL":          dict(oracle_enum=False, oracle_parse=False, oracle_role=False),
    "PARSE_ORACLE":  dict(oracle_enum=False, oracle_parse=True,  oracle_role=False),
    "ENUM_ORACLE":   dict(oracle_enum=True,  oracle_parse=False, oracle_role=False),
    "ROLE_ORACLE":   dict(oracle_enum=False, oracle_parse=False, oracle_role=True),
    "ALL_ORACLE":    dict(oracle_enum=True,  oracle_parse=True,  oracle_role=True),
}


def run_audit(slice_lessons, W, clf, ratings_table, gold):
    sel_fn = V3.build_sel_fn(ratings_table)
    # Shared learned admissibility gate: ONE keepall-evidence pass under the REAL config (byte-identical
    # in spirit to V3's own build), held fixed across all 5 scored arms below (not an audited stage).
    _, _, evidence_real = build_arm_audit(slice_lessons, W, clf, lambda v: True, None, gold,
                                          collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)

    arms = {}
    for name, flags in ARM_FLAGS.items():
        order, kept = build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold, **flags)
        arms[name] = kept

    scored = {}
    for name, kept in arms.items():
        rc, miss, npos, misses = M.recall_ceiling_of(kept, gold)
        sc = L.score_arm(M.to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, n_miss=miss, n_gold_pos=npos, score=sc,
                            kept_hash=M.arm_hash(kept), n_pred=sc["n_pred"])

    real_covered = M.covered_set(arms["REAL"], gold)
    recovered_by_arm = {}
    for name in ("PARSE_ORACLE", "ENUM_ORACLE", "ROLE_ORACLE", "ALL_ORACLE"):
        recovered_by_arm[name] = sorted(M.covered_set(arms[name], gold) - real_covered)

    return dict(arms=arms, scored=scored, recovered_by_arm=recovered_by_arm)


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
    gold, meta = L.load_gold(SMOKE_SLICE)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    assert len(ratings_table) > 100, f"knowledge table suspiciously small: {len(ratings_table)}"

    print("[self-test] training arc-eager parser (smoke budget, reused M code) ...")
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"
    print(f"[self-test] parser trained: {parser_info}")

    res = run_audit(SMOKE_SLICE, W, clf, ratings_table, gold)
    for name in ARM_FLAGS:
        assert name in res["scored"], f"arm {name} missing from smoke run"
    print(f"[self-test] 5-arm audit ran on SMOKE_SLICE: "
          f"{ {k: v['score']['f1'] for k, v in res['scored'].items()} }")

    prec_real = res["scored"]["REAL"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_real < BASELINE_BAND[1], \
        f"REAL precision {prec_real} outside band {BASELINE_BAND}"
    print(f"[self-test] baseline_in_band: precision(REAL)={prec_real} in {BASELINE_BAND}")

    # arms_differ_verified (META_RULE_AF).
    hashes = {name: v["kept_hash"] for name, v in res["scored"].items()}
    assert len(set(hashes.values())) == len(hashes), \
        f"META_RULE_AF VIOLATION: arm hashes collide: {hashes}"
    print(f"[self-test] arms_differ_verified: {hashes}")

    # discriminator fires: at least one oracle arm recovers >=1 additional gold-covered item at smoke
    # scale, OR (small-sample WARN, same discipline V3 itself used) reported honestly.
    any_recovery = any(len(v) > 0 for v in res["recovered_by_arm"].values())
    if not any_recovery:
        print("[self-test] WARN: no oracle arm recovered any additional gold-covered item at SMOKE_SLICE "
              "scale (small-sample; re-verified at FULL scale, which has far more instances) -- reported "
              "honestly, not asserted")
    else:
        print(f"[self-test] discriminator fires: recovered_by_arm counts = "
              f"{ {k: len(v) for k, v in res['recovered_by_arm'].items()} }")

    # determinism: two REAL-arm runs over the same slice + same W are identical.
    order2, kept2 = build_arm_audit(SMOKE_SLICE, W, clf, lambda v: True, None, gold)
    order3, kept3 = build_arm_audit(SMOKE_SLICE, W, clf, lambda v: True, None, gold)
    assert M.arm_hash(kept2) == M.arm_hash(kept3), "non-deterministic REAL-config output across identical runs"
    print("[self-test] deterministic (two identical-config runs produce identical kept-tuple hash)")

    # oracle mechanisms actually override in >=1 case at smoke scale where applicable: spot-check the
    # V3 aux-inversion witness sentence -- PARSE_ORACLE must route "cat" to "rubbed" even under an
    # arc-eager decode that mis-attaches it (reuses V3's own scaffold-free witness sentence).
    raw1 = "The playful cat had rubbed against his mimic castle."
    tagged1 = ORC.pos_tag_sentence(raw1)
    heads1 = M.decode_clause(tagged1, W)
    gold_rec_w = {"pos": [{"v": "rub", "agent": "cat", "patient": "castle", "refs": {"cat"}}],
                  "nopat": set(), "pos_verbs": {"rub"}}
    out_real, _, _ = clause_predicate_pass_audit(tagged1, heads1, clf, lambda v: True, None, None,
                                                  gold_rec_w, False, False, False)
    out_parse_oracle, _, _ = clause_predicate_pass_audit(tagged1, heads1, clf, lambda v: True, None, None,
                                                          gold_rec_w, False, True, False)
    rub_real = {t for t in out_real if t[0] == "rubbed"}
    rub_oracle = {t for t in out_parse_oracle if t[0] == "rubbed"}
    print(f"[self-test] witness (aux-inversion 'rubbed'): REAL_tuples={rub_real} "
          f"PARSE_ORACLE_tuples={rub_oracle}")
    assert any(t[1] == "cat" for t in rub_oracle), \
        f"WITNESS FAIL: PARSE_ORACLE did not route 'cat' to 'rubbed' even with gold agent override; got {rub_oracle}"
    print("[self-test] scaffold-free witness PASS: PARSE_ORACLE recovers the gold agent 'cat' for 'rubbed' "
          "via nearest-gold-match override, independent of the decoded (possibly mis-attached) head chain")

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
    ratings_table = V3.load_knowledge_table()
    gold, meta = L.load_gold(slice_lessons)
    W, parser_info = M.train_dep_parser(run_mode)
    res = run_audit(slice_lessons, W, clf, ratings_table, gold)
    scored = res["scored"]

    f1 = {name: v["score"]["f1"] for name, v in scored.items()}
    prec = {name: v["score"]["precision"] for name, v in scored.items()}
    rec = {name: v["score"]["recall"] for name, v in scored.items()}
    rc = {name: v["recall_ceiling"] for name, v in scored.items()}

    f1_real = f1["REAL"]
    uplift = {name: round(f1[name] - f1_real, 4) for name in ARM_FLAGS if name != "REAL"}

    # Ranked table (biggest end-to-end cost first) over the 3 audited stages (ALL_ORACLE reported
    # separately as the composition-logic ceiling, not ranked alongside single-stage rows).
    stage_rows = [
        dict(component="PARSE (candidate-to-predicate routing)", arm="PARSE_ORACLE",
             standalone_current=parser_info["uas_dev"], standalone_ref_ceiling=0.81,
             standalone_ref_note="MAPPED-BOUND: search(29458)+valency(29460) both HARD_FAIL to break "
                                  "~0.81 UAS; distributed/semantic ceiling per notes/reader_space_MAP_"
                                  "and_deep_lessons_SESSION_SYNTHESIS_2026-07-23.md line 15",
             oracle_uplift=uplift["PARSE_ORACLE"], closable_or_mapped_bound="MAPPED_BOUND"),
        dict(component="CANDIDATE/PREDICATE ENUMERATION", arm="ENUM_ORACLE",
             standalone_current=rc["REAL"], standalone_ref_ceiling=1.0,
             standalone_ref_note="recall_ceiling(REAL) is this stage's OWN standalone upper-bound metric; "
                                  "a candidate-recall push (ad76a3f836d3eaa36) is IN FLIGHT per the routing "
                                  "note -- this row will improve when that lands (flagged, not stale)",
             oracle_uplift=uplift["ENUM_ORACLE"], closable_or_mapped_bound="CLOSABLE_IN_FLIGHT"),
        dict(component="ROLE/PATIENT ASSIGNMENT (clf + knowledge-gate)", arm="ROLE_ORACLE",
             standalone_current=prec["REAL"], standalone_ref_ceiling=None,
             standalone_ref_note="no single closed-form standalone ceiling; AveragedPerceptron clf trained "
                                  "on this same reader's own labeled examples + the 29479 knowledge table "
                                  "(HARD_PASS_SCALED_KNOWLEDGE_HELPS_AT_COVERAGE, acc_scaled=0.6898 vs "
                                  "acc_thin=0.4907 on ITS OWN coverage slice, MEASURED@data/"
                                  "exp_pivot_scaled_seed_knowledge_table_v1/metrics.json)",
             oracle_uplift=uplift["ROLE_ORACLE"], closable_or_mapped_bound="CLOSABLE"),
    ]
    stage_rows.sort(key=lambda r: r["oracle_uplift"], reverse=True)
    top_underperformer = stage_rows[0]["component"] if stage_rows else None

    f1_all_oracle = f1["ALL_ORACLE"]
    logic_ceiling_gap = round(1.0 - f1_all_oracle, 4)
    components_vs_logic = ("COMPONENTS_BOUND: all-oracle F1 is near 1.0 -- fixing POS/PARSE/ENUM/ROLE "
                            "closes nearly the whole gap to gold" if f1_all_oracle >= 0.90 else
                            "MIXED: all-oracle F1 clears real-baseline substantially but is still well "
                            "below 1.0 -- SOME of the gap is components, but the reader's OWN composition "
                            "logic (the admissibility gate / tuple-emission conditions / strict "
                            "(v_lemma,patient) scoring match) is a SEPARATE, non-trivial bound" if
                            f1_all_oracle - f1_real >= 0.10 else
                            "LOGIC_BOUND_SUSPECT: all-oracle F1 barely exceeds real-baseline despite "
                            "perfect inputs -- the reader's OWN composition/decision logic (not the input "
                            "stages) is the dominant bound; investigate the admissibility gate + "
                            "tuple-emission conditions before pushing more on POS/PARSE/ENUM/ROLE")

    repro_diff = abs(f1_real - CITED_BASELINE_F1)
    max_stage_uplift = max(uplift["PARSE_ORACLE"], uplift["ENUM_ORACLE"], uplift["ROLE_ORACLE"])

    sanity_fail_reasons = []
    if repro_diff > REPRO_TOL_FAIL:
        sanity_fail_reasons.append(f"reproduction failed: |f1_real={f1_real} - cited {CITED_BASELINE_F1}| "
                                    f"= {repro_diff} > {REPRO_TOL_FAIL}")
    if f1_all_oracle <= f1_real:
        sanity_fail_reasons.append(f"f1_all_oracle={f1_all_oracle} <= f1_real={f1_real} "
                                    f"(oracle mechanism did not even help -- suspect scoring/matching bug)")
    if max_stage_uplift <= 0.0:
        sanity_fail_reasons.append(f"max stage uplift {max_stage_uplift} <= 0.0 (vacuous audit -- no "
                                    f"stage shows any uplift)")

    sanity_ok = (repro_diff <= REPRO_TOL_OK and f1_all_oracle > f1_real and
                 max_stage_uplift > DISCRIMINATOR_FLOOR)

    if sanity_fail_reasons:
        verdict = "AUDIT_SANITY_FAIL"
        vmsg = ("AUDIT_SANITY_FAIL: " + "; ".join(sanity_fail_reasons) +
                f". f1_real={f1_real} f1_all_oracle={f1_all_oracle} uplifts={uplift}.")
    elif sanity_ok:
        verdict = "AUDIT_SANITY_OK"
        vmsg = (f"AUDIT_SANITY_OK: reproduces cited baseline (f1_real={f1_real} vs cited "
                f"{CITED_BASELINE_F1}, diff={repro_diff}); f1_all_oracle={f1_all_oracle} > f1_real "
                f"(mechanism ceiling gap={round(f1_all_oracle - f1_real, 4)}); top underperformer = "
                f"{top_underperformer} (uplift={stage_rows[0]['oracle_uplift']}). "
                f"{components_vs_logic}")
    else:
        verdict = "MIDDLE_BAND_PARTIAL_SANITY"
        vmsg = (f"MIDDLE_BAND_PARTIAL_SANITY: reproduces (diff={repro_diff}) and all-oracle improves "
                f"(f1_all_oracle={f1_all_oracle} > f1_real={f1_real}) but no single stage clears the "
                f"{DISCRIMINATOR_FLOOR} discriminator-fires floor (max_stage_uplift={max_stage_uplift}). "
                f"Numbers reported honestly below; treat stage ranking as low-confidence at this margin.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: f1_real={f1_real} (cited {CITED_BASELINE_F1}) | "
                 f"uplift PARSE={uplift['PARSE_ORACLE']} ENUM={uplift['ENUM_ORACLE']} "
                 f"ROLE={uplift['ROLE_ORACLE']} ALL_ORACLE_F1={f1_all_oracle} | "
                 f"top_underperformer={top_underperformer} | parser_uas={parser_info['uas_dev']} | "
                 f"recall_ceiling(REAL)={rc['REAL']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["arms"]["REAL"]),
        one_variable="which pipeline stage's output is replaced by gold/oracle (oracle_enum / oracle_parse "
                     "/ oracle_role, one or all-3 flagged), holding the reader's OWN routing/labeling/gate "
                     "mechanism and the shared learned admissibility gate byte-identical across arms",
        bands=dict(CITED_BASELINE_F1=CITED_BASELINE_F1, REPRO_TOL_OK=REPRO_TOL_OK,
                   REPRO_TOL_FAIL=REPRO_TOL_FAIL, DISCRIMINATOR_FLOOR=DISCRIMINATOR_FLOOR),
        f1=f1, precision=prec, recall=rec, recall_ceiling=rc, uplift=uplift,
        ranked_component_table=stage_rows,
        all_oracle_f1=f1_all_oracle, all_oracle_logic_ceiling_gap=logic_ceiling_gap,
        components_vs_logic_bound=components_vs_logic,
        top_underperformer=top_underperformer,
        recovered_by_arm={k: [list(x) for x in v[:40]] for k, v in res["recovered_by_arm"].items()},
        n_recovered_by_arm={k: len(v) for k, v in res["recovered_by_arm"].items()},
        arms={name: dict(f1=v["score"]["f1"], precision=v["score"]["precision"], recall=v["score"]["recall"],
                         recall_ceiling=v["recall_ceiling"], n_pred=v["n_pred"],
                         subcat_fp=v["score"]["subcat_fp"], within_frame_fp=v["score"]["within_frame_fp"],
                         spurious_verb_fp=v["score"]["spurious_verb_fp"], kept_hash=v["kept_hash"])
              for name, v in scored.items()},
        parser_info=parser_info,
        cited_29483=dict(source="data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json",
                         f1=CITED_BASELINE_F1, arm="V3_INTEGRATED",
                         verdict="HARD_FAIL_INTEGRATION_BOUNDED_CEILINGS_COMPOUND (control-arm sub-finding; "
                                 "the V3_INTEGRATED F1=0.5738 number itself is the reader-under-audit here, "
                                 "independent of that cell's OWN must-fail-control verdict outcome)"),
        pos_stage_scope_caveat=(
            "POS was NOT independently oracle-swapped this cycle (no UD/gold-POS treebank exists for "
            "McGuffey narrative prose; the UD-EWT gold trains/evals the PARSER only, a different corpus). "
            "Enumeration-relevant POS errors ARE captured inside the ENUM_ORACLE row above (it force-"
            "includes gold tokens regardless of POS tag); parser-feature-corrupting POS errors are bounded "
            "by the PARSE_ORACLE row (routing bypasses decoded arcs for gold-matched candidates). NOT "
            "captured: a POS error's effect on the ROLE classifier's own features for candidates NOT "
            "gold-matched (second-order residual, not measured this cycle). Standalone reference figures "
            "'substrate ~0.906 vs classical ~0.97' are CITED@task-prompt (2026-07-23 routing note), NOT "
            "independently re-verified on disk this cycle (grep across notes/ for '0.906' found zero hits)."
        ),
        scope_caveat=(
            "Parser trained on UD-EWT (newswire/web/blog) via a from-scratch dynamic-oracle arc-eager model "
            "at a FOREGROUND-bounded training budget, byte-identical reuse of M/V3's own training code; "
            "out-of-domain transfer to 19th-c. McGuffey narrative prose is the SAME untested transfer V3/M "
            "already flagged. The knowledge table (29479) is LLM-self-built (residual leakage-adjacent risk "
            "per that cell's own scope caveat); an independent-KB replication is the flagged rigor "
            "follow-up. The ENUM_ORACLE row's current numbers will change once the in-flight candidate-"
            "recall push (ad76a3f836d3eaa36) lands -- flagged, not stale-claimed. This is a MEASUREMENT/"
            "diagnostic cell, NOT a capability claim; CLAIM-VET-pending; strategic read = HYPOTHESIS "
            "pending landed-VET (skunkworks VETs the numbers separately per the routing task's contract)."
        ),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("ranked_component_table:", json.dumps(stage_rows, indent=1))
    print("arms:", json.dumps(metrics["arms"], indent=1))
    print("all_oracle_f1:", f1_all_oracle, "logic_ceiling_gap:", logic_ceiling_gap)
    print("components_vs_logic_bound:", components_vs_logic)
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
