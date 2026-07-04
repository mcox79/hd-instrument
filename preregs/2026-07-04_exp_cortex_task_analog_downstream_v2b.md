# Pre-registration: exp_cortex_task_analog_downstream_v2b

MULTI-ROUND EMPIRICAL BACKSTOP after v2 HARD-predict-miss. REGIME-EXTENSION
of v2 (commit `4ceb4dc83` frozen infra). SOLE DIFF vs v2 = replace synthetic
`UTIL_CLARIFY = 0.65` payoff with EMPIRICAL Round-2 retry-success DV.

## Purpose

v2's Research 2x-drill predicted H3_gap in `[+0.08, +0.12]` under principled
Bayesian value-of-information CLARIFY credit (0.65). v2 MEASURED@
`data/exp_cortex_task_analog_downstream_v2_s7_smoke/metrics.json` observed
`h3_gap = -0.0583` -- a HARD predict-miss (sign did NOT flip; margin +0.14
short of predicted band).

Cell-author refused post-hoc payoff re-tuning per anti-drift discipline;
escalating to v2b per pre-authorized backstop decision tree from Research
drill note
`notes/research_drill_cortex_task_analog_H3_principled_CLARIFY_utility_2x_2026-07-04.md`:
replace synthetic-payoff CLARIFY credit with EMPIRICAL Round-2 retry-success
as primary DV.

## Claim class + framing (LOAD-BEARING)

- **NOT a new-mechanism claim.** Cortex integration-fidelity CG at atom #51
  UNCHANGED. This cell tests: does cortex composition give marginal task-
  utility lift when CLARIFY earns EMPIRICAL retry-success credit (not
  synthetic 0.65)?
- **SEPARATE task-utility claim under empirical multi-round DV.**
  Maximum defensible claim ceiling at SMOKE = "cortex composition helps on
  THIS utility shape under empirical Round-2 credit" (MM_TENTATIVE).
- **Predict-then-check discipline.** Prediction FROZEN in this prereg BEFORE
  the run. NO post-hoc mask/mechanics tuning under any outcome. If
  prediction fails, single-task arc CLOSES as honest-negative.

## v2b utility function (empirical multi-round; sole diff vs v2)

Per-query utility:

| Round 1 outcome                    | Utility |
|------------------------------------|---------|
| ACCEPT + pred correct              | +1.0    |
| ACCEPT + pred wrong                | +0.0    |
| CLARIFY -> Round-2 correct         | +0.9    |
| CLARIFY -> Round-2 wrong           | +0.0    |
| REFUSE (terminal; no Round 2)      | +0.0    |

`norm_util = mean(per_query_util)` directly (already in [0, 1]; no shift).

**Round 2 mechanics** (fires ONLY on CLARIFY route):
- Identify positions where q0 disagrees with target's original bipolar key.
- Sample `ROUND2_HINT_FRAC_OF_FLIPPED = 0.30` of those positions uniformly.
- Restore sampled positions to target's correct bipolar value.
- Argmax over normed `kb_keys` with the hint-augmented query.
- Success = argmax's item's `kb_val_indices` == `true_val`.

**OOB CLARIFY** (no target): Round 2 automatic fail (`0.0` utility). Cortex
should ideally REFUSE these; if it CLARIFYs, it pays the empirical retry-
miss.

Number tags:
- `UTIL_ACCEPT_CORRECT = 1.0`: HYPOTHESIZED@ this prereg (single-task correct-
  answer reward baseline).
- `UTIL_CLARIFY_ROUND2_CORRECT = 0.9`: HYPOTHESIZED@ this prereg (10% retry
  cost per USER routing note; frozen a-priori; do NOT tune).
- `UTIL_ACCEPT_WRONG = 0.0`, `UTIL_REFUSE_TERMINAL = 0.0`: HYPOTHESIZED@ this
  prereg (empirical DV zeros out non-terminal-correct outcomes; no synthetic
  negative penalty as in v1/v2).
- `ROUND2_HINT_FRAC_OF_FLIPPED = 0.30`: HYPOTHESIZED@ this prereg + Research
  drill authority note (partial-mask hint frac frozen a-priori).

## Round-2 recovery analytics

THEORETICAL@ under 35% flip + 30% flip-restoration:
- remaining_flips = 0.35 * (1 - 0.30) = 0.245
- expected_cos(q_hint, target) = 1 - 2 * 0.245 = 0.51
- random-baseline at M=300, N=8192: sqrt(2 * ln(300) / 8192) ~ 0.037
- SNR ratio: 0.51 / 0.037 ~ 13.8x -> argmax should reliably recover target

