---
problem: the_gate_cannot_measure_its_own_floor
status: SOLVED
bar: "per_row_gain_c3_vet_v1.py measures its floor in its own harness, on its own items, against its own stripped gold, and gates on what it measures." (plus: a recompute-and-refuse guard; a positive control that makes the guard fire; an information-free twin of the trigram arm; the past results re-graded with both numbers side by side; CI half-width and null p95 beside every margin. "A clear, well-controlled failure is an explicit PASS for this brief.")
result: "The orthographic floor for the per_row_gain_c3_vet_v1 harness = A6_TRIGRAM_ONLY hit@1 = 0.0195, 95% CI [0.01525, 0.024] (half-width 0.004375), scorer = argmax-over-eligible-pool cosine on morphology-stripped WordNet gold, n_items=4000 / n_anchors=5491 -- measured IN that harness (A1_BASE 0.04575 and self_retrieval 0.755853 both reproduced to 1e-9), not imported."
floor: "A6_TRIGRAM_ONLY (character-trigram, pure orthographic form) = 0.0195, CI [0.01525, 0.024]. It is the strongest no-understanding floor on this task and it SEPARATES CI-cleanly from both of its own information-free twins (donor-query 0.008, null p95 0.01025; row-permuted 0.011, null p95 0.01375), so it is a real signal, not noise."
controls: "info-free twin #1 donor-query (query = a DIFFERENT word's spelling) 0.008 -- excludes 'the floor is target-form noise' (delta +0.0115, CI [+0.0063,+0.0168], excludes 0); info-free twin #2 row-permuted (candidate spellings shuffled across identities) 0.011 -- excludes the same from the other side (delta +0.0085, CI [+0.0030,+0.0140], excludes 0); known-answer self-retrieval 0.755853 (floor 0.70) -- excludes a broken scorer; guard positive control -- fires (void=True) on the leaky 0.0870 constant, passes (void=False) on the measured 0.0195, excluding a silently-drifted constant; harness-identity A1_BASE 0.04575 to 1e-9 -- excludes 'measured on a look-alike population'; leaky-floor negative control -- the read-out that clears the honest floor does NOT clear the leaky 0.096, so the re-grade flip is real."
files_changed: "experiments/exp_per_row_gain_trigram_floor_calibration_v1.py (new, measures), verification/test_the_gate_can_measure_its_own_floor.py (new, witness), data/exp_per_row_gain_trigram_floor_calibration_v1/metrics.json (new, landed numbers). PROPOSED-ONLY (not landed, out of solver scope): tools/per_row_gain_c3_vet_v1.py -- exact diff below."
reverify: ".venv/Scripts/python.exe verification/test_the_gate_can_measure_its_own_floor.py"
---

# The gate can now measure its own floor: 0.0195, and it is a real floor, not noise

## What was asked, in one line

`tools/per_row_gain_c3_vet_v1.py` grades against a "spell-checker" floor. The floor was 78%
morphological leakage; once the gold is cleaned the borrowed number is wrong, and the tool honestly
**refuses to grade** rather than gate against a number it cannot justify. It has no trigram arm of
its own, so it cannot re-measure the floor. Give it the ability to measure its own floor, prove the
guard, and re-grade the past results. **Do not paste the sibling tool's number across.**

## What I built

- **A calibration cell** ([experiments/exp_per_row_gain_trigram_floor_calibration_v1.py](../../../experiments/exp_per_row_gain_trigram_floor_calibration_v1.py))
  that measures the floor IN per_row_gain's own harness. It does not reconstruct the harness -- it
  imports the tool's own `_gold` and `build_excitability_E`, the same C3 corpus/space/items, the
  same `MS.trigram_matrix`, and the same bootstrap seed (`MASTER_SEED+51`). It then adds the
  `A6_TRIGRAM_ONLY` floor arm, two information-free twins of it, the recompute-and-refuse guard, and
  a leaky-vs-honest re-grade of every arm.
