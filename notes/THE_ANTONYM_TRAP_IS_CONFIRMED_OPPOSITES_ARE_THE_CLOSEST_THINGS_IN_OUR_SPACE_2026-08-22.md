# **PROPAGATING MEANING BY SIMILARITY GIVES OPPOSITES THE SAME VALUE. PREDICTED 2026-08-06, TESTED TONIGHT, CONFIRMED -- AND ANTONYMS ARE THE *CLOSEST* THINGS IN OUR SPACE.**

**The prediction was made two weeks before the measurement and by a different piece of work.**
*`SYNTHESIS_grounding_wall_definitive_2026-08-06.md`: good/bad is not recoverable from text statistics
**because antonyms are distributionally near-identical**. This is its first direct test.*
*`tools/does_propagation_give_antonyms_the_same_valence.py`.*

> **CONFIG:** *28 corpora, 286,069 sentences, 41 sentences/word, `K=25`. **SimVerb-3500's OWN relation
> labels** -- so the antonym/synonym split is GOLD, not my judgement. 635 test words, 2,500-word seed
> pool, **disjoint (asserted in code)**, Warriner valence.*

---

## 1. ✅ **BOTH POSITIVE CONTROLS PASS, SO THE TEST IS READABLE**

| control | requirement | result |
|---|---|---|
| **A -- GOLD** | true valence must actually separate antonyms from synonyms, else the population cannot answer the question | ✅ **`1.3627` vs `0.7260` = 1.88x** *(abort threshold was 1.5x)* |
| **B -- PROPAGATION** | propagation must work at all, else a failure on antonyms means nothing | ✅ **rho `0.2367`** over 635 words |

*Both were written to ABORT the run. Neither fired.*

## 2. 🔻 THE RESULT

| relation | n | **TRUE** diff | **PREDICTED** diff | cosine in our space |
|---|---|---|---|---|
| **ANTONYMS** | 96 | **1.3627** | **0.3017** | **`0.2062`** ← **HIGHEST** |
| SYNONYMS | 232 | 0.7260 | 0.3317 | 0.1727 |
| COHYPONYMS | 141 | 0.8168 | 0.3360 | 0.1660 |
| HYPER/HYPONYMS | 602 | 0.6951 | 0.3272 | 0.1649 |
| NONE | 1,446 | 0.9630 | 0.3221 | 0.1591 |

> ### **TRUE valence spans `0.695` to `1.363` across relations. PREDICTED valence spans `0.302` to `0.336`. PROPAGATION IS FLAT -- IT CANNOT SEE RELATION TYPE AT ALL.**

**AND IT IS SLIGHTLY BACKWARDS ON THE ONE THAT MATTERS: antonyms `0.3017` vs synonyms `0.3317`, a
ratio of `0.91x`.** *The pairs that are genuinely FURTHEST apart are predicted to be the CLOSEST.*
⚠️ *That gap is small; the honest reading is **NO SEPARATION**, not "reversed".*

**WITHIN ANTONYMS, rho(true difference, predicted difference) = `-0.0259` at n=96.** *The null band at
that n is about `+/-0.201`, so this is **indistinguishable from zero** -- and the test was well powered
for the strong relationship a working mechanism would produce.*

## 3. 🎯 **AND THE MECHANISM IS CONFIRMED DIRECTLY, NOT JUST INFERRED**

***ANTONYMS HAVE THE HIGHEST COSINE OF ANY RELATION IN OUR SPACE -- `0.2062`, above SYNONYMS `0.1727`
and above unrelated pairs `0.1591`.***

> ### **IN OUR REPRESENTATION, OPPOSITES ARE THE CLOSEST THINGS THERE ARE. The "distributional twins" claim is not borrowed from the literature here -- it is measured on our own encoder.**

