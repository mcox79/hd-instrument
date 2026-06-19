# Orchestrator refactor plan — 2026-05-23

Author: senior-systems-architect audit sub-agent.
Brief: comprehensive audit of every load-bearing piece of the orchestrator
system (dispatch.py, queue_add routing, sub-agent prompts, status surfaces,
dashboard, remote-CPU runner, structural agent-usage mandate). Goal: ONE
ordered refactor plan that closes all known structural bugs in a single
pass, with parallel sub-agent dispatch where it's safe.

User pressure points (the load-bearing complaints):
1. "Are you ironing out all the bugs? I feel like right now you're woefully inefficient."
2. "When will the dashboard be ready? When will you be using agents to maximum effect? Do we need more architecting?"

Both are structural, not vibes. The system is partially migrated, partially
instrumented, and has at least four known dropped-on-the-floor surfaces.

---

## (a) HEADLINE — the 3 most important fixes to ship in the next 2 hours

These are the three changes that, by themselves, dissolve ~80% of the
"woefully inefficient" feeling without touching anything else.

### FIX-1 (≈45 min): Status log auto-write on every dispatch (close the visibility gap)

**The problem.** `data/orchestrator_status_log.jsonl` is the surface the user
reads to know what the orchestrator is doing — the dashboard already polls
it. But entries are written by the orchestrator's MAIN THREAD ad-hoc, by
hand, between sub-agent calls. The latest entry has a JSON-escape bug
(line 12 is double-quoted — `\"ts\":\"...\"`) which means the file was
written via a bash heredoc that re-escaped already-escaped JSON. This is
the kind of thing that quietly poisons the dashboard and gets the user
asking "are you doing anything?" because the most recent event is unparseable.

**The fix.** Promote status logging from a manual write step to a
*structural* one. Specifically:

- Add `log_event(event_kind, summary, **fields)` to
  `tools/orchestrator/in_flight.py` (rename module to `state.py` so this
  is no longer just an in-flight tracker — it owns both `in_flight.json`
  AND `status_log.jsonl`). Atomic append: write to `.tmp`, fsync, rename
  into a per-line append using `O_APPEND` if available on Windows; else
  read-modify-write under a small fcntl-style lock.
- Add a high-level helper `dispatch_with_log(role, model, summary,
  expected_minutes=15)` that:
  1. calls `record_dispatch(...)` (existing)
  2. writes a `sub_agent_dispatched` status log entry with the same id
  3. returns a context-manager-style handle so the orchestrator can
     `clear_dispatch(...)` AND write `sub_agent_returned` automatically.
- Update `orchestrator_prompt.md` to require: every Agent({...}) call in
  the orchestrator main thread is preceded by `dispatch_with_log(...)`
  and followed by the `_returned` write. Make it impossible to ship a
  dispatch without a log entry by including the call shape in the
  prompt as the literal pattern.

**Acceptance.** After this fix, the dashboard's Live + Status tabs reflect
every sub-agent dispatch within 6 s (3 s poll + 3 s render) without any
hand-writing. The user no longer has to ask "what are you doing?" — they
see it on the dashboard.

### FIX-2 (≈45 min): Dashboard MVP (status stream on Live + tier-summary on Capability + drop Experiment tab)

**The problem.** The dashboard proposal (`notes/dashboard_redesign_proposal_2026-05-23.md`)
defined a 3-MVP scope worth ~2.5 hr but it has not landed. The user has
explicitly said this is the surface that replaces 30-min META snapshots
in chat.

**The fix.** Ship MVPs 1-3 from the proposal verbatim, dispatched to a
single Sonnet sub-agent with the full proposal as context. Specifically:

- `tools/dashboard/poller.py`: add the `orchestrator_status_log` SSH/local
  read (already mostly there per `_STATUS_LOG_PATH`); ensure JSON-lenient
  parser tolerates the line-12 escape bug as a parse-skip with a warning.
- `tools/dashboard/parsers.py`: add `parse_status_log` (jsonl-tolerant)
  and `extract_tier_summary(cap_md)`.
- `tools/dashboard/static/index.html`: add headline banner row at top of
  Live; add a status-stream panel to right column; rename Tests →
  Experiments; drop Experiment tab; add tier-summary banner to top of
  Capability tab.

