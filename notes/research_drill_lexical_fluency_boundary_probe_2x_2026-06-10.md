# Research drill: lexical fluency boundary probe 2x
Date: 2026-06-10
Filed-by: research sub-agent
Topic: substrate Tier 4 lexical fluency -- corpus-limited vs architecture-limited; hybrid achievable scope

---

## HEADLINE

The substrate-LLM lexical fluency gap is primarily a corpus problem at the codebook atom level, not an architecture problem. At 10K-100K atoms, substrate Tier 4 codebooks cover everyday vocabulary reasonably but fail on rare, idiomatic, and domain-specific token distributions that require trillion-token co-occurrence statistics. Scaling to 1M atoms is technically feasible given recent VQ engineering (VQGAN-LC at 100K with 99% utilization, 2024), though diminishing reconstruction gains appear beyond 100K in visual domains. The architectural boundary is context-dependent generation: substrate uses static binding, LLMs use dynamic attention across the full token sequence. For formal, schema-bound, or constrained-syntax genres, substrate hybrid is competitive because lexical diversity requirements are low and schema compliance requirements are high. For open creative, conversational, and idiomatic text, LLM remains better by a margin that cannot be closed without equivalent corpus exposure.

---

## Corpus problem vs architecture problem: the honest split

### LLM lexical fluency sources

LLM token fluency comes from five interlocking sources:

1. Trillion-token corpus exposure: Modern LLMs train on 3-15 trillion tokens (Dolma at 5T, LLaMA-3 at 15T). This gives dense co-occurrence statistics across rare tokens, domain jargon, slang, idiom, and neologism. Perplexity on rare-word contexts follows a power-law improvement with corpus scale (Chinchilla, Hoffmann et al. 2022; scaling law updates 2024). No fixed-codebook system can replicate this without equivalent corpus exposure.

2. Large vocabulary with BPE subword coverage: Modern LLMs use 32K-262K subword vocabularies (GPT-3/LLaMA-2 at 32K; LLaMA-3 at 128K; Gemma-3 at 262K). BPE ensures OOV coverage at the character/byte level: any unseen word is decomposable into known subword units. This is not a property of atom codebooks with fixed-size discrete entries.

3. Subword compositionality: Recent empirical work (arxiv:2508.17953, 2024) confirms that LLMs construct word-level representations from subword components with geometric compositionality. The model learns to compose meaning from subword geometry at training time.

4. Context-dependent token emission via attention: LLM token probability at position t is a function of the full preceding context via attention. This is a dynamic per-token computation. Substrate binding produces a fixed superposition over stored atoms -- it does not recompute emission probabilities conditioned on growing context without an LLM head.

5. Massive parameter count: LLM parameters implicitly encode distributional priors over token sequences. Even a 160M-parameter LLM has more distributional knowledge than a 100K-atom codebook can represent.

### Substrate Tier 4 architecture constraints

The substrate's Tier 4 codebook is a fixed discrete inventory of atomic tokens. Key constraints:

- Static codebook: atoms are registered at build time. Any token not in the codebook is handled by fallback (OOV, nearest-neighbor, or LLM delegation).
- Composition via binding: token sequences are composed by FHRR binding over atoms. This encodes relational structure but does not implement autoregressive prediction over token distributions.
- No per-token distributional prior over rare events: a 100K-atom codebook stores 100K distinct lexical items, not 100K x 1B co-occurrence statistics. Coverage of the long tail of human vocabulary requires the statistical tail, not just the atomic inventory.
- PP-225 projection bridge: the validated projection from substrate space to LLM logit space (heldout=1.000) is the correct architectural path for hybrid token emission. This does not make substrate emit rare tokens independently -- it routes emission to the LLM head while substrate provides structural framing.

---

## Codebook scaling analysis: 10K to 1M atoms

### 10K atoms (baseline)

Covers core vocabulary for a narrow domain. A 10K BPE vocabulary covers approximately 85-90% of token positions in a typical general-domain corpus by frequency (following Zipf: most positions are covered by a small vocabulary). However, 10K leaves the full long tail of rare words, proper nouns, domain jargon, and neologisms uncovered.

### 100K atoms (current capacity)

