"""exp_read_grow_oov_verb_extension_v1 -- RUNG 3 of the open-text glass-box reading curriculum: lifts the
CLOSED-VERB architectural shield that protected exp_read_grow_oov_pos_extension_v1 (RUNG 2)'s precision=1.0.

RUNG 2's landed-VET (skunkworks a3dd86bc) established: RUNG 2's precision=1.000 was protected by
closed-lexicon-first ordering -- verbs were ALWAYS resolved from the closed VERB_LEX (never OOV), so the
classical tagger's real mistag mode (verified in THIS cell's own tagger probe: NLTK tags a bare-form verb
after a plural, determiner-less subject as NN -- e.g. "Rabbits eat berries." -> eat/NN) never went live: the
closed lookup for "eat"/"chase"/"live" short-circuited BEFORE the tagger's per-token judgment on the VERB
token itself was ever consulted. The VET's CP->capability expansion criterion (verbatim): "re-run this same
discriminator design ... on a corpus where VERBS are also OOV (lifting the current closed-verb shield) --
that is the exact condition under which the tagger mistag mode I found (eat->NN) becomes architecturally live
rather than shielded." This cell IS that re-run.

MECHANISM (new relative to RUNG 2): a small set of REAL ENGLISH SYNONYM VERBS for the 3 known relations
(eats/chases/lives_in) are deliberately kept OUT of the closed VERB_LEX (munch/nibble/devour/gobble for
"eats"; pursue/hunt/stalk for "chases"; dwell/reside for "lives_in" -- vacuous-test-guarded disjoint from
VERB_LEX at self-test). When the closed lexicon returns UNK for one of these tokens, POS_EXTENDED gets a
second chance via (a) the classical tagger's VB-family judgment (now genuinely LOAD-BEARING for verbs, not
just nouns) OR (b) a NEW verb-specific morphological suffix-stripper (-ing/-ed/-s/-es, with silent-e
restoration, e.g. "residing"->"resid"->"reside") that recovers the base form and looks it up in a small
PRE-DECLARED (glass-box, not runtime-invented) base-form -> relation-stem table -- deferring to the tagger's
own NOUN-family judgment to avoid the symmetric mistake (mirrors RUNG 2's noun-morphology deferral to the
tagger's VERB-family judgment, now inverted). Nouns are held CLOSED in the PRIMARY corpus (isolates the
verb-OOV axis cleanly, same methodology RUNG 2 used to isolate the noun-OOV axis) -- a SECONDARY, NON-GATING
diagnostic corpus combines OOV nouns (reusing RUNG 2's OOV pools, imported) with OOV verbs, reported
separately (see MIXED_OOV_DIAGNOSTIC), per the contract's explicit invitation to test compounded OOV.

GENUINE 3-LAYER REUSE (does not edit v2 or RUNG 2's cell): imports the closed-schema grammar engine
`_extract_core` DIRECTLY from RUNG 2 (which itself parity-proved `_extract_core` against v2's `ie_extract` at
its own self-test) -- this cell does NOT re-implement the grammar a third time, eliminating re-implementation-
drift risk entirely. Also imports RUNG 2's noun-OOV machinery (`_morph_noun_shape`, `_oov_lemma`,
`_tokenize_cased`, `NLTK_NOUN_TAGS`, `NLTK_VERB_TAGS`, OOV noun pools, and RUNG 2's own
`ie_extract_pos_extended` for a genuine-incrementality control) verbatim.

GLASS-BOX-LEGAL (verified, no LLM, no neural net anywhere in the import chain -- see
`_grep_confirm_no_neural_imports` below, same discipline as v2 and RUNG 2): `nltk.pos_tag` with the
`averaged_perceptron_tagger_eng` model is the same classical, non-neural, structured-perceptron tagger used
by both prior rungs.

EMPIRICALLY-PROBED tagger behavior (MEASURED via a standalone offline nltk.pos_tag() probe run before corpus
design, not hypothesized): the "eat->NN"-class mistag is VERB-SPECIFIC and CONTEXT-SENSITIVE, not a uniform
rule -- of the 9 synonym verbs, in the bare-plural-no-determiner frame: munch/pursue/hunt mistag to NN
(noun-family, NOT rescued -- this cell's design correctly defers to the tagger's noun judgment here, same as
RUNG 2's discipline, so these cause a clean coverage-loss ABSTAIN, not a wrong triple); nibble/gobble mistag
to JJ (adjective, NEITHER noun- nor verb-family -- morphology correctly RESCUES these, since the fallback only
defers to NOUN-family tags); devour/dwell/stalk/reside tag correctly (VBP) even bare-plural. This is a real,
reproducible, MEASURED finding (see self_test assertions (1) and (6b) below), not tuned to force a result.

ARCHITECTURAL SAFETY PROPERTY (a mechanism-level finding, verified by construction and asserted at self-test
(6b)): because `_extract_core` (imported, unmodified) returns immediately with `NO_VERB` the instant
`verb_idx` is empty -- BEFORE any subject/object noun collection runs -- a verb-token mistagged to NOUN can
only ever cause a coverage-loss ABSTAIN in a single-clause sentence, never a WRONG triple with a spurious
"munch"/"pursue"/"hunt" filler in a role slot. This is a structural property of the shared grammar engine, not
a lucky corpus draw; it predicts precision_newly_covered should stay high even where coverage suffers -- an
honest, MEASURED, and DIFFERENT finding from the naive "the shield lifting drops precision" prior, reported
as-found (see module docstring HONEST FINDING note at dispatch time / pre-reg Result section).

CORPUS (hand-authored generator; per contract, deliberately NOT engineered to dodge the mistag mode -- the
verb pool draws from the FULL closed ANIMALS/FOODS/PLACES noun pools, and bare-plural frames are INCLUDED,
not avoided, specifically because that is the exact context the tagger probe showed the mistag fires in):
  PRIMARY: 12 template classes (3sg+determiner / bare-plural-no-determiner / passive / past-active /
  gerund-progressive / adjective-modified, crossed with the 3 relation families where the frame is
  grammatical) x N_PER_TEMPLATE=4 draws x 3 seeds. Nouns held CLOSED (ANIMALS/FOODS/PLACES, imported from v2)
  -- isolates the verb-OOV axis. Bare-plural-safe animal subset excludes "fish" (invariant plural) and
  "mouse" (irregular "mice") to avoid a corpus-GENERATION artifact (same class of bug RUNG 2 caught and fixed
  for "moss"->"mosss"; this is a proactive avoidance of a KNOWN irregular-plural trap, not a mistag-mode
  dodge -- the mistag-prone verbs themselves are NOT filtered out).
  SECONDARY (non-gating diagnostic): MIXED_OOV_DIAGNOSTIC -- a handful of hand-authored sentences with BOTH
  an OOV noun (reusing RUNG 2's OOV_ANIMALS/OOV_FOODS/OOV_PLACES pools) AND an OOV verb, including one
  bare-plural BOTH-OOV case, reported separately per contract ("Nouns may be OOV or closed -- your call").
  GUARD_SENTENCES (fully closed, regression check) and OUT_OF_SCHEMA_CONTROL (a verb genuinely absent from
  BOTH the closed VERB_LEX and this cell's OOV_VERB_BASE_LEX, e.g. "yawns"/"sleeps" -- BOTH arms must abstain,
  proving the extension does not hallucinate a relation for a truly unmapped verb).

METRICS / BANDS (same discriminator design as RUNG 2, envelope-adjusted per the contract's honest expectation
that a live mistag mode may cost precision or coverage rather than the near-ceiling result RUNG 2 found):
  HARD-PASS: coverage_gain_pp (POS_EXTENDED - CURRENT, primary corpus) >= 15.0 AND precision_newly_covered
             (pooled, triple-level, on sentences CURRENT fully abstains on AND EXTENDED extracts >=1 triple)
             >= 0.60 AND guard_regression_ok AND oos_control_fired AND current_coverage_floor_ok.
  HARD-FAIL: coverage_gain_pp < 5.0 OR precision_newly_covered < 0.50.
  MIDDLE_BAND: otherwise (including zero newly-covered sentences).
  HONEST FRAMING: unlike RUNG 2, a HARD-PASS here is NOT expected to show 100pp/1.000 -- the tagger mistag
  mode is architecturally live in this corpus by design; the report states, whatever it measures, (a) how
  often the tagger mistags an OOV verb, (b) whether verb-morphology rescues any of those mistags (previously
  DEAD CODE per RUNG 2's VET finding -- specifically exercised here via -ing/-ed/-s suffix stripping on
  VERBS), and (c) where residual errors land (coverage-loss abstain vs wrong-triple, per the architectural
  safety property above).

Local numpy + nltk, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (pure syntactic parsing over a small
corpus; wall time trivial, MEASURED below). No VSA store touched. progress_logging = print_flush_true (not
required at timeout_s < 1800, included for parity). Dispatch: COMPUTE-PROPORTIONALITY, runs INLINE/FOREGROUND
locally (matches RUNG 2's own precedent; no GPU/remote SCP/atomize needed for a trivial-wall-time parser
cell). Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before this run.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; CURRENT vs POS_EXTENDED accepted-triple-set hash differs
#   on the primary OOV-verb corpus by construction -- CURRENT emits nothing (every verb OOV), EXTENDED emits
#   triples on the subset the tagger/morphology correctly resolves).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor -- discriminator is discrete syntactic role-assignment + a classical
#   POS tagger's own (externally benchmarked, 96-97% PTB, CITED@research note sec 3) categorical accuracy on
#   THIS specific corpus's verb tokens (empirically probed via a standalone nltk.pos_tag() run, MEASURED not
#   guessed). No VSA cleanup step in this cell at all.
# - baseline_in_band: N/A BY DESIGN for this cell's shape (declared, matching RUNG 2's own declared exemption)
#   -- CURRENT-at-floor IS the required vacuous-test guard (current_coverage_floor_ok), not a measurability
#   failure; every primary-corpus sentence requires a verb OOV to the closed VERB_LEX by construction.
# - discriminator survives scale: corpus is FIXED-size (hand-authored templates x random draws). Smoke uses
#   the SAME template set + SAME N_PER_TEMPLATE as FULL (Option A, discriminator-must-survive-scale) --
#   trivial wall time makes this free.
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test calls the REAL `nltk.pos_tag` (external classical-ML tagger, not mocked),
#   the REAL imported `ie_extract` (v2, unmodified), and the REAL imported `_extract_core` (RUNG 2, itself
#   parity-proven against v2 -- this cell does not re-derive parity, it inherits it by reusing the identical
#   function object, eliminating re-implementation-drift risk).
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19]; random.Random(seed) (never hash()); sorted()
#   used for all set->list conversions in metrics; no list(set(...)) ordering dependence.
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics / CITED@research-note
#   / MEASURED@standalone-tagger-probe (this cell's own pre-design empirical nltk.pos_tag() run).
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

ANCHOR_NAME = "read_grow_oov_verb_extension_v1"

# --- GENUINE 3-LAYER REUSE: v2 (closed-schema grammar + lexicon) + RUNG 2 (noun-OOV machinery + the ALREADY
# parity-proven `_extract_core`), both imported verbatim, neither edited. ---
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import (  # noqa: E402
    ADJS, ENTITIES, RELATIONS, ANIMALS, FOODS, PLACES, VERB_LEX,
    _tag_token, _tokenize, _resolve_relation, _split_coord, ie_extract,
)
from experiments.exp_read_grow_oov_pos_extension_v1 import (  # noqa: E402
    _extract_core, _tokenize_cased, _morph_noun_shape, _oov_lemma,
    NLTK_NOUN_TAGS, NLTK_VERB_TAGS,
    OOV_ANIMALS, OOV_FOODS, OOV_PLACES,
    ie_extract_pos_extended as rung2_ie_extract_pos_extended,
)

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only; see glass-box-legal note above.

# ---------------------------------------------------------------------------
# NEW (this cell): OOV verb base-form -> relation-stem table. Real English synonyms for the 3 known
# relations, PRE-DECLARED (glass-box, not invented at runtime from the tagger's output) and deliberately kept
# OUT of the closed VERB_LEX (disjointness confirmed at self-test -- vacuous-test guard).
# ---------------------------------------------------------------------------
OOV_VERB_BASE_LEX = {
    "munch": "eats", "nibble": "eats", "devour": "eats", "gobble": "eats",
    "pursue": "chases", "hunt": "chases", "stalk": "chases",
    "dwell": "live", "reside": "live",
}
EATS_VERBS = ["munch", "nibble", "devour", "gobble"]
CHASES_VERBS = ["pursue", "hunt", "stalk"]
LIVE_VERBS = ["dwell", "reside"]

# bare-plural-safe closed animal subset: excludes "fish" (invariant plural) and "mouse" (irregular "mice") --
# a proactive corpus-GENERATION-artifact avoidance (same class as RUNG 2's "moss"->"mosss" catch), NOT a
# mistag-mode dodge (the risky VERBS are not filtered; only the two irregular-noun-plural traps are).
ANIMALS_BARE_SAFE = [a for a in ANIMALS if a not in ("fish", "mouse")]


def _v3sg(v):
    """productive 3rd-person-singular: sibilant-final stems take -es (matches RUNG 2's `_pluralize` rule,
    now applied to VERBS -- MEASURED@standalone-tagger-probe to match NLTK's own expectation, e.g. munch->
    munches)."""
    if v.endswith(("ch", "sh", "x", "s", "z")):
        return v + "es"
    return v + "s"


def _vpast(v):
    """productive past/participle (regular verbs only, so past==participle spelling): silent-e stems take
    -d, else -ed."""
    if v.endswith("e"):
        return v + "d"
    return v + "ed"


def _vgerund(v):
    """productive gerund: silent-e stems (not double-e) drop the e before -ing."""
    if v.endswith("e") and not v.endswith("ee"):
        return v[:-1] + "ing"
    return v + "ing"


def _pluralize_closed(w):
    """same sibilant-aware pluralization rule as RUNG 2's `_pluralize`, applied to closed nouns for the
    bare-plural verb-OOV templates."""
    if w.endswith(("s", "x", "z", "ch", "sh")):
        return w + "es"
    return w + "s"


def _oov_verb_base_and_form(w_lower):
    """NEW (this cell): morphological suffix-stripper for OOV verb surface forms -> (relation_stem, form).
    Tries -ing (gerund), -ed (past_or_participle), -es/-s (3sg), and the bare base form, with silent-e
    restoration (e.g. 'residing' -> strip 'ing' -> 'resid' -> +'e' -> 'reside', a lex hit) -- MEASURED to
    correctly invert all 9 OOV_VERB_BASE_LEX entries' regular inflections (verified at self-test (2b))."""
    if w_lower in OOV_VERB_BASE_LEX:
        return OOV_VERB_BASE_LEX[w_lower], "base"
    if w_lower.endswith("ing") and len(w_lower) > 4:
        stem = w_lower[:-3]
        for cand in (stem, stem + "e"):
            if cand in OOV_VERB_BASE_LEX:
                return OOV_VERB_BASE_LEX[cand], "gerund"
    if w_lower.endswith("ed") and len(w_lower) > 3:
        stem = w_lower[:-2]
        for cand in (stem, stem + "e"):
            if cand in OOV_VERB_BASE_LEX:
                return OOV_VERB_BASE_LEX[cand], "past_or_participle"
    if w_lower.endswith("es") and len(w_lower) > 3:
        stem = w_lower[:-2]
        for cand in (stem, stem + "e"):
            if cand in OOV_VERB_BASE_LEX:
                return OOV_VERB_BASE_LEX[cand], "3sg"
    if w_lower.endswith("s") and not w_lower.endswith("ss") and len(w_lower) > 2:
        stem = w_lower[:-1]
        if stem in OOV_VERB_BASE_LEX:
            return OOV_VERB_BASE_LEX[stem], "3sg"
    return None


