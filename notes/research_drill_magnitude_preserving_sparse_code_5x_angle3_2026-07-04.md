# Research Drill 5x -- Angle 3/3: Magnitude-Preserving Sparse Code (ceiling-raise + LIVE shot)

Date: 2026-07-04
Author: Research (Director)
Drill family: encoder-rescue 5x-drill, angle 3 of 3 (magnitude-preserving sparse construction)
Trigger: block-argmax K128 sparse code caps retrieval at 0.43 even on teacher's OWN vectors
(the QUANTIZER ceiling) -- throws away graded info. NEED retrieval>=0.35 at ~2% sparse WITH
clean bind/unbind SBC algebra. USER: "should be EASIER."

## HEADLINE

The block-argmax code discards magnitude by quantizing each block's survivor to +-1. For a FIXED
support, +-1 is a strictly SUBOPTIMAL cosine weighting: the cosine-optimal weighting on any support
is the TRUE (graded) values. So keeping magnitude PROVABLY raises the ceiling; the only real question
is whether the graded code still closes under bind/unbind. The literature answer is YES and it is
already published and hardware-validated: **Generalized Sparse Block Codes (GSBC, Hersche/IBM 2023/2025)**
-- blocks are graded positive-real with unit L1-norm, and binding/unbinding is blockwise circular
convolution/correlation, which preserves the unit-L1 (graded) invariant EXACTLY. IBM adopted GSBC
precisely because binary/dense codes lost accuracy on real deep-CNN embeddings -- the SAME failure
mode we have distilling a real teacher.

Single most promising construction: **Sparse-GSBC (block-wise top-m graded positive-real, renormalized
to unit-L1 per block) with blockwise-circular-convolution binding, plus a B-dim block-ENERGY side
channel for between-block magnitude.** Drops the +-1 quantization; switches element-wise-product binding
to blockwise circular convolution (the fix that makes graded values close cleanly).

## PRIOR-WORK CHECK (substrate KB, --chunk-content --schema-version v2 --tau 0.15 --k 5)

