# verdict_handler remote-first metrics fetch (2026-05-27)

## Problem statement

`verdict_handler` (and `strategy` for cap_map decisions) read per-cell metrics
from `data/exp_<name>/metrics.json` on the developer's LOCAL repo. That file
is frequently a STALE pre-ship smoke artifact, because:

1. Scripts use `get_output_dir(name)` which returns the same directory for
   smoke (`--smoke`) and FULL runs. Smoke runs OVERWRITE the FULL-name dir.
2. The dev typically runs `python experiments/<script>.py --smoke` locally
   to validate the prereg before queue_add. That smoke writes
   `data/exp_<name>/metrics.json` with `mode: SMOKE / N: 512 / device: cpu`.
3. After queue_add ships to marsh@home, the runner runs the FULL script
   (no `--smoke`). Production metrics land at
   `marsh@home:C:\dev\hd-instrument\data\exp_<name>\metrics.json`. Nothing
   syncs them back to local.
4. verdict_handler wakes on the dashboard's recent_verdicts entry, reads
   the LOCAL stale smoke metrics.json, runs Step 0 honest re-read, sees the
   anchor `_n4096` but metrics `N=512 mode=SMOKE`, and logs
   `[label-vs-honest]` -- a FALSE catch.

Concrete instance documented in `notes/n_mismatch_root_cause_2026-05-27.md`:
`wave14_saddle_cascade_plateau_v6_n4096_gpu`. Local recorded
`N=512 SMOKE 2.64s cpu`. Remote recorded
`N=4096 FULL 6821s cuda HARD_PASS 5/5`. The pattern fired 78+ times in one
day before this fix landed.

This is the CEILING of the N-mismatch saga. The FLOOR is the runner-side
validator at commit 60d2147 (`experiments/runner_v2_prod.py
validate_n_suffix_binding`), which catches future mis-shipped entries at
exit-time. Together they eliminate both actual mismatches and false-alarm
misreads.

## The fix

`tools/orchestrator/remote_state.py` gains three functions:

- `get_remote_metrics(name)` -- runs `ssh marsh@home type C:\dev\hd-instrument\
  data\exp_<name>\metrics.json`, parses JSON, returns dict with
  `_source: 'remote'` injected. Returns `None` on any failure (timeout,
  non-zero exit, parse error, missing file).
- `get_local_metrics(name)` -- reads the local file. Returns dict with
  `_source: 'local'` injected, or `None`.
- `get_metrics(name, *, prefer_remote=True)` -- THE public entry point.
  Calls remote first; falls back to local on `None`. Returns `None` only
  when both reads fail.

The `_source` field lets the caller distinguish authoritative-remote from
suspect-local-fallback. verdict_handler is required to prefix its return
with `[metrics-source: local-fallback]` when `_source == 'local'`, and to
emit `UNKNOWN` (no cap_map transition) when `get_metrics` returns `None`.

Strategy was updated alongside (it also reads metrics.json on verdict
events). Future agents that need metrics MUST use the bridge helper.

## Why SSH-via-subprocess and not paramiko / ssh_client.py

`tools/dashboard/ssh_client.py` is a persistent paramiko transport with a
strict prefix allowlist. It is excellent for the dashboard's long-running
poll loop. But:

- verdict_handler is a short-lived sub-agent invocation; the persistent
  transport's connection setup amortizes badly here.
- `audit_n_mismatch.py` already uses `subprocess.check_output(["ssh", ...])`
  with the same `marsh@home` alias. Matching that style keeps the dependency
  surface narrow (no paramiko import inside `remote_state.py`).
- The single command shape `type C:\...\metrics.json` is a read-only file
  cat; there is no token-injection surface beyond the anchor name, which is
  validated by `_NAME_RE = ^[A-Za-z0-9._-]+$`.

Timeout is 12s; on the rare occasion SSH hangs the call returns `None`
quickly and local-fallback kicks in. Per
`[[feedback-ssh-powershell-quoting]]` the command is `type` (cmd.exe
builtin) not PowerShell, so no nested-quoting risk.

## Test

```
python -m tools.orchestrator.remote_state wave14_saddle_cascade_plateau_v6_n4096_gpu
```

Expected (and verified 2026-05-27T16:43):

```
=== get_metrics('wave14_saddle_cascade_plateau_v6_n4096_gpu') ===
  _source        : remote
  verdict        : HARD_PASS
  config.mode    : FULL
  config.N       : 4096
  config.device  : cuda
  summary.N      : 4096
  summary.seeds  : [7, 17, 23, 31, 41]
  elapsed_s      : 6821.55
```

Local file at `data/exp_wave14_saddle_cascade_plateau_v6_n4096_gpu/metrics.json`
still shows the stale `SMOKE N=512 2.64s` artifact -- we did NOT delete it,
because the audit tool surfaces those on demand and they have diagnostic
value. The bridge simply no longer trusts them.

Force-local read (`prefer_remote=False`) returns the stale local for
backwards-compat (e.g., explicit dev-mode debug invocations); the production
verdict_handler path uses the default `prefer_remote=True`.

Nonexistent anchor returns `None`, exercising both-failed path.

## Files changed

- `tools/orchestrator/remote_state.py` -- added `get_remote_metrics`,
  `get_local_metrics`, `get_metrics`; extended CLI self-test to accept an
  anchor name argument.
- `tools/orchestrator/agents/verdict_handler.md` -- mandate
  `get_metrics(name)` in Self-discovery and Step 0 sections; add
  `[metrics-source: local-fallback]` and `[metrics-unavailable]` return
  prefixes.
- `tools/orchestrator/agents/strategy.md` -- mandate `get_metrics(name)` in
  the verdict-event entry.
- `notes/verdict_handler_remote_metrics_fix_2026-05-27.md` -- this note.

Out of scope (could not modify in this turn):

- `C:\Users\marsh\.claude\agents\verdict_handler.md` (the harness role-prompt
  the sub-agent loads at dispatch time). Self-modification of agent config
  is blocked by the harness classifier. The in-repo authoritative role
  contract (`tools/orchestrator/agents/verdict_handler.md`) is referenced
  at line 7-9 of the harness file as "Read that file FIRST before doing
  anything else. It is authoritative." -- so the in-repo change is the
  authoritative one. If the user wants the harness pointer file to mirror
  the change explicitly, that edit must be made manually.
