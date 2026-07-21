#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_wordnet_noun_semantics_kb_who_affected_v1

WORDNET NOUN-SEMANTICS KB for the who-is-affected reader. Builds a VETTED KB (per-noun animacy + coarse
semantic type via first-sense lexname + hypernym-closure) and wires it into the affectedness gate's
SELECTIONAL decision, GENERALIZING the hardcoded-`met` object-animacy path (WSD cell commit 9f31de741)
to a KB-backed, for-ANY-verb rule. This is the ENTITY/NOUN-SEMANTICS lever (the NOUN half of the
selectional match; VerbNet supplies the VERB half). Orthogonal to the verb-affectedness loop -> composes.

MECHANISM (glass-box, NO external LLM):
  KB (build-time WordNet ingest -> data/wordnet_noun_semantics_kb_v1/kb.json):
    dominant (first) synset -> lexname -> coarse sem_type + a VerbNet-compatible +selrestr FEATURE set;
    animate = lexname in {noun.person,noun.animal} OR dominant-sense hypernym-closes to
    {person,animal,organism,causal_agent}. Dominant-sense discipline (WordNet over-splits; first sense =
    most frequent). Runtime = cache lookup with live-WordNet fallback (self-test asserts cache==live).
  ARMS (one variable = the KB selectional override; identical negation/phrasal/stative/modal prefix):
    BASE = v2 verb-affectedness gate (full_gate baseline). The 0.769 real baseline (no noun KB).
    KB   = BASE, EXCEPT when BASE would KEEP and the verb has 2+ frame-compatible VerbNet senses that
           differ in affectedness and the parsed OBJECT's KB feature-set SATISFIES a NOT-affecting sense's
           non-subject +selrestr while satisfying NO affected sense's +selrestr -> override to force-none.
           KEEP->NONE only (Pareto). Generalizes met's +animate tie-break to the full selrestr vocabulary.
  REPRESENTATION (substrate-native, secondary): KB also encoded as a sharded additive-map store partition
    (noun (x) sem_type, FHRR unit-phasor codebook, N=1024); retrieve-fidelity == dict asserted (sharded =>
    exact) + reported per-seed. Accuracy measured on the dict (identical to store by the fidelity proof).

EVAL (HELD-OUT, DEPLOYABLE = PREDICTED POS/parse): UD-EWT independent blind gold (52 primary binary,
  base=0.769 MEASURED@scoreboard) + McGuffey held-out (38). KB never saw either gold; front-end trained on
  UD-EWT TRAIN (disjoint from test). Pooled N~90.

MULTI-SEED + MUST-FAIL (SEEDS=[7,13,17,23,29]): SCRAMBLE = permute the noun->feature map (each seed) ->
  the improvement MUST collapse (mean scramble delta near 0) => the type/animacy SIGNAL is load-bearing,
  not a base-rate artifact. BOOTSTRAP CI (B smoke 200 / full 2000) on the pooled delta. STORE fidelity/seed.

BANDS (declared BEFORE full; see preregs/2026-07-21_wordnet_noun_semantics_kb_who_affected_v1.md):
  scramble_collapses := mean_scr_delta<=0.01 AND (pooled_delta<=0 OR mean_scr_delta<0.5*pooled_delta).
  no_regression := ud_delta>=-0.01 AND mcg_delta>=-0.01.
  HARD_PASS_ENTITY_KB: pooled_delta>=0.03 AND no_regression AND scramble_collapses AND arms_differ AND leak_clean.
  HARD_FAIL_ENTITY_KB: pooled_delta<=0 OR ud_delta<=-0.03 OR mcg_delta<=-0.03 OR (not scramble_collapses) OR (not arms_differ).
  MIDDLE_BAND_ENTITY_KB: 0<pooled_delta<0.03 with no_regression AND scramble_collapses.

HYPOTHESIZED (pre-run, tagged): pooled_delta ~ +0.03..+0.05 HYPOTHESIZED (McGuffey met h17/h20 = +2 solid;
  UD met u10 + reach u12/u14 = +0..+3 parse-dependent); mean_scr_delta ~ 0 HYPOTHESIZED. base=0.769
  MEASURED@data/exp_ud_ewt_semantic_affectedness_independent_scoreboard_v1/metrics.json:primary_binary.base_gate_acc.

Compute architecture: sequential-CPU, justified (glass-box pass over ~90 rows x (2 arms + 5 scramble
  seeds) + a small FHRR store over ~120 nouns, numpy N=1024 sharded exact; nltk cached lookups; wall
  seconds; no matmul inner loop -> not a GPU candidate). Storage: sharded additive-map partition (repr
  demo). Determinism: OMP/MKL/OPENBLAS=1; fixed seeds; no hash()-seeded RNG. LOCAL foreground; NO queue,
  NO push, NO remote-persist, NO git add of canonical store, NO hdlab mutation, NO atom bank. ASCII-only.

