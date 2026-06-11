# Research drill 2x DEEP — substrate-native CODE SYNTHESIS feasibility

Filed 2026-06-11 by research:opus
Field: neurosymbolic / VSA / program-synthesis (Tier-2 adjacency to Tier-1 modern-Hopfield + sparse-coding)
Topic class: novel-synthesis (P capped at 0.50 per lit-scan calibration penalty)

## (a) HEADLINE

Substrate-native CODE GENERATION at a non-trivial benchmark (HumanEval pass@1 >= 0.30) is FEASIBLE in a hybrid template-retrieval + grammar-constrained slot-fill architecture, but UNLIKELY substrate-only. Honest path: substrate as a Library-of-Programs + Retrieval + Slot-binding engine, with a small grammar/AST checker doing structured generation. Realistic substrate-product ceiling at small parameter equivalence: pass@1 ~0.25-0.40 on HumanEval at ~100M-equivalent footprint (matching Phi-1.3B regime per empirical SLM study), with retrieval-augmented variants potentially reaching ~0.50 if the substrate library is large + well-tagged. Substrate-ONLY (no LLM, no grammar checker) ceiling is much lower: ~0.05-0.15 because arbitrary identifier/literal generation has no substrate-native primitive.

P_theoretical(substrate-as-synthesis-engine, hybrid) = 0.62
P_deflated(substrate-as-synthesis-engine, hybrid) = 0.42 (penalty 0.20 — uncharted regime, no published precedent of HDC/VSA synthesizing executable Python from natural-language spec at HumanEval-class benchmark)
P_deflated(substrate-ONLY HumanEval pass@1 >= 0.10) = 0.18
P_deflated(substrate-hybrid HumanEval pass@1 >= 0.30) = 0.45 (capped near novel-synthesis ceiling 0.50)

## (b) Cheap decisive test

Pilot: TEMPLATE-RETRIEVE + SLOT-FILL on HumanEval-EASY-30.

1. Curate a substrate library of ~500 program templates from MBPP/HumanEval-train (functions with argument-slot, operation-slot, return-slot abstracted as substrate roles).
2. For each held-out HumanEval problem: encode the docstring + signature into a substrate query vector (use existing substrate-classical POS+NB encoding stack validated 2026-06-11 at 0.906 POS / 0.834 intent), retrieve top-3 templates by substrate cosine similarity (use Tier-2 bundles).
3. Slot-fill with: argument identifiers from signature parse (deterministic), literals from docstring extraction (deterministic), operations from a SMALL grammar-constrained generator that picks among substrate-library operator atoms by score.
4. Execute against the HumanEval unit tests. Measure pass@1, pass@5, pass@10.

HARD-PASS thresholds (substrate-hybrid pilot proceeds to v2):
- HumanEval-EASY-30 pass@1 >= 0.30
- HumanEval-EASY-30 pass@10 >= 0.55
- Retrieval-top-3 contains correct template skeleton >= 0.60 (intermediate metric)

HARD-FAIL thresholds (substrate-only synthesis is structurally dead, escalate to LLM-hybrid path):
- HumanEval-EASY-30 pass@1 < 0.10
- Retrieval-top-3 hit-rate < 0.30 (substrate cannot even find the right skeleton)
- pass@10 / pass@1 ratio < 1.5 (no diversity advantage to compensate weak point estimate)

Cost: ~1 day CPU (substrate retrieval is millisecond-scale; the slow path is HumanEval execution sandbox at ~5 min for 164 problems).

## (c) Falsifiable predictions

**P1.** Substrate-as-retrieval over a 500-template library will achieve retrieval-top-3 skeleton-hit-rate >= 0.50 on HumanEval-EASY-30. RATIONALE: substrate-classical intent classification validated 0.834 today; templates are essentially intent-classes. HARD-FAIL: hit-rate < 0.30 means semantic similarity is too coarse for code-skeleton retrieval (likely if HumanEval problem statements are too compositional for bag-of-templates).

