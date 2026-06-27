# Prereg: edge_importance_v6_CFU_stronger_regime

Date: 2026-06-27
Anchor: edge_importance_v6_CFU_stronger_regime
Cell: experiments/exp_edge_importance_v6_CFU_stronger_regime.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Wave: M-CFU v5 strengthening; lift signal above PASS bar via 4 strengthening levers
Primitives composed:
  - hdlab/edge_importance.py (chain-grade; 2026-06-26)
  - experiments/exp_edge_importance_v5_CFU_counterfactual_utility_v1.py (v5 referent)

## Motivation

v5 (M-CFU) was Skunkworks-tiered MIDDLE_BAND - the FIRST mechanism in
the edge-importance family to PASS fairness (cor(CFU,|W|)=-0.015 vs
+0.83 for trace-family which sources degree-skewed signal) but
sel_unretr=+0.037 short of the +0.15 PASS bar. Brain-grounded
(Tonegawa optogenetic engram-silencing analog; chain-grade in
neuroscience). Structurally orthogonal to magnitude.

The drill (research_drill_cortex_importance_backup_mechanisms_2026-
06-27.md, Section M-CFU) identifies 4 strengthening levers that lift
CFU signal above noise:

  L1 BIGGER HELD-OUT PROBE SET (v5 N_PROBE=100 -> v6 N_PROBE=400; 4x;
     M_HELDOUT also 100 -> 400 to support). Reduces noise floor on
     per-cohort recall delta. Variance of difference scales as
     1/sqrt(N_PROBE); 4x -> 2x lower noise.

  L2 LEAVE-K-OUT VARIANT K=5 (v5 only K=10). Multi-atom co-importance
     captures interaction effects.

  L3 ALPHA SWEEP alpha in {1.5, 2.0, 2.5, 3.0} (v5 fixed at
     alpha=2.148). Finds regime where ablation signal is loudest vs
     noise. Higher alpha = more saturation pressure on W = larger
     per-atom contribution = more measurable CFU. M_OLD derived per
     target alpha via M_OLD = max(50, N*alpha - M_RECENT - M_HELDOUT).
     Note: at N=512 + M_RECENT+M_HELDOUT=800, alpha=1.5 yields
     infeasible M_OLD; floored to 50, ACTUAL alpha=1.66.

  L4 CONTINUOUS DOWNSCALE GRADIENT (v5 binary; v6 5 levels {0, 0.25,
     0.5, 0.75, 1.0}). Importance = trapezoidal integral of recall-
     deficit over weight-fraction. Captures the FULL function
     recall(weight_fraction) rather than just endpoint; atoms with
     steep deficit curves get higher integrated importance than atoms
     with shallow curves of the same endpoint. More signal per atom.

META_RULE_U brain-mechanism-vs-caricature: CFU IS the brain mechanism
(Tonegawa). v6 STRENGTHENS the mechanism's measurement (bigger probe,
gradient sampling, multi-atom co-importance) without substituting any
smooth function of H or magnitude proxy. The leave-one-out ablation
against held-out probe set is preserved load-bearing.

## v6 mechanism summary

```
ARM_BASELINE_RANDOM_IMPORTANCE     uniform random control rail
ARM_TRACE_ONLY                     v3 retrieval-trace control;
                                    expected cor~+0.83 (degree-skew
                                    rail; verifies fairness boundary
                                    where it should fail)
ARM_CFU_LEAVE_ONE_OUT_LARGE_PROBE  v5 mech + L1 (N_PROBE=400, M_HELDOUT=400)
ARM_CFU_LEAVE_K_OUT                L2 K=5 cohort co-importance
ARM_CFU_CONTINUOUS_DOWNSCALE       L4 gradient ablation integral signal
```

L3 alpha-sweep applies to ALL arms (each arm runs at all 4 alphas).

ALL arms share workload + retrieved/unretrieved partition per
(alpha, seed); differ only in importance-scoring axis.

## ARMS (5 mandatory; pre-reg discipline; SCHEMA-VET 5b per-arm scope)

5 arms; per (alpha, seed) all 5 fired. See cell ARM_NAMES list.

## Pre-reg bands (HARD-LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS)