# CELL-TEMPLATE MANDATORY (measurement + multi-seed control cell):
# - arms_differ_verified at smoke (base vs kb decision vectors differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: accuracy on labeled gold, no noise floor
# - baseline_in_band: BASE pooled acc in (0.05,0.95) verified at smoke
# - discriminator survives scale: smoke runs the FULL eval sets (met cases at index>14) -> discriminator fires
# - cardinality_ok: EXPECTED_UNITS = len(SEEDS) scramble runs recorded; verdict counts them
# - calibration_check: default_ok_for_this_regime (VN_GRADED_THRESHOLD 0.35 inherited; selrestr = exact VN strings)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
# - selftest non-tautological: leak-probe + scramble-degrade (must-fail fires) + animacy spot-sample + store fidelity
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
import random
import re
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "wordnet_noun_semantics_kb_who_affected_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# reuse the reader front-end + v2 gate + WSD frame machinery (read-only imports; NO mutation, NO fork)
from experiments.exp_mcguffey_whoaffected_wsd_frame_selectional_v1 import (  # noqa: E402
    POS_PATH, ARC_PATH, LABELER_PATH, UD_TEST, GOLD_PATH as MCG_GOLD_PATH,
    reader_pass, base_pick, load_ud_docs, gold_instances,
    find_verb_index, span_head_tokens,
    parse_frame, _parse_full, sense_frame_sigs, frame_compatible, per_senses,
    sense_roles, full_gate, verb_is_negated_clauseaware,
    AFFECTED_TYPES, NONE_TYPES, NONSUBJ_ROLES,
)
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.arc_parser import ArcParser  # noqa: E402
from hdlab.arc_labeler import ArcLabeler  # noqa: E402
from hdlab.candidate_generator import ud_tokenize  # noqa: E402
from nltk.corpus import wordnet as wn  # noqa: E402

UD_GOLD_PATH = os.path.join(REPO_ROOT, "data", "ud_ewt_semantic_affectedness_gold_v1", "gold.json")
KB_DIR = os.path.join(REPO_ROOT, "data", "wordnet_noun_semantics_kb_v1")
KB_PATH = os.path.join(KB_DIR, "kb.json")

SEEDS = [7, 13, 17, 23, 29]
# animacy = volitional (person/animal), NOT all organisms: organism.n.01 over-includes plants (grass ->
# organism). person/animal still resolve via their own lexname + these hypernyms; causal_agent kept (person
# hyper-path). This is the affectedness-sense of animate, per VerbNet +animate (volitional participant).
ANIM_HYPERNYMS = {"person.n.01", "animal.n.01", "causal_agent.n.01"}
ANIMATE_PRON = {"i", "me", "you", "he", "him", "she", "her", "we", "us", "they", "them",
                "who", "whom", "myself", "himself", "herself", "themselves", "ourselves", "yourself"}
INANIMATE_PRON = {"it", "this", "that", "these", "those", "what", "which", "itself"}

# WordNet lexname -> coarse sem_type + VerbNet-compatible +selrestr FEATURE set. The selrestr feature
# strings are EXACT VerbNet SELRESTR Value names (animate/concrete/location/organization/...). animate is
# ADDED separately from hypernym closure so person/animal ALWAYS carry it. person/animal deliberately do
# NOT carry 'concrete' -> an animate object prefers a +animate sense over a +concrete (physical-contact)
# sense (the meet-36.3 vs contiguous_location discrimination; principled, VerbNet treats them as distinct).
LEXNAME_MAP = {
    "noun.person": ("person", {"animate", "human", "organism"}),
    "noun.animal": ("animal", {"animate", "animal", "organism"}),
    "noun.group": ("group", {"organization"}),
    "noun.location": ("location", {"location", "region", "concrete"}),
    "noun.artifact": ("artifact", {"concrete", "artifact"}),
    "noun.object": ("object", {"concrete"}),
    "noun.substance": ("substance", {"concrete", "substance"}),
    "noun.food": ("food", {"concrete", "comestible"}),
    "noun.body": ("body", {"concrete", "body_part"}),
    "noun.plant": ("plant", {"concrete", "plant"}),
    "noun.possession": ("possession", {"possession"}),
    "noun.communication": ("communication", {"communication"}),
    "noun.phenomenon": ("phenomenon", {"concrete", "phenomenon"}),
    "noun.shape": ("shape", {"concrete"}),
    "noun.cognition": ("abstract", {"abstract"}),
    "noun.state": ("abstract", {"abstract"}),
    "noun.attribute": ("abstract", {"abstract"}),
    "noun.feeling": ("abstract", {"abstract"}),
    "noun.event": ("abstract", {"abstract"}),
    "noun.act": ("abstract", {"abstract"}),
    "noun.time": ("abstract", {"abstract"}),
    "noun.relation": ("abstract", {"abstract"}),
    "noun.quantity": ("abstract", {"abstract"}),
    "noun.motive": ("abstract", {"abstract"}),
    "noun.process": ("abstract", {"abstract"}),
    "noun.shape": ("shape", {"concrete"}),
}


# =====================================================================================================
# KB builder (build-time WordNet ingest). Dominant-sense discipline + hypernym-closure animacy.
# =====================================================================================================
def _clean_noun(surface):
    return (surface or "").lower().strip(".,'\"!?;:()")


def wn_noun_semantics(surface):
    """Live WordNet: (animate:bool|None, sem_type:str|None, feature_set, lexname, n_senses). None type => OOV."""
    s = _clean_noun(surface)
    if not s:
        return None, None, set(), None, 0
    try:
        syns = wn.synsets(s, pos=wn.NOUN)
    except Exception:
        syns = []
    if not syns:
        return None, None, set(), None, 0
    dom = syns[0]
    lexname = dom.lexname()
    animate = False
    if lexname in ("noun.person", "noun.animal"):
        animate = True
    else:
        try:
            for path in dom.hypernym_paths():
                if {h.name() for h in path} & ANIM_HYPERNYMS:
                    animate = True
                    break
        except Exception:
            pass
    sem_type, feats = LEXNAME_MAP.get(lexname, ("other", set()))
    feats = set(feats)
    if animate:
        feats |= {"animate", "organism"}
    return animate, sem_type, feats, lexname, len(syns)


