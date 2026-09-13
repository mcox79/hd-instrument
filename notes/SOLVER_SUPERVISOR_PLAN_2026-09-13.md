# Solver-supervisor plan — running solver sessions as agents (owner-authorised 2026-09-13 ~14:20 local)

**Why:** the evaluation of the four owner-run opus solver sessions (`notes/SOLVER_SESSIONS_EVALUATION_2026-09-13.md`) showed the
owner's guidance was a fixed four-step script broadcast to paired tabs, with only 5 of 33 messages being judgment calls (all pushing a
PARTIAL toward its strongest honest form). The owner asked strategy to try the same with agents: **"run 2 solver sessions in opus
agents to see how you do."** This supersedes, for this pilot, the 09-12 rule "never an opus Agent from here" (the constraint was usage
accounting; the owner now accepts it for two sessions).

## The pilot (run after the next compaction)
- **Model:** `model: "opus"` on the Agent tool (the current Opus; the tool does not expose a 4.8 pin -- say so in the report).
  `subagent_type: "general-purpose"`, `run_in_background: true`, one agent per problem, NO fan-out inside the agent.
- **Problems (different organs, no diff collision):** **pri 97** `the_main_assertion_is_a_scorer_deficit_...` (attachment arm cues:
  finiteness / copular predication / subordination -> root) and **pri 98** `manner_encoded_harm_needs_an_intensity_read_...`
  (force_dynamics_valence + affect norms + grounded channel). Pri 94 (PP) is NOT paired with 97 (both propose attachment_arm diffs).
- **Prompt = the PROBLEM.md verbatim + the standing SOLVER OPERATING PROTOCOL (already inside each brief) + the supervisor script
  as MANDATORY PHASES the agent must execute itself:**
  1. READ the brief's "verify before you start" files in full; restate the bar; list the upstream chain with BF status per rung.
  2. BUILD the brain's mechanism; get the first measured result with floor + twin + CI.
  3. STATUS PROBE (the owner's first checkpoint, verbatim): "how are we performing against the brain, and where do we lose signal
     upstream? are all upstream components brain-foundational?" -- answer it in writing with numbers, then act on it.
  4. QUALITY PUSH (verbatim): "go after the remaining opportunities, BF and right not easy" -- at least one more lever, measured.
  5. VERDICT CHECK against the rubric: witness green; twin loses CI-sep; the bar's CI-separated margin met; no regression on the named
     no-regress populations. If PARTIAL: write "what would it take to make this fully solved", pick the cheapest path ("path A"),
     TRY IT ONCE, re-measure.
  6. FINALIZE (verbatim): documentation highlighting every component interacted with or created and its BF status, priority next
     steps, SOLVED.md with the frontmatter schema (status/bar/result/floor/controls/files_changed/reverify), the proposed hdlab diff
     as a patch file, and a brief submission prompt in a code box that includes the original problem name.
  - Hard rules in the prompt: write ONLY the files the brief names; never edit hdlab/ or tools/ (propose diffs); commit path-limited
    with the standard trailer; never push; never edit preregs/** or arm_key*; cap cores (OMP_NUM_THREADS=2); if a tool call is
    denied, stop and report; do not fan out to sub-agents.
- **Strategy as supervisor:** on each completion notification, read the agent's report; if it stopped before phase 6 (the known
  "ended its turn early" failure), SendMessage the next phase verbatim; if it reports PARTIAL, send "what would it take... path A -
  try it" once. Log each nudge in `notes/OVERNIGHT_PLAN_2026-09-12.md` (or the next day's plan) with timestamps.
- **Measure the pilot itself** (to answer the owner's question): wall time, turns/tool calls (from the agent's output file size or
  its report), number of supervisor nudges needed, and the result quality vs the four owner-run sessions (twins, CIs, golds, refuted
  levers, honest caveats). Then integrate on the owner's DONE as usual.

## Rubric for DONE-readiness (what the owner's verdict check encoded)
witness green; info-free twin loses CI-separated; the bar's primary metric up CI-separated on the item's own population; named
no-regress populations hold; knowledge in counts/assets with an online observe path; negatives numbered and located (never "ceiling");
documentation names every component touched + BF status + next steps; a proposed diff, not an hdlab edit.

## Fallback
If opus agents are unavailable or denied, run the same prompts as haiku-supervised sonnet agents for the BUILD phases and report the
difference; never route around a denial.
