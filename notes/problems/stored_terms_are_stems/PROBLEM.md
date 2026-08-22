# PROBLEM: ABOUT 8% OF THE TERMS THE SYSTEM STORES ARE CHOPPED-UP WORDS

**slug:** `stored_terms_are_stems` · **opened:** 2026-08-22 by the strategy session
**status:** OPEN · **recommended as the FIRST hand-off -- small, concrete, and it tests the loop**

---

## 1. THE PROBLEM IN PLAIN LANGUAGE

The owner sat down with a scoring sheet of things the system had learned and immediately said:
*"there are a lot of words there that are missing letters."*

They were right. `analysis` is stored as `analysi`. `hypothesis` as `hypothesi`. `cigarette` as
`cigarett`. `heterozygous` as `heterozygou`. **A word with letters missing cannot have a meaning, so
every one of those entries is guaranteed junk -- and they sit in the denominator of every quality
number we have ever quoted about this system.**

**The job: find where the chopping happens, stop it, and show the junk rate drops.**

---

## 2. WHY THIS ONE

- **It is cheap and it is certain.** Unlike most problems here, there is no question about whether
  the defect is real -- you can read it.
- **It contaminates measurement, not just output.** Roughly one in twelve stored terms is unusable
  by construction, which quietly drags down every grounding-quality figure.
- **It is the right first test of the strategy/solver split**: small enough to finish, concrete
  enough that "solved" is unambiguous.

---

## 3. MEASURED vs INFERRED

### MEASURED

| population | not-a-word | **TRUE STEMS** |
|---|---|---|
| the blind scoring sheet (subjects + objects) | `19.5%` | **`10.4%`** |
| `data/foundation/reading_grounding_v2_qualityfix` **subjects** | `17.6%` | **`7.9%`** |
| `data/foundation/reading_grounding_v5_termboundary` **definienda** | `22.5%` | `0.4%` |

**HOW "TRUE STEM" WAS MEASURED -- use this detector, not a looser one.** A token counts as stemmer
output iff **(a)** it is not a word, **AND (b)** appending a plausible suffix makes one
(`analysi`+`s`, `acquaintanc`+`e`). *A round-trip test, so it cannot share a blind spot with the
damage.*

> ### ⚠️ **THE DETECTOR MATTERS MORE THAN IT SOUNDS, AND A CRUDER ONE INVERTS THE ANSWER.**
> The strategy session first used *"not in WordNet"* and reported **`24%`** -- **2.3x overstated**,
> because that bucket also contains real words WordNet lacks (`archaea`, `adipocytes`,
> `acoelomates`, `allopolyploid`, `Abdullah`, `apps`). **Under that cruder detector `v5` -- the
> CLEANEST population -- scores WORST**, because its vocabulary is technical.

**The suffix pattern is a Porter/Snowball signature, not random corruption:** terminal `-s` stripped
off `-sis` and `-ous` (`analysis`, `heterozygous`, `status`), terminal `-e` off `-ette` and off
verbs (`cigarette`, `elongate`, `encode`, `define`, `duplicate`, `luteinize`). **WordNet's `morphy`
CANNOT produce these** -- it returns `None` for a non-lemma and callers fall back to the original.
**So something else is doing it.**

### INFERRED -- overturn any of this freely

- *That the responsible call is a Porter/Snowball stemmer.* **Strongly suggested by the suffix
  pattern; NOT located.** A grep for `PorterStemmer|SnowballStemmer|\.stem\(` across `hdlab/`
  returned **one hit, and it is a COMMENT** about `lemma_verb` producing `damag`. **The live path
  may be doing this somewhere the obvious grep does not reach** -- which is why this is a problem
  and not a one-line fix.
- *That fixing it improves grounding quality.* **Untested.** It removes guaranteed-junk entries; it
  does not follow that what remains is better.

---

## 4. ALREADY TRIED -- AND ONE TRAP THAT COST THE STRATEGY SESSION THREE HOURS

