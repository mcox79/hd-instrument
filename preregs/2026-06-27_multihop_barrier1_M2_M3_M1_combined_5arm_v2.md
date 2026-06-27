# Prereg: multihop_barrier1_M2_M3_M1_combined_5arm_v2

Date: 2026-06-27
Anchor: multihop_barrier1_M2_M3_M1_combined_5arm_v2
Cell: experiments/exp_multihop_barrier1_M2_M3_M1_combined_5arm_v2.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive; CPU-feasible
       per drill estimates ~4-5 hr full run)
Wave: Drill 4 rank-1 multi-hop; 3-mechanism stack META_BARRIER_1 test
Supersedes: v1 (HARD_FAIL setup-exception 2026-06-27 in make_deep_chains)

## v2 vs v1 (load-bearing diff)

v1 crashed in `make_deep_chains` with:
  `BLOCKING make_deep_chains: only 200/500 generated for V=200 disallow|=0 max_depth=8`

Root cause: TRAIN call requested 500 chains from V_C=200 codebook, but
the generator enforced distinct starts (`used_s` set) which caps achievable
chains at V_C. Mechanism never ran (verdict reported HARD_FAIL D3 setup
exception across all 3 seeds; ~0.7s wall).

v2 changes:
  1. V_C_FULL raised 200 -> 500 (USER recommendation; preserves test power
     at depth=8 vs the alternative of cutting N_CHAINS_TRAIN which would
     weaken M2 shortcut formation).
  2. make_deep_chains RELAXES distinct-start when disallow_s is empty
     (TRAIN case); KEEPS distinct-start when disallow_s non-empty (QUERY
     needs train-disjoint starts as a load-bearing rail). TRAIN diversity
     comes from random (s, p) sampling NOT start uniqueness.
  3. Pre-flight feasibility check at module init: `preflight_chain_feasibility`
     asserts (V_C, max_depth, N_CHAINS_TRAIN, N_CHAINS_QUERY) is satisfiable.
     SCHEMA-VET HARD_FAIL at import time if infeasible (caught before any
     seed runs setup).

## RECALIBRATION NOTE (sanity band widened)

ARM_BASELINE depth-5 anchor was 0.145 +/- 0.04 at V_C=200 in the
4-prior-refute regime. v2 raises V_C to 500. Per-hop cleanup margin degrades
modestly when V_C grows (more atoms to argmax over, but interference penalty
stays N=8192-bounded). Sanity band conservatively widened from [0.105, 0.185]
to [0.080, 0.200] to accommodate the regime shift.

Discriminator HP / MB bands UNCHANGED:
  - HP_COMBINED_DEPTH5 = 0.65  (META_BARRIER_1 BROKEN threshold)
  - MB_COMBINED_DEPTH5 = 0.30  (partial-breach threshold)
  - INDIVIDUAL_OVER_BASELINE = 0.05  (per-arm signal threshold)

If ARM_BASELINE depth-5 lands BELOW 0.080 at V_C=500, the regime is broken
(margin too thin to discriminate); SANITY_RAIL HARD_FAIL fires.

## Motivation (unchanged from v1)

META_BARRIER_1 (atomized 2026-06-25): 4 substrate-native multi-hop
closure attempts REFUTED at random-bipolar isotropic regime
(consolidation / pointer-chain / WM-scaffold / CSP-gated). META_M7
parallel-vote also regime-artifact.

3 categorically novel mechanisms from drill 2026-06-27 tested as a stack
plus per-arm individual ablations: M1 GROVER amplification / M2 NREM-REPLAY-
COMPACT / M3 STABILIZER-VECTOR.

## ARMS (5; cardinality_ok mandatory)

Same as v1. ALL arms share the SAME train chain set + SAME W_base.

## Pre-reg bands (HARD-LOCKED)

