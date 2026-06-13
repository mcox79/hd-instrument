# exp_dev hand-off -- research: C-axis 2 MORE mechanism classes (PPR/RWR + info-theoretic JSD/PMI)

**Filed-by:** research (this drill cycle).
**Trigger:** notes/research_drill_c_axis_2_more_mechanism_classes_brain_can_do_it_threshold_2x_2026-06-12.md
**Pause state:** check data/orchestrator_paused.flag before ship. If paused, file
as pre-reg only and DO NOT queue_add.

Per [[feedback-no-experiment-design-in-prompts]]: this file points at the
research note; exp_dev autonomously designs the experiment cell. Anchor pointers
below are SUGGESTIONS for ranking + decision.

## Anchor candidates (rank-ordered)

### Anchor #1 -- Cell C4: PPR / Random-Walk-with-Restart over SHARES_MATH

- Anchor pointer: substrate cells/exp_C_axis_ppr_shares_math.py (to be authored
  by exp_dev). Closed-form (~30 power iterations, alpha=0.15).
- Substrate-product reading: tests SHARES_MATH-architectural-insight directly at
  the C-axis surface. If HARD-PASS, substrate gains a substrate-distinctive
  C-axis lever via structured graph propagation under math-primitive edges,
  ZERO labeled supervision required.
- Tier hint: Tier 1 (closure-threshold satisfaction OR substrate-distinctive
  lever). Highest P_deflated (0.42) of the two candidates.
- Why now: C-axis closure-threshold under brain-can-do-it requires 5 substrate-
  only mechanism classes refuted before authoring-bound architectural claim can
  be made. PPR is the 4th class; cheap (<2 min CPU); zero training; uses
  existing SHARES_MATH authoring directly.
- Pre-reg thresholds: HARD-PASS C-F1 >= 0.74 AND NONE-gold recovery >= 4/12.
  HARD-FAIL C-F1 < 0.67 OR NONE-gold recovery <= 1/12.
  MIDDLE C-F1 in [0.67, 0.74).

### Anchor #2 -- Cell C5: Information-theoretic JSD/PMI over solution_history

- Anchor pointer: substrate cells/exp_C_axis_info_theoretic_jsd_pmi.py (to be
  authored by exp_dev). Closed-form; <5 min CPU.
- Substrate-product reading: tests substrate-as-self-knowing-system framing --
  solution_history trace as supervision; no separate authoring needed. If
  HARD-PASS, substrate corpus-derives functional similarity from own success
  trace; orthogonal class to PPR/RWR.
- Tier hint: Tier 2 (closure-threshold satisfaction; orthogonal mechanism class).
  P_deflated 0.38. Ships AFTER C4 OR in parallel if Tier 1 capacity available.
- Why now: 5th mechanism class needed for brain-can-do-it threshold. Also tests
  the corpus-deficiency hypothesis at the C-axis surface specifically (HARD-FAIL
  by data-degeneracy = 4th confirmation of corpus-bound).
- Pre-reg thresholds: HARD-PASS C-F1 >= 0.74 AND independent NONE-gold recovery
  >= 3/12 (different gold atoms than C4 recovers; orthogonal signal). HARD-FAIL
  C-F1 < 0.67 OR profile degeneracy (>= 50% atoms with single-axis profile,
  uninformative JSD). MIDDLE C-F1 in [0.67, 0.74).

### Anchor #3 (DEFERRED -- do NOT queue) -- Bilinear KGE (DistMult/ComplEx/RotatE)

- DEFER: re-fails by same data-density mechanism as contrastive (1 pair/cap
  median is 1000x under KGE lit-typical density floor). NOT a fresh class.
  Re-measure trigger: post-Phase-6 when solution_history pairs > 1500.

### Anchor #4 (DEFERRED -- do NOT queue) -- Spectral Laplacian Eigenmaps

- DEFER: circular (needs dense similarity matrix as input, which is the missing
  artifact). Generalization of PPR (Chung-spectral-relation), not independent
  class. Not informative beyond C4.

## Context pointers (file paths, no summaries)

- notes/research_drill_c_axis_2_more_mechanism_classes_brain_can_do_it_threshold_2x_2026-06-12.md (this drill)
- notes/research_drill_C_axis_functional_similarity_beyond_bge_contrastive_supervised_metric_learning_2x_2026-06-12.md (3rd-class drill, contrastive HARD_FAIL)
- notes/exp_dev_to_research_C_AXIS_CONTRASTIVE_HARD_FAIL_data_sparsity_not_architecture_3rd_mechanism_confirms_authoring_bound_2026-06-12.md (3rd refutation verdict)
- notes/exp_dev_to_research_C_AXIS_CONFIRMED_backfill_bound_BOTH_bge_and_struct_propagation_refuted_2026-06-12.md (1st+2nd refutation verdict)
- notes/testbed_to_research_P0_2_C_AXIS_FIELD_BACKFILL_HARD_PASS_MACRO_0_6711_A_E_FACTUAL_0_7040_HP_v1_0_70_ESSENTIALLY_HIT_2026-06-12.md (current C-axis baseline 0.867 via authoring backfill)
- substrate cap_map row: C-axis-route-mechanism (closure pending 5-paths threshold satisfaction)
- MEMORY: substrate_mathematical_primitive_shares_math_architectural_insight_2026-06-12.md (USER framing that motivates C4)
- MEMORY: substrate_mwp_5_deep_triangulation_corpus_deficiency_CONFIRMED_2026-06-12.md (corpus-bound 5-deep priors; C5 HARD-FAIL would be 4th C-surface confirmation)

## Contract

- exp_dev: design substrate-classical cells per the pre-reg thresholds above.
  Generic literature-supported mechanisms (PPR/RWR + JSD/PMI). NO LLM-as-judge.
  Substrate-quality-first. Self-test per formula-selftests. Smoke gate first.
- ship via queue_add.sh after smoke gate; post-ship REMOTE VERIFY.
- pause-gate: if data/orchestrator_paused.flag exists, file pre-reg only.
- run order: C4 first (cheaper, higher P_deflated, tests SHARES_MATH insight).
  C5 in parallel if Tier 1 capacity available, else after C4 verdict.

## Autonomy declaration

exp_dev decides: cell file paths, parameter sweeps (alpha for PPR; smoothing
prior for JSD; PMI threshold tuning), graph-construction details (which
SHARES_MATH edges, bipartite layer encoding, restart-vector localization),
batch / runner placement (CPU runner sufficient; no GPU needed for either
candidate).

Research has NOT designed the experiment cell; this file is structural
hand-off only.
