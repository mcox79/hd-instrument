# exp_dev hand-off -- research: type-routing capacity multiplier (PP-302 lit scan)

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: PP-302 negres_bundle_split_c4 showed C=4 type-routing gives 4x capacity; research mandate was to determine novelty vs prior art
Research note: d:/AI/hd-instrument/notes/research_drill_type_partitioning_lit_scan_2x_2026-06-10.md

Per [[feedback-no-experiment-design-in-prompts]]: experiment design is exp_dev's domain. This file provides research findings and anchor candidates; it does not prescribe experiment parameters.

---

## Pause state block

Research delivered. No orchestrator pause required for this handoff. Experiments in this area can proceed as pipeline capacity allows.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIORITY)

Pointer: PP-302 type-routing controlled-parameters test
Substrate-product reading: Determine whether the 4x capacity multiplier in PP-302 holds when total parameter budget is held fixed (N/C per type vs N shared). If yes, the multiplier is from interference-reduction, not from increased storage, and is a genuine first-class design principle. If no, the multiplier is trivially explained by 4x total parameters.
Tier hint: Tier-2 (falsifies or confirms core capacity claim)
Why-now: The research scan found NO prior work making this specific claim. Confirmation would establish substrate novelty. Cheap CPU test, 1-2 hours.

### Anchor 2

Pointer: MoE capacity theory drill (adjacent to type-routing multiplier)
Substrate-product reading: The Mixture-of-Experts literature (Shazeer 2017, Switch Transformer 2022) uses sparse routing to independent subspaces. The capacity factor analysis in MoE is the closest formal prior to the type-routing multiplier theorem. A drill on MoE capacity theory may provide the theoretical backing or partial prior art for the multiplier claim.
Tier hint: Research drill (not experiment)
Why-now: Identified as the next-drill candidate in the research note. Low-cost lit scan.

### Anchor 3

Pointer: PBG per-type embedding independence verification
Substrate-product reading: PBG (PyTorch-BigGraph) is the closest production-system prior art. Verifying whether PBG's per-type independent tables yield measurable capacity gains (vs per-type tables of same total size but shared) would confirm whether the production KGE community has already measured the multiplier without naming it.
Tier hint: Confirmatory research / lit verification
Why-now: The PBG paper (MLSys 2019) is available and may contain the relevant experiment. A targeted read could close or open this.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_type_partitioning_lit_scan_2x_2026-06-10.md
- Closest prior art: arXiv 2501.04613 (semantic partitioning, scoring function unchanged)
- Closest production analog: PyTorch-BigGraph arXiv 1903.12287 (per-type embedding tables)
- VSA capacity: arXiv 2301.10352 (capacity analysis, no type-partition multiplier)

---

## Contract section

Research has delivered the lit scan. The question of whether PP-302's 4x multiplier is from interference reduction (novel) or total parameter increase (trivial) is open and falsifiable. exp_dev should prioritize the controlled-parameters test (Anchor 1) when pipeline capacity allows.

## Autonomy declaration

exp_dev owns experiment design for Anchor 1. Research has pre-registered the HARD-PASS and HARD-FAIL thresholds (see research note). exp_dev should not need to consult research before running Anchor 1 -- the test is straightforward and the bands are specified.
