# CORRECTION -- **THE INCUMBENT'S SEMANTIC SIGNAL IS *NOT* ESTABLISHED AS NON-ZERO. ITS CI CROSSES ZERO. AND TWO ASSETS BEAT IT, CI-SEPARATED.**

**One turn ago I wrote that our concept encoding carries *"genuine semantic information at roughly
11% of the demonstrated ceiling"* and called it *"small, real, not an artifact."* **The CI was
missing from the cell I read, and it is present in the one next door.**

`exp_meaning_asset_vs_production_v1` reports it directly:

| | |
|---|---|
| **`P_LIVE_CONCEPT`, d=256** | **rho 0.10478** |
| **95% CI** | **[-0.00731, +0.21257]**, n=322 |
| **crosses zero?** | **YES** |
| its own scramble | -0.0064 |
| lemma collisions in vocab | **1,364** |

**➡️ THE POINT ESTIMATE IS ABOVE ITS OWN SCRAMBLE, BUT THE INTERVAL INCLUDES ZERO. "SMALL, REAL, NOT
AN ARTIFACT" IS WITHDRAWN. The honest statement is: a point estimate of 0.105 that is NOT established
as non-zero.**

**AND THE CELL SAYS SO ITSELF, IN A FIELD WRITTEN FOR EXACTLY THIS MISREADING:**

> **`reading_rule`: *"beating the incumbent is NOT the same as clearing the zero-meaning floor; **the
> incumbent itself does not clear it.** Both must hold before 'wire it' is an evidenced
> recommendation."***

*The author anticipated the mistake I made and wrote the guard into the artifact. I read the sibling
cell first and missed it by one file.*

## 🎯 **AND THE PART THAT IS GENUINELY GOOD: TWO ASSETS BEAT THE INCUMBENT, CI-SEPARATED**

| arm | rho | difference vs incumbent | CI95 | separated? |
|---|---|---|---|---|
| **`d12\|ASSET_NORMS12`** | **0.2701** | **+0.1653** | **[0.0159, 0.3084]** | ✅ |
| **`d512\|ASSET_RETRAIN_ISOL`** | **0.2581** | **+0.1533** | **[0.0220, 0.2807]** | ✅ |

**Both clear zero on the DIFFERENCE, which the incumbent does not clear on its own value.**
*`ASSET_RETRAIN_ISOL` is the same arm that cleared the frequency floor in
`exp_meaning_asset_fair_test_v1` -- **two independent comparisons, same winner.*** **And
`ASSET_NORMS12` does it at `d=12`** -- twelve dimensions, beating a 256-dimension incumbent.

## WHAT THIS ACTUALLY ESTABLISHES

1. **Our production concept encoding has NO ESTABLISHED semantic signal.** Not "a small one" -- an
   unestablished one.
2. **Two built-but-unwired assets are CI-separated ABOVE it**, one of them at 21x smaller dimension.
3. **Neither of them clears the zero-meaning floor either**, per the cell's own reading rule -- *so
   "wire it" is still not an evidenced recommendation.* **Beating a floor-failing incumbent is a real
   but limited claim.**
4. **1,364 lemma collisions in a 4,096-word vocabulary** is a plausible mechanical contributor to the
   incumbent's weakness and is worth its own look.

## TLDR

One turn ago I told you our system carries a small but genuine amount of real meaning. **I have to
walk that back: the margin of error on that number includes zero.** The measurement is 0.105, and the
plausible range runs from slightly below nothing to about 0.21. **So we cannot say the system's grasp
of meaning is distinguishable from none at all.**

The experiment that says so had **written a warning into itself** for exactly this mistake — a field
stating that beating the current system is not the same as showing the current system works, *and
that the current system does not*. I'd read the neighbouring experiment and missed it by one file.

**The genuinely good news:** two of our built-but-unused alternatives are **measurably better than
what's running**, with margins that don't touch zero. One of them achieves it using **twelve
dimensions against the incumbent's 256** — a twentyfold reduction in size for a better result. And
one is the same alternative that won a separate comparison earlier, so it's now won twice
independently.

**The caution the experiment insists on: neither alternative has been shown to clear the "no meaning
at all" bar either.** Beating something that doesn't work is a real result, but a limited one.

One mechanical detail worth chasing: **1,364 of the 4,096 vocabulary words collide** with another
word after lemmatisation. That's a plausible reason the incumbent looks weak.

## QUESTIONS

None.

## NEXT STEPS

1. **`ASSET_NORMS12` at d=12 is the striking result** -- 21x smaller than the incumbent and
   CI-separated above it. *Read that cell before anything else.*
2. **Stop quoting 0.1048 as a signal.** Quote it as `0.105, CI [-0.007, 0.213], not separated from zero`.
3. The 1,364 lemma collisions deserve a look as a mechanical cause.
