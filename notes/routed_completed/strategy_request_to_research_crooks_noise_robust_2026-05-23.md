# Strategy -> Research: 2x drill on noise-robust verifiable erasure -- Cap 1 envelope narrows to clean substrate (cycle 177 v157)

**Sender**: Strategy session (session 1)
**Recipient**: Research session (session 4)
**Date**: 2026-05-23 ~11:58 EDT
**Topic**: Cap 1 Crooks forensic erase envelope under bit-flip noise narrows to clean operating point at FULL -- what protective mechanisms exist for fluctuation-theorem-bounded verifiable erasure under noise?
**cap_map state**: v157 (this cycle)
**User directive**: 2x drill on negative result per [[feedback-rehabilitation-after-rejection]] + [[feedback-negative-results-2x-research]] (measurement-based refutation under harsher conditions triggers 2x research drill; OOM-INCONCLUSIVE exclusion does NOT apply -- 29.2s clean measurement, n_seeds=3, 50-trial).

---

## Context -- cycle 177 envelope-narrowing under bit-flip noise

`wave14_crooks_noise_envelope_v1` FULL verdict
`CROOKS_NOISE_ENVELOPE_KILL` at 29.2s elapsed.

Cycle 173 v153 verified Cap 1 Crooks forensic erase at FULL on a clean
substrate (delta_S_emp = 0.0000 at default noise level). Cycle 176 v156
queued an envelope-expansion probe under bit-flip noise during the
erase trajectory at N=16384, M_base=200, 50 trials per cell, 3 seeds,
noise levels p in {0.05, 0.10, 0.20} + baseline p=0.

Outcome at FULL:

| Cell | delta_S_emp | Pass / Fail |
|---|---|---|
| p=0 (baseline) | 0.0000 | PASS (re-confirms clean Cap 1 ✅) |
| p=0.05 (light) | >= 0.05 | FAIL Crooks-FT bound |
| p=0.10 (moderate) | >= 0.05 | FAIL Crooks-FT bound |
| p=0.20 (heavy) | >= 0.05 | FAIL Crooks-FT bound |

3 of 3 noise cells fail the delta_S_emp < 0.05 bound. The verifiable
Crooks-FT bound holds at the clean operating point but does NOT extend
to realistic bit-flip noise during the erase trajectory. Cap 1
commercial wedge framing narrows to clean operating point.

## The puzzle

**Substrate-product paradox**:
- ✅ Verifiable forensic erase via Crooks fluctuation theorem at the
  clean operating point (cycle 173 + cycle 177 baseline re-confirm)
- ❌ Same bound breaks at bit-flip noise p as low as 0.05 during the
  erase trajectory

In statistical mechanics, the Crooks fluctuation theorem bounds
information erasure via the forward-reverse trajectory ratio; published
work on noise-robust verifiable erasure typically assumes either
specific noise models (Gaussian, dephasing) or specific protective
mechanisms (error-correction, redundant encoding, denoising). The
substrate's failure under simple bit-flip noise suggests the
unconditional Crooks-FT audit needs a protective layer to operate
under realistic perturbation.

## Question for Research

**Generic-math framing** per [[feedback-query-privacy-decomposition]]
(do NOT use substrate-specific configuration / mechanism names in
public queries):

What protective mechanisms in classical associative memory / structured
codebook systems extend a fluctuation-theorem-bounded information-
erasure audit (Crooks-style forward-reverse trajectory ratio) to hold
under bit-flip noise applied during the erasure trajectory?

Specifically:

1. **Redundancy-based protection**: r-fold replication of the
   information being erased; majority-vote or median audit across the
   r copies. What's the theoretical bit-flip noise tolerance vs r?
   Is there a published threshold theorem (Crooks-FT under
   stochastic perturbation analogous to Shannon channel capacity)?
2. **Closed-loop verification**: read-after-erase audit; iterative
   correction. What's the convergence behavior / failure-mode
   characterization under continuous noise during the audit loop?
   Connects to fault-tolerant quantum erasure literature
   (Knill-Laflamme codes, etc.) but with classical bit-flip noise.
3. **Pre-erasure denoising**: signal-processing filter applied to the
   storage substrate before the erase step. What filters preserve the
   forward-reverse trajectory invariance the Crooks-FT audit requires?
   (Median filter, Walsh-Hadamard sparsification, low-rank projection
   are candidate filters; do they break or preserve the FT bound?)
4. **Algebraic error-correction at binding layer**: noise-protected
   binding algebras for the keys used in the anti-Hebbian erase step.
   BCH-coded keys + soft-decoding step OR FHRR circular-correlation
   with continuous phase damping. Do error-corrected binding algebras
   preserve the Crooks-FT trajectory invariance?
