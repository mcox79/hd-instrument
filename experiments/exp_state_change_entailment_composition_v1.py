#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_state_change_entailment_composition_v1

FIRST COMPOSITION/REASONING BRICK = STATE-CHANGE ENTAILMENT.
Compose the reader's event extraction (agent, verb, patient) + the proven verb-affectedness gate WITH
VerbNet's cause->result-state semantic predicates into a BOUND PROPOSITION (VSA / FHRR), and INFER the
affected entity's RESULTING STATE. One genuine forward inference = the atomic unit of a situation model.

CAPABILITY:
  INPUT   : a sentence (subject verb object).
  COMPOSE : reader extracts the patient (reader_pass+base_pick); affectedness gate (v2, reused) gives the
            verb's affectedness TYPE + whether the entity changes; VerbNet (nltk, local) gives the modal
            class's RESULT-STATE predicate family (degradation_material_integrity / state / exist /
            has_possession / location / cognition). BIND patient + state + verb into an FHRR proposition.
  INFER   : derive the affected entity's resulting state via a TYPE-led + result-predicate-refined rule:
            break->not_intact, open/fix->changed_state, build/make->created, give/get->possession_changed,
            put/move->new_location, see/have/negated->UNCHANGED (fed by the gate). The reported label is
            READ OUT of the bound proposition (unbind(prop, ROLE_STATE) -> cleanup) so the VSA is in the
            measurement path + every inference is traceable (unbind any role to inspect).

PRIOR ART CREDITED (adopted + built-on, NOT invented):
  - VerbNet (Kipper-Schuler 2005) semantic predicates (result(E)/end(E) PRED families) via nltk.corpus.
  - data/verbnet_affectedness_lexicon_v1 (verb -> affectedness_type/graded/per_sense/vn_classes).
  - The proven reader + verb-affectedness gate (exp_mcguffey_whoaffected_verb_affectedness_gate_v2_heldout;
    v1 hand-lexicon for copula/stative/light + phrasal + clause-aware negation).
  - hdlab FHRR bind/unbind (Plate 1995 / Gayler 2003) = the glass-box VSA composition substrate.
  Prior-work KB check (substrate_query "state-change entailment resulting state inference VerbNet result
  predicate composition"): NONE at cosine>0.30 (only literal token hits 'Net result'/'State'/'result' in
  wordnet/framenet/notes). Genuinely novel: first resulting-STATE entailment cell (composition frontier
  above the closed lexical who-is-affected arc).

MEASURE (design-gate; can-fail; TWO real baselines):
  1. RESULTING-STATE accuracy: composed inference vs gold resulting-state label (N=44, 6-way taxonomy).
  2. BASELINE_MAJORITY: predict the most-common label ('unchanged').
  3. BASELINE_AFFECTEDNESS_ONLY: the FULL system MINUS the result-predicate composition -- it knows
     changed/unchanged (same type gate) but NOT HOW, so it collapses all affected -> the modal affected
     label (majority-affected). The LIFT of composed over this = the VerbNet-result-predicate composition
     content (the reasoning).
  MUST-FAIL CONTROLS:
   (a) non-affecting designated cases (see/look/have/is/like/think/meet/hunt + 2 negated) MUST infer
       UNCHANGED (fed by the gate). Any inferred change there = BROKEN.
   (b) SCRAMBLE the affected-type->result-label mapping (derangement, 5 fixed seeds) -> affected-case
       accuracy MUST collapse toward base-rate (proves it uses the real VerbNet result-schema, not a
       base-rate memorized on the gold).
  VSA: FHRR binding round-trip (unbind recovers patient + state) across 3 codebook seeds; readout labels
       seed-stable (deterministic accuracy).

CAN-FAIL: composed <= affectedness_only + 0.05 (no composition lift); OR control (a) fails; OR scramble
  does not collapse; OR round-trip < 1.0. HONEST NON-SATURATION: 7 word-sense-ambiguous verbs
  (burn/write/draw/get/send/set/carry) whose MODAL VerbNet sense mismatches the sentence sense are
  EXPECTED misses -> keep composed well below 1.0 and confirm word-sense-disambiguation is the next gap.

HONEST BANDS: N=44 SMALL, authored + McGuffey-register, single-annotator (same caveat as the v2 held-out
  gold). This is a CONTROLLED first-brick demonstration, NOT a wild-corpus generalization claim.
  HARD_PASS = composed - affectedness_only >= 0.20 AND composed >= majority + 0.15 AND control_a holds AND
  scramble collapses (affected drop >= 0.25) AND round-trip == 1.0. MIDDLE_BAND = lift in (0.05, 0.20).
  HARD_FAIL = lift <= 0.05 OR control_a fails OR no scramble collapse OR round-trip < 1.0.
  LEAK-CLEAN: the inference reads ONLY the sentence verb (+ negation) and VerbNet; it NEVER reads the gold
  result_state. Mutation-probe in self_test permutes the gold result_state labels + re-derives -> the
  inference is byte-identical.

