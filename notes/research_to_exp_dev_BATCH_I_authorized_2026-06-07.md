# Research -> Exp-Dev: Batch I AUTHORIZED -- 6 cells consolidated across Drills A+B+C (closes fp16 + F4 gates + LoRA mechanism + pinv N=65,536)

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User + Testbed
**Date:** 2026-06-07 ~11:00
**Re:** Drills A (fp16 3x), B (LoRA 3x), C (F4 2x) all landed; strategic priority items
**Subject:** User authorized "Batch I." Consolidating top cells across 3 drills: bf16 production gate (Drill A); F4 PINV re-audit + W-sharding (Drill C); LoRA layer-depth probe (Drill B); pinv N=65,536 direct measurement (closes G2 extrapolation gap).

---

## Batch I composition (6 cells)

### TIER 1 -- Production gate closure (Drill A bf16)

**I1: bf16 overflow elimination at N=65,536**
- Anchor pointer: research_drill_fp16_N65536_overflow_3x_deep_2026-06-07.md Section 2.1 Anchor 1
- Why now: THE one open production gate. One-line dtype change (torch.bfloat16) predicted to eliminate overflow.
- Wall: GPU smoke (~15 min on A100+)
- HP: zero NaN/Inf at N=65,536 for M <= 26,214
- HF: NaN/Inf in final retrieval output

**I2: bf16 capacity parity vs fp32 at N=65,536**
- Anchor pointer: research_drill_fp16_N65536_overflow_3x_deep_2026-06-07.md Section 2.1 Anchor 2
- Why now: validate that 7-mantissa-bit precision of bf16 doesn't degrade capacity
- Wall: GPU full (~30 min on A100+)
- HP: alpha_c(bf16) / alpha_c(fp32) ratio > 0.95
- MID: 0.80-0.95
- HF: < 0.80

### TIER 2 -- Retroactive audit closure (Drill C F4)

**I3: F4 PINV re-audit (multi-head corruption at flip-rate sweep with PINV)**
- Anchor pointer: research_drill_F4_multi_head_corruption_2x_2026-06-07.md Anchor 1
- Why now: cycle 137 HF was Hebb-specific; PINV (cycle 143 lock) likely passes 20-30% envelope
- Wall: CPU ~30 min; flip-rate sweep at production conditions
- HP: pinv multi-head sustains alpha_c at flip rates up to 20%
- HF: collapse at < 10% flip rate (confirms not Hebb-specific)

**I4: W-sharing vs W-sharding architecture check**
- Anchor pointer: research_drill_F4_multi_head_corruption_2x_2026-06-07.md Anchor 2
- Why now: BFT analogy holds only if heads query INDEPENDENT W shards
- Wall: CPU ~10 min; architecture inspection + targeted test
- HP: production multi-head uses W-sharding (BFT-robust)
- HF: W-sharing (BFT advantage is illusory; corrupt one W -> corrupt all heads)

### TIER 3 -- LoRA mechanism resolution (Drill B)

**I5: Layer-depth RP probe (base vs CELL-5 LoRA at L=2, 6, 10, 15)**
- Anchor pointer: research_drill_LoRA_retrieval_degradation_3x_deep_2026-06-06.md cheap decisive test
- Why now: Drill B headline: SFT objective is structurally incompatible with retrieval geometry (P=0.72 for Hyp-A SFT decoder-semantics drift)
- Wall: ~3 min CPU; trivially cheap; resolves Hyp-A vs Hyp-C
- HP (confirms Hyp-A dominant): degradation is top-heavy (upper layers worse)
- HF (confirms Hyp-C active): degradation is uniform
- Strategic value: informs CELL-3 distillation design (feature-mimic at correct layer)

### TIER 4 -- Production throughput verification (gap closure)

**I6: Pinv write throughput DIRECT measurement at N=65,536**
- Anchor pointer: cycle 144 G2 measured 11,335 writes/sec at N=16,384 but extrapolated to ~708 writes/sec at N=65,536. Direct measurement closes the gap.
- Why now: production deployment claim depends on this; Drill A flagged as "Class S3 scale-sensitivity unverified before production HP"
- Wall: GPU profiling (~15 min on A100+)
- HP: throughput >= 500 writes/sec at N=65,536 (above production threshold 200/s)
- MID: 200-500 (viable but constrained)
- HF: < 200 writes/sec (production deployment requires Sherman-Morrison-Woodbury incremental rank-k approximation)

---

## Total estimate

- Tier 1 (I1+I2): ~45 min GPU
- Tier 2 (I3+I4): ~40 min CPU
- Tier 3 (I5): ~3 min CPU
- Tier 4 (I6): ~15 min GPU
- **Total: ~1.5-2h compute; $0-10 cloud if GPU goes remote**

Mostly local CPU/GPU; cloud only if local capacity constrained.

---

## What Batch I closes

If all cells land cleanly:

| Gate | Status post Batch I |
|---|---|
| fp16 at N=65,536 | ✅ CLOSED via bf16 |
| F4 multi_head_x_corruption | ✅ CLOSED via PINV re-audit |
| W-sharding architecture | ✅ Characterized |
| LoRA mechanism (Hyp-A vs Hyp-C) | ✅ Resolved; informs CELL-3 |
| Pinv throughput at N=65,536 | ✅ Directly measured (not extrapolated) |
| **Substrate production-deployment surface** | **100% empirically grounded** |

This is the FINAL empirical validation pass to lock production-readiness.

---

## Cross-references

- Drill A fp16 3x deep: notes/research_drill_fp16_N65536_overflow_3x_deep_2026-06-07.md
- Drill A handoff: notes/exp_dev_handoff_research_fp16_N65536_overflow_2026-06-07.md
- Drill B LoRA 3x deep: notes/research_drill_LoRA_retrieval_degradation_3x_deep_2026-06-06.md
- Drill B handoff: notes/exp_dev_handoff_research_LoRA_retrieval_3x_deep_2026-06-06.md
- Drill C F4 2x: notes/research_drill_F4_multi_head_corruption_2x_2026-06-07.md
- Drill C handoff: notes/exp_dev_handoff_research_F4_multi_head_corruption_reaudit_2026-06-07.md

---

## Contract

You design anchor specifics, sweep grids, HP/MID/HF threshold values (within drill bounds), queue assignments, timeout formulas. Pre-reg per envelope-fail-band protocol. ASCII-only.

I1 is the production gate; ship it first. I5 (layer-depth probe) is cheapest (~3 min); can run in any spare slot.

## Autonomy

You may:
- Reorder cells by queue state / runner availability
- Parallelize across CPU/GPU lanes
- Batch I5 + I3 + I4 on CPU lane while I1/I2/I6 run on GPU
- Skip I4 if I3 makes it redundant

---

**END.**

**Exp-Dev:** Batch I authorized (6 cells; ~1.5-2h compute; $0-10). I1 is production gate decisive. Tier ordering recommended but you override per queue state.

**User:** Batch I (6 cells consolidated across 3 drills) routed. Closes fp16 production gate + F4 audit + LoRA mechanism + pinv N=65,536 measurement gap. If all HP: substrate production-deployment surface is 100% empirically grounded.

**Orchestrator + Testbed:** Visibility only.
