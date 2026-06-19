# Wave 14d - In-context learning via pool retrieval: research synthesis

Drafted 2026-05-19. Unbiased framing: not "is HDC pool an ICL substrate?"
but "what does softmax-over-stored-keys do mathematically, and how
does that mechanism compose with a delta-rule W?" The answer is the
contribution; the AI label is a side effect.

## 1. TL;DR

1. **Pool retrieval is mathematically a single attention layer with
   frozen keys** - softmax(beta * <ctx, x_i>) is identical to a one-shot
   transformer attention head whose KV cache is the pool. So
   pool-augmentation IS in-context learning, by construction; the
   empirical question is only the *magnitude*, the *sample-efficiency
   slope*, and whether the substrate has the regression-like
   posterior-update structure Xie/Akyurek/Garg analyze, or only the
   coarser nearest-neighbor structure (Wang 2022, kNN-LM).
2. **The proposed test is the right shape but underpowered on three
   axes**: corpus B is too close in byte-statistics to corpus A; N=64
   is too small relative to POOL_SIZE=1024 unless we eviction-bias; and
   ALPHA=0.3 caps the maximum reachable delta at roughly
   0.3 * H(P_W || P_pool), which for a strong W and a weak pool prior
   is probably under the +0.05 bpc threshold even when ICL is real.
3. **Recommended changes**: (a) replace corpus B with byte-distribution-
   shifted material (raw JSON or hex-encoded binary, not Python source);
   (b) extend N to {0, 4, 16, 64, 256, 1024} and report the
   sample-efficiency *curve*, not a single threshold; (c) include an
   ALPHA sweep {0.3, 0.5, 0.7, 1.0} so the linear-fusion cap doesn't
   mask the effect; (d) add a "pool only, W zeroed" head as an upper
   bound on the in-context channel; (e) lower the rejection threshold
   to >= 0.015 bpc with multi-seed t-test (per the same logic that
   rescued R10).

## 2. Literature on retrieval-as-ICL

### 2.1 The Bayesian-implicit view (Xie et al. 2021)

Xie's "An Explanation of In-Context Learning as Implicit Bayesian
Inference" (arXiv:2111.02080) frames ICL as: given a prompt that's a
concatenation of (input, output) pairs from a latent concept theta,
the model approximates p(y_query | x_query, prompt) = integral over
theta of p(y|x,theta) p(theta|prompt). The model "infers" theta from
the prompt.

**Mathematical analog in our substrate**: theta = the corpus-B
distribution. The "prompt" = N corpus-B entries inserted in the pool.
The softmax-over-similarity weights w_i = softmax(beta * <ctx, x_i>)
play the role of p(theta | prompt) - they're the posterior weight on
each stored "hypothesis" given the query context. The retrieved
distribution `P_retr = sum_i w_i * delta(label_i)` is then a Monte-
Carlo estimate of integral p(y|x,theta) p(theta|prompt) where the
particles {(x_i, label_i)} draw from the augmented mixture
((1024-N)/1024 * D_A + N/1024 * D_B).

**This is a real mechanistic match**, not a metaphor. The catch: Xie
assumes the model has enough capacity to represent the posterior;
our pool, with sum-bundle binding at K=4, can only resolve concepts
the bundle can decompose, which is a real bottleneck.

### 2.2 Induction heads (Olsson et al. 2022)

Olsson's "In-context Learning and Induction Heads" (Anthropic) shows
induction heads do prefix-matching + copying: see "AB...A" -> predict
"B". This is content-addressed retrieval. The "AB" bigrams are stored
in the residual stream; the second "A" generates a query that hits
"AB" via QK; the OV head copies "B".

**Mathematical analog**: our pool stores (ctx_i, label_i) which is
exactly an "AB" bigram (ctx_i = A-side encoding, label_i = B-side
prediction). The softmax-similarity is the QK; the scatter_add into
P_retr is the OV head. So our pool implements one induction head with
frozen keys. The corpus-B augmentation is "show the model 64 new
(A,B) pairs"; standard induction-head theory predicts copy accuracy
should rise linearly in N until the softmax saturates or the keys
collide.

