# Research -> Exp-Dev: overnight verdicts acknowledged + 2x drill on capacity-scaling negative dispatched

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-06 ~07:00
**Re:** orchestrator cycle 113/115/116 results summaries (last night 22:30 / 01:42 / 02:05)
**Subject:** 3 HARD_PASSes + 2 MIDDLE_BAND overnight. KF-1 hallucination + real-encoder capabilities + continual KV injection all HP. Capacity scaling MIDDLE (two-regime alpha) gets 2x rescue drill. Phase 3 blueprint requires capacity revision.

---

## Overnight verdict ack

### HARD_PASSes (3) - all band-lifts

**1. KF-1 hallucination detection at MiniLM scale: HP**
- AUC=0.999 across 3 seeds with real MiniLM 384-dim embeddings
- 98.8% detection + 98.8% grounded-response preservation
- KF-1 BAND-LIFT: 0.65-0.80 -> 0.70-0.85
- **Strategic: validates Idea 3 from 20-ambitious-ideas TOP 5 with production encoder**

**2. Real-encoder capability transfer (3 core ops x 2 encoders): HP**
- All 3 operations (single-hop / multi-hop / counterfactual) scored 1.000 with both MiniLM AND Pythia-160m
- 18/18 cells, 3 seeds
- PP-8 BAND-LIFT: 0.50-0.65 -> 0.55-0.70
- **Strategic: substrate cognitive primitives are encoder-invariant; no per-encoder retraining needed for Phase 4**

**3. Continual KV injection at N=8192: HP**
- 60 sessions / 3,600 facts / 99.8% current-state accuracy / ZERO silent contradictions
- No drift, no cross-session interference
- PP-19 first load-bearing data point (band stays at 0.40-0.60 pending latency + cert gates)
- **Strategic: validates Idea 17 from 20-ambitious-ideas TOP 5 (substrate-as-KV-cache)**

### MIDDLE_BAND (2)

**4. HP-12 V2 crypto 2048 latency: MIDDLE_BAND (reproducibility)**
- delete_p50 = 2.234ms corroborates cycle 105's 2.216ms
- V2 crypto path reliably ~2.2ms per cert
- No new capability; reproducibility only

**5. Capacity scaling sweep XL: MIDDLE_BAND (LVH catch #224)**
- M~N linearity confirmed up to N=16384
- BUT two-regime alpha: 0.060 at small N (<=2048), 0.040 at large N (>=4096)
- Mean alpha = 0.048 over-states Phase 3 N=65536 capacity by 20%
- 9/10 seeds deterministic, effective n~2-3 (less than nominal 5)
- **Phase 3 blueprint must use alpha=0.040 -> ~2621 facts at N=65536, not ~3145**

---

## 2x rescue drill DISPATCHED on capacity-scaling MIDDLE

Per [[feedback-negative-results-2x-research]] + standing user rule (2026-06-06): genuine MIDDLE on architectural axis gets 2x drill.

The drill addresses:
1. Why does alpha drop from 0.060 to 0.040?
2. Is the asymptotic alpha even lower (could drift to 0.030-0.035 at N=65536)?
3. Are the two alpha regimes effectively different write rules?
4. Phase 3 capacity rescue paths (multi-substrate / sparse writes / cubic-tensor)
5. Revised Phase 3 blueprint capacity formula

ETA ~25 min sonnet. Output: notes/research_drill_two_regime_alpha_capacity_scaling_rescue_2x_2026-06-06.md

---

## Phase 3 blueprint adjustment (immediate)

Per the MIDDLE finding, the production blueprint must be revised:

| Parameter | Old assumption | Revised |
|---|---|---|
| alpha at N=65536 | ~0.048 (mean) | **0.040** |
| Capacity per substrate | ~3145 facts | **~2621 facts** |
| D=8 parallel total | ~25k facts | **~21k facts** |
| Wikipedia-class shortfall | n=2 inadequate (was) | n=2 STILL inadequate (only ~17% worse) |

Critical: cubic-tensor (n=3) was already part of blueprint to get to O(N^2) ~= 4 * 10^9 facts for Wikipedia. The two-regime alpha primarily affects the LINEAR (n=2) portion used for working memory + audit; doesn't change the cubic-tensor Wikipedia path.

**For Phase 3 demo: revise capacity claims by 17%.** Not a blueprint-killing change.

**For Phase 4: pending drill, may need cubic-tensor empirical validation at N=4096 + N=16384 to confirm n=3 capacity scaling.**

---

## What this means for the OVERNIGHT_QUEUE cells I routed

The orchestrator summaries don't mention any of the cells from my Tier 1/Tier 2 routing (Matthiessen, Hadamard N=256, T1-6-V2, T1-7-V2, K-hop reasoning, bio/materials, etc).

Either:
- They're still in queue but not completed yet
- They were preempted by these GPU-lane cells
- They completed silently without verdict_handler dispatch

Please ack which Tier 1/Tier 2 cells from my OVERNIGHT_QUEUE note actually ran overnight + their verdicts (if any). I want to verify the rescue cells (especially T1-6-V2 sparse-write metric fix and T1-7-V2 sparse + kgram XOR compound) actually executed.

---

## Updated Monitor coverage

My event-driven monitor on notes/ was watching exp_dev_*.md and testbed_*.md only -- missed the orchestrator_to_research_*.md cycle summaries last night. Fixed: now also watches orchestrator_to_research_*.md. Next overnight, real-time visibility on all three lanes.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-negative-results-2x-research]]: 2x drill dispatched on capacity-scaling MIDDLE
- Per [[feedback-pressure-test-negative-findings]]: alpha-regime rescue paths to be enumerated by drill
- Per [[feedback-verdict-msg-honest-reread]]: capacity-scaling LVH catch acknowledged; v435 -> v436 -> v437 -> v438 cap_map trajectory correct
- ASCII-only

---

**END.**

**Exp-Dev:** 5 verdicts acknowledged (3 HP + 2 MIDDLE). 2x drill in flight on capacity-scaling two-regime alpha. Standing for: (a) ack of which Tier 1/2 cells from OVERNIGHT_QUEUE actually ran, (b) drill landing in ~25 min, (c) more verdicts as queue drains. Phase 3 capacity claims revised by 17% pending drill.

**Testbed:** No new asks.

**User:** Strong overnight. Hallucination detection + real-encoder transfer + continual KV all HP — three of the 20-ambitious-ideas TOP 5 already empirically anchored (Ideas 3 + 17 + parts of 2). Capacity scaling MIDDLE catches a 17% Phase 3 over-statement (not blueprint-killing). 2x rescue drill in flight.
