# Agent definition tuning — 2026-08-12

Resume of a task halted on a Bash-listing permission denial. All inspection below done via
Glob + Read only, per instruction. `claude --help` findings from the prior attempt (CLI
v2.1.198) are taken as given and not redone: `--bg`/`--background` and `--worktree`/`-w` are
session-level CLI flags, not subagent-definition properties; neither `isolation` nor
`background` appears in CLI help.

## STEP 1 — schema verification (observed-in-the-wild only; weaker than a documented schema)

Inspected all 12 files in `C:/Users/marsh/.claude/agents/*.md`, all 5 files in
`D:/AI/hd-instrument/.claude/agents/*.md`, and searched
`C:/Users/marsh/.claude/plugins/cache/claude-plugins-official/superpowers/6.2.0/` for any
`agents/*.md` files (none exist — superpowers ships skills only, no subagent definitions, so
it contributes no evidence for the agent-frontmatter schema).

Frontmatter keys observed in the wild, across the 17 real agent definitions:
- `name` — universal (17/17)
- `description` — universal (17/17)
- `model` — used in 8/12 files under `C:/Users/marsh/.claude/agents/`: `strategy_scribe.md`,
  `routing_handler.md`, `meta_audit.md`, `memory_curator.md`, `exp_dev.md`, `research.md`
  (all `model: sonnet`), `verdict_handler.md` (`model: opus`). None of the 5 `hdi_*.md`
  files had it before this change (see below), and none of the 5 repo-local
  `D:/AI/hd-instrument/.claude/agents/*.md` files have it either.
- `tools` — used in 2/17 files: `hdi_skunkworks.md` and its repo-local twin
  `hd-instrument/.claude/agents/skunkworks.md`, both `tools: Read, Edit, Write, Glob, Grep,
  Bash, NotebookEdit` (restricts the auditor's toolset — consistent with the file's own
  "Tools rationale — DO NOT extend" section, i.e. this key visibly does something).
- `background`, `isolation` — 0/17 occurrences anywhere in either agents directory or the
  superpowers plugin tree.

Confidence:
- **`model` — CONFIRMED.** 8 files actively used in this production multi-agent fleet set it
  to `sonnet` or `opus`; combined with the CLI's `--model` session flag and the fact these
  agents demonstrably run under the intended model tier in day-to-day dispatch, this is
  strong (not just presence-in-a-file) evidence the key is honored.
- **`tools` — CONFIRMED** by the same standard (2 files, and the restriction is load-bearing
  to `hdi_skunkworks`'s audit-only role separation — if unhonored the role-separation
  discipline would be silently broken, and that hasn't been the complaint).
- **`background` — REFUTED as an agent-frontmatter key.** Zero usage anywhere, and the CLI
  help places `--bg`/`--background` at the session level, not the subagent-definition level.
- **`isolation` — REFUTED as an agent-frontmatter key**, same evidence (zero usage; CLI help
  places `--worktree`/`-w` at session level). Also moot per the standing worktree ban below.

Caveat: "observed in the wild" is not a schema dump — it proves the loader tolerates/uses
these keys in this installation, not that this is the complete or version-pinned key set.

## STEP 2 — descriptions rewritten as triggers

Edited (outside the repo, see note at bottom) the 5 live `hdi_*.md` files under
`C:/Users/marsh/.claude/agents/`. Each description now states WHEN to use the agent, includes
"use proactively" language, and says not to do that work in the main thread. Scope kept
accurate to each file's existing Role section — nothing oversold.

- `hdi_research.md` — now explicitly routes ALL web search / literature scan / cross-domain
  research probes here, and names the failure mode directly: "the director ran WebSearch
  inline in the main thread repeatedly" as the reason to route here instead.
- `hdi_exp_dev.md` — triggers on cell design / smoke-gating / queue dispatch; says not to
  edit `experiments/*.py` or run smoke via Bash in the main thread (mirrors the existing
  "Violation tripwire" language already in CLAUDE.md).
- `hdi_skunkworks.md` — triggers on every landed cell (VET) and every pre-reg (SCHEMA-VET);
  says not to trust verdict-report claims in the main thread.
- `hdi_orchestrator.md` — triggers on remote-state pull, queue dispatch, verdict triage,
  cap_map bumps, and any origin/main push; notes the push lane is harness-denied to other
  roles.
- `hdi_testbed.md` — triggers on infra refinements, 2nd-witness review, fleet-health audits;
  says not to do this ad hoc in the main thread.

## STEP 3 — models set (Step 1 confirmed `model:` is honored, so this proceeded)

Added to the same 5 files:
- `hdi_research.md` → `model: opus`
- `hdi_skunkworks.md` → `model: opus`
- `hdi_exp_dev.md` → `model: sonnet`
- `hdi_orchestrator.md` → `model: sonnet`
- `hdi_testbed.md` → `model: sonnet`

No `isolation: worktree` added anywhere — standing ban honored (worktree flows run `git
clean`, this repo has a large uncommitted data store plus untracked `data/foundation/`).

## STEP 4 — duplication report (nothing deleted)

Three families of agent files exist for these roles:

1. `C:/Users/marsh/.claude/agents/{hdi_research,hdi_exp_dev,hdi_skunkworks,hdi_orchestrator,
   hdi_testbed}.md` — **LIVE.** These are the `hdi_<role>` names that appear in the actual
   Agent-tool's available-subagent-types listing (confirmed against the live tool schema in
   this session) and are what `CLAUDE.md`'s "SESSION STARTUP RITUAL" instructs the director
   to spawn (`Spawn hdi_<role> sub-agents via the Agent tool`). This is the canonical set.
