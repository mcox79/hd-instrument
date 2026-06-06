# Research -> Exp-Dev: Standard Batch A AUTHORIZED -- ship immediately (4 cheapest-decisive cells, <20 min CPU total)

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User
**Date:** 2026-06-06 ~18:15
**Re:** exp_dev_handoff_research_next_batch_standard_cells_2026-06-06.md (Drill A batch synthesis)
**Subject:** User approved Standard Batch A. Both queues empty -- pipeline refill urgent. Ship Ranks 1-4 in parallel.

---

## User approved Standard Batch A

Per Drill A's recommended dispatch sequence. **Ship immediately as a single CPU batch.**

### Cells (Ranks 1-4 from Drill A handoff):

1. **HOC1 word bigram** -- `hoc1_word_bigram_v1`
   - <2 min CPU
   - Closes/routes KF-1 word-order gate
   - HP threshold: AUC >= 0.85 (drill prediction 0.85-0.92)

2. **EFFECTIVE-RANK SVD diagnostic** -- `effective_rank_svd_v1`
   - 5-10 min CPU
   - Framework gate; tests intrinsic-dim hypothesis
   - HP threshold: d_eff plateaus < 100 for P > 500 (confirms intrinsic-dim-limited framework)
   - HF: d_eff > 300 (DT-framework cells need reassessment)

3. **analogy_map** -- `analogy_map_v1`
   - 3 min CPU
   - New capability class probe (A:B::C:? via VSA arithmetic)
   - HP threshold: >= 0.85 accuracy at N=4096

4. **frame_slot_fill k=16** -- `frame_slot_fill_k16_v1`
   - 2 min CPU
   - Multi-attribute entity test
   - HP threshold: >= 0.95 accuracy at k=16 attributes

### Wall total: <20 min CPU

### Ship in parallel (all 4 are independent + cheap)

---

## Status of OTHER batches

Standard Batch B (CS-1, DIMSPARSE3-alpha, NEG1, fact_checked_khop) -- **NOT yet authorized**; awaiting user decision after Batch A results
Standard Batch C (auditable_khop_kf1, SIG-1, NRO-1, PSE3) -- **NOT yet authorized**; gated on Batch B

User explicitly approved only items 1 and 2 from my Asks list:
- 1 = Standard Batch A
- 2 = CELL-5 cascade FD smoke (separate Testbed dispatch; not your lane)

So your scope is: Standard Batch A only.

---

## Pipeline status note

Both queues were empty at time of Drill A filing. Pipeline refill is URGENT per Drill A. Ship Batch A in parallel ASAP.

After Batch A results land, I'll synthesize verdicts + propose Batch B based on what we learned (especially HOC1 result, which prices NEG1 priority).

---

**END.**

**Exp-Dev:** Ship Standard Batch A (HOC1 + EFFECTIVE-RANK + analogy_map + frame_slot_fill) in parallel; <20 min total. Pipeline refill urgent.

**User:** Standard Batch A authorized + routed to Exp-Dev. CELL-5 cascade FD smoke routed to Testbed (~$2-5; separate note). All other batches + cloud cells awaiting your future authorization.
