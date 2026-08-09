# Pre-registration: exp_goal_cued_valence_channel_v1

**Filed by:** exp_dev, 2026-08-09. **Hand-off:** notes/exp_dev_handoff_research_brain_fidelity_goal_outcome_top_down_2026-08-09.md
(research), parent audit notes/research_brain_fidelity_goal_outcome_architecture_2026-08-09.md.

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "goal-cued valence channel dependency-arc relevance weighting biased
competition top-down outcome valence"` -> top hits cosine 0.34-0.38, ALL pointing at
`outcome_valence_goal_congruence_v1/v2` (`hdlab/goal_typing.py`'s existing GOAL-CONGRUENCE mechanism:
discrete VerbNet-style desired-class-vs-actual-class matching + referent coreference). That is a
RELATED but DISTINCT mechanism from this cell: congruence is a discrete CLASS-MATCH gate (fires only
when both goal and outcome verbs resolve to a registered class, ~2/80 fire-rate per its own docstring);
this cell is a CONTINUOUS RELEVANCE-REWEIGHTING of the existing bag-of-words lexicon-vote signal
(`valence_channel`), gated on dependency-arc proximity, with much higher intended coverage (fires
whenever a goal-cue word or its outcome-clause proximity exists, not only on exact class membership).
No prior cell builds this specific reweighting. Verdict: genuinely novel combination for this arc, not
a rediscovery.

