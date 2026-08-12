# Pre-reg: wire grounded (sensorimotor + concreteness) meaning as concept_similarity's OOV fallback

Date: 2026-08-11
Task: architecture-audit TIER-1 shore-up (notes/architecture_audit_2026-08-11.md, "MEANING is a
~380-word HAND-TAGGED lexicon, while 2 bigger built assets sit UNUSED"). Wire real grounded
meaning into the LIVE similarity path so the substrate's meaning extends past ~380 words.

Prior-work check (substrate_query.sh "grounded lexical similarity sensorimotor norms Lancaster
Brysbaert concreteness OOV fallback wire"): top hit cosine=0.2773 (lexical_similarity.py itself,
background docs), all hits below 0.30 -- NONE at cosine>0.30. This wiring is genuinely novel, not
a rediscovery. Supporting literature found (notes/research_multi_attribute_grounding_fusion_ATL_
hub_2026-07-10.md): Lynott & Connell sensory-modality norms carry information concreteness/
imageability norms do NOT -- a genuinely additional channel, motivating using both sources
together rather than concreteness alone.

## What is being wired

New module `hdlab/grounded_similarity.py`: loads Lancaster sensorimotor norms (11 perceptual/
action-effector dims, 39,707 words) + Brysbaert concreteness (1 dim, 39,954 words) from
`data/grounding_testbed/*.csv`, z-scores the joined single-token vocabulary (36,810 words after
join + multi-token-phrase filtering), returns a capped cosine similarity. `hdlab/lexical_
similarity.py::concept_similarity` is extended ADDITIVELY: unchanged hand-lexicon path when both
words are in CONCEPT_FEATURES; falls back to the grounded path (both words, not a mixed
comparison) when either word is OOV of CONCEPT_FEATURES; new `use_grounded_fallback: bool = True`
kwarg lets a caller reproduce the pre-2026-08-11 None-on-OOV behavior byte-identically. New
`in_lexicon_or_grounded()` helper for callers that currently pre-gate on `in_lexicon()` (opt-in
migration path, zero forced change to existing callers).

Warriner VAD + Kuperman AoA (also in data/grounding_testbed/) are NOT used in v1 -- both are
affect/acquisition-trajectory signals, not identity-content signals, and Warriner's smaller
coverage (13,915 words vs Lancaster's 39,707) would force an asymmetric zero-fill for most words.
Documented as an available, not-yet-used extension point.

scale_win_tinytransformer_encoder (237.7M-token from-scratch transformer, capability_registry.jsonl
gate=WIRE) was EVALUATED as the task instructs, not wired -- see "Learned-encoder diagnostic"
below for the measured reason.

## MEASURED calibration (the decisive finding this pre-reg is built around)

Raw cosine over the z-scored 12-dim [11 sensorimotor + concreteness] vector, n=2000 random
background pairs for percentile context (repo scratch probe, 2026-08-11):

| pair | relation | raw cosine | background percentile |
|---|---|---|---|
| sofa / couch | TRUE SYNONYM | 0.968 | 100.0 |
| happy / joyful | TRUE SYNONYM | 0.962 | 99.95 |
| apple / orange | SIBLING, DISTINCT (both fruit) | 0.952 | 99.85 |
| dog / cat | SIBLING, DISTINCT (both pet) | 0.932 | 99.85 |
| wood / plastic | SIBLING, DISTINCT (both material) | 0.919 | 99.85 |
| wood / coal | SIBLING, DISTINCT (both fuel) | 0.785 | 97.80 |
| stone / idea | UNRELATED | -0.695 | 1.70 |
| wood / happy | UNRELATED | -0.196 | 33.00 |

TRUE_SYNONYM and SIBLING_DISTINCT populations are statistically inseparable at the top of this
metric's range (apple/orange 0.952 vs happy/joyful 0.962 -- no threshold on this metric separates
them). UNRELATED pairs cluster low. This is a genuine ceiling of pure sensorimotor-profile
similarity (it measures "how do I perceive/interact with X", not "what X specifically IS"), not a
calibration bug -- percentile-normalizing against the random-pair background does not rescue it
(both populations sit at/above the p95-p99.9 tail).

**Design response**: `GROUNDED_CAP = 0.45`, structurally below `SIMILARITY_LINK_THRESHOLD` (0.50).
This is an architectural safety cap (derived from the finding above, not tuned per test pair): it
guarantees, by construction, that the grounded fallback can never itself cross the project's
same-idea/merge threshold, while still returning a real, correctly-ordered graded value in the
sub-ceiling band for genuinely different degrees of relatedness (UNRELATED near 0, weak/moderate
relatedness in between).

## Learned-encoder diagnostic (evaluated, NOT wired)

`scale_win_tinytransformer_encoder`'s checkpoint (`data/exp_scale_meaning_learn_arc_heldout_v3_
relobj/ckpt_seed_7.pt`) was loaded (glass-box, local, CPU, no external LLM call) and probed on the
SAME word pairs via its `TinyTransformer.pooled()` mean-token-embedding interface (the only
interface available for a bare two-word API like concept_similarity):

| pair | relation | encoder cosine |
|---|---|---|
| sofa / couch | TRUE SYNONYM | 0.570 |
| trash / garbage | TRUE SYNONYM | 0.490 |
| stone / idea | UNRELATED | 0.548 |
| coal / metal | SIBLING, DISTINCT | 0.744 |
| dog / cat | SIBLING, DISTINCT | 0.744 |

MEASURED finding: bare single-word probing does not preserve synonym > unrelated ordering
(trash/garbage 0.490 < stone/idea 0.548) -- WORSE than the sensorimotor path for this exact task.
Root cause (disk-verified, `experiments/exp_scale_meaning_learn_arc_heldout_v3_relobj.py`): this
encoder was trained/evaluated via `encode_concept_text_reps` -- pooled over many real CORPUS
MENTIONS of a concept (postings), not a bare 1-2-BPE-token embedding. concept_similarity's API
(two bare word strings, no corpus context) is off-distribution for its proper interface; building
the proper interface (corpus-mention lookup + pooling per query word) is a materially heavier,
out-of-scope lift for a live word-pair similarity function. Decision: sensorimotor+concreteness
norms are the better-fitting asset for THIS API; the encoder remains available (WIRE gate intact,
unchanged) as a foundation asset for a future consumer that can supply concept-level corpus
context (e.g. a retrieval-time concept encoder, not a bare-lexeme lookup).

## Compute architecture

(a) batched-GPU / (b) sequential-CPU with justification / (c) mixed: **(b) sequential-CPU**. This
is not a training or bulk-inference cell: it is a one-shot lexicon join (36,810 rows, pure Python
CSV parse + z-score) plus a handful of cosine-similarity lookups. Wall time <5s per the smoke/full
runs below. No batching candidate exists (no per-item independent GPU-amenable compute).

Storage strategy: no_storage / no_composition -- this cell reads two static CSV files into an
in-process dict; there is no persisted multi-item store and no downstream composition/chaining.

## Envelope / fail-bands

**HARD-PASS** (ALL required):
1. NO-REGRESSION: `hdlab/lexical_similarity.py::self_test()` passes unchanged (existing 5
   assertions untouched) AND `experiments/exp_representation_canonicalization_v1.py --self-test`
   AND its FULL run reproduce the landed HARD_PASS verdict with the SAME counts
   (same_idea_match_rate=1.0000 148/148, automatic_corroboration_rate=1.0000 145/145, 72/72
   distinct cross-gap triples, scramble 1.00 real vs 0.00 scrambled) -- zero drop.
2. use_grounded_fallback=False reproduces None-on-OOV byte-identically (toggle works).
3. OOV COVERAGE UNLOCK: a held-out set of >=200 words that CONCEPT_FEATURES returns None for now
   get a real graded similarity via the grounded path; WordNet-synonym-derived held-out pairs
   score meaningfully higher (median) than WordNet-cross-domain-unrelated held-out pairs.
4. ANTI-OVER-MERGE (decisive): 100% of a held-out set of >=15 sibling-distinct "trap" pairs
   (same broad category, different identity: materials/fruits/pets/vehicles/relations incl.
   produces-vs-consumes-style pairs where coverage allows) score STRICTLY BELOW
   SIMILARITY_LINK_THRESHOLD (0.50) via concept_similarity's default path. (Guaranteed by
   GROUNDED_CAP construction for the sensorimotor path; must hold empirically too.)
5. Controls: scramble collapses the mean synonym-pair raw-cosine gain by >=0.30 (hdlab/grounded_
   similarity.py self_test); no-leak (grounded table build reads only the two static CSVs, no
   test-labels/answer leakage into the join or z-score).
6. `python -m pytest verification/` GREEN, no regression vs pre-wiring baseline.

**MIDDLE-BAND / HARD-FAIL (honest, names the real grounding limit)**: grounding over-merges (any
sibling-distinct trap pair crosses SIMILARITY_LINK_THRESHOLD) OR fails to extend coverage
meaningfully OR any control fails OR the canonicalization no-regression check drops. Per director
instruction: if the sensorimotor norms are too coarse to separate distinct concepts, report that
honestly -- already partially true of the RAW metric (see calibration table above); the cap is the
engineered mitigation and its own empirical validation is Gate 4 above.

## Smoke vs Full

Smoke: `--smoke` -- 6 hand-picked pairs (2 synonym / 2 sibling-trap / 2 unrelated) + toggle check,
<2s.
Full: no flag -- WordNet-synset-derived held-out synonym/unrelated pairs (programmatic, not
hand-curated, avoids cherry-picking) + hand-curated sibling-trap set + the canonicalization-cell
replication + pytest run. Expected wall time <60s (no training, no GPU).

## Metadata

cell_name: grounded_meaning_wire_lexical_fallback_v1
final_metrics_atomicity: tmp_replace (os.replace, single-shot)
progress_logging: n/a (elapsed_s < 1800; §17 not triggered)
deterministic_seeding: true (fixed seeds 999/20260811 throughout; sorted(set()) for all word-list
iteration; no hash()-derived seeding)
arms_differ_verified: true (grounded vs hand-lexicon vs scrambled all produce distinct digests,
asserted in self-tests)
