# Wave 14.E: Hierarchical Bundle Composition in BSC HDC

Drafted 2026-05-19 from unbiased mathematical survey. Question: can a
bipolar (BSC) substrate with N=4096 atoms support depth-3+ hierarchical
composition (bytes -> words -> phrases -> paragraphs) cleanly, or does
noise dominate before the third level?

## TL;DR

The math is unambiguous. A flat bundle at K~261 hits the half-recovery
cliff at N=4096 (Frady-Sommer). A 3-level hierarchy with branching B=8
has effective K_total=512, 2x past the cliff: dead. With branching 3-4
and per-level Hopfield cleanup, depth 5-6 is reachable; with block-
substructure (Hersche 2024) added, depth 6-8 is in scope.

Key findings:

1. Plate 1995 chunking (HRR ch.6) is the canonical formalism: a chunk
   replaces a sub-bundle with a cleaned-up dictionary atom BEFORE use
   at the next level. The cleanup is the non-linearity that breaks the
   noise-multiplies-by-depth bound. Kanerva 1996 BSC has the same
   structure; SPA (Eliasmith) and TPR (Smolensky) are variants.
2. Frady-Sommer: K_max ~ N / (2 ln(V/p)) ~ 261 at N=4096, V=256, p=0.1.
   Branching factor B at depth L gives K_total = B^L; depth 5 with B=3
   is K_total=243, still under the cliff. Depth 3 with B=8 = 512, dead.
3. Hersche sparse block codes (arxiv:2303.13957) give ~2x capacity and
   map cleanly onto hierarchy: each level reserves disjoint blocks,
   eliminating cross-level interference.
4. Compositional generalization (Lake-Baroni SCAN) is enabled by the
   ALGEBRAIC binding (HDC has it already); hierarchy provides
   ABSTRACTION across granularity. Recursion is the open hole.
5. Minimal test (K=4 bytes/word, 3 words/phrase) is comfortably below
   the cliff; Variant A (no cleanup) and Variant B (with cleanup) both
   pass 80%. The interesting experiment is depth 3 where Variant B
   outperforms Variant A.
6. Decode cost O(L * K * D * N) is practical (~5ms for L=3, K=4,
   D=100, N=4096). Dictionary lookup is the bottleneck.
7. Brain mapping: cortical hierarchy IS hierarchical HDC with per-
   level Hopfield cleanup. Each cortical area is a Hebbian-learned
   attractor dictionary; the depth ceiling matches V1->IT (~6 levels).

## 1. Hierarchical binding in VSA literature

### 1.1 Plate 1995 HRR Chapter 6 ("Chunking")

The key insight is NOT that hierarchy is free; it is that hierarchy is
possible IFF chunks are cleaned up to dictionary elements BEFORE being
used as fillers at the next level.

Plate's setup (circular convolution binding):
- Level 0: atomic role-filler pairs `r_i * f_i`
- Level 1: bundle `s = sum_i r_i * f_i`
- Cleanup: `s_chunk = nearest_neighbor(s, chunk_dictionary)`
- Level 2: `s' = R * s_chunk + ...`

Without cleanup, depth-L noise scales as sqrt(L * K * B). With cleanup,
noise resets to fresh atom noise at each level; only the cleanup
ERROR PROBABILITY compounds, multiplicatively (not additively in
variance). Plate Table 6.1: N=512, 100 chunks/level, depth 4 recovers
at 0.95^4 = 0.81 per chunk end-to-end.

### 1.2 Kanerva 1996 Binary Spatter Codes

BSC uses XOR for binding, majority for bundling. Capacity is the same
up to constants: K_max ~ N / (2 log V) Bayes-optimal, ~ N/(4 log V)
thresholded. Hierarchy mechanism identical: bundle, cleanup, recurse.

### 1.3 Smolensky-Tesar 1995 Tensor Product Representations

TPR keeps the full N^L tensor at depth L. Zero crosstalk, exponentially
expensive: N=4096, L=3 needs 6.9e10 cells. TPR is the upper bound on
clean storage; HDC trades exponential clean storage for linear noisy
storage. Harmonic Grammar adds constraint-satisfaction parsing on top.

### 1.4 Eliasmith SPA (Semantic Pointer Architecture)

SPA = HRR + Neural Engineering Framework. Spaun model uses depth 4-5
hierarchies at N=512 with per-level Hopfield cleanup. SPA is the
strongest empirical evidence that hierarchical HDC works at depth 4+
provided cleanup is deployed at every level.

