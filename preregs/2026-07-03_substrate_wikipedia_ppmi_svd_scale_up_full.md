# PRE-REG: substrate-native PPMI/SVD Wikipedia SCALE-UP (FULL, N=10K)

**Anchor:** `substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03`
**Cell file:** `experiments/exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026-07-03.py`
**Filed:** 2026-07-03 (preemptive authoring under Skunkworks approval; **HARD HOLD on dispatch** pending Director green-light)
**Author:** hdi_exp_dev
**Run mode:** FULL (N=10K); SMOKE variant reproduces N=500 parent-smoke PPMI r@5=0.906 lift as cell-integrity gate.

## HARD HOLD status

Cell is authored + smoke-gated on local commit ONLY. Do NOT dispatch to `remote_cpu_queue` until:

1. Char-trigram Wikipedia FULL 10K lands + is landed-VET'd (running on `cpu_runner_0` per commit `84c53803e`, ETA ~10min at time of authoring).
2. v3-composed Wikipedia multi-arm SMOKE lands + is landed-VET'd (per commit `0331d844d`).
3. Skunkworks confirms arm-set is not mis-scoped for the current strategic ordering.
4. Director explicitly green-lights dispatch to `remote_cpu_queue`.

Rationale: `cloud_gpu_once_per_stage` discipline extended to expensive `remote_cpu_queue` FULL runs. Dispatching FULL before char-trigram FULL 10K anchors the co-run reference number would burn a cycle on a possibly-mis-scoped arm-set.

## Amendment 2026-07-03 (post-timeout revision)

**Prior FULL run 2026-07-03 evening:** timed out at 1200s ceiling after seeds [11, 17] completed and seed 23 was mid-PPMI-fit. NO metrics.json was written because writes were end-of-run only. Preliminary from `_heartbeat.jsonl` (2/3 seeds; PPMI + trigram deterministic w.r.t. seed):
- `ARM_PPMI_SVD_WIKIPEDIA_N10K` r@5 = 0.6791 MEASURED@_heartbeat.jsonl (remote landing prior to kill)
- `ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K` r@5 = 0.7030
- Preliminary delta = -0.0239 (PPMI LOSES to char-trigram at N=10K real Wikipedia)

**Cell-quality DISCIPLINE_META note (cell-author side of the fence):** original pre-reg estimated ~140s PPMI fit wall (extrapolated 20x smoke ~7s). Actual measured PPMI arm wall ~415s/seed — 3x underestimate. Sparse-SVD fit-wall does not scale linearly in N under real Wikipedia term distributions (vocab grows superlinearly; SVD wall grows superlinearly in V). Estimation methodology error to memorialize.

**Two amendments applied to this cell:**

1. **Timeout bump 1200s -> 1800s.** Justification: measured PPMI arm wall 415s/seed x 3 seeds = 1245s PPMI-only + ~15s x 3 char-trigram + ~7s x 3 random + retrieval + load = ~1330s minimum. 1800s ceiling gives 30% margin.
2. **Per-seed checkpoint discipline** (SH-4-adjacent). Cell now writes `partial_metrics_<seed>.json` (via `experiments/_seed_checkpoint.write_partial`) after each seed completes, PLUS a partial-run `metrics.json` snapshot with `partial_run: true` flag. If a subsequent timeout kills mid-seed-N, work through seed N-1 is preserved AND a re-dispatch resumes from where killed via `resumable_seeds` PROT-021 config-mismatch guard (N + run_mode + anchor). This mirrors the `partial_seed{N}_full.json` pattern used in prior arcs.

**Preliminary evidence supports MEASURED_BOUND_LOW_DELTA prior for FULL verdict** (subject to seed-23 completion at scale + framing discipline; substrate-content HF pattern from 2026-07-02 predicted this behavior). If 3-seed FULL confirms PPMI < char-trigram delta near -0.02 at N=10K, this is a SUPPORT WITNESS for the substrate-content HF pattern (brain-analog concept_encoder LOSES to char-trigram bag on real content, absent VWFA-analog dense feature layer), NOT a novel-first. Framing discipline USER-locked: HF3 verdict is characterization CG only, not "PPMI fails at Wikipedia."

