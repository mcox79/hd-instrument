# PRE-REG: substrate-native Spoke 3 hippocampal-analog encoder Wikipedia SMOKE (N=500)

**Anchor:** `substrate_spoke3_hippocampal_encoder_smoke_2026_07_03`
**Cell file:** `experiments/exp_substrate_spoke3_hippocampal_encoder_smoke_2026-07-03.py`
**Primitive file:** `hdlab/hippocampal_encoder.py`
**Filed:** 2026-07-03 (Skunkworks-approved load-bearing bge-retire path per decision fork (B) after PPMI Wikipedia FULL 10K preliminary HARD_NEGATIVE)
**Author:** hdi_exp_dev
**Run mode:** SMOKE-only (no FULL variant filed at this cell; USER-locked SMOKE-only-on-local_cpu).

## Question

Does the brain-analog hippocampal composition (Marr 1971 CA3 auto-associator on DG-analog sparse-expansion code) provide substrate-native lift over char-trigram surface encoder on the same held-out Wikipedia title -> body retrieval task at N=500?

Reference for load-bearing framing:
- `notes/design_stage2_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_2026-07-02.md` -- Skunkworks-reviewed design.
- Char-trigram Wikipedia FULL 10K r@5 = 0.703 MEASURED@ 2026-07-03.
- PPMI/SVD Wikipedia FULL 10K r@5 = 0.6791 MEASURED@ 2026-07-03 (PRELIMINARY HARD_NEGATIVE -- LOSES to char-trigram).
- No substrate-native surface/semantic mechanism alone closes the bge gap.
- Spoke 3 hippocampal-analog is the remaining brain-analog rescue path per decision fork (B).

## Framing discipline (LOAD-BEARING per USER 2026-07-02)

- SUBSTRATE KNOWS ALMOST NOTHING -- Spoke 3 hippocampal is a MECHANISM PROBE on the SUPERVISED synthetic-corpus regime; NOT a general-knowledge claim.
- Explicitly AVOID 2026-06-23 falsified WTA-collision pattern (documented in design doc):
  * Expansion FIRST (input_dim -> dg_dim), then sparsify by magnitude (not by pre-registered collision-minimization).
  * LEARNING driver via Hebbian outer product in CA3 (not pure allocation).
  * Target sparsity ~1-2% (not 0.25% as in 2026-06-23).
  * Selftest `hippo_ne_naive_wta_collision_2026_06_23` verifies at mechanism level.
