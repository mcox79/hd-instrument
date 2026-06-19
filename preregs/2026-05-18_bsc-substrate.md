# Pre-registration: BSC substrate port

Date: 2026-05-18
Status: Pre-registered, ready to launch (queued after alpha sweep + DeltaNet)
Experiment file: [exp_bsc_charlm.py](../experiments/exp_bsc_charlm.py)

## Hypothesis (H)

Replacing the FHRR substrate (complex64 unit-magnitude phasors) with BSC
(Binary Spatter Codes, ±1 real-valued vectors) produces a comparable test
bpc on our 38KB byte-level corpus. "Comparable" = within ±0.10 bpc of the
FHRR baseline 2.4994.

This is a SUBSTRATE-EQUIVALENCE test, not a "BSC is better" test. We are
asking: is the 2.49 floor a property of FHRR specifically, or does it
reproduce across substrates? Either result is informative:
- BSC matches → floor is substrate-invariant; the bottleneck is data/algorithm
- BSC differs materially → floor is substrate-specific; substrate choice matters

## Cited mechanism / paper

- Kanerva 2009 *"Hyperdimensional computing: An introduction"*
  (Cognitive Computation 1:139-159). The canonical BSC formulation.
- Plate 2003 *Holographic Reduced Representations* (book). Comparison of
  HRR/BSC/FHRR substrates.
- Kleyko et al. 2022 *Survey on Hyperdimensional Computing / VSA Part I*
  (ACM CSUR, arXiv 2111.06077). Modern formal comparison of VSA substrates.

## Operational definition

Substrate:
- Atoms: random ±1 vectors in ℝ^N (FP32)
- Binding: elementwise multiplication (`a * b`)
- Bundling: sum across K bindings; tested both `sign(sum)` and `sum/K` variants
- Similarity: real inner product / N (cosine-like)

Architecture (identical to FHRR baseline in all other respects):
- N=4096, K=4
- Pool size 1024, α=0.3, β=8, decay=1e-4, arousal=0.3
- W ∈ ℝ^{N×N} real-valued, initialized 0
- Forward: q = W @ ctx; optional shifted-ReLU readout NL: ReLU(q − b) with b=0.5
- Softmax over byte_atom similarities
- Delta-rule update: err = target − P_W·byte_atoms; dW = err.T @ ctx / N

Four variants, factorial of two design choices:
1. `bsc_continuous_no_relu`: continuous bundle (sum/K), no readout NL
2. `bsc_continuous_relu`: continuous bundle, ReLU readout NL
3. `bsc_signed_no_relu`: sign(sum) bundle, no readout NL
4. `bsc_signed_relu`: sign(sum) bundle, ReLU readout NL

The closest analog to FHRR combined+modReLU (2.4994) is `bsc_continuous_relu`.

**Faithfulness to BSC literature:** Kanerva's original BSC uses sign(sum)
bundling (`bsc_signed_*`). The continuous variants are extensions that
preserve more information at small K — closer to FHRR's bundling philosophy.
The fact that we test BOTH is intentional: it ablates one design choice
(quantization) without conflating with substrate choice (binary vs complex).

## Falsification criterion (machine-readable)

H supported if best BSC variant 5-seed mean is within ±0.10 of 2.4994
(range 2.40-2.60). Substrate-invariance claim has support.

H rejected if best BSC variant 5-seed mean is OUTSIDE [2.30, 2.70]. Substrate
matters materially — direction informs next experiment:
- If BSC ≤ 2.40: BSC substrate dominates; FHRR was suboptimal. Promote
  BSC as new default.
- If BSC ≥ 2.70: FHRR substrate dominates at small N; BSC may need much
  larger N or different architecture. Document and revisit at N ≥ 16384.

Inconclusive if best BSC is in [2.55, 2.60] or [2.40, 2.45]; promote to
multi-seed for tighter confidence interval.

## Pre-mortem (top 3 failure causes / pathological outcomes)

1. **BSC capacity ceiling at N=4096.** Per Frady-Kleyko-Sommer capacity
   analysis, BSC stores fewer "items per dimension" than FHRR because
   each dim is 1 bit vs FHRR's continuous phase. Could systematically
   underperform at small N. Mitigation: report both BSC and FHRR at the
   same N; if BSC needs N=16384 to match, document that explicitly.
2. **Signed bundle loses too much information at K=4.** sign(sum_4) is a
   2-bit-per-dim discretization. Continuous variant should be the fair
   comparison; signed is the literature baseline.
3. **ReLU on real-valued q has fundamentally different geometry than
   modReLU on complex q.** modReLU shrinks magnitudes (preserves phase);
   ReLU zeros half-space (asymmetric). May produce a non-FHRR-comparable
   regularization effect.

## Parameter-matched non-bio control

The FHRR baseline (2.4994 at identical N, K, hyperparams) IS the
parameter-matched control. The only difference between the two experiments
is the substrate.

## Expected speedup

Per the dtype investigation closed pin: real FP32 matmul DOES engage Tensor
Cores via TF32 (`torch.set_float32_matmul_precision("high")`). cuBLAS
complex64 does NOT. Expected wall-time at N=4096: similar or modestly
faster than FHRR. At N=16384, BSC should be substantially faster.

We do NOT pre-commit to a speedup target — but we will measure and report.

## Expected wall time

4 variants × 15 epochs × N=4096 ≈ ~5 minutes total. (Faster than the FHRR
baseline because real FP32 matmul is Tensor-Core accelerated.)

## What this measurement tells us

If BSC ≈ FHRR: the bottleneck at 2.49 is data + algorithm, not substrate.
Promotes algorithmic-side experiments (DeltaNet, surprise variants,
continual learning) as the right direction. Closes the substrate question
for now.

If BSC < FHRR: a brain-closer substrate is also algorithmically better.
Substantial implication: FHRR was a wrong default. Promote BSC and redo
the architecture sweep on the new substrate.

If BSC > FHRR: substrate matters in the direction of FHRR's continuous
phase code. Either BSC needs more capacity (try N=16384) or the floor
is FHRR-favored at small N. Note as a finding and continue with FHRR.
