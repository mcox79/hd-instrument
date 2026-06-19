# Prereg: wave14e_betB_ewc_smoke_v1

**Date**: 2026-05-24
**Author**: orchestrator main thread (under FULL AUTONOMY from research_15_angles_triage)
**Queue**: remote_cpu_queue
**ETA**: 45-90 min CPU at N=4096, 5 seeds
**Script**: `experiments/exp_wave14e_betB_ewc_smoke_v1.py`

## Source

Tier-2 candidate B1 from `notes/research_15_angles_triage_2026-05-24.md`: EWC
(Elastic Weight Consolidation; Kirkpatrick 2017) for Bet B retention rehab.
Bet B's current state: retention_A approximately 0.73 vs target 0.80 (Tier-1
KILLER status). EWC is the canonical published continual-learning rehab path
with smallest delta from existing Bet B scaffolding
(`experiments/exp_wave14d_betB_kovacs_v1.py`).

## Mechanism

After Phase A trains W to W_A, estimate the Fisher-diagonal
F_ij = E[(d log p(target | ctx) / d W_ij)^2] over Phase-A retrieval samples.
During Phase B and Phase C training, add the EWC pull-back
  W <- W + alpha * dW - lambda * F * (W - W_A)
to the delta-rule update. The intuition: directions important for Phase A
retention (large F_ij) get higher resistance to Phase B/C updates.

## Hypothesis (one-line)

At least one non-zero lambda in {0.001, 0.01, 0.1} lifts retention_A from
the no-EWC baseline (~0.73) to >= 0.80 while keeping gain_C > 0 (Phase C
still learns something).

## Design

| Config | N | seeds | epochs | phase_A_epochs | bytes/corpus | batch | lambdas |
|---|---|---|---|---|---|---|---|
| Full | 4096 | {7,17,23,31,41} | 5 | 8 | 200,000 | 64 | {0.0, 0.001, 0.01, 0.1} |

Phase structure inherited from `exp_wave14b_cl_phase_a.py`: train on corpus A
(bytes from canonical Project Gutenberg sample); then train on corpus B
(bytes from a second corpus); then train on corpus C (bytes from
experiments source). Test sets disjoint per phase. Retention = ratio
of bpc-A-after-C to bpc-A-baseline (clamped to <=1).

Fisher estimate: 256 random Phase-A samples, batch_size=64.

## Verdicts

### HARD PASS - `BET_B_EWC_PASS`

Best non-zero lambda yields:
- retention_A >= 0.80 (averaged over 5 seeds)
- gain_C > 0 (averaged over 5 seeds)

Implication: Bet B row promotes from PARTIAL/THRESHOLD to FULL; cap_map
records new EWC-augmented Phase B/C path; closes one Tier-1 KILLER gap.

### HARD FAIL - `BET_B_EWC_KILLED`

Best non-zero lambda has retention_A < 0.70 (worse than no-EWC baseline).
Implication: EWC is contraindicated for this substrate; close path. File
5 rescue sketches per PROT-004 (Synaptic Intelligence / MAS / per-layer
Fisher / Phase-A-only retention probe / orthogonal-projection update).

### PARTIAL - `BET_B_EWC_PARTIAL`

retention_A improves over lambda=0 baseline by >= 0.02 but stays below 0.80.
Implication: mechanism transfers but does not clear threshold; trigger 2x
Research drill on Fisher-diagonal-vs-Fisher-block-diagonal (Schwarz 2018
Online EWC) or hyperparameter search at lambda > 0.1.

### INCONCLUSIVE - `BET_B_EWC_INCONCLUSIVE`

Best-lambda retention_A in [0.70, 0.80) AND no lift over lambda=0 baseline,
or per_seed data missing. No row movement.

## Self-tests (passed locally 2026-05-24)

`--self-test`: 4/4 verdict synthetic cells pass (PASS / KILLED / PARTIAL /
INCONCLUSIVE branches).

## Smoke gate (passed locally 2026-05-24)

`--smoke` (N=512, 1 seed, 2 epochs, 4000 bytes, lambdas {0.0, 0.01}):
- VERDICT: BET_B_EWC_PASS (retention_A=0.856 at lambda=0.01, gain_C=4.32)
- Fisher mean=1.05e-6, max=2.68e-6 (well-conditioned)
- metrics.json valid

Note: smoke retention_A=0.856 is at N=512 only; full N=4096 typically
shrinks the EWC lift because larger N gives more capacity headroom in
the base substrate. Smoke PASS is **necessary but not sufficient** for
full PASS at N=4096.

## Memory / wallclock budget

- W per cell: 4096 x 4096 float32 ~ 64 MB; Fisher diagonal same ~ 64 MB
- 5 seeds x 4 lambdas x 3 phases ~= 60 train passes
- Estimated wallclock: 60-90 min at remote CPU (i7-class)
- Timeout: 7200s (2 hr safety budget)

## Filing on outcome

- HARD PASS: cap_map Bet B row -> FULL (was PARTIAL); v182 bump; status_log
  importance=CRITICAL; trigger 2x Research drill on Fisher-vs-Synaptic-
  Intelligence comparison + Phase-D extension probe.
- HARD FAIL: file 5 rescue sketches (PROT-004); strategy_request_to_research
  rehab file; cap_map row stays PARTIAL with PROVISIONAL on EWC path.
- PARTIAL: cap_map row PARTIAL with annotation "EWC improves but does not
  clear 0.80 threshold at tested lambdas"; trigger 2x Research on extended
  hyperparam range.
- INCONCLUSIVE: no row movement; document in cap_map history v_unchanged.

All outcomes: status_log entry with importance>=HIGH; plain_language frames
"Did EWC rehab Bet B?" answer.

## Notes / caveats

- Fisher-diagonal on outer-product W is unusual (W is not a gradient-
  descent parameter in standard sense); we estimate Fisher as
  `E[(d log p / d W_ij)^2]` over Phase-A retrieval samples by direct
  per-sample outer-product accumulation. Smoke confirms the mechanism
  produces sensible Fisher values (mean ~ 1e-6 at N=512).
- Source-15-angles synthesis flagged P=0.55 (highest tractability among
  the 15 angles); [[feedback-lit-scan-calibration-penalty]] deflation is
  light here because Kirkpatrick 2017 is direct precedent with published
  margin (5-15pp lift over replay-only baseline). After deflation
  P_substrate-novel ~ 0.45 (the gap is whether the outer-product W formulation
  retains EWC's bias-variance tradeoff).