**Acceptance.** When user opens dashboard, the Live tab shows:
- top banner: `v159 cap_map · 12✅ 6🟢 4🟡 17🔬 13❌ · GPU x% · runners 2/2`
- right column: tail of orchestrator status log with chips per event_kind
- Capability tab shows the 12✅/6🟢/4🟡/17🔬/13❌ counts above the markdown

No "Experiment" tab. Tests tab is "Experiments".

### FIX-3 (≈20 min): queue_add re-run support + cap_map dedup-block fix

**The problem.** `tools/queue_add.py` line 168-169 silently warns and
skips when a name is already in queue. This is RIGHT for accidental
double-dispatch but WRONG when Strategy has explicitly decided to re-run
(e.g., `pq_high_resolution_v1` dedup-blocked twice today per
`orchestrator_questions.md` Q2). There is no `--force` or `--rerun` flag.
Result: legitimate re-runs require manually editing `queue.json` or
renaming the experiment.

**The fix.** Three small mechanical changes:

1. Add `--rerun-as <new_name>` to `queue_add.py`: clones the entry under
   a new name (auto-suffixed if not given) and queues it. Existing entry
   is untouched.
2. Add `--allow-duplicate` to `queue_add.py`: if name already exists with
   `status` in `{done, failed, canceled}`, replace it in-place (set
   `status=pending`, reset `started_at`/etc.). If `status=running` or
   `pending`, still refuse.
3. Update `queue_add.sh` to pass these flags through from the bash
   wrapper, and update `agents/exp_dev.md` to use `--rerun-as` when the
   strategy request says "re-run pq_high_resolution_v1" or similar.

**Acceptance.** User reports two dedup-blocks today; both would succeed
with `--rerun-as pq_high_resolution_v1b` or `--allow-duplicate`. Strategy
no longer has to track "did this name already get used" — the queue layer
handles re-run semantics.

---

## (b) Per-dimension audit findings

### 1. Dispatch latency — orchestrator notifies → I act

(a) **Broken:** none that's structural.
(b) **Fragile:** `dispatch.py` polls at 2 s. Each new file in `notes/` (a
fast-growing directory) is re-scanned every cycle (`NOTES_DIR.glob("*.md")`).
At ~700 files today this is fine; at 5 000 it will start to bite. Cache the
seen set and use `os.scandir` (single dirent walk) before regex matching.
(c) **Missing:** no dedupe window for routing files written in bursts. If
exp_dev writes 5 routing files in 200 ms, dispatch emits 5 events
ordering-undefined. Adding a 500 ms batching window with a single
"routing_batch" emission would let the orchestrator dispatch a single
sub-agent with 5 file paths.
(d) **Redundant:** `dispatch.py` re-reads the dashboard snapshot every
2 s even when nothing has changed. mtime-gate the read.

### 2. Sub-agent prompt quality

(a) **Broken:** `agents/strategy.md` line 22 references
`git diff --cached --name-only` inside the prompt. The sub-agent has no
shell; this must be the agent calling Bash with that command. The prompt
should make that explicit — `run "python tools/validate_capmap_commit.py
--staged-files $(git diff --cached --name-only)"` is shell, but the agent
might mis-parse it as a Python string.
(b) **Fragile:** every agent prompt is OBSOLETED-tagged for the ASCII
constraint ("OBSOLETED 2026-05-23") but that's noise once the constraint
is dead. Strip the OBSOLETED tags. They distract from current rules.
(c) **Missing:** no agent currently writes a status_log entry at end of
its run. Per FIX-1, every agent's final step must be: call
`tools/orchestrator/state.py log_event sub_agent_returned <id> <summary>`.
(d) **Redundant:** the `Honest framing` section in strategy.md references
6+ feedback memories by ID. Sub-agents loading from disk re-read all of
these on cold start, eating context. Compress to one paragraph that
inlines the substance, not the references.

### 3. Multi-queue routing