- **A scaffold-free witness** ([verification/test_the_gate_can_measure_its_own_floor.py](../../../verification/test_the_gate_can_measure_its_own_floor.py)),
  5/5 pass: the guard fires on the leaky / uncalibrated / drifted / broken-control cases and passes
  only when all agree; the sibling's `0.019500` never crossed into this harness; the form-route
  metric fails safe (a real query picks the target's form neighbour, its twin picks by the donor's);
  stripping the gold removes exactly the form-route win; and the landed headline reproduces from disk.

## What I measured (n=4000, per_row_gain's own population)

**The harness-identity check is the load-bearing part.** The brief's whole warning is that a number
right in one harness is wrong in another. I did not assume the two harnesses agree -- I proved it:
`A1_BASE = 0.04575` and `self_retrieval = 0.755853` both reproduce this harness to **1e-9**, and
`n_anchors=5491 / n_items=4000` are identical. Only *after* that identity holds is it legitimate that
the floor coincides with the sibling's value.

| quantity | value | CI | half-width |
|---|---|---|---|
| **A6_TRIGRAM_ONLY (THE FLOOR)** | **0.0195** | [0.01525, 0.024] | 0.004375 |
| A1_BASE (the real read-out, stripped gold) | 0.04575 | [0.0395, 0.05225] | 0.006375 |
| info-free twin: donor-query | 0.008 | [0.00525, 0.01075] | null p95 = 0.01025 |
| info-free twin: row-permuted | 0.011 | [0.008, 0.01425] | null p95 = 0.01375 |

**The floor is real, not noise.** Its lower CI bound (0.01525) sits above both twins' null p95, and
the paired deltas exclude zero: floor - donorq = **+0.0115, CI [+0.0063, +0.0168]**; floor - rowperm
= **+0.0085, CI [+0.0030, +0.0140]**. So `A6_TRIGRAM_ONLY` carries a small but genuine orthographic
signal above its own shuffled versions -- the residual form-similarity the (over-inclusive) strip
does not remove. **This is a usable floor: the gate CAN separate things at this level.**

## The re-grade: the honest floor FLIPS the verdict the leaky one gave

Both the arms and the floor were re-scored on morphology-stripped gold (they must move together --
scoring arms on fair gold against a leaky bar is a different wrong answer, not a half-fix).

| | leaky floor (old) | honest floor (new) |
|---|---|---|
| floor value | 0.0870, CI [0.0783, 0.096] (unstripped, ~78% leakage) | 0.0195, CI [0.01525, 0.024] (stripped) |
| A1_BASE read-out | 0.048 -> **appears to LOSE to spelling** (0.048 < 0.087) | 0.04575 -> **BEATS spelling, CI-separated** (ci_lo 0.0395 > 0.024) |
| every per-row-gain arm | did not clear (0.048 < 0.096) | clears the honest floor CI-separated |

**The single most consequential line:** for the whole thread the read-out "lost to a spell-checker"
(0.048 vs 0.087), and that steered the project. On clean gold it **wins** (0.04575 vs 0.0195,
CI-separated). The leaky floor was hiding a real -- if modest -- semantic result. *This direction was
already reported by the sibling harness (`exp_c3_surprise_weighted_vs_bundling_v1`, and the existing
witness `test_removing_the_bundle_helps...`); my contribution is confirming it in per_row_gain's own
harness with the floor measured here and the gate made honest.*

**And the mechanistic verdict the tool exists for is unchanged:** per-row multiplicative gain still
adds nothing. Five gain arms are bitwise identical to base (fraction 1.0), the two dim arms change
picks but not accuracy, and every delta-vs-base CI includes zero. The re-grade corrects the FLOOR
comparison; it does not resurrect the gain hypothesis. That distinction is why the proposed gate adds
a delta>0 requirement (below) so a no-op arm that merely inherits base's clearance is not misread as
a pass -- the exact sign bug the sibling tool hit under the fair bar.

## The guard, and its positive control (I made it fire)

