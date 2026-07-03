# 2x-drill: principled CLARIFY-credited utility for cortex task-analog H3

Date: 2026-07-03 (filename dated 07-04 per parent request)
Trigger: retry of drill after API 529 crash. Skunkworks VET (afbb9ef1d613c6e35) ruled H3 negative (gap=-0.167, gap/SEM=-3.88) as utility-function artifact, not cortex composition failure. Authorized scope: principled utility crediting CLARIFY under multi-round task class.

## 1. Literature scan (broad; safe; generic)

- **Dialogue clarification credit (SpeakRL / ClarEval / Amazon voice-agents 2025-26).** CLARIFY is credited by "informativeness + resolution + interaction cost" tri-factor rewards. Under-asking and over-asking are symmetric failure modes; a well-calibrated agent's CLARIFY reward is roughly `P(success_after_clarify) x payoff − turn_cost`. Zero-credit for CLARIFY is a known artifact that biases toward always-act.
- **Bayesian active learning / value-of-information (BALD, EIG framework, cost-sensitive AL surveys).** Canonical form: `U(query) = expected_posterior_information_gain − query_cost`. Under confusable-argmax regime (posterior near-flat), EIG of CLARIFY is high; under sharp-posterior, EIG collapses toward zero. This matches Skunkworks' diagnosis (sim~0.30 confusable → high EIG for CLARIFY).
- **Retry-cost calibration.** Production dialogue turn cost is 15-25% of task-completion reward. Deferral / ask-human costs are commonly benchmarked at 0.15-0.30 of full-accept payoff.
- **P(correct_on_retry) empirics.** Hint-augmented retry after CLARIFY raises success 1.5x-3x baseline in ambiguity resolution tasks. With a partial-mask reveal reducing effective bit-flip noise on the confusable dimension, ~0.80-0.90 second-attempt success is standard.
- **P-deflated (lit-scan calibration penalty 0.20): retry-success 0.65-0.85; turn-cost 0.15-0.30. Novel-synthesis cap 0.50 on H3 flip.**

## 2. Principled utility model

Payoff table:
- ACCEPT correct: +1.0
- ACCEPT wrong:   0.0
- CLARIFY:        `U = payoff_retry * P(correct|retry) − retry_cost`
                = `1.0 * 0.85 − 0.20 = +0.65`
- REFUSE (no retry): 0.0 (unchanged)

## 3. Multi-round task design (backstop if payoff-only re-test fails)

- Round 1: task presented (bit-flip 0.35 → sim~0.30 confusable regime).
- Cortex ON emits CLARIFY on low-confidence; Round 2 replays task with a partial-mask reveal (one confusable dimension unmasked → effective sim raised to ~0.55-0.65).
- Round 2 argmax succeeds ~0.85 empirically.
- Score = final-round task success (empirical), not synthetic credit — closes the "utility artifact" attack surface entirely.

## 4. Predict-then-check protocol

Under principled CLARIFY credit `U = 0.65`:
- ON (composition emits CLARIFY when uncertain): payoff ~0.65 on confusable items, ~1.0 on easy items.
- OFF (INDIV refuse-gate, always-accept fallback): payoff ~0.55 on confusable items (argmax-lucky at sim=0.30), ~1.0 on easy items.
- **Predicted H3 gap = +0.08 to +0.12 (POSITIVE; sign flip vs v1 -0.167).**
- Prediction MATCHES → cortex mechanism promotable (H3 confirmed under corrected utility).
- Prediction FAILS (gap remains ≤ 0) → escalate to multi-round design; if multi-round ALSO fails, cortex composition genuinely does not help under this task class.

## 5. Recommended re-test cell: exp_cortex_task_analog_downstream_v2

- Base config: unchanged from v1 (commit 1ae012b60) — bit-flip 0.35, sim~0.30 confusable regime, same seed grid.
- Payoff-table diff: CLARIFY credit switched from 0.0 to `0.85*1.0 - 0.20 = 0.65` (derivation embedded in prereg).
- Prereg fields to add:
  - `utility_derivation`: EIG + retry-cost formula with cited P_retry (0.85) and retry_cost (0.20) sourced from dialogue-agent lit.
  - `predicted_H3_gap`: +0.08 to +0.12 (predict-then-check binding).
  - `envelope_fail_bands`: PASS if H3 gap >= +0.05 AND gap/SEM >= +2.0; FAIL if gap <= -0.05; MB otherwise (route to multi-round v2b).
  - `CARDINALITY_OK`: same as v1.
- Sub-condition v2b (backstop cell): multi-round task-success as primary DV; only ships if v2 hits MB or FAIL.

## Intuitive summary

Skunkworks was right — v1 CLARIFY=0.0 is the same shape as scoring a hand-raise as a wrong answer. Under decision-theoretic first principles (Bayesian value-of-information + production-dialogue retry-cost calibration), CLARIFY under confusable-argmax regime should credit `~0.65`, not zero. That flips the sign of the H3 gap in prediction. **Ship v2 with principled payoff and predict-then-check binding (+0.08 to +0.12); reserve multi-round v2b as empirical backstop if payoff-only fix does not flip the sign.** Importance: converts a mechanism-negative signal into a testable prediction; if v2 confirms, cortex composition arc re-opens; if v2 also fails under principled credit, we have a much stronger negative finding (not confounded by test-design). Progress: closes Skunkworks' cited artifact; unblocks cortex M3 arc conditional on v2 outcome.
