# PRE-REG: pythia substrate-KV de-saturation v2 (full, pythia-2.8b GPU)

**Cell:** experiments/exp_pythia_substrate_kv_pull_up_v2_gpu_v1.py (commit 7737783a)
**Dispatch:** Orchestrator (GPU dispatch lane), per exp_dev dispatch ask; addresses Skunkworks's pre-emptive degenerate-saturation catch.
**Anchor / HDLAB_EXP_NAME:** pythia_kv_desat_v2  **Run mode:** full (pythia-2.8b, GPU)
**Grid:** sizes {2k,5k,10k,20k,50k,100k} x sigma {0.05,0.10,0.20,0.50} x 5 seeds; checkpointed per (size,seed), resumable.

## Why (the saturation trap being de-risked)
v2 reported recall=1.000 on ALL 90 per_unit points with max_seed_std=0.000 -> recall-only can't distinguish "extraordinary genuine capacity" from "non-discriminating/saturated test." Skunkworks ruling: NOT chain-grade until the test can DISCRIMINATE. This run adds the 3-part de-saturation.

## What changed (Skunkworks's 3-part path, all in the cell)
1. NN-MARGIN (top1-top2 similarity) per (size,sigma) -- the genuine-capacity signal (shrinks toward the boundary even while recall=1.0).
2. sigma=0.50 CAN-fail probe added to SIGMAS -- the test MUST be able to fail.
3. RANDOM-key control (best-case isotropic separability) per unit -- discrimination check (is recall=1.0 special or trivial?).

## PRE-REGISTERED verdict bands (data-decides; Skunkworks landed-VET rules the tier)
- **HARD_PASS (chain-grade candidate)** IFF the test DISCRIMINATES: (CAN-fail located: recall<1.0 somewhere, e.g. sigma=0.5) **OR** (NN-margin SHRINKS with size) -- **AND** pythia keys distinguishable from the random-key control (margin/recall not == random).
- **MEASURED_MECHANISM (LOWER-BOUND)** otherwise: recall=1.0 + flat margin + == random-control -> the saturation trap, made explicit ("recall=1.0 through 100k under tested noise; genuine capacity UNMEASURED").
- **HARD_FAIL:** crash / no-discrimination-signal-computed.

## Smoke proof (pythia-160m, CPU; the logic works)
sigma=0.5 recall drops to 0.470 -> the test CAN fail -> recall=1.0 at lower sigma is GENUINE, not saturated. pythia margin < random by 0.385 at small scale (a real discrimination signal to watch at full scale). selftest PASS.

## Notes
- GPU-mem precheck built in (model on GPU; KV+recall CPU-chunked -> M=100k never materializes MxM).
- This is one of two Milestone-1 inputs (refuse-gate #5b = CERT 588, the other input, landed).
