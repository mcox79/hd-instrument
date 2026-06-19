# exp_dev hand-off -- research: Multi-Substrate Engineered Architecture (3x)

## Filed-by
Research sub-agent, 2026-06-11

## Trigger
Research note: notes/research_drill_multi_substrate_engineered_3x_2026-06-11.md
Topic: Implementable multi-W-matrix substrate architectures with migration protocols, routing rules, empirical test predictions

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
All 5 priority anchors below are CPU-only. None are pause-gated for CPU queue.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered by P_deflated x implementation_cost_inverse)

### Anchor 1 (HIGHEST PRIORITY -- CPU, ~1 hour, solves protected subspace directly)
Pointer: Architecture 10 (Crystallized) in research note
Substrate-product reading: W_crystallized is a second Substrate instance with write-protection
  enforced at the Python API level. Items confirmed N_confirm=5 times migrate from W_plastic
  to W_crystallized. After crystallization, W_plastic writes of 500+ new items should cause
  < 2% recall degradation in crystallized items. This is the engineering escape from the
  protected-subspace problem that algebraic approaches could not solve.
Tier hint: CPU; 2 Substrate instances; migration loop ~50 LOC; no GPU needed
Why-now: Directly resolves the "protected subspace" gap that prior 5-stream drills identified
  as requiring substrate algebra features we don't have. Engineering escape is available NOW.
  P_deflated=0.55 -- highest confidence of the batch.
Contract: HARD-PASS = crystallized recall@1 < 2% degradation after 500 new W_plastic writes.
          HARD-FAIL = crystallized recall@1 degrades > 10%.

### Anchor 2 (HIGH PRIORITY -- CPU, ~1 hour, solves reliability under noise)
Pointer: Architecture 8 (Redundant 3x) in research note
Substrate-product reading: 3 Substrate instances (W_primary, W_replica_1, W_replica_2).
  Writes go to W_primary; replicated to W_replica_1 synchronously; W_replica_2 with delay.
  Retrieval vote across W_primary + W_replica_1; W_replica_2 as tiebreaker.
  Under Gaussian noise injection (sigma=0.1 on stored vectors), vote-decoded recall@1
  should be > 0.80 vs. single-W degrading to ~0.60.
Tier hint: CPU; 3 Substrate instances; vote function ~20 LOC; erasure coding analog
Why-now: This is the lowest-risk architecture (redundancy is solved engineering). Tests a
  fundamental reliability property. P_deflated=0.55.
Contract: HARD-PASS = vote recall@1 > 0.80 at sigma=0.1 noise injection.
          HARD-FAIL = vote recall@1 < 0.65 (not better than noisy single-W).

### Anchor 3 (HIGH PRIORITY -- CPU, ~3 hours, tests capacity cliff escape)
Pointer: Architecture 1 (Fast/Slow CLS) in research note
Substrate-product reading: 2 Substrate instances. W_fast receives all writes; migration to W_slow
  via replay for items with retrieval_count >= 3. At K=600 items (above single-W cliff at N=1024),
  migrated items should maintain recall@1 >= 0.75 while single-W at K=600 degrades to ~0.40.
  This directly validates the Teeters et al. (Frontiers Neurosci 2023) finding in the substrate context.
Tier hint: CPU; 2 Substrate instances; migration loop + replay logic ~80 LOC
Why-now: Published HDC precedent (Teeters 2023) shows 15-35x efficiency gain for SDM over
  superposition at K>1000. Our substrate is the superposition case. Fast/Slow CLS is the
  direct migration path. P_deflated=0.50.
Contract: HARD-PASS = migrated item recall@1 >= 0.75 at K=600, N=1024, with single-W baseline <= 0.50.
          HARD-FAIL = migrated recall@1 < 0.55 (no improvement over single-W).

### Anchor 4 (MEDIUM PRIORITY -- CPU, ~2 hours, compositional crosstalk reduction)
Pointer: Architecture 6 (Per-Role: Storage + Computation + Working Memory) in research note
Substrate-product reading: 3 Substrate instances: W_store (persistent), W_compute (clearable
  ephemeral), W_wm (superposition vector, capacity ~7). Intermediate reasoning steps go to
  W_compute only and are cleared between episodes. Final committed results go to W_store.
  Multi-step algebraic manipulation (3 bind->query->rebind operations) should achieve
  precision > 0.90 with isolated W_compute vs. degradation in single-W.
