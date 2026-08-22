# **I RE-RAN THE REAL-PROSE WALL ON THE REPAIRED LEMMATIZER. `primary = 0.4722` -- IDENTICAL TO FOUR DIGITS. MY CONFOUND HYPOTHESIS IS REFUTED, AND THE WALL STANDS.**

**Last turn I argued the wall was confounded by a since-fixed dependency and should be re-run. I re-ran
it. It reproduces.**

---

## 1. THE RE-RUN

*`exp_noise_robust_learn_from_exposure_snorkel_v1`, `--run-mode full`, today, on current code -- so on
the `2026-08-13` repaired `lemma_verb` (`non-word stems 8,692 -> 0`, `gold verb-inflection
53.50% -> 99.03%`).* ✅ **It has NO `units.jsonl`, so it genuinely recomputed** *(65.55 s, vs 56.55 s
originally).*

| field | **2026-08-07** *(pre-repair)* | **2026-08-22** *(post-repair)* |
|---|---|---|
| **primary accuracy** | **`0.4722`** | **`0.4722`** ← *identical to four digits* |
| majority floor | `0.6389` | `0.6389` |
| scramble | `0.5000` | `0.5111` |
| **scramble gap** | **`-0.0278`** | **`-0.0389`** *(still negative -- no collapse)* |
| coverage AND / OR | 439 / 1141 | 434 / 1142 |
| soft-trusted | 165 | 164 |
| learnable ls-acc | `0.4615` | `0.3571` |
| **verdict** | **`HARD_FAIL`** | **`HARD_FAIL`** |

> # ✅ **`SCRAMBLE_DOES_NOT_COLLAPSE_no_real_signal` FIRES AGAIN. THE TEACHING SIGNAL STILL DOES NOT CARRY ON REAL PROSE, WITH A LEMMATIZER THAT IS NOW `99%` ACCURATE INSTEAD OF `53.5%`.**

## 2. 🔻 **SO MY HYPOTHESIS WAS WELL-FORMED AND WRONG**

*Last turn I established -- correctly -- that both wall cells predate the lemmatizer repair by six days,
that the dependency is two calls deep, and that the pre-repair stripper's fingerprint (`ad`) sits in the
saved error lists.* **All of that is still true.**

***AND IT DOES NOT MATTER. The broken dependency was real and its effect on this result is nil.***

**I said at the time: "CONFOUNDED, not REFUTED -- the repair might not move the verdicts at all."**
*That caveat is now the finding.* ✅ **This is what a hypothesis stated with its own kill condition looks
like when the kill condition fires.**

## 3. 🎯 WHAT THIS BUYS -- **IT STRENGTHENS THE PLANS OF RECORD**

**The wall both plans cite as THE bottleneck is now measured TWICE, fifteen days apart, on two different
lemmatizers, with the same verdict and an identical primary accuracy.** *It is no longer a single
2026-08-07 measurement resting on a component that turned out to be broken.*

⚠️ **AND THE `52%` NON-WORD ERROR SHARE IS STILL A PRE-REPAIR ARTIFACT** *(today's `lemma_verb` returns
`baby`/`always`/`capacious` cleanly).* **Both can be true: the stems were garbage, AND cleaning them did
not move the outcome.** *That is worth holding onto -- it says the credit errors were not what was
limiting this.*

## 4. ⚠️ LIMITS

1. **This is the PARENT wall cell only.** *The sharpened credit-assignment cell (`b5fdd956c`) HAS a
   `units.jsonl` and would replay -- **it is still unre-run**, and its `0.4676 -> 0.4941` precision
   numbers remain pre-repair.*
2. **The landed `metrics.json` is now OVERWRITTEN with the re-run.** *Backed up to
   `scratch/_wall_backup.json` first; the file is git-tracked and the pre-repair values are in this
   note and in `git` history.*
3. **`learnable_ls_acc` DROPPED `0.4615 -> 0.3571`** *and `n_learnable` rose 10 -> 11. Small-n movement
   on an arm that is far below floor either way; I am not reading it.*
4. **One run, not a seed sweep** *-- though the primary matching to four digits across fifteen days and
   two lemmatizers is itself strong.*

## TLDR

Last turn I found that the obstacle steering this whole project had been measured with a broken tool,
and said it needed re-checking. **I re-checked it. The result is exactly the same** — the headline number
matches to four decimal places, and the same failure fires.

**So the broken tool was real, and it made no difference.** I was careful at the time to say "this might
change nothing" rather than "the wall is imaginary", and that caution turned out to be the answer.

**This is good news, not bad.** The obstacle is now measured twice, fifteen days apart, with two
different versions of the underlying tool, and it holds. It is no longer a single result resting on
something that later turned out to be faulty.

**One useful thing survives from the wrong hypothesis:** the mangled word-fragments in the old records
*were* genuine rubbish and *have* been fixed — cleaning them up just did not rescue the result. Which
tells us those errors were not what was holding this back.

## QUESTIONS

None.

## NEXT STEPS

1. **The sharpened credit-assignment cell is STILL unre-run** *-- it has stored units and would replay.
   Its precision numbers remain pre-repair, so the `73%`-not-verbs analysis is still on old data.*
2. **The wall can now be quoted WITHOUT the confound** *-- and should be, since I put the confound in the
   plan last turn.*
3. *Method note: **the hypothesis was worth stating and worth killing, and killing it took one 65-second
   run.** The reason it was cheap is that this cell never saved checkpoints -- the same property that
   makes 399 other cells unre-runnable.*
