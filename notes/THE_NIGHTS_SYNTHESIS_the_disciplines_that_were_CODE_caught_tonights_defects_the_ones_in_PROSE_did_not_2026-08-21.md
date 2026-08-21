# **THE NIGHT'S SYNTHESIS: EVERY DEFECT I FOUND TONIGHT WAS ALREADY GUARDED -- IN CODE -- IN A MODULE THAT WAS NOT ATTACHED TO THE JOB. AND MY "NEW TELL" WAS NOT NEW.**

**Three of 151 `hdlab/` modules encode MEASUREMENT DISCIPLINE as executable assertions. Those
assertions already contain, as runnable code, the two defects I spent tonight discovering by hand.
The disciplines that live in PROSE did not catch them.**

*This is the project's own meta-rule -- "prose cautions get violated, CODE controls catch things" --
now with measured evidence rather than assertion.*

---

## 1. 🚫 FIRST, A CORRECTION TO MY OWN CLAIM FROM TWO TURNS AGO

I wrote: ***"NEW TELL: A SWEEP IS ONLY A TEST IF THE SCORE MOVES ACROSS IT."*** **It is not new.
It is an executable assertion in `hdlab/vsa_cleanup_memory.py`, and it is sharper than my prose:**

```python
def selftest_capacity_is_measurable() -> Dict:
    """The capacity axis must actually FALL with load, or it is not measuring capacity."""
    ...
    if recs[0] < 0.99:
        raise AssertionError("recovery at load 1 is not at ceiling: %.4f" % recs[0])
    if recs[-1] > 0.5:
        raise AssertionError("recovery has not fallen by load 32 (%.4f) -- the axis is saturated "
                             "and cannot measure a capacity" % recs[-1])
```

> **IT ASSERTS BOTH ENDPOINTS. Had D3's queued test been written against this guard, tonight's
> `hit@1 = 1.0000 at every N from 1 to 2000` would have RAISED, immediately, with the correct
> diagnosis already in the error string: *the axis is saturated and cannot measure a capacity.***

## 2. THE SAME STORY, TWICE MORE

| tonight's defect, found by hand | the guard that already existed |
|---|---|
| **D3's sweep does not move** (1.0000 at every N) | **`vsa_cleanup_memory.selftest_capacity_is_measurable`** -- *"the axis is saturated and cannot measure a capacity"* |
| **D3's exact cue is solved without the memory** | **`ca3_completer.selftest_full_cue_is_not_where_the_action_is`** -- *"a full-cue test of a completer measures nothing"*, and it **ASSERTS the ceiling (`>=0.999`) as a GUARD** |
| **my no-write floor was degenerate** (zeroing `W` → zero vector) | **`vsa_cleanup_memory` already reclassifies its own bad control**: `FLOOR_random_overcomplete_codebook_reclassified_from_null = 0.4375`, *"M>d makes a random codebook an overcomplete dictionary... **a floor, not a null**"* |

## 3. 🎯 WHAT THESE THREE MODULES DO THAT THE OTHER 148 DO NOT

**Their self-tests assert METHOD, not just correctness.** Names, verbatim:

| assertion | the discipline it encodes |
|---|---|
| `selftest_capacity_is_measurable` | **an axis that cannot fall cannot measure** |
| `selftest_null_and_known_answer_fail_independently` | **STANDING DISCIPLINE 6** -- *"a FLOOR says whether the EFFECT is real, a KNOWN-ANSWER arm whether the INSTRUMENT is -- run both"* |
| `selftest_not_inert` | **a mechanism that returns its input is not a mechanism** -- *"what five banked cells measured"* |
| `selftest_incumbent_is_argmax_preserving` | ***"MEASURE the incumbent rather than characterise it in prose"*** |
| `selftest_full_cue_is_not_where_the_action_is` | **the saturation trap** |
| `selftest_reuse_is_bit_identical` (x2) | **WIRE-DON'T-ISLAND** -- asserts the module *IS* the incumbent, byte for byte |
| `selftest_extension_does_not_invalidate` | **adding a spoke must not move existing answers** |

## 4. ⚡ **AND ONE OF THEM SHOWS RESTRAINT I HAVE NOT SEEN ELSEWHERE**

`selftest_not_inert` asserts three things and then **deliberately refuses to assert a fourth**:

> *"Whether ITERATION beats a ONE-SHOT argmax is **NOT asserted** -- it is REPORTED by `basin_curve`,
> **because that is the open question the experiment exists to decide and pre-judging it here would
> be exactly the fault the `ca3_completer` amendments record**."*

***A self-test that knows which question is not its to answer.*** *That is the exact failure mode --
a test that bakes in its own conclusion -- stated and avoided at the point of temptation.*

## 5. 📊 THE MEASURED CLAIM

**29 self-test functions across 16 of 151 modules. Of those, 13 in THREE modules
(`vsa_cleanup_memory`, `ca3_completer`, `hub_spoke_word`) assert method rather than correctness.**
**Every defect I found tonight by hand falls inside what those three already guard -- and none of
them was applied to the job that needed it.**

*The other 13 self-test entry points are bare `run_all_selftests` / `_self_test` with no docstring
stating what they refuse to let pass.* **That is the gap, and it is a gap in COVERAGE, not in
knowledge.**

## 6. ➡️ WHAT FOLLOWS

1. **Do not write a new prose rule for the sweep tell.** *It exists as code, it is sharper than my
   sentence, and the prose version has now been independently re-derived at the cost of a night.*
2. **Author D3 and B4 against these guards**, not beside them: `capacity_curve` + `basin_curve` +
   the null/known-answer pair are built, passing, and correctly classified.
3. **The generalisable move is to give the other modules the same treatment** -- a self-test whose
   NAME states what it refuses to let pass. *`selftest_capacity_is_measurable` is 8 lines.*

## TLDR

Tonight I found two flaws by hand, and then found that **both were already caught, automatically, by
checks someone had written into the code — in components nobody had connected to the job.**

One of those checks says, in effect: *"if the difficulty dial doesn't actually change the score, it
isn't measuring anything."* **That is precisely the flaw I spent a turn discovering and then wrote up
as a new lesson. It was not new — and the existing version is better than mine, because it runs.**

The other says: *"testing a repair mechanism by giving it something undamaged tells you nothing."*
Same flaw, already written down, already enforced.

**Three components out of 151 do this** — their tests check not just *does the code work* but *is
this measurement even capable of showing me I'm wrong*. One of them is careful enough to
**deliberately not answer the question its own experiment exists to settle**, and says so, to avoid
baking in the conclusion.

**The lesson is not "write more warnings."** We had the warnings. They were prose in one place and
working code in another, and the working code is what caught things. **The gap isn't knowledge — it's
that only three components have this, and nothing pointed the job at them.**

## QUESTIONS

None.

## NEXT STEPS

1. **Withdraw the "new tell"** -- it is `vsa_cleanup_memory.selftest_capacity_is_measurable` and has
   been for some time.
2. **Both re-scoped tests (D3, B4) should be authored against the existing guards**, which are built
   and passing.
3. **The cheapest durable improvement available: a self-test whose NAME states what it refuses to
   let pass, for modules that lack one.** *Eight lines bought the sharpest check found tonight.*
