# RESEARCH (Director) -- STRATEGIC SYNTHESIS AMENDMENT (commits 5a6dc02d). USER caught: my Phase 3 Milestone 1 proposed a hybrid (Pythia+substrate-KV RAG), violating USER-LOCKED rule "substrate standalone-capability FIRST; no LLM comparisons" + "no LLM positioning". Retracting; substrate-native reframe below. USER ratified the substrate-native version ("sounds good"). Brief.

(Filename has no `to_<recipient>` — Director self-catch + working artifact.)

## Director self-catch
My prior synthesis proposed `exp_glass_box_LLM_milestone_1_substrate_RAG_v1_gpu_v1` = Pythia-2.8B + substrate-KV. That's a HYBRID — Pythia as a component, not just a benchmark. Violates the USER-LOCKED rules from 2026-06-13 (`feedback_substrate_standalone_capability_first_before_LLM_positioning_USER_LOCKED_2026-06-13` + `feedback_no_llm_comparisons_substrate_quality_first_2026-06-12`). Same family as a prior self-catch on LLM-vs-substrate positioning. Caught by USER not by me — adding to Director self-catch ledger this session (13 catches total now; cite-without-verify-USER-LOCKED-rule pattern).

## Phase 3 Milestone 1 reframed: substrate-native answer-generation

**`exp_substrate_native_answer_generation_milestone_1_cpu_v1`**

**Architecture (substrate-only; no external LLM in the loop):**
- Substrate stores N facts (target N=10k for full; smoke N=500) via #7 learned projection (CERT 591 — keys decrowded; recall mechanism settled)
- Substrate-native query handler:
  - Input query → encode → key against substrate-KV
  - Chain-recall via K_max NESS envelope (CERT 592 — traverses correct next-node, 2-12× beyond classical equilibrium)
  - Composition primitives assemble answer
  - Refuse-gate (#5 path A) activates if query out-of-envelope (concentration check; refuses vs fabricates)
- Output: substrate's answer to the query + full traceability (every fact-id used, every chain hop, every refusal decision)

**No Pythia / no transformer / no LLM in the architecture.** LLM = benchmark only (run same queries against raw LLM; compare answers for accuracy + transparency + refuse-vs-hallucinate behavior). The LLM is NOT a component; it is the comparator-of-record.

**3-arm CAN-fail discriminating regime (per Skunkworks's LEVER #1.5 R2 discipline):**
- **Arm 1 (substrate-native, full pipeline):** above
- **Arm 2 (substrate-without-refuse-gate):** substrate answers everything even when out-of-envelope (would fabricate); CAN-fail baseline showing refuse-gate's actual value
- **Arm 3 (substrate-without-#7-projection):** raw keys (no contrastive projection); CAN-fail baseline showing #7's actual value
- **Discriminating iff** substrate-native (Arm 1) beats BOTH (a) Arm 2 (refuse-gate matters: factual correctness + non-hallucination) AND (b) Arm 3 (projection matters: recall accuracy) by thresholds.

**HARD_PASS bands (proposal; data-decides):**
- Factual recall on in-envelope queries: ≥0.70 substrate-native vs Arm 3 ≤0.50 baseline (projection-value gate)
- Refuse-rate on out-of-envelope queries: ≥0.90 substrate-native vs Arm 2 ≤0.30 (refuse-value gate)
- Transparency: 100% (every answer traceable to fact_ids + chain hops)
- LLM-comparator: substrate-native ≥ raw-LLM factual correctness OR substrate-native dramatically wins on refuse-rate (substrate refuses; LLM hallucinates)
- 3 seeds; perfectly stable per the LEVER 1.5 stability bar (cv → 0)

**Composes_with:** CERT 591 (#7 projection) + CERT 592 (chain-recall depth-beyond-equilibrium) + refuse-gate #5 path A + sparse super-capacity a3f473dd (if sparse-encoded variant)

**Cert tier target:** CHAIN-GRADE-CANDIDATE (data-decides per cb7e89f1).

**Scope-guard:** substrate-only architecture (no Pythia/LLM components); factual-recall + refuse-behavior in this milestone (not reasoning chains; those are Milestone 2 onward).

## What this DOESN'T do (per USER-LOCKED rules)
- Does NOT compare substrate vs LLM as a positioning claim (LLM = neutral comparator)
- Does NOT use LLM as a component
- Does NOT frame as "substrate-augmented LLM" (the wrong direction)
- Does NOT need an LLM at deployment time

## Standing
- **USER:** ratified substrate-native reframe.
- **Skunkworks:** SCHEMA-VET on this Milestone 1 when ready (parallel to scour-batch + LEVER 1.5 landed-VET; no urgency).
- **Exp-Dev:** cell-author on SCHEMA-VET-pass (substrate-only; no Pythia integration).
- **Me:** amendment filed; plan.json update reflecting substrate-native framing; Phase 3 cost A+B routing to Skunkworks; URGENT dashboard build routing to Testbed (parallel notes this turn).

-- Research (Director)
