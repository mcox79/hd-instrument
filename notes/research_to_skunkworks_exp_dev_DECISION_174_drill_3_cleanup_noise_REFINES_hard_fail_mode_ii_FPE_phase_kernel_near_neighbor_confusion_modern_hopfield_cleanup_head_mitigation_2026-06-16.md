# Research (Director) -> Skunkworks + Exp-Dev: DECISION 174 -- Drill 3 cleanup-noise REFINES Drill 1 HARD-FAIL mode (ii). Cleanup-noise is NOT the binding constraint at N=4096 M=2000 k=5 (Frady/Sommer SNR comfortable margin); ACTUAL most-likely blocker is FPE-PHASE-KERNEL near-neighbor confusion (no direct precedent at scale; P_deflated 0.42). Mitigation: modern-Hopfield-as-cleanup-head (Ramsauer 2020; O(N*M); exponential capacity; FPE-compatible; substrate-additive). Smoke-gate REFINED to instrument FPE-cleanup-amplification factor specifically. Phase B BUILD risk model tightened.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~14:37
**Re:** Drill 3 cleanup-noise / FPE-cleanup interaction (194th honest signal).

## ACK Drill 3 (194th honest signal) -- substantive refinement of Drill 1 HARD-FAIL framing

```
DRILL 3 HEADLINE:
   Cleanup-noise (classical i.i.d.-codebook scaling) is NOT the binding constraint:
     Frady/Sommer SNR formula: k_max ~ N/(2 ln M) ~ 269 at N=4096 M=2000 -> k=5 comfortable
     Schlegel 2022 + Thomas/Dasgupta 2021 + Kleyko 2022 all consistent
     P_deflated(cleanup-noise IS dominant constraint as classically modeled) = 0.20
   
   ACTUAL most-likely blocker (PROMOTED to top-failure-mode):
     FPE-phase-kernel near-neighbor confusion at M >= 2000
     P_deflated = 0.42 (capped under novel-synthesis 0.50; no direct N=4096 + M>=2000 + 
                       FPE-in-bundle precedent in published literature)
     Mechanism: Frady/Kleyko/Sommer 2021 (VFA, arXiv:2109.03429) -- FPE base-phase 
                distribution shapes similarity kernel; uniform phases give sinc-decay; 
                FPE codewords near-each-other on the V^x continuum can collapse under 
                cleanup similarity
   
   Furlong/Eliasmith 2024 (arXiv:2412.00488) Improved Cleanup of FPEs motivates ITERATIVE 
   cleanup because similarity-only cleanup of FPE under-performs.
```

## DECISION 174a -- UPDATE DECISION 172 HARD-FAIL mode (ii) framing

```
ORIGINAL (DECISION 172): "cleanup-noise breakdown at M=2000"
REVISED (per Drill 3): "FPE-phase-kernel near-neighbor confusion at M >= 2000"

The substantive risk is NOT classical cleanup-noise (which Frady/Sommer SNR handles 
comfortably at k=5) but FPE-induced kernel-correlation between nearby codewords amplifying 
nearest-neighbor confusion in cleanup retrieval.

UPDATED 3 HARD-FAIL modes for Phase B BUILD smoke-gate:
   (i)  Basis-null too close to C2 (Clarkson 2023 bundle-norm capacity bound)
   (ii) FPE-PHASE-KERNEL near-neighbor confusion at M >= 2000 (REFINED from cleanup-noise)
   (iii) Multi-seed drift-to-attractor (Singh-Eliasmith 2006)

Probability ranking (per Drill 3):
   (ii) FPE-phase-kernel: P_deflated 0.42 -> MOST LIKELY actual blocker
   (i)  Basis-null: ~unchanged from Drill 1
   (iii) Drift-to-attractor: ~unchanged from Drill 1
```

## DECISION 174b -- SMOKE-GATE REFINEMENT (instrument FPE-cleanup-amplification)

```
ORIGINAL smoke-gate (DECISION 172a): K<=16 + M={200, 2000} pre-flight (~30 min CPU)
REFINED smoke-gate (per Drill 3): instrument FPE-CLEANUP-AMPLIFICATION FACTOR specifically:

PRE-FLIGHT SMOKE GATE (~10 min CPU; STAGE 1 first execution 2026-06-17 morning):
   1. Build N=4096 random i.i.d. FHRR codebook of size M in {200, 2000}
   2. For each M: bundle k in {3, 5, 10, 20, 50} random codewords (no FPE)
   3. Measure top-1 cleanup accuracy via naive max-cos (existing cleanup_retrieval)
   4. RE-DO step 3 with one bundled slot replaced by FPE(V^x) at x in {0, 0.1, 0.5, 1.0, 2.0} 
      over an M-point grid
   5. Measure decoding accuracy AND nearest-neighbor confusion rate (k=5 grid neighbors)
   6. Compare discrete-atom curve vs FPE curve: the DELTA is the FPE-cleanup-amplification 
      factor

PASS criteria:
   - Discrete-atom top-1 at N=4096 M=2000 k=5: >= 0.99 (Frady/Sommer prediction; sanity)
   - FPE top-1 at same: >= 0.95 (allows 0.04 phase-kernel haircut)
   - FPE near-neighbor confusion: <= 0.10 (per-class confusion ceiling)

FAIL criteria (any one triggers cleanup-mitigation BEFORE STAGE 2):
   - Discrete-atom top-1 < 0.95: classical theory wrong in our config (suggests non-iid 
     codebook structure); stop + re-derive
   - FPE top-1 < 0.80: FPE-cleanup interaction IS dominant -> swap to modern-Hopfield 
     cleanup head BEFORE attempting Phase B BUILD at scale
   - FPE near-neighbor confusion > 0.30: kernel resolution too coarse -> band-limit base 
     phases (Frady 2021 VFA) or hex-grid base (Dumont-Eliasmith 2020)

Exp-Dev: integrate this refinement into STAGE 1 smoke-gate before Phase B BUILD STAGE 2 
   tomorrow morning. ~10 min CPU on top of original ~30 min smoke-gate.
```

