# CLAUDE.md

Conventions for AI-assisted work in this repository.

## Project

`hd-instrument` is an observable hyperdimensional computing substrate. See [PLAN.md](PLAN.md) for the full build plan and [PROGRESS.md](PROGRESS.md) for current status.

## SESSION STARTUP RITUAL (FIRST ACTION OF ANY SESSION LIFETIME, ALL ROLES)

Every Claude Code session, as its very first tool call after reading this file, must arm its own notes Monitor via the Monitor tool with the self-healing wrapper. Without this, the session goes dark the moment its previous Monitor crashes (set-u undefined-var on weird input, FS hiccup, etc) and silently stops receiving cross-session events. The wrapper `tools/monitor_arm.sh` re-runs `notes_monitor.sh` on any non-zero exit and emits a `MONITOR-CRASH` line so you know it recovered.

**The canonical Monitor invocation (substitute your role name; verbatim otherwise):**

```
Monitor({
  command: "python D:/AI/hd-instrument/tools/monitor_arm.py <role>",
  persistent: true,
  timeout_ms: 3600000,
  description: "notes_monitor <role> (Python; no subprocess spawns; popup-free)"
})
```

Where `<role>` is one of: `skunkworks | research | exp_dev | testbed | orchestrator`.

**Why Python (USER 2026-06-21 popup audit):** the prior bash wrapper (`tools/monitor_arm.sh` invoking `tools/notes_monitor.sh`) spawned a 4-stage pipeline (`find | grep | grep | sort`) every 20 seconds. Each child `.exe` under Claude Code's hidden-console parent allocated a fresh visible console window = popup flash. The Python port does the same set-diff logic in-process (`os.scandir` + Python re + set ops) with ZERO subprocess spawns after the initial arm. Bash variants remain in-tree for reference but should NOT be re-armed.

You'll receive a `MONITOR-ARMED:` confirmation line as the first task-notification when it's working. After that, every new note matching your role-filter arrives as a task-notification automatically -- no polling, no busy-work, just respond on wake.

If you DON'T do this and your previous-session Monitor crashed, you will SEEM idle while actually being completely disconnected from the bus. Sessions that have been silent for >30min when other sessions are clearly active are usually in this state -- re-arm the Monitor.

After arming, also `register_session.py` if the map needs your hash:
```
python tools/register_session.py <role> --hash auto_<XXX>
```
(Copy `auto_XXX` from your own Stop hook output: "Pending work for auto_XXX". --hash is the safe path; the no-hash inference is racy.)

## Monitoring & cross-session event coordination (ALL SESSIONS READ THIS)

This project runs as a 4-session architecture (exp_dev, research, testbed, orchestrator; plus skunkworks) on one laptop. **Do
NOT run your own heavy watcher loop** (per-session `find notes/ ... ; sleep` + ssh polling). N heavy scanners over ~3000 notes
every few seconds overheated the laptop (2026-06-12).

**CANONICAL monitor (USER directive 2026-06-18 ~00:25 via Skunkworks BROADCAST 21:20): the v5 set-diff TZ-proof
`notes_monitor.sh`.** It supersedes the prior event-bus-tail prescription. Arm it via the Monitor tool with persistent:true:

- Command: `bash tools/notes_monitor.sh <session>`  (`<session>` = skunkworks | research | exp_dev | testbed | orchestrator)
- Each new note arrives as one stdout line: `NOTE-FOR-<SESSION>: <filename>.md`
- 20-second poll cycle; uses `find notes -maxdepth 1 -name '*.md' -printf '%f\n'` (filenames-only -- cheap) + `comm -13` set-diff
  (never reads the clock, so TZ change / DST jump / mtime granularity boundary CANNOT break it; each new note reported exactly once)
- Filter: includes filenames containing `<session>` OR `to_all` OR `_all_`; excludes own outgoing (`^<session>_`)
- **5 `notes_monitor.sh` processes are EXPECTED** (one per session). NOT cruft. Do not kill.

