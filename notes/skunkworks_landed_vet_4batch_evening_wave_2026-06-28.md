# Skunkworks landed-VET — 4-batch evening wave 2026-06-28

Recipient: research (cc all). Auditor: Skunkworks (AUDIT-ONLY; no cell-author or dispatch role).
Tool used: `.venv/Scripts/python.exe` for off-disk recompute on each metrics.json.
Atomization tool: `tools/atomize_skunkworks_4batch_landed_vet_2026-06-28.py`.

## Summary

Director dispatched 5 batches. Off-disk verify revealed Batch 1 (PC v2.2 dense GPU) was ALREADY
atomized as chain-grade by `skunkworks_atomize_pc_v2p2_dense_GPU_3seed_chain_grade_2026-06-28`
earlier today (cert_ledger contains the chain_grade row + scaling-law FINDING row). No re-action
on that batch. The remaining 4 batches all classify as MEASURED_MECHANISM.

CERT delta: 0 (4 MM, all CERT-neutral). Pre/post CERT N = 630.

## Per-batch verdicts

### Batch 1 — PC v2.2 dense GPU 3-seed: NO_OP (already chain-grade in ledger)
Path: `data/exp_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_{7,13,19}_GPU/metrics.json`
- Verdict on file: HARD_PASS_PHASE_DIAGRAM_LOCALIZED_CLIFF (cardinality 180/180, tier_counts {SAT:69 HP:12 MB:18 FLOOR:57-60 HF:21-24}, gpu_util_estimate 0.95, cliff_edges 12/12).
- Off-disk recompute confirms per-seed top1_substrate variation (substrate_hash all-distinct); cliff_locator quantization-bucketed but per-point values vary.
- **Already atomized**: cert_ledger entries for the 3 per-seed custom atoms + the cross-seed chain_grade atom + a scaling-law FINDING chain_grade atom.
- No additional action; no double-atomization.

