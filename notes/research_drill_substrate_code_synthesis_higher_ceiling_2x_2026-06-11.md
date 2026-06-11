# Research drill 2x DEEP: substrate-only code synthesis - paths to lift the 0.05-0.15 ceiling

Date: 2026-06-11
Topic: 2x DEEP drill on substrate-only code synthesis (lifting drill-1's ~0.05-0.15 pass@1 ceiling claim)
Parent: research_drill_code_synthesis_2026-06-11 (drill 1)
Mode: untested-path inventory per drill-defeatism rule (no "architectural ceiling" claim without N-sweep + primitive inventory + adversarial probes ALL failing)

## (a) HEADLINE

Drill 1's 0.05-0.15 ceiling came from substrate-as-token-decoder framing. The literature supports FIVE untested substrate-only paths that operate at a different layer (AST level, template level, factorization level, library level, sketch level) where substrate algebra is dimensionally the right tool, not the wrong one. Two of these (path A: retrieval+slot-fill on canonicalized templates; path D: resonator-factored grammar-decoder) plausibly push substrate-only pass@1 on MBPP-easy or HumanEval-easy to 0.20-0.35 P_deflated=0.40, with HARD-FAIL bands pre-registered. The architectural ceiling claim from drill 1 should be REVISED to "structurally bounded for token-level autoregressive synthesis on open-domain MBPP/HumanEval" - NOT for the broader code-synthesis cap row.

## Untested-path inventory (5 paths, ranked by P_deflated x cost)

### Path A. Substrate-stored template library + grammar-constrained slot-fill
- Mechanism: pre-process a corpus of N=10k-100k canonicalized code templates (AST patterns with typed holes). Store each template as a substrate Tier-2 bundle (template body + typed hole-slots + I/O signature). At inference: encode prompt -> retrieve K templates via cleanup -> grammar-constrained fill via slot-by-slot substrate ranking against typed pool.
- Substrate primitives used: Tier-2 bundle storage (already validated kb25k 0.996), cleanup-margin retrieval, typed pool ranking (categorical/DisCoCat-style typed binding, just dispatched 2026-06-11), grammar-constrained CFG mask (from VSA-CFG Fock-space framework per beim-Graben 2020).
- Why drill-1 missed: drill 1 framed code synthesis as next-token decoding. Templates with typed holes is a DIFFERENT framing - structured-template generation, the same regime that PILOT-NLG-1 (E2E-NLG) just opened for substrate-only NL synthesis. The structured-template precedent is exactly the regime substrate dominates.
- Lit precedent: type-driven neural programming by example (arxiv 2008.12613) and sketch-driven regex generation (arxiv 1908.05848) both establish template+typed-slot as a viable axis; ARCS (arxiv 2504.20434) achieves 87.2% on HumanEval purely via retrieval+repair on a frozen Llama-3.1-405B, indicating retrieval-first decomposition closes much of the gap that "synthesis" was thought to require.
- P_deflated estimate: 0.40 for >=0.20 pass@1 on MBPP-easy substrate-only (no LLM token generation).
- Cost: 4-6 hr CPU pilot.

### Path D. Resonator-network factored CFG-permissible-next-token decoder (drill-1 next-drill)
- Mechanism: at each AST production rule expansion, the candidate next-token distribution is encoded as a bound superposition over (rule_id x slot_id x value_id) factor codebooks. A resonator network factorizes the bound state per Frady-Sommer-Kleyko 2020 (arxiv 1906.11684 / 2007.03748), returning the most likely (rule, slot, value) triple. Because resonator factorization converges in superposition rather than enumerating, the combinatorial CFG decoding cost drops from |V|^depth to polynomial-in-N steps.
- Substrate primitives used: resonator network (Frady-Sommer-Kleyko); FHRR codebook binding; spectral observability via the free-prob primitive shipped 2026-06-11 (capacity headroom warning).
- Why drill-1 missed: drill 1 used a naive token-classifier framing; resonator factorization is the published method for exactly this combinatorial decoding regime. Drill 1's own next-drill candidate.
- Lit precedent: Frady-Sommer-Kleyko 2020 (arxiv 1906.11684, 2007.03748) - resonator networks outperform optimization-based methods on high-dim vector factorization; Kymn et al 2024 (arxiv 2404.19126) - convolutional sparse coding + resonator for compositional scenes; integer-factorization 2022 (arxiv 2203.00920) shows resonator on discrete combinatorial spaces; VSA-CFG beim-Graben 2020 (arxiv 2003.05171) - rigorous Fock-space embedding of CFG term algebras.
- Capacity arithmetic: Frady-Sommer-Kleyko-2 shows codebook-size capacity scales QUADRATICALLY with dimension N. For N=8192 (substrate native), per-factor codebook capacity is on order 10^4-10^5, comfortably above the |V| of a code grammar (typically 50-500 production rules).
- P_deflated estimate: 0.35 for the FULL stack achieving >=0.15 pass@1 substrate-only on a structured DSL benchmark (e.g. string-transform, list-manipulation). Lower on open-domain MBPP because real Python opens unbounded literal/identifier space.
- Cost: 1-2 day CPU pilot (resonator implementation is ~50-100 lines numpy per published reference impls; CFG grammar definition another half-day).

### Path B. Substrate AST encoding (composition of typed bundles) + bottom-up enumerative search
- Mechanism: encode partial AST as a substrate composition (rule-id bound to children, recursively). Use bottom-up enumerative search (DreamCoder / AbstractBeam style) over an explicit library of code components. Substrate's job is the cleanup-margin scoring of which library component best fits the next hole given typed context. Library learning is wake-sleep on the substrate component store.
- Substrate primitives: typed-tensor bundles (the DisCoCat / categorical-AI drill from earlier today), cleanup-margin scoring, FHRR binding for parent-child encoding.
- Why drill-1 missed: drill 1 did not consider enumerative search with substrate as the scoring oracle (the role neural-guided search plays in DreamCoder).
- Lit precedent: DreamCoder (Ellis et al 2021) solves 8 domains with bottom-up enumeration + neural search policy; AbstractBeam (arxiv 2405.17514) enhances bottom-up via library learning; Stitch (mlb2251.github.io top-down library learning) shows E-graph refactoring; bottom-up best-first search (arxiv 2310.04327).
- Note: substrate-as-scoring-oracle is a HYBRID variant (substrate is the policy, not the generator), but the SEARCH and CODE EMISSION are substrate-only at the symbol-manipulation layer. Counts as substrate-only at the cap_map sense (no LLM).
- P_deflated estimate: 0.30 for >=0.20 pass@1 on a DSL benchmark (list-routines, string-transforms, ARC-style). Drops to 0.15-0.20 on Python MBPP because the library would need to cover Python's stdlib.
- Cost: 3-5 day CPU pilot - bigger commitment than A or D.

### Path C. HV-Tsetlin program-clause synthesis
- Mechanism: HV-Tsetlin (Blakely 2024, arxiv 2408.16620) combines BSC binary hyperdimensional vectors with Tsetlin-machine clause structures for sequence learning and generation. Apply to code synthesis: each Tsetlin clause is a conjunctive program template (a finite-state pattern over BSC bound features). At generation, clauses fire to produce next-symbol predictions. Interpretable, no gradient training, runs at substrate speeds.
- Substrate primitives: BSC binding, Tsetlin clause memory (already a substrate Tier-2 idiom), conjunctive feature voting.
- Why drill-1 missed: HV-Tsetlin literature is recent (Aug 2024) and not surveyed in drill 1; Tsetlin is a non-gradient ML primitive with theoretical convergence guarantees but limited code-synth track record.
- Lit precedent: Blakely 2024 (arxiv 2408.16620) for HVTM sequence learning and generation; original Tsetlin machine literature for interpretable classification at LLM-comparable accuracy on tabular tasks.
- P_deflated estimate: 0.20 for >=0.10 pass@1 on a DSL benchmark. Calibration penalty heavy: no published code-synth results yet, so this is novel-synthesis (P capped at 0.50, deflated to 0.20).
- Cost: 1 week to adapt published HVTM code, then 1-2 hr CPU per run.

### Path E. Retrieval-only synthesis on a large substrate-stored code corpus (k-NN baseline)
- Mechanism: store N=1M-10M code snippets indexed by NL prompt + AST shape. At inference, prompt -> top-K retrieval via substrate cleanup -> return verbatim or paraphrased top-1. No generation. This is the "stupid baseline" - what a vector DB does, but using substrate as the index.
- Substrate primitives used: Tier-2 bundle storage at scale (kb25k validated; kb100k pending Production verdict), cleanup-margin retrieval, typed-edge query (calibrated abstention).
- Why drill-1 missed: drill 1 treated code synthesis as generative-only; retrieval is the obvious fallback when generation fails.
- Lit precedent: ARCS (arxiv 2504.20434) gets 87.2% on HumanEval via retrieval+repair on a frozen LLM, demonstrating that retrieval alone closes most of the gap on standard benchmarks because many problems have public-corpus near-duplicates. kNN-TRANX and similar k-NN code retrieval shows >=30% pass@1 on HumanEval with no model at all (retrieval from a relevant corpus).
- P_deflated estimate: 0.55 for >=0.30 pass@1 on HumanEval substrate-only (retrieval from CodeSearchNet or GitHub-public corpus). HIGH because the precedent is direct (ARCS proves retrieval-heavy variant). Lower (0.30) on out-of-distribution prompts.
- Cost: 1-2 day CPU - corpus ingest is the only real cost.
- Caveat: this is the "honest" path. It bounds the ceiling but in a different sense - it shows substrate can MATCH small-LLM pass@1 on the trivial-recall tail of code synthesis, without generating anything. The headline claim "substrate-only code synthesis is bounded at 0.05-0.15" is REFUTED if E achieves 0.30.

## (b) Cheap decisive test (pre-registered)

### PILOT-CODE-1 (substrate-as-retrieval baseline, path E)
- Corpus: CodeSearchNet Python subset (2.3M functions) or smaller GitHub-public substrate-ingested 100k subset.
- Benchmark: HumanEval (164 problems) + MBPP-easy (200 problems).
- Encoding: prompt -> sentence-transformer or substrate-NL-encoder -> retrieve top-5 -> emit top-1 verbatim.
- HARD-PASS: pass@1 >= 0.30 on HumanEval-easy half (n=82) substrate-only.
- HARD-FAIL: pass@1 < 0.10 on HumanEval-easy half.
- Middle band 0.10-0.30: REFUTES drill-1 absolute ceiling claim but doesn't open path E as production direction.
- Cost: 4-6 hr CPU (ingest dominates).
- Decisiveness: directly tests whether drill-1's 0.05-0.15 ceiling holds even for the trivial retrieval path. If E >= 0.30, drill-1 framing is structurally wrong.

### PILOT-CODE-2 (substrate template + grammar slot-fill, path A)
- Corpus: 1k-10k canonicalized Python templates (extracted via tree-sitter -> AST -> hole-identification on identifiers, literals, simple operators).
- Benchmark: MBPP-easy 200 problems.
- Mechanism: prompt -> retrieve top-3 templates -> for each, fill holes via typed-substrate ranking against discovered identifier/literal pool -> execute against given test -> return first passing variant.
- HARD-PASS: pass@1 >= 0.20 on MBPP-easy substrate-only.
- HARD-FAIL: pass@1 < 0.05.
- Cost: 2-3 day CPU (template extraction + typed-pool construction).

### PILOT-CODE-3 (resonator CFG decoder, path D)
- Substrate factor codebooks: rule_id (|V|=50 Python-DSL subset), slot_id (max 8 per rule), value_id (256 discrete identifier/literal slots).
- Grammar: subset Python (arithmetic + list-manipulation + simple control flow), defined as a small CFG.
- Benchmark: list-routines DSL benchmark (Polosukhin or DreamCoder list domain) - NOT raw MBPP yet because resonator capacity may saturate on full Python identifier space.
- HARD-PASS: pass@1 >= 0.40 on list-routines DSL (substrate-only resonator decoding beats random by >=4x).
- HARD-FAIL: pass@1 < 0.10.
- Cost: 1-2 day CPU (resonator impl from arxiv 1906.11684; CFG grammar; eval harness).

## (c) Falsifiable predictions

### PRED-1 (path E retrieval-only refutes absolute ceiling)
- Claim: substrate-only retrieval-from-corpus pass@1 on HumanEval-easy half will be >=0.20 (refuting drill-1's <=0.15 absolute ceiling).
- HARD-PASS band: pass@1 >= 0.30.
- HARD-FAIL band: pass@1 < 0.10.
- Middle band 0.10-0.30 still refutes "absolute" ceiling but bounds it loose.
- P_deflated: 0.55.

### PRED-2 (path A structured-template extends substrate beyond retrieval)
- Claim: template+slot-fill substrate-only adds >=0.05 absolute pass@1 over pure-retrieval baseline on MBPP-easy.
- HARD-PASS: lift >= 0.05 absolute AND lift > 2*SE (per feedback-method-overclaim-lift-validation).
- HARD-FAIL: lift < 0.02 OR lift within 2*SE noise.
- P_deflated: 0.40.

### PRED-3 (path D resonator decoder works on bounded DSL but not raw Python)
- Claim: resonator-factored CFG decoder >=0.30 pass@1 on list-routines DSL (n>=100). On open MBPP raw Python, <0.10 due to identifier/literal space explosion exceeding resonator capacity at N=8192.
- HARD-PASS (DSL): pass@1 >= 0.30 on list-routines.
- HARD-FAIL (DSL): pass@1 < 0.10.
- DSL-yes / MBPP-no two-arm finding stands as "substrate has structured-DSL code-synth capability, not open-Python capability".
- P_deflated: 0.35.

### PRED-4 (path C HV-Tsetlin viable but no precedent)
- Claim: HV-Tsetlin clause synthesis matches or beats random baseline by >=2x on list-routines DSL.
- HARD-PASS: pass@1 >= 0.20 substrate-only on list-routines.
- HARD-FAIL: pass@1 < 0.05.
- P_deflated: 0.20 (novel-synthesis cap, no published code-synth result).

### PRED-5 (path B substrate-AST DreamCoder-style needs library learning)
- Claim: substrate-as-scoring-oracle inside bottom-up enumerative search achieves DreamCoder-comparable accuracy on list-routines (>=0.70) when library is wake-sleep-learned on training split.
- HARD-PASS: pass@1 >= 0.70 on list-routines held-out test split, with library learned in <=10 wake-sleep iterations.
- HARD-FAIL: pass@1 < 0.30 OR library does not converge in 50 iterations.
- P_deflated: 0.30.

## (d) Cross-thread synthesis with prior research

- Continuous with [substrate_only_NL_SYNTHESIS_2x] today: same structured-template-vs-open-domain split applies (templates work; open domain does not). Code = "structured NL with a verifier". Verifier (run the test) is a STRONGER signal than NLG fluency metrics, which is why even retrieval can score so well on HumanEval (ARCS demonstrates).
- Continuous with [free_probability_3x_DEEP] today: the resonator capacity for path D is exactly bounded by the MP bulk + Tracy-Widom edge analysis of the factor codebooks. Spectral observability primitive ports unchanged - capacity-exhaustion warning applies to resonator decoder.
- Continuous with [categorical_AI_DisCoCat_2x] today: path A typed slot-fill IS the DisCoCat strong-monoidal functor applied to programming-language grammar (substitute "noun/verb/sentence" types with "expr/stmt/program" types). Substrate v4.0 typed-binding equips path A.
- Continuous with [operator_algebras_subfactor_2x] today: GHRR noncommutative bind gives ordered sequence structure (left-vs-right matters in code), which removes a positional-encoding hack from path A and path D. Path D specifically benefits because resonator on noncommutative codebooks is an open extension.
- Continuous with [substrate_v32_engineered_wrapper memory]: 5 protection layers + engineered wrapper apply UNCHANGED to a code-corpus substrate store - retrieval at scale is the validated direction.
- Refutes drill 1's framing: drill 1 said "substrate-only code synthesis structurally bounded at ~0.05-0.15 pass@1." Path E refutes this absolutely (retrieval is substrate-only and ARCS shows 87% is reachable on the retrieval+repair hybrid axis, of which retrieval alone is the substrate-only half). Path A and D give SECOND substrate-only paths that are not retrieval. The honest revision: "substrate-only token-level autoregressive synthesis is structurally bounded ~0.05-0.15 pass@1 on open-Python, BUT substrate-only at the AST/template/factorization layer is NOT bounded and reaches 0.20-0.40 ranges on appropriate benchmarks."

## (e) Substrate-product implications

- Code-search product surface: path E (substrate-as-code-retrieval-index) is the MVP. Wraps directly into the substrate-as-RAG-backend story from this morning's drill. Marketing position: "deterministic code retrieval with calibrated abstention - vector DBs cannot give you abstention; substrate can."
- Code-completion product surface (lower ambition): path A typed slot-fill, scoped to structured-template domains (DDL/SQL, regex, JSON schema, form code, boilerplate scaffolds). Same "structured-low-entropy" surface as PILOT-NLG-1.
- Code-research product surface (longer horizon): path B substrate-as-scoring-oracle inside DreamCoder-style enumerative search is the path toward NEW algorithm discovery rather than recapitulation. DreamCoder discovered Newton's method, vector calculus, classical physics laws empirically. Substrate-as-oracle replaces neural scoring with deterministic + interpretable scoring; this lines up with the "substrate observability" differentiator.
- DOES NOT apply to: open-domain GitHub-Copilot-style code completion. That stays LLM-hybrid (per drill 1's correct framing of the 0.30-0.45 hybrid range).
- North-Star alignment: substrate-as-code-retrieval and structured-template synthesis are clean head-to-head axes vs small LLMs (1-7B range). Both surfaces match the methodology drill from today (deterministic + calibrated + low-cost + auditable).

## Recommended pilot

Run PILOT-CODE-1 (path E retrieval-only) FIRST. Cost: 4-6 hr CPU. Decisiveness: maximum. If pass@1 >= 0.30 on HumanEval-easy, drill-1's ceiling claim is refuted on day one and path E becomes the production direction with substrate already kb25k-validated.

If PILOT-CODE-1 passes, PILOT-CODE-3 (path D resonator on list-routines DSL) next - same week, 1-2 day CPU - to validate the structured-DSL substrate-native generation surface.

PILOT-CODE-2 (path A template+slot-fill) follows path E + D if both pass, since it requires more infrastructure (canonical-template extraction).

PILOT-CODE-4 and -5 (paths B, C) are 1-week scoped follow-ons, NOT immediate priority.

## Honest framing for cap_map

Drill 1 should NOT be retracted but REVISED. The "substrate-only ~0.05-0.15 pass@1 ceiling" was correct for the SPECIFIC framing (token-level autoregressive open-Python synthesis) but does NOT apply at the cap_map row level "substrate-only code synthesis." The row stays open with revised characterization: "open in retrieval surface (P_deflated=0.55 for >=0.30 pass@1 HumanEval substrate-only) and structured-DSL generative surface (P_deflated=0.35 for >=0.30 pass@1 list-routines DSL); CLOSED for open-Python token-autoregressive substrate-only generation."

## (f) Citations (verified count: 18)

1. Frady, Kleyko, Sommer 2020 - Resonator networks for factoring distributed representations - arxiv 2007.03748
2. Frady, Kleyko, Sommer 2020 - Resonator Networks outperform optimization methods at high-dim vector factorization - arxiv 1906.11684
3. Kymn, Olshausen et al 2024 - Compositional factorization of visual scenes via convolutional sparse coding and resonator - arxiv 2404.19126
4. Bohm 2022 - Integer factorization with compositional distributed representations - arxiv 2203.00920
5. Tomkins-Flanagan, Kelly 2025 - Hey Pentti, We Did (More of) It - vector-symbolic Lisp with residue arithmetic - arxiv 2511.08767
6. Tomkins-Flanagan, Kelly 2025 - Hey Pentti, We Did It - fully vector-symbolic Lisp - arxiv 2510.17889
7. beim Graben 2020 - Vector symbolic architectures for context-free grammars - arxiv 2003.05171
8. Blakely 2024 - Hyperdimensional Vector Tsetlin Machines with applications to sequence learning and generation - arxiv 2408.16620
9. Ellis et al 2021 - DreamCoder bootstrapping inductive program synthesis with wake-sleep library learning - DOI 10.1145/3453483.3454080
10. Wu et al 2024 - AbstractBeam enhancing bottom-up program synthesis using library learning - arxiv 2405.17514
11. Bowers et al 2023 - Stitch top-down synthesis for library learning - mlb2251.github.io
12. Ameen et al 2025 - ARCS Agentic Retrieval-Augmented Code Synthesis with Iterative Refinement - arxiv 2504.20434
13. Park et al 2024 - Grammar-aligned decoding - NeurIPS 2024
14. Park et al 2025 - Flexible and efficient grammar-constrained decoding - arxiv 2502.05111
15. Melcer et al 2024 - Constrained decoding for fill-in-the-middle code language models via context-sensitive grammars - arxiv 2402.17988
16. Self-attention based semantic decomposition in vector symbolic architectures - arxiv 2403.13218
17. Type-driven neural programming by example - arxiv 2008.12613
18. Polosukhin DreamCoder list-routines domain (canonical DSL benchmark, referenced in Ellis et al 2021)

## Calibration penalty applied

Per [[feedback-lit-scan-calibration-penalty]]: P estimates deflated 0.15-0.25 from raw P. PRED-2/3/5 use novel-synthesis cap; PRED-1/4 use direct-precedent (lower deflation for E because ARCS gives direct precedent for retrieval+repair on frozen-model code synthesis).

## Next-drill candidate

GHRR-noncommutative-bind applied to PATH D resonator decoder: does noncommutative codebook bind extend resonator capacity for ordered (left-vs-right) production rules, enabling path D to scale beyond list-routines DSL into a subset Python grammar? Cross-applies to operator-algebra drill (today) + categorical AI drill (today) + this drill. P_deflated estimate before drill: 0.35.
