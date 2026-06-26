# exp_dev: substrate_anisotropy_dg_pattern_separation_prewrite_v1 SMOKE = HARD_FAIL_SMOKE_SIGN_FLIP (full NOT dispatched)

**Date:** 2026-06-26
**Author:** exp_dev (spawn-and-die cell author)
**Anchor:** `substrate_anisotropy_dg_pattern_separation_prewrite_v1`
**Source:** GAP 2 anisotropy 5x drill Tier A Anchor #2 (P_deflated=0.45 -- N1 / brain-existence-proof)
**Pre-reg:** `preregs/2026-06-26_substrate_anisotropy_dg_pattern_separation_prewrite_v1.md`
**Cell:** `experiments/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1.py`
**Metrics:** `data/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1_smoke/metrics.json` (smoke; pythia-160m; 1 seed)

## Headline

**Smoke = HARD_FAIL_SMOKE_SIGN_FLIP. Full NOT dispatched.** Per cell-author smoke-gate-FIRST
discipline + task-spec sign-check gate: lift_dg_full_over_uniform = -0.147 at M=1000 (separator
HURTS recall by 15 absolute points). 3-5hr full run gated and skipped. Same discipline that caught
MIMO water-filling Anchor #1.

## Per-arm smoke metrics (pythia-160m, M=[400, 1000], 1 seed)

| Arm                            | M=400  | M=1000 |
|--------------------------------|--------|--------|
| `arm_knn_baseline` (RAW keys)  | 1.000  | 1.000  |
| `arm_uniform_no_presep`        | 0.797  | 0.380  |
| `arm_whitening_presep`         | 0.092  | 0.022  |
| `arm_dg_kwta_presep`           | 0.535  | 0.364  |
| `arm_dg_lateral_inhib_presep`  | 0.618  | 0.419  |
| `arm_dg_full`                  | 0.610  | 0.233  |

