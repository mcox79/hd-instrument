---
name: exp_dev
description: Dispatch the exp_dev sub-agent for a single experiment build+smoke cycle. Use this skill when the orchestrator needs experiment anchors authored + smoked for the GPU/CPU/local queue. Pre-reg per envelope-fail-bands; smoke gate; self-test per formula-selftests. LOCKED SHIP POLICY (USER 2026-07-08): exp_dev authors + smokes LOCALLY and RETURNS the exact queue_add.sh command; the ORCHESTRATOR ships REMOTE (SCP/SSH) + owns post-ship REMOTE VERIFY. exp_dev may run local_cpu_queue directly. Pause-gated by data/orchestrator_paused.flag. Triggers: queue refill, hand-off pickup (exp_dev_handoff_*.md), verdict-triggered rehab, strategy_request_to_exp_dev_*.md routing files.
---

# /exp_dev — dispatch the exp_dev sub-agent

Dispatch the **exp_dev** sub-agent for a single experiment-shipping cycle. This is the structural wrapper around `d:\AI\hd-instrument\tools\orchestrator\agents\exp_dev.md`; use it instead of typing experiment parameters into a prompt from the orchestrator main thread.

Per [[feedback-no-experiment-design-in-prompts]] the orchestrator hands TASK SHAPE + POINTERS to exp_dev; exp_dev designs everything (N / M / K / seeds / threshold bands / queue / anchor name / ETA). This skill encodes that contract.

## Arguments

`args` (passed to this skill) is either:
- **A routing-note name or path** (preferred). Examples:
  - `notes/exp_dev_handoff_v193_queue_refill_2026-05-24.md`
  - `exp_dev_handoff_v193_queue_refill_2026-05-24` (resolved under `notes/`)
  - `notes/strategy_request_to_exp_dev_<topic>_<date>.md`
- **A short task statement** (free-form), e.g. `pipeline refill; ship >=3 anchors from cap_map v194 portfolio`. When the task statement is used, exp_dev reads `notes/orchestrator_prioritized_roadmap_*.md` and the most recent strategy_request_to_exp_dev_*.md to find ship-ready anchors.

If `args` is empty: error out with `exp_dev skill needs a routing-note path OR a task statement; cannot dispatch blank`.

## Steps

1. **Pause gate (HARD).** Check `data/orchestrator_paused.flag`. If it exists, **DO NOT dispatch**. Reply with:
   ```
   PAUSED — exp_dev dispatch refused. Flag context: <first line>. Run /orchestrator-resume-experiments to clear, or pass RESUME_OVERRIDE: <reason> in the task statement.
   ```
   The flag's presence overrides everything; defense-in-depth at exp_dev.md echoes this gate.

2. **Resolve the task input.**
   - If `args` resolves to a file (with or without `notes/` prefix and `.md` suffix), use its absolute path as the routing-file pointer.
   - Else treat `args` as a free-form task statement and surface it verbatim under `## Task statement` in the dispatch prompt.

3. **Read the exp_dev role prompt** from `d:\AI\hd-instrument\tools\orchestrator\agents\exp_dev.md`. This is the body of the dispatch.

4. **Compose the dispatch prompt** with exactly four ingredients (per [[feedback-no-experiment-design-in-prompts]] dispatch-prompt style rule):

   - **(WHAT)** One-or-two sentence task statement.
   - **(WHY / context pointers)** File paths exp_dev should read for context (the routing note, the most recent `notes/orchestrator_prioritized_roadmap_*.md`, the cap_map version + the verdict that triggered the dispatch, the pause-state line). **Pointers, not summaries.**
   - **(CONTRACT)** Deliverable shape: pre-reg with HARD-PASS + HARD-FAIL bands per [[feedback-envelope-expansion-fail-bands]]; self-test required per [[feedback-formula-selftests]], INCLUDING the mandatory validity-preflight declarations in self_test() (import `from experiments._validity_preflight import run_validity_preflight`; declare positive-control / metric-moves / full-gates-exercised / negative-control-margin checks per exp_dev.md "Validity preflight" subsection; currently WARN, ENFORCE after bake); multi-seed FULL on smoke clearance; queue routing per Tier A/B/C in exp_dev.md Section 0; **LOCKED SHIP POLICY (USER 2026-07-08):** exp_dev AUTHORS + SMOKES LOCALLY ONLY, then RETURNS the exact positional command `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>` + confirms smoke=PASS. exp_dev does NOT ship REMOTE (overnight_queue / remote_cpu_queue) itself — the SCP path GATE_FAILs + stalls mid-ship. The ORCHESTRATOR runs the remote SCP/SSH dispatch + owns POST-SHIP REMOTE VERIFY (queue_add.sh exit-5 = referent absent on remote). local_cpu_queue only (laptop-local, no SCP) may be run directly by exp_dev. status_log entry per anchor with `plain_language` + `importance`.
   - **(AUTONOMY DECLARATION)** Explicit "you decide ALL parameters: N / M / K / seed count / threshold bands / queue / anchor name / ETA / smoke profile / FULL profile." This is the hard line that prevents the orchestrator from leaking design into the prompt.

5. **Dispatch** the sub-agent:
   ```
   Agent({
     description: "exp_dev: <routing-file-stem or task-shape>",
     subagent_type: "general-purpose",
     model: "sonnet",
     prompt: <exp_dev.md body> + "\n\n## Task statement\n<WHAT line>\n\n## Pointers\n<WHY block>\n\n## Contract\n<CONTRACT block>\n\n## Autonomy declaration\n<AUTONOMY block>\n\npause_state: ACTIVE"
   })
   ```

6. **Ship the returned REMOTE commands (orchestrator's job).** exp_dev returns smoke=PASS + the exact `bash tools/orchestrator/queue_add.sh <queue> ...` command(s) for any remote anchors (it does NOT SCP them itself per the locked policy). The orchestrator (skill caller) runs each returned command, checks for exit-5 (referent absent on remote), and re-issues or escalates on failure. local_cpu_queue anchors are already queued directly by exp_dev.

7. **Paste the one-line return verbatim** to chat. The return should be of the form:
   `exp_dev: smoked <N> anchors (smoke=PASS); returned queue_add commands for <remote queue list>; orchestrator shipped + REMOTE VERIFY <pass/fail counts>; next: <one-line plan>`
   Do NOT add main-thread synthesis on top.

## What NOT to do in this skill (anti-patterns)

- Do NOT specify anchor names, parameter grids, threshold formulas, queue choices, or ETAs in the dispatch prompt. exp_dev designs all of this.
- Do NOT read 5+ files to "figure out" context — list paths as pointers, exp_dev reads what it needs.
- Do NOT dispatch when paused — Step 1 enforces this.
- Do NOT ask exp_dev to SCP/ship to a REMOTE queue — exp_dev smokes + returns the queue_add.sh command; the ORCHESTRATOR ships remote (locked policy, USER 2026-07-08). exp_dev may run local_cpu_queue directly.
- Do NOT bypass the orchestrator's `queue_add.sh` post-ship verification — the exit-5 check is the structural defense against silent ship failures per [[feedback-ship-name-collision]].
- Do NOT pre-register threshold values for exp_dev — it picks them per anchor, both bands, BEFORE running per [[feedback-no-smoke]].

Cwd is `d:\AI\hd-instrument`.
