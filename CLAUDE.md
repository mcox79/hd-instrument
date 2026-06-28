# CLAUDE.md

Conventions for AI-assisted work in this repository.

## Project

`hd-instrument` is an observable hyperdimensional computing substrate. See [PLAN.md](PLAN.md) for the full build plan and [PROGRESS.md](PROGRESS.md) for current status.

## SESSION STARTUP RITUAL (FIRST ACTION OF ANY SESSION LIFETIME, ALL ROLES)

### STEP 0 (research role, post-compaction recovery):

Before arming Monitor, query the substrate-Director-KB for the post-compaction backup doc:

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp
python d:/AI/hd-instrument/tools/director_kb_query.py --filename-contains POST_COMPACTION_BACKUP --source-class=notes
```

The query returns the BACKUP file at rank 1 (cosine=1.0). READ the source file end-to-end — it's self-contained with all USER directives, cortex state, in-flight work, milestones, recovery procedure for the active session. This is the load-bearing first action for any research session that's been compacted; skip only if `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_<date>.md` doesn't exist (in which case grep filesystem for whatever's most recent). See MEMORY.md "READ FIRST AFTER COMPACTION" callout for the full sequence.

### STEP 1 (all roles): arm Monitor

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

**Why Python:** the bash wrapper (`tools/monitor_arm.sh` invoking `tools/notes_monitor.sh`) spawns a 4-stage pipeline (`find | grep | grep | sort`) every 20 seconds. Each child `.exe` under Claude Code's hidden-console parent allocates a fresh visible console window = popup flash. The Python port does the same set-diff logic in-process (`os.scandir` + Python re + set ops) with ZERO subprocess spawns after the initial arm. Bash variants remain in-tree for reference but should NOT be re-armed.

You'll receive a `MONITOR-ARMED:` confirmation line as the first task-notification when it's working. After that, every new note matching your role-filter arrives as a task-notification automatically -- no polling, no busy-work, just respond on wake.

If you DON'T do this and your previous-session Monitor crashed, you will SEEM idle while actually being completely disconnected from the bus. Sessions that have been silent for >30min when other sessions are clearly active are usually in this state -- re-arm the Monitor.

After arming, also `register_session.py` if the map needs your hash:
```
python tools/register_session.py <role> --hash auto_<XXX>
```
(Copy `auto_XXX` from your own Stop hook output: "Pending work for auto_XXX". --hash is the safe path; the no-hash inference is racy.)

### STEP 2 (research role): agent-spawn is the operating model

Research is team lead. Spawn `hdi_<role>` sub-agents for ALL bounded work via the Agent tool.

**NOT ALLOWED in main thread:**
- Editing `experiments/*.py` cell files
- Running cell smoke via Bash
- Writing pre-reg files for cells you're dispatching (cell-author owns pre-reg)
- Iterating on cell implementation when smoke fails (hdi_exp_dev's job)
- Direct SSH dispatch of cells to remote_cpu_queue / overnight_queue (use hdi_orchestrator)
- Landed-VET / atomization in main thread (hdi_skunkworks owns; AUDIT-ONLY discipline)
- Capacity-stress drills / cell debugging in main thread

**ALLOWED in main thread:**
- Reading metrics.json / verdict_msg (verification)
- Running observability tools (`tools/runner_status.py`, `tools/peek_arm_metrics.py`, dashboard reads)
- Reading queue state
- Authoring memory rules / BACKUP doc updates
- Pulling/pushing git commits via Bash (status_log, BACKUP)
- Dispatching agents (Agent tool with `hdi_<role>`)

**Verification:** if you see yourself typing `experiments/*.py` in an Edit tool or running smoke via Bash, that's the violation moment — STOP and spawn `hdi_exp_dev` instead.

## Monitoring & cross-session event coordination (ALL SESSIONS READ THIS)

The monitor infra spans 5 session-names (exp_dev, research, testbed, orchestrator, skunkworks) — one `notes_monitor` scheduled-task process per session-name. These are how spawned sub-agents and the research session observe new notes.

**Do NOT run your own heavy watcher loop** (per-session `find notes/ ... ; sleep` + ssh polling). N heavy scanners over ~3000 notes every few seconds overheat the laptop.

**Canonical monitor: the v5 set-diff TZ-proof `notes_monitor.sh`.** Arm it via the Monitor tool with persistent:true:

- Command: `bash tools/notes_monitor.sh <session>`  (`<session>` = skunkworks | research | exp_dev | testbed | orchestrator)
- Each new note arrives as one stdout line: `NOTE-FOR-<SESSION>: <filename>.md`
- 20-second poll cycle; uses `find notes -maxdepth 1 -name '*.md' -printf '%f\n'` (filenames-only -- cheap) + `comm -13` set-diff
  (never reads the clock, so TZ change / DST jump / mtime granularity boundary CANNOT break it; each new note reported exactly once)
- Filter: includes filenames containing `<session>` OR `to_all` OR `_all_`; excludes own outgoing (`^<session>_`)
- **5 `notes_monitor.sh` processes are EXPECTED** (one per session). NOT cruft. Do not kill.

**Event bus as backstop:** `tools/event_bus.sh` singleton (via `data/.event_bus.lock`; auto-started at logon by `tools/event_bus_launch.cmd` registered in the user Startup folder) is a SECONDARY routing path. Restart if dead: `rm -f data/.event_bus.lock && bash tools/event_bus.sh &`. Sessions may tail `data/events/<session>.log` as an additional sanity-check; v5 `notes_monitor.sh` is the load-bearing primary.

**Deprecated** (do NOT relaunch these per-session watchers): `queue_watch.sh`, `notes_watch.sh`, `research_seen_v5`, `testbed_seen`, `watch_for_orchestrator.py`. The canonical v5 `notes_monitor.sh` is a DIFFERENT script and not in that deprecation list.

Backstop-to-the-backstop: no monitor validates its own death. `find notes -maxdepth 1 -name '*.md'` against a known sender's recent file is the ground-truth manual cross-check. Verify-OUTPUT-not-liveness applies.

## Note filename discipline

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
