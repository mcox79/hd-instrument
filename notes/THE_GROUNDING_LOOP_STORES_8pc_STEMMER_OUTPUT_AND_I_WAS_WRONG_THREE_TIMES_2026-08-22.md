# **THE GROUNDING LOOP STORES ~8% STEMMER OUTPUT. I HAVE NOW BEEN WRONG ABOUT THIS THREE TIMES IN ONE DAY, IN ALTERNATING DIRECTIONS.**

> ## 🔻🔻🔻 **CORRECTION 3, AND IT LARGELY REINSTATES THE ORIGINAL FINDING. READ THIS FIRST; EVERYTHING BELOW IS THE TRAIL.**
> **The measured numbers never moved. My interpretation of them moved three times.** Here is the
> separation of MEASURED from INFERRED, which is what I should have written at the start.
>
> **MEASURED, and all of it still stands:**
> - the blind sheet carries **`10.4%`** true stems (round-trip detector)
> - `reading_grounding_v2_qualityfix` subjects carry **`7.9%`**
> - `reading_grounding_v5_termboundary` definienda carry **`0.4%`**
> - **all nine foundation directories were written on `2026-08-12` -- the SAME DAY**
> - **only `v1` and `v2_qualityfix` are LOADABLE.** `v3`/`v4`/`v5` are missing ALL FOUR artifacts
>   `load_foundation` requires (`store/`, `concept_space.npz`, `library_pending.json`,
>   `manifest.json`)
>
> **WHAT I INFERRED AND MUST WITHDRAW:**
> 1. 🔻 **"We hand-scored a THREE-VERSIONS-STALE foundation." WITHDRAWN.** They are all one day old.
>    **`v3`/`v4`/`v5` are not later versions of `v2q` -- they are a DIFFERENT PIPELINE's output**
>    (definitional extraction fact-dumps, not resumable reading-loop states). *`v2q` is the correct
>    artifact for the question the sheet asked -- "did the grounding loop learn a meaning" -- and
>    sampling it was right.*
> 2. 🔻 **"The stem fix already shipped, so `fix the stemmer` is withdrawn." WITHDRAWN IN TURN.**
>    The `0.4%` is definitional extraction's DEFINIENDA; the `7.9%` is the grounding loop's
>    SUBJECTS. **Different pipelines, different populations -- the no-number-crosses-populations
>    rule, which I invoked twice today and then broke here.** The charter's `16.1% -> 1.0%`
>    term-boundary fix is about definitional extraction's TERM BOUNDARIES, **not the grounding
>    loop's lemmatisation.**
>
> ➡️ **SO: THE GROUNDING LOOP'S ~`8%` STEM RATE IS REAL AND IS *NOT* KNOWN TO BE FIXED.** *My
> original reaction was closer to right than my correction was; I over-corrected on a
> cross-population comparison.* **What genuinely survives from correction 1 is only the `24% -> 10.4%`
> deflation, which was a real detector defect.**
>
> *Recording all three swings rather than a clean final answer, because the pattern is the finding:
> **the measurements were stable all day and my story about them was not.***

---

# ~~24% OF THE FOUNDATION'S SUBJECT TERMS ARE NOT WORDS~~ -- **the original headline and its first two corrections, kept for the trail**

**Found by the OWNER, by hand, on the first blind sheet anyone actually sat down with.** Their
words: *"there are a lot of words there that are missing letters, and a lot of them unrelated."*
**The observation is correct and it found something real -- but not what I first said it was.**

