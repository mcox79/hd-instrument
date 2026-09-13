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

## OWNER CORRECTION (2026-09-13 15:55): ALWAYS send the understanding + improvement probe -- even to a session that reports finished
The owner: "I have found zero times that the agent was able to push to the end without guidance. Almost always, if you ask if the agent
fully understands and if not, research, and then if there are opportunities for improvement, it will find many." So phase 6 is NOT the end.
**Phase 7 (mandatory, sent by the supervisor after EVERY final report, including a SOLVED one):** (a) "Do you fully understand the problem
and the whole chain it sits in? If not, research it now and write what you learned." (b) "Are there opportunities for improvement -- BF and
right, not easy? Find them deliberately (name the residuals, the upstream losses, the unmeasured parts), build and measure each the same way,
keep what the gold accepts, record what it rejects; update SOLVED.md / the patch / the metrics; report the new numbers." Repeat (b) once more
if the first pass found improvements. A session's row in the pilot log is not closed until phase 7 has run; "0 nudges" is a defect of the
supervisor, not a merit of the session.

## OWNER MANDATE (2026-09-13 16:00-16:05): signal-loss trace, upstream BF per signal, the brain's math per chain, every negative understood, and WHY the wins won
"A key request for any solver working on a component with upstream components, is to track exactly where the signal is being lost, confirm any
BF status of upstream components as it relates to the signal that the end component needs, and research how that signal should be handled,
mathematically, in the brain along each chain on down. This helps isolate where the loss occurs, and there is almost always a number of
opportunities to fix it. Additionally, research all negatives encountered until fully understood similarly opens up new avenues for optimization
and upgrades." And: "evaluate the most successful improvements -- what was it about the problem that allowed you to maximize signal so well.
It's almost always going to be that you cracked the real, mathematical BF chain all the way to the top." -> baked into phases 3, 5 and 6 of
`tools/solver_agent_prompt.py`; sent to the three running sessions (97, 98, 99) as binding directives; the supervisor checks SOLVED.md for the
trace, the per-rung BF table, the brain-math comparison, the understood negatives and the why-the-wins-won evaluation before presenting for DONE.

## OWNER RULES (2026-09-13 16:08): measure the prodding yield; loop until exhausted; alternate paths in the readback
"I definitely want to know how much that extra prodding produced in the solvers." -> the pilot log carries, per session, a BEFORE/AFTER table
of every headline number at the first final report vs after each phase-7 round (the yield of the prodding), plus the rounds needed.
"Eventually, when you ask if they know everything and if there are additional opportunities for optimization/upgrades, it will say that it's
entirely exhausted. That's when you end, and the readback should include any identified alternate paths or ways to do this that are similarly
or more brain foundational." -> phase 7 REPEATS (understand? research. opportunities? build+measure) until the session says the opportunities are
entirely exhausted; only then does the supervisor close the row and present for DONE; the final readback must list ALTERNATE PATHS (brain
structure + computation, math, what it would take, why not now), which strategy queues as briefs. Baked into phase 6 of the kick-off prompt.
