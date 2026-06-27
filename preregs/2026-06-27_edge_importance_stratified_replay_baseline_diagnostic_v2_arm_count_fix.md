# Prereg: edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix

Date: 2026-06-27
Anchor: edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix
Cell: experiments/exp_edge_importance_stratified_replay_baseline_diagnostic_v2_arm_count_fix.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Timeout: 600s
Primitives composed:
  - hdlab/edge_importance.py (chain-grade; 2026-06-26) for cor metric
  - hdlab/ultrametric_clustering.py (used by inlined substrate-setup)

## v2 root-cause fix (arm-count cardinality breach in v1)

v1's verdict: `HARD_FAIL: META_RULE_H cardinality_ok breach seed=7:
expected 4 arms, got 6` with the foreign arms
`[ARM_BASELINE_RANDOM_IMPORTANCE, ARM_TRACE_ONLY, ARM_ULTRAMETRIC_ONLY,
ARM_TRACE_X_CORENESS, ARM_TRACE_X_CORENESS, ARM_TRACE_X_CORENESS]`.

Root cause: v1 imported `setup_substrate_with_trace_and_clusters` from
`experiments/exp_edge_importance_retrieval_trace_x_ultrametric_coreness_v3`,
but the v3 module has an UNGUARDED top-level main driver (lines 954+).
Importing v3 ran the v3 driver. The runner sets
`HDLAB_EXP_NAME=edge_importance_stratified_replay_baseline_diagnostic_v1`,
so `get_output_dir(v3_anchor)` inside v3's driver resolved to v1's out_dir
(env var wins), and v3's 6-arm partials were written into v1's out_dir.
v1's `aggregate_partials` then loaded the foreign partials, breaching
META_RULE_H.

v2 fix: inline the substrate-setup function + 5 helper functions
(`generate_pairs`, `build_W_from_pairs`, `predict`,
`composite_query_bundle`, `cleanup_argmax`) verbatim from v3 lines 212-341,
eliminating the v3-module import entirely. Math is identical; only
import-time side effects are removed.

ARM_NAMES remains 4. Pre-reg bands unchanged.

## Drill provenance

notes/research_drill_v4_nrem_replay_fairness_violation_3x_2026-06-27.md
Section "ACTIONABLE CELL-SPEC STUBS / Cell stub 3" --- cheap diagnostic
on the fairness-math conjecture. Drill ANGLE 1: Cauchy-Schwarz says any
sampling-count signal over substrate retrieval correlates with |W|;
stratified sampling by |W|-quantile should BREAK that correlation if
the hypothesis holds.

v4 measurements (drill STEP 0 honest re-read):
  cor(TRACE_ONLY, |W|) = 0.829
  cor(REPLAY_ONLY, |W|) = 0.980
  cor(TRACE+0.5*REPLAY, |W|) = 0.841
  cor(TRACE+1.0*REPLAY, |W|) = 0.852
  cor(TRACE+2.0*REPLAY, |W|) = 0.870

All FAIL the 0.30 fairness gate. v4 HARD_FAILed; cell stub 3 verifies
whether stratification rescues this OR whether deeper substrate property
forbids fairness.

## Mechanism (THE diagnostic)

```
STRATIFIED_REPLAY(atom_norms, trace, n_bins=10, k_per_bin=8):
  Bin atoms by |W|-decile (np.quantile + np.digitize).
  Per bin: sample k_per_bin atoms proportional to within-bin trace.
  importance[atom] = total replay count across bins.

INVERSE_WEIGHTED_REPLAY(atom_norms, trace, n_events=80):
  Sample n_events atoms proportional to trace (v4-style proposal).
  importance[atom] = raw_count[atom] / ||a||^2   (Liu IS correction).
