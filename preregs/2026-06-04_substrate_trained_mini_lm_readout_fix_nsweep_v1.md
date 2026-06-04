# Prereg: substrate_trained_mini_lm_readout_fix_nsweep_v1

## Anchor
substrate_trained_mini_lm_readout_fix_nsweep_v1

## Priority
A (USER AUTHORIZED; routing_substrate_training_n_sweep_readout_fix_2026-06-04). Follow-up to the
readout-artifact de-confound: finds the substrate dimension N at which substrate-trained-LM learning emerges.

## Scientific question
Sweep N in {512,1024,2048,4096,8192,16384}, 3 seeds, calibrated readout (min BPC over temp grid). Find
the N-threshold where gap = uniform_bpc - calibrated_bpc crosses from ~0 (no learning) to >= 1.0 bit
(substantive). Substrate signal scales with N (bipolar MI/coord; more stored patterns at higher N).

## Pre-registered bands (bits)
HARD-PASS: gap >= 1.0 at N >= N_threshold AND gap < 0.3 at N < N_threshold AND gap monotone in N AND
N_threshold within {512..16384} AND 3/3 seeds at threshold.
MIDDLE: improvement visible but max gap < 1.0, OR threshold only at N=16384 edge, OR 2/3 seeds.
HARD-FAIL: gap < 0.3 at ALL N (refutes de-confound; joint D+H redesign promoted).

## Formula self-tests (PROT-022)
1. SubstrateCharLM.fit consumes >=1 pair + finite BPC at N=64. 2. uniform_bpc=log2(vocab)>0.
3. calibrated BPC <= temp=1.0 BPC. [ALL PASS in smoke]

## N-suffix binding (PROT-018)
NO _nN suffix; N is the swept variable; grid declared {512,1024,2048,4096,8192,16384}. 3 seeds (PROT-021).

## Timeout
Per-N wall scales with N (Hopfield write N^2); N=16384 cell heaviest. Total ~3-5h sequential.
timeout_s=21600 (justified by the N=16384 cell; resumable per-seed).

## Smoke gate
Smoke PASSED (N<=512, 2 seeds): mechanics + calibration verified; gaps~0 at small N (the known
no-learning regime, ~26 patterns at alpha=0.05). Full N up to 16384 is the real test.

## Queue
remote_cpu_queue (CPU; pure numpy substrate).
