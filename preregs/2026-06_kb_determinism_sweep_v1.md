# Pre-registration: kb_determinism_sweep_gpu_v1

**Date:** 2026-06-11
**Anchor:** kb_determinism_sweep_gpu_v1
**Queue:** overnight_queue (GPU)
**Cell:** exp_t5c_pp225_kb10k_genuine_v1.py, **Seeds:** 3 (HDLAB_SEED 7,8,9), **Device:** CUDA

## Scientific question
Is the PP-225 production fact-recall claim (held-out recall ~0.994 at kb10k) SEED-DETERMINISTIC, or a lucky seed? The
10K-100K asymptote was n=1 per scale. Runs the validated kb10k cell (frozen Pythia-1.4b + bge-large projection head) at 3
seeds and reports mean +/- std of held-out recall. Research values "deterministic at smaller scales" for the Tier-A claim.

## Pre-registered bands

**HARD-PASS:** mean held-out recall >= 0.90 AND std <= 0.03 (seed-deterministic high recall; reinforces Tier-A).

**MIDDLE:** mean >= 0.90 but std > 0.03 (high but seed-variable).

**HARD-FAIL:** mean held-out < 0.90.

## Calibration rationale
kb10k landed 0.9945 held-out at n=1 in the asymptote sweep; the projection head is trained deterministically (fixed init
via torch.manual_seed, Adam), so std should be near-zero across seeds. >=0.90 mean with std<=0.03 confirms the production
claim is not a lucky-seed artifact. A larger std would itself be the informative signal (seed-sensitivity in the head).

## N-suffix section
Subprocesses the kb10k cell (N_FACTS=10000, frozen Pythia-1.4b + bge-large). Each seed ~5-15 min on CUDA (early-stop).
Per-seed checkpoint via _seed_checkpoint (resume-safe). Fits 8GB GPU (kb10k validated at that scale).
