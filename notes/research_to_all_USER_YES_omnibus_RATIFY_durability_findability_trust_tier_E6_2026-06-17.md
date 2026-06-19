# Research (Director) -> All sessions: USER "yes" omnibus RATIFY -- DURABILITY+FINDABILITY 3 actions GO + Trust-tier T0-T3 architecture APPROVED + E6 amendment v2 RATIFIED + Held-out-retrieval SUPERSEDED-by-findings + STEP-B scope Director-lean B; carryover 5 (Lean/TRACK D/ARM-3/TIER 4c) remain explicit USER signal

**From:** Research (DIRECTOR)
**Date:** 2026-06-17 ~17:10
**Re:** USER "yes" (chat) to my question on items 6-9 dispatch + STEP-B DRY-RUN CLEAN at 16:55. fname_v2 50 chars.

## RATIFY 1 -- DURABILITY+FINDABILITY 3 actions GO

```
Per Skunkworks 16:50 dispatch + Director ratify:

ACTION A: REFRESH SEMANTIC INDEX (Q2 "easy to find")
   - Run bge-embedding index-refresh over FULL current corpus (~30k atoms)
   - 3694 EXP records + research atoms become semantically retrievable
   - Dogfood the substrate's own retrieval
   - Owner: Exp-Dev + Orchestrator (REMOTE compute)
   - Compute: HEAVY (embed ~28k new descriptions)
   - Skunkworks VETs index-coverage post-refresh
   - Deploys when SSH stable (Orchestrator)

ACTION B: SCHEDULE COMPLETENESS-CHECK GUARD (Q1 "won't lose again")
   - Recurring (daily) remote-vs-local count audit
   - Alert on remote > local delta
   - Would have caught 1749-gap in hours not weeks
   - Owner: Orchestrator
   - Implementation: heartbeat_watchdog scheduled task backbone +
     per-15-min remote_vs_local count + alert via
     data/.completeness_alert flag + dashboard endpoint
   - Composes with 99th + 100th candidates
   - Pre-flight design DONE per Orchestrator 16:13
   - Deploys when SSH stable

ACTION C: WIRE RESULT PIPELINE (Q1 durability)
   - Per new result batch: sync (remote->local) -> re-atomize -> embed
   - Currently 3 manual steps
   - Institutionalize as triggered pipeline
   - Auto-lands every result in substrate + index
   - Owner: Orchestrator + Exp-Dev
   - Research auto-ingest STEP-B covers research half; this covers
     experiments
   - Deploys post-A+B foundation

Director RATIFY all 3 actions. Deployment order: B (cheap; deploy
   first when SSH stable) -> A (heavy compute; remote slot) -> C
   (pipeline wiring on A+B foundation).

Composes with USER's morning skepticism (the 1749-gap was the
   recurrence the guard would have caught).
```

## RATIFY 2 -- Trust-tier T0-T3 architecture APPROVED

```
USER "yes" confirms architectural approval (was implicitly OK'd via
   earlier "go" on research-onboarding; this is explicit ratify):

T0 PROVEN: cert-grade exp PASS (full-mode >=3 seeds); ONLY load-bearing;
   anchors capabilities; counts toward axiom_term; ~427 today
T1 TESTED_PARTIAL: smoke/MIDDLE experiments; NOT load-bearing
T2 RESEARCH_SUPPORTED: literature finding WITH citation; NOT load-bearing
T3 HYPOTHESIS: drill conjecture / cross-domain; NOT load-bearing

Structural guards (per Skunkworks STEP-A):
   - RESEARCH_FINDING atoms NO algebra field
   - Excluded from axiom_term automatically
   - Never current_best_solution unless cert-confirmed
   - Research-being-wrong is STRUCTURALLY SAFE

Promotion ONLY via proof:
   T3 hypothesis -> experiment -> cert-grade PASS -> T0 (confirmed_by link)
   HARD_FAIL -> REFUTED + KEEP as negative knowledge
   Skunkworks cert-owner authority on T0 promotions

Already in flight:
   - STEP-B atomizer built (Exp-Dev) per T0-T3 schema
   - Language packs T2 trust-tier (WordNet/ConceptNet structured;
     text8/enwik8 no-tier training data)
   - Skunkworks SCHEMA-VET pipeline

Director RATIFY T0-T3 as substrate-product architecture. USER
   architectural authority preserved per 18th-rule.
```

## RATIFY 3 -- E6 substrate_product_positioning amendment v2 RATIFIED

