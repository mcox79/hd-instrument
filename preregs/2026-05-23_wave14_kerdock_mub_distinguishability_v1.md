# Prereg — wave14_kerdock_mub_distinguishability_v1

**Date filed:** 2026-05-23
**Routing source:** notes/strategy_to_exp_dev_MUB_distinguishability_2026-05-23.md
**Drill source:** notes/research_kerdock_mub_stabilizer_drill_2026-05-23.md (test 3.B)
**Counterpart prereg:** preregs/2026-05-23_wave14_kerdock_2design_frame_potential_v2_symplectic_trace.md (3.A)

## Hypothesis

For substrate states drawn from beta_A-class snapshot regimes, the Born-rule
distribution on the Kerdock-MUB family contains MORE than uniform-on-non-native
structure if and only if the substrate carries BBMD-novel structure beyond the
2-design isomorphism.

## Quantity

For 3 substrate-class states {psi_1, psi_2, psi_3}, compute

```
P_{i, k, j} = |<b^{(k)}_j | psi_i>|^2
TV_{i, k}   = 0.5 * sum_j |P_{i, k, j} - 1/N|
```

over the N+1 Kerdock-MUB bases (1 computational + N Galois-ring-exponential MUBs).

## Construction

- N+1 Kerdock-MUBs at N=4096 (m=12) via the Klappenecker-Roetteler 2003
  Galois-ring GR(4, m) exponential construction.
- Galois ring built with an auto-searched basic primitive polynomial over Z_4
  (Hensel lift of the F_2 primitive poly + 2-mask search until x has order
  2^m - 1 in Z_4[x]/h(x)).
- 3 substrate-class states:
  - `vanilla_stab`: a computational-basis state (stabilizer state in B_0).
  - `enriched_kerdock`: a Kerdock-MUB column from a random non-native basis.
  - `haar`: a Haar-random state in C^N.

If beta_A snapshots from v149/v164a/v167 are available on the runner
(`data/exp_*/snapshot.npz` patterns), they should replace these proxies via
a `--use-snapshots` flag (NOT shipped in v1; deferred to v2 if real snapshots
are confirmed available).

## Hard pass / hard fail (from drill 3.B)

- **HARD PASS (BBMD-NOVEL_SIGNATURE_CONFIRMED):** at least one non-native MUB
  shows TV >= max(0.05, 3 * 1/sqrt(N)) on >= 2 of the 3 states.
- **HARD FAIL (VANILLA_STABILIZER):** all non-native MUBs flat within
  1.5 * 1/sqrt(N) across all 3 states.
- **INCONCLUSIVE:** in between (1 state with spike, others flat).

At N=4096: stat_noise = 1/sqrt(N) = 0.01562; HP_threshold = max(0.05, 3 * 0.01562) = 0.05;
HF_threshold = 1.5 * 0.01562 = 0.0234.

## Self-test gate (mandatory before queueing)

1. Build 5 MUBs of C^4 (m=2) via the Galois-ring construction. Verify
   |<b^{(k)}_j | b^{(l)}_i>|^2 == 1/4 to floating-point zero for k != l (10 pairs).
2. Take a stabilizer state in the computational basis. Verify TV vs uniform
   on each of the 4 non-native MUBs is < 1e-10.
3. Take 200 Haar-random states in C^4. Verify mean TV in (0.05, 0.95).

Smoke executed locally 2026-05-23: ALL THREE self-tests pass; m=4 smoke probe
constructs all 17 MUBs (16+1) and computes TVs end-to-end. Verdict semantics
verified.

## Sample sizes / runtime

- N=4096 (m=12), 3 states x 4097 MUBs x 4096 amplitudes = 5.0e7 inner products.
- Numpy einsum-friendly; runtime estimate < 60 min on remote CPU.
- Building Kerdock-MUBs at m=12 is O(N^3) = 6.9e10 GR(4, m) ops; this is the
  dominant cost. Estimated 30-90 min wall-clock at m=12 on remote CPU.
- Total budgeted timeout: 7200 s (2 h).

## Why it matters

3.B is the discriminator between "substrate is a vanilla Clifford-2-design
subgroup" (HARD FAIL outcome) and "substrate carries BBMD-novel structure
beyond the isomorphism" (HARD PASS outcome). Combined with 3.A (F_4 anchor)
the joint outcomes give a 4-way decision table for the substrate-product
narrative.

## Decision log

`notes/exp_dev_decisions_2026-05-23.md` via `append_decision_log.py`.
