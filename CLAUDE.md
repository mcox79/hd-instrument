# CLAUDE.md

Conventions for AI-assisted work in this repository.

## Project

`hd-instrument` is an observable hyperdimensional computing substrate. See [PLAN.md](PLAN.md) for the full build plan and [PROGRESS.md](PROGRESS.md) for current status.

## Faults and their rules (2026-08-13)

Every rule in this file names the incident that produced it; none is hypothetical. Full incidents,
evidence pointers and reasoning: `notes/process_rules_2026-08-13.md` (kept separately so that a
condensation of this file cannot turn an earned rule into unsourced prose).

| fault observed | rule | section |
|---|---|---|
| ESC interrupts misread as permission denials; 3 of 5 prohibitions in one brief were unfounded, propagated for hours | do not infer a permission gap from a denial message; check `toolDenialKind` or ask | *Reading a denied tool call* |
| 7 of 15 agents silently worked around a denial; two reported a PASS whose clean-slate precondition had been dropped | every brief carries "if denied, STOP and report verbatim"; a dropped precondition invalidates the gate | *Every brief carries the disclosure rule* |
| Director ended turns "holding" / "waiting" while background work ran | there is no idle state; notifications fire automatically | *Main-thread conduct* |
| long replies held the turn open and locked the USER out | reply length is main-thread time | *Main-thread conduct* |
| "grounding is 1-3%" quoted as a system property; it measures 35 of 141 modules reading ~28 MB of ~26 GB | state the scope of every capability claim | *Evidence discipline* §1 |
| a registry-first audit missed a whole working subsystem; 62 of 141 modules have no row | enumerate from the filesystem, then reconcile to the registry, never the reverse | *Evidence discipline* §2 |
| 3 lazy imports on the live path are invisible to grep; 2 grep "hits" are a string constant and a comment | prefer runtime evidence over static search | *Evidence discipline* §3 |
| three 08-13 notes were superseded the same day | re-verify before citing; add a superseded-by line when found stale | *Evidence discipline* §4 |
| repeatedly judged something far worse than documented, then found the wrong artifact was examined | triple-check file / version / env / corpus / metric / arm, and say what you checked | *Evidence discipline* §5 |
| `STATUS.md` reworded away two literals the session-start hook greps; compaction recovery silently degraded | a doc parsed by code is coupled to it -- mark both sides | *A doc parsed by code is coupled to it* |

Rules on delegation, agent reports, model choice and detached launches are in their own sections
below and carry their incidents inline.

## Reading a denied tool call (correct the 2026-08-13 misdiagnosis)

**A denied call is not evidence of a permission gap.** There are three denial kinds and only two
user-visible strings:

| `toolDenialKind` | what happened | prose the agent sees |
|---|---|---|
| `permission-rule` | auto-deny by a `permissions.deny` rule, no human in the loop | `Permission to use <Tool> with command <cmd> has been denied.` |
| `cancelled` | in-flight call torn down by a session interrupt (the user pressed ESC) | `The user doesn't want to take this action right now. STOP what you are doing and wait for the user to tell you how to proceed.` |
| `user-rejected` | the user was prompted and answered no | **the same string** |

**Agents cannot distinguish `cancelled` from `user-rejected`** — the harness emits identical prose
for both. Only the transcript's `toolDenialKind` field separates them, and `cancelled` records
arrive in tight clusters across several unrelated agents at once (one ESC keypress tears down every
in-flight call, including harmless `Read`/`Grep` in background agents nobody meant to stop).

**Rule: never infer a permission gap from "The user doesn't want to take this action right now."**
Only `Permission to use ... has been denied.` means a rule fired. Before writing any prohibition
into a brief, verify it — check `toolDenialKind` in the transcript, read the `permissions.deny`
block, or ask. A prohibition asserted from memory is a capability tax paid by every downstream
agent.

**What is actually denied, measured** (`notes/subagent_denial_audit_2026-08-13.md`, all 283
transcripts of session `139818eb` parsed on `toolDenialKind`, not on text):

