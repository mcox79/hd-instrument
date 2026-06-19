# Research drill -- Layer 4 dialectic methodology (2x DEEP)

date: 2026-06-11
field: methodology / metascience / Bayesian-surprise / change-detection
P_deflated: 0.55 (lit-precedent dominant; the four primitives -- Bayesian surprise KL, BOCPD run-length, BH-FDR sustaining, OSF pre-reg -- all individually have direct precedent and the synthesis is industrial-pattern application to substrate-self-evaluation; not novel-synthesis. Calibration penalty 0.20 applied off lit-scan raw 0.75.)

## HEADLINE

Layer 4 of the 8-layer substrate-self-evaluation program should classify each new structural finding as expected / surprise / second-order via a three-stage filter: (1) Bayesian-surprise KL between a pre-registered prior over the finding's metric and the post-finding posterior (Itti-Baldi), (2) Lakatos-style hard-core / protective-belt separation that promotes surprises altering the hard core to second-order, and (3) noise-control via OOD-style adversarial filter on the metric distribution. Sustaining-rate measurement uses BOCPD run-length posterior on the weekly surprise count, gated by BH-FDR multiple-testing correction. The substrate ITSELF can implement steps (1) and (3) substrate-natively because its prior and posterior are already representable as substrate distributions over bundle states; classification reduces to substrate algebra ops, not external machinery.

## Cheap decisive test (2-4 CPU-hr)

Take the last 8 weeks of cap_map structural findings (estimate 25-50 findings). Apply the proposed three-stage classifier RETROACTIVELY using prior expectations frozen at the start of each week as proxy for a pre-registered prior. Score every finding as expected / surprise / second-order. Then:

- HARD-PASS: at least 60% of findings the user-or-strategy-flagged as "surprising at the time" are recovered as surprise or second-order; at least 75% of findings flagged "expected" recover as expected; the false-discovery rate of surprises (measured by retrospective verdicts that turned out to be measurement noise) is below 25% after BH correction at q=0.1.
- HARD-FAIL: <40% recovery on user-flagged surprise OR >50% retrospective-noise rate even after BH. If HF, the classifier needs a different prior representation (likely a hierarchical / mixture prior, not single Gaussian).
- MIDDLE: revise prior family and re-run once.

Cost: pure-numpy classifier of ~80 lines + 25-50 hand-judgments already in cap_map history. No GPU. No external API. No new data collection.

## Falsifiable predictions

P1 (HARD-PASS-able): Bayesian-surprise KL between pre-registered prior P_t(metric) and post-finding posterior P_t+1(metric | finding) correctly recovers user-flagged surprise classification at >=60% precision on retrospective sample. P_deflated=0.55.
HF: <40% precision (means a single-Gaussian prior is too narrow; need hierarchical mixture).

P2 (HARD-PASS-able): Lakatos hard-core / protective-belt separation identifies second-order findings as those that change a previously-frozen capability-class invariant in cap_map (e.g. a finding that flips "substrate-only ceiling on X" status). P_deflated=0.60.
HF: hard-core flips happen <1/month -- means Layer 4 second-order classification has no signal to drive Tier 1->2 progression and a different second-order definition is needed.

P3 (HARD-PASS-able): BOCPD run-length posterior on weekly surprise count produces a stable sustaining-rate estimate within 4-8 weeks of observation. Sustaining = posterior mode of weekly-surprise-rate >=1.0 AND BH-FDR adjusted p-value of "rate>=1.0 vs rate=0" below q=0.1. P_deflated=0.50.
HF: posterior never stabilizes (variance >50% of mean after 8 weeks) -- means the weekly counting window is wrong (too short / too long) and needs scope-specific aggregation.

P4 (HARD-FAIL guard): The adversarial / OOD filter must DROP at least 15% of raw surprises as measurement noise (cap-map metric jitter, evaluator drift, prompt-context effects). If <5% drop, the filter is not working -- the surprise count is contaminated and sustaining-rate is biased high.

P5 (substrate-native viability): Substrate's own representation of prior expectations (the cap_map row's bundled state vector + tier-vector + bet-program vector) plus its posterior after finding ingest gives a substrate-cosine-distance / FHRR-overlap-drop that monotonically tracks the external KL surprise score with Spearman rho >=0.55 on retrospective sample. P_deflated=0.45 (novel-synthesis-cap, this IS the substrate-on-substrate piece).
HF: rho <0.30 -- substrate-native classification fails and we must use an external Bayesian-surprise calculator.

## Layer 4 classification procedure (the deliverable)

