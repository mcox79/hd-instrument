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
| a cell smoked clean, then its full run read 15 min and died with an EMPTY held-out split: the corpus yields exactly 20,000 and it read all 20,000 | check every split/sample against what the source actually yields, at FULL sizes, before the expensive step | *A smoke with smaller numbers does not test the full run's arithmetic* |
| built a write gate after checking the registry; a HARD_PASS cell from 3 weeks earlier had already measured that it must fail on a weak foundation | the registry says what is BUILT; only `experiment_index.py` says what was ANSWERED -- query BOTH and quote the counts | *Two archives, two questions* |
| a "held-out" set built from a FRESH `CorpusRegistry()` overlapped the training pool 600/600; the arm read median rank 3.0 where every other measurement that day read 69-91 | a separate reader over one ordered source is not a separate sample -- draw held-out from the SAME advanced cursor, and PRINT the overlap count every run | *A fresh reader is not a held-out split* |
| an arm whose accumulator was never written (all-zero profiles) reported median rank 1.0 -- a 20x "win" -- because tied similarities never sort above the target | assert each arm's representation is non-empty before scoring; construct the EMPTY version of a winning arm and check it LOSES | *An empty representation scores perfectly on a rank metric* |
| every paired difference returned `+0.0` with CI `[+0.0, +0.0]`; the "practice" arm added unit vectors where the substrate accumulates RAW ones (mean norm 44.5), so it was 1/44th of a real read and moved the profile by cos 0.999923 | a zero-WIDTH CI is a reachability failure, not a null -- print added/base, cos-shift and ranks-changed before reading any verdict, and ADD WHAT THE SYSTEM ADDS | *A null that is exactly zero is a reachability failure* |
| ran a full 5-point sweep on divisive normalisation after quoting ORGAN_MAP §2; §3 of the same file said *"do not re-propose"* it, with an analytic proof (scalar denominator, cosine is scalar-invariant) | the prior-work check before proposing a BRAIN MECHANISM is THREE reads -- registry, `experiment_index.py`, **and ORGAN_MAP's corrections**; grep the whole file, not the row you cite | *Two archives was not enough* |
| three internal statistics (anchor margin, trace coherence, effective dimensionality) each produced a confident mechanistic claim that the held-out TASK then contradicted | a statistic the mechanism OPTIMISES is not an outcome -- it may DIAGNOSE, never DECIDE; score every lever on the same task, floors and CIs | *A statistic the mechanism optimises is not an outcome* |
| a script exited on "my manipulation failed" before the "the corpus already drifts" check below it could run; both were true, and it suppressed the informative one | a gate's THRESHOLD is not the only thing to check -- check what it EXITS BEFORE; order readings most-informative first | *Non-stationary escape, sixth gate defect* |
| a 1%-sparse arm read 1.06x the floor vs the shipped 3.09x -- apparent parity with word-counting, on two seeds -- while random noise of the same sparsity scored BETTER (14.0 vs 18.0); ~91% of pairs shared no support so their similarity tied at exactly 0.0, and the strict-inequality rank counts every tie as beaten | `norm(v)>0` is not a non-degeneracy check -- assert TIE DENSITY, report both tie conventions, and score the information-free version of any winning arm | *Non-zero is not non-degenerate* |

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
modules; **35 of 141** are reachable from the live path;