```
Director draft delivered earlier:
   notes/substrate_product_positioning_AMENDMENT_v2_DRAFT_2026-06-17.md

USER "yes" RATIFIES the amendment per architectural authority.

Director will UPDATE the canonical doc:
   notes/substrate_product_positioning_2026-06-16.md (current canonical)
   -> notes/substrate_product_positioning_2026-06-17.md (new canonical
      reflecting today's HEALED narrative)

KEY narrative updates from today:
   - Substrate state 30045 atoms / 6746 relations / cert-grade 562
     (15.2%; was 2.7% this morning = ~5.6x improvement)
   - 9 cert-grade KEEP (Skunkworks 9-KEEP enumeration CLEAN holds)
   - Drosophila RESCOPE UP (not over-claim; sparse capacity cert-real
     3-48x; specific MB-bigram config failed)
   - kappa_3 drift RESCOPE UP (cert-grade real multi-backbone
     Pythia + Llama; 22 HARD_PASS vs 17 HARD_FAIL; ratio 11-15.5x
     drift-separation)
   - ARCH-A localization + ARCH-B confirmation: LINEAR readout caps
     capacity; NONLINEAR readout (softmax/modern-Hopfield) LIFTS
     capacity completely (recall 1.0 to 16xN)
   - SQ2 K=12 cert-grade FLAGSHIP (restored from morning audit's
     false-negative)
   - 5/6 production modules GREEN exact-reproduction (V1)
   - Trust-tier T0-T3 architecture LOCKED
   - Research-onboarding load-bearing for char-LM viability
   - Methodology FROZEN at 24 PHASE-2 explicit expansion 24+8 = 32
     today (per Testbed health check; PHASE-2 ratified lane)

Director will update canonical doc as background work; standing
   reactive on next landings.
```

## RATIFY 4 -- Held-out-retrieval generalization track SUPERSEDED-BY-FINDINGS

```
Earlier (16:00) USER E4 item 14: held-out retrieval track decision
   pending ARCH-B verdict

ARCH-B verdict delivered: SPARSITY_NEUTRAL with readout-lever
   CONFIRMED (nonlinear readout LIFTS capacity completely; same lever
   addresses multiple weak-spot clusters per Skunkworks strategic
   synthesis)

Plus Skunkworks fuzzy-retrieval CORRECTION (filed earlier): residual
   issue is NL-parse not retrieval-generalization broadly

Director-lean DISPOSITION:
   Held-out-retrieval as separate dedicated track is SUPERSEDED by
   today's findings:
   - The strategic question (lift weak-spot clusters via nonlinear
     readout) is now empirically CONFIRMED via ARCH-B
   - The retrieval residual (per Skunkworks correction) is NL-parse
     specific, not retrieval-generalization broadly
   - The future Tier-6 char-LM (when language-corpus ready) is the
     natural test of whether nonlinear readout addresses LM-style
     fuzzy mapping

SKIP the dedicated held-out-retrieval track. Composes with:
   - Tier-6 char-LM (when language-corpus enables)
   - ARCH-B substrate-wide architectural-experiment direction
   - Research-onboarding atomizer (adds language data)

Director RATIFY: no separate held-out-retrieval R4. USER E4 item 14
   SUPERSEDED.
```

## DIRECTOR-LEAN ON STEP-B SCOPE (Exp-Dev's a/b/c question)

```
Exp-Dev DRY-RUN CLEAN at 16:55:
   - 4390 notes total / 3161 excluded (bus/spec/state)
   - 1229 candidates pass classification
   - 881 with finding-signal (what_found OR citations OR ranked_candidates)
   - 348 borderline (request-only notes without explicit finding signal)
   - T2: 669, T3: 560

Exp-Dev recommends Option B (881 finding-signal filter):
   - Higher precision/recall at deterministic+no-LLM
   - Drops borderline request notes
   - One-line code change

Director-lean: CONCUR on Option B per Exp-Dev recommendation.
   The structural guard (non-load-bearing T2/T3 + no algebra +
   excluded from axiom_term) means even Option A would be SAFE per
   USER "research can be wrong" architecture. But Option B improves
   precision without losing material findings; cleaner substrate.

Skunkworks owns cert-owner SCOPE RULING. Director defers final
   choice to Skunkworks per audit-discipline lane authority. If
   Skunkworks rules differently (A safer per structural guard +
   over-inclusion-is-queryable-context), Director will concur.

Skunkworks SCHEMA-VET on atom shape + T2-T3 rule + no-phantom +
   no-algebra on sample (data/atomize_research_findings_dryrun_sample.
   jsonl) standing.

On Skunkworks SCOPE RULING + SCHEMA-VET clean -> APPLY batched/gated
   -> per-batch VET -> Testbed invariant verify.
```

## 5 CARRYOVER ITEMS (Lean/TRACK D/ARM-3/TIER 4c/E6) -- explicit USER signal pending

```
USER "yes" was scoped to items 6-9 (DURABILITY+FINDABILITY + trust-tier
   + E6 + held-out-retrieval) per Director's enumeration.

The 5 carryover architectural items remain pending explicit USER signal:
   - Formal-oracle Lean procurement direction
   - 3 TRACK D design Qs (palette/tab/scope)
   - ARM-3 Option C
   - TIER 4c (alpha CONCUR'd; needs explicit confirm)
   - E6 v2 (RATIFIED per item 6-9 ratify above; carryover item
     coverage updated)

Director NOT auto-actioning these per 18th-rule USER architectural
   authority preservation. Will surface when USER signal comes OR
   when natural unblock window aligns.

Standing on these 4 (Lean + TRACK D + ARM-3 + TIER 4c).
```

## SUBSTRATE STATE (continuing)

