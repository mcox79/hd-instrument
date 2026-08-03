# Skunkworks fairness-VET: v2 event-predictor HARD_FAIL (commit 9b9781fda) -- AUDIT-ONLY, adversarial

Target: `experiments/exp_event_level_prediction_error_relation_inference_phase1_v2_associative.py`
+ `data/exp_event_level_prediction_error_relation_inference_phase1_v2_associative/metrics.json`
(TOP_VERDICT=MECHANISM_HARD_FAIL, stage_b_pass=false).

Task: try hard to REFUTE the HARD_FAIL as an artifact of an unfair/handicapped/ill-posed test.
All numbers below are independently recomputed off `metrics.json`'s per-pair records (NOT
read from `verdict_msg`/`summary_fields` alone) via `.venv` Python.

## Recompute verification (sanity)
Re-derived retrieval_accuracy per arm directly from the 4 x 3222 per-pair record blocks:
TRAINED=0.107698, RANDOM_INIT=0.083799, PREDICT_MEAN=0.098386, COPY_CONTEXT=0.118870 --
bit-identical to the file's summary numbers. Pair ordering (novel, true_idx) is identical
across all 4 arms (verified), and `n_negatives_sampled` is uniformly 9 for all 3222 x 4
records -- negative sampling is NOT arm-dependent (same `seed_base + pair_index` call for
every arm, confirmed also by direct code read of `score_retrieval`/`sample_negatives`), so
there is no asymmetric-negatives bug.

## Fairness checks (adversarial, in order of the audit brief)

1. **Context starvation (window=1):** BOTH the trained arm and the copy-context baseline see
   the identical single preceding event -- this is a *level* handicap, not asymmetric. copy
   does not "cheat" with more context than trained. Ruled out as a fairness threat.

2. **Undertraining:** loss curve (`train_curve_sampled`) plateaus hard: 0.6543 (epoch 0) ->
   0.3479 (epoch 40) -> 0.3326 (epoch 120) -> 0.3276 (epoch 299), i.e. <0.5% relative change
   over the last 180 epochs. Converged, not a SGNS-style undertrained strawman.

3. **Segmentation-artifact / near-duplicate-copy hypothesis (adversarial probe, DID NOT
   PAN OUT):** hypothesized copy-context's edge might come from naive-sentence-split
   fragments creating literal near-duplicate consecutive "events" (e.g. split dialogue
   tags). Measured: only 1 of 3222 test pairs has copy true_overlap > 0.95 (near-duplicate).
   Excluding that single pair changes copy's accuracy from 0.1189 to 0.1186 -- negligible.
   **Refuted:** copy's advantage is NOT a segmentation-duplication artifact.

4. **Statistical significance of margin_vs_copy:** McNemar (paired, continuity-corrected) on
   trained-vs-copy per-pair correctness: both_right=97, both_wrong=2589, trained_only=250,
   copy_only=286, chi2=2.285 (not significant at p<0.05, needs >3.84). So "trained LOSES to
   copy" is technically a non-significant tie at this N, even though it fails the
   pre-registered 0.05-absolute-margin gate. This nuance does NOT save Stage B, however:
   margin_vs_random (+0.024) and margin_vs_mean (+0.0093) are BOTH also well under the 0.05
   bar and positive-but-small, so the gate fails independent of the copy-specific tie.

5. **Margin-bar stringency vs N:** binomial SE at N=3222, p~0.10 is 0.0053, so the
   pre-registered 0.05 margin is ~9.5 SE -- a demonstrably conservative, not unfairly strict,
   bar given the ACTUAL N (the pre-reg's own justification assumed "a few hundred" test
   pairs; actual N is ~10x that, meaning the bar is if anything MORE conservative than the
   authors intended, not a rigged high bar). Ruled out as a fairness threat.

6. **THE SUBSTANTIVE FINDING (capacity question, 1c):** per-pair true_overlap profiles are
   highly correlated between TRAINED and PREDICT_MEAN (Pearson r=0.906, n=3222), and much
   less correlated with COPY_CONTEXT (r=0.497) or RANDOM_INIT (r=0.021). The trained
   delta-rule-optimized linear map has effectively collapsed toward outputting something
   close to the corpus mean, largely independent of its per-example input context -- this
   is the SAME mean-reversion failure mode the v1 disqualification (commit d03178c75) found,
   recurring in a new guise despite the retrieval-metric fix (which was designed to make
   predict-mean incapable of directly WINNING the gate -- it succeeds at that narrow goal;
   it does not stop the TRAINED arm's own optimization from converging near mean-like
   output). Critically, this is **not evidence that a linear map lacks the capacity** to
   match copy: W=identity is itself a valid point in the linear hypothesis class and would
   trivially reproduce copy-context's accuracy. The recompute shows gradient descent under
   MSE+L2=1e-4 does not converge there because, given the corpus's actual (weak) event-to-
   event autocorrelation, mean-shrinkage genuinely minimizes MSE better than identity does --
   a well-known property of L2-regularized regression under a low signal-to-noise ratio, not
   a bug and not a capacity ceiling. The mismatch is **between the TRAINING OBJECTIVE (MSE
   regression to a continuous point target) and the EVALUATION OBJECTIVE (retrieval-ranking
   against distractors)** -- these are not the same optimization target, and MSE-optimal
   solutions are not retrieval-optimal solutions when SNR is low.

## VERDICT

**FAIR test AS EXECUTED for the exact recipe it tests** (MSE/delta-rule-trained linear map,
scored via top-1 retrieval against 3 non-learned baselines): no context-window asymmetry,
no undertraining, no negative-sampling bug, no segmentation-duplication artifact inflating
copy, and a margin bar that is conservative-but-legitimate given the achieved N. The negative
is NOT refuted by any of the adversarial probes above -- **HARD_FAIL stands** for this
specific (encoding, training-rule, evaluation-metric) triple. `verified_off_data=True`
(independent recompute from per-pair records, not from `verdict_msg`).

**Single biggest fairness/validity threat identified (does not overturn the verdict, but
should redirect revival):** the cell's own pre-registered revival criteria ((a) nonlinear
MLP, (b) richer multi-event context) target the WRONG lever. The recompute evidence
(trained-vs-mean correlation 0.906) points at a **training-objective/evaluation-objective
mismatch** (MSE regression vs retrieval-ranking), not a capacity ceiling -- a nonlinear
model trained the same MSE way would very plausibly mean-collapse identically, since
mean-shrinkage under low SNR is a property of the LOSS, not of model linearity.

**Recommended FAIR re-test (if this arc is revived):** train the predictor with a
discriminative/contrastive objective consistent with the eval metric itself (e.g. a
margin/triplet loss pushing the predicted-next-event's overlap with the TRUE target above
its overlap with sampled same-novel negatives, the same negatives already used at eval
time) rather than MSE-to-a-point-target -- OR initialize/regularize the linear map toward
identity (small L2, or explicit skip-connection W=I+dW) so gradient descent is not
structurally biased toward the mean-collapsing solution. Context-window expansion and
nonlinearity (the currently-listed revival criteria) are unlikely to fix this specific
failure mode on their own and should be deprioritized relative to the objective-mismatch fix.

AUDIT-ONLY. No cells authored or dispatched. Recompute scripts used for this VET are
scratch/session-local, not committed (only this note + its Store implications, if any,
belong in the repo).
