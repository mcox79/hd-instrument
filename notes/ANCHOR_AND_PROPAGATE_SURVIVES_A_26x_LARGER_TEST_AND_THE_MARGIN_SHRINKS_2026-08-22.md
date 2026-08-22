# ANCHOR + PROPAGATE SURVIVES A 26x LARGER TEST, AND THE MARGIN SHRINKS BY TWO THIRDS

**2026-08-22, strategy session.** A powered re-test of `hdlab/wordnet_polarity_propagation.py`, the
organ for the direction the plan named on 2026-08-06/07 and did not choose tonight: **ground a small
affective anchor and reason outward**, because antonyms are distributional twins, so good/bad is in
neither grammar nor text statistics.

**Its standing result was `0.833` on TWELVE held-out verbs.** Twelve.

---

## 1. THE RESULT

| | |
|---|---|
| scored items | **`326`** (against the reported `12`) |
| organ accuracy | **`0.6595`** CI95 `[0.6074, 0.7117]` |
| majority-class floor, **recomputed on the committed subset** | **`0.5583`** CI95 `[0.5031, 0.6135]` |
| paired difference, same items | **`+0.1012`** CI95 `[+0.0245, +0.1779]`, **EXCLUDES ZERO** |
| McNemar discordant pairs | `96` organ-right / `63` floor-right, **p = `0.0118`** |
| information-free twin (random POS/NEG, same items) | `0.4847` -- **LOSES** |
| seed ablation (anchor polarity labels SHUFFLED) | `0.4645` CI95 `[0.4238, 0.5053]` -- **COLLAPSES TO CHANCE** |
| commit rate | **`326` of `1,971` = `17%`** |

**THE MECHANISM IS REAL AND THE HEADLINE WAS INFLATED BY ROUGHLY THREE.** `0.833` on 12 items
becomes `0.6595` on 326 against a floor of `0.5583` -- a margin of about **ten points, not
thirty-three**. *The direction survives; the magnitude does not.*

---

## 2. THE TWO TESTS DISAGREE, AND SAYING WHICH ONE I TRUST IS THE POINT

| test | verdict |
|---|---|
| independent intervals: organ LOWER `0.6074` vs floor UPPER `0.6135` | 🔻 **NOT_SEPARATED** (overlap `0.006`) |
| paired difference on the same 326 items | ✅ `+0.1012` CI `[+0.0245, +0.1779]`, excludes zero |

**THE PAIRED TEST IS THE CORRECT ONE HERE AND I WILL SAY WHY RATHER THAN JUST PREFERRING IT.** Both
arms score **the same 326 items**; comparing two independent intervals discards that pairing and is
strictly less powerful. Every item where both are right or both are wrong is noise the paired test
removes and the independent test keeps.

⚠️ **BUT THE STANDING BAR IS PHRASED FOR INDEPENDENT ARMS -- "CI-separated over the floor's UPPER
bound" -- AND UNDER THAT READING THIS DOES NOT CLEAR IT.** I am not going to quietly report the
favourable test. **Both are above; the honest summary is: significant under the correct paired test
(`p = 0.0118`), NOT separated under the conservative independent one, and the margin is small enough
that which test you use changes the verdict.** *That is itself the finding at this sample size, and
the fix is more items rather than more argument.*

---

## 3. WHY THE GRADING IS NOT CIRCULAR -- THE PROPERTY THAT MADE THIS WORTH RUNNING

- The mechanism uses **WordNet structure** plus a **hand-authored 52-word seed**.
- The gold is **human valence ratings** (Warriner et al., `13,905` words with a usable score),
  collected and published **years before this organ existed**. ✅ **THE TEST ITEMS EXISTED BEFORE THE
  MECHANISM DID** -- this project's strongest free predictor.
- **WordNet is used ONLY to decide which gold words have a verb sense** -- a population filter, never
  the answer. *Grading with WordNet would be ground-by-X-and-grade-by-X; filtering with it is not,
  and the distinction is stated rather than assumed.*
- The mechanism's own seed is **excluded**: `45` of the `52` seed words appear in the gold and all
  are removed, along with the prior held-out set (`84` total).

---

## 4. THE CONTROLS, AND THE ONE THAT SURPRISED ME

🔑 **THE SELECTION CHECK CAME BACK CLEAN, WHICH I DID NOT EXPECT.** The organ abstains `83%` of the
time, so the obvious worry is that it answers only the easy extremes and its accuracy is a property
of *which* items it answers rather than of how well it answers.

| | mean `|valence - 5|` |
|---|---|
| items it COMMITTED on | `1.635` |
| items it ABSTAINED on | `1.716` |