(a) **Broken:** `queue_add_remote.sh` is a backward-compat wrapper that
always routes to `overnight_queue` — but `agents/exp_dev.md` says
"overnight_queue (fallback) — when in doubt." So the wrapper hides the
queue=field default. If a caller uses the old `queue_add_remote.sh` they
silently bypass `local_cpu_queue` routing. Either DELETE the wrapper or
make it `WARN: deprecated, defaulting to overnight_queue`.
(b) **Fragile:** the queue= header parse in `dispatch.py:parse_queue_entries`
defaults to `overnight_queue` if neither inline nor header set it. This
contradicts exp_dev.md rule 1-4 which has GPU as rule 1, not default.
Default should match exp_dev's classifier — and exp_dev should always
set queue= explicitly. Validate at queue note write time.
(c) **Missing:** no per-queue error-class handling. If SCP fails
(network) vs `--self-test` fails (bug), both surface as "exit non-zero
to user." Differentiate: SCP-failure → retry once + surface; gate-failure
→ surface immediately + dispatch exp_dev to fix.
(d) **Redundant:** `queue_add.sh` re-checks file existence locally, but
`queue_add.py` re-runs `--self-test` on the runner. The local
file-existence check is fine; the smoke skip is fine; but the comment
"runner still runs --self-test as a gate" in `orchestrator_prompt.md` is
not true — `--skip-smoke` skips smoke, not self-test. Self-test runs
ALWAYS at queue_add.py time, which is local for local_cpu_queue and
remote (over SSH) for remote queues. Update the prompt.

### 4. Queue management — dedup-by-name blocks re-runs

(a) **Broken:** the dedup is a silent WARN+skip with `print()` going to
stdout — not a non-zero exit. Caller has no programmatic way to detect.
(b) **Fragile:** see FIX-3. No `--rerun-as` or `--allow-duplicate`.
(c) **Missing:** no `tools/queue_clean.py` (proposed but never built).
A standing housekeeper that prunes `done`/`failed` entries older than 24 h
from queue.json would prevent the queue file from growing unboundedly
and reduce the chance of stale-name collisions.
(d) **Redundant:** `gated_at` timestamp on the entry but no way to
say "this is the third re-run." Add a `run_index` field that increments
on `--allow-duplicate`.

### 5. Status visibility — should writes be automatic on every dispatch?

(a) **Broken:** YES, see FIX-1. Today writes are hand-rolled and one is
already malformed (line 12 of `orchestrator_status_log.jsonl`).
(b) **Fragile:** the file is local to D:\AI but the dashboard poller (per
`poller.py:_STATUS_LOG_PATH`) reads from the same D:\AI path. That's
fine for now but if the dashboard ever runs on the remote machine the
status log needs to be either (i) synced to the runner, or (ii) the
dashboard pulled from this side. Document the assumption.
(c) **Missing:** no schema validator. JSONL is line-by-line so one bad
line shouldn't kill the file, but the dashboard parser must tolerate
malformed lines with a warning, not a crash.
(d) **Redundant:** `data/event_outcomes/` directory and
`recent_verdicts` array in dashboard snapshot are TWO sources of the
same fact. Pick one. event_outcomes is newer (post-Phase-2 direct-write)
and structurally cleaner; recent_verdicts is legacy. Plan: agents start
writing event_outcomes directly; dispatch.py keeps reading
recent_verdicts AS A FALLBACK only.

### 6. Dashboard completeness vs user need

(a) **Broken:** Experiment tab is dead. Drop.
(b) **Fragile:** Capability tab dumps raw markdown. Tier-counts banner
missing.
(c) **Missing:** the entire Status tab (orchestrator-status timeline +
audit summary + sub-agent dispatch timeline). Per dashboard proposal.
(d) **Redundant:** Tests tab has a 194-row table that is overkill for
"what's happening now" — keep it, but it's no longer the home tab.

### 7. Remote CPU runner revival — failed multiple times today

