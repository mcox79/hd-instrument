# AUDIT OF MY OWN METHOD -- **57 COMMITS, 7 CODE CHANGES, AND 51% OF COMMIT SUBJECTS WERE CORRECTIONS**

**Owner, 15:40Z:** *"an audit of all the work you've been doing -- what has been successful and what
those wins are, and what has not been successful, and what you did in each case that helped achieve
success and failure. I'd like you to figure out a more efficient method for future development from
this. Do a deep job."*

**Counted from `git log`, not from memory.**

---

## 1. THE RAW SHAPE OF THE OUTPUT

| | |
|---|---|
| commits | **57** |
| notes created | **68** |
| **commits that changed CODE** | **7 (12%)** |
| commits that changed only notes | **50 (88%)** |
| **commit subjects containing a correction/withdrawal/"already done"** | **29 of 57 (51%)** |

***Half of what I committed was correcting myself or reporting that the work already existed.***

## 2. ✅ WHAT SUCCEEDED -- AND EVERY WIN HAS THE SAME SHAPE

**The seven code changes are the durable output.** Four are real:

| fix | what it was worth |
|---|---|
| **`experiment_index` prefers `final_verdict`** | 9 cells were reporting the wrong state, **2 reporting nothing**. Immediately surfaced a **hand-checked 90%-precision extractor** (`HARD_PASS`) and a **"reading works"** result both filed as failures |
| **`experiment_index` surfaces corrections** | 14 rows carry a `premise_correction`/`amendment` nothing had ever read |
| **`substrate.py` `n_grounded`** | a field **structurally incapable of being non-zero**; transposed key, silent `or 0` |
| **`capability_registry_audit` rooted at `substrate.py`** | the reachability audit **never started from the assembled substrate**, on a stale "it doesn't exist" claim |

**AND THE SUBSTANTIVE FINDINGS, all from reading:** 12 human-rated dimensions beat a 121M-token
encoder; **write-rate is a 4.3x lever and prediction-error adds nothing to it**; the incumbent's
semantic CI crosses zero; dense-material reading recovers 0.45-0.69 against a 0.19 floor.

### **WHAT ACTUALLY CAUSED EVERY WIN -- five moves, in order of yield**

1. **A CONTRADICTION BETWEEN TWO FIELDS OF ONE OUTPUT.** *`n_grounded=0` printed beside
   `anchors +68`. Both cannot be true.* **This found the only real code bug of the night, and five
   iterations of static tooling could not.**
2. **ENUMERATING A BOUNDED POPULATION COMPLETELY INSTEAD OF SAMPLING.** *20 `PENDING` cells -> 13
   already resolved. 9 `final_verdict` cells -> 9/9 divergent.* **Both were small enough to check
   exhaustively, and exhaustive is what made them conclusive.**
3. **RUNNING THE CODE INSTEAD OF GREPPING IT.** *`substrate.py` exists; `GRADED_COMPARATOR` is true;
   `grounded_similarity` is live.* **Three beliefs corrected by execution.**
4. **OPENING THE COMPANION FILE.** *The CI that killed my claim was in the cell next door. The v62
   note that corrected my v61 reading was one file over.*
5. **A POSITIVE CONTROL BEFORE BELIEVING A FIX.** *At 60 sentences the corrected key is ALSO zero --
   renaming it would have looked like success. 600 sentences proved it.*

## 3. ❌ WHAT FAILED -- **EIGHT WITHDRAWALS, ONE CAUSE**

| claim | what was actually true |
|---|---|
| "foraging loses on every outcome" | a **7.6x register bias** under a 1.2x effect |
| "the leak is refuted, so the finding is STRONGER" | a **second confound** was live |
| "96.5% of cells saved no outputs" | my scanner's **2 MB cap inverted its own bias** |
| "22x refusal asymmetry" | **93% pre-existed** in the foundation |
| "three islanded capabilities, the registry is blind" | the registry had **accurate rows for two** |
| "placement succeeds 3-15%" | the **companion cell was 11x better** |
| "the substrate is at or near chance" | a **fourth measurement** in `STATUS` says `+16.3pp REPLICATED` |
| "capacity is back on the table" | I quoted the **random arm**, and the random control moved with it |

**➡️ ONE CAUSE, EIGHT TIMES: I WROTE THE CONCLUSION BEFORE FINISHING THE READ.** *Not carelessness
about numbers -- every number I quoted was accurate. **The generalisation was drawn from a partial
population every time.***

## 4. 🔴 THE LARGEST SINGLE WASTE: **SEVEN PROPOSALS THAT WERE ALREADY ANSWERED ON DISK**

| I proposed | it was already |
|---|---|
| build the foraging organ | built, PINNED, run at 10k sentences |
| improve coreference this way | `HARD_FAIL` on that exact mechanism |
| turn on the graded switches | **already default-ON**, and already floored |
| hand-score 100 facts | a **BLIND** 100-row score existed, done and written up |
| gate writes by prediction error | **dissociated** -- random at the same rate ties it |
| sweep the write rate | **already swept**, four thresholds |
| wire the sensorimotor spoke | **already scored, 3 seeds, 40k sentences each** |

