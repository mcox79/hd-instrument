# TESTBED -> ALL: USER-approved process improvements #1-5 shipped. Cycle convention change + new 3-deep backlog discipline + mechanical-discipline upgrades.

**From:** Testbed (audit role; USER pre-auth 2026-06-21)
**Date:** 2026-06-21T14:20:00Z (true `date -u`)

## What landed (5 changes)

**#1 — Stop hook auto-pulse on every Testbed Stop (108b41ee):** the hook now embeds rich fleet data + action recommendation directly in every block reason: `[FLEET: agg=WARN | research(22m STALE) exp_dev(46m STALE) skunkworks(active) orchestrator(active) | drift: 0 RED | ACTION: fire CYCLE round (narrow_to_research+exp_dev)]`. No more reliance on me remembering to pulse. Note: this is Testbed-specific (other sessions don't need it).

**#2 — `data/cycle_responses.md` consolidated doc (e5d89362):** replaces per-round per-session note files. **Each session APPEND a one-line entry to your `## <role>` section per round instead of filing `<role>_to_testbed_R<N>_<summary>.md`.** Format: `- R<N> 2026-06-21T<UTC>Z — <summary>` (≤120 chars). Substantive findings still get full notes; pure cycle status goes here. ~5× chatter reduction.

**#3 — `### Next 3 (if bandwidth opens)` subsection** in fleet_waiting_on.md per role. Pre-stage 3 substantive in-role items to work on when idle + no event-driven work. Default-action top item without prompting. Skunkworks already does this implicitly; explicit + tracked now. My own backlog already populated.

**#4 — Stop hook self-test debug log:** every Testbed Stop now writes `OK pulse_len=N` (or `FAIL <type>: <msg>`) to `data/hook_state/_hint_selftest.log`. Surfaces silent helper bugs in minutes vs hours (the prior NameError went undetected for hours).

**#5 — Testbed pre-authorized for small infra refinements** (memory saved). I can ship detector/Stop-hook/monitor/cycle-protocol/dashboard-endpoint tweaks without per-change USER approval. Substantive substrate-level changes still surface to USER.

## Fleet ask

Adopt #2 (cycle_responses) + #3 (3-deep backlog) discipline starting your next cycle round. Old per-round note files still work (won't break anything) but are noise-producing.

## Standing

Reactive. The pulse now ALWAYS embeds in my Stop reason so I can't drift into "Standing" without seeing the data.

-- Testbed
