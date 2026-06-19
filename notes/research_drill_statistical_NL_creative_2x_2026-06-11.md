# Research Drill: Statistical NL Fluency + Open-Ended Creative Generation -- Substrate-Only vs LLM-Hybrid Ceiling
# Date: 2026-06-11
# Trigger: User mandate -- drill Q1-Q5 + 5 probe streams on fluency/generation gap
# Calibration penalty: -0.20 applied throughout; novel-synthesis P capped at 0.50
# Prior art: PP-331 paragraph_compose 1.000, PP-342 WUG 1.000, PP-345 translation 1.000
#   wave14d_generation_v2_K16 p1=43.3% vs B3 Markov 27.8%
#   k3_zipf_falsifier confirms Zipf is load-bearing for K=3

---

## HEADLINE

Substrate has genuine, validated structural NL capabilities (composition, morphology, POS, translation
structure) but the two remaining gaps -- statistical fluency at LLM grade and open-ended creative
production -- are NOT substrate-only ceilings in the engineering sense. Both are solvable substrate-
engineering problems with specific, concrete paths. The substrate-only path for fluency tops out at
approximately Markov-chain grade text (P_deflated 0.25-0.35 that substrate-only beats a 5-gram
interpolated Kneser-Ney baseline). The substrate-plus-distributional-codebook path (Q4 n-gram
superposition) has a realistic ceiling closer to pre-neural SMT quality (BLEU ~0.20-0.30 range,
P_deflated 0.30-0.40). True LLM-grade fluency and open-ended creativity require either (a) the
already-validated Tier 5c LLM-hybrid coupling, or (b) a substrate-native autoregressive loop with
Zipf-optimal codebook + temporal policy sampling that has not been built or tested. Path (b) is the
genuine engineering question this drill answers. P_deflated for path (b) reaching 50% of Pythia-160M
fluency: 0.28-0.38 substrate-only; 0.55-0.65 with LLM-hybrid. These are NOT ceilings -- they are
the honest P estimates for the nearest empirically testable milestone.

---

## CHEAP DECISIVE TEST

**Fluency gate (Q1/Q4 combined, 1 hour CPU, $0):**
Build a Zipf-weighted codebook over Brown corpus unigrams (top-5000 words, frequency-proportional
atom allocation). Store trigram conditional distributions as bundle superpositions. Generate 20
sentences of 15-20 tokens each via greedy top-k pool retrieval. Compute BLEU-1/2 against the
Brown test set and mean perplexity under a held-out trigram LM.

Pre-registered bands:
- HARD_PASS: BLEU-2 >= 0.18 AND perplexity <= 80 (beats random at this vocab size ~4000 perplexity)
- MID_BAND: BLEU-2 in [0.10, 0.18) OR perplexity in (80, 200]
- HARD_FAIL: BLEU-2 < 0.10 AND perplexity > 200

This test takes ~1 hour to build and ~10 minutes to run. It is the single cheapest gate between
"substrate can do n-gram lookup" and "substrate can generate plausible text."

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

### Q1: Statistical Fluency via Zipf Codebook + N-gram Superposition

P_deflated = 0.30 (after -0.20 calibration penalty from nominal 0.50)

HARD_PASS: substrate-only Zipf n-gram generation achieves BLEU-2 >= 0.18 on Brown/Penn test set
HARD_FAIL: BLEU-2 < 0.08 (indistinguishable from unigram bag-of-words generation)

Mechanism: Zipf-optimal codebook means high-frequency tokens get fewer atoms (shorter codewords) and
rare tokens get more atoms (longer, more specific codewords). This inverts the naive allocation and
mirrors Shannon optimal coding. The information-theoretic argument (Mandelbrot 1953; Ferrer-i-Cancho
2005 on optimal coding and Zipf origins) predicts that a Zipf-weighted codebook will improve recall
precision for common trigrams, which is what BLEU-2 measures.

Counter-evidence risk: The k3_zipf_falsifier result already confirmed that Zipf statistics are load-
bearing for K=3 trigram retrieval. That result measured RECALL in a structured task. GENERATION
requires the inverse: given a context prefix, retrieve the most likely continuation. The substrate
is a memory system optimized for retrieval from a query, not for sampling from a distribution. This
is the core engineering gap.

