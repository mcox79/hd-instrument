# PROBLEM: THE MANDATORY CERTIFICATION GATE HANGS, SO NOTHING CAN BE CERTIFIED

**slug:** `certification_gate_hangs` · **opened:** 2026-08-22 by the strategy session

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.** *A dropped precondition invalidates the
> declared gate even when the result may be fine.*

---

## THE PROBLEM IN PLAIN LANGUAGE

`CLAUDE.md` states a hard requirement: **"`python verification/run_certification.py` must pass on
`main`."** It is the gate every landed result is supposed to clear.

**It does not finish.** Run 2026-08-22 during a cell re-land: the pytest process sat **resident with
CPU flat at `371.4s -> 371.5s` for 11+ minutes**, having collected only **33 items** with one `F`,
and was killed after ~20 minutes.

**That is not a pass and not a failure. It is a gate that cannot return a verdict** — which is worse
than a failing gate, because a failing gate tells you something.

**Your job: find why it stalls, and make it either finish or fail loudly with a reason.**

## WHY THIS ONE

**Because every other result in this repo is supposed to be gated on it, and right now none of them
can be.** A pre-registration that says "run the cert gate before and after" cannot be satisfied. Work
either proceeds ungated or stops.

**It also has a documented history of failing SILENTLY rather than loudly**, which is why a hang
should not be assumed benign: on 2026-08-20 the same script **exited `3` and ran ZERO of its 456
collected tests while its own report opened with `RESULT: PASS`** — a module-level `raise SystemExit`
under a `test_*` name aborted the pytest session, and the PASS line printed before the crash. *That
was fixed. This is a different symptom in the same file, and the prior one proves this script can
report success while doing nothing.*

## MEASURED vs INFERRED

**MEASURED (2026-08-22):**
- CPU flat at `371.4s -> 371.5s` for 11+ minutes while the process stayed resident.
- Only `33` items collected at the point it was killed; one `F` among them.
- Killed at ~20 minutes. **Inconclusive — explicitly neither pass nor fail.**
- The killing session's own code change was **additive fields in one experiment script**
  (`per_item_predictions`, `scored_population_n`, `ambiguous_pred_count`); **`hdlab/` was untouched.**

**INFERRED, NOT MEASURED — do not start by assuming any of these:**
- 🔻 That the additive edit caused it. **It is not even the same subsystem**, and no before/after
  baseline was taken this session.
- 🔻 That it is a deadlock rather than a very slow test. `371.4 -> 371.5` in 11 minutes is
  *near*-flat, not provably zero.
- 🔻 That the one `F` is related to the stall at all.

## ALREADY TRIED

- **Nothing beyond killing it.** The session that hit this was a cell-author agent under instruction
  not to weaken gates; it disclosed the stall and stopped, which was correct.
- **The 2026-08-20 repair of this same file** guarded a module-level `SystemExit` behind `__main__`
  and `git mv`'d two safety-guard tests into a subprocess driver, taking collection from an abort to
  **`458` tests, zero errors**. *So the file WAS healthy at that point — start by finding what
  changed since.*

## VERIFY BEFORE YOU START

1. **Reproduce it, and time-bound the reproduction.** Run with `-x --timeout=<n>` if the plugin is
   available, or run collection alone (`--collect-only`) first — **that separates "collection hangs"
   from "a test hangs", and they are different bugs.**
2. **Get a baseline**: does it stall on a clean checkout of the last commit where it demonstrably
   passed? `458` tests / zero errors is the known-good figure.
3. **Identify WHICH test.** `-v` plus the last-started item is usually enough; `faulthandler` with a
   timeout will dump the stack of a genuinely stuck thread.
4. `python tools/before_you_start.py "certification gate hangs"` — and **read every row it returns**.

## THE BAR

**The gate returns a verdict, every time, within a stated time budget.**

- **Show the specific cause**, at runtime — the test, the import, the subprocess, the lock. *"It got
  slower" is not a cause.*
- 🚨 **A HANG MUST BECOME A LOUD FAILURE, NOT A LONGER WAIT.** If the fix is a timeout, the timeout
  must print WHAT it was waiting on. **A gate that can hang is a gate that can be quietly skipped.**
- **Positive control:** demonstrate the repaired gate FAILING on a deliberately broken test, so it is
  not merely returning green by refusing to run anything. *This file has already once reported
  `RESULT: PASS` while executing nothing.*
- **Negative control:** the full suite still collects its expected item count (~`458`) and passes on
  an unmodified tree.
- **Report the wall-clock time** of a full clean run. If the honest answer is "it takes 40 minutes",
  that is a finding and changes how the gate is used.

🚫 **DO NOT make the gate pass by narrowing what it runs.** Deselecting the slow test is the failure
mode this brief exists to prevent.

## FILES AND ENTRY POINTS

| what | where |
|---|---|
| the gate | `verification/run_certification.py` |
| its prior silent-failure repair | the 2026-08-20 fix: `SystemExit` guarded behind `__main__`, two guard tests `git mv`'d to `witness_*` |
| the subprocess driver those moved into | the existing witness driver (parametrisation grew `32 -> 34`) |
| the requirement itself | `CLAUDE.md`, *"Verification discipline"* |
| the session that hit the stall | the goal-bearing cell re-land, 2026-08-22 |

## DO NOT QUOTE

- 🚫 **`33 items` as a test count.** It is where the process happened to be when killed.
- 🚫 **The one `F` as a real failure.** It was never allowed to complete or be re-run.
- 🚫 **"the cert gate fails"** — it *hangs*, which is a different and worse thing.
- 🚫 **`458` as the current expected count** without re-checking; that was 2026-08-20 and this repo's
  notes go stale within hours.
