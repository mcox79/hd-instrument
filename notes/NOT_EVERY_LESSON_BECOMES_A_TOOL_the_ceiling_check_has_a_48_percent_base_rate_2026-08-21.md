# **I DID NOT BUILD THE CEILING DETECTOR, BECAUSE I CHECKED ITS BASE RATE FIRST: 48.5% OF HARD_PASS CELLS WOULD FIRE. NOT EVERY GOOD LESSON BECOMES A TOOL.**

**"A perfect score usually means the task is broken" appeared three times tonight. The project's own
meta-rule says prose cautions get violated and code controls catch things, so the obvious move was to
build a detector. I measured its false-positive rate before writing it, and the answer says don't.**

---

## 1. THE PATTERN THAT TEMPTED ME

| # | the ceiling | what it actually meant |
|---|---|---|
| 1 | D3's self-test `ca3_one_shot_binding_recall` at `sign_agree = 1.000` | the task was trivially solvable; the organ was never tested |
| 2 | `CA3 OFF` at `hit@1 = 1.0000` for every N from 1 to 20,000 | completion was never REQUIRED at any load |
| 3 | the form channel at `hit@1 = 1.0000` | the query WAS the answer -- a lookup, not a task |

***Three ceilings, three broken benchmarks, one night. That is a real reading discipline.***

## 2. 🚫 **AND HERE IS WHY IT IS NOT A DETECTOR**

*Scanned every HARD_PASS cell for a metric-named field (`acc|auc|f1|precision|recall|hit|rate|frac|
score|agree|cos|rho|corr|recovery`) equal to exactly 1.0, excluding obvious non-metrics (`chance`,
`floor`, `threshold`, `max`, `min`, `seed`, `version`...).*

| | |
|---|---|
| HARD_PASS cells | **2,680** |
| **reporting a metric field at exactly 1.0** | **1,299 (48.5%)** |

> ### **A FLAG THAT FIRES ON HALF THE ARCHIVE IS NOT A FLAG. It would have been the second cry-wolf detector I shipped tonight.**

**And the 1.0s are mostly LEGITIMATE:** *positive controls that SHOULD sit at ceiling, determinism
assertions, known-answer arms, guard checks, and saturated sub-metrics inside otherwise sound cells.*
**A ceiling somewhere in a metrics file is the normal case, not the alarming one.**

## 3. 🎯 **WHY IT CANNOT BE NARROWED THE WAY THE OTHER CHECKS WERE**

**The discriminating signal is not "a 1.0 exists" -- it is "the HEADLINE CLAIM is at 1.0".** *That
requires knowing which field carries the claim, and nothing in a metrics file marks it. The verdict
string names a verdict, not a field.*

***Every narrowing I could think of is a guess about which key is the headline, and guessing which
key matters is precisely what produced the 3,990-false-positive detector earlier tonight.***

## 4. ✅ WHAT CHANGED, AND IT IS THE POINT

**Earlier tonight I built `sample_tell`, called it "deliberately narrow" on the strength of three
fixtures, and needed two more attempts after it fired 3,990 times on dates.** **This time I ran the
base-rate query BEFORE writing a line of the detector, and it cost one command.**

> ### **THE LESSON STAYS A READING DISCIPLINE: WHEN A NUMBER IS EXACTLY 1.0, ASK WHETHER THE TASK COULD HAVE PRODUCED ANYTHING ELSE. It belongs in the eye, not in a linter.**

## TLDR

Three times tonight a perfect score turned out to mean the test was broken rather than the method
good. Our own working rule says to turn lessons like that into automatic checks rather than written
warnings, because written warnings get ignored.

**So I checked what an automatic version would do before building it. It would flag nearly half of
everything we have ever passed** — 1,299 experiments out of 2,680.

**A warning that fires on half the archive is worthless**, and it would have been the second such
warning I shipped tonight.

**The reason is that most perfect scores are fine.** They're deliberate checks that something works,
tests that a result is repeatable, or a sub-measurement that happens to max out inside a perfectly
sound experiment. **A perfect number somewhere in a results file is normal.**

**What actually matters is whether the *headline* claim is perfect** — and nothing in the files marks
which number is the headline. Every way I could think of to guess that is exactly the guessing that
produced a four-thousand-false-alarm detector earlier tonight.

**So this one stays a habit rather than a tool.** When a number is exactly perfect, ask whether the
test could have produced anything else.

**The thing that improved is the order I did it in.** Earlier I built the detector, called it
carefully targeted on the strength of three toy examples, and needed two more rounds to fix it. **This
time I asked what it would flag before writing it — one command, and the answer was don't.**

## QUESTIONS

None.

## NEXT STEPS

1. **Do not build a ceiling detector.** *48.5% base rate; recorded so nobody re-proposes it.*
2. **Keep it as a reading habit:** *exactly 1.0 → could the task have produced anything else?*
3. *The general rule this instance supports: **measure a detector's base rate BEFORE writing it.**
   Tonight that check cost one query and saved a third round of fixes.*