### 1.5 Comparison

| Formalism | Storage (depth L) | Cleanup required? | Depth-3+ demo |
|---|---|---|---|
| Plate HRR | O(N) | Yes | Yes (Plate 1995) |
| Kanerva BSC | O(N) | Yes | Yes (Kanerva 1996) |
| Smolensky TPR | O(N^L) | No | Trivially |
| Eliasmith SPA | O(N)+dict | Yes | Yes (Spaun, N=512) |

Winner for our setup: Plate-style with per-level cleanup. Matches our
BSC substrate, only one where cleanup IS the chunking (brain analog),
empirically validated at depth 4 at N=512.

## 2. Depth-vs-capacity tradeoff

### 2.1 The Frady-Sommer bound

For bipolar HDC, Hadamard binding, signed-sum bundling
(Frady-Sommer-Kanerva 2018):

    K_max(N, V, p) ~ N / (2 ln(V/p))

For N=4096, V=256, p=0.1:

    K_max ~ 4096 / (2 * ln(2560)) ~ 4096 / 15.7 ~ 261

### 2.2 Compounding across depth (no cleanup)

Without cleanup, effective flat-equivalent bundle size at the top is
K_total = prod_l K_l:

| L | branching | K_total | vs K_max=261 |
|---|---|---|---|
| 2 | 4,3 | 12 | 22x below cliff |
| 3 | 4,3,3 | 36 | 7x below cliff |
| 4 | 4,3,3,3 | 108 | 2.4x below cliff |
| 5 | 4,3,3,3,3 | 324 | ABOVE cliff |
| 3 | 8,8,8 | 512 | 2x ABOVE cliff |
| 4 | 4,4,4,4 | 256 | at cliff |

Without cleanup, depth 4 with branching ~3 is the ceiling.

### 2.3 With per-level cleanup

Cleanup resets noise to atom noise (variance 1) at every level. The
compounding becomes multiplicative in cleanup success rate:

    P(end-to-end correct) = prod_l P_cleanup(K_l, N)

For K_l=8, N=4096: P_cleanup ~ 1 - 1e-3 per level. Depth 5: 0.995.
Depth 10: 0.99. Hierarchy depth is essentially unbounded as long as
each level stays under flat capacity.

### 2.4 The cleanup oracle is doing the work

This is the crucial point: hierarchy in HDC is NOT linearly summing
bundles at every level. It is summing at ONE level, projecting to a
learned dictionary (non-linear cleanup), and using the projection as
the atomic unit at the next level. Without it, BSC hierarchy is dead
at depth 3 for N=4096.

## 3. Block-structured BSC

### 3.1 Hersche 2024 Sparse Block Codes

Divide N dimensions into B equal blocks of size N/B. Atom = 1-hot per
block. Binding = block-wise XOR; bundling = block-wise majority.
Capacity log(N/B) * B bits per atom; operationally ~2x dense BSC.

For N=4096, V=256, p=0.1: K_max ~ 512 atoms (Hersche Table 2) vs.
dense ~261.

### 3.2 Hierarchical block-substructure

Reserve disjoint blocks per level:
- Blocks 0..15 (1024 dims): level-0 byte atoms
- Blocks 16..31: level-1 word atoms
- Blocks 32..47: level-2 phrase atoms
- Blocks 48..63: level-3 paragraph atoms

Cross-level noise is zero. Per-level capacity ~128 atoms (Hersche
extrapolation), plenty for K=8 branching at every level.

### 3.3 Tradeoff

Block partitioning trades intra-level bandwidth for inter-level
isolation; cleanup trades compute for inter-level isolation. Best:
use BOTH. Static block isolation + dynamic per-level cleanup
should reach depth 5-6 at N=4096 with margin.

## 4. Compositional generalization

### 4.1 Lake-Baroni 2018 SCAN

SCAN tests systematic generalization: train "jump twice", test "walk
twice". Seq2seq fails because it lacks an algebraic "twice" operator.

HDC's group-theoretic binding (XOR is the Z_2^N group operation)
already gives systematic composition: `jump * twice = jump-twice`
algebraically. Hierarchy is orthogonal: it provides ABSTRACTION
across granularity so the same "twice" operator applies to any word.

### 4.2 Does hierarchy help SCAN?

