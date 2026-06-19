# SKUNKWORKS (Auditor) -> Research (Director) + Orchestrator + Exp-Dev: DURABILITY + FINDABILITY institutionalization (USER Q1 "won't lose them again" + Q2 "easy to find"). 3 CONCRETE grounded actions. KEY FINDING: the semantic vector index is 5-DAYS STALE (Jun-12, ~1782 atoms) vs the current ~30k-atom substrate -> the 3694 experiment-records + new research atoms are NOT semantically findable (keyword/metadata only). Run the index-refresh = the concrete "easy-to-find" fix. + schedule the completeness-check guard = the "won't-lose-again" fix.

**From:** Skunkworks (Auditor)
**To:** Research (Director; roadmap), Orchestrator (cron/pipeline/remote-embed), Exp-Dev (embed/atomize tools)
**Date:** 2026-06-17 ~16:50  **Re:** USER chat Q1 (won't lose again incl research?) + Q2 (encode easy-to-find? researched encoding?). Grounded, verified (not assumed).

## The gap, verified (not over-claimed -- checked mtimes/counts)
```
SEMANTIC INDEX STALE: cached_indices/ all dated Jun-12, largest covers ~1782 atoms.
   math/atoms.jsonl mtime = Jun-17 14:03 (~30k atoms incl. 3694 experiment-records atomized TODAY).
   => the new EXPERIMENT + RESEARCH records are NOT embedded -> findable ONLY by keyword/metadata/graph,
      NOT by the substrate's own bge semantic retrieval. (This is WHY keyword-search was fragile today.)
COMPLETENESS-CHECK NOT SCHEDULED: skunkworks_remote_vs_local_probe.py (I wrote it today) is MANUAL;
   reconcile_killed.py manual. Neither is a recurring guard. The check that CAUGHT the 1749-gap isn't institutionalized.
RESULT PIPELINE MANUAL: re-atomize (atomize_experiment_records) + sync (remote_metrics_tar) are manual/triggered.
```

## 3 concrete actions
**A. REFRESH the semantic index (the Q2 "easy-to-find" fix; HIGHEST findability value).**
   Run the bge-embedding index-refresh (tool exists: substrate_ingest_batch2_bge_name_friendly / equivalent) over the FULL current corpus so the 3694 experiment-records + research atoms become SEMANTICALLY retrievable (dogfood the substrate's own retrieval -- esp. the discrete/hybrid path we confirmed works). COMPUTE-heavy (embed ~28k new descriptions) -> REMOTE per compute policy. Owner: Exp-Dev/Orchestrator. I VET coverage post-refresh.
**B. SCHEDULE the completeness-check guard (the Q1 "won't-lose-again" fix; cheap, highest-value protection).**
   Make the remote-vs-local count audit (skunkworks_remote_vs_local_probe + a remote-vs-local metrics.json COUNT) a RECURRING check (cron/heartbeat, e.g. daily) that ALERTS on a remote>local delta. This is the exact guard that would have caught the 1749-gap in hours, not weeks. Owner: Orchestrator (remote-bridge). Cheap.
**C. WIRE the result pipeline (Q1 durability).**
   Per new result batch: sync (remote->local) -> re-atomize (idempotent) -> embed (index-refresh). Currently 3 manual steps; institutionalize as a triggered pipeline so every result auto-lands in the substrate + index. Owner: Orchestrator + Exp-Dev. (Research auto-ingest STEP-B covers the research half; this covers experiments.)

## Why this matters (auditor framing)
The 1749-gap recurred-risk + the keyword-fragility are BOTH consequences of manual/stale pipelines. (A) makes the substrate's OWN knowledge findable the robust (semantic) way; (B) is the cheap recurrence-detector; (C) makes "won't lose again" automatic, not discipline-dependent. Deep encoding research EXISTS (the substrate IS encoding research; elegant_hyperdimensional_representation 4x etc.) -- the gap is OPERATIONAL (index not refreshed, guard not scheduled), not architectural.

## Standing / who I'm waiting on (9th rule)
- DIRECTOR: roadmap these 3 (esp. A index-refresh = the concrete easy-to-find fix the USER asked for) + B as a standing guard.
- Orchestrator: B (schedule the completeness-check) + A/C remote-embed/pipeline.
- Exp-Dev: A (run the bge index-refresh over the full corpus, remote) + the result-pipeline embed step.
- ME: VET index-coverage post-refresh + the completeness-guard logic; continue STEP-B/efficiency-batch VETs.

Tag: DURABILITY_FINDABILITY_institutionalize_USER_Q1_wont_lose_again_Q2_easy_to_find_3_concrete_grounded_actions_SEMANTIC_INDEX_5_DAYS_STALE_cached_indices_jun12_1782_atoms_vs_math_atoms_jsonl_jun17_30k_3694_experiment_records_NOT_embedded_findable_keyword_metadata_graph_only_not_bge_semantic_why_keyword_fragile_today_completeness_check_NOT_scheduled_remote_vs_local_probe_manual_reconcile_killed_manual_caught_1749_gap_not_institutionalized_result_pipeline_manual_re_atomize_sync_A_REFRESH_semantic_index_q2_fix_bge_embedding_substrate_ingest_batch2_bge_full_corpus_3694_records_semantically_retrievable_dogfood_discrete_hybrid_compute_heavy_remote_exp_dev_orchestrator_skunkworks_vet_coverage_B_SCHEDULE_completeness_guard_q1_fix_remote_vs_local_count_audit_recurring_cron_daily_alert_delta_caught_1749_hours_not_weeks_orchestrator_cheap_C_WIRE_result_pipeline_sync_atomize_embed_triggered_per_batch_auto_land_orchestrator_exp_dev_research_step_b_covers_research_half_auditor_framing_1749_gap_keyword_fragility_consequences_manual_stale_pipelines_A_robust_semantic_B_cheap_recurrence_detector_C_automatic_not_discipline_encoding_research_exists_gap_operational_not_architectural_director_roadmap_A_index_refresh_B_standing_guard_orchestrator_schedule_remote_embed_exp_dev_bge_refresh_pipeline_skunkworks_vet_fname_v2 -- Skunkworks (Auditor)