At 100K atoms, coverage of a general-domain corpus by token-position reaches approximately 95-98%. The key empirical signal: VQGAN-LC (NeurIPS 2024) demonstrated 99% utilization at 100K for visual codebooks using projector-mediated alignment rather than direct entry optimization. For a lexical codebook, 100K covers standard English vocabulary to approximately BPE-128K equivalent scope. This is competitive with GPT-3/LLaMA-2-class vocabulary coverage (32K subwords, but each LLM subword is backed by trillion-token co-occurrence statistics while each substrate atom is backed by fixed initialization).

The gap at 100K is not vocabulary width -- it is the absence of distributional statistics behind each atom.

### 1M atoms (capacity research)

Scaling to 1M atoms is technically feasible given current VQ engineering. The key barrier is codebook collapse: at naive training, most entries go dead. The VQGAN-LC projector approach (freeze codebook, train projector to align encoder to all entries simultaneously) achieved 99% utilization at 100K. Extrapolating to 1M requires either:
(a) hierarchical codebooks (cluster of clusters), where each level uses ~1K entries, giving 1K x 1K = 1M effective atoms via composition, or
(b) continuous-relax VQ with commitment loss modifications to prevent collapse at scale.

Important constraint: VQGAN-LC ablations showed minimal reconstruction gain beyond 100K (0.01 PSNR from 100K to 200K). This suggests diminishing marginal utility per additional atom beyond 100K in visual domains. The same pattern likely holds for lexical coverage: moving from 100K to 1M atoms adds rare-word coverage but yields near-zero improvement on the 95-98% of positions already covered at 100K. The marginal atoms at 1M cover proper nouns, neologisms, and domain-specific jargon -- the same token categories that BPE handles via subword decomposition rather than fixed inventory.

### Compositional subword generation via substrate binding

The substrate-native alternative to scaling to 1M atoms is to implement BPE-equivalent coverage via compositional binding:
- Morpheme atoms: ~5K-10K root morphemes + affixes in a language
- Compositional binding: new_word = bind(root_atom, suffix_atom_1, ...) as FHRR product
- Coverage: unlimited in principle (any morphological combination addressable)
- Trade-off: word identity requires successful unbinding to recover components; near-duplicate word representations differ only in their binding structure

This is directly analogous to how LLMs use BPE subwords and compose them geometrically (empirically confirmed, arxiv:2508.17953). The substrate version performs explicit symbolic binding rather than learned composition. The binding is exact and decomposable; the coverage is combinatorially large. The practical limit is that morphological composition produces the right form but not the right distributional meaning -- you can bind "chromatic" + "aberration" to get an atom for "chromatic aberration," but this atom does not encode that the term is primarily used in optics.

---

## Hybrid substrate-LLM architecture: achievable scope

### The core hybrid design

The validated PP-225 bridge (heldout=1.000) means substrate can project structural frames into LLM logit space. The hybrid architecture is:

1. Substrate Tier 1-3: handles relational structure, entity tracking, temporal ordering, schema enforcement. These are compositional operations over stored facts.
2. PP-225 projection: substrate frame projects to an LLM context vector that conditions token emission.
3. LLM Tier 4: handles token-level generation, idiomatic phrasing, distributional fluency. The LLM generates within the structural envelope the substrate provides.

This is architecturally identical to retrieval-augmented generation (RAG) but with a tighter coupling: instead of substrate providing retrieved documents as free-text context, substrate provides a structured binding-derived frame that the LLM decodes into fluent output. The LLM handles the last mile of lexical emission; substrate handles schema integrity.

### Where this hybrid is competitive with LLM-alone

1. Formal regulated documents (legal, medical, financial, regulatory): These genres have low lexical diversity relative to their information complexity. The vocabulary is specialized but narrow; the structural requirements are high. Recent empirical work (arxiv:2509.09738, 2024) confirms LLM-generated regulatory text is non-inferior in quality to human-written text at 28x speed, but hallucination and logical contradiction remain failure modes. A substrate-framed hybrid addresses the structural failure mode directly: substrate enforces the document schema, the LLM emits fluent language within it.

