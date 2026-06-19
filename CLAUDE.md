# CLAUDE.md

Conventions for AI-assisted work in this repository.

## Project

`hd-instrument` is an observable hyperdimensional computing substrate. See [PLAN.md](PLAN.md) for the full build plan and [PROGRESS.md](PROGRESS.md) for current status.

## Monitoring & cross-session event coordination (ALL SESSIONS READ THIS)

This project runs as a 4-session architecture (exp_dev, research, testbed, orchestrator) on one laptop. **Do NOT run your own
heavy watcher loop** (per-session `find notes/ ... ; sleep` + ssh polling). N heavy scanners over ~3000 notes every few seconds
overheated the laptop (2026-06-12). Instead:

- A **single shared producer** `tools/event_bus.sh` (singleton via `data/.event_bus.lock`; auto-started at logon by
  `tools/event_bus_launch.cmd` registered in the user Startup folder) does the heavy scan ONCE per 30s and ROUTES queue + notes
  events by recipient into `data/events/<session>.log`.
- **Each session consumes via a cheap tail only** — set your Monitor to: `tail -n0 -F data/events/<session>.log`
  (`<session>` = exp_dev | research | testbed | orchestrator). No find, no grep, no ssh in your monitor.
- **Never launch a second producer** (singleton refuses, but don't try) and never relaunch the old per-session watchers
  (`queue_watch.sh`, `notes_watch.sh`, `research_seen_v5`, `testbed_seen`, `watch_for_orchestrator.py`). Keep ONE runner and
  ONE dashboard instance only.
- Restart the producer if ever truly dead: `rm -f data/.event_bus.lock && bash tools/event_bus.sh &` (or just re-run
  `tools/event_bus_launch.cmd`). Routing rules live in `tools/event_bus.sh`; if your session is missing an event class, add a
  route there.

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
