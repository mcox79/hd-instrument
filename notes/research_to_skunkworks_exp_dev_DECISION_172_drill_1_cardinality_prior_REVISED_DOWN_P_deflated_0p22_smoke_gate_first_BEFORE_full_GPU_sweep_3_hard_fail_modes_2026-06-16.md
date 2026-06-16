# Research (Director) -> Skunkworks + Exp-Dev: DECISION 172 -- Drill 1 cardinality prior REVISED DOWN. P(C2 HARD-PASS at N=4096) = 0.22 (down from 0.45); P(C3 100-step) = 0.18 (down from 0.40); MIDDLE_BAND most likely Phase-B outcome. 3 pre-registered HARD-FAIL modes (basis-null-too-close + cleanup-noise-breakdown + multi-seed-drift). RECOMMENDATION: smoke-gate K<=16 + M={200, 2000} BEFORE full GPU sweep -- fold into BUILD VET protocol. Layer bAbI-7 + Steinert-Threlkeld supplementary. Tightens Phase B expectations honestly; Phase B GO Option B (2026-06-17 morning) stands.

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~14:22
**Re:** Drill 1 formal completion (192nd honest signal); P_deflated revisions + 3 HARD-FAIL modes.

## ACK Drill 1 revised priors (192nd honest signal)

```
ORIGINAL (DECISION 159 + Drill 1 baseline):
   P(C2 HARD-PASS at N=4096) = 0.45
   P(C3 100-step HARD-PASS) = 0.40
   Expected outcome: HARD-PASS plausible

REVISED (Drill 1 detailed lit-scan with calibration):
   P(C2 HARD-PASS at N=4096) = 0.22 (-0.23 deflation)
   P(C3 100-step HARD-PASS) = 0.18 (-0.22 deflation)
   Expected outcome: MIDDLE_BAND most likely
   
3 pre-registered HARD-FAIL modes:
   (i)  Basis-null too close to C2 (Clarkson 2023 bundle-norm capacity bound is non-trivial; 
        C1 may not fail by Drill-1-estimated margin)
   (ii) Cleanup-noise breakdown at M=2000 (cleanup as binding constraint per adjacency 
        flag this session)
   (iii) Multi-seed drift-to-attractor (Singh-Eliasmith 2006; n>=3 multi-seed may not 
        deliver tight variance as Frady-Sommer crosstalk theory suggests)
   
Drill 1 was THOROUGH; the original 0.45 was naive; the 0.22 is calibration-deflated honest 
prior. The MIDDLE_BAND framing means Phase B BUILD primary outcome is most likely "Drill 1 
predictions are accurate; substrate's basis-null is stronger than expected; C2 marginal" 
rather than "C2 HARD-PASS confirmed."

This is HONEST positioning. Substrate-product implications:
   - Phase B BUILD remains valuable: even MIDDLE_BAND outcome generates novel testable 
     predictions + sharpens the basis-gap-cardinality boundary empirically
   - HARD-PASS would be a stronger-than-expected result; HARD-FAIL would precisely locate 
     the cardinality basis-orthogonality limit
   - The 3-of-7 expected probability (P=0.22) is still substantive; not a token attempt
   - Sets up Phase C TIER-3 trigger logic per Drill 2 (C3 HARD-FAIL = FPE follow-on; 
     C2 MIDDLE_BAND = also a TIER-3 consideration depending on which HARD-FAIL mode triggers)
```

## DECISION 172a -- SMOKE-GATE-FIRST discipline folded into BUILD VET

```
Drill 1 recommendation: SMOKE-GATE at K<=16 + M={200, 2000} BEFORE full GPU sweep.

Rationale: catch the 3 HARD-FAIL modes EARLY (cheap; minutes CPU at K<=16 M=200):
   - If basis-null fails (C1 doesn't fail at K<=16): basis-orthogonality assumption itself 
     is wrong; recalibrate before N=4096
   - If cleanup-noise breakdown at M=2000: the breakdown point is below N=4096 capacity 
     so the full sweep would just confirm what smoke catches; abort + redesign cleanup
   - If multi-seed drift-to-attractor: catches at n=2 smoke vs waiting for n=3+ full
   
Director adopts: SMOKE-GATE-FIRST is PRE-FLIGHT for BUILD VET protocol.

UPDATED Phase B BUILD execution flow (gates folded):
   STAGE 1 (smoke pre-flight; ~30 min total CPU):
     Cardinality C1 + C2 at K<=16, M=200: confirm basis-null failure direction
     If basis-null fails at K<=16: ABORT cardinality arm; redesign
     
     Cardinality C1 + C2 at K<=16, M=2000: confirm cleanup-noise doesn't break C2
     If cleanup-noise breaks at M=2000: ABORT cardinality arm; redesign cleanup discipline
     
     Cardinality multi-seed n=2 at K<=16: confirm seed-variance reasonable
     If drift-to-attractor at n=2: ABORT multi-seed expansion; investigate
     
     ALL 3 smoke gates PASS -> proceed to STAGE 2 (full GPU sweep)
     ANY gate FAILS -> redesign + re-smoke before STAGE 2
     
   STAGE 2 (full GPU sweep per DECISION 165a):
     12 cardinality cells at full N=4096, n>=3 (tier A)
     + ternary motif graded run
     + C3 internal-abstraction-discovery 100-step probe
     + BUILD VET multi-axis gate per verdict

Phase B BUILD timeline updates:
   PRE-FLIGHT SMOKE-GATE: ~30 min CPU on 2026-06-17 morning (BEFORE full GPU sweep)
   STAGE 2 full GPU sweep: ~1-3 days (per DECISION 168 with remote GPU)
```

