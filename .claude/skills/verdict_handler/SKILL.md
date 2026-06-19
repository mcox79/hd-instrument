---
name: verdict_handler
description: Dispatch the verdict_handler sub-agent to process a completed experiment verdict end-to-end. Use this skill for every verdict event (PASS / FAIL / PARTIAL / UNKNOWN / HARD-PASS / HARD-FAIL / KILLED / SATURATION / MIDDLE_BAND) from dashboard recent_verdicts or event_outcome_file. Internally composes Step 0 (honest re-read of verdict_msg vs per-cell metrics) + parallel strategy (cap_map decision, atomic commit) + visibility (decisions log) + status_log entry + optional exp_dev queue-refill (pause-gated). Returns ONE line; orchestrator pushes commit hash as 1-tool follow-up.
---

# /verdict_handler — dispatch the verdict_handler sub-agent

Dispatch the **verdict_handler** sub-agent to process a verdict payload end-to-end. This is the structural wrapper around `d:\AI\hd-instrument\tools\orchestrator\agents\verdict_handler.md`; use it instead of typing 2 parallel Agent calls (strategy + visibility) plus a chat synth from the orchestrator main thread.

Per [[feedback-structural-agent-usage-mandate]] the orchestrator's main thread issues ONE agent dispatch per verdict event, NOT 2 + a synthesis. verdict_handler internalizes the verdict-handling flow (Step 0 honest re-read, parallel strategy+visibility fan-out, pipeline-pacing exp_dev refill gated on pause flag, status_log entry, one-line return).

## Arguments

`args` is either:
- **A verdict payload block** (preferred). Example:
  ```
  name: wave14_X_v1
  verdict: FAIL
  verdict_msg: lift=0.004 flat across K
  metrics_file: data/wave14_X_v1/metrics.json
  ```
- **An experiment anchor name** (free-form), e.g. `MOE_KSWEEP_HARD_FAIL_REJECTED`. When the anchor name is used, verdict_handler reads `data/<name>/metrics.json` + the dashboard's recent_verdicts to assemble the full payload.
- **Empty** — defaults to the MOST RECENT verdict in `data/local_dashboard_snapshot.json` recent_verdicts list. Useful when the orchestrator wakes on a dashboard event and the latest verdict is what needs handling.

## Steps

1. **Read the verdict_handler role prompt** from `d:\AI\hd-instrument\tools\orchestrator\agents\verdict_handler.md`. This is the body of the dispatch.

2. **Resolve the verdict payload.**
   - If `args` is a multi-line block with `name:` / `verdict:` / `verdict_msg:` keys, use it as the payload.
   - If `args` is a single token, treat as anchor name; build the payload by reading `data/<name>/metrics.json` if present + the dashboard recent_verdicts entry.
   - If empty, read `data/local_dashboard_snapshot.json` and take the most-recent recent_verdicts entry.

3. **Compose the dispatch prompt** with the four ingredients per [[feedback-no-experiment-design-in-prompts]] dispatch-prompt style rule:

   - **(WHAT)** "Process this verdict end-to-end."
   - **(WHY / context pointers)** The verdict payload + pointers to: `notes/substrate_capability_map.md`, the corresponding `metrics_file`, the latest `notes/strategy_decisions_<date>.md`, the pause-state line (`test -f data/orchestrator_paused.flag`).
   - **(CONTRACT)** Per `tools/orchestrator/agents/verdict_handler.md`:
     - **Step 0 — honest re-read MANDATORY** before any cap_map decision (compare `verdict_msg` label against per-cell metrics; if OVER-CLAIM, file labeled-vs-honest entry, treat honest reading as authoritative downstream, prefix return with `[label-vs-honest]`).
     - **Step 1 — parallel strategy (Opus) + visibility (Haiku)** fan-out; WAIT for both; strategy commits cap_map locally + history + decisions atomically (PROT-008/009 validator), surfaces commit hash in return; sub-agent context cannot push (harness security classifier), so commit hash must be surfaced for main-thread push.
     - **Step 2 — pipeline-pacing GATED on pause flag.** If `data/orchestrator_paused.flag` exists OR `pause_state: PAUSED` in context → SKIP exp_dev dispatch; note `[pipeline-pacing skipped: PAUSED]` in return. Otherwise, if `queue_state_at_arrival.pending == 0`, dispatch exp_dev for refill in parallel with Step 3.
     - **Step 3 — status_log entry MANDATORY** via `tools/orchestrator/state.py log_event` with `plain_language` (1-2 sentences for non-expert) + `importance` (CRITICAL / HIGH / MEDIUM / LOW).
     - **Step 4 — return ONE line** of the form `<name> <verdict_tag>: <verdict_msg>. <strategy_outcome>. <visibility 1line>. [Queue refill: <exp_dev outcome>] [Cap_map: v<N> <change>]`.
   - **(AUTONOMY DECLARATION)** Explicit: "you decide ALL of: cap_map state transition, rescue-sketch count and content for closures (PROT-004/006), routing files to file, importance tier for status_log entry, queue-refill task shape if dispatched."

4. **Dispatch** the sub-agent:
   ```
   Agent({
     description: "verdict_handler: <anchor name or verdict tag>",
     subagent_type: "general-purpose",
     model: "opus",
     prompt: <verdict_handler.md body> + "\n\n## Verdict payload\n<WHAT block>\n\n## Pointers\n<WHY block>\n\n## Contract\n<CONTRACT block>\n\n## Autonomy declaration\n<AUTONOMY block>\n\npause_state: <ACTIVE|PAUSED>"
   })
   ```

5. **After return: 1-tool mechanical push (if commit hash present).** verdict_handler will surface the local cap_map commit hash in its return per Step 1. The orchestrator main thread executes `git push origin main` as a 1-tool mechanical action — wrappers cannot push from sub-agent context (harness security classifier; [[feedback-subagent-permission-inheritance]]).

6. **Paste the wrapper's one-line return verbatim** to chat. Do NOT add main-thread synthesis on top.

## What NOT to do in this skill (anti-patterns)

- Do NOT do strategy's job (cap_map writes) in main thread.
- Do NOT do visibility's job (decisions log) in main thread.
- Do NOT skip Step 0 — over-claimed verdict_msg labels MUST be re-read against per-cell metrics per [[feedback-verdict-msg-honest-reread]].
- Do NOT skip pipeline-pacing pause-flag check per [[feedback-obey-user-pause-explicitly]].
- Do NOT push from inside the wrapper — the security classifier blocks it.
- Do NOT integrate 3 sub-agent returns into a multi-line chat narrative — verdict_handler returns ONE line; paste verbatim.

Cwd is `d:\AI\hd-instrument`.