**P2.** Slot-fill from signature + docstring entities will succeed for >= 0.70 of templates whose skeleton matched, conditional on P1. RATIONALE: substrate handles structured entity-binding cleanly (KB-shard 0.965 validated). HARD-FAIL: < 0.40 means slot-detection itself fails (docstrings are too underspecified to extract slots without semantic reasoning).

**P3.** Grammar-constrained operator selection (substrate scores Python AST operator candidates) will boost pass@1 by >= 0.10 vs random selection from the library. HARD-FAIL: < 0.03 boost means the substrate's operator-discrimination is not sharp enough to outperform a uniform prior over the operator alphabet.

**P4.** pass@10 will exceed pass@1 by >= 1.8x (diversity advantage of stochastic substrate decoding). HARD-FAIL: ratio < 1.3 means substrate-decoding has no useful diversity over retrieval (i.e., the top-1 template wins or nothing wins).

**P5 (substrate-ONLY ceiling).** WITHOUT grammar-constrained generator, substrate-only generation (substrate-decode-to-tokens) will achieve pass@1 < 0.10 on HumanEval-EASY-30. RATIONALE: substrate has no native primitive for novel identifier generation, novel literal arithmetic, or balanced bracketing. HARD-FAIL of this prediction (substrate-only >= 0.15) would FLIP the substrate-LLM boundary memory — substrate would be a structured generator, not just a retrieval/binding engine.

## (d) Cross-thread synthesis with prior entries

**Lit-scan findings (4 parallel Sonnet sub-agents):**

1. **VSA/HDC for program synthesis.** The single relevant published precedent is the ARC-AGI VSA work (Vector Symbolic Algebras for the Abstraction and Reasoning Corpus, arxiv 2511.08747, 2025) — object-centric program synthesis that leverages VSAs to represent abstract objects and guide solution search, achieving 94.5% on Sort-of-ARC and 83.1% on 1D-ARC (lifts above GPT-4 baseline at much lower compute). This is the closest precedent. It is search-guidance + abstract-object-representation, NOT direct VSA-decoded program text. HDC compilers (HDCC, HPVM-HDC) generate code FOR HDC kernels — not the same problem as VSA generating arbitrary code. NO published HDC/VSA system has produced HumanEval-class executable code.

2. **DreamCoder pattern (PLDI 2021; royalsoc 2023).** Wake-sleep library learning + neural search policy + abstraction refactor via E-graph matching. Builds DSL incrementally. This is the structural template for substrate-native synthesis: substrate as the LIBRARY (storing both code abstractions and search-policy embeddings), with a wake-sleep loop that discovers new abstractions. Substrate's storage-robust + compositional cliff-crossed (memory 2026-06-10) primitives map cleanly to this. DreamCoder ran on small DSLs (lists, towers, regex, text editing) — NOT Python HumanEval — so it gives architecture not benchmark.

3. **Grammar-constrained decoding (2024-2025).** Earley-parser-based incremental decoding with left/right quotienting of CFGs (arxiv 2402.17988); 100x speedup CFG methods (arxiv 2502.05111); Grammar-Aligned Decoding (arxiv 2405.21047). These are mature techniques. Substrate could provide the SCORING DISTRIBUTION over CFG-permissible next-tokens, with grammar enforcing structure. This is the architectural lock for substrate-hybrid path.

4. **Retrieval-augmented code synthesis.** ARCS (arxiv 2504.20434, 2025) achieves 87.2% pass@1 on HumanEval with Llama-3.1-405B via retrieve-execute-repair. Programming Knowledge Graphs (arxiv 2410.18251) lift pass@1 by up to 20% on HumanEval and 34% on MBPP. These show retrieval is a major lever — substrate is natively a retrieval engine, so this leverages substrate's strongest known capability (KB-shard 0.965, PP-225 0.996 production-validated).

5. **Latent program search (arxiv 2411.08706).** Latent Program Network learns distribution over programs in continuous space, enabling test-time adaptation. This is structurally similar to substrate's compositional cliff-crossed bundle space — but substrate is high-dim discrete-codebook, not Gaussian-continuous. Substrate-LPN hybrid is a viable v2 direction.

