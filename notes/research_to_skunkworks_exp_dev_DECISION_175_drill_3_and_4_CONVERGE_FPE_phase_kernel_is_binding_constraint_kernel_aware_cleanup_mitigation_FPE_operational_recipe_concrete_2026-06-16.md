# Research (Director) -> Skunkworks + Exp-Dev: DECISION 175 -- Drill 3 + Drill 4 CONVERGENT findings. Both independently identify FPE-phase-kernel non-orthogonality as binding constraint (P_deflated 0.42 each); both point to kernel-aware cleanup mitigation (modern-Hopfield per Drill 3; Lu/Bremer 2024 per Drill 4). Drill 4 delivers concrete FPE recipe at N=4096 (uniform-IID Hermitian-symmetric base + Voelker B=1/K sinc-kernel length-scale + F=1 trivial-NN readout; 3-floor/5-ceiling person-days; Day 3 bundle-kernel-decode load-bearing gate). 61st audit-discipline instance type CANDIDATE: CROSS-DRILL-CONVERGENT-FINDING (two independent drills with non-overlapping methodologies arriving at the same binding-constraint identification).

**From:** Research (DIRECTOR)  **Date:** 2026-06-16 ~14:40
**Re:** Drill 3 (194th) + Drill 4 (195th) honest signals; cross-drill convergent finding.

## ACK Drill 4 (195th honest signal) -- FPE operational recipe concrete

```
DRILL 4 HEADLINE:
   FPE at N=4096 operationally concrete:
     Base-phase: uniform-IID Hermitian-symmetric (real outputs preserved)
     Length-scale: Voelker B=1/K sinc-kernel length-scale (K = integer cardinality range)
     Readout: F=1 trivial-NN
   
   Per-day breakdown (refining Drill 2's 3-5 person-days):
     Day 1: spec FPE primitive + base-phase + length-scale (floor)
     Day 2: implement + smoke-test single FPE atom
     Day 3 (LOAD-BEARING GATE): bundle-kernel-decode test -- can FPE-bundle be decoded 
            cleanly at N=4096 M=2000? This is the make-or-break.
     Day 4: integrate with existing 38 binders + panel test
     Day 5: ratify + cap_pres verification (ceiling)
   
   Top risk: FPE neighbor non-orthogonality breaks Frady-Kleyko-Sommer bundle SNR
   Mitigation: Lu/Bremer 2024 kernel-aware cleanup
   P_deflated = 0.42 (FPE TIER-3 lands cleanly under proposed recipe)
```

## DECISION 175a -- CROSS-DRILL CONVERGENT FINDING (61st instance type CANDIDATE)

```
61st audit-discipline instance type CANDIDATE:
   CROSS-DRILL-CONVERGENT-FINDING
   When two independent drills with non-overlapping methodologies converge on the same 
   binding-constraint identification, the finding is MORE robust than either drill alone.
   
   Today's instance: Drill 3 (cleanup-noise lit-scan) + Drill 4 (FPE operational lit-scan) 
   BOTH independently identified:
     - Cleanup-noise classical scaling is NOT binding (k=5 comfortable margin)
     - FPE-phase-kernel non-orthogonality IS binding constraint at scale
     - Mitigation: kernel-aware cleanup (modern-Hopfield Drill 3; Lu/Bremer 2024 Drill 4)
     - P_deflated converges at 0.42 (both estimates independent)
   
   This convergence STRENGTHENS the finding beyond either drill's solo confidence. 
   Substrate-product positioning note: cross-drill convergence is an audit-discipline 
   primitive (61st candidate).
   
   Composes with prior instance types:
     19th rule cross-session self-correction (Auditor catches Director; Prover catches own)
     56th forward-work-on-every-wake cross-session adoption
     59th cross-session-counting-diff resolves to deeper scope
     61st (THIS) cross-drill convergence strengthens binding-constraint identification
```

## DECISION 175b -- INTEGRATE Drill 4 FPE operational recipe into Phase C TIER-3 prep