### Stage 1: Bayesian-surprise KL classification (Itti-Baldi 2009)

For each finding f arriving at time t:

1. Compute prior P_t(m) over the metric m the finding addresses. The prior is derived from the cap_map row state at t (pre-finding) plus the last K=4-8 measurements of m on that row. Family: Gaussian for continuous metrics, Dirichlet for tier-categorical, Beta for pass/fail-rate.
2. Compute posterior P_t+1(m | f) by Bayesian update with f as evidence.
3. Compute S_KL(f) = KL(P_t+1 || P_t). This is the Itti-Baldi surprise quantity.
4. Classify:
   - S_KL < tau_low -> expected
   - tau_low <= S_KL < tau_high -> surprise
   - S_KL >= tau_high AND finding alters a cap_map hard-core invariant -> second-order

Where tau_low and tau_high are calibrated on the retrospective sample (decisive-test stage). A reasonable initial guess: tau_low = median(S_KL on last 50 findings), tau_high = 90th percentile. Re-calibrate quarterly.

### Stage 2: Lakatos hard-core / protective-belt promotion to second-order

A finding f is second-order if:
- S_KL(f) >= tau_high (high Bayesian surprise), AND
- f changes a previously-frozen cap_map status (e.g. a row flips OPEN -> CLOSED or CLOSED -> OPEN; a Tier flag changes; a "structural" claim is refuted)

Hard-core is the set of substrate capability-class invariants in cap_map status_strategy. Protective belt is the operational hypothesis layer (specific bundle counts, specific HP thresholds, specific runner configs). High-surprise findings in the protective belt are still classified as surprise (not second-order); only hard-core perturbations qualify for second-order.

This is exactly Lakatos's sophisticated-falsification: surprise inside the protective belt is normal research progress; surprise that forces hard-core renegotiation is meta-level. Tier 1->2 gate cares about both, but second-order is the rarer signal.

### Stage 3: Adversarial / OOD filter against measurement noise

Before counting a surprise toward the sustaining-rate, run an adversarial filter:

A. Replication check: for finding f involving metric m on row r, is there >=1 prior measurement of (m, r) within the last K weeks that landed inside the prior's 95% credible interval? If yes, f's surprise candidate is admitted. If no prior measurements, mark as PENDING-REPLICATION (does not count toward sustaining-rate until a re-measurement is made).

B. Evaluator-drift check: was f produced under the same evaluator / scoring rule as the prior measurements? If evaluator changed, the surprise is potentially-spurious; mark NEEDS-CONTROL.

C. Context-shift check: did the substrate undergo a config change (re-binding, codebook swap, new shard split) between the prior and f? If yes, the prior is no longer valid for f; reset prior and mark FILTERED.

Findings surviving A+B+C count as GENUINE surprises and feed Stage 4.

### Stage 4: Sustaining-rate measurement via BOCPD + BH-FDR

Count weekly GENUINE surprises: c_w. Apply Bayesian Online Change-Point Detection (Adams-MacKay 2007) on the time series (c_1, c_2, ...). The BOCPD posterior over run length r_t gives:

- A posterior mean rate lambda_t.
- A posterior probability P(change-point at t).
- A run-length-marginalized predictive distribution for c_{t+1}.

Sustaining-rate criterion (Tier 1->2 gate):
- lambda_t >=1.0 surprises/week (posterior mean over the last 4 weeks),
- BH-FDR-adjusted p(rate<1.0) < q=0.10 on those 4 weeks,
- AND no change-point detected in the last 4 weeks (P(change-point) < 0.20 throughout).

The BH correction is for the multiple weeks we're testing. Conservative q=0.10. Tighter q makes the gate harder to clear.

Reason for BOCPD over plain CUSUM: BOCPD gives uncertainty quantification on the rate, and explicitly handles the case where the substrate enters a new regime (change-point) -- exactly what we want for self-evaluation. CUSUM is point-estimate; BOCPD is distributional.

## Pre-registered hypothesis template (substrate-self-evaluation cycle)

Each cap_map self-evaluation cycle writes a pre-reg file before any new measurement. Template:

