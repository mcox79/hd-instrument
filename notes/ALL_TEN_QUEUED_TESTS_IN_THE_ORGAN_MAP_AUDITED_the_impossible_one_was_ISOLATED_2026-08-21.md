# **ALL 10 QUEUED TESTS IN `ORGAN_MAP` AUDITED FOR "CAN THIS TEST ACTUALLY RUN?" -- THE IMPOSSIBLE ONE WAS ISOLATED, NOT A PATTERN. AND THE BEST-SPECIFIED UNRUN TEST ON THE MAP IS D3.**

> # 🚫 **CORRECTED SAME NIGHT: "1 of 10" IS NOW "2 of 10", AND THE SECOND ONE IS D3 -- THE VERY TEST
> # THIS NOTE PRAISES IN SECTION 4.**
> **I went to prepare D3's test and measured its sweep variable. `hit@1 = 1.0000 at EVERY N from 1
> to 2000`, sd 0.0000, both sparsities -- and `use_ca3=False` gives the IDENTICAL 1.0000, so the
> DG projection solves it with no memory involved. The score does not move across the swept range.**
> **WORSE, AND IT HITS SECTION 4's OWN ARGUMENT: if CA3 is never consulted, the random-address arm
> reads 1.0000 too -- a FALSE "the allocator does not matter" on the one arm the design exists to
> protect.** *The knob that does move it is CUE DEGRADATION (collapse between 25% and 40%), which is
> exactly the metric `ORGAN_MAP`'s own METRIC line already records for this organ.*
> **THE DESIGN PRAISE IN SECTION 4 STANDS -- the random-address arm IS the right idea. The SWEEP
> VARIABLE does not.**
> ⚠️ **AND THE AUDIT BELOW HAD A BLIND SPOT: it asked "does the population its can-fail condition
> needs EXIST?" -- for D3 it does. IT NEVER ASKED WHETHER THE SCORE COULD *MOVE* ACROSS THE SWEPT
> RANGE.** ***A SWEEP IS ONLY A TEST IF THE SCORE MOVES ACROSS IT; two endpoint runs settle it.***
> ➡️ `notes/D3s_QUEUED_TEST_SWEEPS_THE_WRONG_VARIABLE_exact_cue_recall_is_solved_by_the_projection_alone_2026-08-21.md`

**Motivation:** tonight the B1 floor test was found to be impossible as written -- its can-fail
condition needed an OUT stratum that is EMPTY. **The obvious worry is that the map is full of
queued work that cannot produce a result, which would silently waste the scarcest resource we
have (cell authoring).** *This is the check. It is a NULL, and the null is the useful part.*

---

## 1. METHOD -- ENUMERATED, NOT SAMPLED

`grep '\*\*FLOOR TEST|\*\*CAN-FAIL|Can fail:'` over `ORGAN_MAP.md` returns **exactly 10 lines**.
**Small enough to read whole, so all 10 were read whole** -- sampling is what produced every
withdrawal this week. **Question asked of each: does the population / stratum / instrument its
can-fail condition requires ACTUALLY EXIST?**

## 2. RESULT

| # | line | test | can it run? |
|---|---|---|---|
| 1 | L1299 | **H2** -- share of newly-grounded terms that are EVERYDAY, free choice over 36 corpora | ✅ **and effectively RUN** (5 arms x 10k sentences; domain labelling exists -- it reported `textbook_biology 0.632`) |
| 2 | L1315 | **B4** -- held-out near-neighbour 2AFC on the LIVE path at d=1024 vs live d=256 **0.6395** | ✅ **RUNNABLE, GENUINELY UNRUN** (`P_LIVE_CONCEPT` never ran at d=1024) |
| 3 | L1323 | B4 -- "how it can fail" clause of #2 | ✅ part of #2 |
| 4 | L1346 | **B1/B2** -- change context-vector CONTENT, hold arithmetic fixed | ⏸️ **gated "strictly after step 2", blocker STATED** |
| 5 | L1362 | **E3** -- coref among >=2 plausible antecedents, **"n in the hundreds -- not n=10"** | ⏸️ **needs new annotation (have 57); the test NAMES its own shortfall** |
| 6 | L1405 | **D8+D4** -- interleaved OLD-vs-NEW retention after ingesting N new corpora | ⏸️ **gated on step 1, blocker STATED twice** (*"the loop reads the same 4 segments forever"*) |
| 7 | L1769 | B4 orthographic | ✅ *"already run"* -- and correctly says the remaining question is a WIRING decision, not a floor |
| 8 | L1823 | **B1 -- the one that could not run** | 🚫 **WITHDRAWN TONIGHT.** OUT stratum EMPTY: **0 of 86** probe words outside, **29/29** triples fully inside |
| 9 | L1860 | D2 attractor | ✅ *"none needed for the completion claim"*; names the discriminator (BASIN RATIO at matched recall, prior 1.00x) if revived |
| 10 | L1881 | **D3 -- one-shot cued recall, sweeping N to the collapse point** | ✅ **RUNNABLE, UNRUN, AND THE BEST-SPECIFIED TEST ON THE MAP -- see below** |

**➡️ 1 of 10 was impossible. The other 9 are sound: 3 already run or closed, 3 blocked WITH THE
BLOCKER NAMED IN THE TEST ITSELF, 2 runnable-and-unrun, 1 a sub-clause.**

## 3. ✅ **THE HONEST HEADLINE IS A NULL: THE DEFECT WAS ISOLATED**

**I expected a pattern and did not find one.** *The queued work is in better shape than the B1 case
suggested.* **Crucially, the three BLOCKED tests are not defects -- each states its own blocker in
its own text**, which is the behaviour we want: *a test that says "not n=10" is doing its job.*

**Why B1's was different, and it is a recognisable tell: it claimed to be cheap and runnable NOW**
(*"still needed, and it is cheap... a re-scoring of an existing cell, not a new experiment"*) **while
the other blocked ones say plainly that they are waiting on something.** ***THE TELL IS A TEST THAT
ADVERTISES ITS CHEAPNESS WITHOUT NAMING ITS INPUT.***

## 4. 🎯 **THE POSITIVE FINDING: D3 IS THE BEST-SPECIFIED UNRUN TEST ON THE MAP**

**D3 -- hippocampal one-shot write / index.** *`EXISTS` yes / `IS-REACHED` **no -- zero `hdlab/`
importers** / `IS-GOOD` unknown.*

> **"SMALLEST CAN-FAIL FLOOR TEST:** one-shot cued recall of N stored (context → lemma) pairs from
> the live anchor field after a SINGLE exposure, **sweeping N to find the collapse point**. Floors,
> each of which can fail: (i) **no-write arm** -- must sit at chance; (ii) **random-address arm** --
> the same write op to a randomly chosen sparse address instead of the DG-derived one, **so the test
> isolates the ALLOCATOR rather than the outer product**; (iii) shuffled-pair arm. **The organ is
> only interesting if it beats (ii), and (ii) is precisely the arm that would be omitted by someone
> testing the write op.** Report at our sparsity AND at the pinned 0.2%."

**Why this is the standout:**
1. **It pre-empts its own most likely false positive by name** -- arm (ii) -- which is the single
   most common failure in this project's history (a win that came from the wrong source).
2. **The write half is PINNED** (Marr 1971 one-shot Hebbian outer product, and
   `hippocampal_encoder.py:179` `W[ix_(nz,nz)] += outer(sub,sub)` **IS that equation**), while the
   **ALLOCATOR is UNPINNED and declared ours** -- so the fidelity bookkeeping is already honest.
3. **It sweeps to a collapse point rather than testing one setting**, which is the design that would
   have caught the write-rate sweep hitting its edge still climbing (Q96).
4. **It reports at our sparsity AND the pinned 0.2%** -- the parameter-vs-computation rule applied
   in advance, and our own record says the pinned 0.2% band was the WORST point in its own sweep.

⚠️ **NOT A RECOMMENDATION TO RUN IT TONIGHT** -- it needs cell authoring, which this session cannot
do. *It is recorded so that whoever gets that budget does not have to re-derive which queued test is
best posed.*

## TLDR

Earlier tonight I found that a job sitting in our reference document, described as *"still needed,
and cheap"*, **could never have produced an answer** -- it wanted to compare words inside a list
against words outside it, and there are no words outside it.

**The obvious worry was that the document is full of such jobs**, which would quietly waste the one
thing we are short of: someone's time writing experiments. **So I checked all ten queued jobs, whole
-- not a sample.**

**Good news, and it is a boring answer: only that one was broken.** Three are already done, three
are waiting on something and **say so in their own text**, and two are ready to run.

There is a recognisable warning sign, though. The broken one was **the only one that advertised
itself as cheap without saying what it needed as input.** The honest ones say plainly "this needs
hundreds of examples, not ten."

**And one genuinely good thing came out of looking:** the best-designed unrun test we have is for a
memory component that is currently connected to nothing. What makes it good is that it *anticipates
the way it could fool us* -- it insists on a comparison against doing the same thing to a randomly
chosen storage location, and notes that this is exactly the check someone would skip. That is the
mistake this project has made more than any other.

## QUESTIONS

None.

## NEXT STEPS

1. **No action needed on the other nine** -- this is a null, recorded so nobody re-runs the audit.
2. **The tell is worth keeping: a queued test that advertises cheapness without naming its input.**
3. **If cell-authoring budget appears, D3's one-shot recall sweep is the best-posed unrun test on
   the map**, and B4's d=1024 live-path 2AFC is the other runnable one.
