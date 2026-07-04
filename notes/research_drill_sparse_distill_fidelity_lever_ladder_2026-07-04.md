# Research drill: lever ladder to close the TRAINED-student retrieval-fidelity gap (distill dense teacher -> 2% sparse block code)

Date: 2026-07-04
Author: Director (research drill; NO dispatch)
Type: internal tracking notes memo (pre-registered lever ranking, to be ready before the first fallback probe lands)

## Problem (verified on disk -- pointer: data/exp_encoder_teacher_sparsifier_bypass_v1/metrics.json; not re-derived)

- Distill BGE-large (1024d dense teacher) -> K-block bipolar SPARSE code (K128 = 3.125% active; blk_l=32, n_dim=4096) via MLP student + STE hard block-argmax.
- CODE CEILING (teacher's OWN vectors through the SAME sparsifier, ZERO training error): `ortho_k128_ret_agree10 = 0.4295`, `ortho_k256_ret_agree10 = 0.5486`. Confirmed in metrics.json lines 24/26.
- TRAINED student: ~0.20 @ K128, ~0.29 @ K256 (USER-supplied, verified-on-disk elsewhere).
- => Student captures ~0.20/0.43 = **47% of the code's available retrieval capacity** at K128 (~53% at K256).
- Target 0.35 is BELOW the K128 ceiling (0.43) => this is a **training-fidelity gap at fixed 2% sparsity**, NOT a code/sparsity/density limit.
- To hit 0.35 from 0.20 the student must climb from 47% -> 81% of the code ceiling: close ~65% of the remaining 0.20->0.43 gap (+0.15 abs). Ambitious for any single lever.

## Prior arc overlap (substrate concept-query, MANDATORY pre-dispatch check)

`substrate_query.sh "distill dense teacher into sparse bipolar code retrieval fidelity straight-through estimator"` (confidence 0.29):
- Prior arc work on **sparse-vs-dense retrieval NOISE ASYMMETRY** (Sparse Hopfield: sparse retrieval has LINEAR noise-impact-in-load vs exponential for dense) and **sparse-KEY narrow-basin-of-attraction fragility** (notes 2026-06-05, 2026-06-07).
- These are about the *robustness of sparse codes at retrieval time*, NONE about the *distillation TRAINING-fidelity gap*. **Prior arc work on THIS concept (student-underuses-a-sufficient-code): NONE.** New operational question.
- One relevant caution the substrate already holds: sparse k-block codes have a *narrower basin* (T_sparse ~ T/sqrt(alpha_s*N)), i.e. small map errors cost more in sparse-code retrieval than dense -- which raises the bar on gradient/optimization precision (favours levers B/C below).

## Refuted / DEAD (not re-proposed)

1. Loss-FAMILY swap DEAD -- KL-RANK / PKT rank-aware distillation gave +0.01 ret_agree10 vs MSE. Ranking loss is NOT the lever.
2. DENSE / raw-continuous readout WORSE (0.169 < sparse).
3. OPQ / isometric ROTATION pre-quantizer ~0 for retrieval (ortho-vs-random +0.005; on disk isometry_vs_random_gap_k128 = 0.0276 on Spearman, but only +0.0046 on ret_agree10).
4. Bigger K (K256/K512) trades the 2% sparsity goal. Sparsity LOCKED ~2%.

---

## ORDERED LEVER LADDER (most-likely-to-close-the-gap first)

### #1 -- B: DISCRETE-GRADIENT QUALITY (temperature-annealed soft-to-hard assignment, replacing hard-STE block-argmax)  [TOP BET]

**Mechanism.** The forward path is a per-block argmax (one-hot per 32-wide block). Hard STE copies the upstream gradient straight through the non-differentiable argmax, which is a *biased* estimator: the backward pass ignores that the winner could flip, so gradient signal to the *near-winner* logits (exactly the ones that decide fine near-neighbor rank) is starved/mis-signed. Replace with a per-block softmax relaxation (plain or Gumbel) at temperature tau, trained soft, tau annealed high->low so the forward converges to the hard argmax the eval uses. Optionally add a soft/hard consistency term (central-loss style) so the soft-trained geometry survives the hard snap.

**Brain-grounded prior.** Cortex/cerebellum/olfactory k-WTA does NOT use a fixed hard threshold -- it uses *homeostatic gain control / adaptive per-population thresholds* to tune how aggressively it sparsens. That adaptive, graded thresholding (vs a fixed hard argmax) is precisely what lets biological expansion-recoding trade separation against near-neighbor preservation. The trainable analog of homeostatic gain is a *learnable, annealed soft assignment* -- direct support for lever B over a fixed hard STE.

**Supporting lit (strong, convergent across 4 sub-fields).**
- Product Quantization Network (Yu et al., ECCV 2018 / IJCV 2020): soft PQ layer is differentiable; **hard PQ is the special case temp->inf**. Soft-assign end-to-end training is the standard fix for the argmax non-differentiability.
- Deep PQ (DPQ) uses BOTH soft and hard codeword assignment via STE -> **mAP 0.831 vs 0.733 (deep-PQ) on CIFAR-10 @32bit**, ~+0.10 mAP purely from a better soft/hard assignment scheme.
- "Soft-to-Hard Vector Quantization for End-to-End Learning Compressible Representations" (Agustsson et al., arXiv 1704.00648): explicit soft->hard annealing is the canonical recipe for learning discrete codes.
- "Soft then Hard: Rethinking Quantization in Neural Image Compression" (arXiv 2104.05168): names the exact failure -- **train-soft/test-hard MISMATCH** -- and shows a soft-then-hard schedule closes most of it. Also warns annealing is empirically fragile (schedule-sensitive).
- Codebook-softened PQ (Neurocomputing 2022) + joint central loss: a consistency term reduces the soft-hard discrepancy gap.
- STE bias is formally established: ST-Gumbel is biased with first-order bias persisting even under concentrated logits (Decoupled ST-GS arXiv 2410.13331; Shekhovtsov cold-analysis PMLR 2023; low-variance estimators arXiv 2603.08257).

**Contradicting / caution.** Annealing schedules are "empirically determined... fragile training" (Soft-then-Hard). Gain is usually PARTIAL, not full closure. Our block-argmax is a *structured* categorical (one winner per 32-block) -- Gumbel per block is clean, but tau schedule must be per-block-calibrated.

**One cheap decisive test.** At K128, swap hard-STE for per-block softmax with a 2-point tau sweep (e.g. tau: 2.0->0.1 linear vs cosine) + a soft/hard consistency term; hold everything else fixed; read ret_agree10 delta. Smoke-scale first (discriminator must survive scale). Decisive because it isolates the estimator from capacity/data.

### #2 -- A: STUDENT CAPACITY (MLP width/depth)

**Mechanism.** Reproducing a 1024d teacher's *fine* near-neighbor geometry, then arranging it so a hard block-argmax preserves rank, is a harder function than coarse similarity. An under-width/under-depth MLP may lack the capacity to place points quantization-favourably.

**Brain-grounded prior.** Weak/neutral. Biology's "capacity" for this is the LEARNED expansion weights (PN->KC is ~150->2500, a large learned/structured fan-out); argues the *quantizer/codebook* side wants parameters, not just the pre-quantizer trunk.

**Supporting lit.** Teacher-student **capacity-gap** is a named, real failure in distillation-into-hash (Deep Hash Distillation arXiv 2112.08816; "gradual approach to KD in deep supervised hashing" ScienceDirect 2024; growing/progressive-teacher and Bit-mask Robust Contrastive KD WWW 2024 all exist specifically to shrink the capacity gap). BUT: most capacity-gap work is about *small mobile students*; a 1024->4096 MLP is not obviously starved.

**Contradicting.** Capacity underfitting co-presents with high *student TRAINING* loss. If student train loss is already near its floor while ret_agree10 is low, capacity is NOT the lever (points back to B: objective/estimator mismatch, not fit). Cheap to check first.

**One cheap decisive test.** 2x width and +1 depth ablation at K128 (2 arms), smoke-scale; AND read the current student's own train-loss-vs-ceiling first (if train loss is floored, deprioritize A immediately). Near-free diagnostic.

### #3 -- C: OPTIMIZATION / SCHEDULE (longer training, LR schedule, EMA, batch composition)  [distinct from B's tau schedule]

**Mechanism.** Sparse-code retrieval has a narrow basin (substrate prior above) -> small residual map error is expensive, so the last fraction of fidelity is optimization-limited: LR warmup+cosine, longer horizon, EMA of student weights, larger/curriculum-free batch for stable neighbor statistics.

**Brain-grounded prior.** Weak. (Homeostatic adaptation is slow/continual -> loosely favours EMA/longer consolidation, but this is thin.)

**Supporting lit.** Generic distillation benefits from longer schedules + EMA; annealing literature (2104.05168) stresses the schedule is where soft->hard gains are won or lost -- so C is partly the *delivery vehicle* for B.

**Contradicting.** Rarely a standalone +0.15; usually squeezes the last few points AFTER the estimator/capacity are right. Confounded with B (both are schedules).

**One cheap decisive test.** 2x training horizon + cosine LR + student EMA, single arm at K128 vs current baseline. Run PIGGYBACKED on the B test (B already changes the schedule) to avoid a redundant arm.

### #4 -- D: DATA / SUPERVISION FIDELITY (hard-negative mining, more pairs, fine-rank curriculum -- which PAIRS get supervised)

**Mechanism.** Emphasize fine near-neighbor pairs so the student spends capacity where ret_agree10 is decided.

**Brain-grounded prior.** Neutral-to-negative for THIS metric: k-WTA pattern-separation biology sharpens LOCAL contrasts, sometimes *increasing* pattern similarity in downstream cortex ("Increased pattern similarity despite higher sparseness", biorxiv 2021) -- i.e. local sharpening can distort GLOBAL rank, which is exactly what ret_agree10@10 scores.

**Supporting lit.** Hard-negative mining is standard in deep hashing / metric learning (Deep supervised hashing with hard example pairs; Fast hard-negative mining for deep metric learning).

**Contradicting (important).** The lit explicitly warns hard-neg mining "relies on only a SUBSET of training data and may not capture the GLOBAL geometric characteristics of the embedding space, deteriorating the discriminative power of the binary codes," and triplet hard-mining can cause **model collapse (identical embeddings)**. ret_agree10 is a GLOBAL top-10 rank metric -> hard-neg mining optimizes the wrong geometry and risks a regression. Also adjacent to the already-DEAD loss-family lever. Lowest.

**One cheap decisive test.** Only if B/A/C stall: add a fine-near-neighbor pair curriculum (top-50 teacher neighbors up-weighted) as ONE arm at K128, watch for global-rank regression (collapse guard).

---

## Is this gap genuinely hard? (explicit)

Partly YES, and the lit + brain both say so:
- Every discrete-code sub-field (PQ, deep hashing, VQ-VAE, neural compression) reports the train-soft/test-hard mismatch as **fragile and only PARTIALLY closable**; single-lever gains cluster at ~+0.05 to +0.10 (DPQ ~+0.10 mAP is a good analog), not the +0.15 we need in one move.
- Brain prior: k-WTA sparse coding is fundamentally a **pattern-SEPARATION / decorrelation** mechanism (expansion+sparsen enhances discriminability by REDUCING overlap), not a fine near-neighbor-RANK preserver. That structural purpose is WHY the code ceiling is only 0.43 in the first place, and it caps how much of the teacher's dense near-neighbor rank ANY sparse student can carry. FlyHash (arXiv 2001.04907) shows sparse k-WTA CAN be locality-preserving (LSH) -- but in the HIGH-expansion, data-independent regime, not our fixed-dim block code.
- Net: expect to close a good FRACTION of the 47%->81% climb, but reaching 0.35 will likely need levers STACKED (B as the engine + A capacity headroom + C schedule), not a single silver bullet.

## TOP BET

**Lever B -- replace hard-STE block-argmax with per-block temperature-annealed soft assignment (Gumbel or plain softmax, tau high->low) + a soft/hard consistency term, delivered on a longer cosine schedule (folds in C).**

- Rationale: most convergent, multi-domain evidence; directly explains the "student uses only 47% of a proven-sufficient code" signature (hard-STE bias systematically underuses the discrete code); brain-backed (homeostatic graded thresholding vs fixed hard argmax).
- Expected ret_agree10 lift (B alone): **+0.06 to +0.10** -> student ~0.26-0.30 @ K128 (short of 0.35 alone).
- Expected with B+A+C STACK: target 0.35, i.e. needs the capacity headroom + schedule to convert the last +0.05.

**P_deflated (honest, deflated per lit-scan calibration penalty; novel-synthesis cap 0.50):**
- P(B alone reaches ret_agree10 >= 0.35 @ 2% sparse): **~0.20** (raw ~0.35, deflated -0.15 for schedule fragility + partial-closure base rate + structural k-WTA cap).
- P(B+A+C stack reaches >= 0.35 @ 2% sparse): **~0.30-0.33**.
- Single stated top-bet number: **P_deflated ~= 0.25** (B as lead lever deployed with schedule support). Below coin-flip -- the gap is partially structural; keep the sparsity-honest fallback (accept ~0.30 + distill-from-BGE per encoder goals) warm.

## Sources

- Product Quantization Network (Yu et al.): https://link.springer.com/article/10.1007/s11263-020-01326-x , https://openaccess.thecvf.com/content_ECCV_2018/papers/Tan_Yu_Product_Quantization_Network_ECCV_2018_paper.pdf
- End-to-End Supervised PQ: https://arxiv.org/pdf/1711.08589
- Soft-to-Hard Vector Quantization: https://arxiv.org/pdf/1704.00648
- Codebook-softened PQ: https://www.sciencedirect.com/science/article/abs/pii/S0925231222009766
- Soft then Hard (neural image compression): https://arxiv.org/html/2104.05168v4
- Decoupled Straight-Through Gumbel-Softmax: https://arxiv.org/html/2410.13331v1
- Rao-Blackwellized ST-GS cold analysis (Shekhovtsov, PMLR 2023): https://proceedings.mlr.press/v202/shekhovtsov23a.html
- Low-variance discrete gradient estimators (beyond ReinMax): https://arxiv.org/pdf/2603.08257
- Deep Hash Distillation for Image Retrieval: https://arxiv.org/pdf/2112.08816
- Gradual KD in deep supervised hashing: https://www.sciencedirect.com/science/article/abs/pii/S0045790624007262
- Bit-mask Robust Contrastive KD for Unsupervised Semantic Hashing (WWW 2024): https://dl.acm.org/doi/10.1145/3589334.3645440
- Deep supervised hashing with hard example pairs: https://www.researchgate.net/publication/363696661
- Fast hard-negative mining for deep metric learning: https://www.sciencedirect.com/science/article/abs/pii/S0031320320305987
- Sparse connectivity -> decorrelation & pattern separation (Nature Comms 2017): https://www.nature.com/articles/s41467-017-01109-y
- Neural correlates of sparse coding & dimensionality reduction (PLOS Comp Biol): https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006908
- Increased pattern similarity despite higher sparseness (olfactory cortices): https://www.biorxiv.org/content/10.1101/2021.04.15.440031.full.pdf
- Bio-Inspired Hashing (FlyHash): https://arxiv.org/pdf/2001.04907