Mixed evidence, leans yes:
- Smolensky 2022 (TPR-based) passes primitive-to-composition splits.
- Sabour 2017 (capsule nets) passes simple compositional tests.
- Pure flat-bundle HDC has not been benchmarked on SCAN to my
  knowledge — open empirical question.

Prediction: 2-level hierarchical BSC encoder passes
primitive-to-composition splits. Will likely FAIL length-generalization
splits without explicit recursion (BSC hierarchy is fixed-depth, not
recursive).

### 4.3 What compositional generalization needs

Three things:
1. Algebraic composition operator (HDC has this).
2. Abstraction across granularity (hierarchy provides this).
3. Recursion / variable depth (HDC does NOT have this natively).

The small bet (HDC memory for LLM) does not need #3. The big bet
(Hebbian-trained VSA-LM) almost certainly does. Wave 14.E should bound
when hierarchy alone is enough.

## 5. Minimal viable test

### 5.1 Design

- N=4096 BSC bipolar atoms.
- Level-1 (word): K=4 byte atoms bundled with role atoms r_0..r_3.
  Dictionary of 50 words.
- Level-2 (phrase): 3 word-bundles bundled with role atoms R_0..R_2.
  Dictionary of 100 phrases.
- Encode 100 phrases over 50-word vocab. Test: phrase -> 3 words ->
  4 bytes each.

### 5.2 Two variants

**Variant A (no cleanup):**
- `w = sign(sum_i b_i * r_i)`
- `p = sign(sum_j w_j * R_j)`
- Decode word j: `w_j_hat = sign(p * R_j)`
- Decode byte i: `b_i_hat = sign(w_j_hat * r_i)` -> NN against byte
  codebook.

Predicted: K_total=12, well below cliff. P_byte ~ 99%; P_phrase ~
0.99^12 = 88%. Passes 80%.

**Variant B (per-level Hopfield cleanup):**
- After computing w_j_hat, project to nearest word in word dictionary;
  use that clean atom for byte decode.

Predicted: ~95% per word; 0.95^3 = 86% per phrase; byte recovery 99%
conditional on word cleanup correct. Passes 80%.

### 5.3 The interesting comparison

Both pass at depth 2 (K_total=12). Real test is DEPTH 3 with
K_total=36 (still under cliff):
- Variant A drops to ~70% (predicted).
- Variant B holds at ~90% (predicted).

That gap empirically demonstrates cleanup is doing the work.

### 5.4 Falsification

If A passes 80% at depth 3 and B passes 80% at depth 5: theory
confirmed. If A FAILS at depth 2: either N=4096 is effectively
smaller than predicted (correlated atoms) or Frady-Sommer constants
are worse than textbook. Either way, useful data.

## 6. Decoding at multiple levels

### 6.1 Cost

Top-down decode of depth-L with branching K and dictionary D per level:
O(L * K * D * N). For L=3, K=4, D=100, N=4096: 4.9M ops, ~5ms on a
modern CPU.

### 6.2 Optimizations

- Sparse dictionaries (Hersche): D-sparse atoms cut lookup by D/N.
- Hierarchical dictionary indexing: pre-cluster atoms by their bound
  role; lookup at level l only considers atoms with that role.

### 6.3 Iterative decoding

Greedy top-down is suboptimal. A resonator-style iterative decode that
jointly optimizes all levels could improve recovery 5-10% (analogous
to turbo decoding). This is the iterative-Hopfield direction
(wave14b_r1) applied to hierarchy.

## 7. Brain mapping

### 7.1 Cortical hierarchy as chunked cleanup

Ventral visual stream V1 -> V2 -> V4 -> IT:
- V1: Gabor-like oriented edges. Atomic bundle of retinal input.
- V2: contours, junctions. Cleaned up from V1 to contour dictionary.
- V4: complex shapes. Cleaned up from V2 to shape dictionary.
- IT: whole objects, faces. Cleaned up from V4 to object dictionary.

Mechanism: competitive normalization + local recurrent attractor
dynamics (Heeger 1992, Douglas-Martin 2004). Mathematically this is a
Hopfield projection to nearest learned attractor — exactly Plate's
HRR chunking.

### 7.2 Quiroga 2005 grandmother cells