> ## 🔻 **CORRECTION 1 -- MY `24%` DETECTOR CONFLATED TWO CAUSES AND OVERSTATED BY 2.3x.**
> I counted "not in WordNet" as "not a word". **That bucket contains genuine words WordNet simply
> lacks** -- `archaea`, `adipocytes`, `acoelomates`, `allopolyploid`, `Abdullah`, `apps` -- alongside
> real stemmer output. **Rebuilt as a ROUND-TRIP test** (a token is stemmer output iff it is NOT a
> word AND appending a plausible suffix makes one -- `analysi`+`s`, `acquaintanc`+`e`), which cannot
> share a blind spot with the damage:
>
> | population | not-a-word | **TRUE STEMS** |
> |---|---|---|
> | the blind sheet (subjects + objects) | `19.5%` | **`10.4%`** |
> | `reading_grounding_v2_qualityfix` subjects | `17.6%` | **`7.9%`** |
> | **`reading_grounding_v5_termboundary`** | `22.5%` | 🟢 **`0.4%`** |
>
> *Note the trap in that last row: v5 has the HIGHEST not-a-word rate and the LOWEST stem rate,
> because its vocabulary is technical and WordNet's coverage of it is poor. **A cruder detector would
> have scored the FIXED foundation as the worst one.***

> ## 🔻 **CORRECTION 2, AND IT RETIRES MY OWN TOP RECOMMENDATION: THE STEMMER IS ALREADY FIXED.**
> **`v5_termboundary` reads `0.4%` against v2q's `7.9%` -- a ~20x reduction**, and the charter
> already recorded it: *"the v5 term-boundary fix (term corruption `16.1% -> 1.0%`)"*.
> ➡️ **I told the owner an hour ago that "fix the stemmer" was step 1. THAT IS WITHDRAWN. It shipped
> weeks ago.**
> 🎯 **THE REAL DEFECT IS PROVENANCE: `tools/draw_representative_blind_sample.py` DREW FROM
> `v2_qualityfix` WHILE `v3_definitional`, `v4_parsefix` AND `v5_termboundary` ALL EXIST ON DISK.**
> **We asked the owner to spend twenty minutes hand-scoring a foundation three versions out of date.**
> ⚠️ **NOT YET ESTABLISHED, AND IT MATTERS: v5 is a DIFFERENT ARTIFACT SHAPE** -- a single
> `definitional_facts_v5.jsonl`, where v2q has a full `store/` with `concept_space`, provenance and
> refusals. **So "just sample v5 instead" may not be a straight swap, and I am NOT claiming v5 is the
> current live foundation.** *Which foundation the live loop actually writes is the next thing to
> establish, and it is cheap.*

---

## 1. THE MEASUREMENT

`data/blind_samples/representative_reading_grounding_v2q_full_2_n150/blind_sheet.txt`, 150 pairs,
checked against WordNet:

| | not an English word |
|---|---|
| **SUBJECT terms** | **`36/150` = `24.0%`** |
| **OBJECT terms** | **`25/150` = `16.7%`** |

**THE PATTERN IS A PORTER/SNOWBALL SIGNATURE, NOT RANDOM CORRUPTION** -- terminal `-s` stripped off
`-sis` (`analysis -> analysi`, `hypothesis -> hypothesi`, `apoptosis -> apoptosi`), off `-ous`
(`heterozygous -> heterozygou`, `indigenous -> indigenou`, `marvellous -> marvellou`) and off
`status -> statu`; terminal `-e` off `-ette` (`cigarette -> cigarett`) and off verbs
(`elongate -> elongat`, `encode -> encod`, `define -> defin`, `duplicate -> duplicat`,
`luteinize -> luteiniz`).

> # **WE ASKED A HUMAN WHETHER *"`hypothesi` -> `new`"* IS A MEANINGFUL GROUNDING. A QUARTER OF THE SHEET IS UNSCOREABLE BY CONSTRUCTION.**

## 2. 🔻 IT WAS ALREADY ON DISK AS A SMALLER NUMBER, AND NOBODY FOLLOWED IT

`SUBSTRATE_CHARTER_read_first.md`'s own 2026-08-18 correction says: *"121 stem/full-form pairs
(`cigarett` / `cigarette`) are counted as two concepts."* **That was filed as a COUNTING artifact
inflating a concept total. It is not a counting artifact. It is the store holding non-words**, and
at `24%` of subjects it is a first-order property of the foundation, not a rounding note.