### 2.3 Linear regression ICL (Akyurek et al. 2022, Garg et al. 2022)

Akyurek (arXiv:2211.15661) and Garg (arXiv:2208.01066) prove
transformers can implement ridge regression / gradient descent in-
context. The mechanism: attention's softmax(QK^T)V with the right
weight structure performs one step of GD on a regression loss whose
training set is the prompt.

**Analog**: our pool weights are exactly softmax(beta * <q, x_i>).
The output P_retr = sum_i softmax(beta * q^T x_i) * y_i IS the
Nadaraya-Watson kernel regressor with a similarity kernel. This is
mathematically identical to the "kernel regression" reading of
attention (Tsai et al. 2019). At ALPHA=1.0, the substrate would
perform kernel regression over the pool with zero contribution from W.

**Critical math note**: Garg shows the regression-ICL behavior
requires the *value* side (here: label_i one-hots) to be a linear
function of the input (here: ctx_i). Our setup has discrete byte
labels, not continuous regression targets, so the Garg-style
exponential sample-efficiency doesn't apply directly. We're in
Wang's territory, not Garg's.

### 2.4 Neighbor-retrieval ICL (Wang et al. 2022, Khandelwal 2020)

Khandelwal's kNN-LM (arXiv:1911.00172) interpolates a parametric LM
with a kNN retriever over a stored corpus: p(y) = lambda * p_LM(y) +
(1-lambda) * p_kNN(y). This is *exactly* our ALPHA * P_retr +
(1-ALPHA) * P_W. The kNN-LM literature is the most direct precedent.

Wang 2022 (arXiv:2212.10375) shows transformers in-context learn by
nearest-neighbor lookup when the prompt examples are explicit (x,y)
pairs. The substrate's pool is the explicit storage Wang's transformer
has to construct internally - we *start* in the regime Wang's model
has to learn into.

**Implication for our experiment**: we should expect ICL-via-pool to
behave like kNN-LM, not like full attention-ICL. Khandelwal reports
~2-3 bpc improvement at full corpus retrieval; at N=64 added entries
out of 1024, the effective improvement scales as N/POOL_SIZE times
the per-entry information, which is in the 0.02-0.10 bpc range. **The
0.05 bpc threshold is in the right ballpark but on the optimistic
side**; we should pre-register 0.015-0.020 bpc as the real signal
threshold (per the R10 lesson - aspirational thresholds can hide
real effects).

### 2.5 The shared kernel-regression skeleton

All five lines (Xie, Olsson, Akyurek, Wang, Garg) reduce to: the
softmax-of-inner-product over stored (key, value) pairs is a
*posterior-weighted mixture* over hypotheses. Our pool is a frozen,
explicit instance of that mixture. Whether ICL "works" reduces to two
sub-questions:

1. **Selectivity**: do new corpus-B entries get high softmax weight
   when the query is a corpus-B context? (Yes if BSC similarity is
   informative about distribution; this is the byte-statistics
   question of section 4.)
2. **Coverage**: are 64 entries enough to span the corpus-B input
   manifold? (Probably no - see section 5.)

## 3. Recommended experiment design

### 3.1 Modes (keep mostly as designed; add two)

| Mode | Description | Purpose |
|---|---|---|
| off | W only | baseline |
| pool_A | W + corpus-A pool | standard fusion baseline |
| pool_A + N irrelevant | W + pool + N corpus-A entries | control for "pool size shift" confound |
| pool_A + N relevant | W + pool + N corpus-B entries | the ICL test |
| **pool_only_relevant** (NEW) | ALPHA=1.0 with N corpus-B entries | ceiling: what can pure retrieval do? |
| **W_only_corpus_B** (NEW) | W retrained on corpus B from scratch | floor for the "what W could learn" comparison |

