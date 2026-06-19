# exp_dev hand-off -- research: SHARES_MATH amortization depth-amplification

Filed-by: research (Opus, drill cycle 2026-06-13)
Trigger: notes/research_DRILL_SHARES_MATH_amortization_depth_amplification_quantification_substrate_product_canonical_claim_extension_2026-06-13.md (HEADLINE: 6 lit-scan + bisimulation-up-to-congruence + congruence-closure complexity converge on 1.5x-3x depth-amplification estimate)

Pause state: check data/orchestrator_paused.flag before ship. If paused, file as anchor candidate ONLY (no queue add).

Per [[feedback-no-experiment-design-in-prompts]]: anchor pointers + substrate-product reading + tier hint only. exp_dev is autonomous on cell design.

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP -- CPU only, ~30-60 min): Cell SMA-1 -- SHARES_MATH-aware L6-PROOF FINDER

- **Anchor pointer**: extend tools/orchestrator/... or hdlab/... L6-PROOF backward-chaining traversal to admit SHARES_MATH edges as 1-step rewrites within each archetype class (12 classes per KP P3 HARD_PASS 2026-06-13)
- **Substrate-product reading**: HARD-PASS lifts canonical claim from "substrate sound at depth N where LLMs hallucinate" to "substrate sound at effective depth N+k (k~=2-4) where LLMs hallucinate" -- direct quantitative differentiator
- **Tier hint**: T0-T1 substrate-load-bearing operator extension; T2 archetype-class partition as first-class field router (composes with 12th methodology rule)
- **Why now**: KP P3 HARD_PASS just shipped 332 canonical edges; L6-PROOF FINDER is operational; lit-scan gives defensible 1.5x-3x depth-amplification anchor; CPU-only so fits emergency-refill cycles; soundness self-check via CHTV-1 verifier already operational
- **HARD-PASS** (pre-registered): median proof depth >= 6 on held-out post-BATCH-18 goals AND 0 false-accepts AND wallclock-ratio < 3x vanilla L6-PROOF
- **HARD-FAIL** (pre-registered): depth <= 4.1 unchanged OR any false-accept OR wallclock-ratio > 10x
- **MIDDLE-BAND**: 4.1-5.9 depth, soundness preserved -- file Cell SMA-2 to widen archetype-class equivalence definition

### Anchor 2 (FALLBACK if Cell SMA-1 closes): Cell SMA-2 -- finer-grained SHARES_MATH partition

- **Anchor pointer**: re-run KP P3-style coalgebraic-bisimulation extraction at finer granularity (target ~24 archetype classes vs current 12) and re-run Cell SMA-1 with finer partition
- **Substrate-product reading**: tests whether the depth-amplification ceiling is partition-granularity-bound
- **Why now**: only relevant if Cell SMA-1 MIDDLE-BANDs

### Anchor 3 (DEFER): held-out goal authoring at depth 7+

- **Anchor pointer**: author ~20 goals at depth 7+ to extend benchmark range; requires BATCH 17-18 ingest fully landed
- **Why now**: only relevant if Cell SMA-1 HARD-PASSes; extends claim space to depth-10+ regime

## Context pointers (file paths, not summaries)

- notes/research_DRILL_SHARES_MATH_amortization_depth_amplification_quantification_substrate_product_canonical_claim_extension_2026-06-13.md (this drill)
- C:\Users\marsh\.claude\projects\d--AI\memory\substrate_L6_PROOF_FINDER_HARD_PASS_20_20_SOUND_axiom_terminating_38pct_genuine_T1_62pct_authoring_gap_USER_goal_deduction_closed_2026-06-13.md
- C:\Users\marsh\.claude\projects\d--AI\memory\substrate_CHTV1_substrate_as_verifier_HARD_PASS_1p0_precision_LLM_categorical_gap_checkable_ground_truth_2026-06-12.md
- C:\Users\marsh\.claude\projects\d--AI\memory\substrate_CH_P6_LLM_soundness_gap_capstone_HARD_PASS_substrate_0_false_accepts_vs_Qwen_3_of_12_hallucinated_PROVER_NARRATIVE_COMPLETE_2026-06-13.md
- C:\Users\marsh\.claude\projects\d--AI\memory\substrate_mathematical_primitive_shares_math_architectural_insight_2026-06-12.md
- C:\Users\marsh\.claude\projects\d--AI\memory\substrate_CELL_KP_knowledge_promotion_operator_P1_P4_HARD_PASS_2_of_5_paths_multi_mechanism_validated_2026-06-13.md
- C:\Users\marsh\.claude\projects\d--AI\memory\substrate_methodology_rule_verify_before_asserting_5_class_cluster_cycle_51_F4_CH_P6_P4_smoke_GHRR_all_caught_before_report_2026-06-13.md
- C:\Users\marsh\.claude\projects\d--AI\memory\feedback_held_out_test_methodology_required_for_macro_F1_claims_USER_LOCKED_11th_methodology_rule_2026-06-13.md (11th rule -- mandatory held-out goal corpus authored AFTER BATCH 18)

## Contract

- Pre-reg per envelope-fail-bands (HARD-PASS / HARD-FAIL / MIDDLE-BAND as above; no post-hoc relaxation).
- Smoke gate before full run.
- Ship via queue_add.sh (CPU local) IF not paused; else file as candidate.
- Post-ship REMOTE VERIFY (CHTV-1 verifier on every produced proof).
- Self-test per formula-selftests rule (must include false-accept-injection test BEFORE ship).
- Honor 11th methodology rule: held-out goals authored AFTER BATCH 18 land, NOT reused from the 20-goal HARD_PASS corpus.

## Autonomy declaration

exp_dev is autonomous on:
- partition definition (12 archetype classes vs finer; default to 12 per KP P3)
- traversal admission policy (intra-archetype-class only vs cross-class; default intra-only for soundness safety)
- wallclock-ratio measurement methodology
- self-test injection design

Research note authoring is complete; exp_dev does cell design.
