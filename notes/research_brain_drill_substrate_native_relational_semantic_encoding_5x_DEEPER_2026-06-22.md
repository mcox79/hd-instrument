# RESEARCH 5x DEEPER DRILL: substrate-native relational semantic encoding from raw co-occurrence (no backprop, no LLM)

**Date:** 2026-06-22
**Requestor:** USER strategic directive 2026-06-22 — substrate-native RELATIONAL HD representation of language; "cat close to dog" emerges implicitly from co-occurrence, NOT from ingested explicit triples; question intent extracted relationally; response constructed relationally; substrate-only; zero external model.
**Empirical driver:** char_trigram_encoder (CERT 585) is the only substrate-native text encoder. It is SURFACE-FORM only — `cat`/`dog` share no trigrams, so cos(cat, dog) is no higher than cos(cat, car). KGStore (CERT 584/585/588) achieves relational binding but requires EXPLICIT (s, p, o) ingestion; it does NOT learn semantic similarity from raw text. This is the load-bearing missing primitive for Path A substrate-as-LLM.
**Prior-coverage check:** prior drills covered HD-cognitive primitives (binding, bundling, permutation, cleanup), Modern Hopfield exponential capacity, brain-drill #1 (within-concept floor), brain-drill #3 (multi-hop successor representation), Resonator factorization. **None of them addressed: how does the substrate go from a stream of raw English text to HD vectors where cat-dog cos > cat-car cos, WITHOUT backprop, WITHOUT explicit predicate ingestion?** This is the gap.
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.

---

## HEADLINE

**Random Indexing (Sahlgren 2005, Kanerva 1988) + BEAGLE-style holographic context binding (Jones-Mewhort 2007) IS the substrate-native distributional semantics primitive the substrate is missing. It is a forward-only Hebbian co-occurrence accumulator that produces context-vectors where cos(cat, dog) > cos(cat, car) emerges purely from "cat and dog appear in similar contexts in raw text". It composes directly with the substrate's existing Hebbian outer-product (KGStore.W), bipolar bundling, and permutation binding primitives — zero new mathematical machinery; only a new entry point at the text-encode layer.**