(a) **Broken:** SSH-spawned processes inherit stdin/stdout/stderr from
the SSH session. When the SSH session terminates, the child's stdio
pipes close and the runner (which writes to a log file but also has
buffered stdout) gets a SIGPIPE-equivalent on Windows. `start /B` with
`>NUL 2>&1` in the .bat *should* fix this, and `Start-Process` in the
.ps1 *should* fix this, but both have been tried and the runner doesn't
survive SSH disconnect.
(b) **Fragile:** the right approach on Windows is **Task Scheduler**, not
SSH detach tricks. A scheduled task survives SSH disconnect because it's
parented to the Windows service host, not to the SSH-spawned cmd.
(c) **Missing:** the schtasks invocation. The fix shape:
```
schtasks /create /tn "hd-cpu_runner_0" /tr "C:\dev\hd-instrument\.venv\Scripts\python.exe C:\dev\hd-instrument\experiments\runner_v2_prod.py --queue-dir C:\dev\hd-instrument\data\remote_cpu_queue --id cpu_runner_0 --idle-exit-minutes 240" /sc onlogon /ru SYSTEM /rl HIGHEST
```
Then `schtasks /run /tn "hd-cpu_runner_0"`. Survives SSH disconnect and
auto-restarts on logon.
(d) **Redundant:** both `.bat` and `.ps1` exist for the same purpose and
both have failed. Delete one (keep `.ps1`) and rewrite it to issue
`schtasks /create + /run`.

### 8. PYTHONIOENCODING runner restart

(a) **Broken:** the env-var fix was pushed but the runner process running
on marsh@home was never restarted, so new scripts that hit Windows
cp1252 stdout still crash. Patch is in the codebase, not in the live
process.
(b) **Fragile:** new scripts include `sys.stdout.reconfigure(...)` as
defense-in-depth, but old scripts and external libraries that print
emoji at module-import-time still hit cp1252.
(c) **Missing:** a runner-restart procedure documented in
`tools/orchestrator/README.md` (or wherever the runner lifecycle lives).
(d) **Redundant:** the ASCII-grep step in exp_dev's smoke gate has been
REMOVED but the OBSOLETED comments still live in agent files. Strip.

**When to schedule:** as part of FIX-7 (remote CPU revival), the same
`schtasks /change /tn "hd-overnight_runner" /tr "...python.exe -X utf8 ..."`
re-registration restarts the runner with the new env-var setup. Couples
naturally with FIX-7.

### 9. Cap_map dedup-block — queue_clean.py was proposed but not built

(a) **Broken:** see FIX-3. `pq_high_resolution_v1` was dedup-blocked twice.
(b) **Fragile:** the dedup is purely by name; status is irrelevant.
(c) **Missing:** `tools/queue_clean.py` (proposed in audit) — a 30-line
script that prunes done/failed entries older than 24 h and reports a
diff. Should run nightly via Task Scheduler (couples with FIX-7).
(d) **Redundant:** none.

### 10. Sub-agent overuse vs underuse

User flagged this 3+ times this session. Per
`feedback_structural_agent_usage_mandate.md` the rule is HARD now.
Concrete patterns that should have been agent work:

- **Reading 5+ files to "figure out" something** → dispatch an audit
  sub-agent with the file paths. This is exactly what produced
  `audit_dropped_and_review_2026-05-23.md` (correctly delegated). The
  pattern works when applied.
- **Writing 3+ files in sequence** → dispatch implementation sub-agent.
  THIS document is a borderline case — single-file audit output is fine
  for main thread; 5-file refactor is not.
- **Multi-file refactors of the dashboard** → dispatch a Sonnet
  implementation sub-agent. The dashboard MVP (FIX-2) is 4-file changes;
  do not do this in main thread.
- **Cap_map updates** → already structurally dispatched to strategy
  sub-agent. ✅
- **Lit-scan / Research drills** → already dispatched, with
  Sonnet-default per [[feedback-subagent-model-optimization]]. ✅
- **Status responses to user** → typically NO dispatch needed; read state
  files and answer. ✅

**The pattern that breaks today:** orchestrator handles a verdict event
by reading dashboard, reading routing log, reading active_priorities, and
THEN dispatching strategy. The reads-before-dispatch are 3-4 tool calls
each time. This is fine for routing decisions but it's the smell that
flags "should I have just dispatched immediately?" Per FIX-1 + structural
mandate: dispatch first, let the agent read state itself.

### 11. Audit-of-orchestrator-itself — meta-cadence missing