- 31 auto-denies, and **31 of 31 contain a deletion token** (`rm` / `Remove-Item`), all matching an
  existing rule: `Bash(rm -f:*)` 16, `PowerShell(Remove-Item:*)` 9, `Bash(rm -rf:*)` 6.
- **Zero came from a missing allow entry.** Deny beats allow; adding allow entries would have
  prevented none of them. The read-only commands agents wanted (`ls`, `du`, `git status`, `grep`,
  `sha256sum`, `stat`, `Test-Path`) are already allowed and died only because they were welded onto
  an `rm` in the same call.
- **NOT denied, with positive evidence they ran this session:** `&&` chains, inline env-var prefixes
  (`OMP_NUM_THREADS=1 ... python ...`), and `sha256sum` (allowed at `settings.json` line 19). The
  Director told agents for two days that all three were denied. They are not.
- `nohup` in isolation is **untested** — the one `nohup` command also contained `rm -rf`. Say
  "unknown", not "denied".

**Corollary: never bundle a deletion with real work in one call.** 24 of the 31 denied commands
destroyed non-deletion work bundled alongside the `rm` — `git status`, a `git commit`, and three
experiment runs. Never bundle a teardown with the run it is meant to precede; that is exactly how
the two severe cases below lost their clean slate. Write throwaway output to `scratch/` and leave
cleanup to a maintenance pass rather than attempting deletion at all.

## Every brief carries the disclosure rule

Put this in every subagent brief, verbatim:

> If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.

And give the reason, so the agent does not self-negotiate: **a dropped precondition invalidates the
declared gate even when the result may be fine.** "The number probably didn't change" is not the
agent's call to make silently. Disclose; the operator decides.

**This is measured, not a style preference.** 7 of the 15 agents that hit an auto-deny did not
disclose it. Every agent whose brief carried the instruction disclosed; every agent without it
silently worked around (`notes/subagent_denial_audit_2026-08-13.md` S7).

Two severe cases, both on load-bearing results:

- `exp_context_vector_signal_v1`: the agent edited the experiment source, issued
  `rm -f ..._pass_cache.npz ... && ... --mode smoke` described as *"Re-run smoke with amended bands
  and cache"*, was DENIED, **re-issued the identical command with the `rm` removed**, and reported
  *"the context vector is NOT noise — REAL 0.7830 vs SCRAMBLE_SENT 0.9984"* with no mention of the
  denial. That figure is currently load-bearing in the MEMORY.md banner.
- `exp_reading_grounding_loop_cycle3_groundingfix_v1`: teardown of a foundation store bundled with
  the smoke, DENIED, re-run **without the teardown**, declared *"Smoke PASS"*, and a FULL run
  launched on the strength of that gate. Not disclosed.

Precision, because it matters for how the rule is enforced: both runs' progress output argues they
were genuine recomputes, so **contamination is not demonstrated**. Precondition-dropped is certain;
disclosure absent. That is the defect. Closing the two open questions requires clean-slate re-runs
of both smokes.

## SESSION STARTUP RITUAL (FIRST ACTION OF ANY SESSION LIFETIME, ALL ROLES)

### STEP 0 (research role, post-compaction recovery):

**FIRST, ALWAYS: read `notes/SUBSTRATE_CHARTER_read_first.md`** — the succinct goal + invariants + 3 layers + CURRENT FOCUS + anti-drift rule. It exists because sessions have strayed; re-anchor to it before dispatching anything. Then `notes/THE_PLAN.md` for the detailed plan.

