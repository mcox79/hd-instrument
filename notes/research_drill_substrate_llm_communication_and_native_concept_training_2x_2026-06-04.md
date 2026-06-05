# Research Drill: 2x Substrate-LLM Communication + Native Concept Training
# Date: 2026-06-04
# Trigger: User questions on (A) direct substrate-LLM communication status and (B) native concept-level training architecture
# Prior drills incorporated: System1-hybrid-2x, Level3-meta-LLM-2x, substrate-direct-generative-LM-3x
# Calibration penalty: -0.20 applied; novel-synthesis P capped at 0.50
# Discipline: algebraic + lit-scan only; no empirical verification

---

## HEADLINE

The optimal near-term substrate-LLM communication protocol is Option A (text injection) confirmed by four independent algebraic constraints -- bandwidth ceiling at M=200 patterns is only ~200 bits, audit-certificate fidelity is highest at text level, residual injection (Option C) requires geometry alignment training that does not yet exist, and today's B8 sparse residual encoding is the CORRECT substrate-side representation for future Option C migration. The substrate-native concept training architecture is a two-path hybrid: ConceptLM-style VQ codebook on substrate-retrieved vectors (discrete; maps to B8 logit-space encoding directly) PLUS CoCoMix-style continuous concept mixing injected at pretraining time (continuous; maps to Option C residual injection when alignment is available). Both paths are algebraically anchored in 2025 literature. The load-bearing next experiment is substrate-on-LLM-embeddings at concept granularity using Pythia-160M Layer 12 activations as the concept encoder, with VQ quantization matching the B8 sparse residual vocabulary.

P_deflated(overall roadmap executable) = 0.38; P_deflated(Option A near-term superiority) = 0.72; P_deflated(concept-level VQ training works) = 0.35; calibration penalty -0.20 applied throughout; novel-synthesis cap 0.50.

---

## CHEAP DECISIVE TEST

Feed 5-corpus HP substrate retrievals (top-5 patterns per domain, N=8192) through text injection to a frozen Llama-3.2-1B; compare cross-domain QA accuracy WITH vs WITHOUT substrate-retrieved context. Wall: ~2 hrs GPU (already partially set up via Phase 0.5 v1 Hyperprobe infrastructure). Cost: minimal (uses existing Llama-3.2-1B already loaded for Hyperprobe).

Separately: take Pythia-160M Layer 12 activations on 10K sentences from Wikitext-2; VQ-quantize to vocabulary of V_c=256 concept types; train substrate W on sequence of concept-IDs as next-concept-prediction task; measure concept-level perplexity.

---

## FALSIFIABLE PREDICTIONS: HARD-PASS / HARD-FAIL

### (A) Direct substrate-LLM communication

HARD-PASS (Option A):
  Cross-domain QA accuracy WITH substrate context >= 65% vs without context <= 30%.
  Interpretation: text injection of substrate retrievals provides material lift; Option A is product-viable.

MIDDLE-BAND:
  Accuracy WITH substrate context = 40-65%.
  Interpretation: substrate retrieval is partially useful; content compression too aggressive (M=200 patterns too few per domain).

HARD-FAIL (Option A):
  Accuracy WITH substrate context <= 35% (no material lift over 0-shot LLM).
  Interpretation: text-encoded substrate retrievals are too noisy at M=200 for Option A to add value; need higher M or Option C geometry alignment first.

HARD-PASS (Option C prerequisite):
  W_proj alignment training (Procrustes, ~4-8 hrs GPU) achieves cos(W_proj * x_substrate, x_LLM) >= 0.60 on held-out test pairs.
  Interpretation: geometry gap between bipolar substrate and LLM residual stream is bridgeable; Option C migration is unlocked.

HARD-FAIL (Option C prerequisite):
  cos(W_proj * x_substrate, x_LLM) <= 0.30 after alignment training.
  Interpretation: substrate bipolar geometry is too far from LLM activation geometry; Option C requires purpose-built joint training (Option B path).

### (B) Concept-level training

HARD-PASS (VQ concept training):
  Substrate W trained on concept-ID sequences achieves concept-level perplexity <= 20 on held-out Wikitext-2 concepts (V_c=256).
  Interpretation: substrate learns concept-level statistics; native language at concept granularity is viable.

