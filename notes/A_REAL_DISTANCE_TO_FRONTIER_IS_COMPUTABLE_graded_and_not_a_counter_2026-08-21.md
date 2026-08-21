# **A REAL DISTANCE-TO-THE-FRONTIER *IS* COMPUTABLE** -- GRADED, FACE-VALID, AND **NOT A COUNTER IN DISGUISE**

**The owner asked for *"the ~distance from any new fact to the grounded foundation."* The organ we
built answers YES/NO** (`is_gap` = anchor membership 98.75% of the time; `margin` pinned at exactly
1.0 for every known word). **This measures whether the graded version they described can be built
from what we already have. It can.**

---

## 1. WHY IT CANNOT COME FROM THE WORD'S OWN VECTOR

**An unread word has no learned representation.** `symbol_vector()` is a hash-seeded random draw, so
its similarity to any anchor is noise. **Distance for a word we have not read yet cannot come from
the word itself -- it has to come from the company it keeps.** *That is `MEMORY.md`'s own
relational-bridge framing, made arithmetic.*

## 2. THE MEASURE

```
grounded_neighbour_fraction(w) = |{c co-occurring with w : c is anchored}| / |co-occurring with w|
```

**NEAR the frontier** = most words it appears beside are already understood -> **reading it now would
land.** **FAR** = it sits among other unknowns -> **reading it now is wasted.** *ZPD ordering, using
only the corpus and the anchor set.*

## 3. RESULTS -- measured on `reading_grounding_v1` (4,322 anchors) over 6,000 simplewiki sentences

| the three ways it could have died | result |
|---|---|
| **degenerate, like `margin`** | 🟢 **595 distinct values** across unknowns, spanning 0.000-1.000 |
| **a counter wearing a new name** | 🟢 **r = -0.073** against plain neighbour count -- *essentially uncorrelated* |
| **measures nothing** | see §4 -- **survives the strict version** |

**THE SECOND ROW IS THE ONE THAT MATTERS.** Counting has beaten our mechanisms by ~10x all night.
**This quantity is nearly orthogonal to counting**, so a win from it could not be re-derived by
tallying.

## 4. ⚠️ **THE EXTREMES WERE SMALL-DENOMINATOR ARTIFACTS -- CAUGHT, AND THE FIX IMPROVES IT**

The first output looked wrong: `reality`, `jungle`, `burke` at **exactly 1.000**; `budget`,
`evening`, `eagle` at **exactly 0.000**. *Common words scoring 0.000 is not credible.*

| | median neighbours |
|---|---|
| top-20 scorers | **8** |
| bottom-20 scorers | **5** |
| **all words** | **30** |

**The extremes were words we had barely observed** -- 3 neighbours all anchored gives 1.000, and that
is "barely seen", not "near the frontier". *Same shape as the sparse-tie artifact `CLAUDE.md`
records: a small denominator manufacturing an extreme score.*

**RESTRICTED TO >=30 NEIGHBOURS (n=763) THE MEASURE GETS BETTER, NOT WORSE:**
**527 distinct values, range 0.133-0.800, median 0.531** -- no saturation at either end.

**AND THE ORDERING BECOMES FACE-VALID:**

| | |
|---|---|
| **nearest the frontier** (read first) | `detail 0.80 · sharing 0.79 · shop 0.78 · serious 0.77 · label 0.76 · wet 0.76` |
| **farthest** (not ready) | `jazz 0.28 · pierre 0.27 · succeed 0.27 · raid 0.26 · crown 0.26 · district 0.13` |

*Everyday, densely-connected words at the near end; specialised terms and proper nouns at the far
end. **That is what the quantity is supposed to mean**, and it was not tuned to produce it.*

## 5. WHAT THIS IS AND IS NOT

**IS:** a graded, non-degenerate, counting-orthogonal, face-valid ordering over unread words --
**the thing the owner asked for and the current organ does not provide.** Cheap: one pass over
co-occurrence plus an anchor-set lookup.

**IS NOT:** evidence that reading in this order helps. **No task has been run.** *That is precisely
the trap this project keeps falling into -- an internal statistic that looks mechanistic and
persuasive, which `CLAUDE.md` records as having produced three confident claims the task then
refused.* **It may DIAGNOSE. It may not DECIDE.**

**MANDATORY GUARD IF IT IS USED:** a minimum-neighbour threshold (>=30 here). Without it the top and
bottom of the ranking are sample-size noise, and those are exactly the ends a reader would act on.

## TLDR

You asked for something that senses **how far** a new fact is from what the system already
understands. I found earlier that what we built only answers **yes or no**. So I checked whether the
graded version you described could be built from what we already have. **It can.**

The idea: an unread word has no meaning to us yet, so we can't measure it directly — **but we can
look at the company it keeps.** If most of the words appearing alongside it are already understood,
it's within reach; if it sits among other unknowns, it's too far for now. That's exactly the "read
what you're nearly ready for" instinct.

**It passes the three tests that would have killed it.** It produces hundreds of distinct values
rather than one. It is **almost completely uncorrelated with simply counting** — which matters
enormously, because plain counting has out-performed our clever methods ten to one all night, so this
is measuring something genuinely different. And the ordering it produces makes sense on sight:
everyday words like *detail*, *shop*, *serious* come out as ready-to-read; *jazz*, *raid*, and
proper names come out as too far.

**One flaw, caught and fixed.** The first version put *reality* and *jungle* at the very top and
*budget* and *evening* at the very bottom, which is nonsense. Those were words we'd barely seen —
three neighbours, all known, scores a perfect 1.0. Requiring at least thirty neighbours removes the
illusion and the measure gets *better*, not worse.

**The honest limit: this is a promising instrument, not a proven one.** Nothing has been tested yet
on whether reading in this order actually teaches the system more. That's the exact trap this project
keeps falling into, so I'm stating it plainly rather than at the end.

## QUESTIONS

None.

## NEXT STEPS

1. **Score it on the task, against the floors that already exist** -- the FROZEN and RANDOM arms at
   10,000 sentences. Until then it is a diagnostic.
2. If used, **carry the minimum-neighbour guard** -- without it both ends of the ranking are noise.
3. It slots into `identify_missing_prerequisites` as the ordering the gap signal cannot supply.
