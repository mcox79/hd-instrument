# exp_dev hand-off -- research: pattern_b_manifold_storage_2x

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_pattern_b_manifold_storage_2x_2026-06-07.md

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns the anchor design.
This file provides context pointers and candidates only.

---

## Pause state block

This hand-off does NOT override the current pause state.
Exp_dev checks data/orchestrator_paused.flag before acting on this file.

---

## Anchor candidates (rank-ordered)

### Rank 1: Pattern B bundle manifold pre-test
Anchor pointer: bundle_manifold_pretest (new anchor; does not exist yet)
Substrate-product reading: Measures the intrinsic dimensionality of Pattern B bound bundles
  using bge-small fillers and MAP-I role binding. Determines the safe PCA truncation dim
  for Pattern B storage. This is the mandatory pre-test before any Pattern B engineering
  can be authorized. Without it, the bundle compression target (d=? bytes per fact) is
  unknown.
Tier hint: CPU-only; < 2 hours wall time; $0 cloud cost; fits remote_cpu_queue
Why now: The 3x drill (research_drill_pattern_b_compositional_storage_3x_2026-06-07.md)
  authorized Pattern B exploration pending SRL quality validation. This 2x drill adds a
  SECOND mandatory pre-test (manifold dim) that must also complete before v1.1 Pattern B
  engineering begins. The two pre-tests can run in parallel if SRL pre-test is also queued.

Pre-reg bands (for exp_dev to formalize):
  HARD PASS: TwoNN < 100 AND unbinding cosine at d=30 > 0.80
  MID: TwoNN in [100, 300] AND unbinding cosine at d=200 > 0.85
  HARD FAIL: TwoNN > 450 OR unbinding cosine at d=300 < 0.70

Cheap decisive test pattern (from research note, Section 2):
  - 1000 representative bundles; bge-small fillers; MAP-I binding; K=3-5 roles per bundle
  - TwoNN + Participation Ratio on the bundle distribution
  - PCA sweep d = [20, 30, 50, 100, 150, 200, 300, 384]
  - Unbinding cosine similarity sweep at each d
  - Total wall time: < 2 hours CPU

### Rank 2: Modern Hopfield capacity for structured patterns (next-drill candidate)
Anchor pointer: hopfield_structured_capacity_drill (research drill, not exp_dev anchor)
Substrate-product reading: The research note identifies that Pattern B bundles share role
  substructure, which may erode the modern Hopfield exponential energy advantage. This is
  a theory drill (no experiment needed yet) but becomes an exp_dev anchor once the manifold
  pre-test result is in hand.
Tier hint: theory + CPU smoke; fits after Rank 1 completes
Why now: field-advisor flags modern-hopfield as Tier-1 fruit-bearing and under-drilled;
  the structured-patterns angle has not been addressed in prior drills.

---

## Context pointers

Primary research note:
  d:/AI/hd-instrument/notes/research_drill_pattern_b_manifold_storage_2x_2026-06-07.md

Prior Pattern B drills:
  d:/AI/hd-instrument/notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md

Pattern A validated results:
  Cap_map rows for KEY compression; TwoNN=33.6, PR=31.9; F1=1.0 at d=30 (from status log)

Retrieval encoder selection:
  d:/AI/hd-instrument/notes/research_drill_retrieval_encoder_selection_3x_2026-06-07.md
  (bge-small confirmed as preferred filler encoder for Pattern B)

SRL pre-test authorization:
  d:/AI/hd-instrument/notes/research_to_exp_dev_pattern_b_srl_pretest_authorize_2026-06-07.md

---

## Contract section

Research sub-agent delivers: theoretical framework, storage cost projections, pre-test
protocol specification, engineering compatibility matrix, hard-pass/hard-fail thresholds.

Exp_dev owns: anchor design, pre-reg formalization, queue placement, result interpretation.

Research does NOT pre-reg specific band numbers in the queue system -- that is exp_dev's
role. The thresholds in this file are guidance derived from the theoretical analysis.

---

## Autonomy declaration

Exp_dev may act on Rank 1 without further orchestrator confirmation if:
  (a) pause flag is not set
  (b) the SRL pre-test from the prior hand-off has been queued (they can run in parallel)
  (c) the anchor cost estimate (< 2h CPU, $0) fits within standing CPU queue budget

Exp_dev should NOT block Rank 1 on the theory drill (Rank 2) -- the theory drill is a
SUBSEQUENT research dispatch, not a precondition for the CPU pre-test.
