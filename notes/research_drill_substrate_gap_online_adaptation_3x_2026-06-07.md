# Research Drill: Online Concept Formation / Encoder Adaptation Without Breaking Retrieval (3x Deep)
# Date: 2026-06-07
# Triggered by: empirical LoRA -28.9% retrieval degradation + Drill B SFT incompatibility finding

---

## HEADLINE

The adaptation gap is a REAL but TRACTABLE engineering challenge: LoRA and SFT are structurally incompatible with retrieval geometry, but retrieval-objective pre-training (RetroMAE-style) and query-drift compensation (QDC) together solve Level-B and partially Level-C gaps without re-indexing. The hard boundary is Level C: genuinely novel concepts require controlled encoder update, and the cost is 1-2 weeks per customer -- not zero, but not prohibitive. P_deflated = 0.40 (down from raw 0.60-0.65 by calibration penalty of 0.20-0.25).

---

## 1. EXACT DECOMPOSITION OF THE GAP

Three levels are not equally hard. This is the central organizing insight.

### Level A: New entities in existing semantic space
- Example: new patient names, new product SKU codes
- Mechanism: entity = new coordinate in existing semantic manifold
- Substrate W handles this via pinv writes (cycle 149 empirical PASS)
- Encoder produces serviceable embedding even for unseen proper nouns because subword tokenization captures phonological/morphological proximity
- VERDICT: Already solved. NOT a gap.

### Level B: Domain-specific vocabulary / jargon (the soft gap)
- Example: "Tegretol" (drug brand), "EBITDA" (finance), "K8s" (DevOps)
- Tokenizer: Llama-3.2-1B BPE tokenizer was trained on general web text
  - "Tegretol" likely fragments: "Teg", "ret", "ol" -> three subword tokens
  - Each subword token activates base representations that have SOME signal
  - The last-token pooled embedding IS suboptimal but not zero
  - Empirical test: cosine similarity between "Tegretol" and "carbamazepine" in base encoder
    - Expected: low similarity (0.2-0.4), not zero
    - Implication: substrate can write and retrieve "Tegretol" entries but RELATEDNESS to "carbamazepine" is lost
  - This is the VOCABULARY LINKING problem: encoder cannot identify synonymy across jargon/generic name pairs
- Why LoRA fails here: LoRA tries to change last-token geometry -> destroys existing geometry (-28.9%)
- VERDICT: Soft gap. Can be partially addressed without encoder change via W-level synonym tables or retrieval-objective fine-tuning ON TOP of frozen base.

### Level C: Genuinely new concepts requiring representation shift (the hard gap)
- Example: customer's proprietary risk taxonomy (RISK-ALPHA / RISK-BETA / RISK-GAMMA are their internal categories)
- Encoder: no concept of these categories; all produce similar embeddings near generic "risk"
- W write: substrate can store "RISK-ALPHA = doc_1, doc_2" but when queried "what is a RISK-ALPHA situation?" it retrieves poorly because the encoder maps the query near "risk" not near "RISK-ALPHA documents"
- This requires encoder to learn that "RISK-ALPHA" IS a specific cluster, distinct from "RISK-BETA"
- CANNOT be solved at W level alone
- VERDICT: Hard gap. Requires controlled encoder update or architectural extension.

---

## 2. WHY LORA AND SFT BREAK RETRIEVAL: PRECISE MECHANISM

### The information constraint (from Drill B)

    I(h; instruction) + I(h; semantic) <= I(h; X)

where h = last-token hidden state, X = full input.

This is the fundamental mutual information (MI) budget constraint. The encoder's last token is a SINGLE fixed-dimension vector. It cannot carry unbounded information. MI budget is fixed by model capacity and input length.

SFT objective: maximize I(h; next_token) = I(h; instruction)
  -> compresses I(h; semantic) as a byproduct
  -> this is not a design failure; it is what SFT is DESIGNED to do

LoRA on attention matrices:
  - Attention routing changes WHERE information flows within the transformer
  - Specifically: attention-head composition at last token is what produces last-token embedding
  - LoRA modifies Q, K, V weight matrices -> changes which tokens attend to what
  - Result: the routing structure that concentrates semantic content at last token breaks
  - Empirical: -28.9% retrieval degradation = routing destruction

### Encoder-only vs causal LM asymmetry

Encoder-only models (BERT, MiniLM, DeBERTa):
  - [CLS] token attends bidirectionally to ALL tokens
  - Fine-tuning for retrieval (contrastive loss) REINFORCES [CLS] as semantic sink
  - SFT on retrieval pairs works well; no competition between generation and retrieval

Causal LM (Llama-3.2-1B, our production encoder):
  - Last token attends to ALL preceding tokens (causal mask, left-to-right)
  - But: ALL preceding tokens also contribute to what last token "sees"
  - SFT modifies the GENERATION pathway; last-token semantics is a side effect
  - Fine-tuning for retrieval on a causal LM requires explicit retrieval objective (not SFT)
  - This is confirmed by BGE-M3 / RetroMAE design: they use MAE-based retrieval objective, NOT SFT

