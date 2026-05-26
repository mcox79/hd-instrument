# Pre-reg: Wave 14 Bet Z.3 VAMP Single-Hop at N=4096 v1

**Filed:** 2026-05-22
**Source:** `strategy_request_to_exp_dev_post_v127_batch_2026-05-22.md` (Strategy 20:14 EDT) — Priority 5.

## Question

Does VAMP-class single-hop readout (softmax-weighted superposition + argmax) outperform argmax-only cleanup at N=4096 with Kerdock 4-coset codebook under Hamming-perturbed (p=0.10) queries, for K up to 2000?

Background: cycle 115 Research said VAMP+SVD PROVEN P=0.90 for RI matrices. Cycle 120 Kerdock-RI universality KILLED forces fallback to VAMP P1. Need empirical single-hop validation before VAMP-on-chain claims are bound to substrate-product.

## Hypothesis

H_pass: VAMP-class > argmax by ≥10pp recall at intermediate K (substrate-novel readout primitive).

H_kill: VAMP-class < argmax by 5pp+ (substrate's argmax is the better single-hop cleanup).

## Pre-declared verdicts

- `BET_Z3_VAMP_PASS` — VAMP > argmax by ≥0.10.
- `BET_Z3_VAMP_PARTIAL` — |VAMP − argmax| < 0.05.
- `BET_Z3_VAMP_KILLED` — VAMP < argmax by 0.05+.
- `BET_Z3_VAMP_INCONCLUSIVE` — metric collection error.

## Method

For each K ∈ {200, 500, 1000, 2000}:
1. Draw K random Kerdock 4-coset codewords as patterns.
2. For each trial: pick target = patterns[i]; perturb p=0.10 bit-flip → noisy.
3. argmax recovery: pred = argmax(patterns @ noisy).
4. VAMP recovery: softmax(patterns @ noisy) → weighted state; argmax(patterns @ state).
5. Recall = mean correct over 200 trials.

## Acceptance thresholds

- 0.10 PASS gap matches Strategy's "10pp lift" benchmark.
- 0.05 KILL gap = "real underperformance".

## Config

- N=1024 smoke, 4096 full.
- K_grid full: [200, 500, 1000, 2000].
- noise_p = 0.10.
- n_trials = 200 full.
- Single seed=17.

## Pre-declared interpretation

- **PASS**: substrate-novel VAMP-class single-hop readout primitive PROVEN at N=4096. Bet Z.3 single-hop = Tier-1 capability. Couples to VAMP-on-chain.
- **PARTIAL**: VAMP matches argmax — single-hop substrate is already at argmax limit. VAMP-on-chain win was a multi-hop-specific artifact.
- **KILL**: VAMP underperforms argmax for single-hop. Restrict VAMP claim to multi-hop only.

## Not in scope

- Iterative VAMP (single-pass).
- Sparse-prior denoiser (uniform softmax).
- Multi-hop (covered separately).