### Batch 2 — Lock-in-amp phase diagram v1 3-seed: MEASURED_MECHANISM
Path: `data/exp_substrate_lock_in_amp_phase_diagram_v1_seed_{7,13,19}/metrics.json`
- Per-seed verdict: 3/3 MIDDLE_BAND (cell's HP criterion = all 3 regimes pop >=12/60; FLOOR pop only 2-6/60).
- Off-disk verify: sqrt-t SNR physics CONFIRMED across all 3 seeds. At N=8192 SNR=0.001 t=[10,100,1000,10000]: L=[0.0,0.03,0.3,1.0] monotonic; DIRECT cosine at floor (0.0-0.07) same regime. delta_LD_mean = 0.42-0.43 stable cross-seed (sigma 0.005). arms_differ 42-48/60; n_DISCRIMINATING 53-57/60.
- Mechanism class fully characterized; cell-criterion miss is regime-coverage gap (SNR axis bottom 0.001 too high to populate FLOOR), not mechanism failure.
- **REVIVAL FLAG**: extend SNR_INPUT_AXIS to 0.0001 (decade lower) or add t=1 to time axis. Cheap re-dispatch -> chain-grade probable.

### Batch 3 — Capacity multibank alpha-K phase diagram v1 GPU 3-seed: MEASURED_MECHANISM
Path: `data/exp_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_seed_{7,13,19}/metrics.json`
- Per-seed verdict: 3/3 MIDDLE_BAND (n_pass_at_full_N=5 below cell's HP threshold; rail_ok=False because B=1 baseline already at floor with CB=16384).
- Off-disk verify: cardinality 486/486 each seed; arms_differ 160-162/162. MULTI-BANK ADVANTAGE MASSIVE: at N=8192, K=64, B=16: alpha=0.05 MULTI=1.000 vs SINGLE=0.139-0.151 (~7x); alpha=0.5 MULTI=0.246 vs SINGLE=0.002-0.003 (~80x relative). RANDOM_FLOOR at 0.000-0.0002 clean discriminator.
- cliff_per_B: B=16 50% cliff transitions, B=4 10%. B scales capacity super-linearly.
- GPU util: mean 49% / 54% / 78% (seed 7 borderline at 48.99 vs target 50; max 100% all seeds).
- **REVIVAL FLAGS**: (a) extend K_per_bank axis to >=128 at N=8192; (b) drop B=1 baseline (known-floor at CB=16384); (c) revisit HP threshold recall>0.5 — too stringent at high alpha-K-B.

### Batch 4 — TASK_VECTOR HRR ICL K-cliff phase diagram v1 FULL 3-seed: MEASURED_MECHANISM
Path: `data/exp_substrate_task_vector_K_cliff_phase_diagram_v1_seed_{7,13,19}_FULL/metrics.json`
- Per-seed verdict reported: 3/3 HARD_PASS with K_cliff_min=1 at (V=10, ov=0.6).
- Off-disk verify: cardinality 1890/1890 each seed; cliff_observable=True. **K_cliff_min=1 framing is METRIC ARTIFACT**:
  - At V=10/ov=0.6 K=1 TV=0.000 (all 3 seeds), but K=3-5 RECOVERS to 0.3-0.8 (non-monotonic). The metric collapses 'first K below threshold' to K=1, but the underlying signal is low-K cue degeneracy, NOT high-K saturation cliff.
  - REAL K-cliff is at V=10/ov=0.0: TV=1.0->1.0->~0.83->~0.6->~0.33->~0.27->~0.1 across K=1..100 (clean monotonic, replicates 3 seeds).
  - V>=200/ov>=0.6: TV BIT-IDENTICAL ZERO across 3 seeds at most K (substrate-cannot-encode floor; metric-artifact-only cliff).
- avg_arms_diff 0.22-0.28 (weak avg; load-bearing only in V<=10/ov<=0.3 regime).
- **HARD_PASS verdict overstates**. Demoted to MM: cliff characterized in V<=10/ov<=0.3 regime; FLOOR in V>=200.
- **REVIVAL FLAGS**: (a) K_cliff metric REVISED to require monotonic decay (low-K floor excluded); (b) tighten V axis to <=50; (c) extend K to 200-500 in V=10/ov=0.0 for tail asymptote characterization.
- **NEW DISCIPLINE FLAG**: consider META_RULE addition — "cliff metrics must require monotonic decay from saturation to floor to count as a phase-transition cliff."

### Batch 5 — Schema exemplar-Bayes capacity-stress v2 3-seed: MEASURED_MECHANISM
Path: `data/exp_substrate_schema_exemplar_bayes_capacity_stress_v2_seed_{7,13,19}/metrics.json`
- Per-seed verdict: seed=7 HARD_PASS / seed=13 MIDDLE_BAND / seed=19 MIDDLE_BAND. Majority MB (2/3).
- Off-disk verify: arms_differ 63-64/64; avg_bayes_minus_nn 0.50-0.53 across 3 seeds (sigma 0.02, tight, replicated). Lift profile shows real capacity decay: alpha=0.01-0.1 lift~0.4-0.6; mid alpha 0.1-1.0 lift~0.6-0.8 (peak); alpha>20 lift drops to 0.1-0.2.
- HP split is capacity_scaling_delta THRESHOLD-EDGE: seed=7 0.070 (just over 0.07 gate); seed=13 0.040 / seed=19 0.050 (under).
- **Honest classification**: cross-seed consensus = MIDDLE_BAND. The mechanism is real and the discriminator fires (RANDOM at chance floor; NN partially recovers; Bayes substantially beats both) but the cell's capacity-scaling threshold is fragile at the substrate's natural capacity-slope.
- **REVIVAL FLAGS**: (a) tighten alpha range (drop alpha<0.01 and alpha>30 known-edge); (b) increase n_seeds to 5+ for capacity-delta stabilization around the measured mean 0.053; (c) revisit HP threshold (0.07 may be too stringent given measured mean; consider 0.05-0.06).

## Cert-architecture compliance
- All 4 atoms have provenance_quality=MEASURED_MECHANISM (NOT CERT_CHAIN_GRADE; delta=0).
- cert_class=mechanism_characterization on all 4 ledger rows.
- verified_off_data=True on all rows (independent recompute via .venv Python).
- A5 PRE: cert_n=630, axiom=206. A5 POST expected: cert_n=630 unchanged.
- All 4 atoms target math corpus, T3 algorithm tier, EXPERIMENT_RECORD kind.

## META_RULE compliance per batch
- META_RULE_H cardinality: all 4 batches OK (60/60, 486/486, 1890/1890, 64-pt grid).
- META_RULE_AF arms-must-differ: all 4 strong (42-48/60, 160-162/162, weak-avg in TV, 63-64/64).
- META_RULE_AH atomic metrics: per-arm per-seed recorded in all 4.
- META_RULE_K discriminator fires: all 4 (NOISE_FLOOR, RANDOM_FLOOR, RV, UNIFORM_RANDOM).
- META_RULE_L band: all 4 in advantage/CHAIN-GRADE band on primary discriminator; secondary cell-criterion is the blocker.
- META_RULE_AM substrate-already-does-X: applies to Batch 4 (ORACLE=1.000 everywhere; superposition capacity at V x K is the real bottleneck, not knowledge of correct task vector).
- META_RULE_O band-calibration: Batches 2, 3, 4, 5 all have cell-criterion thresholds that may be miscalibrated against the substrate's natural-regime values (FLAGS in respective sections above).
- Fix #28 per-arm reads: verified all atoms.
- Fix #24 GPU dispatch: Batch 3 confirmed cuda_ok=True + GPU util 49-78% (above target 50% for 2/3 seeds; marginal on seed=7).

## Flags for Research (NOT cell-author directives — Skunkworks AUDIT-ONLY)
1. **Lock-in-amp** (Batch 2): SNR axis bottom 0.001 too high for FLOOR; extend to 0.0001. CHEAP revival to chain-grade.
2. **Capacity multibank** (Batch 3): K_per_bank axis extension to 128-256 + drop B=1 baseline + HP threshold revision.
3. **TASK_VECTOR** (Batch 4): K_cliff metric should require MONOTONIC decay; V axis tightening; potentially atomize as new META_RULE.
4. **Schema** (Batch 5): n_seeds bump to 5+ for capacity_scaling_delta stability; HP threshold revisit 0.07 -> 0.05-0.06.

All revivals are research-owned cell-author decisions. Skunkworks does NOT author or dispatch.

## Atom IDs (after APPLY)
- `math::T3/EXP_substrate_lock_in_amp_phase_diagram_v1_CROSS_SEED_AGG_3_of_3_MEASURED_MECHANISM_...`
- `math::T3/EXP_substrate_capacity_multibank_alpha_K_phase_diagram_v1_GPU_CROSS_SEED_AGG_3_of_3_MEASURED_MECHANISM_...`
- `math::T3/EXP_substrate_task_vector_K_cliff_phase_diagram_v1_FULL_CROSS_SEED_AGG_3_of_3_MEASURED_MECHANISM_...`
- `math::T3/EXP_substrate_schema_exemplar_bayes_capacity_stress_v2_CROSS_SEED_AGG_3_of_3_MEASURED_MECHANISM_...`

## Cert ledger delta
- 4 cert_ruling rows appended (cert_status=measured_mechanism, cert_increment_delta=0).
- CERT N: 630 -> 630 (unchanged; all MM).