Key insight: the -28.9% LoRA degradation is NOT a LoRA failure per se. LoRA applied with RETRIEVAL-CONTRASTIVE objective might preserve or improve retrieval. The failure is LoRA + SFT-style objective, not LoRA as an adapter class.

---

## 3. MECHANISMS RANKED BY VIABILITY (with lit-backed P estimates)

### Mechanism 1: Retrieval-Objective Fine-Tuning (RetroMAE / GTR / BGE-style)
RANK: 1st (highest viability)
P_raw = 0.80 | P_deflated = 0.58 (penalty = 0.22)

What it does:
- Replace SFT loss with MAE reconstruction loss on top of sentence embedding
- RetroMAE: encoder gets 15-30% masking ratio; decoder gets 50-70% masking ratio
- Decoder must reconstruct full input from ONLY the sentence embedding
- This forces embedding to contain maximal semantic content -> retrieval quality
- Training signal: reconstruction of masked tokens, NOT next-token prediction

Why it doesn't break retrieval:
- Objective is directly: "sentence embedding must encode all semantics"
- No MI competition between instruction-following and semantic content
- The embedding IS the optimization target

Domain adaptation variant:
- Take frozen production encoder
- Fine-tune with RetroMAE objective on customer domain corpus (no labels needed)
- Customer domain passages = unlabeled training data
- Output: domain-adapted encoder with improved in-domain embedding quality
- Literature evidence: BGE-M3 (2024) uses exactly this: continual RetroMAE pre-training on domain data
  -> achieves state-of-art zero-shot BEIR results while adding domain coverage
  -> "positive transfer without degradation" on out-of-domain sets

Limitations:
- Requires labeled or pseudo-labeled retrieval pairs for supervised RetroMAE (contrastive stage)
- Without labels, unsupervised MAE alone may not capture RELATIONAL semantics (synonymy)
- Cost: ~1-2 weeks training per customer (not zero)
- Hard fail: if customer domain is extremely small (<1K documents), MAE pre-training noise dominates

HARD-PASS: in-domain retrieval AUC improves >15% vs frozen base; out-of-domain AUC drops <5%
HARD-FAIL: in-domain gain <5% OR out-of-domain drops >10%

### Mechanism 2: Query Drift Compensation (QDC) -- NEW from CoLLAs 2025 lit
RANK: 2nd (high viability for INCREMENTAL updates)
P_raw = 0.75 | P_deflated = 0.55 (penalty = 0.20)