*Same shape as this project's recurring fault: the number travelled, the meaning of the number did
not, and it took a human reading the actual rows to see what it was.*

## 3. WHAT IT COSTS, AND IT IS NOT ONLY THE SHEET

- **Every grounding-quality measurement inherits it.** The blind `3/19/78`, the proxy pass rates,
  the `v4` proximity criterion -- all scored over a population where a quarter of the subjects are
  not words. **A non-word cannot have a meaning, so those items are guaranteed NOISE**, and they
  are sitting in the denominator of every quality figure this project has quoted.
- **It corrupts matching.** `analysi` and `analysis` are two concepts; a lookup for either finds
  half the evidence. **The `_prefix_covers` guard in `quality_proxy` exists to stop `com -> company`
  -- the same hazard, caught at the proxy and never at the source.**
- **It hits technical vocabulary hardest** -- `-sis`, `-ous`, `-ize`, `-ate` endings are exactly
  scientific register, which is the register the project measured as its BEST grounding source
  (`textbook 12.6%` vs `Sherlock 0.7%`). **The defect is concentrated where the value is.**

## 4. ⚠️ WHAT IS NOT YET ESTABLISHED

- **WHERE the stemming happens is NOT identified in this note.** The pipeline has both a real
  lemmatizer (`lemma_word`, WordNet morphy) and, historically, stem-shaped output; the 08-13 repair
  took gold verb-inflection `53.50% -> 99.03%` and non-word stems `8,692 -> 0` **for verbs**. This
  sheet is drawn from a `v2q` foundation and shows the defect alive on NOUNS. **Naming the
  responsible call is the next step and it is cheap.**
- **The `24%` is for THIS sample.** It was drawn uniformly at random from the `v2q` foundation with
  a measured drift of `0.0584`, so it should generalise to that foundation -- but it has not been
  recomputed foundation-wide.
- **The owner's partial labels** (`75` of `150` annotated: `1` MEANINGFUL, `15` RELATED, `31`
  NOISE, `28` comments) are broadly consistent with the earlier blind `3/19/78`. **They are NOT a
  clean replication** -- different sample, partially annotated, and the owner reasonably wrote
  commentary rather than a bare label on many rows.

---

## TLDR

The owner sat down with our scoring sheet and noticed lots of the words were missing letters. They
were right, and chasing it found something better than what I first reported.

My first pass said a quarter of the terms were broken. That was wrong by more than double -- I had
counted perfectly good words that our dictionary just doesn't list (`archaea`, `adipocytes`,
someone's surname) as if they were broken. The real figure is about one in ten.

And the broken ones are already fixed. A newer version of the same knowledge base has almost none
of them -- one in two hundred and fifty instead of one in thirteen. **So the fault is not that we
chop up words. It is that we handed the owner a sheet drawn from a three-versions-old copy and
asked them to spend twenty minutes on it.** My recommendation an hour ago to "fix the stemmer
first" is withdrawn; that repair already shipped.

## QUESTIONS

None. Q106 is discharged.

## NEXT STEPS

1. 🎯 **Establish WHICH foundation the live loop actually writes and reads.** *Everything else
   depends on it, and the fact that four exist on disk with no marked current one is the defect
   that produced this whole episode.* **Cheap, and it is a runtime question, not a grep.**
2. **Make `draw_representative_blind_sample.py` refuse a foundation that is not the current one**
   -- the same escalation this repo keeps earning: a caution as prose gets violated, a control in
   code catches it.
3. 🚫 **DO NOT re-run the stem repair.** It exists (`v5_termboundary`, `0.4%`). Re-proposing it is
   the exact waste this project's prior-work rule was written for.
4. ⚠️ *If any grounding-quality number is quoted off `v2_qualityfix`, state the `7.9%` stem rate
   beside it -- those items cannot carry a meaning and they are in the denominator.*
