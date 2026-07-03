# PRE-REG: substrate-native char-trigram Wikipedia SCALE-UP (FULL, N=10K)

**Anchor:** `substrate_wikipedia_char_trigram_scale_up_full_2026_07_03`
**Cell file:** `experiments/exp_substrate_wikipedia_char_trigram_scale_up_full_2026-07-03.py`
**Filed:** 2026-07-03 (Skunkworks landed-VET on smoke recommended parallel HIGH_EV scaling probe)
**Author:** hdi_exp_dev
**Run mode:** FULL (N=10K); SMOKE variant reproduces N=500 parent-smoke as cell-integrity gate.

## Question

At N=10K (20x smoke scale), what is the char-trigram bag-of-HD substrate-native encoder's title -> article recall on real Wikipedia, and how does it compare to the smoke floor at N=500 (r@5=0.854 MEASURED)? This SETS THE SCALING CURVE for the substrate-native surface encoder floor -- it is characterization, not a capability threshold.

Skunkworks strategic framing (from landed-VET on smoke): "cheap, HIGH_EV number -- whether char-trigram degrades modestly (v3-composed needs justification) or sharply (Spoke 3 becomes load-bearing)."

## Framing discipline (LOAD-BEARING)

- Substrate has no general knowledge ingested (`feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`). Char-trigram bag is a MECHANISM PROBE at supervised-Wikipedia regime, NOT a capability claim.
- bge reference (`data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json`, 2026-06-19): r@5=0.992 at N=100K. FLOOR-CHECK / ceiling reference only. NOT re-run in this cell.
- Discriminator-narrows precedent from V2-A (2026-07-02): smoke edge +0.06 shrank to +0.012 at 5x N. A similar shrink here would indicate the smoke over-stated char-trigram capacity by a substantial fraction.
- Encoder-collision channel: at N=500 char-trigram HDs are distinct (r@5=0.854 MEASURED); at N=10K, the physical collision channel is the bundling capacity (~K trigrams summed into N_DIM=2048 buckets under sign()) not the seed hash. THEORETICAL@ birthday-collision on 32-bit blake2b seeds is <=1.2e-5 at K=10K unique trigrams; essentially zero at either scale.

## Prior work check

Substrate-KB concept-query (2026-07-03) for `char trigram scaling wikipedia hash collision`:
- Top hit `entity='collision'` cosine=0.3086 (wordnet gloss; generic).
- Rank 2 `entity='scaling'` cosine=0.2725 (wordnet gloss; generic).
- Rank 3 `entity='Explanation 4: Hash collision (predicate vector collision in bipolar index)'` cosine=0.2627 (`notes/research_drill_predicate_routing_scaling_limit_2x_2026-06-07.md`).
- Rank 4 `entity='collision.n'` cosine=0.2588 (framenet).
- Rank 5 `entity='trigram'` cosine=0.2461 (wordnet).
- **Prior-work check: NONE at cosine > 0.30 for the specific substrate-native char-trigram Wikipedia scaling probe.** Rank 3 predicate-routing hit is about bipolar-index predicate collisions (different mechanism-class). Cell is novel as a substrate-native scaling curve for the char-trigram surface encoder floor on real Wikipedia.

Directly related prior artifacts:
- Parent smoke cell (this same code path at N=500): `experiments/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026-07-03.py` -- r@5=0.854 MEASURED@ `data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json`.
- bge 100K reference: `experiments/exp_wikipedia_ingest_100k_gpu_v1.py` -- r@5=0.992 MEASURED@ `data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json`.
- Substrate-content HF (2026-07-02): brain-analog concept_encoder LOSES to char-trigram bag on real substrate content. This cell probes whether char-trigram's advantage generalizes to real Wikipedia at 10K scale.

## Test protocol

Held-out title -> article retrieval on `data/datasets/wikipedia_100k.jsonl` (first 10K rows for FULL) / `data/datasets/wikipedia_smoke_500.jsonl` (first 500 rows for SMOKE reproduction):

1. Load N articles (`{title, text}` per row); body truncated to 800 chars.
2. For each arm and each of 3 seeds, encode each article body -> body HD; each title -> title HD.
3. Compute cosine similarity `S[i,j] = cos(title_i, body_j)`.
4. Report `recall@{1,5,10}`, MRR, intra/inter cos, SNR, wall, throughput, `n_unique_trigrams` per seed (mechanism diagnostic).

