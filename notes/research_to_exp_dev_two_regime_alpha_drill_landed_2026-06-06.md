# Research -> Exp-Dev: 2x alpha drill landed -- 3 high-priority cells (cubic-tensor is Tier-1 blocker)

**From:** Research session
**To:** Exp-Dev (primary; queue drain owner with bulk re-queue active)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-06 ~07:25
**Re:** Two-regime alpha 2x drill from cycle 116 MIDDLE_BAND LVH catch #224
**Subject:** alpha=0.040 asymptote confirmed via 1-RSB transition + finite-size kurtosis correction. Phase 3 n=2 revised to 20,971 facts. CUBIC-TENSOR n=3 PREFACTOR C_3 IS UNVERIFIED -- blocks Wikipedia-class capacity claim. 3 cells routed per handoff.

---

## Drill verdict (synthesized)

**alpha=0.040 asymptote is REAL.** Two algebraic mechanisms jointly explain the small-N (0.060) vs large-N (0.040) drop:
1. Finite-size kurtosis correction (vanishes at large N)
2. 1-RSB transition at alpha~0.051 (Parisi replica-symmetry-breaking; spin-glass theory)

Further drift below 0.040 at N=65536 is UNLIKELY -- the asymptote is the actual production-scale value.

**Phase 3 n=2 LINEAR capacity formal revision:** D=8 x 0.040 x 65536 = **20,971 facts** (used for working memory + audit; -17% from original)

**CRITICAL UNKNOWN surfaced by drill:** n=3 cubic-tensor prefactor C_3. The Phase 3 Wikipedia-class capacity claim (~10^9 facts) depends on C_3 * N^2 scaling. C_3 has never been empirically measured for this substrate.

P_deflated: 0.50 (N=32768 smoke HP); 0.30 (sparse-write rescue HP).

---

## Three cells per handoff (rank-ordered)

The handoff file at `notes/exp_dev_handoff_research_two_regime_alpha_2026-06-06.md` has full per-anchor details. Quick summary:

### Cell 1: `n3_cubic_tensor_capacity_n4096_v1` (TIER-1 BLOCKER)
- **The Phase 3 Wikipedia-class capacity claim depends on this.**
- Architecture: sparse cubic tensor write (n=3) at N=4096
- Goal: measure prefactor C_3 in M_max = C_3 * N^2
- Wall: moderate (~1-2 days engineering for sparse cubic tensor + smoke)
- **Strategic value:** without this, the "facts explosion" claim at Phase 3 is algebra-only

### Cell 2: `capacity_sweep_n32768_asymptotic_alpha_v1` (TIER-1 gate)
- Cheap decisive test: sweep capacity at N=32768
- Wall: <5 min CPU
- Confirms alpha=0.040 holds at N=32768 (last data point before N=65536 commitment)
- HARD-PASS: alpha in [0.036, 0.044] at N=32768
- HARD-FAIL: alpha drifts below 0.036 (asymptote uncertain; Phase 3 needs further revision)

### Cell 3: `sparse_vs_dense_write_regime_alpha_n4096_n16384_v1` (TIER-2 rescue)
- Test sparse write rule effect on large-N capacity
- Wall: <15 min CPU
- HARD-PASS: sparse write recovers alpha~0.055+ at large N (major rescue path)
- HARD-FAIL: sparse write does NOT change regime (alpha=0.040 is intrinsic)

---

## Why this matters strategically

The user surfaced an important question just before this drill landed: "have we moved to Phase 3 yet? doesn't that explode the number of facts storable?"

Honest answer: we have NOT moved to Phase 3; we are partly into Phase 4a infrastructure. The "facts explosion" claim at Phase 3 depends entirely on:
- n=3 cubic-tensor O(N^2) capacity (UNVERIFIED)
- D=8 parallel composition with VQ routing (UNBUILT)
- Sparse cubic tensor at N=65536 fits in memory (UNVALIDATED)

**Cell 1 above is the single highest-leverage new cell to add to the bulk-re-queue.** Without it, the entire Phase 3 capacity story is algebra-only.

---

## Coordination with user's "queue up a LOT more" directive

You're doing both: (a) bulk re-queue validated cells for second samples, (b) build genuine new cells each tick. Adding Cell 1 (cubic-tensor n=3) is exactly the kind of high-leverage NEW cell that earns its queue slot vs another re-run.

Recommend: queue Cell 2 (N=32768 sweep; cheap) NOW; queue Cell 3 (sparse-write rescue) overnight; build Cell 1 (cubic-tensor) as the multi-day engineering project starting today.

---

## What this does NOT change

The 23 flagship anchors from overnight stand:
- KF-1 hallucination detection (AUC 0.999)
- Real-encoder capabilities (1.000 with both encoders)
- Continual KV injection (3,600 facts, zero contradictions)

These were validated independent of the alpha revision. The continual KV injection HP at 3,600 facts in N=8192 is particularly interesting -- alpha=0.040 would have predicted ~328 facts as classical Hopfield bound. KV-injection mechanism appears to operate in a different regime where the alpha penalty doesn't directly apply (11x over classical Hopfield bound). This is worth a follow-on drill if HP-12 V2 build doesn't surface the answer first.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-experiment-design-in-prompts]]: 3 anchors with WHY + TIER + WALL only; no sweep grids, threshold formulas pre-committed
- Per [[feedback-negative-results-2x-research]]: 2x rescue drill landed for capacity MIDDLE
- Per user 2026-06-06 ~07:20: bulk-re-queue active; new cells should be high-leverage
- ASCII-only

---

**END.**

**Exp-Dev:** 3 cells routed via handoff. Cell 1 (n=3 cubic-tensor) is Tier-1 BLOCKER for Phase 3 Wikipedia claim; Cell 2 (N=32768 sweep) is Tier-1 decision gate. Cell 3 (sparse-write rescue) is Tier-2. Recommend queue order: Cell 2 NOW (5 min cheap), Cell 3 overnight (15 min), Cell 1 multi-day engineering project starting today. Bulk re-queue for second samples on validated cells is the right call.

**Testbed:** No new asks beyond standing items (FAISS env fix, optional Llama weights).

**User:** Drill landed with sharp algebraic answer. Alpha=0.040 asymptote IS real (1-RSB transition + finite-size kurtosis explain the regime drop). Phase 3 n=2 revised to 20,971 facts (-17%). **The critical missing test is n=3 cubic-tensor empirical** -- without it, "facts explosion" at Phase 3 is algebra-only. Routed as Cell 1 (Tier-1 BLOCKER). Per your earlier question, this directly addresses your facts-storable concern.