Query "sparse block codes factorizer bind unbind magnitude" -> cosine 0.4092 top hit.
Prior arc work on this concept: YES, substantial, but on the FACTORIZER (disentangling) axis, NOT the
magnitude/retrieval axis.
- notes/research_drill_codebook_capacity_negative_2x_2026-06-10.md (2c "Distributed sparse block codes
  with factorizers"): mapped SBC = N split into B blocks, ONE non-zero per block (1-of-(N/B) one-hot),
  element-wise-product binding; Cartesian-product codebook. Cited Hersche 2023/2025 (arXiv:2303.13957,
  5+ orders capacity gain) + Kymn 2024 (residue HDC, 40 vs 220 codebook). Framed as FACTORIZATION
  capacity for factorizable items -- did NOT address the magnitude/retrieval ceiling. P_deflated there
  was 0.45 for factorization, gated on item factorizability.
- notes/wave14e_multi_hop_reasoning_research.md::chunk020 + wave14e_hierarchical_composition_research.md
  (Sparse block codes section, cosine 0.4092): adopt-Hersche-factorizer note for 4+ factor resonator
  scaling; disjoint blocks per hierarchy level. Again factorizer-scaling, not retrieval-magnitude.
- notes/exp_dev_handoff_research_field_modern_hopfield_5x_2026-06-07.md: HOPFIELD-SPARSE-K sparsemax
  top-k retrieval -- adjacent (sparse retrieval) but Hopfield energy path, not SBC algebra.
CONCLUSION: our prior SBC work is all one-hot/binary + factorizer-focused. The magnitude-preserving
GSBC generalization and its RETRIEVAL-ceiling implication are NEW to our arc. No rediscovery risk.

## LITERATURE (generic-term searches; lit-scan calibration penalty applied)

(a) Which sparse VSA variants keep MAGNITUDE and still close under bind/unbind?

  - Binary SBC (Laiho-Poikonen-Kanerva-Lehtonen 2015; Frady-Kleyko-Sommer 2021, arXiv:2009.06734):
    one-hot per block, blockwise CIRCULAR CONVOLUTION binding -> "IDEAL properties" (exact, lossless,
    dimensionality-preserving). BUT one-hot => NO within-block magnitude. This IS essentially our
    current block-argmax code (minus the +-1 sign). Closes perfectly; carries no graded info.
  - General sparse / top-k with MAP element-wise-product binding: CAN keep graded magnitude, but Frady
    et al. state plainly: binding for general sparse vectors "also works, but is LOSSY." Element-wise
    product of two sparse vectors collapses to support-intersection; unbind needs reciprocals ->
    small-value noise blow-up. This is why naive "keep magnitude" breaks the algebra.
  - **GSBC -- Generalized Sparse Block Codes (Hersche/IBM 2023/2025, arXiv:2303.13957, "Factorizers
    for Distributed Sparse Block Codes"):** blocks NOT restricted to binary/sparse -- elements in the
    POSITIVE REALS, each block has UNIT L1-NORM. Binding/unbinding = blockwise circular convolution/
    correlation; KEY property: "if both operands have blockwise unit-L1-norm, the result does as well"
    -> the graded structure is an INVARIANT of the algebra. This is the one construction in the
    literature that keeps within-block graded magnitude AND closes EXACTLY. IBM's stated motivation:
    resonator/factorizer accuracy dropped up to 16.22% on product vectors from deep CNNs (real
    embeddings) -> they switched to GSBC to recover it. Directly our distillation-of-real-teacher case.
  - FHRR / phasor-per-block (block-local FHRR): unit-magnitude complex phasor per block, graded PHASE;
    binding = per-block phase addition, unbind = phase subtraction -> EXACT (unit magnitude, no
    reciprocal). Keeps graded info in phase rather than amplitude. Valid alternative; heavier to wire
    into a real-valued cosine-retrieval pipeline than GSBC.
  - Sparse HRR/FHRR with GLOBAL circular convolution: convolution DENSIFIES the support -> not
    magnitude-preserving-sparse under repeated binding. Not the path.

(b) Does a magnitude-preserving 2% code have a HIGHER retrieval ceiling than block-argmax 0.43?
  YES -- provably, and by a large margin.
  - For a fixed support S, cosine(code, teacher x) is MAXIMIZED by setting code_i = x_i (the true
    graded values). Block-argmax uses code_i = +-1, a strictly suboptimal weighting -> its 0.43 is a
    lower ceiling than the magnitude-preserving code on the SAME support.
  - Magnitude-preserving-on-support cosine = sqrt( energy_fraction_captured_by_S ). For heavy-tailed
    transformer/BGE embeddings, the top ~2% of coordinates carry roughly 0.5-0.85 of L2 energy ->
    ceiling ~0.7-0.9. That clears 0.35 with LARGE headroom, and (the point of (b)) it raises the WHOLE
    curve, so the actual student encoder no longer has to hit an unreachable 0.43-ceiling to clear 0.35.
  - GSBC restores the WITHIN-block graded structure that argmax-quantization threw away -> ceiling
    moves up from 0.43 toward that optimum. The block-ENERGY side channel additionally restores the
    BETWEEN-block magnitude that per-block L1-normalization discards -> ceiling approaches the global
    sqrt(top-2%-energy) optimum.

(c) Does keeping magnitude BREAK the clean SBC algebra, and can it be mitigated?
  The tension is REAL but already solved. Naive graded values + element-wise-product binding DOES break
  (lossy support-intersection; reciprocal unbind amplifies small-value noise). Mitigations, cleanest
  first:
    1. SWITCH BINDING to blockwise circular convolution/correlation (NOT element-wise product). This is
       the load-bearing fix: it is ideal/lossless for block codes and preserves the graded unit-L1
       invariant -> exact unbind, no reciprocal. (Frady/Kleyko 2021; GSBC.)
    2. Per-block L1 renormalization after each bind/bundle keeps the invariant exactly (GSBC design).
    3. Separate MAGNITUDE (block-energy) side channel: a B-dim vector e (e_b = original L2 energy of
       block b) carried UN-bound alongside the GSBC part; re-applied at cleanup to reconstruct
       between-block magnitude. It never enters the convolution, so the algebra stays exact.
  Bundle/superposition: blockwise sum of graded blocks, then keep top-m per block + renormalize to
  unit-L1 (standard SBC bundling; graded values sum cleanly).

## SINGLE MOST PROMISING CONSTRUCTION

Sparse-GSBC + block-energy side channel:
  - Split N into B=128 blocks. Within each block, keep the top-m largest positive-real values
    (m=1..3; m=1 gives ~2% but forces value=1 under unit-L1 -> use m>=2 to retain a graded RATIO, or
    rely on the side channel for magnitude). Map to nonnegative via relu-shift or softmax; renormalize
    each block to unit L1 => GSBC block.
  - Carry e in R^B, e_b = pre-normalization L2 energy of block b, as an un-bound side channel.
  - Bind/unbind = blockwise circular convolution/correlation on the GSBC part (exact; graded-preserving).
    Roles/keys are themselves unit-L1 GSBC blocks. Side channel rides along untouched.
  - Retrieval/cleanup: effective vector = GSBC blocks scaled by e_b; cosine to teacher preserves BOTH
    within- and between-block magnitude.
  MINIMAL FIRST STEP (matches USER "should be EASIER"): keep the current argmax SUPPORT, just (i) drop
  the +-1 quantization and store graded magnitude, (ii) renormalize per block to unit-L1, (iii) switch
  element-wise binding -> blockwise circular convolution. That alone removes the argmax-quantization
  loss and should lift the ceiling off 0.43; the side channel is the follow-on ceiling push.

DOES-IT-RAISE-THE-CEILING: YES (0.43 -> ~0.7-0.9 optimum; GSBC alone lifts it materially, side channel
approaches the optimum). DOES-IT-KEEP-ALGEBRA: YES, EXACTLY (blockwise circular conv preserves the
graded unit-L1 invariant; published + IBM hardware-validated on the same real-embedding failure mode).

## P_deflated

P_deflated = 0.50 (novel-synthesis cap). The LOAD-BEARING mechanism -- GSBC preserving within-block
graded magnitude AND closing exactly under blockwise circular convolution -- is PUBLISHED and validated
on the analogous deep-CNN-embedding failure mode (higher-confidence backbone, ~0.6 pre-cap). The full
headline construction (sparse-GSBC + block-energy side channel, clearing 0.35 at 2% in OUR distillation
pipeline) is novel synthesis -> capped at 0.50. Deflation drivers: (i) per-block unit-L1 discards
between-block magnitude unless the side channel is added; (ii) our exact N and top-2% energy fraction
unverified on our teacher; (iii) sparsity-vs-graded trade at m=1 (unit-L1 forces value=1). Upside: the
ceiling-raise is PROVABLE (argmax +-1 is strictly suboptimal cosine weighting), consistent with USER's
"should be EASIER."

## NEXT-STEP CELL SKETCH (SMOKE-first, local CPU)

Cell MP-SBC-1: on the FROZEN teacher vectors used to measure the 0.43 ceiling, compute, at B=128 /
~2% sparse: (arm A) block-argmax +-1 [reproduce 0.43], (arm B) block-top-1 graded + unit-L1, (arm C)
GSBC block-top-3 graded + unit-L1, (arm D) C + block-energy side channel. Metric: mean cosine to
teacher (ceiling) + retrieval@1 on held-out. PAIRED trials across arms (same vectors). Then a SECOND
cell for algebra: bind two GSBC vectors via blockwise circular conv, unbind, measure recovery cosine
vs the element-wise-product baseline (expect element-wise lossy, blockwise conv near-exact).
Discriminator must survive scale: run at full teacher N, not a toy N.

## SOURCES
- Frady, Kleyko, Sommer 2021, "Variable Binding for Sparse Distributed Representations: Theory and
  Applications" -- arXiv:2009.06734 (blockwise circ conv "ideal", general-sparse binding "lossy").
- Hersche, Terzic, Karunaratne, Langenegger, Pouget, Cherubini, Benini, Sebastian, Rahimi 2023/2025,
  "Factorizers for Distributed Sparse Block Codes" -- arXiv:2303.13957 (GSBC: positive-real, unit-L1
  blocks; blockwise conv preserves unit-L1; switched from binary/dense due to deep-CNN accuracy drop).
- Laiho, Poikonen, Kanerva, Lehtonen 2015, "High-dimensional computing with sparse vectors" (SBC).
- Kymn et al. 2024, "Computing with residue numbers in high-dimensional representation" (residue HDC).
- Prior arc: notes/research_drill_codebook_capacity_negative_2x_2026-06-10.md (2c);
  notes/wave14e_hierarchical_composition_research.md (Sparse block codes).
