# **NINE CELLS CARRY A `final_verdict`. ALL NINE DIFFER FROM THE `verdict` EVERY TOOL READS. TWO HAVE NO `verdict` AT ALL.**

**Fully enumerated over all 7,868 cells with a `metrics.json` -- not a sample. The population is
small, and the divergence rate is 9 of 9.**

---

## THE COMPLETE LIST

| cell | `verdict` (what tools read) | **`final_verdict`** (the real answer) |
|---|---|---|
| `..._stated_entity_fate_..._v2_highprecision` | `STRICT_READY_PENDING_HANDCHECK` | ✅ **`HARD_PASS_CLEAN_GROW_BY_READING_VIABLE`** |
| `..._stated_entity_fate_..._v1` | `CURATED_PASS_PENDING_HANDCHECK` | 🔴 **`HARD_FAIL_REAL_PROSE_PRECISION`** |
| `exp_bootstrap_dense_process_article_reading_fa` | `HARD_FAIL_dense_explicit_no_better_than_scattered` | ⬆️ **`MIDDLE_BAND_dense_reading_works_per_process_aggregate_capped_by_volume`** |
| `exp_bootstrap_passage_context_binding_fade_v4` | `PENDING_PASSAGE_TAG_HANDCHECK` | `HARD_FAIL_PARTIAL_passage_binding_no_tag_gain...` |
| `exp_bootstrap_schema_gated_disambiguation_v5` | `PENDING_HANDCHECK` | `HARD_FAIL_schema_gated_extension_fundamentally_limited` |
| `exp_bootstrap_fhrr_superposition_fade_v3` | `HARD_FAIL_no_rise+no_fade_lesion_gap...` | `HARD_FAIL_PARTIAL_..._superposition_separates_rules_out_aver...` |
| `exp_bootstrap_process_conditioned_reading_fade` | `HARD_FAIL_no_fade_lesion_gap...` | `HARD_FAIL_PARTIAL_BOOTSTRAP_extend_not_fully_fade` |
| **`exp_context_conditioned_sense_selection_v1`** | **`None`** | `HARD_FAIL_context_conditioned_sense_selection_DOES_NOT_WORK` |
| **`exp_context_conditioned_sense_selection_v2`** | **`None`** | `HARD_FAIL_context_conditioned_sense_selection_DOES_NOT_WORK` |

## 🔴 **AND IT CORRECTS MY OWN NOTE FROM ONE TURN AGO**

**I described the v1 entity-fate extractor as *"also hand-checked, also behind a `PENDING` verdict"*
and reported its 39/99 precision. Accurate but incomplete: its `final_verdict` is
`HARD_FAIL_REAL_PROSE_PRECISION`.** *It was formally adjudicated a **failure** on real prose, not
merely a low number.* **That makes the v1 -> v2 story cleaner than I told it: a HARD_FAIL on real-prose
precision, fixed, then a HARD_PASS.**

## WHAT THE DIVERGENCES ACTUALLY ARE

**They are not clerical.** Three distinct kinds:

1. **A `PENDING` masking a finished adjudication** (3 cells) -- *including the only `HARD_PASS` here.*
2. **A blunt verdict refined by a more careful one** (4 cells) -- `HARD_FAIL` -> `HARD_FAIL_PARTIAL`
   naming *what survived*, and in one case **`HARD_FAIL` -> `MIDDLE_BAND`**: *"dense reading works per
   process aggregate, capped by volume"* is a materially different conclusion from *"no better than
   scattered"*.
3. **No `verdict` at all** (2 cells) -- *a tool reading `verdict` sees `None` and has no way to know a
   definite `HARD_FAIL` is recorded two fields away.*

## WHY THIS MATTERS MORE THAN NINE CELLS

**`tools/experiment_index.py` -- the results archive, the thing `CLAUDE.md` names as the answer to
"has this been answered?" -- reads `verdict`.** *So for these nine, the prior-work check returns the
wrong answer, and it does so silently.* **Two of them return nothing at all.**

*Tonight I was told repeatedly that prior work existed which I had not found. **This is one concrete
mechanism by which that happens.***

## TLDR

Nine experiments record their conclusion in two different places — a "status" field and a "final
verdict" field. **In all nine, the two disagree.** In two of them the status field is **empty**, while
a clear conclusion sits a few lines below.

**Our search tool reads the status field.** So for these nine, asking "have we already tested this?"
gets the wrong answer — or, twice, no answer.

**The disagreements are not typographical.** One says *"awaiting grading"* while the real verdict is a
**pass**. One says *"awaiting grading"* while the real verdict is a **failure**. And one is recorded as
an outright failure when the considered conclusion was **"this works, it's just limited by volume"** —
a materially different thing to tell someone planning what to build next.

**This also corrects something I said an hour ago.** I described the earlier fact-extractor as
"hand-checked and awaiting a verdict." It wasn't awaiting one — **it had been formally judged a
failure on real prose.** That actually makes the story cleaner: it failed, it was fixed, the fixed
version passed.

**Why this matters beyond nine files:** all evening the owner has pointed out prior work I hadn't
found. **This is one concrete way that happens** — the answer is on disk, in the file, and the tool
looks at the wrong line.

## QUESTIONS

None.

## NEXT STEPS

1. **`experiment_index.py` should prefer `final_verdict` when present** -- nine cells, 100% divergence,
   and it currently reports the wrong state for every one.
2. **`exp_bootstrap_dense_process_article_reading` deserves a read** -- a `HARD_FAIL` that was really a
   `MIDDLE_BAND` saying *dense reading works* is the kind of thing that changes a plan.
3. The two `verdict: None` cells are invisible to any results query at all.
