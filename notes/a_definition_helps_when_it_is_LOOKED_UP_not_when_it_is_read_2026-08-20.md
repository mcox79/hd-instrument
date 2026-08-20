# A DEFINITION HELPS WHEN IT IS **LOOKED UP**, NOT WHEN IT IS **READ** -- AND IT ONLY HELPS *ALONGSIDE* THE PROFILE

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

**Fast mapping (Carey & Bartlett) + SCHEMA-DEPENDENT RAPID CONSOLIDATION (Tse et al. 2007):** a new
item integrates in one or few exposures **when it slots into an existing schema**, slowly when it
does not. The definitional genus IS the schema pointer.
- **PINNED BY EVIDENCE:** that schema-congruent items consolidate rapidly; that prior knowledge is
  what makes one-shot learning possible.
- **OUR INVENTION, UNDER TEST:** that *averaging the profiles of the definition's content words* is
  a faithful stand-in for schema-linked integration. **It is a stand-in. It scored well; that does
  not make it the brain's mechanism**, and the honest version of this result is "a
  schema-pointer-shaped intervention helped", not "we implemented fast mapping".

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
