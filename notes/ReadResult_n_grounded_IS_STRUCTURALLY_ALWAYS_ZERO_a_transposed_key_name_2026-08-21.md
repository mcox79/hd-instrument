# `ReadResult.n_grounded` IS **STRUCTURALLY ALWAYS ZERO** -- A TRANSPOSED KEY NAME, FAILING SILENTLY

**Found by chasing why my own diagnostic reported `n_grounded 0` on a read that processed 1,060
sentences while the anchor set grew by 68.** *A field that says "nothing was learned" while the
vocabulary demonstrably grew is not a null; it is an instrument that is not connected.*

---

## 1. THE BUG, IN TWO LINES

**`hdlab/substrate.py:608` READS:**
```python
res.n_grounded = int(row.get("n_grounded_cumulative", res.n_grounded) or 0)
```

**`checkpoint()` in `hdlab/reading_grounding_loop.py` EMITS:**
```
cumulative_grounded          <-- the words are TRANSPOSED
```

**Measured directly on a live read:** `has n_grounded_cumulative? **False**`.
**And `n_grounded_cumulative` appears EXACTLY ONCE in the entire `hdlab/` tree -- at the line that
reads it.** *Nothing anywhere writes it.*

**➡️ `row.get(...)` ALWAYS TAKES THE DEFAULT (`res.n_grounded`, i.e. `0`), AND `or 0` GUARANTEES THE
RESULT IS `0`. THE FIELD CAN NEVER BE NON-ZERO ON ANY READ.**

## 2. WHY IT FAILS SILENTLY -- AND IT IS THE `or 0` THAT DOES IT

**`.get(key, default)` cannot raise.** *A missing key is indistinguishable from a present zero.* And
`or 0` then converts any `None` into a clean-looking integer. **There is no exception, no warning, and
no way to tell the difference from the outside.**

**`ReadResult`'s own docstring states the contract this violates:**
> *"What one `read()` call did. **Every field is a COUNT OF SOMETHING THAT HAPPENED**, not a score."*

**`n_grounded` counts nothing that happened. It reports a constant.**

## 3. ✅ **BLAST RADIUS: SMALL, MEASURED, AND NO PUBLISHED NUMBER IS AFFECTED**

| | |
|---|---|
| writers of `ReadResult.n_grounded` | **1** -- `substrate.py:608`, the bug itself |
| readers | **1** -- `tools/diagnose_read_with_loaded_foundation.py:78`, **which I wrote tonight** |
| landed cells affected | **none found** -- `exp_information_foraging_reading_v1` and the others compute their own counts from the checkpoint rows directly |

**➡️ THE ONLY VICTIM WAS MY OWN DIAGNOSTIC**, whose "double null" I then spent real time explaining as
a corpus-exhaustion artifact. *Corpus exhaustion was real and separate; **this** is why the number
stayed zero even after that was fixed.*

## 4. THE FIX, AND THE CONTROL IT REQUIRES

**The fix is one identifier:** `"n_grounded_cumulative"` -> `"cumulative_grounded"`.

**⚠️ BUT IT MUST NOT BE APPLIED ON THE STRENGTH OF THE NAME ALONE.** *On a 60-sentence read
`cumulative_grounded` is ALSO `0` -- correctly, because nothing was grounded. **Renaming the key and
still seeing zero would look exactly like success.*** **A longer read that grounds something is
required first, to prove the corrected key carries a non-zero.** *That control is running; the fix is
NOT applied until it returns.*

*This is the same discipline that this repo already demands of guards: **verify with a positive
control, never only an absence check.** Here the absence check would pass trivially.*

## TLDR

I chased down why one of my own measurements kept saying "nothing was learned" while the system's
vocabulary was visibly growing.

**The answer is a spelling mistake.** One part of the code writes a number under the label
`cumulative_grounded`. Another part looks for it under `n_grounded_cumulative` — **the same two words,
swapped.** So it never finds it, quietly substitutes zero, and reports that as the answer.

**It fails invisibly by design of the lookup:** asking a dictionary for a missing key with a default
can't produce an error, and the extra `or 0` tidies away any remaining trace. **From the outside, "not
connected" and "genuinely nothing" look identical.**

**Good news on scope:** only two places in the entire codebase touch this field — the line with the
bug, and **the diagnostic I wrote tonight.** No published result depends on it; the real experiments
read the underlying numbers directly. So this cost me time, not correctness.

**And I'm not fixing it yet.** On a short run the correct number is *also* zero — legitimately, because
nothing was learned. **So if I renamed the key now and still saw zero, it would look like the fix
worked.** A longer run is going first, to prove the corrected label actually carries a real number.

## QUESTIONS

None.

## NEXT STEPS

1. **Await the positive control**, then apply the one-identifier fix.
2. **The `or 0` deserves to go too** -- it converts a wiring failure into a plausible measurement.
3. Worth a broader look: **how many other `.get(key, default)` reads in this repo are looking for keys
   nothing writes?** *That is greppable and this one cost an evening.*
