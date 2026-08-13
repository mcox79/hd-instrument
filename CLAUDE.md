# CLAUDE.md

Conventions for AI-assisted work in this repository.

## Project

`hd-instrument` is an observable hyperdimensional computing substrate. See [PLAN.md](PLAN.md) for the full build plan and [PROGRESS.md](PROGRESS.md) for current status.

## SESSION STARTUP RITUAL (FIRST ACTION OF ANY SESSION LIFETIME, ALL ROLES)

### STEP 0 (research role, post-compaction recovery):

**FIRST, ALWAYS: read `notes/SUBSTRATE_CHARTER_read_first.md`** — the succinct goal + invariants + 3 layers + CURRENT FOCUS + anti-drift rule. It exists because sessions have strayed; re-anchor to it before dispatching anything. Then `notes/THE_PLAN.md` for the detailed plan.

Then, before arming Monitor, query the substrate-Director-KB for the post-compaction backup doc:

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp
python d:/AI/hd-instrument/tools/director_kb_query.py --filename-contains POST_COMPACTION_BACKUP --source-class=notes
```

The query returns the BACKUP file at rank 1 (cosine=1.0). READ the source file end-to-end — it's self-contained with all USER directives, cortex state, in-flight work, milestones, recovery procedure for the active session. This is the load-bearing first action for any research session that's been compacted; skip only if `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_<date>.md` doesn't exist (in which case grep filesystem for whatever's most recent). See MEMORY.md "READ FIRST AFTER COMPACTION" callout for the full sequence.

### STEP 1 (research role): agent-spawn is the operating model

Research is the director. Main session does judgment, strategy, direction, and 1-off important work. Sub-agents do the rote and heavy work — cell authoring, smoke iteration, landed-VET, atomization, dispatch, infra refinements.

Spawn `hdi_<role>` sub-agents via the Agent tool. Available roles: `hdi_exp_dev` (cell author + smoke + local dispatch), `hdi_skunkworks` (landed-VET + atomization; AUDIT-ONLY), `hdi_orchestrator` (push + remote queue_add + state sync), `hdi_testbed` (infra refinements + 2nd-witness on cross-cutting changes).

**Main thread (director's work):**
- Strategy + goal direction + thinking through the process
- 1-off important docs (BACKUP, memory rules, plan updates)
- Reading metrics.json / verdict_msg (verification)
- Running observability tools. PRIMARY monitor = `python tools/inflight_monitor.py` (reliable never-silent status: GPU, queues, runners, local off-queue experiments, alerts). Local GUI = `tools/dash_gui.py` (Tkinter window reading the same `build_state()`; replaces the fragile web dashboard as the day-to-day monitor). Also `tools/runner_status.py`, `tools/peek_arm_metrics.py`.
- **REMOTE-LIVENESS TRUTH SIGNAL = inprogress-checkpoint mtime + GPU utilization, NOT the training heartbeat.** The `_heartbeat.jsonl` cadence is coarse (e.g. every ~6000 units / ~20 min) and stops between beats and when a run finishes — it repeatedly false-alarms as a "stall" or "stale" when the run is fine (fooled the Director 3x on 2026-07-28). To decide if a remote run is alive/progressing: SSH and check that the `ckpt_seed_*_inprogress.pt` mtime is advancing AND `nvidia-smi` util is high. A fresh checkpoint = training is progressing regardless of heartbeat age. Never conclude "stalled/landed" from the heartbeat alone.
- Reading queue state
- Pulling/pushing git commits via Bash (status_log, BACKUP)
- Dispatching agents (Agent tool with `hdi_<role>`)

**Sub-agent work (delegate, don't do in main thread):**
- Editing `experiments/*.py` cell files
- Running cell smoke via Bash
- Writing pre-reg files for cells being dispatched (cell-author owns)
- Iterating on cell implementation when smoke fails (`hdi_exp_dev`)
- SSH dispatch of cells to `remote_cpu_queue` / `overnight_queue` (`hdi_orchestrator`)
- Landed-VET / atomization (`hdi_skunkworks` AUDIT-ONLY)
- Capacity-stress drills / cell debugging

**Lean spawn prompts:** pass paths + raw context. Do NOT pre-bake numbers, predicted analysis, or prescribed conclusions in the prompt — that turns sub-agents into rubber-stamps and defeats independent verification. The sub-agent does its own off-disk recompute, mechanism-class audit, and tier decision.

**Pre-spawn check (before every spawn, three criteria):**
1. Is this task independent from work already in flight (no shared file conflicts)?
2. Is the scope bounded (one cell group, one audit batch, one dispatch operation)?
3. Will the result come back as a summary the director can act on (not a context-flood)?

If any answer is no: do it in main thread, defer, or serialize behind an in-flight spawn.

**Spawn budget:** ≤5 agents in flight by default (raised from 3 by USER 2026-07-02 based on session evidence of persistent bottlenecking with mature sub-agent instrumentation). USER may authorize further exceeding. Watch signals to tighten back: multiple agents on same file, race conditions on git commits, main-thread losing track of who's doing what.

**Default to `run_in_background: true` for `hdi_*` spawns.** Foreground Agent calls BLOCK the main session — Director can't respond to USER, can't dispatch follow-up work, can't author docs. Background mode (`run_in_background: true`) returns an agentId, fires a notification on completion, and keeps the main session responsive throughout. Use foreground only when the very next action depends on the spawn's return value AND there's no other useful work to do meanwhile (rare).

**Spot-check, don't re-do:** when a sub-agent returns, verify by reading 1-2 specific metrics or hash-checking a cited result. If wrong, escalate via SendMessage with the delta — don't restart with a fuller prompt.

**YIELD AFTER DISPATCH (2026-08-13, measured).** When you spawn a subagent with
`run_in_background`, END YOUR TURN. Do not keep working on the same turn while it runs.

Return: one line naming what was dispatched, and nothing else. No summary of what you expect it
to find, no adjacent work, no next steps, no tables. The point of backgrounding is to return
control to the USER, and that only happens when your turn ends.

Why this is written down: session-transcript forensics (notes/director_delegation_audit_2026-08-12.md)
showed the subagents were NOT the blocker — all spawns set `run_in_background: true` and returned
an agentId immediately. The USER's input was queuing behind the DIRECTOR's own continued
generation, not behind any agent. Generation is serial: every additional paragraph after the
dispatch is time the USER spends locked out. This cost hours across 2026-08-12.

**Violation tripwire:** if you see yourself typing `experiments/*.py` in an Edit tool or running smoke via Bash, that's the moment — STOP and spawn `hdi_exp_dev` instead.

## Notes directory (single-session model)

`notes/` is for Director's session-internal artifacts (BACKUP doc, research decisions log, status digests). It is NOT a cross-session mailbox — the 4-session fleet model is dead. Sub-agents communicate via SendMessage (in-conversation), not via `notes/` files. Do NOT use `<from>_to_<recipient>_*.md` filenames; those came from the legacy ferry mechanism. Pick a topic-slug name that describes what the doc IS, not who it's TO.

Filename cap: 120 chars (incl. `.md`). Topic-slug 5-10 words snake_case; optional ALL_CAPS for emphasis.

## Capability tracking (durability gate)

`data/capability_registry.jsonl` is the single current reference for every genuinely-built capability + its wire-or-shelve decision (supersedes `notes/capability_map.md` / `capability_scorecard.md` / `promotion_backlog.md` checkboxes -- those rotted silently; this one is machine-audited by `tools/capability_registry_audit.py`, not hand-checked). Query it before building anything that might already exist.

Gate, at land-time, for anything genuinely-good (cert / HARD_PASS):
1. **WIRE** (promote to `hdlab/`, register in the registry, target + step noted) or **SHELVE** (explicit revival criteria) -- nothing stays in limbo.
2. New experiments CONSULT the registry first; reuse WIRED capabilities, don't reinvent.
3. Run `python tools/capability_registry_audit.py` at **SESSION START** (research role ritual, part of the SESSION STARTUP RITUAL above) AND on the meta_audit cadence -- two triggers, not one.

**The durability anchor is the session-start read, not an OS cron.** 11 `hd_*` scheduled tasks silently disabled for ~12 days (2026-07-16 to 2026-07-28) with no one noticing -- OS crons proved fragile and unmonitored. A rule or capability that lives only in a scheduler is one silent disable away from not existing. Cadence crons (`hd_capability_registry_audit`, meta_audit) still run and are useful, but they are a backstop, NOT the enforcement mechanism -- the enforcement is this file + MEMORY.md + WHERE_WE_ARE_NOW getting read every session regardless of what the scheduler is doing.

**Same durability gate applies to the director_kb ingest loop (testbed 2026-08-01):** `hd_director_kb_continuous_ingest` (the 5-min-poll scheduled task keeping the queryable director_kb current) was found silently Disabled for 6 days (2026-07-26 to 2026-08-01), exactly the same failure class as above -- the KB kept answering queries but with stale, week-old content and no one noticed because nothing read the gap. Run `python tools/director_kb_freshness_check.py` at **SESSION START** (alongside `capability_registry_audit.py` above) -- it compares the index's last-scanned mtime against the newest file on disk under `notes/`+`preregs/` and exits 1 with a loud stderr banner if the gap exceeds 30 minutes or the index hasn't ingested in over an hour. Pass `--fix` to also launch a catch-up ingest in the background. This is a READ, not a cron -- it works even if the scheduled task itself is (again) silently disabled.

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

## Multi-unit cell checkpoint/resume (MANDATORY)

Any experiment cell that loops over >1 (arm, seed) unit MUST use `tools/exp_checkpoint.py`
(`unit_key`, `completed_units`, `record_unit`, `load_units`) instead of accumulating results
in a bare in-memory list. For each unit: skip it if its `unit_key` is already in
`completed_units(OUTPUT_DIR)` (load its prior result from `load_units` instead); otherwise
compute it and call `record_unit(OUTPUT_DIR, key, result)` immediately after it finishes, so a
killed/hung run loses at most the in-flight unit. The final `metrics.json` is still assembled
from `load_units(OUTPUT_DIR)` and written once via the existing atomic `os.replace` pattern —
this only changes how per-unit progress survives a crash, not the final-metrics contract.
Resume order must stay deterministic (respect the existing `sorted(set())` discipline) so a
resumed run computes the same remaining units a fresh run would have.

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

## Superpowers plugin: evaluated and removed (2026-08-12)

The `superpowers` plugin was installed, evaluated, and has been UNINSTALLED. Do not
reinstall it expecting value without re-reading this note. Its one durable contribution
was the SessionStart-hook PATTERN; we adopted that independently as
`tools/session_start_hook.py`, wired to our own rules (below), not to the plugin. Its
skills went largely unused because this project's own disciplines (pre-registration,
the control battery, VET, the capability-registry WIRE-or-SHELVE gate) are already
stricter than what the plugin offered. `using-git-worktrees` and
`finishing-a-development-branch` were rejected as hazards given the large uncommitted
canonical store and untracked `data/foundation/` (worktree flow includes `git clean
-fdx`, which would destroy untracked foundation data). On three separate operational
problems it was tested against -- main-thread blocking, scheduling, and per-agent model
control -- it offered nothing. Separately measured: agent-definition frontmatter keys
`model` and `tools` are real and take effect; `background` and `isolation` are NOT real
keys -- `background: true` was added to an agent definition as a test and had no effect.

## Agent-teams / frontmatter findings (2026-08-12 night)

- `background:` in agent frontmatter is INVALID -- not merely ignored: it makes the whole
  agent definition FAIL TO LOAD. All five `hdi_*` agents vanished from the available types
  the moment it was added to one definition, and returned when it was removed. This corrects
  the "no effect" claim in the superpowers note above -- the effect is total load failure, not
  a no-op. Do not add it.
- `model` and `tools` ARE valid, working frontmatter keys.
- The `hdi_*` fleet only resolves with client env var `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
  (`~/.claude/settings.json` `env` block). Without it, only the plain-named set resolves:
  `exp_dev, research, verdict_handler, strategy_scribe, memory_curator, meta_audit,
  routing_handler`.
- Effort level is driven by env var `CLAUDE_CODE_EFFORT_LEVEL` (currently `high`), which
  overrides the `effortLevel` key in settings.json (reads `xhigh`, inactive) -- don't "fix"
  that key expecting a behavior change.
- Backgrounding subagents was never the main-thread-blocking cause -- see
  `notes/director_delegation_audit_2026-08-12.md`.

## SessionStart hook (enforcement, not advice)

`tools/session_start_hook.py` runs on every session start/clear/compact (wired in
`D:/AI/.claude/settings.json`) and injects: the 6 non-negotiables, the last
capability-registry audit + its age, and a LIVE director_kb freshness check.

**Why a hook and not a read or a cron.** Both prior mechanisms failed silently: 11 `hd_*`
scheduled tasks disabled ~12 days unnoticed; the director_kb ingest disabled 6 days
unnoticed. A session-start READ depends on the agent choosing to do it. The hook depends on
neither. Keep it FAST (<10s): it reports STATUS and reads persisted audit results -- it must
never run the 3-minute registry audit inline.
