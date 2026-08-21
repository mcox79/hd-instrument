# **THE OWNER'S GUI COMPLAINT WAS ALREADY FIXED. WRITING THE GUARD FOR IT FOUND A CRASH THAT KILLS THE WHOLE PANEL REFRESH.**

**Owner, four times: *"they are all legacy and need to be removed"* (D6), *"this has been answered,
hasn't it?"* (D1, D2), and last night *"this made its way back into the gui questions - it should be
archived"* (D3, board Q100, 19:07:33Z).**

---

## 1. FIRST I MEASURED, AND THE COMPLAINT WAS ALREADY CLOSED

| the panel, right now | |
|---|---|
| real open questions | **1** (Q102) |
| legacy decision rows in the working list | **0** |
| archived | **40** |

**The suppression added on 2026-08-20 works.** *And the list is empty for a second reason worth
saying out loud: the owner emptied it themselves, by answering seven legacy rows one at a time over
three days, each time by typing a complaint into it.*

> ### **SO THERE WAS NOTHING TO FIX. WHAT WAS MISSING WAS ANY GUARD THAT IT STAYS FIXED -- and this project is 5-for-5 that a caution written as prose gets violated while a control written as code catches something.**

## 2. 🔴 **THE GUARD FAILED ON ITS FIRST RUN -- NOT ON AN ASSERTION, ON A CRASH**

**`TclError: Item dD1 not found`, thrown inside the refresh itself.**

*The row was registered in `_wait_rows` **before** the check that skips a settled row, so a
suppressed decision left an entry there with no matching item in the table. Those two records are
read together fifty lines further down: the selection-restore looks the kept row up in `_wait_rows`
and hands the id straight to `tv.selection_set()`.*

> ### ⚠️ **REACHABLE BY THE ORDINARY WORKFLOW: SELECT A DECISION, ANSWER IT, WAIT FOR THE NEXT REFRESH. That is precisely when the row disappears while still selected -- and it takes the WHOLE panel refresh down.**

**Fixed in both branches by registering AFTER the skip. The witness now asserts the GENERAL form --
every `_wait_rows` entry has a real table item -- rather than only the instance already fixed.**

## 3. 🔍 **AND THE EXISTING WITNESS HAD BEEN FAILING SINCE THE DAY OF THE FIX**

**Run against the PRE-EDIT modules it produces the IDENTICAL `TclError`** -- *so it was broken
before I touched anything, not by my change.* **It was also asserting that an answered decision
STAYS in the working list wearing an `ANSWERED` label -- the exact behaviour the owner asked to have
removed.** *The 2026-08-20 fix shipped without updating its witness; a witness that has been failing
ever since is WHY the crash went unseen.*

## 4. ✅ **AND TWO OF MY OWN CHECKS PASSED AGAINST STALE DATA BEFORE I CAUGHT THEM**

*A rebuild is deliberately refused while a row is selected -- and the rebuild itself selects the
first row, so my witness was engaged by its own first render and every later render was held.*
**Check C read the FIXTURE's rows and reported a clean pass having tested nothing.**

> ### **CAUGHT ONLY BECAUSE THE POSITIVE CONTROL SAT BESIDE IT. Both witnesses now disengage explicitly, and C asserts the live payload actually replaced the fixture.**

## 5. 🚫 WHAT I DELIBERATELY DID NOT DO

**Delete the section-9 parser.** *The ARCHIVE is built from the SAME `plan.decisions` list, so
removing it to clear the working list would destroy the record of what the owner answered --* **the
opposite of "archived". A check now fails loudly if anyone tries it.**

## TLDR

The owner said, for the fourth time, that settled decisions keep reappearing in the dashboard as
though still needing an answer. **I checked before changing anything, and it was already fixed** --
one real question, no stale ones.

**But nothing guaranteed it would stay fixed, so I wrote an automatic check. It failed immediately,
and not in the way I expected: it found a crash.**

The panel kept two lists of its own rows and they disagreed, so when a row vanished after being
answered the window tried to re-select something that was no longer there and **the whole panel
stopped updating**. It happens on the most ordinary sequence there is: pick a decision, answer it,
wait. **Fixed, and the check now covers the general fault rather than just this one instance.**

**Two things worth noting beyond the fix.** The older test covering this area had been failing since
the day the original fix landed, because it still demanded the old behaviour the owner asked us to
remove -- **which is exactly why the crash sat there unnoticed**. And two of my own new checks
initially passed while testing nothing, because the window refuses to refresh while a row is
selected. **Both were caught only because I had put a deliberately-failing control next to them.**

## QUESTIONS

None.

## NEXT STEPS

1. **Nothing owed on the dashboard complaint** -- it was already fixed; the guard is now in place.
2. **Q102 remains the open decision.**
3. *Method note, 6-for-6 now: **writing the control found a real defect the audit did not.** The
   measurement said "already fixed" and was right; the guard still paid for itself on run one.*
