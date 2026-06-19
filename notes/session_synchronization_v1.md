# Session synchronization protocol (v1)

How the four sessions (orchestrator, research, testbed, cloud) stay coordinated without conflicts. Applies to all sessions. Read this in tandem with `notes/session_architecture_v1_2026-05-31.md`.

## The synchronization problem

Four sessions writing to a shared git repo + shared status_log + shared memory. Without discipline:
- Sessions miss updates from each other (stale context)
- Concurrent commits collide on push
- Routing files filed by one session sit unread by the receiving session
- Cap_map decisions made without seeing recent research findings

## The 3 touch-base patterns (apply each one regularly)

### Pattern A: Pull-before-significant-work

Every session, at every meaningful work step (NOT every tool call — at decision boundaries):

```bash
git -C d:/AI/hd-instrument pull --rebase
```

If the pull surfaces changes, READ what changed before continuing. Especially:
- Cap_map updates (`notes/substrate_capability_map.md` — last few entries)
- Most recent decision log for any session
- Any new routing file in your inbox

This is the minimum coordination. Pull before:
- Starting a new task
- Returning from a long subagent dispatch (which took 5+ min of wall time during which other sessions may have committed)
- About to commit your own work
- Receiving "all clear to ship" or similar high-stakes signal from user

### Pattern B: Inbox polling

Each session has an inbox of routing files filed by other sessions. Poll regularly:

| Session | Polls for files matching | Cadence |
|---|---|---|
| **Orchestrator** | `notes/strategy_request_to_strategy_*.md`, `notes/strategy_request_to_exp_dev_*.md` | Every Pull-before-significant-work + every user turn |
| **Research** | `notes/strategy_request_to_research_*.md` | Every Pull-before-significant-work + every user turn |
| **Testbed** | `notes/testbed_handoff_*.md`, `notes/exp_dev_handoff_*.md` | Every Pull-before-significant-work + every user turn |
| **Cloud** (when active) | `notes/cloud_handoff_*.md` | Every Pull-before-significant-work + every user turn |

Process a routing file: read it, do the work it requests, write the deliverable, file the response routing file (if applicable), DELETE the request file once handled (or move to `notes/routed_completed/`).

### Pattern C: Status_log consumption

The For-You dashboard pulls `data/orchestrator_status_log.jsonl` (gitignored — but visible in the local dashboard). Sessions can also tail it directly:

```python
# Check recent log_event entries from other sessions
python -c "
import json
from pathlib import Path
log = Path('data/orchestrator_status_log.jsonl')
if log.exists():
    lines = log.read_text().splitlines()
    # last 20 entries
    for ln in lines[-20:]:
        try:
            e = json.loads(ln)
            print(f\"{e.get('ts','?')[:19]} [{e.get('source','?')}] {e.get('importance','?')}: {e.get('plain_language','?')[:120]}\")
        except: pass
"
```

Run this when:
- Starting a new task (see what other sessions just did)
- Confused why a decision was made (search log for related event)

## The watchdog setup per session

The orchestrator has a structural watchdog (`tools/orchestrator/heartbeat_watchdog.py`) that monitors runners + queues + emits events. Other sessions need analogous lightweight polling.

### Orchestrator (already in place)
- `tools/orchestrator/heartbeat_watchdog.py` — 13 event kinds (silent_idle, gpu_idle, cpu_idle, gpu_queue_low, cpu_queue_low, ship_unconfirmed, for_you_stale, research_overdue, verdict_landed, bridge_cache_stale, routing_ratio_low, duplicate_runner_detected, duplicate_watchdog_detected)
- Runs as a schtask on the local box
- Writes events to status_log → For-You feed

### Research session (lightweight pattern, no daemon needed)
Behavioral discipline:
- On every user turn AND every dispatch-return, run Pattern A + Pattern B
- If a research drill takes >60 min (long subagent run), re-pull at start AND end
- Watch for `notes/strategy_request_to_research_*.md` appearing — when filed by orchestrator or testbed, prioritize over self-initiated drills (the routing request is explicit asynchronous work assignment)

Optional script (if research session wants automation):
```bash
# notes/research_watchdog.sh — periodic poll
while true; do
  cd d:/AI/hd-instrument
  git pull --rebase --quiet
  ls notes/strategy_request_to_research_*.md 2>/dev/null
  sleep 600  # 10 min poll
done
```

### Testbed session (lightweight pattern)
Behavioral discipline:
- Same as research: pull on every turn + dispatch return
- Watch for `notes/testbed_handoff_*.md` and `notes/exp_dev_handoff_*.md`
- For long engineering work (multi-day implementation), pull at session start each day

Plus a substantive watchdog responsibility: **the dashboard expansion (Tier 1 testbed work) IS the multi-session watchdog**. When complete:
- Per-runner panels show GPU/CPU runner health (already works) + Lambda runner health (new)
- Per-session activity indicators (orchestrator / research / testbed heartbeat files in `data/session_*_heartbeat.json`)
- Inbox-depth indicators per session (counts of unread routing files)

Until the dashboard expansion lands, sessions coordinate by behavioral discipline (the patterns above).

### Cloud session (when active)
- Inherits orchestrator's heartbeat_watchdog pattern but for Lambda runner
- Adds cost-watchdog: auto-shutdown if accumulated cost > budget cap (per anchor + per session)

## Git discipline (load-bearing for parallel work)

### Pull before push, always

```bash
git pull --rebase
# resolve conflicts if any (rare given directory ownership rules)
git push origin main
```