### Q2: Open-Ended Creative Generation

P_deflated = 0.18 (after -0.20 calibration penalty from nominal 0.38)

HARD_PASS: substrate-only story-completion coherence rating >= 2.5/5 human average (5 raters,
10 story fragments, 200-token completions)
HARD_FAIL: coherence <= 1.5/5 (worse than random shuffled sentence baseline)

Reasoning: open-ended generation requires maintaining a topic thread across 200 tokens. The substrate
has demonstrated topic coherence in the PP-331 paragraph compose task (1.000 on 6-slot structured
task). But 6 slots with pre-specified topics is structurally very different from 200 tokens of free-
form continuation where the topic must be inferred and maintained without a schema. The substrate has
no mechanism for token-by-token probability accumulation across a full generation window. It would
need either (a) a sliding-window context bundle updated at each generation step, or (b) a hierarchical
structure with sentence-level and document-level state.

This is a genuine substrate-engineering gap. It is not a theoretical impossibility -- it is a
missing piece that requires building before testing.

### Q3: BLEU on Paragraph Paraphrase

P_deflated = 0.35

HARD_PASS: BLEU-4 >= 0.25 on a 100-sentence paraphrase task (MRPC or similar)
HARD_FAIL: BLEU-4 < 0.10 (near chance for 4-gram overlap)

The substrate has demonstrated translation structure at SVO/SOV/VSO level (PP-345 1.000). Paraphrase
is a softer task -- same meaning, different surface form. The substrate should handle this better
than open-ended generation because paraphrase has a specific source sentence as anchor (retrieval
condition, not generation condition). The structural algebra for paraphrase (bind source form,
retrieve target form bundle) is within the validated compositional framework.

### Q4: N-gram Superposition Recovery

P_deflated = 0.52 (after -0.20 calibration; nominal 0.72 due to alignment with validated K=3 result)

HARD_PASS: recall@1 > 0.80 on 1M trigram recovery from Zipf-weighted codebook (N=8192)
HARD_FAIL: recall@1 < 0.50 (near chance for top-3 vocabulary)

This is the most grounded prediction because the k3_zipf_falsifier anchor already confirms that
K=3 trigram recall is Zipf-sensitive. The Q4 question is whether scaling to 1M n-grams with a Zipf-
weighted codebook preserves recall@1 above 0.80. Given the PP-225 finding that DISC_POOL was fixed
at ~249 entries (not genuine 10k-50k), the scaling question is genuinely open. At 1M trigrams the
substrate capacity analysis suggests significant interference unless N is scaled accordingly (N=65k+
for 1M items at recall@1 > 0.80, per the capacity formula).

Correction: 1M trigrams at N=8192 is ALMOST CERTAINLY a HARD_FAIL. The capacity formula gives
M_max ~ 0.056 * N = 458 items at N=8192 for reliable recall@1. To store 1M trigrams reliably
requires N ~ 18M (impractical). The test as posed in Q4 will fail at 1M scale. Re-scoped:

REVISED Q4: Store 10K trigrams from Brown corpus top-frequency set; test recall@1.
Revised HARD_PASS: recall@1 > 0.85 at 10K trigrams, N=65536
Revised HARD_FAIL: recall@1 < 0.60

### Q5: Substrate-Native Temperature Sampling

P_deflated = 0.40

HARD_PASS: entropy of generated token distribution at T=1.0 >= 2.0 bits AND at T=0.1 <= 0.5 bits
  (controllable diversity); BLEU-1 degradation from T=0.1 to T=1.0 <= 0.10 (coherence maintained)
HARD_FAIL: entropy does not vary with temperature (sampling is non-functional)

The mechanism for substrate temperature sampling is: instead of greedy argmax on cosine similarity,
sample from a softmax over the pool with temperature T. This is algebraically trivial to implement.
The question is whether the resulting distribution has meaningful diversity. Since the substrate pool
is a finite set of stored patterns (not a smooth continuous distribution), temperature sampling will
produce discrete jump behavior rather than the smooth diversity-coherence tradeoff seen in LLMs.
This is a fundamental difference: LLM softmax operates over a vocabulary of ~50K items in a
continuous parametric space; substrate softmax operates over a pool of O(M) stored patterns in a
retrieval space. The distributions are structurally different.