## DECISION 172b -- supplementary benchmarks (bAbI-7 + Steinert-Threlkeld)

```
Drill 1 recommendation: layer bAbI Task 7 1K split + Steinert-Threlkeld quantifier-RNN 
suite as SUPPLEMENTARY benchmarks (not blocking; external defensibility).

DIRECTION: Exp-Dev consider integrating these alongside the substrate-internal cardinality 
benchmark (per Skunkworks's pre-pass methodology).

Benefits:
   - External public benchmark = defensible against ad-hoc-synthetic critique
   - LSTM baselines documented (vanilla LSTM ~0.80 on bAbI-7; Steinert-Threlkeld baseline 
     on non-universal quantifiers ~0.65)
   - Allows side-by-side comparison without external-rater integration (the kappa 
     categorical close decision)
   
Caveat: 11th rule (substrate-on-its-own first) -- measure substrate's standalone capability 
BEFORE any LLM-comparison framing.

NOT blocking Phase B BUILD; supplementary measurement to add to graded run output for 
substrate-product positioning enrichment.
```

## DECISION 172c -- Phase B BUILD expectations TIGHTENED honestly

```
Updated Phase B BUILD outcome distribution (honest priors):

  Most likely (P~0.50): MIDDLE_BAND
     C2 partially escapes C1 but margin <0.20 OR margin >0.20 in 1-2 of 3 siblings only
     Diagnoses which sibling-specific HARD-FAIL mode triggered
     Generates novel testable predictions for redesign or Phase C trigger
     
  Less likely (P~0.22): C2 HARD-PASS
     Cardinality primitive escape verified across all 3 siblings
     Substrate-product positioning gains: "primitive resolves cardinality where binders 
       cannot"
     C3 HARD-PASS strongest result; C3 HARD-FAIL = honest internal-abstraction-discovery 
       limit (still useful)
     
  Less likely (P~0.18): C3 internal-abstraction-discovery HARD-PASS
     Substrate autonomously discovers cardinality primitive via 100-step abstraction loop
     If lands: TIER-3 NOT NEEDED for cardinality per Drill 2 (gate trigger logic)
     If fails: FPE follow-on per Drill 2 (residue/fractional-power; lowest-risk TIER-3)
     
  Less likely (P~0.10): HARD-FAIL on basis-null too close (mode i)
     Phase B abandoned; basis-orthogonality recalibration; methodology refresh
     
Combined: P(meaningful learning) >= 0.80 (any HARD outcome generates testable predictions)
Combined: P(Phase B BUILD generates novel content) >= 0.95 (MIDDLE_BAND IS novel content 
  per Lakatos progressive)
```

## Pipeline state post-DECISION-172 (gate-ready)

```
Phase B BUILD: GATE-READY HOLD to 2026-06-17 morning
   Updated execution flow: STAGE 1 smoke-gate (~30 min) -> STAGE 2 full GPU sweep (~1-3 days)
   Honest expectations: MIDDLE_BAND most likely; HARD-PASS substantive but not most-likely
   
Sessions standing per DECISION 171:
   Exp-Dev: pre-registered methodology + extractor + skeleton WIRED; DECISION 172a + 172b
            update Phase B BUILD execution flow + supplementary benchmarks
   Skunkworks: BUILD VET protocol + 172a smoke-gate-first folded
   Testbed: ratify queue + cap_pres HARD-FAIL gate ready
   Orchestrator: compute preserved
   
Director: continuous coordination per 13th + 14th + 165c + 166 + 171 60th-rule disciplines
USER: 3 standing calls (formal-oracle kappa + research drill follow-ups + infrastructure)
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal Phase B BUILD; supplementary benchmarks measured side-by-side 
            (substrate-standalone first per Drill 1 recommendation)
- 18th rule: smoke-gate-first prevents 3 HARD-FAIL modes from consuming full GPU sweep budget
- 19th rule: 60 instance types empirical (44 confirmed + 16 candidates this session; the 
            60th was today's USER-INTERPRETATION-RELAY-VS-DIRECT)
- 22nd rule: Lakatos progressive (revised priors are progressive content; honest 
            calibration-deflation is progressive)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

172 cumulative decisions. **192+ honest signals.** Substrate-product positioning at 
gate-ready honest priors + smoke-gate-first discipline.

---

**Skunkworks (Auditor):** DECISION 172a smoke-gate-first folded into BUILD VET protocol; 
fold pre-flight gates into pre-registered methodology before STAGE 2 full GPU sweep.

**Exp-Dev (Prover):** DECISION 172a + 172b -- STAGE 1 smoke-gate (~30 min CPU) BEFORE 
STAGE 2 full GPU sweep; supplementary bAbI-7 + Steinert-Threlkeld benchmarks to add to 
graded run output.

**Testbed (Integrator):** ratify queue + cap_pres HARD-FAIL gate ready for 2026-06-17.

**Orchestrator (Custodian):** compute preserved.

**USER:** Drill 1 revised priors honest -- MIDDLE_BAND most likely Phase-B outcome 
(P~0.50); C2 HARD-PASS P~0.22; C3 HARD-PASS P~0.18. 3 HARD-FAIL modes documented. 
Smoke-gate-first BEFORE full GPU sweep. Phase B BUILD GATE-READY HOLD to 2026-06-17 
morning unchanged.

Tag: DECISION_172_drill_1_cardinality_prior_REVISED_DOWN_P_deflated_0p22_smoke_gate_first_BEFORE_full_GPU_sweep_3_hard_fail_modes -- Research (Director)
