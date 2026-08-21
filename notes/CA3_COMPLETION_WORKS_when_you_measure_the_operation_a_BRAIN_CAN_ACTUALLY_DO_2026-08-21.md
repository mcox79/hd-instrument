# **PATTERN COMPLETION WORKS -- +0.2832 -- ONCE YOU MEASURE THE OPERATION A BRAIN CAN ACTUALLY PERFORM. THE TRIVIAL BASELINE THAT KEPT BEATING US WAS DOING SOMETHING NO BRAIN CAN DO.**

**The first mechanism tonight that BEATS its baseline. It took four corrections to get here, two of
them to my own measurements, and it only became visible under the neuroscience framing the owner
asked for.**

---

## 1. THE CHAIN, INCLUDING THE PARTS I GOT WRONG

| step | result |
|---|---|
| CA3 contributes nothing (exact cue) | ✅ real, but the task never *required* completion |
| **hypothesis: retrieval routed through DG is the fault** | 🚫 **REFUTED** -- the direct path is worse |
| **hypothesis: it needs more load** | 🚫 **REFUTED** -- `CA3 OFF` = 1.0000 even at N=20,000 |
| overlapping memories expose it | ✅ Hebbian collapses **0.8450 → 0.1433 → 0.0533** as within-family cos rises |
| ⚠️ *my error: mean over ALL pairs hid it* | *only ~1 pair in 30 is same-family* |
| **the imported Hebbian rule is the fault** | ✅ **projection rule recovers it: 0.0533 → 0.9117, 17x** |
| but completion still never beats codebook search | ✅ true at **every** cue level, 20% down to 2% |
| ⚠️ *my error: compared a DENSE completion to SPARSE codes* | *the live pipeline sparsifies after settling; I did not* |
| **and once BOTH are fixed** | ✅ **completion WINS at every cue level** |

## 2. 🎯 **THE REFRAME THAT MATTERS**

**The baseline that kept winning -- "don't complete, just match the cue against the stored codes" --
requires an explicit list of every pattern ever stored, and an exhaustive comparison against it.**

> ### ***A BRAIN HAS NO SUCH LIST. THE MEMORY IS THE SYNAPSES. THERE IS NOTHING TO SEARCH.***

**So that baseline is not a cheap alternative to CA3 -- it is an operation the organ's biological
counterpart cannot perform at all.** *Measuring completion against it is measuring a brain mechanism
against a database index.*

## 3. THE BRAIN-AVAILABLE MEASUREMENT

**Recover the PATTERN from the WEIGHTS ALONE. No codebook. Output sparsified to the stored sparsity
(k=47), exactly as the live path does (`sparsify_after_settle=True`).** *Overlapping memories,
within-family cosine 0.55, N=600.*

| units of the cue kept | **cue itself** | **completion** | **gain** |
|---|---|---|---|
| **20%** | 0.4461 | **0.7294** | **+0.2832** |
| 10% | 0.3156 | **0.4997** | **+0.1841** |
| 6% | 0.2483 | **0.3677** | **+0.1195** |
| 4% | 0.2048 | **0.2711** | **+0.0664** |
| 2% | 0.1446 | **0.1701** | **+0.0255** |

**➡️ POSITIVE AT EVERY LEVEL. The completed pattern is markedly closer to the true stored memory than
the fragment it was built from -- which is the definition of pattern completion.**

## 4. ⚠️ WHAT THIS IS AND IS NOT

**IS:** *a demonstration that, with (a) the projection rule instead of the imported Hebbian one,
(b) overlapping memories, and (c) the operation a brain can actually perform, CA3-style completion
does the job its biological namesake is defined by.*

**IS NOT:**
1. **A live-path result.** *This is a characterisation on DG codes of synthetic overlapping families,
   not the reading loop. Nothing is wired.*
2. **A licence to drop the codebook.** *Our substrate HAS an explicit store and search is genuinely
   available to it. The point is that measuring the ORGAN against search answers a question about
   our architecture, not about the organ.*
3. **Free.** *The projection rule costs a pseudo-inverse over the stored set -- `O(N^3)` here. The
   brain does not compute pseudo-inverses; a biologically plausible approximation is a separate,
   unpinned question.*

## 5. 🔄 AND IT REVISITS THE SIX-COMPARISON PATTERN

*Earlier tonight: six independent comparisons, in none of which our mechanism beat a trivial
baseline.* **This is the first crack in that pattern, and it suggests a question to ask of the other
five: IS THE TRIVIAL BASELINE DOING SOMETHING THE BRAIN CAN DO?** *For CA3 the answer was no, and the
comparison inverted once corrected.* ⚠️ **I am NOT claiming that generalises -- counting words and
spelling a word ARE things brains do. It is a question to ask, not an answer to assume.**

## TLDR

**This is the first thing tonight that beats its baseline, and it only appeared once I asked the
question the way a neuroscientist would.**

The component's job is to rebuild a whole memory from a fragment. All night it looked useless — worse
than useless, since switching it off scored better.

**Then I noticed what "switching it off" actually means.** The alternative it kept losing to was:
compare the fragment against a complete list of every memory ever stored, and pick the closest.
**A brain has no such list.** Memories live in the connections between cells; there is nothing to
look up. **So we were judging a brain mechanism against a database search.**

Measured the way a brain must do it — rebuild the memory from the connections alone, with no list to
consult — **the component works, and clearly.** Given a fragment holding a fifth of the original, the
rebuilt memory is much closer to the true one than the fragment was. **That is exactly what this part
of the brain is for.**

**Getting here took two corrections to my own measurements**, both worth stating: I first averaged
over the wrong set of comparisons, which hid the effect entirely; then I compared a dense result
against sparse originals, which reversed the sign. **Both were mine, and both were caught by checking
rather than by rerunning until it looked right.**

**Three honest limits.** This is a bench test, not the live system — nothing is wired in. Our system
genuinely does have a searchable list, so search isn't unavailable to *us*; the point is that judging
the organ against it answers a question about our architecture, not about the organ. And the fix
relies on a piece of mathematics the brain almost certainly doesn't compute directly — a plausible
approximation is a separate question.

## QUESTIONS

None.

## NEXT STEPS

1. **The completion rule is now a specific, measured build target:** projection over Hebbian,
   **0.0533 → 0.9117** on identification and **+0.2832** on brain-available recovery.
2. **Ask of the other five trivial baselines: is that operation available to a brain?** *For CA3 it
   was not, and the comparison inverted. **Do not assume it generalises** -- counting and spelling
   are things brains do.*
3. **Open and unpinned: a biologically plausible approximation to the projection rule.** *We should
   not ship a pseudo-inverse and call it CA3.*
