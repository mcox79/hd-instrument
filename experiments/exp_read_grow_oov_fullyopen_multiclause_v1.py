"""exp_read_grow_oov_fullyopen_multiclause_v1 -- RUNG 4 of the open-text glass-box reading curriculum: the
honest culmination. Fully-open register (OOV NOUNS AND OOV VERBS together) PLUS the hard multi-clause
templates (VP-coordination, compound-subject, relative clause, passive) that RUNG 2 and RUNG 3 deliberately
EXCLUDED from their primary corpora to isolate one axis at a time. This cell removes that isolation.

TRIGGER (two VETs converged on this exact next step, verbatim from the dispatching contract):
  - RUNG 3's own landed finding + VET: RUNG 3's precision=1.000 was near-certain BECAUSE its primary corpus had
    no VP-coordination / compound-subject templates; RUNG 3's OWN adversarial probe "The owl munches the seed
    and eats the bread." broke even the BASELINE (CURRENT, zero-extension) arm -- VP-coordination + an
    intervening OOV verb produces a WRONG triple, not a clean abstain. RUNG 3 set this cell's expansion
    criterion verbatim: "fully-open register (OOV nouns AND OOV verbs simultaneously in the primary corpus,
    plus VP-coordination/compound-subject templates ...) -- that is where the corrected classical envelope's
    lower P:60-85%/R:30-55% range should actually start to bind."
  - notes/research_open_text_glassbox_ie_reading_frontier_curriculum_2026-07-16.md: the corrected classical
    envelope is P:60-85%/R:30-55%; classical Open-IE (ClausIE/OLLIE) tops out at R~0.496 on CaRB.

MEASURED PRE-DESIGN MECHANISM PROBE (standalone runs of the REAL imported `ie_extract` / `ie_extract_verb_extended`
against candidate sentences, run before corpus design -- not hypothesized; see self_test for the reproducible
subset). Confirms the VET's prediction and finds TWO further, more precise failure mechanisms:

  MECHANISM 1 (reproduces the VET's own probe, CURRENT arm): `_extract_core` (imported unmodified from RUNG 2,
  itself imported unmodified from v2) computes `subj_region = [i for i in noun_idx if i < matrix_vi]` -- ALL
  noun tokens before the recognized matrix verb, not just those in the local clause. When a VP-coordination
  sentence's FIRST verb is invisible (OOV to the closed VERB_LEX, e.g. "munches"), the first clause's OBJECT
  noun ("seed") falls INSIDE the subject-region computed for the SECOND, recognized verb ("eats"), and
  `_split_coord` (no direct "and"-adjacency between the two nouns, since an invisible-verb token sits between
  them) falls back to "nearest noun" -> the wrong noun becomes the subject. MEASURED: "The owl munches the seed
  and eats the bread." -> CURRENT emits [('seed', 'eats', 'bread')] -- a WRONG triple (self_test (1)).

  MECHANISM 2 (NEW finding this cell adds, EXTENDED arm): RUNG 3's `_classify_unk_token` (imported, reused
  verbatim) ALSO promotes an UNK token to NOUN when the tagger says a noun-family tag (mirrors RUNG 2's own
  mechanism). In a SINGLE-clause sentence this was harmless (RUNG 3's `verb_idx`-first immediate-return safety
  property: if the ONLY verb token in the sentence mistags to NOUN, `verb_idx` is simply empty and the function
  returns NO_VERB before any noun-collection runs). But in a VP-COORDINATION sentence with a SECOND, correctly
  recognized verb, `verb_idx` is NOT empty -- so the immediate-return safety property does not fire, and the
  spuriously-NOUN-promoted verb-1 token gets swept into `subj_region` (or, in some draws, into the object-
  coordination chain after "and") for the surviving verb. This means the SAME combined noun+verb promotion
  mechanism that made RUNG 3's isolated corpus safe now, on a genuinely fully-open + multi-clause corpus,
  ITSELF becomes a wrong-triple-producing pathway -- not merely a coverage-loss abstain. MEASURED: "Cats munch
  seeds and eat bread." -> BOTH CURRENT and EXTENDED emit [('seed', 'eats', 'bread')] -- EXTENDED does NOT
  rescue this case (self_test (2)); "Rabbits munch carrots and hunt goats." -> EXTENDED emits
  [('rabbit','eats','carrot'), ('rabbit','eats','hunt')] -- a SECOND, distinct wrong-triple shape: the
  spuriously-promoted-to-NOUN "hunt" token gets swallowed by the OBJECT-coordination chain ("...and NOUN") of
  the FIRST clause's verb, producing a nonsense triple with a verb-lemma as the object (self_test (3)).

  MECHANISM 3 (a genuine SAFETY finding, not a bug): when BOTH coordinated verbs mistag to a noun-family tag
  (neither promotes to VERB), `verb_idx` becomes fully empty again and the immediate-return property DOES fire
  -- a clean NO_VERB abstain in EXTENDED, not a wrong triple. MEASURED: "Squirrels munch acorns and stalk
  badgers." -> BOTH arms emit [] / NO_VERB (self_test (4)). So the wrong-triple hazard in EXTENDED is
  conditional: it fires specifically when exactly one of the two coordinated verbs is recognized (closed OR
  correctly-tagged-OOV) while the other mistags to a noun-family tag -- not when both fail together.

REUSE (4-layer composition, zero new promotion/grammar logic -- the entire novelty of this cell is the CORPUS,
not the mechanism): imports v2's `ie_extract` (CURRENT arm, unmodified) and RUNG 3's `ie_extract_verb_extended`
(FULLY_EXTENDED arm, unmodified -- RUNG 3 already composed RUNG 2's noun-OOV promotion + its own verb-OOV
promotion into `_classify_unk_token`; this cell does not touch that logic at all). Also imports RUNG 2's OOV
noun pools and RUNG 3's OOV verb pool + verb-form helpers, all verbatim.

GLASS-BOX-LEGAL (verified, no LLM, no neural net anywhere in the import chain -- see
`_grep_confirm_no_neural_imports` below, same discipline as v2/RUNG 2/RUNG 3, PLUS a runtime sys.modules
transitive-closure check per the contract's ask for a stronger guard than the prior rungs used).

CORPUS (hand-authored generator; SCOPE DECISION -- declared honestly, not hidden): the contract's strong
preference is real prose (OneStopEnglish / Simple-Wikipedia) with hand-aligned gold triples. Given this is a
single exp_dev cycle (COMPUTE-PROPORTIONALITY discipline) and real-prose gold-triple curation at sufficient
scale for a stable pooled precision/recall estimate is a genuinely larger undertaking (corpus sourcing +
licensing check + hand-alignment + register filtering), this cell uses the CONTRACT'S EXPLICITLY OFFERED bridge:
hand-authored FULLY-OPEN MULTI-CLAUSE templates, deliberately INCLUDING every hard case that breaks the
verb_idx-first safety property (per contract: "you MUST include the hard cases ... the drop is the deliverable").
This is declared explicitly, matching RUNG 2/RUNG 3's own precedent of hand-authored corpora over real-prose
sourcing at this stage of the curriculum. Real-prose + gold-alignment remains the natural RUNG 5 extension (see
module-end NEXT note).

9 template classes x N_PER_TEMPLATE random draws x 3 seeds:
  EASY/sanity (fully-open, single-clause -- confirms the base composition still works at corpus scale, not
  just RUNG 3's small 6-sentence MIXED_OOV_DIAGNOSTIC): simple_svo_fully_open, compound_subject_all_oov,
  compound_subject_mixed_closed_oov, relative_clause_all_oov, passive_all_oov.
  HARD (the deliverable -- genuinely breaking VP-coordination, NOT engineered to dodge the break):
  vp_coord_closed_nouns_safe_frame (MECHANISM 1, closed nouns force the bleed deterministically regardless of
  tagger draw), vp_coord_closed_nouns_bare_plural (MECHANISM 2, the headline finding -- EXTENDED does NOT
  rescue), vp_coord_all_oov_safe_frame, vp_coord_all_oov_bare_plural (organic MECHANISM 2/3 mix, not hand-
  picked -- real random-draw variance reported as-measured).

METRICS (upgraded scoring vs RUNG 2/3, per this cell's own mechanism finding that CURRENT can now itself emit
WRONG triples, not just abstain -- RUNG 2/3's `precision_newly_covered` metric implicitly assumed CURRENT never
covers-wrongly and would silently EXCLUDE a CURRENT-also-wrong sentence from grading (since "newly_covered"
requires CURRENT to be UNcovered). Reporting only that narrower metric here would UNDER-COUNT the wrong-triple
problem this cell exists to expose. This cell therefore computes a TRIPLE-LEVEL, whole-corpus precision/recall
(CaRB-style, matching the research note's own evaluation convention) as the PRIMARY discriminator, and reports
`precision_newly_covered_pooled` alongside for cross-rung comparability, not as the gate.):
  - precision_extended_overall = (extended triples that are in gold) / (all extended triples emitted), pooled
    over the WHOLE corpus (every row, not just newly-covered rows).
  - recall_extended = (extended triples that are in gold) / (total gold triples across the whole corpus).
  - current_precision_overall / current_recall -- same computation for CURRENT, reported for contrast (this is
    itself a headline finding: CURRENT's precision is no longer 1.0 either, once VP-coordination is present).
  - coverage_gain_pp_pooled -- sentence-level coverage gain (kept for continuity with RUNG 2/3 and as the
    contract's literal "coverage/recall gain" band variable).
  - per_class breakdown: n / cur_wrong / cur_abstain / cur_correct / ext_wrong / ext_abstain / ext_correct,
    per template class -- answers "WHERE precision drops."

BANDS (pre-committed; per contract verbatim, precision-favoring/recall-limited per the corrected classical
envelope): HARD-PASS: precision_extended_overall_pooled >= 0.60 AND coverage_gain_pp_pooled >= 15.0 AND
guard_regression_ok AND oos_control_fired AND recall_improves_over_baseline_ok. HARD-FAIL:
precision_extended_overall_pooled < 0.50 OR coverage_gain_pp_pooled < 5.0. MIDDLE_BAND: otherwise.
`recall_improves_over_baseline_ok` (recall_extended_pooled > recall_current_pooled) REPLACES RUNG 2/3's
`current_coverage_floor_ok` vacuous-test guard -- CURRENT is NOT expected to be near-zero-coverage on this
corpus (MECHANISM 1 means CURRENT actively mis-fires, not just silently abstains, on several hard template
classes); the discriminator-fires check appropriate here is "the mechanism still nets a real recall gain despite
the new failure surface," not "current never covers." This substitution is declared, not silent.

HONEST FRAMING (per contract): precision IS expected to drop below 1.0 here -- that is the deliverable, not a
failure. HARD-FAIL only triggers on a genuine collapse below the classical floor or negligible coverage gain.

Local numpy + nltk, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (pure syntactic parsing over a small
corpus; wall time trivial, MEASURED below). No VSA store touched. progress_logging = print_flush_true (not
required at timeout_s < 1800, included for parity). Dispatch: COMPUTE-PROPORTIONALITY, runs INLINE/FOREGROUND
locally (matches RUNG 2/3 precedent; local re-authorized 2026-07-15 for judicious parallel priority work -- this
is a trivial-wall-time parser cell, no queue needed). Pause flag `data/orchestrator_paused.flag` re-checked
absent immediately before this run.

NEXT (RUNG 5, not this cell): real-prose sourcing (OneStopEnglish / Simple-Wikipedia elementary slice) with
hand-aligned gold triples, evaluated against this same discriminator family, to move off hand-authored templates
entirely -- the natural conclusion of the "real prose is the honest target" thread this cell's docstring flags
but does not attempt (COMPUTE-PROPORTIONALITY: that is a corpus-sourcing task, not a single-cycle cell-author
task).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; CURRENT vs FULLY_EXTENDED accepted-triple-set hash
#   differs on the primary fully-open corpus by construction).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor -- discriminator is discrete syntactic role-assignment + a classical
#   POS tagger's own (externally benchmarked, 96-97% PTB, CITED@research note sec 3) categorical accuracy on
#   THIS corpus's specific tokens (empirically probed via standalone runs against the REAL imported extractors,
#   MEASURED not guessed -- see module docstring MECHANISM 1-3 and self_test).
# - baseline_in_band: N/A BY DESIGN, REPLACED -- see `recall_improves_over_baseline_ok` in module docstring
#   (CURRENT is NOT expected near-floor on this corpus; that itself is a reported finding, MECHANISM 1).
# - discriminator survives scale: corpus is FIXED-size (hand-authored templates x random draws). Smoke uses the
#   SAME template set + SAME N_PER_TEMPLATE as FULL (Option A) -- trivial wall time makes this free.
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test calls the REAL `nltk.pos_tag`, the REAL imported `ie_extract` (v2), and the
#   REAL imported `ie_extract_verb_extended` (RUNG 3, itself composing RUNG 2's `_extract_core`) -- zero new
#   grammar/promotion code in this cell; all three MECHANISM findings reproduced live at self-test, not asserted.
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19]; random.Random(seed) (never hash()); sorted() used
#   for all set->list conversions in metrics; no list(set(...)) ordering dependence.
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics / CITED@research-note /
#   MEASURED@standalone-mechanism-probe (this cell's own pre-design empirical runs against the real extractors).
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

ANCHOR_NAME = "read_grow_oov_fullyopen_multiclause_v1"

# --- GENUINE 4-LAYER REUSE: v2 (grammar+lexicon), RUNG 2 (noun-OOV pools), RUNG 3 (verb-OOV pools + the
# ALREADY-composed noun+verb `ie_extract_verb_extended`) -- all imported verbatim, none edited, no new grammar
# or promotion logic written in this cell. ---
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import (  # noqa: E402
    ADJS, ENTITIES, RELATIONS, ANIMALS, FOODS, PLACES, VERB_LEX,
    _tag_token, _tokenize, _resolve_relation, _split_coord, ie_extract,
)
from experiments.exp_read_grow_oov_pos_extension_v1 import (  # noqa: E402
    OOV_ANIMALS, OOV_FOODS, OOV_PLACES, _pluralize,
)
from experiments.exp_read_grow_oov_verb_extension_v1 import (  # noqa: E402
    OOV_VERB_BASE_LEX, EATS_VERBS, CHASES_VERBS, LIVE_VERBS,
    ANIMALS_BARE_SAFE, _v3sg, _vpast, ie_extract_verb_extended,
)

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only; see glass-box-legal note above.

# bare-plural-safe subsets: proactive corpus-GENERATION-artifact avoidance (same class as RUNG 2's
# "moss"->"mosss" catch / RUNG 3's fish/mouse exclusion), NOT a mistag-mode dodge -- the risky VERBS and the
# hard TEMPLATE STRUCTURES are never filtered, only irregular-plural nouns the reused `_pluralize` helper
# (regular -s/-es only) cannot handle correctly. "deer" (invariant plural) excluded from OOV_ANIMALS;
# "leaf" (leaf->leaves) and "berry" (berry->berries, -y ending not handled by `_pluralize`) excluded from
# OOV_FOODS.
OOV_ANIMALS_BARE_SAFE = [a for a in OOV_ANIMALS if a != "deer"]
OOV_FOODS_BARE_SAFE = [f for f in OOV_FOODS if f not in ("leaf", "berry")]


def _pick(rng, pool):
    return pool[rng.randrange(len(pool))]


# ---------------------------------------------------------------------------
# PRIMARY corpus: 9 template classes. EASY (sanity, single-clause, fully-open) + HARD (multi-clause, the
# deliverable). Nouns/verbs drawn from the FULL applicable pools each time -- not restricted to "safe" draws.
# ---------------------------------------------------------------------------
def _t_simple_svo_fully_open(rng):
    a = _pick(rng, OOV_ANIMALS)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, OOV_FOODS)
    return f"The {a} {_v3sg(v)} the {f}.", [(a, "eats", f)], "simple_svo_fully_open"


def _t_compound_subject_all_oov(rng):
    a1 = _pick(rng, OOV_ANIMALS)
    a2 = _pick(rng, OOV_ANIMALS)
    while a2 == a1:
        a2 = _pick(rng, OOV_ANIMALS)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, OOV_FOODS)
    gold = sorted({(a1, "eats", f), (a2, "eats", f)})
    return f"The {a1} and the {a2} {v} the {f}.", gold, "compound_subject_all_oov"


def _t_compound_subject_mixed_closed_oov(rng):
    a1 = _pick(rng, ANIMALS)
    a2 = _pick(rng, OOV_ANIMALS)
    v = _pick(rng, EATS_VERBS)
    f = _pick(rng, OOV_FOODS)
    gold = sorted({(a1, "eats", f), (a2, "eats", f)})
    return f"The {a1} and the {a2} {v} the {f}.", gold, "compound_subject_mixed_closed_oov"


def _t_relative_clause_all_oov(rng):
    a1 = _pick(rng, OOV_ANIMALS)
    a2 = _pick(rng, OOV_ANIMALS)
    while a2 == a1:
        a2 = _pick(rng, OOV_ANIMALS)
    vrc = _pick(rng, CHASES_VERBS)
    vmat = _pick(rng, LIVE_VERBS)
    p = _pick(rng, OOV_PLACES)
    sent = f"The {a1} that {_v3sg(vrc)} the {a2} {_v3sg(vmat)} in the {p}."
    # gold = MATRIX relation only -- pre-existing v2/RUNG2 scope (relative-clause's own embedded relation is
    # out of scope for this single-matrix-verb-per-sentence grammar design; not a NEW limitation this cell adds).
    return sent, [(a1, "lives_in", p)], "relative_clause_all_oov"


def _t_passive_all_oov(rng):
    a = _pick(rng, OOV_ANIMALS)
    f = _pick(rng, OOV_FOODS)
    v = _pick(rng, EATS_VERBS)
    return f"The {f} is {_vpast(v)} by the {a}.", [(a, "eats", f)], "passive_all_oov"


def _t_vp_coord_closed_nouns_safe_frame(rng):
    """MECHANISM 1 template: closed nouns force the CURRENT-arm bleed DETERMINISTICALLY (structural, not
    tagger-dependent -- CURRENT never sees verb1 at all, closed or not). verb1 OOV (3sg+determiner frame,
    empirically the SAFE frame for EXTENDED per RUNG 3's own probe); verb2 CLOSED ("chases", always
    recognized). MEASURED@standalone-mechanism-probe: CURRENT wrong 100% of draws on this template shape
    (structural); EXTENDED correct-but-incomplete on almost all draws (verb1 tags VBZ reliably in this frame)."""
    a = _pick(rng, ANIMALS)
    a2 = _pick(rng, ANIMALS)
    while a2 == a:
        a2 = _pick(rng, ANIMALS)
    f = _pick(rng, FOODS)
    v1 = _pick(rng, EATS_VERBS)
    sent = f"The {a} {_v3sg(v1)} the {f} and {_v3sg('chase')} the {a2}."
    gold = sorted({(a, "eats", f), (a, "chases", a2)})
    return sent, gold, "vp_coord_closed_nouns_safe_frame"


def _t_vp_coord_closed_nouns_bare_plural(rng):
    """MECHANISM 2 template (the headline finding): closed bare-plural-safe nouns, verb1 OOV bare-plural (the
    mistag-prone frame per RUNG 3's own probe: munch/pursue/hunt->NN, nibble/gobble->JJ-rescued,
    devour/dwell/stalk/reside->VBP-correct), verb2 CLOSED bare form ("chase"). MEASURED@standalone-mechanism-
    probe: "Cats munch seeds and chase dogs." -> BOTH CURRENT and EXTENDED emit [('seed','chases','dog')] --
    EXTENDED does NOT rescue this case; the spurious noun-promotion of the mistagged verb1 poisons subj_region
    for the surviving closed verb2, exactly as it does for CURRENT."""
    a = _pick(rng, ANIMALS_BARE_SAFE)
    a2 = _pick(rng, ANIMALS_BARE_SAFE)
    while a2 == a:
        a2 = _pick(rng, ANIMALS_BARE_SAFE)
    f = _pick(rng, FOODS)
    v1 = _pick(rng, EATS_VERBS)
    sent = f"{_pluralize(a).capitalize()} {v1} {_pluralize(f)} and chase {_pluralize(a2)}."
    gold = sorted({(a, "eats", f), (a, "chases", a2)})
    return sent, gold, "vp_coord_closed_nouns_bare_plural"


def _t_vp_coord_all_oov_safe_frame(rng):
    """Fully-open (both nouns+verbs OOV), 3sg+determiner frame both clauses -- the "should be the safest hard
    case" template. MEASURED@standalone-mechanism-probe: CURRENT cleanly abstains (NO_VERB, no closed anchors
    at all -- no bleed risk since nothing is visible to it). EXTENDED result varies by draw (organic, not
    hand-picked): most draws get clause-1-only correct-but-incomplete; SOME draws (verb2 mistags even in this
    frame, e.g. "dwells" after "and" in one probed draw) still produce a MECHANISM-2-class wrong triple --
    reported as-measured, not assumed uniformly safe."""
    a = _pick(rng, OOV_ANIMALS)
    a2 = _pick(rng, OOV_ANIMALS)
    while a2 == a:
        a2 = _pick(rng, OOV_ANIMALS)
    f = _pick(rng, OOV_FOODS)
    v1 = _pick(rng, EATS_VERBS)
    v2 = _pick(rng, CHASES_VERBS)
    sent = f"The {a} {_v3sg(v1)} the {f} and {_v3sg(v2)} the {a2}."
    gold = sorted({(a, "eats", f), (a, "chases", a2)})
    return sent, gold, "vp_coord_all_oov_safe_frame"


def _t_vp_coord_all_oov_bare_plural(rng):
    """Fully-open (both nouns+verbs OOV), bare-plural both clauses -- the maximally-hard template, organic
    MECHANISM 2/3 mix (not hand-picked): MEASURED@standalone-mechanism-probe draws show a real mix of (a) both
    verbs mistag to noun-family -> clean NO_VERB abstain in EXTENDED (MECHANISM 3, safe), (b) verb1 rescued
    (tagger/morph) + verb2 mistags -> spurious-object wrong triple in EXTENDED (MECHANISM 2), (c) rarely both
    tag correctly -> fully correct 2-triple extraction. All three outcomes are left free to occur; the pooled
    rate across random draws is the honest measurement."""
    a = _pick(rng, OOV_ANIMALS_BARE_SAFE)
    a2 = _pick(rng, OOV_ANIMALS_BARE_SAFE)
    while a2 == a:
        a2 = _pick(rng, OOV_ANIMALS_BARE_SAFE)
    f = _pick(rng, OOV_FOODS_BARE_SAFE)
    v1 = _pick(rng, EATS_VERBS)
    v2 = _pick(rng, CHASES_VERBS)
    sent = f"{_pluralize(a).capitalize()} {v1} {_pluralize(f)} and {v2} {_pluralize(a2)}."
    gold = sorted({(a, "eats", f), (a, "chases", a2)})
    return sent, gold, "vp_coord_all_oov_bare_plural"


TEMPLATES = [
    _t_simple_svo_fully_open,
    _t_compound_subject_all_oov,
    _t_compound_subject_mixed_closed_oov,
    _t_relative_clause_all_oov,
    _t_passive_all_oov,
    _t_vp_coord_closed_nouns_safe_frame,
    _t_vp_coord_closed_nouns_bare_plural,
    _t_vp_coord_all_oov_safe_frame,
    _t_vp_coord_all_oov_bare_plural,
]
HARD_TEMPLATE_NAMES = {
    "vp_coord_closed_nouns_safe_frame", "vp_coord_closed_nouns_bare_plural",
    "vp_coord_all_oov_safe_frame", "vp_coord_all_oov_bare_plural",
}
N_PER_TEMPLATE = 8  # same for smoke and FULL (Option A discriminator-survives-scale; trivial wall time)


def build_fullyopen_corpus(seed, n_per_template=N_PER_TEMPLATE):
    """FIXED-seed random.Random (F.5 -- never hash()); dedupes within a template's instances."""
    rng = random.Random(seed)
    rows = []
    for tmpl in TEMPLATES:
        seen = set()
        made = 0
        tries = 0
        while made < n_per_template and tries < n_per_template * 40:
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


