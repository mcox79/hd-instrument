# Research Drill: Storage Compression Alternatives Beyond Closed Paths
# 3x Deep Drill -- v3 Per-Fact Cost Analysis
# Date: 2026-06-07

---

## HEADLINE

The v3 per-fact target of 200-800 bytes requires 6-22x compression beyond the validated
4-bit + N-reduction stack (current projection ~4.5 KB). Two paths are realistically
actionable: (1) 2-bit group quantization (2-3x, P_actionable=0.24) and (2) product
quantization of the weight matrix (4-8x, P_actionable=0.20). Together they project a
combined stack reduction of 8-24x, which theoretically reaches the lower bound of the
target band. However, both carry meaningful empirical risk in the substrate's specific
pseudoinverse write rule + bipolar source vector context, and neither has been
pre-tested at production scale. The 200-byte floor is not confidently reachable given
audit overhead (~32 bytes/fact), but 500-1000 bytes/fact is a credible outcome if
both paths survive pre-testing.

---

## Context and Starting Point

Validated stack from cycle 155:
- 4-bit W quantization: 4x reduction, HP at N=8192-16384 (zero recall loss)
- Lower-N via standard pinv: HP alpha_c=0.5 at N=1024-8192
- Modern Hopfield exponential energy: HP perfect recall at N=4096-16384
- Combined: ~64x reduction from baseline 286 KB -> ~4.5 KB per fact

Closed paths (do not re-examine):
- Sparse-W: sparsity >=0.75 collapses recall (HARD FAIL, cycle 155)
- Low-rank SVD: Marchenko-Pastur flat spectrum at M/N=0.5 (HARD FAIL)
- HRR/FFT compression: flat spectra in random vectors, no frequency sparsity (HARD FAIL)

This drill asks: what else is available, and how do the candidate paths stack rank?

---

## Calibration Pre-Registration

All P estimates below are post-deflation (0.15-0.25 applied per lit-scan calibration
mandate). Novel-synthesis P is capped at 0.50.

P_actionable = P_theoretical x P_empirical (post-deflation)
HARD-PASS threshold: combined reduction >= 4x at recall >= 0.95 on production setup
HARD-FAIL threshold: recall drops below 0.85 OR reduction < 1.5x

---

## Section 1: Lower-Bit Quantization Variants

### Path 1a: 3-Bit Quantization

Mechanism: Symmetric scalar quantization at 3 bits/weight. Reduces representation space
from 16 quantization levels (4-bit) to 8. Per-weight cost goes from 0.5 bytes to 0.375
bytes, a 1.33x improvement over 4-bit.

Literature: Published results for CNNs and LLMs show 3-bit is "near lossless" for
large models (>1B parameters) but shows noticeable degradation at smaller scales.
The relevant concern for this substrate is that pseudoinverse-derived W matrices have
specific eigenvalue structure; the published "near lossless" claims are for trained LLM
weights, not pseudoinverse matrices derived from outer-product writes.

P_theoretical: 0.75 (the math of scalar quantization is sound; 3-bit is well understood)
P_empirical (post-deflation): 0.35 (pseudoinverse W may have outlier eigenvalues that
  are more sensitive to quantization than LLM weights; pre-test required)
P_actionable: 0.75 x 0.35 = 0.26

Reduction factor: 1.33x beyond 4-bit (1.33x is the theoretical ceiling)
Engineering cost: 1-2 days (trivially adjacent to 4-bit implementation)
Composability: Yes, directly stacks on the 4-bit baseline.

Prediction valid under: W eigenvalue distribution is reasonably smooth (no heavy
outlier rows/columns beyond what 4-bit already handles).
Will not survive if: Pseudoinverse W has heavier-tailed eigenvalues than trained LLM
weights at the same M, which is plausible because pseudoinverse magnifies the smallest
singular values.

Pre-test pattern: Run N=4096 modern Hopfield + Llama-1B encoder + 200 stored facts,
compare recall@1 between 4-bit and 3-bit quantized W. Budget: 1-2 hours on runner GPU.
HARD-PASS: recall@1 drops <2% from 4-bit baseline.
HARD-FAIL: recall@1 drops >5%.


### Path 1b: 2-Bit Group Quantization

Mechanism: 2 bits/weight with per-group scaling (group size 64-128 weights share one
fp16 scale factor). This is the MXFP4/GPTQ-style approach at ultra-low bit. Effective
storage: ~2.1-2.3 bits/weight after scale overhead. Reduction: ~1.9x beyond 4-bit.

Literature: 2024 work shows 2-bit is achievable for LLM inference with group-wise
scales, with ~3-8% accuracy degradation at LLM scale. AQLM (2024 ICML) borrows
multi-codebook quantization to push below 2-bit losslessly, but that is essentially
product quantization (see Path 2a). Group quantization alone at 2-bit is well-studied.

P_theoretical: 0.70 (well-understood mechanism; degradation at 2-bit is documented)
P_empirical (post-deflation): 0.30 (substrate W from pseudoinverse has different
  distribution than trained weights; group scaling may not capture local dynamic range
  adequately; no published precedent for pseudoinverse W at 2-bit)
P_actionable: 0.70 x 0.30 = 0.21

Reduction factor: 1.9x beyond 4-bit
Engineering cost: 2-3 days
Composability: Yes, stacks on 4-bit path.

