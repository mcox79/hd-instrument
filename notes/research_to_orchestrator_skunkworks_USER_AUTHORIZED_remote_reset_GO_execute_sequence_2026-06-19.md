# RESEARCH (Director) -> Orchestrator (executor) + Skunkworks (cert-verify): USER AUTHORIZED the remote-reset. Execute the established sequence. Add one cheap pre-step: confirm no live remote writer (avoid clobbering an in-flight job's working tree). All Skunkworks-cleared cert-safety holds.

**From:** Research (Director)  **To:** Orchestrator, Skunkworks  **Date:** 2026-06-19  **Re:** USER AUTH RECEIVED -- execute the remote-reset sequence. ASCII; fname_v2.

## USER decision (the gate)
- USER quote: "authorized to do this get it going and let's do it right"
- Standing as: explicit destructive-op authorization on `git reset --hard origin/main` on the remote checkout, per the established belt-and-suspenders sequence + Skunkworks GATE-GO + Director GO-AHEAD.

## Sequence to execute (Skunkworks GATE + my "do it right" interpretation)

**Pre-step (added per "do it right"; cheap; ~30s):**
- **(0) Confirm no live remote writer.** Orchestrator: ssh marsh@home + `pgrep -af "python.*hdlab|python.*experiments|python.*atomize" || echo "none-running"` + `find data/substrate_index -newer data/.last_check -mmin -2 2>/dev/null | head` (or equivalent). If anything live writing, HOLD + route to me. Per the 6th-checklist rule (long cells checkpoint+resume), checkpoints survive in .npz outside the working tree, but an in-flight uncheckpointed write IS clobberable -- this catches that.

**Established sequence (Skunkworks-cleared):**
1. **Belt-and-suspenders preserved** -- both files already on the laptop:
   - `data/backup_remote_dirty_store_pre_reset_2026-06-19.tar.gz` (559MB; dirty Store excl derivable caches)
   - `data/backup_remote_3ahead_testbed_pre_reconcile_2026-06-19.bundle` (33KB; 3 remote-only testbed commits)
2. **Reset:** `git reset --hard origin/main` on remote checkout.
3. **Orchestrator immediate verify:** remote HEAD == origin/main + 0-behind / 0-ahead / 0-dirty.
4. **Route to Skunkworks for cert-verify** (sample-diff a set of dirty atom-ids vs origin/main):
   - If ALL resolve on origin -> superset confirmed; archive the tar.
   - If ANY don't -> replay through the atomize-VET chain; do NOT lose; tar is the recovery path.
5. **Re-enable hd_dispatch_consumer task** on remote.
6. **Root-cause the consumer-arch fix** (silent reset-failure since June 12) -> Skunkworks atomize as AUDIT_LESSON if novel root cause.

## What unblocks (post-reset clean)
- 40h Top-1: C-deferred A2 v6 on the grown 43,892 corpus (clean-checkout + commit-hash + substrate-id-hash recorded per Skunkworks's clean-caveat-cert-condition).
- 40h Next-8: ConceptNet apply (CSV acquisition Director-side; held-out firewall verify).
- M3 cron runner wiring (Orchestrator paused pending reset).

## Standing (9th rule)
- **Orchestrator:** execute the sequence (Pre-step 0 first; then established 1-6). Route results to me + Skunkworks at each verify gate.
- **Skunkworks:** reactive on the post-reset sample-diff + root-cause atomize.
- **Me (Director):** USER-visibility ACK filed; cascade-reactive on each gate; standing for verify-the-referent at each layer.
- **USER:** AUTH given; no further decision needed unless the post-reset sample-diff surfaces remote-only cert-bearing atoms (Skunkworks routes if so).

Let's do it right.

-- Research (Director)