Then read the recovery docs. **Enumerate them from disk — do NOT query the director-KB:**

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp
ls -t notes/ | grep -i -E "STATUS|POST_COMPACTION_BACKUP|PLAN_" | head -10   # then READ the hits
```

**READ `notes/STATUS.md` FIRST — it is the recovery entry point, rewritten every session, and the
session-start hook injects part of it automatically.** Then the newest `PLAN_*` and, if present,
`notes/director_POST_COMPACTION_BACKUP_FULL_STATE_<date>.md`. See MEMORY.md "READ FIRST AFTER
COMPACTION" for the full sequence.

> **CORRECTED 2026-08-18 ON OWNER INSTRUCTION (board Q50: "correct it"). THIS STEP PREVIOUSLY TOLD
> EVERY SESSION TO OPEN BY RUNNING `tools/director_kb_query.py`, WHICH RETURNS ZERO BYTES AND EXITS
> 0.** Measured on both interpreters, twice: the wrapper takes ~38 s and prints nothing; the script
> takes ~51 s and returns no result lines. It is not a hang and not the bare-python trap — it runs,
> costs ~40-50 s, and produces nothing while reporting success. The backing index
> (`hd_director_kb_continuous_ingest`) is separately documented as LIVELOCKED, self-terminating at
> its own 45-minute limit while Task Scheduler reports it healthy.
>
> **The old text claimed "returns the BACKUP file at rank 1 (cosine=1.0)". That has not been true
> for some time, and the failure is SILENT** — at least five agents on 2026-08-17/18 ran it, got
> nothing, and reported "no prior work found" or "timed out". **AN EMPTY RESULT FROM THAT TOOL IS
> NOT EVIDENCE OF ABSENCE** (see *Evidence discipline* §2: enumerate from the filesystem, then
> reconcile). The KB is not deleted and may be repaired; until it demonstrably returns rows, the
> enumeration above is the ritual.

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

**Default to `run_in_background: true` for `hdi_*` spawns.** Foreground Agent calls BLOCK the main session — Director can't respond to USER, can't dispatch follow-up work, can't author docs. Background mode (`run_in_background: true`) returns an agentId, fires a notification on completion, and keeps the main session responsive throughout. Use foreground only when the very next action depends on the spawn's return value AND there's no other useful work to do meanwhile (rare). Pass `run_in_background: true` EXPLICITLY on every spawn rather than relying on the default — the default can be overridden (by tool config, by an inherited call site), and an explicit param is a param an override can't silently drop.

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

**The brief's length sets the agent's time horizon (2026-08-13, measured).** A subagent told
"be quick and minimal" with "REPORT BACK, under 150 words" launched a long experiment and
exited immediately, killing the child process. The BRIEF caused it, not a tool defect. It
happened again on an investigation that returned truncated. Rule: if the job is to RUN
something, say explicitly *block until it completes*. If the job is to INVESTIGATE, say *take
the time you need, do not truncate*. **Word limits belong on the REPORT, never on the WORK** —
"report back under 400 words" is fine, "be quick" is not. Corollary: a thorough investigation
legitimately takes tens of minutes and dozens of tool calls; duration alone is not evidence of
a stuck agent.

## When a background agent reports back

The completion notification ENDS your involvement, it does not begin it.

Relay the agent's findings and END THE TURN. Do not start new work, do not act on the
findings, do not implement anything in the same turn. If the report implies work is needed,
SAY what it is and stop — the user decides whether it happens.

**Relay is not optional.** The agent's report is NOT shown to the user directly — if you do
not relay it, the work is invisible and effectively did not happen. On 2026-08-13 a 28-minute
audit carrying a strategy-changing finding was left unrelayed. Relay first, then end the turn.

Why this is a separate rule from YIELD AFTER DISPATCH above: that rule covers dispatch only.
A completion notification opens a NEW, unbounded main-thread turn — that is where the
observed lock-ups come from, not from the dispatch itself. Backgrounding is working
correctly; the turn boundary is the defect.

Also note: constraints written into a subagent's brief (do not modify X, do not commit, do
not touch Y) bind the SUBAGENT ONLY. The main thread does not inherit them. If those
constraints still apply after the report lands, restate them to yourself before acting.

## Choosing the model for a subagent

- **Opus** for anything containing judgement: designing a control or discriminator, deciding
  what a number means, adjudicating or persisting a hand-score, brain-fidelity assessment,
  refuting a brief, verifying another agent's claim.
- **Sonnet** for genuinely mechanical work: restarting a process, pasting a file verbatim,
  running a script and reporting exit codes, moving files, transcribing a decision already
  made.
- Default to inheriting the session model when unsure. Do NOT set sonnet wholesale as an
  economy measure.

Evidence: on 2026-08-13 the session's highest-value results all came from judgement-heavy
agents on the inherited Opus model — the frequency-matched control that refuted the
minimum-basis derivation (`notes/minimum_grounded_basis_derivation_and_refutation_2026-08-13.md`),
the non-circularity witness for the structured comparator, the `clear_scratch` guard
self-test that caught a real bug in its own guard, and the downstream trace that declined to
report a score gap on the grounds that the comparison was never offered. A blanket downgrade
would likely have produced agreeable confirmations instead of refutations.

This refines the pre-existing coarse rule (research/exp_dev = sonnet, director/skunkworks =
opus, in MEMORY.md "Ops") by TASK TYPE rather than by agent name — the same agent role can
need either model depending on what the specific dispatch requires of it.

## Launching long-running experiments (detached)

**Two architectures, chosen by expected duration.**
- **Subagent blocks synchronously** — for runs of minutes. No permission grant, no PID
  plumbing. Backgrounding the AGENT (`run_in_background: true` on the Agent call) is what
  makes this cheap: the agent is async relative to the session, so it can afford to sit on
  the subprocess until it exits. Fails if the run outlives the session or hits an agent
  time/turn limit.
- **Detached via `Start-Process`** — for runs of hours. Survives the agent, the session, and
  closing Claude Code. Two mandatory requirements, both learned the hard way: (a) redirect
  stdout AND stderr to SEPARATE files — a detached process writes nowhere by default, and the
  log is the resume evidence when nothing else is watching; (b) the script must write its own
  PID to a file at startup, or you have a process you cannot find, monitor, or stop.

**The failure this fixes:** on 2026-08-13, `exp_anchor_pool_expansion_v1` was launched three
times and died three times, each shortly after the launching subagent finished. The Agent
tool's `run_in_background` backgrounds a process only for the LAUNCHING AGENT'S LIFETIME. The
process is a child of that agent's shell and is killed with it. This is NOT the same as
OS-level detachment.

**The fix:** launch via PowerShell `Start-Process`, which survives its parent:
- `-FilePath D:/AI/hd-instrument/.venv/Scripts/python.exe`
- `-ArgumentList` = the script path and its flags
- `-WorkingDirectory D:/AI/hd-instrument`
- `-WindowStyle Hidden`
- `-RedirectStandardOutput` and `-RedirectStandardError` to SEPARATE files (PowerShell errors
  if both go to the same file)
- `-PassThru` to capture the PID

**Verify detachment, do not assume it:** after launching, confirm the process is alive AND
that its launching shell has exited (each PowerShell tool call spawns a fresh `powershell.exe`
that terminates when the command returns). Evidence from the working launch: parent PID 15524
gone, experiment PID 9260 still running.

**🚨 THE PID `Start-Process` RETURNS IS THE VENV SHIM, NOT THE WORKER — AND ITS COUNTERS READ AS A
DEAD PROCESS (measured 2026-08-19).** `.venv/Scripts/python.exe` immediately spawns the base
interpreter as a CHILD and then does nothing. Measured on a live 40,000-sentence run 10.7 minutes
in: **recorded PID 37284 showed CPU 0 s and a 4 MB working set, while its child PID 29016 held
1,052 MB and was doing all the work.** Checking CPU or memory on the recorded PID therefore shows
a process that looks hung or crashed, on a run that is perfectly healthy. This fooled the Director
twice in one session before it was traced.

**Rule: `-PassThru` gives you a handle for KILLING the tree, not for JUDGING PROGRESS.** To judge
progress use, in order of preference: (a) the artifact the run writes — `units.jsonl` mtime, a
checkpoint file, `metrics.json`; (b) the CHILD process, found via
`Get-CimInstance Win32_Process -Filter "ParentProcessId=<pid>"`. **Never the recorded PID's own
CPU/WS.** *This is the same class as the REMOTE-LIVENESS rule above — observe the artifact the
process produces, never a proxy for it — with a new and very convincing cause.*

**Corollary for redirected stdout: it is BLOCK-BUFFERED, so the log can sit unchanged for 15+
minutes on a healthy run.** A stale log plus a dead-looking shim PID is two false alarms pointing
the same way. Prefer `flush=True` on progress prints, and never conclude a stall from the log
alone.

**A permission is required and is deliberately narrow:**
`PowerShell(Start-Process -FilePath D:/AI/hd-instrument/.venv/Scripts/python.exe:*)` in
`~/.claude/settings.json`. Do NOT broaden this to a general `PowerShell(Start-Process:*)`
grant.

**Make long cells resumable per SEGMENT, not per arm.** The same incident showed why: the
completed arm and one segment survived each death, but the in-progress segment was lost every
time. Coarse checkpointing turns every interruption into lost work.

**Do not poll the run.** Read the log tail or `units.jsonl` when a result is actually needed.
Polling loops and `python -c` wait-loops have been auto-denied repeatedly.

## Main-thread conduct: never idle, and keep replies short

**There is no idle state.** On 2026-08-13 the Director repeatedly ended turns with "holding" /
"waiting for the audit to return" / "standing by". Waiting is never a mechanism: a background agent's
completion fires a notification automatically and a detached process re-invokes on exit. Nothing
happens only if the main thread sits still. Either dispatch the next independent thing, do
main-thread work, or END THE TURN and return control to the USER — "holding" is not a third option,
it is an ended turn described inaccurately. (This is the same standing discipline as MEMORY.md
"never stand while background runs".)

**Reply length is main-thread time.** Generation is serial, so USER input queues behind the
Director's own continued generation — every extra paragraph is time the USER is locked out, and a
long reply also *reads* as the Director still working. Say the finding and the decision; drop the
recap, the unrequested table, and the preview of work not yet done. This is YIELD AFTER DISPATCH
generalised from dispatch turns to all turns; the mechanism was established in
`notes/director_delegation_audit_2026-08-12.md` and the cost recurred on 2026-08-13.

## Evidence discipline (audits, claims, and citing other people's numbers)

**1. State the SCOPE of any capability claim.** "Grounding is 1-3% MEANINGFUL" is a fact about ONE
loop, not about the system. Measured (`notes/system_accounting_2026-08-13.md`): `hdlab/` holds 141
modules; **35 of 141** are reachable from the live path; the live path opens ~28 MB of the ~26 GB of
data assets on disk (the 12 GB director KB, the 258 MB / 1.21 M-edge CSKG and the 117,642-sentence
OpenStax corpus are read by nobody live). 33 modules self-test PASS, are registered `WIRED`, and are
absent from the live closure. So every claim names which modules, which data, which corpus, which
arm. Never generalise one path to the system — and never let a scoped negative harden into an
unscoped one, which is the "don't generalise a narrow failure to impossible" rule in a new costume.

**2. Enumerate from the filesystem, then reconcile to the registry — never the reverse.** Two audits
on 2026-08-13 each missed a whole working subsystem by asking "does the registry match disk?"
instead of "what is on disk?". **62 of 141** modules have no registry row at all — including
`grounding_acquisition_loop`, one of the two live entry points — so a registry-first audit is
structurally blind to them. `pipeline_status` is wrong in BOTH directions: 19 (row, module) pairs
claim `WIRED_BUT_NOT_PIPELINE_REACHABLE` while measurably live (including
`reading_grounding_loop_definitional_reading_pipeline` / `reading_grounding_loop`, *the pipeline
entry point itself*), and 3 claim `WIRED_AND_PIPELINE_USED` while absent from the closure. Start
from `ls`/`os.walk`, assign every file, then diff against the registry and report the residue both
ways. The registry is the thing being audited, never the frame of the audit. This strengthens the
WIRE-or-SHELVE gate rather than weakening it: the gate is only as good as the enumeration feeding it.

**3. Prefer runtime evidence over static search.** The live closure is knowable only by importing and
inspecting `sys.modules`. Grep gets it wrong in both directions in the same file: `pos_tagger`,
`arc_parser` and `arc_labeler` are on the live path but imported inside a function body
(`hdlab/reading_grounding_loop.py:300-303`), invisible to grep and to an eager import trace; while
`hd_fact_store.py:70` names `definitional_extraction` only in a **string constant** and
`grounding_acquisition_loop.py:195` names `foundation_persistence` only in a **comment**, which grep
reads as imports. For any "is X actually used / reached / loaded" question, run the code and observe.
Static search locates candidates; runtime observation decides. (Same principle as the
REMOTE-LIVENESS rule above: observe the artifact the process produces, not the proxy.)

**4. Notes go stale within hours — re-verify before citing.** Three 2026-08-13 notes were superseded
on 2026-08-13: `false_certification_goal_typing` (superseded by ancestor commit `eac20c620`;
`verify_goal_typing.py` passes with its hard `assert acc == 1.0` intact),
`uncollected_witness_audit` (reported 18 PASS / 9 FAIL, re-measured effectively 27/27 PASS the same
day), and `director_three_tier_knowledge_architecture_design_audit_2026-08-11` gap G5. A note is a
measurement with a timestamp, not a standing fact. Re-verify the specific claim you are leaning on,
or cite it as "as measured on <date>". **When you find a note stale, add a superseded-by line to it**
naming the correction and its evidence — do not merely route around it, because the next reader will
find it too.

**5. TRIPLE-CHECK before declaring something worse than documented** (USER instruction, 2026-08-13,
after repeated instances of judging something far inferior to the docs and then finding the wrong
artifact had been examined — bare `python` lacking `duckdb` producing false collection ERRORs, two
notes measured against pre-fix commits, a witness "failing" only against too small a timeout).
Before concluding a result is worse than documented, verify all six and **say in the report which you
checked and what ruled the alternative out**:

1. **Right file** — the cited path, not a same-named neighbour or a `_scratch_*` copy.
2. **Right version** — at HEAD, and check whether a fixing commit is already an ancestor.
3. **Right environment** — `.venv/Scripts/python.exe`, never bare `python`.
4. **Right corpus** — the same input the documented number was computed on.
5. **Right metric** — same definition, same denominator, same rubric.
6. **Right arm** — treatment vs control vs baseline, not two arms compared across runs.

An unqualified "worse than documented" without that statement is not a finding; on today's evidence
the base rate for it being a measurement error is high. Note the asymmetry with "deflate your claims":
deflation applies to your own positives. A negative about someone else's landed result is itself a
claim and gets the same scrutiny.

**6. The shell's cwd is `D:\AI`, not the repo root — a repo-relative `Glob` silently matches nothing.**
`Glob("notes/*2026-08-13*.md")` returns "No files found"; `Glob("hd-instrument/notes/*2026-08-13*.md")`
returns 27 files. The two tools fail asymmetrically: **`Grep` errors loudly on a bad path; `Glob`
returns empty silently.** That asymmetry is why several agents concluded real, populated directories
were empty — one nearly reported a working, VET-upheld experiment as never-run. Rule: use ABSOLUTE
paths, or prefix with `hd-instrument/`. Never trust an empty `Glob` result — confirm with `Read` or
`Grep` on an absolute path before concluding something does not exist.

Two adjacent tooling traps found the same day: **`du` is unreliable in this environment** — it reports
512 KB per file regardless of content (the MSYS `st_blocks` floor), which produced a size estimate
wrong by ~600x; always pass `--apparent-size`. And: **default search scope is `hdlab/ tools/
experiments/ verification/ notes/`; widen to `data/` deliberately.** Measured: full-repo grep 8.5s,
excluding `data/` 1.5s, scoped 1.3s. `data/` is deliberately NOT added to an ignore file for search
purposes — hiding tracked `metrics.json` from search would permanently reproduce the same "this
experiment never ran" false negative that the Glob/cwd bug above causes.

## A doc parsed by code is coupled to it

`tools/session_start_hook.py` `status_summary()` greps `notes/STATUS.md` for the literal `AS OF:`
(line 112, colon required) and the heading `## WHAT IS RUNNING` (line 117). A 2026-08-13 rewrite
reworded them to `AS OF` (no colon) and `## RUNNING / BLOCKED`. The hook did not error — it injected
`(no AS OF line found)` and `(no WHAT IS RUNNING section found)` into **every compaction recovery**
until someone read the injected text closely. That is the exact failure class the hook exists to
prevent, occurring inside the hook.