The two new modes bracket the achievable range and prevent ALPHA
masking. `pool_only_relevant` is the cleanest ICL measure: it isolates
whether the retrieval channel itself is doing in-context inference.

### 3.2 N range

Replace {0, 4, 16, 64} with **{0, 4, 16, 64, 256, 1024, 2048}**.
- 0 -> 64: under-eviction regime; new entries don't displace existing
  pool. Effect should grow ~linearly in N here (Khandelwal regime).
- 256 -> 1024: matched-eviction regime; new entries displace ~25% to
  100% of pool_A. Effect saturates or peaks.
- 2048: over-saturation regime; pool is fully corpus-B (FIFO has
  evicted all of pool_A). Tests whether pool-only on corpus-B beats
  W-on-corpus-A (a genuine "the substrate learned the new domain in
  context, without weight updates" claim).

The interesting science is in the *shape* of the curve, not the value
at any single N. Report log(N) vs delta-bpc on a single plot.

### 3.3 ALPHA sweep

ALPHA in {0.3, 0.5, 0.7, 1.0} for at least N in {0, 64, 1024}. The
linear-fusion identity ALPHA * P_retr + (1-ALPHA) * P_W means the
maximum achievable retrieval gain is bounded by ALPHA * (H(P_W) -
H_min). With ALPHA=0.3 and a confident P_W, the maximum delta is
roughly 0.3 * H(P_W). If P_W has entropy ~3 bits on test_B, the cap
is ~0.9 bpc - plenty of room - but if P_W is *very* confidently
wrong (entropy <1 bit), ALPHA=0.3 caps the achievable correction at
0.3 bpc and we could miss a strong ICL signal.

### 3.4 Corpus B choice - the key change

Python source vs project markdown is a weak distribution shift in
byte-4-gram space. Both are mostly ASCII printable, both use English
words and identifier-like tokens, both have heavy whitespace. The
KL between byte-4-gram distributions is small.

**Recommended corpus B candidates, in increasing distribution shift**:

| Candidate | KL from markdown (4-gram) | Notes |
|---|---|---|
| Python source (current) | small (~0.5-1 bit) | Too close. Markdown has code blocks. |
| **JSON dumps** | moderate (~1.5-2.5 bits) | Punctuation-heavy, different structure tokens |
| **Base64-encoded blobs** | large (~3-4 bits) | Restricted alphabet, uniform 4-gram distribution |
| **UTF-8 Japanese text** | large (~3-5 bits) | Multi-byte sequences, non-ASCII range |
| **Hex-encoded binary** | very large (~4-6 bits) | Only 16 byte values used |
| **Raw binary (PNG/zip)** | maximal (~6-7 bits) | Non-printable bytes, no English structure |

**Recommendation: run corpus B = JSON dumps as primary and corpus B =
hex-encoded binary as secondary**. JSON is "close enough that W's
representation is partially useful" - the realistic deployment case.
Hex-binary is "the new domain shares almost no atoms with the old" -
the worst case for ICL and the most informative null. Together they
sweep the easy/hard axis.

Avoid Python source as primary; it's a noise floor, not a test.

### 3.5 Pre-registered decision rule (revised)

- delta = bpc(irrelevant) - bpc(relevant) at N=256, mean over 5 seeds
- ICL CONFIRMED: delta >= 0.015 AND seed-SE < 0.008 (t > 4)
- ICL WEAK: 0.005 <= delta < 0.015 OR t in (2, 4)
- ICL NULL: delta < 0.005 OR opposite sign
- ICL REVERSE: delta <= -0.015 (irrelevant entries actively help -
  suggests softmax-collision is the real mechanism, not content match)

The 0.05 threshold from the current script is fine as a "strong ICL"
threshold but should not be the rejection cutoff.

## 4. Predicted outcomes (with mechanism)

### 4.1 Corpus B = Python source (current setup)

**Predicted**: weak signal, delta in [0.005, 0.020] bpc at N=64-256.
Mechanism: byte-4-gram statistics overlap heavily, so the *retrieval*
channel can't preferentially weight corpus-B entries - their cosine
similarity to corpus-B query contexts is close to their similarity to
random corpus-A entries. The "irrelevant" control may even tie or
beat "relevant" because corpus-A markdown sometimes contains the same
code snippets.

### 4.2 Corpus B = JSON

**Predicted**: clear positive, delta in [0.03, 0.10] bpc at N=64,
growing to [0.10, 0.25] at N=256. Mechanism: JSON's 4-grams (`":",`,
`"},`, `[{"`) are distinctive enough that corpus-B entries have
clearly higher softmax weight when querying JSON contexts. This is
the regime where the kNN-LM mechanism cleanly operates.

