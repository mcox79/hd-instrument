# THE MEANING LOOKUP CANNOT INFLECT -- ~13 POINTS OF COVERAGE SITTING UNREAD ON DISK

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**
> *Reason, so you do not self-negotiate it: a dropped precondition invalidates the declared gate even
> when the result may be fine. "The number probably didn't change" is not yours to decide silently.
> Disclose; the operator decides.*

---

## THE PROBLEM IN PLAIN LANGUAGE

We own a table of sensorimotor norms -- roughly 36,810 words, each with a description of how it is
seen, heard, touched, and acted on. It is the **only meaning asset we have whose signal survives
leaving the corpus's most common vocabulary.**

**The way we look words up in it is a plain dictionary lookup on the exact spelling.**

```python
# hdlab/grounded_similarity.py:165 -- the whole thing
return _table().get(word.lower())
```

So the substrate knows `country` and draws a blank on `countries`. Knows `release`, misses
`released`. Knows `animal`, misses `animals`. **The meaning is in the table. The word in front of it
is just wearing a different ending.**

**Your job: make the lookup fall back to a lemma when the exact form misses, and prove on a TASK
that this helps rather than merely widens.**

## WHY THIS ONE

**It is the cheapest large move available in Phase 1, and Phase 1 is the current bottleneck.**

`LONG_TERM_PLAN.md` names the headline job as norming **`+14,704` more words** by hand to lift token
coverage to ~90%. That is a large, slow, expensive build.

