# **THE BIOLOGICALLY PLAUSIBLE LOCAL RULE BEATS BOTH THE INCUMBENT *AND* THE PSEUDO-INVERSE. AND THE METRIC I USED LAST TURN WAS GAMEABLE BY THE VERY FAILURE I WAS MEASURING.**

**Two results. The second is a correction to my own previous turn, and it is the more important one.**

---

## 1. 🔻 **FIRST, THE CORRECTION: RECOVERY-COSINE REWARDS MERGING**

**Last turn I reported completion working at `+0.2832` on "recovery" -- cosine between the completed
output and the true stored code. I called it the brain-available metric. It is gameable, and the
incumbent proves it:**

| rule | recovery-cosine to target |
|---|---|
| cue itself | 0.4652 |
| **one-shot Hebbian (the rule that MERGES)** | **0.7189 -- the HIGHEST of all four** |
| pseudo-inverse | 0.5731 |
| local delta | 0.6794 |

***The rule I had just proven merges correlated memories scores BEST on recovery.*** *Because a
merged attractor sits at the family's shared base, and with within-family overlap of 0.55 that base
is close to every member. Recovery-cosine cannot tell "reconstructed the memory" from "collapsed to
the average of its neighbours".*

**➡️ THE HONEST METRIC IS A MARGIN: similarity to the TARGET minus similarity to the nearest OTHER
MEMBER OF THE SAME FAMILY.** *Merging raises both terms and so cannot inflate the difference. And it
is brain-motivated: keeping similar episodes DISTINCT is precisely why DG separates in the first
place.*

## 2. ✅ **ON THE METRIC THAT CANNOT BE GAMED**

*d=256, dg=1024, N=400, 20 families, within-family overlap high, cue = 20% of units.*

| rule | to TARGET | to SIBLING | **MARGIN** | biologically local? |
|---|---|---|---|---|
| cue itself (no completion) | 0.4652 | 0.3930 | **+0.0723** | -- |
| **one-shot Hebbian (incumbent)** | 0.7189 | **0.8210** | **−0.1021** | yes |
| pseudo-inverse projection | 0.5731 | 0.4892 | **+0.0839** | 🚫 **no -- a global matrix inverse** |
| **LOCAL error-driven delta rule** | 0.6794 | 0.5818 | **+0.0975** | ✅ **YES** |

> ### **THE INCUMBENT'S MARGIN IS NEGATIVE. Its completed output is CLOSER TO A SIBLING THAN TO THE MEMORY IT WAS CUED WITH. That is merging, demonstrated on a metric merging cannot fake.**
>
> ### **AND THE BIOLOGICALLY PLAUSIBLE RULE IS THE BEST OF THE FOUR -- ahead of the cue (+0.0723) and ahead of the non-biological pseudo-inverse (+0.0839).**

## 3. 🧠 WHY THIS IS THE GOOD OUTCOME FOR FIDELITY

**The pseudo-inverse fixed the failure but is not something a brain computes** -- *it needs a global
inverse over every stored pattern at once.* **The delta rule reaches the same place by
ERROR-DRIVEN LOCAL UPDATES: each synapse changes by (what was stored − what was retrieved) × input.**
*That is the shape of error-driven plasticity, and it converges toward the projection rule without
ever forming an inverse.*

***So the fix does not require abandoning biological plausibility. It requires abandoning the
ONE-SHOT outer product -- and one-shot storage was never the pinned part; `ORGAN_MAP` records CA3's
core operation as UNPINNED and the Hopfield sign-update as OUR import.***

## 4. ⚠️ LIMITS, STATED

1. **Different scale from last turn** (dg=1024/N=400 here vs dg=2048/N=600 there), *so the numbers do
   not transfer between the two runs and I am not carrying them across.*
2. **200 epochs of iterative learning is not one-shot.** *The brain's hippocampus is prized for
   ONE-SHOT encoding. A rule needing 200 passes is a different animal, and whether a small number of
   replay passes suffices is UNMEASURED and is the obvious next question.*
3. **Bench characterisation on synthetic families. Nothing is wired.**

## TLDR

Two findings, and the second corrects me.

**Last turn I said the memory component works, scoring it by how close its output lands to the true
memory. That measure is fooled by the exact failure I was investigating.** The old, broken rule scores
**best** on it — because when it blurs similar memories together, the blur sits close to all of them.
**Being close to the right answer isn't the same as telling it apart from its neighbours.**

**The fair measure is the gap: how much closer the result lands to the intended memory than to its
most similar neighbour.** Blurring raises both, so it can't fake a gap.

**On that measure the old rule scores negative** — its output is closer to a *neighbour* than to the
memory it was asked for. That's blurring, proven.

**And the good news is genuinely good.** A biologically realistic rule — where each connection
adjusts by the difference between what was stored and what came back — **beats both the old rule and
the mathematically ideal one.** So fixing this doesn't mean abandoning brain plausibility; it means
abandoning storing everything in a single shot, which was never the part the science pinned down
anyway.

**Three limits.** This run used a different size from last turn's, so those numbers don't carry
across. The learning rule needed 200 passes, and the hippocampus is admired precisely for learning in
*one* — whether a handful of replay passes would do is untested and is the obvious next question. And
this is a bench test; nothing is connected to the live system.

## QUESTIONS

None.

## NEXT STEPS

1. **Use the MARGIN, not recovery-cosine.** *Recovery alone rewards the failure mode.*
2. **The open question is now sharp and brain-shaped: how FEW passes does the local rule need?**
   *One-shot encoding is the hippocampus's signature; 200 epochs is not it. Replay is the pinned
   biological mechanism for turning few exposures into many passes -- which is organ D4.*
3. *Neither number here transfers to last turn's run; different scale.*