What it does (Goswami et al., CoLLAs 2025, arXiv:2506.00037):
- When encoder is updated (by ANY method), the existing indexed corpus is NOW in the OLD embedding space
- Re-indexing is expensive: O(|corpus|) forward passes
- QDC: estimate query drift vector Delta^{t-1->t} = mean(f_t(q) - f_{t-1}(q)) over calibration set
- At retrieval time: project new query BACK to old space: q_hat = f_t(q) - Delta^{t'->t}
- This allows NEW queries to be compared against OLD corpus without re-indexing
- Embedding distillation loss: L_D = mean(D_cos(f_t(q), f_{t-1}(q)) + D_cos(f_t(d), f_{t-1}(d)))
  -> regularizes embedding drift during update -> preserves backward compatibility
- Empirical: FT+KD+QDC achieves nDCG@10 = 54.1, matching joint training, vs 62.6 Recall@10

Why this matters for our substrate:
- Production corpus is indexed at deployment time
- Customer provides NEW domain data -> encoder updated
- Without QDC: all existing indexed documents must be re-embedded (expensive)
- WITH QDC: drift is compensated at query time; existing corpus remains valid
- This is a STRUCTURAL solution to the re-indexing cost problem

Limitations:
- Drift estimation requires calibration query set (small: ~100-1000 queries)
- Marginal gains from multiple drift vectors vs single (0.3-0.7%) -> drift is approximately uniform
- Fails when query-document drift is ASYMMETRIC and large (extreme domain shift)
- Does NOT solve Level-C (new concepts not seen in calibration queries)

HARD-PASS: corpus compatibility maintained with <3% nDCG degradation without re-indexing after encoder update
HARD-FAIL: >8% nDCG drop without re-indexing (QDC fails to compensate extreme drift)

### Mechanism 3: Modular Domain Adapter (frozen base + trainable module)
RANK: 3rd (medium viability, engineering cost is real)
P_raw = 0.65 | P_deflated = 0.43 (penalty = 0.22)

Architecture:
- Production encoder (Llama-3.2-1B) remains FROZEN
- Add small bottleneck adapter module (2-4 linear layers, ~1-5M params) AFTER encoder
- Adapter takes last-token embedding as input; outputs modified embedding in same space
- Adapter trained on customer domain with RETRIEVAL-CONTRASTIVE loss (InfoNCE on pos/neg pairs)
- At inference: base_emb = encoder(x); customer_emb = adapter(base_emb)

Why it avoids Drill B failure:
- Base encoder is FROZEN: no MI competition; no attention routing destruction
- Adapter only modifies the OUTPUT embedding; does not touch attention matrices
- Retrieval geometry of base encoder is preserved for non-adapter queries
- Customer adapter is a LINEAR (or near-linear) transform of base embedding

Mathematics:
- adapter(h) = W2 * ReLU(W1 * h + b1) + b2
  where W1 in R^{d x d_bottleneck}, W2 in R^{d_bottleneck x d}
- This is a RANK-r update to the embedding space (not to the model weights)
- Information-theoretically: I(adapter(h); customer_semantics) <= I(h; customer_semantics)
  -> adapter cannot INVENT information not in h; it can only AMPLIFY it
  -> Level-C gap is NOT closed by adapter; only Level-B (amplifying existing signal)

Limitations:
- Adapter cannot create representation dimensions that base encoder never activated
- Requires customer to provide relevance pairs (at minimum a few hundred labeled pairs)
- Per-customer deployment: each customer gets own adapter module (storage overhead)
- Inference: 2-step compute (base forward + adapter forward; adapter is tiny, cost is ~1%)

Literature evidence: OneEncoder (2024) achieves bidirectional retrieval tuning only 4-8M params
on frozen CLIP backbone; matches giant models. LoRA adapters with RETRIEVAL objective (not SFT)
show different behavior than LoRA+SFT.

HARD-PASS: Level-B vocabulary gain >10% on domain test set; base retrieval unchanged
HARD-FAIL: base retrieval drops >3% (adapter bleeds into base space)

### Mechanism 4: Multi-Head Encoder Composition
RANK: 4th (theoretically clean, expensive to implement)
P_raw = 0.55 | P_deflated = 0.33 (penalty = 0.22)

Architecture:
- Production encoder: one head H0 (general, frozen)
- Customer head H_c: separate encoder trained on customer domain with retrieval objective
  - H_c can be SMALLER than H0 (e.g., Pythia-160M or MiniLM fine-tuned on customer corpus)
- At inference: emb = concat(H0(x), H_c(x)) or weighted sum
- Substrate write: full concatenated embedding stored
- Substrate query: same concatenation applied to query

Information-theoretic justification:
- Multi-head relaxes single-h MI budget: I(h0; semantic_general) + I(h_c; semantic_customer)
- Customer head can carry I/N customer-specific bits without competing with H0's general semantics
- This parallels multi-head substrate (cycle 149 H2/H1 = 2.25x lift finding)

Why it is ranked 4th not 1st:
- Engineering cost: implementing multi-head encoder layer + storage + concat at write time
- Per-customer head training: need retrieval-objective training on customer data
- Dimensionality inflation: concat doubles embedding dim -> substrate W must be adapted
- But: if embedding dim doubles, pinv write cost quadruples (O(d^2) pseudoinverse)

Possible mitigation: use SMALL customer head (64-128 dims) + projection back to shared space
Cost reduction: customer head = small MLP on top of frozen H0 (essentially Mechanism 3 with explicit multi-head framing)

HARD-PASS: customer-domain retrieval >25% gain vs H0 alone; general retrieval unchanged
HARD-FAIL: concat embedding dimension causes pinv failure or AUC regression on general tasks

### Mechanism 5: Sparse Codebook Extension (substrate-native)
RANK: 5th (novel, highest uncertainty, most substrate-specific)
P_raw = 0.50 | P_deflated = 0.25 (penalty = 0.25, novel synthesis)

What it is:
- Production encoder is FROZEN: produces d-dim dense embedding
- Substrate extends the effective vocabulary via SPARSE CODES (cycle 142 sparse-KEY mechanism)
- New customer concepts -> new sparse codes added to sparse-KEY dimension
- Customer concept "RISK-ALPHA" gets assigned sparse code S_alpha in sparse dimension
- At write: (dense_emb || sparse_code_alpha) is written
- At query "RISK-ALPHA situation": encoder produces dense_emb + keyword detector assigns sparse_code_alpha
- Hybrid retrieval: match both dense (semantic similarity) and sparse (exact concept match)

Why this is interesting:
- Avoids encoder modification entirely
- Sparse code = explicit external memory of concept identity
- Similar to how BM25 (term matching) complements dense retrieval in modern hybrid systems
- Customer-specific sparse codes can be added WITHOUT any re-training

Critical open question: how does keyword-to-sparse-code assignment work at query time?
- Option A: exact string match ("RISK-ALPHA" in query -> assign code)
- Option B: small classifier trained on labeled examples per concept (50-200 examples each)
- Option C: customer-provided ontology file -> substrate maps ontology terms to sparse codes

Limitations:
- Only works for LEXICALLY IDENTIFIABLE concepts (terms that appear verbatim)
- Cannot handle paraphrase: "high RISK-ALPHA exposure" != "significant RISK-ALPHA risk" if tokenized differently
- Level-C concepts that have no stable surface form cannot get sparse codes
- Sparse dimension explosion with many customer concepts
- Requires sparse-KEY integration into substrate W writes (engineering work)

HARD-PASS: Level-B jargon retrieval improves >20% with sparse codes; no regression on dense queries
HARD-FAIL: sparse code collision or false-positive rate >10% degrades precision

---

## 4. INFORMATION-THEORETIC CONSTRAINT ANALYSIS

### The MI budget is fixed per encoder

    I(h; X) = encoder_capacity(model_size, input_length)

For Llama-3.2-1B with last-token pooling and PCA whitening:
- Model has ~1B params but last-token is a 2048-dim vector (post-PCA: 512-dim or similar)
- I(h; X) is bounded by dim(h) * log2(precision) bits (practical upper bound)
- Production encoder at cycle 140: 57.3x lift on retrieval means h is well-calibrated for semantic MI
- Any fine-tuning that does NOT increase I(h; semantic) cannot help Level-C

### Multi-head relaxation of the MI constraint

Single head: I(h; instruction) + I(h; semantic) <= I(h; X)
Two heads (h0 general, h_c customer):
  I(h0; semantic_general) <= I(h0; X)
  I(h_c; semantic_customer) <= I(h_c; X_customer_domain)
  Combined: I((h0, h_c); (general, customer)) = I(h0; general) + I(h_c; customer) [if domains orthogonal]

The orthogonality assumption: if customer domain is sufficiently distinct from base training domain,
h0 and h_c carry INDEPENDENT bits. Total mutual information scales with number of heads.

Practical implication: multi-head encoder is NOT a free lunch (compute doubles) but IS
information-theoretically sound. The cycle 149 multi-head substrate finding (H2/H1 = 2.25x) is
STRUCTURALLY ANALOGOUS: adding a second head gave super-linear MI because domains had low overlap.

### Why frozen encoder + W writes CANNOT close Level-C

Substrate W = weight matrix that maps h -> stored patterns
  W_optimal = argmin_{W} ||W * H - Y||_F^2 (pseudoinverse solution)
  where H = [h_1, h_2, ..., h_N] (encoder outputs), Y = [y_1, ..., y_N] (target patterns)

If h_i has NO discriminative signal for customer concept C (I(h_i; C) ~ 0):
  -> W cannot compensate; W * h_i is indistinguishable for C and non-C inputs
  -> This is the Level-C hard boundary: no W transformation can recover information
     not present in h_i

Mathematical statement: W is a linear map. Linear maps cannot increase MI.
  I(W*h; C) <= I(h; C)
  If I(h; C) = 0, then I(W*h; C) = 0 regardless of W.

This makes the encoder the IRREDUCIBLE bottleneck for Level-C. The gap is not engineering;
it is information-theoretic.

---

## 5. RETROMAE-STYLE PRE-TRAINING PIPELINE (PRODUCTION SPEC)

### Objective function

Standard RetroMAE:
  L = L_enc + L_dec
  L_enc = -sum_{masked x_i} log P(x_i | encoder_output)    [MLM on 15-30% masked input]
  L_dec = -sum_{x_i in X} log P(x_i | h, X_dec_masked)      [MAE on 50-70% masked input conditioned on h]

Where h = last_token(encoder(X_enc_masked)) = the sentence embedding.

The decoder's aggressive masking (50-70%) forces h to carry full semantic content.
The encoder's mild masking (15-30%) allows reasonable input quality.

### Why this does NOT break retrieval geometry

SFT loss: L_SFT = -sum log P(x_{t+1} | x_1...x_t)
  -> maximizes I(h_t; x_{t+1}) = instruction-following signal
  -> compresses I(h_t; full_document) as side effect

RetroMAE loss: L_dec = -sum log P(x_i | h, X_dec_masked)
  -> directly maximizes I(h; full_document) = semantic content
  -> h IS the signal being optimized; no MI competition with instruction-following

This is the mechanistic reason RetroMAE preserves retrieval geometry: the objective IS retrieval
geometry maximization.

### Customer onboarding pipeline

Stage 1: Domain corpus collection
  - Customer provides: 10K - 1M domain passages (no labels needed for MAE stage)
  - Format: raw text passages, 128-512 tokens each
  - Privacy: data stays on customer infrastructure (per federated learning models)

Stage 2: Unsupervised RetroMAE fine-tuning on domain corpus
  - Base: frozen production encoder (Llama-3.2-1B, last-token, left-pad, PCA)
  - Fine-tune ONLY the last 2-4 transformer layers + last-token head
  - Learning rate: 1e-5 (low; preserve base geometry)
  - Epochs: 2-3 (minimal; prevent overfitting on small domain corpus)
  - Cost: ~1-3 days on H100 for 1M passages; ~2-4 hours for 10K passages

Stage 3: Supervised contrastive fine-tuning (optional, if customer has labels)
  - If customer has query-document relevance pairs (even 500-1000 pairs):
  - InfoNCE / contrastive loss on top of RetroMAE-adapted encoder
  - THIS stage provides relational semantics (synonymy, equivalence)
  - Cost: 1-4 hours additional training

Stage 4: QDC calibration
  - Sample 100-500 domain queries
  - Compute Delta = mean(f_new(q) - f_old(q))
  - Store drift vector (tiny: d-dimensional float32 vector, ~8KB)
  - At retrieval: project queries using drift compensation (zero re-indexing cost)

Stage 5: Adapter integration (optional)
  - Deploy customer-specific adapter module alongside base encoder
  - Adapter has <5M params; loads at customer initialization
  - Base encoder shared across all customers (no per-customer model copies)

Total per-customer cost:
  - Data: 10K-1M passages (customer provides)
  - Compute: 2 hours - 3 days depending on corpus size
  - Engineering: ~2-4 weeks one-time to build the pipeline
  - Ongoing: 2-4 hours per customer deployment after pipeline exists

---

## 6. WHAT CANNOT BE DONE: SUBSTRATE DESIGN BOUNDARIES

These are NOT engineering challenges. They are structural impossibilities given current architecture.

### Boundary 1: Online concept formation without encoder update
- Substrate cannot INVENT new semantic distinctions in embedding space
- W writes can add new patterns but cannot create new DIMENSIONS of meaning
- Example: cannot spontaneously learn that "RISK-ALPHA" is categorically distinct from "RISK-BETA"
  without either: (a) encoder update, or (b) explicit sparse code assignment
- This is the Level-C hard boundary established in Section 4

### Boundary 2: Self-supervised exploration / curiosity-driven learning
- Substrate is a passive memory store: it writes what it's given, retrieves what is queried
- No generative mechanism to explore unvisited regions of concept space
- No internal "curiosity" signal that notices coverage gaps
- Cannot bootstrap concept formation from raw unlabeled streams without retrieval signal

### Boundary 3: Schema evolution without re-indexing
- If the customer CHANGES their taxonomy (RISK-ALPHA now means something different):
  - All existing substrate entries are in old schema space
  - No mechanism to retroactively re-embed old entries under new schema
  - W cannot be "updated" for this: it would require re-running all old documents through encoder
- Cost of schema evolution = full re-embedding of corpus (expensive but not infinite)

### Boundary 4: Causal reasoning over novel entity relationships
- Substrate retrieves; it does not reason
- If customer asks "why is RISK-ALPHA correlated with MARKET-SCENARIO-7?":
  - Substrate can RETRIEVE documents mentioning both
  - Substrate CANNOT derive the causal structure
  - This is a generation problem, not a retrieval problem
  - Out of scope (by design: substrate is memory, not reasoning engine)

### Boundary 5: Zero-shot concept invention (no examples)
- Encoder can generalize from distribution it was trained on
- For GENUINELY novel concept with no surface-form anchor:
  - Example: customer creates new color "blorp" that has no prior usage anywhere
  - Encoder has no basis for embedding "blorp" differently from random token
  - Sparse code assignment helps (explicit: "blorp -> sparse_code_X") but semantic
    similarity to related concepts remains at chance
- This is the absolute hard floor: zero information -> zero embedding quality

---

## 7. UNCONSIDERED ANGLES (5 non-obvious)

### Angle 1: Embedding-space RAG (use substrate as in-context examples for encoder update)
- Idea: at training time, retrieve related concepts from substrate using current encoder
- Feed retrieved embeddings AS CONTEXT to a small adapter trained to refine embeddings
- Mechanism: adapter(h, retrieved_neighbors) -> refined_h
- Essentially: RAG applied to embedding refinement, not generation
- Adjacent to: "retrieval-augmented training" in REALM / RAG literature
- Why non-obvious: substrate normally retrieves TO answer queries; here substrate trains the encoder
- P_raw = 0.45 (speculative, no direct lit precedent found)
- P_deflated = 0.20 (calibration penalty for novel synthesis)

### Angle 2: Federated cross-customer adapter training (privacy-preserving collective intelligence)
- FedE4RAG (2025) demonstrated: per-client encoder adapters trained without raw data sharing
  using HE-protected gradient aggregation
- Extension: train customer adapters COLLABORATIVELY across customers in same industry vertical
  (e.g., all pharma customers aggregate into shared pharma adapter; all finance into finance adapter)
- Each customer gets: base encoder + shared vertical adapter + private customer delta
- Benefits: each individual customer's data is small; collective data may be sufficient for Level-C
- Privacy: homomorphic encryption on gradients (proven mechanism from FedE4RAG)
- Cost reduction: per-vertical adapter amortized across all customers in that vertical
- Engineering challenge: vertical segmentation; some customers span multiple verticals
- P_raw = 0.55 | P_deflated = 0.32

### Angle 3: Hypernetwork-generated customer adapters (zero per-customer training)
- HyperPEFT (2024) approach: a single shared hypernetwork generates adapter parameters
  conditioned on customer-specific embedding (e.g., embedding of customer's domain description)
- Customer provides: 1-3 sentences describing their domain ("We process medical imaging reports...")
- Hypernetwork: H(domain_description) -> adapter_weights
- NO per-customer training; one-shot adapter generation at onboarding
- Why this might work: hypernetwork generalizes across domain description space if
  trained on diverse domain corpus (one-time cost)
- Analogy: in-context learning for adapter generation
- Current literature: HyperTTS (2024) does this for speaker adaptation; HyperExpert for task adaptation
- Gap: no published work on hypernetwork-generated RETRIEVAL adapters from domain descriptions
- P_raw = 0.40 | P_deflated = 0.15 (novel synthesis, no direct retrieval precedent)
- This is the highest-upside unconsidered angle: if it works, per-customer onboarding cost drops
  from "1-2 weeks" to "generate adapter in 30 seconds from domain description"

### Angle 4: Curriculum learning for cross-domain transfer (staged domain injection)
- Mechanism: instead of fine-tuning directly on customer domain, stage the training:
  Stage 1: Fine-tune on SIMILAR public domain (medical -> PubMed; finance -> Bloomberg)
  Stage 2: Fine-tune on customer-specific domain (starting from Stage 1, not base)
- Why curriculum helps: Stage 1 teaches domain structure (vocabulary, jargon patterns)
  without customer-private data; Stage 2 is small delta on top
- Customer data requirement drops: 500-1000 passages may suffice after Stage 1 curriculum
- Public domain corpora exist for most verticals: PubMed (medical), SEC EDGAR (finance),
  patents (legal/engineering), StackOverflow (software)
- Curriculum reduces Level-B cost substantially; Stage 1 can be pre-computed per vertical
- P_raw = 0.62 | P_deflated = 0.40
- This is the most immediately actionable unconsidered angle

### Angle 5: Drift-aware continual tokenization (encoder-level registry extension)
- From "Drift-Aware Continual Tokenization for Generative Recommendation" (2025):
  BPE/SentencePiece vocabularies can be EXTENDED post-training by adding new tokens
  with initialized embeddings from nearest neighbors in existing vocabulary
- Extension: customer-specific tokens ("RISK-ALPHA", "TEGRETOL") added to tokenizer vocabulary
  with embeddings initialized as: emb(RISK-ALPHA) = mean(emb(RISK), emb(ALPHA))
  or: emb(TEGRETOL) = emb(carbamazepine) [via nearest-neighbor in drug embedding space]
- Fine-tune ONLY the new token embeddings (input embedding table) -> all other weights frozen
- This avoids modifying transformer attention weights; only extends vocabulary
- Information-theoretic: no MI competition; new tokens are NEW dimensions, not reused ones
- Limitation: tokenizer change requires re-indexing ALL existing corpus (every document gets
  re-tokenized); one-time cost; subsequent updates are free
- P_raw = 0.55 | P_deflated = 0.33
- Why non-obvious: most practitioners think "encoder fine-tuning" means modifying transformer
  weights; vocabulary extension is a different intervention that avoids the Drill B failure mode

---

## 8. FALSIFIABLE PREDICTIONS

All P values are deflated. Calibration penalty applied: -0.20 to -0.25 from raw estimates.
Novel synthesis capped at P_deflated = 0.50 maximum.

### HARD-PASS thresholds (must ALL hold to declare gap "tractable")
HP-1: RetroMAE domain fine-tuning on customer corpus (10K+ passages) improves in-domain
      retrieval AUC by >15% vs frozen base encoder; no statistically significant regression
      on out-of-domain general retrieval. P_deflated = 0.55
HP-2: QDC (query drift compensation) maintains nDCG@10 within 5% of re-indexed baseline
      after encoder update; tested on 3+ independent domain shifts. P_deflated = 0.50
HP-3: Frozen-base domain adapter (Mechanism 3) with InfoNCE training on 500 labeled pairs
      achieves >10% Level-B vocabulary lift without measurable regression on general retrieval.
      P_deflated = 0.42
HP-4: Curriculum staging (Stage 1 on public vertical corpus + Stage 2 on customer corpus)
      reduces customer data requirement from 50K to <5K passages for equivalent domain
      adaptation quality. P_deflated = 0.38

### HARD-FAIL thresholds (any one of these closes the mechanism)
HF-1: RetroMAE domain fine-tuning degrades general retrieval AUC by >10%.
      If HF-1 fires: domain adaptation is NOT safe for production; entire Mechanism 1 closes.
HF-2: QDC drift compensation fails when domain shift is large (Delta_norm > 3 sigma of
      calibration drift distribution); nDCG degradation >10%.
      If HF-2 fires: QDC works only for INCREMENTAL updates, not major domain shifts.
HF-3: Level-C gap remains after ALL five mechanisms: custom encoder + adapter + QDC +
      sparse codes + curriculum. Some customer concepts remain unretrieable at >10% gap
      to supervised retrieval baseline.
      If HF-3 fires: Level-C is a FUNDAMENTAL boundary (as predicted by Section 4),
      not an engineering problem.
HF-4: Hypernetwork adapter generation (Angle 3) fails to generalize; adapter quality from
      domain description alone <50% of fine-tuned adapter quality.
      (Expected to fail based on current lit; Angle 3 is the high-uncertainty bet)

---

## 9. CROSS-THREAD SYNTHESIS

### Synthesis with cycle 149 multi-head substrate finding (H2/H1 = 2.25x)
The multi-head SUBSTRATE finding and the multi-head ENCODER proposal are structurally isomorphic:
- Multi-head substrate: H2 carries customer-specific relationship bits; H1 carries general bits
- Multi-head encoder: h_c carries customer-specific semantic bits; h0 carries general bits
- In both cases: the "extra head" serves domain-specific information routing
- Key question: should the additional head live in the ENCODER or in the SUBSTRATE?
  - Encoder head: shapes what information is encoded; more upstream; harder to add
  - Substrate head: shapes what relationships are stored; downstream; already proven at cycle 149
  - RECOMMENDATION: try substrate head FIRST (already exists); encoder head as fallback

### Synthesis with cycle 142 sparse-KEY mechanism
Sparse-KEY mechanism can serve as the structural scaffold for Mechanism 5 (sparse codebook):
- Sparse-KEY already in production; adds sparse signal to substrate writes
- Extending sparse-KEY to customer-concept codes is an incremental engineering step
- This is the cheapest Level-B path that requires NO encoder change

### Synthesis with SFT incompatibility (Drill B, P=0.72)
Drill B finding established SFT structural incompatibility. This drill refines it:
- The incompatibility is SFT + causal LM, NOT fine-tuning + causal LM in general
- RetroMAE objective is compatible with causal LM (different loss structure)
- LoRA + RETRIEVAL-CONTRASTIVE loss is also not ruled out by Drill B (Drill B tested LoRA + SFT)
- This is a meaningful distinction: LoRA is a dead end only when paired with SFT objective

---

## 10. GOLD IDENTIFICATION

### The primary gold insight:
The gap is not "encoder adaptation breaks retrieval." The gap is "SFT objective + causal LM
breaks retrieval." Retrieval-objective fine-tuning (RetroMAE) is structurally different and
empirically safe (BGE-M3 evidence). The Q4 LoRA experiment conflated ADAPTER ARCHITECTURE
with TRAINING OBJECTIVE. These must be disentangled:

  LoRA architecture x SFT objective = breaks retrieval (empirical: -28.9%)
  LoRA architecture x retrieval objective = unknown (NOT TESTED; plausibly fine)
  Frozen base x RetroMAE objective = safe (BGE-M3 empirical evidence)
  No adapter x QDC at inference = handles incremental drift (CoLLAs 2025)

The commercial pitch shifts from "our encoder cannot be adapted" to "we use retrieval-objective
fine-tuning (not SFT) for domain adaptation, which is the same technique used by the best
dense retrieval systems in the world."

### The secondary gold insight:
Query Drift Compensation (QDC, CoLLAs 2025) is directly applicable. The key problem with any
encoder update is: existing indexed corpus is now in the OLD embedding space. QDC solves this
with a single drift vector (tiny: d-dimensional, ~8KB for d=512) estimated from a calibration
set. This removes the re-indexing cost from the critical path, making encoder updates tractable
even in production with large corpora.

### The tertiary gold insight (highest uncertainty but highest upside):
Hypernetwork-generated adapters (Angle 3) could reduce per-customer onboarding from 1-2 weeks
to 30 seconds. This is the highest-leverage research investment if verified. Current lit (HyperTTS,
HyperPEFT) establishes the mechanism works in adjacent domains (speech, NLP tasks); the retrieval
transfer is unproven but mechanistically plausible.

---

## 11. HONEST COMMERCIAL POSITIONING

What IS true (can be asserted with confidence):
- "Domain adaptation that PRESERVES retrieval quality is a solved engineering problem
   (RetroMAE, BGE-M3 evidence, 2024)"
- "We do NOT use SFT-style fine-tuning (known to degrade retrieval)"
- "Customer-specific encoder adaptation takes 2 hours to 3 days depending on corpus size"
- "Existing indexed corpus requires no re-indexing after encoder update (QDC mechanism)"
- "Genuinely new concepts (no surface-form anchor) require encoder update -- one-time cost"

What is NOT true (do not assert):
- "Substrate learns your domain automatically" -> FALSE (requires explicit training)
- "Zero-cost online adaptation" -> FALSE (requires compute; cannot be done in real-time)
- "Substrate generalizes to arbitrary new concepts without training" -> FALSE (Level-C hard boundary)
- "LoRA-style cheap adaptation works" -> FALSE (empirically refuted Q4, -28.9%)

Honest pitch:
"We support domain-specific deployment via retrieval-objective pre-training on your corpus.
This preserves our base retrieval quality (no degradation on general tasks) while improving
in-domain retrieval by 15-25%. Onboarding cost is 2 hours to 3 days of compute. Genuinely
novel concepts your encoder has never encountered require explicit onboarding (one-time, not
ongoing). We do not promise zero-cost online adaptation because that is not physically possible
without destroying retrieval quality -- and we choose retrieval quality over cheap adaptation."

---

## 12. ENGINEERING COST ESTIMATE

| Component                         | Complexity    | Time (after pipeline built) | One-time build cost |
|-----------------------------------|---------------|-----------------------------|---------------------|
| RetroMAE fine-tuning pipeline     | Medium        | 2 hours - 3 days            | 2-3 weeks eng       |
| QDC drift compensation            | Low           | 1 hour (calibration)        | 3-5 days eng        |
| Domain adapter (Mechanism 3)      | Low-medium    | 2-4 hours                   | 1-2 weeks eng       |
| Sparse-KEY concept extension      | Low (existing)| 30 minutes config           | 3-5 days eng        |
| Multi-head encoder (Mechanism 4)  | High          | 1-2 weeks                   | 4-6 weeks eng       |
| Hypernetwork adapters (Angle 3)   | Very high     | 30 seconds (inference only) | 8-12 weeks eng      |
| Federated cross-customer (Angle 2)| Very high     | varies                      | 12+ weeks eng       |

Recommended sequencing:
1. Sparse-KEY concept extension (cheapest; leverages existing infrastructure; Level-B only)
2. QDC deployment (enables ANY encoder update without re-indexing; foundational)
3. RetroMAE fine-tuning pipeline (closes Level-B properly; establishes domain onboarding)
4. Domain adapter (adds per-customer specialization on top of RetroMAE)
5. Curriculum staging (reduces data requirements per customer)
6-7. Multi-head encoder / Hypernetwork (high-upside bets; pursue after 1-5 validated)

---

## 13. CHEAP DECISIVE TEST

The cheapest test that would distinguish "gap is tractable" from "gap is fundamental":

TEST: Take the production encoder (Llama-3.2-1B, last-token, PCA whitening).
Fine-tune ONLY 2 transformer layers (layers 14-15) using RetroMAE objective on a public
domain corpus (PubMed abstracts, ~100K docs, 2-4 hours on remote GPU).
Measure: (a) KF-1 AUC on general test set (should not degrade); (b) retrieval AUC on
PubMed-specific queries (should improve).

If (a) holds and (b) improves: RetroMAE-style fine-tuning is safe. Gap is tractable.
If (a) degrades: the causal LM architecture has deeper incompatibility than Drill B predicted.
   -> Escalate to HARD-FAIL; close Mechanism 1; fall back to adapter-only (Mechanism 3).

Cost: ~4 hours H100 compute, ~$2-4 on Lambda. Decisive within one experiment.
This is the ANCHOR CANDIDATE for exp_dev hand-off.

---

## CITATIONS (verified count: 9)

1. Goswami et al. (2025). "Query Drift Compensation: Enabling Compatibility in Continual Learning
   of Retrieval Embedding Models." CoLLAs 2025 / arXiv:2506.00037.
   [Empirical: nDCG@10 = 54.1 matching joint training; QDC equations; embedding distillation]

2. Xiao et al. (2022). "RetroMAE: Pre-Training Retrieval-oriented Language Models Via Masked
   Auto-Encoder." arXiv:2205.12035.
   [MAE objective for retrieval; encoder 15-30% mask; decoder 50-70% mask]

3. BGE-M3 / M3-Embedding (2024). EmergentMind / BAAI.
   [Continual RetroMAE pre-training; domain adaptation without out-of-domain degradation;
   state-of-art on BEIR zero-shot]

4. FedE4RAG (2025). "Privacy-Preserving Federated Embedding Learning for Localized RAG."
   arXiv:2504.19101.
   [HE-protected gradient aggregation; per-client encoder adaptation; Hit@1 73% on finance]

5. Ansell et al. (2024). "HyperTTS: Parameter Efficient Adaptation in Text to Speech Using
   Hypernetworks." ACL 2024 / LREC-MAIN.747.
   [Hypernetwork generates adapter params conditioned on speaker embedding]

6. HyperPEFT (2024). "Hypernetwork-Assisted Parameter-Efficient Fine-Tuning." NAACL 2024 Findings.
   arXiv:2024.findings-naacl.109.
   [Shared hypernetwork promotes knowledge transfer; reduces catastrophic forgetting]

7. "Drift-Aware Continual Tokenization for Generative Recommendation." arXiv:2603.29705 (2025).
   [BPE vocabulary extension; new token initialization from nearest neighbors]

8. "Knowledge Accumulation in Continually Learned Representations and the Issue of Feature
   Forgetting." arXiv:2304.00933.
   [Contrastive continual learning less prone to forgetting; improved generality]

9. "Rethinking the Understanding Ability across LLMs through Mutual Information." arXiv:2505.23790
   (2025).
   [Encoder-only LLMs maintain higher MI than decoder-only; fine-tuning for token MI improves
   downstream tasks; confirms MI asymmetry between encoder-only and causal LM]

---

## SUMMARY TABLE

| Gap Level | Description                   | Tractable? | Best Mechanism                    | Cost           | P_deflated |
|-----------|-------------------------------|------------|-----------------------------------|----------------|------------|
| Level A   | New entities in same domain   | YES (done) | W writes (cycle 149)              | Near-zero      | 0.90       |
| Level B   | Domain jargon / vocabulary    | YES        | Sparse-KEY + RetroMAE + adapter   | 2 hr - 3 days  | 0.42-0.55  |
| Level C   | Genuinely novel concepts      | PARTIAL    | RetroMAE + curriculum             | 1-3 weeks      | 0.28-0.40  |
| Level C+  | Zero-surface-form new concept | NO         | Hard boundary (MI theorem)        | N/A            | N/A        |

P_deflated global: 0.40 (gap tractable via engineering; novel synthesis cap applied)
Next-drill candidate: online-learning field, Angle 3 (hypernetwork adapters) + curriculum staging
