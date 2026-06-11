# exp_dev hand-off -- research: boredom refinement 2x

## Filed-by
Research sub-agent, 2026-06-10

## Trigger
Research note: d:/AI/hd-instrument/notes/research_drill_boredom_refinement_2x_2026-06-10.md
PP-325 BOREDOM-REAL AUC=0.908, gap -0.092 from synthetic. Four mechanisms identified as production-actionable refinements.

## Pause state
Check data/orchestrator_paused.flag before queuing. Do not queue if paused.

Per [[feedback-no-experiment-design-in-prompts]]: this file contains anchor candidates and context pointers only. Exp_dev designs the experiment cells; this file does not specify implementation details.

---

## Anchor Candidates (rank-ordered)

### Rank 1: Temporal phase segmentation
Anchor pointer: PP-325-TEMPORAL-PHASE
Substrate-product reading: split real-web sessions into 0-30 min / 30-90 min / 90+ min phases; train phase-specific boredom classifiers; compare AUC against single-classifier baseline
Tier hint: Tier-2 (moderate complexity, single data split + 3 training runs)
Why now: cheapest test; directly addresses the temporal autocorrelation gap (main structural cause of synthetic-real difference); no new data required, only session-aware data loading

### Rank 2: Stretched-exponential novelty prior
Anchor pointer: PP-325-KWW-NOVELTY-PRIOR
Substrate-product reading: add Wu-Huberman KWW temporal decay prior (r_t ~ exp(-0.4*t^0.4)) as feature or training augmentation; compare AUC on real-web held-out
Tier hint: Tier-2 (requires temporal session metadata and modified data pipeline)
Why now: has strongest theoretical grounding of all four mechanisms; WW parameters from PNAS 2007 provide concrete starting point even if re-calibration needed

### Rank 3: d' vs criterion decomposition
Anchor pointer: PP-325-SDT-DECOMPOSE
Substrate-product reading: apply signal detection theory decomposition to boredom labels; build two-stream architecture with separate perceptual-sensitivity (d') and decision-criterion (beta/c) heads; verify factor loadings
Tier hint: Tier-3 (requires relabeling or proxy derivation of d' and criterion from behavioral data)
Why now: independent theoretical support from SDT vigilance literature AND dual-CLS lift findings; connects two existing research threads

### Rank 4: ADHD subpopulation mixture model
Anchor pointer: PP-325-ADHD-MIXTURE
Substrate-product reading: separate real-web test set by ADHD/non-ADHD indicator; test mixture model vs single classifier; measure AUC gap
Tier hint: Tier-3 (requires population metadata; may not be available in current dataset)
Why now: ADHD bimodal attention distribution is a known confounder; if metadata exists, this is a cheap probe of population heterogeneity impact

---

## Context Pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_boredom_refinement_2x_2026-06-10.md
- v195 handoff template: d:/AI/hd-instrument/notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md
- Status log: d:/AI/hd-instrument/data/orchestrator_status_log.jsonl
- Cap map: check notes/substrate_capability_map.md for PP-325 current row status

---

## Contract

Exp_dev owns: experiment cell design, anchor registration, queue dispatch, pre-reg bands, smoke gate, post-ship verify.
Research owns: mechanism identification, P estimates, HARD-PASS/HARD-FAIL thresholds (specified in research note).
Orchestrator owns: prioritization, pause/resume gating.

## Autonomy Declaration
Exp_dev may proceed with Rank 1 (PP-325-TEMPORAL-PHASE) and Rank 2 (PP-325-KWW-NOVELTY-PRIOR) without further orchestrator check-in if queue has open slots. Rank 3 and 4 require orchestrator sign-off given metadata dependency uncertainty.
