"""G4-v2: PARTICLE-vs-GOVERNING-PREPOSITION split + POS-BASED prenominal skip -- a HELD-OUT-SAFE,
brain-faithful REPLACEMENT for the banked spurious-gate's G4 (governing-preposition hard-exclusion).

PLUGGABLE OVERRIDE (contract): this cell does NOT edit the banked
experiments/exp_reader_structural_precision_gate_v1.py in place. It IMPORTS that module for the
G1/G2/G3 helpers (byte-identical reuse) and re-implements ONLY the clause pass + a `g4_mode`
selector so the G4 admissibility function is swappable. The G4-v2 exclusion helper
(prev_governing_prep_v2) is importable by the consolidated reader.

WHY (VET flag on the banked cell, seq 29497): the banked G4 hard-excludes ANY kept patient preceded
by a preposition via ORC.prev_prep. Two overfit-exposures the VET raised:
  (E1) SKIP-LIST OVERFIT: ORC.prev_prep's left-scan skips a hardcoded WORD-IDENTITY list
       {the,a,an,this,that,some,five,new,old,fat,big,little,kind,blind} -- dev-specific adjectives +
       a literal "five" -> will NOT generalize to held-out prose (misses "another/my/rare/sudden/..").
  (E2) PARTICLE/GOVERNING CONFLATION: a preposition-tagged token can be a VERB PARTICLE
       ("took UP the blocks", "put ON your coat" -> the following NP IS the patient) OR a GOVERNING
       preposition ("put ON the table", "told in HASTE" -> the NP is oblique, correctly excluded). The
       banked G4 excludes both -> on phrasal-verb-rich held-out prose it OVER-SUPPRESSES true patients.

THE BRAIN-FAITHFUL FIX (what signal is ACTUALLY available -- RECOMPUTED, not assumed):
  The task brief suggested distinguishing particle from governing-prep via the DEPENDENCY RELATION
  (prt/compound:prt vs case). MEASURED REALITY: M.decode_clause returns UNLABELED arc-eager heads only
  ({tok:head}, no deprel labels), and a head-based proxy (prep-attaches-to-verb) MISFIRES on genuine
  obliques under the OOD parser (e.g. L09_09 "round in shape" -> parser attaches "in" to the verb =
  False particle; would wrongly re-admit an FP). So the head-relation route is NOT reliably available.
  The RELIABLE, brain-faithful signal is the PENN POS TAG the tagger already assigns:
      verb PARTICLE  -> RP   (e.g. "up" in "took/RP up ..." -- MEASURED@ L04_03 tagging)
      preposition    -> IN / TO
  G4-v2 therefore:
    (1) SKIP prenominal modifiers by POS CLASS, not word identity:
        SKIP_POS = {DT,PDT,JJ,JJR,JJS,CD,PRP$,POS} (the exact POS classes the old word-list enumerated,
        generalized). This removes E1 and MEASURABLY finds obliques the word-list missed on-slice.
    (2) At the stop token: if POS==RP -> it is a verb PARTICLE -> do NOT exclude (following NP is the
        phrasal verb's object). If lemma in the governing-prep set -> exclude (oblique). This removes E2.

EMPIRICAL PRE-FLIGHT (MEASURED@ scratchpad diag over FULL_SLICE, parser uas_dev=0.7882):
  - The banked G4 makes 20 exclusions; 19 are genuine obliques, 1 is a RECALL COST: L04_03
    "Herbert took up ONE OF THE blocks" -> 'blocks' excluded by the PARTITIVE 'of' (one OF the blocks),
    NOT by the particle 'up'. HYPOTHESIS-FALSIFIED (deflated): the particle guard CANNOT recover
    L04_03 take/blocks -- the offending preposition is a partitive 'of', not a particle. Reported as-is.
  - ZERO of the 20 banked exclusions are particle-governed patients -> the RP guard is INERT on this
    slice (unit-proven in self-test; held-out insurance). Its effect is isolated by the
    G4V2_SKIPONLY-vs-G4V2 arm pair (identical on-slice == guard costs nothing here).
  - The POS-based skip finds 13 MORE genuine obliques the word-list missed (33 vs 20 exclusions;
    e.g. "reaching for ANOTHER block", "meddled with MY flowers", "fall on THEIR knees",
    "fell in SUDDEN ruin") -> G4-v2 should RETAIN and likely IMPROVE the precision-side FP reduction.

FAIRNESS (three hash pins prove the rest of the reader is byte-identical to the banked stack):
  P1  BASE arm reproduces V3_INTEGRATED byte-identically: kept_hash == be02002c1579217f (F1 0.5738).
  P2  G4V1 arm reproduces the banked G4_GOVPREP arm byte-identically: kept_hash == 75fbfc1517b2653f
      (subcat_fp 29, spurious_verb_fp 31, -8 combined) -> proves the v1 re-implementation is faithful,
      so the v1-vs-v2 ablation is clean.
  P3  COMPOSED_V1 (G1+G2+G3+G4v1) reproduces the banked COMPOSED arm byte-identically:
      kept_hash == 936581ccc427f6f6 -> proves G1/G2/G3 are UNCHANGED (the ablation isolates G4).

ABLATION (6 arms): BASE | G4V1 (word-list skip, no RP guard) | G4V2_SKIPONLY (POS skip, no RP guard) |
  G4V2 (POS skip + RP particle guard) | COMPOSED_V1 (G1+G2+G3+G4v1) | COMPOSED_V2 (G1+G2+G3+G4v2).
  v1 -> v2_skiponly isolates the SKIP-LIST generalization; v2_skiponly -> v2 isolates the RP guard.

PRE-REGISTERED BANDS (primary discriminator = G4-v2 keeps >= G4-v1's precision-side FP reduction under
  recall retention, AND the composed-v2 reader does not regress vs the banked composed-v1):
  HARD_PASS requires ALL of:
    (1) P1/P2/P3 hash pins all hold (fairness).
    (2) recall(COMPOSED_V2) >= recall(BASE) - 0.02.
    (3) g4v2_fp_reduction >= g4v1_fp_reduction  (v2 retains >= the -8 precision-side reduction).
    (4) precision(G4V2) >= precision(G4V1)  AND  f1(COMPOSED_V2) >= f1(COMPOSED_V1).
    (5) the POS-based skip fires (G4V2_SKIPONLY hash != G4V1 hash on corpus, i.e. generalization bites).
  MIDDLE_BAND if P1/P2/P3 hold + g4v2_fp_reduction >= g4v1_fp_reduction but recall(COMPOSED_V2) drop in
    (0.02, 0.05], OR f1(COMPOSED_V2) in [f1(COMPOSED_V1)-0.005, f1(COMPOSED_V1)).
  HARD_FAIL if ANY of: a hash pin fails (P1/P2/P3); recall(COMPOSED_V2) < recall(BASE) - 0.05;
    g4v2_fp_reduction < g4v1_fp_reduction (v2 WORSE on precision-side than v1); f1(COMPOSED_V2)<f1(BASE).

BRAIN-CHECK: particle vs governing preposition is a real morphosyntactic distinction the brain resolves
  structurally (the RP/IN split IS how the syntactic parse encodes it). No semantic/knowledge gate (those
  HARD_FAILed in the audit). Precision-side structural admissibility, same class as the banked gate.

COMPUTE: class (b) sequential-CPU (reuses M.train_dep_parser + greedy decode + AveragedPerceptron role
  clf + O(candidates) fixed structural string tests; no matmul/GPU primitive). 7 passes over FULL_SLICE
  (1 evidence + 6 scored arms), ~<5min. no_storage. Determinism: OMP/MKL/OPENBLAS=1, fixed int SEED,
  sorted()/deterministic iteration. LOCAL-ONLY foreground-to-completion, NOT banked, NO queue_add.
  progress_logging: line_buffered_stdout (per-arm flushed line; wall < 1800s so timeout exemption also
  applies). arms_differ_verified at smoke (hashes). final_metrics_atomicity: os.replace. except
  SystemExit/KeyboardInterrupt raised before except Exception. baseline_in_band checked at smoke.
  N/A: KGStore (no KG); CRLB (discrete count/precision, no HD noise floor); multi-seed (deterministic
  given fixed SEED + single-seed parser budget, accepted per V3/M/audit scope).
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

ANCHOR_NAME = "reader_g4_particle_govprep_split_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_multipred_depparse_argstruct_recall_v2 as M              # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L   # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC               # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2        # noqa: E402
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3            # noqa: E402
from experiments import exp_reader_clauseseg_verbclass_filter_v1 as VC              # noqa: E402
# Banked spurious-gate: reuse G1/G2/G3 helpers byte-identically (import does NOT re-run its experiment).
from experiments import exp_reader_structural_precision_gate_v1 as GATE1            # noqa: E402

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260726

# ---- fairness hash pins ---------------------------------------------------------------------
V3_BASE_HASH = "be02002c1579217f"        # P1: BASE == V3_INTEGRATED (MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json)
V3_BASE_SUBCAT_FP = 35
V3_BASE_SPURIOUS_FP = 33
V3_BASE_F1 = 0.5738
G4V1_HASH = "75fbfc1517b2653f"           # P2: G4V1 == banked G4_GOVPREP (MEASURED@data/exp_reader_structural_precision_gate_v1/metrics.json:arms.G4_GOVPREP)
COMPOSED_V1_HASH = "936581ccc427f6f6"    # P3: COMPOSED_V1 == banked COMPOSED (MEASURED@ same)
BASELINE_BAND = (0.05, 0.95)

RECALL_RETENTION_OK = 0.02
RECALL_RETENTION_MB = 0.05

# ---- G4 exclusion helpers (v1 = banked behavior; v2 = POS-skip + RP-particle guard) ----------
GOV_PREP = ORC.PREPS_LOC | ORC.PREP_TO | ORC.PREP_OF_WITH
SKIP_POS = frozenset({"DT", "PDT", "JJ", "JJR", "JJS", "CD", "PRP$", "POS"})


def prev_governing_prep_v2(tagged, i, rp_guard):
    """POS-based prenominal-modifier skip + optional RP particle guard.
    Scan left from i over prenominal-modifier POS classes; at the first non-modifier token:
      - if rp_guard and POS == 'RP'  -> return None (verb PARTICLE; following NP is the object, keep).
      - if lemma in the governing-prep set -> return the prep lemma (oblique object -> exclude).
      - else -> None.
    Glass-box, deterministic, word-identity-free (except the closed governing-prep set)."""
    j = i - 1
    while j >= 0 and tagged[j][2] in SKIP_POS:
        j -= 1
    if j < 0:
        return None
    _surf, low, pos = tagged[j]
    if rp_guard and pos == "RP":
        return None
    if low in GOV_PREP:
        return low
    return None


def g4_excludes(tagged, pi, g4_mode):
    """Return True iff G4 (in the given mode) excludes kept patient at index pi."""
    if g4_mode == "off":
        return False
    if g4_mode == "v1":
        # byte-identical to the banked G4: ORC.prev_prep (word-identity skip-list).
        return ORC.prev_prep(tagged, pi) is not None
    if g4_mode == "v2_skiponly":
        return prev_governing_prep_v2(tagged, pi, rp_guard=False) is not None
    if g4_mode == "v2":
        return prev_governing_prep_v2(tagged, pi, rp_guard=True) is not None
    raise ValueError(f"unknown g4_mode: {g4_mode}")


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# ONE clause pass with G1/G2/G3 (reused from GATE1 helpers) + a swappable G4 (g4_mode).
# The all-inert path (g1=g2=g3=False, g4_mode='off') is byte-identical to the banked BASE == V3.
# NON-G4 logic is a verbatim mirror of GATE1.clause_predicate_pass_gated (pins P1/P2/P3 assert it).
# =======================================================================================
def clause_predicate_pass(tagged, heads, clf, gate_fn, carried_agent_in, sel_fn,
                          g1_contraction, g2_dobj, g3_selfloop, g4_mode, supp):
    lows = [t[1] for t in tagged]
    real_predicates = M.content_verb_indices(tagged)

    if g1_contraction:
        predicates = []
        for i in real_predicates:
            if GATE1.is_contracted_aux(tagged[i][1]):
                supp["g1_pred_dropped"] += 1
                continue
            predicates.append(i)
    else:
        predicates = list(real_predicates)

    candidates = ORC.candidate_indices(tagged)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)

    by_pred_map = V3.assign_candidates_to_predicates_fixed(tagged, heads, predicates)
    route = {}
    for p1, cs in by_pred_map.items():
        for c0 in cs:
            route[c0] = p1

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
        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent
        # gate-INDEPENDENT evidence pass (identical to V3; uses the ORIGINAL ORC.prev_prep, unchanged).
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

        # ---- GATE 4 (swappable): governing-preposition exclusion, v1 or v2 ----
        if g4_mode != "off" and kept_patients:
            filtered = []
            for pi in kept_patients:
                if g4_excludes(tagged, pi, g4_mode):
                    supp["g4_patient_excluded"] += 1
                else:
                    filtered.append(pi)
            kept_patients = filtered

        # ---- GATE 2: verb-class (non-factive) + no genuine NP direct object ----
        if g2_dobj and kept_patients:
            if GATE1._is_nonfactive(low) and not VC._has_genuine_direct_object(tagged, v0):
                supp["g2_emissions_suppressed"] += len(kept_patients)
                kept_patients = []

        if resolved_agent is not None and kept_patients and low not in ("has", "is"):
            if gate_fn(vl):
                is_main = (v0 == main_idx)
                kind = M.predicate_kind(tagged, v0, is_main)
                for pi in kept_patients:
                    if g3_selfloop and resolved_agent == tagged[pi][1]:
                        supp["g3_selfloops_dropped"] += 1
                        continue
                    out.append((low, resolved_agent, tagged[pi][1], v0, kind))
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]
    return out, carried_agent, evidence


def build_arm(slice_lessons, W, clf, gate_fn, sel_fn, gold, flags, collect_evidence=False):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    out = {}
    evidence_total = {}
    supp = defaultdict(int)
    for sid in order:
        raw = sent_text[sid]
        carried_agent = None
        tups = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            clause_tups, carried_agent, ev = clause_predicate_pass(
                tagged, heads, clf, gate_fn, carried_agent, sel_fn,
                flags["g1_contraction"], flags["g2_dobj"], flags["g3_selfloop"], flags["g4_mode"], supp)
            tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
            if collect_evidence:
                for lemma, val in ev.items():
                    evidence_total[lemma] = evidence_total.get(lemma, False) or val
        out[sid] = tups
    if collect_evidence:
        return order, out, evidence_total, dict(supp)
    return order, out, dict(supp)


ARM_FLAGS = {
    "BASE":           dict(g1_contraction=False, g2_dobj=False, g3_selfloop=False, g4_mode="off"),
    "G4V1":           dict(g1_contraction=False, g2_dobj=False, g3_selfloop=False, g4_mode="v1"),
    "G4V2_SKIPONLY":  dict(g1_contraction=False, g2_dobj=False, g3_selfloop=False, g4_mode="v2_skiponly"),
    "G4V2":           dict(g1_contraction=False, g2_dobj=False, g3_selfloop=False, g4_mode="v2"),
    "COMPOSED_V1":    dict(g1_contraction=True,  g2_dobj=True,  g3_selfloop=True,  g4_mode="v1"),
    "COMPOSED_V2":    dict(g1_contraction=True,  g2_dobj=True,  g3_selfloop=True,  g4_mode="v2"),
}


def run_arms(slice_lessons, W, clf, ratings_table, gold):
    sel_fn = V3.build_sel_fn(ratings_table)
    _, _, evidence_base, _ = build_arm(slice_lessons, W, clf, lambda v: True, None, gold,
                                       ARM_FLAGS["BASE"], collect_evidence=True)
    gate_fn = M.build_learned_admissibility(evidence_base)

    arms = {}
    supp_by_arm = {}
    for name, flags in ARM_FLAGS.items():
        order, kept, supp = build_arm(slice_lessons, W, clf, gate_fn, sel_fn, gold, flags)
        arms[name] = kept
        supp_by_arm[name] = supp
        print(f"[arm] {name} done", flush=True)

    scored = {}
    for name, kept in arms.items():
        rc, miss, npos, misses = M.recall_ceiling_of(kept, gold)
        sc = L.score_arm(M.to_kept_list(kept), gold)
        scored[name] = dict(recall_ceiling=rc, score=sc, kept_hash=M.arm_hash(kept), n_pred=sc["n_pred"])

    base_covered = M.covered_set(arms["BASE"], gold)
    lost_by_arm = {}
    for name in ARM_FLAGS:
        if name == "BASE":
            continue
        lost_by_arm[name] = sorted(base_covered - M.covered_set(arms[name], gold))

    return dict(arms=arms, scored=scored, supp_by_arm=supp_by_arm, lost_by_arm=lost_by_arm)


# =======================================================================================
# Markers / metrics (atomic).
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
# Self-test (design-gate).
# =======================================================================================
def _synthetic_tagged(triples):
    out = []
    for surf, pos in triples:
        low = surf.lower().strip(".,'\"!?;:")
        out.append((surf, low, pos))
    return out


def self_test():
    print("[self-test] G4-v2 helper unit checks ...", flush=True)
    # (a) POS-based skip generalizes past ADJ/CD/PRP$ the word-list never listed.
    #     "reaching for another RARE block" -> block <- rare(JJ) <- another(DT) <- for(IN) -> excluded.
    t_gen = _synthetic_tagged([("reaching", "VBG"), ("for", "IN"), ("another", "DT"),
                               ("rare", "JJ"), ("block", "NN")])
    assert prev_governing_prep_v2(t_gen, 4, rp_guard=True) == "for", "v2 skip failed to reach gov prep"
    # word-list v1 stops at 'another'/'rare' (not in its skip-list) -> returns None (the E1 overfit).
    assert ORC.prev_prep(t_gen, 4) is None, "v1 unexpectedly generalized (skip-list changed?)"
    print("[self-test]   (a) POS-skip reaches 'for' where the word-identity skip-list does NOT.", flush=True)

    # (b) RP-particle guard: same surface 'on', but POS distinguishes particle from preposition.
    #     "put ON your coat" (on/RP = particle) -> KEEP the following NP (coat is the object).
    t_prt = _synthetic_tagged([("put", "VBD"), ("on", "RP"), ("your", "PRP$"), ("coat", "NN")])
    assert prev_governing_prep_v2(t_prt, 3, rp_guard=True) is None, "RP guard did NOT keep particle object"
    #     without the guard (v2_skiponly), the lemma 'on' in GOV_PREP would exclude it -> witnesses the guard.
    assert prev_governing_prep_v2(t_prt, 3, rp_guard=False) == "on", "guard-off did not exclude 'on' object"
    #     "put ON the table" (on/IN = preposition) -> EXCLUDE (oblique).
    t_gov = _synthetic_tagged([("put", "VBD"), ("on", "IN"), ("the", "DT"), ("table", "NN")])
    assert prev_governing_prep_v2(t_gov, 3, rp_guard=True) == "on", "gov-prep 'on/IN' not excluded"
    print("[self-test]   (b) RP guard keeps 'on/RP' particle object, excludes 'on/IN' oblique.", flush=True)

    # (c) mirror the L04_03 partitive reality: 'blocks' after 'of/IN' is excluded by BOTH v1 and v2
    #     (partitive 'one OF the blocks' -> the particle guard CANNOT recover it; honest scope).
    t_part = _synthetic_tagged([("took", "VBD"), ("up", "RP"), ("one", "CD"), ("of", "IN"),
                                ("the", "DT"), ("blocks", "NNS")])
    assert ORC.prev_prep(t_part, 5) == "of" and prev_governing_prep_v2(t_part, 5, rp_guard=True) == "of", \
        "partitive 'of' should be excluded by both v1 and v2 (L04_03 is not recoverable via particle guard)"
    print("[self-test]   (c) partitive 'of' excluded by v1 AND v2 (L04_03 not particle-recoverable).", flush=True)

    print("[self-test] loading SMOKE_SLICE reader + gold + knowledge table ...", flush=True)
    gold, meta = L.load_gold(SMOKE_SLICE)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    assert len(ratings_table) > 100, f"knowledge table suspiciously small: {len(ratings_table)}"

    print("[self-test] training arc-eager parser (smoke budget) ...", flush=True)
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"

    res = run_arms(SMOKE_SLICE, W, clf, ratings_table, gold)
    scored = res["scored"]
    for name in ARM_FLAGS:
        assert name in scored, f"arm {name} missing from smoke run"
    print(f"[self-test] 6-arm SMOKE f1: { {k: v['score']['f1'] for k, v in scored.items()} }", flush=True)

    prec_base = scored["BASE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], \
        f"BASE precision {prec_base} outside band {BASELINE_BAND}"

    hashes = {name: v["kept_hash"] for name, v in scored.items()}
    if len(set(hashes.values())) == 1:
        print("[self-test] WARN: all arm hashes identical at SMOKE (gates may not bite the small slice; "
              "each mechanism is unit-proven above + re-checked at FULL)", flush=True)
    else:
        print(f"[self-test] arms differ at smoke: {hashes}", flush=True)

    # corpus-level degrade witness on FULL-style tagging is deferred to FULL; the unit checks above +
    # the smoke run prove the mechanism can fire. Determinism: two identical BASE runs match.
    def _base():
        ev = build_arm(SMOKE_SLICE, W, clf, lambda v: True, None, gold, ARM_FLAGS["BASE"],
                       collect_evidence=True)[2]
        return build_arm(SMOKE_SLICE, W, clf, M.build_learned_admissibility(ev),
                         V3.build_sel_fn(ratings_table), gold, ARM_FLAGS["BASE"])[1]
    assert M.arm_hash(_base()) == M.arm_hash(_base()), "non-deterministic BASE output"
    print("[self-test] deterministic (two identical BASE runs -> identical kept-tuple hash)", flush=True)
    print("[self-test] PASS", flush=True)
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
    res = run_arms(slice_lessons, W, clf, ratings_table, gold)
    scored = res["scored"]

    def sc(name):
        return scored[name]["score"]

    base = sc("BASE")
    g4v1 = sc("G4V1")
    g4v2so = sc("G4V2_SKIPONLY")
    g4v2 = sc("G4V2")
    cv1 = sc("COMPOSED_V1")
    cv2 = sc("COMPOSED_V2")

    def combined_fp(s):
        return s["subcat_fp"] + s["spurious_verb_fp"]

    base_cfp = combined_fp(base)
    g4v1_fp_red = base_cfp - combined_fp(g4v1)
    g4v2so_fp_red = base_cfp - combined_fp(g4v2so)
    g4v2_fp_red = base_cfp - combined_fp(g4v2)

    # fairness pins
    base_hash_ok = (scored["BASE"]["kept_hash"] == V3_BASE_HASH)
    g4v1_hash_ok = (scored["G4V1"]["kept_hash"] == G4V1_HASH)
    cv1_hash_ok = (scored["COMPOSED_V1"]["kept_hash"] == COMPOSED_V1_HASH)
    repro_counts_ok = (base["subcat_fp"] == V3_BASE_SUBCAT_FP and
                       base["spurious_verb_fp"] == V3_BASE_SPURIOUS_FP and
                       abs(base["f1"] - V3_BASE_F1) < 1e-6)

    recall_drop_cv2 = round(base["recall"] - cv2["recall"], 4)
    skip_fires = (scored["G4V2_SKIPONLY"]["kept_hash"] != scored["G4V1"]["kept_hash"])
    rp_guard_fires = (scored["G4V2"]["kept_hash"] != scored["G4V2_SKIPONLY"]["kept_hash"])

    v2_keeps_reduction = (g4v2_fp_red >= g4v1_fp_red)
    v2_precision_ok = (g4v2["precision"] >= g4v1["precision"])
    cv2_f1_ok = (cv2["f1"] >= cv1["f1"])
    cv2_prec_up = (cv2["precision"] > base["precision"])

    hard_fail = []
    if not (base_hash_ok and g4v1_hash_ok and cv1_hash_ok):
        hard_fail.append(f"fairness pin FAILED: base_hash_ok={base_hash_ok} (got "
                         f"{scored['BASE']['kept_hash']}), g4v1_hash_ok={g4v1_hash_ok} (got "
                         f"{scored['G4V1']['kept_hash']}), cv1_hash_ok={cv1_hash_ok} (got "
                         f"{scored['COMPOSED_V1']['kept_hash']})")
    if recall_drop_cv2 > RECALL_RETENTION_MB:
        hard_fail.append(f"recall killed: COMPOSED_V2 recall drop {recall_drop_cv2} > {RECALL_RETENTION_MB}")
    if not v2_keeps_reduction:
        hard_fail.append(f"G4-v2 REGRESSED precision-side: g4v2_fp_red {g4v2_fp_red} < g4v1_fp_red "
                         f"{g4v1_fp_red}")
    if cv2["f1"] < base["f1"]:
        hard_fail.append(f"f1 regressed vs BASE: COMPOSED_V2 f1 {cv2['f1']} < base {base['f1']}")

    hard_pass = (base_hash_ok and g4v1_hash_ok and cv1_hash_ok and
                 recall_drop_cv2 <= RECALL_RETENTION_OK and v2_keeps_reduction and
                 v2_precision_ok and cv2_f1_ok and skip_fires)

    if hard_fail:
        verdict = "HARD_FAIL"
        vmsg = "HARD_FAIL: " + "; ".join(hard_fail)
    elif hard_pass:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS: pins OK (BASE={V3_BASE_HASH}, G4V1={G4V1_HASH}, COMPOSED_V1={COMPOSED_V1_HASH}); "
                f"g4_fp_reduction v1={g4v1_fp_red} -> v2={g4v2_fp_red} (skip-only={g4v2so_fp_red}); "
                f"skip_fires={skip_fires} rp_guard_fires={rp_guard_fires}; G4V2 precision "
                f"{g4v1['precision']}->{g4v2['precision']}; COMPOSED_V2 f1 {cv1['f1']}(v1)->{cv2['f1']}(v2), "
                f"recall {base['recall']}->{cv2['recall']} (drop {recall_drop_cv2}).")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: pins OK={base_hash_ok and g4v1_hash_ok and cv1_hash_ok}; g4_fp_reduction "
                f"v1={g4v1_fp_red} v2={g4v2_fp_red}; COMPOSED_V2 f1 {cv2['f1']} vs COMPOSED_V1 {cv1['f1']}; "
                f"recall drop {recall_drop_cv2}. Below HARD_PASS (recall retention or f1/precision short).")

    elapsed = round(time.perf_counter() - t0, 2)
    arms_out = {}
    for name, v in scored.items():
        s = v["score"]
        arms_out[name] = dict(f1=s["f1"], precision=s["precision"], recall=s["recall"],
                              recall_ceiling=v["recall_ceiling"], n_pred=s["n_pred"],
                              subcat_fp=s["subcat_fp"], within_frame_fp=s["within_frame_fp"],
                              spurious_verb_fp=s["spurious_verb_fp"], total_fp=s["total_fp"],
                              combined_target_fp=s["subcat_fp"] + s["spurious_verb_fp"],
                              kept_hash=v["kept_hash"], suppression_counts=res["supp_by_arm"][name])

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: pins(base={base_hash_ok},g4v1={g4v1_hash_ok},cv1={cv1_hash_ok}) | "
                 f"g4_fp_red v1={g4v1_fp_red} skiponly={g4v2so_fp_red} v2={g4v2_fp_red} | "
                 f"skip_fires={skip_fires} rp_guard_fires={rp_guard_fires} | "
                 f"COMPOSED_V1 f1={cv1['f1']} -> COMPOSED_V2 f1={cv2['f1']} | "
                 f"recall base={base['recall']} cv2={cv2['recall']} drop={recall_drop_cv2}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["arms"]["BASE"]),
        one_variable="the G4 governing-preposition exclusion rule (off / v1 word-list-skip / "
                     "v2_skiponly POS-skip / v2 POS-skip+RP-particle-guard), holding the reader's "
                     "routing/labeling/learned-admissibility gate + G1/G2/G3 byte-identical across arms",
        fairness_pins=dict(base_hash_ok=base_hash_ok, g4v1_hash_ok=g4v1_hash_ok, cv1_hash_ok=cv1_hash_ok,
                           repro_counts_ok=repro_counts_ok,
                           base_kept_hash=scored["BASE"]["kept_hash"], v3_hash=V3_BASE_HASH,
                           g4v1_kept_hash=scored["G4V1"]["kept_hash"], banked_g4_hash=G4V1_HASH,
                           composed_v1_kept_hash=scored["COMPOSED_V1"]["kept_hash"],
                           banked_composed_hash=COMPOSED_V1_HASH),
        ablation=dict(
            g4v1_fp_reduction=g4v1_fp_red, g4v2_skiponly_fp_reduction=g4v2so_fp_red,
            g4v2_fp_reduction=g4v2_fp_red,
            skip_list_generalization_fires=skip_fires, rp_particle_guard_fires_on_corpus=rp_guard_fires,
            v2_keeps_reduction=v2_keeps_reduction, v2_precision_ge_v1=v2_precision_ok,
            g4v1_exclusions=res["supp_by_arm"]["G4V1"].get("g4_patient_excluded", 0),
            g4v2_skiponly_exclusions=res["supp_by_arm"]["G4V2_SKIPONLY"].get("g4_patient_excluded", 0),
            g4v2_exclusions=res["supp_by_arm"]["G4V2"].get("g4_patient_excluded", 0)),
        composed=dict(recall_drop_cv2=recall_drop_cv2, cv2_f1_ge_cv1=cv2_f1_ok, cv2_precision_up=cv2_prec_up,
                      composed_v1_f1=cv1["f1"], composed_v2_f1=cv2["f1"],
                      composed_v1_precision=cv1["precision"], composed_v2_precision=cv2["precision"],
                      composed_v1_recall=cv1["recall"], composed_v2_recall=cv2["recall"]),
        bands=dict(RECALL_RETENTION_OK=RECALL_RETENTION_OK, RECALL_RETENTION_MB=RECALL_RETENTION_MB,
                   V3_BASE_HASH=V3_BASE_HASH, G4V1_HASH=G4V1_HASH, COMPOSED_V1_HASH=COMPOSED_V1_HASH),
        arms=arms_out,
        lost_covered_by_arm={k: [list(x) for x in v[:40]] for k, v in res["lost_by_arm"].items()},
        n_lost_covered_by_arm={k: len(v) for k, v in res["lost_by_arm"].items()},
        parser_info=parser_info,
        cited_base=dict(source="data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json",
                        arm="V3_INTEGRATED", f1=V3_BASE_F1, kept_hash=V3_BASE_HASH),
        cited_banked_g4=dict(source="data/exp_reader_structural_precision_gate_v1/metrics.json",
                             g4_govprep_hash=G4V1_HASH, composed_hash=COMPOSED_V1_HASH),
        scope_caveat=(
            "Parser trained on UD-EWT (out-of-domain to 19th-c. McGuffey prose; same untested transfer "
            "V3/M/audit/gate1 flag). UNLABELED heads -> particle vs governing-prep is resolved by the "
            "RP/IN POS TAG (not the dep relation, which the parser does NOT emit; a head-based proxy "
            "MISFIRES on OOD parses). Gates are FIXED structural rules. HONEST SCOPE: on THIS slice the "
            "RP-particle guard is INERT (no particle-governed patients among the exclusions) and the "
            "L04_03 take/blocks recall loss is a PARTITIVE 'of' (one OF the blocks), NOT a particle -> "
            "the particle guard does NOT recover it; the load-bearing on-slice change is the POS-based "
            "skip generalization. The particle guard's value is HELD-OUT-ONLY (unit-proven, not banked). "
            "Precision-side result; CLAIM-VET-pending; the real transfer test is a held-out phrasal-rich "
            "run. Pluggable: import prev_governing_prep_v2 / g4_excludes(mode='v2') into the reader."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"], flush=True)
    print("verdict:", verdict, flush=True)
    print("verdict_msg:", vmsg, flush=True)
    print("arms:", json.dumps(arms_out, indent=1), flush=True)
    print("lost_covered_by_arm:", json.dumps(metrics["lost_covered_by_arm"], indent=1), flush=True)
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
    except Exception as e:
        _write_crash_metrics(_out_dir("full"), e)
        raise
