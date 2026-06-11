# exp_dev hand-off -- research: substrate algebra-encoding architecture (shared-basis 2x DEEP)

Filed-by: research sub-agent (2x DEEP drill)
Date: 2026-06-11
Trigger: research drill at notes/research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag (CPU-only experiments are routinely allowed during pause; check flag)

Per [[feedback-no-experiment-design-in-prompts]]: this file lists pointers and anchor-candidates; exp_dev owns the experiment design and pre-registration.

## Anchor candidates (rank-ordered)

### Anchor 1 -- ALGE-RRF-1 (CPU, ~1.5-2.5 hr)
- Pointer: research note section "EXP-A: RRF-HYBRID two-index baseline"
- Substrate-product reading: validates the recommended primary architecture for v2 (hybrid two-index + RRF). If passes, substrate ships algebra-aware-retrieval as the v2 differentiator. If fails, substrate falls back to Fix B and loses the algebra-aware-retrieval product story.
- Tier hint: Tier B (decisive for v2 architecture commit; cheap CPU)
- Why now: substrate-self-index v1 already showed cosine-on-tag-sum net-negative on Q2/Q3; v2 ships in 3-4 eng-days and EXP-A unblocks the architecture decision

### Anchor 2 -- ALGE-INTENT-1 (CPU, ~30 min)
- Pointer: research note section "EXP-C: QUERY-INTENT ROUTER decisive test"
- Substrate-product reading: validates whether intent-routing earns its complexity or whether always-RRF is the simpler ship. Customer-visible feature ("ask substrate about algebra and it answers from the algebra index") rides on this passing.
- Tier hint: Tier B (low-cost, gates one product feature)
- Why now: 30 min cost; should run alongside Anchor 1 in same lane

### Anchor 3 -- ALGE-ORTHO-1 (CPU, ~1-2 hr)
- Pointer: research note section "EXP-B: ORTHOGONAL-SUBSPACE single-vector composite"
- Substrate-product reading: validates the FALLBACK 1 single-vector architecture. Run only if Anchor 1 partially passes or shows mixed signal. If Anchor 1 fully passes, Anchor 3 is informative but not gating.
- Tier hint: Tier C (fallback validation; defer unless Anchor 1 ambiguous)
- Why now: substrate may prefer single-vector storage for some customer integrations; worth knowing the answer even if not gating

### Anchor 4 -- ALGE-ALG-ONLY-1 (CPU, ~30 min)
- Pointer: research note section HP-4 ("algebra-only index by itself achieves rank-1 on Q2 family-tag and Q3 count_nb")
- Substrate-product reading: validates whether the substrate-native TPR/HRR algebra encoding is functionally adequate at all. If this fails (HF-3), the substrate-product differentiator narrative is at risk and the issue is substrate-physics, not retrieval architecture. Escalate to GHRR per cross-thread note.
- Tier hint: Tier A (diagnostic for substrate-physics)
- Why now: defensive -- catches the case where the algebra primitive itself is the bottleneck; very cheap to run

### Anchor 5 -- ALGE-GHRR-1 (CPU, ~2-3 hr) -- ONLY if Anchor 4 fails
- Pointer: cross-thread to notes/research_drill_operator_algebras_subfactor_theory_2x_2026-06-11.md
- Substrate-product reading: substrate-physics deepening; matrix-bind GHRR replaces phasor-bind HRR for algebra encoding
- Tier hint: Tier C (only on HF-3 escalation)
- Why now: substrate-physics rescue path if Anchor 4 falsifies the HRR primitive on this corpus

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11.md (this drill)
- d:/AI/hd-instrument/notes/research_drill_categorical_ai_discocat_2x_2026-06-11.md (DisCoCat -- algebra-as-typed-binding convergence)
- d:/AI/hd-instrument/notes/research_drill_operator_algebras_subfactor_theory_2x_2026-06-11.md (GHRR escalation path)
- d:/AI/hd-instrument/notes/exp_dev_handoff_research_categorical_ai_discocat_2026-06-11.md (companion exp_dev anchors from this morning -- some overlap with Anchor 4 diagnostic)
- Substrate-self-index v1 evaluation queries Q1..Q5 (exp_dev knows where these live)

## Contract

- Pre-reg per envelope-fail-bands; HP/HF thresholds already specified in the research drill section (c); exp_dev may tighten further at design time
- Smoke gate before full corpus run
- Ship via queue_add per local-CPU queue convention (cpu_runner_local on FrameworkMPC if home is busy)
- Post-ship REMOTE VERIFY
- Self-test per formula-selftests
- Honest re-read of verdict_msg vs per-cell metrics

## Autonomy declaration

exp_dev owns:
- exact test corpus selection (atoms, query set)
- HRR vs FHRR vs TPR choice for the algebra index in Anchor 1 (research recommends HRR for v2 simplicity but FHRR is acceptable if exp_dev has prior validated)
- RRF k value (research recommends k=60 industry default; exp_dev may sweep)
- intent-router lexicon construction (research suggested initial vocab; exp_dev refines)
- alpha/beta sweep grid for Anchor 3 (research suggested initial grid)
- exact metric for "rank improvement" (top-1 hit-rate vs top-3 hit-rate vs MRR -- exp_dev picks the substrate-product-relevant one)
- ordering and lane allocation across the 4 anchors

Research declines to specify these.
