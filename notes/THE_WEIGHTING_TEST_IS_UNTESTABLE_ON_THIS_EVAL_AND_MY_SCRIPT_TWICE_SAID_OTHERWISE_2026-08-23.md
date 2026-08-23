# THE WEIGHTING TEST IS UNTESTABLE ON THIS EVAL -- AND MY OWN SCRIPT TWICE SAID OTHERWISE

**2026-08-23, strategy session.** I said the calibration findings needed the learning loop run both
ways, and that I had not run it. I ran it. **The answer is that this eval cannot answer the
question**, and the two ways my harness nearly reported otherwise are worth more than the result.

---

## 1. THE SETUP

Two findings stood, both measured on the LOOKUP in isolation: the confidence score does not predict
correctness, and at the low end it is not a weight but a DELETE (`63` of `326` decided answers
dropped by `if n <= 0`). **Four arms, built to SEPARATE the two mechanisms rather than confound
them:**

| arm | priors |
|---|---|
| `WEIGHTED` | `n = round(K_MAX * conf)`, drop if `0` -- **what ships** |
| `NO_DISCARD` | `n = max(1, round(K_MAX * conf))` -- keeps weighting, restores the dropped |
| `FLAT_3` | every committed hit -> `3` -- no weighting, no discard |
| `FLAT_1` | every committed hit -> `1` |

Corpus and scorer are the parent cell's own (`_score_with_overlay`, landed corpus checkpoint), so
the numbers are commensurable with the landed arm rather than coming from a scorer I wrote.

---

## 2. THE RESULT: UNTESTABLE, NOT NEGATIVE

| arm | primary accuracy | vs ships |
|---|---|---|
| `WEIGHTED` | `0.4722` | -- |
| `NO_DISCARD` | `0.4722` | `+0.0000` |
| `FLAT_3` | `0.4722` | `+0.0000` |
| `FLAT_1` | `0.5000` | `+0.0278` |

🚨 **THOSE ZEROES ARE ARITHMETIC, NOT EVIDENCE. THREE OF THE FOUR ARMS INJECT BYTE-IDENTICAL
PRIORS.**

**The blocker is COVERAGE: the dictionary commits on `6` of `33` eval lemmas, and all `6` saturate
at confidence `1.0`.** So there is **nothing for `NO_DISCARD` to restore** (none of the 6 was ever
dropped) and **nothing for `FLAT_3` to flatten** (all 6 are already at 3). `WEIGHTED`, `NO_DISCARD`
and `FLAT_3` are the same arm run three times.

**`FLAT_1` is the only arm that differs, and its `+0.0278` is ONE item out of 36.** At that scale it
carries nothing in either direction.

✅ **SO BOTH CALIBRATION FINDINGS REMAIN OPEN. NEITHER IS CLOSED AS HARMLESS.** *That is a worse
outcome than a clean null and a better one than a false null.*

🔑 **AND THE REASON IS THE LIMIT I HAD ALREADY NAMED AS THE BIGGER ONE:** the organ's `17%` commit
rate. On the eval it is designed for, it answers `6` of `33`. **A weighting scheme cannot be tested
on evidence that is almost never injected.**

---

## 3. MY SCRIPT WOULD HAVE REPORTED A FALSE NULL. TWICE.

**FIRST RUN -- VOID.** I read the eval lemmas from `r["oov_lemma"]`. That key does not exist; the
field is `outcome_verb_lemma`. **Every arm injected ZERO priors, all four returned an identical
`0.5000`**, and the script's own summary text read: *"A ZERO DELTA HERE MEANS THE WEIGHTING AND THE
DISCARD COST NOTHING -- which CLOSES both findings as harmless."*

**SECOND RUN -- STILL NOT A TEST.** Field fixed, priors non-empty, and three arms still identical
for the coverage reason above. **The same canned sentence would have closed both findings again**,
on three copies of one arm.

🔑 **WHAT CAUGHT IT BOTH TIMES WAS PRINTING THE SIZE OF THE INTERVENTION BESIDE THE RESULT** --
`injects 0 lemmas` on the first run, `total pseudo-counts 18 / 18 / 18 / 6` on the second. *Neither
accuracy number looked wrong. `0.5000` and `0.4722` are both plausible values for this eval.*

**This is the project's own rule paying out for the sixth time: `n_grounded=0` printed beside
`anchors +68` is how the only real code bug of an earlier night was found. A number that looks
reasonable cannot be checked by looking at it.**

**TWO GUARDS NOW IN THE SCRIPT, because a caution written as prose gets violated:**
1. **Refuse to run on zero eval lemmas** -- the void case cannot recur silently.
2. **NON-DEGENERACY GATE: compare the arms' prior sets BEFORE running them, and report which arms
   are identical to what ships.** A zero delta against an identical arm now prints *"THE COMPARISON
   IS UNTESTABLE ON THIS EVAL, NOT NEGATIVE"* instead of a conclusion.

*This is the standing "construct the information-free version of your winning arm and check it
LOSES" discipline turned around: **construct the arms and check they DIFFER, before you believe any
comparison between them.***

---

## 4. WHAT THIS DOES AND DOES NOT ESTABLISH

- ✅ **ESTABLISHED:** on this eval, the weighting and discard questions cannot be answered, and the
  reason is measured (`6` of `33` commit; all saturate).
- 🚫 **NOT established:** that the weighting is harmless. Three identical arms say nothing.
- 🚫 **NOT established:** that `FLAT_1` is better. One item of 36.
- 🚫 **NOT** a landed cell -- inline, `scratch/`, no `metrics.json`. It does reuse a landed corpus
  checkpoint, which is a CACHE and is not being called a reproduction.

---

## TLDR

Last stretch I found two problems with how the system weights its own confidence, and said plainly
that I had not checked whether either actually costs anything. I checked.

**The check cannot be run.** Not "no effect" — cannot be run. The dictionary only offers an opinion
on 6 of the 33 words the test covers, and all 6 come in at maximum confidence. So three of my four
comparison arms are literally the same arm with different names, and comparing them produces a
perfect zero that means nothing at all.

**My script was ready to announce that zero as good news, twice.** The first time because a typo in
a field name meant no arm did anything; the second because of the coverage problem. Both times the
accuracy numbers looked entirely reasonable. What caught it was printing *how much was injected*
next to *how well it scored* — a number that looks fine cannot be checked by looking at it.

The script now refuses to draw a conclusion when the things being compared are identical.

## QUESTIONS

None.

## NEXT STEPS

1. **Both calibration findings stay open**, and settling them needs an evaluation where the
   dictionary actually commits — not another run of this one.
2. **The `17%` commit rate is now blocking two separate questions**, which strengthens the case that
   coverage is this organ's real limit rather than its accuracy.
3. The non-degeneracy gate is worth stealing for any future arm comparison here.
