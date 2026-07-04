# Research drill — BRAIN 5x angle 2/5: how the brain preserves near-neighbor RANK through competitive k-WTA sparsification

Date: 2026-07-04
Author: Director (research drill, angle 2 of 5)
Drill class: brain-mechanism synthesis (SHARP, not exhaustive)
Problem owner: concept-encoder rescue (distill BGE-large 1024d dense -> K-block bipolar sparse code)

## The exact failure this drill targets

Annealed training learns EXCELLENT dense geometry: ret_agree10 = 0.65 on the pre-sparse
(graded) code. Pass that same code through **block-argmax k-WTA** (divide vector into K
blocks, argmax within each block -> one-hot-per-block, bipolarize) and retrieval **collapses
to 0.04**. 3/4 goals met at ~2% sparse; the one gap IS this sparsifier. Raising K
(128->512, i.e. keeping MORE winners) walks retrieval 0.21 -> 0.41 — a direct dose-response
signature that the sparsifier, not the geometry, is the lossy stage.

USER: "this should be EASIER — why can't we?"

## WHY naive block-argmax destroys rank (two mechanistic causes)

The dense->sparse map is `f(x) = per_block_argmax(x)`. It collapses rank for two reasons a
neuroscientist would name immediately:

**C1 — Boundary chaos (non-Lipschitz winner-flip).** argmax is discontinuous. When two
coordinates in a block are near-ties, an epsilon perturbation flips the winner. Two inputs
that are cos=0.95 apart in dense space have MANY near-tie blocks; their one-hot patterns
diverge chaotically. The map from a dense neighborhood to the sparse lattice is not
locally smooth, so cosine-rank does not survive it. This is the dominant term: it is
exactly why relaxing to more winners (K512) partially rescues — more winners = more of
the pattern is set by decisive (non-tie) coordinates.

**C2 — Forced-winner + magnitude discard.** Block-argmax forces EXACTLY one winner per
block *even in blocks with no strong drive* (spurious "noise winners" that carry no
similarity signal) AND throws away all graded magnitude. The near-neighbor similarity in
a good dense code lives in the fine graded activation values; one-hot-per-block keeps only
"which unit won," discarding the very gradations that encoded proximity.

Root cause under both: **train/eval metric mismatch.** Training preserved cosine on the
*graded* code; the sparsifier preserves *support-identity overlap* on a coarse lattice.
The gradient never faced the true hard-argmax collapse, so the encoder parked near-neighbor
info in magnitude gradations (C2) and left winners undecided at boundaries (C1).

## HOW the brain runs k-WTA WITHOUT this collapse

The brain sparsifies aggressively (cerebellar granule layer, mushroom-body Kenyon cells,
piriform, cortical L2/3) yet preserves similarity for near-neighbors. Four mechanisms, each
attacking one of our failure modes:

**M1 — Graded survivors, not one-hot.** Biological k-WTA sets a *threshold* (via feedback
inhibition) that only the top few % exceed, but survivors keep GRADED firing rates
proportional to drive. Similarity is preserved in the analog values of the active set, not
just its identity. Zeroing the *smallest* coordinates barely moves cosine (they carry least
direction) — this is why keep-graded-top-k is near-isometric while one-hot-argmax is not.
[fixes C2]

**M2 — Global adaptive threshold, NOT per-block argmax.** Inhibition (e.g. the fly APL
feedback neuron, cortical basket cells) pools over the WHOLE population and adapts a single
threshold so ~k% of the *population* survives — a GLOBAL top-k, not a partitioned per-block
winner. Global top-k never forces a winner in an uninformative block (kills C2 noise
winners) and lets two strongly-driven units in the same "block" both survive. Per-block
argmax is a rigid partition the brain does not impose. [fixes C1 forced-winner + C2 noise]

**M3 — Expansion BEFORE sparsification = provable LSH (the fly/cerebellum trick).** Kenyon
cells expand ~50 projection neurons -> ~2000 KCs; granule cells outnumber mossy inputs
~100:1. Sparse random projection to a MUCH higher dimension, THEN winner-take-all, is
literally locality-sensitive hashing with a proven near-neighbor guarantee
(Dasgupta-Stevens-Navlakha, *Science* 2017, "FlyHash"). Expansion is what makes WTA
locality-sensitive — it spreads near-ties apart so winners become decisive. Our block-argmax
runs on ~equal-or-compressed dimension (K128 at 3.125% => dim 4096, block size 32), the
OPPOSITE regime: it compresses and forces collisions/boundary chaos. [fixes C1]

**M4 — Homeostatic per-unit boosting.** Intrinsic-excitability homeostasis drives every unit
to fire equally often (max-entropy code, no dead units, no "hog" units that always win).
This is exactly Numenta's Spatial-Pooler boost term and the APL/homeostasis pairing in the
fly. Without it, uneven per-coordinate scale in the encoder makes a few units win every
block regardless of input — destroying rank. A learned/running per-coordinate bias
subtracted before top-k enforces uniform usage. [fixes a hidden C1 contributor]

## The provable backbone (is rank-preserving sparsification a real thing? yes)

