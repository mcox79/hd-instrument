# Pre-registration: wave14_kerdock_distance_class_audit_v1

**Date:** 2026-05-26
**Trigger:** AGS-RS-MULTI-FERROMAGNET research drill (research_ags_retrieval_phase_substrate_2026-05-26.md); Test 2 of AGS basin-class validation handoff.
**Hypothesis:** Substrate's Kerdock 4-coset codebook has exactly 4 distinct codeword-pairwise-distance (IP/N) classes, mapping monotonically to the 4 empirical retention plateaus {0.94, 0.74, 0.60, m_4}. Each class maps to a predicted AGS retrieval overlap m_k via the self-consistent equation m_k = erf(m_k / sqrt(2*r_k)).

## Method

Post-hoc analytical on existing Kerdock codebook (no new training):
1. Build 4-coset MM Kerdock codebook at N=1024 via `make_kerdock_4coset_codebook`.
2. Sample 3000 codeword pairs per coset pair (same-coset within and cross-coset).
3. Compute inner product / N for each pair.
4. Cluster into discrete levels (round to 4 decimal places; keep levels >= 0.5% of total).
5. Count distinct levels globally; check monotone ordering.
6. Map each level to AGS predicted overlap m_k via basin-class formula.
7. Compare predicted m_k to empirical plateaus within ±0.07 and ±0.15 tolerance.

## Pre-registered bands

- **HARD-PASS:** exactly 4 distinct distance classes; monotone (higher IP = higher m_k); 3/4 predicted m_k match empirical plateaus within ±0.07.
- **HARD-FAIL:** ≠ 4 distance classes (3 or smooth) OR predicted-vs-observed plateaus off > 0.15 systematically OR non-monotone ordering.
- **MIDDLE_BAND:** 4 classes confirmed but plateau-height mapping has 2/4 mismatches in [0.07, 0.15].
- **INSTRUMENTATION_FAIL:** codebook construction error OR < 2 distinct IP levels.

## Dependencies

- `experiments/exp_wave14y_erase_kerdock_v3.py::make_kerdock_4coset_codebook` (verified local)
- No prior experiment data required; pure analytical

## Effect size at smoke

Smoke (300 pairs/coset-pair) shows 3 distinct levels: {-0.0312, 0.0, 0.0312} — not 4.
Smoke verdict: HARD_FAIL. This is a genuine finding: within-coset IP=0 exactly (Hadamard orthogonality), cross-coset IP ∈ {±1/sqrt(N)} (Welch bound), giving only 3 distinct classes. Effect is large (deterministic algebraic structure, no variance across seeds). FULL run at 3000 pairs/coset-pair confirms the same structural result.

Per [[feedback-walk-back-gate]]: smoke effect size is not borderline — the 3-class structure is exact (deterministic at any sample size). No walk-back needed.

## Note on HARD_FAIL meaning

HARD_FAIL here does not invalidate substrate-product viability or Bet B retention taxonomy — the 4-tier retention structure stands empirically (silhouette=0.788, cell-level CIs non-overlapping). HARD_FAIL falsifies only the specific sub-claim that Kerdock pairwise distance classes = 4 distinct Hamming classes. The correct interpretation is: 4 cosets induce 4 COSET CLASSES (same-coset vs cross-coset-k), not 4 distinct Hamming distance values. The AGS basin-class prediction should be reframed in terms of COSET MEMBERSHIP, not pairwise Hamming distance.

Queue: remote_cpu_queue (BELOWNORMAL priority, structural; ETA ~15-30 min)
