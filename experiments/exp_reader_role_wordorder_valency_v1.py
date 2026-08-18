"""ROLE/PATIENT ASSIGNMENT chain-grade: BRAIN-FAITHFUL WORD-ORDER-AWARE role reassignment as a STRUCTURAL
precision lever on the best current who-did-what reader (V3_INTEGRATED arm of
exp_multipred_argstruct_agentfix_kbgate_v3.py; landed end-to-end patient-F1=0.5738,
MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1).

TARGET (component oracle-ablation audit, MEASURED@data/exp_reader_component_oracle_ablation_audit_v1/
  metrics.json): swapping the ROLE/PATIENT assignment stage for gold (ROLE_ORACLE) lifts end-to-end F1 by
  +0.0391 (F1 REAL=0.5738 -> ROLE_ORACLE=0.6129; precision 0.4861 -> 0.5135; recall 0.70 -> 0.76). DISK-READ
  FP split (MEASURED@ audit:arms): REAL subcat=35 within_frame=6 spurious=33; ROLE_ORACLE subcat=35
  within_frame=4 spurious=33. => the +0.0391 is RECALL-DOMINATED (6 gold (verb,patient) pairs the
  word-identity-free perceptron mislabels) + a small within-frame precision slice.

TWO CONVERGENT STEERS (both adopted; neither a prescribed number):
  (1) BRAIN (Director deep-dive 2026-07-23): thematic-role assignment is a DISSOCIABLE stage from parsing
      (aphasia double-dissociation IFG/frontal vs temporo-parietal/angular). Sequence parse -> grammatical-
      role -> retrieve VERB ARGUMENT STRUCTURE -> map constituents GATED BY WORD-ORDER CANONICITY; parietal
      REANALYSIS fires ONLY for NON-CANONICAL/passive order. Lever = word-order/valency STRUCTURE, NOT
      selectional/animacy (secondary in brain; already REDUNDANT for this reader, CITED@29491).
  (2) EMPIRICAL SCOUR (Director, 2026-07-23): of the reader's 25 residual misses, 11 are ROLE failures from
      FRONTED/OSV word order biasing the perceptron's position features toward AGENT (e.g. "the blockhouse
      he was building" -> 'blockhouse' fronted pre-verbal patient mislabeled AGENT). Dominant v3 regression
      cause = AGENT_ROUTING_DROP=8. The lever is: make role assignment WORD-ORDER-AWARE so it does not
      OVER-ASSIGN AGENT on non-canonical (OSV/fronted) order. Vetted FALSE-STARTS (NOT retried here):
      learned-classifier relabel (-0.019 fair), 5 selectional-injection schemes (all failed scramble-fire,
      CITED@29491 +4), explicit by-agent/PP-patient markers (0 material on McGuffey), object-typicality /
      selectional-coherence / event-outcome-density (all HARD_FAIL, do-not-retest).

FIRST-RUN RESULT ON THE BLUNT LEVER (this cell, run 1, MEASURED@this metrics.json history / reported to
  Director): a BLANKET canonical override (force first post-verbal core -> PATIENT for every non-passive
  valency-admitting predicate) NET-HURT: F1 0.5738 -> 0.5312 (-0.0426), precision 0.4861 -> 0.4359,
  within_frame_fp 6 -> 11. wo_regressed = hold/hands, show/way, give/hour, give/books, show/seeds -- all
  DITRANSITIVE / LIGHT-VERB clauses where the blunt rule steals the patient label onto the recipient/first
  post-verbal NP. Kept in THIS cell as the CANONICAL_BLUNT ablation arm (documents the wall). The valency
  gate never bit (gate_fn True for all these verbs) so NOVALENCY==CANONICAL_BLUNT was dropped.

HEADLINE MECHANISM (glass-box; WORD-IDENTITY-FREE; the NARROW fronted/OSV reanalysis both steers converge
  on): role_wordorder_reassign(mode="fronted"). For a non-passive predicate whose routed local candidates
  include >=2 PRE-VERBAL CORE candidates (a routed local candidate with index < verb index and NO governing
  preposition) AND NO post-verbal core candidate (the object has moved to the front -> clean OSV signature):
    PATIENT <- the FARTHEST pre-verbal core (the fronted object); demote any other perceptron-PATIENT.
    AGENT   <- the NEAREST pre-verbal core (the true subject).
  This corrects exactly the perceptron's animacy/position-driven over-assignment of AGENT to a fronted
  pre-verbal patient, and CANNOT fire on canonical clauses (one pre-verbal subject) or ditransitives (their
  objects are post-verbal) -> it leaves the CANONICAL_BLUNT regressions untouched. No token identity, no
  animacy, no selectional table: position + preposition-governance + the passive flag only.

ARMS (five; BASE and ROLE_ORACLE reuse the audit's OWN byte-identical machinery):
  BASE               = audit REAL arm (== V3_INTEGRATED). P1 FAIRNESS ANCHOR (reproduces F1=0.5738).
  FRONTED_OSV        = BASE + the narrow fronted/OSV pre-verbal reassignment (HEADLINE).
  FRONTED_ANTI       = same trigger but the two pre-verbal roles SWAPPED (nearest->PATIENT, farthest->AGENT).
                       P2 SCRAMBLE-MUST-FIRE control: if the DIRECTION (fronted=patient) carries the signal,
                       this arm must be clearly worse than FRONTED_OSV and give no gain over BASE.
  CANONICAL_BLUNT    = the blunt canonical post-verbal forcing (run-1 net-negative), kept as a documented
                       ablation showing why the blanket lever fails (the ditransitive over-attach wall).
  ROLE_ORACLE        = audit oracle_role arm on the SAME parser weights = the +0.0391 CEILING.

MEASURED (per arm, SAME independent LCCP gold / same split as audit/V3): F1, precision, recall,
  recall_ceiling, subcat/within_frame/spurious FP (L.score_arm byte-identical reuse); n_recovered /
  n_regressed vs BASE (covered-set diffs); fraction of ROLE_ORACLE's recovered set FRONTED_OSV also gets;
  FRACTION OF THE +0.0391 GAP CLOSED = (F1(FRONTED_OSV)-F1(BASE)) / (F1(ROLE_ORACLE)-F1(BASE)).

PRE-REGISTERED BANDS (set BEFORE the FRONTED_OSV full run; grounded on audit MEASURED anchors f1_REAL=0.5738,
  f1_ROLE_ORACLE=0.6129, gap=0.0391):
  HARD_PASS_STRUCTURAL_ROLE_LIFT requires ALL of:
    (P1)  abs(F1(BASE)-0.5738) <= 0.02
    (a)   F1(FRONTED_OSV) >= F1(BASE) + 0.0196            # closes >= 50% of the 0.0391 gap
    (b)   recall(FRONTED_OSV) >= recall(BASE) - 0.005     # no recall regression
    (c)   precision(FRONTED_OSV) >= precision(BASE)       # no precision regression
    (P2)  F1(FRONTED_ANTI) <= F1(BASE) AND F1(FRONTED_OSV) >= F1(FRONTED_ANTI) + 0.01   # direction carries signal
  HARD_FAIL_STRUCTURAL_ROLE_NULL if ANY of:
    F1(FRONTED_OSV) <= F1(BASE)                           # no lift (mechanism null on this corpus)
    recall(FRONTED_OSV) < recall(BASE) - 0.02             # regressed recall
    F1(FRONTED_ANTI) >= F1(FRONTED_OSV)                   # anti-direction not worse -> not direction-specific
    abs(F1(BASE)-0.5738) > 0.02                           # P1 broke
  MIDDLE_BAND_PARTIAL_STRUCTURAL_LIFT otherwise (genuine but partial gap-closure, controls fire, no
  regression) -- the honest 'drove to the ceiling, name the wall' outcome.

FAIRNESS: SAME reader / gold (data/gold_mcguffey_lccp_argstruct_v1.json) / split (FULL_SLICE=
  L04/L05/L07/L08/L09/L10/L12, SMOKE_SLICE=L04/L05) as audit and V3. BASE and ROLE_ORACLE are byte-identical
  reuse of the audit's build_arm_audit; the shared admissibility gate is built ONCE and held identical; the
  pre-existing >=2-patient selectional argmax is held CONSTANT (NOT my variable). ONE variable = the
  structural override. No selectional/animacy knowledge added. No cross-base comparison.

COMPUTE ARCHITECTURE: class (b) sequential-CPU -- ONE arc-eager parser train (~50-65s FULL) + ms/clause
  decode + per-predicate perceptron + O(cand) position/prep lookups. NO matmul/GPU/storage. 5 scored arms +
  1 gate pass, FEWER passes than the audit (122.94s MEASURED@audit:elapsed_s) -> est wall < 3.5min.
  Determinism: OMP/MKL/OPENBLAS=1, fixed int SEED, no hash()-seeded RNG, sorted() iteration. Storage:
  no_storage. Runtime invariant: glass-box, NO LLM/network/autograd. LOCAL-ONLY foreground-to-completion,
  NOT banked (skunkworks VETs separately), NO queue_add.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash over the 5 arms; small-sample WARN permitted)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASE) < 0.95)
  - P1 reproduction self-test: override-disabled clause pass == audit REAL arm (hash-identical)
  - discriminator fires at smoke: FRONTED_OSV recovers >=1 gold item BASE misses (WARN if small-sample)
  - scaffold-free witness: direct unit-check of role_wordorder_reassign on a constructed OSV clause
    ("the blockhouse he was building") -> farthest pre-verbal core 'blockhouse'->PATIENT, nearest 'he'->
    AGENT; the ANTI control swaps them (control live)
  - deterministic seeding (fixed int SEED; no hash()-seeded RNG; sorted() where order matters)
  - all numbers tagged MEASURED@ / CITED@ in this docstring
  - N/A: KGStore (no KG); CRLB (discrete count/precision, no HD noise floor); multi-seed (single-seed parser
    budget, accepted per M/V3/audit)
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

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "reader_role_wordorder_valency_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_multipred_depparse_argstruct_recall_v2 as M              # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L   # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC               # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2        # noqa: E402
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3            # noqa: E402
from experiments import exp_reader_component_oracle_ablation_audit_v1 as AUDIT      # noqa: E402

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260726

# ---- Pre-registered bands (set BEFORE the FRONTED_OSV full run) ------------------------------
CITED_AUDIT_F1_REAL = 0.5738         # MEASURED@data/exp_reader_component_oracle_ablation_audit_v1/metrics.json:f1.REAL
CITED_AUDIT_F1_ROLE_ORACLE = 0.6129  # MEASURED@ same:f1.ROLE_ORACLE
CITED_ROLE_GAP = 0.0391              # MEASURED@ same:uplift.ROLE_ORACLE
P1_REPRO_TOL = 0.02
HP_GAP_CLOSE_FRAC = 0.50
HP_F1_MIN_LIFT = round(CITED_ROLE_GAP * HP_GAP_CLOSE_FRAC, 4)   # 0.0196
HP_RECALL_TOL = 0.005
HP_ANTI_MARGIN = 0.01
HF_RECALL_REGRESS = 0.02
BASELINE_BAND = (0.05, 0.95)
EXPECTED_N_ARMS = 5
HEADLINE = "FRONTED_OSV"


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# STRUCTURAL word-order-aware role reassignment. Mutates `roles` in place. WORD-IDENTITY-FREE.
#   mode="fronted"  : the narrow OSV reanalysis (HEADLINE) -- see module docstring.
#   mode="canonical": blunt post-verbal forcing (documented net-negative ablation from run 1).
#   anti=True       : direction control (roles swapped) -> P2 must fail.
# =======================================================================================
def role_wordorder_reassign(roles, local_cand, tagged, v0, vl, passive, gate_fn, mode, anti):
    if passive:
        return  # non-canonical: left to the perceptron/coref (brain: parietal reanalysis, out of scope)
    post_core = sorted(i for i in local_cand if i > v0 and ORC.prev_prep(tagged, i) is None)
    pre_core = sorted(i for i in local_cand if i < v0 and ORC.prev_prep(tagged, i) is None)

    if mode == "fronted":
        # Clean OSV signature: a fronted object + its subject both pre-verbal, and no post-verbal core
        # (the object moved to the front). Fires narrowly -> cannot touch canonical/ditransitive clauses.
        if len(pre_core) >= 2 and not post_core:
            far = pre_core[0]       # fronted object (farthest left of verb)
            near = pre_core[-1]     # subject (nearest the verb)
            if anti:
                far, near = near, far
            roles[far] = "PATIENT"
            for j in local_cand:
                if j != far and roles.get(j) == "PATIENT":
                    roles[j] = "NONE"
            roles[near] = "AGENT"
        return

    if mode == "canonical":
        # Blunt canonical post-verbal forcing (run-1 net-negative; kept as documented ablation).
        if not gate_fn(vl):
            return
        if not anti:
            pat_i = post_core[0] if post_core else None
            ag_i = pre_core[-1] if pre_core else None
        else:
            pat_i = pre_core[-1] if pre_core else None
            ag_i = post_core[0] if post_core else None
        if pat_i is not None:
            roles[pat_i] = "PATIENT"
            for j in local_cand:
                if j != pat_i and roles.get(j) == "PATIENT":
                    roles[j] = "NONE"
        if ag_i is not None and ag_i != pat_i:
            roles[ag_i] = "AGENT"


# =======================================================================================
# One clause pass. override=None reproduces the audit REAL arm EXACTLY (self-test asserts hash-identity).
# Body mirrors AUDIT.clause_predicate_pass_audit's REAL (all-oracle-False) path plus the single override.
# =======================================================================================
def clause_predicate_pass_wo(tagged, heads, clf, gate_fn, carried_agent_in, sel_fn, override):
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

        if override is not None:
            role_wordorder_reassign(roles, local_cand, tagged, v0, vl, passive, gate_fn,
                                    override["mode"], override["anti"])

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


def build_arm_wo(slice_lessons, W, clf, gate_fn, sel_fn, override, collect_evidence=False):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    out = {}
    evidence_total = {}
    for sid in order:
        raw = sent_text[sid]
        carried_agent = None
        tups = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            clause_tups, carried_agent, ev = clause_predicate_pass_wo(
                tagged, heads, clf, gate_fn, carried_agent, sel_fn, override)
            tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
            if collect_evidence:
                for lemma, val in ev.items():
                    evidence_total[lemma] = evidence_total.get(lemma, False) or val
        out[sid] = tups
    if collect_evidence:
        return order, out, evidence_total
    return order, out


WO_OVERRIDES = {
    "FRONTED_OSV":     dict(mode="fronted",   anti=False),
    "FRONTED_ANTI":    dict(mode="fronted",   anti=True),
    "CANONICAL_BLUNT": dict(mode="canonical", anti=False),
}


def run_experiment(slice_lessons, W, clf, ratings_table, gold):
    sel_fn = V3.build_sel_fn(ratings_table)
    _, _, evidence_real = build_arm_wo(slice_lessons, W, clf, lambda v: True, None, override=None,
                                       collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)

    arms = {}
    _, base_kept = AUDIT.build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold,
                                         oracle_enum=False, oracle_parse=False, oracle_role=False)
    _, roleora_kept = AUDIT.build_arm_audit(slice_lessons, W, clf, gate_fn, sel_fn, gold,
                                            oracle_enum=False, oracle_parse=False, oracle_role=True)
    arms["BASE"] = base_kept
    arms["ROLE_ORACLE"] = roleora_kept
    for name, ov in WO_OVERRIDES.items():
        _, kept = build_arm_wo(slice_lessons, W, clf, gate_fn, sel_fn, override=ov)
        arms[name] = kept

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

    return dict(arms=arms, scored=scored, gate_fn=gate_fn,
                roleora_recovered=roleora_recovered, head_recovered=head_recovered,
                head_regressed=head_regressed, head_of_roleora=head_of_roleora)


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

    # (P1 REPRODUCTION) override-disabled clause pass MUST equal the audit REAL arm bit-for-bit.
    _, _, evidence_real = build_arm_wo(SMOKE_SLICE, W, clf, lambda v: True, None, override=None,
                                       collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_real)
    _, mine_base = build_arm_wo(SMOKE_SLICE, W, clf, gate_fn, sel_fn, override=None)
    _, audit_base = AUDIT.build_arm_audit(SMOKE_SLICE, W, clf, gate_fn, sel_fn, gold,
                                          oracle_enum=False, oracle_parse=False, oracle_role=False)
    assert M.arm_hash(mine_base) == M.arm_hash(audit_base), \
        (f"P1 REPRODUCTION FAIL: override-disabled pass != audit REAL arm "
         f"(mine={M.arm_hash(mine_base)} audit={M.arm_hash(audit_base)})")
    print(f"[self-test] P1 reproduction: override-disabled pass == audit REAL arm (hash {M.arm_hash(mine_base)})")

    res = run_experiment(SMOKE_SLICE, W, clf, ratings_table, gold)
    for name in ("BASE", "FRONTED_OSV", "FRONTED_ANTI", "CANONICAL_BLUNT", "ROLE_ORACLE"):
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
              "OSV-eligible predicate in L04/L05) -- FULL slice is the load-bearing arms-differ check")

    # scaffold-free witness: direct unit-check on a constructed OSV clause "the blockhouse he was building".
    tagged_w = [("The", "the", "DT"), ("blockhouse", "blockhouse", "NN"), ("he", "he", "PRP"),
                ("was", "was", "VBD"), ("building", "building", "VBG"), (".", ".", ".")]
    v0w = 4  # "building"
    local_w = [1, 2]  # blockhouse (fronted object, farther), he (subject, nearer)
    assert ORC.prev_prep(tagged_w, 1) is None and ORC.prev_prep(tagged_w, 2) is None, \
        "witness setup: both pre-verbal candidates must be core (no governing prep)"
    roles_c = {1: "AGENT", 2: "AGENT"}  # perceptron over-assigns AGENT to the fronted patient
    role_wordorder_reassign(roles_c, local_w, tagged_w, v0w, "build", False, lambda v: True,
                            mode="fronted", anti=False)
    roles_a = {1: "AGENT", 2: "AGENT"}
    role_wordorder_reassign(roles_a, local_w, tagged_w, v0w, "build", False, lambda v: True,
                            mode="fronted", anti=True)
    print(f"[self-test] witness OSV 'blockhouse'(far)/'he'(near): canonical roles={roles_c} anti={roles_a}")
    assert roles_c[1] == "PATIENT" and roles_c[2] == "AGENT", \
        f"WITNESS FAIL: fronted reanalysis did not map far->PATIENT near->AGENT; got {roles_c}"
    assert roles_a[1] == "AGENT" and roles_a[2] == "PATIENT", \
        f"WITNESS FAIL: anti control did not swap the roles (control not live); got {roles_a}"
    print("[self-test] scaffold-free witness PASS: fronted maps far pre-verbal core 'blockhouse'->PATIENT, "
          "near 'he'->AGENT; anti control swaps them (P2 live and opposite)")

    if not res["head_recovered"]:
        print(f"[self-test] WARN: {HEADLINE} recovered 0 gold items BASE misses at SMOKE_SLICE scale "
              "(small-sample; OSV cases are sparse; FULL slice is the load-bearing measurement)")
    else:
        print(f"[self-test] discriminator fires: {HEADLINE} recovers {len(res['head_recovered'])} gold "
              f"items BASE misses: {res['head_recovered']}")

    _, k2 = build_arm_wo(SMOKE_SLICE, W, clf, gate_fn, sel_fn, override=None)
    _, k3 = build_arm_wo(SMOKE_SLICE, W, clf, gate_fn, sel_fn, override=None)
    assert M.arm_hash(k2) == M.arm_hash(k3), "non-deterministic BASE output across identical runs"
    print("[self-test] deterministic (two BASE runs produce identical kept-tuple hash)")

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
    res = run_experiment(slice_lessons, W, clf, ratings_table, gold)
    scored = res["scored"]

    f1 = {n: v["score"]["f1"] for n, v in scored.items()}
    prec = {n: v["score"]["precision"] for n, v in scored.items()}
    rec = {n: v["score"]["recall"] for n, v in scored.items()}
    rc = {n: v["recall_ceiling"] for n, v in scored.items()}

    f1_base = f1["BASE"]
    f1_head = f1[HEADLINE]
    f1_anti = f1["FRONTED_ANTI"]
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
        hard_fail_reasons.append(f"F1(FRONTED_ANTI)={f1_anti} >= F1({HEADLINE})={f1_head} (P2 control not "
                                  f"worse -> lift is not word-order-DIRECTION specific)")

    hard_pass_conditions = dict(
        p1_reproduces=p1_ok,
        closes_half_gap=(head_lift >= HP_F1_MIN_LIFT),
        no_recall_regress=(rec[HEADLINE] >= rec["BASE"] - HP_RECALL_TOL),
        precision_holds=(prec[HEADLINE] >= prec["BASE"]),
        anti_direction_fails=(f1_anti <= f1_base and f1_head >= f1_anti + HP_ANTI_MARGIN),
    )

    if hard_fail_reasons:
        verdict = "HARD_FAIL_STRUCTURAL_ROLE_NULL"
        vmsg = ("HARD_FAIL: " + "; ".join(hard_fail_reasons) +
                f". F1 BASE={f1_base} {HEADLINE}={f1_head} FRONTED_ANTI={f1_anti} CANONICAL_BLUNT={f1_blunt} "
                f"ROLE_ORACLE={f1_oracle}. precision BASE={prec['BASE']} {HEADLINE}={prec[HEADLINE]}. recall "
                f"BASE={rec['BASE']} {HEADLINE}={rec[HEADLINE]}. gap_closed_frac={gap_closed_frac}. "
                f"n_head_recovered={len(res['head_recovered'])} n_head_regressed={len(res['head_regressed'])}.")
    elif all(hard_pass_conditions.values()):
        verdict = "HARD_PASS_STRUCTURAL_ROLE_LIFT"
        vmsg = (f"HARD_PASS: fronted/OSV word-order reanalysis lifts F1 BASE={f1_base} -> {HEADLINE}={f1_head} "
                f"(+{head_lift}, closes {gap_closed_frac} of the +{role_gap} ROLE_ORACLE gap); recall "
                f"{rec['BASE']}->{rec[HEADLINE]}; precision {prec['BASE']}->{prec[HEADLINE]}; P2 anti "
                f"direction fails (FRONTED_ANTI={f1_anti} <= BASE, worse than headline). Brain+scour "
                f"convergent STRUCTURAL lever, no selectional/animacy knowledge.")
    else:
        verdict = "MIDDLE_BAND_PARTIAL_STRUCTURAL_LIFT"
        failing = [k for k, v in hard_pass_conditions.items() if not v]
        vmsg = (f"MIDDLE_BAND: no HARD_FAIL trigger, but not all HARD_PASS held (failing: {failing}). "
                f"F1 BASE={f1_base} -> {HEADLINE}={f1_head} (+{head_lift}, closes {gap_closed_frac} of the "
                f"+{role_gap} gap); recall {rec['BASE']}->{rec[HEADLINE]}; precision "
                f"{prec['BASE']}->{prec[HEADLINE]}; FRONTED_ANTI={f1_anti}; CANONICAL_BLUNT={f1_blunt}. "
                f"n_head_recovered={len(res['head_recovered'])} n_head_regressed={len(res['head_regressed'])}. "
                f"Partial structural gap-closure -- residual wall named from FP split + regressed items.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: f1 BASE={f1_base} {HEADLINE}={f1_head} (+{head_lift}) FRONTED_ANTI={f1_anti} "
                 f"CANONICAL_BLUNT={f1_blunt} ROLE_ORACLE={f1_oracle} | gap_closed_frac={gap_closed_frac} "
                 f"(role_gap={role_gap}) | precision BASE={prec['BASE']} {HEADLINE}={prec[HEADLINE]} | "
                 f"recall BASE={rec['BASE']} {HEADLINE}={rec[HEADLINE]} | parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["arms"]["BASE"]), headline_arm=HEADLINE,
        one_variable="role_wordorder_reassign: a WORD-IDENTITY-FREE structural override; HEADLINE mode "
                     "'fronted' reassigns, on non-passive clauses with >=2 pre-verbal core candidates and no "
                     "post-verbal core, the farthest pre-verbal core -> PATIENT and nearest -> AGENT "
                     "(OSV reanalysis); parser/perceptron/routing/admissibility-gate/>=2-patient selectional "
                     "argmax held constant across arms",
        bands=dict(CITED_AUDIT_F1_REAL=CITED_AUDIT_F1_REAL,
                   CITED_AUDIT_F1_ROLE_ORACLE=CITED_AUDIT_F1_ROLE_ORACLE, CITED_ROLE_GAP=CITED_ROLE_GAP,
                   P1_REPRO_TOL=P1_REPRO_TOL, HP_GAP_CLOSE_FRAC=HP_GAP_CLOSE_FRAC,
                   HP_F1_MIN_LIFT=HP_F1_MIN_LIFT, HP_RECALL_TOL=HP_RECALL_TOL, HP_ANTI_MARGIN=HP_ANTI_MARGIN,
                   HF_RECALL_REGRESS=HF_RECALL_REGRESS),
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
        roleora_headroom_coverage=(round(len(res["head_of_roleora"]) / len(res["roleora_recovered"]), 4)
                                   if res["roleora_recovered"] else None),
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
        run1_canonical_blunt_note="Run 1 of this cell tested a BLANKET canonical post-verbal override "
                                  "(now the CANONICAL_BLUNT arm): net-negative (F1 0.5738->0.5312, precision "
                                  "0.4861->0.4359, within_frame_fp 6->11) because it steals the patient label "
                                  "onto ditransitive/light-verb recipients (regressed hold/hands, show/way, "
                                  "give/hour, give/books, show/seeds). The HEADLINE fronted/OSV arm is the "
                                  "narrow redirect converged on by the brain deep-dive + the empirical scour.",
        brain_check="thematic-role assignment dissociable from parsing; map constituents gated by word-order "
                    "canonicity; parietal reanalysis for non-canonical/passive only. Lever = word-order-aware "
                    "reanalysis (structural), NOT selectional/animacy (redundant per 29491).",
        scope_caveat=("Parser trained on UD-EWT out-of-domain to McGuffey (same untested transfer already "
                      "flagged). The fronted trigger uses a structural OSV signature (>=2 pre-verbal core + "
                      "no post-verbal core); genuine OSV cases mis-routed by the parser won't present that "
                      "signature (bounded by head_regressed). Reversible-role + dialogue shelved (out of "
                      "scope). MEASUREMENT cell, NOT banked; CLAIM-VET-pending; strategic read = HYPOTHESIS "
                      "pending landed-VET (skunkworks VETs separately)."),
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
