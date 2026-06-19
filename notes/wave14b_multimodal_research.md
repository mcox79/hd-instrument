# Multimodal validation feasibility — research synthesis

Returned 2026-05-19. Unbiased survey on what shipping CLIP/DINOv2
embeddings into the substrate would actually cost.

## TL;DR

**1-week build for credible weak claim, 1-month for paper-grade.**
Smallest demo: CLIP+random-replay BWT (3 days, leans on our STRONGEST
result, not the weakest link). Decompose recovery will degrade from
100% (bipolar) to 60-90% (continuous correlated atoms).

**Biggest risk: silently overclaiming.** Hu et al. 2024 shows
traditional resonator network is BROKEN on continuous codebooks.

## State of the art

- **Neubert-Schubert CVPR 2021**: canonical. Treats deep image descriptors
  (NetVLAD, DELF) as HDC carriers. Aggregates local descriptors + positions
  into single holistic hypervector; reports 20% mean / 3.6x worst-case
  improvement over runner-up aggregation on place recognition. **Crucially
  they PROJECT descriptors before bundling — they do not use raw learned
  features as bipolar atoms.**
- **Mitrokhin Science Robotics 2019**: event-camera percepts + motor actions
  via fixed projection into binary hypervectors.
- **Frady-Kleyko-Sommer 2021 + FPE**: treats continuous codebooks formally,
  kernel is sinc not delta.
- **Hersche/Karunaratne/Langenegger/Rahimi (IBM line)**: 2023 Nature Nanotech
  + 2025 Factorizers paper — most relevant for our substrate.
- **Hu et al. 2024 (arXiv:2403.13218)**: MOST RELEVANT. Traditional
  resonator networks FAIL TO CONVERGE on continuous (FHRR) codebooks at
  F=4, k=9: ~11% success. Their attention-based replacement gets 29-47%.
  **With continuous codebooks the original resonator is broken.**

**Honest take**: nobody in this literature uses raw CLIP/DINOv2 as atoms.
They project + position-bind first.

## What breaks when atoms are continuous-correlated

- **Effective dimension drops**. CLIP-L nominal d=768 but participation
  ratio is 30-60 for ImageNet classes. Bundle capacity scales with
  effective rank → K-cliff shrinks proportionally.
- **Resonator convergence becomes unreliable** (Hu 2024 cautionary tale).
  Our resonator: bipolar cross-correlation ~1/√N. CLIP inter-class cosine
  routinely 0.3-0.5. Resonator will hallucinate spurious mixtures.
- **Decompose accuracy**: expect 60-90%, not 100%. Below 70% the
  "decompose → edit → recompose" claim collapses for multimodal.
- **Edit/recompose bit-exactness disappears**. Our 100% claim depends
  on bipolar algebra. Continuous correlated atoms give approximate
  recomposition with small angular drift per round trip.

## Cheapest credible validation

**Use sentence-transformers all-MiniLM-L6-v2 (d=384, fastest) and
CLIP-B/32 (d=512) as probes; skip DINOv2 patch-level until basics work.**

### Day 1-2: Decompose recovery curve
- 1000 CLIP-image embeddings + class-label tokens, L2-normalize,
  sign-quantize to bipolar ±1 at N=4096 (trivial bridge)
- Bundle K ∈ {4, 8, 16, 32, 64}, run resonator, record top-1 recovery
- **Prediction**: 95-100% at K=4, dropping below 80% by K=32
  (markedly worse than 92% at K=32 on random atoms)
- If better → learned structure helps; if <60% at K=32 → need projection layer

### Day 3: C3-factored retrieval vs flat cosine
- Bundle (image_embed ⊗ pos) over 1000-entry CLIP pool, query by position
- **Prediction**: factored wins only when positions matter (scene composition).
  Pure semantic retrieval: flat cosine ties or beats — published
  Neubert-Schubert pattern.

### Day 4-7: Continual learning with random replay
- Phase A = 500 ImageNet train-class embeds, Phase B = 500 test-class
- Measure BWT with/without 50% random replay
- **Prediction**: R10 random-replay finding (+0.73 BWT at K=32) SHOULD
  transfer — mechanism is W-drift correction, not atom-specific.
- **Strongest standalone publishable claim.**

## Coherence regularization options

Increasing cost:
1. **Sign-quantize + scale** (free): works for in-modality, loses fine-grained similarity
2. **Random projection to N=4096 then sign** (cheap, ~10 LOC): JL-style, preserves cosine angles approximately
3. **Learned linear projection** with orthogonality penalty W^T W ≈ I (Hersche-style, ~50 LOC, one epoch): literature says +5-15 points classification accuracy

Start with option 2. **Frontiers 2026 makes the point: learning tasks
want correlation, decoding tasks want orthogonality** — for our decompose
use-case, push toward orthogonality.

## Does R10 K-effect transfer?

Math: gap = E[similarity(target, bundle\K)] − E[similarity(target,
concept_fused)]. **Nothing in derivation is byte-specific.** Will
transfer PROVIDED decompose recovery stays above ~70% at K=32. If
recovery collapses to 50%, bundle interference is no longer bottleneck —
atom geometry is — and K-effect curve flattens.

R10 transfer is conditional on decompose-curve test.

## Three falsifiable experiments

1. **CLIP-decompose-curve**: 5 seeds × K ∈ {4,8,16,32,64}; with/without
   random projection. Falsifier: recovery <60% at K=32 even with projection.

2. **C3 vs flat cosine on CLIP-1000**: 5 seeds, MAP@10. Falsifier:
   factored loses by >5% MAP when positions are meaningful.

3. **ImageNet-A→B replay BWT**: 5 seeds, 3 conditions (no replay /
   random 50% / random 10%). **Falsifier: replay gain <+0.30 BWT.**

## Honest bottom line

**Smallest demo for "substrate works on learned embeddings"**:
random-replay BWT recovery on CLIP-embedded ImageNet (test 3), 5 seeds,
**+0.30 BWT or better**. ~3-day build, leans on STRONGEST result
(R10/replay), not weakest link (decompose under correlation).

If decompose recovery is the headline you want, expect extra two weeks
on projection-layer training to get above 90%.

**Biggest risk: silently overclaiming.** If we report 75% decompose
recovery as success without flagging that it's 100% on bipolar, reviewers
will catch it. Hu 2024 paper is a strong prior that traditional resonator
on continuous correlated codebooks is broken. **Either swap to
attention-resonator from day one, or have a clear "limitations on
continuous atoms" subsection.**

## Sources

- [Neubert-Schubert HDC framework for image descriptors CVPR 2021](https://arxiv.org/abs/2101.07720)
- [Mitrokhin Sensorimotor Control Neuromorphic Science Robotics 2019](https://www.science.org/doi/10.1126/scirobotics.aaw6736)
- [Frady-Kleyko-Sommer Sparse VSA Binding](https://arxiv.org/pdf/2009.06734)
- [Hu et al. Self-Attention Semantic Decomposition VSA 2024](https://arxiv.org/html/2403.13218)
- [Karunaratne In-memory factorization Nature Nanotech 2023](https://pubmed.ncbi.nlm.nih.gov/36997756/)
- [Hersche Factorizers for Distributed Sparse Block Codes 2025](https://journals.sagepub.com/doi/10.3233/NAI-240713)
- [Lewis Does CLIP Bind Concepts EACL 2024](https://arxiv.org/abs/2212.10537)
- [Frontiers 2026 Optimal hyperdimensional representation](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1690492/full)