Why v5 supersedes event-bus-tail: production data-point 2026-06-18 ~20:31-20:51 -- the `event_bus.sh` producer hung for 18 min
and missed routing a critical FREEZE signal; Skunkworks's v5 monitor was unaffected (reads `notes/` directly; verify-OUTPUT-not-
liveness baked in). v5's 20s cycle on a filenames-only `find` over ~3000 notes is well below the 2026-06-12 thermal threshold
(that incident was full-content scans every few seconds, plus ssh polling -- a completely different cost class).

**Backstop role of the event bus** (still useful, just not canonical): `tools/event_bus.sh` singleton (via `data/.event_bus.lock`;
auto-started at logon by `tools/event_bus_launch.cmd` registered in the user Startup folder) is preserved as a SECONDARY routing
path. Restart if truly dead: `rm -f data/.event_bus.lock && bash tools/event_bus.sh &`. Sessions may tail
`data/events/<session>.log` as an additional sanity-check; v5 `notes_monitor.sh` is the load-bearing primary.

**Still deprecated** (do NOT relaunch these old per-session watchers): `queue_watch.sh`, `notes_watch.sh`, `research_seen_v5`,
`testbed_seen`, `watch_for_orchestrator.py`. These are the multi-watcher-proliferation cruft from before the bus consolidation;
the canonical v5 `notes_monitor.sh` is a DIFFERENT script and not in that deprecation list.

13th-rule backstop-to-the-backstop: no monitor validates its own death. `find notes -maxdepth 1 -name '*.md'` against a known
sender's recent file is the ground-truth manual cross-check. Verify-OUTPUT-not-liveness applies.

## Note filename discipline (USER 2026-06-21)

**Cap: 120 chars total** (incl. `.md` extension) for `notes/<filename>.md`. Drift: many recent filenames hit 150-250+ chars; restated session lists; stuffed body content into filename.

**Format:**
```
<from>_to_<recipient>_<TOPIC_SLUG>_<YYYY-MM-DD>.md
```
- `<recipient>` is single role (e.g. `skunkworks`) OR `cc_all` for broadcasts. Drop multi-role enumeration like `to_research_skunkworks_exp_dev_orchestrator_cc_all` — pick the primary recipient + put cc-list in note body.
- `<TOPIC_SLUG>` ≈ 5-10 words snake_case + optional ALL_CAPS for emphasis. Headline-quality, not the whole abstract.
- Multi-clause descriptions belong in the note body, not the filename.

**Examples:**
- BAD (156 chars): `testbed_to_research_skunkworks_exp_dev_orchestrator_FLEET_WAITING_ON_SUBSTRUCTURE_v2_section_template_2026-06-21.md`
- GOOD (~70 chars): `testbed_to_all_FLEET_WAITING_SUBSTRUCTURE_v2_2026-06-21.md`

**Why:** unreadable in terminal `ls`; hard to copy-paste; encourages stuffing context into filenames vs bodies; the v5 monitor's filter still works either way but the human + the dashboard parser don't.

## Conventions

- Python 3.11+, PyTorch tensors with explicit dtypes (complex64 for FHRR, float32 for HRR).
- `N` (vector dimensionality) is a config constant, default 1024.
- All randomness uses a passed-in `torch.Generator` with a known seed.
- Type hints on all public functions. One-line docstrings with shape annotations.
- All vectors are `torch.Tensor`; never `numpy.ndarray` at API boundaries.

## Style

- Direct, terse code. No unnecessary abstraction.
- One-line docstrings, max. No multi-paragraph comment blocks.
- No emojis in code, comments, or output.
- No em dashes in code output.

## Verification discipline

- Every framework feature ships with at least one scaffold-free witness in `verification/`.
- Verification tests must pass with `tracing=False`.
- `python verification/run_certification.py` must pass on `main`.

## When implementing a new feature

1. Write the closed-form theory or oracle comparison in `verification/theory.py` or `reference/`.
2. Write the verification test in `verification/`.
3. Implement the feature in `hdlab/`.
4. Run `pytest verification/` and confirm green.
5. Update `PROGRESS.md`.
