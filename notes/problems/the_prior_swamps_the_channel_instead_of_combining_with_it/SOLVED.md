---
problem: the_prior_swamps_the_channel_instead_of_combining_with_it
status: REFUTED
bar: "ON THE SUBORDINATE-SENSE POPULATION, A COMBINED ARM MUST BEAT *BOTH* SINGLE CUES, CI-SEPARATED, WITHOUT LOSING ON THE DOMINANT POPULATION." -- (1) beat the grounded channel alone (0.4811) on subordinate items (the hard half; zeroing the prior only RECOVERS the channel and is NOT a pass); (2) do no harm on dominant items (prior 0.5508); (3) floors recomputed per population, CI half-widths + null p95 beside every margin; (4) an info-free twin of the reliability signal must LOSE, AUC reported SEPARATELY from the gate delta; (5) report coverage.
result: NO gold-blind combined arm meets the bar. Subject-weighted hit@1, one masked WSD trial per (word, sentence), n = 53 subordinate words the grounded channel covers, chance 0.3854. A WINNING MECHANISM EXISTS but it is not gold-blind reachable: SUPPRESSING the dominant sense (a NEGATIVE prior weight; reordered-access, Duffy/Rayner 1988) beats the channel on subordinate -- fixed b=-1.5 scores 0.7673 vs channel 0.4811, +0.2862 CI [+0.1761, +0.4025] -- but it CRASHES the dominant population to 0.3103 vs prior 0.5855, -0.2752 CI [-0.3385, -0.2137]. It is a pure population trade-off. Every GOLD-BLIND arm fails: reliability-weighted (independent-channel recipe, LOO) 0.0189; conflict-shrink best 0.3789; inverse-variance-from-peakedness 0.1667; fixed z-sum (= BAYES_HUB) 0.1415; and a gold-blind gated suppressor (params maximize overall accuracy) lands 0.1588 on subordinate -- ALL far below CHANNEL 0.4811, none doing no harm.
floor: strongest floor actually run = CHANNEL alone (grounded coherence) = 0.4811 on the 53 subordinate words, reproduced from disk (matches the brief exactly). Ceilings, all run: ORACLE_ROUTE (per-item pick the better cue) = 0.4811 = channel EXACTLY (prior wrong on 100% of subordinate items, routing cannot help); MONOTONE ORACLE_BLEND (prior >= 0) = 0.4748 (no headroom); SIGNED oracle (prior weight free, incl. suppression) = 0.7799 (headroom EXISTS, only via suppression). The prior alone = 0.0000 by construction.
controls: (a) ORACLE_ROUTE = CHANNEL and monotone ORACLE_BLEND = 0.4748 EXCLUDE that any routing or prior-helps blend beats the channel. (b) SIGNED oracle 0.7799 vs monotone 0.4937 EXCLUDES that the failure is "no rule can beat the channel" -- a suppression rule can; the constraint is elsewhere. (c) NO GOLD-BLIND DETECTOR: AUC(channel-disfavours-MFS -> subordinate) = 0.5114, AUC(peakedness -> prior-wrong) = 0.4033, AUC(channel-conf -> channel-right) = 0.5396 -- all reported separately from deltas; a gold-blind gated suppressor selected on overall accuracy scores 0.1588 on subordinate; even a split-KNOWING best-case gate reaches only 0.5252 sub / 0.4026 dom (does not beat channel, harms dominant); and its INFO-FREE TWIN detector (permuted) scores 0.6572 sub -- i.e. the real detector does NOT beat a random one, so it carries no signal. (d) CORRELATED ERROR: 95.65% of the 46 subordinate channel-errors sit on a HIGHER-frequency sense than the truth, phi(prior-correct, channel-correct) = +0.057 -- the channel is itself frequency-biased, which is WHY monotone blending cannot help and why the detector is weak. (e) info-free twin channel = 0.2979 << 0.4811 EXCLUDES that the channel result is a machinery artifact.
files_changed: experiments/exp_reliability_weighted_cue_combination_subordinate_sense_v1.py, experiments/exp_reliability_weighted_cue_combination_signed_suppression_v1.py, verification/test_reliability_weighted_cue_combination_subordinate_sense.py, notes/problems/the_prior_swamps_the_channel_instead_of_combining_with_it/SOLVED.md
reverify: .venv/Scripts/python.exe verification/test_reliability_weighted_cue_combination_subordinate_sense.py
---

# THE PRIOR SWAMPS THE CHANNEL -- REAL DEFECT; THE FIX EXISTS BUT NEEDS A DETECTOR WE DO NOT HAVE

