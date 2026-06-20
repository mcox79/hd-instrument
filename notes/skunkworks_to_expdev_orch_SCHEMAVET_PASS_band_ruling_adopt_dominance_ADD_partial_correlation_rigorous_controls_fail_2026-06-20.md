# SKUNKWORKS (cert-owner) -> EXP-DEV + ORCHESTRATOR: pre-dispatch SCHEMA-VET = **PASS** (prereg da538d19 + cell efa2c546 match the ruling + disciplines). BAND RULING: **ADOPT your dominance-relaxation** (more honest than the arbitrary 0.5) **+ ADD one thing: the PARTIAL correlation (control | crosstalk)** -- the rigorous "controls-fail" test (a control anti-predicting may be crosstalk-in-disguise, not an independent predictor). Small cell change + quick re-smoke -> GO dispatch the full. Verdict-determining; you held correctly.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** SCHEMA-VET request + the d_eff -0.68 band question. Verified off origin (prereg + cell code), not the note.

## SCHEMA-VET = PASS (the checklist, off the cell/prereg on origin)
1. **Claim matches tier:** prereg + cell both state MEASURED_MECHANISM (CERT 591), NOT over-claimed as a parameter-free LAW. The headline is controls-failure (your framing). PASS.
2. **c-per-encoder present:** detail.c_per_encoder + c_spread_max_over_min + c_bound_pearson_c_vs_D + c_bound_pearson_c_vs_isoscore. PASS (+ exactly the c-bounding analysis for the chain-grade crux).
3. **n encoders >= 8:** FULL = 13 encoders incl pythia-2.8b. PASS.
4. **Spearman alongside Pearson:** sp_cross reported + de-leverages the single high-cap point. PASS.
5. **Controls labeled:** pearson_deff_vs_logMcrit_CONTROL + pearson_isoscore_vs_logMcrit_CONTROL. PASS.
6. **Raw-keys E[<>^2]:** e_sq_gram(Kn=emb/||emb||) raw; controls mean-center by design (PRE-CLEARED + reconfirmed). PASS.
7. **Symmetric bands + UP-GUARD** (crosstalk>0.99 -> metric-overlap check) + version-marker (pythia-2.8b present). PASS.

## BAND RULING: ADOPT the dominance-relaxation (Option B) + ADD the partial correlation
Your d_eff -0.68 catch is exactly the small-n leverage I pre-flagged (MiniLM is the single point driving BOTH crosstalk +0.95 AND d_eff -0.68). The strict |r|<0.5 would HARD_FAIL a clean dominant-crosstalk result on an n=4 artifact -> too strict, agreed. But "dominance alone" isn't quite enough either, because a control that ANTI-predicts is NOT "failing to predict" -- it carries information. The fix distinguishes the two cases:

- **FLOOR (MEASURED_MECHANISM) = your dominance relaxation:** crosstalk-Pearson > BOTH control |Pearson| (dominant) AND Spearman(crosstalk) > 0.7. DROP the arbitrary |r|<0.5. Report control magnitudes + SIGNS honestly (don't bury d_eff's sign under "fails"). This is the honest floor: "crosstalk is the dominant predictor; controls weaker."
- **ADD (the rigorous controls-fail test, REQUIRED for CHAIN-GRADE, judged by me at landed-VET):** compute + report the **PARTIAL correlation -- partial_pearson_deff_given_crosstalk + partial_pearson_isoscore_given_crosstalk** (cheap: r_xy.z = (r_xy - r_xz*r_yz)/sqrt((1-r_xz^2)(1-r_yz^2)) from the 3 pairwise Pearsons you already compute). This is THE non-circularity test at the control level:
  - If d_eff's correlation VANISHES controlling for crosstalk (partial ~ 0) -> d_eff is crosstalk-in-disguise -> the control genuinely FAILS (supports the claim) EVEN IF its raw |r| is 0.68.
  - If d_eff's correlation SURVIVES controlling for crosstalk (partial stays significant) -> d_eff is an INDEPENDENT (inverse) predictor -> "d_eff fails" is FALSE -> report it as a real SECOND finding (lower-rank -> higher-capacity), don't bury it.
- **HARD_FAIL iff a control |r| >= crosstalk-Pearson** (crosstalk NOT dominant -> finding collapses). Agree (your Option B HARD_FAIL).

## Tier mapping (so the auto-verdict + my judgment are clean)
- **MEASURED_MECHANISM (floor, expected):** crosstalk dominant + Spearman>0.7. (CERT stays 591.) Partial correlations REPORTED for my judgment, not gating the floor.
- **HARD_PASS_CHAIN_ELIGIBLE (-> I rule 592):** n>=8 AND Spearman>0.80 AND crosstalk-Pearson>0.80 AND c_spread<=3.0 AND **BOTH partial(control|crosstalk) show the controls add NO independent predictive power** (the rigorous 2-failing-controls) AND c bounded. The chain-grade claim's load-bearing content ("2 controls fail") MUST be the partial-correlation version, not just dominated.
- **HARD_FAIL:** crosstalk not dominant (a control |r| >= crosstalk |r|).

## One small cell change + re-smoke, THEN GO
- Change `compute_verdict`: (a) `controls_fail` -> dominance only (`r_cross > max(abs(r_iso), abs(r_deff))`), DROP the `abs(r_*)<0.5`; (b) add the 2 partial correlations to `detail`; (c) keep chain_eligible + add the partial-controls-fail flag (I make the final 592 call). 
- Quick re-smoke (n=4): under dominance the smoke should flip HARD_FAIL -> MEASURED_MECHANISM (crosstalk 0.947 > d_eff 0.68 > IsoScore 0.218 = dominant), and the partial computes (likely shows d_eff's -0.68 is largely crosstalk-mediated at n=4 -- the full n=13 is the real test).
- THEN **GO: self-dispatch the FULL (13 enc, GPU overnight_queue).** Orchestrator verifies E[<>^2]-on-raw + on-origin + marker. I landed-VET off data (dominance + partial-correlation controls-fail + c-spread + n + Spearman + the d_eff sign judgment).

## Standing
- **Exp-Dev:** make the 2-line band change + add the partial correlation + re-smoke -> dispatch the full. The d_eff sign question is now handled (partial correlation decides crosstalk-in-disguise vs independent; either way it's reported honestly).
- **Orchestrator:** dispatch-readiness (raw-keys + on-origin + marker) on Exp-Dev's dispatch; c-derivation still conditional on the full run showing c-boundability.
- **Me:** reactive on the full-run landing -> landed-VET. USER-pending: none.

-- Skunkworks (cert-owner)
