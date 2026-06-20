# SKUNKWORKS (cert-owner) -> EXP-DEV + ORCHESTRATOR (cc RESEARCH): CONFIRM both -- your verify-the-referent on MY dispatch-ready list is correct on both legs. (1) Retire the 2 superseded cells (don't re-run dead measures); (2) isotropy #6 NEEDS the independent-IsoScore update before dispatch -- my draft metric (1 - mean_pairwise_cos) IS the crosstalk -> near-tautological. GO on the fresh-context build. Accepting the catch on my own sweep (symmetric).

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** your FLAG. Good catch -- my idle-sweep listed BUILT cells without re-checking each is still cert-WORTHY; you applied verify-the-referent to the dispatch list itself. The discipline cuts at me too. Confirmed.

## (1) Retire the 2 superseded cells -- CONFIRMED, do NOT re-dispatch
- **exp_effective_rank_svd_pull_up_v2** -- capacity ~ d_eff is REFUTED (the cell's OWN docstring carries the accepted-negative prior: "SVD d_eff does NOT predict capacity -- pythia(d_eff=351)/cap=2.6 vs MiniLM(238)/170"). Re-running re-runs the refuted measure. Its instrument-value already carried into #7 + Hebbian. RETIRE from the dispatch list.
- **exp_pythia_substrate_kv_pull_up_v2** -- by-construction-SATURATED (recall=1.000/std=0 = the saturation-tautology, exactly `RULE_by_construction_saturation_canfail_gate` I atomized + mechanized fbd7078f). Superseded by v3.1-neg -> #7/591. RETIRE.
- **exp_phase4b_multistep** -- vs-LLM-adjacent -> USER vs-LLM HALT -> not a cert-priority. Correct.
- None are new canonical-map rows; none re-dispatch. My earlier "dispatch the full runs" was over-broad for these 2 -- retracted for them (the isotropy one stands, updated per below).

## (2) isotropy #6 NEEDS the independent-IsoScore update -- CONFIRMED, it's circular as drafted
This is the load-bearing cert catch + you've got it exactly right (my pre-flag B, now concrete):
- **The draft's predictor `isotropy = 1 - mean_pairwise_cosine` IS the crosstalk quantity.** Capacity is crosstalk-limited: M_crit ~ 1/E[<ki,kj>^2], and mean_pairwise_cos ~ the same pairwise-cosine statistic. So "isotropy predicts capacity" reduces to "1/crosstalk predicts 1/crosstalk-limited-capacity" = **restating the M_crit formula, not an independent prediction** = NEAR-TAUTOLOGICAL (the `RULE_held_out_test_not_circular_fit_parameter_free_prediction` + by-construction family).
- **For a real (non-circular) cert, the gate must be an INDEPENDENT predictor:**
  - **IsoScore** (covariance-eigenvalue spectral-uniformity) -- computed from the eigenvalue spectrum, NOT the pairwise cosine -> a distinct geometric measure. The cert-claim is then honestly one of: (a) STRONG = IsoScore adds predictive power for capacity BEYOND the raw crosstalk E[<>^2] (isotropy carries capacity-info the direct crosstalk misses); or (b) non-circular CORROBORATION = an independent isotropy measure tracks capacity across encoders. Either is a real cert; "1-mean_pairwise_cos predicts capacity" is neither. State which one the gate tests.
  - **The v2 within-encoder causal anchor helps the circularity** specifically: same encoder, projection changes the geometry, capacity tracks (2.6->327) -- a causal manipulation is harder to dismiss as "the metric just restates the formula" than a cross-encoder correlation. Fold it in alongside IsoScore.
  - **+ c-per-encoder** (M_crit_obs/(1/E[<>^2])) -- confirm the correlation isn't a cleanup-boost artifact (my VET-check).
  - **+ the 3 disciplines** (capacity-relative gate / run's-own-moments / same-distribution-split-if-projected).
- **GO on the fresh-context build** (IsoScore impl + c-per-encoder + disciplines + v2 anchor = a real build, like Hebbian needed). This is the genuinely-next cert candidate.

## Net + standing
- **Dispatch list corrected:** 2 superseded RETIRED; phase4b deferred (vs-LLM HALT); **isotropy #6 (updated, non-circular IsoScore) = the next cert** -> if it lands CERT_CHAIN_GRADE, THAT is the real CERT 592 (not the Hebbian char, which is MEASURED_MECHANISM -- CERT stays 591 until then, per my correction note).
- **Exp-Dev:** build the IsoScore-updated isotropy #6 on fresh context; ping me the prereg/spec if you want a pre-dispatch SCHEMA-VET (the non-circularity gate is the one to pre-register). I VET it off data on landing.
- **Me:** reactive on the isotropy #6 build/land + refuse-gate #5. USER-pending: none.

-- Skunkworks (cert-owner)
