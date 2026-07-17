"""exp_read_grow_oov_pos_extension_v1 -- the CHEAP DECISIVE TEST from
notes/research_open_text_glassbox_ie_reading_frontier_curriculum_2026-07-16.md section (b)/(c) Prediction 1:
does adding a CLASSICAL statistical POS tagger (for OOV nouns the hand-lexicon can't tag) feeding UNTYPED
noun slots into the EXISTING closed-schema glass-box grammar (exp_read_grow_foundation_realprose_glassbox_ie_v2)
recover substantial open-text COVERAGE while PRESERVING high precision on the newly-covered sentences?

NEW STANDALONE CELL (does not edit exp_read_grow_foundation_realprose_glassbox_ie_v2.py OR
exp_read_grow_openvocab_fastmap_v1.py -- the latter is concurrently edited by a sibling relation-grounding
cell; this cell only IMPORTS pure helper functions from v2, verbatim, unmodified).

ARMS (per the note's cheap-decisive-test spec, section (b)):
  CURRENT       -- the existing closed-schema symbolic parser, UNCHANGED (`ie_extract`, imported verbatim
                   from exp_read_grow_foundation_realprose_glassbox_ie_v2). A noun not in the hand lexicon
                   (ENTITIES) is tagged UNK and cannot fill a role slot -- expected: abstain whenever a
                   REQUIRED role-slot noun is OOV.
  POS_EXTENDED  -- IDENTICAL grammar rules (a faithful re-implementation of v2's `ie_extract` structural
                   logic, verified bit-for-bit PARITY against the import at self-test time -- see
                   `_extract_core` vs `ie_extract`), but any token the closed lexicon tags UNK gets a SECOND
                   chance: a classical POS tagger (NLTK's averaged-perceptron tagger, context-aware over the
                   full cased sentence -- a structured-perceptron classical ML tagger, NO neural net) tags it
                   NN/NNS/NNP/NNPS, OR a suffix/word-shape morphology check fires (productive plural -s,
                   common nominalizing suffixes, capitalization) -- either signal is sufficient to accept
                   "this fills a NOUN slot," WITHOUT knowing what the noun means (no lexicon entry created,
                   no grounding, no fact-content asserted about the OOV word -- purely a syntactic-category
                   acceptance, per Fisher/Gleitman syntactic-bootstrapping, research note section 1 Rung 2).
                   The morphology fallback DEFERS to the tagger's own verb-family judgment (does not fire if
                   the tagger tags the token VB/VBD/VBG/VBN/VBP/VBZ) to avoid the "-s ending" heuristic
                   mis-promoting a 3rd-person verb to NOUN.

GLASS-BOX-LEGAL (verified, no LLM, no neural net anywhere in the import chain):
  NLTK's `pos_tag` with the `averaged_perceptron_tagger_eng` model is a classical, non-neural, inspectable
  structured-perceptron POS tagger (Collins 2002 averaged-perceptron lineage; ~96-97% PTB accuracy per the
  ACL Wiki POS-tagging SOTA tracker, CITED in the research note section 3) -- explicitly named LEGAL in the
  research note section 4 ("NLTK's built-in averaged-perceptron tagger and TnT-style HMM taggers"). `import
  nltk` pulls in NO torch/spacy/transformers/neural dependency (grep-confirmed at self-test, see
  `_grep_confirm_no_neural_imports` below -- reproduces the discipline the parent v2 cell used).

CORPUS (hand-authored, per contract -- "if you use a gold corpus... keep that separate from the self-graded
  extraction precision"; this cell does NOT use UD-EWT/GUM independent tagger-accuracy checking -- SCOPE
  DECISION, declared up front: NLTK's tagger accuracy is independently benchmarked in the cited literature
  (96-97% PTB, CITED@research note section 3), and downloading/parsing a CoNLL-U treebank is heavier than a
  "cheap decisive test" warrants; the self-test instead asserts hand-verified expected tags on a few of this
  cell's own OOV words as a lightweight sanity check, not a full independent benchmark):
  - OOV NOUNS: 10 animals / 8 foods / 8 places NOT in ENTITIES (the closed hand-lexicon) -- confirmed via a
    set-intersection self-test assertion (the vacuous-test guard: if these ever overlapped ENTITIES the
    "OOV-ness" claim would be false and the test meaningless).
  - 10 sentence-template CLASSES mirroring v2's own supported constructions (simple SVO, SVO_PREP for
    lives_in, adjective-modified, subject-coordination, passive, chase-SVO, bare-plural-no-determiner),
    instantiated with OOV nouns in EITHER subject, object, or BOTH slots -- every template is, BY
    CONSTRUCTION, one CURRENT fully abstains on (verified per-template at self-test: the required role-slot
    noun is OOV, so CURRENT has no NOUN token there at all).
  - HONEST SCOPE NOTE: all function words (determiners/preps/aux/relativizers/conjunctions), ALL VERBS, and
    all ADJECTIVES/ADVERBS in this corpus are drawn from the CLOSED lexicon (never OOV) -- this cell isolates
    the OOV-NOUN-coverage question specifically, exactly as the research note's arm design specifies
    ("holding the existing closed-schema grammar rules fixed... any unknown noun slot is now filled...").
    A harder, fully-open register (real OneStopEnglish/Simple-Wikipedia prose with OOV verbs/ambiguous
    function words too) would likely land in the corrected classical envelope (P:60-85%/R:30-55%, research
    note section (a)/3), not the near-ceiling precision this controlled corpus is expected to show. This is
    a DELIBERATE, DECLARED scope choice (cheap decisive test = isolate ONE variable), not an inflated claim.
  - COORDINATION HONEST FINDING (discovered during cell design, reported not hidden): a coordination sentence
    with ONE known conjunct + ONE OOV conjunct does NOT fully abstain under CURRENT -- the OOV conjunct is
    silently INVISIBLE to `noun_idx` (tagged UNK, never enters the coordination-detection logic), so CURRENT
    emits a single, CORRECT-BUT-INCOMPLETE triple for the known conjunct only (silently drops the OOV fact,
    no error signal). This is a genuine classical-parser behavior, not a bug in this cell -- the PRIMARY
    corpus therefore uses BOTH-conjuncts-OOV coordination (a clean full-abstain case); the mixed-conjunct
    case is reported SEPARATELY as `mixed_coord_diagnostic` (non-gating, an honest additional finding).
  - GUARD_SENTENCES (fully in-lexicon, no OOV) -- regression check: EXTENDED must not corrupt cases CURRENT
    already gets right (both arms must clear 100% coverage + 100% precision).
  - OUT_OF_SCHEMA_CONTROL (known nouns + an out-of-schema verb, e.g. "sleeps") -- MUST-FAIL discriminator:
    BOTH arms must abstain (the verb-schema gate is untouched by the noun extension; a promoted-to-NOUN
    mistag on the verb token itself, e.g. NLTK mistagging "sleeps" as NNS in this register -- an OBSERVED,
    reported tagger error -- still leaves the sentence with NO VERB token at all, so it correctly abstains).

METRICS (reported separately, per contract):
  (i)  sentence-level coverage (non-abstain rate), CURRENT vs POS_EXTENDED, over the full OOV-noun corpus.
  (ii) precision on the NEWLY-COVERED subset ONLY (sentences CURRENT fully abstains on AND POS_EXTENDED
       extracts >=1 triple) -- triple-level precision (fraction of EMITTED triples matching gold), POOLED
       across all seeds for statistical stability (per-seed breakdown also reported).
  Plus: guard-class regression check, out-of-schema must-fail control, mixed-coordination diagnostic,
  vacuous-test guard (CURRENT coverage on the primary corpus must be near 0 -- confirms genuine OOV-ness).

PRE-REG (envelope-fail-bands; bands are PRE-COMMITTED per the dispatching contract, matching the research
  note section (b) verbatim -- I do not loosen these to force a pass):
  HARD-PASS: coverage_gain_pp (POS_EXTENDED - CURRENT, over full corpus) >= 15.0 percentage points AND
             precision_newly_covered (pooled, triple-level) >= 0.90 AND guard_regression_ok AND
             oos_control_fired AND current_coverage_floor_ok (CURRENT coverage <= 0.05, vacuous-test guard).
  HARD-FAIL: coverage_gain_pp < 5.0 OR precision_newly_covered < 0.75.
  MIDDLE_BAND: otherwise (e.g. clears one bar but not the other, or no newly-covered sentences produced).
  HONEST FRAMING (per contract): a HARD-FAIL on precision would mean the closed-schema grammar's precision
  was silently leaning on the LEXICON itself as a disambiguation filter (not just a role-filler) -- report as
  a real finding, not hidden. A HARD-PASS on this controlled corpus does NOT claim the general open-text
  envelope (P:60-85%/R:30-55%) is beaten -- see HONEST SCOPE NOTE above.

Local numpy + nltk, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (pure syntactic parsing over a small
corpus; wall time trivial). No VSA store touched (pure parser-layer test, upstream of any grounding/FoundationStore
-- this cell does not construct KGStore/FoundationStore; real_code_path (F.1) is scoped to the PARSER
entrypoints: `ie_extract` (imported unmodified) + `nltk.pos_tag` (real external classical-ML call) +
`ie_extract_pos_extended` (this cell's own extension), all exercised for real at self-test, not a synthetic
branch. progress_logging = print_flush_true (not required at timeout_s < 1800, included anyway for parity).
Dispatch: COMPUTE-PROPORTIONALITY -- cheapest decisive method; runs INLINE/FOREGROUND locally (no GPU, no
remote SCP, no atomize), matching the parallel sibling cell's precedent (exp_read_grow_relation_identity_v1).
Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before this run.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; CURRENT vs POS_EXTENDED accepted-triple-set hash differs
#   on the primary OOV corpus by construction -- CURRENT emits nothing, EXTENDED emits triples).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor -- discriminator is discrete syntactic role-assignment + a classical
#   POS tagger's own (externally benchmarked, 96-97% PTB, CITED@research note sec 3) categorical accuracy,
#   not phasor decode noise. No VSA cleanup step in this cell at all.
# - baseline_in_band: N/A BY DESIGN for this cell's shape (declared, not a violation of META_RULE_AG) -- the
#   AG floor-gate exists to stop a mechanism from being unmeasurable because baseline is ALREADY saturated;
#   here the discriminator IS coverage RECOVERY FROM a deliberately-constructed near-zero CURRENT baseline
#   (every corpus sentence requires an OOV noun in a role slot CURRENT cannot fill) -- CURRENT-at-floor is
#   the REQUIRED vacuous-test guard (current_coverage_floor_ok), not a measurability failure.
# - discriminator survives scale: corpus is FIXED-size (hand-authored templates x random OOV-word draws).
#   Smoke uses the SAME template set + SAME n_per_template as FULL (Option A, discriminator-must-survive-
#   scale: smoke IS full-N, differing only in seed count) -- trivial wall time makes this free.
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test calls REAL `nltk.pos_tag` (external classical-ML tagger, not mocked) and
#   the REAL imported `ie_extract` (v2, unmodified) on tiny real sentences, and asserts PARITY between this
#   cell's `_extract_core` copy and the imported `ie_extract` (proves "identical grammar rules," not just
#   claims it).
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19]; random.Random(seed) (never hash()); sorted()
#   used for all set->list conversions in metrics; no list(set(...)) ordering dependence.
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics / CITED@research-note.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import re
import argparse
import time
import json
import random
import hashlib
import platform
import traceback
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_oov_pos_extension_v1"

# --- GENUINE REUSE of the existing closed-schema parser (imported verbatim, NOT edited, NOT reimplemented
# for the CURRENT arm) ---
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import (  # noqa: E402
    ADJS, ENTITIES, RELATIONS, ANIMALS, FOODS, PLACES,
    _tag_token, _tokenize, _resolve_relation, _split_coord, ie_extract,
)

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only; see glass-box-legal note above.

# ---------------------------------------------------------------------------
# OOV noun pools -- confirmed NOT in the closed hand-lexicon (ENTITIES). Common early-reader-register nouns,
# same register as the v2 corpus (animals / foods / places), deliberately OUTSIDE the closed set.
# ---------------------------------------------------------------------------
OOV_ANIMALS = ["rabbit", "duck", "goat", "squirrel", "hedgehog", "sparrow", "badger", "otter", "deer", "lamb"]
OOV_FOODS = ["leaf", "berry", "carrot", "acorn", "clover", "nut", "cricket", "moss"]
OOV_PLACES = ["meadow", "burrow", "hollow", "garden", "hedge", "riverbank", "thicket", "orchard"]

KNOWN_ANIMALS = list(ANIMALS)
KNOWN_FOODS = list(FOODS)
KNOWN_PLACES = list(PLACES)
KNOWN_ADJS = sorted(ADJS)

NOUN_SUFFIXES = ("tion", "sion", "ment", "ness", "ity", "ance", "ence", "ery", "ship", "hood", "dom", "age")
NLTK_NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS"}
NLTK_VERB_TAGS = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}


# ---------------------------------------------------------------------------
# POS-EXTENDED tagging: closed lexicon FIRST (unchanged rules), classical tagger + suffix/shape morphology
# ONLY for tokens the closed lexicon cannot place (tag == UNK).
# ---------------------------------------------------------------------------
def _morph_noun_shape(w_lower, w_orig):
    """suffix/word-shape morphology signal (glass-box, no lexicon lookup): capitalization, productive -s
    plural, common nominalizing suffixes. A co-signal alongside the classical tagger, per the research
    note's arm spec ("classical POS tagger + suffix/word-shape morphology check")."""
    if w_orig[:1].isalpha() and w_orig[:1].isupper():
        return True
    if len(w_lower) > 3 and w_lower.endswith("s") and not w_lower.endswith("ss"):
        return True
    for suf in NOUN_SUFFIXES:
        if len(w_lower) > len(suf) + 2 and w_lower.endswith(suf):
            return True
    return False


