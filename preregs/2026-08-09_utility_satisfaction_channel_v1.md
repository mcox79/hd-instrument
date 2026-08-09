# Pre-registration: exp_utility_satisfaction_channel_v1

**Filed by:** exp_dev, 2026-08-09. **Task source:** Director spawn prompt (grounded goal-satisfaction
utility channel), citing `notes/research_glassbox_utility_inverse_planning_leg_2026-08-09.md` (the
mechanism spec + pre-registered bands) and the just-landed HARD_FAIL
`exp_goal_cued_valence_channel_v1` (commit 215ae7a38) as the confound this build must avoid.

## Prior-work check (SUBSTRATE-KB, mandatory before authoring)
`bash tools/substrate_query.sh "utility satisfaction attribute weighted bundle goal achievement
channel"` -> top hit cosine=0.2998 (below the 0.30 novelty threshold), pointing at the existing
3-channel `hdlab/goal_achievement.py` organ itself (the base module this cell extends, not a prior
attempt at this specific mechanism). No hit above cosine 0.30. Consistent with the research drill's
own `capability_registry_query.py --serves "utility function scoring"` returning 0/73 matches.
**Verdict: genuinely novel channel for this arc, not a rediscovery.**

## What / why
`hdlab/goal_achievement.py`'s 3 channels (relation/valence/contrast) ABSTAIN-TO-MAJORITY on a real
cohort of DesireDB items (both `relation_channel` and `valence_channel` return `None`, so the verdict
falls back to `MAJORITY_CLASS="Fulfilled"` by default, `channel=="majority"`). This cell adds a 4th
channel, `hdlab.goal_achievement.utility_channel`, that represents the stated goal as a small
GROUNDED weighted bundle of attribute-predicates and scores the outcome against each active
attribute independently, targeting recovery specifically on that abstain-to-majority cohort (a
strict-ADD evaluation harness -- the channel is NOT wired into `goal_achievement_verdict`'s default
precedence; see `hdlab/goal_achievement.py`'s own module comment for the full mechanism writeup).

## CRITICAL LESSON applied (avoiding the Stage-1 confound)
`goal_cued_valence_channel` (Stage-1, HARD_FAIL commit 215ae7a38) computed its goal-cue anchor as
`_verb_synonyms(goal_verb)` and searched for that anchor LITERALLY IN THE OUTCOME TEXT. On the
cohort defined by `relation_channel` finding NO such recurrence, the anchor was therefore
tautologically absent by construction, so the channel degenerated to uniform weighting (measured
delta=0.0 exactly on all 3 metrics, subset(b) n=21, commit 215ae7a38 metrics.json).

This channel's activation and evidence-scoring **never compare the goal's words directly against
the outcome's words**. Activation (`activate_attributes`) compares the goal's verb/referent only
against a FIXED, goal-independent attribute-exemplar vocabulary (6 attributes: ACQUIRE_POSSESS,
LOCATION_REACHED, SOCIAL_CONNECTION, AVOID_HARM_SAFETY, ACTIVITY_COMPLETION,
EMOTIONAL_STATE_ACHIEVED) -- it never inspects the outcome text at all. Evidence-scoring
(`_attribute_outcome_state`) compares outcome tokens only against that same attribute's FIXED
satisfied/violated cue vocabulary -- it never inspects the goal's specific words. The bridge between
goal and outcome runs only through the shared attribute-category label, never through direct
goal-word-vs-outcome-word comparison, so the channel is structurally unable to inherit Stage-1's
tautological-absence failure and CAN fire on the relation_channel-abstain population.

**Grounding mechanism (per the task's mandatory requirement):** primary-sense (k=1, WordNet's own
frequency-ordered `synsets()[0]`) synonym-set overlap, POS-aware (VERB/ADJ/NOUN), NOT verb-lemma
literal-recurrence. Calibration (this session, scratchpad probe, not committed): raw path/wup
taxonomic similarity with best-of-all-synset-pairs was measured UNRELIABLE for this task -- e.g.
("know","meaning") scored 0.94 wup-similarity against the ACQUIRE_POSSESS pool via an obscure
secondary sense of "get" ("move into a desired direction of discourse"), a clear false positive.
Restricting to primary-sense-only synonym-SET overlap (no hypernym/hyponym expansion) eliminated
that class of false positive across a 15-pair spot-check while still correctly linking
("purchase","get"), ("reach","arrive"), ("meet","see"), ("happy","glad"), etc. -- precision-favoring
by design (MEASURED@self_test_utility_channel, `hdlab/goal_achievement.py`).

## Mechanism (stated once, not swept -- full writeup in hdlab/goal_achievement.py module comment)
1. `activate_attributes(desire)`: `find_desired_state(desire)`'s `verb_lemma`/`referent` vs each
   attribute's `goal_verbs`/`goal_nouns` exemplar pool. Weight 1.0 for literal exact-lemma
   membership (Tier-1), 0.7 for a primary-sense WordNet-synonym-only hit (Tier-2). Attributes
   clearing neither tier are inactive (weight 0, excluded).
2. `_attribute_outcome_state(attr, outcome)`: per-outcome-token grounded polarity vote (Tier-1
   exact cue membership, Tier-2 primary-sense WordNet synonym overlap) against `attr`'s
   `satisfied_cues`/`violated_cues`, negation-aware (`_verb_negated_before`, the same organ
   `relation_channel`/`valence_channel` use), count-voted (tie -> ABSENT, same convention as
   `valence_channel`).
3. FHRR representation: `U_g = bundle(stack([w_i * bind(ATTR_ROLE_i, FILLER[state_i]) for i in
   active]))` (`hdlab.binding.bind`, `hdlab.bundling.bundle`, unmodified). Audit round-trip: for
   each active attribute, `unbind(U_g, ATTR_ROLE_i)` then an FHRR-complex64 argmax+top1-top2-margin
   cleanup (same discipline as `hdlab.glass_box_loop.cleanup_with_margin`, reimplemented for
   complex64 since that module's own implementation is numpy-bipolar-BSC-specific) recovers the
   per-attribute state.
4. `score = sum(w_i * sign(recovered_state_i))` over active attributes (SATISFIED=+1,
   VIOLATED=-1, ABSENT=0). `score==0` (no active attribute fires signal, or exact tie) -> abstain
   (`None`, same tie->abstain convention as `valence_channel`, no extra margin hyperparameter). Else
   `Fulfilled` (score>0) / `Unfulfilled` (score<0).

## Data: DesireDB (same provenance/loader as exp_goal_cued_valence_channel_v1.py)
Cached at `data/desiredb_cache/DesireDB.csv` (gitignored, auto-fetched from
`raw.githubusercontent.com/ra-elahe/DesireDB/main/DesireDB.csv` if absent). `outcome="Evidence"`,
`desire="Desire-Expression-Sentence"`, balanced `rng.sample` per class, seed 20260808 (identical
convention to the Stage-1 cell, verified reproduces the documented benchmark below).

## Cohort definition (abstain-to-majority)
`goal_achievement_verdict(desire, outcome)["channel"] == "majority"` -- i.e. BOTH `relation_channel`
and `valence_channel` return `None` (stricter than Stage-1's subset(b), which only required
`relation_channel` to abstain). MEASURED@this session's calibration probe: n=160 draw (seed
20260808, 80/class) -> cohort n=22 (14 gold-Fulfilled, 8 gold-Unfulfilled).

## Metrics (definitions fixed here, not tuned post-hoc)
- **recovery_rate** (the `>=40%` / `15-40%` / `<15%` band metric): of the cohort items where the
  majority-only baseline is WRONG (gold=="Unfulfilled", since majority always predicts "Fulfilled"),
  the fraction `utility_channel` FIRES on (non-abstain) AND gets CORRECT. This is the standard
  error-recovery definition -- credits genuine discrimination, not just "channel agrees with
  majority a lot" (which would trivially inflate a raw-accuracy-based metric on a
  majority-skewed cohort). Denominator = # cohort items with gold=="Unfulfilled".
