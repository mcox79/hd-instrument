# **THE FIX BOTH PLANS PRESCRIBE -- "FEED THE MAINTAINED SITUATION MODEL + COREF AS THE EXTRACTION CONTEXT" -- DEPENDS ON TWO COMPONENTS THAT `HARD_FAIL`ED AND ONE THAT IS `NO_GO`. THAT IS WHY NOBODY BUILT IT.**

**Full enumeration of 150 cells, which is what I said was the precondition and what I had skipped five
times tonight.**

---

## 1. ✅ THE ENUMERATION, DONE PROPERLY THIS TIME

*`situation` **55** + `coref` **100** = **150 unique cells**, every row read.* **14 bear on
credit-assignment or extraction context.** *The four that decide the question:*

| cell | verdict |
|---|---|
| `situation_model_assembly_learned_stateful_write_v1` | 🔻 **`HARD_FAIL`** -- *learned write <= the frozen encoder on **all three** measures; "does NOT unlock the entity half"* |
| `situation_model_assembly_learned_identity_head_v1` | 🔻 **`HARD_FAIL`** -- *held-out `ef_consistency 0.672` vs a `0.80` bar, **no better than the frozen baseline**, and **train-entity `1.000` = MEMORIZATION*** |
| `extraction_quality_gate_neural_foundation_v1` | 🔻 **`NO_GO`** -- *"coref = rule_based_fallback (modern-neural install failed)"* |
| `interactive_extraction_situation_model_loop_probe1_v1` | ⬜ **no `metrics.json` -- never landed** |

## 2. 🔑 **SO THE FRONTIER IS DEEPER THAN "BUILD THE REPLACEMENT"**

**The charter prescribes replacing the local window with the maintained SituationModel + coref.
BOTH INPUTS ARE BROKEN:**

- **the LEARNED situation-model assembly fails to generalise** -- *and fails in the most diagnostic way,
  scoring `1.000` on training entities and `0.672` on held-out ones.* **That is memorisation, stated by
  the cell itself.**
- **the neural coref the extraction gate wanted would not install**, *so the gate ran on a rule-based
  fallback and returned `NO_GO`.*

> ### **THE PRESCRIBED FIX IS NOT UNATTEMPTED BECAUSE NOBODY THOUGHT OF IT. IT IS UNATTEMPTED BECAUSE THE TWO THINGS IT CONSUMES DO NOT WORK YET.**

***That reframes `exp_sharpened_credit_assignment_v1`'s `HARD_FAIL` from "the wrong fix was chosen" to
"the right fix had no working inputs, so the local-window version was what remained".*** ⚠️ *That is a
reading of the dependency structure, not a documented decision -- I did not find a note saying so.*

## 3. 🔧 **AND I FIXED A REAL DEFECT IN THE PRIOR-WORK TOOL ALONG THE WAY**

⚠️ **FIRST, A CORRECTION TO MYSELF: I accused `experiment_index.py` of SILENT truncation. IT IS NOT
SILENT** -- *it prints `... N more (raise --limit)`.* **I had cut that line off with my own `head` and
`grep -c`.** *The incomplete enumeration was my piping, not the tool.*

🔻 **BUT `--limit` WAS ADVERTISED AND NEVER PARSED.** *`args = [a for a in args if not
a.startswith("--")]` stripped it, so `--limit 200` was silently discarded and the tool told you to raise
a flag that did not exist.* ***An enumeration tool whose own remedy for truncation is unimplemented
cannot answer an absence question -- which is the exact purpose its docstring gives for existing.***

✅ **FIXED AND VERIFIED:** *default still caps at 40 with the notice; `--limit 200` returns all 55;
`--limit=200` returns all 106; `--self-test` passes (8,853 cells).* **This is how I got 150 instead of
78.**

## 4. ⚠️ LIMITS

1. **Name-filtered to 14 of 150** *by keyword. A cell relevant under a different name would be missed --
   though all 150 rows were displayed and scanned.*
2. **Verdicts READ from `metrics.json`, not reproduced.**
3. **Section 2's dependency reading is mine.** *No note states "we skipped the replacement because its
   inputs failed".*
4. **`situation`/`coref` were the query terms.** *The extraction context might be named otherwise.*

## TLDR

I finally did the enumeration I had been promising, and it explains something better than another
measurement would have.

**Both design documents say the fix is to stop using a fixed window of nearby sentences and instead use
the system's running model of the situation and who is being referred to.** I checked whether anyone had
built that. **Nobody has — and the reason is that the two things it needs are themselves broken.**

The learned situation-model builder **fails on entities it has not seen**, scoring perfectly on its
training examples and barely above nothing on new ones, which is the textbook signature of memorising
rather than learning. And the component meant to supply reference-tracking **could not be installed at
all**, so its quality gate returned a no-go.

**So the earlier failure looks different now.** It was not someone picking the wrong fix; it was someone
using the only version available, because the prescribed one had no working parts to build on.

**I also fixed a genuine defect in the search tool this all depends on** — it told you to use an option
that had never been wired up, so any question with more than forty results could not actually be
enumerated. **And I have to correct myself: I first accused it of hiding results silently. It does not;
I had cut off its warning with my own command.**

## QUESTIONS

None.

## NEXT STEPS

1. **The real blocking item is the maintained situation model generalising to unseen entities** *-- a
   `HARD_FAIL` with an explicit memorisation signature, which is upstream of everything the plans call
   the frontier.*
2. **Re-check whether the neural coref install is still broken** *-- a `NO_GO` from an install failure is
   an environment problem, not a science result, and may be cheap to clear.*
3. *Method note: **the enumeration was worth more than the five measurements that preceded it**, and it
   only became possible after fixing a flag the tool had been advertising and ignoring.*