- If Spoke 3 also HF/MB below char-trigram, that is a strong finding but NOT "substrate can't do Wikipedia"; it is mechanism-scope-limited to this task class.
- Discriminator-narrows-at-scale caveat applies: results at N=500 smoke may over-project to N=10K FULL (V2-A precedent -- PPMI PASSED at N=500 smoke but HF'd at N=10K FULL).

## Prior-work check (substrate-KB concept-query 2026-07-03)

Ran `bash tools/substrate_query.sh "hippocampal DG CA3 sparse pattern separation encoder"`:
- Rank 1: `entity='12. Hippocampal pattern separation/completion - DG sparse coding'` cosine=0.4893 (source `notes/research_brain_mechanism_x_HD_broad_exploration_drill_2026-06-22.md`) -- research drill only, no substrate cell tested this composition on real Wikipedia.
- Rank 2: `entity='Hippocampal pattern separation vs pattern completion'` cosine=0.4521 (research drill 2026-06-11).
- Rank 3: `entity='5.2 Hippocampal Dentate Gyrus -- Pattern Separation Engine'` cosine=0.4141 (research drill 2026-06-08).
- Rank 4: `entity='1. Hippocampal Dentate Gyrus pattern separation'` cosine=0.4092 (anisotropy drill 2026-06-25).
- Rank 5: `entity='A2. Hippocampal pattern separation for sense disambiguation'` cosine=0.3955 (image-schema drill 2026-06-10).

Prior-work check: TOP HITS ARE ALL RESEARCH NOTES (no prior substrate cell has tested Marr-CA3-on-DG-expansion as a retrieval encoder on real Wikipedia at any scale). Design doc explicitly grep-verified: 2026-06-23 sparse_engram_allocation HF (naive WTA sampling, no expansion, no learning driver) is mechanism-different in 3 orthogonal ways (documented in design doc). Cell is NOVEL as a first substrate-native Marr CA3 + DG expansion probe on Wikipedia.

Related prior work also examined:
- `experiments/exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1.py` -- prior Spoke 3 CLS cell targeting the SYNTHETIC one-shot-episodic-binding task class (200 concepts + 20 one-shot events + consolidation retention probes). NOT a Wikipedia retrieval task. This cell is a DIFFERENT probe: Spoke 3 mechanism as a body-title retrieval encoder on Wikipedia (same held-out task as PPMI + char-trigram smokes).

## Test protocol

Held-out title -> body retrieval on `data/datasets/wikipedia_smoke_500.jsonl` (bit-identical corpus + query + seed choices to PPMI/char-trigram smoke cells for direct comparability):

1. Load 500 articles (`{title, text}` per row). Truncate body to 800 chars.
2. Char-trigram encode body and title -> `body_hd`, `title_hd` in R^{N_DIM}.
3. Per arm, produce final retrieval codes from `body_hd` and `title_hd` and compute `S[i,j] = cos(title_code[i], body_code[j])`.
4. `recall@k` = fraction of titles whose correct body is in top-k.

Regime:
- N articles: 500. N_DIM (input HD): 2048. DG_DIM (expansion): 8192 (4x expansion). SPARSITY: 0.02 (~164 active DG dims).
- Seeds: [11, 17, 23]. Char-trigram, PPMI-SVD deterministic w.r.t. seed by design; Spoke 3 DG projection depends on seed.
- Chance recall@5 = 5/500 = 0.01 (THEORETICAL@).
- Predicted arm walls (HYPOTHESIZED@ from selftest scale sentinel): Spoke 3 hippocampal ~3-8 min per seed at N=500 (dominated by CA3 outer-product writes O(K^2) per body and W @ cue matmul per title).

## Arms

| Arm | Encoder | Role |
|-----|---------|------|
| ARM_SPOKE3_HIPPOCAMPAL | char-trigram body/title -> DG expansion -> CA3 auto-assoc write on body codes -> title-code sparsified after CA3 settle; retrieval cos on sparsified DG codes | LOAD_BEARING |
| ARM_SPOKE3_ONE_SHOT | char-trigram -> DG expansion only (no CA3 settle); retrieval cos on sparse DG codes | ablation: proves CA3 auto-assoc contribution |
| ARM_PPMI_ALONE | `hdlab.ppmi_sparse_encoder.PPMISparseEncoder` fit on bodies-as-labels, encode body + title | regression: MUST reproduce r@5 = 0.906 within tol 0.05 |
| ARM_CHAR_TRIGRAM | `hdlab.char_trigram_encoder.CharTrigramEncoder` on body + title | regression: MUST reproduce r@5 = 0.854 within tol 0.05 |
| ARM_RANDOM_BASELINE | random bipolar HDs for body + title | chance floor (r@5 <= 0.05) |

Per-arm retrieval detail:
- **ARM_SPOKE3_HIPPOCAMPAL:** body_hd (char-trigram) -> `HippocampalEncoder.encode_and_write` writes CA3 attractor from each body's DG code. title_hd (char-trigram) -> `HippocampalEncoder.retrieve(sparsify_after_settle=True)` -> title_dg_completed. Retrieval: cos(title_dg_completed[i], stored_body_dg[j]).
- **ARM_SPOKE3_ONE_SHOT:** same DG projection but `use_ca3=False` on retrieve; body codes are the raw DG projections of body_hd. Retrieval: cos on raw DG codes both sides. (Isolates DG-expansion contribution from CA3 pattern-completion contribution.)

## Metrics (per arm x seed)

- `recall_at_1`, `recall_at_5`, `recall_at_10`
- `mean_reciprocal_rank`
- `intra_article_body_title_cos`, `inter_article_title_body_cos`, `signal_to_noise_ratio`
- `dg_sparse_rate` (Spoke 3 arms only; diagnostic: must land near 0.02)
- Wall time per arm per seed.

Aggregate: mean + std across seeds.

## HP bands

`HP_SCOPE: LOAD_BEARING on ARM_SPOKE3_HIPPOCAMPAL. Regression arms (PPMI, char-trigram) require reproduction of MEASURED reference r@5 within +/- 0.05. Random arm is baseline_in_band sanity (META_RULE_AG).`

### HARD_PASS

| # | Metric | Threshold | Applies to |
|---|--------|-----------|------------|
| HP1 | recall@5 | >= 0.884 (= char-trigram 0.854 + 0.03 discriminator margin) | ARM_SPOKE3_HIPPOCAMPAL |

Meaning: brain-analog hippocampal composition beats surface char-trigram at N=500 smoke by a discriminator margin >= +0.03 -- signals that Marr-CA3 + DG-expansion is doing load-bearing work over pure surface bag-of-trigrams.

### HARD_FAIL

| # | Condition | Implication |
|---|-----------|-------------|
| HF1 | ARM_SPOKE3_HIPPOCAMPAL r@5 < 0.824 (char-trigram - 0.03) | Spoke 3 hippocampal LOSES to surface char-trigram; mechanism-scope-limited on this task class; no substrate-native surface/semantic mechanism closes the bge gap at N=500 smoke. Route to research 2x-drill. |
| HF2 | ARM_PPMI_ALONE r@5 NOT in [0.856, 0.956] | PPMI regression broken -- retrieval-implementation drift; smoke untrustworthy. |
| HF3 | ARM_CHAR_TRIGRAM r@5 NOT in [0.804, 0.904] | char-trigram regression broken -- same. |
| HF4 | ARM_RANDOM_BASELINE r@5 > 0.05 | META_RULE_AG baseline_in_band violation; retrieval-implementation bug. |
| HFcard | actual_n_units < expected_n_units (5 arms x 3 seeds = 15) | META_RULE_H cardinality breach; one or more (seed, arm) units failed. |

### MIDDLE_BAND

ARM_SPOKE3_HIPPOCAMPAL r@5 in [0.824, 0.884). Neither cleanly beats nor loses to char-trigram. Route to v2 sparsity/expansion sweep (DG_DIM x SPARSITY x seeds) or to Spoke 3 v2 (Option B Hebbian-adjusted projection).

## Envelope-fail bands

- ARM_RANDOM_BASELINE r@5 expected [0.0, 0.05] (chance = 0.01; band cap 5x chance for 3-seed variance).
- ARM_PPMI_ALONE r@5 expected 0.906 +/- 0.05 (MEASURED@ 2026-07-03 char-trigram cell = 0.906; smoke reproduction gate).
- ARM_CHAR_TRIGRAM r@5 expected 0.854 +/- 0.05 (MEASURED@ 2026-07-03 char-trigram cell = 0.854).
- ARM_SPOKE3_HIPPOCAMPAL dg_sparse_rate expected in [0.008, 0.040] (target 0.02; band 2x either side).

## Dispatch plan

- SMOKE via `local_cpu_queue` per USER-locked SMOKE-only-on-local (`feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01.md`).
- No FULL variant filed in this cell. If HP or MIDDLE_BAND at smoke: file a separate scale-up cell N -> 10K on remote_cpu_queue via Orchestrator.
- No push required (local cell).

## Cell-template compliance

- `arms_differ_verified` at smoke gate (META_RULE_AF; hash-check on first-article body HD prefix per arm).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception` in per-arm driver + `__main__` (no `except BaseException`).
- `baseline_in_band` verified in verdict logic (META_RULE_AG; ARM_RANDOM_BASELINE r@5 sanity).
- `cardinality_ok` = actual_n_units >= expected_n_units (5 x 3 = 15).
- Per-unit `failure_class` instrumentation (META_RULE_J).
- `start_marker_written`, `_heartbeat.jsonl`, crash-diagnostic write.
- Per-seed checkpoint (SH-4-adjacent) via partial_metrics_<seed>.json atomic tmp-replace before final aggregation -- avoids PPMI FULL cell's fatal timeout data-loss pattern.
- Default `_parse_args()` mode is `smoke` (SMOKE-only cell); prevents accidental FULL invocation.
- Numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
- `progress_logging: print_flush_true` (Sec 17; not strictly required at expected 3-8 min but wired for safety).

## Compute architecture

- (a) batched-CPU-numpy; corpus fits in memory (500 x 2048 x 4bytes = 4MB body_hds).
- DG expansion: (n=500 x 2048) @ (2048 x 8192) = 500 x 8192 float32 = 16MB (one matmul; batched).
- CA3 outer-product writes: sum of K^2 per write = 500 x (164^2) = ~13M FMAs total. Fits in-memory.
- CA3 W: 8192 x 8192 float32 = 268MB. In RAM.
- Storage strategy: SHARDED per-body DG codes (each body its own vector) + CA3 W matrix (dense associative). Per META_STORAGE_STRATEGY sharded is correct for this compositional retrieval task (each body must be a distinct attractor).
- Per-seed smoke wall estimate: ~3-8 min (dominated by CA3 batched settle: (500 x 8192) @ (8192 x 8192) = one 268GB-FMA matmul per seed on CPU).

## Selftests (`--self-test`)

Chain to `python -m hdlab.hippocampal_encoder --self-test` (13 primitive-level selftests) + a small cell-level integration selftest verifying:

1. Wikipedia-mini corpus retrieval doesn't crash + arms all produce distinct outputs.
2. `retrieval_metrics_identity`: body=title gives r@1=1.0.
3. `random_chance_at_scale`: at N=200 x n_dim=2048 random arm r@5 in [0, 5x chance].
4. `arg_parse_default_is_smoke`.

Total: 13 primitive + 4 cell = 17 selftests, all must pass before dispatch.

## Post-smoke gating

Report per-arm r@5 mean + std; per-seed timings; DG sparse rate; verdict; honest gap-to-char-trigram; HOLD status. Do NOT dispatch FULL. Verdict feeds Director's decision fork (B) resolution.

## Discriminator-must-survive-scale caveat

Analytical: DG expansion + Marr-CA3 discriminator is dominated by two competing effects at scale N:
- (positive) CA3 pattern-completion pulls noisy queries toward stored attractors -> retrieval improves with #attractors up to Tsodyks-Feigelman capacity ~0.14 * dg_dim / (k * ln(1/k)) = 0.14 * 8192 / (164 * 4.1) ~ 1.7 patterns without interference (THEORETICAL@). At N=500 patterns >> capacity, CA3 saturates -> pattern completion may become NOISE-DOMINATED at FULL scale.
- (negative) DG expansion Johnson-Lindenstrauss preserves discrimination for random data at capacity ~ dg_dim/log(N) = 8192/log(500) ~ 1320; well above N=500 -> DG-only should survive scale.

Bands are appropriate for N=500 smoke -- if HP, a scale-up cell to N=10K will need band re-derivation (potential capacity-collapse of CA3 auto-associator at N/dg_dim ratio >= 0.1). Filed HOLD.
