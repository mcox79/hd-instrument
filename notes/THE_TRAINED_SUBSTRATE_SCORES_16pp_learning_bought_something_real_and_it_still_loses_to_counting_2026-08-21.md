# THE TRAINED SUBSTRATE SCORES **+16.3 pp** ON THE ANOMALY TASK: **LEARNING BOUGHT SOMETHING REAL, AND IT STILL DOES NOT CLEAR COUNTING**

**The three-way comparison that decides what F5 would be building on. It has never existed before.**

| arm | per-set discrimination | median | verdict |
|---|---|---|---|
| **untrained codebook** (nothing read) | +0.0, +3.4, *(refused)* | **~0** | CIs span zero -- **donates nothing** |
| **THE TRAINED SUBSTRATE** | **+12.5, +11.8, +20.8, +20.2** | **+16.3 pp** | **`REPLICATED`, all four CIs EXCLUDE zero** |
| first-order counting | +23.3, +23.5, +22.5, +25.2 | +23.5 pp | `REPLICATED` |
| **second-order counting** | +28.3, +29.4, +35.0, +29.4 | **+29.4 pp** | `REPLICATED` -- **the bar, upper bound +44.2** |

*Arm: the substrate's OWN comparison, not a new mechanism. `ConceptSpace.observe` fed the RAW
`context_vector_masked` per occurrence, matching the accumulation line in the source; 7,535
sentences read after excluding every item sentence; 8,969 anchors, mean profile norm 128.3.
Detector = negative cosine between a word's accumulated profile and its sentence context -- the
same cosine `canonicalize` decides on.*

---

## 1. ✅ **LEARNING BOUGHT SOMETHING REAL -- AND THIS IS THE FIRST REPLICATED POSITIVE FROM OUR SIDE ON THIS TASK**

**0 pp untrained -> +16.3 pp trained**, `REPLICATED` across four independently-built sets, **every
one of the four CIs excluding zero.** The same representation, the same comparison, the same items --
the only difference is 7,535 sentences of reading. *That is a clean attribution: the effect is
bought by accumulation, not donated by the codebook, because the codebook was measured separately
at zero.*

## 2. ❌ **AND IT DOES NOT CLEAR THE BAR**

The gate is counting's **upper** bound, `+44.2 pp`. The substrate's best per-set CI reaches
**+30.8**. **DOES NOT CLEAR**, on all four sets.

**This reproduces the project's standing position -- *at or below co-occurrence counting* -- on a
task that did not exist when that position was formed.** An independent task returning the known
answer is a consistency check that passed, and it is worth more than a new number.

## 3. ✅ **THE QUESTION I FLAGGED AS UNTESTED IS NOW TESTED -- AND THE ANSWER GOES AGAINST US**

I originally wrote that I had *not* shown the substrate to be significantly WORSE than counting,
because the marginal CIs overlap (+30.8 vs +20.0) and **overlapping marginal intervals are not a
test of a difference.** That was correct at the time and it was the right thing to refuse to claim.

**SO I RAN THE PAIRED TEST** -- same items, same slots, same corpus, each item contributing its own
`(anom - orig)_SUBSTRATE - (anom - orig)_COUNTING`:

> **SUBSTRATE - COUNTING over 478 items = -0.142 per item, 95% CI [-0.203, -0.082]. SEPARATED.**

**The substrate is MEASURABLY BEHIND second-order counting on this task**, not merely failing to be
ahead. *The standing position -- "at or below co-occurrence counting" -- can now be stated in its
stronger form for this task, tested rather than inferred.*

**Note which direction the extra work pointed.** The paired test was the honest follow-up to a
caution I had written into my own note, and it converted an unresolved overlap into a result that is
worse for us. That is the correct use of the caution.

## 4. 🎯 WHAT THIS MEANS FOR F5

**F5 is NOT building on nothing.** There is a real, replicated ~16-point signal in the accumulated
profiles for a coherence monitor to read. **But the gap to counting is ~13 points on the medians, the gate
is 13.4 above the substrate's best CI, and the paired test confirms the gap is real**, so F5 must
contribute substantially rather than merely surface what is already there.

**And the honest risk, stated up front:** the most likely F5 outcome given every other measurement
this project has made is *another arm that lands between the substrate and counting*. That would be
a real result and it would not clear the bar.

## TLDR

We now have three numbers on the same test, which we have never had before.

Our system **having read nothing** scores **zero** — as it should.
Our system **after reading 7,500 sentences** scores about **16 points**, and that holds up across
four separately-built test sets with the error bars comfortably clear of zero. **So the reading
genuinely bought something.** That is the first solidly positive result from our own side on this
task.

Plain word-counting scores about **29**, and the bar we set — deliberately using the top of
counting's error range rather than its middle — is **44**. **So our system does not pass.**

At first I was careful *not* to say we were *worse* than counting, only that we failed the bar — the
two error ranges overlapped, and overlapping ranges are not a test of a difference. **So I ran the
test that is.** Comparing the two methods sentence by sentence on the identical sentences, **counting
wins by a clear margin that does not include zero.** We are genuinely behind, not merely not ahead.

Worth noting which way that went. The extra work came from a caution I had written into my own
write-up, and doing it produced a **worse** answer for us than leaving the caution in place would
have. That is what a caution is for.

What it means practically: the new component would not be starting from nothing — there is a real
signal in what the system has learned for it to read. But it would need to add a lot, not just
expose what is already there.

## QUESTIONS

None.

## NEXT STEPS

1. `tools/score_the_trained_substrate_on_anomaly.py` is the instrument; it carries leak control and
   prints the anchor count and mean profile norm so an empty accumulator cannot pass unnoticed.
2. The paired substrate-vs-counting comparison is DONE: `-0.142 per item, 95% CI [-0.203, -0.082]`
   over 478 items, SEPARATED. `compare_detectors_paired()` in the harness is the reusable form.
3. F5 remains blocked only on cell-authoring.
