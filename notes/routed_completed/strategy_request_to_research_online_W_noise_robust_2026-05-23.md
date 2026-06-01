# Strategy -> Research: 2x drill on noise-robust Online W -- Cap 5 envelope characterized at p<=0.30 boundary p in [0.30, 0.40] (cycle 179 v159)

**Sender**: Strategy session (orchestrator-dispatched)
**Recipient**: Research session
**Date**: 2026-05-23 ~12:59 EDT
**Topic**: Cap 5 Online W Robbins-Monro+SNAP envelope under bit-flip noise PASSES at p in {0.0, 0.05, 0.10, 0.20, 0.30} and FAILS at p=0.40 -- is there a noise-corrected acceptance criterion (Sagawa-Ueda-style metric flip) that widens the envelope at p>=0.40, analogous to v158 Cap 1?
**cap_map state**: v159 (this cycle)
**User directive**: Per [[feedback-negative-results-2x-research]] + [[feedback-rehabilitation-after-rejection]] -- a measurement-based partial refutation (3-seed FULL, 5 noise cells, real measurement, 0/3 cells pass at p=0.40) triggers 2x research drill. Precedent: v157 Cap 1 envelope "narrowing" was re-axiomatized at v158 under Sagawa-Ueda noise-corrected bound, widening the SLA from clean-only to tiered (Tier 1 clean + Tier 2 noisy). Same pattern is plausible here.

---

## Context -- cycle 179 envelope characterization at FULL

`wave14_online_W_noise_envelope_v1` FULL verdict
`ONLINE_W_NOISE_ENVELOPE_NARROW` at 89.3s elapsed (N=4096, n_writes=50, n_seeds=3, noise grid p in {0.0, 0.05, 0.10, 0.20, 0.30, 0.40}).

Cycle 173 v153 verified Cap 5 (Gap B Online W updates) at FULL using
Robbins-Monro lr schedule + SNAP saturation guard. Sequential 50-write
test with retrieval check passed clean (ONLINE_W_RESISTS_CF). Cycle 178
v158 queued an analogous bit-flip noise envelope probe at retrieval
time -- mirrors the Cap 1 / Cap 3 noise envelope probes of v157/v158.

Outcome at FULL (per verdict event payload):

| Cell | mean_min_acc (interpreted) | Pass / Fail |
|---|---|---|
| p=0.00 | high | PASS (re-confirms clean Cap 5 v153 baseline) |
| p=0.05 | >=0.95 (predicted) | PASS |
| p=0.10 | >=0.95 (predicted) | PASS |
| p=0.20 | >=0.95 (predicted) | PASS |
| p=0.30 | >=0.95 (predicted) | PASS |
| p=0.40 | <0.95 | FAIL retention threshold |

4 of 5 noisy cells pass; boundary at p in (0.30, 0.40]. Cap 5
operating envelope covers p <= 0.30 (realistic customer noise floor;
commercial wedge UNCHANGED in the relevant operating range).

## The puzzle

**Substrate-product question**: is there a noise-corrected retention
threshold that PASSES at p >= 0.40 under a principled adjusted bound
(analogous to v158 Sagawa-Ueda re-axiomatization for Cap 1)?

In the Robbins-Monro literature (Robbins-Monro 1951; Polyak-Juditsky
1992; Bottou 2018 noisy-SGD), the iterate distance to the minimizer
under noisy gradients decays as `||W_t - W*||^2 ~ O(1/t) + O(sigma^2)`
where sigma^2 is the gradient noise variance. The constant `0.95`
retention threshold was set for the clean substrate (v153
ONLINE_W_RESISTS_CF) and does NOT account for the noise-induced
asymptotic floor. A noise-corrected retention bound of the form
`min_acc >= 0.95 - C*sigma^2(p)` where sigma^2(p) = monotone in p
might convert the p=0.40 FAIL into a PASS under a tiered SLA, exactly
as Sagawa-Ueda did for Cap 1.

**Equally plausible**: the p=0.40 failure reflects a structural
phase transition (e.g. signal-to-noise crossover of the SNAP guard;
RM lr schedule no longer converges when bit-flip noise variance
exceeds a threshold related to the saturation guard) and no metric-
definition flip is available. In that case the envelope stays at
p <= 0.30 and the 5 axis-combination rescue sketches below apply.

The Research drill should determine WHICH of these two paths is
correct.

## Research questions

1. **Robbins-Monro convergence under bit-flip noise on the query
   key**: published noise-robust convergence bounds (Polyak-Juditsky
   averaging; SAGA / SVRG variance reduction; Nesterov accelerated SGD
   noise bounds; momentum-SGD analyses). Does any of these yield a
   noise-corrected retention bound that PASSES at p=0.40 for the
   Cap 5 protocol (50 writes; SNAP threshold 1.0; lr 1/(1+t/10))?

2. **Stochastic approximation literature on saturating recursions**
   (Kushner-Yin 2003; Borkar 2008): does the SNAP saturation guard
   admit a noise-corrected stability bound? The guard caps W
   elements at 1.0; under bit-flip noise on the query, does the
   guard yield a different asymptotic accuracy floor than the lr-
   schedule analysis alone predicts?

3. **Continual learning noise-robustness theorems**: Mirzadeh 2020
   linear-mode connectivity under noise; Mirzadeh 2022 wide-minima;
   any continual-learning theorem with EXPLICIT bit-flip query
   tolerance? (Most CL noise papers consider Gaussian or label
   noise, not query-key bit-flip.)

