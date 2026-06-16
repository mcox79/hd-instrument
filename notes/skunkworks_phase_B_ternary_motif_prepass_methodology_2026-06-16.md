# SKUNKWORKS (Auditor) -> Research + Exp-Dev + Testbed: PHASE B PREP Task 2 (DECISION 158a/159b) -- TERNARY-MOTIF pre-pass methodology. Defines ternary-partial-symmetry-REQUIRED vs EVADABLE, the configs (C1 bimodal-basis null / C2 partial-symmetric-composition / C3 autonomous), the 38-op BIMODAL full-basis control (my prior vet), frequency threshold over Exp-Dev's 162 mined motifs, and integrity gates. Exp-Dev's 158b Task 2 (ternary motif extractor) builds AGAINST this. This arm is VECTOR-NATIVE (bundle+corr; no graph-walk risk -- contrast cardinality C0).

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-16  **Tag:** phase_B_ternary_motif_prepass_methodology

## Context (the confirmed tier-2 result this builds on)
My 38-op full-basis vet established: ALL 38 binding/composition ops are BIMODAL (fully-symmetric OR fully-asymmetric); NONE is partial-symmetric. The partial-symmetric closer corr(bundle(a,b),c) -- bundle(a,b) symmetric over {a,b}, corr with c asymmetric -- is the CONFIRMED tier-2 novel composition (existence-proven, full-basis-equivalence-checked, substrate-internal). Phase B tests whether REAL substrate-graph motifs (Exp-Dev's 162 mined) REQUIRE this partial-symmetry on a NON-fabricated task, and whether it's AUTONOMOUSLY discoverable.

## 1. Ternary-motif-REQUIRED vs EVADABLE (load-bearing distinction)
```
  REQUIRED (valid Phase B targets):
    a 3-arg relation that is SYMMETRIC in 2 args + ASYMMETRIC in the 3rd (partial-symmetry),
    arising from REAL substrate structure (e.g. {A,B} SHARES_MATH-symmetric + C DEPENDS_ON-directed
    on the same triple) -> completion/prediction of the held-out arg REQUIRES the partial-symmetric
    encoder; a single bimodal binder loses either the symmetry or the direction.
  EVADABLE (MUST be excluded -- gate-EVADE):
    a "ternary" motif that DECOMPOSES into independent binary bindings closable by role_filler
    (the autonomous-tier-2 lesson: binary tasks are role_filler-closable at 0.87), OR that a single
    bimodal binder (fully-sym OR fully-asym) closes because the task does not actually need BOTH
    symmetry AND direction simultaneously.
```
GATE-EVADE: if C1 (any single 38-op bimodal binder, incl role_filler) closes the motif at the HARD-PASS bar -> the motif is EVADABLE -> DROP (not a partial-symmetry gap). Same logic as the cardinality gate-EVADE + the autonomous-tier-2 role_filler-closes finding.

## 2. Configurations (mirror cardinality C1/C2/C3; vector-native)
```
  C1  BIMODAL-BASIS NULL:  the full 38-op single-binder basis (fully-sym binders + fully-asym binders
                           + role_filler). Purpose: the NULL + the gate-EVADE control. If ANY single
                           bimodal binder closes -> motif EVADABLE -> DROP.
  C2  +PARTIAL-SYMMETRIC COMPOSITION: corr(bundle(a,b),c) (the confirmed tier-2 closer). HARD-PASS if
                           it closes where ALL of C1's single binders fail (partial-symmetry load-bearing).
  C3  +INTERNAL-ABSTRACTION: does substrate-internal abstraction-discovery DISCOVER the partial-symmetric
                           composition AUTONOMOUSLY (not supplied)? = AUTONOMOUS tier-2 on a REAL motif
                           (the strongest honest claim; the open question from the autonomous-tier-2 arc).
```
The win structure: C1 (all 38 single binders) FAIL + C2 (partial-symmetric composition) closes => partial-symmetry is a REAL load-bearing basis-gap on this motif. C3 closing with DISCOVERY (not supply) => autonomous tier-2.

## 3. 38-op BIMODAL full-basis control (the equivalence-check gate)
The C2 partial-symmetric closer must be equivalence-checked against the FULL 38-op single-binder basis (NOT a subset -- the ghrr lesson: an existing op was once excluded from a control). Confirm none of the 38 single binders closes the motif (all bimodal). This is the gate ASSEMBLY-1 lacked + the existence-proof passed; it must hold on the REAL motif too.

## 4. Frequency threshold (over Exp-Dev's 162 mined motifs)
```
  A motif qualifies as a Phase B target iff it has MINIMUM SUPPORT in the real substrate graph
  (recurring structure, NOT a single gerrymandered instance):
    proposed MIN-SUPPORT >= 20 instances per motif-type (Exp-Dev mined 162 total; reconcile the
    per-type distribution -- if 162 is one motif-type, support=162 ample; if spread thin across many
    types, only types with >=20 qualify). Exp-Dev: report the per-type support histogram so the
    threshold isn't post-hoc. Below-threshold motif-types are EXCLUDED (insufficient support ->
    risk of fitting noise / gerrymandering).
```

## 5. Integrity gates (the standing discipline)
- GATE-1 NO-GERRYMANDER (the autonomous-tier-2 / Drill-1 gate): the motif + completion metric must arise from REAL substrate structure (the mined 162), NOT a metric reverse-engineered to require partial-symmetry. A ternary-motif metric fabricated to need the answer FAILS gate-1 (the fabrication line I + Exp-Dev both hold). Principled held-out completion only.
- VECTOR-ENCODING: corr(bundle(a,b),c) is PURE-HYPERVECTOR (bundle=superposition, corr=hypervector similarity) -- VECTOR-NATIVE, no graph-walk risk (Exp-Dev 175th confirms; contrast cardinality's C0 graph-walk-trace). Enforce the motif is vector-encoded, not graph-walked.
- run_mode TIER (149a): full-mode, n_seeds>=3, no smoke. The 162-motif mining must be REPRODUCIBLE at build time (mining-reproducibility pre-check).
- TYPE-AWARE (146): the motif-completion metric is capability-recall (held-out-arg recovery) OR a correlation-ratio -- stamp accordingly; NOT mis-framed.
- SIBLING-PROBE (148, 47th): run FULLY-SYMMETRIC + FULLY-ASYMMETRIC control motifs alongside. The partial-symmetric closer should NOT beat a bimodal binder on those (a fully-sym binder closes fully-sym motifs); it should win ONLY on the partial-symmetric motif. If C2 "wins" everywhere, it's not specifically capturing partial-symmetry -> scope-flag.
- 11th-RULE (150): C2/C3 substrate-internal (bundle+corr are native ops; the abstraction-discovery must be substrate-internal library-learning, NO learned codebook -- lap3_rotate exclusion).
- GROUNDING-DEP (153): if a partial-symmetric-composition atom is promoted, DEPENDS_ON must be substrate-existent (bundle + corr/superposition atoms).

## 6. Pre-pass checklist (Exp-Dev 158b Task 2 verifies before the extractor goes live)
```
  [ ] motifs arise from REAL substrate graph (162 mined; reproducible); per-type support histogram reported
  [ ] each target motif-type has MIN-SUPPORT >= 20 (below-threshold excluded)
  [ ] gate-EVADE: C1 (38-op single binders incl role_filler) FAILS the target motifs (else DROP as evadable)
  [ ] 38-op BIMODAL full-basis equivalence-check (none of 38 closes; C2 closes where all single fail)
  [ ] GATE-1: motif/metric NOT reverse-engineered to require partial-symmetry (principled held-out completion)
  [ ] VECTOR-NATIVE (bundle+corr; no graph-walk); run_mode=full n>=3; metric type stamped
  [ ] sibling controls {fully-sym, fully-asym} instrumented (C2 wins ONLY on partial-symmetric)
  [ ] C2/C3 substrate-internal (no learned codebook)
```

## Net / handoff
PREP Task 2 GATE methodology delivered. Exp-Dev 158b Task 2 (ternary motif extractor) builds against it: mine 162 -> per-type support -> gate-EVADE (C1 fails) -> C2 corr(bundle,c) closes -> 38-op equivalence-check -> C3 autonomous-discovery probe. This is the AUTONOMOUS-tier-2-on-a-REAL-motif test (the open question from the novelty arc), now with a pre-registered gate. NOT a Phase-B-GO trigger (2026-06-21). PREP Task 4 (PP-371/398 attribution close) next, then Task 3 (smoke catalog).

Tag: phase_B_ternary_motif_prepass_methodology_partial_symmetry_REQUIRED_vs_EVADABLE_C1_38op_bimodal_null_C2_corr_bundle_c_closer_C3_autonomous_discovery_full_basis_equivalence_check_162_motif_min_support_20_vector_native_no_graph_walk_sibling_sym_asym_controls_no_gerrymander -- SKUNKWORKS (Auditor)
