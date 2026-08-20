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

## 3. ⚠️ **WHAT I AM *NOT* CLAIMING, AND THE DISTINCTION MATTERS**

**I have NOT shown the substrate is significantly WORSE than counting.** The CIs overlap -- the
substrate reaches +30.8, second-order counting starts at +20.0. **What is established is that it
FAILS THE GATE**, which is a decision rule, not a significance test.

*Testing "is our arm significantly below counting" would need a PAIRED comparison of the two arms on
the same items, which is not what any of these runs did. It is a different question and it is
untested. Reporting "we lose to counting" as though it were measured here would be exactly the
scorer-crossing this project's rules forbid.*

## 4. 🎯 WHAT THIS MEANS FOR F5

**F5 is NOT building on nothing.** There is a real, replicated ~16-point signal in the accumulated
profiles for a coherence monitor to read. **But the gap to counting is ~13 points on the medians and
the gate is 13.4 above the substrate's best CI**, so F5 must contribute substantially rather than
merely surface what is already there.

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

One thing I am careful *not* to say: I have not shown we are *significantly worse* than counting.
The error ranges overlap. What is established is that we fail the test we set in advance — which is
a decision, not a proof of inferiority. Claiming more would be the exact sloppiness I have spent the
day removing.

What it means practically: the new component would not be starting from nothing — there is a real
signal in what the system has learned for it to read. But it would need to add a lot, not just
expose what is already there.

## QUESTIONS

None.

## NEXT STEPS

1. `tools/score_the_trained_substrate_on_anomaly.py` is the instrument; it carries leak control and
   prints the anchor count and mean profile norm so an empty accumulator cannot pass unnoticed.
2. The paired substrate-vs-counting comparison is UNTESTED and is the obvious follow-up if the
   question "are we actually behind counting, or just not ahead" ever becomes load-bearing.
3. F5 remains blocked only on cell-authoring.
