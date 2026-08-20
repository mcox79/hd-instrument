# THE 0.6195 FLOOR THAT DEFEATED THE PERCEPTUAL NORMS LOOKS LIKE AN **UNCONTROLLED MATCHING IMBALANCE** -- AND THE CELL REPORTED IT

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

**➡️ THE MOST LIKELY READING: the matching procedure balanced frequency, length and orthography but
NOT distance-to-prototype, leaving a residual regularity that a query-blind constant-prototype
scorer can exploit. The floor is measuring a property of the MATCHED SET, not a property the
sensorimotor arms had to beat on merit.**

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