| | token coverage | type coverage |
|---|---|---|
| raw string lookup -- **what runs today** | `0.6035` | `0.1027` |
| + `normalize_lemma` (the repo's own, `is_known_word`-gated) | **`0.7350`** | **`0.1633`** |

**The distance from `60.35%` to the `90%` target is `29.65` points. This is `13.15` of them -- 44% of
the way -- using data already on disk and no new norms.**

➡️ **It also revises the build target itself: `+14,704` counts inflected forms of words we have
ALREADY normed as words someone must go and norm.** Nobody should start that build before this is
settled.

## MEASURED vs INFERRED

**MEASURED** (2026-08-22, replication of `exp_meaning_asset_norms_coverage_gap_v1` verified to four
decimals -- 235,876 types / 5,558,698 tokens / `0.6035` / `0.1027` -- BEFORE any delta was computed):

- Token coverage `0.6035` -> `0.7350`; type coverage `0.1027` -> `0.1633`, whole corpus.
- The 1,000 commonest words are **`75.7%`** covered, and that band carries **`41.4%` of all tokens**.
- All **243** uncovered types in that band, enumerated: proper nouns, plurals of covered concepts,
  inflected verbs. **Not one function word.**
- ~**5 of 130** of my suffix-rule recoveries are WRONG (`using -> us`, `uses -> us`, `notes -> not`,
  `james -> jam`, `angeles -> angel`), hand-checked one by one.
- `normalize_lemma` is more conservative (117) **and still makes the `angeles -> angel` error.**
- `women -> woman` and `feet -> foot` are recovered by **neither** method.

**MEASURED 2026-08-22 (was INFERRED until then) -- THE SUBSTITUTION ITSELF IS SOUND:** `3,629`
morphological pairs have BOTH forms carrying their own independent norms. **Morphological pair median
cosine `0.7605` against a random-pair floor of `-0.0131` -- separation `+0.7736`, and only `2.4%` of
random pairs reach the morphological median.** *Self-pair positive control reads `1.0000`. The vectors
are centred, not all-positive (random p05 `-0.5955`), so cosine is informative rather than inflated.*
🔻 **BUT `4.9%` OF PAIRS FALL BELOW THE RANDOM MEDIAN -- the substitution actively misleads on about
one word in twenty**, and **YOUR IMPLEMENTATION MUST REPORT ITS OWN VERSION OF THAT NUMBER.**
🔑 **AND A SUB-HYPOTHESIS IS REFUTED, WHICH SAVES YOU A WRONG TURN: I predicted damage would
concentrate in participles and that restricting the fallback to PLURALS would be safer. It is not --
inflection `5.1%` vs participles `4.9%`, indistinguishable.** *The worst pairs are the RULE landing on
a real but unrelated word (`pales -> pal` `-0.8312`, `doting -> dot`), not morphology drifting.*
➡️ **SO: VALIDATE THE RESIDUE, DO NOT RESTRICT THE SUFFIX SET.** That is exactly what
`normalize_lemma`'s `is_known_word` gate does.

**STILL INFERRED, NOT MEASURED -- this is the remaining risk:**

- 🔻 **That substituting the base form's norm HELPS A TASK.** Similar profiles remove the objection
  "the two might be unrelated"; **they do not establish a gain.** No task was run. **Nothing here is a
  capability claim, and this is the whole point of the problem.**
- ✅ **CLOSED 08-22 -- "the ceiling is above `0.7350`" IS NOW MEASURED AND THE HEADROOM IS SMALL.**
  Adding WordNet `morphy` on top of `normalize_lemma` takes token coverage `0.7350 -> 0.7492`:
  **`+1.42` points, against the `+13.15` ours already buys. OURS CAPTURES ~`90%` OF THE AVAILABLE
  GAIN.** ➡️ **DO NOT BUILD OR ADOPT A HEAVIER LEMMATISER -- reuse `normalize_lemma`.** *A parallel
  build costs a dependency and buys 1.4 points.* ⚠️ *`morphy`'s own control passed 4/5 irregulars and
  MISSED `mice -> mouse`, so `0.7492` is itself a floor, not the true ceiling.*

## ALREADY TRIED

- **`normalize_lemma` EXISTS and is live** in `hdlab/reading_grounding_loop.py:230` -- on the READING
  path. **It is simply not called by the norms lookup.** This is a wiring gap, not a missing organ.
  *Do not build a second lemmatiser; the standing rule is reuse, and a parallel build is both
  non-faithful and islanding.*
- **That function had a real defect and it is FIXED** -- it resolved to an unguarded suffix stripper
  until `01093ac1f`/`7d6036bca` added the `is_known_word(residue)` gate. **Pre-fix it turned 8,692
  dictionary words into non-words.** Any foundation snapshot built before those commits carries
  `7.87%` stem damage. **Build a clean snapshot; do not load `v2_qualityfix`.**
- **`exp_meaning_asset_norms_coverage_gap_v1`** (08-16) already sized the coverage gap and computed
  the `+14,704 / +40,160 / +103,558` build targets. Read it before proposing any widening.
- **A PRIOR NEGATIVE THAT MUST TRAVEL WITH ANY PROPOSAL BUILT ON THIS ASSET:**
  `exp_grounded_inductive_concept_encoder_heldout_new_v1` (07-26) is a **HARD_FAIL** -- an inductive
  concept encoder on this same grounding scored held-out AUC `0.5879` while a **popularity baseline**
  beat it. Wider coverage does not by itself make this asset work.

## VERIFY BEFORE YOU START

1. **Reproduce the landed coverage numbers first.** `0.6035` / `0.1027` on 235,876 types. *If your
   replication does not hit those exactly, a tokenisation difference will look exactly like a
   coverage finding.* This is the positive control for everything downstream.
2. **Confirm line 165 still reads `_table().get(word.lower())`** -- notes go stale within hours here,
   and someone may have already changed it.
3. `python tools/before_you_start.py "lemmatise the norms lookup"` -- and **read every row it
   returns**, not the first.
4. `python tools/organ_map_cite.py` for the grounding organ -- **check we have not already been wrong
   about this**, including any standing "do not re-propose" line.

## THE BAR

**A TASK SCORE. NOT A COVERAGE NUMBER.** Coverage is the statistic this change optimises, and a
statistic the mechanism optimises may DIAGNOSE, never DECIDE.

- **A CI-separated margin over the strongest floor you actually RUN**, gated on that floor's UPPER
  bound, on a held-out task (SimLex, or the reader's own held-out task -- name which, with n and
  pool).
- 🚨 **THE REQUIRED CONTROL, AND IT IS THE ONE THAT DECIDES: an information-free twin that lemmatises
  each miss to a RANDOM covered word instead of its own lemma. IT MUST LOSE.** If it also wins, you
  have measured "having any vector beats having none", which is string-matching luck, not meaning.
- **Report the false-recovery rate on YOUR implementation**, hand-checked, the way the 5-of-130 above
  was. A recovery to a real-but-unrelated word is a wrong meaning silently inserted into the reader.
- Cross-seed: run it through `tools/replication_gate.py` and quote the verdict string.
- **SAVE THE SCORED POPULATION**, not just the score -- which words were recovered, and to what.

**A legitimate outcome is that this does NOT help.** Say so plainly if it does not; a clean negative
here is worth more than the widening build proceeding on an assumption.

## FILES AND ENTRY POINTS

| what | where |
|---|---|
| **the one line to change** | `hdlab/grounded_similarity.py:165` |
| the lemmatiser to REUSE | `hdlab/reading_grounding_loop.py:230` `normalize_lemma` |
| the landed coverage cell | `data/exp_meaning_asset_norms_coverage_gap_v1/metrics.json` |
| the 243 uncovered words | `notes/problems/reader_meaning_channel/uncovered_top1000_2026-08-22.txt` |
| the full finding + its limits | `notes/THE_NORMS_LOOKUP_DOES_NOT_LEMMATISE_AND_THAT_IS_13_POINTS_OF_FREE_COVERAGE_2026-08-22.md` |
| the parent problem this serves | `notes/problems/reader_meaning_channel/PROBLEM.md` |

## DO NOT QUOTE

- 🚫 **`+14,704 words to reach 90%`** as a standalone build target. It counts inflected forms of
  already-normed words as words needing new norms.
- 🚫 **`0.7350` as a capability number.** It is COVERAGE -- how often the asset can speak, not whether
  what it says helps. No task has been run.
- 🚫 **`39,707`** as the asset size. That is the Lancaster CSV filename; the usable join is **36,810**.
  The cell carries a field literally named `NOT_39707` because this error has been made before.
- 🚫 **`rho 0.2701`** as general evidence for the asset. It was measured on SimLex, which this asset
  covers **100%** -- its best case, not its typical one.
- 🚫 **`7.87%` stem damage** as a property of the system. It is a property of pre-fix snapshots only.