USER's spec analytical estimate cited "0.30 -> 0.72" for Round-2 cos --
which corresponds to interpreting "30% correct hint" as 30% of ALL dims
made correct. Cell-author's implementation uses "30% of flipped positions
restored" (= ~10.5% of total dims), yielding expected cos = 0.51. Both
converge to reliable retrieval at M=300; the difference matters only for
mechanism-lift estimation, not directional prediction. Empirical Round-2
success rate is measured directly and does NOT depend on choice between
these two conventions.

## v1/v2 frozen (do NOT re-tune)

Preserved bit-identically from v2 (commit `4ceb4dc83`):

- `N_DIM = 8192`, `M_ITEMS = 300`
- `V_CB = 1024`, `STM_K = 100`, `LTM_K = 1200`, `S_ROLES = 4`
- `REFUSE_TAU = 0.15`, `CLARIFY_LOWER_TAU = 0.18`, `CLARIFY_UPPER_TAU = 0.42`
- `NOISY_FLIP_FRAC = 0.35` (cos = 0.30 target confusable regime)
- Arms: `ARM_CORTEX_ON`, `ARM_CORTEX_OFF`, `ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION`
- Query mix: SMOKE 10/10/10 = 30 (clean/noisy/oob); FULL 30/30/40 = 100
- Seeds: SMOKE `[7]`; FULL `[7, 13, 19]`

Selftest asserts every constant matches.

## Anti-drift discipline (USER-locked; predict-then-check binding)

- **No post-hoc mask/mechanics tuning.** If SMOKE FAILs, single-task arc
  CLOSES as honest-negative. NO further payoff/mechanics adjustment. Any
  future revival requires a NEW task class or a NEW mechanism claim, not
  a re-tune of this cell.
- **`ROUND2_HINT_FRAC_OF_FLIPPED = 0.30` FROZEN.** Do NOT tune to bias PASS.
- **Utility function FROZEN.** Do NOT tune payoffs to bias PASS.
- **Retry mechanics NOT per-query-type.** Same Round-2 procedure applies
  uniformly (30% flip restoration on positions of disagreement).
- **Source signature for cross-cell verify:** `(v2b empirical utility,
  N_DIM=8192, M=300, bit-flip P=0.35, hint_frac_of_flipped=0.30,
  UTIL_R2_CORRECT=0.9, seed=7 SMOKE, ARMS=3)`.

## PRE-COMMITTED PREDICTION (LOAD-BEARING)

Primary observable: **H3_gap = norm_util(ARM_CORTEX_ON) -
norm_util(ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION)**.

**PREDICT: H3_gap >= +0.05 AND H3_gap / SEM >= +2.0.**

Rationale for the +0.05 floor (per USER routing note):
- ON confusable items: CLARIFY-driven Round-2 empirical success at ~0.9-1.0
  (retrieval at cos=0.51 in M=300 KB is near-certain).
- INDIV confusable items: argmax-lucky at cos=0.30 in M=300 KB is
  ALSO near-certain (single-shot).
- The prediction bets that ON's Round-2 empirical retry-success gives a
  MEASURABLE +0.05 lift vs INDIV's ACCEPT-all-noisy that gets full 1.0
  reward per query.
- Under retry-cost 0.1: even at 100% Round-2 success, ON pays 0.1/query
  on noisy queries relative to INDIV's ACCEPT-correct. This means the
  prediction implicitly bets INDIV's ACCEPT-correct rate on noisy queries
  is BELOW 0.9 (i.e., argmax at cos=0.30 misses more than 10% of items).

## PASS / MIDDLE_BAND / FAIL bands (LOCKED)

Primary criterion is **H3_gap** at SMOKE seed=7:

- **HARD_PASS (SMOKE candidate atom `MM_TENTATIVE`):**
  H3_gap >= +0.05 AND H3_gap / SEM >= +2.0.
  Candidate atom:
  `EMPIRICAL_CORTEX_HELPS_UNDER_MULTI_ROUND_EMPIRICAL_UTILITY_v2b_MM_TENTATIVE`.
  Awaits FULL 3-seed cv < 0.20 for MM_STANDARD / atom filing.
- **MIDDLE_BAND:**
  H3_gap in `[+0.02, +0.05)`. Halfway inconclusive; sign flipped but small.
  Route to Skunkworks + Director for tier decision.
- **HARD_FAIL:**
  H3_gap < +0.02 OR (H3_gap >= +0.05 AND gap/SEM < 2.0).
  Definitive negative-finding. Candidate honest-negative atom:
  `CORTEX_COMPOSITION_DOES_NOT_HELP_ON_SINGLE_TASK_v3_MM_TENTATIVE`.
  Single-task arc CLOSES; escalation to a NEW task class or NEW mechanism.

SEM (SMOKE single seed, 30 queries): `sd(per_query_util_ON -
per_query_util_INDIV) / sqrt(30)`.

## Envelope-fail-bands

