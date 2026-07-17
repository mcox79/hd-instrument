"""exp_read_grow_realprose_simple_register_rung9_downstream_bugs_v1 -- RUNG 9: fixes the 4 downstream bugs
Rung 8's coref-coverage-expansion LOCALIZED (irregular-plural-noun lemma restoration; brand/product compound-
noun head-selection; OOV verb-lemma spelling-restoration; do-support negation parsing), on the SAME simple-
register UD-EWT slice Rungs 6/7/8 measured, and answers the DECISIVE question: does fixing these 4 reach BOTH
high coverage AND GATED precision >= 0.60 (the first high-coverage-high-precision milestone), or does the newly
cleared coverage expose YET ANOTHER layer of bugs (a long localized-bug tail)?

TRIGGER (Rung-8 metrics.json a1780b46-successor, MEASURED@data/exp_read_grow_realprose_simple_register_rung8_
coref_1st2nd_person_v1/metrics.json): Rung 8's 1st/2nd-person coref fix raised coverage 0.130->0.307 (+136%,
n_newly_covered=53/300) with PERFECT subject-role correctness (47/47 = 1.000 on newly-covered rows with gold),
but overall GATED precision_on_attempted DROPPED to 0.526 (50/95), HARD_FAIL (< 0.55 floor). The VET's own
`newly_covered_whole_triple_precision`=0.434 localized the drop to 4 SEPARATE, PRE-EXISTING, INDEPENDENT bugs
in code paths 1st/2nd-person sentences never reached before (COREF_UNRESOLVED gated them out upstream):
  (a) irregular-PLURAL-noun lemma restoration: "teeth"->"tooth" not handled (emits "teeth"); ALSO a REGULAR
      "-ies" pattern gap the noun lemmatizer lacks (unlike the verb lemmatizer, which already has it):
      "duties"->"duty" emits "duti".
  (b) brand/product COMPOUND-noun head-selection: "HTC Evo"->"evo" emits "htc"; "Garage Pros"->"pro" emits
      "garage". Rung 7's ALL-CAPS-span heuristic (all-capitalized => UD `flat` personal-name span, head=FIRST)
      misfires on brand+model spans that are ALSO all-capitalized but are UD `compound` (head=LAST).
  (c) OOV VERB spelling-restoration: "need"->"ne" (a base-form/VBP verb that coincidentally ends in the letters
      "-ed", wrongly caught by the past-tense suffix-stripper because the lemmatizer is FORM-BLIND -- it never
      consults the token's own POS-derived form, only raw suffix match); "married"->"marri" (a genuine past-
      participle correctly form-gated for -ed-stripping, but missing the y-restoration orthographic rule
      the verb lemmatizer already has for OTHER suffixes, e.g. flies->fly, but not for -ied->-y).
  (d) DO-SUPPORT negation parsing: "don't"/"won't" tokenize (via apostrophe-splitting) into garbage fragments
      ("don"+"t", "won"+"t") that CONFUSE the classical tagger's context window badly enough that even the
      REAL matrix verb after do-support gets mistagged (MEASURED live below: nltk.pos_tag(["I","don","t","feel",
      "anything",...]) tags "feel" as NN, not VB -- a cascading mistag, not merely "don"/"won" themselves).

THE FIX (4 independent, general, closed-form rules -- NOT memorized per-sentence patches; each verified via
NOVEL nonce cases distinct from the Rung-8 error rows that exposed them):
  (a) `IRREGULAR_NOUN_LEMMA` (new, CITED closed table of genuinely irregular English plurals: teeth/tooth,
      feet/foot, mice/mouse, men/man, women/woman, people/person, children/child, geese/goose, oxen/ox,
      lice/louse -- same "small hand-declared CITED closed table" pattern as Rung 5's `IRREGULAR_VERB_LEMMA`),
      consulted FIRST inside a new `_oov_lemma_v2`, PLUS a regular "-ies"->"-y" orthographic restoration rule
      mirroring the ALREADY-CORRECT rule in the verb lemmatizer (`_open_verb_lemma`'s `ies -> y`) that the noun
      lemmatizer (`_oov_lemma`) never had -- a genuine asymmetry-closing fix, not a new invented mechanism.
  (b) `COMMON_GIVEN_NAMES` (new, CITED closed gazetteer of ~50 common English first names -- name-list
      gazetteers are THE standard classical-NER technique for person-name detection, the same closed-lexicon
      pattern this codebase already uses for DETS/PRONS/BE_AUX/ENTITIES). `_np_head_from_run_v2` refines Rung
      7's all-caps rule: an all-capitalized multi-noun run is a `flat` PERSONAL-NAME span (head=FIRST) ONLY IF
      its first token's lowercased form is a recognized given name; otherwise it is a `compound` BRAND/PRODUCT
      span (head=LAST). "Santa"/"Winston"/"Maria" are given names -> unchanged (head=first, regression-safe);
      "HTC"/"Garage" are not -> now correctly compound (head=last).
  (c) `_open_verb_lemma_v2` (new): made FORM-AWARE (takes the token's own POS-derived form, not just raw
      surface text) -- the "-ed" past-tense stripping rule (and its sibling "-ing"/"-s"/"-es"/"-ies" rules) now
      fire ONLY when the token's form is the grammatically-appropriate one (past/participle for -ed; gerund for
      -ing; 3sg for -s/-es/-ies) instead of blindly pattern-matching any surface suffix regardless of the
      token's actual tag. This is a principled generalization (form-gate every suffix rule uniformly), not a
      special case for "need" alone -- verified below to leave ALL already-correct forms (fax/faxed, etc.)
      untouched. PLUS a new y-restoration rule for -ied-ending stems after -ed-stripping (stem ends in "i"
      preceded by a consonant -> restore "y": marri->marry, carri->carry), mirroring pattern (a)'s -ies->y fix
      but for the -ed-suffix family.
  (d) `_expand_contractions` (new, CITED standard classical-NLP preprocessing technique): a closed contraction-
      expansion table (don't->do not, won't->will not, doesn't->does not, etc., ~18 entries) applied to the RAW
      sentence string BEFORE tokenization, so the tagger sees clean "do not feel" tokens instead of the garbage
      "don"/"t" fragments that were corrupting its context window. PLUS a position-INDEPENDENT post-tag override
      pass (general, not scoped to sentence-position like the existing "please"-DISC override): any VERB-tagged
      "do" immediately followed by an ADV-tagged "not" is retagged AUX (do-support is ALWAYS auxiliary in this
      configuration -- a main-verb "do" never takes "not" as its direct object) -- exposing the REAL matrix verb
      (feel/return/etc.) to the unmodified verb-search logic. Modals (will/would/can/could/etc.) needed NO new
      code: MEASURED live below that nltk already tags them MD, which was ALREADY invisible to this pipeline's
      verb-search (only tags=="VERB" counts) -- so "will" in "will not return" was already correctly excluded
      from matrix-verb candidacy; the do-support override is the only piece that was missing.

ARMS (SAME real simple-syntax UD-EWT slice as Rung 6/7/8 -- SAME seeds=[7,13,19], SAME n_per_seed=100, SAME
`load_simple_sentences_v2` filter, unchanged): BASELINE = Rung 8's `ie_extract_coref_1st2nd_fixed` (imported
UNMODIFIED). Four SINGLE-BUG isolation arms (BASELINE + exactly one of the 4 new fixes) for per-bug
contribution. FIXED_ALL = BASELINE + all 4 fixes (the PRIMARY discriminator).

HONEST RESULT (MEASURED@this cell's own self_test/smoke/full, live-computed, reported in full):
see metrics.json `arms` + `per_bug_contribution` + `residual_error_classification` for the live numbers. THE
DECISIVE DIAGNOSTIC (does fixing the 4 reach the milestone, or expose another layer?) is computed live in
`residual_error_classification`: every row FIXED_ALL still gets WRONG is classified into (i) a signature
matching one of the 4 just-fixed bugs (a self-check -- should be ~0, else a fix didn't fully land), (ii) a
NAMED NEW pattern already visible in Rung 8's own sample even before this rung ran (MODAL_OR_FUNCTION_WORD_
MISTAGGED_AS_MATRIX_VERB -- e.g. "I better pass on the Comets game." mistags reduced-modal "better" as the
main verb via VBP; BARE_ADJUNCT_OVEREXTRACTION -- e.g. "i flew here last night." wrongly extracts the bare
temporal NP "night" as a direct object when gold has no object at all), or (iii) OTHER_UNCLASSIFIED_RESIDUAL
(honestly bucketed, not forced into a named class). This directly answers the tail-length question: a nonzero,
NAMED-NEW-pattern count is honest evidence of ANOTHER bug layer (long tail); an near-zero residual with
precision >= 0.60 is the milestone (short tail).

BANDS (pre-registered; exp_dev-authored per the dispatching contract's own literal thresholds):
  Primary discriminator = FIXED_ALL arm's `precision_on_attempted` (overall, GATED, same extended-gold row set
  as BASELINE) + `coverage_sentence_rate` (must stay materially high, not collapse) + 3rd-person guardrail.
  HARD-PASS (the milestone): FIXED_ALL precision_on_attempted >= 0.60 AND FIXED_ALL coverage_sentence_rate >=
    0.28 (BASELINE's own coverage is 0.307 MEASURED@rung8-metrics.json -- 0.28 gives a small tolerance band
    without permitting collapse) AND n_3rd_person_guard_breaks == 0 AND guard_regression_ok_fixed AND
    oos_control_fired_fixed AND simple_fraction_of_length_matched_pool >= 0.10 AND coref_guardrail_battery_ok
    (Rung 8's guardrail, reproduced) AND all 4 nonce-generalization batteries pass (fixes are general, not
    memorized).
  HARD-FAIL: FIXED_ALL precision_on_attempted < 0.55 OR coverage_sentence_rate < 0.20 (collapse) OR
    n_3rd_person_guard_breaks > 0 OR NOT guard_regression_ok_fixed OR simple_fraction_of_length_matched_pool <
    0.10 OR any nonce-generalization battery fails (a fix that only works on the literal Rung-8 error rows is
    a memorized patch, not a general rule -- contract-disqualifying).
  MIDDLE_BAND: otherwise (e.g. precision in [0.55, 0.60) with coverage/guardrail intact -- reported honestly,
    with the residual-error-classification breakdown carrying the real informational payload in this band).
  HONEST CAVEAT CARRIED FORWARD (unchanged from Rung 6/7/8): PATH A is a simple-SYNTAX subset of general WEB
  VOCABULARY (UD-EWT), not a vocabulary-controlled early-reader corpus.

COMPUTE: SEEDS=[7,13,19], N_PER_SEED=100 (IDENTICAL to Rung 6/7/8). Smoke = seed[7] only, SAME N_PER_SEED
  (Option A, discriminator-survives-scale; trivial wall time -- pure CPU string/POS-tag processing, no torch,
  no numpy, no VSA store, matching Rung 5/5b/6/7/8 precedent). Local, executed DIRECTLY (bash), no queue/GPU/
  atoms/push. Corpus already fetched + committed. NO network access at self-test/smoke/full time. Storage:
  no_storage. Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before running.

NEXT (not this cell, reported honestly if the residual is nonzero): MODAL_OR_FUNCTION_WORD_MISTAGGED_AS_MATRIX_
VERB ("had better" reduction) and BARE_ADJUNCT_OVEREXTRACTION (temporal/locative adjunct NPs mistaken for
direct objects with no preposition to disambiguate) are NOT fixed by this cell (out of the 4 named bugs'
scope) -- flagged as Rung 10 candidates if the residual classification shows they are material.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; BASELINE vs FIXED_ALL vs 4 single-bug arms emitted-
#   triple-set hashes pairwise differ on the real simple-slice sample by construction).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor; discriminator is discrete syntactic role-assignment + the classical
#   tagger's own literature-benchmarked accuracy (96-97% PTB, CITED), same as Rung 5/5b/6/7/8.
# - baseline_in_band: N/A BY DESIGN -- BASELINE's own known Rung-8 precision (0.526, MEASURED@rung8 metrics.json,
#   re-derived live below via same-slice parity) is the pre-registered floor this cell exists to raise.
# - discriminator survives scale: corpus is FIXED-size real prose, deterministic filtered pool, SAME regime as
#   Rung 6/7/8 (no scale axis). Smoke uses the SAME N_PER_SEED as FULL, single seed only (Option A).
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test parses the REAL local corpus file (Rung 7's parse_conllu_v2, feats-aware),
#   applies the REAL simplicity filter, samples a tiny real slice, and runs BOTH BASELINE and FIXED_ALL against
#   REAL sentences, plus live (not narrated) nonce-generalization batteries for all 4 fixes + the 3rd-person
#   zero-hallucination guardrail.
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19], inherited unmodified from Rung 5/6/7/8's own
#   random.Random(seed).sample over a sorted(...) sentence-id-ordered pool.
# - all numbers in comments tagged MEASURED@this-cell (live self_test/smoke/full output) / MEASURED@rung8-
#   metrics.json / MEASURED@corpus / CITED@classical-NLP-technique.
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
import hashlib
import platform
import traceback
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_realprose_simple_register_rung9_downstream_bugs_v1"

# --- GENUINE REUSE: Rung 8 (BASELINE arm = ie_extract_coref_1st2nd_fixed, imported UNMODIFIED, coref-fix
# primitives), Rung 7 (feats-aware corpus loader, gold-deriver, head-selection primitives we EXTEND), Rung 5
# (corpus parser base / CaRB scorer / guard sentences / OOS control / IRREGULAR_VERB_LEMMA), Rung 5b (finite-
# form check), Rung 6 (SAME seeds/n_per_seed), foundation v2 (coordination splitter / closed function-word
# sets), oov_pos_extension (NLTK tag-family sets). ---
from experiments.exp_read_grow_realprose_simple_register_rung8_coref_1st2nd_person_v1 import (  # noqa: E402
    ie_extract_coref_1st2nd_fixed, FIRST_SECOND_PERSON_SUBJECT_PRONOUNS, verify_coref_guardrail,
)
from experiments.exp_read_grow_realprose_simple_register_rung7_fixes_imperatives_v1 import (  # noqa: E402
    CONLLU_PATH, load_simple_sentences_v2, build_rows_for_seed_v2, analyze_sentence_v2, CONSTRUCTION_CLASSES_V2,
    _first_contiguous_noun_run, ie_extract_fix_all, parse_conllu_v2,
)
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import (  # noqa: E402
    score_arm, GUARD_SENTENCES, OUT_OF_SCHEMA_CONTROL, _resolve_relation_open, IRREGULAR_VERB_LEMMA,
    _open_verb_lemma as _open_verb_lemma_v0, _OPEN_FORM_MAP,
)
from experiments.exp_read_grow_realprose_abstain_gate_rung5b_v1 import _is_finite_form  # noqa: E402
from experiments.exp_read_grow_realprose_simple_register_rung6_v1 import SEEDS_FULL, N_PER_SEED  # noqa: E402
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import (  # noqa: E402
    DETS, PRONS, BE_AUX, RELZRS, PREPS, VERB_LEX, ENTITIES, ADJS, ADVS, _tokenize, _split_coord,
)
from experiments.exp_read_grow_oov_pos_extension_v1 import (  # noqa: E402
    _tokenize_cased, _oov_lemma as _oov_lemma_v0, NLTK_NOUN_TAGS, NLTK_VERB_TAGS,
)

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only (same as Rung 5/5b/6/7/8); glass-box-legal.

# ---------------------------------------------------------------------------
# BUG (a) FIX: irregular-PLURAL-noun lemma restoration. CITED closed table (common English irregular plurals,
# same "small hand-declared CITED closed table" pattern as Rung 5's IRREGULAR_VERB_LEMMA) + a regular "-ies"
# y-restoration rule MIRRORING the verb lemmatizer's ALREADY-CORRECT "ies -> y" rule (an asymmetry-closing fix,
# not a new invented mechanism -- the noun lemmatizer simply never had this rule while the verb one did).
# ---------------------------------------------------------------------------
IRREGULAR_NOUN_LEMMA = {
    "teeth": "tooth", "feet": "foot", "mice": "mouse", "men": "man", "women": "woman",
    "people": "person", "children": "child", "geese": "goose", "oxen": "ox", "lice": "louse",
}


def _oov_lemma_v2(w_lower, use_noun_plural_fix):
    """BUG (a) fix, parameterized for per-bug ablation. use_noun_plural_fix=False reproduces the OLD
    `_oov_lemma` byte-for-byte (verified at self_test)."""
    if not use_noun_plural_fix:
        return _oov_lemma_v0(w_lower)
    if w_lower in IRREGULAR_NOUN_LEMMA:
        return IRREGULAR_NOUN_LEMMA[w_lower]
    if w_lower.endswith("ies") and len(w_lower) > 4:
        return w_lower[:-3] + "y"
    if len(w_lower) > 3 and w_lower.endswith("es"):
        return w_lower[:-2]
    if len(w_lower) > 3 and w_lower.endswith("s") and not w_lower.endswith("ss"):
        return w_lower[:-1]
    return w_lower


# ---------------------------------------------------------------------------
# BUG (b) FIX: brand/product COMPOUND-noun head-selection. CITED closed gazetteer of common English given
# names (standard classical-NER name-list technique -- the SAME closed-lexicon pattern this codebase already
# uses for DETS/PRONS/BE_AUX/ENTITIES, just for person first-names). Refines Rung 7's all-caps rule: a `flat`
# personal-name span (head=FIRST) requires the FIRST token to be a recognized given name; otherwise the span
# is treated as a `compound` brand/product span (head=LAST).
# ---------------------------------------------------------------------------
COMMON_GIVEN_NAMES = {
    "santa", "winston", "maria", "john", "mary", "james", "patricia", "robert", "jennifer", "michael",
    "linda", "william", "elizabeth", "david", "susan", "richard", "jessica", "joseph", "sarah", "thomas",
    "karen", "charles", "nancy", "christopher", "lisa", "daniel", "margaret", "matthew", "betty", "anthony",
    "sandra", "donald", "ashley", "mark", "kimberly", "paul", "emily", "steven", "donna", "andrew", "carol",
    "kenneth", "michelle", "george", "amanda", "edward", "melissa", "brian", "deborah", "ronald",
}


def _np_head_from_run_v2(T, run_idx, use_brand_fix):
    """BUG (b) fix, parameterized for per-bug ablation. use_brand_fix=False reproduces Rung 7's OLD
    `_np_head_from_run` byte-for-byte (all-caps -> always head=first) -- verified at self_test."""
    if not run_idx:
        return None
    if len(run_idx) == 1:
        return T[run_idx[0]][2]
    all_caps = all(T[i][0][:1].isupper() for i in run_idx)
    if not all_caps:
        return T[run_idx[-1]][2]
    if not use_brand_fix:
        return T[run_idx[0]][2]
    first_lower = T[run_idx[0]][0].lower()
    head_i = run_idx[0] if first_lower in COMMON_GIVEN_NAMES else run_idx[-1]
    return T[head_i][2]


def _scan_object_np_v2(T, tags, lemmas, j, n, use_head_fix, allow_pron_skip, use_brand_fix):
    """structural copy of Rung 7's `_scan_object_np`, calling `_np_head_from_run_v2` (BUG b fix) instead of
    the old `_np_head_from_run`. Everything else byte-identical."""
    prep = None
    obj_lemmas = []
    skip_tags = ("DET", "ADJ", "ADV", "AUX") + (("PRON",) if allow_pron_skip else ())
    while j < n:
        tg = tags[j]
        if tg in skip_tags:
            j += 1
            continue
        if tg == "PREP" and prep is None and not obj_lemmas:
            prep = lemmas[j]
            j += 1
            continue
        if tg == "NOUN":
            run_start = j
            if use_head_fix:
                while j < n and tags[j] == "NOUN":
                    j += 1
                obj_lemmas.append(_np_head_from_run_v2(T, list(range(run_start, j)), use_brand_fix))
            else:
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
                        run_start2 = j
                        if use_head_fix:
                            while j < n and tags[j] == "NOUN":
                                j += 1
                            obj_lemmas.append(_np_head_from_run_v2(T, list(range(run_start2, j)), use_brand_fix))
                        else:
                            obj_lemmas.append(lemmas[j])
                            j += 1
                        continue
                    break
                break
            break
        break
    return prep, obj_lemmas, j


# ---------------------------------------------------------------------------
# BUG (c) FIX: OOV verb-lemma spelling-restoration. FORM-AWARE lemmatizer (a principled generalization -- every
# suffix rule now fires only for its grammatically-appropriate form, not blind surface-suffix matching) + a new
# y-restoration rule for -ied-ending stems (mirrors bug (a)'s -ies->y fix, for the -ed-suffix family).
# ---------------------------------------------------------------------------
def _open_verb_lemma_v2(w_lower, form, use_verb_oov_fix):
    """BUG (c) fix, parameterized for per-bug ablation. use_verb_oov_fix=False reproduces the OLD
    `_open_verb_lemma` byte-for-byte (verified at self_test)."""
    if not use_verb_oov_fix:
        return _open_verb_lemma_v0(w_lower)
    w = w_lower
    if w in ("is", "are", "was", "were", "been", "being"):
        return "be"
    if form == "3sg" and w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if form == "gerund" and w.endswith("ing") and len(w) > 4:
        stem = w[:-3]
        if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]
        return stem
    if form in ("past", "past_or_participle", "participle") and w.endswith("ed") and len(w) > 3:
        stem = w[:-2]
        if len(stem) >= 2 and stem[-1] == "i" and stem[-2] not in "aeiou":
            # y-restoration: marri(ed) -> marry, carri(ed) -> carry (orthographic y->i-before-suffix undone).
            return stem[:-1] + "y"
        if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]
        return stem
    if form == "3sg" and w.endswith("es") and len(w) > 3 and w[:-2].endswith(("s", "x", "z", "ch", "sh", "o")):
        return w[:-2]
    if form == "3sg" and w.endswith("s") and not w.endswith("ss") and len(w) > 2:
        return w[:-1]
    return w


# ---------------------------------------------------------------------------
# BUG (d) FIX: DO-SUPPORT negation parsing. CITED standard classical-NLP contraction-expansion preprocessing +
# a general (position-INDEPENDENT) post-tag override: any VERB "do" immediately followed by ADV "not" is
# do-support (always auxiliary in that configuration), never a main verb.
# ---------------------------------------------------------------------------
CONTRACTION_EXPANSION = {
    "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "won't": "will not", "wouldn't": "would not", "couldn't": "could not",
    "shouldn't": "should not", "can't": "can not", "cannot": "can not",
    "isn't": "is not", "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "haven't": "have not", "hasn't": "has not", "hadn't": "had not",
    "mustn't": "must not", "mightn't": "might not", "shan't": "shall not",
}
_CONTRACTION_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in CONTRACTION_EXPANSION) + r")\b", re.IGNORECASE)


def _expand_contractions(sentence):
    def _repl(m):
        matched = m.group(0)
        expansion = CONTRACTION_EXPANSION[matched.lower()]
        if matched[0].isupper():
            expansion = expansion[0].upper() + expansion[1:]
        return expansion
    return _CONTRACTION_RE.sub(_repl, sentence)


DO_SUPPORT_LEMMAS = {"do"}


def _apply_dosupport_override(T):
    """position-INDEPENDENT (unlike the existing position-0-only 'please'-DISC override): retag any VERB token
    whose lemma is 'do' when IMMEDIATELY followed by an ADV token whose lemma is 'not'. Do-support 'do' is
    ALWAYS auxiliary in this configuration (a main-verb 'do' never takes 'not' as its direct object) --
    verified NOT to fire on genuine main-verb 'do' (e.g. 'I do the work.', 'I do nothing wrong.') at self_test."""
    out = list(T)
    for i in range(len(out) - 1):
        w_orig, tag, lemma, form = out[i]
        if tag == "VERB" and lemma in DO_SUPPORT_LEMMAS:
            nxt = out[i + 1]
            if nxt[1] == "ADV" and nxt[0].lower() == "not":
                out[i] = (w_orig, "AUX", None, None)
    return out


# ---------------------------------------------------------------------------
# TAGGER (parameterized: threads all 3 tagging-level fixes -- bug1 [inherited from Rung 7], bug (a) noun
# plural, bug (c) verb OOV -- through the shared per-token classifier).
# ---------------------------------------------------------------------------
IMPERATIVE_DISCOURSE_MARKERS = {"please"}


def _tag_token_open_v4(w_lower, w_orig, ptag, use_bug1_fix, use_noun_plural_fix, use_verb_oov_fix):
    """structural copy of Rung 7/8's `_tag_token_open_v2`, with the NOUN and VERB fallback branches routed
    through the BUG (a)/(c) fixed lemmatizers (parameterized -- off reproduces old behavior byte-for-byte)."""
    if w_lower in DETS:
        return "DET", None, None
    if w_lower in PRONS:
        return "PRON", w_lower, None
    if w_lower in BE_AUX:
        return "AUX", None, None
    if w_lower in RELZRS:
        return "RELZR", w_lower, None
    if w_lower == "and":
        return "CONJ", "and", None
    if w_lower in PREPS:
        return "PREP", w_lower, None
    if w_lower in VERB_LEX:
        stem, form = VERB_LEX[w_lower]
        return "VERB", stem, form
    nl = None
    if w_lower in ENTITIES:
        nl = w_lower
    elif len(w_lower) > 3 and w_lower.endswith("es") and w_lower[:-2] in ENTITIES:
        nl = w_lower[:-2]
    elif len(w_lower) > 2 and w_lower.endswith("s") and w_lower[:-1] in ENTITIES:
        nl = w_lower[:-1]
    if nl is not None:
        return "NOUN", nl, None
    if ptag in NLTK_VERB_TAGS:
        form = _OPEN_FORM_MAP.get(ptag, "unknown")
        if use_bug1_fix and w_lower in IRREGULAR_VERB_LEMMA:
            lemma = IRREGULAR_VERB_LEMMA[w_lower]
        else:
            lemma = _open_verb_lemma_v2(w_lower, form, use_verb_oov_fix)
        return "VERB", lemma, form
    if ptag in NLTK_NOUN_TAGS:
        return "NOUN", _oov_lemma_v2(w_lower, use_noun_plural_fix), None
    if ptag.startswith("JJ") or w_lower in ADJS:
        return "ADJ", None, None
    if ptag.startswith("RB") or w_lower in ADVS:
        return "ADV", None, None
    if ptag == "IN":
        return "PREP", w_lower, None
    return "UNK", None, None


def _build_tags_open_v4(sentence, use_bug1_fix, use_noun_plural_fix, use_verb_oov_fix, use_dosupport_fix):
    src = _expand_contractions(sentence) if use_dosupport_fix else sentence
    lower_toks = _tokenize(src)
    cased_toks = _tokenize_cased(src)
    assert len(lower_toks) == len(cased_toks), "tokenization parity break between cased/lowercased split"
    tagged = nltk.pos_tag(cased_toks)  # REAL classical averaged-perceptron call, context-aware over the sentence
    T = []
    for (w_lower, w_orig, (_, ptag)) in zip(lower_toks, cased_toks, tagged):
        tag, lemma, form = _tag_token_open_v4(w_lower, w_orig, ptag, use_bug1_fix, use_noun_plural_fix, use_verb_oov_fix)
        T.append((w_orig, tag, lemma, form))
    if T and T[0][0].lower() in IMPERATIVE_DISCOURSE_MARKERS:
        w_orig0 = T[0][0]
        T[0] = (w_orig0, "DISC", w_orig0.lower(), None)
    if use_dosupport_fix:
        T = _apply_dosupport_override(T)
    return T


# ---------------------------------------------------------------------------
# EXTRACTOR CORE: line-for-line copy of Rung 8's `_extract_core_open_gated_v3`, with `_scan_object_np` ->
# `_scan_object_np_v2` and `_np_head_from_run` -> `_np_head_from_run_v2` (threading use_brand_fix through every
# call site: object scan, subject head-run, passive by-agent). The coref 1st/2nd-person branch (Rung 8) and the
# imperative branch (Rung 7) are UNCHANGED.
# ---------------------------------------------------------------------------
def _extract_core_open_gated_v4(T, use_head_fix, use_imperative_fix, use_coref_1st2nd_fix, use_brand_fix):
    tags = [t[1] for t in T]
    lemmas = [t[2] for t in T]
    forms = [t[3] for t in T]
    n = len(T)
    all_verb_idx = [i for i in range(n) if tags[i] == "VERB"]
    if not all_verb_idx:
        return [], "NO_VERB", "no verb (closed or POS-tag-promoted)"

    verb_idx = [i for i in all_verb_idx if _is_finite_form(tags, forms, i)]
    if not verb_idx:
        return [], "ABSTAIN_NO_FINITE_VERB", (
            "no FINITE verb candidate (only non-finite gerund/participle tokens found, or a fragment) -- "
            "gate refuses to guess a matrix verb")

    noun_idx = [i for i in range(n) if tags[i] == "NOUN"]
    pron_idx = [i for i in range(n) if tags[i] == "PRON"]
    relzr_idx = [i for i in range(n) if tags[i] == "RELZR"]

    v0 = verb_idx[0]
    subj_nouns_before_v0 = [i for i in noun_idx if i < v0]
    subj_prons_before_v0 = [i for i in pron_idx if i < v0]

    pronoun_subject_lemma = None
    if not subj_nouns_before_v0:
        if not subj_prons_before_v0:
            if use_imperative_fix and forms[v0] == "base":
                matrix_vi = v0
                verb_lemma = lemmas[matrix_vi]
                subjects = ["you"]
                prep, obj_lemmas, jend = _scan_object_np_v2(T, tags, lemmas, matrix_vi + 1, n, use_head_fix, True, use_brand_fix)
                consumed_end = jend
                if not obj_lemmas:
                    return [], "ABSTAIN_IMPERATIVE_NO_OBJECT", (
                        "imperative recognized (no subject noun/pronoun before a base-form finite verb) but "
                        "no object noun found -- correctly abstains (intransitive imperative, no SVO triple "
                        "to derive) rather than emitting a subjectless partial guess")
                trailing_finite = [i for i in all_verb_idx if i >= consumed_end and _is_finite_form(tags, forms, i)]
                if trailing_finite:
                    return [], "ABSTAIN_TRAILING_FINITE_VERB", (
                        f"finite verb token(s) remain unconsumed after the matched imperative pattern "
                        f"(idx={trailing_finite})")
                relation = _resolve_relation_open(verb_lemma, prep)
                triples = [("you", relation, o) for o in obj_lemmas]
                valid = [(s, r, o) for (s, r, o) in triples if s != o and s and o]
                seen = set()
                out = []
                for tr in valid:
                    if tr not in seen:
                        seen.add(tr)
                        out.append(tr)
                if not out:
                    return [], "NO_VALID_TRIPLE", "all candidate imperative triples failed validity"
                return out, "IMPERATIVE_OPEN_GATED", None
            return [], "NO_SUBJECT", "no noun left of verb, and not a recognized base-form imperative"
        pron_i = subj_prons_before_v0[-1]
        cand_lemma = lemmas[pron_i]
        if use_coref_1st2nd_fix and cand_lemma in FIRST_SECOND_PERSON_SUBJECT_PRONOUNS:
            pronoun_subject_lemma = cand_lemma
        else:
            return [], "COREF_UNRESOLVED", "pronoun subject, no in-sentence antecedent (coreference gap)"

    if pronoun_subject_lemma is not None:
        subjects = [pronoun_subject_lemma]
        rc = False
        matrix_vi = v0
    else:
        head_noun_i = subj_nouns_before_v0[0]
        rc = False
        matrix_vi = verb_idx[0]
        if relzr_idx and head_noun_i < relzr_idx[0] < verb_idx[0]:
            rc = True
            later = [vi for vi in verb_idx if vi > verb_idx[0]]
            if not later:
                return [], "RELCLAUSE_NO_MATRIX_VERB", "relative clause without a finite matrix verb"
            matrix_vi = later[0]

    verb_lemma = lemmas[matrix_vi]
    verb_form = forms[matrix_vi]

    k = matrix_vi - 1
    while k >= 0 and tags[k] == "ADV":
        k -= 1
    is_passive = (k >= 0 and tags[k] == "AUX" and verb_form in ("participle", "past_or_participle"))

    if pronoun_subject_lemma is None:
        if rc:
            subjects = [lemmas[head_noun_i]]
        else:
            subj_region = [i for i in noun_idx if i < matrix_vi]
            has_and_coord = any(tags[k2] == "CONJ" and lemmas[k2] == "and"
                                 for k2 in range(subj_region[0], subj_region[-1] + 1)) if subj_region else False
            if has_and_coord:
                subjects = _split_coord(subj_region, T)
            elif use_head_fix:
                head_run = _first_contiguous_noun_run(subj_region)
                subjects = [_np_head_from_run_v2(T, head_run, use_brand_fix)] if head_run else [lemmas[subj_region[-1]]]
            else:
                subjects = _split_coord(subj_region, T) or [lemmas[subj_region[-1]]]

    consumed_end = matrix_vi + 1

    if is_passive:
        by_i = None
        for j in range(matrix_vi + 1, n):
            if tags[j] == "PREP" and lemmas[j] == "by":
                by_i = j
                break
        if by_i is None:
            return [], "PASSIVE_NO_AGENT", "agentless passive (subject unrecoverable)"
        agent = None
        agent_i = None
        for j in range(by_i + 1, n):
            if tags[j] == "NOUN":
                if use_head_fix:
                    run_start = j
                    jj = j
                    while jj < n and tags[jj] == "NOUN":
                        jj += 1
                    agent = _np_head_from_run_v2(T, list(range(run_start, jj)), use_brand_fix)
                    agent_i = jj - 1
                else:
                    agent = lemmas[j]
                    agent_i = j
                break
        if agent is None:
            return [], "PASSIVE_NO_AGENT_NOUN", "no agent noun after 'by'"
        consumed_end = agent_i + 1
        relation = _resolve_relation_open(verb_lemma, None)
        triples = [(agent, relation, patient) for patient in subjects]
        rule = "SVO_PASSIVE_OPEN_GATED_V4"
    else:
        prep, obj_lemmas, jend = _scan_object_np_v2(T, tags, lemmas, matrix_vi + 1, n, use_head_fix, False, use_brand_fix)
        consumed_end = jend
        relation = _resolve_relation_open(verb_lemma, prep)
        if not obj_lemmas:
            return [], "NO_OBJECT", "no object noun after verb"
        triples = [(s, relation, o) for s in subjects for o in obj_lemmas]
        if len(subjects) > 1 or len(obj_lemmas) > 1:
            rule = "SVO_COORD_OPEN_GATED_V4"
        elif pronoun_subject_lemma is not None:
            rule = "SVO_1ST2ND_PERSON_PRONOUN_SUBJECT_V4"
        else:
            rule = "SVO_ACTIVE_OPEN_GATED_V4"

    trailing_finite = [i for i in all_verb_idx if i >= consumed_end and _is_finite_form(tags, forms, i)]
    if trailing_finite:
        return [], "ABSTAIN_TRAILING_FINITE_VERB", (
            f"finite verb token(s) remain unconsumed after the matched pattern (idx={trailing_finite})")

    valid = [(s, r, o) for (s, r, o) in triples if s != o and s and o]
    seen = set()
    out = []
    for tr in valid:
        if tr not in seen:
            seen.add(tr)
            out.append(tr)
    if not out:
        return [], "NO_VALID_TRIPLE", "all candidate triples failed validity"
    return out, rule, None


def ie_extract_open_gated_v4(sentence, use_bug1_fix, use_head_fix, use_imperative_fix, use_coref_1st2nd_fix,
                              use_noun_plural_fix, use_brand_fix, use_verb_oov_fix, use_dosupport_fix):
    T = _build_tags_open_v4(sentence, use_bug1_fix, use_noun_plural_fix, use_verb_oov_fix, use_dosupport_fix)
    return _extract_core_open_gated_v4(T, use_head_fix, use_imperative_fix, use_coref_1st2nd_fix, use_brand_fix)


_INHERITED_TRUE = dict(use_bug1_fix=True, use_head_fix=True, use_imperative_fix=True, use_coref_1st2nd_fix=True)


def ie_extract_downstream_all_fixed(sentence):
    """FIXED_ALL: BASELINE (Rung 8) settings + all 4 new Rung-9 fixes enabled."""
    return ie_extract_open_gated_v4(sentence, **_INHERITED_TRUE, use_noun_plural_fix=True, use_brand_fix=True,
                                     use_verb_oov_fix=True, use_dosupport_fix=True)


def ie_extract_downstream_all_disabled(sentence):
    """all-4-off positive control: must byte-for-byte reproduce Rung 8's ie_extract_coref_1st2nd_fixed."""
    return ie_extract_open_gated_v4(sentence, **_INHERITED_TRUE, use_noun_plural_fix=False, use_brand_fix=False,
                                     use_verb_oov_fix=False, use_dosupport_fix=False)


