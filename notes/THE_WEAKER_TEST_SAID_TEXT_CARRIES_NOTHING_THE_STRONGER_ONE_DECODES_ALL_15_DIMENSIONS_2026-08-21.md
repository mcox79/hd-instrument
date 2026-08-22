# **A NEIGHBOUR READ-OUT DECODES ALL 15 NORM DIMENSIONS FROM OUR OWN PROFILES -- INCLUDING VALENCE AT `0.3069` AGAINST A `0.0385` NULL. THE PAIRWISE TEST I RAN AN HOUR EARLIER SAID "TEXT CARRIES ALMOST NONE OF THIS", AND IT WAS THE TEST THAT WAS WRONG.**

**I did not publish the negative. That is the only reason this is a finding and not a retraction.**

> **CONFIG:** *28 corpora round-robin, 286,069 sentences, 41 sentences/word, 3,000 words (2,021
> dropped by a SEEDED cap, printed not silent), `K=25`, self-exclusion ASSERTED in code, nulls = p95
> of 100 shuffles of the word->value map, recomputed PER DIMENSION.*
> **Scripts: `tools/which_norm_dimensions_can_text_recover.py`, `tools/can_a_readout_decode_the_dimensions_knn.py`.**

---

## 1. THE TWO TESTS, AND WHY THEY DISAGREE

| | what it asks | what it found |
|---|---|---|
| **PAIRWISE** *(weaker)* | across 200k random pairs, does text similarity track `-abs(z_d(w1)-z_d(w2))`? | **~nothing.** OURS cleared 3/15, all barely; best non-control `Auditory 0.0497` |
| **NEIGHBOUR READ-OUT** *(stronger)* | is a word's `z_d` predicted by the mean `z_d` of its 25 nearest neighbours, itself excluded? | ✅ **ALL 15 CLEAR, ON BOTH CHANNELS, at 5-12x their nulls** |

> ### **THE SPACE IS LOCALLY ORGANISED BY THESE DIMENSIONS AND GLOBALLY IS NOT.** *Between two random words, a single dimension's difference is swamped by topic. Among a word's NEAREST neighbours it is strongly present. Both statements are true and only the second is about whether the information is there.*

## 2. THE RESULT

| dimension | **OURS** | null95 | **IDF** | null95 | group |
|---|---|---|---|---|---|
| **Concreteness** | **0.4671** | 0.0387 | **0.5723** | 0.0496 | ✅ **POSITIVE CONTROL** |
| Haptic | 0.3681 | 0.0437 | 0.4469 | 0.0379 | sensorimotor |
| Auditory | 0.3537 | 0.0417 | 0.4750 | 0.0423 | sensorimotor |
| Interoceptive | 0.3410 | 0.0456 | 0.4352 | 0.0387 | sensorimotor |
| **Valence** | **0.3069** | 0.0385 | **0.4110** | 0.0389 | **AFFECT** |
| Visual | 0.2972 | 0.0467 | 0.4065 | 0.0453 | sensorimotor |
| Mouth | 0.2957 | 0.0493 | 0.4220 | 0.0403 | sensorimotor |
| Head | 0.2892 | 0.0404 | 0.3661 | 0.0407 | sensorimotor |
| **Dominance** | 0.2616 | 0.0420 | 0.3376 | 0.0403 | **AFFECT** |
| Olfactory | 0.2466 | 0.0419 | 0.3346 | 0.0405 | sensorimotor |
| Hand_arm | 0.2263 | 0.0471 | 0.3195 | 0.0467 | sensorimotor |
| Torso | 0.2116 | 0.0408 | 0.3345 | 0.0487 | sensorimotor |
| Foot_leg | 0.1887 | 0.0367 | 0.3140 | 0.0411 | sensorimotor |
| **Arousal** | 0.1886 | 0.0440 | 0.2946 | 0.0522 | **AFFECT** |
| Gustatory | 0.1742 | 0.0424 | 0.2553 | 0.0409 | sensorimotor |

✅ **THE POSITIVE CONTROL BEHAVES EXACTLY AS THE LITERATURE PREDICTS** -- concreteness is the
best-decoded dimension on BOTH channels. *That is what licenses reading the rest of the table.*

## 3. 🎯 THREE THINGS THIS SETTLES

