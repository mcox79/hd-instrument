# exp_dev hand-off -- research: C-axis functional similarity beyond bge (contrastive supervised)

Filed-by: research (2x DEEP drill)
Date: 2026-06-12
Trigger: research delivery at
  d:/AI/hd-instrument/notes/research_drill_C_axis_functional_similarity_beyond_bge_contrastive_supervised_metric_learning_2x_2026-06-12.md

Pause state: respect data/orchestrator_paused.flag. If paused, treat this as
queued-only -- annotate cap_map / strategy intent but do not ship cells.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors
and substrate-product readings only. exp_dev designs the cell.

## Anchor candidates (rank-ordered)

### 1. C-axis functional-similarity contrastive embedder (PRIMARY)

- Anchor pointer: bge-frozen + 2-layer projection head (256 hidden, 128 out)
  trained with Multiple-Negatives-Ranking + batch-hard triplet (margin ~0.2)
  on (capability, serves_capability) pairs from substrate's structured
  supervision graph.
- Substrate-product reading: substrate LEARNS functional similarity from
  its own structured trace; LLMs cannot because they have no analogous
  serves_capability supervision graph. C-axis becomes a learnable surface,
  not a corpus-bound ceiling.
- Tier hint: Tier-3 mechanism (substrate-distinctive lever class; third
  C-axis mechanism after bge cosine REFUTED and structural 1-hop REFUTED).
- Why-now: 2x DEEP drill identifies supervised contrastive as the
  empirically-supported lever class consistent with lit consensus and
  with substrate's available structured supervision. Two prior mechanism
  classes REFUTED -- mechanism-diversity rule dictates this third class
  is the next discipline.
- Pre-reg HARD-PASS reference (from research note): C-axis lift >= +0.05
  absolute with no axis regression > -0.01.
- Pre-reg HARD-FAIL reference: any axis regression >= 0.02 OR
  C-axis lift < 0.00 OR train loss not converging in budget.

### 2. Hard-negative-mining-only ablation (CHEAP DIAGNOSTIC)

- Anchor pointer: same projection head as #1 but trained without the
  hard-negative mining loop -- random in-batch negatives only.
- Substrate-product reading: isolates whether hard-negative mining is the
  load-bearing ingredient (lit consensus says yes; substrate-empirical
  confirmation has high diagnostic value).
- Tier hint: ablation / diagnostic; ships only if #1 produces signal.
- Why-now: if #1 HARD-PASSes, this ablation confirms which ingredient
  carried the lift -- protects against the "everything-everywhere"
  failure mode where the wrong knob gets credited.

### 3. Cross-encoder rerank distillation second pass (DEFERRED)

- Anchor pointer: train a small cross-encoder on the same triplets;
  distill into the bi-encoder via Margin-MSE (Augmented-SBERT pattern).
- Substrate-product reading: matches two-stage-decomposition methodology
  rule; if substrate corpus is large enough to fit cross-encoder, lit
  predicts +0.02 to +0.04 additional lift.
- Tier hint: deferred until #1 MIDDLE-or-better; not a first-shot cell.
- Why-now: queue ordering -- ship #1 first, evaluate, then decide on #3.

## Context pointers

- Research note (this drill):
  d:/AI/hd-instrument/notes/research_drill_C_axis_functional_similarity_beyond_bge_contrastive_supervised_metric_learning_2x_2026-06-12.md
- Substrate self-knowing baseline (most recent C-axis state):
  see MEMORY.md entry substrate_self_knowing_HP_v2_macro_F1_0_569_Cycle_47_2026-06-12.md
- Methodology rules referenced:
  - capability-portfolio-mechanism-diversity-is-the-lever
  - two-stage-decomposition-beats-joint
  - brain-can-do-it (cortical functional clustering analog)
  - literature-is-not-oracle (deflate predictions; verify empirically)
- Remote-compute constraint:
  feedback_all_cpu_compute_on_remote_desktop_2026-06-11 -- all training
  on remote desktop (100.91.12.42 / C:\dev\hd-instrument), never local.

## Contract

- exp_dev designs the cell.
- This file names anchors, substrate-product readings, tier hints, and
  why-now per [[feedback-no-experiment-design-in-prompts]].
- Pre-reg envelope-fail-bands per existing exp_dev discipline; use the
  HARD-PASS / HARD-FAIL thresholds from the research note as starting
  pre-reg, not as commands -- exp_dev may tighten or split if cell
  design warrants.
- Smoke gate before queue_add per existing exp_dev discipline.
- Remote-only training per all-cpu-compute-on-remote-desktop memory.

## Autonomy declaration

- exp_dev decides cell budget, batch size, mining schedule, evaluation
  questionset, and pre-reg band tightening.
- exp_dev decides ordering between anchor #1 and #2 (likely #1 first,
  #2 as follow-up if #1 ships signal).
- exp_dev decides whether to defer anchor #3 to a later cycle.
- research's role ends at this hand-off; further drill requested only on
  exp_dev verdict-triggered rehab or strategy routing.

End.
