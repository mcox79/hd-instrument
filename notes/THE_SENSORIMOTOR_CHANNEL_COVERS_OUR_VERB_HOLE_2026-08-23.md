# THE PROPOSED FIX DOES COVER OUR WORST HOLE -- AND THE BRIEF FOR IT NEVER MENTIONS VERBS

**2026-08-23, strategy session.** A measurement, not a build. Ran because the highest-ranked problem
in the project proposes replacing our meaning channel with the Lancaster sensorimotor norms, and
**its brief contains the word "verb" zero times** -- while the sharpest fact we have about our
current channel is that it reads **exactly `+0.0000` on verbs.**

We were about to commission a fix without checking whether it addresses the hole we actually have.

---

## 1. THE QUESTION, AND WHY IT IS A BRAIN QUESTION

Our learned channel is not uniformly weak. It is **weak on nouns and ABSENT on verbs**: `0.1310`
against a `0.0843` null on SimLex nouns, and `+0.0000` on SimVerb-3500's 2,651 pairs against a null
whose 95th percentile is `0.0372`.

So the question is not "is the sensorimotor asset better" -- that is already measured, pooled across
all parts of speech. The question is **does it carry the part of speech where we have nothing.**

**And the brain makes a sharper prediction than "it helps".** Action verbs are somatotopically
represented in motor cortex -- *kick* recruits leg regions, *pick* hand regions, *lick* mouth regions
(Hauk, Johnsrude & Pulvermuller 2004, and the wider embodied-semantics line). Object nouns lean on
perceptual cortex. **Lancaster splits its 11 dimensions along exactly that seam:** 6 PERCEPTUAL
(auditory, gustatory, haptic, interoceptive, olfactory, visual) and 5 ACTION (foot_leg, hand_arm,
head, mouth, torso). That predicts a DOUBLE DISSOCIATION, and a double dissociation can fail.

---

## 2. WHAT IT SAYS -- ONE SCORER, ONE POPULATION, ONLY WORD CLASS CHANGING

SimLex-999, **100% covered by the norms** (999 of 999 pairs; N=666, V=222, A=111). Plain cosine over
the raw norms -- **nothing fitted, no model, not our substrate.** Spearman against human similarity;
2,000-draw permutation null and 2,000-resample bootstrap CI per cell.

| dimensions | POS | n | rho [95% CI] | null p95 | verdict |
|---|---|---|---|---|---|
| **ALL 11** | **N** | 666 | **+0.3469** `[+0.2777,+0.4113]` | 0.0762 | **CLEARS** |
| **ALL 11** | **V** | 222 | **+0.3109** `[+0.1841,+0.4283]` | 0.1309 | **CLEARS** |
| ALL 11 | A | 111 | +0.2368 `[+0.0545,+0.4050]` | 0.1841 | INSIDE its null |
| PERCEPTUAL (6) | N | 666 | +0.2752 `[+0.2066,+0.3425]` | 0.0765 | CLEARS |
| 🔻 **PERCEPTUAL (6)** | **V** | 222 | +0.2651 `[+0.1331,+0.3854]` | 0.1338 | 🔻 **INSIDE its null** |
| ACTION (5) | N | 666 | +0.2607 `[+0.1881,+0.3276]` | 0.0745 | CLEARS |
| **ACTION (5)** | **V** | 222 | **+0.3038** `[+0.1762,+0.4127]` | 0.1333 | **CLEARS** |

**INFO-FREE CONTROL:** a constant vector reads **`+0.0000`** on verbs. The scorer discriminates.

---

## 3. THE ANSWER TO THE QUESTION THAT SENT ME HERE

✅ **THE SENSORIMOTOR CHANNEL DOES CARRY VERBS**, on both verb benchmarks, with the CI's LOWER bound
clearing the null's 95th percentile in each case -- gated on the floor's upper bound, which is the bar.

**COMPARED ON THE SAME BENCHMARK, WHICH IS THE ONLY WAY THIS IS SAYABLE.** Our own verb zero was
measured on SimVerb-3500, so that is where the comparison belongs:

| channel on **SimVerb-3500** | pairs it covers | rho | its null p95 |
|---|---|---|---|
| our learned channel | 2,651 of 3,500 | **`+0.0000`** | 0.0372 |
| the sensorimotor norms | **3,487 of 3,500** | **`+0.3107`** `[+0.2822,+0.3390]` | 0.0304 |

⚠️ **THE TWO ROWS DO NOT SHARE A POPULATION -- 2,651 vs 3,487 covered pairs -- so this is NOT a
subtraction and `+0.3107` is not "a gain of `0.31`".** What it licenses is the qualitative statement,
which is the one that matters here: **ours is ABSENT where this one is PRESENT, on the same
benchmark.** *The coverage gap points the same way: the norms reach 99.6% of the benchmark, our
vocabulary reaches 75.7%.*

The fix the top-ranked brief proposes addresses the exact hole we have, and **nobody had checked.**
That is the finding: it de-risks the build.

Note also that on SimLex -- one benchmark, one scorer, only word class changing -- verbs score
**only slightly below nouns** (`+0.3109` vs `+0.3469`), where our own channel collapses from *weak*
to *nothing* across that same boundary. **The verb hole is OURS, not the world's.**

---

## 4. THE SOMATOTOPY PREDICTION -- ABSENT AT n=222, AND IT HOLDS AT n=3,487

On SimLex alone the pattern fell exactly where the brain predicts (nouns: perceptual `+0.2752` vs
action `+0.2607`; verbs: action `+0.3038` vs perceptual `+0.2651`) and **the interaction test said
nothing**: verb(A−P) − noun(A−P) = `+0.0527` `[-0.0989,+0.2031]`. 222 verb pairs cannot carry it.

