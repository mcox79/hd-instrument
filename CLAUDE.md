# CLAUDE.md

Conventions for AI-assisted work in this repository.

## Project

`hd-instrument` is an observable hyperdimensional computing substrate. See [PLAN.md](PLAN.md) for the full build plan and [PROGRESS.md](PROGRESS.md) for current status.

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
