# **D3's QUEUED TEST SWEEPS THE WRONG VARIABLE. WITH AN EXACT CUE, RECALL IS 1.0000 FROM N=1 TO N=2000 -- AND IT IS THE PROJECTION DOING IT, NOT THE MEMORY.**

**One turn ago I called D3's can-fail test "the best-posed unrun test on the map" and said the
impossible-test defect was ISOLATED. The design praise stands -- its random-address arm really is
the right idea. THE SWEEP VARIABLE DOES NOT. And "isolated" is now 2 of 10, not 1.**

*Instrument characterisation only. No verdict, nothing touched the live anchor field, patterns are
synthetic. `scratch/d3_capacity_characterisation.py` + `.json` (full 34-point grid, 3 seeds).*

---

## 1. WHAT THE QUEUED TEST ASKS FOR

> *"SMALLEST CAN-FAIL FLOOR TEST: one-shot cued recall of N stored (context → lemma) pairs from the
> live anchor field after a SINGLE exposure, **sweeping N to find the collapse point**."*

**The organ's own 14/14 self-test reports one-shot recall at `sign_agree = 1.000`, which `ORGAN_MAP`
correctly calls *"a 14/14 self-test with no comparator."*** *So the question an author needs answered
before writing the cell is simply: **where is the collapse point?***

## 2. 🔴 **THERE ISN'T ONE. NOT IN N.**

| N | 1 | 10 | 100 | 500 | 1000 | **2000** |
|---|---|---|---|---|---|---|
| **hit@1, exact cue** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | **1.0000** |

**`sd = 0.0000` across 3 seeds, at BOTH sparsities (ours 0.02 and the pinned MTL 0.002).**
***2,000 patterns stored in a 2,048-dimensional associator at perfect recall is not a capacity
result -- it is a tell.***

## 3. ⚡ **THE CONTROL THAT EXPLAINS IT: `use_ca3=False`**

| N | CA3 **ON** | CA3 **OFF** | delta |
|---|---|---|---|
| 10 | 1.0000 | 1.0000 | **+0.0000** |
| 100 | 1.0000 | 1.0000 | **+0.0000** |
| 500 | 1.0000 | 1.0000 | **+0.0000** |
| 2000 | 1.0000 | 1.0000 | **+0.0000** |

**Switching the memory OFF changes nothing.** *An exact cue deterministically regenerates its own DG
code, so nearest-neighbour lookup recovers the item **with no storage involved at all**. The task is
solved by an injective encoding.*

## 4. ⚠️ **AND A FLOOR THAT LOOKS RIGHT AND IS DEGENERATE**

**My first attempt used a "no-write" floor that zeroed `W`. It tracked chance beautifully and it is
WORTHLESS:** `settle()` computes `sign(W @ cue)`, so `W = 0` returns the **zero vector** and the arm
collapses for a reason that has nothing to do with memory. ***A floor that fails for a degenerate
reason is not a floor.*** **`use_ca3=False` is the informative control -- it removes the MECHANISM
while leaving the PIPELINE intact.**

## 5. ✅ **THE KNOB THAT DOES WORK: DEGRADE THE CUE, NOT THE LOAD**

| N | flip 0.00 | flip 0.10 | **flip 0.25** | **flip 0.40** |
|---|---|---|---|---|
| 100 | 1.0000 | 1.0000 | **0.8833** | **0.1267** |
| 500 | 1.0000 | 1.0000 | **0.7707** | **0.0513** |
| 2000 | 1.0000 | 0.9995 | **0.6867** | **0.0317** |

**The collapse sits between 25% and 40% cue corruption, and it barely moves with N.** *That is where
a sweep belongs.* **AND IT MATCHES THE BRAIN-SIDE METRIC `ORGAN_MAP` ALREADY RECORDS FOR THIS ORGAN:**
*"one-trial retrieval of the full pattern **from a partial cue**."* ***The map states the right metric
in its METRIC line and then queues a test that does not use it.***

## 6. 🚨 **THE CONSEQUENCE FOR THE DECISIVE ARM -- THIS IS THE EXPENSIVE PART**

D3's design is praised precisely for arm (ii): *"the same write op to a **randomly chosen sparse
address** instead of the DG-derived one, so the test isolates the ALLOCATOR... **the arm that would
be omitted by someone testing the write op**."*

> **BUT IF CA3 CONTRIBUTES NOTHING, ARM (ii) READS 1.0000 TOO -- because changing where you write
> cannot matter when retrieval never consults what was written.** ***An author would get "no
> difference between the DG address and a random address" and read it as "the allocator does not
> matter", when it actually means "the test never reached the allocator".*** **A false null on the
> one arm the whole design exists to protect.**

## 7. 📉 AND CA3 IS NEVER BETTER, EVEN WHERE THE TASK IS HARD

**Across all 34 grid points: `ca3_ever_better_than_off = False`. Delta range `-0.0480 .. +0.0000`.**
*At flip 0.25 the task is genuinely non-trivial (CA3-off is 0.71-0.89, not a ceiling) and CA3 STILL
does not improve on skipping it -- it is slightly WORSE.*

**Same SHAPE as D2's independent finding** (*"the settling step buys between −0.020 and +0.005 over
argmax and never widens the basin"*, `IS-GOOD no — indistinguishable from argmax`) **and consistent
with DO-NOT-REDO 45.** ⚠️ *Different organ, different instrument, different task -- so this is
CORROBORATION IN SHAPE, not a shared number. Do not merge the figures.*

## 7b. ⚡ **THE PRIOR-WORK CHECK PAID OUT: THIS WAS ALREADY KNOWN, IN CODE, AND ASSERTED AS A GUARD**

