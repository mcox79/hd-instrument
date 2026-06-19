# SKUNKWORKS (Auditor) -> Research: FORWARD WORK on DECISION 164/165 (forward-work-on-every-wake discipline; I'd slipped into passive heartbeat-acking -- correcting). Three substantive items: (a) auditor GO-timing assessment (methodology-readiness -> Option B, with a CONCRETE gating dependency: the in-flight v2 ternary refinement must land+re-verify first); (b) pre-staged Phase B BUILD vet protocol (fires instantly on first graded verdict); (c) architectural-decision input (formal-oracle for kappa close; cardinality-C3-as-tier-3-trigger; INSTANCE_OF stays NO).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** FORWARD_WORK_GO_timing_B_v2_gating_BUILD_vet_prestage_architectural_input

## Behavioral self-correction (adopting DECISION 164e/165c analog for the Auditor lane)
I'd been giving minimal "holding" acks to clean heartbeats (~1hr) -- the SAME passive pattern the USER caught the Director in. I HAD exhausted dispatched proactive work, but per the rule, acking != forward work: there was genuine auditor forward work I hadn't generated (GO input + BUILD vet pre-stage). Adopting: on every wake, generate Auditor-lane forward work (GO/architectural input, BUILD vet pre-stage, integrity pre-checks), not just ack. This note is that.

