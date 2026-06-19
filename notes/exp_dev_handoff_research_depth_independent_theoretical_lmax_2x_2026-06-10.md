# exp_dev hand-off -- research: depth-independent theoretical L_max (2x drill)

## Filed-by
Research sub-agent, 2026-06-10

## Trigger
Research note: notes/research_drill_depth_independent_theoretical_lmax_2x_2026-06-10.md
Topic: WHY per-level cleanup makes recall depth-independent; theoretical L_max; break conditions

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
All 5 anchors below are CPU-only (numpy/Hopfield; no torch.cuda dependency).
CPU anchors are NOT pause-gated per queue routing rules.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered)

### Anchor A (HIGHEST PRIORITY -- CPU, < 30 min, directly characterizes L_max surface)
Pointer: Section 6 "Anchor A" and "Cheap decisive test" of research note.
Substrate-product reading: Produces an empirical L_max(M, N, K) surface that validates or
  refutes the theoretical formula L_max ~ N/(2*K*M) * C. This is the single number that
  determines how many semantic layers the product can stack without recall degradation.
  Currently validated only at L<=8; this extends to L=20.
Tier hint: CPU; pure-numpy Hopfield attractor sweep; fast (<30 min for base config, <2 hr
  for full grid). No GPU required.
Why-now: The compositional cliff empirical result (L=8, recall=1.000) was just validated
  and the 2x drill has now derived a theoretical L_max formula. The cheap decisive test
  (M=500, N=8192, K=10, L up to 20) will confirm or bound the L_max estimate. Without this,
  the product claim "depth-independent" has no stated ceiling.
Task: See "Cheap decisive test" section of research note. Core: sweep L in {1,2,4,6,8,
  10,12,16,20} at (M=500, N=8192, K=10). Report recall@1 at each depth. Find L* = first
  depth where recall < 0.99. Also run one comparison cell: (M=5000, N=8192, K=10, L=8) to
  test the codebook-exhaustion break condition (HARD-FAIL P3).
HARD-PASS: L* >= 12 (depth-independence holds well past current tested range).
HARD-FAIL: L* < 6 (formula is wrong; depth-independence breaks within tested range).

### Anchor B (CPU, < 20 min -- codebook exhaustion break point)
Pointer: Section 2.1 and Anchor A comparison cell.
Substrate-product reading: Determines how many distinct atoms can be stored per shard
  before the cleanup memory degrades. Direct input to KB shard sizing formula.
Tier hint: CPU; sweep M at fixed N and L.
Why-now: The product architecture requires knowing M_max per shard. Currently unknown.
Task: Fix L=8, K=10, N=8192. Sweep M in {100, 200, 500, 1000, 2000, 5000}. Measure
  recall@1 at each M. Find M* = first M where recall < 0.99. Compare M* to 0.138*N = 1130
  (classical Hopfield capacity) and 0.0488*N = 399 (empirical substrate rule).
HARD-PASS: M* is between 0.04*N and 0.14*N (within calibrated capacity band).
HARD-FAIL: M* > 0.25*N (codebook capacity exceeds classical bound -- implies non-Hebbian
  cleanup is already in effect, need to re-examine implementation).

### Anchor C (CPU, < 20 min -- tier-mixed shard cost)
Pointer: Section 2.4 and Anchor D.
Substrate-product reading: Determines whether tier-separated cleanup memories (entity
  cleanup, predicate cleanup, context cleanup as separate Hopfield nets) outperform a
  single shared cleanup memory. Directly informs KB shard architecture decision.
Tier hint: CPU; two-condition comparison (shared vs. separated).
Why-now: If tier-mixing is free, the architecture can use one flat cleanup. If tier-mixing
  costs, separate per-tier cleanup nets are required. The answer changes the implementation
  plan.
Task: Build two setups at M=500 total atoms, N=8192, L=4, K=10:
  (1) MIXED: single cleanup memory with M/2=250 atoms from domain-A and M/2=250 from domain-B
      (domains have different statistical structure; use random base but add systematic
      within-domain correlation of ~0.2 mean inner product)
  (2) SEPARATED: two cleanup memories of M/2=250 atoms each; retrieval uses domain-matched
      cleanup
  Measure recall@1 in both conditions. Report delta.
HARD-PASS: SEPARATED recall > MIXED recall by > 5 percentage points (tier separation helps).
HARD-FAIL: MIXED recall >= SEPARATED recall (tier-mixing is free; flat architecture optimal).

