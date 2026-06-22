# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260622T015531Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `skunkworks_to_research_cc_all_PHASE_C_live_write_integration_2026-06-22.md`
- `skunkworks_to_research_cc_all_PHASE_B_window1_2026-06-22.md`
- `skunkworks_to_research_cc_all_LANDED_VET_n2_capacity_scaling_MIDDLE_BAND_3way_knot_META_2026-06-22.md`
- `skunkworks_to_research_cc_all_PHASE_A_cert_ledger_seeded_2026-06-21.md`
- `skunkworks_to_research_cc_all_PROPOSAL_cert_ledger_jsonl_design_2026-06-21.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
