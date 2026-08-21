# **HIGHER SAME-WORD OVERLAP DID *NOT* MEAN A BETTER TASK SCORE. THE 12-DIM FEATURE CONTEXT IS WORSE AT EVERY LOAD AND, WORSE, IT DOES NOT ACCUMULATE. AND NORMS12's OWN NOTE PREDICTED THIS.**

**I have spent three turns measuring REPRESENTATIONAL properties -- overlap, margin, ratio -- and
treating them as proxies for usefulness. This runs the actual task. They disagree, and the
representational metric was the misleading one.**

---

## 1. THE TASK RESULT

*Anchor self-identification: build a lemma's anchor from L of its context vectors, probe with a
HELD-OUT context vector of the same lemma, hit@1 over 80 anchors. Chance 0.0125. Both arms use the
same lemmas, the same sentences, the same no-leak masking, the same 8 held-out probes.*

| traces in anchor | 1 | 4 | 8 | 16 | 24 | **37** |
|---|---|---|---|---|---|---|
| **INCUMBENT (word identity)** | 0.0312 | 0.0516 | 0.0719 | 0.0984 | 0.1219 | **0.1328** |
| **FEATURE (12 dims, centred)** | 0.0250 | 0.0203 | 0.0234 | 0.0250 | 0.0266 | **0.0266** |
| delta | −0.0062 | −0.0312 | −0.0484 | −0.0734 | −0.0953 | **−0.1062** |

> ### **WORSE AT EVERY LOAD -- AND IT IS FLAT. The incumbent climbs 4.3x from L=1 to L=37; the feature arm sits at ~2x chance and DOES NOT MOVE.**
>
> ***Accumulating more encounters buys the feature representation NOTHING. That is the more damning
> half: it is not merely weaker, it does not learn.***

## 2. 🔻 **THE PROXY I WAS TRUSTING WAS WRONG**

**Last turn I measured feature context as having 9x the same-word overlap of the incumbent
(0.0503 vs 0.0056) and read that as the better representation.** *On the task it is 5x WORSE at the
operating point.*

***OVERLAP IS NOT DISCRIMINABILITY. Two encounters can be more similar to each other AND less
distinguishable from every other word -- which is exactly what 12 shared dimensions produce: a coarse
"what kind of scene is this" signal, not a word-specific one.***

**FOURTH INSTANCE TONIGHT of measuring the wrong quantity:** *a real number in the wrong context
(B1); a real curve for the wrong operation (the 0.79 threshold); a real flaw in a regime we never
enter (CA3); and now a real representational gain that does not survive contact with the task.*

## 3. ✅ **AND THE ARCHIVE ALREADY SAID SO -- A CONSTRAINT CHECK THAT PASSES**

**`THE_BEST_SEMANTIC_ASSET_...` (the NORMS12 note) scoped itself, in its own words:**

> *"AS A FEATURE SPACE IT WOULD RESOLVE ~60% OF RUNNING TOKENS AND BE SILENT ON THE REST. Usable, and
> exactly what the module already calls itself -- a **FALLBACK**. **"Highest-value cheap move" stands;
> "a graded feature space for everything" does not.**"*

***That is precisely the claim my task measurement refutes, and the note refused to make it. The
scoping was right and I re-derived it the expensive way.*** **This is the second time tonight that
the note carrying its own limit turned out to be the trustworthy one.**

## 4. ⚠️ WHAT IS AND IS NOT REFUTED

| | |
|---|---|
| **12 averaged human dimensions as a general context representation** | 🚫 **REFUTED on this task -- worse everywhere and flat** |
| `ORGAN_MAP` B1's gap ("the brain pools SPOKE inputs; ours pools word identities") | ✅ **UNTOUCHED.** *The brain's spokes are many and high-dimensional; 12 human-rated dims are a tiny proxy for them, and their failure is not the proposal's failure.* |
| NORMS12 as a **fallback** for words the lexicon misses | ✅ **untouched -- that is what its own note claims and all it claims** |
| the measured encoding gap (same-word codes at 0.0056) | ✅ **stands -- still the real problem, still unsolved** |

## TLDR

For three turns I measured how *similar* two encounters with the same word look inside the system, and
treated that as a stand-in for how *useful* the representation is. **This turn I ran the actual job.
They disagree, and the similarity measure was the misleading one.**

Building context from human sensory ratings makes two encounters with the same word much more alike —
I measured that last turn and it was real. **But on the actual task of recognising which word a new
encounter belongs to, it is five times worse.**

**And the damning part isn't that it's worse — it's that it's flat.** Our current method gets steadily
better as it sees a word more often, improving four-fold from one encounter to thirty-seven. **The
feature version doesn't improve at all.** It sits just above guessing no matter how much it sees.
**It doesn't learn.**

**The reason is simple in hindsight:** twelve dimensions describing how things feel and sound give a
rough sense of *what kind of situation this is* — not *which word this is*. Two encounters can be
more alike **and** less distinguishable from everything else.

**And our own archive already said this.** The note introducing those human ratings explicitly refused
the claim I was drifting toward, calling it a **fallback** and stating that "a graded feature space
for everything" does not hold. **It was right, and I spent three turns re-deriving it the expensive
way.** That's the second time tonight the note that stated its own limits turned out to be the
trustworthy one.

**What this does not touch:** the underlying criticism — that the brain builds context from properties
while we use nearby words — stands. The brain's version of those properties is vast and detailed;
twelve human-rated numbers are a thin proxy, and their failure isn't the idea's failure.

## QUESTIONS

None.

## NEXT STEPS

1. **Stop using overlap as a proxy for usefulness.** *Run the task; it disagreed here and the task was
   right.*
2. **The encoding gap is unchanged and still the real problem** -- same-word codes at 0.0056, and the
   cheap fix does not close it.
3. **Trust the note that states its own limits.** *Second time tonight: NORMS12 scoped itself
   correctly and I re-derived the scoping at three turns' cost.*
