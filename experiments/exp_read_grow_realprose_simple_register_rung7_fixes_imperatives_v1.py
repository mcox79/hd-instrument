"""exp_read_grow_realprose_simple_register_rung7_fixes_imperatives_v1 -- RUNG 7: fixes the 3 localized bugs
the Rung-6 VET's complete error taxonomy identified (irregular-verb lemma lookup-ordering; multi-token
proper/compound-noun HEAD selection; subject selection picking the linearly-LAST pre-verb noun instead of the
syntactic head), ADDS handling for the IMPERATIVE construction (53/93 of Rung 6's "other_unhandled" rows,
currently permanently unhandled + a documented FALSE-POSITIVE source via "Please" mis-tagged as subject), and
re-measures GATED precision on the SAME simple-syntax UD-EWT slice Rung 6 measured.

TRIGGER (verbatim scope, Rung-6 VET a3cac63c, commit c71a9eec7, complete error taxonomy -- ADOPT EXACTLY THIS
SCOPE, no more, no less): Rung 6 HARD_FAILed the register-advantage question at GATED precision=0.379 on the
simple register (n=300, n_attempted=26, n_correct=11) -- NOT from a coverage wall, but from 3 localized, fixable
bugs plus one large unhandled CONSTRUCTION GAP:
  BUG 1 (irregular-verb lemma LOOKUP-ORDERING): the suffix-stripper corrupts "has"->"ha" BEFORE the irregular-
    lemma table (`IRREGULAR_VERB_LEMMA`, already defined in Rung 5, previously only used as a POST-HOC
    diagnostic rescoring pass, `_relax_irregular_verb`) is ever consulted -- so "has"->"ha" is never fixed on
    the PRIMARY scoring arm. FIX: run the irregular-verb lookup FIRST, inside the tagger itself
    (`_tag_token_open_v2`), before the lookup-free suffix-stripping fallback -- not as a post-hoc table.
  BUG 2 (multi-token compound-noun HEAD SELECTION): "Santa Claus"->"clau", "customer service"->"customer"
    (picks the WRONG token of a multi-noun span). FIX: select the syntactic HEAD of a contiguous multi-NOUN
    span, not a naive single-token pick.
  BUG 3 (SUBJECT SELECTION picks the linearly-LAST noun before the matrix verb, not the syntactic head):
    PP-modified subjects resolve wrong ("the correction to the working gas" -> "gas" instead of "correction").
    FIX: select the syntactic subject HEAD (the first contiguous noun-run before any PP boundary), not the
    linearly-last pre-verb noun.
  CONSTRUCTION GAP (PRIORITIZED, the core early-reader gap) -- IMPERATIVES: no nsubj -> the existing schema
    marks these permanently unhandled ("other_unhandled", "no_subject") AND, worse, they currently cause FALSE
    POSITIVES ("Please" POS-tag-promoted to NOUN and mis-selected as the subject: MEASURED@rung6-metrics.json
    sample_gated_rows, two REAL landed false-positive rows reproduced live below -- "Please return an executed
    copy of confirm to me." wrongly emitted ('please','return','copy'); "Please, ask Stinson as well." wrongly
    emitted ('please','ask','stinson')). FIX: recognize the imperative pattern (no subject noun/pronoun before
    a base-form finite verb) and EXTRACT as (implicit-addressee "you", verb[+prep], object) rather than merely
    abstaining, per the contract's stated preference for extraction over bare abstention.

HEAD-SELECTION RULE (bugs 2+3 share one general mechanism, not two separate patches): given a maximal
CONTIGUOUS run of NOUN-tagged tokens (positions i, i+1, i+2, ... with no DET/ADJ/PREP boundary between them),
`_np_head_from_run` picks the head by ORIGINAL-CASE capitalization -- if EVERY token in the run is capitalized
in the source text, it is a UD "flat" multi-word PROPER-NAME span (Santa Claus, Winston Peters) and the head is
the LEFTMOST token (UD attaches later name-words to the first via `flat`); otherwise it is a UD "compound"
common-noun modifier+head span (customer service, football team captain) and the head is the RIGHTMOST token
(UD attaches the modifier to the head noun it precedes via `compound`). For the SUBJECT side, the candidate
noun-run is additionally restricted to the FIRST contiguous run walking forward from the start of the subject
region (`_first_contiguous_noun_run`) -- this is what fixes the PP-modified-subject case: a PREP token (e.g.
"to" in "the correction to the report") breaks contiguity, so a noun inside a trailing PP ("report") is never
even a head-run candidate; only "correction" (before the PP) is. This is a single, general, closed-form rule
(no sentence-specific patching) applied uniformly to subject selection, object selection, AND passive by-agent
selection (all three call sites shared the same underlying single-token-pick bug).

IMPERATIVE HANDLING -- EXTRACT, not abstain-only (this cell's call, per the contract's explicit license):
  EXTRACTOR side (`_extract_core_open_gated_v2`, purely classical POS-tag-driven, NO gold access): when a
  base-form (VB-tag) finite verb candidate has NO noun or pronoun anywhere before it in the token stream, the
  sentence is recognized as an imperative; the implicit addressee "you" becomes the subject and the existing
  object-scan logic (extended to also skip PRON tokens, e.g. "her" in "Take her to the vet." -- a closed-class
  function word with no derivable lemma content, same principle as the pre-existing DET/ADJ/ADV/AUX skip-list)
  resolves the object. A recognized imperative with NO object noun (e.g. an intransitive command) correctly
  ABSTAINS (`ABSTAIN_IMPERATIVE_NO_OBJECT`) rather than emitting a subjectless partial guess -- there is no SVO
  triple to derive from an intransitive clause, matching the schema, not a failure of the mechanism.
  DISCOURSE-MARKER FIX (closes the "Please" false-positive class, general not sentence-specific): sentence-
  INITIAL "please" is POSITION-SCOPED overridden to a new closed tag DISC (never eligible as a subject noun or
  a verb) -- MEASURED at self_test that the classical tagger is CONTEXT-FRAGILE on this exact word (tags it
  NOUN in one real sentence, VERB in another, for the IDENTICAL word, depending only on downstream context),
  so a closed-class override removes reliance on that inconsistency for this one genuinely closed-class
  politeness/discourse marker. Scoped to POSITION 0 only (not a blanket word-level ban) so genuine verb usage
  of "please" elsewhere ("She tries to please her boss.") is untouched -- verified NOT to regress at self_test.
  GOLD-DERIVER side (`analyze_sentence_v2` / `_derive_imperative_gold`, extends Rung 5's `analyze_sentence`):
  per the contract's own instruction, scoring imperative extraction requires GOLD to exist for imperative rows
  too (the original `analyze_sentence` requires nsubj and returns `other_unhandled`/`no_subject`/no-gold for
  every imperative, so imperative extractions -- right or wrong -- were previously UNCREDITABLE). The PRIMARY
  signal is UD's own Mood=Imp morphological feature on the root verb (authoritative, MEASURED@corpus: 178
  occurrences of "Mood=Imp" in the local corpus file -- non-vacuous), captured by a new feats-aware CoNLL-U
  parser (`parse_conllu_v2`); a purely-structural fallback (root is the clause-initial token, no nsubj/csubj)
  covers rows where feats is unavailable, reported SEPARATELY (`n_imperative_by_feats` vs
  `n_imperative_by_structural_fallback`) so a reader can see how much of the new imperative gold rests on the
  authoritative UD signal vs the softer structural approximation.

DECLARED RESIDUAL (NOT claimed fixed, MEASURED and reported honestly, not hidden): very short (2-3 token) bare
imperative sentences where the classical POS tagger itself mistags the sentence-INITIAL verb as a proper noun
(e.g. "Sit down." -> "Sit" tagged NOUN; "Look at the cat." -> "Look" tagged NOUN) are NOT recognized as
imperatives by this cell's mechanism, because there is no VERB-tagged token in the sentence at all for the
imperative-recognition branch to ever see -- a TAGGER-ACCURACY limitation (averaged-perceptron taggers are
known to lean on sentence-initial-capitalization as a strong NNP cue, and these bare fragments give the tagger
minimal context to override that prior), NOT a grammar-logic gap, and OUTSIDE this cell's declared scope
(irregular-verb lookup-ordering, head-selection, imperative CONSTRUCTION recognition -- not expanding the
closed VERB_LEX lexicon or hacking the tagger's capitalization handling). MEASURED at self_test: these bare
cases still cleanly ABSTAIN (`NO_VERB`, no false positive) rather than false-firing, which satisfies the
contract's stated MINIMUM bar ("at minimum, cleanly ABSTAIN") even though the "ideally extract" bar is not met
for this specific residual class. The two REAL Rung-6 documented false-positive imperatives ("Please return...",
"Please, ask Stinson...") both have their verb in NON-initial position (after "Please"), where the classical
tagger DOES correctly recognize it as VERB -- so this cell's fix DOES correctly extract both of them (verified
live below, not merely narrated).

HONEST GUARD (contract-mandated, verified not just asserted): none of the fixes above are patches keyed to the
literal Rung-6 error sentences. BUG 1's fix reuses the EXISTING, already-in-the-codebase `IRREGULAR_VERB_LEMMA`
table (Rung 5) wholesale, just re-ordered -- not a new hand-tuned table. BUGS 2/3's fix is a single general
capitalization-based head-selection rule, verified at self_test against BOTH the 2 doc-cited proper names
(Santa Claus, Winston Peters) AND 2 genuinely NOVEL nonce names/constructions never mentioned in this arc
before (Maria Rodriguez; "the correction to the report") plus a compound-object nonce ("football team captain",
a THREE-noun chain never mentioned anywhere) and an explicit REGRESSION GUARD proving an already-correct
compound subject ("customer service team") is NOT disturbed by the fix. The imperative fix is verified against
3 EXTRACTION wins (2 real corpus rows + 1 contract-canonical nonce, "Take her to the vet.") and the DECLARED
residual is measured and reported, not concealed.

ARMS (SAME real simple-syntax UD-EWT slice as Rung 6 -- SAME seeds=[7,13,19], SAME n_per_seed=100, SAME
`load_simple_sentences` filter -- extended ONLY on the GOLD side to derive imperative gold, per the contract's
explicit license "you may extend the filter/gold to INCLUDE imperatives now that they're handled"; the
SIMPLICITY FILTER ITSELF is unchanged and unextended -- imperatives ALREADY structurally satisfy it (single
VERB root, clause_count<=1, token[5-12]) and were ALREADY part of Rung 6's n=300 sample, just mis-bucketed as
other_unhandled by the OLD gold-deriver; MEASURED at self_test that `load_simple_sentences_v2`'s sentence-id
sequence is byte-identical to Rung 6's own `load_simple_sentences`):
  BASELINE = `ie_extract_open_gated` (Rung 5b's GATED extractor, imported UNMODIFIED, re-run live -- this is
    "the Rung-6 pipeline" the contract asks to compare against). Reported BOTH against Rung 6's OLD gold
    (`baseline_reproduction` -- a positive-control SAME-SLICE-PARITY check that must exactly reproduce Rung 6's
    landed n_total=300/n_attempted=26/n_correct=11/precision=0.3793) AND against this cell's EXTENDED gold
    (`baseline_vs_extended_gold`, for apples-to-apples comparison with the 3 fix arms below).
  FIX1 = BASELINE + bug-1 fix only (irregular-verb lookup-ordering). Isolates bug 1's own contribution.
  FIX1_HEAD = FIX1 + bugs 2/3 fix (head selection). Isolates bugs 2/3's own incremental contribution.
  FIX_ALL = FIX1_HEAD + imperative construction handling (the PRIMARY discriminator, "FIXED" in the contract).
  All 4 arms + BASELINE are scored with the SAME `score_arm` CaRB-style function against the SAME
  `all_rows_v2` (extended-gold) row set, so precision deltas between arms isolate EXACTLY one fix at a time.

BANDS (pre-registered, IDENTICAL to the contract's own literal thresholds):
  Primary discriminator = FIX_ALL arm's `precision_on_attempted`.
  HARD-PASS: FIX_ALL precision_on_attempted >= 0.60 AND coverage_sentence_rate >= 0.05 (matches Rung 6's own
    non-vacuous floor) AND guard_regression_ok_fix_all AND oos_control_fired_fix_all AND
    simple_fraction_of_length_matched_pool >= 0.10 AND all_named_bugs_verified_fixed (the live bug-fix-
    verification battery, not just a precision number -- the contract requires the named bugs be
    "demonstrably fixed", not merely that precision happens to clear a threshold).
  HARD-FAIL: FIX_ALL precision_on_attempted < 0.55 (the diagnosis was incomplete -- more is wrong than the
    named 3 bugs + imperative gap, itself informative) OR coverage_sentence_rate < 0.03 (vacuous) OR NOT
    guard_regression_ok_fix_all OR simple_fraction_of_length_matched_pool < 0.10.
  MIDDLE_BAND: otherwise (e.g. precision in [0.55, 0.60), or precision clears 0.60 but a named bug's live
    verification did not fully pass -- reported honestly as partial, not rounded up).
  HONEST CAVEAT CARRIED FORWARD (per contract, NOT claimed closed even on HARD_PASS): PATH A is a simple-
  SYNTAX subset of general WEB VOCABULARY (UD-EWT), not a vocabulary-controlled early-reader corpus. A true
  early-reader-readiness measurement needs a PATH B (OneStopEnglish / Simple-Wikipedia / a decodable-primer
  corpus, imperative-inclusive) -- flagged as the next rung, not claimed closed here even if this cell clears
  the envelope.

COMPUTE: SEEDS=[7,13,19], N_PER_SEED=100 (IDENTICAL to Rung 6, for direct same-slice comparability). Smoke =
  seed[7] only, SAME N_PER_SEED (Option A, discriminator-survives-scale; trivial wall time, matching Rung
  5/5b/6's own precedent -- pure CPU string/POS-tag processing, no torch, no numpy, no VSA store). Local,
  executed DIRECTLY (bash), no queue/GPU/atoms/push. Corpus already fetched + committed (Rung 5's
  `data/corpora/ud_english_ewt/en_ewt-ud-test.conllu`); NO network access at self-test/smoke/full time.
  Storage: no_storage. Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before running.

NEXT (not this cell): (1) PATH B (vocabulary-controlled early-reader corpus) remains the un-collapsed
alternative if the vocabulary-control caveat needs closing; (2) the classical-tagger sentence-initial-
capitalization residual (bare "Sit down."/"Look at the cat."-class imperatives) is a candidate future rung if
imperative RECALL (not just precision/false-positive-elimination) becomes the binding question; (3)
COREF_UNRESOLVED (1st/2nd-person pronoun subjects) remains, BY THE VET's OWN NAMED SCOPE, the dominant
coverage bottleneck in this data (MEASURED@sample_gated_rows: the majority of single_clause_svo misses in
Rung 6's own 60-row sample) -- explicitly OUT OF SCOPE for this cell (not one of the 4 named items), left
unfixed, and reported honestly as the largest remaining lever for a future rung.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; BASELINE vs FIX1 vs FIX1_HEAD vs FIX_ALL emitted-triple-
#   set hashes pairwise differ on the real simple-slice sample by construction).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor; discriminator is discrete syntactic role-assignment + the classical
#   tagger's own literature-benchmarked accuracy (96-97% PTB, CITED), same as Rung 5/5b/6.
# - baseline_in_band: N/A BY DESIGN -- BASELINE's own known Rung-6 precision (0.379, MEASURED@rung6 metrics.json,
#   re-derived live below via `baseline_reproduction`) is the pre-registered floor this cell exists to raise.
# - discriminator survives scale: corpus is FIXED-size real prose, deterministic filtered pool, SAME regime as
#   Rung 6 (no scale axis). Smoke uses the SAME N_PER_SEED as FULL, single seed only (Option A).
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test parses the REAL local corpus file (parse_conllu_v2, feats-aware), applies
#   the REAL simplicity filter, samples a tiny real slice, and runs ALL 4 extraction arms against REAL
#   sentences, plus a battery of live (not narrated) bug-fix verification calls.
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19], inherited unmodified from Rung 5/6's own
#   random.Random(seed).sample over a sorted(...) sentence-id-ordered pool.
# - all numbers in comments tagged HYPOTHESIZED@prereg / MEASURED@metrics / MEASURED@rung6-metrics.json /
#   MEASURED@corpus / CITED@research-note.
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

ANCHOR_NAME = "read_grow_realprose_simple_register_rung7_fixes_imperatives_v1"

# --- GENUINE REUSE: Rung 5 (corpus parser / gold-deriver / scorer / sampler / BASELINE extractor / irregular-
# verb table / open-vocab tagger primitives), Rung 5b (GATED extractor, GATE 1/2 primitives), Rung 6 (simplicity
# filter, SAME seeds/n_per_seed), v2 (closed lexicons + coordination splitter), Rung 2 (POS-tag machinery). ---
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import (  # noqa: E402
    CONLLU_PATH, sample_real_sentences, score_arm, ie_extract_open, _relax_irregular_verb, GUARD_SENTENCES,
    OUT_OF_SCHEMA_CONTROL, _children, analyze_sentence, CONSTRUCTION_CLASSES, build_rows_for_seed,
    IRREGULAR_VERB_LEMMA, _open_verb_lemma, _OPEN_FORM_MAP, _resolve_relation_open,
)
from experiments.exp_read_grow_realprose_abstain_gate_rung5b_v1 import ie_extract_open_gated, _is_finite_form  # noqa: E402
from experiments.exp_read_grow_realprose_simple_register_rung6_v1 import (  # noqa: E402
    load_simple_sentences, TOK_LO_DEFAULT, TOK_HI_DEFAULT, _is_declarative_length_matched, _clause_count,
    SEEDS_FULL, N_PER_SEED,
)
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import (  # noqa: E402
    DETS, PRONS, BE_AUX, RELZRS, PREPS, VERB_LEX, ENTITIES, ADJS, ADVS, _tokenize, _split_coord,
)
from experiments.exp_read_grow_oov_pos_extension_v1 import (  # noqa: E402
    _tokenize_cased, _oov_lemma, NLTK_NOUN_TAGS, NLTK_VERB_TAGS,
)

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only (same as Rung 5/5b/6); glass-box-legal.

# ---------------------------------------------------------------------------
# HEAD-SELECTION primitives (BUG 2/3 fix): general, closed-form, shared by subject/object/passive-agent.
# ---------------------------------------------------------------------------
def _first_contiguous_noun_run(sorted_noun_positions):
    """the FIRST maximal run of CONSECUTIVE token positions within a (possibly non-contiguous) sorted list of
    NOUN-tagged indices. A PREP/DET/other-tag boundary between two nouns breaks contiguity -- this is what
    stops a trailing PP's own object noun from being pulled into the SUBJECT head-run (BUG 3's PP case)."""
    if not sorted_noun_positions:
        return []
    run = [sorted_noun_positions[0]]
    for p in sorted_noun_positions[1:]:
        if p == run[-1] + 1:
            run.append(p)
        else:
            break
    return run


def _np_head_from_run(T, run_idx):
    """selects the syntactic HEAD lemma of a contiguous multi-NOUN run. UD convention: a FLAT multi-word
    PROPER-NAME span (Santa Claus, Winston Peters) attaches later words to the FIRST word via `flat` -> head is
    LEFTMOST; a COMPOUND common-noun modifier+head span (customer service, football team captain) attaches the
    modifier to the head noun it precedes via `compound` -> head is RIGHTMOST. Distinguished by ORIGINAL-CASE
    capitalization (T[i][0] = original-cased surface form): ALL tokens capitalized -> flat proper-name span,
    head=first; otherwise -> compound common-noun span, head=last. A single-token run trivially returns that
    token (no ambiguity)."""
    if not run_idx:
        return None
    if len(run_idx) == 1:
        return T[run_idx[0]][2]
    all_caps = all(T[i][0][:1].isupper() for i in run_idx)
    head_i = run_idx[0] if all_caps else run_idx[-1]
    return T[head_i][2]


def _scan_object_np(T, tags, lemmas, j, n, use_head_fix, allow_pron_skip):
    """object-side NP scan: structural copy of Rung 5b's inline object-scan loop, generalized to (a)
    optionally consume a CONTIGUOUS multi-NOUN run and select its HEAD (use_head_fix -- BUG 2 fix) instead of
    grabbing only the first NOUN token encountered, and (b) optionally treat PRON as a skippable function-word
    token (allow_pron_skip -- needed for imperative objects like "her" in "Take her to the vet.", a closed-
    class pronoun with no derivable lemma content, same principle as the pre-existing DET/ADJ/ADV/AUX skip).
    Returns (prep, obj_lemmas, consumed_end_index)."""
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
                obj_lemmas.append(_np_head_from_run(T, list(range(run_start, j))))
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
                            obj_lemmas.append(_np_head_from_run(T, list(range(run_start2, j))))
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
# TAGGER (BUG 1 fix, parameterized): irregular-verb lookup runs BEFORE the lookup-free suffix-stripper, inside
# the tagger itself -- not a post-hoc rescoring table. Also: sentence-initial "please" -> DISC (imperative
# discourse-marker fix, position-scoped).
# ---------------------------------------------------------------------------
IMPERATIVE_DISCOURSE_MARKERS = {"please"}


def _tag_token_open_v2(w_lower, w_orig, ptag, use_bug1_fix):
    """structural copy of Rung 5's `_tag_token_open`, with ONE change: when a token falls through to the
    POS-tagger VERB branch, the irregular-verb table (`IRREGULAR_VERB_LEMMA`, Rung 5, already in the codebase)
    is consulted FIRST (use_bug1_fix) -- only tokens NOT in the table fall to the lookup-free suffix-stripper
    (`_open_verb_lemma`). This is the ONLY change from Rung 5's tagger; everything else byte-identical."""
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
        if use_bug1_fix and w_lower in IRREGULAR_VERB_LEMMA:
            lemma = IRREGULAR_VERB_LEMMA[w_lower]
        else:
            lemma = _open_verb_lemma(w_lower)
        return "VERB", lemma, _OPEN_FORM_MAP.get(ptag, "unknown")
    if ptag in NLTK_NOUN_TAGS:
        return "NOUN", _oov_lemma(w_lower), None
    if ptag.startswith("JJ") or w_lower in ADJS:
        return "ADJ", None, None
    if ptag.startswith("RB") or w_lower in ADVS:
        return "ADV", None, None
    if ptag == "IN":
        return "PREP", w_lower, None
    return "UNK", None, None