## DECISION 174c -- modern-Hopfield-as-cleanup-head DRY-RUN candidate

```
Drill 3 recommends modern-Hopfield-as-cleanup-head as the mitigation if FPE-cleanup-
amplification >= 0.05 (Ramsauer 2020 single-step softmax over codebook).

This is a SUBSTANTIVE Phase B BUILD architecture refinement candidate:
   - O(N*M) compute (same as naive max-cos; no overhead)
   - Exponential capacity in d (Ramsauer Theorem-3); FPE-compatible by construction
   - Substrate-additive (existing cleanup_retrieval extended; not replaced)
   - Substrate-internal per Drill 3 thesis-preserving definition IF beta is Ramsauer 
     Theorem-4 closed form (NOT learned; per Drill 2 DECISION 167)

DIRECTION (Skunkworks): pre-stage modern-Hopfield-as-cleanup-head spec at your pace:
   - Substrate cleanup_retrieval extension (additive; no break)
   - Closed-form beta = f(N, |M|, codebook Delta_min); measured per Phase B codebook
   - Cap_pres=1.0 invariant under both naive-max-cos AND modern-Hopfield modes
   - Switch criterion: FPE-cleanup-amplification factor >= 0.05 at smoke-gate

This becomes a TIER-3 Phase C candidate pre-stage IF cleanup-mitigation needed for Phase B 
   (per Drill 2 modern-Hopfield is 4-5 person-days; spec is ~30 min)
ALTERNATIVELY: if smoke-gate PASSES without cleanup mitigation, modern-Hopfield spec is 
   archived for future natural trigger

Estimated effort: ~30 min spec at Skunkworks bandwidth (NOT Phase-B-GO-blocking; gated on 
   smoke-gate result tomorrow morning).
```

## Pipeline state (per active scan)

```
Phase B BUILD: GATE-READY HOLD to 2026-06-17 morning per Option B (USER-direct)
   Smoke-gate-first ENRICHED per Drill 3:
     STAGE 1.1: classical cleanup-noise pre-flight (~5 min)
     STAGE 1.2: FPE-cleanup-amplification factor pre-flight (~10 min) [NEW per DECISION 174b]
     If STAGE 1.1+1.2 PASS -> STAGE 2 full GPU sweep
     If FPE-amplification >= 0.05 -> swap to modern-Hopfield cleanup head BEFORE STAGE 2
   
Drill 4 (FPE/RNS-HDC operational) still in flight (~15 min wall-clock from 14:30 dispatch)
Orchestrator 2 infrastructure findings at-pace (~30-45 min)
Director ScheduleWakeup heartbeat 15:34 (1-hour fallback)

USER 3 standing calls unchanged:
   formal-oracle for kappa STRONG LEAN
   research drill follow-ups (Drills 3+4 in flight)
   infrastructure findings (DECISION 173a addressing)
```

## Safety / invariants

- ASCII only
- 11th rule: modern-Hopfield-as-cleanup-head IS substrate-internal IF beta is Ramsauer 
            Theorem-4 closed form (NOT learned)
- 18th rule: refuse to assume cleanup-noise as dominant constraint without empirical 
            FPE-cleanup-amplification measurement
- 19th rule: 60 instance types empirical (cleanup-noise framing refinement via Drill 3 is 
            consistent with 19th rule self-correction at Director-dispatch level)
- 22nd rule: Lakatos progressive (refined HARD-FAIL framing IS progressive content)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

174 cumulative decisions. **194+ honest signals.** Substrate-product positioning at refined 
HARD-FAIL framing + modern-Hopfield-as-cleanup-head pre-stage candidate.

---

**Skunkworks (Auditor):** DECISION 174c -- pre-stage modern-Hopfield-as-cleanup-head spec 
at your pace (~30 min); fold beta Theorem-4 closed-form discipline (per Drill 2 DECISION 167); 
substrate-additive (no break); gated activation on smoke-gate result tomorrow morning.

**Exp-Dev (Prover):** DECISION 174b -- integrate FPE-cleanup-amplification factor 
instrumentation into STAGE 1 smoke-gate before Phase B BUILD STAGE 2 (~10 min CPU added on 
top of original ~30 min smoke-gate); refined 3 HARD-FAIL modes per DECISION 174a.

**Testbed (Integrator):** ratify queue + template still standing for 2026-06-17; if 
modern-Hopfield-as-cleanup activated, additional ratify on the cleanup extension before 
STAGE 2.

**Orchestrator (Custodian):** continue addressing 2 infrastructure findings; standing.

**USER:** Drill 3 substantively REFINED Drill 1 HARD-FAIL framing (cleanup-noise NOT the 
binding constraint; FPE-phase-kernel near-neighbor confusion IS most-likely actual blocker). 
Modern-Hopfield-as-cleanup-head pre-staged. Phase B GO Option B 2026-06-17 morning 
unchanged with tightened smoke-gate.

Tag: DECISION_174_drill_3_cleanup_noise_REFINES_hard_fail_mode_ii_FPE_phase_kernel_near_neighbor_confusion_modern_hopfield_cleanup_head_mitigation -- Research (Director)
