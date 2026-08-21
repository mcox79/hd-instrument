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


---

# **UPDATE, LATER THE SAME NIGHT: 54 MORE COMMITS, AND THE ONE FAULT TURNED OUT TO HAVE THREE SIBLINGS.**

*Appended rather than filed separately, so the owner still has ONE document to read.*
**Counted from `git log`, not memory: 54 commits since the review above, 17 correction-flavoured
(31%), 11 touching code (20% -- up from 15%).**

## A. **THE REVIEW ABOVE NAMED ONE FAULT. THREE MORE EARNED THEIR PLACE.**

### **FAULT 2 -- QUOTING A NUMBER PAST THE LIMITS ITS OWN SOURCE STATES. THREE INSTANCES.**

| the number | what its own source said, close by |
|---|---|
| `0.2449` + the null band | *"These are NOT instrument numbers and may not be quoted as such."* |
| `0.4750` | *"0.4750 is inflated by self-reference"* -- two paragraphs down |
| `3.5x` grounding | MEANINGFUL-**OR-RELATED** combined, **n=17**, one scorer, *"both CIs touch zero"* |

***THE SHAPE: THE NUMBER TRAVELS AND THE CAVEAT DOES NOT.*** **Fix shipped: `tools/cite_check.py`
-- paste the literal, get the caveat lines nearest it.** *Self-tested on two of these three.*

### **FAULT 3 -- MY OWN SAMPLING DECISION BECOMING A FINDING ABOUT THE PROJECT.**

**A 60,000-sentence cap filled in alphabetical order gave me "we have read nine books" and "only 40
of 999 test pairs are usable". THE SHELF IS 28 CORPORA AND 286,069 SENTENCES.** *I filed a board
question on those numbers and withdrew it within the hour.* **And it made me publish a NEGATIVE
that was pure artifact** -- *"not separated from source identity"* became **separated** (`+0.0220` ->
`+0.1163`, CI excluding zero) once the sample was drawn round-robin. **Fix: both tools now sample
across every corpus and PRINT what they sampled, first line, every run.**

### **FAULT 4 -- A CONTROL THAT SHARED THE FLAW IT WAS CHECKING. TWICE.**

1. **`cite_check`'s negative control PASSED while its search was completely broken** -- it shelled
   out to `rg`, which is not on PATH for a subprocess here, so every query returned zero files.
   *A broken search and an absent literal are indistinguishable.* **Fix: a SEARCH POSITIVE CONTROL.**
2. **The corpus-confound tool printed "so it carries something the source tag does not" while its
   OWN bootstrap, four lines above, read `[-0.0419, +0.0764]`.** *Reading a point estimate as a
   finding while the interval spans zero -- inside the control written to prevent that.* **Fix: the
   verdict is gated on the CI.**

### **AND A RECURRING TIDINESS FAULT WORTH NAMING: THE CORRECTED HEADLINE LEFT STANDING. 3x.**
*Each time I corrected a note's body and left its TLDR asserting the original.* **The summary is the
section most likely to be read alone.** *Once, my own fix-up script silently failed on the TLDR
because I asserted the match count on one substitution and not the other -- **a `replace` that
matches nothing returns the string unchanged and reports success.***

## B. ✅ **WHAT WORKED, AND IT IS ONE HABIT WITH A NEW SCOREBOARD**

> ### **CHECKING PRIOR WORK CHANGED THE ANSWER EIGHT TIMES. THREE OF THOSE, THE ANSWER WAS IN THE DOCSTRING OR MAP ENTRY OF THE THING I WAS ABOUT TO CHANGE.**

**The single most expensive miss:** *the plan's TOP ITEM told me to wire the definitional extractor.
It was wired two days earlier, `substrate.py:538`, with 212 of 402 provenance rows to prove it -- and
the function's own docstring carried three numbered corrections saying so.*

**Two new reads now exist for exactly that:** `tools/symbol_corrections.py` (a symbol's own
corrections, including INLINE COMMENTS -- it missed the most expensive case twice before I tested it
against a real one) and `tools/cite_check.py` (a number's own caveats).

**Every one was measured before being built:** *3.8% of docstrings carry a correction; 8.0% of notes
carry a limits section.* **The ceiling-detector proposal stayed dead at 48.5%.**

## TLDR (UPDATE)

Since the review above I made **fifty-four more commits, a third of them corrections.**

**The single fault I identified had three siblings, and they are worth knowing separately:**

**One — I repeat a number and leave its warning behind.** Three times: a figure that only applies to
one word list, a figure its own note calls inflated, a ratio resting on seventeen examples. **The
number is memorable, the caveat isn't.**

**Two — my own shortcut became a claim about the project.** My script read the first sixty thousand
sentences alphabetically, so I announced we'd only read nine books. **We have twenty-eight sources.**
I asked you to change the reading list because of it, then withdrew that within the hour. **Worse, it
made me publish a negative result that vanished when I sampled properly.**

**Three — twice, my safety check had the same blind spot as the thing it was checking.** One reported
"no problems found" while it was in fact finding nothing at all, ever. **A check that can't tell
"nothing wrong" from "I'm broken" isn't a check.**

**What worked is unchanged and is now eight for eight: looking for previous work before starting.**
Three of those eight times, the answer was written inside the very thing I was about to modify — most
expensively, our number-one task, which had been finished two days earlier.

**Two new commands now do that looking automatically**, and I measured that each would be useful
before building it, rather than after.
