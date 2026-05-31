# Pre-registration: G3 handoff_composition_probe_v1_n4096

Date: 2026-05-30
Anchor: handoff_composition_probe_v1_n4096
Queue: overnight_queue
Script: experiments/exp_handoff_composition_probe_v1_n4096.py
N-suffix: _n4096 (PROT-018) — production N = 4096

## Question

At N=4096 BSC, do any of 3 composition strategies deliver measurable
advantage (verifier_catch_rate or accuracy_delta) over Path D alone, in
the sub-capacity / at-capacity / past-capacity regimes? The goal is
informing Pattern B LLM-integration with a mechanism-selection logic.

## Production config (PROT-018)

- N_FULL = 4096
- STRATEGIES = ["A_heuristic", "B_parallel_verify", "C_targeted_verifier"]
- REGIMES_FULL = [("sub_cap", M=2048), ("at_cap", M=4096),
                   ("past_cap", M=16384)]
- DEPTH_FIXED = 5
- K_FIXED = 500
- SEEDS_FULL = [7, 17, 23, 31, 41]  (5 seeds)
- N_STARTS = 16
- 3 strategies x 3 regimes x 5 seeds = 45 cell-seeds
- PER-CELL CHECKPOINT (PROT-021)

## Strategy semantics

- **A_heuristic**: choose path by query characteristic
  (high_K = K>=750 -> E; sub_cap = M<4096 -> B; else D).
  At K_FIXED=500, A reduces to B in sub_cap and D in at_cap/past_cap.
- **B_parallel_verify**: run B, D, E; return D; flag D-vs-B
  disagreements; verifier_catch_rate = fraction where D wrong AND
  B right.
- **C_targeted_verifier**: D + ONE verifier (E if high_K else B).
  At K=500: C uses B as verifier in all 3 regimes; verifier_catch_rate
  as B above.

## Pre-registered bands

- **HP**: at least 1 (strategy, regime) cell delivers
  `verifier_catch_rate >= 0.10` OR `accuracy_delta >= 0.05`
  in `>=3/5 seeds`.
- **HF**: ALL 9 (strategy, regime) cells have
  `verifier_catch_rate < 0.02` AND `accuracy_delta < 0.01`
  across ALL 5 seeds (no value anywhere).
- **MB**: otherwise (composition adds value in only 1 or 2 seeds
  per cell, or only at a single seed-cell).

## Smoke result

- smoke N=1024 regimes=[("sub_cap", 256), ("past_cap", 1024)]
  1 seed K=50 depth=5
- All 3 strategies executed correctly (path B, D, E ran; verifier
  branches recorded in strat_meta).
- All d_acc = 1.000, strat_acc = 1.000, delta = 0, catch = 0
- Smoke verdict: G3_HARD_FAIL (expected — smoke regime far below
  capacity where Path D errors would create headroom for composition).

### Smoke regime is uninformative — FLAGGED

The smoke regime (N=1024, M_max=1024 = at-capacity-of-smaller-N)
saturates Path D at 1.0. The FULL regime at N=4096 puts M=16384 at
2x capacity (C=4N=16384 codebook overlap rate increases), which is
where Path D errors actually appear per v211/v289 envelope work.
G3 HARD_FAIL at smoke is therefore the EXPECTED SMOKE RESULT for
this anchor — FULL run is the actual test, not a replication.

Per role contract suspicious-result gate, the relevant pattern would
be "all-constant metrics across conditions" — but the FULL config
exercises a regime not present in smoke, where Path D variation is
known to exist. Cells are not constant in code structure (different
strategies, different paths, different verifier branches recorded);
they are constant in outcome ONLY because the smoke regime is too
easy. Not blocking ship.

## Calibration / walk-back

- Effect size at smoke is undefined (no headroom). FULL keeps 5 seeds
  at planned regimes (no walk-back doubling) — the past_cap regime
  provides the actual test.

## OOM check

N=4096 M_max=16384. Codebook=256 MiB, W=64 MiB. Strategy B runs B/D/E
sequentially -> peak ~ single-path peak ~600 MiB. Under 6 GiB.

## Timeout estimate

- smoke_wall_s = 0.67s for 6 smoke cell-seeds (~0.11s per cell-seed)
- scaling: N=4x, M_max(1024->16384)=16x but mostly substrate build,
  K(50->500)=10x; effective scaling_exp = 1.5
- Strategy B is heaviest (B+D+E sequential).
- Per-cell-seed at FULL ~ 30-80s. Mean 50s.
- Total: 50s * 45 = 2250s. With margin 6000s.
- TIMEOUT = 21600s (6 hours; per user spec for Batch 1 #3 safety against
  past_cap E-AUC compute tail).
  Note flagged for For You status_log: >7200s long run.

## Outcome routing

- **HP**: at least one strategy delivers value at at least one regime ->
  Pattern B LLM integration gets a concrete mechanism-selection rule
  (which strategy at which regime). Direct input to product-engineering.
- **HF**: composition adds only latency. Path D alone is the operational
  choice; Pattern B integration uses Path D direct. Composition design
  branch closes.
- **MB**: composition useful in some regime but inconsistent across
  seeds -> characterize and route to a tuned-thresholds drill.
