# Prereg — wave14_betB_4stage_continual_v1

**Date**: 2026-05-24
**Filed by**: exp_dev role (inline; orchestrator sub-agent compound dispatch for triage-A anchors)
**Routing**: strategy_untested_rows_triage_2026-05-24.md Priority A #2 K2 KILLER T1 (True continual learning 4-stage A->B->C->D); also v185 Lane D 4-stage pre-registered; v187-ELEVATED to TOP-LIVE-PRIORITY
**Script**: `experiments/exp_wave14_betB_4stage_continual_v1.py`
**Queue**: overnight_queue (GPU; Lane D / Bet B retention infrastructure reuse)

## Hypothesis

Bet B Kovacs v9 confirmed 3-stage A->B->C continual learning with replay (~73% retention_A baseline at PHASE_A_EPOCHS=8). v187 confirmed 3-stage compound per-task + replay reaches 91.5% but ceilings below HARD-PASS. K2 KILLER T1 asks whether the substrate's CL mechanism scales to FOUR distinct corpora (not three) — a real product-grade continual-learning test.

## Design

Compound configuration (per-task substrates + cross-task replay) extended to 4 phases:
- Phase A: English text (existing pa.load_corpus_a)
- Phase B: byte-shuffled A (existing pa.shuffle_bytes)
- Phase C: Python source from `experiments/` dir (existing base.load_corpus_C)
- Phase D: NEW — Python source from `verification/` dir (distinct from C)

Each Phase k>=B uses combined-replay pool from prior phases. Retention checkpoint at each stage.

Parameters: N=4096, BATCH=64, EPOCHS_BC=5, PHASE_A_EPOCHS=8, BYTES=200K, SEEDS=[7,17,23,31,41].

## Falsifier bands (per [[feedback-envelope-expansion-fail-bands]] and [[feedback-no-smoke]])

- **HARD-PASS**: mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70 across 5 seeds. Substrate-product implication: 4-stage continual learning is a substrate capability; K2 KILLER T1 met; the cap_map opens a new ✅ row for "multi-task continual learning at 4 stages".
- **HARD-FAIL**: mean retention_A <= 0.50. 4-stage exceeds substrate ceiling. Substrate-product implication: substrate CL mechanism breaks past 3 stages; K2 KILLER T1 closed-FAILED at substrate level.
- **MIDDLE**: intermediate. Phase D adds substantial load but mechanism survives partially.

## Comparison anchors

- Bet B 3-stage compound (v187): retention_A=0.915
- Bet B Kovacs 3-stage baseline: ~0.73 retention_A

## Self-test

`python experiments/exp_wave14_betB_4stage_continual_v1.py --self-test` verifies all 7 verdict-tag cases.

## Pre-reg routing impact

- HARD-PASS → cap_map v188 NEW ✅ row "multi-task continual learning A->B->C->D" or strong promotion of Bet B retention 🟡 → ✅
- HARD-FAIL → cap_map v188 K2 KILLER T1 closed-FAILED annotation; substrate ceiling at 3 stages confirmed
- MIDDLE → annotation; 4-stage partial benefit; routes to compound + longer-Phase-A or third-axis variants
