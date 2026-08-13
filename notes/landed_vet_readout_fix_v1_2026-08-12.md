# LANDED-VET -- exp_readout_fix_v1 (9979af09e, 31e9946cd). Auditor: hdi_skunkworks, AUDIT-ONLY. 2026-08-12

## VERDICT: **OVERSTATED**. F3 CONFIRMED (and stronger than claimed). **F2's load-bearing claim is REFUTED** by the retention-matched arm the cell itself disclosed as not-run. F1's refutation as an informativeness gate is CONFIRMED; F1's z-statistic is worth MORE than the cell credited it.

Method: full independent recompute from `data/exp_context_vector_signal_v1/_pass_cache.npz`, own
scoring/standardization/flip/gating code (upstream `load_pass_cache`, `build_arm_contexts`,
`_eligible_anchor_view` reused as data construction only; the external anchor is upstream's
published flip 0.782962, reproduced). `.venv` Python, `OMP_NUM_THREADS=1`. No verdict-report number
was taken on trust. Scratch under system temp; nothing written outside this file.

## 1. Reproduction: every headline number reproduces to 6 decimals

| quantity | note/metrics | my recompute |
|---|---|---|
| FIXED BASE flip_all / retention / flip_gated | 0.782962 / 0.416687 / 0.501838 | **identical** |
| FIXED F1 / F2 / F1F2 flip_gated | 0.451967 / 0.372902 / 0.368545 | **identical** |
| FIXED LOO remove-F1 / remove-F2 | +0.004357 / +0.083422 | **identical** |
| GROWING BASE..ALL flip_gated (8 conds) | 0.682211 ... 0.391679 | **all 8 identical** |
| GROWING LOO F1 / F2 / F3 | -0.014846 / +0.077552 / +0.165034 | **identical** |
| F1 AUC z_top / margin / legacy cos (SEL half) | 0.506683 / 0.499204 / 0.500704 | **identical** |
| null admission at matched retention | 0.419343 vs real 0.419464 | **identical** (1.0000x) |
| F2 calibration arm delta mu / sd | 0.003931 / 0.005746 | **identical** |
| R-CTRL FIXED | 0.820643 @ ret 0.332891 | **identical** |
| foundation snapshot rows | 2092 | `wc -l` = 2092 |

Arithmetic of the attribution is also internally consistent: every LOO delta is exactly
`flip_gated(bundle minus fix) - flip_gated(bundle)`. Cardinality 24/24, F3 not run in FIXED,
`f1_gate_moved_an_argmax = []`, 0 unmapped anchors in either GROWING assignment, encounters verified
contiguous-by-lemma (4467 runs = 4467 lemmas), so the adjacency convention is sound.

**Nothing in the cell is miscomputed. The defect is entirely in what the comparisons control for.**

## 2. THE ARM THAT WAS NOT RUN -- and it overturns F2

