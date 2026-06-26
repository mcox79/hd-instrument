# Pre-registration: substrate_continual_NREM_replay_v1

**Date:** 2026-06-25
**Anchor name:** substrate_continual_NREM_replay_v1
**Script:** experiments/exp_substrate_continual_NREM_replay_v1.py
**Queue:** local_cpu_queue
**Authority:** USER directive 2026-06-25 ("build the 3 missing brain-consolidation primitives. Full auto. NREM replay -> synaptic homeostasis -> cortical schema-extraction")
**Composes with:** a8_continual_writes_no_catastrophic_forgetting_v1 (baseline cliff reference); substrate_continual_kv_n32768_120_sessions_v1 (production-scale continual KV); c2_cascade_stc_swr_continual_v2 (cascade STC analog)
**Brain pillar:** 1 of 3 (sleep consolidation: NREM sharp-wave-ripple replay -> REM homeostasis -> cortical schema)

---

## Scientific question

Hippocampal sharp-wave ripples during NREM sleep replay recent episodes to cortex in
SHUFFLED order at 20x compression. Brain uses this to consolidate memories without
catastrophic forgetting at long horizons.

Substrate analog: at every N_REPLAY_INTERVAL cycles, re-write a random subset of older
atoms with full strength in shuffled order. Question: does periodic replay EXTEND
substrate's continual-write horizon beyond a8's measured no-forgetting boundary
(alpha=0.30, 1.5x Hopfield capacity) to 5000 cycles where baseline would cliff?

## Pre-registered bands (LOCKED via module-init assert)

| Band | Condition |
|------|-----------|
| HARD_PASS_REPLAY_EXTENDS_CONTINUAL | best_replay_arm.final_forget <= 0.05 AND baseline cliffs to forget > 0.10 at some cycle < 5000 AND cv <= 0.07 AND strictly better than baseline |
| HARD_PASS_PARTIAL_REPLAY_REDUCES_DRIFT | drift_reduction >= 0.30 absolute but full HARD_PASS conditions not all met |
| MIDDLE_BAND | drift_reduction in (0.05, 0.30) |
| HARD_FAIL_REPLAY_DOESNT_HELP | drift_reduction within +/- 0.05 of baseline (no measurable benefit) |

Sacrosanct both ways (cannot loosen post-hoc).

## Arms (4)

| Arm | Mechanism |
|-----|-----------|
| ARM_BASELINE_NO_REPLAY | rail: reproduce a8 continual-write pattern at extended cycles |
| ARM_REPLAY_EVERY_100 | every 100 cycles, replay random 20% of all atoms so far |
| ARM_REPLAY_EVERY_500 | every 500 cycles, replay random 20% |
| ARM_REPLAY_EVERY_1000 | every 1000 cycles, replay random 20% (sparser) |

## Config (FULL)

- N = 8192
- N_CYCLES = 5000 (alpha = 0.61 at end; well past Hopfield capacity alpha_c=0.138)
- M_INIT_NEW_PER_CYCLE = 1
- RECALL_PROBE_M = 100 (first 100 atoms; forget-prone)
- CHECKPOINT_INTERVAL = 500
- REPLAY_FRAC = 0.20
- 3 seeds [11, 13, 19]
- Substrate-only (numpy + sign() Hopfield iterative cleanup). Zero LLM forward calls.

## Self-tests (3 formula + bands lock)

1. Hopfield retrieval at alpha=0.078 N=256 -> acc >= 0.70
2. Replay-recovery non-decreasing: write 50, drift via 100 new (alpha=0.59 past cliff), replay 50 -> acc_replayed >= acc_drifted
3. Acc non-NaN throughout

## Smoke result (script-validity gate; 2026-06-25)

- N=1024, 500 cycles, 1 seed, 4 arms; wall ~25s
- VERDICT: MIDDLE_BAND (drift_reduction=0.067; ARM_REPLAY_EVERY_100 best at 0.333 forget vs baseline 0.400)
- Script + bands operational. Full run discriminates at 8x N + 10x cycles.

## Honest scope (chain-grade preview)

NREM-replay primitive over 5000 cycles N=8192; 4 arms (baseline + 3 replay intervals);
forget metric on first 100 atoms; substrate-only Hopfield iterative cleanup.

DOES NOT show: brain-grain timing (SWR is 200Hz; substrate cycles abstract), neural
oscillation coupling, downstream task transfer.

## Q-discipline saturation guard

If any arm has cv=0.0000 AND final_forget=0.0000, flag as by-construction-saturation
(arm trivially solved task; not chain-grade evidence). Skunkworks tiers.
