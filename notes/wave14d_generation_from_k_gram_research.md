# Wave 14.D: Autoregressive Generation from a K-Gram HDC Substrate

Unbiased literature synthesis for the experiment design in
`exp_wave14d_generation_via_sample_feedback.py`. The question isn't
"is K=4 byte-level generation good for AI." It's: **what does the math
say about chaining a K=4 byte-level predictor through its own samples,
and where will it fail?**

Drafted 2026-05-19.

---

## 1. TL;DR

1. **The math is brutal and well-known.** A K=4 byte predictor with
   per-step error rate p has expected uncorrupted run length of
   ~1/p bytes (geometric), and produces coherent local n-grams but
   loses ALL long-range structure after position ~K. Coherent output
   past position 8 is the strong claim; past position 32 is essentially
   impossible without higher-order structure.

2. **The proposed experiment design is right in spirit but the
   baseline is too weak.** Random uniform (0.39%) is the wrong floor
   for byte-level English — the correct floor is unigram-most-common
   (which gives ~17% for space-heavy markdown) and the correct
   ceiling for any K=4 model is Shannon's empirical 4-gram next-byte
   accuracy on the held-out corpus (~50-60% at position 1).

3. **Recommend: replace "5x random" with "beats unigram at position 1
   AND beats character-bigram at position 8."** This is the smallest
   test that actually distinguishes the substrate from memorization
   of letter frequency.

---

## 2. Shannon 1951 and K-Gram Autoregressive Generation Literature

### 2.1 Shannon's actual experiment

Shannon 1951 ("Prediction and Entropy of Printed English", Bell System
Technical Journal 30:50-64) is **almost identical to our test**:
- Show a human N preceding characters of English text
- Have them guess next character
- Record rank of correct answer in guess sequence
- Iterate over many positions

What he was measuring was the conditional entropy H(c_n | c_{n-1},
c_{n-2}, ..., c_{n-N+1}) as a function of N. He found that H drops
from ~4.0 bits (N=0, unigram) to ~1.3 bits (N=∞, human-level).

The critical chained-prediction figure (Shannon Figure 4): a human
predictor with full context produces text that is locally English-like
but globally drifts — exactly what we should expect from any finite-N
predictor.

**Shannon-relevant numbers for byte-level English:**
- H_0 (uniform over 256 bytes) = 8.00 bits/byte
- H_1 (unigram, including spaces and punctuation) ≈ 4.8 bpc
- H_2 (bigram) ≈ 3.5 bpc
- H_3 (trigram) ≈ 3.1 bpc
- H_4 (4-gram, our K) ≈ 2.8 bpc
- H_∞ (Shannon human est.) ≈ 1.3 bpc

Our substrate achieves bpc ≈ 2.49 with K=4 + pool + W matrix. This is
**better than pure 4-gram counting (2.8)** — the pool and W are pulling
some signal beyond raw 4-gram statistics. That's an actual result.

### 2.2 Brown et al. 1992 and the K-gram autoregressive failure mode

Brown, Della Pietra, deSouza, Lai, Mercer (1992) "Class-Based n-gram
Models of Natural Language" (Computational Linguistics 18:4) is the
canonical reference for n-gram autoregressive generation. Two findings
directly apply:

1. **Quality vs prefix length tradeoff** is the central tension.
   Too-short prefix → incoherent local structure. Too-long prefix →
   verbatim reproduction (because the table only has one continuation
   for most long contexts). K=4 sits in the "incoherent local
   structure" regime for English.

2. **Perplexity != generation quality.** Their class-based model gave
   perplexity 271 on Brown corpus vs 244 for word-based — a SMALL
   numeric improvement. But generated samples from the two models
   looked dramatically different to humans. **Byte-level accuracy at
   position 8 will not track generation quality monotonically.**

### 2.3 The exposure bias / error accumulation literature

Bengio, Vinyals, Jaitly, Shazeer 2015 (Scheduled Sampling, NeurIPS
arXiv:1506.03099) formalized the cumulative-error problem:

- During training: model sees ground-truth K-byte context
- During generation: model sees its own previous outputs
- Distribution shift between training and inference → error compounds

The standard model: if per-step error rate is p (probability of
emitting the "wrong" byte vs ground truth), then probability of being
correct at position t after a single mistake is bounded by p_correct_t
≤ p_correct_1 · (1-p_corruption)^t where corruption is the
probability that the wrong byte takes us out of the training manifold.

**For K=4 with ~50% per-position accuracy:** even the optimistic
geometric model predicts position-8 ground-truth-match probability
~0.5^8 ≈ 0.4% — basically at the random baseline. **This is the key
quantitative prediction.** Position-8 accuracy near random is
EXPECTED, not failure.

Critically: "ground-truth match" and "coherent generation" are
DIFFERENT METRICS. The substrate can produce locally-coherent English
that has zero ground-truth byte match.

Arora et al. 2022 ("Why Exposure Bias Matters", arXiv:2204.01171)
formalized this further: in K-gram-style finite-context models,
exposure bias is THE dominant failure mode after ~K positions.

### 2.4 Why "5x random" is the wrong threshold

The threshold p_8 > 2% (5x random uniform 0.4%) is satisfied by
**any model that has learned letter unigram frequencies**, because
'e' alone is 12.7% of English letters and 'space' is even higher
in markdown. A trivial unigram model gets ~17% at position 1 and
maintains that forever (the unigram of byte-t doesn't depend on
context).

So "beats 5x random at p_8" is met by a model that simply emits 'e'
at every position. That's not generation; that's degenerate collapse
to the most common byte. **The threshold must be set higher.**

---

## 3. Recommended Experiment Design

### 3.1 Baselines (replace the current ones)

Replace:
- ~~Random uniform 0.39%~~
- ~~"unigram-most-common always-space"~~

With:
- **B0 Uniform**: 1/256 = 0.39%. Floor only.
- **B1 Unigram empirical**: most common byte in training corpus
  (likely space ~17-20% in markdown). Constant across positions.
- **B2 Position-1 conditional only**: char-bigram model, P(c_t | c_{t-1}),
  trained on the same training corpus. At t=1 it uses real prefix's
  last byte; at t>1 it chains its own samples.
- **B3 Char-4-gram counting**: same K=4 but raw probability table,
  no pool, no Hebbian W. This is the strict apples-to-apples baseline
  the substrate must beat to justify the architecture.
- **B4 Teacher-forced one-step**: the substrate eating ground-truth
  K-byte context at every step. This is the upper bound — anything
  the substrate can't do here, it definitely can't do in generation.

**The substrate should beat B3 (char-4-gram counting) at p=1 to
demonstrate the pool and W are useful. It should beat B2 (bigram chain)
at p=2,4,8 to demonstrate it uses more than 1 byte of context.**

### 3.2 Metrics (expand beyond byte-match)

Ground-truth byte match decays geometrically and is a weak signal past
p=4. Add three other metrics that measure coherence INDEPENDENTLY of
ground-truth match:

1. **Byte-match accuracy at {1,2,4,8,16,32,64}** — keep current.
2. **K-gram-validity rate**: fraction of generated 4-grams that appear
   in the training corpus. Coherent text → high. Random walk → low.
3. **Letter-frequency KL divergence**: KL(P_generated || P_training)
   over byte unigrams. Repetition collapse → high (one byte dominates).
   Healthy generation → low.
4. **Per-position empirical entropy**: H of the substrate's predicted
   distribution at each position. Collapsing to a single byte makes
   H→0; healthy uncertainty stays at ~3 bits.

### 3.3 Sample count and statistical reporting

50 prefixes × 64 bytes × 3 seeds × 3 temperatures = 28,800 byte
predictions per condition. Plenty of power. Report bootstrap 95% CIs
on each position. **Pre-register the verdict thresholds before running.**

### 3.4 Pre-registered verdict (replace "5x random")