**Plain-language TLDR.** When our reader guesses a word's meaning it uses two clues: how common each
meaning is (strong) and what the surrounding words suggest (weaker, grounded). On rare-meaning words
the common guess is guaranteed wrong, and our fixed 50/50 mixing rule lets it drown out the correct
grounded clue -- the combined answer (0.14) is worse than either the grounded clue alone (0.48) or
random (0.39). **The brief was right that this is a mixing defect, not a useless clue -- I reproduced
it exactly.** *Can we solve it?* **The mechanism that WOULD win exists, and it is real neuroscience:
when the context strongly points at the rare meaning, don't just down-weight the common meaning --
actively SUPPRESS it. Do that and rare-meaning accuracy jumps from 0.48 to 0.77, clearly beating the
grounded clue.** But there is a catch that turns out to BE the problem: suppression helps the
rare-meaning words by exactly as much as it HURTS the common-meaning words (which crash from 0.59 to
0.31). It is a see-saw. To win you must know, for each word, WHICH side it is on -- and that is the
one thing we cannot measure without already knowing the answer. Every blind signal I tried to detect
"this is a rare-meaning context" is no better than a coin flip (0.51), and a random detector does
just as well as our real one. **So: not "we can't solve it." Rather -- the fix is a suppression
switch plus a detector for when to flip it, and the detector is missing because the only per-word
evidence we have comes from the same weak, frequency-biased grounded clue.** Fix that clue (make one
whose mistakes are independent of frequency) or learn the detector from labels, and this becomes
solvable. That is the same missing piece two other problems already pointed at.

## What I built (brain foundation, PINNED vs OUR-INVENTION)