```
atoms:               30045
relations:           6746
EXP_ atoms:          3695
CERT_CHAIN_GRADE:    562 (15.2%)
AUDIT_LESSON:        34 + 1 NEW (DEGENERATE-REGIME-NOT-REFUTATION
                          promoted per Skunkworks 17:00 harvest;
                          92 CONFIRMED + 11 candidates)
METHODOLOGY_RULE:    32 (24 FROZEN baseline + 8 PHASE-2 expansion;
                          per Testbed awareness)
axiom_term:          206/206 PRESERVED
cap_pres:            1.0 (modules 6/6 OK)

Tracks in flight: 7
   A ARCH-B DONE + VET PASS
   B Drift dive DONE + UPWARD CORRECTION
   C STEP-B atomizer DRY-RUN CLEAN; pending Skunkworks SCOPE + SCHEMA-VET -> APPLY
   D V1 last module + V2 pending Exp-Dev
   E Language packs WordNet LANDED; text8/enwik8 PENDING (SSH transient)
   F Efficiency-batch R4 prep pending preregs
   G NEW: DURABILITY+FINDABILITY 3 actions (A index + B guard + C pipeline)
        on Director RATIFY above; deploy when SSH stable
```

## STANDING / who I'm waiting on (9th rule)

- **Exp-Dev (Prover):** STEP-B APPLY on Skunkworks SCOPE+SCHEMA-VET +
  V1 last module re-run + Action A index-refresh planning (REMOTE
  on SSH-stable)
- **Skunkworks (Auditor; cert-owner):** STEP-B SCOPE-RULING (A/B/C) +
  SCHEMA-VET sample + per-batch VET on APPLY + Action A index-coverage
  VET post-refresh + Action B completeness-guard logic VET +
  efficiency-batch R4 SCHEMA-VETs when preregs land
- **Orchestrator (Custodian):** SSH recovery for text8/enwik8 +
  ConceptNet + Action B deployment + Action A remote-embed slot +
  Action C pipeline wiring
- **Testbed (Integrator):** standing for re-atomize invariant verify
  on STEP-B APPLY + any new RESEARCH_FINDING T2 atoms
- **Research (Director):** E6 canonical doc update (background work);
  reactive on landings; standing for USER continued guidance
- **USER:** 4 remaining carryover (Lean + TRACK D + ARM-3 + TIER 4c)
  pending explicit signal; substantive narrative landing across the
  7 tracks in next 1-4h

Tag: USER_yes_omnibus_RATIFY_items_6_7_8_9_durability_findability_3_actions_GO_action_A_refresh_semantic_index_bge_embedding_full_corpus_3694_exp_research_findable_dogfood_substrate_retrieval_remote_compute_exp_dev_orchestrator_action_B_schedule_completeness_check_guard_daily_remote_vs_local_count_audit_alert_delta_caught_1749_gap_hours_not_weeks_orchestrator_heartbeat_watchdog_backbone_15min_data_completeness_alert_dashboard_endpoint_action_C_wire_result_pipeline_sync_atomize_embed_triggered_per_batch_auto_land_orchestrator_exp_dev_research_step_b_research_half_deployment_order_B_cheap_first_A_heavy_remote_C_pipeline_compose_USER_morning_skepticism_1749_gap_trust_tier_T0_T3_architecture_APPROVED_T0_proven_cert_grade_full_3_seeds_load_bearing_axiom_term_427_T1_tested_partial_T2_research_supported_citation_T3_hypothesis_drill_conjecture_structural_guards_no_algebra_excluded_axiom_term_never_current_best_research_safe_promotion_proof_T3_experiment_cert_PASS_T0_confirmed_by_HARD_FAIL_REFUTED_KEEP_negative_knowledge_e6_substrate_product_positioning_amendment_v2_RATIFIED_director_update_canonical_doc_today_HEALED_narrative_30045_atoms_562_cert_15p2pct_5p6x_improvement_9_cert_grade_keep_drosophila_RESCOPE_UP_kappa_3_drift_RESCOPE_UP_cert_grade_multi_backbone_pythia_llama_15p5x_arch_a_localization_arch_b_confirmation_linear_caps_nonlinear_lifts_completely_sq2_k12_cert_flagship_5_of_6_production_modules_green_trust_tier_locked_research_onboarding_load_bearing_methodology_24_FROZEN_plus_8_PHASE_2_expansion_32_held_out_retrieval_SUPERSEDED_by_findings_arch_b_readout_lever_confirmed_fuzzy_retrieval_NL_parse_not_retrieval_broadly_tier_6_natural_test_research_onboarding_step_B_dry_run_clean_1229_candidates_881_finding_signal_filter_director_lean_option_B_skunkworks_cert_owner_scope_ruling_defers_per_audit_discipline_authority_5_carryover_remain_explicit_USER_lean_track_D_arm_3_tier_4c_substrate_30045_6746_562_206_206_methodology_32_audit_lesson_34_plus_1_new_degenerate_regime_92_confirmed_11_candidates_7_tracks_in_flight_fname_v2_50_chars

-- Research (Director)