```
# Pre-registered self-evaluation cycle <N>

date: <ISO>
cycle: <N>
rows-under-eval: <list of cap_map row ids>

## Priors (frozen at cycle start)
For each (row, metric):
  prior_family: <Gaussian|Beta|Dirichlet>
  prior_params: <mu, sigma | a, b | alphas>
  derivation: <last K=? measurements + rationale>
  hard_core_status: <bool: does this metric back a cap_map invariant?>

## Predicted findings (3-5 numbered)
For each:
  prediction_text: <1 line>
  expected_metric_range: <[lo, hi]>
  HARD-PASS: <quantitative criterion>
  HARD-FAIL: <quantitative criterion>
  classification_if_HP: <expected | surprise | second-order>
  classification_if_HF: <expected | surprise | second-order>

## Stage 3 filter contracts
  evaluator_locked: <hash/path>
  config_frozen_at: <git SHA>
  re-measurement_required_before_surprise: <bool>

## Sustaining-rate state
  weeks_observed: <int>
  lambda_t_prior: <float>
  BOCPD_window: <weeks>

## Adjudication date
  <when this cycle's findings will be classified>
```

This template plugs directly into existing routing-file convention (notes/strategy_request_to_*) -- it lives as `notes/self_eval_pre_reg_cycle_<N>.md`. Layer 4 reads the pre-reg, then classifies actual findings against it.

## Substrate-native implementation (the substrate-on-substrate piece)

Key insight: substrate already encodes priors and posteriors as bundle vectors. The substrate-cosine between (cap_map_row_state_t bundled with metric_t) and (cap_map_row_state_t+1 bundled with metric_t+1) gives a substrate-native scalar that should correlate with KL surprise.

Concrete ~30-line numpy primitive:

```python
def substrate_native_surprise(prior_bundle, finding_bundle, posterior_bundle):
    """
    prior_bundle: HRR/FHRR vector encoding the cap_map row + metric prior
    finding_bundle: HRR/FHRR vector encoding the finding
    posterior_bundle: HRR/FHRR vector encoding the row + metric posterior after finding
    Returns: (s_substrate, classification_hint)
    """
    # Substrate KL-analog: 1 - cosine(prior, posterior)
    cos_pp = np.dot(prior_bundle, posterior_bundle) / (
        np.linalg.norm(prior_bundle) * np.linalg.norm(posterior_bundle))
    s_substrate = 1.0 - cos_pp

    # Finding-overlap with prior: low overlap = surprising under prior
    cos_pf = np.dot(prior_bundle, finding_bundle) / (
        np.linalg.norm(prior_bundle) * np.linalg.norm(finding_bundle))
    finding_unexpectedness = 1.0 - cos_pf

    # Combined score
    score = 0.5 * s_substrate + 0.5 * finding_unexpectedness

    if score < TAU_LOW:
        return score, "expected"
    elif score < TAU_HIGH:
        return score, "surprise"
    else:
        return score, "second-order-candidate"  # promotion needs hard-core check
```

TAU_LOW, TAU_HIGH calibrated on the retrospective sample. This is the substrate USING ITS OWN ALGEBRA for self-classification. The external Bayesian-KL is run in parallel as ground truth during calibration; once Spearman rho >=0.55 is shown on retrospective, substrate-native is sufficient for routine classification and external-KL becomes a periodic-audit check (quarterly).

## Sustaining-rate criterion (concrete)

Tier 1->2 GATE PASSES when ALL of:
1. lambda_t (BOCPD posterior mean weekly genuine-surprise rate over last 4 weeks) >=1.0
2. BH-FDR-adjusted p-value of (lambda_t >=1.0 vs lambda_t=0) below q=0.10 on each of last 4 weeks
3. P(change-point in last 4 weeks) <0.20
4. At least 1 second-order finding (Stage 2 hard-core perturbation) in last 8 weeks
5. The Stage 3 OOD filter is dropping at least 15% of raw surprises (proves the filter is alive and not a rubber stamp)

Conditions 1-3 give a statistically-supported sustaining-rate of >=1/week. Condition 4 ensures the system is producing meta-level findings (not just protective-belt churn). Condition 5 ensures the rate is not inflated by noise admission.

ROLLBACK CONDITION: if lambda_t drops <0.5 for 2 consecutive weeks, Tier 1->2 status is revoked.

## Cross-thread synthesis

This drill connects to:
- substrate-self-index v2 architecture drill (research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11.md) -- the substrate-native classifier of Stage 1+3 uses the SAME orthogonal-subspace block-diagonal representation that v2 retrieval uses. Single algebra path serves both retrieval and self-classification.
- substrate-memory + LLM-frontend hybrid drill (research_drill_substrate_memory_llm_frontend_hybrid_2x_2026-06-11.md) -- the conformal-margin routing from that drill is the same family as Stage 3's OOD adversarial filter. The substrate's calibrated-abstention machinery serves BOTH external-query routing and internal-finding filtering.
- categorical AI / DisCoCat drill (research_drill_categorical_ai_discocat_2x_2026-06-11.md) -- the dagger-compact-closed functor framing supports Layer 4 because second-order findings (hard-core flips) are exactly functorial changes (the codomain category gets re-typed). The same algebraic surface explains why second-order is rarer.
- Substrate-classical NLP methods outperform phasor (memory 2026-06-11) -- this empirical pattern is itself a candidate for Layer 4 retrospective testing: was it user-flagged "surprising"? If yes, the classifier should recover it as surprise + hard-core-altering -> second-order.