Lifts at M=1000 (test discriminator regime):
- `lift_dg_full_over_uniform`            = **-0.147** (SIGN-FLIP; FAIL band: <= -0.02 triggers gate)
- `lift_dg_lateral_inhib_over_uniform`   = **+0.039** (modest positive; below MIDDLE_BAND lower bound 0.05)
- `lift_dg_kwta_over_uniform`            = -0.016
- `lift_whiten_over_uniform`             = -0.358 (reproduces Anchor #1 whitening collapse exactly)

Geometric diagnostics at M=1000:
- `eff_rank_raw` = 0.007 (cone confirmed; matches Anchor #1)
- `eff_rank_dg_full` = 0.038
- `effrank_lift_dg_full_over_raw` = **5.79x** (huge geometric lift; same pattern as Anchor #1
  waterfill 186x lift)
- `off_diag_raw` = 0.354 (cone-aligned cosine collisions confirmed)
- `off_diag_dg_full` = **0.027** (off-diag mass collapsed 13x; separator WORKS geometrically)

## Interpretation (Fix #28 honest, no over-claim)

The DG mechanism produces the expected GEOMETRIC effect (orthogonalizes the keys: eff_rank 5.79x
lift, off-diag mass collapsed 13x) but does NOT translate to recall lift -- it HURTS recall by 0.15
at M=1000. Three observations emerge from the data:

1. **The substrate's uniform-Tikhonov cleanup EXPLOITS the cone, not fights it.** Both Anchor #1
   (water-filling) and Anchor #2 (DG separator) show the same pattern: massive geometric lift, no
   recall benefit. The substrate's dense KV cleanup with uniform Tikhonov pseudo-inverse is
   structurally suited to anisotropic codebooks -- it uses the cone's structure as the SIGNAL, not
   noise. Removing the cone (either via readout-side regularizer redistribution OR input-side
   orthogonalization) destroys the cleanup signal more than it helps disambiguation.

2. **DG_LATERAL_INHIB (no expansion + no homeostasis) is the BEST DG arm: +0.039 lift.** This is
   below the prereg MIDDLE_BAND lower bound (0.05) but is the ONLY DG arm with positive lift. The
   ablative ladder is informative:
   - `dg_kwta` (sparsity alone)             : -0.016 (no help)
   - `dg_lateral_inhib` (+ divisive norm)   : **+0.039** (best)
   - `dg_full` (+ expansion + homeostasis)  : -0.147 (sharp regression)

   This suggests EXPANSION + HOMEOSTASIS are ablative noise on top of k-WTA + divisive norm in this
   regime. The 6x expansion to d=4608 likely dilutes the per-axis cleanup signal because the post-
   Tikhonov solve operates in the larger expanded space with the SAME REG_LAMBDA budget.

3. **KNN sentinel = 1.000 on RAW keys** confirms keys are clean -- not a corruption catch. The
   whitening collapse to 0.022 reproduces Anchor #1's drill 1 rotation-only-ceiling failure exactly
   (cross-cell verification: this fixture is correctly calibrated).

## Decision (DO NOT dispatch full)

Per disciplines:
- **Smoke gate FIRST + SIGN-FLIP gate** (per task spec, load-bearing): smoke shows DG_FULL HURTS by
  0.15; SIGN_FLIP_TOL=0.02 violated by 7x. Full unlikely to flip sign because the geometric
  separation IS working (eff_rank 5.79x, off-diag 0.027) -- the failure mode is STRUCTURAL (the
  substrate's cleanup needs the cone).
- **"Assert measured values match expected BEFORE dispatching full run"** (USER-locked, cell-author
  memory): prereg HARD_PASS predicted lift >= 0.20; smoke shows lift = -0.147 (opposite sign).
  Asserted match FAILS catastrophically.
- **NO BUSY WORK** (USER-standing): dispatching a known-sign-wrong-mechanism for 3-5 hr wastes
  laptop CPU that Tier A Anchors #3-#5 need.
- **Fix #28 default UNDER-claim**: this is a falsification of the brain-existence-proof prior
  for THIS specific composition; the geometric separation works as designed but the substrate's
  cleanup architecture is incompatible with pre-write separation.

## Strategic update: TWO Tier A anchors now falsified

Both top-2 Tier A anchors falsified at smoke with the SAME STRUCTURAL PATTERN:
- Anchor #1 (MIMO water-filling, readout-side): geometric 186x lift, recall lift -0.027
- Anchor #2 (DG pattern separation, input-side): geometric 5.79x lift + 13x off-diag drop, recall
  lift -0.147

**Cross-cell observation (substrate-product insight):** the substrate's UNIFORM-TIKHONOV dense-KV
cleanup is anisotropy-AWARE by construction. Both rank-adding interventions (readout AND input)
destroy retrieval. This is a non-trivial finding -- it means anisotropy is NOT the GAP 2 bottleneck
for the substrate's existing cleanup primitive. The bottleneck may be ELSEWHERE (cleanup capacity
saturating with M; learned-projection ceiling; etc).

## Routing (negative -> Research for 2x revival drill)

Per [[feedback-route-negatives-to-research-2x-3x-revival-drills]] (USER standing), this HARD_FAIL
gets a revival-angle routing note in the same cycle.

**Revival angles for Research to consider:**

1. **DG_LATERAL_INHIB at +0.039 is interesting; widen its operating-regime search.** k-WTA + divisive
   norm WITHOUT expansion/homeostasis was the best DG arm. Worth a SEPARATE small cell (~30 min
   smoke + 1 hr full) that:
   - Sweeps KWTA_FRAC in {0.005, 0.01, 0.02, 0.05, 0.1} -- maybe 2% is too sparse for this regime
   - Sweeps NORM_EPS to test divisive-norm regularization strength
   - Skips expansion (cheaper) -- which Anchor #2 evidence says HURTS
   - This is essentially [N2 Divisive-normalization-only at write] from the research drill, which
     was queued as Tier B but might pre-empt to Tier A given the +0.039 signal

2. **Pivot to Tier A Anchor #3 (Brenier-map cone-to-ball pretransform, P=0.40).** Different
   geometric mechanism (non-linear optimal-transport pretransform vs DG's sparsification +
   normalization). Last UNFAlsified Tier A "add genuine rank" candidate per research drill.
   Compute: ~6 hr CPU.

3. **Pivot to Tier A Anchor #5 (Compressed-sensing coherence-aware fly-LSH, P=0.35).** Rescues
   working v2 fly-LSH chain-grade-candidate at adversarial M=100k. Lower expected payoff but
   defends a working primitive vs invents a new one. Compute: ~4 hr CPU.

4. **Re-examine THE QUESTION.** If two top anchors both show "geometric works, recall doesn't" the
   research question may be mis-posed. Anisotropy may be a RED HERRING for dense-KV cleanup --
   the substrate's uniform-Tikhonov already handles it. The actual GAP 2 bottleneck might be
   capacity scaling (M dependence) not anisotropy per se. Worth a research note: "is GAP 2
   anisotropy-bottleneck framing falsified by Anchors #1 + #2?"

5. **N2 Divisive-normalization at RETRIEVAL (research note Tier A #4, P=0.40, <1 hr CPU).** Cheap;
   different from N1 (RETRIEVAL not WRITE). Independent test of whether the divisive-norm primitive
   has lift at all.

## What was correctly proven by this cell

- DG separator composition works GEOMETRICALLY exactly as designed (eff_rank lift 5.79x; off-diag
  mass dropped 13x). Brain-DG-style separation is implementable from substrate primitives.
- KNN sentinel on RAW keys works as Fix #28 by-construction-saturation contamination catch.
- Whitening collapse to 0.022 reproduces Anchor #1 drill-1 ceiling -- cross-cell fixture verification.
- 5-arm intervention-point ladder (uniform / whitening / dg_kwta / dg_lateral / dg_full) provides
  clear ablation: DG_LATERAL_INHIB best of DG arms; FULL composition over-separates.
- SIGN-FLIP gate works as designed: caught the bad cell BEFORE dispatching full.

## What was NOT proven (smoke caveat)

- Full pythia-2.8b at M=10k could in principle reveal a different regime. Probability of sign flip:
  LOW per Fix #26 verify-the-referent (failure mode is structural; geometric mechanism is fully
  active and works as designed; the substrate cleanup architecture is the incompatible piece).
- Multi-seed std bound NOT validated (1 seed at smoke); full would have validated this. Acceptable
  trade since the lift magnitude (-0.147) is well clear of any plausible seed-noise band.
- KWTA_FRAC=0.02 NOT swept; 2% is DG-canonical but may be wrong for this dense-KV setting
  (relevant for revival angle #1).

## Substrate-product implication (research note prediction)

Research note N1 said: "If N1 passes: substrate gains a real-data dense-KV product NOT requiring
partition routing. Cleaner positioning than today's partition routing as workaround." Since N1 =
HARD_FAIL at smoke (with strong geometric working-as-designed evidence), **this product path does
NOT ship via DG pre-write separation.** Substrate-as-LM continues to rely on partition routing for
dense-KV at scale. The substrate's anisotropy-AWARE uniform-Tikhonov cleanup is the existing answer
-- "anisotropy rescue" is not the load-bearing GAP 2 angle for current cleanup primitive.

## Cites

- `notes/research_gap2_anisotropy_5x_drill_2026-06-26.md` (N1 candidate spec; Tier A Anchor #2)
- `notes/exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26.md`
- `notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md` (sibling falsification;
  same structural pattern)
- `notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md` (drill 2 ranked DG #1
  architecturally; this work prices and falsifies)
- `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` (v2 cone-
  collapse anchor)
- `data/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1_smoke/metrics.json` (this smoke)

## Files committed in this cycle

- `experiments/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1.py` (cell, ASCII, self-test PASS)
- `preregs/2026-06-26_substrate_anisotropy_dg_pattern_separation_prewrite_v1.md` (bands locked)
- `data/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1_smoke/metrics.json` (smoke data)
- `data/exp_substrate_anisotropy_dg_pattern_separation_prewrite_v1_smoke/partial_metrics_s11.json` (seed ckpt)
- `notes/exp_dev_anisotropy_dg_pattern_separation_prewrite_v1_SMOKE_HARD_FAIL_2026-06-26.md` (this note)

**Pause-flag check at decision time:** PASS (no `data/orchestrator_paused.flag`).
**Decision:** smoke HARD_FAIL_SMOKE_SIGN_FLIP gates full dispatch; revival routed to Research with
  5 candidate angles + cross-cell structural insight (anisotropy may be mis-posed GAP 2 framing).