(a) **Broken:** today's audit caught `active_priorities` was 46 versions
stale. That audit would NOT catch itself next time because there's no
standing schedule for it.
(b) **Fragile:** PROT-008/009 catch cap_map commits. They do NOT catch
`active_priorities.md`, `experiments_backlog.md`, or any other
coordination artifact.
(c) **Missing:** a standing 4-hourly orchestrator self-audit. Spec:
- Dispatch the audit sub-agent (Opus) every 4 h of active operation.
- It reads cap_map history tail, last N strategy_decisions files, all
  `*_request_to_*` files in last 24 h.
- Output: `notes/audit_meta_<date>_<HH-MM>.md` (sortable, easy to track).
- Status log entry: `event_kind=meta_audit`.
- If 4 h pass without an audit, dispatch.py emits an
  `audit_overdue` event that wakes the orchestrator.
(d) **Redundant:** `meta_audit_cycle*.md` files exist but they're per-
cycle, not per-time-bucket. Migrate to time-bucketed naming once cycle
counter is dissolved.

### 12. User experience — every interruption is "queue empty?"

(a) **Broken:** the user has had to ask "are you ironing out bugs?" /
"queue empty?" / "still catching up?" — every interrupt is a coordination
check, never a content question. That's a structural failure of the
status surface (FIX-1 + FIX-2).
(b) **Fragile:** even with the dashboard, if status writes are manual
(FIX-1 unfixed), the dashboard goes stale and user falls back to chat.
(c) **Missing:** a "heartbeat" line in the status log every N min when
nothing has happened, so the dashboard's "last entry" never gets older
than N min. This is reassurance for the user: "system is alive; nothing
to report."
(d) **Redundant:** `orchestrator_questions.md` has 3 unanswered questions.
The dashboard surfaces them (see `/api/questions` in server.py) — but if
the user is not opening the dashboard, they don't see them. Add a
"there are 3 open questions for you" line to any orchestrator-to-user
status message until they're answered.

---

## (c) Unified refactor plan — ordered steps with dependencies + ETA

Numbered steps with `[blocks: X]` notation (X must finish first) and `[parallel-safe]` tag where it can fan out.

| # | Step | Time | Depends on | Parallel-safe with |
|---|---|---|---|---|
| 1 | Rename `tools/orchestrator/in_flight.py` → `state.py`; add `log_event()`, `dispatch_with_log()` helpers | 15 min | — | 2, 4, 5 |
| 2 | Build `tools/queue_clean.py` (prune done/failed >24h) | 15 min | — | 1, 4, 5 |
| 3 | Update `orchestrator_prompt.md` to mandate `dispatch_with_log` use; strip OBSOLETED tags from all 5 agent files | 20 min | 1 | 4, 5, 6 |
| 4 | Add `--rerun-as` and `--allow-duplicate` to `tools/queue_add.py`; propagate through `queue_add.sh` | 20 min | — | 1, 2, 5 |
| 5 | Dashboard MVP: status stream on Live + tier-summary on Capability + drop Experiment tab | 75 min | — | 1, 2, 4 (largely independent) |
| 6 | Fix dispatch.py: 500 ms batch window for routing files; mtime-gate dashboard re-read; cap NOTES_DIR scan with cache | 25 min | — | 1, 2, 4, 5 |
| 7 | Remote CPU runner revival via `schtasks` (PowerShell script rewrite + initial install command) | 30 min | — | 1, 2, 4, 5, 6 |
| 8 | PYTHONIOENCODING runner restart: schtasks re-register both overnight + cpu runners with `-X utf8` flag | 10 min | 7 | — |
| 9 | Standing 4-hourly orchestrator self-audit: add `audit_overdue` event to dispatch.py + audit sub-agent prompt at `tools/orchestrator/agents/meta_audit.md` | 30 min | 1, 6 | 7, 8 |
| 10 | Heartbeat: dispatch.py emits `heartbeat` event every 15 min (idle state); orchestrator writes `event_kind=heartbeat` to status_log | 10 min | 1, 6 | 7, 8, 9 |
| 11 | Strip redundant feedback-ID references from agent prompts; inline substance into one-paragraph rules | 20 min | 3 | 5, 7, 8, 9, 10 |
| 12 | Update `orchestrator_questions.md` surfacing: any user-facing status message includes "[N open Qs]" tail | 5 min | — | all |

**Total serial path:** 1 → 3 → 11 (55 min); 7 → 8 (40 min); 1 → 9 (45 min); 5 (75 min standalone). Critical path is FIX-2 / step 5 at 75 min if parallelized.

