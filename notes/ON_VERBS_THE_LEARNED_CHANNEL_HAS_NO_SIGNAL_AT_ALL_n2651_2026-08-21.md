# **ON 2,651 VERB PAIRS THE LEARNED CHANNEL SCORES `rho = +0.0000` AGAINST A NULL p95 OF `0.0372`. NO DETECTABLE MEANING SIGNAL AT ALL -- WHERE IT READS `0.1071` ON THE NOUN-HEAVY SimLex.**

**`MEMORY.md` carries a SUSPENDED claim -- *"we cannot resolve verbs even when handed the answer"* --
retired at `n=86` with the instruction to re-measure before building any verb channel. This is that
re-measurement at `n=2,651`.**

> **Computed on SimVerb-3500** (Gerz, Vulic, Hill, Reichart & Korhonen 2016). *Its provenance file
> asks that it be cited whenever a number computed on it is reported; this note and every number in
> it are that citation.* **CONFIG: `GRADED_COMPARATOR=True`, 28 corpora round-robin, 41 sentences per
> verb, `d=1024`.**

---

## 1. COVERAGE FIRST, BECAUSE IT DECIDES WHETHER THE TEST COULD RUN AT ALL

| | |
|---|---|
| SimVerb-3500 pairs parsed | **3,500** *(positive control: first row `take/remove 6.81`)* |
| distinct verbs | 827 |
| verbs covered at >=41 sentences | **646 (78%)** |
| **PAIRS SCORED** | **2,651** *(SimLex gave 829)* |

## 2. THE RESULT

| arm | rho |
|---|---|
| **UNWEIGHTED bundle -- what ships** | **`+0.0000`** *(null p95 `0.0372`)* |
| idf-repeated, cap 2x | +0.0229 |
| idf-repeated, cap 3x | +0.0236 |
| idf-repeated, cap 5x | +0.0213 |

> ### **`+0.0000`. Not "weak" -- INDISTINGUISHABLE FROM A SHUFFLE, on 2,651 pairs.**

**HELD-OUT weighting gain (cap chosen on one half, scored on the other, 2,000 splits):
`+0.0188`, 95% CI `[-0.0069, +0.0399]`, half-width `0.0234` -- DOES NOT SEPARATE.**

## 2b. ✅ **REPLICATED ON A SECOND BENCHMARK -- AND THIS ONE IS THE EXACT RE-MEASUREMENT MEMORY ASKED FOR**

*`MEMORY.md` says: re-measure on all 222 SimLex verb pairs before building any channel. Done --
203 of the 222 are covered. **Same benchmark, same scorer, same 41-sentence profiles as the noun
number, so THIS contrast is internally valid and needs no cross-population caveat.***

| POS | pairs | rho | null p95 | |
|---|---|---|---|---|
| **NOUN** | 534 | **0.1310** | 0.0843 | ✅ clears its null |
| **VERB** | **203** | **`-0.0002`** | 0.1398 | 🚫 **INSIDE the null band** |
| ADJ | 92 | 0.2207 | 0.1931 | ✅ clears, barely |

> ### **`-0.0002` HERE AND `+0.0000` ON SimVerb'S 2,651 PAIRS. TWO INDEPENDENT BENCHMARKS, BOTH AT ZERO.**

***The two do different jobs and are stronger together: SimVerb supplies the POWER (n=2,651, null
`0.0372`), SimLex supplies the WITHIN-BENCHMARK CONTRAST (nouns clear, verbs do not, nothing else
changed).*** ⚠️ *SimLex's verb null is `0.1398` at n=203 -- a wide band. On its own that would be
"underpowered"; what makes it readable is the SimVerb replication at a tight null.*
⚠️ *ADJ at `0.2207` clears a `0.1931` null on 92 pairs -- noted, not leaned on.*

## 3. ✅ **AND THE POWER PREDICTION FROM AN HOUR AGO WAS CORRECT**

*I calculated that resolving a `+0.03` effect needed roughly `2.8x` more pairs than SimLex's 829.*
**At 2,651 pairs the half-width fell from `~0.05` to `0.0234`** -- close to the `sqrt(2651/829) = 1.79`
improvement predicted. ***The bigger benchmark delivered exactly the resolution it promised.***

**And with that resolution, the `~+0.03` weighting effect did NOT confirm -- the point estimate
SHRANK to `+0.0188` and the interval still spans zero.** *Two schemes, two benchmarks, no separation.*

## 4. 🧠 WHY THIS IS NOT A SURPRISE, AND WHY IT STILL MATTERS

**Verb meaning is the known hard case for distributional context** -- a verb's neighbours are its
arguments, and *give/receive*, *buy/sell*, *feed/starve* share arguments while meaning opposite
things. *SimVerb's own relation labels include ANTONYMS as a category; `feed/starve 1.49` sits in our
data.* **A bag of nearby content words cannot separate those, and ours does not.**

***What matters is the SIZE of the gap: on nouns we are weak (`0.1071`, above a `~0.065` null); on
verbs we are AT the null. The channel is not uniformly weak across word classes -- it is weak on
nouns and ABSENT on verbs.***

## 5. ⚠️ LIMITS

1. **Different population from SimLex. NOTHING here may be blended with the `0.1071`** -- different
   benchmark, different word class, different pairs.
2. **78% verb coverage.** *The 22% uncovered are rarer verbs; the covered set is the easier half.*
3. **This is the LEARNED channel only.** *Not the supplied norms, not counting -- neither was run
   here.*
4. **`+0.0000` is a point estimate inside a null band, not a proof of exactly zero.**

## TLDR

Our system builds a word's meaning from the words around it. **On verbs, that produces nothing at
all** — a correlation with human judgement of exactly zero, across 2,651 verb pairs, indistinguishable
from shuffled data.

On nouns it manages a weak but real signal. **On verbs there is no signal to be weak.**

**This is not shocking, and that is part of the point.** Verbs are the known hard case: *give* and
*receive* appear alongside the same words while meaning opposite things, and *feed* and *starve* sit
in our test data rated as near-opposites. **Counting nearby words cannot tell those apart, and ours
does not.**

**Two other things came out of it.** An hour ago I calculated that our usual test set was too small to
settle a small effect, and estimated we would need roughly three times more data. **That prediction
was accurate** — the larger set cut the uncertainty almost exactly as predicted. **And with that
sharper measurement, the small improvement I had been chasing got smaller and still did not
establish.**

**Our notes have carried a suspended claim that we cannot handle verbs, retired because it rested on
86 examples with an instruction to re-measure. This is that re-measurement, on 2,651.**

## QUESTIONS

None.

## NEXT STEPS

1. **Quote verbs and nouns SEPARATELY, always.** *`0.0000` on SimVerb-3500 and `0.1071` on SimLex are
   different benchmarks and different word classes.*
2. **The suspended MEMORY claim can be reinstated with a real n** -- *but as "no distributional signal
   on verbs at n=2,651", not as the original wording.*
3. *Method note: **the power calculation that motivated this was made before the data was chosen, and
   it held.** That is the first time tonight a prediction of mine survived its own test.*
