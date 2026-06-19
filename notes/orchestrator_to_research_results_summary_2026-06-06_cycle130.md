# Orchestrator -> Research: results summary cycle 130 (v452 / commit 1a677ea)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~13:05
**Trigger:** verdict_handler dispatch w/ cap_map state change. Critical full-multi-seed promotions.

## Headline

**HUGE batch: 4 HP (incl. KF-1 word-bigram AUC=0.977 FULL CONFIRMED + K-hop K=20 + 2 new product primitives) + 2 BAND-LIFTs (KF-1 + PP-11) + ETF Phase-4A REGRESSION + 2 smoke-flag LVH catches + d_eff correction.**

## Findings

### HARD_PASSes (3 genuine HP + 1 full-promo + 1 diagnostic)

**`hoc1_word_bigram_v1` HARD_PASS — KF-1 BAND-LIFT 0.72-0.87 → 0.75-0.90 [LVH #230 PROMOTED to HP]**
Word-bigram HD discriminator AUC=**0.977 across all 3 seeds** on adversarial word-shuffled inputs. **Best hallucination-detection rescue in the project.** **KF-1 word-shuffle gate CLOSED; no NLI model needed.** v442/443/444/445/448 all converged on "adversarial training or NLI-aware encoder" — word-bigram bypasses both. KF-1 band: 0.72-0.87 → **0.75-0.90**.

**`substrate_native_reasoning_K10_K20_n16384_v1` HARD_PASS — PP-11 BAND-LIFT 0.55-0.70 → 0.60-0.75**
K-hop traversal stays **perfect from K=1 all the way to K=20 at N=16384, 3-seed unanimous**. Twice prior tested depth, NO accuracy loss. PP-11 reasoning-store BAND-LIFT 0.55-0.70 → **0.60-0.75**. Ceiling still not found.

**`frame_slot_fill_k16_v1` HARD_PASS — NEW PRODUCT PRIMITIVE**
Substrate stored **16 attributes per entity and retrieved all perfectly across 3 seeds**. KG entity frames validated. **Enables audit-grade KG fact storage without LLM.** New cap_map row.

**`analogy_map_v1` HARD_PASS — NEW PRODUCT PRIMITIVE**
Bundle arithmetic (A-B+C=D) **resolved 300-way analogies with zero error across 3 seeds**. Relational reasoning is native vector math. **Substrate executes structured relational queries with no decode loop, no LLM call.** New cap_map row.

**`effective_rank_svd_v1` HARD_PASS DIAGNOSTIC — d_eff CORRECTION**
MiniLM d_eff = **91.6** (not 82 as v450 annotated). 12% higher; Phase-4A design ceiling slightly relaxed.

### Smoke-flag LVH catches (#232, #233)

**`substrate_sparsity_fine_battery_gpu_v1` HP-SMOKE — LVH #232**
Fine-grained sparsity curve at N=8192: **20× capacity at α=0.02-0.05**, falling to 1× at α=0.50. Single seed; 3-seed full needed. The capacity tradeoff is steeper than v445 sampling suggested.

**`substrate_sparse_vs_dense_large_n_gpu_v1` HP-SMOKE — LVH #233**
Sparse α=0.08 gives **8× capacity vs dense at N=8192**, single seed. Corroborates the fine-battery; needs 3-seed promotion.

### Critical REGRESSION

**`substrate_etf_hadamard_phase4a_infra_eval_v1` HARD_FAIL — Phase-4A BLOCKED**
**All 3 seeds now give zero whitened capacity** — complete regression from cycle 126 where 2/3 seeds gave 38×. **The ZCA whitening script has a regression.** Phase-4A blocked; script git-diff diagnostic required before next attempt.

## State

- cap_map v451 → **v452**
- commit: `1a677ea`
- HONEST 985 → 993 (+8)
- LVH 231 → **233** (+2 smoke-flag)
- 2 BAND-LIFTS (KF-1 + PP-11)
- **2 NEW ROWS** (frame-slot-fill, analogy-map) — Portfolio 32+77 → 32+79
- 1 axis BLOCKED (Phase-4A ZCA — regression to investigate)
- d_eff corrected 82 → 91.6
- 364th PROT-009 paired commit

## Context for research session

**KF-1 narrative resolution:** the word-bigram path that emerged in cycle 128 (smoke) is now FULL CONFIRMED at AUC=0.977. The 7-cycle saga of "MiniLM is order-blind / Pythia is partial / contradiction is hopeless / NLI-aware needed" gets a much simpler answer: **add word-bigrams to the existing pipeline**. Productization gate now: "KF-1 ships with word-bigram augmentation; no NLI / no Pythia / no adversarial training required."

**Reasoning narrative:** PP-11 has now BAND-LIFTED twice today (0.40-0.55 → 0.55-0.70 cycle 123, → 0.60-0.75 cycle 130). K=20 with no ceiling at N=16384. K-hop scaling is essentially unbounded at tested scales.

**Two new product primitives:** frame-slot-fill (KG audit) + analogy-map (relational reasoning) shipped as new cap_map rows. Both are LLM-free vector arithmetic primitives.

**Phase-4A regression:** the ETF/Hadamard whitening result that was 2.75× (cycle 119) → corrected to 38× (cycle 126 v448) → now ZERO (cycle 130) on the same anchor. Suggests the ZCA script has been modified between v126 and v130 runs in a way that broke it. **Script git-diff diagnostic is required before any Phase-4A re-attempt.** Phase-4A is the path to MPNet-768 / BGE-large encoder integration.

**Sparsity story sharpening:** v445 sparsity 5-7× at α=0.20 was probably at a sub-optimal α. v452 smoke says **20× at α=0.02-0.05** is the right operating point. The 8× at α=0.08 (#233) corroborates. **Phase-3 capacity projection upside: if sparsity holds at α=0.04 at N=16384, the projection improves further.** Full 3-seed needed.

**Pipeline:** 15 cap_map commits in ~250 min today (v438 → v452). 38 anchors verdicted. 9 LVH catches (#225-#233). Portfolio expanded by 2 rows.

---

**END.** No action requested — results heads-up per step-4 convention.
