# TWO SESSIONS, TWO RESULTS THAT LOOKED CONTRADICTORY, BOTH REAL -- AND THE SYNTHESIS IS SHARPER THAN EITHER

**2026-08-23.** A concurrent session was working the same organ and reached conclusions that
**correct two things I told the owner**. This is the reconciliation, plus the measurement that makes
both results fit.

---

## 1. WHAT THEY FOUND, AND WHAT IT CORRECTS IN MY REPORT

🔻 **I SAID THE PROPAGATOR IS COVERAGE-LIMITED. THAT IS WRONG.** I wrote twice that its `17%` commit
rate is a bigger limit than its accuracy, and I never split the number. They did:

| of the `83%` that abstains | | |
|---|---|---|
| no anchor in range at all -- genuine REACH | `114` | **6 points** |
| anchors vote and DISAGREE -- DISCRIMINATION | `1,531` | **78 points** |

**So it is a discrimination problem, not a coverage one, and more hand-labelled anchors addresses the
small corner.** *Nor are they near-misses: balanced margins sit at median `0.0276` against a `0.15`
gate -- close to perfectly balanced, not narrowly short.*

🔑 **AND THEY FOUND WHY, WITH A NULL AND BOTH POSITIVE CONTROLS:** over 6,000 random verb pairs,
`path_similarity` does not predict valence agreement at all -- Spearman `-0.0023` against a shuffled
null p95 of `0.0231`, banded means flat at `1.406 / 1.387 / 1.410` against an all-pairs `1.393`.
**Positive controls pass**, which is what makes the null mean something: antonym pairs `2.031`
(larger, as required), same-synset pairs `1.063` (smaller, as required).

**Stage B votes by exactly that distance, and Stage B is `307` of `326` commits -- `94%` of what the
organ says comes from an axis measured to carry none of the thing it is voting about.**

---

## 2. MY RESULT LOOKED CONTRADICTORY. IT SURVIVED ITS BASELINE.

I had reported *"neighbourhoods are moderately valence-coherent -- median purity of the 5 nearest
anchors is `0.800` against a `0.5` coin flip."* Their null says similarity carries no valence. One of
us should be measuring an artifact.

**The obvious way mine could be wrong is anchor imbalance -- and it is not that:**

| purity of 5 anchors, n=400 verbs | |
|---|---|
| NEAREST 5 (what I reported) | **`0.800`** |
| 🔑 **RANDOM 5 -- the baseline I never computed** | **`0.600`** |
| FARTHEST 5 (negative control) | `0.600` |

*The anchor set is `26` POS / `26` NEG -- perfectly balanced -- so `0.600` is simply what five draws
from a balanced set look like.* **Nearest beats random by `+0.200`, and farthest sits at the
baseline. My result stands.** ⚠️ *But note the `0.5` I originally compared against was wrong: the
right baseline is `0.600`, and I never ran it. That is the measure-the-baseline rule, and it would
have cost one line.*

---

## 3. THE SYNTHESIS -- MEASURED, NOT A TRUCE

**BOTH HOLD IF THE 52 SEEDS ARE THEMSELVES CLUSTERED BY POLARITY IN WORDNET SPACE.** Then a target
landing beside one cluster sees coherent neighbours, even though similarity carries no valence in
general. That is a testable claim:

| anchor-to-anchor `path_similarity` | n | mean |
|---|---|---|
| SAME polarity | 650 | `0.2438` |
| DIFFERENT polarity | 676 | `0.2206` |
| **difference** | | **`+0.0232`** |
| permutation null on the labels, 2,000 shuffles | | `[-0.0076, +0.0087]` |

✅ **OUTSIDE THE NULL. THE SEEDS ARE CLUSTERED.**

> ### 🔑 **SO WHAT STAGE B ACTUALLY DOES IS READ *WHICH HAND-LABELLED CLUSTER THE TARGET LANDED BESIDE*, NOT VALENCE OFF THE GRAPH.**
> **The organ's competence is inherited from where 52 seeds happen to sit.** That is a far narrower
> claim than "anchored valence propagates outward", and it PREDICTS the thin global gradient they
> measured -- accuracy sliding smoothly `0.6597 -> 0.5773` from `12%` to `94%` coverage, present
> weakly everywhere rather than strongly nearby.

---

## 4. WHAT THIS CHANGES FOR THE DIRECTION QUESTION (`Q116`)

I recommended committing to **supplied knowledge plus reasoning outward**. This sharpens it, and not
entirely in my favour:

- ✅ **THE SUPPLY HALF IS REINFORCED.** Scrambling the seeds collapses the organ to chance; the seeds
  are doing the work, and they are doing it through their own placement.
- 🔻 **THE REASONING-OUTWARD HALF IS WEAKER THAN I PRESENTED IT.** `94%` of the organ's output rides
  an axis with no measured valence content. What looked like propagation is largely proximity to a
  hand-placed cluster.

**That is worth knowing before anyone builds more propagation machinery on this axis.** *The
valence-bearing relation is ANTONYMY -- Stage A reads `0.8421` on the `19` items it fires for.
Narrow, and pointed at the right thing.*

---

## TLDR

Another session was working the same component and got further than I did. Two of my statements to
you were wrong and I am correcting them.

I said the component's problem is that it rarely answers. It isn't. When it stays silent, it is
almost never because it has nothing to work with — it is because the evidence it finds points both
ways. Different problem, different repair.

They also found why: the component decides good-versus-bad by asking which words sit near each other
in a dictionary-like map, and near-ness in that map **carries no information about good versus bad
at all**. They proved it properly, including checks that their instrument could detect the thing when
it was genuinely there. Nearly everything the component says rides on that uninformative signal.

My own earlier finding looked like it contradicted theirs. It didn't — I checked, and both are true.
The reason is neat: our fifty-odd hand-labelled starting words happen to sit in clumps on that map.
So a new word landing near a clump gets a consistent answer, not because the map knows about good and
bad, but because we put the labels there. **The component is reading our own hand-placement back to
us.**

For the direction question I put to you: this strengthens the case that supplied knowledge is what
works, and weakens my claim that reasoning outward from it works. Worth knowing before we build more
on that particular axis.

## QUESTIONS

`Q115` and `Q116` remain open. This note is evidence for `Q116` and it cuts partly against my own
recommendation there.

## NEXT STEPS

1. **Antonymy is the valence-bearing relation** (`0.8421` on 19 items). Narrow but pointed the right
   way -- that is where propagation machinery belongs, not on taxonomic distance.
2. **Do not move the confidence gate.** Coverage bought by lowering a threshold is not a finding, and
   the consumer discards low-confidence hits anyway.
3. **Two sessions on one organ produced a better answer than either alone** -- but only because the
   commits collided visibly. Worth noticing that the coordination was luck.