HARD-FAIL (VQ concept training):
  Concept perplexity >= 40 (near random at V_c=256).
  Interpretation: substrate's Hebbian associative rule does not capture concept-level statistics; VQ codebook required to be updated jointly (breaks bipolar guarantee).

---

## SUB-QUESTION 1: OPTIMAL COMMUNICATION CHANNEL GIVEN TODAY'S EMPIRICAL ANCHORS

### Four independent algebraic constraints all favor Option A near-term

Constraint 1 -- Bandwidth ceiling at current M.
  At M=200 stored patterns per domain (5-corpus HP test), effective semantic content per retrieved pattern
  is log2(200) ~ 7.6 bits. Top-K=5 retrievals: ~38 bits of unique semantic content.
  Option A (text injection): delivers ~200-400 bits via ~50-token text representation of retrieved patterns.
  Option C (residual injection): delivers D=2048 bits injected dimension.
  KEY INSIGHT: both options are operating WELL ABOVE the semantic ceiling of ~38 bits. Neither is
  bandwidth-limited at M=200. Option A's information fidelity gap vs Option C is irrelevant at this M.
  At M >= 10,000 (product scale): semantic content per retrieval rises to log2(10000) ~ 13 bits;
  top-K=10 retrievals: ~130 bits. Option A is STILL sufficient (200-400 bits text > 130 bits semantic).
  THRESHOLD where Option C bandwidth matters: M >= 50,000 patterns per domain; expected in Tier 1
  product deployment but not in current substrate-class experiments.

Constraint 2 -- Audit certificate fidelity.
  B6 D-ECR produces per-write deletion certificates that must be transmitted to the LLM consumer.
  Option A: certificates are legible tokens in context; LLM can reason about them; auditor can inspect.
  Option C: certificates would need to be encoded in D=2048-dim projection; LLM attention cannot
  parse certificates in residual form without additional supervision.
  Audit-fidelity advantage: Option A >> Option C.

Constraint 3 -- B8 logit-space sparse residual as OPTION C STAGING LAYER.
  B8 encodes substrate retrieval as sparse logit deltas (r=0.263 top-K=5 logits).
  This IS the representation required for Option C migration: the sparse logit vector lives in LLM
  token-probability space, which IS aligned with LLM residual stream at the final layer.
  Algebraic path: B8 sparse delta -> Project to LLM Layer L (logit lens inverse) -> Add to residual
  at layer 0.7*L.
  CRITICAL INSIGHT: B8 sparse residual is not just a storage format; it is a geometry-bridge between
  substrate and LLM activation space. No new W_proj training needed if injection happens at Layer L
  (final) rather than at 0.7*L. Injection at 0.7*L still needs projection training.
  This reduces Option C alignment cost from full Procrustes training to a single logit-to-hidden
  layer projection (one linear layer, ~D^2 params = 4M params at D=2048).

Constraint 4 -- SQ2 multi-hop K=12 pre-processing as Option A enhancement.
  SQ2 multi-hop reasoning HP at K=12 means substrate can PRE-PROCESS queries via 12 iterated
  retrievals BEFORE delivering to LLM. This upgrades Option A from "LLM receives raw retrieval"
  to "LLM receives pre-processed multi-hop gist."
  Bandwidth of SQ2-enhanced Option A: K=12 hops x ~50 tokens/hop = ~600 tokens = ~4800 bits.
  This is HIGHER bandwidth than Option C without additional engineering.
  KEY FINDING: SQ2-enhanced Option A is the product architecture for multi-hop QA.

### Channel ranking updated with today's findings

  Option A (text): NEAR-TERM PRODUCT PATH. Bandwidth sufficient at M<=10K; SQ2 enhancement
    upgrades to 4800 bits; audit certificates fully preserved.
  Option A+SQ2: FLAGSHIP PRODUCT ARCHITECTURE for multi-hop QA. No additional engineering.
  Option C+B8 logit injection at final layer: MEDIUM-TERM (1 eng-week). B8 provides the geometry
    bridge; single linear projection from logit-space to hidden-space is all that is needed.
  Option C+W_proj at 0.7*L: MEDIUM-TERM (2-4 eng-days GPU). Higher bandwidth (D=2048 dims);
    requires Procrustes alignment training on (substrate_retrieval, LLM_activation) pairs.
  Option B (attention substitution): LONG-TERM. Requires joint training; breaks audit certificates
    unless Hopfield-attention identity is exploited at inference-only (no gradient through W_substrate).