🧠 **THIS IS A MECHANISTIC EXPLANATION FOR THE VERB ZERO, NOT A RESTATEMENT OF IT.** *Verbs are where
opposed pairs concentrate -- `give/receive`, `buy/sell`, `feed/starve 1.49`. **A representation that
places opposites closest cannot score verb similarity above chance, and ours reads `0.0000`.***

## 4. 🔻 **A CORRECTION I OWE, AND I MADE IT TWICE TODAY**

**I wrote in the owner assessment and again in the plan that "the fix is already owned -- `OPPOSED_PAIRS`",
repeating the 2026-08-06 synthesis. I HAD NOT OPENED IT. It is this:**

```
OPPOSED_PAIRS = [("REPAIR_PRESERVE","DAMAGE_LOSE"), ("ARRIVE_SUCCEED","FAIL_LOSE"),
                 ("OPEN_CLASS","CLOSE_CLASS"), ("FILL_CLASS","EMPTY_CLASS"),
                 ("GATHER_CLASS","SCATTER_CLASS"), ("HEAL_CLASS","HARM_CLASS")]
```

***SIX HAND-WRITTEN CLASS PAIRS IN `hdlab/goal_typing.py`. NOT a word-level antonym mechanism, and
nothing that could apply to 3,000 words.*** **So "we own the fix" is materially wrong. What we own is
a 12-class hand-supplied opposition table** -- which is the same hand-supplied categorical tagging the
synthesis criticises elsewhere in its own text.

⚠️ **THE HABIT THAT FAILED: I quoted a claim from a note I trusted, twice, without opening the symbol
it named.** *That is exactly what the fifth prior-work read (`cite_check.py`) exists to prevent, and I
did not run it on this claim.*

## 5. ⚠️ LIMITS

1. **n=96 antonym pairs.** *Enough for a strong effect, not for a small one.*
2. **Control B is only `0.2367`.** *Propagation works but weakly on this verb-heavy test set -- so
   this shows similarity-propagation fails on antonyms while it is ALREADY WEAK, not that a strong
   propagator would also fail.* **That is a real caveat and it cuts against the strength of the claim.**
3. **One dimension (valence) and one benchmark.**
4. **`K=25` still unswept** -- third time deferred.
5. **This does not show opposition-aware propagation WOULD work.** *Nothing here tests a fix.*

## TLDR

Two weeks ago a piece of our own work predicted that spreading word meanings by "what appears in
similar company" must fail for opposites, because opposites appear in almost identical company.
**Tonight I tested it for the first time. It is right.**

Using the benchmark's own labels for which verb pairs are opposites, the true emotional distance
between opposites is nearly twice that between synonyms. **Our system predicts them as very slightly
*closer* than synonyms** — and across every kind of word relationship it predicts almost exactly the
same distance, so it is essentially blind to the difference.

**The direct measurement is the striking part: in our system, opposites are the closest things there
are** — closer than synonyms, closer than unrelated words. That is a mechanical explanation for why we
score exactly nothing on verbs, since verbs are where opposites cluster: *give* and *receive*, *buy*
and *sell*, *feed* and *starve*.

**I also have a correction.** Twice today I told you the fix for this was machinery we already own.
**I hadn't looked at it.** It turns out to be six hand-written pairs of category names — useful for
what it was built for, and nothing that could handle three thousand words. **We do not own the fix.**

**One caveat that genuinely weakens this:** our propagation was already weak on these verbs before
opposites entered the picture, so this shows a weak method failing, not that a strong one would fail
too.

## QUESTIONS

None.

## NEXT STEPS

1. **Strike "the fix is already owned" from the plan and the owner assessment.** *It is wrong in both.*
2. **The honest open question is now sharper: is there ANY text-derived signal that separates
   opposites from synonyms?** *If opposites really are distributional twins, no amount of reading
   fixes it and the anchor must supply polarity directly -- which is what the 08-06 synthesis says the
   brain does.*
3. *Method note: **the prediction was made before the measurement, by other work, and the test was
   built to abort itself two ways.** Both controls passing is what makes this readable rather than
   another suggestive table.*