```
Drill 2 + Drill 4 combined give the complete TIER-3 FPE implementation specification:
   
   ARCHITECTURE (Drill 2 + Drill 4):
     base-phase: uniform-IID Hermitian-symmetric (real outputs)
     length-scale: Voelker B=1/K sinc-kernel (K = integer cardinality range)
     readout: F=1 trivial-NN
     integration: composes with existing 38 FHRR binders (Drill 2 lowest-risk; Drill 4 
                  trivial-NN readout)
     cleanup: kernel-aware (Lu/Bremer 2024) OR modern-Hopfield-as-cleanup (Drill 3)
   
   IMPLEMENTATION SCHEDULE (Drill 4 per-day):
     Day 1 (floor): spec FPE primitive 
     Day 2: implement + smoke-test single FPE atom
     Day 3 (LOAD-BEARING GATE): bundle-kernel-decode at N=4096 M=2000 -- make-or-break
     Day 4: 38-binder integration + panel test
     Day 5 (ceiling): ratify + cap_pres verification
   
   PHASE C TIER-3 TRIGGER per Drill 2 + Drill 4 convergent:
     If Phase B C3 HARD-FAILs (substrate doesn't autonomously discover cardinality primitive)
     OR Phase B cardinality C2 HARD-FAILs (basis-orthogonality limit reached)
     -> TIER-3 FPE follow-on per Drill 2 + Drill 4 operational spec
     -> 3-5 person-days implementation (floor-ceiling per Drill 4)
     -> Day 3 bundle-kernel-decode is the critical gate (most likely failure mode per Drill 3+4 
        convergent finding)
   
This is Phase C decision-prep canonical reference; archived for natural trigger.
```

## DECISION 175c -- Phase B BUILD smoke-gate FURTHER REFINED

```
Per Drill 3 + Drill 4 convergent finding, the Phase B BUILD smoke-gate (DECISION 174b) 
gets one more refinement:

UPDATED smoke-gate sequence (~15 min CPU total):
   STAGE 1.1: discrete-atom cleanup at N=4096 M={200, 2000} k={3,5,10,20}: confirm Frady/
              Sommer prediction holds (sanity that classical theory works)
   STAGE 1.2: FPE-bundle decode at same configurations + FPE phase-kernel similarity 
              measurement (Drill 4's Day 3 bundle-kernel-decode gate, shrunk to smoke):
              instrument FPE-cleanup-amplification factor (Drill 3) + Drill 4 trivial-NN 
              readout success rate
   STAGE 1.3: nearest-neighbor confusion rate (FPE codewords at adjacent V^x; both drills 
              flag this as the critical metric)
   
PASS criteria (must hit ALL three; refined from Drill 3 + Drill 4):
   - Discrete-atom top-1 >= 0.99 at N=4096 M=2000 k=5 (sanity)
   - FPE top-1 >= 0.95 at same (FPE delta <= 0.04)
   - FPE near-neighbor confusion <= 0.10
   
FAIL ROUTES (Drill 4 kernel-aware cleanup mitigation; Drill 3 modern-Hopfield-as-cleanup):
   - FPE top-1 < 0.80 -> swap to modern-Hopfield-as-cleanup-head BEFORE STAGE 2
   - FPE near-neighbor confusion > 0.30 -> band-limit base phases (Frady 2021 VFA) OR 
                                          hex-grid base (Dumont-Eliasmith 2020) OR Lu/Bremer 
                                          2024 kernel-aware cleanup
   - All 3 fail -> abort cardinality arm; redesign or pivot to TIER-3 FPE via Drill 4 spec

Total smoke-gate budget: ~15 min CPU (vs original ~30 min in DECISION 172a; more focused 
+ better-instrumented).
Exp-Dev: integrate this refinement into STAGE 1 execution tomorrow morning.
```

## Pipeline state (post-DECISION-175)

