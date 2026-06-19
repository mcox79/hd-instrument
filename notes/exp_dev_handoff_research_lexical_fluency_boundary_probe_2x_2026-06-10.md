# exp_dev hand-off -- research: lexical fluency boundary probe 2x

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_lexical_fluency_boundary_probe_2x_2026-06-10.md
Urgency: HIGH -- resolves the corpus-vs-architecture boundary for Tier 4 generation; directly enables NORTH STAR head-to-head claim on formal-document generation and code generation; PP-225 bridge already validated, this is the next empirical gate

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: lex_hybrid_paragraph_gen_v1 (LEX-3)

Anchor pointer: Research note Section "Cheap decisive test" + Section "Where this hybrid is competitive"; PP-225 projection (heldout=1.000, current experimental state).
Substrate-product reading: Implements PP-225 frame projection into LLM conditioning for formal-text generation. Uses 20 formal documents (regulatory, legal, medical). Measures schema compliance, factual preservation, ROUGE/BERTScore vs LLM-alone baseline. Validates the primary hybrid claim: substrate schema framing improves LLM output compliance without degrading fluency on formal genres.
Tier hint: CPU-local. 160M-parameter LLM is sufficient for smoke. PP-225 bridge already implemented -- only the conditioning integration and evaluation harness are new.
Why-now: PP-225 heldout=1.000 proves the projection works algebraically. LEX-3 is the first end-to-end test of whether it improves generation quality in the downstream task. This is the NORTH STAR formal-document benchmark seed experiment.

Pre-reg bands:
  HARD-PASS: Schema compliance of hybrid >= LLM-alone + 20 percentage points on 20-item benchmark AND factual preservation >= LLM-alone AND ROUGE within 15% of LLM-alone
  MIDDLE-BAND: Schema compliance improvement 10-20 pp OR factual preservation improvement with ROUGE gap > 15% (triggers pipeline tuning anchor)
  HARD-FAIL: Schema compliance of hybrid not better than LLM-alone on formal documents (PP-225 projection not carrying structural signal into generation path; architecture revision required)

### Anchor 2: subword_composition_v1 (LEX-2)

Anchor pointer: Research note Section "Compositional subword generation via substrate binding"; SUBWORD-COMPOSITION engineering anchor.
Substrate-product reading: Implements morpheme-level atom binding over ~5K morpheme inventory. Composes 200 test words from morpheme atoms. Evaluates form correctness (exact match) and semantic preservation (cosine similarity of composed atom vs reference embedding). Validates whether morphological binding is a viable OOV coverage path without corpus scaling.
Tier hint: CPU-local laptop. Small N. Binding operations are existing substrate capability. The experiment is evaluation, not new mechanism.
Why-now: If this passes, OOV coverage is architecture-achievable without 1M-atom codebook scaling. If it fails, corpus-scaling (Anchor 3) becomes the only OOV path. This is the cheap gate before committing to large codebook experiments.

Pre-reg bands:
  HARD-PASS: > 70% of 200 composed forms have cosine similarity > 0.70 vs reference embedding for the target word
  MIDDLE-BAND: 50-70% semantic preservation (partial coverage; triggers selective morpheme-atom selection)
  HARD-FAIL: < 50% semantic preservation (morphological binding does not preserve distributional meaning; 1M-atom codebook scaling is required for OOV path)

### Anchor 3: tier4_codebook_scale_v1 (LEX-1)

Anchor pointer: Research note Section "Codebook scaling analysis: 10K to 1M atoms"; TIER-4-CODEBOOK-SCALE engineering anchor.
Substrate-product reading: Trains substrate at 10K, 100K, and target scale using projector-mediated VQ alignment. Measures retrieval F1, token coverage on a 10K-sample text corpus, and codebook utilization per tier. Validates the claim that 100K atoms achieves competitive coverage with pre-2020 LLM vocabulary class AND that 1M-atom scaling is feasible at 99%+ utilization.
Tier hint: 10K and 100K are CPU-local. 1M-atom requires GPU or extended CPU run. Dispatch 10K and 100K first; 1M only if utilization holds at 100K.
Why-now: Establishes the empirical corpus-coverage curve. Without this, the 100K competitive-with-LLM-vocabulary claim is theoretical only. Cheap to run at 10K/100K; provides the data point for codebook-scale investment decisions.

