# **THE VERB DETECTOR'S TEST IS "THE LEMMATIZER CHANGED THE WORD" -- WHICH *EVERY PLURAL NOUN* SATISFIES. CONFIRMED LIVE: `7 / 10` PLURAL NOUNS ARE ADMITTED AS VERB-LIKE.**

**The mechanism behind the credit-assignment errors, located in one line and confirmed by running it.**

---

## 1. THE ONE LINE

```python
def _is_verblike(tok: str) -> bool:
    return lemma_verb(tok) != tok or tok.endswith(("ed", "ing"))
```

***"THE LEMMATIZER CHANGED THE SURFACE FORM" IS THE PRIMARY TEST. Pluralisation changes the surface
form. So every plural noun passes.***

## 2. ✅ CONFIRMED BY RUNNING IT TODAY

| token | `lemma_verb` | changed? | verb-like? |
|---|---|---|---|
| `boys` | `boy` | yes | 🔻 **True** |
| `friends` | `friend` | yes | 🔻 **True** |
| `babies` | `baby` | yes | 🔻 **True** |
| `amusements` | `amusement` | yes | 🔻 **True** |
| `explanations` | `explanation` | yes | 🔻 **True** |
| `lovers` / `lessons` | `lover` / `lesson` | yes | 🔻 **True** |
| `praise` *(real base-form verb)* | `praise` | no | ⚠️ **False -- MISSED** |
| `wept` *(irregular)* | `weep` | yes | ✅ True |

> ### **`7 / 10` PLURAL NOUNS AND ADJECTIVES ADMITTED. AND THE ERROR LIST FROM THE CELL READS EXACTLY LIKE THAT: `boy`, `friend`, `amusement`, `explanation`, `lover`, `lesson`.**

## 3. ⚠️ **THE DOCSTRING IS WRONG IN TWO PLACES, MEASURED**

*It claims:*

> *"Excludes function words / determiners / **bare nouns** (the/and/nell)"*

**It excludes SINGULAR nouns. It admits PLURAL ones -- and says nothing about that.** *The precision
cost is invisible in the docstring while the recall cost is stated at length.*

> *"a rare base-form or non-lemmatized irregular verb with no -ed/-ing (e.g. bare 'praise', irregular
> **'wept'**) is missed"*

✅ *`praise` IS missed -- that half is accurate.* 🔻 **`wept` is NOT missed today: `wept -> weep` changes
the form, so it passes.** *Half the stated example is stale.*

## 4. 🔻 **AND A DISCREPANCY I MUST FLAG RATHER THAN PAPER OVER**

***The cell's error list contains `babi`, `alway`, `capaciou`, `admir`, `behav`. Today's `lemma_verb`
returns `baby`, `always`, `capacious`, `admiration`, `behaviour` -- CLEAN.***

**So the broken-stem garbage is NOT reproduced by the current lemmatizer.** *Either the stemmer changed
after that cell ran, or the cell reached a different code path.* ⚠️ **THAT SPLITS MY PREVIOUS
"73% ARE NOT VERBS" FINDING:**

| | |
|---|---|
| **NOUNS admitted (21% of error types)** | ✅ **CONFIRMED LIVE TODAY** |
| **broken stems (52% of error types)** | ⚠️ **NOT REPRODUCED TODAY -- possibly historical** |

***I should not claim the 52% is a current defect until I know which lemmatizer produced it.***

## 5. ⚠️ LIMITS

1. **10 hand-chosen tokens.** *Enough to demonstrate the mechanism, not a rate.*
2. **The stemmer discrepancy (section 4) is unresolved** -- *I did not trace which `lemma_verb`
   the cell used.*
3. **Nothing is fixed.**
4. **The types/tokens caveat still stands** *-- these are word types, not occurrences.*

## TLDR

I found the exact line behind the credit-assignment errors, and it is one line.

**The test for "is this a verb?" is "did the lemmatizer change the word?"** — and turning a plural into a
singular changes the word. **So every plural noun is treated as a verb.** I ran it: *boys, friends,
babies, amusements, explanations, lovers, lessons* — all pass as verbs. Those are exactly the words the
experiment was wrongly crediting.

**Meanwhile a real verb in its plain form — "praise" — is rejected**, because nothing about it changes.
So the test is backwards in both directions at once.

**The function's own description says it excludes bare nouns.** It excludes *singular* nouns and says
nothing about plurals, and the recall cost is described at length while this precision cost is not
mentioned at all.

**One thing I have to flag rather than smooth over.** The old error list also contained mangled
fragments like *babi* and *capaciou*, and today's lemmatizer does not produce those — it returns *baby*
and *capacious* cleanly. **So that half of the problem may already be gone**, and I should not keep
quoting it as current until I know which version produced it.

## QUESTIONS

None.

## NEXT STEPS

1. **The plural-noun admission is a confirmed live defect with a one-line cause** *-- and a WordNet
   verb-sense gate would reject `boy`/`friend`/`lesson` while keeping `praise`, fixing BOTH directions.*
   ⚠️ *Must be measured, not assumed.*
2. **Resolve the stemmer discrepancy before quoting the 52%** *-- it may be a fixed historical fault.*
3. *Method note: **the docstring described the recall cost honestly and was silent on the precision
   cost.** Reading it would not have found this; running it did.*
