# PRE-REG: Stage 2 VSA Cell 4 (episodic-formal) DISCRIMINATIVE-REGIME smoke

**Anchor:** `substrate_vsa_cell4_episodic_formal_discriminative_smoke_2026_07_03`
**Cell file:** `experiments/exp_substrate_vsa_cell4_episodic_formal_discriminative_smoke_2026-07-03.py`
**Primitive file:** `hdlab/hippocampal_encoder.py` (13/13 selftests, CG'd)
**Filed:** 2026-07-03
**Author:** hdi_exp_dev
**Run mode:** SMOKE-only (USER-locked SMOKE-only-on-local_cpu per 2026-07-01).

## Scope

Stage 2 VSA-suite Cell 4 (episodic-formal): refine Spoke 3 W2 (episodic-binding) `regime-too-easy` caveat + Gate 2 close `regime-insufficient` HF by moving to a genuinely discriminative regime per Skunkworks-verified analytical prediction. Refines an OPEN caveat rather than adding a shallow 6th witness (Scope A per hand-off).

**DO NOT frame as CG_META promotion attempt** (Skunkworks explicit directive 2026-07-03). This cell is a WIN-witness-at-discriminative-regime refinement of the existing W2 caveat, not a promotion probe.

## Question

At an ADVERSARIAL_CLUSTER codebook with within-cluster cos ~ 0.90 (via `flip_frac = 0.026`), N = 500 pairs (~48% of Tsodyks-Feigelman capacity C_TF = 1047), and 75% partial-cue corruption, does the brain-analog Marr-CA3 + DG-expansion primitive `hdlab.hippocampal_encoder` measurably OUTPERFORM plain-cosine-argmax on episodic one-shot binding + partial-cue retrieval - the SAME task class as Spoke 3 CLS episodic?

Prior cells at cluster_cos ~ 0.64 (`flip_frac = 0.10`) left COSINE r@1 = 1.000 (Gate 2 close, commit `13f479fc6` MEASURED@ `data/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_gate2_close_smoke_2026_07_03/metrics.json`): baseline saturated -> discriminator did NOT fire. Skunkworks analytical prediction: at cluster_cos ~ 0.90, sig-sib = 0.022 vs sib_std = 0.017 -> z_sib_beats ~ 1.29 -> P(sib > signal) ~ 10% -> cosine baseline expected to genuinely DEGRADE.

## Framing discipline (LOAD-BEARING per USER 2026-07-02 + Skunkworks 2026-07-03)

- SUBSTRATE KNOWS ALMOST NOTHING. Mechanism probe on SUPERVISED synthetic (role_key, filler) binding task. NOT a general-knowledge claim. NOT a language capability claim.
- **DO NOT frame as CG_META promotion attempt** (Skunkworks explicit).
- Skunkworks-corrected T-F formula: `C_TF = dg_dim / (2 * ln(1/sparsity))`. At dg_dim=8192, sparsity=0.02: C_TF = 8192 / (2 * 3.912) = 1047 patterns. THEORETICAL@ Tsodyks-Feigelman 1988.
- Skunkworks-verified cluster_cos formula for bipolar with independent random flip masks of size `f * d` per member: `cos(member_a, member_b) = 1 - 4*f*(1-f)`. At f=0.026: cos = 1 - 0.10125 = 0.8987 ~ 0.90. THEORETICAL@.
- If HP1..HP4 all fire: legitimate WIN witness at discriminative regime; refines W2 caveat; potentially satisfies Skunkworks-flagged missing discriminative-regime witness type.
- If HF: mechanism fails even at discriminative regime; W2 caveat becomes STRONGER (mechanism may have deeper issue).
- If MB: some HP fire, not all four; partial witness.
- All numbers below tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ per META_RULE_AC.

## Prior-work check (substrate-KB concept-query 2026-07-03)

Ran `bash tools/substrate_query.sh "episodic binding discriminative regime adversarial cluster partial cue Skunkworks"`:
- Rank 1: `Discriminating regime` cosine=0.3223 (generic term across preregs; unrelated to specific regime).
- Rank 2: `Why discriminative + binding > discriminative alone` cosine=0.3057 (Path 1/3 note; adjacent).
- Rank 3: `Discriminating regime added` cosine=0.2920 (v2 pre-reg addendum; adjacent).

Prior-work check: NONE at cosine > 0.36 for the specific probe (Cell 4 = flip_frac=0.026 cluster_cos~0.90 discriminative regime). NOVEL cell. Prior Spoke 3 cells at commits `96d9055e5`, `1d8b0ec44`, `13f479fc6` are ancestors this cell explicitly builds on (regression arms bit-identical to `96d9055e5` for code-integrity).

## Compute architecture

- Class: **(b) sequential-CPU** with justification.
- Justification: encoder-per-arm CPU wall is bounded (see wall estimate). Substrate primitives (DGProjection, CA3AutoAssociator) are numpy-based and the cell is the substrate-primitive being validated (bit-identical CPU reference). Total smoke wall estimated < 15 min at N_arms=12, seeds=3.
- Storage strategy: **sharded** (each episode is one HD; CA3 outer-product summed only as Hebbian associative weight matrix, not as composed retrieval vector). Retrieval is single-hop cleanup against per-item DG codes. No downstream composition.

## Task protocol

Per seed: for each (N, codebook, corruption) regime, draw pairs, form episodes, one-shot write, partial-corrupt-cue retrieve, score.

### Task class (SAME as predecessor Spoke 3 cells)

1. Draw N pairs of role_key/filler HDs in R^n_dim (n_dim=2048, bipolar {-1,+1}).
2. `episode_i = role_key_i * filler_i` (elementwise bind).
3. `HippocampalEncoder.encode_and_write(episodes)`.
4. `cue_i = episode_i` with `fraction_zeroed` dims zeroed (per-query random mask, seed-fixed).
5. `HippocampalEncoder.retrieve(cues, use_ca3=True, sparsify_after_settle=True)`.
6. recall@1 = fraction where `argmax_j cos(completed_cue_i, stored_dg_j) == i`.

### Regime axes

- N in {50 (regression, 4.8% of C_TF), 500 (48%), 800 (76%)}
- codebook in {random (regression), adversarial_cluster (Skunkworks discriminative)}
- corruption in {0.50 (regression), 0.75 (PRIMARY), 0.90 (extended)}

### Adversarial-cluster codebook construction (`_draw_pairs_adversarial`)

Per cluster of `CLUSTER_SIZE = 5` pairs:
- Draw one anchor role_key (shared across cluster) and one anchor filler.
- Each of 5 members has `filler_member = anchor_filler` with `n_flip = round(0.026 * n_dim)` random dims flipped (per-member independent).
- Since role_key is shared within cluster: `cos(episode_a, episode_b) = cos(filler_a, filler_b)` (role_key cancels).
- THEORETICAL@ cos(anchor, member) = 1 - 2 * 0.026 = 0.948.
- THEORETICAL@ cos(member_a, member_b) = 1 - 4 * 0.026 * (1 - 0.026) = 0.8987 ~ 0.90.
- Selftest verifies observed within-cluster mean cos in [0.85, 0.95] across at least 100 pair-comparisons.

## Arms (12 arms x 3 seeds = 36 units)

`EXPECTED_N_UNITS = 12 * 3 = 36`

| # | Arm | N | Codebook | Corrupt | Role |
|---|-----|---|----------|---------|------|
| A | ARM_REGRESSION_HIPPOCAMPAL_N50_RANDOM_50CORRUPT | 50 | random | 0.50 | regression |
| B | ARM_REGRESSION_HIPPOCAMPAL_DG_ONLY_N50_RANDOM_50CORRUPT | 50 | random | 0.50 | regression |
| C | ARM_REGRESSION_COSINE_BASELINE_N50_RANDOM_50CORRUPT | 50 | random | 0.50 | regression |
| D | ARM_HIPPOCAMPAL_N500_ADV_CLUSTER_75CORRUPT | 500 | adv_cluster | 0.75 | LOAD_BEARING PRIMARY |
| E | ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_CLUSTER_75CORRUPT | 500 | adv_cluster | 0.75 | CA3 ablation PRIMARY |
| F | ARM_COSINE_BASELINE_N500_ADV_CLUSTER_75CORRUPT | 500 | adv_cluster | 0.75 | baseline PRIMARY |
| G | ARM_HIPPOCAMPAL_N500_ADV_CLUSTER_90CORRUPT | 500 | adv_cluster | 0.90 | LOAD_BEARING extended |
| H | ARM_HIPPOCAMPAL_DG_ONLY_N500_ADV_CLUSTER_90CORRUPT | 500 | adv_cluster | 0.90 | CA3 ablation extended |
| I | ARM_COSINE_BASELINE_N500_ADV_CLUSTER_90CORRUPT | 500 | adv_cluster | 0.90 | baseline extended |
| J | ARM_HIPPOCAMPAL_N800_ADV_CLUSTER_75CORRUPT | 800 | adv_cluster | 0.75 | approach capacity |
| K | ARM_COSINE_BASELINE_N800_ADV_CLUSTER_75CORRUPT | 800 | adv_cluster | 0.75 | baseline approach cap |
| L | ARM_RANDOM_BASELINE_N500 | 500 | n/a | 0.0 | chance floor |

## HP band (PRIMARY regime = N=500 ADV_CLUSTER 75-corrupt)

- **HP1**: `ARM_HIPPOCAMPAL_N500_ADV_CLUSTER_75CORRUPT` recall@1 >= 0.60. HYPOTHESIZED@ mechanism-appropriate at 48% C_TF + cluster_cos ~ 0.90 + 75% corruption; degraded from ~ 1.000 predecessor MEASURED@ but well above chance = 0.002.
- **HP2 (discriminator FIRES)**: `ARM_COSINE_BASELINE_N500_ADV_CLUSTER_75CORRUPT` recall@1 <= 0.85. HYPOTHESIZED@ Skunkworks analytical: at cos ~ 0.90 sib_std = 0.017 -> ~ 10% sib-beats-signal -> cosine r@1 should drop 10-30% below saturation at 75-corrupt.
- **HP3**: HIPPO - COSINE r@1 delta >= 0.10 at PRIMARY. HYPOTHESIZED@ separation strong enough to reject "encoders identical to cosine" hypothesis.
- **HP4**: HIPPO - DG_ONLY r@1 delta >= 0.05 at PRIMARY. HYPOTHESIZED@ CA3 pattern-completion earns its keep over DG-only expansion; below 0.05 means CA3 is not load-bearing at this regime.

**Cardinality:** `cardinality_ok = True` iff `actual_n_units >= 36`.

## HF classes

- HF-regression: any regression arm r@1 < 0.95 (bit-identical reproduction fails -> code drift).
- HF-baseline (META_RULE_AG): `ARM_RANDOM_BASELINE_N500` r@1 > 0.01 (chance = 0.002; band 5x chance = 0.010).
- HF-dg-rate: HIPPO dg_sparse_rate out of [0.008, 0.040].
- HF-nodisc: `ARM_COSINE_BASELINE_N500_ADV_CLUSTER_75CORRUPT` r@1 > 0.95 (discriminator did NOT fire; regime insufficient even at cluster_cos ~ 0.90).
- HF-nomech: HIPPO - COSINE <= 0.05 at BOTH 75 AND 90 ADV regimes (mechanism does not beat baseline; W2 caveat STRONGER).
- HF-card (META_RULE_H): actual_n_units < 36.

## MIDDLE_BAND

Some but not all four HP fire at PRIMARY, and no HF trigger.

## SCHEMA-VET gate compliance

- `cardinality_ok`: enforced via EXPECTED_N_UNITS = 36 check; HF-card if not met.
- `arms_differ_verified`: hash check at smoke-time across all non-regression arms; regression arm-group (A/B/C) exempted (share input episodes at N=50 random; encoder outputs still differ within group; documented).
- `final_metrics_atomicity`: `tmp_replace` (write to `metrics.json.tmp` then `os.replace`).
- `baseline_in_band` (META_RULE_AG): `ARM_RANDOM_BASELINE_N500` r@1 in [0, 0.010]; HF if breached.
- `crlb_n/a`: THEORETICAL@ argmax cleanup accuracy has no CRLB floor in the classical sense; retrieval bound is 1/N (chance) = 0.002 at N=500. HP1 = 0.60 = 300x chance, far above floor.
- `discriminator_reachability`: True. Prior cells hit chance-floor and near-saturation on cosine at various regimes, confirming both directions reachable.
- `predicted_accuracy_per_point` (gate B, `bracket_includes_discriminating_band`): mechanism arms predicted in [0.60, 0.85] band; baseline predicted in [0.65, 0.90] band; separation in [0.10, 0.35]; ALL PRIMARY sweep points expected in discriminating band [0.30, 0.90] -> `discriminating_fraction = 1.0` for primary regime.
- `composition_edges` (gate C): no compositional pipeline; single primitive validation; SHAPE_MATCH within DG->CA3 (existing CG'd primitive).
- `positive_control_arms` (gate D): regression arms (A/B/C) reproduce predecessor MEASURED@ `data/exp_substrate_spoke3_hippocampal_encoder_episodic_binding_smoke_2026_07_03/metrics.json` r@1 = 1.000 with tolerance 0.05.
- `sweep_alignment_verdict`: ALIGNED (N + corruption + codebook parameters are the effective parameters each encoder experiences).
- `functional_requirements`: (1) one-shot episodic binding -> DG expansion + CA3 Hebbian outer product (CG'd in `hdlab.hippocampal_encoder`); (2) partial-cue retrieval -> CA3 settle + DG re-sparsify (CG'd); (3) baseline degradation at cluster_cos ~ 0.90 -> plain cosine on raw episodes.
- `calibration_check`: `default_ok_for_this_regime` + Skunkworks analytical evidence (sig-sib = 0.022 vs sib_std = 0.017; z_sib_beats ~ 1.29).
- `progress_logging`: `print_flush_true` (line-buffered stdout via `sys.stdout.reconfigure` at cell start; per-arm print with `flush=True`).
- `cell_chunked`: False (single-seed loop within one cell; 3 seeds x 12 arms; smoke wall estimate < 15 min).
- `start_marker_written`: True (`_write_start_marker` at main() entry).
- `crash_diagnostic_present`: True (outer try/except in `__main__` with `_write_crash_metrics`; `except SystemExit: raise` BEFORE `except Exception`).
- `heartbeat_present`: True (`_heartbeat` per arm).
- `defensive_error_checking`: `passed_all_4_patterns`.
- `arms_must_differ_verified`: True (bit-identical arm bug guard).
- HP_SCOPE per-arm declaration: emitted in metrics.json under `hp_scope`.

## DISCRIMINATOR-MUST-SURVIVE-SCALE (option B: analytical justification)

Per Skunkworks 2026-07-03 analytical model:
- At cluster_cos = 0.899 (flip_frac = 0.026), the signal (correct-match cos = 1.0 baseline before corruption) vs sibling (in-cluster incorrect-match cos ~ 0.899 before corruption) leaves margin ~ 0.10 pre-corruption.
- 75% partial-cue corruption zeros 75% of dims -> reduces effective inner-product SNR by ~ 4x.
- Result: sig-sib = 0.022, sib_std = 0.017, z_sib_beats ~ 1.29 -> P(sib > signal) ~ 10% -> cosine r@1 expected 0.60 - 0.90 range.
- Mechanism (DG expansion + CA3 Hebbian settle) is invariant to cluster_cos structure once DG codes are per-item sparse-distinct (dg_dim = 8192 gives ample capacity at N=500).
- Expected mechanism r@1 = 0.75 - 0.95.
- Expected separation = 0.10 - 0.30 at PRIMARY.

Smoke uses full N=500 at N_DIM=2048 DG_DIM=8192 (bit-identical to intended sweep of the discriminator). Discriminator fires at smoke = fires at full.

## Timeout estimate

Smoke wall: ~ 10-15 min at 12 arms x 3 seeds on local CPU (dominated by N=500 and N=800 CA3 outer-product + settle). Per-arm ~30-60s at N=500; ~1-2 min at N=800. Total: 12 * 60 = 720s + 2*120 = 240s -> ~ 16 min ceiling. Cell timeout: 3600s (60 min ceiling; per Skunkworks 1.5x smoke wall * 3x margin for load variance).

## Route

- Selftest: `python experiments/exp_substrate_vsa_cell4_episodic_formal_discriminative_smoke_2026-07-03.py --self-test` (must exit 0; 7 selftests pass).
- Smoke: local_cpu_queue via `python tools/queue_add.py local_cpu_queue <entry> <script> --prereg <this file> --timeout 3600` (USER-locked SMOKE-only-on-local_cpu 2026-07-01).
- FULL: HARD HOLD post-smoke until Director + Skunkworks decision (cell is smoke-only per Stage-2 VSA-suite discipline).
