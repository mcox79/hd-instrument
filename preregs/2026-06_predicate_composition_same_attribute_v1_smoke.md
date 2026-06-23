# predicate_composition_same_attribute_v1_smoke -- pre-reg

**Anchor:** `predicate_composition_same_attribute_v1_smoke`
**Date (UTC):** 2026-06-23
**Author:** exp_dev (cell-author)
**Queue:** local_cpu_queue (smoke wall ~15 min target)
**Source:** prior `predicate_composition_temporal_not_v1_smoke` landed MIDDLE_BAND-then-HARD_FAIL with fire_rate_temporal=0.0 across all 3 seeds. Root cause: corpus mismatch -- the 59-Q yes/no comparison subset has only 1 temporal question; 56 of 59 (~95 percent) are SAME-attribute / BOTH-membership questions like "Are X and Y both documentaries?" or "Were X and Y from the same country?"
**Methodology lesson banked:** predicate-primitive cells must VERIFY-THE-REFERENT on actual corpus slice (FREQ_BIAS + question-type distribution) BEFORE dispatch. Parent-drill coverage estimates may not survive corpus-specific reality.

## Scientific question

Does a substrate-native SAME-ATTRIBUTE primitive (cosine over attribute-projected entity vectors), optionally composed with LOGICAL_AND + QUANTIFIER_EXISTS (BOTH-MEMBERSHIP recipe), lift HotpotQA yes/no comparison EM beyond the FREQ_BIAS_BASELINE (= 0.542 majority-class on this 59-Q subset)?

This NARROW smoke is the corpus-matched complement of `predicate_composition_temporal_not_v1_smoke`. It targets the predicate family that actually dominates this subset (95 percent of yes/no comparison Qs share the form "do X and Y both have attribute A" or "is X-attribute equal to Y-attribute"). Cert-eligible evidence that a substrate-native SAME / BOTH primitive lifts beyond FREQ_BIAS would be the first chain-grade-eligible reading on this addressable space.

## Pre-registered HARD bands (sacrosanct per negativity-bias rule)

