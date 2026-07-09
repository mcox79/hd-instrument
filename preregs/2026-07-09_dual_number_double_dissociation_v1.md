# Pre-reg: exp_dual_number_double_dissociation_v1

**Anchor:** `exp_dual_number_double_dissociation_v1`
**Script:** `experiments/exp_dual_number_double_dissociation_v1.py`
**Filed:** 2026-07-09 by exp_dev
**Source:** `notes/research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md` (Prediction 1 / "cheap decisive test")
**Prior-work check:** substrate-KB top hit `exp_weber_fraction_duration_discrimination_v1` cosine=0.3604 (a single temporal Weber-fraction magnitude cell; shared conceptual ancestor but NOT this probe). Rest of KB hits are WordNet "discrimination" word-sense noise. This cell is genuinely novel: it tests a DOUBLE DISSOCIATION between two structurally-distinct number primitives, not one magnitude fraction.

## Question
Is baking in TWO structurally-distinct number primitives (small-exact addressable pointer-array + continuous ratio/Weber magnitude code) worth the complexity over ONE unified magnitude representation? Test via a clean DOUBLE DISSOCIATION a la Hyde & Spelke 2011 (CITED: distinct ERP N1/P2p + psychophysical signatures for small-exact vs large-approximate number).

## Design (clean synthetic data; NO substrate state)
- **Substrate:** bipolar BSC {-1,+1}, N=8192. bind = elementwise mul; bundle = sum; unbind = self-inverse mul; cleanup = codebook argmax cosine.
- **POINTER-ARRAY channel (parallel-individuation analog):** S=4 fixed slots (CITED Feigenson & Carey 2005 ~3-4 object-file limit); scene = sum of bind(slot_role_i, token_i); per-slot unbind+cleanup recovers identity-at-slot. Capacity-limited to S.
- **MAGNITUDE channel (ANS analog):** unnormalized bundle whose L2 norm ~ sqrt(count) (Weber-scaled), plus a familiarity cosine. No slot, no identity; unbounded cardinality.
- **Task (a) EXACT identity-at-slot after occlusion** (counts {1,2,3,4}, F_OCC=0.15 sign-flip). Negatives 50/50: (i) X absent, (ii) X present but at a DIFFERENT slot -> familiarity/magnitude says 'present' and gets it WRONG; only pointer answers correctly.
- **Task (b) RATIO discrimination** "is A>B" (n in {8,16,32}, ratios 1:2 and 2:3, F_B=0.10). Both scenes overflow S=4 -> pointer count-estimate caps at 4 for both -> cannot discriminate; only magnitude norm can.
- **SHARED trained readout** per task (numpy logistic regression) over features from BOTH channels, trained on CLEAN train split, evaluated on held-out test split (test scenes disjoint from train; held-out methodology). Giving the readout both channels makes "one unified code suffices" a real alternative, not a straw man.

## PAIRED ablation (mandatory)
ONE trial set per seed scored under 3 conditions on identical scenes/seed: CLEAN / POINTER_ABLATED (slot roles randomized -> unbind noise) / MAGNITUDE_ABLATED (scene norm + familiarity replaced by noise). Deltas are paired. Readout trained on CLEAN; ablation applied at TEST (causal-lesion logic).

## Discriminator + BANDS (pre-registered BOTH before running)
- delta_a_pointer = acc_a(clean) - acc_a(pointer_ablated) ; delta_b_pointer analog.
- delta_a_mag, delta_b_mag analog for magnitude ablation.
- R_pointer = max(delta_a_pointer,0) / max(delta_b_pointer, 1e-6) (capped 100).
- R_mag = max(delta_b_mag,0) / max(delta_a_mag, 1e-6) (capped 100).
- MIN_EFFECT = 0.08 (a delta must clear this to count as a real effect).

**HARD_PASS** (bake in two systems, not one): R_pointer >= 2.0 AND R_mag >= 2.0, with delta_a_pointer >= MIN_EFFECT AND delta_b_mag >= MIN_EFFECT, AND majority of seeds individually HARD_PASS. Clean double dissociation both directions.

**HARD_FAIL** (one unified magnitude code suffices): a real ablation effect present (max delta >= MIN_EFFECT) AND R_pointer <= 1.3 AND R_mag <= 1.3 AND majority of seeds individually HARD_FAIL. Ablating either channel degrades both tasks roughly equally.

**MIDDLE_BAND:** dissociation one direction only (mixed).
**INCONCLUSIVE_NO_ABLATION_EFFECT:** no ablation moved any task (mechanism inert; should be caught at smoke).

Both outcomes are gold per task framing.