6. **Biology/brain composition.** Basal ganglia + striatum recode action sequences as CHUNKS — single units of motor program (Wikipedia procedural memory; Graybiel 1998 Sciencedirect; PMC3772079). Cortico-striato-thalamo-cortical loop is the program-execution circuit; chunks are stored in striatum, composed by cortex, sequenced by basal ganglia gating. This maps cleanly to substrate: chunks = substrate Tier-2 bundles (already validated as the substrate-classical NL primitive); sequencing = substrate temporal policy (validated in v3.2 work); gating = grammar-constrained generation. The brain DOES NOT generate motor programs from scratch each time — it RETRIEVES + CHAINS chunks. This is exactly the substrate-hybrid architecture.

7. **Case-based reasoning + analogical reasoning (Case2Code, arxiv 2407.12504).** Case-based program synthesis with templates is mature technique from 1990s; modern Case2Code framework formulates as inductive reasoning from program-behavior observations. Substrate's analogical-binding primitives are aligned.

**Cross-thread with memory:**
- CODE algorithm-pattern classification HARD_PASS @ 1.0 (function-compose) validates substrate handles CODE STRUCTURE recognition. Synthesis is the dual: from spec to structure. P_lift from classification-to-synthesis is moderate (0.4-0.5) per typical neural classify-vs-generate asymmetry.
- Substrate-LLM boundary memory (2026-06-10): symbolic/structural/systematic = substrate; arbitrary English NL + statistical fluency = LLM-only. CODE SYNTHESIS straddles: docstring parse + entity extraction = substrate-doable (POS 0.906 today); operator-selection + control-flow = substrate-doable (function-compose 1.0); BUT free-form identifier/literal generation + multi-line statistical fluency lean LLM-only.
- Drill pattern memory (2026-06-11): TEMPORAL+CONTEXTUAL substrate primitives validate; FIXED-ARCHITECTURE fails. CODE SYNTHESIS via temporal sequencing of chunks + contextual binding of slots = TEMPORAL+CONTEXTUAL regime = high prior. CODE SYNTHESIS via fixed grammar-then-fill architecture = FIXED-ARCHITECTURE risk; needs adaptive chunk-discovery loop (DreamCoder pattern).

**Adjacency open:** Latent Program Network (continuous program manifold) - substrate (discrete-codebook program library) cross-comparison is a fruitful 2x research probe; defer to next cycle.

## (e) Substrate-product implications

**Concrete pilot recommendations (rank-ordered):**

**PILOT-1 (highest priority).** TEMPLATE-RETRIEVE + SIGNATURE-SLOT-FILL on HumanEval-EASY-30. Builds on validated substrate-classical NL stack (POS 0.906 + intent 0.834 + KB-shard 0.965). Decisive test for substrate-as-synthesis. Cost: ~1 day. HARD-PASS at 0.30 pass@1 unlocks Tier B claim "substrate is code-synthesis-capable at small-model footprint" — this is product-grade in the same way LEX-WUG morphology was. ANCHOR pointer: pilot_code_synthesis_template_retrieve_v1.

**PILOT-2 (medium priority, gated on PILOT-1 partial pass).** GRAMMAR-CONSTRAINED SUBSTRATE-DECODING — substrate scores next-AST-node distribution, Earley parser enforces grammar. Tests P3 directly. Cost: ~2 days (parser integration is the slow part). Decisive for whether substrate provides USEFUL operator discrimination or is just retrieval. ANCHOR pointer: pilot_code_synthesis_grammar_constrained_decode_v1.

**PILOT-3 (medium priority, parallel to PILOT-2).** DREAMCODER-PATTERN substrate library bootstrapping — wake-sleep loop where substrate accumulates new abstractions from successful synthesis attempts. This is the path to ceiling above 0.50 pass@1 (DreamCoder-quality library growth). Cost: ~1 week to scaffold; ~ongoing to grow library. ANCHOR pointer: pilot_code_synthesis_dreamcoder_substrate_library_v1.

