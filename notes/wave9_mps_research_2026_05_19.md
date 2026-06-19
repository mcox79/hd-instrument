# Wave 9 MPS substrate failure — research synthesis

Returned 2026-05-19. Unbiased deep research on the closed Wave 9
negative (6.55 bpc, basically random, argmax 0.087).

## Bottom line

**Implementation, not capacity.** The 6.55 bpc number contains zero
information about whether MPS works as a VSA carrier — the experiment
ran an FHRR variant on a particularly bad initialization. The site
index never entered a contraction. Wave 9 falsified NOTHING about
MPS-VSA.

## What the prototype actually did

Packed (L=12, d=4, chi=16, chi=16) = 12,288 floats into a flat vector,
normalized per-site Frobenius, then ran FHRR-style elementwise
multiply on the flat 12,288-dim representation. Then dense 12288x12288
Hebbian W.

**Why this implements nothing MPS-like:**

1. Multiplying entry (j=3, s=2, a=7, b=11) of atom A by entry
   (j=3, s=2, a=7, b=11) of atom B is NOT the SVD-truncated site-wise
   Kronecker product. Bond indices a, b are dummies under Hadamard.
2. Position (pos_atoms) is bound with the same flat Hadamard,
   so position never gets injected at a specific site j.
3. W is dense 12,288 x 12,288 with no MPS structure — equivalent to
   FHRR with bad init at large N.

## Canonical MPS for sequence prediction

Per Stoudenmire-Schwab 2016 / Han 2018 / Miller-Rabusseau u-MPS 2020:

- **Local feature map**: each byte position lifted to small Hilbert
  space, `Phi(x) = phi^{s1}(x_1) ⊗ ... ⊗ phi^{sL}(x_L)`
- **Model value**: `Psi(x) = Tr(A^{(1),x_1} A^{(2),x_2} ... A^{(L),x_L})`
  — chain of matrix multiplies indexed by byte at each position
- **u-MPS for byte LM**: L = context window, one site per byte, d = 256
  (or d=8..16 via embedding), uniform A across sites for
  translation-invariance, supports arbitrary length
- **Trained by DMRG two-site sweeps**: local update, no backprop.
  Strong fit with our brain-inspired framing.

## Capacity estimate at L=16, chi=8, d=8

- Param count: L·d·chi^2 = 16·8·64 ≈ 8.2k params
- Honest order-of-magnitude bpc: 3.5-4.5 (beats Wave 9's broken 6.55
  by ~2 bpc but loses to FHRR's 2.4994)
- Need chi=64-256 to enter the Stoudenmire-style ML regime
- At chi=64, L=16, d=16 (~1M params): plausibly 2.0-2.6 bpc band
- At chi=256, L=16, d=16 (~17M params): FHRR-beating territory but
  loses cheap-CPU pitch

## Fit with project constraints

- **Decompose**: TT-SVD IS the definition of decomposition. Clean win.
- **Continual learning**: DMRG two-site sweep IS a delta-rule analog
  -- local, layer-wise, no backprop. Strong brain-inspired fit.
- **Cheap CPU**: O(L·d·chi^3) for inner products; O(L·d·chi^6) for
  binding. At chi=8 manageable; chi=64 borderline; chi=256 kills CPU.

## MPS vs TTN

MPS has exponentially decaying correlations along chain. For byte
language, correlations DO decay geometrically with distance, so 1D
MPS is actually better-matched than for 2D images. TTN's advantage
is hierarchy — natural fit for bytes -> words -> sentences as binary
tree. Cost similar.

**MPS is the right first cut**; TTN is natural follow-up if MPS shows
signal but plateaus.

## Five rescues (most -> least promising)

1. **Proper u-MPS with site contraction**: L=16, d=16, chi=32, DMRG
   sweeps. Best test of hypothesis. ~1 week eng.
2. **MPS as feature extractor only**: 1-2 DMRG sweeps over context,
   feed contracted scalar/vector into existing FHRR + dense-W pipeline.
   Cheapest hybrid.
3. **TTN substrate** (binary tree, d=16, chi=32) — better correlation
   structure for byte hierarchy.
4. **MPO W operator** — keep FHRR atoms but represent W as MPO with
   bond dim wD. Compresses W from N^2 to L·d^2·wD^2.
5. **PEPS** — not promising for 1D byte streams.

## Smallest disambiguating experiment (~2 days, ~50 LOC)

- u-MPS, L=16, d=16, chi=16 (~4k params)
- Proper sequential contraction `Tr(A^{x_1}...A^{x_L})` for Born-machine
- Single epoch of DMRG sweeps on byte corpus
- Decision rule:
  - bpc < 4.0: MPS substrate has signal; rescale to chi=64 and continue
  - bpc > 5.5: capacity at chi=16 too small; bump chi or kill the bet
  - bpc 4.0-5.5: ambiguous, run chi=64

## Sources

- [Stoudenmire-Schwab Supervised Learning with Quantum-Inspired TN NeurIPS 2016](https://arxiv.org/abs/1605.05775)
- [Han et al. Unsupervised Generative Modeling using MPS PRX 2018](https://arxiv.org/abs/1709.01662)
- [Miller-Rabusseau-Terilla u-MPS Tensor Networks for Probabilistic Sequence Modeling](https://arxiv.org/abs/2003.01039)
- [Cheng-Wang Tree Tensor Networks for Generative Modeling 2019](https://arxiv.org/abs/1901.02217)
- [Qiu Tensor Products and HDC 2023](https://arxiv.org/abs/2305.10572)
- [Kleftogiannos Language Modeling using Tensor Trains 2024](https://arxiv.org/pdf/2405.04590)
- [Tensor Network ML overview](https://tensornetwork.org/ml/)
- [DMRG algorithm reference](https://tensornetwork.org/mps/algorithms/dmrg/)
