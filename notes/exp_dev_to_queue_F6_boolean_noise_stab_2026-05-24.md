# exp_dev → queue — F-6 Boolean noise-stability Cap-13 candidate — 2026-05-24

**Trigger**: orchestrator autonomous cycle (standing "never idle" directive). The three Cap-13 continents from `notes/research_new_continents_deep_drill_2026-05-24.md` have been triaged:

- F-14 Tropical: shipped (Anchor 1 KILLED at small-N discretization artifact; Anchor 2 EMP_MARGIN_WELL_DEFINED licensed). Tropical Cap-13 candidate now under post-mortem; closed-form margin needs continuous-relaxation reformulation.
- F-4 Clifford-TN: shipped (sub-anchor B HARD_PASS_LICENSED at N=4096; sub-anchor A HARD_FAIL_TN_DIVERGENCE at small-N rel_err=0.308 — Hopfield-cleanup magic-injection suspected).
- **F-6 Boolean noise-stability: NOT YET SHIPPED.** This file dispatches it.

Pause flag CLEARED at dispatch (orchestrator main verified `data/orchestrator_paused.flag` absent).

## Task hand-off (per [[feedback-no-experiment-design-in-prompts]])

WHAT: implement and ship the F-6 Boolean noise-stability anchor proposed in `notes/research_new_continents_deep_drill_2026-05-24.md` Section 2.5. The anchor tests whether the bent-function Walsh-spectrum structure of Kerdock codewords yields a closed-form noise-stability certificate Stab_rho(f_Kerdock) = rho^2, and whether the KKL lower bound 2*log(N)/N is tight for the substrate.

WHY (pointers, not summaries):
- Research deep-drill source: `notes/research_new_continents_deep_drill_2026-05-24.md` Section 2 (theory anchor, KKL application, Cap-1 erase certificate via noise-stability, Cap-3 streaming polynomial-decay reformulation).
- Cap_map context: v181; F-14 partial (Anchor 2 PASS, Anchor 1 KILLED), F-4 partial (sub-B PASS, sub-A FAIL), F-6 the third leg of the audit-triangle pattern (Section 4.3 of the drill).
- HARD PASS / HARD FAIL thresholds from Section 2.5 of the drill (verbatim):
  - HARD PASS: Empirical Stab_rho(Kerdock readout) at N=1024, rho=0.9 matches closed-form rho^2 = 0.81 within 2%. KKL inequality holds with equality (within numerical noise) for sampled codewords.
  - HARD FAIL: Empirical Stab_rho off by >10% from rho^2 (means substrate has Fourier mass outside degree-2, contradicting bent assumption — audit cap_map). OR KKL inequality slack > 30% (means substrate not at KKL-tight, downgrades Cap-13 claim).
- Risk noted: Hopfield-cleanup post-processing may inject higher-degree Fourier content not captured by bent analysis. Per Section 5 honest reading, the bent-function analysis applies only to PRE-cleanup readout — anchor should report both PRE-cleanup and POST-cleanup Stab_rho separately.
- Citations from drill: Solov'eva-Tokareva 2008 (Kerdock=bent); Mesnager bent-functions invited paper; Avishay Tal CS294-92 (KKL/noise-stability); Bonami-Beckner hypercontractivity.

CONTRACT:
- Anchor name suggestion: `wave14_boolean_noise_stab_kerdock_kkl_v1` (or exp_dev judgement on collision).
- Queue: CPU per drill recommendation (Walsh transform of Kerdock codewords; CPU-cheap at N <= 1024, ~2-4 hr CPU wallclock per drill estimate). Per [[feedback-pipeline-pacing]] CPU-explore tier.
- Per [[feedback-envelope-expansion-fail-bands]]: HARD PASS / HARD FAIL bands verbatim in prereg (above).
- Per [[feedback-ship-before-dependency-verified]]: bent-function Walsh transform may need a new helper; verify deps + remote --self-test before queue_add.
- Per [[feedback-ship-name-collision]]: name-uniqueness grep against remote queue.json prior to ship.
- Per [[feedback-no-smoke]]: smoke at N <= 256 should report PRE-cleanup and POST-cleanup Stab_rho separately; if smoke kills the post-cleanup branch (expected risk per Section 2.5), prereg should still permit shipping the PRE-cleanup-only certificate as a partial Cap-13 with explicit caveat.

AUTONOMY DECLARATION: exp_dev decides — exact N grid, seed count, codeword sample size, rho grid, prereg threshold formatting, smoke design, dependency chain, queue_add invocation, status_log message text. Mechanism cap_map version bumping is downstream verdict_handler work, not part of this dispatch.

## Why ship now, not later

1. F-14 and F-4 results just landed; F-6 is the missing third leg of the audit-triangle (drill Section 4.3). Shipping now means all three legs are in-flight and the audit-triangle pattern can be evaluated as a single coherent Cap-13 picture in next verdict cycle.
2. Queue depth analysis (this dispatch's time): CPU queue depth=3 (1 running + 2 pending), GPU depth=2 (1+1). Adding F-6 to CPU keeps CPU depth >= 3 through the LR envelope dose-response + tropical N4 follow-ups; matches goal of depth >= 2 for 4-6h.
3. Cheapest of the three Cap-13 continents per drill Section 4.2 (after tropical small-N discretization issue surfaced); ~2-4 hr CPU only.
4. Per [[feedback-dont-dismiss-adjacent-methods]]: bent-function-on-Kerdock is published fact (Solov'eva-Tokareva); not running this is the dominant failure mode.

## Honest framing per [[feedback-no-smoke]]

This is one of the three Cap-13 candidates the new-continents drill identified. Probable outcome (per drill Section 5):
- PRE-cleanup Stab_rho = rho^2: HIGH confidence (mechanism = published bent-function fact).
- POST-cleanup Stab_rho = rho^2: MEDIUM confidence; Hopfield-cleanup is degree-O(N) in Boolean Fourier; may collapse the cert to PARTIAL.
- KKL tightness on substrate: MEDIUM confidence; tightness needs numerical verification.

Honest read per drill Section 5: "70-80% Cap 13" with explicit cleanup caveat. Not framed as automatic win.

## Open backlog reminder for exp_dev or next orchestrator cycle

- antiRM mechanism Research drill (Strategy shoreup #4, ~30 min research-only, no compute).
- Bet T Mondrian / Bet V kappa_4 close-or-rescue probes (Strategy matrix #2 + #3).
- 2x deep drill on LR_ENVELOPE_MIXED E4 winner — `wave14_lr_envelope_dose_response_v1` already pending CPU; verdict will surface the 2x answer; do not double-ship.
- F-14 Tropical Anchor 1 post-mortem rescue (continuous-relaxation reformulation; rel_err blew up at N=16 + N=64 per the cap_map note).

Per [[feedback-for-you-tab-primary-channel]]: status_log entry to be written by orchestrator at dispatch + by exp_dev at ship + by verdict_handler at landing.