## Question

At N=10K (20x smoke scale), what is the substrate-native PPMI/SVD encoder's title -> article recall on real Wikipedia, and does the smoke +0.052 lift over char-trigram (0.854 -> 0.906) survive at scale?

META `TASK_CLASS_AND_MECHANISM_CLASS_MATCH` MM_TENTATIVE_SYNTHESIS expansion criterion (Skunkworks CG filed `b207d3d7f`): Wikipedia FULL 10K `delta_PPMI_vs_char_trigram >= +0.03` to preserve the MM claim at scale.

## Framing discipline (LOAD-BEARING per USER 2026-07-02)

- Substrate has no general knowledge ingested (`feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`).
- HP here = "PPMI mechanism-lift on this SUPERVISED regime at 10K scale." Does NOT mean "substrate understands Wikipedia."
- MECHANISM ANALOG != TASK ANALOG (`feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`).
- If FULL lands MB (delta in [+0.012, +0.03]), that is valuable characterization, not "PPMI fails."
- If FULL lands HP (delta >= +0.05), still MECHANISM CG on SUPERVISED regime, NOT capability.

Discriminator-narrows precedent (2026-07-02): V2-A WordNet smoke +0.06 shrank to +0.012 at 5x N. Naked PPMI Wikipedia FULL 10K carries MB-most-likely prior (Skunkworks estimated FULL delta in [+0.017, +0.026]).

## Prior work check

Substrate-KB concept-query (2026-07-03) for `PPMI SVD wikipedia scale up 10K`:
- Rank 1 `entity='scale_up'` cosine=0.3438 (wordnet gloss; generic).
- Rank 2 `entity='Scale'` cosine=0.2744 (prereg gloss; unrelated).
- Rank 3 `entity='scale'` cosine=0.2744 (verbnet/wordnet gloss; generic).
- Rank 4 `entity='wikipedia_ingest_100k_gpu_v1'` cosine=0.2598 (bge reference cell; different mechanism-class).
- Rank 5 `entity='Wikipedia-scale memory target'` cosine=0.2578 (research drill note; different concern).
- **Prior-work check: NONE at cosine > 0.30 for the specific substrate-native PPMI/SVD Wikipedia scaling probe.** Cell is novel as substrate-native PPMI/SVD scaling curve on real Wikipedia at 10K; no prior PPMI Wikipedia FULL cell.

Directly related prior artifacts:
- Parent PPMI smoke cell (this same code path at N=500): `experiments/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026-07-03.py` -- PPMI r@5=0.906 MEASURED@ `data/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03/metrics.json` (commit `b655b9fd3`).
- Companion char-trigram scale-up FULL 10K: `experiments/exp_substrate_wikipedia_char_trigram_scale_up_full_2026-07-03.py` (commit `84c53803e`; running on `cpu_runner_0`). Sampling policy VERBATIM-MATCHED by this cell.
- Skunkworks META atom (CG_MEASURED_BOUND) `TASK_CLASS_AND_MECHANISM_CLASS_MATCH` (`b207d3d7f` and prior).
- V2-A WordNet FULL precedent (discriminator-narrows-at-scale): smoke +0.06 -> FULL +0.012 at 5x N.
- bge 100K reference: `experiments/exp_wikipedia_ingest_100k_gpu_v1.py` -- r@5=0.992 MEASURED@ `data/exp_wikipedia_ingest_100k_gpu_v1/metrics.json`.

## Test protocol

Held-out title -> article retrieval on `data/datasets/wikipedia_100k.jsonl` (first 10K rows for FULL) / `data/datasets/wikipedia_smoke_500.jsonl` (first 500 rows for SMOKE reproduction). Sampling policy: streaming read of first N rows (VERBATIM-MATCHES char-trigram scale-up FULL for direct co-run comparability).

