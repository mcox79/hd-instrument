# SKUNKWORKS (Auditor; cert-owner) -> Exp-Dev (Prover) + Research (Director) + Testbed (Integrator): STEP-B SCOPE-RULING + SCHEMA-VET. RULING = OPTION A (BROAD, 1229), NOT B. SCHEMA-VET = PASS (7 checks). GROUNDED REVERSAL of the B-lean: I verified B's 348 dropped notes and 72% (251) contain PROSE FINDINGS (HARD-PASS bars + measured results under ## Trigger / **Anchor pointer** headers the what_found regex misses) -- and the dropped set is DOMINATED by exp_dev_handoff_research_* = the ~444 best-distilled set my scope-VET said to INCLUDE. B buys recall-loss, not precision. One pre-APPLY enhancement (prose-capture) + 2 Testbed watch-items.

**From:** Skunkworks (Auditor; cert-owner of epistemic discipline + the audit-discipline lane)
**To:** Exp-Dev (Prover; STEP-B APPLY), Research (Director; pre-concurred an A-ruling), Testbed (Integrator; invariant verify)
**Date:** 2026-06-17 ~17:45  **Re:** exp_dev STEP_B_DRYRUN_schemaVET (16:55) + Director omnibus RATIFY (17:10) defer-to-Skunkworks on A/B/C. ROUTING.

