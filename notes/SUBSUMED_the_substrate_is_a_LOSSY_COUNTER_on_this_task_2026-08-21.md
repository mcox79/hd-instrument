# **SUBSUMED**: THE SUBSTRATE'S ANOMALY SIGNAL IS A **WEAKER VERSION OF COUNTING**, NOT SOMETHING OF ITS OWN

**"Behind" and "subsumed" are different findings with opposite consequences, and I had only measured
the first.** The paired test said we score below counting. That leaves open whether we contribute
anything counting lacks. **We do not.**

| on 478 anomalous sentences -- did the arm put the planted word FIRST? | observed | if INDEPENDENT |
|---|---|---|
| both arms hit | **88** | 62.3 |
| **SUBSTRATE ONLY** -- the contribution in question | **58** | **83.7** |
| counting only | 116 | 141.7 |
| neither | 216 | 190.3 |

*substrate hit rate 0.305, counting 0.427.*

> **substrate-unique rate MINUS what independence predicts = `-0.0537`, 95% CI `[-0.0741, -0.0330]`.**
> **The CI excludes zero. SUBSUMED.**

---

## 1. WHAT THIS ACTUALLY SAYS

**The two arms agree far more than two independent arms of those rates would** -- 88 joint hits where
independence predicts 62, and only 58 substrate-unique wins where independence predicts 84.
**That is the signature of one underlying signal read twice, not of two sources.**

**➡️ ON THIS TASK THE SUBSTRATE IS A LOSSY COUNTER.** It succeeds mostly where counting already
succeeds, less often, and its unique wins are *below* chance rather than above it.

**AND THIS MATTERS MORE THAN THE MARGIN DID.** *"We score 16 against counting's 29"* leaves room for
"but we get different items, so combining helps". **That room is now closed by measurement.**

## 2. ✅ IT REPRODUCES A RESULT THIS PROJECT ALREADY HAS

The same analysis was run before on two other routes and returned **both** answers: the **cortical
read came back SUBSUMED** (unique contribution below what independence predicts, at every k), and the
**sensorimotor spoke came back NOT SUBSUMED** (~independent of counting, contribution more than
doubled). **So the method discriminates, both outcomes were live, and the answer here is not an
artifact of a test that can only say one thing.**

## 3. WHAT IT DOES **NOT** SAY -- AND THE LIMITS ARE REAL

- **One task, one corpus.** Anomaly detection is not comprehension. *"Subsumed on this task"* is not
  *"subsumed in general"*, and the sensorimotor precedent shows different routes can differ.
- **It does NOT say the substrate has no signal.** `+16.3 pp`, `REPLICATED`, 4/4 CIs excluding zero,
  and **0 pp before reading** -- the learning is real. **Subsumption says the signal is not
  INDEPENDENT, not that it is absent.**
- **58 items are still substrate-only.** The finding is that this is *fewer* than chance, not zero.

## 4. 🎯 WHAT IT MEANS FOR THE BUILD

**F5 would read a situation model built from these representations.** If the representation is a
lossy counter on this task, **a monitor built on it inherits that** -- and the honest expectation is
an arm that lands between the substrate and counting, which is exactly the risk I recorded when
recommending F5 and which now has evidence behind it rather than pessimism.

**The sharper implication: the interesting question is no longer "how do we score higher" but "what
would make the representation carry something counting cannot".** *That is a different and harder
question, and it is the one this measurement hands over.*

## TLDR

We already knew our system scores worse than plain word-counting at spotting an odd word. **The
question left open was whether we at least get *different* ones right — because if so, the two could
be combined and each would be contributing something.**

**They cannot.** We succeed almost entirely on the sentences counting already handles, and the
overlap is much higher than chance would produce. Where two genuinely different methods would
disagree on about 84 sentences, we only manage 58.

**So on this task our system is a weaker copy of counting rather than a different approach.** That is
a harder finding than "we score lower", because "we score lower but differently" would have left a
route open, and this closes it.

**Three things it does not mean.** It is one task, and this project has run this same check before on
a different component and got the opposite answer, so the test can say both things. It does not mean
our system learned nothing — it scores zero before reading and something real after. And it is not
total: there are still 58 sentences only we get, just fewer than chance would give.

**What it changes:** the useful question stops being "how do we score higher" and becomes "what would
make what we build carry something counting cannot". That is harder, and it is the question this
hands over.

## QUESTIONS

None.

## NEXT STEPS

1. Any future arm should be checked for subsumption, not just for margin -- `tools/is_the_substrate_
   signal_subsumed_by_counting.py` generalises to any two detectors.
2. The finding strengthens, with evidence, the risk already recorded against building F5 on this
   representation.
