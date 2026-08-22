# **MY OWN PREDICTED FIX FAILED ITS OWN TEST -- SUBTRACTING CO-OCCURRENCE MAKES VERBS *WORSE* AT EVERY SETTING. AND THE PROPAGATOR I WAS TRYING TO INVENT WAS BUILT, `HARD_PASS`, TWO WEEKS AGO, FROM A 12-WORD SEED.**

**Two findings, and the second is worth more than the first.**
*`tools/does_subtracting_cooccurrence_rescue_verbs.py`.*

---

## 1. ✅ THE GATES PASSED, SO THE NEGATIVE IS READABLE

| gate | result |
|---|---|
| **A REPRODUCTION** -- OURS alone must return near `0.0000` on this population | ✅ **`+0.0062`**, 646 verbs / **2,651 pairs** -- exactly the recorded population |
| **THE BAR** -- idf-counting, same pairs | **`+0.0819`** |
| **B COOC ALONE** | **`+0.0464`** |

⚠️ *`0.0819` here vs `0.0689` recorded earlier for idf on the same 2,651 pairs -- **a real
implementation difference between two scripts, flagged not hidden.** Either way it is the bar and we
are far below it.*

## 2. 🔻 THE ARM: SUBTRACTING CO-OCCURRENCE HURTS, MONOTONICALLY

| lambda | OURS - L*COOC | OURS - L*RANDOM *(control)* |
|---|---|---|
| **0.00** | **`+0.0062`** | `+0.0062` |
| 0.10 | `+0.0008` | `+0.0032` |
| 0.20 | `-0.0048` | `+0.0002` |
| 0.50 | `-0.0217` | `-0.0037` |
| 1.00 | `-0.0397` | `-0.0052` |
| 1.50 | `-0.0464` | `-0.0062` |

**IN-SAMPLE BEST lambda = `0.0` -- THE FITTED OPTIMUM IS TO NOT DO IT.** *Held-out gain `-0.0005`
over 2,000 splits; does not exclude zero.* ⚠️ *The held-out CI prints `[+0.0000,+0.0000]` because
lambda=0 wins on nearly every split so the gain is exactly 0 there -- **a degenerate-looking interval
with an ordinary cause, NOT the reachability failure that shape usually signals.***

> ### **AND IT IS WORSE THAN A RANDOM PENALTY OF THE SAME MAGNITUDE AT EVERY LAMBDA.**

## 3. 🧠 **WHY I WAS WRONG -- AND ONE NUMBER SAYS IT**

***`COOC ALONE = +0.0464`. CO-OCCURRENCE IS *POSITIVELY* CORRELATED WITH HUMAN SIMILARITY.***

**My chain was right about antonyms and wrong about the population.** *Antonyms really do co-occur
more (`0.0782` vs `0.0022` random -- that measurement stands). **But across all 2,651 pairs the
dominant fact is that RELATED WORDS CO-OCCUR** -- synonyms, cohyponyms, topically linked verbs. The
antonym elevation is a genuine minority effect swamped by the general one, so subtracting deletes
mostly good signal.*

**THE LINKS OF THE CHAIN REMAIN MEASURED AND TRUE. THE FIX DERIVED FROM THEM DOES NOT FOLLOW.**
*A correct mechanism does not entail that its obvious inverse is a correction.*

## 4. 🔎 **THE PRIOR-WORK CATCH, WHICH IS THE REAL RESULT**

*Found by opening `notes/PLAN_B_grounding_word_context_affect_superposition_map_2026-08-07.md` -- **a
PLAN OF RECORD, USER-confirmed, co-designed with the owner** -- which I had never read.*

**Its BUILD ORDER stage 1 is marked `[DONE = HARD_PASS, Director-VET'd]`.**
*`exp_social_relational_grounding_axis_v1`: a **12-WORD supplied seed** propagated to open vocabulary
through `hdlab/wordnet_polarity_propagation.py`, feeding the already-owned earned valuation.*