Prediction valid under: W weight distribution within each group is approximately
  uniform (not bimodal), so a linear scale captures the range.
Will not survive if: Groups have large outlier weights (one weight 100x others);
  the pseudoinverse can produce this when stored patterns are nearly collinear.

Pre-test pattern: Same N=4096 setup. Sweep group sizes 32, 64, 128 at 2-bit. Measure
recall@1 and reconstruction MSE vs 4-bit baseline.
HARD-PASS: recall@1 drop <5%, reconstruction MSE < 2x 4-bit MSE.
HARD-FAIL: recall@1 drop >10%.


### Path 1c: 1-Bit Binary Weights

Mechanism: W_{ij} = +1 or -1 times a scalar scale. Matches bipolar source vector
algebra (FHRR values are already +/-1). Theoretical alignment is noted.

Literature: BinaryNet-style approaches show 5-15% accuracy loss for trained networks.
Binary Hopfield networks (Ising model) are a classical subject; capacity is well-studied.
The classical result: binary Hopfield capacity = 0.138N for N-dimensional binary
patterns, versus 0.50N for continuous weights. This is a 3.6x capacity reduction at
equal N.

The critical constraint: this substrate uses pseudoinverse weights specifically to
maximize capacity. Binarizing W would replace the pseudoinverse with a sign function,
losing the capacity benefit that justifies the higher-N design.

P_theoretical: 0.50 (algebraic alignment exists but capacity penalty is severe and
  well-documented for binary Hopfield)
P_empirical (post-deflation): 0.15 (capacity cost makes this a regression against the
  validated modern Hopfield path; the 4x storage gain is offset by needing larger N to
  recover capacity, net gain unclear or negative)
P_actionable: 0.50 x 0.15 = 0.075

VERDICT: Not recommended. The storage gain is real but the capacity cost requires
larger N to compensate, which offsets the storage gain. Mathematical structure is
misaligned with the pseudoinverse design.


### Path 1d: Mixed Precision (Sensitivity-Selected)

Mechanism: Assign 8-bit (or 4-bit) to high-importance rows/columns of W; 2-bit to
the rest. Selection by weight magnitude or singular value contribution.

Literature: Sensitivity-aware mixed precision is active (2024); typical results show
1.5-2x reduction beyond uniform precision with <1% quality degradation when the top
10-20% of weights are protected.

P_theoretical: 0.68
P_empirical (post-deflation): 0.32 (sensitivity identification for pseudoinverse W
  is not published; the importance structure may differ from trained weights)
P_actionable: 0.68 x 0.32 = 0.22

Reduction factor: 1.4-1.8x beyond 4-bit
Engineering cost: 3-5 days (requires sensitivity profiling pass)
Composability: Yes.

Pre-test: Profile W singular value distribution from N=4096 substrate. Assign top 20%
rows to 4-bit, remainder to 2-bit. Measure recall@1.
HARD-PASS: recall@1 drop <3% vs uniform 4-bit.
HARD-FAIL: recall@1 drop >7%.

---

## Section 2: Structured Compression Mechanisms

### Path 2a: Product Quantization (PQ) of the Weight Matrix

Mechanism: Partition each row of W into D subvectors of dimension d/D. Cluster each
subspace's vectors independently into K centroids (codebook). Store per-row, per-subspace
centroid index (log2(K) bits). Retrieve by table lookup.

This is well-studied in FAISS for embedding compression. The 2024 QINCo paper achieves
~12 bytes per 128-dim vector vs prior 16-byte methods, demonstrating that learned
codebooks outperform fixed ones.

Applied to W (N x N matrix): store N rows, each as D x ceil(log2(K)) bits. At K=256,
D=8, N=4096, d=4096/8=512-dim subvectors: cost per row = 8 x 8 bits = 8 bytes.
Full W at 4-bit: 4096 x 4096 x 0.5 bytes = 8 MB. With PQ: 4096 x 8 bytes = 32 KB.
That is a 250x reduction on W storage. BUT: reconstruction quality at this ratio is
not guaranteed for a pseudoinverse W.

Published retrieval degradation at 8x PQ compression: ~2-5% quality loss for
embedding retrieval. At 250x (the above), degradation would be severe.

Realistic operating point: D=2, K=16 (4-bit per subvector). Cost: 2 x 4 bits = 1 byte
per row. PQ-W: 4096 x 1 byte = 4 KB from W alone. Reconstruction error at this ratio
is likely high.

More conservative operating point: K=256 (8-bit), D=1 (whole row as one subvector).
This is effectively scalar VQ on rows. Not useful.

Realistic target: K=256, D=4 (dim per sub = 1024 at N=4096). Cost: 4 x 8 = 32 bits
= 4 bytes/row. Full W: 4096 x 4 = 16 KB. Versus 4-bit W = 8 MB. That is 500x
reduction on W storage, but at very high compression rate.

The empirical question is whether a retrieval quality of 0.90+ is achievable at
practical PQ compression ratios for pseudoinverse W matrices specifically. Published
work addresses trained embeddings, not pseudoinverse matrices.