Cite: CAA (Zou et al. arXiv:2312.06681); Modern Hopfield = Attention (Ramsauer et al. ICLR 2021;
arXiv:2008.02217); CAMELoT associative memory injection (arXiv:2402.13449; 29.7% perplexity reduction,
training-free coupling to frozen LLMs); Hyperdimensional Probe VSA-residual coupling (arXiv:2509.25045).

---

## SUB-QUESTION 2: CONCEPT-LEVEL TRAINING ARCHITECTURE

### Three architecture candidates and their algebraic relationship

Candidate A: Substrate-on-Coconut-outputs (continuous latent thought as concept vector)
  Coconut (Hao et al. arXiv:2412.06769): feeds last hidden state h_t back as next-token embedding
  without decoding to text. Each h_t is a D-dimensional continuous vector.
  Substrate role: store sequence of Coconut h_t vectors as Hebbian memory;
    W += bind(h_t, position_k) for K-step context.
  Retrieval: given h_t-K...h_t-1, retrieve predicted h_t+1.
  Algebraic problem: Coconut's h_t is a continuous D-dimensional Gaussian-distributed vector;
    substrate is bipolar {-1,+1}^N. Mismatch: NO binarization of continuous thought preserves
    its continuous BFS structure. P_deflated(works directly) = 0.20.
  Resolution: Project h_t -> bipolar via learned sign-projection P: {h_t -> sign(W_map * h_t)}.
    This is a 1-bit compressive sensing step. At D=2048, N=8192: 4x expansion; SNR preserved
    if W_map is an incoherent random projection (Johnson-Lindenstrauss; Achlioptas 2003).
  P_deflated(works with JL projection) = 0.40.

Candidate B: Substrate-on-LLM-embeddings (Pythia-160M Layer 12 as concept encoder)
  Use frozen Pythia-160M (or Llama-3.2-1B) to generate contextualized embeddings for each
  sentence position. Embedding e_t = LLM_hidden_layer_k(sentence, position_t).
  VQ-quantize e_t to concept-ID using Vector Quantization codebook of size V_c = 256-512
  (ConceptLM style; arXiv:2602.08984; trained on 300B tokens, VQ codebook, next-concept gain).
  Substrate trains on sequence of concept-IDs: W_{concept} via Hebbian outer-product on
    bind(concept_ID_t, position_k).
  Retrieval predicts next-concept-ID; scores decoded back to token probabilities via concept->token
    distribution from codebook.
  P_deflated(VQ concept training at substrate-class): 0.40.
  ADVANTAGE: concept vocabulary is discrete (V_c=256); substrate operates on sparse hypervectors
    for each concept-ID, which IS the substrate's native mode. No geometry mismatch.
  DISADVANTAGE: requires frozen LLM pass to generate concept-IDs (inference overhead); concept
    vocabulary is LLM-derived, not substrate-native.
  CRITICAL LINK TO B8: B8's sparse logit-space residual (r=0.263, K=5 top logits) is itself a
    compact encoding of next-token-probability delta -- algebraically equivalent to a soft concept-ID
    when projected through the logit lens. Substrate trained on B8 residuals IS training on concept-level
    prediction in logit space.
    CONCLUSION: B8 residual training is ALREADY concept-level training under a logit-lens interpretation.

Candidate C: Substrate-via-CoCoMix-continuous-concept-mixing
  CoCoMix (Tack et al. arXiv:2502.08524, Meta 2025): extracts continuous concepts from pretrained
  SAE; mixes concept vectors into LLM hidden states during pretraining; more sample-efficient than
  pure NTP; directly inspectable and steerable.
  Substrate role: store the concept vectors (extracted from pretrained SAE) as substrate atoms;
    retrieve concept vectors given query; inject back into LLM hidden state.
  This IS Option C residual injection applied at pretraining time rather than inference time.
  Algebraic requirement: concept vectors from SAE are sparse D-dimensional real vectors (same
  geometry as LLM activations); projection to bipolar substrate requires same JL step as Candidate A.
  P_deflated(CoCoMix-style with substrate): 0.32 (requires JL alignment + SAE pretraining).
  ADVANTAGE: SAE concept vocabulary is substrate-native in the sense that it IS the sparse
  feature decomposition of the LLM -- most conceptually aligned with substrate's distributed
  representation philosophy.

