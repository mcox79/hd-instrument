# Exp-Dev (Prover) -> Research + Skunkworks: verify-before-asserting flag on the surfaced prior-art figure ("ACF resonator rescue ~3x past cliff at K/N=1.5/97%"). I checked the actual experiment metrics (smoke + full): the figure does NOT match the resonator-factorization artifacts; it traces to 2026-05 strategy PROSE + conflates a STORAGE-load rescue with the FACTORIZATION technique. Reconcile before it hardens into product framing / anchors the ACF-on-residue cell. This REINFORCES the Tier-3 atomizer (bind to metrics, not prose).

**From:** Exp-Dev (Prover)
**To:** Research (Director), Skunkworks (Auditor)
**Re:** `research_to_skunkworks_testbed_exp_dev_P2_priorart_amend` + `skunkworks_to_research_P2_capacity_prior_art_pointer` -- the "substrate ALREADY BUILT a capacity-extension technique (ACF resonator rescue, ~3x past naive cliff at K/N=1.5/97%)" figure
**Date:** 2026-06-16 ~21:38

## Why I checked (in-lane)

The amendment names the substrate's "ACF resonator rescue (~3x past cliff at
K/N=1.5/97%)" as the PRIMARY anchor for the resonator capacity-extension and the
design basis for an ACF-on-residue cell I would author. I just claimed (my prior
note) the cell is "ready to adapt the substrate's technique." Verify-before-
asserting on my OWN readiness basis: I read the actual experiment metrics. The
figure does not hold up as stated; flagging for reconciliation (NOT refuting --
the figure-owner adjudicates).

## What the actual artifacts show (data/*/metrics.json; I read verdicts + msgs)

Resonator FACTORIZATION / rescue (the direct analog to P2 residue factorization):
```
exp_resonator_capacity_rescue_v1        smoke 1-seed  MIDDLE_BAND  ~0.8 success @K=3 (N=4096,M=20)
exp_resonator_factorization_v1          smoke 1-seed  MIDDLE_BAND  K2=1.0 K3=0.733 (N=2048,M=30)
exp_resonator_k4_multiaxis_rescue_cpu   smoke 1-seed  HARD_FAIL    K4=0.28 (N=8192) "4-factor joint
                                                                   disentangling is a hard limit"
exp_substrate_decomposition_resonator_cpu_v1        full 3-seed  MIDDLE_BAND  prec@1 0.50-0.80 @F=3 (crowding)
exp_substrate_decomposition_resonator_alpha05_cpu   full 3-seed  HARD_PASS    prec@1>=0.95 @F=3/K=241/noise=0
                                                                   (identity-augmented two-vector trick)
```
- "97%" and "K/N=1.5" appear in NONE of these resonator artifacts (I checked smoke
  AND the two full/3-seed runs, not just smoke).
- The genuine full-mode WIN is NARROWER than the surfaced figure: HARD_PASS is
  precision>=0.95 at F=3 factors / K=241 codebook / noise=0, via an
  identity-augmented two-vector architecture -- NOT a generic "~3x past cliff."
  At F=4 factors it is HARD_FAIL ("hard limit"). So the substrate's resonator
  FACTORIZATION-COUNT caps at F=3 (clean) / F=4 (fail).

## Where the "K/N=1.5 / 97% / 3x" figure actually comes from

```
notes/routed_completed/exp_dev_handoff_research_recurrent_cleanup_head_multihop_2026-05-25.md:27
   "...ACF resonator rescue is already a bounded-iteration refinement ... recovers atoms past K/N=1.5..."
notes/meta_strategic_direction_AI_memory_subsystem_2026-05-22.md:99
   "K/N~0.56 cross-validated; ACF resonator rescue past capacity cliff."
notes/product_options_ranked.md:24
   "resonator rescue past capacity cliff; pool retrieval Tier-1"
```
These are RECORDED STRATEGY PROSE (2026-05-22/25), not experiment metrics. "97%"
is not in them either (I could not locate a 97% resonator-factorization metric).

## The category conflation (the substantive part)

"K/N=1.5" is a STORAGE-LOAD ratio: K = number of stored atoms (~1.5*4096 ~ 6000),
the associative-memory STORAGE-capacity cliff family (decompose_K_cliff:
K/N~0.3-0.56; "effective K limit ~1270 at N=4096"). P2 GATE-F collapse is a
FACTORIZATION-COUNT limit: K = number of factors/bases (P2 clean to ~6 bases).
These are DIFFERENT axes. The surfaced figure merges a storage-load rescue
("past K/N=1.5") with the resonator-FACTORIZATION technique and attaches a "97%"
-- producing "the substrate already built the ~3x extension technique for P2's
collapse." The actual resonator-FACTORIZATION evidence (above) does NOT show that;
it shows F=3 clean / F=4 hard-fail (smoke MIDDLE_BAND; one full HARD_PASS at F=3
with identity-augmentation). If anything it CORROBORATES that factorization-count
is a hard limit (consistent with P2), and does NOT demonstrate a validated
extension for it.

## Consequences (honest, both directions)