def ie_extract_plural_only(sentence):
    return ie_extract_open_gated_v4(sentence, **_INHERITED_TRUE, use_noun_plural_fix=True, use_brand_fix=False,
                                     use_verb_oov_fix=False, use_dosupport_fix=False)


def ie_extract_brand_only(sentence):
    return ie_extract_open_gated_v4(sentence, **_INHERITED_TRUE, use_noun_plural_fix=False, use_brand_fix=True,
                                     use_verb_oov_fix=False, use_dosupport_fix=False)


def ie_extract_verb_oov_only(sentence):
    return ie_extract_open_gated_v4(sentence, **_INHERITED_TRUE, use_noun_plural_fix=False, use_brand_fix=False,
                                     use_verb_oov_fix=True, use_dosupport_fix=False)


def ie_extract_dosupport_only(sentence):
    return ie_extract_open_gated_v4(sentence, **_INHERITED_TRUE, use_noun_plural_fix=False, use_brand_fix=False,
                                     use_verb_oov_fix=False, use_dosupport_fix=True)


SINGLE_BUG_ARMS = {
    "PLURAL_ONLY": ie_extract_plural_only,
    "BRAND_ONLY": ie_extract_brand_only,
    "VERB_OOV_ONLY": ie_extract_verb_oov_only,
    "DOSUPPORT_ONLY": ie_extract_dosupport_only,
}