def _oov_lemma(w_lower):
    """productive singular normalization for OOV nouns (same style as v2's `_noun_lemma`, generalized since
    the word is not a member of a closed set to check membership against)."""
    if len(w_lower) > 3 and w_lower.endswith("es"):
        return w_lower[:-2]
    if len(w_lower) > 3 and w_lower.endswith("s") and not w_lower.endswith("ss"):
        return w_lower[:-1]
    return w_lower


def _tokenize_cased(sentence):
    """same punctuation-stripping/split logic as v2's `_tokenize`, but WITHOUT lowercasing -- feeds the
    classical tagger cased tokens (better fidelity) while the closed-lexicon lookups still use lowercase."""
    s = sentence.strip()
    for p in [".", "!", "?", ",", ";", ":", '"', "'"]:
        s = s.replace(p, " ")
    return [t for t in s.split() if t]


def _build_tags_current(sentence):
    """T for the CURRENT arm -- IDENTICAL to what v2's `ie_extract` builds internally."""
    return [(w,) + _tag_token(w) for w in _tokenize(sentence)]


def _build_tags_extended(sentence):
    """T for the POS_EXTENDED arm: closed lexicon first; UNK tokens get a second chance via the classical
    POS tagger (context-aware, cased) OR suffix/word-shape morphology (deferring to the tagger's own
    verb-family judgment to avoid mis-promoting a 3rd-person verb via the '-s ending' heuristic)."""
    lower_toks = _tokenize(sentence)
    cased_toks = _tokenize_cased(sentence)
    assert len(lower_toks) == len(cased_toks), "tokenization parity break between cased/lowercased split"
    tagged = nltk.pos_tag(cased_toks)  # REAL classical averaged-perceptron call, context-aware over the sentence
    T = []
    n_promoted = 0
    for (w_lower, w_orig, (_, ptag)) in zip(lower_toks, cased_toks, tagged):
        tag, lemma, form = _tag_token(w_lower)
        if tag == "UNK":
            tagger_says_noun = ptag in NLTK_NOUN_TAGS
            morph_says_noun = _morph_noun_shape(w_lower, w_orig) and (ptag not in NLTK_VERB_TAGS)
            if tagger_says_noun or morph_says_noun:
                tag, lemma, form = "NOUN", _oov_lemma(w_lower), None
                n_promoted += 1
        T.append((w_orig, tag, lemma, form))
    return T, n_promoted


