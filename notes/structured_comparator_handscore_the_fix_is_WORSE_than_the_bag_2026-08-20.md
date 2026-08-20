# THE STRUCTURED COMPARATOR IS **WORSE** THAN THE BAG-OF-WORDS IT WAS BUILT TO REPLACE (blind hand-score, pending since 2026-08-13)

**2026-08-20.** `exp_structured_comparator_v1` landed 2026-08-13 as
`STRUCTURAL_PASS_PENDING_HANDSCORE` and its blind sample was never scored. **It is the built fix for
the exact defect this whole day kept running into** -- the read-out's decision variable is a cosine
between two BAGS of nearby content words, which cannot separate *"X means Y"* from *"X occurs near
Y"*. Scored today.

## THE RESULT

| 100 rows, blind, `arm_key.json` unopened until scoring was committed to disk | MEANINGFUL | RELATED | NOISE |
|---|---|---|---|
| **CONTROL** -- bag of nearby content words (the shipped read-out) | 0% | **24%** | 76% |
| **STRUCTURED** -- "content word in THIS DEPENDENCY RELATION to the target" | 0% | **6%** | **94%** |

- **MEANINGFUL: 0/50 vs 0/50, p = 1.0.** Neither arm produced a single row that would teach a
  reader the word. **The M cell cannot discriminate here and must not be read as a tie between
  working systems** -- it is a tie at zero.
- **RELATED: 24% vs 6%, Fisher one-sided p = 0.0113 -- THE CONTROL IS SIGNIFICANTLY BETTER.**
- **NOISE: 76% vs 94%.**

**➡️ THE STRUCTURAL FIX MAKES THE READ-OUT WORSE, NOT BETTER, AND THE ONLY SEPARATED CELL SEPARATES
AGAINST IT.**

## WHY THIS IS A REAL NEGATIVE AND NOT A WEAK TEST

The cell had already proved the arms genuinely differ, so a null could not be blamed on the
intervention failing to reach the metric -- the failure mode that has produced several fake nulls
here:

- **97.8% argmax disagreement** (6,145 of 6,283 common lemmas) between the two encoders on the same
  3,992-sentence slice.
- **A worked example in the cell's own witness:** `wedding` is in the CONTROL bag in **all three**
  corpus sentences containing `whisky`, and in the STRUCTURED feature set in **none** of them. So
  STRUCTURED genuinely cannot reproduce the documented `whisky -> wedding` failure.

**It does not reproduce that failure. It produces different ones, and more of them.** Being unable
to make a specific documented error is not the same as being right, and this is a clean measured
example of the difference.

## ⛔ WHAT THIS CLOSES

The bag-of-words read-out has been this project's named defect for over a week, and the structured
comparator was the principled fix -- replace the feature alphabet with syntax, so a word that merely
*occurs near* the target stops counting as evidence for what it *means*. **Measured blind, it is
worse.** *That does not prove syntax cannot help; it proves THIS syntactic encoding, on this corpus,
at this scale, does not. But it is a fair test of a serious implementation with its
non-circularity already demonstrated, so it is a genuine negative rather than an inconclusive one.*

## LIMITS, STATED PLAINLY

1. **n = 50 per arm, one scorer (me), one corpus.**
2. **The only separated cell is RELATED**, which is the softest and most scorer-dependent of the
   three categories. The hard category, MEANINGFUL, is 0 vs 0 and says nothing.
3. **My RELATED/NOISE boundary is measurably more generous than the 2026-08-12 scorer's** (measured
   today: 44% vs 19% RELATED on a comparable population), so absolute rates should not be compared
   across scorers -- **but both arms here were scored by me in one sitting, so the COMPARISON is
   internally valid**, which is the whole point of the design.
4. **Do NOT line these numbers up against the historical 35% / 64% / 94% figures.**
   `SUBSTRATE_CHARTER` and `MEMORY.md` carry a standing prohibition; different scorers, rubrics and
   populations.

## 🔎 A PROCESS NOTE WORTH MORE THAN THE RESULT

My first join used the wrong key shape -- I assumed `arm_key.json` was a flat `blind_id -> arm` map;
it is `{"warning", "shuffle_seed", "rows": [...]}`. **The join produced 100 unmapped rows, and the
script PRINTED `!! 100 rows had no arm in arm_key.json -- reported, not dropped silently` instead of
quietly reporting two empty arms.** That loud failure is the only reason the mis-join was caught
rather than written up as a null. **Same lesson as the rest of today: the guard has to be in the
code, not in the intention.**

*Also worth recording: the file `SCORING_SHEET.txt` in this cell's directory shares **50 of its 100
rows** with the already-scored `exp_grounding_quality_readout_v1` sheet, whose verdicts are attached
to PBV arms. Anyone scoring that .txt believing it settles this cell's question would be scoring a
half-overlapping population against the wrong arms. **The right artefact is `blind_sample.json` +
`arm_key.json`, which is what the cell's own `QUALITY_CLAIM` field says.***

## TLDR

For over a week the known weak point of this system has been how it decides what a word means: it
looks at which words appear NEARBY, which cannot tell "a whisky is a drink" from "whisky was served
at a wedding".

Someone built the obvious fix -- use grammar, so only words in a real grammatical relationship to
the target count. It was finished on the 13th and left waiting for a human to grade its output.
**I graded it today, without being able to see which system produced which answer.**

**The grammar version is worse.** Judged on how many answers were at least connected to the right
meaning, the old crude version got 24 out of 50 and the clever one got 3 out of 50. Neither produced
a single answer that would actually teach you a word.

The interesting part is that the fix *does* avoid the specific mistakes it was designed to avoid --
it genuinely cannot produce the whisky-wedding error. **It just makes different mistakes instead,
and more of them.** Avoiding a known error is not the same as being right.

## QUESTIONS

None. This closes a route rather than opening a choice.

## NEXT STEPS

1. **`exp_structured_comparator_v1`'s pending verdict is now answerable** -- and the answer is
   negative. Its landed `metrics.json` is deliberately NOT modified (same discipline as the seven
   unread runs and the B3 audit): the verdict is recorded beside the evidence.
2. **Do not wire the structured comparator on.** It is `DEFAULT-OFF` and should stay that way; the
   registry row should carry this result.
3. **The bag-of-words defect remains open and is now harder**, because the principled fix for it has
   been measured and is worse.
