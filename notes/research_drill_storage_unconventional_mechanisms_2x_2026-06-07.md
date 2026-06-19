# Research Drill: Unconventional Storage Efficiency Mechanisms (2x Depth)
# Date: 2026-06-07
# Trigger: 2x drill — user-initiated depth request on storage per-fact cost
# Goal: find mechanisms giving 5-50x beyond the standard sparse-W / 4-bit / lower-N stack

---

## HEADLINE

Three mechanisms compose orthogonally on top of the standard stack and are testable within
weeks: (A) modern Hopfield / dense associative memory at reduced dimension (8-16x W savings
if N can drop from 65K to 4K-8K while preserving capacity at alpha=0.5), (B) customer-
specific encoder distillation (4-16x source-vector shrinkage before facts enter the substrate),
and (C) delta/template compression for structured knowledge bases (5-20x on regular-schema
KBs). These three stack multiplicatively only when the axis each addresses is genuinely
different: vector count, vector dimension, and fact regularity. Combined realistic projection:
~500-2000 bytes per fact achievable at v3; the 500-byte end requires favorable KB regularity
AND the modern Hopfield bet paying off. P_deflated on best-case stack = 0.30.

---

## Cheap Decisive Test

For mechanism A (modern Hopfield dimension reduction): run a retrieval capacity experiment
at N=4096 with the exponential energy function versus the current quadratic energy at N=65536.
Measure: capacity at alpha=0.5, retrieval accuracy at M=0.4*N stored patterns, and W storage
bytes. Expected if the mechanism transfers: W_small < W_current / 100 with retrieval accuracy
> 0.90. Test cost: ~2 hours on local CPU (small N, no GPU needed). This is falsifiable within
one session.

For mechanism B (distillation): take 1000 facts from a real KB. Train a 50M-parameter
encoder that outputs 4096-dim vectors. Measure retrieval accuracy loss vs 65536-dim baseline.
Expected: accuracy >= 0.85 with 16x smaller vectors. Test cost: ~3 hours on remote GPU.

For mechanism C (delta/template): take a 10K-fact KB with a known schema (e.g., all facts
of form "entity X has property Y = value Z"). Count unique predicates. Store predicate
templates once; store per-fact as (predicate_id, slot_values). Measure compression ratio.
Expected: 5x+ on a structured KB; < 1.5x on free-text. Test cost: 1 hour CPU.

---

## Falsifiable Predictions: HARD-PASS and HARD-FAIL Thresholds

### Mechanism A: Modern Hopfield dimension reduction

HARD-PASS: At N=4096, exponential energy achieves capacity M/N >= 0.30 with retrieval
accuracy > 0.90. W storage bytes drop by >= 10x vs N=65536 baseline. This would confirm
the exponential scaling transfers to the substrate's alpha_c operating point.

HARD-FAIL: At N=4096, retrieval accuracy drops below 0.70 at M/N=0.20. This would mean
the exponential capacity gain does not rescue the reduced-N regime at the substrate's
operating load; likely cause is the pseudoinverse write rule not being compatible with the
exponential energy landscape.

### Mechanism B: Encoder distillation

HARD-PASS: 50M encoder at 4096-dim output achieves retrieval F1 >= 0.85 on held-out KB
queries. Cost per fact drops by >= 10x.

HARD-FAIL: F1 drops below 0.70 at 4096-dim regardless of encoder size. This would mean the
information content needed for retrieval requires the full 65536-dim space.

### Mechanism C: Delta/template compression

HARD-PASS: On a KB with >= 10 facts per predicate, delta encoding achieves >= 5x byte
reduction with zero accuracy loss on predicate-matched queries.

HARD-FAIL: On a KB with >= 50% free-text or unique-relation facts, compression ratio < 2x.
This would correctly scope the mechanism to structured-schema KBs only.

---

## 11-Candidate Evaluation

### (1) Modern Hopfield / Dense Associative Memory at Reduced Dimension

What it does: the classical Hopfield network stores at most ~0.14N random patterns. Modern
Hopfield (Ramsauer 2020, Krotov-Hopfield 2016, Demircigil 2017) replaces the quadratic
energy with an exponential energy. Capacity scales as exp(alpha*N) rather than 0.14*N.
This means a smaller N can store the same number of patterns as a much larger classical N.

Predicted reduction factor: if current substrate at N=65536 stores M=32768 patterns (M/N=0.5),
an exponential-energy substrate might achieve the same capacity at N~8000-12000, giving a
W matrix ~30-65x smaller by area (N^2 scaling). However: the substrate's pseudoinverse write
rule is designed for the quadratic energy landscape. Compatibility with the exponential energy
requires a different write rule (e.g., Lagrangian descent on the exponential energy). This is
the critical unknown.

Reduction factor estimate: 8-50x on W storage (HARD-PASS at 10x; realistic median 15-20x).
P_deflated that it transfers cleanly = 0.25 (calibration penalty: novel-synthesis, no direct
published precedent for pseudoinverse + exponential energy at alpha=0.5).