If rebase produces conflicts, STOP and investigate. The 4-session architecture's directory-ownership rules make conflicts rare; a conflict usually indicates either (a) someone violated ownership boundaries, or (b) two sessions worked on the same boundary file (e.g., both wrote a routing file with same name).

### Commit-per-deliverable

Don't batch many small commits. Each deliverable (a research note, an experiment ship, a testbed engineering milestone) = one commit with descriptive message. This makes `git log` useful for finding "what did session X do recently."

### Commit message format

```
<deliverable type>: <one-line summary>

<3-5 line context if needed>
```

Examples:
- `Research delivery: Modern Hopfield theoretical analysis (cross-N + cross-codebook hypotheses)`
- `Testbed milestone: Lambda remote_state_emitter scaffolded; pending integration test`
- `Cap map: v290 -> v291 (X-batch processed; Path D row LIFT to green)`

## What to do when sessions disagree

If research and testbed BOTH propose work that touches the same area (e.g., both want adversarial defense work but in different directions), they file separate routing requests to orchestrator. Orchestrator decides via cap_map cost-benefit + reads any prior decision logs. Decision recorded in `notes/strategy_decisions_<date>.md`.

If a session believes the orchestrator made a wrong cap_map decision, file `notes/strategy_request_to_strategy_<topic>_revisit_<date>.md` with the counter-evidence. Orchestrator reads, decides, records.

The DECISION authority for cap_map is orchestrator-final. The INPUT to that decision can come from any session.

## What to do when you (session) realize you've been working without recent pulls

Apologize to yourself, pull, read what changed, then either:
- Continue (if no conflict)
- Reframe your work (if the context has shifted)
- File a routing request asking orchestrator to coordinate (if your work might duplicate or conflict with what another session just did)

## Cadence summary (the short version)

| Activity | Cadence |
|---|---|
| `git pull --rebase` | Every user turn + every dispatch-return + before every push |
| Read recent cap_map entries (last 3) | Every Pull-before-significant-work |
| Check own inbox (routing files) | Every Pull-before-significant-work + every user turn |
| Tail status_log last 20 entries | When starting a new task OR when confused about context |
| Read full session_architecture + own kickoff | Cold start of session |
| Write your own log_event | Every substantive deliverable |
| Push commits | After every substantive deliverable (don't batch days of work) |

## Recurring user workflows

Cross-session patterns the user repeats; named here so all sessions recognize them.

### Workflow R1: External-Claude synthesis-and-discussion cycle (research-owned)

The user often takes a synthesis of recent project state to an external Claude conversation (no project context), has an exploratory discussion, and brings back angles. This produces fresh-perspective input without giving the external Claude write access.

**Routing:** Goes through the research session. Memory file `feedback_research_synthesis_external_discussion_cycle.md` documents trigger phrases and artifact structure.

**Flow:**
1. User → research: "give me something to discuss with another Claude" (or similar)
2. Research generates `notes/research_synthesis_<topic>_<date>.md` (self-contained for external Claude)
3. User has external discussion
4. User → research: "here's what came out of the discussion" (or similar)
5. Research writes `notes/research_<topic>_<date>.md` with the angles, applying calibration penalty
6. Research files `notes/strategy_request_to_exp_dev_<topic>_<date>.md` for angles warranting experiment dispatch
7. Orchestrator processes routing request, dispatches via exp_dev

Other sessions: if user asks orchestrator or testbed for this pattern, redirect to research session.

### Workflow R2: Cap_map decision request (any source-session → orchestrator)

When research or testbed identifies something cap_map-worthy:
1. Source session files `notes/strategy_request_to_strategy_<topic>_<date>.md` with finding + recommended cap_map action + confidence
2. Orchestrator reads on next pull, processes via strategy_scribe subagent
3. Cap_map bumped (version increment, history entry, decision log entry)
4. Source session sees the bump in cap_map on next pull

### Workflow R3: Experiment dispatch request (any source-session → orchestrator)

When research or testbed needs a substrate-physics anchor dispatched:
1. Source session files `notes/strategy_request_to_exp_dev_<topic>_<date>.md` with spec (anchor name, setup, pre-reg bands, queue choice, justification)
2. Orchestrator reads on next pull, processes via exp_dev subagent
3. Anchor scaffolded, smoke-tested, shipped to queue
4. When verdict lands, orchestrator dispatches verdict_handler
5. Source session sees the cap_map evolution on next pull

### Workflow R4: Testbed engineering milestone (testbed → orchestrator)

When testbed completes a production-engineering milestone that warrants cap_map representation (e.g., "Pattern B integration validated; substrate is empirically deployable for X use case"):
1. Testbed writes `notes/testbed_milestone_<topic>_<date>.md` with what shipped + validation results + production characteristics
2. Testbed files `notes/strategy_request_to_strategy_<topic>_<date>.md` requesting cap_map representation
3. Orchestrator processes as R2

## Related documents

- `notes/session_architecture_v1_2026-05-31.md` — the 4-session model
- `notes/session_kickoff_orchestrator_v1.md` — orchestrator role (this session is also operating from `notes/orchestrator_post_compaction_brief.md`)
- `notes/session_kickoff_research_v1.md` — research role
- `notes/session_kickoff_testbed_v1.md` — testbed role
- `notes/substrate_capability_map.md` — cap_map (the strategic SSoT)
- `data/orchestrator_status_log.jsonl` — For-You feed (gitignored; local-only)
- `MEMORY.md` index → `feedback_cap_map_update_protocol`, `feedback_sessions_self_coordinate`, `feedback_for_you_tab_primary_channel`