Tier hint: CPU; 3 Substrate instances; routing wrapper ~100 LOC; clearable W_compute is just .reset()
Why-now: Resolves compositional crosstalk from ephemeral intermediate results polluting
  the persistent store. Directly useful for the multi-step reasoning use case. P_deflated=0.48.
Contract: HARD-PASS = 3-step operation precision > 0.90 with isolated W_compute.
          HARD-FAIL = no improvement vs. single-W at 3 steps.

### Anchor 5 (MEDIUM PRIORITY -- CPU, ~3 hours, capacity cliff priority lane)
Pointer: Architecture 9 (Excitability-Gated Allocation) in research note
Substrate-product reading: 2 Substrate instances. Incoming bundle scored by excitability
  E(bundle) = mean(|components|). Bundles with E > E_threshold go to W_priority (stays well below
  its own cliff). At K/N=0.70 (above the single-W K/N=0.56 cliff), high-priority items
  should maintain recall@1 > 0.90 because they are in W_priority which has spare capacity.
Tier hint: CPU; 2 Substrate instances; excitability score ~5 LOC; lateral inhibition demotion
  requires a ranking step over stored items (~30 LOC using existing similarity query)
Why-now: Priority protection above the capacity cliff is a clear product capability
  (critical facts always retrievable even when KB is overloaded). Biologically grounded
  in CREB/engram allocation (Tonegawa lab). P_deflated=0.45.
Contract: HARD-PASS = priority item recall@1 > 0.90 at K/N=0.70.
          HARD-FAIL = priority items degrade at same rate as non-priority items.

---

## Context pointers (file paths, not summaries)

- Research note (full architecture specs + migration protocols + routing rules):
  d:/AI/hd-instrument/notes/research_drill_multi_substrate_engineered_3x_2026-06-11.md

- Substrate capability map (current state of all capabilities):
  d:/AI/hd-instrument/notes/substrate_capability_map.md

- Substrate v3.0 compositional cliff note:
  d:/AI/hd-instrument/memory/substrate_v3_compositional_cliff_crossed.md

- Static robust / dynamic fragile finding:
  d:/AI/hd-instrument/memory/substrate_static_robust_dynamic_fragile_2026-06-10.md

- Primitives YES integration NO finding:
  d:/AI/hd-instrument/memory/substrate_primitives_yes_integration_no_2026-06-10.md

- Cross-domain retraction (2026-06-10):
  d:/AI/hd-instrument/memory/substrate_cross_domain_retraction_2026-06-10.md

- PP-225 fact-scaling correction:
  d:/AI/hd-instrument/memory/pp225_fact_scaling_correction_2026-06-10.md

---

## Contract

The exp_dev agent owns: anchor grid design, sweep parameters, threshold formulas, queue assignment, smoke gate, and post-ship remote verify.

Research has provided: architecture specifications, migration protocols, read/write routing rules, P_deflated estimates, HARD-PASS / HARD-FAIL thresholds, and priority ordering.

Research has NOT provided: specific Python implementation code, exact hyperparameter values for migration thresholds (N_confirm, C_replay, E_threshold, theta values), or queue cell names. These are exp_dev design decisions.

Implementation note from research: every architecture in this batch requires ONLY multiple Substrate Python instances + a routing wrapper. No changes to substrate core required. This is by design: the multi-substrate architecture engineering rule is "add instances, not primitives."

---

## Autonomy declaration

Exp_dev has full autonomy to:
- Reorder the anchor sequence based on current queue depth and runner state
- Combine anchors 1+2 into a single cell if they share setup code (they do: both use multiple Substrate instances)
- Skip architectures with P_deflated < 0.40 if queue is full
- Add intermediate diagnostic steps (e.g., single-W baseline measurement must always be included as the control condition)

Exp_dev should NOT:
- Deploy architectures 4 (Per-Domain) or 7 (Hierarchical cross-domain) without additional Research input on the domain classifier design
- Treat any HARD-PASS result as a cap_map update without Orchestrator/verdict_handler confirmation
- Use GPU for any of the 5 priority anchors (all are CPU-runnable)