# guard corpus: fully closed lexicon (no OOV anywhere), including ONE closed VP-coordination sentence to show
# the matrix-only-clause scope limit is PRE-EXISTING (v2/RUNG2 grammar design), not introduced by this cell.
GUARD_SENTENCES = [
    ("The cat eats the seed.", [("cat", "eats", "seed")]),
    ("The dog chases the cow.", [("dog", "chases", "cow")]),
    ("The frog lives in the pond.", [("frog", "lives_in", "pond")]),
    ("The bread is eaten by the mouse.", [("mouse", "eats", "bread")]),
    ("The cat and the dog eat the bread.", sorted({("cat", "eats", "bread"), ("dog", "eats", "bread")})),
    ("The cat eats the seed and chases the mouse.", [("cat", "eats", "seed")]),
]

# out-of-schema control: a verb genuinely absent from BOTH the closed VERB_LEX and OOV_VERB_BASE_LEX, including
# a MULTI-CLAUSE OOS control -- BOTH arms MUST abstain even in coordination.
OUT_OF_SCHEMA_CONTROL = [
    "The cat sleeps in the barn.",
    "The dog yawns near the tree.",
    "The cat sleeps in the barn and yawns near the tree.",
]


def _grep_confirm_no_neural_imports():
    """Static source-scan (glass-box-legal discipline, matches v2/RUNG 2/RUNG 3's own convention): this cell's
    own source must not import torch/spacy/transformers/stanza."""
    src = Path(__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(import|from)\s+(torch|spacy|transformers|stanza)\b", re.MULTILINE)
    hits = [m.group(0).strip() for m in pattern.finditer(src)]
    return hits


def _runtime_neural_module_check():
    """RUNTIME transitive-closure check (stronger than the static source-scan; catches a neural dependency
    pulled in transitively by nltk or any imported module, not just this file's own import statements) -- per
    the contract's explicit ask to add the sys.modules check the Rung-3 VET used. Call AFTER all imports +
    at least one nltk.pos_tag() call (nltk lazy-loads some submodules on first use)."""
    banned = ("torch", "spacy", "transformers", "stanza")
    hits = sorted(m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in banned))
    return hits


