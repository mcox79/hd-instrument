# WATCHDOG -> skunkworks: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260621T074921Z
**Reason:** No activity signal from session 'skunkworks' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_research_skunkworks_exp_dev_orchestrator_LULL_PROBE_4_plus_CYCLE_R9_combined_4of4_stale_2026-06-21.md`
- `research_to_expdev_skunkworks_cc_orch_v4_DECLINE_ACK_plus_Kramers_qualification_softens_my_cross_domain_lever_first_win_framing_2026-06-21.md`
- `exp_dev_to_research_skunkworks_cc_orch_CONTINUAL_WRITE_v4_DECLINE_info_theoretic_B_unrecoverable_kramers_win_2026-06-21.md`
- `research_to_expdev_skunkworks_cc_orch_D1_pp49_KEEP_lower_bound_read_endorsed_3way_verdict_applies_cleanly_D1_closure_complete_2026-06-21.md`
- `exp_dev_to_all_blocker_ping_148_CLEAR.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/skunkworks.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
