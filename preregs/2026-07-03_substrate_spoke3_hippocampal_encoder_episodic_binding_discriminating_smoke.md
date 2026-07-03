# PRE-REG: Spoke 3 hippocampal encoder EPISODIC ONE-SHOT BINDING DISCRIMINATING smoke

**Anchor:** `substrate_spoke3_hippocampal_encoder_episodic_binding_discriminating_smoke_2026_07_03`
**Cell file:** `experiments/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_discriminating_smoke_2026-07-03.py`
**Primitive file:** `hdlab/hippocampal_encoder.py`
**Filed:** 2026-07-03 (follow-up to episodic-binding SMOKE HP `regime-too-easy` caveat, commit `96d9055e5`)
**Author:** hdi_exp_dev
**Run mode:** SMOKE-only (USER-locked SMOKE-only-on-local_cpu).

## Question

Under a DISCRIMINATING regime (approach Tsodyks-Feigelman capacity + adversarially-correlated codebook + high partial-cue corruption), does the brain-analog Marr-CA3 + DG-expansion primitive `hdlab.hippocampal_encoder` measurably OUTPERFORM a plain-cosine-argmax baseline on the SAME task class (novel role_key/filler binding + partial-cue retrieval)?

Prior episodic-binding SMOKE HP (commit `96d9055e5`) landed r@1=1.000 for ALL encoder arms (HIPPOCAMPAL_ONE_SHOT, DG_ONLY, COSINE_ARGMAX) at N=50 pairs, random-orthogonal fillers, 50%-corruption. Regime-too-easy caveat: mechanism-vs-baseline separation was 0.00 → task-class-mismatch hypothesis is SUPPORTED, not PROVEN. This cell forces separation by (1) approaching capacity, (2) adversarial correlations, (3) high corruption.

## Framing discipline (LOAD-BEARING per USER 2026-07-02)

