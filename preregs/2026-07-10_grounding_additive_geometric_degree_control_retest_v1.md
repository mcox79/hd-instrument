# Pre-reg: additive-geometric-code inductive-inference DEGREE-CONTROL RETEST v1

- anchor_name: `grounding_additive_geometric_degree_control_v1`
- cell: `experiments/exp_grounding_additive_geometric_degree_control_retest_v1.py`
- metrics: `data/exp_grounding_additive_geometric_degree_control_v1/metrics.json`
- date: 2026-07-10
- queue: overnight_queue (GPU) FULL; local self-test + local CPU smoke are the pre-flight gates (KGE FULL is GPU-heavy; local is smoke-only, USER-locked)
- seeds FULL: [7, 13, 17] (3, matches prior); EXPECTED_N_UNITS = n_seeds

## Question
The prior FULL (`grounding_additive_geometric_inductive_v1`, MIDDLE_BAND) measured COMPLETABLE reach@1
TRANSE=0.187 DISCRETE=0.089 (d=0.098, just below the 0.10 bar). The landed VET flagged PROMISING-BUT-CONFOUND-OPEN:
no degree stratification, no popularity baseline, and a DEGENERATE DistMult (0.0116 < random 0.0142). Prior #4
established KGE held-out wins on this ConceptNet subgraph are largely PA/DEGREE artifacts. Decisive question: does the
TransE-over-discrete margin SURVIVE degree/frequency control, or is it a popularity shortcut?

## Arms (PAIRED: same held-out split + completable subset + candidate negatives + degree strata per seed)
- DISCRETE_HRR_BIND (ARM A, current substrate multiplicative binding code)
- TRANSE_ADDITIVE (ARM B, mechanism under test; h+r~=t)
- DISTMULT_TRAINED (ARM C, NEW convergent bilinear KGE; logistic loss, light L2, no unit-renorm)
- POPULARITY_DEGREE (ARM D, NEW; score = visible-graph degree of candidate; no geometry)
- RANDOM_CODES (control / codes-necessary null)
- TRANSE_TRANSDUCTIVE (oracle / must-fire)
- DISTMULT_TRANSDUCTIVE (NEW convergence check for ARM C; must be >> random or ARM C is untrustworthy)

## Primary metric
reach@1 = filtered Hits@1 on the COMPLETABLE held-out subset (identical to prior), PLUS per-degree-stratum reach@1
for every arm. Strata = LOW/MID/HIGH tertiles of the TRUE-TAIL visible-graph degree (data-driven quantiles).

## Pre-registered bands (picked BEFORE the run; the decision is DEGREE-STRATIFIED margin SURVIVAL, not an aggregate delta)
- GEOM_MARGIN = 0.05 (aggregate materiality; prior aggregate was 0.098)
- STRAT_MARGIN = 0.03 (tail survival: transe-minus-discrete >= this in BOTH LOW and MID strata)
- TIE_EPS = 0.02 (collapse: transe-minus-discrete <= this in a tail stratum)
- POP_GAP = 0.05; POP_RECOVER_FRAC_MAX = 0.60 (PASS); POP_RECOVER_FRAC_HI = 0.80 (FAIL)
- RANDOM_CEIL = 0.15; ORACLE_FIRE_MARGIN = 0.15; DM_CONVERGE_MARGIN = 0.15; MIN_STRAT_Q = 40
- HELDOUT_FRAC = 0.30; MIN_HELDOUT_COMPLETABLE = 60; N_RANK_NEG = 99