# ---------------------------------------------------------------------------
# Evaluation. Triple-level: track wrong/abstain/correct per row for BOTH arms (per-class breakdown answers
# "WHERE precision drops").
# ---------------------------------------------------------------------------
def evaluate_row(row):
    sent = row["sentence"]
    gold = set(tuple(g) for g in row["gold"])
    cur_triples, cur_rule, cur_fail = ie_extract(sent)
    ext_triples, ext_rule, ext_fail, counts = ie_extract_verb_extended(sent)
    cur_set = set(cur_triples)
    ext_set = set(ext_triples)
    cur_correct = cur_set & gold
    ext_correct = ext_set & gold
    return {
        "sentence": sent, "cls": row["cls"], "gold": sorted(gold),
        "current_triples": sorted(cur_set), "current_covered": bool(cur_set), "current_rule": cur_rule,
        "extended_triples": sorted(ext_set), "extended_covered": bool(ext_set), "extended_rule": ext_rule,
        "promo_counts": counts,
        "newly_covered": bool(ext_set) and not bool(cur_set),
        "current_wrong": bool(cur_set) and (cur_set != cur_correct),
        "extended_wrong": bool(ext_set) and (ext_set != ext_correct),
        "n_gold": len(gold), "n_cur_correct": len(cur_correct), "n_cur_emitted": len(cur_set),
        "n_ext_correct": len(ext_correct), "n_ext_emitted": len(ext_set),
    }