def _classify_unk_token(w_lower, w_orig, ptag):
    """NEW (this cell): combined NOUN (RUNG 2's mechanism, reused verbatim) + VERB (new) promotion decision
    for a token the closed lexicon tagged UNK. VERB path: tagger says VB-family, OR (verb-morphology
    recognizes the base AND tagger does NOT say NOUN-family -- defers to the tagger's noun judgment, mirror
    of RUNG 2's noun-morphology deferral to the tagger's verb judgment, now inverted). If the tagger says
    VB-family but this cell's small base-lexicon doesn't recognize the base (a genuinely unmapped verb),
    still tag VERB with an unresolved lemma -- `_resolve_relation` (imported, unmodified) correctly returns
    None for it, so the sentence honestly abstains downstream (UNKNOWN_VERB) rather than hallucinating a
    relation. Returns (tag, lemma, form, promo_kind) where promo_kind in {None, 'verb_tagger', 'verb_morph',
    'verb_tagger_and_morph', 'verb_unresolved', 'noun_tagger', 'noun_morph'} for honest bookkeeping."""
    verb_hit = _oov_verb_base_and_form(w_lower)
    tagger_says_verb = ptag in NLTK_VERB_TAGS
    tagger_says_noun = ptag in NLTK_NOUN_TAGS
    morph_verb_ok = (verb_hit is not None) and (not tagger_says_noun)
    if tagger_says_verb or morph_verb_ok:
        if verb_hit is not None:
            stem, form = verb_hit
            kind = "verb_tagger_and_morph" if tagger_says_verb else "verb_morph"
            return "VERB", stem, form, kind
        return "VERB", "__OOV_UNRESOLVED__", "unknown", "verb_unresolved"
    morph_noun_ok = _morph_noun_shape(w_lower, w_orig) and (not tagger_says_verb)
    if tagger_says_noun or morph_noun_ok:
        kind = "noun_tagger" if tagger_says_noun else "noun_morph"
        return "NOUN", _oov_lemma(w_lower), None, kind
    return "UNK", None, None, None