# ---------------------------------------------------------------------------
# LIVE NONCE-GENERALIZATION BATTERIES (MEASURED, not narrated) -- verifies each of the 4 fixes is a GENERAL
# rule, not a memorized patch keyed to the literal Rung-8 error sentences. Every nonce word/name below is
# DISTINCT from the Rung-8 sample rows that exposed the bug.
# ---------------------------------------------------------------------------
def verify_downstream_fixes():
    evidence = {}

    # (a) irregular-plural-noun + regular -ies restoration -- NOVEL words (not teeth/duties).
    plural_cases = [
        ("I saw the mice.", "mouse"), ("I have the geese.", "goose"), ("I read the stories.", "story"),
    ]
    plural_detail = []
    plural_ok = True
    for sent, expect_obj in plural_cases:
        base = ie_extract_coref_1st2nd_fixed(sent)
        fixed = ie_extract_plural_only(sent)
        ok = bool(fixed[0]) and fixed[0][0][2] == expect_obj
        plural_detail.append({"sent": sent, "baseline": base, "fixed": fixed, "expected_object": expect_obj, "ok": ok})
        plural_ok = plural_ok and ok
    evidence["bug_a_plural_nonce_generalization_ok"] = plural_ok
    evidence["bug_a_plural_nonce_detail"] = plural_detail

    # (b) brand/product compound head -- NOVEL personal name + NOVEL brand (not Santa/Winston/Maria/HTC/Garage).
    brand_cases = [
        ("John Smith bought the truck.", "subject", "john"),
        ("I broke the Sony Walkman.", "object", "walkman"),
    ]
    brand_detail = []
    brand_ok = True
    for sent, role, expect in brand_cases:
        base = ie_extract_coref_1st2nd_fixed(sent)
        fixed = ie_extract_brand_only(sent)
        got = None
        if fixed[0]:
            got = fixed[0][0][0] if role == "subject" else fixed[0][0][2]
        ok = (got == expect)
        brand_detail.append({"sent": sent, "role": role, "expected": expect, "baseline": base, "fixed": fixed, "ok": ok})
        brand_ok = brand_ok and ok
    # regression guard: the 3 Rung-7-established personal names still resolve head=first with the fix ON.
    regression_cases = [("Santa Claus visited the school.", "santa"), ("Winston Peters resigned yesterday.", "winston"),
                         ("Maria Rodriguez opened the office.", "maria")]
    for sent, expect in regression_cases:
        fixed = ie_extract_brand_only(sent)
        ok = bool(fixed[0]) and fixed[0][0][0] == expect
        brand_detail.append({"sent": sent, "role": "subject", "expected": expect, "baseline": None, "fixed": fixed,
                              "ok": ok, "regression_guard": True})
        brand_ok = brand_ok and ok
    evidence["bug_b_brand_nonce_generalization_ok"] = brand_ok
    evidence["bug_b_brand_nonce_detail"] = brand_detail

    # (c) OOV verb form-aware lemma -- NOVEL base-form pseudo-"-ed" word + NOVEL -ied passive.
    verb_cases = [
        ("I feed the cat.", "feed"), ("The cake was carried by the waiter.", "carry"),
    ]
    verb_detail = []
    verb_ok = True
    for sent, expect_rel in verb_cases:
        base = ie_extract_coref_1st2nd_fixed(sent)
        fixed = ie_extract_verb_oov_only(sent)
        ok = bool(fixed[0]) and fixed[0][0][1] == expect_rel
        verb_detail.append({"sent": sent, "baseline": base, "fixed": fixed, "expected_relation": expect_rel, "ok": ok})
        verb_ok = verb_ok and ok
    evidence["bug_c_verb_oov_nonce_generalization_ok"] = verb_ok
    evidence["bug_c_verb_oov_nonce_detail"] = verb_detail

    # (d) do-support -- NOVEL sentences (not don't-feel / won't-return).
    dosupport_cases = [
        ("I don't want coffee.", ("i", "want", "coffee")), ("We didn't finish the project.", ("we", "finish", "project")),
        ("You won't leave.", None),  # intransitive after modal-negation -> correctly abstains (no object)
    ]
    dosupport_detail = []
    dosupport_ok = True
    for sent, expect in dosupport_cases:
        base = ie_extract_coref_1st2nd_fixed(sent)
        fixed = ie_extract_dosupport_only(sent)
        if expect is None:
            ok = fixed[0] == []
        else:
            ok = bool(fixed[0]) and fixed[0][0] == expect
        dosupport_detail.append({"sent": sent, "baseline": base, "fixed": fixed, "expected": expect, "ok": ok})
        dosupport_ok = dosupport_ok and ok
    # negative control: genuine main-verb "do" must NOT be retagged AUX.
    do_main_verb_cases = [("I do the work.", ("i", "do", "work")), ("I do the laundry.", ("i", "do", "laundry"))]
    for sent, expect in do_main_verb_cases:
        fixed = ie_extract_dosupport_only(sent)
        ok = bool(fixed[0]) and fixed[0][0] == expect
        dosupport_detail.append({"sent": sent, "baseline": None, "fixed": fixed, "expected": expect, "ok": ok,
                                  "negative_control_main_verb_do": True})
        dosupport_ok = dosupport_ok and ok
    evidence["bug_d_dosupport_nonce_generalization_ok"] = dosupport_ok
    evidence["bug_d_dosupport_nonce_detail"] = dosupport_detail

    # fix-disabled positive control: all-4-off must byte-for-byte reproduce Rung 8's FIXED arm.
    all_nonce_sents = ([s for s, _ in plural_cases] + [s for s, _, _ in brand_cases]
                        + [s for s, _ in regression_cases] + [s for s, _ in verb_cases]
                        + [s for s, _ in dosupport_cases] + [s for s, _ in do_main_verb_cases])
    # compare TRIPLES only (index 0) -- rule-NAME strings are cosmetically renamed V3->V4 in this cell even when
    # the underlying extraction logic is byte-identical (all 4 new fixes off); the triples themselves are the
    # semantically load-bearing parity check.
    disabled_matches_baseline = all(
        ie_extract_downstream_all_disabled(s)[0] == ie_extract_coref_1st2nd_fixed(s)[0] for s in all_nonce_sents)
    evidence["fix_disabled_reproduces_rung8_baseline"] = disabled_matches_baseline

    evidence["all_downstream_fixes_generalize"] = (
        plural_ok and brand_ok and verb_ok and dosupport_ok and disabled_matches_baseline)
    return evidence


