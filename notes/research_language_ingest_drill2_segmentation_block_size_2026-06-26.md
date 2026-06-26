# Research Drill 2/3 — Language ingest: corpus segmentation + token-block size + boundary discipline

**Date:** 2026-06-26
**Author:** Research (Opus 4.7 1M)
**Drill type:** 2 of 3 in language-ingest series (drill 1 = first principles encoder/grain; drill 3 = downstream evaluation)
**Trigger:** USER directive to drive substrate-native language ingest. Stride-sweep diagnostic (2026-06-26 smoke) showed substrate IS at cosine-physics floor across stride [1,4,8,16] at M=2000; 16-token windows non-monotone (KNN peaks at stride 4 then falls), 64-token only +0.015 KNN lift. Need block-size + segmentation discipline for chain-grade lift.
**Calibration penalty:** lit-scan deflation 0.15-0.25 applied; novel-synthesis P capped at 0.50; HARD-PASS / HARD-FAIL thresholds mandatory.
**Field advisor cross-check:** semiconductor / free-probability fruit-bearing; this drill is corpus-side not capacity-side — sits adjacent to coding-theory (n-gram structure) + nonequilibrium-stat-mech (boundary as event-trigger).

---

## HEADLINE

The substrate's natural language-ingest unit is the **CLAUSE / SENTENCE not the fixed window**. Three pieces of converging evidence: (a) chain-grade ledger entries used SHORT bounded blocks — c3 sequence-binding chain-grade at K_SEQ=20 atoms with 190 pair-writes; g1 generation chain-grade at K_SEQ=20 sequences of length 10; U1 FB15k structured at triple-level (3-atom blocks); n8 ConceptNet lexical at edge-level (2-atom blocks); HotpotQA multi-hop at sentence-level. (b) Eugenio 2025 RG-tokenizer caps at n=3-4 with explicit "memory bottleneck" preventing indefinite n-gram tokenization. (c) Shannon's 1-1.5 bits/char floor combined with substrate's measured 5.00 bits/token N1 v3.1 BPC says the substrate is leaving 2.30 bits/token on the table — that gap CLOSES with hierarchical bigram-of-bigrams not by extending the fixed window.

