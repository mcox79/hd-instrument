# PRE-REG: Spoke 3 hippocampal encoder EPISODIC ONE-SHOT BINDING smoke (N=50 pairs)

**Anchor:** `substrate_spoke3_hippocampal_encoder_episodic_binding_smoke_2026_07_03`
**Cell file:** `experiments/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_smoke_2026-07-03.py`
**Primitive file:** `hdlab/hippocampal_encoder.py`
**Filed:** 2026-07-03 (Skunkworks-recommended existence proof for task-mechanism fit)
**Author:** hdi_exp_dev
**Run mode:** SMOKE-only (USER-locked SMOKE-only-on-local_cpu).

## Question

Does the brain-analog Marr-CA3 + DG-expansion primitive (`hdlab.hippocampal_encoder`) provide load-bearing episodic one-shot binding + pattern completion on its INTENDED task class (novel (role_key, filler) pair binding with partial-cue recall) at N pairs well below Tsodyks-Feigelman capacity?

**Task-class rationale (LOAD-BEARING framing per Skunkworks 2026-07-03):**
Prior Wikipedia title->body smoke (2026-07-03, commit `1cd8e3757`) HARD_FAIL: `ARM_SPOKE3_HIPPOCAMPAL` r@5=0.145 vs char-trigram 0.854. Cell-author diagnosis: Marr-CA3+DG-expansion is designed for EPISODIC one-shot binding + pattern completion (Marr 1971, Wilson-McNaughton 1994, McClelland-McNaughton-O'Reilly 1995), NOT open-domain many-to-many surface retrieval. Task-class MISMATCH hypothesis. This cell tests the primitive on its INTENDED task class as an existence proof for task-mechanism fit, independent of the Wikipedia task-class mismatch.

**Skunkworks 2026-07-03 correction to prior cell-author claim:** Tsodyks-Feigelman capacity is `C_TF = N / (2 * ln(1/p))` where p=sparsity=0.02 -> ln(50)=3.912 -> C_TF = 8192/(2*3.912) = 1047 patterns. Prior cell's "N=500 >> capacity ~1.7 patterns" claim was WRONG (used wrong formula). At N=50 pairs, load fraction = 50/1047 = 4.8% (deeply under-capacity). Interference is not the issue. THEORETICAL@ Tsodyks-Feigelman 1988.

## Framing discipline (LOAD-BEARING per USER 2026-07-02)

- SUBSTRATE KNOWS ALMOST NOTHING. This is a MECHANISM PROBE on a SYNTHETIC supervised regime (random bipolar (role_key, filler) HDs, ground-truth pair identity). NOT a general-knowledge claim.
- If HP: mechanism CG on Marr-CA3 for one-shot episodic binding on its intended task class; validates task-class-mismatch hypothesis for prior Wikipedia HF (Wikipedia HF is task-class issue, NOT mechanism failure).
- If HF: mechanism has issues even on intended task class; requires drill (Marr-CA3 primitive itself, not composition).
- HYPOTHESIZED/THEORETICAL numbers explicitly tagged per META_RULE_AC.

## Prior-work check (substrate-KB concept-query 2026-07-03)

Ran `bash tools/substrate_query.sh "hippocampal episodic one shot binding partial cue pattern completion"`:
- Rank 1: `B7. Hippocampal pattern completion` cosine=0.4219 (research drill 2026-06-10) -- research note only, no substrate cell tested one-shot pair binding as a probe.
- Rank 2: `2.1 Hippocampal Episodic Binding` cosine=0.4062 (research drill 2026-06-08).
- Rank 3-5: hippocampal replay / episodic binding research notes; no prior substrate cell on this exact task.

Related prior work also grep-checked:
- `experiments/exp_substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1.py` -- prior Spoke 3 CLS cell for CLS replay on synthetic concepts (200 concepts + 20 one-shot events + consolidation retention). More ambitious (uses placeholder cortex + full CLS). This cell is a NARROWER first probe: mechanism-only, using `hdlab/hippocampal_encoder.py` primitive directly.

Prior-work check: NONE at cosine>0.30 for the exact task (episodic pair-binding with partial cue on the extracted `hdlab/hippocampal_encoder.py` primitive). NOVEL cell.

## Task protocol (Option A: novel-pair binding + partial-cue recall)

1. Per seed: draw N pairs of random bipolar HDs. For pair i, `role_key_i, filler_i ~ Uniform{-1,+1}^n_dim` (n_dim=2048).
2. Compose episode HD: `episode_i = role_key_i * filler_i` (elementwise bind; bipolar preserves shape and dtype).
3. One-shot write: `HippocampalEncoder.encode_and_write(episodes)` -- each episode becomes a CA3 attractor.
4. Corrupt cue: zero 50% of dims of each episode_i (random per query, seed-fixed) -> `cue_i` in R^n_dim.
5. Retrieve: `HippocampalEncoder.retrieve(cues, use_ca3=True, sparsify_after_settle=True)` -> completed DG codes.
6. Score: recall@1 = fraction of queries where `argmax_j cos(completed_cue_i, stored_dg_j) == i`. Also recall@5.

## Arms

| Arm | Encoder | Role |
|-----|---------|------|
| ARM_HIPPOCAMPAL_ONE_SHOT | full DG + CA3: encode_and_write episodes, retrieve from 50%-partial cue with sparsify_after_settle=True | LOAD_BEARING |
| ARM_HIPPOCAMPAL_DG_ONLY_ABLATION | DG expansion only (no CA3 settle). Retrieve = DG(partial_cue) vs stored DG(full_episode). Isolates CA3 contribution. | ablation |
| ARM_COSINE_ARGMAX_BASELINE | Plain cosine argmax between partial_cue HD (n_dim) and stored episode HDs (n_dim); no encoder. Weak baseline: partial cue has cos ~0.5 with correct episode + comparable overlap with random episodes. | weak baseline |
| ARM_RANDOM_BASELINE | Retrieved index = random from [0, N). Chance floor. | chance floor |

## Regime

- N_PAIRS: 50 (smoke; well under Tsodyks-Feigelman capacity 1047 at dg_dim=8192, sparsity=0.02).
- N_DIM: 2048 (input HD).
- DG_DIM: 8192 (4x expansion).
- SPARSITY: 0.02 (top-K by magnitude; ~164 active DG dims).
- PARTIAL_CUE_FRACTION_ZEROED: 0.50 (per Marr-CA3 selftest ca3_pattern_completion_from_partial_cue which uses 50%).
- Seeds: [11, 17, 23].
- Chance recall@1 = 1/50 = 0.02 (THEORETICAL@).
- Chance recall@5 = 5/50 = 0.10.
- Tsodyks-Feigelman capacity at dg_dim=8192, p=0.02: C_TF = 8192 / (2 * ln(50)) = 1047 patterns (THEORETICAL@ Tsodyks-Feigelman 1988). Load fraction 50/1047 = 4.8% (deeply under-capacity).

## Metrics (per arm x seed)

- recall_at_1, recall_at_5, mean_reciprocal_rank
- intra_pair_cos_mean (cos of completed cue vs correct episode), inter_pair_cos_mean (cos vs other episodes)
- signal_to_noise_ratio = intra / |inter|
- dg_sparse_rate (spoke3 arms only)
- Wall time per arm per seed

Aggregate: mean + std across seeds.

## HP bands

`HP_SCOPE: HP1 applies to ARM_HIPPOCAMPAL_ONE_SHOT only. HF1 same. HF-baseline applies to ARM_RANDOM_BASELINE.`

### HARD_PASS

| # | Metric | Threshold | Applies to |
|---|--------|-----------|------------|
| HP1 | recall@1 | >= 0.80 (mechanism-appropriate for one-shot binding under-capacity) | ARM_HIPPOCAMPAL_ONE_SHOT |

HP threshold rationale: primitive selftest `ca3_pattern_completion_from_partial_cue` PASSES at 0.90 sign-agreement on 50% partial cue for a SINGLE stored pattern at dg_dim=2048. At dg_dim=8192, N=50 (4.8% load fraction, well under 1047 capacity), recall@1 >= 0.80 is the mechanism-appropriate threshold. HYPOTHESIZED@ from primitive selftest scaling.

### HARD_FAIL

| # | Condition | Implication |
|---|-----------|-------------|
| HF1 | ARM_HIPPOCAMPAL_ONE_SHOT recall@1 < 0.50 | Mechanism fails even on INTENDED task class at 4.8% capacity load. Marr-CA3 primitive has issues; requires drill on CA3 iteration/sparsity/settle-parameters. Task-class-mismatch hypothesis for Wikipedia HF is NOT confirmed (task-class fit itself is broken). |
| HF-baseline | ARM_RANDOM_BASELINE recall@1 > 0.10 | META_RULE_AG baseline_in_band violation; retrieval-implementation bug. |
| HF-dg-rate | ARM_HIPPOCAMPAL_ONE_SHOT dg_sparse_rate out of [0.008, 0.040] | Architectural sanity (target 0.02, band 2x either side). |
| HFcard | actual_n_units < expected_n_units (4 arms x 3 seeds = 12) | META_RULE_H cardinality breach. |

### MIDDLE_BAND

ARM_HIPPOCAMPAL_ONE_SHOT recall@1 in [0.50, 0.80). Partial mechanism validation: primitive works on intended task class but not at full mechanism-appropriate threshold. Route to CA3 parameter sweep (iteration count, sparsity) or DG expansion factor drill.

## Envelope-fail bands

- ARM_RANDOM_BASELINE recall@1 expected [0.0, 0.10] (chance = 0.02; band 5x chance for 3-seed variance).
- ARM_HIPPOCAMPAL_ONE_SHOT dg_sparse_rate expected [0.008, 0.040] (target 0.02).
- ARM_HIPPOCAMPAL_DG_ONLY_ABLATION: expected recall@1 well BELOW ARM_HIPPOCAMPAL_ONE_SHOT (isolates CA3 contribution). HYPOTHESIZED@ 0.10-0.40 -- DG-only doesn't pattern-complete the missing 50% of dims.
- ARM_COSINE_ARGMAX_BASELINE: expected recall@1 moderate (~0.30-0.60) -- partial cue in n_dim=2048 has cos~sqrt(0.5) with correct episode; other episodes are random and orthogonal by JL, so still some signal.

## Dispatch plan

- SMOKE via `local_cpu_queue` per USER-locked SMOKE-only-on-local.
- No FULL variant filed at this cell.
- No push required (local cell).
- Post-smoke: if HP -> HOLD pending USER decision on next steps (task-class-mismatch validated; scale + composition options). If HF -> route to research 2x-drill on Marr-CA3 primitive itself.

## Cell-template compliance

- `arms_differ_verified` at smoke gate (META_RULE_AF; hash-check per arm).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception` (no `except BaseException`).
- `baseline_in_band` verified in verdict logic (META_RULE_AG).
- `cardinality_ok` = actual_n_units >= expected_n_units (4 x 3 = 12).
- Per-unit `failure_class` instrumentation (META_RULE_J).
- `start_marker_written`, `_heartbeat.jsonl`, crash-diagnostic write.
- Per-seed checkpoint (SH-4-adjacent) via partial_metrics_<seed>.json atomic tmp-replace.
- Default `_parse_args()` mode is `smoke`.
- Numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
- `progress_logging: print_flush_true`.

## Compute architecture

- (a) batched-CPU-numpy. Corpus is synthetic 3 * 50 * 2048 * 4B = 1.2MB per seed.
- DG expansion (50 x 2048) @ (2048 x 8192) = 50 x 8192 float32 = 1.6MB per matmul.
- CA3 outer-product writes: 50 * K^2 = 50 * 164^2 = 1.3M FMAs.
- CA3 W: 8192 x 8192 float32 = 268MB.
- Storage strategy: SHARDED per-episode DG codes. Correct for compositional retrieval; each episode must be a distinct attractor. Per META_STORAGE_STRATEGY.
- Per-seed smoke wall estimate: 10-60 seconds (dominated by CA3 batched settle: 50 x 8192 @ 8192 x 8192 = single matmul).

## Selftests (`--self-test`)

Chain to `python -m hdlab.hippocampal_encoder --self-test` (13 primitive-level selftests) + 4 cell-level integration selftests:

1. mini_binding_recall: N=10 pairs, dg_dim=2048; recall@1 >= 0.80.
2. arg_parse_default_is_smoke.
3. corrupt_cue_correct_fraction: cue has exactly 0.50 zero-fraction.
4. arms_differ_hash: HIPPOCAMPAL_ONE_SHOT vs DG_ONLY completed cue hashes differ.

Total: 13 primitive + 4 cell = 17 selftests, all must pass before dispatch.

## Post-smoke gating

Report per-arm recall@1 mean + std; per-seed timings; DG sparse rate; verdict; honest interpretation whether task-class-mismatch hypothesis is validated. Do NOT dispatch FULL. Verdict feeds Director's evaluation of Wikipedia HF root cause.