1. Load N articles (`{title, text}` per row); body truncated to 800 chars.
2. For each arm and each of 3 seeds, encode each article body -> body HD; each title -> title HD.
3. Compute cosine similarity `S[i,j] = cos(title_i, body_j)`.
4. Report `recall@{1,5,10}`, MRR, intra/inter cos, SNR, encoding wall, PPMI fit wall, throughput, PPMI diagnostics (V, effective_dim, title_oov).

Regime (FULL):
- N articles: 10000 (first 10K from `wikipedia_100k.jsonl`).
- N_DIM: 2048 (same as smoke for direct comparability).
- Seeds: [11, 17, 23]. PPMI + char-trigram are deterministic w.r.t. seed by construction; random arm depends on seed.
- Chance recall@5 = 5/10000 = 0.0005. THEORETICAL@ 5x-chance baseline band = 0.0025.

## Arms

| Arm | Encoder | HD dim | Compute | Role |
|-----|---------|--------|---------|------|
| ARM_PPMI_SVD_WIKIPEDIA_N10K | `hdlab.ppmi_sparse_encoder.PPMISparseEncoder` (n_dim=2048, min_term_freq=2, smoothing=0.75) | 2048 | Sequential CPU per text; SVD fit once per seed | LOAD_BEARING |
| ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K | `hdlab.char_trigram_encoder.CharTrigramEncoder` (deterministic bag-of-trigrams, sign-bundled) | 2048 | Sequential CPU per text | Co-run reference (must match FULL-scale char-trigram number on `cpu_runner_0`) |
| ARM_RANDOM_BASELINE_N10K | Random bipolar HDs from a seeded `np.random.default_rng` | 2048 | numpy in-process | Chance floor at larger N |

## Metrics (per arm x seed)

- `recall_at_1`, `recall_at_5`, `recall_at_10`
- `mean_reciprocal_rank`
- `intra_article_body_title_cos`, `inter_article_title_body_cos`, `signal_to_noise_ratio`
- `n_dim`, `encoding_wall_s`, `fit_wall_s`, `throughput_articles_per_sec`
- PPMI arm only: `ppmi_diag` = `{vocab_size, effective_n_dim, title_oov_count, title_oov_frac}`
- Trigram arm only: `n_unique_trigrams`

Aggregate top-level:
- `delta_from_smoke_r5_ppmi = ppmi_r5_mean - 0.906`
- `delta_from_smoke_r5_char_trigram = tri_r5_mean - 0.854`
- `delta_from_char_trigram_at_10K = ppmi_r5_mean - tri_r5_mean` (LOAD_BEARING scoring metric)

## HP bands (MEASURED_BOUND-style + delta tiering)

`HP_SCOPE:`
- `HP_MECHANISM_LIFT_LOAD_BEARING: [ARM_PPMI_SVD_WIKIPEDIA_N10K]`
- `MB_MECHANISM_CHARACTERIZATION: [ARM_PPMI_SVD_WIKIPEDIA_N10K]`
- `HF_BASELINE_IN_BAND: [ARM_RANDOM_BASELINE_N10K]`
- `CO_RUN_REFERENCE: [ARM_CHAR_TRIGRAM_WIKIPEDIA_N10K]` (no HP/HF gate applied; drift check only)

### EXPECTED_MEASURE_BAND

| # | Metric | Band | Applies to |
|---|--------|------|------------|
| MB_PPMI_R5 | PPMI recall@5 | in [0.80, 0.92] | ARM_PPMI_SVD_WIKIPEDIA_N10K |
| MB_DELTA_MIN | delta_ppmi_vs_char_trigram | >= +0.03 | LOAD_BEARING scoring metric |

Rationale: smoke PPMI r@5=0.906 at N=500 (MEASURED); 5-12% degradation from smoke is the expected physical range at 20x N (bundling-capacity saturation + PPMI SVD subspace narrowing + increased title/body ambiguity across 10K corpus). Upper band 0.92 catches suspicious over-performance; lower band 0.80 catches sharp collapse.

