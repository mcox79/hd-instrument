# PRE-REG: Spoke 3 hippocampal encoder EPISODIC ONE-SHOT BINDING GATE 2 CLOSE smoke

**Anchor:** `substrate_spoke3_hippocampal_encoder_episodic_binding_gate2_close_smoke_2026_07_03`
**Cell file:** `experiments/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_gate2_close_smoke_2026-07-03.py`
**Primitive file:** `hdlab/hippocampal_encoder.py`
**Filed:** 2026-07-03 (follow-up to discriminating smoke HF_no_separation, commit `1d8b0ec44`)
**Author:** hdi_exp_dev
**Run mode:** SMOKE-only (USER-locked SMOKE-only-on-local_cpu).

## Question

Under a TIGHTER discriminating regime (cue-zero=0.95 extreme corruption AND n_dim=1024 reduced-SNR variant on top of adversarial cluster-cos=0.64 codebook), does COSINE baseline finally DEGRADE below 0.90 AND does the Marr-CA3 + DG-expansion primitive `hdlab.hippocampal_encoder` beat it by >= 0.10, cleanly satisfying the Skunkworks 2-gate parent-META promotion criterion Gate 2?

## Prior context

- Prior discriminating regime (commit `1d8b0ec44`) HP1 CLEARED (HIPPO_N500_ADV_90 r@1=0.719 >= 0.70) but HP2 FAILED (COSINE saturated 1.000 -> sep=-0.281). Classified MB (MEASURED_MECHANISM), not HF, by Skunkworks re-tier (commit `56618ca2e`).
- Skunkworks 2-gate promotion criterion for parent META `SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_...`:
  - Gate 1: PPMI FULL 10K formal 3-seed within +-0.02 of preliminary (in flight, separate arc).
  - **Gate 2 (this cell): Spoke 3 discriminator-fires witness with baseline r@1 <= 0.90 AND HIPPO - COSINE separation >= 0.10.**

## Framing discipline (LOAD-BEARING per USER 2026-07-02)

- SUBSTRATE KNOWS ALMOST NOTHING. MECHANISM discriminator on SUPERVISED synthetic binding task. NOT a general-knowledge claim. NOT a language claim.
- If HP1 + HP2 at ndim=2048: parent-META promotion path CLEAR via clean primary witness.
- If HP1 + HP2 only via ndim=1024 fallback: parent-META promotion via reduced-SNR variant with recommendation to next-tighter regime for primary.
- If HF-sat (COSINE still >= 0.95 at ndim=2048 AND ndim=1024 fallback fails): report + recommend next-tighter regime (cluster cos >= 0.90, flip_frac <= 0.05).
- If MB (baseline degrades but separation < 0.10): honest partial validation.
- HYPOTHESIZED/THEORETICAL/MEASURED numbers tagged per META_RULE_AC.

## Prior-work check (substrate-KB concept-query 2026-07-03)

Ran `bash tools/substrate_query.sh "Spoke 3 gate 2 close discriminating regime cue zero 95 percent extreme corruption"`:
- Rank 1: `Discriminating regime` cosine=0.3545 (generic across preregs; unrelated to gate 2 close probe).
- Rank 2: `Discrimination regime` cosine=0.332 (research drill; unrelated).
- Rank 3-5: various generic mentions cosine 0.31-0.33.

Prior-work check: NONE at cosine>0.36 for the specific probe (n_dim=1024 reduced-SNR + 95% corruption + Gate 2 promotion criterion). NOVEL cell. Predecessor `exp_substrate_spoke3_hippocampal_encoder_episodic_binding_discriminating_smoke_2026-07-03.py` is the direct antecedent; regression arms of THIS cell reproduce that regime bit-identically to confirm code integrity.

## Task protocol

Per seed: for each arm (spec = encoder_kind, n_dim, n_pairs, codebook, corruption), draw pairs, form episodes, one-shot write, partial-corrupt-cue retrieve, score.

### Task class (SAME as predecessor cell)

1. Draw N pairs of role_key/filler HDs in R^n_dim (n_dim in {1024, 2048}, bipolar).
2. `episode_i = role_key_i * filler_i` (elementwise bind).
3. `HippocampalEncoder.encode_and_write(episodes)`.
4. `cue_i = episode_i` with `fraction_zeroed` dims zeroed.
5. `HippocampalEncoder.retrieve(cues, use_ca3=True, sparsify_after_settle=True)`.
6. recall@1 = fraction where `argmax_j cos(query_i, stored_j) == i`.

