# Pre-reg deviation note: exp_sparse_bundling_capacity_decorr_frontend_v1 (M-WIDEN, FULL de-censor pass)

Cell: `experiments/exp_sparse_bundling_capacity_decorr_frontend_v1.py`
Base pre-reg: embedded in the cell's own module docstring (arms, bands, self-tests, brain-check —
authored + landed as smoke MIDDLE_BAND at `data/exp_sparse_bundling_capacity_decorr_frontend_v1_smoke/metrics.json`).
This file is a DEVIATION NOTE only — it does not restate or supersede the docstring pre-reg; it documents
the ONE change made before the FULL dispatch, per Director task directive (2026-07-17).

## Why (Step 0 honest re-read of the smoke verdict)
Smoke landed `MIDDLE_BAND` / `MIDDLE_BAND_CENSORED`: at the realistic-MEAN decision rho=0.10, both RAW and
DECORR searches over J hit the `capacity_search` ceiling `cap_J = M_CODEBOOK // 2` (smoke M=4096, cap=2048)
before recall dropped below the 0.90 target — i.e. the reported `J_max` at that point is a FLOOR (a
censored lower bound), not the real 0.90-recall crossing the HARD_PASS/HARD_FAIL bands are defined against.
The mechanism claim itself is NOT in question here (decorr keeps within-cluster code cos ~0.04 at rho=0.50
vs raw's rcos=0.50, absolute J_max recovery 85.2x at the tail, must-fail control fires at every rho, all
already landed in the smoke) — this pass exists ONLY to get an un-censored capacity number at FULL scale.

## The ONE change (everything else IDENTICAL to the docstring pre-reg)
`M_CODEBOOK` for `RUN_MODE != "smoke"` (i.e. FULL) raised from the prior in-source default `8192` to
`16384` (search ceiling `cap_J = M_CODEBOOK // 2` therefore raised from 4096 to 8192). No other constant,
arm, formula, correlation model, DG expansion/WTA algebra, rho grid, seed set, or verdict-band threshold
changed. `NPRIME_GRID`, `CORR_LEVELS`, `SEEDS`, `K_BLOCK`, `EXPAND_FACTOR`, `DG_CONN`, `F_THIN`, `N_TRIAL`
are untouched from the pre-existing FULL config.

