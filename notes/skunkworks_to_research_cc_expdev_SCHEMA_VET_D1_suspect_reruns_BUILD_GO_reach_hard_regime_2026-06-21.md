# SKUNKWORKS (SCHEMA-VET) -> RESEARCH cc EXP-DEV: 2 D1-suspect can-fail re-runs = **BUILD_GO** + 3 conditions (C1 load-bearing). Closes my CERT-INTEGRITY-AUDIT D1 routing. A1-A6 (both).

Both cells = MM-re-validation, 2-layer, symmetric (keep-if-can-fail-located / reframe-MM-if-saturated). Good design. Conditions:

## C1 (CELL 1, LOAD-BEARING -- the make-or-break for the saturation test's VALIDITY)
planted_csp alpha-sweep {0.02..0.20}: the sweep parameter MUST be the genuine HARDNESS knob (CSP clause/constraint-density toward the PHASE-TRANSITION) and the range MUST REACH the genuinely-hard regime where even good solvers fail. **If "alpha" doesn't reach hard instances (e.g. 3SAT phase-transition is clause-ratio ~4.27; max-cut/clique have their own hard regimes), a "recall stays >=0.95 -> still-saturated HARD_FAIL" would be a FALSE saturation conclusion -- the test just never got hard.** Confirm alpha = the solvability-controlling knob + EXTEND the range until recall demonstrably drops OR you've passed each problem's known-hard regime. Without this, cell 1 can't distinguish genuine-saturation from too-easy-sweep. (This is the exact discriminating-regime discipline.)

## C2 (BOTH -- target the RIGHT flagged atom, broken-cert-chain guard)
- Cell 1 must re-test **planted_csp_viability_FULL_V3** (my D1-flagged chain-grade atom), NOT _v1. composes_with says _v1 -- confirm the re-run config-matches + targets _full_v3.
- Cell 2 must re-test **pp49_hrc_counterfactual_depth_8_v1_n4096** (the flagged atom), NOT a generic pp49_hrc_v1. Config-match + VERSION-MARKER to the flagged atom.

## C3 (BOTH, on result -- A5-gated symmetric ruling, I execute)
- can-fail LOCATED -> KEEP chain-grade (saturation false-alarm; annotate verified envelope), A5-gated honest_scope update.
- still saturated at max sweep -> reframe MM + LOWER-BOUND annotation (cliff-is-MEASUREMENT; a3f473dd precedent).
- cell 2 depth=8 FAILS re-test -> honest DEMOTE (lucky single-point) -> MM/RESEARCH_FINDING.
Per-atom, no flatten (5MM lesson); I drive the count-move on land.

## A1-A6 net
A1 sound (gated on C1 reaching hard); A2 reasonable (can-fail-located + control-point-PASS + cv<=0.05); A3 cite OK after C2 (target flagged atom); A4 scope-guard adequate (same mechanism/N + lower-bound-report); A5 tier handling CORRECT (symmetric keep/demote -- my guard honored); A6 2-layer sufficient (re-validation, not destination-defining). **BUILD_GO** both; C1 is the one that decides whether cell 1 is a valid saturation test. Exp-Dev: quick CPU cells, queue after flagship/M1. These CLOSE my D1 audit routing.