def _build_tags_verb_extended(sentence):
    """T for the POS_EXTENDED arm: closed lexicon FIRST (unchanged, via `_tag_token`); UNK tokens get a
    second chance via `_classify_unk_token` (noun OR verb promotion). Returns (T, promo_counts dict)."""
    lower_toks = _tokenize(sentence)
    cased_toks = _tokenize_cased(sentence)
    assert len(lower_toks) == len(cased_toks), "tokenization parity break between cased/lowercased split"
    tagged = nltk.pos_tag(cased_toks)
    T = []
    counts = {"verb_tagger": 0, "verb_morph": 0, "verb_tagger_and_morph": 0, "verb_unresolved": 0,
              "noun_tagger": 0, "noun_morph": 0}
    for (w_lower, w_orig, (_, ptag)) in zip(lower_toks, cased_toks, tagged):
        tag, lemma, form = _tag_token(w_lower)
        if tag == "UNK":
            new_tag, new_lemma, new_form, kind = _classify_unk_token(w_lower, w_orig, ptag)
            if kind is not None:
                counts[kind] += 1
                tag, lemma, form = new_tag, new_lemma, new_form
        T.append((w_orig, tag, lemma, form))
    return T, counts


def ie_extract_verb_extended(sentence):
    T, counts = _build_tags_verb_extended(sentence)
    triples, rule, fail = _extract_core(T, require_known_entities=False)
    return triples, rule, fail, counts


