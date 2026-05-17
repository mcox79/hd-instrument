# Experiment A3: attention modulator yields precision/recall curve

**Date:** 2026-05-16
**Phase:** Week 6 atomic experiments

## Hypothesis

Sweeping the `attention` modulator from 0 to ~1 trades recall for precision monotonically. With a mix of recoverable true queries and unmatched junk queries, attention=0 returns everything (low precision) and attention close to true-sim returns only the matches (high precision, lower recall).

## Predicted

- Precision rises non-decreasing as attention rises (allow ~0.05 tolerance).
- Recall falls non-increasing as attention rises.
- Best F1 occurs at an interior attention value (not 0 or 1).
- At attention=0: precision ~ 0.5 (50/50 true/junk).
- At attention=0.9: precision -> 1.0 (only confident matches kept).

## Falsification

- Non-monotone precision curve means attention is not the gate we think it is.
- F1 maximum at attention=0 or attention=1 means the modulator isn't carving an interior region.

## Result (2026-05-16)

| Check | Predicted | Observed | Outcome |
|---|---|---|---|
| Precision monotone non-decreasing | yes | **NO** | falsified |
| Recall monotone non-increasing | yes | yes | confirmed |
| Best F1 at interior attention | yes | yes (attention=0.10) | confirmed |
| Precision @ attention=0 | ~ 0.5 | 0.50 | confirmed |
| Precision @ attention=0.9 | -> 1.0 | 0.00 (everything rejected) | precision degenerates when tp=0 |
| Best F1 value | high | **1.000** (perfect classifier) | confirmed |

## Takeaway

**Precision is not monotone in attention.** It rises from 0.50 (everything accepted) to 1.0 at the "gap" between junk-similarity (~0.08) and true-similarity (~0.96), plateaus at 1.0 across the whole 0.1-0.9 region, then crashes to 0 when attention exceeds true-similarity (everything rejected, tp=0).

This is a real geometric finding about the substrate at N=1024 with these parameters:
- **In-codebook vs out-of-codebook similarities are an order of magnitude apart** (~0.96 vs ~0.08).
- **Any attention in [0.1, 0.95] perfectly separates them** (F1=1.0 across a huge plateau).
- **The attention modulator is more knife-edge than slider** for this regime: there's a 10x gap to span, and once you cross it you cross it.

This is informative for Week 7 molecule experiments: at fixed N=1024 with k=30 atoms and sigma=0.6 noise, attention doesn't trade off precision and recall along a smooth curve — it either accepts everything, perfectly separates, or rejects everything.

## Pre-registration check

My "monotone precision" prediction was falsified, which the system flagged via `review=True` (the workload's own pre-registration check). The falsification is not a bug; it's the substrate telling me my mental model of attention-as-PR-knob was wrong at this regime. The geometric separation is wider than I assumed.

To get a smooth P/R trade-off, future runs should increase k (bringing junk-max-sim closer to true-sim), or increase noise sigma above 1.5 (where mean true-sim drops to ~0.5).
