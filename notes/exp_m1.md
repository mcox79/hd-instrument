# Experiment M1: single (role, filler) binding fidelity

**Date:** 2026-05-16
**Phase:** Week 7 molecule experiments

## Hypothesis

For FHRR with complex unit-magnitude atoms, bind(role, filler) followed by unbind(., role) recovers the filler exactly (within float roundoff). 100 random trials should all give similarity > 0.999.

## Falsification

Any trial with similarity < 0.999 means the bind/unbind algebra has drift beyond float roundoff.

## Result (2026-05-16)

| Check | Predicted | Observed | Outcome |
|---|---|---|---|
| Perfect recoveries (sim > 0.999) | 100/100 | 100/100 | confirmed |
| Min sim across all trials | > 0.999 | 1.000000 | confirmed |
| Mean sim | ~ 1.0 | 1.000 | confirmed |

## Takeaway

FHRR bind/unbind is exact within float precision — no roundoff drift visible even across 100 trials. The complex unit-magnitude algebra is well-conditioned. This is the foundation everything else stands on.
