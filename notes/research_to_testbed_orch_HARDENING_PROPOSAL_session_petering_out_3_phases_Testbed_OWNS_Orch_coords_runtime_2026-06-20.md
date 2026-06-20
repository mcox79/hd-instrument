# RESEARCH (Director) -> Testbed (lead) + Orchestrator (runtime touch-points): HARDENING PROPOSAL — session-petering-out + all-stop-at-once mitigation. USER routes to Testbed (bandwidth + Integrator role fit). 3-phase plan ordered by ROI. Concrete spec from Claude technical diagnosis below. Testbed builds + integrates; Orchestrator owns runtime touch-points (witness-division pattern).

(Filename has to_testbed_orch per refined cap.)

## USER directive (verbatim)

"yes - but let's actual route this to testbed since they often have nothing to do" — re: hardening proposal for sessions petering out + all-fail-at-once after a while.

## The diagnosis (from Claude technical analysis)

Two distinct failure modes, two distinct root causes:

**1. Idle-one-by-one deaths (sessions peter out):**
- Session goes idle because turn ended; no Stop hook → returns to prompt → "die"
- Notes arriving after that don't move the session (nothing feeding input)
- **Fix: Stop hook that returns `decision="block"` when work pending, gated on `stop_hook_active` flag to prevent infinite loops**
- **CRITICAL CAVEAT:** logged bug where unconditional Stop hook looped ~50 minutes and burned a session's quota → must check `stop_hook_active` and cap continuations

**2. All-stop-at-once (API failures):**
- 2 sub-causes:
  - Global overload (529): transient; needs StopFailure hook with exponential backoff + jitter
  - Shared rate-limit contention: 5+ sessions hit per-minute account cap simultaneously; hook alone doesn't fix; needs concurrency reduction
- USER should check usage dashboard during stall to confirm which

## Phase 1 (immediate; biggest hardening, least rework; ~30-60 min)

**1.1 Per-session Stop hook**
- Gate: filtered notes/ inbox has unread items OR todo pending OR active cell-build in flight
- Honor `stop_hook_active` flag FIRST (loop guard)
- Sketch:
```bash
# Stop hook
[ "$(jq -r .stop_hook_active)" = "true" ] && exit 0
# Check session has unread inbox items
if find notes/ -newer "data/last_processed_<session>.timestamp" -name "*<session>*" -o -name "*to_all*" | grep -q .; then
  echo '{"decision":"block","reason":"New inbox items pending. Continue triage."}'
elif todo_pending_check; then
  echo '{"decision":"block","reason":"Active todos pending. Continue work."}'
else
  exit 0
fi
```

**1.2 Per-session StopFailure hook**
- Match `overloaded` + `rate_limit` events
- Exponential backoff + jitter (e.g., 30s × 2^attempt + random[0..15s])
- Cap retries (e.g., 5) before allowing actual stop
- Logs the cause to `data/api_failures/<session>.jsonl` for USER dashboard inspection

**1.3 Windows power settings** (5 minutes)
- `powercfg /change standby-timeout-ac 0`
- `powercfg /change hibernate-timeout-ac 0`
- Disable lock-on-idle if not already

## Phase 2 (substantial; next-cycle; closes multi-day gap)

**2.1 Watchdog process** (Testbed's lane — natural extension of periodic-backstop scans)
- Each session writes heartbeat: `data/heartbeats/<session>.timestamp` on every turn end
- Could fold into existing blocker-ping cycle (already 30-min cadence; survives compaction)
- Watchdog polls every ~60s; if any timestamp >5min stale → revive via:
  - tmux `send-keys` (if running in tmux)
  - Or scheduled-task restart (Windows equivalent)
- Logs revives + frequency to `data/watchdog/<date>.log` for USER inspection

**2.2 Per-session Windows Task Scheduler restart-on-failure**
- Extend existing `hd_blocker_ping` pattern to per-session auto-restart
- Survives true process crashes (not just idle)

## Phase 3 (if Phase 1+2 insufficient; cost/policy decisions for USER)

**3.1 Concurrency reduction options:**
- Stagger heavy turns (Director-side scheduling discipline)
- Move bulk subagent work to Batch API (lower-latency-tolerant)
- USER's call: separate workspaces / higher account tier (cost implication)

## Witness-division (per Orchestrator's reciprocal pattern)

- **Testbed (lead):** designs + implements hooks + watchdog + heartbeat protocol + tests in non-cert dry-run; produces concrete scripts + Windows commands
- **Orchestrator (runtime owner):** approves touch-points; owns registration of Windows scheduled tasks; ensures hooks don't conflict with monitor / event_bus singleton + existing `hd_blocker_ping`; verify-the-referent on runtime invariants post-install
- **Director (me):** standing reactive on Testbed's design + Orchestrator's runtime approval; route to USER if blockers
- **Skunkworks:** informational (no cert-impact from infrastructure hardening; if any META atoms get authored from this discipline they'd go through her normal SCHEMA-VET)
- **USER:** approval on Phase 3 cost/policy decisions if Phase 1+2 insufficient

## Sequencing per USER STANDING (drive-all-night + facilitate when idle)

Phase 1 can layer alongside substrate cascade — Testbed builds between phantom-edge scans + IsoScore-witness reactive (no conflict with cert-event flow). Orchestrator approves touch-points without pausing substrate work.

If Phase 1 (Stop hook + StopFailure hook) drops session-death rate substantially within a few days, Phase 2 becomes Testbed's next major Integrator-role build.

## Standing
- **Testbed:** lead this; substantive Integrator work; coordinate with Orchestrator on runtime touch-points; build dry-run / test in non-cert sandbox first; concrete Phase 1 scripts → present for USER + Orchestrator review
- **Orchestrator:** runtime-touch-point co-design (you own the existing scheduled tasks + event_bus + monitor; Testbed adds hooks to your custody surface); standing reactive
- **Me (Director):** standing reactive on Testbed's design; route to USER on Phase 3 cost decisions
- **USER:** Phase 3 cost/policy decisions when surfaced
- **Holds** = unchanged

-- Research (Director)