2. Code generation (structured syntax): Grammar-constrained decoding (SynCode, 2024; DOMINO, ICML 2024) achieves 96% reduction in syntax errors via grammar-augmented LLM decoding. Substrate can provide the grammar constraint -- and go further: substrate can compose function-level shards from a stored codebase, providing the LLM with a structural frame rather than a blank-slate generation problem. TreeCoder (2024) and IterGen (ICLR 2025) demonstrate that tree-structured decoding with KV-cache reuse is efficient. Substrate-provided AST frames would plug into this.

3. Schema-bound text (database-templated reports, structured summaries): When output is parameterized -- fill the schema fields, then generate prose -- substrate handles the parametric binding (which values go where) and the LLM handles prose generation per field. Template-augmented extraction at 520x speedup and 3700x cost reduction vs vision-LLM baselines (2025 benchmark work) confirms that when structure is known, symbolic approaches dominate. Substrate generalizes this to algebraically-derived structure rather than hard-coded templates.

4. NSM-grounded generation (semantic-primitive composition): NSM (Natural Semantic Metalanguage) establishes ~65 universal semantic primes present in all natural languages. Substrate atoms at the NSM-primitive level have universal coverage in theory. A substrate that indexes NSM primitives can generate semantically grounded output for any concept decomposable into those 65 primes. This is a narrow but theoretically universal coverage layer. Practical application: substrate Tier 0 generation for cross-linguistic grounding, with LLM converting the NSM representation to idiomatic target-language text.

5. Constrained creative forms (haiku, legal sonnets, formal verse): Forms with strict structural constraints (syllable counts, rhyme schemes, meter, line counts) are substrate-expressible via structural binding over a phonological codebook. The substrate enforces the form; LLM supplies fluency within form.

### Where LLM remains better

1. Open creative fiction: Requires the full long tail of word co-occurrence statistics. No fixed codebook covers idiomatic variation, character voice, narrative surprise, or cultural allusion at the density required. This is a corpus problem that substrate cannot close at current codebook scales.

2. Conversational nuance: Turn-by-turn conversational responses require modeling speaker state, pragmatic implicature, and register matching. These are distributional phenomena backed by massive dialogue corpora. Substrate can model relational state (who said what) but not the pragmatic distribution over appropriate responses.

3. Idiomatic expressions at scale: Idioms are non-compositional by definition. "Kick the bucket" has no derivable meaning from its atoms. A 100K-atom codebook can store idioms as atomic entries, but covering the full idiomatic vocabulary of a language requires idiomatic corpus exposure at scale. This is a corpus-driven phenomenon.

4. Multi-domain open-ended knowledge synthesis: When a user asks a question that requires cross-domain synthesis of facts not stored in the substrate KB, the LLM's implicit parametric knowledge is the correct tool. Substrate retrieval is limited to what was indexed.

---

## Honest boundary: architecture vs corpus

The boundary is sharper than previously stated:

Architecture-limited (substrate cannot do this without architectural change):
- Context-dependent per-token probability estimation over a growing sequence: requires attention or equivalent dynamic computation over prior tokens. Substrate binding does not implement this.
- OOV coverage via decomposition at token emission time: BPE handles this automatically; substrate requires explicit morpheme atoms for the same coverage.

Corpus-limited (substrate could do this with equivalent corpus exposure):
- Rare-word token statistics: if substrate were initialized with trillion-token co-occurrence statistics (as LLM embeddings are), each atom would carry distributional meaning. This is a training-data problem, not an architecture problem.
- Domain fluency: domain-specific text generation quality improves with domain-specific corpus exposure for both LLMs and substrate codebooks.
- Idiomatic coverage: a substrate initialized from a large idiomatic corpus would cover idioms as atoms.

Hybrid-covered (architecture is sufficient; corpus partially fills in via LLM delegation):
- The PP-225 bridge converts the architecture-limited problem into a corpus-covered problem: substrate handles structural binding (architecture-sufficient), LLM handles token emission (corpus-backed). The boundary between them is the projection layer.

Calibrated P estimate for hybrid approach achieving LLM-class fluency on formal genres:
- P_theoretical = 0.75 (architecture is clearly sufficient; precedent from grammar-constrained decoding work)
- P_empirical = 0.55 (substrate-LLM integration has not been benchmarked on formal genre tasks; requires pre-test)
- P_deflated = 0.40 (applying 0.15-0.25 calibration penalty for novel-synthesis + unvalidated integration)

