# ITEM 2 -- verb target-space re-measurement at n=222 (2026-08-17)

**Cell:** `experiments/exp_verb_target_space_n222_v1.py`
**Metrics:** `data/exp_verb_target_space_n222_v1/metrics.json` (run_mode=full, N_PERM=2000,
N_BOOT=10000, elapsed 652.8s)
**Prereg:** `notes/PLAN_NEXT_24H.md` section 4 ITEM 2 + section 0 RETRACTION 2 (thresholds fixed
there before this script was written; no separate `preregs/*.md` file -- this is a measurement of
an existing target space, not a new channel).

**THIS MEASURES THE INSTRUMENT, NOT A CAPABILITY.** K1_OWN_NORMS is the known-answer arm: both
words of every SimLex pair keep their real 12-dim grounding-norms code. No bridging, no held-out
endpoint, no new target-space channel was built.

## Prior-work check (substrate-KB concept-query, before authoring)

`bash tools/substrate_query.sh` was run first and **failed**: `PermissionError: [WinError 32] ...
E_unit_fp16.npy.tmp.npy -> E_unit_fp16.npy` inside `hdlab/director_kb_query.py` -- the KB's ingest
cache is mid-write/locked, consistent with `MEMORY.md`'s standing note that
`director_kb_query.py`'s ingest is livelocked and its results are STALE. The tool did not return
"no hits"; it errored. Proceeding was reasonable here because the plan itself already named the
two pieces of prior art to reuse verbatim (`experiments/exp_thematic_relation_supply_bridged_
grounding_v2.py` and `experiments/exp_selectional_constraint_bridge_v1.py`), and this script
imports their scorer/floor-battery functions as libraries rather than re-deriving them --
**Prior-work check: substrate_query tool ERRORED (known-stale KB); direct read of the two named
sibling cells substituted, and their code is imported (not reimplemented) here.**

## Population recount (measured, not assumed)

`data/encoder_eval_benchmarks/simlex999.txt`: **N=666, V=222, A=111, total=999.** Matches the
plan's stated expectation exactly.

## The F_CONSTANT_PROTOTYPE generalisation (OURS, stated)

The two sibling bridging cells replace the *bridged* endpoint's code with the mean CORE direction
while the other endpoint stays real -- an asymmetry that only exists because bridging holds one
endpoint out. K1_OWN_NORMS has no held-out role, so that construction does not type-check as-is.
Two variants were computed per stratum: (a) both endpoints replaced by the same constant --
cosine is then identically 1.0 for every pair, so Spearman is undefined (confirmed: `INS._spearman`
returns `nan`, reported as `null`, never used as the floor); (b) ONE endpoint replaced, scored
under both column orderings, the stronger (harder-to-beat) ordering reported as the floor. This is
a generalisation, not an import of the sibling cells' number or exact construction.

## Arm-by-arm margins, CI half-widths, and scramble p95 -- per stratum, never crossed

All bands are the **paired-bootstrap CI-separation** test over the STRONGEST of the four floors
(`FT.boot_rho_diff`, N_BOOT=10000, paired over the SAME items), which is the plan's stated bar.

### V (verbs), n=222 -- THE STRATUM THAT SETTLES RETRACTION 2

- K1_OWN_NORMS rho = **0.2607** [0.1282, 0.3841] (bootstrap CI half-width 0.128; analytic
  1.96/sqrt(n-3) approx = **0.1324**, close agreement).
- Floors: F_ORTHOGRAPHIC 0.0183, F_FREQUENCY_HARDENED 0.0341, F_CONSTANT_PROTOTYPE 0.0536,
  **F_SCRAMBLE_PERM_P95 0.1152** (strongest).
- **Null width orientation (1.645/sqrt(221)) = 0.1107; measured scramble p95 = 0.1152** -- these
  closely agree (ratio 1.04), unlike the n=86 measurement where the floor WAS the null's own width
  (0.1784 predicted vs 0.1776-0.1814 measured, ratio ~1.0 but at a much wider absolute value). The
  null construction is behaving exactly as predicted at n=222: it genuinely tightened.
- Margin over strongest floor (K1 - F_SCRAMBLE_PERM_P95) = **+0.1452 [-0.0496, +0.3379],
  NOT_SEPARATED.**
