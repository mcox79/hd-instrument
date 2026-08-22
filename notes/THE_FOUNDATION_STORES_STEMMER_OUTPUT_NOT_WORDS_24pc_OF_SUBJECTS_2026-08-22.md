# **24% OF THE FOUNDATION'S SUBJECT TERMS ARE NOT WORDS. THEY ARE STEMMER OUTPUT -- `analysi`, `hypothesi`, `apoptosi`, `cigarett`, `heterozygou`, `statu`.**

**Found by the OWNER, by hand, on the first blind sheet anyone actually sat down with.** Their
words: *"there are a lot of words there that are missing letters, and a lot of them unrelated."*
**Verified and quantified the same hour.**

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

The owner sat down with our scoring sheet and immediately noticed that lots of the words were
misspelled. They are not misspelled -- they are chopped-off word stems, and there are a lot of
them: a quarter of the terms on the sheet are not real words at all. `analysis` is stored as
`analysi`, `hypothesis` as `hypothesi`, `cigarette` as `cigarett`.

This matters more than the scoring exercise it was found during. It means a quarter of what our
system has "learned" cannot be a meaning, because the thing it learned about is not a word. Every
quality number we have quoted about grounding includes those items. And it bites hardest on
scientific vocabulary, which is exactly where the system grounds best.

## QUESTIONS

None. Q106 is discharged -- the owner answered it and the answer is better than the number it was
asking for.

## NEXT STEPS

1. 🎯 **Find the call that emits the stem and name it.** Cheap, and everything else waits on it.
2. **Re-measure the non-word fraction foundation-wide**, not just on this sample.
3. ⚠️ **Report the stem fraction beside every grounding-quality number until it is fixed** -- those
   items are guaranteed NOISE and they are in the denominator.
