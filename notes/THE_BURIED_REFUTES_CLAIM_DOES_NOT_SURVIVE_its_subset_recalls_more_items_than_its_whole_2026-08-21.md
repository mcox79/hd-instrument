# **THE BURIED "THIS REFUTES 'READING CAN'T SUPPLY THE KNOWLEDGE'" CLAIM DOES NOT SURVIVE. FOUR INDEPENDENT REASONS, AND THE LAST IS ARITHMETIC: ITS SUBSET RECALLS MORE ITEMS THAN ITS WHOLE.**

**When I fixed the archive index tonight it surfaced this cell as a buried result and I flagged it,
quoting its own text. I had not opened it. I have now. The claim fails.**

*Cell: `exp_bootstrap_dense_process_article_reading_fade_v6` (2026-08-11).
`verdict = HARD_FAIL_dense_explicit_no_better_than_scattered`;
`final_verdict = MIDDLE_BAND_dense_reading_works_per_process_aggregate_capped_by_volume`.*

---

## 1. THE CLAIM

> `diagnosis.headline`: *"DENSE/EXPLICIT topic-known reading RECOVERS substantial process-conditioned
> knowledge per process... **REFUTING the overstated 'reading can't supply the knowledge'**. The
> AGGREGATE is capped by corpus VOLUME + specific mismatches, not by a fundamental reading limit."*

**It rests on five per-process numbers: 0.561, 0.4516, 0.6923, 0.60, 0.50 -- against a
`scramble_floor_aggregate` of 0.1879.**

## 2. 🔴 REASON ONE -- THE FIVE ARE A POST-HOC SELECTED SUBSET, AND THE FIELD SAYS SO

**The key is literally named `per_process_strong`.** *Its sibling is `per_process_failed`:
fossilization 0.2308, hydrocarbon_formation **0.0**, sound_propagation **0.0**.* **Selecting the
processes that worked and reporting those is not a result about reading.**

## 3. 🔴 REASON TWO -- THE FLOOR IS AN *AGGREGATE* FLOOR, AND NO PER-PROCESS FLOOR EXISTS

**`scramble` appears 13 times in the file. Every occurrence is aggregate** -- `scramble_recall`,
`signal_above_scramble`, `scramble_floor_aggregate`. ***The key names itself `_aggregate`.***
*So `strong_processes_far_above_scramble_floor: true` compares per-process TREATMENT values against
a floor computed on a DIFFERENT population.* **STANDING DISCIPLINE 8/11: every floor is recomputed
on the item's own population, and no number crosses populations. There is no per-process floor to
clear, so the comparison has no bar.**

## 4. 🔴 REASON THREE -- THE SEED BEATS READING IN **8 OF 8** PROCESSES, WITHOUT EXCEPTION

| process | n | reading_only | seed_only |
|---|---|---|---|
| electricity_generation | 41 | 0.5610 | **0.6585** |
| combustion | 31 | 0.4516 | **0.6452** |
| igneous_rock_cycle | 13 | 0.6923 | **0.8462** |
| fossilization | 13 | 0.2308 | **0.7692** |
| hydrocarbon_formation | 9 | 0.0000 | **0.7778** |
| erosion_weathering | 5 | 0.6000 | **1.0000** |
| digestion | 4 | 0.5000 | **0.7500** |
| sound_propagation | 2 | 0.0000 | **1.0000** |

**Item-weighted over the listed processes: reading 0.4576 vs seed 0.7203.** *"APPROACHING the seed"
is generous for a gap of 0.26 with zero exceptions.* **And three of the five "strong" processes have
n = 13, 5 and 4** -- *erosion is 3 items out of 5; digestion is 2 out of 4.*

## 5. 🚨 REASON FOUR -- THE ARITHMETIC DOES NOT CLOSE. THE SUBSET RECALLS MORE THAN THE WHOLE.

| quantity | value |
|---|---|
| `n_heldout_items` | **165** |
| aggregate `reading_only` | **0.2121** → **≈ 35 items recalled** |
| items covered by the 8 listed processes | **118** |
| item-weighted `reading_only` over those 8 | **0.4576** → **≈ 54 items recalled** |