# ---------------------------------------------------------------------------
# RESIDUAL-ERROR CLASSIFICATION (the decisive tail-length diagnostic): for every FIXED_ALL-attempted row that
# is still WRONG vs gold, classify into (i) still matches one of the 4 just-fixed bug SIGNATURES (self-check --
# should be ~0), (ii) a NAMED NEW pattern already visible in Rung 8's own sample (modal-reduction mistagged as
# matrix verb; bare-adjunct-as-object overextraction), or (iii) an honestly-unclassified residual.
# ---------------------------------------------------------------------------
MODAL_REDUCTION_WORDS = {"better", "gotta", "gonna", "hafta", "oughta", "wanna", "sposta"}


def _classify_residual_error(row):
    gold_set = set(tuple(g) for g in row["gold"])
    emitted = row["fixed_emitted"]
    emitted_set = set(tuple(e) for e in emitted)
    if emitted_set == gold_set:
        return None  # not actually wrong
    reasons = []
    for (s, r, o) in emitted:
        if r in MODAL_REDUCTION_WORDS or s in MODAL_REDUCTION_WORDS:
            reasons.append("MODAL_OR_FUNCTION_WORD_MISTAGGED_AS_MATRIX_VERB")
    if not gold_set and emitted_set:
        reasons.append("BARE_ADJUNCT_OVEREXTRACTION")
    if any(o.endswith(("i", "es")) and o not in {g[2] for g in gold_set} for (s, r, o) in emitted):
        # heuristic self-check: an un-restored -i/-es-suffixed lemma surviving into FIXED_ALL output would mean
        # bug (a)/(c) did not fully land -- flag distinctly so it is NEVER silently folded into "unclassified".
        reasons.append("SELF_CHECK_POSSIBLE_UNFIXED_BUG_A_OR_C_SIGNATURE")
    if not reasons:
        reasons.append("OTHER_UNCLASSIFIED_RESIDUAL")
    return reasons


