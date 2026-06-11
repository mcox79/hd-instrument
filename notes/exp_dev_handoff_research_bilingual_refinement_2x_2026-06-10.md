# exp_dev hand-off -- research: bilingual_refinement_2x

Filed-by: research sub-agent (2026-06-10)
Trigger: notes/research_drill_bilingual_refinement_2x_2026-06-10.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context
pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids, thresholds, and
queue assignment autonomously. Pre-reg bands below are RESEARCH recommendations -- exp_dev validates
and may refine before queue dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or confirm with
orchestrator). Do not ship if paused.

---

## Context

PP-323 HARD_PASS: bilingual dual-substrate hub-and-spoke interlingua at A->B=0.997, pivot=1.000,
4 languages, 400 concepts. The algebra is confirmed. The research note identifies 8 push paths and
5 empirical tests for harder cases (typological distance, abstract concepts, production scale).

The research note is at:
  d:/AI/hd-instrument/notes/research_drill_bilingual_refinement_2x_2026-06-10.md

Cross-reference notes:
  d:/AI/hd-instrument/notes/research_drill_image_schema_polysemy_negative_2x_2026-06-10.md
    (context-binding paths D2.6/D2.1/D2.5 apply to abstract concept polysemy here)

Relevant PP rows:
  PP-323: bilingual hub-and-spoke founding result
  PP-306: NOW-shard context binding (mechanism for evidentiality + abstract polyseme)
  PP-302: bundle-split 4x type-routing capacity (mechanism for 10K production scale)
  PP-309: within-domain analogy at L3 (mechanism for grammatical construction binding)
  PP-299: depth-independent capacity kstar>=80 (informs 10K scale calculation)

---

## Anchor candidates (rank-ordered by P_deflated x impact x CPU-feasibility)

### 1. TEST-3: PRODUCTION-SCALE-10K (HIGHEST PRIORITY)

Anchor pointer: bilingual_10k_scale_cpu_v1 (new; not yet queued)

Substrate-product reading: extends PP-323 from 400 to 10,000 concepts using type-routing sharding
(PP-302, C=5 semantic shards, N=8192). Confirms the O(N) scaling claim for commercial multilingual
KB at production vocabulary size. If this passes, the substrate multilingual product claim covers
commercial vocabulary (~10K lemmas covers ~95% of most text corpora).

Pre-reg bands (research recommendation; exp_dev validates):
  HARD-PASS: cross-lingual recall >= 0.95 at 1K, 5K, and 10K concept checkpoints
  HARD-FAIL: recall < 0.80 at any checkpoint even with type sharding (C=5)
  MID-BAND: recall 0.80-0.95 at 10K but >= 0.95 at 1K/5K (sharding overhead)

P_deflated: 0.55
Tier: CPU only; est. 90-120 min at 10K concepts, N=8192

Why-now: directly extends a HARD_PASS result (PP-323) with no new mechanism; only scale. If it
passes, the multilingual product claim is production-grade. If it fails, the type-sharding strategy
needs revision before product claims.

### 2. TEST-1: TYPOLOGICAL-DISTANCE-TEST English-Mandarin (HIGH PRIORITY)

Anchor pointer: bilingual_mandarin_tonal_cpu_v1 (new; not yet queued)

Substrate-product reading: English-Mandarin is the commercially highest-priority typologically
distant pair. Requires tone-disambiguated Mandarin codebook atoms (separate atom per tone+syllable
combination for polyphonic syllables, e.g. ba-1/ba-2/ba-3/ba-4). Tests whether the concept layer
is truly language-agnostic across tonal/non-tonal boundary.

Pre-reg bands:
  HARD-PASS: English->Mandarin recall >= 0.95 on tone-unambiguous concepts; >= 0.85 on tone-
             ambiguous concepts when codebook uses tone-disambiguated atoms
  HARD-FAIL: recall < 0.80 on tone-unambiguous concepts (non-tonal gap in concept layer)
  MID-BAND: recall 0.80-0.95 on tone-unambiguous; tone-ambiguous recall < 0.85

P_deflated: 0.45
Tier: CPU only; est. 30-60 min; requires Mandarin tone-annotated concept list

Why-now: Mandarin-English translation is the largest commercial multilingual market. A HARD_PASS
here locks the typologically distant pair claim. A HARD_FAIL on tone-unambiguous concepts would
indicate a concept-layer gap requiring architectural revision.

