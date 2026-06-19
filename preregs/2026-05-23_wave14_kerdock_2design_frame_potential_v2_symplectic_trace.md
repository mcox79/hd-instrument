# Prereg — wave14_kerdock_2design_frame_potential_v2_symplectic_trace

**Date filed:** 2026-05-23
**Routing source:** notes/strategy_to_exp_dev_F4_v2_symplectic_trace_2026-05-23.md
**Drill source:** notes/research_kerdock_mub_stabilizer_drill_2026-05-23.md (test 3.A)
**Counterpart prereg:** preregs/2026-05-23_wave14_kerdock_mub_distinguishability_v1.md (3.B)

## STATUS: NOT QUEUED — d=8 self-test gate FIRED.

See `notes/exp_dev_to_strategy_F4_v2_d8_selftest_failed_2026-05-23.md` for the
upstream-push. This prereg documents the intended-design parameters for
future re-staging.

## Hypothesis

The substrate's Kerdock-anchored PSL(2, F_{2^m}) Clifford-subgroup is a
unitary 2-design iff F_4 = E|Tr(U_S)|^4 = 2 + O(1/d^2). The Bravyi-Maslov
formula |Tr(U_S)|^2 = d / 2^{rank(S - I)} reduces this to a symplectic-rank
expectation:

```
F_4 = E_{S ~ uniform PSL(2, F_{2^m})} [ d^2 / 2^{2 * rank(S - I)} ]
```

## Hard pass / hard fail (unchanged from drill 3.A)

- **HARD PASS (2-design):** F_4 in [1.90, 2.10] (Haar; within +/-5% of 2.0).
- **HARD PASS (3-design):** F_4 in [2.85, 3.15] (Clifford; within +/-5% of 3.0).
- **HARD FAIL:** F_4 outside BOTH bands.
- **INCONCLUSIVE:** Haar baseline empirical F_4 deviates from 2.0 by > 0.30.

## Algorithm

1. Sample S in PSL(2, F_{2^m}) uniformly (size: q*(q^2 - 1) where q = 2^m).
2. Build the 2m x 2m F_2 block matrix S_g = [[M_a, M_b], [M_c, M_d]].
3. Conjugate to standard symplectic form: S = C @ S_g @ C^{-1}, C = diag(I, T^{-1}).
4. Compute rank_F_2(S - I) by Gaussian elimination.
5. Accumulate d^2 / 2^{2 * rank(S - I)} into a running mean.

n=2000 samples at m=4 (d=16) for smoke; n=2000 at m=12 (d=4096) for production.

## Self-test gate (MANDATORY before queueing)

1. f2_rank correctness on 5 hand-constructed test cases (I, 0, duplicate-row,
   lower-triangular full-rank, rank-deficient sum).
2. Trace-form matrix invertibility at m=3 and m=4.
3. **d=8 exact enumeration of all 504 PSL(2, F_8) elements**, computing F_4
   via the rank formula. Sanity-band [1.5, 4.5] (wider than production bands
   to detect catastrophic rank-routine bugs).
4. Haar baseline at d=16 n=1000: |F_4 - 2.0| < 0.30.

## What happened on 2026-05-23 self-test execution

- f2_rank: PASS (after correcting my hand-computed test cases).
- trace-form invertible: PASS at m=3 and m=4.
- **d=8 enumeration: F_4 = 0.265625, FAIL** (way below sanity band [1.5, 4.5]).
- Rank histogram: 1 elt rank=0 (identity), 63 elts rank=3, 440 elts rank=6.

The bulk of elements (87%) have full rank in S - I, which contributes ~0.0156
per element. This pattern is consistent with the symplectic-block construction
producing essentially-random F_2 matrices, not genuinely Sp(2m, F_2) elements.

Probable bug: conjugation convention C = diag(I, T^{-1}) may have wrong sign
or transpose vs. the trace-self-dual basis. NOT a rank-routine bug; the
unit tests passed.

## Next steps (deferred to strategy decision)

See upstream-push for Options E (Sp-membership unit test), F (random Sp word),
G (defer 3.A), H (pull in stim).

## Sample sizes / runtime (intended if shipped)

- d=4096 (m=12), n=2000 PSL samples.
- Per-sample: build 24x24 F_2 block matrix + rank via F_2 Gaussian elim.
  Cost: O(m^3) per rank = O(1728) bit-ops per sample. Pure numpy.
- Total: estimated < 20 min CPU. Lane: remote_cpu_queue.
- Plus Haar baseline at d=4096 n=500 for direct comparison (~5 min).
- Timeout if re-queued: 3600 s.

## Decision log

`notes/exp_dev_decisions_2026-05-23.md` via `append_decision_log.py`.