HARD_PASS (all 4 must hold):
  1. best v6 CFU sel_unretr asymmetry >= 0.15
     (rec_UNRETR_random_at_alpha - rec_UNRETR_cfu_at_alpha across best
     (CFU_arm, alpha) combo; ORIGINAL Path A PASS bar)
  2. AND cor(best_CFU, |W|) < 0.30 absolute (META_RULE_F fairness; v5
     win preserved)
  3. AND mechanism fires (n_downscaled > 0 AND n_ablations > 0 AND
     cfu_variance > 0 on EACH CFU arm at EACH alpha)
  4. AND best_v6_sel >= V5_BASELINE_SEL_CFU + 0.05
     (V5_BASELINE_SEL_CFU = +0.037 measured 2026-06-27 in
     data/exp_edge_importance_v5_CFU_counterfactual_utility_v1/
     metrics.json; v6 lift bar = +0.087 absolute)

HARD_FAIL:
  A. fairness regression (any CFU arm at any alpha |cor| >= 0.30)
  B. best_v6_sel <= V5_BASELINE_SEL_CFU (stronger regime did NOT help)
  C. mechanism inert (n_downscaled == 0 OR n_ablations == 0 OR
     cfu_variance == 0 on any CFU arm at any alpha)
  D. saturation: all 5 arms across all alphas within 0.05 on
     rec_RETRIEVED
  E. D3 any caught exception
  F. D4 cardinality breach: observed_arm_entries != 60 (full) or != 5
     (smoke)

MIDDLE_BAND: HONEST_BOUND if all hold:
  - best_v6_sel in [0.08, 0.15]
  - fairness held (|cor| < 0.30 on best CFU arm)
  - mechanism fired
  - v6 lift over v5 >= +0.02 (stronger regime DID help, modestly)
  -> Ship as new band annotation; lifts ceiling estimate for M-CFU family.

## Cardinality (D4 META_RULE_H mandatory)

EXPECTED_N_UNITS = len(ALPHA_GRID) * len(SEEDS) * 5 arm entries
                  = 4 * 3 * 5 = 60 arm entries TOTAL (full mode)
HARD_FAIL_CARDINALITY_BREACH = observed_n_arm_entries != 60.

Smoke EXPECTED_N_UNITS = 1 * 1 * 5 = 5 arm entries (ALPHA_GRID=[2.5];
SEEDS=[7]).

Per-(alpha, seed) partial uses compound key "alpha{X.X}_seed{Y}"
via write_partial_key (12 partial files full mode).

## Discriminator-must-survive-scale (D1)

Smoke uses FULL-N (N=512), FULL probe set (M_HELDOUT=400,
N_PROBE_BATCH=400), 1 representative alpha (2.5), 1 seed, reduced
J_composite (1500 vs 3000), reduced CFU_EVAL_FRAC (0.30 vs 0.50).

D1 GATE: smoke must measure best_v6_CFU_sel > V5_BASELINE_SEL_CFU +
0.02 OR explicit halt-and-route-back.

Note: USER 2026-06-27 NO LOCAL directive => no local smoke; cell ships
to remote_cpu_queue directly. Smoke config defined here for cell
completeness + remote --smoke invocation if needed.

## Substrate-only-decode gate (load-bearing)

n_llm_calls per (alpha, seed) = 0 (numpy-only mechanism; substrate
primitives only; no transformers / no encoders).

## Real data / synthetic provenance

Random bipolar key/value pairs (matches v3/v4/v5 base; the mechanism
is about importance scoring + pruning + held-out ablation, NOT corpus
semantics). allow_synthetic=True appropriate.

## Compute budget

Per (alpha, seed): O(setup ~3-5s + 3 CFU variants ~30-60s each + 5
arms ~5s each) ~= 100-200s.

Total full: 4 alphas * 3 seeds * 150s avg = ~30 min. Continuous
downscale variant is 5x slower per cohort due to gradient sampling
(but cohort count CFU_EVAL_FRAC * M_TOTAL / K is reduced via the
divisor); net: continuous arm ~3x cost of large-probe arm.

Per-cell timeout: 5400s (1.5hr; ample buffer for queue contention +
cold start + alpha-sweep variance + 4x larger probe vs v5).

