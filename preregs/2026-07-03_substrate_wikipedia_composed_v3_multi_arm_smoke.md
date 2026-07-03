# Pre-reg: substrate wikipedia composed v3 multi-arm SMOKE (2026-07-03)

## Anchor

`substrate_wikipedia_composed_v3_multi_arm_smoke_2026_07_03`

## Cell path

`experiments/exp_substrate_wikipedia_composed_v3_multi_arm_smoke_2026-07-03.py`

## Motivation (LOAD-BEARING framing)

Skunkworks-recommended optimal-info probe: single 5-arm cell delivers 4 findings simultaneously on the Wikipedia (title -> body retrieval) regime.

Prior context:
- Wikipedia char-trigram SMOKE HP: r@5=0.854
  MEASURED@ `data/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03/metrics.json:per_arm_aggregate.ARM_CHAR_TRIGRAM_WIKIPEDIA.recall_at_5_mean` (commit `43ec44a50`).
- Wikipedia PPMI/SVD SMOKE HP: r@5=0.906 (+0.052 lift)
  MEASURED@ `data/exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026_07_03/metrics.json:per_arm_aggregate.ARM_PPMI_SVD_WIKIPEDIA.recall_at_5_mean` (commit `b655b9fd3`).
- v3-composed WordNet SMOKE HF (equal-alpha dilutes asymmetric-strength streams; Skunkworks META
  MM_TENTATIVE_SYNTHESIS at commit `cc1807726`).
- 5x drill 5/5 (2026-07-02): VWFA HRR position-binding underperforms on single-token queries but
  predicted to earn keep on multi-token bodies where phrase-position IS load-bearing.
- v3-composed encoder module: `hdlab/composed_encoder_v3.py` (13/13 selftests PASS; commit `114a0f3cf`).

