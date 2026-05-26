# Pre-reg: Wave 14 Lane D End-to-End N=65536 with VAMP-on-chain v1

**Filed:** 2026-05-22
**Source:** `strategy_request_to_exp_dev_post_v127_batch_2026-05-22.md` (Strategy 20:14 EDT) — Priority 1: Demo 1 demonstration.

## Question

Does the full Lane D cognitive-architecture pipeline (U → S → T → X) compose at N=65536 with VAMP-class softmax-cleanup readout at Stage S, sustaining composed_acc ≥ 0.50?

Cycle 105 demonstrated composed_acc=1.000 at N=4096 with argmax cleanup. Cycle 127 demonstrated VAMP-on-chain restores multi-hop at N=65536. This integration test verifies Demo 1 (Lane D agent memory SDK) substrate-product story at full N=65536 + new readout layer.

## Hypothesis

H_pass: composed_acc ≥ 0.50 at N=65536. Lane D pipeline integrates cleanly with VAMP-class readout.

H_killed: composed_acc < 0.25 — chained failures at N=65536 collapse the pipeline.

## Pre-declared verdicts

- `LANE_D_E2E_N65K_PASS` — composed_acc ≥ 0.50.
- `LANE_D_E2E_N65K_PARTIAL` — 0.25 ≤ composed_acc < 0.50.
- `LANE_D_E2E_N65K_KILLED` — composed_acc < 0.25.
- `LANE_D_E2E_N65K_INCONCLUSIVE` — metric collection error.

## Method

Same as cycle 105 Lane D end-to-end but:
- N=65536 (was 4096)
- Stage S cleanup uses VAMP-class softmax-weighted state-then-argmax (was hard argmax)

Per trial: stream true hypothesis's facts into EMA buffer B; pattern-complete via softmax weighted superposition over codebook; identify hypothesis via M_T similarity; decode skill program of predicted hypothesis. composed = all 4 stages correct.

3 seeds × 60 trials = 180 trials full.

## Acceptance thresholds

- 0.50 PASS matches Lane D PASS threshold.
- 0.25 KILL threshold same as cycle 105.

## Config

- N=8192 smoke, 65536 full.
- K=3 hypotheses, F=10 facts/hyp, skill_len=4, alphabet=5.
- n_trials=60 full, 3 seeds.

## Pre-declared interpretation

- **PASS**: Lane D Demo 1 substrate-product story end-to-end at N=65536 validated. Cycle 127 substrate-novel VAMP-class readout integrates cleanly.
- **PARTIAL**: identify weakest stage at N=65536; iterate that primitive.
- **KILL**: pipeline collapses at N=65536 even with VAMP readout; Demo 1 positioning bounded.

## Not in scope

- Full chain composition through multi-step planning (covered by VAMP-on-chain).
- Noise injection (covered by separate noise-robust experiment).
- K-scaling of pipeline.
