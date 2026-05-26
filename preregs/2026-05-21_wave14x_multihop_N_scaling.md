# Pre-registration: wave14x_multihop_N_scaling

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14x_multihop_N_scaling.py](../experiments/exp_wave14x_multihop_N_scaling.py)
Priority source: follow-up to [wave14u_multihop_envelope_v1_b](../experiments/exp_wave14u_multihop_envelope_v1.py)
verdict `ENVELOPE_V2_NOT_REPLICATED` (substrate's 1-hop ceiling is ~0.95-0.97
multi-seed at N=4096, not the 0.98 implied by v2's single-seed result)
Author: experiment_dev session, pipeline tick 9

## Why

Multi-hop envelope showed the substrate's 1-hop ceiling at N=4096 is bounded
~0.95-0.97 across NUM_FACTS in {50, 100, 200, 400, 800}. The implied
cause: noise floor scales with NUM_FACTS / sqrt(N). Substrate theory
(per v2 docstring) predicts per-hop detection margin = sqrt(N/F); doubling
N at fixed F should square-root-improve the margin → tighter ceiling.

v4 tests this directly: keep NUM_FACTS=100 fixed (matches v3), sweep
N ∈ {4096, 8192, 16384}. Predicted: acc_1hop should improve to ~0.99 at
N=8192 and toward perfect at N=16384.

This is a capability *characterization* experiment — answers "how much do
we need to widen the substrate to get high 1-hop fidelity at fixed F?"

## Hypothesis

At NUM_FACTS=100, NUM_ENTITIES=200, NUM_RELATIONS=20, HOP_DEPTHS=[1, 10, 50],
3 seeds, sweep N ∈ {4096, 8192, 16384}:

- acc_1hop monotonically increases with N (theory: noise ∝ 1/sqrt(N))
- acc_1hop ≥ 0.99 at N=8192 (predicted by per-hop margin theory)
- acc_50hop also improves with N (per-hop retention closer to 1.0)

## Multi-probe success criteria

Characterization, not pass/fail. Verdict captures:

1. Did acc_1hop reach ≥0.99 at any tested N? If yes, at what N?
2. Did per-hop retention rate (estimated from acc_50hop^(1/50)) cross 0.98?
3. Is the N-scaling consistent with sqrt(N) theory (acc_1hop = 1 - C/sqrt(N))?

## Kill criterion

If acc_1hop doesn't improve with N (slope of acc_1hop vs log2(N) ≤ 0),
the substrate is bounded by something other than crosstalk noise — likely
the cleanup mechanism itself has a floor independent of N. Verdict
`MULTIHOP_N_SCALING_NO_BENEFIT`.

## Verdict labels (5)

- `MULTIHOP_N_RECOVERS_AT_<N>` — acc_1hop ≥ 0.99 at the specified N or
  smaller; substrate scales as theory predicts
- `MULTIHOP_N_IMPROVES_BUT_BOUNDED` — acc_1hop improves with N but doesn't
  reach 0.99 even at largest tested N
- `MULTIHOP_N_SCALING_NO_BENEFIT` — kill criterion; N has little effect
- `MULTIHOP_N_SCALING_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. At smoke's smallest N, acc_1hop must be high (substrate sanity).
2. Per-N codebook orthogonality bounded — same Mirage check as v3.

## Pre-mortem (3 failure causes)

1. **GPU memory at N=16384**: substrate W and pool entries scale as N
   per atom, fact-base M = 100 facts × N each = 100*16384 = 1.6M floats
   per fact-base seed. Per seed (just one M built per trial), 1.6M * 4
   bytes = 6.4 MB. Plus entity_atoms (200 × 16384 = 3.2M = 13MB) and
   relation_atoms (20 × 16384 = ~1.3MB). Total ~20 MB per seed. Per
   trial 50 trials × 3 depths × 3 N values × 3 seeds = ~1350 fact-base
   builds. Each independent so memory recycles. Should be fine.
2. **Runtime at N=16384**: matmul cost for build_factbase scales O(N) per
   triple, cleanup_argmax scales O(N*num_entities). Each hop step is
   O(N*num_entities) cleanup + O(N) bind. 50 hops × 50 trials × 3 N × 3
   seeds × 3 depths = 67500 cleanup ops × 16384*200 = ~220 G ops total.
   On GPU at 10 TFLOPS effective: ~22 s. Plus build_factbase: 100 facts ×
   3 binds each × 16384 ops = 5M ops per build × 7500 builds = 37 G ops
   = ~4 s. Total <1 min. Easy.
3. **Per-hop retention at N=16384 might be too close to 1.0 to detect
   meaningfully**: if every hop is essentially perfect, retention_rate
   ≈ 1.0 - epsilon, hard to compare across N. Mitigation: report
   1 - retention as the "error per hop" instead.

## Operational definition

Reuses [exp_wave14t_multihop_v3.py](../experiments/exp_wave14t_multihop_v3.py)
functions: make_bsc_codebook, build_factbase, run_chain, per_hop_retention_rate.

Sweep over N_LIST = {4096, 8192, 16384}, holding everything else equal:
- NUM_ENTITIES = 200
- NUM_RELATIONS = 20
- NUM_FACTS = 100
- HOP_DEPTHS = [1, 10, 50]
- N_TRIALS = 50
- SEEDS = [17, 23, 31]

## Cited mechanism / sources

- Plate 1995, Kanerva 2009 — HRR/BSC binding + cleanup primitives
- wave14e_multi_hop_v2 (own work) — original 1-hop=0.98 measurement at
  N=4096, NUM_FACTS=50 (single seed)
- wave14t_multihop_v3 (own work) — multi-seed acc_1hop=0.93 at NUM_FACTS=100
- wave14u_multihop_envelope_v1_b (own work) — 1-hop ceiling characterized

## Expected runtime

- Smoke (N=[512, 1024], NUM_FACTS=20, depths=[1, 10], 5 trials, 1 seed):
  ~3-5 s on CPU
- Full (N=[4096, 8192, 16384], NUM_FACTS=100, depths=[1, 10, 50], 50
  trials, 3 seeds): estimated 1-3 min on GPU

## What product decision this enables

- `N_RECOVERS_AT_<N>` → cap_map row gets explicit N-vs-fidelity number
  (e.g., "N=8192 needed for 99% 1-hop fidelity at F=100")
- `N_IMPROVES_BUT_BOUNDED` → suggests cleanup mechanism has its own floor
  beyond noise; routes to mechanism investigation
- `N_SCALING_NO_BENEFIT` → 1-hop ceiling is intrinsic to the substrate
  design, not noise-limited
