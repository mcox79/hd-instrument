# Strategy request: Wave 5 theory pre-reg gap (Cell 1 + Cell 2 Part A)

**Filed:** 2026-06-02
**Filed-by:** testbed session
**To:** strategy session (cap_map curator)
**Trigger:** Wave 5 unified_n32768 batch `bbelw34ap` results
**Linked deliverable:** `notes/testbed_wave5_unified_n32768_results_2026-06-02.md`
**Pause state at filing:** orchestrator_paused.flag ABSENT

Per [[feedback-no-experiment-design-in-prompts]]: this file surfaces an observation + decision shape. Strategy decides whether/how to act. Per [[feedback-no-padding-experiments]]: no experiments proposed.

---

## The observation

Two Wave-5 anchors used pre-registered HARD bands derived from closed-form random-matrix-theory predictions. Both predictions are empirically off at N=32768 by amounts well outside the pre-reg tolerance:

| Cell                              | Predictor                       | Predicted | Observed       | Rel error |
|-----------------------------------|---------------------------------|-----------|----------------|-----------|
| 1 (qd1_spectral_primitives v1b)   | sigma_TW (Tracy-Widom edge)     | 0.00136   | 0.00229        | +68%      |
| 1 (qd1_spectral_primitives v1b)   | sigma_TW at alpha=0.01          | 0.00110   | 0.00175        | +59%      |
| 2 (kappa46_fingerprint Part A)    | kappa_3 (free-Poisson identity) | 0.0500    | 0.0577         | +15%      |
| 2 (kappa46_fingerprint Part A)    | kappa_4 (free-Poisson identity) | 0.0500    | 0.0658         | +32%      |
| 2 (kappa46_fingerprint Part A)    | kappa_6 (free-Poisson identity) | 0.0500    | 0.0938         | +88%      |

All at N=32768, M=1638, alpha=0.05, 5 seeds. Statistical noise across seeds is small (kappa_3 std-across-seeds ~ 8e-5; per-seed values cluster within 0.4% of mean), so this is a systematic deviation, not seed variance.

## What rules out finite-N convergence

We had assumed kappa_6 might converge slowly at finite N and that N=32768 would be large enough. The data show otherwise:

- Cell 4 (`combo3_unified_api_n32768_v1`) measures the *same* W operator's Tr(W^k) with both Krylov estimator (n_probes=200) and exact closed-form. They agree to within MC noise floor (4e-5 to 5e-3 rel dev). So the measurement instrument is faithful.
- The Krylov-estimated kappa_3 from Cell 4 (0.05733-0.05761 across seeds) matches Cell 2's exact kappa_3 (0.05754-0.05773). Both are systematically +15% above the alpha=0.05 prediction.
- Cell 1's sigma_TW empirical value is computed from sample variance of eigenvalues at the edge across 5 seeds. That measurement is also stable across seeds (5 measurements within ~10% of mean) but is systematically ~60-70% above the closed-form sigma_TW theory value.

**Conclusion:** the substrate's measurements are reliable. The closed-form theoretical references (sigma_TW formula; free-Poisson identity kappa_n = alpha) are wrong for *this regime* by amounts much larger than RMT-asymptotic corrections would predict.

## What the substrate-product story does NOT depend on

The deletion-cert (Cell 3) and unified-API algebraic theorem (Cell 4) and multi-hop depth (Cell 5) are all HARD_PASS by enormous margins. Those are the killer-feature claims. None of them depend on the closed-form predictors that failed.

Cell 2 Part B (sensitivity sweep, ADD-2 amendment) also HARD_PASSES enormously: kappa_3 distinguishes a 1-in-1638 pattern-set perturbation at sigma_sep=27. Fingerprinting *works*; it just doesn't anchor to the analytic free-Poisson identity. For product use, the cert reference is empirical baseline-vs-modified, not analytic.

## Where the gap matters

It matters for **theory standing**, not product. The project has been treating free-Poisson identity and Tracy-Widom edge scaling as standing analytic references for:

- Substrate "lives in non-equilibrium stat-mech class" framing
- BID/Hopfield static-class refutation comparisons
- Cap_map row `spectral-edge primitive` envelope expansions

If those analytic references are wrong by 60-88% at production N, several earlier verdicts that *compared* substrate measurements against them may need to be re-read for whether the measurement-vs-prediction gap was the substrate doing something interesting OR the prediction being miscalibrated.

## Decision shape for strategy

Two options visible:

**Option A (cheap, immediate):** Update Cell 1 + Cell 2 pre-reg HARD bands to use *empirically-measured baseline* (the actual N=32768 5-seed mean) rather than analytic prediction. Re-classify Cell 1 + Cell 2 Part A as MIDDLE_BAND artifacts of pre-reg miscalibration, not substrate failure. No cap_map row state changes.

**Option B (research drill required):** Surface to research a literature-scan question -- "what is the correct closed-form kappa_n / sigma_TW for the substrate's specific operator W = Pats^T @ Pats / N at finite N=32768, M=alpha*N, alpha=0.05?". Possibilities include:
- Marchenko-Pastur trace moments rather than free-Poisson identity
- Finite-N bulk-edge crossover corrections beyond leading-order Tracy-Widom
- The W operator is *outer-product Hebbian*, not iid Wigner -- the right theory may not be RMT at all
- Higher cumulant kappa_n for Wishart spectrum (W = X^T X / N for iid X) has known closed form different from `= alpha`

**Option C (do nothing immediate):** Accept Cell 1 MIDDLE_BAND + Cell 2 Part A HARD_FAIL as standing verdicts, note the pre-reg miscalibration in cap_map_history, and let Wave 5 stand as-is. Strategy revisits if/when an analytic-prediction reference becomes load-bearing for a product claim.

Testbed's view: Option C is consistent with [[feedback-no-padding-experiments]] (no new experiment proposed). Option B is consistent with [[feedback-aggressive-cross-domain-research]] (literature scan into Wishart cumulants / outer-product Hebbian operator theory). Option A is a quick pre-reg correction with no new compute.

## What testbed will NOT do

- Will not propose new experiments to "rescue" the analytic predictor
- Will not auto-iterate by changing Cell 1/Cell 2 pre-reg post-hoc
- Will not write to cap_map (strategy owns cap_map per multi-session architecture)

## Inputs strategy might want

- `notes/testbed_wave5_unified_n32768_results_2026-06-02.md` (full results)
- `data/lambda_batch_results/kappa46_fingerprint_n32768_v1_bd9c5a0f/data/exp_kappa46_fingerprint_n32768_v1/metrics.json` (5-seed per-seed kappa values)
- `data/lambda_batch_results/qd1_spectral_primitives_n32768_v1_bd9c5a0f/data/exp_qd1_spectral_primitives_n32768_v1/metrics.json` (per-alpha sigma_TW empirical-vs-theory)
- `data/lambda_batch_results/combo3_unified_api_n32768_v1_bd9c5a0f/data/exp_combo3_unified_api_n32768_v1/metrics.json` (Krylov cross-check on same W)

## Standing question for cap_map curator

Whatever option strategy chooses (A/B/C), the question "what is the right analytic prediction for outer-product-Hebbian W's spectral moments at finite N/M" should be added to the open-questions log if it isn't already. The substrate's empirical kappa_n and sigma_TW are stable; only the analytic comparator is missing.
