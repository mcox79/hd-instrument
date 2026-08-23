---
owner_verdict: DONE
---

SUBMISSION — problem: the_grow_by_reading_pass_has_no_floor — status: SOLVED

WHAT WAS ASKED
Our best evidence that the system learns by reading — an extractor scoring 90/100 on what-happened-
to-things — had no floor under it. The 90% was measured only on sentences that survived six filters
throwing away two-thirds of the output. Nobody checked what a dumb method scores on those same
survivors, so the number could mean "reads well" or "kept only the easy sentences."

THE ANSWER (all on the SAME 100 survivor sentences the 90% was scored on)
  real extractor .............................. 0.90
  trivial "grab the noun next to the verb" .... 0.70   (real beats it +0.23, CI [+0.13,+0.33], p=2e-5)
  two-line "notice active vs passive" rule ..... 0.83   (real beats it only +0.07, NOT statistically real)
  information-free twin (always say "water") ... 0.09   (loses hugely — the mandated control)
The 90% is REAL, not a mirage: it clears the strongest genuinely-trivial floor with statistical
separation. But it is far less impressive than it sounds — the filtering does most of the work
(a dumb method already gets 70% on the survivors vs 39% on raw prose), and a two-line rule closes
almost all of the rest. The number is now on record with a floor beneath it and can't be quoted bare.

BRAIN-FOUNDATIONAL FINDING (the reason to care)
Splitting the sentences by grammar: on ordinary "X does Y" sentences the dumb rule TIES the real
system (0.94 vs 0.96). On "Y is done by X" (passive) sentences the dumb rule collapses to 0.09 and
the real system wins by +0.69. The system's entire advantage lives exactly where word order stops
telling you who did what to whom — which is precisely where the human brain stops using its fast
reading shortcut and recruits effortful grammar processing (good-enough parsing; Ferreira 2003).
So although the mechanism's implementation (hand-written filters) is not brain-like, its ERROR
PROFILE tracks the brain's own division of labour. This was invisible until the floor was run.

DISK vs BRIEF
The brief said the survivors weren't saved and this needed a full re-run. Only partly true: the exact
100 adjudicated survivors WERE saved with their sentences, and the extractor reproduces 99/100 of
them, so I scored on the same items with no re-run (~seconds).

WHAT I DID NOT CLAIM
n=100 (the adjudicated sample, not the full 1,414); single annotator on the 198 novel judgements
(the +0.23 margin survives that, the +0.07 does not); and NOT that "grow-by-reading is viable" —
this floor doesn't establish that.

NEXT PROBLEM WORTH ASKING
Recall on NON-CANONICAL sentences. The filters buy precision by discarding the hard sentences —
exactly the ones where reading (and the brain) does real work. The open question: can the machinery
hold precision as it admits more passives / object-relatives / reversible sentences? That's a
precision-vs-recall curve stratified by grammatical canonicity — the place where "reading" earns its
keep over a heuristic.

FILES / REVERIFY
experiments/exp_grow_by_reading_trivial_floor_v1.py, ..._score_v1.py,
verification/test_grow_by_reading_trivial_floor.py, notes/problems/.../SOLVED.md
reverify:  .venv/Scripts/python.exe verification/test_grow_by_reading_trivial_floor.py