| | |
|---|---|
| open-vocab accuracy, **12 HELD-OUT verbs**, disjoint from seed | **`0.833`** |
| scramble | `0.483` *(lift 0.35)* |
| **seed ablation** | **`0.000`** -- *the seed IS the lever* |
| random-theta | `0.467` *(near chance -- the EARNED valuation does the work)* |

**AND IT IS ANTONYM-AWARE BY CONSTRUCTION.** *Verified on disk: its **Stage A, at HIGHER PRECEDENCE
than the similarity stage, predicts the OPPOSITE pole from WordNet lemma antonyms** unioned with
curated flip-pairs.* ***That is precisely the opposition mechanism distributional propagation
provably lacks, and it existed before I started.***

> # 🔑 **I SPENT THE NIGHT MEASURING A PROPAGATION MECHANISM WORSE THAN ONE ALREADY ON DISK.**

⚠️ **THE TWO NUMBERS ARE NOT COMPARABLE AND I AM NOT COMPARING THEM.** *`0.833` is accuracy on a
12-word polarity task; my `0.3035` is a rank correlation on valence across 1,000 words. Different
tasks, scorers and populations.* **The fair comparison is STRUCTURAL: theirs propagates along explicit
lexical relations INCLUDING ANTONYMY; mine along distributional similarity, which cannot see it.**

⚠️ *It is WordNet-SUPPLIED, not learned by reading -- admissible under the owner's 2026-08-16 ruling
that a static offline-built asset is fine, but it is **SUPPLY, not learning**.*

## 5. ⚠️ LIMITS

1. **One scorer, one benchmark, verbs only.**
2. **The co-occurrence term is my own construction** (`log1p(lift) + 3*coord_rate`). *A different
   formulation might behave differently -- though the sign of `COOC ALONE` makes that unpromising.*
3. **I have NOT re-run the WordNet propagator.** *Its numbers are quoted from the plan of record and
   its cell; I verified only that the module and its antonym stage exist on disk.*
4. 🔻 **NOTHING I MEASURED TONIGHT TESTS THE PLAN'S ACTUAL LAYER 2.** *That is a CONTEXT-CONDITIONED
   superposition -- "spoil" holding both *ruin* and *pamper* until context collapses it. **Everything
   I ran assigns ONE value per word, which the architecture explicitly calls the wrong object.**
   So tonight's numbers are a FLOOR for it, not a test of it.*

## TLDR

I predicted that if our system mistakes "these two words appear together" for "these two words mean the
same thing", then subtracting that signal should help. **I built it. It fails at every setting** — and
is worse than subtracting a random number of the same size.

**One number explains it:** words that appear together usually *are* related. Opposites appearing
together is real, but it is a small effect sitting inside a much larger one, so removing it throws away
more good information than bad. **My reasoning about opposites was right; the fix I derived from it was
not.**

**The more important discovery came from reading, not measuring.** There is a plan of record for
grounding that you and I co-designed on the 7th of August, and I had never opened it. Its first build
stage is already finished and passed: **twelve hand-chosen words, spread outward through a dictionary's
own network of synonyms and opposites, reaching 83% accuracy on held-out words it had never seen** —
and deleting those twelve words drops it to zero, so the seed genuinely does the work.

**Crucially it spreads through explicit "opposite-of" links** — exactly what my approach cannot do, and
it was built two weeks before I started trying to invent it.

**So, honestly: I spent tonight measuring a way of spreading word meanings that needs hundreds of
starting words and still loses to word-counting, while a better one needing twelve sat on disk.** I am
not comparing the two scores directly — they are different tasks — but structurally the built one has
the property mine provably lacks.

## QUESTIONS

None.

## NEXT STEPS

1. **Read the rest of the plan of record and re-plan against it.** *It is USER-confirmed and
   authoritative; I have read about two thirds.*
2. **Re-frame every number from tonight as a FLOOR.** *They all assign one value per word; the
   architecture specifies a context-conditioned superposition.*
3. *Method note: **the failing arm was cheap and its gates made it readable.** The expensive mistake
   was not opening a USER-confirmed plan of record before spending a night re-deriving part of it.*