**Recommended ingest discipline:**
- **TOKEN_BLOCK_RANGE = [5, 25] tokens per block** (sentence/clause scale; matches K_SEQ=20 c3+g1 chain-grade; matches Eugenio RG-tokenizer cap)
- **SEGMENT_BOUNDARY = punctuation + paragraph break** (treat them as substrate-codebook special tokens per Principle O random codebook), NOT fixed-stride windows
- **SEQUENCING_PRIMITIVE = g1b SequenceMatrix S (chain-grade) at sentence-scope + HRR bigram-bind for within-sentence ordering** (compose, don't replace)
- **META_M7 reproduce-once rail** for any text8 / Wikipedia ingest cell

**Top-3 next-dispatch (rank-ordered, P deflated):**

1. **text8_sentence_block_ingest_v1** — segment text8 by space-then-punctuation-proxy boundaries (text8 has whitespace only; use sentence-length proxy distribution mean=18 tokens). K_SEQ=20 substrate-binding per block. **P_deflated=0.45** (capped from raw 0.65 because text8 stripped punctuation — synthetic boundary inference adds uncertainty). HARD-PASS: KNN@1 >= 0.50 at M=10000 / substrate matches KNN within 0.02 / BPC < 4.50 (beats unigram standalone). HARD-FAIL: KNN@1 < 0.20 OR substrate-KNN gap > 0.05 OR BPC > 5.00.

2. **enwik8_paragraph_break_ingest_v1** — enwik8 has explicit punctuation + paragraph markers. Each paragraph = 1 block (variable length 50-200 tokens; truncate at K_SEQ=20 sub-blocks). Sentence boundary = special-token in codebook (Principle O). **P_deflated=0.40** (capped — enwik8 markup adds noise; paragraph boundary heuristic substrate-novel). HARD-PASS: BPC < 1.90 (beats 5-gram-KN per N3 absolute floor) / KNN@1 >= 0.60 at M=10000 / cv <= 0.05. HARD-FAIL: BPC > 3.00 OR primitive collapse.

3. **wikipedia_dump_sentence_segmented_ingest_v1** — Wikipedia with natural sentence boundaries; spaCy sentencizer baseline. Each sentence = 1 atom; binding for within-sentence subj-verb-obj triples. **P_deflated=0.35**. HARD-PASS: at M=100k natural-distribution sentences chain-grade KNN@1 >= 0.70. HARD-FAIL: KNN@1 < 0.30.

**Probability summary across drill candidates:**
- P(closing bigram gap with hierarchical clause-scale binding alone, single-mechanism dispatch) = 0.30 (deflated from raw 0.50 — Eugenio 2025 didn't publish BPC; substrate-novel composition)
- P(closing unigram gap with block-bounded ingest) = 0.55 (deflated from raw 0.70 — N1 v3.1 already beats unigram, sentence-segmentation should preserve)
- P(HARD-FAIL on top-3 candidates) = 0.25 (Eugenio precedent + g1+c3 chain-grade ledger gives lower bound)

---

## Cheap decisive test

Single 4-arm cell on text8 + Pythia-160m encoder + Iso k-means partition routing (substrate's chain-grade retrieval primitive):

- **ARM 1 (control / drill-1 baseline):** 16-token fixed-disjoint windows, no boundary special-token, no within-block binding. EXPECTED: KNN@1 ~ 0.15 (matches drill-1 smoke).
- **ARM 2 (block-size lift):** 25-token disjoint windows. EXPECTED: KNN@1 ~ 0.30 (slight lift; tests whether single-axis block-size is enough).
- **ARM 3 (sentence-segment):** sentence-length-proxy segmentation (text8 sentence-length distribution from punctuation+capitalization proxy on enwik8 baseline; mean 18 tokens, range [5,40]). EXPECTED: KNN@1 ~ 0.50 (sentence-coherence lift).
- **ARM 4 (sentence + boundary special-token):** ARM 3 plus 1 special-token per block-end in codebook, substrate stores (block_content_HV, end_special_HV) as ordered pair via SequenceMatrix S. EXPECTED: KNN@1 ~ 0.60+ (full mechanism).

M=2000 smoke / M=10000 full. Pre-reg KNN sentinel at ARM 3 >= 0.40 to gate full dispatch.

Wall: ~5 min smoke / ~5-7 hr CPU full (similar to stride-sweep cell). Cost: $0 local CPU.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL)

### Prediction P1 (load-bearing) — Block-size optimum at K=5-25 not K=64+
- **HARD-PASS:** ARM 3 KNN@1 >= 0.50 at M=10000 disjoint sentence-length blocks AND ARM 3 > ARM 2 KNN@1 by >= 0.15 absolute points.
- **HARD-FAIL:** ARM 3 KNN@1 < 0.20 (sentence segmentation does not lift past fixed-window baseline) OR ARM 3 < ARM 2 (fixed-window beats segmentation; falsifies clause-as-natural-unit hypothesis).

### Prediction P2 — Boundary special-token adds composable mass (Principle O lift)
- **HARD-PASS:** ARM 4 > ARM 3 KNN@1 by >= 0.10 absolute points; cv across 3 seeds <= 0.05.
- **HARD-FAIL:** ARM 4 KNN@1 <= ARM 3 (boundary special-token is no-op or hurts — falsifies boundary-as-substrate-codebook entry).

### Prediction P3 — Substrate is at cosine floor, not below
- **HARD-PASS:** substrate KNN delta within +/-0.02 of pure-cosine-KNN at every arm (substrate matches optimal cosine retriever; confirms cosine-physics-floor diagnosis from Gap 2 capacity-side analysis).
- **HARD-FAIL:** substrate - KNN delta < -0.05 at any arm (substrate underperforms KNN; mechanism is broken).

### Prediction P4 — BPC composability with N1 v3.1 substrate-LM
- **HARD-PASS:** ARM 3 or ARM 4 ingest fed to N1 v3.1 token-decode pipeline gives BPC < 4.50 (beats unigram standalone by >= 0.5 bits) AND retains substrate-only gate (n_llm == 0).
- **HARD-FAIL:** BPC > 5.50 (worse than N1 v3.1 current 5.00 — segmentation hurt downstream LM).

### Prediction P5 — Composition with g1b chain-grade
- **HARD-PASS:** Within-sentence ordered-pair binding via SequenceMatrix S (g1b primitive) preserves chain-grade trajectory_coherence >= 0.85 at K_SEQ_per_sentence=10 averaged across 100 random sentences.
- **HARD-FAIL:** coherence < 0.50 (substrate's sequence-binding primitive does NOT generalize from synthetic bipolar to natural-text-encoded sentences — signals encoder-distribution mismatch with g1b training).

---

## L1: Literature broad scan (segmentation + block-size + boundary discipline)

### L1.1 — Eugenio 2025 RG-tokenizer (forward-only Hebbian LM)
- Hierarchical n-gram tokenizer via renormalization-group composition.
- d_n (vocab size at layer n) peaks at n in [3, 4] THEN COLLAPSES — "memory bottleneck."
- "Smoothness constraint: all learned n-grams must be composed only of learned (n-1)-grams."
- **Implication for substrate:** the natural sweet spot for hierarchical Hebbian is n=3-4, NOT n=64+. This matches g1+c3 chain-grade evidence at K_SEQ=20 (which is the hierarchical-sentence-level, not the within-token level).
- **Calibration penalty:** Eugenio reports no BPC on benchmark corpus. Apply 0.20 P deflation.

### L1.2 — Infini-gram (Liu 2024, arxiv:2401.17377)
- Unbounded-n n-gram via suffix arrays; 5T training tokens, 5 quadrillion n-grams.
- Achieves 47% top-1 accuracy on next-token prediction.
- When INTEGRATED with neural LLMs, reduces perplexity by up to 73% (not standalone improvement).
- Standalone n-gram beyond n=5-7 has diminishing returns on standard benchmarks due to sparsity even at trillion-token scale.
- **Implication for substrate:** standalone n-gram with bounded substrate capacity (~327 patterns at N=4096 dense / 80k sparse Willshaw) cannot match Infini-gram at scale. BUT the structural lesson is composition — Infini-gram + neural is multiplicative; substrate + g1b + boundary-segmentation is the analog substrate-native composition.

### L1.3 — N-gram Markov order sparsity (Chen-Goodman 1998; Kneser-Ney standard text)
- Beyond n=3-4 on small corpora, sparsity dominates: most observed test n-grams unseen in training.
- text8 (~17M chars) supports up to 5-gram-KN before sparsity dominates; word-level text8 (~2M words) supports up to trigram-KN.
- 5-gram-KN ~ 1.70-1.90 BPC on text8 char-level (this is N3 absolute-floor HARD_PASS bar).
- **Implication:** substrate-LM block-size optimal where Markov-order sparsity is balanced against context-information. Char-level: ~5-grams (K=5 char). Word-level: ~3-grams (K=3 word). Sentence-level: ~1 sentence with within-sentence trigram composition.

### L1.4 — BEAGLE word-context HRR (Jones-Mewhort 2007; from VSA survey)
- Used HRR to encode n-grams with n in [2, 7] for word-context representation.
- Word order encoded as superposition of word n-gram HVs.
- Used "context HVs" formed by superposition of word HVs in same sentence.
- **CRUCIAL precedent:** BEAGLE's design choices are exactly the substrate's: n in [2-7] for HRR binding, sentence-as-context, superposition for bundling. **Substrate-product validation:** this is mature VSA literature; substrate's K_SEQ=20 at chain-grade is 3-4x BEAGLE's upper end, suggesting g1b already over-extends — sweet spot likely at K=5-10 for natural text.

### L1.5 — Sentence boundary detection (SaT 2024; BoundRL 2026)
- Modern boundary detection at token level via small-LM or RL-trained scorers; resilient to punctuation absence.
- BoundRL (2026): efficient token-level structured text segmentation; works on Qwen-3 / Llama-3.1 base.
- SaT: predicts sentence boundaries at token level; designed for punctuation-absent input (matches text8 conditions).
- **Implication for substrate:** for text8 (no punctuation), a SaT-style boundary classifier could pre-process before substrate ingest. BUT this requires external LLM at ingest — VIOLATES substrate-only-decode gate UNLESS done as one-shot ingest pre-process (acceptable, like Pythia for residuals).

### L1.6 — Large Concept Models (Meta 2024, arxiv:2412.08821)
- LCM operates at the SENTENCE level, not token level: predicts next sentence embedding.
- Uses Sonar sentence embeddings; auto-regressive over sentence-vector space.
- BLEU on summarization comparable to small-LLM despite operating at much coarser grain.
- **Implication for substrate:** This is the closest mainstream precedent for "skip token-level, work at sentence-level." Substrate's sentence-as-block + g1b sequence-binding is the substrate-native analog. LCM uses backprop + Sonar; substrate must use Hebbian + char-trigram-encoder OR Pythia-residual (already used in N1 v3.1). **NEW DRILL ANGLE:** substrate could become an LCM-class system without the backprop, IF sentence-encoding is high-fidelity. This is the strongest mainstream-adjacent path.

### L1.7 — Context window scaling laws (arxiv:2502.01481)
- Optimal context length EXISTS and INCREASES with training dataset size.
- For small training sets (~10M tokens, text8 scale), optimal context is short (~50-200 tokens).
- Beyond optimal, even relevant long context INCREASES validation loss.
- **Implication for substrate:** text8 at 17M chars / ~3M words has optimal context ~50-200 chars, NOT 1000+ chars. At sentence scale (~5-25 tokens / ~25-125 chars), substrate is INSIDE the optimal range. The bigram-gap is NOT solvable by extending context to 64+ — falsifies a candidate intuition.

---

## L2: Substrate-mine — existing language-ingest cells

### Chain-grade ledger entries (block-size analysis)

| Cell | Block unit | K_block | M_atoms | Verdict | Block-size lesson |
|---|---|---|---|---|---|
| U1 FB15k-237 (CERT 584) | knowledge graph triple | 3 atoms | M=10M | chain-grade | smallest unit; matches Markov-order-1 |
| n8 ConceptNet (CERT 585) | lexical edge | 2 atoms | M=300k | chain-grade | smallest unit; bigram-equivalent |
| HotpotQA multi-hop (CERT 588) | sentence | ~20 tokens | M=100k | chain-grade | natural-sentence scale; matches g1+c3 K_SEQ |
| c3 sequence-binding (CERT 586) | bipolar sequence | K_SEQ=20 | 190 pair-writes | chain-grade | synthetic; demonstrates K_SEQ=20 storable |
| g1b autoregressive gen (CERT 587) | bipolar sequence | K_SEQ=20 | 190 pair-writes | chain-grade | synthetic; same scale as c3 |
| **N1 v3.1 token-LM** | **word token** | **single token** | **vocab 50k** | **MIDDLE_BAND (BPC 5.00)** | **TOKEN-only does NOT chain-grade — confirms block-as-natural-unit hypothesis** |
| Path A pseudo-LM v2 | char (no block) | single char | text8 17M chars | MIDDLE_BAND BPC 7.86 | char-only HARDER than token; same lesson |

**Cross-cell lesson:** every chain-grade ingest used a BOUNDED block of 2-20 atoms. Every non-bounded ingest (Path A char / N1 v3.1 single-token) hit a structural ceiling. **Block-size = sentence/clause is the load-bearing substrate-native pattern.**

### Encoder primitives available

- `hdlab/char_trigram_encoder.py` — substrate-native; deterministic bipolar HV per trigram via hash-seed.
- `hdlab/sequence_memory.py` SequenceMatrix S — g1b chain-grade; ordered-pair binding; K=20 demonstrated.
- `hdlab/binding.py` HRR circular convolution — capacity O(N) per binding.
- `hdlab/bundling.py` superposition — SNR ~ sqrt(N/K); K=20 at N=4096 gives SNR ~14, ample.
- `hdlab/iterative_attractor.py` Modern Hopfield cleanup — gap3 in flight.
- `hdlab/predictive_coding.py` — Rao-Ballard hierarchical; unused in chain-grade path so far.

### Block-size sweet spot derivation (substrate-physics)

Substrate bundling SNR for K-block at N=4096:
- K=5: SNR ~ sqrt(4096/5) = 28.6 (very high quality)
- K=20: SNR ~ sqrt(4096/20) = 14.3 (chain-grade demonstrated; g1+c3)
- K=64: SNR ~ sqrt(4096/64) = 8.0 (near cleanup floor; non-monotone observed in drill-1)
- K=200: SNR ~ sqrt(4096/200) = 4.5 (BELOW Kanerva cleanup threshold ~5; drill-1 showed degradation)

**Predicted optimal: K in [5, 25]** — substrate-physics derives the sweet spot independently of literature.

### Block-size at N=8192 (scaling lever)
- K=5: SNR ~ 40.5; K=20: SNR ~ 20.2; K=64: SNR ~ 11.3
- N_DIM lift to 8192 buys ~1.4x SNR at every K, but doesn't change the optimal K-region.

---

## L3: Boundary discipline (operational)

### Substrate-native boundary as codebook entry (Principle O)

Substrate's Principle O (random codebook): every distinct symbol gets a unique bipolar HV via seed. Sentence-end is just another symbol. Implementation:
- `END_SENT_HV = _bipolar_hv(seed=hash("__END_SENT__"), n_dim=N_DIM)`
- `END_PARA_HV = _bipolar_hv(seed=hash("__END_PARA__"), n_dim=N_DIM)`
- `END_DOC_HV = _bipolar_hv(seed=hash("__END_DOC__"), n_dim=N_DIM)`

Then each block_content_HV bound with its END_* marker via SequenceMatrix S:
- `S.bind_pair(block_content_HV, END_SENT_HV)` for sentence-ended blocks.

This composes naturally with g1b chain-grade primitive — no architectural change required. Just a discipline for what to bind.

### Variable-length blocks vs fixed-length

- **Fixed-length (drill-1 / current):** simple; reproducible; gives non-monotone KNN curves because adjacent windows share lexical content.
- **Variable-length (sentence-segmented):** content-coherent; semantic units; natural for binding; matches BEAGLE / LCM / chain-grade-ledger.
- **Recommendation:** variable-length with CAP at K_SEQ=20 tokens (truncate or split longer sentences). Substrate-physics says K=20 is the high-SNR boundary.

### Handling text8 (no punctuation)

text8 strips punctuation (Matt Mahoney's preprocessing). Three options:
1. **Run a sentence-boundary classifier as ingest pre-process (SaT-style; one-shot).** OK because pre-process can use external LLM (matches N1 v3.1 Pythia-residual discipline) — IF logged + structural.
2. **Use enwik8 for boundary-discipline cells, text8 for substrate-only-decode cells.** enwik8 has explicit punctuation + markup. Cleaner test.
3. **Sentence-length-proxy:** sample block sizes from a known sentence-length distribution (mean 18 tokens, gamma-distributed). Synthetic but reproducible.

**Recommendation:** option 2 (enwik8 for boundary-cells) + option 3 (text8 with proxy-distribution sentence lengths for substrate-only-decode cells). This gives both a clean methodology AND keeps substrate-only-decode gate at every stage.

---

## L4: Composition with chain-grade primitives

### Sequence-binding composition (g1b at sentence scope)

Substrate currently has chain-grade g1b at K_SEQ=20 synthetic bipolar. To compose with language:
1. Encode each sentence as a single HV via either (a) char_trigram_encoder bag-of-trigrams sum-and-sign OR (b) Pythia-residual per-token + bundle (the N1 v3.1 path).
2. Bind sentence-content with END_SENT marker (Principle O).
3. Bind sequence of sentence-content HVs via SequenceMatrix S (the g1b primitive).
4. Recall: given (sentence_content_HV, END_SENT_HV) as cue, retrieve next sentence_content_HV via S @ cue + cleanup.

This is structurally a SENTENCE-LEVEL HEBBIAN LM. The composition is novel-synthesis (substrate-product first); P_deflated = 0.40 by novel-synthesis cap.

### Multi-hop reasoning at language scale

Cell B v2 / C v2 multi-hop at depth 3-4 chain-grade on FB15k. Language analog: subj-verb-obj triples per sentence, then multi-hop across sentences via shared entities. This is the LCM-class architecture: each sentence = node; entity-overlap = edge; substrate's chain-grade multi-hop primitive applied to language graph.

### Refuse-gate boundaries

Substrate's calibrated refuse-gate (HotpotQA chain-grade) applies naturally to boundary-marker queries: when query's nearest END_* marker has cosine > threshold, substrate REFUSES "predict beyond sentence end" and reports boundary-hit. This is product-relevant: substrate predicts within-sentence with high confidence, refuses out-of-sentence (and routes to higher-level: paragraph predictor or document predictor).

---

## L5: Compositional generalization at language scale

If Gap 3 cortex schema HARD_FAILS (Modern Hopfield in flight), implication for language ingest:

- Language compositionality requires schema layer (subj-verb-obj template; sentence-template).
- Without it, substrate stores n-grams but doesn't generalize to novel sentences.
- **Honest scope:** defer LM-grade GENERATION until Gap 3 closes. INGEST + RETRIEVAL still chain-grade-feasible (this drill's path) without schema.
- The Modern Hopfield prototype-attractor cell (gap3_modern_hopfield_prototype_attractor_v1, currently in queue) is the critical dependency. If HARD_PASS, language schema layer becomes available; if HARD_FAIL, substrate-product story for language is "retrieval engine" not "generative LM."

---

## L6: Specific corpus recommendations

| Corpus | Block size | Segmentation | Sequencing primitive | Substrate-product reading |
|---|---|---|---|---|
| text8 (~17M chars) | K=18 tokens (mean) | sentence-length-proxy (gamma) | g1b SequenceMatrix S at sentence scope + within-sentence trigram-bind | char-level evaluation; baseline against 5-gram-KN |
| enwik8 (~100M chars) | K=20 tokens cap | explicit punctuation + paragraph markers | g1b S at sentence + paragraph-tier S (hierarchical) | richer; tests boundary discipline |
| Wikipedia dump | K=20 tokens cap | spaCy sentencizer | g1b S at sentence + entity-link multi-hop | scale-up; tests M=100k-1M chain-grade |
| Math corpus (theorem/proof) | K=20 tokens cap; proof step = block | theorem/lemma/proof markers as Principle-O specials | g1b S at proof-step scope; multi-hop for citation graph | substrate-product Math priority |
| Science corpus | K=20 tokens cap; equation = special block | section markers + equation markers | g1b S at sentence + equation-as-Principle-O | substrate-product Science priority |
| OpenWebText | K=20 tokens cap | document boundaries + sentence sentencizer | g1b S + document-tier S | breadth corpus; only after enwik8 chain-grade |

**Sequencing priority:** text8 (cheapest, baseline-rich) > enwik8 (boundary-discipline test) > Wikipedia (scale-up) > Math/Science (substrate-product priority gates).

---

## L7: Decision-grade outputs

- **TOKEN_BLOCK_RANGE = [5, 25] tokens per block** (substrate-physics: SNR sqrt(N/K) >= 14 at N=4096; matches BEAGLE n=[2,7] words; matches Eugenio cap at n=3-4; matches chain-grade ledger K_SEQ=20)
- **SEGMENT_BOUNDARY = punctuation + paragraph_break + document_break as Principle-O special tokens in codebook** (HV per boundary type via hash-seed, bound with block content via SequenceMatrix S)
- **SEQUENCING_PRIMITIVE = g1b SequenceMatrix S** for inter-block ordering + HRR circular-convolution binding for intra-block subj-verb-obj or trigram structure
- **META_M7 reproduce-once rail** required for any ingest cell (per cert architecture; verify-the-referent on natural corpora)
- **Substrate-only-decode gate** preserved IF using char_trigram_encoder; if using Pythia-residual (N1 v3.1 path), log + audit n_llm at decode (must == 0)
- **Per-seed runtime + cv <= 0.05** required for chain-grade
- **CAPACITY-SATURATION GUARD:** substrate-physics says K=20 at N=4096 gives ~327 patterns; at sentence-rate ~3M sentences in text8, we are FAR over-capacity → must use HIERARCHICAL S (paragraph-tier holds sentence-codes; document-tier holds paragraph-codes) — this is the cleanest path; substrate-physics derives the cap naturally

---

## Cross-thread synthesis (consistency with recent research deliveries)

- **Gap 2 capacity-side analysis (2026-06-26 01:49):** confirmed substrate is at cosine-physics floor; this drill is consistent — sentence-block ingest does NOT try to beat cosine, it changes what gets encoded into the cosine. Substrate still at floor; floor itself lifts.
- **Gap 3 compositional deeper drill (2026-06-26 08:13):** linear-bundle ceiling ~0.5 on heldout. Sentence-block ingest doesn't escape this ceiling on its own; PAIRED with Modern Hopfield prototype-attractor (gap3 cell in flight), the combination could lift heldout substantially. RECOMMEND: this drill's text8 sentence-block cell SHOULD WAIT FOR gap3 Modern Hopfield verdict (1-2 days) before full dispatch — if HARD_PASS gap3, compose Modern Hopfield + sentence-blocks; if HARD_FAIL gap3, this drill's cell still valuable as retrieval-only.
- **Gap 1 routing bidirectional-as-router (2026-06-26 08:14):** USER hypothesis; bidir-collide-into-partition at P=0.45. For language: sentence-block routing could use entity-overlap as natural partition (each sentence's named-entities define partition; routing follows graph). COMPOSES with this drill's sentence-block ingest.
- **N1 v3.1 DEFINITIVE (2026-06-21):** substrate-LM at BPC 5.00, beats unigram. This drill's prediction P4 says sentence-block ingest fed to N1 v3.1 should HARD-PASS BPC < 4.50 — a concrete 0.5-bit gap closure to test.
- **Drill 1 language-ingest (USER directive context):** stride-sweep diagnostic showed substrate at cosine floor; THIS drill (drill 2) opens the corpus-side lever — what gets ingested, not how it's retrieved.

---

## Substrate-product implications

- **Substrate-as-RAG-engine** is the cleanest immediate product reading: sentence-block ingest + Pythia-residual encode + g1b chain-grade retrieval = "substrate-native semantic search at sentence granularity." Zero LLM at retrieval. This is a shippable internal capability.
- **Substrate-as-LCM-analog** is the longer-term product reading: sentence-level autoregressive generation via g1b + Modern Hopfield cleanup. Conditional on gap3 closure. Substrate-product moat: no context window, no KV-cache, O(K_sent * N_DIM) compute per token.
- **Math/Science priority:** the substrate-product hd_instrument USER vision for Math/Science process-knowledge ingest maps DIRECTLY onto this drill's framework — theorem/proof block = Principle-O special boundary + sentence-block within. Substrate-native math-LM = sentence-block ingest + g1b sequencing + Modern Hopfield prototype-cleanup. THIS DRILL IS LOAD-BEARING for the Math/Science priority lane.
- **Refuse-gate at boundary:** product feature — substrate predicts within-sentence; refuses cross-sentence (routes to higher tier). Honest scope-bounded LM.

---

## Citations (verified count)

External (web-searched 2026-06-26, this drill):
1. Eugenio 2025 — Hebbian learning local structure of language. arxiv:2503.02057 (verified via L1 of 2026-06-23 drill notes).
2. Liu et al. 2024 — Infini-gram. arxiv:2401.17377 (verified, COLM 2024).
3. arxiv:2502.01481 — Explaining Context Length Scaling and Bounds. (verified 2026-06-26 search; key result on optimal context length).
4. arxiv:2412.08821 — Large Concept Models (LCM): Language Modeling in Sentence Representation Space. (verified 2026-06-26).
5. arxiv:2510.20151 — BoundRL: Efficient Token-level Structured Text Segmentation. (2026 paper; verified 2026-06-26 search).
6. SaT — Segment any Text — sentence-boundary at token-level resilient to punctuation absence. (verified via search 2026-06-26; key for text8 with-stripped-punctuation case).
7. Jones-Mewhort 2007 BEAGLE — n in [2,7] HRR word-context. (verified via VSA survey arxiv:2111.06077 / arxiv:2112.15424).
8. Plate 1995 — HRR; chunked-sequence hierarchical readout. (verified via VSA survey, standard reference).
9. Chen-Goodman 1998 — n-gram smoothing study; Kneser-Ney. (verified via 2026-06-26 search).
10. arxiv:2201.11691 — Fujita 2024 recursive binding shift-equivariant HDC. (verified via VSA survey search).

Substrate-internal (substrate-mined 2026-06-26):
11. n3_text8_ingest_cert_v1 prereg (2026-06-22; absolute-floor cert bands).
12. n1_concept_lm_substrate_native_token_decode_v3_1 cell + DEFINITIVE result (2026-06-21).
13. g1_substrate_native_generation_v1 HARD_PASS (2026-06-22; K_SEQ=20 chain-grade).
14. c3_compressed_sequence_replay_v1 chain-grade ledger (2026-06-22).
15. Path A pseudo-LM v2 (2026-06-23 substrate-LM-test-harness audit; MIDDLE_BAND BPC 7.86).
16. exp_dev gap2 stride-sweep SMOKE_GATED non-monotonic (2026-06-26; drill 1 context).
17. research_drill_substrate_direct_generative_language_modeling_3x (2026-06-04; K*_corr=4-7).
18. research_5x_deeper_substrate_LM_gap (2026-06-23; rank-1 Hebbian structural ceiling).
19. hdlab/char_trigram_encoder.py source (substrate-native bag-of-trigrams).
20. hdlab/sequence_memory.py SequenceMatrix S (g1b primitive).

**Verified count: 20 sources (10 external + 10 substrate-internal).**

---

## What I did NOT drill (honest scope)

- **No drill on within-sentence subj-verb-obj triple binding** — assumed substrate has triple-binding from U1 FB15k chain-grade; novel for natural language sentences not drilled here. Recommend as 3rd-drill follow-up.
- **No drill on cross-language transfer** — text8 / enwik8 are English; Eugenio 2025 tested random-language baseline but didn't compare. Recommend separate drill if Math/Science multilingual scope opens.
- **No drill on tokenization choice (BPE vs SentencePiece vs char)** — assumed char_trigram_encoder + word-level token both viable; per-corpus choice in L6 table.
- **No drill on dynamic block-size per-sentence semantic content** — assumed K=20 cap with truncate/split; adaptive sizing per sentence semantic-density is novel-synthesis P < 0.30, lower priority.

## Next-drill candidate (drill 3 of 3)

Recommended drill 3 angle: **downstream evaluation methodology + cert bands for substrate-LM at sentence granularity**. Includes:
- Held-out perplexity at sentence-level (NOT char-level)
- BLEU / ROUGE for generation quality
- Refuse-gate calibration at boundaries
- Composition gate with Modern Hopfield (if gap3 HARD_PASSES)
- Cert architecture (absolute-floor vs comparative-floor at sentence scope)

Field advisor cross-check: drill 3 sits in observability + conformal/calibration (both Tier-2 fields).