**It commits on slightly HARDER items than it skips.** *So the accuracy is not bought by
cherry-picking, and the abstention is not a hidden difficulty filter.* This is the confound that has
killed several claims here and it is simply absent.

✅ **THE SEED ABLATION IS THE STRONGEST CONTROL AND IT PASSED CLEANLY.** Shuffling the anchor's
polarity labels drops the organ to `0.4645` -- chance. **So the anchor is doing the work, not
WordNet's structure alone.** *That matters for the brain claim specifically: it says the GROUNDED
SEED is load-bearing, which is the whole hypothesis.* ⚠️ *Unexplained and worth someone's attention:
the ablated arm COMMITS MORE (`564` vs `326`). Shuffling polarity should not change how often the
mechanism is confident, and it does. **I do not know why, and I am not going to invent a reason.***

**BY STAGE:** antonym opposition `0.8421` on `19` items (CI `[0.6842, 1.0000]` -- **too few to
carry weight**); neighbour vote `0.6482` on `307`. **The bulk of the result is the neighbour vote.**

---

## 5. HOW THIS BECAME POSSIBLE, AND THE NEAR-MISS

The organ's entire gold universe was the hand-authored seed plus ~32 held-out words, so I was about
to record **"a powered test cannot be built, the blocker is data"** -- the same call made on
2026-08-21 for the meaning test at n=40.

🔻 **THAT WOULD HAVE BEEN WRONG. THE GOLD WAS ALREADY ON DISK** at
`data/grounding_testbed/Ratings_Warriner_et_al.csv`, and **my first check missed it because I
grepped instead of enumerating** -- the grep never reached that directory. **AN ABSENCE CLAIM
REQUIRES AN ENUMERATION, NOT A SEARCH**, for the second time in this project's record; the
enumeration walked `8,808` directories and `6,537` tabular files with a positive control confirming
it reached known data.

🔻 **AND THE PARSE RETURNED ZERO ROWS ON THE FIRST ATTEMPT** -- the columns are `Word` and
`V.Mean.Sum`, and I had lowercased the header when checking but not when reading. *A zero from my own
parser, presented as an absence, is exactly the failure the 08-21 note records against its own SimLex
reader. Two nights running, same trap, different file.*

---

## 6. WHAT THIS DOES NOT SAY

- 🚫 **Not that the organ is good enough to wire.** `17%` commit rate: it answers one polar verb in
  six. It is **coverage-limited**, the same shape as the OOV-36 finding.
- 🚫 **Not that `0.833` was wrong** -- it was twelve items, which is a number that cannot carry a
  claim in either direction.
- 🚫 **Not a test of the plan's actual specification.** The plan calls for a **context-conditioned
  superposition**; this assigns ONE value per word. **So this is a FLOOR for the direction, not a
  test of it** -- the same caveat the archive already carries and which still stands.
- 🚫 **Not a landed cell.** This is an inline measurement, `~1` minute, scripts in `scratch/`. It
  writes no `metrics.json` and should not be cited as a landed verdict.

---

## TLDR

There is a long-standing idea here about how a system could learn what is good and what is bad:
you cannot get it from reading, because words like "love" and "hate" appear in almost identical
sentences. So you hand-label a small set of words and let the system reason outward from them
through a dictionary of word relationships.

That idea had been tested on **twelve words**, where it looked excellent. I found a set of
**thirteen thousand words rated for good-vs-bad by actual people**, already sitting on our disk,
and re-tested on **326** of them.

**It works, and it is much weaker than it looked.** It gets about 66 in 100 right where always
guessing "good" gets about 56 — a real gain, but a third the size the small test implied. Two
reasonable ways of checking whether that gain is solid disagree with each other, which at this
sample size is honest to report rather than resolve by picking the friendlier one.

The most encouraging part: when I scrambled the hand-labelled starting words, performance fell to
coin-flip. **The hand-labelled anchor is genuinely doing the work** — which is the whole claim. The
least encouraging: it only ventures an answer about one word in six.

I nearly recorded "we cannot test this, we lack the data." The data was already here; my first
search just never looked in that folder.

## QUESTIONS

None.

## NEXT STEPS

1. **The gap between the two tests closes with more items, not more argument.** Relaxing the polarity
   band or including non-verbs would grow the population; both change the task, so say which.
2. **The `17%` commit rate is the bigger limit than the accuracy** — coverage, not discrimination,
   is what stops this being useful, and that is a different repair.
3. **Somebody should explain why shuffling the anchor makes it commit MORE often** (`564` vs `326`).
   That should not happen and I do not have a reason.
