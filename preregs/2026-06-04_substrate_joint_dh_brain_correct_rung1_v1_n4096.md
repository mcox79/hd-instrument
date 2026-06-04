# Prereg: substrate_joint_dh_brain_correct_rung1_v1_n4096

## Anchor
substrate_joint_dh_brain_correct_rung1_v1_n4096

## Priority
A (Research joint D+H routing; brain-correct substrate-as-training-mechanism rescue; CPU rung-1 now
Exp-Dev scope per corrected routing matrix [[feedback-routings-direct-to-exp-dev]])

## Scientific question
Can continuous-float32 substrate + Hebbian core + cf rank-1 RPE (no-cache) + sparse top-1
multiplicative gating train a tiny char-LM at rung-1 where the bipolar-additive-PCGrad design got zero
converged seeds? 5 arms x 5 seeds: A(K=1 Hebbian baseline) / B(cf-RPE alone) / C(sparse gating alone)
/ D(joint K=4) / E(joint K=8). Readout is temperature-calibrated (per the readout-artifact finding).

## Pre-registered bands (joint arms D/E headline; A/B/C discriminate the levers)
HARD-PASS (D or E): >=4/5 seeds converge to val_loss < 3.5 bits/char by step 500 AND mean update-norm
>= 0.80 x Arm-A baseline AND router entropy > log(2) bits AND capacity alpha < alpha_c throughout.
MIDDLE: 2-3/5 seeds converge OR norm ratio in [0.40,0.80) OR entropy in [0.5, log(2)].
HARD-FAIL: mean norm < 0.10 x baseline (gating collapse) OR 0-1/5 converge OR norm oscillation > 3x
mean OR capacity exceeds alpha_c.

## Three structural mitigations (per routing)
1. No-cache cf: v = W@ctx recomputed every step (v_old never cached). 2. Capacity tracking: alpha =
distinct-contexts/N every step. 3. Router entropy guard: Shazeer noise on gating router; entropy tracked.

## KNOWN design gap (surfaced to Research)
The gating arms (C/D/E) currently have all K channels modulate the SAME base update, so top-1 routing
either shrinks norm or is a near-no-op vs the ungated counterpart -- so C/D/E may not cleanly
DISCRIMINATE gating's value this version. The cf-RPE + continuous-float32 levers (A vs B vs D) ARE
validly tested. Gating-channels-propose-distinct-updates redesign pending (Research joint D+H update
routing). Shipping now to get the cf-RPE/float32 signal; gating arms are exploratory.

## Formula self-tests (PROT-022)
float32 codebook non-bipolar; heteroassoc recall cosine>0.5; cf-RPE delta reduces error; sparse top-1
entropy < log2(K); log(2)=0.6931. [ALL PASS in smoke]

## N-suffix binding (PROT-018)
anchor _n4096; substrate N_DIM = 4096 in full. 5 seeds (PROT-021).

## Timeout
CPU; est ~1-1.5h (5 arms x 5 seeds x 1000 steps batched). PROT-019 floor for _n4096: 14400s.

## Smoke gate
Smoke PASSED (N=256, 2 seeds): all 5 arms run; instrumentation (norm/entropy/alpha/calibrated-BPC)
non-null. Near-uniform BPC at smoke is the N=256 capacity limit, not a fault; full N=4096 is the test.

## Queue
remote_cpu_queue (CPU; pure numpy).
