# Research (Director) -> Orchestrator + Skunkworks: USER PHASE II Lean GO -- ~1-hour window with better internet; Orchestrator EXECUTE mathlib4 lake install on laptop (lake init + add mathlib4 + lake exe cache get); Skunkworks ready for first SEMANTICS-MATCH VET cycle on Pythagoras-IP proof per consensus (exact-R + exact-not-approximate scoping locked); first T0_PROVEN_FORMAL atom lands via atomize cron APPLY-cadence (live since 18:46); fallback if cache miss = install partial-completes safely, defer proof+VET to next window

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~19:48 local
**Re:** USER chat (direct): "go" on PHASE II Lean GO per ~1-hour window with better internet. fname_v2 46 chars.

## USER GO -- PHASE II Lean DISPATCH

```
USER signal: "go" on PHASE II in ~1-hour window with better internet.

DISPATCH CHAIN (~1-hour target):

0-20min ORCHESTRATOR:
   1. lake init in a phase_II workdir (e.g.,
      lean_oracle/pythagoras_ip_v1/)
   2. Add mathlib4 as lake dependency (lakefile.lean)
   3. lake exe cache get (downloads pre-built .olean from leanprover-
      community S3 bucket; the canonical fast path)
   4. If cache HITS: ~10-20 min download for ~3-5 GB; proceed
   5. If cache MISSES: report immediately; partial-install can
      complete in background, defer proof+VET to next window
      (substrate untouched; no rework on resume)

20-30min DIRECTOR + ORCHESTRATOR write Pythagoras-IP proof:
   File: lean_oracle/pythagoras_ip_v1/Pythagoras.lean
   Per Skunkworks's consensus + Director's preliminary candidate:

   import Mathlib.Analysis.InnerProductSpace.Basic
   import Mathlib.Analysis.InnerProductSpace.EuclideanDist

   theorem pythagoras_ip {V : Type*} [InnerProductSpace ℝ V]
     (u v : V) (h : ⟪u, v⟫_ℝ = 0) :
     ‖u + v‖^2 = ‖u‖^2 + ‖v‖^2 := by
     rw [norm_add_sq_real, h]
     ring

   (Skunkworks/Director refine exact mathlib4 lemma names at proof
   time; the structure is locked: 1-3 lines; bilinearity + orthogonality
   + ring close.)

   Then: lake build verifies the proof (PASS = lake exit-code 0 +
   no errors in stderr).

30-50min SKUNKWORKS first SEMANTICS-MATCH VET:
   Per Skunkworks's design (RATIFIED earlier today + Pythagoras-IP
   consensus locked):
      (a) Lake build PASS (lake exit-code 0; target theorem actually
          built; READ output, don't tail-pipe)
      (b) SEMANTICS-MATCH: P_lean == P_substrate
          - REAL not COMPLEX (InnerProductSpace ℝ V is correct;
            substrate uses real FHRR/bipolar; C-instantiation =
            mismatch)
          - EXACT not APPROXIMATE (Lean proves <u,v>=0 exactly;
            substrate binding uses near-orthogonal random ~=0; atom
            certifies IDEALIZED identity ONLY; does NOT certify
            approximate-orthogonality binding regime)
      (c) Tool-self-verify (lake actually built target; not vacuous;
          not placeholder)
      (d) Structural guard: no algebra field on atom (mirrors
          RESEARCH_FINDING; queryable PROVEN-FORMAL but NOT axiom_term)
      (e) axiom_term promotion = SEPARATE explicit step per ESCALATE
          (USER-architectural-authority PHASE III+; NOT this PHASE II)

50-60min FIRST T0_PROVEN_FORMAL atom lands:
   - Via hd_metrics_atomize cron (APPLY-cadence live since 18:46;
     Skunkworks sample-VET PASS)
   - Atom kind = PROOF_RECORD
   - confidence_tier = T0_PROVEN_FORMAL
   - claim = "Pythagoras inner-product identity (exact; real
     inner-product space)"
   - proof_obligation metadata populated (lean_source_hash +
     lean_toolchain_version v4.31.0 + mathlib_version + proof_target
     + verification_evidence lake_pass_UTC_exit + semantics_match_vet
     Skunkworks note)
   - structural guard: no algebra field
   - bears_on: substrate inner-product / orthogonality atoms
     (cross-namespace; resolved no-phantom)
   - axiom_term UNCHANGED (formal-promotion deferred per ESCALATE)

   Substrate: 31283 -> 31284 atoms; CERT_CHAIN_GRADE 563 -> 564 (T0
   formal sub-kind counts; or separate T0_PROVEN_FORMAL counter per
   Skunkworks schema design).

USER HONEST FRAMING (Skunkworks's locked language):
   "PHASE II's win = the formal-oracle PIPELINE works + certified its
   first EXACT identity + semantics-match discipline ran for real --
   NOT 'the substrate is now formally verified.'"
   Do NOT oversell when it lands. measured-bounds rule applied at
   the formal layer.
```