## Evidence the new M clears the decision-critical points (real-code-path probe, not synthetic)
Before editing, a scratch probe imported the cell's REAL `build_arm` / `capacity_search` functions
(unmodified) at the FULL grid's `N'=16384` (the discriminator-survives-scale endpoint) and swept
`M_CODEBOOK in {8192, 16384}` at both decision rhos (0.10 realistic-mean, 0.50 correlated-tail):
- **rho=0.50 (tail, the primary HARD_PASS/HARD_FAIL decision point):** MEASURED directly via the cell's own
  unmodified `build_arm`/`capacity_search` at N'=16384, seed=7, rho=0.5, at the PRIOR FULL default
  `M_CODEBOOK=8192` (cap_J=4096): RAW J_max=5.4 (censored=False; correlation collapses it, as already
  established — never anywhere near the ceiling at any M). DECORR J_max=2498.8, **censored=False** — i.e.
  the decision-critical tail crossing was ALREADY a real (non-floor) 0.90 crossing at the pre-existing M,
  just with a bare ~61%-of-ceiling margin (2498.8 of 4096). Doubling `M_CODEBOOK` to 16384 (cap_J=8192)
  keeps this a real crossing with a wide safety margin (>3x the measured J_max) instead of a bare majority-
  of-ceiling margin, and gives room for seed-to-seed variance across the FULL run's 2-seed set.
- **rho=0.10 (mean, secondary decision point):** DECORR's low-rho capacity is intrinsically very high
  (near-decorrelated codes at this rho — dcos~0.003 in the smoke), so a real (non-floor) 0.90 crossing at
  this rho would require an M far beyond what's compute-feasible for a CPU numpy sweep at this scale (the
  DG-expansion build cost scales as `O(M * N_exp * DG_CONN)`, confirmed compute-heavy at M=32768 in the
  scratch probe — a naive further M-quadrupling was abandoned as disproportionate, per the
  compute-proportionality discipline). The cell's OWN verdict logic (already present in source,
  `compute_verdict`, the `decorr_lower_bound_rhos` branch) treats a DECORR-side censor at a decision rho as
  a HONEST, NON-FATAL lower bound — not a floor that invalidates the verdict — whenever the floored
  decoupling value already clears the HARD-PASS bar (>=4.0x): a lower bound that already exceeds the bar
  proves the true (uncapped) value clears it too, a fortiori. Only a RAW-side censor, or a DECORR censor
  BELOW the bar, is treated as fatal ("MIDDLE_BAND_CENSORED"). This is unchanged by this deviation; M=16384
  was NOT chosen to chase an uncensored rho=0.10 crossing (compute-infeasible), only to (a) give the
  rho=0.50 tail decision point a real, uncensored crossing, and (b) double the existing FULL headroom at
  rho=0.10 in case it shifts the lower-bound value materially.

## What did NOT change
Verdict thresholds, band definitions, must-fail control, arms, correlation model, DG projection, rho grid,
seed list are byte-identical to the pre-existing FULL branch of the cell (see `experiments/exp_sparse_
bundling_capacity_decorr_frontend_v1.py`, the `else:` branch of `if RUN_MODE == "smoke":`). Only
`M_CODEBOOK` (8192 -> 16384) changed. `arms_differ_verified`, `final_metrics_atomicity=tmp_replace`,
`except SystemExit: raise` ordering, `cardinality_ok` (EXPECTED_N_UNITS gate), and deterministic seeding
(no `hash()`/`list(set())`) are all pre-existing cell-template mandates, unaffected by this deviation and
re-verified via `--self-test` before dispatch.

## Compute architecture (restated, unchanged)
Sequential-CPU numpy, $0, justified: this cell IS the substrate-primitive measurement (bit-identical CPU
reference for the block-sparse / DG-decorrelation capacity search); GPU batching would not materially help
the adaptive-doubling `capacity_search` sequential dependency structure. No `import torch`; routes to
`remote_cpu_queue` (routing-sanity gate in `tools/orchestrator/queue_add.sh` requires torch for
`overnight_queue`/GPU — correctly rejected there).

## Timeout justification (MEASURED, not estimated)
The `make_blocksparse_decorr` front-end build (per-block Python loop over `DG_CONN=16` random-signed
gathers of shape `(M, N_exp/K_BLOCK)`) is the dominant cost, O(M * N_exp * DG_CONN), and is UNCHANGED
algorithm (this deviation does not touch it). MEASURED via the same real-code-path probe: at M=8192,
N'=16384 (N_exp=65536), one DECORR build = 424.1s wall. This scales ~linearly in M, so at the new
M=16384: ~848s per Nhi DECORR build. FULL needs this build once per (seed, rho) pair at N'=16384 —
`len(SEEDS)=2 * len(CORR_LEVELS)=4` = 8 such builds ~ 8*848s ~ 6784s (~113min). Nlo (N'=1024, N_exp=4096,
16x smaller) builds are ~1/16th cost each (~53s x8 ~7min). RAW/DENSE/VALUE_THIN arms have no comparable
per-block Python-loop cost (RAW is vectorized gather/copy; DENSE/VALUE_THIN are BLAS-backed dense ops) —
estimated low tens of seconds total across all combos. Sum ~130-140min; with a 1.75x safety margin for
seed-to-seed build-cost variance and system load: **timeout_s = 21600 (6h)**, exceeding the queue_add.sh
soft-cap of 14400s (4h) — justified here per that script's own "cap at 14400 or justify" convention, on a
$0 CPU remote_cpu_queue run with no GPU/BOINC contention.
