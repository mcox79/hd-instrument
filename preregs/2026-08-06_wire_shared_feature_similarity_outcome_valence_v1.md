# Pre-reg: wire n11c shared-feature-similarity organ into outcome-valence referent-match

Date: 2026-08-06
Task: WIRE-DONT-ISLAND -- replace outcome-valence's narrow hand-authored SYNONYM_GROUPS
(hdlab/goal_typing.py, promoted commit ab12d8e88) with the just-PROVEN shared-feature-similarity
organ from `experiments/exp_n11c_shared_feature_lexical_similarity_v1.py` (commit 7d0a574b4,
HARD_PASS, Director-VET'd).

## What is being wired

New production module `hdlab/lexical_similarity.py` (clean copy, not a live import, of
exp_n11c's CONCEPT_FEATURES 86-concept McRae-style feature lexicon + its FHRR bundle-cosine
encoder, both reusing already-promoted hdlab primitives `hdlab.bundling.bundle` and
`hdlab.situation_model_accumulate.unit_phase_vec` -- hdlab does not import experiments/).
SUPPLY EXTENSION: 3 concepts added (`ferry`, `sister`, `rival`) needed to cover
`experiments/data/outcome_valence_congruence_v2.jsonl`'s referent-stress items, same tagging
convention exp_n11c already used elsewhere (near-synonym pairs share almost all defining tags;
related-not-synonym pairs share only the domain tag).

`hdlab/goal_typing.py::_referent_links` Tier-2 (currently: `actual_ref in
_SYNONYM_OF.get(desired_ref, ())`, backed by the single hand-authored group
`{ferry, vessel, boat, ship}`) is REPLACED with: if both `desired_ref` and `actual_ref` are IN
`hdlab.lexical_similarity.CONCEPT_FEATURES`, link iff
`concept_similarity(desired_ref, actual_ref) >= SIMILARITY_LINK_THRESHOLD`; if either referent is
OOV of the lexicon, fall through to the existing no-link behavior (never crash, never over-link
by default). Tier-1 pronoun-coref is UNCHANGED. Link-tier label renamed `"synonym"` ->
`"shared_feature"` (reflects the new mechanism; `LINK_TIERS` and the one dependent pytest
assertion in `verification/test_outcome_valence_goal_congruence.py` (L-met's `link_tier`) are
updated to match).

## Threshold selection (measured, before wiring into the consumer)

Computed directly from `hdlab/lexical_similarity.py::self_test()` against the exact concepts the
outcome-valence v2 bank needs:

| pair | relation | sim (MEASURED) |
|---|---|---|
| vessel / ferry | true near-synonym (L-family, must LINK) | 0.6340 |
| sister / rival | over-link-guard analog (D-family, must NOT link) | 0.3977 |
| vessel / dock | related-not-synonym (domain-tag-only overlap) | 0.2789 |
| vessel / ferry, SCRAMBLED assignment | circularity control | 0.0134 |

`SIMILARITY_LINK_THRESHOLD = 0.50`: sits 0.134 below the decisive synonym pair and 0.102-0.221
above the two must-not-link pairs -- clean separation, not a knife-edge. Not tuned per-pair: the
CONCEPT_FEATURES tagging convention (domain tag vs specific defining tags) is the same uniform
rule exp_n11c's author already applied to the other 86 concepts; the 3 SUPPLY additions follow it
verbatim (ferry = boat's exact tag set; sister/rival = new domain-tag-only-overlap pair, same
shape as the existing dock/sailor pair).

## HARD-PASS (ALL required, measured on `experiments/data/outcome_valence_congruence_v2.jsonl`
via `verification/test_outcome_valence_goal_congruence.py` + `hdlab.goal_typing.self_test()`)

1. `sim(vessel,ferry) >= SIMILARITY_LINK_THRESHOLD` (mechanism fires on the decisive synonym pair)
2. `sim(vessel,dock) < SIMILARITY_LINK_THRESHOLD` AND `sim(sister,rival) < SIMILARITY_LINK_THRESHOLD`
   (over-link guard: related-not-synonym / genuinely-different concepts never link)
3. `sim(vessel,ferry) - sim(vessel,ferry SCRAMBLED) >= 0.30` (circularity control: scrambling the
   concept->feature assignment collapses the gain -- earned, not an encoder artifact)
4. `core_flip` (16 items, families A-J): 16/16 correct, UNCHANGED from the pre-wiring baseline
   (none of these items route through the synonym tier)
5. `coverage_stress` L-family (2/2: L-unmet, L-met): both correct, L-met's `link_tier ==
   "shared_feature"` (proves the shared-feature mechanism actually fired, not an incidental
   literal/pronoun match)
6. `over_link_guard`: D-unmet stays `UNMET` via `reason == "referent_mismatch"` (not an
   OOV-fallthrough -- both `sister` and `rival` ARE in the lexicon, so this is a genuine
   sub-threshold measurement, not a lexicon-coverage accident); M-unmet stays `UNMET` (unaffected,
   `garage`/`workshop`/`shed` are not in the lexicon so this path is untouched by this wiring)
7. `precision_guard` H/H2 abstain (NA), `positive_controls` G/G2 correct -- unaffected, no change
8. `backward_compat` 48/48 (`hdlab.goal_owner_select.select_outcome_owner`, structurally invariant
   to outcome polarity -- unaffected by this wiring by construction)
9. `v1_regression`: v1's original 10-item bank re-verdicts bit-identically (0 mismatches)
10. `python verification/run_certification.py` GREEN, no regression vs the pre-wiring baseline
    (220 passed / 3 skipped per commit ab12d8e88; new tests in `hdlab/lexical_similarity.py`'s own
    self-test may add to the pytest count if collected, but zero prior tests may flip)

## HARD-FAIL (ANY triggers)

- `sim(vessel,ferry) < SIMILARITY_LINK_THRESHOLD` (the ATL organ under-links; synonym-stress
  regresses vs the prior SYNONYM_GROUPS behavior)
- `sim(vessel,dock) >= SIMILARITY_LINK_THRESHOLD` OR `sim(sister,rival) >=
  SIMILARITY_LINK_THRESHOLD` (the ATL organ over-links; breaks the D-unmet over-link guard)
- `core_flip < 16/16` OR `backward_compat < 48/48` (regression on previously-held gates)
- scramble does not collapse (`delta < 0.30`) -- circular/artifact result
- certification regresses vs the 220/3 baseline (any previously-green test flips red)

MIDDLE_BAND: not applicable -- this is a deterministic wiring change (no stochastic sweep), so
the outcome is binary: either every above gate holds (HARD-PASS, ship) or one breaks
(HARD-FAIL, revert).

## Compute architecture

Sequential-CPU, justified: this is a lexicon lookup + one FHRR bundle + one cosine per referent
pair, called at most a handful of times per passage (2-4 referent comparisons per bank item, 26
items). Wall time for the full bank + certification suite is seconds, not the GPU-batching regime
this pre-reg's parent checklist targets. `crlb_n/a`: graded-similarity threshold decision, not a
capacity/argmax-noise-floor cell. `storage_strategy: no_storage` (no persisted vectors; feature
vectors are process-local and recomputed deterministically from the fixed seed).

## Files touched

- `hdlab/lexical_similarity.py` (NEW) -- the lifted organ
- `hdlab/goal_typing.py` (EDIT) -- `_referent_links` Tier-2 swap, `LINK_TIERS` update, self_test
  addition citing the new tier
- `verification/test_outcome_valence_goal_congruence.py` (EDIT) -- `link_tier == "synonym"` ->
  `"shared_feature"` assertion update (the mechanism genuinely changed; this witness must track
  the promoted module's real behavior)

`experiments/exp_outcome_valence_goal_congruence_v2.py` (the historical source-of-truth cell) is
LEFT UNTOUCHED, per the existing convention documented throughout `hdlab/goal_typing.py` (source
cells stay the source-of-truth for their own historical numbers; only the promoted hdlab copy is
upgraded).

## Prior-work check (substrate-KB concept-query, per exp_dev standing discipline)

`bash tools/substrate_query.sh "shared feature lexical similarity ATL hub synonym referent
linking ferry vessel"` -> top hit cosine=0.2539 (drinking_vessel/wordnet), all hits below the
0.30 rediscovery threshold. No prior arc cell at cosine>0.30 beyond the already-cited n11c/n11b
lineage itself (which this task explicitly builds on, not rediscovers). Genuinely a fresh wiring
task.
