# Pre-registration: appraisal_structure_extraction_v1

Date: 2026-08-03
Author: exp_dev
Parent cell: `exp_grounded_appraisal_transfer_to_text_v1` (verdict EXTRACTION_BOTTLENECK, landed
2026-08-03T23:36Z). Diagnoses and fixes ONE bounded slice of arm_b's extraction bottleneck on
the `multi_candidate_causal_attribution` items (n=4) of
`data/eval_gold_mention_role_mcguffey_v1/gold_grounded_appraisal_richer_v1.jsonl`.

## Diagnosis (done BEFORE writing the fix, re-derived from `data/exp_grounded_appraisal_transfer_to_text_v1/metrics.json`,
not trusted from the prior thread's claim)

Re-reading the per-seed `causal_rows` in the parent cell's metrics.json: extraction differentiation
(`arm_b_extraction_differentiated`) is TRUE only for `grapp_mcca_005`, across all 5 seeds -> 5/20,
confirming the "5 of 20" figure. Root cause per item (valence comes from
`resolve_valence_blind(span_text)`, a fixed exact-token HARM_WORDS/HELP_WORDS lookup table in
`exp_situated_goal_structure_valence_v1.py`, applied directly to the true/distractor span text):

- `grapp_mcca_001`: true_span "the half-breed saw his chance and drove the knife to the hilt..." and
  distr_span "Muff Potter'll hang for this if they catch him!" -- ZERO tokens in either span match
  HARM_WORDS/HELP_WORDS at all. Genuine lexicon-coverage gap (MISSING-FACT), no violent-verb coverage
  ("drove...knife", "hang").
- `grapp_mcca_003`: true_span "...been punished quite enough." contains "punished", an inflected form
  of the already-present lexicon entry "punish". Exact-string match fails on this inflection -> NA.
  This is USED-ABILITY-WRONG: the fact ("punish"=HARM) already exists in the table, it is only not
  reachable because token matching does not normalize morphology.
- `grapp_mcca_004`: true_span "...let her take care of herself" tokenizes to include "care", literally
  present in HELP_WORDS -> classified HELP. This is the withheld-warning/spite item (same span reused
  as `grapp_irony_001`): the true valence is negative-by-omission, invisible to a positive-surface-word
  lookup. MISSING-PRIMITIVE (irony/negation/omission-aware valence) -- large, explicitly OUT OF SCOPE
  this cycle (see "Not fixed" below).
- `grapp_mcca_005`: distr_span "He took a good scolding about clodding Sid..." contains "scolding" (in
  HARM_WORDS) describing an EARLIER, UNRELATED offense (Tom being scolded for something else), not the
  sugar-bowl-breaking action itself; true_span "Sid's fingers slipped and the bowl dropped and broke"
  is an ACCIDENT with no harm-intent lexicon coverage. The lexicon fires on an incidental nearby word
  regardless of whether it describes the causally relevant action. Scope/salience issue, not a
  vocabulary gap -- OUT OF SCOPE this cycle (would need clause-level action-verb targeting, a larger
  build).

