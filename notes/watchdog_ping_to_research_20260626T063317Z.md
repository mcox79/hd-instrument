# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260626T063317Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_research_anisotropy_v4_cpu_path_DISPATCHED_2026-06-25.md`
- `exp_dev_to_research_Cell_B_C_v2_META_M7_redispatch_DISPATCHED_2026-06-25.md`
- `exp_dev_to_research_3cell_brain_consolidation_DISPATCHED_2026-06-25.md`
- `exp_dev_to_research_USER_beam_search_and_expansion_sweep_DISPATCHED_2026-06-25.md`
- `exp_dev_to_research_4cell_envelope_extension_DISPATCHED_2026-06-25.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
