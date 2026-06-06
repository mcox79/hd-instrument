# exp_dev hand-off -- research: sparse activation extraction entropy-gated

Filed-by: research sub-agent (2026-06-05)
Trigger: research drill notes/research_drill_sparse_activation_extraction_entropy_gated_2x_2026-06-05.md
Pause state: CHECK data/orchestrator_paused.flag before dispatching any anchor.

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
explains WHY they are ready for empirical test. It does NOT specify sweep grids, threshold
formulas, numerical bounds, queue choices, or pre-committed cap_map decisions. exp_dev
designs the experiment autonomously after reading context pointers.

---

## ANCHOR CANDIDATES (rank-ordered)

### Rank 1: Embedding-norm discriminability for extraction gating
Anchor pointer: validates Option B (embedding-norm pre-filter) as the zero-cost gating
  mechanism for sparse extraction.
Substrate-product reading: if AUROC of embedding-norm vs. POS-ground-truth classification
  exceeds the HARD PASS threshold (> 0.80), Option B can be deployed immediately with no
  additional LLM overhead. This is the cheapest path to 3x extraction speedup.
Tier hint: Tier 1 (cheap CPU smoke; no GPU required; corpus subsample ~2M tokens).
Why-now: the algebraic prediction (norm ~ IDF, large separability between content and filler
  norms) has strong lit backing (arXiv:2212.09663) but has not been validated on the specific
  BPE tokenizer + VQ assignment pipeline used in this substrate. The discriminability test is
  the decisive gate before investing in full sparse extraction pipeline.

### Rank 2: VQ codebook coverage preservation under sparse extraction
Anchor pointer: validates the P1 prediction (K(g=0.30)/K(g=1.0) > 0.97 on 10^7 token corpus).
Substrate-product reading: directly quantifies the extraction quality loss from 70% token
  skipping. If HARD PASS, the coverage argument is empirically closed and the pipeline can
  be deployed. If HARD FAIL, signals that content-token misclassification rate is higher than
  predicted and gating threshold must be tightened.
Tier hint: Tier 2 (medium CPU run; requires running extraction pipeline on Wikipedia subset).
Why-now: coverage safety is the primary uncertainty. The algebraic model (Section 4 of
  research note) predicts coverage preservation but rests on Zipf distribution assumptions
  that may not hold for the specific tokenizer + codebook combination.

### Rank 3: Speedup measurement of Stage 1+2+3 gating pipeline
Anchor pointer: validates P4 (2.5x+ speedup on tokens-processed-per-second) for the
  recommended stop-list + embedding-norm + first-layer-entropy gating stack.
Substrate-product reading: if HARD PASS, the combined gating pipeline is production-ready.
  This anchor should run AFTER Rank 1 and 2 confirm the quality preservation story.
Tier hint: Tier 2-3 (GPU helpful for first-layer entropy computation at scale).
Why-now: speedup is not guaranteed if gating overhead (embedding lookups, norm computation,
  layer-1 forward pass bookkeeping) eats into the savings. Need wall-time measurement, not
  just FLOP count.

---

## CONTEXT POINTERS (file paths, not summaries)

Research note:
  d:/AI/hd-instrument/notes/research_drill_sparse_activation_extraction_entropy_gated_2x_2026-06-05.md

Prior sparse coding / D-RIP research:
  d:/AI/hd-instrument/notes/research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x_2026-06-04.md

Related testbed authorization:
  d:/AI/hd-instrument/notes/research_to_testbed_pythia_per_token_extraction_request_2026-06-05.md

Cap map (for context on where extraction anchors fit in capability roadmap):
  d:/AI/hd-instrument/data/cap_map.md  (check current state; do not modify)

---

## CONTRACT

exp_dev may:
  - Design anchor sweep grids, seed counts, and pre-registration bands autonomously.
  - Choose which queue (overnight_queue / remote_cpu_queue / laptop) based on cost/scale.
  - Combine Rank 1 and Rank 2 anchors into a single batch if substrate overhead allows.
  - Propose additional anchors that emerge from design-space reasoning.

exp_dev must NOT:
  - Pre-commit cap_map decisions (verdict_handler owns those).
  - Ship anchors that require GPU if remote_cpu_queue can handle them.
  - Exceed envelope without explicit orchestrator authorization.

## AUTONOMY DECLARATION

This hand-off file is structural. exp_dev does not require orchestrator confirmation to
pick it up on a normal queue-refill cycle. The pause flag check is the only gate.