## SCHEMA-VET fields
- `cardinality_ok`: true. EXPECTED_N_UNITS = n_seeds = 3 (FULL) / 1 (SMOKE). Verdict counts len(per_seed); < expected -> HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- `arms_differ_verified`: true (smoke asserts CLEAN / POINTER_ABL / MAG_ABL feature matrices are bit-distinct via sha256; META_RULE_AF).
- `final_metrics_atomicity`: "tmp_replace" (write_metrics tmp+os.replace) + per-seed write_partial checkpoint.
- `except SystemExit: raise` before `except Exception` (no BaseException; no bare except). Grep-gate clean.
- `crlb_n/a`: "discriminator is an ablation-delta RATIO (paired lesion effect), not a noise-floor point estimate; no Cramer-Rao floor applies. Feasibility instead governed by bind/unbind cosine SNR ~ 1/sqrt(c) at c<=4 (~0.5 at c=4, THEORETICAL) which is >> the classification threshold; magnitude norm ratio ~ sqrt(nA/nB) (2:3 -> 0.816, THEORETICAL) is comfortably discriminable."
- `discriminator_reachability`: true (smoke MEASURED d_a_pointer=0.527, d_b_mag=0.513, both >> MIN_EFFECT=0.08).
- `baseline_in_band` (META_RULE_AG reframed): the discriminating quantity is the paired ablation DELTA, not a mid-band arm accuracy. Gate: clean acc in [0.60, 1.0001] (room to drop) AND ablated acc drops. Smoke MEASURED clean_a=1.000, clean_b=0.993; pointer-ablated a=0.473; mag-ablated b=0.480.
- `calibration_check`: "default_ok_for_this_regime" (clean synthetic corpus; channel params chosen by analytical SNR, not tuned-for-PASS).
- `progress_logging`: "print_flush_true" (per-seed print(flush=True) + CellHeartbeat every 30s).
- `cell_chunked`: false. Justification: total FULL wall ~6 min, per-seed ~2 min; per-seed write_partial + resumable_seeds checkpointing means a runner death loses <=1 seed of ~2min work; chunking to 3 files adds dispatch overhead disproportionate to a sub-10-min cell. Per-seed checkpoint/resume satisfies the spirit of §13A.
- `start_marker_written`: true. `crash_diagnostic_present`: true (Exception -> CELL_CRASHED metrics + traceback). `heartbeat_present`: true. `defensive_error_checking`: "passed_all_4_patterns".

## §15 composition/sweep gates
- Gate A `sweep_alignment_verdict`: N/A (no partition-routed nominal-vs-effective sweep; counts/ratios are task-defining, not a discriminator sweep axis). ALIGNED trivially.
- Gate B `discriminating_fraction`: N/A as a per-sweep-point band; discriminator is the dissociation ratio. Predicted (and MEASURED@smoke) accs land in discriminating regime: clean ~0.99-1.00, ablated ~0.47-0.53 (near chance). Effect magnitude ~0.5 >> MIN_EFFECT.
- Gate C `composition_edges`: pipeline bind -> unbind -> cos/cleanup -> logistic-readout; all shapes match (N-vectors -> scalar features -> LR). SHAPE_MATCH.
- Gate D `positive_control`: the pointer channel's CLEAN exact-tracking acc (task a) IS the in-regime positive control that bind/unbind fidelity holds at N=8192,S=4,c<=4; MEASURED@smoke = 1.000. Novel regime (no external chain-grade atom to cite); reproduction is self-contained at the test regime. SHAPE_MATCH (synthetic clean).
- Gate E `functional_requirements`:
  1. Exact identity-at-slot tracking under corruption -> pointer-array unbind+cleanup (bind primitive).
  2. Ratio/cardinality judgment of large sets -> magnitude bundle L2 norm (bundle primitive).
  3. Causal dissociation measurement -> paired ablation deltas (lesion logic).
  4. Fair "unified code" null -> shared readout with access to both channels.

## Vacuous-smoke guard (assert_discriminator_fires)
Frontier/negative control = shuffled-label readout. It MUST fail the double-dissociation headline (labels destroyed -> no channel predicts -> deltas ~0). Smoke passes control_dissociation=False -> assert_discriminator_fires does not raise. Verified.

## Smoke result (MEASURED@data/exp_dual_number_double_dissociation_v1_smoke/metrics.json)
- run_mode=smoke, full N=8192, 1 seed [7], m_train=200/m_test=150, wall ~34s.
- verdict=HARD_PASS; R_pointer=100.0 (d_a|ptr=0.527 vs d_b|ptr=0.000); R_mag=100.0 (d_b|mag=0.513 vs d_a|mag=0.000); clean acc a=1.000 b=0.993.
- smoke_discriminator_fires=True; arms_differ_verified=True; clean_acc_in_band=True; 6/6 structured gates PASS.

## Compute architecture
- **Class: (b) sequential-CPU with justification.** Total FULL wall ~6 min; pure numpy elementwise bind (mul) + bundle (sum) + small codebook-cleanup matmuls (V=64 x N=8192). No GPU-batchable independent-phase-point sweep; per-trial loop is trivially cheap. Wall < the batching-candidate threshold at the per-seed level.
- **Storage strategy: no_storage / no_composition** (probe over freshly-generated synthetic scenes; no PartitionedStore writes; no chained retrieval).

## Config
N_DIM=8192, S_SLOTS=4, V_TOK=64, F_OCC=0.15, F_B=0.10, CLEANUP_THRESH=0.20.
Task_a counts {1,2,3,4}; Task_b pairs {(8,16),(16,8),(16,32),(32,16),(16,24),(24,16),(8,12),(12,8)}.
SEEDS_FULL=[7,17,23]; M_TRAIN_FULL=800, M_TEST_FULL=500.
Bands: HP_RATIO=2.0, HFAIL_RATIO=1.3, MIN_EFFECT=0.08.

## Dispatch
- Queue: `remote_cpu_queue` (CPU cell; per SMOKE-only-local rule FULL goes remote).
- Timeout: 1200s (est FULL ~379s = 11.1x smoke wall for 3 seeds x 3.71x trials; 1.5x safety + remote-CPU headroom).