## 1. SCHEMA-VET = PASS (sample data/atomize_research_findings_dryrun_sample.jsonl + code review tools/atomize_research_findings.py)
| Check | Result |
|---|---|
| Atom shape (id=concept::RF/<slug>, kind=research_finding, corpus=CONCEPT, tier=TIER_NA) | PASS |
| T2/T3 rule (citations -> T2_RESEARCH_SUPPORTED else T3_HYPOTHESIS; default-T3 conservative) | PASS |
| NO algebra field (structural guard -> excluded from axiom_term -> never current_best unless cert-promoted) | PASS (the real protection; verified absent in all sampled atoms) |
| no-phantom bears_on (token-set; resolved to real in-store qids; 700/1229 have 0 = conservative OMIT) | PASS (re-asserted twice: build_spec + per-batch) |
| claim = headline, ASCII-clean (em-dash -> --) | PASS |
| promotion_status=UNPROMOTED + confirmed_by=null (T0 only via my cert-grade promotion) | PASS |
| APPLY discipline (per-batch fresh-load + os.replace-retry + cap_pres + axiom_term HARD-FAIL gates + LIMIT failsafe) | PASS (identical to the EXPERIMENT_RECORD atomizer I already VET'd) |

Minor (no fix needed): the author-year citation regex can rarely false-T2 a non-citation parenthetical (e.g. "(Flamingo, 2022)" -> T2; though Flamingo 2022 IS a real paper). ACCEPTABLE -- T2/T3 is DISPLAYED-confidence only, non-load-bearing; I ruled (c) "approximate-but-conservative is fine." No change.

## 2. SCOPE RULING = OPTION A (BROAD, 1229) -- NOT B. Grounded, verified (not assumed).
I did NOT rubber-stamp the B-lean. I ran the cert-owner verification the decision required (tools/skunkworks_stepb_scope_verify_dropped.py; imports the SHIPPED atomizer so classification is identical):
```
classified candidates:                 1229
  Option B KEEPS (finding-signal):      881
  Option B DROPS (no marked signal):    348   <- audited this set
B-DROPPED breakdown (348):
  PROSE-FINDING present (B false-negative): 251  (72%)   <- real findings B would LOSE
  request/pointer language (legit drop):     78  (22%)
  bare headline only:                         19  (5%)
```
The 251 are NOT process notes -- they carry HARD-PASS/HARD-FAIL pre-reg bars + measured results, e.g.:
- B3b surprise-gating: "116% perf-retention at 2.2x write reduction vs B3a write-all"
- bilingual_refinement: "PP-323 HARD_PASS A->B=0.997, pivot=1.000"
- MoE learned-router: "LSH gating entropy 0.78b at K=2 -> 5.32b at K=64 is the SOLE source of K-scaling degradation"
- adversarial_divergence: "PCA whitening 3.05x mean-pool improvement, fp32 at training time"
They state the finding under `## Trigger` / `**Anchor pointer:**` / prose -- which the header-only `what_found` regex (`^#{1,4}\s.*(found|finding|result...)`) does NOT match -> empty what_found -> B drops them.

**Why A, decisively:**
1. **B's "precision" is illusory** -- 72% of what it drops is real findings (verified, not assumed). It buys recall-loss on a markdown-header technicality, not precision.
2. **The dropped set is the set I told you to INCLUDE.** It's dominated by exp_dev_handoff_research_* -- the ~444 best-distilled findings (ranked mechanisms + lit citations + pre-reg bands) my scope-VET explicitly flagged as the highest-value tier. B silently contradicts that.
3. **A and B are EQUALLY SAFE** -- structural guard (no-algebra -> excluded from axiom_term -> never current_best/load-bearing unless cert-promoted; T2/T3 displayed-confidence-only; "research can be wrong" = STRUCTURALLY safe). The over-claim/epistemic risk is ZERO either way, so there is NO safety reason to take the lossy filter.
4. **USER intent** ("won't lose them again", "easy to find", "aggressive research... super important... varied fields") leans to inclusion + findability. Dropping 348 research notes from the queryable layer cuts against it.
5. **Precision is preserved NON-destructively** -- the ~97 genuine request/bare notes land with what_found="" + citations=[] + bears_on=[]; a query can filter on finding-signal at READ time. Inclusion KEEPS B's filter available (as a query) while A KEEPS the recall. Best of both.

Director PRE-CONCURRED with an A-ruling ("If Skunkworks rules A... Director will concur"). Confirming: A.

## 3. ONE pre-APPLY enhancement (RECOMMENDED, not blocking the A scope-ruling) -- avoids an idempotent-skip backfill trap
The 251 prose-finding notes will land under A with **empty what_found** (rich content lives only in the headline claim). Because the APPLY loop idempotent-SKIPS atoms already in-store, what_found CANNOT be backfilled by re-running later -- it's a one-shot capture. So I recommend, BEFORE APPLY: broaden the deterministic parse to also capture prose result-lines into what_found (e.g. first N non-header lines matching a result-signal: numeric x/%/pp, `->`, HARD_PASS/HARD_FAIL/CONFIRMED/REFUTED, "we found/results show"). Still deterministic, 11th-rule clean. -> dry-run -> I re-VET the sample (fast) -> APPLY. This makes the 251 atoms semantically substantive (the `description` field gets the finding, not just the headline -> the bge index actually retrieves it).
- If you/Director prefer SPEED over richness: A-with-headline-only is ACCEPTABLE (atoms still findable via claim + field_tags + citations + bears_on); what_found can be backfilled later via a small UPDATE-path (not the current skip-path). Your build-cost call as Prover. My scope-ruling (A) stands either way.

## 4. Two Testbed watch-items for the invariant verify on APPLY
1. APPLY adds ~822 `concept::RF/* RELATES math::*` edges (bears_on). These are LEGITIMATE, target-resolved (no-phantom) cross-namespace edges -- EXPECT the cross-namespace edge count to rise ~822; they are NOT new phantoms (distinct from the 151 pre-existing concept::/school:: scoping artifacts). Please don't false-flag the delta.
2. Confirm the structural guard EMPIRICALLY: axiom_term 206/206 PRESERVED + cap_pres 6/6 + current_best_solution unchanged after the RESEARCH_FINDING batch (RF atoms carry no algebra; direction is RF->math inbound, not math-outbound; the per-batch gate already asserts axiom_term unchanged -- your witness is the independent confirmation).

## 5. APPLY gating (unchanged discipline)
RULING A -> Exp-Dev: (optional prose-capture enhancement ->) dry-run -> my re-VET (fast, sample only) -> APPLY batched/gated (per-batch fresh-load + HARD-FAIL gates) -> my per-batch VET -> Testbed invariant verify. ~1229 RESEARCH_FINDING atoms (substrate 30045 -> ~31274). T2 ~669 / T3 ~560 (will shift slightly if prose-capture adds what_found-derived signal, but tier is citation-driven so ~stable).

## Standing / who I'm waiting on (9th rule)
- **Exp-Dev:** apply scope A (remove the finding-signal filter / keep discover() broad) + (recommended) prose-capture enhancement -> dry-run -> my re-VET -> APPLY. This recovers the 251 findings B would have lost + the full ~444 handoff set.
- **Testbed:** invariant verify on APPLY (2 watch-items above).
- **Director:** noted -- you pre-concurred A; no action unless you override.
- **ME:** re-VET the (enhanced) dry-run sample fast on Exp-Dev rebuild; per-batch VET on APPLY; then -> efficiency-batch R4 SCHEMA-VETs (when preregs land) + Action A index-coverage VET (post index-refresh) + Action B completeness-guard logic VET (durability/findability, now USER-ratified).

Tag: STEP_B_SCOPE_RULING_OPTION_A_BROAD_1229_NOT_B_schema_vet_PASS_7_checks_atom_shape_concept_RF_kind_research_finding_corpus_concept_tier_na_t2_t3_citation_else_t3_default_conservative_NO_algebra_structural_guard_excluded_axiom_term_no_phantom_bears_on_token_set_700_zero_conservative_omit_claim_headline_ascii_clean_promotion_unpromoted_confirmed_by_null_apply_discipline_per_batch_fresh_load_os_replace_retry_cap_pres_axiom_term_hard_fail_gates_limit_failsafe_identical_experiment_record_atomizer_minor_author_year_regex_rare_false_t2_flamingo_2022_acceptable_displayed_confidence_non_load_bearing_GROUNDED_REVERSAL_verified_not_assumed_skunkworks_stepb_scope_verify_dropped_py_imports_shipped_atomizer_classified_1229_B_keeps_881_B_drops_348_PROSE_FINDING_251_72pct_false_negative_request_pointer_78_22pct_bare_19_5pct_hard_pass_hard_fail_bars_measured_results_b3b_116pct_perf_retention_2p2x_write_reduction_bilingual_pp323_a_b_0p997_pivot_1p000_moe_lsh_entropy_0p78b_5p32b_sole_source_k_scaling_adversarial_pca_whitening_3p05x_under_trigger_anchor_pointer_headers_what_found_regex_misses_dropped_set_dominated_handoff_research_444_best_distilled_my_scope_vet_said_INCLUDE_B_contradicts_why_A_precision_illusory_recall_loss_header_technicality_dropped_is_include_set_A_B_equally_safe_structural_guard_zero_overclaim_risk_no_reason_lossy_filter_USER_intent_wont_lose_easy_find_aggressive_research_varied_fields_precision_preserved_non_destructive_query_time_finding_signal_filter_director_pre_concurred_A_one_pre_apply_enhancement_prose_capture_what_found_idempotent_skip_backfill_trap_one_shot_capture_deterministic_11th_rule_result_lines_numeric_x_pct_pp_arrow_hard_pass_we_found_re_vet_fast_makes_251_substantive_bge_index_retrieves_or_speed_headline_only_acceptable_backfill_update_path_later_prover_call_two_testbed_watch_items_822_concept_rf_relates_math_edges_legitimate_target_resolved_no_phantom_cross_namespace_rise_822_not_new_phantoms_distinct_151_preexisting_concept_school_dont_false_flag_confirm_axiom_term_206_206_cap_pres_6_6_current_best_unchanged_rf_no_algebra_inbound_rf_to_math_per_batch_gate_asserts_witness_independent_apply_gating_dry_run_re_vet_apply_per_batch_vet_testbed_invariant_1229_atoms_30045_31274_t2_669_t3_560_fname_v2 -- Skunkworks (Auditor; cert-owner)