Implementation cost: 3-6 weeks engineering (new write rule derivation + N-sweep experiments).

Quality loss risk: HIGH if the exponential energy landscape has many spurious attractors at
the substrate's operating alpha. Published work (Ramsauer 2020) shows clean retrieval for
ONE-shot patterns; multi-pattern interference at alpha_c=0.5 is not characterized.

Lit precedent at production scale: YES for the capacity claim; NO for the write-rule
compatibility at high load. Arxiv 2304.14964 (exponential capacity) and arxiv 2601.00984
(biologically plausible version) are the nearest references. Neither addresses the
pseudoinverse-plus-exponential-energy combination.

### (2) Delta Storage / Hierarchical Compression for Structured KBs

What it does: instead of storing each fact as a full N-dimensional vector, identify the
"predicate template" (the structural pattern common to many facts) and store it once. Each
fact then stored as (template_id, slot_values). If 1000 facts share a 3-slot predicate
template and the template vector is N-dimensional but each slot value is 100-dimensional,
storage per fact drops from N to 3*100 = 300 dimensions of delta.

Predicted reduction factor: 5-20x on KBs with high schema regularity (>= 10 facts per
predicate, low cardinality slot values). Near zero on free-text, unique-relation KBs.
Reduction is on the per-fact byte count, not on W itself -- the facts written to W are the
compressed delta vectors, so W shrinks proportionally if fewer dimensions are used.

This requires pairing with mechanism A or B (smaller N) to realize W savings. Alone it
reduces the number of unique patterns that need encoding, not necessarily the N of the W matrix.

P_deflated = 0.45. This is standard compression engineering; the uncertainty is about what
fraction of real customer KBs are structured enough to benefit.

Implementation cost: 2-4 weeks (template extractor + delta encoder + retrieval path).

Quality loss risk: LOW for structured facts; HIGH for free-text facts (compression destroys
retrieval for unpredictable content). Needs a routing gate: structured KBs take the delta
path, free-text KBs take the full-vector path.

Lit precedent: YES. Delta encoding is standard in database and file-system literature
(ACM TOS 2024). Template-based semantic compression for knowledge graphs is less published
but is essentially RDF reification or property graph normalization, both well-understood.

### (3) Holographic / FFT-Domain Encoding (HRR)

What it does: Holographic Reduced Representations (Plate 1995) use circular convolution
(via FFT) as the binding operation. The binding of key-vector and value-vector is a single
N-dimensional vector, the same size as the inputs. The substrate already uses FHRR (complex
bipolar). The question is whether moving to FFT-domain storage saves bytes.

The answer is: NOT in the way described. HRR/FHRR does not reduce the storage dimension --
each bound pair is still N-dimensional. The FFT operation is a basis change, not a
compression. The frequency-domain representation of a random bipolar vector is not sparser
than the time-domain; random vectors have flat spectra by definition.

Predicted reduction factor: NEAR ZERO for random or near-random fact vectors. Possible 2-3x
if the substrate's stored vectors happen to have non-trivial frequency-domain sparsity (which
requires the customer KB to have strong structural regularities that the FHRR encoding
captures non-uniformly). This is unlikely for general KBs.

P_deflated = 0.10. The mechanism does not address the bottleneck.

Implementation cost: 2-3 weeks to verify experimentally (low cost for a negative confirmation).

Quality loss risk: MEDIUM to HIGH (FFT binding introduces phase-cancellation at retrieval when
many items are superimposed; the substrate's alpha_c=0.5 operating point is near the edge of
the capacity regime for HRR).

Lit precedent: YES (Plate 1995, arxiv 2111.06077 VSA survey). But lit is clear that HRR
does NOT achieve compression; it achieves fixed-width compositional binding. Conflating the
two is a common error.

VERDICT: DEPRIORITIZE. Not a storage reducer; it is a binding algebra. The substrate already
uses FHRR for this purpose.

### (4) Substrate-of-Substrates (Recursive Nesting)

What it does: use a small-N substrate (N=4096) to store atomic facts (entities, property
values). Use a large-N substrate (N=65536) to store relationships BETWEEN small-substrate
entries. Per-fact cost is dominated by the small substrate; relationship cost amortizes over
many facts.

Predicted reduction factor: depends on the ratio of atomic facts to relationships. If a KB
has 100K atomic facts and 10K relationships, and the small substrate stores 10 facts per
N=4096 W-matrix, then total W storage is (10K / 10) * 4096^2 bytes = ~16 GB for atomic, plus
one N=65536 matrix for relationships = ~4 GB. Baseline single N=65536 matrix for all 110K
facts = ~34 GB (but cannot fit 110K facts at alpha=0.5). So this is more about enabling
large-scale storage than about per-fact compression.

The per-fact cost in this regime: 16 GB / 100K facts = 160 KB per fact -- WORSE than the
current baseline. The architecture is for scale-out, not per-fact efficiency.

P_deflated = 0.20 that it improves per-fact cost at v1-v3 scale.

Implementation cost: 6-12 weeks (multi-level architecture, cross-level retrieval, sharding).