### 4.3 Corpus B = hex-encoded binary

**Predicted**: very strong delta on relevant pool (>0.5 bpc at
N=256), BUT confounded by W collapse: W trained on markdown will
output near-uniform predictions for hex bytes, so even tiny correct
pool weight dominates. Mechanism: this is the "easy ICL" regime where
W has no opinion and pool has all the signal. Useful as a sanity
check that the retrieval channel functions when given a free run.

### 4.4 Sample-efficiency curve shape

For all corpus B choices, predicted shape: delta(N) ~
log(1 + N/N_half) where N_half is the half-saturation point.
- Python: N_half undefined (no slope)
- JSON: N_half ~ 100-300
- Hex: N_half ~ 4-16 (saturates fast - high mutual info per entry)

The *shape* of the curve identifies the mechanism. Linear-in-log-N
is Khandelwal/Wang kernel regression. Step function is induction-
head copy. Pure linear (no saturation) before eviction would suggest
something exotic (and probably an artifact).

## 5. Likely failure modes

### 5.1 Pool entropy collapse at small N

If 64 corpus-B entries are inserted into a 1024-pool and they happen
to share a common label byte (e.g., JSON has lots of `"`), softmax
over similarity may cause ALL queries in the corpus-B regime to
return that same byte, producing a uniform-but-wrong distribution.
Diagnostic: monitor pool-weight entropy at eval time. If
H(softmax weights) << log(POOL_SIZE), pool has collapsed.

### 5.2 BSC similarity saturation

K=4 byte 4-grams encode at most ~32 bits of byte identity. With
N=4096 and bipolar atoms, the similarity distribution between any
two random ctx vectors concentrates around 0 with sigma ~ 1/sqrt(N).
At beta=8, this means the softmax distribution is *nearly uniform*
unless similarities exceed ~3/sqrt(N) ~ 0.047. If new corpus-B
entries don't reach this similarity threshold against corpus-B
queries, retrieval is noise. Diagnostic: pre-compute the
self-similarity distribution of corpus-B chunks; mean should be
>>0.05 for the test to be meaningful.

### 5.3 FIFO eviction wipes the experiment

The `augment_pool` function uses FIFO when N + pool_used > POOL_SIZE.
At N=2048 the relevant entries get pushed out by themselves. The
"saturation" regime needs either a larger pool or sampled retention,
not FIFO. Recommendation: bump POOL_SIZE to 4096 for the N>1024
regime, or use random eviction instead of FIFO.

### 5.4 The "softmax distractor bias" inverted-U (per wave14b pool size theory)

Adding 64 entries grows effective pool size; per the
sqrt(log P) scaling, optimal beta should rise slightly. At fixed
beta=8, larger augmented pools should slightly hurt - this is a
known artifact. Anneal beta with sqrt(log(pool_used)) or report
results at the per-pool-size optimal beta.

### 5.5 ALPHA=0.3 hard cap

Already discussed in 3.3. The current threshold of 0.05 bpc is
~16% of the maximum achievable correction at ALPHA=0.3 for moderate
P_W entropy. Multi-ALPHA sweep is mandatory.

