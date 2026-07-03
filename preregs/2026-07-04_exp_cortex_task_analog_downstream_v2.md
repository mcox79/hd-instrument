# Pre-registration: exp_cortex_task_analog_downstream_v2

REGIME-EXTENSION of v1 (commit `1ae012b60` frozen config). SOLE DIFF vs v1 =
CLARIFY payoff `0.0 -> 0.65` (principled Bayesian value-of-information credit).

## Purpose

Re-test cortex task-analog H3 (composition-fidelity claim) under a
DECISION-THEORETICALLY PRINCIPLED CLARIFY credit, replacing v1's zero-credit
utility function which Skunkworks VET `a9c698659626b3521` diagnosed as a
utility-function artifact biasing the task against any CLARIFY-emitting arm.

## Claim class + framing (LOAD-BEARING)

- **NOT a new-mechanism claim.** Cortex integration-fidelity CG at atom #51
  (composed pipeline reproduces primitive numbers under runtime-call-trace,
  MEASURED@ `data/exp_cortex_integration_end_to_end_v1/metrics.json`) stands
  UNCHANGED.
- **SEPARATE task-utility claim under corrected payoff.** Maximum defensible
  claim ceiling at SMOKE = "cortex composition helps on THIS utility function
  shape" (MM_TENTATIVE). Any SMOKE-only ATOM candidate ships with the
  arc-continuation caveat: not arc-closure (needs FULL + STACKED + cv +
  all-seeds).
- **Predict-then-check discipline.** Prediction band is FROZEN in this
  prereg BEFORE the run. NO post-hoc payoff tuning under any outcome. If the
  prediction fails, escalation is v2b (multi-round task-success as primary
  DV) NOT further payoff-table adjustment.

## Principled CLARIFY-credit derivation (v2 sole diff)

Under confusable-argmax regime (noisy queries land at cos ~ 0.30, center of
CLARIFY zone `[0.18, 0.42]`), the Bayesian value-of-information of asking
CLARIFY is:

    U(CLARIFY) = P(correct | retry after clarify) * payoff_retry - retry_cost

CITED@ authority note
`notes/research_drill_cortex_task_analog_H3_principled_CLARIFY_utility_2x_2026-07-04.md`:

- **P(correct|retry) = 0.85** — CITED@ SpeakRL / ClarEval / Amazon
  voice-agents 2025-26 hint-augmented retry empirics (1.5x-3x baseline
  in ambiguity resolution; ~0.80-0.90 second-attempt success with partial
  disambiguation cue); DEFLATED 0.20 per lit-scan calibration penalty.
- **payoff_retry = 1.0** — SAME as UTIL_ACCEPT_CORRECT (retry yields the
  same terminal reward as first-shot correct-accept).
- **retry_cost = 0.20** — CITED@ production dialogue turn-cost calibration
  (15-25% of task-completion reward); mid-of-band 0.20; DEFLATED same
  penalty applied to ceiling.

    U(CLARIFY) = 0.85 * 1.0 - 0.20 = +0.65

Constant frozen in `exp_cortex_task_analog_downstream_v2_core.py` as
`UTIL_CLARIFY = 0.65`. Selftest asserts exact equality.

Number tags:
- `UTIL_CLARIFY = 0.65`: CITED@ authority note derivation
  (Research 2x-drill task `af140c36af45121b1`).
- Baseline empirics for P_retry / retry_cost: CITED@ lit-scan (SpeakRL,
  ClarEval, BALD/EIG, production dialogue).
- Prediction band [+0.08, +0.12]: HYPOTHESIZED@ authority note simulation
  under principled credit (ON confusable-item payoff ~0.65; OFF confusable-
  item payoff ~0.55 under argmax-lucky).

## v1 frozen (do NOT re-tune)

Preserved bit-identically from `1ae012b60`:

- `N_DIM = 8192` (CITED@ `hdlab/cortex.py:74` CG floor)
- `M_ITEMS = 300` (M/N = 0.037 << Amit-Gutfreund 0.138)
- `V_CB = 1024`, `STM_K = 100`, `LTM_K = 1200`, `S_ROLES = 4`
- `REFUSE_TAU = 0.15`
- `CLARIFY_LOWER_TAU = 0.18`, `CLARIFY_UPPER_TAU = 0.42`
- `NOISY_FLIP_FRAC = 0.35` (cos = 1 - 2*0.35 = 0.30 target confusable regime)
- Arms: `ARM_CORTEX_ON`, `ARM_CORTEX_OFF`, `ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION`
- Query mix: SMOKE `10/10/10 = 30` (clean/noisy/oob); FULL `30/30/40 = 100`
- Seeds: SMOKE `[7]`; FULL `[7, 13, 19]`
- Utility payoffs OTHER than CLARIFY: `ACCEPT_CORRECT=+1.0`, `ACCEPT_WRONG=-1.0`,
  `REFUSE_OOB=+0.5`, `REFUSE_INKB=-0.5`