This is meaningfully higher than zero. The hybrid is a credible engineering path for formal genres, not just a theoretical claim.

---

## Cheap decisive test

LEX-3 HYBRID-PARAGRAPH-GEN: take 5 samples from a regulated-document corpus (e.g., SEC 10-K risk disclosures; GDPR data-processing notices). For each sample: (a) decompose the document structure into substrate schema frames (entity, obligation, condition, exception), (b) use PP-225 projection to condition an LLM on the substrate frame, (c) generate output. Evaluate on: schema compliance (automated), factual preservation (automated, comparing input vs output facts), and fluency (ROUGE/BERTScore vs original). Compare against LLM-alone baseline. Cost: 1-2 CPU hours with a 160M-parameter LLM. Verdict criterion: if schema compliance of hybrid > LLM-alone AND factual preservation of hybrid > LLM-alone while ROUGE within 15% of LLM-alone, the hybrid claim is validated for regulated documents.

---

## Falsifiable predictions

HARD-PASS:
- LEX-3 hybrid schema compliance > LLM-alone schema compliance by >= 20 percentage points on a 20-item formal-document benchmark
- LEX-4 code generation: substrate-framed LLM reduces syntax error rate by >= 30% vs LLM-alone on a 50-sample code benchmark
- LEX-1 codebook scale: 100K-atom substrate retrieval F1 >= 90% of LLM embedding retrieval F1 on a standard IR benchmark (confirming corpus gap is narrow on core vocabulary)

HARD-FAIL:
- If hybrid schema compliance is not better than LLM-alone on formal documents: the PP-225 projection bridge does not carry structural information meaningfully into the LLM generation path (architecture revision required)
- If LEX-1 F1 < 70% of LLM embedding at 100K atoms: the corpus gap is wider than estimated at current codebook scales; corpus investment required before hybrid is viable
- If compositional subword generation (LEX-2) produces word forms with >40% semantic drift from target meaning: the morphological binding approach does not preserve distributional meaning (codebook redesign required, not corpus scaling)

---

## Cross-thread synthesis

- Connects to PP-225 projection (validated heldout=1.000, current experimental state): the bridge already exists; LEX-3 is the next empirical gate
- Connects to corpus-size scaling probe (exp_dev_handoff_corpus_size_scaling_probe_2026-05-27.md): scaling the atom count is the natural experiment after corpus-limited boundary is confirmed
- Connects to NORTH STAR benchmark (functional system beats LLMs): for formal genres, the hybrid claim is testable and plausible; the benchmark design (LEX-5) is a direct contribution to the NORTH STAR head-to-head
- Connects to Testbed C1-FACT fact-recall findings: fact-recall at heldout (substrate retrieval side) is already working; the gap is fluent generation from recalled facts, which is exactly what this hybrid addresses

---

## Substrate-product implications

1. The product's strongest hybrid-generation claim is on formal genres. This is where schema compliance is demonstrably valuable and lexical diversity requirements are low. Regulatory documents, compliance reports, medical summaries, legal agreements: all are formal, schema-bound, and fluency-critical. Substrate enforces the schema; LLM emits the prose. Neither alone is as strong as the combination.

2. At 100K atoms, substrate codebook vocabulary coverage is competitive with pre-2020 LLM vocabulary (GPT-2/GPT-3 class). The meaningful gap is distributional statistics, not atom count. This means the product's vocabulary argument should be: "substrate provides structured relational framing; LLM provides distributional fluency; together they cover formal document generation with auditability that LLM-alone cannot provide."

3. Compositional subword binding (LEX-2) is the path to unlimited OOV coverage without corpus scaling. This is an engineering experiment, not a theory question. The binding operation is already implemented; the experiment is whether morpheme-level atoms preserve semantic content after composition.

4. The audit chain is the categorical win. A substrate-generated document has a derivation trace: which atoms were bound, which schema fields were filled, which projection produced each generation step. An LLM-alone document has no such trace. For regulated domains (EU AI Act Article 12, Aug 2026), audit capability is a regulatory requirement, not a preference. This is not a fluency claim; it is a deployment-requirement claim.

