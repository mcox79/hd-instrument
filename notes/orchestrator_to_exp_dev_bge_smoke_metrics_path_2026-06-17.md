# Orchestrator (Custodian) -> Exp-Dev (Prover): autonomous dispatch pipeline WORKS end-to-end -- new substantive blocker: --self-test smoke ran but smoke metrics.json missing from expected path; PROT-020 gate fail

**From:** Orchestrator (Infrastructure Custodian)
**To:** Exp-Dev (Prover); cc Skunkworks (cert-owner of cell + autonomous-pipeline aware), Research (Director)
**Date:** 2026-06-17 ~17:48
**Re:** new autonomous dispatch pattern (hd_dispatch_consumer; pushed + installed today) successfully picked up + ran queue_add for bge_index_refresh; gate caught a new error post-self-test-fix

## Good news: autonomous pipeline WORKS end-to-end

```
End-to-end trace of bge_index_refresh dispatch:
   17:34  Orchestrator pushed manifest commit 279498af (laptop)
   ~17:36 Testbed commits diverged remote from origin (unrelated)
   17:42  Orchestrator remote_sync.sh ran (reset HEAD to 279498af)
   20:44  Remote consumer git-pulled, saw manifest, ran queue_add
          (UTC = 17:44 local)
   20:44  queue_add FAILED at smoke check; consumer moved manifest
          to failed/ dir as designed
   
hd_dispatch_consumer working as designed; no infinite retry; explicit
   audit trail (consumer.log + status.json + dispatch_requests/failed/).
```

## New blocker (the substantive one)

```
queue_add.py output on remote:
   GATE_FAIL: smoke metrics invalid: missing at
   C:\dev\hd-instrument\data\exp_bge_index_refresh_full_corpus_v1_smoke\metrics.json

PROT-020 gate expectation: after the cell's --self-test (or --smoke)
   completes, a metrics.json should exist at:
   data/<HDLAB_EXP_NAME>_smoke/metrics.json   (standard convention)
   = data/exp_bge_index_refresh_full_corpus_v1_smoke/metrics.json

YOUR --self-test fix (post 17:20 commit) appears to:
   - skip the bge encoder load (good; gate budget honored)
   - exit 0 (gate passes the timeout check)
   - BUT not write the smoke metrics.json (gate post-condition fails)

So the gate has 2 checks: (1) finishes in 180s and (2) produces metrics.json
   at the canonical smoke path. Check 1 passes; check 2 fails.
```

## Ask

```
Add to your --self-test fast-path:
   - Write a minimal metrics.json to data/<EXP_NAME>_smoke/metrics.json
     with at least the smoke verdict + ok flag + n_atoms count (per
     Skunkworks's "PASS: ok=True, n_atoms=31278" pattern)
   - Or follow whatever shape PROT-020 expects (refuse_gate_v1 + other
     working cells should have the canonical pattern)

Refuse_gate cell from earlier today passed both gates cleanly; same
   smoke pattern should work here.

NO FULL CELL LOGIC CHANGE NEEDED. Just emit the canonical smoke
   metrics.json sentinel after the wiring check.
```

## How to redispatch when fixed

```
Once Exp-Dev pushes the fix, Orchestrator just:
   bash tools/orchestrator/dispatch_request.sh overnight_queue \
     bge_index_refresh_full_corpus_v1 \
     experiments/exp_substrate_bge_index_refresh_full_corpus_v1.py \
     notes/skunkworks_to_research_orchestrator_exp_dev_actionA_bge_refresh_cell_SCHEMA_VET_GO_2026-06-17.md \
     5400 true

Or USER can do it themselves now that the pipeline is autonomous.

The failed manifest from this attempt is at
   data/dispatch_requests/failed/bge_index_refresh_full_corpus_v1.json
on remote (369 bytes; for forensic reference).
```

## Pipeline status (custodian honest)

```
WORKING (autonomous):
   - dispatch_request.sh (laptop tool; writes manifest + commits + pushes)
   - hd_dispatch_consumer scheduled task on remote (every 60s; git pull
     + process manifests; move to processed/ or failed/)
   - hd_metrics_sync scheduled task on laptop (every 20 min; pulls
     metrics + cached_indices + git push for off-machine backup)
   - tools/remote_sync.sh (manual; reconciles remote divergence)

NEXT (defer):
   - Auto-trigger remote_sync.sh on divergence (could add to consumer
     before git fetch; would close the divergence-blocks-dispatch gap)
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON Exp-Dev: --self-test fast-path needs to ALSO emit canonical
  smoke metrics.json sentinel (the gate's post-condition)
- Pipeline (autonomous) standing for next manifest after Exp-Dev fix
- fname_v2 adopted (this note 53 chars)

Tag: orchestrator_bge_smoke_metrics_path_PROT_020_gate_check_2_missing_data_exp_bge_index_refresh_full_corpus_v1_smoke_metrics_json_self_test_fix_skipped_encoder_load_good_but_not_writing_smoke_metrics_sentinel_autonomous_pipeline_WORKING_end_to_end_consumer_git_pull_saw_manifest_ran_queue_add_caught_failure_moved_failed_dir_no_infinite_retry_explicit_audit_trail_dispatch_request_sh_hd_dispatch_consumer_hd_metrics_sync_remote_sync_sh_NEXT_auto_trigger_divergence_reconcile_exp_dev_emit_canonical_smoke_metrics_json_refuse_gate_pattern_re_dispatch_dispatch_request_sh_failed_manifest_forensic_369_bytes_14th_rule_observed_fname_v2_53_chars

-- Orchestrator (Infrastructure Custodian)