## Decision (HARD-PASS / HARD-FAIL, both bands, before running)
- **HARD_PASS_ADDITIVE_GEOMETRY_IS_THE_LEVER** = aggregate margin ok (transe1 >= discrete1 + GEOM_MARGIN)
  AND tail survival (LOW and MID strata each n >= MIN_STRAT_Q and transe-minus-discrete >= STRAT_MARGIN in BOTH)
  AND popularity does NOT recover (transe1 - pop1 >= POP_GAP AND pop1/transe1 <= POP_RECOVER_FRAC_MAX)
  -> additive geometry is a genuine inductive-inference lever (build it as barrier #1's specific objective).
- **HARD_FAIL_GEOMETRY_IS_POPULARITY_SHORTCUT** = margin collapses (transe-minus-discrete <= TIE_EPS in LOW or MID)
  OR popularity recovers (transe1 - pop1 <= TIE_EPS OR pop1/transe1 >= POP_RECOVER_FRAC_HI)
  -> the win is mostly the degree/popularity shortcut; geometry is not the lever; redirect to knowledge-richness.
- **MIDDLE_BAND_PARTIAL_DEGREE_AMBIGUOUS** = otherwise.
- Gating INCONCLUSIVE arms: enough completable, negatives_valid (random <= RANDOM_CEIL), oracle_fires.
- DISTMULT convergence is REPORTED (distmult_converged), NOT in the PASS/FAIL decision path.

## Self-test (proves the NEW discriminators FIRE) -- MEASURED@ local self-test 2026-07-10, SELFTEST_PASS 16.5s
- GRID_ADDITIVE (degree-varied, degree-independent geometry): grid_transe=0.40, grid_pop=0.00, grid_random=0.003,
  transe_low_stratum=0.375 -> TransE recovers + survives in LOW stratum + beats popularity (delta 0.40 >= 0.15).
- PLANTED_POPULARITY: pop_pop=0.2275 (baseline FIRES, ~22x chance), pop_transe=0.1232 (TransE does NOT beat popularity).
- NONADDITIVE: nonadd_transe=0.003 (null). gap (grid-nonadd)=0.40 >= 0.20; arms differ.
- DistMult convergence: probe on real subgraph -> DM_ORACLE transductive hits1 ~1.0 >> random 0.01 (converges).

## Compute architecture
class: (a) batched-GPU. KGE = batched embedding-lookup + vectorized loss; discrete arm = batched InfoNCE + HRR bind;
ranking = single batched reduction per arm on a shared candidate tensor; popularity = degree gather. Storage: SHARDED.
n<=5000, dim=64. Routes to overnight_queue (GPU) for FULL. Self-test + CPU smoke are the local pre-flight gates.

## SCHEMA-VET fields
- cardinality_ok: True (EXPECTED_N_UNITS = n_seeds; per-seed asserts all 7 arms produce >= 5 distinct sigs)
- arms_differ_verified: True (>= 5 distinct sigs among 7 arms per seed)
- final_metrics_atomicity: tmp_replace (write_metrics + os.replace; write_partial per seed)
- crlb: filtered Hits@1 chance floor = 1/(N_RANK_NEG+1) ~ 0.01 THEORETICAL; discriminator_reachability: OK
- baseline_in_band: RANDOM <= 0.15 null; ORACLE >= random+0.15 must-fire; POPULARITY = measured confound-baseline
- calibration_check: default_ok_for_this_regime (split/negatives inherited from phase-0 M5 / prior cell; degree tertiles
  are data-driven quantiles, not tuned; KGE hyperparams pre-registered standard defaults)
- progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm/per-stratum flush)
- start_marker_written / crash_diagnostic_present: True; except SystemExit: raise before except Exception (no BaseException)
- HYPOTHESIZED prior numbers tagged MEASURED@data/exp_grounding_additive_geometric_inductive_v1/metrics.json

## Smoke preview (2 seeds n=1525; REPORT-ONLY, telemetry may wash at FULL scale -- HOLD mechanism story until landed-VET)
MEASURED@/tmp smoke 2026-07-10 (pre-DistMult-fix run): HARD_FAIL_GEOMETRY_IS_POPULARITY_SHORTCUT; d(transe-discrete)
LOW=-0.030 MID=+0.039 HIGH=+0.153 (win concentrated in HIGH-degree stratum, reverses in tail); pop_recover_frac=0.70;
DISCRETE far-neg AUC=0.708 reproduces M5 0.695; oracle fires 0.805.
