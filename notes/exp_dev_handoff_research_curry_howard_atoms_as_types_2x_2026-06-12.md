# exp_dev hand-off -- research: Curry-Howard atoms-as-types + substrate as proof verifier (2x)

Filed-by: research (Opus), 2026-06-12
Trigger: research drill notes/research_drill_curry_howard_atoms_as_types_substrate_dependent_types_proof_verification_2x_2026-06-12.md HEADLINE pre-registered CHTV-1 cell + predictions CH-P1..CH-P6
Pause state: respect data/orchestrator_paused.flag; if set, do not ship -- queue annotation only.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides ANCHOR POINTERS and CONTEXT POINTERS only. Exp-Dev owns experiment design.

## Anchor candidates (rank-ordered)

### Anchor 1 (tier-A): exp_substrate_curry_howard_type_checking_well_typed_ill_typed_witness_v1
- Substrate-product reading: substrate `prove --check witness goal` mode verifies a DEPENDS_ON-chain witness type-checks against a goal proposition; this is the substrate-as-VERIFIER surface (distinct from prior L6-PROOF substrate-as-FINDER drill). Demonstrates CH-P1 (well-typed PASS) + CH-P2 (ill-typed honest failure).
- Tier hint: A (substrate-product positioning win at LLM-categorical-gap scale; classical type-checker precision required at CH-P2 = 1.0).
- Why-now: 60/144 T1 algebra atoms shipped across 9 categories provide the proof-context corpus TODAY; no PHASE 2 ingest dependency for the cell; honest-failure axis already validated at 100% on Gap 7 negatives -> CH-P2 likely PASS.
- Pre-reg HARD-PASS / HARD-FAIL bands: see CH-P1 and CH-P2 in section (c) of research note. CH-P1 HP >= 6/8 = 0.75. CH-P2 HP = 8/8 = 1.00 (any hallucinated edge HARD-FAILs the cell -- type-checker precision is non-negotiable).
- P_deflated: 0.65 (mechanical path enumeration + reuses honesty axis; not novel-synthesis).
- Cost: ~3 hours local-CPU (8 atoms x 3 tests = 24 trials; pure substrate file IO + algebra_dict comparison; local laptop ALLOWED class per all-CPU-on-remote feedback).

### Anchor 2 (tier-A, complementary): exp_substrate_curry_howard_alpha_equivalent_proof_enumeration_v1
- Substrate-product reading: substrate `prove --equiv A B` decides whether two atoms are alpha-equivalent under algebra_dict OR connected via SHARES_MATH; demonstrates CH-P3 (identity-type / univalence-fragment surface).
- Tier hint: A (closes the dependent-type-layer thesis; SHARES_MATH-as-univalence-fragment is the load-bearing novel framing).
- Why-now: SHARES_MATH edge type already designed (per memory: substrate_mathematical_primitive_shares_math_architectural_insight); algebra_dict alpha-conversion is a ~40 LOC comparator.
- Pre-reg: CH-P3 HARD-PASS >= 2/3 = 0.67; HARD-FAIL < 1/3 = 0.33 (novelty-gated exploratory).
- P_deflated: 0.40 (depends on SHARES_MATH edge backfill being non-empty; gated on Strategy SHARES_MATH commit).
- Cost: ~1.5 hours local-CPU once SHARES_MATH edges populated.

### Anchor 3 (tier-A, novel-synthesis load-bearing): exp_substrate_defeasible_NbE_judgmental_equality_cleanup_gap_v1
- Substrate-product reading: substrate HRR-cleanup confidence is measured as a defeasible normalization-by-evaluation oracle for judgmental equality; this is the unified-Curry-Howard thesis (NbE + neural cleanup). CH-P5 isolation.
- Tier hint: A (substrate-product thesis novel-synthesis claim; if it lands, hybrid Curry-Howard prover positioning is product-ready; if it HARD-FAILs, fall back to "classical-checker + neural-heuristic-synthesizer" two-engine framing).
- Why-now: T1 algebra atoms encoded; PP-410 two-vector composite (alpha=0.5 wide robust plateau) is the cleanup primitive deployed.
- Pre-reg: CH-P5 HARD-PASS cleanup confidence gap >= 0.45 (TRUE equalities >= 0.85 AND FALSE equalities <= 0.40); HARD-FAIL gap < 0.20.
- P_deflated: 0.50 (novel-synthesis cap; lit-scan calibration penalty applied; no published direct precedent).
- Cost: ~2 hours CPU on T1 algebra atom pairs.

