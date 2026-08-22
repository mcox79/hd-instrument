# **`run_certification.py` -- WHICH `CLAUDE.md` REQUIRES TO PASS ON MAIN -- HAS EXITED `3` AND RUN *ZERO* OF ITS `456` COLLECTED TESTS SINCE 2026-08-20. ITS OWN REPORT SAYS `RESULT: PASS`.**

**Found while verifying my own change. It is not my change: the file that breaks it landed two days
ago and I have not touched it.**

---

## 1. THE FAILURE, AND WHY IT WAS INVISIBLE

**`verification/test_hypernym_matcher_positive_control.py` is a SCRIPT** -- it defines **zero
`test_` functions** and ends with a bare, module-level:

```python
raise SystemExit(1 if fails else 0)
```

**Fine when run directly. Under pytest COLLECTION it is an `INTERNALERROR` that aborts the ENTIRE
SESSION.** *`456` tests collected, none run, exit code 3.*

> ### 🔻 **AND THE REPORT LOOKS FINE. The script's own `print("RESULT: PASS -- ...")` runs BEFORE the crash, so `data/certification.md` opens with a PASS line and buries the abort below.** *That is why two days passed.*

*Verified not-mine: `git log` puts that file's last change at **2026-08-20** (`0a13e1e9f`), and my
change today was to `hdlab/learner/registry.py`.*

## 2. IT IS NOT ONE FILE -- IT IS A STRUCTURAL SPLIT IN `verification/`

*Parsed all 64 `verification/test_*.py` with `ast`:*

| kind | count | behaviour under pytest |
|---|---|---|
| **clean pytest tests** (no module-level work) | **33** | fine |
| 🔻 **has `test_` functions BUT ALSO module-level work** | **26** | **executes at COLLECTION, before any test runs** |
| 🔻 **scripts only** (zero `test_` functions) | **5** | pytest collects them, runs nothing, and their side effects fire |

**Guarding the one `SystemExit` moved the failure along rather than clearing it:** the next error is
`test_board_answerable_all.py`, which asserts at MODULE LEVEL that `status_state.BOARD_DOC` points at
its own temp dir -- **but a sibling witness already redirected that global to a DIFFERENT temp dir when
IT was imported.** *Two standalone witnesses, each correct alone, colliding because pytest imports
them into ONE process.*

## 3. 🔑 WHAT THIS ACTUALLY IS

**These files were written to be run STANDALONE, one process each** -- which is exactly how I have been
running them all week, and they pass that way. **`verification/` is doing two jobs under one naming
convention**: a pytest suite, and a collection of independent witness scripts. **Under `pytest
verification/` the second kind breaks the first.**

*It is the same shape as the defect I fixed an hour ago -- a SCRIPT's module-level setup running
because something IMPORTED it -- in a different place.*

## 4. WHAT I DID AND DELIBERATELY DID NOT DO

| | |
|---|---|
| ✅ **guarded the `SystemExit`** behind `if __name__ == "__main__"` | *one line, removes the session abort* |
| 🚫 **did NOT patch the other 30** | *26 mixed + 5 script-only. Each needs its own judgement about what may safely move behind a `__main__` guard, and a blind sweep across 30 witness files is exactly the change that looks mechanical and is not* |
| 🚫 **did NOT touch `pyproject.toml`'s pytest config** | *narrowing collection would make the gate pass by looking at less, which is the "adjusting the bands" failure* |

## 5. LIMITS

1. **`456` is what pytest COLLECTS, not what would pass.** *I do not know how many of the 456 pass,
   because they still cannot all run together.*
2. **The `ast` split is heuristic** -- *it counts any module-level expression/assert/loop as "work";
   some are harmless constants.*
3. **The individual witnesses DO pass standalone**, which is how the project has actually been
   verifying things. *The gate is broken; the verification is not necessarily.*

## TLDR

We have a command that is supposed to run every check in the project and confirm it passes. **It has
been running none of them for two days, and saying PASS while it did.**

The cause is small and unlucky. One file in the checks folder is really a standalone script rather
than a test. It ends by telling the program to exit — which is correct when you run it yourself, and
fatal when the test runner merely *loads* it. The runner crashes on the spot and never gets to any of
the **456** checks.

**The reason nobody noticed is worth more than the bug**: that script prints "RESULT: PASS" as its last
action *before* the crash, so the report opens with a pass line and hides the abort further down.

**And it isn't one file.** Of 64 files in that folder, 33 are proper tests, **26 are tests that also do
work when merely loaded**, and 5 are scripts pretending to be tests. Fixing the first crash just moved
the failure to the next one — two independent checks that each redirect the same setting to their own
temporary folder, which is fine one at a time and contradictory when loaded together.

**I fixed the one line that aborts everything and stopped there.** Sweeping through thirty files
adjusting when their code runs is precisely the kind of change that looks mechanical and isn't. And I
did not touch the test runner's configuration, because making the gate pass by having it look at less
would be cheating.

**Worth saying clearly: the individual checks do pass when run one at a time**, which is how everything
this week was actually verified. What is broken is the single command that runs them all.

## QUESTIONS

None — Q106 (the scoring sheet) remains open and is unrelated.

## NEXT STEPS

1. 🎯 **Decide the split: `verification/` needs either two folders or two naming conventions** -- one
   for pytest tests, one for standalone witnesses. *Until then `run_certification.py` cannot work,
   whatever is patched.*
2. **Until it does, `run_certification.py`'s output may NOT be read as evidence** *-- and its leading
   `RESULT: PASS` line is actively misleading.*
3. *Method note: **this was found by verifying my own change** -- I ran the gate to check I had broken
   nothing, and the gate had been broken since before I started.*
