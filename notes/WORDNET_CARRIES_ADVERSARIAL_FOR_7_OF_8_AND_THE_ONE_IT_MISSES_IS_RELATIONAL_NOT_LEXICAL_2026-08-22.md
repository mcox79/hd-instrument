# **WORDNET *CAN* SUPPLY THE MISSING `ADVERSARIAL` CLASS -- 7 OF 8 WORDS AT A `0.8%` BASE RATE. THE ONE IT MISSES IS `rival`, AND IT MISSES IT FOR THE RIGHT REASON: A RIVAL IS AN ADVERSARY *RELATIONALLY*, NOT LEXICALLY.**

**This bounds how far the lexical substitution can go, which is the question the open-vocabulary
diagnosis left open.**

---

## 1. THE TEST

*Does any WordNet hypernym marker separate adversarial-role people from ordinary people?*
**Markers:** `adversary, opponent, enemy, wrongdoer, criminal, offender, assailant, unwelcome_person`,
top sense only *(the body-part test established that widening the sense window costs precision and buys
nothing)*.

| | result |
|---|---|
| **ADVERSARIAL words fired** | **7 / 8** -- `enemy`, `thief`, `intruder`, `foe`, `attacker`, `burglar`, `robber` |
| 🔻 **missed** | **`rival`** |
| ordinary people wrongly fired | **1 / 10** -- `stranger` |
| **base rate, 400 random nouns** | **`0.8%`** |

✅ **TWO OF THE THREE WORDS THAT ACTUALLY FAIL ARE COVERED** *(`enemy` in `B`, `thief` in `Bgen`)*.
🔻 **THE THIRD, `rival`, IS NOT.**

## 2. 🔑 **AND `rival` MISSES FOR A PRINCIPLED REASON, NOT A GAP IN THE DATA**

| word | WordNet path | |
|---|---|---|
| `enemy` | `person > **adversary** > enemy` | ✅ adversarial **taxonomically** |
| **`rival`** | `person > **contestant** > rival` | 🔻 *gloss: "the contestant **you hope to defeat**"* |
| `stranger` | `person > traveler > entrant > **intruder** > stranger` | *why it fired; sense 1 is "does not belong here"* |

> ### **WORDNET CLASSIFIES `rival` CORRECTLY. A RIVAL *IS* A CONTESTANT. WHETHER A CONTESTANT IS AN ADVERSARY DEPENDS ON WHOSE SIDE YOU ARE ON -- THE ADVERSARIAL-NESS SITS IN THE GLOSS ("you hope to defeat"), NOT IN THE TAXONOMY.**

***THAT IS NOT A DEFICIENCY IN WORDNET. IT IS THE CONCEPT BEING RELATIONAL.*** **And it is exactly what
both plans of record say needs SITUATION context rather than a lexicon** -- so the residue after the
lexical fix is precisely the part the architecture already claims a lexicon cannot supply.

## 3. 🎯 WHAT THIS BOUNDS

| | |
|---|---|
| can the lexical substitution be completed for `ADVERSARIAL`? | ⚠️ **MOSTLY -- 7/8 at a `0.8%` base rate** |
| would it fix the measured failures? | ✅ `enemy` (2 items in `B`), ✅ `thief` (1 in `Bgen`), 🔻 **NOT `rival` (1 in `Bgen`)** |
| is the residue a data gap or a concept boundary? | ✅ **A CONCEPT BOUNDARY** -- *relational, not lexical* |

⚠️ **`stranger` FIRES AND SHOULD NOT, CONCEPTUALLY.** *It happens to be harmless on this data --
"he attacked the stranger" has gold `BLOCK_HIGH`, so an adversarial override would still answer
correctly -- **but that is luck, not correctness, and I am not counting it as a pass.***

## 4. ⚠️ LIMITS

1. **8 adversarial and 10 ordinary words.** *Enough to show the class exists and to find the residue;
   not a precision certificate.*
2. **Nothing was built or run.** *This says the signal is derivable, not that wiring it helps.*
3. **`0.8%` base rate is measured on random nouns, not on the instrument's vocabulary.**
4. **Top sense only** *(justified by the earlier body-part comparison, not re-derived here).*
5. **The four failing items are 4 of 20 across two subsets.** *Fixing three of four would not by itself
   restore `1.000`.*

## TLDR

The one real defect in the open-vocabulary results is that the stand-in dictionary cannot say "this
person is an adversary". **I checked whether WordNet can supply that, and it mostly can** — it fires for
seven of eight adversarial words and for less than one noun in a hundred overall.

**It misses exactly one: "rival". And the reason is the interesting part.** WordNet files a rival under
*contestant*, which is correct — a rival **is** a contestant. Whether a contestant counts as an
adversary depends on whose side you are on. **The hostility is in the definition ("the contestant you
hope to defeat"), not in the classification.**

**So this is not a hole in the dictionary — it is the concept being about a relationship rather than a
kind of thing.** Which is precisely what both design documents say needs the surrounding situation
rather than a word list. The part a lexicon can supply, it can supply; the part left over is the part
they already predicted a lexicon cannot.

**One caution:** the rule also fires on "stranger", which is not really an adversary. On this data that
happens to give the right answer anyway, but that is luck and I am not counting it.

## QUESTIONS

None.

## NEXT STEPS

1. **The lexical half is now bounded and buildable** *-- `ADVERSARIAL` via WordNet covers `enemy` and
   `thief`; `rival` needs situation context and always would have.*
2. **Nothing here is wired.** *Both this and the body-part rule remain measured-but-unrun.*
3. *Method note: **the word that failed the test is the one that taught me something.** Seven successes
   said "the class exists"; the single miss said where the lexical approach stops, which is the more
   useful half.*