# ---------------------------------------------------------------------------
# SHARED structural grammar engine -- a faithful re-implementation of v2's `ie_extract` core logic,
# parameterized by `require_known_entities` (CURRENT=True enforces the closed-lexicon validity filter;
# POS_EXTENDED=False accepts an OOV lemma identity as long as the RELATION is in-schema and s != o).
# PARITY with the imported `ie_extract` is asserted at self-test (proves "identical grammar rules").
# ---------------------------------------------------------------------------
def _extract_core(T, require_known_entities):
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
        if any(i < v0 for i in pron_idx):
            return [], "COREF_UNRESOLVED", "pronoun subject, no in-sentence antecedent (coreference gap)"
        return [], "NO_SUBJECT", "no noun left of verb"

    head_noun_i = subj_nouns_before_v0[0]

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

    k = matrix_vi - 1
    while k >= 0 and tags[k] == "ADV":
        k -= 1
    is_passive = (k >= 0 and tags[k] == "AUX" and verb_form in ("participle", "past_or_participle"))

    if rc:
        subjects = [lemmas[head_noun_i]]
    else:
        subj_region = [i for i in noun_idx if i < matrix_vi]
        subjects = _split_coord(subj_region, T) or [lemmas[subj_region[-1]]]

    if is_passive:
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

    if require_known_entities:
        valid = [(s, r, o) for (s, r, o) in triples
                 if s != o and r in RELATIONS and s in ENTITIES and o in ENTITIES]
    else:
        valid = [(s, r, o) for (s, r, o) in triples if s != o and r in RELATIONS]
    seen = set()
    out = []
    for tr in valid:
        if tr not in seen:
            seen.add(tr)
            out.append(tr)
    if not out:
        return [], "NO_VALID_TRIPLE", "all candidate triples failed validity"
    return out, rule, None


