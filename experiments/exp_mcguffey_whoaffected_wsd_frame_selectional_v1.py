#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_mcguffey_whoaffected_wsd_frame_selectional_v1

WORD-SENSE DISAMBIGUATOR for the verb-affectedness gate. The v2 gate is lemma-level: it collapses each
verb to its MODAL VerbNet sense, so it mis-grades polysemy (leave=depart-vs-DEPOSIT, meet=contact-vs-
ENCOUNTER). Held-out VET a38fa920 confirmed word-sense-disambiguation as the next meaning-module gap:
2/5 sense cases pass, 3/5 failures RESCUABLE-BY-PER-SENSE. This cell EXTENDS v2 (does not fork the
pipeline): it adds a sense-selection step that matches the reader's PARSE-FRAME to the VerbNet sense
whose syntactic frame matches, then reads THAT sense's affectedness -- plus a minimal object-ANIMACY
selectional refinement (the drill's frame+selectional mutual-constraint design).

THREE DECIDERS (one variable = the sense-selection step; negation + hand copula/stative/phrasal overrides
IDENTICAL across all three):
  BASELINE  = v2 COMBINED lemma-modal gate (combined_forces_none), reproduced in-cell = positive control.
  FRAME     = coarse parse-frame signature {INTRANS/TRANS/NP_PP/PP/DATIVE} matched to each VerbNet sense's
              frame-signature set (nltk vn.frames); select frame-compatible senses; AGREE -> use; else
              ABSTAIN to modal. Pareto-safe overlay (only changes a decision when compat senses agree AND
              differ from the modal).
  FRAME_SEL = FRAME + object-animacy tie-break: when frame-compatible senses DISAGREE and the parsed
              direct object is ANIMATE (pronoun closed-class OR local WordNet person/animal hypernym),
              prefer senses whose VerbNet class carries a +animate selrestr on a non-subject role;
              unique decision -> use; else abstain. Fires ONLY on animate objects (the safe case: animate
              objects of contact/social/perception verbs = targets-not-affected). Selectional naturally
              pulls in ENTITY/NOUN SEMANTICS (the next gap) -- MINIMAL (animacy only) via LOCAL WordNet.

BRAIN MECHANISM (CITED@notes/research_drill_word_sense_disambiguation_frame_selectional_2026-07-21):
  frame + selectional mutual constraint settling to the coherent sense (Paczynski-Kuperberg 2012; N400
  pre-activation). Runtime = parser-frame + nltk VerbNet/WordNet lookups ONLY. NO external LLM.

MEASURE (design-gate, can-fail):
  1. WORD-SENSE rescue on the 5 cases {h08 leave-deposit(HARD), h14 hunt, h15 lose, h17/h20 meet}: per-case
     decision vs gold for each decider + chosen sense + rescue classification.
  2. NO-REGRESSION: 33 non-sense held-out sentences per-sentence delta FRAME_SEL vs BASELINE (broken =
     baseline-correct & mechanism-wrong) + UD-EWT who-affected (structural gold -> gate can only cost).

CAN-FAIL (per drill; a can't-fail cell is worse than idle): frame granularity coarse (met transitive
  under BOTH meet senses; leave-deposit shares NP-PP with keep) -> frame-alone may rescue 0 = REAL outcome
  (HARD-FAIL-FRAME); parser attach errors propagate (h08 "on the box" misattaches to noun); h08
  leave-deposit unresolvable by frame OR animacy (needs aspect/world-knowledge) = acknowledged hard bound;
  FRAME_SEL can REGRESS if the animacy tie-break fires wrongly -> HARD-FAIL-WSD.

BANDS (declared BEFORE full; see preregs/2026-07-21_mcguffey_whoaffected_wsd_frame_selectional_v1.md):
  rescued_frame = frame_sense_correct - baseline_sense_correct (of 5); rescued_sel likewise; broken_* =
  non-sense sentences baseline-correct but mechanism-wrong; ud_delta = mechanism UD acc - baseline UD acc.
  HARD-PASS-FRAME: rescued_frame >= +1 AND broken_frame == 0 AND ud_delta_frame >= -0.05.
  HARD-FAIL-FRAME: rescued_frame <= 0.
  HARD-PASS-WSD:   rescued_sel >= +2 AND broken_sel == 0 AND ud_delta_sel >= -0.05.
  MIDDLE_BAND-WSD: rescued_sel == +1 (no regression) OR rescued_sel >= +2 with exactly 1 collateral.
  HARD-FAIL-WSD:   rescued_sel <= 0 OR broken_sel >= 2 OR ud_delta_sel < -0.05.

HYPOTHESIZED (pre-run, tagged): rescued_frame=0 HYPOTHESIZED (frame alone insufficient; ambiguity
  selectional); rescued_sel=+2 HYPOTHESIZED (met h17/h20 via animacy; h08 unresolved); baseline_sense=2/5
  CITED@atom 29415.

Compute architecture: sequential-CPU, justified (pure-python glass-box pass over 38 McGuffey gold + UD
  subset; persisted averaged-perceptron POS + hashed arc-parser/labeler; nltk VerbNet/WordNet cached
  lookups; wall seconds; no matmul inner loop -> not a GPU candidate). Storage: no_storage/no_composition
  (measurement cell; atomic tmp+replace). Determinism: OMP/MKL/OPENBLAS=1; fixed seed in leak probe; no
  hash()-seeded RNG; sense-selection deterministic. LOCAL foreground; NO queue, NO push, NO remote-persist,
  NO git add, NO hdlab mutation. ASCII-only, no em-dashes.

# CELL-TEMPLATE MANDATORY (measurement cell; single-shot, no seed/sweep axis):
# - arms_differ_verified at smoke gate (baseline/frame/frame_sel decision vectors not all identical)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: accuracy on labeled gold, no noise floor
# - baseline_in_band: baseline held-out acc in (0.05,0.95) verified at smoke
# - discriminator survives scale: full IS the scale (N=38 held-out fixed)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - cardinality_ok: n/a (no sweep axis; single deterministic pass)
# - calibration_check: default_ok_for_this_regime (0.35 = v2 builder spot-check 94.4% dec acc)
# - selftest NON-tautological: WSD probe DEGRADES the animacy cue and asserts the decision reverts (must-fail control)
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
import re
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "mcguffey_whoaffected_wsd_frame_selectional_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# reuse the v2 gate machinery + reader/UD wiring (read-only import; NO mutation, NO fork)
from experiments.exp_mcguffey_whoaffected_verb_affectedness_gate_v2_heldout import (  # noqa: E402
    POS_PATH, ARC_PATH, LABELER_PATH, UD_TEST, GOLD_PATH,
    reader_pass, base_pick, load_ud_docs, gold_instances,
    lemmatize, VN_LEX, VN_GRADED_THRESHOLD,
    combined_forces_none, verb_is_negated_clauseaware,
    find_verb_index, span_head_tokens,
    AFFECTED_TYPES, NONE_TYPES, SENSE_CASE_IDS,
    PHRASAL_CLASS, HAND_STATIVE_LIGHT, affectedness_class, NONE_CLASSES,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.candidate_generator import ud_tokenize  # noqa: E402
from nltk.corpus import verbnet as vn  # noqa: E402
from nltk.corpus import wordnet as wn  # noqa: E402

# directional/goal prepositions = CORE-arg PPs (caused-motion / recipient / result-location); everything
# else (on/in/at/by/over/under...) is treated as a LOCATIVE ADJUNCT (not part of the subcat frame).
DIRECTIONAL_PREPS = {"to", "into", "onto", "unto", "upon", "toward", "towards"}
ANIMATE_PRON = {"i", "me", "you", "he", "him", "she", "her", "we", "us", "they", "them",
                "who", "whom", "myself", "himself", "herself", "themselves", "ourselves", "yourself"}
INANIMATE_PRON = {"it", "this", "that", "these", "those", "what", "which", "itself"}
# non-subject (object-candidate) VerbNet roles for the animacy selrestr test
NONSUBJ_ROLES = {"theme", "theme1", "theme2", "patient", "recipient", "actor2", "co-agent",
                 "co-theme", "destination", "topic", "stimulus", "experiencer", "beneficiary"}
ANIM_HYPERNYMS = {"person.n.01", "animal.n.01", "organism.n.01", "causal_agent.n.01"}

# =====================================================================================================
# VerbNet frame-signature extractor (glass-box, cached). Maps each VerbNet frame's primary description to
# a coarse syntactic signature the reader's parse can also produce.
# =====================================================================================================
_FRAME_CACHE = {}


def sense_frame_sigs(vn_class):
    """Set of coarse frame signatures {INTRANS,TRANS,NP_PP,PP,DATIVE} for a VerbNet (sub)class."""
    if vn_class in _FRAME_CACHE:
        return _FRAME_CACHE[vn_class]
    sigs = set()
    try:
        frames = vn.frames(vn.vnclass(vn_class))
    except Exception:
        frames = []
    for fr in frames:
        prim = ((fr.get("description", {}) or {}).get("primary", "") or "").strip()
        pl = prim.lower()
        if "dative" in pl:
            sigs.add("DATIVE"); sigs.add("NP_PP")
        if "np-pp" in pl or "pp-np" in pl:
            sigs.add("NP_PP")
        if pl == "pp":
            sigs.add("PP")
        if "transitive" in pl or "understood reciprocal object" in pl:
            sigs.add("TRANS")
        if "preposition drop" in pl:          # surface-transitive (dropped preposition): "meet (with) him"
            sigs.add("TRANS")
        if "intransitive" in pl:
            sigs.add("INTRANS")
    _FRAME_CACHE[vn_class] = sigs
    return sigs


# =====================================================================================================
# VerbNet selrestr extractor (glass-box, cached). Themroles live on the parent VNCLASS; a subclass id
# (e.g. meet-36.3-1) inherits from its top class (meet-36.3). Strip a trailing -<digits> subclass suffix.
# =====================================================================================================
_ROLE_CACHE = {}


def sense_roles(vn_class):
    """List of (role_type, [(Value,type),...]) for a VerbNet (sub)class; walks to the parent for themroles."""
    if vn_class in _ROLE_CACHE:
        return _ROLE_CACHE[vn_class]
    tries = [vn_class]
    stripped = re.sub(r"-\d+$", "", vn_class)
    if stripped != vn_class:
        tries.append(stripped)
    roles = []
    for t in tries:
        try:
            vc = vn.vnclass(t)
        except Exception:
            continue
        els = vc.findall(".//THEMROLES/THEMROLE")
        if els:
            roles = [(r.get("type"), [(s.get("Value"), s.get("type")) for s in r.findall(".//SELRESTR")])
                     for r in els]
            break
    _ROLE_CACHE[vn_class] = roles
    return roles


def sense_wants_animate_object(vn_class):
    """True iff the class carries a +animate selrestr on a NON-SUBJECT (object-candidate) role -- i.e. the
    sense is about acting on/with an animate participant (social/encounter/perception), not a physical thing."""
    for rtype, sr in sense_roles(vn_class):
        if (rtype or "").lower() in NONSUBJ_ROLES:
            if any(v == "+" and t == "animate" for (v, t) in sr):
                return True
    return False


# =====================================================================================================
# Argument animacy: pronoun closed-class (KB-free) + LOCAL WordNet person/animal hypernym for nouns.
# =====================================================================================================
_ANIM_CACHE = {}


def noun_is_animate(surface):
    """WordNet: True if any of the noun's top-3 senses hypernym-closes to person/animal/organism; else False;
    None if OOV in WordNet. Local, deterministic, glass-box (no external LLM)."""
    s = surface.lower().strip(".,'\"!?;:")
    if s in _ANIM_CACHE:
        return _ANIM_CACHE[s]
    res = None
    try:
        syns = wn.synsets(s, pos=wn.NOUN)
        for syn in syns[:3]:
            for path in syn.hypernym_paths():
                if {h.name() for h in path} & ANIM_HYPERNYMS:
                    res = True
                    break
            if res:
                break
        if res is None and syns:
            res = False
    except Exception:
        res = None
    _ANIM_CACHE[s] = res
    return res


def arg_animacy(surface, pos):
    """True/False/None animacy of an argument surface given its POS."""
    low = (surface or "").lower().strip(".,'\"!?;:")
    if pos == "PRON":
        if low in ANIMATE_PRON:
            return True
        if low in INANIMATE_PRON:
            return False
        return None
    if pos == "PROPN":
        return True                    # McGuffey proper nouns are named characters/animals
    if pos == "NOUN":
        return noun_is_animate(low)
    return None


# =====================================================================================================
# Parse-frame signature from the reader's own parse (heads + relation labels).
# =====================================================================================================
def parse_frame(tokens, pos, heads, labels, vidx):
    """Coarse subcat signature for the verb at 1-based vidx + the obj/subj indices for animacy."""
    obj = subj = iobj = None
    has_dir = False
    has_loc = False
    if vidx is None:
        return {"sig": "INTRANS", "obj_aidx": None, "subj_aidx": None, "iobj_aidx": None,
                "has_loc_obl": False, "has_dir_obl": False}
    for n in range(1, len(tokens) + 1):
        if heads.get(n) != vidx:
            continue
        rel = labels.get(n, "")
        if rel == "obj" and obj is None:
            obj = n
        elif rel == "iobj" and iobj is None:
            iobj = n
        elif rel == "nsubj" and subj is None:
            subj = n
        elif rel == "obl":
            prep = None
            for c in range(1, len(tokens) + 1):
                if heads.get(c) == n and labels.get(c) == "case":
                    prep = tokens[c - 1].lower().strip(".,'\"!?;:")
                    break
            if prep in DIRECTIONAL_PREPS:
                has_dir = True
            else:
                has_loc = True
    has_obj = obj is not None
    if has_obj and iobj is not None:
        sig = "DATIVE"
    elif has_obj and has_dir:
        sig = "NP_PP"
    elif has_obj and not has_dir:
        sig = "TRANS"
    elif (not has_obj) and has_dir:
        sig = "PP"
    else:
        sig = "INTRANS"
    return {"sig": sig, "obj_aidx": obj, "subj_aidx": subj, "iobj_aidx": iobj,
            "has_loc_obl": has_loc, "has_dir_obl": has_dir}


def frame_compatible(parse_sig, sense_sigs):
    """Is the parse's coarse signature realized by this sense's frame set?"""
    if parse_sig == "TRANS":
        return "TRANS" in sense_sigs
    if parse_sig == "NP_PP":
        return ("NP_PP" in sense_sigs) or ("DATIVE" in sense_sigs)
    if parse_sig == "DATIVE":
        return ("DATIVE" in sense_sigs) or ("NP_PP" in sense_sigs)
    if parse_sig == "PP":
        return "PP" in sense_sigs
    if parse_sig == "INTRANS":
        return "INTRANS" in sense_sigs
    return False


def per_senses(verb_surface):
    """(lemma, [{vn_class,graded,forces_none,vn_type}, ...]) from the VerbNet lexicon per_sense data."""
    head = (verb_surface or "").lower().strip().split()[0] if verb_surface else ""
    lem = lemmatize(head)
    entry = VN_LEX.get(lem)
    if entry is None:
        return lem, []
    out = []
    for ps in entry.get("per_sense", []):
        g = float(ps.get("graded_score", 0.5))
        out.append({"vn_class": ps.get("vn_class"), "graded": g, "forces_none": g < VN_GRADED_THRESHOLD,
                    "vn_type": ps.get("affectedness_type")})
    return lem, out


def wsd_decide(verb_surface, pframe, obj_anim, arm):
    """Sense-selected force-none decision. arm in {'frame','frame_sel'}. Falls back to the v2 modal decision
    (combined_forces_none) whenever the frame/selectional evidence does not resolve a unique sense.
    Returns (force_none, source, detail)."""
    base_dec, base_src, _ = combined_forces_none(verb_surface)
    lem, ps = per_senses(verb_surface)
    detail = {"lemma": lem, "n_senses": len(ps), "parse_sig": pframe["sig"], "obj_anim": obj_anim}
    if len(ps) <= 1:
        detail["route"] = "single_or_oov->modal"
        return base_dec, "modal(" + base_src + ")", detail
    compat = [s for s in ps if frame_compatible(pframe["sig"], sense_frame_sigs(s["vn_class"]))]
    detail["compat_classes"] = [s["vn_class"] for s in compat]
    if not compat:
        detail["route"] = "no_frame_compat->modal"
        return base_dec, "frame_no_compat_modal(" + base_src + ")", detail
    decs = {s["forces_none"] for s in compat}
    if len(decs) == 1:
        d = next(iter(decs))
        detail["route"] = "frame_agree"
        detail["chosen_classes"] = detail["compat_classes"]
        return d, "frame_agree", detail
    # frame-compatible senses DISAGREE
    if arm == "frame":
        detail["route"] = "frame_disagree->abstain->modal"
        return base_dec, "frame_abstain_modal(" + base_src + ")", detail
    # frame_sel: object-animacy tie-break, fires ONLY on an animate object
    if obj_anim is True:
        anim_senses = [s for s in compat if sense_wants_animate_object(s["vn_class"])]
        detail["anim_subset"] = [s["vn_class"] for s in anim_senses]
        if anim_senses:
            adecs = {s["forces_none"] for s in anim_senses}
            if len(adecs) == 1:
                d = next(iter(adecs))
                detail["route"] = "frame_sel_animate_unique"
                detail["chosen_classes"] = detail["anim_subset"]
                return d, "frame_sel_animate", detail
    detail["route"] = "frame_sel_no_resolve->abstain->modal"
    return base_dec, "frame_sel_abstain_modal(" + base_src + ")", detail


def full_gate(verb_surface, pframe, obj_anim, neg, arm):
    """Complete gate: negation -> hand phrasal -> hand copula/stative/light -> WSD (frame/frame_sel) with
    modal fallback. arm='baseline' uses the v2 combined lemma-modal decision (no WSD). Returns (force_none, source)."""
    if neg:
        return True, "negation"
    key = (verb_surface or "").lower().strip()
    head = key.split()[0] if key else ""
    if key in PHRASAL_CLASS:
        return (PHRASAL_CLASS[key] in NONE_CLASSES), "hand_phrasal"
    lem = lemmatize(head)
    if lem in HAND_STATIVE_LIGHT or affectedness_class(head) == "possession_stative":
        return True, "hand_stative_light"
    if arm == "baseline":
        d, src, _ = combined_forces_none(verb_surface)
        return d, "modal(" + src + ")"
    d, src, _ = wsd_decide(verb_surface, pframe, obj_anim, arm)
    return d, src


# =====================================================================================================
def _parse_full(tokens, tagger, parser, labeler):
    pos = tagger.tag(tokens)
    pr = parser.parse(tokens, pos)
    heads = pr.heads
    labels = labeler.label(tokens, pos, heads)
    return pos, heads, labels


def eval_mcguffey(gold, tagger, parser, labeler):
    inst = []
    for g in gold:
        text, gverb, gaff, gtype = g["text"], g["verb"], g["affected"], g["type"]
        gold_none = gtype in NONE_TYPES
        heads_gold = span_head_tokens(gaff)

        tokens = ud_tokenize(text)
        rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
        pos = rp["pos"]
        vidx, pos_missed = find_verb_index(tokens, pos, gverb)
        pool = rp["pools"].get(vidx, []) if vidx is not None else []
        bp = base_pick(pool)
        pred_surf = bp["surf"] if bp is not None else None
        pred_none = bp is None

        # separate parse to build the frame signature (heads + relation labels)
        _pos2, heads, labels = _parse_full(tokens, tagger, parser, labeler)
        pframe = parse_frame(tokens, _pos2, heads, labels, vidx)
        obj_aidx = pframe["obj_aidx"]
        obj_anim = arg_animacy(tokens[obj_aidx - 1], _pos2[obj_aidx - 1]) if obj_aidx else None

        neg = verb_is_negated_clauseaware(tokens, vidx)

        base_none, base_src = full_gate(gverb, pframe, obj_anim, neg, "baseline")
        frame_none, frame_src = full_gate(gverb, pframe, obj_anim, neg, "frame")
        sel_none, sel_src = full_gate(gverb, pframe, obj_anim, neg, "frame_sel")

        def correct(force_none):
            pred_is_none = pred_none or force_none
            if gold_none:
                return pred_is_none
            return bool((not force_none) and pred_surf is not None and pred_surf in heads_gold)

        row = {
            "id": g["id"], "text": text, "verb": gverb, "type": gtype, "gold_affected": gaff,
            "gold_none": gold_none, "pred_surf": pred_surf, "pred_none": pred_none,
            "parse_sig": pframe["sig"], "obj_aidx": obj_aidx, "obj_anim": obj_anim,
            "has_loc_obl": pframe["has_loc_obl"], "neg": neg, "pos_missed": pos_missed,
            "base_none": base_none, "base_src": base_src,
            "frame_none": frame_none, "frame_src": frame_src,
            "sel_none": sel_none, "sel_src": sel_src,
            "base_correct": correct(base_none), "frame_correct": correct(frame_none),
            "sel_correct": correct(sel_none),
            "is_sense_case": g["id"] in SENSE_CASE_IDS,
        }
        if g["id"] in SENSE_CASE_IDS:
            lem, ps = per_senses(gverb)
            _, _, sel_detail = wsd_decide(gverb, pframe, obj_anim, "frame_sel")
            _, _, frame_detail = wsd_decide(gverb, pframe, obj_anim, "frame")
            row["per_sense"] = ps
            row["frame_route"] = frame_detail.get("route")
            row["sel_route"] = sel_detail.get("route")
            row["sel_chosen"] = sel_detail.get("chosen_classes")
        inst.append(row)
    return inst


def eval_ud(docs, tagger, parser, labeler, arm):
    """UD-EWT who-affected for one arm (structural gold -> gate can only cost). Returns per-instance rows."""
    rows = []
    for doc in docs:
        for sent in doc:
            rp = reader_pass(sent, tagger, parser, labeler)
            tokens, lemmas = sent["tokens"], sent["lemmas"]
            _pos2, heads, labels = _parse_full(tokens, tagger, parser, labeler)
            for gi in gold_instances(sent):
                v, gp = gi["vidx"], gi["gold_pidx"]
                pool = rp["pools"].get(v, [])
                bp = base_pick(pool)
                base_aidx = bp["aidx"] if bp is not None else None
                lemma = lemmas[v - 1] if 1 <= v <= len(lemmas) else tokens[v - 1].lower()
                pframe = parse_frame(tokens, _pos2, heads, labels, v)
                obj_aidx = pframe["obj_aidx"]
                obj_anim = arg_animacy(tokens[obj_aidx - 1], _pos2[obj_aidx - 1]) if obj_aidx else None
                neg = verb_is_negated_clauseaware(tokens, v)
                force_none, _ = full_gate(lemma, pframe, obj_anim, neg, arm)
                base_correct = bool(base_aidx is not None and base_aidx == gp)
                arm_correct = bool((not force_none) and base_correct)
                rows.append({"base_correct": base_correct, "arm_correct": arm_correct, "fired": force_none})
    return rows


# ---------------------------------------------------------------------------------------------------
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
    if mode == "smoke":
        gold = gold[:14]

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded; held-out McGuffey N={len(gold)}", flush=True)

    minst = eval_mcguffey(gold, tagger, parser, labeler)
    n_m = len(minst)

    def acc(items, key):
        c = sum(1 for i in items if i[key])
        return (round(c / len(items), 4) if items else None), len(items), c

    m_base = acc(minst, "base_correct")
    m_frame = acc(minst, "frame_correct")
    m_sel = acc(minst, "sel_correct")

    # WORD-SENSE cases (of the 5) -- per-decider correct counts + per-case table
    sense_rows = [i for i in minst if i["is_sense_case"]]
    n_sense = len(sense_rows)
    base_sense = sum(1 for i in sense_rows if i["base_correct"])
    frame_sense = sum(1 for i in sense_rows if i["frame_correct"])
    sel_sense = sum(1 for i in sense_rows if i["sel_correct"])
    rescued_frame = frame_sense - base_sense
    rescued_sel = sel_sense - base_sense
    sense_table = [{
        "id": i["id"], "verb": i["verb"], "gold_type": i["type"], "gold_none": i["gold_none"],
        "parse_sig": i["parse_sig"], "obj_anim": i["obj_anim"],
        "base_none": i["base_none"], "frame_none": i["frame_none"], "sel_none": i["sel_none"],
        "base_correct": i["base_correct"], "frame_correct": i["frame_correct"], "sel_correct": i["sel_correct"],
        "frame_route": i.get("frame_route"), "sel_route": i.get("sel_route"), "sel_chosen": i.get("sel_chosen"),
        "n_senses": len(i.get("per_sense", [])), "per_sense": i.get("per_sense", []),
        "rescued_by_frame": (i["frame_correct"] and not i["base_correct"]),
        "rescued_by_sel": (i["sel_correct"] and not i["base_correct"]),
    } for i in sense_rows]

    # NO-REGRESSION on the non-sense held-out sentences (per-sentence, both mechanism arms)
    nonsense = [i for i in minst if not i["is_sense_case"]]
    ns_base = sum(1 for i in nonsense if i["base_correct"])
    ns_frame = sum(1 for i in nonsense if i["frame_correct"])
    ns_sel = sum(1 for i in nonsense if i["sel_correct"])
    broken_frame = [i["id"] for i in nonsense if i["base_correct"] and not i["frame_correct"]]
    gained_frame = [i["id"] for i in nonsense if (not i["base_correct"]) and i["frame_correct"]]
    broken_sel = [i["id"] for i in nonsense if i["base_correct"] and not i["sel_correct"]]
    gained_sel = [i["id"] for i in nonsense if (not i["base_correct"]) and i["sel_correct"]]

    # ARMS-MUST-DIFFER (baseline/frame/frame_sel decision vectors)
    def _digest(key):
        return hashlib.sha256(bytes([1 if i[key] else 0 for i in minst])).hexdigest()
    arm_digests = {"baseline": _digest("base_correct"), "frame": _digest("frame_correct"),
                   "frame_sel": _digest("sel_correct")}
    arms_differ = len(set(arm_digests.values())) > 1

    # decision-level arms-differ (correctness can coincide even when decisions differ) -- report both
    dec_digests = {"baseline": _digest("base_none"), "frame": _digest("frame_none"),
                   "frame_sel": _digest("sel_none")}
    decisions_differ = len(set(dec_digests.values())) > 1

    # UD-EWT no-regression for both mechanism arms
    ud_docs = load_ud_docs(UD_TEST)
    ud_docs = [d for d in ud_docs if len(d) >= 1]
    ud_docs = ud_docs[:(20 if mode == "smoke" else 250)]
    u_base_rows = eval_ud(ud_docs, tagger, parser, labeler, "baseline")
    u_frame_rows = eval_ud(ud_docs, tagger, parser, labeler, "frame")
    u_sel_rows = eval_ud(ud_docs, tagger, parser, labeler, "frame_sel")
    n_u = len(u_base_rows)
    u_base = acc(u_base_rows, "arm_correct")
    u_frame = acc(u_frame_rows, "arm_correct")
    u_sel = acc(u_sel_rows, "arm_correct")
    ud_delta_frame = round((u_frame[0] or 0.0) - (u_base[0] or 0.0), 4)
    ud_delta_sel = round((u_sel[0] or 0.0) - (u_base[0] or 0.0), 4)

    baseline_in_band = bool(0.05 < (m_base[0] or 0.0) < 0.95)

    # ---- verdict (bands declared in prereg; computed from measured numbers) ----
    # PRIMARY: does FRAME-matching pick the right sense?
    frame_no_reg = bool(len(broken_frame) == 0 and ud_delta_frame >= -0.05)
    if rescued_frame >= 1 and frame_no_reg:
        frame_verdict = "HARD_PASS_FRAME"
    elif rescued_frame <= 0:
        frame_verdict = "HARD_FAIL_FRAME"
    else:
        frame_verdict = "MIDDLE_BAND_FRAME"

    # OVERALL deliverable: FRAME_SEL Pareto rescue
    if rescued_sel >= 2 and len(broken_sel) == 0 and ud_delta_sel >= -0.05:
        wsd_verdict = "HARD_PASS_WSD"
    elif rescued_sel <= 0 or len(broken_sel) >= 2 or ud_delta_sel < -0.05:
        wsd_verdict = "HARD_FAIL_WSD"
    else:
        wsd_verdict = "MIDDLE_BAND_WSD"

    if not arms_differ and not decisions_differ:
        verdict = "GATE_ARMS_IDENTICAL_BUG"
    else:
        verdict = wsd_verdict

    elapsed = round(time.perf_counter() - t0, 2)
    verdict_msg = (
        f"[{verdict}] WSD frame+selectional on held-out McGuffey N={n_m} (SMALL, single-annotator) | "
        f"who-affected acc: BASELINE={m_base[0]}({m_base[2]}/{m_base[1]}) FRAME={m_frame[0]} "
        f"FRAME_SEL={m_sel[0]} | WORD-SENSE cases (of {n_sense}): base={base_sense} frame={frame_sense} "
        f"frame_sel={sel_sense} (rescued_frame={rescued_frame} rescued_sel={rescued_sel}) | "
        f"NO-REG non-sense (n={len(nonsense)}): base={ns_base} frame={ns_frame} sel={ns_sel} "
        f"broken_frame={broken_frame} broken_sel={broken_sel} gained_sel={gained_sel} | "
        f"UD-EWT N={n_u}: base={u_base[0]} frame={u_frame[0]}(d={ud_delta_frame}) "
        f"sel={u_sel[0]}(d={ud_delta_sel}) | FRAME_VERDICT={frame_verdict} WSD_VERDICT={wsd_verdict} | "
        f"arms_differ={arms_differ} decisions_differ={decisions_differ} baseline_in_band={baseline_in_band}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "N_heldout": n_m, "N_ud_instances": n_u, "is_probe_flag": True,
        "frame_verdict": frame_verdict, "wsd_verdict": wsd_verdict,
        "note": ("WORD-SENSE DISAMBIGUATOR extending the v2 lemma-modal verb-affectedness gate: parse-frame "
                 "matched to VerbNet per-sense frames (FRAME) + object-animacy selrestr tie-break (FRAME_SEL) "
                 "via LOCAL nltk VerbNet/WordNet. Runtime = parser-frame + KB lookup, NO external LLM. "
                 "Deliverable = Pareto rescue of polysemy without breaking non-polysemous held-out. Gate = "
                 "verb-lemma + parse-frame + argument-animacy, gold-independent -> leak-clean. Credit "
                 "VerbNet/WordNet/Levin/Dowty/Beavers/Paczynski-Kuperberg + v1/v2. LOCAL-only; no push/"
                 "remote-persist; no hdlab mutation."),
        "heldout_mcguffey": {
            "baseline_acc": m_base[0], "frame_acc": m_frame[0], "frame_sel_acc": m_sel[0],
            "baseline_correct": m_base[2], "frame_correct": m_frame[2], "frame_sel_correct": m_sel[2],
            "n": n_m, "baseline_in_band": baseline_in_band,
        },
        "word_sense_cases": {
            "n_cases": n_sense, "base_correct": base_sense, "frame_correct": frame_sense,
            "frame_sel_correct": sel_sense, "rescued_frame": rescued_frame, "rescued_sel": rescued_sel,
            "table": sense_table,
        },
        "no_regression": {
            "nonsense_n": len(nonsense), "base_correct": ns_base, "frame_correct": ns_frame,
            "frame_sel_correct": ns_sel, "broken_frame": broken_frame, "gained_frame": gained_frame,
            "broken_sel": broken_sel, "gained_sel": gained_sel,
            "ud_base_acc": u_base[0], "ud_frame_acc": u_frame[0], "ud_frame_sel_acc": u_sel[0],
            "ud_delta_frame": ud_delta_frame, "ud_delta_sel": ud_delta_sel, "ud_n": n_u,
            "ud_gold_is_structural_caveat": ("UD-EWT who-affected gold = parse-derived (every obj=patient); "
                                             "the semantic gate can only COST here, never help. Delta = "
                                             "over-fire cost, not a capability gap."),
        },
        "arms_differ_verified": arms_differ, "decisions_differ_verified": decisions_differ,
        "arm_digests": arm_digests, "decision_digests": dec_digests,
        "mcguffey_per_instance": minst,
        "design_gate": {
            "real_baseline": "v2 COMBINED lemma-modal gate (combined_forces_none), recomputed in-cell",
            "one_variable": "the sense-selection step (baseline=modal; frame=frame-match; frame_sel=+animacy)",
            "can_fail": ("frame granularity coarse (met transitive under both meet senses; leave-deposit "
                         "shares NP-PP with keep) -> frame may rescue 0; parser attach errors propagate; "
                         "h08 leave-deposit unresolvable by frame OR animacy (aspect/world-knowledge); "
                         "frame_sel can regress non-sense held-out -> HARD_FAIL_WSD"),
            "difficulty_on": "real archaic McGuffey held-out + deliberately-packed word-sense cases",
            "leak_clean": ("gate = verb-lemma + parse-frame + argument-animacy, gold-independent; mutation-"
                           "probe permutes gold labels + re-derives -> gate decisions byte-identical"),
            "final_metrics_atomicity": "tmp_replace", "crlb_n/a": "accuracy on labeled gold, no noise floor",
            "calibration_check": "default_ok_for_this_regime (0.35 = v2 builder spot-check 94.4% dec acc)",
            "selftest_nontautological": ("WSD probe DEGRADES the animacy cue (obj_anim True->False) and "
                                         "asserts frame_sel reverts from the encounter decision to modal"),
        },
        "prereg": "preregs/2026-07-21_mcguffey_whoaffected_wsd_frame_selectional_v1.md",
        "credit": ("VerbNet (Kipper-Schuler 2005); WordNet (Fellbaum 1998); Levin 1993; Dowty 1991; "
                   "Beavers 2011; Paczynski-Kuperberg 2012; v1 hand-lexicon + v2 held-out gate."),
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
    # --- frame-signature extractor (nltk VerbNet) ---
    put_sigs = sense_frame_sigs("put-9.1-2")
    assert "NP_PP" in put_sigs, ("put-9.1-2 should be NP_PP", put_sigs)
    meet_sigs = sense_frame_sigs("meet-36.3-1")
    assert "INTRANS" in meet_sigs and "TRANS" in meet_sigs, ("meet-36.3-1 sigs", meet_sigs)
    contig_sigs = sense_frame_sigs("contiguous_location-47.8-1")
    assert "TRANS" in contig_sigs, ("contiguous should be TRANS (Understood Reciprocal Object)", contig_sigs)
    assert frame_compatible("TRANS", contig_sigs) and frame_compatible("TRANS", meet_sigs)
    assert frame_compatible("NP_PP", put_sigs) and not frame_compatible("INTRANS", put_sigs)

    # --- selrestr extractor (parent-class inheritance) ---
    assert sense_wants_animate_object("meet-36.3-1") is True          # Actor2 +animate (social encounter)
    assert sense_wants_animate_object("contiguous_location-47.8-1") is False  # Theme +concrete (physical)

    # --- animacy (pronoun closed-class + local WordNet) ---
    assert arg_animacy("him", "PRON") is True
    assert arg_animacy("it", "PRON") is False
    assert arg_animacy("man", "NOUN") is True
    assert arg_animacy("box", "NOUN") is False
    assert arg_animacy("step", "NOUN") is False

    # --- WSD sense-selection probe (NON-TAUTOLOGICAL: degrade the cue -> decision must revert) ---
    # 'met' with a TRANS parse: meet has 2 senses (contiguous_location contact 0.45 KEEP; meet-36.3
    # encounter 0.1 NONE). frame alone abstains (both TRANS-compat, disagree) -> modal KEEP (force_none
    # False). frame_sel with ANIMATE object -> picks the encounter sense -> force_none True.
    tframe = {"sig": "TRANS", "obj_aidx": 1, "subj_aidx": None, "iobj_aidx": None,
              "has_loc_obl": False, "has_dir_obl": False}
    d_frame, src_frame, det_frame = wsd_decide("met", tframe, True, "frame")
    assert d_frame is False and "abstain" in src_frame, (d_frame, src_frame, det_frame)   # modal KEEP
    d_sel_anim, src_sel_anim, det_sel_anim = wsd_decide("met", tframe, True, "frame_sel")
    assert d_sel_anim is True and src_sel_anim == "frame_sel_animate", (d_sel_anim, src_sel_anim, det_sel_anim)
    # DEGRADE the cue: object no longer animate -> the selectional tie-break must NOT fire -> revert to modal
    d_sel_inan, src_sel_inan, det_sel_inan = wsd_decide("met", tframe, False, "frame_sel")
    assert d_sel_inan is False and "abstain" in src_sel_inan, (d_sel_inan, src_sel_inan, det_sel_inan)
    # determinism: same inputs -> same decision
    assert wsd_decide("met", tframe, True, "frame_sel")[0] == d_sel_anim

    # --- single-sense verbs pass through to modal (Pareto-safe: no spurious change) ---
    d_put, _, det_put = wsd_decide("put", {"sig": "TRANS", "obj_aidx": 1, "subj_aidx": None,
                                           "iobj_aidx": None, "has_loc_obl": False, "has_dir_obl": False},
                                   False, "frame_sel")
    assert det_put["route"].endswith("modal") or "modal" in det_put["route"], det_put

    # --- real code path: construct the REAL front-end + parse a real sentence + build a frame sig ---
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    toks = ud_tokenize("I met the man.")
    pos, heads, labels = _parse_full(toks, tagger, parser, labeler)
    vi = [k + 1 for k, t in enumerate(toks) if t.lower() == "met"][0]
    pf = parse_frame(toks, pos, heads, labels, vi)
    assert pf["sig"] in ("TRANS", "NP_PP", "INTRANS"), pf   # parser-dependent; obj expected
    rp = reader_pass({"tokens": toks}, tagger, parser, labeler)
    assert "pos" in rp and "pools" in rp
    ud_docs = load_ud_docs(UD_TEST)
    assert ud_docs, "UD test conllu must load"
    ur = eval_ud(ud_docs[:2], tagger, parser, labeler, "frame_sel")
    assert isinstance(ur, list)

    # --- LEAK-CLEAN mutation probe (REAL): permute gold type/affected labels + re-derive gate ---
    with open(GOLD_PATH, encoding="utf-8") as f:
        gd = json.load(f)
    gold = gd["gold"]
    assert len(gold) == 38
    for g in gold:
        assert g["type"] in (AFFECTED_TYPES | NONE_TYPES), "unexpected gold type: %r" % g["type"]

    def gate_decisions(gold_list):
        out = []
        for g in gold_list:
            toks = ud_tokenize(g["text"])
            pos, heads, labels = _parse_full(toks, tagger, parser, labeler)
            vi = [k + 1 for k, t in enumerate(toks) if t.lower() == g["verb"].split()[0].lower()]
            vidx = vi[0] if vi else None
            pf = parse_frame(toks, pos, heads, labels, vidx)
            oa = arg_animacy(toks[pf["obj_aidx"] - 1], pos[pf["obj_aidx"] - 1]) if pf["obj_aidx"] else None
            neg = verb_is_negated_clauseaware(toks, vidx)
            d, _ = full_gate(g["verb"], pf, oa, neg, "frame_sel")
            out.append(bool(d))
        return out

    base_dec = gate_decisions(gold)
    import random
    rng = random.Random(12345)      # FIXED seed (no hash()-derived seeding; PROT-023)
    perm = list(range(len(gold)))
    rng.shuffle(perm)
    mutated = []
    for k, g in enumerate(gold):
        gg = dict(g)
        gg["type"] = gold[perm[k]]["type"]
        gg["affected"] = gold[perm[k]]["affected"]
        mutated.append(gg)
    mut_dec = gate_decisions(mutated)
    assert base_dec == mut_dec, "LEAK: gate decision changed when gold labels were permuted"

    print("[self_test] frame-sigs OK; selrestr OK; animacy OK; WSD degrade-cue probe OK (non-tautological); "
          "single-sense passthrough OK; real-code-path OK; UD-load OK; leak-clean permutation OK", flush=True)
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
                       "traceback": traceback.format_exc()[:4000]}, f, indent=2)
        raise
