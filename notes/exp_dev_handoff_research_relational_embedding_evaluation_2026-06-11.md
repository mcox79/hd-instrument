# exp_dev hand-off — research: relational embedding + cross-corpus retrieval evaluation harness

Filed-by: research sub-agent
Date: 2026-06-11
Trigger: research drill delivery -> notes/research_drill_relational_embedding_evaluation_2x_2026-06-11.md

## Pause state

Honor data/orchestrator_paused.flag. This handoff is a queued candidate; ship only when pipeline accepts new authorized work.

Per [[feedback-no-experiment-design-in-prompts]] — this file lists ANCHOR POINTERS and substrate-product reading, not experiment specs. exp_dev designs the cells.

## Anchor candidates (rank-ordered)

### Anchor A (Tier-1, PRIORITY): CLUTRR-pattern compositional retrieval on substrate

- Substrate-product reading: substrate's structural strength is in multi-hop relational traversal; CLUTRR is the cleanest synthetic protocol for this in the published literature (Sinha-Sodhani 2019, NeurIPS).
- Why-now: research note pre-registered Q2 (multi-hop compositional retrieval) with HARD-PASS substrate >= 0.55 at depth-3 / LLM-RAG <= 0.35 / lift >= 2x SE. This is the cleanest substrate-vs-LLM discriminator with externally-verifiable synthetic ground truth.
- Anchor pointer: see notes/research_drill_relational_embedding_evaluation_2x_2026-06-11.md section "Falsifiable predictions" Q2.
- Tier hint: Tier-1 (high-value structural-claim falsifier; ~2-3 days build + 1 day eval).
- Adjacent prior: substrate v3.0 compositional cliff crossed 2026-06-10 (L5 recall 0.000->1.000). CLUTRR-on-substrate is the natural external benchmark for that cliff-crossing claim.

### Anchor B (Tier-1): SME structural-analogy retrieval with disjoint-vocab control

- Substrate-product reading: substrate's algebraic role-filler binding (Plate HRR / FHRR) is cognate to LISA's relational binding via synchrony; both predict structural-similarity is detectable when surface tokens differ. LLM-RAG keys on lexical/semantic surface and should fail.
- Why-now: research note Q3 (structural analogy) HARD-PASS substrate >= 0.40 / LLM-RAG <= 0.15 / lift >= 3x SE. This is the MOST distinguishing axis if substrate is genuinely relational.
- Anchor pointer: research note section "Cross-thread synthesis" subsection 4 (SME / LISA), and "Falsifiable predictions" Q3.
- Tier hint: Tier-1 (highest discriminator; ~2 days build + 1 day eval). Pair with Anchor A.
- Adjacent prior: substrate cross-domain RETRACTION 2026-06-10 — disjoint-vocab control here addresses the entity-geometry / degree-bias confound that retracted P9. SME systematicity scoring is exactly the right protocol.

### Anchor C (Tier-2): MIRB-style 3-axis text-math retrieval decomposition

- Substrate-product reading: cross-corpus retrieval (math-op <-> concept-claim) has a published canonical benchmark (MIRB arXiv 2505.15585) with 4 subtasks; substrate's bidirectional cross-link claim is testable on Premise Retrieval + Formula Retrieval subtasks specifically.
- Why-now: research note Q4 (cross-corpus bridge) HARD-PASS substrate Hits@10 >= 0.75 in either direction; symmetry gap < 0.10.
- Anchor pointer: research note section "Cross-thread synthesis" subsection 7.
- Tier hint: Tier-2 (broader scope, more corpus infra; ~3-5 days build).

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_relational_embedding_evaluation_2x_2026-06-11.md (THIS drill — primary)
- d:/AI/hd-instrument/notes/substrate_v3_compositional_cliff_crossed.md (prior substrate cliff-crossing evidence)
- d:/AI/hd-instrument/notes/substrate_cross_domain_retraction_2026-06-10.md (prior cross-domain retraction; SME disjoint-vocab addresses this)
- d:/AI/hd-instrument/notes/slipnet_polysemic_substrate_only_ceiling_2026-06-11.md (WN18RR diagnostic precedent; OGB-style filtered-rank protocol applicable)
- d:/AI/hd-instrument/MEMORY.md feedback indices: lit-scan calibration penalty, method-overclaim lift validation, smoke-test methodology, drill-defeatism

## Contract section

- HARD-PASS / HARD-FAIL thresholds pre-registered in the research note (Q1-Q5).
- Externally-verified ground truth REQUIRED — no LLM-as-judge in the eval loop (per circular-evaluation literature).
- Lift-over-baseline scoring with 2x SE CI bands (per [[feedback-method-overclaim-lift-validation]]).
- Smoke gate before full eval (per [[feedback-smoke-test-methodology]]) — composition-matched smoke, CI-band rule, multi-seed at HP boundaries.
- Pre-dispatch checklist (speed audit / failure-mode hardening / progress-saving) per [[feedback-pre-dispatch-speed-harden-progress-discipline]].

## Autonomy declaration

exp_dev decides:
- which anchor to ship first (A vs B priority; both Tier-1)
- corpus construction details (size, depth range for CLUTRR-pattern, vocab-disjoint protocol for SME)
- substrate retrieval pipeline (which tier, cleanup policy, threshold)
- baseline LLM-RAG configuration (encoder, top-k, prompt template)
- compute budget (CPU vs GPU; aim CPU-first per pure-numpy patterns)

Research does NOT prescribe the experiment design beyond the pre-registered Q1-Q5 thresholds. If exp_dev finds the thresholds need revision (e.g. Q2 depth-3 too easy or too hard), file a strategy_request back to research, do not silently relax.
