# exp_dev hand-off -- research: production scaling 5x chain drill 1

**Filed-by:** research sub-agent (2026-06-07)
**Trigger:** notes/research_drill_substrate_production_scaling_5x_chain3_drill1_2026-06-07.md
**Pause state:** Check data/orchestrator_paused.flag before dispatching.

Per [[feedback-no-experiment-design-in-prompts]]: this file specifies WHAT and WHY; exp_dev
designs anchor names, sweep grids, thresholds, and queue placement autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist, or confirm
with orchestrator. Do not ship if paused.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (MUST-DO): Cross-shard K-hop capability gap validation
**Pointer:** Research note Section 1 (Axis 4) + Section 3 (Surprise 1) + Section 5 (Cheap decisive test)
**Substrate-product reading:** 3-shard N=4,096 substrate, write 1,000 facts spread across 3 shards,
execute K=3 hop query crossing all 3 shard boundaries. Tests whether the capability gap is real:
K-hop should FAIL without cross-shard routing, confirming architectural work is required.
**Tier hint:** CPU; small N=4,096; <30 min wall; laptop-runnable.
**Why now:** This is the highest-impact untested capability gap in the production roadmap. A K=3
query across 3 shards is the minimal test of the cross-shard K-hop problem. The result is binary:
works or does not. If it fails (expected), the capability gap is confirmed and architectural design
work begins. If it passes (surprising), the gap is smaller than predicted.
**Pre-reg from research note:** HARD-PASS (gap confirmed) = K-hop fails OR latency > 500 ms for K=3.
HARD-FAIL = K-hop succeeds with correct answer and latency < 50 ms (would mean gap is not real).

### Anchor 2: Per-GPU pseudoinverse throughput measurement at N=65,536 under bf16
**Pointer:** Research note Section 2.4 + Section 6 HP-2
**Substrate-product reading:** Measures actual throughput at production N=65,536 with bf16 (once
fp16 fix is validated). The N^2 memory scaling projection gives ~44 writes/sec; empirical measurement
validates or contradicts the memory-bandwidth-bound model.
**Tier hint:** GPU required (bf16 native on A100/H100); medium wall (~30 min).
**Why now:** The 708 writes/sec throughput claim for N=16,384 is the only data point. Production N
is 4x larger (16x in memory traffic). Customers will ask for this number.
**Pre-reg from research note:** HARD-PASS = 30-60 writes/sec (bandwidth-bound confirmed).
HARD-FAIL = >200 writes/sec (contradicts bandwidth model; re-analysis required).

### Anchor 3 (MONITORING): Per-shard capacity cliff pre-alert validation
**Pointer:** Research note Section 2.5 + Section 4 Change 4 + Section 6 HP-3
**Substrate-product reading:** Fills a shard to 80%, 90%, 95%, 99%, 101% of alpha_c x N and
measures retrieval accuracy at each load level. Validates that the cliff is truly discontinuous
(hard transition) and calibrates the 80% alert threshold.
**Tier hint:** CPU; any N with clean data (N=8,192 recommended for speed + fidelity); <1h wall.
**Why now:** Production monitoring requires an empirically-validated alert threshold. The
discontinuous-transition prediction from spin-glass statistical mechanics must be confirmed.
This anchor requires no new architectural work.
**Pre-reg from research note:** HARD-PASS = retrieval > 90% at 90% capacity, < 50% at 101% capacity
(confirming sharp, discontinuous transition). HARD-FAIL = smooth degradation from 0% to 20% load
(contradicts first-order transition prediction).

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_substrate_production_scaling_5x_chain3_drill1_2026-06-07.md
- fp16 overflow prior research: d:/AI/hd-instrument/notes/research_drill_fp16_N65536_overflow_3x_deep_2026-06-07.md
- fp16 overflow handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_fp16_N65536_overflow_2026-06-07.md
- Production architecture handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_production_deployment_architecture_2026-06-07.md
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

exp_dev owns: anchor naming, sweep grids, queue routing, pre-reg thresholds (may refine from
research note bands), cell recipes, self-test formulas.

Research has provided: capability gap identification, throughput projection model, phase transition
prediction, P_deflated estimates, and pre-registration band recommendations.

Research has NOT provided: specific anchor names, exact sweep grids, HF1/HF2/HF3 numerical bounds
beyond the ranges above, queue choice, or ETA.

## Autonomy declaration

exp_dev is fully autonomous within the bounds above. Anchor 1 (cross-shard K-hop gap test) is
the highest-priority dispatch and can run immediately; it requires no GPU and no new mechanism,
just a minimal 3-shard harness. Anchors 2 and 3 can be batched at exp_dev's discretion.
Anchor 2 depends on bf16 fix validation (from the fp16 overflow handoff); if that has not yet
been dispatched, Anchor 2 should be deferred until bf16 at N=65,536 is confirmed clean.
