# Orchestrator skill-pickup — v193 hand-off via /exp_dev

**Filed:** 2026-05-24 by orchestrator-tasks sub-agent (Task 4 deliverable).

## Status

- `/exp_dev` skill: LANDED at `C:\Users\marsh\.claude\commands\exp_dev.md`
- `/research` skill: LANDED at `C:\Users\marsh\.claude\commands\research.md`
- Pause flag: ABSENT (state ACTIVE)
- All 3 queues: IDLE per dashboard snapshot (`gpu_pending=0`, `cpu_pending=0`, `local_cpu` field missing)
- Watchdog: armed and emitting `silent_idle` events (confirms idle, paused=false)

## Main-thread next action

The orchestrator main thread should invoke `/exp_dev` with the v193 hand-off as the argument. Two equivalent invocations:

```
/exp_dev notes/exp_dev_handoff_v193_queue_refill_2026-05-24.md
```

or (shorter form, the skill resolves under `notes/`):

```
/exp_dev exp_dev_handoff_v193_queue_refill_2026-05-24
```

The skill will:

1. Verify pause flag is ABSENT (defense-in-depth; exp_dev.md role prompt also has its own pause gate).
2. Read the hand-off note for context pointers (it names anchors 1-9 with priorities and queue defaults — TASK SHAPE only, NOT parameters).
3. Read the exp_dev role body from `tools/orchestrator/agents/exp_dev.md`.
4. Compose the dispatch with the 4-ingredient style rule (WHAT / WHY pointers / CONTRACT / AUTONOMY DECLARATION) and fire the Agent dispatch with `model: "sonnet"`.

## What exp_dev should ship this cycle (target)

Per the v193 hand-off: **>=3 anchors landed** (1 GPU + 1 remote CPU + 1 local/analyzer minimum). exp_dev decides anchor selection from the 3-mandatory + 6-optional list:

**Mandatory (3):**
1. R-PRIME-2 MoE M_c falsifier (GPU)
2. Field-A reservoir-computing Lyapunov spectrum (remote CPU)
3. Bet D analyzer pass at K=32 / K=64 (local/analyzer)

**Optional (6):** F-6 Boolean re-ship, MS_1ST_ORDER script-fix, Bet M log-forgetting fit, R-PRIME-3 RESCUES, K2 mechanism-class rescues M1-M4, K6 axes 2/3/4.

exp_dev designs ALL parameters (N / M / K / seeds / threshold bands / queue / anchor name / ETA). The hand-off note + roadmap + research notes are pointers.

## Post-ship expectation

exp_dev returns one line:

```
exp_dev: shipped <N> anchors to <queue list>; REMOTE VERIFY <pass/fail counts>; next: <one-line plan>
```

Orchestrator pastes verbatim, fires a status_log entry per anchor (or exp_dev does it itself per its role prompt), and re-arms verdict_handler for the first verdict to land.

## Why this is the right path (and NOT inline-exp_dev from the tasks sub-agent)

Per [[feedback-structural-agent-usage-mandate]] and Section 2 of `notes/orchestrator_post_compaction_brief.md`, substantive multi-file work (3 experiment scripts + 3 preregs + 3 smoke runs + 3 ships + REMOTE VERIFY) belongs to a dedicated sub-agent, not to a generalist orchestrator-tasks sub-agent. The new `/exp_dev` skill IS the dedicated dispatch path. The tasks sub-agent's job here is to land the skill files + document the pickup; the main thread fires the skill.

The runtime did not expose an `Agent`/`Task` tool to this tasks sub-agent (sub-agents cannot recurse), so the only way to actually fire `/exp_dev` is from the main thread. That fire happens immediately after the tasks sub-agent returns.
