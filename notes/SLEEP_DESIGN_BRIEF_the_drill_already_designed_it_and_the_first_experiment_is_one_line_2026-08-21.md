# SLEEP (D8+D4) DESIGN BRIEF -- **THE DRILL ALREADY DESIGNED THE EXPERIMENT. THE FIRST ONE IS ONE LINE.**

**My job here was to write the evaluation design. Most of it was already written**, in
`drill_cascade_synapse_replay_consolidation_biology_2026-08-14.md` section 4, and re-deriving it
would have been the waste this project keeps paying for. **This brief adds three things the drill
does not have** and otherwise points at it.

---

## 1. ✅ WHAT THE DRILL ALREADY SETTLED -- DO NOT RE-DERIVE

**The measurand is the LOG-LOG RETENTION SLOPE, not a task score.** Learn set A, stream `t` new
items, retest A, plot on log-log axes. The models predict **different curve FAMILIES**, not "better":

| system | shape on LOG-LOG |
|---|---|
| naive / sign-quantised | **curved, no straight segment** (straight on SEMI-log) |
| cascade, depth `n` | **straight, slope `-alpha`**, `alpha ~ 3/4..1` |
| Benna-Fusi, `m` vars | **straight, slope `-1/2`**, knee at `T = 2^(2m+1)` |

### 🎯 **AND PREDICTION 1 IS THE BEST CAN-FAIL CONDITION I HAVE SEEN IN THIS PROJECT**

> **THE SIGN FLIPS. The cascade arm must start BELOW the naive arm, by exactly `1/n`
> (`1/sqrt(m)` for Benna-Fusi). *An arm that is better everywhere has not implemented a cascade.*
> The theory predicts OUR OWN TREATMENT ARM IS WORSE AT `t=0` BY A COMPUTABLE FACTOR.**

*A theory that predicts your arm loses at t=0 cannot be satisfied by an arm that merely looks good.
Every artifact this project has caught -- the empty accumulator scoring rank 1.0, the 10-sparse
noise beating a real arm -- would FAIL this test, because artifacts are better everywhere.*

Plus: a **crossover `t*` predicted before running**; the **slope fitted with a CI** as the
measurand; and **the knee moving 4x with `m` but NOT with `N`** -- two orthogonal manipulations no
level-effect confound reproduces. **Replay (D4) moves the LEVEL; cascade (D8) moves the SLOPE.**

## 2. 🔬 THE FIRST EXPERIMENT IS ONE LINE, AND I VERIFIED IT ON DISK

**The drill's analysis (flagged as its own, not literature):** Benna-Fusi's whole achievement is
reaching `t^-1/2` with **BOUNDED** variables -- an **unbounded** perfect integrator already gives
`SNR = sqrt(N/t)`, the same exponent, for free. And `ConceptSpace.observe` does
`self._sums[lemma] += ctx_vec` -- **exactly that unbounded integrator.** Then `np.sign()` is applied
one line before use, converting a bounded-variance `t^-1/2` system into a saturating 1-bit one.

**➡️ SO THE HYPOTHESIS IS: OUR FORGETTING EXPONENT IS NOT ABSENT, IT IS DESTROYED BY THE `sign()`.**

**DISK-VERIFIED TODAY, and the situation has half-changed since the drill was written:**

| path | state |
|---|---|
| anchors (`bundle`, `anchor_matrix`) | **graded** -- `GRADED_COMPARATOR` defaults ON since 2026-08-14 |
| **the QUERY** (`reading_grounding_loop.py:776`) | **`new_bundle = np.sign(new_raw_sum)` -- UNCONDITIONAL, not gated by the flag** |

**Half the quantiser was removed and the query half is still there.** *The drill described a
default-OFF graded path; that is now stale, and the live version of its hypothesis is narrower and
sharper: only the query side still quantises.*

**THE EXPERIMENT: measure the log-log retention slope with the query graded vs `sign()`-quantised.**
One line, no new organ, and it tests a **pinned** prediction.

## 3. ⚠️ WHAT THE DRILL DOES NOT HAVE, AND F5 TAUGHT ME TO ADD

