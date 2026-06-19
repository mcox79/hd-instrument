# Phase Region C/D -- TCFT and Saad-Solla Tier-2 Blocker

Filed: 2026-05-29
Routing: exp_dev -> Strategy

## Blocker Summary

The strategy request `strategy_request_to_exp_dev_post_reset_priority_2026-05-29.md`
requested 8 phase region C/D anchors: 4 variants (kf1/kf2/tcft/saad_solla) x 2 regions.
kf1 and kf2 variants shipped successfully (4 anchors).
TCFT and Saad-Solla variants are blocked for structural reasons.

## TCFT Blocker

TCFT (Thermodynamic Conditioning for Free-energy Trajectory) experiments in this repo
(exp_tcft_n8192_v5/v7, exp_tcft_fresh_erase_v4) use:
- numpy float64 Hebbian W
- Fixed thermodynamic parameter KBT=1.0 (not a sweep axis)
- No argparse --beta parameter
- The "beta" in TCFT context is inverse temperature in the Jarzynski/TCFT work formalism,
  structurally different from Hopfield's retrieval beta (softmax temperature at inference)

Adding a Hopfield retrieval beta sweep to TCFT would require:
  1. Adding argmax/softmax retrieval probe (TCFT experiments measure thermodynamic work, not retrieval accuracy)
  2. Adding --beta arg to exp_tcft_n8192_v7's softmax retrieval path
  3. Merging two conceptually distinct beta parameters in one script

Estimate: 2-4h engineering to retrofit TCFT properly. Not worth doing in this cycle.

## Saad-Solla Blocker

Saad-Solla experiments (exp_saad_solla_v15/v16/v19) are language model BPC experiments:
- Phase-A/Phase-B training on byte corpus
- `beta_inf` in v19 is the INFERENCE SOFTMAX TEMPERATURE for LM prediction
- Not the Hopfield inverse temperature (beta_c) that governs phase transitions in key-value memory
- The "retention" metric is BPC-based, not argmax key-value accuracy

The phase diagram probe requires the Kerdock key-value retrieval architecture.
Saad-Solla experiments do not have this architecture.

## Recommendation

File as Tier-2: if Strategy decides the phase lattice story requires TCFT/SS comparison,
route back with explicit "add Hopfield-retrieval beta arm to TCFT" as a new experiment spec.

Anchors shipped this cycle: region_c_kf1, region_c_kf2, region_d_kf1, region_d_kf2 (4 total).
