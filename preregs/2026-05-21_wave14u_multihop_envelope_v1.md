# Pre-registration: wave14u_multihop_envelope_v1

Date: 2026-05-21
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14u_multihop_envelope_v1.py](../experiments/exp_wave14u_multihop_envelope_v1.py)
Priority source: follow-up to [wave14t_multihop_v3](../experiments/exp_wave14t_multihop_v3.py)
verdict `MULTIHOP_DECAY_AT_50` (soft fail on acc_1hop=0.927 < 0.98)
Author: experiment_dev session, pipeline tick 6

## Why

wave14t_multihop_v3 just landed `MULTIHOP_DECAY_AT_50`. The depth coverage
all worked (acc=0.93/0.72/0.54/0.19/0.15 at depths 1/5/10/25/50, per-hop
retention 0.96, log-decay slope -0.038). But acc_1hop=0.93 vs the
expected 0.98 floor. The expected 0.98 came from
`wave14e_multi_hop_v2.acc_1hop=0.98` measured at NUM_FACTS=50. v3 used
NUM_FACTS=100 (twice the distractor noise). The difference is the noise
floor.

The actually-load-bearing capability claim for cap_map is the
**fact-base envelope**: for what range of NUM_FACTS does the substrate
support deep multi-hop chains with high 1-hop floor? This envelope
sweep gives Strategy the operating numbers.

## Hypothesis

At N=4096, sweep NUM_FACTS in {25, 50, 100, 200, 400}, hop depths
{1, 10, 50}, 3 seeds. Expectations:

- acc_1hop monotonically decreases with NUM_FACTS (more noise floor)
- acc_50hop monotonically decreases with NUM_FACTS (compound noise)
- There exists some NUM_FACTS* below which both criteria pass
  simultaneously (acc_1hop >= 0.98 AND acc_50hop > 0.10)

## Multi-probe success criteria

This is a characterization experiment, not a pass/fail. Verdict
captures the largest NUM_FACTS at which:

1. acc_1hop >= 0.98 (substrate 1-hop floor stable)
2. acc_50hop > 0.10 (50-hop chains remain viable)
3. per-hop retention rate >= 0.90 (compound failures don't cascade)

The "envelope width" is the largest NUM_FACTS where all three hold.
Verdict reports the envelope width and the failure mode at the first
NUM_FACTS that breaks.

## Kill criterion

If even at NUM_FACTS=25 the substrate fails criterion 1 (acc_1hop < 0.98),
the wave14e_multi_hop_v2 result didn't replicate — verdict
`ENVELOPE_V2_NOT_REPLICATED`, route to setup audit.

If even at NUM_FACTS=25 the substrate fails criterion 2 (acc_50hop ≤ 0.10),
the multi-hop capability claim is bounded at very low fact-base sizes —
verdict `ENVELOPE_NARROW_AT_LOW_NUM_FACTS`.

## Verdict labels (5)

- `MULTIHOP_ENVELOPE_GE_200` — passes through NUM_FACTS=200 or higher
- `MULTIHOP_ENVELOPE_AT_<N>` — largest NUM_FACTS passing is <N>;
  envelope characterized
- `ENVELOPE_V2_NOT_REPLICATED` — even smallest NUM_FACTS fails acc_1hop
- `ENVELOPE_NARROW_AT_LOW_NUM_FACTS` — even smallest NUM_FACTS fails acc_50hop
- `MULTIHOP_ENVELOPE_INCONCLUSIVE` — missing data

## Oracle assertions (smoke mode)

1. At smoke's smallest NUM_FACTS, acc_1hop must replicate the v2/v3 floor:
   `oracle.assert_baseline_high("acc_1hop_smoke", acc_at_smallest, 0.85)`
2. Per-depth accuracies are non-increasing in depth at any fixed NUM_FACTS
   (sanity: deeper chain can't outperform shallower).

## Pre-mortem (3 failure causes)

1. **NUM_FACTS not the only variable** — chain construction also varies
   (chain entities sampled per trial). Solution: same chain construction
   logic as v3, single confound = NUM_FACTS.
2. **NUM_FACTS=400 + HOP_DEPTH=50 takes too long** — 400 facts in M
   means probe matmul is 400×N. 50 hops × 50 trials × 3 seeds × 5 NUM_FACTS
   = lots of probes. Estimated ~3-7 min on GPU; smoke should be <8s.
3. **Per-seed variance dominates the envelope estimate** — only 3 seeds.
   Mitigation: include per-seed accuracy in metrics; if seed-to-seed
   variance > 0.1 at any cell, log a `HIGH_SEED_VARIANCE` warning in
   the verdict_msg.

## Operational definition

- N=4096 (substrate width)
- NUM_ENTITIES=200, NUM_RELATIONS=20 (matches v3)
- NUM_FACTS sweep = {25, 50, 100, 200, 400}
- HOP_DEPTHS = [1, 10, 50] (reduced from v3's [1,5,10,25,50] for speed;
  the 3 depths are the load-bearing ones for the envelope claim)
- N_TRIALS=50, SEEDS=[17, 23, 31]
- Reuses v3 functions: make_bsc_codebook, build_factbase, run_chain

## Cited mechanism / sources

Same as v3. This is a NUM_FACTS-axis sweep of v3's exact mechanism.

## Expected runtime

- Smoke (N=512, NUM_FACTS={20, 50}, depths=[1, 10], 2 trials, 1 seed):
  ~3-6 s on CPU
- Full (N=4096, 5 NUM_FACTS values × 3 depths × 50 trials × 3 seeds):
  estimated 3-7 min on GPU

## What product decision this enables

- `ENVELOPE_GE_200` → product claim "multi-hop reasoning to 50 hops on
  fact-bases up to 200 facts" — concrete operating range
- `ENVELOPE_AT_<N>` → product claim with explicit fact-base cap
- `ENVELOPE_NARROW_AT_LOW_NUM_FACTS` → multi-hop capability is fact-base-
  size-bounded; cap_map row gets a small envelope number
- `V2_NOT_REPLICATED` → audit test setup before drawing conclusions