### HARD_PASS (delta-tiered)

| # | Condition | Verdict |
|---|-----------|---------|
| HP_DELTA | delta_ppmi_vs_char_trigram >= +0.05 | HARD_PASS_MECHANISM_LIFT (mechanism CG survives at 20x scale strongly) |

### MEASURED_BOUND (delta-tiered)

| # | Condition | Verdict |
|---|-----------|---------|
| MB_DELTA | delta in [+0.03, +0.05) | MEASURED_BOUND (mechanism CG survives; discriminator narrows partially; still meets META expansion criterion) |
| MB_DELTA_LOW | delta < +0.03 | MEASURED_BOUND_LOW_DELTA (discriminator narrows sharply; below META expansion criterion; still valuable characterization -- NOT capability failure) |

### INCONCLUSIVE

| # | Condition | Implication |
|---|-----------|-------------|
| INC1 | PPMI r@5 < 0.50 (INCONCLUSIVE_R5_LOWER=0.60 minus MARGIN=0.10) | Sharper-than-expected degradation. Signals encoder failure mode or task-shape shift at scale. Route to research. |
| INC2 | PPMI r@5 > 1.05 (INCONCLUSIVE_R5_UPPER=0.95 plus MARGIN=0.10; degenerate) | Suspiciously robust; verify against bge ref. Route to research. |

### HARD_FAIL (mechanism-invariant / cell-integrity)

| # | Condition | Implication |
|---|-----------|-------------|
| HF1 | ARM_RANDOM_BASELINE_N10K recall@5 > 0.0025 | META_RULE_AG baseline_in_band violation; retrieval-implementation bug; all r@5 numbers untrustworthy. |
| HFcard | actual_n_units < 9 (3 arms x 3 seeds) | META_RULE_H cardinality breach; one or more (seed, arm) units failed. |
| HFmiss | any arm has no r@5 metric | HARD_FAIL_ARM_MISSING; arm-level catastrophic failure. |

### Substrate-content HF gate (post-amendment 2026-07-03)

| # | Condition | Verdict |
|---|-----------|---------|
| HF3 | delta_ppmi_vs_char_trigram <= -0.010 at N=10K (PPMI loses to surface char-trigram bag) | MEASURED_BOUND_LOW_DELTA classified as SUPPORT WITNESS for substrate-content HF pattern (`feedback_concept_query_before_dispatch_would_have_predicted_substrate_content_HF_2026-07-02.md`). Verdict `MEASURED_BOUND_LOW_DELTA` covers this case in current cell logic; delta encoded in `delta_from_char_trigram_at_10K` metrics field. Framing: characterization CG (SUPERVISED Wikipedia regime), NOT "PPMI fails" — the encoder is a mechanism-lift probe, not a language-understanding claim. Preliminary 2/3-seed heartbeat evidence: delta = -0.0239 (aligns with predicted PPMI-loses-at-real-corpus behavior). |

Note: scoring is MEASURED_BOUND CHARACTERIZATION + delta tiering, not a pure capability threshold. Verdict tiers rank: `HARD_PASS_MECHANISM_LIFT` > `MEASURED_BOUND` > `MEASURED_BOUND_LOW_DELTA` > `INCONCLUSIVE_SCALE_SHAPE_SHIFT` > `HARD_FAIL_*`. HF3 is a MEASURED_BOUND_LOW_DELTA sub-classification: NOT a HARD_FAIL tier because the cell measured the substrate cleanly; the negative delta IS the load-bearing scientific outcome, not a bug.

## Compute architecture