- Normalization: `norm_util = (utility_mean + 1.0) / 2.0`

Selftest asserts every one of these constants matches v1.

## Anti-drift discipline (USER-locked)

- **No post-hoc payoff tuning.** If SMOKE hits FAIL, we escalate to v2b
  (multi-round task-success as primary DV) — NOT another payoff-table
  adjustment. USER discipline `predict-then-check` requires the prediction
  binding to survive contact with data.
- **CLARIFY / noise / tau NOT re-tuned.** Only payoff table changed. If
  any wrapper tweak lands, selftest fails.
- **Source signature for cross-cell verify:** `(v2 payoff table, N_DIM=8192,
  M=300, bit-flip P=0.35, seed=7 SMOKE, ARMS=3, CLARIFY=0.65)`.

## Pre-committed prediction (LOAD-BEARING; predict-then-check binding)

Primary observable: **H3 gap** = `norm_util(ARM_CORTEX_ON) -
norm_util(ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION)` (v1 code
`compute_verdict` field `h3_gap`; measured `-0.167` at v1 SMOKE per
`data/exp_cortex_task_analog_downstream_v1_s7_smoke/metrics.json`; sign-flip
target).

Predicted band: **H3_gap in [+0.08, +0.12]** (POSITIVE; sign-flip from
v1 -0.167).

Routing-note disambiguation: the authority note also flags `ON - OFF` (v1
code `h1_gap`) as a valid task-utility observable. This prereg locks the
PASS/FAIL decision to **H3_gap = ON - INDIV** because that is the gap that
was `-0.167` in v1 and therefore the gap under sign-flip prediction. The
`h1_gap` (ON - OFF) is reported as SECONDARY observable but does NOT gate
the verdict.

Rationale for +0.08 to +0.12 (from authority note simulation):
- ON confusable items: CLARIFY-driven, payoff ~0.65.
- INDIV confusable items: argmax-lucky (sim=0.30 still recovers item ID
  in M=300 KB), payoff drifts toward 0.55-0.60 net of some REFUSE noise.
- On easy items (clean/OOB), ON ~= INDIV.
- Net gap ~0.08 to 0.12 depending on how many of the 30 SMOKE queries
  fall in each regime after seed=7 sampling.

## PASS / MIDDLE_BAND / FAIL bands (LOCKED)

Primary criterion is **H3_gap** (ON - INDIV) at SMOKE seed=7:

- **HARD_PASS (SMOKE candidate atom `MM_TENTATIVE`):**
  H3_gap >= +0.05 AND H3_gap / SEM >= +2.0.
  Candidate: `EMPIRICAL_CORTEX_MARGINAL_LIFT_UNDER_PRINCIPLED_UTILITY_v2_MM_TENTATIVE`.
  Awaits FULL 3-seed cv < 0.20 for MM_STANDARD / atom filing (arc-closure).
- **MIDDLE_BAND:**
  H3_gap in [+0.02, +0.05). Escalate v2b (multi-round task-success DV).
- **HARD_FAIL:**
  H3_gap < +0.02 OR H3_gap / SEM < 2.0. Escalate v2b as empirical backstop;
  original Skunkworks utility-artifact diagnosis stands.

SEM at SMOKE (single seed, 30 queries): approximated as
`sd(per_query_util_ON - per_query_util_INDIV) / sqrt(30)`.

## Envelope-fail-bands

- **PASS_BAND:** `ARM_CORTEX_ON norm_util in [0.60, 0.90]`;
  `ARM_CORTEX_OFF norm_util in [0.40, 0.75]`;
  `ARM_INDIV norm_util in [0.75, 0.95]` (INDIV benefits from argmax-lucky
  on noisy items at M=300).
- **FAIL_BAND:** any arm `norm_util > 0.98` (saturation vacuous null risk)
  OR any arm `norm_util < 0.05`. Also FAIL if `arms_differ_verified = False`
  (retrieval sha256 collision).

## Formula-selftests

