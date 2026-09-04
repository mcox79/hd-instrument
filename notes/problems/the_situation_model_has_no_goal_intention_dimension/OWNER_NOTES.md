---
owner_verdict:
---

# Owner notes -- the_situation_model_has_no_goal_intention_dimension

(owner_verdict is BLANK -- this is the solver's hand-back; the owner sets DONE when satisfied. Strategy
integrates ONLY on owner_verdict: DONE.)

## What this is, in plain language
The reader could track what happened in a story, who did it, when, where, what physically caused what, and
what characters believed -- but nothing about what any character WANTED or was TRYING to do. That is the
last of the five classic "situation model" dimensions psychologists use to describe story understanding
(intentionality / goals), and it is the backbone of most stories (goal -> plan -> action -> outcome). I
built it: a per-character goal-tracker that reads goals from the plain "wanted to / tried to / in order to"
phrasings, ties each goal to the right character, tracks whether it was reached, and answers goal questions.

## What we are submitting (the parts)
1. **A glass-box goal register** (no external AI, no black box) that reads each character's goals from the
   reliable explicit phrasings and binds them to the right character using the reader's existing character
   tracker. `experiments/goal_register.py`.
2. **A measurement on 100 real story chapters** proving it works and where it doesn't.
   `experiments/exp_goal_register_qa_v1.py`.
3. **A self-checking witness** (8/8 checks) that re-verifies the claims without re-running the big job.
   `verification/test_goal_register.py`.
4. **The brain-mechanism research** it is built on. `research_goal_intention_brain_mechanism_2026-09-04.md`.

## The headline numbers (plain)
- "What is she trying to do?" on the reliable phrasings: right about **53%** of the time, vs **20%** for
  just naming her most recent action, vs **3%** if you scramble which character each goal belongs to. (The
  53% is capped because a character can hold several goals and we return the current one; the point is it
  crushes the trivial baselines.)
- "Why did he do that?" answered with the GOAL **98%** of the time, where the physical-cause tracker gets
  it **4%** -- and on physical "why" questions the physical-cause tracker gets **85%** where the
  goal-tracker gets **1%**. So the two are genuinely different, complementary tools (which the psychology
  predicts).
- It ties each goal to the RIGHT character: on multi-character passages it is right where a
  character-blind guess is wrong **827** times, vs the reverse only **4** times.
- Whether a goal was reached/abandoned/still-open: **100%** on clean hand-made examples vs **33%** for a
  tracker that never updates.

## Where it honestly falls short (measured, named)
- **Implied goals** (never said out loud -- "he picked up the knife" -> "to attack") need real-world
  knowledge we do not yet have. This is the same missing "meaning channel" several other problems hit.
- **Messier "did-X-in-order-to" phrasings on old literary prose** need a better grammar parser than the
  lightweight one we use (precision drops from 85% to 33% on that slice, measured against a reference
  parser). Same parser limitation other dimensions hit.
Both are the "explicit vs implied" split the brief itself predicted -- a rigorous located negative, which
the brief says is a full pass.

## What strategy would land (only after you mark DONE)
A default-off `track_goals` switch on the reader (mirrors the belief/world-state switches exactly -- purely
additive, changes no other dimension), plus a `goal` row on the board's question test. Details in SOLVED.md
§5. Nothing is wired into the live reader yet (solver scope).

## Reverify
`.venv/Scripts/python.exe verification/test_goal_register.py`  -> 8/8 PASS (re-runs no landed cell).