**Wall-clock estimate, parallelized:** 1.5 - 2 hours from go-decision to "stable orchestrator" criteria (see (e)).

---

## (d) Implementation parallelism — what to fan out

Three Sonnet sub-agents can run in parallel without conflict:

- **Agent A (state-layer):** steps 1 + 3 + 6 + 9 + 10 + 11 — orchestrator
  infrastructure. Single-author, single-file-set, no conflict.
- **Agent B (queue-layer):** steps 2 + 4 + 7 + 8 — queue + runner. Single-
  author, touches `tools/queue_add.py`, `tools/queue_clean.py`,
  `tools/orchestrator/start_remote_cpu_runner.ps1`, `queue_add.sh`.
  No overlap with Agent A.
- **Agent C (dashboard):** step 5 only — `tools/dashboard/*`. No overlap
  with A or B.

**Step 12** is a 5-min main-thread doc edit; the orchestrator does it
itself after A/B/C return.

Dispatch shape (one message, three Agent calls):

```
[Agent({A: state-layer refactor, model: sonnet, prompt: <spec>}),
 Agent({B: queue-layer refactor, model: sonnet, prompt: <spec>}),
 Agent({C: dashboard MVP,        model: sonnet, prompt: <spec>})]
```

Each gets a written spec from this document + the relevant files. None
sees the other's work mid-flight. Conflicts are inspected at merge time
in main thread (which is a 5-min review job, not a re-implementation).

---

## (e) Acceptance criteria — "stable orchestrator" definition

The orchestrator is **stable** when ALL of the following hold:

1. **Auto status:** Every sub-agent dispatch produces a
   `sub_agent_dispatched` status_log entry without any hand-write step.
   Every return produces a `sub_agent_returned` entry. Verified by
   tailing the file during one verdict event cycle.
2. **Dashboard visibility:** Opening the dashboard at any moment shows:
   - Headline banner: cap_map version + tier counts + runner state
   - Right column of Live: tail of orchestrator status log with chips
   - Capability tab: tier-summary table above the markdown
   - No Experiment tab
3. **Queue re-runnability:** `queue_add.py --rerun-as foo_v1b script.py
   --prereg foo.md` succeeds when `foo` already exists in queue with
   `status=done`. `--allow-duplicate` flag also works.
4. **Remote CPU runner alive:** `schtasks /query /tn "hd-cpu_runner_0"`
   shows status=Running; runner heartbeat in dashboard <60 s old.
5. **PYTHONIOENCODING active:** both runners have `PYTHONIOENCODING=utf-8`
   in their effective env; new utf-8-using scripts run without cp1252
   crashes.
6. **Meta-audit cadence:** A `notes/audit_meta_*` file lands within
   30 min of the first 4 h interval after refactor finish. Status log
   entry confirms.
7. **Heartbeat present:** When idle for 15 min, a `heartbeat` entry lands
   in status_log; dashboard shows it.
8. **Queue clean exists:** `python tools/queue_clean.py --dry-run`
   reports which entries it would prune; cron-able.
9. **No double-bookkeeping:** `recent_verdicts` array in dashboard
   snapshot is still populated for back-compat, but `data/event_outcomes/`
   is the authoritative new source; dispatch.py reads both and dedupes
   correctly.
10. **Agent prompts:** every agent file has been stripped of OBSOLETED
    tags and feedback-ID lists are compressed into prose substance.

When 8 of 10 hold, the orchestrator is "good enough to ship"; the user
shouldn't need to ask "what's happening" for >24 h.

---

## (f) Risks / things to NOT do

- **DON'T re-architect dispatch.py into an async/event-loop framework.**
  The 2 s polling loop is fine; the bottleneck is not detection latency,
  it's reaction latency, which is sub-agent dispatch time. Re-arch is
  scope creep.
- **DON'T move the status log to the remote machine.** Right now it
  lives on D:\AI alongside the orchestrator — same-machine read is
  cheap. Moving it adds an SSH dependency to the dashboard's most
  important panel.
- **DON'T add inotify / fswatch / file-system-events.** Polling at 2 s
  is fine for the scale of files we're producing. fswatch on Windows is
  a maintenance burden; polling is dead simple.