Estimate justification: v5 single-alpha full was ~50-60s for 3
seeds. v6: 4x alphas + 4x probe + 3 CFU variants per (alpha, seed) ~=
4 * 4 * 3 * 20s = 960s = 16 min nominal. 5400s = 5.6x buffer.

## Honest scope

This cell tests whether 4 strengthening levers (bigger probe + leave-
K variant + alpha sweep + continuous gradient ablation) lift CFU
sel_unretr above the +0.15 PASS bar AND clear v5_baseline+0.05 lift
gate. It does NOT test:
  - Other backup mechanisms (M-SURP, M-MI, M-BTSP, M-KSHELL, M-JL;
    drill 4 ranks 2-6; separate cells if v6 still MIDDLE_BAND).
  - CFU x TRACE composition (v5 ARM_COMBINED; dropped from v6 because
    composition was HARD_FAIL in v5; cleaner to isolate CFU
    strengthening first; composition can return if v6 PASSes).
  - CFU x NREM-replay (v4 modulator); follow-up if v6 PASSes.
  - Per-cluster CFU (ultrametric-cluster level); honest-negative
    retreat path from drill.

## Verdict logic (3-class)

HARD_PASS only if all 4 HARD_PASS conditions met.
HARD_FAIL if any HARD_FAIL trigger fires (A-F).
MIDDLE_BAND if HONEST_BOUND conditions met (sel in [0.08, 0.15] +
  fairness held + lift >= 0.02 over v5).
HARD_FAIL otherwise (default).

## SCHEMA-VET 5b per-arm HP scope

Each arm's metrics fully reported per (alpha, seed) in
metrics.json per_alpha_seed[].arms[]:
  - arm_name
  - alpha (actual, computed)
  - recall_old_RETRIEVED (per-arm; per-(alpha, seed))
  - recall_old_UNRETRIEVED (per-arm; per-(alpha, seed))
  - recall_recent
  - cor_importance_magnitude
  - importance_min / max / mean / std
  - n_downscaled / downscale_frac_actual
  - wall_s

Verdict reads per-arm aggregates per-alpha across seeds; best
selection is over (CFU_arm, alpha) cartesian product on sel_unretr
asymmetry. Per Fix #28: verdict reads metrics.json per-arm fields,
NOT summary text.

## Per-arm fields in summary

Top-level metrics.json includes:
  - per_alpha_seed[] full per-unit
  - baseline_heldout_rec_{large_probe, leave_k, continuous} per (alpha, seed)
  - n_ablations_{large_probe, leave_k, continuous} per (alpha, seed)
  - cfu_variance_{large_probe, leave_k, continuous} per (alpha, seed)
  - cardinality_ok bool
  - expected_n_units / observed_n_units
  - v5_baseline_sel_cfu (constant for cross-cell comparison)

## REQUIRED_FIELDS for metrics.json

- anchor_name (str)
- verdict (str; one of HARD_PASS / MIDDLE_BAND / HARD_FAIL)
- verdict_msg (str)
- summary (str)
- config_version (str)
- N, M_RECENT, M_HELDOUT, alpha_grid, n_seeds (ints / list)
- expected_n_units, observed_n_units, cardinality_ok
- per_alpha_seed[] with arms[] full per-arm scope
- v5_baseline_sel_cfu (float; cross-cell anchor)
- n_llm_calls_total (must be 0)

## Cross-cell context

If v6 HARD_PASS: M-CFU family chain-grade-eligible for cortex importance
gate; queue cluster-level CFU (per-ultrametric-cluster) + CFU x NREM-replay
composition as follow-ups.

If v6 MIDDLE_BAND HONEST_BOUND: file ceiling estimate for M-CFU at
+~0.10 sel_unretr; route to M-SURP (rank 2; P_deflated=0.48) as next
backup mechanism per drill priority. Composition CFU x SURP remains
candidate per drill "Single highest-leverage composition" note.

If v6 HARD_FAIL: route to M-SURP directly; M-CFU family ruled out at
substrate's scale; substrate may require different perturbation regime
than per-atom ablation (drill honest-negative path: schema-level
ultrametric cluster importance + Wave 3 ANCHOR 2 TWO_TIER promotion
heuristic acceptance at MIDDLE_BAND ceiling).