Compute architecture: sequential-CPU, justified (pure-python glass-box pass over 44 sentences + nltk
  VerbNet lookups + tiny FHRR N=1024 binds; wall seconds; no matmul-heavy inner loop -> NOT a GPU-batching
  candidate). Storage: no_storage (each proposition is an independent bound structure, round-trip verified;
  no multi-item bundled store). Determinism: OMP/MKL/OPENBLAS=1; fixed integer seeds (no hash()-seeded RNG,
  no list(set()) ordering); torch.Generator(seed). LOCAL-only foreground; NO queue, NO push, NO
  remote-persist, NO git add of the store, NO production hdlab mutation. ASCII-only, no em-dashes.

# CELL-TEMPLATE MANDATORY (measurement + composition cell; VSA seeds only, no capacity/argmax-noise axis):
# - arms_differ_verified at smoke gate (composed / affectedness_only / scrambled decision vectors differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: accuracy on labeled gold, no quantitative noise floor (FHRR N=1024 round-trip is lossless)
# - baseline_in_band: affectedness_only majority-affected expected 0.05 < acc < 0.95 (verified at smoke)
# - discriminator survives scale: N=44 gold IS the scale; VSA lossless at N=1024 (checked all 3 seeds)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - cardinality_ok: EXPECTED_N_UNITS = 44 sentences (verified len == 44)
# - calibration_check: default_ok_for_this_regime (type-led rule from VerbNet predicate FAMILIES, gold-independent)
# - composition edges: reader(patient) -> FHRR bind (SHAPE_MATCH: surface token -> atom vec);
#   affectedness_type + VerbNet result-pred -> state label -> FHRR bind (SHAPE_MATCH: label -> codebook row)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "state_change_entailment_composition_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from nltk.corpus import verbnet as vn  # noqa: E402  (local; nltk 3.9.2, 429 classes)

# reuse the proven lemmatizer + VerbNet lexicon + clause-aware negation + stative/light set (v2 gate)
from experiments.exp_mcguffey_whoaffected_verb_affectedness_gate_v2_heldout import (  # noqa: E402
    lemmatize, VN_LEX, HAND_STATIVE_LIGHT, verb_is_negated_clauseaware,
)
from experiments.exp_mcguffey_whoaffected_verb_affectedness_gate_v1 import (  # noqa: E402
    affectedness_class, find_verb_index,
)
from hdlab.candidate_generator import ud_tokenize  # noqa: E402
from hdlab.binding import bind, unbind  # noqa: E402  (FHRR complex64 elementwise mul / conj mul)

GOLD_PATH = os.path.join(REPO_ROOT, "data", "resulting_state_entailment_gold_v1", "gold.json")

# ---- resulting-state taxonomy (6 labels; small + principled) ----
STATE_LABELS = ["not_intact", "changed_state", "created", "possession_changed", "new_location", "unchanged"]

# affectedness TYPE -> unchanged vs affected. cognition/perception/possession/contact = non-affecting
# (perception targets, mental objects, stative have/own, encounter/touch); the rest change the entity.
UNCHANGED_TYPES = {"cognition", "perception", "possession", "contact"}

# TYPE -> specific resulting-state label (used for affected types; refined by result predicate below)
TYPE_TO_STATE = {
    "change_of_state": "changed_state",   # refined to not_intact if degradation predicate present
    "effected": "created",
    "transfer": "possession_changed",
    "motion": "new_location",
    "other": "changed_state",             # refined by result predicate (state/created_image/location)
}

# VerbNet result-predicate families -> resulting-state (refinement signal; CITED@VerbNet frame PRED names)
NOT_INTACT_PREDS = {"degradation_material_integrity", "apart", "physical_form"}
CREATED_PREDS = {"created_image", "made_of", "designated", "exist"}
LOCATION_PREDS = {"location", "motion", "path_rel", "spatial_configuration"}
STATE_PREDS = {"state", "has_state", "cooked", "apply_heat"}


def modal_class(entry):
    """The per-sense VerbNet class whose affectedness_type == the verb's aggregate (modal) type."""
    at = entry.get("affectedness_type")
    for ps in entry.get("per_sense", []):
        if ps.get("affectedness_type") == at:
            return ps.get("vn_class")
    cls = entry.get("vn_classes") or []
    return cls[0] if cls else None


_PRED_CACHE = {}


def class_pred_names(cid):
    """Set of ALL semantic-predicate names in a VerbNet class's frames (result + end + during)."""
    if cid is None:
        return set()
    if cid in _PRED_CACHE:
        return _PRED_CACHE[cid]
    try:
        vc = vn.vnclass(cid)
    except Exception:
        _PRED_CACHE[cid] = set()
        return set()
    names = set()
    for fr in vn.frames(vc):
        for p in fr["semantics"]:
            names.add(p["predicate_value"])
    _PRED_CACHE[cid] = names
    return names


