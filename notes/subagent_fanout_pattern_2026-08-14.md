# Subagent fan-out pattern -- implementation + verification, 2026-08-14

Owner directive (verbatim, quoted in full in the dispatch prompt) specified four mechanisms:
tools-restricted scan agents, `dontAsk` permission mode, the disk-fragment result pattern, and
a Stop-hook fragment-count gate -- plus an assessment of Agent Teams. Evidence base:
`notes/agent_usage_practices_audit_2026-08-14.md` (committed `625da6276`): 235 spawns measured,
0% batched, 85% of completions unrelayed within 30 chars, yield-after-dispatch compliance
WORSE after the enforcement hook landed (63.9% pre-install violation vs 97.4% post-install),
and a concrete incident of a chain spawning six children with no surviving parent.

Built this cycle without spawning any subagent, per explicit instruction. Every claim below is
either measured in this session (state HOW), pulled from an existing dated note (cited, not
re-verified), or explicitly marked NOT VERIFIED with the reason the verification path was
unavailable.

## 1. Verification-path constraint, stated up front

The owner's directive asks to "add [a frontmatter key], confirm the fleet still resolves, and
report what you observe" for `permissionMode: dontAsk`, and to re-verify the `background`/
`isolation`/`model`/`tools` claims empirically rather than assume them. The task also
explicitly **forbids spawning any subagent**. These two instructions are in tension: the only
way this harness exposes "does the agent-type list still resolve" is a system-reminder that is
injected passively -- observed once, at the very start of this conversation, immediately after
the first tool-result batch -- and does **not** refresh on ordinary tool calls (tested:
created/edited an agent-definition file, then issued a plain `Bash` call; the reminder did not
reappear). Calling the `Agent` tool itself, even just to observe whether a `subagent_type`
resolves, is a spawn attempt and is exactly what's forbidden. **Resolution: I did not attempt a
live spawn-based test.** Where a live test would have been the only way to know, I say so below
rather than asserting a result I did not observe. Two things I *could* verify without spawning,
described in full in section 3.

## 2. Fragment convention (`.claude/scan-out/`)

- `D:/AI/hd-instrument/.claude/scan-out/` -- created. Contains only `README.md` (tracked);
  `*.json` fragments are gitignored.
- `.gitignore` -- added, mirroring the existing `data/literature_cache/` negation pattern
  (verified precedent: `git ls-files scratch/` shows `scratch/README.md` is tracked despite a
  bare `scratch/` ignore rule; `data/literature_cache/README.md` uses an explicit `!` negation,
  which is what I copied):
  ```
  .claude/scan-out/*.json
  !.claude/scan-out/README.md
  ```
  Verified live: wrote a probe `.json` into the directory, `git check-ignore -v` confirmed it
  matched the ignore rule; `git check-ignore -v .claude/scan-out/README.md` produced no
  match-as-ignored (the negation line was the reported match, i.e. the file is tracked).
  Probe file removed afterward (plain `rm <file>`, no flags -- not denied; the global deny
  list only covers `rm -f`/`rm -r`/`rm -rf`, confirmed by reading
  `~/.claude/settings.json` and `.claude/settings.local.json` directly).
- Schema (v1) documented in two places, deliberately duplicated: `.claude/scan-out/README.md`
  (tracked, discoverable by anyone opening the directory) and the module docstring of
  `tools/scan_out_collect.py` (tracked, next to the code that enforces it). Required fields:
  `agent`, `task`, `timestamp` (UTC ISO-8601), `findings` (list; each finding requires `claim`
  + `evidence`). Optional: `source`, `detail` per finding, top-level `summary`.
- Evidence tags, matching this project's existing literature discipline (not invented new
  vocabulary): `ESTABLISHED` / `CONTESTED` / `SINGLE-STUDY` / `FAILED-REPLICATION`. A finding
  with a missing or off-list tag is not rejected -- the collector assembles it and flags it
  inline (`[UNTAGGED]` / `[INVALID-TAG:<value>]`) so the omission is visible to a reader rather
  than silently dropped (same "don't silently drop a signal" instinct as the rest of this repo's
  guard patterns).