### Anchor D (CPU, < 30 min -- cleanup pass multiplicity)
Pointer: Section 6 Anchor C.
Substrate-product reading: Determines whether running Hopfield cleanup 2x or 4x per level
  (multiple convergence passes) helps push L_max higher. Cheap to test; if positive, it is
  a zero-cost engineering win (just run the attractor update more times).
Tier hint: CPU; sweep cleanup_passes at fixed architecture.
Why-now: If 2 cleanup passes per level halve p_err, L_max roughly doubles (from L_product
  formula). This is the cheapest possible lever for extending depth-independence.
Task: Fix L=8, K=10, M=1000, N=8192 (in the intermediate regime where p_err is non-trivial).
  Sweep cleanup_passes in {1, 2, 4, 8}. Measure recall@1 at each. Report improvement.
HARD-PASS: recall monotonically increases with cleanup_passes; 2 passes gives > 30% of
  maximum possible improvement over 1 pass.
HARD-FAIL: recall does not change at 2 passes vs 1 pass (single-pass Hopfield is already
  at fixed point; more passes are wasted compute).

### Anchor E (CPU/GPU, < 1 hr -- modern Hopfield cleanup comparison)
Pointer: Cross-thread synthesis, Section 3.2.
Substrate-product reading: Tests whether replacing classical Hebbian cleanup with modern
  polynomial-order Hopfield (p=3) at each level increases L_max. This is the most
  impactful potential engineering change: theory predicts moving from L_max ~ 10-100 to
  L_max ~ 1000+.
Tier hint: CPU for small N (N=1024); GPU if N=8192 needed. Likely CPU is sufficient for
  the discriminating comparison.
Why-now: Classical vs modern Hopfield cleanup is a concrete switchable design choice. The
  research note predicts that modern Hopfield buys dramatically larger L_max. If confirmed,
  this is a mandatory architectural upgrade.
Task: Build two cleanup implementations: (a) classical Hebbian (linear); (b) modern Hopfield
  with p=3 polynomial interaction. Fix M=1000, N=8192, K=10. Sweep L in {4,8,12,16,20,30}.
  Measure recall@1 for both. Compare L_max (first L where recall < 0.99).
HARD-PASS: modern-Hopfield L_max > 1.5x classical-Hopfield L_max (theory predicts larger
  margin at same M/N load).
HARD-FAIL: modern-Hopfield L_max <= classical-Hopfield L_max (polynomial interaction does
  not help for compositional depth; model needs re-examination).

---

## Context pointers

- Research note (primary): notes/research_drill_depth_independent_theoretical_lmax_2x_2026-06-10.md
- Prior compositional depth biology note: notes/research_drill_biological_overcome_compositional_depth_3x_2026-06-10.md
- Empirical result context: see orchestrator MEMORY.md entry "Substrate v3.0 compositional cliff crossed 2026-06-10"
- Spectral background (non-Gaussian codebook overlap): notes/strategy_decisions_2026-05-23.md (v164a, v165 wave14 results)
- Shard architecture context: notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md

---

## Contract

The research note has pre-registered HARD-PASS and HARD-FAIL thresholds for each anchor.
Exp_dev is contracted to:
  1. Execute anchors in rank order (A first, then B, then C/D/E in parallel if queues allow)
  2. Pre-register per-cell bands before dispatch (no post-hoc relabelling per
     [[feedback-no-preframe-batch-all-pass]])
  3. Report verdicts to verdict_handler for cap_map decisions
  4. If Anchor A shows L* < 8: STOP and escalate to Research before proceeding to B-E
     (early break means the theoretical model is wrong and anchors B-E are premised on it)

## Autonomy declaration

Exp_dev has full autonomy over:
  - Exact sweep parameter grids within the ranges stated (do not over-sweep; CPU time is finite)
  - Queue assignment (all 5 are CPU-eligible; use remote_cpu_queue or local_cpu_queue as available)
  - Implementation of the Hopfield cleanup (classical Hebbian or pytorch-free numpy -- numpy preferred)
  - Smoke vs full run decision at each anchor (smoke first, FULL only if smoke passes)
  - Whether to run anchors C and D in parallel (they are independent)

Do NOT design new experiments beyond the 5 anchors above. If a result is surprising enough
to warrant a new experiment, escalate to Research via a routing note.