### Regime axes

- n_dim in {1024, 2048} (n_dim=1024 = reduced SNR variant)
- N in {50 (regression), 500 (primary), 800 (approach-capacity)}
- codebook in {random (regression), adversarial (cluster-shared role_key, within-cluster filler cos ~0.64)}
- corruption in {0.50 (regression), 0.95 (Gate 2 close primary)}

### Chunk-checkpoint

Per-seed `partial_metrics_<seed>.json` written atomically after each seed completes (SH-4).

## Arms (12 arms x 3 seeds = 36 units)

`EXPECTED_N_UNITS = 12 * 3 = 36`

| # | Arm | n_dim | N | Codebook | Corrupt | Role |
|---|-----|-------|---|----------|---------|------|
| A | ARM_REGRESSION_HIPPOCAMPAL_N50_RANDOM_50CORRUPT_ndim2048 | 2048 | 50 | random | 0.50 | regression |
| B | ARM_REGRESSION_HIPPOCAMPAL_DG_ONLY_N50_RANDOM_50CORRUPT_ndim2048 | 2048 | 50 | random | 0.50 | regression |
| C | ARM_REGRESSION_COSINE_BASELINE_N50_RANDOM_50CORRUPT_ndim2048 | 2048 | 50 | random | 0.50 | regression |
| D | ARM_HIPPOCAMPAL_N500_ADV_95CORRUPT_ndim2048 | 2048 | 500 | adversarial | 0.95 | LOAD_BEARING primary |
| E | ARM_HIPPOCAMPAL_N500_ADV_95CORRUPT_ndim1024 | 1024 | 500 | adversarial | 0.95 | reduced-SNR variant |
| F | ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_95CORRUPT_ndim2048 | 2048 | 500 | adversarial | 0.95 | DG-only ablation |
| G | ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_95CORRUPT_ndim1024 | 1024 | 500 | adversarial | 0.95 | DG-only ablation reduced SNR |
| H | ARM_COSINE_BASELINE_N500_ADV_95CORRUPT_ndim2048 | 2048 | 500 | adversarial | 0.95 | baseline (must degrade for HP1) |
| I | ARM_COSINE_BASELINE_N500_ADV_95CORRUPT_ndim1024 | 1024 | 500 | adversarial | 0.95 | baseline reduced SNR |
| J | ARM_HIPPOCAMPAL_N800_ADV_95CORRUPT_ndim2048 | 2048 | 800 | adversarial | 0.95 | approach-capacity 76% C_TF |
| K | ARM_COSINE_BASELINE_N800_ADV_95CORRUPT_ndim2048 | 2048 | 800 | adversarial | 0.95 | baseline approach-capacity |
| L | ARM_RANDOM_BASELINE_N500 | 2048 | 500 | n/a | n/a | chance floor |

**arms_differ_verified:** hash-check per (seed x arm) on the retrieval-query prefix. `arms_differ_exempted`: regression arms A/B/C share input `episodes` at N=50 (predecessor bit-identity check).

## Regime constants

- DG_DIM = 8192 (fixed)
- SPARSITY = 0.02
- CLUSTER_SIZE = 5
- ADVERSARIAL_FLIP_FRAC = 0.10 -> THEORETICAL@ within-cluster cos ~ (1-2*flip)^2 = 0.64
- Seeds: [11, 17, 23]
- C_TF at dg_dim=8192, p=0.02 = 1047 patterns (THEORETICAL@ Tsodyks-Feigelman 1988)
- Load fractions: N=50 -> 4.8%; N=500 -> 48%; N=800 -> 76% of C_TF

## SNR analytical predictions (Skunkworks-derived; verify in-code)

MEASURED@this cell (`_compute_snr_prediction`, run at cell startup and logged):
Signal cos = sqrt(1-z); sibling cos mean = 0.64 * sqrt(1-z), std = sqrt(0.59/n_dim); random distractor cos std = 1/sqrt(n_dim).

| Regime | kept | signal | sib_mean | sib_std | sig-sib | z_sib_beats |
|--------|------|--------|----------|---------|---------|-------------|
| ndim=2048 z=0.95 N=500 | 102 | 0.224 | 0.143 | 0.017 | 0.080 | 4.74 |
| ndim=1024 z=0.95 N=500 |  51 | 0.224 | 0.143 | 0.024 | 0.080 | 3.35 |
| ndim=2048 z=0.95 N=800 | 102 | 0.224 | 0.143 | 0.017 | 0.080 | 4.74 |

