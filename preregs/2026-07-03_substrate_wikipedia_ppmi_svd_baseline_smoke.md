# PRE-REG: substrate-native PPMI/SVD Wikipedia retrieval SMOKE (parallel to char-trigram HP)

**Anchor:** `substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03`
**Cell file:** `experiments/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026-07-03.py`
**Filed:** 2026-07-03 (USER-directed spawn: ATL-hub-analog PPMI/SVD parallel-probe to char-trigram Wikipedia HP)
**Author:** hdi_exp_dev
**Run mode:** SMOKE-only (no FULL variant filed).

## Question

Does a SUBSTRATE-NATIVE PPMI/SVD encoder (co-occurrence semantic reader; ATL-hub analog) beat the char-trigram surface bag baseline (r@5=0.854 MEASURED@ 2026-07-03) on real Wikipedia title -> body retrieval?

Or is Wikipedia already so bag-favorable that PPMI adds no signal above surface trigram?

Feeds strategic decision: is single-stream ATL-analog (PPMI alone) enough to lift Wikipedia retrieval above char-trigram, or does the substrate-native ingest require Spoke 1 v3-D composition (VWFA + PPMI late-combine) or Spoke 3 hippocampal consolidation?

## Framing discipline (LOAD-BEARING)

- Substrate has no general knowledge ingested (`feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`). PPMI is a MECHANISM PROBE on the SUPERVISED corpus-as-labeled-partition regime, not a capability claim.
- MECHANISM ANALOG vs TASK ANALOG (`feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`): fitting PPMI on 500 article bodies with article-index as concept label is a SUPERVISED regime (designer-supplied labels are the article indices; a real substrate ingest would need unsupervised discovery). HP here means "PPMI mechanism on supervised article-partition regime beats surface bag by discriminator margin at this smoke scale"; it does NOT mean "substrate understands Wikipedia."
- PPMI/SVD is ATL-hub analog for amodal semantic co-occurrence (Levy/Goldberg 2015 skip-gram-PPMI equivalence; SPOWV Faruqui 2015). Distinct brain-analog from VWFA surface reader (char-trigram).
- Char-trigram r@5=0.854 is a WELL-ESTABLISHED FLOOR (MEASURED@ commit a71920bbf, 2026-07-03). Not "substrate understanding" -- surface-bag exploits title-body trigram overlap. Question is whether ATL-hub-analog semantics adds signal ON TOP.

## Prior work check

Substrate-KB concept-query (2026-07-03) for "PPMI SVD wikipedia retrieval semantic co-occurrence real corpus":
- Rank 1 `entity='Real-corpus retrieval'` cosine=0.3564 (`notes/exp_dev_to_testbed_benchmark_suite_results_2026-06-08.md`; multi-arm benchmark harness discussion).
- Rank 2 `entity='Normal semantic retrieval'` cosine=0.335 (`notes/testbed_to_research_INDEX_ALGEBRA_VEC_EXTENSION_PROPOSAL_2026-06-11.md`; index algebra proposal).
- Rank 3 `entity='co-occurrence'` cosine=0.3125 (WordNet generic).
- Rank 4 `entity='3. temporal_wikipedia_ceo_retrieval_accuracy_v1'` cosine=0.2969 (temporal fact versioning hand-off).
- Rank 5 `entity='Retrieval'` cosine=0.29 (`notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md`).
- **Prior-work check: NONE at cosine > 0.30 for the specific substrate-native PPMI/SVD-on-real-Wikipedia probe.** Top hits are generic retrieval / semantic notes, not a prior PPMI Wikipedia mechanism probe. Cell is genuinely novel as a PPMI/SVD parallel-probe to the char-trigram Wikipedia HP.

Directly related prior cells consulted (this session):
- `experiments/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026-07-03.py` -- char-trigram Wikipedia SMOKE HP (r@5=0.854 MEASURED@ 2026-07-03 commit a71920bbf). Task/corpus/metrics BIT-IDENTICAL forked here; only encoder changes.
- `experiments/exp_substrate_composed_encoder_v3_smoke_2026-07-03.py` -- v3-composed WordNet smoke landed 2026-07-03 (`ARM_PPMI_ALONE` r@5 = MEASURED beats char-trigram +0.06 on WordNet single-word synonym task). PPMI-alone was a positive control there; here it becomes the LOAD_BEARING arm on Wikipedia multi-token task.
- `hdlab/ppmi_sparse_encoder.py::PPMISparseEncoder` -- fit + encode implementation reused as-is.

## Prior V2-A shrinkage precedent (informs HP-margin realism)

