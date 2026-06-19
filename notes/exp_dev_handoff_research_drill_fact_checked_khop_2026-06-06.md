# exp_dev hand-off -- research: fact_checked_khop optimization and robustness

Filed-by: research sub-agent (2026-06-06)
Trigger: Level-2 operational drill on Batch B HP winner (fact_checked_khop)
Research note: d:/AI/hd-instrument/notes/research_drill_fact_checked_khop_optimization_robustness_2026-06-06.md

## Pause state block

This file is auto-discoverable on exp_dev emergency-refill cycles.
Experiments proposed here are NEW anchors, not re-runs of existing ones.
All cells are CPU-feasible unless noted. No cloud needed for Cells 1-5.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev has full autonomy
over anchor names, sweep parameters, numerical thresholds, queue choice,
and pre-reg bands. This file provides TASK + WHY + CONTRACT only.

---

## Anchor Candidates (rank-ordered)

### Rank 1 -- Confidence-weighted aggregation AUC lift (CELL-2 equivalent)
Why now: Zero compute overhead; 1-day implementation; directly lifts adversarial
robustness of Batch B HP winner. Cheapest possible lift on the killer demo.
Substrate-product reading: replacing binary per-hop flag with C_min/C_chain
adds a richer adversarial signal without touching KF-1 architecture.
Tier hint: CPU smoke -> CPU full -> if AUC lift confirmed, ship to product layer
Anchor pointer: fact_checked_khop + confidence aggregation (C_min, C_chain product)

### Rank 2 -- Middle-hop adversarial injection localization (CELL-1 equivalent)
Why now: The key brittleness claim (error propagation misattributes localization
to later hops) is unvalidated. This is the decisive production gate test.
Substrate-product reading: if middle-hop localization accuracy < 0.65 (HF-1),
the current architecture needs backward chaining before K >= 5 deployment.
Tier hint: CPU only; K in {3,5}; injection positions {0, K//2, K-1}
Anchor pointer: fact_checked_khop adversarial middle-hop localization

### Rank 3 -- Per-hop Merkle chain + HP-12 V1 root composition (CELL-4 equivalent)
Why now: HP-12 V1 (< 1ms RSA accumulator) already validated. Extending to per-hop
Merkle chain is pure engineering; produces the cryptographically-verifiable
reasoning trace moat that no frontier system has.
Substrate-product reading: transforms "answer certified" into "per-hop reasoning
chain certified end-to-end" -- second-order audit moat.
Tier hint: CPU; engineering extension; target < 1ms overhead at K=20

### Rank 4 -- K-scaling latency parallelization (CELL-3 equivalent)
Why now: Sequential O(K) latency is production gap #1. If parallelization is safe
(accuracy within 0.005 AUC), this is a free throughput lift.
Substrate-product reading: enables K=20 production deployment at feasible latency.
Tier hint: CPU/GPU; measure latency at K in {5, 10, 20}

### Rank 5 -- Backward chaining accuracy lift (CELL-5 equivalent)
Why now: Required if Rank 2 (middle-hop localization) returns HF-1 result.
Only queue if Rank 2 reveals middle-hop localization accuracy < 0.85.
Substrate-product reading: backward pass catches error propagation that
forward-only misses; 2x KF-1 calls but higher adversarial robustness.
Tier hint: CPU; conditionally queued on Rank 2 outcome

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_fact_checked_khop_optimization_robustness_2026-06-06.md
- KF-1 prior results: search notes/ for KF-1 or hallucination detection AUC entries
- HP-12 V1 audit cert: search notes/ for HP-12 or RSA accumulator entries
- PP-11 BAND-LIFT K=20: search notes/ for PP-11 or K-hop K=20 entries
- Batch B HP results: search notes/ for fact_checked_khop or Batch B verdict entries

---

## Contract

exp_dev owns: anchor naming, sweep grids, HF/MID/HP numerical bands, queue routing,
pre-reg formulation, smoke gate, post-ship verify.

Research has delivered: mechanism identification, failure mode taxonomy, ranked
architectural tweaks, production readiness checklist, cross-domain analogues,
and P_deflated estimates for each claim.

## Autonomy declaration

exp_dev has full autonomy on implementation choices within the task scope above.
No inline experiment design has been provided. exp_dev reads the research note
for mechanism depth and designs anchors per its own judgment.