- **fires_rate**: fraction of the cohort where `activate_attributes(desire)` is non-empty (the
  Stage-1-killer check -- MUST be verified non-zero before trusting any HARD_FAIL, per the task's
  explicit mandate).
- **cohort accuracy** (i)/(ii)/(iii): (i) majority-only baseline, (ii) utility-augmented
  (utility_channel fires ? its prediction : majority fallback), (iii) wrong-goal pairscramble
  (utility_channel with a SCRAMBLED desire, same deterministic derangement offset=n//2 as Stage-1 --
  `PROT-023` compliant, not `hash()`-derived).
- **pairscramble deltas**: `abs(acc_iii - acc_i)` (HARD-PASS needs `<=0.05`, "collapses to within
  0.05 of the majority-only baseline"); `abs(acc_iii - acc_ii)` (HARD-FAIL if `<=0.03`, "stays within
  0.03 of the real-goal score" -- the leg would be reading outcome-valence alone, ignoring the goal).
- **full-bench macro-F1**: composed 4-channel verdict (`relation -> valence -> utility -> majority`,
  contrast-override unaffected -- see "composition" below) on the SAME n=80 (40/class, seed 20260808)
  sample the documented 0.686 organ number was measured on, for a direct no-regression comparison.
  Also reports the n=160 composed macro-F1 for context (non-gating).

**Composition** (full-bench only; NOT the default production precedence -- pure evaluation-harness
composition): `base = goal_achievement_verdict(desire, outcome)`; if `base["channel"]=="majority"`,
try `u = utility_channel(desire, outcome)`; if `u is not None`, final verdict = `u`; else final =
`base["verdict"]`. No re-application of the contrast-override is needed: `channel=="majority"`
already implies `contrast_present(outcome)` was False for this item (if it had been True, the
override would have fired on the `Fulfilled` majority default and `channel` would read
`"contrast_override"`, not `"majority"` -- verified by construction in
`goal_achievement_verdict`'s own logic).

## Pre-registered bands (fixed by the task, not exp_dev's to loosen)
- **HARD-PASS:** `recovery_rate >= 0.40` AND full-bench (n=80) macro-F1 `>= 0.686` (no regression)
  AND `abs(acc_iii - acc_i) <= 0.05`.
- **MIDDLE_BAND:** `0.15 <= recovery_rate < 0.40`, full-bench macro-F1 does not regress below 0.686,
  pairscramble collapses (`abs(acc_iii - acc_i) <= 0.05`) -- iterate attribute vocab/weights.
- **HARD-FAIL:** `recovery_rate < 0.15` OR full-bench macro-F1 `< 0.620` (the rule floor) OR
  `abs(acc_iii - acc_ii) <= 0.03` (pairscramble stays too close to the real-goal score --
  goal-blind valence leakage, not genuine goal-conditioning).
- **INVALID:** `harness_validity_check` delta `> 0.03` macro-F1 vs the documented 0.686 baseline, OR
  cohort n `< 15` at n=160 (underpowered), OR the # gold-Unfulfilled cohort items (recovery_rate's
  denominator) is 0 (recovery_rate undefined).

Any outcome not cleanly matching one of HARD-PASS/MIDDLE_BAND/HARD-FAIL's stated conjunctions (e.g.
recovery_rate in-band but a HARD-FAIL disjunct also fires) resolves HARD-FAIL first (the disjuncts
are checked before the bands, matching Stage-1's own precedence convention).

## Mandatory pre-full-dispatch check (per the task's explicit instruction)
Before trusting any HARD_FAIL from the full run, the cell logs `fires_rate` (attribute-activation
fire rate on the cohort) prominently in `verdict_msg` and metrics. If `fires_rate == 0.0`, the
Stage-1 confound would have structurally repeated -- self_test_utility_channel's
STAGE-1-CONFOUND-IMMUNITY check (mechanism-fires assertion, `hdlab/goal_achievement.py`) already
verifies this cannot happen by construction (activation never inspects the outcome text), but the
cell also verifies it empirically on the smoke run before full dispatch.

## Compute architecture
(b) sequential-CPU with justification: lexicon/WordNet lookup + FHRR bind/bundle/unbind over N=2048
complex64 vectors, up to 6 attributes/item, ~160 items x 3 arms. `_primary_synonyms` is
`lru_cache`-memoized (repeated words across items are cheap after the first WordNet lookup). No
matmul-heavy batchable primitive at this scale; MEASURED wall time this session (self-test + smoke)
well under a few seconds per ~80-item arm. Storage: no_storage/no_composition (independent per-item
scoring; the FHRR bundle is a single-item construction, not a multi-item associative store).

## Cell-template mandatory fields
- `cell_chunked`: false (single-process, seconds of compute).
- `start_marker_written` / `crash_diagnostic_present` / `heartbeat_present`: true.
- `arms_differ_verified`: true (hash-check on the 3 arms' full prediction vectors, smoke + full).
- `final_metrics_atomicity`: `tmp_replace`.
- `except SystemExit: raise` before `except Exception` (no bare except, no `except BaseException`).
- `crlb_n/a`: "deterministic symbolic/lexicon vote + FHRR bind/bundle/cleanup over a fixed 6-role x
  3-filler codebook, no decoded/noisy continuous signal from a swept capacity regime -- CRLB does
  not apply; FHRR round-trip fidelity is instead verified directly via
  `self_test_utility_channel`'s roundtrip_ok assertions (bundle capacity at <=6 items, N_DIM=2048,
  is far below any capacity-noise regime)".
- `baseline_in_band` / `discriminator_reachability`: n/a per META_RULE_AG (channel-comparison cell,
  not a swept-difficulty cell; arm (i) is a fixed prior-benchmark baseline).
- `HP_SCOPE`: `{arm_ii: [recovery_rate, full_bench_macro_f1, pairscramble_collapse_vs_i]}` -- arms i
  and iii are comparators only, do not themselves gate HARD_PASS/HARD_FAIL.
- `cardinality_ok`: `EXPECTED_N_UNITS = 3` (one unit per arm; no seed/sweep axis).
- `deterministic_seeding`: true (fixed int seed 20260808; FHRR role/filler vectors seeded 20260809;
  derangement offset `n//2`, not `hash()`-derived).
- `calibration_check`: `adaptive_with_discriminator_gate` -- the WordNet grounding parameter (k=1
  primary-sense-only, no hypernym expansion) was selected via a principled spot-check against
  independently-chosen sanity pairs (not the DesireDB eval items themselves) BEFORE running the full
  eval, and is applied identically to activation and evidence-scoring; not tuned against the
  mechanism arm's own cohort score.
- `functional_requirements`: "represent a stated goal as a weighted bundle of grounded
  attribute-predicates" -> `activate_attributes` + the FHRR bind/bundle layer (this cell's new
  organs, reusing owned `hdlab.binding`/`hdlab.bundling`/`hdlab.goal_typing.find_desired_state`).
  "score an outcome per active attribute without lexical recurrence on the goal's own words" ->
  `_attribute_outcome_state` + `_token_cue_polarity` (grounded via WordNet primary-sense synonymy,
  a FIXED goal-independent cue vocabulary).
- `real_code_path_exercised`: `[find_desired_state, activate_attributes, _attribute_outcome_state,
  bind, unbind, bundle, utility_channel_trace]` -- self-test constructs the REAL substrate primitives
  (`hdlab.binding.bind/unbind`, `hdlab.bundling.bundle`) at small hand-authored scale, not a
  synthetic-only branch.
- `progress_logging`: n/a (`timeout_s` well under 1800; single-process run measured in seconds).

## Autonomy notes (exp_dev-owned, per the task's contract)
6 attribute primitives + role codebook, activation-tier weights (1.0/0.7), the count-vote +
zero-sum-abstain scoring formula, FHRR N_DIM=2048/seed=20260809, cell/file naming, single-seed
(20260808) evaluation -- all exp_dev's own design choices, documented above and in
`hdlab/goal_achievement.py`'s module comment. The bands, the mandatory pairscramble control, and the
GROUNDED-cue (not lexical-recurrence) requirement are NOT exp_dev's to drop and were not altered.
