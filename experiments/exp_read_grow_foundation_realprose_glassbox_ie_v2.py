"""exp_read_grow_foundation_realprose_glassbox_ie_v2 -- UPGRADE the glass-box IE parser past its failure frontier.

v1 (commit d39c6b273) built a GLASS-BOX, RULE-BASED IE parser over REAL simple prose: correct_rate = 0.765 on
34 sentences. Its per-class breakdown localized THREE deterministic failure modes (all covered-but-WRONG, i.e.
the parser FIRED and produced a reversed/partial triple):
  passive              (correct 0.00): "The worm is eaten by the frog." -> took 'by'-agent as object -> REVERSED.
  coordination_subject (correct 0.00): "The cat and the dog eat bread." -> nearest-conjunct only -> 1 of 2 facts.
  relative_clause      (correct 0.00): "The cat that lives in the barn eats a fish." -> subordinate verb won.
And ONE correct-abstain residual: out_of_schema (owl sleeps / mouse runs) -> no in-schema relation -> abstain.

This v2 implements the drill's classical roadmap (research_glass_box_reading_robust_parsing_ceiling_2026-07-16):
  PASSIVE handling      -- be-AUX + PAST-PARTICIPLE + 'by'-agent -> assign roles by GRAMMAR not surface order
                           (patient = surface subject, agent = by-NP) -> correct (agent, rel, patient). No reversal.
  COORDINATION split    -- CALM-style: emit one triple PER conjunct (subject-coord AND object-coord), via a
                           cross-product over split subject/object noun lists. No nearest-conjunct truncation.
  RELATIVE-CLAUSE attach -- ClausIE-style clause typing: a relativizer (that/which/who) right after the head noun
                           marks a relative clause; its verb is SKIPPED and the MATRIX verb (next verb) is used;
                           the matrix SUBJECT is the head noun, not a noun inside the RC.
  (RELNOUN / Hearst / a narrow neural parser are NOT added here -- out of scope; still fully symbolic, NO LLM.)

STILL GLASS-BOX / NO-LLM (load-bearing honesty): the parser remains FULLY SYMBOLIC deterministic rules over a
  POS-lexicon tag sequence. The new rules inject SYNTACTIC STRUCTURE (word classes + clause typing), NOT FACTS.
  The parser CANNOT hallucinate a fact -- it can MIS-APPLY a rule (wrong/no triple) but only over tokens present
  in the input. A general system swaps the hand lexicon for a learned/statistical POS tagger (the SCALE-UP);
  the drill's ONE carve-out (a narrow, structure-only neural dependency parser) is deferred to a later rung.

HONEST RESIDUAL (the drill's permanent classical gaps -- NOT fixed here, reported as the ceiling-limiter):
  COREFERENCE  -- a pronoun subject with no in-sentence antecedent ("It eats the worm.") -> ABSTAIN (correct not
                  to hallucinate). Does NOT shrink with simpler prose; unaddressed by any classical IE technique.
  OUT-OF-SCHEMA -- a relation not in the schema ("The owl sleeps in the tree.") -> ABSTAIN. A closed-schema
                  extractor correctly declines rather than force a wrong relation.
  These two classes keep correct_rate BELOW 1.0 by DESIGN -- a precision-favoring parser abstains when unsure.

BEFORE vs AFTER (apples-to-apples): metrics report the OLD positional extractor (ie_extract_baseline_positional,
  a frozen copy of v1's logic) AND the UPGRADED extractor (ie_extract) on the SAME broadened corpus, per class.
  The broadened corpus adds MORE real early-reader sentences of EACH hard structure (passive/coord/rel-clause
  now n=5 each, up from n=2) PLUS coreference (new residual) -- so the lift is measured on far more than v1's
  8 hard cases, not a cherry-picked few.

METRICS (reported SEPARATELY):
  (a) EXTRACTION on real prose (seed-independent, pure parser), BASELINE vs UPGRADED:
        parser_coverage      = fraction of sentences yielding ANY well-formed triple
        parser_precision      = fraction of EMITTED triples that are CORRECT (triple-level; coordination-aware)
        parser_correct_rate  = fraction of sentences whose EMITTED triple-set EXACTLY equals the gold set
        per_class breakdown  = coverage + correct-rate per structure class (the lift, per failure mode)
        residual             = out_of_schema + coreference correctly-abstained counts (the honest ceiling)
  (b) FOUNDATION correctness on what IS extracted: precision (no false/misfire fact admitted) + true-recall.
  (c) QUERY accuracy: retrieve a stored object given an (s, r) cue via the grown VSA store.
  (d) GATE behavior: FULL vs NO_GATE precision (does the gate clean up parser noise?) + accept_false_rate.
  Localization arms: ORACLE lexicon (isolates PARSER error from lexicon error) + RANDOM lexicon (floor).

PRE-REG (envelope-fail-bands; I own the bands; set BEFORE running). "target classes" = {passive,
  coordination_subject, coordination_object, relative_clause}; "guard classes" = the simple structures v1 already
  read (simple_svo, svo_prep, svo_no_determiner, adjective_modifier, present_continuous, plural_no_determiner,
  adverb_modifier).
  HARD-PASS (the upgrade LIFTS the hard classes materially toward the ~70-85%P classical ceiling WITHOUT breaking
             the simple cases, and the read->grow loop still builds a correct queryable foundation):
    parser_coverage >= 0.60 AND parser_precision >= 0.80 AND parser_correct_rate >= 0.80 AND
    every target-class correct_rate >= 0.80 AND every guard-class correct_rate == 1.00 AND
    FULL foundation_precision >= 0.90 AND accept_false_rate == 0.0 AND FULL true_recall >= 0.70 AND
    query_acc >= 0.80 AND (FULL foundation_precision - NO_GATE foundation_precision) >= 0.05 AND
    novel_owl_ok AND hold_release_ok.
  HARD-FAIL (rules do not generalize / break the simple cases / no lift):
    parser_correct_rate <= baseline_correct_rate + 0.01 OR any target-class correct_rate == 0.0 OR
    any guard-class correct_rate < 1.0 OR parser_precision < 0.40 OR FULL foundation_precision < 0.60 OR
    accept_false_rate == 1.0 OR query_acc < 0.40.
  MIDDLE otherwise (partial: some hard structures fixed, some not -- report which + the residual toward ceiling).

Local numpy, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (foundation grows fact-by-fact; wall < 10s).
Storage: SHARDED (one VSA vector per accepted fact) per META_STORAGE_STRATEGY. progress_logging = print_flush_true.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FULL_LOOP vs NO_GATE accepted-store hash differs).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor. FHRR cleanup among ~25 concepts at N=1024 with 3-term bundle is
#     z ~ sqrt(2N/3) ~ 26 sigma -> VSA decode reachable ~1.0; extraction is gated by PARSER rule-misfire +
#     LEXICON map error, NOT by phasor noise.
# - baseline_in_band at smoke: NO_GATE foundation_precision < 1.0 (admits false facts); FULL ~1.0; RANDOM-lex ~0.
# - discriminator survives scale: corpus is FIXED-size (real prose, hand-authored GT). Discriminators =
#     (1) UPGRADED parser correct on passive/coord/rel-clause (deterministic, asserted at self-test),
#     (2) BASELINE parser still WRONG on those (frozen v1 logic, asserted at self-test) -> the lift is real,
#     (3) residual (coref/out-of-schema) still ABSTAIN -> correct_rate < 1.0 (asserted),
#     (4) gate-vs-nogate precision + accept_false_rate (injected false facts deterministic; FULL rejects).
# - HARD_PASS strictly above floor; explicit bands in prereg JSON.
# - real_code_path (F.1): self_test constructs the REAL imported objects (learn_lexicon + SVO encode/decode +
#     FoundationStore) at tiny scale + the REAL ie_extract, and asserts (not a synthetic-only branch).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab ordering; NO hash()/list(set()) for seeds.
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_foundation_realprose_glassbox_ie_v2"

# --- GENUINE REUSE of the proven downstream (imported, not rebuilt) ---
from experiments.exp_read_grow_foundation_endtoend_v1 import (
    N_DIM,
    RELATIONS,
    ENTITIES,
    ANIMALS,
    FOODS,
    PLACES,
    GT_TYPE,
    build_typed_foundation,
    build_lexicon_train,
    FoundationStore,
    _svo_make_phasors,
    _encode_meaning,
    _decode_meaning,
    _learn_lexicon,
    _lexicon_top,
)

# ---------------------------------------------------------------------------
# POS-lexicon (closed-class function words + content lexicon + productive morphology). Glass-box; injects
# WORD-CLASS + CLAUSE structure, never facts.
# ---------------------------------------------------------------------------
DETS = {"the", "a", "an"}
PREPS = {"in", "on", "by", "at", "near", "under", "with", "to"}
RELZRS = {"that", "which", "who"}           # relativizers -> a relative clause
BE_AUX = {"is", "are", "was", "were", "be", "been", "am"}
PRONS = {"it", "he", "she", "they", "him", "her", "them", "we", "i", "you"}
ADJS = {"hungry", "little", "small", "big", "brown", "fast", "lazy", "happy", "quick",
        "old", "young", "grey", "gray", "black", "white", "red", "wet", "green"}
ADVS = {"quickly", "slowly", "happily", "then", "always", "often", "gently"}
# verb surface form -> (canonical relation stem, morphological form).
# form in {base, 3sg, gerund, past, participle, past_or_participle}. 'live' stays provisional -> lives_in via 'in'.
VERB_LEX = {
    "eat": ("eats", "base"), "eats": ("eats", "3sg"), "eating": ("eats", "gerund"),
    "ate": ("eats", "past"), "eaten": ("eats", "participle"),
    "chase": ("chases", "base"), "chases": ("chases", "3sg"), "chasing": ("chases", "gerund"),
    "chased": ("chases", "past_or_participle"),
    "live": ("live", "base"), "lives": ("live", "3sg"), "living": ("live", "gerund"),
    "lived": ("live", "past_or_participle"),
}
NOUNS = set(ENTITIES)


def _noun_lemma(w):
    """productive singular morphology: birds->bird, seeds->seed, foxes->fox. Glass-box, no plural lexicon."""
    if w in NOUNS:
        return w
    if len(w) > 3 and w.endswith("es") and w[:-2] in NOUNS:
        return w[:-2]
    if len(w) > 2 and w.endswith("s") and w[:-1] in NOUNS:
        return w[:-1]
    return None


def _tag_token(w):
    """return (tag, lemma, form). tag in {DET,PRON,AUX,RELZR,CONJ,PREP,ADV,ADJ,VERB,NOUN,UNK}."""
    if w in DETS:
        return "DET", None, None
    if w in PRONS:
        return "PRON", w, None
    if w in BE_AUX:
        return "AUX", None, None
    if w in RELZRS:
        return "RELZR", w, None
    if w == "and":
        return "CONJ", "and", None
    if w in PREPS:
        return "PREP", w, None
    if w in ADVS:
        return "ADV", None, None
    if w in ADJS:
        return "ADJ", None, None
    if w in VERB_LEX:
        stem, form = VERB_LEX[w]
        return "VERB", stem, form
    nl = _noun_lemma(w)
    if nl is not None:
        return "NOUN", nl, None
    return "UNK", None, None


def _tokenize(sentence):
    s = sentence.lower().strip()
    for p in [".", "!", "?", ",", ";", ":", '"', "'"]:
        s = s.replace(p, " ")
    return [t for t in s.split() if t]


def _resolve_relation(verb_lemma, prep):
    if verb_lemma == "live":
        return "lives_in" if prep == "in" else None
    if verb_lemma in ("eats", "chases"):
        return verb_lemma
    return None


def _split_coord(noun_indices, T):
    """CALM-style coordination split over a noun region: if an 'and' joins the nouns, return ALL noun lemmas;
    else return just the head (nearest) noun lemma. T entry = (word, tag, lemma, form)."""
    if not noun_indices:
        return []
    lo, hi = noun_indices[0], noun_indices[-1]
    has_and = any(T[k][1] == "CONJ" and T[k][2] == "and" for k in range(lo, hi + 1))
    if has_and and len(noun_indices) >= 2:
        return [T[i][2] for i in noun_indices]
    return [T[noun_indices[-1]][2]]


def _validity_filter(triples):
    out = []
    for (s, r, o) in triples:
        if s == o:
            continue
        if r not in RELATIONS:
            continue
        if s not in ENTITIES or o not in ENTITIES:
            continue
        if (s, r, o) not in out:
            out.append((s, r, o))
    return out


# ---------------------------------------------------------------------------
# UPGRADED GLASS-BOX SYMBOLIC IE PARSER: passive + coordination-split + relative-clause + coreference-abstain.
# Returns (list_of_triples, rule_name, fail_reason). Empty list = abstain. Deterministic; provenance =
# (sentence, rule_name). NO LLM, NO neural dependency parser.
# ---------------------------------------------------------------------------
def ie_extract(sentence):
    toks = _tokenize(sentence)
    T = [(w,) + _tag_token(w) for w in toks]        # (word, tag, lemma, form)
    tags = [t[1] for t in T]
    lemmas = [t[2] for t in T]
    forms = [t[3] for t in T]
    n = len(T)
    verb_idx = [i for i in range(n) if tags[i] == "VERB"]
    if not verb_idx:
        return [], "NO_VERB", "no known verb (out-of-schema relation)"
    noun_idx = [i for i in range(n) if tags[i] == "NOUN"]
    pron_idx = [i for i in range(n) if tags[i] == "PRON"]
    relzr_idx = [i for i in range(n) if tags[i] == "RELZR"]

    v0 = verb_idx[0]
    subj_nouns_before_v0 = [i for i in noun_idx if i < v0]
    if not subj_nouns_before_v0:
        # COREFERENCE residual: a pronoun in subject position with no antecedent noun -> abstain (do not guess).
        if any(i < v0 for i in pron_idx):
            return [], "COREF_UNRESOLVED", "pronoun subject, no in-sentence antecedent (coreference gap)"
        return [], "NO_SUBJECT", "no noun left of verb"

    head_noun_i = subj_nouns_before_v0[0]           # sentence-initial matrix head (this register)

    # --- RELATIVE-CLAUSE clause typing: relativizer between head noun and first verb -> first verb is the RC
    # verb; matrix verb = next verb; matrix subject = head noun (not a noun inside the RC). ---
    rc = False
    matrix_vi = verb_idx[0]
    if relzr_idx and head_noun_i < relzr_idx[0] < verb_idx[0]:
        rc = True
        later = [vi for vi in verb_idx if vi > verb_idx[0]]
        if not later:
            return [], "RELCLAUSE_NO_MATRIX_VERB", "relative clause without a matrix verb"
        matrix_vi = later[0]

    verb_lemma = lemmas[matrix_vi]
    verb_form = forms[matrix_vi]

    # --- PASSIVE detection: matrix verb is a participle-capable form preceded (skipping ADV) by a be-AUX. ---
    k = matrix_vi - 1
    while k >= 0 and tags[k] == "ADV":
        k -= 1
    is_passive = (k >= 0 and tags[k] == "AUX" and verb_form in ("participle", "past_or_participle"))

    # --- SUBJECT(S) ---
    if rc:
        subjects = [lemmas[head_noun_i]]            # no subject coordination across an RC in this register
    else:
        subj_region = [i for i in noun_idx if i < matrix_vi]
        subjects = _split_coord(subj_region, T) or [lemmas[subj_region[-1]]]

    if is_passive:
        # GRAMMAR-driven role assignment: surface subject = PATIENT (object); 'by'-NP = AGENT (subject).
        by_i = None
        for j in range(matrix_vi + 1, n):
            if tags[j] == "PREP" and lemmas[j] == "by":
                by_i = j
                break
        if by_i is None:
            return [], "PASSIVE_NO_AGENT", "agentless passive (subject unrecoverable; coreference-like)"
        agent = None
        for j in range(by_i + 1, n):
            if tags[j] == "NOUN":
                agent = lemmas[j]
                break
        if agent is None:
            return [], "PASSIVE_NO_AGENT_NOUN", "no agent noun after 'by'"
        relation = _resolve_relation(verb_lemma, None)
        if relation is None:
            return [], "PASSIVE_REL_UNRESOLVED", "passive verb not in relation schema (or needs a prep)"
        triples = [(agent, relation, patient) for patient in subjects]
        rule = "SVO_PASSIVE"
    else:
        # --- ACTIVE: relation (+ governing prep for 'live') and OBJECT(S) with object-coordination split. ---
        prep = None
        obj_lemmas = []
        j = matrix_vi + 1
        while j < n:
            tg = tags[j]
            if tg in ("DET", "ADJ", "ADV", "AUX"):
                j += 1
                continue
            if tg == "PREP" and prep is None and not obj_lemmas:
                prep = lemmas[j]
                j += 1
                continue
            if tg == "NOUN":
                obj_lemmas.append(lemmas[j])
                j += 1
                # object coordination: consume ('and' DET* ADJ* NOUN)*
                while j < n:
                    if tags[j] in ("DET", "ADJ"):
                        j += 1
                        continue
                    if tags[j] == "CONJ" and lemmas[j] == "and":
                        j += 1
                        while j < n and tags[j] in ("DET", "ADJ"):
                            j += 1
                        if j < n and tags[j] == "NOUN":
                            obj_lemmas.append(lemmas[j])
                            j += 1
                            continue
                        break
                    break
                break
            break
        relation = _resolve_relation(verb_lemma, prep)
        if relation is None:
            if verb_lemma == "live":
                return [], "LIVE_WITHOUT_IN", "live verb without a governing 'in'"
            return [], "UNKNOWN_VERB", "verb not in relation schema"
        if not obj_lemmas:
            return [], "NO_OBJECT", "no object noun after verb"
        triples = [(s, relation, o) for s in subjects for o in obj_lemmas]
        if len(subjects) > 1 or len(obj_lemmas) > 1:
            rule = "SVO_COORD"
        elif prep == "in" and relation == "lives_in":
            rule = "SVO_PREP"
        else:
            rule = "SVO_ACTIVE"

    valid = _validity_filter(triples)
    if not valid:
        return [], "NO_VALID_TRIPLE", "all candidate triples failed validity"
    return valid, rule, None


# ---------------------------------------------------------------------------
# BASELINE parser: FROZEN COPY of v1's positional-SVO logic (single triple), wrapped to return a list, used ONLY
# for the apples-to-apples before/after comparison on the SAME broadened corpus. NOT used in the read->grow loop.
# ---------------------------------------------------------------------------
_EAT_FORMS = {"eat", "eats", "eating", "ate", "eaten"}
_CHASE_FORMS = {"chase", "chases", "chasing", "chased"}
_LIVE_FORMS = {"live", "lives", "living", "lived"}
_DETS = DETS
_PREPS = PREPS
_AUXES = BE_AUX
_ADJS = ADJS
_ADVS = ADVS
_CONJS_V1 = {"and", "that", "which", "who"}


def _tag_token_v1(w):
    if w in _DETS:
        return "DET", None
    if w in _AUXES:
        return "AUX", None
    if w in _PREPS:
        return "PREP", w
    if w in _CONJS_V1:
        return "CONJ", w
    if w in _ADVS:
        return "ADV", None
    if w in _ADJS:
        return "ADJ", None
    if w in _EAT_FORMS:
        return "VERB", "eats"
    if w in _CHASE_FORMS:
        return "VERB", "chases"
    if w in _LIVE_FORMS:
        return "VERB", "live"
    nl = _noun_lemma(w)
    if nl is not None:
        return "NOUN", nl
    return "UNK", None


def ie_extract_baseline_positional(sentence):
    """v1's positional-SVO extractor (single triple), returned as a list for uniform analysis."""
    toks = _tokenize(sentence)
    tags = [(t,) + _tag_token_v1(t) for t in toks]
    vi = None
    for i, (w, tg, lm) in enumerate(tags):
        if tg == "VERB":
            vi = i
            break
    if vi is None:
        return [], "NO_VERB", "no known verb"
    verb_lemma = tags[vi][2]
    subj = None
    for jj in range(vi - 1, -1, -1):
        if tags[jj][1] == "NOUN":
            subj = tags[jj][2]
            break
    if subj is None:
        return [], "NO_SUBJECT", "no noun left of verb"
    prep = None
    obj = None
    j = vi + 1
    while j < len(tags):
        tg = tags[j][1]
        if tg in ("DET", "ADJ", "ADV", "AUX"):
            j += 1
            continue
        if tg == "PREP" and prep is None and obj is None:
            prep = tags[j][2]
            j += 1
            continue
        if tg == "NOUN":
            obj = tags[j][2]
            break
        break
    if verb_lemma == "live":
        if prep == "in":
            relation = "lives_in"
        else:
            return [], "LIVE_WITHOUT_IN", "live without 'in'"
    elif verb_lemma in ("eats", "chases"):
        relation = verb_lemma
    else:
        return [], "UNKNOWN_VERB", "verb not in schema"
    if obj is None:
        return [], "NO_OBJECT", "no object noun after verb"
    if subj == obj:
        return [], "SUBJ_EQ_OBJ", "subject == object"
    if relation not in RELATIONS or subj not in ENTITIES or obj not in ENTITIES:
        return [], "INVALID", "type/schema check failed"
    return [(subj, relation, obj)], "SVO_POSITIONAL", None