- SUBSTRATE KNOWS ALMOST NOTHING. Mechanism probe on SUPERVISED synthetic (role_key, filler) binding task. NOT a general-knowledge claim. NOT a language capability claim.
- If HP with separation (HP1 + HP2): task-class-mismatch hypothesis PROVEN (mechanism was correct; Wikipedia HF was task-class mismatch); reframes to "substrate-native structural mechanisms lose on retrieval task class specifically; work on their intended task classes."
- If HF (mechanism doesn't beat baseline anywhere): task-class-mismatch hypothesis REFUTED; substrate structural mechanisms may have deeper problem; requires drill on CA3 primitive itself.
- If MB: partial validation; further probes needed.
- HYPOTHESIZED/THEORETICAL numbers explicitly tagged per META_RULE_AC.
- Use Skunkworks-verified T-F formula: `C_TF = dg_dim / (2 * ln(1/p))`. At dg_dim=8192, p=0.02: C_TF = 8192 / (2 * 3.912) = 1047 patterns. THEORETICAL@ Tsodyks-Feigelman 1988.

## Prior-work check (substrate-KB concept-query 2026-07-03)

Ran `bash tools/substrate_query.sh "hippocampal capacity adversarial corruption discriminating regime interference"`:
- Rank 1: `hippocampal interneuron differentiation` cosine=0.3594 (gene ontology; irrelevant).
- Rank 2: `Discriminating regime` cosine=0.3467 (generic term across preregs; unrelated).
- Rank 3: `Discrimination regime` cosine=0.3320 (research drill; unrelated).
- Rank 4-5: generic "discriminating regime" mentions in prior preregs; unrelated.

Prior-work check: NONE at cosine>0.36 for the specific probe (approach-capacity + adversarial codebook + high-corrupt cue on the extracted `hdlab.hippocampal_encoder` primitive). NOVEL cell.

Predecessor cell: `experiments/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_smoke_2026-07-03.py` (HP but regime-too-easy). Regression arms of THIS cell reproduce that regime bit-identically to confirm code integrity.

## Task protocol

Per seed: for each (N, codebook, corruption) regime, draw pairs, form episodes, one-shot write, partial-corrupt-cue retrieve, score.

### Task class (SAME as predecessor cell)

1. Draw N pairs of role_key/filler HDs in R^n_dim (n_dim=2048, bipolar {-1,+1}).
2. `episode_i = role_key_i * filler_i` (elementwise bind).
3. `HippocampalEncoder.encode_and_write(episodes)`.
4. `cue_i = episode_i` with `fraction_zeroed` dims zeroed (per-query random mask, seed-fixed).
5. `HippocampalEncoder.retrieve(cues, use_ca3=True, sparsify_after_settle=True)`.
6. recall@1 = fraction where `argmax_j cos(completed_cue_i, stored_dg_j) == i`.

### Regime axes

- N ∈ {50 (regression: 4.8% of C_TF), 500 (48%), 800 (76%)}
- codebook ∈ {random (regression, independent bipolar), adversarial (cluster-shared role_key + fillers with within-cluster cos ≈ 0.64 ≥ 0.60)}
- corruption ∈ {0.50 (regression), 0.75, 0.90}

### Adversarial codebook construction (`_draw_pairs_adversarial`)

For each cluster of `CLUSTER_SIZE=5` pairs:
- Draw one anchor role_key (shared across the cluster) and one anchor filler.
- Each of the 5 members has `filler_member = anchor_filler` with `n_flip = round(0.10 * n_dim)` random dims flipped. Bipolar cos(anchor_filler, filler_member) = 1 - 2 * 0.10 = 0.80 (each individually) → expected cos(filler_a, filler_b) within cluster ≈ (1 - 0.20)² + 0.10² - 2*0.10*0.80 ≈ 0.68 ≥ 0.60 lower-bound.
- Since role_key is shared within cluster: cos(episode_a, episode_b) = cos(filler_a, filler_b) (role_key cancels out under elementwise product).
- THEORETICAL@ bipolar-cos formula: cos = (n_agree - n_disagree)/n_dim = 1 - 2*flip_frac.
- Selftest verifies observed within-cluster mean cos ≥ 0.60 across at least 100 pair-comparisons.

### Chunk-checkpoint

Per-seed `partial_metrics_<seed>.json` written atomically after each seed completes (SH-4).

## Arms (12 arms × 3 seeds = 36 units)

`EXPECTED_N_UNITS = 12 * 3 = 36`

| # | Arm | N | Codebook | Corrupt | Role |
|---|-----|---|----------|---------|------|
| A | ARM_REGRESSION_HIPPOCAMPAL_N50_RANDOM_50CORRUPT | 50 | random | 0.50 | regression |
| B | ARM_REGRESSION_HIPPOCAMPAL_DG_ONLY_N50_RANDOM_50CORRUPT | 50 | random | 0.50 | regression |
| C | ARM_REGRESSION_COSINE_BASELINE_N50_RANDOM_50CORRUPT | 50 | random | 0.50 | regression |
| D | ARM_HIPPOCAMPAL_N500_ADVERSARIAL_75CORRUPT | 500 | adversarial | 0.75 | LOAD_BEARING (HP1 warmup) |
| E | ARM_HIPPOCAMPAL_N500_ADVERSARIAL_90CORRUPT | 500 | adversarial | 0.90 | LOAD_BEARING (HP1 + HP2 primary) |
| F | ARM_HIPPOCAMPAL_N800_ADVERSARIAL_75CORRUPT | 800 | adversarial | 0.75 | approach-capacity |
| G | ARM_HIPPOCAMPAL_DG_ONLY_N500_ADVERSARIAL_75CORRUPT | 500 | adversarial | 0.75 | DG-only ablation |
| H | ARM_HIPPOCAMPAL_DG_ONLY_N500_ADVERSARIAL_90CORRUPT | 500 | adversarial | 0.90 | DG-only ablation |
| I | ARM_COSINE_BASELINE_N500_ADVERSARIAL_75CORRUPT | 500 | adversarial | 0.75 | baseline (must degrade) |
| J | ARM_COSINE_BASELINE_N500_ADVERSARIAL_90CORRUPT | 500 | adversarial | 0.90 | baseline (should collapse) |
| K | ARM_COSINE_BASELINE_N800_ADVERSARIAL_75CORRUPT | 800 | adversarial | 0.75 | baseline |
| L | ARM_RANDOM_BASELINE_N500 | 500 | n/a | n/a | chance floor |

**arms_differ_verified:** hash-check per (seed × arm) on the retrieval-query prefix. `arms_differ_exempted`: regression arms A/B/C SHARE INPUT `episodes` (same draw for regression coherence) — exempted from bit-identity check WITHIN a seed since encoders differ. All other pairs must differ.

## Regime constants

- N_DIM = 2048
- DG_DIM = 8192 (4x expansion)
- SPARSITY = 0.02 (top-K by magnitude; ~164 active DG dims)
- CLUSTER_SIZE = 5 (adversarial cluster size)
- ADVERSARIAL_FLIP_FRAC = 0.10 (bipolar flip fraction within cluster → cos ~0.80 filler-to-anchor, ~0.64 filler-to-filler)
- Seeds: [11, 17, 23]
- Chance recall@1 = 1/N per arm.
- C_TF at dg_dim=8192, p=0.02: 1047 patterns (THEORETICAL@ Tsodyks-Feigelman 1988).
- Load fractions: N=50 → 4.8%; N=500 → 48%; N=800 → 76%.

## HP bands (LOAD_BEARING)

`HP_SCOPE`:
- HP1 applies to ARM_HIPPOCAMPAL_N500_ADVERSARIAL_90CORRUPT (mechanism holds under stress).
- HP2 applies to `ARM_HIPPOCAMPAL_N500_ADVERSARIAL_90CORRUPT - ARM_COSINE_BASELINE_N500_ADVERSARIAL_90CORRUPT` (mechanism-vs-baseline separation).
- REGRESSION applies to arms A, B, C at N=50.
- HF-baseline applies to ARM_RANDOM_BASELINE_N500.

### HARD_PASS

| # | Metric | Threshold | Applies to |
|---|--------|-----------|------------|
| HP1 | recall@1 | >= 0.70 | ARM_HIPPOCAMPAL_N500_ADVERSARIAL_90CORRUPT |
| HP2 | recall@1 delta | >= 0.20 | HIPPO_N500_ADV_90 - COSINE_N500_ADV_90 |
| REGRESSION | recall@1 | == 1.000 for all encoder arms | A, B, C at N=50 random 0.50 (bit-identical to prior) |

Both HP1 AND HP2 required for HARD_PASS. HP threshold rationale: at 48% of T-F capacity + adversarial-cluster interference + 90% corruption, mechanism-appropriate threshold is 0.70 (HYPOTHESIZED@ from primitive selftest scaling); a >= 0.20 gap over cosine baseline separates encoded-decorrelation from raw-similarity retrieval (HYPOTHESIZED@ mechanism claim strength).

### HARD_FAIL

| # | Condition | Implication |
|---|-----------|-------------|
| HF-separation | HIPPO r@1 <= COSINE r@1 + 0.05 at BOTH ADVERSARIAL_75CORRUPT AND ADVERSARIAL_90CORRUPT | No mechanism-vs-baseline separation anywhere. Task-class-mismatch hypothesis is REFUTED; substrate structural mechanisms may have deeper problem. |
| HF-regression | any regression arm r@1 < 0.95 | Code drift from predecessor cell; cannot trust discriminating verdict. |
| HF-baseline | ARM_RANDOM_BASELINE_N500 r@1 > 5/500 = 0.01 | META_RULE_AG baseline_in_band violation; retrieval-implementation bug. |
| HF-dg-rate | any HIPPO arm dg_sparse_rate out of [0.008, 0.040] | Architectural sanity (target 0.02, band 2x either side). |
| HF-cardinality | actual_n_units < 36 | META_RULE_H cardinality breach. |

### MIDDLE_BAND

Any of: 0.05 < (HIPPO - COSINE separation) < 0.20 at N=500 ADV 90; HIPPO r@1 in [0.50, 0.70); ADV_75CORRUPT separates but ADV_90CORRUPT does not. Partial mechanism validation; further probes needed.

## Envelope-fail bands

- ARM_RANDOM_BASELINE_N500 recall@1 expected [0.0, 0.01] (chance 0.002 at N=500; 5x chance band).
- HIPPO arms dg_sparse_rate expected [0.008, 0.040] (target 0.02).
- COSINE_BASELINE_N500_ADV_90 recall@1 expected ~[0.05, 0.40] (partial-cue in n_dim=2048 at 90% corruption + adversarial-cluster interference — baseline expected to degrade substantially).
- COSINE_BASELINE_N500_ADV_75 recall@1 expected ~[0.20, 0.60].
- HIPPO_N500_ADV_75 expected [0.75, 0.95] (mechanism handles moderate stress).
- HIPPO_N500_ADV_90 expected [0.65, 0.90] (mechanism handles high stress).
- HIPPO_N800_ADV_75 expected [0.60, 0.85] (approach-capacity).
- REGRESSION arms expected == 1.000 (bit-identical to predecessor).

## Cell-template compliance

- `arms_differ_verified` at smoke gate (META_RULE_AF; per-seed per-arm hash check on retrieval query prefix). Regression arm-pair A/B/C exempted (shared input episodes, encoders differ).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` BEFORE `except Exception` (no `except BaseException`).
- `baseline_in_band` verified in verdict logic (META_RULE_AG).
- `cardinality_ok` = actual_n_units >= 36 (12 arms × 3 seeds).
- Per-unit `failure_class` instrumentation (META_RULE_J).
- `start_marker_written`, `_heartbeat.jsonl`, crash-diagnostic write.
- Per-seed checkpoint (SH-4) via `partial_metrics_<seed>.json` atomic tmp-replace.
- Default `_parse_args()` mode is `smoke`.
- Numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ (META_RULE_AC).
- `progress_logging: print_flush_true` (line-buffered stdout + explicit flush).

## SCHEMA-VET gates

- **sweep_alignment_verdict: ALIGNED** — swept parameters (N, codebook, corruption) are the effective parameters at all three encoder types (no partition-routing).
- **discriminating_fraction: 0.75** — 9/12 arms are in the discriminating regime (D, E, F, G, H, I, J, K, L); 3/12 are regression at the too-easy regime (bit-identical to prior HP for code-integrity check). All 9 discriminating arms predicted to land in [0.05, 0.95] band.
- **composition_edges** — none (no primitive-primitive composition; encoder-only).
- **positive_control_arms** — REGRESSION arms A, B, C at N=50 random 50% reproduce prior cell's per-arm r@1=1.000 (tolerance 0.05). Same `_draw_pairs` + `_corrupt_cue` + same seeds → bit-identical reproduction expected.
- **functional_requirements**:
  - FR1: one-shot binding at higher capacity load (48-76% of C_TF) — mechanism: HippocampalEncoder DG expansion + CA3 Hebbian outer product.
  - FR2: decorrelation of adversarially-correlated input codebook — mechanism: DG random-projection + top-K sparsification (JL-lemma-adjacent).
  - FR3: partial-cue pattern completion under high corruption — mechanism: CA3 auto-associator single-step settle over top-K.
- **crlb_n/a**: "Task is retrieval-accuracy over sparse-attractor cleanup; no closed-form CRLB. Discriminator = mechanism-vs-baseline gap; capacity-feasibility is Tsodyks-Feigelman C_TF=1047 patterns, well above tested N=800."
- **discriminator_reachability: True** — HP1 (0.70) and HP2 (0.20 separation) are both below capacity-feasibility ceilings (T-F allows ≥0.90 recall at N ≤ ~700; adversarial + 90% corruption may pull to ~0.70).

## Compute architecture

- (a) batched-CPU-numpy (no GPU needed; batched matmul via BLAS).
- Storage strategy: SHARDED per-episode DG codes (each episode is a distinct CA3 attractor).
- Per-seed smoke wall estimate:
  - Regression arms: ~5s combined.
  - N=500 HIPPO arms (D, E, plus G, H DG-only): 3 hippocampal encoders + 2 DG-only. Each hippocampal ~60s (DG expand + CA3 outer + batched settle at DG_DIM=8192). Total ~200s.
  - N=800 HIPPO arm F: ~120s.
  - N=500/800 COSINE + RANDOM arms: ~10s combined.
- Estimated total per seed: 6-8 min. 3 seeds → 18-24 min wall.
- Timeout: 3600s (60 min) with safety margin.

## Selftests (`--self-test`)

Chain to `python -m hdlab.hippocampal_encoder --self-test` (13 primitive selftests) + 6 cell-level integration selftests:

1. `arg_parse_default_is_smoke`
2. `corrupt_cue_correct_fraction` (0.50, 0.75, 0.90 each)
3. `mini_binding_recall_random` (N=10 pairs, dg_dim=2048, random-codebook: recall@1 >= 0.80)
4. `arms_differ_hash_micro` (HIPPOCAMPAL vs DG_ONLY completed cues differ)
5. `adversarial_codebook_within_cluster_cos` (observed mean within-cluster filler-to-filler cos >= 0.60 across 100 comparisons at n_dim=2048)
6. `regression_arm_bit_identical` (reproduce predecessor at N=50 random 50% seed=11 → r@1==1.000 for HIPPO_ONE_SHOT)

Total: 13 primitive + 6 cell = 19 selftests, all must pass before dispatch.

## Post-smoke gating

Report per-arm recall@1 mean + std; per-seed timings; DG sparse rate; per-arm mechanism-vs-baseline separation; verdict; honest interpretation whether task-class-mismatch hypothesis is PROVEN / REFUTED / partially validated. Do NOT dispatch FULL. Verdict feeds Director's re-evaluation of substrate structural mechanisms scope.
