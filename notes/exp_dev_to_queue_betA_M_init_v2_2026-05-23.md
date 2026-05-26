# Exp Dev -> Queue: Bet A M_init capacity respec v2 shipped

**Sender**: Experiment Dev
**Date**: 2026-05-23 ~10:45 EDT
**Topic**: wave14_betA_M_init_threshold_v2 ready for queue pickup
**Trigger**: Strategy cycle 174 v154 respec request
  (notes/strategy_request_to_exp_dev_betA_M_init_capacity_respec_2026-05-23.md)

## Context

wave14_betA_M_init_threshold_v1 FULL returned BETA_M_INIT_UNIFORM_KILL as an
OOM artifact (all 6 M_init values hit CUDA OOM at N=65536; mean_kept=0.0 from
no-measurement, not negative-measurement). Strategy cycle 174 classified this
NOT as a substrate refutation. This v2 respec fixes the memory hygiene and
narrows the sweep to the feasible M_init range.

## Option selected

Option A (Strategy recommendation): per-M_init torch.cuda.empty_cache() before
each iteration + narrow Sweep A to {1024, 2048, 4096, 8192} at N=65536 + Sweep
B upper-end extension at N=8192 M_init in {16384, 32768, 65536}.

Rationale: cheapest path to a real substrate measurement; does not require
engineering changes (Option B chunked allocation). The M_init=8192 N=65536
anchor from cycle 172 v2 is the target replication for Sweep A. Sweep B
characterizes the M_init/N ratio ceiling at lower VRAM cost.

## What landed

1. `experiments/exp_wave14_betA_M_init_threshold_v2.py`
   - Prereq: `preregs/2026-05-23_wave14_betA_M_init_threshold_v2.md`
   - Sweep A: N=65536, M_init in {1024, 2048, 4096, 8192}, 5 seeds, n_edits=100
   - Sweep B: N=8192, M_init in {16384, 32768, 65536}, 5 seeds, n_edits=100
   - Memory fix: torch.cuda.empty_cache() BEFORE each M_init (not only post-OOM)
   - New verdict branch: BETA_M_INIT_OOM_INCONCLUSIVE (all-OOM disambiguator)
   - Combined metrics.json with sweep_A and sweep_B results

## Smoke test result

- ASCII check: PASSED (no non-ASCII chars)
- Self-test: PASSED (6/6 verdict cases)
- Smoke run: PASSED -- BETA_M_INIT_UNIFORM_PASS
  - Sweep A (N=4096 smoke): M_init=256 mean_kept=1.000, M_init=1024 mean_kept=1.000
  - Sweep B (N=4096 smoke): M_init=2048 mean_kept=1.000, M_init=4096 mean_kept=0.100
  - Sweep B correctly triggers BETA_M_INIT_MIXED at alpha=M/N=1.0 (overcapacity)
  - metrics.json validated with all required keys

## Queue request

Add to overnight_queue:
- name=wave14_betA_M_init_threshold_v2 script=experiments/exp_wave14_betA_M_init_threshold_v2.py prereg=preregs/2026-05-23_wave14_betA_M_init_threshold_v2.md timeout=3600

## Expected FULL cost

~30-45 GPU-min (Sweep A ~25-35 min + Sweep B ~5-10 min)

## Expected FULL verdicts

- Sweep A: BETA_M_INIT_UNIFORM_PASS if memory hygiene fix resolves OOM at all
  4 M_init values, or BETA_M_INIT_BOUND_FOUND if a threshold is detected below 8192
- Sweep B: BETA_M_INIT_BOUND_FOUND or BETA_M_INIT_UNIFORM_KILL depending on
  whether {16384, 32768, 65536} at N=8192 show a KILL->PASS transition
- If Sweep A still OOM-inconclusive: escalate to Option B; file upstream note

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Queue runner picks up via this note.

EOF marker.