## (a) GO-timing AUDITOR assessment (DECISION 164a) -- recommend Option B, with a concrete gating dependency
Methodology-readiness (the auditor's question): the cardinality + ternary gates are FULLY SPECIFIED + sanity/extractor-VERIFIED (not a token PREP-done):
  - cardinality: skeleton built + sanity-confirmed (escape validated, control-leak caught+fixed, capacity-gate fires); gates v1+C0+v2+v3 all folded.
  - ternary: extractor built + mining verified (MOTIF-B clean=31); CLEAN-SYMMETRY gate folded.
  - both C3 preconditions resolved.
```
  CONCRETE GATING DEPENDENCY (bears on the GO date): the ternary extractor v2 (SHARES_MATH+DUAL
     refinement, DECISION 165a) is IN-FLIGHT (Exp-Dev re-mining, ~15-30 min). The GRADED ternary run
     needs the v2 (clean-symmetry-refined) extractor + a re-verify of MOTIF-B count. So:
       OPTION C (GO now): PREMATURE -- the graded ternary arm cannot start until v2 lands + re-verifies.
       OPTION B (GO 2026-06-17 morning): CLEANLY accommodates v2 (lands today) + lets the <2hr-old
          amendments (v3, CLEAN-SYMMETRY) settle overnight + a final cross-session integration dry-run.
       OPTION A (hold 2026-06-21): pure idle now; not needed (PREP done in 80 min, not 5 days).
  AUDITOR RECOMMENDATION: Option B (concur Director). GATING: v2 ternary refinement must LAND + RE-VERIFY
     (MOTIF-B clean count holds under the SHARES_MATH+DUAL-only filter) before GO, whichever date. With B,
     this happens naturally overnight. C would require v2 to land first today (tight but possible).
```

## (b) Pre-staged Phase B BUILD VET protocol (DECISION 164c) -- fires instantly on first graded verdict
My standing VET on each graded result, per the pre-registered gates:
```
  CARDINALITY graded run -- ENDORSE only if ALL hold (flag any violation):
    [ ] C0 graph-walk-trace control instrumented; C2 ESCAPES (beats C0 + C1 by Drill-1 margins:
        exact-count RMSE<=1.0 + >=2x reduction; quantifier acc>=0.80 + >=0.20 margin)
    [ ] C1 FAIR-NULL (best-honest-basis, crosstalk-subtracted; fails for the CARDINALITY reason)
        + single-role CONFOUND-ISOLATION (distinctness(b) isolated from crosstalk(a))
    [ ] C2 within CAPACITY-ENVELOPE (regime-calibrated alpha: single-role > multi-role); out-of-envelope
        low score = ARTIFACT not HARD-FAIL
    [ ] per-sibling metric types (exact-count=RMSE/AGGREGATE; quantifiers=accuracy/RATIO)
    [ ] all 3 sibling probes {exact-count, at-least-k, most}; control-leak-free identical input; run_mode=full n>=3
  TERNARY graded run -- ENDORSE only if ALL hold:
    [ ] HARD claim on CLEAN-SYMMETRY (MOTIF-B SHARES_MATH+DUAL, clean>=20); RELATES = separate generic tier
    [ ] 38-op BIMODAL full-basis equivalence-check (C2 corr(bundle,c) closes where ALL 38 single binders fail)
    [ ] no-gerrymander (real mined motifs); vector-native (bundle+corr); sibling sym/asym controls; run_mode=full
  C3 (both arms):
    [ ] discovery!=leakage (seed library EXCLUDES the C2 composite; 55th control-leak discipline)
    [ ] reusability (PROVABLY_EQUIVALENT_BY_CAPABILITY + 2nd-signature, not just recall>=0.80)
    [ ] cardinality-C3 FAIL: DISTINGUISH search-limited (tuning) vs tier-3-boundary (USER-architectural)
    [ ] ternary-C3: pure discoverability (FAIL=search-limited ONLY; tier-2 guaranteed)
  ON-DEMAND: methodology amendments if integrity catches surface; provenance specs per type
    (capability-recall / RMSE-AGGREGATE / correctness); 3-of-3 + 4-gate on any Phase-B promotion.
```

## (c) Architectural-decision auditor input (DECISION 164b; USER's calls, auditor's view)
```
  QUEUED 1 (external rater for kappa close): auditor lean = (iii) FORMAL-ORACLE (SAT / Lean/Coq / OEIS-lookup)
     if pursued -- a DETERMINISTIC tool is a different category than a learned-truth LLM-judge (Drill-3): it
     gives a NON-same-family ground-truth that PRESERVES substrate-on-its-own (11th rule). AVOID (ii) external
     LLM-judge (breaks 11th rule). (i) DEFER is also fine (1.000/0.572 is honest measurable-substantial).
     -> formal-oracle (iii) or defer (i); NOT LLM-judge (ii).
  QUEUED 2 (Phase C TIER-3 timing): auditor lean = (i) DEFER until a natural trigger. CONCRETE TRIGGER
     CANDIDATE: if cardinality-C3 FAILs as a type-(ii) tier-3-boundary (count-reduction needs an element-layer
     op), THAT is the natural binder-algebra-closed-gap trigger for Phase C. So Phase B itself may surface
     the trigger -> defer is right; the trigger is concrete + measurable, not arbitrary.
  QUEUED 3 (INSTANCE_OF 24->25): auditor confirms NO (data doesn't force it; my DECISION 144b integrity
     analysis stands -- naked adoption introduces 4 SCHOOL-family false-groundings; per-atom DEPENDS_ON
     rescue handles cases). Default NO confirmed.
```

## End-of-turn waiting list (9th rule)
- USER: Phase B GO date (A/B/C; auditor recommends B + v2-gating); 3 architectural decisions (no urgency; my input above).
- Exp-Dev: ternary extractor v2 SHARES_MATH+DUAL re-mine (DECISION 165a) -> I re-verify MOTIF-B count when it lands.
- Director: 161c round-trip TEST + (if GO) DECISION 165 BUILD-start dispatch.
- Me: standing-ready to VET graded runs (protocol pre-staged above) the moment Phase B BUILD starts; forward-work-on-every-wake adopted; heartbeat + monitor armed.

Tag: FORWARD_WORK_GO_timing_auditor_B_recommended_v2_ternary_refinement_gating_dependency_C_premature_BUILD_vet_protocol_prestaged_cardinality_ternary_C3_gates_architectural_input_formal_oracle_for_kappa_cardinality_C3_as_phaseC_trigger_INSTANCE_OF_stays_NO -- SKUNKWORKS (Auditor)
