# Research drill: algebra-preserving semantic distillation (sparse bipolar code from dense teacher)

Date: 2026-07-04. Author: Research (Director). Type: focused false-win-guard drill.
Complements (does NOT duplicate) the Step 1b distillation cell being authored; that
builds a first working version, this finds the principled recipe + characterizes the
fundamental tension.

Concept-query-before-dispatch (USER-locked): ran
`substrate_query.sh "sparse bipolar code distillation semantic teacher FHRR bind unbind
invertibility orthogonality"`. Prior arc work on this concept: YES (not NONE) --
`notes/research_drill_hrr_capacity_vs_depth_2026-06-23.md` (DG orthogonalize-before-bind,
sparse coding) and `notes/research_drill_2x_orthogonal_role_basis_failure_revival_or_
close_2026-06-27.md` (orthogonality develops via learning, not init). This drill builds
on both.

Lit-scan calibration penalty applied (deflate P 0.15-0.25; cap novel-synthesis at 0.50).

============================================================================
## Q1 VERDICT (single most load-bearing output)
============================================================================

**The semantic-cosine-vs-invertibility tension AS POSED is DISSOLVED by the substrate's
binding structure. The real residual risk is a DIFFERENT axis -- SPARSITY-vs-algebra --
which is itself DISSOLVABLE by choosing the right code structure (sparse block codes +
block-local circular convolution) instead of an unstructured top-k code fed into FHRR.**

The false-win to guard is therefore NOT "high cosine breaks unbind". It is: "an
unstructured sparse code passes the semantic-cosine gate while silently degrading unbind
SNR, and the eval only checks cosine."

### Evidence that settles it (off-disk, hdlab)

The substrate does NOT bind raw concept codes to each other. It binds each concept filler
to a RANDOM role key and recovers by unbinding with that same random key, then cleanup:

- `hdlab/semantic_parser.py` L16-17 -- production composition:
  `input_hd = INTENT_WEIGHT*intent_codebook[intent_id] + sum_r bind(role_key[r], slot_dict[r][slot_id_r])`
- `hdlab/semantic_parser.py` L176-177 -- recovery: `unbound_r = hd_unbind(input_hd, role_keys[r])`, then k_NN_lookup cleanup on the per-role SHARDED slot dictionary.
- `hdlab/atoms.py` make_atoms -- role keys are INDEPENDENT RANDOM atoms (FHRR uniform-phase or HRR gaussian), generated with no reference to the concept codes' semantic geometry.
- `hdlab/binding.py` -- unbind is `c * b.conj()` (FHRR) or circular correlation (HRR).

Unbind of a bundle recovers `filler_r + crosstalk`, where
`crosstalk = sum_{i!=r} bind(key_r^{-1} (x) key_i, filler_i)`.
The crosstalk magnitude is governed by (a) mutual near-orthogonality of the RANDOM ROLE
KEYS (guaranteed by construction), and (b) bundle depth K (Plate capacity). **It is
independent of the fillers' mutual semantic overlap.** Distillation pulling cat/kitten to
0.85 cosine does not touch the unbind algebra -- the fillers are "protected" by being
multiplied by random keys. The two goals were assumed to fight over the SAME degree of
freedom; they do not. The role-key randomization decouples them. (This is the same
brain-analog insight in the 2026-06-23 drill: orthogonalize-at-the-key/expansion stage,
not the concept stage.)

### The residual tensions, ranked by real risk

1. **DEEPEST / SHARPEST: sparsity vs the algebra (orthogonal to semantics).**
   - **FHRR is a category mismatch for a sparse code.** FHRR atoms are unit-magnitude
     complex on ALL dims (`atoms.py` make_atom_fhrr: `complex(cos phi, sin phi)`). A
     k=20/1024 code has 1004 zero dims -> not unit-modulus -> not a valid FHRR atom.
     FHRR bind/unbind on a sparse real code is ill-posed. If the substrate mode is literal
     FHRR, sparsity and invertibility conflict DIRECTLY, before distillation even starts.
   - **General-sparse HRR (circular convolution) is LOSSY.** A sparse vector has norm
     sqrt(k) not sqrt(n); unbind SNR against full-energy crosstalk degrades (Frady/Kleyko/
     Sommer 2020; "random-projection binding works but is lossy").
   - **RECONCILIATION EXISTS and is provable: sparse block codes (SBC) + block-local
     circular convolution give LOSSLESS unbinding** (Frady/Kleyko/Sommer 2020; Hersche/
     Karunaratne/Rahimi "Factorizers for Distributed Sparse Block Codes" 2023). Partition
     N into K blocks of length L=N/K with ~1 active per block; bind/unbind blockwise. This
     yields exactly-invertible binding AND enforced sparsity simultaneously. This is the
     principled path.

