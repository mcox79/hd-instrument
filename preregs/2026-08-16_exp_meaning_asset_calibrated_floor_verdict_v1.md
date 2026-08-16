# PRE-REGISTRATION -- meaning-asset floor calibration (three analysis cells)

Covers `exp_meaning_asset_hardened_margins_v2_complete`,
`exp_meaning_asset_permutation_null_v1`, `exp_meaning_asset_norms_coverage_scope_v1` and
`exp_meaning_asset_calibrated_floor_verdict_v1`.

Parent pre-reg: `preregs/exp_meaning_asset_fair_test_v1.md`. Its section 5 bands are INHERITED
UNCHANGED and are not edited here: CLEARS THE FLOOR = 95% CI of the paired-bootstrap difference
`arm - strongest_floor` entirely above 0 AND point margin >= 0.05; CI contains 0 = NOT ESTABLISHED;
CI entirely below 0 = BELOW. `T_MARGIN_MIN` stays 0.05. No threshold is changed by any cell here.

## 0. THESE ARE ANALYSIS CELLS, NOT NEW MEASUREMENTS

No arm is re-encoded. Every number is computed from per-pair cosines already written by
`exp_meaning_asset_fair_test_v1`, `..._v1b_distributional` and `..._power_extension_v2_paired`.
The single exception is `exp_meaning_asset_permutation_null_v1`, which rebuilds the 12-dimensional
norm table through its own live module in order to permute its ROWS, and which asserts in
self-test that the rebuilt table reproduces the landed rho to 1e-9 before permuting anything.

## 1. WHY THEY EXIST

`exp_meaning_asset_hardened_margins_v1` ran at 18:12 while the parent's `units.jsonl` was still
being written and covered 6 of 25 arms, omitting every arm that scored highest. Its verdict
(`NO_ASSET_CLEARS_THE_HARDENED_FLOOR`) is therefore an artefact of coverage and is superseded.

## 2. THE FLOOR-POLICY CHANGE, AND THE ORDER IN WHICH IT HAPPENED

**Disclosed plainly because the order matters and post-hoc method changes are how bars get
lowered.** I computed the complete table FIRST, using the parent's floor policy hardened to take
each seeded floor's STRONGEST of three seeds. `ASSET_NORMS12` came out NOT_SEPARATED against a
scramble floor of 0.1152. Only THEN did I look at the three scramble draws -- 0.0220, 0.0241,
0.1152 -- and recognise that a max-of-three is an n=3 estimate of a null's upper tail, not a
floor. So the calibration below was designed AFTER seeing a result it could have changed.

Two things constrain it against being a rescue:

1. It is pre-declared HERE, before the calibrated cell was run, that the scramble floor is the
   null's **95th percentile** -- a one-sided 5% floor that sits ABOVE the null's centre and above
   two of the three original draws. A mean-of-draws or a median policy would have been laxer and
   is not used.
2. **It did not rescue the arm.** The norms' margin on the instrument population is
   +0.1549 [-0.0071, +0.3101], NOT_SEPARATED under BOTH policies. The calibration changes the
   floor from 0.1152 to 0.0943 and the verdict not at all. Recorded here so the reader can check
   that claim rather than take it.

Where both the expensive row-permutation null and the cheap gold-permutation null exist, the
HIGHER p95 is used. The cheap estimator is asserted in self-test to agree with the expensive one
within 0.01, and the cell REFUSES TO RUN if it does not.

## 3. BANDS AND GATES, FIXED BEFORE THE CALIBRATED CELL RAN

- **HEADLINE (LITERAL, the standing rule):** paired bootstrap, 10,000 resamples, of
  `arm - max(A_ORTHOGRAPHIC, hardened seed-free frequency, SCRAMBLE_NULL_P95)` on the IDENTICAL
  scorer / n / pool / gold. Bands per the parent. This is the gated form.
- **DECOMPOSED (diagnostic, not gated):** an exact permutation p-value against the scramble null,
  plus a separate paired-bootstrap CI against orthographic and against frequency.
- **CONCRETENESS-CONTROLLED:** the same paired bootstrap on PARTIAL rho with both words' mean
  concreteness and their absolute difference regressed out of both rank vectors. Reported
  alongside, never instead of, the raw margin. An arm counts as clearing only if it clears BOTH.
- **TRAINED vs RANDOM-INIT:** paired bootstrap of the trained arm minus its untrained twin,
  same architecture, tokenizer and read-out.

## 4. POPULATIONS ARE NEVER MERGED AND NEVER AVERAGED

`INSTRUMENT_322` (the instrument's own covered SimLex pairs at V=4096) is the LIKE-FOR-LIKE number
and the only one that may be quoted as the instrument result. `SIMLEX999` and `WORDSIM353` come
from the power extension and are a DIFFERENT item population. IDENTITY and STRUCTURE are reported
as separate axes and are never averaged into a single score.

## 5. WHAT WOULD FALSIFY THE READING

If the norms' advantage is a concreteness confound, the concreteness-controlled partial margin
collapses toward zero and `CTRL_CONCRETENESS_ONLY` scores high. If the learned encoder's advantage
is an artefact of a lucky read-out, `CTRL_RANDINIT_*` ties it. If an arm's score is carried by
spelling, `A_ORTHOGRAPHIC` -- a FORM channel, never scored as meaning -- ties or beats it. All
three are live arms and any of them firing is a real result.
