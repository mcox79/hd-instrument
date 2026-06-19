# RESEARCH DRILL 3x DEEP -- Substrate Language Capabilities BEYOND Tier-A Roster

Date: 2026-06-12
Drill type: 3x DEEP literature + cross-domain probe
Safety: ASCII only; generic queries only; no LLM-as-judge; lit-scan calibration penalty applied (deflate P 0.15-0.25; cap novel-synthesis P at 0.50)
Context: substrate dominates structural-cognition + low-data regime; LLM dominates full-data unstructured English. USER pushback: "we still have language and creativity capabilities and we're going to drill that hard."

================================================================
Q1: WHERE does substrate structured-cognition UNIQUELY beat LLM in language?
================================================================

Strongest substrate-distinctive corridors (from lit + first-principles):

(a) Low-data / few-shot domain adaptation
    HD/VSA "excels in few-shot learning scenarios" via low-resolution
    hypervector representations (Kleyko et al. 2021 survey). HyperEmbed
    (n-gram statistics) competitive with deep models on small-corpus text
    classification at fraction of compute. Substrate aux-features shrink
    with data (memory rule) -> low-data regime is substrate-OPTIMAL.
    Brain analogue: hippocampal one-shot binding (sharp-wave ripples
    orchestrate ATL semantic networks; bioRxiv 2024.04.10).

(b) Adversarial / noisy-text robustness
    LLMs degrade under char-level noise, synonym swap, paraphrase
    (Nature Sci Rep 2025; arXiv 2405.02764). Substrate compositional
    primitives + bundling cleanup are intrinsically denoising
    (associative retrieval). Substrate does NOT pattern-match surface
    forms the way attention does.
    Brain analogue: ATL category-general semantic representation
    robust to surface lexical noise (Hagoort/Federmeier paradigm).

(c) Explicit slot-role binding (coreference, SRL)
    Substrate HRR slots ARE the structure attention only approximates.
    Lee et al. (EMNLP 2017) end-to-end coref needs implicit span-binding;
    substrate has it natively via P^k indexed binding.
    Brain analogue: prefrontal role-filler binding via theta-gamma
    nesting (Hasselmo/Lisman).

(d) Morphologically rich languages (Turkish, Finnish, Hungarian)
    SPMRL shared task (Tsarfaty et al., CL 2013): MRLs are
    inherently hard for word-as-terminal parsers; agglutinative
    morphemes are EXPLICIT compositional structure. Substrate
    FHRR bind(stem, suffix_chain) is the natural primitive; LLM
    BPE blurs morpheme boundaries.

(e) Programmatic / templated generation
    Already validated in substrate-UNIFIED-compositional-generation
    memory: coding + storytelling + math share ONE compositional
    engine. Smolensky TPR (1990) gives the theoretical scaffold;
    Soft TPR (arXiv 2412.04671) is recent extension.

================================================================
Q2: CREATIVE / GENERATIVE language capabilities via compositional engine
================================================================

Substrate has the algebraic primitives to do generation LLMs do
statistically:

- Novel compositional generation: HRR_bind(structure_template,
  content_fillers) -- structure as schema, fillers as LEX_T atoms.
- Analogical sentence generation a:b :: c:?: substrate bind/unbind
  is literal Smolensky-Lee (arXiv 1601.02745) "Basic Reasoning with
  TPR" -- predicate-logic inference reduced to tensor algebra.
- Schema-guided story generation: substrate has solution_history
  partition; can generate by structural reuse rather than next-token
  sampling.
- Code synthesis via templated bind: structure=code template
  (for/if/while), fillers=identifiers. Already substrate-validated
  pattern.
- Schema-driven summarization: substrate emits SCHEMA
  (problem -> solution; cause -> effect) not surface paraphrase.

Brain analogue: Hagoort's MUC (memory-unification-control) model --
unification at LIFG over ATL-stored fragments is exactly substrate
bind-over-cleanup-retrieved-atoms.

================================================================
Q3: LITERATURE anchors
================================================================

VSA / HRR NLP:
- Plate (1995) HRR original
- Kleyko, Rachkovskij, Osipov, Rahimi (2021) HD/VSA survey Part II
  (applications, cognitive models) -- arXiv 2112.15424
- Frady, Sommer (Neural Comp 2023) "Efficient decoding of
  compositional structure in holistic representations"
- Frady, Kleyko, Sommer (IEEE TNNLS 2023) variable binding for SDR
- Recasens et al. (arXiv 2512.14709) "Attention as Binding: VSA
  Perspective on Transformer Reasoning"

Compositional / TPR / categorical:
- Smolensky (1990) TPR variable binding
- Smolensky, Lee (arXiv 1601.02745) Basic Reasoning with TPR
- Coecke, Sadrzadeh, Clark (2010) DisCoCat categorical compositional
  distributional