def ie_extract_pos_extended(sentence):
    T, n_promoted = _build_tags_extended(sentence)
    triples, rule, fail = _extract_core(T, require_known_entities=False)
    return triples, rule, fail, n_promoted


# ---------------------------------------------------------------------------
# Corpus: 10 template classes, each constructed so the REQUIRED role-slot noun is OOV -> CURRENT fully
# abstains BY CONSTRUCTION (verified at self-test, not just asserted).
# ---------------------------------------------------------------------------
def _pick(rng, pool):
    return pool[rng.randrange(len(pool))]


def _t_simple_subj_oov(rng):
    a = _pick(rng, OOV_ANIMALS)
    f = _pick(rng, KNOWN_FOODS)
    return f"The {a} eats the {f}.", [(a, "eats", f)], "simple_svo_subj_oov"


def _t_simple_obj_oov(rng):
    a = _pick(rng, KNOWN_ANIMALS)
    f = _pick(rng, OOV_FOODS)
    return f"The {a} eats the {f}.", [(a, "eats", f)], "simple_svo_obj_oov"


def _t_simple_both_oov(rng):
    a = _pick(rng, OOV_ANIMALS)
    f = _pick(rng, OOV_FOODS)
    return f"The {a} eats the {f}.", [(a, "eats", f)], "simple_svo_both_oov"


def _t_prep_subj_oov(rng):
    a = _pick(rng, OOV_ANIMALS)
    p = _pick(rng, KNOWN_PLACES)
    return f"The {a} lives in the {p}.", [(a, "lives_in", p)], "svo_prep_subj_oov"


def _t_prep_obj_oov(rng):
    a = _pick(rng, KNOWN_ANIMALS)
    p = _pick(rng, OOV_PLACES)
    return f"The {a} lives in the {p}.", [(a, "lives_in", p)], "svo_prep_obj_oov"


def _t_adj_mod_oov(rng):
    a = _pick(rng, OOV_ANIMALS)
    f = _pick(rng, KNOWN_FOODS)
    adj = _pick(rng, KNOWN_ADJS)
    return f"The {adj} {a} eats the {f}.", [(a, "eats", f)], "adj_modifier_oov"


def _t_coord_subj_both_oov(rng):
    a1 = _pick(rng, OOV_ANIMALS)
    a2 = _pick(rng, OOV_ANIMALS)
    while a2 == a1:
        a2 = _pick(rng, OOV_ANIMALS)
    f = _pick(rng, KNOWN_FOODS)
    gold = sorted({(a1, "eats", f), (a2, "eats", f)})
    return f"The {a1} and the {a2} eat the {f}.", gold, "coordination_subject_both_oov"


def _t_passive_agent_oov(rng):
    a = _pick(rng, OOV_ANIMALS)
    f = _pick(rng, KNOWN_FOODS)
    return f"The {f} is eaten by the {a}.", [(a, "eats", f)], "passive_agent_oov"


def _t_chase_subj_oov(rng):
    a1 = _pick(rng, OOV_ANIMALS)
    a2 = _pick(rng, KNOWN_ANIMALS)
    return f"The {a1} chases the {a2}.", [(a1, "chases", a2)], "svo_chase_subj_oov"


def _pluralize(w):
    """proper English -es pluralization for sibilant-final words (moss->mosses), matching what _oov_lemma's
    -es-stripping branch expects; a naive blanket '+s' on 'moss' would yield the non-word 'mosss', which is a
    CORPUS-GENERATION artifact, not a tagger/precision finding -- caught by the smoke gate (see report)."""
    if w.endswith(("s", "x", "z", "ch", "sh")):
        return w + "es"
    return w + "s"


def _t_plural_both_oov(rng):
    a = _pick(rng, OOV_ANIMALS)
    f = _pick(rng, OOV_FOODS)
    return f"{_pluralize(a).capitalize()} eat {_pluralize(f)}.", [(a, "eats", f)], "plural_no_determiner_both_oov"


TEMPLATES = [
    _t_simple_subj_oov, _t_simple_obj_oov, _t_simple_both_oov,
    _t_prep_subj_oov, _t_prep_obj_oov, _t_adj_mod_oov,
    _t_coord_subj_both_oov, _t_passive_agent_oov, _t_chase_subj_oov, _t_plural_both_oov,
]
N_PER_TEMPLATE = 4  # same for smoke and FULL (Option A discriminator-survives-scale; trivial wall time)


