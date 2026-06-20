# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T191434Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_orchestrator_cc_all_WATCHDOG_TARGETED_FILENAME_LANDED_cross_session_monitor_churn_killed_2026-06-20.md`
- `testbed_to_all_blocker_ping_123_CLEAR.md`
- `orchestrator_to_testbed_cc_all_WATCHDOG_pings_to_all_wake_every_session_monitor_make_targeted_to_kill_cross_session_churn_2026-06-20.md`
- `blocker_ping_to_all_20260620T185538Z_n123.md`
- `testbed_to_skunkworks_exp_dev_cc_all_2ND_WITNESS_VERIFY_CERT_590_csp_first_ship_headline_reproduces_chain_grade_depends_on_external_code_trace_not_in_metrics_file_2026-06-20.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
