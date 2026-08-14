# Delegation enforcement + agent-registration outage fix (2026-08-14)

Scope: (1) root-caused and fixed the two-day `hdi_*` agent-registration outage;
(2) installed a PostToolUse/Agent hook that forces end-of-turn after a background
dispatch; (3) ruled on the proposed PreToolUse Bash blocker. Nothing under
`hdlab/` or `experiments/` was touched.

---

## 1. AGENT REGISTRATION OUTAGE -- ROOT CAUSE WAS A UTF-8 BOM

### Verified before touching anything

Hexdump of the first 3 bytes of every `.md` in `C:/Users/marsh/.claude/agents/`:

| file | first 3 bytes | registered before fix |
|---|---|---|
| `hdi_exp_dev.md` | `ef bb bf` | NO |
| `hdi_orchestrator.md` | `ef bb bf` | NO |
| `hdi_research.md` | `ef bb bf` | NO |
| `hdi_skunkworks.md` | `ef bb bf` | NO |
| `hdi_testbed.md` | `ef bb bf` | NO |
| `exp_dev.md`, `memory_curator.md`, `meta_audit.md`, `research.md`, `routing_handler.md`, `strategy_scribe.md`, `verdict_handler.md` | `2d 2d 2d` (`---`) | YES |

Correlation is exact: 5/5 BOM files failed to register, 0/7 BOM-free files failed.
All five share mtime `2026-08-12 21:16:17`, consistent with a single PowerShell 5.1
`Set-Content`/`Out-File -Encoding utf8` rewrite (the documented "PS BOM" hazard).

### THE DOCUMENTED `background:` EXPLANATION IS WRONG -- FLAG FOR DIRECTOR

The existing docs claim a `background:` key in frontmatter causes the load failure.
That is refuted:

- `grep -n "^background:" *.md` over the whole agents directory returns **zero
  matches in any file**. No agent definition has a `background:` frontmatter key at all.
- The word "background" appears nowhere in the body of `hdi_exp_dev.md`,
  `hdi_skunkworks.md`, or `hdi_testbed.md` (count 0) -- yet all three failed to load.
- It *does* appear in body prose of `hdi_orchestrator.md` and `hdi_research.md`, which
  fails to separate the two groups in either direction.

`background:` cannot be the cause. The BOM is. **CLAUDE.md was NOT edited (a concurrent
session owns it); the Director should correct that claim there.**

Secondary note, not acted on: the same PowerShell rewrite also mojibaked every em-dash
in the five files (`C3 A2 E2 82 AC E2 80 9D` = `Ã¢â‚¬â€` -- UTF-8 `—` read as cp1252 and
re-encoded). This is cosmetic, does not affect parsing, and was deliberately left alone
so the fix stayed a pure 3-byte delete. Worth a separate cleanup pass.

### The fix

Backups first (nothing deleted): `<name>.md.bak-20260813-BOMfix`, preserving mtimes.

Strip performed in Python **binary mode** (`open(n,'wb')`), never text mode, per the
documented CRLF-doubling hazard. Result:

```
hdi_exp_dev.md         6527 -> 6524 bytes | tail-identical=True | CRLF 79->79   LF 79->79
hdi_orchestrator.md   27832 -> 27829 bytes | tail-identical=True | CRLF 346->346 LF 346->346
hdi_research.md        8696 -> 8693 bytes | tail-identical=True | CRLF 68->68   LF 68->68
hdi_skunkworks.md      9936 -> 9933 bytes | tail-identical=True | CRLF 117->117 LF 117->117
hdi_testbed.md         4264 -> 4261 bytes | tail-identical=True | CRLF 56->56   LF 56->56
```

Exactly 3 bytes removed from each. `CRLF count == LF count` before and after proves every
newline is still CRLF -- no line-ending damage. Independently confirmed with
`cmp <(tail -c +4 <backup>) <file>` -> IDENTICAL for all five.

### Proof the fix worked

A fresh headless session (`claude -p ... --output-format stream-json`) reports its agent
registry at init. Before: 12 agents, no `hdi_*`. After:

```
['claude','exp_dev','Explore','general-purpose','hdi_exp_dev','hdi_orchestrator',
 'hdi_research','hdi_skunkworks','hdi_testbed','memory_curator','meta_audit','Plan',
 'research','routing_handler','statusline-setup','strategy_scribe','verdict_handler']
```

All five restored (17 total). `hdi_testbed` was then actually dispatched and executed
successfully, twice. **Note: an already-running session keeps the agent list it
snapshotted at startup -- the Director must start a new session (or /clear) to see them.**

---

## 2. INSTALLED: PostToolUse hook on the `Agent` matcher

- Script: `D:/AI/hd-instrument/tools/agent_dispatch_stop_hook.py`
- Wired in: `D:/AI/.claude/settings.json` (backup: `settings.json.bak-20260813-190000`)
- No collision: neither settings file previously had `PreToolUse`/`PostToolUse`.
- Written UTF-8 **without BOM** (verified `7b 0a 20`, i.e. `{\n `), parses as JSON,
  `claude doctor` -> "No installation issues found."