- **PASS_BAND:** `ARM_CORTEX_ON norm_util in [0.55, 0.90]`;
  `ARM_CORTEX_OFF norm_util in [0.40, 0.80]`;
  `ARM_INDIV norm_util in [0.50, 0.90]`.
- **FAIL_BAND:** any arm `norm_util > 0.98` (saturation vacuous null risk)
  OR `norm_util < 0.05`. Also FAIL if `arms_differ_verified == False`.

## Formula-selftests

Enumerated selftest assertions (must all pass before dispatch):

1. `UTIL_ACCEPT_CORRECT == 1.0`, `UTIL_ACCEPT_WRONG == 0.0`,
   `UTIL_CLARIFY_ROUND2_CORRECT == 0.9`, `UTIL_CLARIFY_ROUND2_WRONG == 0.0`,
   `UTIL_REFUSE_TERMINAL == 0.0`.
2. `ROUND2_HINT_FRAC_OF_FLIPPED == 0.30` exactly (frozen a-priori).
3. `N_DIM == 8192`, `M_ITEMS == 300`, `NOISY_FLIP_FRAC == 0.35`,
   `REFUSE_TAU == 0.15`, `CLARIFY_LOWER_TAU == 0.18`,
   `CLARIFY_UPPER_TAU == 0.42`, `V_CB == 1024`, `STM_K == 100`,
   `LTM_K == 1200`, `S_ROLES == 4`.
4. `len(ARMS) == 3`; arms named exactly `ARM_CORTEX_ON` / `ARM_CORTEX_OFF` /
   `ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION`.
5. `ANCHOR_BASE == "exp_cortex_task_analog_downstream_v2b"`.
6. Tiny pipeline run: 20-item KB, 3/3/4 queries, all arms return
   `utility_norm in [0, 1]`.
7. `retrieval_sha256(ARM_CORTEX_ON) != retrieval_sha256(ARM_CORTEX_OFF)`
   (META_RULE_AF).
8. Round-2 hint recovery sanity: 35%-flip query with 30%-flip-restoration
   argmax hits correct kb_item at M=20 (SNR ~19x).

Prints `SELFTEST_OK` on green.

## SCHEMA-VET fields (mandatory)

- `cardinality_ok`: True. `EXPECTED_N_UNITS = 3 arms * 1 seed = 3` (SMOKE).
- `arms_differ_verified`: True. SHA256 of per-query `(route, pred_val,
  round2_success)` tuple sequence per arm must differ.
- `final_metrics_atomicity`: `tmp_replace`.
- `sweep_alignment_verdict`: N/A (no sweep axis).
- `discriminating_fraction`: N/A (single-regime measurement).
- `composition_edges`: `query -> cortex.forward -> (M1.4 refuse-gate +
  M1.6 attention-router + M1.8 clarify-gate) -> Round-2 hint-argmax on
  kb_keys (v2b addition)`. Round-2 SHAPE_MATCH via bipolar-vector-in ->
  argmax-out (standard argmax primitive).
- `positive_control_arms`: `ARM_CORTEX_ON` reproduces integration-fidelity
  cell route distribution at this regime within tolerance 0.15
  (regime_extension_audit: SHAPE_MATCH; same N_DIM, same cortex config).
- `functional_requirements`:
  - FR-1 (accept-when-confident): high-sim query -> ACCEPT + correct_val.
  - FR-2 (refuse-when-uncertain): low-sim OOB query -> REFUSE.
  - FR-3 (clarify-when-ambiguous): mid-sim noisy query -> CLARIFY.
  - FR-4 (Round-2 retry-success as empirical CLARIFY credit): partial-mask
    hint on CLARIFY queries recovers correct kb_item at Round 2.
  - FR-5 (task-utility-lift under empirical multi-round DV):
    `H3_gap(v2b) > +0.05` (composition genuinely helps beyond argmax-lucky).
- `calibration_check`: `default_ok_for_this_regime` (v1-frozen tau; Round-2
  hint frac frozen a-priori).
- `crlb_n/a`: "gating-utility metric; no capacity noise floor at this M/N".
- `baseline_in_band`: True (expected `ARM_CORTEX_OFF norm_util ~ 0.60-0.70`,
  well inside [0.05, 0.95]).
- `cell_chunked`: True. Sibling `_s13` / `_s19` deferred until FULL (SMOKE-
  only local-cpu rule).
- `start_marker_written`: True.
- `crash_diagnostic_present`: True.
- `heartbeat_present`: True.
- `defensive_error_checking`: `passed_all_4_patterns`.
- `except SystemExit: raise` BEFORE `except Exception`: yes.
- `progress_logging`: `print_flush_true`; cell < 30s so compliance-formal.
- `run_mode_verification_post_dispatch`: True.
- `CARDINALITY_OK`: mandatory field asserted at cell exit.