def _build_tags_open_v2(sentence, use_bug1_fix):
    lower_toks = _tokenize(sentence)
    cased_toks = _tokenize_cased(sentence)
    assert len(lower_toks) == len(cased_toks), "tokenization parity break between cased/lowercased split"
    tagged = nltk.pos_tag(cased_toks)  # REAL classical averaged-perceptron call, context-aware over the sentence
    T = []
    for (w_lower, w_orig, (_, ptag)) in zip(lower_toks, cased_toks, tagged):
        tag, lemma, form = _tag_token_open_v2(w_lower, w_orig, ptag, use_bug1_fix)
        T.append((w_orig, tag, lemma, form))
    if T and T[0][0].lower() in IMPERATIVE_DISCOURSE_MARKERS:
        # sentence-INITIAL "please" only -- the classical tagger is MEASURED (self_test) to be context-fragile
        # on this exact word (NOUN in one real sentence, VERB in another, for the identical word); a closed-
        # class override at position 0 removes that dependence. Non-initial "please" (a genuine verb) is
        # untouched.
        w_orig0 = T[0][0]
        T[0] = (w_orig0, "DISC", w_orig0.lower(), None)
    return T


# ---------------------------------------------------------------------------
# EXTRACTOR CORE (parameterized: use_head_fix = bugs 2/3, use_imperative_fix = the CONSTRUCTION gap). GATE 1
# (finite-matrix-verb) and GATE 2 (no-unhandled-trailing-finite-verb) reused UNMODIFIED from Rung 5b -- not
# in this cell's declared scope.
# ---------------------------------------------------------------------------
def _extract_core_open_gated_v2(T, use_head_fix, use_imperative_fix):
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

    if not subj_nouns_before_v0:
        if not subj_prons_before_v0:
            # IMPERATIVE PATTERN CANDIDATE: zero nominal material of any kind before the first finite verb
            # (discourse markers like sentence-initial "please" are DISC-tagged and invisible to noun_idx/
            # pron_idx). Extract as (implicit "you", verb[+prep], object) when the fix is enabled AND the
            # verb is base-form (VB-tag, the imperative-typical bare form).
            if use_imperative_fix and forms[v0] == "base":
                matrix_vi = v0
                verb_lemma = lemmas[matrix_vi]
                subjects = ["you"]
                prep, obj_lemmas, jend = _scan_object_np(T, tags, lemmas, matrix_vi + 1, n, use_head_fix, True)
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
        return [], "COREF_UNRESOLVED", "pronoun subject, no in-sentence antecedent (coreference gap)"

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

    if rc:
        subjects = [lemmas[head_noun_i]]
    else:
        subj_region = [i for i in noun_idx if i < matrix_vi]
        # BUG 3 fix: `_split_coord`'s OWN no-"and" internal fallback already picks the LAST noun in the
        # region (this IS where the original bug lived, not in a caller-side `or` clause) -- so genuine
        # "and"-coordination must be detected explicitly here and routed to `_split_coord`'s correct multi-
        # lemma behavior; the NO-coordination case uses the new head-selection rule (or, with the fix
        # disabled, `_split_coord`'s own byte-identical last-noun fallback, for FIX1-only comparability).
        has_and_coord = any(tags[k2] == "CONJ" and lemmas[k2] == "and"
                             for k2 in range(subj_region[0], subj_region[-1] + 1)) if subj_region else False
        if has_and_coord:
            subjects = _split_coord(subj_region, T)
        elif use_head_fix:
            head_run = _first_contiguous_noun_run(subj_region)
            subjects = [_np_head_from_run(T, head_run)] if head_run else [lemmas[subj_region[-1]]]
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
                    agent = _np_head_from_run(T, list(range(run_start, jj)))
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
        rule = "SVO_PASSIVE_OPEN_GATED_V2"
    else:
        prep, obj_lemmas, jend = _scan_object_np(T, tags, lemmas, matrix_vi + 1, n, use_head_fix, False)
        consumed_end = jend
        relation = _resolve_relation_open(verb_lemma, prep)
        if not obj_lemmas:
            return [], "NO_OBJECT", "no object noun after verb"
        triples = [(s, relation, o) for s in subjects for o in obj_lemmas]
        rule = ("SVO_COORD_OPEN_GATED_V2" if (len(subjects) > 1 or len(obj_lemmas) > 1)
                else "SVO_ACTIVE_OPEN_GATED_V2")

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


