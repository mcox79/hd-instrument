# **`import hdlab.reading_grounding_loop` SILENTLY REWRITES `sys.stdout`'s ENCODING AND PINS `OMP_NUM_THREADS=1` FOR THE WHOLE PROCESS -- BECAUSE IT DRAGS IN `9` EXPERIMENT CELLS.**

**Measured, not inferred. Found because it crashed a probe of mine, and it is worth more than the probe
was.**

---

## 1. THE MEASUREMENT

```
before importing hdlab.reading_grounding_loop:  stdout=cp1252/surrogateescape   OMP=None
after                                        :  stdout=utf-8/replace           OMP=1
GLOBAL STATE MUTATED BY A LIBRARY IMPORT: True
```

**Importing the project's main reading module pulls `9` experiment cells into `sys.modules`:**

`exp_graded_thematic_fit_integrated_reader_gate_v1` · `exp_learned_argstruct_parser_lccp_independent_gold_v1` ·
`exp_online_knowledge_condenser_selectional_v1` · `exp_parser_ruleinduction_cls_ppattach_v1` ·
`exp_parser_selfimprove_case_sleep_ppattach_v1` · `exp_pivot_selectional_knowledge_richness_2afc_v1` ·
`exp_role_filler_factorization_conceptnet_cg_v1` · `exp_scene_coherence_verifier_contrastive_scv_v1`

**The mechanism is a cell doing what a CELL is supposed to do, at module level:**

```python
# experiments/exp_online_knowledge_condenser_selectional_v1.py, module scope
os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

***That is correct for a script and wrong for a dependency.*** *CLAUDE.md itself mandates the thread
pins at the top of every cell -- the defect is not the cell, it is that a LIBRARY imports one.*

## 2. THE DEPENDENCY, MEASURED

| | count |
|---|---|
| `hdlab/` files importing an experiment **CELL** | **6** |
| distinct cells they depend on | **13** |
| `hdlab/` files importing a shared `_helper` from `experiments/` | 3 (9 helpers) |

**The cell dependencies, by file:** `reasoner.py` (5), `context_grounded_valence.py` (4),
`situation_reader.py` (2), `learner/plugins/estimation_plugin.py` (1),
`learner/plugins/ruleind_plugin.py` (1), `word_acquisition_loop.py` (1).

*The `_helper` group (`harness.py`, `additive_map.py`, `situation_reader.py`) is milder -- shared
infrastructure that merely lives in the wrong folder.*

## 3. 🔻 WHY THIS MATTERS BEYOND TIDINESS -- THREE CONCRETE HARMS, ONE ALREADY PAID

1. ✅ **PAID: it crashed a probe.** *Running the live-closure audit under a `redirect_stdout(StringIO)`
   died with `'_io.StringIO' object has no attribute 'reconfigure'` -- because importing a LIBRARY ran
   a SCRIPT's stdout setup. Any caller who redirects stdout hits this.*
2. **Thread pins are set behind the caller's back.** *`OMP_NUM_THREADS=1` appears from nowhere. CLAUDE.md
   requires it BEFORE numpy import for cells; a consumer of `hdlab` who wanted 8 threads silently gets
   1, and only if they had not already set it (`setdefault`).*
3. **13 experiment cells are now undeletable.** *`experiments/` is where disposable cells live; these
   thirteen are load-bearing library dependencies, and nothing marks them as such. An author editing
   one has no signal that `hdlab` imports it.*

> ### **A LIBRARY THAT REWRITES `sys.stdout` AND PINS THREAD COUNTS WHEN YOU IMPORT IT IS NOT EMBEDDABLE. That is a plain fact about commercial readiness, separate from anything about meaning or grounding.**

## 4. THE MINIMAL FIX -- SPECIFIED, DELIBERATELY NOT APPLIED

**Make the `experiments` imports LAZY** (inside the functions that use them) in the 6 files. *That is
how `reading_grounding_loop` already loads `pos_tagger` / `arc_parser` / `arc_labeler`, so the pattern
is established in this codebase.*

🚫 **NOT DONE HERE, and the reason is specific rather than timid:** *these 6 files sit upstream of the
live path (`learner -> frame_induction -> goal_typing -> consequence_learning_loop ->
grounding_acquisition_loop -> reading_grounding_loop`). **A lazy-import change there is exactly the
kind of edit that looks safe and reorders module initialisation.** It needs its own before/after
witness on the live path, which is a task, not a footnote to an audit.*

## 5. LIMITS

1. **One import path measured** (`hdlab.reading_grounding_loop`). *Other entry points may drag in more
   or fewer cells.*
2. **Static enumeration for the 6/13 counts**, runtime for the 9 cells actually loaded. *The two differ
   because some imports are conditional -- both numbers are real, they answer different questions.*
3. **`setdefault` means the thread pin only fires if unset** -- *a caller who set it first is unaffected.*
4. **I have not checked whether any of the 13 cells has been edited since a library started depending
   on it.** *That is the failure this enables, and it is not measured.*

## TLDR

Loading the system's main reading module **quietly changes two global settings for the entire program**:
it switches how text output is encoded, and it forces the maths library to use a single processor core.

Neither is something a library should do. It happens because the library imports **nine experiment
files**, and experiment files are scripts — they're *supposed* to set up their own output encoding and
processor settings when run directly. Our own guidelines require it. The mistake isn't in those files;
it's that permanent code depends on them at all.

**This already cost me something today**: a check I was running crashed outright, because importing a
library ran a script's start-up code in a context that didn't support it.

**It also means thirteen experiment files can never be deleted or freely changed**, because parts of the
permanent system now import them — and nothing anywhere says so. Someone tidying up old experiments
would break the system with no warning.

**Why this matters beyond neatness:** if we ever want this to run inside someone else's software,
"importing our library rewrites your program's output settings and limits it to one processor core" is
not acceptable. That's a straightforward engineering fact, independent of any question about whether the
system understands anything.

**I have not fixed it.** The fix is small and well understood — load those imports only when needed,
which this codebase already does elsewhere — but those files sit upstream of the main reading path, and
changing when modules load is exactly the sort of edit that looks harmless and isn't. It needs its own
before-and-after test.

## QUESTIONS

None — Q106 (the scoring sheet) remains the only open one.

## NEXT STEPS

1. 🎯 **Convert the 6 files' `experiments` imports to lazy, one file at a time, each with a
   before/after check that the live path still self-tests and the closure is unchanged.** *`reasoner.py`
   (5 cells) and `context_grounded_valence.py` (4) carry most of it.*
2. **Mark the 13 depended-on cells as load-bearing** *-- a comment at the top of each saying which
   `hdlab` module imports it, so nobody deletes one.*
3. *Method note: **this came out of a crash I caused with a stdout redirect.** I nearly dismissed it as
   my own bug -- it was, and the bug was only possible because of a real defect underneath.*
