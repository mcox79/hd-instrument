# Prereg — wave14_betB_compound_plus_longer_phaseA_v1

**Date**: 2026-05-24
**Filed by**: exp_dev role (inline; orchestrator sub-agent compound dispatch for v187 follow-up)
**Routing**: v187 NEW pre-registered untested — longer-Phase-A consolidation variant (cheap orthogonal axis to structural separation + replay; tests whether substrate has not fully settled on Phase A at PHASE_A_EPOCHS=8)
**Script**: `experiments/exp_wave14_betB_compound_plus_longer_phaseA_v1.py`
**Queue**: overnight_queue (GPU)

## Hypothesis

v187 compound per-task + replay stacks +18.5pp above baseline but ceilings at 0.915 (3.5pp below HARD-PASS 0.95). The compound script uses PHASE_A_EPOCHS=8 — the substrate may not have fully settled on Phase A before the shift to Phase B. Extending Phase A consolidation (24 epochs vs 8) is a cheap orthogonal axis that does not require any new mechanism.

## Design

Identical to `exp_wave14_betB_compound_pertask_replay_v1.py` except `PHASE_A_EPOCHS_FULL=24` (3x v187 baseline 8). All other parameters (N=4096, BATCH=64, EPOCHS_BC=5, BYTES=200K, REPLAY_FRAC=0.5, SEEDS=[7,17,23,31,41]) carried forward.

## Falsifier bands (per [[feedback-envelope-expansion-fail-bands]] and [[feedback-no-smoke]])

- **HARD-PASS**: mean retention_A >= 0.95 across 5 seeds. Longer Phase A consolidation IS the missing third axis. Substrate-product implication: Bet B retention rehab clears HARD-PASS via cheap-to-implement longer consolidation (no new mechanism).
- **HARD-FAIL**: mean retention_A <= 0.915 (v187 baseline). PHASE_A_EPOCHS=8 is already saturating; longer consolidation does NOT lift retention. Substrate-product implication: consolidation is NOT the missing third axis — must look elsewhere (MoE stacking, Lane D 4-stage, eligibility-trace).
- **MIDDLE**: 0.915 < mean retention_A < 0.95. Partial third-axis benefit; v187 ceiling breaks but HARD-PASS not cleared. Substrate-product implication: 🟡 row gets fourth-evidence-point annotation; longer consolidation contributes but a fifth axis still required.

## Comparison anchors

- v187 compound per-task + replay: retention_A=0.915 (baseline)
- v185 Ablation A per-task alone: 0.821
- v186 Ablation B replay-only plateau: 0.846
- Bet B Kovacs single-shared-W baseline: ~0.73

## Self-test

`python experiments/exp_wave14_betB_compound_plus_longer_phaseA_v1.py --self-test` verifies all 7 verdict-tag cases.

## Pre-reg routing impact

- v187 row state STAYS 🟡 M-DEPENDENT PARTIAL regardless of outcome
- HARD-PASS → cap_map v188 annotation: longer-Phase-A IS the third axis
- HARD-FAIL → cap_map v188 annotation: longer-Phase-A NOT the third axis; rotate to MoE-stacking or Lane D 4-stage
- MIDDLE → cap_map v188 annotation: fourth evidence point; partial third-axis benefit
