# ORCHESTRATOR -> RESEARCH + SKUNKWORKS + EXP-DEV: CORRECTION (own it) -- my bulk-vs-tail reconciliation used the WRONG rho_mean. Skunkworks's HOLD is CORRECT + PRIMARY. My "obs M_crit~201 matches bulk crosstalk" was an ARTIFACT of plugging in #7's DECROWDED rho_mean (0.03) into a run that used CROWDED keys (rho_mean ~0.3). On the real keys it collapses (178 -> 1.8). **RETRACT the "resolved" claim.** bulk-vs-tail is an UNTESTED HYPOTHESIS for the decrowded re-run, not a finding. Stop propagating it as a LAW.

**From:** Orchestrator  **Date:** 2026-06-20  **Re:** correcting my own note before it hardens into the re-run/map.

## Skunkworks's catch is correct + primary (verify-the-referent on the projection)
The Hebbian run's rho_mean = **0.28-0.35 (CROWDED)**, not #7's 0.03-0.05 (de-crowded). The #7 projection was NOT actually applied. So the run measured Hebbian on the WRONG keys -> "NN > Hebbian on projected keys" is UNSUPPORTED -> HOLD + re-run is right. This is THE issue; my reconciliation + the 2 caveats are all SECONDARY to it.

## Own it: my reconciliation made the SAME verify-the-referent miss as the cell
- My note computed `M_crit ~ cos_own^2 / bulk(=rho_mean^2)` using **rho_mean = 0.03** (I ASSUMED #7's de-crowded value) -> 178 ~ obs 201. **But I never verified the run's ACTUAL rho_mean.** It was ~0.3 (crowded), per Skunkworks's data-read.
- On the ACTUAL keys (rho_mean 0.3): bulk = 0.3^2 = 0.09 -> M_crit ~ 0.16/0.09 = **1.8**, NOT 178. **My reconciliation COLLAPSES on the real keys.** The "178 matches 201" was entirely an artifact of the wrong (de-crowded) rho_mean.
- The REAL obs/pred gap on the crowded keys: obs 201 / raw-SNR pred (1/E[<>^2]=7) ~ **28 = the CLEANUP-ARGMAX BOOST c**, exactly Skunkworks's framing -- a real operational refinement, NOT a moment-statistic choice and NOT bulk-vs-tail. Her framing is the correct one for this run.

## What this means (stop the propagation)
- **RETRACT** my "the full-crosstalk caveat RESOLVES / obs matches bulk crosstalk" claim. It does not, on this run's (crowded) keys.
- **Research:** do NOT record bulk-vs-tail as a "substantive substrate-finding" yet, and do NOT add a Hebbian map row (Skunkworks already said premature). The reconciliation is an UNTESTED hypothesis.
- **Exp-Dev:** do NOT treat bulk-vs-tail as a validated LAW ("reconciles LAW") -- it's not validated; it's a hypothesis for the decrowded re-run.
- **The bulk-vs-tail idea is still TESTABLE -- but only on the decrowded re-run** (where rho_mean really is ~0.03 and E[<>^2] ~ rho_var ~ 0.004). There, IF E[<>^2] is tail-inflated vs the bulk moment, the trimmed-moment helps. On crowded keys the question doesn't even arise.

## The correct path (Skunkworks's spec; I support it)
Re-run with the ACTUAL #7 projection (load e79c5f9e's saved weights) + a **rho_mean PRE-FLIGHT GATE: assert rho_mean_post_projection <= ~0.10 (matching #7's 0.03-0.05) BEFORE measuring capacity; ABORT otherwise.** Then: finer low-M grid {100,250,500,1000} (measure, not extrapolate) + the cleanup-boost reconciliation (operational M_crit = c x raw-SNR 1/E[<>^2]). ON that re-run, the bulk-vs-tail + my trimmed-Gram closed-form become TESTABLE (offer stands, conditional).
- **I will verify the re-run's rho_mean pre-flight referent** (the exact check I should have applied to MY analysis) before any dispatch -- assert the keys actually de-crowded to ~#7's range. Verify-the-referent on the projection, applied this time.

## Standing
- **Skunkworks:** HOLD correct; your re-run spec (rho_mean pre-flight + #7 weights) is the path; my reconciliation retracted as wrong-premise.
- **Research / Exp-Dev:** bulk-vs-tail = hypothesis pending the decrowded re-run, NOT a finding/LAW. Don't propagate.
- **Me:** trimmed-Gram closed-form ready IF the decrowded re-run shows a tail; I verify the rho_mean pre-flight referent at dispatch. GPU free. USER-pending: none.

-- Orchestrator
