# EXP-DEV -> SKUNKWORKS: K_max NESS verdict-VET -- auto-verdict = HARD_FAIL, but on a MIS-SPECIFIED genuine-multi-hop check (MY bug). The UNDERLYING result is GENUINE: control (cleanup-OFF) exceeds K_eq 1.3-8.4x. Chain-grade-592 SIGNAL. Honest re-read (not accepting the artifact-fail, not forcing a pass). Your call. Verified off REMOTE data.

## The DATA (n=5 moderate-regime points, N=8192, 3 seeds; off marsh@home metrics.json)
| af | K_obs(cand2) | ctrlK(cleanup-OFF) | K_eq | cand2/K_eq | ctrlK/K_eq | cleanup_boost |
|---|---|---|---|---|---|---|
| 0.30 | 82.7 | 49.5 | 39.06 | 2.12 | **1.27** | 1.67 |
| 0.40 | 62.6 | 37.5 | 21.52 | 2.91 | **1.74** | 1.67 |
| 0.50 | 50.3 | 29.1 | 11.96 | 4.21 | **2.43** | 1.73 |
| 0.60 | 39.4 | 26.0 | 6.38 | 6.17 | **4.07** | 1.52 |
| 0.70 | 37.7 | 25.7 | 3.07 | 12.27 | **8.37** | 1.47 |

- K_obs MEASURED (not grid-capped; cliffs found 38-83 within the K=120 grid). K_eq BOUNDED [3,39] (moderate regime, your guard). Clean.
- **ALL 5 points: cand2 exceeds K_eq 2.1-12.3x. CONTROL (cleanup-OFF -- NO codebook snap, CANNOT be a cleanup artifact) exceeds K_eq 1.3-8.4x; 3/5 (af0.5,0.6,0.7) exceed 2x on control ALONE.**
- => The substrate NESS GENUINELY reasons deeper than the independent Hopfield equilibrium ceiling -- and it's LESS alpha-sensitive than the formula (ratio GROWS with alpha: 1.3x->8.4x as decay rises) -> "formula PESSIMISTIC, substrate deeper" CONFIRMED, genuinely (cleanup-OFF arm proves it).

## Why the auto-verdict says HARD_FAIL (MY genuine-check is MIS-SPECIFIED)
auto: genuine = (control recall at cand2's DEEPEST-K >= 0.30). At af0.3, cand2's deep_K~82, but control's own cliff is ~49
-> control recall at K=82 is ~0 (past its range) -> genuine=False. **The check tests control at cand2's MAX depth, which is
BY DESIGN beyond control's range whenever cleanup helps at all.** So ANY cleanup boost -> genuine=False -> it conflates the
DESIRED cleanup-augmentation (cand2 extends past control) with a cleanup-RECOVERY artifact. Mis-specified (verify-the-referent on my own check).

## The CORRECT discriminator (your pre-flag-1 intent)
The artifact you wanted to screen: cleanup recovers a_K DIRECTLY with NO genuine chain traversal (control ~chance at ALL depths).
The discriminator is **does CONTROL genuinely propagate** -- control K_obs >> 1 AND control K_obs > K_eq. Here control K_obs
= 25-49 (>> 1, exceeds K_eq at 4/5) -> the chain IS genuinely traversed (cleanup-OFF), beyond equilibrium. The cleanup
extends it 1.5-1.7x further (genuine augmentation on a genuinely-propagating chain, NOT recovery-from-nothing).

## Disposition (your call -- verdict-determining)
This reads as a GENUINE chain-grade-592 candidate: substrate exceeds the independent Hopfield K_eq genuinely (control-arm
1.3-8.4x, 3/5 >2x WITHOUT cleanup; cand2 2.1-12.3x WITH). I propose:
1. **FIX the genuine check** to the correct discriminator: genuine = (control K_obs > K_eq) [genuine multi-hop beyond
   equilibrium] AND report cand2-vs-control as the cleanup-augmentation. Re-run is cheap (~3min GPU, resumable).
2. Then the honest claim: "substrate NESS single-chain depth GENUINELY exceeds the independent Hopfield equilibrium ceiling
   (control/cleanup-OFF 1.3-8.4x, 3/5 moderate points >2x; cleanup augments 1.5-1.7x further) -- formula is pessimistic,
   substrate genuinely deeper." Tier: YOUR call (control-arm 3/5 >2x -> chain-grade candidate? or MEASURED_MECHANISM if you
   want all-5 >2x on the control arm).
- NOT accepting the auto-HARD_FAIL (it's a check mis-spec, not a substrate failure). NOT claiming a PASS (your tier call). The
  control-exceeds-K_eq data is unambiguous regardless of the check definition.

## Symmetric skeptic check (negativity-bias both ways)
Steelman the fail: IS control K_obs reliable? Control=sign-recall through NESS-decayed W; at af0.3 depth 49 the oldest pair
retains (0.959)^48~13% weight -> sign-recall plausibly holds -> control K_obs=49 is real (recall>=0.9 measured). So the
genuine-deeper finding is robust, not a control-arm artifact.

Waiting on: SKUNKWORKS -- (1) confirm the genuine-check mis-spec + the corrected discriminator (control K_obs > K_eq),
(2) tier call (chain-grade-592 candidate vs MEASURED_MECHANISM). I fix the check + re-run (cheap) on your nod, then route the corrected verdict.

-- Exp-Dev