- V2-A (PPMI/SVD as one component) WordNet smoke +0.06 shrank to WordNet FULL +0.012 at N=500 (MIDDLE_BAND) -- discriminator narrowed at scale. Same risk here: at Wikipedia N=500 the surface bag is ALREADY at r@5=0.854 (high absolute; low headroom above bag). +0.03 HP margin is chosen as a tight-but-fair discriminator on the mechanism-adds-signal question, accepting real risk of MIDDLE_BAND landing.

## Test protocol

BIT-IDENTICAL to char-trigram Wikipedia SMOKE on task, corpus loader, and metric definitions. The ONLY substantive change is the encoder for `ARM_PPMI_SVD_WIKIPEDIA` (`ARM_CHAR_TRIGRAM_WIKIPEDIA` reproduces the char-trigram HP as a regression check; `ARM_RANDOM_BASELINE` is the chance floor).

1. Load 500 articles from `data/datasets/wikipedia_smoke_500.jsonl` (`{title, text}` per row).
2. Truncate each body to 800 chars (matches char-trigram cell BODY_CHAR_CAP).
3. **PPMI arm:** fit `PPMISparseEncoder(n_dim=2048, min_term_freq=2)` on 500 article bodies as 500 training sentences with concept_label = article index. Fit produces V x 500 co-occurrence -> PPMI -> SVD-reduce to effective_dim = min(V, 500, 2048) = 500, right-zero-padded to 2048. Then encode each body + each title with the fit encoder (dense output; trigram-embedding-sum). Cosine on unit-normalized dense HDs.
4. **Char-trigram arm:** REGRESSION CHECK; identical implementation to char-trigram cell. Must reproduce r@5 ~ 0.854.
5. **Random arm:** identical implementation to char-trigram cell. Must land in chance band.
6. Compute cosine similarity matrix `S[i, j] = cos(title[i], body[j])`.
7. `recall@k` = fraction of titles whose correct body index i is in top-k.

Regime:
- N articles: 500 (all of `wikipedia_smoke_500.jsonl`; `wc -l = 500` MEASURED).
- N_DIM: 2048 (matches char-trigram cell for direct comparison).
- Seeds: [11, 17, 23]. PPMI fit is deterministic on this corpus (SVD is deterministic given rows/cols order); random arm depends on seed. Per-seed std for PPMI expected ~ 0.
- Chance recall@5 = 5/500 = 0.01 THEORETICAL@.

## Arms

| Arm | Encoder | Training | HD dim | Compute |
|-----|---------|----------|--------|---------|
| ARM_PPMI_SVD_WIKIPEDIA | `hdlab.ppmi_sparse_encoder.PPMISparseEncoder` | fit on 500 bodies as (sentence, article_index) pairs | 2048 (effective 500) | Sequential CPU numpy SVD + per-text encode |
| ARM_CHAR_TRIGRAM_WIKIPEDIA | `hdlab.char_trigram_encoder.CharTrigramEncoder` (regression check) | none (deterministic hash) | 2048 | Sequential CPU per text |
| ARM_RANDOM_BASELINE | Random bipolar HDs | none | 2048 | numpy |

Per-arm retrieval:
- **ARM_PPMI_SVD_WIKIPEDIA:** fit encoder on bodies; `body_HD[i] = encoder.encode(body[i])`; `title_HD[i] = encoder.encode(title[i])`. Title trigrams that never appear in body training corpus are OOV and skipped. Cosine on unit-normalized HDs.
- **ARM_CHAR_TRIGRAM_WIKIPEDIA:** regression -- reproduce r@5 = 0.854 (MEASURED). If off by > 0.05, dispatch is untrustworthy.
- **ARM_RANDOM_BASELINE:** random bipolar. Sanity floor.

## Metrics (per arm x seed)

- `recall_at_1`, `recall_at_5`, `recall_at_10`
- `mean_reciprocal_rank`
- `intra_article_body_title_cos`, `inter_article_title_body_cos`, `signal_to_noise_ratio`
- `n_dim`, `encoding_wall_s`, `fit_wall_s` (PPMI only), `throughput_articles_per_sec`

Aggregate across seeds: mean + std.

## HP bands

`HP_SCOPE:`
- **LOAD_BEARING on ARM_PPMI_SVD_WIKIPEDIA** (mechanism probe -- primary question).
- **REGRESSION on ARM_CHAR_TRIGRAM_WIKIPEDIA** (must reproduce 0.854 +/- 0.05).
- **SANITY on ARM_RANDOM_BASELINE** (META_RULE_AG baseline_in_band; must land <= 0.05).

Reference constant: `char_trigram_reference = 0.854` MEASURED@ `data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json:per_arm_aggregate.ARM_CHAR_TRIGRAM_WIKIPEDIA.recall_at_5_mean`.

