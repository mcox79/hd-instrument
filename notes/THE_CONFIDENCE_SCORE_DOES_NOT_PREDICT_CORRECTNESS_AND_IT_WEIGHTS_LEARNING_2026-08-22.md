# A REFUTED EXPLANATION FOUND SOMETHING BIGGER: THE CONFIDENCE SCORE DOES NOT PREDICT CORRECTNESS

**2026-08-22, strategy session.** Chasing one unexplained number from the powered anchor+propagate
test ([the 26x note](ANCHOR_AND_PROPAGATE_SURVIVES_A_26x_LARGER_TEST_AND_THE_MARGIN_SHRINKS_2026-08-22.md)):
**shuffling the anchor's polarity labels made the organ commit MORE often, `564` against `326`.**
Shuffling a label set should not change how often a mechanism is confident.

---

## 1. THE ANOMALY IS EXPLAINED, AND MY EXPLANATION FOR IT IS WITHDRAWN

**WHAT SHUFFLING ACTUALLY DOES:**

| | committed | median confidence of committed |
|---|---|---|
| TRUE labels | `326` | **`1.0000`** |
| SHUFFLED labels | `564` | **`0.3380`** |

**Shuffling does not make it more confident. It makes it LESS confident but more often just over the
threshold.** The extra `238` commits are low-confidence, and they score at chance. *So the anomaly
does not undermine the seed ablation -- it sharpens it.*

🔻 **MY CAUSAL STORY FOR THAT IS REFUTED BY ITS OWN PREDICTION, AND I AM WITHDRAWING IT RATHER THAN
SOFTENING IT.** I proposed that real labels make the vote BIMODAL -- decisive inside a
valence-coherent cluster, balanced on a boundary -- which is the signature of real structure. **That
account predicts confidence should track accuracy.** I checked, because an explanation that only
redescribes the numbers it came from is not worth keeping:

| confidence band (TRUE labels) | n | accuracy |
|---|---|---|
| `[0.00, 0.34)` | 83 | `0.6747` |
| `[0.34, 0.67)` | 23 | `0.6522` |
| `[0.67, 1.00)` | 16 | `0.6875` |
| **`1.00` (saturated)** | **204** | **`0.6520`** |

**FLAT. The prediction failed, so the account goes.** *Stated before measuring, which is the only
reason the failure is legible.*

*(Partially salvageable and NOT claimed: WordNet neighbourhoods are moderately valence-coherent --
median polarity purity of a verb's 5 nearest anchors is `0.800` against a `0.5` coin flip, but `287`
of `600` items have a mixed top-5. That is a real measurement; it just does not rescue the
explanation.)*

---

## 2. WHAT THE FAILED PREDICTION FOUND INSTEAD, WHICH MATTERS MORE

🚨 **THE CONFIDENCE SCORE CARRIES NO DETECTABLE INFORMATION ABOUT WHETHER THE ANSWER IS RIGHT -- AND
IT IS USED TO WEIGHT WHAT THE LEARNING LOOP IS TOLD.**

`pseudo_counts_from_dictionary` does `n = round(K_MAX * confidence)` (`K_MAX = 3`), consumed at
`hdlab/word_learning_tool.py:48`. So a maximally-confident hit is injected into the consequence
learning loop with **three times the weight** of a barely-committed one. That is sound only if
confidence tracks reliability.

| | n | accuracy |
|---|---|---|
| saturated (confidence `1.0`, injected at **3** pseudo-counts) | `204` | `0.6520` |
| everything else (injected at **0-1**) | `122` | `0.6721` |
| **difference** | | **`-0.0202`, CI95 `[-0.1249, +0.0894]`** |

⚠️ **THE INTERVAL SPANS ZERO, SO THE SIGN CARRIES NOTHING AND "SLIGHTLY INVERTED" WOULD BE AN
OVERCLAIM.** What is supportable is the weaker and still consequential statement: **confidence does
not predict correctness on this population, so weighting the loop's evidence by it has no measured
justification.**

✅ **AND THE WEIGHT GENUINELY VARIES, so this is not moot:** `204` of `326` commits saturate
(`63%`), leaving `37%` injected at a third of the weight or less. *Had it been ~100%, the multiplier
would be a constant in practice and the question would not arise.*

---

## 2b. AND AT THE LOW END IT IS NOT A WEIGHT AT ALL -- IT IS A DELETE

`pseudo_counts_from_dictionary` does not merely down-weight a low-confidence hit:

```python
n = round(k_max * lu.confidence)
if n <= 0:
    continue          # no entry, ZERO influence
```

With `K_MAX = 3`, anything under confidence ~`0.167` rounds to zero. **The organ decided POS or NEG,
and the learning loop is never told.**