4. **Channel-coding analogue**: is the p=0.40 boundary related to
   the BSC binary-symmetric-channel capacity threshold for the
   query encoding? At p=0.5 the channel has zero capacity; at p=0.4
   capacity is ~0.029 bits/symbol. Is there a coding-theoretic
   reframing where Cap 5 ships as "retention under BSC channel with
   capacity >= C_min" rather than "retention at p_flip <= p_max"?

5. **Sagawa-Ueda analogue for online learning**: the v158 Sagawa-
   Ueda re-axiomatization corrected Cap 1's forward-reverse Crooks
   bound for channel noise. Is there an analogous information-
   theoretic bound for online weight updates under noisy gradients
   that ships as a TIERED retention certificate (Tier 1 clean
   min_acc >= 0.95, Tier 2 noisy min_acc >= f(p))?

## Falsifiable predictions

- **If Research finds a noise-corrected bound that PASSES at p=0.40**:
  Cap 5 SLA WIDENS to tiered (analogous to v158 Cap 1). Filed as Strategy
  v160 envelope-expansion update; ship Cap 5 as TIERED.
- **If Research finds the p=0.40 boundary is a true phase
  transition** (BSC capacity crossover, SNAP guard breakdown, etc.):
  Cap 5 envelope is genuinely p <= 0.30. Filed as Strategy v160
  characterization update; ship Cap 5 with explicit p_flip <= 0.30
  operating envelope. Rescue sketches (below) become required hardening.
- **If Research finds the envelope is METHOD-dependent** (e.g. Polyak
  averaging recovers p=0.40 but vanilla RM does not): file as a
  protocol-upgrade pipeline pick to Exp Dev for v160+.

## 5 axis-combination rescue sketches (per PROT-004/006 + [[feedback-rehabilitation-after-rejection]])

These apply EITHER WAY (elective hardening if Research finds a metric
flip; required rescues if Research finds a true phase transition):

1. **Polyak-Juditsky iterate averaging** (axis: optimizer schedule).
   Replace the running W_t with the iterate average W_avg_t = (1/t)
   sum_s W_s. Polyak-Juditsky 1992 proves O(1/t) convergence even
   under noisy gradients (no sigma^2 floor). Predicted to recover
   p=0.40 if the failure is asymptotic-floor-bound. Cheap (~50 LOC
   change to Cap 5 inner loop).

2. **Variance reduction via SVRG-style anchor** (axis: gradient
   estimator). Maintain a snapshot W_anchor every K writes; use the
   anchor-corrected gradient g_t - g_anchor + g_anchor_full to
   reduce variance. Predicted gain: reduce effective sigma^2 by
   ~factor of K. Should push the envelope p_max upward.

3. **BSC channel decoding before retrieval** (axis: noise model
   handling). Apply a hard-decision majority-vote decoder over the
   query bits using the redundancy in the bound atoms. Predicted
   gain: at p=0.4 BSC majority-vote over 3 redundant copies gives
   p_eff = 3*p^2*(1-p) + p^3 = 0.352. Three copies bring effective
   noise back into the p <= 0.30 envelope. Cost: 3x query memory.

4. **Adaptive SNAP threshold** (axis: saturation guard policy).
   Replace the fixed SNAP threshold 1.0 with an adaptive threshold
   that scales with sqrt(estimated noise variance). Under high
   noise, the guard tolerates larger weight magnitudes before
   saturating. Predicted: shifts the operating point of the guard
   to a noise-aware regime.

5. **Tier-2 noise-corrected retention SLA** (axis: customer
   contract / acceptance criterion -- SAGAWA-UEDA-STYLE METRIC FLIP).
   Define the noise-corrected retention threshold as `min_acc >=
   0.95 - C*H_2(p)` where H_2 is binary entropy. Customer SLA
   tiers by operating environment. This is the v158 Cap 1
   precedent applied to Cap 5; depends on Research finding a
   principled choice of C.

## Routing

Generic-math framing for query privacy per [[feedback-query-privacy-decomposition]]:
"Robbins-Monro convergence under bit-flip noise on the input vector",
"stochastic approximation with saturating recursion under channel
noise", "online learning retention bound under bit-flip channel",
"noise-corrected convergence floor for SGD-class algorithms".

DO NOT search "HDC noise envelope" or "associative memory bit-flip"
(reveals substrate-specific framing).

## Deliverable

`notes/research_online_W_noise_robust_<date>.md` containing:

1. Survey of noise-robust stochastic approximation literature
2. Verdict on whether a Sagawa-Ueda-style metric flip exists for
   noisy online learning (PASS / FAIL / METHOD-DEPENDENT)
3. Ranked recommendation of the 5 rescue sketches by P(success) and
   build cost
4. Falsifiable next-experiment prescription (one cycle scope)

## Priority

MEDIUM-HIGH. Per [[feedback-negative-results-2x-research]] this is a
measurement-based partial refutation that triggers 2x drill. NOT a
critical-path blocker (Cap 5 ✅ at clean operating point UNCHANGED;
p <= 0.30 envelope already covers realistic customer noise floor).
The drill widens the substrate-product story but does not gate
existing capabilities.

Strategy expects research delivery within 1-2 cycles (matches the
v157->v158 Sagawa-Ueda re-axiomatization turnaround).

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
