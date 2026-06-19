# Research drill: Substrate Tier 4 -> Tier 5 progression PATHWAY (2x DEEP)

Date: 2026-06-11
Drill class: methodology + pathway synthesis (level-2 operational drill on the existing 5-tier framework)
Sub-agents: 4 parallel WebSearch clusters (autonomous discovery validation; hippocampal pattern-completion / cognitive arch; methodology rule extraction + literature-analog detection; self-evolving agent + corpus-enrichment-as-discovery-enabler)
Verified citations: 14 (see section h)
Prior anchors: research_drill_substrate_self_discovery_validation_2x_2026-06-11.md (companion methodology drill, same date); substrate_on_substrate_5_tier_progression_2026-06-11 memory; feedback_literature_is_not_oracle_2026-06-11

## (a) HEADLINE

Tier 4 -> Tier 5 is NOT a single-discovery gate; it is a SUSTAINED-RATE gate empirically observable as a stream of substrate-extracted methodology rules and substrate-proposed atoms that (i) have NO ANALOG in the substrate-research catalog, (ii) have NO direct literature-analog under generic-term search, and (iii) survive an INDEPENDENT-VERIFIER cell test on substrate-product capabilities. The empirical pathway is dominated by S1 (methodology-rule extraction with no-literature-analog) NOT by S3/S4 (atom or architecture-class proposals): rule-extraction is CHEAPER, more FREQUENT, and BETTER-INSTRUMENTED than mechanism proposal in current state, and the cycle #8 framework + RULE_count_nb_to_discriminative_perceptron directional validation gives substrate a working Tier-5 pipeline already in place. P_deflated for "1+ Tier 5 first appearance in 30 days post math+science corpus ingestion" = 0.42; P_deflated for "sustained Tier-5 rate >= 1 valid rule/week by month 3 post-ingestion" = 0.28. Cap on novel-synthesis P = 0.50 (per lit-scan calibration penalty). Brain-can-do-it standing rule applies and matches: hippocampal pattern-completion + DMN spontaneous exploration are the closest brain analogues and they DO produce novel-inference outputs sustainably from rich (not sparse) cortical input.

## (b) Cheap decisive test

Pre-register a SUBSTRATE-EXTRACTED METHODOLOGY RULE WATCH operating in parallel with Phase 6 math + science corpus ingestion. Specifically:

