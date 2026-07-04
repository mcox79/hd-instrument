# Pre-registration: exp_cortex_task_analog_downstream_v3

HIGHER-NOISE REGIME REVIVAL after v2b HARD-predict-miss + Skunkworks VET
LOCKED revival criterion. REGIME-EXTENSION of v2b (commit `7345bbbbe`)
frozen infra. SOLE DIFF vs v2b = raise `NOISY_FLIP_FRAC` 0.35 -> 0.45.

Prior-work check (substrate-KB concept-query 2026-07-03): NONE at cosine >
0.30. Top hit `Downstream` (cosine=0.24) is generic term; hit
`cortex_E_tensor_HARDER_REGIME_v1` (cosine=0.23) is a different mechanism
family. This v3 authoring is genuinely novel (not rediscovery of prior arc).

## Purpose

v1 (commit `1ae012b60`) MEASURED@ `data/exp_cortex_task_analog_downstream_v1_smoke/metrics.json`:
`h3_gap = -0.167` -- MB (utility-artifact diagnosis per Skunkworks VET
`a9c698659626b3521`).

v2 (commit `ac201f6a6`) MEASURED@ `data/exp_cortex_task_analog_downstream_v2_s7_smoke/metrics.json`:
`h3_gap = -0.058` -- HARD-predict-miss (CLARIFY=0.65 principled credit
predicted [+0.08, +0.12]; actual sign did NOT flip).

v2b (commit `7345bbbbe`) MEASURED@ `data/exp_cortex_task_analog_downstream_v2b_s7_smoke/metrics.json`:
`h3_gap = -0.033` -- HARD-predict-miss (multi-round empirical DV predicted
`>= +0.05`; actual sign did NOT flip). Atom
`CORTEX_TASK_ANALOG_DOWNSTREAM_v2b_SMOKE_HONEST_NEGATIVE_MM_TENTATIVE`
filed; single-task arc closed under HONEST_NEGATIVE.

**v2b Skunkworks VET (task `a1940529089318a75`) LOCKED revival criterion:**
> Revival requires: (a) higher-noise regime (flip >= 0.45), OR (b) new
> task class where CLARIFY adds value beyond argmax-restart.

**v3 scope: option (a).** SOLE parameter change: `NOISY_FLIP_FRAC 0.35 ->
0.45`. All other params bit-identical to v2b (utility function, Round-2
hint frac, tau values, KB size, seed, query mix).

## Claim class + framing (LOAD-BEARING)

- **NOT a new-mechanism claim.** Cortex integration-fidelity CG at atom #51
  UNCHANGED. This cell tests: does cortex composition give marginal task-
  utility lift at HIGH-NOISE regime (P=0.45) where INDIV argmax degrades?
- **Noise-regime-conditional single-task-utility claim.** Maximum defensible
  claim ceiling at SMOKE PASS = "cortex composition helps on THIS utility
  shape under empirical Round-2 credit AT HIGH-NOISE REGIME P>=0.45"
  (MM_TENTATIVE; scope-conditional atom).
- **Predict-then-check discipline.** Prediction FROZEN in this prereg
  BEFORE the run. NO post-hoc mask/mechanics/flip-frac tuning under any
  outcome. If prediction fails, single-task arc CLOSES DEFINITIVELY as
  MM_STANDARD honest-negative (v2b was MM_TENTATIVE; v3 upgrades tier
  because higher-noise revival criterion was pre-authorized then failed).

## Skunkworks Monte-Carlo prediction (from v2b VET)

