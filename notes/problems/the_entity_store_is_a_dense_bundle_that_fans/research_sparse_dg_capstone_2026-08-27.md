# Capstone drill: optimal design + sparse DG for the exact-recall store

Fourth drill (owner: "consider this in sparse - right? ... research how this should be done optimally").
Via `research`. Full synthesis persisted here. Tags PINNED / OUR-INVENTION / PLAUSIBLE-BUT-UNTESTED. ASCII.

## HEADLINE
The already-built TWO-SYSTEM FACTORIZED store is independently convergent with the freshest neuroscience
AND the most precise published model -- it is not an engineering compromise:
- **Bausch et al. 2026 (Nature 650:690, pub. 7 Jan 2026; 3,109 human MTL neurons):** content (597) and
  context (200) are SEPARATE populations, bound by cross-population co-firing TIMING ("neuronal
  reinstatement"), NOT a shared conjunctive code. Direct human single-unit evidence for two systems.
- **TEM (Whittington et al. 2020, Cell 183:1249):** hippocampal code p = element-wise multiply (outer
  product) of content x and structure g -- separate streams, conjunctively bound ONLY AT STORAGE. Reconciles
  O'Reilly-Rudy (conjunction at p), Bausch (separate populations), TCM (graded context bound to items).

## Q1 -- SHARP store should be SPARSE (DG k-WTA): YES, real superlinear advantage (for CORRELATED patterns)
- Willshaw 1969: optimal ln(2)~0.69 bits/synapse; M ~ 0.45 N^2/(log N)^2. Treves & Rolls 1991/94:
  p_max ~ C/(a ln(1/a)) (C=conn/cell, a=sparseness); CA3 example C=12000,a=0.02 -> p_max~36,000. Dense
  Hopfield (Amit-Gutfreund-Sompolinsky 1985) ~0.138N with a CATASTROPHIC cliff. Dense ~0.14 vs sparse ~0.69
  bits/synapse = ~5x. PINNED.
- CRUX QUALIFIER: modern dense Hopfield (Ramsauer 2020 = transformer attention) exponential capacity ONLY
  for RANDOM/orthogonal patterns; correlated conjunctions (recurring entities/roles) are NOT covered ->
  sparse wins there. PINNED (papers' own theorems).
- HONESTY: sparse codes ALSO cliff (Tsodyks-Feigelman 1988 alpha~0.72), just at higher loading -- size with
  margin, don't expect soft failure.
- Kanerva SDM sparsity is a DIFFERENT axis (address sampling) -- does NOT give the content-sparsity boost;
  the win requires sparsifying the stored content vector's ACTIVITY LEVEL. PINNED.

## Q2 -- CRUX: sparsity COMPLEMENTS, does NOT DISSOLVE, the separation-vs-contiguity tradeoff
- Inside ONE population, gradedness is preserved under sparsification ONLY with axis-specific LSH
  (locality-sensitive hashing = similarity-preserving; fly olfactory expand+kWTA formalized as LSH), NOT
  generic random kWTA (Cayco-Gajic & Silver 2019 Neuron: aggressive sparsening collapses toward step-like,
  "excessive sparsening limits the coding subspace"). PINNED.
- The empirical DG record is split (Leutgeb 2007 DG graded under morph vs Neunuebel-Knierim 2014 DG cliff
  under cue-conflict) -- paradigm-dependent; DG's cliff is a FEATURE for exact recall, a bug only if applied
  to the context axis.
- Bausch 2026: the brain doesn't even attempt one-population binding -> two systems is the faithful answer.
- VERDICT: sparsity gives the SHARP system a capacity/cleanliness win, ORTHOGONAL to how the graded system
  solves contiguity. Our measured two-system store (fan 0.00, contiguity 0.58) is what both lines converge on.

## Q3 -- optimal content+context combination: separate streams, bind ONLY at storage (TEM outer product).

## Q4 -- optimal full architecture + minimal set (no single paper unifies all 5 components)
- Closest published: TEM; Vector-HaSH (Chandra 2025 Nature 638:739: factorized grid scaffold + heteroassoc,
  avoids the Hopfield memory cliff, uses "LSH with locality in the TEMPORAL domain" -- a published precedent
  for LSH-structured-for-time); "When and Where" (Yu 2026 bioRxiv: place/time = two modes of one CA3).
- LOAD-BEARING: DG-optimal-sparsity content code + diluted CA3 connectivity; separate action-driven
  multi-timescale graded context; TEM bind-only-at-storage; index/pointer separation (store a compact index,
  not full content, in the conjunctive code).
- CONTESTED (test before committing): CA3 iterative completion (Neher 2015: redundant/harmful under
  correlated EC input vs Nakazawa 2002: causally necessary); SR-layer vs grid-scaffold redundancy
  (Stachenfeld 2017: grid cells = SR eigenvectors -- a real identity claim, untested on our data).
- DO NOT BUILD: one shared sparse conjunctive population (contradicted by Bausch 2026); BPTT scaffold;
  generic uniform kWTA across the bound vector (contiguity collapse).

## BOTTOM LINE
Keep the two-system factorized store; make each half more faithful. SHARP half: DG expand+kWTA at
Treves-Rolls-optimal sparsity (a~0.02-0.05) instead of dense orthogonal bundling; dilute CA3 connectivity.
GRADED half: keep the action-driven multi-timescale leaky-integrator context; sparsify LSH-style if needed,
never generic. Bind only at storage. sparsity COMPLEMENTS (does not dissolve) the tradeoff.

## PRE-REGISTERED DECISIVE TEST (build next)
DG-sparsify the sharp store's content code at FIXED dimension, vary sparsity, CORRELATED content, measure
recall vs SCALE (out to ~4x). HARD-PASS: sparser holds/degrades-SLOWER than dense as scale grows
(Treves-Rolls superlinear signature), CI-separated. HARD-FAIL: no CI-separated improvement -> our codes are
not yet in the correlated-pattern regime where sparse pays off; defer sparsification.