**1. THE AFFECT TARGET IS NOT OUT OF REACH BY READING.** *`exp_verb_event_salient_channel_v1` found
3 affect dims beat all 12 sensorimotor ones on verb similarity (`0.3030` vs `0.2639`), and I flagged
it as SUPPLY with no evidence a reading system could get there.* **Our own accumulated profiles carry
valence at `0.3069`, eight times its null. The information is already in what we read.**

**2. AFFECT IS NOT MORE TEXT-LEARNABLE THAN SENSORIMOTOR -- IT IS SLIGHTLY LESS.** *OURS: mean affect
`+0.2524` vs mean sensorimotor `+0.2720`. IDF: `+0.3477` vs `+0.3736`.* **So my original caution was
right and the pairwise test's apparent reversal of it was noise.** ⚠️ *These are means over unequal
group sizes (3 vs 11) and no test of the difference was run -- read it as "no advantage", not as a
ranking.*

**3. 🔻 IDF BEATS US ON EVERY SINGLE DIMENSION, 15 OF 15.** *`0.5723` vs `0.4671` on the control,
`0.4110` vs `0.3069` on valence.* **The standing "behind counting" position reproduces on a
fifteenth independent measure.** *It is now: word recall, meaning similarity, and every norm
dimension separately.*

## 4. ⚠️ WHAT A NEIGHBOUR READ-OUT DOES **NOT** SHOW, AND THIS IS THE LOAD-BEARING LIMIT

***IT USES THE TRUE VALUES OF 25 NEIGHBOURS.*** **So it proves the SPACE IS ORGANISED such that the
attribute is smooth over it. It does NOT prove the substrate can produce the value unaided** -- to
use it you must already know the answer for some seed set.

> ### **THAT IS NOT A DEFECT, IT IS AN ARCHITECTURE: a small GROUNDED CORE plus PROPAGATION ALONG READING-DERIVED NEIGHBOURHOODS. It is this project's own three-tier design, and the owner's standing "distance to the grounded frontier" question, arriving from the measurement side.**

*What is NOT established: how small the seed can be, whether propagation survives more than one hop,
and whether it holds on words the corpus covers thinly. **None of those was measured here.***

## 5. ⚠️ LIMITS

1. **`K=25` was never swept.** *One value, chosen once. The result is not known to be K-robust.*
2. **3,000 of 5,021 eligible words**, seeded cap for memory. *Coverage is stated, not silent, but it
   is a sample.*
3. **A rank correlation across words is not a usable value.** *`0.3069` does not mean we could assign
   a word a valence score anyone should act on.*
4. **No paired test between OURS and IDF per dimension** -- 15/15 in the same direction is the
   evidence, not a CI on any one gap.
5. **This is the same 41-sentence read as every other number tonight**, so it inherits that regime.

## TLDR

An hour ago I ran a test asking whether reading can pick up the qualities that human rating tables
give us -- how concrete a word is, how it feels, whether it is pleasant. **The answer came back
"almost nothing", and I said I would not publish it until I had run a stronger test, because the weak
test could only detect one simple kind of pattern.**

**The stronger test reversed it completely.** All fifteen qualities are recoverable from the way words
sit near each other in what we read -- typically five to twelve times better than chance. Concreteness
comes out best, exactly as the published work predicts, which is the check that tells me the
measurement is sound.

**Why the two disagreed is worth keeping.** Pick two words at random and how pleasant they are tells
you nothing about whether they appear in similar contexts. But look at a word's closest neighbours and
they share it strongly. **The organisation is local, and the weak test only looked globally.**

**Two things follow.** The feeling-based information that separates verbs so well is **already sitting
in what we read** -- it is not something only a purchased table can supply. And plain word-counting
still beats us on **every one of the fifteen**, which is the same result we keep getting, now on
fifteen more measures.

**The honest catch:** this test works by looking up the true answer for a word's neighbours. It shows
the information is *arranged* usefully, not that we can produce it from nothing. That points at a
specific design -- ground a small core, spread outward along what reading puts nearby -- which is what
you have been asking about.

## QUESTIONS

None.

## NEXT STEPS

1. **The obvious next measurement, and it is cheap: HOW SMALL CAN THE SEED BE?** *Give the read-out
   only `N` labelled words and predict the rest. That converts this from a property of the space into
   a statement about how much grounding we would have to supply.*
2. **Sweep `K`** before this number is leaned on.
3. *Method note: **the weak test produced a clean, plausible, wrong negative, and the only thing that
   caught it was refusing to write it up.** It is the "narrow implementation failure generalised to
   impossible" rule firing in real time -- and the stronger test cost one command.*
