# CLAUDE.md

Conventions for AI-assisted work in this repository.

## Project

`hd-instrument` is an observable hyperdimensional computing substrate. See [PLAN.md](PLAN.md) for the full build plan and [PROGRESS.md](PROGRESS.md) for current status.

## SESSION STARTUP RITUAL (FIRST ACTION OF ANY SESSION LIFETIME, ALL ROLES)

### STEP 0 (research role, post-compaction recovery):

Before arming Monitor, query the substrate-Director-KB for the post-compaction backup doc:

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp
python d:/AI/hd-instrument/tools/director_kb_query.py --filename-contains POST_COMPACTION_BACKUP --source-class=notes
```

The query returns the BACKUP file at rank 1 (cosine=1.0). READ the source file end-to-end — it's self-contained with all USER directives, cortex state, in-flight work, milestones, recovery procedure for the active session. This is the load-bearing first action for any research session that's been compacted; skip only if `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_<date>.md` doesn't exist (in which case grep filesystem for whatever's most recent). See MEMORY.md "READ FIRST AFTER COMPACTION" callout for the full sequence.

### STEP 1 (research role): agent-spawn is the operating model

Research is the director. Main session does judgment, strategy, direction, and 1-off important work. Sub-agents do the rote and heavy work — cell authoring, smoke iteration, landed-VET, atomization, dispatch, infra refinements.

Spawn `hdi_<role>` sub-agents via the Agent tool. Available roles: `hdi_exp_dev` (cell author + smoke + local dispatch), `hdi_skunkworks` (landed-VET + atomization; AUDIT-ONLY), `hdi_orchestrator` (push + remote queue_add + state sync), `hdi_testbed` (infra refinements + 2nd-witness on cross-cutting changes).

**Main thread (director's work):**
- Strategy + goal direction + thinking through the process
- 1-off important docs (BACKUP, memory rules, plan updates)
- Reading metrics.json / verdict_msg (verification)
- Running observability tools (`tools/runner_status.py`, `tools/peek_arm_metrics.py`, dashboard reads)
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

**Default to `run_in_background: true` for `hdi_*` spawns.** Foreground Agent calls BLOCK the main session — Director can't respond to USER, can't dispatch follow-up work, can't author docs. Background mode (`run_in_background: true`) returns an agentId, fires a notification on completion, and keeps the main session responsive throughout. Use foreground only when the very next action depends on the spawn's return value AND there's no other useful work to do meanwhile (rare).

**Spot-check, don't re-do:** when a sub-agent returns, verify by reading 1-2 specific metrics or hash-checking a cited result. If wrong, escalate via SendMessage with the delta — don't restart with a fuller prompt.

**Violation tripwire:** if you see yourself typing `experiments/*.py` in an Edit tool or running smoke via Bash, that's the moment — STOP and spawn `hdi_exp_dev` instead.

## Notes directory (single-session model)

`notes/` is for Director's session-internal artifacts (BACKUP doc, research decisions log, status digests). It is NOT a cross-session mailbox — the 4-session fleet model is dead. Sub-agents communicate via SendMessage (in-conversation), not via `notes/` files. Do NOT use `<from>_to_<recipient>_*.md` filenames; those came from the legacy ferry mechanism. Pick a topic-slug name that describes what the doc IS, not who it's TO.

Filename cap: 120 chars (incl. `.md`). Topic-slug 5-10 words snake_case; optional ALL_CAPS for emphasis.

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