### 5.6 W-overfit to corpus A means P_W is *wrong* on corpus B

W is trained for 15 epochs on corpus A. Its output P_W on corpus-B
contexts is not just "uninformed" - it's confidently wrong. The
linear fusion ALPHA * P_retr + (1-ALPHA) * P_W then puts 70% mass
on a confidently-wrong distribution. Effect: even a perfect P_retr
can only reduce bpc by ALPHA * 0.3 * KL(P_true || P_W) bits. The
"pool_only" (ALPHA=1.0) mode bypasses this and is the cleaner
measurement.

## 6. R10 + ICL compound question

R10 (concept-fusion retrieval) and ICL-via-pool *share the pool as a
substrate but use it differently*:
- R10: uses pool entries to compute PPMI-based concept atoms over
  decomposed K-grams. The pool contributes statistical structure.
- ICL: uses pool entries as direct retrieval anchors. The pool
  contributes specific (context, label) examples.

Per the compound-falsification finding (wave14b_compound_falsification
_research.md): "mechanisms with shared evidence don't compound." Both
mechanisms read from the same 1024 entries. Two predictions:

### 6.1 At small N (corpus B in pool < 64)

R10 and ICL probably compound additively. R10's PPMI computation is
relatively insensitive to a handful of distribution-shifted entries
(64/1024 = 6%, in the noise of bigram counting). ICL's direct
retrieval IS sensitive to those entries. The mechanisms read from
overlapping but not identical features.

### 6.2 At large N (corpus B in pool > 256)

R10's PPMI computation degrades - the bigram statistics now reflect a
mixture distribution, and PPMI(byte_i, byte_j) over the mixture is
not a useful prior for either pure corpus. ICL retrieval should
continue improving. The two mechanisms substitute.

### 6.3 Recommended compound test

Single experiment: pool augmented with N=256 corpus-B entries, run
{R10-off, R10-on} x {ALPHA=0.3, ALPHA=1.0} at K in {4, 16}. If R10
loses its +0.628 gain when the pool is contaminated, we have a
substrate-level "concepts" mechanism that's brittle to ICL-style
augmentation - a finding interesting in itself.

**Prediction**: R10 contribution shrinks from +0.628 to +0.2-0.4 at
N=256 contamination; ICL contribution adds +0.05-0.15 on top; the
sum (~+0.4-0.6) is LESS than baseline R10 alone. The pool can do one
job well or two jobs poorly. This is a *useful* substrate finding -
it tells us pool architecture (concept-level vs example-level) is a
choice, not a free compose.

## 7. Brain mapping

### 7.1 Hippocampus-cortex complementary learning systems

McClelland-McNaughton-O'Reilly 1995 (CLS): hippocampus stores rapidly-
encoded episodes; cortex consolidates statistical regularities slowly.
Novel experiences are first indexed in hippocampus and retrieved
alongside cortical priors during recall.

**Mapping**:
- W = neocortex: slowly-trained (15 epochs delta rule), stores
  statistical regularities of corpus A. Hard to update on a single
  exposure to corpus B.
- pool = hippocampus (specifically CA3 + CA1 pattern separation /
  completion): rapidly-indexed via FIFO insertion, content-addressed
  via softmax similarity, mixes with cortical readout via ALPHA.
- corpus-B augmentation at query time = experience replay from
  recent episodes during recall. Schapiro 2017 (arXiv:1703.02256)
  shows hippocampus indexes statistical structure too, not just
  episodes - which matches our finding that pool retrieval contributes
  beyond pure episodic memory.

### 7.2 The specific mechanism for ICL-via-pool

Schapiro et al. 2017 "Complementary learning systems within the
hippocampus" (and the 2016 Hippocampus paper) show:
- monosynaptic pathway (DG -> CA1 direct) = fast pattern completion
  on familiar episodes
- trisynaptic pathway (DG -> CA3 -> CA1) = pattern separation +
  episode-specific recall

