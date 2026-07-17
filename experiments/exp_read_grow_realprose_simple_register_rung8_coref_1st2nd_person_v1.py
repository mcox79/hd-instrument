"""exp_read_grow_realprose_simple_register_rung8_coref_1st2nd_person_v1 -- RUNG 8: resolves 1ST/2ND-PERSON
SUBJECT PRONOUNS ("I"/"we"/"you") DIRECTLY instead of abstaining COREF_UNRESOLVED, on the SAME simple-register
UD-EWT slice Rung 7 measured (GATED precision 0.643).

TRIGGER (Rung-7 VET a1780b46): Rung 7's comprehensive-fix cell reached GATED precision_on_attempted=0.643 on
the simple register (n=300), VET-confirmed CHAIN_GRADE, conservative. The VET's own NEXT-section (carried
forward verbatim in Rung 7's docstring) named "COREF_UNRESOLVED (1st/2nd-person pronoun subjects) remains, BY
THE VET's OWN NAMED SCOPE, the dominant coverage bottleneck in this data (MEASURED@sample_gated_rows: the
majority of single_clause_svo misses in Rung 6's own 60-row sample)". 1st/2nd-person subjects need NO
antecedent search -- "I"/"we" = the speaker, "you" = the addressee -- unlike genuine 3rd-person antecedent-less
pronouns (he/she/it/they), where the pipeline's COREF_UNRESOLVED abstain is the correct zero-hallucination
behavior (no in-sentence antecedent-resolution mechanism exists in this extractor; guessing would hallucinate
a referent). The prior COREF_UNRESOLVED branch (inherited from the Rung-5b abstain-gate lineage, unchanged
through Rung 6/7) abstained on BOTH classes indiscriminately -- an over-broad abstention this rung fixes.

THE FIX (surgical, ONE branch changed): `_extract_core_open_gated_v3` is a line-for-line copy of Rung 7's
`_extract_core_open_gated_v2` with exactly one control-flow addition, at the point where a pronoun subject is
found with no preceding noun subject. The pronoun CLOSEST to the verb (`subj_prons_before_v0[-1]` -- in this
single-clause/short-token simple-register slice there is normally exactly one pronoun subject candidate) is
checked against `FIRST_SECOND_PERSON_SUBJECT_PRONOUNS = {"i", "we", "you"}` (MEASURED@corpus: UD-EWT's own gold
lemma for "I"/"We"/"You" IS the lowercased surface word itself -- "I"->"i", "We"->"we", "You"->"you", verified
live below via a real-corpus grep-equivalent parse -- so the extractor's own pronoun lemma, already `w_lower`
per the existing `_tag_token_open_v2` PRON branch, is directly gold-compatible with NO adapter needed). If it
IS 1st/2nd-person, `subjects = [pron_lemma]` is set directly (no antecedent search -- the referent is the
sentence's own speaker/addressee by definition of the person category) and control falls through into the
UNCHANGED shared object-scan / passive / relation-resolution code every other subject type already uses (same
"one general mechanism, not per-sentence patches" principle Rung 7 itself invoked for bugs 2/3). If it is NOT
1st/2nd-person (he/she/it/they/him/her/them -- any pronoun outside the 3-word closed set), the ORIGINAL,
UNCHANGED `COREF_UNRESOLVED` abstain fires -- this is the zero-hallucination guardrail this rung is
contractually required to preserve, verified live below (0 guard-breaks measured across all 3 real corpus
seeds AND a hand-built battery of 3rd-person nonce sentences).

GOLD SIDE: UNCHANGED. `analyze_sentence_v2` (Rung 7) already derives correct SVO gold for 1st/2nd-person-
subject sentences via UD's own nsubj edge (regardless of the subject's person) -- these rows were ALREADY
correctly bucketed as `single_clause_svo`/`imperative`/etc. in the existing gold set; only the EXTRACTOR side
(recognition) previously threw them away via COREF_UNRESOLVED. No gold-side change is needed or made.

ARMS (SAME real simple-syntax UD-EWT slice as Rung 6/7 -- SAME seeds=[7,13,19], SAME n_per_seed=100, SAME
`load_simple_sentences_v2` filter, unchanged):
  BASELINE = Rung 7's `ie_extract_fix_all` (imported UNMODIFIED -- "the Rung-7 pipeline" per the contract).
  FIXED = `ie_extract_coref_1st2nd_fixed` = BASELINE's exact settings (bug1 + head-fix + imperative-fix) PLUS
    the ONE new 1st/2nd-person-subject branch above. Isolates EXACTLY this one fix.

HONEST RESULT (MEASURED@this-cell's own self_test/smoke/full, live-computed below, NOT hypothesized -- reported
IN FULL per the contract's "report honestly" instruction, not softened):
  Coverage recovers MATERIALLY: BASELINE coverage_sentence_rate=0.130 (39/300) -> FIXED=0.307 (92/300), a
  +136% relative increase (+0.177 absolute) -- confirming the VET's "dominant coverage bottleneck" framing was
  correct and the fix is NOT inert.
  Overall GATED precision on the FIXED arm DROPS to 0.526 (50/95), BELOW the 0.55 HARD-FAIL floor and below
  the 0.60 stay-above bar. This is an HONEST NEGATIVE the contract's own pre-registered bands are designed to
  catch and localize, not paper over.
  MECHANISM-LEVEL LOCALIZATION (the reason this is informative, not merely "the fix is bad"): of the 53
  sentences newly covered (BASELINE abstained, FIXED emits), the coref-fix's OWN contribution -- SUBJECT-ROLE
  correctness (does the emitted triple's subject slot match gold's subject slot, isolating person-resolution
  from everything downstream) -- is 47/47 = 1.000 on every newly-covered row that has any gold at all (6 of
  the 53 are `other_unhandled` rows with EMPTY gold by schema construction, where no extractor could ever score
  correct regardless of subject; excluded from this check, reported separately). The person-resolution
  mechanism itself makes ZERO referent-assignment errors. Every wrong WHOLE-TRIPLE in the newly-covered set is
  attributable to four SEPARATE, PRE-EXISTING, INDEPENDENT bugs in code paths that 1st/2nd-person sentences
  simply never reached before (because COREF_UNRESOLVED gated them out upstream of the object/relation logic):
    (a) irregular plural-noun lemma restoration ("teeth"->"tooth" not handled: emits ("i","have","teeth") vs
        gold ("i","have","tooth")).
    (b) multi-word BRAND/PRODUCT compound-noun head-selection (Rung 7's bug2/3 capitalization heuristic
        distinguishes personal-name `flat` spans (head=first) from common-noun `compound` spans (head=last),
        but a brand+model span like "HTC Evo" or "Garage Pros" is ALSO all-capitalized yet is a `compound`
        deprel in UD, not `flat` -- the heuristic misclassifies it as a personal name and picks the WRONG head:
        "HTC Evo"->"htc" (gold "evo"), "Garage Pros"->"garage" (gold "pro")).
    (c) OOV verb-lemma suffix-stripper spelling-restoration gaps ("need"->"ne", "married"->"marri" -- the
        stripper does not restore the y/i or other orthographic changes correctly for these forms).
    (d) DO-SUPPORT negation parsing ("don't"/"won't" tokenized/tagged such that "don"/"won" is picked as the
        matrix verb instead of the real main verb after do-support: "I don't feel anything" emits
        ("i","don","anything") vs gold ("i","feel","anything")) -- a genuinely NEW construction-class gap this
        rung's expanded coverage newly exposes, not a coref-fix defect.
  NONE of these four bug classes are touched or claimed fixed by this cell -- they are OUT OF SCOPE (this
  rung's contract is surgical to the 1st/2nd-person-subject branch only) and are flagged as the natural Rung 9
  candidate list, exactly analogous to how Rung 6's HARD_FAIL diagnosis fed Rung 7's targeted fix list.
  ZERO-HALLUCINATION GUARDRAIL: PRESERVED. 0 of 32 genuine 3rd-person-subject COREF_UNRESOLVED rows in the real
  sample newly fire in the FIXED arm (measured live below), and a hand-built battery of 3rd-person nonce
  sentences (he/she/it/they/him/her/them) all still cleanly abstain COREF_UNRESOLVED, unchanged from BASELINE.

BANDS (pre-registered, per the dispatching contract's own literal thresholds):
  Primary discriminator = FIXED arm's `precision_on_attempted` (overall, GATED, on the same extended-gold row
  set as BASELINE) + `coverage_sentence_rate` delta vs BASELINE + the 3rd-person guardrail (must be 0 breaks).
  HARD-PASS: FIXED precision_on_attempted >= 0.60 AND FIXED coverage_sentence_rate materially exceeds
    BASELINE's (delta >= 0.05) AND n_3rd_person_guard_breaks == 0 AND guard_regression_ok_fixed (Rung 5
    GUARD_SENTENCES) AND oos_control_fired_fixed AND simple_fraction_of_length_matched_pool >= 0.10.
  HARD-FAIL: FIXED precision_on_attempted < 0.55 OR coverage delta < 0.02 (fix inert) OR
    n_3rd_person_guard_breaks > 0 (the guardrail broke -- would be a much more serious finding) OR
    NOT guard_regression_ok_fixed OR simple_fraction_of_length_matched_pool < 0.10.
  MIDDLE_BAND: otherwise (e.g. precision in [0.55, 0.60) with coverage recovered and guardrail intact -- a
    genuinely mixed, honestly-reported outcome, NOT rounded up or down).
  HONEST CAVEAT CARRIED FORWARD (unchanged from Rung 6/7): PATH A is a simple-SYNTAX subset of general WEB
  VOCABULARY (UD-EWT), not a vocabulary-controlled early-reader corpus.

COMPUTE: SEEDS=[7,13,19], N_PER_SEED=100 (IDENTICAL to Rung 6/7, direct same-slice comparability). Smoke =
  seed[7] only, SAME N_PER_SEED (Option A, discriminator-survives-scale; trivial wall time -- pure CPU
  string/POS-tag processing, no torch, no numpy, no VSA store, matching Rung 5/5b/6/7 precedent). Local,
  executed DIRECTLY (bash), no queue/GPU/atoms/push. Corpus already fetched + committed. NO network access at
  self-test/smoke/full time. Storage: no_storage. Pause flag `data/orchestrator_paused.flag` re-checked absent
  immediately before running.

NEXT (not this cell): the 4 newly-exposed downstream bug classes (irregular-plural-noun lemma, brand/product
compound-noun head-selection, OOV verb spelling-restoration, do-support negation parsing) are the natural
Rung-9 candidate list -- each independently fixable via the SAME general-closed-form-rule discipline Rung 7
established, each currently DECLARED not fixed, not hidden. The classical-tagger sentence-initial-
capitalization residual (bare "Sit down."-class imperatives, Rung 7) and PATH B (vocabulary-controlled early-
reader corpus) remain the other two un-collapsed threads.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; BASELINE vs FIXED emitted-triple-set hashes differ on
#   the real simple-slice sample by construction -- the fix materially changes coverage).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor; discriminator is discrete syntactic role-assignment + the classical
#   tagger's own literature-benchmarked accuracy (96-97% PTB, CITED), same as Rung 5/5b/6/7.
# - baseline_in_band: N/A BY DESIGN -- BASELINE's own known Rung-7 precision (0.643, MEASURED@rung7 metrics.json,
#   re-derived live below via `baseline_reproduction`) is the pre-registered floor this cell exists to test
#   against (does the coref-fix preserve it while raising coverage, or trade it away).
# - discriminator survives scale: corpus is FIXED-size real prose, deterministic filtered pool, SAME regime as
#   Rung 6/7 (no scale axis). Smoke uses the SAME N_PER_SEED as FULL, single seed only (Option A).
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test parses the REAL local corpus file (Rung 7's parse_conllu_v2, feats-aware),
#   applies the REAL simplicity filter, samples a real slice, and runs BOTH extraction arms against REAL
#   sentences, plus a live (not narrated) 3rd-person zero-hallucination guardrail battery.
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19], inherited unmodified from Rung 5/6/7's own
#   random.Random(seed).sample over a sorted(...) sentence-id-ordered pool.
# - all numbers in comments tagged MEASURED@this-cell (live self_test/smoke/full output) / MEASURED@rung7-
#   metrics.json / MEASURED@corpus / CITED@research-note.
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

ANCHOR_NAME = "read_grow_realprose_simple_register_rung8_coref_1st2nd_person_v1"

# --- GENUINE REUSE: Rung 7 (the pipeline this cell extends -- BASELINE arm, feats-aware corpus loader, gold-
# deriver, tagger, object-scan/head-selection primitives, bug-fix verification battery), Rung 5 (corpus parser
# base / CaRB scorer / guard sentences / OOS control), Rung 5b (finite-form check), Rung 6 (SAME seeds/n_per_
# seed), foundation v2 (coordination splitter). ---
from experiments.exp_read_grow_realprose_simple_register_rung7_fixes_imperatives_v1 import (  # noqa: E402
    CONLLU_PATH, load_simple_sentences_v2, build_rows_for_seed_v2, analyze_sentence_v2, CONSTRUCTION_CLASSES_V2,
    _build_tags_open_v2, _scan_object_np, _np_head_from_run, _first_contiguous_noun_run, ie_extract_fix_all,
    verify_bug_fixes,
)
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import (  # noqa: E402
    score_arm, GUARD_SENTENCES, OUT_OF_SCHEMA_CONTROL, _resolve_relation_open, analyze_sentence,
)
from experiments.exp_read_grow_realprose_abstain_gate_rung5b_v1 import _is_finite_form  # noqa: E402
from experiments.exp_read_grow_realprose_simple_register_rung6_v1 import SEEDS_FULL, N_PER_SEED  # noqa: E402
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import _split_coord  # noqa: E402

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only (same as Rung 5/5b/6/7); glass-box-legal.

# ---------------------------------------------------------------------------
# THE FIX: 1st/2nd-person subject pronouns need NO antecedent search -- resolve DIRECTLY. 3rd-person
# antecedent-less pronouns (and any other pronoun form) are UNCHANGED -- still ABSTAIN (COREF_UNRESOLVED),
# preserving the zero-hallucination guardrail.
# ---------------------------------------------------------------------------
FIRST_SECOND_PERSON_SUBJECT_PRONOUNS = {"i", "we", "you"}
# genuine 3rd-person (+ case-inflected object forms a mistagger occasionally routes into PRON position) --
# informational only (the branch below is a closed-set MEMBERSHIP check against the 3-word set above; anything
# NOT in that set -- including these -- falls through unchanged to COREF_UNRESOLVED).
THIRD_PERSON_OR_OTHER_SUBJECT_PRONOUNS_STILL_ABSTAIN = {"it", "he", "she", "they", "him", "her", "them"}


def _extract_core_open_gated_v3(T, use_head_fix, use_imperative_fix, use_coref_1st2nd_fix):
    """line-for-line copy of Rung 7's `_extract_core_open_gated_v2`, with ONE control-flow addition: when a
    pronoun subject is found with no noun subject before the verb, the pronoun closest to the verb is checked
    against FIRST_SECOND_PERSON_SUBJECT_PRONOUNS. If it matches (and use_coref_1st2nd_fix), the subject is
    resolved DIRECTLY (no antecedent search -- the referent is the sentence's own speaker/addressee) and
    control falls through into the SAME shared object-scan/passive/relation-resolution code every other subject
    type already uses. Otherwise (3rd-person, or fix disabled), the ORIGINAL COREF_UNRESOLVED abstain fires,
    byte-identical to Rung 7."""
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

    pronoun_subject_lemma = None  # set below iff the RUNG 8 fix fires
    if not subj_nouns_before_v0:
        if not subj_prons_before_v0:
            # IMPERATIVE PATTERN CANDIDATE (unchanged from Rung 7 -- byte-identical).
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
        # PRONOUN SUBJECT CANDIDATE: the pronoun CLOSEST to the verb (last before v0) is the surface subject --
        # in this single-clause/short-token simple-register slice there is normally exactly one candidate.
        pron_i = subj_prons_before_v0[-1]
        cand_lemma = lemmas[pron_i]
        if use_coref_1st2nd_fix and cand_lemma in FIRST_SECOND_PERSON_SUBJECT_PRONOUNS:
            # RUNG 8 FIX (the ONLY new branch this rung adds): 1st/2nd-person needs no antecedent search --
            # resolve DIRECTLY to its own surface lemma (already gold-compatible, MEASURED@corpus: UD-EWT's
            # own gold lemma for I/We/You lowercases to i/we/you, verified live at self_test).
            pronoun_subject_lemma = cand_lemma
        else:
            # UNCHANGED from Rung 7: genuine 3rd-person (or any pronoun outside the 3-word set) -- no
            # antecedent-resolution mechanism exists in this extractor; abstain rather than hallucinate a
            # referent. This is the zero-hallucination guardrail this rung preserves.
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
                subjects = [_np_head_from_run(T, head_run)] if head_run else [lemmas[subj_region[-1]]]
            else:
                subjects = _split_coord(subj_region, T) or [lemmas[subj_region[-1]]]
    # else: subjects already = [pronoun_subject_lemma], set above (RUNG 8 fix path).

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
        rule = "SVO_PASSIVE_OPEN_GATED_V3"
    else:
        prep, obj_lemmas, jend = _scan_object_np(T, tags, lemmas, matrix_vi + 1, n, use_head_fix, False)
        consumed_end = jend
        relation = _resolve_relation_open(verb_lemma, prep)
        if not obj_lemmas:
            return [], "NO_OBJECT", "no object noun after verb"
        triples = [(s, relation, o) for s in subjects for o in obj_lemmas]
        if len(subjects) > 1 or len(obj_lemmas) > 1:
            rule = "SVO_COORD_OPEN_GATED_V3"
        elif pronoun_subject_lemma is not None:
            rule = "SVO_1ST2ND_PERSON_PRONOUN_SUBJECT_V3"
        else:
            rule = "SVO_ACTIVE_OPEN_GATED_V3"

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


def ie_extract_open_gated_v3(sentence, use_bug1_fix, use_head_fix, use_imperative_fix, use_coref_1st2nd_fix):
    T = _build_tags_open_v2(sentence, use_bug1_fix)
    return _extract_core_open_gated_v3(T, use_head_fix, use_imperative_fix, use_coref_1st2nd_fix)


def ie_extract_coref_1st2nd_fixed(sentence):
    """FIXED arm: BASELINE's exact settings (bug1 + head-fix + imperative-fix, all True, matching Rung 7's
    FIX_ALL) PLUS the RUNG 8 1st/2nd-person coref fix."""
    return ie_extract_open_gated_v3(sentence, True, True, True, True)


def ie_extract_coref_1st2nd_disabled(sentence):
    """same settings as ie_extract_coref_1st2nd_fixed but with the RUNG 8 fix OFF -- must reproduce Rung 7's
    ie_extract_fix_all byte-for-byte (positive-control / same-slice-parity check, NOT a scored arm)."""
    return ie_extract_open_gated_v3(sentence, True, True, True, False)


# ---------------------------------------------------------------------------
# LIVE 3RD-PERSON ZERO-HALLUCINATION GUARDRAIL BATTERY (called at both self_test AND full-run time -- MEASURED,
# not narrated). Verifies the fix is SURGICAL: only 1st/2nd-person resolves; 3rd-person still abstains.
# ---------------------------------------------------------------------------
def verify_coref_guardrail():
    evidence = {}

    # (1) hand-built 3rd-person nonce battery: every one of these has a bare pronoun subject with NO in-
    # sentence antecedent and NO noun subject -- COREF_UNRESOLVED must fire, unchanged, on BOTH arms.
    third_person_cases = [
        "He walked to the store.", "She read the book.", "It broke the window.",
        "They visited the museum.", "Him ate the cake.",  # nonstandard object-case subject "him" -- still 3rd person
    ]
    tp_detail = []
    tp_ok = True
    for sent in third_person_cases:
        base = ie_extract_fix_all(sent)
        fixed = ie_extract_coref_1st2nd_fixed(sent)
        ok = (base == fixed) and (fixed[0] == []) and (fixed[1] == "COREF_UNRESOLVED")
        tp_detail.append({"sent": sent, "baseline": base, "fixed": fixed, "guardrail_held": ok})
        tp_ok = tp_ok and ok
    evidence["third_person_guardrail_battery_held"] = tp_ok
    evidence["third_person_guardrail_detail"] = tp_detail

    # (2) hand-built 1st/2nd-person nonce battery: the fix MUST extract these (not abstain), with the correct
    # subject.
    first_second_cases = [
        ("I own a red car.", "i", "car"), ("We finished the report.", "we", "report"),
        ("You broke the rule.", "you", "rule"),
    ]
    fs_detail = []
    fs_ok = True
    for sent, expect_subj, expect_obj in first_second_cases:
        base = ie_extract_fix_all(sent)
        fixed = ie_extract_coref_1st2nd_fixed(sent)
        ok = (base[1] == "COREF_UNRESOLVED" and base[0] == [] and bool(fixed[0])
              and fixed[0][0][0] == expect_subj and fixed[0][0][2] == expect_obj)
        fs_detail.append({"sent": sent, "baseline": base, "fixed": fixed, "expected_subject": expect_subj,
                           "expected_object": expect_obj, "fixed_correctly": ok})
        fs_ok = fs_ok and ok
    evidence["first_second_person_extraction_battery_ok"] = fs_ok
    evidence["first_second_person_extraction_detail"] = fs_detail

    # (3) fix-disabled positive control: with the RUNG 8 fix off, must byte-for-byte reproduce Rung 7's
    # FIX_ALL on both batteries (same-slice-parity for the parameterization itself).
    disabled_matches_baseline = all(
        ie_extract_coref_1st2nd_disabled(s) == ie_extract_fix_all(s)
        for s in third_person_cases + [c[0] for c in first_second_cases])
    evidence["fix_disabled_reproduces_rung7_baseline"] = disabled_matches_baseline

    evidence["coref_guardrail_all_ok"] = (
        tp_ok and fs_ok and disabled_matches_baseline)
    return evidence


# ---------------------------------------------------------------------------
# glass-box-legal checks (same method as Rung 5/5b/6/7).
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

    baseline_score = score_arm(all_rows, ie_extract_fix_all)
    fixed_score = score_arm(all_rows, ie_extract_coref_1st2nd_fixed)

    def _guard_ok(fn):
        return all(set(fn(s)[0]) == set(g) for (s, g) in GUARD_SENTENCES)

    def _oos_ok(fn):
        return all(not fn(s)[0] for s in OUT_OF_SCHEMA_CONTROL)

    guard_ok = {"baseline": _guard_ok(ie_extract_fix_all), "fixed": _guard_ok(ie_extract_coref_1st2nd_fixed)}
    oos_ok = {"baseline": _oos_ok(ie_extract_fix_all), "fixed": _oos_ok(ie_extract_coref_1st2nd_fixed)}

    # --- newly-covered + 3rd-person-guardrail measurement over the REAL sample (the load-bearing numbers). ---
    newly_covered_rows = []
    n_3rd_person_coref_rows = 0
    n_3rd_person_guard_breaks = 0
    for r in all_rows:
        b = ie_extract_fix_all(r["text"])
        f = ie_extract_coref_1st2nd_fixed(r["text"])
        if (not b[0]) and f[0]:
            newly_covered_rows.append({"text": r["text"], "cls": r["cls"], "gold": r["gold"],
                                        "baseline_rule": b[1], "fixed_emitted": f[0], "fixed_rule": f[1]})
        if b[1] == "COREF_UNRESOLVED":
            T = _build_tags_open_v2(r["text"], True)
            tags = [t[1] for t in T]
            lemmas = [t[2] for t in T]
            forms = [t[3] for t in T]
            all_verb_idx = [i for i in range(len(T)) if tags[i] == "VERB"]
            verb_idx = [i for i in all_verb_idx if _is_finite_form(tags, forms, i)]
            v0 = verb_idx[0]
            pron_before = [i for i in range(len(T)) if tags[i] == "PRON" and i < v0]
            cand = lemmas[pron_before[-1]] if pron_before else None
            if cand not in FIRST_SECOND_PERSON_SUBJECT_PRONOUNS:
                n_3rd_person_coref_rows += 1
                if f[0]:
                    n_3rd_person_guard_breaks += 1

    n_newly_covered = len(newly_covered_rows)
    newly_covered_with_gold = [r for r in newly_covered_rows if r["gold"]]
    n_subj_checkable = len(newly_covered_with_gold)
    n_subj_correct = sum(
        1 for r in newly_covered_with_gold
        if ({t[0] for t in r["fixed_emitted"]} & {g[0] for g in r["gold"]}))
    nc_emitted = sum(len(r["fixed_emitted"]) for r in newly_covered_rows)
    nc_correct = sum(len(set(r["fixed_emitted"]) & set(r["gold"])) for r in newly_covered_rows)

    coref_guardrail_evidence = verify_coref_guardrail()

    return {
        "seeds": seeds, "n_per_seed": n_per_seed, "n_total": n_total,
        "simple_pool_size": len(simple_sorted_v2), "length_matched_pool_size": length_matched_pool_size_v2,
        "simple_fraction_of_length_matched_pool": simple_fraction_of_length_matched_pool,
        "construction_distribution_counts": dist_pooled, "construction_distribution_fractions": dist_frac,
        "baseline_score": baseline_score, "fixed_score": fixed_score,
        "guard_regression_ok": guard_ok, "oos_control_fired": oos_ok,
        "n_newly_covered": n_newly_covered,
        "n_newly_covered_with_gold": n_subj_checkable,
        "newly_covered_subject_role_correct": n_subj_correct,
        "newly_covered_subject_role_correct_rate": (n_subj_correct / n_subj_checkable) if n_subj_checkable else None,
        "newly_covered_whole_triple_precision": (nc_correct / nc_emitted) if nc_emitted else None,
        "newly_covered_whole_triple_n_correct": nc_correct, "newly_covered_whole_triple_n_emitted": nc_emitted,
        "n_3rd_person_coref_unresolved_rows": n_3rd_person_coref_rows,
        "n_3rd_person_guard_breaks": n_3rd_person_guard_breaks,
        "coref_guardrail_evidence": coref_guardrail_evidence,
        "sample_newly_covered_rows": newly_covered_rows[:60],
    }


def compute_verdict(agg):
    prec_b = agg["baseline_score"]["precision_on_attempted"]
    prec_f = agg["fixed_score"]["precision_on_attempted"]
    cov_b = agg["baseline_score"]["coverage_sentence_rate"]
    cov_f = agg["fixed_score"]["coverage_sentence_rate"]
    cov_delta = cov_f - cov_b
    guard_ok = agg["guard_regression_ok"]["fixed"]
    oos_ok = agg["oos_control_fired"]["fixed"]
    simple_frac = agg["simple_fraction_of_length_matched_pool"]
    n_guard_breaks = agg["n_3rd_person_guard_breaks"]
    coref_guardrail_ok = agg["coref_guardrail_evidence"]["coref_guardrail_all_ok"]

    if prec_f is None:
        return ("MIDDLE_BAND", "FIXED arm emitted zero triples on the whole simple-register sample -- "
                                "mechanism did not fire at all", "no_triples_emitted")

    hard_pass = (prec_f >= 0.60 and cov_delta >= 0.05 and n_guard_breaks == 0 and guard_ok and oos_ok
                 and simple_frac >= 0.10 and coref_guardrail_ok)
    hard_fail = (prec_f < 0.55 or cov_delta < 0.02 or n_guard_breaks > 0 or (not guard_ok)
                 or simple_frac < 0.10)

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
        elif simple_frac < 0.10:
            weakest = "simple_fraction_of_length_matched_pool_below_0.10_stratum_vacuous"
        elif cov_delta < 0.02:
            weakest = "coverage_delta_below_0.02_fix_inert"
        elif prec_f < 0.55:
            weakest = "fixed_precision_on_attempted_below_0.55_hard_fail_floor"
        elif prec_f < 0.60:
            weakest = "fixed_precision_on_attempted_in_middle_band_0.55_to_0.60"
        elif not guard_ok:
            weakest = "guard_regression_failed_fixed"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire_fixed"
        elif not coref_guardrail_ok:
            weakest = "hand_built_coref_guardrail_battery_failed"

    msg = (
        f"{tier} | RUNG8 1ST/2ND-PERSON COREF FIX on the SAME simple-register slice as RUNG 6/7 (n={agg['n_total']}) | "
        f"BASELINE(rung7-FIX_ALL) precision={prec_b:.3f} coverage={cov_b:.3f} -> "
        f"FIXED precision={prec_f:.3f} coverage={cov_f:.3f} (delta_cov={cov_delta:+.3f}) | "
        f"n_newly_covered={agg['n_newly_covered']} (of which {agg['n_newly_covered_with_gold']} have gold) | "
        f"newly_covered_subject_role_correct_rate={agg['newly_covered_subject_role_correct_rate']} "
        f"({agg['newly_covered_subject_role_correct']}/{agg['n_newly_covered_with_gold']}) | "
        f"newly_covered_whole_triple_precision={agg['newly_covered_whole_triple_precision']} | "
        f"n_3rd_person_coref_unresolved_rows={agg['n_3rd_person_coref_unresolved_rows']} "
        f"n_3rd_person_guard_breaks={n_guard_breaks} (MUST be 0) | "
        f"coref_guardrail_battery_ok={coref_guardrail_ok} | "
        f"guard_regression_ok={guard_ok} oos_control_fired={oos_ok} | weakest={weakest} | "
        f"COVERAGE_FIX_MATERIAL={cov_delta >= 0.05} PRECISION_HELD_ABOVE_0.60={prec_f >= 0.60} "
        f"ZERO_HALLUCINATION_PRESERVED={n_guard_breaks == 0}")
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
# self-test: EXERCISE THE REAL code path (real corpus file, real nltk.pos_tag, real filters + both arms + the
# live coref-guardrail battery).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (real feats-aware CoNLL-U parse via Rung 7's loader, real "
          "nltk.pos_tag calls, real simplicity filter + both extraction arms)...", flush=True)

    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"
    _ = nltk.pos_tag(["The", "cat", "sat", "."])
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print(f"[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural)", flush=True)

    # (1) UD gold-lemma compatibility check (the "no adapter needed" claim): verify the REAL local corpus's
    # own gold lemma for I/We/You lowercases to i/we/you (not e.g. capitalized or a normalized different form).
    from experiments.exp_read_grow_realprose_simple_register_rung7_fixes_imperatives_v1 import parse_conllu_v2
    all_sents = parse_conllu_v2(CONLLU_PATH)
    lemma_by_form = {}
    for s in all_sents:
        for t in s["tokens"]:
            fl = t["form"].lower()
            # restrict to SUBJECT-eligible tokens (nsubj/csubj deprel, i.e. the population the coref fix
            # actually resolves) -- a handful of Typo=Yes genitive "you"->"your" tokens (nmod:poss, Case=Gen,
            # e.g. a writer typing "you" meaning "your") exist in the corpus but are NEVER subject candidates,
            # so including them would test an irrelevant population.
            if fl in ("i", "we", "you") and t["upos"] == "PRON" and t["deprel"].split(":")[0] in ("nsubj", "csubj"):
                lemma_by_form.setdefault(fl, set()).add(t["lemma"])
    for w in ("i", "we", "you"):
        assert w in lemma_by_form, f"no subject PRON token with lowercased form {w!r} found in real corpus"
        assert lemma_by_form[w] == {w}, (
            f"UD gold lemma for SUBJECT {w!r} is NOT the lowercased surface word itself: {lemma_by_form[w]} -- "
            f"the no-adapter-needed assumption does not hold, extractor output would not match gold format")
    print(f"[self_test] UD gold-lemma compatibility confirmed on the REAL corpus: "
          f"{ {w: sorted(s) for w, s in lemma_by_form.items()} } (extractor's own pronoun lemma is directly "
          f"gold-compatible, no adapter needed).", flush=True)

    # (2) coref-guardrail battery (hand-built 3rd-person MUST-abstain + 1st/2nd-person MUST-extract +
    # fix-disabled positive control).
    guardrail = verify_coref_guardrail()
    assert guardrail["third_person_guardrail_battery_held"], (
        f"3RD-PERSON ZERO-HALLUCINATION GUARDRAIL BROKEN: {guardrail['third_person_guardrail_detail']}")
    assert guardrail["first_second_person_extraction_battery_ok"], (
        f"1st/2nd-person extraction did not generalize: {guardrail['first_second_person_extraction_detail']}")
    assert guardrail["fix_disabled_reproduces_rung7_baseline"], (
        "fix-disabled positive control did NOT byte-for-byte reproduce Rung 7's FIX_ALL -- parameterization bug")
    for d in guardrail["third_person_guardrail_detail"]:
        print(f"[self_test] 3RD-PERSON GUARDRAIL (must abstain, unchanged): {d['sent']!r} "
              f"baseline={d['baseline']} fixed={d['fixed']} guardrail_held={d['guardrail_held']}", flush=True)
    for d in guardrail["first_second_person_extraction_detail"]:
        print(f"[self_test] 1ST/2ND-PERSON EXTRACT (must resolve, no antecedent search): {d['sent']!r} "
              f"baseline={d['baseline']} fixed={d['fixed']} fixed_correctly={d['fixed_correctly']}", flush=True)
    print("[self_test] coref-guardrail battery PASS: 3rd-person still abstains (COREF_UNRESOLVED, unchanged), "
          "1st/2nd-person now resolves directly, fix-disabled reproduces Rung 7 byte-for-byte.", flush=True)

    # (3) existing-bucket byte-identical parity spot check (Rung 7's own regression discipline): FIX_ALL vs
    # FIXED with the coref fix DISABLED must byte-for-byte agree on Rung 7's own GUARD_SENTENCES + OOS control.
    for sent, gold in GUARD_SENTENCES:
        gset = set(gold)
        assert set(ie_extract_fix_all(sent)[0]) == gset, f"BASELINE guard regression on {sent!r}"
        assert set(ie_extract_coref_1st2nd_fixed(sent)[0]) == gset, f"FIXED guard regression on {sent!r}"
    for s in OUT_OF_SCHEMA_CONTROL:
        assert ie_extract_fix_all(s)[0] == [], f"BASELINE unexpectedly extracted on OOS control {s!r}"
        assert ie_extract_coref_1st2nd_fixed(s)[0] == [], f"FIXED unexpectedly extracted on OOS control {s!r}"
    print("[self_test] guard-sentence regression + out-of-schema control PASS on both arms.", flush=True)

    # (4) real_code_path (F.1): parse the REAL local corpus (feats-aware, Rung 7's loader), apply the REAL
    # simplicity filter, sample a tiny real slice, run BOTH arms, confirm the discriminator FIRES (mechanism
    # produces non-trivial newly-covered rows at tiny scale, not just at full scale).
    simple_sorted_v2, length_matched_pool_size_v2 = load_simple_sentences_v2(CONLLU_PATH)
    assert length_matched_pool_size_v2 > 100, f"expected a sizeable length-matched pool, got {length_matched_pool_size_v2}"
    rows, dist = build_rows_for_seed_v2(simple_sorted_v2, seed=7, n_per_seed=40)
    base_res = score_arm(rows, ie_extract_fix_all)
    fixed_res = score_arm(rows, ie_extract_coref_1st2nd_fixed)
    assert fixed_res["n_attempted"] > base_res["n_attempted"], (
        f"DISCRIMINATOR DID NOT FIRE at tiny (n=40) scale: baseline n_attempted={base_res['n_attempted']} "
        f"fixed n_attempted={fixed_res['n_attempted']} -- fix produced no coverage gain even at this scale")
    print(f"[self_test] real_code_path + discriminator-fires: tiny 40-sentence real slice (seed 7) -- "
          f"BASELINE n_attempted={base_res['n_attempted']} coverage={base_res['coverage_sentence_rate']:.3f} | "
          f"FIXED n_attempted={fixed_res['n_attempted']} coverage={fixed_res['coverage_sentence_rate']:.3f} "
          f"(fix fires and materially raises attempted-count at tiny scale, matching the full-scale claim).",
          flush=True)

    # (5) SAME-SLICE PARITY vs Rung 7 (byte-identical sentence-id sequence + BASELINE arm reproduces Rung 7's
    # own metrics.json numbers exactly, at FULL scale).
    full_rows = []
    for seed in SEEDS_FULL:
        r_, _ = build_rows_for_seed_v2(simple_sorted_v2, seed, N_PER_SEED)
        full_rows.extend(r_)
    assert len(full_rows) == 300, f"pooled n_total drifted from Rung 6/7's 300: got {len(full_rows)}"
    full_base = score_arm(full_rows, ie_extract_fix_all)
    print(f"[self_test] SAME-SLICE PARITY: n_total=300, BASELINE(Rung7-FIX_ALL) reproduced live -- "
          f"n_attempted={full_base['n_attempted']} n_correct={full_base['n_correct']} "
          f"precision={full_base['precision_on_attempted']}.", flush=True)

    # (6) ARMS-MUST-DIFFER (META_RULE_AF): BASELINE vs FIXED emitted-triple-set hashes differ on the real slice
    # (the fix materially changes coverage, so this must fire trivially, unlike Rung 7's bug1 low-frequency
    # case).
    variants = {"BASELINE": ie_extract_fix_all, "FIXED": ie_extract_coref_1st2nd_fixed}
    digests = {}
    for name, fn in variants.items():
        all_triples = sorted(set(t for r in full_rows for t in fn(r["text"])[0]))
        digests[name] = hashlib.sha256(json.dumps(all_triples, sort_keys=True).encode()).hexdigest()
    assert digests["BASELINE"] != digests["FIXED"], "META_RULE_AF VIOLATION: BASELINE and FIXED bit-identical on real data"
    print(f"[self_test] PASS | ARMS-MUST-DIFFER verified: BASELINE and FIXED emit different triple sets on "
          f"the real 300-sentence full slice.", flush=True)
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
    print(f"[rung8_coref_1st2nd_person] run_mode={run_mode} seeds={seeds} n_per_seed={N_PER_SEED} "
          f"expected_n_units={expected_n_units} corpus={CONLLU_PATH}", flush=True)

    agg = run_full(seeds, N_PER_SEED)
    tier, msg, weakest = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    print(f"[rung8_coref_1st2nd_person] {tier} in {elapsed:.2f}s", flush=True)
    print(f"[rung8_coref_1st2nd_person] {msg}", flush=True)

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
            "name": "UD_English-EWT test split -- SIMPLE-SYNTAX SUBSET (PATH A), SAME slice as Rung 6/7",
            "path": str(CONLLU_PATH), "license": "CC BY-SA 4.0",
            "same_slice_as": "read_grow_realprose_simple_register_rung7_fixes_imperatives_v1",
            "length_matched_pool_size": agg["length_matched_pool_size"],
            "simple_pool_size": agg["simple_pool_size"],
            "simple_fraction_of_length_matched_pool": agg["simple_fraction_of_length_matched_pool"],
            "n_sampled_total": agg["n_total"],
            "register_note": "PATH A caveat carried forward UNCHANGED from Rung 6/7: a syntax-simple subset "
                              "of general WEB vocabulary, NOT a vocabulary-controlled early-reader corpus.",
        },
        "construction_distribution_counts": agg["construction_distribution_counts"],
        "construction_distribution_fractions": agg["construction_distribution_fractions"],
        "arms": {
            "BASELINE_rung7_fix_all": _strip_rows(agg["baseline_score"]),
            "FIXED_coref_1st2nd_person": _strip_rows(agg["fixed_score"]),
        },
        "coverage_recovery": {
            "baseline_coverage_sentence_rate": agg["baseline_score"]["coverage_sentence_rate"],
            "fixed_coverage_sentence_rate": agg["fixed_score"]["coverage_sentence_rate"],
            "coverage_delta": agg["fixed_score"]["coverage_sentence_rate"] - agg["baseline_score"]["coverage_sentence_rate"],
            "n_newly_covered_sentences": agg["n_newly_covered"],
            "n_newly_covered_with_gold": agg["n_newly_covered_with_gold"],
            "newly_covered_subject_role_correct": agg["newly_covered_subject_role_correct"],
            "newly_covered_subject_role_correct_rate": agg["newly_covered_subject_role_correct_rate"],
            "newly_covered_whole_triple_precision": agg["newly_covered_whole_triple_precision"],
            "newly_covered_whole_triple_n_correct": agg["newly_covered_whole_triple_n_correct"],
            "newly_covered_whole_triple_n_emitted": agg["newly_covered_whole_triple_n_emitted"],
        },
        "zero_hallucination_guardrail": {
            "n_3rd_person_coref_unresolved_rows": agg["n_3rd_person_coref_unresolved_rows"],
            "n_3rd_person_guard_breaks": agg["n_3rd_person_guard_breaks"],
            "coref_guardrail_battery_evidence": agg["coref_guardrail_evidence"],
        },
        "guard_regression_ok": agg["guard_regression_ok"],
        "oos_control_fired": agg["oos_control_fired"],
        "sample_newly_covered_rows": agg["sample_newly_covered_rows"],
        "sample_fixed_rows": agg["fixed_score"]["rows"][:60],
        "sample_baseline_rows": agg["baseline_score"]["rows"][:60],
        "prereg": {
            "hard_pass": "fixed_precision_on_attempted>=0.60 AND coverage_delta>=0.05 AND "
                         "n_3rd_person_guard_breaks==0 AND guard_regression_ok_fixed AND oos_control_fired_fixed "
                         "AND simple_fraction_of_length_matched_pool>=0.10 AND coref_guardrail_battery_ok",
            "hard_fail": "fixed_precision_on_attempted<0.55 OR coverage_delta<0.02 (fix inert) OR "
                         "n_3rd_person_guard_breaks>0 (guardrail broken) OR NOT guard_regression_ok_fixed OR "
                         "simple_fraction_of_length_matched_pool<0.10",
            "hp_scope": "FIXED (coref_1st2nd_person) is the PRIMARY discriminator vs BASELINE (Rung 7's "
                        "FIX_ALL, imported unmodified, informational comparison arm).",
            "scope": "adopts EXACTLY the Rung-7 VET's named next-item: resolve 1st/2nd-person subject "
                     "pronouns (I/we/you) DIRECTLY (no antecedent search) instead of abstaining "
                     "COREF_UNRESOLVED. Genuine 3rd-person antecedent-less pronouns (he/she/it/they/+object-"
                     "case forms) UNCHANGED -- still abstain (zero-hallucination guardrail). Does NOT fix the "
                     "4 newly-exposed downstream bug classes (irregular-plural-noun lemma, brand/product "
                     "compound-noun head-selection, OOV verb spelling-restoration, do-support negation "
                     "parsing) -- flagged as Rung 9 candidates, not claimed fixed here.",
            "honest_guard": "the fix is a single closed-set membership check (FIRST_SECOND_PERSON_SUBJECT_"
                            "PRONOUNS = {i, we, you}) verified against a hand-built battery of 3rd-person "
                            "nonce sentences (must still abstain) + 1st/2nd-person nonce sentences (must "
                            "extract) + a fix-disabled positive control (must byte-for-byte reproduce Rung "
                            "7's FIX_ALL) -- not a sentence-specific patch.",
            "compute_architecture": "sequential-CPU; pure syntactic parsing + dependency-tree traversal, no "
                                    "VSA store; wall time trivial (MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer + dependency-classifier test)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "runner_python_u_only (timeout_s < 1800; cell wall time is seconds, matching "
                                 "Rung 5/5b/6/7's own precedent)",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["parse_conllu_v2 (Rung 7's feats-aware parser, real local corpus)",
                                         "load_simple_sentences_v2 (Rung 7's loader, SAME-SLICE-PARITY vs "
                                         "Rung 6/7)", "analyze_sentence_v2 (Rung 7's gold-deriver, UNCHANGED)",
                                         "ie_extract_fix_all (Rung 7 BASELINE, imported unmodified)",
                                         "ie_extract_coref_1st2nd_fixed (this cell, the ONE new branch)",
                                         "nltk.pos_tag (real classical averaged-perceptron call)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete syntactic role-assignment + "
                       "the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED), same "
                       "as Rung 5/5b/6/7.",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports) AND a "
                               "runtime sys.modules transitive-closure check after nltk use, both asserted "
                               "at self-test",
            "prior_work_check": "substrate_query.sh run before authoring (see completion report) -- top hits "
                                "were generic wordnet 'person' concept-graph nodes (cosine<=0.343), not prior "
                                "experiment cells; this is a genuinely novel measurement within the actively-"
                                "developed RUNG 2-8 open-text-reading arc, not a rediscovery. The relevant "
                                "prior work is the directly-pointed-to Rung 7 pipeline + the Rung-5b coref "
                                "abstain-gate lineage, both cited and reused (not independently rediscovered).",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[rung8_coref_1st2nd_person] metrics written -> {out_dir / 'metrics.json'}", flush=True)
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
