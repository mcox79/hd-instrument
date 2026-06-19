# Pre-registration: wave14r_multihop_hybrid_v1

Date: 2026-05-21
Status: Pre-registered, gated
Priority: Strategy push (R8 C1 — substrate-coherent hybrid)
Author: experiment_dev session, pipeline tick 60

## Why

R8 C1 hybrid keeps BSC storage (M = sign(sum subj*rel*obj)) but executes the
chain in FHRR — boundary conversions inject discretization noise (~Berry-Esseen
bound per Frady-Sommer signal detection) but preserve no-closure benefit during
the continuous-multiply chain.

Companion to A1 (wave14r_multihop_FHRR_v1, which landed MULTIHOP_FHRR_KILLED).
C1 tests whether the rescue can land with BSC storage preserved — substrate-
coherent variant that doesn't invalidate existing experiments.

R8 predicted 40-55% acc_50 for C1; A1 was killed already, so C1 is the next
rescue candidate.

## Mechanism

- Storage: BSC entities + relations (bipolar +/-1); M = sign(sum BSC subj*rel*obj).
- Per-hop unbind: BSC probe = M * (current * rel), then convert probe to FHRR
  phasor via z_j = exp(i*pi*probe_j/2) (= ±i for bipolar ±1).
- Cleanup: argmax over FHRR-converted entity codebook by |<entity_fhrr, probe_fhrr>|.
  Continuous cleanup avoids the discrete-codebook collision pathology.

## Verdict labels

- MULTIHOP_HYBRID_50HOP_VALIDATED (acc_50 >= 0.80)
- MULTIHOP_HYBRID_PARTIAL_AT_<D> (0.40 <= acc_50 < 0.80)
- MULTIHOP_HYBRID_KILLED (acc_50 < 0.40)
- MULTIHOP_HYBRID_INCONCLUSIVE

## Pre-armed rescues (PROT-004 + feedback-rehabilitation-after-rejection)

If MULTIHOP_HYBRID_KILLED:
1. B1 modern Hopfield exponential cleanup
2. Smaller NUM_FACTS to lift depth ceiling
3. Larger N (Goldstone-mode prediction: noise ~ sqrt(K)/N)
4. Sparser relation codebook (orthogonal-by-construction)
5. Per-hop M re-derivation with current factbase subset only

## Runtime: ~10 min full multi-seed