- **DON'T rewrite the queue file format.** It's JSON-on-disk and lots
  of code reads it. `queue_clean.py` should read/modify/write the same
  schema; adding columns is fine, changing the format is not.
- **DON'T merge `queue_add_remote.sh` into `queue_add.sh`.** The
  backward-compat wrapper is two lines; deleting it would break any
  hard-coded caller. Leave it as a thin wrapper with a deprecation WARN.
- **DON'T add a UI to the dashboard for triggering experiments.** It is
  a read-only surface by design and that's correct. The user explicitly
  separated control (chat) from observation (dashboard). Don't violate.
- **DON'T eliminate the live-session fallback path.** The migration
  status doc has a rollback plan (re-spawn a live session for any role).
  Keep it functional. If orchestrator regresses, the rollback is the
  safety net.
- **DON'T spawn the sub-agents for this plan from main thread without
  first writing this document.** Sub-agents need a clear spec, and this
  document IS the spec.

---

## (g) Policy issues — what code alone cannot fix

These remain user-side decisions, not refactor scope:

- **User noise tolerance for orchestrator turns.** Some users want every
  verdict surfaced; others want only ❌ closures and ✅ promotions. The
  current default is "every verdict gets a chat update." Refactor does
  NOT change this; it's a user preference call.
- **Chat vs dashboard for status.** The dashboard is the right surface
  for "what's happening" but the user has explicitly asked for chat
  status updates too. The compromise: chat gets the 1-3-sentence summary
  per significant event (verdict, cap_map version bump, audit
  completion). Routine sub-agent dispatch / return is dashboard-only.
- **Cycle counter dissolution.** `meta_audit_*_cycleN.md` numbering is
  vestigial from the pre-orchestrator era. Should be dissolved into
  time-bucketed naming, but that's a documentation discipline call.
- **Product session cadence.** Product is user-pull and the orchestrator
  queues `notes/product_inbox_<date>.md`. Whether the user opens it is
  their schedule; refactor doesn't touch it.
- **Cross-application probes.** Per
  [[feedback-strategy-shore-up-capabilities]] Strategy should
  periodically probe very different applications. This is a Strategy
  agent prompt nuance; orchestrator doesn't enforce.
- **Lit-scan calibration penalty.** Per
  [[feedback-lit-scan-calibration-penalty]] novel-synthesis P estimates
  should be deflated 0.15-0.25. This is a research-agent prompt
  discipline, not orchestrator code.

---

## (h) Open question to file as Q4 in orchestrator_questions.md

Should the orchestrator's structural status-log entries include the
sub-agent's full return text (verbatim) or only a 1-line summary? The
verbose version makes the dashboard's Status tab a complete narrative
record but balloons file size (estimated 200 KB/day at current dispatch
rate). The terse version keeps the file small but loses the
"what did the agent actually say" context unless the user clicks
through to the agent's decision file. Default proposal: terse summary
in status_log, with `decision_file` field pointing at the canonical
note where the full return lives.

This is the one call the user should make before steps 1 + 3 land
(it changes the `log_event` helper signature).

---

## Done-or-not-done quick reference

| Item | Status |
|---|---|
| Dispatch.py written | ✅ done |
| Sub-agent prompts (5 roles) | ✅ done |
| Multi-queue routing | ✅ done |
| Backward-compat wrapper | ✅ done |
| `in_flight.py` (basic) | ✅ done |
| Status log file | ⚠️ exists but manual-write, malformed line present |
| Dashboard read of status log | ✅ done (poller side); ❌ UI side |
| Dashboard tier summary | ⚠️ endpoint exists; ❌ UI side |
| Drop Experiment tab | ❌ pending |
| Remote CPU runner alive | ❌ dead since 2026-05-21 |
| PYTHONIOENCODING runner restart | ❌ patched not deployed |
| `queue_clean.py` | ❌ not built |
| `queue_add.py --rerun-as` | ❌ not built |
| `active_priorities.md` freshness | ✅ now v159 (refreshed today) |
| `meta_audit` 4-h cadence | ❌ not scheduled |
| Heartbeat in status log | ❌ not implemented |
| Open Q surface in chat | ❌ not structural |
