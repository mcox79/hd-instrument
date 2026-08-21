# **THE MOST LOAD-BEARING STANDING CLAIM SURVIVES THE ONE METHOD THAT WORKED TONIGHT -- AND RECONCILES EXACTLY.**

**Tonight's method review concluded that of five written rules, only ONE paid out: *put a number
beside another number that constrains it*. It killed four of my own claims. So I turned it on the
claim in `STATUS.md`'s `## POSITION` block, which I had never checked. IT PASSES, and precisely.**

*A method that only ever destroys is not a method. This is the check that could have failed.*

---

## 1. THE CLAIM

> **`SUBSTRATE - COUNTING = -0.142 per item over 478 items, 95% CI [-0.203, -0.082]`, SEPARATED**
> -- reported as a PAIRED test, beside marginals of **+16.3 pp** (substrate) and **+29.4 pp**
> (counting).

**These are two different computations. A paired per-item test over 478 items and four per-set
marginal medians need not agree -- which is exactly what makes it a constraint.**

## 2. THE CHECK

| arm | per-set values | median |
|---|---|---|
| SUBSTRATE | +12.5, +11.8, +20.8, +20.2 | **+16.35 → +16.3** ✅ |
| COUNTING | +28.3, +29.4, +35.0, +29.4 | **+29.4** ✅ |

**Per-set differences: −15.8, −17.6, −14.2, −9.2.**

> ### **MEAN = −14.200 pp = −0.142 per item. REPORTED PAIRED VALUE = −0.142. EXACT TO THREE SIGNIFICANT FIGURES.**

*And the label is right too: the MEDIAN of those differences is −15.0, so the reported figure is the
MEAN and is correctly described as a per-item mean rather than a median.* **A sloppy write-up would
have quoted −15.0 while calling it the same thing.**

## 3. ✅ THREE MORE CONSTRAINTS, ALL SATISFIED

1. **The gate is counting's UPPER bound (+44.2), not its point value** -- standing discipline 18,
   correctly applied. Substrate's best per-set CI reaches **+30.8**, so DOES NOT CLEAR, on all four.
2. **The marginals OVERLAP (+30.8 vs +20.0), and the note says so and refuses to treat that as a
   test** -- *"overlapping marginal intervals are not a test of a difference"*. That is why the
   paired test exists here, which is the correct reason to run one.
3. **Untrained ~0 with CIs spanning zero; trained +16.3 with all four CIs excluding zero.** The
   ordering is coherent and the untrained arm is a real floor rather than a formality.

## 4. 🎯 WHY THIS MATTERS MORE THAN A PASS USUALLY DOES

**Tonight the same check killed:** the B1 cliff (inverted), "6.2 traces/lemma" (mismatched
denominator), "92,155 traces" (part exceeded whole by 3.5x), "63% past 0.79" (wrong operation), and
a detector of my own that fired 3,990 times on dates.

***Five failures and one pass means the check DISCRIMINATES rather than condemns.*** **A claim that
survives it is meaningfully stronger than one that was never subjected to it -- and this is the claim
the top item and the F5 build decision both rest on.**

## TLDR

Tonight's review found that only one of my five working rules actually earned its place: **put a
number next to another number that limits it, and see whether they agree.** That rule caught four of
my own mistakes today.

**So I pointed it at the biggest claim we haven't checked** — the one our current top priority rests
on, which says our system is measurably behind simple word-counting.

**It passes, and it passes exactly.** The headline difference was worked out one way; adding up the
four individual test sets gives the same answer to three decimal places. Those are genuinely separate
calculations, so agreeing was not guaranteed.

**Three smaller checks also hold.** The comparison is made against the tough end of word-counting's
range rather than its average — the stricter choice. The write-up openly says the simple comparison
was inconclusive and explains why a better test was needed, rather than quietly picking the flattering
one. And the do-nothing baseline really does score nothing.

**Why a pass is worth reporting:** the same check destroyed five things today. **One that survives it
is genuinely more trustworthy than one nobody tested** — and this is the claim our current direction
depends on.

## QUESTIONS

None.

## NEXT STEPS

1. **The `## POSITION` claim stands as written.** *Checked, not assumed.*
2. **The check discriminates (5 kills, 1 pass), so it is worth applying to the remaining standing
   claims** rather than treating it as a fault-finder.
3. *`compare_detectors_paired()` in that harness is the reusable form, per the note's own tail.*
