# **Q96 ANSWERED WITHOUT AUTHORING ANYTHING: THE "WRITE LESS" AXIS TERMINATES IN AN ARM THAT WROTE NOTHING AND READS EXACTLY 0.5000 WITH A ZERO-WIDTH CI. THE ENDPOINT WAS ALREADY IN THE CELL.**

**I filed Q96 asking the owner to authorise extending the write-rate sweep past its edge. My own
recommendation attached the risk: *"the curve may keep rising simply because writing less means
fewer chances to be wrong, in which case the peak is trivially 'write almost nothing' and the
finding evaporates -- so the extended sweep must also report how MUCH is being kept at each point."*
**THAT NUMBER WAS ALREADY RECORDED. I did not open the file before filing.**

---

## 1. THE TABLE THE CELL ALREADY HELD

`data/exp_predictive_coding_write_gate_dissociation_v1/metrics.json`,
`COMPOSITION_PER_ARM` joined to `AUC_PER_ARM`:

| arm | acceptance | tokens written | AUC | CI half-width |
|---|---|---|---|---|
| `A0_INCUMBENT` (write everything) | 1.0000 | 33,907 | 0.0710 | 0.0211 |
| `P1 @0.4039` | 0.7485 | 25,380 | 0.0961 | 0.0254 |
| `P1 @0.4497` | 0.5139 | 17,426 | 0.1526 | 0.0334 |
| `P1 @0.4862` | 0.3067 | 10,400 | 0.2268 | 0.0407 |
| `P1 @0.5151` **(the edge)** | 0.1581 | 5,362 | **0.3079** | 0.0464 |
| 🚫 **`N2_ANTI_GATE` (any threshold)** | **0.0000** | **0** | **0.5000** | **0.0000** |

## 2. 🚫 **THE ENDPOINT IS DEGENERATE, AND IT IS THE REFERENCE VALUE**

**`N2_ANTI_GATE` writes NOTHING and scores EXACTLY `0.5000`, with `ci95 = [0.5, 0.5]` and
`ci_halfwidth = 0.0`.** *A bootstrap that returns ZERO width means every resample produced
identically 0.5 -- **the signature of an all-ties arm.** With no tokens written the store is empty,
every pair scores identically, and a tie is scored as a draw.* **The cell labels it
`NOT_SEPARATED_FROM_CHANCE`, correctly.**

> **SO THE AXIS RUNS FROM 0.0710 (write everything) TO A DEGENERATE 0.5000 (write nothing) -- AND
> 0.5 IS THE VERY REFERENCE VALUE EVERY ARM IS BEING COMPARED AGAINST.** ***Extending the sweep
> pushes acceptance toward zero, i.e. toward an arm whose score is high FOR NO REASON AT ALL.***

**This is the same defect class as tonight's other two, for the third time:** *the zeroed-`W` floor
that collapsed because `sign(0 @ cue)` is the zero vector; B1's empty OUT stratum; and now an
endpoint that scores well by containing no information.* **`hdlab/vsa_cleanup_memory.py::
selftest_capacity_is_measurable` is the guard that asserts BOTH endpoints of a sweep for exactly
this reason.**

## 3. ⚠️ TWO MORE WARNINGS IN THE SAME TABLE

**(a) THE HIGHER SCORES ARE THE LESS CERTAIN ONES.** CI half-width grows monotonically as acceptance
falls: **0.0211 → 0.0254 → 0.0334 → 0.0407 → 0.0464 -- it MORE THAN DOUBLES.** *Fewer tokens, wider
error. STANDING DISCIPLINE 14: a width is not an effect.*

**(b) THE RATE-MATCHED RANDOM GATE MATCHES AT EVERY SINGLE THRESHOLD** -- and now visibly across the
whole sweep, not just at one point:

| threshold | prediction-gated | **random, rate-matched** | delta |
|---|---|---|---|
| 0.4039 | 0.0961 | **0.0971** | **−0.0010** |
| 0.4497 | 0.1526 | **0.1368** | +0.0158 |
| 0.4862 | 0.2268 | **0.2165** | +0.0103 |
| 0.5151 | 0.3079 | **0.3007** | +0.0072 |

**Every delta is far inside the CI half-widths (0.03-0.05).** *Already recorded as `NOT_SEPARATED`;
what is new is that it holds at all four points, so "prediction-error gating" contributes nothing
anywhere on the axis. **The gain is RATE.***

## 4. ✅ WHAT WOULD ACTUALLY SETTLE IT

**Not a longer sweep. A TIE-MASS measurement.** *Report, at each threshold, what fraction of the
242 P-pairs and 242 S-pairs are exact ties.* **If tie mass rises with the score, the curve is
interpolating toward the degenerate arm and there is no optimum to find.** *This is cheap, it is a
re-scoring rather than a new experiment, and `tools/orthographic_floor_tie_mass_v1.py` already
exists for the tie-convention problem in another arm.*

⚠️ **WHAT I AM NOT CLAIMING: that the gain IS the degenerate effect.** *The intermediate arms write
5,362-25,380 real tokens and their CIs exclude 0.5 comfortably. At the edge, 0.3079 is still far
from 0.5. **The curve may well be genuine up to some point** -- what is established is that its
DESTINATION is meaningless, so "keep going until it stops improving" cannot find an optimum.*

## TLDR

Last night I asked you to approve extending an experiment, because the system scores better the less
it writes down and the best setting tried was the edge of the range and still improving.

**I've now found the answer in results we already had, and it's: don't extend it. I should have
opened that file before asking.**

The experiment already contains a version that writes down **nothing at all**. It scores **0.50** —
which is exactly the reference number everything is compared against. But it gets there by having no
information whatsoever: with nothing written, every comparison is a dead heat, and a dead heat counts
as a draw. **Its error bar is literally zero-width, which is the fingerprint of that.**

**So the direction the curve is climbing toward isn't a good score — it's an empty one.** Asking
"where does it stop improving?" has no answer, because it improves all the way to writing nothing.

**Two more warnings sit in the same table.** The less it writes, the less certain the result — the
error bar more than doubles across the range. And throwing away the same amount **at random** scores
the same at every single setting: 0.097 against 0.096, 0.137 against 0.153, 0.217 against 0.227,
0.301 against 0.308. **So the gain is about quantity, not about being clever — now confirmed at all
four points rather than one.**

**What I'm not saying:** that the improvement is fake. The middle settings write thousands of real
items and score genuinely below the empty version. **The curve may be real up to a point — but its
destination is meaningless, so "keep going until it stops" can't locate that point.**

## QUESTIONS

**Q96 is withdrawn and replaced** -- see the board. The replacement asks for a cheap tie-count check
instead of a longer sweep.

## NEXT STEPS

1. **Do not extend the sweep.** The endpoint is measured and degenerate.
2. **Measure TIE MASS per threshold** -- a re-scoring, not a new experiment.
3. **Third instance tonight of "a control that scores well by containing nothing".** *The guard for
   it already exists in `vsa_cleanup_memory`; it is not applied to this cell.*
