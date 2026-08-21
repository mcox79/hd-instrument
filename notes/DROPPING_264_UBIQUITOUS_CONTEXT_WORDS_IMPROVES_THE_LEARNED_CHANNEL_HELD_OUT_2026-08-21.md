# **DROPPING THE ~264 CONTEXT WORDS THAT APPEAR IN MORE THAN A FIFTH OF WORD-PROFILES RAISES THE LEARNED MEANING CHANNEL FROM `0.1071` TO `0.1558`. HELD-OUT GAIN `+0.0433`, CI `[+0.0002, +0.0994]`. THE FIRST THING TONIGHT THAT MAKES THE SUBSTRATE BETTER RATHER THAN EXPLAINING WHY IT IS NOT.**

**The counting result showed one standard weighting (idf) takes counting from below us to above us.
This asks whether the substrate can have the same thing. It can, partly.**

> **CONFIG: `GRADED_COMPARATOR=True`, passed EXPLICITLY. 28 corpora round-robin, 41 sentences per
> word, 829 SimLex pairs, `d=1024`.**

---

## 1. THE SWEEP

*Drop context words whose document frequency across the 854 word-profiles exceeds a cutoff. **Same
encoder, unchanged** -- only the word list handed to it is filtered, which is exactly what
`context_vector_masked` already does for the target word.*

| df cutoff | context words kept | rho | null p95 |
|---|---|---|---|
| **none** | 22,544 | **0.1071** | 0.0577 |
| >50% | 22,504 | 0.1154 | 0.0696 |
| >30% | 22,421 | 0.1291 | 0.0604 |
| **>20%** | 22,280 | **0.1558** | 0.0672 |
| >10% | 21,851 | 0.0988 | 0.0743 |

**An inverted U -- over-dropping hurts -- and the peak drops only `264` of `22,544` context words,
about 1%.** *The ones removed are `make, other, more, about, see, like, come, take`.*

## 2. ✅ **HELD OUT, BECAUSE A SWEPT MAXIMUM IS A FITTED NUMBER**

***I chose `>20%` by looking at the same pairs I scored it on. That is selection on the test set and
the `+0.0487` above is optimistic by construction.***

**So: pick the cutoff on one random half of the pairs, score it on the other half, 200 splits.**

| | |
|---|---|
| in-sample (fitted) gain | +0.0487 |
| **HELD-OUT gain** | **+0.0433, 95% CI `[+0.0002, +0.0994]`** |
| CI excludes zero | **yes -- but the lower bound is `0.0002`. Marginal, not comfortable.** |
| cutoff chosen | `>20%` in **184 of 200** splits |

**The small shrinkage (`0.0487 -> 0.0433`) and the stable choice are what make this credible.**

## 3. 🎯 WHERE IT LEAVES US AGAINST THE REAL FLOOR

| | rho |
|---|---|
| counting, raw | 0.0885 |
| ours, unchanged | 0.1071 |
| **ours + drop-ubiquitous** | **0.1558** |
| **counting + idf (the floor to beat)** | **0.1835** |

***It closes about 57% of the gap to idf-counting and does not clear it.*** **We are still behind the
rival, by less.**

## 4. 🧠 AND IT IS THE BRAIN'S OWN OPERATION, NOT A TRICK

**A stimulus that occurs everywhere carries little information, and the brain responds to it less --
repetition suppression and predictive coding are the same idea in neural form.** *Our accumulation
gave every context word equal weight regardless of how predictable it was. `idf` is that idea in
information-retrieval clothing; this is its hard form.*

## 5. ⚠️ LIMITS

1. **The CI's lower bound is `0.0002`.** *Real at this n, and only just.*
2. **A HARD DROP, not a graded weight.** *Proper idf weighting is the obvious next form and is
   untested -- the encoder is NOT linear (`cos 0.729` for `cv(a)+cv(b)` vs `cv("a b")`), so a
   weighted sum is a DIFFERENT encoder and needs its own justification.*
3. **Meaning only.** *Not tested on identification or on the live recall task.*
4. **Still below the floor.** `0.1558` vs `0.1835`.

## TLDR

Earlier I found that plain word-counting, plus one standard adjustment, beats our system. **The
adjustment is simply to ignore words that turn up everywhere.** So I asked whether our system can
have the same thing.

**It can.** Removing the roughly two hundred and sixty context words that appear in more than a fifth
of all word-profiles — words like *make, other, more, about, see* — **improves our meaning score by
about 45%**, from 0.107 to 0.156.

**I checked it properly.** Picking that threshold by looking at the results would have flattered it,
so I chose the threshold on half the word-pairs and scored it on the other half, two hundred times.
**The gain survives, at a bit under the headline figure, and the same threshold wins in 184 of 200
splits.** The margin is real but slim.

**This is the first change tonight that makes the system better rather than explaining why it isn't.**
It closes a bit over half the gap to the rival — **it does not close it.**

**And it is not a trick borrowed from search engines.** The brain does this: something you encounter
constantly stops producing much response. Our system was treating every surrounding word as equally
informative, which nothing in biology does.

## QUESTIONS

None.

## NEXT STEPS

1. **The graded form is the obvious next test** -- *a proper weight rather than a hard drop.* ⚠️ *The
   encoder is NOT linear, so a weighted sum is a different encoder and must be justified, not assumed.*
2. **Re-run identification with the same filter** -- *it may help or hurt there; untested.*
3. *Method note: **the in-sample number was `+0.0487` and the honest one is `+0.0433`.** The gap is
   small only because the chosen cutoff was stable; with a jumpy optimum it would have been the whole
   effect.*
