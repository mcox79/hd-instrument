# exp_dev hand-off -- research: mean_pool_tax_investigation

Filed-by: research sub-agent
Trigger: notes/research_drill_mean_pool_tax_investigation_2026-06-07.md
Pause state: RESPECT data/orchestrator_paused.flag -- do not queue if paused.

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY only. Exp_dev designs the anchors, sweep grids, threshold formulas, and pre-reg bands. Do NOT treat any number in this file as a pre-committed design parameter.

---

## ANCHOR CANDIDATES (rank-ordered by EV)

### Anchor A: Alpha fine-sweep below current optimum
- Anchor pointer: TAX-10 in research note above
- Substrate-product reading: Cycle 130 established alpha=0.04 gives ~20x capacity vs alpha=0.20 gives ~5-7x. The sweep did not go below 0.04. If the curve continues to rise, further 2-4x gain is available with zero architecture change.
- Tier hint: CPU rung-1/2, short wall, cheap
- Why now: EV=1.86 (highest); empirical precedent from cycle 130; one cell sweep; no architecture change required

### Anchor B: Metric ceiling uncensor (M_max 50 -> 200)
- Anchor pointer: TAX-6 in research note above
- Substrate-product reading: If any prior condition was measured at M_50 and true capacity > 50, those verdicts are measurement artifacts not capacity ceilings. Uncensoring in one reference condition establishes whether prior saturation verdicts need to be revisited.
- Tier hint: CPU rung-1, shortest wall, 0.5 cells
- Why now: EV=1.82; measurement fix; retroactively validates or invalidates prior saturation verdicts (cycle 133 M=4 "saturation" is at risk)

### Anchor C: Padding side audit + capacity sweep
- Anchor pointer: TAX-2 in research note above
- Substrate-product reading: Right-padding in HuggingFace defaults causes last-token pooling to extract PAD token embeddings. If the pipeline uses right-padding (the HuggingFace default for batch processing), cycle 138's "last-token raw = 0" may be explained entirely by extracting PAD embeddings. One-line fix (tokenizer.padding_side = 'left') with potentially 1.5-3x capacity impact.
- Tier hint: CPU rung-1, 1 cell, 15 min wall
- Why now: EV=1.13; one-line fix; may retroactively explain the raw=0 anomaly from cycle 138

### Anchor D: Write rule comparison (Hebb vs pseudoinverse/perceptron)
- Anchor pointer: TAX-1 in research note above
- Substrate-product reading: Amit-Gutfreund-Sompolinsky (1985) established that the pseudoinverse/perceptron rule achieves alpha_c ~ 1.0 vs Hebb alpha_c ~ 0.14, a ~7x difference for binary patterns and ~3-4x for analog. If the substrate uses Hebb, this is the largest single unrealized capacity gain available.
- Tier hint: CPU rung-2, 2 cells, 30 min wall
- Why now: EV=1.57; algebraically confirmed in 1985 literature; potentially largest capacity gain of any pipeline change

### Anchor E: ZCA epsilon sweep (soft-whitening regularization)
- Anchor pointer: TAX-3 in research note above
- Substrate-product reading: Standard ZCA inverts ALL eigenvalues including near-zero ones, producing noise amplification for borderline-rank data. Soft-ZCA (epsilon regularization) documents this fix. Cycle 130 ZCA regression is circumstantial evidence the substrate may be in the instability regime.
- Tier hint: CPU rung-1, 1 cell, 15 min wall
- Why now: EV=0.83; cycle 130 regression is unexplained; cheap to test

---

## CONTEXT POINTERS (file paths)
- Research note: d:/AI/hd-instrument/notes/research_drill_mean_pool_tax_investigation_2026-06-07.md
- Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
- Prior v195 handoff template: d:/AI/hd-instrument/notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md

---

## CONTRACT
- Exp_dev owns anchor design, sweep grids, HP/MID/HF bands, queue assignment, ETA, and pre-reg
- Research sub-agent provided EV ranking and hypothesis framing only
- Orchestrator routes this file to exp_dev on next refill cycle (auto-discovered via notes/exp_dev_handoff_*.md sort by mtime)

## AUTONOMY DECLARATION
Exp_dev has full autonomy to:
- Reorder anchors by pipeline state or queue depth
- Combine anchors into a single multi-cell batch if that is more efficient
- Reject anchors that conflict with current queue or paused state
- Add additional anchors not listed here if cap_map priorities justify them
- Set all numerical parameters (sweep ranges, thresholds, cell counts)