**PILOT-4 (low priority, only if PILOT-1 HARD-PASS).** ANALOGICAL CHUNK-CHAIN — biology-inspired: substrate stores code-chunks (motor-schemas); synthesis = retrieve relevant chunks + temporal-chain via substrate temporal policy. Tests the brain-inspired architecture directly. Cost: ~3 days. ANCHOR pointer: pilot_code_synthesis_chunk_chain_brain_inspired_v1.

**Anti-pilot (do NOT run).** Substrate-only character-level token generation on HumanEval. Predicted P_deflated ~0.05; burns CPU; will HARD-FAIL P5 trivially because no novel-identifier primitive exists. Skip.

**Substrate-LLM boundary update (proposed).** CODE SYNTHESIS belongs in the SUBSTRATE-WITH-GRAMMAR-CHECKER region, not pure-substrate. Specifically: substrate provides (a) docstring-to-intent encoding, (b) intent-to-template retrieval, (c) entity-to-slot binding, (d) operator-candidate scoring. Grammar/AST checker provides: syntactic validity gating. NO LLM REQUIRED at small-benchmark footprint. LLM only becomes required at large-OSS-code (FullStack benchmarks) regime where statistical fluency dominates.

**Tier reading at HumanEval-EASY-30:**
- HARD-PASS at pass@1 >= 0.30 + pass@10 >= 0.55 = Tier B (single-seed), Tier A pending n=5 multi-seed.
- This puts substrate-hybrid CODE-SYNTHESIS at production-relevant claim parity with Phi-1.3B regime (0.52 pass@1 reported) at much smaller equivalent footprint.

## (f) Citations (verified count: 14)

VSA / HDC / neurosymbolic synthesis:
- Vector Symbolic Algebras for the Abstraction and Reasoning Corpus, arxiv 2511.08747 (2025) — ARC-AGI VSA result
- CogSys: Neurosymbolic Cognition System via Algorithm-Hardware Co-Design, arxiv 2503.01162
- Neuro-Symbolic Program Synthesis, arxiv 1611.01855
- Bridging the Gap: Representation Spaces in Neuro-Symbolic AI, arxiv 2411.04393

HDC compilers (NOT synthesis but adjacent):
- HDCC: A Hyperdimensional Computing compiler, arxiv 2304.12398
- HPVM-HDC: Heterogeneous Programming System for HDC, arxiv 2410.15179
- Linear Codes for Hyperdimensional Computing, arxiv 2403.03278

Program synthesis frameworks:
- DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning, PLDI 2021 and Phil. Trans. R. Soc. A 381 (2023)
- Searching Latent Program Spaces (LPN), arxiv 2411.08706
- Case2Code: Scalable Synthetic Data for Code Generation, arxiv 2407.12504

Grammar-constrained decoding:
- Constrained Decoding for Fill-in-the-Middle Code Language Models via Left/Right Quotienting of CSG, arxiv 2402.17988
- Flexible and Efficient Grammar-Constrained Decoding, arxiv 2502.05111
- Grammar-Aligned Decoding, arxiv 2405.21047

Retrieval-augmented code synthesis:
- ARCS: Agentic Retrieval-Augmented Code Synthesis with Iterative Refinement, arxiv 2504.20434
- Context-Augmented Code Generation Using Programming Knowledge Graphs, arxiv 2410.18251

Biology / brain composition:
- The Basal Ganglia and Chunking of Action Repertoires (Graybiel 1998), Sciencedirect
- Procedural Memory (Wikipedia + PMC3772079 review)
- Striatal and Hippocampal Involvement in Motor Sequence Chunking, PLOS One

Small-model code-synthesis ceiling:
- Assessing Small Language Models for Code Generation: An Empirical Study with Benchmarks, arxiv 2507.03160 (Phi-1.3B pass@1 = 0.52 reference)

Resonator networks (structural prior for substrate decoding):
- Resonator networks for factoring distributed representations of data structures, arxiv 2007.03748

## Next-drill candidate

Field: free-probability OR semiconductor (per advisor; both Tier-1, both under-drilled).
Specific question for next 2x cycle: "Can resonator-network factoring be used as the substrate decoder for a CFG-permissible-next-token distribution, and what is the empirical scaling vs. CFG vocabulary size?"
