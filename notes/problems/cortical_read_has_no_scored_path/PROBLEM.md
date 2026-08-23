---
priority:
review: EXCELLENT
review_text: Refuted my brief with evidence, found a 100% leak in the only prior scoring, and refused to over-claim.
---
> 🔻 **THE REVERIFY COMMAND IS WRONG -- AND MY FIRST DIAGNOSIS OF WHY WAS ALSO WRONG (08-23).**
> Running `SOLVED.md`'s command under `HDI_FRESH_RUN` exits 0 after `224s` leaving an EMPTY fresh
> directory. **I first wrote that the cell "silently no-ops against an empty directory". It does
> not.** Reading `main()`: `--mode` **defaults to `"smoke"`** (line 393); in smoke mode the cell does
> the full work and then **PRINTS instead of calling `record_unit`** (413-415), then `return 0`
> (419-421). **The 224 seconds were real work being thrown away.**
> ✅ **THE FIX IS ONE FLAG: the reverify command must pass `--mode full`.**
> 🚨 **AND THE GENERAL POINT, WHICH IS BIGGER THAN THIS CELL: `tools/reproduce.py` RUNS CELLS WITH
> NO ARGUMENTS, so it CANNOT reproduce ANY cell whose default mode is smoke -- it will report
> `NOTHING_RECORDED` every time and look like a broken cell rather than a wrong invocation.**
> ✅ **AND WITH THE TOOL FIXED, IT REPRODUCES: `724` of `725` numeric fields IDENTICAL.** The single
> difference is `/result/read_seconds` (`380.8` -> `507.4`) -- **wall-clock time, which is supposed
> to vary.** `units 0 -> 1`, `classify_run: RECOMPUTED`, landed directory unchanged.
> ➡️ **This solution is VERIFIED. The apparent failure was entirely my tool's invocation.**

# MY REVIEW OF THE SUBMISSION: **EXCELLENT**