**`hdlab/ca3_completer.py` carries a self-test named `selftest_full_cue_is_not_where_the_action_is`.**
Its docstring, verbatim:

> *"At a FULL cue both arms are at ceiling -- **the saturation trap, made explicit**. This is why **a
> full-cue test of a completer measures nothing**, and it is asserted here **so the scope of the
> three earlier floored cells cannot be quietly forgotten**."*

***It ASSERTS the ceiling (`plain >= 0.999 and done >= 0.999`) -- the trap is encoded as a GUARD.***

**And its `routed_completion_discriminates` curve already IS the sweep D3 needs:**

| cue kept | 1.00 | 0.80 | **0.60** | **0.50** | 0.35 | 0.20 |
|---|---|---|---|---|---|---|
| top1 **uncompleted** | 1.0 | 1.0 | **0.9766** | 0.5000 | 0.0 | 0.0 |
| top1 **completed** | 1.0 | 1.0 | **0.8984** | 0.4922 | 0.0 | 0.0 |

**Completion NEVER helps at any cue level** (identical in shape to my `CA3 ON − CA3 OFF` ≤ 0), and
the **informative band is ~0.80 → 0.35 kept**, which **brackets consistently with the 25-40%
corruption collapse I measured on `hippocampal_encoder`.**

**➡️ THIS MATERIALLY WEAKENS MY OWN SCOPE CAVEAT IN §8.** *I flagged that my patterns were synthetic
and near-orthogonal. `ca3_completer` uses a **multi-spoke bound store with a shared mask and donor
across spokes** -- its own note calls that *"harder than the experiment's"* -- **different code,
different structure, same shape.** Two independent implementations agree.*

*It also classifies its own controls correctly, which is the §4 lesson already solved:*
`FLOOR_random_overcomplete_codebook_reclassified_from_null = 0.4375`, *"M>d makes a random codebook
an overcomplete dictionary; snapping to it reconstructs the cue. **A floor, not a null.**"*

> **➡️ REUSE, DO NOT REBUILD (error-flavour route 4). Whoever authors D3 should reuse this harness --
> cue-fraction sweep, oracle, null, and a correctly-classified floor, already built and passing --
> rather than author a parallel one.** ⚠️ *`ca3_completer` is the D2/cleanup family, NOT D3, so this
> is CROSS-ORGAN corroboration and not the same measurement twice.*

## 8. 🔻 SCOPE LIMITS, STATED BECAUSE THEY BOUND EVERY NUMBER ABOVE

1. **Patterns are i.i.d. random bipolar -- near-orthogonal. Real `(context → lemma)` pairs are
   CORRELATED, and DG pattern separation exists precisely to decorrelate them.** *The real task is
   harder and these numbers do not transfer to it.* **What DOES transfer is structural: an exact cue
   regenerates its own DG code whatever the inputs are.**
2. `d = 256 → 2048`, sparsity 0.02 / 0.002, 3 seeds. **No claim outside that box.**
3. **This does NOT say the organ is worthless.** It says *this task, with an exact cue, cannot see
   it.* **EXISTS yes / IS-GOOD still genuinely unknown -- which is what the map said.**

## 9. 🚫 CORRECTING MYSELF FROM ONE TURN AGO

I wrote: *"1 of 10 was impossible. The other 9 are sound."* **That should now read 2 of 10 needing a
specification fix**, and the second is a different failure mode: **not an empty stratum, but a sweep
over a variable that does not move the score.** *My audit asked "does the population its can-fail
condition needs exist?" -- for D3 it does. **I never asked whether the score could MOVE across the
swept range**, which is the question that catches this one.*

> **ADD TO THE TELL LIST: A SWEEP IS ONLY A TEST IF THE SCORE MOVES ACROSS IT. CHECK THE ENDPOINTS
> BEFORE AUTHORING THE GRID -- ONE RUN AT N=1 AND ONE AT N=MAX WOULD HAVE SHOWN 1.0000 = 1.0000.**

## TLDR

One turn ago I called the memory component's queued test the best-designed unrun test we have. **Its
design is still good — but it measures the wrong thing, and I found out by trying to prepare it.**

The test wants to store more and more items until recall breaks. **It never breaks.** Storing 1 item
and storing 2,000 both give a perfect score, with zero variation across three runs.

**The reason: with a perfect reminder, the system doesn't need memory at all.** Handing it the exact
original converts it back into its own internal fingerprint, and matching fingerprints is enough.
**Switching the memory off entirely changes nothing.**

**What does break it is a damaged reminder.** Corrupt a quarter of it and the score drops to about
0.7–0.9; corrupt 40% and it falls to near nothing. That's where the test belongs — **and our own
reference document already says so in a different line, describing the brain's version as recall
"from a partial cue". The right metric was written down and then not used.**

**The costly part:** that test's cleverest feature is a check on whether *where* things get stored
matters. **But if the memory is never consulted, that check returns "no difference" — and someone
would read it as "where you store things doesn't matter", when it really means "the test never
looked".** A false all-clear on the one thing the design exists to protect.

**Two honest limits.** The items I used are artificially unlike each other; real ones overlap more,
so the real task is harder. And this doesn't show the component is useless — it shows **this test
can't see it.**

## QUESTIONS

None.

## NEXT STEPS

1. **The D3 cell is still worth authoring — with the cue-corruption level as the swept variable, not
   the number of items**, and collapse bracketed between 25% and 40% corruption.
2. **Arm (ii) is only meaningful once the mechanism is doing work** — verify a non-zero
   `CA3 ON − CA3 OFF` gap exists at the chosen operating point *before* trusting any allocator
   comparison.
3. **New tell for queued tests: a sweep is only a test if the score MOVES across it.** Two endpoint
   runs cost seconds and settle it.