Injected `additionalContext`: a background agent has been dispatched; END YOUR TURN NOW;
do not begin new work; do not run adjacent or "while we wait" commands; report the
dispatch in one line and stop.

### Evidence it fires (not assumed)

From `--include-hook-events` on a live headless session:

```json
{"subtype":"hook_response","hook_name":"PostToolUse:Agent","hook_event":"PostToolUse",
 "exit_code":0,"outcome":"success",
 "output":"{\"hookSpecificOutput\": {\"hookEventName\": \"PostToolUse\",
   \"additionalContext\": \"SYSTEM ENFORCEMENT (PostToolUse/Agent): a background agent
   has been dispatched. END YOUR TURN NOW. ...\"}}"}
```

The hook also self-logs every payload to `data/hooks/agent_dispatch_hook.log`; that log
independently records 2 real harness `Agent`-matcher events, both with
`tool_input.subagent_type = hdi_testbed`.

Cost: ~292 ms/call (system Python 3.12 with `-S -E`, chosen over the venv interpreter at
~517 ms). Fires only on `Agent` dispatches, which are rare, so critical-path cost is
negligible. Timeout 10 s; the script swallows all exceptions and always exits 0, so a
failure can never break a tool result.

### SessionStart hook still healthy (regression check)

Ran `tools/session_start_hook.py` via the venv interpreter after the edit: exit 0,
5147 bytes, `AS OF:` present, `WHAT IS RUNNING` present, and **neither** sentinel
`(no AS OF line found)` nor `(no WHAT IS RUNNING section found)` fired, with a
non-empty section body. The hook reformats `## WHAT IS RUNNING` to `WHAT IS RUNNING:`
in its output, so grepping the *raw literal* `## WHAT IS RUNNING` against the output is
a false-alarm test -- check the decoded `additionalContext` and the two "not found"
sentinels instead.

---

## 3. VERDICT ON HOOK 3 (PreToolUse Bash blocker): **NOT INSTALLED**

The safety question was answered empirically rather than assumed, using a temporary
logging-only probe (installed, sampled, then removed).

**The payload DOES distinguish main thread from subagent.** Both `PreToolUse` and
`PostToolUse` payloads carry `agent_type` and `agent_id`:

```
PreToolUse keys: [agent_id, agent_type, cwd, effort, hook_event_name, permission_mode,
                  prompt_id, session_id, tool_input, tool_name, tool_use_id, transcript_path]

agent_type=None            agent_id=None                cmd=echo pre-probe-main   <- MAIN THREAD
agent_type=hdi_testbed     agent_id=abe9eb1ef8e29bed6   cmd=echo pre-probe-sub    <- SUBAGENT
agent_type=general-purpose agent_id=a2190213b92c8b860   cmd=...                   <- SUBAGENT
```

So a subagent-safe gate is constructible: **act only when `agent_type` is null/absent.**

**It was still not installed, because the mechanism being safe is not the same as the
deployment being safe.** The decisive finding: hooks in `D:/AI/.claude/settings.json`
apply to *every* session with that cwd, and they take effect **live, without a restart**,
for newly spawned subagents. The logging probe immediately began capturing 47+ Bash calls
from a **concurrent session** (`139818eb-...`) that has uncommitted work in flight. A
blocking hook would therefore have started denying another Director's commands
mid-flight, with no way for me to warn or coordinate with it. That is an outage risk
that outweighs the benefit.

Also worth noting: every observed Bash call from that concurrent session carried a
non-null `agent_type` -- i.e. it was *already* delegating correctly. The blocker would
have added risk while addressing behaviour that was not occurring.

**Recommendation:** install it deliberately when no concurrent session is live, gated on
`agent_type in (None, "")`, using **exit code 2** with the delegate-instead instruction on
stderr (not `permissionDecision: "deny"`, which has open reports of non-enforcement).
Measure per-call overhead at that time; on the Bash matcher it lands on *every* command,
where ~292 ms is no longer negligible.

---

## 4. HOW TO DISABLE

- **PostToolUse/Agent hook:** delete the `"PostToolUse"` key from
  `D:/AI/.claude/settings.json`, or restore
  `D:/AI/.claude/settings.json.bak-20260813-190000`. Takes effect for new sessions and
  newly spawned subagents; a running main thread keeps its startup snapshot.
- **Whole hook script:** `D:/AI/hd-instrument/tools/agent_dispatch_stop_hook.py`. Safe to
  leave on disk once unwired.
- **BOM fix:** restore any of `C:/Users/marsh/.claude/agents/hdi_*.md.bak-20260813-BOMfix`
  (these restore the *broken* BOM state; only useful for re-testing the diagnosis).
- **Log:** `D:/AI/hd-instrument/data/hooks/agent_dispatch_hook.log` grows ~1 line per
  Agent dispatch. Not committed. Safe to truncate.

## 5. OPEN ITEM FOR THE DIRECTOR

Correct the `background:`-causes-load-failure claim wherever it appears in `CLAUDE.md`
and related docs. It is wrong; the cause was a UTF-8 BOM. `CLAUDE.md` was deliberately
left untouched here because a concurrent session owns it.