### Anchor 4 (tier-B, LLM categorical gap demonstration): exp_substrate_LLM_baseline_curry_howard_24_trials_v1
- Substrate-product reading: same 24 trials from CHTV-1 (Anchor 1) given to small-LLM (1.5B instruct) baseline; demonstrates LLM cannot match CH-P1+CH-P2 jointly (LLM expected to fail CH-P2 honest-failure per arxiv 2401.11817 hallucination-inevitability).
- Tier hint: B (substrate-LLM categorical-gap evidence for product narrative; gated on Anchor 1 ship).
- Why-now: gated on Anchor 1 PASS; cheap follow-up (~1 hr LLM inference on REMOTE per all-CPU-on-remote feedback).
- Pre-reg: CH-P6 HARD-PASS substrate combined score >= LLM by >= 0.20 absolute; HARD-FAIL substrate matches or trails LLM.

## Context pointers (file paths; not summaries)

- notes/research_drill_curry_howard_atoms_as_types_substrate_dependent_types_proof_verification_2x_2026-06-12.md
- notes/research_drill_substrate_as_differentiable_theorem_prover_surface_USER_goal_aligned_2x_2026-06-12.md (prior L6-PROOF drill; this 2x EXTENDS it with type-checking layer)
- notes/exp_dev_handoff_research_substrate_as_differentiable_theorem_prover_surface_2026-06-12.md (prior hand-off; anchors are COMPLEMENTARY not duplicative -- prior = FINDER, this = VERIFIER)
- backend/substrate_index/algebra_index.py (PP-410 two-vector composite production code; alpha=0.5 plateau)
- tools/substrate_query.py (existing 9-subcommand CLI surface; extend with `prove --check` and `prove --equiv` modes)
- T1 algebra backfill batches 01-06 (60/144 atoms across 9 categories: linear_algebra + probability + info_theory + topology + analysis + inequalities + convexity + abstract_algebra + category_theory)
- memory: substrate_algebra_coverage_gap_two_populations_backfill_144_T1_2026-06-12.md
- memory: substrate_mathematical_primitive_shares_math_architectural_insight_2026-06-12.md (SHARES_MATH-as-univalence-fragment basis for Anchor 2)
- memory: substrate_self_knowing_HP_v2_macro_F1_0_569_Cycle_47_2026-06-12.md (honesty axis 100% on negatives validates CH-P2 prior)
- memory: substrate_two_vector_alpha_wide_robust_plateau_high_d_orthogonality_2026-06-12.md (cleanup primitive for Anchor 3)
- memory: feedback_all_cpu_compute_on_remote_desktop_2026-06-11.md (Anchors 1+2 are local-allowed pure-file-IO; Anchor 3 cleanup-dense goes REMOTE; Anchor 4 LLM baseline REMOTE)

## Contract

- Exp-Dev owns experiment design (per [[feedback-no-experiment-design-in-prompts]]).
- Pre-reg envelope per envelope-fail-bands; smoke gate; ship via queue_add.sh; post-ship REMOTE VERIFY; self-test per formula-selftests.
- Pause-gated by data/orchestrator_paused.flag.
- No LLM-as-judge for Anchors 1-3 (substrate-quality-first); LLM baseline for Anchor 4 is COMPARISON only (substrate score is ground truth).
- Literature-is-not-oracle: Typed-CoT (arxiv 2510.01069) and NTP numerics are PRIOR not ORACLE.
- CH-P2 is type-checker-precision-critical: any single hallucinated DEPENDS_ON edge HARD-FAILs the cell. Do NOT relax this threshold to make the cell PASS.

## Autonomy declaration

- Exp-Dev MAY reorder anchors based on pipeline state (Anchor 3 may need to ship first if cleanup-gap measurement requires fresh re-encoding).
- Exp-Dev MAY swap test atom count from 8 to [6, 12] based on T1 atoms with depth-2 DEPENDS_ON chains actually present (corpus dictates feasibility).
- Exp-Dev MAY merge Anchors 1+2 into a single smoke if SHARES_MATH backfill is present at runtime.
- Exp-Dev MAY downgrade Anchor 3 to MIDDLE-only smoke if T1 coverage proves too sparse for clean TRUE/FALSE pair selection -- honest middle, not failure.
- Exp-Dev MAY defer Anchor 4 entirely if Anchor 1 fails (no LLM-categorical-gap claim to demonstrate).

End of hand-off.
