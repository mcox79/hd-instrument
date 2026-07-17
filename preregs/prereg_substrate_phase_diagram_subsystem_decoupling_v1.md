# Pre-registration: substrate_phase_diagram_subsystem_decoupling_v1

Dedicated PHASE-DIAGRAM consolidation cell (USER 2026-07-17). Full pre-reg is
embedded in the cell docstring:
`experiments/exp_substrate_phase_diagram_subsystem_decoupling_v1.py` (top).
This file is the pointer + condensed summary for queue_add.sh provenance.

## Question

(1) Does the substrate's memory phase transition (recall vs load) on the REAL
FHRR bind/bundle/cleanup codes match the closed-form VSA capacity theory
`K_cliff(N,V) = N / (4 ln V)` (Plate 1995, cited via
`notes/research_5x_drill_N_scaling_analytical_formula_2026-07-01.md` Drill 1)?
(2) Can 3 memory subsystems be placed at DIFFERENT phase-points on a SHARED
substrate resource and operate correctly + INDEPENDENTLY (no cross-interference)?
(3) Does a deliberately mis-placed subsystem crater (telemetry-sensitive control)?

## Subsystems (construction-determined placement; NOT at risk)

- WM-FOCUS: N=1024, small direct bundle, low load (w=12) -- "focus" register.
- DURABLE STORE: same N=1024 registers, PAGED + EXACT external store (reuses
  `wm_paging_exact_store_ram_disk_v1`, commit 2c44dbc5); correct point = huge
  total load (2000 items, ~32x the WM cliff).
- COMPUTE: N'=16384, BLOCK-SPARSE fixed active-cost k=16 (reuses
  `sparse_bundling_capacity_per_cost_v1` mechanism); correct point = fixed tiny
  cost regardless of huge pool size. Architecturally isolated from the shared
  buffer (separate address space) -- its "independence" is by construction,
  disclosed honestly, not tested at risk.

## At-risk claims (these earn the tier)

- (a) transition-vs-theory: MATCH 0.5<=ratio<=3.0; PARTIAL 0.2-0.5 or 3.0-8.0;
  MISMATCH outside. Author 3-seed pre-check (N=1024,V=64) found the measured
  0.5-crossing near mult~6.5-8x theory, not 1x -- tolerance set at whole-order-
  of-magnitude granularity, honestly, not tuned to force MATCH.
- (b) independence: WM-focus and Store share ONE physical buffer (their bound
  items are summed into the SAME complex vector). DECOUPLED if
  recall_wm_alone>=0.90 AND recall_wm_concurrent>=0.85 AND
  (alone - concurrent) <= 0.05. INTERFERES if delta > 0.15.
- (c) mis-placement craters: c1 = WM-focus alone at top-of-grid load (~14x
  theory); c2 = Store's window deliberately oversized (~14x theory) while
  sharing WM's buffer. FIRED iff both recall <= 0.35 (chance floor = 1/64 =
  0.0156, so 0.35 is a real, well-above-floor degradation bar).

## Overall tier (CLAIM, VET-PENDING -- never asserted as fact by this cell)

- chain-grade-capable: (a) MATCH AND (b) DECOUPLED AND (c) FIRED.
- MEASURED_MECHANISM (mixed): any single claim MIDDLE/PARTIAL.
- construction-proof only: any claim MISMATCH/INTERFERES/NOT-FIRED.

## Schema-vet gates (see docstring for full detail)

storage_strategy=mixed (explicit exemption, comparison arms); cardinality_ok
EXPECTED_N_UNITS = n_seeds_a*n_grid_m + n_seeds_bc*3 + n_seeds_store + n_seeds_compute;
real_code_path/substrate_signature N/A (self-contained numpy FHRR, no KGStore);
deterministic_seeding=fixed ints only; discriminator survives scale (smoke =
full N=1024/N'=16384, fewer seeds/grid points only); arms_differ_verified=True
(hashes actual generated codes, not scalar recall); final_metrics_atomicity=
tmp_replace; progress_logging=n/a (wall time is seconds, well under 1800s).

## Compute architecture

(b) sequential-CPU with justification: all arrays N<=16384, load<=2000, total
wall time ~10-13s (measured, both smoke and FULL). No GPU speedup available at
this scale. Local numpy only; no remote queue-push / GPU / atoms / origin push.

## Measured smoke + FULL (landed, both HARD_PASS on cardinality, verdict=MIDDLE_BAND / MEASURED_MECHANISM)

FULL (5 seeds claim-a, 5 seeds claim-b/c, 3 seeds store, 3 seeds compute;
expected_n_units=71, elapsed_s=10.2):
  m50_measured=376.0 vs K_theory=61.55 -> ratio=6.11 -> PARTIAL
  recall_wm_alone=1.000 recall_wm_concurrent=1.000 cross_interference=+0.000 -> DECOUPLED
  c1(m=862)=0.235 crater=True; c2(store_window=862)=0.333 crater=True -> FIRED
  subsystem2 paged_exact=1.000 (correct); subsystem3 compute recall=1.000 (correct)
  OVERALL TIER: MEASURED_MECHANISM (mixed at-risk verdicts; CLAIM, VET-PENDING)
