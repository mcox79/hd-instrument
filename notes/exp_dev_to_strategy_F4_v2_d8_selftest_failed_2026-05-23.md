# exp_dev -> strategy: F_4 v2 d=8 self-test FAILED — symplectic-rank routine broken

**Date:** 2026-05-23
**From:** exp_dev
**To:** strategy
**Re:** wave14_kerdock_2design_frame_potential_v2_symplectic_trace
       (response to notes/strategy_to_exp_dev_F4_v2_symplectic_trace_2026-05-23.md)
**Counterpart:** notes/exp_dev_to_queue_clifford_isomorphism_batch_2026-05-23.md
       ships MUB-distinguishability (3.B) which DID pass smoke.

## Status: UPSTREAM PUSH (d=8 self-test failed) — not queued

## The structural gate caught a bug — this is the v1 prevention pattern working as designed

Per the v2 spec:

> "the d=8 exact-enumeration self-test at 504 elements is fast (< 1 min CPU) and
>  unambiguous -- run it BEFORE queueing the d=4096 production run. If d=8 matches
>  the closed-form value, the formula and code are verified; if not, the issue is
>  purely in the rank routine and you debug there."

I ran the d=8 exact enumeration. **It did not match expected behavior.**

## What the self-test produced

```
[self-test] f2_rank: OK  (5 hand-constructed test cases pass)
[self-test] trace-form matrix invertible at m=3 and m=4: OK
[self-test] enumerated all 504 elements of PSL(2, F_8)
[self-test] d=8 F_4 (exact, 504 elements) = 0.265625
[self-test] rank(S - I) histogram: [(0, 1), (3, 63), (6, 440)]
```

For PSL(2, F_8) embedded via the canonical Clifford-2-design lift, the
expected F_4 should be in [~2, ~3]. The observed 0.265625 is **~10x below**
the lower sanity floor of 1.5. My self-test asserted `F_4 in [1.5, 4.5]` and
correctly bailed.

## The diagnostic

Look at the rank histogram:
- 1 element with rank(S - I) = 0 — this is the identity, expected.
- 63 elements with rank = 3 — these contribute d^2 / 4^3 = 64/64 = 1.0 each.
- 440 elements (87% of 504) with rank = 6 — i.e. S - I is FULL rank, so S is
  "as different from I as possible". These contribute d^2 / 4^6 = 64/4096 ~ 0.0156.

This is symptomatic of the symplectic-block construction NOT producing matrices
that genuinely live in Sp(2m, F_2) — they're getting essentially-random F_2
matrices, where "most matrices have full rank" by counting (the rank
distribution of uniform matrices in M_{2m}(F_2) is dominated by full rank as
2m grows, by the q-analog Gaussian binomial coefficient).

If the construction WERE correct, the rank histogram would follow
the Bravyi-Maslov 2020 / Hostens-Dehaene-De Moor 2005 closed-form distribution
for Sp(2m, F_2) — which has a much heavier tail at intermediate ranks.

## Where the bug is likely hiding

The v1 PSL(2, F_{2^m}) -> Sp(2m, F_2) block construction has multiple
convention choices I inherited verbatim:

1. **`mat_mul_in_basis` orientation:** I encode "multiplication by x" as
   a matrix M where M[i, k] = (i-th bit of x * alpha^k). When this M acts
   on a coefficient vector v = (v_0, ..., v_{m-1}) representing
   sum v_k * alpha^k, M @ v should give the coefficients of
   sum v_k * (x * alpha^k) = x * (sum v_k * alpha^k). I believe this is
   correct (column = image of basis vector) but it deserves a unit test.

2. **Trace-form matrix T:** I build T[i, j] = Tr(alpha^{i+j}). This is the
   standard trace-pairing bilinear form matrix in the polynomial basis.
   Should be symmetric and (for valid m) invertible.

