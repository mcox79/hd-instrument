# exp_dev hand-off — research: complementary coverage partitioning formalization (KP ODK-CC)

Filed-by: research (Opus drill, 2026-06-13)
Trigger: research note `notes/research_DRILL_complementary_coverage_partitioning_formalization_INV2a_KP_architectural_extension_2026-06-13.md`
Pause state: respect `data/orchestrator_paused.flag` if present at pickup time; this hand-off is structural and may be picked up on next emergency-refill or scheduled exp_dev cycle.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev decides ALL cell design details (atom selection, codebook sample, tier filters, exact mechanism invocation). The pointers below are anchor candidates and structural reasoning, not experiment prescriptions.

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY): CELL KP-COMPL — operator-decomposed K-fold complementary coverage validation
- Anchor pointer: held-out atom set (target ~150 atoms, balanced across 3 structural classes — T3 records / T1-T2 cross-disciplinary / T3 math-codebook); run P1, P3, P4 independently; measure pairwise candidate overlap, union recall vs best-single recall, Q-statistic on error-indicator vectors, Coincident-Failure Diversity (CFD), and joint entropy of mechanism candidate-set indicators.
- Substrate-product reading: validates "ODK-CC" claim — K-fold operator decomposition with intrinsic structural gating — as substrate-product positioning vs LLMs' entangled-embedding architectural inability. Closes INV-2a's candidate-set finding into an oracle-recall HARD-PASS artifact.
- Tier hint: KP capability column; promotion-operator architectural property; ODK-CC novel-claim 1st-appearance candidate.
- Why-now: INV-2a HARD-PASS just refuted "convergence" framing and surfaced the partition-coverage finding; the next empirical extension is oracle-recall union dominance + CFD bound. Cost ~30 min CPU local. Pre-registered HARD-PASS / HARD-FAIL thresholds in the research note section (c).

### Anchor 2 (SECONDARY): CELL KP-LEAKAGE — cross-class leakage stress test
- Anchor pointer: construct adversarial atoms designed to look like one class but actually belong to another (e.g. a T3 math atom with high graph-degree mimicking a T3 record); measure L_ij leakage matrix to see if mechanism specialization survives adversarial routing.
- Substrate-product reading: stress-tests the "intrinsic gating" claim — does mechanism specialization survive when structural signals partially overlap? Either result is publishable substrate-product evidence (robust => claim strengthens; fragile => refines claim to "class-pure regime only").
- Tier hint: KP capability column; robustness sub-property of ODK-CC; not primary HP — supplementary.
- Why-now: only run AFTER Anchor 1 PASSes. If Anchor 1 HARD-FAILs, skip Anchor 2 entirely.

### Anchor 3 (BACKLOG): CELL KP-K-EXTEND — does adding a 4th mechanism (P2 DRUM when ready, or P5 Curry-Howard) preserve ODK-CC?
- Anchor pointer: when P2 or P5 ships, re-run KP-COMPL with K=4. Measure whether the new mechanism adds a structurally distinct support OR collapses into an existing one.
- Substrate-product reading: tests scalability of ODK-CC architectural pattern — does it generalize to K > 3 or does the partition saturate?
- Tier hint: deferred until P2/P5 ships (DEPENDS_ON BATCH 17 ingest + Pi/Sigma per memory index).
- Why-now: backlog only; do not pick up until at least one of P2/P5 reaches HARD-PASS individually.

## Context pointers (file paths, not summaries)

- Research note (this drill): `d:/AI/hd-instrument/notes/research_DRILL_complementary_coverage_partitioning_formalization_INV2a_KP_architectural_extension_2026-06-13.md`
- INV-2a HARD-PASS verdict context: most recent INV-2a verdict file under `notes/` and `data/orchestrator_status_log.jsonl`
- KP P1+P4 prior HARD-PASS memory: `c:/Users/marsh/.claude/projects/d--AI/memory/substrate_CELL_KP_knowledge_promotion_operator_P1_P4_HARD_PASS_2_of_5_paths_multi_mechanism_validated_2026-06-13.md`
- 12th methodology rule (universal operators + field partition routing): `c:/Users/marsh/.claude/projects/d--AI/memory/substrate_methodology_rule_12th_universal_operators_field_specific_signal_extractors_first_class_field_partition_routing_H3_HYBRID_first_appearance_2026-06-13.md`
- Two-axes architecture (TOOLS vs MATERIALS): `c:/Users/marsh/.claude/projects/d--AI/memory/substrate_architecture_two_orthogonal_axes_epistemic_foundationality_vs_substrate_load_bearing_capability_primitive_USER_craftsman_distinction_13th_methodology_rule_candidate_2026-06-13.md`
- Partition-routing read-side analog (CELL SC HARD-PASS): `c:/Users/marsh/.claude/projects/d--AI/memory/substrate_CELL_SC_HARD_PASS_VSA_partition_routing_survives_10M_N_invariant_existential_validation_categorical_gap_widens_at_scale_2026-06-13.md`

## Contract

exp_dev:
- Pre-register exact HARD-PASS / HARD-FAIL thresholds before ship (R_union - R_max bands, L_ij bands, |Q| bands, CFD, joint entropy as ratio of marginals); the research note section (c) gives a starting set — exp_dev may tighten or widen with rationale.
- Smoke gate before full run (5-10 atoms per class).
- Ship via queue_add.sh after smoke PASS.
- REMOTE VERIFY post-ship per standing protocol.
- Self-test per `formula-selftests` skill — particularly Q-statistic sign convention (Q < 0 = complementary) and CFD definition (fraction with at-most-one failure, not at-least-one).
- Held-out test methodology per 11th methodology rule (USER-LOCKED): held-out atom set MUST be constructed AFTER mechanism shipment, not curated to be partition-favorable. Record construction protocol in pre-reg.

## Autonomy declaration

exp_dev owns: exact held-out atom selection protocol; codebook sample size; tier-filter cutoffs; mechanism invocation parameters; HP threshold tightening; smoke gate design; whether to add a 4th-mechanism placeholder run; reporting format. research authored the architectural framing and the formal characterizations; exp_dev authors the empirical shipment.
