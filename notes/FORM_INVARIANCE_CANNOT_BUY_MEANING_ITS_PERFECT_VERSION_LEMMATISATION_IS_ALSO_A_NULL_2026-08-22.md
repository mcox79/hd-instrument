# **THE FORM CHANNEL MUST NOT BE WIRED INTO THE MEANING PATH. MEASURED TWO WAYS, INCLUDING ITS OWN PERFECT VERSION.**

**This closes the "what consumes `form_identity_vector`" question with a NEGATIVE on the consumer I
would have picked first**, and it discharges the owner's Q102 watch condition in the honest
direction: *the thing that raises recognition cannot raise meaning, and now that is a number.*

---

## 1. THE SETUP -- A REAL DEFECT IN THE LIVE CODE

`context_vector_masked` (`hdlab/reading_grounding_loop.py:251`) calls `normalize_lemma` on **every**
token to decide what to mask, then hands the **surface forms** to the encoder:

```python
words = [w for w in content_words(sentence) if normalize_lemma(w) != target_lemma]
return context_vector(" ".join(words), d=d, graded=graded)
```

**The lemma is computed on the live path and thrown away.** So `cat` and `cats` in the surrounding
context get independent random codes (measured `cos +0.0469`), and **21.8% of context tokens
(3,018 of 13,824) have a surface that differs from their lemma.** That is a genuine, live,
one-line-fixable inconsistency.

## 2. ⚠️ AND IT COSTS NOTHING. THE PREDICTION WAS WRITTEN DOWN FIRST AND IT FAILED.

*829 SimLex-999 pairs, both words with 41 sentences, 28 corpora, one variable -- whether the
surviving tokens are encoded as they appeared or as their lemma.*

| d | SURFACE (live) | LEMMA (twin) | **LEMMA - SURFACE** | 95% CI |
|---|---|---|---|---|
| 256 | `+0.0944` | `+0.0760` | `-0.0184` | `[-0.0867, +0.0458]` **not separated** |
| 1024 | `+0.1071` | `+0.0719` | `-0.0351` | `[-0.0921, +0.0218]` **not separated** |

*Floors recomputed on this population, never imported: **orthographic `|0.0791|`** (null p95 0.0704),
**frequency `|0.0392|`** (null p95 0.0664).*

> ### **THE POINT ESTIMATE IS NEGATIVE BOTH TIMES AND NEITHER CI SEPARATES. LEMMATISING THE MEANING BAG BUYS NOTHING.**

## 3. 🔑 **WHICH SETTLES THE FORM CHANNEL, BECAUSE LEMMATISATION IS ITS CEILING**

**Lemmatisation is the PERFECT merge of inflectional variants.** A form code is a *partial* merge
(`cat`/`cats` at `+0.4658`) that **additionally manufactures similarity between unrelated
lookalikes.** So lemma upper-bounds form-invariance on this axis. **An argument is not a
measurement, so the arm was run** (ungraded on both, so the only variable is the code):

| d=1024, ungraded bag | rho | its own null p95 | |
|---|---|---|---|
| SURFACE hash | `+0.0702` | `0.0596` | clears, barely |
| **FORM code** | **`+0.0573`** | **`0.0716`** | 🔻 **INSIDE THE NULL** |

> # **THE FORM CODE IN THE MEANING BAG CARRIES NO DETECTABLE MEANING SIGNAL. THE MEASUREMENT AGREES WITH THE ARGUMENT.**

## 4. WHAT THIS MEANS FOR Q102

The owner's ruling was: ***"connect it only after it is doing the job required of it... if it is not
performing sufficiently, as according to the brain, then it needs work."*** Applied **per consumer**,
which is the only way it can be applied:

| consumer | does the form channel do the job? |
|---|---|
| **recognition / lexical index** (retrieve `cat` from `cats`) | ✅ **YES** -- `0.0053 -> 0.9645` hit@1, the hash is at chance |
| **the meaning bag** | 🔻 **NO** -- inside its own null, and its perfect version is also null |