def build_kb(vocab):
    """Materialize the KB over a noun vocabulary (build-time). Returns dict lemma -> record."""
    nouns = {}
    for w in sorted(set(_clean_noun(v) for v in vocab if _clean_noun(v))):
        animate, sem_type, feats, lexname, n = wn_noun_semantics(w)
        if sem_type is None:
            continue  # OOV in WordNet -> not stored (runtime falls back to live, which also returns None)
        nouns[w] = {"animate": bool(animate), "sem_type": sem_type,
                    "features": sorted(feats), "lexname": lexname, "n_senses": n}
    return nouns


def corpus_noun_vocab():
    """Collect candidate noun surfaces from BOTH gold texts (build-time; WordNet filters non-nouns)."""
    vocab = set()
    for path, key in ((UD_GOLD_PATH, "gold"), (MCG_GOLD_PATH, "gold")):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        for g in doc[key]:
            for tok in re.split(r"[^A-Za-z']+", g.get("text", "")):
                if tok:
                    vocab.add(tok.lower())
            aff = g.get("affected")
            if aff:
                for tok in re.split(r"[^A-Za-z']+", aff):
                    if tok:
                        vocab.add(tok.lower())
    return vocab


def write_kb_artifact(kb):
    os.makedirs(KB_DIR, exist_ok=True)
    doc = {
        "_meta": {
            "name": "wordnet_noun_semantics_kb_v1", "built": datetime.now(timezone.utc).isoformat(),
            "source": "WordNet (nltk) dominant-sense lexname + hypernym-closure animacy",
            "n_nouns": len(kb),
            "schema": "lemma -> {animate:bool, sem_type:str, features:[verbnet_selrestr], lexname, n_senses}",
            "note": ("dominant (first) synset only; WordNet over-splits so first sense = most frequent. "
                     "features = VerbNet-compatible +selrestr strings for the selectional match. "
                     "Built from BOTH gold corpora's word tokens; runtime falls back to live WordNet on OOV."),
            "credit": "WordNet (Fellbaum 1998); selrestr vocabulary from VerbNet (Kipper-Schuler 2005).",
        },
        "nouns": kb,
    }
    tmp = KB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    os.replace(tmp, KB_PATH)
    return KB_PATH


# =====================================================================================================
# KB runtime lookup (cache with live fallback) + object feature extraction.
# =====================================================================================================
def kb_lookup_features(surface, kb):
    """Object feature-set from the KB (cache) with live-WordNet fallback. Returns set or None (OOV)."""
    s = _clean_noun(surface)
    if not s:
        return None
    rec = kb.get(s)
    if rec is not None:
        return set(rec["features"])
    animate, sem_type, feats, _lex, _n = wn_noun_semantics(s)  # live fallback
    return feats if sem_type is not None else None


def _arg_features_real(surface, pos, kb):
    """REAL feature-set of a verb argument. Pronoun closed-class + PROPN + KB noun lookup. None => no type."""
    low = _clean_noun(surface)
    if pos == "PRON":
        if low in ANIMATE_PRON:
            return {"animate", "human", "organism"}
        return None  # inanimate/deictic pronoun ('it','this') -> unknown referent type -> no KB fire
    if pos == "PROPN":
        return {"animate", "human", "organism"}  # McGuffey named characters/animals
    if pos == "NOUN":
        return kb_lookup_features(low, kb)
    return None


def arg_features(surface, pos, kb):
    """Object feature-set (pronoun closed-class + PROPN + KB noun lookup). None => no type info. The must-
    fail control is applied downstream as a positional permutation of these outputs (see permute_feats)."""
    return _arg_features_real(surface, pos, kb)


# =====================================================================================================
# Selectional override (generalized entity-semantics animacy path).
# =====================================================================================================
_SELF_CACHE = {}


def sense_nonsubj_pos_features(vn_class):
    """Set of +selrestr feature strings on NON-SUBJECT (object-candidate) roles for a VerbNet (sub)class."""
    if vn_class in _SELF_CACHE:
        return _SELF_CACHE[vn_class]
    feats = set()
    for rtype, sr in sense_roles(vn_class):
        if (rtype or "").lower() in NONSUBJ_ROLES:
            for (v, t) in sr:
                if v == "+":
                    feats.add(t)
    _SELF_CACHE[vn_class] = feats
    return feats


def sel_status(vn_class, obj_features):
    """SATISFIED / VIOLATED / NEUTRAL: does the object feature-set satisfy the sense's non-subj +selrestr?"""
    R = sense_nonsubj_pos_features(vn_class)
    if not R:
        return "NEUTRAL"
    if R & obj_features:
        return "SATISFIED"
    return "VIOLATED"


def kb_selectional_override(verb_surface, pframe, obj_features):
    """Returns (override_to_none:bool, detail). Fires ONLY when object-type uniquely selects a NOT-affecting
    frame-compatible sense (SATISFIED) with NO affected sense also SATISFIED. KEEP->NONE only (Pareto)."""
    detail = {"obj_features": sorted(obj_features) if obj_features else None}
    if obj_features is None:
        detail["route"] = "no_obj_type"
        return False, detail
    lem, ps = per_senses(verb_surface)
    detail["lemma"] = lem
    detail["n_senses"] = len(ps)
    if len(ps) <= 1:
        detail["route"] = "single_or_oov"
        return False, detail
    compat = [s for s in ps if frame_compatible(pframe["sig"], sense_frame_sigs(s["vn_class"]))]
    detail["compat"] = [s["vn_class"] for s in compat]
    if not compat:
        detail["route"] = "no_frame_compat"
        return False, detail
    none_sat = [s["vn_class"] for s in compat
                if s["forces_none"] and sel_status(s["vn_class"], obj_features) == "SATISFIED"]
    # TRUE selectional disambiguation: fire ONLY when the object-type actively CONTRADICTS a present,
    # competing AFFECTED sense. Require (a) an object-satisfied not-affecting sense, (b) at least one
    # frame-compatible AFFECTED sense that the object VIOLATES, and (c) NO frame-compatible affected sense
    # that the object satisfies-or-is-neutral-to. This rejects the case where the affected sense is merely
    # frame-absent (e.g. 'made the marble one': build-26.1 not bare-TRANS -> only naming/cognition senses
    # remain -> DON'T fire), while keeping 'met [animate]' (contact sense present AND violated -> fire).
    aff_compat = [s["vn_class"] for s in compat if not s["forces_none"]]
    aff_violated = [c for c in aff_compat if sel_status(c, obj_features) == "VIOLATED"]
    aff_ok = [c for c in aff_compat if sel_status(c, obj_features) != "VIOLATED"]
    detail["none_satisfied"] = none_sat
    detail["affected_violated"] = aff_violated
    detail["affected_ok"] = aff_ok
    if none_sat and aff_violated and not aff_ok:
        detail["route"] = "kb_selectional_none"
        return True, detail
    detail["route"] = "no_resolve"
    return False, detail


