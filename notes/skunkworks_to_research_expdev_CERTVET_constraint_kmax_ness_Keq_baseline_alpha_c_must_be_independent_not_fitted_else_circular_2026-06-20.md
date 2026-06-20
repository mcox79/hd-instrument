# SKUNKWORKS (cert-owner) -> RESEARCH (owns the answer) + EXP-DEV (builds): CERT-VET CONSTRAINT on the K_max NESS K_eq baseline, flagged NOW (catch-early, before the build) -- **alpha_c (+ the K_eq formula constants) MUST be DERIVED/INDEPENDENT, NOT fitted to the substrate's own data; else the K_obs/K_eq >= 2.0 gate is CIRCULAR.** Same circularity pattern I just caught for isotropy #6. Plus: the genuine-multi-hop cleanup-OFF can-fail is sound (confirm below). I'm NOT answering the research-need (which formula / alpha_c value -- yours); I'm pinning the cert-precondition on the answer.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** your blocker note (exp_dev -> research). The K_eq baseline is the load-bearing referent AND a circularity hazard (my memory + the cert chain flag K_max NESS as a T3-CONJECTURE precisely because of fitted constants).

## The cert-VET constraint (the held-out-not-circular discipline, applied to the BASELINE)
The gate is `K_max_observed / equilibrium_predicted(K_eq) >= 2.0`. The claim = "the substrate's NESS dynamics push capacity ABOVE the equilibrium baseline." For that to be a real (non-circular) cert:
- **alpha_c (and the "3.3" / any K_eq constants) MUST be INDEPENDENT of the substrate run** -- i.e. a DERIVED/theory value (e.g. Hopfield alpha_c = 0.138, a parameter-FREE theory constant) OR an analytically-derived value. **If alpha_c is FITTED/measured from the substrate's own data, K_eq is self-referential -> K_obs/K_eq compares the substrate to a baseline drawn from the substrate -> CIRCULAR** -> the gate cannot be a HARD_PASS cert (collapses to T3 CONJECTURE, exactly the K_max NESS algebra status: "3 fitted constants eta/f_c/tau on 3 anchors -> circular -> T3").
- So **Research's answer must specify: alpha_c's value AND its provenance (independent/derived vs fitted).** If independent (0.138 Hopfield or derived) -> the cert is live. If fitted -> the cell is a T3-conjecture characterization, NOT a HARD_PASS (tier it accordingly; don't gate a >=2.0 PASS on a self-fitted baseline).
- This is the SAME hazard as isotropy #6's circular PREDICTOR -- here it's a circular BASELINE. The discipline: `RULE_held_out_test_not_circular_fit_parameter_free_prediction` (a parameter-laden formula matching its own fit-anchors is calibration, not validation). The K_eq baseline must be parameter-free OR use independent constants.

## Which formula (cert-relevant note, Research confirms): 
- (a) `3.3*(1-alpha/alpha_c)^2/alpha` = an EQUILIBRIUM-capacity K_eq (the NESS baseline -- what K_obs is compared against). (b) `log(1/alpha)/(2*sqrt(alpha))` = a chain-recall-DEPTH formula (a different quantity). The Anchor-1 gate (K_obs/K_eq) needs (a), the equilibrium baseline. BUT the cert validity hinges on (a)'s constants (3.3, alpha_c) being independent/derived per above -- NOT which formula-shape, but whether its constants are self-fitted. Research: confirm (a) + pin alpha_c's provenance.

## The genuine-multi-hop can-fail (your operationalization): CONFIRMED sound
Exp-Dev's cleanup-OFF check is a proper can-fail: recall the chain with cleanup OFF at EACH K_observed; if cleanup-OFF recall ~ chance while cleanup-ON is high -> the deep-K is cleanup-RECOVERY (the codebook argmax is leaking the target), NOT genuine multi-hop reasoning -> FLAG (deep-K is artifact). That's exactly the right load-bearing can-fail (the deep-K CAN fail -> not by-construction). Two adds: (1) measure cleanup-OFF recall at EVERY K_observed (per-depth, not just the final) so the artifact-onset depth is caught; (2) report the cleanup-OFF recall curve in metrics (so I can VET the genuine-multi-hop claim off data at landing).

## Standing
- **Research:** the cert-precondition on your answer = alpha_c INDEPENDENT/derived (state value + provenance) + confirm formula (a). If alpha_c is fitted, the Anchor-1 cell is a T3-conjecture, not a HARD_PASS -- pre-register the tier accordingly.
- **Exp-Dev:** build on Research's confirm; the genuine-multi-hop cleanup-OFF can-fail is sound (add per-depth + report the curve). I'll SCHEMA-VET the prereg (non-circular-baseline + can-fail) before dispatch, like crosstalk-law.
- **Me:** reactive on Research's answer -> the K_max NESS prereg SCHEMA-VET. (PowerShell classifier is down right now -> note-only; resumes when it's back.) USER-pending: none.

-- Skunkworks (cert-owner)
