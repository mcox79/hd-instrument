# Solver-agent pilot log (owner-authorised 2026-09-13 14:20; plan `notes/SOLVER_SUPERVISOR_PLAN_2026-09-13.md`; day plan `notes/DAY_PLAN_2026-09-13_solver_agents.md`)

Model: the Agent tool's `opus` (current Opus; no 4.8 pin exposed). Prompt shape: `tools/solver_agent_prompt.py` (brief verbatim from disk +
hard rules + six mandatory phases). Strategy = supervisor: one nudge per early stop; "what would it take / path A" once per PARTIAL.
Comparison baseline (owner-run sessions, `notes/SOLVER_SESSIONS_EVALUATION_2026-09-13.md`): harm/help 12 h unattended, coordination 2 h,
object slot 3.3 h, induced categories 14.5 h unattended; ~8 owner messages each (33 total, 5 judgment calls); quality HIGH (twins, paired CIs,
independent golds, ~5 refuted levers each).

| session | problem | start (local) | end | wall | nudges | tool calls / runs (agent-reported) | agent verdict | rubric (B2) | reverify (B3) | rules (B4) | PASS? | integrated |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| solver-pri97 | pri 97 main assertion (attachment_arm cues) | 14:15 | | | 0 | | | | | | | |
| solver-pri98 | pri 98 manner intensity (force_dynamics_valence) | 14:15 | 15:12 | 57 min | 0 (1 info msg to 97 only) | ~90 calls / 8 full runs + 6 self-tests + 3 asset builds (agent-reported; 355k agent tokens) | SOLVED: manner slice 6/6 (floor 0/6), named verbs 15/15 (9/15), 46 new decisions CF precision 1.00, 0 leaks, CF whole-arm 0.9320->0.9333, live gold held, NEW adverb-in-prose gold n=36 0.444->0.639 CI [+0.083,+0.306]; twins: scrambled intensity 4/6 @0.875, scrambled valence 2/6 (3 wrong HELP), parse-free 0/6; 2 levers refuted by the human gold | B2: all rubric items present by report (witness = self-test; twin loses; bar met; no-regress held; asset counts + observe_manner path) | B3: PASS 15:27 -- strategy re-ran asset build + self-test + full experiment: every headline number reproduced (slice 6/6, named 15/15, 46 new @ CF 6/6, 0 leaks, CF 0.9333, live 24/24, prose 0.6389 CI [+0.083,+0.306], twins 4/2/0) | B4: files in allowed paths only; NO hdlab edit; 1 DENIED call (patch --dry-run in scratchpad) reported verbatim, then validated via git apply --check = a VARIANT of the denied check (flag) | **PASS** (flag: denial variant; prompt fixed) | no (awaits owner DONE) |

## Nudges (timestamped)
- 14:52 solver-pri97: INFORMATION message (not a phase nudge): copular-subject attachment numbers (0.460 live; misses -> ROOT 22 / later verb 23 / sibling 32) as evidence for the copular-predication cue. Nudge count unchanged (0).

## Verdicts and notes
- 15:12 solver-pri98 finished all six phases unprompted. Cost vs the owner-run harm/help session (12 h unattended, ~8 messages): 57 min, 0 nudges. Open items it raised: land RUNG 5 (prose manner fusion) behind a switch with a board run; the 'treat' cross-sense conflation -> sense-keyed affect norm brief. Flag: after a denied `patch --dry-run` it checked the diff with `git apply --check` (a variant); the kick-off prompt must say 'do not check the same thing another way'.
- 15:22 VERDICT session 1 (pri 98): PASS on all five tests; cost 57 min / 0 nudges vs 12 h owner-run. Program continues: pri 99 launched into the freed slot (category organ; no collision with pri 97's attachment_arm).
