"""PRECISION-SIDE SPURIOUS-PREDICATE SUPPRESSION -- a PLUGGABLE, glass-box STRUCTURAL emission/admissibility
gate for the who-did-what reader. DRIVE DOWN spurious_verb_fp + subcat_fp WITHOUT killing recall.

WHY (component oracle-ablation audit, 29494 MEASURED@data/exp_reader_component_oracle_ablation_audit_v1/
metrics.json): spurious_verb_fp stays FLAT ~31-33 and subcat_fp FLAT ~32-35 across EVERY oracle arm
including ALL_ORACLE (perfect enum+parse+role). So this FP is the reader's OWN emission logic, not
parse/enum/role. Brain mechanism (deep-dive): the brain suppresses spurious predicates by EXPLAINING-AWAY
(a token a higher-level structural account already covers is not emitted) + precision-weighting + lateral
inhibition -- STRUCTURAL, not semantic/knowledge. Converges with the scour: SEMANTIC gating HARD_FAILed
(exp_subcat_licensing_graded_frame_break050_v1 bal_acc 0.601 near chance; selectional-knowledge-table gate
redundant 2x); STRUCTURAL gates work (clauseseg_verbclass_filter CLAUSE_SEG_PRECISION_CLEAN, selfloop
cheapfix precision 0.472->0.500).

FOUR STRUCTURAL CUES, each a SEPARATE TOGGLE (glass-box ablation + P2 must-fire), composed on TOP of a
BASE arm that reproduces V3_INTEGRATED byte-identically (kept_hash=be02002c1579217f, subcat_fp=35,
spurious_verb_fp=33, precision=0.4861, recall=0.7, f1=0.5738 MEASURED@data/
exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED):

  G1 CONTRACTION-NORMALIZE before the AUX filter (cheapest, most certain, zero recall risk). CODE BUG:
     M.content_verb_indices uses `low not in ORC.AUX_LEMMAS` on the RAW SURFACE token, so contracted modals
     ("won't","can't","shouldn't") are NEVER in AUX_LEMMAS and, when the tagger tags them VB*, get emitted
     as content-verb predicates. G1 drops a predicate whose contraction-normalized lemma IS an aux/modal.
     Contracted auxiliaries are NEVER true predicates here -> zero recall risk.

  G2 VERB-CLASS + DIRECT-OBJECT-PARSE gate (generalizes exp_reader_clauseseg_verbclass_filter_v1's
     CLAUSE_SEG_PRECISION_CLEAN PASS, zero recall regression): suppress a (verb,patient) emission when the
     verb is NON-FACTIVE/mental-state (wished/thought/know) AND the parse shows NO genuine NP direct object
     for that verb (only a PP or a sentential complement -- the complement NP is wrongly pulled up as the
     object). Byte-identical reuse of VC._NON_FACTIVE_SURFACE + VC._has_genuine_direct_object (the
     verb-INDEPENDENT structural direct-object check is the generalizable guard). Recall-safe: a non-factive
     verb WITH a genuine direct object ("wanted the ball") has_do=True -> NOT suppressed.

  G3 SELF-LOOP guard (exp_reader_cheapfix_selfloop_rolefix_v1, PASS, precision 0.472->0.500): drop an
     emitted (v, X, X) where agent surface == patient surface.

  G4 GOVERNING-PREPOSITION hard-exclusion (structural generalization of G2, verb-INDEPENDENT): use
     ORC.prev_prep(tagged, i) -- already a SOFT feature-cue -- as a HARD admissibility exclusion for a
     kept patient that is object-of-a-stripped-preposition (adjunct-PP mis-extracted as direct object:
     told...in haste / home / school). Drop the kept patient pi when ORC.prev_prep(tagged, pi) is not None.

Prefer FIXED/structural thresholds over learned weighting where they disagree (per
exp_lccp_motion_aspectual_subcat_break_v1: the hand cue 0.2 reduction beat the learned 0.1; the cues
suffice, the learning underperforms) -- ALL FOUR gates here are fixed structural rules, no learned weight.

ARMS (6): BASE (all gates off; MUST reproduce V3 hash) | G1_CONTRACTION | G2_DOBJ | G3_SELFLOOP |
  G4_GOVPREP | COMPOSED (all 4 on). Per-gate suppression counters logged for glass-box ablation +
  P2 must-fire.

FAIRNESS:
  P1 same-base: BASE arm reproduces V3 byte/count-identical (assert kept_hash == be02002c1579217f;
     subcat_fp==35, spurious_verb_fp==33, f1==0.5738). The BASE path is a copy of the audit's REAL branch
     (audit REAL reproduced V3 hash exactly, MEASURED@data/exp_reader_component_oracle_ablation_audit_v1/
     metrics.json:arms.REAL.kept_hash) with all oracle branches removed and the 4 gate hooks inert.
  P2 must-fire: EACH gate must PROVABLY fire -- ablate it (BASE hash != Gi hash on corpus, OR a self-test
     degrade-control witness when a gate does not bite the corpus tagger). The self-test unit-proves each
     gate's mechanism CAN fire independent of whether the FULL corpus exercises it.
  RECALL-RETENTION floor (pre-registered): a gate must NOT kill recall. recall(COMPOSED) >= recall(BASE)
     - 0.02 for HARD_PASS; recall drop in (0.02, 0.05] -> MIDDLE_BAND; recall drop > 0.05 -> HARD_FAIL.
     recall(before/after) reported per gate + composed.

PRE-REGISTERED BANDS (primary discriminator = combined_target_fp = spurious_verb_fp + subcat_fp on COMPOSED
  vs BASE=68, under recall retention + f1 non-regression):
  HARD_PASS requires ALL of:
    (1) P1 reproduction: BASE kept_hash == be02002c1579217f
    (2) recall(COMPOSED) >= recall(BASE) - 0.02
    (3) combined_target_fp(COMPOSED) <= combined_target_fp(BASE) - 4   (>=4 FP removed)
    (4) precision(COMPOSED) > precision(BASE) AND f1(COMPOSED) >= f1(BASE)
    (5) >=1 gate fires cleanly (suppresses >=1 emission with no recall regression from that gate alone)
  MIDDLE_BAND if P1 holds + f1 non-regression but FP reduction in [1,3], OR recall drop in (0.02, 0.05].
  HARD_FAIL if ANY of: P1 reproduction fails (BASE hash mismatch); recall(COMPOSED) < recall(BASE) - 0.05;
    combined_target_fp not reduced at all (0); f1(COMPOSED) < f1(BASE); no gate fires anywhere.

BRAIN-CHECK: the mechanism IS brain-faithful (explaining-away / precision-weighting / lateral inhibition =
  structural suppression of a token a higher-level account already covers). This is a precision-side
  structural admissibility layer, exactly the class the audit + scour both pointed to; no semantic/knowledge
  gate (those HARD_FAILed). N/A new-capability claim beyond the reader; this is a chain-grade optimization of
  an EXISTING reader component, banked/VET'd by skunkworks separately.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- reuses M.train_dep_parser's arc-eager
  training pass (ONE parser, ~50-65s FULL) + per-clause greedy decode (ms/clause) + per-predicate role
  classification (AveragedPerceptron) + O(candidates) dict lookups + fixed structural string tests; NO
  matmul/storage/GPU-batchable primitive. 7 passes over FULL_SLICE (1 keepall-evidence pass to build the
  shared learned admissibility gate + 6 scored arms), same order as the audit's own 6-pass cell (~<5min).
  Storage: no_storage. Runtime invariant: glass-box (from-scratch-trained transition parser + curated dict
  lookups + fixed structural rules), NO LLM/network/autograd at inference. Determinism: OMP/MKL/OPENBLAS=1,
  fixed int SEED, no hash()-seeded RNG, sorted()/deterministic dict iteration only. LOCAL-ONLY,
  foreground-to-completion, NOT banked (skunkworks VETs numbers separately), NO queue_add.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground precision-gate cell):
  - arms_differ_verified at smoke (hash test over the 6 arms' kept-tuple sets; BASE hash pinned to V3)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASE) < 0.95)
  - discriminator fires at smoke: >=1 gate suppresses >=1 emission at SMOKE scale OR self-test degrade
    witness fires (small-sample WARN permitted, same discipline as the audit / V3 self-tests)
  - deterministic seeding (fixed int SEED; no hash()-seeded RNG; sorted() where order matters)
  - all numbers tagged MEASURED@ / CITED@ / HYPOTHESIZED@ in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/precision measurement, no HD noise floor); N/A multi-seed
    (deterministic given fixed SEED + the parser's own single-seed training budget, accepted scope tradeoff
    per V3/M/audit docstrings)
  - progress_logging: line_buffered_stdout (each arm prints a flushed progress line; full wall < 5min so the
    timeout_s < 1800 exemption also applies, but line-buffering is set defensively)
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

ANCHOR_NAME = "reader_structural_precision_gate_v1"
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
from experiments import exp_reader_clauseseg_verbclass_filter_v1 as VC              # noqa: E402

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
SEED = 20260726

# ---- P1 reproduction pin (V3_INTEGRATED == audit REAL) --------------------------------------
V3_BASE_HASH = "be02002c1579217f"   # MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.kept_hash
V3_BASE_SUBCAT_FP = 35              # MEASURED@ same
V3_BASE_SPURIOUS_FP = 33           # MEASURED@ same
V3_BASE_F1 = 0.5738                # MEASURED@ same
V3_BASE_RECALL = 0.7               # MEASURED@ same
BASELINE_BAND = (0.05, 0.95)

# ---- pre-registered bands (see docstring) ---------------------------------------------------
RECALL_RETENTION_OK = 0.02     # HARD_PASS: recall drop <= this
RECALL_RETENTION_MB = 0.05     # MIDDLE_BAND up to this; beyond -> HARD_FAIL
FP_REDUCTION_HARD_PASS = 4     # combined (spurious+subcat) FP removed for HARD_PASS


# =======================================================================================
# GATE 1 helper: contraction-normalize a token to its underlying aux/modal lemma.
# Glass-box, deterministic. A predicate whose normalized lemma is an aux/modal is dropped.
# =======================================================================================
CONTRACTED_MODAL_MAP = {
    "won't": "will", "can't": "can", "cannot": "can", "shan't": "shall",
    "shouldn't": "should", "couldn't": "could", "wouldn't": "would", "mustn't": "must",
    "mightn't": "might", "don't": "do", "doesn't": "does", "didn't": "did",
    "isn't": "is", "aren't": "are", "wasn't": "was", "weren't": "were", "ain't": "is",
    "hasn't": "has", "haven't": "have", "hadn't": "had",
    "'ll": "will", "'d": "would", "'ve": "have", "'re": "are", "'m": "am",
}
_NT_IRREGULAR_BASE = {"wo": "will", "ca": "can", "sha": "shall"}


def normalize_contraction(low):
    """Return the underlying aux/modal lemma for a contracted token, else the token unchanged.
    Deterministic, word-identity-based ON FUNCTION WORDS ONLY (never touches content verbs)."""
    if low in CONTRACTED_MODAL_MAP:
        return CONTRACTED_MODAL_MAP[low]
    if low.endswith("n't"):
        base = low[:-3]
        if base in _NT_IRREGULAR_BASE:
            return _NT_IRREGULAR_BASE[base]
        if base in ORC.AUX_LEMMAS:
            return base
    return low


def is_contracted_aux(low):
    """True iff `low` is a contracted auxiliary/modal (normalizes to an ORC.AUX_LEMMAS member)."""
    if "'" not in low and not low.endswith("n't"):
        return False
    norm = normalize_contraction(low)
    return norm != low and norm in ORC.AUX_LEMMAS


def _is_nonfactive(low):
    """G2 verb-class membership (byte-identical reuse of VC's surface set)."""
    return low in VC._NON_FACTIVE_SURFACE


# =======================================================================================
# Gold + shared-gate scaffolding (byte-identical in spirit to the 29494 audit).
# =======================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# ONE clause pass with 4 independent STRUCTURAL gate flags (all-False reproduces V3 exactly).
# The all-False path is a verbatim copy of the audit's REAL branch (oracle branches removed).
# =======================================================================================
def clause_predicate_pass_gated(tagged, heads, clf, gate_fn, carried_agent_in, sel_fn,
                                g1_contraction, g2_dobj, g3_selfloop, g4_govprep, supp):
    lows = [t[1] for t in tagged]
    real_predicates = M.content_verb_indices(tagged)

    # ---- GATE 1: contraction-normalize before the (content-verb / aux) predicate gate ----
    if g1_contraction:
        predicates = []
        for i in real_predicates:
            if is_contracted_aux(tagged[i][1]):
                supp["g1_pred_dropped"] += 1
                continue
            predicates.append(i)
    else:
        predicates = list(real_predicates)

    candidates = ORC.candidate_indices(tagged)
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)

    # Routing: byte-identical reuse of V3's OWN routing function (the audit REAL arm proved this
    # reproduces the V3 kept-tuple hash exactly).
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
        # gate-INDEPENDENT evidence pass (shared learned-gate build reads this; must stay identical
        # to V3 -- runs over the pre-gate local_cand exactly as the audit/V3 do).
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

        # ---- GATE 4: governing-preposition hard-exclusion (per kept patient) ----
        if g4_govprep and kept_patients:
            filtered = []
            for pi in kept_patients:
                if ORC.prev_prep(tagged, pi) is not None:
                    supp["g4_patient_excluded"] += 1
                else:
                    filtered.append(pi)
            kept_patients = filtered

        # ---- GATE 2: verb-class (non-factive) + no genuine NP direct object ----
        if g2_dobj and kept_patients:
            if _is_nonfactive(low) and not VC._has_genuine_direct_object(tagged, v0):
                supp["g2_emissions_suppressed"] += len(kept_patients)
                kept_patients = []

        if resolved_agent is not None and kept_patients and low not in ("has", "is"):
            if gate_fn(vl):
                is_main = (v0 == main_idx)
                kind = M.predicate_kind(tagged, v0, is_main)
                for pi in kept_patients:
                    # ---- GATE 3: self-loop (agent surface == patient surface) ----
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
            clause_tups, carried_agent, ev = clause_predicate_pass_gated(
                tagged, heads, clf, gate_fn, carried_agent, sel_fn,
                flags["g1_contraction"], flags["g2_dobj"], flags["g3_selfloop"], flags["g4_govprep"],
                supp)
            tups.extend([(t[0], t[1], t[2]) for t in clause_tups])
            if collect_evidence:
                for lemma, val in ev.items():
                    evidence_total[lemma] = evidence_total.get(lemma, False) or val
        out[sid] = tups
    if collect_evidence:
        return order, out, evidence_total, dict(supp)
    return order, out, dict(supp)