def run_seed(seed, n_per_template=N_PER_TEMPLATE):
    rows = build_fullyopen_corpus(seed, n_per_template)
    results = [evaluate_row(r) for r in rows]
    n = len(results)

    coverage_current = sum(r["current_covered"] for r in results) / n
    coverage_extended = sum(r["extended_covered"] for r in results) / n
    coverage_gain_pp = (coverage_extended - coverage_current) * 100.0

    newly = [r for r in results if r["newly_covered"]]
    n_emitted_newly = sum(r["n_ext_emitted"] for r in newly)
    n_correct_newly = sum(r["n_ext_correct"] for r in newly)
    precision_newly = (n_correct_newly / n_emitted_newly) if n_emitted_newly else None

    total_gold = sum(r["n_gold"] for r in results)
    total_cur_emitted = sum(r["n_cur_emitted"] for r in results)
    total_cur_correct = sum(r["n_cur_correct"] for r in results)
    total_ext_emitted = sum(r["n_ext_emitted"] for r in results)
    total_ext_correct = sum(r["n_ext_correct"] for r in results)

    precision_current_overall = (total_cur_correct / total_cur_emitted) if total_cur_emitted else None
    recall_current = total_cur_correct / total_gold
    precision_extended_overall = (total_ext_correct / total_ext_emitted) if total_ext_emitted else None
    recall_extended = total_ext_correct / total_gold

    n_current_wrong = sum(r["current_wrong"] for r in results)
    n_extended_wrong = sum(r["extended_wrong"] for r in results)

    per_class = {}
    for r in results:
        c = per_class.setdefault(r["cls"], {"n": 0, "cur_wrong": 0, "cur_correct_only": 0, "cur_abstain": 0,
                                             "ext_wrong": 0, "ext_correct_only": 0, "ext_abstain": 0})
        c["n"] += 1
        if r["current_wrong"]:
            c["cur_wrong"] += 1
        elif r["current_covered"]:
            c["cur_correct_only"] += 1
        else:
            c["cur_abstain"] += 1
        if r["extended_wrong"]:
            c["ext_wrong"] += 1
        elif r["extended_covered"]:
            c["ext_correct_only"] += 1
        else:
            c["ext_abstain"] += 1

    guard_rows = [evaluate_row({"sentence": s, "gold": g, "cls": "guard"}) for (s, g) in GUARD_SENTENCES]
    guard_current_ok = all(r["current_covered"] and set(r["current_triples"]) == set(tuple(x) for x in r["gold"])
                            for r in guard_rows)
    guard_extended_ok = all(r["extended_covered"] and set(r["extended_triples"]) == set(tuple(x) for x in r["gold"])
                             for r in guard_rows)

    oos_current_abstains = all(not evaluate_row({"sentence": s, "gold": [], "cls": "oos"})["current_covered"]
                                for s in OUT_OF_SCHEMA_CONTROL)
    oos_extended_abstains = all(not evaluate_row({"sentence": s, "gold": [], "cls": "oos"})["extended_covered"]
                                 for s in OUT_OF_SCHEMA_CONTROL)

    hard_rows = [r for r in results if r["cls"] in HARD_TEMPLATE_NAMES]
    any_wrong_on_hard = any(r["current_wrong"] or r["extended_wrong"] for r in hard_rows)

    return {
        "seed": seed, "n_sentences": n,
        "coverage_current": coverage_current, "coverage_extended": coverage_extended,
        "coverage_gain_pp": coverage_gain_pp,
        "n_newly_covered": len(newly),
        "n_emitted_newly": n_emitted_newly, "n_correct_newly": n_correct_newly,
        "precision_newly_covered": precision_newly,
        "total_gold": total_gold,
        "total_cur_emitted": total_cur_emitted, "total_cur_correct": total_cur_correct,
        "total_ext_emitted": total_ext_emitted, "total_ext_correct": total_ext_correct,
        "precision_current_overall": precision_current_overall, "recall_current": recall_current,
        "precision_extended_overall": precision_extended_overall, "recall_extended": recall_extended,
        "n_current_wrong": n_current_wrong, "n_extended_wrong": n_extended_wrong,
        "per_class": per_class,
        "guard_current_ok": guard_current_ok, "guard_extended_ok": guard_extended_ok,
        "oos_current_abstains": oos_current_abstains, "oos_extended_abstains": oos_extended_abstains,
        "any_wrong_on_hard_templates": any_wrong_on_hard,
        "results": results,
    }