def ie_extract_open_gated_v2(sentence, use_bug1_fix, use_head_fix, use_imperative_fix):
    T = _build_tags_open_v2(sentence, use_bug1_fix)
    return _extract_core_open_gated_v2(T, use_head_fix, use_imperative_fix)


def ie_extract_fix1_only(sentence):
    return ie_extract_open_gated_v2(sentence, True, False, False)


def ie_extract_fix1_head(sentence):
    return ie_extract_open_gated_v2(sentence, True, True, False)


def ie_extract_fix_all(sentence):
    return ie_extract_open_gated_v2(sentence, True, True, True)


# ---------------------------------------------------------------------------
# GOLD-SIDE EXTENSION: feats-aware CoNLL-U parser + imperative gold-derivation, layered on Rung 5's
# `analyze_sentence` (byte-identical for every pre-existing bucket).
# ---------------------------------------------------------------------------
def parse_conllu_v2(path):
    """copy of Rung 5's `parse_conllu` with ONE addition: captures the FEATS column (fields[5]), needed for
    principled gold-side IMPERATIVE detection (UD's own Mood=Imp morphological feature). Everything else
    byte-identical to Rung 5's parser."""
    sentences = []
    cur_meta, cur_tokens = {}, []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# "):
                if "=" in line:
                    k, _, v = line[2:].partition("=")
                    cur_meta[k.strip()] = v.strip()
                continue
            if not line.strip():
                if cur_tokens:
                    sentences.append({"meta": cur_meta, "tokens": cur_tokens})
                cur_meta, cur_tokens = {}, []
                continue
            fields = line.split("\t")
            if len(fields) != 10:
                continue
            tid = fields[0]
            if "-" in tid or "." in tid:
                continue
            cur_tokens.append({
                "id": int(tid), "form": fields[1], "lemma": fields[2].lower(), "upos": fields[3],
                "feats": fields[5], "head": int(fields[6]) if fields[6] not in ("_", "") else None,
                "deprel": fields[7],
            })
    if cur_tokens:
        sentences.append({"meta": cur_meta, "tokens": cur_tokens})
    return sentences


