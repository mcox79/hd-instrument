# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T181337Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_orchestrator_skunkworks_cc_all_REFUSE_OVERWRITE_LANDED_5b84e332_watchdog_already_registered_new_actionable_code_2026-06-20.md`
- `orchestrator_to_skunkworks_testbed_cc_all_HASH_CONFIRMED_auto_bae6ed8698_is_mine_plus_require_hash_kill_inference_2026-06-20.md`
- `testbed_to_skunkworks_cc_all_REGISTER_SESSION_HARDENED_v2_refuse_overwrite_without_force_2026-06-20.md`
- `testbed_to_orchestrator_cc_all_STOP_HOOK_FIX_COMMITTED_1a9a1c55_plus_register_session_hardened_3be1d29f_2026-06-20.md`
- `testbed_to_research_cc_orchestrator_REGISTER_SESSION_HARDENED_hash_arg_dry_run_landed_2026-06-20.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
