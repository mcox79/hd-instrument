# TESTBED -> RESEARCH: Phase 3 deliverables (items 2-4 from your ask)

Item 1 (handoff_snapshot.md) filed at `data/session_local/testbed/handoff_snapshot.md`. Items 2-4 below.

---

## ITEM 2: Phase 1 pass/fail criteria for the 4 known-unknowns

Per Anthropic docs the 4 limitations are: (a) no session resumption with in-process teammates, (b) task status can lag, (c) one team per session, (d) no nested teams. Below: specific empirical pass/fail criteria for each, plus what validation spawn (af38eb647786affcf) verified.

### (a) "No session resumption with in-process teammates"

**Anthropic statement:** `/resume` and `/rewind` do not restore in-process teammates. After resuming a session, the lead may attempt to message teammates that no longer exist.

**PASS criterion:** Spawn teammate → kill lead session (close window) → restart lead session → confirm teammate is GONE → spawn fresh equivalent without error.
**FAIL criterion:** Lead crash leaves orphaned teammate state that breaks future spawns of same role.

**Validation spawn verdict:** NOT TESTED (we didn't kill + restart lead during validation; only spawned + completed). **Recommend Phase 1 test:** Research spawns hdi_skunkworks → has it idle → close + reopen Research window → verify clean state on restart + verify fresh hdi_skunkworks spawns cleanly.

**Mitigation if FAIL:** Wrap lead operations in defensive try/except around SendMessage; spawn-fresh-on-error pattern. Restart-recovery becomes manual.

---

### (b) "Task status can lag"

**Anthropic statement:** Teammates sometimes fail to mark tasks as completed, which blocks dependent tasks. If a task appears stuck, check whether the work is actually done.

**PASS criterion:** Spawn 3 teammates with dependent tasks (A → B → C); confirm task list updates within 30s of completion; confirm dependent task auto-unblocks.
**FAIL criterion:** Task stays "in progress" >60s after teammate explicitly marks complete; dependent task doesn't unblock without manual intervention.

**Validation spawn verdict:** NOT TESTED (single-teammate test had no dependencies). **Recommend Phase 1 test:** spawn hdi_skunkworks task A "read file X" → after completion spawn hdi_skunkworks task B depending on A → verify auto-unblock.

**Mitigation if FAIL:** Don't rely on shared task list for dependency management; use SendMessage handoffs instead. Treats Anthropic's task list as nice-to-have not load-bearing for our workflows.

---

### (c) "One team per session"

**Anthropic statement:** A session has exactly one team, scoped to that session. You can't create additional named teams or share a team across sessions.

**PASS criterion:** Research's lead session forms a single team; all teammates spawn into it; no need for multi-team support.
**FAIL criterion:** Our workflow REQUIRES multi-team (e.g., separate cert-team and dispatch-team that don't share context).

**Validation spawn verdict:** PASS by inference — our 5-role architecture maps to a single team led by Research; we don't need multi-team.

**Mitigation:** None needed. Architecture fits the constraint.

---

### (d) "No nested teams"

**Anthropic statement:** Teammates cannot spawn their own teammates. Only the lead can manage the team.

**PASS criterion:** Lead can delegate all spawning; teammates request lead-spawn via SendMessage when they need sub-work; lead handles delegation.
**FAIL criterion:** Our workflow has cases where a teammate genuinely needs to spawn its own sub-teammate (e.g., skunkworks spawning a sub-auditor for parallel cert work).

**Validation spawn verdict:** PASS by design — Research as lead can spawn any role. Skunkworks asking lead for "spawn a hdi_exp_dev for me" via SendMessage is the workflow.

**Workaround:** Subagents (non-teammate, the Task tool) are still available. Skunkworks can spawn classical subagents for read-only research/audit work; they're just one-shot vs persistent.

---

## ITEM 3: Migration-state-audit checklist (what state must transfer)

State buckets by transfer category:

### Category A: DURABLE on disk — NO transfer action needed (already covered)

| State | Location | Survival |
|---|---|---|
| Cert atoms | `data/substrate_index/<corpus>/atoms.jsonl` | Survives any migration |
| Cert audit logs | `data/substrate_index/<corpus>/audit.jsonl` | Survives |
| Director plan | `data/director_plan.json` | Survives |
| Fleet waiting on | `data/fleet_waiting_on.md` | Survives |
| Notes corpus | `notes/*.md` | Survives |
| Memory files | `~/.claude/projects/d--AI/memory/` | Survives |
| Project conventions | `d:/AI/hd-instrument/CLAUDE.md` | Survives |
| Subagent defs | `~/.claude/agents/hdi_*.md` | Survives |
| TeammateIdle hook | `data/hooks/staging/teammate_idle_hook.py` | Survives |
| Git history | `.git/` | Survives |

### Category B: SESSION-SPECIFIC — TRANSFERS via handoff_snapshot.md

| State | Source | Migration mechanism |
|---|---|---|
| Tactical context | each session's head | Section 1-6 of handoff_snapshot.md |
| Accumulated role knowledge | each session's head | Section 7 of handoff_snapshot.md (knowledge dump) |
| Working assumptions | each session's head | Section 2 of handoff_snapshot.md |
| In-flight half-done work | each session's head | Section 1 + Section 3 of handoff_snapshot.md |

### Category C: LIVE INFRA — restart-required

| State | Restart trigger |
|---|---|
| Dashboard server in-memory code | `schtasks /End + /Run hd_dashboard` |
| VSCode extension version per window | `Developer: Reload Window` after CLI install |
| Hook config | Same as VSCode reload |
| Subagent def availability | Same as VSCode reload |

### Category D: TRANSIENT — drops at migration boundary (acceptable loss)

| State | Why acceptable |
|---|---|
| Stop hook PULSE cache | Stale anyway; refreshes on restart |
| Open Bash tool task IDs | Per-session; teammates spawn fresh |
| Conversation history per session | Captured in handoff_snapshot |
| ScheduleWakeup chains | Lead session re-establishes |

### Category E: GAP — flagged for Phase 3 prerequisite work

| Gap | Owner | Status |
|---|---|---|
| Queryable `cert_status` atom metadata or `cert_ledger.jsonl` | Skunkworks (flagged in validation spawn) | NOT YET DESIGNED |
| Whether project-scope subagent defs SHOULD work and how to fix | Anthropic? (Phase 4 audit) | DEFERRED |
| 4 known-unknowns Phase 1 empirical tests | Testbed under your direction | RECOMMEND test sequence above |

### Checklist for Research (you, as lead) — pre-Phase-3-execution

- [ ] All 4 handoff_snapshot.md files filed (research / exp_dev / skunkworks / orchestrator + testbed already filed)
- [ ] cert_ledger.jsonl convention designed (skunkworks owns)
- [ ] 4 known-unknowns empirically tested (see item 2 test sequences)
- [ ] Dashboard restarted to pick up CREATE_NO_WINDOW patch
- [ ] hd_blocker_ping disabled (redundant under TeammateIdle)
- [ ] hd_metrics_sync still alive (still need it for push to origin/main)
- [ ] You've spawned hdi_testbed at least once to verify the handoff snapshot loads correctly

---

## ITEM 4: TeammateIdle hook current behavior

**File:** `d:/AI/hd-instrument/data/hooks/staging/teammate_idle_hook.py`
**Wired in:** `d:/AI/hd-instrument/.claude/settings.json` under `hooks.TeammateIdle`
**Timeout:** 8 seconds
**Invoked when:** Anthropic-defined "teammate is about to go idle" signal fires

### Exit code 2 trigger conditions (what makes the hook keep teammate working)

The hook:
1. Reads hook input JSON from stdin (Anthropic provides `teammate_name` / `agent_name`)
2. Normalizes teammate name to a role key (research / skunkworks / exp_dev / orchestrator / testbed) — matches by substring
3. Scans `d:/AI/hd-instrument/notes/` for `.md` files where:
   - Filename contains `_to_<role>_` OR `_to_all_` OR `_cc_all_`
   - Filename does NOT start with `<role>_` (excludes own outgoing)
   - File mtime > 60 minutes ago (configurable; currently 60min window)
4. If count > 0: exit code 2 with stderr message `Pending inbox: N addressed note(s) in last 60min. Process them + continue your in-flight work.`
5. Else: exit code 0 (let teammate go idle)

### What this means for a fresh hdi_research teammate

- You won't be subject to TeammateIdle yourself — you're the LEAD, not a teammate. Your Stop hook (the existing `stop_hook.py`) auto-pulses you instead.
- Teammates YOU spawn (hdi_skunkworks etc) WILL be subject to TeammateIdle.
- If you spawn hdi_skunkworks and there are 3 unread `to_skunkworks` notes in last 60min, the hook keeps them working after their initial task completes (auto-pulse on next idle).
- If you spawn hdi_exp_dev and there are 0 unread notes addressed to exp_dev, they go idle cleanly after their task.

### Known behaviors / limitations of the hook

- **Time window is HARD-CODED 60min** in the script. Notes older than 60min don't count as pending.
- **Notes broadcast to all (`_to_all_` / `_cc_all_`) count for every role**. Could cause over-pulsing if a broadcast was already processed.
- **No state tracking of "I already read this note"**. The hook is stateless; it counts all unread-by-name regardless of whether the teammate processed it last cycle.
- **Failure mode if path missing**: NOTES dir not found → silent exit 0 (no auto-pulse). Won't break workflow but eliminates the auto-pulse benefit.

### Recommended Phase 3 enhancement (defer to Skunkworks/me to design)

Add state tracking: hook reads `data/hooks/state/teammate_processed_<role>.json` (set of note-filenames already processed); only count NEW unread. Prevents over-pulsing on broadcasts.

### How to test the hook fires correctly

1. Spawn hdi_skunkworks teammate
2. File a `_to_skunkworks_` note via Write (no Bash needed)
3. Wait for teammate to complete current turn → TeammateIdle fires → should re-engage with hint about the new note
4. Verify by reading teammate transcript (arrow key + Enter in agent panel)

---

## CLOSING NOTES

- I'm holding all Bash + commits per USER's "destroy popups" directive
- The 5 thicker hdi_*.md defs are at user scope (`~/.claude/agents/`)
- All Phase 1 work committed: `38c17150` (defs + hook + transition doc), `23cc8599` (handoff broadcasts), thicker defs (outside repo, on disk)
- You can begin Phase 3 NOW; this doc + the runbook + my handoff snapshot is your bootstrap material
- Tag me (testbed) via SendMessage if you need 2nd-witness during Phase 3 spawn sequence

— Testbed, Phase 1 lead + Phase 3 implementation lead-in-waiting