Enumerated selftest assertions (run via `--self-test`; must all pass before
dispatch):

1. `UTIL_CLARIFY == 0.65` exactly.
2. `N_DIM == 8192`, `M_ITEMS == 300`, `NOISY_FLIP_FRAC == 0.35`,
   `REFUSE_TAU == 0.15`, `CLARIFY_LOWER_TAU == 0.18`,
   `CLARIFY_UPPER_TAU == 0.42`, `V_CB == 1024`, `STM_K == 100`,
   `LTM_K == 1200`, `S_ROLES == 4`.
3. `UTIL_ACCEPT_CORRECT == 1.0`, `UTIL_ACCEPT_WRONG == -1.0`,
   `UTIL_REFUSE_OOB == 0.5`, `UTIL_REFUSE_INKB == -0.5`.
4. `len(ARMS) == 3` and arms named exactly
   `ARM_CORTEX_ON` / `ARM_CORTEX_OFF` / `ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION`.
5. `ANCHOR_BASE == "exp_cortex_task_analog_downstream_v2"` (guards wrapper /
   core anchor mismatch).
6. Tiny pipeline run: 20-item KB, 3/3/4 queries, all arms return
   `utility_norm in [0.0, 1.0]`.
7. `retrieval_sha256(ARM_CORTEX_ON) != retrieval_sha256(ARM_CORTEX_OFF)`
   (META_RULE_AF).

Prints `SELFTEST_OK` on green.

## SCHEMA-VET fields (mandatory per META_RULE_H/J/K/L/M + AC/AF/AG/AH)

- `cardinality_ok`: True. `EXPECTED_N_UNITS = 3 arms * 1 seed = 3` (SMOKE);
  `= 3 arms * 3 seeds = 9` (FULL). Cell asserts.
- `arms_differ_verified`: True. SHA256 of per-query `(route, pred_val)`
  sequence per arm must differ (META_RULE_AF).
- `final_metrics_atomicity`: `tmp_replace` (inherited from v1;
  `_write_metrics_atomic`).
- `sweep_alignment_verdict`: N/A (no sweep axis).
- `discriminating_fraction`: N/A (single-regime measurement).
- `composition_edges`: `query -> cortex.forward -> (M1.4 refuse-gate +
  M1.6 attention-router + M1.8 clarify-gate)`; SHAPE_MATCH via cortex
  facade signature (all edges internal to facade). UNCHANGED from v1.
- `positive_control_arms`: `ARM_CORTEX_ON` reproduces integration-fidelity
  cell route distribution at this regime within tolerance 0.15
  (regime_extension_audit: SHAPE_MATCH; same N_DIM, same cortex config).
- `functional_requirements`:
  - FR-1 (accept-when-confident): high-sim query -> ACCEPT + correct_val.
  - FR-2 (refuse-when-uncertain): low-sim OOB query -> REFUSE.
  - FR-3 (clarify-when-ambiguous): mid-sim noisy query -> CLARIFY.
  - FR-4 (task-utility-lift under PRINCIPLED CLARIFY credit):
    `H3_gap(v2) > +0.05` (sign-flip from v1 -0.167).
- `calibration_check`: `default_ok_for_this_regime` (v1-frozen tau values;
  do NOT re-tune per anti-drift discipline).
- `crlb_n/a`: "gating-utility metric; no capacity noise floor at this M/N".
- `baseline_in_band`: True (expected `ARM_CORTEX_OFF norm_util ~ 0.55-0.70`,
  well inside `[0.05, 0.98]`; v1 SMOKE measured 0.6667).
- `cell_chunked`: True. Sibling wrappers `_s13` / `_s19` deferred until
  FULL profile (not authored this cycle per SMOKE-only local-cpu rule).
- `start_marker_written`: True.
- `crash_diagnostic_present`: True (`_write_crash_metrics`).
- `heartbeat_present`: True (per-arm ticks via
  `experiments._cell_heartbeat`).
- `defensive_error_checking`: passed_all_4_patterns (inherited from v1:
  arm-level try/except, cardinality check, arms_differ check,
  baseline_in_band check).
- `except SystemExit: raise` BEFORE `except Exception` in wrapper
  (META_RULE_AC ordering; inherited from v1).
- `progress_logging`: `print_flush_true` per §17; cell is < 60s so field is
  compliance-formal not load-bearing.
- `run_mode_verification_post_dispatch`: True. SMOKE dispatch verifies
  landed `metrics.json` `run_mode == "smoke"` field per §16.
