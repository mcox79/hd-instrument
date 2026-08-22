# PROBLEM FOLDERS -- the hand-off protocol between the strategy session and the solver sessions

**Owner's design, 2026-08-22.** *"I'd like you to keep the long vision and longterm strategy here,
and create a folder with documents in which you identify hard problems to solve... I'll have a
separate session dig in to specifically solve those problems. I'll use opus 4.8 to do that, as I
find it more interactive and able to really dig in and solve bounded issues, while I'd like you to
keep the 10k view and integrate solved issues."*

## ⚠️ READ THIS BEFORE ANY BRIEF: `notes/LONG_TERM_PLAN.md` IS THE PHASE STRUCTURE AND IT OUTRANKS THESE BRIEFS

**It states five phases, each with a GATE and a KILL CONDITION, and the owner's status GUI parses it
live.** The problem folders are how work gets HANDED OVER; **`LONG_TERM_PLAN.md` is why those
problems are the ones worth doing, and in what order.** *A brief that contradicts it is a defect in
the brief.*

**Three things in it that a solver will otherwise re-derive or get wrong:**

- **PHASE 1 IS MEANING SUPPLY AND IT IS NAMED AS THE CURRENT BOTTLENECK.** *Brain structure:
  sensorimotor spokes feeding the anterior-temporal hub, PINNED.*
- **PHASE 3 (ADDRESSED STORAGE) IS EXPLICITLY "BLOCKED UNTIL PHASE 1 CLEARS."** *That is the
  reader/store coupling, already decided as an ORDERING -- do not re-argue it. Its gate is worded
  to catch exactly the trap: "addressed beats flat CI-separated on the REAL reading task, not in
  isolation. An isolation win is a construction proof; this project has repeatedly mistaken one for
  a capability."*
- **PHASE 2's KILL CONDITION FIRED on 2026-08-17** -- two independent bridging mechanisms, both
  null, both gated, one of them the owner's own. **Do not build a third bridging variant without a
  new reason.** *What it does NOT license: "relational bootstrapping is impossible". A child does
  acquire most of its vocabulary this way, so a miss is a fact about OUR implementation.*

---

## THE DIVISION

| | strategy session (this one) | solver session |
|---|---|---|
| **holds** | the 10,000-foot view, the plan, `STATUS.md`, the board, **and ALL integration into the live substrate** | ONE problem, deeply |
| **writes** | `notes/**`, **`hdlab/`** (the live substrate -- SOLE WRITER) | `experiments/`, `verification/`, and its own `notes/problems/<slug>/` |
| **must not** | 🔻 **work a FILED problem at all** (see Q113 below), or REWRITE a solver's `SOLVED.md` | **write to `hdlab/`**, or touch the plan, `STATUS.md`, `BOARD.md`, or another problem's folder |

> ### 🔑 **OWNER RULING, BOARD Q113, 2026-08-22 — AND IT CHANGES THIS TABLE IN BOTH DIRECTIONS.**
> **Verbatim: *"you can definitely start and run experiments and helpers. eliminate that line from
> your instructions. Remember that any 'problem' you have in the problems tab is going to be worked
> on, so try not to compete with that."***
>
> **(1) THE STRATEGY SESSION MAY NOW RUN CELLS AND SPAWN `hdi_*` HELPERS.** *This table was written
> when it could only measure, document and guard. That constraint is RETIRED — and it was doubly
> wrong: board Q109 had already retracted the `verification/`-is-closed half.*
>
> **(2) FILING A PROBLEM HANDS IT AWAY, IMMEDIATELY AND IN PARALLEL.** The briefs are not a queue
> waiting for attention; **they are being worked NOW.** So the strategy session's own build work must
> go to what is **NOT** filed. *Before Q113 this rule cost nothing, because this session could not
> build anyway. Now it is the difference between two sessions doing one job and two sessions doing
> two.*
>
> ➡️ **THE PRACTICAL TEST BEFORE STARTING ANY BUILD HERE: is there a folder for it in
> `notes/problems/`? If yes, it is not mine — the value I add is INTEGRATION, and integration begins
> when a `SOLVED.md` appears.** *`python tools/problem_ledger.py` lists what is filed; check it, do
> not recall it.*