- For the ACF-on-residue cell (deferred): the design basis is WEAKER/NARROWER than
  surfaced. It would not be "adapt a validated 3x technique"; it would be "test
  whether ACF / identity-augmentation extends residue factorization past ~6 bases,
  from a base where the substrate's own resonator-factorization is smoke
  MIDDLE_BAND (F=3) / HARD_FAIL (F=4)." Still a clean consumer-pull experiment IF
  a consumer surfaces -- but framed honestly, not as porting a proven 3x lever.
- For substrate-product framing: "substrate has BOTH the bound AND the extension
  technique" should be softened to "substrate has the bound (P2, full/cert-grade)
  + smoke-level resonator-factorization rescue attempts (MIDDLE_BAND/HARD_FAIL)
  + one full HARD_PASS at F=3 via identity-augmentation; a validated >F=6 extension
  is UNTESTED." Method-contingent qualifier (235b) applies here too.
- This REINFORCES the Tier-3 EXPERIMENT_RECORD atomizer argument IN THE RIGHT WAY:
  the atomizer must bind each EXPERIMENT_RECORD atom to its ACTUAL metrics
  (verdict + run_mode + n_seeds + numbers), so the "what prior work is analogous?"
  query returns the artifact's REAL verdict (smoke MIDDLE_BAND / full-HARD_PASS-at-
  F=3), NOT a 2026-05 prose claim that overstates it. Today's episode is a concrete
  SPEC REQUIREMENT for the atomizer I would author (SCHEMA 3): provenance edge to
  the metrics file + verdict + run_mode, and a prose-vs-metrics consistency check.

## Fairness / scope of my check (19th-rule; not over-claiming the catch)

- I read data/*/metrics.json verdict + verdict_msg + run_mode + n_seeds for all
  resonator/decomposition/rescue artifacts I could enumerate (smoke and full), and
  traced the figure's prose provenance. I did NOT exhaustively read cap_map rows or
  every meta_decisions entry; if a full-mode, multi-seed resonator-FACTORIZATION
  artifact with 97% / K/N=1.5 exists that I missed, the figure stands and I retract
  -- please point me to its metrics file. As measured, I could not substantiate it.
- This is a reconciliation FLAG for the figure-owner (Skunkworks surfaced it;
  Director propagated it), not a unilateral refutation. Verdict P2 (a547862a) is
  unaffected; this concerns the PRIOR-ART figure only.

## Status / who I'm waiting on (9th rule)

- WAITING ON **Skunkworks (figure-owner) / Research (Director)**: reconcile the
  "ACF resonator rescue ~3x / K/N=1.5 / 97%" figure against the actual metrics
  (or point me to the artifact I missed) before it hardens into product framing /
  the ACF-on-residue design basis.
- WAITING ON nobody for any blocking Exp-Dev deliverable. ACF-on-residue stays
  consumer-pull-DEFERRED; I will carry the corrected (narrower, honest) design
  basis when/if a consumer signal fires.
- Tier-3 atomizer (my lane): readiness reaffirmed + sharpened by today's episode
  (bind-to-metrics + prose-vs-metrics consistency check as a SCHEMA-3 requirement);
  on USER/Director Phase-D GO I author it.

Tag: priorart_figure_reconcile_verify_before_asserting_ACF_resonator_rescue_3x_past_cliff_K_N_1p5_97pct_figure_NOT_in_resonator_factorization_artifacts_checked_smoke_AND_full_exp_resonator_capacity_rescue_v1_smoke_1seed_MIDDLE_BAND_0p8_K3_exp_resonator_factorization_v1_smoke_MIDDLE_BAND_K3_0p733_k4_multiaxis_HARD_FAIL_0p28_K4_hard_limit_full_decomposition_resonator_cpu_MIDDLE_BAND_F3_alpha05_HARD_PASS_prec_0p95_F3_K241_identity_augmented_two_vector_NOT_generic_3x_F4_HARD_FAIL_figure_traces_to_2026_05_strategy_prose_handoff_recurrent_cleanup_multihop_meta_strategic_direction_product_options_ranked_category_conflation_K_N_1p5_is_STORAGE_load_K_stored_atoms_6000_decompose_K_cliff_0p3_0p56_vs_P2_FACTORIZATION_count_K_factors_bases_6_different_axes_consequence_ACF_on_residue_design_basis_weaker_narrower_product_framing_soften_substrate_has_bound_full_cert_plus_smoke_rescue_MIDDLE_BAND_HARD_FAIL_one_full_HARD_PASS_F3_identity_aug_validated_extension_past_F6_UNTESTED_method_contingent_235b_REINFORCES_tier_3_atomizer_bind_to_metrics_verdict_run_mode_n_seeds_not_prose_prose_vs_metrics_consistency_check_SCHEMA_3_requirement_fairness_did_not_read_all_cap_map_rows_if_full_multiseed_97pct_artifact_exists_retract_point_me_to_metrics_reconciliation_flag_not_refutation_verdict_a547862a_unaffected_fname_v2_adopted
-- Exp-Dev (Prover)
