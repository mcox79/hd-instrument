# Research (Director) -> USER: SUBSTANTIVE UPDATE -- (1) 7th self-cert gate PHANTOM-DEP LIVE (engine 6 -> 7 gates LIVE; commit 450c7a03 by Skunkworks; 53/53 self-test; non-retroactive VERIFIED; CERT 569 unchanged); directly enforces 0-phantom for FrameNet + deeper-ingest pre-ingest cert-gate. (2) Capability-map MISLABEL CATCH (verify-the-referent applied to every sub-count): `positives_by_verdict` actually summed to 569 not 433 -- data correct but key name over-claimed; renamed to `cert_by_verdict` honestly; corpus_total staleness also fixed. (3) Items 2+3 scaffold refinements absorbed (FrameNet ID-collision-only + DEFER FE atoms to v2; deeper-ingest LEXICON-tier + pre-reg DIRECTION-as-hypothesis-not-threshold). Substrate state: atoms 41330 / CERT 569 honest / engine 7 LIVE.

**From:** Research (Director); USER-routed
**To:** USER
**Date:** 2026-06-18 ~16:30 PDT
**Re:** Substantive update -- 7th gate LIVE + cap-map mislabel + scaffold refinements. fname_v2.

## 7th self-cert gate LIVE -- PHANTOM-DEP

Skunkworks built + landed the 7th gate from Item 1 of the joint initiatives (the top-recommendation PHANTOM-DEP from my audit-catalog survey):

```
Gate: PHANTOM-DEPENDENCY
Encodes: audit lessons #2 + #4 (CONFIRMED 3+4 witnesses; "don't fabricate grounding"
         + "phantom-dep pre-ratify check")
Mechanism: producer phantom_dep_self_check + consumer phantom_dep_violation; placed
           BEFORE the CERT grant so a phantom DEPENDS_ON/COMPOSES/STRENGTHENS
           lineage edge pre-empts cert even when verdict + method-gate + gate0
           all pass
Severity: would-be-cert + is_phantom_free=False -> UNVERIFIED
  (distinct from 5th gate path-provenance which is HARD_FAIL; reasoning-path
   hallucination makes RESULT false, lineage phantom makes PROVENANCE unverifiable)
Non-retroactive VERIFIED: grep of data/ for phantom_dep_self_check = 0 occurrences
  -> 0 atoms can be re-tiered -> CERT 569 UNCHANGED
Self-test: 53/53 PASS (was 41 for gates 3-6; +12 for 7th)
Commit: 450c7a03 (push routed to Orchestrator)
Substrate-autonomy: gates 3+4+5+6+7 ALL bootstrapped from TODAY's catches
```

**Directly serves Items 2+3**: this gate is the deterministic enforcement of the "0-phantom verified post-ingest" pre-ingest cert-condition for BOTH FrameNet + deeper-ingest ingests. When those cells declare typed edges, 7th gate auto-enforces at atomize-time.

## Capability-map MISLABEL caught (verify-the-referent on every sub-count working)

Skunkworks's verify-the-referent on every sub-count of the capability-map atom (the discipline she institutionalized after my morning scour-script bug):

```
CATCH (sub-field mislabel):
  Field positives_by_verdict ACTUALLY summed to 569 (full-CERT distribution
  including MIDDLE_BAND 69 + HARD_FAIL 63 + NON_TEST 1 + SPARSITY_NEUTRAL 2 +
  HONEST_BOUNDED 1) -- NOT 433 positives as the key name implied.
  
  Data: CORRECT (the inventory was honest in headline numbers)
  Key name: OVER-CLAIMED (a reader would mis-read HARD_FAIL 63 as "positives")
  
  Fix: rename positives_by_verdict -> cert_by_verdict (accurate label for full-
       CERT distribution; headline 569 stays exact)
  
  Plus: corpus_total_atoms_at_scour was stale at 41324 (Store now 41330; the +6
        atoms are non-cert post-scour). Fix: live-count at scour time.

CERT 569 EXACT (unchanged); inventory accurate on every load-bearing number;
the rename + corpus-total refresh are precision/honesty fixes -- exactly the
class verify-the-referent exists to catch.
```

Both fixed + committed (50c18c46; scour tool now live-counts corpus_total + uses honest key name).

## Items 2+3 scaffold refinements (cert-honesty absorbed)

```
FRAMENET (Item 2):
  REFINEMENT A: cross-corpus check = "0 ID-COLLISION" only (namespaced
                linguistics:: distinct from LEXICON IDs). Lemma-REFERENCE
                overlap is EXPECTED (it's the SemLink-style cross-resource
                bridge), NOT a collision -- don't false-flag.
  REFINEMENT B: DEFER ~10,503 FRAME_ELEMENT atoms to v2. v1 lean scope:
                ~1,221 frames + 8 first-class rel_types + ~13,572 LU edges.
                (FE atoms add complexity + don't substantially advance the
                orthogonal-composition demo with WordNet.)

DEEPER-INGEST (Item 3):
  REFINEMENT A: new synsets -> LEXICON tier (consistent with Bucket B1; raw
                WordNet entries are SAME provenance, NOT distilled claims --
                don't use RESEARCH_FINDING tier for raw ontology atoms).
  REFINEMENT B: pre-reg DIRECTION (denser -> higher 3-hop recall) IS the
                hypothesis; thresholds (+15 / +5 absolute at 20% coverage)
                are LOOSE cross-method lit-anchors NOT BFS-validated cuts.
                Why: PullNet is a learned-reader RETENTION study; ours is a
                deterministic-BFS DENSIFICATION. Two transfer gaps (learned
                vs deterministic; removal vs addition). The DIRECTION is
                pre-registered + sacrosanct; magnitudes are honest-loose.
```

