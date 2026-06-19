# exp_dev hand-off — research: Kantorovich-functor categorical grounding for 3-mode distillation taxonomy

Filed-by: research (Opus) 2026-06-13
Trigger: research drill notes/research_DRILL_kantorovich_functor_framework_categorical_grounding_3_mode_distillation_taxonomy_audit_robust_claim_5_extension_2026-06-13.md
Pause state: respect data/orchestrator_paused.flag — if present, exp_dev should NOT pick these up until /orchestrator-resume-experiments is invoked.

Per [[feedback-no-experiment-design-in-prompts]]: this file contains anchor candidates and context pointers only. exp_dev owns experiment design, smoke gating, queue-shipping, and pre-reg envelope-fail-bands.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (highest priority, GATED on Cell SMA-1 HARD-PASS): Cell KFC-1
- **anchor pointer**: Kantorovich-Functor Compositionality test on substrate 12 archetype classes, 3-mode distillation taxonomy
- **substrate-product reading**: converts closed-loop step 3 from heuristic to architecturally typed; LLM categorical-gap canonical claim for claim 5 (closed-loop)
- **tier hint**: CPU-symbolic / pen-and-paper category-theory verification, no GPU; ~30-45 min compute, mostly analysis
- **why-now**: KP P3 SHARES_MATH HARD-PASS (332 canonical edges + 12 archetype classes) is the empirical input; closed-loop step 3 OPERATIONAL gives the distillation operator events; Cell SMA-1 HARD-PASS would confirm SHARES_MATH ~ is the kernel-of-behavioural-equivalence candidate, which is the precondition for KFC-1 to be well-posed
- **decisive thresholds** (see research note section c for full pre-reg): HARD-PASS requires >= 10/12 coequalizer fit for ATOM-REMOVING + >= 10/12 left-adjoint fit for STRUCTURE-ADDING + >= 8/12 restriction-idempotent fit for REFUSAL + >= 10/12 Kantorovich-distance monotone decrease

### Anchor 2 (after KFC-1 HARD-PASS): Cell CHTV-K
- **anchor pointer**: CHTV-1 enrichment with quantitative modalities; behavioural distance d(prover_state_n, prover_state_{n+1}) under Kantorovich extension on L6-PROOF FINDER runs
- **substrate-product reading**: converts CHTV-1 from binary verifier to quantitative verifier with continuous convergence metric; per-step prover-progress observability
- **tier hint**: small Python prototype + L6-PROOF FINDER re-run on existing 20-corpus, ~1-2 hr CPU
- **why-now**: CHTV-1 HARD-PASS + L6-PROOF FINDER HARD-PASS both shipped (substrate-CHTV1 + substrate-L6-PROOF-FINDER); existing 20-derivation corpus is reusable; KFC-1 HARD-PASS provides the predicate-lifting blueprint

### Anchor 3 (parallel to CHTV-K): Cell REF-RC
- **anchor pointer**: catalogue refusal events from closed-loop step 3 over a 1-cycle window; verify restriction-category idempotency + domain consistency
- **substrate-product reading**: closes the weakest leg of Kantorovich-functor extension (REFUSAL fit); empirical answer to "is refusal architectural or heuristic"
- **tier hint**: log-replay analysis, no compute; ~30 min
- **why-now**: closed-loop step 3 already emits refusal records; analysis is pure read-side

### Anchor 4 (scope-expansion, optional): Cell QENR-1
- **anchor pointer**: extend 3-axis architecture predicate-liftings to quantale-enriched logic following Kurz 2025; check if 3 axes factor as 3 independent quantale enrichments tensored
- **substrate-product reading**: would extend the 3-axis EMPIRICALLY ORTHOGONAL result with quantale-tensor categorical grounding
- **tier hint**: symbolic analysis + CPU experiments on 3-axis predicate-lifting evaluation, ~1-2 hr
- **why-now**: 3-axis architecture EMPIRICALLY ORTHOGONAL HARD-PASS (substrate_architecture_3_axis); CHTV-K HARD-PASS would provide the quantale-modality framework to extend

### Anchor 5 (deferred-large): Cell LEAN-KF
- **anchor pointer**: Lean 4 formalization of Kantorovich extension over Lawvere quantale + substrate predicate liftings
- **substrate-product reading**: machine-checked categorical grounding of claim 5 — major substrate-product positioning artifact
- **tier hint**: substantial (1-2 PhD-cycle equivalent); NOT a single-cycle experiment; flagged for substrate-product roadmap
- **why-now**: deferred; do not pick up in immediate cycles

---

## Context pointers (file paths, no summaries)

- d:/AI/hd-instrument/notes/research_DRILL_kantorovich_functor_framework_categorical_grounding_3_mode_distillation_taxonomy_audit_robust_claim_5_extension_2026-06-13.md (this drill's full pre-reg + falsifiable predictions)
- d:/AI/hd-instrument/notes/research_SUBSTRATE_SELF_IMPROVEMENT_LOOP_ARCHITECTURE_5_step_loop_3_mode_taxonomy_safety_guarantee_North_Star_metric_substrate_product_positioning_artifact_2026-06-13.md
- d:/AI/hd-instrument/notes/research_CYCLE_52_PLAN_v2_post_closed_loop_step_3_OPERATIONAL_3_mode_taxonomy_safety_guarantee_substrate_self_improvement_loop_architecture_integrated_2026-06-13.md
- Memory: substrate_CELL_KP_knowledge_promotion_operator_P1_P4_HARD_PASS_2_of_5_paths_multi_mechanism_validated_2026-06-13.md (KP P3 SHARES_MATH 332 canonical edges + 12 archetype classes)
- Memory: substrate_CHTV1_substrate_as_verifier_HARD_PASS_1p0_precision_LLM_categorical_gap_checkable_ground_truth_2026-06-12.md
- Memory: substrate_L6_PROOF_FINDER_HARD_PASS_20_20_SOUND_axiom_terminating_38pct_genuine_T1_62pct_authoring_gap_USER_goal_deduction_closed_2026-06-13.md
- Memory: substrate_architecture_3_axis_EMPIRICALLY_ORTHOGONAL_Cell_3_KP_P6_HARD_PASS_USER_craftsman_VERBATIM_corroborated_13th_rule_2nd_appearance_2026-06-13.md

---

## Contract

- exp_dev owns: experiment design, pre-reg envelope-fail-bands, smoke gate, queue_add.sh shipping, post-ship REMOTE VERIFY, self-test per formula-selftests.
- research owns (this file): anchor pointers + substrate-product readings + pre-reg thresholds for decisive tests (already in the research note, not re-stated here).
- Cell SMA-1 is the gate: if SMA-1 HARD-FAIL, Anchor 1 is not well-posed; revert to empirical-only framing for closed-loop step 3.

## Autonomy declaration

exp_dev may pick up any of Anchors 1-4 in priority order, subject to:
1. Pause-flag respect;
2. Cell SMA-1 result (gates Anchor 1; if HARD-FAIL, re-route to Strategy);
3. CPU-only budgeting — Anchors 1-3 are CPU/symbolic, Anchor 4 is small CPU; Anchor 5 is deferred.
exp_dev may re-order Anchors 2-4 based on queue health and substrate state at pickup time.

