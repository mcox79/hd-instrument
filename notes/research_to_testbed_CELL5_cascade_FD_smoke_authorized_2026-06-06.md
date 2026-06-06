# Research -> Testbed: CELL-5 cascade distillation FD smoke AUTHORIZED (~$2-5)

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~18:15
**Re:** exp_dev_handoff_research_cloud_portfolio_post_CLOUD1b_2026-06-06.md CELL-5
**Subject:** User approved CELL-5 cascade distillation FD ratio smoke. Independent of CELL-1; can dispatch immediately or in parallel.

---

## User approved CELL-5

Per Drill B's cloud portfolio synthesis.

### Cell spec (from Drill B research note):

- **Anchor:** `substrate_cascade_distillation_fd_ratio_smoke_v1`
- **Cost:** ~$2-5 (cloud API + H100)
- **Wall:** ~4 hours
- **Architecture:** FD ratio (fine-tuned-1B, 405B) / (off-shelf-1B, 405B) on 5K sentences
- **HP threshold:** FD ratio < 0.40 (>60% reasoning-quality gap closed)
- **MID:** FD ratio 0.40-0.70
- **HF:** > 0.70 (cascade distillation doesn't work)

### Independent of CELL-1 fp16 70B disambiguation

Can dispatch immediately OR run in parallel with CELL-1 (already authorized). Your call on timing -- both are independent binding answers.

### Strategic value

Binds whether cascade distillation (405B -> 70B -> 8B -> 1B) closes the FD gap for reasoning-quality extraction. Relevant if we ever want to push reasoning quality beyond retrieval (CLOUD-1b showed 1B is sufficient for retrieval but cascade matters if we want to extract reasoning).

Low cost; high optionality. Good cell for portfolio.

---

## Status of OTHER cloud cells

- CELL-1 fp16 70B disambiguation: AUTHORIZED earlier today (~$3-5)
- CELL-2 Wikipedia extraction at L=15: NOT authorized ($31-50; user holding decision)
- CELL-3 distilled student: NOT authorized ($15; gated on CELL-2)
- CELL-4 HP-12 V2 at 100K: NOT authorized ($10-20; gated on CELL-2)

So your active scope: CELL-1 + CELL-5. ~$5-10 total.

---

**END.**

**Testbed:** CELL-5 cascade distillation FD ratio smoke authorized at ~$2-5. Independent of CELL-1; dispatch when convenient. Combined CELL-1 + CELL-5 active scope ~$5-10.

**User:** CELL-5 routed to Testbed. Plus Standard Batch A (4 cells; <20 min CPU) routed to Exp-Dev separately. All other cells (CELL-2/3/4 + Standard Batches B/C) awaiting your future authorization.
