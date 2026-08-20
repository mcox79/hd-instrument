# ⛔⛔ **WITHDRAWN ON THE SECOND SEED. THE HEADLINE BELOW IS AN ARTIFACT.** ⛔⛔

**Seed 7 gave `BOTH` a 16-rank gain. Seed 101 gives it -1.0, and the INFORMATION-FREE CONTROL BEATS
IT.**

| seed 101, n=119, 195 candidates | rank |
|---|---|
| PROFILE | 53.0 |
| BOTH (profile + **right** definition-lookup) | 52.0 -- **a 1-rank "gain"** |
| BOTH_SHUFFLE (profile + **wrong** definition) | 62.0 |
| **BOTH_NOISE (profile + RANDOM VECTOR)** | **45.0 -- THE BEST ARM ON THIS SEED** |
| COOC | 3.0 |

**BLENDING WITH RANDOM NOISE BEAT BLENDING WITH THE RIGHT DEFINITION.** The guard printed its own
verdict without being asked: *"AN INFORMATION-FREE BLEND ALSO BEATS THE PROFILE -- the gain is
SMOOTHING, not the definition. BOTH is an ARTIFACT unless it clears these two."*

**SO THE SEED-7 RESULT WAS A LUCKY DRAW AND THE MECHANISM STORY BUILT ON IT IS VOID.** It is also
unstable *within* seed 101: `BOTH` beats `PROFILE` by 11.5 in the low-exposure stratum and LOSES by
16.0 in the high one, where seed 7 had it winning in both.

### ✅ SEED 13 CONFIRMS THE WITHDRAWAL, FROM THE OTHER DIRECTION

| seed 13, n=131 | rank |
|---|---|
| PROFILE | 57.0 |
| BOTH | 52.0 |
| **BOTH_SHUFFLE (the WRONG definition)** | **53.0 -- ONE RANK from BOTH** |
| BOTH_NOISE | 62.0 |

**Using another term's definition performs the same as using the right one.** The guard fired here
too. **ALL THREE SEEDS: `BOTH - PROFILE` = -16.0 / -1.0 / -5.0, and on TWO OF THREE an
information-free blend matched or beat the treatment.** A gain that only appears on one seed, and
that a random vector reproduces on another, is not a gain.

**⚠️ FOURTH TIME IN A WEEK A SINGLE-SEED WIN WAS READ AS A RESULT.** The standing rule -- *a
single-seed win is a HYPOTHESIS* -- is written in the note below, by me, before the second seed ran.
**The rule was written down, applied to the limits section, and I still led with the headline.**

**WHAT SURVIVES, ON BOTH SEEDS:**
- **`DEF_LOOKUP` alone is WORSE than `PROFILE`** (67.0 vs 54.5; 69.0 vs 53.0). Consistent.
- **`SHUFFLE_LOOKUP` is far worse than `DEF_LOOKUP`** (106 vs 67; 104 vs 69), so **the definitions
  DO carry term-specific signal -- just not enough of it.** Consistent, and the one honest positive.
- **`COOC` reads 5.0 / 3.0 and crushes every arm on both seeds.** Consistent.

**⛔ AND THE CORRECTION I MADE AN HOUR AGO IS ITSELF WITHDRAWN.** I used the seed-7 `BOTH` result to
refute my earlier claim that "combining dilutes when one channel is weaker", replacing it with "the
condition is INDEPENDENCE, not comparable strength". **That refutation rested on this artifact, so it
is void.** Honest position: **NEITHER boundary condition is established -- both claims were built on
single runs, and combining behaved inconsistently across seeds.** *The earlier note has been restored
to say that rather than leaving my confident correction standing.*

**WHAT WORKED: the control did its job.** `BOTH_NOISE` and `BOTH_SHUFFLE` were added *before* the
replication, precisely because a blend beating its own component is where an artifact hides. They
caught it automatically, on the first seed that disagreed.

---

# [WITHDRAWN -- KEPT FOR THE RECORD] A DEFINITION HELPS WHEN IT IS **LOOKED UP**, NOT WHEN IT IS **READ**

**2026-08-20, late.** Two hours ago I measured that indexing a term by its definition's raw text
vector retrieves **28 ranks WORSE** than the accumulated profile, and concluded the route was
closed. **That conclusion was too broad. Changing HOW the definition is consumed reverses the
sign.**