ARM_FLAGS = {
    "BASE":          dict(g1_contraction=False, g2_dobj=False, g3_selfloop=False, g4_govprep=False),
    "G1_CONTRACTION": dict(g1_contraction=True,  g2_dobj=False, g3_selfloop=False, g4_govprep=False),
    "G2_DOBJ":       dict(g1_contraction=False, g2_dobj=True,  g3_selfloop=False, g4_govprep=False),
    "G3_SELFLOOP":   dict(g1_contraction=False, g2_dobj=False, g3_selfloop=True,  g4_govprep=False),
    "G4_GOVPREP":    dict(g1_contraction=False, g2_dobj=False, g3_selfloop=False, g4_govprep=True),
    "COMPOSED":      dict(g1_contraction=True,  g2_dobj=True,  g3_selfloop=True,  g4_govprep=True),
}


def run_arms(slice_lessons, W, clf, ratings_table, gold):
    sel_fn = V3.build_sel_fn(ratings_table)
    # Shared learned admissibility gate: ONE keepall-evidence pass under BASE flags (byte-identical to V3).
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
    lost_by_arm = {}   # gold-covered items the gate DROPPED vs BASE (recall cost)
    for name in ARM_FLAGS:
        if name == "BASE":
            continue
        lost_by_arm[name] = sorted(base_covered - M.covered_set(arms[name], gold))

    return dict(arms=arms, scored=scored, supp_by_arm=supp_by_arm, lost_by_arm=lost_by_arm)


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
# Self-test (design-gate).
# =======================================================================================
def _synthetic_tagged(triples):
    """Build a (surf, low, pos) tagged list from (surface, pos) pairs (low = ORC-style)."""
    out = []
    for surf, pos in triples:
        low = surf.lower().strip(".,'\"!?;:")
        out.append((surf, low, pos))
    return out