> ### **54 > 35. A SUBSET OF THE HELD-OUT SET RECALLS MORE ITEMS THAN THE ENTIRE HELD-OUT SET.**
> ***The per-process numbers and the aggregate are computed on DIFFERENT BASES and the cell does not
> say so anywhere.*** **Whichever is right, the two cannot both be quoted, and the "REFUTES" claim
> is built on the one that contradicts the headline.**

*Also unexplained: the corpus lists **18** processes covered, `per_process` reports **8**, and
**47 of 165 held-out items (28.5%)** appear in no per-process row at all.*

## 6. ✅ WHAT DOES SURVIVE, AND IT IS WORTH KEEPING

1. **The failure localisation is genuinely good and is the useful output of this cell:**
   *hydrocarbon_formation extracted **32 facts** and scored **0.0** -> the cell correctly diagnoses
   ENTITY MISMATCH rather than reader depth. fossilization extracted **0 facts** -> a descriptive
   rather than mechanistic article.* **Those are two different failures and it separated them.**
2. **The cell DID self-correct once** -- `final_verdict_msg` opens *"(overstated conclusion
   CORRECTED)"* and the honest aggregate comparison is right there: **dense signal above scramble
   `0.0242` vs scattered `0.0485`, `beats_v4_genuine_signal: false`, `approaches_seed: false`.**
   ***The correction stopped one step short of the headline it was correcting.***

## 7. 🔻 AND MY OWN CORRECTION

**Earlier tonight I listed this cell as one of two buried results the archive fix surfaced, and
quoted its "REFUTES" line as evidence of something worth attention.** *I quoted a claim from a
`diagnosis.headline` without opening the numbers under it -- **the identical fault that cost me the
B1 "cliff" earlier tonight, in the same session, after I had written the lesson down.*** **The cell
is still worth attention. Its headline is not.**

## TLDR

Earlier tonight I fixed the tool that reads our experiment archive, and it surfaced a result that had
been filed as a failure but whose own summary claimed to overturn one of our standing conclusions. I
flagged it as worth a look. **I hadn't looked. I have now, and the claim doesn't hold up.**

Four separate problems, any one of which would be enough.

**It reports only the topics that worked** — the field is literally named "strong", and its
counterpart lists three topics scoring 0.23, 0.0 and 0.0.

**It compares those winners against a difficulty benchmark calculated across everything**, not
against one calculated for those topics. There isn't a per-topic benchmark anywhere in the file, so
there's nothing for them to have cleared.

**Being told the answer up front beats reading in every single topic — eight out of eight, no
exceptions**, by a wide margin. And three of the five "strong" topics rest on 13, 5 and 4 questions
— one of them is literally three correct answers out of five.

**And the arithmetic doesn't add up.** The overall score says about 35 questions were answered
correctly out of 165. But the topics it lists cover 118 questions and, at the scores given, account
for about 54. **A part of the test can't beat the whole test.** So the per-topic figures and the
overall figure are measuring different things, and nothing in the file says so.

**What is genuinely good here:** when reading failed, it worked out *why*, and distinguished two
different causes — one topic where the reader pulled out 32 facts that were simply about the wrong
things, and another where the article was descriptive and yielded nothing. That's real diagnostic
work.

**And my own error:** I repeated a headline without opening the numbers beneath it. **That is the
exact mistake that cost me earlier tonight — in the same session, after I had written down the
lesson.**

## QUESTIONS

None.

## NEXT STEPS

1. **Do not quote "reading can supply the knowledge" from this cell.** *The honest summary is in its
   own comparison block: dense signal above scramble 0.0242 against scattered 0.0485,
   `beats_v4_genuine_signal: false`, `approaches_seed: false`.*
2. **The arithmetic gap is worth one question to whoever owns it:** are the per-process and aggregate
   recalls on the same denominator? *If yes, one is wrong; if no, the cell needs to say which.*
3. **Keep the failure localisation.** *32-facts-but-zero-recall from entity mismatch is a reusable
   diagnosis and is the best thing in the file.*
