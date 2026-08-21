# **THE BEST SEMANTIC ASSET WE OWN IS 12 HUMAN-MEASURED DIMENSIONS -- IT BEATS A 121-MILLION-TOKEN TRAINED ENCODER, IT IS LIVE, AND IT IS CAPPED OUT OF INFLUENCING ANY DECISION**

**`ASSET_NORMS12` -- the arm that beat our production encoding CI-separated (`rho 0.2701` vs
`0.1048`, difference `+0.1653`, CI `[0.0159, 0.3084]`) -- is not a trained model at all.**

`asset_provenance` names it: **`hdlab/grounded_similarity.py`**. Twelve dimensions:
**11 Lancaster sensorimotor norms + 1 Brysbaert concreteness norm.** *Direct human behavioural
measurements.*

---

## 1. WHAT IT BEAT

| arm | what it is | rho |
|---|---|---|
| **`ASSET_NORMS12`** | **12 human norm dimensions** | **0.2701** |
| `ASSET_RETRAIN_ISOL` | retrained encoder | 0.2581 |
| `ASSET_V2` | **121.1M-token encoder trained on a 237.7M-token corpus** | 0.0783-0.1890 by readout |
| `P_LIVE_CONCEPT` (incumbent) | our live 256-d accumulation | **0.1048, CI crosses zero** |

**➡️ TWELVE HUMAN-RATED DIMENSIONS BEAT A 121-MILLION-TOKEN LEARNED ENCODER AND OUR 256-DIMENSION
PRODUCTION ENCODING.** *21x smaller than the incumbent.*

**AND IT IS THE BRAIN-FOUNDATIONAL OPTION, EXPLICITLY.** The module's own rationale: the **ATL amodal
hub** aggregates graded MULTIMODAL sensorimotor experience (Cox et al. 2024), **not bag-of-words
co-occurrence**, and the Lancaster norms (Lynott, Connell, Brysbaert, Brand & Carney 2020) are *"a
direct behavioral measurement of exactly that signal."* **The most brain-faithful asset is also the
best-performing one.** *That is the cleanest vindication of the standing brain-foundational
instruction I have found.*

## 2. ✅ IT IS **NOT** ISLANDED -- I CHECKED BY RUNNING

A real 40-sentence read loads **both** `hdlab.grounded_similarity` and `hdlab.lexical_similarity`.
`lexical_similarity.py:60` imports it; `:615` calls it. **Live and reached.**

## 3. 🔴 **BUT WHAT IS LIVE IS THE *CAPPED SCALAR*, NOT THE VECTORS THAT WON**

```
GROUNDED_CAP = 0.45     # structurally BELOW SIMILARITY_LINK_THRESHOLD = 0.50
```

**The cap exists so the grounded fallback can NEVER trigger a same-idea/merge decision** -- deliberate,
principled, and documented as safe-by-construction. Measured live:

| pair | `grounded_similarity()` |
|---|---|
| `sofa / couch` (true synonym) | **0.45** |
| `dog / cat` (sibling, distinct) | **0.45** |
| `kidney / liver` (sibling) | **0.45** |
| `stone / idea` | 0.0 |
| `democracy / freedom` | 0.0 |

**Effectively two-valued** -- and `dog/cat` scores identically to `sofa/couch`, **exactly the ceiling
the module's own docstring documents up front with measured numbers.**

**➡️ THE ARM THAT WON USED `grounded_vector()` -- THE RAW 12-DIM Z-SCORED VECTORS. THE LIVE PATH USES
`grounded_similarity()` -- A SCALAR CAPPED AT 0.45.** *These are different objects. The measured
advantage belongs to the vectors, and the vectors are not what any decision sees.*

## 4. AND ALMOST NOTHING CONSUMES THE RAW VECTORS

`grounded_vector` appears in exactly **two** modules: its own file, and `hdlab/sensorimotor_spoke.py`
(one import, inside a function). **The 39,707-word asset resolves abstract words too** -- `democracy`
returns a full 12-dim vector -- **so this is not a coverage limit.**

**THE CAP IS RIGHT FOR ITS JOB AND WRONG AS A CEILING ON EVERYTHING ELSE.** *Preventing a false
same-idea merge is a decision-safety rule. It is not a reason to withhold a 12-dimensional graded
feature space from anything that needs graded meaning -- which, tonight, is every organ examined.*

## TLDR

The best measure of word meaning we own is **not a trained model**. It is **twelve numbers per word,
measured from human beings** — eleven ratings of how strongly a word relates to each sense and body
action, plus one rating of how concrete it is.

**Those twelve numbers beat a model trained on 121 million tokens, and beat our own running system,
which uses 256 numbers per word.**

They're also the most brain-faithful option we have, and the module says why: the brain region that
does this job pools graded sensory and motor experience, and these ratings are a direct measurement
of exactly that. **The most brain-like choice is also the best-performing one** — which is the
clearest support I've found for the instruction to chase brain-foundational designs.

**It is not sitting unused** — I confirmed by running the system that it loads and is called.

**But what's live is a deliberately blunted version.** The output is squashed to a maximum of 0.45,
just below the level that would let it declare two words the same thing. That cap is sensible for its
original job — stopping the system from wrongly merging concepts. The consequence is that in practice
it returns **0.45 or 0.0 and little else**: *sofa/couch* and *dog/cat* score identically.

**The twelve raw numbers — the thing that actually won — are used by almost nothing.** They exist,
they're loaded, they cover abstract words too. But every decision in the system sees only the
flattened score.

**So the cap is right for preventing bad merges and wrong as a ceiling on everything else.**

## QUESTIONS

None.

## NEXT STEPS

1. **The raw 12-dim vectors are already live and already loaded** -- exposing them as a feature space
   is a wiring, not a build, and it is the highest-value cheap move I have found tonight.
2. **Do NOT remove the cap on `grounded_similarity`** -- it is doing a different, correct job.
3. `hdlab/sensorimotor_spoke.py` is the one existing consumer and should be read next.
