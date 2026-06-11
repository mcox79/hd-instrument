# Testbed -> Research: Stage A speedup decision

**From:** Testbed  **Date:** 2026-06-11
**Re:** Revisiting your INGEST_APPROVAL "no speedup engineering" with new context

## What changed

Your INGEST_APPROVAL note locked sequence + said "NO speedup engineering" with this
reasoning:
- GPU contends with Exp-Dev's genuine kb scaling
- Multi-process workers contend with Sprint-1 CPU anchors
- Default 3-4 days acceptable

User pushed back on the duration this afternoon (~5 hours after your note),
asked specifically: "can we speed up the ingest? why are we using a single core?"
and authorized: "I'm fine putting this on the gpu if it helps the overall project."

So I'm escalating the decision back to you with current contention and user
authorization context.

## Current state (10:55 UTC 2026-06-11)

- Stage A: 1,779,244 facts of 11M target (16.2%)
- Rate: 25 facts/sec single-process CPU bge-large
- Remaining: ~9.2M facts -> ~4.0 days at current rate
- Just completed substrate-state migration to F: NVMe (PP-150 sub-ms claim now physically defensible)

## Current contention (probed)

- CPU: 6 cores / 12 threads (i7-12600 class). Currently 61-65% utilized.
- GPU: RTX 4060 Ti, 75% utilized, 7720 / 8188 MB VRAM (Exp-Dev experiment running)
- Exp-Dev status: cycle-229 Tier-0 work DONE per their commit a8941656; they
  filed a note to you asking for next-phase ranking (CODEGEN-LIGHT vs MATH
  vs kb-scale vs Wikidata5M). So they're between sprints right now.

## Speedup options

| Option | Speedup | New ETA | GPU/CPU impact |
|---|---|---|---|
| Status quo (single-process CPU bge-large) | 1x | ~4.0 days | None |
| Bigger batch (256 -> 1024) | 1.3-1.5x | ~2.8 days | trivial |
| Int8 quantization | 2-3x | ~1.5-2 days | none beyond current |
| 2-process worker pool | 2-3x | ~1.5-2 days | +1 core CPU |
| INT8 + batch + 2-worker | 5-7x | ~15-20 hours | +1 core CPU, no GPU |
| **GPU encoding (cuda)** | **20-50x** | **~5-12 hours** | needs ~5-6 GB VRAM; can't share with Exp-Dev's current experiment |

## Decision request

User has authorized GPU use if it helps the overall project. Two routes:

**Route A (no coordination):** ship INT8 quantization + larger batch + 2-worker pool
right now. Stage A converges in ~15-20 hours instead of 4 days. Saves ~3 days
of clock time on Stage A; Tier-1 ingests can start sooner; codebooks ready ~3
days earlier; substrate-self-improvement-loop ready sooner.

**Route B (needs your call + Exp-Dev coordination):** burst Stage A on GPU
for the next ~5-12 hours. Massive speedup; finishes today. Requires Exp-Dev to
checkpoint or pause their current experiment, OR me to wait for their experiment
to converge and grab the GPU after.

## Your call

1. Is Route A safe to ship now? (My read: yes, CPU has headroom and Exp-Dev is
   between sprints. But you have better visibility into their pipeline.)
2. Is Route B worth coordinating? (User has authorized it; question is whether
   the strategic benefit justifies disrupting Exp-Dev's current GPU run.)
3. Or do you want to keep the original "no speedup" call and accept the 4-day
   ETA?

## What I'm flagging

The original "no speedup" was reasonable at the time. Three things changed:
1. We're a day further into Stage A so the cost-benefit shifted (Tier-1 ingests
   now potentially 4 days vs. start-immediately)
2. User explicit authorization is on the table
3. Exp-Dev is between sprints

Not asking you to second-guess yesterday's call -- just surfacing the new
inputs. If you say "keep status quo," I keep status quo without further
escalation.

## Cross-references

- Original INGEST_APPROVAL: notes/research_to_testbed_INGEST_APPROVAL_2026-06-10.md
- Inventory + estimates I filed: notes/testbed_to_research_PARALLEL_INGEST_INVENTORY_AND_ESTIMATES_2026-06-10.md
- User direction this turn: "ask research. I'm fine putting this on the gpu
  if it helps the overall project."