> ## 📣 **OWNER INSTRUCTION, 2026-08-22: EVERY REVIEW PUTS ITS VERDICT AT THE TOP OF `PROBLEM.md`.**
> **Verbatim: *"on the problems tab, after you review the submissions, I want the beginning of the
> problem description to give your feedback. how well did the solver do? I want to know"*.**
>
> ➡️ **SO INTEGRATION HAS A THIRD STEP, AND IT IS OWNER-FACING:** re-verify -> append the
> `INTEGRATED_BY_STRATEGY` block to `SOLVED.md` -> **PREPEND a `SOLVER REVIEW` block to the TOP of
> `PROBLEM.md`.** *The owner reads the problems tab, and the tab shows the problem DESCRIPTION — so a
> verdict buried in `SOLVED.md` is a verdict they never see.*
>
> **WHAT THE REVIEW BLOCK MUST CONTAIN, because "they did well" is not feedback:**
> 1. **A plain verdict in the heading** — EXCELLENT / STRONG / ADEQUATE / WEAK, and the status it was
>    accepted at.
> 2. **WHAT MAKES IT GOOD OR BAD, SPECIFICALLY** — name the control they ran, the number they
>    volunteered against themselves, the thing they refused to claim. *Praise that does not cite
>    evidence is indistinguishable from politeness.*
> 3. 🔻 **WHAT DID NOT REPRODUCE UNDER MY OWN CHECK**, if anything — with the two numbers side by
>    side and whether the conclusion survives it. **A review with no friction in it has not been done.**
> 4. **ANYTHING THEY DID NOT CLAIM THAT MATTERS.** *The best property of the v2 eval bank — that its
>    majority class flipped away from the answer the organ cannot give — was not in the submission.*
>
> 🚫 **DO NOT GRADE ON EFFORT OR LENGTH.** A `PARTIAL` that correctly refuses to fix a non-defect is
> better work than a `SOLVED` that fixed the wrong thing — `stored_terms_are_stems` is the worked
> example.

> ### ⚠️ **ONE EXCEPTION, AND IT EXISTS BECAUSE THE PROTOCOL CONTRADICTED ITS OWN TOOL (found 2026-08-22 while integrating the first solution).**
> The strategy session **APPENDS** an integration block to `SOLVED.md` -- and only appends. That is
> how `problem_ledger.scan()` learns a result has been re-verified and folded in; without it the
> ledger reports every accepted solution as awaiting integration, forever. **The solver's own text
> is never edited or reordered.** *The rule as first written said "do not edit a solver's
> SOLVED.md", which made the mechanism I had already built into a violation of my own protocol.
> The tool was right and the prose was wrong.*

> ## 🔑 **THE SOLVER DOES NOT EDIT THE LIVE SUBSTRATE. OWNER RULING, BOARD Q111, 2026-08-22:**
> *"I honestly think that you should own all of the full integration... if we fracture our live
> substrate modification I fear we'll lose sight of state and keeping it fully updated. I want THIS
> session to own it all and ~subcontract out the target research to that other session."*
>
> **SO THE HAND-BACK IS A RESULT PLUS A PROPOSED CHANGE, NOT A LANDED ONE.** Prove the mechanism in
> `experiments/` and `verification/`, where you may write freely; state in `SOLVED.md` exactly what
> would have to change in `hdlab/` and why. **The strategy session re-verifies and lands it.**
>
> *This is not ceremony. The concrete hazard it prevents is documented: two writers on one live file
> already destroyed a full day's audit here, silently -- no error, no corruption, just a lost
> update. And a substrate whose state is tracked in one place is the only way "what is actually
> wired" stays answerable.*

**WHY THIS EXISTS AND IS NOT BUREAUCRACY.** Measured on this project, today: 13 commits, **zero**
touching capability code, because cell work routes to a subagent lane that is closed in the strategy
session. **The strategy session can measure, document and guard. It cannot build.** This protocol
opens the building lane rather than pretending the constraint is not there.

---

## THE FIVE RISKS, EACH FROM THIS PROJECT'S OWN MEASURED HISTORY

Every one of these has already cost this project real time. The protocol below is shaped around
them, not around tidiness.

1. **THE BRIEF GOES STALE.** *"Notes go stale within hours"* is a documented rule here, and on
   2026-08-22 the strategy session retracted a recommendation, un-retracted it, and re-retracted it
   inside three hours. **-> Every `PROBLEM.md` carries a `## VERIFY BEFORE YOU START` block with
   RUNNABLE COMMANDS, not just numbers. Run it first. If it disagrees with the brief, the DISK wins
   and you say so in `SOLVED.md`.**
2. **PRIOR WORK GETS MISSED.** Measured: **7 proposals in one night were already answered on disk.**
   A fresh session with a narrow brief is MORE exposed to this, not less. **-> Every `PROBLEM.md`
   carries a `## ALREADY TRIED` section with the query counts already run and the cells already
   read. Run `python tools/before_you_start.py "<what you are about to do>"` anyway.**
3. **THE NUMBER TRAVELS AND THE CAVEAT DOES NOT.** Three instances in one night. **-> Every number
   in a brief carries its scorer, n, population and floor INLINE, and every brief has a
   `## DO NOT QUOTE` list.**
