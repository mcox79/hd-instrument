# Prereg: operating_point_singularity_basin_map_v1_n4096

Filed: 2026-05-29
Source: research_surge_synthesis_v276_2026-05-29.md Agent 1 cross-row insight / Priority 4.

## Hypothesis
4 lagging cap_map rows (Rows 4/5/6/8) may be artifacts of probing near a substrate
basin boundary / attractor singularity. Basin-mapping drill could defuse all 4 simultaneously.

## N-suffix
_n4096 binding: production N = 4096. Anchor: operating_point_singularity_basin_map_v1_n4096.

## Pre-registered bands

### Signal 1: Retention variance across seeds
HARD_PASS: max retention_variance > 0.05 at boundary M_fracs (4.0-7.0).
HARD_FAIL: max retention_variance < 0.01 across all M_fracs.

### Signal 2: Hysteresis amplitude
HARD_PASS: max hysteresis_amp > 0.02 at transition M_frac.
HARD_FAIL: max hysteresis_amp < 0.005 everywhere.

### Signal 3: BNV spike at transition
HARD_PASS: >= 2 boundary M_fracs show BNV >= 1.5x median BNV.
HARD_FAIL: no BNV spike.

### Joint outcome
HARD_PASS: >= 2 of 3 signals HARD_PASS.
HARD_FAIL: both variance AND hysteresis HARD_FAIL.
MIDDLE_BAND: 1 signal HARD_PASS.

## Smoke result
BASIN_MAP_SMOKE_PASS: hysteresis=0.02 (exactly HP_HYST), BNV spike at M_frac=5.5
(13.7 vs 1.4 baseline), retention drops 1.0->0.80->0.63 across M_fracs at N=1024.
Clear transition structure detected. Walk-back gate: not borderline.

## Timeout estimate
Smoke: N=1024, 3 M_fracs, 3 betas, 3 seeds: ~3.5s CPU.
FULL: N=4096, 8 M_fracs, 6 betas, 5 seeds.
Scale: (4096/1024)^1.5 * (8/3) * (6/3) * (5/3) = 8 * 2.67 * 2 * 1.67 = 71.5.
Est: 1.5 * 3.5 * 71.5 = 375s. Safety 2.5x: 938s. timeout_s = 1200.

## Middle-band outcome plan
If MIDDLE_BAND: file note that partial boundary signal detected. Route lagging rows
for re-run at M_frac < 4.0 (within-capacity).
If HARD_PASS: re-run all 4 lagging-row KF experiments at M_frac=1.0-2.0 (off-singularity).