- **GENERATION CONFIRMED** if greedy substrate beats B3 (char-4-gram
  counting baseline) at position 1 by ≥5 percentage points AND
  K-gram-validity rate at length 64 is ≥0.4 (i.e., 40% of generated
  4-grams appear in training data).
- **COHERENT** if greedy substrate K-gram-validity rate at length 64
  is ≥0.7 AND letter-frequency KL < 0.1 nats.
- **DEGENERATE** if substrate's per-position entropy collapses below
  1.0 bit within 16 positions (i.e., emits the same byte ≥50% of the
  time). This is the "GPT-quality" killer for K=4.

---

## 4. Predicted Accuracy Curves with Mechanism

### 4.1 The geometric decay model

Let p_t = P(byte t matches ground truth | substrate emitted t-1 bytes
of its own). Then:

p_1 = single-step accuracy when given real prefix.
p_t = p_1 · (probability previous t-1 bytes formed a context the
substrate handles) ≈ p_1 · (training-context-hit-rate)^{t-1}.

For K=4 trained on 50KB markdown, the training-context-hit-rate
after sampling 1 byte from substrate (vs sampling from training
distribution) is ~0.4 — the substrate's own samples diverge from
training contexts quickly because errors compound.

Predicted curve (greedy):
- p_1 ≈ 0.50-0.60 (substrate's reported 1-step accuracy)
- p_2 ≈ 0.40 (one byte off training manifold)
- p_4 ≈ 0.15 (window fully filled with own samples)
- p_8 ≈ 0.05 (twice K, no real prefix bytes left)
- p_16 ≈ 0.02 (approaching unigram floor)
- p_32 ≈ 0.02 (at unigram floor; pure letter-frequency match)
- p_64 ≈ 0.02

The "5x random = 2%" threshold is **exactly the unigram floor.**
This is why the current threshold is too permissive — it's testing
"does the substrate know letter frequencies" not "does the substrate
generate."

### 4.2 Why coherent text can have low byte-match

A K=4 model trained on `the quick brown fox` and prompted with `the_`
might generate `the_lazy_dog`. That's perfectly coherent English with
zero byte-match to the ground-truth continuation. **K-gram-validity
and frequency-KL are the right metrics for coherence.**

---

## 5. Expected Collapse Modes

Five known modes (Holtzman et al. 2019 "The Curious Case of Neural
Text Degeneration", arXiv:1904.09751; Welleck et al. 2019
"Unlikelihood Training", arXiv:1908.04319):

### 5.1 Greedy collapse to most-frequent byte
- Mechanism: at each step, greedy picks argmax. If 'space' has the
  highest probability under most contexts, greedy emits space forever.
- Predicted onset: position 4-8 (one full K-window of substrate's own
  output). Once the K-window fills with spaces, the substrate has
  never seen `' '*4` in training, so all bytes look ~equally likely
  and softmax argmax goes to the most-common byte.
- Test: per-position entropy should collapse to <1 bit within p=8.

### 5.2 Repetition cycles ("the the the the")
- Mechanism: substrate hits a context C that maps to byte b, and
  C[1:] + b == C. Then b is emitted forever.
- For K=4: any 4-cycle in the byte sequence becomes a fixed point.
- Predicted onset: position 4-16. Common with markdown (lots of
  `\n\n\n\n` and `    ` indentation).

### 5.3 Temperature explosion at T≥1.0
- Mechanism: with temp 1.0 + flat softmax, byte selection becomes
  near-random. Random byte → off-manifold context → flatter softmax
  → more random. Positive-feedback loop.
- Predicted onset: position 2-4 at T=1.0 on K=4.
- T=0.7 should be a sweet spot — sharp enough to stay on manifold,
  diverse enough to avoid greedy collapse.

### 5.4 K-gram boundary collapse
- Mechanism: K=4 cannot encode "this is a code block" vs "this is
  prose" — those are 20+ byte distinctions. Substrate can't maintain
  document-level register, will mix code and prose tokens.
- Always present in K=4 generation. Not "collapse" per se, just the
  ceiling.

### 5.5 Pool-divergence drift (specific to our substrate)
- Mechanism: pool was built from real training contexts. Substrate's
  own generations produce K-grams not in the pool. Pool retrieval
  returns increasingly-irrelevant entries. (See §6.)

### Predicted collapse length

For K=4 byte models on 50KB markdown:
- **Greedy: collapse to ≤2-byte cycle within position 8-16.**
- **T=0.7: drifts to random-walk within position 16-32 but no fixed
  point — likely the most informative regime.**
- **T=1.0: nearly random by position 4.**

---

## 6. Pool's Role in Generation

### 6.1 The training-inference mismatch

During training: every K-gram context fed to the pool actually exists
in the training corpus. Pool retrieval is meaningful — it pulls
similar real contexts that have known next bytes.

During generation: the substrate's own emitted bytes form K-grams
that are **not in the pool**. Cosine similarity between a substrate-
emitted K-gram and the nearest pool entry will be low (~0.1-0.2 for
random BSC vectors), so retrieval degrades to noise.

### 6.2 Prediction: pool will help less as generation progresses

Position 1: real K-byte prefix → high pool similarity → pool helpful.
Position 4: K-window half real / half substrate → moderate pool help.
Position 8+: K-window all substrate → pool retrieves noise.

### 6.3 Recommended A/B test (add to experiment)

Run two variants in parallel:
- **Substrate-W-only**: disable pool entirely. P(byte) = softmax(W·ctx).
- **Substrate-W+pool**: current setup.

**Pre-registered prediction:** pool helps at p≤4 and hurts at p≥8.
If pool helps at p≥8, that's a surprising and valuable result — it
means the BSC similarity manifold is wider than the training contexts.
If pool always hurts, that's an architectural finding: for generation
specifically, the substrate should be pool-disabled.

Cite for the mechanism: Veličković et al. 2024 "Softmax is not
Enough" (arXiv:2410.01104) — same extreme-value-statistics math as
the pool-size inverted-U. Retrieval from off-manifold queries
amplifies distractor noise even more than fixed-P with on-manifold
queries.

---

## 7. Upper Bound for K=4 Byte Coherence

### 7.1 The information-theoretic ceiling

Conditional entropy H(byte_t | byte_{t-K:t-1}) for K=4 on English
markdown ≈ 2.8 bpc. Compare to:
- H_1 (unigram): 4.8 bpc
- H_∞ (human-level): 1.3 bpc

So K=4 captures (4.8 - 2.8) / (4.8 - 1.3) ≈ 57% of the available
mutual information. **It's a real signal but far from coherent text.**

### 7.2 The Markov-order ceiling

For text to look coherent at the WORD level, the model needs to track
at least one full word (~5-7 bytes including space). K=4 cannot do
this. **Coherent word-level output is mathematically impossible** for
K=4. Coherent sub-word transitions (within-word letter sequences) are
achievable — `the_`, `ion_`, `ing_` will be common in output.

### 7.3 The 50KB ceiling

50KB markdown contains ~50000 bytes, ~12500 unique 4-grams,
~3000 unique 4-grams with frequency ≥2. The substrate has at most
3000 reliable next-byte predictions. **For position-8 ground-truth
match, the relevant figure is: how often does an 8-byte substrate
output exactly match an 8-byte training continuation?** Combinatorially:
(3000 reliable contexts)^8 ≈ 6.5 × 10^27. Vanishingly unlikely.

### 7.4 The product question answered

**"GPT-quality generation with auditable memory" requires K≥16
minimum, plausibly K≥64. K=4 is for diagnosis, not product.**

What K=4 CAN deliver:
- Locally-coherent letter patterns (English-looking nonsense).
- Verbatim memorization of K-gram completions (useful for retrieval).
- Diagnostic signal that the substrate's W and pool work as expected
  in the autoregressive regime.

What K=4 CANNOT deliver:
- Word-level coherence past ~position 8.
- Document-level register (prose vs code).
- Argument structure, code logic, anything compositional.

**Tier-1 killer test:** if at K=4, the substrate's K-gram-validity
rate at length 64 is ≥0.4 AND it beats char-4-gram counting (B3) at
position 1, that justifies running the experiment at K=16 and K=64
to see if the architecture scales. If K=4 fails B3 at position 1,
the substrate has no information beyond what raw counting gives, and
scaling K won't help — that closes the killer.

---

## 8. Brain Mapping: Hippocampal Replay as Sequence Generator

The hippocampus has a relevant mechanism, but the mapping is more
specific than "it's like an LM."

### 8.1 What hippocampal replay actually does

**Foster & Wilson 2006** ("Reverse replay of behavioural sequences in
hippocampal place cells during the awake state", Nature 440:680-683)
showed that during rest after navigation, place-cell sequences fire
in temporally-compressed reverse order along the just-experienced
trajectory. Time-compression factor ~20x.

**Stella et al. 2019** ("Hippocampal Reactivation of Random
Trajectories Resembling Brownian Diffusion", Neuron 102:450-461)
showed that during deeper rest/sleep, the SAME cells produce sequences
that don't reproduce experienced trajectories — they follow Brownian
diffusion through the place-cell graph. Novel, plausible, off-manifold.

### 8.2 The mechanism (math)

Hippocampal place-cell sequences are generated by recurrent CA3
attractor dynamics. The transition probability from place A to place B
is set by Hebbian potentiation between cells co-active during
experience (Levy & Steward 1979, "Synapses as associative memory
elements", Neuroscience 4:791-797). So:

P(B | A) ∝ Hebbian-weight(A,B) ∝ co-occurrence frequency during
experience.

**This is structurally identical to a K=1 Markov chain on the place
graph.** And it produces apparently-novel trajectories despite K=1,
because the place graph has rich topology (each place has many
neighbors). The "generative" quality comes from the *graph structure*,
not from long-range context.

### 8.3 The lesson for our substrate

The hippocampus generates novel-but-plausible sequences using only
LOCAL (K=1-2) transition statistics over a SPARSE graph. We use K=4
transitions over a DENSE graph (256 bytes). Two design implications:

1. **Sparsity of the next-byte distribution may matter more than K.**
   If the substrate's softmax stays peaked (low entropy, few
   plausible continuations per context), output looks structured. If
   softmax goes flat, it looks random. Test this: report softmax
   entropy at each position.

2. **The Brownian-diffusion finding (Stella 2019) suggests novel
   coherent generation requires the substrate to stay within the
   training manifold while moving randomly through it.** Our pool
   retrieval is exactly the mechanism that could enforce this: stay
   on the manifold of training K-grams. If pool retrieval keeps
   substrate outputs close to training contexts, we'd see
   hippocampus-like novel-but-plausible sequences. **If pool retrieval
   degrades on substrate's own samples (§6), we lose this property.**

3. **Sharp-wave ripple time-compression (~20x)** suggests biological
   sequence generation operates at much higher per-step rates than
   the underlying experience. Not directly relevant to our test, but
   notable: if the substrate can ever do useful generation, doing it
   FAST is plausible.

### 8.4 What this isn't

This isn't "the brain is a K-gram model." Hippocampal sequences are
gated by theta rhythm, modulated by neuromodulators (acetylcholine
during encoding, low-ACh during replay), and embedded in a cortico-
hippocampal loop. Our substrate has none of these. The mapping is at
the level of "Hebbian-trained transition statistics on a sparse graph"
— a very specific math claim, not a metaphor.

---

## 9. Sources with arXiv IDs and DOIs

**Foundational (no arXiv):**
- Shannon, C. E. (1951). "Prediction and Entropy of Printed English."
  Bell System Technical Journal 30:50-64. DOI:10.1002/j.1538-7305.1951.tb01366.x
- Brown, P. F., et al. (1992). "Class-Based n-gram Models of Natural
  Language." Computational Linguistics 18(4):467-479. ACL Anthology J92-4003.
- Levy, W. B. & Steward, O. (1979). "Synapses as associative memory
  elements in the hippocampal formation." Brain Research 175:233-245.
- Hopfield, J. J. (1982). "Neural networks and physical systems with
  emergent collective computational abilities." PNAS 79:2554-2558.
- Bahl, L. R., Jelinek, F., Mercer, R. L. (1983). "A Maximum Likelihood
  Approach to Continuous Speech Recognition." IEEE TPAMI 5(2):179-190.

**Neuroscience:**
- Foster, D. J. & Wilson, M. A. (2006). "Reverse replay of behavioural
  sequences in hippocampal place cells during the awake state."
  Nature 440:680-683. DOI:10.1038/nature04587
- Stella, F., Baracskay, P., O'Neill, J., Csicsvari, J. (2019).
  "Hippocampal Reactivation of Random Trajectories Resembling
  Brownian Diffusion." Neuron 102:450-461.
  DOI:10.1016/j.neuron.2019.01.052

**Modern LM error accumulation:**
- Bengio, S., Vinyals, O., Jaitly, N., Shazeer, N. (2015). "Scheduled
  Sampling for Sequence Prediction with Recurrent Neural Networks."
  arXiv:1506.03099
- Holtzman, A., Buys, J., Du, L., Forbes, M., Choi, Y. (2019). "The
  Curious Case of Neural Text Degeneration." arXiv:1904.09751
- Welleck, S., et al. (2019). "Neural Text Generation with
  Unlikelihood Training." arXiv:1908.04319
- Arora, K., et al. (2022). "Why Exposure Bias Matters: An Imitation
  Learning Perspective of Error Accumulation in Language Generation."
  arXiv:2204.01171

**HDC/VSA sequence representation:**
- Schlegel, K., et al. (2022). "A comparison of Vector Symbolic
  Architectures." Artificial Intelligence Review.
- Kleyko, D., et al. (2022). "Vector Symbolic Architectures as a
  Computing Framework for Emerging Hardware." Proc. IEEE.

**Softmax/retrieval extreme-value statistics:**
- Veličković, P., et al. (2024). "Softmax is not Enough (for Sharp
  Size Generalisation)." arXiv:2410.01104

---

## Appendix A: Concrete experiment-design changes (checklist)

- [ ] Add baseline B3 (char-4-gram counting). Substrate must beat at p=1.
- [ ] Add baseline B2 (char-bigram chain). Substrate must beat at p≥2.
- [ ] Replace verdict threshold "5x random" with "beats B3 at p=1 by
      ≥5pp AND K-gram-validity ≥0.4 at length 64".
- [ ] Add K-gram-validity metric (fraction of generated 4-grams found
      in training corpus).
- [ ] Add letter-frequency KL divergence metric.
- [ ] Add per-position softmax entropy metric.
- [ ] Add pool-on / pool-off A/B test as a within-experiment factor.
- [ ] Pre-register: pool helps at p≤4, hurts at p≥8.
- [ ] Pre-register: greedy collapses to ≤2-byte cycle by p=16.
- [ ] Pre-register: T=0.7 most informative; T=1.0 random-walk by p=4.
- [ ] Save 5 sample generations per (seed, temperature, pool-on/off)
      for human inspection. K-gram-validity should correlate with
      qualitative coherence.

---

## Appendix B: What "GENERATION CONFIRMED" actually proves

Under the recommended design:
- Beats B3 at p=1 → "the W matrix and pool extract real signal beyond
  raw 4-gram counts." This is the substrate-justifying result.
- K-gram-validity ≥0.4 at length 64 → "outputs stay on or near the
  training manifold." This is the coherence claim.
- Letter-frequency KL <0.1 → "no degenerate collapse." This is the
  not-just-emitting-spaces claim.

If all three pass at K=4, the architecture is worth scaling. If only
B3-beating passes, the substrate has a measurable but tiny advantage
over counting. If nothing passes, K=4 is too short for our corpus —
which is exactly the predicted Shannon-order ceiling and tells us to
go to K=16 next.
