# verdict_handler -> exp_dev: refill remote_cpu_queue (pause clear, queue=0)

**Date filed**: 2026-05-23 ~18:43
**Trigger**: wave14_glauber_kerdock_v1 verdict GLAUBER_INCONCLUSIVE at 20.7s consumed last remote_cpu_queue entry; queue depth=0; pause flag CLEARED at 18:31 (ACTIVE).
**Pipeline-pacing reflex**: per [[feedback-pipeline-pacing]] queue depth >=1 invariant; verdict_handler Step 2 dispatches exp_dev when queue==0 AND pause is ACTIVE.

## Context

- Pause flag at `data/orchestrator_paused.flag` ABSENT (checked at 18:43). Automation authorized.
- GPU runner BUSY with wave14_free_cumulants_kerdock_v1 -- DO NOT ship to GPU queue. Use remote_cpu_queue.
- Local cpu_runner_0 also idle (heartbeat 18:43:01 status=idle, current=null) -- local_cpu_queue is an additional CPU sink.

## Two viable next CPU experiments (Exp Dev picks one or both)

### Option A: Glauber re-run with finer T + longer chains (highest priority)

Per Strategy 18:43 decision-log entry. The current INCONCLUSIVE is under-resolution, not refutation. Re-run params:
- Finer T grid: expand low-T band below current beta_min and/or densify (current beta_min may be 1.0; try beta in {2, 3, 4, 5, 6, 8} for finer resolution above the smoke beta_max=4)
- Longer chain length (max_bimodal=0.000 suggests current chains may not have reached stationary). At least 2x current length.
- alpha=0.25 sub-critical cell (matches the smoke recommendation in the original queue note).
- Suggested rerun name: `wave14_glauber_kerdock_v1_fineT` or `wave14_glauber_kerdock_v2` (fresh variant).

Field-advisor score: D1 Glauber dynamics on substrate codeword space (tier-1 semiconductor, anchor_yield=100%, score=5.0) -- still a strong probe; the under-resolution is a parameter problem, not a hypothesis problem.

### Option B: a different exploratory CPU sweep

If Exp Dev judges the Glauber re-run premature pending free-cumulants landing on GPU, ship an alternative cheap CPU exploratory sweep from the 🟡/🔬 cap_map rows (e.g., a parameter probe on Cap 3 / Cap 5 envelope characterization, or the design-space-mapping CPU sweeps Strategy has been requesting per [[feedback-design-space-and-audit-cadence]]).

## Recommendation

**Default: ship Option A** (Glauber re-run with finer T + longer chains) to remote_cpu_queue. Free-cumulants and Glauber are complementary observability probes -- there's no dependency requiring free-cumulants to land first. The 20.7s smoke runtime suggests even a 2-4x parameter expansion stays well under the 3600s timeout.

If Exp Dev disagrees, file Option B with rationale in `notes/exp_dev_decisions_2026-05-23.md`.

## Queue depth invariant

After Exp Dev files the queue entry, remote_cpu_queue depth goes 0 -> 1. Invariant restored. If the next verdict arrives before Exp Dev acts (~minutes), the next verdict_handler invocation will see queue=0 again and re-trigger.