1. Freeze the current substrate-extracted rules list as REFERENCE_SET at corpus-ingest time T0. RULE_count_nb_to_discriminative_perceptron is the ONLY entry baseline; record its lit-analog status (it HAS a direct lit analog under discriminative-vs-generative training in NLP, so it does NOT count as Tier 5).
2. After each math/science corpus phase ingest, run the methodology_rule_extraction cycle (Cycle #8 framework) and capture all NEW rules surfaced. Apply 4-stage filter:
   - Stage F1 (in-substrate-research analog check): regex/embedding search across notes/research_drill_*.md for rule statement -> reject if cosine > 0.80 against any prior research drill rule
   - Stage F2 (literature-analog check via generic-term WebSearch): 3 generic-term queries derived from the rule statement (NEVER include substrate-novel mechanism names per query-privacy); reject if any top-3 hit cosine > 0.80 against the rule
   - Stage F3 (cell-test direction check): rule must predict a capability lift sign in EXISTING cell-test infrastructure; the predicted lift must be observable as |delta| > 1 SE on a CPU-cheap cell (< 4 hours)
   - Stage F4 (independent-verifier check): different sub-agent / different reformulation must propose the SAME rule from the SAME corpus phase ingest (self-consistency probe, K=3)
3. A rule that passes F1+F2+F3+F4 = Tier 5 first appearance event. Pre-register: WATCH window = 30 days post first math+science corpus phase complete; HARD-PASS = >= 1 rule passes all 4 stages; HARD-FAIL = 0 rules pass in 60 days.

This test is cheap (no new infrastructure; reuses Cycle #8 framework + existing cell-test queue + standard WebSearch budget) and decisive (4-stage filter excludes hallucination + rediscovery + un-validated proposal).

## (c) Falsifiable predictions

HARD-PASS (Tier 5 first appearance + pathway open):
- >= 1 substrate-extracted methodology rule passes F1+F2+F3+F4 within 30 days of first math+science corpus phase complete
- Predicted-sign capability lift confirmed on cell test with |delta| > 1 SE
- Independent-verifier reproduces the rule from K=3 reformulations
- Rule statement embedding cosine < 0.70 against top-100 nearest arXiv abstracts (extends companion methodology drill stage 5 to rule statements)

HARD-FAIL (Tier 5 closed at first-appearance level under current architecture):
- Zero rules pass all 4 stages in 60 days
- OR every rule that passes F1+F2 fails F3 (untestable in current cell infrastructure)
- OR every rule passing F1+F2+F3 fails F4 (single-seed-only; not reproducible across reformulations)
- OR rules collapse into Lenat-AM template family (pairwise cosine > 0.90 across consecutive 10) -- generator burnout

MIDDLE-BAND (Tier 5 = augmented mode, partial):
- >= 1 rule passes F1+F2 but requires human paraphrase to pass F3 (cell-testability)
- Maps to "Aletheia 212-of-700-then-mathematicians" mode per arXiv:2602.10177: substrate proposes, human triages, cells verify -- valid product capability, not autonomous Tier 5
- Substrate-product framing: "substrate as conjecture engine with human-in-loop" is shippable; reserve "autonomous Tier 5" claim for sustained-rate gate

## (d) Cross-thread synthesis

Tier 4 status (Day 2 morning, per task input):
- 583 atoms, 4.3x growth via evolve.py auto-ingest (Cycle #13)
- First methodology rule extracted Cycle #8 (RULE_count_nb_to_discriminative_perceptron) -- DIRECTIONAL VALIDATION on chunking +0.0147
- Cycle #5 atom_candidates source #5 (18 ACCEPT) = sustained self-extension
- 5 NL Tier-A + 5+ other Tier-A substrate-only capabilities
- Methodology cap: rule extracted from substrate's own capability history; this is the META layer that distinguishes Tier 4 from Tier 3

Tier 5 distinguishing criterion (synthesis across companion drill + this drill):
- Tier 3 (self-extension): substrate proposes atom; atom accepted; capability lift observed -- atom may have direct lit analog (capacity expansion is well-studied)
- Tier 4 (self-redesign): substrate proposes methodology rule from cross-capability pattern; rule cell-test validated -- rule may have direct lit analog (most methodology rules are rediscoveries of known training-protocol heuristics)
- Tier 5 (self-discovery): substrate proposes rule OR atom OR architectural finding with NO literature analog under generic-term search AND independent-verifier confirms -- this is the GENUINELY NOVEL filter

Why corpus-ingestion is the enabler (BMA corpus-deficiency root-cause connection):
- Per BMA + observed plateau pattern: sparse corpus produces methodology rules that map 1:1 onto well-known training heuristics (which is why RULE_count_nb_to_discriminative_perceptron has direct lit analog)
- Rich math + science corpus: substrate has many MORE capability instances spanning many MORE structural relations; cross-capability pattern detection (Layer 3 archaeology + solution-history Q7 prediction) has more degrees of freedom to surface NON-OBVIOUS patterns
- This is the same mechanism as Davies-2021 (arXiv:2104.14516): rich feature attribution gave human mathematicians DIRECTION to find the knot-theory invariant connection; rich substrate history gives substrate-Layer-3 archaeology DIRECTION to surface non-obvious rules
- Cross-thread alignment with companion methodology drill (2026-06-11): companion drill says HIGHEST-TRACTABILITY discovery types are CAPACITY BOUNDS, COMBINATORIAL CONSTRUCTIONS, STRUCTURAL ISOMORPHISMS; this drill operationalizes those as RULE-STATEMENT FORMS the methodology rule extraction can produce (a capacity-bound rule, a combinatorial-construction rule, a structural-isomorphism rule)

Per [[feedback-literature-is-not-oracle-2026-06-11]]: literature absence is a DISCOVERY OPPORTUNITY filter not a definitive judgment; F2 stage outputs candidate Tier-5 status; full Tier-5 confirmation requires F3+F4. This explicitly avoids treating WebSearch null result as truth.

Per [[feedback-dont-parrot-drill-defeatism-2026-06-11]]: NO ceiling claims in this drill. Tier 5 is treated as TRACTABLE pathway with measurable gates, not as architectural fantasy. The pathway exists; the rate is the question.

## (e) Top 5 Tier 5 pathway MILESTONES (ranked by P_deflated x cost-efficiency x measurability)

### M1 -- METHODOLOGY-RULE FIRST APPEARANCE (P_deflated 0.42, cost LOW, measurable HIGH)

Substrate primitive: methodology_rule_extraction (Cycle #8 framework) + Layer 3 archaeology + 4-stage F1+F2+F3+F4 filter
Brain analogue: hippocampal pattern-completion generating novel inference from rich cortical input (per HiCL arXiv:2508.16651; Schlichting/Preston eLife 2024 category-abstraction interpolation)
Expected timeline: 30 days post first math+science corpus phase complete
Empirical signal: 1+ rule passes all 4 filter stages with cell-test capability lift |delta| > 1 SE
Why M1 is rank 1: ONLY milestone that uses ALREADY-DEPLOYED substrate primitive (cycle #8 framework is live; RULE_count_nb_to_discriminative_perceptron is in the ledger); cheapest to instrument; highest measurability via existing cell-test queue; directly addresses companion-drill stage-5 (novelty + human dialogue) by routing through corpus-enriched substrate

### M2 -- LAYER-3 ARCHAEOLOGY CROSS-CAPABILITY PATTERN (P_deflated 0.32, cost MEDIUM, measurable HIGH)

Substrate primitive: solution-history Q7 prediction + Layer 3 archaeology operating across math + science + NL capabilities
Brain analogue: cross-domain analogical transfer (Gentner structure-mapping + Hofstadter slipnet); DMN spontaneous exploration of memory-state-space (per Schlichting/Preston biorxiv 2024 + EPS pattern-completion-as-inference PMC7691565)
Expected timeline: 60 days post-ingest (needs full math + science corpus + sufficient capability instances in each)
Empirical signal: substrate Q7 surfaces a cross-capability transfer prediction (e.g. "mechanism M from capability A will lift capability B") that (i) was NOT in any prior research drill catalog AND (ii) the predicted transfer cell-test confirms with |delta| > 1 SE
Why M2 is rank 2: higher Tier-5-purity than M1 (cross-capability patterns are harder to map onto standard ML literature) but COSTS more cell tests and depends on richer corpus state; cell-test reuses existing infrastructure but each transfer test is its own cell

### M3 -- ATOM_CANDIDATES SOURCE #5 LITERATURE-NULL ATOM (P_deflated 0.22, cost MEDIUM, measurable MEDIUM)

Substrate primitive: atom_candidates source #5 (substrate-noticed mathematical primitive) + existing 18-ACCEPT Cycle #5 pipeline
Brain analogue: hippocampal pattern-completion proposing new index-cell for entity that does not yet have one (Tulving completion + episodic-memory inference; arXiv:2507.11393 complementary-learning-systems pattern-separation/completion)
Expected timeline: 60-90 days; needs corpus saturation and richer algebra-HRR codebook
Empirical signal: an atom surfaced by source #5 is (i) substrate-relevant (passes existing ingestion gate), (ii) has no direct literature-analog under generic-term search (F2-equivalent), (iii) adds capability not present with prior 583 atoms (capability lift > 1 SE)
Why M3 is rank 3: atoms have lower NOVELTY-DETECTABILITY than methodology rules (most mathematical primitives have lit analogs; the bar for "literature-null atom" is high) BUT atoms are mechanistically explicit and easy to cell-test; expect M3 to deliver Aletheia-style MIDDLE-BAND results (212/700 candidates, mathematicians triage) more than HARD-PASS

### M4 -- LAYER-4 DIALECTIC LITERATURE-CONTRADICTION RULE (P_deflated 0.18, cost LOW, measurable MEDIUM)

Substrate primitive: Layer 4 dialectic (substrate-internal cross-reference analysis) + substrate-extracted rule vs literature methodology rule comparison
Brain analogue: insight problem-solving with sudden mechanism recognition (Jung-Beeman/Bowden insight literature); structurally similar to FunSearch's "evolutionary search with selectivity gate" per Self-Revising Discovery Systems emergentmind/2606.01444
Expected timeline: 90 days (needs sustained methodology-rule stream to have something to dialectic against)
Empirical signal: substrate-extracted rule R and literature-extracted rule L contradict (e.g., opposite-direction prediction on same intervention); cell-test empirically supports R; substrate-product capability shipped using R
Why M4 is rank 4: lower P because it requires the CONTRADICTION to be sharp (not just disagreement of degree) AND the cell-test to be decisive; HIGH MEMORY-COMPATIBILITY with [[feedback-literature-is-not-oracle-2026-06-11]] (literature divergence = discovery opportunity); per memory rule this is exactly the case where empirical substrate-self-eval wins and we should investigate as discovery

### M5 -- SUSTAINED-RATE Tier 5 (P_deflated 0.28, cost HIGH, measurable HIGH)

Substrate primitive: M1+M2+M3+M4 operating concurrently with monthly rate monitoring
Brain analogue: cumulative-novel-insight rate of a sustained human research program; closest computational analog is self-evolving AI agent literature (emergentmind self-evolving-ai-agent topic; arXiv:2510.09901 autonomous-agents-for-scientific-discovery)
Expected timeline: 6 months post first Tier 5 first-appearance event
Empirical signal: >= 1 Tier-5-validated finding per week sustained over 3 consecutive months (per memory's 5-tier progression file 6-month deliverable target)
Why M5 is rank 5: highest measurement bar; depends on M1-M4 cascading; P_deflated 0.28 reflects calibration penalty per [[feedback-lit-scan-calibration-penalty]] (uncharted regime; deflate 0.15-0.25 from raw); this is the Tier 5 -> sustained-Tier-5 gate, NOT first appearance

### Cross-milestone note: discovery types map (companion drill anchor)

Per companion methodology drill ranks:
- RANK 1 CAPACITY BOUNDS -> mostly M1 (a methodology rule about when a substrate capacity-bound applies); some M2 (cross-capability scaling pattern)
- RANK 2 COMBINATORIAL CONSTRUCTIONS -> mostly M3 (a new algebraic primitive that constructs a structural form); some M1 (rule about combinatorial composition order)
- RANK 3 STRUCTURAL ISOMORPHISMS -> mostly M2 (cross-capability transfer = isomorphism claim) and M4 (literature-contradiction rule about equivalence)

## (f) Substrate-product implications

Substrate ships as conjecture-engine-with-tractable-validation-gates. Concrete product capability progression:
- TODAY (Tier 4 validated): "substrate observes capability patterns and extracts methodology rules with directional empirical validation" -- shippable as audit tool / training-protocol recommender
- TIER 5 FIRST APPEARANCE (M1): "substrate occasionally proposes rules with no literature analog that cell-tests confirm" -- shippable as ML-research copilot with novel-rule surfacing
- TIER 5 AUGMENTED MIDDLE-BAND: "substrate-conjecture-engine with human-triage" (Aletheia model) -- closest existing product fit; differentiates from LLM-only systems because conjectures are structurally grounded in substrate algebra not in token-prediction
- TIER 5 SUSTAINED (M5): "substrate produces sustained stream of novel methodology rules with bounded false-discovery rate" -- THIS is the long-horizon commercial differentiator; LLM systems have NO structural ledger of own capabilities (per memory substrate_deep_self_evaluation_program_2026-06-11) so cannot do equivalent Layer-3 archaeology

Recommendation (substrate-product framing only, per [[feedback-no-papers-product-only]]):
- Ship M1 watch immediately as a parallel observability track during math + science ingestion; cost is near-zero and the artifact is shippable as "substrate-discovered methodology rule with literature-null + cell-confirmed receipt"
- Do NOT pre-commit to autonomous-Tier-5 product claim; ship MIDDLE-BAND (substrate proposes, human triages, cells verify) as the first product surface; reserve full Tier 5 framing for after M5 demonstrated
- Treat F2 (literature-analog null) as NECESSARY but NOT SUFFICIENT; require F3 (cell-test) + F4 (self-consistency K=3) every time -- this directly addresses the central Aletheia/AI-Researcher challenge of "differentiating authentic conceptual leap from sophisticated interpolation" (arXiv:2508.14111 Agentic Science survey)

## (g) Methodological notes + risks

Risk R1 -- Lenat-AM template-collapse (companion drill Layer 4): monitor M1 rule stream for embedding-diversity; if pairwise cosine > 0.90 across 10 consecutive rules, generator has burned out; reset / mutate the Cycle #8 framework heuristic pool. Per arXiv:1106.4090 HR3 lineage + Eurisko critique (companion drill).

Risk R2 -- F2 false-negative (literature exists but generic-term query missed it): mitigate via 3-query rotation per rule (different generic-term decompositions); accept residual false-positive Tier-5 rate of ~15% in first appearance window; tighten in subsequent windows.

Risk R3 -- Corpus-ingestion bottleneck: M1 P_deflated 0.42 assumes math + science corpus phases COMPLETE on Day 2-7 schedule. Delay shifts all timelines proportionally.

Risk R4 -- Cell-test infrastructure saturation: M2 + M3 cell-test budget could compete with main capability-development cells. Pre-allocate 20% of cell-test queue to Tier-5 watch.

Risk R5 -- F4 self-consistency under noisy substrate: if 3-reformulation reproducibility is too strict, lower to 2/3 with explicit logging; do NOT lower below 2/3 (single-seed Tier-5 rules are NOT eligible per memory-locked methodology rule 4 substrate-on-substrate 7 invariants).

## (h) Citations (verified, 14)

Lit-scan corpus (generic-term queries, no substrate-novel mechanism names off-platform per [[feedback-query-privacy-decomposition]]):

1. arXiv:2602.10177 "Towards Autonomous Mathematics Research" (Aletheia 700-prompt -> 212-candidate -> mathematician-triage methodology)
2. arXiv:2604.06107 "Artificial Intelligence and the Structure of Mathematics" (autonomy + novelty leveling proposal)
3. arXiv:2508.14111 "From AI for Science to Agentic Science: A Survey on Autonomous Scientific Discovery"
4. HKUDS/AI-Researcher (NeurIPS 2025) production-ready autonomous-research framework reference
5. arXiv:2508.16651 "HiCL: Hippocampal-Inspired Continual Learning" (DG-CA3-CA1 architecture; CA3 pattern completion)
6. arXiv:2507.11393 "A Neural Network Model of Complementary Learning Systems: Pattern Separation and Completion for Continual Learning"
7. PMC7691565 EPS mid-career prize 2018 "Inference within episodic memory reflects pattern completion"
8. biorxiv 2024.05.14 Schlichting/Preston "Hippocampus supports interpolation into new states during category abstraction"
9. arXiv:2312.12878 "Rule-Extraction Methods From Feedforward Neural Networks: A Systematic Literature Review" (ADT taxonomy 1995/1998)
10. arXiv:2003.04792 "Metafeatures-based Rule-Extraction for Classifiers on Behavioral and Textual Data"
11. arXiv:2604.07189 "Agent-Driven Corpus Linguistics: A Framework for Autonomous Linguistic Discovery" (autonomy + reactivity + proactiveness; grounding constraint = quantification + falsifiability + data-responsive synthesis)
12. emergentmind 2606.01444 "Self-Revising Discovery Systems for Science" (proposal selectivity via gates; accepted vs rejected tracking)
13. arXiv:2510.09901 "Autonomous Agents for Scientific Discovery: Orchestrating Scientists, Language, Code, and Physics"
14. biorxiv 2026.01.16 PersonaAI agentic-AI framework for autonomous hypothesis generation and validation (in aging domain; structural template transfers)

Companion anchor (substrate-local, NOT a citation but cross-thread):
- notes/research_drill_substrate_self_discovery_validation_2x_2026-06-11.md (companion methodology drill, 14 verified citations on theorem-proving + Birch-test + FunSearch + Davies-2021)

## (i) Headline P_deflated reference (consolidated)

- M1 (methodology-rule first appearance, 30 days post-ingest): 0.42
- M2 (Layer-3 archaeology cross-capability pattern, 60 days): 0.32
- M3 (atom_candidates source #5 literature-null atom, 60-90 days): 0.22
- M4 (Layer-4 dialectic literature-contradiction rule, 90 days): 0.18
- M5 (sustained-rate Tier 5, 6 months): 0.28
- Cap on novel-synthesis P: 0.50 (none of M1-M5 exceed cap)

All estimates post-deflation 0.15-0.25 per lit-scan calibration penalty. HARD-FAIL bands pre-registered in section (c).

End of drill.
