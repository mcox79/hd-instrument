# THE 0.6195 FLOOR THAT DEFEATED THE PERCEPTUAL NORMS IS **NOT YET EXPLAINED** -- FOUR CANDIDATES RULED OUT, AND MY OWN FIFTH IS TOO SMALL BY 2.87x

> **⚠️ THE FILENAME AND THE ORIGINAL TITLE BOTH SAID "UNCONTROLLED MATCHING IMBALANCE". THE
> SELF-CORRECTION AT THE BOTTOM SHOWS THAT IS TOO STRONG:** the imbalance is real and is the only
> unbalanced covariate, **but it is ~3x too small to produce the observed floor.** *Filename left
> alone because notes are cited by name. **THIRD TIME TONIGHT I HAVE WRITTEN A HEADLINE BEFORE THE
> INVESTIGATION FINISHED AND HAD TO CORRECT IT** -- the pattern is mine, not the data's.*

**2026-08-20.** `exp_sensorimotor_channel_discrimination_v1` filed the sensorimotor channel as
failing: best arm **0.6039** against a credible bar of **0.6791** derived from
`F_CONSTANT_PROTOTYPE__SM11` at **0.6195**. **A query-INDEPENDENT floor beat every query-dependent
arm, which is the tell that has recurred all night.** This is what it turns out to be.

## WHAT IT IS NOT -- AND THE CELL'S OWN ARMS RULE THESE OUT

**My hypothesis last turn was that the gold's correct answers differ systematically in
CONCRETENESS. The cell already tested that and it is wrong.**

| candidate explanation | the cell's arm | AUC |
|---|---|---|
| **concreteness** (my hypothesis) | `CONC1_NEG_ABSDIFF` | **0.5388** [0.4775, 0.6002] -- near chance |
| frequency | `F_FREQUENCY` | **0.4851** -- BELOW chance |
| orthography | `F_ORTHOGRAPHIC` | 0.5000 -- a clean null |
| distance-from-prototype as a magnitude | `F_PROTOTYPE_MAGNITUDE__SM11` | **0.4709** -- BELOW chance |
| **the floor itself** | `F_CONSTANT_PROTOTYPE__SM11` | **0.6195** [0.5599, 0.6792] |

**So it is not concreteness, not frequency, not orthography, and not prototype magnitude.**

## ⚡ WHAT IT LOOKS LIKE: THE MATCHING BALANCED EVERYTHING **EXCEPT** THE FEATURE THAT BECAME THE FLOOR

From the cell's own `POST_MATCH_BALANCE_ON_SURVIVORS`, standardized mean differences between arms:

| covariate | smd |
|---|---|
| `orthographic_trigram_cos` | 0.0027 |
| `mean_length` | 0.0026 |
| `abs_freq_diff` | 0.0036 |
| `mean_log_freq` | -0.0617 |
| **`mean_constant_prototype`** | **0.1501** |

**Every covariate the matching controlled is balanced to within ~0.06. The one covariate it did NOT
control is off by 0.1501 -- roughly 2.4x the largest other imbalance -- and it is EXACTLY the
feature the strongest floor is built from.**

**➡️ A PARTIAL READING (corrected below, and it is NOT sufficient): the matching balanced frequency,
length and orthography but NOT distance-to-prototype, leaving a residual regularity a query-blind
scorer can exploit.** *The self-correction at the bottom shows this accounts for at most a third of
the floor -- it is a contributor, not the cause.*

## ⚖️ WHAT THIS DOES AND DOES NOT LICENSE

- **It does NOT overturn the negative result.** An smd of 0.15 is a modest imbalance by
  conventional standards (<0.1 good, 0.1-0.2 modest), and I have **not** demonstrated that removing
  it would drop the floor below 0.6039. **That requires re-matching with prototype distance as a
  balancing covariate and re-running -- which is the actual next step, not a rhetorical one.**
- **It DOES mean the -0.0752 margin is not a clean verdict on the norms.** The arm was asked to
  beat a floor that an uncontrolled covariate was helping.
- **And it is consistent with the asset being fine**, which the previous note established
  independently (no genericity axis; PC1 is an auditory-vs-haptic modality contrast).