# ---------------------------------------------------------------------------
# PRIMARY corpus: 12 template classes, nouns held CLOSED, verbs held OOV -- isolates the verb-OOV axis.
# ---------------------------------------------------------------------------
def _pick(rng, pool):
    return pool[rng.randrange(len(pool))]


def _t_3sg_det_eats(rng):
    a = _pick(rng, ANIMALS)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, FOODS)
    return f"The {a} {_v3sg(v)} the {f}.", [(a, "eats", f)], "verb_oov_3sg_det_eats"


def _t_bare_plural_eats(rng):
    a = _pick(rng, ANIMALS_BARE_SAFE)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, FOODS)
    return f"{_pluralize_closed(a).capitalize()} {v} {_pluralize_closed(f)}.", [(a, "eats", f)], "verb_oov_bare_plural_eats"


def _t_3sg_det_chases(rng):
    a1 = _pick(rng, ANIMALS)
    a2 = _pick(rng, ANIMALS)
    while a2 == a1:
        a2 = _pick(rng, ANIMALS)
    v = _pick(rng, CHASES_VERBS)
    return f"The {a1} {_v3sg(v)} the {a2}.", [(a1, "chases", a2)], "verb_oov_3sg_det_chases"


def _t_bare_plural_chases(rng):
    a1 = _pick(rng, ANIMALS_BARE_SAFE)
    a2 = _pick(rng, ANIMALS_BARE_SAFE)
    while a2 == a1:
        a2 = _pick(rng, ANIMALS_BARE_SAFE)
    v = _pick(rng, CHASES_VERBS)
    return f"{_pluralize_closed(a1).capitalize()} {v} {_pluralize_closed(a2)}.", [(a1, "chases", a2)], "verb_oov_bare_plural_chases"


def _t_3sg_det_live(rng):
    a = _pick(rng, ANIMALS)
    v = _pick(rng, LIVE_VERBS)
    p = _pick(rng, PLACES)
    return f"The {a} {_v3sg(v)} in the {p}.", [(a, "lives_in", p)], "verb_oov_3sg_det_live"


def _t_bare_plural_live(rng):
    a = _pick(rng, ANIMALS_BARE_SAFE)
    v = _pick(rng, LIVE_VERBS)
    p = _pick(rng, PLACES)
    return f"{_pluralize_closed(a).capitalize()} {v} in {_pluralize_closed(p)}.", [(a, "lives_in", p)], "verb_oov_bare_plural_live"


def _t_passive_eats(rng):
    a = _pick(rng, ANIMALS)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, FOODS)
    return f"The {f} is {_vpast(v)} by the {a}.", [(a, "eats", f)], "verb_oov_passive_eats"


def _t_passive_chases(rng):
    a1 = _pick(rng, ANIMALS)
    a2 = _pick(rng, ANIMALS)
    while a2 == a1:
        a2 = _pick(rng, ANIMALS)
    v = _pick(rng, CHASES_VERBS)
    return f"The {a2} is {_vpast(v)} by the {a1}.", [(a1, "chases", a2)], "verb_oov_passive_chases"


def _t_past_active_eats(rng):
    a = _pick(rng, ANIMALS)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, FOODS)
    return f"The {a} {_vpast(v)} the {f}.", [(a, "eats", f)], "verb_oov_past_active_eats"


def _t_past_active_chases(rng):
    a1 = _pick(rng, ANIMALS)
    a2 = _pick(rng, ANIMALS)
    while a2 == a1:
        a2 = _pick(rng, ANIMALS)
    v = _pick(rng, CHASES_VERBS)
    return f"The {a1} {_vpast(v)} the {a2}.", [(a1, "chases", a2)], "verb_oov_past_active_chases"


def _t_gerund_prog_eats(rng):
    a = _pick(rng, ANIMALS)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, FOODS)
    return f"The {a} is {_vgerund(v)} the {f}.", [(a, "eats", f)], "verb_oov_gerund_prog_eats"


def _t_adj_mod_3sg_eats(rng):
    a = _pick(rng, ANIMALS)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, FOODS)
    adj = _pick(rng, sorted(ADJS))
    return f"The {adj} {a} {_v3sg(v)} the {f}.", [(a, "eats", f)], "verb_oov_adj_mod_3sg_eats"


TEMPLATES = [
    _t_3sg_det_eats, _t_bare_plural_eats,
    _t_3sg_det_chases, _t_bare_plural_chases,
    _t_3sg_det_live, _t_bare_plural_live,
    _t_passive_eats, _t_passive_chases,
    _t_past_active_eats, _t_past_active_chases,
    _t_gerund_prog_eats, _t_adj_mod_3sg_eats,
]
N_PER_TEMPLATE = 4  # same for smoke and FULL (Option A discriminator-survives-scale; trivial wall time)


def build_verb_oov_corpus(seed, n_per_template=N_PER_TEMPLATE):
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


# guard corpus: fully closed lexicon (no OOV anywhere) -- regression check.
GUARD_SENTENCES = [
    ("The cat eats the seed.", [("cat", "eats", "seed")]),
    ("The dog chases the cow.", [("dog", "chases", "cow")]),
    ("The frog lives in the pond.", [("frog", "lives_in", "pond")]),
    ("The bread is eaten by the mouse.", [("mouse", "eats", "bread")]),
    ("The cat and the dog eat the bread.", sorted({("cat", "eats", "bread"), ("dog", "eats", "bread")})),
]

# out-of-schema control: closed nouns, a verb genuinely absent from BOTH the closed VERB_LEX and this cell's
# OOV_VERB_BASE_LEX -- BOTH arms MUST abstain (proves the extension does not hallucinate a relation).
OUT_OF_SCHEMA_CONTROL = [
    "The cat sleeps in the barn.",
    "The dog yawns near the tree.",
]