def build_oov_corpus(seed, n_per_template=N_PER_TEMPLATE):
    """FIXED-seed random.Random (F.5 -- never hash()); dedupes within a template's instances."""
    rng = random.Random(seed)
    rows = []
    for tmpl in TEMPLATES:
        seen = set()
        made = 0
        tries = 0
        while made < n_per_template and tries < n_per_template * 25:
            tries += 1
            sent, gold, cls = tmpl(rng)
            if sent in seen:
                continue
            seen.add(sent)
            rows.append({"sentence": sent, "gold": sorted(gold), "cls": cls})
            made += 1
        if made < n_per_template:
            raise RuntimeError(f"CORPUS_BUILD_STARVED: template {tmpl.__name__} only produced {made}/{n_per_template}")
    return rows


# guard corpus: fully in-lexicon (no OOV) -- regression check.
GUARD_SENTENCES = [
    ("The cat eats the seed.", [("cat", "eats", "seed")]),
    ("The dog chases the cow.", [("dog", "chases", "cow")]),
    ("The frog lives in the pond.", [("frog", "lives_in", "pond")]),
    ("The bread is eaten by the mouse.", [("mouse", "eats", "bread")]),
    ("The cat and the dog eat the bread.", sorted({("cat", "eats", "bread"), ("dog", "eats", "bread")})),
]

# out-of-schema control: known nouns, out-of-schema verb -- BOTH arms MUST abstain.
OUT_OF_SCHEMA_CONTROL = [
    "The cat sleeps in the barn.",
    "The rabbit sleeps in the meadow.",  # OOV noun AND out-of-schema verb -- verb-gate must still hold.
]

# mixed-conjunct coordination diagnostic (non-gating; reports the honest silent-partial-coverage finding).
MIXED_COORD_DIAGNOSTIC = [
    ("The rabbit and the cat eat the seed.", sorted({("rabbit", "eats", "seed"), ("cat", "eats", "seed")})),
    ("The dog and the badger eat the grass.", sorted({("dog", "eats", "grass"), ("badger", "eats", "grass")})),
]