**So I powered it instead of reporting the direction.** SimVerb-3500, **3,487 of 3,500 pairs covered
(99.6%)**, same scorer, same controls:

| dimensions | n | rho [95% CI] | null p95 | verdict |
|---|---|---|---|---|
| **ALL 11** | 3,487 | **+0.3107** `[+0.2822,+0.3390]` | 0.0304 | **CLEARS** |
| **ACTION (5)** | 3,487 | **+0.2888** `[+0.2583,+0.3185]` | 0.0316 | **CLEARS** |
| PERCEPTUAL (6) | 3,487 | +0.2237 `[+0.1916,+0.2553]` | 0.0320 | CLEARS |

🧠 ✅ **ACTION − PERCEPTUAL ON VERBS = `+0.0651`, 95% CI `[+0.0306, +0.1005]` -- SEPARATED FROM
ZERO.** Paired bootstrap, same pairs both arms. **The motor dimensions carry verb meaning better
than the perceptual ones, and that survives at power.** This is Hauk/Johnsrude/Pulvermuller's
somatotopy showing up in an offline norm table, on our disk, on a benchmark chosen for verbs.

**AND IT REPLICATES ACROSS TWO INDEPENDENT VERB BENCHMARKS:** all-11 reads `+0.3109` on SimLex's 222
verbs and `+0.3107` on SimVerb's 3,487. *Different pair sets, different raters, agreeing to three
decimals.*

🔻 **WHAT IS STILL NOT ESTABLISHED, AND THE DISTINCTION MATTERS.** This is a **SINGLE dissociation,
not a double one.** On verbs, action beats perceptual, CI-separated. On NOUNS the same paired test
reads `-0.0150` `[-0.0951,+0.0635]` -- **includes zero**, so "perceptual carries nouns better" is
NOT shown. The claim that survives is: *within verbs, the motor dimensions do more work than the
perceptual ones.* **Do not retell that as "motor for verbs, perceptual for nouns."**

*Recorded because the first pass produced exactly the archive's most expensive error -- an
underpowered null that reads like a capability statement. The fix was not more caution in the
wording. It was 3,487 pairs instead of 222, from a file already on disk.*

---

## 5. WHAT MAY AND MAY NOT BE QUOTED

- ✅ **MAY: the sensorimotor channel clears its null on SimLex VERBS at `+0.3109`,** CI lower bound
  `+0.1841` vs null p95 `0.1309`, 222 pairs, plain cosine, nothing fitted.
- ✅ **MAY: our learned channel is `+0.0000` on verbs and this one is not.** Different benchmarks
  (SimVerb vs SimLex) — **so quote it as "ours is absent where this one is present", never as a
  subtraction.** No number crosses populations.
- ✅ **MAY: within VERBS, action dimensions beat perceptual ones by `+0.0651` `[+0.0306,+0.1005]`,**
  paired, 3,487 SimVerb pairs. **A SINGLE dissociation.**
- 🚫 **MAY NOT: "action dimensions carry verbs and perceptual dimensions carry nouns."** That is the
  DOUBLE dissociation and the noun half is `-0.0150` `[-0.0951,+0.0635]` — includes zero.
- 🚫 **MAY NOT:** anything about our substrate. This measures the ASSET'S ceiling, not our ability to
  reach it. `read()` still makes **zero** calls to the meaning asset.
- 🚫 **MAY NOT:** the adjective row. `n=111`, inside its null on every dimension set.

---

## TLDR

The top item on our problem list says: stop guessing word meanings from which words appear nearby,
and use a set of human ratings of how words feel to see, hear, touch and move instead. Good idea —
but that write-up never once mentions verbs, and verbs are exactly where our current method scores a
flat zero.

So I checked whether the replacement actually covers the gap. **It does.** On action words it scores
about `0.31` against human judgement where ours scores `0.00`, and that is comfortably clear of
chance. It is also almost as good on verbs as on nouns, whereas ours falls off a cliff between the
two — which says the verb problem is ours, not the world's.

I also tested the more interesting brain claim: that *movement* ratings should carry verbs, because
the brain stores action words in the parts that control movement. On the small test it could easily
have been chance — so rather than claim it, I re-ran it on a file already on our disk with about
fifteen times more word pairs. **It holds.** Movement ratings genuinely beat sensory ratings for
working out what a verb means. The same effect turns up in two completely separate sets of human
judgements, agreeing to three decimal places.

What I still cannot say is the mirror image — that sensory ratings are better for nouns. That half
did not separate, so the claim is one-directional and I have written it down that way.

## HOW TO CHECK THIS YOURSELF

```
.venv/Scripts/python.exe verification/test_sensorimotor_covers_the_verb_hole.py
```

**A TRACKED witness, not a scratch file** -- `scratch/` is gitignored, so citing it would have
pointed at something nobody else can open. It asserts the null-clearing, the action-over-perceptual
margin, and the information-free control, and **it does NOT assert the double dissociation**,
because that is not established.

## QUESTIONS

None. `Q116` remains open and this is evidence for it.

## NEXT STEPS

1. **Put this in the `reader_meaning_channel` brief** so whoever builds it knows the channel covers
   the verb hole — and knows the somatotopy split is not established.
2. ~~Power the dissociation on SimVerb-3500.~~ **DONE IN THIS PASS — 3,487 pairs, and it HOLDS**
   (§4). The remaining open half is the NOUN side of the double dissociation, which needs a
   noun-only benchmark bigger than SimLex's 666.
3. *Nothing here changes what our substrate can do. The adapter is still missing.*