## Substrate state

```
atoms                41330
CERT_CHAIN_GRADE     569 (honest; engine 7 enforces)
PROOF_RECORD         5
MEASURED_MECHANISM   3
methodology_rule     46+ (PHANTOM-DEP rule landing)
audit_lesson         49
self-cert engine     7 GATES LIVE (gate0 + discrimination + working-baseline-cliff
                      + corpus-completeness + multi-hop-provenance + verdict-mappable
                      + phantom-dep)
capability_map       1 LIVE (renamed cert_by_verdict + corpus_total refreshed)
axiom_term           206/206 PRESERVED
cap_pres             6/6 PRESERVED
```

## Still pending (your decisions)

```
1. FrameNet ARC-3 sign-off (filed 14:00; Skunkworks cert-conditions confirmed
   with the 2 refinements; v1 scope leaner per Skunkworks DEFER-FE)
2. T3 deeper-ingest GO/HOLD/REFRAME (filed 15:10 + addendum + Skunkworks
   cert-conditions confirmed with LEXICON-tier + direction-as-hypothesis)
```

## Standing

- ME: cap-map fixes applied + Items 2+3 refinements absorbed + Director ACK to Skunkworks forthcoming. Reactive on USER decisions + A2-v6 verdict + Skunkworks check-in #11 (~16:25).
- ALL: substrate-discipline-running-fast pattern produced 7 gates LIVE in one session day (started session at 1 gate); FOUR of them bootstrapped from TODAY's own catches -- the substrate-autonomy directive realized at multiple distinct layers.

Tag: user_substantive_update_7th_gate_live_cap_map_mislabel_scaffolds_refined_phantom_dep_engine_6_7_450c7a03_skunkworks_53_53_self_test_non_retroactive_verified_cert_569_unchanged_0_phantom_pre_ingest_framenet_deeper_audit_2_4_confirmed_3_4_witnesses_producer_phantom_dep_self_check_consumer_violation_before_cert_pre_empts_lineage_unverified_distinct_5th_path_hard_fail_reasoning_false_lineage_provenance_unverifiable_grep_0_occurrences_53_pass_41_5_6_12_7th_commit_orchestrator_substrate_autonomy_gates_3_4_5_6_7_today_catches_serves_2_3_deterministic_enforcement_0_phantom_pre_ingest_atomize_time_cap_map_mislabel_verify_referent_every_sub_count_morning_scour_bug_lesson_positives_by_verdict_569_full_cert_middle_band_69_hard_fail_63_non_test_1_sparsity_2_honest_bounded_1_not_433_data_correct_key_over_claim_hard_fail_63_positives_rename_cert_by_verdict_accurate_full_cert_headline_exact_corpus_total_stale_41324_41330_6_atoms_non_cert_live_count_scour_cert_569_exact_unchanged_inventory_accurate_load_bearing_rename_refresh_precision_honesty_verify_referent_50c18c46_live_count_honest_key_items_2_3_refinements_framenet_a_cross_corpus_id_collision_only_linguistics_lexicon_distinct_lemma_reference_overlap_expected_semlink_bridge_not_collision_false_flag_b_defer_10503_frame_element_v2_lean_1221_frames_8_rel_13572_lu_complexity_orthogonal_composition_deeper_ingest_a_new_synsets_lexicon_tier_bucket_b1_consistency_raw_wordnet_provenance_not_distilled_research_finding_raw_ontology_b_pre_reg_direction_denser_higher_3_hop_hypothesis_thresholds_15_5_absolute_20_loose_cross_method_lit_anchors_not_bfs_validated_pullnet_learned_reader_retention_deterministic_bfs_densification_two_transfer_gaps_learned_deterministic_removal_addition_direction_sacrosanct_magnitudes_honest_loose_substrate_atoms_41330_cert_569_engine_7_proof_5_measured_3_methodology_46_phantom_dep_audit_49_capability_map_1_renamed_corpus_refreshed_axiom_cap_pres_pending_framenet_sign_off_skunkworks_confirmed_2_refinements_v1_leaner_defer_fe_t3_go_hold_reframe_addendum_lexicon_direction_standing_cap_map_fixes_2_3_refinements_director_ack_reactive_user_a2_v6_check_in_11_1625_substrate_discipline_running_fast_7_gates_one_session_4_today_catches_substrate_autonomy_directive_multiple_fname_v2_50

-- Research (Director); USER-routed
