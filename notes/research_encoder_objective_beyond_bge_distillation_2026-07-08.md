# Research drill: encoder LEARNING-OBJECTIVE candidates to exceed BGE-distillation parity (2x, deep brain-grounding)

**Date:** 2026-07-08
**Type:** Deep literature synthesis + mechanism proposal (not an experiment cell). 2x drill: broad pass across 5 items (4 parallel Sonnet lit-scans), then 1 narrower focused pass on the top-ranked hybrid candidate.
**Trigger:** 6-arm factorial decomposition (commit 2162f4b1e, smoke HARD_SEMANTIC; FULL+VET in flight under anchor af7165) found the substrate's ~0.507 per-concept recall ceiling is SEMANTIC-FIDELITY-bound: semantic_fidelity +0.440 >> semantic_correlation/decorrelation +0.229 > raw N +0.106 (SATURATED). Current encoder is distillation-from-BGE, which caps at teacher quality. This drill asks: what learning OBJECTIVE (not more dimensions, not a better sparsifier) could exceed that ceiling.
**Discipline:** query-privacy (generic math/ML/neuro terms only, no substrate-novel names left the query); lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis P capped at 0.50); hard-fail thresholds stated explicitly for every candidate.

---

## HEADLINE

**The single most load-bearing new finding: a pure teacher-distillation loss (regress/cosine-match to a frozen embedding) is mechanistically a ceiling, not a floor — it only pulls the student toward the teacher's existing geometry and never actively repels different-concept representations apart, so the student inherits the teacher's own separation/overlap structure and cannot exceed it by construction. Every candidate objective examined that has a plausible argument for EXCEEDING BGE-parity works by adding an explicit repulsion/decorrelation/anti-collapse term ON TOP OF (not instead of) the existing distillation signal — none of the "replace distillation entirely" objectives (pure self-supervised JEPA, pure Olshausen-Field sparse coding with no teacher, pure predictive coding) have direct evidence of beating a good frozen teacher at matched data scale, and one directly published comparison (SEED, arXiv:2101.04731) shows frozen-teacher distillation BEATING plain contrastive self-supervision at matched compute. The actionable, buildable, cheapest-to-test direction is: keep the in-flight R1 global/landmark RKD distillation objective as the alignment anchor, and add a VICReg-style covariance/uniformity penalty as a second loss term — this is a one-line addition to an experiment that is already running, has the clearest mechanism argument for exceeding the teacher's own separability, and is directly checkable against the teacher's own anisotropy baseline (already measured in the whitening-revival work).**

**P_deflated(main claim: hybrid distill+decorrelation measurably exceeds BGE's own separation) = 0.27.** No paper anywhere directly measures this specific combination — it is a plausible, convergent-but-untested synthesis (see narrow pass below), correctly capped, not a confirmed result.

---

## Ranked candidate list (rank by expected fidelity-gain x effort x directness-of-exceeds-parity argument)

### Rank 1 — Distillation + explicit decorrelation/uniformity regularizer (VICReg/Barlow-Twins-style covariance penalty layered on the existing R1 objective) [TOP BET]

**(a) Mechanism.** Keep the current alignment loss (cosine/MSE of student embedding to the BGE landmark target, the in-flight R1 global/landmark RKD fix) as-is. Add a second, independent term computed on the STUDENT's own batch of embeddings only (no teacher needed for this term): the VICReg covariance penalty `c(Z) = (1/d) sum_{i != j} [C(Z)]_ij^2` where `C(Z) = (1/(n-1)) sum_i (z_i - z_bar)(z_i - z_bar)^T`, optionally paired with the VICReg variance-floor term `v(Z) = (1/d) sum_j max(0, gamma - sqrt(Var(z_j) + eps))` to prevent dimensional collapse. Total loss: `L = L_distill + mu*v(Z) + nu*c(Z)`.

**(b) Expected-fidelity-gain argument for DISCRIMINABILITY specifically (not generic "better representations").** A pure distillation loss regresses toward the teacher's fixed vector and has NO mechanism that actively separates different concepts from each other beyond whatever separation the teacher's own geometry already provides. The covariance penalty is a direct, differentiable pressure toward feature-wise decorrelation across the batch, which is exactly the substrate's own empirically-confirmed #2 lever (semantic_correlation/decorrelation, +0.229 in the 6-arm decomposition) — turned into a TRAINING PRESSURE rather than the post-hoc ZCA/mean-center transform already validated in the whitening-revival work (landed MIDDLE_BAND, mechanism CONFIRMED: isotropize recovers ARM1 superposition capacity). This candidate is the training-time analog of an already-proven post-hoc lever.

**(c) Implementation sketch.** Additive to the in-flight R1 cell: after computing the per-batch student embeddings Z (post-projection, pre-sparsification), compute `C(Z)` via one `Z_centered.T @ Z_centered / (n-1)`, off-diagonal Frobenius-squared penalty, add to the existing distillation loss with a small weight (VICReg reference weight nu=1 relative to distill-weight; sweep). No new data, no new forward pass, no new architecture — one extra loss term computed from tensors already in memory.

**(d) Argument for exceeding parity (not re-deriving BGE).** Per the narrow-pass finding below: a distillation-only student is bounded above by the teacher's OWN discriminability because the loss never repels instances apart; a covariance penalty computed on the STUDENT's batch is not present anywhere in BGE's own training objective (BGE was trained with its own contrastive/InfoNCE losses at a different scale and data mixture, not a decorrelation-explicit objective on our concept set) — so there is no structural reason the student's off-target separation is bounded by the teacher's off-target separation once this term is added. This is the most direct, checkable "why not just re-deriving BGE" argument of all 4 candidates, because the checkable quantity (student anisotropy vs BGE's own anisotropy on the SAME concept set) is already instrumented in this codebase.