- 🔻 **"The fix already shipped in v5" -- WITHDRAWN, and do not repeat it.** The `0.4%` is
  **definitional extraction's DEFINIENDA**; the `7.9%` is **the grounding loop's SUBJECTS**.
  **Different pipelines, different populations.** The charter's `16.1% -> 1.0%` term-boundary fix is
  about definitional extraction's TERM BOUNDARIES, not the grounding loop's lemmatisation.
  **All nine foundation directories were written on the same day (2026-08-12); `v3`/`v4`/`v5` are
  not later versions of `v2q`, they are a different pipeline's output.**
- **A verb-lemmatizer repair DID land 2026-08-13** (`7d6036bca`): non-word stems `8,692 -> 0`, gold
  verb inflection `53.50% -> 99.03%`. **That was VERBS.** The blind sheet's damage is largely NOUNS
  (`analysi`, `apoptosi`, `cigarett`). *Check whether that repair covers nouns; it may be the same
  bug in an uncovered part of speech, which would make this much cheaper.*
- **The charter already records the symptom as a COUNTING artifact** -- *"121 stem/full-form pairs
  (`cigarett`/`cigarette`) counted as two concepts"*. **It is not a counting artifact; it is
  non-words in the store.** That reframing is the finding, and it was sitting there.

---

## 5. VERIFY BEFORE YOU START -- THE DISK OUTRANKS THIS BRIEF

```bash
python tools/before_you_start.py "find and fix the stemmer corrupting stored terms"
python tools/experiment_index.py query "lemmatizer"
python tools/experiment_index.py query "stem"
python tools/symbol_corrections.py lemma_word     # and lemma_verb
```
**Re-measure the `7.9%` yourself before you start** -- if it does not reproduce, that is the finding
and you should stop and say so.

---

## 6. THE BAR

1. **NAME THE CALL.** Point at the specific line that emits `analysi`. *"Somewhere in the pipeline"
   is not an answer.* **Prefer runtime evidence over grep** -- this project has been wrong in both
   directions on exactly this kind of question, twice today.
2. **FIX IT** so a word that is not a lemma is left ALONE rather than truncated.
3. **SHOW THE DROP** on a freshly built store: the true-stem rate on the SAME population, with the
   SAME round-trip detector, before and after.
4. **PROVE YOU DID NOT BREAK LEMMATISATION.** The system genuinely needs `dogs -> dog`. A fix that
   stops all normalisation would "solve" this and be much worse. **Report inflection accuracy
   before and after against the same gold the 2026-08-13 repair used (`53.50% -> 99.03%`).**

### HOW WE WOULD KNOW IT FAILED
- **(a)** The stem rate does not drop -> you fixed the wrong call.
- **(b)** It drops but inflection accuracy drops too -> you disabled normalisation; that is worse
  than the defect.
- **(c)** You cannot reproduce the `7.9%` -> the brief is stale; **say so, that is a real result.**
- **(d)** The stems come from the CORPUS rather than our code -> then it is a data-cleaning problem
  and the brief is misaimed. **Check this early; it is cheap.**

---

## 7. FILES AND ENTRY POINTS

- **The store with the damage:** `data/foundation/reading_grounding_v2_qualityfix/store/store_facts.json`
- **The live grounding path:** `hdlab/reading_grounding_loop.py`
- **The lemmatiser(s):** `lemma_word` / `lemma_verb` -- and note `hdlab/goal_typing.py:1673` carries
  a comment about `lemma_verb("damaged") == "damag"`, which is the same shape of damage
- **The detector:** re-implement the round-trip test in §3; do not reuse a "not in WordNet" check
- **🚫 DO NOT TOUCH:** `preregs/**`, `arm_key*`, `notes/STATUS.md`, the build plan, other problem
  folders. **`data/foundation/` is READ-ONLY, one disk, no backup -- build a NEW store, never
  overwrite one.**

---

## 8. DO NOT QUOTE / DO NOT REDO

- 🚫 **Do not quote `24%`.** It is the strategy session's retracted first number.
- 🚫 **Do not put the `7.9%` and the `0.4%` side by side as before/after.** Different pipelines.
- 🚫 **Do not conclude "already fixed" from the v5 numbers.** That inference was made and withdrawn.
- ⚠️ **Do not re-run the 2026-08-13 verb repair.** It landed. Check whether it covers nouns instead.