**So the channel is an IDENTITY organ and the meaning path is off-limits to it.** That is not a
disappointment -- it is the VWFA's actual role in the brain: **it feeds lexical access, it is not
lexical access, and it is certainly not semantics.** The empirical result and the anatomy agree.

## 5. LIMITS

1. **One benchmark (SimLex-999, Hill et al. 2015), one scorer, 829 pairs, one corpus shelf.**
2. **The word-class split is NOT a finding.** Verbs read `SURFACE +0.0341 -> LEMMA +0.1071`, which
   looks like a jump — **`0.1071` is inside its own null of `0.1372`.** Adjectives (n=92) are inside
   theirs too. **Only the noun cell clears anything** (`SURFACE +0.1037` vs null `0.0752`), and it
   moves the WRONG way under lemmatisation. *Reporting the verb number as a win would be the
   underpowered-null-as-capability error for the fourth time.*
3. **A null is not a proof of zero.** It says: at this power, on this population, no effect.
4. **The wiring itself stands and is unaffected** -- it is additive, `symbol_vector` is byte-identical
   (witnessed), and nothing in the meaning path was touched.

## 6. A BUG THIS RUN CAUGHT IN ITS OWN FIRST DRAFT, WORTH MORE THAN THE RESULT

**The first version's frequency floor read `-0.1335` against a null of `0.0664` -- a floor stronger
than the learned channel.** It was fake. The floor used `len(by[lem])`, which is **capped at 41**, and
every covered lemma has exactly 41 -- **a constant vector.** `np.argsort` of a constant array returns
`0..n-1` **in index order**, so a scorer carrying **zero information** produced a real-looking rho.

> ### **AN INFORMATION-FREE ARM MUST SCORE AS NOTHING, NOT AS A FLOOR.** *`_spearman` now refuses any vector with fewer than 3 distinct values, verified with a positive control (constant -> `nan`, real -> `0.8685`).*

*This is the documented "construct the information-free version of your winning arm and check it
LOSES" rule firing on a FLOOR rather than on a treatment -- and a fake floor is worse than a fake
treatment, because it silently raises the bar every other arm is judged against.*

## TLDR

The system reads a sentence and builds up what a word means from the words around it. **Those
neighbours are stored as they were spelled** — so "cat" and "cats" nearby count as two unrelated
things. The code already works out that they're the same word, and then throws that away. It looked
like an obvious thing to fix, and **21.8% of the surrounding words are affected**, so it should have
mattered.

**It doesn't.** I fixed it and measured: the score went slightly *down*, and the change is small
enough to be noise either way. So the spelling-vs-word-identity split is not what's holding meaning
back.

**That also answers the bigger question I was about to get wrong.** Yesterday I connected a
brain-inspired spelling-recognition component that is far better at telling "cat" and "CAT" are the
same word. The tempting next step was to feed it into the meaning machinery. **Fixing the same
problem perfectly buys nothing, so feeding it in partially cannot buy anything either — and measuring
it directly confirms that: its score sits inside the noise band.**

**So the component stays where it belongs: recognising words, not understanding them.** Which is what
the brain's word-recognition area actually does — it hands words off to the parts that do meaning; it
doesn't do meaning itself. **A negative result, arrived at cheaply, that stopped a wiring decision I
had already talked myself into.**

## QUESTIONS

None.

## NEXT STEPS

1. ⛔ **`form_identity_vector` is BARRED from the meaning path.** Recorded here and in the witness;
   its legitimate consumers are recognition/index sites only.
2. **The surface/lemma inconsistency stays as-is.** It is real but inert — *and now measured, so
   nobody spends another hour on it.*
3. *Method note: the honest sequence was **argue -> then measure the argument anyway.** The argument
   was right, and it cost about four minutes to stop trusting it.*
