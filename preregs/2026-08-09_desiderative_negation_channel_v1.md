# Pre-registration: exp_desiderative_negation_channel_v1 (2026-08-09)

## Task / motivation

`exp_outcome_event_extraction_recovery_v1` (HARD_FAIL, commit f1250c1a2) cleanly falsified
referent-linkage EXTRACTION for the 37-item gold-Unfulfilled residual of the abstain-to-majority
cohort (`goal_achievement_verdict(desire, outcome, use_union_oov=False)["channel"] == "majority"`,
900-row ENLARGED draw, ENLARGED_SEED=20260809, byte-identical construction to
`exp_direction_b_M2_speechact_result_generalization_v1`/`exp_outcome_event_extraction_recovery_v1`).
Director's own VET of that residual (reading the actual 37 items) found it is NOT uniformly
deep-inference: ~9 items are recoverable via a DISCOURSE-LEVEL negation/substitution of the
desiderative that neither Channel-A (`relation_channel`: only fires when the GOAL VERB ITSELF
recurs+negates) nor the WIRED union channel (M2 resulttype / fork-A relation+`mwe_disengage_scan` /
M1 idiom -- Director-MEASURED 0/37 on this exact residual on disk) catch. This cell builds +
tests a new, complementary channel (`hdlab.goal_achievement.desiderative_negation_channel`) targeting
that slice.

Reference items (idxs into the 900-row ENLARGED sample, gold=Unfulfilled, USED FOR TAXONOMY DESIGN
ONLY, never for tuning thresholds -- see "Anti-circularity" below): 210, 506, 526, 333, 378, 650,
353, 868 (Director's 8 high-confidence items) + marginally 116/107.

## Mechanism summary

5 constructions, ALL requiring genuine cross-text goal-conditioning (not a bare outcome-only scan --
see `hdlab/goal_achievement.py`'s module comment above `desiderative_negation_channel` for the full
mathematical argument for why this is mandatory for pairscramble to be able to collapse at all):

1. `reply_negation` -- bare "no/nope/nah" discourse-reply particle, gated on `_goal_linked`
   (shared-entity words OR the desire being phrased as an embedded yes/no REQUEST_FRAME OR an
   ABANDON_GOAL predicate).
2. `modal_negation` -- an anaphoric subject (it/that/this/there) + a negator (reuses
   `hdlab.goal_typing._is_negator`/`_verb_negated_before`) + a closed-class modal-possibility
   predicate ("not an option" / "not going to happen"), same `_goal_linked` gate.
3. `negated_existence_object` / `negated_availability_object` / `negated_result_attribute` -- the
   goal's own shared-entity word (content-word overlap between desire and outcome text, len>=4,
   goal-verb-synonyms excluded) recurs inside a negated-existence ("no X for me"), negated-
   availability ("X was sold out"), or negated-result-attribute ("X didn't fit", reusing
   `_verb_negated_before`) frame.
