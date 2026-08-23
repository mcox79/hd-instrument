# MY PREDICTION WAS CONFIRMED AND THE CONCLUSION IT POINTED AT WAS WRONG

**2026-08-23, strategy session.** Third and last step of the polarity thread. I predicted that the
pseudo-count rounding **discards exactly the items where the similarity weighting earns its keep**.
**The prediction is true.** The conclusion I was walking toward -- *"so the discard is harmful"* --
**is refuted by the same data, one slice deeper.**

---

## 1. THE PREDICTION, AND IT HELD

Stated before measuring: the weighting's benefit sits at the COMMIT BOUNDARY, so those items have
low margins, therefore low confidence, therefore `round(3 * conf) == 0`.

| | n | median confidence | discarded by the rounding | accuracy |
|---|---|---|---|---|
| **items the weighting ADDS** (weighted vote commits, unweighted does not) | `75` | **`0.0933`** | **`57` = `76%`** | `0.7200` |
| items both votes agree to answer | `234` | `1.0000` | `8` = `3%` | `0.6282` |

✅ **Confirmed. The items the weighting adds are low-confidence, and three quarters of them are
thrown away before the learning loop ever sees them.**

---

## 2. AND THEN THE SLICE THAT KILLS THE CONCLUSION

The obvious next sentence is *"so the rounding is discarding the organ's best work."* **I checked
instead of writing it.**

| | n | accuracy |
|---|---|---|
| weighting-added, **DISCARDED** | `57` | `0.6491` |
| 🔑 **weighting-added, SURVIVES** | **`18`** | **`0.9444`** (17/18) |
| overlap, DISCARDED | `8` | `0.5000` |
| overlap, SURVIVES | `226` | `0.6327` |

🚨 **WITHIN THE GROUP THE WEIGHTING ADDS, THE ROUNDING KEEPS THE BEST ITEMS AND DROPS THE REST.**
`0.9444` against `0.6491`. **The `0.7200` headline for those 75 is carried almost entirely by the 18
the rounding retains.** *Far from throwing away the best work, the rounding is picking it out.*

**SO THE DISCARD IS DOING USEFUL SELECTION HERE -- the opposite of where I was heading**, and the
opposite of the tone of my earlier note, which said there is "no measured basis for preferring the
ones it keeps."

---

## 3. THE METHODOLOGICAL FINDING, WHICH IS THE DURABLE ONE

**THE AGGREGATE CONFIDENCE-ACCURACY NULL WAS HIDING AN INTERACTION.**

Measured earlier and correctly: across everything the organ commits to, kept `0.6557` vs discarded
`0.6308`, difference `+0.0250`, CI95 `[-0.1052, +0.1603]` -- **spans zero, no signal.** That is still
true.

But the cell structure shows confidence is **uninformative among items both vote types reach**
(`0.6327` vs `0.5000`, n=8) and **strongly informative among items only the weighted vote reaches**
(`0.9444` vs `0.6491`). **Averaging those together produces a clean null that describes neither.**

*I reported that null as "confidence does not predict correctness on this population" and that
statement remains literally correct. It was also incomplete in a way I could not see without
splitting on a variable I had not yet measured.*

---

## 4. THE CAVEAT THAT COULD SINK SECTION 2, STATED UP FRONT

⚠️ **THE `18`-ITEM CELL IS A POST-HOC SUBGROUP AND I HAVE NOW SLICED THIS DATA MANY WAYS.**

`17/18` is a striking number and n=18 is a small one. It arrived from a split I chose *after* seeing
that the 75 outperformed, in a thread that has already partitioned this dataset by band, by stage,
by anchor size, by weighting, and by rounding. **Somewhere in that sequence a subgroup was going to
look excellent by chance.**

**WHAT WOULD SETTLE IT:** the same split on a population fixed in advance -- a fresh gold slice, or
the loop's own OOV lemmas -- with the cells named before the numbers are seen.

**WHAT I AM NOT DOING:** proposing a change to the rounding on the strength of `n=18`. *Section 2
refutes my previous direction; it does not establish its opposite.*

---

## 5. WHERE THE THREE FINDINGS NOW STAND

| finding | status |
|---|---|
| confidence does not predict correctness | ✅ stands **in aggregate**, ⚠️ now known to average over an interaction |
| the rounding discards a fifth of decisions | ✅ stands, and **it is not established that this is harmful** -- section 2 argues the reverse |
| similarity carries answerability, not valence | ✅ stands, unaffected |
| *"no measured basis for preferring the ones it keeps"* | 🔻 **TOO STRONG. Withdraw.** There is a basis; it is confined to one subgroup and rests on 18 items |

---

## TLDR

I predicted that the system throws away exactly the answers where its cleverest step does the most
work. **The prediction was right** — three quarters of those answers are discarded before the
learning ever sees them.

The obvious conclusion is that this is a bug worth fixing. **I checked before writing it, and it is
wrong.** Of that group, the ones the system keeps are right 17 times out of 18, and the ones it
throws away are right about 6 times in 10. It is not discarding its best work — it is **selecting**
it.

There is a real lesson underneath. Earlier I measured that the system's confidence tells you nothing
about whether it is right, and that was true on average. Splitting the data one level further shows
confidence is useless on the easy half and very useful on the hard half — **and averaging those
together produces a tidy "no effect" that describes neither half.**

The honest limit: that 17-out-of-18 comes from a group I chose to look at after noticing it was
doing well, in a stretch where I have sliced this dataset many different ways. Something was going
to look excellent eventually. It is worth re-testing on a group picked in advance, and it is not
worth changing anything on yet.

## QUESTIONS

None.

## NEXT STEPS

1. **Re-run this split on a population fixed in advance** before anyone acts on the 18-item cell.
2. **Withdraw "no measured basis for preferring the ones it keeps"** from the earlier note — done
   here; the claim was stronger than the evidence.
3. The polarity thread is at a natural close: the mechanism is understood well enough to say what it
   does, and the remaining questions all need populations this eval cannot supply.
