# Pre-registration: cls_ca3complete_significance_v1

**Date:** 2026-07-08
**Author:** exp_dev (cell author)
**Cell:** `experiments/exp_cls_ca3complete_significance_v1.py`
**Anchor:** `cls_ca3complete_significance_v1`
**Purpose:** Firm the logged MM_TENTATIVE CA3-completion SUB-CLAIM to a real verdict by re-running the
CLS consolidation loop at >=5 seeds and testing the cross-seed SIGNIFICANCE of the paired lift.

## What this firms (and what it does NOT touch)
The parent cell `exp_cls_ca3complete_consolidation_v1` (commit 92e01cf3f) landed the CLS consolidation
MAIN claim (integrate-new-without-forgetting) CHAIN_GRADE at 3 seeds [7,17,23]. Its CA3-completion
SUB-CLAIM -- does the CA3 pattern-completion step during replay measurably lift OLD-item retention over
the SAME loop WITHOUT the completion step -- came in MM_TENTATIVE:
- lift = CONSOLIDATE_FULL old_retention - CONSOLIDATE_NO_CLEANUP old_retention
- MEASURED@`data/exp_cls_ca3complete_consolidation_v1/metrics.json`: per-seed {0.08, 0.04, 0.04}, mean ~0.053
- directionally consistent 3/3 but did NOT clean-clear significance at n=3 (sign-test one-sided p=0.125;
  paired-t t~4.0 df=2 p~0.06).
- recorded revival criterion: rerun at >=5 seeds to establish (or refute) significance before any CG
  claim on CA3-completion specifically.

This cell does exactly that. **The parent cell and its metrics.json are UNTOUCHED**; the MAIN claim is
unaffected. This is a NEW anchor writing to a NEW output dir (`data/exp_cls_ca3complete_significance_v1/`).

## Prior-work check (mandatory)
`bash tools/substrate_query.sh "CA3 pattern completion consolidation replay significance seeds old retention lift"`
top hits: `substrate_pattern_completion_corruption_cliff_v2_*` (cosine ~0.386) -- a DIFFERENT mechanism
(corruption-cliff sweep, not consolidation-replay); generic wordnet `consolidation` node (cosine 0.389).
No prior atom is this CA3-completion-lift significance re-run. **Genuinely novel, NOT a rediscovery** --
it is the recorded >=5-seed revival of an existing MM_TENTATIVE sub-claim.

## Design (IDENTICAL loop to parent; ONLY the seed count + the primary metric/verdict differ)
Same regime, same 3 arms, same OLD/RECENT item sets, same discrete fixed budget, same CA3 params.
- **Seeds:** FULL = [7, 17, 23, 29, 31, 37, 41, 43] (n=8). The original 3 are INCLUDED so the run
  composes / reproduces them (deterministic per seed).
- **Arms** (identical single-step argmax readout; only the queried store differs):
  - NAIVE_NO_CONSOLIDATION (positive control): fast buffer only -> OLD decays out -> forgotten.
  - CONSOLIDATE_FULL (mechanism): per-epoch discrete offline phase, budget B, partial-cue (SWR) replay
    -> CA3-complete (`iterative_cleanup` alpha=0.5) -> write clean concept to SLOW store.
  - CONSOLIDATE_NO_CLEANUP (ablation): same schedule/budget/partial-cue but SKIP CA3 completion
    (write raw noisy readout). Isolates the completion contribution.