Our softmax-over-similarity is closest to CA3's auto-associative
recall: the query pattern partially activates many stored patterns,
softmax sharpens to the most similar, output is weighted mixture.
The "irrelevant vs relevant" experiment is testing whether CA3-like
recall is selectivity-driven (relevant entries win) or just
capacity-driven (any extra entries help).

### 7.3 Predictions from biology

If the substrate is doing CA3-like content-addressed completion:
- delta(relevant) > delta(irrelevant): YES (pattern completion is
  content-selective)
- Effect grows with similarity of new entries to query: YES
- Effect saturates when storage fills: YES (interference grows)
- Effect can REVERSE when storage overflows beyond capacity: YES
  (catastrophic interference, what hippocampal lesion + overload
  experiments show)

The Schapiro framing predicts the inverted-U we observed in pool size
theory (wave14b_pool_size_theory.md) as a feature, not a bug:
hippocampal capacity is real, and the inverted-U at P=4096 may be
the substrate's analog of CA3's ~10^4-10^5 storage capacity (Treves &
Rolls 1992 estimate).

### 7.4 The mapping AS contribution

Don't ask "is the pool brain-like." Ask: "what does softmax-over-
stored-keys compute, and when does that match what hippocampus
appears to compute?" The mathematical answer is: kernel-weighted
mixture inference over a finite set of (key, value) pairs, with the
softmax temperature controlling pattern-separation-vs-completion
tradeoff. The biological match is non-coincidental: both systems
need fast indexing + content-addressed retrieval. *That* is the
finding - the substrate is implementing a real, well-defined
computation that biology also implements.

## 8. Sources

- [Xie et al. 2021 - An Explanation of In-Context Learning as Implicit Bayesian Inference - arXiv:2111.02080](https://arxiv.org/abs/2111.02080)
- [Olsson et al. 2022 - In-Context Learning and Induction Heads - arXiv:2209.11895](https://arxiv.org/abs/2209.11895)
- [Akyurek et al. 2022 - What Learning Algorithm Is In-Context Learning? - arXiv:2211.15661](https://arxiv.org/abs/2211.15661)
- [Garg et al. 2022 - What Can Transformers Learn In-Context? A Case Study of Simple Function Classes - arXiv:2208.01066](https://arxiv.org/abs/2208.01066)
- [Wang et al. 2022 - Towards Understanding Chain-of-Thought Prompting via Latent-Variable Inference - arXiv:2212.10375](https://arxiv.org/abs/2212.10375)
- [Khandelwal et al. 2020 - Generalization through Memorization: Nearest Neighbor Language Models - arXiv:1911.00172](https://arxiv.org/abs/1911.00172)
- [Tsai et al. 2019 - Transformer Dissection: An Unified Understanding for Transformer's Attention via the Lens of Kernel - arXiv:1908.11775](https://arxiv.org/abs/1908.11775)
- [Schapiro et al. 2017 - Complementary learning systems within the hippocampus - arXiv:1703.02256](https://arxiv.org/abs/1703.02256)
- [McClelland McNaughton O'Reilly 1995 - Why there are complementary learning systems - Psych Review (no arxiv)](https://psycnet.apa.org/record/1995-42327-001)
- [Treves & Rolls 1992 - Computational constraints suggest the need for two distinct input systems to the hippocampal CA3 network - Hippocampus](https://onlinelibrary.wiley.com/doi/10.1002/hipo.450020209)
- [Velickovic et al. 2024 - Softmax is Not Enough for Sharp Size Generalisation - arXiv:2410.01104](https://arxiv.org/abs/2410.01104)

Cross-references in our notes:
- [wave14b_pool_size_theory.md](wave14b_pool_size_theory.md) - inverted-U + sqrt(log P) beta scaling
- [wave14b_r10_deep_dive.md](wave14b_r10_deep_dive.md) - R10 mechanism candidates
- [wave14b_compound_falsification_research.md](wave14b_compound_falsification_research.md) - shared-evidence compounding