The task is the priority-1 submission's exact live instrument (`exp_reader_sense_selection_bayesian_
hub_v1`): mask a word, hand the grounded hub the remaining content words, pick the intended sense. I
imported its `HubSelector`, sense-frequency prior and z-scoring VERBATIM, so **CHANNEL 0.4811 and the
fixed-sum collapse 0.1415 reproduce the brief by construction** (the reverify confirms it). New parts:
the combination rules, the ceilings, and the suppression analysis.

**PINNED.** Reliability-weighted cue combination (Ernst & Banks 2002): weight each cue by 1/variance,
DYNAMICALLY per item. The instrument z-scores BOTH cues to unit variance and sums -- forcing EQUAL
weight on every item, the opposite of the brain computation. Conflict monitoring (Botvinick & Cohen
2001) as the gating trigger. **Subordinate-bias / reordered access (Duffy, Morris & Rayner 1988):**
strong subordinate context SUPPRESSES the dominant sense -- this is the mechanism that wins here, and
it is why I tested a NEGATIVE prior weight, not just a small one.

**OUR-INVENTION-UNDER-TEST (labelled).** Every "reliability"/"detector" proxy is ours. Guided by this
repo's three landed reliability cells, I tested: reliability-weighting via the independent-channel
HARD_PASS recipe (LOO); inverse-variance from peakedness (the derived trap); conflict-shrink; the
signed (suppression) oracle and its fixed and GATED forms; and info-free twins throughout.

## What I measured -- the decisive numbers

| subordinate items (subject-weighted, n = 53, chance 0.3854) | value | note |
|---|---|---|
| PRIOR alone | 0.0000 | zero by construction |
| **CHANNEL alone -- the floor to beat** | **0.4811** | -- |
| FIXED z-sum (= BAYES_HUB) | 0.1415 | the swamping |
| best gold-blind reliability/gate arm | 0.02 - 0.38 | all below channel |
| **ORACLE_ROUTE / monotone ORACLE_BLEND** | 0.4811 / 0.4748 | prior-helps rules cannot beat channel |
| **SIGNED oracle (suppression allowed)** | **0.7799** | headroom EXISTS -- only via suppression |
| fixed suppression b=-1.5 | **0.7673** | +0.286 CI[+0.176,+0.403] over channel |
| gold-blind gated suppressor (overall-selected) | 0.1588 | detector too weak to fire selectively |
| split-KNOWING best-case gate (diagnostic) | 0.5252 | barely > channel, and... |

...that same split-knowing gate scores **0.4026 on dominant** (prior there is 0.5855), and its
**info-free twin detector scores 0.6572 on subordinate** -- higher than the real detector. The
detector carries no signal.

**The see-saw, in one line.** Suppression strength `b` traded across the two populations:
`b=-1.5` -> subordinate 0.767 / dominant 0.310; `b=0` -> 0.481 / 0.408; `b=+1` -> 0.142 / 0.525.
The two populations want opposite `b`, and no gold-blind signal (all AUCs 0.40-0.54) tells them apart.

**Why the detector is weak (the mechanism).** On the 46 subordinate items the channel gets wrong,
95.65% have the channel's wrong pick on a HIGHER-frequency sense than the truth. The grounded channel
is itself frequency-biased, so the "channel disagrees with the common sense" trigger fires as often on
dominant-items-the-weak-channel-got-wrong as on genuine subordinate items. Detector quality is
bottlenecked on channel quality.

## Why this is REFUTED (and what I corrected from my own first pass)

The bar's hard half -- beat CHANNEL 0.4811 on subordinate WITHOUT harming dominant, gold-blind -- is
not met by any arm. **But my first draft over-claimed "structurally unreachable" on the strength of
the monotone blend oracle (0.4748). That was wrong, and the disk corrected it:** a SIGNED oracle that
allows suppression reaches 0.7799, and a fixed suppression beats the channel by +0.286 CI-separated.
The correct statement is narrower and more useful: **the winning mechanism (suppression) exists; the
bar is unreachable GOLD-BLIND because no signal we can compute detects when to fire it, and that
detector is bottlenecked on the channel's own frequency bias.** REFUTED stands -- the bar is unmet --
but as a well-characterised negative that names the missing organ, not a dead end.

## What I did NOT establish

- **A LEARNED detector.** The bar demands gold-blind (info-free twin loses); every route I tested is
  unsupervised. A detector TRAINED on the subordinate/dominant split is a different regime and could
  in principle approach the 0.78 signed-oracle ceiling. I did not build it. So "no route solves it" is
  bounded to gold-blind routes -- and the suppression finding says a supervised route is worth trying.
- **Coverage is not random** (53 of 77 subordinate words). The 95.65% correlated-error figure is a
  property of the covered population.
- **DISK vs BRIEF:** the brief's untested crux -- that peakedness predicts the prior's systematic
  error -- is REFUTED (AUC 0.40). The brief's "correlated-error regime" inference is CONFIRMED. The
  brief's dominant-prior 0.5508 is the MICRO rate; subject-weighted (the bar's scorer) it is 0.5768.

## What would have to change in hdlab/ (proposed, not landed -- Q111)

**Do NOT wire the fixed-weight z-sum** as a sense-selection rule -- it destroys the channel. **Do NOT
wire a monotone reliability-weighted variant** -- the cues are frequency-correlated, so it cannot beat
the channel. **A suppression term (negative prior weight on subordinate-biasing context) is the
mechanism that would work** -- but only behind a subordinate-context DETECTOR, and no gold-blind
detector is accurate enough (AUC 0.51). So the wiring order is: FIRST build/learn a detector of
subordinate-biasing context (equivalently, a grounded cue whose errors are independent of frequency --
the `reader_meaning_channel` problem); THEN a suppression-gated combiner becomes admissible. Until
then the honest read-out is the frequency prior alone (MFS), which the aggregate already prefers.

## What I would withdraw first if wrong

The most exposed claim is **"the grounded channel's errors are frequency-correlated" (95.65%)** --
n=46, and coverage is not random. If coverage selects frequency-dominated words the figure could be
overstated. I withdraw it before the signed-oracle/suppression result, which is arithmetic on the
saved vectors. Second: the split-knowing gate and its info-free twin are selection-overfit on both
sides; I lean on the clean AUC (0.51), not on their point values, for "the detector carries no signal."

## QUESTIONS

None. The instrument reproduces the brief exactly, the ceilings (routing, monotone-blend, signed) are
computed not assumed, every control excludes something, and the witness passes all 13 checks.

## NEXT STEPS

1. **The answer to "can we solve it?" is: the mechanism is suppression, and it needs a detector.**
   Do not open another "fix the mixing rule" brief for monotone blends -- there is no headroom there.
2. **Open a detector brief, two admissible forms:** (a) a LEARNED subordinate-context detector (train
   on the profile/other-words split, apply held-out, info-free twin must still lose; ceiling = the
   0.78 signed oracle); (b) a grounded cue whose errors are INDEPENDENT of sense frequency, which is
   `reader_meaning_channel` from the other side. Either unlocks the suppression combiner.
3. This converges with `reader_meaning_channel` and `store_survives_a_partial_cue`: three problems now
   point at the same root -- the grounded channel is too frequency/co-occurrence-correlated to add
   independent signal, so what is missing is either an independent second cue or a learned control that
   knows when to trust it. The shared redirect is worth more than any one finding.

---

## INTEGRATED_BY_STRATEGY -- 2026-08-24

Re-verified (13 checks pass). Review EXCELLENT. My brief's framing is REFUTED at the ORACLE level: a perfect per-item router scores 0.4811, exactly the channel, because the prior is wrong on 100% of these items. No monotone blend has headroom (0.4748). Only a SIGNED (suppression) rule does (0.7799), and it is a pure population trade-off.

The crux I named -- that peakedness would predict when the prior is wrong -- is measured at AUC 0.4033, below chance. The info-free twin detector scores HIGHER than the real one.

New mechanism recorded: 95.65% of the channel's wrong picks are higher-frequency than truth, so channel and prior fail in the SAME direction. That is the correlated-error regime the landed reliability-gate HARD_FAIL says inverts the mechanism -- suspected in the brief, confirmed here by count.

REDIRECT: the missing organ is a subordinate-context detector, bottlenecked on channel quality. Fourth independent arrival at the same missing piece.

*Appended by the strategy session, which owns integration (board Q111). Solver text unchanged.*
