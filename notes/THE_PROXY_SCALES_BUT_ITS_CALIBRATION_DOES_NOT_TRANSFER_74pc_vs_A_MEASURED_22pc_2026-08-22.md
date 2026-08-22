# **THE VALIDATED PROXY RUNS ON THE WHOLE FOUNDATION -- `50.16%` OF `634` FACTS PASS. TURNING THAT INTO A QUALITY ESTIMATE GIVES `74%` GOOD AGAINST A MEASURED `22%`. THE CALIBRATION DOES NOT TRANSFER.**

**First real use of `hdlab/quality_proxy.py`, and the useful result is the one that stopped me
publishing a number.**

---

## 1. THE MEASUREMENT AT SCALE (READ-ONLY snapshot, nothing written)

*`data/foundation_snapshots/reading_grounding_v2q_full_20260815T182838Z`, loaded through
`foundation_persistence.load_store`:*

| | |
|---|---|
| grounded-meaning facts (`ACTIVE`/`COMBINED`) | **634** |
| distinct cross pairs scored | **634** *(all of them -- no sampling)* |
| **pass the validated proxy** | **318 = `0.5016`**, 95% CI `[0.4628, 0.5404]` |

**This is the job the proxy was validated for: triage at a scale hand-scoring cannot reach.** *634
facts scored in one run against 30,889 tokenised sentences.*

## 2. 🔻 **AND HERE IS WHERE IT GOES WRONG IF YOU ARE NOT CAREFUL**

**The obvious next step is to invert the pass rate into a quality estimate.** *The proxy's measured hit
rates are `0.591` on human-GOOD and `0.244` on human-NOISE, so:*

```
0.5016 = p * 0.591 + (1 - p) * 0.244     ->     p = 0.7424
```

| | |
|---|---|
| **inverted estimate of GOOD fraction** | **`0.7424`** |
| **MEASURED GOOD fraction (blind hand-score)** | 🔻 **`0.2200`** |
| **disagreement** | 🔻 **`3.4x`** |

> # **A NUMBER I COULD HAVE REPORTED AS "74% OF OUR FOUNDATION IS MEANINGFUL" SITS AGAINST A DIRECTLY MEASURED `22%`. THE ONLY THING THAT STOPPED IT WAS CHECKING THE TWO AGAINST EACH OTHER.**

## 3. WHAT THE DISAGREEMENT ACTUALLY MEANS

**Two explanations, both live, neither established:**

1. **The populations genuinely differ.** *The hand-scored rows came from
   `exp_grounding_quality_readout_v1`'s arms (`PBV_BASE` / `PBV_F1F3`, segments like `adv_new`); this
   is the `v2q` snapshot. **Different reads, different material, possibly different quality.***
2. **The proxy's hit rates are population-specific.** *`0.591` / `0.244` were measured on ONE set of
   100 facts. A filter's sensitivity and specificity are properties of the DISTRIBUTION it is applied
   to, not constants of the filter.*

**Both are ordinary. What is not ordinary is assuming neither.** *This is the standing rule -- NO
NUMBER CROSSES POPULATIONS -- and it applies to a calibration exactly as much as to a score.*

## 4. WHAT THIS COSTS AND WHAT IT BUYS

| | |
|---|---|
| ✅ **the proxy scales** | 634 facts, whole population, no sampling, seconds |
| ✅ **the raw pass rate is a real, reportable number** | `0.5016` CI `[0.4628, 0.5404]` **on this snapshot, under this criterion** |
| 🔻 **it may NOT be converted into a meaningful-fraction** | not without hit rates measured ON THIS POPULATION |
| 🎯 **what would fix it** | **a blind hand-score of ~150 facts drawn FROM THIS SNAPSHOT** -- the same eval-bank enlargement now wanted for the fifth distinct reason |

## 5. LIMITS

1. **One snapshot.** *`v2q` only; I have not run `v1_full`, which is the one the `0.2533` correctness
   gap was measured on.*
2. **634 facts is the whole population here, so the CI is sampling-free** -- *but it is one foundation
   at one moment.*
3. **The proxy is a filter with `0.591` recall.** *Even correctly calibrated it discards ~4 in 10 good
   facts, so its pass rate is not a quality measure without inversion, and inversion is what just
   failed.*
4. **I have not verified the two populations are disjoint** -- only that they come from different cells
   and different snapshots.

## TLDR

Yesterday I wired up a fact-quality checker that had been validated against a human's judgement. Today
I ran it over an entire stored foundation — **634 learned facts, all of them, in one go. Half of them
pass.**

**Then I nearly made a bad mistake.** The natural thing is to work backwards from "half pass" to "so
what fraction are actually good?" — and the arithmetic gives **74%**. That would have been a great
headline.

**A human has already scored a batch of these facts by hand, and got 22%.** My clever indirect estimate
is more than three times higher than the direct measurement.

**The reason is mundane and worth remembering:** how often a filter says yes depends on what you feed
it. The hit rates I used were measured on a *different* batch of facts from a *different* run. Reusing
them on new material is the same mistake as quoting a test score from one exam on a different exam.

**So the honest output is narrower than I hoped**: half the facts in this foundation pass a
human-validated filter. That is a real number. **It is not a claim that half the facts are meaningful**,
and I can't make that claim without someone hand-scoring a fresh batch from this specific foundation.

**That's now the fifth separate thing this week that a bigger hand-scored sample would unblock.**

## QUESTIONS

None — Q105 remains open, and this is the fifth argument for the "enlarge the sample" side of it.

## NEXT STEPS

1. 🎯 **Any use of the proxy's pass rate as a QUALITY figure requires hit rates measured on that same
   population.** *Recording it here so the `0.5016` does not travel as "50% meaningful".*
2. **Run the proxy over the `v1_full` snapshot too** -- *cheap, and it says whether `0.5016` is stable
   across foundations or a property of `v2q`.*
3. *Method note: **the check that saved this was comparing an indirect estimate against a direct
   measurement of the same quantity.** I had both on disk and it took one line.*