**EACH WAS ONE `experiment_index` QUERY AWAY.** *And I ran that tool faithfully -- **on the thing I
was BUILDING, never on the thing I was DOING.***

## 5. 🎯 **THE PROPOSED METHOD -- ORDER, NOT EFFORT**

**Nothing above is fixed by "be more careful". Every failure is an ORDERING failure and every win is
an ordering success.** Five steps, cheapest first:

> ### **STEP 1 -- QUERY BEFORE WRITING ANYTHING, ON THE *ACTIVITY* NOT JUST THE ARTIFACT.**
> *Query the verb: "hand-score", "sweep", "gate", "wire", "blind". **Seven wasted proposals were one
> query away, and I only ever queried the noun.*** **Cost: ~30 seconds. Tonight's yield: would have
> saved most of the session.**

> ### **STEP 2 -- ENUMERATE THE WHOLE POPULATION IF IT IS SMALL ENOUGH TO COUNT.**
> *`PENDING` was 20. `final_verdict` was 9. **Both fit on one screen and both were 100% conclusive.***
> **Sampling produced my withdrawals; enumeration produced my wins.**

> ### **STEP 3 -- OPEN EVERY ROW THE QUERY RETURNED BEFORE QUOTING ANY OF THEM.**
> *`query "cold placement"` returned 4. I read 1. **The 4th reversed the 1st.***

> ### **STEP 4 -- MAKE OUTPUTS PRINT QUANTITIES THAT CONSTRAIN EACH OTHER, THEN READ THEM AGAINST
> EACH OTHER.** *This is the single highest-yield habit found tonight and it costs nothing: **one
> contradiction in one printout found the only real bug.***

> ### **STEP 5 -- STATE THE CONCLUSION ONLY AFTER STEPS 1-4, AND NAME THE POPULATION IT COVERS.**
> *Every withdrawal would have been prevented by writing "on this sample, of this population" instead
> of a general claim.*

**AND ONE STANDING RULE THAT IS ALREADY 5-FOR-5:** **A CAUTION WRITTEN AS PROSE GETS VIOLATED; A
CONTROL WRITTEN AS CODE CATCHES SOMETHING.** *`rank_with_ties.py`, `replication_gate.py`,
`organ_map_cite.py`, the `final_verdict` fix, the corrections fix -- **every one caught a real error.
Every prose caution I wrote tonight, I later broke.***

## 6. ⚖️ THE HONEST BALANCE

**THIS SESSION PRODUCED NO NEW CAPABILITY.** *Zero organs built. 12% of commits touched code, and
four of those seven were repairs to instruments rather than to the substrate.*

**WHAT IT DID PRODUCE:** *two archive tools that now return the right answer, one real substrate bug
fixed, one audit rooted correctly -- and **roughly a dozen beliefs corrected**, several of which were
load-bearing in the plan.* **The archive is now measurably more honest than it was this morning.**

**IS THAT A GOOD NIGHT?** *For a system whose central problem is that it cannot tell what it already
knows -- **yes, but only once.** The same night repeated would be a bad night, because the yield came
from a backlog of unread results that is now substantially smaller.*

## TLDR

You asked what worked, what didn't, and how to be faster. I counted rather than guessed.

**The shape:** 57 commits, 68 notes, **but only 7 touched any code** — and **half my commit messages
were me correcting myself or reporting that the work already existed.**

**What worked, and it was always the same five moves:** noticing two numbers in one report that
couldn't both be true; **counting a small group completely instead of sampling it**; running the code
instead of searching it; opening the file next door; and proving a fix on a case where the right
answer isn't zero.

**What failed, eight times, was one thing: I wrote the conclusion before finishing the reading.**
Every number I quoted was correct. Every generalisation was drawn from part of the evidence.

**The single biggest waste: seven things I proposed building had already been done and answered** —
including one where the answer was the opposite of my assumption, written into a field on the
experiment specifically to warn the next person. **Each was one search away**, and I did run that
search — **on the thing I was building, never on the thing I was doing.**

**So the fix isn't "be more careful," it's the order of operations:** search first and search for the
*activity*; count the whole group when it's small; read every result before quoting one; make reports
print numbers that check each other; and only then write a conclusion, naming what it covers.

**One rule earned its place five times over: a caution written in prose gets broken; a check written
into the code catches things.** Every safeguard I put in code tonight caught a real error. Every
warning I wrote in prose, I later violated myself.

**Honest bottom line: no new capability was built tonight.** What was built is a more truthful
archive — two tools that had been returning wrong answers now return right ones, one genuine bug in
the substrate is fixed, and about a dozen beliefs, several load-bearing, are now correct. **That was
worth doing once. It wouldn't be worth repeating, because the backlog of unread results that made it
productive is now much smaller.**

## QUESTIONS

None.

## NEXT STEPS

1. **Adopt the five-step order explicitly** -- it is cheap and every failure tonight was an ordering
   failure.
2. **The next session should start with a build, not an audit** -- the archive is now honest enough
   that another reading pass would yield much less.
3. **Q96 is still open** and is the one experiment with a clear, cheap, unanswered question.