> **⚠️ "35 of 141" IS A LOWER BOUND FROM ONE PROBE, NOT A CENSUS (measured 2026-08-20).** The
> figure is an EAGER-IMPORT trace of two modules (32 top-level) plus **3 lazy imports added BY
> HAND**. Re-run today it reproduces EXACTLY -- 40 entries, 32 top-level -- **so the number is not
> stale.** But a probe that actually RUNS the substrate (read + `recall_sentence` +
> `recall_cortical` + `query`) loads **6 modules the import trace never sees**:
> `corpus_registry, cortical_recall, definitional_extraction, hippocampal_encoder,
> information_foraging, substrate`. **And it MISSES all three of the hand-added ones**
> (`pos_tagger`, `arc_parser`, `arc_labeler`), which load only on a path it did not exercise.
> **NEITHER PROBE IS COMPLETE AND THEIR UNION IS LARGER THAN EITHER.**
>
> **This is not pedantry -- it caused a real error.** `_make_definitional_gate`'s docstring said
> *"it is NOT on the live reading path"*, citing this accounting. It was faithfully quoting a
> method that **structurally cannot see a lazily-imported module** -- and `definitional_extraction`
> is now responsible for **212 of 402** banked facts on a 12,000-sentence read. **Two of the
> organs the standard trace misses are the two that this project's 2026-08-20 findings are
> entirely about.**
>
> **Rule: quote the live-closure count WITH its probe** ("35 under an eager-import trace of the two
> loop modules"), and when the question is *"is this organ live"*, RUN THE CODE THAT WOULD USE IT
> rather than consulting the number. `tools/audit_docstrings_vs_live_closure.py` does the running
> version. the live path opens ~28 MB of the ~26 GB of
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
substitution.

**AND THE REPAIR HAS ITS OWN LESSON, WHICH IS WORTH MORE THAN THE ENCODING RULE.** The first repair
script detected damage with a regex over "characters that look like mojibake", fixed **9 lines**,
and reported *"mojibake remaining: 0"* **using that same regex**. The real damage was **56 lines**.
A mangled 🚨 decodes to `ð Ÿ š ¨`, and two of those code points fall outside the range the pattern
allowed — so the detector could not see them, and neither could its verification.

**That is standing discipline 3 — A CHECKER SHARING A FLAW WITH WHAT IT CHECKS HIDES IT — for the
fifth recorded time.** Two rules follow, and they generalise well past encoding:

1. **Detect by ROUND TRIP, not by pattern.** A line is damaged iff `line.encode("cp1252")` then
   `.decode("utf-8")` succeeds and *changes* it. That cannot share a blind spot with the damage,
   because it makes no assumption about what damage looks like.
2. **Verify with a POSITIVE control, never only an absence check.** *"No mojibake found"* shares
   the detector's bug; *"the character 🚨 is present in the file"* does not. Absence tests inherit
   every blindness of the thing that measures them.

`scratch/fix_status_encoding2.py` is the worked repair: round-trip detection, iterated until
stable, verified against the characters that must be present afterwards.

## TWO ARCHIVES, TWO QUESTIONS -- THE REGISTRY DOES NOT TELL YOU IF THE QUESTION IS ANSWERED

**Owner, 2026-08-19: *"I want to know how you missed that surprise experimental data - I thought we
had this all consolidated and known at this point? What else are we missing?"***

**THE INCIDENT.** I proposed building an error-signal write gate, ran the prior-work check, found
`hdlab/predictive_coding.py` already implemented it, and correctly called the next step a WIRING
rather than a build. The cell then failed. The owner remembered prior work on novelty detection;
`tools/experiment_index.py query "novelty"` returns **17 cells**, `"surprise"` returns **28**, and
one of them -- `exp_ingest_gate_strong_foundation_novelty_v2`, HARD_PASS, 2026-07-16 -- **had
already measured that novelty detection collapses to chance on a weak foundation.** It predicted
my result three weeks before I ran it.

**THE FAILURE IS SPECIFIC AND IS NOT "I FORGOT TO SEARCH".** I ran a prior-work check every time.
I ran the WRONG ONE:

| question | the archive that answers it |
|---|---|
| *Does the tool already exist?* | `data/capability_registry.jsonl`, `hdlab/` |
| ***Has this question already been ANSWERED?*** | **`tools/experiment_index.py query "<kw>"`** |

**I checked the CODE inventory and called it a prior-work check. It is not one.** The registry
tells you whether something is BUILT. It cannot tell you whether the experiment was already RUN
and what it FOUND -- and a built organ with a landed negative beside it is exactly the case where
building again is most wasteful.

**AND THE STANDING RULE ITSELF POINTS AT THE WRONG FILE.** Non-negotiable 5 says *"Query
data/capability_registry.jsonl BEFORE building"*. I followed it to the letter and still missed a
HARD_PASS that answered my question. **The rule names the code archive and is silent on the results
archive.**

**Rule: before building OR wiring anything, query BOTH, and quote the counts.** Not "I checked" --
the actual line, because `experiment_index.py` prints rows scanned before results and that is what
makes silence distinguishable from absence.

**Measured the same day, for everything else I had built without checking:** `"coverage"` **120
cells**, `"projection"` **102**, `"trace"` **78**, `"cortical"` **9**. Four diagnostics and a cell
built that day, none of them preceded by a results-archive query. *The answer to "what else are we
missing" is not a feeling; it is a number you can print in one command.*

## A SMOKE WITH SMALLER NUMBERS DOES NOT TEST THE FULL RUN'S ARITHMETIC

**Measured 2026-08-19.** `exp_cortical_read_consolidated_v1` smoked clean (exit 0), then its full
run read for ~15 minutes and died on its own summary line with
`TypeError: must be real number, not NoneType`. Every arm had scored `None`, meaning ZERO items.

The cause was corpus arithmetic, not logic. The cell takes `n_read + 6*n_items` sentences and
splits them into a read half and a held-out half. **`simplewiki`'s handle yields EXACTLY 20,000
sentences**; the full run asked to read 20,000 and hold out 1,800 more, so the held-out split was
**empty**. The smoke used 2,000 + 360, which fits inside 20,000 comfortably — **so the smoke could
not have caught it, at any level of care.**

**Rule: any quantity a cell SPLITS, SAMPLES FROM, or ASSUMES IS AVAILABLE must be checked against
what the source actually yields, at FULL-RUN sizes, BEFORE the expensive step.** Smoke and full
differ in exactly the numbers that make this class of bug possible, so smoke passing is not
evidence about it.

Two guards, and both belong in the cell rather than in a note:

1. **A precondition immediately after acquisition, before the read**, that raises naming the
   ACTUAL numbers — "corpus yielded N, reading M leaves K held out, J required". Fail in seconds
   and legibly, not after 15 minutes and with a `TypeError` in a print statement.
2. **A separate guard for the semantic version of the same failure**: enough items exist but none
   is answerable (here: held-out sentences mentioning none of the consolidated terms). Scoring
   that as zero would be a measurement error, so refuse to score instead.

**Verify a new guard with a POSITIVE CONTROL — run it on the numbers that actually broke** and
confirm it fires. A guard nobody has seen fire is a guard nobody has tested.

*This is the "could this experiment have succeeded?" question — which redirected this session's
plan three times — applied to resource arithmetic rather than to mechanism. It is the same
question and it is cheaper than every other way of finding out.*

## A STATISTIC THE MECHANISM OPTIMISES IS NOT AN OUTCOME -- SCORE LEVERS ON THE TASK

**Measured three times on 2026-08-20, in three disguises, each time producing a confident claim that
the task metric then refused.**

| internal statistic | what it said | what the TASK said |
|---|---|---|
| anchor **margin** (top-1 minus top-2) | pooling traces is worse than one trace -> *"accumulation is the problem, 4th time"* | the sum beats any single trace by **+13.0, CI [+6.0, +17.5]** |
| trace **coherence** | narrative is 2.67x less consistent -> a mechanism-shape problem | the mechanism was doing what its own model predicts; nothing was recoverable |
| **effective dimensionality** | our code is 4-12x too diffuse -> the projection is the defect | an ordinary text encoder sits there too; attribution withdrawn |

**The failure mode is specific and seductive: the mechanism is TUNED to maximise the statistic, so
the statistic moves readily, looks mechanistic, and explains everything.** Margin is literally what
`canonicalize` optimises -- **measuring it after selecting on it is circular, and I did exactly that
once before catching it.**

**RULE: a candidate lever is scored on the SAME held-out task, floors and CIs as every other result.
An internal statistic may DIAGNOSE — it may never DECIDE.** *This is the measurement-side twin of the
existing "a cheap probe may MEASURE, it may never SET DIRECTION".*

**The cheap check that catches it: before believing a statistic, ask what the TASK does under the
same intervention.** If they disagree, the task wins and the statistic was a mechanism artifact.
*Three of this session's more confident claims died to that one question.*

## TWO ARCHIVES WAS NOT ENOUGH -- **READ ORGAN_MAP'S *CORRECTIONS*, NOT ONLY ITS PINNED TABLE**

**Measured 2026-08-20.** I proposed divisive normalisation over a population pool, justified it by
quoting `notes/ORGAN_MAP.md` §2 (*"graded competition implemented BY the normalisation pool, not a
hard argmax"*), queried `experiment_index.py` and the capability registry, found nothing, and built
and ran a full five-point sweep. It came back inert.

**§3 of the SAME FILE says, verbatim: *"Do not re-propose 'apply divisive normalisation to fix the
argmax.'"*** — with the analytic reason: the Carandini & Heeger pool index ranges over other
**neurons at the same moment**, so the denominator is a **scalar for the whole representation**, and
**cosine is invariant to a scalar.** The mechanism cannot move a cosine ranking. ORGAN_MAP had
already recorded a NULL for it (+0.0018, CI [−0.0030, +0.0065]) and identified what was actually
implemented as efficient-coding adaptation (Laughlin 1981; Fairhall 2001).

**The prior-work habit had a hole exactly the shape of the ones it was built to close.** *Two
archives, two questions* covers "does the tool exist" (registry) and "has this been answered"
(`experiment_index.py`). **Neither covers "has the brain reference itself already ruled this out."**

**Rule: the prior-work check before proposing a BRAIN MECHANISM is THREE reads, not two.**

| question | where |
|---|---|
| Does the tool already exist? | `data/capability_registry.jsonl`, `hdlab/` |
| Has this question already been ANSWERED? | `tools/experiment_index.py query "<kw>"` |
| ***Have we already been WRONG about this mechanism?*** | **`python tools/organ_map_cite.py <ORGAN_ID>`** — greps the WHOLE file and prints constraints BEFORE the entry |

**THE THIRD READ IS NOW A TOOL, BECAUSE THE RULE FAILED TWICE ON THE SAME FILE.** 2026-08-20 I
quoted `ORGAN_MAP` §2 to justify divisive normalisation while §3 said *"do not re-propose"* it.
**2026-08-21 I quoted F5's `BRAIN'S MATH` row all session and never read line 1440 in the same file
-- "F5/F6 -- queue behind step 4" -- under a heading reading *"recorded so it is not started by
accident."*** Same file, same rule, same failure, two days apart.

`tools/organ_map_cite.py` has **no call signature that returns the math row alone**: it prints every
line naming the organ, with scheduling / prohibition / correction lines FIRST, plus the file-wide
standing prohibitions. Self-tested against the exact line that was missed. *Same escalation as
`rank_with_ties.py` and `replication_gate.py`: when a caution written as prose has been violated,
move it into the code path where the unsafe usage is unrepresentable.*

**A pinned equation tells you what the brain computes. The corrections tell you what we already got
wrong about it — including analytic impossibility results that no experiment needs to re-derive.**
*Quoting one section of a document is not reading it.*

## A NULL THAT IS *EXACTLY* ZERO IS A REACHABILITY FAILURE, NOT A RESULT

**Measured 2026-08-20.** A retrieval-practice cell returned `TEST - STUDY +0.0, 95% CI [+0.0, +0.0]`
and the same for every other pair. **A confidence interval of exactly zero width is not a null --
it means the intervention never reached the thing being scored.**

The cause was a units mismatch inside my own arm. The substrate accumulates the **raw** context
vector (`_sums[lemma] += ctx_vec`), and those vectors have **mean norm 44.5** (measured, n=599).
My "read it again" arm added the **unit-normalised** vector. So a practice episode was **1/44th of
an actual read**, the whole practice phase came to **0.85% of the accumulated profile**, and the
profile turned by `cos = 0.999923`. The arm labelled *study-type practice* was not practice.

**THE DIAGNOSTIC, AND IT BELONGS IN ANY CELL THAT PERTURBS AN EXISTING REPRESENTATION** — run it
BEFORE reading the verdict:

    mean base profile norm
    mean added magnitude / base norm      <- relative SIZE of the intervention
    mean cos(updated, original)           <- did the representation TURN at all
    how many scored items CHANGED RANK    <- did it reach the SCORER

Before: `0.0085 / 0.999923 / 61 of 300`. After using the raw vector: `0.4271 / 0.9158 / 252 of 300`.
Same code, same question — one was unanswerable and reported a clean-looking null.

**Rule: when an arm is meant to imitate something the system already does, ADD WHAT THE SYSTEM ADDS.
Read the accumulation line in the source and match it, units included.** An arm that normalises where
the substrate does not is a different experiment wearing the right label.

*Related failure, opposite sign: an arm can also be too LARGE to be meaningful. The same three
numbers catch that — `added/base` near or above 1.0 means the practice phase overwrote the reading
phase rather than modifying it.*

## AN EMPTY REPRESENTATION SCORES *PERFECTLY* ON A RANK METRIC -- ASSERT THE ARM IS NON-EMPTY

**Measured 2026-08-20.** A divisive-normalisation arm scaled each write by a term's response, and
an uninitialised profile responded **0.0**. So the first write was `0 * trace`, the accumulator
stayed **exactly zero forever**, and every term's profile was the zero vector.

**It reported median rank 1.0 -- `0.05x` the counter, a twenty-fold "win" -- at every sweep point.**
The mechanism is arithmetic, not luck: ranking is `sum(sims > sims[target])`, all-zero profiles make
every similarity tie at 0, nothing sorts strictly above the target, so the target "wins" every item.
**The emptier the arm, the better it scores.** Effective dimensionality printed `inf`, which was the
only visible tell, and it sat in a column labelled "descriptive only".

Three things, and the third is the general one:

1. **ASSERT THE REPRESENTATION EXISTS BEFORE SCORING IT**, per arm, per point:
   `alive = sum(norm(acc[t]) > 1e-9 for t in names)`; refuse if `alive < 0.5 * len(names)`. Fail
   LOUD with the counts in the message. Verified with a positive control on the numbers that broke
   it -- 0 of 4 non-zero, guard fires.
2. **A NEUTRAL INITIAL VALUE IS PART OF THE DESIGN, NOT A DETAIL.** The docstring *claimed* empty
   profiles "respond at the pool mean"; the code used 0.0. **The prose and the code disagreed and
   the prose was never executed.** Where a rule multiplies, the identity element is 1, not 0.
3. **THE GENERAL FORM: ASK WHAT SCORE A BROKEN ARM WOULD GET.** Any metric where "no information"
   and "perfect information" produce the same output is a metric that cannot fail safely. Rank-based
   scores tie-break in favour of the target; similarity thresholds pass everything at zero; ratios
   divide by zero into `inf` and sort first. **Before trusting a winning arm, construct the empty
   version of it and check that it LOSES.**

*This is the same shape as the held-out leak below -- a suspiciously good number in the arm you
hoped would win -- but arriving from the opposite direction: there the data was too good, here the
model was too empty. Both were caught by the number disagreeing with every other measurement of the
same quantity that day.*

## A BOARD QUESTION CARRIES ITS CONTEXT **IN THE QUESTION TEXT**, NOT IN A SIDE FIELD

**Owner, 2026-08-20, clarifying an earlier instruction: *"When I asked you to add context to
questions I mean in the question itself."*** Said after questions were filed with a one-line ask in
`question` and the actual context pushed into `--why` / `--rec`, or split with a
*"(Detail follows; the one-line ask is above.)"* seam.

**Why the side fields do not work as context:** `--why` and `--rec` are rendered in SEPARATE
sections of the reading pane and as SEPARATE columns in the table, so the owner reads the question
first, on its own, with nothing to interpret it by. A question that only makes sense after scrolling
to a different field is a question they have to reconstruct before they can answer it.

**Rule: `question` must stand alone.** Someone reading only that field should get the situation, the
number with its units in words, and what it costs -- without reading anything else. `--why` is then
what is BLOCKED, and `--rec` is the recommendation plus **the risk of that recommendation**. Those
two supplement; they never carry the setup.

This compounds with the standing plain-language rule (the owner has said four times that the writing
is too jargon-heavy to act on, and returned two board questions unanswered for that reason). **A
question they cannot act on is not a question -- it is a decision taken unilaterally while appearing
to consult.**

## `experiment_index.py` RETURNED A SILENT ZERO FOR MULTI-WORD QUERIES -- THE SAME DEFECT AS THE TOOL IT REPLACED

**Measured 2026-08-20. FIXED, with a self-test -- run `python tools/experiment_index.py --self-test`.**

Matching was literal substring, so a query with a SPACE could never match a cell name with an
UNDERSCORE. **`query "active growth"` returned 0 against a LANDED HARD_PASS cell named
`exp_breadth_foundation_active_growth_loop_ud_ewt_v1`.** Every multi-word query was structurally
unable to match any cell name -- and it failed the way that costs most, with a clean `0 matching
cells` that reads exactly like "no prior work exists".

Measured on one afternoon's prior-work checks -- **5 false negatives in 12 queries**:

| query | literal | normalised |
|---|---|---|
| **pattern separation** | **1** | **12** |
| gap driven | 0 | 7 |
| active growth | 0 | 2 |
| growth loop | 0 | 2 |
| frequency weight | 0 | 1 |

**WHAT IT COST, CONCRETELY: a DG pattern-separation diagnostic was designed, launched and run partly
on the strength of "1 cell, 0 landed".** The truth was 12 cells, 9 landed, including
`exp_dg_pattern_separation_mcscript_purity_v1` **HARD_FAIL** (purity 0.1013 vs a 0.1999 baseline)
and `exp_selfplay_dg_pattern_separation_xfit_v1` **HARD_FAIL_REPRESENTATION_INSUFFICIENT_REDIRECT_
EXOGENOUS** (DG improved the metric by 0.015). **The archive had already answered the question, and
that second verdict name -- redirect to exogenous information -- is the same conclusion the day's
fidelity synthesis reached independently a month later.**

Three points, and the third is why this section exists at all:

1. **SINGLE-WORD queries were never affected**, so conclusions drawn from them still stand
   (`"moral"` and `"fable"` really are 0). Multi-word conclusions from before this fix are void.
2. **The fix folds `_` and `-` to spaces on BOTH sides**, and the self-test asserts the three
   spellings return EQUAL counts, plus a known-present and a known-absent control.
3. **CLAUDE.md already documents this exact failure mode for `director_kb_query.py` -- "it runs,
   costs 40-50s, and produces nothing while reporting success" -- and the replacement tool shipped
   with its own version of it.** *A tool that can return zero without proving it CAN return non-zero
   is not a prior-work check. Any tool relied on to establish ABSENCE needs a known-present positive
   control wired into it, not into the habits of whoever runs it.*

## A RULE IN THIS FILE DID NOT STOP ME REPEATING THE FAULT TWICE THE SAME DAY -- USE `tools/rank_with_ties.py`

**Measured 2026-08-20. THREE false results in one day, all from `1 + sum(scores > scores[target])`:**

| | optimistic | truth |
|---|---|---|
| DG at 1% sparsity | 18.0, "parity with word-counting" | random noise scored **14.0**; 89.4% of similarities exactly 0.0 |
| "never picks an available synonym, 775 of 775" | 100% miss | a random picker also scores 0 (P(zero) = 0.64 / 0.85) |
| first-order co-occurrence | 21.0 | **100.0 pessimistic**; 92.2% of items tied, 79.2% of the column zero |

A STRICT inequality meeting a score distribution with mass on one value counts every tie as BEATEN,
so **the less a representation knows, the better it scores.**

**THE PART THAT MATTERS FOR HOW RULES GET WRITTEN HERE: the rule "report both tie conventions" was
added to this file on the MORNING of 2026-08-20, and I then failed to apply it to the next two
scripts I wrote that same day.** A rule in a document is a habit; a habit is not a guard.

**So the guard moved into a function.** `tools/rank_with_ties.py` returns a `RankResult` carrying
`optimistic` / `midpoint` / `pessimistic` / `n_tied` / `suspicious` -- **there is no call signature
that yields a bare rank.** Self-tested against all three real failures above plus a negative control
(a tie-free field must NOT be flagged, or the guard cries wolf and gets ignored).

**Rule: any rank-based comparison uses that helper. If `optimistic` and `pessimistic` disagree
materially, the optimistic number is not a result** -- report the midpoint or fix the representation
so the ties go away.

*Corollary worth generalising past ranks: when the same class of error recurs, stop writing the
lesson down and put it in the code path that can enforce it.*

## NON-ZERO IS NOT NON-DEGENERATE -- A *SPARSE* ARM BREAKS A RANK METRIC THE SAME WAY AN EMPTY ONE DOES

**Measured 2026-08-20, and the guard that should have caught it is the one directly above -- written
by the same person, the same week, for the EMPTY case, while building the arm most exposed to the
SPARSE case.**

A dentate-gyrus pattern-separation arm (`dg_separate`, `expand_dim=1024`, `sparsity=0.01`) took the
held-out word-recall task from **3.09x the co-occurrence floor to 1.06x** -- apparent parity with
word-counting for the first time in the project, reproduced on two seeds. **It was an artifact.**

`k = round(0.01 * 1024) = 10` non-zero components. Two independent 10-subsets of 1024 slots are
disjoint with probability `(1 - 10/1024)^10 ~= 0.91`, so **~91% of candidate/query pairs have a dot
product of EXACTLY 0.0**. The rank statistic is `1 + #{sims > sims[target]}` -- a STRICT inequality
-- so whenever the target also scores 0.0, **every one of those ties counts as BEATEN**.

**The refutation needed no corpus and took seconds: construct the MEANINGLESS version of the winning
arm and check whether it WINS.**

| arm (286 candidates, 300 probes) | optimistic | pessimistic |
|---|---|---|
| **random 10-sparse noise -- ZERO information** | **14.0** | 272.0 |
| the real DG@0.01 arm | 18.0 / 15.0 | -- |
| random dense noise (control) | 143.0 | 143.0 |
| **every profile IDENTICAL (degenerate extreme)** | **1.0** | 286.0 |

Noise beat the real arm, and reproduced the whole sweep shape across k. The harness was fine --
positive control `query == profile` scored rank 1.0 under both conventions. **The sparsity was the
defect, not the scorer.**

Three rules, and the third is the general one:

1. **ASSERTING `norm(v) > 0` PER ITEM IS NOT ENOUGH.** That guard passed at `alive = 286 of 286`.
   For any arm that sparsifies, thresholds, quantises or masks, ALSO assert **tie density**: the
   fraction of candidates whose similarity to the query is exactly equal to the target's. Print it.
2. **REPORT BOTH TIE CONVENTIONS WHENEVER TIES ARE POSSIBLE** -- optimistic (ties beaten),
   pessimistic (ties beating), and the midpoint. A result that exists only under the optimistic
   convention is a tie-breaking result, not a ranking result. *The measurement bar already says
   "report tie conventions both ways"; this is what it costs to skip it.*
3. **THE GENERAL FORM: BUILD THE INFORMATION-FREE VERSION OF YOUR WINNING ARM AND SCORE IT.** Empty,
   constant, shuffled, or random-with-the-same-shape -- whichever degeneracy your mechanism can
   approach. If it scores well, the metric cannot fail safely in that regime and no number from that
   regime means anything. **This is cheap, needs no data, and catches the failure BEFORE the
   expensive run rather than after it.**

*Note what did NOT catch it: two seeds agreeing. The artifact is a deterministic property of sparse
codes, so it reproduces perfectly. Replication is not a defence against a metric defect.*

## FOUR SINGLE-SEED WINS PUBLISHED IN ONE SESSION -- USE `tools/replication_gate.py`

**Measured 2026-08-20. Four of my own claims withdrawn in one session, every one the same shape:
ONE SEED PRODUCED A CLEAN-LOOKING NUMBER AND I LED WITH IT.**

The worst case in full, because it shows why judgement is not the fix. A blend of the accumulated
profile with the term's own looked-up definition scored **16 ranks better** than the profile on seed
7, with both information-free controls failing to beat the profile. It was written up, committed, and
reported. Then:

| | seed 7 | seed 101 | seed 13 |
|---|---|---|---|
| BOTH - PROFILE | **-16.0** | -1.0 | -5.0 |
| profile + **random vector** | +23.5 | **-8.0 (BEAT the treatment)** | +5.0 |
| profile + **wrong** definition | +3.5 | +9.0 | **-4.0 (TIED the treatment)** |

**A random vector beat the right definition on one seed and the wrong definition tied it on
another.** The effect also swung **16x** in magnitude across seeds and flipped between strata.

**THE RULE ALREADY EXISTED IN THREE PLACES** -- MEMORY.md, this file, and *my own limits section of
the note whose headline I then retracted*, written before the disconfirming seed ran. **A rule in a
document is a habit; a habit is not a guard.** This is the same escalation the tie rule got: written
down on the morning of 2026-08-20, violated twice the same day, then moved into `rank_with_ties.py`.

**So the guard is a function.** `replication_verdict(effects, controls=..., lower_is_better=...)`
returns `SINGLE_SEED_HYPOTHESIS` / `ARTIFACT_CONTROL_MATCHES` / `INCONSISTENT_SIGN` /
`UNSTABLE_MAGNITUDE` / `REPLICATED`. **There is no call signature that returns a pass from one seed**,
and passing `controls=` makes it check whether an information-free arm reproduced **half** the effect
on any seed.

**Rule: any cross-seed claim goes through that helper, and the verdict string is quoted in the
write-up.** Self-tested (`--self-test`) against the real failure above, against the single-seed
moment it was published, against a sign flip, against the 16x spread -- **and against a genuine
stable effect that it must NOT flag**, because a guard that flags everything gets ignored.

**It says REPRODUCIBLE, never GOOD.** The measurement bar (CI-separated margin over the strongest
floor actually RUN) still applies on top. Verified both ways on real data the day it was written: it
returns `ARTIFACT_CONTROL_MATCHES` for the withdrawn result above and `REPLICATED` for the phrase-
floor result that survived (4/4 same sign, 1.2x spread, no control within half the effect).

*The generalisable half, and it is the day's most useful finding: **EVERY CAUTION WRITTEN AS PROSE
THAT DAY WAS SUBSEQUENTLY VIOLATED; EVERY CONTROL WRITTEN AS CODE CAUGHT SOMETHING.** Write the
control into the script, not the caution into the prose.*

## A FRESH READER IS NOT A HELD-OUT SPLIT -- CHECK OVERLAP, DO NOT INFER IT FROM THE CONSTRUCTION

**Measured 2026-08-19.** A probe answering the owner's "one textbook or many?" built its held-out
set with a brand-new `CorpusRegistry()`, on the reasoning that a fresh registry is a separate object
from the one the substrate read through. It is. **Its handles also start at sentence one -- which is
exactly where the substrate had just been reading.** Measured directly: **600 of 600 "held-out"
sentences were already in the substrate's own pool. A 100% leak.**

**The number it produced was `OURS median 3.0` against a counter's `2.0`.** Every comparable
measurement this session had our arm at 69-91 against a counter at 15-20. A thirty-fold improvement
appeared, and it appeared in the arm testing a hypothesis the owner had just proposed. **The fix
restored `OURS 91.0 / COUNTER 19.5` -- which is itself the positive control on the diagnosis.**

Three things, in order of how much they cost:

1. **INDEPENDENT OBJECT != INDEPENDENT DATA.** Two readers over one ordered source, both starting at
   the beginning, return the same sentences. Draw the held-out slice from THE SAME cursor the
   training read advanced, so "what comes next" means it.
2. **COMPUTE THE OVERLAP AND PRINT IT, EVERY RUN, EVEN WHEN IT SHOULD BE ZERO.** One line:
   `sum(1 for s in held if s in seen)`. It is cheaper than the reasoning required to convince
   yourself it must be zero, and unlike that reasoning it cannot be wrong.
3. **A SMALL RESIDUAL LEAK GETS EXCLUDED AND COUNTED, NOT TOLERATED AND NOT USED TO BIN THE ARM.**
   The many-corpus arm leaked 416 of 15,914 (2.6%) because small corpora get exhausted and their
   handles wrap to the start. Dropping those and reporting the count is the honest move; refusing to
   score the whole arm throws away a valid measurement, and keeping them silently is the bug above
   in miniature.

**The general form: a suspiciously good number in the arm you were hoping would win is a leak
hypothesis before it is a result.** The strongest tell here was not statistical -- it was that the
number disagreed with every other measurement of the same quantity taken that day.

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
