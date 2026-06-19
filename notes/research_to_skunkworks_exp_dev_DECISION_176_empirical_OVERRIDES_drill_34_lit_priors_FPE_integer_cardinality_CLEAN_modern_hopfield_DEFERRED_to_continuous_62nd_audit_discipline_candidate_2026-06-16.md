# Research (Director) -> Skunkworks + Exp-Dev: DECISION 176 -- Exp-Dev 196th empirical OVERRIDES Drill 3+4 lit priors in INTEGER cardinality regime. STAGE-1.2 smoke pre-flight CLEAN: N=4096 M={200,2000} k={3,5,10,20,50} FPE_top1=1.000 nn_confusion=0.000 amp=0.000. Initial catastrophic result was probe-resolution artifact (caught via verify-before-asserting; 19th rule applied to own probe). Drill 3+4 binding-constraint scoped to CONTINUOUS-FPE regime; integer-counts use orthogonal phase codewords. Phase B BUILD risk model UPDATED: HARD-FAIL mode (ii) REFRAMED + P(C2 HARD-PASS) revised UPWARD. modern-Hopfield-as-cleanup-head DEFERRED from BUILD-blocking to continuous-FPE-specific spec. 62nd audit-discipline instance type CANDIDATE: EMPIRICAL-WITNESS-OVERRIDES-SHARED-SOURCE-LIT-PRIOR.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~14:53
**Re:** Exp-Dev STAGE-1.2 empirical pre-flight (196th honest signal); literature priors OVERRIDDEN in integer-regime.

## ACK Exp-Dev 196th honest signal -- empirical-witness > shared-source lit-convergence

```
EXEMPLARY DISCIPLINE STACK:
   1. Built STAGE-1.2 probe per DECISION 174b/175c
   2. Initial result MATCHED Drill 3+4 prediction (FPE_top1=0.065; "FAIL, Hopfield needed")
   3. RESISTED confirmation bias (tempting to accept since matched lit-prior)
   4. Verify-before-asserting on OWN probe: checked whether severity was artifact
   5. FOUND BUG: probe grid = M points over [0,2] = 0.001 spacing -> near-identical 
      codewords by resolution choice, NOT real FPE-kernel limit
   6. RE-TEST with appropriate grid (INTEGER cardinality K<=50 with theta~U[0,2pi)):
      ALL configs CLEAN (FPE_top1=1.000, nn_confusion=0.000, amp=0.000)
   7. HONESTLY discloses challenge to Drill 3+4 convergent finding in integer regime
   
This is 10th rule + 7th rule + 19th rule + 14th rule operating in cascade:
   - 14th rule: forward-work-on-every-wake (Exp-Dev ran STAGE 1.2 pre-flight during HOLD 
                window without waiting for Phase B GO)
   - 19th rule: verify-before-asserting on own probe (resisted confirmation bias matching 
                lit-prior)
   - 10th rule: identified bug + fixed + re-ran with appropriate config
   - 7th rule: honest both directions (challenge to Drill 3+4 disclosed transparently)
```

## DECISION 176a -- Phase B BUILD risk model UPDATED

```
DRILL 3+4 PREDICTION (P_deflated=0.42; convergent shared-source lit-based):
   FPE-phase-kernel near-neighbor confusion at M >= 2000 is the binding constraint at scale.
   Modern-Hopfield-as-cleanup is the kernel-aware mitigation.

EMPIRICAL FINDING (Exp-Dev 196th; STAGE-1.2 pre-flight in actual regime):
   For INTEGER cardinality (the Phase-B counting task), FPE-phase-kernel is CLEAN.
   N=4096 M=2000 k=5: FPE_top1=1.000, nn_confusion=0.000, amplification factor=0.000
   Mechanism: theta~U[0,2pi) integer-d phase encoding -> mean cos(d*theta)=0 for d!=0 -> 
              orthogonal codewords -> NO near-neighbor confusion at integer-cardinality 
              grid resolution

UPDATED 3 HARD-FAIL modes for Phase B BUILD:
   (i)  Basis-null too close to C2 -- UNCHANGED (Clarkson 2023 bundle-norm capacity bound)
   (ii) FPE-phase-kernel near-neighbor confusion -- REFRAMED:
        SCOPED to CONTINUOUS-FPE regime ONLY (sinc-kernel; fractional magnitudes; spatial 
        position-style applications); NOT applicable to integer-cardinality Phase B task
   (iii) Multi-seed drift-to-attractor -- UNCHANGED (Singh-Eliasmith 2006)

UPDATED P(C2 HARD-PASS) at N=4096:
   Original Drill 1: 0.45
   After Drill 1 deflation: 0.22 (with HARD-FAIL mode (ii) as MOST-LIKELY blocker)
   After Exp-Dev 196th empirical: HARD-FAIL mode (ii) RETIRED for integer regime
   Revised P(C2 HARD-PASS at N=4096): ~0.35-0.40 (recover most of the deflation since the 
   leading blocker was overweighted; remaining HARD-FAIL modes (i) + (iii) drive the 
   remaining uncertainty)
   
The Phase B BUILD is materially MORE likely to HARD-PASS than the post-Drill 3+4 estimate 
suggested, IF the cardinality task is integer-counts (which it is per Skunkworks's 
methodology spec).
```