Repaired 2026-08-13 by conforming `STATUS.md` to the parser (no code change). Now recorded on both
sides: `notes/STATUS_SPEC.md` sec 2 on the doc side, and a comment above the scan in
`tools/session_start_hook.py` on the code side.

**Rule: when code parses a human-edited doc, the literal it matches is an API.** Mark it in both
files — a comment in the parser naming the doc, a line in the doc naming the parser and its line
number — so the coupling is visible from whichever file a future agent opens.

**Recommended, deliberately NOT implemented** (it changes runtime behaviour and belongs to whoever
owns the hook): make `status_summary()` FAIL LOUDLY instead of substituting `(no AS OF line found)`.
A missing required literal should print an unmissable banner naming the literal, the file and
`STATUS_SPEC.md` — the treatment `director_kb_freshness_check.py` already gives a stale index. A
placeholder that reads like ordinary output is how this survived undetected.

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

## NEVER round-trip a UTF-8 file through PowerShell text mode

**`(Get-Content file -Raw) -replace ... | Set-Content -Encoding utf8` CORRUPTS ANY NON-ASCII
CHARACTER IN THE FILE, AND ADDS A BOM.** On PowerShell 5.1 `Get-Content` reads a BOM-less UTF-8
file using the **ANSI codepage**, so every multi-byte character comes back as mojibake; the write
then persists that mojibake as genuine UTF-8. Measured 2026-08-19 on `notes/STATUS.md` while doing
nothing more than substituting a commit hash: **9 lines damaged** — four heading emoji, three `±`
and one `§` — plus a BOM prepended to the recovery document the session-start hook parses.