`void_plumbing_check` recomputes the floor in-harness and refuses (`void=True`) unless the constant
matches to 1e-9, A1_BASE reproduces the stripped headline, and self-retrieval clears its floor. At
full power: **fires on the wrong constant 0.0870** (void=True), **passes on the measured 0.0195**
(void=False). A guard nobody has seen fire is untested; this one has been seen to fire.

## Brain structure: replicating vs substituting (asked in the brief, and by the owner)

Two things live in this task and they sit on opposite sides of the fidelity line -- and conflating
them would be inventing neuroscience for a spreadsheet, which the brief explicitly warns against.

- **The grading gate itself is bookkeeping, NOT a brain mechanism.** The brain does not gate its own
  read-outs against a bootstrapped orthographic null. Dressing this up as predictive-coding
  confidence or conflict monitoring would be a fabricated justification. So the *tool* is measurement
  hygiene, full stop. *OUR-INVENTION / not-a-brain-claim.*
- **But the dissociation it encodes is real, and that is where fidelity legitimately lives.** The
  trigram floor is a model of the **orthographic / visual-word-form route** (form, no meaning); the
  thing being graded is the **anterior-temporal-lobe semantic hub read-out** of a distributed,
  overlapping code. That is the dual-route model of reading, and surface/deep dyslexia dissociate
  exactly there. *Both routes PINNED; our particular VSA read-out of the semantic route is
  OUR-INVENTION-UNDER-TEST.* The morphology we strip (nation/national) is itself a brain fact --
  morphological decomposition in visual word recognition -- so a form route *should* win those
  without meaning, and stripping them is the correct way to isolate the semantic route from the
  morpho-orthographic one. *PINNED.*

So the honest, non-fabricated content is: **the ATL-hub semantic read-out (0.04575) now beats what
the pure orthographic route can do (0.0195), CI-separated** -- a real, if small, statement that our
distributed read-out is doing something form-matching cannot. It is not large (4.6% hit@1 is still a
poor reader), so read it as "beats spelling", not "reads well". The residual floor separating from
its twins says the form route still carries a little signal our strip does not kill -- worth keeping
as the null, not worth chasing.

## PROPOSED change to tools/per_row_gain_c3_vet_v1.py (NOT landed -- solver scope; strategy lands it)

Three hunks, each mirroring the already-landed sibling `score_space_gain_and_topk_ci_v1.py`:

**(1) Set the measured constant (currently `None`), replacing lines 73-74:**
```python
# MEASURED IN THIS HARNESS on stripped gold, 2026-08-24, n_items=4000 / n_anchors=5491, by
# experiments/exp_per_row_gain_trigram_floor_calibration_v1.py (reproduces THIS harness's A1_BASE
# 0.04575 and self_retrieval 0.755853 to 1e-9 -- the identity check that licenses the value here;
# it coincides with the sibling's 0.019500 because the population is provably the same, not pasted):
#   A6_TRIGRAM_ONLY = 0.019500  CI [0.015250, 0.024000]  (half-width 0.004375)
ORTHO_BAR = 0.019500
ORTHO_BAR_CI = (0.015250, 0.024000)
```

**(2) Add the `A6_TRIGRAM_ONLY` floor arm** (the tool already imports `MS`). Build the matrix once
before the scoring loop, and score it per item exactly as the sibling does:
```python
t_mat, t_cov = MS.trigram_matrix(anchors)          # pure orthographic form route == the floor
# ... add "A6_TRIGRAM_ONLY" to the scored arms; in the per-item loop:
tqL = t_mat[pos[L]] if t_cov[pos[L]] else None
sc  = t_mat[sel] @ tqL if tqL is not None else np.zeros(sel.size)
# argmax/hit recorded identically to A1_BASE; include A6_TRIGRAM_ONLY in the paired_bootstrap arms.
```
Keep it OUT of `gain_arms` (it is a floor, not a gain arm).