Let `FREQ_BIAS = ARM_FREQ_BIAS em` measured on this 59-Q yes/no-comparison subset (this run's measurement; predicted reference value = 0.542 = 32/59 no-majority).

**HARD_PASS** (predicate composition unlocks substrate compositional generalization on the addressable space; chain-grade-eligible):
- HP1: `ARM_SAME_PLUS_AND_EXISTS.em_mean >= FREQ_BIAS + 0.05` (lifts substantially over trivial guessing; >= 0.592 if FREQ_BIAS lands at 0.542)
- HP2: `ARM_SAME_PLUS_AND_EXISTS.em_mean >= ARM_SAME_ATTRIBUTE.em_mean + 0.05` (composition adds real value over SAME-only)
- HP3: CV across 3 seeds (7, 17, 23) <= 0.15
- HP4: Sanity self-test passes -- SAME-ATTRIBUTE gives 20/20 correct on synthetic "Are X and X the same?" pairs

**HARD_FAIL** (SAME / BOTH predicate composition refuted on real HotpotQA yes/no comparison):
- HF1: `ARM_SAME_PLUS_AND_EXISTS.em_mean <= FREQ_BIAS - 0.02` (predicate composition does not beat trivial baseline)
- HF2: Sanity self-test fails (< 20/20 on synthetic identity holdout) -- primitive math broken

**MIDDLE_BAND:** any other configuration
- Examples: lift over `ARM_SAME_ATTRIBUTE` but below `FREQ_BIAS + 0.05` (composition helps over SAME-only but ceiling unclear)
- Or `ARM_SAME_PLUS_AND_EXISTS >= FREQ_BIAS + 0.05` but composition delta < 0.05 (SAME alone carries the load; AND-EXISTS decorative on this subset)

## Arms (4)

1. `ARM_FREQ_BIAS` -- majority-class baseline on the 59-Q yes/no comparison subset; canonical FREQ_BIAS reference
2. `ARM_RAW_W_LOOKUP` -- current substrate; pattern-match without predicate primitives (yes/no codebook + projected w2v question vector)
3. `ARM_SAME_ATTRIBUTE` -- SAME primitive in isolation: detect attribute mentioned in question, project both entity vectors onto attribute direction (or against attribute-anchor vector), score "same" if both projections agree on sign / both pass threshold
4. `ARM_SAME_PLUS_AND_EXISTS` -- composed SAME + LOGICAL_AND + QUANTIFIER_EXISTS recipe: for "Are X and Y both A?" use LOGICAL_AND(is_A(X), is_A(Y)); for "Are X and Y the same B?" use SAME-ATTRIBUTE on attribute B; for negated forms use detect_negation + flip

## Mechanism (substrate-native)

- **SAME-ATTRIBUTE**(X, Y, attr): substrate-native -- if attr is a single shared category vector C (e.g., "documentaries"), return `1 if (cos(X, C) > tau AND cos(Y, C) > tau) else 0`. If attr is a relational property (e.g., "from the same country"), compute `cos(X, Y) > tau_sim` directly (X, Y are entity vectors that encode their attribute through w2v geometry).
- **LOGICAL_AND**(p1, p2): bipolar AND on predicate bits (substrate-free: `1 if (p1==1 AND p2==1) else 0`; equivalent to bind with binary scalars).
- **QUANTIFIER_EXISTS**(candidates, threshold): bundle(candidates) above threshold -- in the BOTH-MEMBERSHIP recipe this collapses to LOGICAL_AND over the 2 entity bits.
- **Question parse:** lightweight regex pattern-match (no LLM): `both X and Y are <CAT>` -> BOTH-MEMBERSHIP on CAT; `same <ATTR>` -> SAME-ATTRIBUTE on ATTR; `different <ATTR>` -> NOT(SAME-ATTRIBUTE).

## Calibration: threshold `tau` and `tau_sim`

- `tau` (category-membership threshold): calibrated by sweeping cos(entity, category) over the 59-Q corpus and picking the value that maximizes balanced-accuracy on a held-out half (seed-dependent). Reported per-seed in diag.
- `tau_sim` (entity-similarity threshold for "same"): same protocol, on cos(entity_X, entity_Y) for SAME-attribute questions.
- Both thresholds are fitted ON THE SAME CORPUS the eval runs on -- this is acknowledged as in-domain calibration; the appropriate downstream cell would do held-out calibration on a separate split (deferred per smoke scope).

## Discipline

- N_DIM = 4096; seeds = [7, 17, 23]; n = 59 yes/no-only comparison subset from `data/datasets/hotpot_qa_distractor_dev_1k.jsonl` (id-sorted for determinism)
- Word2vec-google-news-300 (`data/gensim_cache/word2vec-google-news-300/`) for entity + attribute encoding (Path A pretrained semantic encoder)
- Real HotpotQA comparison questions (no synthetic contamination)
- Numpy + gensim only; ASCII-only; no unicode
- Selftest: synthetic 20-pair "Are X and X the same?" identity holdout for SAME-ATTRIBUTE must give 20/20 correct (trivial-yes degenerate; primitive must not break)
- Sanity controls:
  - FREQ_BIAS_BASELINE is THIS RUN'S majority-class measurement on the 59-Q yes/no comparison subset
  - All primitives are L2-norm preserving (within epsilon) and composable with existing bind/bundle/permute
  - Fresh substrate state per arm (no cross-arm contamination)
  - Per-arm `fire_rate` diagnostic (what fraction of Qs did the SAME primitive actually fire on?) -- distinguishes "predicate broken" from "predicate never fires"
- Per-seed checkpointing via `experiments/_seed_checkpoint.py`
- Pre-dispatch verify-the-referent: `tools/predispatch_check.py predicate_composition same_attribute` returned PROCEED (0 prior landings of same anchor, 1 MIDDLE_BAND of distinct temporal_not cell)

## Routing + budget

- **Queue:** local_cpu_queue (CPU-bound; no GPU needed at N_DIM=4096; matmul-free at small M=59; w2v load dominates wall ~30s)
- **Smoke wall-clock target:** ~10-15 min on laptop (3 seeds * ~3min each; matched to temporal_not 526s elapsed)
- **Production:** this IS the smoke; downstream production = full 5-primitive cell or held-out calibration version

## Risk + asymmetry

- The substantive risk is in attribute extraction: if the regex parser fails to identify the attribute mentioned in question (e.g., "both documentaries", "same country"), SAME primitive cannot fire and falls back to majority-class -- that would land MIDDLE_BAND with low `fire_rate`.
- Per-arm `same_fire_rate` recorded in metrics so cert-owner (Skunkworks) can distinguish "predicate broken" from "predicate never fires on this corpus."
- Honest acknowledgement: the predicate-evaluation drill rated SAME as a derived primitive of cosine + threshold (substrate-trivial in expectation); this smoke is the actual cert-eligible reading on a real corpus.
- In-domain threshold calibration risk: `tau` and `tau_sim` are fitted on the same 59-Q corpus they evaluate on. This is acknowledged as a smoke-scope shortcut; the true downstream test is held-out calibration. We log calibration-fit em vs eval-em to make leakage visible.

## Endpoint check (sanity self-test)

Synthetic 20-pair identity holdout: for each pair, `(entity_X, entity_X)` where entity_X is a random unit vector. SAME-ATTRIBUTE(X, X) must return 1 (true) for all 20 pairs (cos(X, X) = 1.0 > any tau in [0, 1)). Trivial-yes degenerate; primitive must not break. This is the same pattern as the temporal_not cell's selftest #4.

## Status_log

- event_kind = `experiment_ship`
- importance = HIGH (top-tier substrate-only enabler; corpus-matched predicate primitive validation; replaces previously-non-dispatched TEMPORAL_NOT cell which had corpus-mismatch)