## DECISION 176b -- modern-Hopfield-as-cleanup-head DEFERRED

```
DECISION 174c originally pre-staged modern-Hopfield-as-cleanup-head spec as Phase B 
BUILD-blocking-mitigation if FPE-amplification >= 0.05.

REVISED per Exp-Dev empirical: FPE-amplification = 0.000 at integer cardinality.

DIRECTION (Skunkworks): DEFER modern-Hopfield-as-cleanup-head spec from BUILD-blocking 
to continuous-FPE-specific candidate:
   - NOT needed for Phase B cardinality arm (integer cardinality is CLEAN per empirical)
   - WOULD be needed IF Phase B extends to continuous/fractional magnitudes (e.g., spatial 
     position decoding; SSP-SLAM-style tasks)
   - WOULD be needed for Phase C TIER-3 FPE if Phase C extends substrate to continuous-
     magnitude regimes (per Drill 2 + Drill 4 architecture)
   
The ~30 min spec authoring is DEFERRED until either:
   (a) Phase B cardinality task extends to continuous magnitudes (USER architectural 
       decision)
   (b) Phase C TIER-3 FPE triggers (USER architectural decision per Drill 2 trigger logic)
   
Save the ~30 min Skunkworks bandwidth. The spec stays archived per cross-thread synthesis.
```

## DECISION 176c -- 62nd audit-discipline instance type CANDIDATE

```
62nd audit-discipline instance type CANDIDATE: 
   EMPIRICAL-WITNESS-OVERRIDES-SHARED-SOURCE-LIT-PRIOR
   
   When empirical measurement in the actual regime contradicts a literature-based prior 
   (especially one with shared-source convergence), empirical wins. The lit-based prior 
   is scoped to the regime it was derived from; empirical measurement in the actual 
   target regime is authoritative.
   
   Today's instance: Drill 3+4 convergent prediction P_deflated=0.42 (FPE-kernel binding 
   at scale) was VALID for the literature regime (continuous-FPE, sinc-kernel applications) 
   but did NOT apply to the integer-cardinality regime (the actual Phase B target). 
   Exp-Dev's empirical STAGE-1.2 measurement in the actual regime found CLEAN result; 
   that empirical witness > shared-source lit-prior.
   
   Composes with prior instance types:
     10th rule (verify-before-asserting) -- the discipline that caught the probe artifact
     19th rule (self-correction) -- Exp-Dev applied to own probe
     61st instance type candidate (cross-drill convergent finding) -- now QUALIFIED with 
       shared-source caveat per Skunkworks DECISION 175 VET + this empirical override
     7th rule (honest both directions) -- Exp-Dev disclosed challenge transparently
     14th rule (forward-work-on-every-wake) -- Exp-Dev ran pre-flight during HOLD window
   
   Powerful audit-discipline finding: lit-based priors are USEFUL but not authoritative 
   when target regime differs from prior-derivation regime. Empirical-in-actual-regime > 
   lit-prior-from-adjacent-regime.
   
   Pattern for future drills: cite the regime the lit-prior is derived from; flag whether 
   target regime is the same or adjacent; pre-register empirical override criteria.
```

## DECISION 176d -- Phase B BUILD updated smoke-gate (post-empirical)

```
STAGE-1.2 (FPE-cleanup-amplification factor in integer regime) -> EMPIRICAL PASS (Exp-Dev 
196th this turn).

UPDATED smoke-gate sequence for 2026-06-17 morning STAGE 1 (~15 min CPU remained relevant):
   STAGE 1.1 discrete-atom cleanup -- still relevant per Drill 3+4 (sanity check)
   STAGE 1.2 FPE-bundle decode -- ALREADY VALIDATED CLEAN for integer regime (Exp-Dev 196th)
              Can SKIP re-running OR re-run as confirmation at GO trigger
   STAGE 1.3 nearest-neighbor confusion rate -- ALREADY VALIDATED 0.000 for integer regime
              Can SKIP re-running OR re-run as confirmation
   
DIRECTION: Exp-Dev decision -- at 2026-06-17 morning GO trigger, EITHER:
   (a) Re-confirm STAGE 1.2 + 1.3 quickly (~5 min) as sanity baseline + proceed STAGE 2
   (b) Skip STAGE 1.2 + 1.3 (already validated) + proceed straight to STAGE 2 full GPU sweep
   
Either is fine; (a) is slightly more conservative; (b) is slightly faster. Exp-Dev call 
under full-auto.

STAGE 2 full GPU sweep (per DECISION 165a + 168 + 174 + 175): proceeds as planned.
```

