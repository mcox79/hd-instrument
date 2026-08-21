# T1b -- **THE FORAGE-vs-FROZEN DIRECTION *REVERSES* WHEN THE METRIC STOPS BEING REGISTER-MATCHED** — and the map's "free re-score" does not exist

**No new run.** Re-reading `data/exp_information_foraging_reading_v1/metrics.json` (`run_mode: full`,
5 arms x 10,000 sentences, **`substrate_seed = 20260814` -- ONE SEED**).

---

## 1. 🔴 FIRST, A CORRECTION TO THE ORGAN MAP: **THE DECISIVE RE-SCORE IS NOT FREE**

`ORGAN_MAP` §10.1/H2b-5 says the register question is settled by
*"a re-scoring of an existing cell, **not a new run**."*

**It cannot be.** The cell computes `banked_subjects` at
`experiments/exp_information_foraging_reading_v1.py:601` and **never persists it** -- only counts
reach `metrics.json`, and `units.jsonl` carries the same per-arm dicts. **The banked term lists do
not exist on disk.** Any coverage re-score against a different probe vocabulary therefore **requires
a re-run.**

*Recorded because the map's sentence would send the next reader looking for a free check that is not
there -- and because the fix is two lines: persist `banked_subjects` per arm.*

## 2. ✅ BUT A **REGISTER-NEUTRAL** MEASURE WAS ALREADY IN THE ARTIFACT

The held-out-coverage probe is SUBTLEX-backed general-English vocabulary, which is **register-matched
to FROZEN's 75%-news diet** (T1's finding). **WordNet agreement is not** -- it scores the
`(subject, object)` pairs *each arm actually banked*, against WordNet. **It never consults a probe
vocabulary, so it cannot favour anyone's corpus by register.**

| arm | pairs | scorable | **WN-confirmed related** | agreement rate | mean wup |
|---|---|---|---|---|---|
| **FORAGE** | 604 | 544 | **191** | **0.3511** | 0.4059 |
| FROZEN | 696 | 572 | 167 | 0.2920 | 0.3765 |
| FIXED_LEAVE | 440 | 417 | 142 | 0.3405 | 0.4102 |
| FORAGE_REFUSAL | 383 | 334 | 111 | 0.3323 | 0.3833 |
| RANDOM | 157 | 132 | 51 | **0.3864** | 0.4256 |

**➡️ FORAGE BEATS FROZEN ON BOTH HALVES OF THIS METRIC — the RATE (0.3511 vs 0.2920) AND the
ABSOLUTE COUNT (191 vs 167) — having banked FEWER pairs (604 vs 696).** *On the register-matched
probe FROZEN won 0.0743 to 0.0617. **The direction of the comparison flips with the metric, and the
flip is exactly what T1's register diagnosis predicted.***

**AND THE OBVIOUS OBJECTION IS CHECKED AND FAILS:** WordNet covers common words better than
technical ones, which should penalise the biology-heavy arm. **It does not** -- FORAGE has the
*highest* scorable fraction of any arm (**0.901** vs FROZEN 0.822, RANDOM 0.841). The metric is not
quietly excluding FORAGE's vocabulary.

**RANDOM's higher RATE is precision-at-low-recall, not quality:** it scored 132 pairs to FORAGE's
544 and produced **51 confirmed facts to FORAGE's 191 — 3.75x fewer.** *Reporting its rate without
its denominator would be the "an empty representation scores perfectly" failure in a new costume.*

## 3. ⚠️ **WHAT THIS IS NOT: `replication_gate.py` SAYS `SINGLE_SEED_HYPOTHESIS`**

```
replication_verdict([191-167], controls={'RANDOM_minus_FROZEN': [51-167]}, lower_is_better=False)
  -> VERDICT: SINGLE_SEED_HYPOTHESIS
```

**The cell ran ONE seed** (`substrate_seed = 20260814`; `cardinality: 5 units = 5 arms x 1 seed`).
**So this reversal is a HYPOTHESIS, not a result**, and it is filed as one. *Four claims were
withdrawn in one session for exactly this shape; the guard exists so that judgement is not the only
thing standing between a clean-looking number and a retraction.*

*The control does behave: the information-free arm's effect (RANDOM − FROZEN = **−116**) does not
reproduce the treatment's (**+24**) -- it runs the opposite way.*

## 4. WHERE THIS LEAVES THE ORGAN — **BOTH FINDINGS STAND, AND THEY ARE ABOUT DIFFERENT THINGS**

| | verdict |
|---|---|
| **QUALITY of what it learned** | **FORAGE ≥ FROZEN**, on the metric that cannot be register-gamed -- *single-seed* |
| **WHERE it chose to read** | **UNCHANGED AND STILL BAD.** `dominant_domain = textbook_biology, 0.63245` -- the organ built to break a 64.5% biology skew produced a 63.2% one |

**These do not conflict.** Section 2 is about *how good the facts were*; T1's finding is about *where
it went to get them*. **The leave rule (PINNED, Charnov 1976) is doing its job; the patch-CHOICE
function (UNPINNED) is not.** *A cell can mine an adjacent seam expertly and still be in the wrong
mine.*

## TLDR

Yesterday's record said this organ **lost** to the old fixed reading schedule. I found the losing
scoreboard was tilted — it counted everyday words, and the old schedule reads mostly everyday news.
**So I looked for a fairer scoreboard, and one was already sitting in the results file.**

Instead of asking "how many common words did it pick up," it asks "of the facts it actually wrote
down, how many does an independent dictionary agree are real relationships?" **That can't favour
anyone's choice of reading material.** On that measure the organ **wins** — better hit rate (35% vs
29%) *and* more correct facts in total (191 vs 167), from fewer attempts.

**Two honest brakes on that.** It's **one run with one seed**, and our own guard classifies it as a
hypothesis rather than a finding — this is the exact shape of four claims I withdrew earlier this
week. And the random-reading arm has a *higher* hit rate, but only because it wrote down four times
less; counted properly it produced **51 correct facts against 191**.

**Also: the organ map claims this check was free. It isn't.** The experiment throws away the actual
word lists and keeps only counts, so a proper redo needs the experiment re-run. That's a two-line
fix worth making before anyone plans around it.

**And none of this rescues the real problem.** Being *good at judging what it read* is a different
thing from *choosing well what to read* — and it still walked back into biology.

## QUESTIONS

None.

## NEXT STEPS

1. **Persist `banked_subjects` per arm** (two lines) so the coverage re-score becomes possible at all.
2. **Re-run at >=3 seeds** to move the reversal out of `SINGLE_SEED_HYPOTHESIS`. *Cheap and decisive;
   the cell is already resumable.*
3. **The build target is unchanged: the patch-CHOICE function.** Quality was never the deficit.
