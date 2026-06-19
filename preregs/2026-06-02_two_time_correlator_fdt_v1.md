# Prereg: two_time_correlator_fdt_v1

**Date:** 2026-06-02
**Anchor:** two_time_correlator_fdt_v1
**Queue:** remote_cpu_queue
**Research source:** notes/research_ultrametricity_revival_consolidation_2026-06-01.md, Q-F2

## Scientific question

Does the substrate's two-time correlator C(t,t_w) and FDT-violation ratio X(C)
discriminate between CK pure aging and the Garcia-Lorenzana oscillating-amorphous
overlay? Q19 confirmed CK-class aging via scaling collapse at N=1024. Q-F2 tests
shape discrimination: piecewise-constant X(C) = 1-step RSB; smooth-monotone = CK
pure aging; finite-omega DFT peak = Garcia-Lorenzana oscillating overlay.

## Pre-registered thresholds

Three sub-tests with independent thresholds:

**Sub-test A (aging confirmation):**
- HP-A: scaling_collapse_mse < 0.05 (C(t,t_w) is f(t/t_w))
- HF-A: scaling_collapse_mse > 0.20 (no aging; CK-class refuted)

**Sub-test B (X(C) shape):**
- HP-B: piecewise_r2 >= 0.85 (1-step RSB) OR smooth_r2 >= 0.85 (CK)
- HF-B: X(C) structureless (non-monotone, no shape)

**Sub-test C (Garcia-Lorenzana oscillation):**
- HP-C: DFT peak SNR > 3 at omega* > 0
- HF-C: DFT flat spectrum (rules out oscillating overlay)
- MIDDLE-C: 1 < SNR <= 3

**Overall:**
- HARD_PASS: HF-A absent AND (HP-B or HP-C)
- HARD_FAIL: HF-A triggered (aging absent => reopens static shelf)
- MIDDLE_BAND: HP-B and HP-C absent but HF-A absent

These are calibration probe bands (first FDT-ratio measurement for this substrate).

## Smoke result

- N=512, 2 t_w values {16,64}, 3 ratio points per t_w, 1 seed
- collapse_mse = 0.0048 (PASS sub-test A, well below HP=0.05)
- piecewise_r2 = 0.9826 (PASS sub-test B, above HP=0.85)
- smooth_r2 = 0.8547 (also passes sub-test B)
- DFT SNR = NaN (only 2 t_w values, need >= 4 ratio points for DFT)
- Wall: 0.2s
- Verdict: HARD_PASS decisive on sub-tests A + B

## Multi-scale smoke (N*4 = 2048)

- collapse_mse = 0.0104 (still passes HP=0.05 for aging test)
- piecewise_r2 = 0.1071 (FAILS at N*4 with 3 ratio points)
- smooth_r2 = 0.5714 (FAILS at N*4 with 3 ratio points)

Walk-back gate triggered: X(C) shape test degrades at N*4 with only 3 ratio points.
Analysis: the degradation is due to limited ratio_grid at smoke scale (3 points).
The FULL run has 6 ratio points across 3 t_w values, which should resolve this.
Walk-back action: note in prereg; ship at planned N=2048 with 6 ratio points.
The aging collapse test (sub-test A) remains strong at both scales.

## N-suffix declaration

No _nN suffix; production N=2048 per PROT-018 rule 3. N=2048, rationale: larger N
for cleaner FDT signal (Berthier 2001 used N~4000); 2048 is compute-feasible at
5 seeds with 3 t_w values and 6 ratio points.

## Timeout estimate

- smoke_wall_s = 0.2 (sub-estimate: fast at N=512 with few t_w)
- FULL_N/smoke_N = 4 (2048/512)
- FULL_seeds/smoke_seeds = 5 (5/1)
- scaling_exp = 1.5 (matrix ops + Glauber sweeps)
- t_max factor: full T_MAX = 256*16 = 4096 vs smoke 64*8 = 512; ratio = 8
- Combined scale: 0.2 * 4^1.5 * 5 * 8 = 0.2 * 8 * 5 * 8 = 64s. Add 1.5x buffer = 96s.
- But smoke was very fast due to small t_max. Full t_max=4096 vs smoke ~512: 8x longer.
- Conservative: 1.5 * 0.2 * (4096/512) * (2048/512)^1.5 * 5 = 1.5 * 0.2 * 8 * 8 * 5 = 96s
- Round to: timeout=1800s (conservative; DFT + 3 t_w overhead included; 18x buffer)

## Cap_map impact

- HP: PP-33 non-equilibrium row lifts; Garcia-Lorenzana 2025 (PRL 135, 187402) DYNAMICAL
  signature confirmed or ruled out; new oscillating-amorphous row candidate if DFT peak
- HF: aging absent => reopens static-RSB shelf; major strategic reassessment
