# Wave 14d - Self-supervised concept discovery to replace PPMI

Research synthesis 2026-05-19. Question: PPMI on argmax-decoded position-pair
co-occurrences is a hand-crafted statistical prior. Can the substrate
discover its own concepts from data, and would that beat the +0.628 bpc
R10 best-config baseline at K=512?

## 1. TL;DR

The single highest-EV replacement for PPMI is **online sparse dictionary
learning (Mairal 2009) on the residual pool vectors after argmax-decoding**,
not on raw bytes. This is the only candidate that (a) operates directly in
the substrate's bundle space rather than over a hand-engineered tokenization
of it, (b) is theoretically guaranteed to recover a basis that minimizes
reconstruction error of the actual interference-corrupted vectors PPMI
currently ignores, and (c) yields concepts that are NOT a Borel function of
argmax(G), so it can break the Lippl-Stachenfeld 2025 redundancy ceiling
that limits PPMI fusion. Expected gain at K=512: **+0.05 to +0.15 bpc over
the +0.628 baseline**, with credible downside of zero if interference noise
in the pool is dominated by orthogonal-atom shot noise rather than
structured pair co-occurrence. PCA, K-SVD, and k-means are predicted to
match or slightly underperform PPMI; sparse coding with an over-complete
dictionary and L1 sparsity is the one with substrate-unique mechanism.

## 2. Literature on self-supervised concept discovery

### 2.1 Sparse coding (Olshausen-Field 1996)

