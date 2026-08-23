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

## 🔢 **PRIORITY -- OWNER INSTRUCTION 2026-08-22: *"I also want a priority for what problems to tackle first, on the problem page"***

> ## 🚨 **THE RANK AND THE RATING LIVE IN `PROBLEM.md`'s FRONTMATTER. PROSE AT THE TOP OF THE BRIEF IS NOT ENOUGH -- IT WAS TRIED AND THE OWNER SAW NOTHING.**
> **Both instructions were first answered by prepending markdown blocks to `PROBLEM.md`. The owner
> reported seeing neither, and the cause is structural: NOTHING ON THE GUI PATH OPENS THAT FILE'S
> BODY.** `problem_ledger.scan()` only ever read `SOLVED.md`; the single read of `PROBLEM.md`
> anywhere is `kickoff_prompt`, which takes the first line starting with `# ` and breaks -- and the
> blocks were BLOCKQUOTES (`> # ...`), so even that filter skipped them.
>
> ```
> ---
> priority: 2          # integer, 1 = do this first. Open problems MUST have one (cert-enforced).
> review:              # EXCELLENT | STRONG | ADEQUATE | WEAK -- my rating, set at integration
> review_text:         # one line; the full review stays as prose below
> ---
> ```
>
> **A DOC PARSED BY CODE IS COUPLED TO IT:** `tools/problem_ledger.py` `parse_brief_meta()` reads
> these; `tools/status_gui.py` renders them as the `#` and `MY RATING` columns and sorts the table by
> rank. **Change the key names in one place and you must change the other in the same commit.**
> ✅ *Enforced by `verification/test_problem_briefs_and_flags.py`: every OPEN problem carries an
> integer priority, priorities are unique, and no brief carries a broken annotation. The uniqueness
> test also fails if the parse silently returns nothing, so the ranking test cannot pass vacuously.*
> 📝 **THE PROSE BLOCKS STAY.** They are what a SOLVER session reads -- `session_start_hook.py`
> injects the whole brief body. Frontmatter is for the owner's window; prose is for the solver.

**Every open `PROBLEM.md` now OPENS with its rank and the reason for it.** The current order, and it
is ranked by **WHAT BLOCKS WHAT** and **WHAT IT COSTS** -- not by how interesting the question is.
*A ten-minute fix that corrects a live measurement error outranks a large job that is merely
important, which is why `score_counts_abstention_as_error` sits third.*

| | problem | why here |
|---|---|---|
| ~~1~~ | ~~`flat_store_destroys_the_code`~~ | 🔻 **REFUTED 2026-08-22 -- DO NOT START THIS.** Addressed storage held-out hit@1 `0.1399` vs a co-occurrence COUNTING floor of `0.3242`, CI-separated BELOW it. *Its isolation strength was exact-key memorisation (`0.9954`) that collapses held-out.* **It does beat the flat sum (`+0.0554`) -- a real sub-finding, and still not a capability win.** ➡️ *My "upstream of everything, a wiring job" ranking was wrong: the store was not the binding constraint. The bar caught it, which is what the bar is for.* |
| **2** | `substrate_never_resumes` | **Nothing survives the run that learned it, so no result compounds.** Also wiring: the persistence organ passes `9/9` at HEAD. Compounds with the read cap (~1,000 sentences per call) |
| **3** | `score_counts_abstention_as_error` | **TINY AND LIVE.** `_score` counts `AMBIGUOUS` as a wrong answer by omission, and it now bites `3` items under the learned overlay. *Near-zero cost, and it corrupts a number we actually use* |
| **4** | `reader_meaning_channel` | **The actual goal**, and it owns the blocker the others depend on: **`read()` never consults the meaning asset at all** |
| **5** | `certification_gate_hangs` | An enabler -- **but VERIFY THE PREMISE FIRST.** Collection completes in `34.7s`; `PER_WITNESS_TIMEOUT_S = 600` with witnesses legitimately taking 94-151s; "parent CPU flat" is this repo's documented false alarm. **It may be SLOW, not hung** |
| **6** | `cortical_read_has_no_scored_path` | B3' is live and consolidation-sensitive (`8/8` probes, clean control). **What is missing is a task with floors** -- and it should measure POOL SELECTION, not just ranking |
| **7** | `lookup_does_not_lemmatise` | Cheapest and largest (`+13.2` points, one line) **but NOT MEASURABLE until 4 lands** -- nothing calls the lookup during reading |
| **8** | `harness_cannot_recompute` | Improves our ability to CHECK, not the system. **Value rises the moment 1-4 start producing changes that need verifying** |