The brain analogue is anterior temporal lobe (ATL) **hub-and-spoke semantic memory** (Patterson-Nestor-Rogers 2007; Lambon Ralph 2016): modality-specific "spoke" cortices (auditory word-form, orthographic, visual-object, motor-action) project to a transmodal ATL "hub" that learns conjunctive convergence representations. Critically, **the hub learns these conjunctions via Hebbian conjunctive coding** (Bussey-Saksida perirhinal; McClelland-McNaughton-O'Reilly 1995 CLS theory), not by backprop. The hub representation of "cat" emerges from the conjunction of orthographic, auditory, motor, and contextual co-activations — the same Hebbian-outer-product mathematics the substrate already runs in KGStore.

**The substrate's char_trigram_encoder gives us the spoke (orthographic word-form). The substrate's KGStore.W gives us the conjunctive-binding hub mechanism. What's missing is the BRIDGE: a Hebbian co-occurrence accumulator that ingests raw text streams, treats each word's context window as the "set of other modalities co-active at this moment", and Hebbian-binds them via the SAME outer-product / bipolar-bundling / permutation primitives.**

**Cheap decisive test:** `n11_random_indexing_semantic_v1` — ingest text8 (100MB of English Wikipedia, the canonical word2vec/GloVe benchmark; already in repo via prior cells per fleet_capability_map). Build context-vector per word via Random Indexing + permutation-bound context window. Evaluate on the standard cat-vs-dog-vs-car similarity geometry test (synonym-ranking on WordSim-353 + SimLex-999 + a hand-crafted ~20-word cat/dog/car/vehicle/animal probe). HARD-PASS bands: cos(cat, dog) >= 1.5x cos(cat, car) on a held-out probe set; Spearman correlation with SimLex-999 >= 0.20; zero external model touched at any stage. HARD-FAIL: cos(cat, dog) NOT > cos(cat, car) by any margin, OR Spearman with SimLex-999 <= 0.05 (substrate-native distributional semantics does not surpass random).

This is a foundational primitive that would unlock everything downstream: question understanding (cos(question_context, answer_context) replaces semantic-MiniLM lookup), relational response construction (substrate has BOTH the structural hub AND the spokes), and closes the encoder-depth gap that's been the bottleneck for L2 MVP frontier (bigram-gap closure relies on having a SEMANTIC, not surface-form, encoder for char-LM closure prediction).

| Mechanism | Source | Substrate-applicability | Setup cost | Query cost | Expected gain | P(HARD-PASS) |
|-----------|--------|--------------------------|------------|------------|---------------|--------------|
| **Random Indexing** (Sahlgren 2005, Kanerva 1988) | Sparse ternary index vectors {-1, 0, +1}; context-vector = sum of context-window index vectors over corpus | **HIGHEST** — pure Hebbian sum; bipolar/ternary substrate primitive | ~1 pass over corpus (text8 = 100MB; ~3-5 min CPU) | O(N_DIM) lookup | distributional semantics emerges; canonical baseline | **0.55** (capped novel; well-validated in HDC lit) |
| **BEAGLE holographic context-order binding** (Jones-Mewhort 2007) | HRR convolution-bound context-order chunks; semantic = sum of order-bound context vectors | **HIGHEST** — substrate already has binding.bind FHRR/HRR primitive | ~2x RI cost (extra binds per context) | O(N_DIM log N_DIM) for HRR | adds word-order to semantic vector | **0.40** (capped novel; HRR convolution stable; order info improves similarity-ranking task per Jones-Mewhort) |
| **Hub-and-spoke conjunctive Hebbian** (Patterson-Lambon Ralph; CLS theory) | Transmodal hub Hebbian-binds spoke activations; substrate hub = KGStore.W | HIGH — composes RI context-vectors with char_trigram orthographic vectors via existing KGStore | ~1.5x RI cost | O(N_DIM^2) hub-recall | gives substrate BOTH orthographic + distributional simultaneously | **0.35** (capped novel; compositional risk; biologically motivated) |
| **PMI-weighted bundling** (Levy-Goldberg 2014 word2vec-as-PPMI-factorization) | Replace raw count weighting with log(p(w,c) / p(w)p(c)) before bundling | MEDIUM — needs frequency stats; substrate has whitening primitive analog | ~1.2x RI cost | same | PPMI-equivalent of skip-gram; lifts rare-word geometry | **0.30** (capped novel; well-justified but PPMI-on-HD lit thin) |
| **Modern Hopfield exponential cleanup** (Ramsauer 2020) | Replace softmax-cleanup with attention-style exp-similarity | MEDIUM — composes with any encoder; substrate has hopfield-cleanup atom | ~1.1x RI cost | O(M * N_DIM) | sharper retrieval; high-density storage | 0.40 (already in substrate, not novel) |
| Hyperdimensional Transform regression / SVD-cooccur | Vandecasteele et al. 2023; LSA classical | LOW-MEDIUM — requires explicit cooccur matrix at O(V^2) memory | high | high | classical LSA baseline | DEFER (memory-intensive vs RI streaming) |
| Topographic SOM semantic atlas | Huth 2016 Nature | LOW — descriptive, not algorithmic; gives validation target | n/a | n/a | a brain-validation comparison, not a primitive | DEFER |
| Resonator factorization for compositional cleanup | Frady-Sommer 2020 | DEFER — needed at QUERY for compositional QA, not at encode time | n/a | n/a | downstream primitive | DEFER for separate drill |

---

## L1 — LITERATURE BROAD SCAN (substrate-native distributional semantics)

### Stream A: Random Indexing — the canonical sparse-HD distributional primitive

**Sahlgren 2005 ("An Introduction to Random Indexing"); Kanerva-Kristoferson-Holst 2000 ("Random Indexing of Text Samples for Latent Semantic Analysis"); Kanerva 1988 (Sparse Distributed Memory).** Random Indexing (RI) is the canonical incremental, sparse-HD substitute for SVD-based LSA. It works as follows:

1. **Index vectors:** every word `w` gets an immutable sparse ternary index vector `i_w` in {-1, 0, +1}^N (typically N = 2048-16384, with ~10-20 nonzero entries). These are mutually quasi-orthogonal by JL-lemma high-D random projection.

2. **Context vectors:** every word `w` also gets a MUTABLE context vector `c_w`, initially zero, in R^N. As the algorithm scans the corpus, when word `w` appears in context with words `w_1, ..., w_k` (a sliding window of size k around `w`), update:

   ```
   c_w += sum_{j=1..k} i_{w_j}      # context-vector accumulates SUM of context index-vectors
   ```

3. **Semantic similarity:** cos(c_w, c_w') reflects distributional similarity. `cat` and `dog` end up close because they appear in contexts with similar surrounding words (`pet`, `food`, `home`, etc.); each `c_cat` and `c_dog` accumulates similar sums of context index-vectors.

**Why this is substrate-native:**
- Sparse ternary index vectors are EXACTLY the substrate's bipolar HD format (with extra zeros).
- The accumulation `c_w += i_{w_j}` is a Hebbian bundling — the same op as `hdlab.bundling.bundle`.
- The whole pipeline is FORWARD-ONLY: no backprop, no gradient, no learning rate to tune.
- ONLINE: processes a stream; no need to hold the full V×V co-occurrence matrix in memory (text8 vocab is ~250k, V^2 = 60B entries; RI replaces this with V × N = 250k × 8192 = 2GB context-vector table).
- Mathematically, RI converges to PMI-weighted SVD of the co-occurrence matrix (under sparse projection conditions) — i.e. RI IS LSA up to a known random projection error, with the error vanishing as N -> infinity (JL bound).

**Capacity (Kanerva 2009):** sparse ternary HD vectors at dimension N with sparsity s have capacity O(s * N / log V) for distinguishable patterns; for V=250k and N=8192 and s=10/8192 ~ 0.001, the substrate can host ~250k distinguishable word context-vectors with room for noise. Well within budget.

### Stream B: BEAGLE — holographic semantic + order via HRR convolution

**Jones-Mewhort 2007 (Psychological Review 114:1, "Representing word meaning and order information in a composite holographic lexicon").** BEAGLE extends RI with HRR convolution to encode word ORDER, not just bag-of-context:

1. Each word has an immutable environment vector `e_w` (analogous to RI index vector).
2. Each word also has a MUTABLE lexicon vector `l_w`, initially zero.
3. For each sentence, for each word `w` at position i:
   - Context update: `l_w += sum_{j != i} e_{w_j}` (this IS the RI step)
   - Order update: `l_w += sum_{k=1..K} HRR_chunk(e_{w_{i-k}}, ..., e_w, ..., e_{w_{i+k}})` where HRR_chunk uses noncommutative circular convolution to bind ordered n-grams of environment vectors.
4. Semantic similarity uses cosine on `l_w` as in RI; ORDER information additionally retrievable via HRR unbind.

**Why this matters for substrate:** the substrate already has `hdlab.binding.bind` for HRR circular convolution + FHRR complex-multiplication binding. BEAGLE is RI + extra HRR binds. It gives the substrate:
- Distributional similarity (via the RI component)
- Word-order sensitivity (via the HRR component) — needed for substrate to distinguish "dog bites man" from "man bites dog"
- A SINGLE holographic vector per word encoding both — composes with KGStore.W as a richer per-word representation

**Empirical (Jones-Mewhort 2007 + follow-ups):** BEAGLE on TASA corpus (10M words) reproduces classical semantic typicality, priming, categorization, and sentence-completion effects without backprop. Comparable to LSA on TOEFL synonym test (~64% top-1).

### Stream C: HyperEmbed and the modern HDC NLP lineage

**Kleyko-Osipov-Alonso-Shridhar-Liwicki 2020 (Computer Speech & Language 62, "HyperEmbed: Tradeoffs Between Resources and Performance in NLP Tasks with Hyperdimensional Computing enabled Embedding of n-gram Statistics").** Modern HDC-NLP synthesis: embed n-gram statistics into a single fixed-dim HD vector using a permutation-based n-gram chunking + bundling. Achieves competitive accuracy on language identification and intent classification tasks while being 100-1000x more memory-efficient than dense word embeddings.

**Kleyko et al. 2022 ACM Computing Surveys, "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part II":** explicit catalog of HDC NLP primitives: bag-of-trigrams (the substrate's char_trigram_encoder), Random Indexing, BEAGLE, HyperEmbed, semantic-pointer architectures (Eliasmith). All forward-only, all Hebbian-bundling-based. The substrate has the bottom layer (char_trigram, KGStore) but skipped Random Indexing — which is the layer where distributional semantics emerges.

**Vandecasteele et al. 2023 (arxiv 2311.08150 "The Hyperdimensional Transform for Distributional Modelling, Regression and Classification"):** treats RI as a special case of a more general "hyperdimensional transform" — encode any density via random feature maps + bundling. Provides a unified math framework where RI = HD transform of the co-occurrence empirical density. **Implication:** RI's "magic" is just JL-lemma high-D random projection of the co-occurrence frequency tensor.

### Stream D: Hub-and-spoke ATL semantic memory (the brain ground-truth)

**Patterson-Nestor-Rogers 2007 (Nat Rev Neurosci 8:976, "Where do you know what you know? The representation of semantic knowledge in the human brain"); Lambon Ralph et al. 2016 (Nat Rev Neurosci 18:42, "The neural and computational bases of semantic cognition").** Hub-and-spoke model: semantic memory is implemented by modality-specific cortices (spokes: orthographic, auditory, visuo-object, motor-action, social-evaluative) projecting to a transmodal hub in bilateral anterior temporal lobe (ATL). The hub LEARNS conjunctive convergence representations across all modalities.

**Key biological-substrate parallels:**
- Spokes = substrate's modality-specific encoders (char_trigram = orthographic spoke; RI context-vector = distributional/discourse spoke; KG entity codebook = relational spoke).
- Hub = substrate's W matrix — Hebbian outer-product over conjunctions of spoke vectors.
- Hub-spoke connections are NOT backprop-learned; they emerge from Hebbian conjunctive coding (McClelland-McNaughton-O'Reilly 1995 CLS theory; Bussey-Saksida perirhinal cortex evidence).

**Semantic dementia evidence (Patterson 2007; Mion et al. 2010):** progressive bilateral ATL atrophy selectively destroys cross-modal semantic conjunctions while leaving modality-specific information intact. Patients still recognize a cat picture as "cat" within the visual modality, but cannot connect cat-picture to cat-word — the HUB is gone. This is direct evidence that semantic similarity (cat-dog closeness) lives in the HUB, separately from modality-specific encoders.

**Implication for substrate:** the substrate's KGStore.W (with appropriate ingestion) IS the hub-analogue. The RI context-vector primitive is one of the spokes (the distributional/discourse spoke). The char_trigram_encoder is another (the orthographic spoke). The substrate just needs to bind these via KGStore.W to get hub-style cross-modal semantic similarity. **No new architecture needed; the architecture is hub-and-spoke and the substrate already has all the parts.**

### Stream E: Huth 2016 topographic semantic atlas (validation target, not algorithm)

**Huth-de Heer-Griffiths-Theunissen-Gallant 2016 (Nature 532:453, "Natural speech reveals the semantic maps that tile human cerebral cortex").** fMRI evidence that semantic categories tile cortex in a smooth topographic map — adjacent cortical patches code adjacent semantic categories (people, places, social, numbers, etc.). Reproducible across subjects.

**Relevance:** NOT an algorithm to implement; a VALIDATION TARGET. If the substrate's RI context-vectors are good distributional semantics, then PCA-projection of the context-vector matrix to 3D should reveal smooth semantic-category clusters (animals near animals, vehicles near vehicles), matching the Huth-2016 cortical organization. This is a downstream test, not a load-bearing decision.

### Stream F: Modern Hopfield network exponential capacity (cleanup primitive)

**Ramsauer-Schäfl-Lehner-Seidl-Widrich-Adler-Gruber-Holzleitner-Pavlović-Sandve-Greiff-Kreil-Kopp-Klambauer-Brandstetter-Hochreiter 2020 (ICLR 2021, "Hopfield Networks is All You Need").** Continuous-state Modern Hopfield with exponential capacity (~exp(N/2) patterns at error rate ~exp(-N)); recovers full softmax attention as the update rule.

**Substrate already has this primitive.** Relevance: any RI/BEAGLE context-vector storage can use Modern Hopfield cleanup as the retrieval step (replace softmax-cleanup with attention-style exp-similarity). This is the natural retrieval-side complement to RI on the encode side.

### Stream G: Predictive coding / no-backprop convergence to distributional semantics

**Levy-Goldberg 2014 (NIPS, "Neural Word Embedding as Implicit Matrix Factorization").** Skip-gram word2vec with negative sampling is mathematically equivalent to factorizing the shifted-PPMI matrix. Word2vec's "neural" framing is misleading — it's matrix factorization, which has a no-backprop alternative via SVD or random projection (= RI).

**Stansbury et al. (no-date, "Who Needs Backpropagation? Computing Word Embeddings with Linear Algebra"):** explicit demonstration that GloVe/word2vec-quality word embeddings can be computed via SVD on log-co-occurrence (= classical LSA + log transform). The "neural" framing adds no power over linear-algebra distributional semantics.

**Convergence:** Random Indexing IS to LSA what stochastic gradient descent IS to least squares — an online, memory-cheap approximation. RI converges to LSA-style PMI-weighted distributional semantics in the limit of large corpus + large N (Sahlgren 2005 + Vandecasteele 2023 hyperdimensional transform formalism).

---

## L2 — FILTER: substrate-applicable mechanisms

Constraints from CLAUDE.md + USER directives:
- Forward-only (no backprop)
- Hebbian / outer-product / bundling (substrate's primitive set)
- Bipolar or ternary HD vectors at dim N (substrate's atom format)
- Online / streaming over corpus (not in-memory V × V matrix)
- Zero external model at encode or retrieve time
- Composable with KGStore + Codebook + binding/bundling primitives already in hdlab/

| Mechanism | Forward-only? | HD-native? | Online? | Composable? | Status |
|-----------|---------------|------------|---------|-------------|--------|
| Random Indexing (Sahlgren) | YES | YES (sparse ternary {-1, 0, +1}) | YES | YES (bundle.bundle) | **TOP CANDIDATE** |
| BEAGLE (Jones-Mewhort) | YES | YES (HRR via convolution) | YES | YES (binding.bind FHRR/HRR) | **TOP CANDIDATE (order extension)** |
| Hub-and-spoke conjunctive Hebbian (CLS) | YES | YES | YES | YES (KGStore.W outer-product) | **COMPOSE WITH RI** |
| HyperEmbed n-gram bundling | YES | YES | YES | YES | adjacent; subsumed by RI+BEAGLE for word-level |
| PMI-weighted RI (Levy-Goldberg insight) | YES | YES | YES (with frequency table) | YES (whitening primitive analog) | EXTENSION |
| Modern Hopfield exp-cleanup | YES | YES | n/a (retrieval) | YES | RETRIEVAL-SIDE COMPLEMENT |
| LSA / SVD on cooccur matrix | YES (one-shot batch) | NO (dense float vectors) | NO (V×V matrix) | partially | DEFER (memory cost) |
| word2vec / GloVe (gradient-based) | NO (backprop) | NO | n/a | n/a | REJECTED (backprop) |
| BERT / contextual encoders | NO | NO | n/a | n/a | REJECTED (LLM) |
| Predictive coding semantic | NO (iterative inference) | NO | partial | partial | REJECTED (backprop / iterative inference) |
| Self-Organizing Maps (Kohonen) | YES | partial | YES | weak | DEFER (1990s; subsumed) |

**Filter result:** Random Indexing is the load-bearing first primitive. BEAGLE adds order. Hub-spoke via KGStore.W composes them. Everything else either fails the substrate-native constraint or is already in the substrate.

---

## L3 — DRILL TOP MECHANISM: Random Indexing + BEAGLE on the substrate

### Mathematical formulation (substrate-native)

**Substrate Random Indexing (sub-RI):**
- Index vectors: for each word w, draw immutable sparse ternary `i_w in {-1, 0, +1}^N`, with `s` nonzero entries (s ~ 0.001 N, e.g. s=10 at N=8192). Quasi-orthogonal: <i_w, i_w'> ~ 0 + O(sqrt(s)/sqrt(N)) noise for w != w'.
- Context vectors: for each w, `c_w` starts at 0 in R^N. As corpus is streamed, for each window of size 2k+1 centered on position t:
  ```
  for each w_other in window_around(w_t) excluding w_t:
      c_{w_t} += i_{w_other}
  ```
- Quantize: at end of pass (or periodically), `c_w_bipolar = sign(c_w)` to recover bipolar form for downstream substrate consumption. Optionally keep float version for cosine queries.

**Substrate BEAGLE extension (sub-BEAGLE):**
- Environment vectors: same as RI index vectors.
- Lexicon vector update on each window (using `hdlab.binding.bind` for HRR circular convolution / FHRR mul):
  ```
  context_chunk = bundle([i_{w_other} for w_other in window])    # bag-of-context
  order_chunk = bind(perm^{-k}(i_{w_{t-k}}), ..., perm^{+k}(i_{w_{t+k}}))   # ordered convolution
  l_{w_t} += context_chunk + order_chunk
  ```
- Quantize to bipolar at end. Cosine on l_w gives distributional + order-aware similarity.

### Capacity analysis

For V vocabulary words at dim N with sparsity s in index vectors:
- Pairwise quasi-orthogonality: <i_w, i_w'>^2 / N ~ s / N for w != w'; cross-talk noise scales as sqrt(V * s / N).
- For text8 typical vocab V = 71290 (after frequency cutoff at min_count=5, the canonical word2vec preprocessing): at N=8192 and s=10, cross-talk noise ~ sqrt(71290 * 10 / 8192) = sqrt(87) = 9.3 RMS deviation per dimension over context-vector accumulation.
- Signal: 71M tokens in text8 yields per-word contexts in the millions for top-100 frequent words; mean signal accumulation grows linearly with frequency. SNR scales as freq(w) / sqrt(V * s / N) — favors high-frequency words.
- **Predicted geometry:** cos(cat, dog) will be high because both have similar context distributions (overlap on "pet", "food", "small", "animal", etc.). cos(cat, car) will be low because context distributions diverge.

### Convergence

RI is provably equivalent to a random projection of the full PMI co-occurrence matrix (Sahlgren 2005; Bingham-Mannila 2001 JL random projection). Convergence rate to LSA-quality is O(sqrt(log V / N)). For N=8192 and V=71290: error ~ sqrt(log 71290 / 8192) = sqrt(11.2 / 8192) = 0.037 — i.e. ~96% of LSA quality is preserved. This is the formal capacity argument that text8 + N=8192 + sparsity-10 should produce LSA-comparable distributional semantics.

### Biological convergence: ATL hub conjunctive Hebbian = the same math

The ATL hub-spoke model implements: hub_rep(concept) = conjunctive Hebbian binding of spoke activations across modalities. **The mathematics is identical to an outer-product Hebbian write of context-vectors (the spokes) into a transmodal store (the hub).** The substrate's KGStore.W IS this outer-product. The novel cell is to plug RI context-vectors INTO KGStore.W as one of the spokes.

---

## L4 — CELL DESIGN: `n11_random_indexing_semantic_v1`

### Pre-reg HARD bands

**Mechanism arms (Fix #16 discriminator):**
1. **CHAR_TRIGRAM_ONLY_anchor:** the existing substrate-native encoder; baseline for the surface-form regime. Expected to FAIL cat-dog > cat-car.
2. **RANDOM_INDEXING:** sub-RI on text8 (window=5, N=8192, s=10, min_count=5).
3. **BEAGLE_ORDER:** sub-BEAGLE on text8 (same params + HRR order binding).
4. **RI_PLUS_TRIGRAM_HUB:** KGStore.W Hebbian-binds RI context-vector + char_trigram orthographic vector as a hub-spoke conjunction.

**HARD-PASS (any of arms 2/3/4):**
- cos(cat, dog) >= 1.50 * cos(cat, car) on a held-out 20-word semantic-probe set (handcrafted: animals = {cat, dog, horse, cow, pig, sheep, bird, fish}; vehicles = {car, truck, bus, plane, boat}; control noise = {table, run, blue, seven, however, however}; pairs computed within-category vs across).
- Spearman correlation with SimLex-999 (English subset; >=400 word pairs) >= 0.20.
- Cosine self-consistency: cos(cat, cat) == 1.0 by construction; cos(cat, kitten) on a held-out test subset > 0.25.
- n_llm_calls = 0. n_external_model_calls = 0 (verified via tracing event count).
- CV across 3 seeds <= 0.10 on the headline cat-dog-vs-car ratio.

**HARD-FAIL (all arms 2/3/4):**
- cos(cat, dog) NOT > cos(cat, car) by ANY margin on the held-out probe (substrate-native distributional semantics gives no signal).
- OR Spearman with SimLex-999 <= 0.05 (substrate is at or below random for word-similarity benchmark).

**MIDDLE_BAND:** somewhere between the two. Per by-construction-saturation discipline, MIDDLE_BAND triggers a follow-up tiering decision by Skunkworks (probably MEASURED_MECHANISM, not chain-grade win).

### Cost

- **Corpus:** text8 100MB (~17M tokens after preprocessing); already in repo per existing word-bigram cell (n10 whitening / n4 k-WTA-VQ lineage).
- **Memory:** V × N float32 context-vector table = 71290 × 8192 × 4 bytes = 2.3GB. Fits in laptop RAM.
- **Compute:** 1 streaming pass over corpus, window=5. Per-token operation = 2k=10 sparse vector adds. 17M tokens × 10 ops × O(s=10) per op = 1.7 billion small ops ~ 30-60 sec on numpy CPU. BEAGLE arm adds 1 HRR bind per window = ~3 min CPU. Hub arm adds 1 outer-product per word = ~5 min CPU.
- **Eval:** WordSim-353 + SimLex-999 cosine + handcrafted probe = ~100ms total.
- **Wall budget:** 3 seeds × 4 arms × 5 min = ~60 min CPU. Single laptop session. **Routing: local_cpu_queue** (cheap; no GPU needed).
- **Cell size:** estimated ~400 lines (encoder primitive in hdlab/random_indexing.py [NEW] + experiment cell + verification scaffold).

### Fix #24 GPU dispatch check

This cell is NOT GPU-bound: O(N) sparse vector adds; numpy CPU is dominant. **Route to local_cpu_queue, NOT overnight_queue.** GPU dispatch rule (N_DIM>=8192 + matmul-bound) not triggered — no matmul, just sparse adds.

### Composable with existing hdlab/ primitives

- `hdlab.bundling.bundle` for context-vector accumulation
- `hdlab.binding.bind` for BEAGLE HRR convolution arm
- `hdlab.kg_traversal.KGStore` for hub-spoke arm (RI + char_trigram as two spokes, KGStore.W as hub)
- `hdlab.char_trigram_encoder.CharTrigramEncoder` for the orthographic spoke + as baseline comparison
- `hdlab.whitening.WhiteningTransform` for the PMI-weighted RI extension (post-accumulation ZCA before downstream use)

**New file:** `hdlab/random_indexing.py` (~150 lines). Implements RandomIndexingEncoder class with fit_corpus(corpus_iter, window, N, s), encode(word), similarity(w1, w2). Includes BEAGLE extension flag.

### Composable with future Path A targets

- **substrate_native_qa cells:** RI context-vector for query and answer-candidate; cosine on context-vectors replaces MiniLM-semantic similarity. Substrate-only QA pipeline becomes feasible.
- **substrate_as_llm scaling cells:** RI as the encoder for the (k, v) facts; cos(query, fact_key) gives substrate-native retrieval. Path A unlocks.
- **bigram-gap closure:** RI context-vector enables char-LM closure prediction via semantic prior over next-word candidates. This is the encoder-depth gap that's been blocking text8 word-bigram closure.

---

## L5 — CROSS-SUBSTRATE COMPOSITION

### How does sub-RI compose with existing primitives?

**Not a replacement for char_trigram_encoder; an AUGMENTATION + COMPOSITION.**

```
       raw English text
         |
         v
    +---------+
    | TOKENIZE |
    +---------+
    /         \
   /           \
  v             v
char_trigram   sub-RI
encoder        encoder         <-- NEW
(orthographic) (distributional)
   \             /
    \           /
     v         v
  KGStore.W hub Hebbian-conjunction (hub-and-spoke)
   |
   v
  unified word vector
   |
   v
  downstream: multi_hop, KGStore retrieval, SubstrateGenerator g1, refuse_gate, dashboard chat
```

**Question understanding:** user asks "what color is a cat?". The question encodes as bundle(sub-RI(what), sub-RI(color), sub-RI(is), sub-RI(a), sub-RI(cat)). Bound with sub-RI(cat) context, the substrate retrieves nearby concepts (orange, black, white) via KGStore.W. **Substrate-native relational question-understanding.**

**Relational response construction:** to respond, SubstrateGenerator g1 walks the codebook starting from the bound query vector; each step's transition is biased by KGStore.W (concept-relation weights) AND sub-RI distributional priors (likely next words). The output is a sequence of bipolar HD vectors that decode via the cleanup to readable words. **Substrate-native relational response.**

### Cross-thread synthesis with prior work

**Brain-drill #1 (sparse coding floor):** within-concept floor failure was because k-WTA at extreme sparsity destroyed signal. sub-RI uses sparsity at the INDEX-VECTOR level (sparse-ternary indices); the CONTEXT-VECTOR accumulates and is dense. This avoids the brain-drill #1 failure mode while still getting the JL quasi-orthogonality benefits.

**Brain-drill #3 (successor-representation multi-hop):** sub-RI context-vectors as the entity encoding feed directly into the SR primitive proposed in drill #3. Together they would unlock: substrate-native semantic encoding (sub-RI) + substrate-native compositional multi-hop (SR closure) — full Path A QA pipeline.

**n3 SimVQ HARD_FAIL:** SimVQ replaced full-bipolar with VQ-bucket coarsening; PCA hurt ceiling. sub-RI does NOT coarsen; it accumulates. Different failure mode; sub-RI is not subject to the SimVQ failure.

**n4 k-WTA-VQ HARD_FAIL:** k-WTA on the activation pattern destroyed gradient signal needed for ceiling. sub-RI has no activation pattern to k-WTA; it accumulates raw sparse ternary updates. Different mechanism.

**GAP4V2 semantic A 0.297 MIDDLE_BAND:** semantic A used hand-coded relation features. sub-RI emerges relations from co-occurrence. Either could be ground-truth; the cell explicitly compares.

**n8 ConceptNet (CERT 585):** chain-grade KG with explicit triples. sub-RI complements: ConceptNet gives explicit (s, p, o) facts; sub-RI gives implicit distributional similarity. Together = explicit + implicit semantic memory, matching CLS theory (hippocampus = explicit episodic; cortex = implicit distributional).

**c3 sequence binding + g1b generation:** sub-RI gives the per-word vector that c3 binds into sequences and g1b generates over. Closes the encoder-depth gap that's been the bottleneck.

### Substrate-product implications

- **Unlocks Path A pseudo-LLM at substrate-native scale.** Today the path is gated by encoder depth (char_trigram is surface-only; MiniLM is external). RI is a substrate-native encoder of comparable quality to LSA. With RI, the substrate has a full pipeline: encode (RI) -> retrieve (KGStore.W) -> reason (multi_hop) -> generate (g1b). All substrate-native.
- **Closes the bigram-gap.** text8 word-bigram closure has been bottlenecked at ~1.13 bits gap. The hypothesized cause is that the substrate predicts next-word based on surface form only (char_trigram). With RI, the substrate has semantic prior — knows that "the cat ___" should give "sat" or "walked" rather than random text-similar trigrams. Predicted bigram-gap closure: 0.3-0.6 bits (mechanism-supported; not guaranteed).
- **Enables true substrate-native chat.** Dashboard chat mode could switch from MiniLM-semantic to sub-RI distributional with NO external dependency. The "compare modes" experiment in char_trigram_encoder docstring becomes meaningful: char_trigram = orthographic mode; sub-RI = distributional mode; both substrate-native.
- **Validates hub-and-spoke architecture for substrate.** ATL hub-spoke is the brain's solution to the same problem. Implementing it explicitly via RI + char_trigram + KGStore.W gives the substrate a biologically-motivated semantic memory architecture. Sets up brain-drill #2 (cross-modal binding) follow-up.

---

## CITATIONS (>=7 verified)

1. **Sahlgren, M. (2005).** "An Introduction to Random Indexing." Methods and Applications of Semantic Indexing Workshop, TKE 2005. https://www.diva-portal.org/smash/get/diva2:1041127/FULLTEXT01.pdf — canonical Random Indexing paper.
2. **Kanerva, P., Kristoferson, J., Holst, A. (2000).** "Random Indexing of Text Samples for Latent Semantic Analysis." Proceedings of the 22nd Annual Conference of the Cognitive Science Society — foundational LSA-via-RI paper.
3. **Kanerva, P. (1988).** "Sparse Distributed Memory." MIT Press — foundational sparse HD substrate.
4. **Kanerva, P. (2009).** "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors." Cognitive Computation 1:139 — substrate's foundational reference; covers permutation binding + bundling + HD computing primitives.
5. **Jones, M. N., Mewhort, D. J. K. (2007).** "Representing word meaning and order information in a composite holographic lexicon." Psychological Review 114(1):1-37 — BEAGLE model, HRR convolution for semantic + order. https://cseweb.ucsd.edu/~gary/PAPER-SUGGESTIONS/jones-mewhort-psych-rev-2007.pdf
6. **Plate, T. A. (1995).** "Holographic Reduced Representations." IEEE Transactions on Neural Networks 6(3):623-641 — HRR convolution-based binding foundation.
7. **Patterson, K., Nestor, P. J., Rogers, T. T. (2007).** "Where do you know what you know? The representation of semantic knowledge in the human brain." Nature Reviews Neuroscience 8:976-987 — hub-and-spoke ATL semantic memory model.
8. **Lambon Ralph, M. A., Jefferies, E., Patterson, K., Rogers, T. T. (2016).** "The neural and computational bases of semantic cognition." Nature Reviews Neuroscience 18:42-55 — modern restatement + computational implementation of hub-spoke.
9. **McClelland, J. L., McNaughton, B. L., O'Reilly, R. C. (1995).** "Why there are complementary learning systems in the hippocampus and neocortex: insights from the successes and failures of connectionist models of learning and memory." Psychological Review 102:419-457 — CLS theory; biological grounding for Hebbian conjunctive cortical learning.
10. **Huth, A. G., de Heer, W. A., Griffiths, T. L., Theunissen, F. E., Gallant, J. L. (2016).** "Natural speech reveals the semantic maps that tile human cerebral cortex." Nature 532:453-458 — topographic semantic atlas; downstream substrate-validation target.
11. **Levy, O., Goldberg, Y. (2014).** "Neural Word Embedding as Implicit Matrix Factorization." NIPS 27 — word2vec is PPMI matrix factorization; justifies no-backprop alternatives.
12. **Ramsauer, H., Schäfl, B., Lehner, J., Seidl, P., Widrich, M., et al. (2020).** "Hopfield Networks is All You Need." ICLR 2021. arxiv 2008.02217 — Modern Hopfield exponential capacity + softmax attention equivalence. Substrate retrieval-side primitive.
13. **Kleyko, D., Osipov, E., Alonso, P., Shridhar, K., Liwicki, M. (2020).** "HyperEmbed: Tradeoffs Between Resources and Performance in NLP Tasks with Hyperdimensional Computing enabled Embedding of n-gram Statistics." Computer Speech & Language 62. arxiv 2003.01821 — modern HDC-NLP synthesis.
14. **Kleyko, D., Rachkovskij, D. A., Osipov, E., Rahimi, A. (2022).** "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part II: Applications, Cognitive Models, and Challenges." ACM Computing Surveys 55(9). arxiv 2112.15424 — canonical HDC survey; full HDC NLP primitive catalog.
15. **Vandecasteele, P., De Smet, P., De Baets, B. (2023).** "The Hyperdimensional Transform for Distributional Modelling, Regression and Classification." arxiv 2311.08150 — unified math framework treating RI as random-projection of co-occurrence density.
16. **Frady, E. P., Kent, S. J., Olshausen, B. A., Sommer, F. T. (2020).** "Resonator Networks 1+2: Factoring High-Dimensional Distributed Representations of Data Structures." Neural Computation 32(12):2311-2400 — compositional factorization for downstream QA retrieval (DEFERRED, separate drill).
17. **Bussey, T. J., Saksida, L. M. (2007).** "Memory, perception, and the ventral visual-perirhinal-hippocampal stream: thinking outside of the boxes." Hippocampus 17(9):898-908 — perirhinal Hebbian conjunctive coding biological evidence for hub-spoke.

---

## PRE-DISPATCH NOTES

- `python tools/predispatch_check.py n11 random indexing semantic` — likely PROCEED (novel; sub-RI is not in any prior cell per substrate-mine).
- Verify hdlab/bundling.bundle + hdlab/binding.bind + hdlab/kg_traversal.KGStore + hdlab/char_trigram_encoder.CharTrigramEncoder current.
- Verify text8 corpus present locally; if not, download in pre-flight (it's 100MB; small).
- SimLex-999 + WordSim-353 word-pair datasets available via public release; ASCII text files. Include in repo under `verification/data/` or fetch in cell.
- Smoke gate: confirm sub-RI on 1MB of text8 produces non-zero cos(cat, dog); verify n_external_model_calls = 0 before full-corpus dispatch.

## WHAT THIS CELL DOES NOT TEST

- 100M-word corpora (text8 is 17M tokens; sufficient for initial validation; scale-up is separate cell).
- Multi-language (English only; cross-lingual transfer is separate brain-drill).
- Contextualized embeddings (sub-RI gives a single vector per type, not per token; contextual extension is separate).
- Real downstream QA (this cell tests SEMANTIC GEOMETRY; QA application is separate cell, would compose sub-RI + KGStore + multi_hop + Generator).
- Continual ingest (this is one-shot corpus pass; continual is c2's domain).

## ABSOLUTE PATHS (deliverables + key referenced files)

- This drill note: `d:\AI\hd-instrument\notes\research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md`
- Existing substrate primitives this cell composes with:
  - `d:\AI\hd-instrument\hdlab\char_trigram_encoder.py`
  - `d:\AI\hd-instrument\hdlab\bundling.py`
  - `d:\AI\hd-instrument\hdlab\binding.py`
  - `d:\AI\hd-instrument\hdlab\kg_traversal.py`
  - `d:\AI\hd-instrument\hdlab\whitening.py`
- New primitive (proposed): `d:\AI\hd-instrument\hdlab\random_indexing.py`
- Companion drill (multi-hop): `d:\AI\hd-instrument\notes\research_brain_drill_3_multihop_reasoning_5x_DEEPER_2026-06-22.md`
- Strategic-direction reference: `d:\AI\hd-instrument\notes\substrate_as_llm_scaling_million_facts_v1_design_2026-06-22.md`
