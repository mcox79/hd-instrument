# Prereg: substrate_training_n_threshold_sweep_512_8192_v1_gpu

## Anchor
substrate_training_n_threshold_sweep_512_8192_v1_gpu

## Routing
notes/research_drill_substrate_training_n_threshold_3x_2026-06-04.md -- the drill's CHEAP DECISIVE TEST +
N-SWEEP RECOMMENDATION (verbatim bands). GPU (O(N^2) W, N up to 8192, wall-time-bound per drill feasibility).

## Scientific question
Below which N can the cf-RPE substrate-as-training mechanism NOT drive char-LM bigram training? Theory
(3 mechanisms: capacity 0.138N, BCM SNR sqrt(N/M), concentration) predicts N_threshold ~2000-4000 for the
bipolar-outer-product substrate. Sweep N in {512,1024,2048,3072,4096,8192} x {bipolar, continuous} codings,
3 seeds, fixed budget. cf-RPE delta rule; calibrated-temp readout; BPC gap = uniform_nats - trained_nats.
Also tracks substrate pattern diversity per the drill. (Bigram has few distinct contexts ~V, so the true
threshold may be LOWER than the drill's M_eff~500-1000 assumption -- the sweep refines this.)

## Pre-registered bands (BIPOLAR arm; NATS)
HARD-PASS: HP1 [gap@4096>=1.0 AND gap@1024<=0.05] OR HP2 [phase transition gap@4096>=5x gap@2048].
MIDDLE: gap@4096>=0.5 but threshold unclear / no sharp transition.
HARD-FAIL: HF1 [gap@4096<=0.1 AND gap@8192<=0.1 -> no learning] OR HF2 [gap@1024>=0.5*gap@8192 -> N not the axis].
Continuous arm = secondary mitigation comparison (does continuous lower the threshold?).

## Formula self-tests (PROT-022)
1. continuous codebook unit-norm + non-bipolar. 2. heteroassoc recall cos>0.5. 3. cf-RPE shrinks error.
4. uniform nats = ln(V). [ALL PASS]

## Smoke gate
Smoke PASSED on remote GPU (N={256,512}, 2 seeds, 2 codings): self-test green, all cells run, GPU used;
verdict guarded to MIDDLE on reduced grid. Small-N already learns (~1.1 nat gap) -> hints a lower threshold.

## PROT-018 / 019 / 021
NO _nN suffix (N swept; grid declared). timeout 21600s. 3 seeds; partials keyed seed+run_mode.

## Queue
overnight_queue (GPU).