- `CARDINALITY_OK`: mandatory field (per META_RULE); asserted at cell-exit.

## Composition atoms cited by source signature

- **Parent atom (integration-fidelity CG #51):** v1 cortex integration cell,
  MEASURED@ `data/exp_cortex_integration_end_to_end_v1/metrics.json`;
  UNCHANGED by v2 (v2 tests a separate task-utility claim, not integration).
- **Anti-claim (utility-artifact diagnosis):** Skunkworks task-analog VET
  `a9c698659626b3521` — ruled v1 H3 negative under zero-credit CLARIFY
  as utility-function artifact, not composition failure.
- **Research drill authority (principled utility model):** Research
  2x-drill 2026-07-04 task `af140c36af45121b1`, note
  `notes/research_drill_cortex_task_analog_H3_principled_CLARIFY_utility_2x_2026-07-04.md`.
- **v1 baseline SMOKE metrics (source of `-0.167` sign-flip target):**
  MEASURED@ `data/exp_cortex_task_analog_downstream_v1_s7_smoke/metrics.json`
  (h3_gap = -0.16666666666666674; verdict = MIDDLE_BAND).

## Storage strategy

**SHARDED.** Each of M=300 KB items has its own key vector (M1.6 attention
tape). Inherited from v1; compliant with
`META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW` (CG_META 2026-07-02).

## Compute architecture

**(b) sequential-CPU with justification.** Same as v1: ~0.4s SMOKE wall,
< 60s FULL. GPU batching not justified (task IS cortex forward pipeline;
stateful sequential facade).

## Discriminator-survives-scale

SMOKE runs at FULL `N_DIM=8192`, FULL `M=300` (only N_queries reduced
30 -> 30 with 10/10/10 mix). Mechanism discriminator is per-query gating
(scale-invariant in queries). If discriminator fires at SMOKE seed=7 with
H3_gap >= +0.05, prediction is confirmed at MM_TENTATIVE ceiling; FULL
3-seed cv closes to MM_STANDARD.

## Post-SMOKE decision tree (report-only; Skunkworks + Director route)

- **PASS (H3_gap >= +0.05 AND gap/SEM >= +2.0):** Report candidate atom
  `EMPIRICAL_CORTEX_MARGINAL_LIFT_UNDER_PRINCIPLED_UTILITY_v2_MM_TENTATIVE`
  at SMOKE ceiling. Do NOT file. Skunkworks + Director route to FULL 3-seed
  dispatch for arc-closure.
- **MIDDLE_BAND (H3_gap in [+0.02, +0.05)):** Report escalation ask to
  v2b (multi-round task-success DV).
- **FAIL (H3_gap < +0.02):** Report escalation to v2b as empirical backstop.
  Original Skunkworks utility-artifact diagnosis stands.

## Provenance

- Author: `hdi_exp_dev` spawn under USER FULL-AUTO 2026-07-03.
- Reference cell: `experiments/exp_cortex_task_analog_downstream_v1_core.py`
  (commit 1ae012b60 frozen config).
- Authority note: `notes/research_drill_cortex_task_analog_H3_principled_CLARIFY_utility_2x_2026-07-04.md`.
- Load-bearing memory refs:
  - `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03.md`
  - `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03.md`
  - `feedback_experiment_bias_master_checklist_USER_2026-06-24.md`
  - `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`
  - `feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01.md`
  - `feedback_commit_prereg_notes_before_remote_dispatch_USER_2026-06-17.md`

## Number-tagging (META_RULE_AC)

- `N_DIM = 8192`: CITED@ `hdlab/cortex.py:74` (Cortex CG envelope floor).
- `M_ITEMS = 300`: v1-frozen CITED@ v1 prereg (M/N < Amit-Gutfreund 0.138).
- `UTIL_CLARIFY = 0.65`: CITED@ authority note derivation
  `U = 0.85 * 1.0 - 0.20`.
- P_retry = 0.85, retry_cost = 0.20: CITED@ lit-scan
  (SpeakRL / ClarEval / production dialogue).
- v1 H3_gap = -0.167 (baseline for sign-flip):
  MEASURED@ `data/exp_cortex_task_analog_downstream_v1_s7_smoke/metrics.json`.
- Predicted v2 H3_gap in [+0.08, +0.12]:
  HYPOTHESIZED@ authority note simulation.
- PASS band H3_gap >= +0.05 AND gap/SEM >= +2.0:
  HYPOTHESIZED@ this prereg (USER routing note).
