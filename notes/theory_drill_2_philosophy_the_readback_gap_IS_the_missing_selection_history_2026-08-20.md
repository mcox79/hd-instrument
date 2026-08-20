# THEORY DRILL 2 (philosophy): OUR MEASURED FAILURE SIGNATURE IS THE **PREDICTED** ONE -- AND THE READ-BACK GAP IS NOT A MISSING FEATURE, IT IS THE REASON GROUNDING CANNOT ARISE

**Owner, answering Q89: *"drill relevant theory... learning research, linguistic research, even
philosophy."*** The first drill covered learning and linguistics. **This is the philosophy half, and
it is the more consequential of the two.**

---

## 1. 🎯 **OUR THREE-BUCKET RUBRIC IS THE DISTRIBUTIONAL-SEMANTICS LIMIT, RESTATED**

The standard characterisation of what co-occurrence statistics can and cannot deliver:

> **"Similar distributional patterns can identify that two words have SIMILAR MEANINGS, but not
> WHAT those meanings are."**

**THAT IS OUR MEASURED SIGNATURE, EXACTLY.** Every hand-score tonight has the same shape:

| | RELATED | MEANINGFUL |
|---|---|---|
| distributional read-out (structured-comparator control) | 24% | **0%** |
| NEWS / TEXTBOOK streams | 24% / 36% | **0% / 0%** |
| paired live test | -- | **4%** |

**High RELATED, near-zero MEANINGFUL, over and over.** Our rubric's buckets map onto the theory's
distinction without anyone having designed them to: **RELATED is distributional similarity being
captured successfully; MEANINGFUL is grounding, which the literature says co-occurrence cannot
supply in principle.**

**➡️ SO THE 0-4% IS NOT A TUNING FAILURE OR A BUG. IT IS THE PREDICTED CEILING OF THE MECHANISM.**
*This does not excuse the numbers -- it explains them, and it means no amount of cleverness applied
to the co-occurrence signal will move the MEANINGFUL column. Thirteen closed interventions already
said this empirically; the theory says why.*

## 2. 🔑 **THE PHILOSOPHY NAMES THE MISSING INGREDIENT, AND IT IS NOT SENSORY DATA**

**Harnad 1990 (the Symbol Grounding Problem)**: symbols defined only in terms of other symbols give
definitional circularity or infinite regress; grounding must come bottom-up from **non-symbolic**
representations -- iconic (sensory) and categorial (invariant feature detectors). *That reading
supports the perceptual-norms direction.*

**BUT Mollo & Millière 2023 (The Vector Grounding Problem) SHARPEN IT AND POINT SOMEWHERE ELSE.**
They separate **five** notions of grounding that are habitually conflated and argue only
**REFERENTIAL grounding** matters -- the connection between a representation and its worldly
referent. Their conditions, from teleosemantics, are that a system's internal states must:

1. **stand in appropriate causal-informational relations to the world**, and
2. **have A HISTORY OF SELECTION that has endowed them with the FUNCTION of carrying that
   information.**

**And they argue this is achievable WITHOUT multimodality or embodiment** -- what supplies the
selection history in their case is training feedback.

## 3. ⚡ **AND THIS IS WHERE IT MEETS TONIGHT'S MEASUREMENT: WE HAVE NO SELECTION HISTORY, AND I MEASURED THE REASON**

**Our substrate satisfies neither condition, and the second failure is structural.**

Nothing in this system has ever selected a representation for **successfully carrying information**.
There is no process by which a meaning that misrepresents gets corrected, because -- **measured
tonight, enumerated across all four read routes** --

> **NOTHING READS THE MEANINGS.** `build_cortical_index` builds its rows from accumulated context
> profiles; the meaning VALUE is never vectorised, never compared, never read. `query`'s decision
> keys on whether a meaning EXISTS, not on what it says. Every read of a banked meaning's content in
> `hdlab/` is a self-test assertion.

**➡️ THE READ-BACK GAP IS NOT A MISSING FEATURE. IT IS THE ABSENCE OF THE SELECTION LOOP THAT
REFERENTIAL GROUNDING REQUIRES.** Nothing consumes the meanings -> nothing can be right or wrong
because of them -> **no selection pressure can ever act on them** -> the representations cannot
acquire the function of carrying information about the world. **A system whose outputs are never
used cannot ground them, on this account, no matter how much it reads.**

*I measured the gap empirically hours before finding the theory that says it is the crux. The two
arrived independently and agree.*

## 4. ⚖️ THE TENSION IN THE LITERATURE IS REAL AND SHOULD NOT BE COLLAPSED

**Harnad's route** -- add non-symbolic sensory grounding -> **supports the perceptual-norms branch
the owner endorsed.** *Note our one attempt on that route did NOT clear its floor:
`exp_sensorimotor_channel_discrimination_v1`, best arm AUC 0.6039 CI [0.5439, 0.6644] against a
0.6791 credible bar from the CONSTANT-PROTOTYPE floor -- **margin -0.0752.** Memory records that as
a narrow-instrument failure later improved on a better-posed problem, so it is not a closed route --
but it is not a demonstrated one either.*

**Mollo & Millière's route** -- build the causal-informational link and the **selection history**;
multimodality NOT required -> **supports building a consumer + feedback loop**, i.e. closing the
read-back gap so that banked meanings can be selected for.

**These are live, competing positions. I am not qualified to adjudicate them and will not pretend
to.** What is useful is that **both diagnose our system as ungrounded for reasons we have
independently measured**, and they disagree about the remedy.

## TLDR

The owner told me to read the philosophy too. It turned out to explain the thing I spent all night
measuring.

**First: our results have exactly the shape the theory predicts.** Statistics about which words
appear near each other can tell you two words are *related* — but not what either one *means*. Every
score tonight came out that way: plenty of "related", almost no "actually explains the word". **That
is not our system being broken. It is the known ceiling of the method.**

**Second, and more useful: the philosophy names what is missing, and it is not what I expected.** One
influential answer says you need sensory experience — pictures, touch, the physical world. But a more
recent argument says the crucial ingredient is different: a representation only comes to *mean*
something if there has been **a history of it being selected for getting things right**. Something has
to use it, succeed or fail, and push back.

**Our system has nothing of the kind — and I measured exactly why tonight, before finding this
argument.** Nothing in it ever reads the meanings it writes down. They are stored and never
consulted. So nothing can go wrong because of a bad meaning, so nothing can ever correct one.

**That reframes the gap I found.** I had called it a missing feature — a piece nobody built yet. On
this account it is the reason the whole approach cannot get off the ground: **a system whose answers
are never used cannot learn what they mean, however much it reads.**

The two camps disagree on the fix — add senses, or add consequences — and I am not qualified to
settle that. Worth knowing that both say we are ungrounded for reasons we had already measured.

## QUESTIONS

None. This is context for the direction already chosen, not a new fork.

## NEXT STEPS

1. **This changes what "close the read-back gap" would mean.** Not "make retrieval better" -- three
   attempts at that failed tonight -- but **"give banked meanings a job whose success or failure can
   select them."** That is a different and more demanding build than the one I costed earlier.
2. **The perceptual-norms branch has one measured attempt that did NOT clear its floor.** Before
   more is spent there, that result deserves the same re-examination the definitional cells got.
3. Read Mollo & Millière properly rather than from an abstract.
