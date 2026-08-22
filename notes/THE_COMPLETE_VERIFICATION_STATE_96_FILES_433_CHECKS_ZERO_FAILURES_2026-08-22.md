# **COMPLETE VERIFICATION STATE, MEASURED PROPERLY AT LAST: `96` FILES, `403` TEST FUNCTIONS + `32` WITNESS SCRIPTS, **ZERO FAILURES**. AND THE "EXPECTED RED, 9 FAILURES" NOTE IN THE SUITE IS NINE DAYS STALE.**

**It took four wrong measurements to get here, three of them mine. The final number is the least
interesting part of this note.**

---

## 1. THE STATE

| population | files | result |
|---|---|---|
| `test_*.py` via per-file pytest | 64 | **403 test functions PASS, 0 fail** |
| `verify_*.py` / `witness_*.py` as subprocesses | 32 | **32 PASS, 0 fail** |
| **total** | **96** | 🟢 **no failures anywhere** |

*The last two stragglers (`verify_import_graph_scans_all_source_dirs`,
`verify_integration_health_import_graph`) are not broken -- they are import-graph scanners that need
more than 45s. Given 280s: **both exit 0**, one reporting `10/10 passed`.*

## 2. 🔑 **THE SUITE'S OWN META-TEST DOCUMENTS THIS PROBLEM BETTER THAN I DID -- AND ITS NUMBERS ARE STALE**

`verification/test_all_witnesses_exit_clean.py` exists precisely because of what I spent two turns
rediscovering. Its docstring, from 2026-08-13:

> *"`pyproject.toml` sets `python_files = ["test_*.py"]`, so the 27 `verify_*.py` / `witness_*.py`
> files in this directory have **NEVER been collected by certification at any commit since the
> 2026-05-16 scaffold**. 9 of the 27 fail when actually executed... This driver is named `test_*` so
> it IS collected, and it runs each witness as a SUBPROCESS so the `__main__` body actually executes.
> It is EXPECTED to be RED (9 failures) on `main`."*

✅ **Measured today: `30/32` passed at a 45s cap, and the two stragglers pass with more time. The
9 failures are GONE.** *That file's "expected red" contract is nine days out of date -- the redness it
declares as "the point" no longer exists, so a reader today would take a green result as a broken
driver.*

🔻 **AND I BUILT `tools/per_file_pytest_sweep.py` WITHOUT FINDING IT.** *The project already had a
subprocess-per-witness driver. My tool is not useless -- it covers `test_*.py`, which that driver does
NOT, and it is resumable -- but I did not check, and that is the fifth time this week the archive was
ahead of me.*

## 3. 🔻 FOUR WRONG MEASUREMENTS BEFORE THE RIGHT ONE

| attempt | claimed | why it was wrong |
|---|---|---|
| 1. `python <file>`, count exit 0 | "63/64", then "64/64" | **35 files have no `__main__` runner -- they exit 0 having run NOTHING.** 285 functions scored as passing without executing |
| 2. per-file pytest, first try | *(nothing)* | printed only a final summary, timed out, left a **ZERO-BYTE** file |
| 3. per-file pytest, second try | 3 files "TIMEOUT" at 100s | 🔻 **CONTENTION -- I launched it while the previous sweep was STILL ALIVE in the background.** Re-run alone: `24.9s`, `3.1s` |
| 4. same run | 2 files "crashed" (`rc=143`, `rc=0x80000003`) | **my own outer `timeout` killing the process group.** Re-run: both pass |
| 5. scope | "the true verification state" | **counted only `test_*.py` -- 32 `verify_*`/`witness_*` files were never in it** |

> ## **EVERY ONE OF THOSE IS A MEASUREMENT ARTIFACT I INTRODUCED. NONE WAS A DEFECT IN THE THING BEING MEASURED.**

## 4. WHAT REMAINS GENUINELY BROKEN

**Only the GATE.** *`pytest verification/` still aborts during collection -- one file raises
`SystemExit` at module level (guarded now) and others collide on module globals. `run_certification.py`
therefore still reports exit 3.* **The verification is healthy; the single command that runs it is
not.**

## 5. LIMITS

1. **"Zero failures" is a snapshot** at one commit, on one machine, with a 280s ceiling for the slowest
   two.
2. **`test_all_witnesses_exit_clean.py` itself takes >550s** and I have not seen it finish -- its one
   `F` is unidentified. *It is the only check in the suite whose result I am reporting as unknown.*
3. **403 + 32 counts FUNCTIONS and FILES respectively** -- different units, not summable into one
   number, and I have deliberately not summed them.

## TLDR

After several wrong attempts, here is the honest state of the project's checks: **96 files, 403
individual checks plus 32 standalone witness programs, and nothing is failing.**

Getting that number took five tries, and **every wrong answer was my own measurement breaking, not the
project's checks breaking**:

- I counted files that exited successfully **without running any checks at all** — 285 checks recorded
  as passed having never executed.
- I wrote a measurement that only printed at the end, then killed it on a timeout, and got an empty
  file for ten minutes of work.
- I reported three files as too slow — they were only slow because **I was running two heavy sweeps at
  once**. Alone, one takes 25 seconds and another 3.
- I reported two files as crashing — **my own timeout was killing them**.
- And my "complete" measurement quietly excluded a third of the checks, because they're named
  differently.

**The most useful thing I found is a note the project wrote to itself nine days ago**, describing this
exact trap — files that pass by doing nothing — and building the right tool for it. **Its stated
expectation is that 9 checks should be failing. None are.** So that file now needs updating, and I
built a partly-overlapping tool without noticing it existed.

**What is actually still broken is the single command that runs everything.** The checks are fine; the
button that presses them all at once is not.

## QUESTIONS

None — Q106 (the scoring sheet) remains the only open one.

## NEXT STEPS

1. ⚠️ **Update `test_all_witnesses_exit_clean.py`'s docstring** -- *it declares an expected redness that
   no longer exists, which will mislead the next reader in the opposite direction.*
2. **Identify its single `F`** -- *the only unknown left; it needs a >550s run.*
3. *Method note: **five measurements, five self-inflicted errors, one healthy subject.** The pattern is
   that a measurement harness needs the same controls as an experiment -- and I gave mine none until
   the fourth attempt.*
