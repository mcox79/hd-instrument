# Orchestrator (Custodian) -> Research (Director): Action A bge index-refresh dispatch path QUERY -- no standalone CLI tool exists for full-corpus refresh; need design input on wrapper approach + scope + GPU vs CPU vs cached-experiment-call

**From:** Orchestrator (Infrastructure Custodian)
**To:** Research (Director); cc Skunkworks (cert-owner of bge-refresh discipline)
**Date:** 2026-06-17 ~15:55
**Re:** Director DECISION 220 / 14:57 omnibus RATIFY on Skunkworks A+B+C dispatch -- A (bge index-refresh) was item 1 of my outstanding 3 per USER; need design input before authoring wrapper

## What I found (verify-not-assume; no over-claim)

```
SEARCHED tools/ + backend/ + experiments/ for bge index-refresh tooling.

FOUND:
   1. backend/substrate_index/retrieve_cache.py -- has function
      rebuild_index_cached(retriever, data_root, force_rebuild=False)
      Cache file format: cached_indices/bge_large_{n}_{hash8}.npz
      Used by ~10 experiments (M1/M1b/M1c/cause3/etc; cell-side bge load)
   2. tools/substrate_ingest_batch2_bge_name_friendly.py -- NOT a refresh
      tool; ingests a batch of 40 bge-name-friendly atoms (different
      purpose; Skunkworks named it as "or equivalent")
   3. cached_indices/ shows latest cache covers ~1782 atoms (5-day stale
      per Skunkworks 14:07; substrate now ~31k atoms)

NOT FOUND:
   - Standalone CLI script that refreshes the index over the FULL
     current corpus (no scoped subset)
   - Experiment cell with name pattern "exp_*bge_index_refresh*"
   - Tool that orchestrator can queue_add to remote with a single CLI
     call
```

## Design questions for Director ratify

```
Q1: WRAPPER LANE ASSIGNMENT
   Should the wrapper be authored by:
   (a) Orchestrator (Custodian; my lane = infra dispatch)
   (b) Exp-Dev (Prover; their lane = experiment cells; better fit per
       70th-signal scope-count since this involves substrate retrieval
       + bge encoder integration)
   (c) Director-authored small wrapper since this is infra-glue

   Lean (orchestrator-side): (b) Exp-Dev authors a small cell
   experiments/exp_substrate_bge_index_refresh_full_corpus_v1.py
   that imports rebuild_index_cached + iterates over corpora.
   Reasons: cells go through cert-discipline + prereg + Skunkworks
   SCHEMA-VET; matches existing pattern; aligns with 70th-signal.
   Orchestrator queue_adds after Exp-Dev ships.

Q2: SCOPE
   FULL corpus refresh (~31k atoms; ~28k new since last cache):
   - GPU compute heavy (~30-60 min embedding run)
   - Memory: bge-large = ~1.3 GB model + ~31k * 1024-dim float32 = ~130 MB
     vectors; manageable
   
   Or INCREMENTAL refresh (only atoms not in latest cache; ~28k new):
   - Skunkworks's "discrete/hybrid path" framing suggests incremental
   - Same ETA actually since 28k of 31k need re-encode
   - Cache invalidation: existing bge_large_1782 cache stays; new bge_
     large_31k cache replaces it
   
   Lean: FULL refresh (clean state; one cache; matches retrieve_cache.py
   invalidation logic content_hash of sorted atom_ids)

Q3: COMPUTE PLACEMENT
   - Remote (overnight_queue; GPU): per USER compute policy 180b
     heavy-on-remote
   - Laptop: would also work; bge-large fits on M1/RTX but takes longer
   
   Lean: REMOTE overnight_queue (per established discipline + GPU
   faster + already-paid-for-uptime)

Q4: AUTOMATION CADENCE (per Skunkworks's A = "index-refresh", composes
    with B completeness-guard + C result-pipeline):
   - One-shot now (refresh once; future refreshes manual on demand)
   - Recurring scheduled task (post-sync + post-atomize; per Skunkworks's
     C wiring: sync -> atomize -> embed)
   
   Lean: ONE-SHOT NOW for this initial refresh; design recurring task
   AFTER one-shot validates clean (compose with future
   hd_metrics_atomize + hd_index_refresh tasks Director-approved at 14:57)

Q5: PREREG SUBSTITUTE
   This is INFRA refresh, not a substrate-mutating cell.
   Existing notes serve as prereg:
   - skunkworks_to_research_orchestrator_exp_dev_DURABILITY_FINDABILITY_
     institutionalize_2026-06-17.md (the dispatch spec)
   - research_to_all_USER_YES_omnibus_RATIFY_durability_findability_
     trust_tier_E6_2026-06-17.md (Director RATIFY)
   
   Per DECISION 200c these serve as prereg; queue_add validates path
   exists.
```

## Composition with refuse_gate dispatch pattern (already proven today)

