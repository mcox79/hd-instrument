# Prereg: wave14_1rsb_pq_retained_v1

**Filed**: 2026-05-24 exp_dev
**Anchor**: Pred-2 (1-RSB diagnostic) -- P(q) multi-delta from retained W-vectors
**Trigger**: k2_m1_hierreplay HARD_PASS + basin-discrete 1-RSB framing;
             if 1-RSB is genuine, the W_ABCD vectors across seeds should
             cluster into discrete basins (multi-peaked P(q)), not a broad
             unimodal distribution (RS).

## Hypothesis

1-RSB prediction: overlap distribution of W_ABCD snapshots across seeds shows
multi-peaked / delta-like structure (>= 2 peaks at >= 2-sigma separation +
binder > 0.30).
RS prediction: broad near-Gaussian unimodal P(q), binder <= 0.05.

## Design (exp_dev autonomy)

- N = 2048 (FULL), 512 (smoke) [CPU-feasible]
- Batch = 32 (FULL), 16 (smoke)
- Epochs = 5 (FULL), 1 (smoke)
- Phase-A epochs = 8 (FULL), 1 (smoke)
- Bytes per stage = 100000 (FULL), 3000 (smoke)
- Seeds = 10 seeds range(10) (FULL), {7, 17} (smoke)
- N_triples for ultrametric = 1000 (FULL), 100 (smoke)
- Queue: remote_cpu_queue (CPU -- no GPU needed; W collection at N=2048 is feasible)
- ETA: ~45-60 min CPU

## Pre-registered falsifier bands (before FULL run)

- **HARD-PASS (1-RSB multi-delta)**: >= 2 peaks with >= 2-sigma separation in
  KDE of W-overlap distribution AND binder > 0.30.
  -> PQ_1RSB_MULTI_DELTA: W-overlap P(q) multi-peaked; 1-RSB framing supported.

- **HARD-FAIL (RS)**: <= 1 peak OR max peak separation < 2-sigma AND binder <= 0.05.
  -> PQ_RS_UNIMODAL: W-overlap P(q) unimodal; 1-RSB NOT supported at P(q) axis.

- **MIDDLE**: anything between.

## Self-test cells

(n_peaks=2, max_sep_sigma=2.5, binder=0.35) -> PQ_1RSB_MULTI_DELTA
(n_peaks=1, max_sep_sigma=0.0, binder=0.03) -> PQ_RS_UNIMODAL
(n_peaks=2, max_sep_sigma=1.5, binder=0.15) -> PQ_RETAINED_MIDDLE
({}) -> PQ_RETAINED_MIDDLE

All 4/4 self-test cases pass in script self_test_verdict().

## Queue entry

`queue=remote_cpu_queue name=wave14_1rsb_pq_retained_v1 script=experiments/exp_wave14_1rsb_pq_retained_v1.py prereg=preregs/2026-05-24_wave14_1rsb_pq_retained_v1.md timeout=5400`