[Olshausen-Field Nature 1996](https://www.nature.com/articles/381607a0) and
follow-up [Olshausen-Field Vision Research 1997](https://doi.org/10.1016/S0042-6989\(97\)00169-7).

Objective: find dictionary D and codes a such that x ~ D a with a sparse.

$$ \min_{D, a} \sum_i \|x_i - D a_i\|_2^2 + \lambda \|a_i\|_1 $$

Properties:
- D is over-complete (more atoms than dimensions): K_atoms > N.
- Atoms are NOT orthogonal; they are an over-complete frame.
- Produces "parts-based" features: Gabor-like filters from natural images,
  phoneme-like atoms from speech.
- Cost: alternating minimization, expensive at scale; non-convex jointly
  but convex in each block.

For HDC: pool vectors are sums of (pos, byte) atoms. A learned sparse
dictionary over pool vectors would recover something CLOSER to the original
atoms (or their products) — but with weighting that reflects actual usage
frequency, not uniform.

### 2.2 Sparse autoencoders for interpretability (Cunningham 2023, Anthropic)

[Cunningham et al. arXiv:2309.08600](https://arxiv.org/abs/2309.08600)
"Sparse Autoencoders Find Highly Interpretable Features in Language Models".

[Bricken-Templeton 2023 "Towards Monosemanticity"](https://transformer-circuits.pub/2023/monosemantic-features)
and [Templeton et al. 2024 "Scaling Monosemanticity"](https://transformer-circuits.pub/2024/scaling-monosemanticity).

Method: train a one-hidden-layer autoencoder with ReLU and L1 penalty on
hidden activations. Dictionary size 8-128x model dim. Extract features as
the column vectors of the decoder.

What it gives:
- Monosemantic features (one feature = one concept), much cleaner than
  raw neurons.
- Cost: ~10-100x model params in dictionary, requires training data passing
  through the host model.

For HDC: substrate has NO hidden layer in the LLM sense. The "neurons" are
the N=1024 (or 4096) bundle dimensions, and they are SUPERPOSITIONS by
construction. A SAE on bundle vectors would discover the linear basis
that maximally explains pool variance with sparsity — directly analogous
to dictionary learning, with a learned encoder. Expected to be roughly
equivalent to sparse coding for our purposes.

### 2.3 Dictionary learning - K-SVD and online (Mairal 2009)

[Aharon-Elad-Bruckstein K-SVD 2006](https://doi.org/10.1109/TSP.2006.881199).
[Mairal et al. ICML 2009](https://www.di.ens.fr/~fbach/mairal_icml09.pdf)
"Online Dictionary Learning for Sparse Coding"
[arXiv:0908.0050](https://arxiv.org/abs/0908.0050).

K-SVD: alternating between sparse coding (with current D) and SVD-based
atom updates. Online dictionary learning: streaming version with stochastic
approximation; O(P N K) per pass.

For HDC: pool has P ~ 50k entries of dim N=1024. Online dictionary learning
with K_atoms=512 and L1 sparsity costs ~1 GPU minute, comparable to PPMI.

### 2.4 NMF (Lee-Seung 1999) for parts-based features

[Lee-Seung Nature 1999](https://www.nature.com/articles/44565)
"Learning the parts of objects by non-negative matrix factorization".

Constraint: X = W H with W, H >= 0. Produces strictly additive
parts-based decomposition.

For HDC: BSC pool vectors are bipolar {-1, +1}, NOT non-negative. NMF
would require representing pool as one-hot per-position-per-byte
(non-negative) — which is essentially the PPMI co-occurrence matrix
again. Predicted to be near-equivalent to PPMI in performance, with no
mechanism advantage.

### 2.5 Topic models - LDA (Blei 2003)

[Blei-Ng-Jordan JMLR 2003](https://www.jmlr.org/papers/v3/blei03a.html)
"Latent Dirichlet Allocation".

Probabilistic generative model: each document is a mixture of latent
topics; each topic is a distribution over words.

For HDC: each pool entry could be a "document" of K bytes. LDA would
discover topic-level structure — but byte K-grams are too short (K=512
bytes is ~one paragraph) and the vocabulary is too small (256 bytes) for
LDA's Dirichlet prior to find meaningful structure. Predicted to
underperform PPMI; LDA needs document collections with multinomial
structure that bytes lack.

### 2.6 InfoNCE / contrastive (van den Oord 2018, Chen SimCLR 2020)

[van den Oord et al. arXiv:1807.03748](https://arxiv.org/abs/1807.03748)
"Representation Learning with Contrastive Predictive Coding".
[Chen et al. arXiv:2002.05709](https://arxiv.org/abs/2002.05709) SimCLR.

Learn features by maximizing mutual information between contextually
related views; sidesteps explicit generative model.

For HDC: would require defining positive/negative pairs over pool
entries. Substrate-natural choice: positives are entries from the same
local window of training stream; negatives are random pool entries.
This is a real candidate but more engineering than sparse coding for
the same expected gain.

### 2.7 Vector-symbolic concept discovery (substrate-native)

[Sutor-Aerts-Kanerva 2022 arXiv:2202.04481](https://arxiv.org/abs/2202.04481)
"Resonator Networks Outperform Optimization Methods at Symbolic Discovery
Tasks". Resonator dynamics CAN surface latent factors WITHOUT external
training, but only for clean factored inputs.

[Kymn-Mazelet-Olshausen-Sommer 2024 arXiv:2406.19121](https://arxiv.org/abs/2406.19121)
"Compositional Factorization of Visual Scenes with Convolutional Sparse
Coding and Resonator Networks" - the relevant paper. Combines sparse coding
with resonator factorization: sparse coding finds atoms, resonator binds.

[Frady-Kleyko-Sommer 2018 arXiv:1812.01087](https://arxiv.org/abs/1812.01087)
"A Theory of Sequence Indexing and Working Memory in Recurrent Neural
Networks". Trajectory of bundles can be unpacked by resonator iteration,
but unpacking requires the codebook to already exist.

Key implication: the substrate's resonator dynamics presume a codebook.
The codebook can be the byte-atom set (what we use now) OR a learned
dictionary. The novel direction is the latter.

## 3. Substrate-specific options

### 3.1 PCA of bundle matrix

Take pool matrix P in R^{50k x 1024}, compute SVD, keep top-k components
as concepts.

Mechanism: top-k principal components capture maximum variance directions
in pool space. Useful concepts = directions where pool entries strongly
agree.

Cost: ~30 sec for SVD; one-shot.

Why it probably doesn't help: bundle matrix is composed of nearly
orthogonal random atoms summed; eigenvalue spectrum is approximately
Marchenko-Pastur from the random matrix theory perspective. Principal
directions WILL pick up the most-frequent (pos, byte) atoms but as
LINEAR COMBINATIONS that are not interpretable and not byte-aligned.
Effectively a re-basis of bundle space, not a concept dictionary.

**Prediction: +0.00 to +0.02 bpc over baseline. PPMI knows the
position-byte structure; PCA throws it away by mixing across positions.**

### 3.2 Sparse coding (Olshausen-Field) on pool

Learn over-complete dictionary D in R^{1024 x 2048} such that
each pool vector x ~ D a with a sparse.

Mechanism: dictionary atoms become "schema fragments" that explain
common pool-vector patterns. Unlike PPMI which sees only argmax-decoded
bytes, sparse coding sees the full bundle including the interference
mass that argmax discards.

Cost: ~5 GPU minutes for K_atoms=2048, P=50k.

Why it's the best candidate:

1. Operates on bundle vectors directly - sees information that argmax
   destroys. Specifically: at K=512 the per-position argmax has
   error rate > 0% from bundle interference; the residual interference
   mass IS predictive of byte identity (Bayes-optimal soft posterior),
   and PPMI on argmax cannot see it. Sparse coding can.

2. Atoms are not constrained to be byte-aligned. They can pick up
   trigram-like or longer structure that PPMI pair-counting cannot
   represent.

3. Not a Borel function of argmax(G); Lippl-Stachenfeld 2025
   redundancy corollary does NOT apply.

**Prediction: +0.05 to +0.15 bpc over baseline at K=512. Risk:
interference noise in pool may be largely structureless (Gaussian-like
from CLT on 1024 atoms summed), in which case sparse coding finds the
same pair structure PPMI finds plus noise atoms = no gain.**

### 3.3 K-SVD on pool

K-SVD is sparse coding's batch dual: same objective, different solver.

Cost: ~10 GPU minutes for K_atoms=2048.

Why predicted equivalent to sparse coding: same Frobenius+L1 objective.
The Mairal online version is faster and easier to tune. Predicted
gain identical to 3.2 within noise.

### 3.4 k-means in BSC space

Cluster pool entries into k centroids; each centroid is a "concept".

Mechanism: pool entries that are bundle-similar (high BSC overlap) get
the same cluster label. Centroid is a soft majority-vote bundle.

Cost: ~1 GPU minute.

Why predicted to underperform: k-means assumes Euclidean cluster
structure that bipolar bundles don't have well. BSC space has near-
uniform pairwise distance for random vectors (curse of high dimensions)
and the cluster signal is weak relative to interference. K=512 pool
entries don't form tight clusters; the substrate is INHERENTLY
distributed.

**Prediction: +0.00 to +0.03 bpc. PPMI extracts hundreds to thousands
of pair atoms; k-means would need k > 10000 to match the resolution,
at which point it's just over-fitting.**

### 3.5 Resonator-discovered concepts (substrate-native)

Run resonator dynamics on pool entries WITHOUT a known codebook;
iterate until convergence; collect the converged factor vectors as
"discovered concepts".

Mechanism: resonator (Frady-Kent-Olshausen-Sommer 2020) factorizes
bundles into (pos, byte) factors when codebooks are given. Without
codebooks, the dynamics don't converge to a fixed point - they
explore the full bundle space. So this is not naturally
self-supervised in the literature sense.

**Prediction: not a credible candidate without further mechanism
development. Not pursued.**

### 3.6 Soft-posterior PPMI (the M2 escape from R10 deep dive)

Replace argmax in decompose_pool with full softmax posterior; compute
PPMI using soft expected counts.

This is NOT self-supervised concept discovery - it is still PPMI - but
it IS the lightest test that demonstrates pool-level information beyond
argmax matters. Should be the FIRST experiment, as a baseline beyond
which sparse coding must add value.

## 4. Predicted bpc impact (mechanism-grounded)

| Method | Mechanism for gain | Mechanism for failure | Predicted gain at K=512 over +0.628 |
|---|---|---|---|
| Soft-posterior PPMI | Recover argmax-quantization loss | If argmax error rate is low, no info | +0.02 to +0.05 |
| PCA on pool | Top variance directions | Mixes across positions, no byte-level | 0 to +0.02 |
| Online sparse coding | Captures non-Borel structure; over-complete | Interference is structureless | +0.05 to +0.15 |
| K-SVD | Same as sparse coding | Same | +0.05 to +0.15 |
| NMF on co-occurrence | Same info as PPMI, different solver | Same info as PPMI | -0.02 to +0.02 |
| LDA | Topic structure | K=512 bytes too short, vocab too small | -0.05 to 0 |
| k-means | Cluster majority concepts | High-dim bipolar has no clusters | 0 to +0.03 |
| InfoNCE/contrastive | Local-window pairs | More tuning, similar mechanism to sparse coding | +0.03 to +0.10 |
| SAE on pool | Same as sparse coding with learned encoder | Same | +0.05 to +0.15 |

### Per-concept bpc analysis (the user's question 6)

At K=64, R10 gains ~+0.4 bpc with N_concepts=100; that's +0.004 bpc per
concept on average. The PPMI scores are heavily Zipfian - top-10
concepts likely carry 50% of the gain, the bottom 50 carry < 10%.

Per-concept ceiling argument: Bayes-floor bound says max gain per
independent estimator added to a strong baseline is bounded by
(1/2) log2(1 + sigma_r^2/sigma_c^2). For K=512 with retrieval noise
sigma_r ~ sqrt((2B-1)/N) ~ 0.15 and current PPMI noise sigma_c ~ 0.3,
a SINGLE optimal concept atom could give up to ~0.05 bpc; ten
near-orthogonal ones up to ~0.4 bpc. So a 10-concept sparse-coding
dictionary that is genuinely orthogonal in noise structure could MATCH
or BEAT the 500-concept PPMI total.

**This is the substrate-unique mechanism: information density per
concept, not count.**

## 5. Right experiment design for smallest credible test

### Phase 0 (1 hour, sanity check): soft-posterior PPMI

Drop-in replacement: in extract_ppmi, change pool_byte_at_pos from
argmax to soft posterior expectations. Use soft counts (fractional
co-occurrence) for PMI. K=64 (cheapest), 3 seeds.

Pass criterion: mean(soft - argmax) > 0.01 bpc, t > 2. If yes:
information at sub-argmax level is real, sparse coding worth pursuing.
If no: argmax loses nothing; sparse coding probably also loses; pivot
to a different question entirely (e.g., bigger pool, different
substrate).

### Phase 1 (3 hours, main experiment): online sparse coding vs PPMI

Implementation: scikit-learn `MiniBatchDictionaryLearning`
(Mairal 2009 online algorithm) on pool matrix at end of training
phase. K_atoms in {128, 512, 2048}; alpha (L1 weight) in {0.1, 1.0, 10}.

Concepts at retrieval: replace `concept_active` boolean from PPMI
pair-matching with sparse code `a_query` from encoding the query
bundle via the trained dictionary. Linear fusion identical to R10.

Phases:
- K=64, N=1024, 5 seeds, single (K_atoms=512, alpha=1.0) config
- If gain > +0.02 over PPMI at K=64 (t > 2): expand to K=512, 3 seeds
- If gain > +0.05 over PPMI at K=512: claim substrate-unique mechanism

Pre-registered failure threshold:
- mean(sparse - PPMI) < 0.01 at K=64 with SE < 0.005: kill the
  hypothesis; PPMI is near-optimal for byte K-grams
- mean(sparse - PPMI) > 0.03 at K=64: continue
- intermediate: K-sweep at K in {16, 64, 256, 512}

### Phase 2 (5 hours, mechanism confirmation): substrate-unique tests

If Phase 1 passes:

1. **Domain transfer**: train sparse dictionary on Wikitext, freeze
   atoms, evaluate on code corpus. PPMI is corpus-specific (it's
   literal byte-pair statistics); sparse atoms might transfer. Expected
   transfer gap: PPMI loses ~50% of its gain; sparse coding loses
   ~20%. If this holds, this is the product story.

2. **Concept-count scaling**: 10, 30, 100, 300, 1000 atoms. PPMI
   plateaus; sparse coding stays steeper (information per atom is
   higher). The PPMI-plateau-at-100 vs sparse-keeps-rising-to-300
   curve, if observed, is the cleanest evidence for substrate-unique
   capability.

3. **Atom interpretability**: project sparse atoms back into
   byte-position space (D.T @ pos_atoms_pinv @ byte_atoms_pinv) and
   inspect. If atoms correspond to trigrams or longer schema fragments
   (e.g., "the ", "ing\n", "{ }"), this is the explainability story.

### Smallest credible test (the ONE replacement)

If I can run only one experiment: Phase 1 K=64 sparse-vs-PPMI head-to-head,
5 seeds, both methods tuned. Cost: ~75 min. Pass if mean gain > 0.02 bpc
with t > 2.

## 6. Brain mapping

Hippocampus has TWO complementary subsystems relevant here:

**Dentate gyrus (DG): pattern separation.** Sparse activity (~1-5% of
granule cells fire), high dimensionality, decorrelation. DG takes
overlapping cortical input and produces near-orthogonal output codes.
Mechanism: feed-forward inhibition + sparse expansion + Hebbian-tuned
mossy-fiber synapses. [Schapiro et al. 2017 Phil Trans Roy Soc
B](https://doi.org/10.1098/rstb.2016.0049) "Complementary learning systems
within the hippocampus: a neural network modelling approach to reconciling
episodic memory with statistical learning".

DG <-> sparse coding: both produce sparse, decorrelated codes from
denser inputs. The substrate's pool entries are dense bundles; sparse
coding gives the DG-like sparse code.

**CA1: schema completion.** Receives DG output via CA3 and reconciles
with neocortical context (entorhinal). Performs pattern COMPLETION:
given partial input, fills in the rest by associative recall on Hebbian
weights. [Kumaran-Hassabis-McClelland 2016 Trends Cog Sci](https://doi.org/10.1016/j.tics.2016.05.004)
"What learning systems do intelligent agents need? Complementary learning
systems theory updated".

CA1 <-> the LLM substrate: the LLM acts as the schema-completer,
predicting next byte given context. PPMI / sparse-coding concepts
are the DG-side; they tag relevant patterns, the host model completes.

**The CLS-aligned design**: extract concepts via sparse coding (DG
analog) during a CONSOLIDATION phase between training and retrieval -
distinct from both. This matches the user's framing: a "concept-
extraction" phase distinct from retrieval. The phase mirrors slow-wave
sleep's hippocampal replay phase where DG sparse codes reactivate.

[Káli-Dayan 2004 Nature Neurosci](https://doi.org/10.1038/nn1202)
"Off-line replay maintains declarative memories in a model of
hippocampal-neocortical interactions" predicts this consolidation
gives better generalization than online learning - which maps to
the domain-transfer test in Phase 2.

## 7. Product implications

Self-discovered concepts unlock three product narratives that
hand-crafted PPMI cannot:

**1. Domain transfer.** PPMI concepts are literal byte-pair statistics:
the (pos=2, byte='\n') ∧ (pos=3, byte='#') concept is Markdown-header
specific. Train substrate on corpus A (e.g., Wikitext) then deploy
on corpus B (e.g., code) - PPMI atoms are stale. Sparse-coding atoms
discovered from pool BUNDLES are more abstract; they should transfer
better because the atoms are in vector space, not byte-position space.

Testable: train on Wikitext, evaluate frozen concepts on code; report
gain-retention ratio (PPMI vs sparse).

**2. Compositional generalization.** PPMI atoms are 2-grams of (pos,
byte). They cannot compose: "the " is not a PPMI atom of "(pos=2,
't'),(pos=3,'h'),(pos=4,'e'),(pos=5,' ')" - it's four pair-atoms.
Sparse dictionary atoms are full N-dim vectors that can encode arbitrary
substructure simultaneously across all positions.

Testable: at retrieval, a sparse-coding query encoding will activate
multiple atoms simultaneously; their LINEAR COMBINATION can encode
schemas that no single PPMI pair-atom captures.

**3. Explainability.** PPMI atoms ARE human-readable: "(pos=2, '\n') ∧
(pos=3, '#') = Markdown header line at position 2". This is PPMI's
ONE genuine advantage. Sparse atoms are 1024-dim vectors; need
post-hoc interpretation.

But: sparse atoms CAN be interpreted by inspecting which (pos, byte)
atoms they correlate with most strongly. The interpretation will often
be richer than PPMI's pairs (e.g., "this atom = English-prose word
boundary plus following capital letter"). The pure explainability
crown goes to PPMI; sparse coding is more EXPRESSIVE at the cost of
interpretation overhead.

## 8. Why PPMI works at all on byte K-grams (the user's question 6)

PPMI exploits two properties of English/code byte streams:

1. **Strong byte-bigram statistics.** "th", "he", "in", "an" are the
   most common English bigrams; "  " (double space) and "\n#" (Markdown
   header) are strong code/markdown signals. Mutual information between
   adjacent bytes is high (~1-2 bits per pair in English).

2. **Positional regularity.** At fixed K, certain positions have
   predictable byte distributions (e.g., position 0 after a newline
   has elevated P('#'), P(' '), P('\t')). PPMI keys on (i, b_i) ∧
   (j, b_j) preserves this.

Why PPMI is NOT optimal:
- It uses argmax-decoded bytes, throwing away the substrate's
  bundle-level interference signal that the soft posterior carries.
- It is pair-only (2-gram), not higher-order. Trigram and 4-gram
  structure exists in English/code (chr-CFG-like) and is not captured.
- It is corpus-specific by construction; transfer is poor.

Per-concept contribution at K=64 with 100 concepts: ~+0.4 bpc / 100 =
+0.004 per concept AVERAGE, but the distribution is sharply Zipfian.
The top 10 PPMI concepts probably carry 50%+ of the total gain.

This is precisely where sparse coding should win: 30 sparse atoms with
maximum information density per atom can deliver the same +0.4 bpc,
and 100 sparse atoms can push it to +0.6-0.7 bpc that PPMI cannot
reach because PPMI's atoms are bottlenecked by pair-counting.

## 9. Brutal honesty section

**Is PPMI already near-optimal for byte K-grams?** Plausibly yes for
the specific quantity it computes (pair MI). The headroom for
self-supervised concept discovery rests on three claims:

1. Pool interference at K=512 carries information argmax destroys.
   This is the M2 escape from the R10 deep dive and is testable in
   one experiment. If false, sparse coding has no mechanism advantage.

2. Sparse atoms can encode multi-byte schemas pair-atoms cannot.
   Plausible but unproven for byte streams; vision sparse coding
   does this well (Gabor filters > pixel pairs) but bytes are
   not pixels.

3. The Lippl-Stachenfeld 2025 redundancy ceiling actually binds.
   At K=512 we're well above the K-threshold where redundancy
   ceiling matters; the +0.628 baseline is already inside that
   regime, so sparse coding has to compete with a strong baseline.

**Honest expected value**: 50% probability sparse coding gives
+0.02 to +0.08 bpc over baseline (worth shipping); 30% probability
it gives +0.00 to +0.02 (matches PPMI, not worth the complexity);
20% probability it gives +0.08 to +0.20 (substrate-unique capability
established). Expected gain: ~+0.05 bpc.

This is not a swing-for-the-fences experiment. It is the
substrate-discipline experiment: replace one hand-crafted prior with
data-driven learning and measure. The downside is bounded; the upside
is moderate; the mechanism story is clean. Worth running.

## 10. Sources

Core literature:
- [Olshausen-Field Nature 1996](https://www.nature.com/articles/381607a0)
  - foundational sparse coding
- [Olshausen-Field Vision Research 1997](https://doi.org/10.1016/S0042-6989\(97\)00169-7)
  - over-complete sparse coding
- [Aharon-Elad-Bruckstein K-SVD 2006](https://doi.org/10.1109/TSP.2006.881199)
  - batch dictionary learning
- [Mairal et al. arXiv:0908.0050](https://arxiv.org/abs/0908.0050)
  - online dictionary learning, what to use in practice
- [Lee-Seung Nature 1999](https://www.nature.com/articles/44565)
  - NMF
- [Blei-Ng-Jordan JMLR 2003](https://www.jmlr.org/papers/v3/blei03a.html)
  - LDA
- [van den Oord et al. arXiv:1807.03748](https://arxiv.org/abs/1807.03748)
  - CPC / InfoNCE
- [Chen et al. arXiv:2002.05709](https://arxiv.org/abs/2002.05709)
  - SimCLR

Anthropic interpretability:
- [Cunningham et al. arXiv:2309.08600](https://arxiv.org/abs/2309.08600)
  - SAEs find interpretable features
- [Bricken-Templeton 2023](https://transformer-circuits.pub/2023/monosemantic-features)
  - Towards Monosemanticity
- [Templeton et al. 2024](https://transformer-circuits.pub/2024/scaling-monosemanticity)
  - Scaling Monosemanticity (Claude 3 Sonnet)

VSA-native:
- [Sutor-Aerts-Kanerva arXiv:2202.04481](https://arxiv.org/abs/2202.04481)
  - resonator at symbolic discovery
- [Kymn-Mazelet-Olshausen-Sommer arXiv:2406.19121](https://arxiv.org/abs/2406.19121)
  - convolutional sparse coding + resonator
- [Frady-Kleyko-Sommer arXiv:1812.01087](https://arxiv.org/abs/1812.01087)
  - sequence indexing theory
- [Lippl-Stachenfeld arXiv:2405.16391](https://arxiv.org/abs/2405.16391)
  - redundancy ceiling (R10 deep dive reference)

Brain CLS:
- [Schapiro et al. Phil Trans Roy Soc B 2017](https://doi.org/10.1098/rstb.2016.0049)
  - CLS within hippocampus
- [Kumaran-Hassabis-McClelland Trends Cog Sci 2016](https://doi.org/10.1016/j.tics.2016.05.004)
  - CLS updated
- [Káli-Dayan Nature Neurosci 2004](https://doi.org/10.1038/nn1202)
  - off-line replay for consolidation

Internal references:
- `notes/wave14b_r10_deep_dive.md` - R10 mechanism analysis
- `notes/STATE_2026_05_19.md` - +0.628 at K=512 baseline
- `experiments/exp_wave14b_r10_best_config_K512.py` - current PPMI
  implementation, lines 123-144 (extract_ppmi)