- **FlyHash (Dasgupta et al. 2017):** sparse random expansion + WTA => LSH; tag Hamming
  distance provably tracks input distance for near-neighbors. Directly our setting.
- **WTA-hash (Yagnik et al. 2011):** ordinal/rank-based hash; preserves rank BY CONSTRUCTION
  because it encodes pairwise ordinal comparisons (rank-invariant to monotone rescaling).
- **SimHash (Charikar 2002):** sign of random projections preserves ANGULAR (cosine)
  distance provably. Our bipolar sign-code is SimHash-adjacent — but block-argmax is NOT
  SimHash; the argmax nonlinearity is what breaks the guarantee.

Takeaway: locality-sensitive sparse coding is a solved problem *when you expand-then-WTA or
use ordinal/sign codes*. Our failure is that we compress-then-argmax.

## CONCRETE untried sparsifier (implementable spec)

**Name: BOOSTED-GLOBAL-TOPK with straight-through winner-MARGIN, dual (graded+sign) readout.**
Replace `per_block_argmax` with:

1. **Learned expansion** to D >> 1024 (e.g. D = 8k-16k) via a sparse random or learned
   projection (M3). Optional but high-value; test with and without.
2. **Homeostatic boost** b_i: subtract a running per-coordinate bias driving each unit toward
   equal win-frequency (M4). `z_i = a_i - b_i`, update `b_i += eta * (winfreq_i - target)`.
3. **GLOBAL top-k** over the whole boosted vector (M2), NOT per-block argmax. k = target
   active count (2% of D).
4. **Graded survivors** kept for the RETRIEVAL metric (M1): survivors keep value (or
   normalized value); non-survivors zeroed. Cosine is near-preserved.
5. **Dual readout to satisfy bipolar-algebra:** the SUPPORT + SIGN of survivors is the
   bipolar code for clean bind/unbind SBC algebra; the GRADED survivor values feed
   retrieval scoring. One forward pass, two heads — resolves the graded-vs-bipolar tension
   without a second code.
6. **Straight-through winner-MARGIN loss (trains the sparsifier IN the loop, fixes C1):**
   forward = hard global-top-k; backward = soft top-k (temperature-annealed). Add a margin
   penalty pushing (k-th survivor) - (k+1-th loser) above a margin m, so the support becomes
   STABLE to input perturbation (decisive winners, no near-ties). This is the single change
   that most directly targets the boundary-chaos root cause the annealing missed.

**If forced to name ONE lever:** swap per-block argmax for **homeostatic-boosted GLOBAL
top-k with graded survivors** (steps 2-4). It removes the forced-noise-winner and
dead/hog-unit failure modes that per-block argmax *structurally* creates, requires no
architecture change beyond the sparsify op, and is directly testable as an ablation against
the current 0.04 baseline. The margin loss (step 6) and expansion (step 1) are the next two
increments if the swap alone under-delivers.

## Prior-work overlap (substrate KB concept-query run per discipline)

Query "k-WTA ... preserve near-neighbor rank locality sensitive sparse code", tau=0.15, k=5:
- Top hits are block-sparse RIP capacity (`research_drill_sparse_key_composition_partners_2x`,
  cos 0.287) and adaptive sparsity (`..._substrate_training_speed_design_space_2x`) — about
  CAPACITY under sparsity, NOT rank-preservation through the sparsifier. Tangential.
- `design_stage2_concept_encoder_spoke1_v3_WTA_base_PC_multiplicative_top_down_gain` and
  `spoke3_sparse_hippocampal_pattern_separation` are the on-topic encoder notes but point at
  the OPPOSITE operation: DG-style **pattern SEPARATION / decorrelation** (maximize distinct-
  ness). **CONFOUND FLAG:** the brain does separation (DG) AND similarity-preservation
  (mushroom body / cerebellum LSH) in DIFFERENT structures. Our goal is the LSH-like
  similarity-PRESERVING sparse code, so we should copy the KC/granule (expand+WTA) circuit,
  NOT the DG separator. Prior encoder work leaned separator-side; this angle is the missing
  half.
- Prior arc work on THIS specific concept (rank-preserving / LSH sparsification, homeostatic
  boosting, margin-annealed hard WTA): **NONE found.** Not a rediscovery.

## P_deflated

Claim scored: "some variant of boosted-global-topk (+/- margin/expansion) recovers retrieval
to the >=0.35 target at ~2% sparse while preserving bipolar algebra."
- Strong independent evidence each lever helps: dose-response already visible (0.21->0.41 by
  relaxing sparsity => magnitude/decisiveness matters); FlyHash is a proven LSH result;
  homeostatic boosting is established (Numenta, fly).
- Real integration risk: the bipolar-algebra requirement (clean bind/unbind) may fight
  global (non-per-block) support and graded survivors; dual-readout may not give as clean an
  algebra as fixed-block one-hot.
- Raw P ~0.62; lit-scan calibration + novel-synthesis integration risk => deflate ~0.17;
  cap novel-synthesis at 0.50.
- **P_deflated = 0.45.**
