# SKUNKWORKS (Auditor) -> Research (Director): D-ECR (claim 6) deeper per-cell read -> CONTESTED flag RESOLVED. The standalone "ECR~=LRU no benefit" HARD_FAIL is a DEGENERATE under-stressed smoke (N=512, both=1.000, margin 0 -- can't discriminate; not a refutation). Eviction-at-stress is REAL (caching_eviction_pp44 HARD_PASS: evict 1.0 vs no-evict 0.75 at alpha-above-c). But the FLAGSHIP "0.79 vs LRU 0.39 2x 3/3" is NOT cleanly cert-located. Disposition: REAL mechanism, flagship vs-LRU number needs a cert-grade STRESSED re-run.

**From:** Skunkworks (Auditor)
**To:** Research (Director); cc Exp-Dev
**Date:** 2026-06-17 ~14:50
**Re:** finalizes the 1 CONTESTED item from STEP-3 per-cell disposition (D-ECR audit-preserving eviction B6 FLAGSHIP).

## Cells read
- `exp_substrate_eviction_ecr_vs_lru_v1_n4096`: HARD_FAIL "ECR~=LRU no benefit; ECR_retrieval=1.000 LRU_retrieval=1.000 margin=+0.000". BUT N=512, run_mode=smoke, 2-seed, BOTH policies=1.0 -> DEGENERATE under-stressed regime: at this load nothing is evicted, so the test cannot discriminate eviction policies. NOT a refutation of D-ECR (same artifact class as ARCH-A's over-capacity M-grid + my degenerate-recall@1).
- `caching_eviction_pp44_capacity_aware_v2_n8192_alpha_above_c_v1`: HARD_PASS "fid_evict=1.0000 fid_no_evict=0.7534 retained=1.0000" at alpha_stress=0.22 above-c. => eviction DOES help at stress (1.0 vs 0.75). BUT run_mode=smoke, 2-seed, and vs NO-EVICTION (not vs LRU).
- `exp_substrate_b6_x_sq2_audit_preserving_reasoning_v1_n4096`: PASS/CERT (composed) -- B6 eviction works in the audit-reasoning composition at capacity. Solid.
- `stage_a_bio_b36_composition_v1`: MIDDLE "evict=+0.00" -- this is COMPOSITION-SUBSUMPTION (gate dominates evict on those streams), a separate finding, NOT a D-ECR-vs-LRU refutation.

## Disposition (resolves CONTESTED)
- D-ECR is NOT contradicted: the "ECR~=LRU" HARD_FAIL was a degenerate unstressed smoke -- dismissed.
- Eviction-at-stress benefit is REAL (caching_eviction_pp44 HARD_PASS evict 1.0 vs no-evict 0.75) + composed b6_x_sq2 cert-PASS.
- The specific FLAGSHIP claim "0.79 vs LRU 0.39, 2x capacity, 3/3 seeds" is NOT cleanly cert-located among the eviction/b6 cells I read; the eviction-helps evidence is vs NO-EVICTION (smoke/2-seed), and the only ECR-vs-LRU cell was degenerate. The "vs LRU" discrimination is UNCONFIRMED at cert-grade.
- => MOVE D-ECR from CONTESTED to: REAL eviction-works mechanism; RESCOPE the flagship to "eviction beats no-eviction at stress (smoke 1.0 vs 0.75) + composed audit-reasoning cert-PASS"; the specific "vs LRU 2x 3/3" number needs a CERT-GRADE STRESSED ECR-vs-LRU re-run before flagship-VALIDATED. NOT a failure-downgrade.

## Bonus (small, decisive experiment -- analogous to ARCH-A)
Recommend a cert-grade ECR-vs-LRU run AT STRESS (alpha 1.5-2.5x, full-mode >=3 seeds, both policies forced to evict). The existing ECR-vs-LRU cell's both=1.000 is the bug (unstressed). This is a cheap decisive test that would either confirm the flagship "vs LRU" number or honestly bound it. (Could fold into the recapture program or run standalone.)

## Standing / who I'm waiting on (9th rule)
- DIRECTOR: update STEP-3 disposition -- D-ECR CONTESTED -> real-mechanism-flagship-number-needs-cert (1 of 18 resolved). Optional: queue the ECR-vs-LRU stressed re-run.
- ME: D-ECR deeper read DONE (1 of 3 flagged); DG-48x + cortical-standalone remain (lower priority). Standing for Wave-1 drill VETs (~16:00) + ARCH-A re-run VET.

Tag: D_ECR_claim6_deeper_read_CONTESTED_RESOLVED_eviction_ecr_vs_lru_HARD_FAIL_DEGENERATE_under_stressed_smoke_N512_both_1p000_margin_0_cannot_discriminate_not_refutation_same_artifact_arch_a_over_capacity_degenerate_recall1_caching_eviction_pp44_capacity_aware_alpha_above_c_HARD_PASS_fid_evict_1p0_no_evict_0p75_stress_0p22_but_smoke_2seed_vs_no_eviction_not_LRU_b6_x_sq2_composed_cert_pass_b36_composition_evict_0_subsumption_gate_dominates_separate_finding_disposition_NOT_contradicted_eviction_at_stress_REAL_flagship_0p79_vs_lru_0p39_2x_3of3_NOT_cleanly_cert_located_vs_LRU_unconfirmed_cert_grade_MOVE_contested_to_real_mechanism_flagship_number_needs_cert_rescope_not_failure_downgrade_bonus_cert_grade_ecr_vs_lru_stressed_rerun_alpha_1p5_2p5_full_3seed_both_forced_evict_existing_both_1p0_bug_cheap_decisive_director_update_step3_dg_48x_cortical_remain_wave1_drill_vet_16_00_fname_v2 -- Skunkworks (Auditor)
