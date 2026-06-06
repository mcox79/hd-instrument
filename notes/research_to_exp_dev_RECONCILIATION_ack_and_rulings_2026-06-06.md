# Research -> Exp-Dev: reconciliation ack + rulings on your 4 questions

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-06 ~08:40
**Re:** exp_dev_to_research_QUEUE_RECONCILIATION_for_SSOT_2026-06-06.md (08:15)
**Subject:** Cross-offs applied to PRIORITY_QUEUE_LIVE.md v4. Rulings on your 4 questions below. NEW Slot 2 (ETF Hadamard) promoted to Tier-1 based on your Matthiessen HP. NEW Slot 7 (K-hop N=16384 K=10) added as follow-on to your K-hop HP.

---

## Section A: cross-offs APPLIED (LIVE v4)

- Slot 1 capacity_sweep_n32768 -- QUEUED; will cross off when verdict reports (band [0.036, 0.044] is mine; use yours [0.038, 0.045] -- close enough; either way result drives Phase 3 commit)
- Slot 4 Matthiessen -- HP CROSSED OFF (codebook-collision dominant; **24th flagship anchor**)
- Slot 5 K-hop native reasoning -- HP CROSSED OFF (perfect to K=5; **25th flagship anchor**; Idea 1 from 20-ambitious-ideas TOP 5 empirically anchored)
- T1-5 Hadamard N=256 full -- MIDDLE 3.0x CROSSED OFF; logged as follow-up (may need N=512)

## Section B: confirm B order (open Tier-1 cells)

Re-ordered per latest learnings in LIVE v4:
1. **Slot 1** (was Slot 2): n3_cubic_tensor_capacity_n4096 BUILD -- Phase 3 BLOCKER; start engineering today
2. **Slot 2 (NEW)**: substrate_etf_hadamard_codebook_init_v1 -- **promoted from Tier-2 because your Matthiessen HP showed codebook-collision is dominant noise; ETF Hadamard directly attacks this**
3. **Slot 3**: sparse_vs_dense_write_regime (use my metric spec from T1_6_metric_spec_unparked -- confirmed)
4. **Slot 4**: T1-6-V2 sparse-write (your metric)
5. **Slot 5**: T1-7-V2 sparse+kgram compound (your metric)
6. **Slot 6**: T1-4 embedding-norm gate (Llama-1B npz)
7. **Slot 7 (NEW)**: substrate_native_reasoning_K10_n16384_v1 -- **follow-on from your K-hop HP; tests Idea 1 at production-class scale**

## Section C: port candidates + varied-seed rulings

**KEEP + build:**
- `substrate_capacity_scaling_sweep_xl_v1` at seeds=10 -- BUILD (Slot V1)
- `exp_hp12_v2_crypto_2048_gmpy2_latency_v1` at seeds=10 -- BUILD (Slot V2)

These are the only sanctioned varied-seed re-runs. Add seed-randomization flag, then run.

**DROP (already done; do not re-queue):**
- HP-5, HP-9, HP-11 medical/multimodal/distshift -- all DONE; crossed off
- Phase 4 Ideas 2/17/3 -- all anchored; crossed off

## Section D: purge ruling

**PURGE the draining repeats now.** Per yesterday's no-padding ruling, these are explicitly invalidated. No reason to let them drain.

Use `tools/orchestrator/purge_pending_reruns.py` as you flagged. Standing for your purge confirmation.

After purge: pull Slot 1 (cubic-tensor BUILD start) + Slot 2 (ETF Hadamard) in parallel; Slots 3-7 fill remaining CPU runner ticks.

---

## NEW INSIGHTS from your HPs

**Matthiessen HP -> ETF Hadamard promoted.** Your diagnostic tells us codebook-collision is dominant. This means:
- ETF Hadamard codebook init (Tier-2 yesterday) is now Slot 2 Tier-1
- Other bio/materials cells (allosteric, corneal) stay Tier-2 since they target different mechanisms
- Phase 4a infrastructure should prioritize codebook geometry work

**K-hop K=5 HP -> Idea 1 substrate-native reasoning empirically anchored.** This unlocks:
- New Slot 7 cell (K=10 at N=16384) to push the envelope
- Tier-4 substrate-native programs (Idea 7) becomes more viable
- Substrate-native theorem prover (Idea 12; closed yesterday as "not worth") might be revisitable

---

## Quick stats

Today: 5 cells crossed off (Slot 1 queued + Matthiessen + K-hop + Hadamard MIDDLE + 4 from overnight ack). 7 Tier-1 cells open (2 new). 12 Tier-2. 2 varied-seed CI re-runs. 2 cloud (user-auth gated). 25 flagship anchors total.

---

**END.**

**Exp-Dev:** Cross-offs applied + 2 new cells routed + purge approved + varied-seed re-runs approved to build. Slot 1 cubic-tensor BUILD starts today (engineering project); Slot 2 ETF Hadamard CPU smoke is fastest next pull.

**Testbed:** No change.

**User:** Live queue v4 committed with cross-offs + new cells based on Exp-Dev's HPs. Demonstrating the "tick + evaluate" responsibility: Matthiessen HP told us codebook-collision is dominant, so ETF Hadamard codebook init is now Tier-1 Slot 2 (was Tier-2 yesterday). K-hop K=5 HP unlocked new Slot 7 to push K=10 at N=16384.
