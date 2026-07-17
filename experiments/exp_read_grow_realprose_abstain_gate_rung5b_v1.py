"""exp_read_grow_realprose_abstain_gate_rung5b_v1 -- RUNG 5b: strict substrate-native ABSTAIN GATE on top of
the RUNG-5 glass-box OPEN_RELATION extractor, to fix the VET-confirmed real-prose precision collapse via
SPURIOUS FIRING (wrong triples committed instead of clean abstains) rather than via new grammar coverage.

TRIGGER (verbatim from the dispatching contract): the Rung-5 real-prose HARD_FAIL (P=0.179 on UD-English-EWT,
commit 7da8a4c8, VET ad06aaf2) was VET-confirmed a GENUINE capability wall, not a scoring artifact. The
precision-killer is SPURIOUS FIRING: the simple linear grammar emits WRONG triples (a majority of emissions
land on unhandled constructions) instead of cleanly abstaining -- localized (module docstring, RUNG-5) to
three mechanisms: (a) gerund/participial phrases misidentified as the matrix verb, (b) copular/complement-
clause sentences, (c) fragments (no finite root verb). BRAIN-CHECK (drill a0dce2e9, folded into
notes/research_classical_openie_glassbox_parsing_2026-07-17.md): the good-enough-parsing literature
(Ferreira 2003; Christianson et al. 2001; Qian/Garnsey/Christianson 2018) shows humans do NOT gracefully
abstain on unparseable constructions -- they commit to confident, plausibility-driven, often-WRONG shallow
readings (the SAME failure mode this pipeline exhibits). P600/regression/reading-time signals exist but are
read out post-hoc for repair, never wired into a pre-commit withhold-output gate. So a strict abstain gate is
NOT a brain-copy -- it is licensed as a SUBSTRATE-NATIVE precision advantage (glass-box exact-match gating a
biological system can only approximate crudely), matching the "two frontiers" doctrine
([[project_two_frontiers_brain_faithful_world_plus_substrate_native_world_later_thrust_USER_2026-07-16]]):
nail the brain-faithful baseline (RUNG 5 = "commit to a wrong answer", the honest brain-consistent floor),
THEN layer the substrate-native augmentation (this cell) the brain does not do.

THE GATE (operationalized on the SAME linear POS-tag-based grammar the Rung-5 OPEN_RELATION arm uses --
no gold-dependency access at extraction time, only the classical POS/lexicon signals the pipeline already
has). Before a triple commits, the parse must FULLY match one of the handled construction templates via TWO
strict full-slot-match checks; either failing -> ABSTAIN (emit nothing), never a partial/best-guess triple:

  GATE 1 -- FINITE-MATRIX-VERB: the chosen matrix-verb candidate (and, for relative clauses, the matrix verb
  found after the relativizer) must be a FINITE verb form (base/3sg/past/past_or_participle, or
  participle/gerund immediately preceded -- skipping adverbs -- by an AUX, i.e. genuine passive/progressive).
  A VERB-tagged token that is a bare gerund or bare participle NOT preceded by an AUX is a non-finite
  modifier (a participial/gerund PHRASE, not a finite clause) and is REJECTED as a matrix-verb candidate.
  If NO finite verb-tagged token exists in the sentence at all, ABSTAIN_NO_FINITE_VERB. This directly targets
  mechanism (a) [gerund/participial-as-matrix-verb] and mechanism (c) [fragments: the only "verb" evidence
  found is non-finite] -- MEASURED (see self_test) to fire on BOTH real Rung-5 false-positive sentences
  ("Bike ride in the park, followed by coffee." -> "followed" is a bare participle after a NOUN, not an AUX;
  "Now they are part of your working group." -> "working" is a bare gerund after "your", not an AUX).

  GATE 2 -- NO-UNHANDLED-TRAILING-FINITE-VERB: after the matched SVO/passive/relative-clause pattern's own
  token span is consumed, if ANY further finite verb-tagged token remains in the sentence (not consumed by
  the matched pattern), the sentence carries embedded/subordinate structure the linear grammar cannot
  reliably parse (canonically: a that-omitted finite complement clause, "The manager believes the plan will
  succeed" -> the naive scan grabs "plan" as the object of "believes" when it is actually the SUBJECT of the
  embedded finite clause "the plan will succeed") -> ABSTAIN_TRAILING_FINITE_VERB rather than emit the
  partial-match guess. This directly targets mechanism (b) [copular/complement clauses] for the
  finite-complement-clause sub-case -- MEASURED (see self_test) to fire on two constructed complement-clause
  sentences built from real-corpus-typical NOUN-subject + verb-of-cognition/-utterance + that-omitted clause
  patterns ("The manager believes the plan will succeed."; "The manager said the team lost the game.").
  (Plain copular sentences with NO embedded gerund/participle, e.g. "She is happy.", already abstain via the
  pre-existing NO_VERB path inherited unmodified below -- "is" tags AUX not VERB, verb_idx is empty before
  either gate even runs. Gate 1 additionally catches the copular-with-embedded-gerund sub-case, e.g. "Now
  they are part of your working group.", where a gerund inside an NP gets POS-tag-promoted to VERB.)

DECLARED RESIDUAL (NOT claimed fixed, NOT in scope per the contract's named failure-mode list): a reduced
relative clause on the SUBJECT with a FINITE embedded verb and no relativizer ("The report the manager wrote
impressed everyone.") is NOT caught by either gate -- the embedded verb ("wrote") is finite (Gate 1 does not
reject it) and precedes the wrongly-chosen matrix verb rather than trailing it (Gate 2 only looks forward).
MEASURED at self_test (this sentence still misfires under GATED, exactly as under BASELINE) and reported
honestly in the completion report as a known 4th mechanism for a future rung, not silently absorbed into this
cell's claimed coverage.

ARMS (SAME real UD-EWT slice, SAME seeds/N_PER_SEED/CaRB-style scoring as RUNG 5, for direct comparability):
  BASELINE = `ie_extract_open` (RUNG 5's OPEN_RELATION arm, imported UNMODIFIED -- re-run here, not re-cited,
    so the comparison is a live, same-process measurement, not a cross-run number pull).
  GATED = `ie_extract_open_gated`, a structural COPY of RUNG 5's `_extract_core_open` (subject-finding /
    relative-clause matrix-verb selection / passive by-agent detection / coordination splitting -- ALL
    UNCHANGED, copied not imported for the same reason RUNG 5 copied RUNG 2's `_extract_core`: the function
    is not parameterized for a swapped commit-gate and cannot be monkeypatched cleanly) with GATE 1 + GATE 2
    inserted before any triple is allowed to commit.

KEY GUARD (contract-mandated, checked explicitly, not just narrated): the gate must PRESERVE firing on
genuinely-handled constructions, not just abstain-on-everything to inflate precision. Reported metrics:
  - `true_positive_retention`: of BASELINE's own correctly-emitted triples (triples in emitted & gold, same
    sentence), what fraction does GATED still correctly emit. This is the most direct "did the gate keep the
    good extractions" measure the contract asks for.
  - `handled_class_coverage_{baseline,gated}`: attempted-sentence rate restricted to rows the GOLD classifier
    labeled a genuinely-handled non-"other_unhandled" construction class (single_clause_svo / vp_coordination
    / compound_subject / relative_clause / passive) -- the gate must not collapse this toward zero.
  - `spurious_other_unhandled_rate_{baseline,gated}`: of all ATTEMPTED (nonempty-emission) sentences, the
    fraction whose GOLD class is "other_unhandled" (no derivable gold at all) -- this is the direct measure
    of "spurious firing on unhandled constructions" the contract asks the gate to kill. HARD-PASS requires
    this to drop materially under GATED vs BASELINE.
Guard sentences (GUARD_SENTENCES, all clean finite SVO/passive with no trailing structure) and the
out-of-schema control (OUT_OF_SCHEMA_CONTROL) are re-verified against BOTH arms -- the gate must not
regress these known-good/known-abstain trivial cases.

CORPUS / METHOD: identical to RUNG 5 (`load_qualifying_sentences`, `sample_real_sentences`,
`build_rows_for_seed`, `analyze_sentence` gold-deriver, `score_arm` CaRB-style scoring, all imported
UNMODIFIED from the Rung-5 module -- this cell adds ZERO new gold-derivation or corpus-sampling logic, only
the new gated extractor). SEEDS=[7,13,19], N_PER_SEED=70 (pooled n=210), SAME real UD-EWT slice as RUNG 5
(same qualifying-pool + same seeds + same rng.sample call -> byte-identical row set, verified at self_test by
re-deriving RUNG 5's own pooled n_total=210 and its OPEN_RELATION_strict n_attempted=25/n_correct=5 numbers
live, not cited from memory).

BANDS (pre-registered BEFORE reading the FULL numbers below -- the standalone probe in the completion report
IS the finalize-numbers step, run AFTER this docstring/gate logic was fixed, per the contract's explicit
license to set thresholds "subject to the honest precision-favoring shape"; the STRUCTURE of the bands --
precision floor + non-vacuous coverage + spurious-rate-drop + retention guard -- was fixed before any FULL
number was read, matching RUNG 2/3/4/5's own committed-bands-before-measurement discipline):
  Primary discriminator = GATED arm vs BASELINE arm, on the SAME pooled real slice.
  HARD-PASS: precision_on_attempted_GATED >= 0.60 (into the classical envelope, per the contract's literal
    threshold) AND coverage_sentence_rate_GATED >= 0.01 (non-vacuous -- gate still fires on SOMETHING) AND
    spurious_other_unhandled_rate_GATED < spurious_other_unhandled_rate_BASELINE (the gate is measurably
    killing spurious firing, not just coincidentally raising precision some other way) AND
    true_positive_retention >= 0.50 (the KEY GUARD: at least half of BASELINE's own correct extractions
    survive GATED -- "keep ~all the correct single-clause-SVO extractions", deflated from a literal "all" to
    a majority given n=5 baseline true positives is a small-n regime where "all" is a single-lost-TP away
    from failing the gate on noise alone) AND guard_regression_ok_gated AND oos_control_fired_gated.
  HARD-FAIL: precision_on_attempted_GATED < 0.45 (does not materially clear BASELINE's 0.179, i.e. the gate
    did not fix the precision problem) OR coverage_sentence_rate_GATED < 0.005 (effectively fires on nothing
    -- vacuous, the abstain-on-everything failure mode the contract explicitly warns against) OR
    true_positive_retention == 0.0 (the gate killed EVERY correct extraction along with the wrong ones --
    vacuous with respect to the KEY GUARD even if coverage is nonzero on wrong sentences) OR NOT
    guard_regression_ok_gated.
  MIDDLE_BAND: otherwise (e.g. precision rises but not to 0.60, or retention is nonzero but below 0.50 --
    a real but partial win, reported honestly as partial, not rounded up to HARD-PASS).
  HONEST FRAMING (contract-mandated): a coverage DROP under GATED vs BASELINE is the EXPECTED, DESIRED shape
    (precision-favoring / recall-limited envelope) -- coverage dropping alone is never grounds for HARD-FAIL;
    only a coverage drop TO NEAR-ZERO (vacuous) or a retention collapse (killed the good extractions too) is.

COMPUTE: identical trivial-wall-time profile to RUNG 5 (pure CPU string/POS-tag processing, no torch, no VSA
store, no numpy). Executed DIRECTLY (bash) rather than via queue_add -- matching RUNG 5's own stated
precedent ("Local numpy-free ... no queue/GPU/atoms/push") for cells whose measured wall time is sub-second;
no remote dispatch needed, nothing to hand off. Storage: no_storage. Pause flag
`data/orchestrator_paused.flag` re-checked absent immediately before every run in this cell's lifecycle.
ASCII-only. No LLM, no neural component anywhere in the import closure (re-verified at self_test, both a
static source-scan of THIS file and a runtime sys.modules transitive-closure check, same method as RUNG 5).

NEXT (not this cell): the declared residual (reduced relative clause on the subject, finite embedded verb,
no relativizer) is a candidate 4th gate mechanism for a future rung if it proves to be a material fraction of
remaining spurious firing once the pooled numbers are read.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; BASELINE vs GATED emitted-triple-set hash differs on
#   the real corpus tiny slice by construction -- the gate strictly reduces the emission set).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor; discriminator is discrete syntactic gate-pass/abstain logic over
#   the same classical-tagger-driven token stream RUNG 5 already used (96-97% PTB tagger accuracy, CITED).
# - baseline_in_band: N/A BY DESIGN -- BASELINE's own known precision (0.179, MEASURED@RUNG5 metrics.json,
#   re-derived live below) is the pre-registered floor this cell exists to raise; the discriminator is
#   GATED-vs-BASELINE-on-the-same-slice, not a baseline-saturation check.
# - discriminator survives scale: corpus is FIXED-size real prose, deterministic sample, SAME regime as
#   RUNG 5 (no scale axis in this cell).
# - HARD_PASS strictly above floor; explicit bands declared above + in metrics.json prereg block.
# - real_code_path (F.1): self_test parses the REAL local corpus file (via RUNG 5's own loader, unmodified),
#   samples a tiny real slice, and runs BOTH extractors + the gold classifier against REAL sentences.
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19], inherited unmodified from RUNG 5's own
#   random.Random(seed).sample over a sorted(...) sentence-id-ordered qualifying list.
# - all numbers in comments tagged HYPOTHESIZED@prereg / MEASURED@metrics / MEASURED@RUNG5 / CITED@research-note.
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

ANCHOR_NAME = "read_grow_realprose_abstain_gate_rung5b_v1"

# --- GENUINE REUSE: RUNG 5's corpus loader / sampler / gold-deriver / scorer / OPEN tagger-builder / BASELINE
# extractor, all imported UNMODIFIED. RUNG 2/v2's `_split_coord` imported for the gated core's coordination
# logic (same function RUNG 5's own `_extract_core_open` already depends on). ---
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import (  # noqa: E402
    CONLLU_PATH, load_qualifying_sentences, sample_real_sentences, build_rows_for_seed, analyze_sentence,
    CONSTRUCTION_CLASSES, score_arm, ie_extract_open, _build_tags_open, _resolve_relation_open,
    GUARD_SENTENCES, OUT_OF_SCHEMA_CONTROL, SEEDS_FULL, N_PER_SEED,
)
from experiments.exp_read_grow_foundation_realprose_glassbox_ie_v2 import _split_coord  # noqa: E402

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only (same as RUNG 5); glass-box-legal.

# ---------------------------------------------------------------------------
# THE GATE: new code, clearly demarcated. See module docstring for the two checks + why.
# ---------------------------------------------------------------------------
_FINITE_FORMS = ("base", "3sg", "past", "past_or_participle")
_AUX_DEPENDENT_FORMS = ("participle", "gerund")


def _is_finite_form(tags, forms, i):
    """GATE 1 primitive: is the VERB-tagged token at index i a FINITE verb-form candidate. base/3sg/past/
    past_or_participle are always finite-compatible. A bare gerund or bare participle is finite-compatible
    ONLY when immediately preceded (skipping adverbs) by an AUX -- i.e. it is a genuine passive/progressive,
    not a free-standing non-finite modifier phrase. Any other form (None -- e.g. a VERB_LEX entry with no
    form info -- or an unrecognized tag) is treated as NOT confidently finite (gate refuses to guess)."""
    f = forms[i]
    if f in _FINITE_FORMS:
        return True
    if f in _AUX_DEPENDENT_FORMS:
        k = i - 1
        while k >= 0 and tags[k] == "ADV":
            k -= 1
        return k >= 0 and tags[k] == "AUX"
    return False


def _extract_core_open_gated(T):
    """structural copy of RUNG 5's `_extract_core_open` (itself a structural copy of RUNG 2's
    `_extract_core` -- subject-finding / relative-clause matrix-verb selection / passive by-agent detection /
    coordination splitting, ALL UNCHANGED), with GATE 1 (finite-matrix-verb) and GATE 2
    (no-unhandled-trailing-finite-verb) inserted. Either gate failing -> ABSTAIN (empty triple list) instead
    of committing a best-guess triple. See module docstring THE GATE section."""
    tags = [t[1] for t in T]
    lemmas = [t[2] for t in T]
    forms = [t[3] for t in T]
    n = len(T)
    all_verb_idx = [i for i in range(n) if tags[i] == "VERB"]
    if not all_verb_idx:
        return [], "NO_VERB", "no verb (closed or POS-tag-promoted)"

    # GATE 1 -- finite-matrix-verb candidates only.
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
                agent = lemmas[j]
                agent_i = j
                break
        if agent is None:
            return [], "PASSIVE_NO_AGENT_NOUN", "no agent noun after 'by'"
        consumed_end = agent_i + 1
        relation = _resolve_relation_open(verb_lemma, None)
        triples = [(agent, relation, patient) for patient in subjects]
        rule = "SVO_PASSIVE_OPEN_GATED"
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
        consumed_end = j
        relation = _resolve_relation_open(verb_lemma, prep)
        if not obj_lemmas:
            return [], "NO_OBJECT", "no object noun after verb"
        triples = [(s, relation, o) for s in subjects for o in obj_lemmas]
        rule = "SVO_COORD_OPEN_GATED" if (len(subjects) > 1 or len(obj_lemmas) > 1) else "SVO_ACTIVE_OPEN_GATED"

    # GATE 2 -- no unhandled finite verb left over after the matched pattern's own consumed span.
    trailing_finite = [i for i in all_verb_idx if i >= consumed_end and _is_finite_form(tags, forms, i)]
    if trailing_finite:
        return [], "ABSTAIN_TRAILING_FINITE_VERB", (
            f"finite verb token(s) remain unconsumed after the matched pattern (idx={trailing_finite}) -- "
            f"signals unhandled subordinate/complement-clause structure; gate refuses the partial match")

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


def ie_extract_open_gated(sentence):
    T = _build_tags_open(sentence)
    return _extract_core_open_gated(T)


# ---------------------------------------------------------------------------
# diagnostics: spurious-on-unhandled rate, handled-class coverage, true-positive retention.
# ---------------------------------------------------------------------------
def diagnose_arm(rows, extractor):
    n_attempted_other_unhandled = 0
    n_attempted_handled = 0
    n_attempted_total = 0
    per_class_attempted = {c: 0 for c in CONSTRUCTION_CLASSES}
    per_row_correct = []  # list of (row_index, frozenset(correct_triples))
    for idx, r in enumerate(rows):
        emitted = set(extractor(r["text"])[0])
        gold = set(r["gold"])
        if emitted:
            n_attempted_total += 1
            per_class_attempted[r["cls"]] += 1
            if r["cls"] == "other_unhandled":
                n_attempted_other_unhandled += 1
            else:
                n_attempted_handled += 1
        per_row_correct.append((idx, frozenset(emitted & gold)))
    spurious_rate = (n_attempted_other_unhandled / n_attempted_total) if n_attempted_total else None
    n_handled_rows = sum(1 for r in rows if r["cls"] != "other_unhandled")
    handled_class_coverage = (n_attempted_handled / n_handled_rows) if n_handled_rows else 0.0
    return {
        "n_attempted_total": n_attempted_total,
        "n_attempted_other_unhandled": n_attempted_other_unhandled,
        "n_attempted_handled": n_attempted_handled,
        "spurious_other_unhandled_rate": spurious_rate,
        "handled_class_coverage": handled_class_coverage,
        "per_class_attempted": per_class_attempted,
        "per_row_correct": per_row_correct,
    }


def true_positive_retention(rows, baseline_extractor, gated_extractor):
    base_diag = diagnose_arm(rows, baseline_extractor)
    gated_diag = diagnose_arm(rows, gated_extractor)
    base_correct = {idx: s for idx, s in base_diag["per_row_correct"] if s}
    gated_correct = {idx: s for idx, s in gated_diag["per_row_correct"] if s}
    n_base_tp = sum(len(s) for s in base_correct.values())
    n_retained = 0
    for idx, base_set in base_correct.items():
        gated_set = gated_correct.get(idx, frozenset())
        n_retained += len(base_set & gated_set)
    retention = (n_retained / n_base_tp) if n_base_tp else None
    return {"n_baseline_true_positives": n_base_tp, "n_retained": n_retained, "retention": retention}


# ---------------------------------------------------------------------------
# glass-box-legal checks (same method as RUNG 5).
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
    qualifying_sorted = load_qualifying_sentences(CONLLU_PATH)
    all_rows = []
    dist_pooled = {c: 0 for c in CONSTRUCTION_CLASSES}
    for seed in seeds:
        rows, dist = build_rows_for_seed(qualifying_sorted, seed, n_per_seed)
        all_rows.extend(rows)
        for c in CONSTRUCTION_CLASSES:
            dist_pooled[c] += dist[c]

    n_total = len(all_rows)

    baseline_score = score_arm(all_rows, ie_extract_open, relax=False)
    gated_score = score_arm(all_rows, ie_extract_open_gated, relax=False)
    baseline_diag = diagnose_arm(all_rows, ie_extract_open)
    gated_diag = diagnose_arm(all_rows, ie_extract_open_gated)
    tp_retention = true_positive_retention(all_rows, ie_extract_open, ie_extract_open_gated)

    guard_ok_baseline = all(set(ie_extract_open(s)[0]) == set(g) for (s, g) in GUARD_SENTENCES)
    guard_ok_gated = all(set(ie_extract_open_gated(s)[0]) == set(g) for (s, g) in GUARD_SENTENCES)
    oos_baseline = all(not ie_extract_open(s)[0] for s in OUT_OF_SCHEMA_CONTROL)
    oos_gated = all(not ie_extract_open_gated(s)[0] for s in OUT_OF_SCHEMA_CONTROL)

    return {
        "seeds": seeds, "n_per_seed": n_per_seed, "n_total_sentences": n_total,
        "qualifying_pool_size": len(qualifying_sorted),
        "construction_distribution_counts": dist_pooled,
        "construction_distribution_fractions": {c: (dist_pooled[c] / n_total if n_total else 0.0)
                                                 for c in CONSTRUCTION_CLASSES},
        "baseline_score": baseline_score, "gated_score": gated_score,
        "baseline_diag": baseline_diag, "gated_diag": gated_diag,
        "true_positive_retention": tp_retention,
        "guard_regression_ok_baseline": guard_ok_baseline, "guard_regression_ok_gated": guard_ok_gated,
        "oos_control_fired_baseline": oos_baseline, "oos_control_fired_gated": oos_gated,
        "all_rows": all_rows,
    }


def compute_verdict(agg):
    prec_g = agg["gated_score"]["precision_on_attempted"]
    prec_b = agg["baseline_score"]["precision_on_attempted"]
    cov_g = agg["gated_score"]["coverage_sentence_rate"]
    spur_g = agg["gated_diag"]["spurious_other_unhandled_rate"]
    spur_b = agg["baseline_diag"]["spurious_other_unhandled_rate"]
    retention = agg["true_positive_retention"]["retention"]
    guard_ok = agg["guard_regression_ok_gated"]
    oos_ok = agg["oos_control_fired_gated"]

    if prec_g is None:
        return ("HARD_FAIL", "GATED arm emitted zero triples on the whole real-prose sample -- "
                              "vacuous abstain-on-everything (KEY GUARD violated)", "gated_emitted_nothing")

    spurious_dropped = (spur_g is not None and spur_b is not None and spur_g < spur_b) or (spur_g == 0.0)
    retention_ok_for_pass = (retention is not None and retention >= 0.50)
    retention_vacuous = (retention is None) or (retention == 0.0)

    hard_pass = (prec_g >= 0.60 and cov_g >= 0.01 and spurious_dropped and retention_ok_for_pass
                 and guard_ok and oos_ok)
    hard_fail = (prec_g < 0.45 or cov_g < 0.005 or retention_vacuous or (not guard_ok))

    if hard_pass:
        tier = "HARD_PASS"
    elif hard_fail:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    weakest = "n/a"
    if not hard_pass:
        if prec_g < 0.60:
            weakest = "gated_precision_on_attempted_below_0.60"
        elif cov_g < 0.01:
            weakest = "gated_coverage_near_vacuous"
        elif not spurious_dropped:
            weakest = "spurious_other_unhandled_rate_did_not_drop"
        elif not retention_ok_for_pass:
            weakest = "true_positive_retention_below_0.50_key_guard"
        elif not guard_ok:
            weakest = "guard_regression_failed_gated"
        elif not oos_ok:
            weakest = "oos_control_did_not_fire_gated"

    msg = (f"{tier} | BASELINE precision_on_attempted={prec_b:.3f} coverage={agg['baseline_score']['coverage_sentence_rate']:.3f} "
           f"spurious_other_unhandled_rate={spur_b if spur_b is not None else 'n/a'} | "
           f"GATED precision_on_attempted={prec_g:.3f} (HP>=0.60,HF<0.45) coverage={cov_g:.3f} (HP>=0.01,HF<0.005) "
           f"spurious_other_unhandled_rate={spur_g if spur_g is not None else 'n/a'} "
           f"true_positive_retention={retention if retention is not None else 'n/a'} (HP>=0.50,HF==0) "
           f"handled_class_coverage_baseline={agg['baseline_diag']['handled_class_coverage']:.3f} "
           f"handled_class_coverage_gated={agg['gated_diag']['handled_class_coverage']:.3f} | "
           f"guard_regression_ok_gated={guard_ok} oos_control_fired_gated={oos_ok} | weakest={weakest}")
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
# self-test: EXERCISE THE REAL code path (real corpus file, real nltk.pos_tag, real gate logic).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (real CoNLL-U parse of the local corpus file, real "
          "nltk.pos_tag calls, real gate + both extraction arms)...", flush=True)

    # (0) glass-box-legal: static source-scan + RUNTIME transitive sys.modules check.
    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"
    _ = nltk.pos_tag(["The", "cat", "sat", "."])
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print(f"[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural)", flush=True)

    # (1) GATE 1 fires on the two REAL Rung-5 false-positive sentences (MEASURED@rung5-sample_open_rows,
    # re-derived live here, not cited from memory): gerund/participial-as-matrix-verb + fragment.
    s1 = "Bike ride in the park, followed by coffee."
    base1 = ie_extract_open(s1)
    gate1 = ie_extract_open_gated(s1)
    assert base1[0] == [("park", "follow_by", "coffee")], f"BASELINE behavior on s1 drifted: {base1}"
    assert gate1[0] == [] and gate1[1] == "ABSTAIN_NO_FINITE_VERB", f"GATE 1 did not abstain on s1: {gate1}"
    s2 = "Now they are part of your working group."
    base2 = ie_extract_open(s2)
    gate2 = ie_extract_open_gated(s2)
    assert base2[0] == [("part", "work", "group")], f"BASELINE behavior on s2 drifted: {base2}"
    assert gate2[0] == [] and gate2[1] == "ABSTAIN_NO_FINITE_VERB", f"GATE 1 did not abstain on s2: {gate2}"
    print(f"[self_test] GATE 1 (finite-matrix-verb) verified on 2 REAL Rung-5 false-positive sentences: "
          f"BASELINE wrongly emitted {base1[0]} and {base2[0]}; GATED correctly abstains on both.", flush=True)

    # (2) GATE 2 fires on constructed that-omitted complement-clause sentences (verified BASELINE misfires
    # first, matching the real "manager believes/said" mechanism-(b) pattern from the corpus register).
    s3 = "The manager believes the plan will succeed."
    base3 = ie_extract_open(s3)
    gate3 = ie_extract_open_gated(s3)
    assert base3[0] == [("manager", "believe", "plan")], f"BASELINE behavior on s3 drifted: {base3}"
    assert gate3[0] == [] and gate3[1] == "ABSTAIN_TRAILING_FINITE_VERB", f"GATE 2 did not abstain on s3: {gate3}"
    s4 = "The manager said the team lost the game."
    base4 = ie_extract_open(s4)
    gate4 = ie_extract_open_gated(s4)
    assert base4[0] == [("manager", "said", "team")], f"BASELINE behavior on s4 drifted: {base4}"
    assert gate4[0] == [] and gate4[1] == "ABSTAIN_TRAILING_FINITE_VERB", f"GATE 2 did not abstain on s4: {gate4}"
    print(f"[self_test] GATE 2 (no-trailing-finite-verb) verified on 2 constructed complement-clause "
          f"sentences: BASELINE wrongly emitted {base3[0]} and {base4[0]}; GATED correctly abstains on both.",
          flush=True)

    # (3) KEY GUARD: gate PRESERVES firing on genuinely-handled constructions (guard sentences + self-test's
    # own novel-verb sentence from Rung-5).
    for sent, gold in GUARD_SENTENCES:
        gset = set(gold)
        assert set(ie_extract_open(sent)[0]) == gset, f"BASELINE guard regression on {sent!r}"
        assert set(ie_extract_open_gated(sent)[0]) == gset, f"GATED guard regression on {sent!r} -- KEY GUARD VIOLATED"
    s5 = "The boy walked the dog to the store."
    assert set(ie_extract_open_gated(s5)[0]) == {("boy", "walk", "dog")}, (
        f"GATED failed on a genuinely-handled novel-verb sentence: {ie_extract_open_gated(s5)}")
    for s in OUT_OF_SCHEMA_CONTROL:
        assert ie_extract_open(s)[0] == [], f"BASELINE unexpectedly extracted on OOS control {s!r}"
        assert ie_extract_open_gated(s)[0] == [], f"GATED unexpectedly extracted on OOS control {s!r}"
    print("[self_test] KEY GUARD: GATED preserves ALL 4 guard-sentence extractions + the novel-verb "
          "self-test sentence + both OOS abstains -- gate is not vacuous-on-everything.", flush=True)

    # (4) declared residual (NOT fixed here, verified to still misfire honestly -- not silently absorbed).
    s6 = "The report the manager wrote impressed everyone."
    gate6 = ie_extract_open_gated(s6)
    assert gate6[0] != [], (f"declared residual (reduced-relative-on-subject) unexpectedly now abstains -- "
                             f"either a real incidental fix (re-verify + update docstring) or a gate bug: {gate6}")
    print(f"[self_test] declared residual reproduced honestly: GATED still misfires on the reduced-relative-"
          f"on-subject case ({gate6[0]}) -- NOT claimed fixed by this cell, see module docstring.", flush=True)

    # (5) real_code_path (F.1): parse the REAL local corpus file, sample a tiny REAL slice, run both arms.
    qualifying_sorted = load_qualifying_sentences(CONLLU_PATH)
    assert len(qualifying_sorted) > 100, f"expected a real, sizeable qualifying pool, got {len(qualifying_sorted)}"
    rows, dist = build_rows_for_seed(qualifying_sorted, seed=7, n_per_seed=40)
    assert sum(dist.values()) == 40, f"distribution counts do not sum to sample size: {dist}"
    base_res = score_arm(rows, ie_extract_open)
    gated_res = score_arm(rows, ie_extract_open_gated)
    print(f"[self_test] real_code_path: REAL corpus ({len(qualifying_sorted)} qualifying sentences), tiny "
          f"40-sentence real slice -- BASELINE coverage={base_res['coverage_sentence_rate']:.3f} precision="
          f"{base_res['precision_on_attempted']} | GATED coverage={gated_res['coverage_sentence_rate']:.3f} "
          f"precision={gated_res['precision_on_attempted']}", flush=True)

    # (6) SAME-SLICE PARITY (this cell's own discipline, extends F.1): re-derive Rung 5's own pooled n_total
    # and BASELINE n_attempted/n_correct at FULL seeds/N_PER_SEED, byte-for-byte, proving this cell samples
    # the IDENTICAL real slice Rung 5 measured (MEASURED@rung5 metrics.json: n_total=210, n_attempted=25,
    # n_correct=5) -- not a re-derivation that silently drifted.
    full_rows = []
    for seed in SEEDS_FULL:
        r, _ = build_rows_for_seed(qualifying_sorted, seed, N_PER_SEED)
        full_rows.extend(r)
    assert len(full_rows) == 210, f"pooled n_total drifted from Rung 5's 210: got {len(full_rows)}"
    full_base = score_arm(full_rows, ie_extract_open)
    assert full_base["n_attempted"] == 25, f"BASELINE n_attempted drifted from Rung 5's 25: got {full_base['n_attempted']}"
    assert full_base["n_correct"] == 5, f"BASELINE n_correct drifted from Rung 5's 5: got {full_base['n_correct']}"
    print(f"[self_test] SAME-SLICE PARITY confirmed: n_total=210 n_attempted=25 n_correct=5, byte-identical "
          f"to Rung 5's own landed metrics.json (commit 7da8a4c8) -- this cell measures the SAME real slice.",
          flush=True)

    # (7) ARMS-MUST-DIFFER (META_RULE_AF): BASELINE vs GATED emitted-triple-set hash on the real tiny slice.
    base_all = sorted(set(t for r in rows for t in ie_extract_open(r["text"])[0]))
    gated_all = sorted(set(t for r in rows for t in ie_extract_open_gated(r["text"])[0]))
    h_base = hashlib.sha256(json.dumps(base_all, sort_keys=True).encode()).hexdigest()
    h_gated = hashlib.sha256(json.dumps(gated_all, sort_keys=True).encode()).hexdigest()
    assert h_base != h_gated, "META_RULE_AF VIOLATION: BASELINE and GATED bit-identical on real data"
    print(f"[self_test] PASS | ARMS-MUST-DIFFER verified (BASELINE emitted {len(base_all)} unique triples, "
          f"GATED emitted {len(gated_all)}, on the real 40-sentence tiny slice)", flush=True)
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
    print(f"[abstain_gate_rung5b] run_mode={run_mode} seeds={seeds} n_per_seed={N_PER_SEED} "
          f"expected_n_units={expected_n_units} corpus={CONLLU_PATH}", flush=True)

    agg = run_full(seeds, N_PER_SEED)
    tier, msg, weakest = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    print(f"[abstain_gate_rung5b] {tier} in {elapsed:.2f}s", flush=True)
    print(f"[abstain_gate_rung5b] {msg}", flush=True)

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
            "name": "UD_English-EWT test split", "path": str(CONLLU_PATH), "license": "CC BY-SA 4.0",
            "same_slice_as": "read_grow_realprose_ud_ewt_rung5_v1 (commit 7da8a4c8, VET ad06aaf2)",
        },
        "construction_distribution_counts": agg["construction_distribution_counts"],
        "construction_distribution_fractions": agg["construction_distribution_fractions"],
        "arms": {
            "BASELINE_OPEN_RELATION": {k: v for k, v in agg["baseline_score"].items() if k != "rows"},
            "GATED_OPEN_RELATION": {k: v for k, v in agg["gated_score"].items() if k != "rows"},
        },
        "diagnostics": {
            "baseline": {k: v for k, v in agg["baseline_diag"].items() if k != "per_row_correct"},
            "gated": {k: v for k, v in agg["gated_diag"].items() if k != "per_row_correct"},
            "true_positive_retention": agg["true_positive_retention"],
        },
        "guard_regression_ok_baseline": agg["guard_regression_ok_baseline"],
        "guard_regression_ok_gated": agg["guard_regression_ok_gated"],
        "oos_control_fired_baseline": agg["oos_control_fired_baseline"],
        "oos_control_fired_gated": agg["oos_control_fired_gated"],
        "sample_baseline_rows": agg["baseline_score"]["rows"][:60],
        "sample_gated_rows": agg["gated_score"]["rows"][:60],
        "prereg": {
            "hard_pass": "gated_precision_on_attempted>=0.60 AND gated_coverage_sentence_rate>=0.01 AND "
                         "spurious_other_unhandled_rate DROPS (gated<baseline OR gated==0) AND "
                         "true_positive_retention>=0.50 AND guard_regression_ok_gated AND oos_control_fired_gated",
            "hard_fail": "gated_precision_on_attempted<0.45 OR gated_coverage_sentence_rate<0.005 OR "
                         "true_positive_retention==0.0 (or undefined -- no baseline TPs survive) OR "
                         "NOT guard_regression_ok_gated",
            "hp_scope": "GATED arm is the primary discriminator, measured against BASELINE (Rung-5's own "
                        "OPEN_RELATION arm, re-run live on the identical slice) on the SAME pooled real "
                        "UD-EWT sample. true_positive_retention is the KEY GUARD metric (contract-mandated: "
                        "the gate must not just abstain-on-everything).",
            "gate_mechanisms": "GATE 1 finite-matrix-verb (targets gerund/participial-as-matrix-verb + "
                                "fragments); GATE 2 no-unhandled-trailing-finite-verb (targets "
                                "that-omitted finite complement clauses). Declared residual: reduced "
                                "relative clause on the subject with a finite embedded verb and no "
                                "relativizer is NOT caught by either gate (verified still misfires at "
                                "self_test, not silently absorbed).",
            "compute_architecture": "sequential-CPU; pure syntactic parsing + gate logic, no VSA store; "
                                    "wall time trivial (MEASURED below)",
            "storage_strategy": "no_storage (pure parser-layer + gate-logic test)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "runner_python_u_only (timeout_s < 1800; not mandatory, cell wall time is "
                                 "seconds, matching Rung 5's own precedent)",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["load_qualifying_sentences (real local corpus file, imported from "
                                         "Rung 5 unmodified)", "analyze_sentence (Rung 5's gold-deriver, "
                                         "imported unmodified)", "ie_extract_open (Rung 5's BASELINE, "
                                         "imported unmodified, re-run live)", "ie_extract_open_gated (NEW "
                                         "gate logic, this cell)", "nltk.pos_tag (real classical "
                                         "averaged-perceptron call)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete gate-pass/abstain logic over "
                       "the same classical-tagger-driven token stream.",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports) AND a "
                               "runtime sys.modules transitive-closure check after nltk use, both asserted "
                               "at self-test",
            "prior_work_check": "substrate_query.sh run before authoring (see completion report); this is "
                                "an ABSTAIN-GATE extension of the RUNG 5 arc, VET-triggered and drill-"
                                "brain-checked (notes/research_classical_openie_glassbox_parsing_2026-07-17.md), "
                                "not a rediscovery.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[abstain_gate_rung5b] metrics written -> {out_dir / 'metrics.json'}", flush=True)
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
