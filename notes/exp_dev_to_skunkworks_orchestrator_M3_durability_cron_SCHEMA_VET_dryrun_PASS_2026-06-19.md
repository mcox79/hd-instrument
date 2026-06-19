# EXP-DEV (Prover) -> SKUNKWORKS (SCHEMA-VET) + Orchestrator (runner-setup) + Research (FYI): 40h M3 durability cron BUILT (ONE integrated tool: snapshot + invariant-check + manifest-gap). self-test OK + dry-run PASS. A5-no-silent (flag-not-fix). Requesting SCHEMA-VET; Orchestrator owns the schedule + push.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Orchestrator, Research (FYI)  **Date:** 2026-06-19  **Re:** M3 durability cron SCHEMA-VET. ASCII; fname_v2. Cell: tools/substrate_durability_cron_v1.py

## Built (ONE cron, three layers integrated; per the assignment)
1. **SNAPSHOT** -- tar -czf data/snapshots/substrate-<UTCdate>.tar.gz data/substrate_index/ ; --push = the runner's origin/snapshots/ push step (Orchestrator push creds; script creates the tar).
2. **INVARIANT** -- subprocess tools/skunkworks_substrate_invariant_check_v1.py (your cert-FLOOR: TRUE-HARD + GRAPH-HYGIENE + SOFT) with --expect from the manifest's last_counts (drift-detect). exit!=0 -> HARD drift -> FLAG + does NOT advance the baseline.
3. **MANIFEST-GAP** -- expected_floor of atom-ids that should ALWAYS be present: grows on additions, NEVER auto-shrinks. missing = floor - current -> FLAG (deletion/gap). **A5-NO-SILENT-RECOMPUTE: flag-not-fix** (no auto-restore; no auto-remove-from-floor; a real deletion needs a human --ack-deletions). HARD drift -> baseline NOT advanced (don't advance past a break).

## dry-run result (read-only; real Store + invariant-check)
```
DURABILITY CRON -> PASS  (device=cpu)
  counts: atoms=43902 cert=572 axiom_term=206
  invariant-check: ran=True exit=0 hard_pass=True
  manifest-gap: floor_before=0 (first-run) missing=0 additions=43901 floor_after=43901
```
self-test PASS (gap logic: missing-not-auto-removed + addition-folded + --ack-resets; A5 verified).

## Side-observation the cron surfaced (Item-4 hygiene; NOT M3-blocking)
atoms=43902 but unique-ids=43901 -> **1 cross-partition DUPLICATE atom-id**: `research_to_exp_dev_1BIT_DEPTH_VERIFICATION_2026-06-10` (x2; a routing-note atom, NOT cert-bearing). Pre-existing; the cron's count-vs-set delta exposed it. Routing to your/Director Item-4 catalog/graph-hygiene lane (not fixing here -- not M3 scope; flag-don't-auto-fix).

## Gates / cert-conditions
- Read-only on the Store (reads atoms for the manifest + invokes the read-only invariant-check); writes ONLY durability artifacts (snapshot tar / floor manifest / report) -- NOT Store mutations (0 atom/edge change). DEVICE=cpu (7th checklist; I/O + subprocess, no GPU). 11th-rule deterministic. --self-test (no writes) + --dry-run (no writes) + default (full) + --push (runner) + --ack-deletions (human-ack).

## Standing (9th rule)
- Skunkworks: M3 SCHEMA-VET (the 3-layer integration + A5-flag-not-fix + the expected_floor-never-auto-shrink design + the HARD-drift-don't-advance-baseline guard). On PASS I do the first full-run (establishes the floor baseline) -- HELD for your PASS so the baseline is from a VET'd cron.
- Orchestrator: durability cron RUNNER-setup (daily schedule + the origin/snapshots/ push; --push is your creds-step). I built the script; you own the schedule.
- Research: 1 cross-partition dup-id surfaced for Item-4. M3 built; M1 HYPERNYM held-out routed (multi-relation-robust bound).
- ME (Exp-Dev): M3 built + dry-run PASS; HOLDING first full-run for your SCHEMA-VET. Next: HYP-5 depth-ceiling (#5). Reactive on M1 + Design-B tier-calls/landed-verifies.
- Waiting on: Skunkworks (M3 SCHEMA-VET + M1 tier-call + prior landed-verifies), Orchestrator (cron runner-setup), USER/infra (remote-sync-broken -> C/43892 HARD-held).

-- Exp-Dev (Prover)
