# Prereg: wave14_1rsb_ultrametric_triples_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Pred-3 (1-RSB diagnostic) -- Ultrametric inequality on retained-task triples
**Trigger**: k2_m1_hierreplay HARD_PASS + basin-discrete 1-RSB framing;
             Parisi ultrametricity predicts that retained-task W-vector triples
             satisfy the isosceles ultrametric condition significantly above
             the random 0.33 baseline.

## Hypothesis

1-RSB (Parisi ultrametricity) prediction: for any triple (W_i, W_j, W_k) from
the pool of retained-task W snapshots, the two smallest pairwise overlaps are
approximately equal (isosceles condition). Empirical fraction of such triples
>= 0.50 (well above 0.33 random baseline).

RS prediction: overlaps are near-Gaussian; ultrametric fraction ~= 0.33 (random).

## Design (exp_dev autonomy)

- N = 2048 (FULL), 512 (smoke)
- Batch = 32 (FULL), 16 (smoke)
- Epochs = 5 (FULL), 1 (smoke)
- Phase-A epochs = 8 (FULL), 1 (smoke)
- Bytes per stage = 100000 (FULL), 3000 (smoke)
- Seeds = 12 seeds range(12) (FULL) -- gives 220 distinct triples, {7, 17, 23} (smoke)
- N_triples = 1000 (FULL), 100 (smoke)
- eps_ultrametric = 0.10
- Queue: local_cpu_queue (CPU; W is N=2048 x N=2048 but we only need flattened
         overlap matrix; < 25 min; laptop CPU tier for scoping)
- ETA: ~15-25 min CPU

## Pre-registered falsifier bands (before FULL run)

- **HARD-PASS (ultrametric / 1-RSB)**: ultrametric fraction >= 0.50 (> 0.33 + 0.17 margin).
  -> ULTRAMETRIC_1RSB_CONFIRMED: W triples satisfy isosceles condition; 1-RSB framing supported.

- **HARD-FAIL (RS)**: ultrametric fraction <= 0.36 (within noise of 0.33 random baseline).
  -> ULTRAMETRIC_RS_FLAT: W triples do NOT satisfy ultrametric; 1-RSB NOT supported.

- **MIDDLE**: fraction in (0.36, 0.50).

## Self-test cells

(ultra_frac=0.55, mean_gap=0.02) -> ULTRAMETRIC_1RSB_CONFIRMED
(ultra_frac=0.34, mean_gap=0.15) -> ULTRAMETRIC_RS_FLAT
(ultra_frac=0.43, mean_gap=0.08) -> ULTRAMETRIC_MIDDLE
({}) -> ULTRAMETRIC_RS_FLAT [default 0 values]

All 4/4 self-test cases pass in script self_test_verdict().

## Queue entry

`queue=local_cpu_queue name=wave14_1rsb_ultrametric_triples_v1 script=experiments/exp_wave14_1rsb_ultrametric_triples_v1.py prereg=preregs/2026-05-24_wave14_1rsb_ultrametric_triples_v1.md timeout=2400`