*(reviewed 2026-08-22 by the strategy session, which owns integration. **Checked against the
artifacts and by direct measurement, not by re-running their pipeline** -- a re-run shares the
pipeline's bugs.)*

> **THIS BRIEF WAS WRONG AND THEY PROVED IT RATHER THAN WORKING AROUND IT.** I wrote that the organ
> "has never been scored." It had been, three days earlier, with the same task and the same floors,
> and it had already failed. **They found that, checked the old cell was the current version on the
> right corpus with the right metric before building on it, and said so plainly.** *A solver who
> corrects the brief is worth more than one who satisfies it.*
>
> ? **AND THE OLD RESULT WAS MEASURED ALMOST ENTIRELY ON DATA THE SYSTEM HAD ALREADY READ:
> `298`, `300` and `300` of `300` test sentences, on three seeds.** The one prior scoring of this
> organ was effectively an open-book exam. *The leak flattered the organ and it lost anyway, so
> removing the leak makes the negative STRONGER -- which is the honest direction to report and the
> one they reported.*
>
> ? **I MEASURED THE THING THAT WOULD HAVE SUNK THEIR OWN SPLIT, AND IT HELD.** Their clean test set
> starts where the reading stopped, counted by sentences DELIVERED. If reading consumed more of the
> book than it handed back, their "unread" set would quietly contain read sentences -- the exact
> defect they had just caught in someone else's cell. **Measured directly at three settings: the
> book cursor advances by EXACTLY what is delivered, gap `0` every time. Their split is clean.**
>
> ? **ONE SENTENCE OF THEIRS IS WRONG, AND THE TRUTH IS TIDIER THAN WHAT THEY WROTE.** They blame
> the leak on the reading call running past what it was asked for. It does the OPPOSITE -- ask for
> 3,000 and it delivers 1,150, which is a separate landed finding of mine. **The real cause is their
> own loop shape: reading in chunks until a 16,000 target is passed lands at 16,600, and the old cell
> drew its test items from the FRONT of what it called held-out -- which is precisely those 600
> sentences.** *That explains `300 of 300` exactly, where "the reader overshoots" does not.* **The
> measurement is unaffected; only the label on the cause was wrong.**
>
> **WHAT I MOST WANT REPEATED: they ran the test that could have exonerated the organ, and reported
> it as underpowered instead of as a win or a verdict.** The task here rewards guessing a word that
> sits next to other words, which is what a word-counter is best at and NOT what this organ is for.
> They stratified out the cases where counting cannot help -- and found nothing there either -- then
> labelled it a direction rather than a finding because only 43 items qualified, and named the
> follow-up that would settle it. *That is the standing rule against turning one unfavourable test
> into "impossible", applied without being asked.*
>
> **NOT LANDED, CORRECTLY.** They left `hdlab/` untouched per Q111 and wrote the slot-note change out
> for me, with a revival criterion framed in terms of what the organ is FOR rather than "someone
> should score it." **That hand-off is mine and is still open.**

# PROBLEM: THE CORTICAL READ HAS NO SCORED PATH, SO NOBODY KNOWS IF IT IS ANY GOOD

**slug:** `cortical_read_has_no_scored_path` · **opened:** 2026-08-22 by the strategy session

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.** *A dropped precondition invalidates the
> declared gate even when the result may be fine.*

---

## THE PROBLEM IN PLAIN LANGUAGE

`hdlab/cortical_recall.py` is slot **B3'** in the substrate's architecture table, and it exists
because of a specific measured defect: **ablating consolidation to zero left the read-out identical
in 9 of 12 cells, because every retrieval route addressed the EPISODIC store.** Under CLS,
consolidated knowledge should be read from CORTEX. This is that route.

It is `NEEDS_ADAPTER` for one stated reason: **"no SCORED path calls it yet."**

**Your job: build that scored path — a held-out task where consolidated knowledge is required,
with floors and a CI — and report what it scores.**

## WHY THIS ONE

**It is the only organ whose absence was named as this substrate's largest measured fidelity
defect, and it has never been scored.** Everything said about it so far is diagnostic.

**And the strategy session has taken it as far as diagnostics can go** (2026-08-22), which is why it
is being handed over rather than continued:

- ✅ **The route is LIVE and consolidation-dependent.** Ablating consolidation changed the read on
  **`8/8` probes**, against a positive control where the same config run twice is identical `8/8`.
  *So it is not inert — that question is closed.*
- 🔻 **But it shows no detectable semantic SELECTIVITY**, and the hypothesis that it did was
  **refuted by its own control** (see below).

## MEASURED vs INFERRED

**MEASURED (all 2026-08-22, all on the strategy session's own runs):**

| finding | number |
|---|---|
| consolidation-sensitivity | changed on `8/8` probes; positive control identical `8/8` |
| within-pool ranking vs a random term from the same pool | `+0.0675`, CIs overlap — **NOT_SEPARATED** |
| consolidated vs read-but-not-consolidated, frequency-matched | `+0.1514`, `n=24` terms — **NOT CI-separated** |
| **what consolidation selects for** | **CONCRETENESS `+0.631`, `p = 0.00040`, survives Bonferroni x12** |
| 🔻 **the same test with a CONCRETENESS-matched floor** | 🔻 **`0.1966` vs `0.1891`, `p = 0.42` — THE EFFECT VANISHES** |

> ### 🔑 **READ THAT LAST ROW BEFORE PLANNING ANYTHING. The "consolidation selects semantically relevant terms" hypothesis is REFUTED, not merely underpowered: match the floor on concreteness and it dies. Concrete words resemble other concrete words, and the probes were all concrete.**

**INFERRED, NOT MEASURED:**
- 🔻 **That the cortical read is USELESS.** Not shown. **Every measurement above is a similarity
  statistic, not a task** — and a statistic the mechanism optimises may diagnose, never decide.
- 🔻 **That the consolidation gate READS concreteness.** It correlates; the gate may be entirely
  blind to the property. Concrete words may simply be the ones that accumulate `min_confirm=4`
  traces across passes.

## ALREADY TRIED

- **Two yardsticks.** WordNet Wu-Palmer was too blunt — both arms sat at exactly `0.3333`, its
  taxonomy floor. The sensorimotor-norms cosine is sharper (random pairs read `-0.0131`) **and is
  independent of the mechanism for a measured reason: `read()` never consults the norms** (runtime
  counters on `grounded_similarity` / `grounded_vector` / `_table` register `0` calls).
- **A unit-of-analysis error, caught and corrected:** bootstrapping over 400 *draws* from 24 *terms*
  gave clean separation; over TERMS it overlaps. **The term is the unit. Do not resample pairs.**
- 🚫 **DO NOT re-run the similarity-statistic family.** It has been run four ways and the answer is
  the same each time. **The missing thing is a TASK.**

## VERIFY BEFORE YOU START

1. **`Substrate.read(n_sentences=N)` DOES NOT READ `N`** — it visits at most 4 patches and stops
   (`substrate.py:548`, `max_patches=4`). Asked 8,000, delivers ~1,000. **Check
   `ReadResult.n_sentences` and `.short_read`, and state the corpus size you ACTUALLY read.**
2. **The consolidated pool is small** — ~30 terms per `read()` call. If your task needs more, you
   need more CALLS, not a bigger `n_sentences`. **Board Q114 is open on whether that is intended.**
3. `python tools/slot_status.py cortical` — the slot's own rationale, including why the name is
   called "imperfect" there.
4. `python tools/before_you_start.py "score the cortical read"` — and read every row.

## THE BAR

**A TASK SCORE with a CI-separated margin over the strongest floor you actually RUN, on a held-out
set.**

- 🚨 **THE TASK MUST REQUIRE CONSOLIDATED KNOWLEDGE.** If an episodic-only arm scores the same, you
  have measured nothing — that is precisely the 9-of-12 defect this organ exists to fix, and it is
  the first control to build.
- 🚨 **A CONCRETENESS-MATCHED FLOOR IS MANDATORY, NOT OPTIONAL.** The last hypothesis on this organ
  died to exactly that control. **Match frequency AND concreteness, or the result is uninterpretable.**
- **The information-free twin must LOSE:** the same pipeline drawing from the pool at random.
- **Report `n`, the pool size, and how many sentences were actually read.**

**A legitimate outcome is that the cortical read scores at its floor.** Say so plainly — the organ
being live and consolidation-dependent while adding nothing is a real and useful finding.

## FILES AND ENTRY POINTS

| what | where |
|---|---|
| the organ | `hdlab/cortical_recall.py`; `Substrate.recall_cortical(sentence, target, space=...)` |
| the consolidated contents | `Substrate.consolidated()` — term -> accepted meaning |
| the independent yardstick | `hdlab/grounded_similarity.py` (**not consulted by `read()`** — that is why it is independent) |
| the slot's own rationale | `python tools/slot_status.py cortical` |
| all of the above, with its limits | `notes/THE_CORTICAL_READ_IS_CONSOLIDATION_SENSITIVE_WHERE_THE_EPISODIC_ONES_WERE_NOT_2026-08-22.md` |

## DO NOT QUOTE

- 🚫 **`+0.1514` as evidence consolidation selects semantically.** **It is refuted** by the
  concreteness-matched floor (`p = 0.42`).
- 🚫 **`8/8` as evidence the cortical read WORKS.** It shows only that it responds to consolidation.
- 🚫 **The concreteness result as a claim about the GATE.** It is correlational.
- 🚫 **`30` consolidated terms as a property of consolidation** — it is a property of one `read()`
  call, and the read cap is why.