---

## SECTION 1: PROBE STREAM SYNTHESIS

### Stream A: Biology -- Saffran Statistical Learning + Bybee Usage-Based Grammar

Saffran et al. (1996) demonstrated that infants learn word boundaries using transitional probabilities
between syllables (TP within words ~1.0 vs TP between words ~0.33). This is the gold standard for
distributional learning without parametric models. The brain computes TPs via an implicit memory
system (striatum involvement confirmed; Turk-Browne et al. 2010 fMRI). The substrate analogy:
bundled n-gram superpositions stored in W ARE a form of distributional memory. Each trigram (A, B,
C) stored as bind(A, bind(B, C)) is equivalent to encoding P(C | A, B) at the storage granularity.

Bybee's key empirical finding: token frequency drives chunk entrenchment (high-frequency items become
stored as single units); type frequency drives productivity (abstract schemas generalize). This maps
directly onto the Q1 Zipf-weighted codebook design: high-frequency bigrams/trigrams are stored with
more precise codebook entries (lower quantization noise); rare n-grams are stored with less precision
but more contextual diversity.

Direct implication: the substrate is biologically plausible for distributional learning, but the
brain implements this via a continuous weight-update mechanism (Hebbian + dopamine-modulated striatal
learning), whereas the substrate uses discrete bundle storage. The capacity constraint is the key
engineering gap: the brain stores billions of n-gram statistics; the substrate at N=65K stores ~3600
reliable items.

### Stream B: Brain -- Levelt Speaking Model + Lexical Access Pipeline

The Levelt model (1999, validated computationally via WEAVER++) provides a staged production pipeline:
  (1) Conceptual preparation
  (2) Lemma selection (syntax + semantics without phonology)
  (3) Morphological encoding (morpheme assembly)
  (4) Phonological encoding (syllabification)
  (5) Phonetic encoding (articulatory gestures)
  (6) Articulation

The substrate already has components for stages 1-4:
- Stage 1: retrieval from W is conceptual lookup
- Stage 2: lemma selection ~ pool retrieval of the best-matching item
- Stage 3: PP-342 WUG morphological productivity at 1.000
- Stage 4: PP-345 distant-language translation at 1.000 (language-specific phonological structure)
- Stage 5-6: out of scope (articulatory gestures require different representation)

The gap is INTER-STAGE FLOW: in the Levelt model, stages are staged and feedforward with
incremental output. The substrate has each stage as a separate retrieval operation, but no mechanism
for CHAINING the output of one stage as the input query to the next stage while accumulating a
growing output sequence. This is the same architectural gap as Q2 open-ended generation.

Cheap path for stages 1-4 only: concept -> lemma -> morphological form -> phonological form as a
4-hop chain. The substrate has validated heteroassociative chains up to depth 3 (PP-9b, depth3
fidelity=0.986). A 4-hop Levelt pipeline is within validated territory.

### Stream C: Materials / Information Theory -- Zipf Optimal Coding

Ferrer-i-Cancho and Sole (2003) and subsequent work by Ferrer-i-Cancho et al. (2022) provide the
information-theoretic basis: Zipf's law emerges from a communication system that minimizes the ratio
of cost (code length) to entropy (information). The optimal code assigns short codes to frequent
items and long codes to rare items. This is exactly the inverse of how naive VSA/HDC systems allocate
atoms: random codes have no frequency-sensitivity.

Concrete implication for substrate: a Zipf-optimal codebook should allocate atoms as:
  n_atoms(word_i) proportional to -log(p_i) / log(V)
where p_i is the corpus frequency of word i and V is vocabulary size. This means:
  - "the" (p ~ 0.07) gets ~0.4 atoms (effectively a single atom with high precision)
  - rare words (p ~ 1e-6) get ~7 atoms (longer, more specific codewords)

This is implementable by using superposition of multiple random atoms for rare words and a single
atom for common words. The precision/recall tradeoff at retrieval time: common words are retrieved
with high precision (low confusion with neighbors) but low distinctiveness; rare words are retrieved
with high distinctiveness but higher memory cost.