## Composition atoms cited by source signature

- **Parent atom (integration-fidelity CG #51):** UNCHANGED by v2b.
- **v1 outcome:** MEASURED@
  `data/exp_cortex_task_analog_downstream_v1_s7_smoke/metrics.json`
  h3_gap = -0.16666 (MB); Skunkworks VET `a9c698659626b3521` diagnosed
  utility-artifact (CLARIFY=0.0 zero-credit).
- **v2 outcome (predict-then-check MISS):** MEASURED@
  `data/exp_cortex_task_analog_downstream_v2_s7_smoke/metrics.json`
  h3_gap = -0.0583 (predicted [+0.08, +0.12]; -0.14 short).
- **Research drill authority:**
  `notes/research_drill_cortex_task_analog_H3_principled_CLARIFY_utility_2x_2026-07-04.md`
  (task `af140c36af45121b1`) -- authored v2 principled-CLARIFY credit; pre-
  authorized v2b multi-round backstop.
- **v2b escalation authorization:** USER routing note 2026-07-04 (this
  spawn's task prompt).

## Storage strategy

**SHARDED.** Each of M=300 KB items has its own key vector. Inherited from
v1; compliant with `META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW`.

## Compute architecture

**(b) sequential-CPU with justification.** Per-query cortex.forward is a
sequential facade; ~30s SMOKE wall total. GPU batching not justified.

## Discriminator-survives-scale

SMOKE runs at FULL `N_DIM=8192`, FULL `M=300` (only N_queries reduced to
30). Mechanism discriminator is per-query gating + Round-2 retrieval
(scale-invariant in queries). If H3_gap >= +0.05 at SMOKE seed=7,
prediction is confirmed at MM_TENTATIVE ceiling; FULL 3-seed closes to
MM_STANDARD.

## Post-SMOKE decision tree (report-only)

- **PASS (H3_gap >= +0.05 AND gap/SEM >= +2.0):** Report candidate atom
  `EMPIRICAL_CORTEX_HELPS_UNDER_MULTI_ROUND_EMPIRICAL_UTILITY_v2b_MM_TENTATIVE`;
  DO NOT file. Route to Skunkworks + Director for FULL 3-seed decision.
- **MIDDLE_BAND (H3_gap in `[+0.02, +0.05)`):** Halfway; report inconclusive.
  Route to Skunkworks + Director for tier decision.
- **FAIL (H3_gap < +0.02):** Report candidate honest-negative atom
  `CORTEX_COMPOSITION_DOES_NOT_HELP_ON_SINGLE_TASK_v3_MM_TENTATIVE`.
  Single-task arc CLOSES; escalation to a NEW task class or NEW mechanism.

## Provenance

- Author: `hdi_exp_dev` spawn under USER FULL-AUTO 2026-07-04.
- Reference cell: `experiments/exp_cortex_task_analog_downstream_v2_core.py`
  (commit `4ceb4dc83` frozen infra).
- Load-bearing memory refs:
  - `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03.md`
  - `feedback_smoke_gates_null_hypothesis_should_not_gate_on_discriminator_firing_2026-07-03.md`
  - `feedback_experiment_bias_master_checklist_USER_2026-06-24.md`
  - `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`
  - `feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01.md`
  - `feedback_commit_prereg_notes_before_remote_dispatch_USER_2026-06-17.md`
  - `feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27.md`

## Number-tagging (META_RULE_AC)

- `N_DIM = 8192`: CITED@ `hdlab/cortex.py:74` (Cortex CG envelope floor).
- `M_ITEMS = 300`: v1-frozen CITED@ v1 prereg (M/N < Amit-Gutfreund 0.138).
- `NOISY_FLIP_FRAC = 0.35`: v1-frozen; THEORETICAL@ cos = 1 - 2*0.35 = 0.30
  target confusable regime.
- `ROUND2_HINT_FRAC_OF_FLIPPED = 0.30`: HYPOTHESIZED@ this prereg
  (frozen a-priori).
- `UTIL_CLARIFY_ROUND2_CORRECT = 0.9`: HYPOTHESIZED@ this prereg (10%
  retry cost per USER routing note; frozen a-priori).
- v1 H3_gap = -0.167: MEASURED@
  `data/exp_cortex_task_analog_downstream_v1_s7_smoke/metrics.json`.
- v2 H3_gap = -0.0583: MEASURED@
  `data/exp_cortex_task_analog_downstream_v2_s7_smoke/metrics.json`.
- PASS floor H3_gap >= +0.05 AND gap/SEM >= +2.0: HYPOTHESIZED@ this
  prereg (USER routing note).
- Round-2 hint recovery SNR ~13.8x: THEORETICAL@ cos_hint=0.51 vs random-
  baseline sqrt(2*ln(300)/8192) ~ 0.037.
