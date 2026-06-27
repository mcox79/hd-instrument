# Prereg: edge_importance_v5_CFU_counterfactual_utility_v1

Date: 2026-06-27
Anchor: edge_importance_v5_CFU_counterfactual_utility_v1
Cell: experiments/exp_edge_importance_v5_CFU_counterfactual_utility_v1.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Wave: Drill 4 rank-1 backup; brain-grounded importance via leave-one-out ablation
Primitives composed:
  - hdlab/edge_importance.py (chain-grade; 2026-06-26)
  - experiments/exp_edge_importance_v3p2_trace_only_with_D1_audit_v1.py (TRACE rail referent)
  - experiments/exp_edge_importance_v4_NREM_replay_modulated_trace.py (v4 schedule pattern referent)

## Motivation

v1-v4 of edge-importance (PageRank-centrality + retrieval-trace +
ultrametric-coreness + NREM-replay-modulated-trace) all converged to
MIDDLE_BAND. Diagnosis (drill_cortex_importance_backup_mechanisms
2026-06-27): all four variants are smooth functions of accumulated
activity along a graph-structural axis. The substrate's bound-pair graph
H[i,j] populates with degree-skew under composite-query workloads; any
smooth function that integrates over H inherits that skew. Result:
top-K importance correlates with degree, and the discriminator's
"retrieved-old" set IS the high-degree set; sel_unretr asymmetry is
structurally bounded by the workload degree distribution.

The drill identified M-CFU (counterfactual utility / leave-one-out
ablation) as rank-1 backup mechanism (P_deflated=0.50; novel-synthesis
cap honored). M-CFU sources importance from a categorically orthogonal
signal axis: ABLATION RECALL DELTA against a HELD-OUT probe set.

Brain analog (chain-grade in brain): Tonegawa lab optogenetic engram
silencing (Liu Cell 2012, Ramirez Science 2013, Tonegawa Cell Reports
2015 review) - engram cells in DG/CA1 are tagged via channelrhodopsin
during learning; selectively silencing them during recall abolishes the
memory. This IS counterfactual-utility per neuron, measured
experimentally; chain-grade in neuroscience.

## v5 mechanism (CFU; leave-K-out ablation)

```
importance_CFU[atom] = baseline_recall(P_held) - recall_when_atom_ablated(P_held)
```

- Baseline_recall is computed on a HELD-OUT probe set (M_HELDOUT=100
  atoms written into W but never queried during WAKE-trace population;
  decouples CFU from retrieval-trace signal).
- Cohort leave-K-out (COHORT_K=10): atoms partitioned into N_CFU_COHORTS
  cohorts of K atoms each; per-cohort recall delta divided by K assigned
  to each atom in the cohort. Cohort averaging amplifies signal beyond
  per-atom noise (established lit pattern: "leave-K-out" for noisy CFU).
- Atoms outside scored cohorts retain importance = 0 (compute bound).

## Composition (CFU x TRACE)

```
importance_COMBINED[atom] = cfu_normalized[atom] * trace_normalized[atom]
```

Multiplicative composition tests whether CFU and TRACE add orthogonal
information. Per design doc: "requires BOTH utility AND surprise" -
atoms with high CFU AND high trace get highest composition score.
Filters out high-utility-but-redundant atoms (CFU absorbed by
neighbors) AND novel-but-useless atoms (high trace but low CFU).

## ARMS (4 mandatory; pre-reg discipline)

- ARM_BASELINE_RANDOM_IMPORTANCE (uniform random; sanity rail)
- ARM_TRACE_ONLY (v3 lineage; retrieval-trace; rail vs categorically
  different signal axis)
- ARM_CFU_LEAVE_ONE_OUT (the MECHANISM; cohort-K=10 ablation against
  held-out probe set)
- ARM_COMBINED (CFU * TRACE composition; tests orthogonal stacking)

ALL arms share the SAME workload, the SAME retrieved/unretrieved
partition; differ only in importance-scoring + which counters they
consume.

## Pre-reg bands (HARD-LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS)

HARD_PASS (all 4 must hold):
  - best CFU sel_unretr asymmetry >= 0.15
    (rec_UNRETR_random - rec_UNRETR_cfu >= 0.15; ORIGINAL Path A PASS
    bar; CFU brain-grounded prior says P=0.50)
  - AND cor(CFU_importance, |W|) < 0.30 (USER fairness gate META_RULE_F)
  - AND mechanism fires (n_downscaled > 0 AND n_ablations_evaluated > 0
    AND cfu_variance > 0)
  - AND COMP over CFU_ONLY: combined sel >= cfu_sel + 0.03
    (composition adds value; if not, composition is over-engineering)

