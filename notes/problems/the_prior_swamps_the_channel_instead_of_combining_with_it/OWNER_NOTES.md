---
owner_verdict: DONE
---

SUBMISSION — problem: the_prior_swamps_the_channel_instead_of_combining_with_it (priority 1)
status: REFUTED (first-class — a well-characterised negative that names the missing organ)

WHAT WAS ASKED
Our reader picks a word's meaning from two clues: how common each meaning is (a strong prior) and
what the surrounding words suggest (a weaker grounded channel). On words whose intended meaning is
the RARE one, the common-meaning prior is guaranteed wrong, and our fixed-weight mixing rule lets it
drown out the correct grounded clue — the combined answer (0.1415) is worse than the grounded clue
alone (0.4811) or random (0.3854). The bar: on the subordinate-sense population, a combined arm must
BEAT BOTH single cues CI-separated (the hard half is beating the channel; zeroing the prior only
RECOVERS the channel and is NOT a pass) WITHOUT harming the dominant population (prior 0.5508), with
floors recomputed per population, info-free twin losing, and AUC reported separately from gate delta.

THE ANSWER — the mixing rule is a real defect, but it is NOT the bottleneck. The fix exists; the
missing piece is a detector we cannot build blind.
On the priority-1 submission's exact instrument (CHANNEL 0.4811 and the fixed-sum collapse 0.1415
reproduce the brief by construction), subject-weighted hit@1, 53 subordinate words, chance 0.3854:

  ceilings (all computed, not assumed):
    ORACLE_ROUTE (pick the better cue per item) ..... 0.4811  == channel EXACTLY (routing can't help:
                                                               the prior is wrong on 100% of these)
    monotone ORACLE_BLEND (prior may only HELP) ...... 0.4748  no headroom
    SIGNED oracle (prior weight free, incl. NEGATIVE)  0.7799  headroom EXISTS — only via suppression

  the winning mechanism (real neuroscience — reordered access, Duffy/Rayner 1988):
    SUPPRESS the dominant sense (negative prior weight). Fixed b=-1.5:
       subordinate 0.7673  vs channel 0.4811  = +0.2862 CI [+0.1761, +0.4025]  (BEATS the channel)
       dominant    0.3103  vs prior   0.5855  = -0.2752 CI [-0.3385, -0.2137]  (WRECKS dominant)
    It is a pure see-saw: suppression helps rare-meaning words by exactly what it costs common ones.

  every GOLD-BLIND arm fails to meet the bar:
    reliability-weighted (independent-channel HARD_PASS recipe, LOO) ... 0.0189
    conflict-shrink (best) ............................................ 0.3789
    inverse-variance from peakedness (the derived trap) ............... 0.1667
    fixed z-sum (= BAYES_HUB) ......................................... 0.1415
    gold-blind gated suppressor (params max overall accuracy) ......... 0.1588   all << 0.4811

WHY — no gold-blind detector of "this context wants the rare meaning" exists here
  AUC(channel-disfavours-MFS -> subordinate) .......... 0.5114  (a coin flip)
  AUC(peakedness -> prior-wrong) — the brief's CRUX ... 0.4033  (below 0.5: REFUTES the crux)
  AUC(channel-confidence -> channel-right) ............ 0.5396
  even a split-KNOWING best-case gate reaches only 0.5252 sub / 0.4026 dom (doesn't beat the channel,
  wrecks dominant), and its INFO-FREE TWIN detector scores 0.6572 sub — the real detector is no
  better than a random one, so it carries NO signal.
  The reason the detector is weak: on 95.65% of the 46 subordinate items the channel gets wrong, its
  wrong pick is a HIGHER-frequency sense than the truth (phi(prior-correct, channel-correct)=+0.057).
  The grounded channel is ITSELF frequency-biased, so its errors correlate with the prior's — the
  Ernst-Banks independent-noise premise is violated (this repo's correlated_error_v1 HARD_FAIL regime),
  and the "context disagrees with the common sense" trigger fires as often on dominant words the weak
  channel simply got wrong. Detector quality is bottlenecked on channel quality.

DIAGNOSIS: the mixing rule is not the lever. A suppression rule fixes the mixing; what's missing is a
subordinate-context DETECTOR, and that is bottlenecked on the grounded channel's own frequency bias.

DISK vs BRIEF: the brief's untested crux (peakedness predicts the prior's systematic error) is
REFUTED (AUC 0.40); the brief's "correlated-error regime" inference is CONFIRMED. Brief's dominant-
prior 0.5508 is the MICRO rate; subject-weighted (the bar's scorer) it is 0.5768. My own first pass
over-claimed "structurally unreachable" on the monotone blend oracle; the signed/suppression oracle
corrected it, and the writeup says so.

PROPOSED hdlab CHANGE (not landed — Q111): do NOT wire the fixed-weight z-sum as a sense-selection
rule (it destroys the channel); do NOT wire a monotone reliability-weighted variant (correlated cues,
can't beat the channel). A suppression term (negative prior weight on subordinate-biasing context) is
the mechanism that would work, but ONLY behind a subordinate-context detector — and no gold-blind
detector is accurate enough (AUC 0.51). Wiring order: FIRST build/learn a detector (equivalently, a
grounded cue whose errors are independent of frequency — the reader_meaning_channel problem); THEN a
suppression-gated combiner is admissible. Until then the honest read-out is the frequency prior alone
(MFS), which the aggregate already prefers.

WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST
Did NOT build a LEARNED detector — every route tested is gold-blind (as the bar requires), so "no
route solves it" is bounded to gold-blind routes; the 0.78 signed oracle says a SUPERVISED detector
is worth trying. Coverage is not random (53 of 77 subordinate words). Most-exposed claim: the 95.65%
correlated-error figure (n=46) — I withdraw it before the signed-oracle/suppression result, which is
arithmetic on the saved vectors.

NEXT STEP (for a new brief): NOT another "fix the mixing rule" brief — open a "build the detector"
brief, two admissible forms: (a) a LEARNED subordinate-context detector (train on the profile/other-
words split, apply held-out, info-free twin must still lose; ceiling = the 0.78 signed oracle); (b) a
grounded cue whose errors are INDEPENDENT of sense frequency = reader_meaning_channel from the other
side. Either unlocks the suppression combiner. This converges with reader_meaning_channel and
store_survives_a_partial_cue: three problems now point at one root — the grounded channel is too
frequency/co-occurrence-correlated to add independent signal.

FILES / REVERIFY
experiments/exp_reliability_weighted_cue_combination_subordinate_sense_v1.py   (main cell; smoke+full)
experiments/exp_reliability_weighted_cue_combination_signed_suppression_v1.py  (suppression/detector
   analysis; reads the saved population, writes only its own dir — does not re-run/re-date the cell)
verification/test_reliability_weighted_cue_combination_subordinate_sense.py    (scaffold-free witness)
notes/problems/the_prior_swamps_the_channel_instead_of_combining_with_it/SOLVED.md
reverify:  .venv/Scripts/python.exe verification/test_reliability_weighted_cue_combination_subordinate_sense.py
   (13/13 checks pass: reproduces the swamping, the routing/monotone/signed ceilings, the suppression
    win + its dominant cost, the correlated-error 95.65%, the crux AUC, and that the detector carries
    no signal. Reads only the saved population; no re-run. Ledger: malformed/incomplete: 0.)