def load_length_matched_pool_v2(path, tok_lo=TOK_LO_DEFAULT, tok_hi=TOK_HI_DEFAULT):
    if not path.exists():
        raise FileNotFoundError(
            f"UD-EWT corpus not found at {path}. This cell reads a LOCAL, pre-fetched copy (no network access "
            f"at self-test/smoke/full time) -- see data/corpora/ud_english_ewt/PROVENANCE.md.")
    all_sents = parse_conllu_v2(path)
    matched = [s for s in all_sents if _is_declarative_length_matched(s, tok_lo, tok_hi)]
    return sorted(matched, key=lambda s: s["meta"]["sent_id"])


def load_simple_sentences_v2(path, tok_lo=TOK_LO_DEFAULT, tok_hi=TOK_HI_DEFAULT):
    """byte-identical FILTER to Rung 6's own `load_simple_sentences` (token band, single verbal root,
    clause_count<=1) -- the SIMPLICITY FILTER is NOT extended for imperatives (they already satisfy it); only
    the underlying parser is swapped for the feats-aware `parse_conllu_v2`, verified at self_test to select
    the byte-identical sentence-id sequence."""
    length_matched = load_length_matched_pool_v2(path, tok_lo, tok_hi)
    simple = []
    for s in length_matched:
        roots = [t for t in s["tokens"] if t["deprel"].split(":")[0] == "root"]
        if len(roots) != 1:
            continue
        if roots[0]["upos"] not in ("VERB", "AUX"):
            continue
        if _clause_count(s["tokens"]) > 1:
            continue
        simple.append(s)
    return sorted(simple, key=lambda s: s["meta"]["sent_id"]), len(length_matched)


def _derive_imperative_gold(tokens, root):
    """gold-side IMPERATIVE recognition + triple derivation. PRIMARY signal: UD's own Mood=Imp morphological
    feature on the root verb (authoritative -- this IS what UD annotators marked, MEASURED@corpus: 178
    occurrences in the local file). FALLBACK (only when feats is unavailable/empty): a purely-structural check
    -- root is the clause-initial token (no nsubj/csubj already verified by the caller). Returns None (not
    imperative) if neither signal fires."""
    feats = root.get("feats", "") or ""
    is_imp_feats = "Mood=Imp" in feats
    first_tok_id = min(t["id"] for t in tokens)
    is_clause_initial_verb = (root["id"] == first_tok_id)
    if not (is_imp_feats or is_clause_initial_verb):
        return None
    signal = "feats_mood_imp" if is_imp_feats else "structural_fallback_clause_initial_verb"
    obj_direct = _children(tokens, root["id"], deprel_base="obj") + _children(tokens, root["id"], deprel_base="dobj")
    obl = _children(tokens, root["id"], deprel_base="obl")
    gold = []
    subclass = "imperative_no_object"
    if obj_direct:
        obj_head = obj_direct[0]
        obj_conj = _children(tokens, obj_head["id"], deprel_base="conj")
        obj_lemmas = [obj_head["lemma"]] + [c["lemma"] for c in obj_conj]
        gold = [("you", root["lemma"], o) for o in obj_lemmas]
        subclass = None
    else:
        prep_obl = None
        for o in sorted(obl, key=lambda t: t["id"]):
            cases = _children(tokens, o["id"], deprel_base="case")
            if cases and cases[0]["form"].lower() != "by":
                prep_obl = (o, cases[0]["form"].lower())
                break
        if prep_obl:
            o, prep = prep_obl
            gold = [("you", f"{root['lemma']}_{prep}", o["lemma"])]
            subclass = None
    gold = sorted({(s, r, o) for (s, r, o) in gold if s != o})
    return {"cls": "imperative", "subclass": subclass, "gold": gold, "imp_signal": signal}


def analyze_sentence_v2(sent_tokens):
    """copy of Rung 5's `analyze_sentence`, BYTE-IDENTICAL for every pre-existing bucket (passive /
    vp_coordination / compound_subject / relative_clause / single_clause_svo / other_unhandled), with ONE
    addition: when the root has no nsubj AND no csubj, `_derive_imperative_gold` is consulted BEFORE falling
    back to other_unhandled/no_subject."""
    tokens = sent_tokens
    roots = [t for t in tokens if t["deprel"].split(":")[0] == "root"]
    if len(roots) != 1:
        return {"cls": "other_unhandled", "subclass": "multi_or_no_root", "gold": []}
    root = roots[0]
    if root["upos"] not in ("VERB", "AUX"):
        return {"cls": "other_unhandled", "subclass": "nonverbal_root", "gold": []}
    subj = _children(tokens, root["id"], deprel_base="nsubj")
    if not subj:
        csubj = _children(tokens, root["id"], deprel_base="csubj")
        if not csubj:
            imp = _derive_imperative_gold(tokens, root)
            if imp is not None:
                return imp
        return {"cls": "other_unhandled", "subclass": "no_subject", "gold": []}
    subj_head = subj[0]
    is_pass_subj = subj_head["deprel"] == "nsubj:pass"
    aux_pass = _children(tokens, root["id"], deprel_exact="aux:pass")
    is_passive = is_pass_subj or bool(aux_pass)
    conj_verbs = [t for t in _children(tokens, root["id"], deprel_base="conj") if t["upos"] in ("VERB", "AUX")]
    subj_conj = _children(tokens, subj_head["id"], deprel_base="conj")
    obj_direct = (_children(tokens, root["id"], deprel_base="obj")
                  + _children(tokens, root["id"], deprel_base="dobj"))
    rel_clause = _children(tokens, subj_head["id"], deprel_exact="acl:relcl")
    obl = _children(tokens, root["id"], deprel_base="obl")
    by_agent = None
    for o in sorted(obl, key=lambda t: t["id"]):
        cases = _children(tokens, o["id"], deprel_base="case")
        if any(c["form"].lower() == "by" for c in cases):
            by_agent = o
            break

    def _drop_self_loop(gold):
        return sorted({(s, r, o) for (s, r, o) in gold if s != o})

    if is_passive:
        gold = [(by_agent["lemma"], root["lemma"], subj_head["lemma"])] if by_agent is not None else []
        subclass = None if by_agent is not None else "agentless_passive_gold_undefined"
        return {"cls": "passive", "subclass": subclass, "gold": _drop_self_loop(gold)}

    if conj_verbs:
        subj_lemmas = [subj_head["lemma"]] + [c["lemma"] for c in subj_conj]
        gold = []
        for v in [root] + conj_verbs:
            v_obj = _children(tokens, v["id"], deprel_base="obj") + _children(tokens, v["id"], deprel_base="dobj")
            v_subj = _children(tokens, v["id"], deprel_base="nsubj")
            subs = [v_subj[0]["lemma"]] if v_subj else subj_lemmas
            for o in v_obj:
                for s in subs:
                    gold.append((s, v["lemma"], o["lemma"]))
        return {"cls": "vp_coordination", "subclass": None, "gold": _drop_self_loop(gold)}

    if subj_conj:
        subj_lemmas = [subj_head["lemma"]] + [c["lemma"] for c in subj_conj]
        gold = []
        subclass = "no_object"
        if obj_direct:
            obj_head = obj_direct[0]
            obj_conj = _children(tokens, obj_head["id"], deprel_base="conj")
            obj_lemmas = [obj_head["lemma"]] + [c["lemma"] for c in obj_conj]
            gold = [(s, root["lemma"], o) for s in subj_lemmas for o in obj_lemmas]
            subclass = None
        return {"cls": "compound_subject", "subclass": subclass, "gold": _drop_self_loop(gold)}

    if rel_clause:
        gold = []
        subclass = "no_object"
        if obj_direct:
            obj_head = obj_direct[0]
            obj_conj = _children(tokens, obj_head["id"], deprel_base="conj")
            obj_lemmas = [obj_head["lemma"]] + [c["lemma"] for c in obj_conj]
            gold = [(subj_head["lemma"], root["lemma"], o) for o in obj_lemmas]
            subclass = None
        return {"cls": "relative_clause", "subclass": subclass, "gold": _drop_self_loop(gold)}

    if obj_direct:
        obj_head = obj_direct[0]
        obj_conj = _children(tokens, obj_head["id"], deprel_base="conj")
        obj_lemmas = [obj_head["lemma"]] + [c["lemma"] for c in obj_conj]
        gold = [(subj_head["lemma"], root["lemma"], o) for o in obj_lemmas]
        return {"cls": "single_clause_svo", "subclass": "direct_object", "gold": _drop_self_loop(gold)}

    prep_obl = None
    for o in sorted(obl, key=lambda t: t["id"]):
        cases = _children(tokens, o["id"], deprel_base="case")
        if cases and cases[0]["form"].lower() != "by":
            prep_obl = (o, cases[0]["form"].lower())
            break
    if prep_obl:
        o, prep = prep_obl
        gold = [(subj_head["lemma"], f"{root['lemma']}_{prep}", o["lemma"])]
        return {"cls": "single_clause_svo", "subclass": "prep_governed", "gold": _drop_self_loop(gold)}

    return {"cls": "other_unhandled", "subclass": "no_object_no_obl", "gold": []}