- `tools/scan_out_collect.py` -- reader/assembler + retention tool. Guard pattern **copied, not
  reinvented**, from `tools/clear_scratch.py` (`assert_under_root` / `_real` /
  `GUARD_ENABLED` / `--_disable_guard`), per the explicit instruction. `--self-test` result
  (`.venv/Scripts/python.exe tools/scan_out_collect.py --self-test`), all 10 checks PASS,
  including a **negative control** that disables the guard and confirms the delete then
  succeeds (proving the guard, not some other check, was doing the refusing) and a malformed-
  JSON fragment reported as `UNREADABLE` rather than raising:
  ```
  [self-test] PASS guard refused out-of-tree root: ...
  [self-test] PASS victim file survived
  [self-test] PASS guard refused root-itself: ...
  [self-test] PASS guard accepts a legitimate scan-out child
  [self-test] PASS negative control: disabled guard DID allow the delete ...
  [self-test] PASS assembled note names the fragment file
  [self-test] PASS assembled note carries the ESTABLISHED tag
  [self-test] PASS assembled note flags the untagged finding
  [self-test] PASS assembled note carries the task text
  [self-test] PASS malformed fragment reported as UNREADABLE, not raised
  [self-test] RESULT: PASS
  ```
  Retention: `python tools/scan_out_collect.py --clear [--yes] [--older-than-days N]` (dry-run
  by default, same convention as `clear_scratch.py`).

## 3. Agent frontmatter audit -- `.claude/agents/` + the `hdi_*` fleet

Enumerated by listing the directory directly: `ls .claude/hdinstrument-relative agents/` ->
5 files (`exp_dev.md`, `orchestrator.md`, `research.md`, `skunkworks.md`, `testbed.md`), each
read in full. This is the complete `hdi_*`-backing set; there is no other agent-definition
directory in the repo (`.claude/` at repo root has only `agents/`, `settings.json`,
`settings.local.json`, `skills/`).

**Finding: none of the 5 existing roles are genuinely read-only scan roles.** Every one's own
"Role" section names a write/commit/dispatch duty central to its job: `research` maintains
`data/director_plan.json`; `exp_dev` authors cell files and dispatches to
`local_cpu_queue`; `skunkworks` performs A5-gated `PartitionedStore` writes and git commits
(and already carries a restricted `tools:` line for a *different* reason -- role-separation
from dispatch, not read-only-ness); `orchestrator` pushes to origin and writes
`orchestrator_status_log.jsonl`; `testbed` (this role) edits dashboard/hook/monitor code and
commits it. Applying `tools: Read, Grep, Glob` to any of the five would break the stated
function of that role. **I did not touch any of the 5 existing fleet files' frontmatter** --
the risk of leaving the fleet unloadable outweighs forcing a restriction that doesn't fit, and
per instruction I have no live way to confirm a frontmatter edit didn't break loading (see
section 1).

**Action taken instead: one new agent definition, `.claude/agents/scan.md`** (`name: scan`),
purpose-built for the pattern that actually produced tonight's 2000-4000-word-report problem
(literature scans and codebase surveys, historically dispatched as `general-purpose` -- 139 of
235 spawns per the audit, the largest single bucket). Frontmatter:
```yaml
tools: Read, Grep, Glob, WebSearch, WebFetch, Write
permissionMode: dontAsk
```
Reasoning for the tool list, stated in the role file itself so a future reader doesn't have to
reconstruct it: `Bash` is excluded because the audit's own denial data
(`notes/subagent_denial_audit_2026-08-13.md`, cited in `CLAUDE.md`) shows **31/31** auto-denies
that session carried a deletion token in a `Bash` command -- removing `Bash` removes the
mechanism, not just the symptom. `Edit`/`NotebookEdit` are excluded so the role cannot touch
source. `Agent` is excluded so it cannot spawn a child (directly answers the "six children, no
surviving parent" incident). `Write` is the one exception, needed for the fragment convention
itself (writing to `.claude/scan-out/<name>.json`) -- **this is a deliberate, disclosed
departure from the owner's literal "tools: Read, Grep, Glob"**, because that literal list
cannot both avoid prompts *and* satisfy "each scan writes its full findings to
`.claude/scan-out/<name>.json`" in the same role (a write-nothing agent cannot write a
fragment). I judged satisfying the actual end-to-end pattern (write the fragment, return one
line) more valuable than a literal 3-tool list that would require a *different* mechanism to
get the findings to disk. Flagged here rather than silently deviating.

