# Pre-reg: exp_resonator_verifier_readout_v1

Author: hdi_exp_dev | Date: 2026-07-07 | Anchor: resonator_verifier_readout_v1

## Question
On the resonator K4 factorization, can a SMARTER read-out (reconstruction verifier) harvest the
already-reached correct answer into the accepted answer -- lifting K4 success past the 0.50 bar the
PLURALITY read-out missed (0.464) -- WITHOUT any new decode mechanism?

## Lever (ONLY the aggregator changes)
Glauber-dither + R=10 restart machinery HELD IDENTICAL (decode_trial verbatim port). Replace plurality
vote with: SCORE each of the R candidate tuples by reconstruction fidelity to the input probe s
(bind candidate factors back -> s_hat; normalized real inner product Re(<s, s_hat>)/N) and pick argmax.
Uses only s (the input being factored) + codebooks; NEVER the true index tuple.

## Why it should work (THEORETICAL@normalized-phasor-inner-product)
True tuple reconstructs s exactly -> score = 1.0. Wrong tuple differs in >=1 factor -> s_hat = s x
independent random phasor product -> score ~ N(0, 1/N), magnitude ~1/sqrt(N) ~ 0.0156 at N=4096. So
whenever truth is among the R candidates (prob = oracle_any), verifier picks it near-certainly ->
verifier harvest ~= oracle_any. VET measured oracle_any=0.80 at T0=0.35 -> expected harvest ~0.80 >> 0.50.

## Bands (pre-registered BEFORE full)
- HARD-PASS: K4 verifier harvest >= 0.50 AND verifier > plurality + 0.05 AND K3 baseline in [0.40,0.95].
  Clears the bar plurality missed -> residual gap WAS aggregation-loss (confirms VET diagnostic).
- HARD-FAIL: verifier <= plurality + 0.02 (no material lift). If a reconstruction verifier CANNOT beat
  plurality the gap is NOT aggregation-loss -> REFUTES the VET diagnostic. Report honestly, do not force.
- MIDDLE: plurality+0.05 < verifier < 0.50 (real lift, does not clear bar).
- INTEGRITY (HARD_FAIL override): verifier harvest <= oracle_any per arm (verifier cannot invent truth
  absent from candidates). Any violation => read-out bug => HARD_FAIL_INVARIANT.

## Formula self-test (PASS)
verifier true-tuple score = 1.0000; wrong-tuple = -0.0005 (N=4096); argmax recovers truth when present;
cannot recover truth when absent. 6 checks pass.

## Compute architecture
Class: (b) sequential-CPU with justification. decode_trial has genuine sequential dependency (coupled
alternating-projection iterations, step it depends on it-1); it IS the mechanism under test (bit-faithful
numpy port of the GPU resonator). Verifier read-out adds ~10 length-N phasor products per trial
(negligible). Full wall ~= 1215s baseline (measured for the plurality cell at identical grid) + small
verifier overhead. Storage: no_storage (decode-only). No batching gain available (sequential recurrence).

## SCHEMA-VET fields
- arms_differ_verified: true (verifier winners != plurality winners; smoke lift +0.367 at K4 T0=0.10)
- final_metrics_atomicity: tmp_replace (write_metrics) + per-seed write_partial
- cardinality_ok: EXPECTED_N_UNITS = 3 seeds x 2 K x 5 T0 = 30 glauber arms (+ 2 baseline); verdict
  raises HARD_FAIL_CARDINALITY if len(per_seed) != 3.
- crlb_floor_computed / discriminator_reachability: verifier <= oracle_any(~0.80); HARD_PASS 0.50 is on
  the achievable side of the 0.80 ceiling -> reachable = true.
- baseline_in_band: K3 baseline ~0.70 in [0.40,0.95]; K4 baseline <=0.35 (not saturated). Verified smoke.
- discriminator survives scale: smoke runs at FULL N=4096 M=30 K=4 (only TR + seed count reduced);
  verifier discrimination SHARPENS with N (wrong recon ~1/sqrt(N)).
- HP_SCOPE: {K4_verifier_T*: [HARD_PASS_0.50, LIFT_0.05], K3_baseline: [POSITIVE_CONTROL_ONLY]}
- calibration_check: default_ok_for_this_regime (reconstruction threshold is parameter-free argmax).
- positive_control_arms: K3 baseline reproduces GPU-port ~0.70 (Gate D); K4 baseline ~0.14 not saturated.
- functional_requirements: "harvest the reached-but-outvoted correct tuple" -> reconstruction verifier
  (new read-out; no existing primitive maps to argmax-by-reconstruction over restart candidates).
- start_marker_written / crash_diagnostic_present / heartbeat_present: true.
- progress_logging: print_flush_true (+ heartbeat per arm).
- cell_chunked: false (3-seed loop with per-seed write_partial + resumable_seeds checkpoint/resume).

## Smoke result (seed 3, TR=30, full N=4096) -- HARD_PASS
K4: verifier {T0.10=0.867, T0.20=0.800, T0.35=0.800, T0.50=0.800} == oracle_any at EVERY arm;
plurality {0.500, 0.400, 0.533, 0.433}. Lift +0.27 to +0.37. Zero invariant violations. K3 baseline
0.700, K4 baseline 0.033. Verifier harvests the FULL oracle ceiling exactly as theorized.

## Dispatch
FULL -> remote_cpu_queue (CPU/numpy decode-only; ~20min). Seeds [3,7,13] (reuse VET seeds). timeout 2700s.