4. `companion_substitution` -- the desire structurally names a companion argument ("with them/him/
   her/us/me"); the outcome negates it via a closed solitude-marker list ("ended up going alone").
5. `divergence_marker` -- a discourse substitution marker ("ended up"/"in the end"/"instead") +
   generic divergence phrase ("a different X"/"another X"/"alone"/"elsewhere"), `_goal_linked` gated.

Always votes Unfulfilled (never Fulfilled) or abstains. Wired as an OPT-IN abstain-cohort fallback
(`use_desiderative_negation`, default `_DESID_NEG_DEFAULT=False`) -- byte-identical to the certified
base pipeline when off (no new trace fields, verdict/channel unchanged). Wire-or-shelve is the
Director's call at land.

## Anti-circularity (locked)

Development + self-test (`hdlab.goal_achievement.self_test_desiderative_negation_channel`) happens
on 7 hand-authored TRAIN exemplars with DIFFERENT surface phrasing than the real DesireDB reference
items (different entities, different verbs, different exact wording for every construction). The
reference items above informed the TAXONOMY (which construction *classes* exist -- first-person
reply / modal negation / object negation / substitution, exactly the classes the task handed me as
"reference examples ONLY") but no regex/threshold/word-list entry was chosen by checking whether it
makes a specific reference item pass. The true recovery number is measured, once, against the FULL
900-row ENLARGED gold-Unfulfilled cohort (n~37, unknown to me beyond the 8-10 flagged idxs) --
reported honestly including any additional items caught or missed beyond the reference set.

(Disclosure: an informal, non-committing sanity check run against the 10 reference items' exact text
during authoring found 8/10 recovered -- this number is HYPOTHESIZED-grade, informal, run AFTER the
mechanism was already fixed, and is NOT the pre-registered gate; the gates below are set with headroom
below that check specifically so the official FULL run is not rubber-stamping the same computation.)

## Compute architecture

Sequential-CPU, no GPU. Pure Python regex/tokenization + WordNet lookups (cached), operating on a
900-row DesireDB draw + n=160/n=80 balanced full-bench draws. No matmul, no batching opportunity, no
composition/chaining. Storage: no_storage (stateless per-item classification). Estimated wall time:
low tens-of-seconds to a few minutes (this channel does not invoke the heavier UD arc-parser/
CandidateGenerator the extraction-recovery cell used -- the extraction cell's own 592s FULL runtime
was dominated by that parser + the same 900-row cohort-build step this cell also pays once).

## Pre-registered bands (fixed before FULL; my own thresholds per task's explicit autonomy grant)

Denominator for all recovery bands: `enlarged_gold_unfulfilled_n` (~37, measured at run time, not
assumed).

- `MIN_GOLD_UNFULFILLED_ENLARGED = 15` -- underpowered-cohort sanity floor (same as the sibling
  extraction-recovery cell).

**HP1 (recovery floor):** `recovery_real.rate >= 0.15` AND `recovery_real.n_recovered >= 5`.
Calibrated well below the informal 8/10-recovered-on-the-flagged-set check (~0.22 rate on n=37 if
none of those 8 are lost and no false items are gained) -- "a meaningful share of the ~9", not a
rubber-stamp of the informal check.

**HP2 (pairscramble collapses cleanly):** `recovery_pairscramble.rate <= 0.10` AND
`(recovery_real.rate - recovery_pairscramble.rate) >= 0.10`.

**HP3 (beats fresh base, full n=160 bench):** `full_bench_160.macro_f1_on >= full_bench_160.macro_f1_off`
(the SAME run's freshly-measured base, `use_desiderative_negation=False`) -- strict, not a rubber-
stamp of the previously-documented 0.686/0.6623 numbers (those are cited as secondary context only).

**HP4 (beats the RULE floor):** `full_bench_160.macro_f1_on >= 0.620` (RULE_MACRO_F1_FLOOR, cited
from `hdlab/goal_achievement.py`'s own module docstring).

**HP5 (arms differ):** REAL and PAIRSCRAMBLE predictions differ (META_RULE_AF hash check) over the
cohort.

HARD_PASS requires HP1-HP5 all true and no HARD_FAIL reason below.

**HF1 (mechanism inert):** `recovery_real.n_recovered == 0` (fires nowhere, or fires but always
wrong).

**HF2 (pairscramble fails to collapse):** `recovery_pairscramble.rate >= recovery_real.rate - 0.05`.

**HF3 (net-negative full-bench -- LOCKED, task-mandated):** `full_bench_160.macro_f1_on <
full_bench_160.macro_f1_off` (ANY regression vs the same run's fresh base measurement is a HARD_FAIL,
per the task's explicit "NET-NEGATIVE full-bench = HARD-FAIL" mandate -- no tolerance epsilon).

**HF4 (underpowered cohort):** `enlarged_gold_unfulfilled_n < MIN_GOLD_UNFULFILLED_ENLARGED`.

**HF5 (false-positive regression on the full abstain cohort, not just the Unfulfilled subset):**
`full_cohort_accuracy_on < full_cohort_accuracy_majority_baseline - 0.05` -- catches the channel
flipping gold-Fulfilled cohort items wrong (VET the positive as hard as the negative).

Otherwise: MIDDLE_BAND (fires + doesn't false-positive-regress + doesn't literally net-negative the
full bench, but misses one of the HP floors -- e.g. pairscramble collapses less cleanly than HP2, or
recovery is real but below the 0.15/n=5 floor).

## Reporting requirements (task-mandated, all present in metrics.json)

- Per-item glass-box diagnosis table over the full enlarged gold-Unfulfilled cohort: gold, pred
  (REAL arm), fired constructions, shared_entity_words -- for EVERY item, not only recovered ones.
- `harness_validity_check` (n=80 reproduction of the documented base macro-F1, `use_union_oov=False,
  use_desiderative_negation=False`) as a harness-sanity gate (not a HARD_PASS/HARD_FAIL band, mirrors
  the sibling cell's own convention).
- Full-bench n=160 AND n=80 macro-F1/accuracy, ON vs OFF, reported both.

## Cell-template mandates checklist

- `arms_differ_verified`: HP5 above (hash-compare REAL vs PAIRSCRAMBLE predictions).
- `final_metrics_atomicity`: tmp_replace (`os.replace`).
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`).
- `crlb_n/a`: glass-box lexical/regex/WordNet pipeline, no swept capacity regime, no decoded/noisy
  continuous signal.
- `cardinality_ok`: `EXPECTED_N_UNITS` declared per run_mode; cell is resumable per-unit via
  `tools/exp_checkpoint.py` (reused, same convention as the sibling extraction-recovery cell).
- `calibration_check`: n/a -- no adaptive threshold; every regex/word-list/window-size constant is a
  pre-registered, fixed design choice (see mechanism summary), not fit post-hoc to this cell's own
  eval data.
- `deterministic_seeding`: true (fixed SEED/ENLARGED_SEED, `sorted(set())`-safe draws, reused verbatim
  from the sibling cells).
- `progress_logging`: print_flush_true (FULL run has no single unit >30min, but printed per-phase for
  auditability; not required by the >=1800s MANDATORY threshold at this cell's expected runtime, done
  anyway for consistency with sibling cells).
- self-test constructs the REAL `goal_achievement_verdict`/`desiderative_negation_channel` objects at
  small scale (real_code_path); no synthetic-only branch; no DesireDB/network needed for `--self-test`.

## Smoke gate (before FULL)

`--smoke`: n=80 (VALIDITY_N_PER_CLASS) balanced draw, same cohort-construction + REAL/PAIRSCRAMBLE
arms, no HARD-PASS/HARD-FAIL claim (DISCRIMINATOR-MUST-SURVIVE-SCALE pre-flight) -- confirms the
mechanism actually fires (extraction_fire_rate/construction-fire-rate > 0) and arms differ before
committing to the heavier 900-row ENLARGED FULL run.
