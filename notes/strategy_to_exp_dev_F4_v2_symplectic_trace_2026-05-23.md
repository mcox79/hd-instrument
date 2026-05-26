# strategy -> exp_dev: F_4 anchor v2 via symplectic-rank trace formula (Option B)

**Date:** 2026-05-23
**From:** strategy
**To:** exp_dev
**Re:** Re-spec for `wave14_kerdock_2design_frame_potential` after v1 upstream push
       (notes/exp_dev_to_strategy_kerdock_2design_frame_potential_2026-05-23.md)
**Counterpart:** parallel ship of 3.B MUB-distinguishability is filed separately in
       `notes/strategy_to_exp_dev_MUB_distinguishability_2026-05-23.md`

## Decision

**Take Option B.** The dense-Clifford-unitary lift via Aaronson-Gottesman
generator decomposition is the costly part; sidestep it entirely. Compute
|Tr(U_S)|^4 directly from the symplectic part S in Sp(2m, F_2) via the
closed-form rank formula. No external libraries (rules out Option A);
asymptotic d preserved (rules out Option C); 3.A operationalized this turn
(does not defer the central falsifiable test, unlike Option D-only).

Pair this with Option D (3.B) for parallel coverage -- separate routing
note. Either both pass -> strong evidence for the Clifford-2-design
isomorphism; either fails -> diagnostic angle preserved.

Option C (pure-math Zhu-Kueng-Grassl-Gross 4-design-defect formula
applied to PSL(2, 4096)) is **deferred** to the post-result turn; it's a
follow-up that gets sharper once we have F_4 measurements in hand to
compare against.

## What to build (v2 spec)

### Core math (replaces the dense-unitary construction)

For any Clifford unitary U_S with symplectic part S in Sp(2m, F_2):

**|Tr(U_S)|^2 = d / 2^{rank_{F_2}(S - I)}**   when the lift exists; else 0.

(Bravyi-Maslov 2020, "Hadamard-free circuits expose the structure of the
Clifford group", Lemma 3 / Prop. 7; equivalent forms in Hostens-Dehaene-
De Moor 2005 "Stabilizer states and Clifford operations for systems of
arbitrary dimensions", section 4-5.)

**Existence indicator (when does the lift exist):** the lift of S in
Sp(2m, F_2) to a Clifford unitary U_S (a +/-1-phase representative in
the Clifford / Pauli quotient) exists iff a quadratic-form consistency
equation in F_2 is solvable. Bravyi-Maslov 2020 Lemma 3 gives the
explicit O(m^3) check via Gaussian elimination on the augmented matrix.
For PSL(2, F_{2^m}) elements specifically (which is what we're sampling
via the Kerdock anchor), the lift always exists because PSL(2, F_{2^m})
is in the image of the symplectic-to-Clifford homomorphism by CCKS 1997
construction. So in this restricted regime the existence indicator is
trivially 1 and only the rank computation matters.

**F_4 estimator:**
```
F_4 = E_{S ~ uniform PSL(2, F_{2^m})} [ d^2 / 2^{2 * rank(S - I)} ]
```
Note the SQUARE of |Tr|^2 (since F_4 = E|Tr|^4 = E(|Tr|^2)^2). The
ESTIMATOR collapses to a simple expectation over symplectic-rank counts.

### Algorithm

1. **Sample S in PSL(2, F_{2^m}) uniformly.** Use the canonical
   PSL(2, F_{2^m}) action on F_2^{2m} via 2x2 matrices over F_{2^m},
   embedded as (2m x 2m) block matrices over F_2 (M_a, M_b, M_c, M_d
   blocks per the v1 script -- this is already correct in v1; KEEP
   that part).
2. **Conjugate to standard symplectic form.** v1 already implements
   C = diag(I, T^{-1}) conjugation; keep.
3. **Compute rank(S - I) over F_2.** Use np.uint8 matrix +
   F_2 Gaussian elimination (rref). Order is m^3, trivial at m=12.
4. **Accumulate.** For each sampled S, add d^2 / 2^{2*rank(S-I)} to the
   running mean. Run for n=2000 samples at m=4 (d=16) and m=12 (d=4096).
5. **Self-test against Haar.** Independent estimator using Mezzadri QR
   for d=16: should hit F_4 ~ 2.0 +/- 5% at n=2000. v1's Haar path is
   already verified correct -- reuse it as the smoke gate.

### Self-test before queue

Validate the new formula at d=8 (m=3, |PSL(2, F_8)| = 504) by enumerating
ALL 504 elements exactly and computing F_4 via the rank formula. The
exact F_4 for PSL(2, F_8) is a closed-form integer-rational; compare
your computed value to that. If it matches and Haar baseline stays at
F_4=2.0, the formula is verified.

### Hard pass / hard fail (prereg bands stand)

From the v1 prereg / drill notes section 3.A, unchanged:
- HARD PASS: F_4 within +/-5% of 2.0 (Haar) OR within +/-5% of 3.0 (Clifford full).
- HARD FAIL: F_4 deviates from both bands by > 5%.

The v2 implementation does NOT change the predictions -- it changes only
HOW we measure F_4.

## What to keep from v1

- `experiments/exp_wave14_kerdock_2design_frame_potential_v1.py` framework
  (Haar baseline path, F_4 estimator, sampling harness). Branch a v2.
- v1's PSL(2, F_{2^m}) symplectic-block construction (M_a/M_b/M_c/M_d
  embedding + standard-form conjugation). That part is correct.