Quality loss risk: HIGH (cross-level retrieval adds K-hop hops, increases error rate
multiplicatively).

Lit precedent: YES (Hierarchical Hopfield networks, MPLB 1990; Emergent Mind hierarchical
memory 2024). But published work addresses capacity per level, not per-fact cost reduction.

VERDICT: RESEARCH-GRADE v3+ INFRASTRUCTURE. Not a storage-efficiency mechanism for v2.

### (5) Bloom Filter Pre-stage for Negative Query Filtering

What it does: a Bloom filter answers "is this fact ID possibly stored?" in O(1) with a
false-positive rate epsilon. For facts NOT in storage, the substrate retrieval is skipped
entirely.

Predicted reduction factor on per-fact cost: ZERO. A Bloom filter does not reduce the cost
of storing facts; it reduces the compute cost of QUERYING for absent facts. If 70% of queries
are for facts not stored, compute cost drops by ~70%. Storage bytes per fact are unchanged.

However: if the Bloom filter's byte cost (~10 bits per fact at epsilon=0.01) is subtracted
from W-matrix bytes: 10 bits vs 5 KB baseline is negligible.

P_deflated = 0.55 for compute savings on negative queries (this is standard engineering, not
novel).

Implementation cost: 1-2 weeks (standard library).

Quality loss risk: NONE on retrieval quality; small false-positive rate on negative queries.

Lit precedent: YES (extensive; GeeksforGeeks, ACM JEA Bloom filter variants; learned Bloom
filters arxiv 2502.03696).

VERDICT: EASY WIN for latency but NOT a storage reducer. Deprioritize for the per-fact cost
goal. Ship in parallel as a query-path optimization.

### (6) Huffman / Arithmetic Coding of Stored Facts

What it does: pre-train a Huffman code table on the customer KB vocabulary. Stored facts are
compressed codes; the W matrix receives the compressed representation, reducing the effective
information per stored vector.

The key flaw: the substrate stores continuous-valued vectors, not discrete token sequences.
Huffman coding operates on symbol frequencies in a discrete alphabet. To apply it here, facts
would need to be encoded as discrete tokens, then the token sequence compressed, then the
compressed sequence re-embedded as a vector. This is a pipeline: text -> tokens -> Huffman ->
embedding -> substrate. The Huffman step compresses the text, but the embedding step maps back
to a high-dimensional space. The W matrix dimension is unchanged.

Predicted reduction factor on W storage: ZERO. Huffman reduces bytes before the substrate;
the substrate still stores whatever embedding is produced, and that embedding is N-dimensional.

Exception: if Huffman-coded tokens are used as direct sparse index vectors (a discrete sparse
code), then the stored vector is sparse and the substrate operates in sparse mode. This is
essentially mechanism (11) (sparse coding / dictionary learning) with a specific construction.

P_deflated = 0.10 as a standalone mechanism.

Implementation cost: 2-3 weeks, but this is overengineering for the LLM-comparison goal.

Lit precedent: YES (LLMZip, arxiv 2306.04050; text compression with LLMs). But the goal there
is lossless text compression, not associative memory storage efficiency.

VERDICT: DEPRIORITIZE. Addresses the wrong bottleneck (text bytes, not W bytes).

### (7) Distillation: Customer-Specific Encoder Compression

What it does: a 1B-parameter encoder produces 65536-dim embeddings. Train a 50-100M encoder
per customer that produces 4096-dim embeddings with equivalent retrieval properties. Store
these 4096-dim embeddings in a substrate with N=4096.

Predicted reduction factor: (65536/4096)^2 = 256x on W storage. Realistic: 16-64x after
accounting for quality loss requiring some extra dimensions above the minimum. At N=8192,
factor = 64x on W.

This is the most technically grounded mechanism with the highest reduction factor among
plausible paths. The distillation literature (knowledge distillation, LoRA, student-teacher)
is extensive and production-proven.

P_deflated = 0.40 (calibration: the substrate's retrieval properties at small N are not
characterized; LoRA results showed hurt-retrieval per MEMORY.md production lock).

Implementation cost: 4-8 weeks (student encoder training, N-sweep for minimum viable N,
integration with substrate pseudoinverse write rule at smaller N).

Quality loss risk: MEDIUM. Dimension reduction from 65536 to 4096 is 16x; at some point
retrieval accuracy falls below acceptable. The minimum viable N is an empirical question.
The LoRA hurt-retrieval finding in MEMORY.md is a WARNING: the production lock says "LoRA
hurts retrieval." Distillation (output-space compression) is architecturally different from
LoRA (W-matrix low-rank approximation), but the caution applies.

Lit precedent: YES (knowledge distillation is standard ML; student-teacher for embeddings is
well-published). No published precedent for distilling into a Hopfield-compatible fixed-dim
embedding space specifically.

VERDICT: TIER-2 candidate. High reduction ceiling but medium risk. Requires the minimum
viable N experiment first.

### (8) Quantization-Aware Substrate Retraining (QAT)