## Config
`D=1024 T=600 E=12 DECAY=0.94 V=64 BUDGET_B=50 CUE_RHO=0.70 ca3_temp=4.0 ca3_alpha=0.50 ca3_steps=6`
(byte-identical to the parent cell). FULL seeds n=8. SMOKE seeds=[7,17,23] at IDENTICAL full-scale
params (discriminator-survives-scale option A on the regime; the significance discriminator is
exercised at the smoke's n=3 -> reproduces MM_TENTATIVE MIDDLE_BAND, proving the machinery).

## PRIMARY discriminator = the paired CA3-completion lift and its significance
Per-seed paired lift `d_i = CONSOLIDATE_FULL old_retention_i - CONSOLIDATE_NO_CLEANUP old_retention_i`.
Two PRE-DECLARED tests on `{d_i}` at n=8 (alpha=0.05, **two-sided** for both -- the conservative,
direction-agnostic choice; note the parent's recorded p=0.125 sign-test was ONE-sided):
- **paired-t (two-sided):** `scipy.stats.ttest_rel(FULL_old, NO_CLEANUP_old)`.
- **sign-test (two-sided binomial):** `scipy.stats.binomtest(n_pos, n_nonzero, 0.5, "two-sided")`.

## Pre-registered bands (strict, META_RULE_L)
- **HARD_PASS** (sub-claim promotes toward CG-eligible): `mean(d) > 0` AND `paired_t p_two_sided < 0.05`
  AND `sign_test p_two_sided < 0.05`. Interpretation: the CA3 pattern-completion step reliably and
  significantly lifts OLD-item retention at n=8.
- **HARD_FAIL** (sub-claim refuted): `mean(d) <= 0` -- the CA3 completion provides no lift (or hurts)
  when measured over 8 seeds.
- **MIDDLE_BAND** (sub-claim = small MM refinement): `mean(d) > 0` but NOT both tests clear p<0.05
  (directionally consistent but marginal/non-significant). NO_CLEANUP already retains ~0.88 so CA3 is a
  marginal refinement, not load-bearing. **This is the recorded "confirm as small MM refinement" outcome.**
- **CONTEXT_INVALID -> MIDDLE_BAND** guard: if the consolidation regime did not behave
  (`NAIVE old > 0.55` OR `CONSOLIDATE_FULL old < 0.80`), the sub-claim test is not interpretable and the
  cell returns MIDDLE_BAND flagged CONTEXT_INVALID (defends against a silently-drifted regime).

Either HARD_PASS or MIDDLE_BAND or HARD_FAIL is a clean result per the task.

### Discriminator-survives-scale note
The significance discriminator does NOT saturate/auto-pass: SMOKE at n=3 correctly returns MIDDLE_BAND
(paired-t p=0.0572, sign-test p=0.25 -- both fail p<0.05), reproducing the MM_TENTATIVE state exactly.
Whether it fires HARD_PASS at n=8 depends genuinely on the 5 new seeds' measured lifts -- the cell does
NOT pre-judge. (Analytical expectation, NOT a gate: if the 5 new seeds behave like the original 3, the
SEM shrinks ~sqrt(8/3) and both tests would clear; if the lift shrinks or scatters, MIDDLE_BAND. The
FULL run decides.)

## Discriminator-fires gate (META_RULE_K; contract)
Self-test/smoke: the NAIVE catastrophic-forgetting POSITIVE CONTROL must STILL fire --
`assert_discriminator_fires(NAIVE old_retention >= 0.80, ...)` (control must FAIL the OLD-retention
headline = must forget), AND `NAIVE new_acquisition > 0.70` (the store CAN learn recent items) so the
~0.02 OLD retention is a genuine forgetting readout, not a dead store. SMOKE measured NAIVE old=0.020
new=0.960 -> both fire correctly.

## Telemetry-sensitivity (2026-07-08 rule)
Self-test: zeroing the queried store drops retention (>0.3); corrupting it drops (>0.1) -- the metric
reads store state, is NOT analytically pinned. Plus the significance functions are unit-tested against
known values (8/8 -> sign p=2*0.5^8=0.0078; n=3 {0.08,0.04,0.04} -> paired-t p=0.0572 cross-checked
against `stats.ttest_rel` independently; reversed-lift -> mean<0; zero-variance-nonzero -> perfectly
significant).

## SMOKE result (MEASURED)
MEASURED@`data/exp_cls_ca3complete_significance_v1_smoke/metrics.json`: verdict MIDDLE_BAND,
run_mode=smoke, elapsed=11.4s, n_units=3, cardinality_ok=true. Per-seed lift {0.080, 0.040, 0.040}
mean=0.0533 | paired-t t=4.0 p=0.0572 | sign-test 3/3 p=0.2500 | FULL_old=0.933 NO_CLEANUP_old=0.880
NAIVE_old=0.020 new=0.960 | regime_sane=true | budget_ok=true. Structured gate claims:
mean_lift_positive=True, paired_t_significant=False, sign_test_significant=False, regime_sane=True.
(Exactly reproduces the recorded MM_TENTATIVE state -> proves the significance pipeline is correct.)

## SCHEMA-VET fields
- `cardinality_ok: true` -- EXPECTED_N_UNITS = n_seeds = 8 (FULL); verdict emits
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if `len(units) < 8`; `cardinality_ok` written to metrics.
- `final_metrics_atomicity: "tmp_replace"` -- write_metrics + crash-diag use os.replace; per-seed
  partials atomic (write_partial_key).
- `arms_differ_verified: true` -- `_arms_must_differ` hashes F / S_full / S_nc (META_RULE_AF); distinct.
- `HP_SCOPE:` {sub-claim verdict scoped to the paired FULL-vs-NO_CLEANUP lift only; NAIVE arm is the
  discriminator-fires control (no HP gate); regime-sanity uses NAIVE+FULL as a context guard}.
- `calibration_check: "default_ok_for_this_regime"` -- CA3 params are the certified att1 defaults,
  byte-identical to the parent CHAIN_GRADE cell; regime unchanged.
- `crlb_n/a: "significance-of-a-paired-mean, not a noise-floor threshold. The n=3 SMOKE demonstrates the
  test is NOT auto-passing (p=0.057/0.25 both fail); reachability of p<0.05 at n=8 is data-contingent on
  the 5 new seeds, which is precisely the question being firmed."`
- `baseline_in_band: true (interpretation)` -- NAIVE=0.02 is the intended forgetting control; the
  ablation arm NO_CLEANUP=0.88 provides the paired reference the lift is measured against (non-saturated
  headroom that CA3 fills). The discriminator is the significance of that paired gap, honestly gated.
- `sweep_alignment_verdict: N/A (no swept axis; seed replication only)`.
- `discriminating_fraction: N/A (paired significance test, not a sweep)`.
- `composition_edges:` fast-readout -> CA3 completion (`iterative_cleanup`) -> slow write. All D-dim.
  verdict: SHAPE_MATCH.
- `positive_control_arms:` CA3 primitive reproduced at test regime (self-test: cos_cleaned > cos_raw);
  `iterative_cleanup` is the cited CG primitive. Plus the run reproduces the parent's 3-seed lifts
  exactly (composition check).
- `cell_chunked: false` -- fast CPU cell (~2.6s/seed measured; 8 seeds ~ 21-30s); per-seed
  write_partial_key checkpoint/resume (restartable). Runner-zombie risk minimal.
- `start_marker_written: true`; `crash_diagnostic_present: true` (Exception -> CELL_CRASHED + traceback,
  atomic); `heartbeat_present: false` (exempt: wall << 15min); `defensive_error_checking: "passed
  (start-marker + crash-diag + no bare except; heartbeat exempt <15min)"`.
- `progress_logging: "print_flush_true"` (all progress lines flush=True; wall < 30min so field advisory).
- `except SystemExit: raise` ordered BEFORE `except Exception` (no BaseException). Grep gate CLEAN.
- `functional_requirements:` (Gate E) FR = "quantify whether the CA3 pattern-completion step is a
  statistically real contributor to OLD-item retention (vs a noise-level refinement)"; primitive =
  paired within-seed lift + sign-test/paired-t across an adequately-powered seed set (n>=5). Mapped.

## Dispatch
- Compute: recency-decay recurrence is inherently sequential; tiny D x D numpy matmuls; ~21-30s FULL
  (8 seeds). No GPU benefit (numpy-only, no torch). -> `remote_cpu_queue` (idle).
- SMOKE-only-local honored: FULL routed remote (never local). Local used ONLY for smoke/self-test.
- Timeout: `tools/exp_guard.py timeout --smoke-wall 8 --axis seeds:3:8 --class default` -> floor-dominated
  `timeout_s=1800` (30min; generous vs ~30s expected wall; restartable if killed).
- FULL run_mode verification post-dispatch (orchestrator): expect run_mode=full, per_unit=8,
  cardinality_ok=true, elapsed ~20-40s, structured_gate_claims present.