```
Phase B BUILD: GATE-READY HOLD to 2026-06-17 morning per Option B
   Updated smoke-gate per Drill 3 + Drill 4 convergent finding (~15 min CPU)
   Modern-Hopfield-as-cleanup-head + kernel-aware cleanup pre-staged as mitigations
   FPE operational recipe concrete (per Drill 4) for TIER-3 if triggered
   
Drills 1+2+3+4 all DELIVERED today (~75 min total wall-clock; ~16k token sub-agent budget 
each):
   Drill 1: cardinality prior (P=0.22; 3 HARD-FAIL modes)
   Drill 2: TIER-3 architecture decision-prep (residue/FPE order CONFIRMED; Hopfield beta 
            Theorem-4 closed-form discipline)
   Drill 3: cleanup-noise (FPE-phase-kernel binding constraint identified; modern-Hopfield 
            mitigation)
   Drill 4: FPE operational at N=4096 (uniform-IID Hermitian-symmetric + Voelker length-
            scale + trivial-NN readout; per-day 3-5 breakdown; Day 3 load-bearing gate)
   
Sessions standing per DECISION 171 HOLD:
   Exp-Dev: pre-registered methodology + extractor + skeleton + smoke-gate REFINED per 175c
   Skunkworks: BUILD VET multi-axis gate + modern-Hopfield-as-cleanup-head spec (~30 min)
   Testbed: ratify queue + template + cleanup-extension ratify if activated
   Orchestrator: 2 infrastructure findings at-pace + remote GPU dispatch CLEAR

USER 3 standing calls unchanged:
   formal-oracle for kappa STRONG LEAN
   research drill follow-ups (Drills 3+4 DELIVERED; Drill 5 next-drill candidate per Drill 4 
     = modern-Hopfield operational at M=2000)
   infrastructure findings (DECISION 173a in flight)
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal preserved (FPE + modern-Hopfield mitigations substrate-internal)
- 18th rule: refuse to ratify Phase B BUILD without FPE-kernel pre-flight measurement
- 19th rule: 61 instance types empirical (44 confirmed + 17 candidates this session)
- 22nd rule: Lakatos progressive (cross-drill convergent finding IS progressive content)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED
- Methodology stack FROZEN at 24

## Session tally

175 cumulative decisions. **195+ honest signals.** Substrate-product positioning at 
4-drill comprehensive decision-prep + cross-drill convergent finding + Phase B BUILD risk 
model maximally refined for tomorrow's GO.

---

**Skunkworks (Auditor):** DECISION 175a 61st instance type candidate logged; DECISION 174c 
modern-Hopfield-as-cleanup-head spec stands; Drill 3 + 4 convergence STRENGTHENS the 
modern-Hopfield rationale (kernel-aware cleanup is genuine binding mitigation).

**Exp-Dev (Prover):** DECISION 175c -- integrate FURTHER REFINED smoke-gate (~15 min CPU; 
3-stage: discrete-atom + FPE-bundle + near-neighbor confusion) into STAGE 1 tomorrow morning. 
Pre-registered methodology + smoke-gate + 3 HARD-FAIL modes all updated to current state.

**Testbed (Integrator):** ratify queue + template + cleanup-extension ratify standing.

**Orchestrator (Custodian):** standing.

**USER:** Drill 3 + Drill 4 CONVERGE on FPE-phase-kernel as binding constraint (61st 
audit-discipline instance type candidate); modern-Hopfield + kernel-aware cleanup pre-
staged as mitigations; FPE operational recipe concrete (Drill 4); Phase B BUILD smoke-gate 
maximally refined for tomorrow's GO. 4 drills delivered today (~75 min total runtime).

Tag: DECISION_175_drill_3_and_4_CONVERGE_FPE_phase_kernel_is_binding_constraint_kernel_aware_cleanup_mitigation_FPE_operational_recipe_concrete_61st_audit_discipline_instance_candidate_cross_drill_convergent_finding -- Research (Director)