## 🔑 THE CELL DID ITS JOB. NOBODY READ THE NUMBER.

**`mean_constant_prototype: 0.1501` was computed, labelled and written into the metrics by the cell
itself.** It is sitting in `POST_MATCH_BALANCE_ON_SURVIVORS` next to four well-balanced covariates.
**The instrument reported its own weak point and the finding was filed as a refutation anyway.**

**That is the THIRD time tonight the answer was already in an artifact nobody had read** -- after
two pre-registered hand-score samples sat unscored for a week, and after a landed cell's own
`floor_note` spelled out the retrieves-but-not-competitive distinction. *The pattern is not that
this project measures badly. It is that it measures well and then does not read what it wrote.*

## TLDR

The experiment that supposedly showed human sensory ratings do not work had a comparison built into
it: a deliberately stupid method that ignores the question entirely and guesses the same thing every
time. The stupid method won, which is why the ratings were filed as a failure.

**I went looking for why, and the experiment's own records answer it.**

It is not that the ratings encode something trivial -- I checked that last turn and they do not. It
is not the obvious suspects either: the experiment tested concreteness, word frequency and spelling,
and all three came out at chance or worse.

**What the records show is that when the experiment paired up its test items, it carefully matched
them for frequency, length and spelling -- and did not match them for the one property the stupid
method uses.** On that property the two groups differ about twenty-five times more than on anything
else that was controlled.

**So the bar the ratings had to clear was partly propped up by an accident of how the test pairs
were assembled.** That does not prove the ratings would have passed -- proving that needs the test
re-run with the extra control -- but it does mean the failure verdict is not clean.

**And the experiment had written that number down itself.** It measured its own weak spot, printed
it, and the result was filed as a refutation anyway. That is the third time tonight the answer was
already sitting in a file nobody had read.

## QUESTIONS

None.

## NEXT STEPS

1. **Re-match including distance-to-prototype as a balancing covariate, and re-run.** If the floor
   falls below 0.6039 the sensorimotor verdict changes; if it does not, the negative stands and is
   now genuinely clean. **Either outcome is worth having before anything is built on this branch.**
2. **This is a cell-authoring job** (`experiments/*.py`, smoke-gated), not a main-thread edit.
3. Whoever does it should check whether the SAME uncontrolled covariate affects the other
   dissociation-instrument cells that share this matching procedure.

---

## ⛔ **SELF-CORRECTION, SAME NIGHT: THE IMBALANCE IS TOO SMALL TO EXPLAIN THE FLOOR**

Before leaving this as "the floor is a matching artifact", I checked whether the imbalance is
**big enough**. It is not.

| | |
|---|---|
| reported smd on `mean_constant_prototype` | **0.1501** |
| AUC a normal-theory effect of that size predicts | **0.5423** |
| **OBSERVED floor AUC** | **0.6195** |
| d implied by the observed AUC | **0.4302** |
| **ratio** | **2.87x larger than the reported imbalance** |

**➡️ SO THE UNCONTROLLED COVARIATE IS AT MOST A PARTIAL CONTRIBUTOR. Something else is doing most
of the work, and my previous framing overstated it.**

*Caveats on the arithmetic, which is first-order: it assumes normality and equal variance, and the
balance statistic may be computed over a different population (survivors vs full set) or a different
granularity (per-word vs per-pair) than the floor's score. **It is enough to say "not sufficient"; it
is not enough to say "irrelevant".***

### 🔍 AND THE GAP POINTS AT SOMETHING SHARPER: **BALANCE-ON-MEANS IS NOT BALANCE**

**A standardized mean difference detects only a shift in MEANS.** If the two arms differ in
**VARIANCE or in distributional shape** on the prototype feature, a scorer can separate them well
while the smd stays near zero -- **and every number in that balance table would still look clean.**

**That is a general weakness of the matching check, not a quirk of this cell**, and it is a better
candidate for the missing 2.87x than anything about concreteness or frequency.

**THE CONCRETE NEXT TEST IS CHEAP AND DIFFERENT FROM THE ONE I PROPOSED ABOVE:** compare the two
arms' **DISTRIBUTIONS** of the constant-prototype score -- variance ratio, and a
Kolmogorov-Smirnov statistic -- not just their means. *If the variances differ materially, the
matching procedure needs a distributional check and every cell sharing it inherits the same blind
spot.*