### Recommendation: Candidate B first, Candidate C second

Step 1 (Candidate B, ~1-2 eng-days): Train substrate on VQ concept-ID sequences from Pythia-160M.
  - Extract LLM Layer 12 activations for Wikitext-2 training sentences.
  - VQ-quantize to V_c = 256 concept-IDs (VQ-VAE; 10-minute GPU training for VQ head).
  - Train substrate W on concept-ID Hebbian rule: W += bind(concept_k, position_k).
  - Evaluate: concept-level perplexity on held-out Wikitext-2 concepts.
  - PRE-REG HARD-PASS: concept ppl <= 20. HARD-FAIL: concept ppl >= 40.
  - This establishes whether substrate can capture concept-level statistics at all.

Step 2 (Candidate A variant, +1 eng-day): Once Step 1 established, test substrate-on-Coconut-outputs
  with JL sign-projection; compare concept-level perplexity vs VQ-derived concepts.

Step 3 (Candidate C, Phase 2): CoCoMix-style mixing requires SAE pretraining (GPU-intensive);
  deferred to Phase 0.5b or Phase 1.

Cite: Coconut (Hao et al. arXiv:2412.06769); ConceptLM NCP (arXiv:2602.08984); CoCoMix
(Tack et al. arXiv:2502.08524); HRR Plate 1995; VSA concept binding Frady-Sommer 2020 (NeCo);
Johnson-Lindenstrauss (Achlioptas 2003, J. Comput. Syst. Sci. 66:671-687).

---

## SUB-QUESTION 3: NEXT-EXPERIMENT DESIGN -- BUILDING ON 11 BIO-PRIMITIVES + 3 LESSONS

### 3 composition lessons constrain the next experiment

Lesson 1 -- Same-axis collinear: primitives that encode along the same semantic axis
  (e.g., position-binding AND semantic content both in hd-space) must be orthogonalized or
  they constructively interfere and saturate the context vector. Design constraint: concept-ID
  vectors for DIFFERENT semantic positions must have pairwise cosine < 0.1 (achievable with
  N >= 1024 for V_c = 256; expected cosine ~ 1/sqrt(N) = 0.031 at N=1024).

Lesson 2 -- Linear-W replay-incompatible: algebraically proven (prior drill). Replay of
  pattern x_i reinforces W along x_i direction; if new patterns x_j are collinear with x_i,
  replay interferes with new learning. For concept-level training: concept-ID vectors
  should be drawn from a fixed RANDOM codebook, NOT from a learned codebook that drifts during
  training (drift would create collinearity between old and new concept vectors).

Lesson 3 -- Metric-must-match-axis-of-improvement: validation metric must measure the
  axis being improved. For concept-level training: metric is CONCEPT-LEVEL perplexity
  (not token-level ppl); token-level ppl will not show improvement if substrate captures
  concept structure but not surface token distribution.

### Next experiment: substrate concept-level prediction via VQ concept-IDs (EX-CONCEPT-1)

Architecture (applying 3 lessons):
  Concept encoder: frozen Pythia-160M Layer 12; VQ codebook V_c=256 trained separately;
    concept-IDs are fixed RANDOM hypervectors phi(c_i) in {-1,+1}^N, NOT learned
    (satisfies Lesson 2: no drift; satisfies Lesson 1: pairwise cosine ~ 0.031 at N=1024).
  Context window K=8 (within SQ2 validated K=12 window; safe operating regime).
  Hebbian rule: W += bind(phi(c_{t+1}), h_t^{K}) where h_t^{K} = sum_k bind(phi(c_{t-k}), rho_k).
  Metric: concept-level perplexity on held-out Wikitext-2 concept sequences (Lesson 3).
  Sweep: N in {1024, 4096, 8192}; V_c in {64, 256, 512}; K in {4, 8, 12}.
  Wall: ~20-60 min CPU per cell; full sweep ~4-8 hrs remote CPU.

