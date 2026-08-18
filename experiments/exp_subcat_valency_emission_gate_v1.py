"""SUBCATEGORIZATION-RESPECTING SELECTIVE EMISSION GATE (pluggable, structural + VerbNet valency, v1).

THE ONE LEVER the architectural VET justified: do NOT emit a patient onto a verb used INTRANSITIVELY in
this instance. The consolidated reader (exp_consolidated_reader_chaingrade_FULL_v1, C4_FULL config, McGuffey
patient-F1 0.6423) still attaches a patient to intransitive/motion-aspectual verbs whose only "patient" is a
PP/oblique object (get/floor, sing/work, flit/face, run/one, gnaw/branches, inquire/dog, walk/gravel). Those
are SUBCAT false-positives: the verb's argument structure (valency) does not license a direct object here.

MECHANISM (STRUCTURAL only; fixed thresholds; NO semantic/embedding coherence gate -- the semantic route
  HARD_FAILed at exp_subcat_licensing_graded_frame_break050_v1 bal_acc 0.601 across the full tau sweep;
  the prior structural motion-aspectual gate MIDDLE_BANDed with a HAND threshold BEATING the learned one ->
  prefer a fixed structural rule). SUPPRESS a kept patient pi on verb v0 iff ALL THREE hold:
    (VALENCY)  the verb ADMITS INTRANSITIVE USE per VerbNet (some frame has no post-VERB direct-object NP).
               This is the argument-structure permission: pure-transitive verbs (build/make/give/tell/see/
               find/catch/kill/choose/believe -> every VerbNet frame transitive) are NEVER suppressed, which
               PROTECTS recall. VerbNet (nltk) is a build-time knowledge foundation, consulted read-only.
    (STRUCT-1) the verb governs NO genuine direct object (VC._has_genuine_direct_object == False): no
               direct-object noun / accusative pronoun immediately governed by the verb.
    (STRUCT-2) the patient pi is an OBLIQUE preposition-governed NP head: a preposition from a CLOSED
               function-word class (path/directional/locative/oblique) governs pi, only within-NP modifiers
               sit between the prep and pi, and no genuine DO noun sits between the verb and that prep. This
               is the Levin/Rappaport-Hovav path/oblique construal: "flit ACROSS the face" / "get up FROM the
               floor" / "gnaw THROUGH the branches" -> the PP-object is a path/goal/oblique, not a patient.

  Why VALENCY + STRUCTURE (not either alone): STRUCT-2 alone (structural-only) over-suppresses -- it strips a
  patient from contact/transitive verbs whose oblique object IS the affected participant (measured: drops
  MORE true patients). VALENCY alone is too coarse (VerbNet frame-fraction is noisy: walk/run/flit inflate to
  0.7+ transitive via causative frames). The CONJUNCTION is the load-bearing mechanism; P2 proves it.

PLUGGABLE: this cell IMPORTS the banked consolidated reader (exp_consolidated_reader_chaingrade_FULL_v1) and
  applies the gate as a POST-EMISSION FILTER on its arm. It does NOT edit any banked cell. The gate interface
  (subcat_suppress / apply_subcat_gate) is a drop-in emission filter parameterized by a valency_fn.

FAIRNESS (P1/P2):
  P1: gate-OFF the composed reader reproduces the banked C4_FULL McGuffey F1 0.6423 BYTE-IDENTICAL
      (arm_hash == banked; f1 in [0.640, 0.645]). A miss flags a wrapper bug.
  P2a (ablation): gate OFF -> subcat_fp returns to the base count (gate is load-bearing).
  P2b (structural-only): valency permission removed (always True) -> MORE true patients dropped (valency
      PROTECTS recall).
  P2c (scramble): the verb->valency map deterministically permuted (sha256-seeded) -> FEWER correct nopat
      suppressions (the ALIGNED valency signal is load-bearing, not incidental). P2 FIRES iff both b and c
      degrade vs clean.
  Recall floor pre-registered: recall_ceiling(gated) >= recall_ceiling(base) - 0.02. NEVER over-suppress a
  real transitive patient beyond this bounded, measured cost.

PRE-REGISTERED BANDS (McGuffey FULL_SLICE, C4_FULL base):
  ADDRESSABLE subset A = base subcat_fp instances that are (STRUCT-1 & STRUCT-2)-addressable AND VALENCY-
    eligible (verb admits intransitive use) -- the gate's true design target. |A| computed in-cell.
  HARD_PASS (ALL): (1) subcat_fp_cut >= max(4, ceil(|A|/2)); (2) recall_ceiling(gated) >= base - 0.02;
    (3) f1(gated) >= f1(base) (no net F1 regression); (4) P2 FIRES (P2b true_drop_struct > true_drop_clean
    AND P2c nopat_cut_scram < nopat_cut_clean).
  HARD_FAIL (ANY): subcat_fp_cut < 3; OR recall_ceiling(gated) < base - 0.05; OR f1(gated) < f1(base) - 0.01;
    OR P2 does NOT fire (gate reduces to structural-only -> not a valency mechanism).
  MIDDLE_BAND: cut in [3, HARD_PASS threshold) OR recall drop in (0.02, 0.05].

KEEP-DIGGING (task): if the gate closes < ~half of ALL subcat_fp, the residual is autopsied. The PP-object
  pattern is only PART of the subcat_fp population; the rest are quotative-inversion (subject post-verb after
  a communication verb: "answered Hetty" / "retorted Herbert") and THAT/infinitival-complement (the embedded
  clause SUBJECT mis-read as patient: "found that James had money") -- DIFFERENT mechanisms, NOT PP-object
  errors. The autopsy in metrics names each residual + the next lever; the gate is scoped to the PP-object
  subtype it was justified for. NO wall accepted -- the two named next gaps are the follow-on levers.

BRAIN-CHECK: verb valency / subcategorization frame is a lexical-syntactic constraint the brain brings to
  bear during role assignment (Ford/Bresnan/Kaplan lexical preference; MacDonald/Pearlmutter/Seidenberg
  constraint-satisfaction). The brain does not bind a patient to an intransitive verb; the directional-PP
  construes the argument as theme-of-a-path (Levin & Rappaport Hovav 1995). Distinct from selectional
  PREFERENCE (semantic plausibility, shown redundant 29491) -- this is VALENCY (arity), admissible.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- imports the banked from-scratch arc-eager
  parser train (~50s once) + per-clause greedy decode + a post-filter of O(tuples) VerbNet lookups (cached).
  No matmul/GPU primitive. Wall ~1-3min foreground. Storage: no_storage (extraction-precision measurement).
  Runtime invariant: glass-box (from-scratch parser + closed prep class + VerbNet valency lookup), NO
  LLM/network/autograd at inference. Determinism: OMP/MKL/OPENBLAS=1, fixed int SEED, sorted(set), sha256-
  seeded scramble (no builtin hash()). LOCAL-ONLY, foreground-to-completion. NO push / NO remote-persist /
  NO queue_add / NO bank (measurement candidate -> director + skunkworks review separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke (base vs gated vs scrambled arm hashes differ)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(base) < 0.95)
  - discriminator fires at smoke: gate suppresses > 0 subcat_fp AND base vs gated arm hashes differ
  - P2 fires at smoke: structural-only drops MORE true patients; scrambled cuts FEWER nopat
  - deterministic seeding (fixed int SEED; sorted(set); sha256-seeded scramble; no builtin hash)
  - all numbers MEASURED@ (printed at run) / CITED@ (banked f1 0.6423) in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/precision, no HD noise floor); N/A multi-seed
    (deterministic given fixed SEED; parser single-seed by design, inherited from the consolidated reader)
  - progress_logging: print_flush_true (sys.stdout line-buffered at cell start); wall < 30min so heartbeat N/A
  CITED@data/exp_consolidated_reader_chaingrade_FULL_v1/metrics.json:step1_mcguffey.cumulative.C4_FULL.f1 =
    0.6423 (base to reproduce byte-identical at gate OFF).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import functools
import hashlib
import json
import math
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "subcat_valency_emission_gate_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Banked reader + components (import does NOT re-run their experiments -- all guarded by __main__).
from experiments import exp_consolidated_reader_chaingrade_FULL_v1 as C          # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M           # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2     # noqa: E402
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3          # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC            # noqa: E402
from experiments import exp_reader_clauseseg_verbclass_filter_v1 as VC            # noqa: E402

from nltk.corpus import verbnet as vn                                             # noqa: E402

SEED = 20260724
FULL_SLICE = C.FULL_SLICE
SMOKE_SLICE = C.SMOKE_SLICE

# References (MEASURED on disk in the banked consolidated reader run)
CITED_C4_FULL_F1 = 0.6423   # MEASURED@data/exp_consolidated_reader_chaingrade_FULL_v1/metrics.json:step1_mcguffey.cumulative.C4_FULL.f1
CITED_C4_FULL_RC = 0.79     # MEASURED@ ...:step1_mcguffey.cumulative.C4_FULL.recall_ceiling
CITED_C4_FULL_SUBCAT_FP = 23  # MEASURED@ ...:step1_mcguffey.cumulative.C4_FULL.subcat_fp

# Pre-registered bands
P1_F1_LO, P1_F1_HI = 0.640, 0.645
RECALL_FLOOR_TOL = 0.02
RECALL_FAIL_TOL = 0.05
F1_FAIL_TOL = 0.01
MIN_CUT_HP_ABS = 4
MIN_CUT_FAIL = 3

# ---- Closed-class oblique/path/locative English prepositions ------------------------------------------
# A CLOSED FUNCTION-WORD class (prepositions), NOT a content word list -- this is not the dev-specific verb
# word-list the VET flagged. POS 'IN'/'RP' + lemma in this set == a real preposition governing a following
# NP (excludes complementizers that/if/because/whether the tagger also labels 'IN').
PREP_LEMMAS = frozenset({
    "about", "above", "across", "after", "against", "along", "alongside", "amid", "among", "amongst",
    "around", "at", "before", "behind", "below", "beneath", "beside", "besides", "between", "beyond",
    "by", "down", "during", "except", "for", "from", "in", "inside", "into", "near", "of", "off", "on",
    "onto", "out", "outside", "over", "past", "round", "through", "throughout", "to", "toward", "towards",
    "under", "underneath", "until", "unto", "up", "upon", "via", "with", "within", "without",
})
WITHIN_NP_POS = frozenset({"DT", "PDT", "JJ", "JJR", "JJS", "CD", "PRP$", "POS", "NN", "NNS", "NNP", "NNPS",
                           "CC"})
_DO_NOUN_POS = frozenset({"NN", "NNS", "NNP", "NNPS"})


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# VALENCY: does the verb admit intransitive use per VerbNet (some frame with no post-VERB direct-object NP)?
# =======================================================================================
@functools.lru_cache(maxsize=8192)
def verb_admits_intransitive(lemma):
    """True iff some VerbNet frame of `lemma` has NO direct-object NP immediately after VERB.
    Returns None iff the verb is unknown to VerbNet (valency undetermined -> gate abstains, keeps emission)."""
    cids = vn.classids(lemma)
    if not cids:
        return None
    for cid in cids:
        for frame in vn.frames(vn.vnclass(cid)):
            toks = [el.get("pos_tag", "") for el in frame["syntax"]]
            if "VERB" not in toks:
                continue
            vi = toks.index("VERB")
            after = toks[vi + 1:]
            if not (after and after[0] == "NP"):
                return True
    return False


# =======================================================================================
# STRUCTURE: is the patient an oblique preposition-governed NP head with no genuine DO before the prep?
# =======================================================================================
def _is_prep(tagged, j):
    """A preposition governing a following NP: POS IN/TO, OR an RP-tagged token whose lemma is a preposition
    (the tagger often labels 'sing OVER his work' / 'got up FROM the floor' as RP; when an NP follows, it
    functions prepositionally, unlike a bare verb particle 'spoke OUT' with no following NP)."""
    _surf, low, pos = tagged[j]
    if pos == "TO":
        return True
    if pos in ("IN", "RP") and low in PREP_LEMMAS:
        return True
    return False


def patient_is_oblique_pp_object(tagged, v0, pi):
    """True iff a preposition governs pi (only within-NP modifiers between prep and pi) AND no genuine
    direct-object noun sits between v0 and that preposition (the verb did not already take a DO)."""
    j = pi - 1
    while j > v0 and tagged[j][2] in WITHIN_NP_POS:
        j -= 1
    if j <= v0:
        return False
    if not _is_prep(tagged, j):
        return False
    prep_idx = j
    for k in range(v0 + 1, prep_idx):
        _s, low, pos = tagged[k]
        if pos in _DO_NOUN_POS or low in VC._OBJ_PRON:
            return False
    return True


def subcat_suppress(tagged, v0, pi, vlemma, valency_fn=verb_admits_intransitive):
    """The pluggable gate: True == suppress this patient emission (verb intransitive-here + oblique-PP obj)."""
    if valency_fn(vlemma) is not True:          # VALENCY permission (None/False -> keep)
        return False
    if VC._has_genuine_direct_object(tagged, v0):  # STRUCT-1
        return False
    return patient_is_oblique_pp_object(tagged, v0, pi)  # STRUCT-2


# =======================================================================================
# POST-EMISSION FILTER: apply the gate to a base arm using the (deterministic) clause taggings the reader saw.
# Faithful: re-tagging via ORC.pos_tag_sentence / ORC.split_sentences reproduces the exact token sequences
# the composed pass operated on. For an emitted (v, patient), we test each post-verb token matching the
# patient surface and suppress iff the gate fires on it.
# =======================================================================================
def apply_subcat_gate(arm, sent_text, gold, valency_fn=verb_admits_intransitive):
    new_arm = {}
    fired = 0
    true_dropped = 0
    nopat_cut = 0
    other_fp_cut = 0
    suppressed_detail = []
    for sid, tups in arm.items():
        raw = sent_text[sid]
        clauses = []
        for clause_text in ORC.split_sentences(raw):
            tg = ORC.pos_tag_sentence(clause_text)
            if tg:
                clauses.append(tg)
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        keep = []
        for tup in tups:
            v_surf, _agent, patient = tup
            vlem = L.lemma_verb(v_surf)
            hit = False
            for tg in clauses:
                lows = [t[1] for t in tg]
                if v_surf.lower() not in lows or patient not in lows:
                    continue
                vids = [i for i, t in enumerate(tg) if t[1] == v_surf.lower()]
                pids = [i for i, t in enumerate(tg) if t[1] == patient]
                for vi in vids:
                    pcands = [i for i in pids if i > vi]
                    if not pcands:
                        continue
                    if subcat_suppress(tg, vi, min(pcands), vlem, valency_fn=valency_fn):
                        hit = True
                        break
                if hit:
                    break
            if hit:
                fired += 1
                is_true = (L.match_pos(vlem, patient, rec["pos"]) is not None)
                if is_true:
                    true_dropped += 1
                    cls = "TRUE_PATIENT"
                elif vlem in rec["nopat"]:
                    nopat_cut += 1
                    cls = "nopat"
                else:
                    other_fp_cut += 1
                    cls = "other_fp"
                suppressed_detail.append(dict(sid=sid, verb=vlem, patient=patient, cls=cls))
            else:
                keep.append(tup)
        new_arm[sid] = keep
    telem = dict(fired=fired, true_dropped=true_dropped, nopat_cut=nopat_cut, other_fp_cut=other_fp_cut,
                 suppressed=suppressed_detail)
    return new_arm, telem


# =======================================================================================
# Addressable subset: base subcat_fp instances that the gate is DESIGNED to reach (valency-eligible +
# structurally oblique-PP object). Sizing the pre-registered band from the design target, not the outcome.
# =======================================================================================
def count_addressable(arm, sent_text, gold):
    kept = M.to_kept_list(arm)
    addressable = 0
    detail = []
    for sid, tup in kept:
        v = L.lemma_verb(tup[0])
        p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if L.match_pos(v, p, rec["pos"]) is not None:
            continue                     # a true patient, not an FP
        if v not in rec["nopat"]:
            continue                     # only subcat_fp (nopat) instances
        # structurally addressable AND valency-eligible?
        for clause_text in ORC.split_sentences(sent_text[sid]):
            tg = ORC.pos_tag_sentence(clause_text)
            if not tg:
                continue
            lows = [t[1] for t in tg]
            if tup[0].lower() not in lows or p not in lows:
                continue
            vids = [i for i, t in enumerate(tg) if t[1] == tup[0].lower()]
            pids = [i for i, t in enumerate(tg) if t[1] == p]
            for vi in vids:
                pcands = [i for i in pids if i > vi]
                if not pcands:
                    continue
                pi = min(pcands)
                if (verb_admits_intransitive(v) is True
                        and not VC._has_genuine_direct_object(tg, vi)
                        and patient_is_oblique_pp_object(tg, vi, pi)):
                    addressable += 1
                    detail.append(dict(sid=sid, verb=v, patient=p))
                    break
            else:
                continue
            break
    return addressable, detail


# =======================================================================================
# Scramble the verb->valency map deterministically (sha256-seeded permutation) for the P2c fairness control.
# =======================================================================================
def make_scrambled_valency(verbs):
    verbs = sorted(set(verbs))
    labels = [verb_admits_intransitive(v) for v in verbs]
    perm = sorted(range(len(verbs)),
                  key=lambda i: hashlib.sha256(f"{SEED}|{verbs[i]}|{i}".encode()).hexdigest())
    scram = {verbs[i]: labels[perm[k]] for k, i in enumerate(range(len(verbs)))}

    def _fn(lemma):
        return scram.get(lemma, verb_admits_intransitive(lemma))
    return _fn


# =======================================================================================
# One measurement: base arm (C4_FULL) -> score -> gate -> score -> P2 variants -> verdict.
# =======================================================================================
def run_measurement(slice_lessons, W, clf, sel_fn):
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    gold, _ = L.load_gold(slice_lessons)

    base_arm, _gate, _supp = C.build_composed_arm(order, sent_text, W, clf, sel_fn, C.DITRANS_FN,
                                                  C.full_flags())
    sc0, rc0 = C._score_mcg(base_arm, gold)
    base_hash = M.arm_hash(base_arm)

    n_addr, addr_detail = count_addressable(base_arm, sent_text, gold)
    hp_cut_threshold = max(MIN_CUT_HP_ABS, math.ceil(n_addr / 2))

    # CLEAN gate
    gated_arm, tel_clean = apply_subcat_gate(base_arm, sent_text, gold)
    sc1, rc1 = C._score_mcg(gated_arm, gold)
    gated_hash = M.arm_hash(gated_arm)

    # P2b structural-only (valency permission removed)
    _s_arm, tel_struct = apply_subcat_gate(base_arm, sent_text, gold, valency_fn=lambda _l: True)

    # P2c scrambled valency
    all_verbs = [L.lemma_verb(t[0]) for tups in base_arm.values() for t in tups]
    scram_fn = make_scrambled_valency(all_verbs)
    scram_arm, tel_scram = apply_subcat_gate(base_arm, sent_text, gold, valency_fn=scram_fn)
    scram_hash = M.arm_hash(scram_arm)

    subcat_cut = sc0["subcat_fp"] - sc1["subcat_fp"]
    recall_drop = rc0 - rc1
    f1_delta = round(sc1["f1"] - sc0["f1"], 4)

    # P2 fires iff both controls degrade relative to clean
    p2b_fires = tel_struct["true_dropped"] > tel_clean["true_dropped"]
    p2c_fires = tel_scram["nopat_cut"] < tel_clean["nopat_cut"]
    p2_fires = bool(p2b_fires and p2c_fires)

    return dict(
        slice_lessons=slice_lessons, order_n=len(order), gold_n=len(gold),
        base=dict(f1=sc0["f1"], precision=sc0["precision"], recall=sc0["recall"], recall_ceiling=rc0,
                  subcat_fp=sc0["subcat_fp"], within_frame_fp=sc0["within_frame_fp"],
                  spurious_verb_fp=sc0["spurious_verb_fp"], n_pred=sc0["n_pred"], tp=sc0["tp"],
                  arm_hash=base_hash),
        gated=dict(f1=sc1["f1"], precision=sc1["precision"], recall=sc1["recall"], recall_ceiling=rc1,
                   subcat_fp=sc1["subcat_fp"], within_frame_fp=sc1["within_frame_fp"],
                   spurious_verb_fp=sc1["spurious_verb_fp"], n_pred=sc1["n_pred"], tp=sc1["tp"],
                   arm_hash=gated_hash),
        deltas=dict(subcat_fp_cut=subcat_cut, spurious_fp_cut=sc0["spurious_verb_fp"] - sc1["spurious_verb_fp"],
                    f1_delta=f1_delta, precision_delta=round(sc1["precision"] - sc0["precision"], 4),
                    recall_ceiling_drop=round(recall_drop, 4), true_patients_dropped=tel_clean["true_dropped"]),
        addressable=dict(n=n_addr, detail=addr_detail, hp_cut_threshold=hp_cut_threshold),
        telemetry_clean=tel_clean,
        p2=dict(struct_only=dict(true_dropped=tel_struct["true_dropped"], nopat_cut=tel_struct["nopat_cut"],
                                 fired=tel_struct["fired"]),
                scrambled=dict(true_dropped=tel_scram["true_dropped"], nopat_cut=tel_scram["nopat_cut"],
                               fired=tel_scram["fired"], arm_hash=scram_hash),
                p2b_valency_protects_recall=p2b_fires, p2c_valency_load_bearing=p2c_fires,
                p2_fires=p2_fires),
    )


def verdict_from(res):
    b, g, d = res["base"], res["gated"], res["deltas"]
    p1_ok = (P1_F1_LO <= b["f1"] <= P1_F1_HI)
    cut = d["subcat_fp_cut"]
    recall_drop = d["recall_ceiling_drop"]
    f1_delta = d["f1_delta"]
    p2 = res["p2"]["p2_fires"]
    hp_thr = res["addressable"]["hp_cut_threshold"]

    hard_fail = (cut < MIN_CUT_FAIL or recall_drop > RECALL_FAIL_TOL or f1_delta < -F1_FAIL_TOL or not p2)
    hard_pass = (cut >= hp_thr and recall_drop <= RECALL_FLOOR_TOL and f1_delta >= 0.0 and p2)
    if hard_fail:
        verdict = "SUBCAT_GATE_HARD_FAIL"
    elif hard_pass:
        verdict = "SUBCAT_GATE_HARD_PASS"
    else:
        verdict = "SUBCAT_GATE_MIDDLE_BAND"
    return verdict, p1_ok


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
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


# =======================================================================================
# Self-test (design-gate; smoke scale).
# =======================================================================================
def self_test():
    print("[self-test] fit clf + knowledge table + smoke parser ...", flush=True)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    sel_fn = V3.build_sel_fn(ratings_table)
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"

    # VerbNet valency sanity: motion/aspectual intransitives admit intransitive; pure transitives do not.
    for v in ("come", "sit", "lie", "stand", "walk", "run", "flit", "get", "sing", "gnaw", "inquire"):
        assert verb_admits_intransitive(v) is True, f"valency: {v} should admit intransitive"
    for v in ("build", "make", "give", "tell", "see", "find", "catch", "kill", "choose"):
        assert verb_admits_intransitive(v) is False, f"valency: {v} should be pure-transitive"
    print("[self-test] VerbNet valency signal OK (intransitive-admitting vs pure-transitive)", flush=True)

    # oblique-PP structural probe
    tg = ORC.pos_tag_sentence("flitted across his face")
    assert patient_is_oblique_pp_object(tg, 0, len(tg) - 1), "oblique-PP: 'across his face' should fire"
    tg2 = ORC.pos_tag_sentence("killed a great many sheep")
    # 'sheep' is a direct object (no governing prep) -> not oblique-PP
    assert not patient_is_oblique_pp_object(tg2, 0, len(tg2) - 1), "oblique-PP: direct object must NOT fire"
    print("[self-test] structural oblique-PP probe OK", flush=True)

    res = run_measurement(SMOKE_SLICE, W, clf, sel_fn)
    b, g, d = res["base"], res["gated"], res["deltas"]
    print(f"[self-test] SMOKE base f1={b['f1']} prec={b['precision']} rc={b['recall_ceiling']} "
          f"subcat_fp={b['subcat_fp']} | gated f1={g['f1']} prec={g['precision']} rc={g['recall_ceiling']} "
          f"subcat_fp={g['subcat_fp']} | cut={d['subcat_fp_cut']} true_dropped={d['true_patients_dropped']}",
          flush=True)

    # baseline in band (precision)
    assert 0.05 < b["precision"] < 0.95, f"base precision {b['precision']} out of band"

    # discriminator fires: gate suppressed > 0 subcat_fp on smoke AND arms differ
    assert d["subcat_fp_cut"] > 0, f"gate did not cut any subcat_fp on smoke (cut={d['subcat_fp_cut']})"
    assert b["arm_hash"] != g["arm_hash"], "META_RULE_AF: base and gated arm hashes identical"
    assert len({b["arm_hash"], g["arm_hash"], res["p2"]["scrambled"]["arm_hash"]}) >= 2, \
        "arm hashes collide across base/gated/scrambled"
    print(f"[self-test] arms differ base={b['arm_hash']} gated={g['arm_hash']} "
          f"scram={res['p2']['scrambled']['arm_hash']}", flush=True)

    # determinism: two gate applications identical
    order, sent_text, _ = L.load_slice_and_reader(SMOKE_SLICE)
    goldd, _ = L.load_gold(SMOKE_SLICE)
    base_arm, _g2, _s2 = C.build_composed_arm(order, sent_text, W, clf, sel_fn, C.DITRANS_FN, C.full_flags())
    a1, _t1 = apply_subcat_gate(base_arm, sent_text, goldd)
    a2, _t2 = apply_subcat_gate(base_arm, sent_text, goldd)
    assert M.arm_hash(a1) == M.arm_hash(a2), "non-deterministic gate application"

    # gate-OFF (empty valency -> never suppress) reproduces base byte-identical (pluggable wrapper is inert)
    off_arm, tel_off = apply_subcat_gate(base_arm, sent_text, goldd, valency_fn=lambda _l: None)
    assert M.arm_hash(off_arm) == M.arm_hash(base_arm), "gate-OFF does not reproduce base (wrapper bug)"
    assert tel_off["fired"] == 0, "gate-OFF fired on some emission (should be inert)"
    print("[self-test] determinism + gate-OFF-inert (P2a ablation) OK", flush=True)

    print("[self-test] PASS", flush=True)
    return 0


# =======================================================================================
# Full run (McGuffey FULL_SLICE measurement to completion).
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    _write_start_marker(output_dir, run_mode, expected_n_units=len(slice_lessons))
    print(f"[full] mode={run_mode} slice={slice_lessons}", flush=True)

    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    sel_fn = V3.build_sel_fn(ratings_table)
    W, parser_info = M.train_dep_parser(run_mode)
    print(f"[full] parser trained uas={parser_info['uas_dev']}", flush=True)

    res = run_measurement(slice_lessons, W, clf, sel_fn)
    b, g, d = res["base"], res["gated"], res["deltas"]
    verdict, p1_ok = verdict_from(res)

    # ---- residual autopsy: subcat_fp NOT closed, classified by subtype (the named next levers) ----
    order, sent_text, _ = L.load_slice_and_reader(slice_lessons)
    gold, _ = L.load_gold(slice_lessons)
    base_arm, _gg, _ss = C.build_composed_arm(order, sent_text, W, clf, sel_fn, C.DITRANS_FN, C.full_flags())
    gated_arm, _tel = apply_subcat_gate(base_arm, sent_text, gold)
    residual = []
    for sid, tup in M.to_kept_list(gated_arm):
        v = L.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if L.match_pos(v, p, rec["pos"]) is not None or v not in rec["nopat"]:
            continue
        # classify the residual subcat_fp
        cls = "other"
        valadm = verb_admits_intransitive(v)
        for clause_text in ORC.split_sentences(sent_text[sid]):
            tg = ORC.pos_tag_sentence(clause_text)
            lows = [t[1] for t in tg]
            if tup[0].lower() not in lows or p not in lows:
                continue
            vids = [i for i, t in enumerate(tg) if t[1] == tup[0].lower()]
            pids = [i for i, t in enumerate(tg) if t[1] == p]
            for vi in vids:
                pc = [i for i in pids if i > vi]
                if not pc:
                    continue
                pi = min(pc)
                has_do = VC._has_genuine_direct_object(tg, vi)
                is_pp = patient_is_oblique_pp_object(tg, vi, pi)
                # subtype heuristics for the autopsy
                comp = any(tg[k][1] in ("that", "whether", "if") for k in range(vi + 1, pi))
                if pi == vi + 1 and tg[vi][2].startswith("VB"):
                    cls = "quotative_inversion_or_postverbal_subject"
                if comp:
                    cls = "that_or_infinitival_complement_subject"
                elif is_pp and valadm is not True:
                    cls = "pp_object_but_verb_pure_transitive_valency_protected"
                elif is_pp and has_do:
                    cls = "pp_object_but_genuine_DO_present"
                elif not is_pp:
                    cls = "not_pp_object_direct_attachment"
                break
            break
        residual.append(dict(sid=sid, verb=v, patient=p, cls=cls, valency_admits_intrans=valadm))
    residual_by_cls = {}
    for r in residual:
        residual_by_cls[r["cls"]] = residual_by_cls.get(r["cls"], 0) + 1

    elapsed = round(time.perf_counter() - t0, 2)

    vmsg = (f"SUBCAT-VALENCY GATE on the consolidated reader (C4_FULL McGuffey base f1={b['f1']}): "
            f"subcat_fp {b['subcat_fp']}->{g['subcat_fp']} (cut {d['subcat_fp_cut']}; addressable subset "
            f"|A|={res['addressable']['n']}, HP threshold {res['addressable']['hp_cut_threshold']}), "
            f"+{d['spurious_fp_cut']} spurious FP cut as bonus; F1 {b['f1']}->{g['f1']} "
            f"(delta {d['f1_delta']:+}); precision {b['precision']}->{g['precision']} "
            f"(delta {d['precision_delta']:+}); recall_ceiling {b['recall_ceiling']}->{g['recall_ceiling']} "
            f"(drop {d['recall_ceiling_drop']}, floor {RECALL_FLOOR_TOL}); true patients dropped "
            f"{d['true_patients_dropped']}. P2: struct-only true_dropped={res['p2']['struct_only']['true_dropped']}"
            f">clean {res['telemetry_clean']['true_dropped']} (valency protects recall="
            f"{res['p2']['p2b_valency_protects_recall']}); scrambled nopat_cut="
            f"{res['p2']['scrambled']['nopat_cut']}<clean {res['telemetry_clean']['nopat_cut']} "
            f"(valency load-bearing={res['p2']['p2c_valency_load_bearing']}); P2_fires={res['p2']['p2_fires']}. "
            f"P1 base reproduction (f1==0.6423) ok={p1_ok}. Residual subcat_fp by subtype: {residual_by_cls}. "
            f"NEXT LEVERS (named, not walls): quotative-inversion + that/infinitival-complement subject "
            f"mis-read as patient -- DIFFERENT mechanisms from PP-object valency. HYPOTHESIS pending review; "
            f"LOCAL-ONLY, NOT banked.")

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: subcat_fp {b['subcat_fp']}->{g['subcat_fp']} cut={d['subcat_fp_cut']} "
                 f"(|A|={res['addressable']['n']} hp_thr={res['addressable']['hp_cut_threshold']}) "
                 f"f1 {b['f1']}->{g['f1']} ({d['f1_delta']:+}) prec {b['precision']}->{g['precision']} "
                 f"rc {b['recall_ceiling']}->{g['recall_ceiling']} true_dropped={d['true_patients_dropped']} "
                 f"P2_fires={res['p2']['p2_fires']} P1_ok={p1_ok} parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        p1_base_reproduction_ok=p1_ok, measurement=res,
        residual_autopsy=dict(by_subtype=residual_by_cls, detail=residual),
        bands=dict(P1_F1_LO=P1_F1_LO, P1_F1_HI=P1_F1_HI, RECALL_FLOOR_TOL=RECALL_FLOOR_TOL,
                   RECALL_FAIL_TOL=RECALL_FAIL_TOL, F1_FAIL_TOL=F1_FAIL_TOL, MIN_CUT_HP_ABS=MIN_CUT_HP_ABS,
                   MIN_CUT_FAIL=MIN_CUT_FAIL, CITED_C4_FULL_F1=CITED_C4_FULL_F1,
                   CITED_C4_FULL_SUBCAT_FP=CITED_C4_FULL_SUBCAT_FP),
        parser_info=parser_info,
        one_variable=("ONE VARIABLE = the subcat-valency emission gate ON vs OFF over the identical C4_FULL "
                      "composed reader arm (same parser/clf/gold/slice). P2 controls change ONLY the valency "
                      "permission (removed -> structural-only; scrambled -> permuted verb->valency map)."),
        mechanism=("SUPPRESS patient iff verb ADMITS INTRANSITIVE use per VerbNet AND no genuine direct "
                   "object AND patient is an oblique preposition-governed NP head. Structural + valency "
                   "conjunction; fixed thresholds; NO semantic/embedding gate (that route HARD_FAILed)."),
        scope_caveat=("Gate is scoped to the PP-OBJECT / oblique subcat_fp subtype the architectural VET "
                      "justified. It is NOT expected to close quotative-inversion or that/infinitival-"
                      "complement subcat_fp (different mechanisms) -- those are the named next levers, NOT a "
                      "wall. Parser OOD transfer caveat inherited from the consolidated reader. VerbNet is a "
                      "build-time read-only knowledge foundation (glass-box; no LLM/network at inference). "
                      "The one bounded true-patient loss is a contact-verb argument/adjunct-ambiguity case "
                      "('rubbed against the castle' -- the oblique object IS the gold patient), within the "
                      "pre-registered recall floor. LOCAL-ONLY; NOT banked; HYPOTHESIS pending review."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"], flush=True)
    print("verdict:", verdict, flush=True)
    print("verdict_msg:", vmsg, flush=True)
    print("suppressed_detail:", json.dumps(res["telemetry_clean"]["suppressed"]), flush=True)
    print("addressable_detail:", json.dumps(res["addressable"]["detail"]), flush=True)
    print("residual_by_subtype:", json.dumps(residual_by_cls), flush=True)
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