CONSTRUCTION_CLASSES_V2 = CONSTRUCTION_CLASSES + ("imperative",)


def build_rows_for_seed_v2(pool_sorted, seed, n_per_seed):
    sample = sample_real_sentences(pool_sorted, seed, min(n_per_seed, len(pool_sorted)))
    rows = []
    dist = {c: 0 for c in CONSTRUCTION_CLASSES_V2}
    for s in sample:
        a = analyze_sentence_v2(s["tokens"])
        dist[a["cls"]] += 1
        rows.append({"text": s["meta"]["text"], "sent_id": s["meta"]["sent_id"], "cls": a["cls"],
                     "subclass": a["subclass"], "gold": a["gold"], "imp_signal": a.get("imp_signal")})
    return rows, dist


# ---------------------------------------------------------------------------
# LIVE bug-fix verification battery (called at both self_test AND full-run time -- MEASURED, not narrated).
# General nonce constructions + the 2 REAL Rung-6 documented false-positive rows as regression fixtures.
# ---------------------------------------------------------------------------
def verify_bug_fixes():
    evidence = {}

    b1_cases = [
        ("The boy has a dog.", "have"),
        ("The boy had a dog.", "have"),
        ("The manager did the work.", "do"),
    ]
    b1_detail = []
    b1_ok = True
    for sent, expect_lemma in b1_cases:
        old = ie_extract_open_gated(sent)
        new = ie_extract_fix_all(sent)
        ok = bool(new[0]) and new[0][0][1] == expect_lemma
        b1_detail.append({"sent": sent, "old_emitted": old[0], "new_emitted": new[0],
                           "expected_relation": expect_lemma, "fixed": ok})
        b1_ok = b1_ok and ok
    evidence["bug1_irregular_verb_lemma_fixed"] = b1_ok
    evidence["bug1_detail"] = b1_detail

    head_cases = [
        ("Santa Claus visited the school.", "subject", "santa"),
        ("Winston Peters resigned yesterday.", "subject", "winston"),
        ("Maria Rodriguez opened the office.", "subject", "maria"),
        ("The correction to the report satisfied the board.", "subject", "correction"),
        ("The manager thanked customer service.", "object", "service"),
        ("The teacher thanked the football team captain.", "object", "captain"),
        ("The customer service team thanked the manager.", "subject", "team"),  # regression guard
    ]
    head_detail = []
    head_ok = True
    for sent, role, expect in head_cases:
        old = ie_extract_open_gated(sent)
        new = ie_extract_fix_all(sent)
        got = None
        if new[0]:
            got = new[0][0][0] if role == "subject" else new[0][0][2]
        ok = (got == expect)
        head_detail.append({"sent": sent, "role": role, "expected": expect, "old_emitted": old[0],
                             "new_emitted": new[0], "fixed": ok})
        head_ok = head_ok and ok
    evidence["bug23_head_selection_fixed"] = head_ok
    evidence["bug23_detail"] = head_detail

    imp_extract_cases = [
        ("Take her to the vet.", [("you", "take_to", "vet")]),
        ("Please return an executed copy of confirm to me.", [("you", "return", "copy")]),
        ("Please, ask Stinson as well.", [("you", "ask", "stinson")]),
    ]
    imp_detail = []
    imp_extract_ok = True
    for sent, expect in imp_extract_cases:
        old = ie_extract_open_gated(sent)
        new = ie_extract_fix_all(sent)
        ok = (sorted(new[0]) == sorted(expect))
        imp_detail.append({"sent": sent, "expected": expect, "old_emitted": old[0], "old_rule": old[1],
                            "new_emitted": new[0], "new_rule": new[1], "fixed": ok})
        imp_extract_ok = imp_extract_ok and ok
    evidence["imperative_extraction_demonstrated"] = imp_extract_ok
    evidence["imperative_extraction_detail"] = imp_detail

    imp_ff_cases = ["Please return an executed copy of confirm to me.", "Please, ask Stinson as well."]
    imp_ff_detail = []
    imp_ff_ok = True
    for sent in imp_ff_cases:
        old = ie_extract_open_gated(sent)
        new = ie_extract_fix_all(sent)
        old_wrongly_fired = bool(old[0]) and old[0][0][0] == "please"
        new_no_please_subject = not any(t[0] == "please" for t in new[0])
        ok = old_wrongly_fired and new_no_please_subject
        imp_ff_detail.append({"sent": sent, "old_emitted": old[0], "new_emitted": new[0], "fixed": ok})
        imp_ff_ok = imp_ff_ok and ok
    evidence["imperative_no_longer_false_fires"] = imp_ff_ok
    evidence["imperative_no_false_fire_detail"] = imp_ff_detail

    residual_cases = ["Sit down.", "Look at the cat.", "Close the door quietly."]
    residual_detail = []
    for sent in residual_cases:
        new = ie_extract_fix_all(sent)
        residual_detail.append({"sent": sent, "emitted": new[0], "rule": new[1], "clean_abstain": (new[0] == [])})
    evidence["declared_residual_tagger_mistag_clean_abstain"] = all(d["clean_abstain"] for d in residual_detail)
    evidence["declared_residual_detail"] = residual_detail

    evidence["all_named_bugs_verified_fixed"] = (
        evidence["bug1_irregular_verb_lemma_fixed"] and evidence["bug23_head_selection_fixed"]
        and evidence["imperative_no_longer_false_fires"] and evidence["imperative_extraction_demonstrated"])
    return evidence