### Empirical status of the specific frontmatter-key claims

| claim | status | evidence |
|---|---|---|
| `model` and `tools` are valid, working frontmatter keys | **VERIFIED, live, this session** | The "Available agent types" system-reminder shown automatically at the start of this conversation (before any edits) printed, verbatim, per-agent tool lists reflecting the current files on disk: `hdi_skunkworks: ... (Tools: Read, Edit, Write, Glob, Grep, Bash, NotebookEdit)` matching `skunkworks.md`'s `tools:` line exactly, and `(Tools: All tools)` for every role with no `tools:` key. This is passive confirmation from the live harness, not an assumption. |
| `permissionMode` is a real, working **agent-definition frontmatter** key (distinct from the deprecated Agent-tool-call `mode` param) | **VERIFIED via installed SDK source, not via live dispatch** | `sdk-tools.d.ts` inside the installed `@anthropic-ai/claude-code@2.1.229` npm package (`C:\Users\marsh\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\sdk-tools.d.ts`, line 521-523) documents the `AgentInput.mode` parameter itself as *"Deprecated; ignored. Subagents inherit the parent session's permission mode; **agent-definition frontmatter may override it**."* This is the exact same sentence visible in this session's own `Agent` tool schema for the `mode` parameter (top of this conversation). It directly names agent-definition frontmatter as the real override path, and confirms the enum includes `dontAsk`: `"acceptEdits" \| "auto" \| "bypassPermissions" \| "default" \| "dontAsk" \| "plan"`. |
| `dontAsk` behavior ("auto-denies prompts while explicitly allowed tools keep working") | **NOT VERIFIED live this session** | Requires an actual dispatch to a `dontAsk`-mode agent that hits a would-prompt call; forbidden by the no-spawn constraint. Applied to `scan.md` on the strength of the owner's directive + the confirmed-real key, with the caveat below stated in the role file itself. |
| `background:` in agent-definition frontmatter causes total load failure (not merely "no effect") | **Cited from `CLAUDE.md`, dated 2026-08-12, not re-verified this session** | `CLAUDE.md` "Agent-teams / frontmatter findings" section: *"All five `hdi_*` agents vanished from the available types the moment it was added to one definition, and returned when it was removed."* I did not re-run this live (would require a spawn-adjacent test path I don't have, and re-breaking the fleet even briefly to re-confirm a documented, dated, concretely-evidenced incident was judged not worth the risk). Did NOT add `background:` to any file. |
| `isolation:` has no effect in agent-definition frontmatter | **UNVERIFIED, flagged as inherited-from-a-disproven-methodology** | The only source is the `CLAUDE.md` "Superpowers plugin" section's single sentence: *"`background` and `isolation` are NOT real keys -- `background: true` was added to an agent definition as a test and had no effect."* That sentence's claim about `background` was later corrected in the *same file* to "FAIL TO LOAD" (not "no effect") -- the two claims share one disproven test methodology, and `isolation` was never independently re-tested after the correction. Separately: `isolation` **is** a real, documented parameter -- but of the `Agent` **tool call** (`AgentInput.isolation: "worktree" \| "remote"`, confirmed in `sdk-tools.d.ts` and in this session's own `Agent` tool schema), not of the `.md` YAML frontmatter. Whether the *same* key name inside frontmatter does anything is genuinely unknown from any source available to me. I did not add `isolation:` to `scan.md` or to any fleet file, given this. |

A secondary, inconclusive data point: `strings`-style grep of the installed `claude.exe` binary
turns up a literal array containing `"tools","disallowedTools","color","permissionMode",
"maxTurns","initialPrompt","memory","background","isolation","observer","observerMessage",
"observeSubagents",...` -- `background` and `isolation` both appear as recognized identifiers
somewhere in the compiled app. I am **not** citing this as proof either way: the same string
table mixes in what look like routine/scheduled-agent config keys (`"routine",
"attachStallRespawns","reattachEnv","worktree","ownershipToken"`), so it's ambiguous whether
this is the `.md`-frontmatter schema, a different schema that happens to share field names, or
both. Noted for whoever next has spawn budget to actually test it.

## 4. This session's actual permission mode

**Determined empirically, live**, not assumed. `PowerShell(Get-CimInstance Win32_Process
-Filter "ProcessId=$PID")`, walked up to the launching `claude.exe` process (PID 26544,
`--resume=139818eb-7f83-457e-928d-a8db02a0214d`, matching this session's own
`CLAUDE_CODE_SESSION_ID` env var exactly) -- its full command line includes
**`--permission-mode default`**. (Separately visible on the same host: four *other*, unrelated
`claude.exe` processes -- the VS Code extension's own sessions, different session IDs --
running `--permission-mode auto`; those are not this session and do not apply here.)

**Consequence for the `dontAsk` route:** the owner's caveat is "if your parent session is in
auto mode, the subagent inherits auto mode and the frontmatter value is ignored." This
session's parent is in **`default`** mode, not `auto` -- so per that caveat, and per the SDK's
own docstring ("agent-definition frontmatter may override" the inherited mode), the `dontAsk`
route on `scan.md` should be **live, not inert**, when dispatched from this parent. This is the
strongest claim I can make without a live dispatch: consistent with all available documentation
and the measured parent mode, but the actual runtime behavior of a `dontAsk` agent hitting a
would-prompt call was not observed this session (see table above).

## 5. Stop hook fix -- `data/hooks/staging/stop_hook.py`

**This is the live, currently-wired Stop hook** (confirmed by reading
`C:\Users\marsh\.claude\settings.json` directly: `"Stop": [{"matcher": "",
"hooks": [{"command": "...pythonw.exe D:/AI/hd-instrument/data/hooks/staging/stop_hook.py"}]}]`)
-- despite its own module docstring still saying *"STAGING ONLY -- not yet registered."* That
docstring is stale (a doc-vs-wiring mismatch of exactly the kind `CLAUDE.md` already has a rule
about, "a doc parsed by code is coupled to it" -- except here it's the reverse, code IS wired
but the doc claims otherwise). Flagged, not fixed (out of this task's scope; noted for whoever
owns that file next).

Added `_scan_out_gate(repo_root, session)`: a new signal alongside the existing `have_unread`
(notes-dir unread inbox) and `have_watchdog_ping` checks, wired into the same GUARD-3
block/continue logic. **Fragment count is the gate, and zero is the mandatory early exit**,
directly implementing the owner's caveat: no `.claude/scan-out/` directory, or an empty one,
returns `(False, None)` immediately -- a scan still running in the background has written
nothing yet, so it can never look like a block-worthy signal. Only a fragment that has
*already landed* (the scan finished) and is newer than this session's own
`data/last_scan_collected_<session>.timestamp` mark triggers a block, mirroring the existing
unread-inbox idiom (first-run doesn't retroactively block on history; the mark advances on
block so the same fragment doesn't reblock every cycle).

Added a `--self-test` entrypoint (`python data/hooks/staging/stop_hook.py --self-test`,
checked before the file even tries to read stdin) proving both directions against an isolated
tempfile root -- **never touches the real repo's `data/hook_state/`**:
```
[self-test] PASS no scan-out dir -> early exit 0 (no block)
[self-test] PASS empty scan-out dir (scans in flight) -> no block
[self-test] PASS pre-existing fragment on first check -> no retroactive block
[self-test] PASS new completed fragment after the mark -> blocks, names the fragment
[self-test] PASS after mark is advanced, same fragments no longer block
[self-test] RESULT: PASS
```
Also smoke-tested the real hook-protocol entrypoint end to end against a throwaway session name
(`fanout_infra_test_session`, not a real session): `echo '{}' | ...stop_hook.py` (no session
resolvable) exits 0 with no output; `echo '{"stop_hook_active": false}' |
...stop_hook.py fanout_infra_test_session` twice in a row both exit 0 with no block decision
printed (correct: `.claude/scan-out/` currently holds only `README.md`, zero fragments, so the
new gate stays silent, matching "scans legitimately in flight never block"). Test-session
artifact (`data/last_processed_fanout_infra_test_session.timestamp`) removed afterward in its
own isolated call.

## 6. Agent Teams assessment (recommendation only -- no migration performed)

**Load-bearing fact this assessment turns on: Agent Teams is not a prospective migration here
-- it is already the live architecture for the `hdi_*` fleet**, confirmed from this exact
session's own environment: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`,
`CLAUDE_CODE_TEAM_NAME=session-71ab49cc`, `CLAUDE_CODE_AGENT_NAME=team-lead`,
`CLAUDE_CODE_AGENT_TYPE=team-lead` -- I (the `hdi_testbed` role) am myself a named teammate
under it right now. `CLAUDE.md`'s own 2026-08-12 note says the same: *"The `hdi_*` fleet only
resolves with client env var `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`."* So the question is not
"adopt or don't" -- it's already adopted for the 5 persistent fleet roles. The real question the
owner's caveat raises is narrower: *should the disposable, one-shot scan pattern (the 139
general-purpose + literature-scan dispatches driving tonight's problem) also move to
long-lived, named, `SendMessage`-addressable teammates* -- Agent Teams' actual distinguishing
feature over a one-shot `Agent` tool call, per the owner's own framing ("each worker gets its
own independent context rather than dumping back into yours").

**Recommendation: no, not for the scan pattern specifically -- keep scans as one-shot
dispatches using the fragment convention built this cycle; keep Agent Teams for the 5
already-well-suited persistent roles.**

Reasoning against expanding it to scans:
- A named teammate is, by construction, a *standing* context: it persists (addressable,
  presumably holding state) until explicitly stopped, unlike a one-shot `Agent` call whose
  cost ends the moment it returns. The audit's own numbers show fan-out is already the
  dominant cost driver -- 235 spawns/~57h (~4.1/hour, clearly "a standing part of the
  workflow," meeting the owner's own bar for when Agent Teams is worth it), averaging ~14.9k
  output tokens per Agent-bearing message, and **a weekly API limit exhausted in about six
  minutes by fan-out this same night**. Converting the highest-volume bucket (one-shot
  literature/code scans, which have no need to persist once they've reported) into
  standing-context teammates adds concurrent-context overhead on top of an already-measured
  limit-exhaustion incident, for a workload shape (ask once, get an answer, done) that doesn't
  need persistence.
- The audit's root-cause findings (0% batching, 85% unrelayed, yield-after-dispatch
  compliance getting *worse* after an enforcement hook landed) are **discipline** failures, not
  **dispatch-primitive** failures -- switching primitives doesn't fix a compliance problem that
  a dedicated PostToolUse hook already failed to fix by nagging harder. The fragment convention
  (section 2) and the tool-restricted `scan` role (section 3) target the actual measured
  mechanisms (large-report-into-context, Bash-permission-prompt storms, orphaned child chains)
  directly and are cheaper than a persistence-model change.
- Where Agent Teams' distinguishing feature genuinely fits: the 5 `hdi_*` roles already use it
  for exactly what it's good at -- ongoing, stateful, multi-turn collaboration across a long
  session (this very report is being written by a teammate that was spawned once and has been
  doing bounded work since). That's the correct scope; expanding it further to disposable,
  single-question scans would be applying the persistent-context tool to a workload that is, by
  the owner's own description of the fragment pattern, supposed to be "truly fire-and-forget."

**Cost I could not measure this session** (flagged, not fabricated): the actual relative
per-dispatch token/context overhead of a standing named teammate vs. a one-shot `Agent` call
under this specific harness version. I do not have a clean before/after comparison and did not
run one (would require live dispatches, which are forbidden here). The recommendation above is
reasoned from the audit's existing numbers plus the structural argument, not from a fresh
measurement -- state this distinction if the recommendation is acted on.

## 7. Drafted `CLAUDE.md` patch (NOT applied -- concurrent writers, per instruction)

To be added by whoever next has write access to `CLAUDE.md`, as a new subsection near the
existing "Choosing the model for a subagent" / delegation sections (this note supersedes
nothing in the audit's own drafted patch from `notes/agent_usage_practices_audit_2026-08-14.md`
section 5 -- that patch is about idle-nudging and yield-after-dispatch and still stands
independently; this is a new, additional subsection):

```
## Fragment convention for fire-and-forget scans (2026-08-14, measured)

Literature scans and codebase surveys ("read a bunch of things and report") do NOT return
prose into the dispatching session. Dispatch them as `scan` (`.claude/agents/scan.md` --
tools: Read, Grep, Glob, WebSearch, WebFetch, Write; permissionMode: dontAsk), which writes
its full findings to `.claude/scan-out/<slug>.json` (schema + evidence tags in
`.claude/scan-out/README.md`) and returns exactly ONE LINE. Read fragments directly, or run
`python tools/scan_out_collect.py` to assemble everything currently in the directory into one
note. Why: four literature scans in one night returned 2000-4000 word reports straight into
the main conversation -- the same attention tax as a same-turn-continuation violation, arriving
by a slower route (`notes/agent_usage_practices_audit_2026-08-14.md`).

`scan`'s tool list is deliberately narrow: no Bash (the measured denial data shows 31/31
auto-denies that session carried a deletion token in a Bash call -- removing Bash removes the
mechanism), no Edit (cannot touch source), no Agent (cannot spawn a child -- directly answers
the incident where a chain spawned six children with no surviving parent to collect them).

The Stop hook (`data/hooks/staging/stop_hook.py`) gates on scan-out fragment COUNT, and zero is
the mandatory early exit: an empty or absent `.claude/scan-out/` means scans are legitimately
still in flight and must never block a turn from ending. Only an already-landed fragment
(newer than this session's own last-collected mark) can trigger a block, nudging toward
`scan_out_collect.py` rather than leaving results uncollected indefinitely.

Do NOT expand this pattern to persistent named teammates (Agent Teams) for one-shot scan work
-- see `notes/subagent_fanout_pattern_2026-08-14.md` section 6 for the reasoning (standing
context cost vs. disposable-workload shape; the fleet's 5 persistent `hdi_*` roles are the
correct scope for that primitive, not scans).
```

## 8. File manifest

- `D:/AI/hd-instrument/.claude/scan-out/README.md` -- new, tracked (schema doc)
- `D:/AI/hd-instrument/.claude/scan-out/*.json` -- gitignored (fragments; none present except
  during self-tests, all cleaned up)
- `D:/AI/hd-instrument/.claude/agents/scan.md` -- new agent definition
- `D:/AI/hd-instrument/tools/scan_out_collect.py` -- new, `--self-test` passing
- `D:/AI/hd-instrument/.gitignore` -- amended (scan-out fragment rule)
- `D:/AI/hd-instrument/data/hooks/staging/stop_hook.py` -- amended (`_scan_out_gate` +
  `--self-test`), live-wired hook, both isolated self-test and real-protocol smoke test passing
- `D:/AI/hd-instrument/notes/subagent_fanout_pattern_2026-08-14.md` -- this note
- **Not touched**: `.claude/agents/exp_dev.md` carries a pre-existing uncommitted modification
  from a concurrent writer (last commit on that file 2026-07-14; working-tree diff adds an
  "INLINE-LOCAL MANDATE" section postdating that commit) -- not mine, not committed by me, per
  "commit your own files only."
- **Not touched**: `.claude/agents/{research,orchestrator,skunkworks,testbed}.md` -- audited,
  no changes (see section 3 reasoning).
- **Not touched**: `CLAUDE.md` -- per explicit instruction (patch drafted in section 7 only).