Interpretation: HYPOTHESIZED@ z_sib_beats=3.35 (n_dim=1024) is marginal enough that cosine may see genuine sibling-distractor overtake events; z_sib_beats=4.74 (n_dim=2048) is still deterministic so cosine likely stays high. If ndim=2048 baseline still saturates >= 0.95, ndim=1024 is the fallback Gate 2 witness.

## HP bands (LOAD_BEARING per Skunkworks 2-gate promotion criterion)

`HP_SCOPE`:
- HP1 applies to ARM_COSINE_BASELINE_N500_ADV_95CORRUPT_ndim2048 (baseline DEGRADES).
- HP2 applies to `ARM_HIPPOCAMPAL_N500_ADV_95CORRUPT_ndim2048 - ARM_COSINE_BASELINE_N500_ADV_95CORRUPT_ndim2048`.
- REGRESSION applies to arms A, B, C.
- HF-sat applies to ARM_COSINE_BASELINE_N500_ADV_95CORRUPT_ndim2048.
- HF-baseline_in_band applies to ARM_RANDOM_BASELINE_N500.

### HARD_PASS

| # | Metric | Threshold | Applies to |
|---|--------|-----------|------------|
| HP1 | recall@1 | <= 0.90 | ARM_COSINE_BASELINE_N500_ADV_95CORRUPT_ndim2048 (baseline DEGRADES) |
| HP2 | recall@1 delta | >= 0.10 | HIPPO_ndim2048 - COSINE_ndim2048 at ADV_95 |
| REGRESSION | recall@1 | >= 0.95 for all encoder arms | A, B, C at N=50 random 0.50 |

Both HP1 AND HP2 required for `HARD_PASS_GATE2_CLEAN` (primary ndim=2048). If ndim=2048 baseline still saturates >= 0.95 BUT ndim=1024 fallback satisfies both HP1 and HP2, verdict is `HARD_PASS_GATE2_VIA_REDUCED_SNR` (Gate 2 still satisfied but recommend next-tighter regime for cleaner primary).

### HARD_FAIL

| # | Condition | Implication |
|---|-----------|-------------|
| HF-sat | COSINE_ndim2048 r@1 >= 0.95 AND ndim=1024 fallback doesn't satisfy HP1+HP2 | regime STILL insufficient; recommend cluster_cos >= 0.90 with flip_frac <= 0.05 |
| HF-regression | any regression arm r@1 < 0.95 | code drift from predecessor |
| HF-baseline | RANDOM_BASELINE_N500 r@1 > 0.01 | META_RULE_AG violation; retrieval-impl bug |
| HF-dg-rate | HIPPO dg_sparse_rate out of [0.008, 0.040] | architectural sanity |
| HF-cardinality | actual_n_units < 36 | META_RULE_H breach |

### MIDDLE_BAND

Baseline degrades (COSINE ndim=2048 < 0.95) but HIPPO - COSINE separation < 0.10 at ndim=2048 AND ndim=1024 fallback does not clean up. Regime is discriminating but mechanism-vs-baseline gap under Gate 2 floor. Recommend parameter tuning (CA3 iterations, sparsity, expansion factor) or accept mechanism has ~= baseline at extreme corruption.

## Envelope-fail bands

- ARM_RANDOM_BASELINE_N500 recall@1 expected [0.0, 0.01] (chance 0.002; 5x band).
- HIPPO arms dg_sparse_rate expected [0.008, 0.040] (target 0.02).
- COSINE_N500_ADV_95_ndim2048 recall@1 expected [0.60, 0.98] (HYPOTHESIZED@ signal margin exists but with reduced-kept-dims variance at kept=102, some degradation possible; SNR z_sib_beats=4.74 argues for saturation).
- COSINE_N500_ADV_95_ndim1024 recall@1 expected [0.30, 0.90] (HYPOTHESIZED@ z_sib_beats=3.35 marginal; degradation more likely).
- HIPPO_N500_ADV_95_ndim2048 recall@1 expected [0.40, 0.85] (mechanism at 48% C_TF + 95% corruption; predecessor HIPPO_ADV_90 was 0.719 - expect further drop at 95%).
- HIPPO_N800_ADV_95_ndim2048 recall@1 expected [0.30, 0.75] (approach capacity 76% + 95% corruption).
- REGRESSION arms expected == 1.000 (bit-identical to predecessor).

