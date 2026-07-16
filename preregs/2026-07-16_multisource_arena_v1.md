# Pre-reg: multi-source memory-assimilation arena + ingest gate (v1)

- **Cell:** `experiments/exp_multisource_arena_v1.py`
- **Metrics:** `data/exp_multisource_arena_v1/metrics.json`
- **Date:** 2026-07-16  **Author:** exp_dev
- **Design source:** `notes/research_multisource_memory_assimilation_arena_2026-07-16.md` (Part 5),
  4th axis from `notes/research_surprise_decomposition_unexpectedness_vs_importance_2026-07-16.md`,
  pairwise schema-fit from `notes/research_schema_fit_derivability_signal_upgrade_2026-07-16.md`,
  route gate from `notes/research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`.
- **Builds on:** `experiments/toy_multisource_arena_validity_2026-07-16.py` (self-tests + copy-detector reused verbatim).

## What it is
Parametric multi-source arena with FOUR genuinely-separate generative processes
(temporal Markov arrival stream / schema similarity graph from a disjoint seed
corpus / source population with a hidden copy-dependence graph / an INDEPENDENT
consequence-dependency graph). Ground-truth TRUE/FALSE from a hidden generator
combining four independent latents via a noisy sigmoid (held SEPARATE from every
signal; not derivable from any single signal by construction). Four pluggable
signal functions (`SIGNAL_FUNCS`): unexpectedness = online schema-conditioned PE;
schema_fit = PAIRWISE Resource-Allocation graph index (Tier A; SR/PPR resolvent
= pluggable slot); recurrence = copy-corrected corroboration (dependence-detected,
not naive count); importance = intrinsic downstream-reach centrality (exogenous
query-relevance = pluggable slot, default OFF). Route-based gate as a SEPARATE
module (`GATE_FUNCS`: route / weighted_sum), combination form + weights as config.

## Compute architecture
Class (b) sequential-CPU, justified: pure-numpy, FULL wall time ~2.5s (well under
the 10s batching threshold). No torch, no GPU speedup available or needed. No
substrate atoms persisted; no store writes; no origin push.

## Staging (report BOTH, in order)
- **A** generator self-tests (reliability->accuracy; copies share parent errors;
  copy detector recovers hidden clusters; schema RA-index non-degenerate spread;
  importance independent of schema_fit; conflict injection produces disagreement;
  truth base-rate non-degenerate). Fail => abort (correlations meaningless).
- **B** ARENA-VALIDITY precondition at scale FIRST (pairwise |r|, conditional-MI
  per signal | other three, copying stress-test). Arena must pass before any gate
  result is trusted.
- **C** GATE BASELINE only if arena valid: does the 4-axis gate beat the best
  single-signal on held-out within-cell (stratified) AND marginal recovery.

## Pre-registered bands

### Arena validity (primary precondition)
- **HARD-PASS (ARENA_VALID):** all pairwise |r| < 0.30 AND copying separates
  independent > copied >= 1.5x with worst-p < 0.05 AND >= 3/4 signals retain
  conditional-MI > 1e-3 after conditioning on the other three.
- **HARD-FAIL (ARENA_INVALID):** any pairwise |r| > 0.60 OR copying ratio < 1.05
  OR copying worst-p >= 0.05 (arena still degenerate; do not trust the gate).
- **MIDDLE:** re-collapse concern band, any |r| in [0.30, 0.60].
  (~0.2 truth-coupling floor is expected/acceptable per design note.)

### Gate baseline (secondary; trusted only if arena valid/middle)
- **within-cell** balanced-acc, stratified on the 3 core note-signals (surprise x
  schema-fit x corroboration); baseline = best single signal measured WITHIN-CELL
  (a stratification-axis signal is pinned to ~0.5, so best-single is selected on
  the within-cell metric to stay fair).
- **HARD-PASS (GATE_ROUTE_WINS):** 4-axis ROUTE beats best-single-within-cell by
  >= 15% relative error reduction, baseline in (0.05, 0.95), arms differ verified.
- Localizers (MIDDLE): `GATE_LOGISTIC_WINS_ROUTE_UNCALIBRATED` (logistic within-
  cell >= 15% but route < 15%); `GATE_MARGINAL_MULTISIGNAL_ONLY` (multi-signal
  value only on the marginal held-out metric, not the strict within-cell one).
- **HARD-FAIL (GATE_NO_MULTISIGNAL_VALUE):** no gate variant beats best-single on
  any metric (rel err reduction <= 0 everywhere) => signals redundant.

### Discriminator-fires / fairness gates
- Multi-seed (smoke 3, full 5) per the confidence/discriminator multi-seed rule.
- baseline_in_band: best-single balanced-acc in (0.05, 0.95).
- arms_differ_verified: route / weighted_sum / best_single decisions hash-distinct.
- Ground-truth held-out (test_frac split); gate + baseline fit on TRAIN only.
- Determinism: fixed integer seeds; no hash()-derived seeds; sorted(set) ordering.

## Config knobs (nothing hardcoded)
n_claims, n_schema_entities, n_communities, target_intra/inter_degree,
claim_intra_frac, n_sources, reliabilities, copy_parent graph, copy_fidelity,
assert_prob, specialization (<=0.6), n_topics, self_transition, conflict_frac,
conseq_edge_p, conseq_reach_k, query_relevance_on/weight, truth-generator weights
(w_schema/w_source/w_temporal/w_importance), copy-detector thresholds, test_frac,
cell_bins, min_cell.