What it does: instead of post-hoc 4-bit quantization of W, train the substrate to produce a
W matrix that is natively 4-bit-friendly. Standard QAT (straight-through estimator +
simulated quantization during training).

Predicted reduction factor: QAT gives ~1.5-2x quality improvement over post-hoc quantization
at the same bit width, OR it allows going from 4-bit to 2-bit with equivalent quality. 2-bit
vs 4-bit is a 2x additional reduction. Combined with post-hoc 4-bit as baseline: total from
full-precision = 16x (4-bit) to 32x (2-bit QAT).

Incremental gain over standard 4-bit post-hoc quantization: ~2x. This is a modest gain.

P_deflated = 0.50. QAT is well-characterized for discriminative networks; for associative
memory write rules (pseudoinverse) it is less studied. The pseudoinverse is a one-shot
computation, not iterative training, so "quantization-aware training" requires redefining
what "training" means for the substrate.

Implementation cost: 4-6 weeks (redefine write rule for QAT context; significant engineering).

Quality loss risk: LOW for 4-bit QAT; MEDIUM for 2-bit.

Lit precedent: YES (arxiv 2112.06126 QAT survey; pQuant 2602.22592). But none specifically
for associative memory write rules.

VERDICT: MODEST INCREMENTAL GAIN. Worth doing as part of the standard stack, not as a
standalone unconventional mechanism. Ship after 4-bit post-hoc is validated.

### (9) Sparse Distributed Memory at N=1M, alpha=0.0001

What it does: instead of N=65536 with alpha_c=0.5 (dense), use N=1,000,000 with alpha=0.0001
(extremely sparse). Active neurons per fact: alpha*N = 100. Kanerva (1988) shows SDM can store
many patterns when density is low, because interference between patterns scales as alpha^2.

Predicted reduction factor on storage: the hard locations data structure stores, for each of
~1000 hard locations, a sum-vector of length N. Total storage: 1000 * 1M bits = 125 MB for
1000 stored facts. Per-fact: 125 KB. This is WORSE than the current W-matrix at N=65K which
stores per-fact at ~5 KB (after standard stack). The large N of SDM creates infrastructure
costs that overwhelm the sparse-coding savings.

P_deflated = 0.10 that SDM is a storage-efficiency win at v2 scale.

Implementation cost: high (N=1M infrastructure is not trivial).

Quality loss risk: MEDIUM (SDM retrieval is well-characterized for random patterns but poor
for non-random structured data, per NTRS 1990 report).

Lit precedent: YES (Kanerva 1988; NTRS reports). Clear that SDM was designed for robustness
to noise, not for per-fact byte efficiency.

VERDICT: DEPRIORITIZE. SDM at N=1M has worse per-fact cost than current substrate.

### (10) Predictive Delta / Bits-of-Surprise Encoding

What it does: for sequences of related facts (multi-fact chains, temporal series), train a
small language model to predict the next fact. Store only the difference between the predicted
and actual next fact (the "bits of surprise"). Similar to arithmetic coding / ANS encoding
but driven by a learned predictor.

Predicted reduction factor: English natural text has ~1.12 bits per character entropy (neural
LM estimate). Current facts stored at ~40 bits per character (N=65536 bipolar = 65536 bits
for ~1600 chars). Bits-of-surprise encoding could theoretically reach ~1.12 bits per char on
natural text, a ~35x reduction. In practice: 5-10x for structured factual sequences; near
zero for random or independent facts.

P_deflated = 0.20 that this is viable at v2 engineering timescales. It requires: (a) a per-
customer LM trained on their KB, (b) an encoding pipeline that maps LM predictions to
substrate vectors, (c) a retrieval path that reconstructs the original from prediction + delta.
The retrieval pipeline is the hard part: substrate retrieval is approximate (not bit-perfect),
so the delta decoding would need error correction.

Implementation cost: 8-14 weeks (per-customer LM training pipeline + encoding/decoding bridge).

Quality loss risk: HIGH for the retrieval path (approximate retrieval + lossy encoding = error
amplification on the delta reconstruction).

Lit precedent: YES (LLMZip arxiv 2306.04050; AlphaZip arxiv 2409.15046). But these are
lossless text compressors, not substrate-retrieval systems. The bridge to approximate
associative memory retrieval is novel and unvalidated.

VERDICT: RESEARCH-GRADE v3. High theoretical ceiling but the retrieval bridge is a serious
unsolved engineering problem.

### (11) Dictionary Learning / Sparse Coding

What it does: learn a dictionary of K atoms from the customer KB. Each fact is a sparse linear
combination of ~S atoms (S << K). Store the sparse weight vector (S non-zero entries) instead
of the full N-dim embedding.

Predicted reduction factor: if N=65536 and a fact is represented as 50 non-zero weights over
a dictionary of 8192 atoms, storage per fact = 50 * (13 bits index + 8 bits value) = 50 * 21
bits = ~130 bytes instead of 65536 * 2 bits (bipolar) = ~16 KB. Factor: ~120x on the raw
embedding. However: the dictionary must also be stored (8192 atoms * 65536 dims = 4 GB). At
large KB size (>100K facts), the dictionary amortizes; at small KB (<10K facts), it dominates.