# ---------------------------------------------------------------------------
# glass-box-legal checks (same method as Rung 5/5b/6).
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
def run_full(seeds, n_per_seed, tok_lo=TOK_LO_DEFAULT, tok_hi=TOK_HI_DEFAULT):
    simple_sorted_v2, length_matched_pool_size_v2 = load_simple_sentences_v2(CONLLU_PATH, tok_lo, tok_hi)
    simple_sorted_old, length_matched_pool_size_old = load_simple_sentences(CONLLU_PATH, tok_lo, tok_hi)
    same_slice_parity = ([s["meta"]["sent_id"] for s in simple_sorted_v2] ==
                          [s["meta"]["sent_id"] for s in simple_sorted_old])
    simple_fraction_of_length_matched_pool = (
        len(simple_sorted_v2) / length_matched_pool_size_v2 if length_matched_pool_size_v2 else 0.0)

    all_rows_v2, all_rows_old = [], []
    dist_pooled_v2 = {c: 0 for c in CONSTRUCTION_CLASSES_V2}
    dist_pooled_old = {c: 0 for c in CONSTRUCTION_CLASSES}
    for seed in seeds:
        rows_v2, dist_v2 = build_rows_for_seed_v2(simple_sorted_v2, seed, n_per_seed)
        rows_old, dist_old = build_rows_for_seed(simple_sorted_old, seed, n_per_seed)
        all_rows_v2.extend(rows_v2)
        all_rows_old.extend(rows_old)
        for c in CONSTRUCTION_CLASSES_V2:
            dist_pooled_v2[c] += dist_v2[c]
        for c in CONSTRUCTION_CLASSES:
            dist_pooled_old[c] += dist_old[c]

    n_total = len(all_rows_v2)
    dist_frac_v2 = {c: (dist_pooled_v2[c] / n_total if n_total else 0.0) for c in CONSTRUCTION_CLASSES_V2}
    n_imperative_by_feats = sum(1 for r in all_rows_v2 if r.get("imp_signal") == "feats_mood_imp")
    n_imperative_by_fallback = sum(
        1 for r in all_rows_v2 if r.get("imp_signal") == "structural_fallback_clause_initial_verb")

    baseline_reproduction = score_arm(all_rows_old, ie_extract_open_gated)
    baseline_vs_extended_gold = score_arm(all_rows_v2, ie_extract_open_gated)
    fix1_score = score_arm(all_rows_v2, ie_extract_fix1_only)
    fix1_head_score = score_arm(all_rows_v2, ie_extract_fix1_head)
    fix_all_score = score_arm(all_rows_v2, ie_extract_fix_all)
    baseline_ungated_informational = score_arm(all_rows_v2, ie_extract_open)

    def _guard_ok(fn):
        return all(set(fn(s)[0]) == set(g) for (s, g) in GUARD_SENTENCES)

    def _oos_ok(fn):
        return all(not fn(s)[0] for s in OUT_OF_SCHEMA_CONTROL)

    guard_ok = {"baseline": _guard_ok(ie_extract_open_gated), "fix1": _guard_ok(ie_extract_fix1_only),
                "fix1_head": _guard_ok(ie_extract_fix1_head), "fix_all": _guard_ok(ie_extract_fix_all)}
    oos_ok = {"baseline": _oos_ok(ie_extract_open_gated), "fix1": _oos_ok(ie_extract_fix1_only),
              "fix1_head": _oos_ok(ie_extract_fix1_head), "fix_all": _oos_ok(ie_extract_fix_all)}

    bug_fix_evidence = verify_bug_fixes()

    return {
        "seeds": seeds, "n_per_seed": n_per_seed, "n_total": n_total, "tok_lo": tok_lo, "tok_hi": tok_hi,
        "simple_pool_size": len(simple_sorted_v2), "length_matched_pool_size": length_matched_pool_size_v2,
        "simple_fraction_of_length_matched_pool": simple_fraction_of_length_matched_pool,
        "same_slice_parity_vs_rung6_pool": same_slice_parity,
        "construction_distribution_counts_v2": dist_pooled_v2, "construction_distribution_fractions_v2": dist_frac_v2,
        "construction_distribution_counts_old": dist_pooled_old,
        "n_imperative_by_feats": n_imperative_by_feats, "n_imperative_by_structural_fallback": n_imperative_by_fallback,
        "baseline_reproduction": baseline_reproduction, "baseline_vs_extended_gold": baseline_vs_extended_gold,
        "fix1_score": fix1_score, "fix1_head_score": fix1_head_score, "fix_all_score": fix_all_score,
        "baseline_ungated_informational": baseline_ungated_informational,
        "guard_regression_ok_baseline": guard_ok["baseline"], "guard_regression_ok_fix1": guard_ok["fix1"],
        "guard_regression_ok_fix1_head": guard_ok["fix1_head"], "guard_regression_ok_fix_all": guard_ok["fix_all"],
        "oos_control_fired_baseline": oos_ok["baseline"], "oos_control_fired_fix1": oos_ok["fix1"],
        "oos_control_fired_fix1_head": oos_ok["fix1_head"], "oos_control_fired_fix_all": oos_ok["fix_all"],
        "bug_fix_evidence": bug_fix_evidence,
        "all_rows_v2": all_rows_v2,
    }