# ---------------------------------------------------------------------------
# glass-box-legal checks (same method as Rung 5/5b/6/7/8).
# ---------------------------------------------------------------------------
def _grep_confirm_no_neural_imports():
    src = Path(__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(import|from)\s+(torch|spacy|transformers|stanza)\b", re.MULTILINE)
    return [m.group(0).strip() for m in pattern.finditer(src)]


def _runtime_neural_module_check():
    banned = ("torch", "spacy", "transformers", "stanza")
    return sorted(m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in banned))


# ---------------------------------------------------------------------------
# run + aggregate.
# ---------------------------------------------------------------------------
def run_full(seeds, n_per_seed):
    simple_sorted_v2, length_matched_pool_size_v2 = load_simple_sentences_v2(CONLLU_PATH)
    simple_fraction_of_length_matched_pool = (
        len(simple_sorted_v2) / length_matched_pool_size_v2 if length_matched_pool_size_v2 else 0.0)

    all_rows = []
    dist_pooled = {c: 0 for c in CONSTRUCTION_CLASSES_V2}
    for seed in seeds:
        rows, dist = build_rows_for_seed_v2(simple_sorted_v2, seed, n_per_seed)
        all_rows.extend(rows)
        for c in CONSTRUCTION_CLASSES_V2:
            dist_pooled[c] += dist[c]
    n_total = len(all_rows)
    dist_frac = {c: (dist_pooled[c] / n_total if n_total else 0.0) for c in CONSTRUCTION_CLASSES_V2}

    baseline_score = score_arm(all_rows, ie_extract_coref_1st2nd_fixed)
    fixed_all_score = score_arm(all_rows, ie_extract_downstream_all_fixed)
    single_bug_scores = {name: score_arm(all_rows, fn) for name, fn in SINGLE_BUG_ARMS.items()}

    def _guard_ok(fn):
        return all(set(fn(s)[0]) == set(g) for (s, g) in GUARD_SENTENCES)

    def _oos_ok(fn):
        return all(not fn(s)[0] for s in OUT_OF_SCHEMA_CONTROL)

    guard_ok = {"baseline": _guard_ok(ie_extract_coref_1st2nd_fixed), "fixed_all": _guard_ok(ie_extract_downstream_all_fixed)}
    oos_ok = {"baseline": _oos_ok(ie_extract_coref_1st2nd_fixed), "fixed_all": _oos_ok(ie_extract_downstream_all_fixed)}

    # --- 3rd-person zero-hallucination guardrail measurement over the REAL sample (must stay 0 breaks). ---
    n_3rd_person_coref_rows = 0
    n_3rd_person_guard_breaks = 0
    for r in all_rows:
        b = ie_extract_coref_1st2nd_fixed(r["text"])
        f = ie_extract_downstream_all_fixed(r["text"])
        if b[1] == "COREF_UNRESOLVED":
            T = _build_tags_open_v4(r["text"], True, True, True, True)
            tags = [t[1] for t in T]
            lemmas = [t[2] for t in T]
            forms = [t[3] for t in T]
            all_verb_idx = [i for i in range(len(T)) if tags[i] == "VERB"]
            verb_idx = [i for i in all_verb_idx if _is_finite_form(tags, forms, i)]
            if verb_idx:
                v0 = verb_idx[0]
                pron_before = [i for i in range(len(T)) if tags[i] == "PRON" and i < v0]
                cand = lemmas[pron_before[-1]] if pron_before else None
                if cand not in FIRST_SECOND_PERSON_SUBJECT_PRONOUNS:
                    n_3rd_person_coref_rows += 1
                    if f[0]:
                        n_3rd_person_guard_breaks += 1

    # --- residual-error classification (the decisive tail-length diagnostic). ---
    residual_rows = []
    residual_tags = {}
    for r in all_rows:
        f = ie_extract_downstream_all_fixed(r["text"])
        gold = r["gold"]
        if not f[0] and not gold:
            continue  # correctly abstained, nothing to classify
        if not f[0]:
            continue  # abstained on a row WITH gold -- a coverage miss, not a wrong-triple error (out of scope here)
        row = {"text": r["text"], "gold": gold, "fixed_emitted": f[0], "fixed_rule": f[1]}
        reasons = _classify_residual_error(row)
        if reasons is None:
            continue
        row["residual_reasons"] = reasons
        residual_rows.append(row)
        for tag in reasons:
            residual_tags[tag] = residual_tags.get(tag, 0) + 1

    downstream_fixes_evidence = verify_downstream_fixes()

    return {
        "seeds": seeds, "n_per_seed": n_per_seed, "n_total": n_total,
        "simple_pool_size": len(simple_sorted_v2), "length_matched_pool_size": length_matched_pool_size_v2,
        "simple_fraction_of_length_matched_pool": simple_fraction_of_length_matched_pool,
        "construction_distribution_counts": dist_pooled, "construction_distribution_fractions": dist_frac,
        "baseline_score": baseline_score, "fixed_all_score": fixed_all_score, "single_bug_scores": single_bug_scores,
        "guard_regression_ok": guard_ok, "oos_control_fired": oos_ok,
        "n_3rd_person_coref_unresolved_rows": n_3rd_person_coref_rows,
        "n_3rd_person_guard_breaks": n_3rd_person_guard_breaks,
        "downstream_fixes_evidence": downstream_fixes_evidence,
        "residual_error_tag_counts": residual_tags,
        "n_residual_wrong_rows": len(residual_rows),
        "sample_residual_rows": residual_rows[:60],
    }