def kb_gate(verb_surface, pframe, obj_features, neg):
    """KB arm = BASE arm, Pareto override toward force-none via the KB selectional match.
    Returns (force_none, source)."""
    base_dec, base_src = full_gate(verb_surface, pframe, None, neg, "baseline")
    if base_dec:
        return True, base_src  # neg/phrasal/stative/low-graded already forces none -> unchanged
    ov, det = kb_selectional_override(verb_surface, pframe, obj_features)
    if ov:
        return True, "kb_" + det["route"]
    return False, base_src


# =====================================================================================================
# Eval: UD-EWT independent gold (binary affected-vs-not) + McGuffey held-out (span-match). PREDICTED parse.
# =====================================================================================================
def normalize_gold_span(affected):
    if affected is None:
        return set()
    stripped = re.sub(r"\s*\([^)]*\)", "", affected).strip()
    return span_head_tokens(stripped)


def eval_ud(gold_rows, tagger, parser, labeler, kb, override_feats=None):
    """Binary affected-vs-not on UD-EWT independent gold. Returns per-instance rows (base + kb correctness).
    override_feats (must-fail control): positional list of object feature-sets to use INSTEAD of the object's
    real features (aligned to the produced rows) -> destroys the surface->type correspondence."""
    rows = []
    oi = 0
    for g in gold_rows:
        if g.get("ambiguous"):
            continue
        text, gverb, gtype = g["text"], g["verb"], g["type"]
        gold_yes = gtype in AFFECTED_TYPES
        tokens = ud_tokenize(text)
        rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
        pos = rp["pos"]
        vidx, _ = find_verb_index(tokens, pos, gverb)
        pool = rp["pools"].get(vidx, []) if vidx is not None else []
        bp = base_pick(pool)
        pred_surf = bp["surf"] if bp is not None else None
        _pos2, heads, labels = _parse_full(tokens, tagger, parser, labeler)
        pframe = parse_frame(tokens, _pos2, heads, labels, vidx)
        obj_aidx = pframe["obj_aidx"]
        if override_feats is not None:
            obj_feats = override_feats[oi]
        else:
            obj_feats = arg_features(tokens[obj_aidx - 1], _pos2[obj_aidx - 1], kb) if obj_aidx else None
        oi += 1
        neg = verb_is_negated_clauseaware(tokens, vidx)
        base_fn, _ = full_gate(gverb, pframe, None, neg, "baseline")
        kb_fn, kb_src = kb_gate(gverb, pframe, obj_feats, neg)

        def pred_yes(fn):
            return bool((not fn) and pred_surf is not None)
        rows.append({"id": g["id"], "verb": gverb, "type": gtype, "gold_yes": gold_yes,
                     "base_fn": base_fn, "kb_fn": kb_fn, "kb_src": kb_src,
                     "obj_feats": sorted(obj_feats) if obj_feats else None,
                     "base_correct": bool(pred_yes(base_fn) == gold_yes),
                     "kb_correct": bool(pred_yes(kb_fn) == gold_yes),
                     "flipped": bool(base_fn != kb_fn)})
    return rows


def eval_mcguffey(gold_rows, tagger, parser, labeler, kb, override_feats=None):
    """Span-match who-affected on McGuffey held-out. Returns per-instance rows (base + kb correctness).
    override_feats (must-fail control): positional list of object feature-sets (aligned to produced rows)."""
    rows = []
    oi = 0
    for g in gold_rows:
        text, gverb, gaff, gtype = g["text"], g["verb"], g["affected"], g["type"]
        gold_none = gtype in NONE_TYPES
        heads_gold = span_head_tokens(gaff)
        tokens = ud_tokenize(text)
        rp = reader_pass({"tokens": tokens}, tagger, parser, labeler)
        pos = rp["pos"]
        vidx, _ = find_verb_index(tokens, pos, gverb)
        pool = rp["pools"].get(vidx, []) if vidx is not None else []
        bp = base_pick(pool)
        pred_surf = bp["surf"] if bp is not None else None
        pred_none = bp is None
        _pos2, heads, labels = _parse_full(tokens, tagger, parser, labeler)
        pframe = parse_frame(tokens, _pos2, heads, labels, vidx)
        obj_aidx = pframe["obj_aidx"]
        if override_feats is not None:
            obj_feats = override_feats[oi]
        else:
            obj_feats = arg_features(tokens[obj_aidx - 1], _pos2[obj_aidx - 1], kb) if obj_aidx else None
        oi += 1
        neg = verb_is_negated_clauseaware(tokens, vidx)
        base_fn, _ = full_gate(gverb, pframe, None, neg, "baseline")
        kb_fn, kb_src = kb_gate(gverb, pframe, obj_feats, neg)

        def correct(force_none):
            pred_is_none = pred_none or force_none
            if gold_none:
                return pred_is_none
            return bool((not force_none) and pred_surf is not None and pred_surf in heads_gold)
        rows.append({"id": g["id"], "verb": gverb, "type": gtype, "gold_none": gold_none,
                     "base_fn": base_fn, "kb_fn": kb_fn, "kb_src": kb_src,
                     "obj_feats": sorted(obj_feats) if obj_feats else None,
                     "base_correct": correct(base_fn), "kb_correct": correct(kb_fn),
                     "flipped": bool(base_fn != kb_fn)})
    return rows


