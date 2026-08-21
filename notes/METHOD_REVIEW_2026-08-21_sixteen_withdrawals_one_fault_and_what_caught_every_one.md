# **METHOD REVIEW, 2026-08-21: 99 COMMITS, 15% TOUCHED CODE, 16 WITHDRAWALS -- AND ALL FOUR BIG ONES WERE THE SAME FAULT, CAUGHT THE SAME WAY.**

**Owner asked for this in COMMENTARY: *"what did you find after your deep review of your
methodologies and positive vs negative results? I missed your report."* They missed it because I
gave it in chat only. Writing it down so it cannot be missed again.**

---

## 1. THE COUNTS, FROM `git log`, NOT FROM MEMORY

| | today | earlier audit |
|---|---|---|
| commits | **99** | 57 |
| **touched CODE (`hdlab/`, `tools/`)** | **15 (15%)** | 7 (12%) |
| notes only | 76 (77%) | -- |
| **corrections / withdrawals** | **16** | 29 of 57 subjects |

***The code-touch ratio barely moved: 12% -> 15%. The largest single waste named by the earlier
audit -- proposals already answered on disk -- recurred TWICE today, both times as me asking the
OWNER to authorise producing a number that was already saved (Q96, Q97).***

## 2. 🔴 **THE FOUR BIG WITHDRAWALS WERE ONE FAULT WEARING FOUR HATS**

***A NUMBER MEASURED IN ONE SETTING, APPLIED TO A DIFFERENT ONE.***

| # | what I claimed | the setting mismatch |
|---|---|---|
| 1 | **"B1 is a coverage cliff, 0.931/0.304/0.002"** | three RELATEDNESS LEVELS read as three VOCABULARY STRATA -- **inverted**: 0.002 on unrelated pairs is the GOAL |
| 2 | **"6.2 traces per lemma, we have room"** | one arm's `n_tokens_accepted` over a DIFFERENT stream's `n_lemmas` |
| 3 | **"max 92,155 traces"** | `\|\|sum\|\|^2/d` counts only INDEPENDENT contributions; it returns L^2 for correlated ones |
| 4 | **"63% of writes past 0.79 recovery"** | a threshold from a BIND/UNBIND retrieval the concept store never performs |

**And a fifth, in my own tooling: a "deliberately narrow" detector I shipped fired 3,990 times, its
top hits being `20260802`, `20260816` -- DATES stored as integers.** *Two more narrowings took it to
53. I had tested it on three fixtures and called that verified.*

## 3. ✅ **WHAT CAUGHT EVERY ONE OF THEM -- THE SAME THING, FIVE TIMES**

> ### **PUTTING A NUMBER BESIDE ANOTHER NUMBER THAT CONSTRAINS IT.**

| | the constraint that fired |
|---|---|
| 92,155 traces | **total occurrences in the whole store = 26,123.** A part cannot exceed the whole |
| the "REFUTES" cell | subset covers 118 items at 0.4576 (~54 recalled) vs whole at 165x0.2121 (~35). **A subset cannot out-recall the whole** |
| the 3,990-hit detector | *"population" 20,260,802* -- **a plausible count cannot be a calendar date** |
| the B1 cliff | opening `per_triple` and reading the FIELD NAMES beside the numbers |
| `n_grounded` (earlier) | `n_grounded = 0` printed beside `anchors +68` |

***NOT re-reading. NOT caution. NOT more careful prose. Arithmetic that had to agree and didn't.***
**This is already `CLAUDE.md` step 4 -- "print quantities that CONSTRAIN EACH OTHER" -- and it is the
only step that paid out today.**

## 4. POSITIVE RESULTS THAT SURVIVED SCRUTINY

1. **The 0.90-precision extractor HOLDS** -- random sample drawn AFTER the filters were designed and
   explicitly independent of the design set; per-row verdicts kept; 10 errors in 10 DISTINCT
   categories. Quote as **0.90 [0.826, 0.945]**.