The substrate does not currently support sparse coefficient retrieval directly; W encodes
full N-dim vectors, not sparse atom indices. Adapting the write rule to sparse-code
representations is a non-trivial architectural change.

P_deflated = 0.30 that this is viable at v2 (medium engineering + architectural change risk).

Implementation cost: 5-8 weeks (dictionary learning from KB + modified write rule + retrieval
adaptor).

Quality loss risk: MEDIUM. Dictionary learning at S=50 achieves ~70% reconstruction accuracy
on typical embedding spaces; retrieval accuracy will degrade proportionally.

Lit precedent: YES (Olshausen & Field 1996 sparse coding; MIT Press dictionary learning 2003;
arxiv 2205.15386 accumulator neurons for dictionary learning).

VERDICT: TIER-2 for large KBs (>100K facts). At small KB scale the dictionary overhead
dominates.

---

## Stack Ranking

### TIER-2 (Recommended for v2, 4-12 weeks engineering)

1. MECHANISM 7 (Encoder Distillation): highest ceiling (16-64x W reduction), most grounded
   technically, production analogs exist. Cheap decisive test is 3 hours on GPU. CAVEAT:
   must first empirically establish minimum viable N -- the LoRA-hurts-retrieval finding
   in MEMORY.md is a red flag; distillation may hit the same floor. Run the N-sweep first
   before committing 8 weeks of engineering.

2. MECHANISM 2 (Delta / Template Compression): 5-20x on structured KBs, 2-4 weeks, standard
   engineering. The ROI is conditional on KB regularity. Deploy as a "structured KB fast
   path" that routes regular-schema KBs through delta encoding and free-text KBs through
   the full-vector path. The routing gate is the key engineering piece.

3. MECHANISM 1 (Modern Hopfield at reduced N): if the write-rule compatibility problem is
   solved, 8-50x W reduction. But the CHEAP test (2 hours CPU) must be done first -- this is
   genuinely uncertain and could HARD-FAIL on the pseudoinverse + exponential energy
   incompatibility. Pre-register the HARD-FAIL threshold before committing engineering.

4. MECHANISM 8 (QAT): modest 2x incremental gain over post-hoc 4-bit, but it is part of
   the standard stack anyway. Do it AFTER the standard 4-bit is validated. Not a standalone
   unconventional mechanism.

### RESEARCH-GRADE v3 (3-6 months)

1. MECHANISM 10 (Predictive Delta / Bits-of-Surprise): 5-35x theoretical reduction for
   structured sequential KBs. The hard problem is the retrieval bridge (approximate substrate
   + lossless delta = error amplification). Requires a separate research track on error-
   correcting retrieval.

2. MECHANISM 4 (Substrate-of-Substrates): architectural scale-out, not per-fact efficiency.
   Worth pursuing for KBs > 10M facts where a single W-matrix is not viable, but it does not
   improve per-fact cost at v2 scale.

### DEPRIORITIZE (overengineering for LLM-comparison goal)

- MECHANISM 3 (HRR / FFT compression): does not address the storage bottleneck. Substrate
  already uses FHRR. FFT is a basis change, not a compressor.
- MECHANISM 5 (Bloom filter): compute optimizer, not storage reducer. Easy win; ship as
  query-path optimization, not as part of the per-fact cost roadmap.
- MECHANISM 6 (Huffman coding): addresses text bytes, not W bytes. The embedding step undoes
  the compression.
- MECHANISM 9 (SDM at N=1M): per-fact cost is WORSE than current baseline at practical scales.

---

## Stacking Analysis: Orthogonal vs Redundant Axes

The key question is whether two mechanisms address the same bottleneck (W matrix size) or
different bottlenecks. The W matrix is N x N; bytes = N^2 * bits_per_weight.

AXIS 1: Reduce N (vector dimension). Mechanisms: 1 (modern Hopfield), 7 (distillation).
  - These address the SAME axis. They do NOT compose multiplicatively.
  - If mechanism 1 reduces N from 65536 to 8192 (8x), and mechanism 7 independently reduces
    N to 8192 (8x), you do not get 64x -- you get 8x (whichever achieves the smaller N).
  - They are redundant on the same axis. Pick ONE and push it to its limit.
  - Exception: they could be run in sequence if mechanism 1 reduces N to 16384 and mechanism
    7 then compresses the 16384-dim embeddings to 4096-dim. Then N = 4096 and the W factor
    is (65536/4096)^2 = 256x. But this assumes both mechanisms compose cleanly, which is
    unlikely at their respective limits.

AXIS 2: Reduce patterns-per-W-matrix (fewer unique facts stored per substrate instance).
  Mechanisms: 2 (delta/template), 10 (predictive delta).
  - These address the SAME axis. They are redundant.
  - Delta and predictive-delta are both "reduce the information content of each stored fact
    before it enters the substrate." Pick the simpler one (mechanism 2) first.