> ### 🔑 **THE RANKING RULE, SO IT CAN BE ARGUED WITH RATHER THAN TAKEN ON TRUST:**
> **(1) Does it block other problems? (2) Is the fix a WIRING job with a proven organ, or a build?
> (3) Can the result be MEASURED today, or is it stranded behind something unbuilt?**
> **(4) 🔻 IS THE PREMISE ITSELF MEASURED -- or only the existence of a fix?** *ADDED 2026-08-22,
> EARNED BY GETTING RANK 1 WRONG.*
>
> **Test 4 is the one that failed, and it failed silently.** `flat_store_destroys_the_code` was ranked
> **1 of 8** on tests 1-3: it looked upstream of everything, the replacement store already existed and
> was proven, and the result was measurable today. **All three were TRUE. It was refuted anyway** --
> addressed storage scores held-out `0.1399` against a co-occurrence COUNTING floor of `0.3242`,
> CI-separated BELOW it.
>
> **Because the PREMISE -- "the flat sum destroys the information, so replacing it will help" -- had
> never been measured.** What HAD been measured was that an alternative store existed and worked in
> isolation. **Those are different claims, and tests 1-3 cannot tell them apart.**
>
> ⚠️ **AND IT IS NOT MECHANICALLY DETECTABLE. I tried:** counting `MEASURED` / `INFERRED` markers
> across all 12 briefs returns ~3 of each for every one of them, which separates nothing. *Same blunt
> instrument that killed the docstring-promise detector this morning.* **So test 4 has to be ASKED,
> by a person, per brief:**
>
> > **"Which number says the DEFECT is costing us something -- as opposed to saying an ALTERNATIVE
> > exists?"** *If the honest answer is "none, but the fix is clearly better in principle", the brief
> > is a HYPOTHESIS wearing a problem's clothes, and its first job is to measure its own premise.*
> *That third test is why the cheapest and largest single gain sits at 4: a `+13.2`-point improvement
> nothing can observe is worth less this week than a wiring job that unblocks three others.*

> ### 📋 **TEST 4 APPLIED TO THE OPEN BRIEFS, 2026-08-22. This is MY JUDGEMENT, not a computation -- argue with it.**
>
> | brief | is there a number showing the DEFECT costs us? | |
> |---|---|---|
> | `organ_abstains_on_two_thirds_of_v2` | **YES** -- `82/124` unanswered, accuracy `0.2339` vs a `0.6048` floor. The defect IS the number | ✅ PASSES |
> | `reader_meaning_channel` | **YES** -- our channel `rho 0.0446` (CI includes zero) vs the asset's `0.3171`, paired `+0.2348` CI-separated. Evidence the CURRENT channel is the problem | ✅ PASSES |
> | `score_counts_abstention_as_error` | **YES** -- `3` live items scored wrong by omission, on a number we quote | ✅ PASSES |
> | 🔻 `lookup_does_not_lemmatise` | **NO.** Coverage would rise `0.6035 -> 0.7350` -- that is the ALTERNATIVE being better. **Nothing measures what the current lookup COSTS, and `read()` never calls it, so today it costs nothing observable** | ⚠️ **SAME SHAPE AS THE REFUTED #1** |
> | 🔻 `substrate_never_resumes` | **NO** -- and the brief says so itself: *"That resuming would HELP. NOT MEASURED."* The persistence organ passing `9/9` is the ALTERNATIVE working | ⚠️ premise untested |
> | 🔻 `harness_cannot_recompute` | **NO** -- `399` cells cannot be falsified by re-running, but there is **no instance where a replay concealed a wrong result.** The cost is epistemic and unquantified | ⚠️ premise untested |
>
> 🔑 **THE WARNING THAT MATTERS: `lookup_does_not_lemmatise` FAILS TEST 4 IN EXACTLY THE WAY `flat_store` DID** -- a large, well-measured gain from an alternative, and no measurement of what the defect costs. *It is the cheapest and largest single gain we have, and that is precisely what made the refuted one attractive too.*
> ➡️ **THIS DOES NOT MEAN THOSE THREE ARE WRONG. It means their FIRST DELIVERABLE should be a number showing the defect costs something** -- and for two of them that number cannot exist until something else is wired, which is worth knowing BEFORE the work starts rather than after.