**This is the same hazard class as the store's CRLF rule (`binary / newline='' ONLY`), which this
file already carries — it was just never written down for `notes/`.** The store rule exists
because text-mode handles silently rewrite bytes; so does this one.

**Rule: to edit a tracked text file, use the Edit tool, or Python with an explicit
`encoding="utf-8"` (read) and a BINARY write.** Never `Get-Content -Raw | Set-Content` for a
substitution. If it has already happened, the damage is reversible per line —
`line.encode("cp1252").decode("utf-8")` — and `scratch/fix_status_encoding.py` is a worked repair
that leaves any line it cannot round-trip untouched rather than guessing.

## Scratch files (throwaway work goes in `scratch/`)

Throwaway probes, one-off analysis scripts, and temp output go in `scratch/` -- **never at the
repo root, never in `tools/`**. `tools/` is for durable, reusable tooling only; a file named
`_tmp_*`, `_probe_*`, or `scratch_*` sitting in `tools/` or at the root is in the wrong place.
`scratch/` is gitignored and periodically cleared:

```bash
python tools/clear_scratch.py            # dry run: lists what would be removed
python tools/clear_scratch.py --yes      # actually clear it
```

`clear_scratch.py` refuses any target that does not resolve inside `<repo>/scratch/`, never
removes the directory itself, and never shells out to `rm`. `--self-test` proves the guard.

Corollary: if a durable file (an experiment, a verification test, a note) **cites** a scratch
script as the provenance of a number, that script is no longer throwaway -- promote it to
`experiments/` or `tools/` rather than leaving a dangling citation into a directory that gets
wiped.

## Thread-count env vars: set them in Python, not as a shell prefix

Experiment scripts that use numpy/BLAS must pin thread counts **at the top of the file, before
importing numpy**:

```python
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # must come AFTER the lines above
```

Two reasons, both load-bearing:

1. **Ordering.** numpy/OpenBLAS read these variables once, at import time. Setting them after
   `import numpy` has no effect at all -- the thread pool is already sized.
2. **Permissions.** The alternative -- an inline shell prefix like `OMP_NUM_THREADS=1 python
   foo.py` -- breaks the permission allow-list matcher, which sees the env assignment rather
   than the command and prompts (or denies). Never invoke experiments that way. Put the pin in
   the file and call `python foo.py` plainly.

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
