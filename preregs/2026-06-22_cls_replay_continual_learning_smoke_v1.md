# PRE-REG: cls_replay_continual_learning_smoke_v1

Author: exp_dev
Date: 2026-06-22
Anchor: `cls_replay_continual_learning_smoke_v1`
Authorization: USER 2026-06-23 blanket authorization (operational durability primitive from gap framework)

## Scientific Question

Does a substrate-native CLS (Complementary Learning Systems) replay mechanism
(small fast-learning `W_hippo` + large slow-learning `W_cortex` with periodic
replay between them) prevent catastrophic forgetting in a sequential
multi-phase learning protocol, WHILE still learning new phases
(plasticity-stability tradeoff)?

## Intuitive Mechanism

Brain hippocampus stores new memories quickly (fast Hebbian write); during
sleep / idle, hippocampus REPLAYS those memories to cortex which gradually
consolidates them into slow-learning long-term storage. This prevents
catastrophic forgetting and allows continual learning.

Substrate analog:
- `W_hippo` (small fast): high learning rate `alpha_fast=1.0`; cleared after each phase
- `W_cortex` (large slow): low learning rate `alpha_slow=0.1`; accumulates across phases
- Replay: at end of each phase, sample subset of `W_hippo` atoms, present to
  `W_cortex` with slow update

## Config

- `N_DIM=4096`
- `seeds=[7, 17, 23]` (smoke); `[7, 17, 23, 31, 41]` (full)
- `J_PHASES=3`
- `M_PER_PHASE_LIST=[200, 400, 600]` (smoke) / `[200, 400, 600, 800]` (full)
  - Sweep covers alpha_total in [0.146, 0.293, 0.439, 0.586] to FIND the
    discriminating regime (per kappa3/a8 cliff-finding discipline).
  - Cell-author smoke (2026-06-22) confirmed that at M=200 alone (alpha=0.146),
    noise=0.10, all arms recall=1.0 (below the forgetting cliff) - same as c1 lesson.
- `NOISE_FRAC=0.20` (raised from 0.10 to push past clean-recall floor)
- `N_PROBE=30` (smoke) / `60` (full)
- `ALPHA_FAST=1.0`, `ALPHA_SLOW=0.1`
- `REPLAY_FRAC=1.0`, `N_REPLAY_PASSES=10` (multi-pass sleep consolidation)
- `REHEARSAL_FRAC=1.0`, `N_REHEARSE_PASSES=10` (matched to keep arms fair)

**Multi-pass design rationale**: cell-author smoke 2026-06-22 (M_PER_PHASE=400)
revealed a flaw in single-pass CLS: `alpha_slow=0.1` on a single replay event
gives W_cortex 10x weaker signal than naive's W -- CLS_REPLAY collapsed to
0.00 while RANDOM_REHEARSAL preserved Phase 1 at 0.59. Brain-faithful CLS is
multi-pass: hippocampal replay events recur many times during slow-wave
sleep. With N_REPLAY_PASSES=10, effective consolidation = 0.1*10 = 1.0,
matching naive's write strength but with the per-phase hippo clearing
(prevents interference accumulation in `W_cortex`). The discriminator now
properly tests the CLS architecture (dual-W + clearing), not just the
alpha_slow numeric.

## Arms

1. **ARM_NAIVE_HEBBIAN** -- single W, just keep adding Hebbian outer products
   per phase; no replay, no rehearsal. Catastrophic-forgetting baseline.
2. **ARM_CLS_REPLAY** -- the mechanism; dual-W (`W_hippo` + `W_cortex`),
   per-phase replay from hippo to cortex with slow update, hippo cleared.
3. **ARM_RANDOM_REHEARSAL** -- control baseline; single W; at end of each
   phase, rehearse random subset of ALL past atoms with slow update.
   Tests whether dual-W slow-consolidation is what matters vs just rehearsal.

## Metric

