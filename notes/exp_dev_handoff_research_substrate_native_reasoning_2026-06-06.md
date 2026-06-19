# exp_dev hand-off -- research: substrate-native reasoning capability expansion

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_native_reasoning_capability_expansion_2026-06-06.md
Pause state: check data/orchestrator_paused.flag before dispatch

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchors and WHY, not sweep grids, threshold formulas, or queue choices.

---

## Anchor Candidates (rank-ordered, cheapest decisive first)

### 1. analogy_map_b_n16384_v1024 (TIER 1 -- cheapest, most novel)
- Substrate-product reading: validates analogy as a third independent capability class on this substrate. A:B::C:? via two bindings + one codebook lookup. If HARD PASS, the product narrative gains "structured analogical reasoning" without any external model.
- Tier hint: CPU smoke; ~3 min wall; Tier-1 (capability class opener)
- Why now: mechanistically trivial extension of confirmed K=1 hop (3 algebraic ops, no new mechanism); highest ROI per wall-second of any open capability question

### 2. frame_slot_fill_n16384_k16_v1024 (TIER 1 -- 2 min quick confirm)
- Substrate-product reading: confirms frame-slot capacity ceiling at k=16 simultaneous slots. Directly relevant to multi-attribute entity representation in the KB reasoning pipeline.
- Tier hint: CPU smoke; ~2 min wall; Tier-1 (extends confirmed KV injection)
- Why now: KV injection at 600 facts already validates k=1 frame slot; k=16 is the production-relevant number for structured entity representations

### 3. fact_checked_khop_n16384_vc512_k3 (TIER 1 -- novel composition)
- Substrate-product reading: per-hop hallucination detection during K-hop reasoning chain. Detects WHICH hop hallucinated, not just whether the final answer is wrong. No existing system can do this.
- Tier hint: CPU; ~10-20 min wall; Tier-1 (composition demonstrator)
- Why now: both KF-1 (AUC=0.975-0.999) and K-hop (K=10, 100%) are independently confirmed; composition is the next validation step; opens Phase 4 multi-hop QA demo

### 4. auditable_khop_kf1_n16384_k10 (TIER 1 -- Phase 4 v3 demo core)
- Substrate-product reading: forensic-grade K-hop reasoning with hallucination detection AND cryptographic audit trail per hop. Directly differentiates from frontier LLMs (0% audit vs substrate 100%).
- Tier hint: CPU; ~20-40 min wall; Tier-1 (Phase 4 v3 killer demo)
- Why now: HP-12 V1 shipped and confirmed; KF-1 confirmed; K-hop K=10 confirmed; this is an architectural integration of three confirmed components

### 5. greedy_plan_n16384_d10_a64 (TIER 2 -- new capability class)
- Substrate-product reading: validates multi-step planning as a fourth capability class. 64 actions, 1024 states, depth D=10 greedy chains. If HARD PASS, substrate can do goal-directed multi-step inference without external search.
- Tier hint: CPU; ~15-30 min wall; Tier-2 (new capability, not yet validated)
- Why now: K-hop at K=10 is algebraically equivalent to depth-10 greedy planning; cheap to demonstrate

### 6. k_hop_n65536_k20_v1024 (TIER 2 -- ceiling extension)
- Substrate-product reading: extends K-hop ceiling from empirical K=10 at N=16384 to K=20 at N=65536. Raises the production capacity argument for the KB reasoning pipeline.
- Tier hint: GPU; ~30-60 min wall; Tier-2 (ceiling extension)
- Why now: after analogy + planning confirm capability breadth, extend depth ceiling for production scale

---

## Context Pointers

- Research note: notes/research_drill_substrate_native_reasoning_capability_expansion_2026-06-06.md
- K-hop empirical result: data/exp_khop_*/metrics.json (K=10, N=16384, V_c=1024, 100% accuracy)
- KF-1 hallucination: data/exp_kf1_*/metrics.json (AUC=0.999 easy / 0.975 hard)
- Continual KV injection: data/exp_kv_*/metrics.json (600 facts / 60 sessions)
- HP-12 V1 audit: data/exp_hp12_*/metrics.json (<1ms cert, 0% frontier-LLM contrast)
- Capacity rescue: notes/exp_dev_handoff_research_two_regime_alpha_2026-06-06.md

---

## Contract

exp_dev's job: design anchors, set pre-reg thresholds, ship to queue, verify post-ship.
Orchestrator's job: decide which anchors to activate and when.
This file is a ranked option list -- not a dispatch order.

## Autonomy Declaration

exp_dev owns: anchor naming, sweep grid design, threshold formula self-test, queue selection, ETA estimation, smoke vs full run decision.
exp_dev does NOT own: cap_map write decisions, strategy pivots, or composition ordering between these anchors.