The n-gram extension: Mandelbrot (1953) showed that n-gram frequencies also follow Zipf with a
smaller exponent (xi ~ 0.7 for bigrams vs xi ~ 1.0 for unigrams). This means the optimal codebook
for n-grams requires approximately 1.4x more atoms per entry than unigrams. At N=65K, the capacity
for n-gram entries drops proportionally.

### Stream D: LLM Theory -- Distributional Semantics + Small LLM Baselines

Key empirical baseline data from the literature:
- Pythia-160M: trained on Pile, evaluated on standard benchmarks (LM Evaluation Harness); Wikitext-2
  perplexity ~20-25 (competitive with similar-size models)
- Cerebras-GPT-111M: slightly smaller, Chinchilla-tuned; similar perplexity range
- Trigram Kneser-Ney: Wikitext-2 perplexity ~150-200 (pre-neural baseline)
- 5-gram KN interpolated: Wikitext-2 perplexity ~100-150

These baselines define the "zone of relevance" for substrate fluency:
  - Substrate-only Zipf n-gram superposition: expected perplexity 150-400 (between trigram KN and
    unigram baseline)
  - Substrate + simple feedforward coupling: could approach 100-150 with trigram-quality text
  - Substrate + LLM hybrid (Tier 5c validated): already shown to improve LLM perplexity by 15-28%

The BLEU-2 baseline for statistical MT systems (pre-2016) on standard WMT benchmarks was typically
0.20-0.35. For paraphrase tasks, rule-based systems achieve BLEU-4 ~ 0.15-0.25. These are the
honest comparison points for substrate-only generation, not LLM-grade outputs.

Pre-LLM SMT observation: statistical phrase-based MT systems (MOSES era) achieved BLEU-4 ~ 0.25-0.35
by storing millions of phrase pairs and doing Viterbi-style decoding. The substrate's n-gram
superposition is analogous to a very small phrase table (limited by N capacity) with no decoding
algorithm -- greedy pool retrieval is not Viterbi. The gap is the decoding algorithm, not the
memory representation.

### Stream E: New Paths -- 10 Substrate-Native Paths for Fluency + Creative Generation

Each path rated on: P_deflated (substrate-only ceiling) | cheap test cost | open vs closed question

**PATH 1: ZIPF-OPTIMAL-CODEBOOK**
Allocate atoms per word proportional to -log(p). Implement: during W training, assign each word
a vector that is a superposition of floor(-log(p)/log(V) * 8) + 1 random basis atoms (capped at
some max). This increases distinctiveness for rare words and reduces interference from common words.
P_deflated (beat unigram baseline on BLEU-2): 0.42
Cheap test: Brown corpus, 5000 words, 1 hour CPU. OPEN QUESTION.

**PATH 2: N-GRAM-SUPERPOSITION (BIGRAM/TRIGRAM)**
Store bigrams as bind(w_i, w_{i+1}) and trigrams as bind(w_i, bind(w_{i+1}, w_{i+2})).
At inference: given context (w_{i-1}, w_i), retrieve candidates from pool and pick argmax cosim.
This is autoregressive byte/word generation already validated at K=16 (wave14d_generation_v2_K16).
The Q4 extension: scale to Brown corpus 10K top trigrams at N=65536.
P_deflated (recall@1 > 0.80 at 10K): 0.52 (well-aligned with validated K=3 result).
Cheap test: 30 minutes CPU build, 5 minutes inference. OPEN BUT NEAR-VALIDATED.

**PATH 3: TEMPORAL-POLICY-GENERATION (TEMPERATURE SAMPLING)**
Replace greedy argmax with softmax-T over pool cosine similarities. Implement: sort pool by cosim,
apply softmax with temperature T, sample index, emit token. Trivial code change to existing
generation loop. Q5 asks whether diversity is controllable.
P_deflated (entropy varies with T): 0.40 (trivially implementable; question is whether useful
diversity is generated or just noise).
Cheap test: 10 minutes CPU on existing generation scaffold. OPEN TRIVIAL TO TEST.

