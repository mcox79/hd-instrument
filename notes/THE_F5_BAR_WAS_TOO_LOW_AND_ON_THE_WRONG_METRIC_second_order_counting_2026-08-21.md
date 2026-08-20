# THE F5 BAR I PRE-COMMITTED WAS **TOO LOW AND ON THE WRONG METRIC** -- SECOND-ORDER COUNTING, AND WHY ABSOLUTE RANK CANNOT BE THE READ-OUT

> # 🚫 SUPERSEDED 2026-08-21 (same day) -- **THE SLOT-EFFECT STORY BELOW WAS LARGELY A LOOKUP BUG**
> This note's central claim -- *"the floor ranks that slot first 42.6% of the time even when the word
> is CORRECT, so most of its skill is a SLOT property"* -- was computed with a SURFACE-vs-LEMMA
> lookup bug that let unknown/inflected words outrank real candidates in BOTH conditions.
> **After the fix the original-sentence hit rate falls 42.6% -> 12.5%, and second-order counting's
> discrimination rises +10.9 pp -> +28.3 pp.** The slot effect is real but MUCH smaller; the floor is
> far STRONGER than this note says.
> **WHAT SURVIVES, AND IT IS THE IMPORTANT HALF:** absolute rank IS slot-inflated for every arm, so
> the paired anomalous-vs-original difference is the only valid read-out -- that conclusion is
> unchanged and is now built into `tools/f5_evaluation_harness.py`. **CURRENT BAR: +44.2 pp**, not the
> +18.8 below.


**I set the bar with FIRST-order co-occurrence: *"beat median rank 4.0 of ~9."*** This project's
standing position is that we only **TIE second-order** counting, which is repeatedly the stronger
floor -- so a bar set on first-order risks being **a weakened gate**, and F5 could clear it while
still losing to plain counting. Checked before anything was judged against it.

---

## 1. SECOND-ORDER COUNTING IS FAR STRONGER IN ABSOLUTE RANK

Comparing each word's whole PPMI co-occurrence **profile** against its neighbours' -- so a word need
never have been SEEN with them, only keep similar company.

| floor | OPTIMISTIC | MIDPOINT | PESSIMISTIC | tie mass |
|---|---|---|---|---|
| **SECOND-ORDER** | **1.0** | **1.0** | **1.0** | **~0, 0.8-1.7% items flagged** |
| first-order surprisal | 1.0 | 4.0 | 5.0 | 40-50% items flagged |

**1.0 under BOTH tie conventions on all four independently-built sets.** Not a tie artifact -- the
failure that produced three false results here. First-order's optimistic 1.0 *is* tie-inflated; its
honest read is the midpoint 4.0.

## 2. 🚨 **AND THEN THE CONTROL REVERSED THE READING -- I NEARLY FIRED THE KILL CONDITION**

Median rank 1.0 reads as *"counting SATURATES this task"*, and the F5 design pre-committed
*"IT FAILS IF co-occurrence surprisal matches it -- then the monitor is re-deriving counting."*
**I was one step from reporting that the kill condition had fired before the build.**

**It has not.** The same floor, scored on the **ORIGINAL, untouched** sentence at the **same slot**:

| second-order counting, 101 CLEAN items, hit@1 (PESSIMISTIC -- ties count against it) | |
|---|---|
| the **anomalous** sentence | **53.5%** (54 of 101) |
| the **original** sentence, same slot, word is CORRECT | **42.6%** (43 of 101) |
| **paired difference** | **+10.9 pp, 95% CI [+3.0, +18.8]** |
| McNemar | 14 anomaly-only vs 3 original-only, **p = 0.0153** |

**➡️ THE FLOOR RANKS THAT SLOT FIRST 42.6% OF THE TIME EVEN WHEN THE WORD IS CORRECT.** Most of its
apparent skill is a property of **the SLOT** -- content nouns in mid-sentence keep less consistent
company than function words -- **not of the anomaly.** Its real discrimination is modest and it is
REAL: the CI excludes zero.

## 3. **SO ABSOLUTE RANK CANNOT BE THE READ-OUT AT ALL, FOR ANY ARM**

Every arm's absolute rank is inflated by the same slot effect, so *"F5 achieved rank N"* would be
uninterpretable no matter what N was. **The only valid read-out is the PAIRED anomalous-vs-original
difference** -- which is exactly the control I added to catch a confound, now promoted to being the
measurement. *A control that changes the answer was never a control; it was the missing metric.*

## 4. 🎯 THE CORRECTED BAR

> **SUPERSEDED:** ~~beat median rank 4.0 of ~9~~ -- too low, and on a slot-contaminated metric.
>
> **F5 must beat +18.8 pp -- the UPPER bound of second-order counting's paired discrimination, not
> its point value -- on the anomalous-vs-original hit@1 difference over CLEAN frequency-matched
> items, across >=3 independently-built sets, `replication_gate.py` = `REPLICATED`.**
>
> Available headroom: the item ceiling is ~86% and the floor's original-sentence rate is 42.6%, so
> roughly **43 pp** of room exists. The floor takes **10.9** of it.

## 5. WHAT THIS DOES AND DOES NOT SAY

**F5 IS NOT PRE-EMPTED.** Counting takes about a quarter of the available headroom; the task
discriminates. **But the bar is now nearly twice as high as what I pre-committed**, and it is on a
metric that cannot be gamed by slot effects.

**Nothing here measures the substrate.** No F5 exists; no arm in these tables is ours.

## TLDR

Before anything gets judged against the target I set for the missing component, I checked whether I
had set it against the *strongest* competitor. I had not.

I used a simple word-counting method. A slightly cleverer one — compare each word's whole "company
it keeps" against its neighbours' — is **much** better: it puts the planted word in first place,
where the simple method managed fourth.

**That looked like the end of the road**: if plain counting already tops the test, the new component
can't prove anything, and I was about to report exactly that. **Then the check I'd built in saved
me.** Run the same method on the *untouched* sentence, and it still flags that same position first
**42.6% of the time — when the word there is perfectly correct.** So most of its apparent skill is
"that slot tends to look odd", not "that word is wrong".

Its genuine skill is the difference: **53.5% versus 42.6%, about 11 points, and that gap is real.**

Two consequences. **The target I'd set was far too low.** And more importantly, **the way I planned
to score this was wrong for everyone** — raw position is inflated by the slot for every method, so
the only honest score is the before-versus-after comparison. The check I added to catch a problem
turned out to be the measurement itself.

The new component now has to beat about 19 points out of roughly 43 available. Counting takes 11 of
them. There is still room to win — just less, and measured properly.

## QUESTIONS

None.

## NEXT STEPS

1. The corrected bar replaces the old one in the plan and in `STATUS.md`.
2. `tools/hit_at_1_second_order_vs_ceiling.py` and the second-order arm in
   `tools/score_anomaly_set_floors.py` are the instruments; both carry leak control.
3. F5 remains blocked only on cell-authoring.