2. **The crosstalk mechanism** -- `MEASURED_MECHANISM`, r 0.976, and the rival explanations' partials
   go NEGATIVE, which is the test that kills crosstalk-in-disguise.
3. **Our keys sit AT the Welch bound** -- `inv_e_sq/D = 1.000` vs the best trained encoder's 0.179.
   **"Better keys" is closed by geometry, not by failure.**
4. **More traces genuinely HELP** the store's own operation -- 0.0312 -> 0.1328, CI-separated, and
   the shuffled-label control collapses to chance.
5. **B4's queued test is sound** -- it CLEARS the sweep tell, which is what makes the tell worth
   having.

## 5. NEGATIVE RESULTS THAT SURVIVED SCRUTINY

1. **The "REFUTES reading can't supply the knowledge" claim FAILS four ways**, the decisive one
   arithmetic.
2. **B1's queued floor test cannot run** -- its OUT stratum is empty, 0 of 86.
3. **D3's queued test sweeps a dead variable** -- 1.0000 at every N, and identical with the memory
   switched OFF.
4. **Bundle saturation does NOT explain "writing less helps"** -- measured, and it points the other
   way.

## 6. 🎯 **THE EFFICIENCY ANSWER**

**The bottleneck is not thinking speed. It is that 85% of commits move no code, and the recurring
waste is asking a question the archive has already answered.** *Two countermeasures shipped today,
both as CODE rather than prose, because the prose rule existed already and was violated anyway:*

- **`tools/what_did_this_cell_save.py`** -- RE-ANALYSABLE vs SUMMARY-ONLY in one command. **~31% of
  7,905 cells are re-analysable** (full enumeration). *3 of 4 "must we re-run?" questions today were
  already answered on disk.*
- **`hippocampal_encoder._st_exact_cue_cannot_measure_this_organ`** -- the D3 defect as an assertion
  that raises, rather than a note someone must find.

## TLDR

You asked what my review of my own methods found. Here it is, written down this time.

**Ninety-nine commits today. Only fifteen percent touched code. And I withdrew or corrected my own
claims sixteen times.**

**Nearly all the big mistakes were the same mistake:** taking a number measured in one situation and
applying it to a different one. Reading three grades of similarity as three groups of words. Dividing
one experiment's total by another's word count. Using a difficulty score from a harder task than the
system performs. **Four times, wearing four different disguises.**

**What caught every single one was the same simple thing: putting a number next to another number
that limits it.** One word can't have 92,000 entries when the whole store has 26,000. Part of a test
can't score better than the whole test. A "count" of twenty million turns out to be a date.
**Not carefulness — arithmetic that had to add up and didn't.**

**What held up:** the fact-extractor that's right nine times in ten, tested properly on examples it
never saw during design. The explanation for why writing less helps. The finding that our word-codes
are already mathematically as good as they can get. And that building a word's picture from more
encounters genuinely does help.

**What failed, and deserved to:** a forgotten result claiming to overturn a standing conclusion — it
fails four ways. Two queued experiments that couldn't have produced answers. And my own saturation
theory, twice.

**On efficiency, the honest answer:** the bottleneck isn't thinking, it's that most of the work
produces writing rather than code, and the single most repeated waste is asking a question our own
archive already answered — **twice today I asked you to approve producing a number that was already
saved.** Both fixes I shipped are code, not more written rules, because the written rule already
existed and I broke it anyway.

## QUESTIONS

**One, on the board:** the six stale GUI panels are banner-stamped rather than moved or deleted.
Moving them is a deletion-shaped change and is your call.

## NEXT STEPS

1. **The only method step that paid out today is "print quantities that constrain each other."**
   *Weight it above the others.*
2. **Run `tools/what_did_this_cell_save.py` before concluding "we must re-run" or filing a question.**
3. **Prefer a failing assertion to a written caution** -- five prose rules were violated today by the
   person who wrote them.