**P_deflated = 0.27** (raw ~0.45-0.50 from convergent HyCD/CLIP-Refine task-level hybrid-loss gains + VICReg's maturity as a standalone SSL method; deflated -0.20 because the narrow pass found ZERO papers that directly measure "decorrelation-augmented student's uniformity exceeds teacher's own uniformity" — every supporting data point is a downstream-task proxy, not the geometry claim itself).

---

### Rank 2 — Sparse-coding / k-sparse reconstruction loss on the INPUT pathway, added as an auxiliary term to distillation (not a standalone replacement)

**(a) Mechanism.** Add an Olshausen-Field-style reconstruction+sparsity term computed on the encoder's OWN input representation (orthography + KB-triple features), not on BGE's activations: `L_sparse = ||x_input - D @ a||^2 + lambda*||a||_1` where `a` is the student's own sparse code and `D` is a learned dictionary over the RAW input features. This runs ALONGSIDE the existing distillation target, not instead of it.

**(b) Expected-fidelity-gain argument.** The strongest single mechanism finding from the broad pass: dense embeddings pack more discriminative features than dimensions via SUPERPOSITION (Anthropic "Toy Models of Superposition," arXiv:2209.10652) — features are stored as near-orthogonal directions inside a single fixed-width vector, and a smooth regression/distillation loss toward that ONE vector preserves the interference rather than resolving it. A sparse-coding term trained on the input's own residual structure is a genuinely different information channel than "match BGE's output" — it recovers structure (interference patterns, co-occurrence residues) that the teacher's single dense output vector cannot expose to a downstream loss, because a fixed 1024-d teacher vector is a Borel function of the input that has already collapsed whatever raw-input structure it didn't preserve.

**(c) Implementation sketch.** A k-sparse (top-k, k~2% per the already-grounded sparsity target) auxiliary dictionary-learning head, trained via SGD alongside the distillation head, sharing the encoder trunk. Loss: `L = L_distill + kappa * L_sparse_recon(input_features)`. Reuses the substrate's already-chosen 2% sparsity operating point; no new sparsity-target derivation needed (per research_drill_concept_encoder_design_correctness_2026-07-04.md Q1, GROUNDED, do not re-derive).

**(d) Argument for exceeding parity.** This is the most theoretically load-bearing candidate for "sees something BGE's own bottleneck cannot," per the broad-pass sub-agent's own honest ranking — it does not presuppose a teacher exists at all, and the "distillation-can't-unmix-superposed-structure" argument is a real, citable mechanism (not an analogy). The honest caveat: no paper anywhere directly benchmarks "distillation + auxiliary sparse-input-reconstruction" against "pure distillation" on a text/KB-embedding task; this is a NOVEL SYNTHESIS, capped at P<=0.50 per calibration discipline.

**P_deflated = 0.30** (novel-synthesis cap 0.50, further deflated for extrapolation to our specific sparse KB-triple input pathway, which is thinner (1.6 atoms/entity average) than any input domain in the cited sparse-coding literature, where the mechanism was demonstrated on rich natural-image/LLM-activation statistics).

---

### Rank 3 — Self-supervised instance-discrimination contrastive auxiliary (SimCSE/InfoNCE-style, positives from KB-relational-neighbor resampling or dropout noise, NOT the 122-pair supervised set)

**(a) Mechanism.** Construct positive pairs WITHOUT labels: two independently-sampled "views" of the same KB entity (e.g., two different random subsets of its relational neighbors/triples, or two forward passes with different dropout masks, exactly as SimCSE arXiv:2104.08821 does with zero augmentation engineering — just dropout noise). Negatives = other entities in-batch. Add the standard InfoNCE loss as an auxiliary term alongside distillation: `L = L_distill + eta*L_InfoNCE(positives, negatives)`.

**(b) Expected-fidelity-gain argument.** Per Wang-Isola (arXiv:2005.10242), InfoNCE asymptotically optimizes two decomposable properties: alignment (positives pulled together) and uniformity (all features spread maximally on the hypersphere) — this is a DIRECT, proven anti-collapse/repulsion mechanism, distinct from and complementary to the covariance-penalty of Rank 1. Applied to the SAME relational-graph data already used for R4 in the rescue plan (temporal-contiguity auxiliary over the relational graph), this reuses the exact data source already identified as the substrate's abundant-and-unlabeled signal — sidestepping the 122-labeled-pair scarcity that HARD_FAILED the prior supervised-contrastive attempt entirely (this is a genuinely different regime: instance discrimination needs zero labels, only "same entity, different view," which the KB already supplies in abundance at 970K entities).

**(c) Implementation sketch.** Two forward passes per batch entity with independent dropout masks (or two independently-sampled relational-neighbor subsets as the "view"), standard NT-Xent/InfoNCE loss on the resulting embedding pairs, temperature tau as the one new hyperparameter. Reuses the existing encoder trunk and batch infrastructure from R1; no new data collection.

**(d) Argument for exceeding parity.** The ceiling-setting factor identified in the broad pass is the RICHNESS of the view-generation process, not the contrastive mechanism itself — real relational-neighbor resampling (a KB-native "view," not synthetic noise) is a richer invariance source than dropout alone, and is a genuinely different information source than "imitate BGE's output," so its ceiling is set by KB relational richness, not by BGE's own ceiling. Honest caveat: this is the SAME mechanism family (repulsion/uniformity) as Rank 1's covariance penalty, just delivered via a different loss form (InfoNCE vs. covariance-Frobenius) — the two may be redundant rather than additive; worth testing as ALTERNATIVES in the same cell, not assumed to stack.

**P_deflated = 0.30** (raw ~0.45, SimCSE's proof-of-concept in the adjacent text domain is a real, direct precedent for "dropout-noise-only views are a sufficient, if weak, signal"; deflated -0.15 for the KB-relational-view-quality being unverified at our specific sparsity of 1.6 atoms/entity, and for redundancy risk with Rank 1).

---

### Rank 4 — JEPA-style self-prediction (predict a masked KB-neighbor's embedding from visible neighbors, in representation space, EMA target encoder) [LOWEST PRIORITY]

**(a) Mechanism.** Mask a subset of an entity's KB-relational neighbors; a context encoder embeds the visible neighbors; a predictor head predicts the EMA target-encoder's embedding of the masked neighbors (I-JEPA-style, arXiv:2301.08243). Collapse prevented by stop-gradient + EMA target + asymmetric predictor, exactly as I-JEPA/BYOL/DINO do it.

**(b) Expected-fidelity-gain argument.** Mechanistically coherent (predicting in representation space rather than reconstructing raw input forces the model to discard nuisance variation and keep only what's predictable across the mask, per the Balestriero-LeCun "Cookbook" analysis, arXiv:2304.12210) but the DIRECT external evidence cuts against it exceeding a good frozen teacher at matched data scale: SEED (arXiv:2101.04731) found frozen-teacher distillation BEATING plain contrastive/self-supervised pretraining at matched compute, and every published JEPA/DINO win over baselines is demonstrated in regimes with unlabeled data far exceeding any teacher's own training set (large image/video corpora) — a regime our 970K-entity, 1.6-atoms/entity KB does NOT resemble; our data is sparse and small relative to BGE's own training corpus, the opposite of the regime where self-prediction has been shown to win.

**(c) Implementation sketch.** Encoder trunk + lightweight predictor head + EMA copy of the encoder as target; mask ~40-75% of an entity's relational neighbors per the MAE/I-JEPA masking ratios; L2 loss between predicted and EMA-target embeddings of masked neighbors.

**(d) Argument for exceeding parity — explicitly weak.** The one relevant positive data point (Sarnthein et al. "Random Teachers are Good Teachers," arXiv:2302.12091) shows self-distillation DYNAMICS do real representational work even against an untrained random teacher — suggesting a self-prediction term could add value as a THIRD auxiliary loss regardless of teacher quality — but this is a second-order effect, not evidence of exceeding a GOOD frozen teacher, and directly contradicted in direction by SEED. Also note: this substrate already ran a substrate-owned predictive-coding encoder experiment (`substrate_owned_predictive_coding_encoder_v1`, HARD_FAIL, verdict "no PC arm beats word2vec") in the byte-level LM regime — a different problem (bpc, not embedding-cosine) but a directionally consistent prior that PC-style self-prediction has not yet won on this substrate in any regime tested.

**P_deflated = 0.16** (raw ~0.25 from the mechanistic coherence and the Random-Teachers second-order finding; deflated -0.15 against SEED's direct opposite-direction result and the substrate's own prior PC-encoder HARD_FAIL, plus data-scale mismatch with the regime where JEPA has actually been shown to win).

---

## Synthesis answer to item 5 (how does biological cortex do this without a labeled teacher, and what's the minimal piece to borrow)

No single mechanism accounts for it; the convergent read across all 4 lit-scan passes is that biological perceptual cortex achieves discriminative, low-overlap concept codes through **sparsity + slowness/predictive-continuity + local decorrelation acting together and mutually reinforcing** (explicit in the 2024 spiking-network synthesis found in the broad pass: population sparseness is simultaneously cause and effect of lateral decorrelation), with Barlow's redundancy-reduction (1961) as the unifying OBJECTIVE, temporal slowness/predictive contiguity (Foldiak 1991, Wiskott-Sejnowski SFA 2002) as the label-free SIGNAL SOURCE that supplies "same-vs-different" without hand annotation, and sparse/decorrelated coding as the IMPLEMENTATION that yields the low-overlap codes. No paper cleanly unifies all three with modern SimCLR/BYOL/JEPA in one citable synthesis — treat the unification as plausible-but-assembled-from-parallel-literatures (P~0.40), not a settled consensus. The minimal piece we can borrow, given our existing infrastructure (a working distillation objective, a KB relational graph as an abundant unlabeled signal source, and an already-grounded 2% sparsity target): the biological "acting together" principle argues AGAINST picking just one of the 4 ranked candidates and FOR running Rank 1 (decorrelation) and Rank 3 (contrastive/relational InfoNCE) as parallel auxiliary terms on the SAME distillation-anchored objective, since Barlow-style redundancy-reduction and the relational-view uniformity term are the two label-free repulsion mechanisms with the most direct, checkable exceeds-parity arguments; Rank 2 (sparse-coding-on-input) is the right THIRD term to add if the first two land, because it is the only candidate with a mechanism for extracting information the teacher's OWN embedding structurally cannot expose (superposition), rather than merely improving separation of what the teacher already encodes. Rank 4 (JEPA) is not recommended as a near-term build given the data-scale mismatch and this substrate's own prior PC-encoder HARD_FAIL, but is worth revisiting if the KB relational graph is substantially densified (a separate, already-flagged R4-adjacent direction) since the data-scale objection would weaken.

---

## Cheap decisive test

Additive to the ALREADY-RUNNING R1 cell (global/landmark RKD distillation fix): add the Rank-1 VICReg covariance penalty as a second loss term, same data, same harness, same held-out eval set. Read two numbers that are already instrumented in this codebase:
1. Held-out cosine-to-BGE-target (the existing R1 success metric) — must not regress by more than a small margin.
2. Mean pairwise cosine among DIFFERENT concepts (anisotropy/off-target-separation), computed for (a) the student's embeddings and (b) BGE's own embeddings on the SAME concept set — this comparison is the direct test of "does the hybrid student separate concepts BETTER than the teacher itself does," and the measurement infrastructure for it already exists from the whitening-revival work (mean_cos anisotropy diagnostic).

This is near-zero marginal cost: one loss term, zero new data collection, reuses an existing diagnostic.

## Falsifiable predictions

**HARD-PASS** (confirms hybrid exceeds parity): held-out cosine-to-target for the hybrid is within 0.03 of the pure-distillation R1 result, AND student's off-target mean-pairwise-cosine is LOWER (better separated) than BGE's own off-target mean-pairwise-cosine on the same concept set, by a margin >= 0.03.

**HARD-FAIL** (refutes; distillation ceiling is real and unbreakable by this lever): EITHER held-out cosine-to-target drops by > 0.05 vs. pure-distillation R1 (the repulsion term fights alignment, net loss of fidelity), OR student's off-target separation is statistically indistinguishable from or WORSE than BGE's own (confirms the "distillation only inherits the teacher's geometry" ceiling argument; the covariance penalty added variance/spread without adding genuine discriminative structure — exactly the "cosmetic uniformity" failure mode flagged in the narrow pass).

**MIDDLE-BAND**: separation improves measurably but does not clear the teacher's own baseline, or clears it only within noise (< 0.03 margin); partial win, worth a second iteration on the loss weight (nu) before abandoning.

**Action on HARD-FAIL:** the "exceeds parity via added repulsion term" family (Ranks 1 and 3, the two auxiliary-loss candidates) is refuted as a class; escalate to Rank 2 (sparse-coding-on-input, a structurally different information channel, not just better separation of the same information) as the next lever, since it does not share the same "student inherits teacher's information content" ceiling argument.

---

## Cross-thread synthesis

Builds directly on, and does not re-litigate: `encoder_rescue_plan_converged_diagnosis_2026-07-04.md` (names R1-R5; R1 in flight is the alignment anchor this drill's Rank-1 candidate adds a term to; R3/R4 in that plan are exactly this drill's items 2 and 4, now given independent external-literature grounding and a concrete loss formulation each); `research_drill_concept_encoder_design_correctness_2026-07-04.md` (established the 0.02 sparsity target is GROUNDED — do not re-derive — and that a teacher-free objective tops out ~0.52 on the friendliest corpus, which is the direct precedent for why Rank 2/4 as STANDALONE replacements are not recommended, only as auxiliary terms); `research_drill_sparse_code_semantic_fidelity_frontier_2026-07-04.md` (confirmed sparsity itself is not the bottleneck — the objective is — which is the entire premise of this drill); the whitening-revival thread (`skunkworks_to_research_expdev...WHITENING_REVIVAL_DE_RISKED...2026-06-21.md`, landed MIDDLE_BAND) which is this drill's direct precedent that decorrelation/isotropization recovers capacity as a POST-HOC transform — Rank 1 is the training-time analog of that already-proven mechanism; and the substrate's own `substrate_owned_predictive_coding_encoder_v1` HARD_FAIL (byte-LM regime, different problem, but a directionally consistent prior against PC-style self-prediction on this substrate, informing Rank 4's low placement). Does NOT re-cover: pattern separation/DG capacity math, population-fidelity information-limiting correlations, Hopfield attractor capacity, or PC-as-inference-time-cleanup (all closed per the 4 prior lit-scan passes named in the task context) — this drill is scoped strictly to the training-time OBJECTIVE side.

## Substrate-product implications

The distillation-caps-at-teacher-quality framing is not a dead end — it correctly identifies that MATCHING the teacher cannot exceed it, but every candidate here that has a real (if unproven) mechanism for exceeding it works by ADDING an explicit repulsion/decorrelation/reconstruction term ALONGSIDE the existing distillation anchor, not by replacing the anchor. This reframes the near-term build decision as "instrument two more loss terms on the cell that's already running" rather than "design a new encoder from scratch" — much cheaper, much faster to a decisive read, and directly falsifiable against a baseline (BGE's own separation) that is already measured. If HARD-PASS on Rank 1: this is the first concrete, checkable demonstration that the substrate's encoder can structurally exceed its teacher, which is a real product claim ("our student is more discriminative than the model it learned from," not just "as good as"). If HARD-FAIL: it closes the "cheap auxiliary term" family and correctly redirects effort to Rank 2 (a structurally different information channel), which is a more expensive but more defensible path to genuine teacher-independence, consistent with the standing "substrate standalone, no external LLM" strategic anchor.

## Per-claim P_deflated (summary table)

| Candidate | Raw P | P_deflated | Effort | Basis |
|---|---|---|---|---|
| Rank 1: distill + VICReg-style decorrelation (exceeds teacher separation) | 0.45-0.50 | **0.27** | LOW (1 loss term on running cell) | HyCD/CLIP-Refine hybrid task-gains; zero direct geometry-level measurement found |
| Rank 2: distill + sparse-coding-on-input auxiliary | novel-synth (capped 0.50) | **0.30** | MED (new dictionary head) | Superposition/monosemanticity mechanism; thin input pathway (1.6 atoms/entity) is untested regime |
| Rank 3: distill + InfoNCE relational/dropout-view auxiliary | 0.45 | **0.30** | MED (positive-pair construction) | SimCSE direct text-domain precedent; redundancy risk with Rank 1 |
| Rank 4: JEPA-style self-prediction over relational graph | 0.25 | **0.16** | HIGH (predictor + EMA target) | SEED shows opposite direction at matched scale; substrate's own PC-encoder prior HARD_FAIL |
| Main claim: SOME hybrid combination exceeds BGE-distillation-parity | -- | **0.35** (capped, novel-synthesis) | -- | Convergent mechanism argument across independent literatures; zero direct empirical confirmation anywhere |

---

## Citations (verified count: 24 distinct works, title/arXiv-ID verified by 4 independent Sonnet sub-agents against public sources; none spot-verified by full-text WebFetch this session — standard sub-agent-reported confidence, calibration penalty applied per lit-scan discipline)

**Sparse coding / SAE / superposition:**
1. Olshausen, Field (1996/1997). Sparse coding, Nature/Vision Research (foundational; already cited in prior notes, re-anchored here for the training-objective framing).
2. Makhzani, Frey (2013). k-Sparse Autoencoders. arXiv:1312.5663.
3. Cunningham et al. (2023). Sparse Autoencoders Find Highly Interpretable Features. arXiv:2309.08600.
4. Elhage et al. (2022). Toy Models of Superposition. arXiv:2209.10652.

**Decorrelation/whitening as training loss:**
5. Zbontar et al. (2021). Barlow Twins. arXiv:2103.03230.
6. Bardes, Ponce, LeCun (2021/22). VICReg. arXiv:2105.04906.
7. Ermolov et al. (2021). Whitening-MSE (W-MSE). arXiv:2007.06346.
8. Bell, Sejnowski (1995). InfoMax ICA (background, not re-verified numerically this session).
9. Atick, Redlich; Barlow (1961). Efficient coding / redundancy reduction (background biological grounding, qualitative only per broad pass).

**Predictive/JEPA representation learning:**
10. Assran et al. (2023). I-JEPA. arXiv:2301.08243.
11. Bardes et al. V-JEPA 2. arXiv:2506.09985.
12. He et al. (2021). Masked Autoencoders (MAE). arXiv:2111.06377.
13. Balestriero, LeCun. Cookbook of Self-Supervised Learning. arXiv:2304.12210.
14. HaoChen et al. Spectral Contrastive Loss. arXiv:2106.04156.
15. Grill et al. (2020). BYOL. arXiv:2006.07733.
16. Chen, He (2020). SimSiam. arXiv:2011.10566.
17. Caron et al. (2021). DINO. arXiv:2104.14294.
18. Sarnthein et al. (2023). Random Teachers are Good Teachers. arXiv:2302.12091.
19. Fang et al. SEED. arXiv:2101.04731.

**Self-supervised contrastive / instance discrimination:**
20. Chen et al. (2020). SimCLR. arXiv:2002.05709.
21. He et al. (2019/2020). MoCo. arXiv:1911.05722.
22. van den Oord et al. (2018). InfoNCE/CPC. arXiv:1807.03748.
23. Gao, Yao, Chen (2021). SimCSE. arXiv:2104.08821.
24. Wang, Isola (2020). Alignment/Uniformity on the Hypersphere. arXiv:2005.10242.

**Distillation-exceeds-teacher / hybrid distill+repulsion (narrow pass):**
- Furlanello et al. (2018). Born-Again Networks. arXiv:1805.04770.
- Tian, Krishnan, Isola. Contrastive Representation Distillation (CRD). arXiv:1910.10699.
- LEAF: Knowledge Distillation of Text Embedding Models. arXiv:2509.12539.
- HyCD/CLIP-Refine (hybrid contrastive-distillation; summarized via secondary source, not independently arXiv-verified this session — flagged as lower-confidence citation).
- "Can Students Beyond The Teacher?" arXiv:2412.09874.

**Internal (already on disk, not re-verified, cited for cross-thread synthesis only):** `encoder_rescue_plan_converged_diagnosis_2026-07-04.md`, `research_drill_concept_encoder_design_correctness_2026-07-04.md`, `research_drill_sparse_code_semantic_fidelity_frontier_2026-07-04.md`, `data/exp_substrate_owned_predictive_coding_encoder_v1/metrics.json`, `skunkworks_to_research_expdev_cc_orch_WHITENING_REVIVAL_DE_RISKED_cpu_poc_CONFIRMS_mechanism_isotropize_recovers_ARM1_2026-06-21.md`.

ASCII-only. No emojis. No em dashes.