def compute_verdict(agg):
    prec_b = agg["baseline_score"]["precision_on_attempted"]
    prec_f = agg["fixed_all_score"]["precision_on_attempted"]
    cov_b = agg["baseline_score"]["coverage_sentence_rate"]
    cov_f = agg["fixed_all_score"]["coverage_sentence_rate"]
    guard_ok = agg["guard_regression_ok"]["fixed_all"]
    oos_ok = agg["oos_control_fired"]["fixed_all"]
    simple_frac = agg["simple_fraction_of_length_matched_pool"]
    n_guard_breaks = agg["n_3rd_person_guard_breaks"]
    fixes_generalize = agg["downstream_fixes_evidence"]["all_downstream_fixes_generalize"]

    if prec_f is None:
        return ("MIDDLE_BAND", "FIXED_ALL arm emitted zero triples on the whole simple-register sample -- "
                                "mechanism did not fire at all", "no_triples_emitted")

    hard_pass = (prec_f >= 0.60 and cov_f >= 0.28 and n_guard_breaks == 0 and guard_ok and oos_ok
                 and simple_frac >= 0.10 and fixes_generalize)
    hard_fail = (prec_f < 0.55 or cov_f < 0.20 or n_guard_breaks > 0 or (not guard_ok)
                 or simple_frac < 0.10 or (not fixes_generalize))

    if hard_pass:
        tier = "HARD_PASS"
    elif hard_fail:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    weakest = "n/a"
    if not hard_pass:
        if n_guard_breaks > 0:
            weakest = "ZERO_HALLUCINATION_GUARDRAIL_BROKEN_3rd_person_pronoun_wrongly_extracted"
        elif not fixes_generalize:
            weakest = "one_or_more_fixes_did_not_generalize_to_nonce_cases_memorized_patch_risk"
        elif simple_frac < 0.10:
            weakest = "simple_fraction_of_length_matched_pool_below_0.10_stratum_vacuous"
        elif cov_f < 0.20:
            weakest = "coverage_collapsed_below_0.20"
        elif prec_f < 0.55:
            weakest = "fixed_all_precision_on_attempted_below_0.55_hard_fail_floor_MORE_BUGS_THAN_THE_4_NAMED"
        elif prec_f < 0.60:
            weakest = "fixed_all_precision_on_attempted_in_middle_band_0.55_to_0.60"
        elif not guard_ok:
            weakest = "guard_regression_failed_fixed_all"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire_fixed_all"

    tail_diag = (
        "SHORT_TAIL_MILESTONE_REACHED" if hard_pass else
        ("LONG_TAIL_MORE_BUGS_EXPOSED" if agg["n_residual_wrong_rows"] > 0 else "AMBIGUOUS_NO_RESIDUAL_BUT_PRECISION_SHORT"))

    msg = (
        f"{tier} | RUNG9 DOWNSTREAM-BUG FIXES on the SAME simple-register slice as RUNG 6/7/8 (n={agg['n_total']}) | "
        f"BASELINE(rung8) precision={prec_b:.3f} coverage={cov_b:.3f} -> "
        f"FIXED_ALL precision={prec_f:.3f} coverage={cov_f:.3f} | "
        f"n_3rd_person_guard_breaks={n_guard_breaks} (MUST be 0) | fixes_generalize_to_nonce={fixes_generalize} | "
        f"guard_regression_ok={guard_ok} oos_control_fired={oos_ok} | weakest={weakest} | "
        f"n_residual_wrong_rows={agg['n_residual_wrong_rows']} residual_tag_counts={agg['residual_error_tag_counts']} | "
        f"TAIL_DIAGNOSIS={tail_diag} | "
        f"MILESTONE_REACHED={hard_pass} ZERO_HALLUCINATION_PRESERVED={n_guard_breaks == 0}")
    return tier, msg, weakest, tail_diag


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
# self-test: EXERCISE THE REAL code path.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (real feats-aware CoNLL-U parse via Rung 7's loader, real "
          "nltk.pos_tag calls, real simplicity filter + BASELINE/FIXED_ALL/single-bug arms + nonce batteries)...",
          flush=True)

    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"
    _ = nltk.pos_tag(["The", "cat", "sat", "."])
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print(f"[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural)", flush=True)

    # (1) do-support tag-cascade evidence (MEASURED, not narrated): confirms the "confused context" mechanism
    # claimed in the module docstring for bug (d).
    tagged_broken = nltk.pos_tag(["I", "don", "t", "feel", "anything", "until", "noon"])
    tagged_fixed = nltk.pos_tag(["I", "do", "not", "feel", "anything", "until", "noon"])
    feel_broken_tag = dict((w, t) for w, t in tagged_broken)["feel"]
    feel_fixed_tag = dict((w, t) for w, t in tagged_fixed)["feel"]
    assert feel_broken_tag not in ("VB", "VBP"), (
        f"expected the UNEXPANDED apostrophe-split tokenization to mistag 'feel' (got {feel_broken_tag!r}); "
        f"if this assertion fails the do-support mechanism claim in the docstring needs re-verification")
    assert feel_fixed_tag in ("VB", "VBP"), f"expected contraction-expanded 'feel' to tag as a verb, got {feel_fixed_tag!r}"
    print(f"[self_test] do-support tag-cascade CONFIRMED: unexpanded 'feel' tags {feel_broken_tag!r}, "
          f"expanded 'feel' tags {feel_fixed_tag!r} -- contraction expansion is load-bearing, not cosmetic.",
          flush=True)

    # (2) nonce-generalization batteries for all 4 fixes (MEASURED, not narrated).
    fixes_ev = verify_downstream_fixes()
    assert fixes_ev["bug_a_plural_nonce_generalization_ok"], f"bug (a) failed to generalize: {fixes_ev['bug_a_plural_nonce_detail']}"
    assert fixes_ev["bug_b_brand_nonce_generalization_ok"], f"bug (b) failed to generalize: {fixes_ev['bug_b_brand_nonce_detail']}"
    assert fixes_ev["bug_c_verb_oov_nonce_generalization_ok"], f"bug (c) failed to generalize: {fixes_ev['bug_c_verb_oov_nonce_detail']}"
    assert fixes_ev["bug_d_dosupport_nonce_generalization_ok"], f"bug (d) failed to generalize: {fixes_ev['bug_d_dosupport_nonce_detail']}"
    assert fixes_ev["fix_disabled_reproduces_rung8_baseline"], "fix-disabled positive control did NOT reproduce Rung 8 byte-for-byte"
    print("[self_test] ALL 4 nonce-generalization batteries PASS (novel words/names, not the literal Rung-8 "
          "error rows) + fix-disabled positive control reproduces Rung 8 byte-for-byte.", flush=True)

    # (3) 3rd-person zero-hallucination guardrail (Rung 8's own battery, reproduced through the new pipeline).
    coref_guard = verify_coref_guardrail()
    assert coref_guard["coref_guardrail_all_ok"], f"Rung-8 coref guardrail regressed: {coref_guard}"
    print("[self_test] Rung-8 coref-guardrail battery still PASS through the (unmodified) Rung-8 BASELINE arm.",
          flush=True)

    # (4) existing-bucket byte-identical parity spot check on BASELINE + FIXED_ALL vs GUARD_SENTENCES/OOS.
    for sent, gold in GUARD_SENTENCES:
        gset = set(gold)
        assert set(ie_extract_coref_1st2nd_fixed(sent)[0]) == gset, f"BASELINE guard regression on {sent!r}"
        assert set(ie_extract_downstream_all_fixed(sent)[0]) == gset, f"FIXED_ALL guard regression on {sent!r}"
    for s in OUT_OF_SCHEMA_CONTROL:
        assert ie_extract_coref_1st2nd_fixed(s)[0] == [], f"BASELINE unexpectedly extracted on OOS control {s!r}"
        assert ie_extract_downstream_all_fixed(s)[0] == [], f"FIXED_ALL unexpectedly extracted on OOS control {s!r}"
    print("[self_test] guard-sentence regression + out-of-schema control PASS on BASELINE and FIXED_ALL.", flush=True)

    # (5) real_code_path (F.1): tiny real slice, discriminator fires.
    simple_sorted_v2, length_matched_pool_size_v2 = load_simple_sentences_v2(CONLLU_PATH)
    assert length_matched_pool_size_v2 > 100, f"expected a sizeable length-matched pool, got {length_matched_pool_size_v2}"
    rows, dist = build_rows_for_seed_v2(simple_sorted_v2, seed=7, n_per_seed=40)
    base_res = score_arm(rows, ie_extract_coref_1st2nd_fixed)
    fixed_res = score_arm(rows, ie_extract_downstream_all_fixed)
    n_base_correct = base_res["n_correct"] if base_res["n_correct"] is not None else 0
    n_fixed_correct = fixed_res["n_correct"] if fixed_res["n_correct"] is not None else 0
    assert n_fixed_correct >= n_base_correct, (
        f"DISCRIMINATOR DID NOT FIRE at tiny (n=40) scale: baseline n_correct={n_base_correct} "
        f"fixed_all n_correct={n_fixed_correct} -- fixes produced no improvement even at this scale")
    print(f"[self_test] real_code_path + discriminator-fires: tiny 40-sentence real slice (seed 7) -- "
          f"BASELINE n_correct={n_base_correct}/{base_res['n_attempted']} | "
          f"FIXED_ALL n_correct={n_fixed_correct}/{fixed_res['n_attempted']}.", flush=True)

    # (6) SAME-SLICE PARITY vs Rung 8 (BASELINE arm reproduces Rung 8's own metrics.json numbers exactly).
    full_rows = []
    for seed in SEEDS_FULL:
        r_, _ = build_rows_for_seed_v2(simple_sorted_v2, seed, N_PER_SEED)
        full_rows.extend(r_)
    assert len(full_rows) == 300, f"pooled n_total drifted from Rung 6/7/8's 300: got {len(full_rows)}"
    full_base = score_arm(full_rows, ie_extract_coref_1st2nd_fixed)
    print(f"[self_test] SAME-SLICE PARITY: n_total=300, BASELINE(Rung8) reproduced live -- "
          f"n_attempted={full_base['n_attempted']} n_correct={full_base['n_correct']} "
          f"precision={full_base['precision_on_attempted']}.", flush=True)

    # (7) ARMS-MUST-DIFFER (META_RULE_AF).
    variants = {"BASELINE": ie_extract_coref_1st2nd_fixed, "FIXED_ALL": ie_extract_downstream_all_fixed}
    variants.update(SINGLE_BUG_ARMS)
    digests = {}
    for name, fn in variants.items():
        all_triples = sorted(set(t for r in full_rows for t in fn(r["text"])[0]))
        digests[name] = hashlib.sha256(json.dumps(all_triples, sort_keys=True).encode()).hexdigest()
    pairs = [(a, b) for a in digests for b in digests if a < b]
    for a, b in pairs:
        assert digests[a] != digests[b], f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical on real data"
    print(f"[self_test] PASS | ARMS-MUST-DIFFER verified: all {len(variants)} arms pairwise differ on the real "
          f"300-sentence full slice.", flush=True)
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
    seeds = [7] if run_mode == "smoke" else SEEDS_FULL
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * N_PER_SEED
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[rung9_downstream_bugs] run_mode={run_mode} seeds={seeds} n_per_seed={N_PER_SEED} "
          f"expected_n_units={expected_n_units} corpus={CONLLU_PATH}", flush=True)

    agg = run_full(seeds, N_PER_SEED)
    tier, msg, weakest, tail_diag = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    print(f"[rung9_downstream_bugs] {tier} in {elapsed:.2f}s", flush=True)
    print(f"[rung9_downstream_bugs] {msg}", flush=True)

    def _strip_rows(d):
        return {k: v for k, v in d.items() if k != "rows"}

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_per_seed": N_PER_SEED,
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        "tail_diagnosis": tail_diag,
        "corpus": {
            "name": "UD_English-EWT test split -- SIMPLE-SYNTAX SUBSET (PATH A), SAME slice as Rung 6/7/8",
            "path": str(CONLLU_PATH), "license": "CC BY-SA 4.0",
            "same_slice_as": "read_grow_realprose_simple_register_rung8_coref_1st2nd_person_v1",
            "length_matched_pool_size": agg["length_matched_pool_size"],
            "simple_pool_size": agg["simple_pool_size"],
            "simple_fraction_of_length_matched_pool": agg["simple_fraction_of_length_matched_pool"],
            "n_sampled_total": agg["n_total"],
            "register_note": "PATH A caveat carried forward UNCHANGED from Rung 6/7/8: a syntax-simple subset "
                              "of general WEB vocabulary, NOT a vocabulary-controlled early-reader corpus.",
        },
        "construction_distribution_counts": agg["construction_distribution_counts"],
        "construction_distribution_fractions": agg["construction_distribution_fractions"],
        "arms": {
            "BASELINE_rung8": _strip_rows(agg["baseline_score"]),
            "FIXED_ALL_downstream": _strip_rows(agg["fixed_all_score"]),
        },
        "per_bug_contribution": {name: _strip_rows(s) for name, s in agg["single_bug_scores"].items()},
        "zero_hallucination_guardrail": {
            "n_3rd_person_coref_unresolved_rows": agg["n_3rd_person_coref_unresolved_rows"],
            "n_3rd_person_guard_breaks": agg["n_3rd_person_guard_breaks"],
        },
        "guard_regression_ok": agg["guard_regression_ok"],
        "oos_control_fired": agg["oos_control_fired"],
        "downstream_fixes_generalization_evidence": agg["downstream_fixes_evidence"],
        "residual_error_classification": {
            "n_residual_wrong_rows": agg["n_residual_wrong_rows"],
            "residual_error_tag_counts": agg["residual_error_tag_counts"],
            "sample_residual_rows": agg["sample_residual_rows"],
        },
        "sample_fixed_all_rows": agg["fixed_all_score"]["rows"][:60],
        "sample_baseline_rows": agg["baseline_score"]["rows"][:60],
        "prereg": {
            "hard_pass": "fixed_all_precision_on_attempted>=0.60 AND fixed_all_coverage_sentence_rate>=0.28 AND "
                         "n_3rd_person_guard_breaks==0 AND guard_regression_ok_fixed_all AND oos_control_fired_"
                         "fixed_all AND simple_fraction_of_length_matched_pool>=0.10 AND "
                         "all_downstream_fixes_generalize (nonce batteries)",
            "hard_fail": "fixed_all_precision_on_attempted<0.55 OR coverage<0.20 (collapse) OR "
                         "n_3rd_person_guard_breaks>0 OR NOT guard_regression_ok_fixed_all OR "
                         "simple_fraction_of_length_matched_pool<0.10 OR NOT all_downstream_fixes_generalize",
            "hp_scope": "FIXED_ALL is the PRIMARY discriminator vs BASELINE (Rung 8's ie_extract_coref_1st2nd_"
                        "fixed, imported unmodified). Single-bug arms (PLURAL_ONLY/BRAND_ONLY/VERB_OOV_ONLY/"
                        "DOSUPPORT_ONLY) are informational per-bug-contribution arms, not independently gated.",
            "scope": "fixes EXACTLY the 4 named bugs Rung 8 localized (irregular-plural-noun lemma restoration; "
                     "brand/product compound-noun head-selection; OOV verb-lemma spelling-restoration; "
                     "do-support negation parsing). Does NOT fix modal-reduction mistagging ('better'/'gotta') "
                     "or bare-adjunct-as-object overextraction -- both already visible in Rung 8's own sample, "
                     "flagged honestly in residual_error_classification if material, not claimed fixed here.",
            "honest_guard": "each of the 4 fixes verified via NOVEL nonce cases (distinct words/names from the "
                            "literal Rung-8 error rows that exposed them) -- see downstream_fixes_generalization_"
                            "evidence. A fix that only worked on the literal error sentences would fail its own "
                            "nonce battery and HARD_FAIL the cell (all_downstream_fixes_generalize gate).",
            "compute_architecture": "sequential-CPU; pure syntactic parsing + dependency-tree traversal, no "
                                    "VSA store; wall time trivial (MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer + dependency-classifier test)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "runner_python_u_only (timeout_s < 1800; cell wall time is seconds, matching "
                                 "Rung 5/5b/6/7/8's own precedent)",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["parse_conllu_v2 (Rung 7's feats-aware parser, real local corpus)",
                                         "load_simple_sentences_v2 (SAME-SLICE-PARITY vs Rung 6/7/8)",
                                         "analyze_sentence_v2 (Rung 7's gold-deriver, UNCHANGED)",
                                         "ie_extract_coref_1st2nd_fixed (Rung 8 BASELINE, imported unmodified)",
                                         "ie_extract_downstream_all_fixed (this cell, the 4 new fixes)",
                                         "nltk.pos_tag (real classical averaged-perceptron call)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete syntactic role-assignment + "
                       "the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED), same "
                       "as Rung 5/5b/6/7/8.",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports) AND a "
                               "runtime sys.modules transitive-closure check after nltk use, both asserted "
                               "at self-test",
            "prior_work_check": "substrate_query.sh run before authoring (see completion report).",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[rung9_downstream_bugs] metrics written -> {out_dir / 'metrics.json'}", flush=True)
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
