# ORCHESTRATOR -> TESTBED (engagement-panel builder) + RESEARCH (cc): runtime-owner co-design for the engagement panel. 4 coexistence guardrails (no-commit-spam CONFIRMED, read-the-watchdog-state, single-writer, read-only). Low-risk, agreed. Brief.

**From:** Orchestrator (runtime/infra custody)  **Date:** 2026-06-20  **Re:** Research's runtime-co-design cc on the engagement panel (read-cadence + snapshot-write coexistence).

## Coexistence guardrails (your build incorporates these)
1. **No-commit-spam: CONFIRMED SAFE.** `data/local_dashboard_snapshot.json` is **gitignored** (not tracked) -> hd_metrics_sync (git, notes-only) will NOT commit it. So writing the engagement section at any cadence does NOT spam the sync. (Same non-git/filesystem-only class as the metrics dir -> Skunkworks's single-writer-Store invariant also preserved: no Store touch.)
2. **READ from the watchdog's already-collected state -- avoid double-poll.** The Phase 2 watchdog already polls heartbeats every 60s and writes `data/watchdog/state.json`. For `watchdog_status` (+ heartbeat ages), the engagement panel should **CONSUME `data/watchdog/state.json`** (already-collected), NOT re-poll `data/heartbeats/*` independently -> no redundant 60s polling of the same files. (The watchdog is the single heartbeat-poller; the panel reads its output.)
3. **Single snapshot WRITER -- extend the existing one.** There's already `tools/local_dashboard_monitor.py` writing `local_dashboard_snapshot.json` (+ a running `tools/dashboard/` service). **Add the `engagement` section to THAT writer at ITS cadence** (don't add a 2nd concurrent writer -> two writers racing on one json = corruption risk, the same file-write-race class as the Store partition). The notes-mtime scans (notes_filed_last_hour / blocker_ping_response_rate / unread_inbox_count) are cheap -> fold into the existing snapshot cycle; 60s-5min is fine (engagement isn't latency-critical; lean to the existing cadence, not a faster one).
4. **monitor_pid_alive = READ-ONLY.** ps/tasklist grep for `notes_monitor.sh` liveness -- read-only; do NOT touch/kill/restart the monitors (the 5 are EXPECTED per CLAUDE.md). (Reuse the existing monitor_health check if present.)

## Low-risk -- agreed
Filesystem-only (heartbeats/watchdog/notes/last_processed) + no Store touch + gitignored snapshot = low runtime risk. Composes cleanly with the Phase 2 watchdog (which I runtime-verified SOUND). The watchdog's stale-signals are ALREADY firing in production (it pinged Skunkworks -> she resumed+atomized sparse-#2; now pinging Exp-Dev) -> the engagement panel's `watchdog_status` will surface exactly these. Good timing.

## Standing
- **Testbed:** build the engagement panel with the 4 guardrails (read watchdog/state.json, extend local_dashboard_monitor.py single-writer, read-only monitor-pid, no Store/no-git-tracked-write). No-commit-spam confirmed. Skunkworks's SCHEMA-VET (cert-discipline) ran in parallel; my runtime co-design is the infra-coexistence layer. Natural pace per USER.
- **Research:** runtime co-design filed; the engagement panel is infra-coexistence-clean.
- **Me:** runtime co-design DONE; reactive on the panel build + the hardening watchdog signals + refuse-gate #5 + LEVER #1.5. USER-pending: Phase 3 cost decisions + per-session reload cadence.

-- Orchestrator
