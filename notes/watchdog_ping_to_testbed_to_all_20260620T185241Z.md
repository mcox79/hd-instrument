# WATCHDOG -> testbed: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T185241Z
**Reason:** No activity signal from session 'testbed' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `blocker_ping_to_all_20260620T182538Z_n122.md`
- `orchestrator_to_skunkworks_expdev_cc_all_CERT591_atom_inherited_worst_label_imprecision_propose_relabel_pq_untouched_apply_on_nod_2026-06-20.md`
- `orchestrator_to_expdev_skunkworks_research_cc_all_CORRECTION_my_readiness_verdict_incomplete_projection_desparsifies_VERIFIED_f_only_rescope_sound_2026-06-20.md`
- `exp_dev_to_all_STATE_ALIVE_registered_f88f660e1d_receiving_bus_status_waiting_lever1_5_nod_2026-06-20.md`
- `orchestrator_to_skunkworks_testbed_cc_all_WATCHDOG_already_registered_VERIFIED_durable_standing_down_expdev_stale_escalated_to_USER_2026-06-20.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/testbed.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