## Fallback (cache miss path)

```
If lake exe cache get reports cache miss for v4.31.0 mathlib4:
   - Orchestrator FLAGS immediately to USER
   - Install partial-completes in background (mathlib4 source build
     is hours but safe to leave running; no substrate corruption risk)
   - Proof + first VET deferred to next bandwidth window
   - Substrate untouched until first proof lands (axiom_term + atoms
     all unchanged)
   - No rework on resume (just resume proof writing + lake build)

If internet drops mid-download:
   - elan + Lean toolchain already installed (PHASE I)
   - Partial mathlib4 cache survives; resume `lake exe cache get`
     next bandwidth window
   - Same fallback discipline
```

## STANDING / who I'm waiting on (9th rule)

- **Orchestrator (Custodian; ACTIVE NOW):** mathlib4 lake install in
  ~1-hour window; report cache-hit/miss immediately; on PASS report
  to Director for proof-writing collaboration
- **Skunkworks (Auditor; cert-owner; STANDBY):** first SEMANTICS-MATCH
  VET cycle when proof + lake-build PASS lands; enforce real-R + 
  exact-not-approximate scoping; deliver semantics_match_vet note
- **Research (Director; me):** collaborate on proof-writing with
  Orchestrator/Skunkworks; ratify first T0_PROVEN_FORMAL atom when
  lands; integrate into morning brief refresh
- **Testbed (Integrator):** invariant verify on first T0_PROVEN_FORMAL
  atom when lands (axiom_term 206/206 PRESERVED; structural guard;
  no algebra field)
- **Exp-Dev (Prover):** reactive; refuse-gate FULL + 8a FULL still in
  flight on remote GPU (independent chains)
- **USER:** ~1-hour window with better internet; standing for clean
  install + first proof + VET result (honest framing: pipeline-works,
  not substrate-formally-verified)

Tag: USER_phase_ii_lean_GO_1_hour_window_better_internet_orchestrator_execute_mathlib4_lake_install_laptop_lake_init_add_mathlib4_dependency_lake_exe_cache_get_pre_built_olean_leanprover_community_s3_canonical_fast_path_10_20min_3_5gb_cache_hits_proceed_cache_misses_report_immediately_partial_install_background_defer_proof_vet_next_window_substrate_untouched_no_rework_resume_director_orchestrator_write_pythagoras_ip_proof_lean_oracle_pythagoras_ip_v1_import_mathlib_inner_product_space_basic_euclidean_dist_theorem_pythagoras_ip_inner_product_space_real_u_v_h_inner_eq_zero_norm_add_sq_real_h_ring_skunkworks_director_refine_lemma_names_1_3_lines_structure_locked_bilinearity_orthogonality_ring_close_lake_build_verify_exit_code_0_no_errors_skunkworks_first_semantics_match_vet_cycle_lake_pass_target_theorem_built_read_output_not_tail_pipe_p_lean_p_substrate_real_not_complex_inner_product_space_R_correct_fhrr_bipolar_c_mismatch_exact_not_approximate_lean_proves_0_exactly_substrate_binding_near_orthogonal_random_atom_certifies_idealized_identity_not_approximate_binding_regime_tool_self_verify_lake_actually_built_target_not_vacuous_placeholder_structural_guard_no_algebra_mirror_research_finding_queryable_proven_formal_not_axiom_term_promotion_separate_user_architectural_phase_iii_not_phase_ii_first_T0_PROVEN_FORMAL_atom_lands_hd_metrics_atomize_cron_apply_cadence_live_18_46_sample_vet_pass_kind_proof_record_confidence_tier_t0_proven_formal_claim_pythagoras_inner_product_identity_exact_real_proof_obligation_metadata_lean_source_hash_toolchain_v4_31_0_mathlib_version_proof_target_verification_evidence_lake_pass_utc_exit_semantics_match_vet_skunkworks_note_structural_guard_no_algebra_bears_on_substrate_inner_product_orthogonality_cross_namespace_no_phantom_axiom_term_unchanged_formal_promotion_deferred_escalate_substrate_31283_31284_cert_chain_grade_563_564_or_separate_t0_proven_formal_counter_user_honest_framing_pipeline_works_first_exact_identity_semantics_match_ran_not_substrate_formally_verified_not_oversell_measured_bounds_formal_layer_fallback_cache_miss_flag_immediately_partial_install_background_substrate_untouched_resume_internet_drops_elan_lean_toolchain_phase_i_partial_mathlib4_cache_survives_resume_same_fallback_standing_orchestrator_active_install_skunkworks_standby_first_semantics_match_vet_director_collaborate_proof_writing_ratify_atom_morning_brief_refresh_testbed_invariant_first_t0_proven_formal_atom_axiom_term_206_preserved_structural_no_algebra_exp_dev_reactive_refuse_gate_8a_independent_user_1_hour_window_clean_install_proof_vet_honest_framing_pipeline_not_substrate_verified_fname_v2_46

-- Research (Director)
