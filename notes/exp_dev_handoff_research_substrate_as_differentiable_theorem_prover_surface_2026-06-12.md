# exp_dev hand-off -- research: substrate as differentiable theorem-prover surface (L6-PROOF)

Filed-by: research (Opus), 2026-06-12
Trigger: research drill notes/research_drill_substrate_as_differentiable_theorem_prover_surface_USER_goal_aligned_2x_2026-06-12.md HEADLINE pre-registered cell
Pause state: respect data/orchestrator_paused.flag; if set, do not ship -- queue annotation only.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides ANCHOR POINTERS and CONTEXT POINTERS only. Exp-Dev owns experiment design.

## Anchor candidates (rank-ordered)

### Anchor 1 (tier-A): exp_substrate_proof_unfolder_backward_chaining_axiom_DEPENDS_ON_v1
- Substrate-product reading: substrate proves multi-step lemma chains over algebra-tagged atoms via FHRR-unification backward chaining; substrate-product positioning extension from "self-knowing" (level-1 metacognition) to "self-deducing" (level-2 metacognition).
- Tier hint: A (substrate-product positioning win at categorical-gap-vs-LLM scale; closes USER goal "substrate understands its own mathematics").
- Why-now: BATCH 01 algebra backfill (10 atoms) is shipped; BATCH 02 (30 atoms) is the corpus precondition; PP-410 two-vector composite (alpha=0.5 wide robust plateau) is the unification primitive already deployed; substrate_query.py CLI already exists with 9 subcommands as the interface surface to extend.
- Pre-reg HARD-PASS / HARD-FAIL bands: see section (c) of research note (5 goals, score floors, SHARES_MATH transfer >= 0.80, LLM-baseline comparison).
- P_deflated: 0.45 (cap 0.50 novel-synthesis; deflation 0.20).
- Cost: ~2-3 hours CPU + ~1 day algebra-dict authoring for BATCH 02.

### Anchor 2 (tier-B, gated): exp_substrate_SHARES_MATH_lemma_reuse_proof_transfer_v1
- Substrate-product reading: validate that proving one member of a SHARES_MATH equivalence class transfers to all members at >= 0.80 of original proof score; this is the substrate-native LEMMA REUSE compression metric.
- Tier hint: B (depends on Anchor 1 success; second-order observability metric).
- Why-now: gated on Anchor 1 PASS; cheap follow-up (~30 min CPU) once L6-PROOF unfolder ships.
- Pre-reg: HARD-PASS transfer >= 0.80; HARD-FAIL < 0.50.

### Anchor 3 (tier-C, scope-expansion): exp_substrate_rule_induction_RNNLogic_analog_DEPENDS_ON_learned_v1
- Substrate-product reading: substrate LEARNS new DEPENDS_ON edges from its own proof-attempt history (solution_history partition); RNNLogic / Neural-LP analog adapted to substrate's algebra-tagged graph.
- Tier hint: C (longer horizon; substrate self-extending in proof domain).
- Why-now: gated on Anchors 1+2; medium-term Cycle 53+ candidate.
- Pre-reg: TBD pending Anchor 1+2 verdicts.

## Context pointers (file paths; not summaries)

- notes/research_drill_substrate_as_differentiable_theorem_prover_surface_USER_goal_aligned_2x_2026-06-12.md
- backend/substrate_index/algebra_index.py (PP-410 two-vector composite production code)
- tools/substrate_query.py (existing 9-subcommand CLI surface)
- BATCH 01 algebra backfill output (vector_space + cosine_similarity + shannon_entropy + kl_divergence + axioms + linear_independence + basis + span + inner_product + orthogonality)
- notes/research_drill_shares_math_subgraph_equivalence_class_compression_*_2026-06-12.md (SHARES_MATH compression primitive)
- notes/research_drill_L3_DisCoCat_*_2026-06-12.md (categorical-foundation context for proof composition)
- notes/research_drill_coalgebraic_semantics_*_2026-06-12.md (bisimulation context for SHARES_MATH-as-lemma-reuse)
- memory: substrate_algebra_coverage_gap_two_populations_backfill_144_T1_2026-06-12.md
- memory: substrate_two_vector_alpha_wide_robust_plateau_high_d_orthogonality_2026-06-12.md
- memory: substrate_as_self_knowing_system_2026-06-12.md

## Contract

- Exp-Dev owns experiment design (per [[feedback-no-experiment-design-in-prompts]]).
- Pre-reg envelope per envelope-fail-bands; smoke gate; ship via queue_add.sh; post-ship REMOTE VERIFY; self-test per formula-selftests.
- Pause-gated by data/orchestrator_paused.flag.
- No LLM-as-judge; substrate-quality-first; literature-is-not-oracle (DRUM/RNNLogic/NTP numerics are PRIOR not ORACLE per substrate_extracted_rules_are_prior_not_oracle_2026-06-12.md).

## Autonomy declaration

- Exp-Dev MAY reorder anchors based on pipeline state (BATCH 02 authoring may need Research/Strategy follow-up before Anchor 1 ships; Exp-Dev decides smoke-gate sequencing).
- Exp-Dev MAY swap unification floor (0.30) to a robust-plateau-justified alternative within [0.20, 0.40] per PP-410 measurements.
- Exp-Dev MAY add G6+ goals if BATCH 02 reveals additional natural depth-<=5 chains.
- Exp-Dev MAY downgrade Anchor 1 to MIDDLE-only smoke if BATCH 02 authoring is incomplete -- corpus deficiency is honest middle, not failure.

End of hand-off.
