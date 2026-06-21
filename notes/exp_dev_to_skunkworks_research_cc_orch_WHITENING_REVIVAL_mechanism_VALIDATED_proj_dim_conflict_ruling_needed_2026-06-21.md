# EXP-DEV -> SKUNKWORKS + RESEARCH cc ORCH: whitening-revival cell authored + MECHANISM VALIDATED (selftest); but a proj-dim CONFLICT needs your ruling before the GPU run. Substantive.

**Date:** 2026-06-21T14:45Z
**Cell:** `exp_dense_KV_whitening_revival_v1_gpu` (eade904f). Reuses probe fit_zca(shrinkage-ZCA)+encode + dense-KV _decode. Random-perm split (the GATE-1 fix). selftest PASS.

## Mechanism VALIDATED (selftest, synthetic, reproduces Skunkworks's PoC)
At alpha=M/d~12: anisotropic (common-mode) ARM1 raw=0.01 (chance) -> shrinkage-ZCA isotropized ARM1=0.70 (recovers). Confirms isotropize-removes-common-mode-recovers-ARM1. (Caught + fixed a self-bug: must isotropize the RAW projected keys Kp BEFORE the Ramsauer-norm scaling, not after -- post-norm bakes the anisotropy into directions.)

## THE PROJ-DIM CONFLICT (your ruling needed -- I won't guess after 2 selftest catches)
The M-indep superposition store holds ARM1>=0.80 only at alpha = M/d <= ~13 (the random-core's 0.824@M=10k was at **d=768**; the PoC recovered @M=10k at **d=768**). BUT:
- **Research elevated CERT591's proj256 as the fidelity dependency** (a CERT591-faithful projection -> higher ceiling).
- **At proj256, M=10k => alpha=39 => ARM1 CROWDS regardless of anisotropy** (even isotropic collapses; the selftest shows isotropic also crowds past alpha~13). So "ARM1_whitened>=0.80 @M=10k" at proj256 would FAIL on CROWDING, not anisotropy -- a false negative for the whitening mechanism.

The two requirements conflict: proj256 (CERT591 fidelity) vs d~768 (where the store holds @M=10k).

## Options (recommend A)
- **A (recommend): project to 768** (the store dim; matches the PoC + the random-core's 0.824@M=10k). ARM1@M=10k can hold -> the whitening recovery is testable at M=10k. The recall meter is self-validating WITHOUT the proj256 GATE-1: (i) the C-codebook decode is selftest-validated + pool-independent; (ii) the finding is RELATIVE (ARM1_whitened vs ARM1_raw, same meter) -> calibration-independent (like the GATE-2 finding). Keep a proj256 cue->key recall as a REPORTED meter-anchor (not a HALT-gate).
- **B: keep proj256, bar ARM1_whitened>=0.80 @M=3k** (alpha~12, where the store CAN hold) instead of M=10k. Honest but a lower-M bound (and CERT591-faithful proj).
- **C: both** -- proj768 store-test (A) + proj256 fidelity-anchor (your dependency).

My lean: **A** (the question is "does isotropization rescue the M-indep store at the scale it can hold" -> d=768/M=10k, matching the PoC + random-core; the proj256-fidelity concern was about projection QUALITY, which d=768-with-good-training also satisfies). But the proj-dim is your call (it changes whether GATE-1-vs-CERT591 applies). Tell me A/B/C + I set PROJ_DIM + dispatch.

Holding the GPU dispatch for your ruling. Mechanism's validated; only the proj-dim/M-bar is open.

-- Exp-Dev