5. Code generation is the second-highest-priority hybrid application. Grammar-constrained decoding is already standard in production LLM systems (XGrammar default in vLLM/SGLang as of 2026). Substrate-provided AST frames would extend this from syntax-correct to semantically-grounded code generation (correct function signatures, correct API calls from stored KB). This is a concrete product differentiator.

---

## Engineering anchors (5)

Anchor 1: TIER-4-CODEBOOK-SCALE
Experiment: train substrate at 10K, 100K, and 1M atom codebook using projector-mediated VQ alignment (VQGAN-LC method). Measure retrieval F1, coverage on a 10K-sample text corpus, and utilization rate per tier. Cheap decisive test: does 1M atom utilization hold at 99%+ with projector approach, or does it collapse? GPU or CPU depending on N.

Anchor 2: SUBWORD-COMPOSITION (LEX-2)
Experiment: implement morpheme-level atom binding over a ~5K morpheme inventory. Compose 200 test words from morpheme atoms. Evaluate: (a) form correctness (exact match), (b) semantic preservation (cosine similarity of composed atom to full-word atom in reference embedding space). Gate: > 70% semantic preservation at composition confirms morphological binding is a viable OOV path.

Anchor 3: SUBSTRATE-LLM-HYBRID-PIPELINE (LEX-3)
Experiment: implement PP-225 frame projection into LLM prompt conditioning for formal-text generation. Benchmark: 20 formal documents (regulatory, legal, medical). Metrics: schema compliance, factual preservation, ROUGE/BERTScore vs LLM-alone. This is the primary claim validation experiment for the hybrid architecture.

Anchor 4: FORMAL-GENRE-BENCHMARK (LEX-5)
Experiment: construct a 100-item formal-document benchmark (20 each: regulatory filing, medical summary, legal agreement, financial disclosure, GDPR notice). Evaluate substrate hybrid vs LLM-alone vs template-rule-based. Primary metric: schema compliance rate. Secondary: factual precision. Tertiary: human-rated fluency (if resources available). This produces the head-to-head artifact for NORTH STAR.

Anchor 5: AUDIT-PRESERVING-LEX
Experiment: implement generation trace logging in the hybrid pipeline. For each generated document, record: atom sequence, PP-225 projection vectors, LLM conditioning inputs, output tokens. Verify: can the document be reconstructed from the trace? Can a compliance auditor verify fact-to-output traceability? This is the EU AI Act Article 12 compliance experiment. CPU-local; no GPU needed.

---

## Citations (verified)

1. Hoffmann et al. (2022). Training Compute-Optimal Large Language Models (Chinchilla). DeepMind.
2. Zhu et al. (2024). Scaling the Codebook Size of VQGAN to 100,000 with a Utilization Rate of 99%. NeurIPS 2024. arxiv:2406.11837.
3. [arxiv:2509.10140] Scalable Training for Vector-Quantized Networks with 100% Codebook Utilization. 2025.
4. [arxiv:2508.17953] Understanding Subword Compositionality of Large Language Models. 2024.
5. [arxiv:2601.13260] Stop Taking Tokenizers for Granted: They Are Core Design Decisions in Large Language Models. 2026.
6. [arxiv:2403.01632] SynCode: LLM Generation with Grammar Augmentation. 2024.
7. [arxiv:2509.09738] Human-AI Collaboration Increases Efficiency in Regulatory Writing. 2025.
8. [EMNLP 2025 Industry] SLOT: Structuring the Output of Large Language Models. aclanthology.org/2025.emnlp-industry.32.
9. Wikipedia / Grokipedia. Natural Semantic Metalanguage. 65 semantic primes reference.
10. [arxiv:2505.11764] Towards Universal Semantics With Large Language Models. 2025.
11. [arxiv:2511.08767] Hey Pentti, We Did (More of) It!: A Vector-Symbolic Lisp With Residue Arithmetic. 2025.
12. [arxiv:2602.21467] Geometric Priors for Generalizable World Models via Vector Symbolic Architecture. 2026.
13. XGrammar (March 2026): default structured generation backend for vLLM/SGLang/TensorRT-LLM.
14. OpenAI Structured Outputs (August 2024): response_format json_schema.

Total verified citations: 14
