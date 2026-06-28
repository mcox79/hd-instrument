# exp_dev: TOM recursive v2 reframed smoke HARD_FAIL_FLAT_DEPTH_PROFILE 2026-06-28

**Cell:** `substrate_higher_order_tom_recursive_v2_reframed`
**Prereg:** `preregs/2026-06-28_substrate_higher_order_tom_recursive_v2_reframed.md`
**Smoke metrics:** `data/exp_substrate_higher_order_tom_recursive_v2_reframed_smoke/metrics.json`
**Commit:** c9484c52
**Verdict:** HARD_FAIL on smoke (NO full dispatch issued per pre-reg STOP rule)

## Reframe vs v1

v1 MIDDLE_BAND flat-depth: d2=0.673, d3=0.633, d4=0.633, d5=0.580 across 3 seeds.
v2 reframe: INTERLEAVE N_chains concurrent TOM chains in single substrate state to force depth-dependent interference. NEW HARD_FAIL_FLAT_DEPTH_PROFILE diagnostic guard (variance(ARM_TOM across depths) < 0.05 for ALL (N, N_chains) -> HF).

## Smoke result (32-cell reduced grid; full N range; 20 trials/cell)

- verdict: HARD_FAIL_FLAT_DEPTH_PROFILE (max_depth_var=0.030 < 0.05 threshold)
- mb_cells=21/32 (TOM > FLAT + 0.30 in 21 cells; discrimination present)
- pos_control (N=8192, N_chains=1, d=1): ARM_TOM=0.75 (need >=0.95)
- ARM_RANDOM=0.20 (chance OK)

## Depth profile flatness (load-bearing data)

ARM_TOM at (N=16384, N_chains=1):
  d=1: 0.60 / d=3: 0.80 / d=6: 0.80 / d=10: 0.75 (variance ~0.007)

ARM_TOM at (N=2048, N_chains=10):
  d=1: 0.70 / d=3: 0.80 / d=6: 0.80 / d=10: 0.75 (variance ~0.002)

Substrate accuracy is anchored at ~0.70-0.80 regardless of regime. Depth and N_chains DO NOT move the needle.

## Honest diagnosis

Three candidates:
1. Per-level distractor noise dominates the cleanup-attractor signal even at d=1 (PER_LEVEL_DISTRACTORS=2 gives ~3x noise per level but the bind+unbind chain re-isolates the focal token via fortunate FHRR phase alignment).
2. Cleanup attractor at 4 locations has a ~0.75 ceiling under any superposition noise (only 4 candidates -> winner-take-all guesses 1-of-4 with ~25% bias from a single noise sample = floor 0.25; observed 0.75 = high-confidence ceiling).
3. N_TRIALS=20 sampling resolution rounds out smaller depth-dependent effects (variance 0.03 ≈ 1 trial difference).

Most likely: combination of (2) + (3). The 4-location cleanup floor is saturating; any noise above SNR threshold gives ~0.75 not 1.0; below it gives chance 0.25; no graceful in-between.

## Per pre-reg STOP rule

"If smoke MIDDLE_BAND or HARD_FAIL_FLAT_DEPTH_PROFILE: report + STOP (no full dispatch)."

No seeds dispatched. Pre-reg discipline honored.

## What this means for Stage 3 TOM higher-order

The substrate-as-tested at 4 locations and N up to 16384 cannot discriminate recursive depth — neither v1 nor v2 reframe surfaced depth-cliff. Conclusion:

**For Stage 3 TOM, both v1 (per-trial-independent) and v2 (interleaved) test designs are CAPACITY-FLOOR-LIMITED, not depth-limited.**

To actually characterize higher-order TOM as a function of recursion depth, the test design needs:
- larger N_LOCATIONS (16, 64) to spread the cleanup floor across more candidates
- per-level distractors scaling with depth (PER_LEVEL_DISTRACTORS = depth * k)
- OR a fundamentally different encoding (e.g. higher-rank tensor TOM encoder; positional binding rather than nested bind)

## Routing

- **Research:** if v3 desired, propose alternative test designs (above); confirm Stage 3 TOM higher-order remains MM-40%; do NOT promote to chain-grade.
- **Skunkworks:** smoke metrics path above for landed-VET review of HF diagnostic discipline.
- **Cert trail:** v1 + v2 both MIDDLE_BAND/HF at flat-depth; Stage 3 TOM higher-order documented as "test-design-limited; capability not characterizable with current 4-loc cleanup-attractor instrument."

## Commits

- c9484c52 exp_dev: substrate_higher_order_tom_recursive_v2_reframed cell+prereg