Flavor tally across the 4 items (transfer cell's own diagnosis, re-derived): (a) USED-ABILITY-WRONG =
1 (mcca_003, morphology not normalized before an existing lexicon lookup); (b) MISSING-PRIMITIVE = 2
(mcca_004 omission/irony-valence; mcca_005 clause-scoped action targeting), both correctly judged too
large to build this cycle, reported not forced; (c) MISSING-FACT (bare lexicon-coverage gap, no
morphology issue) = 1 (mcca_001).

## The ONE fix (bounded, in-scope this cycle)

Add a light, general, deterministic suffix-stripping stem BEFORE lexicon lookup, applied identically
to the HARM_WORDS/HELP_WORDS lexicon entries and to input tokens (never hand-adding inflected forms
per-item -- that would be item-specific overfitting; the stem function is content-blind and applies to
any word). Suffixes stripped (only if resulting stem length >= 3): `ingly, edly, edness, ing, ed, es, s`.

Brain-structure framing: this is lemma-based lexical access -- affix-stripping to reach a shared root
lexical entry is a standard property of the mental lexicon / lexical-semantic store (left temporal
lobe), not a new appraisal mechanism. It is a WIRING fix (USED-ABILITY-WRONG): the HARM/HELP fact
table already exists (`sgv.HARM_WORDS` / `sgv.HELP_WORDS`, reused verbatim, unedited), it was simply
unreachable from inflected tokens. No new fact is invented, no external stemmer/lemmatizer/NLP library
is imported (glass-box).

## Hypothesis

Applying stemmed lookup should flip `grapp_mcca_003`'s extraction from non-differentiated (NA,NA) to
differentiated-and-correct (HARM,NA) deterministically across all seeds, since "punished" stems to
"punish" (already HARM) and no HELP-lexicon term appears in either span. `grapp_mcca_001`,
`grapp_mcca_004`, `grapp_mcca_005` are predicted UNCHANGED by this fix (their tokens do not stem-match
the lexicon either way) -- this is stated in advance so a null result on those 3 items is not spun as
"the fix generalized," and a change on them would flag an unexpected side effect worth investigating.

Predicted numbers (computed by hand from the stemmed lexicon against the 4 spans, to be checked against
measured output): differentiation rate 5/20 -> 10/20 (mcca_003 goes from 0/5 to 5/5 differentiated).
Causal arm_b accuracy 0.45 -> ~0.50 (mcca_003 goes from 4/5-by-luck to 5/5-deterministic; net effect
across the 20 seed x item cells is small because the other 3 items already often "worked by luck" on
non-differentiated coin-flip outcomes). This is NOT expected to flip the overall EXTRACTION_BOTTLENECK
verdict (0.50 does not exceed the CHANCE=0.5 threshold with strict `>`), and that is reported honestly,
not spun.

## Negative control (must fail, proves the differentiation metric is sensitive)

`RANDOM_DEGENERATE` extraction: valence assigned via a `torch.Generator` seeded per (item, seed) draw
over {HARM, HELP, NA}, completely ignoring span content. This MUST NOT show accuracy or differentiation
that tracks correctness above chance -- if the degenerate control passed the causal_arm_b_beats_all
gate, the metric itself would be broken (not a real signal).

## Anti-overfit check (broader gold, honesty gate)

The task brief pointed at a broader ~165-item mention-role/entity-track gold set in
`data/eval_gold_mention_role_mcguffey_v1/`. That directory was searched exhaustively (`wc -l` over
every `.jsonl`, 843 lines total across 29 files, largest single file 208 lines
`gold_causal_relations_v1.jsonl`); no ~165-item file exists, and none of the mention-role/entity-track
files (`candidates.jsonl`, `gold_multiclause_*`, `gold_quotative_*`, `gold_passive_*`, etc.) carry
HARM/HELP valence ground truth -- they gold-label coreference/mention-role, a different task, not
inputs the `resolve_valence_blind` mechanism under test consumes. Using them would not test this fix at
all. Substituting the closest existing broader eval that DOES exercise the exact same mechanism:
`gold_relation_inference_v1.jsonl` (25 items total across 3 DISJOINT item_type schemas --
`unstated_goal`(12) / `satisfy_restate`(7) / `thwart_cause`(6). Only `unstated_goal` carries both
`action_text` AND `correct_category`, the two fields this mechanism needs; `satisfy_restate` has
`goal_text`/`restate_text` with no `correct_category`, `thwart_cause` has `event_a_text`/
`event_b_text` with no `correct_category` either -- neither is valence-scorable by this mechanism and
both are excluded, not silently dropped). Anti-overfit set = n=12 (`unstated_goal`), the same 12-item
pool `exp_causal_attribution_bridging_v1.py` already treats as its full item set, scored here via
`CATEGORY_STRUCTURE[correct_category][1]` as `gold_valence`. Report BASELINE vs FIXED
valence-classification accuracy against this n=12 set honestly, in both directions (if the fix helps
4-item causal but hurts n=12, that is a REJECT, stated as such, not spun). This substitution (the
~165->12 broader-set swap, disclosed as a deviation from the literal task brief) is honestly a WEAKER
anti-overfit guard than a genuinely independent ~165-item set would have been -- n=12 overlaps
partially in provenance with the 4-item target (same novels/gold-authoring process) and is small;
noted as a caveat on any "generalizes" claim, not hidden.

## Metrics recorded (`data/exp_appraisal_structure_extraction_v1/metrics.json`)

- Per-condition (BASELINE / FIXED / RANDOM_DEGENERATE) x per-seed (0-4) causal-item rows: predicted
  slot, correct, differentiated, extracted valence pair.
- `differentiation_rate_before` / `differentiation_rate_after` (out of 20).
- `causal_arm_b_acc_before` / `causal_arm_b_acc_after`, vs `causal_arm_a_ceiling` (=1.000, reused
  unchanged from the parent cell) and `causal_recency_baseline` (=0.000, reused unchanged).
- `anti_overfit_relation_inference_v1_acc_before` / `_after` (n=25) + per-item deltas.
- `random_degenerate_acc` + gate `random_degenerate_beats_chance` (must be False).
- `verdict`: FIX_HELPS_NARROW / FIX_HELPS_AND_GENERALIZES / FIX_REJECTED_HURTS_BROADER /
  NEGATIVE_CONTROL_FAILED (hard fail if the random-degenerate control passes the beats-chance gate).

## Fairness / contamination

No scoring function reads `true_blocker_agent`/`true_blocker_span`'s identity label, only span TEXT.
theta is reconstructed bit-identically from `exp_grounded_appraisal_sim_earned_v1` (digest-verified,
never retrained). Deterministic seeding: `torch.Generator` per seed/condition, `sorted(set())` id
pools, no `hash()`-based ordering.
