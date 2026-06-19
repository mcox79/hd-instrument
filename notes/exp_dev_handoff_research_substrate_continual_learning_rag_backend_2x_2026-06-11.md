# exp_dev hand-off -- research: substrate continual-learning at production scale + substrate-as-RAG-backend (2x DEEP drill)

filed-by: research:opus
trigger: 2x DEEP combined drill on two open scaling questions surfaced by PP-225 production validation
research-note: d:/AI/hd-instrument/notes/research_drill_substrate_continual_learning_rag_backend_2x_2026-06-11.md
date: 2026-06-11

## Pause state

Check d:/AI/hd-instrument/data/orchestrator_paused.flag at pickup time. If present, log hand-off pickup intent in status_log and HOLD until resume.

## Per [[feedback-no-experiment-design-in-prompts]]

This handoff specifies WHAT to test and WHY (anchors, HARD-PASS / HARD-FAIL thresholds, decisive observables) but NOT the experiment-design specifics (cell topology, batch size, smoke composition, runner placement). exp_dev owns those decisions per autonomy contract.

## Anchor candidates (rank-ordered)

### Anchor 1 (lead, tier hint = production-decisive)

- **Anchor pointer**: Test A -- continual-learning million-scale streaming on substrate
- **Substrate-product reading**: validates (or bounds) the substrate-as-million-scale-continual-learning-KB commercial claim. PP-225 kb25k 0.996 validates at 25k single-batch; this test extends to 1M incremental (40x scale, streaming regime).
- **Tier hint**: production-decisive (single-batch validated; incremental untested at this scale; literature precedent in HDC streaming but no published 1M substrate benchmark)
- **HARD-PASS / HARD-FAIL**: see research note section (c) P1.1, P1.2, P1.3
- **Why-now**: production claim ladder needs the next rung above kb25k; incremental ingestion is the operationally-relevant mode for any real deployment
- **Decisive observables**: forgetting curves at 5 anchor batches; tier-2 atom-isolation margin and Parisi-q overlap (existing observability); compare to single-batch baseline at 1M

### Anchor 2 (lead, tier hint = commercial-load-bearing)

- **Anchor pointer**: Test B -- substrate-as-RAG-backend head-to-head vs pgvector on Wikipedia 100k
- **Substrate-product reading**: first direct substrate-vs-vector-DB benchmark. Decides whether substrate-as-RAG-backend is a viable commercial wedge against the established vector-DB market (Pinecone, Qdrant, Weaviate, Milvus, pgvector, ChromaDB).
- **Tier hint**: commercial-load-bearing (no prior substrate-vs-vector-DB benchmark exists; all RAG commercial claims downstream of this)
- **HARD-PASS / HARD-FAIL**: see research note section (c) P2.1, P2.2, P2.3, P2.4
- **Why-now**: aligns with North Star (functional system beats LLMs of relative size in measurable ways); substrate-as-retrieval-layer is the direct LLM-app integration point; commercial story has not been empirically grounded yet
- **Decisive observables**: retrieval@5 recall; P50/P99 latency; calibrated-abstention rate (true-abstain on adversarial OOD MINUS false-abstain on in-distribution); end-to-end LLM answer accuracy with Pythia-1.4B generator; LLM-judge or NLI-entailment hallucination rate

### Anchor 3 (follow-on, conditional)

- **Anchor pointer**: 3-tier substrate consolidation policy validation
- **Substrate-product reading**: validates the unified architectural recommendation (single 3-tier substrate solves both continual learning AND RAG backend)
- **Tier hint**: architectural-grounding (foreshadowed by CLS literature + substrate v3.2 engineered-wrapper memory; not yet empirically validated as single architecture for both modes)
- **Gate**: run if Anchor 1 OR Anchor 2 produces a PARTIAL result that suggests 3-tier-specific rescue
- **Decisive observable**: does the SAME 3-tier deployment achieve both Anchor 1 HARD-PASS thresholds AND Anchor 2 HARD-PASS thresholds without architectural divergence

## Context pointers (paths, not summaries)

- Research note (full thresholds + lit synthesis): d:/AI/hd-instrument/notes/research_drill_substrate_continual_learning_rag_backend_2x_2026-06-11.md
- PP-225 production validation context: search status_log for "PP-225 genuine kb25k"
- Substrate v3.2 engineered wrapper context (5 protection layers): C:/Users/marsh/.claude/projects/d--AI/memory/substrate_v32_engineered_wrapper_2026-06-11.md
- STATIC-robust DYNAMIC-fragile pattern: C:/Users/marsh/.claude/projects/d--AI/memory/substrate_static_robust_dynamic_fragile_2026-06-10.md
- Substrate-LLM boundary decomposition: C:/Users/marsh/.claude/projects/d--AI/memory/substrate_LLM_boundary_decomposition_2026-06-10.md
- Conformal calibration prior drill (cleanup-margin = Vovk NN distance-ratio): search recent research_decisions for "substrate_conformal_calibration_2x"
- Testbed Wikipedia 184K facts already extracted: search testbed brief for "Wikipedia 100K DONE (184K facts)"
- Testbed ConceptNet 458K and arXiv in progress: same brief

## Contract section

- exp_dev owns: cell topology, lane selection (GPU home / home-CPU / cpu_runner_local), smoke composition + thresholds, batch sizing, runner placement, queue ordering, verdict reporting
- research owns: anchor selection rationale, HARD-PASS / HARD-FAIL thresholds, lit synthesis, post-verdict synthesis with prior threads
- verdict_handler owns: per-cell PASS/FAIL/PARTIAL classification per honest-re-read protocol
- strategy_scribe owns: cap_map bumps post-verdict

## Autonomy declaration

exp_dev decides ALL of:
- Which anchor ships first (1 vs 2, or in parallel if capacity allows)
- Smoke composition: which substrate config, which batch sizes, which observability cadence
- Runner placement: GPU home for any encoder-heavy work; CPU lanes for substrate-only cells
- Pre-flight verification: smoke gate on a 10k sub-test before 1M run; smoke gate on a 5k pgvector + substrate sub-test before 100k run
- Resource budget: Anchor 1 estimated ~3-6 hours single 1M run + observability snapshots; Anchor 2 estimated ~4-8 hours including pgvector setup
- Whether to do Anchor 1 first (continuity with PP-225) or Anchor 2 first (commercial-pull priority)

## Pre-reg discipline reminder

Per envelope-fail-bands: pre-register HARD-PASS / HARD-FAIL bands BEFORE running cells, not after. Thresholds in research note section (c) are the pre-reg source of truth. Any band tightening or relaxation between pre-reg and ship must be logged in the cell pre-reg comment with rationale.

Per formula-selftests: each cell self-tests its observability code path (atom-isolation margin / Parisi-q overlap / cleanup-margin) BEFORE shipping. Self-test must exercise the actual code path used in the cell, not a parallel reference path.

Per [[feedback-method-overclaim-lift-validation]]: if Anchor 1 or Anchor 2 reports a method-rescue (e.g. "3-tier rescues 1M continual learning"), verify LIFT > 2*SE, not just absolute threshold. Single-batch baseline is the canonical comparator.
