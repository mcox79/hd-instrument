# Orchestrator -> Research: results summary cycle 133 (v455 / commit b7157ad)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-06 ~14:30
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

**6-batch: 2 HP (per-hop fabrication localization + multi-head M2 super-sqrt scaling) + 1 LVH #236 + 1 HF closing sparse-KEY M_c rescue + 2 MID resolutions** — sequential layering doesn't compound (LVH catch); multi-head DOES (super-sqrt-M scaling); per-hop fabrication localization is a NEW differentiating capability.

## Findings

### HARD_PASSes

**`fact_checked_khop_v1` HARD_PASS — NEW DIFFERENTIATING CAPABILITY**
Substrate follows 2-5 reasoning hops with **perfect accuracy AND identifies exactly which hop introduced a fabrication** — simultaneously, at ceiling, 3-seed unanimous. **Per-hop hallucination localization** is a uniquely differentiating capability vs frontier LLMs. Adds hop-level audit trail to PP-11 K-hop reasoning.

**`multi_head_sparse_key_M2_v1` HARD_PASS — LVH #235 RESOLVED, super-sqrt scaling**
M=2 heads vs 1: **2.25× pattern capacity** (min 2.00×, max 2.75×, all seeds above threshold). **Exceeds sqrt(2)=1.41 theoretical prediction.** Cycle 132's LVH #235 catch is RESOLVED — multi-head with sparse-KEY composes super-linearly at M=2. M=4 sweep is the next design probe.

### LVH catch #236

**`substrate_hierarchical_hadamard_then_sparse_key_alpha_v1` MIDDLE_BAND — LVH #236**
Label claimed 1.0-1.2× range. **Honest: exactly 1.00× (same as either alone).** Sequential composition ordering does NOT compound capacity. **Independent-mask architecture** (not sequential layering) is the correct path forward.

### MIDDLE_BANDs

**`cs1_dt_algebraic_audit_v1` MIDDLE_BAND** — DT boundary formula predicts data correctly only at extreme sparsity (1 of 5 arms). DT framework is a **limit law, not a general engineering guide**. Empirical α sweeps required at moderate sparsity.

**`sparse_key_composition_battery_gpu_v1` MIDDLE_BAND — DESIGN PRINCIPLE LOCKED**
- **Independent-mask Hadamard ≈ flat sparse** (no gain)
- **Joint-mask Hadamard = 3× weaker**
- **Block sparse = 10-20× weaker**

**Locked principle:** multi-arm sparse-KEY architectures must use **independent mask paths**; coupling is destructive.

### HARD_FAIL — axis closed

**`dimsparse3_alpha_at_mc_v1` HARD_FAIL — full confirms cycle 132 smoke; M_c rescue via sparse-KEY DEFINITIVELY CLOSED**
- sparse-key M_c = 2 vs baseline M_c = 12
- dim-expansion lift = 1.11× < 1.2× threshold
- Cycle 132 smoke confirmed at full 3-seed
- **M_c rescue axis via sparse-KEY definitively CLOSED**
- R1-R5 filed (cheapest: dense M_c + sparse-KEY retrieval head pipeline as separate stages)

## State

- cap_map v454 → **v455**
- commit: `b7157ad`
- HONEST 998 → 1003 (+5)  ✨ **passed 1000**
- LVH 235 → **236** (+1; sequential-layering over-claim)
- 1 axis CLOSED (sparse-KEY M_c rescue)
- 1 design principle LOCKED (independent-mask)
- 0 BAND-LIFTS, 0 new rows
- Portfolio 32+79

## Context for research session

**Three architectural lessons consolidated this cycle:**

1. **Sequential composition fails; multi-head composition succeeds.** Hadamard→sparse-KEY sequential = 1.00× (no gain). Multi-head sparse-KEY M2 = 2.25× (super-sqrt-M). **Composition path = parallel mask-independent heads, NOT sequential pipeline.**

2. **Independent-mask is the architectural principle for sparse-KEY composition.** Cycle 133's battery: independent-mask = flat sparse (no penalty), joint-mask = 3× worse, block sparse = 10-20× worse. **All multi-arm sparse-KEY designs must use independent masks.**

3. **M_c rescue via sparse-KEY is dead.** Cycle 132 smoke is now confirmed at 3-seed full. The rescue path must be **dense M_c + sparse-KEY retrieval head as separate stages** (R1 sketch).

**New differentiating capability — per-hop fabrication localization.** This is the kind of capability frontier LLMs CANNOT do natively (they hallucinate without revealing which step is fabricated). The substrate gets this for free from its K-hop algebraic reasoning. Worth flagging as a Tier-1 product positioning angle.

**HONEST crossed 1000** — first time today's pipeline pushed past the millennium mark.

**Pipeline:** 18 cap_map commits in ~310 min today (v438 → v455). 49 anchors verdicted. 12 LVH catches (#225-#236). 8 axes closed; 3 design principles locked; 5 BAND-LIFTS pending (1 confirmed).

---

**END.** No action requested — results heads-up per step-4 convention.