def _grep_confirm_no_neural_imports():
    """Static source-scan (glass-box-legal discipline, matches v2's own convention): this cell's own source
    must not import torch/spacy/transformers/stanza (a neural component would silently break glass-box
    legality). nltk itself is legal per the research note section 4 -- only pin-checked here for THIS file.
    Regex-anchored to actual import STATEMENTS (line start) so the banned-name list literal quoted in this
    very function's body (and in this docstring) does not self-trigger a false positive."""
    src = Path(__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(import|from)\s+(torch|spacy|transformers|stanza)\b", re.MULTILINE)
    hits = [m.group(0).strip() for m in pattern.finditer(src)]
    return hits


# ---------------------------------------------------------------------------
# Evaluation.
# ---------------------------------------------------------------------------
def evaluate_row(row):
    sent = row["sentence"]
    gold = set(tuple(g) for g in row["gold"])
    cur_triples, cur_rule, cur_fail = ie_extract(sent)
    ext_triples, ext_rule, ext_fail, n_promoted = ie_extract_pos_extended(sent)
    cur_set = set(cur_triples)
    ext_set = set(ext_triples)
    return {
        "sentence": sent, "cls": row["cls"], "gold": sorted(gold),
        "current_triples": sorted(cur_set), "current_covered": bool(cur_set), "current_rule": cur_rule,
        "extended_triples": sorted(ext_set), "extended_covered": bool(ext_set), "extended_rule": ext_rule,
        "n_promoted": n_promoted,
        "newly_covered": bool(ext_set) and not bool(cur_set),
    }


def run_seed(seed, n_per_template=N_PER_TEMPLATE):
    rows = build_oov_corpus(seed, n_per_template)
    results = [evaluate_row(r) for r in rows]

    n = len(results)
    coverage_current = sum(r["current_covered"] for r in results) / n
    coverage_extended = sum(r["extended_covered"] for r in results) / n
    coverage_gain_pp = (coverage_extended - coverage_current) * 100.0

    newly = [r for r in results if r["newly_covered"]]
    n_emitted = sum(len(r["extended_triples"]) for r in newly)
    n_correct = sum(len(set(r["extended_triples"]) & set(tuple(g) for g in r["gold"])) for r in newly)
    precision_newly = (n_correct / n_emitted) if n_emitted else None
    sentence_exact_newly = (
        sum(1 for r in newly if set(r["extended_triples"]) == set(tuple(g) for g in r["gold"])) / len(newly)
        if newly else None
    )

    per_class = {}
    for r in results:
        c = per_class.setdefault(r["cls"], {"n": 0, "cur_cov": 0, "ext_cov": 0})
        c["n"] += 1
        c["cur_cov"] += int(r["current_covered"])
        c["ext_cov"] += int(r["extended_covered"])

    # guard-class regression check.
    guard_rows = [evaluate_row({"sentence": s, "gold": g, "cls": "guard"}) for (s, g) in GUARD_SENTENCES]
    guard_current_ok = all(r["current_covered"] and set(r["current_triples"]) == set(tuple(x) for x in r["gold"])
                            for r in guard_rows)
    guard_extended_ok = all(r["extended_covered"] and set(r["extended_triples"]) == set(tuple(x) for x in r["gold"])
                             for r in guard_rows)

    # out-of-schema must-fail control.
    oos_current_abstains = all(not evaluate_row({"sentence": s, "gold": [], "cls": "oos"})["current_covered"]
                                for s in OUT_OF_SCHEMA_CONTROL)
    oos_extended_abstains = all(not evaluate_row({"sentence": s, "gold": [], "cls": "oos"})["extended_covered"]
                                 for s in OUT_OF_SCHEMA_CONTROL)

    # mixed-conjunct coordination diagnostic (non-gating).
    mixed_rows = [evaluate_row({"sentence": s, "gold": g, "cls": "mixed_coord"}) for (s, g) in MIXED_COORD_DIAGNOSTIC]
    mixed_current_partial = [
        {"sentence": r["sentence"], "current_triples": r["current_triples"], "gold": r["gold"],
         "silently_incomplete": r["current_covered"] and set(r["current_triples"]) < set(tuple(x) for x in r["gold"])}
        for r in mixed_rows
    ]

    return {
        "seed": seed, "n_sentences": n,
        "coverage_current": coverage_current, "coverage_extended": coverage_extended,
        "coverage_gain_pp": coverage_gain_pp,
        "n_newly_covered": len(newly),
        "n_emitted_newly": n_emitted, "n_correct_newly": n_correct,
        "precision_newly_covered": precision_newly,
        "sentence_exact_newly_covered": sentence_exact_newly,
        "per_class": per_class,
        "guard_current_ok": guard_current_ok, "guard_extended_ok": guard_extended_ok,
        "oos_current_abstains": oos_current_abstains, "oos_extended_abstains": oos_extended_abstains,
        "mixed_coord_diagnostic": mixed_current_partial,
        "results": results,
    }


def aggregate_seeds(seeds, n_per_template=N_PER_TEMPLATE):
    per_seed = [run_seed(s, n_per_template) for s in seeds]

    coverage_current_pooled_num = sum(r["coverage_current"] * r["n_sentences"] for r in per_seed)
    total_sentences = sum(r["n_sentences"] for r in per_seed)
    coverage_current_pooled = coverage_current_pooled_num / total_sentences
    coverage_extended_pooled = sum(r["coverage_extended"] * r["n_sentences"] for r in per_seed) / total_sentences
    coverage_gain_pp_pooled = (coverage_extended_pooled - coverage_current_pooled) * 100.0

    n_emitted_pooled = sum(r["n_emitted_newly"] for r in per_seed)
    n_correct_pooled = sum(r["n_correct_newly"] for r in per_seed)
    precision_newly_covered_pooled = (n_correct_pooled / n_emitted_pooled) if n_emitted_pooled else None

    guard_all = all(r["guard_current_ok"] and r["guard_extended_ok"] for r in per_seed)
    oos_all = all(r["oos_current_abstains"] and r["oos_extended_abstains"] for r in per_seed)
    current_floor_ok = coverage_current_pooled <= 0.05

    return {
        "seeds": seeds, "n_per_template": n_per_template, "total_sentences": total_sentences,
        "coverage_current_pooled": coverage_current_pooled,
        "coverage_extended_pooled": coverage_extended_pooled,
        "coverage_gain_pp_pooled": coverage_gain_pp_pooled,
        "n_newly_covered_pooled": sum(r["n_newly_covered"] for r in per_seed),
        "n_emitted_newly_pooled": n_emitted_pooled, "n_correct_newly_pooled": n_correct_pooled,
        "precision_newly_covered_pooled": precision_newly_covered_pooled,
        "guard_regression_ok": guard_all,
        "oos_control_fired": oos_all,
        "current_coverage_floor_ok": current_floor_ok,
        "per_seed_summary": [
            {"seed": r["seed"], "coverage_current": r["coverage_current"], "coverage_extended": r["coverage_extended"],
             "coverage_gain_pp": r["coverage_gain_pp"], "precision_newly_covered": r["precision_newly_covered"],
             "n_newly_covered": r["n_newly_covered"]}
            for r in per_seed
        ],
        "per_seed_full": per_seed,
    }


def compute_verdict(agg):
    cg = agg["coverage_gain_pp_pooled"]
    prec = agg["precision_newly_covered_pooled"]
    guard_ok = agg["guard_regression_ok"]
    oos_ok = agg["oos_control_fired"]
    floor_ok = agg["current_coverage_floor_ok"]

    if prec is None:
        return ("MIDDLE_BAND",
                "no newly-covered sentences were produced by POS_EXTENDED -- cannot grade precision; "
                "the extension mechanism did not fire on this corpus", "no_newly_covered_sentences")

    hard_pass = (cg >= 15.0) and (prec >= 0.90) and guard_ok and oos_ok and floor_ok
    hard_fail = (cg < 5.0) or (prec < 0.75)

    if hard_pass:
        tier = "HARD_PASS"
    elif hard_fail:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    weakest = "n/a"
    if not hard_pass:
        if cg < 15.0:
            weakest = "coverage_gain_below_15pp"
        elif prec < 0.90:
            weakest = "precision_newly_covered_below_0.90"
        elif not guard_ok:
            weakest = "guard_regression_failed"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire"
        elif not floor_ok:
            weakest = "current_arm_not_at_floor_vacuous_test_risk"

    msg = (f"coverage_gain_pp={cg:.1f} (HARD-PASS needs >=15.0, HARD-FAIL if <5.0) | "
           f"precision_newly_covered={prec:.3f} (HARD-PASS needs >=0.90, HARD-FAIL if <0.75) | "
           f"guard_regression_ok={guard_ok} oos_control_fired={oos_ok} current_coverage_floor_ok={floor_ok} "
           f"(current_coverage_pooled={agg['coverage_current_pooled']:.3f}) | n_newly_covered_pooled="
           f"{agg['n_newly_covered_pooled']}/{agg['total_sentences']}")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# boilerplate: start marker / metrics write / crash diagnostic.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": f"exp_{ANCHOR_NAME}", "smoke": f"exp_{ANCHOR_NAME}_smoke",
           "self_test": f"exp_{ANCHOR_NAME}_selftest"}[run_mode]
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
    os.replace(tmp, out_dir / "metrics.json")


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
# self-test: EXERCISE THE REAL code path + assert the discriminators FIRE (F.1) + PARITY proof.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (imported ie_extract, real nltk.pos_tag call, this cell's "
          "ie_extract_pos_extended)...", flush=True)

    # (0) glass-box-legal: no neural imports in THIS file's own source.
    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"

    # (0b) vacuous-test guard: the OOV pools are genuinely NOT in the closed lexicon.
    assert not (set(OOV_ANIMALS) & set(ENTITIES)), "OOV_ANIMALS overlaps closed ENTITIES -- test would be vacuous"
    assert not (set(OOV_FOODS) & set(ENTITIES)), "OOV_FOODS overlaps closed ENTITIES -- test would be vacuous"
    assert not (set(OOV_PLACES) & set(ENTITIES)), "OOV_PLACES overlaps closed ENTITIES -- test would be vacuous"

    # (1) REAL classical tagger call + a few hand-verified expected tags (lightweight sanity check --
    #     scope decision: NOT a full UD-EWT/GUM independent benchmark, see module docstring).
    tagged = nltk.pos_tag(["The", "rabbit", "eats", "the", "carrot", "."])
    tagmap = dict(tagged)
    assert tagmap["rabbit"] in NLTK_NOUN_TAGS, f"expected classical tagger to tag 'rabbit' as a noun-family tag, got {tagmap['rabbit']}"
    assert tagmap["carrot"] in NLTK_NOUN_TAGS, f"expected 'carrot' noun-family tag, got {tagmap['carrot']}"
    print(f"[self_test] real nltk.pos_tag sanity: rabbit={tagmap['rabbit']} carrot={tagmap['carrot']}", flush=True)

    # (2) PARITY: this cell's _extract_core(CURRENT-tags, True) must equal the imported v2 ie_extract exactly,
    #     on a handful of sentences -- proves "identical grammar rules" rather than asserting it.
    parity_sentences = ["The cat eats the seed.", "The dog chases the cow.", "The frog lives in the pond.",
                         "The bread is eaten by the mouse.", "The cat and the dog eat the bread."]
    for s in parity_sentences:
        mine = _extract_core(_build_tags_current(s), True)
        theirs = ie_extract(s)
        assert mine == theirs, f"PARITY BREAK on {s!r}: mine={mine} theirs={theirs}"
    print(f"[self_test] PARITY OK on {len(parity_sentences)} sentences (this cell's grammar == v2's ie_extract)", flush=True)

    # (3) discriminator-fires: CURRENT must fully abstain, EXTENDED must extract, on a representative OOV sentence.
    s = "The rabbit eats the carrot."
    cur = ie_extract(s)
    ext = ie_extract_pos_extended(s)
    assert cur[0] == [], f"CURRENT unexpectedly extracted on a both-OOV sentence: {cur}"
    assert set(ext[0]) == {("rabbit", "eats", "carrot")}, f"EXTENDED failed to extract expected triple: {ext}"

    # (4) coordination both-OOV: CURRENT must fully abstain (NO_SUBJECT); EXTENDED must extract BOTH facts.
    s = "The rabbit and the duck eat the seed."
    cur = ie_extract(s)
    ext = ie_extract_pos_extended(s)
    assert cur[0] == [] and cur[1] == "NO_SUBJECT", f"CURRENT coordination-both-oov did not abstain as expected: {cur}"
    assert set(ext[0]) == {("rabbit", "eats", "seed"), ("duck", "eats", "seed")}, f"EXTENDED coord mismatch: {ext}"

    # (5) mixed-conjunct diagnostic: CURRENT silently emits an INCOMPLETE-but-correct triple (documented finding).
    s = "The rabbit and the cat eat the seed."
    cur = ie_extract(s)
    assert set(cur[0]) == {("cat", "eats", "seed")}, f"mixed-conjunct diagnostic behavior changed: {cur}"

    # (6) out-of-schema must-fail control: BOTH arms abstain even with an OOV noun present.
    for s in OUT_OF_SCHEMA_CONTROL:
        cur = ie_extract(s)
        ext = ie_extract_pos_extended(s)
        assert cur[0] == [], f"CURRENT unexpectedly extracted on out-of-schema control {s!r}: {cur}"
        assert ext[0] == [], f"EXTENDED unexpectedly extracted on out-of-schema control {s!r}: {ext}"

    # (7) guard-class regression: EXTENDED must not corrupt fully in-lexicon sentences.
    for sent, gold in GUARD_SENTENCES:
        cur = ie_extract(sent)
        ext = ie_extract_pos_extended(sent)
        gset = set(tuple(g) for g in gold)
        assert set(cur[0]) == gset, f"CURRENT guard regression on {sent!r}: {cur[0]} != {gset}"
        assert set(ext[0]) == gset, f"EXTENDED guard regression on {sent!r}: {ext[0]} != {gset}"

    # (8) ARMS-MUST-DIFFER (META_RULE_AF): CURRENT vs EXTENDED accepted-triple-set hash differs on the OOV corpus.
    rows = build_oov_corpus(seed=7, n_per_template=2)
    cur_all = sorted(set(t for r in rows for t in ie_extract(r["sentence"])[0]))
    ext_all = sorted(set(t for r in rows for t in ie_extract_pos_extended(r["sentence"])[0]))
    h_cur = hashlib.sha256(json.dumps(cur_all, sort_keys=True).encode()).hexdigest()
    h_ext = hashlib.sha256(json.dumps(ext_all, sort_keys=True).encode()).hexdigest()
    assert h_cur != h_ext, "META_RULE_AF VIOLATION: CURRENT and POS_EXTENDED produced bit-identical output"
    assert cur_all == [], f"CURRENT unexpectedly non-empty on the tiny self-test OOV corpus: {cur_all}"
    assert len(ext_all) > 0, "POS_EXTENDED produced zero triples on the tiny self-test OOV corpus -- mechanism did not fire"

    # (9) real_code_path (F.1): the full run_seed loop, tiny scale, exercising every entrypoint for real.
    r = run_seed(seed=7, n_per_template=2)
    assert r["coverage_current"] == 0.0, f"real_code_path smoke: CURRENT coverage should be 0.0, got {r['coverage_current']}"
    assert r["coverage_extended"] > 0.0, f"real_code_path smoke: EXTENDED coverage should be > 0, got {r['coverage_extended']}"
    assert r["precision_newly_covered"] is not None and r["precision_newly_covered"] >= 0.90, \
        f"real_code_path smoke: precision_newly_covered unexpectedly low: {r['precision_newly_covered']}"

    print(f"[self_test] PASS | tiny-corpus coverage_current={r['coverage_current']:.2f} "
          f"coverage_extended={r['coverage_extended']:.2f} coverage_gain_pp={r['coverage_gain_pp']:.1f} "
          f"precision_newly_covered={r['precision_newly_covered']:.3f} n_newly_covered={r['n_newly_covered']}", flush=True)
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
    seeds = [7] if run_mode == "smoke" else [7, 13, 19]
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * len(TEMPLATES) * N_PER_TEMPLATE
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[oov_pos_extension] run_mode={run_mode} seeds={seeds} n_per_template={N_PER_TEMPLATE} "
          f"n_templates={len(TEMPLATES)} expected_n_units={expected_n_units}", flush=True)

    agg = aggregate_seeds(seeds, N_PER_TEMPLATE)
    print(f"[oov_pos_extension] coverage_current_pooled={agg['coverage_current_pooled']:.3f} "
          f"coverage_extended_pooled={agg['coverage_extended_pooled']:.3f} "
          f"coverage_gain_pp_pooled={agg['coverage_gain_pp_pooled']:.1f} "
          f"precision_newly_covered_pooled={agg['precision_newly_covered_pooled']}", flush=True)

    tier, msg, weakest = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_per_template": N_PER_TEMPLATE,
        "n_templates": len(TEMPLATES),
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        "metric_coverage_current_pooled": agg["coverage_current_pooled"],
        "metric_coverage_extended_pooled": agg["coverage_extended_pooled"],
        "metric_coverage_gain_pp_pooled": agg["coverage_gain_pp_pooled"],
        "metric_precision_newly_covered_pooled": agg["precision_newly_covered_pooled"],
        "metric_n_newly_covered_pooled": agg["n_newly_covered_pooled"],
        "metric_n_emitted_newly_pooled": agg["n_emitted_newly_pooled"],
        "metric_n_correct_newly_pooled": agg["n_correct_newly_pooled"],
        "metric_guard_regression_ok": agg["guard_regression_ok"],
        "metric_oos_control_fired": agg["oos_control_fired"],
        "metric_current_coverage_floor_ok": agg["current_coverage_floor_ok"],
        "per_seed_summary": agg["per_seed_summary"],
        "mixed_coord_diagnostic": agg["per_seed_full"][0]["mixed_coord_diagnostic"],
        "arms": {
            "CURRENT": {"coverage": agg["coverage_current_pooled"]},
            "POS_EXTENDED": {"coverage": agg["coverage_extended_pooled"],
                              "precision_newly_covered": agg["precision_newly_covered_pooled"]},
        },
        "prereg": {
            "hard_pass": "coverage_gain_pp_pooled>=15.0 AND precision_newly_covered_pooled>=0.90 AND "
                         "guard_regression_ok AND oos_control_fired AND current_coverage_floor_ok",
            "hard_fail": "coverage_gain_pp_pooled<5.0 OR precision_newly_covered_pooled<0.75",
            "corpus": "10 hand-authored template classes x N_PER_TEMPLATE random OOV-word draws per seed, "
                      "OOV pools confirmed disjoint from closed ENTITIES lexicon",
            "scope_note": "function words/verbs/adjectives held CLOSED (never OOV) -- isolates OOV-NOUN "
                          "coverage specifically, per the cheap-decisive-test arm design. Not a general "
                          "open-text benchmark (see module docstring HONEST SCOPE NOTE).",
            "compute_architecture": "sequential-CPU; pure syntactic parsing, no VSA store; wall time trivial "
                                    "(MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer test, no FoundationStore/KGStore touched)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract (imported, unmodified)", "nltk.pos_tag (real classical "
                                         "averaged-perceptron call)", "ie_extract_pos_extended (this cell)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete syntactic role-assignment + "
                       "the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED)",
            "glass_box_legal": "no torch/spacy/transformers/stanza imports in this file (source-scanned at "
                               "self-test); nltk averaged_perceptron_tagger_eng is classical, non-neural",
            "prior_work_check": "substrate_query.sh top hits all below cosine 0.30 (top=0.2764, entity="
                                "'syntactical') -- no prior arc cell at cosine>0.30; genuinely novel, not a "
                                "rediscovery.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[oov_pos_extension] {tier} in {elapsed:.2f}s -> {out_dir / 'metrics.json'}", flush=True)
    print(f"[oov_pos_extension] {msg}", flush=True)
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