```

If stratified gives cor(importance, |W|) < 0.30, math holds, v4 fairness
violation = sampling-bias artifact, v5 M-CFU / stratified path validated.

If stratified STILL gives cor >= 0.30, deeper substrate property at play,
sampling tricks insufficient; v5 must sidestep via counterfactual utility.

## Arms (4 mandatory; identical to v1)

- ARM_RAND_IMPORTANCE       -- uniform random (control rail; cor ~ 0)
- ARM_TRACE_ONLY            -- raw retrieval_trace_score (reproduce
                               v3.2 / v4 baseline; expect cor >= 0.7)
- ARM_STRATIFIED_REPLAY     -- THE diagnostic; n_bins=10, k_per_bin=8;
                               expect cor < 0.30 if math holds
- ARM_INVERSE_WEIGHTED_REPLAY -- Liu IS; expect cor < 0.30 if math holds

## Pre-reg bands (load-bearing; LOCKED; identical to v1)

### HARD_PASS
- TRACE reproduces bias: |cor(TRACE_ONLY, |W|)| >= 0.70 (full)
                         OR >= 0.50 (smoke)
- AND (|cor(STRATIFIED_REPLAY, |W|)| < 0.30
       OR |cor(INVERSE_WEIGHTED_REPLAY, |W|)| < 0.30)
- AND mechanism fired (n_nonzero_atoms > 0 for STRAT and INV arms)

Interpretation: fairness violation IS sampling-bias artifact; sampling
fixes (stratification + Liu IS) work; v5 stratified-replay path validated.

### MIDDLE_BAND
- TRACE reproduces bias but neither STRATIFIED nor INVERSE_WEIGHTED
  clears the 0.30 gate.
- Interpretation: PARTIAL diagnostic; sampling tricks insufficient;
  deeper substrate property suspected; v5 must use counterfactual
  utility path (M-CFU) rather than sampling rebias.

### HARD_FAIL
- TRACE cor < 0.30 (drill claim contradicted; SURPRISE_NEGATIVE; either
  Cauchy-Schwarz math is wrong OR test rigging wrong)
- OR cardinality breach (per-seed arm count != 4)  [v2 fix targets this]
- OR any caught exception (META_RULE_J)
- OR stale smoke partials loaded into FULL run

## Regime (inherits v3.2 / v4; identical to v1)

- N = 512, M_OLD = 600, M_RECENT = 400, alpha = 1.953
- N_BINS_STRATIFIED = 10
- K_PER_BIN = 8 (so TOTAL_REPLAY_EVENTS = 80 per arm; matches v4 budget)
- N_COMPOSITE_QUERIES = 3000 full / 1500 smoke (substrate-setup; inlined)
- COMPOSITE_ARITY = 3
- USE_FRAC = 0.40
- SEEDS = [7, 17, 23] full; [7] smoke

## Discriminator-must-survive-scale (USER 2026-06-26)

Smoke runs at FULL-N (N=512, M_OLD=600, M_RECENT=400); only SEEDS=[7] and
N_COMPOSITE_QUERIES=1500. Smoke must reproduce TRACE bias (cor >= 0.5) to
clear META_RULE_K. If cor < 0.5 at smoke, route back -- substrate state
isn't producing the expected bias signal at this regime.

## Substrate-only-decode gate

n_llm_calls = 0 by structural-guarantee. Pure numpy. No transformers.

## Diagnostic value (either way; unchanged from v1)

This is a STUB 3 verify-the-referent cell. PASS validates drill ANGLE 1
math AND endorses v5 stratified path. MIDDLE_BAND validates measurement
but rules out sampling-fix path AND endorses v5 M-CFU path. HARD_FAIL
indicates measurement bug (rare; would invalidate v4's HARD_FAIL claim
too).

In ALL three outcomes the cell answers a load-bearing Q for the v5
edge-importance program: is fairness violation fixable via sampling
discipline, or does it require sidestepping the sampling operator
entirely (CFU)?

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`.

## New disciplines applied

- META_RULE_H cardinality_ok: per-seed expected arm count = 4 (this
  cell's fix target; v1 failed this).
- META_RULE_J no-silent-except: setup + each arm wrapped; exception
  RECORDED + HARD_FAIL.
- META_RULE_K smoke fires discriminator: smoke must reproduce TRACE
  bias (cor >= 0.5).
- META_RULE_L band-floor strictly-above-floor (use > and >=).
- USER 2026-06-26 discriminator-must-survive-scale: smoke at full-N.
- PROT-020: numpy-only -> remote_cpu_queue.
- v2-specific discipline atomization candidate:
  RULE_NO_TOP_LEVEL_DRIVER_IN_IMPORTABLE_CELL -- if a cell exposes
  helpers that other cells will import, guard its main driver behind
  `if __name__ == "__main__":`. v3 violates this; v2 sidesteps by
  inlining rather than fixing v3 (NO LOCAL directive).

## Runtime estimate

Smoke (1 seed, full-N substrate, 1500 composite queries): ~30s setup +
~5s arms = ~35s. Full (3 seeds, 3000 composite queries): 3 * ~60s setup
+ ~5s arms = ~195s. Budget 600s = 1.5x worst-case (allows for setup
slop on remote_cpu vs laptop benchmark).

timeout_s = 600 (per dispatch request)

## ASCII-only; no unicode; no emojis; no em-dashes.