## Cell-template compliance

- `arms_differ_verified` at smoke gate (META_RULE_AF; per-seed hash check).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` BEFORE `except Exception` (no `except BaseException`).
- `baseline_in_band` in verdict logic (META_RULE_AG).
- `cardinality_ok` = actual_n_units >= 36.
- Per-unit `failure_class` (META_RULE_J).
- `start_marker_written`, `_heartbeat.jsonl`, crash-diagnostic write.
- Per-seed checkpoint (SH-4).
- Default `_parse_args()` mode = `smoke`.
- Numbers tagged per META_RULE_AC.
- `progress_logging: print_flush_true`.

## SCHEMA-VET gates

- **sweep_alignment_verdict: ALIGNED** — swept parameters (n_dim, N, corruption) are the effective parameters at all encoder types (no partition-routing).
- **discriminating_fraction: 0.75** — 9/12 arms in discriminating regime (D-L excluding random/regression). All 9 discriminating arms predicted to land in [0.05, 0.95] band (see envelope-fail-bands).
- **composition_edges** — none.
- **positive_control_arms** — REGRESSION arms A, B, C at N=50 random 50%; reproduce predecessor r@1 = 1.000 (tolerance 0.05). Same `_draw_pairs_random` + `_corrupt_cue` + same seeds -> bit-identical expected.
- **functional_requirements**:
  - FR1: one-shot binding at 48-76% C_TF -> DG expansion + CA3 Hebbian outer product.
  - FR2: decorrelation of adversarially-correlated codebook -> DG random-projection + top-K sparsification.
  - FR3: extreme partial-cue completion (95% zeroed) -> CA3 auto-associator single-step settle.
- **crlb_n/a**: "Retrieval-accuracy over sparse-attractor cleanup; no closed-form CRLB. Discriminator = mechanism-vs-baseline gap; capacity feasibility via T-F = 1047 patterns >> tested N=800."
- **discriminator_reachability: True** — HP1 (COSINE <= 0.90) and HP2 (sep >= 0.10) are within analytical envelope (SNR z_sib_beats < 5 at both n_dims; margin exists).

## Compute architecture

- (a) batched-CPU-numpy (matmul via BLAS; no GPU).
- Storage strategy: SHARDED per-episode DG codes.
- Per-seed wall estimate:
  - Regression arms (n_dim=2048 N=50): ~5s combined.
  - Primary N=500 hippocampal + dg-only arms at ndim=2048 (D, F): ~120s combined.
  - Reduced-SNR N=500 hippocampal + dg-only at ndim=1024 (E, G): ~60s combined (half input-dim matmul).
  - COSINE arms (H, I, K): ~10s combined.
  - Approach-capacity N=800 hippocampal (J): ~120s.
  - RANDOM_BASELINE (L): ~5s.
- Estimated total per seed: 5-6 min. 3 seeds -> 15-18 min wall.
- Timeout: 3600s (60 min) with safety margin.

## Selftests (`--self-test`)

Chain to `python -m hdlab.hippocampal_encoder --self-test` (13 primitive tests) + 8 cell-level integration selftests:

1. `arg_parse_default_is_smoke`
2. `corrupt_cue_correct_fractions` (0.50, 0.90, 0.95 fractions)
3. `snr_math_predictions` (analytical formula matches Skunkworks-derived table above)
4. `mini_binding_recall_random`
5. `arms_differ_hash_micro`
6. `adversarial_codebook_within_cluster_cos` (n_dim=2048)
7. `adversarial_codebook_n_dim1024` (new: n_dim=1024 codebook works)
8. `regression_arm_bit_identical`

Total: 13 primitive + 8 cell = 21 selftests, all must pass before dispatch.

## Post-smoke gating

Report per-arm r@1 mean + std; per-seed timings; DG sparse rate; per-arm mechanism-vs-baseline separation; verdict; honest interpretation of Gate 2 satisfaction (`HARD_PASS_GATE2_CLEAN` at primary ndim=2048 OR `HARD_PASS_GATE2_VIA_REDUCED_SNR` at ndim=1024 fallback OR HF-sat with next-regime recommendation OR MB). Do NOT dispatch FULL. Verdict feeds Skunkworks parent-META 2-gate promotion decision.