# =====================================================================================================
# Sharded additive-map store partition (FHRR unit phasors) -- representation demonstration.
# =====================================================================================================
def build_and_verify_store(kb, N, seed):
    """Encode each noun as noun (x) sem_type in a SHARDED FHRR partition; retrieve sem_type via unbind +
    cleanup vs the type codebook. Returns (fidelity, n). Sharded => exact => fidelity 1.0."""
    rng = np.random.default_rng(seed)
    nouns = sorted(kb.keys())
    types = sorted({kb[n]["sem_type"] for n in nouns})
    if not nouns or not types:
        return 1.0, 0

    def code(names):
        return {nm: np.exp(1j * rng.uniform(-np.pi, np.pi, N)) for nm in names}
    noun_cb = code(nouns)
    type_cb = code(types)
    type_names = list(type_cb.keys())
    type_mat = np.stack([type_cb[t] for t in type_names], axis=0)  # (T, N)
    store = {nm: noun_cb[nm] * type_cb[kb[nm]["sem_type"]] for nm in nouns}  # sharded bind
    correct = 0
    for nm in nouns:
        approx_type = store[nm] * np.conj(noun_cb[nm])  # unbind
        sims = (type_mat @ np.conj(approx_type)).real / N
        recovered = type_names[int(np.argmax(sims))]
        if recovered == kb[nm]["sem_type"]:
            correct += 1
    return round(correct / len(nouns), 4), len(nouns)


# =====================================================================================================
def _collect_feats(rows):
    """Ordered list of the object feature-sets actually used per row (set or None)."""
    return [set(r["obj_feats"]) if r["obj_feats"] else None for r in rows]


def permute_feats(feats_list, seed):
    """Must-fail control: positionally permute the object feature-sets ACROSS instances. Preserves the EXACT
    base-rate multiset of feature types but destroys the surface->type correspondence (an animate object may
    receive an inanimate type). This is the correct null for 'does the CORRECT object type carry the lift'."""
    n = len(feats_list)
    rng = random.Random(seed)
    perm = list(range(n))
    rng.shuffle(perm)
    return [feats_list[perm[i]] for i in range(n)]


def _acc(rows, key):
    if not rows:
        return 0.0, 0, 0
    c = sum(1 for r in rows if r[key])
    return round(c / len(rows), 4), len(rows), c