**(3) Replace the refusal block (lines 266-281) with a guarded gate:**
```python
measured_a6 = bs["arm_acc_ci"]["A6_TRIGRAM_ONLY"]["acc"]
a6_matches_bar     = abs(measured_a6 - ORTHO_BAR) < 1e-9
a1_matches_headline = (abs(bs["arm_acc_ci"]["A1_BASE"]["acc"] - 0.04575) < 1e-9) if not SMOKE else None
void_plumbing = bool((not SMOKE) and ((not a6_matches_bar) or (a1_matches_headline is False)
                                      or self_retrieval < SELF_RETRIEVAL_FLOOR))
if void_plumbing:
    print("[VOID_PLUMBING] measured A6=%.6f vs constant %.6f -- refuse to gate" % (measured_a6, ORTHO_BAR))
    return 3
bar_lo = ORTHO_BAR_CI[1]                            # gate on the floor's UPPER CI bound
clears_bar          = {a: bool(bs["arm_acc_ci"][a]["ci_lo"] > bar_lo) for a in gain_arms}
delta_is_improvement = {a: bool(bs["deltas"]["d_%s_minus_BASE" % a]["delta"] > 0.0) for a in gain_arms}
delta_excludes_zero  = {a: bool(bs["deltas"]["d_%s_minus_BASE" % a]["ci_excludes_zero"]) for a in gain_arms}
hard_pass = {a: bool(clears_bar[a] and delta_is_improvement[a] and delta_excludes_zero[a]) for a in gain_arms}
```
The `delta_is_improvement` term is the sign-bug guard the sibling added on 2026-08-24: without it, a
gain arm identical to base inherits base's clearance of the honest floor and reads as a pass. Under
this harness every gain arm is a no-op, so `hard_pass` is all-False -- correct.

## What I did NOT establish, and what I would withdraw first

- **I did not land the tool edit.** It is out of solver scope; the tool on disk still refuses until
  the strategy session applies the diff above. Everything it needs is measured and proven here.
- **"The honest floor is a real signal" depends on WHICH info-free twin.** Against MY twins
  (donor-query, row-permutation of the trigram arm) it separates CI-cleanly. The sibling cell's note
  reported the stripped string floor *overlapping* its twin -- but that comparison used a shuffled
  **co-occurrence** arm (0.0135-0.0213) as the null, not the trigram floor's own shuffle. Different
  null, different answer; both defensible. **If challenged, I withdraw "the floor carries real
  orthographic signal" first.** The twin-independent, rock-solid facts are (a) the 78% collapse
  0.087 -> 0.0195 and (b) the read-out clears the honest floor CI-separated.
- **"Re run the past results" -- scope.** The one recorded verdict that carried the leaky bar
  (`data/exp_per_row_gain_c3_vet_v1/metrics.json`, ts 2026-08-15, bar 0.087, all arms ~0.048 on
  unstripped gold, `clears_bar` all False) is re-graded here. I did not enumerate every downstream
  doc that quotes 0.048/0.087; `tools/cite_check.py 0.0870` would list them, and that sweep is the
  strategy session's to run when it lands the fix.
- **Absolute level.** 0.04575 hit@1 clears the floor but is a poor reader. Do not let "beats
  spelling" travel as "reads meaning well".

## TLDR (plain language)

