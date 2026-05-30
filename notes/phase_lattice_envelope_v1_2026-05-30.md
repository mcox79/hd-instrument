# Phase-lattice envelope reference (v1, 2026-05-30)

Reference data from `phase_lattice_grid_v1_n4096` GRID_HARD_PASS verdict (v283 batch).

## Source

- Anchor: `phase_lattice_grid_v1_n4096`
- N=4096 fixed; 5-seed (7,17,23,31,41); CPU run; 343.29s elapsed
- 9 betas x 7 M_fracs x 5 seeds = 315 cells, all populated
- Verdict: GRID_HARD_PASS ENVELOPE_MAP_DELIVERED frac=1.000

## Sweep axes

- betas = [2.0, 4.0, 8.0, 10.0, 12.0, 16.0, 32.0, 64.0, 128.0]
- M_fracs = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
- 6 metrics per cell: retention, above_thresh_frac (KF-1), max_iso (KF-2), edit_then_retrieve, retrieval_latency_ns, kf1_sharpness

## Aggregate

- mean_retention = 0.820 across the 9x7 grid
- mean_above_thresh_frac = 0.225 (KF-1 fires moderately on average)

## Usage

This file exists to make cap_map updates faster: when a future verdict claims "at cell (beta=X, M_frac=Y) ...", first check whether the cell is in this 315-cell map. The grid covers most-tested operating regions; cells outside (very-low M_frac<0.25, very-high beta>128, M_frac>16) need separate characterization.

## Source artifact (remote authoritative)

- Remote: `data/exp_phase_lattice_grid_v1_n4096/metrics.json` on marsh@home
- Local fallback: `data/exp_phase_lattice_grid_v1_n4096/metrics.json` (may be stale smoke)
- Read via `tools.orchestrator.remote_state.get_metrics('phase_lattice_grid_v1_n4096')` for authoritative

## Linked cap_map entry

v283 (2026-05-30) batched 16-verdict major-batch. See `notes/substrate_capability_map.md` v283 entry annotation "phase_lattice_grid: STORE 315-cell envelope as reference at notes/phase_lattice_envelope_v1_2026-05-30.md".
