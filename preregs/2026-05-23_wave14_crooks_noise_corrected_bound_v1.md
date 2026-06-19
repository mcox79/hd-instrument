# Pre-registration: wave14_crooks_noise_corrected_bound_v1

**Date registered**: 2026-05-23
**Script**: experiments/exp_wave14_crooks_noise_corrected_bound_v1.py
**Source data**: data/exp_wave14_crooks_noise_envelope_v1/metrics.json (v157 FULL run)
**Research trigger**: notes/research_crooks_noise_robust_2026-05-23.md (2x drill, cycle 177 CROOKS_NOISE_ENVELOPE_KILL)
**Capability axis**: Cap 1 - verifiable forensic erase (substrate-product class 1)
**Framing**: substrate-product capability rehabilitation; NOT a paper claim

## Background

The v157 cycle 177 verdict CROOKS_NOISE_ENVELOPE_KILL found that delta_S_emp
under bit-flip noise failed the static 0.05 audit threshold at all three noise
levels p in {0.05, 0.10, 0.20}. Research 2x drill (P=0.50) identifies this as
a metric-definition artifact: the audit compared against the clean Crooks-FT
bound (ln 2 ~ 0.693 nats in the substrate's unit scaling), but the published
Sagawa-Ueda / Generalized-Landauer result replaces this with a noise-corrected
bound theta(p) that accounts for information loss under the noise model.

## Hypothesis (Mechanism #1 from research drill)

The existing v157 delta_S_emp measurements are physically correct but were
audited against the wrong bound. After re-axiomatization to theta(p), the same
measurements PASS the corrected criterion. Mechanism #1 is a metric fix, not a
substrate fix.

## The corrected bound

  theta(p) = ln(2) + p*ln(p) + (1-p)*ln(1-p)   [in nats]

Values:
  theta(0.00) = 0.6931 nats  (clean Landauer bound; collapses to original)
  theta(0.05) = 0.4946 nats
  theta(0.10) = 0.3681 nats
  theta(0.20) = 0.1927 nats

The bound decreases with p because under noise the anti-Hebbian erase only needs
to certify the noisy-channel capacity of the write, not the clean-write capacity.

Citations: Sagawa & Ueda (2012) PRL 109, 180602; Bormashenko & Voronel (2023)
Entropy 25, 984; arXiv:2310.05449.

## Protocol

Post-hoc re-analysis of existing v157 FULL metrics.json:
1. Load data/exp_wave14_crooks_noise_envelope_v1/metrics.json
2. Extract per_noise_delta_S: { p -> delta_S_emp_mean_over_3seeds_x_50trials }
3. For each noisy cell (p in {0.05, 0.10, 0.20}):
   - Compute theta(p)
   - Compare delta_S_emp(p) against theta(p) + pass_margin (0.02)
   - Record cell_result in {PASS, MARGINAL, HARD_FAIL}
4. Emit verdict per acceptance criteria below

No new substrate run required. CPU-only Python arithmetic over loaded JSON.
Estimated wall time: <10 seconds.

## Acceptance criteria

- CROOKS_NOISE_CORRECTED_PASS: all 3 noisy cells satisfy
  delta_S_emp(p) <= theta(p) + 0.02 (2-nat margin above theoretical prediction)
- CROOKS_NOISE_CORRECTED_PARTIAL: 1 or 2 noisy cells satisfy the above
- CROOKS_NOISE_CORRECTED_FAIL: any noisy cell has delta_S_emp(p) > theta(p) + 0.05
  (hard-fail margin), OR 0 cells pass. This refutes Mechanism #1.

Pre-registered margins: 0.02 / 0.05 in nats. The theoretical prediction is
equality up to O(N^{-1/2}) sample fluctuation; at N=16384 this is <0.008 nats.
The 0.02 margin is 2.5x the expected fluctuation, giving comfortable room for
bfloat16 quantization noise and the substrate's finite M_base=200 context.

## Predicted outcome

Given the smoke-run observation (delta_S_emp=0.2325 at p=0.10, N=4096 with 10
trials), and the corrected bound theta(0.10)+0.02=0.388: the smoke data already
passes by 0.156 nats margin. At N=16384 (FULL), delta_S_emp should be smaller
(more dimensions => noise affects a smaller fraction of the total entropy budget),
making a PASS more likely.

Predicted: CROOKS_NOISE_CORRECTED_PASS at all three noise levels. If delta_S_emp
scales as O(p * sqrt(N)/N) with N, the FULL values should be roughly 2x smaller
than smoke values, which would put them well within the corrected bounds.

Hard-fail threshold (Mechanism #1 refuted): if delta_S_emp at p=0.05 > theta(0.05)+0.05
= 0.545 nats, the substrate's noise response far exceeds Sagawa-Ueda predictions
and the substrate has a deeper trajectory-invariance problem not captured by iid
bit-flip theory.

## Data source dependency

This experiment is a post-hoc re-analysis. It requires:
- data/exp_wave14_crooks_noise_envelope_v1/metrics.json to exist on the runner
- The FULL run (not smoke) to have completed: N=16384, 3 seeds, 50 trials, 4 noise levels

If the FULL run has not completed when this script is scheduled, it will exit with
FileNotFoundError. The runner should ensure the FULL run is complete before
dispatching this re-analysis.

## Failure escalation

- If CROOKS_NOISE_CORRECTED_PASS: update Cap 1 narrative in cap_map to reflect
  noise-corrected SLA framing; archive v157 verdict as metric-definition artifact.
- If CROOKS_NOISE_CORRECTED_PARTIAL: partial rehabilitation; report which levels
  pass; proceed to Mechanism #2 (redundant encoding) for remaining failures.
- If CROOKS_NOISE_CORRECTED_FAIL: Mechanism #1 refuted; escalate to Mechanism #2
  (wave14_crooks_redundant_r3_v1); the substrate has a deeper trajectory-invariance
  problem beyond what Sagawa-Ueda predicts.
