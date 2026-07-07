# PRE-REG: resonator_glauber_plurality_v1 -- EXTERNAL-RESET lever (finite-T Glauber + restart-plurality)

**Date:** 2026-07-07
**Author:** exp_dev
**Cell:** `experiments/exp_resonator_glauber_plurality_v1.py`
**Parent drill:** `notes/research_noise_compounding_bound_deep_mechanism_2026-07-07.md`
(+ `notes/research_resonator_basin_proliferation_self_predictability_2026-07-07.md`)
**Thread:** SECONDARY (not critical path). Honest odds P_deflated ~0.20-0.28.

## Hypothesis / mechanism

The resonator K-way factorization HARD_FAILs at K4 (0.142 single-shot,
MEASURED@data/exp_resonator_capacity_gpu_v1/metrics.json:per_seed[0].by) because its 60-iteration
deterministic zero-temperature coupled alternating-projection search has NO external reset (unlike
reasoning-depth's regenerative-repeater re-clean to a fixed codebook per hop). Test whether adding a
finite-temperature GLAUBER relaxation (annealed complex-Gaussian dither into the est vectors) + a
REDUNDANT-RESTART PLURALITY-VOTE (R=10 independent noisy trajectories, decode = most-frequent decoded
joint-index tuple) makes the bound CONTRABLE.

## Bands (VERBATIM from the drill, K=4 target)

- **HARD-PASS:** K4 plurality-vote success **>= 0.50** AND failures scatter over **>= 5 DISTINCT wrong
  configs** (proves it is outvoting DIVERSE spurious basins, not luck).
- **HARD-FAIL:** K4 plurality **<= 0.192** (no better than 0.142 baseline + 0.05) OR restarts **COLLAPSE
  onto the same 1-2 wrong configs** (redundancy inverts -- the basin-measure trap: if spurious basins
  collectively outweigh the true basin, plurality converges on a spurious answer).
- **MIDDLE:** 0.192 < K4 plurality < 0.50 -- real lift, honest partial rescue; do NOT force to HARD-PASS.

Implemented gates: `HARD_PASS_FLOOR=0.50`, `SCATTER_MIN=5` (distinct_wrong_min across seeds),
`HARD_FAIL_CEIL=0.1917`, `COLLAPSE_WTD=1.5` (mean within-trial distinct-tuple count below this ==
restarts do not decorrelate). Verdict picks the best T0>0 for K4 by mean plurality across seeds.

## Discriminator (META_RULE_K)

ERROR-CORRECTION-class mechanism. Discriminator FIRES iff the finite-T dither DECORRELATES restart
trajectories: measured by `mean_within_trial_distinct` (mean number of distinct decoded tuples among R
restarts per trial). If ~1.0 -> dither vacuous / basin-deterministic -> HARD-FAIL by construction
(collapse). If >1 -> dither perturbs; plurality can then aggregate. The T0=0.0 arm (R=10) is the
in-cell deterministic reference: it MUST show within_trial_distinct==1 and plurality==baseline.

## Positive control (Gate D, reproduce prior CG at test regime)

`K4_baseline_T0_R1` (T0=0, R=1) = the ORIGINAL deterministic single-shot decode, ported to numpy. Must
reproduce ~0.142 (band [0.05, 0.30] to allow seed/trial-count variation vs the 120-trial GPU run). If
outside band -> HARD_FAIL_POSITIVE_CONTROL, downstream arms untrusted (numpy port diverged from the
GPU decode). This is the SHAPE_MATCH reproducer arm at the test regime, not a citation.

## CRLB / discriminator reachability

`crlb_formula_reference`: idealized-i.i.d.-restart plurality. If restarts were i.i.d. with per-restart
success p=0.142 and failures uniformly scattered over M^K-1 ~ 810,000 configs, then
P(true appears >=1 in R=10) = 1 - (1-0.142)^10 = 0.784, and the true config is then the near-certain
unique mode (each specific wrong config expected ~10*0.858/810000 ~ 0 hits). So idealized plurality
success ~ 0.78, which CLEARS 0.50.
`discriminator_reachability`: **TRUE, conditional on dither decorrelating restarts** -- the HARD-PASS
floor is physically reachable IFF the coupled dynamics is chaotically sensitive to the dither. Whether
it IS is exactly the open empirical question (P~0.25). Not force-fit.

## Compute architecture

Class **(b) sequential-CPU with justification**. numpy, complex128, decode-only. Restarts (R=10)
are BATCHED on axis 0 (vectorized matmuls). Sequential over: K factors (genuine coupling dependency --
est[k] depends on all est[j!=k]), trials, and T0 arms. This is the CPU reference of a decode-only
capability; no GPU speedup needed at this scale (original GPU full = 13.4s for K2,3,4 x120 trials;
this is comparable x R=10 x T0-grid ~ minutes on CPU). Target queue: remote_cpu_queue for FULL.
storage strategy: no_storage (no atom persistence; pure decode probe).

## PAIRED trials (mandatory for arm comparison)

Within each (seed, K): identical phasor codebooks (rng seeded seed*100+K) and identical TR true-index
tuples (rng seeded seed*1000+K) are reused across ALL T0 arms and the baseline. Only the dither stream
differs across T0. Arms are strictly paired.

## Cardinality (META_RULE_H)

`EXPECTED_N_UNITS = len(SEEDS) * len(K_GRID) * len(T0_GRID)`. FULL: 3*2*5 = 30 glauber units (+ per-K
baseline). Verdict raises HARD_FAIL_CARDINALITY if aggregated seed count != len(SEEDS).

## Schema-vet fields

- `sweep_alignment_verdict: ALIGNED` (T0 is the swept axis; the dither the resonator experiences IS T0,
  no nominal-vs-effective gap).
- `discriminating_fraction`: T0-grid spans deterministic (0.0) through signal-destroying (0.50); the
  Goldilocks band is what the sweep localizes. baseline ~0.142 is in [0.05,0.95] measurable band.
- `arms_differ_verified`: baseline vs K4 T0=0.20 glauber arm hash-checked != (META_RULE_AF).
- `final_metrics_atomicity: tmp_replace` (write_metrics) + per-seed partials (_seed_checkpoint).
- `calibration_check: default_ok_for_this_regime` (no learned calibration; fixed codebooks).
- `cell_chunked: false` -- single-cell multi-seed with per-seed _seed_checkpoint partials (resumable);
  fast CPU cell (est <5 min FULL), runner-zombie loses at most the in-progress seed, completed seeds
  persist as partials.
- `start_marker_written: true`, `crash_diagnostic_present: true`, `heartbeat_present: true`,
  `defensive_error_checking: passed_all_4_patterns`.
- `progress_logging: print_flush_true` (per-unit flush + _heartbeat.jsonl; timeout est < 1800s but
  included for audit).
- `run_mode` default = full; `--smoke` -> smoke; `--self-test` -> exit 0. RUN_MODE verified post-dispatch.

## Functional requirements

1. Escape/outvote spurious joint fixed points -> finite-T Glauber dither (new mechanism; no existing
   primitive) + restart-plurality (mode estimation over R samples).
2. Clean final read -> anneal T0 -> 0 over MAXIT (last iteration deterministic given current est).
3. Diagnose WHY it works/fails -> log per-restart decoded tuples; within_trial_distinct (decorrelation)
   + distinct_wrong_configs (basin diversity vs pile-up).

## Honest disposition

If plurality does NOT beat baseline (basin-measure trap / basin-deterministic collapse), REPORT THAT:
the bound is harder than the drill hoped for the resonator, single-step/external-reset stays the only
fix. Do NOT force a pass on a P~0.25 test.