def self_test():
    print("[self-test] G1 contraction unit checks ...", flush=True)
    assert is_contracted_aux("won't") and normalize_contraction("won't") == "will"
    assert is_contracted_aux("can't") and is_contracted_aux("shouldn't") and is_contracted_aux("don't")
    assert is_contracted_aux("hasn't") and is_contracted_aux("didn't")
    # content verbs / true predicates are NEVER touched
    assert not is_contracted_aux("rubbed") and not is_contracted_aux("wished") and not is_contracted_aux("cat")
    assert not is_contracted_aux("its")  # possessive, not a contracted aux
    print("[self-test] G1 unit PASS (contracted modals -> aux, content verbs untouched)", flush=True)

    print("[self-test] G2 verb-class + dobj unit checks ...", flush=True)
    assert "wished" in VC._NON_FACTIVE_SURFACE and "thought" in VC._NON_FACTIVE_SURFACE
    assert "killed" not in VC._NON_FACTIVE_SURFACE and "rubbed" not in VC._NON_FACTIVE_SURFACE
    # "wished for a place" -> no genuine direct object (prep-governed)
    t_wish = _synthetic_tagged([("She", "PRP"), ("wished", "VBD"), ("for", "IN"), ("a", "DT"),
                                ("place", "NN")])
    assert not VC._has_genuine_direct_object(t_wish, 1)
    # "wanted the ball" -> genuine direct object (recall-safe: NOT suppressed)
    t_want = _synthetic_tagged([("He", "PRP"), ("wanted", "VBD"), ("the", "DT"), ("ball", "NN")])
    assert VC._has_genuine_direct_object(t_want, 1)
    print("[self-test] G2 unit PASS (non-factive+no-dobj suppressible; non-factive+dobj preserved)",
          flush=True)

    print("[self-test] loading SMOKE_SLICE reader + gold + knowledge table ...", flush=True)
    gold, meta = L.load_gold(SMOKE_SLICE)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    assert len(ratings_table) > 100, f"knowledge table suspiciously small: {len(ratings_table)}"

    print("[self-test] training arc-eager parser (smoke budget, reused M code) ...", flush=True)
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"

    res = run_arms(SMOKE_SLICE, W, clf, ratings_table, gold)
    scored = res["scored"]
    for name in ARM_FLAGS:
        assert name in scored, f"arm {name} missing from smoke run"
    print(f"[self-test] 6-arm run on SMOKE_SLICE f1: "
          f"{ {k: v['score']['f1'] for k, v in scored.items()} }", flush=True)

    prec_base = scored["BASE"]["score"]["precision"]
    assert BASELINE_BAND[0] < prec_base < BASELINE_BAND[1], \
        f"BASE precision {prec_base} outside band {BASELINE_BAND}"

    # arms_differ_verified (at least one gate arm must differ from BASE at smoke, OR small-sample WARN).
    hashes = {name: v["kept_hash"] for name, v in scored.items()}
    n_distinct = len(set(hashes.values()))
    if n_distinct == 1:
        print("[self-test] WARN: all arm hashes identical at SMOKE_SLICE (gates may not bite the small "
              "smoke slice; each gate mechanism is unit-proven above + re-checked at FULL)", flush=True)
    else:
        print(f"[self-test] arms differ at smoke: {hashes}", flush=True)

    # G3 self-loop synthetic degrade-witness (must-fire proof independent of corpus): agent==patient.
    supp = defaultdict(int)
    t_loop = _synthetic_tagged([("Tom", "NNP"), ("saw", "VBD"), ("Tom", "NNP")])
    heads_loop = {1: 2, 3: 2}  # Tom(1)->saw(2); Tom(3)->saw(2)
    # force both candidates PATIENT via a stub classifier to guarantee the self-loop path is reached
    class _AllPatient:
        def predict(self, feats):
            return "PATIENT"
    # resolved_agent in production is always the lowercased `low` form, so the carried agent here is "tom".
    base_loop, _, _ = clause_predicate_pass_gated(t_loop, heads_loop, _AllPatient(), lambda v: True, "tom",
                                                  None, False, False, False, False, defaultdict(int))
    g3_loop, _, _ = clause_predicate_pass_gated(t_loop, heads_loop, _AllPatient(), lambda v: True, "tom",
                                                None, False, False, True, False, supp)
    assert any(t[1] == t[2] for t in base_loop), f"G3 witness setup wrong: base has no self-loop {base_loop}"
    assert not any(t[1] == t[2] for t in g3_loop), f"G3 did NOT drop the self-loop: {g3_loop}"
    print(f"[self-test] G3 degrade-witness PASS: base emits self-loop {base_loop}, G3 drops it "
          f"(supp={dict(supp)})", flush=True)

    # G4 governing-prep synthetic degrade-witness: patient governed by a stripped preposition.
    supp4 = defaultdict(int)
    t_gp = _synthetic_tagged([("He", "PRP"), ("told", "VBD"), ("them", "PRP"), ("in", "IN"),
                              ("haste", "NN")])
    # both 'them'(2) and 'haste'(4) route to 'told'(1); haste is object-of 'in' -> G4 excludes it
    heads_gp = {1: 2, 3: 2, 5: 2}
    class _PatientBoth:
        def predict(self, feats):
            return "PATIENT"
    base_gp, _, _ = clause_predicate_pass_gated(t_gp, heads_gp, _PatientBoth(), lambda v: True, "He",
                                                None, False, False, False, False, defaultdict(int))
    g4_gp, _, _ = clause_predicate_pass_gated(t_gp, heads_gp, _PatientBoth(), lambda v: True, "He",
                                              None, False, False, False, True, supp4)
    assert any(t[2] == "haste" for t in base_gp), f"G4 witness setup wrong: base missing 'haste' {base_gp}"
    assert not any(t[2] == "haste" for t in g4_gp), f"G4 did NOT exclude prep-governed 'haste': {g4_gp}"
    print(f"[self-test] G4 degrade-witness PASS: base emits prep-governed 'haste', G4 excludes it "
          f"(supp={dict(supp4)})", flush=True)

    # G1 predicate-drop synthetic degrade-witness: a contracted modal tagged VB* is dropped as a predicate.
    t_c = _synthetic_tagged([("He", "PRP"), ("won't", "VBP"), ("it", "PRP")])
    preds_all = M.content_verb_indices(t_c)
    assert 1 in preds_all, f"G1 witness setup wrong: 'won't'@VBP not enumerated as predicate {preds_all}"
    preds_g1 = [i for i in preds_all if not is_contracted_aux(t_c[i][1])]
    assert 1 not in preds_g1, f"G1 did NOT drop the contracted-modal predicate: {preds_g1}"
    print(f"[self-test] G1 degrade-witness PASS: base enumerates 'won't'@VBP {preds_all}, G1 drops it "
          f"{preds_g1}", flush=True)

    # determinism: two BASE runs identical.
    _, kept2, _ = build_arm(SMOKE_SLICE, W, clf, M.build_learned_admissibility(
        build_arm(SMOKE_SLICE, W, clf, lambda v: True, None, gold, ARM_FLAGS["BASE"],
                  collect_evidence=True)[2]), V3.build_sel_fn(ratings_table), gold, ARM_FLAGS["BASE"])
    _, kept3, _ = build_arm(SMOKE_SLICE, W, clf, M.build_learned_admissibility(
        build_arm(SMOKE_SLICE, W, clf, lambda v: True, None, gold, ARM_FLAGS["BASE"],
                  collect_evidence=True)[2]), V3.build_sel_fn(ratings_table), gold, ARM_FLAGS["BASE"])
    assert M.arm_hash(kept2) == M.arm_hash(kept3), "non-deterministic BASE output across identical runs"
    print("[self-test] deterministic (two identical BASE runs produce identical kept-tuple hash)", flush=True)

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

    def _m(name, key):
        return scored[name]["score"][key]

    base = scored["BASE"]["score"]
    comp = scored["COMPOSED"]["score"]
    base_combined_fp = base["subcat_fp"] + base["spurious_verb_fp"]
    comp_combined_fp = comp["subcat_fp"] + comp["spurious_verb_fp"]
    fp_reduction = base_combined_fp - comp_combined_fp
    recall_drop = round(base["recall"] - comp["recall"], 4)

    # per-gate individual effect (single-gate arm vs BASE).
    per_gate = {}
    for gate_arm in ("G1_CONTRACTION", "G2_DOBJ", "G3_SELFLOOP", "G4_GOVPREP"):
        s = scored[gate_arm]["score"]
        per_gate[gate_arm] = dict(
            fired=(scored[gate_arm]["kept_hash"] != scored["BASE"]["kept_hash"]),
            spurious_verb_fp=s["spurious_verb_fp"], subcat_fp=s["subcat_fp"],
            combined_fp=s["subcat_fp"] + s["spurious_verb_fp"],
            combined_fp_reduction=base_combined_fp - (s["subcat_fp"] + s["spurious_verb_fp"]),
            precision=s["precision"], recall=s["recall"], f1=s["f1"],
            recall_drop=round(base["recall"] - s["recall"], 4),
            n_lost_covered=len(res["lost_by_arm"][gate_arm]),
            suppression_counts=res["supp_by_arm"][gate_arm])
    n_gates_fired = sum(1 for g in per_gate.values() if g["fired"])
    # a gate "fires cleanly" = fired AND no recall regression from that gate alone.
    n_gates_clean = sum(1 for g in per_gate.values() if g["fired"] and g["recall_drop"] <= 0.0)

    base_hash_ok = (scored["BASE"]["kept_hash"] == V3_BASE_HASH)
    repro_counts_ok = (base["subcat_fp"] == V3_BASE_SUBCAT_FP and
                       base["spurious_verb_fp"] == V3_BASE_SPURIOUS_FP and
                       abs(base["f1"] - V3_BASE_F1) < 1e-6)

    f1_nonregress = (comp["f1"] >= base["f1"])
    precision_up = (comp["precision"] > base["precision"])

    hard_fail_reasons = []
    if not base_hash_ok:
        hard_fail_reasons.append(f"P1 reproduction FAILED: BASE kept_hash={scored['BASE']['kept_hash']} "
                                 f"!= V3 {V3_BASE_HASH}")
    if recall_drop > RECALL_RETENTION_MB:
        hard_fail_reasons.append(f"recall killed: COMPOSED recall drop {recall_drop} > {RECALL_RETENTION_MB}")
    if fp_reduction <= 0:
        hard_fail_reasons.append(f"no FP reduction: combined(spurious+subcat) FP {comp_combined_fp} "
                                 f">= base {base_combined_fp}")
    if not f1_nonregress:
        hard_fail_reasons.append(f"f1 regressed: COMPOSED f1 {comp['f1']} < base {base['f1']}")
    if n_gates_fired == 0:
        hard_fail_reasons.append("no gate fired on the corpus (all 4 single-gate arms == BASE)")

    hard_pass = (base_hash_ok and recall_drop <= RECALL_RETENTION_OK and
                 fp_reduction >= FP_REDUCTION_HARD_PASS and precision_up and f1_nonregress and
                 n_gates_clean >= 1)

    if hard_fail_reasons:
        verdict = "HARD_FAIL"
        vmsg = "HARD_FAIL: " + "; ".join(hard_fail_reasons)
    elif hard_pass:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS: P1 reproduced (BASE hash={V3_BASE_HASH}); combined(spurious+subcat)_fp "
                f"{base_combined_fp}->{comp_combined_fp} (-{fp_reduction}); recall {base['recall']}->"
                f"{comp['recall']} (drop {recall_drop} <= {RECALL_RETENTION_OK}); precision "
                f"{base['precision']}->{comp['precision']}; f1 {base['f1']}->{comp['f1']}; "
                f"{n_gates_fired}/4 gates fired, {n_gates_clean} clean.")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: P1 reproduced; combined_fp {base_combined_fp}->{comp_combined_fp} "
                f"(-{fp_reduction}); recall drop {recall_drop}; precision {base['precision']}->"
                f"{comp['precision']}; f1 {base['f1']}->{comp['f1']}; {n_gates_fired}/4 gates fired. "
                f"Below HARD_PASS FP-reduction bar ({FP_REDUCTION_HARD_PASS}) or recall/precision short.")

    elapsed = round(time.perf_counter() - t0, 2)
    arms_out = {}
    for name, v in scored.items():
        s = v["score"]
        arms_out[name] = dict(f1=s["f1"], precision=s["precision"], recall=s["recall"],
                              recall_ceiling=v["recall_ceiling"], n_pred=s["n_pred"],
                              subcat_fp=s["subcat_fp"], within_frame_fp=s["within_frame_fp"],
                              spurious_verb_fp=s["spurious_verb_fp"], total_fp=s["total_fp"],
                              kept_hash=v["kept_hash"], suppression_counts=res["supp_by_arm"][name])

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: BASE_hash_ok={base_hash_ok} | combined(spurious+subcat)_fp "
                 f"{base_combined_fp}->{comp_combined_fp} (-{fp_reduction}) | recall {base['recall']}->"
                 f"{comp['recall']} | precision {base['precision']}->{comp['precision']} | f1 {base['f1']}->"
                 f"{comp['f1']} | gates_fired={n_gates_fired}/4 clean={n_gates_clean}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        n_sentences=len(res["arms"]["BASE"]),
        one_variable="which structural emission gate(s) are on (G1 contraction / G2 verb-class+dobj / "
                     "G3 self-loop / G4 governing-prep), holding the reader's routing/labeling/learned "
                     "admissibility gate byte-identical to V3 across arms",
        p1_reproduction=dict(base_hash_ok=base_hash_ok, repro_counts_ok=repro_counts_ok,
                             base_kept_hash=scored["BASE"]["kept_hash"], v3_kept_hash=V3_BASE_HASH,
                             base_subcat_fp=base["subcat_fp"], base_spurious_verb_fp=base["spurious_verb_fp"],
                             base_f1=base["f1"]),
        bands=dict(RECALL_RETENTION_OK=RECALL_RETENTION_OK, RECALL_RETENTION_MB=RECALL_RETENTION_MB,
                   FP_REDUCTION_HARD_PASS=FP_REDUCTION_HARD_PASS, V3_BASE_HASH=V3_BASE_HASH),
        composed=dict(fp_reduction=fp_reduction, base_combined_fp=base_combined_fp,
                      comp_combined_fp=comp_combined_fp, recall_drop=recall_drop,
                      precision_up=precision_up, f1_nonregress=f1_nonregress,
                      n_gates_fired=n_gates_fired, n_gates_clean=n_gates_clean,
                      composed_suppression_counts=res["supp_by_arm"]["COMPOSED"]),
        per_gate=per_gate,
        arms=arms_out,
        lost_covered_by_arm={k: [list(x) for x in v[:40]] for k, v in res["lost_by_arm"].items()},
        n_lost_covered_by_arm={k: len(v) for k, v in res["lost_by_arm"].items()},
        parser_info=parser_info,
        cited_base=dict(source="data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json",
                        arm="V3_INTEGRATED", f1=V3_BASE_F1, subcat_fp=V3_BASE_SUBCAT_FP,
                        spurious_verb_fp=V3_BASE_SPURIOUS_FP, kept_hash=V3_BASE_HASH),
        scope_caveat=(
            "Parser trained on UD-EWT (out-of-domain to 19th-c. McGuffey prose, same untested transfer "
            "V3/M/audit already flag). Gates are FIXED structural rules (no learned weight). BASE reproduces "
            "V3 byte-identically (P1). Precision-side result; CLAIM-VET-pending; strategic read = HYPOTHESIS "
            "pending skunkworks landed-VET. Pluggable: clause_predicate_pass_gated drops into the "
            "consolidated reader by importing this module and flipping the 4 flags."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"], flush=True)
    print("verdict:", verdict, flush=True)
    print("verdict_msg:", vmsg, flush=True)
    print("arms:", json.dumps(arms_out, indent=1), flush=True)
    print("per_gate:", json.dumps(per_gate, indent=1), flush=True)
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
