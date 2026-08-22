# **ARE WE MAKING PROGRESS? — A PLAIN ANSWER TO YOUR THREE QUESTIONS**

*You asked three things and I went and did more measurements instead of answering. Here are the
answers, in ordinary words, with the numbers explained rather than quoted.*

---

## 1. "HOW ARE WE DOING ON PERFORMANCE NOW?"

**Worse than I have been telling you, and I found out today by building a test nobody had built.**

The task I have spent this week on: the system reads a story where a character wants something, and
has to say whether they got it.

| | score out of 100 |
|---|---|
| **our four-part reasoning machine** | **47** |
| just answering "yes, they got it" every time | 64 |
| **counting negative words in the last sentence** *(one line of code)* | **81** |

**A single line of pattern-matching — no understanding of the story, no idea who anyone is — beats our
purpose-built machinery by more than thirty points.** And until today we were comparing ourselves
against the 64, because nobody had tried the 81.

**That is the honest performance picture on this line, and it is the least flattering version I have
ever sent you.**

## 2. "DID THE NEUROSCIENCE PERSPECTIVE PRODUCE BETTER RESULTS? IS IT CONCRETE?"

**It has produced better DIAGNOSES. It has not yet produced a better SCORE. Both halves are true and I
do not want to blur them.**

**Where it concretely helped, today:**

- You ruled that a component only gets connected once it does the job required of it *as according to
  the brain*. I applied that per-use rather than in general — and it **stopped a wiring I had already
  talked myself into.** The spelling-recognition part is genuinely excellent at recognising words
  (from 1 correct in 200 to 96 in 100). It is worthless for meaning — I measured it, twice, and one of
  those tests was designed to give it the best possible chance. **So it got connected to recognition
  and barred from meaning.** That is your rule doing real work.
- The sharpest insight of the week came from asking what a *reader* does. When a person cannot work out
  whose outcome a sentence describes, **they keep reading — they do not conclude it went badly.** Our
  code concludes it went badly. I reached that from the brain side and from the numbers side
  independently, and they agreed.

**Where it has not helped yet:** none of this has moved a score. **Diagnosis is not performance**, and
I would rather say that plainly than dress up a good week of understanding as progress you can bank.

## 3. "ARE WE MAKING PROGRESS? WHAT WOULD COMMERCIAL READINESS TAKE?"

**Not close, and I want to give you a real sense of the distance rather than a feeling.**

**What is genuinely working:**
- One part of the judging machinery — the part that decides "yes, this went well" — is right about 78%
  of the time, better than guessing. **It is the only component on this line that beats its own
  baseline.**
- The word-recognition organ does its job extremely well, now that it is connected to the right job.
- **The measurement discipline is working, and that is not nothing.** This week it caught six of my own
  wrong conclusions before they reached you, including one where I had a tidy explanation that the
  cheapest possible test destroyed.

**What is not working:**
- The three parts that decide "no, this went badly" are right 36% of the time. **They are worse than
  staying silent**, because the safe default already beats them.
- The whole judging cascade, on the cases it was built for, **cannot be shown to do better than a coin
  flip.**
- **Every judgement on this line is being decided by 36 test questions.** That is too few to settle
  anything, and it has been the limiting factor in three separate investigations this week.

**What commercial readiness would require, concretely:** a system that beats the simple tricks — not
the naive baseline, the *good* tricks like the one-line word counter — on a test set of hundreds rather
than 36, on text it has never seen, without a language model doing the reading. **We currently lose to
the simple trick on the one task I have measured most carefully.** I cannot give you a date and I would
not believe one if I wrote it.

## 4. THE HONEST SHAPE OF THIS WEEK

**I got a lot right and most of what I got right was finding out I was wrong.** Six retractions, each
caught by me before it became a decision:

- I asked your permission to build something **we already had** — I had described a mechanism by where
  it looks instead of by how it decides.
- I found a spectacular-looking cause of the failure (the system learns that 96% of words mean
  "bad"), **and the cheapest possible test showed the lopsided version works BETTER than the balanced
  one.** I was one step from filing it as the explanation.
- I recommended making the machinery speak up more often, then found **it is a coin flip when it does
  speak** — so that advice would have routed more work to a coin flip.
- I claimed a fix was an improvement; the correct statistical test, which I had to build, **refused
  it.**

**That is the process working.** But I want to be straight: **a week where the main output is six
corrected errors and a much harder bar is a week of understanding, not a week of progress.**

## TLDR

**Performance: worse than I had been reporting.** On the task I know best, one line of pattern-matching
beats our purpose-built reasoning by 30 points, and we had been measuring against an easier bar.

**The neuroscience framing: real, concrete, and working — as a way of deciding what NOT to build.** It
stopped me connecting a component in the wrong place this week and it gave the sharpest insight of the
week. It has not yet produced a better score.

**Progress: understanding, yes. Capability, no.** One component beats its baseline. The rest of that
subsystem does not, and part of it is worse than doing nothing.

**Commercially: not close, and the honest blocker is that we lose to simple tricks on our best-measured
task.**

## QUESTIONS

**One, and it is a real fork I would like your call on.**

I have spent this week taking one subsystem apart and I now understand it well: I can tell you exactly
which pieces work, which are worse than silence, and what each one could possibly be worth even if
perfected. **What I have found is that no single repair in it can clear the bar** — the arithmetic says
so, several times over.

**So: do you want me to keep going on this subsystem, or stop and write up what we have?** My
recommendation is **STOP taking it apart and spend the next stretch making the test itself bigger** —
everything here is being decided by 36 questions, and I have now hit that limit three separate times in
one week. **The risk of my own recommendation:** building a bigger test set is slow, unglamorous, and
produces no capability at all; if the subsystem is fundamentally the wrong design, a bigger test just
measures the wrong thing more precisely.

## NEXT STEPS

1. **If you say keep going:** the only lever left with enough behind it is why the machinery cannot beat
   a coin flip on the cases it was designed for.
2. **If you say stop:** I write up the subsystem's map — what works, what is worse than silence, what
   each repair is worth — so it is not re-derived later, and move to the grounding line.
3. **Either way**, the harder bar (81 rather than 64) is now built into the code and every future result
   on this line will be graded against it.
