# **WE ALREADY HAD A WORKING QUALITY PROXY AND NOBODY HAD CHECKED IT AGAINST THE HUMAN SCORES. `v4`'s PROXIMITY CRITERION SEPARATES MEANING FROM NOISE AT `p = 0.0038` AND SURVIVES CORRECTION FOR EVERY TEST I HAVE RUN.**

**The loose criterion is refuted, my own invented replacement did not survive its own search -- and the
archive's THIRD REPAIR ATTEMPT, built weeks ago for exactly this defect, works.**

---

## 1. THE COMPARISON, ON THE SAME 100 HUMAN-SCORED ROWS

| criterion | MEANINGFUL | RELATED | NOISE | **GOOD vs NOISE** | Fisher p |
|---|---|---|---|---|---|
| **v3** *same-sentence anywhere* | 1.000 | 0.842 | 0.846 | `0.864` vs `0.846`, **+0.0175** | 🔻 **`1.0000`** |
| ✅ **v4** *both tokens within 6* | 0.667 | 0.579 | **0.244** | **`0.591` vs `0.244`, +0.3473** | ✅ **`0.0038`** |

**Monotone on v4: `0.667 > 0.579 > 0.244`.** *It rejects `76%` of what a human called noise while keeping
`59%` of what they called good.*

## 2. ✅ **AND IT SURVIVES THE MULTIPLICITY THAT KILLED MY OWN RESULT**

*Seven tests have now been run on these 100 rows across the session. Smallest `p = 0.0038`;
**Bonferroni x7 = `0.0266`, still under `0.05`.***

> ### **THE DIFFERENCE FROM MY GRADED COUNT IS NOT THE p-VALUE, IT IS THE PROVENANCE. `v4` IS NOT A MEASURE I INVENTED WHILE SEARCHING: it is a purpose-built repair whose `PROXIMITY_WINDOW = 6` was derived from corpus structure (`median_sentence_len 18 / 3`) BEFORE any result existed, and I tested it ONCE.**

## 3. 🔑 **WHAT I GOT WRONG, AND IT IS THE THIRD TIME TODAY**

**I found that same-sentence co-occurrence is at ceiling and cannot discriminate. Then I built a graded
count to fix it. `v4`'s docstring says, in the archive, weeks earlier:**

> *"same-sentence-anywhere is no longer sufficient"* -- *and it is described as the **THIRD** repair
> attempt of this instrument, requiring "a GENUINELY DIFFERENT mechanism (proximity window /
> dependency check), not a parameter sweep".*

**The defect I discovered was already diagnosed, and the fix was already built, landed and
HARD_PASSed.** *What had NOT been done is the thing that took twenty minutes: **checking the repaired
criterion against the human labels.** `v4` was validated against a FREQUENCY FLOOR (gap `0.2667` over
`0.22`), never against a person.*

***This is the "use the instrument, do not imitate it" lesson for the third time in three days*** -- the
census, the graded count, and now this.

## 4. WHAT THIS CHANGES

| claim | status |
|---|---|
| the v1/v3 co-occurrence criterion tracks meaning | 🔻 **REFUTED** (`p = 1.0000`, at ceiling) |
| *"foundation validated"* where it rests on v1/v3 | 🔻 **still must be re-worded** |
| **we have a cheap automatic proxy that tracks human meaning** | ✅ **YES -- `v4` proximity, `p = 0.0038`** |
| my graded-count declaration | ⚠️ **SUPERSEDED before use** -- `v4` is better-provenanced and already tested |
| `v4`'s own HARD_PASS (`gap 0.2667` vs a frequency floor) | ✅ **stands, and now has a SECOND, independent validation** |

## 5. LIMITS

1. **100 rows, one scorer, once, no kappa.** *And only 3 MEANINGFUL, so the three-level ordering leans
   on a group of three; the `22`-vs-`78` collapse is what carries the result.*
2. **`0.591` recall on human-GOOD.** *It is a usable filter, not an oracle -- it discards 4 in 10 good
   facts.*
3. **My first run of `v4` returned `0/100`** because I passed raw strings where it wants TOKENIZED
   sentences. *I checked before reporting it, because its own landed run reports precision `0.4867` and
   a criterion that rejects everything contradicts that. **The triple-check rule caught a wrong headline
   by one step.***
4. **This validates the CRITERION, not the foundation.** *A better ruler does not make the facts good --
   the blind score is still `3 / 19 / 78`.*

## TLDR

Yesterday I showed our automatic quality check is useless — it waves through 86% of everything, good and
junk alike. I then built a better version myself and had to disown it, because I'd tried five variants
and reported the one that passed.

**Today I found we already had the fix, built weeks ago, and nobody had ever checked it.**

The repaired check adds one requirement: the two words must appear **within six words of each other**,
not merely somewhere in the same sentence. On the same 100 human-scored facts, **it throws out 76% of
what a person called junk while keeping 59% of what they called good** — a 35-point gap where the old
check had a 2-point gap. The statistics hold up even after allowing for every test I've run.

**The most useful part is what it says about how we work.** The problem I "discovered" was diagnosed
here weeks ago; the file literally says same-sentence matching "is no longer sufficient" and calls
itself the third attempt at fixing it. **The fix was built, tested against a statistical baseline,
marked as passing — and never once compared against a human's judgement.** That comparison took twenty
minutes and turned an unvalidated repair into our only working quality measure.

**What this does not mean:** the facts are still mostly junk (3 meaningful, 19 related, 78 noise). We
now have a better ruler, not better facts.

## QUESTIONS

None — Q105 still open; this strengthens the case for a bigger sample either way.

## NEXT STEPS

1. ✅ **Use `v4`'s `cooccurs_v4` as the standing automatic quality proxy**, and retire my graded-count
   declaration in favour of it.
2. ⚠️ **Re-word "foundation validated" only where it rests on v1/v3** *-- `v4`'s own claim now has two
   independent validations and should be cited as the good one.*
3. *Method note: **three times in three days the answer was "the instrument already existed".** The
   census, the graded count, and now the quality criterion. **The cheapest question in this repo remains
   "has someone already built this", and I keep asking it late.***