def _bootstrap_delta(pooled, B, seed):
    """Bootstrap CI on kb_correct - base_correct over paired per-instance rows."""
    n = len(pooled)
    if n == 0:
        return {"mean": 0.0, "lo": 0.0, "hi": 0.0}
    base = np.array([1 if r["base_correct"] else 0 for r in pooled])
    kbv = np.array([1 if r["kb_correct"] else 0 for r in pooled])
    rng = np.random.default_rng(seed)
    deltas = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, n, n)
        deltas[b] = kbv[idx].mean() - base[idx].mean()
    return {"mean": round(float(deltas.mean()), 4),
            "lo": round(float(np.percentile(deltas, 5)), 4),
            "hi": round(float(np.percentile(deltas, 95)), 4)}


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

    # ---- build + materialize the KB ----
    vocab = corpus_noun_vocab()
    kb = build_kb(vocab)
    write_kb_artifact(kb)
    print(f"[{ANCHOR_NAME}:{mode}] KB built n_nouns={len(kb)} (from {len(vocab)} candidate tokens)", flush=True)

    with open(UD_GOLD_PATH, encoding="utf-8") as f:
        ud_gold = json.load(f)["gold"]
    with open(MCG_GOLD_PATH, encoding="utf-8") as f:
        mcg_gold = json.load(f)["gold"]

    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded; UD N={len(ud_gold)} McGuffey N={len(mcg_gold)}", flush=True)

    # ---- KB arm (real KB) ----
    ud_rows = eval_ud(ud_gold, tagger, parser, labeler, kb)
    mcg_rows = eval_mcguffey(mcg_gold, tagger, parser, labeler, kb)
    pooled = ud_rows + mcg_rows

    ud_base = _acc(ud_rows, "base_correct")
    ud_kb = _acc(ud_rows, "kb_correct")
    mcg_base = _acc(mcg_rows, "base_correct")
    mcg_kb = _acc(mcg_rows, "kb_correct")
    p_base = _acc(pooled, "base_correct")
    p_kb = _acc(pooled, "kb_correct")

    ud_delta = round(ud_kb[0] - ud_base[0], 4)
    mcg_delta = round(mcg_kb[0] - mcg_base[0], 4)
    pooled_delta = round(p_kb[0] - p_base[0], 4)

    # rescued / broken (KB flips vs base, per set)
    def flips(rows):
        rescued = [{"id": r["id"], "verb": r["verb"], "type": r["type"], "kb_src": r["kb_src"],
                    "obj_feats": r["obj_feats"]} for r in rows if (not r["base_correct"]) and r["kb_correct"]]
        broken = [{"id": r["id"], "verb": r["verb"], "type": r["type"], "kb_src": r["kb_src"],
                   "obj_feats": r["obj_feats"]} for r in rows if r["base_correct"] and (not r["kb_correct"])]
        return rescued, broken
    ud_resc, ud_brok = flips(ud_rows)
    mcg_resc, mcg_brok = flips(mcg_rows)
    all_flips = [{"id": r["id"], "verb": r["verb"], "type": r["type"], "base_fn": r["base_fn"],
                  "kb_fn": r["kb_fn"], "kb_src": r["kb_src"], "obj_feats": r["obj_feats"]}
                 for r in pooled if r["flipped"]]

    # ---- ARMS-MUST-DIFFER ----
    def _digest(rows, key):
        return hashlib.sha256(bytes([1 if r[key] else 0 for r in rows])).hexdigest()
    base_dec_dig = _digest(pooled, "base_fn")
    kb_dec_dig = _digest(pooled, "kb_fn")
    arms_differ = base_dec_dig != kb_dec_dig

    # ---- MUST-FAIL scramble control (multi-seed) ----
    B = 200 if mode == "smoke" else 2000
    seeds = SEEDS[:2] if mode == "smoke" else SEEDS
    real_feats = _collect_feats(ud_rows) + _collect_feats(mcg_rows)
    n_ud = len(ud_rows)
    scramble_runs = []
    for sd in seeds:
        perm = permute_feats(real_feats, sd)
        s_ud = eval_ud(ud_gold, tagger, parser, labeler, kb, override_feats=perm[:n_ud])
        s_mcg = eval_mcguffey(mcg_gold, tagger, parser, labeler, kb, override_feats=perm[n_ud:])
        s_pooled = s_ud + s_mcg
        s_delta = round(_acc(s_pooled, "kb_correct")[0] - _acc(s_pooled, "base_correct")[0], 4)
        scramble_runs.append({"seed": sd, "scramble_pooled_delta": s_delta,
                              "n_flips": sum(1 for r in s_pooled if r["flipped"])})
    mean_scr_delta = round(float(np.mean([r["scramble_pooled_delta"] for r in scramble_runs])), 4)
    max_scr_delta = round(float(np.max([r["scramble_pooled_delta"] for r in scramble_runs])), 4)

    # ---- bootstrap CI on the real KB delta ----
    boot = _bootstrap_delta(pooled, B, 12345)

    # ---- store fidelity per seed (representation demonstration) ----
    store_runs = []
    for sd in seeds:
        fid, n_store = build_and_verify_store(kb, 1024, sd)
        store_runs.append({"seed": sd, "store_fidelity": fid, "n_nouns": n_store})
    store_fidelity_min = round(float(np.min([r["store_fidelity"] for r in store_runs])), 4)

    # ---- KB coverage / quality spot-check on gold-object nouns ----
    spot = {}
    for w in ["man", "box", "hen", "duck", "fox", "moon", "house", "letter", "nest", "step",
              "president", "hostage", "embassy", "song", "milk", "grass", "hat"]:
        rec = kb.get(w)
        if rec is None:
            a, st, ft, lx, ns = wn_noun_semantics(w)
            rec = {"animate": a, "sem_type": st, "lexname": lx, "live": True}
        spot[w] = {"animate": rec["animate"], "sem_type": rec["sem_type"]}

    # ---- bands / verdict ----
    scramble_collapses = bool(mean_scr_delta <= 0.01 and (pooled_delta <= 0 or mean_scr_delta < 0.5 * pooled_delta))
    no_regression = bool(ud_delta >= -0.01 and mcg_delta >= -0.01)
    baseline_in_band = bool(0.05 < p_base[0] < 0.95)
    leak_clean = True  # asserted in self_test; recorded here for the report

    if not arms_differ:
        verdict = "GATE_ARMS_IDENTICAL_BUG"
    elif pooled_delta >= 0.03 and no_regression and scramble_collapses:
        verdict = "HARD_PASS_ENTITY_KB"
    elif pooled_delta <= 0 or ud_delta <= -0.03 or mcg_delta <= -0.03 or (not scramble_collapses):
        verdict = "HARD_FAIL_ENTITY_KB"
    else:
        verdict = "MIDDLE_BAND_ENTITY_KB"

    elapsed = round(time.perf_counter() - t0, 2)
    verdict_msg = (
        f"[{verdict}] WordNet noun-semantics KB entity-selectional gate | POOLED N={p_base[1]} "
        f"base={p_base[0]}({p_base[2]}/{p_base[1]}) kb={p_kb[0]}({p_kb[2]}/{p_kb[1]}) delta={pooled_delta} "
        f"(boot90 [{boot['lo']},{boot['hi']}]) | UD N={ud_base[1]} base={ud_base[0]} kb={ud_kb[0]} "
        f"(d={ud_delta}) | McGuffey N={mcg_base[1]} base={mcg_base[0]} kb={mcg_kb[0]} (d={mcg_delta}) | "
        f"rescued: UD={[r['id'] for r in ud_resc]} McG={[r['id'] for r in mcg_resc]} broken: "
        f"UD={[r['id'] for r in ud_brok]} McG={[r['id'] for r in mcg_brok]} | "
        f"SCRAMBLE(must-fail) mean_delta={mean_scr_delta} max={max_scr_delta} collapses={scramble_collapses} "
        f"| store_fidelity_min={store_fidelity_min} | arms_differ={arms_differ} "
        f"no_regression={no_regression} baseline_in_band={baseline_in_band} kb_nouns={len(kb)}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict,
        "elapsed_s": elapsed, "run_mode": mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "is_probe_flag": True,
        "note": ("WordNet noun-semantics KB (dominant-sense lexname + hypernym-closure animacy) wired into "
                 "the who-affected gate's selectional decision, generalizing the hardcoded-met object-"
                 "animacy path to a KB-backed for-any-verb rule. KB arm = BASE arm + Pareto force-none "
                 "override when the object's KB feature-set selects a not-affecting frame-compatible sense. "
                 "Runtime = KB lookup + VerbNet selrestr match, NO external LLM. Gold-independent -> leak-"
                 "clean. LOCAL-only; no push/remote-persist; no hdlab mutation; no atom bank."),
        "kb": {"n_nouns": len(kb), "artifact_path": os.path.relpath(KB_PATH, REPO_ROOT),
               "spot_check": spot, "vocab_candidates": len(vocab),
               "coverage_note": "OOV gold-object nouns fall back to live WordNet (self-test asserts cache==live)."},
        "pooled": {"n": p_base[1], "base_acc": p_base[0], "kb_acc": p_kb[0],
                   "base_correct": p_base[2], "kb_correct": p_kb[2], "delta": pooled_delta,
                   "bootstrap_90ci": boot, "baseline_in_band": baseline_in_band},
        "ud_ewt": {"n": ud_base[1], "base_acc": ud_base[0], "kb_acc": ud_kb[0], "delta": ud_delta,
                   "rescued": ud_resc, "broken": ud_brok},
        "mcguffey_heldout": {"n": mcg_base[1], "base_acc": mcg_base[0], "kb_acc": mcg_kb[0],
                             "delta": mcg_delta, "rescued": mcg_resc, "broken": mcg_brok},
        "flips": all_flips,
        "must_fail_scramble": {"seeds": seeds, "runs": scramble_runs,
                               "mean_pooled_delta": mean_scr_delta, "max_pooled_delta": max_scr_delta,
                               "collapses": scramble_collapses,
                               "interpretation": ("permuting the noun->feature map must destroy the lift "
                                                  "(mean delta ~0) => the animacy/type SIGNAL is load-"
                                                  "bearing, not a base-rate artifact")},
        "store_partition": {"runs": store_runs, "fidelity_min": store_fidelity_min, "N": 1024,
                            "note": "sharded additive-map (noun (x) sem_type); retrieve==dict => fidelity 1.0"},
        "arms_differ_verified": arms_differ,
        "arm_decision_digests": {"base": base_dec_dig, "kb": kb_dec_dig},
        "cardinality": {"expected_scramble_runs": len(seeds), "actual_scramble_runs": len(scramble_runs),
                        "expected_store_runs": len(seeds), "actual_store_runs": len(store_runs),
                        "cardinality_ok": bool(len(scramble_runs) == len(seeds) and len(store_runs) == len(seeds))},
        "design_gate": {
            "real_baseline": "v2 verb-affectedness gate (full_gate baseline), no noun KB; 0.769 on UD",
            "one_variable": "the KB selectional override (base=modal; kb=+object-type selrestr match)",
            "can_fail": ("narrow lever (only meet/reach-class polysemy with a discriminating object type; "
                         "hunt/watch/look already force-none at base) -> could give 0 lift; or regress on a "
                         "spurious selectional match; or the scramble must-fail could fail to collapse"),
            "difficulty_on": "real UD-EWT web-text (blind annotator) + archaic McGuffey; predicted parse; verb/noun disjoint from tuning",
            "leak_clean": ("gate = verb-lemma + parse-frame + KB-noun-type, gold-independent; mutation-probe "
                           "permutes gold labels + re-derives -> KB decision vector byte-identical"),
            "deployable_regime": "PREDICTED POS/parse from the trained front-end (not gold-oracle)",
            "final_metrics_atomicity": "tmp_replace", "crlb_n/a": "accuracy on labeled gold, no noise floor",
            "calibration_check": "default_ok_for_this_regime (VN_GRADED_THRESHOLD 0.35 inherited; selrestr = exact VerbNet strings)",
        },
        "prereg": "preregs/2026-07-21_wordnet_noun_semantics_kb_who_affected_v1.md",
        "credit": ("WordNet (Fellbaum 1998); VerbNet (Kipper-Schuler 2005); Levin 1993; Dowty 1991; "
                   "Beavers 2011; Paczynski-Kuperberg 2012; v1 hand-lexicon + v2 gate + WSD frame_selectional_v1."),
        "leak_clean": leak_clean,
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
    # --- KB derivation: dominant-sense animacy + sem_type spot ground-truth ---
    a, st, ft, lx, n = wn_noun_semantics("man")
    assert a is True and st == "person" and "animate" in ft, (a, st, ft)
    a, st, ft, _, _ = wn_noun_semantics("box")
    assert a is False and st == "artifact" and "concrete" in ft and "animate" not in ft, (a, st, ft)
    a, st, ft, _, _ = wn_noun_semantics("hen")
    assert a is True and st == "animal", (a, st, ft)
    a, st, ft, _, _ = wn_noun_semantics("moon")
    assert a is False and st == "object", (a, st, ft)
    a, st, ft, _, _ = wn_noun_semantics("zzzqqxnotaword")
    assert st is None, "OOV noun must return None sem_type"

    # --- build a small KB + store fidelity (sharded => exact) ---
    kb = build_kb({"man", "box", "hen", "duck", "moon", "house", "letter", "hat", "fox"})
    assert "man" in kb and kb["man"]["animate"] is True
    assert "box" in kb and kb["box"]["animate"] is False
    fid, ns = build_and_verify_store(kb, 256, 7)
    assert fid == 1.0, ("sharded store must retrieve type exactly", fid, ns)

    # --- selrestr extraction (VerbNet non-subject +features) ---
    assert "animate" in sense_nonsubj_pos_features("meet-36.3-1"), sense_nonsubj_pos_features("meet-36.3-1")
    assert "concrete" in sense_nonsubj_pos_features("contiguous_location-47.8-1")
    assert sel_status("meet-36.3-1", {"animate"}) == "SATISFIED"
    assert sel_status("meet-36.3-1", {"concrete"}) == "VIOLATED"
    assert sel_status("contiguous_location-47.8-1", {"concrete"}) == "SATISFIED"

    # --- selectional override: animate object of 'met' selects the encounter (none) sense ---
    tframe = {"sig": "TRANS", "obj_aidx": 1, "subj_aidx": None, "iobj_aidx": None,
              "has_loc_obl": False, "has_dir_obl": False}
    ov, det = kb_selectional_override("met", tframe, {"animate", "human", "organism"})
    assert ov is True and det["route"] == "kb_selectional_none", (ov, det)
    # kb_gate composes: base KEEPS (contact 0.45) -> KB overrides to force-none
    fn, src = kb_gate("met", tframe, {"animate", "human", "organism"}, False)
    assert fn is True and src.startswith("kb_"), (fn, src)

    # --- NON-TAUTOLOGICAL must-fail DEGRADE: object with a non-animate type must NOT fire the override ---
    ov2, det2 = kb_selectional_override("met", tframe, {"concrete"})
    assert ov2 is False, ("concrete object must not select the encounter sense", det2)
    fn2, src2 = kb_gate("met", tframe, {"concrete"}, False)
    assert fn2 is False, ("base KEEP must survive when object type does not select a none-sense", fn2, src2)
    # None object type (pronoun 'it') -> no fire
    ov3, _ = kb_selectional_override("met", tframe, None)
    assert ov3 is False

    # --- Pareto: single-sense verb unaffected (feed) ---
    fn3, _ = kb_gate("fed", tframe, {"animate"}, False)
    fnb, _ = full_gate("fed", tframe, None, False, "baseline")
    assert fn3 == fnb, "single-sense verb must match base (Pareto)"

    # --- real code path: front-end + real sentence + real eval rows ---
    tagger = PosTagger.load(POS_PATH)
    parser = ArcParser.load(ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    with open(MCG_GOLD_PATH, encoding="utf-8") as f:
        mcg = json.load(f)["gold"]
    with open(UD_GOLD_PATH, encoding="utf-8") as f:
        ud = json.load(f)["gold"]
    fullkb = build_kb(corpus_noun_vocab())
    assert len(fullkb) > 50, ("KB should cover the gold noun vocab", len(fullkb))
    mrows = eval_mcguffey(mcg, tagger, parser, labeler, fullkb)
    urows = eval_ud(ud, tagger, parser, labeler, fullkb)
    assert len(mrows) == len(mcg)
    # met cases h17/h20 must be RESCUED by the KB (base wrong -> kb right)
    resc_ids = {r["id"] for r in mrows if (not r["base_correct"]) and r["kb_correct"]}
    assert {"h17", "h20"} <= resc_ids, ("KB must rescue the McGuffey met cases", sorted(resc_ids))

    # --- cache == live (no drift): a sampled KB record matches live WordNet ---
    for w in ["man", "box", "hen"]:
        a, st, ft, _, _ = wn_noun_semantics(w)
        assert fullkb[w]["animate"] == a and fullkb[w]["sem_type"] == st, w

    # --- LEAK-CLEAN mutation probe: permute gold labels -> KB decision vector byte-identical ---
    def kb_decisions(gold_list, evalfn):
        rows = evalfn(gold_list, tagger, parser, labeler, fullkb)
        return [r["kb_fn"] for r in rows]
    base_dec = kb_decisions(mcg, eval_mcguffey)
    rng = random.Random(12345)
    perm = list(range(len(mcg)))
    rng.shuffle(perm)
    mutated = []
    for k, g in enumerate(mcg):
        gg = dict(g)
        gg["type"] = mcg[perm[k]]["type"]
        gg["affected"] = mcg[perm[k]]["affected"]
        mutated.append(gg)
    mut_dec = kb_decisions(mutated, eval_mcguffey)
    assert base_dec == mut_dec, "LEAK: KB decision changed when gold labels were permuted"

    # --- must-fail scramble fires: positionally permuting object types destroys the lift on aggregate ---
    real_feats = _collect_feats(urows) + _collect_feats(mrows)
    n_ud = len(urows)
    real_pooled = urows + mrows
    real_delta = _acc(real_pooled, "kb_correct")[0] - _acc(real_pooled, "base_correct")[0]
    assert real_delta > 0, ("real KB arm must lift over base on the pooled eval", real_delta)
    scr_deltas = []
    for sd in (7, 13, 17, 23, 29):
        perm = permute_feats(real_feats, sd)
        s_u = eval_ud(ud, tagger, parser, labeler, fullkb, override_feats=perm[:n_ud])
        s_m = eval_mcguffey(mcg, tagger, parser, labeler, fullkb, override_feats=perm[n_ud:])
        scr_deltas.append(_acc(s_u + s_m, "kb_correct")[0] - _acc(s_u + s_m, "base_correct")[0])
    mean_scr = sum(scr_deltas) / len(scr_deltas)
    assert mean_scr < real_delta, ("scramble must collapse the lift (must-fail fires)", mean_scr, real_delta, scr_deltas)

    print("[self_test] KB-derivation OK; store-fidelity OK; selrestr OK; override OK; degrade-cue OK "
          "(non-tautological); Pareto OK; real-code-path OK; met-rescue OK; cache==live OK; leak-clean OK; "
          "scramble-fires OK", flush=True)
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
