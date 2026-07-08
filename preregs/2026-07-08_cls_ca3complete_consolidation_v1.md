# Pre-registration: cls_ca3complete_consolidation_v1

**Date:** 2026-07-08
**Author:** exp_dev (cell author)
**Cell:** `experiments/exp_cls_ca3complete_consolidation_v1.py`
**Anchor:** `cls_ca3complete_consolidation_v1`
**Routing:** biology-first consolidation drill RANK 1 + RANK 2
(`notes/research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08.md`). Builds the
diagnosed-but-never-assembled RESCUE-4 CLS fix (cycle-228 `two_substrate_fastslow_cls` HARD_FAIL,
`research_drill_cls_2substrate_rescue_2x_2026-06-11`).

## Prior-work check (mandatory)
- substrate concept-query top hit cosine=0.372 (`research_drill_substrate_continual_learning_rag_backend_2x`) -- prior-arc overlap, NOT a rediscovery.
- `exp_cls_rescue4_plus_rescue2_cpu_v1.py` EXISTS but is a PARTIAL RESCUE-4: single-seed; NO CA3-completion (writes ground-truth `truth[i]` values = answer-storage, the note's warned anti-pattern); NO no-consolidation control; NO discrete fixed-budget phase-gate discriminator. This cell adds all four and reuses the certified `hdlab.iterative_attractor.iterative_cleanup` as the CA3 operator (generative partial-cue replay, no answer-leak).

## Hypothesis / functional requirements (Gate E)
1. Integrate NEW stream items without catastrophically forgetting OLD ones -> continual learning.
   Primitive: recency-decayed FAST buffer (hippocampus) + CA3-completed offline migration to a SLOW store (cortex).
2. Cortex must receive a CLEANED (CA3-completed), not raw, signal (Buzsaki 1.1). Primitive: certified `iterative_cleanup` (alpha=0.5 perforant-path).
3. Consolidation is a DISCRETE offline phase with a FIXED per-phase budget (SO-spindle-ripple, 1.5), not a free-running background process. Primitive: per-epoch offline phase, budget cap `BUDGET_B`.

## Model / arms
Stream of T=600 (key->concept) items in E=12 epochs. FAST buffer F is a recency-decayed associative matrix
(F = DECAY*F + concept outer key); OLD = epoch-0 items, RECENT = last-epoch items. Recency-decay is the
genuine substrate forgetting driver (the linear-store argmax readout is otherwise too robust to forget --
META_RULE_AG; confirmed empirically in regime sweep, and matching prior rescue4/cycle-228 cells). Readout is
identical single-step argmax across arms; only the queried store differs.
- **NAIVE_NO_CONSOLIDATION** (control): fast buffer only, no offline migration. OLD recalled from F -> decayed out -> FORGOTTEN. MUST forget at smoke.
- **CONSOLIDATE_FULL** (mechanism): per-epoch discrete offline phase, budget B, partial-cue (SWR) replay -> CA3-complete noisy FAST readout -> write clean concept to SLOW store S. OLD migrated while fresh -> recalled from S -> RETAINED.
- **CONSOLIDATE_NO_CLEANUP** (Rank-1 ablation): same schedule/budget/partial-cue but SKIP CA3 completion (raw readout written). Isolates the completion contribution.

## Config
`D=1024 T=600 E=12 DECAY=0.94 V=64 BUDGET_B=50 CUE_RHO=0.70 ca3_temp=4.0 ca3_alpha=0.50 ca3_steps=6`.
FULL seeds=[7,17,23]; SMOKE seed=[7] at IDENTICAL full-scale params (discriminator-survives-scale option A).

## Pre-registered bands (strict, META_RULE_L)
- **HARD_PASS:** CONSOLIDATE_FULL old_retention >= 0.80 AND new_acquisition >= 0.70 AND NAIVE old_retention <= 0.55 AND (FULL old - NAIVE old) >= 0.25 AND budget_respected.
- **HARD_FAIL:** FULL old_retention <= NAIVE old_retention + 0.05 (consolidation no better) OR (at FULL) NAIVE old_retention > 0.55 (interference regime not real).
- **MIDDLE_BAND:** one gate short.
Strictly-above-floor: HARD_PASS floors (0.80 / 0.70) are >5% band-width below the measured mechanism values (smoke 0.96 / 0.90); at-floor would be MIDDLE_BAND.

## Discriminator-fires gate (META_RULE_K)
`assert_discriminator_fires(NAIVE old_retention >= 0.80, ...)` in self-test/smoke: the no-consolidation control
MUST fail the OLD-retention headline (forget). SMOKE measured NAIVE old=0.000 -> gate fires correctly.

## Telemetry-sensitivity (2026-07-08 rule)
Self-test T2: zeroing the queried store drops old_retention (>0.3), corrupting it drops (>0.1) -- the metric
reads store state, is NOT analytically pinned. T3: CA3 completion raises cosine-to-true of a partial-cued
noisy readout (positive-control reproduction of the primitive at the test regime, Gate D).

## SMOKE result (MEASURED)
MEASURED@`data/exp_cls_ca3complete_consolidation_v1_smoke/metrics.json`: verdict HARD_PASS, run_mode=smoke,
elapsed=7.7s. NAIVE old=0.000 new=0.940 | CONSOLIDATE_FULL old=0.960 new=0.900 | NO_CLEANUP old=0.880 new=0.860
| gap=0.960 | ca3_cleanup_lift=+0.080 | budget_respected=true | old_retention_cv=0.0 (single-seed smoke).

## SCHEMA-VET fields
- `cardinality_ok: true` -- not a sweep-axis cell. EXPECTED_N_UNITS = n_seeds = 3 (FULL). Verdict counts len(units).
- `final_metrics_atomicity: "tmp_replace"` -- write_metrics + crash-diag use os.replace.
- `arms_differ_verified: true` -- `_arms_must_differ` hashes F / S_full / S_nc (META_RULE_AF); all distinct at smoke.
- `HP_SCOPE:` {CONSOLIDATE_FULL: [old_floor, new_floor, gap], NAIVE_NO_CONSOLIDATION: [forget_ceiling], CONSOLIDATE_NO_CLEANUP: [ablation-only, no HP gate]}.
- `calibration_check: "default_ok_for_this_regime"` -- CA3 params (temp=4, alpha=0.5, steps=6) are the certified att1 defaults; regime sweep confirms cleanup denoises at test regime.
- `crlb_n/a: "recall-accuracy bands, not a noise-floor threshold; capacity-feasibility confirmed empirically (naive 0.0 vs full 0.96 separation, ablation 0.88 shows non-saturated headroom)"`.
- `baseline_in_band: true (interpretation)` -- NAIVE=0.0 is the intended negative control (forgets by design, not a difficulty-miscalibration); the mechanism arm CONSOLIDATE_FULL=0.96 sits above the 0.80 floor with the ablation arm at 0.88 proving the regime is NOT trivially saturated (headroom the CA3 completion fills). Max discriminator separation (control at floor, mechanism in-band).
- `sweep_alignment_verdict: N/A (no swept axis)`.
- `discriminating_fraction: N/A (arm-vs-arm, not sweep); arms land at 0.0 vs 0.96 -> maximally discriminating`.
- `composition_edges:` fast-readout -> CA3 completion (iterative_cleanup) -> slow write. All D-dim vectors. verdict: SHAPE_MATCH.
- `positive_control_arms:` CA3 primitive reproduced at test regime (self-test T3: cos_cleaned > cos_raw at D=384 test regime); iterative_cleanup is the cited CG primitive.
- `cell_chunked: false` -- fast CPU cell (~8s/seed); per-seed checkpoint via write_partial_key (att1 template); runner-zombie risk minimal.
- `start_marker_written: true`; `crash_diagnostic_present: true` (Exception -> CELL_CRASHED + traceback, atomic); `heartbeat_present: false` (exempt: wall << 15min); `defensive_error_checking: "passed (start-marker + crash-diag + no bare except; heartbeat exempt <15min)"`.
- `progress_logging: "print_flush_true"` (all progress lines flush=True; wall < 30min so field advisory).
- `except SystemExit: raise` ordered before `except Exception` (no BaseException). Grep gate CLEAN.

## Dispatch
- Compute: recency-decay recurrence is inherently sequential; small CPU matmuls; ~24s FULL (3 seeds). No GPU benefit. -> `remote_cpu_queue`.
- SMOKE-only-local honored: FULL routed remote (not local). Local used only for smoke.
- FULL run_mode verification post-dispatch (orchestrator): expect run_mode=full, per-seed units=3, elapsed ~15-40s.