HARD_FAIL:
  - All four arms within 0.05 of each other on rec_RETRIEVED (saturation;
    regime too easy)
  - OR cor(CFU, |W|) >= 0.30 (fairness regression)
  - OR n_downscaled == 0 OR n_ablations_evaluated == 0 OR
    cfu_variance == 0 (inert mechanism)
  - OR ARM_COMBINED UNDERPERFORMS ARM_CFU by > 0.02 on sel_unretr
    (composition actively hurts)
  - OR any caught exception (D3 no-silent-except)

MIDDLE_BAND: fairness held + mechanism fired + some CFU sel_unretr
  signal but full PASS not cleared.

## Cardinality (D4 mandatory)

EXPECTED_N_UNITS = len(SEEDS) * 4 arm entries = 3 * 4 = 12 arm entries
TOTAL across full run.
HARD_FAIL_CARDINALITY_BREACH = observed_n_arm_entries != 12.

Smoke EXPECTED_N_UNITS = 1 * 4 = 4 arm entries.

## Discriminator-must-survive-scale (D1)

Smoke uses FULL-N parameters (N=512, M_OLD=600, M_RECENT=400,
M_HELDOUT=100) with reduced J_composite=1500 (half full) +
N_CFU_COHORTS reduced via CFU_EVAL_FRAC=0.30 (smoke) vs 0.50 (full) +
SEEDS=[7] + N_QUERIES=100 + N_PROBE_BATCH=50 (smoke) vs 100 (full).
alpha=2.148 at full N=512 (>= 1.5 high-alpha regime; held-out atoms
included in M_TOTAL).

Note: USER 2026-06-27 NO LOCAL directive => no local smoke. Smoke
parameters defined here for cell completeness + production-mode dispatch
(smoke could be invoked remotely if needed via --smoke flag).

## Substrate-only-decode gate (load-bearing)

n_llm_calls per seed = 0 (numpy-only mechanism; substrate primitives
only; no transformers / no encoders).

## Real data / synthetic provenance

The cell uses random bipolar key/value pairs (matches v3/v4 base; the
mechanism is about importance scoring + pruning + held-out ablation,
NOT corpus semantics). allow_synthetic=True is appropriate here per
scope; cell asserts no real-corpus dependency.

## Compute budget

Full mode: per seed ~ N_CFU_COHORTS (~50-110) * (W_ablate + recall on
N_PROBE_BATCH=100) for the CFU phase + 4 arms * (1 prune + 3 recall
sweeps of N_QUERIES=200) for the eval phase. At N=512 + M_TOTAL=1100:
  - CFU phase: ~50 cohorts * (~5ms ablate + ~50ms recall) = ~3s/seed
  - eval phase: 4 arms * ~200 recall ops * ~1ms = ~1s/seed
  - WAKE-trace phase: 3000 composite queries * ~3ms = ~10s/seed
Estimated total: ~15-20s/seed * 3 seeds = ~50-60s remote CPU. Cap at
1800s per-cell timeout to allow for slowness / queue contention.

## Honest scope

This cell tests whether COUNTERFACTUAL-UTILITY (ablation-based
importance against held-out probe set) breaks the H-smooth-integral
saturation of v1-v4 and lifts the sel_unretr discriminator past the
+0.15 PASS floor. It does NOT test:
  - Other backup mechanisms (M-SURP, M-MI, M-BTSP, M-KSHELL, M-JL;
    drill 4 rank 2-6; separate cells if M-CFU also MIDDLE_BAND).
  - Composition with NREM-replay (v4 mechanism; CFU x REPLAY is a
    follow-up cell if CFU HARD_PASS).
  - Per-cluster CFU (ultrametric-cluster level rather than per-atom;
    honest-negative retreat path from drill).

## Verdict logic (4-class)

HARD_PASS only if all 4 HARD_PASS conditions met.
HARD_FAIL if any HARD_FAIL trigger fires.
MIDDLE_BAND if mechanism fired + sel_unretr > 0 + fairness held but
  PASS gaps not cleared.
HARD_FAIL otherwise (default).

## SCHEMA-VET 5b per-arm HP scope

Each arm's metrics fully reported in metrics.json per_seed.arms[]:
  - recall_old_RETRIEVED (per-arm; per-seed)
  - recall_old_UNRETRIEVED (per-arm; per-seed)
  - recall_recent (per-arm; per-seed)
  - cor_importance_magnitude (per-arm; per-seed)
  - importance_min / max / mean / std (per-arm; per-seed)
  - n_downscaled / downscale_frac_actual (per-arm; per-seed)
  - wall_s (per-arm; per-seed)

Verdict reads per-arm aggregates not summary text (Fix #28); aggregate
fields per arm: mean_rec_RETRIEVED / std + cv, mean_rec_UNRETRIEVED,
mean_rec_recent, mean_cor_imp_W, mean_n_downscaled.
