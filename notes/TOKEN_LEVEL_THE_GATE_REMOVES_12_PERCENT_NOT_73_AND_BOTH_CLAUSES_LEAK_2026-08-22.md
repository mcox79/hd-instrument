# **AT TOKEN LEVEL THE VERB-SENSE GATE WOULD REMOVE `12.2%` OF ADMITTED TOKENS, NOT THE `73%` I HAD BEEN QUOTING AT TYPE LEVEL. THE TYPES/TOKENS GAP I FLAGGED THREE TIMES MATTERED, AND IT SHRINKS MY CLAIM.**

**First token-level measurement in this thread, on the same four corpora the cell used.**

---

## 1. THE MEASUREMENT -- `412,446` TOKENS

| | |
|---|---|
| tokens admitted by current `_is_verblike` | **`70,141` (17.0% of all tokens)** |
| of those, **HAVE** a WordNet verb sense | ✅ **`61,549` (87.8%)** |
| of those, **NO** verb sense -- the gate would remove | 🔻 **`8,592` (12.2%)** |

> ### 🔻 **`12.2%`, NOT `73%`. AT TYPE LEVEL `73%` OF THE *ERROR LEMMAS* WERE NON-VERBS; AT TOKEN LEVEL ONLY `12.2%` OF *ADMITTED TOKENS* ARE. THE ERROR TYPES ARE A LONG TAIL OF RARE JUNK; THE TOKEN MASS IS DOMINATED BY REAL VERBS.**

***I flagged the types/tokens gap three times and refused to project a number across it. That refusal
was correct: the two differ by a factor of six.***

## 2. 🔑 **AND THE REMOVED TOKENS EXPOSE *BOTH* CLAUSES LEAKING -- INCLUDING THE ONE I HAD NOT EXAMINED**

*Most frequent removals:*

| clause of `_is_verblike` | what it lets through |
|---|---|
| **`endswith("ing")`** ← *I flagged this as UNEXAMINED last turn* | `something` **359**, `thing` **331**, `anything` **316**, `nothing` **291**, `morning` **201**, `everything` **181** |
| **`endswith("ed")`** | `red` **166**, `wicked` **121** |
| **`lemma_verb(tok) != tok`** *(the plural-noun path)* | `girls` **388**, `boys` **274**, `children` **174**, `friends` **150**, `others` **92** |

**The `-ing` clause is the single largest source** *-- and it is admitting pronouns and quantifiers
(`something`/`anything`/`nothing`/`everything`), not just nouns.* ***`red` and `wicked` are adjectives
admitted for ending in `-ed`.***

## 3. 🎯 WHAT THE GATE WOULD ACTUALLY BUY

✅ **It is a PURE FILTER: it can only remove, never add.** *So it cannot break anything `_is_verblike`
already rejects -- including the base-form verbs (`praise`) it wrongly rejects today. **The gate does
NOT fix that direction, contrary to what I said last turn.***

⚠️ **CORRECTION TO MYSELF: I claimed a verb-sense gate "fixes both directions". IT DOES NOT.** *It fixes
over-admission only. Under-admission of base-form verbs needs a separate change to the test itself.*

**Ceiling on the benefit: `12.2%` of admitted tokens.** *Whether that moves attribution precision
depends on how those tokens distribute across credit windows, which I have not measured.*

## 4. ⚠️ LIMITS

1. **The `8,592` removals are audited only at the top 15.** *All fifteen are clearly non-verbs; the tail
   is unaudited and will contain some real verbs whose lemma lacks a WordNet verb sense.*
2. **Token counts over the raw corpora, not over credit windows.** *Credit only happens inside
   goal-linked windows, so the in-window rate could differ.*
3. **This measures the FILTER, not its effect on attribution precision** *-- that still needs the cell.*
4. **WordNet is the arbiter of "is a verb"**, *with the usual coverage caveat.*

## TLDR

I have been saying about three quarters of the credit mistakes are not verbs. **Measured properly, on
actual words in actual books rather than on the list of distinct mistake-names, it is one in eight.**

The difference is that the junk is a long tail of many rare words, while the bulk of what gets picked up
is ordinary verbs. **I flagged this gap three times and refused to guess across it. That was right — the
two numbers differ sixfold.**

**The measurement did surface something new, though.** The biggest single leak is the rule that treats
anything ending in "-ing" as a verb: *something, anything, nothing, everything, morning* — none of them
verbs, and together the most frequent mistakes in the whole set. The "-ed" half lets through *red* and
*wicked*. I had flagged that clause as unexamined last turn; it turns out to be the largest source.

**And I have to correct myself again.** I said a dictionary check would fix the problem in both
directions. **It cannot** — it only ever removes candidates, so it does nothing about genuine verbs like
*praise* being wrongly rejected. That needs a different change.

## QUESTIONS

None.

## NEXT STEPS

1. **The honest ceiling for this fix is `12.2%` of admitted tokens** *-- worth doing, but not the
   transformation "73%" implied, and I should stop quoting that figure without its unit.*
2. **The `-ing` clause is the largest single leak and is trivially narrowable** *(exclude the closed
   class `something/anything/nothing/everything`, or require a verb sense) -- measure, do not assume.*
3. **Under-admission of base-form verbs remains unaddressed** *by anything proposed in this thread.*
4. *Method note: **three turns of refusing to project across types and tokens were vindicated in one
   measurement.** The gap was a factor of six, and in the direction that shrinks the claim.*