4. **A SOLVED CLAIM THAT DID NOT SURVIVE ITS OWN CONTROLS.** Base rate here: **30 vetted HARD_PASS,
   1 upheld.** **-> `SOLVED.md` is not accepted on its summary. The strategy session RE-VERIFIES on
   disk before integrating, and `tools/problem_ledger.py` REFUSES a `SOLVED.md` that lacks a floor
   or a control.**
5. **TWO SESSIONS WRITING THE SAME FILE.** A registry lost-update already destroyed a full audit
   here. **-> Ownership is per the table above. Solvers touch `hdlab/`, `experiments/`,
   `verification/` and their own folder. The strategy session touches `notes/` (except
   `problems/*/SOLVED.md`).**

---

## THE FLAG -- MACHINE-CHECKED, NOT A WORD IN PROSE

**When a problem is solved, the solver writes exactly one file: `notes/problems/<slug>/SOLVED.md`.**

It must begin with this block, and **`tools/problem_ledger.py` refuses it otherwise** -- so the flag
cannot be raised on prose alone:

```
---
problem: <slug>                     # must match the folder name
status: SOLVED | PARTIAL | REFUTED  # REFUTED is a real, valuable outcome
bar: <the success criterion from PROBLEM.md, quoted verbatim>
result: <the number, with scorer, n and population>
floor: <the strongest floor actually run, with its value>
controls: <which controls ran, and what each excluded -- a control that excludes nothing is not one>
files_changed: <paths>
reverify: <a single command the strategy session can run to reproduce the headline>
---
```

**Then prose: what was built, what was measured, what was NOT established, and what you would
withdraw first if it turned out to be wrong.**

**Check the flag from anywhere:**
```bash
python tools/problem_ledger.py            # every problem, its state, and what is awaiting integration
python tools/problem_ledger.py --check    # exit 1 if any SOLVED.md is malformed or unintegrated
```

**`status: REFUTED` is a first-class success.** *A problem shown to be the wrong problem is worth
more than a problem half-solved, and this project's most useful days have been refutation days.*

---

## A PROBLEM THAT WAS PROPOSED AND MERGED RATHER THAN WRITTEN

**"READ-OUT DISCRIMINATION" WAS ON THE QUEUE AND HAS BEEN MERGED INTO `reader_meaning_channel`.**
*The framing was: a related word is in the top 50 of a plain count list for most words, but we
cannot put it FIRST -- "the answer is in reach and we cannot pick it out".*

**It is not a separate problem. It is the SAME TASK measured from the other side.** The pick-the-
right-one-of-50 instrument is exactly where the sensorimotor result was measured, and the
co-occurrence ceiling on it (`0.3104`, converged from two unrelated feature sets) is what says the
missing information is **not in co-occurrence at all**. *Writing both would have handed two sessions
the same task with different names -- which is the duplicated-work failure this protocol exists to
prevent, committed by the person writing the protocol.*

⚠️ **AND A RELATED FRAMING IS RETIRED, DELIBERATELY: do not open a problem aimed at the CLOZE
task.** Its ceiling is a tie with the dumbest available method (best achievable `0.0300` against our
`0.0150`), and a task whose best case is a tie with word-counting is not an instrument for detecting
understanding.

---

## WHAT A SOLVER SHOULD EXPECT FROM A BRIEF

Each `PROBLEM.md` has the same eight sections, in this order:

1. **THE PROBLEM IN PLAIN LANGUAGE** -- readable by the owner, no jargon, no organ names.
2. **WHY THIS ONE** -- what it blocks, and what it is worth if solved.
3. **MEASURED vs INFERRED** -- a hard line between them. *Everything under INFERRED is fair game to
   overturn, and overturning it is a result.*
4. **ALREADY TRIED** -- with verdicts and query counts, so you do not re-run a landed negative.
5. **VERIFY BEFORE YOU START** -- runnable commands. The disk outranks the brief.
6. **THE BAR** -- the success criterion, its floor, and **how we would know it failed**.
7. **FILES AND ENTRY POINTS** -- where to look, and what NOT to touch.
8. **DO NOT QUOTE / DO NOT REDO** -- numbers whose caveats do not travel, and routes already closed.

---

## THE STANDING RULES THAT APPLY TO EVERY SOLVER

*Short version of `CLAUDE.md`; read it in full before landing anything.*

- **A gate is a CI-separated margin over the STRONGEST floor actually run** -- never a bare number,
  and gate on the floor's UPPER bound.
- **Build the information-free version of your winning arm and check it LOSES.** Empty, constant,
  shuffled, or random-with-the-same-shape.
- **A caution written as prose gets violated; a control written as code catches something.** If a
  lesson recurs, put it in the code path.
- **Save the population you scored, not just the score.**
- **If a tool call is denied: STOP and report the denial verbatim.** Do not retry a variant.
- **Ask whether the experiment COULD have succeeded before asking why it did not.**