- Per-floor margins, all CI-separated ABOVE except the scramble: vs F_ORTHOGRAPHIC +0.2424
  [0.0426, 0.4287] ABOVE; vs F_FREQUENCY_HARDENED +0.2266 [0.0484, 0.4059] ABOVE; vs
  F_CONSTANT_PROTOTYPE +0.2070 [0.0496, 0.3590] ABOVE; vs F_SCRAMBLE_PERM_P95 +0.1452
  [-0.0496, +0.3379] NOT_SEPARATED (this is the binding one, being the strongest floor).
- **Row-permutation p-value = 0.000999** (K1's raw rho of 0.2607 sits far into the tail of 2000
  scrambled-code draws, mean 0.0014, sd 0.0666) -- a single-sample significance test says the
  effect is real. The PAIRED bootstrap on the margin says the CI still crosses zero. These are two
  different statistical constructs and both are reported rather than picking the flattering one.

### N (nouns, contrast stratum, own floors), n=666

- K1_OWN_NORMS rho = 0.2745 [0.1996, 0.3475] (CI half-width 0.074; analytic approx 0.0761).
- Strongest floor F_SCRAMBLE_PERM_P95 = 0.0680 (null width orientation 0.0638, ratio 1.07).
- Margin = **+0.2065 [+0.1015, +0.3102], ABOVE, CI-separated over all four floors.**
- F_CONSTANT_PROTOTYPE = **-0.1247** here -- a second, independent reproduction (different cell,
  different construction) of retraction 3's finding that the constant/prototype floor can be
  CI-separated BELOW zero on a pair-correlation instrument, never imported as a number, consistent
  in direction only.
- **Not compared directly to V's margin** (standing rule: never cross populations).

### A (adjectives, contrast stratum, own floors), n=111

- K1_OWN_NORMS rho = 0.1472 [-0.0447, 0.3300] (CI half-width 0.187; analytic approx 0.1886).
- Strongest floor F_SCRAMBLE_PERM_P95 = 0.1546 (null width orientation 0.1568, ratio 0.986,
  again close agreement -- K1's raw rho does not even clear the floor's own point estimate here).
- Margin = **-0.0074 [-0.2666, +0.2479], NOT_SEPARATED.** Permutation p=0.0605 -- not significant
  even at the single-sample level, unlike verbs.

## Which stop-if fired

**STOP-IF (ii): K1 does not clear at n=222, and the null width has fallen to ~0.11 as predicted.**
Measured V scramble p95 (0.1152) matches the analytic orientation (0.1107) closely -- this is NOT
a repeat of the n=86 failure mode where the floor WAS the null's own undifferentiated width; the
null construction genuinely tightened with n. Stop-if (iii) ("scramble p95 still same order as the
margin" / power insufficient at every n) does **not** fire: the null moved exactly as the plan's
own orientation formula predicted, so this is not a broken-null situation.

**Retraction 2 does not close in the "CONFIRMED" direction.** K1_OWN_NORMS does not clear the
CI-separated bar at n=222 (band NOT_SEPARATED, margin +0.145 with a CI that crosses zero,
[-0.050, +0.338]), even though its point estimate is ~2x the strongest floor and a row-permutation
test rejects the null at p=0.001. **Retraction 2 closes in the "MEASURED rather than asserted"
direction**: the claim "the 12-dim space cannot resolve verbs even handed the known answer" is no
longer an artifact of an underpowered n (as it was at n=86, where no arm of any quality could ever
separate); it is now a real, CI-honest negative at n=222, sitting close to significance under a
weaker (unpaired) test. Per the plan's own wording for this branch, **a channel build is now
licensed** -- but only after asking the brain-framed question first ("which experiential block is
missing?"), and any future channel-build cell must cite this measurement, not the retired n=86 one.

## Tooling note

`tools/verdict_bar_check.py --cell data/exp_verb_target_space_n222_v1/metrics.json` returns
`bar_status: NO_EVIDENCE` / `disagreement_class: AGREES` -- it does not recognise this cell's
flattened `pos_strata.<TAG>` schema as containing a known-answer arm (`has_known_answer_arm:
false`), so it produced no usable verdict. Per standing instruction, its verdict was not relied
upon; the arm-by-arm margins above were read directly from `metrics.json` and are the basis for
every claim in this note.