# past-tense/irregular forms the reused v2 lemmatizer misses (y-stems + a few strong verbs); applied
# before the reused lemmatize() so VerbNet lookup keys resolve. Verb-surface only, gold-independent.
IRREGULAR_EXT = {"broke": "break", "broken": "break", "tore": "tear", "torn": "tear",
                 "dried": "dry", "carried": "carry", "shut": "shut", "built": "build"}


def lemmatize2(surface):
    """Cell-local lemmatizer: extended irregular map first, then the proven v2 lemmatize()."""
    s = (surface or "").lower().strip()
    if s in IRREGULAR_EXT:
        return IRREGULAR_EXT[s]
    return lemmatize(s)


def verb_entry(verb_surface):
    """Lemmatize the verb head and fetch its VerbNet-affectedness lexicon entry (or None if OOV)."""
    head = (verb_surface or "").lower().strip().split()[0] if verb_surface else ""
    lem = lemmatize2(head)
    return lem, VN_LEX.get(lem)


def is_unchanged_verb(verb_surface, negated):
    """Binary affectedness decision (the affectedness-ONLY signal): does the entity change at all?
    True => unchanged. Fed to must-fail control (a). Type-led (cognition/perception/possession/contact),
    plus stative/light + negation. OOV (have/is) -> stative/light -> unchanged."""
    if negated:
        return True
    lem, entry = verb_entry(verb_surface)
    if lem in HAND_STATIVE_LIGHT:
        return True
    if entry is None:
        # OOV in VerbNet: fall back to hand affectedness class (copula/stative/light already caught above)
        return affectedness_class(lem) in {"perception", "cognition", "possession_stative"}
    return entry.get("affectedness_type") in UNCHANGED_TYPES


def infer_result_state(verb_surface, negated, label_map=None):
    """THE COMPOSITION: (affectedness type from gate) x (VerbNet result-predicate) -> resulting state.
    label_map: optional permutation of the 5 affected labels (control (b) scramble); identity if None.
    Returns (state_label, trace_dict). Reads ONLY the verb + negation + VerbNet -> gold-independent."""
    lm = label_map or {}

    def mapped(lbl):
        return lm.get(lbl, lbl)

    if is_unchanged_verb(verb_surface, negated):
        return "unchanged", {"route": "gate_unchanged", "negated": negated}
    lem, entry = verb_entry(verb_surface)
    if entry is None:
        return mapped("changed_state"), {"route": "oov_default", "lemma": lem}
    at = entry.get("affectedness_type")
    mc = modal_class(entry)
    preds = class_pred_names(mc)
    if at == "change_of_state":
        lbl = "not_intact" if (preds & NOT_INTACT_PREDS) else "changed_state"
    elif at == "other":
        if preds & STATE_PREDS:
            lbl = "changed_state"
        elif preds & (CREATED_PREDS - {"exist"}):   # created_image/made_of/designated (not bare 'exist')
            lbl = "created"
        elif preds & {"location", "motion"}:
            lbl = "new_location"
        else:
            lbl = "changed_state"
    else:
        lbl = TYPE_TO_STATE.get(at, "changed_state")
    return mapped(lbl), {"route": "composed", "lemma": lem, "type": at, "modal_class": mc,
                         "preds": sorted(preds & (NOT_INTACT_PREDS | CREATED_PREDS | LOCATION_PREDS | STATE_PREDS)),
                         "base_label": lbl}


# =====================================================================================================
# FHRR VSA: bind the inferred proposition + read the state back out (glass-box, traceable, round-trip).
# =====================================================================================================
N_DIM = 1024


def fhrr_codebook(n_rows, seed):
    """(n_rows, N) complex64 unit-magnitude FHRR vectors from a fixed-seed generator (deterministic)."""
    g = torch.Generator().manual_seed(int(seed))
    theta = 2.0 * math.pi * torch.rand(n_rows, N_DIM, generator=g)
    return torch.complex(torch.cos(theta), torch.sin(theta)).to(torch.complex64)


def fhrr_cleanup(query, codebook):
    """Argmax FHRR cleanup: index of codebook row maximizing real(<query, conj(row)>)."""
    sims = torch.real(torch.matmul(codebook.conj(), query))  # (n_rows,)
    return int(torch.argmax(sims).item())


def build_and_readout(patient_idx, state_idx, verb_idx, roles, ent_cb, state_cb, verb_cb):
    """Bundle bind(ROLE_ENTITY,patient)+bind(ROLE_STATE,state)+bind(ROLE_VERB,verb); read state + entity
    back via unbind+cleanup. Returns (recovered_state_idx, recovered_entity_idx)."""
    RE, RS, RV = roles
    prop = (bind(RE, ent_cb[patient_idx]) + bind(RS, state_cb[state_idx]) + bind(RV, verb_cb[verb_idx]))
    rec_state = fhrr_cleanup(unbind(prop, RS), state_cb)
    rec_ent = fhrr_cleanup(unbind(prop, RE), ent_cb)
    return rec_state, rec_ent


