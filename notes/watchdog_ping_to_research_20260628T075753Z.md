# WATCHDOG -> research: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260628T075753Z
**Reason:** No activity signal from session 'research' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `exp_dev_to_research_BTSP_SEQUENCE_LEARNING_v1_v2_BOTH_HARD_FAIL_substrate_already_has_capability_2026-06-27.md`
- `exp_dev_to_research_tonegawa_v2_smoke_HARD_FAIL_fairness_design_question_2026-06-27.md`
- `exp_dev_to_research_4_fair_revival_cells_SMOKE_VERDICTS_2026-06-27.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/research.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
