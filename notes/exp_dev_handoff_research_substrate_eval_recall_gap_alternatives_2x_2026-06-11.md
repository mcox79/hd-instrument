# exp_dev hand-off -- research: substrate-eval recall_gap architectural alternatives

filed_by: research (Opus, 2x DEEP drill)
date: 2026-06-11
trigger: Findings 17 HARD_FAIL -- composite_C did not drop post-ingest of 449 drills; root cause is algebra_novelty saturation under MAX gate; this drill proposes 5 architectural alternatives beyond Option B
research note: d:/AI/hd-instrument/notes/research_drill_substrate_eval_recall_gap_alternatives_2x_2026-06-11.md

pause state: respect data/orchestrator_paused.flag. If pause flag set, queue these as DRAFT cells; do not ship until resume.

Per [[feedback-no-experiment-design-in-prompts]] -- this hand-off names anchor candidates and tier hints; exp_dev owns the actual cell design + smoke + queue_add.

## Anchor candidates (rank-ordered)

### 1. substrate_eval_recall_gap_dual_process_B_plus_H_2026-06-11  (RANK 1 -- SHIP)
- pointer: research note section "Option B + H combined", lines covering dual-process recognition
- substrate-product reading: explicit recollection (file_id) + familiarity (top-k retrieval cosine) is a substrate-product differentiator vs LLM continuous-logprob memory; supports auditable-AI-memory-subsystem strategic direction
- tier hint: TIER-A target (AUROC >= 0.85 on Set A ingested vs Set B held-out; AUROC >= 0.75 on Set A_perturbed paraphrased ingested)
- why-now: dual-process is the brain-validated architecture, ~80 LOC, lit-anchored to Yonelinas 2002 + DPR/ColBERT. P_deflated 0.50 (caps at novel-synthesis cap).
- decisive test: substrate-CPU AUROC pass on probe sets A / B / A_perturbed in single eval pass

### 2. substrate_eval_recall_gap_bundle_space_G_2026-06-11  (RANK 2 -- STRUCTURAL CLEANUP)
- pointer: research note section "Option G (redefine algebra_novelty in BUNDLE space)"
- substrate-product reading: attacks Findings 17 root cause directly (saturation is metric-definitional); aligns with substrate-self-index foundational tool memory; produces a per-document bundle index as new substrate-self-evaluation primitive
- tier hint: TIER-A target (AUROC >= 0.85) AND backward-compat sanity (r > 0.3 with old algebra_novelty on cross-cutting content)
- why-now: highest structural leverage; sequence AFTER B+H lands so we have ground truth (B+H AUROC) to validate G against
- decisive test: same AUROC pass + backward-compat correlation check

### 3. substrate_eval_recall_gap_weighted_avg_E_2026-06-11  (DAY-1 PARALLEL PARTIAL FIX)
- pointer: research note section "Option E (weighted-average instead of max)"
- substrate-product reading: 5-LOC change; unmasks the semantic_novelty signal that MAX gate hides; partial fix only, not architectural
- tier hint: TIER-B or MIDDLE-BAND expected (AUROC 0.70-0.78); HARD_PASS = post-ingest NOVEL drops from 68.2% to below 50%
- why-now: cheapest insurance while B+H is built; can ship in same eval pass
- decisive test: NOVEL fraction delta on already-ingested 449 drills

### 4. substrate_eval_recall_gap_hierarchical_J_2026-06-11  (ABLATION / 4-CHANNEL)
- pointer: research note section "Option J (hierarchical 4-level novelty)"
- substrate-product reading: aligns with substrate-two-axes memory empirical finding (semantic and content-reference orthogonal); operationalizes v3 indexes architecture (3 indexes + RRF + intent router) at the novelty-classification layer
- tier hint: TIER-A target on content_reference_novelty channel alone (AUROC >= 0.85); composite over 4 channels potentially higher
- why-now: ablation value -- tells us which channel does the work; informs intent-router design for v3
- decisive test: per-channel AUROC + Mondrian-conformal composite AUROC

### 5. substrate_eval_recall_gap_supervised_F_2026-06-11  (BENCHMARK ONLY)
- pointer: research note section "Option F (parallel in_corpus_likelihood classifier)"
- substrate-product reading: benchmark for the unsupervised options to beat; introduces supervised-learning artifact which is mildly off-thesis (no LLM-as-judge norm)
- tier hint: TIER-A ceiling expected in-distribution (AUROC 0.90+); generalization is the risk
- why-now: only as upper-bound reference; do NOT ship as production classifier
- decisive test: train/val split AUROC + out-of-fold stress

## Context pointers (paths, not summaries)

- research note (full drill): d:/AI/hd-instrument/notes/research_drill_substrate_eval_recall_gap_alternatives_2x_2026-06-11.md
- substrate-two-axes empirical finding: memory file substrate_two_axes_semantic_vs_content_referenced_2026-06-11.md
- methodology rule (Findings 11 Layer 2): mp_bulk_kl 12x ratio = algebra codebook more structured than semantic (Q3 structural-saturation argument)
- prior substrate-eval drill chain: notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill[1-5]_2026-06-07.md
- substrate-self-index foundational tool memory: substrate_self_index_foundational_tool.md (4 partitions + 13 categories + algebra taxonomy)
- substrate-deep-self-evaluation 8-layer program memory: substrate_deep_self_evaluation_program_2026-06-11.md (Layer 2 spectral / Layer 6 weight-sweep / Tier 4 self-extension gate context)
- exp_dev brief: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-11_north_star.md

## Probe set spec (use for all 5 anchors)

Set A: 449 post-Phase-1 drill files known ingested into research_history partition; pull by file_id
Set B: 50-100 held-out drill-like files NOT in corpus; mixed-source (different agents, different dates) to break surface-form symmetry per methodology rule 8
Set A_perturbed: paraphrase-rewritten Set A (~50 files; cheap rewriting; preserves content-reference set but changes surface form) -- stress probe for recollection-vs-familiarity decomposition

## Contract

exp_dev owns:
- cell design (smoke + full + multi-seed if needed for TIER-A boundary CI rule)
- pre-reg per envelope-fail-bands (use stated HARD_PASS / MIDDLE_BAND / HARD_FAIL thresholds from research note)
- smoke gate before queue_add
- queue_add via queue_add.sh (or queue_add.py for local_cpu)
- post-ship REMOTE VERIFY
- per-cell self-test per formula-selftests

research owns:
- this hand-off file + the parent research drill note
- structural P_deflated estimates and decisive thresholds
- NOT cell-level python (per [[feedback-no-experiment-design-in-prompts]])

## Autonomy declaration

exp_dev autonomy: full on anchor sequencing within the rank order, smoke/CI/cost decisions, multi-seed at HP boundaries, choice of substrate-CPU runner vs home-CPU. Default sequence: ship 1 + 3 in parallel (B+H combined plus weighted-avg) first; sequence 2 (bundle-space G) after 1 reads; 4 (hierarchical J) as ablation after 1 + 2; 5 (supervised F) as benchmark only if time permits.

research autonomy: re-drill if AUROC HARD_FAIL on B+H -- that would refute dual-process hypothesis and trigger a different structural drill (Q3 codebook structural-bias deeper investigation).
