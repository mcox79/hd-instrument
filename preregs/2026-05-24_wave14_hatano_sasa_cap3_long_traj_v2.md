# Prereg — wave14_hatano_sasa_cap3_long_traj_v2

## Hypothesis

v1 (`wave14_hatano_sasa_cap3_ness_crooks_v1`) landed in the MIDDLE BAND of
the Hatano-Sasa integral fluctuation theorem (HS-IFT) audit-cert for
Cap 3 (streaming-NESS). The MIDDLE result may have been a
finite-trajectory-length artifact: 60 Glauber steps and 150 trajectories
per cell may have been too few to sample the NESS distribution faithfully.

v2 doubles both:
- glauber_steps: 60 -> 120 (each Markov chain longer).
- n_traj_per_cell: 150 -> 300 (more chains per (noise, seed) cell).

If v2 lands HARD PASS, Cap 3 acquires the full HS-IFT audit-cert
(composable with Cap 1's Crooks erase cert into a full lifecycle).
If v2 stays MIDDLE, the v1 MIDDLE was not a length artifact — the
substrate NESS truly departs from canonical Markov detailed balance.

## Pre-registered bands (verbatim from v1)

- **HARD PASS** (`HATANO_SASA_CAP3_LONG_TRAJ_V2_HARD_PASS`):
  - <exp(-W_ex)> in [0.95, 1.05] aggregated across cells.
  - cross_basin_frac >= 0.05 (non-vacuous).
  - n_valid_cells >= 3.

- **HARD FAIL** (`HATANO_SASA_CAP3_LONG_TRAJ_V2_HARD_FAIL`):
  - <exp(-W_ex)> outside [0.5, 2.0].
  - n_valid_cells >= 3.

- **MIDDLE BAND**:
  - Anything else.

## Design

- N = 2048, M = 50, alpha = M/N = 0.024 (well below Hopfield critical
  alpha_c = 0.14 -- replica-symmetric retrieval phase).
- beta = 1.5 (near critical; cross-basin events at moderate rate).
- 4 noise levels: {0.30, 0.40, 0.50, 0.60}.
- 4 seeds: {17, 23, 31, 41}.
- 16 (noise, seed) cells * 300 trajectories * 120 Glauber steps each.

ETA: 1-2 hr CPU. v1 full ran ~30-40 min; v2 = 2x trajectories * 2x steps = ~4x v1 cost.

## Citations

- Hatano & Sasa 2001 (PRL 86: 3463): NESS fluctuation theorem.
- Speck & Seifert 2005: discrete Markov form.
- v1 prereg: preregs/2026-05-24_wave14_hatano_sasa_cap3_ness_crooks_v1.md.

## Routing

- Queue: `remote_cpu_queue`.
- Timeout: 7200 s.
- Pure-CPU; no CUDA.
