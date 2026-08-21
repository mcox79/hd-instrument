# **I TRIED TO MEASURE THE LIVE LOOP'S SUPERPOSITION LOAD FROM THE PERSISTED STORE. THE ESTIMATOR IS INVALID, AND A CONSTRAINT CHECK CAUGHT IT: ITS MAXIMUM EXCEEDS EVERY OCCURRENCE IN THE WHOLE STORE BY 3.5x.**

**One turn ago I wrote that the live loop's frequent words *"would saturate WORSE... but that is a
prediction, not a measurement"*. I went to measure it. THE PREDICTION REMAINS UNMEASURED, and this
records why so nobody repeats the attempt the same way.**

---

## 1. THE ATTEMPT

**`data/foundation/*/concept_space.npz` stores `lemmas` + `sums` (the accumulated
`context_vector_masked`) but NO per-lemma count.** *Entries are integer-valued, consistent with
accumulating ±1 vectors, so the obvious estimator is:*

> **`L_hat = ||sum||^2 / d`** -- *for L INDEPENDENT ±1 traces, `E[||sum||^2] = L*d`, so this returns
> the count.*

| store | lemmas | median `L_hat` | mean | p90 | **max** |
|---|---|---|---|---|---|
| `reading_grounding_v1` | 4,322 | 8.1 | 257.7 | 204.7 | **92,155** |
| `reading_grounding_v2_qualityfix` | 1,415 | 39.4 | 998.3 | 1,683.5 | **94,688** |

*A coherence check passed -- `L_hat >= max|entry|` for 100% / 99.8% of lemmas -- and **that check was
not strong enough to catch the problem**.*

## 2. 🚫 **THE CONSTRAINT CHECK THAT KILLED IT**

**`manifest.json`: `n_occurrences_seen = 26,123` for the ENTIRE v1 store, across all 4,322 lemmas.**

> ### **MAX `L_hat` = 92,155 IS 3.5x THE TOTAL OCCURRENCES OF EVERY WORD IN THE STORE COMBINED.**
> ***A single lemma cannot have more traces than the whole store has occurrences. The estimator is
> not returning a count.***

## 3. WHY IT FAILS, AND WHY THE FAILURE IS FAMILIAR

**`L_hat = ||sum||^2/d` returns L only for INDEPENDENT contributions.** *For perfectly correlated
ones -- the same context vector added L times -- `sum = L*v` and `||sum||^2 = L^2 * d`, so
**`L_hat = L^2`**.* **The estimator conflates COUNT with CORRELATION and cannot separate them.**

**And correlation is exactly what this substrate is already known to have:** *`STATUS` correction
**C11 "58% common mode"**, and **DO-NOT-REDO 27, "rank-1 common-mode removal"** (with a revival
criterion).* **So the large `L_hat` values are consistent with a known strong common component, not
with an enormous trace count.** *That is the reading the evidence supports; I am not claiming a
figure for the common mode here, only that the estimator cannot see past it.*

## 4. 🔻 **WHAT THIS DOES AND DOES NOT CHANGE**

| claim | status |
|---|---|
| the write-gate sweep's stream saturates (median 17 vs capacity ~22, 65.8% of writes past 1/3 recovery) | ✅ **STANDS** -- measured on the actual stream with real per-lemma counts (`lens`) |
| *"the live loop would saturate worse"* | 🚫 **STILL UNMEASURED.** *My attempt was invalid; the prediction is neither confirmed nor refuted* |
| the live store's sums are far larger than a single trace | ✅ true, **but that is a magnitude statement, not a load statement** |

## 5. ✅ WHAT WOULD ACTUALLY MEASURE IT

**A per-lemma trace COUNT, which the store does not persist.** *The live loop knows it at write
time -- `century, 7 traces / 92 occurrences` is exactly this quantity, quoted from a run that
computed it.* **The cheap fix is to persist the count alongside the sum**, which is one integer per
lemma and turns an unanswerable question into a lookup. *That is the same "save the population you
scored" lesson found three times earlier tonight, in its cheapest possible form: one number.*

## TLDR

Last turn I predicted the live system's common words are probably far more overloaded than the
experiment I'd measured — and said plainly that this was a guess. **I went to check it. My method was
wrong, and I caught it before believing the answer.**

The stored memory files keep the accumulated totals but not a count of how many things went into
each. There's a standard trick for recovering the count from the total's size, and it gave numbers up
to about **92,000 entries** for a single word.

**Then a simple sanity check killed it:** the entire store was built from **26,123 word
occurrences**. One word cannot have 92,000 entries when everything put together only has 26,000.
**So the trick isn't measuring what I thought.**

**The reason is worth keeping:** that method only counts correctly when the things being added point
in different directions. When they're all similar, it reports roughly the *square* of the true
count. And we already know this system has a strong shared component across words — it's on our own
correction list.

**So the honest position:** the earlier finding, about the specific experiment, stands — that one had
real per-word counts. **My prediction about the live system remains untested.** Not confirmed, not
refuted.

**And the fix is almost free:** store one extra number per word — how many things went in. The live
system already knows it while writing, and it turns an unanswerable question into a lookup.

## QUESTIONS

None.

## NEXT STEPS

1. **Do not re-attempt this via `||sum||^2/d`.** *It cannot see past the common mode, and a
   coherence check (`L_hat >= max|entry|`) passes anyway -- it is not a sufficient guard.*
2. **Persist a per-lemma trace COUNT alongside the sum.** *One integer; makes the question a lookup.*
3. **The saturation finding for the approved sweep is unaffected** -- that one had real counts.