Regime (FULL):
- N articles: 10000 (first 10K from `wikipedia_100k.jsonl`).
- N_DIM: 2048 (same as smoke for direct comparability).
- Seeds: [11, 17, 23]. Char-trigram is deterministic w.r.t. seed by construction; random arm depends on seed.
- Chance recall@5 = 5/10000 = 0.0005. THEORETICAL@ 5x-chance baseline band = 0.0025.

## Arms

| Arm | Encoder | HD dim | Compute |
|-----|---------|--------|---------|
| ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K | `hdlab.char_trigram_encoder.CharTrigramEncoder` (deterministic bag-of-trigrams, sign-bundled) | 2048 | Sequential CPU per text |
| ARM_RANDOM_BASELINE_N10K | Random bipolar HDs from a seeded `np.random.default_rng` | 2048 | numpy in-process |

## Metrics (per arm x seed)

- `recall_at_1`, `recall_at_5`, `recall_at_10`
- `mean_reciprocal_rank`
- `intra_article_body_title_cos`, `inter_article_title_body_cos`, `signal_to_noise_ratio`
- `n_dim`, `encoding_wall_s`, `throughput_articles_per_sec`
- (trigram only) `n_unique_trigrams`, `seed_hash_collision_probability_estimate`

Aggregate: mean + std across seeds for each; report `delta_from_smoke_r5 = tri_r5_mean - 0.854`, `gap_to_bge_100k_ref_r5 = 0.992 - tri_r5_mean`.

## HP bands (MEASURED_BOUND-style, not pass/fail capability)

`HP_SCOPE: MEASURED_BOUND on ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K (scaling characterization); ARM_RANDOM_BASELINE_N10K is a sanity control (META_RULE_AG baseline_in_band).`

### EXPECTED_MEASURE_BAND

| # | Metric | Band | Applies to |
|---|--------|------|------------|
| MB1 | recall@5 | in [0.60, 0.90] | ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K |

Rationale: smoke r@5=0.854 at N=500 (MEASURED); 5-30% degradation from smoke is the expected physical range at 20x N (bundling-capacity saturation + increased title/body ambiguity across 10K corpus). Upper band 0.90 catches suspicious over-performance; lower band 0.60 catches sharp collapse.

### INCONCLUSIVE

| # | Condition | Implication |
|---|-----------|-------------|
| INC1 | r@5 < 0.50 (band lower minus INCONCLUSIVE_MARGIN=0.10) | Sharper-than-expected degradation. Signals encoder failure mode or task-shape shift at scale; Spoke 3 hippocampal consolidation likely LOAD_BEARING for substrate-native ingest. Route to research. |
| INC2 | r@5 > 1.00 (band upper plus INCONCLUSIVE_MARGIN=0.10; degenerate) | Suspiciously robust; verify against bge ref. Route to research. |

### HARD_FAIL (mechanism-invariant / cell-integrity)

| # | Condition | Implication |
|---|-----------|-------------|
| HF1 | ARM_RANDOM_BASELINE_N10K recall@5 > 0.0025 | META_RULE_AG baseline_in_band violation; retrieval-implementation bug; all r@5 numbers untrustworthy. |
| HFcard | actual_n_units < 6 (2 arms x 3 seeds) | META_RULE_H cardinality breach; one or more (seed, arm) units failed. |

Note: scoring is MEASURED_BOUND CHARACTERIZATION of the scaling curve, not pass/fail against a capability threshold. `MEASURED_BOUND` verdict for expected-band; `MEASURED_BOUND_EDGE` for outside-band but inside INCONCLUSIVE_MARGIN buffer.

## Compute architecture

Class: **(b) sequential-CPU with justification.** CharTrigramEncoder is a per-text sequential loop over overlapping trigrams (Python; ~microseconds per trigram; ~1-2ms per article at BODY_CHAR_CAP=800). Smoke measured ~349 art/sec MEASURED@ smoke metrics. FULL 10K x 3 seeds = 30K article encodes (~90s wall + retrieval matmul); well under the 10s-per-phase-point batching threshold on a per-seed basis and no genuine batch-GPU speedup available (bag-sum + sign is memory-bound; matmul step at N=10K x N_DIM=2048 is trivial for numpy). Sequential-CPU is the correct choice.

