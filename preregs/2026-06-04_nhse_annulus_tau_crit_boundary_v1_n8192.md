# Prereg: nhse_annulus_tau_crit_boundary_v1_n8192

## Anchor
nhse_annulus_tau_crit_boundary_v1_n8192

## Priority
A (NHSE-annulus handoff Anchor 2; resolves the most-uncertain framework element: tau_crit + transition
continuity). Complements Anchor 1 (tau-sweep).

## Scientific question
Dense 6-cell sweep of the predicted disk-to-annulus transition zone (build knob t -> tau_actual ~
{0.21,0.27,0.33,0.39,0.46,0.52}). Is the transition CONTINUOUS (smooth crossover; NHSE) or
DISCONTINUOUS (jump; first-order critical NHSE)? Where is tau_crit? Framework predicts continuous,
tau_crit ~ 0.25-0.45. Same controlled-asymmetry build + kappa_3 gamma_emp + spectral annulus radii.

## Pre-registered bands (continuity / tau_crit)
HARD-PASS: gamma_emp monotone (5% slack) AND continuous (max consecutive-cell gamma ratio < 3.0) AND
tau_crit (first tau with gamma >= 2.0) in [0.25, 0.45].
MIDDLE: monotone + continuous but tau_crit outside [0.25,0.45], OR mild jump (ratio 3.0-5.0).
HARD-FAIL: discontinuous jump (max ratio > 5.0 -> first-order, refutes smooth exponential) OR
non-monotone OR no transition (gamma flat: max/min < 1.5 across the zone).

## Formula self-tests (PROT-022)
Inherited from Anchor 1: tau_actual map (t=0.50->0.707; t=0.71->0.926); NHSE prediction; exp-fit
recovery. [ALL PASS in smoke]

## N-suffix binding (PROT-018)
anchor _n8192; production N = 8192 (kappa_3). N_EIG=512 for the annulus eigendecomposition.

## Timeout
6 tau cells x (kappa_3 + eigvals N_EIG=512) x 5 seeds. PROT-019 floor for _n8192: 21600s.

## Smoke gate
Smoke PASSED (N=256, 2 seeds): tau_actual spans the 0.21-0.52 transition zone; instrumentation
non-null; self-tests pass. Low gamma at smoke is small-N; full N=8192 resolves tau_crit.

## Queue
remote_cpu_queue (pure numpy; CPU).
