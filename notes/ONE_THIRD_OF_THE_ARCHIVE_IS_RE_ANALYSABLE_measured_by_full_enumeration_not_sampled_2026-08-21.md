# **ABOUT ONE CELL IN THREE CAN ANSWER A QUESTION IT WAS NEVER ASKED. MEASURED BY FULL ENUMERATION OF ALL 7,905 CELLS, NOT SAMPLED.**

**Every finding I made tonight came from re-analysing a cell that already existed -- three for three.
Against my own recorded impression that almost nothing is re-analysable, three for three is unlikely
enough to check. So I checked all of them.**

---

## 1. THE MEASUREMENT

**Enumerated from disk: every `data/exp_*` directory. `n = 7,905`. Nothing sampled.**

| | count | share |
|---|---|---|
| extra files including a **DATA** extension (`.json`, `.jsonl`, `.npz`, `.npy`, `.csv`, `.pkl`...) | **2,012** | 25.5% |
| no extra files, but **metrics.json holds a population** (a list *or dict* of >=50 entries) | **435** | 5.5% |
| **➡️ CONFIRMED RE-ANALYSABLE** | **2,447** | **31.0%** |
| **summary-only -- must RE-RUN to ask anything new** | **~5,356** | **67.8%** |

## 2. TWO CHECKS ON MY OWN METHOD, BOTH OF WHICH CHANGED THE ANSWER

**(a) COUNTING ONLY LISTS UNDERCOUNTED BY 35%.** *My first pass looked for a list of >=50 items and
found 283. Populations are often stored as a **dict keyed by item** -- `COMPOSITION_PER_ARM`,
`feature_provenance` -- and counting those too gives **435**.* **A heuristic's blind spot is part of
its result.**

**(b) THE "EXTRA FILES" COUNT IS *NOT* INFLATED BY LOGS.** *The obvious objection is that a cell with
a stray `.log` would be counted as re-analysable. Measured: extra-file extensions are `.json` 3,759,
`.jsonl` 450, `.npz` 228 against `.log` **45** -- and only **15 cells** have extra files that are
**all** log-ish.* **The objection is real and it is small.**

## 3. ⚠️ WHAT THIS NUMBER IS NOT

**It is NOT a refutation of the earlier "158 saved / 3,518 not" figure.** *That was a different
population (3,676, not 7,905) and, as far as I can tell from its own record, a different criterion. I
have not re-derived it and I am not claiming it wrong.* **Discipline 11: a number may not be carried
between populations. This one is defined here and stands on its own.**

**It is a LOWER bound in one direction and a LOOSE one in the other:** *a saved population of fewer
than 50 entries is not counted; and a `.json` sibling is not guaranteed to be the population that was
scored -- tonight's own counter-example is the 90%-precision extractor, whose v2 saved a 37 KB
hand-check SAMPLE rather than its 1,414 survivors, and would be counted re-analysable here while
being unable to settle the question actually asked of it.*

## 4. 🎯 WHY IT MATTERS -- IT IS A DECISION RULE, NOT A STATISTIC

**Tonight, four separate times, the choice was "re-analyse or re-run":**

| question | which third | outcome |
|---|---|---|
| what ARE B1's three tier numbers? | `per_unit[0].per_triple` **inline** | **answered in minutes -- and overturned a claim I had put in three documents** |
| does B4's d-sweep move? | `curve_by_dimension` **inline** | **answered; also showed the map's "probe scale" label was wrong** |
| does the write-less curve drift to ties? | `units.jsonl` **per-pair scores** | **answered; refuted my own suspicion and reversed a board recommendation** |
| what did the 90% extractor throw away? | **v2 saved only its SAMPLE** | 🚫 **unanswerable -- must re-run** |

> **THREE OF FOUR WERE ALREADY ON DISK. TWICE IN ONE NIGHT I ASKED THE OWNER FOR PERMISSION TO
> PRODUCE A NUMBER THAT WAS ALREADY SAVED.** ***THE RULE THAT FOLLOWS: BEFORE CONCLUDING "WE MUST
> RE-RUN", OR FILING A QUESTION ASKING FOR A MEASUREMENT, OPEN THE CELL. ROUGHLY ONE TIME IN THREE
> THE ANSWER IS SITTING THERE.***

## TLDR

Everything I worked out tonight came from re-reading experiments we had already run — three times out
of three. That surprised me, because I'd recorded the impression that almost nothing we run is worth
re-reading. **So I counted all 7,905 of them, rather than guessing from a sample.**

**About one in three can answer a question it was never asked.** Either they saved their working
alongside the summary, or the summary itself quietly contains the full detail. **The other two-thirds
kept only the conclusion**, so asking anything new of them means running them again.

**Two things I checked about my own counting, and both changed the answer.** My first method only
recognised results stored as lists, and missed a third of them, which are stored keyed by name
instead. And the obvious objection — that I was counting stray log files as if they were data — turns
out to be true for only fifteen cells out of thousands.

**Why this matters is practical, not statistical.** Four times tonight the choice was "dig into what
we have" versus "run it again". **Three times the answer was already sitting on disk** — including
one that overturned a claim I'd written into three planning documents, and one that reversed advice
I'd given you an hour earlier. The fourth genuinely wasn't there, because that experiment saved only
the hundred examples it graded rather than everything it produced.

**Twice tonight I asked you to approve producing a number that was already saved.** The habit worth
keeping is simply: **open the file before asking.**

## QUESTIONS

None.

## NEXT STEPS

1. **Before concluding "we must re-run", check which third the cell is in.** *One in three times the
   work is already done.*
2. **The two-thirds that kept only conclusions are the real cost of the save-only-your-summary
   habit** -- three separate instances of it were found earlier tonight, in unrelated subsystems by
   different authors.
3. *No action needed on the number itself; it is recorded so nobody re-derives it.*