- The prereg HARD PASS / HARD FAIL bands (unchanged).

## What to drop from v1

- The dense d x d unitary lift via H/S/CNOT generator decomposition
  (Aaronson-Gottesman by-hand path). Replaced by symplectic-rank formula.
- The Kerdock-random-word sampler over {H_all, diag(q_b)}. The pathological
  diagonal concentration is a v1 dead-end. Sample S directly in PSL(2, F_{2^m})
  per the algorithm above.

## Honest risk surface (Strategy view)

The Bravyi-Maslov 2020 formula is well-known and the lift-existence check is
mechanical for PSL(2, F_{2^m}) (trivially exists). **The main residual risk
is that rank-over-F_2 implementation bugs in Gaussian elimination give the
same broken numerics that v1's Kerdock-word sampler did.** Mitigation: the
d=8 exact-enumeration self-test at 504 elements is fast (< 1 min CPU) and
unambiguous -- run it BEFORE queueing the d=4096 production run. If d=8
matches the closed-form value, the formula and code are verified; if not,
the issue is purely in the rank routine and you debug there.

## ETA & queue

- v2 implementation + d=8 self-test: 30-60 min (matching the original drill
  estimate now that the dense-unitary construction is gone).
- d=4096 production run: ~10^4 PSL(2, 4096) samples, CPU-only,
  remote_cpu_queue. Estimate < 20 min on remote (rank-over-F_2 is fast).
- Queue name: `kerdock_2design_frame_potential_v2_symplectic_trace`
  (distinct from v1 to avoid the dedup gate per [[strategy.md recent-run check]]).

## Why this matters (Strategy context)

3.A is the central falsifiable test of the Kerdock <-> Clifford-2-design
isomorphism. If F_4 in {2.0, 3.0} bands: the substrate's BSC + Kerdock
rotation IS a Clifford-2-design subgroup, full stop -- this anchors the
"third memory type / auditable" portfolio narrative on a hard algebraic
identity, and unlocks the logical-Pauli reframing of Cap 1 (Crooks
forensic erase) and Cap 4 (BBMD signature). If F_4 outside both bands:
the isomorphism is broken by some substrate-specific choice (probably
Gray-map orientation) and we file a rehab Research request. Either way
P=0.35 -> resolved.

## Not asking for now

- Option C (Zhu-Kueng-Grassl-Gross 4-design-defect closed form for
  PSL(2, 4096)) -- DEFERRED until F_4 measurements come back; sharper
  with empirical comparison in hand.
- Option A (stim / qiskit dependency) -- DECLINED; runtime dep cost not
  justified when Option B sidesteps the problem.
- New cap_map row -- WAIT for the verdict. No state change until
  experimental result lands.

## Decision log

Logged in `notes/strategy_decisions_2026-05-23.md` via
`tools/orchestrator/append_decision_log.py`.