| | n | accuracy |
|---|---|---|
| survive the rounding | `263` | `0.6692` |
| 🔻 **DISCARDED by `if n <= 0`** | **`63` = `19%` of everything it decided** | `0.6190` |
| difference | | `+0.0502`, CI95 `[-0.0768, +0.1809]` -- **spans zero** |

*Pseudo-count distribution among survivors: `3` -> 211, `2` -> 27, `1` -> 25. So the discard is not
a rare edge case; it is a fifth of the organ's output.*

⚠️ **AND THE HONEST LIMIT, WHICH CUTS AGAINST THE OBVIOUS FIX: at `n=63` I ALSO CANNOT SHOW THE
DISCARDED ANSWERS ARE USABLE.** On their own subset they read `0.6190` against a `0.5714` majority
floor -- a margin of `+0.0476`, CI95 `[-0.1587, +0.2381]`, **crossing zero**.

**So this is a QUESTION TO SETTLE, NOT A DEFECT TO FIX.** What is established: the rounding discards
a fifth of the organ's decisions, and there is **no measured basis** for preferring the ones it
keeps. What is NOT established: that keeping them would help. *"Restore the discarded hits" is a
plausible-sounding change that this evidence does not license, and shipping it on these numbers
would be the same overclaim in the opposite direction.*

---

## 3. WHAT THIS IS AND IS NOT

- ✅ **IS:** a measured absence of calibration in a wired organ's confidence output, on `326` items
  graded against human ratings that pre-date the mechanism.
- 🚫 **IS NOT** a claim that the organ is wrong, or that any landed number is wrong. Its accuracy
  (`0.6595` over a `0.5583` floor) is unaffected -- **this is about the WEIGHT attached to each
  answer, not the answer.**
- 🚫 **IS NOT** a claim that the learning loop is measurably harmed. **I did not run the loop.** The
  chain from "uncalibrated weight" to "worse learning" is plausible and **untested**, and saying
  otherwise would be inventing the consequence.
- 🚫 **IS NOT** a landed cell -- an inline measurement, scripts in `scratch/`, no `metrics.json`.
- ⚠️ **SCOPE:** polar verbs only (`|valence - 5| >= 1.0`), one gold set, one anchor. The organ's
  designed job is OOV outcome-verbs inside the consequence loop, which is a **narrower and different
  population** than 1,971 dictionary verbs.

---

## 4. THE METHOD NOTE, WHICH IS THE REUSABLE PART

**THE EXPLANATION WAS THE MOST VALUABLE THING I PRODUCED, AND IT WAS WRONG.** Chasing one number I
could not explain -- rather than leaving it as a caveat -- cost about ten minutes and turned up a
calibration gap in a wired organ that nobody was looking for.

**WHAT MADE THE FAILURE LEGIBLE WAS WRITING THE PREDICTION DOWN BEFORE MEASURING.** "Confidence must
track accuracy" was derivable from my account and from nothing else. Without it I would have kept a
tidy story that happened to be false, and never looked at the confidence-accuracy join at all.

*This is the standing rule -- a statistic the mechanism OPTIMISES may diagnose, never decide -- with
a new face: **a statistic the mechanism EMITS is not evidence that the statistic MEANS anything.**
Confidence was computed, stored, documented, and multiplied into downstream evidence without anyone
ever checking it against an outcome.*

---

## TLDR

I chased a single number I could not explain: scrambling the hand-labelled starting words made the
system *answer more often*, which should not happen.

The explanation is that scrambling makes it much less sure of itself while still just clearing its
bar to speak — it goes from typically certain to typically hesitant, and hesitant answers are at
coin-flip. Fine, and it makes the earlier result look better rather than worse.

But I had a *reason* for that, and my reason predicted something specific: when the system says it
is certain, it should be right more often. **It isn't.** Certain answers are right about 65 times in
100; unsure ones about 67. So my reason was wrong and I have thrown it out.

The valuable part is what throwing it out revealed. That certainty number isn't decoration — it is
multiplied into how strongly the system's learning is nudged, so a "certain" answer counts three
times as much as an unsure one. **We have never checked whether certain answers are actually better,
and on this test they aren't.** I have not shown this makes learning worse — I did not run the
learning — but the weighting currently rests on an assumption nobody tested.

## QUESTIONS

None.

## NEXT STEPS

1. **Someone should run the learning loop with the weight flattened** (every committed hit worth the
   same) and see whether anything moves. That is the test that turns this from a calibration gap
   into a cost, or dismisses it.
2. **If the weight is kept, it needs a calibration check that can fail** — confidence against
   outcome, on the loop's own OOV population rather than on dictionary verbs.
3. The `17%` commit rate remains the bigger limit on this organ than its accuracy.