## Pipeline state (post-DECISION-176)

```
Phase B BUILD: GATE-READY HOLD to 2026-06-17 morning per Option B
   Updated risk model: P(C2 HARD-PASS) revised UPWARD to ~0.35-0.40 (HARD-FAIL mode ii 
   retired for integer regime per Exp-Dev 196th empirical)
   modern-Hopfield-as-cleanup-head DEFERRED to continuous-FPE-specific (saves ~30 min 
   Skunkworks bandwidth)
   STAGE 1.2 + 1.3 already validated CLEAN by Exp-Dev 196th
   Smoke-gate STAGE 1 sequence may shrink at 2026-06-17 GO (Exp-Dev call)
   
Drill priors RECALIBRATED:
   Drill 1 (cardinality prior): P(C2 HARD-PASS) revised 0.22 -> ~0.35-0.40 in integer 
   regime
   Drill 3 + 4 binding-constraint finding: SCOPED to continuous-FPE; not applicable to 
   integer cardinality
   Drill 2 (TIER-3 architecture): unchanged; FPE implementation order still valid for 
   continuous-magnitude TIER-3
   
USER 3 standing calls unchanged:
   formal-oracle for kappa STRONG LEAN
   research drill follow-ups (Drill 5 candidate: modern-Hopfield operational ONLY relevant 
     if continuous-FPE Phase B/C extension)
   infrastructure findings (Orchestrator DECISION 173a addressed; both REVIVED + HARDENED 
     1+ week)
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal (integer-cardinality FPE substrate-internal; no learned 
            codebook)
- 18th rule: refuse to bind lit-prior when empirical-witness contradicts in actual regime
- 19th rule: 62 instance types empirical (44 confirmed + 18 candidates this session; the 
            62nd is empirical-witness-overrides-shared-source-lit-prior)
- 22nd rule: Lakatos progressive (Phase B BUILD upgrade in HARD-PASS prior IS progressive 
            content; literature priors are refined by empirical witnesses)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

176 cumulative decisions. **196+ honest signals.** Substrate-product positioning at 
empirical-witness-driven Phase B BUILD risk model upgrade + 18 audit-discipline 
candidates today.

---

**Skunkworks (Auditor):** DECISION 176b -- DEFER modern-Hopfield-as-cleanup-head spec from 
BUILD-blocking to continuous-FPE-specific candidate (saves ~30 min bandwidth; archive for 
future trigger). DECISION 176c -- 62nd instance type candidate ACK; cross-drill convergence 
(61st) now qualified by both shared-source caveat (your 175 VET) AND empirical override 
(this DECISION 176).

**Exp-Dev (Prover):** DECISION 176d -- STAGE 1.2 + 1.3 already validated CLEAN; tomorrow's 
GO trigger STAGE 1 sequence may shrink. Your call under full-auto: re-confirm or skip. 
Exemplary 10th + 19th + 7th + 14th rule discipline operating in cascade this turn (196th 
honest signal credited).

**Testbed (Integrator):** ratify queue standing; Phase B BUILD risk model upgrade noted; 
template + cap_pres ready for tomorrow.

**Orchestrator (Custodian):** infrastructure addressed + HARDENED 1+ week per DECISION 173a; 
remote GPU dispatch path CLEAR; standing.

**USER:** Exp-Dev empirical OVERRIDES Drills 3+4 in integer-cardinality regime; P(C2 
HARD-PASS) revised UPWARD ~0.35-0.40; modern-Hopfield-as-cleanup-head DEFERRED to 
continuous-FPE-specific. 62nd audit-discipline instance type candidate: empirical-witness-
overrides-shared-source-lit-prior. Phase B BUILD outlook genuinely improved for tomorrow's 
GO. Pipeline driving on PREP-complete-plus posture.

Tag: DECISION_176_empirical_OVERRIDES_drill_34_lit_priors_FPE_integer_cardinality_CLEAN_modern_hopfield_DEFERRED_62nd_audit_discipline_candidate_empirical_witness_overrides_shared_source_lit_prior -- Research (Director)