### 3. TEST-2: ABSTRACT-CONCEPT-TRANSLATION (MEDIUM PRIORITY)

Anchor pointer: bilingual_abstract_polyseme_cpu_v1 (new; not yet queued)

Substrate-product reading: tests whether polyseme-indexed concept atoms (from PP-306 context-binding
mechanism) extend the multilingual result to abstract concepts (time, freedom, justice, truth, right,
wrong, good, bad, know, think, feel + 39 more from NSM primitives + culturally-variable abstracts).
Reports separately for NSM-primitive sub-band (expected high) and culturally-variable sub-band
(expected lower).

Pre-reg bands:
  HARD-PASS: NSM primitive sub-band recall >= 0.93; culturally-variable recall >= 0.70 with polyseme
             indexing
  HARD-FAIL: NSM sub-band recall < 0.80 (indicates concept layer fails for verbs/adjectives not
             just nouns); culturally-variable recall < 0.45 even with polyseme tags
  MID-BAND: NSM >= 0.93 but culturally-variable 0.45-0.70

P_deflated: 0.38
Tier: CPU only; est. 45-75 min; requires polyseme-tagged concept list and context-binding prototype

Why-now: abstract concepts are the primary failure mode for existing PP-323 (nouns-only limitation).
This test determines whether the product claim extends beyond lexical nouns. Interacts with
image-schema-polysemy rescue; coordinate with exp_dev.

### 4. TEST-4: LOW-RESOURCE-TRANSFER (MEDIUM PRIORITY)

Anchor pointer: bilingual_low_resource_cpu_v1 (new; not yet queued)

Substrate-product reading: tests codebook atom quality degradation at 500-example vs 5,000-example
training set per concept. Determines minimum data requirement for new language on-boarding. If
HARD-PASS, the O(N) language scaling claim is reinforced (new languages need only hundreds of
examples per concept vs millions for LLM fine-tuning).

Pre-reg bands:
  HARD-PASS: recall at 500 examples per concept >= 0.90 (within 7pp of full baseline)
  HARD-FAIL: recall < 0.75 at 500 examples per concept
  MID-BAND: recall 0.75-0.90 at 500 examples

P_deflated: 0.32
Tier: CPU only; est. 30-45 min; uses subsampled codebook construction

### 5. TEST-5: IDIOM-METAPHOR (LOWER PRIORITY; queue after tests 1-4)

Anchor pointer: bilingual_idiom_explicit_atom_cpu_v1 (new; not yet queued)

Substrate-product reading: tests whether explicit idiom atoms (single concept_hv per idiomatic
meaning, not compositionally derived) enable cross-lingual idiom retrieval at >= 0.80. 100 matched
idioms across 3 language pairs. Confirms that non-compositionality is handled by codebook design,
not substrate algebra.

Pre-reg bands:
  HARD-PASS: cross-lingual idiom recall >= 0.80 with explicit idiom atoms
  HARD-FAIL: recall < 0.60 even with explicit atoms (idiomatic concept_hv culturally unstable)
  MID-BAND: recall 0.60-0.80

P_deflated: 0.42
Tier: CPU only; est. 20-30 min; requires idiom inventory construction

---

## Context pointers (file paths, not summaries)

  d:/AI/hd-instrument/notes/research_drill_bilingual_refinement_2x_2026-06-10.md
  d:/AI/hd-instrument/notes/substrate_capability_map.md (PP-323, PP-306, PP-302, PP-309, PP-299)
  d:/AI/hd-instrument/notes/research_drill_image_schema_polysemy_negative_2x_2026-06-10.md
  d:/AI/hd-instrument/hdlab/ (substrate implementation)
  d:/AI/hd-instrument/verification/ (existing tests for anchor design reference)

---

## Contract section

Research provides: mechanism analysis, P_deflated estimates, pre-reg band recommendations, test
design framing, failure mode identification.

exp_dev owns: anchor implementation, exact threshold grid, queue assignment, smoke gate, dispatch
order, self-test per formula-selftests, post-ship verify.

exp_dev may adjust pre-reg bands based on substrate-implementation constraints not visible to
research. The P_deflated estimates are calibrated per [[feedback-lit-scan-calibration-penalty]];
exp_dev should not inflate them without new empirical evidence.

---

## Autonomy declaration

exp_dev operates fully autonomously on anchor design and dispatch. This file does not constrain
exp_dev's implementation choices. The research note provides direction; execution is exp_dev's domain.
