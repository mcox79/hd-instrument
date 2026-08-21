# RETIRED DASHBOARD PANELS -- 2026-08-21

**Nothing here is deleted. These nine panels were moved out of `data/` because they are ORPHANED:
no tool in `tools/` writes them any more, so they can never update again.**

**Owner, board Q99:** *"I want the only things in the gui to be regularly updated. static windows
that get old are useless. Evaluate what is genuinely useful here, keep it, and make sure it's
effortless to maintain."*

## WHY THESE AND NOT OTHERS -- ORPHANED vs IDLE

**Age alone could not decide it.** A panel that is stale because *nothing is running* comes back by
itself the moment work resumes. A panel with **no writer at all** never will. So the test is not
"how old is it" but **"does any live tool still write it"** -- implemented in
`tools/dashboard_staleness.py::has_live_writer()`, which excludes itself (a tool that mentions every
panel would otherwise certify all of them healthy) and excludes `_`-prefixed one-off scripts.

| retired (ORPHANED -- no writer) | content age at retirement |
|---|---|
| `orchestrator_questions.md` | 90 days |
| `strategy_request_to_exp_dev_cycle49_refill.md` | 78 days |
| `cycle_responses.md` | 61 days |
| `research_work_queue.md` | 60 days |
| `gpu_fill_queue.md` | 60 days |
| `research_master_plan.md` | 60 days |
| `fleet_waiting_on.md` | 56 days |
| `autonomous_loop_instructions.md` | 55 days |
| **`fleet_status_NOW.md`** | **content dated 2026-06-30 (52 days) although its mtime read 4 days** |

**`fleet_status_NOW.md` is the instructive one:** its file timestamp said 4 days old while its own
body said *"Last update: 2026-06-30"*. **A timestamp is not evidence of currency.** It was retired on
the writer test, which is not fooled by a touch.

## WHAT WAS KEPT, AND WHY

| kept | writer | state |
|---|---|---|
| `data/inflight_status.md` | `tools/inflight_monitor.py` | **IDLE** -- 9 days, updates when work runs |
| `data/latest_landings.md` | `tools/landing_notifier.py` | **IDLE** -- 7 days, updates on each landing |
| `data/certification.md` | a skunkworks atomize script | **IDLE** -- 4 days |

*The genuinely live surfaces are not in `data/` at all: `notes/STATUS.md` (rewritten every session and
size-guarded by the session hook), `notes/BOARD.md` (rewritten by `tools/board.py`) and
`notes/COMMENTARY.md` (the owner's own channel).*

## THESE ARE RELICS OF THE RETIRED 4-SESSION FLEET

*They describe runner PIDs, a Testbed that overwrites them each cycle, and a queue-refill protocol.
That architecture is recorded as dead ("4-session model DEAD; agent-spawn only"). The panels did not
rot -- **their writer was switched off and nothing replaced it**.*

## TO RESTORE ANY OF THEM

`git mv data/retired_2026-08/<name>.md data/<name>.md` -- and if you do, give it a writer, or it
will be back here next time.

## KEEPING IT EFFORTLESS

`python tools/dashboard_staleness.py` reports every panel with its age, whether it claims to be
current, and now whether it has a live writer. Re-runnable, idempotent, changes nothing without
`--apply`.