## THE DIFFERENCE, AND IT IS THE WHOLE RESULT

| how the definition is used | what the vector is | rank |
|---|---|---|
| **READ** (previous experiment) | context vector of the definiens TEXT, ~7 raw tokens | **92.0** vs profile's 64.0 |
| **LOOKED UP** (this one) | **mean of the already-learned PROFILES of the words the definition names** | 67.0 vs profile's 54.5 -- *still worse alone* |
| **LOOKED UP, ALONGSIDE THE PROFILE** | normalised sum of the two | **38.5 vs 54.5 -- 16 RANKS BETTER** |

**"a drupe is a fleshy FRUIT with a hard STONE" is worth little as seven tokens and a great deal as
a POINTER TO `fruit`** -- a profile built from hundreds of encounters. The definition's value is
BORROWED VOLUME, which is exactly what the previous experiment's failure predicted: it identified
volume, not quality, as the binding constraint.

## THE CONTROLS, WHICH ARE THE REASON THIS IS REPORTABLE AT ALL

A blend beating its own component is precisely where a regularisation artifact hides, so **the
information-free version of the winning arm was built and scored** (standing rule):

| arm | ALL | LOW exposure | HIGH exposure |
|---|---|---|---|
| PROFILE | 54.5 | 65.0 | 44.0 |
| **BOTH** = profile + **right** definition-lookup | **38.5** | **46.0** | **32.0** |
| **BOTH_SHUFFLE** = profile + **another term's** definition-lookup | 58.0 | 65.5 | 55.5 |
| **BOTH_NOISE** = profile + **random unit vector** | 78.0 | 81.0 | 64.5 |
| SHUFFLE_LOOKUP alone | 106.0 | 106.0 | 97.5 |
| **COOC** | **5.0** | 5.2 | 4.5 |

**BOTH_SHUFFLE (58.0) is WORSE than PROFILE (54.5), and BOTH_NOISE (78.0) far worse.** Averaging the
profile with *any* smooth in-space vector does NOT help -- **it hurts.** Only the term's OWN
definition helps. **The gain is not smoothing; it requires the right content.** That holds in both
exposure strata separately, not just pooled.

## ⚠️ AND IT IS STILL EIGHT TIMES WORSE THAN COUNTING WORDS

**COOC = 5.0. Our best arm = 38.5.** This is an INTERNAL improvement on a task where plain
co-occurrence counting remains far ahead. **It is not a capability claim and must never be quoted as
one.** What it is: the first thing measured all day that makes the definitions *do* anything at all.

## ⛔ TWO OF MY OWN CLAIMS CORRECTED, ONE FROM TWO HOURS AGO

1. **"Combining helps when channels are comparably strong; when one is strictly weaker it dilutes."
   REFUTED.** DEF_LOOKUP (67.0) is weaker than PROFILE (54.5) and BOTH still gains 16 ranks.
   **THE CORRECTED CONDITION IS INDEPENDENCE, NOT COMPARABLE STRENGTH:** the second channel must be
   an INDEPENDENT ESTIMATE OF THE SAME THING IN A COMPARABLE REPRESENTATION. Here it is a mean of
   learned profiles -- same kind of object, different evidence. In the failed experiment it was a
   raw context vector over seven tokens: not an estimate of the term, just more text. **The owner's
   original "combine channels" hypothesis was right and my amendment to it made it worse.**
   *Corrected in place in the earlier note, which had published the wrong version.*
2. **MY PRE-COMMITTED PREDICTION FAILED.** I predicted DEF_LOOKUP would beat PROFILE **in the
   low-exposure stratum and not the high one**. It beat PROFILE in NEITHER (+8.5 low, +11.0 high).
   The stratification is visible only in the COMBINATION (**-19.0 low vs -12.0 high**), which is
   directionally what fast-mapping predicts but is not what I said would happen. **Recorded because
   a prediction that has to be reinterpreted after the fact is not a prediction that succeeded.**

## 🧠 THE BRAIN FRAME, AND WHAT IS PINNED VS INVENTED