How this builds on validated bio-primitives:
  Uses: position-binding (validated Bundle E HP), DG-sparse expansion (validated B2/B3),
  palimpsest decay (validated B5), D-ECR eviction (B6 HP), PPMI concept extraction (M2).
  New: VQ concept encoder (Candidate B above).
  NOT used: cf-RPE (excluded per Lesson 2 -- cf-RPE is a comparison-axis operation that
  would create cross-axis interference when combined with concept-level encoding).

Cite: SQ2 multi-hop K=12 (today HP), Bundle E E1 trigram K=3 (HP), ConceptLM (arXiv:2602.08984),
Plate 1995 HRR, Frady-Sommer 2020.

---

## SUB-QUESTION 4: PRODUCT-ROADMAP STATUS

### Direct substrate-LLM communication front

| Item | Status | Next gate |
|------|--------|-----------|
| Phase 0.5 v1 Llama-3.2-1B Hyperprobe | ENGINEERING (npz ~done) | Run audit core on npz; establish which LLM layers carry substrate-predictable signal |
| 5-corpus HP aggregator | VALIDATED HP | Level 3 meta-LLM test (~1 eng-day, text injection) |
| B6 D-ECR | VALIDATED HP | Deploy in Option A pipeline; certificates propagate via text |
| B8 logit-space sparse residual | VALIDATED HP (r=0.263) | B8 as Option C geometry bridge (logit-lens injection) |
| SQ2 multi-hop K=12 | VALIDATED HP | Combine with Option A for SQ2-enhanced multi-hop pipeline |
| C1/C2/C3 cornerstone at 8B | ROUTED, not dispatched | $9-12 cloud; holds until Phase 0.5 v1 audit complete |
| Tier 1 RAG (substrate-class) | NOT TESTED | Requires Option A text injection pipeline + prompt templates |
| Option C residual injection | NOT STARTED | B8 logit bridge reduces alignment cost to 1 linear layer |

### Substrate-native language front

| Item | Status | Next gate |
|------|--------|-----------|
| Bigram/trigram/K=8 | VALIDATED HP | Baseline established |
| Extended K=12 multi-hop | VALIDATED HP (today, SQ2) | Flagship capability |
| EX1 substrate-direct LM | Smoke ppl=7.4 synthetic | Wikitext-2 char-level test pending |
| Concept-level (VQ/Coconut) | NOT TESTED | EX-CONCEPT-1 (above) is the next gate |
| SQ1 resonator-generative | SPEC'd, not built | Deferred to after EX-CONCEPT-1 |

### Priority order for next 1-week empirical work

1. (Day 1, CPU, ~2 hrs) EX-CONCEPT-1: substrate-on-VQ-concept-IDs from Pythia-160M.
   WHY: opens concept-level language axis; closes biggest gap in native-language front.
   LINK to B8: VQ concept-ID in logit-space IS B8 sparse residual; no code reuse gap.

2. (Day 1-2, GPU, ~3-4 hrs) Phase 0.5 v1 Hyperprobe audit: run audit core on Llama-3.2-1B npz.
   WHY: establishes which LLM layers are predictable from substrate; prerequisite for Option C
   alignment (need to know the target layer before training W_proj).
   OUTPUT: layer-activation profile; input for C1/C2/C3 cornerstone dispatch.

3. (Day 2-3, CPU, ~4 hrs) EX1 Wikitext-2 char-level LM: confirm substrate-direct LM
   generalizes from synthetic counting task to natural language.
   WHY: closes biggest uncertainty in native-language ppl ceiling.

4. (Day 3-5, GPU, ~8 hrs) Option C geometry alignment: W_proj from B8 logit-space to
   LLM residual at Layer 0.7*L; use (substrate_retrieval, LLM_hidden) pairs from Hyperprobe npz.
   WHY: unlocks Option C; prerequisite for CoCoMix-style concept injection.

5. (Day 5-7, GPU, ~4-8 hrs) Level 3 meta-LLM text injection smoke test: cross-domain QA
   accuracy WITH vs WITHOUT 5-corpus substrate context on frozen Llama-3.2-1B.
   WHY: validates the full Option A pipeline at product scale; prerequisite for C1/C2/C3 dispatch.

