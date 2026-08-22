---
priority:
review: EXCELLENT
review_text: Built the switch, proved a re-run can FAIL, and found a real bug in my own detector.
---

> # MY REVIEW OF THE SUBMISSION: **EXCELLENT**
> *(reviewed 2026-08-22 by the strategy session, which owns integration. **I re-checked this against
> the artifacts myself instead of re-running their pipeline** -- a re-run shares the pipeline's bugs.)*
>
> **THEY DID THE HARD PART, WHICH WAS PROVING A RE-RUN CAN COME OUT DIFFERENT.** Anyone can make a
> re-run repeat a number; the deliverable was a re-run that can DISAGREE. They broke one input on
> purpose, re-ran through the new path, and the answer flipped from pass to fail -- then re-ran it
> unbroken and got the original answer back. Both directions, which is what makes either one mean
> anything. The witness passes here, in my hands: `verification/test_recompute_can_fail.py` RESULT
> PASS.
>
> **AND THEY FOUND A REAL BUG IN MY OWN TOOL, WHICH IS THE HIGHEST-VALUE THING IN THE SUBMISSION.**
> My replay detector counted LINES in the record file, while the thing it describes counts unique
> entries -- so it overstated how much work a re-run would skip. **I confirmed it at full scale
> rather than taking it on report: 21 of 421 record files repeat an entry, 70,644 lines against
> 70,191 distinct ones, a `0.65%` overstatement.** Their 3-in-60 sample rate reproduces at 21-in-421.
> Fixed in `6d5f480d1`, controlled both ways. *And deflating it, since the finding sounds bigger than
> it is: the headline counts CELLS, a cell replays if the count is above zero at all, and no cell
> changes side. Only the secondary total moves.*
>
> ? **THEIR SELF-DECLARED WEAKEST CLAIM RECOUNTED AND HELD.** They said the first thing they would
> withdraw is the `80 / 264 / 56` split of how many experiments the clean fix covers for free.
> **Recounted independently from disk: `87 / 275 / 59` of 421 -- same proportions (`20.7%` vs `20.0%`
> covered).** *That is the right instinct to have flagged and it survived the check.*
>
> ? **WHAT I MOST WANT REPEATED: they named five places THE DISK OUTRANKED THE BRIEF, including two
> where my brief was simply wrong** -- the census had drifted, and my worry that the 12,137-piece
> experiment would be expensive to redo is **backwards** (it is one of the cheapest, 2 minutes,
> while a 619-piece one takes 13 minutes). *A solver who corrects the brief is worth more than one
> who satisfies it.* They also disclosed drift THEY caused, and answered "is this brain-work?" with
> **"mostly no, and I will not dress it up"** rather than retrofitting a justification.
>
> **THE ONE THING I WOULD HAVE WANTED DIFFERENT, and it is small:** the deciding control runs on a
> demo experiment they wrote, not on a real landed one. The 60 real experiments were exercised
> read-only. That is the correct safety call and they said so plainly -- but it means "a re-run can
> fail" is proven on a purpose-built case, and the first real re-verification is still the real test.
>
> **NOT LANDED, CORRECTLY.** They left the shared harness untouched per Q111 and wrote the exact
> change out for me. **That hand-off is mine and is still open.**

> # 5️⃣ **PRIORITY 8 of 8 -- AN ENABLER, AND IT MATTERS MOST ONCE FIXES START LANDING.**
> *(ranked 2026-08-22)*
> **`399` of `7,868` landed cells (`5.1%`) replay their checkpoints on re-run: same verdict, same
> numbers, `elapsed 0.0s`, no work done. A landed cell cannot currently be falsified by re-running
> it.**
> 🔻 **IT RANKS LAST BECAUSE IT IMPROVES OUR ABILITY TO CHECK, NOT THE SYSTEM ITSELF** -- and
> nothing here says any landed number is wrong. *Its value rises sharply the moment problems 1-3
> start producing changes that need verifying, so this is a "soon", not a "never".*
> ✅ *A DETECTOR already exists (`tools/reproduction_check.py`) and will tell you a re-run proved
> nothing. What is missing is the ability to make it recompute.*

# A LANDED CELL CANNOT BE FALSIFIED BY RE-RUNNING IT

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**
> *Reason, so you do not self-negotiate it: a dropped precondition invalidates the declared gate even
> when the result may be fine. "The number probably didn't change" is not yours to decide silently.
> Disclose; the operator decides.*

---

## THE PROBLEM IN PLAIN LANGUAGE

Long experiments here save their progress unit by unit, so a crash loses at most the one in flight.
That rule is correct and `CLAUDE.md` makes it mandatory -- killed runs used to lose everything.

**It has a consequence nobody designed: re-running a finished experiment skips all the work.** It
reads its saved units back, prints the same verdict line and the same numbers, and exits. Measured on
one cell: **`elapsed 0.0s`, five resume-and-skip lines, every number identical.**

**So re-running a landed cell cannot disconfirm it.** The re-run and a genuine reproduction are
indistinguishable unless somebody reads the elapsed time and notices it was zero.

**Your job: give the harness a way to recompute into a FRESH output directory, without deleting
anything, and prove that a re-run through it can actually FAIL.**

## ✅ **TEST 4 ANSWERED 2026-08-22, BY THE DEFECT FIRING IN THE WORKING TREE THE SAME DAY**

**When this brief was written its cost was hypothetical -- "a landed cell cannot be falsified by
re-running it" -- and it said so honestly, with ONE observed instance.**

**It stopped being hypothetical hours later.** A routine `git status` during a restart re-read found
**`63` `metrics.json` modified and `3` deleted in the working tree, of which `54` had a CHANGED
`ts_iso` and IDENTICAL numbers.** Worked example: `exp_bridge1_twostage_event_situation_v2`,
`elapsed_s 31.36 -> 0.0355`, `ts_iso 2026-08-05 -> 2026-08-22`. **A re-run replayed its checkpoints,
did no work, and restamped a landed record with today's date. Oldest true date `2026-07-04`.**

> ### **THAT IS THE DEFECT COSTING US, NOT AN ALTERNATIVE BEING BETTER: 54 RECORDS SILENTLY RE-DATED, CAUGHT BY A ROUTINE RE-READ RATHER THAN BY ANY GUARD.**

⚠️ **AND THE HONEST LIMIT: THIS IS MISLABELLING, NOT DATA LOSS.** *`git show HEAD:<path>` returns
every one intact, deletions included. It matters because TOOLS READ THE FILE, NOT THE HISTORY -- and a
staleness check is exactly what started the goal-bearing re-land the same afternoon.*
✅ *True dates preserved in `notes/TRUE_LANDED_TIMESTAMPS_BEFORE_THE_08-22_REPLAY.md`.*
🔑 **`tools/reproduction_check.py` can NAME a replay after the fact. Nothing PREVENTS one
overwriting a landed record, and that gap is exactly this brief.**

## WHY THIS ONE

**Because "I re-ran it and it reproduced" is currently not evidence, and it is a sentence this
project says often.** The author of the original note wrote it about themselves:

> *"I would have reported verified and reproduces exactly on the strength of the verdict line alone,
> which is what a verification step exists to prevent."*

**Archive scale, measured: `399` of `7,868` landed cells (`5.1%`) carry checkpoint units, so
re-running any of them replays. A further `18` dirs carry units with no `metrics.json`. ZERO unit
files are empty -- there is no benign subset. The largest would skip `12,137` units.**

➡️ **It also gates other work.** Several open threads -- re-landing the stale `HARD_FAIL`, the
`0.1667 -> 0.3889` divergence, checking whether other cells are stale the same way -- all need a
cell that can genuinely be re-run. **Right now none of them can be.**

## MEASURED vs INFERRED

**MEASURED:**

- `399 / 7,868 = 5.1%` of landed cells would replay; `18` orphan dirs; `0` empty unit files;
  largest `12,137` units. *(`python tools/reproduction_check.py --census`, enumerated from disk.)*
- The mechanism is small and legible: `tools/exp_checkpoint.py` writes `<output_dir>/units.jsonl`,
  and `completed_units()` is what every cell skips against.
- On the one cell tested: `elapsed 0.0s`, verdict and numbers byte-identical, no work done.
- **What DID recompute on that cell was its built-in `--self-test`**, which uses its own fixed
  configuration and independently reproduced the pattern -- *that is why it is a check and not a
  replay.*

**INFERRED, NOT MEASURED:**

- 🔻 **That the other 398 behave the same way.** One cell was tested. **The census counts cells that
  CAN replay; it does not prove each one DOES.** Verifying a sample of them is part of this job.
- 🔻 **That landed numbers are correct.** Nothing here casts doubt on any of them. **The defect is in
  our ability to check, not in the results.** Do not let this problem turn into a claim that the
  archive is wrong.

## ALREADY TRIED

- **`notes/RESUMABILITY_DEFEATS_REPRODUCTION_CHECKING_2026-08-22.md` (`61e3b39fc`)** diagnosed it and
  **deliberately did not fix it**, because the fix touches the cell harness across every experiment.
  It proposed *"a verify or fresh-units flag writing to a new output directory and ignoring existing
  checkpoints, recomputing without deleting anything."* **That proposal is the starting point; it was
  never implemented.**
- **`tools/reproduction_check.py` + `verification/test_replay_is_not_reproduction.py` (08-22)** make
  the unsafe reading unrepresentable -- `ReproductionVerdict` has no `__bool__` and no attribute
  called `reproduced`. **That is a DETECTOR, not a fix: it tells you a re-run proved nothing. It
  cannot make the run recompute.** Reuse it rather than writing another one.
- 🚫 **Forcing a recompute BY DELETING checkpoints is separately forbidden here** and has been
  auto-denied repeatedly. **The flag must write somewhere new and leave existing data untouched.**

## VERIFY BEFORE YOU START

1. `python tools/reproduction_check.py --census` -- confirm `399 / 7,868` still holds. *If it has
   moved, say so; these notes go stale within hours.*
2. **Reproduce the incident on a real cell before changing anything**: pick one from the census, run
   it, and observe `elapsed ~0.0s` with resume lines. **A fix for a bug you have not seen fire is a
   fix you cannot test.**
3. Read `tools/exp_checkpoint.py` end to end -- it is short, and `completed_units()` is the whole
   mechanism.
4. `python tools/before_you_start.py "make a cell recompute instead of resuming"` and **read every
   row it returns**, not the first.

## THE BAR

**A re-run through the new path must be able to FAIL. That is the whole deliverable.**

- 🚨 **THE DECIDING CONTROL, AND IT IS A POSITIVE ONE: take a landed cell, corrupt one input (change
  a seed, drop an item, perturb a constant), re-run through the fresh path, and show the verdict
  CHANGES.** *A path that always agrees with the landed number is indistinguishable from the replay
  it replaces -- **build the version that must disagree and check that it does.***
- **And the negative control: an unmodified fresh re-run must reproduce the landed number**, within
  whatever seed tolerance the cell declares. Both directions, or neither means anything.
- **Report `units_before` / `units_after` / `elapsed` for every run you call a reproduction**, and
  pass them through `tools.reproduction_check.classify_run`. **Quote the returned `status` string.**
- **Nothing is deleted.** Show that the original output directory is byte-identical afterwards.
- **State how many of the 399 you actually exercised.** *"It works" on one cell is what produced this
  problem in the first place.*

**A legitimate outcome: the flag is easy but recomputing is prohibitively expensive for the large
cells** (`12,137` units is not free). **Say so with timings** -- that turns an unbounded worry into a
priced decision.

## FILES AND ENTRY POINTS

| what | where |
|---|---|
| the checkpoint mechanism (short) | `tools/exp_checkpoint.py` -- `completed_units`, `record_unit`, `load_units` |
| the detector to REUSE | `tools/reproduction_check.py` (`--census`, `classify_run`) |
| its witness | `verification/test_replay_is_not_reproduction.py` |
| the original diagnosis | `notes/RESUMABILITY_DEFEATS_REPRODUCTION_CHECKING_2026-08-22.md` |
| the mandatory-checkpoint rule this must not break | `CLAUDE.md`, *"Multi-unit cell checkpoint/resume (MANDATORY)"* |
| a concrete cell that needs this | the stale `HARD_FAIL` re-landing (`0.1667` landed vs `0.3889` today) |

## DO NOT QUOTE

- 🚫 **`399` as a count of WRONG results.** It counts cells that *cannot be re-verified by re-running*.
  **Nothing here says any landed number is incorrect.**
- 🚫 **`elapsed 0.0s` as evidence a cell is broken.** It is evidence the harness resumed, which is the
  behaviour `CLAUDE.md` mandates.
- 🚫 **"the archive is unverified"** as a general claim. `5.1%` of landed cells are affected; the
  other `94.9%` have no checkpoint units and re-run normally.
- 🚫 **The one-cell `elapsed 0.0s` observation as a property of all 399** -- that is the inferred half
  above, and closing it is part of this job.