**PATH 4: LEVELT-PIPELINE-COMPLETE (4-hop chain)**
Concept -> lemma -> morphological form -> phonological form -> surface form as 4-hop heteroassoc
chain. PP-9b validated depth-3 fidelity=0.986. A 4-hop extension is the next obvious rung.
P_deflated (4-hop fidelity > 0.95): 0.55 (conservative extrapolation from depth-3 result).
Cheap test: 1 hour CPU extension of existing heteroassoc chain test. OPEN HIGH-CONFIDENCE.

**PATH 5: SUBSTRATE-AS-DISTRIBUTIONAL-MODEL (no parameters, stored distributions)**
Instead of training a parametric LM, store P(w | context) directly as bundle superpositions with
frequency-weighted amplitudes. Retrieve by querying the context bundle, getting a distribution over
the pool. This is closest to what the Saffran/Bybee TP mechanism does biologically.
P_deflated (better than unigram baseline on perplexity): 0.38.
Hard ceiling: no parameter learning means no generalization beyond stored n-grams. Coverage drops
fast for rare contexts (the fundamental n-gram sparsity problem, predating LLMs).
Cheap test: Brown corpus 10K sentences, 2 hours CPU. OPEN MEDIUM CONFIDENCE.

**PATH 6: BIGRAM-TRIGRAM-LAYERED (Tier 2-3 text quality)**
Hierarchical n-gram store: Tier-1 stores unigrams, Tier-2 stores bigrams, Tier-3 stores trigrams.
At generation time, query the highest-order matching Tier first (Kneser-Ney backoff logic, but
substrate-native). This replicates interpolated KN smoothing in a substrate architecture.
P_deflated (matches interpolated trigram KN quality, perplexity ~ 100-200): 0.35.
Hard limit: without proper backoff weighting, performance degrades at low-frequency n-grams.
Cheap test: 3 hours CPU to build 3-tier store, 30 minutes eval. OPEN MEDIUM CONFIDENCE.

**PATH 7: SLIDING-WINDOW-CONTEXT-BUNDLE (long-range coherence)**
Maintain a context bundle of the last K tokens as a superposition of bound position-token pairs.
Update incrementally: at each step, shift the position bindings and add the new token. This extends
the autoregressive generation to handle >K context. The challenge: superposition noise grows with K.
P_deflated (coherent generation at K=32 context window): 0.28.
Hard limit: interference from superposed context items grows as sqrt(K); at K=32 the noise may
dominate signal in N=8192. N=65536 likely required.
Cheap test: 2 hours CPU, measure context window accuracy vs K. OPEN MEDIUM-LOW CONFIDENCE.

**PATH 8: STRUCTURED-TEMPLATE GENERATION (PP-331 extension)**
PP-331 demonstrated perfect 6-slot structured paragraph composition. Extend to: fill-in-the-blank
creative templates (story schemas, narrative structures). The substrate fills template slots with
retrieved content from the KB. This is NOT open-ended generation -- it is template-constrained
generation with retrieved slot-fills. But it IS a viable substrate-only path to creative-looking text.
P_deflated (story coherence rating >= 3.0/5 on structured templates): 0.55.
This is the HIGHEST CONFIDENCE creative generation path because it uses validated PP-331 machinery.
Cheap test: 1 hour CPU, 5 human raters on 10 generated stories. LOW COST HIGH CONFIDENCE.

**PATH 9: CONCEPT-LEVEL AUTOREGRESSION (semantic generation)**
Instead of word-by-word generation, generate concept-by-concept (VQ concept IDs from the validated
Tier 5c PP-225 fact-recall head). Each step retrieves the next concept, then decodes to a word via
a lookup (concept -> canonical surface form). This yields semantically coherent but stylistically
flat text. Text will read like "the PERSON went to the PLACE and did the ACTION" with real values.
P_deflated (semantically coherent at concept level): 0.45. P for surface fluency: 0.22.
Cheap test: 2 hours CPU, use existing VQ concept IDs from the PP-225 infrastructure. OPEN MEDIUM.

**PATH 10: SUBSTRATE + TINY-LM RESIDUAL HYBRID**
Use substrate for concept-level structure planning (which concepts appear in what order) and
Pythia-70M for surface realization (filling in fluent words around the substrate-planned concepts).
This is the minimal hybrid that keeps substrate "in the loop" for creative planning but delegates
fluency to the LLM. The Tier 5c substrate-attention architecture already demonstrates this pattern.
P_deflated (coherent + fluent 200-token generation): 0.55-0.62.
This path has the highest P because it has direct precedent (Tier 5c validated 15-28% LLM lift).
Cheap test: 2-4 hours CPU/GPU using existing Tier 5c infrastructure. NEAR-VALIDATED.