2. **REAL but bounded/partly-desirable: semantic overlap vs cleanup exact-recovery margin.**
   After unbind, identifying WHICH filler needs cosine-argmax cleanup over the concept
   dictionary. At cat/kitten cosine 0.85 the cleanup margin shrinks and unbind noise can
   flip the argmax. But: (a) confusing semantically-close neighbors is DESIRED behavior,
   not an invertibility failure; (b) what must survive is CROSS-CLUSTER separability (cat
   vs airplane), which distillation preserves; (c) it is bounded by the same cosine-floor
   cleanup physics already documented in `hdlab/memory.py`. Graded cost, directly
   measurable, not a catastrophic false-win.

============================================================================
## Q2 -- distillation objective (ranked by expected impact on BOTH gates)
============================================================================

1. **PRIMARY: relational / similarity-distillation (RKD/RRD).** Match the teacher's
   PAIRWISE cosine matrix (distance-wise + angle-wise loss), NOT absolute vectors. This is
   theoretically correct here: it preserves NEIGHBORHOOD structure (what the 0.85 gate
   measures) while leaving absolute code placement FREE -- exactly the degree of freedom
   the block-structure/sparsification needs to satisfy the algebra gate. Lit: Park RKD
   2019, Relational Representation Distillation 2024.
2. **AUXILIARY: InfoNCE with teacher-derived positives + SEMI-hard negatives.** Preserves
   discriminability and cross-cluster separability; scales with negative count (lit: 4096
   negatives >> 1; 1-negative NCE == MSE).
3. **AVOID as primary: MSE-to-teacher regression.** Over-constrains absolute placement,
   fights the block-structure/orthogonality freedom, and is the worst false-win trap
   (hits cosine, silently kills unbind SNR). Lit: 1-negative NCE reduces to MSE.

Recommended objective: `L = alpha*RKD(student_cos, teacher_cos) + beta*InfoNCE(semi-hard)`,
NO absolute-MSE term.

============================================================================
## Q3 -- sparsification under distillation
============================================================================

- Unstructured top-k magnitude (current `concept_encoder.py` argpartition): hard,
  non-differentiable; gradient reaches only surviving k dims (dead-dim problem in a
  gradient-trained distillation).
- **RECOMMENDED: block-structured sparsity with per-block Gumbel-softmax straight-through.**
  Enforce ~1 active per block (K blocks). This (a) enforces k=K architecturally, (b) yields
  the SBC structure that makes unbind lossless (Q1), (c) keeps teacher gradient flowing via
  the soft relaxation (hard argmax forward, soft backward). Strictly dominates unstructured
  top-k for the dual gate.
- If staying unstructured: use straight-through top-k (forward hard, backward soft) to
  preserve teacher gradient. Second-best.

============================================================================
## Q4 -- hard-negative mining at 178K
============================================================================

- Mine from the BGE cache by teacher cosine, but sample from the SEMI-hard band
  (cosine ~[0.3, 0.6]), NOT the top-nearest. Critical subtlety in a distillation-of-
  SEMANTICS setting: the hardest teacher-neighbors are TRUE semantic positives that SHOULD
  stay close; mining them as negatives fights Goal 2. Lit confirms a limitation curve --
  benefit turns NEGATIVE past a hardness threshold.
- Count: monotone benefit up to ~thousands of negatives for NCE; use in-batch + ~5-20 mined
  semi-hard per anchor.
- Effect on algebra: negatives push codes APART (lower cosine) -> INCREASE cleanup margin /
  orthogonality -> HELP Goal 4. So negative hardness is the tuning knob between the gates:
  more/harder -> better algebra, worse semantic-neighborhood; fewer/softer -> the reverse.
  Set the operating point from the dual-metric below, not a priori.

============================================================================
## Q5 -- dual-metric operating point + GO/NO-GO (the false-win guard)
============================================================================

Run BOTH at EVERY checkpoint (fixed codebook M, production bundle depth K):

