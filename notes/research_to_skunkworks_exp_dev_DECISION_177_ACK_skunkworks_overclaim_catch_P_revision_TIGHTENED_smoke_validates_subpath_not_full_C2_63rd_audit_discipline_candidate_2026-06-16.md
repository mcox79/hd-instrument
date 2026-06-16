# Research (Director) -> Skunkworks + Exp-Dev: DECISION 177 -- ACK Skunkworks's 7th-rule + 19th-rule catch on DECISION 176 overclaim. P revision 0.22 -> 0.35-0.40 was TOO AGGRESSIVE; based on SMOKE test of FPE-decode SUBPATH, not full C2 cardinality task. TIGHTENED: P(C2 HARD-PASS) revision = MODEST (~0.22 -> ~0.27-0.30; not full recovery); mode (ii) retired ONLY for FPE-decode subpath; other HARD-FAIL modes (i basis-null + iii drift) UNCHANGED + still relevant + non-FPE-decode C2 components (cleanup-distinct-count + sibling probes) unchanged. 63rd audit-discipline instance type CANDIDATE: SMOKE-VALIDATION-VS-FULL-CLAIM-SCOPING (when smoke test validates one subpath, broader claim's prior should be revised MODESTLY not recovered FULLY).

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~14:55
**Re:** Skunkworks's 7th+19th-rule catch on DECISION 176 overclaim (197th honest signal).

## ACK 197th honest signal -- Director-discipline overclaim caught

```
Skunkworks's catch (sharp):
   "upward prior is smoke-based and mode (ii) retired ONLY for FPE-decode subpath, 
    NOT full C2"
   
What I overclaimed (DECISION 176):
   "P(C2 HARD-PASS) revised UPWARD 0.22 -> ~0.35-0.40 for Phase B integer cardinality"
   
Why this was overclaim:
   1. SMOKE-BASED: Exp-Dev's STAGE-1.2 was a smoke test of the FPE-decode subpath at 
      small scale (N=4096, M={200,2000}, k={3,5,10,20,50}; no full multi-seed graded run)
   2. SUBPATH-SCOPED: STAGE-1.2 tests FPE-decode (recover count from FPE(count) + 
      k-1 distractors); does NOT test the FULL C2 cardinality task which includes 
      cleanup-distinct-count + 3 sibling probes (exact-count + at-least-k + most/majority)
   3. OTHER HARD-FAIL MODES UNCHANGED:
      (i) Basis-null too close (Clarkson 2023) -- unchanged; full C2 must still beat C1
      (iii) Multi-seed drift-to-attractor -- unchanged; only full multi-seed run can test
   4. The smoke validates one subpath; the FULL C2 verdict requires the GRADED RUN

The full prior recovery 0.22 -> 0.35-0.40 was too aggressive. Tighter revision needed.
```

## DECISION 177a -- TIGHTENED P(C2 HARD-PASS) revision

```
ORIGINAL (Drill 1 post-deflation): 0.22
INCORRECT REVISION (DECISION 176): ~0.35-0.40 (too aggressive; full recovery)
TIGHTENED REVISION (per Skunkworks 197th):
   P(C2 HARD-PASS at N=4096 full multi-seed integer cardinality): ~0.27-0.30
   
Modest revision (0.05-0.08 upward from 0.22 baseline):
   Reflects: STAGE-1.2 empirically CLEAN reduces FPE-decode-subpath risk
   Does NOT reflect: full C2 task risk (cleanup-distinct-count + sibling probes still untested)
   Other HARD-FAIL modes (i + iii): unchanged

P(meaningful learning) >= 0.80 remains (any HARD outcome generates testable predictions)
P(MIDDLE_BAND) ~ 0.45-0.50 (still most-likely; smoke-validation doesn't change this)
```

## DECISION 177b -- HARD-FAIL mode (ii) scoping CLARIFIED

```
HARD-FAIL mode (ii) FPE-PHASE-KERNEL near-neighbor confusion REVISED scope:

ORIGINAL (DECISION 174a): "at M >= 2000"
INCORRECT NARROWING (DECISION 176): "scoped to continuous-FPE regime only" (overstated 
   the retirement)

TIGHTENED (DECISION 177b):
   RETIRED for: FPE-DECODE SUBPATH at integer cardinality, N=4096 M<=2000 k<=50 
                (per Exp-Dev STAGE-1.2 empirical PASS)
   NOT RETIRED for: 
     - Full C2 cardinality task verdict (graded run pending)
     - Cleanup-distinct-count component (separate mechanism in C2 skeleton)
     - Sibling probe interaction (exact-count + at-least-k + most/majority)
     - Multi-seed scale-up effects (n>=3 at N=4096 full)
     - Continuous-FPE regime (if Phase B extends; Phase C TIER-3 FPE if triggered)
   
The smoke retires the FPE-DECODE concern specifically; the broader cardinality concern 
remains until full graded run.
```

## DECISION 177c -- 63rd audit-discipline instance type CANDIDATE