# ---------------------------------------------------------------------------
# REAL-PROSE CORPUS (v1's original 34 + 12 broadening rows). Each row: text, gts (tuple of GOLD triples -- a set
# for coordination), label (gate role), cls (structure class), role (foundation role), expect_parse, residual.
# residual in {None, "out_of_schema", "coreference"} marks the classical permanent gaps (correct to abstain).
# ---------------------------------------------------------------------------
def _row(text, gts, label, cls, role, expect_parse, residual=None):
    return {"text": text, "gts": tuple(gts), "label": label, "cls": cls, "role": role,
            "expect_parse": expect_parse, "residual": residual}


PROSE_CORPUS = [
    # -- foundational block: simple SVO (eats) -- bootstraps relation argument-type profiles --
    _row("The cat eats the fish.", [("cat", "eats", "fish")], "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("The dog eats the bread.", [("dog", "eats", "bread")], "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("A cow eats grass.", [("cow", "eats", "grass")], "TRUE_ACCEPT", "svo_no_determiner", "required", True),
    _row("The bird eats a seed.", [("bird", "eats", "seed")], "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("The frog eats the worm.", [("frog", "eats", "worm")], "TRUE_ACCEPT", "simple_svo", "required", True),
    # -- foundational block: SVO + preposition (lives_in) --
    _row("The cat lives in the barn.", [("cat", "lives_in", "barn")], "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The dog lives in a barn.", [("dog", "lives_in", "barn")], "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The bird lives in the nest.", [("bird", "lives_in", "nest")], "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The fish lives in the pond.", [("fish", "lives_in", "pond")], "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The frog lives in the pond.", [("frog", "lives_in", "pond")], "TRUE_ACCEPT", "svo_prep", "required", True),
    # -- foundational block: simple SVO (chases) --
    _row("The cat chases the bird.", [("cat", "chases", "bird")], "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("The dog chases the cat.", [("dog", "chases", "cat")], "TRUE_ACCEPT", "simple_svo", "required", True),
    _row("The bird chases the frog.", [("bird", "chases", "frog")], "TRUE_ACCEPT", "simple_svo", "required", True),
    # -- schema-checkable TRUE facts --
    _row("The cow lives in a field.", [("cow", "lives_in", "field")], "TRUE_ACCEPT", "svo_prep", "required", True),
    _row("The hungry frog eats a seed.", [("frog", "eats", "seed")], "TRUE_ACCEPT", "adjective_modifier", "required", True),
    _row("The cat is eating a worm.", [("cat", "eats", "worm")], "TRUE_ACCEPT", "present_continuous", "required", True),
    _row("The small dog eats an apple.", [("dog", "eats", "apple")], "TRUE_ACCEPT", "adjective_modifier", "required", True),
    # -- HARD-STRUCTURE probes (coverage-only; facts duplicate easy sentences OR are new type-valid facts) --
    _row("Birds eat seeds.", [("bird", "eats", "seed")], "TRUE_ACCEPT", "plural_no_determiner", "probe", True),
    _row("The cat quickly eats the fish.", [("cat", "eats", "fish")], "TRUE_ACCEPT", "adverb_modifier", "probe", True),
    # passive (v1 REVERSED these -> correct 0.00; v2 target): patient=surface subj, agent=by-NP.
    _row("The worm is eaten by the frog.", [("frog", "eats", "worm")], "TRUE_ACCEPT", "passive", "probe", True),
    _row("The seed is eaten by the bird.", [("bird", "eats", "seed")], "TRUE_ACCEPT", "passive", "probe", True),
    # coordination subject (v1 nearest-conjunct only -> correct 0.00; v2 target): one triple per conjunct.
    _row("The cat and the dog eat bread.", [("cat", "eats", "bread"), ("dog", "eats", "bread")],
         "TRUE_ACCEPT", "coordination_subject", "probe", True),
    _row("The dog and the cat chase the bird.", [("dog", "chases", "bird"), ("cat", "chases", "bird")],
         "TRUE_ACCEPT", "coordination_subject", "probe", True),
    # relative clause (v1 subordinate verb won -> correct 0.00; v2 target): matrix verb + head subject.
    _row("The cat that lives in the barn eats a fish.", [("cat", "eats", "fish")],
         "TRUE_ACCEPT", "relative_clause", "probe", True),
    _row("The frog that eats worms lives in the pond.", [("frog", "lives_in", "pond")],
         "TRUE_ACCEPT", "relative_clause", "probe", True),
    # out-of-schema (residual: relation not in schema -> correct to ABSTAIN).
    _row("The owl sleeps in the tree.", [("owl", "sleeps", "tree")], "TRUE_ACCEPT", "out_of_schema_relation",
         "probe", False, residual="out_of_schema"),
    _row("The mouse runs to the barn.", [("mouse", "runs", "barn")], "TRUE_ACCEPT", "out_of_schema_relation",
         "probe", False, residual="out_of_schema"),
    # -- FALSE injection (TYPE-VIOLATING; gate must reject) --
    _row("The cat eats the barn.", [("cat", "eats", "barn")], "FALSE_REJECT", "simple_svo", "false", True),
    _row("The bird lives in the worm.", [("bird", "lives_in", "worm")], "FALSE_REJECT", "svo_prep", "false", True),
    # -- OUT-OF-ORDER (provisional-hold-bootstrap): both concepts ungrounded on arrival -> HOLD --
    _row("The kitten chases the mouse.", [("kitten", "chases", "mouse")], "HOLD_THEN_ACCEPT", "simple_svo", "hold", True),
    # -- support arrives (grounds kitten + mouse) -> held fact releases --
    _row("The kitten eats a seed.", [("kitten", "eats", "seed")], "NOVEL", "simple_svo", "novel", True),
    _row("The mouse eats the grass.", [("mouse", "eats", "grass")], "NOVEL", "simple_svo", "novel", True),
    # -- NOVEL entity late (owl) slots into the known schema -> admit + queryable --
    _row("The owl eats a worm.", [("owl", "eats", "worm")], "NOVEL", "simple_svo", "novel", True),
    _row("The owl lives in the nest.", [("owl", "lives_in", "nest")], "NOVEL", "svo_prep", "novel", True),
    # ===================== v2 BROADENING (more of each hard structure + coreference residual) =====================
    # more passive (n_passive -> 5): chase-passive + eat-passive.
    _row("The bird is chased by the dog.", [("dog", "chases", "bird")], "TRUE_ACCEPT", "passive", "probe", True),
    _row("The cat is chased by the dog.", [("dog", "chases", "cat")], "TRUE_ACCEPT", "passive", "probe", True),
    _row("The bread is eaten by the dog.", [("dog", "eats", "bread")], "TRUE_ACCEPT", "passive", "probe", True),
    # object coordination (n_coordination_object -> 2): one triple per object conjunct.
    _row("The bird eats seeds and worms.", [("bird", "eats", "seed"), ("bird", "eats", "worm")],
         "TRUE_ACCEPT", "coordination_object", "probe", True),
    _row("The cat eats fish and bread.", [("cat", "eats", "fish"), ("cat", "eats", "bread")],
         "TRUE_ACCEPT", "coordination_object", "probe", True),
    # more subject coordination (n_coordination_subject -> 3).
    _row("The cow and the frog eat grass.", [("cow", "eats", "grass"), ("frog", "eats", "grass")],
         "TRUE_ACCEPT", "coordination_subject", "probe", True),
    # more relative clause (n_relative_clause -> 5).
    _row("The dog that chases the cat eats bread.", [("dog", "eats", "bread")],
         "TRUE_ACCEPT", "relative_clause", "probe", True),
    _row("The bird that lives in the nest eats a seed.", [("bird", "eats", "seed")],
         "TRUE_ACCEPT", "relative_clause", "probe", True),
    _row("The cow that eats grass lives in a field.", [("cow", "lives_in", "field")],
         "TRUE_ACCEPT", "relative_clause", "probe", True),
    # coreference residual (NEW class; parser MUST abstain -- no antecedent in-sentence). gold = intended fact.
    _row("It eats the worm.", [("bird", "eats", "worm")], "TRUE_ACCEPT", "coreference", "probe", False,
         residual="coreference"),
    _row("They chase the mouse.", [("dog", "chases", "mouse")], "TRUE_ACCEPT", "coreference", "probe", False,
         residual="coreference"),
    # more out-of-schema residual.
    _row("The dog sleeps in the barn.", [("dog", "sleeps", "barn")], "TRUE_ACCEPT", "out_of_schema_relation",
         "probe", False, residual="out_of_schema"),
]

# precision set = every GOLD triple from a non-false, non-residual row (these ARE facts that SHOULD be admitted;
# coordination adds new type-valid facts here so admitting them is NOT a precision hit).
SHOULD_ACCEPT_TRUE = set()
for _d in PROSE_CORPUS:
    if _d["role"] != "false" and _d["residual"] is None:
        SHOULD_ACCEPT_TRUE |= set(_d["gts"])
# recall denominator = the REQUIRED foundational facts only (required + novel + hold), as in v1.
REQUIRED_RECALL_SET = set()
for _d in PROSE_CORPUS:
    if _d["role"] in ("required", "novel", "hold"):
        REQUIRED_RECALL_SET |= set(_d["gts"])
SHOULD_REJECT = set()
for _d in PROSE_CORPUS:
    if _d["role"] == "false":
        SHOULD_REJECT |= set(_d["gts"])

TARGET_CLASSES = {"passive", "coordination_subject", "coordination_object", "relative_clause"}
GUARD_CLASSES = {"simple_svo", "svo_prep", "svo_no_determiner", "adjective_modifier",
                 "present_continuous", "plural_no_determiner", "adverb_modifier"}


# ---------------------------------------------------------------------------
# METRIC (a): pure PARSER analysis (seed/lexicon-independent). Coverage + precision + per-class + residual.
# Parameterized by extractor so BASELINE and UPGRADED run on the SAME corpus (apples-to-apples).
# ---------------------------------------------------------------------------
def analyze_parser(extractor):
    per_class = defaultdict(lambda: {"n": 0, "covered": 0, "correct": 0})
    rows = []
    n_emitted = 0
    n_emitted_correct = 0
    for d in PROSE_CORPUS:
        triples, rule, freason = extractor(d["text"])
        emitted = set(triples)
        gold = set(d["gts"])
        covered = len(emitted) > 0
        correct = (emitted == gold)                       # sentence-level EXACT set match
        n_emitted += len(emitted)
        n_emitted_correct += len(emitted & gold)          # triple-level precision numerator
        c = d["cls"]
        per_class[c]["n"] += 1
        per_class[c]["covered"] += int(covered)
        per_class[c]["correct"] += int(correct)
        rows.append({"text": d["text"], "gold": sorted(list(t) for t in gold),
                     "extracted": sorted(list(t) for t in emitted), "rule": rule, "fail_reason": freason,
                     "cls": c, "residual": d["residual"], "covered": covered, "correct": correct})
    n = len(PROSE_CORPUS)
    coverage = sum(r["covered"] for r in rows) / float(n)
    precision = (n_emitted_correct / float(n_emitted)) if n_emitted else 0.0
    correct_rate = sum(r["correct"] for r in rows) / float(n)
    per_class_out = {}
    for c, v in per_class.items():
        per_class_out[c] = {"n": v["n"], "coverage": v["covered"] / float(v["n"]),
                            "correct_rate": v["correct"] / float(v["n"])}
    misfire = [{"text": r["text"], "gold": r["gold"], "got": r["extracted"], "rule": r["rule"], "cls": r["cls"]}
               for r in rows if r["covered"] and not r["correct"]]
    abstain = [{"text": r["text"], "gold": r["gold"], "fail_reason": r["fail_reason"], "cls": r["cls"],
                "residual": r["residual"]} for r in rows if not r["covered"]]
    residual_out_of_schema = sum(1 for d in PROSE_CORPUS if d["residual"] == "out_of_schema")
    residual_coreference = sum(1 for d in PROSE_CORPUS if d["residual"] == "coreference")
    return {
        "parser_coverage": coverage,
        "parser_precision": precision,
        "parser_correct_rate": correct_rate,
        "n_sentences": n,
        "n_emitted_triples": n_emitted,
        "per_class": per_class_out,
        "residual_out_of_schema_n": residual_out_of_schema,
        "residual_coreference_n": residual_coreference,
        "misfire_examples": misfire,
        "abstain_examples": abstain,
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# ONE end-to-end read->grow loop, one seed + one arm, with the UPGRADED glass-box IE parse (list-aware).
# ---------------------------------------------------------------------------
def run_loop(seed, use_gate, lexicon_kind="learned"):
    rng = np.random.default_rng(seed)
    scene_rng = np.random.default_rng(seed * 7 + 1)
    foundation = build_typed_foundation()
    cid_idx = foundation["cid_idx"]
    n_concept = len(foundation["concept_ids"])
    C = _svo_make_phasors(rng, n_concept, N_DIM)
    roles = _svo_make_phasors(rng, 3, N_DIM)
    inv = {v: k for k, v in cid_idx.items()}

    if lexicon_kind == "random":
        top_map = {w: foundation["concept_ids"][rng.integers(n_concept)] for w in foundation["words"]}
        mapping_acc = float(np.mean([top_map[w] == foundation["true_map"][w] for w in foundation["words"]]))
    elif lexicon_kind == "oracle":
        top_map = dict(foundation["true_map"])
        mapping_acc = 1.0
    else:
        train = build_lexicon_train(rng, foundation, n_per_word_min=14)
        assoc, _ = _learn_lexicon(train, foundation, scene_rng, role_gating=True, soft_me=True, fast_map=True,
                                  n_dist_noun=2, n_dist_verb=2, p_drop=0.05, p_syst=0.0)
        top_map = _lexicon_top(assoc, foundation)
        tm = foundation["true_map"]
        mapping_acc = float(np.mean([top_map.get(w) == tm[w] for w in foundation["words"]]))

    store = FoundationStore(C, roles, cid_idx)
    n_extract_ok = 0
    n_sent = len(PROSE_CORPUS)
    per_sentence = []

    for d in PROSE_CORPUS:
        text, gold_set, label, role = d["text"], set(d["gts"]), d["label"], d["role"]
        triples, rule, freason = ie_extract(text)
        if not triples:
            per_sentence.append({"text": text, "gold": sorted(gold_set), "extracted": None, "rule": rule,
                                 "fail_reason": freason, "label": label, "role": role, "residual": d["residual"],
                                 "extract_ok": False, "gate": "IE_NO_TRIPLE"})
            continue
        decoded_set = set()
        gate_log = []
        stage_fail = None
        for parsed in triples:
            try:
                learned_concepts = tuple(top_map.get(w) for w in parsed)
                filler_idx = tuple(cid_idx[c] if c in cid_idx else 0 for c in learned_concepts)
                M = _encode_meaning(filler_idx, C, roles)
                dec_idx = _decode_meaning(M, C, roles, 3)
                extracted = tuple(inv[i] for i in dec_idx)
            except Exception as ex:                       # attributable interface failure, never silent
                stage_fail = repr(ex)
                break
            decoded_set.add(extracted)
            cand = extracted
            well_formed = (cand[1] in RELATIONS and cand[0] != cand[2]
                           and cand[0] in ENTITIES and cand[2] in ENTITIES)
            if not well_formed:
                gate_log.append(["SKIP_MALFORMED", list(cand)])
                continue
            if use_gate:
                dec, info = store.gate(cand)
                store.decisions.append({"stage": "read", **info, "decision": dec})
                if dec == "ACCEPT":
                    store.commit(cand)
                elif dec == "HOLD":
                    store.held.append([cand, 0])
                store.reeval_holds()
                gate_log.append([dec, list(cand)])
            else:
                store.commit(cand)
                gate_log.append(["ACCEPT_NOGATE", list(cand)])
        if stage_fail is not None:
            per_sentence.append({"text": text, "gold": sorted(gold_set), "stage_fail": stage_fail,
                                 "label": label, "role": role, "extract_ok": False})
            continue
        extract_ok = (decoded_set == gold_set)
        if extract_ok:
            n_extract_ok += 1
        per_sentence.append({"text": text, "gold": sorted(gold_set),
                             "extracted": sorted(list(t) for t in decoded_set), "rule": rule, "label": label,
                             "role": role, "residual": d["residual"], "extract_ok": extract_ok, "gate": gate_log})
    if use_gate:
        store.reeval_holds()

    endtoend_correct_rate = n_extract_ok / float(n_sent)

    accepted = store.accepted
    n_false_in_store = len(accepted & SHOULD_REJECT)
    true_in_store = accepted & SHOULD_ACCEPT_TRUE
    precision = (len(true_in_store) / float(len(accepted))) if accepted else 0.0
    true_recall = len(accepted & REQUIRED_RECALL_SET) / float(len(REQUIRED_RECALL_SET))
    accept_false_rate = (n_false_in_store / float(len(SHOULD_REJECT))) if SHOULD_REJECT else 0.0

    true_extracted = [r for r in per_sentence
                      if r.get("extract_ok") and r.get("role") in ("required", "novel", "hold")]
    true_accepted = [r for r in true_extracted if set(map(tuple, r["extracted"])) <= accepted]
    accept_true_rate = (len(true_accepted) / float(len(true_extracted))) if true_extracted else 0.0

    obj_sets = defaultdict(set)
    for (s, r, o) in accepted:
        if (s, r, o) in SHOULD_ACCEPT_TRUE:
            obj_sets[(s, r)].add(o)
    q_total = 0
    q_ok = 0
    for (s, r), objs in sorted(obj_sets.items()):
        got = store.query(s, r)
        q_total += 1
        if got in objs:
            q_ok += 1
    query_acc = (q_ok / float(q_total)) if q_total else 0.0

    novel_owl_ok = ("owl", "eats", "worm") in accepted and store.query("owl", "eats") == "worm"
    novel_owl_place_ok = ("owl", "lives_in", "nest") in accepted
    hold_release_ok = ("kitten", "chases", "mouse") in accepted
    kitten_query_ok = store.query("kitten", "eats") in obj_sets.get(("kitten", "eats"), {"seed"})

    rt_total = 0
    rt_ok = 0
    for (s, r, o) in sorted(true_in_store):
        rt_total += 1
        if store.query(s, r) in obj_sets.get((s, r), {o}):
            rt_ok += 1
    store_roundtrip_acc = (rt_ok / float(rt_total)) if rt_total else 0.0

    return {
        "seed": seed, "use_gate": use_gate, "lexicon_kind": lexicon_kind,
        "mapping_acc": mapping_acc,
        "endtoend_correct_rate": endtoend_correct_rate,
        "n_sentences": n_sent,
        "n_accepted": len(accepted),
        "foundation_precision": precision,
        "true_recall": true_recall,
        "accept_false_rate": accept_false_rate,
        "n_false_in_store": n_false_in_store,
        "accept_true_rate": accept_true_rate,
        "query_acc": query_acc,
        "store_roundtrip_acc": store_roundtrip_acc,
        "novel_owl_ok": bool(novel_owl_ok),
        "novel_owl_place_ok": bool(novel_owl_place_ok),
        "hold_release_ok": bool(hold_release_ok),
        "kitten_query_ok": bool(kitten_query_ok),
        "accepted_hash": store.accepted_hash(),
        "accepted_sorted": sorted(accepted),
    }


def avg_arm(seeds, use_gate, lexicon_kind="learned"):
    runs = [run_loop(s, use_gate, lexicon_kind) for s in seeds]
    keys_mean = ["mapping_acc", "endtoend_correct_rate", "foundation_precision", "true_recall",
                 "accept_false_rate", "accept_true_rate", "query_acc", "store_roundtrip_acc",
                 "n_accepted", "n_false_in_store"]
    keys_all = ["novel_owl_ok", "novel_owl_place_ok", "hold_release_ok", "kitten_query_ok"]
    out = {k: float(np.mean([r[k] for r in runs])) for k in keys_mean}
    out.update({k: bool(all(r[k] for r in runs)) for k in keys_all})
    out["per_seed"] = runs
    return out


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands per pre-reg).
# ---------------------------------------------------------------------------
def _class_rate(parser, cls):
    v = parser["per_class"].get(cls)
    return v["correct_rate"] if v else None


def compute_verdict(parser_up, parser_base, full, nogate, oracle, random_ctrl):
    cov = parser_up["parser_coverage"]
    prec = parser_up["parser_precision"]
    cr = parser_up["parser_correct_rate"]
    base_cr = parser_base["parser_correct_rate"]

    target_rates = {c: _class_rate(parser_up, c) for c in TARGET_CLASSES if _class_rate(parser_up, c) is not None}
    guard_rates = {c: _class_rate(parser_up, c) for c in GUARD_CLASSES if _class_rate(parser_up, c) is not None}
    targets_ok = all(v >= 0.80 for v in target_rates.values()) and len(target_rates) > 0
    guards_ok = all(v >= 1.0 for v in guard_rates.values()) and len(guard_rates) > 0
    any_target_zero = any(v == 0.0 for v in target_rates.values())
    any_guard_broken = any(v < 1.0 for v in guard_rates.values())

    hp = (
        cov >= 0.60 and prec >= 0.80 and cr >= 0.80 and
        targets_ok and guards_ok and
        full["foundation_precision"] >= 0.90 and
        full["accept_false_rate"] == 0.0 and
        full["true_recall"] >= 0.70 and
        full["query_acc"] >= 0.80 and
        (full["foundation_precision"] - nogate["foundation_precision"]) >= 0.05 and
        full["novel_owl_ok"] and full["hold_release_ok"]
    )
    hf = (
        cr <= base_cr + 0.01 or
        any_target_zero or
        any_guard_broken or
        prec < 0.40 or
        full["foundation_precision"] < 0.60 or
        full["accept_false_rate"] == 1.0 or
        full["query_acc"] < 0.40
    )
    if hp:
        tier = "HARD_PASS"
    elif hf:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    localize = []
    for c in sorted(TARGET_CLASSES):
        r = _class_rate(parser_up, c)
        if r is not None and r < 0.80:
            localize.append("target class %s not lifted (correct_rate=%.2f)" % (c, r))
    for c in sorted(GUARD_CLASSES):
        r = _class_rate(parser_up, c)
        if r is not None and r < 1.0:
            localize.append("guard class %s BROKEN by upgrade (correct_rate=%.2f)" % (c, r))
    if cr <= base_cr + 0.01:
        localize.append("no lift over baseline (%.3f vs baseline %.3f)" % (cr, base_cr))
    if full["accept_false_rate"] > 0.0:
        localize.append("triple->gate (gate admitted a type-violating false fact)")
    if full["foundation_precision"] < 0.90:
        localize.append("triple->gate (parser misfire passed the gate; precision degraded)")
    weakest = localize if localize else ["none (targets lifted, guards intact, foundation clean)"]

    tstr = " ".join("%s=%.2f" % (c, target_rates[c]) for c in sorted(target_rates))
    msg = (f"{tier} | PARSER UPGRADED coverage={cov:.3f} precision={prec:.3f} correct_rate={cr:.3f} "
           f"(baseline {base_cr:.3f}; delta={cr - base_cr:+.3f}) | targets[{tstr}] | "
           f"residual: out_of_schema={parser_up['residual_out_of_schema_n']} coref={parser_up['residual_coreference_n']} | "
           f"endtoend FULL={full['endtoend_correct_rate']:.3f} (oracle={oracle['endtoend_correct_rate']:.3f} "
           f"random={random_ctrl['endtoend_correct_rate']:.3f}) | foundation_prec FULL={full['foundation_precision']:.3f} "
           f"vs NO_GATE={nogate['foundation_precision']:.3f} | recall={full['true_recall']:.3f} "
           f"accept_false={full['accept_false_rate']:.3f} query={full['query_acc']:.3f} | "
           f"novel_owl={full['novel_owl_ok']} hold_release={full['hold_release_ok']} | weakest={weakest}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_grow_foundation_realprose_glassbox_ie_v2",
           "smoke": "exp_read_grow_foundation_realprose_glassbox_ie_v2_smoke",
           "self_test": "exp_read_grow_foundation_realprose_glassbox_ie_v2_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")           # atomic per META_RULE_AH


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the FIX FIRES (passive/coord/rel now correct), the BASELINE
# still FAILS them (lift is real), and the residual (coref/out-of-schema) still ABSTAINS (correct_rate < 1.0).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (ie_extract + imported learn_lexicon + SVO encode/decode + "
          "FoundationStore)...", flush=True)
    exercised = set()
    exercised.add("ie_extract")
    # (1) simple cases STILL work (guards not broken).
    assert set(ie_extract("The cat eats the fish.")[0]) == {("cat", "eats", "fish")}, "simple SVO broke"
    assert set(ie_extract("The bird lives in the nest.")[0]) == {("bird", "lives_in", "nest")}, "SVO+prep broke"
    assert set(ie_extract("The cat is eating a worm.")[0]) == {("cat", "eats", "worm")}, "present-continuous broke"
    assert set(ie_extract("Birds eat seeds.")[0]) == {("bird", "eats", "seed")}, "plural morphology broke"
    # (2) PASSIVE fixed: correct roles, NOT reversed.
    assert set(ie_extract("The worm is eaten by the frog.")[0]) == {("frog", "eats", "worm")}, "passive not fixed"
    assert set(ie_extract("The bird is chased by the dog.")[0]) == {("dog", "chases", "bird")}, "chase-passive not fixed"
    # (3) COORDINATION fixed: one triple per conjunct (subject AND object).
    assert set(ie_extract("The cat and the dog eat bread.")[0]) == {("cat", "eats", "bread"), ("dog", "eats", "bread")}, \
        "subject coordination not split"
    assert set(ie_extract("The bird eats seeds and worms.")[0]) == {("bird", "eats", "seed"), ("bird", "eats", "worm")}, \
        "object coordination not split"
    # (4) RELATIVE CLAUSE fixed: matrix verb + head subject.
    assert set(ie_extract("The cat that lives in the barn eats a fish.")[0]) == {("cat", "eats", "fish")}, "RC not attached"
    assert set(ie_extract("The frog that eats worms lives in the pond.")[0]) == {("frog", "lives_in", "pond")}, "RC(2) not attached"
    # (5) residual ABSTAINS (correct not to hallucinate): coreference + out-of-schema.
    assert ie_extract("It eats the worm.")[0] == [], "coreference should abstain, not guess"
    assert ie_extract("The owl sleeps in the tree.")[0] == [], "out-of-schema verb should abstain"
    # (6) the BASELINE parser still FAILS the hard cases (proves the lift is real, not a corpus artifact).
    exercised.add("ie_extract_baseline_positional")
    assert set(ie_extract_baseline_positional("The worm is eaten by the frog.")[0]) != {("frog", "eats", "worm")}, \
        "baseline should MISFIRE on passive (else lift is not attributable to the upgrade)"
    assert set(ie_extract_baseline_positional("The cat and the dog eat bread.")[0]) != \
        {("cat", "eats", "bread"), ("dog", "eats", "bread")}, "baseline should miss coordination"
    assert set(ie_extract_baseline_positional("The cat that lives in the barn eats a fish.")[0]) != {("cat", "eats", "fish")}, \
        "baseline should mis-attach the relative clause"
    # (7) parser analysis: upgraded lifts over baseline; both < 1.0 (residual remains -> not a stub).
    pa_up = analyze_parser(ie_extract)
    pa_base = analyze_parser(ie_extract_baseline_positional)
    assert pa_up["parser_precision"] >= 0.80, f"upgraded precision too low: {pa_up['parser_precision']}"
    assert pa_up["parser_correct_rate"] > pa_base["parser_correct_rate"] + 0.05, \
        f"no material lift: up={pa_up['parser_correct_rate']} base={pa_base['parser_correct_rate']}"
    assert pa_up["parser_correct_rate"] < 1.0, "cannot be perfect (residual coref+out-of-schema must remain)"
    for c in TARGET_CLASSES:
        r = _class_rate(pa_up, c)
        if r is not None:
            assert r >= 0.80, f"target class {c} not lifted: {r}"
        rb = _class_rate(pa_base, c)
        if rb is not None:
            assert rb == 0.0, f"baseline unexpectedly handles {c}: {rb} (lift not attributable)"
    # (8) REAL lexicon learner (imported verbatim).
    foundation = build_typed_foundation()
    train = build_lexicon_train(np.random.default_rng(5), foundation, n_per_word_min=10)
    assoc, _ = _learn_lexicon(train, foundation, np.random.default_rng(9), role_gating=True, soft_me=True,
                              fast_map=True, n_dist_noun=2, n_dist_verb=2, p_drop=0.05, p_syst=0.0)
    top = _lexicon_top(assoc, foundation); exercised.add("learn_lexicon")
    macc = float(np.mean([top.get(w) == foundation["true_map"][w] for w in foundation["words"]]))
    assert macc >= 0.5, f"lexicon learner degenerate: mapping_acc={macc}"
    # (9) REAL end-to-end single seed (FULL vs NO_GATE) + gate/store discriminator FIRING.
    full = run_loop(11, use_gate=True, lexicon_kind="learned"); exercised.add("run_loop")
    nogate = run_loop(11, use_gate=False, lexicon_kind="learned")
    assert full["endtoend_correct_rate"] > 0.0, "end-to-end extraction cratered"
    assert full["accepted_hash"] != nogate["accepted_hash"], \
        "META_RULE_AF: FULL and NO_GATE store bit-identical (gate not firing on prose noise)"
    assert full["n_false_in_store"] <= nogate["n_false_in_store"], "gate did not reduce false facts"
    assert nogate["n_false_in_store"] >= 1, "smoke-vacuous: NO_GATE did not admit the false fact"
    for ep in ["ie_extract", "ie_extract_baseline_positional", "learn_lexicon", "run_loop"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"
    print(f"[self_test] PASS | UPGRADED coverage={pa_up['parser_coverage']:.3f} precision={pa_up['parser_precision']:.3f} "
          f"correct_rate={pa_up['parser_correct_rate']:.3f} (BASELINE correct_rate={pa_base['parser_correct_rate']:.3f}) | "
          f"lexicon_macc={macc:.3f} | endtoend={full['endtoend_correct_rate']:.3f} full_false={full['n_false_in_store']} "
          f"nogate_false={nogate['n_false_in_store']}", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    seeds = [11, 23] if run_mode == "smoke" else [11, 23, 37, 41, 53]
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * 4
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[realprose_ie_v2] run_mode={run_mode} seeds={seeds} corpus={len(PROSE_CORPUS)} real sentences", flush=True)

    parser_up = analyze_parser(ie_extract)
    parser_base = analyze_parser(ie_extract_baseline_positional)
    print(f"[realprose_ie_v2] BASELINE  coverage={parser_base['parser_coverage']:.3f} "
          f"precision={parser_base['parser_precision']:.3f} correct_rate={parser_base['parser_correct_rate']:.3f}", flush=True)
    print(f"[realprose_ie_v2] UPGRADED  coverage={parser_up['parser_coverage']:.3f} "
          f"precision={parser_up['parser_precision']:.3f} correct_rate={parser_up['parser_correct_rate']:.3f} "
          f"(delta={parser_up['parser_correct_rate'] - parser_base['parser_correct_rate']:+.3f})", flush=True)
    print("[realprose_ie_v2] per-class correct-rate  BASELINE -> UPGRADED:", flush=True)
    for c in sorted(set(parser_up["per_class"]) | set(parser_base["per_class"])):
        vb = parser_base["per_class"].get(c, {"correct_rate": 0.0, "n": 0})
        vu = parser_up["per_class"].get(c, {"correct_rate": 0.0, "n": 0})
        tag = " [TARGET]" if c in TARGET_CLASSES else (" [residual]" if c in ("out_of_schema_relation", "coreference") else "")
        print(f"[realprose_ie_v2]   {c:24s} n={vu['n']:2d}  {vb['correct_rate']:.2f} -> {vu['correct_rate']:.2f}{tag}", flush=True)

    full = avg_arm(seeds, use_gate=True, lexicon_kind="learned")
    nogate = avg_arm(seeds, use_gate=False, lexicon_kind="learned")
    oracle = avg_arm(seeds, use_gate=True, lexicon_kind="oracle")
    random_ctrl = avg_arm(seeds, use_gate=True, lexicon_kind="random")
    print(f"[realprose_ie_v2] FULL endtoend={full['endtoend_correct_rate']:.3f} foundation_prec={full['foundation_precision']:.3f} "
          f"recall={full['true_recall']:.3f} query={full['query_acc']:.3f} false_in_store={full['n_false_in_store']:.2f}", flush=True)
    print(f"[realprose_ie_v2] NO_GATE foundation_prec={nogate['foundation_precision']:.3f} false_in_store={nogate['n_false_in_store']:.2f} "
          f"| ORACLE endtoend={oracle['endtoend_correct_rate']:.3f} RANDOM endtoend={random_ctrl['endtoend_correct_rate']:.3f}", flush=True)

    tier, msg, weakest = compute_verdict(parser_up, parser_base, full, nogate, oracle, random_ctrl)
    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in a.items() if k != "per_seed"}

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_read_sentences": len(PROSE_CORPUS),
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        # METRIC (a) -- BASELINE vs UPGRADED glass-box IE parser on the SAME broadened real-prose corpus.
        "metric_a_baseline_correct_rate": parser_base["parser_correct_rate"],
        "metric_a_baseline_coverage": parser_base["parser_coverage"],
        "metric_a_baseline_precision": parser_base["parser_precision"],
        "metric_a_upgraded_correct_rate": parser_up["parser_correct_rate"],
        "metric_a_upgraded_coverage": parser_up["parser_coverage"],
        "metric_a_upgraded_precision": parser_up["parser_precision"],
        "metric_a_correct_rate_lift": parser_up["parser_correct_rate"] - parser_base["parser_correct_rate"],
        "metric_a_v1_original34_correct_rate": 0.765,   # MEASURED@data/exp_read_grow_foundation_realprose_glassbox_ie_v1/metrics.json
        "parser_per_class_baseline": parser_base["per_class"],
        "parser_per_class_upgraded": parser_up["per_class"],
        "residual_out_of_schema_n": parser_up["residual_out_of_schema_n"],
        "residual_coreference_n": parser_up["residual_coreference_n"],
        "parser_failure_modes_upgraded": {"misfire": parser_up["misfire_examples"], "abstain": parser_up["abstain_examples"]},
        "parser_rows_upgraded": parser_up["rows"],
        # METRIC (b/c/d) -- downstream foundation on real-prose-derived triples (UPGRADED parser).
        "metric_b_foundation_precision": full["foundation_precision"],
        "metric_b_true_recall": full["true_recall"],
        "metric_c_query_acc": full["query_acc"],
        "metric_d_accept_true_rate": full["accept_true_rate"],
        "metric_d_accept_false_rate": full["accept_false_rate"],
        "endtoend_correct_rate_learned": full["endtoend_correct_rate"],
        "endtoend_correct_rate_oracle_lex": oracle["endtoend_correct_rate"],
        "endtoend_correct_rate_random_lex": random_ctrl["endtoend_correct_rate"],
        "gate_vs_accept_all_precision_gain": full["foundation_precision"] - nogate["foundation_precision"],
        "arms": {
            "FULL_LOOP": strip(full),
            "NO_GATE": strip(nogate),
            "ORACLE_LEXICON": strip(oracle),
            "RANDOM_LEXICON": strip(random_ctrl),
        },
        "full_loop_per_seed": full["per_seed"],
        "prereg": {
            "hard_pass": "coverage>=0.60 & precision>=0.80 & correct_rate>=0.80 & every target-class>=0.80 & "
                         "every guard-class==1.0 & FULL foundation_prec>=0.90 & accept_false_rate==0 & "
                         "FULL recall>=0.70 & query>=0.80 & (FULL-NOGATE prec)>=0.05 & novel_owl & hold_release",
            "hard_fail": "correct_rate<=baseline+0.01 | any target-class==0 | any guard-class<1.0 | precision<0.40 | "
                         "FULL foundation_prec<0.60 | accept_false_rate==1.0 | query<0.40",
            "middle": "otherwise (some hard structures fixed, some not; report per-class + residual toward ceiling)",
            "target_classes": sorted(TARGET_CLASSES),
            "guard_classes": sorted(GUARD_CLASSES),
            "residual_classes": ["out_of_schema_relation (closed schema abstains)", "coreference (no antecedent)"],
            "compute_architecture": "sequential-CPU (genuine sequential dependency: foundation grows fact-by-fact)",
            "storage_strategy": "sharded (one VSA vector per accepted fact)",
            "parser_class": "fully-symbolic glass-box rule-based IE (NO LLM, NO neural dependency parser); "
                            "adds passive role-assignment + CALM coordination-split + ClausIE relative-clause typing",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract", "ie_extract_baseline_positional", "learn_lexicon", "run_loop"],
            "crlb_n/a": "no quantitative noise floor; extraction gated by rule-misfire + lexicon-map error, not phasor noise",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[realprose_ie_v2] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[realprose_ie_v2] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