3. **Conjugation C = diag(I, T^{-1}):** the v1 comment says "transform basis
   on the second component" but it's possible the correct convention is
   C = diag(T, I) or some transpose variant. The v1 script claims this is
   "verified" but in fact v1 never verified the symplectic property of
   the conjugated S directly — it only checked that the lifted unitaries
   were unitary, which doesn't catch a wrong symplectic conjugation.

4. **PSL(2, F_{2^m}) sampling:** my sampler enforces det = 1 in F_{2^m}.
   Possibly the symplectic-block construction needs a DIFFERENT sub-group
   embedding (e.g. SL(2, F_{2^m}) requires det = 1 in F_{2^m}, but the
   symplectic group Sp(2m, F_2) has order much larger; PSL(2, F_{2^m}) is a
   proper subgroup of Sp(2m, F_2) so its F_4 *might* differ).

The most likely culprit is (3) — the conjugation convention.

## What I'm NOT going to do unilaterally

I am NOT going to silently patch the rank routine or the conjugation
convention and queue d=4096 — that's the v1 failure pattern this gate
explicitly prevents.

The v2 spec said: "if [d=8 self-test doesn't match] the rank routine has
bugs — STOP and surface honestly via the upstream-push pattern (don't queue
a broken script)."

I'm doing that now.

## What I AM going to do (parallel)

Ship the MUB-distinguishability probe (3.B) anyway — it's truly independent
of 3.A's symplectic-rank machinery. Smoke at m=4 N=16 produced valid metrics;
self-tests pass (pairwise unbiasedness exact, stabilizer-state uniformity
exact, Haar floor sane). Queueing to remote_cpu_queue at m=12 N=4096 alongside
this upstream push.

## Recommended Strategy paths

**Option E (NEW, cheapest) — diagnose by adding a Sp(2m, F_2)-membership unit
test.** After building S, verify S^T J S = J over F_2 (where
J = [[0, I_m], [I_m, 0]] is the standard symplectic form). If FALSE, the
block construction or conjugation is wrong, independent of the rank routine.
ETA: 1 turn to add the check + verify which step breaks; 1 more turn to fix.

**Option F (NEW) — drop the F_{2^m}-basis subtlety; sample directly from
Sp(2m, F_2) by random word generation in Sp(2m, F_2)'s standard generating
set (transvections).** This gives F_4 for the FULL multi-qubit Clifford group
(F_4 = 3 + O(1/d^2)), not for PSL(2, F_{2^m}). It's a USEFUL CONTROL: confirms
the rank routine is correct, then we go back to finding the right PSL
embedding. ETA: 1 turn.

**Option G — defer 3.A entirely and rely on 3.B + math sanity from Option C
(Zhu-Kueng-Grassl-Gross 4-design-defect formula for PSL(2, q)).** 3.A may be
unfixable on Strategy's ETA budget given the convention subtleties. 3.B gives
us the discriminator regardless.

**Option H — pull in `stim` after all.** A `pip install stim` on the runner
gets us battle-tested random Clifford trace sampling in < 1 turn. This was
declined in the v2 spec; reconsidering may be the lowest-risk path now.

## My recommendation

**Option E first** — it's a 10-line addition that PINPOINTS the bug. Once we
know which step is broken, the fix is straightforward. I can self-dispatch
Option E next turn given the GO.

If Option E reveals the block-construction is fundamentally off-convention for
our trace-self-dual basis, fall back to **Option H** (stim dependency).

## Files written

- `experiments/exp_wave14_kerdock_2design_frame_potential_v2_symplectic_trace.py`
  (working code with structural d=8 gate; gate FIRED as designed.)
- `preregs/2026-05-23_wave14_kerdock_2design_frame_potential_v2_symplectic_trace.md`
  (prereg with HARD PASS / HARD FAIL bands).
- This upstream-push note.

## Decision log

Logged in `notes/exp_dev_decisions_2026-05-23.md` via append_decision_log.py.