HARD_PASS_META_BARRIER_1_BROKEN (all must hold):
  - ARM_COMBINED depth-5 mean top1 >= 0.65
  - AND ARM_BASELINE depth-5 mean top1 in [0.080, 0.200]  (v2 widened)
  - AND cardinality_ok: 5 arms x SEEDS=3 x DEPTHS=4 = 60 arm entries

MIDDLE_BAND_PARTIAL_BARRIER_BREACH:
  - ARM_COMBINED depth-5 in [0.30, 0.65) AND ARM_BASELINE in sanity band

HARD_FAIL_META_BARRIER_1_NEGATIVE:
  - ARM_COMBINED depth-5 < 0.30 AND no individual M1/M2/M3 arm exceeds
    ARM_BASELINE by > 0.05 at depth-5

HARD_FAIL_STACK_NOT_SYNERGISTIC:
  - ARM_COMBINED depth-5 < 0.30 BUT individual arm lift >= 0.05

HARD_FAIL (other):
  - PREFLIGHT_INFEASIBLE (caught at import; surface message includes V_C,
    max_depth, N_CHAINS_QUERY)
  - SANITY RAIL breach: ARM_BASELINE depth-5 NOT in [0.080, 0.200]
  - D4 cardinality breach
  - D3 caught exception in any arm
  - D2 mechanism inert: n_shortcuts_added==0 OR n_replay_events==0

## Cardinality (D4 mandatory)

EXPECTED_N_UNITS_FULL = SEEDS x ARMS x DEPTHS = 3 x 5 x 4 = 60 arm entries.
HARD_FAIL_CARDINALITY_BREACH = observed != 60 OR any seed != 20 arm entries.

Smoke EXPECTED_N_UNITS = 1 x 5 x 1 = 5.

## Discriminator-must-survive-scale (D1)

Smoke uses FULL V_C=500, FULL N_CHAINS_TRAIN=500, FULL K_SET=20.
Smoke reduces ONLY: N_DIM 8192->2048; SEEDS [7,17,23]->[7]; N_CHAINS_QUERY
200->50; DEPTHS [2,3,5,8]->[5]. Smoke must show ARM_COMBINED > ARM_BASELINE
by >= 0.05 at depth-5 OR stop.

USER 2026-06-27 NO LOCAL directive => no local smoke. Full dispatch
straight to remote_cpu_queue.

## SANITY RAIL (hard abort path)

- ARM_BASELINE depth-5 mean top1 NOT in [0.080, 0.200]
- ARM_BASELINE depth-1 (if depth=1 included in DEPTHS) below 0.50

## Substrate-only-decode gate

n_llm_calls per seed = 0 (numpy-only mechanism).

## Real data / synthetic provenance

Random bipolar atoms + random predicate selection per chain (matches
pointer-chain v2 conventions). allow_synthetic=True.

## Compute budget

Per drill estimates: ~80-100 min per seed at V_C=500 (slight increase over
V_C=200 due to larger cleanup argmax: 500-element vs 200-element); 3 seeds
~ 4.5 hr remote CPU. Recommended --timeout: 21600s (6 hr; 1.5x buffer).

Smoke: 1 seed, 1 depth, 5 arms at N_DIM=2048: ~10-15 min.

## Verdict logic (4-class)

Same as v1; only band recalibration on sanity rail.

## SCHEMA-VET 5b per-arm HP scope

Each arm's metrics fully reported in metrics.json per_seed.arms[].

## Atomization on landing

HARD_PASS: META_BARRIER_1_BROKEN_VIA_M2_M3_M1_STACK atom; chain-grade
  candidate after 5-seed reproducibility on next cell.
MIDDLE_BAND: META_BARRIER_1_PARTIAL_BREACH atom; identify load-bearing
  mechanism + dispatch single-mechanism cell at higher resolution.
HARD_FAIL_NEG: META_BARRIER_1_QUADRUPLE_NEGATIVE_PLUS_TRIPLE atom;
  adopt M5 honest-acceptance framing.
PREFLIGHT_INFEASIBLE: cell-author bug; not a META_BARRIER_1 verdict
  (re-author cell with feasible config).
