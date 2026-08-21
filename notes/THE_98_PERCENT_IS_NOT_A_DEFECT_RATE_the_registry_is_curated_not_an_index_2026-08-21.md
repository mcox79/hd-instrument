# **"98% OF HARD_PASS CELLS HAVE NO REGISTRY ROW" IS A REAL MEASUREMENT AND *NOT* A DEFECT RATE -- RECORDED SO NOBODY RE-RUNS IT**

**Measured, with an exact join key (registry `path` entries -> experiment filenames, not name
guessing) and a working positive control:**

| | |
|---|---|
| registry rows | **210** |
| distinct experiment files any row cites | **272** |
| landed `HARD_PASS` cells (excl. `_smoke` / `_selftest`) | **2,005** |
| **of those, no registry row cites their file** | **1,974 (98%)** |
| positive control | both capabilities I registered tonight now read **CITED** ✅ |

---

## ⚠️ **WHY I AM NOT REPORTING THIS AS A FINDING**

**THE REGISTRY IS A CURATED LIST OF CAPABILITIES. IT IS NOT AN INDEX OF EVERY CELL THAT PASSED, AND
IT WAS NEVER MEANT TO BE.** *A `HARD_PASS` on a diagnostic, a measurement, a floor calibration or a
self-test is **not a capability to wire** -- there is nothing to promote. 210 rows against 2,005
`HARD_PASS` cells is a **curation ratio**, not a coverage failure.*

**➡️ THE NUMBER IS ACCURATE AND THE INFERENCE FROM IT WOULD BE FALSE.** *This is exactly the failure
my own audit named an hour ago -- **a generalisation drawn from a population that does not support
it** -- so I am stopping at the measurement.*

**AND IT IS THE SAME SHAPE AS THE KEY-AUDIT TOOL THAT FAILED EARLIER TONIGHT:** *1,925 -> 871 -> 801
-> 132 suspects, legitimate at every level.* **A check that fires on 98% of its population cannot be
acted on, and `CLAUDE.md` already records that such a check gets ignored.**

## WHAT WOULD MAKE IT MEANINGFUL, AND WHY I AM NOT DOING IT

**The meaningful question is narrower: how many `HARD_PASS` cells are CAPABILITY-SHAPED** -- an
extractor, an organ, a mechanism someone could wire -- **rather than a measurement?** *That is not
mechanically separable from a verdict string, and every heuristic I would reach for (verdicts
containing `VIABLE`, `WORKS`, `USEFUL`) is the same keyword guessing that produced tonight's failed
key-audit.*

**THE TWO I FOUND TONIGHT WERE FOUND BY READING, NOT BY THIS METRIC** -- cold placement and the
90%-precision entity-fate extractor -- **and in both cases what identified them was that a HUMAN
would obviously want them in the inventory.** *That judgement is the filter, and I do not have a
cheap mechanical proxy for it.*

## TLDR

I measured how many of our passing experiments are missing from the capability list. **The answer is
98%** — and **it means almost nothing**, so I'm recording it here specifically so nobody runs it again
and reports it as a scandal.

The capability list is a **deliberately curated** set of things worth reusing. Most passing
experiments are measurements, calibrations and diagnostics — **there is nothing in them to reuse.**
So "98% aren't listed" is roughly like observing that 98% of a lab's completed measurements aren't in
its equipment inventory. True, and not a problem.

**The number is right and the conclusion would be wrong** — which is precisely the mistake my own
audit identified an hour ago, so I stopped at the number.

**The two genuinely missing capabilities I did find tonight, I found by reading them** and
recognising that a person would obviously want them catalogued. I don't have a cheap automatic
version of that judgement, and the attempts I made tonight to build one all produced lists too long
to act on.

## QUESTIONS

None.

## NEXT STEPS

1. **Do not re-run this as an audit.** *The measurement is here; the inference it invites is invalid.*
2. Capability-shaped results are found by reading, and tonight's two were found that way.
3. **This is the second mechanical audit tonight that produced an unusable population** -- consistent
   with my own audit's conclusion that the remaining yield is in building, not scanning.
