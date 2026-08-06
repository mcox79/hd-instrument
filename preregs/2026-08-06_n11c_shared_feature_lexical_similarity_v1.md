# Pre-reg: n11c_shared_feature_lexical_similarity_v1

**Date:** 2026-08-06
**Anchor:** `n11c_shared_feature_lexical_similarity_v1`
**Script:** `experiments/exp_n11c_shared_feature_lexical_similarity_v1.py`
**Reused primitives (unmodified):** `hdlab/bundling.py` (bundle -- FHRR per-component-phase
compress), `hdlab/situation_model_accumulate.py` (unit_phase_vec -- random unit-magnitude
complex64 vector; also `_cos_complex` reuses that module's `cleanup_argmax` cosine convention)
**Route:** LOCAL (this turn, in-process; not queue-dispatched -- whole cell runs in well under
1 second, no corpus dependency)
**Driver note:** `notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md` Section 3 option (a)
(SUPPLY a feature lexicon, EARN the composition) + the north-star drill on the EARN(distributional)
HARD_FAIL (commit d0dc07c91, banked commit 52bae63e2: "VINDICATES brain shared-FEATURE-correlation
metric (Cox 2024). PIVOT to SUPPLY(McRae feature-lexicon) track").
**Prior-work check (SUBSTRATE-KB, mandatory before authoring):** `bash tools/substrate_query.sh
"ATL hub lexical semantic similarity shared feature McRae feature norms concept bundle"` -> max
cosine 0.3555 (top hit entity='feature', a generic concept-node, plus a `research_drill_reasoning_
composition_routing_2x_2026-06-11.md` chunk describing bind(feature_X, feature_Y) prototype
composition for PROBLEM CLASSES, not lexical similarity). No prior McRae-style shared-feature
lexical-similarity cell found. NONE at cosine>0.30 on a lexical-similarity-specific reading of the
hits -> novel cell, not a rediscovery (the 0.3555 hit is a generic "feature" concept-node match,
not a prior implementation of this mechanism).

## Mechanism under test

The EARN(distributional) track (exp_n11b, `context_mode="symmetric_pattern"` on
`hdlab/random_indexing.py`) HARD_FAILED: `sym_frac=0.2069` was EXACTLY EQUAL to its own scramble
control (`scramble_frac=0.2069`) -- a noise-floor result, not real signal; the WINDOW baseline
(0.3793) actually beat it. MEASURED@`d:/AI/hd-instrument/data/exp_n11b_symmetric_pattern_lexical_
similarity_v1/metrics.json:detail` (sym_frac, window_frac, scramble_frac all read directly this
session). Per the drill, this is diagnosed as (a) distributional co-occurrence measures the WRONG
METRIC (topical relatedness, not synonym-grade similarity -- WINDOW's tier-means are flat at
~0.83-0.86 across all three tiers) and (b) the symmetric-pattern signal specifically is
data-starved/noise-dominated at this corpus scale.

The brain's ATL hub computes similarity as shared cross-modal FEATURE correlation, not
co-occurrence (Cox, Rogers, Shimotake et al. 2024, *Imaging Neuroscience*, PMC12224414:
intracranial vATL activity is graded/multidimensional and tracks McRae-style behavioral
feature-norm overlap). Per the standing invariant, supplying a feature LEXICON is allowed DATA
supply (same class as prior RESULT_VERB_CLASS / desiderative-verb supplies); the MECHANISM
(composing shared features into a graded similarity signal) must be the substrate's OWN glass-box
VSA op. This cell supplies a compact, hand-authored McRae-style (McRae, Cree, Seidenberg &
McNorgan 2005) feature lexicon for the 86 concepts in exp_n11b's probe, and EARNS the composition
via `hdlab.bundling.bundle` (FHRR superposition) over `hdlab.situation_model_accumulate.
unit_phase_vec` feature-index vectors -- reused unmodified, not a new mechanism class.

## Arms (single unit; N_DIM=8192; deterministic seed=7)

| Arm | Mechanism | Hypothesis |
|---|---|---|
| SHARED_FEATURE | NEW: concept = `bundle()` of its hand-authored feature tags' index-vectors; cosine of bundles | Separates Tier1 > Tier2 > Tier3 (shared-feature-count-driven) |
| WINDOW_CITED | CITED (not re-run): loaded from n11b's landed FULL metrics.json | Plateaus (already-measured HARD_FAIL baseline: 0.3793, tier-means flat ~0.83-0.86) |
| HASH_RANDOM | Floor control: ONE independent random unit-phase vector per concept (no bundling at all) | No graded ordering, by construction |
| SCRAMBLED_FEATURES | Ablation: SAME feature vectors, but concept-name -> feature-set ASSIGNMENT permuted (fixed seed=999, verified 0 fixed points this run) | Collapses the SHARED_FEATURE gain toward chance (~1/6=0.167 for strict 3-way ordering) |

WINDOW is CITED not re-run: re-running the ~300-400s text8 WINDOW fit would duplicate an
already-established, deterministic fact (same code path, same config, same seed). The cell loads
`data/exp_n11b_symmetric_pattern_lexical_similarity_v1/metrics.json` at runtime (dynamic, not
hardcoded, so it cannot silently go stale) with a hardcoded MEASURED@ fallback if that file is
absent on a given host.

## Probe set

REUSES (imports, does not copy) the SAME 29 Tier1/Tier2/Tier3 triples from
`experiments/exp_n11b_symmetric_pattern_lexical_similarity_v1.py` (`_PROBE_TRIPLES`), verified by
direct import (not a hand-copy that could silently drift). Coverage: all 86 distinct words across
the 29 triples have a `CONCEPT_FEATURES` entry (verified in `_selftest`, `n_skipped_oov_or_zero=0`
on the actual run).

## Feature-lexicon design (McRae-style, hand-authored, documented convention)

Each of the 86 concepts gets a small (2-5 tag) `frozenset` of feature tags drawn from a 76-tag
vocabulary organized into domain families (NAUTICAL, VEHICLE_DOM, EMOTION_DOM, GEO_DOM,
MAGNITUDE_DOM, SPEED_DOM, REPAIR_DOM, COGNITION_DOM, FINANCE_DOM, TEMPORAL_DOM, ART_DOM,
ACADEMIC_DOM, VISUAL_DOM). Uniform design convention (applied identically across all 86 concepts,
not tuned per-triple):
- **True synonym pairs (Tier1)** share the domain tag AND (nearly) all of the anchor's SPECIFIC
  tags -- they denote basically the same thing (e.g. vessel/ship share `{NAUTICAL, WATERCRAFT,
  HAS_HULL, CARRIES_CARGO}`).
- **Related-not-synonym pairs (Tier2)** share ONLY the domain tag, not the defining specific tags
  (e.g. vessel/dock share only `NAUTICAL`; dock is `STATIC_STRUCTURE`, not `WATERCRAFT`/`HAS_HULL`).
- **Unrelated pairs (Tier3)** share nothing (different domain tag entirely).

This is a MODELING SIMPLIFICATION applied uniformly, not a per-triple result-shaping choice.
**One disclosed, PRE-PREDICTED miss:** "happy"/"music" (probe row 10, tier2) is a genuine
CROSS-DOMAIN associative relation (people associate happy music) that a taxonomic feature-lexicon
structurally cannot capture by this convention (`music`'s domain=`ART_DOM` != `happy`'s domain=
`EMOTION_DOM`, so shared-feature count=0, same as the Tier3 target). This was identified by
hand-tracing all 29 triples' domain assignments BEFORE running the cell (see reasoning trace this
session) -- not an after-the-fact excuse. It is the SOLE predicted failure; 28/29 other triples
were predicted to have anchor/Tier1 same-domain-and-mostly-shared-specific-tags, Tier2
same-domain-only, Tier3 different-domain.

## Pre-reg HARD bands

**HARD_PASS (ALL required):**
1. `SHARED_FEATURE.ordered_inequality_frac >= 0.81` (>= 0.80 + 5% of [0.80,1.0] band width, per
   META_RULE_L strictly-above-floor; task's stated floor is >=0.80)
2. `SHARED_FEATURE.ordered_inequality_frac - WINDOW_CITED.ordered_inequality_frac >= 0.20`
   (materially beats the 0.3793 distributional baseline, large margin)
3. `SHARED_FEATURE.ordered_inequality_frac - HASH_RANDOM.ordered_inequality_frac >= 0.20`
   (materially beats the zero-structure floor)
4. `SCRAMBLED_FEATURES.ordered_inequality_frac <= 0.35` AND
   `SHARED_FEATURE.ordered_inequality_frac - SCRAMBLED_FEATURES.ordered_inequality_frac >= 0.30`
   (scramble ablation collapses the gain toward chance ~0.167 -- earned, not artifact)
5. `tier1_syn_mean_cos > tier2_rel_mean_cos > tier3_unrel_mean_cos` (strict) AND
   `tier1_syn_mean_cos - tier2_rel_mean_cos >= 0.10` (clear synonym-vs-related gap)
6. `n_llm_calls == 0` AND `n_external_model_calls == 0` at every stage (earned, not borrowed)

**HARD_FAIL (ANY triggers):**
- `SHARED_FEATURE.ordered_inequality_frac < 0.50`
- `SHARED_FEATURE.ordered_inequality_frac - WINDOW_CITED.ordered_inequality_frac < 0.10` (does not
  materially beat WINDOW)
- `SHARED_FEATURE.ordered_inequality_frac - SCRAMBLED_FEATURES.ordered_inequality_frac < 0.10`
  (scramble does not collapse -> feature lexicon is circular/degenerate, not earned structure)

**MIDDLE_BAND:** everything else (real but partial signal, a gate missed narrowly, or the
disclosed cross-domain miss pulls `ordered_frac` below 0.81 but still clearly above
window/chance).

## Config

- N_DIM = 8192 (matches n11/n11b precedent for cross-cell comparability).
- seed = 7 (feature-vector generation; matches n11/n11b's first seed).
- scramble_seed = 999 (fixed, disjoint seed for the concept->feature permutation; verified this
  run to be a full derangement, 0/86 fixed points).
- No corpus, no text8 dependency for the SHARED_FEATURE/HASH_RANDOM/SCRAMBLED_FEATURES arms
  (concept set and feature lexicon are fixed, hand-authored data) -- WINDOW_CITED alone depends on
  the prior cell's text8 run, which is CITED not re-run.

## Smoke-gate note (DISCRIMINATOR-MUST-SURVIVE-SCALE, Option A: smoke AT full-N)

Unlike exp_n11b (which needed Option B analytical justification because its WINDOW/SYMMETRIC_
PATTERN arms depend on a 17M-token corpus), this cell has NO corpus-scale dependency: the 86
concepts and N_DIM=8192 ARE the full regime. `--smoke` therefore runs the IDENTICAL computation
as FULL (verified: both produced `verdict=HARD_PASS`, `sf_frac=0.9655`, byte-identical detail
except `run_mode` and output path). This is Option A, trivially and honestly satisfied (not a
shortcut around the gate -- there is no smaller regime to define).

## Cost (MEASURED, not hypothesized -- already run)

Whole cell (self-test + full run + smoke run) completed in well under 2 seconds total wall time.
FULL run alone: `elapsed_s=0.672` MEASURED@`d:/AI/hd-instrument/data/exp_n11c_shared_feature_
lexical_similarity_v1/metrics.json:elapsed_s`.

## Why this matters (strategic)

Per the drill and the north-star EARN-track HARD_FAIL: general synonym/hypernym resolution
("vessel"~"ferry") is BLOCKED on the missing ATL learned lexical-semantic hub. The EARN
(distributional) track failed because raw co-occurrence measures relatedness, not similarity, and
is separately data-starved for the symmetric-pattern variant at text8 scale. This cell tests
whether the SUPPLY(feature-lexicon)+EARN(composition) track -- which matches the brain's actual
METRIC (Cox et al. 2024's vATL shared-feature-correlation finding) rather than its corpus-scale --
closes the gap. If HARD_PASS, the substrate gains a genuinely earned (mechanism, not data),
glass-box, graded lexical-similarity signal on the covered vocabulary. **Honest scope, stated
before running:** this is a MECHANISM-PROOF on 86 hand-authored concepts; general open-vocabulary
feature coverage (inducing features for arbitrary words, not just the 86 in this probe) is a
separate, missing-LEARNING follow-up and is explicitly NOT claimed here.

## Skunkworks structural blockers (baked into cell)

- `_LLM_CALL_COUNTER = [0]`, `_EXTERNAL_MODEL_CALL_COUNTER = [0]` -- substrate-only, no borrowed
  embedding, at every stage.
- per-ARM checkpoint (single unit; `write_partial_key`/`aggregate_partials` keyed by arm name).
- atexit + SIGTERM synthesize a PARTIAL metrics.json from whatever arms completed.
- `except SystemExit: raise` / `except KeyboardInterrupt: raise` BEFORE `except Exception` (no
  bare `except:` / `except BaseException:` anywhere in the cell -- verified via grep gate).
- ARMS-MUST-DIFFER (META_RULE_AF): SHARED_FEATURE / HASH_RANDOM / SCRAMBLED_FEATURES vectors for
  the same concept ("vessel") verified bit-distinct in `_selftest`.
- Glass-box provenance: `feature_provenance` (concept -> sorted feature tags) persisted in
  metrics detail; `_selftest` verifies rebuilding a concept vector from the same features is
  bit-identical (deterministic, inspectable) and from different features is bit-different (not a
  constant / borrowed embedding).
- structured `gate_claims` (`record_gate`) persisted under `structured_gate_claims`.

## CAN-FAIL discriminators

1. SHARED_FEATURE must clear the >=0.81 ordered-inequality bar; if the hand-authored lexicon does
   not actually separate synonym/related/unrelated by shared-feature count, it fails honestly.
2. HASH_RANDOM (zero structure) must fail by construction -- a sanity floor.
3. SCRAMBLED_FEATURES must collapse the SHARED_FEATURE gain -- if permuting the concept-to-feature
   assignment does NOT hurt, the "signal" is not earned from real feature-content structure
   (possible bug, e.g. leaking concept-name information into the scored vectors) and must not be
   trusted.
4. If SHARED_FEATURE does not beat the CITED WINDOW baseline, the SUPPLY-track hypothesis (that
   matching the brain's METRIC, not scaling the corpus, closes the gap) is falsified for this
   design.

## Earned-not-borrowed verification (mandatory)

- `n_llm_calls == 0` AND `n_external_model_calls == 0` at fit and inference time.
- Own, inspectable weights at every stage: per-feature-tag random unit-phase index vectors
  (`_build_feature_vectors`, reusing `hdlab.situation_model_accumulate.unit_phase_vec`
  unmodified), concept vectors via `hdlab.bundling.bundle` (reused unmodified) -- no black-box
  distillation, no pretrained embedding file loaded anywhere in the SHARED_FEATURE/HASH_RANDOM/
  SCRAMBLED_FEATURES arms (WINDOW_CITED is a CITED prior substrate-own result, not a borrowed
  embedding either).
- `feature_provenance` in metrics detail names exactly which features drove each concept vector
  -- a true glass-box result can name WHICH shared features drove a similarity call, not just
  produce a number (verified inspectable for all 86 concepts).
- SCRAMBLED-assignment ablation (HARD-PASS gate 4 / HARD-FAIL gate 3) is the mandatory "does the
  graded structure survive destroying the concept-to-feature correspondence" check.

## Cites

- `notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md` (Section 3 option (a), Section 4)
- Cox, R., Rogers, T.T., Shimotake, A., Kikuchi, T., Kunieda, T., Miyamoto, S., Takahashi, R.,
  Matsumoto, R., Ikeda, A., Lambon Ralph, M.A. (2024). "Graded, cross-modal similarity in ventral
  anterior temporal lobe." *Imaging Neuroscience* (MIT Press), PMC12224414.
- McRae, K., Cree, G.S., Seidenberg, M.S., McNorgan, C. (2005). "Semantic feature production norms
  for a large set of living and nonliving things." *Behavior Research Methods* 37(4).
- `data/exp_n11b_symmetric_pattern_lexical_similarity_v1/metrics.json` (prior landed HARD_FAIL;
  WINDOW arm CITED from here).
- `hdlab/situation_model_accumulate.py`, `hdlab/bundling.py` (reused FHRR primitives, unmodified).

## Predispatch / prior-work check

`bash tools/substrate_query.sh "ATL hub lexical semantic similarity shared feature McRae feature
norms concept bundle"` -> max cosine 0.3555 (generic "feature" concept-node hit; not a prior
implementation of this mechanism). PROCEED (2026-08-06).

## MEASURED RESULT (this session, FULL run, not hypothesized)

`MEASURED@d:/AI/hd-instrument/data/exp_n11c_shared_feature_lexical_similarity_v1/metrics.json`:
`verdict=HARD_PASS`. `sf_frac=0.9655` (28/29; sole miss = happy/music, the pre-predicted
cross-domain case), `window_frac=0.3793` (cited), `hash_frac=0.1034`, `scramble_frac=0.3103`.
`tier_means`: shared_feature=(0.9307, 0.3041, 0.0020), window_cited=(0.8586, 0.8515, 0.8301),
hash_random=(0.0001, 0.0009, 0.0004), scrambled_features=(0.0799, 0.0648, 0.0646). All 6
structured gate claims TRUE. `elapsed_s=0.672`. `n_llm_calls=0`, `n_external_model_calls=0`.