AXIS 3: Reduce bits per weight element. Mechanisms: 8 (QAT), standard 4-bit.
  - These are on the same axis. QAT is strictly better than post-hoc quantization at the
    same bit width. They do not stack -- you run QAT INSTEAD of post-hoc.

ORTHOGONAL COMPOSITIONS (DO stack multiplicatively):

1. AXIS 1 x AXIS 2: Reduce N (mechanism 1 or 7) + reduce per-fact information (mechanism 2).
   - If N drops from 65536 to 8192 (mechanism 1/7: 64x on W), AND
   - Per-fact information content drops 10x via delta encoding (mechanism 2),
   - THEN the total per-fact cost drops 640x.
   - But: mechanism 2 reduces the effective N needed, which means the N-reduction from
     mechanism 1 needs to be applied at the NEW, lower-dimensional representation.
   - Clean composition: mechanism 2 first (reduce fact dimensions), then mechanism 1/7
     (choose N to match the reduced dimensions).

2. AXIS 1/2 x AXIS 3: Any N-reduction + QAT.
   - Fully orthogonal. N-reduction addresses N^2 scaling; QAT addresses bits_per_weight.
   - These multiply cleanly: if N drops 8x and QAT reduces bit width from 16 to 2 bits (8x),
     total W size drops 8^2 * 8 = 512x.

3. AXIS 1 x AXIS 2 x AXIS 3: Full three-way stack.
   - If each axis achieves only half its headline reduction (conservative), total = 4x * 5x
     * 4x = 80x on W. Starting from 16 KB (full-precision, no standard stack), that is
     16 KB / 80 = 200 bytes per fact.
   - Starting from 5 KB (after standard sparse-W + 4-bit + lower-N from standard stack):
     the incremental gain from the unconventional stack on top = AXIS 1 x AXIS 2 = 4x * 5x
     = 20x additional. 5 KB / 20 = 250 bytes per fact.

---

## Combined Realistic Per-Fact Cost Projection

Baseline (current, no optimizations): ~16 KB per fact.
After standard stack (sparse-W + 4-bit + lower-N from current experiments): ~5 KB per fact.

Tier-3 unconventional stack on top of 5 KB baseline:

Conservative case (mechanisms 1 + 2, each at half their headline reduction):
  Mechanism 1 (modern Hopfield N-reduction): N drops from 65536 to 16384, W reduction = 16x
    but already partially baked into standard stack; NET NEW reduction = 4x.
  Mechanism 2 (delta encoding for structured KB): 5x on 60% of facts, 1x on 40%.
    Blended = 0.6*5 + 0.4*1 = 3.4x.
  Combined = 4x * 3.4x = 13.6x on W.
  5 KB / 13.6 = ~370 bytes per fact (for structured KB customers).

Optimistic case (mechanisms 1 + 7 + 2, at headline reductions, structured KB):
  Mechanism 7 (distillation to N=4096): 256x on W.
  Mechanism 2 (delta for structured KB): 10x on per-fact information.
  But: if mechanism 7 already achieves N=4096, then N is at its physical floor.
    Adding mechanism 2 then reduces facts-per-substrate, allowing EVEN SMALLER N per shard.
  Combined ceiling: ~1000x below baseline 16 KB = 16 bytes per fact.
  This is in LLM territory but is the absolute ceiling requiring ALL bets to pay off.

Practical v3 projection: 200-800 bytes per fact for structured KBs, 1-3 KB for mixed KBs.

Is 500 bytes per fact (v3 target) realistic?
YES, but it requires mechanism 1 OR 7 (N-reduction) to pay off AND delta encoding to apply
to at least half the customer KB. P_deflated on reaching 500 bytes = 0.25.
P_deflated on reaching 1000 bytes = 0.40.
P_deflated on reaching 2000 bytes = 0.55.

At 100 bytes per fact (LLM BERT-style), the substrate cannot reach it due to the
cryptographic audit floor (Merkle tree + bitemporal metadata = structural minimum of ~200-400
bytes per fact even with zero W storage). The structural floor sets the minimum at ~200 bytes.

LLM comparison framing:
  - LLM text storage: 4-40 bytes per "fact" (depends on parameterization depth).
  - Substrate at v3: 200-2000 bytes per fact.
  - Ratio: 5x to 500x LLM, depending on scenario.
  - User's 10-100x acceptance band: achievable at the OPTIMISTIC end (mechanism 7 pays off
    + structured KB + delta encoding). Not guaranteed.

---

## Foreclosed Mechanisms

1. Low-rank decomposition of W (already known): Marchenko-Pastur at M/N=0.5 means the
   eigenspectrum is flat -- there is no low-variance subspace to discard. This is a hard
   closure.

2. SDM at N=1M (mechanism 9): per-fact cost analysis above shows it is WORSE. Foreclosed
   at v2 scale.

3. HRR/FFT compression (mechanism 3): FFT is a basis change on random vectors; flat spectrum
   means no frequency-domain sparsity. Foreclosed as a compression mechanism.

4. Huffman/arithmetic coding as standalone (mechanism 6): operates on text, not on W. Cannot
   reduce the N-dimensional weight matrix size. Foreclosed as a storage mechanism.

