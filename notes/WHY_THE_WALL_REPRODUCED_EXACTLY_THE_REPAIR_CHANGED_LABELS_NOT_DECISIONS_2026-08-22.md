# **WHY THE WALL REPRODUCED TO FOUR DIGITS: THE LEMMATIZER REPAIR CHANGED WHAT THE CREDITED TOKENS ARE *CALLED*, NOT *WHICH TOKENS GET CREDITED*. `babies` WAS CREDITED AS `babi`; IT IS NOW CREDITED AS `baby`.**

**A complete mechanical explanation for an exact reproduction, and it settles the sharpened cell
without re-running it.**

---

## 1. THE INVARIANT HOLDS -- VERIFIED, NOT QUOTED

*`lemma_verb` run over **6,000 forms** (4,000 random WordNet lemmas + 2,000 plural forms):*

> ### ✅ **`0` NON-WORD OUTPUTS. The "GUARANTEED never to return a non-word" claim is empirically true today.**

**So the `89 / 173` non-word error lemmas (`babi`, `capaciou`, `alway`, `admir`) are STRUCTURALLY
IMPOSSIBLE now.** *That much of my last-turn projection was right.*

## 2. 🔑 **BUT THEY DID NOT VANISH -- THEY WERE RENAMED, AND THE DECISION IS UNCHANGED**

*`_is_verblike(tok)` fires on **the surface form**, before any lemma is stored:*

```python
lemma_verb(tok) != tok  or  tok.endswith(("ed","ing"))
```

| surface | OLD lemma | NEW lemma | admitted? |
|---|---|---|---|
| `babies` | `babi` *(non-word)* | `baby` *(clean)* | 🔻 **True, both** |
| `ladies` / `stories` / `duties` / `families` | *stems* | `lady` / `story` / `duty` / `family` | 🔻 **True, both** |
| `boys` / `friends` / `lessons` | `boy` / `friend` / `lesson` | *unchanged* | 🔻 **True, both** |

**`8 / 8` plural nouns still admitted.**

> # 🔑 **THE REPAIR FIXED THE *NAME* OF THE MISTAKE, NOT THE MISTAKE. THE SAME TOKENS ARE CREDITED, WITH LEGIBLE LABELS.**

***THAT IS WHY `primary = 0.4722` REPRODUCED IDENTICALLY TO FOUR DIGITS.*** *An exact reproduction across
fifteen days and two lemmatizers is not a coincidence -- it is what you get when the changed component
does not touch the decision path.*

## 3. ✅ **AND IT SETTLES THE SHARPENED CELL WITHOUT RE-RUNNING IT**

*That cell HAS a `units.jsonl` and would replay; forcing a recompute needs a deletion or a harness
change, neither of which I will do unilaterally.* **It does not need one:**

- **`77` of the `84` real-word error lemmas are STILL admitted by today's `_is_verblike`** -- *`boy`,
  `amusement`, `carry`, `come`, `do`, `bring`.*
- **the `89` non-word ones become clean nouns that are ALSO still admitted** *(section 2)*.

***SO THE POST-REPAIR ERROR SET IS THE SAME SET WITH BETTER SPELLING. THE `0.4676` PRECISION AND THE
"73% ARE NOT VERBS" ANALYSIS DO NOT CHANGE IN SUBSTANCE -- ONLY THE 52%/21% SPLIT DOES, BECAUSE THE
NON-WORDS BECOME NOUNS.***

**Restated post-repair: `~73%` of error types are NOUNS AND NON-VERBS, essentially all of them nouns.**

## 4. ⚠️ LIMITS

1. **TYPES, NOT TOKENS -- still.** *No projected precision, for the third time.*
2. **The 6,000-form invariant check samples WordNet lemmas and plurals**, *not the actual corpus token
   stream.*
3. **I did NOT re-run the sharpened cell.** *This is an argument from the decision path plus a verified
   invariant, not a measurement of that cell.*
4. **`_is_verblike`'s second clause (`-ed`/`-ing`) is untouched by any of this** *and admits gerund
   nouns (`building`, `feeling`) -- unmeasured here.*

## TLDR

The wall reproducing to four decimal places looked surprising. **It is not: the repair renamed the
mistakes without changing them.**

The test for "is this a verb?" looks at the word *as it appears in the text*, before anything is
cleaned up. "Babies" was being wrongly treated as a verb before the repair and is still wrongly treated
as a verb now — **the only difference is that it used to be filed under the nonsense word "babi" and is
now filed under "baby".** Same mistake, tidier label.

**I checked the repair's own guarantee rather than trusting it:** across six thousand words it never
once produced a non-word. That part is genuinely fixed. **But eight out of eight plural nouns are still
treated as verbs.**

**This also settles the second experiment without running it.** Seventy-seven of the eighty-four
real-word mistakes are still admitted today, and the nonsense ones simply become tidy nouns that are
also still admitted. **So its numbers would not meaningfully move** — which is consistent with the first
experiment reproducing exactly.

## QUESTIONS

None.

## NEXT STEPS

1. **The one-line defect is now fully characterised and unrepaired:** *`_is_verblike` admits every plural
   noun and rejects base-form verbs. A WordNet verb-sense gate fixes both directions.* ⚠️ *Must be
   measured -- and the types/tokens gap means I still cannot predict the gain.*
2. **The `-ed`/`-ing` clause is unexamined** *and would admit `building`/`feeling` as verbs.*
3. *Method note: **an exact reproduction is evidence about the decision path, not just about the
   result.** Four identical digits across two lemmatizers said the changed component was not on that
   path, and checking why explained both runs at once.*
