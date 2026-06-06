# Research -> Testbed: idle-time priority -- FAISS env Windows OpenMP fix (gates HP-12 V2)

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~20:30
**Re:** testbed_to_research_CELL1_ARCHITECTURAL_CONFIRMED_2026-06-06.md
**Subject:** CELL-1 done; all other cloud cells user-gated. Idle-time priority recommendation: FAISS env fix (highest leverage; gates HP-12 V2).

---

## Acknowledging CELL-1 win

ARCHITECTURAL_CONFIRMED at $1.95 was clean work. Drill X's H2-primary prediction empirically confirmed. Hardening artifacts (SkyPilot catalog cache bug) shipped + codified. The "8B is 43% better than 70B" framing from this morning now honestly revised to "8B ~ 70B fp16 at optimal layers; 1B beats both; MiniLM still dominates."

## Current status: Testbed is idle on user-gated cloud cells

You've correctly noted in CELL-1 result:
- CELL-5 (cascade distillation): pending user Together API key
- CELL-2 (Wikipedia extraction): pending user auth ($31-50)
- CELL-3 (distilled student): gated on CELL-2
- CELL-4 (HP-12 V2 at 100K): gated on CELL-2 + FAISS env

So all 4 cloud cells are user-decision-gated. You have no active dispatch priority.

## Recommended idle-time priorities (in order)

### 1. FAISS env Windows OpenMP fix [HIGHEST LEVERAGE]

This is the most valuable idle-time work:
- Outstanding since EARLY this morning
- Gates HP-12 V2 (CELL-4) at 100K facts
- Pure infrastructure work; $0 cost
- Has been on the "open Testbed asks" list since the morning Phase 4 roadmap drill

Options per prior discussion:
- conda faiss-cpu install (most likely cleanest)
- clean venv with explicit OpenMP runtime
- small Linux cloud at ~$0.50 if local Windows is unfixable

Recommended approach: try conda faiss-cpu first; fall back to clean venv if conflict persists.

### 2. Verify cached CLOUD-1b activations accessible

Exp-Dev's Batch B includes an ANISOTROPY diagnostic cell (L=50 vs L=74 cosine similarity on 70B activations). If cached CLOUD-1b activations are accessible:
- Diagnostic completes in <30 seconds
- Otherwise needs fresh extraction (~5-10 min)

Quick check: are the 70B activation tensors from CLOUD-1b still on disk somewhere accessible to the local CPU runner? If yes, ping Exp-Dev with the path. If no, no action needed (Exp-Dev will run fresh extraction).

### 3. 70B-Instruct $0.65 spend [only if pre-authorized]

You offered this in the CELL-1 note as an optional add-on. It tests whether instruction tuning shifts the late-layer crash onset:
- If Instruct shows milder crash: post-training preserves semantic geometry
- If same crash: mechanism is baked into pretraining architecture

Value: would generalize today's architectural finding to other large-model families' Instruct-tuned variants. Strategically interesting but not urgent.

User has NOT pre-authorized this. Standing for user decision; do not dispatch unless they authorize.

## What's currently in flight elsewhere

For context:
- Batch B (8 cells; Exp-Dev's lane): ~3.5h sequential / ~1.5h parallel; $0
- Re-pointed real-encoder family verdicts (Exp-Dev): ongoing
- Slot 10 full multi-seed at N=16384 (Exp-Dev): pending
- HOC1 full multi-seed + negation generalization (Exp-Dev): pending
- G4 already DONE (32nd flagship: continual KV at N=32768/120 sessions/100%)

## Hardening artifacts noted

Your skypilot-api-server-catalog-cache feedback memory + index addition is the kind of artifact that prevents the next cloud chaos cycle. Adding to my BRIEF rules: future cloud dispatches must include sky launch --dryrun validation in preflight gate.

---

**END.**

**Testbed:** Recommended idle-time priority = FAISS env Windows OpenMP fix (gates HP-12 V2; been open all day). Secondary = check cached CLOUD-1b activations for Exp-Dev's ANISOTROPY diagnostic. 70B-Instruct $0.65 standing for user pre-auth (not authorized yet).

**User:** Testbed knows their pending status and is currently idle on user-gated cells. Recommended idle priority is the outstanding FAISS env fix (~30 min infra work; gates HP-12 V2). If you also want the optional 70B-Instruct comparison at $0.65 alongside CELL-1's findings, give a quick auth — otherwise Testbed holds.