def compute_verdict(agg):
    prec = agg["fix_all_score"]["precision_on_attempted"]
    cov = agg["fix_all_score"]["coverage_sentence_rate"]
    guard_ok = agg["guard_regression_ok_fix_all"]
    oos_ok = agg["oos_control_fired_fix_all"]
    simple_frac = agg["simple_fraction_of_length_matched_pool"]
    bugs_verified = agg["bug_fix_evidence"]["all_named_bugs_verified_fixed"]

    if prec is None:
        return ("MIDDLE_BAND", "FIX_ALL (GATED) arm emitted zero triples on the whole simple-register sample -- "
                                "mechanism did not fire at all", "no_triples_emitted")

    hard_pass = (prec >= 0.60) and (cov >= 0.05) and guard_ok and oos_ok and (simple_frac >= 0.10) and bugs_verified
    hard_fail = (prec < 0.55) or (cov < 0.03) or (not guard_ok) or (simple_frac < 0.10)

    if hard_pass:
        tier = "HARD_PASS"
    elif hard_fail:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    weakest = "n/a"
    if not hard_pass:
        if simple_frac < 0.10:
            weakest = "simple_fraction_of_length_matched_pool_below_0.10_stratum_vacuous"
        elif prec < 0.60:
            weakest = "fix_all_precision_on_attempted_below_0.60_register_advantage_still_not_realized"
        elif cov < 0.05:
            weakest = "fix_all_coverage_sentence_rate_below_0.05"
        elif not guard_ok:
            weakest = "guard_regression_failed_fix_all"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire_fix_all"
        elif not bugs_verified:
            weakest = "named_bug_fixes_not_fully_verified_despite_precision_clearing_envelope"

    b = agg["baseline_reproduction"]["precision_on_attempted"]
    f1 = agg["fix1_score"]["precision_on_attempted"]
    f12 = agg["fix1_head_score"]["precision_on_attempted"]

    def _d(a, c):
        return round(c - a, 4) if (a is not None and c is not None) else None

    msg = (f"{tier} | RUNG7 FIXES+IMPERATIVES on the SAME simple-register slice as RUNG 6 (n={agg['n_total']}) | "
           f"BASELINE(rung6-reproduced)={b:.3f} -> FIX1(irregular-verb)="
           f"{'n/a' if f1 is None else f'{f1:.3f}'} (d={_d(b, f1)}) -> FIX1+HEAD(bug2/3)="
           f"{'n/a' if f12 is None else f'{f12:.3f}'} (d={_d(f1, f12)}) -> FIX_ALL(+imperative)={prec:.3f} "
           f"(d={_d(f12, prec)}) | total_delta={_d(b, prec)} | coverage={cov:.3f} (HP>=0.05,HF<0.03) | "
           f"bugs_verified={bugs_verified} | guard_regression_ok={guard_ok} oos_control_fired={oos_ok} | "
           f"n_imperative_by_feats={agg['n_imperative_by_feats']} "
           f"n_imperative_by_structural_fallback={agg['n_imperative_by_structural_fallback']} | "
           f"weakest={weakest} | REGISTER_ADVANTAGE_REAL={hard_pass}")
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
# self-test: EXERCISE THE REAL code path (real corpus file, real nltk.pos_tag, real filters + all 4 arms +
# the live bug-fix verification battery).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (real feats-aware CoNLL-U parse, real nltk.pos_tag calls, "
          "real simplicity filter + all 4 extraction arms)...", flush=True)

    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"
    _ = nltk.pos_tag(["The", "cat", "sat", "."])
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print(f"[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural)", flush=True)

    # (1) hand-built-tree tests for the NEW gold logic (`_derive_imperative_gold`): primary Mood=Imp signal,
    # structural fallback, and a NEGATIVE control (must NOT be misclassified imperative).
    def _tok(id_, form, lemma, upos, head, deprel, feats=""):
        return {"id": id_, "form": form, "lemma": lemma, "upos": upos, "head": head, "deprel": deprel, "feats": feats}

    imp_feats_tree = [
        _tok(1, "Click", "click", "VERB", 0, "root", feats="Mood=Imp|VerbForm=Fin"),
        _tok(2, "the", "the", "DET", 3, "det"),
        _tok(3, "button", "button", "NOUN", 1, "obj"),
    ]
    r = analyze_sentence_v2(imp_feats_tree)
    assert r["cls"] == "imperative" and r["gold"] == [("you", "click", "button")] and r["imp_signal"] == "feats_mood_imp", r

    imp_fallback_tree = [
        _tok(1, "Sit", "sit", "VERB", 0, "root", feats=""),  # no feats -- fallback (root IS first token)
        _tok(2, "down", "down", "ADV", 1, "advmod"),
    ]
    r2 = analyze_sentence_v2(imp_fallback_tree)
    assert r2["cls"] == "imperative" and r2["subclass"] == "imperative_no_object" and r2["gold"] == [], r2
    assert r2["imp_signal"] == "structural_fallback_clause_initial_verb", r2

    non_imp_tree = [  # root NOT first token, no Mood=Imp feats, no nsubj/csubj -- must NOT be "imperative"
        _tok(1, "Meanwhile", "meanwhile", "ADV", 2, "advmod"),
        _tok(2, "arrived", "arrive", "VERB", 0, "root", feats="Mood=Ind|VerbForm=Fin"),
        _tok(3, "late", "late", "ADV", 2, "advmod"),
    ]
    r3 = analyze_sentence_v2(non_imp_tree)
    assert r3["cls"] == "other_unhandled" and r3["subclass"] == "no_subject", (
        f"NEGATIVE CONTROL FAILED: a non-first-token, non-Mood=Imp subjectless verb was wrongly classified "
        f"imperative: {r3}")
    print("[self_test] `_derive_imperative_gold` hand-built-tree tests PASS: Mood=Imp primary signal, "
          "structural fallback, and negative control (non-imperative subjectless clause NOT misclassified).",
          flush=True)

    # (2) existing-bucket byte-identical parity: `analyze_sentence_v2` must agree with Rung 5's own
    # `analyze_sentence` on the SAME 5 non-imperative hand-built trees Rung 5/6 already validated.
    svo = [_tok(1, "The", "the", "DET", 2, "det"), _tok(2, "cat", "cat", "NOUN", 3, "nsubj"),
           _tok(3, "eats", "eat", "VERB", 0, "root"), _tok(4, "the", "the", "DET", 5, "det"),
           _tok(5, "fish", "fish", "NOUN", 3, "obj")]
    assert analyze_sentence_v2(svo) == analyze_sentence(svo), "analyze_sentence_v2 drifted on single_clause_svo"
    print("[self_test] `analyze_sentence_v2` byte-identical to Rung 5's `analyze_sentence` on a known "
          "single_clause_svo tree (spot check for accidental drift on pre-existing buckets).", flush=True)

    # (3) BUG 1 (irregular-verb lookup-ordering) -- general nonce battery, live-verified.
    b1 = verify_bug_fixes()
    assert b1["bug1_irregular_verb_lemma_fixed"], f"BUG 1 fix did not generalize: {b1['bug1_detail']}"
    for d in b1["bug1_detail"]:
        print(f"[self_test] BUG1: {d['sent']!r} old={d['old_emitted']} new={d['new_emitted']} "
              f"(expected verb-relation={d['expected_relation']!r}) fixed={d['fixed']}", flush=True)

    # (4) BUGS 2/3 (head selection) -- doc-cited + genuinely novel nonce cases + regression guard.
    assert b1["bug23_head_selection_fixed"], f"BUGS 2/3 fix did not generalize: {b1['bug23_detail']}"
    for d in b1["bug23_detail"]:
        print(f"[self_test] BUG2/3: {d['sent']!r} role={d['role']} old={d['old_emitted']} "
              f"new={d['new_emitted']} expected={d['expected']!r} fixed={d['fixed']}", flush=True)

    # (5) IMPERATIVE construction -- extraction wins (2 REAL Rung-6 rows + 1 contract-canonical nonce) and
    # no-longer-false-fires (the same 2 real rows, explicit old-vs-new comparison).
    assert b1["imperative_extraction_demonstrated"], f"imperative extraction did not generalize: {b1['imperative_extraction_detail']}"
    assert b1["imperative_no_longer_false_fires"], f"imperative false-fire fix failed: {b1['imperative_no_false_fire_detail']}"
    for d in b1["imperative_extraction_detail"]:
        print(f"[self_test] IMPERATIVE-EXTRACT: {d['sent']!r} old={d['old_emitted']}({d['old_rule']}) "
              f"new={d['new_emitted']}({d['new_rule']}) expected={d['expected']} fixed={d['fixed']}", flush=True)
    for d in b1["imperative_no_false_fire_detail"]:
        print(f"[self_test] IMPERATIVE-NO-FALSE-FIRE: {d['sent']!r} old={d['old_emitted']} "
              f"new={d['new_emitted']} fixed={d['fixed']}", flush=True)

    # (6) DECLARED RESIDUAL -- bare tagger-mistagged imperatives still cleanly abstain (not a false positive).
    assert b1["declared_residual_tagger_mistag_clean_abstain"], (
        f"declared residual unexpectedly changed behavior (re-verify + update docstring): {b1['declared_residual_detail']}")
    for d in b1["declared_residual_detail"]:
        print(f"[self_test] DECLARED RESIDUAL (tagger mistag, honest, not claimed fixed): {d['sent']!r} "
              f"emitted={d['emitted']} rule={d['rule']}", flush=True)

    # (7) genuine-verb "please" usage (NON-initial) is NOT swallowed by the DISC override -- regression guard.
    non_disc = ie_extract_fix_all("The manager tries to please the customer.")
    print(f"[self_test] non-initial 'please' (genuine verb usage) regression check: {non_disc} "
          f"(informational -- the DISC override is position-0-scoped only; the classical tagger's own "
          f"context-dependent tag for this construction is whatever it is, not asserted here since it is "
          f"outside this cell's declared scope; only confirming DISC is NOT applied at non-initial position)",
          flush=True)
    _t_please = _build_tags_open_v2("The manager tries to please the customer.", True)
    _please_toks = [t for t in _t_please if t[0].lower() == "please"]
    assert _please_toks and _please_toks[0][1] != "DISC", (
        f"DISC override incorrectly applied to a non-initial 'please': {_t_please}")

    # (8) guard-sentence + OOS regression across ALL 4 extraction variants.
    for sent, gold in GUARD_SENTENCES:
        gset = set(gold)
        for fn, name in ((ie_extract_open_gated, "BASELINE"), (ie_extract_fix1_only, "FIX1"),
                         (ie_extract_fix1_head, "FIX1_HEAD"), (ie_extract_fix_all, "FIX_ALL")):
            assert set(fn(sent)[0]) == gset, f"{name} guard regression on {sent!r}: {fn(sent)}"
    for s in OUT_OF_SCHEMA_CONTROL:
        for fn, name in ((ie_extract_open_gated, "BASELINE"), (ie_extract_fix1_only, "FIX1"),
                         (ie_extract_fix1_head, "FIX1_HEAD"), (ie_extract_fix_all, "FIX_ALL")):
            assert fn(s)[0] == [], f"{name} unexpectedly extracted on OOS control {s!r}: {fn(s)}"
    print("[self_test] guard-sentence regression + out-of-schema control PASS on all 4 arms.", flush=True)

    # (9) real_code_path (F.1): parse the REAL local corpus (feats-aware), apply the REAL simplicity filter,
    # sample a tiny real slice, run ALL 4 arms.
    simple_sorted_v2, length_matched_pool_size_v2 = load_simple_sentences_v2(CONLLU_PATH)
    simple_sorted_old, length_matched_pool_size_old = load_simple_sentences(CONLLU_PATH)
    assert length_matched_pool_size_v2 > 100, f"expected a sizeable length-matched pool, got {length_matched_pool_size_v2}"
    assert 20 < len(simple_sorted_v2) < length_matched_pool_size_v2
    same_ids = ([s["meta"]["sent_id"] for s in simple_sorted_v2] == [s["meta"]["sent_id"] for s in simple_sorted_old])
    assert same_ids, "SAME-SLICE PARITY FAILED: load_simple_sentences_v2 (feats-aware) selected a DIFFERENT " \
                      "sentence-id sequence than Rung 6's own load_simple_sentences"
    print(f"[self_test] SAME-SLICE PARITY confirmed: load_simple_sentences_v2 selects the byte-identical "
          f"{len(simple_sorted_v2)}-sentence sequence Rung 6's own loader selects "
          f"(length_matched_pool={length_matched_pool_size_v2}).", flush=True)

    rows, dist = build_rows_for_seed_v2(simple_sorted_v2, seed=7, n_per_seed=40)
    assert sum(dist.values()) == len(rows), f"distribution counts do not sum to sample size: {dist}"
    non_other = sum(v for c, v in dist.items() if c not in ("other_unhandled",))
    assert non_other > 0, "discriminator-fires check failed: a real 40-sentence tiny slice produced ZERO non-other rows"
    base_res = score_arm(rows, ie_extract_open_gated)
    fixall_res = score_arm(rows, ie_extract_fix_all)
    print(f"[self_test] real_code_path: length_matched_pool={length_matched_pool_size_v2} simple_pool="
          f"{len(simple_sorted_v2)} tiny-slice dist={dist} | BASELINE coverage="
          f"{base_res['coverage_sentence_rate']:.3f} precision={base_res['precision_on_attempted']} | "
          f"FIX_ALL coverage={fixall_res['coverage_sentence_rate']:.3f} precision={fixall_res['precision_on_attempted']}",
          flush=True)

    # (10) SAME-SLICE PARITY (extends F.1): re-derive Rung 6's OWN pooled n_total/n_attempted/n_correct at
    # FULL seeds/N_PER_SEED, byte-for-byte (MEASURED@rung6 metrics.json: n_total=300, n_attempted=26,
    # n_emitted=29, n_correct=11, precision=0.3793103448275862).
    full_rows_old = []
    for seed in SEEDS_FULL:
        r_, _ = build_rows_for_seed(simple_sorted_old, seed, N_PER_SEED)
        full_rows_old.extend(r_)
    assert len(full_rows_old) == 300, f"pooled n_total drifted from Rung 6's 300: got {len(full_rows_old)}"
    full_base = score_arm(full_rows_old, ie_extract_open_gated)
    assert full_base["n_attempted"] == 26, f"n_attempted drifted from Rung 6's 26: got {full_base['n_attempted']}"
    assert full_base["n_correct"] == 11, f"n_correct drifted from Rung 6's 11: got {full_base['n_correct']}"
    assert full_base["n_emitted"] == 29, f"n_emitted drifted from Rung 6's 29: got {full_base['n_emitted']}"
    assert abs(full_base["precision_on_attempted"] - 0.3793103448275862) < 1e-9, full_base["precision_on_attempted"]
    print(f"[self_test] SAME-SLICE PARITY confirmed at FULL scale: n_total=300 n_attempted=26 n_correct=11 "
          f"n_emitted=29 precision=0.3793..., byte-identical to Rung 6's own landed metrics.json "
          f"(commit c71a9eec7) -- this cell measures the SAME real slice Rung 6 measured.", flush=True)

    # (11) ARMS-MUST-DIFFER (META_RULE_AF): all 4 arms' emitted-triple-set hashes pairwise differ on a real
    # slice. Bug 1 (irregular-verb lemma) is a LOW-FREQUENCY differentiator -- MEASURED: 0/40 rows differ
    # between BASELINE and FIX1 at n=40, but 4/100 differ at n=100 (seed 7) -- so this check uses a larger
    # n_per_seed=100 real sample (still trivial wall time) specifically to give bug 1 a fair chance to fire,
    # rather than exempting the pair or padding the check with a synthetic case.
    rows_100, _ = build_rows_for_seed_v2(simple_sorted_v2, seed=7, n_per_seed=100)
    variants = {"BASELINE": ie_extract_open_gated, "FIX1": ie_extract_fix1_only,
                "FIX1_HEAD": ie_extract_fix1_head, "FIX_ALL": ie_extract_fix_all}
    digests = {}
    for name, fn in variants.items():
        all_triples = sorted(set(t for r in rows_100 for t in fn(r["text"])[0]))
        digests[name] = hashlib.sha256(json.dumps(all_triples, sort_keys=True).encode()).hexdigest()
    names = list(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digests[names[i]] != digests[names[j]], (
                f"META_RULE_AF VIOLATION: {names[i]} and {names[j]} bit-identical on real data")
    print(f"[self_test] PASS | ARMS-MUST-DIFFER verified pairwise across all 4 arms "
          f"({', '.join(names)}) on a real 100-sentence slice (seed 7).", flush=True)
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
    print(f"[rung7_fixes_imperatives] run_mode={run_mode} seeds={seeds} n_per_seed={N_PER_SEED} "
          f"expected_n_units={expected_n_units} corpus={CONLLU_PATH}", flush=True)

    agg = run_full(seeds, N_PER_SEED)
    tier, msg, weakest = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    print(f"[rung7_fixes_imperatives] {tier} in {elapsed:.2f}s", flush=True)
    print(f"[rung7_fixes_imperatives] {msg}", flush=True)

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
        "corpus": {
            "name": "UD_English-EWT test split -- SIMPLE-SYNTAX SUBSET (PATH A), SAME slice as Rung 6",
            "path": str(CONLLU_PATH), "license": "CC BY-SA 4.0",
            "same_slice_as": "read_grow_realprose_simple_register_rung6_v1 (commit c71a9eec7)",
            "same_slice_parity_verified": agg["same_slice_parity_vs_rung6_pool"],
            "length_matched_pool_size": agg["length_matched_pool_size"],
            "simple_pool_size": agg["simple_pool_size"],
            "simple_fraction_of_length_matched_pool": agg["simple_fraction_of_length_matched_pool"],
            "n_sampled_total": agg["n_total"],
            "register_note": "PATH A caveat carried forward UNCHANGED from Rung 6: a syntax-simple subset of "
                              "general WEB vocabulary, NOT a vocabulary-controlled early-reader corpus. NOT "
                              "claimed closed even on HARD_PASS -- PATH B remains the next rung.",
        },
        "construction_distribution_counts_v2": agg["construction_distribution_counts_v2"],
        "construction_distribution_fractions_v2": agg["construction_distribution_fractions_v2"],
        "construction_distribution_counts_old_rung6_gold": agg["construction_distribution_counts_old"],
        "n_imperative_by_feats_mood_imp": agg["n_imperative_by_feats"],
        "n_imperative_by_structural_fallback": agg["n_imperative_by_structural_fallback"],
        "arms": {
            "BASELINE_reproduction_old_gold": _strip_rows(agg["baseline_reproduction"]),
            "BASELINE_vs_extended_gold": _strip_rows(agg["baseline_vs_extended_gold"]),
            "FIX1_irregular_verb_only": _strip_rows(agg["fix1_score"]),
            "FIX1_HEAD_bug23": _strip_rows(agg["fix1_head_score"]),
            "FIX_ALL_plus_imperative_PRIMARY": _strip_rows(agg["fix_all_score"]),
            "BASELINE_ungated_informational": _strip_rows(agg["baseline_ungated_informational"]),
        },
        "guard_regression_ok": {
            "baseline": agg["guard_regression_ok_baseline"], "fix1": agg["guard_regression_ok_fix1"],
            "fix1_head": agg["guard_regression_ok_fix1_head"], "fix_all": agg["guard_regression_ok_fix_all"],
        },
        "oos_control_fired": {
            "baseline": agg["oos_control_fired_baseline"], "fix1": agg["oos_control_fired_fix1"],
            "fix1_head": agg["oos_control_fired_fix1_head"], "fix_all": agg["oos_control_fired_fix_all"],
        },
        "bug_fix_evidence": agg["bug_fix_evidence"],
        "sample_fix_all_rows": agg["fix_all_score"]["rows"][:60],
        "sample_baseline_rows": agg["baseline_vs_extended_gold"]["rows"][:60],
        "prereg": {
            "hard_pass": "fix_all_precision_on_attempted>=0.60 AND fix_all_coverage_sentence_rate>=0.05 AND "
                         "guard_regression_ok_fix_all AND oos_control_fired_fix_all AND "
                         "simple_fraction_of_length_matched_pool>=0.10 AND all_named_bugs_verified_fixed",
            "hard_fail": "fix_all_precision_on_attempted<0.55 OR fix_all_coverage_sentence_rate<0.03 OR "
                         "NOT guard_regression_ok_fix_all OR simple_fraction_of_length_matched_pool<0.10",
            "hp_scope": "FIX_ALL (bugs 1+2+3 + imperative construction) is the PRIMARY discriminator. "
                        "BASELINE/FIX1/FIX1_HEAD are informational, per-fix-contribution arms.",
            "scope": "adopts EXACTLY the Rung-6 VET's (a3cac63c) named taxonomy: bug1 irregular-verb lookup-"
                     "ordering, bug2/3 multi-token noun head selection, imperative construction handling. "
                     "Does NOT fix COREF_UNRESOLVED (out of the named scope, flagged as the dominant remaining "
                     "coverage bottleneck) or the classical-tagger sentence-initial-capitalization residual "
                     "(bare 2-3-token imperatives, declared not fixed).",
            "honest_guard": "no fix is keyed to the literal Rung-6 error sentences -- bug1 reuses the "
                            "EXISTING IRREGULAR_VERB_LEMMA table wholesale (Rung 5), bug2/3 is a single "
                            "general capitalization-based head-selection rule verified on 2 doc-cited + 4 "
                            "genuinely novel nonce cases + 1 regression guard, imperative handling verified "
                            "on 2 real corpus rows + 1 contract-canonical nonce + an explicit declared "
                            "residual (see bug_fix_evidence.declared_residual_detail).",
            "compute_architecture": "sequential-CPU; pure syntactic parsing + dependency-tree traversal, no "
                                    "VSA store; wall time trivial (MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer + dependency-classifier test)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "runner_python_u_only (timeout_s < 1800; cell wall time is seconds, matching "
                                 "Rung 5/5b/6's own precedent)",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["parse_conllu_v2 (real local corpus file, feats-aware, this cell)",
                                         "load_simple_sentences_v2 (NEW feats-aware loader, verified SAME-"
                                         "SLICE-PARITY vs Rung 6)", "analyze_sentence_v2 (Rung 5's "
                                         "analyze_sentence + imperative extension, this cell)",
                                         "ie_extract_open_gated (Rung 5b BASELINE, imported unmodified)",
                                         "ie_extract_fix1_only / ie_extract_fix1_head / ie_extract_fix_all "
                                         "(this cell, parameterized fix arms)",
                                         "nltk.pos_tag (real classical averaged-perceptron call)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete syntactic role-assignment + "
                       "the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED), same "
                       "as Rung 5/5b/6.",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports) AND a "
                               "runtime sys.modules transitive-closure check after nltk use, both asserted "
                               "at self-test",
            "prior_work_check": "substrate_query.sh run before authoring (see completion report) -- top hits "
                                "were generic wordnet 'subject'/'objection' concept-graph nodes (cosine<=0.366), "
                                "not prior experiment cells; this is a genuinely novel measurement within the "
                                "actively-developed RUNG 2-7 open-text-reading arc, not a rediscovery.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[rung7_fixes_imperatives] metrics written -> {out_dir / 'metrics.json'}", flush=True)
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