def aggregate_seeds(seeds, n_per_template=N_PER_TEMPLATE):
    per_seed = [run_seed(s, n_per_template) for s in seeds]
    total_sentences = sum(r["n_sentences"] for r in per_seed)

    coverage_current_pooled = sum(r["coverage_current"] * r["n_sentences"] for r in per_seed) / total_sentences
    coverage_extended_pooled = sum(r["coverage_extended"] * r["n_sentences"] for r in per_seed) / total_sentences
    coverage_gain_pp_pooled = (coverage_extended_pooled - coverage_current_pooled) * 100.0

    n_emitted_newly_pooled = sum(r["n_emitted_newly"] for r in per_seed)
    n_correct_newly_pooled = sum(r["n_correct_newly"] for r in per_seed)
    precision_newly_covered_pooled = (n_correct_newly_pooled / n_emitted_newly_pooled) if n_emitted_newly_pooled else None

    total_gold_pooled = sum(r["total_gold"] for r in per_seed)
    total_cur_emitted_pooled = sum(r["total_cur_emitted"] for r in per_seed)
    total_cur_correct_pooled = sum(r["total_cur_correct"] for r in per_seed)
    total_ext_emitted_pooled = sum(r["total_ext_emitted"] for r in per_seed)
    total_ext_correct_pooled = sum(r["total_ext_correct"] for r in per_seed)

    precision_current_overall_pooled = (total_cur_correct_pooled / total_cur_emitted_pooled) if total_cur_emitted_pooled else None
    recall_current_pooled = total_cur_correct_pooled / total_gold_pooled
    precision_extended_overall_pooled = (total_ext_correct_pooled / total_ext_emitted_pooled) if total_ext_emitted_pooled else None
    recall_extended_pooled = total_ext_correct_pooled / total_gold_pooled

    guard_all = all(r["guard_current_ok"] and r["guard_extended_ok"] for r in per_seed)
    oos_all = all(r["oos_current_abstains"] and r["oos_extended_abstains"] for r in per_seed)
    recall_improves_over_baseline_ok = recall_extended_pooled > recall_current_pooled
    any_wrong_on_hard_pooled = any(r["any_wrong_on_hard_templates"] for r in per_seed)

    # per-class pooled breakdown.
    per_class_pooled = {}
    for r in per_seed:
        for cls, c in r["per_class"].items():
            pc = per_class_pooled.setdefault(cls, {"n": 0, "cur_wrong": 0, "cur_correct_only": 0, "cur_abstain": 0,
                                                     "ext_wrong": 0, "ext_correct_only": 0, "ext_abstain": 0})
            for k in c:
                pc[k] += c[k]

    return {
        "seeds": seeds, "n_per_template": n_per_template, "total_sentences": total_sentences,
        "coverage_current_pooled": coverage_current_pooled,
        "coverage_extended_pooled": coverage_extended_pooled,
        "coverage_gain_pp_pooled": coverage_gain_pp_pooled,
        "n_newly_covered_pooled": sum(r["n_newly_covered"] for r in per_seed),
        "precision_newly_covered_pooled": precision_newly_covered_pooled,
        "total_gold_pooled": total_gold_pooled,
        "precision_current_overall_pooled": precision_current_overall_pooled,
        "recall_current_pooled": recall_current_pooled,
        "precision_extended_overall_pooled": precision_extended_overall_pooled,
        "recall_extended_pooled": recall_extended_pooled,
        "n_current_wrong_pooled": sum(r["n_current_wrong"] for r in per_seed),
        "n_extended_wrong_pooled": sum(r["n_extended_wrong"] for r in per_seed),
        "guard_regression_ok": guard_all,
        "oos_control_fired": oos_all,
        "recall_improves_over_baseline_ok": recall_improves_over_baseline_ok,
        "any_wrong_on_hard_templates_pooled": any_wrong_on_hard_pooled,
        "per_class_pooled": per_class_pooled,
        "per_seed_summary": [
            {"seed": r["seed"], "coverage_gain_pp": r["coverage_gain_pp"],
             "precision_extended_overall": r["precision_extended_overall"], "recall_extended": r["recall_extended"],
             "precision_current_overall": r["precision_current_overall"], "recall_current": r["recall_current"],
             "n_current_wrong": r["n_current_wrong"], "n_extended_wrong": r["n_extended_wrong"]}
            for r in per_seed
        ],
        "per_seed_full": per_seed,
    }