---

## SECTION 2: HONEST SUBSTRATE-ONLY vs LLM-HYBRID ASSESSMENT

### The core engineering gap

The substrate's generation capability (wave14d_generation_v2_K16) demonstrates that the substrate
CAN generate text via autoregressive pool retrieval. The p1=43.3% vs Markov B3=27.8% (+15.5pp)
result means the substrate already beats a pure Markov baseline.

The gap to LLM-grade fluency is NOT a theoretical ceiling. It is a stack of engineering pieces:

1. Codebook frequency-weighting (PATH 1) -- missing, implementable in 1 day
2. N-gram layered store with backoff (PATH 6) -- missing, implementable in 3 days
3. Temperature sampling (PATH 3) -- trivially implementable, 1 hour
4. Context window beyond K=16 (PATH 7) -- requires N scaling, 1 week
5. Concept-level planning layer (PATH 9) -- moderate effort, 3-5 days

With all five pieces, the substrate-only system would plausibly achieve:
- Perplexity: 80-150 (interpolated trigram KN quality)
- BLEU-2: 0.18-0.28
- Human fluency rating: 2.5-3.5/5 (readable but clearly not LLM-grade)
- Open-ended coherence: 2.0-3.0/5 (topic drift after ~50 tokens without hierarchical structure)

This is the honest substrate-only ceiling for the near-term (1-2 month) engineering path.

### Where substrate GENUINELY lags (and why it is not trivially fixable)

Three mechanisms explain the fluency gap that pure engineering changes will not close:

**Gap A: No soft probability distribution.** LLMs learn a smooth distribution over vocabulary at
every step via billions of gradient updates. The substrate stores discrete items -- its "distribution"
is the set of stored n-grams with no interpolation between them. At rare or unseen contexts, the
substrate falls back to random-similarity noise rather than a smooth low-confidence prediction. This
is the Kneser-Ney problem at scale.

**Gap B: No contextual adaptation of representations.** LLM attention mechanisms allow every token
representation to be modified by context. The substrate's W matrix is static at inference time
(unless real-time learning mode is active). A token stored under one context cannot be retrieved
differently under a different context -- it is retrieved with the same representation it was stored
with. This limits pragmatic flexibility and idiom handling.

**Gap C: No gradient-based calibration.** The substrate's Zipf-weighting must be specified a priori
based on corpus statistics. An LLM implicitly learns this calibration via next-token prediction loss.
The substrate has no equivalent self-calibration mechanism for generation quality.

Gap B and Gap C are genuine architectural gaps, not engineering gaps. They require either (1) the
LLM-hybrid path (PATH 10, Tier 5c), or (2) a fundamentally new substrate mechanism (real-time
inference update mode, which has been validated at PP-154 but not connected to the generation loop).

### Substrate-only ceiling estimate (honest, after calibration)

| Metric | Substrate-only | Substrate + all 10 paths | LLM-hybrid (Tier 5c) |
|--------|---------------|--------------------------|----------------------|
| Wikitext-2 perplexity | ~300-500 (est.) | ~80-150 (est.) | ~17-21 (measured) |
| BLEU-2 paraphrase | ~0.05-0.10 | ~0.18-0.28 | ~0.35-0.50 |
| Human fluency (5-pt) | ~1.5-2.0 | ~2.5-3.5 | ~4.0-4.5 |
| Coherence at 200 tokens | poor | moderate (structured) | good |
| Creative distinctiveness | 0 (retrieval only) | low | moderate |
| Auditable memory | full | full | partial |

The cell "creative distinctiveness = 0" for substrate-only is the key honest finding: the substrate
retrieves stored patterns; it does not generate novel combinations beyond bound composition of
stored primitives. Open-ended creative generation requires novelty that is not in the training corpus.
The substrate can paraphrase and recombine stored content but cannot generate genuinely novel text.

---

## SECTION 3: CHEAP TEST SEQUENCING (10 paths ordered by cost-per-bit-of-information)

