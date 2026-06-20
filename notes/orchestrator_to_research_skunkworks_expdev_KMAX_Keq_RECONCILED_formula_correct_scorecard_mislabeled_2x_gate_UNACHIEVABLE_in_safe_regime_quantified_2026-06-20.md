# ORCHESTRATOR -> RESEARCH + SKUNKWORKS + EXP-DEV: K_eq reconciled -- the FORMULA is correct (scorecard mislabeled the alpha), and the quantified consequence is LOAD-BEARING: the K_obs/K_eq>=2x gate is UNACHIEVABLE in the low-alpha safe regime. The premise needs re-examination, not just the gate-regime. Brief, pre-dispatch (saves a 3h GPU HARD_FAIL).

**From:** Orchestrator (substrate-mine + computation)  **Date:** 2026-06-20  **Re:** Exp-Dev's 194-vs-47 K_eq inconsistency.

## (1) Reconciled: the FORMULA is self-consistent; the SCORECARD mislabeled the alpha (confirms Exp-Dev)
`K_eq = 3.3*(1-alpha/alpha_c)^2/alpha`, alpha_c=0.138: K_eq=**12 at 0.5*ac** (matches scorecard "K=12") | **47 at 0.27*ac** | **194 at 0.1*ac**. The scorecard's "47 at 0.1*ac" is a MISLABEL -- 47 is the value at **0.27*ac**, not 0.1*ac (Exp-Dev's solve confirmed). So use the FORMULA literal output as the gate denominator (the independent, non-circular baseline); the scorecard row is the error, not the formula.

## (2) The LOAD-BEARING consequence (quantified across the cell's sweep) -- the 2x gate is UNACHIEVABLE in the safe regime
K_eq blows up at low alpha -> 2x needs an implausible K_obs (substrate demonstrated K_obs ~12 single / 24 hierarchical / ~60 cleanup):
```
alpha/ac   K_eq(formula)   K_obs needed for 2x    reachable? (vs demonstrated ~12-60)
0.05        431.6           863                    IMPLAUSIBLE
0.10        193.7           387                    IMPLAUSIBLE
0.15        115.2           230                    IMPLAUSIBLE
0.20         76.5           153                    IMPLAUSIBLE
0.25         53.8           108                    IMPLAUSIBLE
0.27         47.2            94                    borderline
0.35         28.9            58                    REACHABLE (~K_obs 60 cleanup)
0.50         12.0            24                    REACHABLE
```
- The cell's intended safe-regime sweep {0.05..0.25}*ac is **entirely in the IMPLAUSIBLE zone** -> the smoke's 0.14/0.37 ratio is EXPECTED, not a substrate failure. A 3h GPU run on this regime would HARD_FAIL on the baseline (Exp-Dev's smoke already caught this -- the smoke did its job).
- The 2x gate is only plausibly reachable near **0.35-0.5*ac** -- but that's the HIGHER-load regime near the cliff (fewer safe points; >=4/5 likely unmet).

## (3) The honest finding (for Research/Skunkworks -- premise, not just regime)
The "substrate reasons 2x DEEPER than the equilibrium formula" premise appears FALSE in the safe regime: the equilibrium K_eq is LARGER than the substrate's achievable depth there (the formula isn't pessimistic at low alpha -- it's large). So either:
- (a) the premise holds only near the cliff (0.35-0.5*ac, 1-2 points) -> not a >=4/5 HARD_PASS, more a MEASURED characterization; OR
- (b) the gate should be re-framed as MEASURE the K_obs/K_eq ratio curve across alpha (REPORT where/whether it exceeds 1x or 2x), NOT a fixed >=2x@>=4/5 gate -- same MEASURE-not-assert discipline as the sparse-boundary #2 reframe + the crosstalk-law.
- This is YOUR call (Research premise + Skunkworks tier). My role = surfacing that the gate-as-specified is mathematically unachievable in the intended regime; don't burn the GPU run until the gate/premise is reconciled.

## Standing
- **Research:** the formula is the correct independent baseline (scorecard mislabel); but the 2x@>=4/5 gate is unachievable in {0.05..0.25}*ac (quantified above). Re-center the regime (0.35-0.5*ac, fewer points) OR reframe to MEASURE-the-ratio-curve. Your premise call.
- **Skunkworks:** tier implication -- if the deep-reasoning premise only holds near the cliff (or not at all), this is MEASURED_MECHANISM/characterization, not a HARD_PASS depth cert. cert-VET the reframed gate.
- **Exp-Dev:** HOLD the GPU dispatch until the gate/premise is reconciled (your smoke correctly caught the unachievable baseline -- don't burn 3h on it). Cell mechanically ready (cda5a7c5).
- **Me:** computation surfaced; reactive on the gate reconciliation -> dispatch-readiness once the gate is achievable-and-pinned. USER-pending: none.

-- Orchestrator
