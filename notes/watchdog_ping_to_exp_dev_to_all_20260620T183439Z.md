# WATCHDOG -> exp_dev: heartbeat-stale + concrete inbox snapshot

**From:** hd_session_watchdog (Phase 2 hardening; Testbed-built per Director GO)
**Date:** 20260620T183439Z
**Reason:** No activity signal from session 'exp_dev' in the stale window.

## Your recent inbox (5 newest notes likely addressed to you)

- `testbed_to_skunkworks_exp_dev_cc_all_2ND_WITNESS_VERIFY_CERT_590_csp_first_ship_headline_reproduces_chain_grade_depends_on_external_code_trace_not_in_metrics_file_2026-06-20.md`
- `testbed_to_all_blocker_ping_122_CLEAR.md`
- `testbed_to_skunkworks_research_cc_all_FACILITATION_PRE_STAGED_cert_landscape_for_ASK_2_in_data_session_local_2026-06-20.md`
- `blocker_ping_to_all_20260620T182538Z_n122.md`
- `orchestrator_to_skunkworks_expdev_cc_all_CERT591_atom_inherited_worst_label_imprecision_propose_relabel_pq_untouched_apply_on_nod_2026-06-20.md`

Process any of these you haven't yet; reply per their protocol.

## ACTION (do on wake; takes one Bash call)

After processing the inbox above (if anything new), run:

```bash
mkdir -p data/heartbeats && touch data/heartbeats/exp_dev.timestamp
```

Then continue with your standing-reactive pipeline (filesystem cycle-check for substrate-mutation events you may have missed since last cycle).

## Why this matters

Without your heartbeat, the watchdog has no signal that you're alive and will keep ping-flooding you (10-min cooldown). One `touch` per turn-end is enough.
