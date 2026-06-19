# Pre-reg: Kovacs Hump (Wave 14 Observability V2 — Strategy 07:05 P-B-2)

Double-quench protocol: aging at beta_low for t_w steps, then beta_target. Measure max overshoot of Hopfield energy. Substrate adapted: t_w_grid=[10, 100, 1000, 5000], beta_low=0.5, beta_target=2.0, N=8192, K=100.

## Verdicts
- `KOVACS_RS_INDEPENDENT` — max/min amplitude across t_w < 1.2 (RS-phase aging-independent).
- `KOVACS_BROAD_RELAXATION` — max/min amplitude > 2.0 (broad/RSB relaxation with aging).
- `KOVACS_INTERMEDIATE` — between 1.2 and 2.0.
