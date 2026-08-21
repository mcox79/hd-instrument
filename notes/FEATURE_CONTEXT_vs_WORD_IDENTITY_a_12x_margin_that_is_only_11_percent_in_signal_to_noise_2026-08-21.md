# **FEATURE-BASED CONTEXT GIVES A 12x LARGER MARGIN AND ONLY AN 11% BETTER SIGNAL-TO-NOISE RATIO. BOTH NUMBERS ARE TRUE AND THE SECOND IS THE ONE THAT MATTERS FOR THE CLAIM I ALMOST MADE.**

**`ORGAN_MAP` B1 STEP 3 names the fidelity gap qualitatively: *"the brain's hub pools SPOKE (feature)
inputs; ours pools co-occurring word identities."* Last turn I measured its consequence -- same-word
episodes are near-orthogonal (0.0056). This tests the map's own proposed fix.**

---

## 1. THE COMPARISON

*80 lemmas x 20 real sentences. Both arms use the SAME no-leak masking (the target lemma removed).
Feature arm = mean of the 12 human sensorimotor dimensions over the remaining content words.
Incumbent arm = the live `context_vector_masked` bag-of-word-identities, DG-coded.*

| representation | WITHIN-lemma | CROSS-lemma | **margin** | ratio |
|---|---|---|---|---|
| feature context, **raw** | 0.2516 | 0.2115 | +0.0401 | **1.19x** |
| **feature context, MEAN-CENTRED** | 0.0503 | 0.0019 | **+0.0484** | **26.16x** |
| feature context, centred + rank-1 removed | 0.0468 | 0.0006 | +0.0462 | 76.64x |
| **incumbent (word identity, DG-coded)** | 0.0056 | 0.0015 | **+0.0041** | 3.73x |

**⚠️ THE RAW FEATURE ARM IS THE TRAP: its 0.2516 looks impressive and its RATIO IS THE WORST OF ALL
(1.19x).** *A 12-dimensional cosine has a random level around 0.29, so 0.2115 cross-lemma is close to
chance for that space. Absolute similarity in a low-dimensional space is not evidence of anything;
centring is what makes it readable.*

## 2. 🔻 **THE OVER-CLAIM I ALMOST MADE, AND THE CONTROL THAT STOPPED IT**

**A margin of +0.0484 against +0.0041 is 12x. I was about to report that.**

**Shuffled-label control, 20 permutations each:**

| | margin | shuffled mean | shuffled sd | **z** |
|---|---|---|---|---|
| feature context (centred) | +0.0484 | +0.0007 | **0.0032** | **14.8 sd** |
| incumbent | +0.0041 | −0.0000 | **0.0003** | **13.3 sd** |

> ### **THE NOISE SCALES WITH THE MARGIN. IN UNITS OF ITS OWN NULL, THE FEATURE REPRESENTATION IS 11% BETTER, NOT 1,100% BETTER.**
>
> ***STANDING DISCIPLINE 14: A WIDTH IS NOT AN EFFECT. I had the width and was about to call it the
> effect.***

**✅ AND BOTH CONTROLS FIRE PROPERLY** -- shuffled margins are +0.0007 and −0.0000 against real
margins of +0.0484 and +0.0041. ***Both representations carry GENUINE same-word signal; the
incumbent's is real too, just small.***

## 3. ✅ **WHERE THE 12x DOES MATTER: ABSOLUTE OVERLAP, FOR THE COMPLETION QUESTION**

**For signal detection, z is the right measure and the two are comparable. For pattern completion,
ABSOLUTE overlap is the right measure, because completion needs stored patterns that actually
resemble each other.**

| | same-word overlap | vs the 0.22 threshold where completion earns its place |
|---|---|---|
| incumbent | 0.0056 | **40x below** |
| **feature context, centred** | **0.0503** | **4x below** |

***Features get 9x closer to the regime where the episodic machinery would have work to do -- and
still do not reach it.*** **So this does not rescue CA3 either; it moves the number in the right
direction by an order of magnitude and stops short.**

## TLDR

Our reference document names a specific flaw: the brain builds a word's context from **what things
are like** — their feel, sound, how you act on them — while ours builds it from **which other words
happened to be nearby**. Last turn I measured the damage: our system barely registers two encounters
with the same word as related.

**This tests the fix. It helps, but far less than the headline suggests.**

Building context from human ratings of sensory and motor properties makes two encounters with the
same word **nine times more alike** than our current method does. That's real, and it survived the
check where I scrambled which sentence belongs to which word — the effect vanished, as it should.

**But I nearly reported it as a twelve-fold improvement, and that would have been wrong.** The new
measure is also twelve times noisier. Judged against its own random baseline — the fair comparison —
**it's about 11% better, not 1,100%.** Our own rules warn about exactly this, and I had the mistake
in hand before the control caught it.

**One trap worth flagging.** The raw feature version looks best of all on a first glance, scoring 0.25
where the others score near zero. **It's the worst of the lot** — in a twelve-dimensional space
everything scores about that by chance. Removing the average made it readable.

**Where the improvement genuinely counts:** for rebuilding memories from fragments, what matters is
whether stored memories actually resemble each other. Ours overlap at 0.006; the feature version at
0.05; the level where the machinery would earn its keep is 0.22. **So it closes most of an order of
magnitude and still falls four times short.**

## QUESTIONS

None.

## NEXT STEPS

1. **Quote the z, not the margin: 11%, not 12x.** *Both are true; only one answers "is this better".*
2. **Feature context is genuinely better in absolute overlap (0.0503 vs 0.0056) and still 4x short of
   the completion regime.** *It does not rescue CA3.*
3. **Mean-centring is doing most of the work** (ratio 1.19x → 26.16x). *Rank-1 removal adds ratio but
   costs margin -- consistent with DO-NOT-REDO 27, "the operation WORKED and the task did not care".*
