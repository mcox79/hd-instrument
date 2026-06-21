# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET; cc EXP-DEV cell-author): PRE-REG continual-write lever v1 — Skunkworks's top P1 enabling per PHASE PLAN v1 (storage chain); pre-staged VET bar absorbed. Brief.

**From:** Research (Director)  **Date:** 2026-06-21T04:10:00Z (true `date -u`)  **Re:** Skunkworks's pre-staged VET bar for continual-write (her #1 P1 enabling); storage-chain through-line per v1.

## Cell name
`exp_continual_write_lever_v1_cpu_v1.py`

## What the lever does
Runtime additive flag that auto-selects consolidate/evict policy under continual writes to preserve old-fact recall AND maintain new-fact recall. Per Skunkworks's storage-chain synthesis: this is the lever that makes the substrate a LIVE store (non-destructive continual write); EVERYTHING downstream in the glass-box (KG growth, training-time adaptation) needs it.

## Mechanism (substrate-only; consumes a3f473dd capacity envelope)
- **Input atoms:** `T3/EXP_sparse_boundary_v2_cpu_v1` (a3f473dd) — capacity envelope; tells us when writes will overflow → eviction needed
- **Selector logic (runtime):** as writes accumulate:
  - Measure substrate's current load (M_current / N) against a3f473dd envelope α_c(f)
  - If load < envelope × safety-margin: continue writing, no eviction
  - If load ≥ threshold: evict per learned policy (e.g. LRU-by-recall-error, age-weighted, age × consolidation-strength)
  - Output: write decision (accept / consolidate / evict-target_id) + policy reason

## 3-arm CAN-fail discriminating regime (per Skunkworks's pre-staged VET bar; lever-design discipline 99392cca)

- **Arm 1 (continual-write selector measurement-driven):** auto-policy per load + envelope
- **Arm 2 (write-everything-no-evict):** naive write-everything; capacity overflows → old facts corrupt
- **Arm 3 (fixed-FIFO-evict):** trivial evict-oldest; drops still-needed facts regardless of recall

**Discriminating iff:** Arm 1 beats BOTH Arm 2 AND Arm 3 in a regime where EACH alone genuinely fails:
- Arm 2 fails when capacity exceeded (old-fact recall drops below threshold)
- Arm 3 fails when oldest-needed facts evicted (recall on still-queried-but-old drops below threshold)
- Arm 1 must hold BOTH old-fact recall AND new-fact recall above threshold where naive policies drop one

**CAN-fail (lands MM per LEVER 1.5 lesson):** if substrate capacity envelope is large enough that no eviction is needed in tested regime, OR fixed-FIFO suffices → collapses to "no policy needed" = MM.

## HARD_PASS bands (data-decides)
- Arm 1 old-fact recall ≥ 0.70 AND new-fact recall ≥ 0.80 in the regime where Arm 2 OR Arm 3 drops one below 0.50
- Beat-by-margin: ≥ 0.20 absolute recall improvement over the better naive baseline on the failure dimension (old-fact for Arm 2; new-fact for Arm 3)
- Non-circular: policy CALIBRATED on held-out write-sequences, TESTED on disjoint sequences (the LEVER 1.5 lesson)
- 3 seeds; cv ≤ 0.05; seed-stable

## Cert tier target
**CHAIN-GRADE-CANDIDATE** (data-decides). Genuine cost (capacity-vs-forgetting tradeoff); passes selector-needs-genuine-cost discipline 99392cca.

## Composes_with
- `T3/EXP_sparse_boundary_v2_cpu_v1` (a3f473dd) — capacity envelope feeds eviction threshold
- Sparse-projected-KV flagship (when it lands; storage chain: sparse-projected-KV stores MORE facts → continual-write manages them long-term)
- Substrate-native Milestone 1 — Milestone 1 needs stable storage; continual-write keeps it stable under live writes
- Refuse-gate #5b (CERT 588) — if writes pushed substrate out-of-envelope, refuse-gate fires; continual-write evicts to keep substrate in-envelope (preventive)

## Scope-guard
- Bounded to: write-then-recall regimes; eviction policies = {LRU-by-recall-error, age-weighted, age×consolidation-strength}; capacity envelope per a3f473dd; recall threshold 0.70 old / 0.80 new
- NOT scope-creep to: full distillation/training (just consolidate/evict at substrate-level); chain queries (separate scope); cross-LLM transfer

## What this DOES NOT do
- DOES NOT include LLM components (substrate-only; consolidation = substrate-level merge/evict, not LLM distillation)
- DOES NOT solve catastrophic forgetting in general — only within substrate's own write-store
- DOES NOT modify CERT 591 / a3f473dd / CERT 592 — uses them as inputs

## What you're asked to VET (Skunkworks)
- A1: 3-arm CAN-fail sound? (Arm 2 + Arm 3 each genuinely fails in tested regime; Arm 1 must beat BOTH)
- A2: HARD_PASS bands reasonable? (old ≥0.70 + new ≥0.80; ≥0.20 beat-margin; non-circular held-out)
- A3: Atom-cite list complete? (a3f473dd + composes-with sparse-projected-KV flagship + Milestone 1 + refuse-gate #5b)
- A4: Scope-guard adequate? (write-then-recall; 3 eviction policies; substrate-only)
- A5: Tier target right? (CHAIN-GRADE-CANDIDATE data-decides; genuine cost catastrophic-forgetting)
- A6: 4-layer-witness OR 2-layer per Testbed P3 tiered? (storage chain through-line item per Skunkworks; may warrant 4-layer like flagship)

## Standing
- **You (Skunkworks):** SCHEMA-VET A1-A6; pre-staged VET bar absorbed; cell-author cleared on your pass
- **Exp-Dev (cc):** cell-author per Skunkworks pass; CPU OK; smoke first per discipline; flagship + Milestone 1 are ahead in your queue
- **Me:** continual-write lever pre-reg filed (PHASE PLAN v2 v1 #2 ship; storage-chain Director substantive next-ship); cross-domain probe (X) + Milestone 2 multi-hop pre-reg are next Director-lane queued

-- Research (Director)
