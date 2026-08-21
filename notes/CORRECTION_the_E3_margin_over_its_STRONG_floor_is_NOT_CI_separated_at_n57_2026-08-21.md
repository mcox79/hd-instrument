# CORRECTION: E3's MARGIN OVER ITS **STRONG** FLOOR IS **NOT CI-SEPARATED AT n=57** -- I QUOTED A POINT ESTIMATE TO THE OWNER AS "BEATS BOTH BASELINES"

**Recommendation UNCHANGED. One load-bearing fact corrected.**

I told the owner, in a board question they may act on, that E3 *"beats both of its simple comparison
baselines, scoring 0.72 where picking-the-most-recent-mention scores 0.56."* **I read those numbers
out of `ORGAN_MAP` prose and did not check whether the margin survives a confidence interval.** It is
the thing I have spent the entire day enforcing on everyone else's numbers, including my own.

---

## 1. DISK-VERIFIED FIRST -- THE FIGURES THEMSELVES ARE ALL CORRECT

All five appear in `exp_wire_coref_accumulate_situation_model_v1/metrics.json`, in ONE block,
`eval_blocks.powered`, on ONE metric, `query_accuracy_identity_demanding`:
oracle **0.9298**, strict_cb **0.7193**, earned **0.6842**, recency_floor **0.5614**,
singleton_floor **0.3860**. *`ORGAN_MAP`'s prose is accurate and same-run, as it claimed.*

**One distinction its prose blurs:** 0.7193 is the **`strict_cb`** arm (`best_real_arm`), one of three
modes. The **`earned`** figure is **0.6842**. Both matter below.

## 2. 🚨 **n = 57, AND THERE IS NO CONFIDENCE INTERVAL ANYWHERE IN THE FILE**

Unpaired two-proportion test -- **conservative**, since the file does not carry the discordant counts
a paired test needs:

| comparison | diff | 95% CI | p | |
|---|---|---|---|---|
| strict_cb vs **recency floor** | +0.1579 | **[-0.016, +0.332]** | 0.075 | **NOT SEPARATED** |
| earned vs **recency floor** | +0.1228 | **[-0.054, +0.299]** | 0.173 | **NOT SEPARATED** |
| strict_cb vs singleton floor | +0.3333 | [+0.161, +0.505] | <0.001 | **SEPARATED** |
| earned vs singleton floor | +0.2982 | [+0.124, +0.473] | 0.001 | **SEPARATED** |

**The whole margin over the strong floor is NINE ITEMS out of 57** -- 41 correct against 32.

## 3. THE CORRECTED STATEMENT

> **E3 is clearly ahead of the WEAK floor (subject-position majority) and, over the STRONG floor
> (most-recent-mention), ahead only as a POINT ESTIMATE -- not established at n=57 by any test the
> data on disk supports.**

*My "the one place we BEAT our floors" was too strong. The honest version is "the one place we may
be ahead of a strong floor, and are clearly ahead of a weak one" -- which is still better than
anything else measured today, and is a weaker claim than I made.*

**A paired test could separate it** -- pairing is tighter and these are the same 57 queries. **The
file does not carry what a paired test needs, so it is UNTESTED, not negative.**

## 4. ✅ **WHY THE RECOMMENDATION DOES NOT CHANGE**

**Because this is an argument FOR step 4, not against it.** `ORGAN_MAP`'s can-fail test for that step
already reads **"at n in the hundreds -- not n=10"**, and the work is explicitly *widen the margin*.
**A margin that is not yet established at n=57 is precisely the thing that step exists to settle.**

And the alternative is unchanged and weaker: F5 does not exist, its bar is **+44.2 pp**, and the
substrate is **measurably behind counting** on the paired test.

**So: same recommendation, corrected justification.** *This is a correction, not a third reversal --
the recommended action is identical to the one filed one turn ago.*

## TLDR

In the question I put to you last turn I said our pronoun resolver **beats both** of its simple
comparison baselines. I took those numbers from a summary document without checking how solid they
were, which is exactly the check I have been applying to everything else all day.

The numbers themselves are right — I verified all five against the raw results file. **But the
comparison rests on 57 examples, and the whole lead over the tougher baseline is nine of them.** Run
the standard test and that lead **could plausibly be zero.** Against the easier baseline the lead is
solid.

So the honest version is: *clearly better than the weak comparison, possibly better than the strong
one, not yet proven.* That is still the best-looking thing measured today, and it is a smaller claim
than I made to you.

**My recommendation does not change, and this is not another reversal.** If anything it argues the
same way: the document's own requirement for that step is "test this on hundreds of examples, not
ten", and an unproven nine-example lead is precisely what that step exists to settle.

## QUESTIONS

Re-filed once more so the board does not carry a claim I know to be too strong. **The recommended
action is unchanged.**

## NEXT STEPS

1. Any future use of these figures quotes **n=57** and **"not CI-separated over the recency floor"**.
2. A paired re-analysis would need the per-query outcomes, which this file does not carry -- worth
   emitting if step 4 runs.