- Soft TPR (arXiv 2412.04671) flexible distributed compositional
- McCoy et al. (arXiv 1812.08718) RNNs implicitly implement TPR

Structural NLP:
- Tsarfaty et al. (CL 2013) MRL parsing special issue
- Lee et al. (EMNLP 2017) end-to-end neural coref
- Liu et al. (EMNLP 2020) SRL as syntactic dep parsing
- Liu et al. (COLING 2020) Multilingual Neural RST Discourse Parsing

LLM brittleness:
- Nature Sci Rep 2025 LLM robustness against perturbation
- arXiv 2405.02764 empirical study LLM adversarial robustness

Brain anchors:
- Hagoort MUC model (LIFG unification)
- Friederici syntactic hierarchy (BA44/45)
- Federmeier semantic memory ATL
- bioRxiv 2024.04.10 hHFO-cortical ripples orchestrate semantic nets

================================================================
Q4: CONCRETE EXPERIMENTAL DIRECTIONS
================================================================

C1. Adversarial NER under char-noise: train substrate NER on clean,
    test on 5/10/20pct char-perturbed inputs; compare LLM 0.5B/1.5B
    same protocol. Predicted substrate degrades less.

C2. MRL dependency parsing on UD Turkish-IMST + Finnish-TDT:
    substrate FHRR bind(stem, agglutinative-suffix) primitive +
    Tier-A dep-parse pipeline. Compare UAS vs LLM zero-shot.

C3. Few-shot transfer curve: NER 4-type at 1pct/5pct/10pct/50pct/100pct
    training; measure substrate-vs-LLM crossover point.

C4. OntoNotes coreference via P^k multi-occurrence binding (PP-401
    extension); MUC/B^3/CEAF-phi4 vs e2e-coref baseline.

C5. PropBank SRL via Tier-A dep-parse + role-binding algebra.

C6. RST discourse parsing on RST-DT (only 385 docs -- low-data sweet
    spot per lit). Substrate schema-binding over EDU embeddings.

C7. Text-to-code synthesis via HRR composition templates on a small
    DSL (HumanEval-easy subset or Karel-style).

C8. Code-switching POS/NER on LinCE benchmark (Eng-Spa, Eng-Hin):
    substrate structural primitives may transfer where shared BPE
    breaks down.

C9. Low-resource MT inductive-bias baseline on FLORES-low-resource
    pairs (Sw-En, Tl-En): substrate as alignment-bias provider.

================================================================
Q5: WHERE LLM DOMINATES -- DO NOT COMPETE
================================================================

- Full-data English text generation at GPT-class scale (creative
  prose, long-form writing)
- Comprehension/inference on long unstructured passages (LAMBADA,
  NarrativeQA) -- but USER rule: "comprehension is brain-implementable;
  substrate equivalents EXIST" -- treat as substrate-corpus-deficient
  not architectural ceiling, file as Tier-2 not Tier-1 retreat.
- Open-domain QA where corpus IS the world (TriviaQA-large)

================================================================
Q6: SUBSTRATE-PRODUCT POSITIONING
================================================================

"Substrate is structured-cognition NLP: dominant on LOW-DATA
regimes + adversarial-robust + morphologically rich languages +
explicit-slot-role tasks + structured/templated generation. LLMs
are statistical-text-similarity NLP: dominant on FULL-DATA
unstructured English. Different paradigms for different tasks;
hybrid LLM-NL-frontend + substrate-reasoning-backend captures both."

================================================================
SYNTHESIS -- RANK 5 LANGUAGE CAPABILITIES TO DRILL HARD
================================================================

Ranking criteria: substrate-product-distinctive (LLM cannot match)
+ empirically tractable (CPU, small data) + literature-supported.

#1 ADVERSARIAL-ROBUST NER (C1)
    Distinctiveness: HIGH (LLM brittleness well-documented; substrate
        denoising via cleanup intrinsic)
    Tractability: HIGH (reuse Tier-A 0.71 NER pipeline + perturb)
    Lit support: STRONG (Nature 2025; 2405.02764)
    Cell: 4-type NER, 0/5/10/20pct char/synonym noise, 5 seeds,
        substrate vs Qwen 0.5B/1.5B
    Predicted lift: substrate +0.15 at 20pct noise (deflated 0.50)
    Cost: ~2 GPU-hours