Pre-reg bands:
  HARD-PASS: 100K-atom F1 >= 90% of LLM embedding retrieval F1 on a standard 1K-query IR benchmark AND utilization >= 95%
  MIDDLE-BAND: F1 80-90% (confirmed coverage gap; triggers corpus-scaling investment discussion)
  HARD-FAIL: F1 < 70% of LLM embedding at 100K (corpus gap is wider than estimated; cannot close with architecture alone at current scales)

### Anchor 4: formal_genre_benchmark_v1 (LEX-5)

Anchor pointer: Research note Section "Engineering anchors" Anchor 4; NORTH STAR note.
Substrate-product reading: Constructs 100-item formal-document benchmark (20 each: regulatory filing, medical summary, legal agreement, financial disclosure, GDPR notice). Evaluates substrate hybrid vs LLM-alone vs template-rule-based. This is the NORTH STAR head-to-head artifact for formal-document generation. Depends on Anchor 1 passing.
Tier hint: CPU-local benchmark construction and evaluation. Deferred until Anchor 1 is validated. Anchor 1 verdict determines whether the benchmark should proceed.
Why-now: NORTH STAR requires empirical head-to-head. This is the measurement instrument for formal documents. File here so it is not lost when Anchor 1 completes.

Pre-reg bands:
  HARD-PASS: Substrate hybrid schema compliance rate > LLM-alone AND factual precision > LLM-alone on >= 3 of 5 document categories
  HARD-FAIL: Substrate hybrid weaker than LLM-alone on >= 3 categories (formal-document hypothesis refuted; audit-chain is the only differentiated claim remaining)

### Anchor 5: audit_preserving_lex_v1 (AUDIT-PRESERVING-LEX)

Anchor pointer: Research note Section "Engineering anchors" Anchor 5; EU AI Act Article 12 (Aug 2026).
Substrate-product reading: Implements generation trace logging in the hybrid pipeline. Records atom sequence, PP-225 projection vectors, LLM conditioning inputs, output tokens per generated document. Validates that documents have full derivation traces. This is the EU AI Act Article 12 compliance experiment -- audit capability is a regulatory requirement for high-risk AI systems in regulated domains (effective Aug 2026).
Tier hint: CPU-local. No GPU needed. Pure logging and trace verification. Can run in parallel with any of Anchors 1-4.
Why-now: EU AI Act Article 12 compliance deadline is Aug 2026. For the product to be deployable in regulated European domains (healthcare, financial services, legal), audit trails are required. This anchor converts the research claim into a compliance artifact.

Pre-reg bands:
  HARD-PASS: Full document derivable from logged trace (atom + projection + conditioning + output) with zero information gap
  HARD-FAIL: Trace incomplete or not reconstructable (audit-chain claim cannot be made; fundamental logging redesign required)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_lexical_fluency_boundary_probe_2x_2026-06-10.md
- PP-225 projection (bridge state): d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- NORTH STAR note: d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- C1-FACT fact-recall findings: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09.md
- Corpus-size scaling probe (prior handoff): d:/AI/hd-instrument/notes/exp_dev_handoff_corpus_size_scaling_probe_2026-05-27.md
- Full post-compaction system state: d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md

---

## Contract

exp_dev owns:
- Anchor prioritization within this file (may reorder based on queue depth + runner availability)
- Experiment design details: cell grids, hyperparameter values, script structure
- Pre-reg envelope refinement from the bands above
- Go/no-go decision per pause gate

Research sub-agent provided:
- Ranked anchor candidates with substrate-product readings
- Pre-reg band proposals (NOT final -- exp_dev calibrates from cap_map context)
- Context pointers (file paths, not summaries)

---

## Autonomy declaration

exp_dev may dispatch Anchor 2 (LEX-2 subword composition) immediately if pause gate is clear -- it is small, CPU-local, and gates Anchor 3 routing decision.
Anchor 1 (LEX-3 hybrid pipeline) is the primary claim experiment; dispatch after Anchor 2 verdict or in parallel if queue has capacity.
Anchor 3 (LEX-1 codebook scale) at 10K/100K may dispatch in parallel with Anchor 1.
Anchors 4 and 5 should wait for Anchor 1 verdict.
No authorization needed for CPU-local anchors under the standing experiment authorization.
