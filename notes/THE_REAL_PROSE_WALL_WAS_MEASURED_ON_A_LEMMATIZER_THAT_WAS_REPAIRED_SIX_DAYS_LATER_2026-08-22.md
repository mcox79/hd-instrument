# **BOTH `HARD_FAIL`s THAT ESTABLISH THE "REAL PROSE WALL" RAN ON 2026-08-07. THE LEMMATIZER THEY DEPEND ON WAS REPAIRED ON 2026-08-13, FROM `53.50%` TO `99.03%` VERB-INFLECTION ACCURACY. THE WALL IS CONFOUNDED AND SHOULD BE RE-RUN.**

**This is the wall both plans of record cite as the bottleneck. It has never been measured on a working
lemmatizer.**

---

## 1. THE DATES, FROM `git log`, NOT FROM MEMORY

| commit | date | what |
|---|---|---|
| `fc21752f3` | **2026-08-07** | *the PARENT WALL cell* -- `HARD_FAIL`: real `0.4722` vs scrambled `0.5000`, scramble does NOT collapse |
| `b5fdd956c` | **2026-08-07** | *the SHARPENED credit-assignment fix* -- `HARD_FAIL`: `lift 0.0167`, precision `0.4676 -> 0.4941` |
| **`7d6036bca`** | **2026-08-13** | ***"lemma_verb repair: non-word stems `8,692 -> 0`; gold verb-inflection `53.50% -> 99.03%`"*** |

> # 🔻 **BOTH CELLS RAN SIX DAYS BEFORE THE REPAIR, ON A VERB LEMMATIZER WHOSE INFLECTION ACCURACY WAS `53.50%` -- BARELY BETTER THAN A COIN FLIP -- AND WHICH EMITTED `8,692` NON-WORD STEMS.**

## 2. ✅ THE DEPENDENCY IS DIRECT AND LOAD-BEARING, NOT INCIDENTAL

*`_is_verblike` IS `lemma_verb(tok) != tok or tok.endswith(("ed","ing"))`* -- **the primary test is
literally a call to the broken function.** *`_credit_targets` then calls `lemma_verb` again to key the
credited lemma.* **Every credit decision in both cells passed through it twice.**

✅ **AND THE FINGERPRINT IS IN THE DATA:** *`attribution_precision_old.light_lemmas` contains **`ad`** --
which the repair's own docstring names as an example of the old bug (`added` -> `ad`), alongside
`status -> statu`, `analysis -> analysi`, `arteries -> arteri`.* ***That is the pre-repair stripper's
signature sitting in the metrics I have been analysing all thread.***

## 3. 🔑 WHAT THIS DOES AND DOES NOT LICENSE

| | |
|---|---|
| the two `HARD_FAIL`s are **CONFOUNDED** by a since-fixed dependency | ✅ **established** |
| the `52%` non-word share of the errors is **a pre-repair artifact** | ✅ **established** -- *today's `lemma_verb` returns `baby`/`always`/`capacious` cleanly* |
| **the wall is FALSE** | 🔻 **NOT CLAIMED.** *The repair might not move the verdicts at all -- "scramble does not collapse" could survive a perfect lemmatizer.* |
| **the wall is SETTLED** | 🔻 **NO -- and that is the point.** *It is currently treated as settled by both plans of record.* |

⚠️ **`53.50% -> 99.03%` IS THE LEMMATIZER'S OWN GOLD METRIC, not the cells'.** *I have not measured how
much of the cells' attribution error it accounts for -- and the types/tokens caveat from earlier still
prevents me projecting one.*

## 4. 🔻 **WHY THIS MATTERS BEYOND THESE TWO CELLS**

***`PLAN_B`'s STATUS section cites exactly these numbers as THE WALL*** -- *"on REAL prose the teaching
signal DOESN'T CARRY (scramble does NOT collapse, gap `-0.03`; primary `0.472` < floor `0.639`)"* --
**and derives its whole revised plan from them, including the credit-assignment lever I spent this
thread scoping.**

**So the bottleneck that has been steering the plan for two weeks rests on two runs whose shared
foundation was repaired six days afterwards, and nobody re-ran them.** *That is not anyone's
carelessness -- the repair was a separate thread and the dependency is two calls deep.*

## 5. ⚠️ LIMITS

1. **`ts_iso` is `None` in both metrics files** -- *dates come from `git log` on the cell and metrics
   paths, which is the stronger evidence anyway.*
2. **I have NOT re-run either cell.** *The claim is CONFOUNDED, not REFUTED.*
3. **I have not verified the repair is on the code path those cells import** *beyond both importing
   `hdlab.thematic_role_labeler.lemma_verb`, which is the repaired symbol.*
4. **Re-running is blocked by the resume behaviour** *recorded earlier -- both cells would replay stored
   units unless their checkpoints are bypassed.*

## TLDR

The obstacle that has been steering this project's plan for two weeks — "the teaching signal does not
survive on real prose" — **was measured twice on the same day, and the tool both measurements depend on
was repaired six days later.**

That tool turns words into their dictionary form. Before the repair it got verb endings right **just
over half the time** and produced nearly nine thousand non-words. **The test for "is this word a verb?"
is a direct call to it, and every credit decision went through it twice.**

**The fingerprint is still visible in the saved data:** the error list contains "ad", which is precisely
the example the repair notes give for the old bug — "added" mangled into "ad".

**What I am not saying is that the wall is imaginary.** A perfect lemmatizer might leave the result
exactly where it was. **What I am saying is that it has never been measured with working parts, and it
is currently treated as settled.**

**This is not carelessness by whoever ran it.** The repair happened in a different thread, and the
dependency is buried two function calls deep.

## QUESTIONS

None.

## NEXT STEPS

1. ⭐ **RE-RUN BOTH CELLS POST-REPAIR.** *This is now the highest-value item in the thread: it is a
   re-measurement, not a build, and it tests the premise the whole plan rests on.*
2. ⚠️ **IT NEEDS THE FRESH-UNITS CAPABILITY** *already filed -- both cells will otherwise replay their
   stored units and report the old verdict in zero seconds.*
3. **Until then, quote the wall WITH its confound.**
4. *Method note: **the thing that found this was chasing a discrepancy I could have waved away** -- old
   records said `babi`, today's code says `baby`, and the difference was six days and a repaired
   dependency.*