### **THE CONFOUND THAT WOULD RUIN IT: A SYSTEM THAT LEARNS LESS FORGETS LESS.**
Retention is trivially maximised by not learning. A frozen accumulator has **perfect** retention and
**zero** acquisition -- and this project has already been fooled by the same shape twice (an all-zero
accumulator scored median rank 1.0; a 10-sparse random arm beat a real one).

**MANDATORY: both arms must reach criterion on set A BEFORE the retention stream starts, and
acquisition must be REPORTED beside retention.** *A retention curve from an arm that never learned
set A is not a slower forgetting curve -- it is a flat line, and flat lines fit any slope you like.*
**Add a FROZEN arm explicitly as a floor**: it must show perfect retention and fail acquisition, so
the metric is demonstrated to be capable of exposing the cheat.

### **THE TIME AXIS IS NOT THE SAME AXIS.**
The drill flags this against itself and it must survive into the build: **their `t` is "memories
stored at this synapse"; ours is "new concepts ingested".** Those coincide only if each ingested
concept writes to the measured slot. **State the mapping explicitly, or the fitted slope is a
number about a different quantity.**

### **A CHEAP PROBE MAY MEASURE, IT MAY NEVER SET DIRECTION.**
The one-line experiment is unusually cheap for this project. **That is a reason to run it, not a
reason to let it choose what gets built.** If it passes, the drill's own reading is that the cascade
buys protection against *weight-range growth*, not against forgetting -- **a different and much more
precise justification for building it**, which is a better outcome than a vague win.

## 4. CARRIED CORRECTIONS (do not re-introduce)

**D8:** *"Roxin & Fusi 2012"* is **2013**, and it **shares the cascade's scaling, never supported
`~N`**. **D4:** reward-scaling is **Ambrose, Pfeiffer & Foster 2016**, not Foster & Wilson 2006 --
that paper **found reverse replay and never reward modulation**. **The drill also records that
`ORGAN_MAP`'s SNR equation is WRONG IN THE EXPONENT OF `N`** (its section 2.4) and owes ORGAN_MAP a
list of corrections (section 5) that has not been applied.

**UNPINNED, and must be labelled as ours if used:** how many times an experience is replayed (3.1),
the interleaving ratio as a number (3.5), and **the selection function -- which traces get replayed
(3.8, "confirmed unpinned")**. *That last one is exactly where an invention would be easiest to
disguise as biology.*

## TLDR

I set out to design how we would test a sleep-like memory system, and found most of the design
already written in a careful literature note from a week ago. Re-doing it would have been the waste
this project keeps paying for.

**The test is unusual and good: you measure the SHAPE of forgetting, not how much is remembered.**
Plot memory against time on a log scale and the three candidate mechanisms produce visibly different
curves — one bends, two are straight lines with different slopes. You are fitting a slope, not
comparing scores.

**And the best part is that the theory predicts our new version will be WORSE to begin with**, by a
precise, calculable amount. Anything that looks better everywhere has not implemented the mechanism.
Every fake result this project has caught would fail that test, because fakes are better everywhere.

**Then the genuinely surprising bit.** The note points out that our existing code already does the
mathematically hard part — it accumulates evidence without throwing any away — and then destroys it
one line later by crushing everything to plus-or-minus one. I checked the code today: **half of that
crushing was already removed last week, and the other half is still there, on the query side.** So
the first experiment is a one-line change measuring the shape of forgetting with and without it.

I added three things the original note lacks: the way this test could fool us (**a system that learns
nothing forgets nothing** — so both arms must be shown to have actually learned first), a warning
that "time" means something different in their equations than in ours, and a reminder that a cheap
experiment may measure but must never choose direction.

## QUESTIONS

None.

## NEXT STEPS

1. **The one-line graded-query retention-slope measurement**, with acquisition reported beside
   retention and a frozen arm as the cheat-detector floor.
2. The drill owes `ORGAN_MAP` a correction list (its section 5) that has not been applied.
3. The cascade build itself remains a real build and is not started.