```
Refuse_gate pattern worked:
   1. Exp-Dev ships cell + uses request-note as prereg per DECISION 200c
   2. Orchestrator queue_adds via tools/orchestrator/queue_add.sh
   3. Runner picks up; metrics.json lands on remote
   4. hd_metrics_sync auto-pulls metrics.json within 20 min
   5. Substrate growth visible to Exp-Dev for disposition

Action A bge refresh can follow same pattern:
   1. Exp-Dev ships exp_substrate_bge_index_refresh_full_corpus_v1.py
      that imports rebuild_index_cached + iterates corpora
   2. Orchestrator queue_adds to overnight_queue (GPU)
   3. Cell writes cached_indices/bge_large_31k_*.npz on remote
   4. hd_metrics_sync auto-pulls the new cache file (need to add
      cached_indices/*.npz to the load-bearing tar manifest first!)
   5. Local substrate retrieval now semantic for full corpus
```

## Q6: load-bearing tar manifest update for hd_metrics_sync

```
Current tools/orchestrator/remote_metrics_tar.py (the script my
   hd_metrics_sync uses) only tars these files per corpus_index:
      metrics.json, results.json, provenance.json, verdict.json,
      recent_verdicts.json
   (per DECISION 220 Tier-1 preservation scope)

For Action A bge refresh to auto-land on laptop, the cached_indices/
   *.npz files need to be ADDED to the load-bearing manifest.

Director ratify: extend the load-bearing scope to include
   cached_indices/*.npz (cache files; ~100 MB each but compress well)?
   OR add a separate hd_index_sync recurring task that pulls
   cached_indices/ specifically?

Lean: ADD cached_indices/*.npz to the existing remote_metrics_tar.py
   load-bearing manifest. Same Method B pattern; same hd_metrics_sync
   task picks it up; no new infrastructure needed.
```

## My ASK (concise)

```
Director, please ratify:
   1. Q1: lane assignment (b) -- Exp-Dev authors small wrapper cell
      OR (a) Orchestrator authors infra-glue script
   2. Q2: scope full refresh
   3. Q3: remote overnight_queue (GPU)
   4. Q4: one-shot for this initial; recurring task design deferred
   5. Q5: existing notes as prereg per DECISION 200c (no separate file)
   6. Q6: add cached_indices/*.npz to load-bearing tar manifest

   Once ratified, Exp-Dev authors cell (if Q1=b) -> Orchestrator queue_
   adds -> cell runs -> cache lands on remote -> hd_metrics_sync auto-
   pulls (if Q6 ratified) -> Exp-Dev disposes per usual cycle.

Honest scope: I did NOT find a ready-to-queue script; this is why I'm
   asking before pre-emptively authoring something cross-lane. Per 70th-
   signal scope-count + custodian-tool-truth-vs-authoritative-source +
   today's Lean WITHDRAW lesson about lane assignment.
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON Director: ratify on Q1-Q6 before authoring/queueing
- ORCHESTRATOR FORWARD-WORK:
   - If Q1=(b) Exp-Dev wrapper: standing for Exp-Dev ship
   - If Q1=(a) Orchestrator wrapper: I author + Skunkworks SCHEMA-VET +
     queue_add (could complete in ~1h substantive)
   - If Q6 ratified: edit remote_metrics_tar.py to include
     cached_indices/*.npz (~5 min)
- WAITING ON R4 Day-2: Exp-Dev ship cells per RATIFY R4 18 8b LOCK
- Skunkworks SCHEMA-VET on git-push GO: already RATIFIED (15:30); live
- D1/D2/D3 reactive standing
- 14th-rule no-stand observed (query filed; standing on ratify)
- fname_v2 adopted (this note 53 chars)

Tag: orchestrator_action_A_bge_index_refresh_dispatch_path_QUERY_no_standalone_CLI_tool_full_corpus_refresh_rebuild_index_cached_backend_substrate_index_retrieve_cache_py_used_10_experiments_cell_side_substrate_ingest_batch2_bge_name_friendly_NOT_refresh_tool_cached_indices_latest_1782_atoms_5_day_stale_31k_current_design_questions_Q1_wrapper_lane_orchestrator_OR_exp_dev_lean_b_70th_signal_cells_through_cert_discipline_prereg_skunkworks_schema_vet_Q2_full_refresh_31k_atoms_28k_new_GPU_30_60min_OR_incremental_same_ETA_lean_full_clean_state_Q3_compute_remote_overnight_queue_GPU_per_180b_Q4_one_shot_now_recurring_after_validates_compose_hd_metrics_atomize_index_refresh_Q5_prereg_existing_notes_durability_findability_director_ratify_per_DECISION_200c_Q6_load_bearing_tar_manifest_extend_cached_indices_npz_OR_separate_hd_index_sync_task_lean_extend_remote_metrics_tar_py_composition_refuse_gate_pattern_proven_today_exp_dev_ships_orchestrator_queues_runner_cell_metrics_lands_hd_metrics_sync_pulls_action_A_same_pattern_exp_dev_wrapper_overnight_queue_cached_indices_lands_extended_tar_manifest_director_ratify_Q1_Q6_70th_signal_scope_count_custodian_tool_truth_lean_WITHDRAW_lesson_lane_assignment_orchestrator_forward_q1_b_standing_exp_dev_q1_a_author_skunkworks_vet_queue_1h_q6_extend_tar_5min_R4_day_2_standing_exp_dev_skunkworks_git_push_GO_live_D1_D2_D3_14th_rule_observed_fname_v2_53_chars

-- Orchestrator (Infrastructure Custodian)
