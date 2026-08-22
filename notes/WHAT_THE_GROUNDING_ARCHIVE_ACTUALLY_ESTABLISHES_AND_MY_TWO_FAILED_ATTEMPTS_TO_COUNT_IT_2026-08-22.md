# **THE GROUNDING ARCHIVE: `237` CELLS, `219` LANDED, `41` HARD_PASS -- AND I TRIED TWICE TO COUNT WHAT IS EVIDENCED AND WAS WRONG BOTH TIMES BY `14x` AND `4x`.**

*Owner: "we did a fuckton of work on grounding. make sure you understand all of it." Starting the
map, and the first thing to understand is that the archive's own labels cannot be counted naively --
which I proved on myself twice in twenty minutes.*

---

## 1. THE SIZE OF IT

| | |
|---|---|
| cells matching `grounding` | **237** (`219` landed) |
| of those, verdict `HARD_PASS` | **41** |
| archive-wide: HARD_PASS carrying **BOTH a CI and a null** | **14 of 2,680** = **`0.5%`** |

**So the headline count is not "41 grounding wins". It is "41 labels, drawn from a population where
99.5% of that label does not carry the evidence the label claims".** *That is the standing 2026-08-18
audit finding, and it applies here undiluted.*

## 2. 🔻 **MY TWO ATTEMPTS TO COUNT THE EVIDENCED SUBSET, BOTH WRONG**

| attempt | result | truth |
|---|---|---|
| my own CI/null regex | **198** carry both | census: **14** |
| **the census tool's OWN patterns**, my loop | **58** carry both | census: **14** |

**Even borrowing the instrument's exact regexes I was still `4x` off, and I scanned `3,200`
HARD_PASS cells where the census scans `2,680`.**

> ### 🔑 **THE BUG, FOUND BY QUERYING ONE CELL PROPERLY: I MATCHED THE STRING `HARD_PASS` ANYWHERE IN THE FILE. THE CENSUS READS THE *VERDICT FIELD*.**

*`exp_grounding_quality_readout_v1` came back in my list as a HARD_PASS. Its verdict is
`STRUCTURAL_PASS_PENDING_B3`, and it has **no null at all**. The string appears in gate-name fields.
**520 of my 3,200 are cells that merely MENTION the label.***

***Two reimplementations of a purpose-built, self-tested instrument, both confidently wrong, both
about to become numbers in a report.*** **The rule earns itself again: use the instrument, do not
imitate it.**

## 3. ✅ WHAT IS ACTUALLY EVIDENCED -- VERIFIED CELL BY CELL THROUGH THE TOOL

| cell | verdict | CI | null | floor | what it establishes |
|---|---|---|---|---|---|
| **`exp_reading_grounding_loop_cycle2_v1`** | HARD_PASS | ✅ | ✅ | ✅ | *the reading loop's foundation **persists and grows**: `185 -> 3,544` entries in one cycle, scramble ratio `0.077`, no-leak and monotonicity both checked* |
| **`exp_foundation_validation_harness_v4_proximity_v1`** | HARD_PASS | ✅ | ✅ | ✅ | *proximity claim clears a **frequency floor**: gap `0.2667` over floor `0.22`, precision `0.4867`, with a known-answer instrument-validity gate that PASSES (`chance_hat 0.04`)* |
| `exp_grounding_quality_readout_v1` | 🔻 **not HARD_PASS** | ✅ | 🔻 **no** | ✅ | *`STRUCTURAL_PASS_PENDING_B3` -- I had it in my list as a pass* |

**These two are real and worth knowing: the loop genuinely accumulates, and one grounding claim
genuinely clears a real floor with a validity gate attached.** *That is more than "no evidence" and
much less than "41 wins".*

## 4. ⚠️ WHAT THIS MAP IS NOT, YET

1. **`38` grounding cells remain unverified individually.** *My bulk list is unreliable by
   construction, so the honest position is that only the cells I queried one at a time are known.*
2. **Evidence-carrying is not correctness.** *The gate's own docstring: it cannot see a written-in
   answer, gold defined by the rule under test, a skipped stronger floor, or a gate tuned after the
   fact. **A cell can pass it and still be worthless.***
3. **I have not yet read either verified cell's method**, only its verdict fields.

## TLDR

You asked me to make sure I understand all the grounding work. **There are 237 experiments on it, 219
finished, 41 marked as wins.**

**The 41 is not a count of things that worked.** A standing audit of this project found that only about
1 in 200 results labelled "win" actually carries the two statistical checks that would justify the
label. That applies here too.

So I tried to count how many grounding results *do* carry those checks. **I got 198. Then, using the
official tool's own definitions, 58. The official answer is 14.** I was wrong twice, by 14× and then
4×, and I found out only because I stopped and asked the tool about one single experiment instead of
running my own version of it.

**The cause was dumb and worth remembering: I was searching for the word "win" anywhere in the file
rather than reading the result field.** Some experiments merely mention the word in the names of their
internal checks. One I had listed as a win is not a win at all.

**What I can tell you stands up**, having checked them one at a time: the reading loop really does
accumulate knowledge as it reads — it grew from 185 to 3,544 entries in a single pass, with the
scrambled control failing as it should. And one grounding result genuinely beats a real baseline with a
sanity check attached. **Two solid things, not forty-one.**

**I'll keep going through the rest one at a time.** It's slower, and it's the only method that hasn't
lied to me today.

## QUESTIONS

None — Q105 (keep taking the subsystem apart, or build a bigger test set) is still open and this work
proceeds either way.

## NEXT STEPS

1. **Continue the map cell by cell through the tool**, not by bulk scan. *Priority: the cells on the
   live reading path, since those are the ones any capability claim would rest on.*
2. **Then read the METHOD of the two that passed** -- carrying a CI and a null is the cheapest hurdle,
   not the real one.
3. *Method note: **the instrument disagreeing with my reimplementation of it is the single most useful
   event of this turn.** Had the two agreed I would have reported 198.*