At bit-flip `P=0.45`:
- `cos(query, target) = 1 - 2*0.45 = 0.10`
- random-baseline at M=300, N=8192: `sqrt(2*ln(300)/8192) ~ 0.037`
- SNR at INDIV argmax: `0.10 / 0.037 ~ 2.7x` (down from v2b's ~8x at P=0.35)

**INDIV argmax expected to degrade meaningfully at this SNR.** Cortex
CLARIFY-then-Round2 should recover where INDIV argmax fails, because the
Round-2 hint mechanic restores 30% of flipped positions -> effective
`cos = 0.37`, SNR ~10x (still comfortably reliable for retrieval).

## v2b utility function (empirical multi-round; unchanged in v3)

Per-query utility:

| Round 1 outcome                    | Utility |
|------------------------------------|---------|
| ACCEPT + pred correct              | +1.0    |
| ACCEPT + pred wrong                | +0.0    |
| CLARIFY -> Round-2 correct         | +0.9    |
| CLARIFY -> Round-2 wrong           | +0.0    |
| REFUSE (terminal; no Round 2)      | +0.0    |

`norm_util = mean(per_query_util)` directly (already in [0, 1]; no shift).

**Round 2 mechanics** (fires ONLY on CLARIFY route; unchanged from v2b):
- Identify positions where q0 disagrees with target's original bipolar key.
- Sample `ROUND2_HINT_FRAC_OF_FLIPPED = 0.30` of those positions uniformly.
- Restore sampled positions to target's correct bipolar value.
- Argmax over normed `kb_keys` with the hint-augmented query.
- Success = argmax's item's `kb_val_indices` == `true_val`.

**OOB CLARIFY** (no target): Round 2 automatic fail (`0.0` utility).

## Round-2 recovery analytics at v3 regime

THEORETICAL@ under 45% flip + 30% flip-restoration:
- `remaining_flips = 0.45 * (1 - 0.30) = 0.315`
- `expected_cos(q_hint, target) = 1 - 2 * 0.315 = 0.37`
- random-baseline at M=300, N=8192: `~ 0.037`
- SNR ratio: `0.37 / 0.037 ~ 10.0x` -> Round-2 argmax should reliably
  recover target item at M=300 (down from v2b's 13.8x SNR but still
  comfortably above M=300 confusion threshold).

## v3 config change (SOLE DIFF vs v2b; frozen a-priori)

- `NOISY_FLIP_FRAC = 0.45` (was 0.35).
- All other constants v2b-frozen bit-identical.

## v1/v2/v2b frozen (do NOT re-tune)

Preserved bit-identically from v2b (commit `7345bbbbe`):

- `N_DIM = 8192`, `M_ITEMS = 300`
- `V_CB = 1024`, `STM_K = 100`, `LTM_K = 1200`, `S_ROLES = 4`
- `REFUSE_TAU = 0.15`, `CLARIFY_LOWER_TAU = 0.18`, `CLARIFY_UPPER_TAU = 0.42`
- `ROUND2_HINT_FRAC_OF_FLIPPED = 0.30`
- `UTIL_ACCEPT_CORRECT = 1.0`, `UTIL_CLARIFY_ROUND2_CORRECT = 0.9`
- Arms: `ARM_CORTEX_ON`, `ARM_CORTEX_OFF`, `ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION`
- Query mix: SMOKE 10/10/10 = 30 (clean/noisy/oob); FULL 30/30/40 = 100
- Seeds: SMOKE `[7]`; FULL `[7, 13, 19]` deferred until SMOKE PASS

Selftest asserts every constant matches (v3 delta explicitly verified).

## Anti-drift discipline (USER-locked; predict-then-check binding)

Per today's 28+ Fix#28 hits + v2b HONEST_NEGATIVE atom escalation:

- **ONLY parameter changed is bit-flip P (0.35 -> 0.45).** NO other tuning.
- **Prediction pre-committed BEFORE running** (this document; committed
  prior to smoke).
- **If FAIL:** DEFINITIVE_NEGATIVE MM_STANDARD atom
  `CORTEX_COMPOSITION_DOES_NOT_HELP_ON_SINGLE_TASK_EVEN_AT_HIGH_NOISE_v3_MM_STANDARD_close_arc`.
  NO further re-tune of this cell. Single-task arc CLOSES DEFINITIVELY.
  Escalation requires option (b): NEW task class where CLARIFY adds value
  beyond argmax-restart.
- **Utility function FROZEN.** Do NOT tune payoffs to bias PASS.
- **Retry mechanics FROZEN.** Same Round-2 procedure applies uniformly.
- **Source signature for cross-cell verify:** `(v2b empirical utility,
  N_DIM=8192, M=300, bit-flip P=0.45, hint_frac_of_flipped=0.30,
  UTIL_R2_CORRECT=0.9, seed=7 SMOKE, ARMS=3)`.
- **Query set identical to v2b** (30 queries at seed=7, same intent mix
  10/10/10). Only per-query noise level changes; sampling procedure
  bit-identical.

## PRE-COMMITTED PREDICTION (LOAD-BEARING; anti-drift binding)

Primary observable: **H3_gap = norm_util(ARM_CORTEX_ON) -
norm_util(ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION)**.

**PREDICT: H3_gap >= +0.05 AND H3_gap / SEM >= +2.0.**

Sign-flip prediction: `+0.05 vs v2b's actual -0.033` -> `+0.083 delta`
between predicted v3 and measured v2b.

Rationale (per Skunkworks VET Monte-Carlo):
- At P=0.45, INDIV argmax SNR ~2.7x -> noisy queries where INDIV picks
  a wrong item become material (unlike v2b's ~8x SNR where INDIV mostly
  argmax-lucky).
- Cortex CLARIFY route triggers Round-2 hint retrieval at effective SNR
  ~10x -> reliably recovers target where INDIV missed.
- Retry-cost 0.1: even at 100% Round-2 success, ON pays 0.1/CLARIFY-query
  relative to INDIV's ACCEPT-correct. Prediction bets INDIV's noisy-query
  accuracy is now BELOW 0.9 by MORE than the retry-cost overhead.

## PASS / MIDDLE_BAND / FAIL bands (LOCKED)

Primary criterion is **H3_gap** at SMOKE seed=7:

- **HARD_PASS (SMOKE candidate atom `MM_TENTATIVE`):**
  `H3_gap >= +0.05 AND H3_gap / SEM >= +2.0`.
  Candidate atom:
  `EMPIRICAL_CORTEX_COMPOSITION_HELPS_AT_HIGH_NOISE_REGIME_v3_MM_TENTATIVE`
  (single-task arc REOPENS under noise-regime-conditional atom).
  Awaits FULL 3-seed cv < 0.20 for MM_STANDARD / atom filing.
- **MIDDLE_BAND:**
  `H3_gap in [+0.02, +0.05)`. Halfway inconclusive; sign flipped but small.
  Route to Skunkworks + Director for tier decision; may need FULL 3-seed cv.
- **HARD_FAIL:**
  `H3_gap < +0.02 OR (H3_gap >= +0.05 AND gap/SEM < 2.0)`.
  DEFINITIVE_NEGATIVE close-arc. Candidate honest-negative atom:
  `CORTEX_COMPOSITION_DOES_NOT_HELP_ON_SINGLE_TASK_EVEN_AT_HIGH_NOISE_v3_MM_STANDARD_close_arc`.
  Single-task arc CLOSES DEFINITIVELY. Escalation requires NEW task class.

SEM (SMOKE single seed, 30 queries): `sd(per_query_util_ON -
per_query_util_INDIV) / sqrt(30)`.

## Envelope-fail-bands

- **PASS_BAND (v3-expected at P=0.45):**
  - `ARM_CORTEX_ON norm_util in [0.45, 0.85]` (some CLARIFY-triggers on
    noisier queries; overall lower than v2b's [0.55, 0.90] due to more
    noisy-query misses upstream of Round-2 recovery).
  - `ARM_CORTEX_OFF norm_util in [0.30, 0.75]` (raw argmax loses more
    noisy queries at P=0.45).
  - `ARM_INDIV norm_util in [0.35, 0.80]` (argmax + REFUSE gate loses more
    noisy queries at P=0.45; REFUSE bites deeper).
- **FAIL_BAND:** any arm `norm_util > 0.98` (saturation vacuous null risk)
  OR `norm_util < 0.05`. Also FAIL if `arms_differ_verified == False`.

## Formula-selftests

Enumerated selftest assertions (must all pass before dispatch):

1. `NOISY_FLIP_FRAC == 0.45` exactly (v3 revival regime; SOLE DIFF vs v2b).
2. `UTIL_ACCEPT_CORRECT == 1.0`, `UTIL_ACCEPT_WRONG == 0.0`,
   `UTIL_CLARIFY_ROUND2_CORRECT == 0.9`, `UTIL_CLARIFY_ROUND2_WRONG == 0.0`,
   `UTIL_REFUSE_TERMINAL == 0.0`.
3. `ROUND2_HINT_FRAC_OF_FLIPPED == 0.30` exactly (v2b-frozen).
4. `N_DIM == 8192`, `M_ITEMS == 300`, `REFUSE_TAU == 0.15`,
   `CLARIFY_LOWER_TAU == 0.18`, `CLARIFY_UPPER_TAU == 0.42`,
   `V_CB == 1024`, `STM_K == 100`, `LTM_K == 1200`, `S_ROLES == 4`.
5. `len(ARMS) == 3`; arms named exactly `ARM_CORTEX_ON` / `ARM_CORTEX_OFF` /
   `ARM_INDIVIDUAL_PRIMITIVES_NO_COMPOSITION`.
6. `ANCHOR_BASE == "exp_cortex_task_analog_downstream_v3"`.
7. Tiny pipeline run: 20-item KB, 3/3/4 queries, all arms return
   `utility_norm in [0, 1]`.
8. `retrieval_sha256(ARM_CORTEX_ON) != retrieval_sha256(ARM_CORTEX_OFF)`
   (META_RULE_AF).
9. Round-2 hint recovery sanity at v3 regime: 45%-flip query with
   30%-flip-restoration argmax hits correct kb_item at M=20 N=8192
   (theoretical SNR ~13.7x at v3 regime; reliable).

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
  kb_keys (v2b addition)`. SHAPE_MATCH via bipolar-vector-in -> argmax-out.
- `positive_control_arms`: `ARM_CORTEX_ON` reproduces integration-fidelity
  cell route distribution at this regime within tolerance 0.15
  (regime_extension_audit: SHAPE_DRIFT_with_documented_risk; N_DIM matched
  but flip regime higher than atom #51 measured; SNR calculation shows
  Round-2 recovery still SNR-safe at ~10x).
- `functional_requirements`:
  - FR-1 (accept-when-confident): high-sim query -> ACCEPT + correct_val.
  - FR-2 (refuse-when-uncertain): low-sim OOB query -> REFUSE.
  - FR-3 (clarify-when-ambiguous): mid-sim noisy query at v3 regime ->
    CLARIFY (expected to fire more often at P=0.45).
  - FR-4 (Round-2 retry-success as empirical CLARIFY credit): partial-mask
    hint on CLARIFY queries recovers correct kb_item at Round 2 (SNR ~10x).
  - FR-5 (task-utility-lift under high-noise multi-round DV):
    `H3_gap(v3) > +0.05` (composition genuinely helps beyond argmax-lucky
    at v3 higher-noise regime).
- `calibration_check`: `default_ok_for_this_regime` (v1-frozen tau; Round-2
  hint frac v2b-frozen; only flip frac raised per Skunkworks VET).
- `crlb_n/a`: "gating-utility metric; no capacity noise floor at this M/N".
- `baseline_in_band`: True (expected `ARM_CORTEX_OFF norm_util ~ 0.40-0.60`
  at v3 regime; well inside [0.05, 0.95]).
- `cell_chunked`: True. Sibling `_s13` / `_s19` deferred until FULL
  (SMOKE-only local-cpu per USER-locked 2026-07-01 rule).
- `start_marker_written`: True.
- `crash_diagnostic_present`: True.
- `heartbeat_present`: True.
- `defensive_error_checking`: `passed_all_4_patterns`.
- `except SystemExit: raise` BEFORE `except Exception`: yes.
- `progress_logging`: `print_flush_true`; cell < 30s so compliance-formal.
- `run_mode_verification_post_dispatch`: True.
- `CARDINALITY_OK`: mandatory field asserted at cell exit.

## Compute architecture

- Class: **(b) sequential-CPU with justification**. Per-query
  cortex.forward pipeline (M1.4/M1.6/M1.8 gates + STM/LTM update). No
  batchable GPU cell primitive; per-query ~30ms at N=8192 M=300; total
  SMOKE wall <30s.
- Storage strategy: **SHARDED** (each M=300 KB item has its own key vector;
  no bundled composition).

## Dispatch plan

- SMOKE: `local_cpu_queue` (USER-locked 2026-07-01 SMOKE-only rule).
- Timeout: 300s (10x expected wall).
- FULL: deferred until SMOKE PASS; then 3-seed chunked (_s7/_s13/_s19) via
  `remote_cpu_queue` (needs Orchestrator push).

## Post-SMOKE outcomes

- **PASS:** candidate atom
  `EMPIRICAL_CORTEX_COMPOSITION_HELPS_AT_HIGH_NOISE_REGIME_v3_MM_TENTATIVE`.
  Single-task arc REOPENS under noise-regime-conditional atom. FULL 3-seed
  cv < 0.20 gates atom promotion to MM_STANDARD.
- **MB:** inconclusive; may need FULL 3-seed cv for tier resolution.
  Route to Director + Skunkworks.
- **FAIL:** DEFINITIVE_NEGATIVE atom
  `CORTEX_COMPOSITION_DOES_NOT_HELP_ON_SINGLE_TASK_EVEN_AT_HIGH_NOISE_v3_MM_STANDARD_close_arc`.
  Single-task arc CLOSES DEFINITIVELY (both revival options a/b now
  effectively exhausted: option (a) high-noise fails; option (b) new task
  class requires NEW cell design, not this one).

## Composition atoms cited by source signature

- v2b HONEST_NEGATIVE atom
  `CORTEX_TASK_ANALOG_DOWNSTREAM_v2b_SMOKE_HONEST_NEGATIVE_MM_TENTATIVE`
  (v2b filed; v3 tests the LOCKED revival criterion from this atom's VET).
- v2b Skunkworks VET task `a1940529089318a75` (revival criterion source).
- Cortex integration-fidelity atom #51 (`hdlab/cortex.py:74` cited; N_DIM
  invariant preserved).
- v1 utility-artifact diagnosis Skunkworks VET `a9c698659626b3521`.

## Independence declaration

Independent of Cortex-2 v1.1, Probe 16 dispatch, Step 3 pre-authoring,
other in-flight work. No shared file conflicts (new cell + prereg only;
no edits to existing cortex/hdlab modules).
