---
owner_verdict: DONE
---

Problem: no_shared_shallow_predicate_argument_front_end — done, ready for review (PARTIAL).

WHAT IT WAS: the reader had three separate hand-written copies of "who did what / where,"
and the proven role modules were all sitting unplugged. Verified on disk: there is no shared
predicate-argument front-end, the validated role organs are islanded, and the "coref
caused-motion residual" the brief named does not exist in the coref code (a correction).

WHAT I BUILT: one shared module that maps a parsed sentence to roles — agent, moved-thing,
goal, location, path, source, recipient — built on how the brain actually decides spatial
roles (the preposition's telicity + the verb's event-class + the caused-motion construction;
Jackendoff/Talmy/Zwarts), NOT a hand-list of motion verbs. Glass-box, no external model.

KEY VALIDATED RESULT: on FrameNet's expert-labeled gold (~59k real-prose items) it correctly
separates location / path / source / recipient — five role types the current conflating rule
scores exactly 0.0 on — all CI-separated, scrambled control below each; caused-motion
theme-attribution 8/8. I then drilled the biggest remaining limit (which phrase attaches to
which verb) to the brain's verb-prediction mechanism, built it, and — after catching a
measurement leak with my own control — showed it genuinely recovers a majority of the parse
gap where the parser is weakest (path 60%, source 92%), a minority elsewhere.

HONEST BOUNDS: on raw "destination" recall the naive blind-grab rule still wins (it calls every
spatial phrase a destination); the leftover parse errors need the better parser we already have
on the shelf (a separate follow-on), NOT a richer word-representation (drilled and ruled out).

FOR STRATEGY: land the shared dispatch default-off, de-duplicate the three inline copies with
measured no-regression, on owner-DONE. Ranked follow-on problems are in SOLVED.md's next-problem
map (incremental-parser swap = biggest lever; recipient-span resolver; representation coupling).

REVERIFY: .venv/Scripts/python.exe experiments/exp_shared_predarg_frontend_v2.py --self-test
FILES: experiments/exp_shared_predarg_frontend_v{1,2,3}*.py, the minimal-pair gold + metrics dirs,
and SOLVED.md — all in experiments/, data/, and the problem folder. No hdlab/ touched.
