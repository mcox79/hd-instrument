# **THE BEST-EVIDENCED GROUNDING RESULT IS REAL, ITS NAME MISATTRIBUTES THE CAUSE, AND A BIGGER LEVER THAN EITHER IS SIMPLY MORE DIMENSIONS.**

**Reading the METHOD of the four evidenced grounding cells, as promised. The first one read carries
three corrections that a verdict string cannot show -- and ORGAN_MAP had already written all three.**

---

## 1. ✅ THE CELL IS GENUINELY WELL BUILT -- SAID FIRST, BECAUSE IT IS TRUE

`exp_graded_divisive_comparator_v1`:

- **Pre-registered `d6c56353c` BEFORE the file existed and before any arm was scored.**
- **2AFC, chance exactly `0.50`, nothing hand-scored** -- the discriminator's range is fixed by
  construction, not by a rubric.
- **Item set, leak controls, held-out split and bootstrap IMPORTED from the landed parent cell**, so
  the only difference from the parent is the comparator's arithmetic. **The gold is independent of the
  mechanism under test.**
- **Non-fork controls**: its encoder is byte-identical to `hdlab.context_vector`, its anchor matrix
  byte-identical to `ConceptSpace.anchor_matrix()`, its read-out agrees item-for-item with
  `canonicalize_fast`.
- **MDE stated in advance** (`~0.021` at n=4000) against a `+0.05` band.

**Result: `0.6395 -> 0.6997`, `d = 0.0602`, CI `[0.0440, 0.0762]`, floors scramble `0.5065`/`0.4975`,
frequency `0.4800`, chance `0.50`.** *That is a real, controlled, replicable measurement and I am not
diminishing it.*

## 2. 🔻 **BUT THE CAUSE IS NOT WHAT THE CELL IS NAMED AFTER**

***ORGAN_MAP L1631, already written, decomposing this exact comparison:***

| lever, d=256, near-neighbour 2AFC | effect |
|---|---|
| **CAPACITY** (16x dimensionality, quantised arm) | ✅ **`+0.0985`** |
| **SIGN** (removing the magnitude-destroying `np.sign`) | **`+0.0585`** |
| 🔻 **DIVISIVE NORM** | **`+0.00175`, CI INCLUDES ZERO** |

> # **ESSENTIALLY ALL OF THE `0.0602` IS REMOVING `sign()`. THE DIVISIVE NORMALISATION IN THE CELL'S NAME CONTRIBUTES ABOUT `0.002` AND ITS INTERVAL SPANS ZERO.**

**And that is not a surprise, it is a THEOREM the archive already holds** (ORGAN_MAP L249): *the
canonical pool denominator is a **scalar for the whole representation**, and **cosine is invariant to a
scalar**, so divisive normalisation cannot change a two-candidate argmax -- "not weakly, identically
not at all."* **What was measured null (`+0.0018`, CI `[-0.0030, +0.0065]`) was efficient-coding
adaptation (Laughlin 1981; Fairhall 2001), a different mechanism wearing the same name.**

*ORGAN_MAP also pre-empts a citation error on this very number: `0.0602` is THIS cell; the d-sweep
`0.0585 / 0.0465 / 0.04425` belongs to `exp_capacity_ceiling_near_far_v1`. **Use `0.0585` to keep the
series inside one cell.***

## 3. 🔑 **THE STRATEGIC FACT, AND IT IS THE ONE WORTH CARRYING**

**Our best-evidenced MECHANISM change buys `+0.0585`. Multiplying the dimensionality by 16 buys
`+0.0985`.** *And the graded advantage SHRINKS as d grows -- `0.0585 -> 0.0465 -> 0.04425` across
`256 -> 1024 -> 4096`.*

> ## **SO REMOVING `sign()` IS NOT AN INDEPENDENT WIN. IT IS A WORKAROUND FOR A CODE THAT IS CAPACITY-LIMITED AT d=256, AND IT MATTERS LESS THE MORE CAPACITY YOU GIVE IT.**

**A mechanism change that decays as you relieve the constraint is a symptom, not a cure.** *The
archive's own §3.3 says exactly this -- "the quantised comparator is CAPACITY-limited at d=256" -- and
the number series confirms it.*

## 4. WHAT THIS MEANS FOR "UNDERSTAND ALL THE GROUNDING WORK"

| | |
|---|---|
| ✅ the best-evidenced grounding result is **methodologically sound** | pre-reg, independent gold, four floors, byte-identity controls |
| 🔻 **its headline name misattributes the cause** | the win is `sign()` removal, not divisive normalisation |
| 🔻 **a plain capacity increase beats it** | `+0.0985` vs `+0.0585` |
| ⚠️ **and the mechanism gain decays with capacity** | it is relieving a bottleneck, not adding an ability |

## 5. LIMITS

1. **I read one of four.** *Three evidenced grounding cells remain unread.*
2. **The decomposition is ORGAN_MAP's, not mine** -- I verified the lines exist and read their context;
   I have not re-run the capacity sweep.
3. **All of this is 2AFC near-neighbour discrimination at d=256** -- a matching task. **None of it is a
   comprehension claim**, and the `+0.0985` capacity result is on a quantised arm.

## TLDR

I said I would read the method behind the four grounding results that carry real evidence. Here is the
first, which was also the strongest.

**The experiment itself is well done** — registered in advance, its answer key comes from somewhere
independent of the thing being tested, four separate baselines, and checks confirming its code matches
the live system exactly. The improvement is real: about 6 points, with an error bar that excludes zero.

**But it is named after the wrong cause.** The change bundles two things: throwing away a step that
crushes each number to plus-or-minus one, and a brain-inspired scaling operation. **Our own records
already show the first is worth about 6 points and the second about 0.2 points with an error bar
straddling zero.** There is even a proof on file that the second one *cannot* work for this kind of
comparison — the maths cancels it out exactly.

**And the more useful fact: simply making the vectors 16 times bigger buys more (about 10 points) than
our best mechanism change (about 6).** Worse, the mechanism gain *shrinks* as the vectors get bigger.
**That means removing the crushing step isn't adding an ability — it's compensating for vectors that
are too small.** Relieve the real constraint and the clever fix matters less.

**So the strongest evidenced result in the grounding archive is genuine, misnamed, and beaten by
buying more space.**

## QUESTIONS

None — Q105 still open, independent of this.

## NEXT STEPS

1. **Read the other three evidenced grounding cells** — `reading_grounding_loop_cycle2`,
   `foundation_validation_harness_v1` and `_v4_proximity`.
2. ⚠️ **Anyone citing `exp_graded_divisive_comparator_v1` should cite it as a `sign()`-removal result**,
   not as evidence for divisive normalisation. *The prohibition against re-proposing the latter stands.*
3. *Method note: **the third read paid for itself again.** The verdict string said HARD_PASS with a
   clean CI; the corrections said the cause is a different variable and a bigger lever exists. Neither
   is visible from the metrics file.*
