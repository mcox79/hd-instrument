"""ROLES chain-grade DRIVE-2: BRAIN-FAITHFUL SUBCAT-FRAME-GATED WORD-ORDER patient mapping as a STRUCTURAL
precision/recall lever on the best current who-did-what reader (V3_INTEGRATED; landed end-to-end
patient-F1=0.5738, MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1).

WHY DRIVE-1 FAILED (precise diagnosis, MEASURED@data/exp_reader_role_wordorder_valency_v1/metrics.json):
  The +0.0391 ROLE_ORACLE headroom is 6 gold (verb,patient) pairs the perceptron mislabels. DISK-READ the
  roleora_recovered set: build/blockhouse (clean OSV, 1/6), rub/castle, knock/castles, see/child, meet/boys,
  find/boy (canonical post-verbal, 5/6). The brain assigns canonical transitive patients by WORD-ORDER +
  VERB ARGUMENT STRUCTURE (post-verbal object of a transitive = patient; animacy SECONDARY). The perceptron
  over-weights animacy (routes animate post-verbal nouns -> AGENT), FIGHTING word order. Drive-1's two levers
  were the WRONG mechanism: CANONICAL_BLUNT forced first-post-verbal-core -> PATIENT UN-GATED by frame, so it
  STOLE ditransitive/light-verb RECIPIENTS (regressed hold/hands, show/way, give/hour, give/books, show/seeds;
  net F1 0.5738 -> 0.5312, within_frame_fp 6->11). FRONTED_OSV only touched fronted-object clauses (recovered
  only build/blockhouse; net -0.0081). NEITHER built the brain's SUBCAT-FRAME-GATED word-order mapping.

THE BRAIN-FAITHFUL MECHANISM THIS CELL BUILDS (role_frame_reassign; glass-box; WORD-IDENTITY-FREE):
  Retrieve the verb's argument-structure FRAME STRUCTURALLY from the parse, THEN map by word order GATED BY
  FRAME. Frame retrieval uses ONLY the parse (count of post-verbal CORE candidates -- a routed local candidate
  with index > verb and NO governing preposition) + the reader's OWN learned admissibility gate (does this
  verb admit a patient at all):
    TRANSITIVE frame (exactly 1 post-verbal core): that core -> PATIENT, OVERRIDING the perceptron's animacy
      bias (recovers the 5/6 canonical animate/inanimate post-verbal mislabels).
    DITRANSITIVE frame (>=2 post-verbal core = double object): the LAST core (theme) -> PATIENT; the FIRST
      core (recipient) is NOT the patient (AVOIDS drive-1's recipient over-steal). A give-X-to/for-Y PP
      recipient is already EXCLUDED from the core set by prev_prep, so its theme is the single core -> handled
      by the transitive branch correctly.
  No selectional / animacy / token-identity KNOWLEDGE anywhere (position + governing-preposition function-word
  + passive + the reader's own learned frame gate only). Selectional knowledge is proven REDUNDANT for this
  reader (CITED@29491) and fair-control-forbidden.

ARMS (five; BASE / ROLE_ORACLE reuse the AUDIT's OWN byte-identical machinery; CANONICAL_BLUNT reuses DRIVE-1's
  OWN build_arm_wo byte-identically -> cross-checks the 0.5312 wall):
  BASE            = AUDIT REAL arm (== V3_INTEGRATED). P1 FAIRNESS ANCHOR (reproduces F1=0.5738 byte-identical).
  FRAME_GATED     = BASE + subcat-frame-gated word-order mapping (HEADLINE; the mechanism drive-1 did not build).
  FRAME_ANTI      = same frame trigger, DIRECTION REVERSED (ditransitive: recipient->PATIENT; transitive:
                    pre-verbal subject->PATIENT, post-verbal core->AGENT). P2 SCRAMBLE-MUST-FIRE control: if
                    the post-verbal-theme DIRECTION carries the signal, this arm must be clearly worse.
  CANONICAL_BLUNT = drive-1's UN-GATED post-verbal forcing (first-post-core->PATIENT for every admissible verb).
                    THE ABLATION: FRAME_GATED vs CANONICAL_BLUNT isolates the FRAME EFFECT (theme-vs-first-core
                    selection + recipient-protection). Reuses WO.build_arm_wo -> reproduces the 0.5312 wall.
  ROLE_ORACLE     = AUDIT oracle_role arm on the SAME parser weights = the +0.0391 CEILING (F1=0.6129).

KEEP-DIGGING MANDATE (USER 07-23): if FRAME_GATED does NOT close the +0.0391, this cell does a DEEP PER-ITEM
  AUTOPSY (function autopsy_roleora_headroom) of EACH roleora_recovered item: the parser's tokens, the frame
  detected, the post/pre core sets, the perceptron role of the gold-patient token, the final role after the
  override, whether it was emitted, and the mechanism gap (parser? frame detection? residual classifier /
  selectional / gate override?). A failure = our FIDELITY is still wrong, NOT a real bound.

MEASURED (per arm, SAME independent LCCP gold / split as audit/V3): F1, precision, recall, recall_ceiling,
  subcat/within_frame/spurious FP; n_recovered / n_regressed vs BASE; fraction of ROLE_ORACLE's recovered set
  FRAME_GATED also gets; FRACTION OF THE +0.0391 GAP CLOSED = (F1(FRAME_GATED)-F1(BASE))/(F1(ROLE_ORACLE)-F1(BASE)).

PRE-REGISTERED BANDS (set BEFORE the FRAME_GATED full run; grounded on audit MEASURED anchors f1_REAL=0.5738,
  f1_ROLE_ORACLE=0.6129, gap=0.0391):
  HARD_PASS_STRUCTURAL_FRAME_LIFT requires ALL of:
    (P1)  abs(F1(BASE)-0.5738) <= 0.02                                  # base reproduces V3
    (a)   F1(FRAME_GATED) >= F1(BASE) + 0.0196                          # closes >= 50% of the 0.0391 gap
    (b)   recall(FRAME_GATED) >= recall(BASE) - 0.005                   # no recall regression
    (c)   precision(FRAME_GATED) >= precision(BASE)                     # no precision regression
    (d)   F1(FRAME_GATED) >= F1(CANONICAL_BLUNT) + 0.01                 # frame-gating beats un-gated (ablation)
    (P2)  F1(FRAME_ANTI) <= F1(BASE) AND F1(FRAME_GATED) >= F1(FRAME_ANTI) + 0.01   # direction carries signal
  HARD_FAIL_STRUCTURAL_FRAME_NULL if ANY of:
    F1(FRAME_GATED) <= F1(BASE)                                         # no lift (mechanism null on this corpus)
    recall(FRAME_GATED) < recall(BASE) - 0.02                          # regressed recall
    F1(FRAME_ANTI) >= F1(FRAME_GATED)                                   # anti-direction not worse
    abs(F1(BASE)-0.5738) > 0.02                                         # P1 broke
  MIDDLE_BAND_PARTIAL_STRUCTURAL_LIFT otherwise (genuine but partial gap-closure, controls fire, no
  HARD_FAIL trigger) -- the honest 'drove toward the ceiling, name the residual wall from the autopsy' outcome.

FAIRNESS: SAME reader / gold (data/gold_mcguffey_lccp_argstruct_v1.json) / split (FULL_SLICE=
  L04/L05/L07/L08/L09/L10/L12, SMOKE_SLICE=L04/L05) as audit / V3 / drive-1. BASE and ROLE_ORACLE are
  byte-identical reuse of AUDIT.build_arm_audit; CANONICAL_BLUNT is byte-identical reuse of WO.build_arm_wo;
  the shared admissibility gate is built ONCE (from a pass-through-gate evidence pass, exactly as drive-1) and
  held identical; the pre-existing >=2-patient selectional argmax is held CONSTANT (NOT my variable). ONE
  variable = the subcat-frame-gated override. No selectional/animacy knowledge added. No cross-base comparison.

COMPUTE ARCHITECTURE: class (b) sequential-CPU -- ONE arc-eager parser train (~68s FULL, MEASURED@drive-1
  parser_info) + ms/clause decode + per-predicate perceptron + O(cand) position/prep lookups. NO matmul/GPU/
  storage. 5 scored arms + 1 evidence pass + 1 autopsy trace pass. drive-1 FULL elapsed 204.88s MEASURED ->
  est wall < 4min. Determinism: OMP/MKL/OPENBLAS=1, fixed int SEED, no hash()-seeded RNG, sorted() iteration.
  Storage: no_storage. Runtime invariant: glass-box, NO LLM/network/autograd. LOCAL-ONLY foreground-to-
  completion, NOT banked (skunkworks VETs separately), NO queue_add.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash over the 5 arms; small-sample WARN permitted)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASE) < 0.95)
  - P1 reproduction self-test: override-disabled pass == AUDIT REAL arm (hash-identical); BLUNT via WO reused
  - discriminator fires at smoke: FRAME_GATED recovers >=1 gold item BASE misses (WARN if small-sample)
  - scaffold-free witness: direct unit-check of role_frame_reassign on a constructed transitive clause
    ("the girl saw the child" -> child->PATIENT overriding animacy) AND a ditransitive ("give the boy books"
    -> books(theme)->PATIENT, boy(recipient) NOT patient); anti control reverses both
  - deterministic seeding (fixed int SEED; no hash()-seeded RNG; sorted() where order matters)
  - progress_logging: line_buffered_stdout (sys.stdout.reconfigure) -- FULL est < 4min < 30min so not gated,
    but enabled defensively
  - all numbers tagged MEASURED@ / CITED@ in this docstring
  - N/A: KGStore (no KG); CRLB (discrete count/precision, no HD noise floor); multi-seed (single-seed parser
    budget, accepted per M/V3/audit/drive-1); GPU-batching (sequential parse, no matmul)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "reader_role_frame_gated_valency_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_multipred_depparse_argstruct_recall_v2 as M              # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L   # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC               # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2        # noqa: E402
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3             # noqa: E402
from experiments import exp_reader_component_oracle_ablation_audit_v1 as AUDIT       # noqa: E402
from experiments import exp_reader_role_wordorder_valency_v1 as WO                   # noqa: E402  (drive-1; reuse only)

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260726

# ---- Pre-registered bands (set BEFORE the FRAME_GATED full run) ------------------------------
CITED_AUDIT_F1_REAL = 0.5738         # MEASURED@data/exp_reader_component_oracle_ablation_audit_v1/metrics.json:f1.REAL
CITED_AUDIT_F1_ROLE_ORACLE = 0.6129  # MEASURED@ same:f1.ROLE_ORACLE
CITED_ROLE_GAP = 0.0391              # MEASURED@ same:uplift.ROLE_ORACLE
P1_REPRO_TOL = 0.02
HP_GAP_CLOSE_FRAC = 0.50
HP_F1_MIN_LIFT = round(CITED_ROLE_GAP * HP_GAP_CLOSE_FRAC, 4)   # 0.0196
HP_RECALL_TOL = 0.005
HP_ANTI_MARGIN = 0.01
HP_ABLATION_MARGIN = 0.01
HF_RECALL_REGRESS = 0.02
BASELINE_BAND = (0.05, 0.95)
EXPECTED_N_ARMS = 5
HEADLINE = "FRAME_GATED"


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# SUBCAT-FRAME-GATED word-order role mapping. Mutates `roles` in place. WORD-IDENTITY-FREE.
#   Frame retrieved STRUCTURALLY (count of post-verbal core candidates) + the reader's OWN learned
#   admissibility gate. anti=True reverses the frame->role DIRECTION (P2 control).
# Returns a trace dict (frame label + the constituents) for the per-item autopsy.
# =======================================================================================
def role_frame_reassign(roles, local_cand, tagged, v0, passive, gate_fn, anti):
    tr = {"frame": None, "post_core": [], "pre_core": [], "pat": None, "ag": None, "applied": False}
    if passive:
        tr["frame"] = "passive_skip"  # non-canonical: parietal reanalysis, out of scope
        return tr
    post_core = sorted(i for i in local_cand if i > v0 and ORC.prev_prep(tagged, i) is None)
    pre_core = sorted(i for i in local_cand if i < v0 and ORC.prev_prep(tagged, i) is None)
    tr["post_core"] = post_core
    tr["pre_core"] = pre_core
    if not post_core:
        tr["frame"] = "no_postverbal_core"  # fronted/OSV/intransitive -> frame override N/A in this cell
        return tr
    vl = L.lemma_verb(tagged[v0][1])
    if not gate_fn(vl):
        tr["frame"] = "gate_blocked"  # learned frame gate: verb admits no patient
        return tr

    # ---- STRUCTURAL FRAME RETRIEVAL + word-order->role map (canonical direction) ----
    if len(post_core) >= 2:
        frame = "ditransitive"
        pat = post_core[-1]   # theme (LAST core)
    else:
        frame = "transitive"
        pat = post_core[0]    # the single post-verbal object
    ag = pre_core[-1] if pre_core else None  # nearest pre-verbal core = subject

    if anti:
        # P2 anti-direction control: map the WRONG constituent to PATIENT.
        if frame == "ditransitive":
            pat = post_core[0]                 # recipient (the drive-1 over-steal) -> PATIENT (wrong)
        else:
            if pre_core:
                pat = pre_core[-1]             # transitive: subject -> PATIENT (wrong)
                ag = post_core[0]              # object -> AGENT (wrong)
            # else degenerate: no pre-verbal core to swap onto; leave transitive theme (control inert here)
        frame = frame + "_anti"

    tr["frame"] = frame
    tr["pat"] = pat
    tr["ag"] = ag
    roles[pat] = "PATIENT"
    for j in local_cand:
        if j != pat and roles.get(j) == "PATIENT":
            roles[j] = "NONE"   # frame determines THE patient (also un-steals a ditransitive recipient)
    if ag is not None and ag != pat:
        roles[ag] = "AGENT"
    tr["applied"] = True
    return tr


# =======================================================================================
# One clause pass. Mirrors AUDIT.clause_predicate_pass_audit's REAL (all-oracle-False) path plus the single
# frame override. override=None reproduces the AUDIT REAL arm EXACTLY (P1 self-test asserts hash-identity via
# the byte-identical WO.build_arm_wo(override=None) path -- this function is only ever called WITH an override).
# trace_sink: optional dict {sid: [per-predicate trace, ...]} populated when sid in trace_sids.
# =======================================================================================
def clause_predicate_pass_frame(sid, tagged, heads, clf, gate_fn, carried_agent_in, sel_fn, anti,
                                trace_sink=None, trace_sids=None):
    lows = [t[1] for t in tagged]
    predicates = M.content_verb_indices(tagged)
    candidates = ORC.candidate_indices(tagged)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)
    route = AUDIT.real_route(tagged, heads, predicates, candidates, False)

    pred_1based = set(p + 1 for p in predicates)
    by_pred = defaultdict(list)
    for c0 in candidates:
        c1 = c0 + 1
        if c1 in pred_1based:
            continue
        target = route.get(c0)
        if target is not None:
            by_pred[target].append(c0)

    tracing = (trace_sink is not None and trace_sids is not None and sid in trace_sids)
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
        roles = {}
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
            roles[i] = clf.predict(feats)
        perceptron_roles = dict(roles) if tracing else None

        tr = role_frame_reassign(roles, local_cand, tagged, v0, passive, gate_fn, anti)

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
        emitted = None
        if resolved_agent is not None and kept_patients and low not in ("has", "is"):
            if gate_fn(vl):
                is_main = (v0 == main_idx)
                kind = M.predicate_kind(tagged, v0, is_main)
                emitted = []
                for pi in kept_patients:
                    out.append((low, resolved_agent, tagged[pi][1], v0, kind))
                    emitted.append(tagged[pi][1])
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]

        if tracing:
            def _w(idxs):
                return [tagged[i][1] for i in idxs]
            trace_sink.setdefault(sid, []).append(dict(
                sid=sid, verb=vl, verb_low=low, verb_idx=v0, passive=passive,
                frame=tr["frame"], gate_admits=bool(gate_fn(vl)),
                local_cand=_w(local_cand), post_core=_w(tr["post_core"]), pre_core=_w(tr["pre_core"]),
                perceptron_roles={tagged[i][1]: perceptron_roles[i] for i in local_cand},
                final_roles={tagged[i][1]: roles[i] for i in local_cand},
                override_pat=(tagged[tr["pat"]][1] if tr["pat"] is not None else None),
                override_ag=(tagged[tr["ag"]][1] if tr["ag"] is not None else None),
                resolved_agent=resolved_agent,
                kept_patients=[tagged[i][1] for i in kept_patients],
                emitted_patients=emitted))
    return out, carried_agent, evidence


def build_arm_frame(slice_lessons, W, clf, gate_fn, sel_fn, anti, trace_sink=None, trace_sids=None):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    out = {}
    for sid in order:
        raw = sent_text[sid]
        carried_agent = None
        tups = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            clause_tups, carried_agent, _ = clause_predicate_pass_frame(
                sid, tagged, heads, clf, gate_fn, carried_agent, sel_fn, anti,
                trace_sink=trace_sink, trace_sids=trace_sids)
            tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
        out[sid] = tups
    return order, out


# =======================================================================================
# Deep per-item autopsy of the ROLE_ORACLE headroom set (the KEEP-DIGGING deliverable).
# For each (sid, gold_verb, gold_patient) that ROLE_ORACLE recovers but BASE misses: replay the FRAME_GATED
# clause trace and report the mechanism state at that item -- so a failure names the SPECIFIC fidelity gap
# (parser did/didn't route it; frame detected; perceptron role of the gold-patient token; final role; emitted).
# =======================================================================================
def autopsy_roleora_headroom(slice_lessons, W, clf, gate_fn, sel_fn, roleora_recovered, head_recovered):
    trace_sids = set(sid for (sid, v, p) in roleora_recovered)
    trace_sink = {}
    build_arm_frame(slice_lessons, W, clf, gate_fn, sel_fn, anti=False,
                    trace_sink=trace_sink, trace_sids=trace_sids)
    head_set = set((sid, v, p) for (sid, v, p) in head_recovered)
    report = []
    for (sid, gverb, gpat) in roleora_recovered:
        recovered_by_frame = (sid, gverb, gpat) in head_set
        preds = trace_sink.get(sid, [])
        matches = [pr for pr in preds if pr["verb"] == gverb]
        item = dict(sid=sid, gold_verb=gverb, gold_patient=gpat,
                    recovered_by_frame_gated=recovered_by_frame)
        if not matches:
            item["diagnosis"] = ("NO_PREDICATE_TRACE: FRAME_GATED produced no predicate with lemma "
                                 f"{gverb!r} in {sid} -> upstream (parser routing / predicate detection / "
                                 "clause segmentation) never presented this verb. Not a role-assignment gap.")
            item["predicate_traces"] = []
            report.append(item)
            continue
        pdiag = []
        for pr in matches:
            gpat_in_local = gpat in pr["local_cand"]
            gpat_in_post = gpat in pr["post_core"]
            perc_role = pr["perceptron_roles"].get(gpat)
            fin_role = pr["final_roles"].get(gpat)
            emitted_ok = pr["emitted_patients"] is not None and gpat in (pr["emitted_patients"] or [])
            if not gpat_in_local:
                why = ("ROUTING_GAP: gold patient not among this predicate's routed local candidates "
                       f"(local={pr['local_cand']}) -> parser routing / mention gate dropped it.")
            elif not gpat_in_post:
                why = ("NON_POSTVERBAL: gold patient is a routed candidate but NOT a post-verbal core "
                       f"(post_core={pr['post_core']}, pre_core={pr['pre_core']}) -> frame trigger cannot "
                       "target it (fronted/OSV/prep-governed -> out of this cell's transitive/ditransitive scope).")
            elif pr["frame"] == "gate_blocked":
                why = ("GATE_BLOCKED: post-verbal core present but the learned admissibility gate_fn says the "
                       "verb admits no patient -> frame retrieval suppressed the override.")
            elif pr["frame"] == "ditransitive" and pr["override_pat"] != gpat:
                why = (f"DITRANSITIVE_THEME_MISPICK: frame=ditransitive picked theme={pr['override_pat']!r} "
                       f"(post_core={pr['post_core']}) but gold patient is {gpat!r} -> the last-core theme "
                       "heuristic chose the wrong core.")
            elif fin_role != "PATIENT":
                why = (f"OVERRIDE_NOT_APPLIED: post-verbal core, frame={pr['frame']}, but gold-patient final "
                       f"role={fin_role!r} (perceptron={perc_role!r}) -> override did not set it PATIENT.")
            elif not emitted_ok:
                why = (f"POST_OVERRIDE_FILTER: gold patient set PATIENT (frame={pr['frame']}) but not emitted "
                       f"(kept_patients={pr['kept_patients']}, emitted={pr['emitted_patients']}) -> the >=2-"
                       "patient selectional argmax OR the emit gate dropped it.")
            else:
                why = (f"EMITTED_OK: frame={pr['frame']}, perceptron={perc_role!r} -> PATIENT; emitted "
                       f"{pr['emitted_patients']} (recovered by FRAME_GATED = {recovered_by_frame}).")
            pdiag.append(dict(frame=pr["frame"], gate_admits=pr["gate_admits"],
                              post_core=pr["post_core"], pre_core=pr["pre_core"],
                              perceptron_role_of_gold_patient=perc_role, final_role_of_gold_patient=fin_role,
                              override_pat=pr["override_pat"], emitted_patients=pr["emitted_patients"],
                              diagnosis=why))
        item["predicate_traces"] = pdiag
        report.append(item)
    return report


# =======================================================================================
# Full 5-arm experiment.
# =======================================================================================
def run_experiment(slice_lessons, W, clf, ratings_table, gold, with_autopsy=True):
    sel_fn = V3.build_sel_fn(ratings_table)
    # Gate built EXACTLY as drive-1: pass-through-gate evidence pass via WO.build_arm_wo -> byte-identical gate.
    _, _, evidence_real = WO.build_arm_wo(slice_lessons, W, clf, lambda v: True, None, override=None,
                                          collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)

    arms = {}
    _, base_kept = AUDIT.build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold,
                                         oracle_enum=False, oracle_parse=False, oracle_role=False)
    _, roleora_kept = AUDIT.build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold,
                                            oracle_enum=False, oracle_parse=False, oracle_role=True)
    _, blunt_kept = WO.build_arm_wo(slice_lessons, W, clf, gate_fn, sel_fn,
                                    override=dict(mode="canonical", anti=False))
    _, frame_kept = build_arm_frame(slice_lessons, W, clf, gate_fn, sel_fn, anti=False)
    _, anti_kept = build_arm_frame(slice_lessons, W, clf, gate_fn, sel_fn, anti=True)

    arms["BASE"] = base_kept
    arms["FRAME_GATED"] = frame_kept
    arms["FRAME_ANTI"] = anti_kept
    arms["CANONICAL_BLUNT"] = blunt_kept
    arms["ROLE_ORACLE"] = roleora_kept

    scored = {}
    for name, kept in arms.items():
        rc, miss, npos, misses = M.recall_ceiling_of(kept, gold)
        sc = L.score_arm(M.to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, n_miss=miss, n_gold_pos=npos, score=sc,
                            kept_hash=M.arm_hash(kept), n_pred=sc["n_pred"])

    base_covered = M.covered_set(arms["BASE"], gold)
    roleora_recovered = sorted(M.covered_set(arms["ROLE_ORACLE"], gold) - base_covered)
    head_recovered = sorted(M.covered_set(arms[HEADLINE], gold) - base_covered)
    head_regressed = sorted(base_covered - M.covered_set(arms[HEADLINE], gold))
    head_of_roleora = sorted(set(head_recovered) & set(roleora_recovered))
    blunt_recovered = sorted(M.covered_set(arms["CANONICAL_BLUNT"], gold) - base_covered)
    blunt_regressed = sorted(base_covered - M.covered_set(arms["CANONICAL_BLUNT"], gold))

    autopsy = None
    if with_autopsy:
        autopsy = autopsy_roleora_headroom(slice_lessons, W, clf, gate_fn, sel_fn,
                                           roleora_recovered, head_recovered)

    return dict(arms=arms, scored=scored, gate_fn=gate_fn,
                roleora_recovered=roleora_recovered, head_recovered=head_recovered,
                head_regressed=head_regressed, head_of_roleora=head_of_roleora,
                blunt_recovered=blunt_recovered, blunt_regressed=blunt_regressed,
                autopsy=autopsy)


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
    sel_fn = V3.build_sel_fn(ratings_table)

    print("[self-test] training arc-eager parser (smoke budget, reused M code) ...")
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"
    print(f"[self-test] parser trained: {parser_info}")

    # (P1 REPRODUCTION) BASE via AUDIT REAL must equal WO.build_arm_wo(override=None) (both reproduce V3).
    _, _, evidence_real = WO.build_arm_wo(SMOKE_SLICE, W, clf, lambda v: True, None, override=None,
                                          collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)
    _, audit_base = AUDIT.build_arm_audit(SMOKE_SLICE, W, clf, gate_fn, sel_fn, gold,
                                          oracle_enum=False, oracle_parse=False, oracle_role=False)
    _, wo_base = WO.build_arm_wo(SMOKE_SLICE, W, clf, gate_fn, sel_fn, override=None)
    assert M.arm_hash(audit_base) == M.arm_hash(wo_base), \
        (f"P1 REPRODUCTION FAIL: AUDIT REAL != WO override-disabled "
         f"(audit={M.arm_hash(audit_base)} wo={M.arm_hash(wo_base)})")
    print(f"[self-test] P1 reproduction: AUDIT REAL == WO override-disabled (hash {M.arm_hash(audit_base)})")

    res = run_experiment(SMOKE_SLICE, W, clf, ratings_table, gold, with_autopsy=True)
    for name in ("BASE", "FRAME_GATED", "FRAME_ANTI", "CANONICAL_BLUNT", "ROLE_ORACLE"):
        assert name in res["scored"], f"arm {name} missing from smoke run"
    f1s = {k: v["score"]["f1"] for k, v in res["scored"].items()}
    print(f"[self-test] 5-arm run on SMOKE_SLICE: f1={f1s}")

    prec_base = res["scored"]["BASE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], \
        f"BASE precision {prec_base} outside band {BASELINE_BAND}"
    print(f"[self-test] baseline_in_band: precision(BASE)={prec_base}")

    hashes = {name: v["kept_hash"] for name, v in res["scored"].items()}
    print(f"[self-test] kept_hashes: {hashes}")
    if len(set(hashes.values())) != len(hashes):
        print("[self-test] WARN: >=2 arms share a kept_hash at SMOKE_SLICE scale (small-sample; likely no "
              "frame-eligible discriminating predicate in L04/L05) -- FULL slice is the load-bearing "
              "arms-differ check")

    # scaffold-free witness A: TRANSITIVE clause "the girl saw the child" -> child->PATIENT overriding animacy.
    tagged_t = [("The", "the", "DT"), ("girl", "girl", "NN"), ("saw", "saw", "VBD"),
                ("the", "the", "DT"), ("child", "child", "NN"), (".", ".", ".")]
    v0t = 2  # saw
    local_t = [1, 4]  # girl (pre-verbal subject), child (post-verbal object)
    assert ORC.prev_prep(tagged_t, 4) is None, "witness: 'child' must be a core (no governing prep)"
    roles_t = {1: "AGENT", 4: "AGENT"}  # perceptron animacy-mislabels the animate post-verbal 'child' AGENT
    tr_t = role_frame_reassign(roles_t, local_t, tagged_t, v0t, False, lambda v: True, anti=False)
    assert tr_t["frame"] == "transitive", f"witness: expected transitive frame, got {tr_t['frame']}"
    assert roles_t[4] == "PATIENT" and roles_t[1] == "AGENT", \
        f"WITNESS-A FAIL: transitive did not map post-verbal 'child'->PATIENT subj 'girl'->AGENT; got {roles_t}"
    roles_ta = {1: "AGENT", 4: "AGENT"}
    role_frame_reassign(roles_ta, local_t, tagged_t, v0t, False, lambda v: True, anti=True)
    assert roles_ta[1] == "PATIENT" and roles_ta[4] == "AGENT", \
        f"WITNESS-A anti FAIL: anti did not reverse (subj->PATIENT obj->AGENT); got {roles_ta}"
    print(f"[self-test] witness A transitive: canonical={roles_t} anti={roles_ta} (frame={tr_t['frame']})")

    # scaffold-free witness B: DITRANSITIVE "give the boy books" -> books(theme)->PATIENT; boy(recipient) NOT.
    tagged_d = [("give", "give", "VB"), ("the", "the", "DT"), ("boy", "boy", "NN"),
                ("books", "books", "NNS"), (".", ".", ".")]
    v0d = 0  # give
    local_d = [2, 3]  # boy (recipient, first post-core), books (theme, last post-core)
    assert ORC.prev_prep(tagged_d, 2) is None and ORC.prev_prep(tagged_d, 3) is None, \
        "witness: 'boy' and 'books' must both be core (no governing prep)"
    roles_d = {2: "PATIENT", 3: "NONE"}  # perceptron mis-steals the recipient 'boy' as PATIENT
    tr_d = role_frame_reassign(roles_d, local_d, tagged_d, v0d, False, lambda v: True, anti=False)
    assert tr_d["frame"] == "ditransitive", f"witness: expected ditransitive frame, got {tr_d['frame']}"
    assert roles_d[3] == "PATIENT" and roles_d[2] != "PATIENT", \
        f"WITNESS-B FAIL: ditransitive did not map theme 'books'->PATIENT + un-steal 'boy'; got {roles_d}"
    roles_da = {2: "NONE", 3: "PATIENT"}
    role_frame_reassign(roles_da, local_d, tagged_d, v0d, False, lambda v: True, anti=True)
    assert roles_da[2] == "PATIENT" and roles_da[3] != "PATIENT", \
        f"WITNESS-B anti FAIL: anti did not map recipient 'boy'->PATIENT; got {roles_da}"
    print(f"[self-test] witness B ditransitive: canonical={roles_d} anti={roles_da} (frame={tr_d['frame']})")

    # ablation is live: CANONICAL_BLUNT (WO) differs from FRAME_GATED on the ditransitive witness direction.
    assert tr_d["frame"] == "ditransitive" and tr_d["pat"] == 3, \
        "ablation witness: FRAME_GATED must pick the LAST core (theme) on a ditransitive, unlike BLUNT (first)"
    print("[self-test] ablation live: FRAME_GATED picks ditransitive theme (last core); BLUNT picks first core")

    if not res["head_recovered"]:
        print(f"[self-test] WARN: {HEADLINE} recovered 0 gold items BASE misses at SMOKE_SLICE scale "
              "(small-sample; canonical cases are sparse in L04/L05; FULL slice is load-bearing)")
    else:
        print(f"[self-test] discriminator fires: {HEADLINE} recovers {len(res['head_recovered'])} gold "
              f"items BASE misses: {res['head_recovered']}")

    assert res["autopsy"] is not None, "autopsy did not run in smoke"
    print(f"[self-test] autopsy produced {len(res['autopsy'])} roleora-headroom item reports")

    _, k2 = build_arm_frame(SMOKE_SLICE, W, clf, gate_fn, sel_fn, anti=False)
    _, k3 = build_arm_frame(SMOKE_SLICE, W, clf, gate_fn, sel_fn, anti=False)
    assert M.arm_hash(k2) == M.arm_hash(k3), "non-deterministic FRAME_GATED output across identical runs"
    print("[self-test] deterministic (two FRAME_GATED runs produce identical kept-tuple hash)")

    print("[self-test] PASS")
    return 0


# =======================================================================================
# Verdict.
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    _write_start_marker(output_dir, run_mode, expected_n_units=EXPECTED_N_ARMS)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    gold, meta = L.load_gold(slice_lessons)
    W, parser_info = M.train_dep_parser(run_mode)
    res = run_experiment(slice_lessons, W, clf, ratings_table, gold, with_autopsy=True)
    scored = res["scored"]

    f1 = {n: v["score"]["f1"] for n, v in scored.items()}
    prec = {n: v["score"]["precision"] for n, v in scored.items()}
    rec = {n: v["score"]["recall"] for n, v in scored.items()}
    rc = {n: v["recall_ceiling"] for n, v in scored.items()}

    f1_base = f1["BASE"]
    f1_head = f1[HEADLINE]
    f1_anti = f1["FRAME_ANTI"]
    f1_blunt = f1["CANONICAL_BLUNT"]
    f1_oracle = f1["ROLE_ORACLE"]

    role_gap = round(f1_oracle - f1_base, 4)
    head_lift = round(f1_head - f1_base, 4)
    gap_closed_frac = round(head_lift / role_gap, 4) if role_gap > 1e-9 else None

    p1_ok = abs(f1_base - CITED_AUDIT_F1_REAL) <= P1_REPRO_TOL

    hard_fail_reasons = []
    if not p1_ok:
        hard_fail_reasons.append(f"P1 reproduction broke: |F1(BASE)={f1_base} - {CITED_AUDIT_F1_REAL}| "
                                  f"> {P1_REPRO_TOL}")
    if f1_head <= f1_base:
        hard_fail_reasons.append(f"F1({HEADLINE})={f1_head} <= F1(BASE)={f1_base} (structural lever null)")
    if rec[HEADLINE] < rec["BASE"] - HF_RECALL_REGRESS:
        hard_fail_reasons.append(f"recall({HEADLINE})={rec[HEADLINE]} < recall(BASE)={rec['BASE']} - "
                                  f"{HF_RECALL_REGRESS} (recall regressed)")
    if f1_anti >= f1_head:
        hard_fail_reasons.append(f"F1(FRAME_ANTI)={f1_anti} >= F1({HEADLINE})={f1_head} (P2 control not "
                                  f"worse -> lift is not word-order-DIRECTION specific)")

    hard_pass_conditions = dict(
        p1_reproduces=p1_ok,
        closes_half_gap=(head_lift >= HP_F1_MIN_LIFT),
        no_recall_regress=(rec[HEADLINE] >= rec["BASE"] - HP_RECALL_TOL),
        precision_holds=(prec[HEADLINE] >= prec["BASE"]),
        beats_ungated_ablation=(f1_head >= f1_blunt + HP_ABLATION_MARGIN),
        anti_direction_fails=(f1_anti <= f1_base and f1_head >= f1_anti + HP_ANTI_MARGIN),
    )

    if hard_fail_reasons:
        verdict = "HARD_FAIL_STRUCTURAL_FRAME_NULL"
        vmsg = ("HARD_FAIL: " + "; ".join(hard_fail_reasons) +
                f". F1 BASE={f1_base} {HEADLINE}={f1_head} FRAME_ANTI={f1_anti} CANONICAL_BLUNT={f1_blunt} "
                f"ROLE_ORACLE={f1_oracle}. precision BASE={prec['BASE']} {HEADLINE}={prec[HEADLINE]}. recall "
                f"BASE={rec['BASE']} {HEADLINE}={rec[HEADLINE]}. gap_closed_frac={gap_closed_frac}. "
                f"n_head_recovered={len(res['head_recovered'])} n_head_regressed={len(res['head_regressed'])}. "
                "SEE autopsy[] for the per-item mechanism gap (KEEP-DIGGING deliverable).")
    elif all(hard_pass_conditions.values()):
        verdict = "HARD_PASS_STRUCTURAL_FRAME_LIFT"
        vmsg = (f"HARD_PASS: subcat-frame-gated word-order mapping lifts F1 BASE={f1_base} -> {HEADLINE}="
                f"{f1_head} (+{head_lift}, closes {gap_closed_frac} of the +{role_gap} ROLE_ORACLE gap); "
                f"recall {rec['BASE']}->{rec[HEADLINE]}; precision {prec['BASE']}->{prec[HEADLINE]}; beats "
                f"un-gated CANONICAL_BLUNT={f1_blunt}; P2 anti-direction fails (FRAME_ANTI={f1_anti}). "
                "Brain-faithful frame-gated STRUCTURAL lever, no selectional/animacy knowledge.")
    else:
        verdict = "MIDDLE_BAND_PARTIAL_STRUCTURAL_LIFT"
        failing = [k for k, v in hard_pass_conditions.items() if not v]
        vmsg = (f"MIDDLE_BAND: no HARD_FAIL trigger, but not all HARD_PASS held (failing: {failing}). "
                f"F1 BASE={f1_base} -> {HEADLINE}={f1_head} (+{head_lift}, closes {gap_closed_frac} of the "
                f"+{role_gap} gap); recall {rec['BASE']}->{rec[HEADLINE]}; precision "
                f"{prec['BASE']}->{prec[HEADLINE]}; FRAME_ANTI={f1_anti}; CANONICAL_BLUNT={f1_blunt}. "
                f"n_head_recovered={len(res['head_recovered'])} n_head_regressed={len(res['head_regressed'])}. "
                "SEE autopsy[] for the per-item residual wall (KEEP-DIGGING deliverable).")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: f1 BASE={f1_base} {HEADLINE}={f1_head} (+{head_lift}) FRAME_ANTI={f1_anti} "
                 f"CANONICAL_BLUNT={f1_blunt} ROLE_ORACLE={f1_oracle} | gap_closed_frac={gap_closed_frac} "
                 f"(role_gap={role_gap}) | precision BASE={prec['BASE']} {HEADLINE}={prec[HEADLINE]} | "
                 f"recall BASE={rec['BASE']} {HEADLINE}={rec[HEADLINE]} | parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["arms"]["BASE"]), headline_arm=HEADLINE,
        one_variable="role_frame_reassign: a WORD-IDENTITY-FREE subcat-frame-gated override; retrieves the "
                     "argument-structure frame structurally (count of post-verbal core candidates + the "
                     "reader's own learned admissibility gate) then maps by word order: TRANSITIVE (1 post-"
                     "verbal core) -> that core=PATIENT overriding animacy; DITRANSITIVE (>=2 post-verbal "
                     "core) -> LAST core (theme)=PATIENT, first core (recipient) NOT patient. "
                     "parser/perceptron/routing/admissibility-gate/>=2-patient selectional argmax held "
                     "constant across arms",
        bands=dict(CITED_AUDIT_F1_REAL=CITED_AUDIT_F1_REAL,
                   CITED_AUDIT_F1_ROLE_ORACLE=CITED_AUDIT_F1_ROLE_ORACLE, CITED_ROLE_GAP=CITED_ROLE_GAP,
                   P1_REPRO_TOL=P1_REPRO_TOL, HP_GAP_CLOSE_FRAC=HP_GAP_CLOSE_FRAC,
                   HP_F1_MIN_LIFT=HP_F1_MIN_LIFT, HP_RECALL_TOL=HP_RECALL_TOL, HP_ANTI_MARGIN=HP_ANTI_MARGIN,
                   HP_ABLATION_MARGIN=HP_ABLATION_MARGIN, HF_RECALL_REGRESS=HF_RECALL_REGRESS),
        f1=f1, precision=prec, recall=rec, recall_ceiling=rc,
        role_gap=role_gap, head_lift=head_lift, gap_closed_frac=gap_closed_frac, p1_reproduces=p1_ok,
        hard_pass_conditions=hard_pass_conditions, hard_fail_reasons=hard_fail_reasons,
        n_roleora_recovered=len(res["roleora_recovered"]),
        roleora_recovered=[list(x) for x in res["roleora_recovered"][:40]],
        n_head_recovered=len(res["head_recovered"]),
        head_recovered=[list(x) for x in res["head_recovered"][:40]],
        n_head_regressed=len(res["head_regressed"]),
        head_regressed=[list(x) for x in res["head_regressed"][:40]],
        n_head_of_roleora=len(res["head_of_roleora"]),
        head_of_roleora=[list(x) for x in res["head_of_roleora"][:40]],
        n_blunt_recovered=len(res["blunt_recovered"]),
        blunt_recovered=[list(x) for x in res["blunt_recovered"][:40]],
        n_blunt_regressed=len(res["blunt_regressed"]),
        blunt_regressed=[list(x) for x in res["blunt_regressed"][:40]],
        roleora_headroom_coverage=(round(len(res["head_of_roleora"]) / len(res["roleora_recovered"]), 4)
                                   if res["roleora_recovered"] else None),
        autopsy=res["autopsy"],
        arms={name: dict(recall_ceiling=v["recall_ceiling"], n_miss=v["n_miss"],
                         n_gold_pos=v["n_gold_pos"], precision=v["score"]["precision"],
                         recall=v["score"]["recall"], f1=v["score"]["f1"], n_pred=v["n_pred"],
                         subcat_fp=v["score"]["subcat_fp"], within_frame_fp=v["score"]["within_frame_fp"],
                         spurious_verb_fp=v["score"]["spurious_verb_fp"], kept_hash=v["kept_hash"])
              for name, v in scored.items()},
        parser_info=parser_info,
        cited_audit=dict(source="data/exp_reader_component_oracle_ablation_audit_v1/metrics.json",
                         f1_real=CITED_AUDIT_F1_REAL, f1_role_oracle=CITED_AUDIT_F1_ROLE_ORACLE,
                         role_uplift=CITED_ROLE_GAP),
        drive1_note="Drive-1 (exp_reader_role_wordorder_valency_v1) HARD_FAILed: CANONICAL_BLUNT stole "
                    "ditransitive/light-verb recipients (F1->0.5312), FRONTED_OSV only touched fronted "
                    "clauses (F1 0.5657, -0.0081). This v2 builds the SUBCAT-FRAME-GATED mapping drive-1 "
                    "did not: transitive post-verbal core->PATIENT (overriding animacy) but ditransitive "
                    "theme (last core)->PATIENT with the recipient protected. CANONICAL_BLUNT here reuses "
                    "drive-1's OWN build_arm_wo -> the ablation FRAME_GATED vs CANONICAL_BLUNT isolates "
                    "the frame effect.",
        brain_check="thematic-role assignment dissociable from parsing (aphasia IFG vs temporo-parietal); "
                    "retrieve verb argument-structure frame then map constituents GATED BY word-order "
                    "canonicity; parietal reanalysis for non-canonical/passive only. Lever = frame-gated "
                    "word-order mapping (structural), NOT selectional/animacy (redundant per 29491).",
        scope_caveat=("Parser trained on UD-EWT out-of-domain to McGuffey (same untested transfer already "
                      "flagged). Frame retrieval uses the STRUCTURAL post-verbal-core count + the reader's "
                      "learned admissibility gate; light-verb vs transitive single-object clauses are "
                      "structurally identical (both 1 post-verbal core) so the transitive branch cannot "
                      "distinguish them without the verb's lexical subcat frame -- this is the anticipated "
                      "residual (see autopsy + subcat_fp). Passive/fronted-OSV left to the perceptron/coref "
                      "(out of this cell's canonical scope; build/blockhouse OSV is drive-1's FRONTED arm). "
                      "MEASUREMENT cell, NOT banked; CLAIM-VET-pending; strategic read = HYPOTHESIS pending "
                      "landed-VET (skunkworks VETs separately)."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"])
    print("verdict:", verdict)
    print("verdict_msg:", vmsg)
    print("arms:", json.dumps(metrics["arms"], indent=1))
    print("gap_closed_frac:", gap_closed_frac, "role_gap:", role_gap, "head_lift:", head_lift)
    print("head_recovered:", res["head_recovered"])
    print("head_regressed:", res["head_regressed"])
    print("roleora_recovered:", res["roleora_recovered"])
    print("AUTOPSY (roleora headroom per-item):")
    print(json.dumps(res["autopsy"], indent=1))
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