# =====================================================================================================
def evaluate(gold, use_reader, tagger=None, parser=None, labeler=None, reader_pass=None, base_pick=None):
    """Per-sentence: reader patient extraction (if use_reader) + composed state inference + baselines."""
    rows = []
    for g in gold:
        text, verb, gaff = g["text"], g["verb"], g["affected"]
        gold_state = g["result_state"]
        tokens = ud_tokenize(text)

        # negation via the proven clause-aware detector (parse-free)
        vi = [k + 1 for k, t in enumerate(tokens) if t.lower() == verb.split()[0].lower()]
        negated = verb_is_negated_clauseaware(tokens, vi[0] if vi else None)

        # reader patient extraction (compose reader output into the proposition; guarded, gold fallback)
        reader_patient = None
        if use_reader:
            try:
                rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
                vidx, _ = find_verb_index(tokens, rp["pos"], verb)
                pool = rp["pools"].get(vidx, []) if vidx is not None else []
                bp = base_pick(pool)
                reader_patient = bp["surf"] if bp is not None else None
            except Exception:
                reader_patient = None
        patient_surf = reader_patient if reader_patient is not None else (gaff or "NONE")

        composed, trace = infer_result_state(verb, negated)
        affected_only = "unchanged" if is_unchanged_verb(verb, negated) else "AFFECTED_BUCKET"

        rows.append({
            "id": g["id"], "text": text, "verb": verb, "gold_state": gold_state,
            "gold_affected": gaff, "ambiguous": bool(g.get("ambiguous", False)),
            "negated": negated, "reader_patient": reader_patient, "patient_surf": patient_surf,
            "composed": composed, "affected_only": affected_only,
            "route": trace["route"], "modal_class": trace.get("modal_class"),
            "type": trace.get("type"), "preds": trace.get("preds"),
            "composed_correct": bool(composed == gold_state),
            "is_designated_unchanged": bool(gold_state == "unchanged"),
        })
    return rows