Class: **(b) sequential-CPU with justification.**
- PPMI fit: one SVD per seed on term x concept co-occurrence matrix. At N=10K bodies, V ~= 10K-30K trigrams, C=10K labels; sparse matrix + truncated SVD to k=min(V, C, 2048). Estimated ~140s fit wall (20x smoke ~7s scaling; sparse SVD dominant).
- PPMI encode: per-text term-vector sum. Estimated ~12s encode wall at N=10K (20x smoke ~0.6s scaling).
- Per-seed total ~= 152s; 3 seeds x 2 arms + random ~= 8-12 min total. Well under 1200s ceiling.
- No genuine batch-GPU speedup available (sparse coo build + truncated SVD is memory-bound; matmul at N=10K x N_DIM=2048 trivial for numpy).
- Sequential-CPU is the correct choice.

Storage strategy: **no_storage / no_composition.** Cell is single-hop retrieval (title HD -> nearest body HD). No downstream composition; no cross-item bundling; no chain-grade primitive invocation. `sharded-vs-bundled` META rule does NOT apply.

## Envelope-fail bands

- ARM_RANDOM_BASELINE_N10K recall@5 expected band: [0.0, 0.0025]. Chance = 5/10000 = 0.0005. Band cap 5x chance = 0.0025.
- HF1 fires if observed > 0.0025.

## Dispatch plan

- **Pre-flight smoke gate (LOCAL):** run cell with `--smoke` flag (uses `wikipedia_smoke_500.jsonl` present on local disk). Verify PPMI r@5 at N=500 matches parent PPMI smoke (0.906 MEASURED) within 0.02 tolerance and delta_vs_char_trigram matches parent smoke (+0.052 MEASURED) within 0.01 tolerance. This certifies cell integrity + code-path equivalence BEFORE FULL dispatch. META rule "smoke code path exercises same branches as FULL" is satisfied by identical arm implementations + retrieval + verdict logic; the FULL/SMOKE branch differs ONLY in `dataset_path` + `n_articles_target` constant.
- **FULL dispatch:** `remote_cpu_queue` (marsh@home). The 100K wikipedia dataset lives on the remote runner host (not present on local disk); FULL cannot run locally. Measured wall (from prior 2026-07-03 timeout run): PPMI arm ~415s/seed x 3 = 1245s + char-trigram ~15s x 3 = 45s + random ~7s x 3 = 21s + load/retrieval overhead ~50s = ~1360s total. Recommend `timeout_s=1800` (30 min) for 30% margin over measured wall.
- **HARD HOLD:** cell-author authorized to author + smoke-gate ONLY. Push + queue_add gated on Director explicit green-light after char-trigram FULL 10K lands + v3-composed multi-arm SMOKE lands + landed-VET.
- **Requires push to origin/main** (harness-denied to exp_dev). Author files locally + commit; caller (Director / Orchestrator) pushes + runs (on green-light): `bash tools/orchestrator/queue_add.sh remote_cpu_queue substrate_wikipedia_ppmi_svd_scale_up_full_2026_07_03 experiments/exp_substrate_wikipedia_ppmi_svd_scale_up_full_2026-07-03.py preregs/2026-07-03_substrate_wikipedia_ppmi_svd_scale_up_full.md 1800`.
- **Per-seed checkpoint:** cell writes `partial_metrics_<seed>.json` after each seed + partial-run `metrics.json` snapshot. Timeout kill mid-seed-N preserves completed seeds 0..N-1. Re-dispatch resumes remaining seeds via `resumable_seeds` PROT-021 config-mismatch guard (N + run_mode + anchor stamped in each partial).

## Cell-template compliance

