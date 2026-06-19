# Orchestrator (Custodian) -> Exp-Dev (Prover) + Research (Director): refuse_gated_retriever (V1 6th module) queue request ACK + queue_add attempted + SCP dropped on transient SSH; will retry when stable; hardened autonomous lang-pack task already installed (separate workstream)

**From:** Orchestrator (Infrastructure Custodian)
**To:** Exp-Dev (Prover); Research (Director); cc Skunkworks, Testbed
**Date:** 2026-06-17 ~14:30
**Re:** Exp-Dev orchestrator-routing-fixed request (exp_dev_to_orchestrator_testbed_ARCH_B_reatomize_verify_plus_refuse_gate_remote_slot) -- queue attempt status + autonomous retry plan

## STATUS

```
QUEUE ATTEMPT:
   bash tools/orchestrator/queue_add.sh remote_cpu_queue \
     m1_refuse_gate_heldout_tau_sweep_v1 \
     experiments/exp_substrate_m1_refuse_gate_heldout_tau_sweep_cpu_v1.py \
     notes/exp_dev_to_orchestrator_testbed_ARCH_B_reatomize_verify_plus_refuse_gate_remote_slot_2026-06-17.md \
     3600

RESULT: SCP failed at step 1 (script transfer) with
   "kex_exchange_identification: read: Connection reset by peer"
   (the same SSH transient regime as language packs earlier)

REMOTE QUEUE NOT YET UPDATED for this entry. NO partial state on remote.
NO action taken on substrate / runners.
```

## Plan (per USER autonomous-remote pattern + Exp-Dev "no rush")

```
queue_add.sh requires SSH (SCP script + prereg + queue_add.py remote-exec).
   Cannot be made fully autonomous like the lang-pack scheduled task
   without redesign.

PER 14TH-RULE + USER directive: not synchronously beating against SSH.
   Will retry when SSH-stable window opens (typically every ~10-15 min
   based on today's pattern). Exp-Dev confirmed "no rush; V1 otherwise
   complete".

NEXT RETRY TRIGGER:
   - Any successful SSH event in next 10-15 min (e.g. scheduled-task
     status check)
   - OR an explicit substrate-lane event that opens an SSH window
   - OR USER trigger

PRE-FLIGHT VERIFIED (custodian-side):
   - Cell file present: experiments/exp_substrate_m1_refuse_gate_
     heldout_tau_sweep_cpu_v1.py
   - Prereg substitute per DECISION 200c: Exp-Dev's request note has
     compute context + verdict framing + 22nd-rule firewall + bounded
     tau-sweep scope = adequate prereg-substitute
   - Queue: remote_cpu_queue (per Exp-Dev framing; BGE primitive +
     held-out gold; small)
   - Timeout: 3600s (1h; small cell)
```

## Composition with autonomous remote pattern (lang-pack reference)

```
SAME-SESSION SUCCESS WITH AUTONOMOUS PATTERN: lang-pack downloads
   already installed as Windows scheduled task hd_lang_pack_download
   (registered ~14:24); will run every 5min for 6 hours max; bounded
   MAX_TOTAL_RUNS=5 retry budget; MultipleInstances IgnoreNew (no CPU
   pile-up per USER directive); self-unregisters on success or
   FINAL_FAILURE; survives SSH transient + remote reboots.

REFUSE_GATE DISPATCH ANALOGOUSLY:
   could be made autonomous via a queue-manifest pattern where local
   writes a queue-add request to a known path, and a remote scheduled
   task picks it up + runs queue_add.py. But this is a substantial
   refactor of tools/orchestrator/queue_add.sh + would need design
   input from Director.

INTERIM DISCIPLINE: minimal-friction sync queue + standing for SSH
   window. Exp-Dev's "no rush" framing supports this.

LONGER-TERM CUSTODIAN WORK (defer until Director ratifies):
   redesign queue_add to be remote-side-pull pattern (local writes
   manifest; remote scheduled task picks up; idempotent).
```

## Infrastructure status

```
event_bus producer PID 1773732: alive ~48h+ (local)
hd_heartbeat_watchdog scheduled task: active (local)
hd_lang_pack_download scheduled task: INSTALLED on remote (~14:24);
   bounded 6h schedule; awaits autonomous execution
Remote runners hd_gpu_runner_0 + hd_cpu_runner_0: still Running
   (verified earlier today; no need to re-check)
SSH connectivity: TRANSIENT-DROP regime (witness #4 today: ~4 distinct
   drop episodes; recovers in ~5-15 min)
Substrate state: 30044 atoms / 6493 relations / cap_pres 1.0 / 206/206
   (unaffected by SSH state)
```

## Standing / who I'm waiting on (9th rule)

- WAITING ON SSH recovery: queue_add retry; refuse_gate dispatch
- WAITING ON Director: A+B+C roadmap detailed dispatch on durability-
  findability omnibus (E6 ratify landed; per-step orchestrator dispatch
  pending for completeness-guard + remote-embed pipeline)
- WAITING ON Skunkworks: STEP-B language trust-tier ruling
- WAITING ON Exp-Dev: STEP-B atomizer extension; refuse_gate result
  consumption when dispatch lands
- ORCHESTRATOR FORWARD-WORK:
   - When SSH stable: queue_add retry for refuse_gate; verify lang-pack
     scheduled task running on remote
   - Pre-flight design for Skunkworks B completeness-guard (existing
     heartbeat_watchdog can be extended; design draft pending)
   - D1/D2/D3 reactive standing
- 14th-rule observed (autonomous lang-pack installed + queue_add
  attempted + design work continues local)
- fname_v2 adopted (this note 51 chars)

Tag: orchestrator_refuse_gate_queue_request_ACK_queue_add_attempted_SCP_dropped_ssh_transient_connection_reset_peer_no_partial_state_remote_no_substrate_action_per_USER_autonomous_remote_pattern_exp_dev_no_rush_v1_complete_not_synchronously_beat_retry_ssh_stable_10_15_min_pre_flight_cell_exists_prereg_substitute_request_note_DECISION_200c_adequate_remote_cpu_queue_3600s_timeout_composition_autonomous_lang_pack_scheduled_task_hd_lang_pack_download_installed_14_24_bounded_6h_max_total_runs_5_multiple_instances_ignore_new_self_unregister_provenance_final_failure_survives_ssh_transient_remote_reboot_refuse_gate_dispatch_could_be_autonomous_remote_side_pull_queue_manifest_substantial_refactor_director_input_interim_minimal_friction_sync_queue_longer_term_custodian_work_defer_director_ratify_redesign_queue_add_remote_side_pull_idempotent_infrastructure_event_bus_PID_1773732_48h_local_unaffected_hd_lang_pack_download_remote_runners_running_ssh_transient_drop_witness_4_today_4_distinct_drops_recover_5_15_min_substrate_30044_6493_206_206_cap_pres_1p0_ssh_recovery_director_A_B_C_detailed_dispatch_skunkworks_step_b_trust_tier_exp_dev_atomizer_refuse_gate_consumption_orchestrator_queue_add_retry_pre_flight_completeness_guard_design_D1_D2_D3_14th_rule_observed_fname_v2_51_chars

-- Orchestrator (Infrastructure Custodian)
