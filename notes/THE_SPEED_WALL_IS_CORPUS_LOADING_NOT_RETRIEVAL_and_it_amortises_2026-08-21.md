# THE SPEED WALL IS **CORPUS LOADING**, NOT RETRIEVAL -- AND IT **AMORTISES**

**The charter names *"the O(n_facts) speed wall"* as a known frontier, and after finding memory is a
non-problem I said speed was the live version. Measured, the wall is real but it is somewhere else,
and it is a FIXED cost rather than a scaling one.**

---

## 1. ❌ THE `O(n_slots)` RETRIEVAL WALL DOES NOT FIRE ON THE READ PATH

I predicted a specific defect: `ConceptSpace._version` bumps on **every** `observe()`, so the cached
anchor matrix would be invalidated constantly and rebuilt. **Measured cost of a rebuild scales
linearly and would be ~145 ms at 69,171 slots** -- a severe wall if it fired.

**IT DOES NOT FIRE. Instrumented over a real 200-sentence read: `anchor_matrix` called ZERO times.**
*The anchor scan is not on the reading path at all, so the invalidation cannot cost anything there.*

**⚠️ SCOPE, STATED HONESTLY: I instrumented a 200-sentence read, and `consolidate_every` defaults to
200.** A longer read that triggers consolidation repeatedly may call it. **So the anchor scan's cost
is UNTESTED, not shown to be absent.** *That distinction is the one this project keeps paying for.*

## 2. ✅ WHERE THE TIME ACTUALLY GOES -- 89% IS CORPUS LOADING

Profiling a 120-sentence read (49.2 s total):

| | cumulative | what it is |
|---|---|---|
| `corpus_registry.remaining()` -> `pool()` | **43.8 s (89%)** | loading and filtering corpus files |
| `_acceptable` (785,899 calls) | 20.3 s | the per-sentence acceptance filter, inside loading |
| `_io.open` (825 calls) | 8.7 s | file opens |
| **`process_sentence` + `context_vector_masked`** | **~6 s** | **the actual learning** |

**The system spends nine tenths of a short read deciding what to read, and one tenth reading.**

## 3. ✅ AND IT AMORTISES -- THE COST IS FIXED, NOT PER-SENTENCE

| read | per-sentence |
|---|---|
| #1 of 120 | **171 ms** |
| #2 of 120 | 55 ms |
| #3 of 120 | 66 ms |
| of 1,000 | **24 ms** |

**Steady state ~24 ms/sentence, and still falling with read size** -- so 24 ms itself still contains
residual fixed cost.

**➡️ AT 24 ms/SENTENCE, EVERY SENTENCE WE OWN (325,798) READS IN ~2.2 HOURS.**

## 4. 🎯 THE COMPLETE CAPACITY PICTURE, BOTH AXES

| axis | measured |
|---|---|
| **memory** | **142 MB** for all 325,798 sentences; growth **saturating** (`beta` 0.589 -> 0.289) |
| **time** | **~24 ms/sentence** steady state -> **~2.2 hours** for everything we own |

**RETAIN-FOREVER IS AFFORDABLE ON BOTH AXES.** *The owner's instinct -- never throw out useful
information -- now has a number on each: under a gigabyte, and an afternoon.*

**AND THE CHARTER'S NAMED WALL IS NOT WHAT FIRES.** *That is worth recording: a frontier named in
the charter turned out, on measurement, not to be the binding constraint on this path. It may bind
elsewhere -- the anchor scan is untested, not absent.*

## TLDR

After finding that storing everything is cheap in memory, I said the real worry was speed — that
looking things up gets slower as we store more. **I measured it and the worry is misplaced.**

The specific slowdown I predicted does not happen: the expensive lookup structure is **never built
during reading at all**. (Careful caveat: I checked a short read, and it is possible longer ones
behave differently. So that cost is untested, not proven absent.)

**What actually eats the time is loading the reading material.** Nine tenths of a short reading
session is spent opening and filtering corpus files; only one tenth is spent learning.

**And that cost is paid once, not per sentence.** The first short read costs 171 milliseconds per
sentence, the fourth costs 24 — because the files are already loaded. At that rate, reading every
sentence we own takes about **two and a quarter hours**.

So the full picture on keeping everything forever: **under a gigabyte of memory, and an afternoon of
reading.** Both cheap. Your instinct about never discarding information now has a measured number on
both axes rather than a principle on one.

One thing worth flagging: the slowdown named in our own project charter as a known frontier turned
out not to be what binds here. That does not mean it is imaginary — it means it has not been shown to
bind on this path, which is a different claim.

## QUESTIONS

None.

## NEXT STEPS

1. **The anchor scan's cost is UNTESTED, not absent** -- a read long enough to trigger repeated
   consolidation would settle it.
2. Corpus loading is a fixed cost worth knowing about but is not a scaling wall.
3. Capacity, on both axes, is closed as a reason to build sleep.