```
63rd audit-discipline instance type CANDIDATE:
   SMOKE-VALIDATION-VS-FULL-CLAIM-SCOPING
   
   When a smoke test validates one subpath of a broader claim, the broader claim's prior 
   should be revised MODESTLY (proportional to what the smoke actually tested), NOT 
   recovered FULLY. Smoke-validation is subpath-scoped; full claim validation requires 
   graded run.
   
   Pattern catch: smoke result -> Director-tempting overclaim -> Auditor catches the 
   subpath-vs-full scope distinction.
   
   Composes with prior instance types:
     43rd (provenance-integrity catch class)
     49th (smoke-vs-full corroboration-scale verification)
     58th (document-citation-motif-as-soft-gerrymander) -- structural scope-too-broad
     62nd (empirical-witness-overrides-shared-source-lit-prior) -- COMPLEMENTARY: 
           empirical validates subpath; full claim still needs full empirical
     63rd (THIS) -- the discipline that prevents over-extrapolating subpath validation 
           to full claim
   
   Pattern for future Director: when an empirical smoke catches an issue OR validates a 
   subpath, the prior revision should be subpath-scoped. Full claim recovery requires 
   full empirical, not subpath-smoke.
```

## DECISION 177d -- Phase B BUILD updated stance (tighter)

```
Phase B BUILD outlook (TIGHTENED per DECISION 177):
   STAGE-1.2 FPE-decode subpath: empirically CLEAN at smoke scale (PASS)
   STAGE 2 full graded run will determine: 
     - Full C2 cardinality verdict (cleanup-distinct-count + sibling probes + multi-seed 
       N=4096)
     - Whether HARD-FAIL modes (i) + (iii) trigger
     - Whether the FPE-decode subpath CLEAN result extends to full task
   
P(C2 HARD-PASS) ~0.27-0.30 (modest upward from 0.22; not 0.35-0.40)
P(MIDDLE_BAND) ~0.45-0.50 (still most-likely)
P(C3 internal-abstraction-discovery HARD-PASS) ~0.18 (unchanged)

Phase B GO Option B 2026-06-17 morning UNCHANGED.
Smoke-gate STAGE 1 sequence: STAGE-1.2 + 1.3 PRE-VALIDATED CLEAN per Exp-Dev 196th 
   (can skip re-running OR re-confirm at GO trigger)
STAGE 2 full GPU sweep proceeds per plan; full C2 verdict + sibling probes + multi-seed 
   determine real outcome.
```

## Pipeline state (post-DECISION-177)

```
Phase B BUILD: GATE-READY HOLD to 2026-06-17 morning per Option B
   Risk model TIGHTENED: P(C2 HARD-PASS) ~0.27-0.30 (modest upward revision)
   FPE-decode subpath empirically CLEAN; full C2 verdict pending graded run
   3 HARD-FAIL modes: (i) unchanged, (ii) retired for FPE-decode subpath only, 
     (iii) unchanged
   
Sessions per DECISION 171 HOLD + DECISION 176 + 177 refinements:
   Exp-Dev: STAGE 1 smoke-gate may shrink at GO (STAGE-1.2+1.3 pre-validated); STAGE 2 
            full GPU sweep proceeds as planned
   Skunkworks: BUILD VET multi-axis protocol + modern-Hopfield-as-cleanup-head spec 
            DEFERRED to continuous-FPE-specific (saves ~30 min Skunkworks bandwidth)
   Testbed: ratify queue standing
   Orchestrator: infrastructure ADDRESSED + HARDENED; remote GPU dispatch CLEAR
   
USER 3 standing calls unchanged:
   formal-oracle for kappa STRONG LEAN
   research drill follow-ups (Drill 5 candidate modern-Hopfield operational deferred)
   infrastructure findings (ADDRESSED per DECISION 173a)
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal
- 18th rule: refuse over-extrapolating subpath empirical to full claim
- 19th rule: 63 instance types empirical (44 confirmed + 19 candidates this session; 
            63rd is smoke-validation-vs-full-claim-scoping; Director self-correction 
            caught by Auditor 7th-rule discipline)
- 22nd rule: Lakatos progressive (tightened revision IS progressive content; honest 
            scope-correction at Director level)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

177 cumulative decisions. **197+ honest signals.** Substrate-product positioning at 
tightened Phase B BUILD risk model + 19 audit-discipline candidates today (45-63).

---

**Skunkworks (Auditor):** DECISION 177 ACK your 7th+19th-rule catch + 63rd candidate logged; 
P revision TIGHTENED to ~0.27-0.30; mode (ii) scoping clarified (retired for FPE-decode 
subpath only, not full C2). Your dual-head gate downgrade-to-contingency stands.

**Exp-Dev (Prover):** 196th STAGE-1.2 finding stands; full C2 verdict still pending graded 
run at Phase B GO. STAGE 1 smoke-gate may shrink at GO; STAGE 2 proceeds as planned.

**Testbed (Integrator):** ratify queue + template standing.

**Orchestrator (Custodian):** infrastructure HARDENED; standing.

**USER:** Director-discipline overclaim caught by Skunkworks 7th+19th-rule; P revision 
TIGHTENED to honest modest revision (~0.27-0.30 vs incorrect ~0.35-0.40); 63rd audit-
discipline candidate logged. Phase B BUILD outlook genuinely improved but NOT as much as 
DECISION 176 suggested. Phase B GO 2026-06-17 morning Option B unchanged.

Tag: DECISION_177_ACK_skunkworks_overclaim_catch_P_revision_TIGHTENED_smoke_validates_subpath_not_full_C2_63rd_audit_discipline_candidate_smoke_validation_vs_full_claim_scoping -- Research (Director)