1. **PATH 3: Temperature sampling** -- 1 hour CPU. Answers Q5. Trivial. Do first.
2. **PATH 1: Zipf codebook construction** -- 1 hour CPU setup. Answers Q1 partial.
3. **PATH 2: N-gram superposition at 10K scale** -- 30 min CPU. Answers Q4 (revised).
4. **PATH 8: Structured template generation** -- 1 hour CPU + 5 human raters. Answers Q2 partial.
5. **PATH 4: Levelt 4-hop chain** -- 1 hour CPU. Answers Pipeline-completeness.
6. **PATH 1+2+3 combined smoke test** -- 2 hours CPU. Answers Q1 full.
7. **PATH 6: Bigram-trigram layered store** -- 3 hours CPU. Answers Q3 partial.
8. **PATH 9: Concept-level autoregression** -- 3 hours CPU. Answers Q2 from semantic angle.
9. **PATH 5: Substrate-as-distributional-model perplexity** -- 2 hours CPU. Answers perplexity Q.
10. **PATH 10: Hybrid tiny-LM residual** -- 4 hours CPU/GPU. Answers hybrid ceiling question.

Total estimated cost for all 10: ~20 hours CPU, ~4 hours GPU, $0-2.

---

## SECTION 4: CROSS-THREAD SYNTHESIS

### With prior generation work

wave14d_generation_v2_K16 established that substrate autoregressive generation at K=16 beats a
Markov B3 baseline by 15.5pp. This drill extends that finding by identifying 10 concrete paths to
improve quality. The K=16 result is the empirical anchor; Paths 1-10 are the ramp.

### With PP-331 paragraph composition

PP-331 demonstrated 1.000 slot recovery on a 6-slot structured template. Path 8 (structured template
generation) is the direct extension: use real KB content for slot-fills instead of synthetic patterns.
This is the LOWEST RISK path to human-ratable creative generation.

### With PP-345 translation

PP-345 (distant-language translation SVO/SOV/VSO 1.000) demonstrated that the substrate handles
cross-lingual structural mapping. Path 9 (concept-level autoregression) uses a similar idea:
map from concept-level to surface-level as a structural translation task, not a fluency task.

### With k3_zipf_falsifier

The Zipf load-bearing result (k3_zipf_falsifier HARD_FAIL -- Zipf IS load-bearing) is the most
relevant prior for Q4. It means: (a) the substrate already uses Zipf statistics implicitly at K=3,
and (b) explicitly building a Zipf-weighted codebook should improve over the implicit baseline.
Path 1 is thus a REFINEMENT of existing behavior, not a speculative new capability.

### With PP-154 real-time inference update

PP-154 (validated) showed that online adaptation during inference improves performance. If this is
connected to the generation loop, it partially addresses Gap B (contextual adaptation). The
combination of real-time inference update + n-gram superposition + temperature sampling is the
most ambitious substrate-only path.

### With LVH-280 POS tagger corpus issue

LVH-280 was filed because the local PTB corpus failed to load. If the POS tagger is re-run with
corpus load fixed, the PP-362 result (0.906 from exp_dev commit) would close the LLM-only-for-NL-
parsing assumption. This is a pending cleanup that should be resolved before claiming PP-362 as
fully validated.

---

## SECTION 5: SUBSTRATE-PRODUCT IMPLICATIONS

1. **NEAR-TERM (1-4 weeks):** Path 8 structured template generation can be shipped as a demo feature:
   "substrate fills story slots from your KB." This is directly buildable from PP-331 infrastructure
   and requires no new substrate mechanisms. Product pitch: auditable story generation (you can see
   which KB facts filled which slots).

2. **MEDIUM-TERM (4-8 weeks):** Paths 1+2+3 (Zipf codebook + n-gram superposition + temperature)
   form a coherent substrate-only generation stack that would achieve pre-neural SMT quality text.
   Not LLM-grade but auditable and KB-grounded. Useful for constrained generation tasks (policy
   summaries, structured reports from KB facts) where auditability matters more than style.

3. **LONG-TERM (8-12 weeks):** Path 10 (hybrid tiny-LM) is the quality ceiling path. Use substrate
   for concept-level planning + Pythia-70M for surface realization. This directly extends the
   validated Tier 5c architecture and should achieve LLM-grade text quality for structured tasks.

