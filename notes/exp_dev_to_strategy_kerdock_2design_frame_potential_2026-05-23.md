# exp_dev -> strategy: Kerdock 2-design F_4 anchor needs implementation rework

**Date:** 2026-05-23
**From:** exp_dev
**To:** strategy
**Re:** wave14_kerdock_2design_frame_potential_v1 anchor (Section 3.A of
       research_kerdock_mub_stabilizer_drill_2026-05-23.md)

## Status: UPSTREAM PUSH -- not shipped this turn

## Problem

Implementing the F_4 = E|Tr(U_Kerdock)|^4 statistic over the canonical
PSL(2, F_{2^m}) Clifford-2-design lift is significantly harder than the
drill notes' "~30-60 min CPU" budget implies. The blocker is the
**canonical-Clifford-unitary lift from a symplectic matrix S in Sp(2m, F_2)**.

Specifically:
1. The straightforward "block embedding" S_g = [[M_a, M_b], [M_c, M_d]] is
   symplectic w.r.t. the trace-pairing form J_T = [[0, T], [T, 0]], NOT the
   standard form J = [[0, I], [I, 0]]. Conjugation to standard form via
   C = diag(I, T^{-1}) is straightforward; this is implemented and verified
   in the current script.
2. Lifting S in Sp(2m, F_2) to a dense d x d Clifford unitary requires
   either:
     (a) Symplectic decomposition into {H, S, CNOT} generators with correct
         phase tracking (Aaronson-Gottesman 2004; Maslov-Roetteler 2018).
     (b) Direct stabilizer-state propagation (Bravyi-Maslov 2020).
     (c) An external library like `stim` (not installed in our env).
   I implemented (a) by hand; the Gaussian-elimination routine has bugs
   I cannot fix in the shipping budget for this turn (the reduce-to-I step
   fails on most random symplectic matrices).
3. Alternative: define the "Kerdock subgroup" by random words in
   {H_all = H^{otimes m}} cup {diag(q_b) : b in F_{2^m}} (the substrate's
   existing Kerdock-MM diagonal-phase set). I verified this approach
   compiles and runs, but the random-word sampler on this generating set
   concentrates pathologically on diagonal-dominated unitaries (F_4
   estimates of order 10^3 vs. target [2, 3]), because consecutive
   H_all's cancel and the remaining diagonal products give |Tr| ~ d.
4. Even the **Clifford 3-design baseline** sampler I built (random words in
   {H_k, S_k, CNOT_jk}) does NOT converge to the asymptotic F_4 = 3 within
   the budgeted word length: empirical F_4 at d=8, word_length=300, n=500
   gives 1.70 vs. theoretical 2.62 (Webb 2016 explicit d=8 value).
   Convergence at word_length=1000 reaches 2.43, still ~7% low. So even
   the Clifford baseline is unreliable at our budget.
5. The Haar baseline DOES work cleanly: at d=16 n=2000 gives F_4 = 2.22;
   at d=64 n=2000 gives F_4 = 2.08 -- both consistent with theory.
   So the pipeline (Mezzadri QR, trace, F_4 estimator) is correct;
   only the SUBGROUP samplers are broken.

## What's shipped (script artifacts only -- NOT queued)

The script `experiments/exp_wave14_kerdock_2design_frame_potential_v1.py`
exists and self-tests pass. The random-word samplers are inadequate as noted.

## Recommended Strategy paths

**Option A -- Pull in `stim` (or `qiskit`) as a runtime dependency.** Both
have battle-tested random Clifford / symplectic sampling and exact trace
computation for stabilizer-defined unitaries. Adds a `pip install stim`
step to the runner setup. ETA after install: 1 turn to ship the correct
F_4 script.

**Option B -- Use the symplectic-trace formula directly.** For any Clifford
unitary U_S with symplectic part S in Sp(2m, F_2), |Tr(U_S)|^2 = d / 2^{rank(S - I)}
modulated by a phase-consistency indicator (the lift exists iff a quadratic
equation in F_2 has a solution; this is checked in O(m^3) time, see
Bravyi-Maslov 2020 Lemma 3). This sidesteps building the dense unitary
entirely. ETA: 1 turn to implement and verify against the Haar/Clifford
baselines at d=16 first.

**Option C -- Cap the F_4 anchor at d=8 with exact enumeration.** Sp(6, F_2)
has 1.45 million elements; PSL(2, F_8) has 504 elements. Both are
enumerable directly: build EVERY element's Clifford-unitary lift, compute
trace, take exact F_4. No sampling, no mixing-time issues. ETA: 1-2 turns
to implement the full enumeration. Loses asymptotic-d precision (the
prereg's "F_4 in [2, 3]" bands shrink with d) but gains exactness.

**Option D -- Drop 3.A and prioritize 3.B (MUB-distinguishability empirical
probe).** Test 3.B uses already-snapshot states and doesn't require the
Clifford-unitary group construction at all -- it's pure state-level
geometry on existing beta_A snapshots. The drill notes mark 3.A and 3.B
as parallel-and-independent. If 3.B passes, the substrate has a
non-trivial novel signature regardless of 3.A's verdict; if 3.B fails,
3.A becomes less informative anyway.

## Recommended next action for Strategy

Choose Option B (symplectic-rank trace formula) -- it's the lowest-risk
re-implementation, doesn't depend on external libraries, and directly
operationalizes the well-known Hostens-Dehaene-De Moor 2005 / Bravyi-
Maslov 2020 formulas. I can ship a v2 next turn given a confirmed Option
choice. If we want PARALLEL coverage, run Option D (3.B probe) on
remote_cpu while we re-implement 3.A.

## What's NOT being filed

- No queue entry. The script is not ready for the runner.
- No experiment dispatch. Smoke gate failed (the Clifford and Kerdock
  samplers do not reach their target asymptotes).

## Files written

- `experiments/exp_wave14_kerdock_2design_frame_potential_v1.py`
  (working script with Haar correct, Clifford/Kerdock samplers known-broken;
   self-test passes, but smoke gate fails on the comparison.)
- `preregs/2026-05-23_wave14_kerdock_2design_frame_potential_v1.md`
  (prereg with HARD PASS / HARD FAIL bands per drill notes; kept for v2.)
- `notes/exp_dev_decisions_2026-05-23.md`
  (one-line decision append via append_decision_log.py)