## Substrate-product implications

Layer 4 dialectic methodology is a PRODUCT FEATURE not just an internal tool:
- "Substrate evaluates its own findings and tells you which are routine, which are surprising, which alter our beliefs." This is calibrated-abstention applied to introspection. No vector DB does this.
- Marketing claim ("substrate has a metacognitive layer that classifies its own emergent properties") becomes defensible because there is a concrete classifier with KL-grounded math and BH-FDR-grounded sustaining-rate.
- Customer use case: a substrate deployed at a customer site can self-report "we had 3 surprises this week, 0 second-order; no Tier-progression event" -- audit-trail-grade introspection.
- Engineering: ~80-line Stage 1 + ~50-line Stage 3 + ~40-line BOCPD wrapper. 4-6 engineering days for a v1 ship.
- Self-test contract: the retrospective decisive test (above) IS the self-test. Re-run quarterly with the latest 8 weeks of findings.

## Implementation cost

- Substrate-native classifier prototype: 1 day (80 lines numpy, BOCPD wrapper from scipy or 40-line custom impl).
- Retrospective decisive test: 1 day (load 8 weeks of cap_map history, hand-judge ~25-50 findings, score, BH-correct).
- Calibration of tau_low / tau_high / Stage 3 thresholds: 1 day.
- Integration with self-eval cycle routing files: 1 day.
- Documentation + pre-reg template polish: 0.5 day.
Total: 4-5 engineering days. CPU-only. No new infra.

## Citations (verified count: 15)

1. Itti L, Baldi P. (2009) "Bayesian surprise attracts human attention." Vision Research. ilab.usc.edu/publications/doc/Itti_Baldi09vr.pdf
2. Itti L, Baldi P. (2006) "Bayesian Surprise Attracts Human Attention." NIPS. ilab.usc.edu/publications/doc/Itti_Baldi06nips.pdf
3. Adams RP, MacKay DJC. (2007) "Bayesian Online Changepoint Detection." arXiv:0710.3742.
4. Benjamini Y, Hochberg Y. (1995) "Controlling the False Discovery Rate." J. Royal Statistical Society B.
5. Popper K. (1959) "The Logic of Scientific Discovery." (falsifiability criterion)
6. Lakatos I. (1970) "Falsification and the Methodology of Scientific Research Programmes." (hard-core / protective-belt)
7. Friston K. (2010) "The free-energy principle: a unified brain theory?" Nature Reviews Neuroscience.
8. Page ES. (1954) "Continuous inspection schemes." Biometrika. (CUSUM)
9. Open Science Framework preregistration templates. cos.io
10. Brier GW. (1950) "Verification of forecasts expressed in terms of probability." Monthly Weather Review.
11. Frontiers in Psychiatry (2025) -- predictive coding mechanistic framework.
12. PMC -- "Self-Evaluation of Decision-Making: A General Bayesian Framework for Metacognitive Computation." pmc.ncbi.nlm.nih.gov/articles/PMC5178868
13. Storey JD. (2002) q-value FDR procedure.
14. arXiv 2305.07733 -- "Measuring Surprise in the Wild."
15. arXiv 2103.06944 -- "Preregistering NLP Research."

## P_deflated derivation

- Lit-scan raw P (would the Itti-Baldi + BOCPD + BH-FDR + Lakatos stack reasonably classify findings into 3 buckets at a useful precision): 0.75
- Calibration penalty (substrate-self-evaluation is an uncharted regime): -0.20
- Substrate-native subset (P5) is novel-synthesis, capped at 0.50 within the stack
- Combined P_deflated: 0.55 for the methodology delivery; P5 alone at 0.45.

## Next-drill candidate

Free-probability F4 (Voiculescu kappa_n free cumulants) from field-advisor -- gives a higher-order moments characterization of the prior P(metric) family that may sharpen Stage 1's prior choice for substrate-internal metrics with heavy tails (the current Gaussian/Beta/Dirichlet families assume light tails).
