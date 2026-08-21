# **THREE PASSES, FIVE KILLS -- AND THE SPLIT IS NOT RANDOM. THE CAREFULLY-WRITTEN NOTES PASS; THE SUMMARY HEADLINES AND MY OWN QUICK INFERENCES FAIL.**

**The constraint check -- put a number beside another number that constrains it -- has now been run
on eight claims. It discriminates, and WHAT it discriminates on is the useful part.**

---

## 1. THE SCOREBOARD

| # | claim | verdict | what the constraint was |
|---|---|---|---|
| 1 | three-way comparison (`-0.142/item`) | ✅ **PASS** | per-set differences mean to **−14.200 pp = −0.142**, EXACT |
| 2 | NORMS12 (`rho 0.2701, +0.1653`) | ✅ **PASS** | `0.2701 − 0.1048 = 0.1653`, EXACT; CI excludes 0 |
| 3 | **E3b (`n=89, CI 0.22 wide`)** | ✅ **PASS** | CI `[−0.2500,−0.0337]` **= 0.2163 wide**; and 52/89, 64/89, 19/32 all reconcile |
| 4 | B1 "coverage cliff" | 🚫 **KILL** | tiers are relatedness LEVELS, not vocabulary STRATA -- **inverted** |
| 5 | "REFUTES reading can't supply knowledge" | 🚫 **KILL** | subset recalls ~54 items, whole recalls ~35 |
| 6 | my "6.2 traces/lemma" | 🚫 **KILL** | numerator and denominator from different populations |
| 7 | my "92,155 traces" | 🚫 **KILL** | exceeds the store's TOTAL 26,123 occurrences by 3.5x |
| 8 | my "63% past 0.79 recovery" | 🚫 **KILL** | threshold from a BIND/UNBIND task the store never performs |

*(plus my own `sample_tell` detector, killed at 3,990 false positives on DATES)*

## 2. 🎯 **THE SPLIT IS THE FINDING**

| | what they are |
|---|---|
| **ALL THREE PASSES** | **landed notes that carry a CI, a control, and a stated limit** |
| **THE FIVE KILLS** | **two inherited SUMMARY HEADLINES** (`ORGAN_MAP`'s cliff bullet; a `diagnosis.headline`) **and three of MY OWN same-day inferences** |

> ### **NOT ONE FAILURE CAME FROM A CAREFULLY-WRITTEN RESULT NOTE. NOT ONE PASS CAME FROM A HEADLINE.**

**And the passes are not passing by luck -- they pass because they were BUILT to be checkable:**
- the three-way note reports the four per-set values, so the paired figure can be re-derived;
- NORMS12 reports both arms' rho, so the difference can be re-derived, **and volunteers its own
  coverage limit and a prior negative against it**;
- E3b reports 52/89, 64/89, 19/32 as counts, so every rate can be re-derived, **and flags its own
  scramble as running on a different subset**.

***A claim that shows its working can be checked. A headline cannot -- and headlines are what I
quoted.***

## 3. ⚠️ WHAT I GOT WRONG *IN THIS CHECK*, RECORDED BECAUSE IT MATTERS

**I suspected E3b before I checked it.** *"CI 0.22 wide at n=89" exceeds the maximum possible
normal-approximation width for a proportion (0.2078 at p=0.5), which looked like a violation.*
**It is not: the interval is on a DIFFERENCE, `[−0.2500, −0.0337]`, where a wider interval is
expected.** *I have manufactured a violation from a plausible-looking heuristic twice tonight
already; opening the source first is what stopped a third.*

## 4. ➡️ THE OPERATIONAL RULE THIS YIELDS

> **QUOTE THE NOTE, NEVER THE HEADLINE -- AND IF THE NOTE DOES NOT SHOW ITS WORKING, TREAT THE
> NUMBER AS UNVERIFIED RATHER THAN AS EVIDENCE.**

*This is sharper than "check things", because it says exactly WHERE to look and exactly WHAT makes a
claim checkable: the constituent counts, the control, and the stated limit. All three passes have
all three. The `ORGAN_MAP` bullet and the `diagnosis.headline` have none.*

## TLDR

I've now run the same simple test — **put a number next to another number that limits it** — on eight
of our standing claims. Three survived, five didn't. **The interesting part is which.**

**All three survivors are properly written-up results.** Each one shows its working: it gives the
individual numbers that add up to the headline, includes a check that could have failed, and states
plainly what it does *not* cover. Because they show their working, I could re-derive their headline
figures independently — and all three came out exactly right.

**All five failures are either one-line summaries copied from a reference document, or my own
same-day reasoning.** Not one failure came from a careful write-up. Not one success came from a
summary line.

**So the rule isn't "be more careful" — it's "quote the write-up, never the summary".** And there's a
concrete test for whether a write-up is worth quoting: does it give you the pieces that make up its
headline number, does it include a check that could have gone against it, and does it say what it
doesn't cover? Our three survivors do all three. The failures do none.

**One thing I got wrong inside this very check:** I suspected the third claim was impossible before
reading it, because its error bar looked too wide to be real. It wasn't — it measures a *difference*
between two things, where a wider bar is normal. **I've invented a problem from a plausible-looking
shortcut twice tonight; opening the actual file first is what prevented a third.**

## QUESTIONS

None.

## NEXT STEPS

1. **Quote the note, never the headline.** *If it doesn't show its working, the number is unverified.*
2. **The three-part test for a quotable claim:** *constituent counts, a control that could fire, and
   a stated limit.* All three passes have all three.
3. *`ORGAN_MAP`'s B1 bullet has now been corrected at source; the `diagnosis.headline` that failed is
   flagged in `STATUS`'s ARCHIVE FIXED row.*