- `arms_differ_verified` at smoke gate (META_RULE_AF; hash-check on first-article body HD prefix across all 3 arms).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception` in per-arm driver + `__main__` (Sec 8 ordering).
- `baseline_in_band` verified in verdict logic at RUNTIME N (META_RULE_AG).
- `cardinality_ok` = actual_n_units >= expected_n_units (9 = 3 arms x 3 seeds).
- Per-unit `failure_class` instrumentation (META_RULE_J).
- `start_marker_written`, `_heartbeat.jsonl`, crash-diagnostic write (Sec 13).
- Numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ (META_RULE_AC).
- Default `_parse_args()` mode is `full` (no silent smoke downgrade); explicit `--smoke` or `HDLAB_RUN_MODE=smoke` needed for smoke reproduction. Env-var contract: `os.environ.get("HDLAB_RUN_MODE", None)` with `None` fallback to `full`, NOT hardcoded default `"smoke"`.
- Selftest: `arg_parse_default_is_full` verifies no-flag/no-env default is `full`.
- `progress_logging: "print_flush_true"` + line-buffered stdout (Sec 17). Cell timeout 1800s (30-min bracket); heartbeat + flushed prints per Sec 17 mandate for `timeout_s >= 1800`.

## Selftests (`--self-test`)

1. `retrieval_metrics_identity`: body=title -> r@1=1.0.
2. `random_chance_at_scale`: random bipolar HDs at N=200 x n_dim=2048 -> r@5 in chance band.
3. `ppmi_encoder_fits_mini_corpus`: 5-article mini corpus PPMI fit + encode; r@5 >= 0.6.
4. `arms_differ_mini`: PPMI + char-trigram + random body HDs on mini corpus hash-differ; no NaN.
5. `arg_parse_default_is_full`: `_parse_args()` returns `"full"` when no flag/env is provided.

## SCHEMA-VET fields

- `cardinality_ok: true` (EXPECTED_N_UNITS = 9 = 3 arms x 3 seeds).
- `arms_differ_verified: true` (smoke gate; hash-check across 3 arms).
- `final_metrics_atomicity: "tmp_replace"`.
- `progress_logging: "print_flush_true"`.
- `cell_chunked: false` (single-file cell; 3 seeds run in-process; per-seed independence via encoder-instance recreation). Per-seed checkpoint applied via `write_partial` after each seed completes; `resumable_seeds` PROT-021 config-mismatch guard on N/run_mode/anchor at start-of-run.
- `per_seed_checkpoint: true` (partial_metrics_<seed>.json + partial-run metrics.json snapshot per seed).
- `resumable: true` (via `_seed_checkpoint.resumable_seeds` with run_config={N, run_mode, anchor}).
- `start_marker_written: true`.
- `crash_diagnostic_present: true`.
- `heartbeat_present: true`.
- `defensive_error_checking: "passed_all_4_patterns"`.
- `calibration_check: "default_ok_for_this_regime"` (PPMI defaults match smoke; smoke MEASURED r@5=0.906 is within-band demonstration).
- `discriminator_reachability: true` (PPMI smoke lift +0.052 already MEASURED; question is scale survival).
- `baseline_in_band: true` (verified at smoke and FULL via RUNTIME chance-r5 calculation).
- `crlb_n/a: "retrieval task; no scalar noise-floor; discriminator is empirical delta between mechanism vs surface-bag arm at MATCHED regime."`

## Post-FULL gating

Report per-arm r@5 mean + std, per-seed r@5, wall + throughput, PPMI diagnostics (V, effective_dim, title_oov), `delta_from_smoke_r5_ppmi`, `delta_from_smoke_r5_char_trigram`, `delta_from_char_trigram_at_10K`. Verdict feeds strategic decision:

- `HARD_PASS_MECHANISM_LIFT` (delta >= +0.05): META `TASK_CLASS_AND_MECHANISM_CLASS_MATCH` MM firmed; PPMI/SVD is LOAD_BEARING substrate-native encoder for supervised-Wikipedia regime at scale.
- `MEASURED_BOUND` (delta in [+0.03, +0.05)): META expansion criterion met; discriminator survives partially; v3-composed or Spoke 3 needed for further lift.
- `MEASURED_BOUND_LOW_DELTA` (delta < +0.03): discriminator narrows below META criterion; PPMI lift does NOT survive 20x scale on real Wikipedia; MECHANISM CHARACTERIZATION only; route to research for v3-composed VWFA + late-combine or Spoke 3 hippocampal consolidation pathway analysis.

Route verdict to hdi_research + hdi_skunkworks for landed-VET + atomization.