We grade our system against a deliberately dumb "spell-checker" baseline. That baseline turned out
to be mostly cheating on words that are spelled alike, so one of our two graders honestly stopped
grading rather than use a number it knew was wrong. I measured the *fair* version of that baseline in
that grader's own test -- it is about 0.02 (a word is retrieved correctly ~2% of the time by spelling
alone), down from the inflated ~0.09 -- and I checked it is a real signal, not random noise. The
important consequence: our actual meaning-reader scores ~0.046, which **beats** the fair spelling
baseline (it did NOT beat the inflated one). The old inflated baseline had been telling us our reader
loses to a spell-checker; on a fair test it wins -- though it is still a weak reader in absolute
terms. I also built the safety check that refuses to grade if this number ever drifts, and showed it
actually fires. I could not edit the grader itself (that is the strategy session's job); the exact
change is written above.

## QUESTIONS

None. The one judgement call for the owner/strategy session is noted in NEXT STEPS, not blocking.

## NEXT STEPS

1. **Strategy session lands the three-hunk diff** into `tools/per_row_gain_c3_vet_v1.py`, re-runs it
   (~45 min full), and confirms `A6_TRIGRAM_ONLY` reads 0.0195 and the guard passes -- the witness's
   landed-headline test already asserts this from disk.
2. **Run `tools/cite_check.py 0.0870` and `cite_check.py 0.048`** to find every doc still quoting the
   leaky floor or the unstripped headline, and re-grade or annotate them.
3. **Judgement call (non-blocking):** the "floor separates from its twin" result is twin-dependent
   (see withdrawals). If the project wants one canonical info-free null for the string/trigram floor,
   the trigram arm's OWN shuffle (donor-query / row-permuted) is the faithful one; the shuffled
   co-occurrence arm answers a different question. Worth settling once, since both gates cite a floor.

## INTEGRATED_BY_STRATEGY -- 2026-08-24, re-verified and LANDED

**Re-verified: `verification/test_the_gate_can_measure_its_own_floor.py` passes 5/5, exit 0**,
including a check literally named `sibling_number_did_not_cross_harnesses`. Review: **EXCELLENT.**
The submission built a control for the exact trap the brief warned about, and named what it would
withdraw first -- the twin-dependence of "the floor is real signal" -- which is the rarest and most
useful thing a submission can do.

**ALL THREE PROPOSED HUNKS LANDED** in `tools/per_row_gain_c3_vet_v1.py`: the calibrated constant,
the `A6_TRIGRAM_ONLY` floor arm, and the `void_plumbing` recompute-and-refuse guard. **The tool
grades again.** Two additions beyond the diff, both from running it:

- **`hard_pass` was NOT in this tool at all** -- it reported `clears_bar` as its verdict. On the
  smoke, `clears_bar` reads **True for 6 of 7** gain arms **that are bitwise identical to A1_BASE**:
  a no-op inheriting base's clearance of the honest floor, exactly the sign bug the submission
  flagged. Landed `delta_is_improvement` + `delta_excludes_zero` + `hard_pass`, which reads **False
  for all 7** -- correct.
- **The `A1_BASE` identity check was abstaining.** It returned `None` under stripped gold because
  `0.048` was a leaky-gold number. With `0.04575` now measured in this harness there IS a value to
  check, and leaving it `None` would have left `void_plumbing` toothless in one of its three terms.

**🔻 A CORRECTION TO THE BRIEF I WROTE, WHICH THIS SUBMISSION DISPROVED.** The brief said the two
harnesses were "a different item construction and a different scorer", so pasting `0.019500` would
be a fabrication. **They are the SAME population** -- `n_items=4000 / n_anchors=5491` in both, which
I asserted without checking. The prescription was still right and the submission is why: measuring
in-harness turned my assumption into a *checked* fact, and the identity proof (`A1_BASE` and
`self_retrieval` to 1e-9) is what licenses the coincidence. It is now a free replication --
`0.019500`, `0.0195`, `0.0193` across three measurements -- rather than a number taken on trust.

➡️ **THE RESULT THAT MATTERS AND SHOULD TRAVEL: on the honest floor the read-out WINS
(`0.04575` vs `0.0195`); on the leaky floor it LOST (`0.048` vs `0.087`).** The inflated bar had
been telling the project our reader loses to a spell-checker. It does not. ⚠️ **And the submission's
own caveat travels with it: `0.04575` is still a weak reader in absolute terms. "Beats spelling"
must never travel as "reads meaning well".**

**STILL OPEN, from the submission's own scope note:** the downstream sweep for docs quoting
`0.048` / `0.0870` (`tools/cite_check.py 0.0870`) has NOT been run. That is mine, not the solver's.

*Appended by the strategy session, which owns integration (board Q111). Solver text unchanged.*
