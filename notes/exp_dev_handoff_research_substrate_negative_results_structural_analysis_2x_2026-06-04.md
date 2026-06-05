# exp_dev hand-off -- research: substrate negative results structural analysis (2x)

Filed-by: research sub-agent, 2026-06-04
Trigger: notes/research_drill_substrate_negative_results_structural_analysis_2x_2026-06-04.md
Pause state: CHECK data/orchestrator_paused.flag before dispatching any anchor below.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
context pointers only. exp_dev designs sweep grids, threshold formulas, queue assignments,
and HF/HP numerical bounds without further input from research.

---

## Background

2x drill on today's 8 HF results revealed three structural substrate limits:
(1) SPARSITY PREREQUISITE: dense modes fail across resonator, modulator, and representation axes.
(2) UNIDIRECTIONAL BINDING PRIMITIVE: substrate algebra is factor-binding, not edge-relation.
(3) ORDER-INVARIANCE IN ADDITIVE WRITE: linear W is commutative; temporal sequence invisible.

Four escape paths have algebraic justification and are ready for cheap empirical test.
Priority order below is by (leverage / cost) ratio.

---

## Anchor Candidates (rank-ordered by decisiveness and cheapness)

### 1. 4-modulator hippocampal-tier smoke
- Anchor pointer: compositional-minimum rescue for K=1 modulator accepted-negative (< 0.1 nats
  gap). Research drill confirms: 4 modulators provide 2^4=16 combinatorial modulatory states
  vs K=1 single-bit modulation. 4-modulator system is the bio-tier-scaling prediction that
  has NOT been empirically tested yet.
- Substrate-product reading: HARD-PASS unlocks 24x-96x capacity expansion for neuromodulatory
  tier; potential TIER-1 capability if retention ratio > 1.50x. HARD-FAIL confirms K=1 is
  a deeper architectural issue requiring different rescue.
- Tier hint: CPU smoke (~1h, N=2048, K=4 modulators, few seeds). Fast iteration.
- Why-now: Highest P_deflated (0.45) of all escapes; cheapest decisive test for an accepted-
  negative that has been sitting open since Drosophila-MB single-modulator HF. Research drill
  provides algebraic justification; only empirical test remains.

### 2. Sparse resonator K=26 replication (arXiv:2404.19126)
- Anchor pointer: dense-resonator-V=100 accepted-negative (acc=0.000 all K=5..11 N=4096).
  Published result: K=26 at N=5000 with V=1 (sparse regime: each concept = one atom).
  Engineering fix: change representation format from dense-V to sparse-V=1.
- Substrate-product reading: HARD-PASS directly rescues resonator compositional retrieval at
  high K for product use cases. Frady-Sommer 2020 capacity formula predicts this succeeds.
  P_deflated = 0.45 (highest confidence escape because published empirical proof exists).
- Tier hint: CPU smoke (~2h, N=5000, K in {10,20,26}, V=1). Straightforward replication.
- Why-now: arXiv:2404.19126 published result provides the implementation target; substrate
  needs to replicate at production N. Removes the V-constraint as the active blocker.

### 3. cf-RPE weighted replay smoke (B5 Escape B)
- Anchor pointer: B5 additive-W replay-consolidation accepted-negative. Research confirms:
  additive-W commutativity makes replay-ORDER algebraically irrelevant. Escape B breaks
  commutativity by using sequential cf-RPE updates as per-item weights in the Hebbian write.
  Wright-Fisher analysis: cf-RPE provides a selection coefficient that depends on replay ORDER
  (earlier items set the running baseline; later items' weights are relative to shifted baseline).
- Substrate-product reading: HARD-PASS (ratio > 1.15) would validate cf-RPE as a nonlinear
  write mechanism that preserves consolidation benefit in operating modes using replay.
  HARD-FAIL (ratio < 1.02) confirms B5 is FULLY FUNDAMENTAL with no in-substrate rescue at
  the Hebbian-write level.
- Tier hint: CPU smoke (~30min, N=2048, K=10 replay items, sequential vs. random order).
- Why-now: Cheapest test of the nonlinear-write escape class. Result directly determines
  whether cf-RPE consolidation should enter the priority queue.

### 4. Bloom-substrate membership smoke (SQ6 Escape)
- Anchor pointer: SQ6 architectural gap (bundle SNR wall for membership queries). Research
  confirms: current SQ6 bundling cannot detect edge-membership because 1/sqrt(E) SNR at
  E=O(N). Bloom-substrate variant: hash each edge (a_u XOR a_v) into a SEPARATE sparse
  indicator vector h_{uv} in {0,1}^N using K=2-4 hash functions; membership = check h_{uv}
  in accumulated indicator. This is algebraically distinct from SQ6 bundling.
- Substrate-product reading: HARD-PASS opens a probabilistic-membership capability that
  complements substrate's existing GRAPH RECOVERY strength (resonator). Knowledge-graph
  product use case needs both. Bloom-substrate is the substrate-native implementation.
- Tier hint: CPU smoke (~1h, N=4096, E in {N/8, N/4, N/2}, K_hash=2..4).
- Why-now: SQ6 v1+v2 both HF confirms the bundle approach is closed. Bloom-substrate is the
  only substrate-native alternative that doesn't require external data structures.

---

## Context Pointers

- Research note (primary):
  notes/research_drill_substrate_negative_results_structural_analysis_2x_2026-06-04.md
- Cap_map HF annotations:
  notes/substrate_capability_map.md (CYCLE 71 batch, SQ6 v1+v2 HF, resonator dense HF,
  B5 bounded-W HF, SQ1 generative HF entries at v401)
- Bio-tier-scaling drill (4-modulator prediction):
  notes/research_to_exp_dev_bio_smoke_followup_consolidated_2026-06-04.md
- Frady-Sommer 2020 + arXiv:2404.19126 (sparse resonator theory):
  referenced in research note above; external sources
- Wright-Fisher drill (B5 algebraic analysis):
  status_log entry 2026-06-04 (Wright-Fisher + Kimura fixation theory delivery)

---

## Contract

Research has delivered: algebraic categorization of 8 HF results, 4-taxonomy mapping,
P_deflated estimates for each escape path, pre-reg HARD-PASS and HARD-FAIL thresholds.

exp_dev's job: design sweep grids, assign queues, specify exact anchor names (per
PROT-018 naming contract), verify timeout formulas, and ship the 4 candidates above
in cost-prioritized order without padding. Research does NOT specify these parameters.

## Autonomy Declaration

exp_dev has full autonomy to:
- Choose N values and seed counts within the CPU/GPU routing rules
- Design the specific implementation of each anchor (e.g., exact hash functions for
  Bloom-substrate; exact modulatory mechanism for 4-modulator system)
- Sequence and batch anchors as appropriate for queue health
- Add additional rescues or variants if mechanistic understanding during implementation
  suggests a better approach

exp_dev does NOT have autonomy to:
- Modify cap_map directly (orchestrator/verdict_handler owns that)
- Interpret verdicts beyond completion status (orchestrator owns strategy decisions)
- Add anchors without cap_map or handoff justification (no padding per memory rule)