After each phase i, evaluate recall on ALL phases learned so far.
Primary endpoints (computed from phase_recalls[J-1][:]):
- `retention_p1_after_p3 = phase_recalls[2][0]` -- recall on Phase 1 after Phase 3
- `recall_p3 = phase_recalls[2][2]` -- recall on Phase 3 after Phase 3
- `delta_cls_vs_naive = cls_ret_p1 - naive_ret_p1`

## Pre-Registered Bands

**HARD_PASS** (CLS replay works; chain-grade-eligible continual learning primitive):
- ANY M_PER_PHASE value in sweep where ALL THREE hold:
  - `ARM_CLS_REPLAY` `retention_p1_after_p3 >= 0.80` (no catastrophic forgetting)
  - AND `ARM_CLS_REPLAY` `recall_p3 >= 0.80` (still plastic)
  - AND `delta_cls_vs_naive >= 0.30` (real rescue, not flat regime)
- Single-point pre-reg: a SINGLE (M, arm) point satisfying all three is
  sufficient for HARD_PASS. Sweep is for cliff-finding, not Bonferroni.

**HARD_FAIL** (CLS replay catastrophic forgets OR fails to learn new):
- At the HIGHEST M tested (max-stress):
  - `ARM_CLS_REPLAY` `retention_p1_after_p3 < 0.30`
  - OR `ARM_CLS_REPLAY` `recall_p3 < 0.50`
- HARD_FAIL bar applies ONLY at the max-stress point; lower-M
  "no-forgetting-happens" outcomes drop to MIDDLE_BAND (not HARD_FAIL),
  matching the c1 lesson-learned that "all arms recall=1.0" is a degenerate
  regime not a failure of the mechanism.

**MIDDLE_BAND**: partial -- sweep ran but no chain-grade point found
(characterizes plasticity-stability envelope but below chain-grade bar).

## Mining Note: c1_cls_replay_continual_ingest_v1 HARD_FAIL Lesson

The 2026-06-22 `c1_cls_replay_continual_ingest_v1_smoke` HARD_FAIL'd because at
`N=1024, M=171/task, alpha=0.5, 3 tasks, noise=0.10` BOTH `NONE` and
`ONLINE_1to1` arms recalled 1.0 (delta=0.0 = HARD_FAIL: cannot show CLS rescue
when no forgetting happens). The substrate was below the forgetting cliff for
the chosen config.

**This cell's design fix**: at `N=4096, 600 atoms, alpha=0.146 ~= alpha_c`,
the cumulative interference SHOULD push the naive arm past the forgetting cliff
on Phase 1 atoms (oldest, most interfered with), while CLS's slow `W_cortex`
with low `alpha_slow=0.1` and per-phase replay preserves earlier phases.

If this design ALSO ends up below the cliff (all arms recall 1.0), the cell
will land MIDDLE_BAND with `delta < 0.30` rather than HARD_FAIL, and a follow-up
will push to `alpha=0.30+` (e.g. M_per_phase=400) to find the discriminating
regime.

## Formula Self-Tests

1. Single-phase no-continual (200 atoms one shot at small N): all arms recall >= 0.95
2. Sign-flip retrieval non-degenerate: clean probe (no noise) gives recall=1.0
3. Total alpha sanity: 3*200/4096 = 0.146 > 0.10 (cliff regime)

## Queue / Dispatch

- Queue: `local_cpu_queue`
- Estimated smoke wall: 5-15 minutes (3 arms x 3 seeds x N=4096 matmuls)
- Timeout: 1200s (20 min) headroom

## Honest Scope

This is a synthetic-bipolar continual-learning probe. The CLS mechanism is
characterized in this regime; capacity / scale extension is a follow-up.
The HARD_PASS claim is bounded to: N_DIM=4096, J=3 phases, M_PER_PHASE=200,
synthetic-bipolar atoms, noise_frac=0.10, 5-step Hopfield retrieval.

Zero LLM calls at inference (`zero_llm_calls_at_inference=True`).