def compute_verdict(agg):
    prec = agg["precision_extended_overall_pooled"]
    cg = agg["coverage_gain_pp_pooled"]
    guard_ok = agg["guard_regression_ok"]
    oos_ok = agg["oos_control_fired"]
    recall_ok = agg["recall_improves_over_baseline_ok"]

    if prec is None:
        return ("MIDDLE_BAND", "FULLY_EXTENDED emitted zero triples on the whole corpus -- mechanism did not "
                                "fire", "no_triples_emitted")

    hard_pass = (prec >= 0.60) and (cg >= 15.0) and guard_ok and oos_ok and recall_ok
    hard_fail = (prec < 0.50) or (cg < 5.0)

    if hard_pass:
        tier = "HARD_PASS"
    elif hard_fail:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    weakest = "n/a"
    if not hard_pass:
        if prec < 0.60:
            weakest = "precision_extended_overall_below_0.60"
        elif cg < 15.0:
            weakest = "coverage_gain_below_15pp"
        elif not guard_ok:
            weakest = "guard_regression_failed"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire"
        elif not recall_ok:
            weakest = "recall_did_not_improve_over_baseline"

    msg = (f"precision_extended_overall={prec:.3f} (HARD-PASS needs >=0.60, HARD-FAIL if <0.50) | "
           f"recall_extended={agg['recall_extended_pooled']:.3f} recall_current={agg['recall_current_pooled']:.3f} | "
           f"coverage_gain_pp={cg:.1f} (HARD-PASS needs >=15.0, HARD-FAIL if <5.0) | "
           f"precision_current_overall={agg['precision_current_overall_pooled']} | "
           f"n_current_wrong={agg['n_current_wrong_pooled']} n_extended_wrong={agg['n_extended_wrong_pooled']} "
           f"/{agg['total_sentences']} | guard_regression_ok={guard_ok} oos_control_fired={oos_ok} "
           f"recall_improves_over_baseline_ok={recall_ok}")
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
# self-test: EXERCISE THE REAL code path + reproduce the 3 MECHANISM findings live (not asserted from memory).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (imported ie_extract, imported ie_extract_verb_extended, "
          "real nltk.pos_tag calls)...", flush=True)

    # (0) glass-box-legal: static source-scan + RUNTIME transitive sys.modules check (stronger guard, per
    # contract's explicit ask -- the Rung-3 VET used a static scan only; this cell also checks the live
    # module-import closure AFTER nltk has been used, catching a transitive neural dependency the static scan
    # of THIS file alone could never see).
    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"
    _ = nltk.pos_tag(["The", "cat", "sat", "."])  # force nltk's lazy submodule loading before the closure check
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print("[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural)", flush=True)

    # (0b) vacuous-test guards.
    assert not (set(OOV_ANIMALS) & set(ANIMALS)), "OOV_ANIMALS overlaps closed ANIMALS"
    assert not (set(OOV_FOODS) & set(FOODS)), "OOV_FOODS overlaps closed FOODS"
    assert not (set(OOV_VERB_BASE_LEX) & set(VERB_LEX)), "OOV_VERB_BASE_LEX overlaps closed VERB_LEX"
    assert "deer" not in OOV_ANIMALS_BARE_SAFE, "bare-plural-safe filter did not exclude the irregular 'deer'"
    assert "leaf" not in OOV_FOODS_BARE_SAFE and "berry" not in OOV_FOODS_BARE_SAFE, \
        "bare-plural-safe filter did not exclude the irregular-plural foods"

    # (1) MECHANISM 1, MEASURED@standalone-mechanism-probe reproduction: the VET's own adversarial probe shape
    # -- CURRENT (baseline, zero extension) produces a WRONG triple on VP-coordination with an intervening OOV
    # verb, not a clean abstain.
    s = "The owl munches the seed and eats the bread."
    cur = ie_extract(s)
    assert cur[0] != [], f"MECHANISM 1 did not reproduce: expected CURRENT to emit a (wrong) triple on {s!r}, got abstain {cur}"
    assert set(cur[0]) != {("owl", "eats", "seed"), ("owl", "eats", "bread")} & set(cur[0]), \
        "sanity: cur[0] should not equal the gold set"
    assert ("seed", "eats", "bread") in cur[0], \
        f"MECHANISM 1: expected the specific wrong triple ('seed','eats','bread') (object-of-clause-1 " \
        f"misread as subject-of-clause-2), got {cur[0]}"
    ext = ie_extract_verb_extended(s)
    assert set(ext[0]) == {("owl", "eats", "seed")}, \
        f"expected EXTENDED to FIX this specific case (verb1 tags correctly in the 3sg+determiner frame), got {ext[0]}"
    print(f"[self_test] MECHANISM 1 reproduced: CURRENT={cur[0]} (WRONG, matches the VET's own probe finding) "
          f"| EXTENDED={ext[0]} (correct-but-incomplete -- the extension FIXES this specific case)", flush=True)

    # (2) MECHANISM 2, MEASURED@standalone-mechanism-probe reproduction (the headline finding): a bare-plural
    # mistag combined with the noun-promotion fallback poisons EXTENDED too, not just CURRENT.
    s = "Cats munch seeds and chase dogs."
    cur = ie_extract(s)
    ext = ie_extract_verb_extended(s)
    assert ("seed", "chases", "dog") in cur[0], f"MECHANISM 2 CURRENT reproduction failed: got {cur[0]}"
    assert ("seed", "chases", "dog") in ext[0], \
        f"MECHANISM 2 (headline finding) did not reproduce: expected EXTENDED to ALSO emit the wrong triple " \
        f"('seed','chases','dog') on {s!r} (spurious noun-promotion of the mistagged 'munch' token poisons " \
        f"subj_region for the surviving closed verb 'chase'), got {ext[0]} -- if this now differs, the tagger " \
        f"model version may have changed and this cell's headline finding needs re-verification"
    print(f"[self_test] MECHANISM 2 reproduced (headline finding): CURRENT={cur[0]} EXTENDED={ext[0]} -- "
          f"BOTH arms wrong; the compound noun+verb promotion mechanism does NOT rescue this case", flush=True)

    # (3) MECHANISM 2 variant: spurious-noun-as-object bug (all-OOV bare-plural, second verb swallowed into
    # the FIRST clause's object-coordination chain).
    s = "Rabbits munch carrots and hunt goats."
    ext = ie_extract_verb_extended(s)
    assert ("rabbit", "eats", "hunt") in ext[0], \
        f"MECHANISM 2 (object-coordination variant) did not reproduce on {s!r}: expected a triple with the " \
        f"verb-lemma 'hunt' as a spurious OBJECT, got {ext[0]}"
    print(f"[self_test] MECHANISM 2 (object-coordination variant) reproduced: EXTENDED={ext[0]} -- a distinct "
          f"wrong-triple SHAPE (verb-as-object), not the same shape as (2)", flush=True)

    # (4) MECHANISM 3 (a genuine safety finding): when BOTH coordinated verbs mistag to noun-family, verb_idx
    # is fully empty again and the immediate-return safety property DOES fire -- clean abstain, not wrong.
    s = "Squirrels munch acorns and stalk badgers."
    cur = ie_extract(s)
    ext = ie_extract_verb_extended(s)
    assert cur[0] == [] and cur[1] == "NO_VERB", f"MECHANISM 3 CURRENT reproduction failed: {cur}"
    assert ext[0] == [] and ext[1] == "NO_VERB", \
        f"MECHANISM 3 did not reproduce: expected EXTENDED to cleanly abstain (both verbs mistag to noun-" \
        f"family -> verb_idx empty -> immediate NO_VERB) on {s!r}, got {ext}"
    print(f"[self_test] MECHANISM 3 reproduced (safety case): both arms cleanly abstain (NO_VERB) when BOTH "
          f"coordinated verbs mistag to noun-family -- the immediate-return property still fires when verb_idx "
          f"is fully empty", flush=True)

    # (5) EASY templates still work correctly (compound subject, relative clause, passive, all fully-open).
    s = "The rabbit and the duck munch the carrot."
    ext = ie_extract_verb_extended(s)
    assert set(ext[0]) == {("rabbit", "eats", "carrot"), ("duck", "eats", "carrot")}, \
        f"compound-subject fully-open sanity failed: {ext[0]}"
    s = "The duck that hunts the sparrow lives in the meadow."
    ext = ie_extract_verb_extended(s)
    assert set(ext[0]) == {("duck", "lives_in", "meadow")}, f"relative-clause fully-open sanity failed: {ext[0]}"
    s = "The carrot is nibbled by the rabbit."
    ext = ie_extract_verb_extended(s)
    assert set(ext[0]) == {("rabbit", "eats", "carrot")}, f"passive fully-open sanity failed: {ext[0]}"
    print("[self_test] EASY fully-open templates (compound-subject / relative-clause / passive) all correct", flush=True)

    # (6) guard-class regression, including the closed VP-coordination guard (pre-existing scope, unaffected).
    for sent, gold in GUARD_SENTENCES:
        cur = ie_extract(sent)
        ext = ie_extract_verb_extended(sent)
        gset = set(tuple(g) for g in gold)
        assert set(cur[0]) == gset, f"CURRENT guard regression on {sent!r}: {cur[0]} != {gset}"
        assert set(ext[0]) == gset, f"EXTENDED guard regression on {sent!r}: {ext[0]} != {gset}"

    # (7) out-of-schema must-fail control, including the multi-clause OOS control.
    for s in OUT_OF_SCHEMA_CONTROL:
        cur = ie_extract(s)
        ext = ie_extract_verb_extended(s)
        assert cur[0] == [], f"CURRENT unexpectedly extracted on out-of-schema control {s!r}: {cur}"
        assert ext[0] == [], f"EXTENDED unexpectedly extracted on out-of-schema control {s!r}: {ext}"

    # (8) ARMS-MUST-DIFFER (META_RULE_AF).
    rows = build_fullyopen_corpus(seed=7, n_per_template=2)
    cur_all = sorted(set(t for r in rows for t in ie_extract(r["sentence"])[0]))
    ext_all = sorted(set(t for r in rows for t in ie_extract_verb_extended(r["sentence"])[0]))
    h_cur = hashlib.sha256(json.dumps(cur_all, sort_keys=True).encode()).hexdigest()
    h_ext = hashlib.sha256(json.dumps(ext_all, sort_keys=True).encode()).hexdigest()
    assert h_cur != h_ext, "META_RULE_AF VIOLATION: CURRENT and EXTENDED produced bit-identical output"
    assert len(ext_all) > 0, "EXTENDED produced zero triples on the tiny self-test corpus -- mechanism did not fire"

    # (9) discriminator-fires: at least one HARD template row produces a wrong triple in at least one arm on
    # the tiny self-test corpus -- proves the hard cases are genuinely exercised, not vacuously absent.
    tiny_results = [evaluate_row(r) for r in rows]
    hard_tiny = [r for r in tiny_results if r["cls"] in HARD_TEMPLATE_NAMES]
    assert any(r["current_wrong"] or r["extended_wrong"] for r in hard_tiny), \
        "discriminator-fires check failed: no HARD template row produced a wrong triple in either arm on the " \
        "tiny self-test corpus -- the hard cases are not being genuinely exercised"

    # (10) real_code_path (F.1): the full run_seed loop, tiny scale, every entrypoint exercised for real.
    r = run_seed(seed=7, n_per_template=3)
    assert r["precision_extended_overall"] is not None, "real_code_path smoke: EXTENDED emitted zero triples"
    assert r["coverage_extended"] > r["coverage_current"], "real_code_path smoke: EXTENDED did not gain coverage over CURRENT"
    print(f"[self_test] PASS | tiny-corpus precision_extended_overall={r['precision_extended_overall']:.3f} "
          f"recall_extended={r['recall_extended']:.3f} precision_current_overall={r['precision_current_overall']} "
          f"recall_current={r['recall_current']:.3f} n_current_wrong={r['n_current_wrong']} "
          f"n_extended_wrong={r['n_extended_wrong']}", flush=True)
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
    print(f"[fullyopen_multiclause] run_mode={run_mode} seeds={seeds} n_per_template={N_PER_TEMPLATE} "
          f"n_templates={len(TEMPLATES)} expected_n_units={expected_n_units}", flush=True)

    agg = aggregate_seeds(seeds, N_PER_TEMPLATE)
    print(f"[fullyopen_multiclause] precision_extended_overall_pooled={agg['precision_extended_overall_pooled']} "
          f"recall_extended_pooled={agg['recall_extended_pooled']:.3f} "
          f"precision_current_overall_pooled={agg['precision_current_overall_pooled']} "
          f"recall_current_pooled={agg['recall_current_pooled']:.3f} "
          f"coverage_gain_pp_pooled={agg['coverage_gain_pp_pooled']:.1f} "
          f"n_current_wrong={agg['n_current_wrong_pooled']} n_extended_wrong={agg['n_extended_wrong_pooled']}",
          flush=True)

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
        "metric_precision_extended_overall_pooled": agg["precision_extended_overall_pooled"],
        "metric_recall_extended_pooled": agg["recall_extended_pooled"],
        "metric_precision_current_overall_pooled": agg["precision_current_overall_pooled"],
        "metric_recall_current_pooled": agg["recall_current_pooled"],
        "metric_total_gold_pooled": agg["total_gold_pooled"],
        "metric_n_current_wrong_pooled": agg["n_current_wrong_pooled"],
        "metric_n_extended_wrong_pooled": agg["n_extended_wrong_pooled"],
        "metric_guard_regression_ok": agg["guard_regression_ok"],
        "metric_oos_control_fired": agg["oos_control_fired"],
        "metric_recall_improves_over_baseline_ok": agg["recall_improves_over_baseline_ok"],
        "metric_any_wrong_on_hard_templates_pooled": agg["any_wrong_on_hard_templates_pooled"],
        "per_class_pooled": agg["per_class_pooled"],
        "per_seed_summary": agg["per_seed_summary"],
        "arms": {
            "CURRENT": {"coverage": agg["coverage_current_pooled"],
                        "precision_overall": agg["precision_current_overall_pooled"],
                        "recall": agg["recall_current_pooled"]},
            "FULLY_EXTENDED": {"coverage": agg["coverage_extended_pooled"],
                                "precision_overall": agg["precision_extended_overall_pooled"],
                                "recall": agg["recall_extended_pooled"]},
        },
        "prereg": {
            "hard_pass": "precision_extended_overall_pooled>=0.60 AND coverage_gain_pp_pooled>=15.0 AND "
                         "guard_regression_ok AND oos_control_fired AND recall_improves_over_baseline_ok",
            "hard_fail": "precision_extended_overall_pooled<0.50 OR coverage_gain_pp_pooled<5.0",
            "corpus": "9 hand-authored template classes (5 easy fully-open sanity + 4 hard multi-clause) x "
                      "N_PER_TEMPLATE random noun/verb draws per seed, OOV pools confirmed disjoint from "
                      "closed lexicon",
            "scope_note": "hand-authored templates, NOT real prose (SCOPE DECISION, declared -- see module "
                          "docstring). Nouns AND verbs both OOV in the primary corpus; hard templates "
                          "(VP-coordination, compound-subject, relative-clause, passive) genuinely included, "
                          "not dodged. Gold triples for VP-coordination sentences include BOTH clauses' facts "
                          "even though the shared _extract_core grammar structurally captures only the matrix "
                          "verb's clause -- this is what makes recall genuinely limited, not an inflated target.",
            "compute_architecture": "sequential-CPU; pure syntactic parsing, no VSA store; wall time trivial "
                                    "(MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer test, no FoundationStore/KGStore touched)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract (v2, imported unmodified)", "ie_extract_verb_extended "
                                         "(RUNG 3, imported unmodified -- composes RUNG 2's _extract_core + "
                                         "its own noun+verb promotion)", "nltk.pos_tag (real classical "
                                         "averaged-perceptron call)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete syntactic role-assignment + "
                       "the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED) on "
                       "this corpus's specific tokens (MEASURED via standalone pre-design mechanism probes "
                       "against the REAL imported extractors, see module docstring MECHANISM 1-3)",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports in this file) "
                               "AND a runtime sys.modules transitive-closure check after nltk use, both "
                               "asserted at self-test",
            "prior_work_check": "substrate_query.sh confidence=0.29, top hit cosine=0.29 ('coordination "
                                "compound', a WordNet/generic-concept entry, NOT a prior arc experiment cell) "
                                "-- no prior cell at cosine>0.30; genuinely novel, not a rediscovery.",
            "baseline_scope_deviation": "current_coverage_floor_ok (RUNG 2/3's vacuous-test guard) is REPLACED "
                                        "by recall_improves_over_baseline_ok -- CURRENT is NOT expected near-"
                                        "zero coverage on this corpus; MECHANISM 1 means CURRENT actively "
                                        "mis-fires (wrong triples) rather than silently abstaining on several "
                                        "hard template classes, so a near-zero-coverage floor check would be "
                                        "the wrong vacuous-test guard here. Declared, not silent.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[fullyopen_multiclause] {tier} in {elapsed:.2f}s -> {out_dir / 'metrics.json'}", flush=True)
    print(f"[fullyopen_multiclause] {msg}", flush=True)
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