5. **Lower-noise operating envelope characterization**: what's the
   empirical / theoretical noise floor where the unprotected Crooks-FT
   audit still holds (extrapolating from the cycle 177 FULL data:
   bound breaks at p >= 0.05; where does it break first)? Connects
   to standard SNR analysis of associative memory but conditioned on
   the FT-bound metric.

## Strategy's 5 unvetted rescue sketches (filed for context only)

These are pre-armed per PROT-004/006 rehab discipline; Research's 2x
drill will produce the vetted ranking, NOT vet a Strategy-drafted list.

1. Redundant erase encoding (r >= 3 copies; majority-vote audit).
2. Post-erase verification + retry (closed-loop iterative correction).
3. Lower-noise operating envelope + SLA on noise floor.
4. Pre-erase denoising filter (median / WHT-sparse / low-rank).
5. Code-based protected erase (BCH or FHRR binding-algebra
   error-correction).

Per [[feedback-unbiased-research]]: pass 1 surveys broadly (what does
noise-robust fluctuation-theorem-bounded information erasure look like
in the published literature?); pass 2 drills substrate-compatible
mappings (which mechanisms map onto the clean-substrate Cap 1 protocol
at N=16384?). Do NOT pre-filter to "AI / VSA" framings -- broad
statistical-mechanics + information-theory literature is the canonical
home for this question.

## Lit-scan calibration

Per [[feedback-lit-scan-calibration-penalty]]: deflate agent P
estimates by 0.15-0.25 if the regime is uncharted (noise-robust
Crooks-FT bounds in classical associative memory specifically). Cap
novel-synthesis P at 0.50. Include explicit hard-fail thresholds in
falsifiable predictions for any candidate mechanism (e.g., "Mechanism
M is predicted to preserve delta_S_emp < 0.05 at p <= X; if FULL
measurement shows delta_S_emp >= 0.05 at p < X/2 the mechanism is
falsified").

Per [[feedback-dont-dismiss-adjacent-methods]]: classical-bit-flip
fault-tolerance + redundant-encoding + stochastic-thermodynamics
forward-reverse audits are ALL adjacent methods. Dispatch lit-scan
agents on each; do NOT pre-judge "this is just error-correction
literature, not Crooks-FT literature."

Per [[feedback-subagent-model-optimization]]: default lit-scan
subagents to Sonnet (not Opus); reserve Opus for main-thread synthesis
of the 5-sketch vetted ranking.

## Deliverable

`notes/research_crooks_noise_robust_<date>.md` with:

1. Pass 1 broad survey: noise-robust fluctuation-theorem-bounded
   information erasure in published literature. Spin-glass / Hopfield
   / VSA / associative-memory + classical thermodynamics + fault-
   tolerant computing literature.
2. Pass 2 substrate-compatible drill: which mechanisms map onto the
   cycle 173 v153 Cap 1 protocol (Hadamard bind WRITE + anti-Hebbian
   ERASE + log-ratio AUDIT) at N=16384? Rank the 5 Strategy sketches
   + any additional mechanisms found in pass 1.
3. For each candidate mechanism: substrate-compatible protocol sketch +
   falsifiable prediction (noise tolerance threshold) + cost estimate
   (M-budget, N-budget, latency).
4. Vetted top-3 ranked candidates with explicit P estimates (deflated
   per [[feedback-lit-scan-calibration-penalty]]).

## Strategy preference for sequencing

Research's vetted ranking will inform a Strategy -> Exp Dev request to
queue the top-ranked rescue at FULL. Strategy preference today:
mechanisms #1 (redundant encoding) and #2 (post-erase verification)
are likely the cheapest to operationalize at the existing N=16384
protocol; mechanisms #4 (denoising) and #5 (algebraic error-correction)
require more substantive build. Research is free to overrule this
preference if the literature supports a different ranking.

## Cross-references

- cap_map v157 narrative section "Five axis-combination rescue
  sketches for noise-robust Crooks erase".
- cap_map v153 narrative (cycle 173) where Cap 1 was promoted to
  COMMERCIAL WEDGE at FULL on the clean substrate.
- cap_map v156 narrative (cycle 176) where the envelope-expansion
  probe was queued.
- `notes/strategy_request_to_exp_dev_crooks_noise_envelope_v1_2026-05-23.md`
  (the Exp Dev request that produced this verdict).
- `notes/strategy_decisions_2026-05-23.md` cycle 177 entry (paired
  decision log).

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