## What / why
`hdlab/goal_achievement.py::valence_channel` is a goal-BLIND uniform bag-of-words valence vote over the
whole outcome sentence. 4 independent brain-fidelity lit-scans (RPE, PFC guided-activation/biased-
competition/predictive-coding, situation-model/discourse comprehension, ACC/PRO-model) converge on
TOP-DOWN: the goal should actively bias which outcome content gets weighted, not be consulted only
after an independent bottom-up scan. `goal_cued_valence_channel` (added to `hdlab/goal_achievement.py`,
NOT wired into `goal_achievement_verdict`'s precedence -- pure ADD) reweights each candidate
valence-bearing outcome token by its dependency-arc proximity to a goal cue (goal verb + WordNet
synonyms + referent content word), falling back to uniform weighting when no textual anchor exists.

## Mechanism (stated once, not swept)
1. Goal cue = `find_desired_state(desire)["verb_lemma"]` + `_verb_synonyms` (WordNet neighbor
   expansion, byte-identical organ to `relation_channel`'s own) UNION the `referent` field's content
   word(s).
2. Crude clause-split the outcome on `. ! ?`; parse each clause via the persisted UD front-end
   (`hdlab.candidate_generator.CandidateGenerator`: UPOS tagger + hashed arc parser, UAS ~0.79,
   `data/frontend_assets/{pos_tagger_ud_ewt_upos.json,arc_parser_hashed_ud_ewt.npz}` -- already
   persisted, reused unmodified, no new parser).
3. For each candidate valence token (same `opinion_lexicon`/`wordnet_polarity_propagation` detection
   `valence_channel` already uses): weight = `1/(1+dependency_tree_distance)` to the nearest
   goal-cue-lemma anchor token IN THE SAME CLAUSE; `0.25` (fixed) if the anchor is only in a DIFFERENT
   clause; `1.0` (uniform fallback) if no anchor anywhere in the outcome.
4. Weighted-vote (sum of weights per polarity, not counts); negation-flip via the same
   `_verb_negated_before` scan `valence_channel` already uses.
`goal_cue_desire` parameter defaults to `desire` (mechanism arm ii); the harness passes a DIFFERENT
item's desire for the mandatory scrambled-cue control (arm iii).

## Data: DesireDB provenance (load-bearing correction to the hand-off)
The hand-off could not locate `DesireDB.csv` on disk and flagged it as possibly form-gated. Verified
this session: the corpus is PUBLICLY hosted, unauthenticated, at
`https://github.com/ra-elahe/DesireDB/blob/main/DesireDB.csv` (raw:
`https://raw.githubusercontent.com/ra-elahe/DesireDB/main/DesireDB.csv`), 3988215 bytes, matching the
GitHub tree API's recorded blob size exactly (byte-verified). The earlier "fill out a form" hit was a
different (older/mirror) listing, not the actual data source. The cell's loader
(`_load_desiredb_rows`) caches this file at `data/desiredb_cache/DesireDB.csv` (auto-fetched via
`urllib` if absent; gitignored by the existing `data/*/**` pattern, never committed, consistent with
the project's established "DesireDB.csv is not committed" convention in
`verification/test_goal_achievement.py`). 3680 raw rows; 3076 binary-eligible (`Fulfillment-Label` in
{Fulfilled, Unfulfilled}; 1950/1126 split); columns include `Desire-Expression-Sentence`,
`Post-Context`, `Evidence`, `Fulfillment-Label`.

**Field-mapping calibration (MEASURED, not guessed):** tried `outcome` = `Evidence` /
`Post-Context` / concatenations, `desire` = `Desire-Expression-Sentence`, against the UNCHANGED
`goal_achievement_verdict` (the existing 3-channel pipeline whose docstring/witness cite macro-F1
0.686 / F1 0.706 / acc 0.688 on a DesireDB n=80 balanced seed-20260808 subsample).
`outcome="Evidence"`, balanced sampling = `rng=random.Random(seed); rng.sample(pos_rows, n_per_class)
+ rng.sample(neg_rows, n_per_class)` reproduces macro-F1=0.699 / F1=0.714 / acc=0.700 at n=80
(MEASURED@this pre-reg's calibration script, run against the unmodified `goal_achievement_verdict`) --
within ~0.01-0.015 of the documented numbers, well under the project's own established ~0.05 SE band
at n=80 for this benchmark. Adopted as the harness construction. `harness_validity_check` in the cell
re-runs this exact check at dispatch time and gates INVALID if the delta exceeds 0.03 macro-F1.

## Sample size (exp_dev deviation from the hand-off's "n=80" starting point, flagged per its own
escape valve: "exp_dev flags this and either sources additional DesireDB items or widens the
thresholds")
The hand-off anticipated DesireDB might be inaccessible or n=80 might underpower subsets (b)/(c)
(n<~15 gate). Since the FULL corpus (3076 binary-eligible rows) is now accessible, `n=160` (80/80
balanced, same seed 20260808) is used for the FULL run to give subsets (b)/(c) more headroom, while
the n=80 draw is retained ONLY for the `harness_validity_check` (the number with a precise documented
target). Both use the identical loader/field-mapping/seed convention -- purely a `n_per_class` change
(40 vs 80), not a different construction.

## Subsets
- (a) full sample (n=160).
- (b) mixed-polarity/relation-abstain: `relation_channel(desire, outcome)` reason in
  `{"abstain","no_goal"}` AND outcome has >=2 valence-bearing tokens (opinion_lexicon or
  wordnet_polarity_propagation hits) with BOTH polarities present (npos>=1 and nneg>=1).
- (c) single-clause/unambiguous: outcome has <=1 total valence-bearing token (npos+nneg<=1).
Cell reports subset sizes; if (b) or (c) < 15 at n=160, cell flags `UNDERPOWERED_SUBSET` in
verdict_msg (does not silently proceed past the INVALID band without flagging).

## Arms
- (i) `valence_channel(outcome)` -- baseline, unchanged.
- (ii) `goal_cued_valence_channel(desire, outcome)` -- mechanism.
- (iii) `goal_cued_valence_channel(desire, outcome, goal_cue_desire=<different item's desire>)` --
  mandatory scrambled-cue control (deterministic derangement: item i's cue source = item
  `(i + n//2) % n`, guaranteeing a full offset / no self-match). Falsifies whether goal-RELEVANCE
  specifically, not just any reweighting, is the active ingredient.
Channel-`None` outputs (tie/no-signal) map to `MAJORITY_CLASS` ("Fulfilled", same fallback
`goal_achievement_verdict` itself uses) for per-arm accuracy/macro-F1 scoring -- documented policy,
applied identically to all 3 arms.

## Pre-registered bands (subset (b), the population most exposed to goal-blind confusion)
- **HARD-PASS:** (ii) beats (i) by >= 10 points macro-F1 on (b) AND (ii) beats (iii) by a comparable
  margin (>= 7 points) on (b) AND (ii) does not regress (c) by more than 2 points macro-F1 vs (i).
- **HARD-FAIL:** (ii) within 3 points of (i) on (b) (goal-cue weighting isn't the lever even where
  affect words are present), OR (ii) regresses (c) by > 5 points vs (i).
- **MIDDLE_BAND:** any outcome not meeting HARD-PASS or HARD-FAIL cleanly (e.g. (ii)>(i) but
  (ii) vs (iii) gap thin, or (ii)>(i) with a (c) regression between 2 and 5 points).
- **INVALID:** `harness_validity_check` delta > 0.03 macro-F1 vs the documented 0.686 baseline, OR
  subset (b) or (c) has n < 15 at the chosen sample size.

## Compute architecture
(b) sequential-CPU with justification: this is a lexicon-lookup + shallow-parse (perceptron POS tag +
hashed-perceptron arc parse) pipeline over ~160 short text items x 3 arms; per-item wall time
MEASURED ~16ms/clause (candidate_generator parse), no matmul-heavy batchable primitive, no GPU
benefit. Total wall time MEASURED (this pre-reg's probe): CandidateGenerator load 0.16s, single-clause
parse 0.016s. Storage strategy: no_storage / no_composition (independent per-item scoring, no
chained/composed retrieval).

## Cell-template mandatory fields
- `cell_chunked`: false (single-process, <1min compute; no multi-hour risk requiring per-seed cell
  files).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: true (all 3 present per
  template, defensive even though runtime is short).
- `arms_differ_verified`: true (hash-check on the 3 arms' full prediction vectors at smoke + full).
- `final_metrics_atomicity`: `tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`).
- `crlb_n/a`: "deterministic symbolic/lexicon vote + shallow-parse weighting, no decoded/noisy
  continuous signal -- CRLB does not apply".
- `baseline_in_band`: n/a per META_RULE_AG (this is a channel-comparison cell, not a
  substrate-vs-adversarial-regime cell; the "baseline" (arm i) is a fixed prior benchmark, not swept
  for difficulty). `discriminator_reachability`: n/a, no quantitative noise floor.
- `HP_SCOPE`: `{arm_ii: [hard_pass_delta_vs_i, hard_pass_delta_vs_iii, subset_c_regression_guard]}` --
  arm i and arm iii do not themselves gate HARD_PASS/HARD_FAIL, only participate as comparators.
- `cardinality_ok`: `EXPECTED_N_UNITS = 3` (one unit per arm; no seed/sweep axis -- single
  deterministic split per the hand-off's "direct comparability" mandate).
- `deterministic_seeding`: true (fixed int seed 20260808; derangement offset is `n//2`, not
  `hash()`-derived).
- `calibration_check`: `adaptive_with_discriminator_gate` -- the outcome-field mapping (`Evidence`)
  and sampling recipe (`rng.sample` per class) were selected by matching the documented baseline
  (principled: reproduces a known, disk-cited number), not tuned against the mechanism arm's own
  score.
- `functional_requirements`: "reweight valence votes by goal-relevance" -> `_tree_distance` +
  `_goal_cue_words` (this pre-reg's new organs, reusing owned `candidate_generator`/`goal_typing`/
  `_verb_synonyms`). "detect mixed-polarity/relation-abstain population" -> `relation_channel` +
  lexicon-hit counting (both existing organs).
- `real_code_path_exercised`: `[CandidateGenerator, find_desired_state, relation_channel,
  valence_channel, goal_cued_valence_channel]` -- self-test constructs the REAL CandidateGenerator at
  small scale (a handful of hand-authored sentences), not a synthetic-only branch.
- `progress_logging`: n/a (`timeout_s` well under 1800; single-process run measured in seconds of
  actual compute beyond the one-time torch/nltk/CandidateGenerator load).

## Autonomy notes (exp_dev-owned, per the hand-off's contract)
Weighting formula = dependency-arc distance (not lexical-similarity-bucket): chosen because
`hdlab.lexical_similarity`'s CONCEPT_FEATURES lexicon (89 concepts, mostly concrete nouns) and
`verb_lexical_similarity`'s OUTCOME_VERB_FEATURES (~50 verbs) have far lower expected coverage of the
actual valence-bearing tokens `opinion_lexicon`/`wordnet_polarity_propagation` surface on real
DesireDB prose than a structural dependency-arc distance (which needs no lexicon match at all, only a
literal/lemma goal-cue recurrence + a parse). Weight-to-vote mapping: sum of weights per polarity
(not count), one clean monotonic formula `1/(1+dist)`, stated once, not swept. Seed count: single
seed (20260808) per the hand-off's own "direct comparability" framing -- no multi-seed robustness
sweep in this pre-reg (a natural follow-up if HARD-PASS/MIDDLE_BAND, not required for the falsifiable
verdict itself). Harness authored together with the cell (single self-contained file).