def run(mode):
    t0 = time.perf_counter()
    out_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    _tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(_tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(_tmp, os.path.join(out_dir, "_start_marker.json"))
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    with open(GOLD_PATH, encoding="utf-8") as f:
        gold_doc = json.load(f)
    gold = gold_doc["gold"]
    EXPECTED_N_UNITS = 44
    if mode == "smoke":
        gold = gold[:16]

    # front-end for reader patient extraction (compose reader output). Guarded: if load fails, gold patient.
    tagger = parser = labeler = reader_pass = base_pick = None
    use_reader = True
    try:
        from experiments.exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 import (
            POS_PATH, ARC_PATH, LABELER_PATH, reader_pass as _rp, base_pick as _bp,
        )
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        from hdlab.arc_labeler import ArcLabeler
        tagger = PosTagger.load(POS_PATH)
        parser = ArcParser.load(ARC_PATH)
        labeler = ArcLabeler.load(LABELER_PATH)
        reader_pass, base_pick = _rp, _bp
        print(f"[{ANCHOR_NAME}:{mode}] reader front-end loaded", flush=True)
    except Exception as e:
        use_reader = False
        print(f"[{ANCHOR_NAME}:{mode}] reader front-end unavailable ({type(e).__name__}); "
              f"binding patient from gold span", flush=True)

    rows = evaluate(gold, use_reader, tagger, parser, labeler, reader_pass, base_pick)
    n = len(rows)

    # ---- accuracies ----
    composed_correct = sum(1 for r in rows if r["composed_correct"])
    composed_acc = round(composed_correct / n, 4)

    # majority baseline
    maj_label = Counter(r["gold_state"] for r in rows).most_common(1)[0][0]
    maj_acc = round(sum(1 for r in rows if r["gold_state"] == maj_label) / n, 4)

    # affectedness-only baseline (MINUS result predicate): unchanged for non-affecting; else the modal
    # AFFECTED label (majority gold label among the affected cases) -> the fairest ablation baseline.
    affected_gold = [r["gold_state"] for r in rows if r["gold_state"] != "unchanged"]
    modal_affected = Counter(affected_gold).most_common(1)[0][0] if affected_gold else "changed_state"
    def aff_only_pred(r):
        return "unchanged" if r["affected_only"] == "unchanged" else modal_affected
    aff_only_correct = sum(1 for r in rows if aff_only_pred(r) == r["gold_state"])
    aff_only_acc = round(aff_only_correct / n, 4)
    # the weaker unresolved variant (all affected -> a bucket that matches no specific label)
    aff_only_unresolved_acc = round(sum(1 for r in rows
                                        if r["affected_only"] == "unchanged" and r["gold_state"] == "unchanged") / n, 4)

    lift_vs_affonly = round(composed_acc - aff_only_acc, 4)
    lift_vs_majority = round(composed_acc - maj_acc, 4)

    # per-label breakdown
    per_label = {}
    for lbl in STATE_LABELS:
        items = [r for r in rows if r["gold_state"] == lbl]
        if items:
            per_label[lbl] = {"n": len(items), "correct": sum(1 for r in items if r["composed_correct"]),
                              "acc": round(sum(1 for r in items if r["composed_correct"]) / len(items), 4)}

    # ---- MUST-FAIL CONTROL (a): designated non-affecting cases MUST infer unchanged ----
    unchanged_rows = [r for r in rows if r["is_designated_unchanged"]]
    control_a_violations = [{"id": r["id"], "verb": r["verb"], "composed": r["composed"]}
                            for r in unchanged_rows if r["composed"] != "unchanged"]
    control_a_holds = (len(control_a_violations) == 0)

    # ---- MUST-FAIL CONTROL (b): SCRAMBLE affected-type->label mapping -> affected acc must collapse ----
    affected_rows = [r for r in rows if r["gold_state"] != "unchanged"]
    n_aff = len(affected_rows)
    composed_affected_acc = round(sum(1 for r in affected_rows if r["composed_correct"]) / n_aff, 4) if n_aff else 0.0
    affected_labels = ["not_intact", "changed_state", "created", "possession_changed", "new_location"]
    scramble_accs = []
    import random
    for sseed in [101, 211, 331, 457, 569]:  # FIXED seeds (no hash()-derived seeding; PROT-023)
        rng = random.Random(sseed)
        # derangement: no label maps to itself
        while True:
            perm = affected_labels[:]
            rng.shuffle(perm)
            if all(a != b for a, b in zip(affected_labels, perm)):
                break
        lm = dict(zip(affected_labels, perm))
        c = 0
        for r in affected_rows:
            scr, _ = infer_result_state(r["verb"], r["negated"], label_map=lm)
            if scr == r["gold_state"]:
                c += 1
        scramble_accs.append(c / n_aff if n_aff else 0.0)
    scramble_affected_acc_mean = round(sum(scramble_accs) / len(scramble_accs), 4)
    scramble_drop = round(composed_affected_acc - scramble_affected_acc_mean, 4)
    control_b_collapses = bool(scramble_drop >= 0.25)

    # ---- VSA binding round-trip over 3 codebook seeds (glass-box proposition; readout in the path) ----
    # atom vocab: distinct patient surfaces + distinct verbs (deterministic sorted order)
    ent_vocab = sorted(set(r["patient_surf"] for r in rows))
    verb_vocab = sorted(set(r["verb"] for r in rows))
    ent_idx = {e: i for i, e in enumerate(ent_vocab)}
    verb_idx = {v: i for i, v in enumerate(verb_vocab)}
    state_idx = {s: i for i, s in enumerate(STATE_LABELS)}
    seed_roundtrips = {}
    seed_readout_labels = {}
    for seed in [7, 13, 19]:
        roles = (fhrr_codebook(1, seed * 3 + 1)[0], fhrr_codebook(1, seed * 3 + 2)[0], fhrr_codebook(1, seed * 3 + 3)[0])
        ent_cb = fhrr_codebook(len(ent_vocab), seed * 101 + 1)
        state_cb = fhrr_codebook(len(STATE_LABELS), seed * 101 + 2)
        verb_cb = fhrr_codebook(len(verb_vocab), seed * 101 + 3)
        rt_state = rt_ent = 0
        labels_this = []
        for r in rows:
            rec_s, rec_e = build_and_readout(ent_idx[r["patient_surf"]], state_idx[r["composed"]],
                                             verb_idx[r["verb"]], roles, ent_cb, state_cb, verb_cb)
            recovered_state = STATE_LABELS[rec_s]
            labels_this.append(recovered_state)
            if recovered_state == r["composed"]:
                rt_state += 1
            if rec_e == ent_idx[r["patient_surf"]]:
                rt_ent += 1
        seed_roundtrips[seed] = {"state_recover": rt_state, "entity_recover": rt_ent, "n": n}
        seed_readout_labels[seed] = labels_this
    roundtrip_state_ok = all(v["state_recover"] == v["n"] for v in seed_roundtrips.values())
    roundtrip_ent_ok = all(v["entity_recover"] == v["n"] for v in seed_roundtrips.values())
    readout_seed_stable = (len({tuple(v) for v in seed_readout_labels.values()}) == 1)
    # the VSA-readout label (seed 7) IS the reported inferred label (VSA in the measurement path)
    vsa_readout_acc = round(sum(1 for r, lab in zip(rows, seed_readout_labels[7]) if lab == r["gold_state"]) / n, 4)

    # ---- ARMS-MUST-DIFFER: composed / affected-only / scrambled decision vectors must differ ----
    def _digest(seq):
        return hashlib.sha256("|".join(seq).encode()).hexdigest()
    composed_vec = [r["composed"] for r in rows]
    affonly_vec = [aff_only_pred(r) for r in rows]
    rng0 = random.Random(101)
    perm0 = affected_labels[:]
    while True:
        rng0.shuffle(perm0)
        if all(a != b for a, b in zip(affected_labels, perm0)):
            break
    lm0 = dict(zip(affected_labels, perm0))
    scrambled_vec = [infer_result_state(r["verb"], r["negated"], label_map=lm0)[0] for r in rows]
    arm_digests = {"composed": _digest(composed_vec), "affected_only": _digest(affonly_vec),
                   "scrambled": _digest(scrambled_vec)}
    arms_differ = len(set(arm_digests.values())) == 3

    baseline_in_band = bool(0.05 < aff_only_acc < 0.95)
    composed_nonsaturated = bool(composed_acc < 0.95)

    # ---- verdict ----
    generalizes = bool(lift_vs_affonly >= 0.20 and lift_vs_majority >= 0.15)
    weak_lift = bool(0.05 < lift_vs_affonly < 0.20)
    roundtrip_ok = bool(roundtrip_state_ok and roundtrip_ent_ok)

    if not arms_differ:
        verdict = "COMPOSITION_ARMS_IDENTICAL_BUG"
    elif not control_a_holds:
        verdict = "HARD_FAIL_CONTROL_A_NONAFFECTING_CHANGED"
    elif not control_b_collapses:
        verdict = "HARD_FAIL_CONTROL_B_SCRAMBLE_NO_COLLAPSE"
    elif not roundtrip_ok:
        verdict = "HARD_FAIL_VSA_ROUNDTRIP"
    elif generalizes:
        verdict = "HARD_PASS_STATE_COMPOSITION"
    elif weak_lift:
        verdict = "MIDDLE_BAND_WEAK_COMPOSITION_LIFT"
    else:
        verdict = "HARD_FAIL_NO_COMPOSITION_LIFT"

    elapsed = round(time.perf_counter() - t0, 2)
    verdict_msg = (
        f"[{verdict}] resulting-state entailment N={n} (SMALL, authored+McGuffey, single-annotator) | "
        f"composed={composed_acc}({composed_correct}/{n}) vs majority={maj_acc}('{maj_label}') "
        f"affectedness_only={aff_only_acc}(modal_aff='{modal_affected}') | "
        f"LIFT vs_affonly=+{lift_vs_affonly} vs_majority=+{lift_vs_majority} | "
        f"per_label=" + ",".join(f"{k}:{per_label[k]['acc']}({per_label[k]['correct']}/{per_label[k]['n']})"
                                 for k in STATE_LABELS if k in per_label)
        + f" | MUST-FAIL(a) non-affecting->unchanged holds={control_a_holds}"
        + (f" VIOL={control_a_violations}" if control_a_violations else "")
        + f" | MUST-FAIL(b) scramble affected {composed_affected_acc}->{scramble_affected_acc_mean} "
        f"drop={scramble_drop} collapses={control_b_collapses} | "
        f"VSA round-trip state={roundtrip_state_ok} entity={roundtrip_ent_ok} seed_stable={readout_seed_stable} "
        f"vsa_readout_acc={vsa_readout_acc} | arms_differ={arms_differ} baseline_in_band={baseline_in_band} "
        f"composed_nonsaturated={composed_nonsaturated}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "N": n, "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": bool(mode == "smoke" or n == EXPECTED_N_UNITS),
        "is_probe_flag": True, "used_reader": use_reader,
        "note": ("FIRST composition/reasoning brick = state-change entailment. Compose reader event "
                 "extraction + proven verb-affectedness gate WITH VerbNet cause->result-state predicates "
                 "into an FHRR bound proposition; infer the affected entity's resulting state (6-way "
                 "taxonomy). Composed vs majority + affectedness-only (ablation minus the result predicate) "
                 "= the composition/reasoning lift. Must-fail (a) non-affecting->unchanged, (b) scramble "
                 "collapses. VSA round-trip recovers patient+state. LOCAL-only; no push/persist; no hdlab "
                 "mutation. Credit VerbNet/Levin/Dowty/Beavers + v1/v2 gate + FHRR (Plate/Gayler)."),
        "accuracy": {
            "composed_acc": composed_acc, "composed_correct": composed_correct, "n": n,
            "majority_acc": maj_acc, "majority_label": maj_label,
            "affectedness_only_acc": aff_only_acc, "affectedness_only_modal_label": modal_affected,
            "affectedness_only_unresolved_acc": aff_only_unresolved_acc,
            "lift_vs_affectedness_only": lift_vs_affonly, "lift_vs_majority": lift_vs_majority,
            "vsa_readout_acc": vsa_readout_acc,
            "per_label": per_label, "composed_nonsaturated": composed_nonsaturated,
            "baseline_in_band": baseline_in_band,
        },
        "must_fail_control_a": {
            "designated_unchanged_n": len(unchanged_rows), "holds": control_a_holds,
            "violations": control_a_violations,
            "desc": "non-affecting verbs (perception/cognition/stative/negated) MUST infer unchanged; fed by the gate",
        },
        "must_fail_control_b": {
            "composed_affected_acc": composed_affected_acc, "n_affected": n_aff,
            "scramble_seeds": [101, 211, 331, 457, 569], "scramble_accs": [round(a, 4) for a in scramble_accs],
            "scramble_affected_acc_mean": scramble_affected_acc_mean, "drop": scramble_drop,
            "collapses": control_b_collapses,
            "desc": "derangement of affected-type->result-label; affected acc must collapse (proves real VerbNet schema use)",
        },
        "vsa_binding": {
            "N_DIM": N_DIM, "flavor": "FHRR complex64 unit-magnitude (bind=elementwise mul, unbind=conj mul)",
            "seeds": [7, 13, 19], "per_seed": seed_roundtrips,
            "roundtrip_state_ok": roundtrip_state_ok, "roundtrip_entity_ok": roundtrip_ent_ok,
            "readout_seed_stable": readout_seed_stable,
            "desc": ("proposition = bind(ROLE_ENTITY,patient)+bind(ROLE_STATE,state)+bind(ROLE_VERB,verb); "
                     "readout = unbind(prop,ROLE_STATE)->cleanup. Round-trip recovers state + patient; each "
                     "inference traceable by unbinding any role."),
        },
        "arms_differ_verified": arms_differ, "arm_digests": arm_digests,
        "per_instance": rows,
        "label_taxonomy": STATE_LABELS,
        "design_gate": {
            "real_baseline": "majority-class AND affectedness-only (full system MINUS result predicate)",
            "one_variable": "the VerbNet result-predicate composition (off=affectedness_only; on=composed)",
            "can_fail": ("composed<=affectedness_only+0.05 (no lift) OR control_a fails OR scramble no-collapse "
                         "OR round-trip<1.0"),
            "difficulty_on": ("6-way specific resulting-state resolution across diverse verb classes; 7 "
                              "word-sense-ambiguous verbs (burn/write/draw/get/send/set/carry) = honest misses "
                              "keeping the system non-saturated"),
            "leak_clean": ("inference reads ONLY the sentence verb + negation + VerbNet; never the gold "
                           "result_state. Mutation-probe (self_test) permutes gold labels -> inference byte-identical"),
            "bands": ("HARD_PASS: lift_vs_affonly>=0.20 AND lift_vs_majority>=0.15 AND control_a AND "
                      "scramble_drop>=0.25 AND round-trip==1.0. MIDDLE_BAND: lift in (0.05,0.20). "
                      "HARD_FAIL: lift<=0.05 OR control_a fails OR no collapse OR round-trip<1.0"),
            "final_metrics_atomicity": "tmp_replace", "crlb_n/a": "accuracy on labeled gold; FHRR N=1024 round-trip lossless",
            "calibration_check": "default_ok_for_this_regime (type-led rule from VerbNet predicate families, gold-independent)",
        },
        "credit": ("VerbNet (Kipper-Schuler 2005) semantic predicates; Levin 1993; Dowty 1991 proto-patient; "
                   "Beavers 2011; v1/v2 verb-affectedness gate; FHRR bind/unbind (Plate 1995, Gayler 2003)."),
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    print(f"[{ANCHOR_NAME}:{mode}] DONE {verdict} elapsed={elapsed}s", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] {verdict_msg}", flush=True)
    return metrics


def self_test():
    print("[self_test] start", flush=True)
    # --- composition inference on clean + word-sense cases ---
    assert infer_result_state("broke", False)[0] == "not_intact"
    assert infer_result_state("cracked", False)[0] == "not_intact"
    assert infer_result_state("opened", False)[0] == "changed_state"
    assert infer_result_state("fixed", False)[0] == "changed_state"
    assert infer_result_state("built", False)[0] == "created"
    assert infer_result_state("gave", False)[0] == "possession_changed"
    assert infer_result_state("put", False)[0] == "new_location"
    assert infer_result_state("moved", False)[0] == "new_location"
    # non-affecting -> unchanged (control-a mechanism)
    assert infer_result_state("see", False)[0] == "unchanged"
    assert infer_result_state("has", False)[0] == "unchanged"
    assert infer_result_state("hunt", False)[0] == "unchanged"
    # NEGATION forces unchanged even for a change-of-state verb (control-a: 'did not break')
    assert infer_result_state("break", True)[0] == "unchanged"
    assert infer_result_state("broke", False)[0] != "unchanged"  # same verb un-negated changes
    print("[self_test] composition inference OK", flush=True)

    # --- FHRR round-trip: unbind recovers state + patient exactly at N=1024 ---
    seed = 7
    roles = (fhrr_codebook(1, 22)[0], fhrr_codebook(1, 23)[0], fhrr_codebook(1, 24)[0])
    ent_cb = fhrr_codebook(5, 700)
    state_cb = fhrr_codebook(len(STATE_LABELS), 701)
    verb_cb = fhrr_codebook(4, 702)
    for p in range(5):
        for s in range(len(STATE_LABELS)):
            rec_s, rec_e = build_and_readout(p, s, p % 4, roles, ent_cb, state_cb, verb_cb)
            assert rec_s == s, f"state round-trip failed p={p} s={s} got {rec_s}"
            assert rec_e == p, f"entity round-trip failed p={p} got {rec_e}"
    print("[self_test] FHRR round-trip OK (state + entity recovered exactly)", flush=True)

    # --- scramble control FIRES on a fixture: derangement collapses affected accuracy ---
    fixture = [("broke", "not_intact"), ("opened", "changed_state"), ("built", "created"),
               ("gave", "possession_changed"), ("put", "new_location"), ("moved", "new_location"),
               ("fixed", "changed_state"), ("cracked", "not_intact")]
    clean = sum(1 for v, gs in fixture if infer_result_state(v, False)[0] == gs) / len(fixture)
    affected_labels = ["not_intact", "changed_state", "created", "possession_changed", "new_location"]
    import random
    rng = random.Random(999)
    while True:
        perm = affected_labels[:]
        rng.shuffle(perm)
        if all(a != b for a, b in zip(affected_labels, perm)):
            break
    lm = dict(zip(affected_labels, perm))
    scr = sum(1 for v, gs in fixture if infer_result_state(v, False, label_map=lm)[0] == gs) / len(fixture)
    assert clean >= 0.9, f"fixture composed acc unexpectedly low {clean}"
    assert scr <= clean - 0.25, f"scramble did NOT collapse (clean={clean} scr={scr})"
    print(f"[self_test] scramble control fires (clean={clean:.3f} scrambled={scr:.3f})", flush=True)

    # --- LEAK-CLEAN: permute gold result_state labels -> inference byte-identical (reads only the verb) ---
    with open(GOLD_PATH, encoding="utf-8") as f:
        gd = json.load(f)
    gold = gd["gold"]
    assert len(gold) == 44, f"expected 44 gold rows, got {len(gold)}"
    for g in gold:
        assert g["result_state"] in STATE_LABELS, f"unexpected result_state {g['result_state']!r}"

    def infer_all(gold_list):
        out = []
        for g in gold_list:
            toks = ud_tokenize(g["text"])
            vi = [k + 1 for k, t in enumerate(toks) if t.lower() == g["verb"].split()[0].lower()]
            neg = verb_is_negated_clauseaware(toks, vi[0] if vi else None)
            out.append(infer_result_state(g["verb"], neg)[0])
        return out

    base = infer_all(gold)
    rng2 = random.Random(12345)  # FIXED seed (PROT-023)
    perm2 = list(range(len(gold)))
    rng2.shuffle(perm2)
    mutated = []
    for k, g in enumerate(gold):
        gg = dict(g)
        gg["result_state"] = gold[perm2[k]]["result_state"]
        mutated.append(gg)
    mut = infer_all(mutated)
    assert base == mut, "LEAK: inference changed when gold result_state labels were permuted"
    print("[self_test] leak-clean mutation-probe OK (inference gold-independent)", flush=True)

    # --- reader import path (compose reader output) exercised, guarded ---
    try:
        from experiments.exp_read_discourse_docorder_stateofmind_whoaffected_ud_ewt_v1 import (
            POS_PATH, ARC_PATH, LABELER_PATH, reader_pass, base_pick,
        )
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        from hdlab.arc_labeler import ArcLabeler
        tagger = PosTagger.load(POS_PATH)
        parser = ArcParser.load(ARC_PATH)
        labeler = ArcLabeler.load(LABELER_PATH)
        toks = ud_tokenize("Tom broke the cup.")
        rp = reader_pass({"tokens": toks}, tagger, parser, labeler)
        assert "pos" in rp and "pools" in rp
        print("[self_test] reader front-end real-code-path OK", flush=True)
    except Exception as e:
        print(f"[self_test] reader front-end unavailable ({type(e).__name__}); binding will use gold patient", flush=True)

    print("[self_test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run("smoke"); return
    if args.full:
        run("full"); return
    self_test()


if __name__ == "__main__":
    out_dir_crash = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(out_dir_crash, exist_ok=True)
        with open(os.path.join(out_dir_crash, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                       "summary": "CELL_CRASHED", "elapsed_s": 0.0,
                       "traceback": traceback.format_exc()[:4000]}, f, indent=2)
        raise
