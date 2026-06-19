# Prereg — wave14_betB_compound_pertask_replay_v1

**Date**: 2026-05-24
**Filed by**: exp_dev role (inline; orchestrator sub-agent compound dispatch)
**Routing**: v185 pre-registered untested item — compound MoE + per-task structural-separation untested (axis stacking question; per-task + replay variant)
**Script**: `experiments/exp_wave14_betB_compound_pertask_replay_v1.py`

## Hypothesis

v185 confirmed per-task sub-substrate (Ablation A) lifts retention_A from ~73% baseline to 82.1% (MIDDLE band; +9pp, structural-separation axis CONDITIONAL). Ablation B (parallel ship) bounds replay-only ceiling. This compound stacks BOTH structural-separation axes — per-task W matrices PLUS cross-task replay — to test whether the axes stack enough to clear HARD-PASS 0.95.

## Design

- Per-task W matrices: W_A, W_B, W_C trained zero-init separately (matches Ablation A).
- Phase A: no replay (no prior pool exists).
- Phase B: replay_frac=0.5 against Phase A's pool.
- Phase C: replay_frac=0.5 against combined (A+B) pool.
- Retrieval: average of (W_A @ ctx, W_B @ ctx, W_C @ ctx) (matches Ablation A's concat readout).

## Parameters (exp_dev decided per [[feedback-no-experiment-design-in-prompts]])

- N_FULL = 4096 (matches Ablation A full)
- BATCH_SIZE_FULL = 64
- EPOCHS_FULL = 5
- PHASE_A_EPOCHS_FULL = 8
- BYTES_PER_CORPUS_FULL = 200000
- REPLAY_FRAC = 0.5 (matches Bet B Kovacs baseline)
- SEEDS_FULL = [7, 17, 23, 31, 41]

## Falsifier bands (per [[feedback-envelope-expansion-fail-bands]] and [[feedback-no-smoke]])

- **HARD-PASS**: mean retention_A >= 0.95 across 5 seeds. Compound axis-stacking CLEARS the HARD-PASS gate; both per-task substrates AND replay are required for full retention. Substrate-product implication: the Bet B retention rehab promotion gate is met; row promotes from 🟡 M-DEPENDENT PARTIAL toward ✅ pending multi-N replication.
- **HARD-FAIL**: mean retention_A <= 0.821 (the v185 Ablation A point estimate). Cross-task replay does NOT add anything on top of per-task substrates; +9pp lift is the structural ceiling. Substrate-product implication: the structural-separation axis (per-task) and the replay-frequency axis (Ablation B parallel) are coupled, not independent.
- **MIDDLE**: 0.821 < mean retention_A < 0.95. Partial stacking benefit; replay adds something but compound still does NOT clear HARD-PASS. Substrate-product implication: 🟡 row gets a stacking-benefit annotation but stays 🟡 PARTIAL; new pre-registered probe = compound + Lane D 4-stage (third axis).

## Smoke result (this cycle, local CPU)

- N=1024, 1 seed (17), 1 epoch each phase: retention_A=0.942 (MIDDLE band), retention_B=0.990. Within (0.821, 0.95). VERDICT: COMPOUND_MIDDLE_BAND. Smoke encouraging but not HARD-PASS at smoke resolution; full run will resolve.

## Comparison anchors

- Bet B Kovacs baseline (single shared W + replay): ~73% retention_A.
- Ablation A (per-task, no replay): 82.1% retention_A (v185 verdict).
- Ablation B (single W, replay sweep): pending (parallel ship).
- This compound: TBD; full pre-reg above.

## Dependencies verified (per [[feedback-ship-before-dependency-verified]])

- Base script `experiments/exp_wave14d_betB_kovacs_v1.py` present.
- Ablation A module `experiments/exp_wave14_betB_ablation_A_per_task_v1.py` present.
- `verification/oracle.py` present.
- `hdlab/session_log.py` import is best-effort (try/except).
- No external data files needed beyond corpus_a and corpus_C (already in repo).

## Verdict formula self-test

Passed (8/8 cases) before ship — covers HARD_PASS / HARD_FAIL / MIDDLE_BAND / INCONCLUSIVE boundary points.

## Routing

GPU queue (overnight_queue). Compute-heavy: 5 seeds × 3 phases × N=4096. Expected wall ~30-60 min on GPU per Ablation A's earlier full run (~30 min observed).