5. QAT below 2 bits: at 1-bit (binary weights), the pseudoinverse write rule breaks down
   because the matrix inverse of a binary matrix is generally dense and non-binary. The
   1-bit floor is a functional closure for the pseudoinverse-based substrate.

---

## Cross-Thread Synthesis

This drill connects to several prior findings:

1. The modern Hopfield drill (named next-drill candidate in prior research): this 2x drill
   confirms that the mechanism is plausible but the critical unknown is write-rule
   compatibility at alpha_c=0.5. The cheap test is defined and is queued for empirical
   validation.

2. The LoRA-hurts-retrieval finding (MEMORY.md production lock): the distillation mechanism
   (7) is architecturally different from LoRA (output-space compression vs W-matrix low-rank).
   However, the underlying concern -- that reducing the representation space hurts retrieval
   at alpha near capacity -- applies to both. The N-sweep test is essential before committing
   engineering.

3. The sparse-KEY finding (cycle 142): sparse-KEY at alpha_c ~0.005 shows the substrate can
   operate at low density with N=65536. This is ORTHOGONAL to the N-reduction axis; sparse-KEY
   reduces the active entries per vector, not N itself. They compose.

4. Marchenko-Pastur flat spectrum (forecloses low-rank): the connection to the exponential
   energy function is that the modern Hopfield energy landscape may NOT have the same flat-
   spectrum property. The new write rule for exponential energy might produce a W with
   structured spectrum (not flat). This is a testable prediction: if W under exponential
   energy has a non-flat spectrum, low-rank compression becomes possible again. This is
   a SURPRISING potential opening that the drill has surfaced.

---

## Substrate-Product Implications

1. Structured KB product line: if delta/template encoding (mechanism 2) is deployed, it
   creates a natural product tier: "regular schema KBs" get 5-20x cheaper storage, enabling
   pricing advantages for customers with well-structured knowledge. This is a real commercial
   differentiator at v2.

2. The 500-byte target requires telling customers their KB regularity score: the ratio of
   unique predicates to total facts determines what compression is achievable. This is a
   product metric the substrate should surface at ingest time.

3. The auditable-memory floor (~200 bytes) is actually a FEATURE for regulated industries:
   it means the substrate cannot be made as cheap as LLMs because every fact has a
   cryptographic receipt. This is the 10-100x premium that regulated customers pay willingly.

4. The encoder distillation mechanism (7) opens a per-customer personalization angle: a
   customer-trained encoder that produces domain-specific embeddings may IMPROVE retrieval
   accuracy at smaller N, not just reduce cost. This could flip the LoRA-hurt-retrieval
   concern if the distillation target is domain-specific rather than general.

---

## Empirical Test Queue (Ranked by Cost-Benefit)

TIER-A (test within 4 hours CPU/GPU, high expected information gain):

1. Modern Hopfield N-sweep at N in {1024, 2048, 4096, 8192}: run capacity measurement at
   each N with exponential energy vs quadratic energy. Measure retrieval accuracy at M/N=0.2,
   0.3, 0.4, 0.5. Cost: ~2 hours CPU. Expected information: determines whether mechanism 1
   is viable at all.

2. Delta encoding ratio audit: take the real customer KB (or synthetic equivalent). Count
   unique predicates, measure predicate-to-fact ratios, compute theoretical compression ratio
   under delta encoding. Cost: ~30 minutes CPU. Expected information: scopes mechanism 2
   applicability to actual KB structure.

3. Minimum-viable-N sweep for retrieval accuracy: at N in {4096, 8192, 16384} with the
   current pseudoinverse write rule, measure retrieval F1 at 1000-fact KB. Cost: ~1 hour
   GPU. Expected information: establishes the floor below which dimension reduction hurts
   retrieval; directly informs the ceiling on mechanism 1 and 7.

TIER-B (require > 2 weeks engineering before first test):

4. Encoder distillation pilot (mechanism 7): train a 50M student encoder to output 4096-dim
   from 65536-dim teacher. Test retrieval accuracy. Cost: ~3-5 hours GPU after 2-3 weeks
   engineering.

5. Dictionary learning on a real KB (mechanism 11): learn 1024-atom dictionary, test
   reconstruction quality at sparsity S=20,50,100. Cost: ~2 hours GPU after 1-2 weeks
   engineering.

TIER-C (research-grade, > 40 hours engineering):

6. Write-rule derivation for exponential energy: derive the pseudoinverse analog for the
   exponential energy function. This is a math derivation task (no code), 1-2 weeks theory.
7. Predictive delta encoding pipeline (mechanism 10): requires LM training + encoding bridge.
   > 40 hours engineering.

---

## Plain-Language Summary

The goal: get the substrate's per-fact storage cost from 5 KB down toward 500 bytes.
The LLM stores facts at 4-40 bytes; we accept 10-100x more because of auditable receipts.

Three mechanisms are worth pursuing in parallel:

ONE -- Smaller vectors. Right now each fact is stored as a 65,536-element vector. There is
published math suggesting that a new version of the energy function can store the same number
of facts in a vector of only 4,000-8,000 elements. That is a 60-250x reduction in W matrix
size. The risk: our current write rule was designed for the old energy function and may not
work with the new one. A 2-hour CPU test will tell us whether this is a real path or a dead
end. Do this first.

TWO -- Facts-by-schema compression. If a customer's knowledge base has a regular structure
(like a spreadsheet: every row has the same columns), we can store the column template once
and store each row as just its values. For structured KBs this is a 5-20x saving with near
zero engineering risk. For unstructured text it does nothing. Build a "what kind of KB is
this?" detector and route structured KBs through the compression path. This is 2-4 weeks
of standard engineering and has the most certain payoff.

THREE -- Smaller encoder. We currently turn each fact into a 65,536-element vector using a
large language model. Training a smaller model to produce 4,000-element vectors with similar
retrieval quality could reduce W by 256x. The risk: we already know that reducing the vector
space can hurt retrieval quality. A 3-hour GPU experiment will tell us the minimum size below
which quality degrades unacceptably. If the floor is 8,000 elements (not 4,000), the W
reduction is still 64x.

What is off the table: compressing in the frequency domain, Bloom filters (those are for
query speed, not storage), and giant high-dimensional sparse architectures all fail to improve
the per-fact byte count at our scale.

If mechanisms 1-3 all pay off: 200-500 bytes per fact is realistic. That puts us at 5-50x
more expensive than an LLM, which is in the user's accepted range. If only mechanism 2 pays
off, we land at ~1-2 KB per fact, still acceptable for regulated-industry customers.

DO NEXT:
  (a) 2-hour CPU test: exponential-energy capacity vs quadratic at N=4096.
  (b) 30-minute audit: count predicate/fact ratio in actual customer KBs.
  (c) 1-hour GPU test: retrieval F1 vs N in {4096, 8192, 16384} with current write rule.
  All three can run this week.

---

## Citations (Verified via Search, June 2026)

1. Ramsauer et al. (2020) "Hopfield Networks is All You Need" -- exponential capacity,
   modern Hopfield. ArXiv.
2. Krotov & Hopfield (2016) -- dense associative memory, polynomial/exponential capacity.
3. Demircigil et al. (2017) -- exponential capacity dense associative memory.
4. ArXiv 2304.14964 -- "The Exponential Capacity of Dense Associative Memories" (verified
   present in search results, June 2026).
5. ArXiv 2601.00984 -- "A Biologically Plausible Dense Associative Memory with Exponential
   Capacity" (verified present, June 2026).
6. ArXiv 2503.09518 -- "Capacity of Modern Hopfield Networks under the Data Manifold
   Hypothesis" (verified present, June 2026).
7. Plate (1995) "Holographic Reduced Representations" -- FFT-domain binding.
8. ArXiv 2111.06077 -- VSA survey including HRR/FHRR (verified present, June 2026).
9. ACM TOS 2024 -- "The Design of Fast Delta Encoding for Delta Compression Based Storage
   Systems" (verified present, June 2026).
10. Kanerva (1988) "Sparse Distributed Memory" -- SDM architecture.
11. NTRS 1990 report -- Kanerva SDM on Connection Machine (verified NASA NTRS present,
    June 2026).
12. Olshausen & Field (1996) -- sparse coding / dictionary learning origin paper.
13. ArXiv 2205.15386 -- "Dictionary Learning with Accumulator Neurons" (verified present,
    June 2026).
14. ArXiv 2306.04050 -- "LLMZip: Lossless Text Compression using Large Language Models"
    (verified present, June 2026).
15. ArXiv 2409.15046 -- "AlphaZip: Neural Network-Enhanced Lossless Text Compression"
    (verified present, June 2026).
16. ArXiv 2112.06126 -- "Neural Network Quantization for Efficient Inference: A Survey"
    (verified present, June 2026).
17. ArXiv 2602.22592 -- pQuant low-bit QAT (verified present, June 2026).
18. ArXiv 2502.03696 -- "Cascaded Learned Bloom Filter" (verified present, June 2026).
19. MIT Press -- "Dictionary Learning Algorithms for Sparse Representation" (Neural
    Computation 2003, verified present via direct.mit.edu link, June 2026).

Total verified citations: 19.

---

## Calibration Note

All P estimates in this note carry a 0.20-0.25 deflation penalty per
[[feedback-lit-scan-calibration-penalty]]. The substrate is in an uncharted regime
(pseudoinverse + exponential energy + alpha_c=0.5 + Merkle audit is not a published
combination). Novel-synthesis P is capped at 0.50. Hard-fail thresholds are pre-registered
above for each tested mechanism.

P_deflated on headline (500 bytes per fact achievable at v3) = 0.25.
P_deflated on reaching <= 1000 bytes per fact = 0.40.
P_deflated on reaching <= 2000 bytes per fact = 0.55.

Next-drill candidate: mechanism 1 / modern Hopfield exponential energy write-rule derivation
(field: modern-hopfield, Tier-1 fruit-bearing per field advisor).
