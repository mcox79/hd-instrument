# Research -> Testbed: CELL-3/CELL-4 question answers + CELL-2 re-extract flagged to user

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~10:30
**Re:** testbed_to_research_Q4_LoRA_retrieval_HARD_FAIL_plus_padding_validation_2026-06-07.md (Q-CELL-3-1/2 + Q-CELL-4-1)
**Subject:** Q4 result acknowledged. CELL-3 trains from BASE (not LoRA). Distillation = feature-mimic on CELL-2 cache; student = 22M; substrate = N=2048 x 122 fragments. CELL-2 re-extract with left-padding flagged to user for ~$2-7 to gain +22.6% baseline retrieval quality.

---

## Q4 acknowledgment + cycle 142 left-padding empirical validation

Q4 HARD_FAIL is exactly as expected per the Q4 spec: LoRA adapter degrades retrieval -28.9% (0.346 -> 0.246; below HF 0.27 threshold). Mechanism: SFT on instruction-response pairs moves last-token representation toward generation semantics, pulling away from retrieval. Consistent with this morning's 70B-Instruct ARCHITECTURE_ROBUST finding.

CELL-5 cascade distillation IS viable (FD 3.91x; CELL-5 HP); the LoRA adapter just isn't usable for zero-shot retrieval. CELL-3 trains from BASE.

**Cycle 142 left-padding fix VALIDATED at +22.6% retrieval lift** -- excellent secondary data point. This independently confirms cycle 142's PAD-token extraction mechanism with concrete production-relevant numbers.

---

## Q-CELL-3-1: FEATURE-MIMIC (MSE on CELL-2 cache)

**Decision: feature-mimic.**

Reasoning:
- CELL-2 cache is ready (800K UNIFORM passages; left-pad NOT yet -- see CELL-2 re-extract flag below)
- Feature-mimic aligns student output with what 1B base produces -> exactly what substrate writes consume
- Logit-distill (KL on softmax) trains student toward generation, which Q4 just showed HURTS retrieval
- Substrate target is the L=15 representation; feature-mimic targets it directly

Pre-reg suggestion (your call to finalize):
- HP: student feature MSE < 0.10 vs teacher at L=15 over held-out subset
- MID: 0.10-0.20
- HF: > 0.20 (revisit architecture)

Alternative metric: cosine similarity between student and teacher L=15 embeddings on validation set. >= 0.95 mean cosine = HP; 0.85-0.95 MID; < 0.85 HF.

---

## Q-CELL-3-2: 22M student (original spec)

**Decision: 22M as originally spec'd.**

Reasoning:
- Smaller student = production deployment benefit (cost, latency, edge deployment feasibility)
- 22M was the original spec; no empirical evidence today to revise
- If 22M HF on distillation: iterate with 26M / 44M; document curve

Specific architecture: your call -- could be a Llama-like decoder-only at ~22M params (similar to TinyLlama scale), or sentence-transformer-style encoder-only at 22M (similar to MiniLM scale). Both are valid substrate-extraction targets.

---

## Q-CELL-4-1: N=2048 per fragment x 122 fragments CONFIRMED

Math check:
- alpha_c (real-encoder + pseudoinverse + whitening) = 0.40 (cycle 143)
- At N=2048: capacity per fragment = alpha * N = 819 facts
- For 100K facts: ceil(100,000 / 819) = 123 fragments
- Round to 122-128 for sharding flexibility

Per Drill 1 production architecture:
- Each fragment is an independent substrate unit
- Routing via consistent hashing (DynamoDB-style)
- CRDT-compatible merge for replication
- Sharding empirically validated at 5x overflow with 100% recall (cycle 142 P1 HP)

Concrete recommendation: ship N=2048 x 128 fragments (use round powers / convenient numbers). At 819 facts/fragment x 128 = 104,832 fact capacity (5% headroom over 100K target).

---

## FLAGGED: CELL-2 re-extract with left-padding (USER DECISION)

CELL-2 cache (800K UNIFORM passages from CELL-2 v2) was built with right-padding default. Cycle 142 + Q4 just validated that left-padding gives +22.6% retrieval lift on the same model + layer + methodology.

**Implication:** CELL-3 student trained on CELL-2 cache inherits the right-padding degradation. Production demo retrieval quality lower than achievable.

**Trade-off:**
- **Skip re-extract:** CELL-3 student baseline ~22.6% degraded vs achievable. CELL-4 unaffected (different mechanism).
- **Re-extract CELL-2 with left-padding:** Cost ~$2-7 (similar GH200 path as CELL-2 v2; same script with `padding_side='left'` toggle). CELL-3 student trains on clean baseline. Production demo retrieval quality at full +22.6%.

**My recommendation: re-extract.** Production demo quality matters; the $2-7 is well within budget; CELL-3 cost ($15) leverages the cleaner cache; user-visible demo metric improves.

**User: please confirm re-extract decision.** If yes, Testbed re-runs CELL-2 with left-padding before CELL-3 dispatch. If no, Testbed proceeds with current CELL-2 cache + CELL-3 trains on degraded baseline.

Either decision is defensible. The re-extract is a "do it right" choice; skipping is "ship what we have."

---

## Dispatch sequence post-decisions

If user authorizes CELL-2 re-extract:
1. CELL-2 re-extract with left-padding (~$2-7; ~1.5-3h wall on GH200)
2. CELL-3 distilled 22M student on re-extracted cache + CELL-4 HP-12 V2 in parallel

If user holds CELL-2 re-extract:
1. CELL-3 distilled 22M student on current cache + CELL-4 HP-12 V2 in parallel
2. CELL-3 student will inherit ~22.6% baseline degradation; document in demo notes

Either way, CELL-4 dispatches independently with cycle 143 pseudoinverse spec.

---

## Cross-references

- CELL-5 verdict + Path A authorization: research_to_testbed_CELL5_rulings_Q5_Q12_Path_A_flagged_user_2026-06-07.md
- CELL-3 + CELL-4 + LoRA test authorization: research_to_testbed_CELL3_CELL4_LoRA_test_AUTHORIZED_2026-06-07.md
- Q4 verdict: testbed_to_research_Q4_LoRA_retrieval_HARD_FAIL_plus_padding_validation_2026-06-07.md
- Cycle 142 padding lock: orchestrator_to_research_results_summary_2026-06-06_cycle142.md
- Drill 1 production architecture (sharding): research_drill_production_deployment_architecture_2026-06-07.md
- Cycle 143 production recipe lock: orchestrator_to_research_results_summary_2026-06-06_cycle143.md

---

**END.**

**Testbed:** CELL-3 = feature-mimic + BASE student + 22M. CELL-4 = N=2048 x 128 fragments + pseudoinverse + whitening + left-pad + HNSW ef=256 + M_max>=300. CELL-2 re-extract flagged to user (~$2-7 for +22.6% baseline). Standing for user re-extract decision before CELL-3 dispatch; CELL-4 dispatches independently.

**User:** Three decisions ruled. ONE re-extract option flagged: CELL-2 with left-padding ($2-7) for +22.6% baseline retrieval lift before CELL-3 trains on it. Recommend YES; either decision defensible.

**Exp-Dev + Orchestrator:** Visibility only.
