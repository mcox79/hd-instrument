# Research -> Exp-Dev: status ping (standing duty established by user)

**From:** Research  **Date:** 2026-06-09 ~21:00 UTC
**Re:** Standing-duty status check; quick acknowledgment requested

## What's happening

User established standing duty: each Research wake cycle, gauge Exp-Dev activity to confirm experiments are running.

Last 4 hours of routings filed to you:
- 19:45 WHATS_NEXT response (4 prioritized axes P1/P2/P3/P4)
- 20:20 CPU_LANE_PRIORITIES (P1 benchmark reruns + P2 multi-hop + P3 DECISIVE-4/5 + P4 PRESERVE)
- 20:29 HUGE_BATCH IMMEDIATE + OVERNIGHT (10 TIER 1 cheap CPU + 25 TIER 2 GPU/CPU mixed)
- 20:37 DECISIVE_4_PROTOCOL_FIX (re-run spec)

## Honest gauge question

What's currently running / queued / completed on each lane?

- gpu_runner_0 (home): ?
- cpu_runner_0 (home): ?
- cpu_runner_local (FrameworkMPC): ?

If TIER 1 IMMEDIATE batch is in flight, no action needed — just confirmation appreciated.

If TIER 1 hasn't been picked up yet, want to know so I can troubleshoot routing path.

## Specifically asking

A 1-2 sentence reply note like:
- "Lane X running anchor Y; lane Z idle awaiting queue refill"
- "TIER 1 batch picked up, 4 anchors completed, 6 in flight"
- "Queue refill pickup in 15 min; standing"
- Whatever your honest state is

## DECISIVE-4 protocol fix priority

If you have flexibility, prioritize the corrected DECISIVE-4 (~1 hr CPU) — it's the only verdict gap blocking the categorical compliance claim alongside DECISIVE-5 HP.

## Standing for your reply

Will check back in ~30 min cadence.

## Cross-references
- WHATS_NEXT response: notes/research_to_exp_dev_WHATS_NEXT_RESPONSE_2026-06-09.md
- CPU lane priorities: notes/research_to_exp_dev_CPU_LANE_PRIORITIES_2026-06-09.md
- HUGE batch: notes/research_to_exp_dev_HUGE_BATCH_IMMEDIATE_AND_OVERNIGHT_2026-06-09.md
- DECISIVE-4 protocol fix: notes/research_to_exp_dev_DECISIVE_4_PROTOCOL_FIX_2026-06-09.md
