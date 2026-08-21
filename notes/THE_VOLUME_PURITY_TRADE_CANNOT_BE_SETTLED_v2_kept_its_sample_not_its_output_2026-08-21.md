# **THE VOLUME/PURITY TRADE CANNOT BE SETTLED FROM DISK -- v2 PERSISTED ITS HAND-CHECK *SAMPLE*, NOT ITS 1,414 SURVIVORS. AND v1 PERSISTED EVERYTHING.**

**I registered the 90%-precision extractor as `WIRE_CANDIDATE` rather than `WIRE` for exactly one
reason: it produces FEWER correct facts at higher purity (~1,273 vs ~1,582), and whether downstream
prefers volume or cleanliness is unmeasured. I tried to settle it from existing artifacts. It cannot
be settled, and the reason is the defect I spent tonight cataloguing.**

---

## 1. WHAT EACH VERSION KEPT

| | file | rows | its metrics claim |
|---|---|---|---|
| **v1** | `_extractions_all.json` (1.2 MB) | **4,015** ✅ | `n_raw_v1 = 4015` -- **exact match** |
| **v2 strict** | `_survivors_for_handcheck.json` (37 KB) | **0 parseable rows** 🔴 | `n_strict_v2 = 1414` |

***v1 saved its ENTIRE output. v2 saved only what it needed for the hand-check.***

## 2. WHY THAT KILLS THE QUESTION

**Both hand-check files carry 99 and 100 adjudicated rows -- but they OVERLAP ON ONLY 5 TRIPLES.**
*They are two independent samples of two different populations, not a matched comparison, so
"what did the strict filter throw away that v1 got RIGHT?" cannot be answered from them.*

**And the full survivor set that WOULD answer it was never written.** *So the two computable
questions both die:*
- *is v2 a pure SUBSET of v1, or does it find things v1 missed?* -> **unanswerable**
- *of v1's correct facts, how many survive the filter?* -> **unanswerable**

**➡️ SETTLING THE TRADE NOW REQUIRES RE-RUNNING THE EXTRACTOR.** *Which is exactly the cost I
documented this morning: **an experiment that saves only its scores can only ever answer the question
it was originally asked.***

## 3. 🎯 **THE INSTRUCTIVE PART: THE SAME PROJECT, DAYS APART, GOT IT RIGHT AND THEN WRONG**

**v1 wrote all 4,015 extractions to disk -- 1.2 MB, and it exactly matches its own reported count.
v2, the SUCCESSOR, wrote 37 KB.** *Nobody removed a habit deliberately; the sample was what the
hand-check needed, so the sample is what got saved.*

**AND IT COST THE BETTER VERSION.** *v1 -- the one that `HARD_FAIL`ed -- is fully re-analysable
forever. v2 -- the `HARD_PASS`, the one worth promoting -- is not.* **The stronger result is the less
examinable one.**

## 4. WHAT THIS CHANGES

1. **The `WIRE_CANDIDATE` decision stands and is now stated more precisely:** *promotion is blocked
   not by doubt about the 90% figure, which is solid, but because **the one number that would decide
   between v1 and v2 no longer exists.***
2. **Any re-run must persist the full survivor set.** *One line, a few hundred KB.*
3. **This is a THIRD independent instance tonight of the same defect** -- after the foraging cell's
   lost vocabulary and my own hand-scores' lost per-row labels. *Three for three, in unrelated
   subsystems, by different authors.*

## TLDR

I registered the 90%-accurate extractor as a *candidate* rather than ready-to-use, because it keeps
only a third of what it finds and therefore produces **fewer** correct facts overall — just much
cleaner ones. Whether that's the right trade is the one thing that would settle it.

**I tried to answer it from what's already saved. It can't be answered**, and the reason is the exact
problem I spent tonight documenting elsewhere.

**The older, worse version saved everything it produced** — all 4,015 extracted facts, still on disk,
still fully re-examinable. **The newer, better version saved only the hundred examples it needed for
grading.** Nobody decided to stop saving; the sample was what the grading required, so the sample is
what survived.

**So the stronger result is the one we can no longer examine.** Deciding between the two versions now
means running the extraction again.

That's the **third** time tonight this same thing has bitten, in three unrelated parts of the project
by different authors: the reading experiment that lost its vocabulary, my own grading that lost its
individual verdicts, and now this. **The pattern isn't carelessness — each time, someone saved exactly
what their immediate question needed. The loss only appears when the next question arrives.**

## QUESTIONS

None.

## NEXT STEPS

1. **The `WIRE_CANDIDATE` status is correct and now has a precise blocker** -- not doubt about the
   result, but a missing artifact.
2. **Any re-run persists the full survivor set** -- a few hundred KB against a re-run.
3. **Three instances in one night makes this a build-time habit, not a note:** *save the population
   you scored, not just the sample you scored it on.*