# SECONDARY, NON-GATING diagnostic: BOTH an OOV noun (RUNG 2 pools, imported) AND an OOV verb (this cell's
# pool) in the same sentence, per contract's explicit invitation ("Nouns may be OOV or closed -- your call").
# "carrot"/"acorn" chosen (not "berry"/"leaf") to avoid RUNG 2's own -ies/irregular-plural lemma-reduction
# edge case in the bare-plural row (a corpus-authoring precaution, not a mechanism dodge).
MIXED_OOV_DIAGNOSTIC = [
    ("The rabbit munches the carrot.", [("rabbit", "eats", "carrot")], "mixed_3sg_det_eats"),
    ("The duck resides in the meadow.", [("duck", "lives_in", "meadow")], "mixed_3sg_det_live"),
    ("The otter pursues the rabbit.", [("otter", "chases", "rabbit")], "mixed_3sg_det_chases"),
    ("Rabbits munch carrots.", [("rabbit", "eats", "carrot")], "mixed_bare_plural_eats"),
    ("The carrot is munched by the rabbit.", [("rabbit", "eats", "carrot")], "mixed_passive_eats"),
    ("The rabbit is munching the carrot.", [("rabbit", "eats", "carrot")], "mixed_gerund_prog_eats"),
]


def _grep_confirm_no_neural_imports():
    """Static source-scan (glass-box-legal discipline, matches v2/RUNG 2's own convention): this cell's own
    source must not import torch/spacy/transformers/stanza. nltk itself is legal (research note section 4)
    -- only pin-checked here for THIS file. Regex-anchored to actual import STATEMENTS (line start) so the
    banned-name list literal quoted in this very function's body does not self-trigger."""
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
    ext_triples, ext_rule, ext_fail, counts = ie_extract_verb_extended(sent)
    cur_set = set(cur_triples)
    ext_set = set(ext_triples)
    return {
        "sentence": sent, "cls": row["cls"], "gold": sorted(gold),
        "current_triples": sorted(cur_set), "current_covered": bool(cur_set), "current_rule": cur_rule,
        "extended_triples": sorted(ext_set), "extended_covered": bool(ext_set), "extended_rule": ext_rule,
        "promo_counts": counts,
        "newly_covered": bool(ext_set) and not bool(cur_set),
        "wrong_triple_emitted": bool(ext_set) and (ext_set != (ext_set & gold)),
    }


def run_seed(seed, n_per_template=N_PER_TEMPLATE):
    rows = build_verb_oov_corpus(seed, n_per_template)
    results = [evaluate_row(r) for r in rows]

    n = len(results)
    coverage_current = sum(r["current_covered"] for r in results) / n
    coverage_extended = sum(r["extended_covered"] for r in results) / n
    coverage_gain_pp = (coverage_extended - coverage_current) * 100.0

    newly = [r for r in results if r["newly_covered"]]
    n_emitted = sum(len(r["extended_triples"]) for r in newly)
    n_correct = sum(len(set(r["extended_triples"]) & set(tuple(g) for g in r["gold"])) for r in newly)
    precision_newly = (n_correct / n_emitted) if n_emitted else None

    # verb-mistag / morphology-rescue bookkeeping (the tagger's own tag on the OOV verb token, pooled).
    n_verb_tagger = sum(r["promo_counts"].get("verb_tagger", 0) for r in results)
    n_verb_morph_rescue = sum(r["promo_counts"].get("verb_morph", 0) for r in results)
    n_verb_tagger_and_morph = sum(r["promo_counts"].get("verb_tagger_and_morph", 0) for r in results)
    n_verb_unresolved = sum(r["promo_counts"].get("verb_unresolved", 0) for r in results)
    n_verb_mistagged_uncorrected = sum(
        1 for r in results if "verb_oov" in r["cls"] and not r["extended_covered"] and r["current_rule"] == "NO_VERB"
    )

    per_class = {}
    for r in results:
        c = per_class.setdefault(r["cls"], {"n": 0, "cur_cov": 0, "ext_cov": 0})
        c["n"] += 1
        c["cur_cov"] += int(r["current_covered"])
        c["ext_cov"] += int(r["extended_covered"])

    guard_rows = [evaluate_row({"sentence": s, "gold": g, "cls": "guard"}) for (s, g) in GUARD_SENTENCES]
    guard_current_ok = all(r["current_covered"] and set(r["current_triples"]) == set(tuple(x) for x in r["gold"])
                            for r in guard_rows)
    guard_extended_ok = all(r["extended_covered"] and set(r["extended_triples"]) == set(tuple(x) for x in r["gold"])
                             for r in guard_rows)

    oos_current_abstains = all(not evaluate_row({"sentence": s, "gold": [], "cls": "oos"})["current_covered"]
                                for s in OUT_OF_SCHEMA_CONTROL)
    oos_extended_abstains = all(not evaluate_row({"sentence": s, "gold": [], "cls": "oos"})["extended_covered"]
                                 for s in OUT_OF_SCHEMA_CONTROL)

    # no WRONG-triple ever emitted anywhere on the primary corpus (architectural safety-property assertion).
    any_wrong_triple = any(r["wrong_triple_emitted"] for r in results)

    # SECONDARY non-gating diagnostic: combined OOV noun + OOV verb.
    mixed_rows = [evaluate_row({"sentence": s, "gold": g, "cls": c}) for (s, g, c) in MIXED_OOV_DIAGNOSTIC]
    mixed_summary = [
        {"sentence": r["sentence"], "cls": r["cls"], "gold": r["gold"],
         "current_covered": r["current_covered"], "extended_covered": r["extended_covered"],
         "extended_triples": r["extended_triples"], "extended_correct": r["extended_triples"] == r["gold"]}
        for r in mixed_rows
    ]

    # RUNG 2 incrementality control: RUNG 2's own POS_EXTENDED mechanism (noun-OOV only) should NOT already
    # solve this corpus (verbs are untouched by RUNG 2) -- proves the verb-OOV capability is genuinely new.
    rung2_coverage_on_this_corpus = sum(
        1 for r in results if set(rung2_ie_extract_pos_extended(r["sentence"])[0])
    ) / n

    return {
        "seed": seed, "n_sentences": n,
        "coverage_current": coverage_current, "coverage_extended": coverage_extended,
        "coverage_gain_pp": coverage_gain_pp,
        "n_newly_covered": len(newly),
        "n_emitted_newly": n_emitted, "n_correct_newly": n_correct,
        "precision_newly_covered": precision_newly,
        "n_verb_tagger": n_verb_tagger, "n_verb_morph_rescue": n_verb_morph_rescue,
        "n_verb_tagger_and_morph": n_verb_tagger_and_morph, "n_verb_unresolved": n_verb_unresolved,
        "n_verb_mistagged_uncorrected": n_verb_mistagged_uncorrected,
        "any_wrong_triple_emitted": any_wrong_triple,
        "per_class": per_class,
        "guard_current_ok": guard_current_ok, "guard_extended_ok": guard_extended_ok,
        "oos_current_abstains": oos_current_abstains, "oos_extended_abstains": oos_extended_abstains,
        "mixed_oov_diagnostic": mixed_summary,
        "rung2_coverage_on_this_corpus": rung2_coverage_on_this_corpus,
        "results": results,
    }