Framing discipline (USER-locked; 3 Fix#28 hits today):
- SUBSTRATE KNOWS ALMOST NOTHING: this is a MECHANISM COMPOSITION test on the SUPERVISED Wikipedia
  regime; NOT a capability claim.
- MECHANISM ANALOG != TASK ANALOG per
  `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`.
- Discriminator-narrows-at-scale caveat applies (V2-A precedent: smoke +0.06 -> FULL +0.012).
- No "first-ever" without precedent grep (grep clean below).
- No "physics law": smoke-scale mechanism CHARACTERIZATION only.
- HF on composition = stronger structural finding across task classes (WordNet + Wikipedia both
  show dilution) NOT rescue-required.

## Question

Four questions, tested in one cell:
1. Does composition earn keep on multi-token (V3 vs best-single)?
2. Does VWFA earn keep on multi-token (VWFA vs char-trigram baseline)?
3. Does PPMI-alone reproduce cross-cell (0.906 sanity)?
4. Does char-trigram reproduce cross-cell (0.854 sanity)?

## Prior-work check (grep experiments/)

Prior cells matching "composed*(vwfa|ppmi|wiki)" and "wikipedia":

- `exp_substrate_composed_encoder_v3_smoke_2026-07-03.py` (WordNet, NOT Wikipedia; HF equal-alpha).
- `exp_substrate_composed_encoder_v3_adaptive_alpha_smoke_2026-07-03.py` (WordNet; adaptive-alpha probe).
- `exp_substrate_wikipedia_char_trigram_baseline_smoke_2026-07-03.py` (char-trigram alone; HP 0.854).
- `exp_substrate_wikipedia_char_trigram_scale_up_full_2026-07-03.py` (FULL scale-up variant).
- `exp_substrate_wikipedia_ppmi_svd_baseline_smoke_2026-07-03.py` (PPMI/SVD alone; HP 0.906).
- `exp_substrate_wikipedia_layer15_cache_extraction_v1.py` (unrelated).
- `exp_wikipedia_ingest_*_gpu_v1.py` (bge-large ingest infra; unrelated).

No prior "composed VWFA+PPMI on Wikipedia" cell exists. Novel probe on this regime. Not a first-ever
mechanism claim (composition primitive already probed on WordNet; on Wikipedia it is a task-class
generalization test).

Substrate-KB concept-query top hits at cosine>=0.30:
- `ARM_PIPELINE_COMPOSED` (prereg, cosine 0.3486, unrelated stage3 device demo)
- `combine` (VerbNet/WordNet entity, cosine 0.3398, dictionary sense)
- (all below 0.30) confirms novel on this regime.

## Arms (5 arms x 3 seeds = 15 units)

- `ARM_V3_COMPOSED_EQUAL_ALPHA` (LOAD-BEARING) - `hdlab.composed_encoder_v3.ComposedEncoderV3(n_dim=2048, alpha=0.5, beta=0.5)` fit on
  bodies with `labels=arange(N)`, retrieved via `retrieve_topk(title, k=10)`.
  Primary probe of composition on multi-token Wikipedia regime.
- `ARM_VWFA_ALONE` - `hdlab.vwfa.VWFAEncoder(n_dim=2048, scales=(1,2,3,4), bind_position=True)`
  encoding body + title as sentence-bag; retrieval via cosine title-vs-body table.
  Direct test of drill 5 prediction that VWFA earns keep on multi-token bodies.
- `ARM_PPMI_ALONE` (regression check) - `hdlab.ppmi_sparse_encoder.PPMISparseEncoder(n_dim=2048,
  min_term_freq=2, smoothing=0.75, seed=<seed>)` fit + encode identical to standalone cell.
  MUST reproduce PPMI Wikipedia r@5=0.906 within +/- 0.005.
- `ARM_CHAR_TRIGRAM_UNSUP_REFERENCE` (regression check) - `hdlab.char_trigram_encoder.CharTrigramEncoder(n_dim=2048)`
  identical to standalone cell.
  MUST reproduce char-trigram Wikipedia r@5=0.854 within +/- 0.001.
- `ARM_RANDOM_BASELINE` - random bipolar HDs (chance floor).

## Corpus + task (mirror ppmi cell VERBATIM for direct comparability)

- Corpus: `data/datasets/wikipedia_smoke_500.jsonl` (500 articles).
- Task: title -> body retrieval; each query is an article title, gold is its own body index.
- `N_DIM = 2048`, `N_ARTICLES = 500`, `BODY_CHAR_CAP = 800` (matches ppmi + trigram cells).
- Seeds: `[11, 17, 23]` (matches ppmi + trigram cells).

## HP / MB / HF bands (per arm; strict-above-floor per META_RULE_L)

Reference constants MEASURED@:
- `PPMI_REFERENCE_R5 = 0.906` (Wikipedia PPMI standalone smoke aggregate)
- `CHAR_TRIGRAM_REFERENCE_R5 = 0.854` (Wikipedia char-trigram standalone smoke aggregate)

HP scope:

- HP1 (composition earns keep; LOAD-BEARING) - `ARM_V3_COMPOSED_EQUAL_ALPHA.r@5 >= 0.936`
  (PPMI_ref + 0.03 discriminator margin).
- HP2 (VWFA earns keep on multi-token; LOAD-BEARING) - `ARM_VWFA_ALONE.r@5 >= 0.884`
  (char_trigram_ref + 0.03 discriminator margin).
- HP3 (PPMI reproduction sanity) - `ARM_PPMI_ALONE.r@5 in [0.901, 0.911]`
  (PPMI_ref +/- 0.005; deterministic PPMI-fit + same seeds).
- HP4 (char-trigram reproduction sanity) - `ARM_CHAR_TRIGRAM_UNSUP_REFERENCE.r@5 in [0.853, 0.855]`
  (char_trigram_ref +/- 0.001; hash-codebook determinism).
- HP5 (chance floor) - `ARM_RANDOM_BASELINE.r@5 <= 0.05`.

HF scope:

- HF1 (composition strictly hurts across task classes; stronger structural finding) -
  `ARM_V3_COMPOSED_EQUAL_ALPHA.r@5 < max(ARM_VWFA_ALONE.r@5, ARM_PPMI_ALONE.r@5) - 0.01`.
  Would generalize the WordNet dilution finding across task classes.
- HF-BASELINE (chance breach) - `ARM_RANDOM_BASELINE.r@5 > 0.05` (implementation bug).
- HF-REG-PPMI - `|ARM_PPMI_ALONE.r@5 - 0.906| > 0.005` (dispatch untrustworthy vs standalone cell).
- HF-REG-TRIGRAM - `|ARM_CHAR_TRIGRAM_UNSUP_REFERENCE.r@5 - 0.854| > 0.001` (dispatch untrustworthy).

MB scope:

- MB-COMPOSED - `ARM_V3_COMPOSED_EQUAL_ALPHA.r@5 in [PPMI_alone, PPMI_alone + 0.03)`;
  composition helps but by less than discriminator margin (consistent with V2-A smoke-narrows-at-full lesson).

## HP_SCOPE per-arm mapping

```
HP1_LOAD_BEARING     : [ARM_V3_COMPOSED_EQUAL_ALPHA]
HP2_LOAD_BEARING     : [ARM_VWFA_ALONE]
HP3_REGRESSION_PPMI  : [ARM_PPMI_ALONE]
HP4_REGRESSION_TRIGRAM : [ARM_CHAR_TRIGRAM_UNSUP_REFERENCE]
HP5_baseline_in_band : [ARM_RANDOM_BASELINE]
HF1_COMPOSITION_HURTS : [ARM_V3_COMPOSED_EQUAL_ALPHA]
```

## Selftests (minimum 5)

1. `retrieval_metrics_identity` - identity of body-title -> r@k=1.0.
2. `random_chance_at_scale` - random arm at N=200 x n_dim=2048 lands in chance band.
3. `composed_v3_retrieves_on_mini_corpus` - ComposedEncoderV3 at n_dim=2048 alpha=0.5 beta=0.5
   retrieves >= 4/5 on the composed_encoder_v3 toy corpus (same as its selftest 4). Sanity link to
   upstream module's 13/13 PASS.
4. `arms_differ_mini` - all 5 encoder outputs hash-differ on the mini corpus body table.
5. `scale_sentinel_n8192` - ComposedEncoderV3 at n_dim=8192 still passes fit + encode + retrieve
   on mini corpus (mirror composed_v3 selftest 10).
6. `arg_parse_default_is_smoke` - default run_mode is smoke.
7. `formula_identity_alpha_1_equals_vwfa_alone_in_composed_stream` - composed at alpha=1, beta=0
   produces the same top-1 as pure-VWFA argmax on the mini corpus (delegates to composed_v3's
   own formula-identity selftest).

## Env-var contract check (per SMOKE code-path exercises same branches as FULL META rule)

- Cell has ONE code path for smoke and would-be full: `SEEDS`, `N_ARTICLES`, `N_DIM` are cell
  constants and never differ across modes. Only `run_mode` field in metrics differs, plus this cell
  refuses non-smoke mode (SMOKE-only cell). This satisfies META rule since no branch behavior
  changes with mode.

## Compute architecture (per GPU-batching-mandatory rule)

- Class: **(c) mixed with justification**. PPMI/SVD fit + encode is pure numpy on 500 x 2048
  which runs 10-30s on CPU total; VWFA encode iterates chars per word which is also CPU-bound
  numpy; ComposedEncoderV3 sums the two. All arms are CPU-side numpy < 10s per arm per seed.
  Total wall <= 15 min on local_cpu.
- Storage strategy: `no_composition` (retrieval is single-hop title -> body cosine argmax over
  proto table; no chain-storage).

## META_RULE checklist

- `arms_differ_verified`: TRUE at smoke gate (META_RULE_AF)
- `final_metrics_atomicity`: `tmp_replace` (META_RULE_AH)
- `except SystemExit: raise` BEFORE `except Exception` (§8 mandatory ordering)
- `crlb_n/a`: retrieval r@k is not a Cramer-Rao-bounded scalar; band is empirically-anchored to
  standalone cells' MEASURED@ references + discriminator margin. Sanity gate = 500-article
  chance = 0.01 r@5 (random arm HP5 = 0.05 ceiling caps implementation bugs).
- `baseline_in_band`: HP5 ensures RANDOM r@5 <= 0.05 (META_RULE_AG)
- `discriminator_survives_scale`: HP4 char-trigram is deterministic; identical output at same
  N_DIM. HP3 PPMI is seed-dependent but same seeds as standalone give same expected mean. HP1/HP2
  bands are strictly above discriminator margin. Discriminator-narrows-at-scale caveat is CALLED
  OUT in report; interpretation is smoke-mechanism-lift scope.
- `HP strictly above floor`: HP1 = PPMI_ref + 0.03; HP2 = char_trigram_ref + 0.03; HP4/HP5 are
  narrow-tolerance regression bands.
- `HP_SCOPE per-arm`: declared above.
- `cardinality_ok`: `EXPECTED_N_UNITS = 5 arms x 3 seeds = 15`. Verdict emits
  `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if `actual_n_units < 15`.
- `per-unit failure-class instrumentation`: `except (KeyboardInterrupt, SystemExit): raise` then
  `except Exception as e:` records `failure_class = type(e).__name__` per arm per seed.
- `calibration_check`: `default_ok_for_this_regime` - PPMI + VWFA + char-trigram already have
  hardened selftests + Wikipedia SMOKE HPs; hyperparams are inherited unchanged.
- All numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ (META_RULE_AC).
- `cell_chunked`: false (single-cell 5-arm smoke; failure of one seed doesn't kill others due to
  per-arm try/except).
- `start_marker_written`: true
- `crash_diagnostic_present`: true
- `heartbeat_present`: true (per-arm per-seed emit)
- `defensive_error_checking`: passed_all_4_patterns
- `progress_logging`: `print_flush_true` + line_buffered_stdout at cell start
- `sweep_alignment_verdict`: n/a (no sweep axis; 5 fixed arms)
- `discriminating_fraction`: n/a (no sweep)
- `composition_edges`: composed arm edges declared explicit in `hdlab.composed_encoder_v3`
  docstring (VWFA stream + PPMI stream -> late-combine at cosine score layer; SHAPE_MATCH per
  wrapped-encoder n_dim propagation)
- `positive_control_arms`: ARM_PPMI_ALONE + ARM_CHAR_TRIGRAM_UNSUP_REFERENCE are explicit
  reproduce-at-test-regime arms with narrow-tolerance bands (Gate D compliance).
- `functional_requirements`:
  - retrieve article body from title on real-corpus Wikipedia at 500 articles -> cosine-argmax
    over per-body HD table (surface + semantic streams composed)

## Dispatch

- Route: `local_cpu_queue` (per USER-locked SMOKE-only-local rule)
- Timeout: `1800s` (15 min elapsed + 15 min safety margin)
- No FULL variant.

## Reproducibility

- Same corpus file as `exp_substrate_wikipedia_ppmi_svd_baseline_smoke` + `exp_substrate_wikipedia_char_trigram_baseline_smoke`.
- Same seeds, same N_DIM, same BODY_CHAR_CAP, same retrieval metric definition.

## Post-smoke actions (before FULL dispatch)

FULL routing is HELD per task discipline. If HP1 fires cleanly (+ HP2 fires, + regression arms
reproduce), Director decides whether to author a FULL follow-up at scaled corpus + n_dim; if HF1
fires the finding IS the structural verdict (composition dilutes across task classes).