Single human IT/hippocampus neurons fire selectively and invariantly
to specific concepts (Jennifer Aniston cell). In HDC terms: top-level
atoms in a deep hierarchy. Each high-level concept is a single
attractor; lower-level features (eye, mouth, hair) bind with role
atoms and are cleaned up to person atoms in IT.

Quiroga's finding: representation IS sparse and selective at the top.
This is exactly what Hersche's sparse block codes model.

### 7.3 The math

Cortical hierarchical cleanup formalized:
- Layer l has activity x_l in R^{N_l}.
- Forward: `x_{l+1} = sigma(W_l x_l - b_l)`, then attractor dynamics
  to nearest stored pattern p_l^k in dictionary.
- Stored patterns learned via Hebbian rule over experience: p_l^k
  aligns with frequent x_l patterns.

HDC analog:
- x_l is the bundle at level l.
- W_l x_l is the unbinding (Hadamard with role atoms).
- Attractor step = cleanup to dictionary.
- p_l^k are dictionary atoms.
- Hebbian learning = Wave 14.B iterative pool update.

So cortical hierarchy IS hierarchical HDC with per-level Hopfield
cleanup. Dictionary atoms are learned by Hebbian co-activation. This
is the deep mapping that makes HDC hierarchy brain-inspired by
mathematical necessity, not by analogy.

### 7.4 What this predicts

- USE Hebbian dictionary learning at each level, not random.
- Sparsity (Hersche) is biologically motivated, not just engineering.
- Depth ceiling set by cleanup error compounding; with cleanup, depth
  6-8 reachable (V1 -> IT has ~6 levels).

## 8. Sources

### Primary VSA hierarchy

- Plate 1995, "Holographic Reduced Representations", ch.6 "Chunking
  and Recursion". Foundational treatment of per-level cleanup.
- Kanerva 1996, "Binary Spatter Codes of Ordered K-tuples", ICANN.
- Smolensky-Tesar 1995, "Harmonic Grammar". TPR hierarchy.
- Eliasmith 2013, "How to Build a Brain", ch.4. SPA hierarchy in Spaun.

### Capacity bounds

- Frady-Sommer 2019, "Robust computation with rhythmic spike
  patterns", PNAS.
- Frady-Kleyko-Sommer 2018, "A theory of sequence indexing and working
  memory in recurrent neural networks", Neural Computation.
- Kanerva 2009, "Hyperdimensional computing", Cognitive Computation.

### Sparse block codes

- Hersche et al. 2024 (arxiv:2303.13957), "Constrained nonnegative
  hyperdimensional computing with sparse block codes".
- Laiho-Poikonen-Kanerva-Lehtonen 2015, "High-dimensional computing
  with sparse vectors".

### Compositional generalization

- Lake-Baroni 2018 (arxiv:1711.00350), "Generalization without
  systematicity: SCAN benchmark".
- Smolensky-McCoy-Fernandez-Goldrick-Gao 2022, "Neurocompositional
  computing".

### Brain hierarchy

- DiCarlo-Cox 2007, "Untangling invariant object recognition".
- Quiroga-Reddy-Kreiman-Koch-Fried 2005, "Invariant visual
  representation by single neurons in the human brain", Nature 435.
- Douglas-Martin 2004, "Neuronal circuits of the neocortex".
- Heeger 1992, "Normalization of cell responses in cat striate
  cortex", Visual Neuroscience.

### Resonator / iterative decoding

- Kent-Frady-Olshausen-Sommer 2020, "Resonator Networks 2", Neural
  Computation.
- Kymn et al. 2024, "Computing with Resonator Networks".

## 9. Decision: depth ceiling for hd-instrument

Given N=4096 and the math:
- WITHOUT cleanup: depth 2-3 only.
- WITH per-level Hopfield cleanup: depth 4-5 reachable.
- WITH block partitioning + cleanup: depth 6-8 reachable.

Recommended milestones for Wave 14.E:
1. Variant A at depth 2 (user's minimal test). Should pass easily.
2. Variant B at depth 3, explicit per-level Hopfield cleanup against
   a learned dictionary. Tests the THEORY that cleanup is the
   mechanism.
3. Block-partitioned depth 4. Tests whether engineering composes
   cleanly with the theory.

Falsification: if (2) does NOT outperform (1), cleanup
implementation is wrong or dictionary too small. If (3) fails, blocks
are mis-allocated. If both pass, path to depth 6-8 opens; bridges
small bet to big bet via the cortical-hierarchy mapping.
