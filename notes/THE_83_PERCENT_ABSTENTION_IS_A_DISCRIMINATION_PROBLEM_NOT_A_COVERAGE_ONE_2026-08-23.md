# THE 83% ABSTENTION IS A DISCRIMINATION PROBLEM, NOT A COVERAGE ONE

**2026-08-23, strategy session.** I had twice written that the propagator's `17%` commit rate is
"the bigger limit than its accuracy", and once that it "blocks two separate questions". **I had
never split the number.** Splitting it changes what the repair is.

---

## 1. THE PARTITION NOBODY HAD RUN

Stage B abstains for two structurally different reasons, and they imply opposite work:

| | n (of 1,971 polar held-out verbs) | what it means |
|---|---|---|
| **COMMITTED** | `326` (`17%`) | -- |
| abstain -- **no anchor in range** (`n_neighbors == 0`) | `114` (**`6%`**) | a **REACH** limit; fix = more/better anchors |
| 🔻 abstain -- **neighbours vote and DISAGREE** | **`1,531` (`78%`)** | a **DISCRIMINATION** limit; a different fix entirely |

🔑 **SO "MORE ANCHORS" ADDRESSES `6` POINTS OF THE `83`.** The organ almost always HAS neighbours in
range. They just do not agree about valence.

⚠️ **AND THEY ARE NOT NEAR-MISSES.** The balanced-vote margins have **median `0.0276`** against a
`0.15` threshold, p90 `0.0909`. **The votes are close to perfectly balanced, not narrowly short.**
*Moving the threshold does not "recover" these; there is almost nothing there to recover, one item
at a time.*

---

## 2. THE ABSTENTION IS CONSERVATIVE, NOT PROTECTIVE

🚨 **THIS IS A CURVE, NOT A PROPOSAL. Lowering the gate buys coverage BY DEFINITION and that is not
a result** -- weakening a gate is explicitly not a finding here. The question the curve answers is
whether the signal **degrades gracefully** past where the organ stops, or **falls off**.

**Floor recomputed on each operating point's OWN committed subset**, because both class balance and
commit rate move with the threshold.

| `VOTE_MARGIN` | committed | coverage | organ | floor | margin | CI95 |
|---|---|---|---|---|---|---|
| `0.30` | 238 | `12.1%` | `0.6597` | `0.5630` | `+0.0966` | `[+0.0168, +0.1765]` |
| `0.20` | 269 | `13.6%` | `0.6691` | `0.5576` | `+0.1115` | `[+0.0297, +0.1933]` |
| **`0.15` (ships)** | **326** | **`16.5%`** | **`0.6595`** | **`0.5583`** | **`+0.1012`** | `[+0.0276, +0.1779]` |
| `0.10` | 444 | `22.5%` | `0.6486` | `0.5631` | `+0.0856` | `[+0.0248, +0.1532]` |
| `0.05` | 751 | `38.1%` | `0.6365` | `0.5273` | `+0.1092` | `[+0.0626, +0.1531]` |
| `0.01` | 1512 | `76.7%` | `0.5926` | `0.5099` | `+0.0827` | `[+0.0529, +0.1118]` |
| `0.00` | 1857 | `94.2%` | `0.5773` | `0.5213` | `+0.0560` | `[+0.0280, +0.0845]` |

✅ **THE MARGIN NEVER COLLAPSES. It excludes zero at EVERY operating point, from `12%` coverage to
`94%`.** Accuracy declines smoothly (`0.6597` -> `0.5773`) rather than falling off a cliff.

🧠 **SO THE MECHANISM CLAIM IS THIS, AND IT IS NOT WHAT I EXPECTED:** anchored valence does **not**
propagate strongly to a neighbourhood and stop. **It is present WEAKLY ACROSS ESSENTIALLY THE WHOLE
VERB SPACE.** A thin global gradient, not a sharp local one.

🚫 **WHAT THIS DOES NOT LICENSE: "lower the threshold".** At `17%` the organ is right `66` times in
`100`; at `94%` it is right `58`. Which you want depends on the consumer, and the consumer
(`pseudo_counts_from_dictionary`) currently discards low-confidence hits anyway. **The curve is
information about the mechanism, not a recommendation about a constant.**

---

## 3. A BIGGER ANCHOR BUYS REACH -- AND MOST OF THE HEADLINE GAIN IS THE FLOOR MOVING

| anchor | committed | no-reach | organ | floor | margin |
|---|---|---|---|---|---|
| `52` words (ships) | `326` (`17%`) | `114` | `0.6595` | `0.5583` | `+0.1012` |
| `84` words (extended) | `409` (`21%`) | **`71`** | `0.6773` | `0.5086` | `+0.1687` |

**Reach improves materially: unreachable items fall `114` -> `71`.**

⚠️ **BUT THE MARGIN NEARLY DOUBLING IS MOSTLY THE FLOOR FALLING, NOT THE ORGAN IMPROVING.** Accuracy
moves `+0.0178`; the floor moves `-0.0497`. **The bigger anchor commits on a more class-balanced
subset, which lowers the majority baseline.** *Reporting `+0.1012 -> +0.1687` as "the anchor nearly
doubles the margin" would be true and misleading; both numbers are correct and they are on different
committed populations.*

*Both arms exclude the full 84-word extended set from the TEST population, so neither is scored on
its own anchor.*

---

## 4. WHAT THIS ESTABLISHES

- ✅ The `83%` abstention is **`78` points discrimination, `6` points reach.** The framing "coverage
  is the real limit" was **mine and it was wrong** -- coverage is a symptom.
- ✅ The abstention is **conservative**: real signal exists past the gate, at every level tested.
- ✅ A larger anchor genuinely improves reach; its accuracy gain is small and its margin gain is
  mostly a floor artifact.
- 🚫 **NOT established:** that any threshold should change. No gate is being proposed.
- 🚫 **NOT established:** that this transfers to the loop's own OOV population, which is `33` lemmas
  and where the dictionary commits on `6`. *These are dictionary verbs; no number crosses.*
- 🚫 **NOT a landed cell** -- inline, `scratch/`, no `metrics.json`.

---

## TLDR

The system only ventures an opinion about one word in six, and I had twice called that a coverage
problem without ever asking *why* it stays silent.

There are two reasons it can stay silent, and they need opposite fixes: either no known word is
close enough to compare against, or known words are close but they **disagree**. I had assumed the
first. It is overwhelmingly the second — **78 of the 83 silent cases are disagreement, only 6 are
nothing-in-range.** So "give it more hand-labelled words" fixes a small corner of the problem.

I also checked what happens if it is made to answer anyway, everywhere. It does not fall apart — it
gets gradually worse but stays better than guessing, all the way out to answering 94 in 100 words.
**That says something specific about how this kind of grounding spreads: not strongly to nearby
words and then stopping, but weakly almost everywhere.**

This is deliberately not a proposal to make it answer more. Answering rarely, it is right about 66
times in 100; answering nearly always, 58. Which is better depends on who is using it.

One caution about a number that looks better than it is: doubling the hand-labelled set appears to
nearly double the advantage, but most of that is the comparison baseline shifting, not the system
improving.

## QUESTIONS

None.

## NEXT STEPS

1. **The real question is now discrimination, not coverage:** why do a verb's nearest neighbours in
   this relational structure disagree about valence? That is where the `78` points are.
2. Anything built on "more anchors" should be priced against the `6%` it can address.
3. Both calibration findings still need an evaluation where the dictionary commits broadly.