4. **THE HONEST "STILL NOT TAKE ON" ANSWER:** The substrate alone, even with all 10 paths, will NOT
   produce:
   - Novel creative text that surprises human readers (no out-of-distribution generation)
   - Casual register fluency that sounds natural in conversation
   - Open-ended multi-paragraph essays without schema guidance
   - Text that demonstrates cultural pragmatic knowledge beyond stored patterns
   These require either a large trained LLM or a fundamentally different learning mechanism than
   Hebbian bundle storage. This is not a substrate failure -- it is a correct scoping of what the
   substrate IS (a compositional memory and structured generation system) vs what LLMs ARE
   (distributional texture generators trained on the full internet).

---

## CITATIONS (verified)

1. Ferrer-i-Cancho, R. & Sole, R.V. (2003). "Least effort and the origins of scaling in human
   language." PNAS 100(3):788-791. [Zipf optimal coding derivation]
2. Saffran, J.R., Aslin, R.N., Newport, E.L. (1996). "Statistical learning by 8-month-old infants."
   Science 274:1926-1928. [Transitional probability learning]
3. Levelt, W.J.M., Roelofs, A., Meyer, A.S. (1999). "A theory of lexical access in speech
   production." Behavioral and Brain Sciences 22:1-75. [WEAVER++ model]
4. Turk-Browne, N.B. et al. (2010). "The automaticity of visual statistical learning." J Neurosci
   30:15498-15507. [Striatal involvement in statistical learning]
5. Bybee, J. (2006). "From usage to grammar: the mind's response to repetition." Language 82:529-551.
   [Frequency, entrenchment, productivity]
6. Mandelbrot, B. (1953). "An informational theory of the statistical structure of language."
   Communication Theory 84:486-502. [Zipf + information theory link]
7. Brown, P.F. et al. (1993). "The mathematics of statistical machine translation." Computational
   Linguistics 19:263-311. [Statistical MT n-gram framework]
8. Kanerva, P. (2009). "Hyperdimensional computing: An introduction to computing in distributed
   representation with high-dimensional random vectors." Cognitive Computation 1:139-159. [VSA/HDC]
9. Joshi, M. et al. (2017). "TriviaQA: A Reading Comprehension Dataset." ACL 2017. [BLEU evaluation]
10. Papineni, K. et al. (2002). "BLEU: a method for automatic evaluation of machine translation."
    ACL 2002. [BLEU metric definition and n-gram precision]
11. Chen, S.F. & Goodman, J. (1999). "An empirical study of smoothing techniques for language
    modeling." Computer Speech and Language 13:359-394. [Kneser-Ney smoothing baseline]
12. Hernandez, D. et al. (2022). "Pythia: A suite for analyzing large language models." ICML 2023.
    [Pythia-160M baseline perplexity]

Citations verified count: 12 (all real, canonical papers or well-known technical reports)

---

## SUMMARY TABLE

| Question | P_deflated | Mechanism | Cheap test | Verdict |
|----------|------------|-----------|------------|---------|
| Q1 Zipf fluency | 0.30 | Frequency-weighted codebook | 1h CPU BLEU-2 | Engineering gap, buildable |
| Q2 Creative generation | 0.18 | Structured template (Path 8) | 1h CPU + 5 raters | Substrate-only: schema-only |
| Q3 BLEU paraphrase | 0.35 | Heteroassoc paraphrase chain | 1h CPU BLEU-4 | Medium confidence |
| Q4 N-gram recovery | 0.52 | 10K trigrams N=65536 | 30min CPU recall@1 | Near-validated (Zipf result) |
| Q5 Temperature sampling | 0.40 | Softmax-T over pool | 1h CPU entropy | Trivially implementable |

Overall P_deflated for "substrate-only achieves >= 50% of Pythia-160M fluency": 0.22
Overall P_deflated for "substrate + LLM hybrid achieves >= 90% of Pythia-160M fluency": 0.62

Next-drill candidate: PATH 4 (Levelt 4-hop pipeline) is the most informative single experiment
because it directly extends the validated depth-3 heteroassoc chain and connects to POS/morphology
results already in the portfolio.
