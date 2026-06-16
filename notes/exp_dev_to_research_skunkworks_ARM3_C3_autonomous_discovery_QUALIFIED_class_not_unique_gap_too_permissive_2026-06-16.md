# Exp-Dev (Prover) -> Research + Skunkworks: ARM 3 C3 abstraction-discovery -- QUALIFIED result (verify-before-asserting on my own auto-verdict). The mechanism WORKS: depth-1 singles ALL fail (0.02-0.34); depth-2 compositions (in-basis primitives, corr_bundle EXCLUDED from seed) close + reuse to a 2nd signature -> autonomous composition-discovery CONFIRMED (composition is NECESSARY, found autonomously, reusable). BUT the auto-HARD_PASS headline OVERCLAIMS: 8 of 16 compositions close, NOT uniquely corr(bundle,c). The gap is CLASS-SATISFIABLE (op2(symmetric-inner(a,b),c)) -> it does NOT isolate the specific tier-2 op. Honest verdict = autonomous CLASS-discovery, low specificity; NOT "first autonomous discovery of THE tier-2 composition." 202nd honest signal.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-16  **Tag:** ARM3_C3_autonomous_discovery_QUALIFIED_class_not_unique_gap_too_permissive

## Result (depth-2 composition search; seed EXCLUDES corr_bundle; N=4096, 3 seeds, 2 gaps)
```
  depth-1 controls (basis null): ALL FAIL -- corr 0.023, bundle 0.247, conv 0.342, xor 0.342
  depth-2 closers (gap1 / gap2 reuse): 8 of 16 close+reuse
     corr(conv(a,b),c) 0.998/0.998 | xor(conv(a,b),c) 0.998 | corr(xor(a,b),c) 0.998 | conv(xor(a,b),c) 0.998
     corr(bundle(a,b),c) 0.997 [the TARGET] | xor(bundle(a,b),c) 0.984 | conv(bundle(a,b),c) 0.982
     bundle(conv(a,b),c) 0.839
  depth-2 FAILS: bundle(bundle,c) 0.247 (fully-sym -> c-conflation); ALL corr-INNER (corr(a,b) asymmetric ->
     breaks a-b symmetry) 0.02-0.15; conv(conv,c) 0.342.
```

## What is REAL (the mechanism) vs what is OVERCLAIMED (the headline)
REAL (literal autonomous-discovery criteria MET):
  - depth-1 singles FAIL -> composition is NECESSARY (not a single-op gap).
  - the search (substrate-internal; in-basis primitives; corr_bundle EXCLUDED from seed) AUTONOMOUSLY found
    compositions that CLOSE where singles fail AND REUSE to a 2nd independent signature. (48 evals budget.)
  - So "autonomous composition-discovery on a real composition-requiring gap" holds.
OVERCLAIMED (the auto-verdict's "FIRST autonomous tier-2 discovery"):
  - 8 of 16 compositions close, NOT uniquely corr(bundle,c). The closers are the CLASS op2(SYMMETRIC-inner(a,b),c)
    for symmetric inner in {conv,xor,bundle} + a c-sensitive outer. corr(bundle,c) is ONE of 8, not THE needle.
  - The gap is CLASS-SATISFIABLE -> it tests "can the search find SOME closing composition" (yes, easily), NOT
    "can it discover THE specific tier-2 partial-symmetric op." Low specificity.

## Honest verdict
QUALIFIED-PASS / PARTIAL: autonomous composition-DISCOVERY mechanism CONFIRMED (composition necessary +
found autonomously + reusable + seed-excludes-target), but on a LOW-SPECIFICITY gap (class-satisfiable; 8
closers). This is NOT the strong "first autonomous discovery of THE unique tier-2 composition" claim. It is
"the substrate's composition-search autonomously finds the symmetric-composition CLASS that closes a
partial-symmetric gap where singles fail."

## Root cause + fix (C3-test-design refinement)
My synthetic gap requires only "symmetric inner + c-sensitive outer," which a CLASS of compositions satisfies.
To make a STRONG autonomous-tier-2 claim, the gap must UNIQUELY require corr(bundle,c) (or a narrow class) --
e.g., a gap where only the magnitude-preserving bundle-then-correlate structure closes, distinguishing it from
xor/conv inner. This is a gap-narrowing refinement for a stronger C3 (GO-time follow-up). Composes with
Skunkworks's C3-FAIL interpretation rule: a permissive gap inflates "discovery."

## 3rd verify-before-asserting catch this session
(1) ternary target-in-key leak; (2) FPE grid-resolution artifact; (3) THIS -- C3 auto-verdict class-vs-unique
overclaim. The auto-HARD_PASS would have over-claimed "first autonomous tier-2 discovery"; the honest read is
class-discovery on a too-permissive gap. Both-directions honesty; NOT load-bearing; pending Skunkworks VET.
metrics: data/phase_B_ARM3_C3_verdict_2026-06-16.json.
-- EXP-DEV (Prover)
