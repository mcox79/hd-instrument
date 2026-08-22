# **RUN ON THE SAME 100 ITEMS: THE CO-OCCURRENCE CRITERION PASSES `86%` OF THE FACTS A HUMAN CALLED NOISE, AND `86%` OF THE ONES THEY CALLED GOOD. FISHER EXACT `p = 1.0000`. IT DOES NOT MEASURE MEANING.**

**Yesterday I flagged this as a discrepancy that had never been tested because the two criteria ran on
different samples. It is the cheapest experiment on the board. I ran it. The suspicion was right.**

---

## 1. THE TEST

**The 100 blind human-scored rows survived on disk** (`_joined_verdicts.json` -- `subj`, `obj`, `arm`,
and the human verdict `v`). **The harness's own `cooccurs()` was IMPORTED, not reimplemented**, and run
against its own `CORPUS_SOURCES_FULL` reference corpus (30,889 sentences).

*One variable: the same facts, scored both ways.*

## 2. 🔻 THE RESULT

| human label | n | **co-occurrence pass rate** | decoy rate |
|---|---|---|---|
| MEANINGFUL | 3 | `1.000` | 0.667 |
| RELATED | 19 | `0.842` | 0.737 |
| 🔻 **NOISE** | **78** | 🔻 **`0.859`** | 0.705 |
| **ALL** | 100 | `0.860` CI `[0.779, 0.915]` | 0.710 |

**Collapsing to the question that matters:**

| | pass rate |
|---|---|
| human **GOOD** (MEANINGFUL + RELATED) | `19/22` = **`0.864`** |
| human **NOISE** | `67/78` = **`0.859`** |
| **difference** | **`+0.0047`, Fisher exact two-sided `p = 1.0000`** |

> # **THE CRITERION CANNOT TELL A MEANINGFUL FACT FROM A NOISE FACT. NOT WEAKLY -- THE DIFFERENCE IS HALF A PERCENTAGE POINT ON 100 ITEMS AND THE TEST RETURNS EXACTLY 1.**

## 3. 🔑 WHAT THIS DOES AND DOES NOT OVERTURN

**The real-vs-decoy gap is REAL and reproduces here** -- `0.860` vs `0.710` on this population.
**Stored facts genuinely co-occur more than random decoys.** *That is a true statement and the harness
measured it correctly.*

> ### **BUT THE GAP IS THE SAME FOR NOISE AS FOR MEANING. So "beats a decoy" certifies that the pair is TOPICALLY ADJACENT, which the substrate learned from reading -- and topical adjacency is exactly what a reader calls NOISE when it is offered as a meaning.**

| claim | status |
|---|---|
| stored facts beat random decoys on co-occurrence | ✅ **stands** -- measured again here |
| **that this validates the foundation's QUALITY** | 🔻 **REFUTED on the same items** |
| the blind human `3 / 19 / 78` | ✅ **stands** |
| *"foundation validated"* as a quality claim | 🔻 **must be re-worded wherever it appears** |

## 4. ⚠️ LIMITS -- **AND ONE IS SERIOUS**

1. 🔻 **`n = 3` MEANINGFUL.** *The three-way table is decoration; only the GOOD-vs-NOISE collapse
   (22 vs 78) carries weight, and even that is 100 items.*
2. 🔻 **A CEILING EFFECT COULD EXPLAIN THIS ENTIRELY.** *`cooccurs()` is a PREFIX match anywhere in a
   30,889-sentence corpus and passes `86%` of everything. **A criterion that says yes to almost
   everything cannot discriminate anything**, and that is a property of the threshold, not proof that
   co-occurrence carries no signal.* **A graded count, or a tighter window, might separate where a
   boolean does not** -- untested, and the honest next move.
3. **My decoy draw is my own** (seeded, from the same object pool); I did not reproduce the harness's
   exact `0.2533`, and I am not claiming to -- different population, different draw.
4. **The human labels are one scorer, once.** *No second annotator, no kappa.*

## TLDR

Our automatic check on whether a learned fact is any good asks: do these two words actually turn up
together in real text, more often than a randomly chosen wrong word would? On that test the system's
facts pass comfortably, which is where "foundation validated" comes from.

**Yesterday I noticed a human had scored 100 of those same facts and called 78 of them noise, and that
nobody had ever run both checks on the same facts. Today I did.**

**The automatic check passes 86% of the facts the human called noise — and 86% of the ones the human
called good.** The difference is half a percentage point. The statistical test comes back at exactly
1.0, meaning no detectable difference whatsoever.

**So the check is real but it is measuring the wrong thing.** It confirms the two words hang around
together in text, which is true of "whisky" and "wedding" — and that is precisely what a person calls
noise when you offer it as the *meaning* of a word.

**One honest possibility I can't rule out:** the check says yes to 86% of everything, so it may simply
be set too loose to tell anything apart, rather than being blind to meaning in principle. A stricter
version might do better. That's worth an hour, and it's the next thing.

**What this does not change:** the facts really do beat random decoys, and the reading machinery really
does work. **What it changes is that we can no longer call that "validated quality"** — we measured it,
and it isn't.

## QUESTIONS

None — Q105 still open, independent of this.

## NEXT STEPS

1. 🎯 **Retry with a GRADED co-occurrence count and a tighter window** *before concluding co-occurrence
   is worthless. An 86% pass rate is a threshold problem first and a validity problem second.*
2. ⚠️ **Re-word "foundation validated" wherever it appears** *-- it means "beats a decoy on
   co-occurrence", which is now measured NOT to track meaning.*
3. *Method note: **the experiment took twenty minutes and needed no new data** -- both halves had been
   sitting on disk for ten days. **What was missing was running them on the same rows.***