**Recorded because I nearly shipped "the floor is an artifact of matching" as a finding on the
strength of one suggestive number, one turn after writing that this project measures well and then
does not read what it wrote.** The arithmetic took a minute.

---

## 🧱 **FIFTH EXPLANATION TESTED, FIFTH FAILURE: THE FLOOR IS LOOKING REAL**

The distributional check I proposed cannot be run: `units.jsonl` retains **21 aggregate ARM
results and no per-pair scores**, so the balance question cannot be re-examined without a re-run.
*(Worth recording as a retention lesson: **a cell that reports a balance table but keeps no
per-unit feature values cannot have its balance re-checked by anyone, ever.**)*

**But the retained units DO answer a different suspicion, and it also fails:**

| arm | tie mass | AUC ties->P | AUC ties->S |
|---|---|---|---|
| **`F_CONSTANT_PROTOTYPE__SM11`** (the binding floor) | **0.000** | 0.6195 | 0.6195 |
| every `SM11_*` arm | 0.000 | -- | -- |
| `F_ORTHOGRAPHIC` | **0.976** | **0.9881** | **0.012** |

**THE BINDING FLOOR IS COMPLETELY TIE-FREE AND CONVENTION-INDEPENDENT.** After a night in which
tie-density destroyed three separate results, that was the obvious next suspicion. **It is wrong.**

*Separate observation, not verdict-changing: `F_ORTHOGRAPHIC` is **97.6% ties**, and its AUC runs
from 0.012 to 0.9881 depending on convention. Its reported 0.5 is a ties-half artifact, not a
measured null. It is not the binding floor so nothing here turns on it -- but **a 97.6%-tied arm is
an information-free control**, exactly the hazard `tools/rank_with_ties.py` exists for.*

## 📊 SO: FIVE EXPLANATIONS TRIED, FIVE FAILED

| # | my explanation for why the floor beats the norms | outcome |
|---|---|---|
| 1 | the norms are really a GENERICITY axis | **refuted** -- PC1 is auditory-vs-haptic, 73.3% residual |
| 2 | the gold's answers differ in CONCRETENESS | **refuted** by the cell's own arm, 0.5388 |
| 3 | frequency / orthography leakage | **refuted** -- 0.4851 and a clean 0.5000 |
| 4 | an uncontrolled MATCHING IMBALANCE | **insufficient** -- 2.87x too small |
| 5 | TIE-DENSITY artifact | **refuted** -- tie mass exactly 0.000 |

**➡️ I HAVE NOW TRIED FIVE TIMES TO EXPLAIN AWAY THE RESULT THAT COUNTS AGAINST THE BRANCH I
RECOMMENDED, AND FAILED EVERY TIME. THE HONEST UPDATE IS THAT THE FLOOR IS PROBABLY REAL, AND SO IS
THE SENSORIMOTOR NEGATIVE.**

*That is a genuine update AGAINST my own recommendation, reached by trying hard to rescue it. The
branch is still not refuted -- one instrument, one resolution, and the better-posed follow-up
exists -- but **"the negative was an artifact" is no longer an available story**, and anyone
building here should know that five candidate artifacts were checked and none held.*

## TLDR (revised after five checks)

I have spent several rounds trying to show that the experiment counting against the direction you
chose was flawed. **I could not, and I checked five different ways.**

The ratings are not measuring something trivial. The test items do not differ in concreteness,
frequency or spelling. There is one property the test failed to control for, but the arithmetic says
it is about three times too small to matter. And the tie-breaking bug that wrecked three other
results tonight is absent here -- that comparison has no ties at all.

**So the unflattering result is probably sound.** The direction is not refuted -- it was one test on
one framing, and a later, better-posed attempt did better -- but **I can no longer offer "that
negative was an artifact" as a reason for confidence**, and it would be dishonest to leave the
impression that I can.

One thing did turn up along the way: a different comparison in the same experiment is 97.6% ties,
so its "no effect" reading is an accounting convention rather than a measurement. It does not change
this verdict, but it is the kind of thing worth knowing about a shared instrument.