Storage strategy: **no_storage / no_composition.** Cell is single-hop retrieval (title HD -> nearest body HD). No downstream composition; no cross-item bundling; no chain-grade primitive invocation. §sharded-vs-bundled META rule does NOT apply.

## Envelope-fail bands

- ARM_RANDOM_BASELINE_N10K recall@5 expected band: [0.0, 0.0025]. Chance = 5/10000 = 0.0005. Band cap 5x chance = 0.0025.
- HF1 fires if observed > 0.0025.

## Dispatch plan

- **Pre-flight smoke gate:** locally run cell with `--smoke` flag (uses `wikipedia_smoke_500.jsonl` present on local disk). Verify r@5 at N=500 matches parent smoke (0.854 MEASURED) within 0.02 tolerance. This certifies cell integrity + code-path equivalence BEFORE FULL dispatch. META rule "smoke code path exercises same branches as FULL" is satisfied by identical arm implementations + retrieval + verdict logic; the FULL/SMOKE branch differs ONLY in `dataset_path` + `n_articles_target` constant.
- **FULL dispatch:** `remote_cpu_queue` (marsh@home). The 100K wikipedia dataset lives on the remote runner host (not present on local disk); FULL cannot run locally. Estimated wall: 10K articles x 3 seeds / ~349 art/sec = ~86s per seed = ~260s + retrieval + overhead. Recommend `timeout_s=1200` (20 min) for comfortable margin on slower remote CPU.
- **Requires push to origin/main** (harness-denied to exp_dev). Author files locally + commit; caller (Director / Orchestrator) pushes + runs `bash tools/orchestrator/queue_add.sh remote_cpu_queue substrate_wikipedia_char_trigram_scale_up_full_2026_07_03 experiments/exp_substrate_wikipedia_char_trigram_scale_up_full_2026-07-03.py preregs/2026-07-03_substrate_wikipedia_char_trigram_scale_up_full.md 1200`.

## Cell-template compliance

- `arms_differ_verified` at smoke gate (META_RULE_AF; hash-check on first-article body HD prefix).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception` in per-arm driver + `__main__` (§8 ordering).
- `baseline_in_band` verified in verdict logic at RUNTIME N (META_RULE_AG).
- `cardinality_ok` = actual_n_units >= expected_n_units.
- Per-unit `failure_class` instrumentation (META_RULE_J).
- `start_marker_written`, `_heartbeat.jsonl`, crash-diagnostic write (§13).
- Numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ (META_RULE_AC).
- Default `_parse_args()` mode is `full` (no silent smoke downgrade); explicit `--smoke` or `HDLAB_RUN_MODE=smoke` needed for smoke reproduction. Env-var contract: `os.environ.get("HDLAB_RUN_MODE", None)` with `None` fallback to `full`, NOT hardcoded default `"smoke"`.
- Selftest: `arg_parse_default_is_full` verifies no-flag/no-env default is `full`.
- `progress_logging: "print_flush_true"` + line-buffered stdout (§17). Cell timeout <1800s but heartbeat + flushed prints included for defense-in-depth.

## Selftests (`--self-test`)

1. `retrieval_metrics_identity`: body=title -> r@1=1.0.
2. `random_chance_at_scale`: random bipolar HDs at N=200 x n_dim=2048 -> r@5 in chance band.
3. `mini_arms_differ`: char-trigram r@1 >= 0.20 on 5-article mini corpus; random r@5 = 1.0 (all in top-5 of N=5); arm hashes distinct.
4. `arg_parse_default_is_full`: `_parse_args()` returns `"full"` when no flag/env is provided.

## Post-FULL gating

Report per-arm r@5 mean + std, per-seed r@5, wall + throughput, `delta_from_smoke_r5`, `gap_to_bge_100k_ref_r5`, `n_unique_trigrams` mean. Verdict = MEASURED_BOUND scaling characterization -- feeds strategic decision on whether v3-composed encoder needs justification to replace char-trigram floor (if degrades modestly) or whether Spoke 3 hippocampal consolidation is load-bearing (if degrades sharply). Route verdict to hdi_research + hdi_skunkworks for landed-VET + atomization.