def aggregate_seeds(seeds, n_per_template=N_PER_TEMPLATE):
    per_seed = [run_seed(s, n_per_template) for s in seeds]

    total_sentences = sum(r["n_sentences"] for r in per_seed)
    coverage_current_pooled = sum(r["coverage_current"] * r["n_sentences"] for r in per_seed) / total_sentences
    coverage_extended_pooled = sum(r["coverage_extended"] * r["n_sentences"] for r in per_seed) / total_sentences
    coverage_gain_pp_pooled = (coverage_extended_pooled - coverage_current_pooled) * 100.0

    n_emitted_pooled = sum(r["n_emitted_newly"] for r in per_seed)
    n_correct_pooled = sum(r["n_correct_newly"] for r in per_seed)
    precision_newly_covered_pooled = (n_correct_pooled / n_emitted_pooled) if n_emitted_pooled else None

    guard_all = all(r["guard_current_ok"] and r["guard_extended_ok"] for r in per_seed)
    oos_all = all(r["oos_current_abstains"] and r["oos_extended_abstains"] for r in per_seed)
    current_floor_ok = coverage_current_pooled <= 0.05
    any_wrong_triple_pooled = any(r["any_wrong_triple_emitted"] for r in per_seed)

    return {
        "seeds": seeds, "n_per_template": n_per_template, "total_sentences": total_sentences,
        "coverage_current_pooled": coverage_current_pooled,
        "coverage_extended_pooled": coverage_extended_pooled,
        "coverage_gain_pp_pooled": coverage_gain_pp_pooled,
        "n_newly_covered_pooled": sum(r["n_newly_covered"] for r in per_seed),
        "n_emitted_newly_pooled": n_emitted_pooled, "n_correct_newly_pooled": n_correct_pooled,
        "precision_newly_covered_pooled": precision_newly_covered_pooled,
        "n_verb_tagger_pooled": sum(r["n_verb_tagger"] for r in per_seed),
        "n_verb_morph_rescue_pooled": sum(r["n_verb_morph_rescue"] for r in per_seed),
        "n_verb_tagger_and_morph_pooled": sum(r["n_verb_tagger_and_morph"] for r in per_seed),
        "n_verb_unresolved_pooled": sum(r["n_verb_unresolved"] for r in per_seed),
        "n_verb_mistagged_uncorrected_pooled": sum(r["n_verb_mistagged_uncorrected"] for r in per_seed),
        "any_wrong_triple_emitted_pooled": any_wrong_triple_pooled,
        "guard_regression_ok": guard_all,
        "oos_control_fired": oos_all,
        "current_coverage_floor_ok": current_floor_ok,
        "rung2_coverage_on_this_corpus_pooled": sum(
            r["rung2_coverage_on_this_corpus"] * r["n_sentences"] for r in per_seed) / total_sentences,
        "per_seed_summary": [
            {"seed": r["seed"], "coverage_current": r["coverage_current"], "coverage_extended": r["coverage_extended"],
             "coverage_gain_pp": r["coverage_gain_pp"], "precision_newly_covered": r["precision_newly_covered"],
             "n_newly_covered": r["n_newly_covered"], "n_verb_mistagged_uncorrected": r["n_verb_mistagged_uncorrected"]}
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
                "the verb extension mechanism did not fire on this corpus", "no_newly_covered_sentences")

    hard_pass = (cg >= 15.0) and (prec >= 0.60) and guard_ok and oos_ok and floor_ok
    hard_fail = (cg < 5.0) or (prec < 0.50)

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
        elif prec < 0.60:
            weakest = "precision_newly_covered_below_0.60"
        elif not guard_ok:
            weakest = "guard_regression_failed"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire"
        elif not floor_ok:
            weakest = "current_arm_not_at_floor_vacuous_test_risk"

    msg = (f"coverage_gain_pp={cg:.1f} (HARD-PASS needs >=15.0, HARD-FAIL if <5.0) | "
           f"precision_newly_covered={prec:.3f} (HARD-PASS needs >=0.60, HARD-FAIL if <0.50) | "
           f"guard_regression_ok={guard_ok} oos_control_fired={oos_ok} current_coverage_floor_ok={floor_ok} "
           f"(current_coverage_pooled={agg['coverage_current_pooled']:.3f}) | n_newly_covered_pooled="
           f"{agg['n_newly_covered_pooled']}/{agg['total_sentences']} | "
           f"verb_mistagged_uncorrected={agg['n_verb_mistagged_uncorrected_pooled']} "
           f"verb_morph_rescued={agg['n_verb_morph_rescue_pooled']} "
           f"any_wrong_triple_emitted={agg['any_wrong_triple_emitted_pooled']}")
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
# self-test: EXERCISE THE REAL code path + assert the discriminators FIRE (F.1) + the empirically-probed
# mistag/rescue findings ARE reproduced (not just hoped for).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (imported ie_extract, real nltk.pos_tag call, this cell's "
          "ie_extract_verb_extended)...", flush=True)

    # (0) glass-box-legal: no neural imports in THIS file's own source.
    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"

    # (0b) vacuous-test guard: the OOV verb base forms are genuinely NOT in the closed VERB_LEX.
    assert not (set(OOV_VERB_BASE_LEX) & set(VERB_LEX)), \
        "OOV_VERB_BASE_LEX overlaps closed VERB_LEX -- verb-OOV claim would be false / test vacuous"

    # (1) MEASURED@standalone-tagger-probe: the tagger mistag mode is real and reproduces. "eat"-class
    # bare-plural mistag: at least one of the 9 synonym verbs, in a bare-plural-no-determiner frame, tags
    # NN (not VB-family) -- this is the exact condition the VET flagged as now architecturally live.
    tagged = dict(nltk.pos_tag(["Cats", "munch", "seeds", "."]))
    assert tagged["munch"] not in NLTK_VERB_TAGS, \
        f"expected the classical tagger to MISTAG bare-plural 'munch' as non-verb (reproduces the VET's "\
        f"'eat->NN' finding); got {tagged['munch']} -- if this now tags correctly, the mistag-probe corpus "\
        f"needs re-verification against current NLTK model version"
    print(f"[self_test] MEASURED mistag reproduction: 'Cats munch seeds.' -> munch/{tagged['munch']} "\
          f"(non-verb tag, as expected -- the shield-lifted mistag mode)", flush=True)

    # (2) real classical tagger sanity on a correctly-tagged OOV verb (3sg+determiner context).
    tagged2 = dict(nltk.pos_tag(["The", "cat", "munches", "the", "seed", "."]))
    assert tagged2["munches"] in NLTK_VERB_TAGS, f"expected 'munches' (3sg+determiner) to tag VB-family, got {tagged2['munches']}"

    # (2b) morphological suffix-stripper correctly inverts every regular inflection of every OOV verb base.
    for base in OOV_VERB_BASE_LEX:
        for form_fn, expect_form in ((lambda w: w, "base"), (_v3sg, "3sg"), (_vpast, "past_or_participle"), (_vgerund, "gerund")):
            surf = form_fn(base)
            hit = _oov_verb_base_and_form(surf)
            assert hit is not None, f"morphology stripper failed to recover base for {surf!r} (base={base!r})"
            stem, form = hit
            assert stem == OOV_VERB_BASE_LEX[base], f"morphology stripper recovered wrong relation stem for {surf!r}: {stem} != {OOV_VERB_BASE_LEX[base]}"
            assert form == expect_form, f"morphology stripper recovered wrong form for {surf!r}: {form} != {expect_form}"
    print(f"[self_test] morphology stripper PASS on all {len(OOV_VERB_BASE_LEX)} OOV verb bases x 4 inflections", flush=True)

    # (3) discriminator-fires: CURRENT must fully abstain, EXTENDED must extract, on a representative
    # correctly-tagged OOV-verb sentence (3sg+determiner, not the risky bare-plural frame).
    s = "The cat munches the seed."
    cur = ie_extract(s)
    ext = ie_extract_verb_extended(s)
    assert cur[0] == [], f"CURRENT unexpectedly extracted on an OOV-verb sentence: {cur}"
    assert set(ext[0]) == {("cat", "eats", "seed")}, f"EXTENDED failed to extract expected triple: {ext}"

    # (4) morphology-rescue reproduces: a JJ-mistagged OOV verb ('nibble' in bare-plural) is still correctly
    # promoted to VERB via morphology (deferring only to NOUN-family tagger judgments, not ADJ).
    s = "Cats nibble seeds."
    tagged3 = dict(nltk.pos_tag(["Cats", "nibble", "seeds", "."]))
    assert tagged3["nibble"] not in NLTK_VERB_TAGS, f"expected 'nibble' bare-plural to NOT tag VB-family (JJ-class mistag), got {tagged3['nibble']}"
    ext = ie_extract_verb_extended(s)
    assert set(ext[0]) == {("cat", "eats", "seed")}, \
        f"morphology RESCUE failed: expected EXTENDED to still extract (cat,eats,seed) despite the tagger's "\
        f"non-verb mistag on 'nibble' (tag={tagged3['nibble']}); got {ext}"
    print(f"[self_test] morphology-rescue reproduces: 'nibble' mistagged {tagged3['nibble']} by tagger, "\
          f"still correctly promoted to VERB via suffix-stripping", flush=True)

    # (5) architectural safety property: the NN-mistagged bare-plural sentence correctly ABSTAINS (no verb
    # found) rather than emitting a WRONG triple with a spurious noun-filler.
    s = "Cats munch seeds."
    ext = ie_extract_verb_extended(s)
    assert ext[0] == [], f"expected clean abstain (mistag->coverage-loss, not wrong-triple) on {s!r}, got {ext[0]}"
    assert ext[1] == "NO_VERB", f"expected NO_VERB abstain reason on {s!r}, got {ext[1]!r}"
    print(f"[self_test] architectural safety property confirmed: verb-mistag causes clean NO_VERB abstain, "\
          f"not a wrong triple", flush=True)

    # (6) out-of-schema must-fail control: BOTH arms abstain even though the verb is syntactically real.
    for s in OUT_OF_SCHEMA_CONTROL:
        cur = ie_extract(s)
        ext = ie_extract_verb_extended(s)
        assert cur[0] == [], f"CURRENT unexpectedly extracted on out-of-schema control {s!r}: {cur}"
        assert ext[0] == [], f"EXTENDED unexpectedly extracted on out-of-schema control {s!r}: {ext}"

    # (7) guard-class regression: EXTENDED must not corrupt fully closed-lexicon sentences.
    for sent, gold in GUARD_SENTENCES:
        cur = ie_extract(sent)
        ext = ie_extract_verb_extended(sent)
        gset = set(tuple(g) for g in gold)
        assert set(cur[0]) == gset, f"CURRENT guard regression on {sent!r}: {cur[0]} != {gset}"
        assert set(ext[0]) == gset, f"EXTENDED guard regression on {sent!r}: {ext[0]} != {gset}"

    # (8) ARMS-MUST-DIFFER (META_RULE_AF): CURRENT vs EXTENDED accepted-triple-set hash differs on the corpus.
    rows = build_verb_oov_corpus(seed=7, n_per_template=2)
    cur_all = sorted(set(t for r in rows for t in ie_extract(r["sentence"])[0]))
    ext_all = sorted(set(t for r in rows for t in ie_extract_verb_extended(r["sentence"])[0]))
    h_cur = hashlib.sha256(json.dumps(cur_all, sort_keys=True).encode()).hexdigest()
    h_ext = hashlib.sha256(json.dumps(ext_all, sort_keys=True).encode()).hexdigest()
    assert h_cur != h_ext, "META_RULE_AF VIOLATION: CURRENT and POS_EXTENDED produced bit-identical output"
    assert cur_all == [], f"CURRENT unexpectedly non-empty on the tiny self-test OOV-verb corpus: {cur_all}"
    assert len(ext_all) > 0, "POS_EXTENDED produced zero triples on the tiny self-test corpus -- mechanism did not fire"

    # (9) real_code_path (F.1): the full run_seed loop, tiny scale, exercising every entrypoint for real.
    r = run_seed(seed=7, n_per_template=2)
    assert r["coverage_current"] == 0.0, f"real_code_path smoke: CURRENT coverage should be 0.0, got {r['coverage_current']}"
    assert r["coverage_extended"] > 0.0, f"real_code_path smoke: EXTENDED coverage should be > 0, got {r['coverage_extended']}"
    assert not r["any_wrong_triple_emitted"], "real_code_path smoke: a WRONG triple was emitted (architectural safety property violated)"
    assert r["rung2_coverage_on_this_corpus"] == 0.0, \
        f"incrementality control: RUNG 2's noun-only mechanism should NOT cover any verb-OOV sentence, got {r['rung2_coverage_on_this_corpus']}"

    # (10) mixed OOV (noun+verb) diagnostic lemma-reduction sanity (non-gating, just confirms it runs cleanly).
    for s, g, c in MIXED_OOV_DIAGNOSTIC:
        ext = ie_extract_verb_extended(s)
        print(f"[self_test] mixed_oov_diagnostic[{c}]: extended={ext[0]} gold={g}", flush=True)

    print(f"[self_test] PASS | tiny-corpus coverage_current={r['coverage_current']:.2f} "
          f"coverage_extended={r['coverage_extended']:.2f} coverage_gain_pp={r['coverage_gain_pp']:.1f} "
          f"precision_newly_covered={r['precision_newly_covered']} n_newly_covered={r['n_newly_covered']}", flush=True)
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
    print(f"[oov_verb_extension] run_mode={run_mode} seeds={seeds} n_per_template={N_PER_TEMPLATE} "
          f"n_templates={len(TEMPLATES)} expected_n_units={expected_n_units}", flush=True)

    agg = aggregate_seeds(seeds, N_PER_TEMPLATE)
    print(f"[oov_verb_extension] coverage_current_pooled={agg['coverage_current_pooled']:.3f} "
          f"coverage_extended_pooled={agg['coverage_extended_pooled']:.3f} "
          f"coverage_gain_pp_pooled={agg['coverage_gain_pp_pooled']:.1f} "
          f"precision_newly_covered_pooled={agg['precision_newly_covered_pooled']} "
          f"verb_mistagged_uncorrected={agg['n_verb_mistagged_uncorrected_pooled']} "
          f"verb_morph_rescued={agg['n_verb_morph_rescue_pooled']}", flush=True)

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
        "metric_n_verb_tagger_pooled": agg["n_verb_tagger_pooled"],
        "metric_n_verb_morph_rescue_pooled": agg["n_verb_morph_rescue_pooled"],
        "metric_n_verb_tagger_and_morph_pooled": agg["n_verb_tagger_and_morph_pooled"],
        "metric_n_verb_unresolved_pooled": agg["n_verb_unresolved_pooled"],
        "metric_n_verb_mistagged_uncorrected_pooled": agg["n_verb_mistagged_uncorrected_pooled"],
        "metric_any_wrong_triple_emitted_pooled": agg["any_wrong_triple_emitted_pooled"],
        "metric_rung2_coverage_on_this_corpus_pooled": agg["rung2_coverage_on_this_corpus_pooled"],
        "per_seed_summary": agg["per_seed_summary"],
        "mixed_oov_diagnostic": agg["per_seed_full"][0]["mixed_oov_diagnostic"],
        "arms": {
            "CURRENT": {"coverage": agg["coverage_current_pooled"]},
            "POS_EXTENDED": {"coverage": agg["coverage_extended_pooled"],
                              "precision_newly_covered": agg["precision_newly_covered_pooled"]},
        },
        "prereg": {
            "hard_pass": "coverage_gain_pp_pooled>=15.0 AND precision_newly_covered_pooled>=0.60 AND "
                         "guard_regression_ok AND oos_control_fired AND current_coverage_floor_ok",
            "hard_fail": "coverage_gain_pp_pooled<5.0 OR precision_newly_covered_pooled<0.50",
            "corpus": "12 hand-authored template classes x N_PER_TEMPLATE random verb/noun draws per seed, "
                      "OOV verb base forms confirmed disjoint from closed VERB_LEX",
            "scope_note": "nouns held CLOSED (never OOV) in the PRIMARY corpus -- isolates the OOV-VERB "
                          "axis, mirroring RUNG 2's own noun-axis isolation. A SECONDARY non-gating "
                          "MIXED_OOV_DIAGNOSTIC combines OOV nouns (RUNG 2 pools) with OOV verbs.",
            "compute_architecture": "sequential-CPU; pure syntactic parsing, no VSA store; wall time trivial "
                                    "(MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer test, no FoundationStore/KGStore touched)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract (imported, unmodified)", "_extract_core (imported from "
                                         "RUNG 2, itself parity-proven against v2)", "nltk.pos_tag (real "
                                         "classical averaged-perceptron call)", "ie_extract_verb_extended "
                                         "(this cell)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete syntactic role-assignment + "
                       "the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED) on "
                       "this corpus's specific verb tokens (MEASURED via standalone pre-design tagger probe)",
            "glass_box_legal": "no torch/spacy/transformers/stanza imports in this file (source-scanned at "
                               "self-test); nltk averaged_perceptron_tagger_eng is classical, non-neural",
            "prior_work_check": "substrate_query.sh top hit cosine=0.3008 ('inflectional_morphology', a "
                                "WordNet lexical-concept entry, NOT a prior arc EXPERIMENT CELL) -- no prior "
                                "cell at cosine>0.30; genuinely novel cell design, not a rediscovery.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[oov_verb_extension] {tier} in {elapsed:.2f}s -> {out_dir / 'metrics.json'}", flush=True)
    print(f"[oov_verb_extension] {msg}", flush=True)
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
