# **THE ONE BUG THE SOURCE DOCUMENTS BY NAME HAS A CEILING OF `0.6111` AGAINST A FLOOR OF `0.6389`. FIXING IT PERFECTLY STILL FAILS. THE CASCADE ABSTAINS ON `44%` OF ITEMS AND THAT IS THE ONLY LEVER BIG ENOUGH.**

**Yesterday's diagnosis said the wall is an `UNMET` bias in the base predictor. This decomposes that
bias by TIER and then asks the only question that matters before building: CAN IT REACH THE BAR?**

---

## 1. WHERE THE 36 ITEMS ARE DECIDED

*Read straight out of `per_item_predictions` + `reason`, which now ship. No new run.*

| gold | pred | n | deciding tier |
|---|---|---|---|
| MET | ✅ MET | 7 | `same_class_same_referent` |
| MET | 🔻 UNMET | **5** | `abstain_fallback_to_lexicon` |
| MET | 🔻 UNMET | **5** | `referent_mismatch` |
| MET | 🔻 AMBIGUOUS | 2 | `abstain_fallback_to_lexicon` |
| MET | 🔻 UNMET | 2 | `opposed_class_same_referent` |
| MET | 🔻 NONE | 1 | `abstain_fallback_to_lexicon` |
| MET | ✅ MET | 1 | `abstain_fallback_to_lexicon` |
| UNMET | ✅ UNMET | 5 | `abstain_fallback_to_lexicon` |
| UNMET | ✅ UNMET | 3 | `referent_mismatch` |
| UNMET | 🔻 MET | 2 | `same_class_same_referent` |
| UNMET | 🔻 NONE | 2 | `abstain_fallback_to_lexicon` |
| UNMET | ✅ UNMET | 1 | `grounded_result_class` |

**`referent_mismatch` returns `UNMET` in 8 of 8 cases.** *It is not inferring a bad outcome; it is
DEFAULTING to one whenever it cannot work out whose outcome this is.* ***And the source already knows:
`hdlab/goal_typing.py:2151` documents the exact failure -- "fails the referent link (the subject-scan
picks up the stray adverb 'kindly', not 'the gardener') -> 'referent_mismatch' -> a confident but WRONG
UNMET (gold MET)".***

## 2. 🔑 **AND THAT DOCUMENTED BUG CANNOT CLEAR THE BAR. CEILING ARITHMETIC, BEFORE ANY BUILD.**

*Each row asks: if THIS TIER WERE PERFECT and nothing else changed, what is the best achievable score?
A generous upper bound by construction.*

| tier | n | wrong | **ceiling** | vs floor `0.6389` |
|---|---|---|---|---|
| **`abstain_fallback_to_lexicon`** | **16** | **10** | ✅ **`0.7500`** | **CLEARS** |
| `referent_mismatch` | 8 | 5 | 🔻 **`0.6111`** | **BELOW -- fails even if perfect** |
| `same_class_same_referent` | 9 | 2 | `0.5278` | below |
| `opposed_class_same_referent` | 2 | 2 | `0.5278` | below |
| `grounded_result_class` | 1 | 0 | `0.4722` | below |

> # **THE SATISFYING BUG -- NAMED IN THE SOURCE, WITH A WORKED EXAMPLE, MECHANISTIC, OBVIOUSLY WRONG -- IS PROVABLY INSUFFICIENT. IT HAS FIVE ITEMS BEHIND IT AND THE GAP NEEDS SEVEN.**

**The only single lever with enough mass is the unglamorous one: `16 of 36` items (`44%`) never get a
structural verdict at all.** *The goal-congruence cascade -- four tiers deep, each one a documented
build -- ABSTAINS on nearly half the eval, and a goal-independent word lexicon guesses instead.*

## 3. WHAT THIS CHANGES

| | |
|---|---|
| 🔻 **do NOT start with the referent-link repair** | *it is the most attractive target on the page and it mathematically cannot clear the floor alone* |
| ✅ **the question worth asking** | **why does a four-tier structural cascade abstain on 44% of a bank built for it?** |
| ⚠️ **and note what "fixing" the fallback means** | *the lexicon is not broken -- it is a GUESS being asked to stand in for a structural verdict that never arrived. The repair is upstream: make the cascade FIRE, not make the guess better.* |

## 4. ⚠️ LIMITS

1. **n=36. `referent_mismatch` has 5 wrong items; `0.6111` vs `0.6389` is ONE ITEM of separation.**
   The ranking is robust (16 items vs 8); the exact ceilings are not.
2. **Ceilings assume tiers are independent.** Fixing the cascade's abstentions would remove items FROM
   the fallback tier, so these are not additive. *Combinations do clear -- `referent_mismatch` +
   `same_class` + `opposed_class` = `0.7222` -- but no other tier clears ALONE.*
3. **"Perfect tier" is an upper bound, not a plan.** Nothing here says the abstentions are fixable.
4. **This is one eval bank.** The 44% abstention rate is a property of the cascade ON THIS BANK.

## TLDR

The system decides whether a story's goal was achieved by running through four increasingly clever
checks, and if none of them can tell, it falls back to guessing from a word list.

I traced all 36 test questions to whichever check actually decided them. **There is an obvious villain:
when the system can't work out *whose* outcome it is looking at, it confidently answers "it went badly"
— every single time, 8 times out of 8. It is wrong on 5 of those.** The source code even documents this
exact mistake, with a worked example.

**Then I checked whether fixing it would be enough, and it wouldn't.** Even if that check were made
perfect tomorrow, the score reaches about 61 out of 100 — and the "just guess the common answer"
baseline we have to beat is 64. **The obvious villain has five questions behind it and we need seven.**

**The thing that is big enough is far less interesting: on 16 of the 36 questions — nearly half — none
of the four clever checks reaches a verdict at all**, and the word-list guess answers instead. That is
the only single place with enough questions behind it to get us over the line.

**And the repair there is not "make the guess smarter."** The guess is a stand-in for an answer that
never arrived. The real question is why four purpose-built checks go silent on half the very test they
were built for. **That is now the only lead I would spend time on.**

## QUESTIONS

None.

## NEXT STEPS

1. 🎯 **Ask why the cascade abstains on 16 of 36** -- which tier abstains first, and on what property of
   the passage. *The per-item `reason` says "fell through"; it does not say WHICH tier declined and why.
   That needs the tier-by-tier verdicts, which are not currently persisted -- the same "save what you
   scored" gap, one level deeper.*
2. 🚫 **Do not repair `referent_mismatch` yet**, despite it being documented, mechanistic and clearly
   wrong. *It cannot clear the floor alone. It becomes worth doing AFTER the abstention rate falls, when
   its 5 items might matter at the margin.*
3. *Method note: **the ceiling calculation took four minutes and redirected the work away from the most
   attractive target on the page.** Asking "can this reach the bar?" before "how do I fix it?" is the
   habit that keeps paying today.*