#2 MRL DEPENDENCY PARSING TURKISH + FINNISH (C2)
    Distinctiveness: HIGH (FHRR bind = native morpheme algebra; BPE
        blurs)
    Tractability: MED (UD treebanks small; tokenizer work needed)
    Lit support: STRONG (Tsarfaty CL 2013; SPMRL)
    Cell: UD Turkish-IMST + Finnish-TDT, substrate dep-parse
        pipeline with morpheme-binding extension vs mBERT/XLM-R
    Predicted UAS: substrate competitive within 3pts (deflated 0.45)
    Cost: ~4 hours

#3 FEW-SHOT TRANSFER CURVE (C3)
    Distinctiveness: HIGH (substrate aux-features memory rule already
        proven; need crossover quantification)
    Tractability: HIGH (just sweep training fraction)
    Lit support: MED-HIGH (Kleyko 2021; HyperEmbed)
    Cell: NER 4-type @ 1/5/10/50/100pct; measure substrate-LLM
        crossover point
    Predicted: substrate wins <=5pct training (deflated 0.55)
    Cost: ~3 hours

#4 ONTONOTES COREFERENCE via P^k MULTI-OCC BINDING (C4)
    Distinctiveness: HIGH (substrate has EXPLICIT slots; LLM has
        implicit attention)
    Tractability: MED (CoNLL-2012 eval scripts available)
    Lit support: STRONG (Lee EMNLP 2017; PP-401 substrate precedent)
    Cell: OntoNotes test, MUC/B^3/CEAF, substrate P^k binding vs
        e2e-coref + LLM zero-shot
    Predicted: substrate beats LLM zero-shot, within 5pts of
        supervised e2e-coref (deflated 0.40)
    Cost: ~6 hours

#5 STRUCTURED TEMPLATED GENERATION (C7 hybrid)
    Distinctiveness: HIGH (substrate-unified-compositional-engine
        memory)
    Tractability: MED (need bind-templates + lex atoms; small DSL)
    Lit support: STRONG (Smolensky-Lee 1601.02745; Soft TPR)
    Cell: Karel-style DSL, 50 templates x 200 fillers; exact-match
        vs Qwen 0.5B
    Predicted: substrate >0.50 exact match where LLM <0.30
        (deflated 0.45)
    Cost: ~5 hours

================================================================
TOP-2 IMMEDIATE RECOMMENDATION
================================================================

REC-A (Exp-Dev immediate): #1 ADVERSARIAL-ROBUST NER
    Rationale: reuses existing 0.71 Tier-A pipeline; just adds
    perturbation harness; high-confidence substrate-product story
    ("substrate doesn't pattern-match surface forms"); supports
    customer-facing positioning. Lowest-risk highest-visibility.

REC-B (Research authoring + Exp-Dev parallel): #3 FEW-SHOT TRANSFER
    CURVE
    Rationale: empirically quantifies the substrate-OPTIMAL low-data
    regime claim from aux-features-shrink memory. Gives a publishable
    crossover-point number. Cheap CPU work.

(Defer #2 MRL until #1+#3 ship; #4 coref needs PP-401 extension
work first; #5 generation rides substrate-unified-engine work in
flight.)

================================================================
PRE-REGISTERED NEGATIVES
================================================================

The following empirical outcomes would prove substrate has NO
language advantage beyond current Tier-A and force retreat:

N1. Adversarial NER: substrate degradation slope >= LLM 0.5B slope
    across 5/10/20pct noise (5 seeds). Would refute robustness claim.
N2. Few-shot crossover: LLM 0.5B beats substrate at every training
    fraction down to 1pct. Would refute low-data claim.
N3. MRL parsing: substrate UAS gap to XLM-R > 10 points on
    UD-Turkish + UD-Finnish. Would refute morpheme-algebra claim.
N4. Coref: substrate MUC < 0.40 (well below e2e-coref ~0.78
    historical). Would refute explicit-slot-binding claim.
N5. Templated gen: substrate exact-match <= Qwen 0.5B on DSL
    template task. Would refute unified-compositional-engine claim
    extended to code/template domain.

Per literature-is-not-oracle + brain-can-do-it rules: a negative
result triggers 2x DEEP re-drill, NOT immediate retreat. Three
substrate-only paths must FAIL on a capability before architectural-
boundary claim. Surface divergence from lit predictions as DISCOVERY
not bug.

================================================================
SAFETY / METHODOLOGY CHECK
================================================================

- ASCII only: YES
- No project-specific numerical values in web queries: YES (only
  generic terms used)
- No LLM-as-judge: YES (all metrics are objective end-task)
- Lit-scan calibration penalty applied: P deflated 0.15-0.25;
  novel-synthesis P capped 0.50
- Drill-defeatism guard: none of the 5 ranks accept LLM dominance
  as boundary; each has substrate-only path + 5-fail rule + brain
  analogue
- Generic-terms-only query-privacy rule honored

Word count: ~1080
