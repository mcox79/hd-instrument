# OWNER WAS RIGHT -- **BOTH PIECES EXIST. NEITHER HAS EVER TOUCHED REAL READING, AND THE GAP READER IS CALLED BY NOTHING.**

**Owner, 2026-08-21T13:00Z:** *"we did a bunch of work on this I believe - the reading part. We
explicitely built something that stored the knowledge we read. We also developed something that
tried to sense the ~distance from any new fact to the grounded foundation - which is essentially
what we need to read next. You should look for those experiments."*

**Both recollections are correct. I found them. The state they are in is the finding.**

---

## 1. WHAT EXISTS

| the owner's description | what it is | status |
|---|---|---|
| *"something that stored the knowledge we read"* | **`hdlab/hd_fact_store.py`** | built; **12 cells, 10 landed** |
| *"sense the distance from any new fact to the grounded foundation"* | **`hdlab/gap_driven_reader.py`** | built; **`exp_gap_driven_reader_controlled_v1` HARD_PASS 2026-08-12** |
| (adjacent) prerequisite ordering | `exp_curriculum_prerequisite_scaffold_consolidation_v1` | **HARD_PASS 2026-08-12** |

## 2. 🚨 **BUT THE HARD_PASS IS A CONSTRUCTION PROOF, NOT A CAPABILITY WIN**

`exp_gap_driven_reader_controlled_v1`, read from its own metrics:

| | |
|---|---|
| **elapsed** | **3.0 SECONDS** |
| trials | **8**, budget 2 |
| prereq identification precision | **REAL 1.0 / ABLATED 0.0** |
| doc prioritization top-1 | **REAL 1.0** / ablated 0.25 |
| grounding rate | **REAL 1.0** / ablated 0.0 / random 0.125 |

**EVERY REAL METRIC IS EXACTLY 1.0 AND EVERY ABLATION EXACTLY 0.0.** *That is the signature of a
constructed demonstration, not a measurement on text.* Its self-tests operate on the invented words
**`dravithex`** and **`velmara`**, and the module's own docstring says the driver *"uses a wholly
separate ... fresh, throwaway `HDFactStore`"*.

`exp_curriculum_prerequisite_scaffold_consolidation_v1` is the same shape: **0.4 seconds**, run_mode
`full`, `correct=1.0000 reversed=0.0000 scramble=0.0000`.

**➡️ THE MECHANISM IS PROVEN TO WORK IN PRINCIPLE. IT HAS NEVER BEEN SHOWN TO WORK ON REAL TEXT.**
*`MEMORY.md` already carries the distinction verbatim: **CONSTRUCTION-PROOF != capability-win.***

## 3. 🔴 **AND IT IS CALLED BY NOTHING**

Absence claim, made properly -- **with a positive control, because "I looked and did not find it" is
no evidence of absence:**

> Pattern `gap_driven_reader|rank_material|identify_missing_prerequisites` over `hdlab/`:
> **20 matches, ALL 20 INSIDE `gap_driven_reader.py` ITSELF. Zero in any other module.**
> *The pattern demonstrably matches -- that is the positive control -- and every match is
> self-referential.*

**The organ that senses distance-to-the-frontier has no callers.** It is a working instrument sitting
in a drawer, which is the same shape as the meanings problem: **built, correct, unconsumed.**

## 4. ⚡ **THE PAYOFF: THIS IS EXACTLY THE HOLE TONIGHT'S FORAGING DRILL FOUND**

Tonight established that the foraging organ -- which **does** run on real text, 10,000 sentences
across 19 corpora -- implements **Charnov's marginal value theorem**, a rule for **WHEN TO LEAVE** a
patch, and that MVT is **silent on WHERE TO GO**. That silence is filled by our patch-CHOICE
function, which `ORGAN_MAP` marks **UNPINNED**, and which is the half that failed.

**➡️ `gap_driven_reader.rank_material()` IS A PATCH-CHOICE FUNCTION. IT IS THE MISSING HALF.**

**AND `ORGAN_MAP` ALREADY WROTE THE INSTRUCTION, VERBATIM:**

> *"call the already-HARD_PASS `gap_driven_reader.rank_material()` with candidates from that registry
> **instead of the synthetic dict** -- **a call site, not new code**."*

*Note what that phrasing concedes: the map's author already knew the dict was synthetic.*

## 5. WHAT THIS CHANGES

1. **The next build is SMALLER than I told the owner an hour ago.** I ranked "patch-choice" as
   *equation unknown, needs inventing*. **The mechanism is built and self-tested; what is missing is
   a CALL SITE and a real-text evaluation.**
2. **It does not change the top recommendation.** Meanings-supply-the-prediction is still the only
   candidate that makes being wrong about a word *cost* anything. **But this one is much cheaper**,
   and the two are independent.
3. **The honest caveat, stated before anyone runs it:** wiring a 1.0-on-8-synthetic-trials mechanism
   to real text is exactly where perfect scores go to die. **Expect it to degrade; the question is
   how much, against the FROZEN and RANDOM floors that already exist at 10,000 sentences.**

## TLDR

You were right on both counts, and I found them.

**We built the thing that stores what we read** — it exists and a dozen experiments used it. **We
also built the thing that senses how far a new fact is from what we already understand** — that's
the "what should I read next" instinct, and it passed its test.

**Two problems, and they're both about connection rather than correctness.**

First, that test was **three seconds long, on eight made-up examples, using invented words like
"dravithex".** It scored a perfect 1.0 with the mechanism on and exactly 0.0 with it off — which is
what a demonstration looks like, not a measurement. **It proves the idea works. It doesn't show it
works on real text.**

Second, and more striking: **nothing in the system ever calls it.** I checked carefully, including
proving my search could find it if it were there. Every reference to it is inside its own file. It's
a working instrument that has been sitting in a drawer since the 12th.

**Here's why that matters right now.** Tonight I established that our reading system implements a
published rule that tells it **when to put a book down** — and is completely silent on **which book
to pick up next**. That missing half is precisely what this drawer instrument does.

**So the next step is smaller than I told you an hour ago.** I'd ranked "choosing what to read" as
needing invention. It doesn't — **it needs plugging in.** Our own architecture notes already say so,
word for word, and even acknowledge the test data was fake.

One caution: connecting something that scored perfectly on eight invented examples to real text is
exactly where perfect scores collapse. **Expect it to get worse; the useful question is how much**,
measured against the two dumb baselines we already have at proper scale.

## QUESTIONS

None.

## NEXT STEPS

1. **Wire `rank_material()` into the foraging patch-choice** and score it on real text against the
   FROZEN and RANDOM arms that already exist at 10,000 sentences.
2. **Report the degradation honestly** -- a drop from 1.0 is expected and is not a failure.
3. This is independent of the meanings-supply-the-prediction work; both can proceed.