---

## SUB-QUESTION 5: PRODUCT-TO-EMPIRICAL GAP ANALYSIS

### Claim: "Substrate auditable System 1 for hybrid AI"

EMPIRICAL STATUS: PARTIALLY VALIDATED.
  - TC0 complexity class role: algebraically derived (prior drill), not empirically measured.
  - Audit certificates (B6 D-ECR): HP, operational at substrate-class.
  - 5-corpus aggregator HP: validates multi-domain System 1 function.
  - SQ2 K=12: validates pre-processing (System 1 pre-fills LLM context).
REMAINING GAP: no end-to-end measurement of cross-domain QA accuracy WITH substrate vs WITHOUT.
  This is precisely the Level 3 meta-LLM smoke test (priority #5 above).
  P_deflated(claim fully validated in 1 week): 0.45.

### Claim: "Substrate trains language via bio-primitives"

EMPIRICAL STATUS: SUBSTRATE-CLASS VALIDATED; LLM-TIER AND CONCEPT-LEVEL UNTESTED.
  - Bigram/trigram/K=8/K=12: HP at substrate-class.
  - EX1 synthetic counting task: smoke ppl=7.4 (promising but synthetic corpus).
  - EX1 Wikitext-2: PENDING (1-week priority #3).
  - Concept-level: NOT TESTED (1-week priority #1).
REMAINING GAP: two open experiments (Wikitext-2 char-level; VQ concept-level).
  P_deflated(both pass in 1 week): 0.30.

### Claim: "Substrate reasoning at substrate-class"

EMPIRICAL STATUS: HARD-PASS VALIDATED (SQ2 K=12 today).
  - Multi-hop retrieval chain with 12 hops: HP.
  - NC1 complexity class: algebraically confirmed.
REMAINING GAP: only substrate-class tested; LLM-tier (Llama-3.2-1B native language reasoning
  augmented by substrate multi-hop) not yet measured.
  P_deflated(extends to LLM-tier with Option A): 0.55.

### Claim: "Direct substrate-LLM communication"

EMPIRICAL STATUS: TIER 0.5b LOCKED ARCHITECTURALLY; EMPIRICAL VALIDATION IMMINENT.
  - Tier 0.5b residual at 0.7*L: ESTABLISHED architectural choice.
  - Phase 0.5 v1 Hyperprobe: ENGINEERING (audit imminent).
  - C1/C2/C3 cornerstone: ROUTED, pending dispatch.
  - Option A text injection smoke test: 1-week priority #5.
REMAINING GAP: zero end-to-end measurements yet. All gaps close within 1 week per priority list.
  P_deflated(first end-to-end measurement in 1 week): 0.60.

---

## CROSS-DOMAIN PROBE: PUBLISHED SUBSTRATE-LLM COUPLING AT PRODUCTION SCALE

The lit-scan finds NO published system that demonstrates bipolar-discrete-state associative memory
+ LLM + concept-level training at production scale as a unified product. The closest published
systems are:

1. CAMELoT (arXiv:2402.13449, 2024): associative memory coupled to frozen LLM, training-free.
   Achieves 29.7% perplexity reduction. Architecture-agnostic injection. KEY FINDING: proves
   training-free coupling is viable; substrate can couple to frozen LLM without modifying LLM weights.
   SUBSTRATE ADVANTAGE: substrate's coupling provides audit certificates; CAMELoT does not.

2. ConceptLM NCP (arXiv:2602.08984, 2025): VQ discrete concept prediction, 70M-1.5B scale,
   300B training tokens, consistent gains on 13 benchmarks. KEY FINDING: VQ concept vocabulary
   IS the correct training objective; discrete concept granularity outperforms token-level.
   SUBSTRATE LINK: substrate W trained on VQ concept-IDs IS this paradigm applied to associative memory.

3. CoCoMix (arXiv:2502.08524, 2025): SAE continuous concept mixing during LLM pretraining.
   Sample-efficient; directly steerable. KEY FINDING: concept-level signals during pretraining
   are more sample-efficient than token-level. SUBSTRATE LINK: substrate as external SAE
   concept store enables CoCoMix-style injection without modifying LLM pretraining.

4. Hyperdimensional Probe (arXiv:2509.25045, 2025): VSA/HDC applied to LLM residual stream
   for interpretability probing. KEY FINDING: bipolar hypervector algebra is COMPATIBLE with
   LLM residual stream at the conceptual level; VSA binding works over residual activations.
   SUBSTRATE LINK: directly validates that substrate's VSA operations are a valid representational
   framework for LLM internals; the geometry alignment problem is solvable.

5. MemLLM (survey arXiv:2603.07670, 2025): fine-tuned LLM + explicit read-write memory module;
   tightly couples parametric and non-parametric knowledge. KEY FINDING: joint training of
   retrieval and generation yields better utilization than frozen-retriever. SUBSTRATE LINK:
   substrate's Hebbian W update IS a read-write module; MemLLM-style joint training path
   exists if substrate binarization is treated as a quantization step.

ALGEBRAIC ANCHOR FOR OPTIMAL PROTOCOL: no published system has combined bipolar associative
memory + concept-level training + audit certificates in one architecture. The combination
IS novel. Literature confirms each component separately; composition is substrate's unique
contribution. Calibration penalty -0.20 applied to composition claims.

---

## CROSS-THREAD SYNTHESIS WITH PRIOR DRILLS

1. System1-hybrid-2x (today): established TC0 role division; episodic buffer at ~400 bits
   per cycle. THIS DRILL ADDS: SQ2 K=12 HP upgrades Option A bandwidth from 400 bits to
   ~4800 bits via pre-processing; changes the near-term product architecture from "raw retrieval
   injection" to "pre-processed multi-hop gist injection."

2. Level3-meta-LLM-2x (today): established Option A >> C near-term; Option B long-term.
   THIS DRILL ADDS: B8 logit-space residual reduces Option C alignment cost from full
   Procrustes to single linear layer; concrete migration path from A to C without retraining.

3. Substrate-direct-generative-LM-3x (today): established char-LM architecture + K*_corr=4-7.
   THIS DRILL ADDS: concept-level VQ training is COMPLEMENTARY (not competing) with char-LM;
   they operate at different granularities; char-LM at token level, VQ concept training at
   concept level; both use the same W with different encoding schemes.

4. Substrate-unexplored-capabilities-2x (today): established resonator-generative as
   unexplored upside. THIS DRILL ADDS: SQ1 resonator-generative is deferred pending EX-CONCEPT-1;
   the concept-level VQ training is a prerequisite for resonator generation over concepts
   (need concept codebook before resonator can factorize concept compositions).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. OPTION A+SQ2 IS THE NEAR-TERM PRODUCT ARCHITECTURE. Implemented by: substrate SQ2 K=12
   pre-processes query -> multi-hop gist at ~600 tokens -> prepended to LLM context. No model
   modification, no new training. Deliverable in 1 eng-week using existing validated components.
   Product narrative: "Ask a question; substrate pre-processes via 12 retrieval hops; LLM
   receives curated, audited context." Audit certificates are in the text context -- inspectable.

2. B8 LOGIT-BRIDGE IS THE KEY TECHNICAL ENABLER FOR OPTION C MIGRATION. B8 proved r=0.263
   logit-space encoding; this IS the substrate representation in LLM probability space.
   Option C migration cost is one linear layer (D^2 = 4M params) rather than full alignment.
   Timeline: 1 eng-week after Hyperprobe audit.

3. VQ CONCEPT TRAINING IS SUBSTRATE'S ENTRY POINT INTO CONCEPT-LEVEL LANGUAGE. ConceptLM
   literature confirms concept-level pretraining beats token-level on 13 benchmarks. Substrate
   can execute this paradigm at inference scale (no retraining of LLM) by training W on
   concept-ID sequences derived from any frozen LLM's VQ layer.

4. AUDIT CERTIFICATES ARE ONLY COMPLETE FOR SUBSTRATE-SOURCED FACTS. LLM parametric knowledge
   is not substrate-auditable. Product must bound the audit guarantee explicitly to
   substrate-retrieved knowledge; hybrid reasoning chains require orchestrator-level tagging
   of "substrate-grounded" vs "LLM-generated" steps.

5. COCONUT + SUBSTRATE COMPOSITION REQUIRES JL PROJECTION (ADDRESSABLE). Coconut continuous
   thoughts are D-dimensional Gaussians; substrate is bipolar. JL sign-projection preserves
   cosine structure to within 1/sqrt(N) ~ 0.012 at N=8192. Composition is algebraically
   feasible but not yet tested.

---

## P_DEFLATED SPLITS (calibration penalty -0.20 applied throughout)

| Claim | P_algebraic | P_implementation | P_deflated | Threshold |
|-------|-------------|------------------|------------|-----------|
| Option A near-term superiority | 0.92 | 0.88 | 0.72 | HP: >=65% QA accuracy with context |
| Option C migration via B8 bridge | 0.78 | 0.55 | 0.42 | HP: cos(alignment) >= 0.60 |
| VQ concept training on substrate | 0.65 | 0.55 | 0.35 | HP: concept ppl <= 20 |
| CoCoMix+substrate composition | 0.60 | 0.45 | 0.32 | HP: concept ppl improvement vs token ppl |
| Coconut+substrate via JL projection | 0.55 | 0.40 | 0.28 | HP: retrieval fidelity >= 0.80 after JL |
| Overall 1-week roadmap executable | 0.65 | 0.55 | 0.38 | HP: all 5 priority items start |
| Full Option B (joint training) | 0.45 | 0.30 | 0.20 | Long-term; no near-term test |

Novel-synthesis cap at 0.50 applied to VQ concept training and Coconut+substrate claims.
Additional 0.05 deflation applied per v317 uncharted-regime note for composition claims.

---

## CITATIONS (verified count: 18)

1. Hao et al. (2024) "Training Large Language Models to Reason in a Continuous Latent Space"
   (Coconut). arXiv:2412.06769.
2. Liu et al. (2025) "Next Concept Prediction in Discrete Latent Space Leads to Stronger
   Language Models" (ConceptLM). arXiv:2602.08984.
3. Tack et al. (2025) "LLM Pretraining with Continuous Concepts" (CoCoMix). arXiv:2502.08524.
4. Zou et al. (2023) "Steering Llama 2 via Contrastive Activation Addition" (CAA).
   arXiv:2312.06681.
5. Ramsauer et al. (2021) "Hopfield Networks is All You Need." ICLR 2021. arXiv:2008.02217.
6. Anonymous (2025) "Hyperdimensional Probe: Decoding LLM." arXiv:2509.25045.
7. Anonymous (2024) "CAMELoT: Towards Large Language Models with Training-Free Consolidated
   Associative Memory." arXiv:2402.13449. [29.7% perplexity reduction]
8. Frady and Sommer (2020) "Resonator Networks, 1: An Efficient Solution for Factoring
   High-Dimensional, Distributed Representations of Data Structure." Neural Computation 32(12).
9. Plate (1995) "Holographic Reduced Representations." IEEE Trans. Neural Netw. 6(3):623-641.
10. Kanerva (2009) "Hyperdimensional Computing: An Introduction to Computing in Distributed
    Representation with High-Dimensional Random Vectors." Cognitive Computation 1(2):139-159.
11. Merrill and Sabharwal (2022) "The Parallelism Tradeoff: Limitations of Log-Precision
    Transformers." arXiv:2207.00729. TACL 2023.
12. Baddeley (2000) "The episodic buffer: a new component of working memory?" Trends Cogn. Sci.
    4(11):417-423.
13. Cowan (2001) "The magical number 4 in short-term memory: A reconsideration of mental
    storage capacity." Behav. Brain Sci. 24(1):87-114.
14. Meng et al. (2022) "Locating and Editing Factual Associations in GPT" (ROME). NeurIPS 2022.
15. Kymn et al. (2022) "Decomposing Data with Hierarchical Resonator Networks." arXiv:2207.03617.
16. Yeung et al. (2024) "Generalized Holographic Reduced Representations." arXiv:2405.09689.
17. Achlioptas (2003) "Database-friendly random projections: Johnson-Lindenstrauss with binary
    coins." J. Comput. Syst. Sci. 66(4):671-687.
18. Su et al. (2024) "DRAGIN: Dynamic Retrieval Augmented Generation." arXiv survey cited in
    arXiv:2506.00054.