> # ⛔ **CORRECTED WITHIN THE HOUR: I LABELLED THIS MECHANISM "PINNED BY EVIDENCE". IT IS NOT.**
> **`notes/ORGAN_MAP.md` §G1 says the opposite, verbatim:** *"Lexical-semantic acquisition:
> **UNPINNED, deliberately.** ... **No equation is offered for either half.** (And the strong 'fast
> mapping writes directly to cortex' alternative has **collapsed under replication** -- Warren & Duff
> 2014; Cooper, Greve & Henson 2019.)"*
>
> **PRESENTING AN INVENTION AS BRAIN-DERIVED IS THE SPECIFICALLY BARRED MOVE** -- the standing rule
> is *invent freely, but never label an invention as pinned* -- and it is **the same fault already
> on record for VSA binding**, where every brief and organ row calling it brain-derived was found
> mislabelled. **I found this only because I ran the THIRD archive check (ORGAN_MAP's corrections)
> AFTER building, which is also the wrong order.** The prior-work rule is three reads *before*
> proposing a brain mechanism, and I did two of them late.
>
> **THE EMPIRICAL RESULT IS UNAFFECTED** -- the ranks, the controls and the shuffles are what they
> are. **What is withdrawn is the justification**, and that matters because a brain-derived label is
> exactly what would license building on this without further evidence.

**WHAT IS ACTUALLY STANDING, STATED HONESTLY:**
- **BEHAVIOURAL PHENOMENON, not disputed:** children acquire a usable word meaning from very few
  exposures when told what kind of thing it is (Carey & Bartlett fast mapping). *That is a fact
  about behaviour, not a mechanism, and it is all I am entitled to lean on.*
- **MECHANISM: UNPINNED.** Per ORGAN_MAP G1 the field offers no equation for either the fast or the
  slow phase of lexical-semantic acquisition, and the strong direct-to-cortex account has failed
  replication. **I should not have cited Tse et al. 2007 as pinning this.**
- **OUR INVENTION, UNDER TEST:** that *averaging the profiles of the definition's content words* is
  a stand-in for schema-linked integration. **It scored well; that does not make it the brain's
  mechanism.** The honest sentence is *"a schema-pointer-SHAPED intervention helped on this task"* --
  never *"we implemented fast mapping"*.
- **UNPINNED != STOP** (standing rule): testing the best brain-motivated candidate is allowed. What
  is barred is the label, and the label is what I got wrong.

## LIMITS

1. **ONE SEED (7), n=132, 211 candidates.** Seeds 101/13 running. **A single-seed win is a
   HYPOTHESIS** -- this project's own rule, and it has burned three results this week.
2. **`GENUS_HEAD` alone (71.2) is the WORST definition-based arm** -- worse than using all the
   definition's words. So if a schema pointer is what helps, it is not carried by the head noun
   alone, which is mild evidence against the narrowest reading of the mechanism.
3. Leak-controlled: **3,252 cue sentences excluded** as a definition's own source; the term is
   excluded from its own definition's lookup words.

## TLDR

Earlier I found the system writes good definitions, nothing reads them, and that making it read
them made things worse. **That last part was too hasty -- it depended on HOW you read them.**

Feeding the system the definition's raw words is nearly useless: seven words against the hundreds it
has already seen. But a definition mostly points at things the system **already knows** -- "a drupe
is a fleshy *fruit*" is valuable because it knows a lot about fruit. **Looking those words up and
using what it already knows about them, TOGETHER with its own experience of the new word, made
finding the right word about 30% better.**

The check that makes this believable: doing the same trick with the **wrong** definition, or with a
random vector, makes things **worse**, not better. So it is the actual content that helps, not the
act of blending.

**Two honest dampeners.** Plain word-counting still beats this by about eight to one, so this is us
getting better at our own game, not winning. And it is one run — I have two more going, and a single
run has fooled us three times this week.

I also got two things wrong and am correcting them: I predicted this would help mainly for rarely-
seen words and it helps for both; and I claimed two hours ago that blending a weaker source always
dilutes, which this disproves.

## QUESTIONS

None. Nothing here needs a decision -- it needs replication.

## NEXT STEPS

1. **Seeds 101/13** -- running. Single seed is a hypothesis.
2. If it replicates, the named build target is **a read route that blends the profile with the
   looked-up definition** -- notably NOT the "index by the definition" route measured and rejected
   two hours ago.
3. **Still do not spend on extractor recall.** This is the first evidence the definitions can matter
   at all; volume of them is a later question.