- **Metric A (semantic):** Spearman rank-correlation of the STUDENT pairwise-cosine matrix
  vs the TEACHER pairwise-cosine matrix on held-out concept pairs.
  GO >= 0.85 ; MIDDLE 0.70-0.85 ; NO-GO < 0.70.
- **Metric B (algebra):** bind -> bundle(M fillers at depth K) -> unbind -> cleanup
  accuracy@1, at fixed M and production K. Report also the continuous unbind SNR =
  cos(recovered, true) - max_distractor cos(recovered, distractor) as early warning.
  GO >= 0.95 recovery@1 ; NO-GO < 0.90.
- **FALSE-WIN GATE: reject ANY checkpoint with B < 0.90 REGARDLESS of A.** The catastrophic
  false win is A climbing to 0.85 while B silently falls.
- **Controls (mandatory):**
  (i) shuffled-key control -- unbind with the WRONG role_key must give near-zero cleanup;
      if not, fillers leak un-bound (degenerate code).
  (ii) sparse-vs-dense ablation -- run Metric B with the sparse block code AND a dense
       bipolar control. If sparse B << dense B, sparsity is the algebra-killer -> block
       structure is required, not optional.

============================================================================
## P_deflated -- "a code exists that hits 0.85 semantic AND passes FHRR unbind"
============================================================================

- LITERAL FHRR (dense unit-modulus) + sparse k=20 code: near-contradictory. P ~ 0.10-0.15.
  (This is the naive-path false-win trap: it will pass cosine and fail/degrade unbind.)
- Right algebra (sparse block codes + block-local circular convolution) + relational
  distillation + semi-hard negatives: lossless unbind is provable; relational objective can
  hit high rank-correlation. P ~ 0.45-0.50 that BOTH gates pass at production M/K.
- Honoring novel-synthesis cap (no paper does BGE-distill -> sparse-block-VSA jointly) and
  deflation: **headline P_deflated ~ 0.40**, conditional on adopting block-structure + the
  relational objective. On the naive top-k+FHRR+MSE path, ~0.12.

Confidence the dual-gate is SIMULTANEOUSLY satisfiable: MODERATE-and-conditional. Yes IF
the algebra is switched to sparse-block-code / block-local circular convolution (or the
concept-composition path is HRR, not literal FHRR) AND the objective is relational, not
absolute-MSE. NO on the naive path.

============================================================================
## Recommended changes to Step 1b design (route to authoring exp_dev)
============================================================================

1. **[HIGHEST IMPACT] Block-structured sparsity, not unstructured top-k.** K blocks of
   length L=N/K, ~1 active per block, so the code is a sparse block code compatible with
   lossless block-local circular convolution.
2. **Decide the algebra explicitly up front.** If the concept-composition path is literal
   FHRR (unit-modulus, `atoms.make_atom_fhrr`), a sparse real code is a category error --
   either switch the concept-filler composition to HRR / block-local circular convolution,
   or emit a dense phase code and drop Goal 3. Do NOT feed a top-k sparse real code into
   FHRR bind and check only cosine.
3. **Objective = relational similarity-distillation (RKD distance+angle) + InfoNCE with
   SEMI-hard negatives; NO absolute-MSE term.**
4. **Differentiable sparsification: per-block Gumbel-softmax straight-through** (hard argmax
   eval, soft backward) to keep teacher gradient.
5. **Add the dual-gate eval with the false-win guard + shuffled-key + sparse-vs-dense
   controls at every checkpoint** (Q5). Reject any checkpoint with Metric B < 0.90
   regardless of Metric A.

## Sources
- Frady, Kleyko, Sommer, "Variable Binding for Sparse Distributed Representations: Theory
  and Applications", 2020 (arXiv:2009.06734) -- sparse binding lossy; SBC + block-local
  circular convolution lossless.
- Hersche/Karunaratne/Rahimi et al, "Factorizers for Distributed Sparse Block Codes", 2023
  (arXiv:2303.13957).
- Park et al, "Relational Knowledge Distillation", 2019; "Relational Representation
  Distillation", 2024 (arXiv:2407.12073).
- "Contrastive Representation Distillation" (ICLR 2020); dense-retrieval distillation
  hard-negative limitation-curve literature (2024-2025).
- hdlab off-disk: semantic_parser.py, atoms.py, binding.py, memory.py, concept_encoder.py.