The cell removed "gated flip < ungated flip" as non-failable (prereg sec 8 band #3) and replaced it
with R-CTRL. **R-CTRL is the wrong null.** It asks "is a RANDOM subset of this size stable?" (no:
0.82). It does not ask "is a subset of this size selected by ANY score-ranked criterion on the SAME
field stable?" Every LOO comparison in the attribution table -- "the point of the cell" -- compares
two conditions at DIFFERENT retentions (FIXED: F1 @0.4195 vs bundle @0.3329; GROWING: F1F3 @0.4097
vs ALL @0.3236). The removed non-failable band was thus re-admitted, unlabelled, at the attribution
level. I ran the missing arms.

**FIXED, all at retention ~0.333 (BASE is 0.5018 @ 0.4167):**

| selector at matched retention | flip_gated | increment |
|---|---|---|
| legacy raw-cos, threshold raised to ret 0.330 | **0.420550** | retention alone: **-0.081** |
| F1 z-gate at ret 0.3333 | **0.372881** | z over cos: **-0.048** |
| F1+F2 bundle at ret 0.3329 | 0.368545 | **F2 over z: -0.004** |
| R-CTRL random at ret 0.3329 | 0.820643 | (bounds nothing above) |

**GROWING, at retention ~0.324-0.333 (BASE is 0.6822 @ 0.4448):**

| selector at matched retention | flip_gated |
|---|---|
| legacy raw-cos raised to ret 0.3236 | 0.609626 |
| F1F2 field (no F3), z-gate to ret 0.3248 | 0.528178 |
| **F1F3 field (no F2), z-gate to ret 0.3331** | **0.360176** |
| ALL (with F2) @ ret 0.3236 | 0.391679 |

**Consequences.**
* **F2 is NOT load-bearing.** Its credited `+0.0834` (FIXED) / `+0.0776` (GROWING) LOO degradation is
  a retention artifact. At matched retention F2 buys **-0.004** in FIXED and **+0.032 (it HURTS)** in
  GROWING. The best configuration measured anywhere in this cell is F1+F3 with the gate tightened --
  0.3602, beating the note's headline F2F3 = 0.3768, **with F2 off**. F2 fails its own
  LOAD_BEARING band (>= 0.05) once the confound is removed.
* **F1's z-statistic is worth more than credited.** At equal retention z beats raw cosine by -0.048.
  F1 was filed NOT_JUSTIFIED only because its LOO was also computed at unmatched retention. F1 is a
  real STABILITY selector; its refutation as a LEMMA-SPECIFICITY gate (AUC 0.5067, enrichment
  1.0000x) is independently confirmed and is the cell's most durable result.
* **The primary drop is 61% retention.** FIXED BASE->bundle -0.1333 decomposes as -0.081 retention /
  -0.048 z-statistic / -0.004 F2. R-CTRL's +0.32 margin does not license reading -0.1333 as "the
  read-out was fixed".

## 3. F3 survives every control I could construct -- CONFIRMED

* Matched retention: with-F3 0.3602 vs without-F3 0.5282 at ret ~0.333 -> **-0.168**.
* Retention pushed ABOVE baseline: F3-only gated to ret 0.4575 (vs BASE 0.4448) still gives
  **0.544959** vs BASE 0.682211 -> **-0.137 while retaining MORE encounters**. No gate can do this.
* F3 moves `flip_all` (0.856881 -> 0.796592, -0.0603) -- a selection effect provably cannot.
* **Field-size confound (not disclosed, tested here):** the episode-freeze field is smaller (mean
  734.0 vs 783.5 eligible anchors; 2173/8282 rows shrink), so "fewer candidates" could mimic
  freezing. Control: each encounter scored against its OWN segment field randomly subsampled to its
  epi-field size -> flip_all 0.880734, flip_gated 0.720188, i.e. **WORSE than BASE**. F3's gain is
  the field being STILL, not the field being SMALL.

## 4. The four self-disclosed unverified items -- adjudicated

1. **No quality evidence.** Correct, and it blocks every meaning claim. It does NOT block wiring a
   default-OFF stability knob. The specific worry ("always picking `also` would score well") is
   empirically defeated as a mechanism: retained-argmax share of the top-10 background hubs falls
   **0.0739 (BASE) -> 0.0000 (bundle)**; BASE's modal retained winner is `people` (113 hits) and it
   disappears under calibration; top1_share 0.0149 -> 0.0086; n_distinct 884. The stable subset is
   not the function-word backbone. It is still not shown to be RIGHT.
2. **F2 retention confound.** **BLOCKING, and now fatal** (sec 2). This is the one that blocks WIRE.
3. **F3 at 5-snapshot, not per-episode freeze.** Does not block the FINDING (sec 3). It blocks the
   claim that `make_pbv_fns(freeze_episode=True)` delivers this in a live pass -- self-tested,
   never exercised. WIRE default-OFF with that caveat explicit.
4. **PBV never re-run.** Blocks only the 0.101 revival-gate claim, which the cell already demoted
   itself (`projection_calibrated=false`, baseline projects 0.4881 vs observed 0.1006). Honest.

## 5. Non-failable bands: 4 named ones ARE gone; a 5th was reintroduced

Removed as claimed and verified off disk: (1) F1 `flip_all` invariance -- inverted into the failable
positive `f1_gate_moved_an_argmax = []`, and my recompute confirms F1 flip_all is bit-equal to BASE
in both regimes; (2) FIXED F3 rows absent from `conditions` (24 units, not 32); (3) R-CTRL present
and firing; (4) every band names metric/direction/size/CI; (5) `verified_baseline_reproduces` is
block-only. The C1/C2/C3/C4 amendments are disclosed with unamended outcomes preserved
(`prereg_literal_degenerate_collapse = []`, `prereg_literal_arms_differ_all_distinct = false`), the
collapse guard is not at the floor, and the confirm-rate calibration gate FIRED and demoted its own
results -- a can-fail gate that actually failed.
**But** the retention confound removed from the headline (band #3) reappears inside every
leave-one-out delta. The LOO table passes by construction in the direction of whichever arm retains
fewer encounters. That is the fifth non-failable band, and it is the one that decided the verdict.

## 6. The two warts

* **341 vs 2092.** `check_backward_compat` reads the correct path and counts JSON-parseable
  non-blank lines; metrics said 2092 and `wc -l` says 2092. No foundation snapshot in the repo has
  341 rows and "341" appears in metrics only as a float substring. So 341 was a narrative figure
  that reproduced from nothing, self-caught and corrected in 31e9946cd. **No deeper bookkeeping
  trouble** -- the gate was never wrong -- but it is a live instance of the cited-number discipline
  and the note's numbers earned their re-derivation.
* **`attribution.F1/F2.leave_one_out_GROWING` holds FIXED values.** Confirmed: both equal
  `deltas["FIXED|LOO_drop_*"]` exactly; only F3's is genuinely GROWING. The sibling
  `regime_for_attribution` disambiguates and the note quotes both regimes correctly, so nothing
  downstream is currently wrong. It is a mislabel, not a mis-value -- but any consumer keying on the
  name misattributes regime, so fix the key before anything reads this file programmatically.

## 7. Disposition

* **F3 (`ConceptSpace.freeze` / `FrozenAnchorSpace`): PASSES VET.** WIRE, default OFF, caveat that
  the per-episode freeze path is self-tested but not exercised in a live reading pass.
* **F2 (`anchor_center`/`anchor_scale`): DOES NOT PASS VET. SHELVE.** Revival criterion: a
  retention-matched F2 arm (same field, gate tightened to the F2 arm's retention) showing >= 0.05
  residual with a paired CI excluding 0. Current measurement: -0.004 (FIXED), +0.032 (GROWING).
* **F1: keep as an explicit STABILITY selector at a chosen operating point** (worth -0.048 at
  matched retention), NOT as an informativeness gate. The blindness refutation is chain-grade.
* **Scope licensed:** read-out ARGMAX STABILITY only, on arm-A's 8282 cached encounters, 4467
  lemmas, 898 eligible anchors, d=256, one deterministic pass, no seed axis, 5-snapshot freeze
  granularity. NOT licensed: any statement about grounding quality/correctness, any claim against
  the PBV 0.101 revival gate, any claim that the GROWING headline 0.6822 -> 0.3768 reflects three
  working fixes -- it reflects one (F3), plus a tighter operating point.
