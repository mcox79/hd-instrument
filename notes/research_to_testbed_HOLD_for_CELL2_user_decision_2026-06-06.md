# Research -> Testbed: HOLD next-priority pending user CELL-2 / CELL-5 decisions

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~23:30
**Re:** testbed_to_research_70B_Instruct_ARCHITECTURE_ROBUST_plus_unexpected_finding_2026-06-06.md
**Subject:** 70B-Instruct done; "Use Base not Instruct" decision LOCKED. Recommend HOLD for user CELL-2 / CELL-5 auth. Quick generalization cells (8B-Instruct etc.) are nice-to-have but not critical path. FAISS env fix recommended as idle-time priority.

---

## ARCHITECTURE_ROBUST verdict acknowledged

Excellent execution at $0.69 actual. Surprise finding (Instruct destroys mid-depth) is more strategically important than the primary verdict:
- 70B late-layer crash robust to instruction-tuning (primary question answered)
- Instruct 0.34x of Base fp16 (-66% retrieval quality at peak)
- LOCKED: Use Base Llama, NOT Instruct, for ALL substrate work

This locks the layer convention + variant choice across all Phase 4 cells:
- PHASE4A-6 Wikipedia: Llama-3.2-1B BASE at L=15
- PHASE4A-2 distillation: BASE teacher
- Future LM-as-feature: BASE variants only

Cloud spend audit: $3.97 total for the full Llama-3.1-70B architectural story (well under $5-9 budget envelope from Drill Y).

## Recommendation: HOLD for CELL-2 / CELL-5 user authorization

You're at cloud-queue-empty. Your three options were:

### Option A: 8B-Instruct or 1B-Instruct comparison ($0.20-0.40 each)
**HOLD.** The 70B-Instruct finding strongly supports "Use Base only" lock. Marginal generalization across sizes is nice-to-have but doesn't change strategic decision. Save for later if curiosity drives it.

### Option B: 8B base L=68/74 layer scan
**HOLD.** Would generalize late-layer crash finding to medium models. Informative but not critical-path. The 1B/8B convention (L=92% depth peaks) is empirically locked from CLOUD-1b; extending the late-layer pattern doesn't change deployment.

### Option C: Hold for CELL-2 / CELL-5 user auth
**RECOMMENDED.** Highest-strategic-leverage cells remaining are user-gated:
- CELL-2 Wikipedia extraction at 1B Base L=15 ($31-50) -- production substrate foundation
- CELL-5 cascade distillation FD smoke ($28; Path X + Option 4 confirmed) -- tests distillation viability for 22M student

Both await user authorization. CELL-5 also needs user-provided Together API key.

## Recommended idle-time priority while standing for user

Per my earlier idle-priority note:

**FAISS env Windows OpenMP fix [HIGHEST IDLE-TIME LEVERAGE]:**
- Outstanding since early today
- Gates HP-12 V2 (CELL-4) at 100K facts
- Pure infra; $0 cost
- Try conda faiss-cpu first; fall back to clean venv

This is the most valuable thing you could do during the hold.

## Updated standing items (cloud)

Pending user auth:
- CELL-2 Wikipedia extraction at 1B BASE L=15 ($31-50; production substrate foundation)
- CELL-5 cascade distillation FD smoke ($28; awaits Together API key from user)

Standing items (informational):
- HP-12 V1 5-min screen recording (user manual task)
- FAISS env Windows OpenMP fix (idle-time priority for you)

Closed today:
- CELL-1 fp16 70B (DONE; ARCHITECTURAL_CONFIRMED)
- 70B-Instruct follow-up (DONE; ARCHITECTURE_ROBUST + Instruct-destroys-mid-depth surprise)

## Hardening continues to land

GH200 + aarch64 + cu128 path proven SECOND time today. Smart launcher dual-SKU polling worked. 25 known bug defenses all held. This infrastructure is now a durable asset for future Phase 4a work where >40 GB VRAM is needed.

## Bonus reading

The "Instruct destroys mid-depth" finding is worth documenting as an interesting fact about Llama-3.1-70B's information geometry. May affect downstream architecture decisions when distillation pipeline is built (PHASE4A-2). Worth flagging if anyone asks "why didn't we use Instruct as teacher" later.

---

**END.**

**Testbed:** HOLD for user CELL-2 / CELL-5 auth. Recommend FAISS env fix as idle-time priority. 70B-Instruct done was clean execution + surprising-but-informative result.

**User:** Cloud queue empty. CELL-2 ($31-50; Wikipedia substrate foundation) and CELL-5 ($28; needs Together API key) await your authorization. Either authorize one/both now or hold for tomorrow. 70B-Instruct cloud done at $0.69; LOCKED "Use Base not Instruct" decision. Total cloud spend today: $3.97 for the full Llama-3.1-70B architectural story.

**Exp-Dev:** All Phase 4 cells now lock to BASE Llama variants. Layer convention final: 1B base L=15; 8B base L=29; 70B base L=50.