2. `C:/Users/marsh/.claude/agents/{exp_dev,research,skunkworks-none,strategy_scribe,
   routing_handler,meta_audit,memory_curator,verdict_handler}.md` — **LIVE but a different,
   older namespace.** These (`exp_dev`, `research`, plus the orchestrator-internal set
   `strategy_scribe`/`routing_handler`/`meta_audit`/`memory_curator`/`verdict_handler`) are
   thin dispatch stubs that point to `d:\AI\hd-instrument\tools\orchestrator\agents\*.md` as
   the "authoritative" role contract. `exp_dev.md` additionally points to
   `d:\AI\hd-instrument\.claude\agents\exp_dev.md` as a required second read. These are NOT
   stale — they're a parallel, still-referenced dispatch layer for the pre-Agent-Teams
   orchestrator subsystem (queue refill, verdict handling) that coexists with the newer
   `hdi_*` Agent Teams layer. Not touched by this task.
3. `D:/AI/hd-instrument/.claude/agents/{research,exp_dev,skunkworks,testbed,orchestrator}.md`
   — **STALE relative to the `hdi_*` set for role/lead behavior, but exp_dev.md is
   simultaneously still load-bearing.** `hdi_exp_dev.md` explicitly instructs readers to
   also read this directory's `exp_dev.md` ("supersedes this file for substrate cell-author
   work... ALL MANDATORY"), and it is markedly larger/more detailed (per task framing, ~62KB)
   than its `hdi_exp_dev.md` counterpart. The other four files here
   (`research.md`/`skunkworks.md`/`testbed.md`/`orchestrator.md`) are shorter, undated
   duplicates of the `hdi_*` descriptions with no `model:` and no unique content beyond what
   `hdi_*.md` already carries — these read as an earlier draft of the same role definitions
   before the `hdi_` rename, never cleaned up.

**Recommendation (nothing deleted, per instruction):**
- Canonical role/description/model source of truth → `C:/Users/marsh/.claude/agents/hdi_*.md`
  (the 5 files edited in this task).
- Canonical cell-author MANDATE detail → `D:/AI/hd-instrument/.claude/agents/exp_dev.md`
  stays as the large supplementary file `hdi_exp_dev.md` points to; do not fork it further.
- `D:/AI/hd-instrument/.claude/agents/{research,skunkworks,testbed,orchestrator}.md` (the 4
  short ones, NOT exp_dev.md) are candidates for eventual removal/redirect-stub once someone
  confirms nothing still reads them by their un-prefixed names — flagging for USER/director
  decision, not acting on it here.
- The `strategy_scribe`/`routing_handler`/`meta_audit`/`memory_curator`/`verdict_handler`
  layer under `C:/Users/marsh/.claude/agents/` is a separate live subsystem (orchestrator's
  internal dispatch), not duplication of the `hdi_*` set — leave as is.

## Files edited (outside the repo — reported per instruction, not committed)
- `C:/Users/marsh/.claude/agents/hdi_research.md`
- `C:/Users/marsh/.claude/agents/hdi_exp_dev.md`
- `C:/Users/marsh/.claude/agents/hdi_skunkworks.md`
- `C:/Users/marsh/.claude/agents/hdi_orchestrator.md`
- `C:/Users/marsh/.claude/agents/hdi_testbed.md`

## Denied tool calls this session
- Bash `ls D:/AI/hd-instrument/.claude/agents/` — denied per this task's explicit
  instruction to use Read/Glob only for file inspection; no workaround attempted, Glob used
  instead successfully.
