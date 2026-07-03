# PRE-REG: substrate concept encoder vs bge-large vs surface baselines -- Wikipedia 10K apples-to-apples

**Anchor:** `substrate_concept_encoder_wikipedia_10k_apples_to_apples_v1_2026_07_02`
**Cell file:** `experiments/exp_substrate_concept_encoder_wikipedia_10k_apples_to_apples_v1_2026-07-02.py`
**Filed:** 2026-07-02 (USER-authorized late evening: Option A' -- brain-analog ConceptEncoder on prior wikipedia_ingest infra)
**Author:** hdi_exp_dev

## Question

Does the brain-analog `hdlab.concept_encoder.ConceptEncoder` (Spoke 1 v3-D CG'd 2026-07-02 on 25-cluster synthetic corpus) work at real-corpus scale, or was its success confined to the synthetic supervised regime?

Head-to-head: bge-large frozen (borrowed neural encoder) vs ConceptEncoder (brain-analog, one-shot supervised) vs char_positional (V1 surface) vs char_trigram (bag-of-substrings) on title -> article retrieval over real Wikipedia.

## Framing discipline (LOAD-BEARING)

Per USER-locked memory:
- `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`: substrate has no general knowledge ingested; this test does NOT ingest general knowledge.
- `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`: brain-analog mechanism at supervised regime is not brain-analog capability at unsupervised discovery.
- Prior Wikipedia HP (`data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json`) recall@5=0.992 was achieved with the BORROWED bge-large encoder. This test asks whether the substrate's OWN concept-encoding mechanism can do this task.

**Honest scope:** the ConceptEncoder arm here uses one-shot supervision (article title = unique concept label; article body sentences = training text for that concept). Even a HARD_PASS does NOT grant "substrate knows general knowledge"; it grants "brain-analog concept-encoding mechanism works on real-corpus title->article retrieval with one-shot title supervision."

## Prior work check

Substrate-KB concept-query (2026-07-02) for "brain-analog concept encoder wikipedia real corpus retrieval title article one-shot supervision":
- Top hit cosine=0.31 (NaturalQuestions/DPR discussion; unrelated).
- **Prior-work check: NONE at cosine>0.30 for the specific test.** Cell is genuinely novel.

Related prior cells consulted:
- `experiments/exp_wikipedia_ingest_100k_gpu_v1.py` -- prior HP bge-large FROZEN + Wikipedia 100K (recall@5=0.992). We ADAPT that harness for the bge-large reference arm.
- `experiments/exp_substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026-07-02.py` -- CG source cell for ConceptEncoder (synthetic 25-cluster corpus). Extended primitive: `hdlab.concept_encoder.ConceptEncoder` (commit e8f15a036).

## Test protocol

Title -> article retrieval over N Wikipedia articles (loaded from `data/datasets/wikipedia_100k.jsonl` in FULL; `data/datasets/wikipedia_smoke_500.jsonl` in SMOKE).

For each arm:
1. Encode each article body -> body HD.
2. Encode each title -> title HD.
3. Compute cosine similarity matrix S[i, j] = cos(title[i], body[j]).
4. For each title i, sort articles by S[i, :] descending.
5. recall@k = fraction of titles whose correct body index i is in top-k of its sort.

Regime:
- N articles: SMOKE=500, FULL=10000.
- Seeds: SMOKE=1 (seed=11), FULL=3 (11, 17, 23).
- Substrate-arm N_DIM: 8192 (scale-sentinel validated per concept_encoder selftest 10).
- BGE arm N_DIM: 1024 (bge-large native).

## Arms

| Arm | Encoder | Training | HD dim | Compute |
|-----|---------|----------|--------|---------|
| ARM_BGE_LARGE_REFERENCE | `BAAI/bge-large-en-v1.5` (frozen bf16) | none (pretrained) | 1024 | Batched GPU |
| ARM_CONCEPT_ENCODER_ONESHOT | `hdlab.concept_encoder.ConceptEncoder` | one-shot: article title = unique concept label; article body split into K sentences (SMOKE K=3, FULL K=5); `fit(sentences, article_indices)` | 8192 | Sequential CPU numpy per concept (per module compute_arch); batched matmul for retrieval |
| ARM_CHAR_POSITIONAL_ONLY | `hdlab.char_positional_encoder.CharPositionalEncoder` | none (deterministic hash HDs) | 8192 | Sequential CPU per sentence |
| ARM_CHAR_TRIGRAM_UNSUP | `hdlab.char_trigram_encoder.CharTrigramEncoder` | none (deterministic hash HDs) | 8192 | Sequential CPU per sentence |

### Per-arm retrieval:

- **BGE:** body HD = bge-large(article_body); title HD = bge-large("Represent this sentence for searching relevant passages: " + title). Cosine on unit-normalized 1024-dim vectors.
- **CONCEPT_ENCODER:** fit ConceptEncoder(n_dim=8192, n_concepts=N_articles, k_sparsity=0.02, seed=seed) on (body_sentences, article_indices) supervised pairs. concept_hds[i] IS the body HD for article i (sparse-bipolar int8). Title HD = surface HD via internal char_positional encoder. Retrieval: title_surface @ concept_hds^T with cosine norms.
- **CHAR_POSITIONAL_ONLY:** body HD = `encoder.encode_sentence(article_body)`; title HD = `encoder.encode_sentence(title)`. Cosine on bipolar HDs.
- **CHAR_TRIGRAM_UNSUP:** body HD = `encoder.encode(article_body)`; title HD = `encoder.encode(title)`. Cosine on bipolar HDs.

## Metrics (per arm x seed)

- `recall_at_1`, `recall_at_5`, `recall_at_10`
- `mean_reciprocal_rank`
- `intra_article_body_title_cos` (mean cos(title_i, correct_body_i))
- `inter_article_title_body_cos` (mean cos(title_i, random_other_body))
- `signal_to_noise_ratio` = intra / max(inter, 1e-6)
- `n_dim`, `encoding_wall_s`, `throughput_articles_per_sec`

Aggregate across seeds: mean + std for each of the above.

## HP bands

`HP_SCOPE: LOAD_BEARING on ARM_BGE_LARGE_REFERENCE (Gate D) + ARM_CONCEPT_ENCODER_ONESHOT (brain-analog scale-up claim)`

### HARD_PASS (target CG)

| # | Metric | Threshold | Applies to |
|---|--------|-----------|------------|
| HP1 | Gate D reproducibility: recall@5 | >= 0.85 | ARM_BGE_LARGE_REFERENCE |
| HP2 | Brain-analog real-corpus: recall@5 | >= 0.60 | ARM_CONCEPT_ENCODER_ONESHOT |
| HP3 | Mechanism advantage over V1 surface: recall@5(CE) - recall@5(CHAR_POSITIONAL) | >= 0.15 | ARM_CONCEPT_ENCODER_ONESHOT |
| HP4 | Mechanism advantage over bag-word: recall@5(CE) - recall@5(CHAR_TRIGRAM) | >= 0.15 | ARM_CONCEPT_ENCODER_ONESHOT |
| HP5 | No regression on Gate D: BGE arm behaves as expected (r@5 >= 0.85) | -- | ARM_BGE_LARGE_REFERENCE (same as HP1; HP5 = reproducibility discipline check) |

### HARD_FAIL

| # | Condition | Implication |
|---|-----------|-------------|
| HF1 | ARM_BGE_LARGE_REFERENCE recall@5 < 0.75 | Gate D violation -- cell has invocation bug or dataset changed; halt+investigate |
| HF2 | ARM_CONCEPT_ENCODER recall@5 < max(ARM_CHAR_POSITIONAL, ARM_CHAR_TRIGRAM) | Brain-analog mechanism no real-corpus advantage; MAJOR ARC REFRAME |
| HF3 | ARM_CONCEPT_ENCODER recall@5 < 0.05 | Mechanism fundamentally fails on real text (near chance = 5/10000 = 0.0005) |

### MIDDLE_BAND

- ARM_CONCEPT_ENCODER recall@5 in [0.30, 0.60) OR
- (recall@5(CE) - max(baselines)) in (0.05, 0.15)
-> partial success; scope-tighten cell required before promotion.

## SCHEMA-VET fields (mandatory)

| Field | Value |
|-------|-------|
| cardinality_ok | true |
| EXPECTED_N_UNITS | SMOKE 4 (1 seed x 4 arms); FULL 12 (3 seeds x 4 arms) |
| arms_differ_verified | true (smoke gate hashes first 100 dims of first body HD per arm; all 4 must differ) |
| final_metrics_atomicity | tmp_replace |
| except SystemExit: raise BEFORE except Exception | true |
| crlb_floor_computed | n/a -- retrieval task; chance baseline recall@5 = 5/N articles = 0.0005 at N=10000; HP2=0.60 is well above chance and below Gate D (0.85) |
| crlb_n/a | "retrieval task; chance floor 5/N=0.0005 at N=10000; not a matmul CRLB problem" |
| discriminator_reachability | true -- BGE prior cell measured 0.992; HP2=0.60 is reachable-in-principle for the concept encoder (bridge from 0.05 chance to 0.85 bge) |
| baseline_in_band | true expected: char_positional and char_trigram predicted in [0.05, 0.60] (V1 surface has weak but non-zero title-body signal via char-overlap; trigram has stronger substring overlap) |
| HP_SCOPE | `{HP1: [ARM_BGE_LARGE_REFERENCE], HP2: [ARM_CONCEPT_ENCODER_ONESHOT], HP3: [ARM_CONCEPT_ENCODER_ONESHOT], HP4: [ARM_CONCEPT_ENCODER_ONESHOT], HP5: [ARM_BGE_LARGE_REFERENCE]}` |
| calibration_check | default_ok_for_this_regime -- ConceptEncoder inherits Spoke 1 v3-D CG defaults (k_sparsity=0.02, max_pos=24); N_DIM=8192 is scale_sentinel validated; N_CONCEPTS=10000 is 200x the CG regime (50) -- see calibration risk below |
| progress_logging | print_flush_true |
| cell_chunked | false -- single-seed loop in one file; seeds cheap for this task |
| start_marker_written | true |
| crash_diagnostic_present | true |
| heartbeat_present | true (arm-level; 4 arms) |
| defensive_error_checking | passed_all_4_patterns |
| sweep_alignment_verdict | ALIGNED -- no sweep, arms only |
| bracket_includes_discriminating_band | n/a -- no sweep |
| discriminating_fraction | n/a -- no sweep |

## Calibration risk (declared honestly)

- Spoke 1 v3-D CG regime: N_CONCEPTS=50, SPC=40. This test: N_CONCEPTS=10000 (200x), SPC=5 (8x fewer sentences per concept in FULL). The ConceptEncoder's competitive-Hebbian outer-product accumulator may saturate at N_CONCEPTS>>50 (dim-usage competition) or under-fit at SPC<10.
- Selftest 10 (scale sentinel N=8192, N_CONCEPTS=50) validates N_DIM extends. Does NOT validate N_CONCEPTS extends to 10000.
- If HF2 fires (concept encoder no advantage vs baselines), it may be a regime-extension failure of ConceptEncoder at 10K concepts NOT a fundamental mechanism failure. Verdict framing must call this out.
- Scope check: N=10000 articles * K=5 sentences * n_dim=8192 = 400M float32 ops for surface encoding -- 30-90 min CPU. FULL routes GPU.

## Composition edges (§15C)

Only one composition: `article_body_sentences -> ConceptEncoder.fit() -> concept_hds table -> ConceptEncoder.encode(title) via _classify`.
- Natural output of char_positional: bipolar surface HD [n_dim] float32
- Natural input of ConceptEncoder.fit: (sentences, integer labels)
- Verdict: SHAPE_MATCH (ConceptEncoder was designed to wrap char_positional).

## Compute architecture

Storage strategy: SHARDED for CONCEPT arm (concept_encoder module contract, per math4_v2 substrate physics law). NO storage for surface arms (direct encode + immediate similarity computation). BGE: NO storage (direct encode + matmul).

- ARM_BGE_LARGE_REFERENCE: batched-GPU (mandatory per GPU-batching rule; bge-large in bf16 batched=32).
- ARM_CONCEPT_ENCODER_ONESHOT: sequential-CPU for fit (per module docstring; each sentence updates one concept accumulator -- can't parallelize competitive-Hebbian across concepts without algorithm change); batched CPU matmul for retrieval.
- ARM_CHAR_POSITIONAL_ONLY: sequential-CPU per sentence (Python loop over words per encode_sentence).
- ARM_CHAR_TRIGRAM_UNSUP: sequential-CPU per sentence (Python loop over trigrams per encode).

Justification for sequential in surface arms:
- Per-sentence encoding is fast (~5-15 ms/sentence at N=8192).
- 10000 articles * 2 (title+body) = 20000 encodings * ~10ms = ~200s. Below the 10s trigger threshold does not apply; it IS above 10s total. But the sequential is a physics requirement of the mechanism (HRR bind is inside a Python loop per character position). Batching would require re-authoring the encoder module. Deferred.

## Functional requirements (§15E)

| # | Functional requirement | Existing primitive |
|---|-----------------------|--------------------|
| FR1 | Title text -> HD | ConceptEncoder._surface_encoder (char_positional) OR char_trigram OR bge-large |
| FR2 | Article body text -> HD | ConceptEncoder.fit(body_sentences, article_idx) OR char_positional.encode_sentence OR char_trigram.encode OR bge-large |
| FR3 | HD similarity for retrieval | Cosine over unit-normalized vectors |
| FR4 | recall@k over ranked scores | np.argsort |

All functional requirements map to existing primitives. No new mechanism required.

## Regime extension audit

- CE arm: CG regime N_CONCEPTS=50 SPC=40 -> test regime N_CONCEPTS=10000 SPC=5 = SHAPE_DRIFT_with_documented_risk (declared in calibration risk section).
- BGE arm: same regime as prior cell exp_wikipedia_ingest_100k_gpu_v1 (except N=10K vs 100K) = SHAPE_MATCH.
- Surface arms: no prior chain-grade result at test regime -> not a regime extension.

## Timeout

- SMOKE local CPU: 1800s (30 min) -- 500 articles, 1 seed, all 4 arms.
- FULL remote GPU: 10800s (3 hr) -- 10K articles, 3 seeds, all 4 arms. bge is bottleneck.

## Reference

- `d:/AI/hd-instrument/hdlab/concept_encoder.py` (commit e8f15a036 2026-07-02)
- `d:/AI/hd-instrument/hdlab/char_positional_encoder.py`
- `d:/AI/hd-instrument/hdlab/char_trigram_encoder.py`
- `d:/AI/hd-instrument/experiments/exp_wikipedia_ingest_100k_gpu_v1.py` (prior HP r@5=0.992 with bge-large)
- `d:/AI/hd-instrument/data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json` (prior HP evidence)

USER-authorized 2026-07-02 late evening: "do it" (Option A').