### HARD_PASS

| # | Metric | Threshold | Applies to |
|---|--------|-----------|------------|
| HP1 | recall@5 | >= char_trigram_reference + 0.03 = 0.884 | ARM_PPMI_SVD_WIKIPEDIA |
| HPreg | recall@5 | in [char_trigram_reference - 0.05, char_trigram_reference + 0.05] = [0.804, 0.904] | ARM_CHAR_TRIGRAM_WIKIPEDIA |

HP1 interpretation: PPMI-alone ATL-hub-analog encoder beats surface bag by a discriminator-margin margin at this smoke scale, tolerating typical smoke-scale noise. CG MECHANISM_LIFT tier claim on Wikipedia SUPERVISED regime.

### HARD_FAIL

| # | Condition | Implication |
|---|-----------|-------------|
| HF1 | ARM_PPMI_SVD_WIKIPEDIA recall@5 < char_trigram_reference - 0.03 = 0.824 | PPMI-alone loses to char-trigram on Wikipedia. ATL-hub-analog underperforms surface bag on multi-token real-corpus. Signal: composition (v3-D) or Spoke 3 hippocampal is needed; PPMI-alone insufficient. |
| HFreg | ARM_CHAR_TRIGRAM_WIKIPEDIA recall@5 outside [0.804, 0.904] | Regression check failed -- dispatch untrustworthy; investigate cell drift vs char-trigram cell of 2026-07-03. |
| HF2 | ARM_RANDOM_BASELINE recall@5 > 0.05 | META_RULE_AG baseline_in_band violation; implementation bug. |
| HFcard | actual_n_units < expected_n_units (3 arms x 3 seeds = 9) | META_RULE_H cardinality breach. |

### MIDDLE_BAND

ARM_PPMI_SVD_WIKIPEDIA recall@5 in [0.824, 0.884): mechanism within +/-0.03 of char-trigram floor. Neither clear lift nor clear loss. Signal: at N=500 Wikipedia the surface bag already captures most of the mechanism's headroom; composition may be genuinely needed for lift.

## Envelope-fail bands

- ARM_RANDOM_BASELINE recall@5 expected band: [0.0, 0.05]; chance = 0.01.
- ARM_CHAR_TRIGRAM_WIKIPEDIA recall@5 expected band: [0.804, 0.904] (regression floor).

## Compute architecture

Class `(b) sequential-CPU with justification`. Per-text encode is trivial numpy (sum term embeddings; 800 chars -> ~800 trigrams -> 800 vector adds). PPMI fit does one full SVD on V x C ~ 10K x 500 matrix -- ~1-5s. No batching needed; total smoke expected < 60s per seed.

Storage strategy: `no_composition` (no chain retrieval; single-hop cosine only).

## Selftests (`--self-test`)

1. `retrieval_metrics_identity` -- body=title gives r@1=1.0.
2. `random_chance_at_scale` -- random arm at N=200 x n_dim=2048 in [0, 5*chance].
3. `ppmi_encoder_fits_mini_corpus` -- fit encoder on 5-atom in-code mini corpus; ensure encoder builds vocab, term_embeddings non-None, encode(title) non-zero norm for at least 3/5 titles (some titles may have zero in-vocab trigrams; that's OK if not majority).
4. `arms_differ_mini` -- PPMI body HDs, char-trigram body HDs, random body HDs are hash-distinct.
5. `arg_parse_default_is_smoke` -- SMOKE-only discipline.

## Cell-template compliance

- `arms_differ_verified` (META_RULE_AF; hash on first-article body HD prefix across all 3 arms).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception`.
- `baseline_in_band` verified in verdict logic (META_RULE_AG; random arm).
- `cardinality_ok` (META_RULE_H).
- Per-unit `failure_class` (META_RULE_J).
- `start_marker_written`, `_heartbeat.jsonl`, crash-diagnostic write.
- Numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ (META_RULE_AC).
- Default `_parse_args()` = `smoke` (SMOKE-only cell).
- Print flush True + line-buffered stdout.

## Dispatch plan

- SMOKE via `local_cpu_queue` per USER-locked SMOKE-only-on-local discipline.
- **NO FULL variant filed. HOLD before any FULL dispatch.**
- Do NOT modify `backend/kb/wikipedia_ingest.py`. This is a parallel probe.

## Post-smoke reporting

Report per-arm r@5 mean, per-arm std, wall-time, throughput, PPMI vs char-trigram delta with honest scope. Do NOT claim "substrate understands Wikipedia" -- HP claim is mechanism-lift on SUPERVISED regime only.
