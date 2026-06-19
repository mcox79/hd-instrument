# Prereg: substrate_trained_mini_lm_rung1_readout_fix_v2

## Anchor
substrate_trained_mini_lm_rung1_readout_fix_v2

## Priority
A (USER-AUTHORIZED; routing_readout_fix_reevaluate_4_brain_inspired_hfs_2026-06-04). Tests whether the
cycle-43 mini_lm "no learning" HARD_FAIL was a readout artifact (cosine-softmax @ temp=1.0 -> near-flat).

## Scientific question
Re-run substrate-trained mini-LM with a temperature-CALIBRATED readout (min BPC over temp grid
{1.0,0.5,0.3,0.2,0.15,0.1}; report temp=1.0 artifact baseline + temp=0.2 nominal + calibrated). Does
the substrate show learning (calibrated BPC below uniform) once the readout flatness is removed?

## Pre-registered bands (routing; BITS, uniform_bpc ~ log2(vocab) ~ 5.52)
HARD-PASS: calibrated BPC < 4.5 (>= 1.0 bit below uniform) on >= 4/5 seeds.
MIDDLE: calibrated BPC in [4.5, 5.2] (0.3-1.0 bit below uniform).
HARD-FAIL: calibrated BPC > 5.2 (within 0.3 bit of uniform; readout-fix does not rescue).

## ONE parameter change (per routing)
Readout temperature only (v1 used 1.0; v2 reports temperature-calibrated). All else identical to v1
(alpha_max=0.05, N=512, 4-primitive SubstrateCharLM). Anchor suffix _readout_fix_v2.

## CAVEAT surfaced to Research (interpret a HF correctly)
At alpha_max=0.05 the substrate stops writing at ~25 stored patterns (N=512); smoke at N=128 stored
only 7. So mini_lm is also CAPACITY-limited (and bipolar-quantized), independent of readout. The
Exp-Dev de-confound BPC=3.76 came from an UNCAPPED continuous-float32 memory, not this capped bipolar
LM. Therefore the readout fix is necessary-but-maybe-not-sufficient here. The decisive signal is the
COMPARISON calibrated-BPC vs temp=1.0-BPC (how much the readout masked); a residual HF would point to
the alpha-cap + bipolar quantization (-> joint D+H continuous-float32 redesign), NOT refute "substrate
trains." Recommend an alpha-cap-raised variant if v2 lands HF for the capacity reason.

## Formula self-tests (PROT-022)
1-5 inherited from v1 (SubstrateCharLM.fit/score_bpc finite; plateau_detection; max_abs_eig bound).

## N-suffix binding (PROT-018)
No _nN suffix; PRODUCTION_N=512 declared (rung-1). 5 seeds (PROT-021).

## Timeout
$0 CPU; ~30-60 min. PROT-019: no _n>=4096 suffix -> floor 600s; set generous for full 5-seed -> 7200s.

## Smoke gate
Smoke PASSED (N=128, 2 seeds): calibration grid works, reports temp1.0/temp0.2/calibrated BPC. Smoke
BPC~uniform is the N=128/7-pattern capacity limit (not a broken instrument); full N=512 is the real test.

## Queue
remote_cpu_queue (CPU).