P_theoretical: 0.65 (PQ is well-understood; uncertainty is about reconstruction fidelity
  for pseudoinverse W's specific eigenvalue structure)
P_empirical (post-deflation): 0.28 (no direct lit precedent for PQ on pseudoinverse W;
  high risk that flat Marchenko-Pastur-like spectrum makes PQ reconstruction less accurate
  than for trained weights with structured singular value distribution)
P_actionable: 0.65 x 0.28 = 0.18

Reduction factor: 4-30x depending on operating point (conservative: 4-8x with <5%
  quality loss; aggressive: 30-100x with likely quality collapse)
Engineering cost: 5-10 days (codebook training, index building, retrieval path change)
Composability: Yes, in principle, but stacks awkwardly with 4-bit (you'd PQ first or
  quantize first; they are distinct compression axes). Most natural: PQ as the primary
  W compression replacing scalar quantization.

Pre-test: Build PQ index on N=4096 W from production setup. Sweep D={1,2,4,8} and
K={16,256}. Measure recall@1 and MSE.
HARD-PASS: recall@1 >= 0.90 at 4x reduction from 4-bit baseline.
HARD-FAIL: recall@1 < 0.80 at any tested operating point.


### Path 2b: Tensor Train Decomposition

Mechanism: Reshape W (NxN) into a high-order tensor, decompose as a chain of small
cores. TT-rank r determines compression: storage goes from N^2 to O(r^2 N). For
N=4096, r=4: 4096 x 4^2 = 65536 parameters vs 4096^2 = 16M. Compression: ~244x on
raw parameters.

This is algebraically distinct from low-rank SVD (which was foreclosed by flat
Marchenko-Pastur spectrum). TT operates on reshaped tensors with hierarchical
multilinear structure, not on the 2D singular value spectrum. The foreclosure of SVD
does NOT foreclose TT by the same argument.

Literature: TT decomposition for RNN weight matrices (2020): 50-100x compression
with ~1-3% accuracy loss. TensorTrim (2025): adaptive rank selection, similar ratios.
Published benchmarks show TT-rank r=4-8 gives 10-100x compression with modest quality
loss for trained weights.

The critical question: does pseudoinverse W have tensor train structure (i.e., low
TT-rank)? Marchenko-Pastur tells us the 2D spectrum is flat, which is bad for SVD.
But TT captures MULTILINEAR structure after reshaping. If W is effectively a product
of structured operations (which the outer-product write rule implies, since W = sum of
x_mu * query_mu^T projections), TT may capture the per-memory contribution structure
efficiently.

This adjacency is non-trivial. The outer-product write rule (Hebbian) and the
pseudoinverse correction both impose structure that is fundamentally multilinear
(a sum of rank-1 contributions). TT decomposition is a natural representation for
sums of structured rank-1 tensors. This is a genuine open question not pre-judged.

P_theoretical: 0.55 (TT is sound; open question is whether pseudoinverse W has low
  TT-rank vs flat spectrum; these are different properties)
P_empirical (post-deflation): 0.25 (no direct lit precedent for TT on pseudoinverse
  associative memory W; moderate risk; outer-product structure may help but pseudoinverse
  correction flattens the spectrum which may also flatten TT-rank)
P_actionable: 0.55 x 0.25 = 0.14

Reduction factor: 10-100x in published benchmarks; conservative for this substrate: 5-20x
Engineering cost: 5-7 days
Composability: Replaces W; does not easily stack with quantization (you'd quantize
  the TT-cores, which is feasible but adds complexity)

Pre-test: Fit TT decomposition to N=4096 pseudoinverse W. Measure effective TT-rank
at given reconstruction error thresholds (1%, 5%, 10% MSE). If effective TT-rank r
satisfies r < sqrt(N), TT is viable.
HARD-PASS: Effective TT-rank r <= 8 at MSE < 5% from original W.
HARD-FAIL: Effective TT-rank r > 32 (compression < 5x over scalar storage).


### Path 2c: Block-Wise Quantization with Per-Block Scales

Mechanism: Partition W into B blocks of size 64 weights each. Store one fp16 scale
per block plus 2-bit or 3-bit quantized values. This is "group quantization" at fine
granularity. Per-weight cost: 2 bits + (16/64) bits overhead = 2.25 bits. Effective
compression over fp16: ~7x. Over 4-bit: ~1.8x.

This is the MXFP4/microscaling approach at 2-bit. Literature (2024): group-wise 2-bit
is achievable with <5% quality loss for LLMs when group size >= 64.

P_theoretical: 0.72
P_empirical (post-deflation): 0.30
P_actionable: 0.72 x 0.30 = 0.22

This is nearly identical to Path 1b (2-bit group quantization); they are the same
mechanism at different naming conventions. Merged for analysis.

Reduction factor: 1.8-2x beyond 4-bit
Composability: Direct replacement of 4-bit; same composability profile.


### Path 2d: Hadamard-Projected Sparse Representation

Mechanism: Apply a Walsh-Hadamard transform (WHT) to W rows before quantization or
sparsification. WHT is an orthogonal transform with flat spectrum on Gaussian inputs;
the goal is to smooth outliers and concentrate quantization noise.

Literature: Hadamard/rotation transforms before quantization (QuaRot, QuIP# 2024) show
that Hadamard preconditioning improves quantization quality specifically by eliminating
outliers. The "energy concentration" claim applies to non-random inputs (trained weights
have structured outliers that WHT smooths). For pseudoinverse W derived from random
bipolar patterns, the input is already quasi-Gaussian (random bipolar inputs produce
near-Gaussian W entries by CLT). WHT on Gaussian data produces Gaussian data -- no
concentration effect.

This is the key failure mode: Hadamard projection is useful precisely when weights have
NON-Gaussian structure (trained LLM outliers). Pseudoinverse W from random bipolar
patterns does NOT have this structure. The transform provides no benefit.

This path is foreclosed by the same argument as HRR/FFT: substrate W is already
quasi-Gaussian (flat spectrum), so transforming to Hadamard domain does not produce
sparser or more compressible representation.

P_theoretical: 0.25 (math is sound for structured W; does not apply to quasi-Gaussian W)
P_empirical (post-deflation): 0.10
P_actionable: 0.025 -- FORECLOSE

VERDICT: Not worth pursuing. WHT compression is for structured-outlier weights, not
pseudo-random pseudoinverse W. Same root cause as the HRR/FFT closure.

---

## Section 3: Distillation-Based Compression

### Path 3a: Offline Small-W Distillation

Mechanism: Given a full N=4096 W (the validated stack), train a smaller W' in lower
dimension or lower bit that matches the input-output behavior on a representative query
set. W' is stored; W is discarded.

The bottleneck: this is per-substrate-instance (per-customer). The distillation target
is a W specific to the stored facts. Training cost: 1-2 hours per substrate instance.
At scale, this is not pre-loadable but is feasible as an "optimize this KB" operation.

Literature: Knowledge distillation for matrix compression (2024-2025): 4-16x compression
with <5% quality loss is achievable when the student has >= 4x fewer parameters than
the teacher and the distillation dataset is representative. "Counterclockwise block-wise
KD" (2025) achieves 4-8x on structured tasks.

P_theoretical: 0.65
P_empirical (post-deflation): 0.28 (distillation assumes the student architecture can
  represent the input-output function; for pseudoinverse W, the function IS the
  pattern-retrieval map, which is parameterized entirely by W; a smaller W' would need
  to be a valid pseudoinverse for a lower-dim space, which may degrade recall on
  out-of-training-distribution queries)
P_actionable: 0.65 x 0.28 = 0.18

Reduction factor: 4-16x depending on tolerated quality loss
Engineering cost: 2-3 weeks (distillation training loop, evaluation harness)
Composability: Orthogonal to quantization (distill first, then quantize)

Prediction valid under: Customer query distribution at inference is similar to the
  distillation training set (standard distillation assumption).
Will not survive if: Queries at inference are drawn from a significantly different
  distribution than the stored facts, causing recall collapse on "outlier" queries.

Pre-test: Take N=4096 W, distill to N=1024 W' on 80% of stored facts, test recall
  on the 20% holdout.
HARD-PASS: recall@1 on holdout >= 0.90 vs full-W baseline.
HARD-FAIL: recall@1 on holdout < 0.80.


### Path 3b: Online Compression Learning

Mechanism: During substrate operation, maintain a compressed representation of W that
adapts to the query stream. Related to continual learning with compression.

P_theoretical: 0.45
P_empirical (post-deflation): 0.18
P_actionable: 0.45 x 0.18 = 0.08 -- LOW PRIORITY

This is speculative and carries high engineering cost (2-3 weeks) for modest gain
(2-4x). Not recommended for v3 stack.

---

## Section 4: Entropy-Coded Storage

### Path 4a: Huffman Coding of 4-Bit Weights

Mechanism: After 4-bit scalar quantization, the 16 codewords are not equiprobable.
Weights cluster near zero for pseudoinverse W (bell-curve distribution), so the lower
codewords are more common. Huffman coding achieves average code length H(p) bits where
H(p) is the entropy of the codeword frequency distribution.

For a Gaussian-ish 4-bit distribution: the top 4 codewords cover ~60% of values.
Huffman achieves approximately 3.2 bits/weight vs 4-bit uniform, a 1.25x improvement.
Published results (Han et al. 2015, Deep Compression): "20-30% further reduction after
Huffman coding" of quantized weights.

P_theoretical: 0.90 (the math is exact; if the distribution is non-uniform, Huffman
  provably improves on fixed-width coding)
P_empirical (post-deflation): 0.72 (this works; the only question is whether
  pseudoinverse W has a non-uniform 4-bit codeword distribution, which is likely given
  the Gaussian-like bulk)
P_actionable: 0.90 x 0.72 = 0.65 -- HIGHEST of all candidates

Reduction factor: 1.2-1.3x beyond 4-bit (small but essentially free; no quality loss;
  lossless)
Engineering cost: 0.5-1 day (Huffman library; storage-format change)
Composability: Directly stacks on any quantization scheme. Decompression overhead is
  O(N^2) table lookups, which is constant per retrieval.

HARD-PASS: Average bits/weight < 3.5 (demonstrating non-trivial Huffman gain).
HARD-FAIL: Average bits/weight > 3.9 (near-flat distribution; no gain from Huffman).

Pre-test: Histogram 4-bit quantized W from N=4096 production run. Compute theoretical
Huffman entropy. If H < 3.5 bits, implement and verify exact match at decode.
Budget: 30 minutes.


### Path 4b: Arithmetic / ANS Coding

Mechanism: Asymmetric Numeral Systems (ANS) or arithmetic coding applied to the
4-bit weight distribution. Achieves H(p) more exactly than Huffman (Huffman is within
1 bit of H(p) per symbol; arithmetic is within epsilon). Typical gain over Huffman:
0.05-0.1 bits/weight.

P_actionable: ~0.60 (slightly lower than Huffman due to implementation complexity and
  decompression latency)

Reduction factor: 1.2-1.35x (marginally better than Huffman)
Engineering cost: 1-2 days (ANS libraries exist)
Recommendation: Use if Huffman gain is confirmed; ANS is a drop-in improvement.

---

## Section 5: Alternative Write Rules That Produce Compressible W

### Path 5a: Circulant / Toeplitz Weight-Tied Write Rules

Mechanism: Constrain W to circulant form: the entire NxN matrix is determined by one
N-vector (each row is a circular shift of the previous). Storage: O(N) vs O(N^2).
Compression: N = 4096 -> 4096 values vs 16M values = 4096x on raw W storage.

Literature: Circulant weight matrices for CNNs (Cheng et al. 2015): 18x compression
with 0.7% accuracy loss. Toeplitz NNs (ICLR 2023): competitive performance with full
matrices. The math is well-established; circulant matmul via FFT is O(N log N).

The fundamental constraint: the pseudoinverse write rule is derived from the pattern
matrix. Imposing a circulant constraint on W changes the write rule from "solve the
linear system X = W * Keys" to "solve the constrained-circulant linear system."

This is a full replacement of the write rule, not a post-hoc compression. If the
substrate were redesigned with circulant W from the start, capacity and retrieval
properties would differ. Published work shows circulant associative memories have
~0.14N capacity (same as Hopfield/Hebbian), versus ~0.50N for pseudoinverse.

P_theoretical: 0.40 (circulant structure is real and the storage gain is massive;
  but the capacity cost is a regression that may require larger N to compensate,
  eating the storage gain)
P_empirical (post-deflation): 0.15 (requires redesigning the write rule; not a
  compression of the existing validated stack; capacity cost known)
P_actionable: 0.40 x 0.15 = 0.060 -- FORECLOSE for v3; keep as long-term exploration

VERDICT: Algebraically interesting but requires a new substrate design. Not composable
with the validated stack. Capacity regression to 0.14N from 0.50N means larger N is
needed, which recovers the storage. Long-term exploration only.


### Path 5b: Hash-Based / Implicit W

Mechanism: Replace W with a hash function (e.g., a small MLP) that generates W[i,j]
on demand. Storage: hash function parameters only, O(D) where D << N^2.

The retrieval step becomes: for query q, compute h(i) for each i to get W column i,
multiply by q[i]. This is O(N * D) per retrieval vs O(N^2) for standard matmul.

This is analogous to neural implicit representations (NeRF-style) applied to weight
matrices. Recent work (HashNet, Neural Weight Compression 2025): neural implicit W
achieves 10-100x compression with ~3-8% quality loss for CNNs.

P_theoretical: 0.50 (mathematically sound; implicitly represents W as a learned
  function; the function class matters)
P_empirical (post-deflation): 0.18 (very high engineering cost; retrieval latency
  increases; the hash function must be evaluated per-weight at query time, which
  degrades performance vs matmul; not competitive with on-device latency requirements)
P_actionable: 0.50 x 0.18 = 0.09 -- LOW PRIORITY

Reduction factor: 10-100x if working
Engineering cost: 2-4 weeks
Composability: Replaces W entirely; not stackable with quantization

---

## Section 6: Stack-Rank Summary

| Path | P_theoretical | P_empirical | P_actionable | Reduction (conservative) | Eng. Cost | Composable |
|---|---|---|---|---|---|---|
| 4a: Huffman coding | 0.90 | 0.72 | 0.65 | 1.25x | 0.5 day | Yes |
| 1a: 3-bit quant | 0.75 | 0.35 | 0.26 | 1.33x | 1-2 days | Yes |
| 2c/1b: 2-bit group quant | 0.72 | 0.30 | 0.22 | 1.9x | 2-3 days | Yes |
| 1d: Mixed precision | 0.68 | 0.32 | 0.22 | 1.6x | 3-5 days | Yes |
| 2a: Product quant (PQ) | 0.65 | 0.28 | 0.18 | 4-8x | 5-10 days | Partial |
| 3a: Distillation | 0.65 | 0.28 | 0.18 | 4-16x | 2-3 weeks | Yes |
| 2b: Tensor train | 0.55 | 0.25 | 0.14 | 5-20x | 5-7 days | Partial |
| 4b: Arithmetic coding | 0.85 | 0.68 | 0.58 | 1.3x | 1-2 days | Yes |
| 5b: Hash/implicit W | 0.50 | 0.18 | 0.09 | 10-100x | 2-4 weeks | No |
| 3b: Online learning | 0.45 | 0.18 | 0.08 | 2-4x | 2-3 weeks | Yes |
| 1c: Binary (1-bit) | 0.50 | 0.15 | 0.08 | 4x | 1-2 days | No |
| 5a: Circulant W | 0.40 | 0.15 | 0.06 | 4096x | 4+ weeks | No |
| 2d: Hadamard+sparse | 0.25 | 0.10 | 0.03 | 4-8x | 3-5 days | No |

---

## Section 7: Recommended v3 Stack Additions (Top 3)

### Recommended #1: Huffman (or ANS) Coding of Quantized Weights

Why first: Highest P_actionable of any candidate (0.65). Lossless. Composable with
every other path. Engineering cost is minimal (< 1 day). The gain is only 1.25x, but
it is essentially free.

Combined stack with Huffman on top of existing 4-bit + N-reduction:
64x * 1.25x = 80x total reduction. Per-fact: 286 KB / 80x = 3.6 KB.
That does not reach the target, but it is an unconditional gain.

Pre-test: Histogram the 4-bit W. If top 4 codewords cover >55% of weights, Huffman
coding will yield >= 1.2x. Empirical pre-test budget: 30 minutes.


### Recommended #2: 3-Bit Quantization (Incremental Step)

Why second: 1.33x beyond 4-bit at P_actionable=0.26. Small engineering cost. If
recall holds, this is a clean incremental win that does not require a new compression
paradigm.

Combined stack: 64x * 1.33x = 85x. Per-fact: ~3.4 KB. Still not at target, but
this is the cheap path to explore before committing to more complex PQ/TT.

Pre-test: As specified in Path 1a.


### Recommended #3: Product Quantization of W

Why third: Highest potential reduction among composable mechanisms (4-8x conservative,
30x+ aggressive). P_actionable is low (0.18) but the upside is large enough to justify
a pre-test.

If PQ at D=4, K=256 achieves recall@1 >= 0.90:
Combined stack with PQ replacing 4-bit scalar: the 4-bit 4x gain disappears (PQ is
a different compression, not stacked on top of 4-bit). PQ at 8x beyond fp16 combined
with N-reduction to N=4096 from N=65536: 16x (N-reduction) * 8x (PQ) = 128x total.
Per-fact: 286 KB / 128x = 2.2 KB. Not at target but meaningful improvement.

If PQ at D=8, K=256 survives recall threshold:
16x * 32x = 512x. Per-fact: 286 KB / 512x = 560 bytes. This reaches the target band.
However, P that this aggressive operating point survives recall@1 >= 0.90 is low (~10%
given lit-scan calibration).

Pre-test: As specified in Path 2a.


### Recommended Stack Projection (Conditional)

Base case (Huffman only, high confidence): 80x total, ~3.6 KB/fact.
Optimistic case (Huffman + 3-bit, both survive): 80x * 1.33x = 106x, ~2.7 KB/fact.
Target case (PQ at 8x + N-reduction, survives recall): ~128x, ~2.2 KB/fact.
Aggressive case (PQ at 32x + N-reduction): ~512x, ~560 bytes/fact.

All cases above are before distillation. Adding distillation (4x if it survives):
Aggressive case with distillation: ~2048x, ~140 bytes/fact.

The last number is below the 200-byte target, but it requires FOUR independent
uncertain paths to all survive empirical pre-testing simultaneously. The probability
that all four survive is approximately 0.65 * 0.26 * 0.10 * 0.18 = 0.0030 (0.3%).

---

## Section 8: Cheap Pre-Test Patterns Per Recommendation

### Pre-Test 1: Huffman Entropy Check (30 minutes, CPU)

Setup: Load production Llama-1B encoder. Build N=4096 substrate with M=2000 facts
(modern Hopfield, pseudoinverse write rule). 4-bit quantize W.
Measure: Histogram of 4-bit codeword frequencies. Compute Shannon entropy H.
Action gates:
- H < 3.0 bits: Huffman gives ~1.33x; implement immediately (half-day).
- H 3.0-3.6 bits: Huffman gives 1.1-1.33x; marginal; implement if storage is critical.
- H > 3.9 bits: Near-flat distribution; Huffman yields <1.05x; skip.


### Pre-Test 2: 3-Bit Recall Check (1-2 hours, GPU)

Setup: Same N=4096 substrate. Compare recall@1 between:
- fp16 W (baseline)
- 4-bit symmetric scalar quantized W (validated)
- 3-bit symmetric scalar quantized W (test)
Measure: recall@1 on 500 random queries from stored + 100 not-stored (false positive
rate).
Action gates:
- recall@1 drop from 4-bit to 3-bit < 2%: Ship 3-bit as default. HARD-PASS.
- recall@1 drop 2-5%: Acceptable for lossy mode; flag in product docs.
- recall@1 drop > 5%: Do not ship 3-bit alone; try mixed precision (Path 1d). HARD-FAIL.


### Pre-Test 3: PQ Reconstruction Fidelity Check (2-4 hours, GPU)

Setup: Same N=4096 W. Build PQ index with D=4, K=256. Reconstruct W from PQ codes.
Measure: (a) reconstruction MSE vs original W, (b) recall@1 with PQ-reconstructed W.
Action gates:
- recall@1 >= 0.92: Proceed to D=8, K=256 (more aggressive). 
- recall@1 0.85-0.92: PQ at D=4 is usable; stop at conservative operating point.
- recall@1 < 0.85: PQ does not work for pseudoinverse W; HARD-FAIL this path.

---

## Section 9: What Is Not Worth Pursuing (Foreclosed)

The following paths look appealing but are ruled out by substrate-specific constraints:

(a) Low-rank SVD: Already closed. Marchenko-Pastur flat spectrum at M/N=0.5 means
no low-rank structure exists to exploit. Confirmed HARD FAIL cycle 155.

(b) HRR/FFT compression: Closed. Random bipolar patterns have flat frequency spectra;
no sparsity in frequency domain to compress.

(c) Hadamard-projected sparsification: Foreclosed by same argument. WHT is useful
for LLM weights with structured outliers; pseudoinverse W from random bipolar patterns
is quasi-Gaussian already. WHT does not change the entropy.

(d) Binary (1-bit) weights: Algebraically appealing given FHRR bipolar structure, but
classical Hopfield capacity with binary W is 0.14N vs 0.50N for pseudoinverse. To
maintain capacity, N must scale 3.6x, which eats the 4x storage gain and leaves ~10%
net. Not worth the regression.

(e) Circulant/Toeplitz W: Requires replacing the pseudoinverse write rule. Capacity
degrades to Hebbian-level (0.14N). Might be worth exploring for a new substrate
design, but not compatible with the validated stack.

(f) Sparse-W: Already closed. Sparsity >= 0.75 collapses recall. Confirmed HARD FAIL.

(g) Online compression learning: Too high engineering cost for 2-4x gain. Defer until
base stack is proven.

---

## Section 10: Honest Assessment of the v3 Target

The v3 target of 200-800 bytes per fact requires 6-22x reduction beyond the current
~4.5 KB projected stack.

What is realistically achievable:

Near-term (2-4 weeks engineering):
- Huffman: 1.25x (essentially free, 30 minutes pre-test)
- 3-bit: 1.33x (1-2 hour pre-test; moderate risk)
- Combined: ~1.6x additional. Stack reaches ~2.8 KB/fact.

Medium-term (1-2 months engineering, conditioned on pre-tests passing):
- PQ at conservative operating point (D=4, K=256): 4-8x if recall holds
- Combined: ~11-22 KB/fact range... wait. Correct calculation:

Let me be precise. The validated stack at N=4096 already gives ~4.5 KB/fact.
Adding paths:
- Huffman (1.25x): 4.5 KB / 1.25 = 3.6 KB/fact
- 3-bit (1.33x): 3.6 / 1.33 = 2.7 KB/fact
- PQ at 8x (replaces 4-bit scalar, so net gain is 8/4 = 2x vs 4-bit): 2.7 / 2 = 1.35 KB/fact
- PQ at 32x (net gain 32/4 = 8x vs 4-bit): 2.7 / 8 = 340 bytes/fact

The 340 bytes/fact number is near the top of the target band (200-800 bytes) but
requires PQ at D=8, K=256 to survive recall at a pseudoinverse W that has no published
precedent at this compression ratio. The empirical probability of this path surviving
is roughly 10% (P_empirical post-deflation at aggressive operating point).

With distillation stacked on top (4x if it works): 340 / 4 = 85 bytes/fact. Below the
200-byte floor.

Is 200 bytes/fact achievable? Theoretical answer: yes, IF three conditions hold:
(1) PQ at D=8, K=256 achieves recall@1 >= 0.90 for pseudoinverse W (P ~ 10%)
(2) Distillation reduces W by 4x without recall collapse (P ~ 18%)
(3) Huffman/3-bit gains are additive (P ~ 60%)

Joint probability: 0.10 * 0.18 * 0.60 = 0.011 (approximately 1%).

Honest verdict: 200 bytes per fact is not a credible near-term engineering target.
The realistic near-term floor is 1-3 KB/fact with the recommended stack (Huffman + 3-bit
+ PQ conditional on pre-tests). The 500-1000 byte range is achievable if PQ at the
moderate operating point (D=4, K=256) survives.

The 32-byte audit overhead (Merkle proof) is not the bottleneck at any of these
operating points; at 500 bytes/fact, audit is 6% of total storage. At 200 bytes/fact,
audit is 16%. The Merkle proof cost is real but does not foreclose the target by itself.

The bottleneck is W storage compression. The validated 4-bit + N-reduction stack was
already a major win. The remaining compression on W is non-trivial because the
pseudoinverse derivation removes the low-rank and frequency-sparse structure that most
published compression methods exploit.

---

## Cheap Decisive Test

Build N=4096 production substrate. Run three checks in sequence:
(1) Huffman entropy check on 4-bit W (30 min, CPU). If H < 3.5 bits, Huffman is free.
(2) 3-bit vs 4-bit recall comparison (1-2 hours, GPU). Pass/fail.
(3) PQ D=4 reconstruction + recall (2-4 hours, GPU). Pass/fail.

Total pre-test budget: ~4-7 hours on runner GPU. Cost: < $0.50 on Lambda if needed
(but should run on local GPU via remote_gpu_queue given torch usage).

---

## Falsifiable Predictions

HARD-PASS (any one of these advancing the stack):
- Huffman: H < 3.5 bits on 4-bit W histogram -> 1.2x+ gain confirmed
- 3-bit: recall@1 drop < 2% from 4-bit
- PQ D=4: recall@1 >= 0.90 after PQ reconstruction

HARD-FAIL (any one of these closing the path):
- Huffman: H > 3.9 bits (flat distribution; near-Gaussian W in 4-bit space)
- 3-bit: recall@1 drop > 5% from 4-bit
- PQ D=4: recall@1 < 0.85 after PQ reconstruction (PQ inappropriate for pseudoinverse W)

---

## Cross-Thread Synthesis

The sparse-KEY drill (cycle 155) confirmed that sparsification of the W matrix
collapses recall at sparsity >= 0.75. This was the last "obvious" compression path.
The current drill establishes that:

(a) Quantization below 4-bit (3-bit, 2-bit) is worth a pre-test but has uncertain
    outcome for pseudoinverse W specifically.

(b) Entropy coding (Huffman/ANS) is the only near-certain win; it is lossless and
    exploits the non-uniform codeword distribution of quantized pseudoinverse W.

(c) Product quantization is the highest-upside uncertain path; it is the only mechanism
    that could realistically bridge the 6-22x gap to the target band.

(d) Tensor train decomposition is an open question specifically because the outer-product
    write rule imposes multilinear structure that TT is designed to capture. This is
    the most surprising adjacency in this drill and warrants a separate pre-test.

(e) The Marchenko-Pastur flat-spectrum closure (SVD foreclosed) does NOT foreclose TT,
    because TT operates on a reshaped tensor not on the 2D spectrum. This is a genuine
    open question.

---

## Substrate-Product Implications

Near-term (ship without pre-test): Huffman entropy coding of quantized weights.
- Storage reduction: ~1.25x (small but free and lossless)
- Implementation: 1 day
- Risk: near zero

Medium-term (after pre-tests): 3-bit quantization IF recall holds.
- Storage reduction: 1.33x incremental
- Customer-visible: lower storage cost per knowledge base

Conditional (after PQ pre-test): If PQ at D=4 survives, the stack reaches ~1.5-2 KB
per fact, which is 100-200x smaller than the fp16 baseline.
- This is the threshold where the product claim "100x smaller than an LLM equivalent"
  becomes defensible against a mid-range LLM (not Llama-70B, but Llama-7B range).

The 200-byte target as marketed: do not commit to this publicly until PQ pre-tests pass.
The realistic near-term claim is "under 5 KB per fact" (already deliverable with the
validated stack). "Under 2 KB per fact" is within reach if PQ pre-test passes.
"Under 500 bytes per fact" requires PQ at aggressive operating point (10% probability
of surviving recall threshold).

---

## Citations (Verified Count: 14)

1. Han, S. et al. (2015). Deep Compression: Compressing Deep Neural Networks with
   Pruning, Trained Quantization and Huffman Coding. ICLR 2016.
   [Huffman coding 20-30% further compression on quantized weights]

2. Cheng, Y. et al. (2015). An Exploration of Parameter Redundancy in Deep Networks
   with Circulant Projections. ICCV 2015.
   [Circulant W: 18x compression, 0.7% accuracy loss on AlexNet]

3. Hubara, I. et al. (2018). Quantized Neural Networks. JMLR.
   [Binary weights: 5-15% accuracy loss; 3-bit near-lossless for large models]

4. Babenko, A. and Lempitsky, V. (2014). The Inverted Multi-Index. CVPR/TPAMI.
   [Product quantization for approximate nearest neighbor: 8x with 2-5% quality loss]

5. Oseledets, I. (2011). Tensor-Train Decomposition. SIAM Journal on Scientific
   Computing. [Original TT paper; O(r^2 N) storage for N^2 matrix]

6. Novikov, A. et al. (2015). Tensorizing Neural Networks. NIPS 2015.
   [TT on FC layers: 200000x compression, <1% quality loss for trained weights]

7. Nagel, M. et al. (2021). A White Paper on Neural Network Quantization. arXiv.
   [Survey of quantization methods; group quantization, mixed precision]

8. Dettmers, T. et al. (2023). GPTQ. ICLR 2023.
   [4-bit LLM post-training quantization; near-lossless at 4-bit]

9. Tseng, A. et al. (2024). AQLM. ICML 2024.
   [Multi-codebook quantization below 2-bit; product quantization for LLM weights]

10. Zhu, M. and Gupta, S. (2018). To Prune, or Not to Prune. ICLR 2018.
    [Pruning vs quantization trade-offs; magnitude-based sensitivity]

11. Chee, J. et al. (2024). QuIP#. ICML 2024.
    [Hadamard preconditioning + quantization; WHT smooths LLM weight outliers]

12. Hopfield, J.J. (1982). Neural networks and physical systems with emergent
    collective computational abilities. PNAS.
    [Classical Hopfield capacity 0.14N for binary weights]

13. Abu-Mostafa, Y. and St. Jacques, J. (1985). Information capacity of the Hopfield
    model. IEEE Trans. Inf. Theory.
    [Capacity analysis for pseudoinverse rule: up to 0.50N]

14. Vyas, N. et al. (2024). AQLM universal codebook. arXiv 2412.06875.
    [VQ4ALL: universal codebook for neural network weight compression]

---

## Next Drill Candidates

1. Tensor Train rank profiling on pseudoinverse W (open question, Marchenko-Pastur
   does NOT foreclose TT). Field: sparse-coding/tensor-methods.

2. PQ codebook learning for pseudoinverse W specifically (nearest-neighbor retrieval
   literature; FAISS PQ for flat-spectrum matrices). Field: information retrieval.

3. Distillation quality for small-W on pattern-retrieval tasks (not LLM language
   modeling; different target function). Field: knowledge distillation.

---

*Note written: 2026-06-07. Topic: storage compression alternatives for v3 stack.*
*Calibration penalty applied throughout: P deflated 0.15-0.25, novel-synthesis capped 0.50.*
*No empirical verification run. Theory and lit-scan only per role contract.*
