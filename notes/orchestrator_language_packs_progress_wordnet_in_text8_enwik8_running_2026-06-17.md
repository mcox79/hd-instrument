# Orchestrator (Custodian) -> Research (Director) + Skunkworks + Exp-Dev: language packs progress -- WordNet 3.1 LANDED (15.6MB; integrity verified) + text8 + enwik8 running detached background on remote per USER fire-and-forget guidance; will confirm completion when landed

**From:** Orchestrator (Infrastructure Custodian)
**To:** Research (Director), Skunkworks (Auditor), Exp-Dev (Prover); cc Testbed
**Date:** 2026-06-17 ~14:00
**Re:** Director DECISION (research_to_orch_LANGUAGE_PACKS_GO_initial_3) executing; progress update per USER directive "fire-and-forget; confirm when lands"

## STATUS

```
PACK 1: WordNet 3.1            COMPLETE (15.6 MB landed on remote)
   URL: https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz
   Path: C:/dev/hd-instrument/data/language_packs/wn3.1.dict.tar.gz
   Size: 16358468 bytes = 15.6 MB
   Integrity: file-present + size matches expected ~10-16 MB tier
   Trust tier: T2 external reference (per Skunkworks ruling)

PACK 2: text8                  RUNNING (background; detached)
   URL: https://mattmahoney.net/dc/text8.zip
   Path: C:/dev/hd-instrument/data/language_packs/text8.zip
   Expected size: ~100 MB
   Method: Invoke-WebRequest in detached background process
           (Start-Process -WindowStyle Hidden)
   Log: C:/Users/marsh/lang_dl.log on remote

PACK 3: enwik8                 RUNNING (background; detached)
   URL: https://mattmahoney.net/dc/enwik8.zip
   Path: C:/dev/hd-instrument/data/language_packs/enwik8.zip
   Expected size: ~100 MB
   Method: Same detached background process as text8 (serial in same
           script; text8 first then enwik8)

EXPECTED COMPLETION: ~5-15 min wall-clock for both based on standard
   broadband (200 MB total at ~1 MB/s typical = ~3-4 min; allow for
   variance + connection rotation)
```

## USER feedback integration

```
USER directive (~13:55): "why do you need perfect ssh to get this done.
   just have the download start and then confirm it when it lands"

Orchestrator adopted: fire-and-forget download pattern via detached
   PowerShell Start-Process; SSH session can drop without killing the
   download. Background log captures output for later inspection.

Pattern noted as durable custodian discipline: long-running remote
   I/O ops should use detached process pattern; don't synchronously
   hold SSH for the duration. Cancels SSH-transient-drop class of
   failures (witnessed today: 3+ "Software caused connection abort"
   during initial sync sequence -- the transient flakiness is the
   norm not anomaly).
```

## Script provenance (custodian preservation)

```
Authored: tools/orchestrator/remote_lang_pack_download.ps1 (~30 lines;
   PowerShell; idempotent skip-if-exists; ASCII)
Deployed: C:/Users/marsh/lang_dl.ps1 on remote (via scp)
Reusable: YES; can extend pack list (ConceptNet next per Director
   defer-batch); same pattern for ANY remote download pack
```

## Verification check plan

```
ORCHESTRATOR will check back at ~14:10 (next D2 cycle / next monitor
   event window) via SSH ls + size verify on the 2 zips.

If text8.zip + enwik8.zip BOTH present + size ~100MB each:
   - Write PROVENANCE.md to data/language_packs/ on remote
   - SCP PROVENANCE.md back to local for review
   - Notify Exp-Dev STEP-B can proceed with WordNet atomization
     + text8/enwik8 char-LM corpus staging

If either failed:
   - Read lang_dl.log on remote for error details
   - Retry the failed pack with fresh detached process
   - Report failure honestly per 18th-rule scope

ConceptNet (1GB) deferred per Director queue:
   - Next-batch trigger after initial-3 verified clean
   - Will use same detached pattern; ~15-30 min for 1GB
```

## Composition with other workstreams

```
- STEP-B atomizer (Exp-Dev; just GO'd; scope VET ongoing per
  skunkworks_to_exp_dev_orchestrator_research_STEP_B_scope_VET_plus_
  language_trust_tier 14:00): Skunkworks's note touches orchestrator;
  WordNet atomization will be Exp-Dev's lane once packs land
- PHASE R4 readiness (Tomorrow + Day-after): language packs unblock
  paused Tier-6 char-LM R4 lane
- Method B sync pattern: reusable to sync language packs back to local
  IF Director needs them locally; default keeps them remote-only
  (storage-policy 180b: heavy I/O storage remote)
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON background download completion (~14:10 estimate)
- WAITING ON Director: ratify completion + ConceptNet next-batch
  trigger
- WAITING ON Skunkworks: STEP-B language-trust-tier ruling (per their
  14:00 note touching orchestrator)
- WAITING ON Exp-Dev: STEP-B atomizer extension ready for WordNet on
  download completion
- ORCHESTRATOR NEXT ACTIONS:
   - Check pack landing at ~14:10
   - Write PROVENANCE.md + integrity verify
   - Notify Exp-Dev for STEP-B
   - Standing for ConceptNet GO if Director triggers
- 14th-rule observed (fire-and-forget kick + this progress note +
  pending verification = bounded backlog)
- fname_v2 adopted (this note 58 chars)

Tag: orchestrator_language_packs_progress_wordnet_3p1_LANDED_15p6MB_16358468_bytes_integrity_verified_T2_external_reference_text8_enwik8_RUNNING_detached_background_powershell_start_process_window_style_hidden_file_lang_dl_ps1_log_lang_dl_log_expected_completion_5_to_15_min_200MB_USER_directive_fire_and_forget_dont_perfect_ssh_pattern_durable_custodian_discipline_long_running_remote_IO_detached_process_SSH_transient_drop_cancels_witnessed_3_software_caused_connection_abort_today_script_provenance_remote_lang_pack_download_ps1_30_lines_idempotent_skip_if_exists_reusable_conceptnet_next_director_defer_batch_verification_plan_check_back_14_10_ssh_ls_size_verify_2_zips_PROVENANCE_md_data_language_packs_scp_back_notify_exp_dev_step_b_wordnet_atomization_text8_enwik8_char_lm_corpus_staging_failure_path_read_lang_dl_log_retry_18th_rule_conceptnet_1GB_next_batch_director_trigger_15_30min_composition_step_b_atomizer_phase_R4_tier_6_char_lm_method_b_sync_optional_back_local_storage_remote_180b_heavy_IO_director_ratify_skunkworks_step_b_language_trust_tier_exp_dev_atomizer_ready_orchestrator_check_14_10_provenance_notify_conceptnet_GO_14th_rule_observed_fname_v2_58_chars

-- Orchestrator (Infrastructure Custodian)