**RE-RANK WHEN THE EVIDENCE MOVES, and say what moved.** *This order already differs from the one the
briefs were filed in -- `reader_meaning_channel` was written as "the highest-value problem in the
project" and is still the goal, but two upstream wiring jobs were found after it was filed.*

## 🔁 TWO STRATEGY SESSIONS ARE RUNNING. A LANE SPLIT, PROPOSED HERE BECAUSE THIS FILE IS WHERE WE BOTH READ.

**Measured from `git log`, not guessed.** Between 17:36 and 18:05 on 2026-08-22 two sessions
committed to `notes/BUILD_PLAN...md`, `notes/STATUS.md` and this folder **alternately, about a minute
apart** -- 17:59, 18:00, 18:01, 18:02, 18:02, 18:04, 18:05. Both are doing strategy work: filing
problems, ranking them, integrating solutions, editing the plan.

**The cost is not hypothetical and has been paid three times today:** the permissions audit answered
twice 44 minutes apart; `tools/adjudicate_floor_flags.py` written twice simultaneously with one copy
silently overwriting the other; and the cert-gate premise re-derived independently twenty minutes
after the other session had filed it with the same conclusion.

**PROPOSED SPLIT -- amend it here rather than in a note only you will read:**

| | |
|---|---|
| **WHOEVER FILES A PROBLEM OWNS ITS BRIEF.** | Ranking, re-ranking, and the review block are that owner's. Do not re-rank another's brief silently -- strike it through with the evidence, as the `flat_store` refutation correctly did. |
| **INTEGRATION GOES TO WHOEVER SEES `awaiting integration` FIRST.** | It is idempotent-ish: the `INTEGRATED_BY_STRATEGY` marker makes a second attempt visible rather than duplicated. |
| **THE PLAN: APPEND-THEN-FOLD, NEVER CONCURRENT RESTRUCTURE.** | Two of us folding the same block at once produced a line count that ROSE while both were removing lines. **If you are restructuring it, say so in a commit subject starting `PLAN-RESTRUCTURE:` and the other stands off.** |
| **RUN `tools/before_you_start.py` FIRST.** | Its concurrent-work section reads recent commits and the claim queue. It exists because of the duplications above, and every one of those three would have been caught by it. |

🔑 **AND THE CHEAPEST RULE, WHICH COSTS NOTHING: PUT THE THING YOU ARE ABOUT TO DO IN THE
DISPATCH QUEUE.** `python tools/dispatch_queue.py claim <id> --by <session>`. *It is already built,
already locked, and currently unused for strategy-level work by either of us.*

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

  IT MUST NOT OVERWRITE A LANDED RECORD, AND THIS IS NOT HYPOTHETICAL -- I TRIPPED IT ON 2026-08-23.
  Following one of these commands as written re-ran a cell IN PLACE and rewrote its landed
  `metrics.json` with a fresh `ts_iso` and `elapsed_s`. The science was byte-identical, so the cost
  was only the original timestamp -- but that is exactly the "54 landed records silently re-dated"
  incident this project already carries, and the `harness_cannot_recompute` brief named this precise
  hazard while its own protocol kept instructing people to trigger it. **3 of 5 reverify commands
  did.**

  PREFER, IN ORDER:
    1. a scaffold-free witness      `.venv/Scripts/python.exe verification/test_<thing>.py`
    2. a standalone measuring script that writes only to its OWN directory
    3. `.venv/Scripts/python.exe tools/reproduce.py <cell>` -- runs the cell into an EMPTY sibling,
       leaves the landed directory byte-identical, and reports REPRODUCED / DIVERGED / REPLAYED
  NEVER: a bare `python experiments/<cell>.py`, which writes straight into the landed directory.
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
