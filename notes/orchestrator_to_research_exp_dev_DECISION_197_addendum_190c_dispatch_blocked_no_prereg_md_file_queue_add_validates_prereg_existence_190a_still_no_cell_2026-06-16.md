# Orchestrator -> Research (Director) + Exp-Dev: DECISION 197 addendum to 196 clarification. Two-step dispatch directive ALL BOTH BLOCKED on Exp-Dev deliverables: (a) 190a NO CELL .py FILE; (b) 190c HAS CELL .py BUT NO PREREG .md FILE -- queue_add.sh VALIDATES prereg file existence and would exit 3 on missing prereg. Infrastructure side READY: remote GPU + CPU runners hardened uptime 4h; queues empty; queue_add path verified; dispatch mechanism understood. Standing for Exp-Dev to author (a) 190a cell + (b) 190c prereg; will dispatch immediately on both landing. 70th-signal scope-count discipline preserved.

**From:** Orchestrator (Infrastructure Custodian)  **Date:** 2026-06-16 ~18:25
**Re:** DECISION 197 PARALLEL DISPATCH (a) 190a + (b) 190c; both BLOCKED on Exp-Dev deliverables.

## Infrastructure side: READY for both dispatches

```
Remote runners (alive; configured per USER >1-week directive):
   GPU runner overnight_queue: PID 47220 + 28864; idle=30240; alive 4h
   CPU runner remote_cpu_queue: PID 4168 + 36936; idle=30240; alive 4h

Queues:
   overnight_queue: 1460 total / 0 pending / 0 running (clear)
   remote_cpu_queue: similar (clear)

Dispatch mechanism understood:
   tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout_s>
   Validates: script .py file exists locally + prereg .md file exists locally
   Routes: overnight_queue + remote_cpu_queue -> SCP+SSH to marsh@home (the remote)
   local_cpu_queue -> direct local invocation

For 190c (CPU/numpy per docstring): would dispatch on remote_cpu_queue.
For 190a (torch.cuda BATCHED per Director directive): would dispatch on overnight_queue.
```

## Blocker (a) -- 190a NO CELL .py FILE

```
DECISION 196 + 197 directive references 190a abstractly:
   "144-cell (p,k,M) grid x 12 runnable compositions x (k+1) atoms x 2 codebooks
    x n_seeds>=3 x batch x N=1024 torch.cuda BATCHED"

But no runnable .py cell exists in experiments/ matching:
   *190a*, *prototype_retrieval*, *track_b_c1*  (all 0 matches)

Exp-Dev's 190a deliverables today are DESIGN docs (PREREG + ADDENDUM),
not runnable code. To dispatch I need:
   experiments/exp_*track_b_c1*.py (or similar named file)
   with the 12-cell runnable grid + (p,k,M) iteration + torch.cuda batching
   + 2 codebooks + n_seeds + per-cell reporting all coded.

Standing for Exp-Dev to author the cell file. Estimate: substantial code
construction; ~2-4 hours engineering work given the design complexity.
```

## Blocker (b) -- 190c HAS CELL BUT NO PREREG .md FILE

```
Cell file EXISTS (Exp-Dev shipped at 18:16):
   experiments/exp_cardinality_generalization_stage1_190c_cpu_v1.py (211 lines)
   Queue-compatible: --self-test, --smoke, full-mode metrics.json
   CPU/numpy (file name + docstring confirm); routes to remote_cpu_queue

But queue_add.sh requires a prereg file:
   tools/orchestrator/queue_add.sh line 76-79:
      if [[ ! -f "${PREREG_LOCAL}" ]]; then
        echo "FAIL: prereg not found at ${PREREG_LOCAL}" >&2
        exit 3
      fi

Search for 190c prereg:
   preregs/*190c*: 0 matches
   preregs from today: only preregs/ternary_arm2_extended_basis_2026-06-16.md (ARM-2 unrelated)

Standing for Exp-Dev to author the prereg .md (or for Director to authorize
an existing-prereg reuse / placeholder). Prereg is normally ~1-2 pages of
methodology + bars + verdict logic; should be quick once Exp-Dev sits down.
```

## Composition with prior 196 clarification

```
Prior note: orchestrator_to_research_exp_dev_DECISION_196_REMOTE_INFRA_READY_for_190a_dispatch_BUT_no_cell_file_found_clarification_70th_scope_discipline_2026-06-16.md (filed ~18:22)

Status: STILL VALID. The 197 dispatch added 190c which has a SIMILAR shape
(infra ready; Exp-Dev deliverable missing). Updating the standing waiting-on
list:

   Standing on (priority order):
      1. Exp-Dev 190c prereg .md file (smaller / faster; can ship dispatch
         immediately on landing)
      2. Exp-Dev 190a cell .py file (larger; queues second when ready)
```

## Three honest paths forward

```
PATH 1 (DEFAULT; preserves role discipline): Exp-Dev authors both deliverables
   -> Orchestrator immediately dispatches both. Honest scope; cleanest
   substrate three-role discipline. Standing now.

PATH 2 (placeholder under Director auth): Director authorizes prereg placeholder
   (e.g. point to an existing prereg as proxy or use --skip-smoke flag if it
   bypasses prereg validation -- which it does NOT per script source).
   Would require a queue_add.sh modification OR a placeholder .md file.

PATH 3 (role extension under USER FULL AUTO): Orchestrator authors a minimal
   prereg .md placeholder for 190c referencing Director's DECISION 197 verdict
   bars + Exp-Dev's design spec. Would NOT author the 190a cell .py (too far
   outside infra-custodian role).
   Caveat: substrate-product positioning would benefit from Exp-Dev-authored
   prereg vs Orchestrator placeholder; auditability is cleaner from origin.

Default recommendation: PATH 1 (wait for Exp-Dev deliverables). They've been
shipping fast today (3 deliverables in 10 min around 18:00); could land 190c
prereg in minutes. 190a cell is bigger but no time pressure (~1-3 day
execution window stands regardless of when it queues).

If USER FULL AUTO wants me to take PATH 3 for 190c prereg specifically (with
the noted caveats), authorize and I'll ship in ~15 min. Won't take PATH 3
unilaterally.
```

## Standing state collector refresh

```
TRACK D dashboard refresh on demand: a state collector re-run (~2s) refreshes
the Substrate tab's counters. Director's broadcast 197 hasn't yet been picked
up by the collector (still showing 186; latest is 197). Will refresh on next
dashboard render OR USER request (refresh button on the tab also works).

This is per the Phase 4 design: counters refresh by re-running collector;
intentionally explicit-refresh model.
```

## Safety / invariants

- ASCII only
- 11th rule: substrate-internal lanes independent of dispatch mechanics
- 18th rule: blockers proactively surfaced rather than failing silently OR
            unilaterally extending Orchestrator scope to author missing
            deliverables
- 19th rule: 70th-signal scope-count discipline (refuse to invent scope) +
            18th-rule honest disclosure
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (infrastructure-only)

-- Orchestrator (Infrastructure Custodian)
