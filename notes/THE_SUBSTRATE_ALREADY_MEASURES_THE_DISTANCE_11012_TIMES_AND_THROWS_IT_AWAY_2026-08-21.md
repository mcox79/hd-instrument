# **THE SUBSTRATE ALREADY MEASURES THE DISTANCE-TO-FRONTIER -- 11,012 TIMES -- AND COLLAPSES IT TO A YES/NO AGAINST A CONSTANT MARKED "HYPOTHESIZED"**

**Owner asked for *"the ~distance from any new fact to the grounded foundation."* I went looking for
whether one could be BUILT. It is already being COMPUTED, RECORDED, AND DISCARDED.**

---

## 1. IT IS ON DISK, AND IT IS RICHLY GRADED

`best_cos` -- the cosine to the nearest existing anchor -- is written on **every refusal row**:

| | `reading_grounding_v2_qualityfix` |
|---|---|
| rows carrying a recorded distance | **11,012** |
| **distinct values** | **2,190** |
| range | **0.1416 - 0.4500** |
| p05 / median / p95 | 0.2033 / **0.3090** / 0.4240 |

***This is the graded quantity the owner described.*** *It is nothing like `is_gap` (binary) or
`margin` (pinned at exactly 1.0 for all 67 known words). It has been sitting in the foundation file
the whole time.*
*(`reading_grounding_v1` records none -- consistent with tonight's separate finding that v1 persists
no refusal log at all.)*

## 2. AND THE ARCHITECTURE THROWS THE GRADATION AWAY

`reading_grounding_loop.py:144`:

```python
SENSE_MATCH_THRESH = 0.45  # HYPOTHESIZED
```

`:789` -- `if best_anchor is not None and best_cos >= thresh: return best_anchor, best_cos`

**So the distance is computed, compared to a constant, and reduced to a yes/no. The 0.4500 ceiling
in the refusal data is that threshold, confirmed in code rather than inferred.**

**➡️ THE SYSTEM HAS BEEN MEASURING EXACTLY WHAT THE OWNER ASKED FOR, ~11,000 TIMES, AND KEEPING ONLY
THE BOOLEAN.** *And the constant that erases it is labelled **HYPOTHESIZED** in its own source --
never swept, never validated.*

## 3. 🚨 **WHAT SITS JUST BELOW THE LINE -- AND WHY THIS IS *NOT* A "WE ARE LOSING 90%" CLAIM**

| if the threshold were | refusals that would instead have MATCHED an anchor |
|---|---|
| 0.44 | 178 (1.6%) |
| 0.42 | 670 (6.1%) |
| **0.40** | **1,267 (11.5%)** |
| 0.35 | 3,389 (30.8%) |
| 0.30 | 6,000 (54.5%) |

**⚠️ STOP HERE. MATCHING MORE IS NOT THE SAME AS LEARNING MORE, AND MIGHT BE MUCH WORSE.**
**The threshold exists to prevent FALSE merges** -- binding a genuinely new concept onto a wrong
existing anchor. Lowering it raises recall **and error together**, and a wrong merge is worse than a
refusal because it silently corrupts a concept that was previously correct. *`MEMORY.md` records
exactly this failure: `arteries -> arteri` minting a second concept and then "grounding" one as the
other -- **a tautology wearing a disguise**.*

**SO THE FINDING IS NOT "LOWER THE THRESHOLD."** It is:

> **EVERY GROUNDING DECISION IN THIS SYSTEM TURNS ON A GUESSED CONSTANT THAT SITS IN THE MIDDLE OF A
> DENSE, CONTINUOUS DISTRIBUTION -- 178 attempts fall within 0.01 of it and 1,267 within 0.05 --
> AND IT HAS NEVER BEEN SWEPT.**

*That sensitivity is a fact about the architecture and is true regardless of which direction the
right answer lies in.*

## 4. AND MY OWN INVENTED MEASURE FAILED ITS VALIDITY TEST -- REPORTED BEFORE THE GOOD NEWS ABOVE IS ACTED ON

I proposed `grounded_neighbour_fraction` (what share of a word's neighbours are already anchored) and
showed it was graded, face-valid and uncorrelated with counting. **The one test that mattered came
back null:**

| words with >=30 neighbours | median |
|---|---|
| **successfully anchored** | 0.394 |
| **refused and never anchored** | 0.388 |
| **gap** | **+0.007** |

**On a scale spanning 0.13-0.80, that is nothing. It does NOT predict which words the system managed
to ground.** *Caveats, stated fairly: the anchor set is measured now rather than at attempt time, and
the fairer test -- scoring the OBJECT that blocked each attempt -- **could not be run at all**,
because `candidate_object` is `None` in all 11,012 rows. The field exists in the schema and was never
populated.*

**➡️ SO THE MEASURE I INVENTED IS UNVALIDATED, AND THE ONE THE SUBSTRATE ALREADY RECORDS IS THE
BETTER LEAD.** *That is the correct order of preference and I had it backwards for an hour.*

## TLDR

You asked whether we'd built something that senses **how far** a new fact is from what the system
already understands. I went looking for whether such a thing could be built. **It turns out the
system has been measuring it all along — about eleven thousand times — and throwing the answer
away.**

Every time the system fails to attach a new word, it first works out **how close that word came to
something it already knows**, and writes that number down. Those numbers are richly varied — over two
thousand distinct values across a real range. **That is exactly the graded sense of distance you
described.**

**Then the code compares it to a fixed cutoff of 0.45 and keeps only "yes" or "no".** The cutoff is
labelled, in our own source code, as a guess. It has never been tested.

**And a lot sits right underneath it:** 178 attempts came within a hair of the line, and over 1,200
within a small margin of it.

**I want to be careful here, because this is exactly the kind of number that has misled me four times
tonight.** This does *not* mean we're throwing away learning. That cutoff exists to stop the system
gluing a new idea onto the wrong old one — and a wrong merge is worse than a refusal, because it
quietly corrupts something that was previously right. Moving the line might help or might do real
damage.

**The solid finding is narrower and still important: every decision this system makes about what it
learns turns on a guessed number sitting in the middle of a dense range, and nobody has ever tested
whether it's in the right place.**

I should also report that **my own proposed measure failed its test.** I invented a way to estimate
distance from a word's neighbours, and it looked good on every preliminary check — but it does not
actually predict which words the system succeeded in learning. **The measure the substrate was
already recording is the better lead, and I had that backwards for an hour.**

## QUESTIONS

None.

## NEXT STEPS

1. **Sweep `SENSE_MATCH_THRESH`** -- it is a one-parameter sweep with 11,012 recorded distances
   already in hand, and it must be scored on grounding QUALITY (hand-scored), not on volume, because
   volume trivially increases as the threshold falls.
2. **Populate `candidate_object`** -- one field, currently `None` in every row, and it blocks the
   fairer validity test.
3. `grounded_neighbour_fraction` is **parked, not promoted** -- graded but unvalidated.
