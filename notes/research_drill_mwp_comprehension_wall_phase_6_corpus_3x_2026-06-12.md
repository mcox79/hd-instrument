# Research Drill 3x DEEP: ASDiv MWP Comprehension Wall - Phase 6 Corpus Structural Gaps

Date: 2026-06-12
Target: ASDiv 1-op (1166 problems), substrate plateau 0.385-0.39 across 6 mechanism classes
Question: What CORPUS-STRUCTURAL properties is the 92-atom MWP corpus missing?
Drill type: 3x DEEP, convergently closed negative finding, production-blocking
Safety: ASCII-only, generic queries only, no LLM-as-judge

---

## Pre-Registered Framing

Six independent mechanisms (discriminative perceptron, world-model schema, BMA ensemble, hippocampal k-NN, heuristic entity-binding, trained SRL) collapse to 0.385-0.39 with correlated errors. Op-mapping is solved; the bottleneck is OPERAND SELECTION / SCENARIO SEMANTICS. On distractor subsets (>2 numbers) heuristic entity-binding drops to 0.135, exactly where linguistic structure should help. This is a CORPUS DEFICIENCY signature (per substrate_mwp_comprehension_blind_spot_corpus_limited_2026-06-12), not an architectural ceiling. Brain-can-do-it (USER-locked) forbids accepting comprehension as a substrate boundary.

---

## Hypothesis H1 - Quantity-Verb Dependency Atoms (SYNTACTIC)

1. Structural property: SYNTACTIC. Each quantity in the surface text has a DEPENDENT VERB found by walking up the dependency tree from the numeric mention to the first verb. The (quantity, verb, subject, object) tuple encodes the local transfer semantics.
2. Literature: Roy and Roth (2015, arXiv:1608.01413) build a "quantity schema" per quantity using the dependent verb plus subject/object; this drives correct op selection on AddSub/SingleOp benchmarks. Hosseini et al. (MAWPS construction line) use verb categorization (gain/lose/transfer) to predict operator. Liang et al. arXiv:1808.03028 use frame identification of the dependent verb to disambiguate addition vs subtraction in MWP.
3. Brain grounding: Ventral-stream verb-argument structure (Trueswell, Tanenhaus) - human readers resolve quantity reference by binding verb to argument slot in the same sentence. PFC top-down attention modulates which dependency edges are foregrounded.
4. Substrate ingestion: For each ASDiv-style problem, emit atoms QVERB_<verb_lemma>_<polarity> with relations DEPENDS_ON (number_mention) and ARG_OF (subject_entity), and LEX_T atoms for the ~40 high-frequency arithmetic verbs (give/take/lose/buy/sell/eat/save/share/break/leave). Add per-verb polarity tag (+1 gain, -1 loss, 0 stative). Population ~400 atoms + ~800 edges from 92 existing problems plus a few hundred parsed ASDiv-train.
5. Discriminating signal: Distractor subset suffers because non-target numbers have NULL or stative dependent verbs; gain/loss verbs anchor the target. Estimated lift on distractor cells +0.10 to +0.15; on full ASDiv +0.04 to +0.07 (target plateau 0.39 -> 0.43-0.46).
6. Cost: CHEAP. spaCy dependency parse on existing 1166 problems, deterministic extraction, no annotation. Hours-scale CPU.
7. P_deflated: 0.62 (lit confidence 0.85, substrate-fit 0.90 via existing LEX_T pattern, ASDiv-applicability 0.80; deflated 0.20 per literature-not-oracle).

## Hypothesis H2 - Container/Transfer World-Model Schema (SEMANTIC + PRAGMATIC)

1. Structural property: SEMANTIC/PRAGMATIC. Each agent in a problem owns a TYPED CONTAINER (cookies, marbles, dollars). Transfer events update two containers symmetrically: "Alice gives 3 apples to Bob" decrements Alice.apples, increments Bob.apples.
2. Literature: arXiv:2306.04347 "World Models for Math Story Problems" - explicit container abstraction improves MWP solvers on transfer-heavy subsets. arXiv:1712.09391 "Mapping to Declarative Knowledge" formalizes container-update schemas. arXiv:2211.12164 OLGA ontology of transfer-type AWPs.
3. Brain grounding: Hippocampal episodic schema (Schlichting and Preston) - humans track entity state across narrative time. Bilateral PFC-hippocampal top-down (Menon group, PMC3462165) actively suppresses non-target entity states during arithmetic problem solving.
4. Substrate ingestion: CONTAINER atoms parametrized by (owner_entity, object_type, count_var), TRANSFER_EVENT atoms binding (source_container, target_container, magnitude_quantity, verb). HRR-bind owner * object * count per state snapshot. Use solution_history reverse-index pattern from Gap 1. ~200 schema atoms + ~600 event-relation edges.
5. Discriminating signal: H2 directly addresses E4 schema-simulation plateau 0.34 by giving substrate executable state-update primitives instead of static schemas. Estimated lift on multi-entity / transfer subset +0.08 to +0.14; on full ASDiv +0.05 to +0.09 (-> 0.44-0.48).
6. Cost: MEDIUM. Schema authoring is semi-manual; ~150 transfer-type ASDiv problems need light annotation (1-2 days). Parser logic ~80 lines.
7. P_deflated: 0.58 (lit confidence 0.80, substrate-fit 0.75 via HRR-binding, ASDiv-applicability 0.85; deflated 0.20).

## Hypothesis H3 - Distractor / Irrelevant-Quantity Discriminator (PRAGMATIC)

1. Structural property: PRAGMATIC. Each numeric mention carries a RELEVANCE feature: does this quantity participate in the answer? Distinct from operand-selection, this is a binary upstream filter.
2. Literature: arXiv:2403.12744 "Identify and Ignore Irrelevant Conditions" shows distractor-aware filtering breaks LLM CoT collapse. arXiv:2601.06853 DAGGER distractor-aware graph generation. Roy-Roth binary SVM "is this quantity in the equation". Munoz-Sanchez et al. ScienceDirect 2018 cognitive evidence numerical irrelevant info more harmful than literal.
3. Brain grounding: PFC top-down attention (dlPFC) explicitly suppresses task-irrelevant numerical features in arithmetic (Menon and Chang neuroimaging). Hippocampal episodic gating filters irrelevant context.
4. Substrate ingestion: RELEVANCE_TAG atom per quantity mention with features (in_question_sentence, shares_entity_with_question, dependent_verb_polarity, numeric_value_distinctness). Train discriminative perceptron (already substrate Tier-A universal lever, +0.728 to +0.114 across 11/12 caps) on (relevance=1/0). Reuses substrate's empirically validated mechanism.
5. Discriminating signal: H3 directly attacks the distractor cliff (0.135 on >2-number subset). Expected lift on distractor subset +0.15 to +0.25; on full ASDiv +0.03 to +0.06 (since distractor subset is fraction of total). Combined with H1 effect compounds.
6. Cost: CHEAP. ~50 ASDiv-train problems with relevance annotation (or auto-label by checking quantity membership in gold equation). Perceptron training ~minutes.
7. P_deflated: 0.65 (lit confidence 0.88, substrate-fit 0.95 - exact match to discriminative perceptron universal lever, ASDiv-applicability 0.78; deflated 0.20). HIGHEST P.

## Hypothesis H4 - Bridging Anaphora and Entity Coreference (LEXICAL + SEMANTIC)

1. Structural property: LEXICAL/SEMANTIC. "John has 5 marbles. He gives 2 to Mary." requires resolving He->John AND "2" -> 2 marbles (bridging). Substrate needs explicit coref + bridging atoms.
2. Literature: Hou et al. MIT Press 2018 unrestricted bridging resolution. arXiv:1803.04790 enhanced word reps for bridging. arXiv:2512.07134 GUMBridge corpus. Sundaram et al. (cognitive psych) - children solving MWP fail more on pronoun-heavy variants.
3. Brain grounding: Hippocampus binds entity tokens across sentences (episodic binding). Ventral stream resolves anaphor through discourse memory.
4. Substrate ingestion: COREF_LINK relation type connecting pronouns/definites to antecedent entity atoms. BRIDGING_LINK connecting quantity mention to (entity, object_type) via possessive or partitive context. ~300 link edges per pass over 1166 problems.
5. Discriminating signal: ASDiv lexical diversity (CLD 0.49 vs MAWPS 0.42) means more pronominal and definite-NP variants. Estimated lift +0.03 to +0.06 on full ASDiv. Lower than H1-H3 because effect is concentrated in pronoun-heavy minority.
6. Cost: MEDIUM. Need coref resolver (neuralcoref or huggingface coref). Substrate stores resolved links; resolver runs offline.
7. P_deflated: 0.42 (lit confidence 0.70, substrate-fit 0.65, ASDiv-applicability 0.55; deflated 0.20).

## Hypothesis H5 - Cross-Domain Scenario Priors / Commonsense (CROSS-DOMAIN)

1. Structural property: CROSS-DOMAIN. "If a pizza has 8 slices and 3 people share equally" requires implicit prior: division, equal-share, integer-result. Scenario priors live outside the 92-atom MWP corpus, in commonsense.
2. Literature: arXiv:2301.09723 "MWP, common sense, and AI". Patel et al. NAACL 2021 (aclanthology 2021.naacl-main.168) show SVAMP plateau is partly commonsense-deficit. arXiv:2210.07128 code-LM as commonsense few-shot learners.
3. Brain grounding: Semantic memory (ATL) holds object/scenario priors; PFC retrieves and binds to current MWP.
4. Substrate ingestion: SCENARIO_PRIOR atoms (sharing -> division, group_of -> multiplication, remaining -> subtraction). LEX_T atoms for ~30 scenario triggers (share, distribute, altogether, left, gave_away).
5. Discriminating signal: Overlaps heavily with H1 (verb-as-op-cue) and H2 (transfer schema). Marginal lift beyond H1+H2 estimated +0.02 to +0.04. Low independent contribution.
6. Cost: MEDIUM-HEAVY if pursued via large commonsense ingest; CHEAP if scoped to 30 scenario triggers.
7. P_deflated: 0.38 (lit confidence 0.65, substrate-fit 0.60 - risk of overlap with H1, ASDiv-applicability 0.65; deflated 0.20).

---

## Ranking by P_deflated x cost-efficiency

| H  | P_def | Cost   | Efficiency (P/cost) | Rank |
|----|-------|--------|---------------------|------|
| H3 | 0.65  | cheap  | 0.65                | 1    |
| H1 | 0.62  | cheap  | 0.62                | 2    |
| H2 | 0.58  | medium | 0.29                | 3    |
| H4 | 0.42  | medium | 0.21                | 4    |
| H5 | 0.38  | medium | 0.19                | 5    |

Top-2 recommendation: H3 (distractor-relevance discriminator) + H1 (quantity-verb dependency atoms). Both CHEAP, both leverage substrate's empirically validated discriminative perceptron universal lever, both attack the operand-selection bottleneck and the distractor cliff directly.

## Compound Estimate

H1 + H3 jointly: expected full-ASDiv lift +0.07 to +0.13 (plateau 0.39 -> 0.46-0.52). Distractor subset lift +0.18 to +0.30 (0.135 -> 0.31-0.44). H2 as Phase-6.2 follow-up if H1+H3 partial; H4/H5 deferred.

## Pre-Registered Negative Outcomes (2x discipline)

NEG-1: If H3 trained relevance discriminator gets >0.85 P(R) on held-out but full-ASDiv accuracy does not move >+0.03, the bottleneck is NOT distractor filtering but something downstream (operand-to-equation binding). Pivot to H2.
NEG-2: If H1 verb-dependency atoms populate but discriminative perceptron with verb features cannot beat 0.40, then dependency parse is too noisy on MWP register; pivot to LEX_T-only verb polarity features.
NEG-3: If H1+H3 jointly lift <+0.04, the architectural ceiling claim revives - but only after these substrate-only paths fail empirically (per drill-defeatism rule).

## Cross-Drill Convergence

H1 + H3 + H2 converge on the same finding from 3 angles: surface dependency parse (H1), pragmatic relevance filter (H3), and executable world-model (H2). All three are corpus-structural augmentations to the 92-atom base, not new mechanisms. Consistent with substrate_mwp_comprehension_blind_spot_corpus_limited memory and brain-can-do-it locked rule.

## Recommendation for Routing

- Research authoring: H3 (distractor-relevance) + H1 (quantity-verb dependency) corpus design notes. Define atom schemas, relation types, parser logic.
- Exp-Dev cell design: Phase 6.1 H3-only A/B vs current 0.39 baseline (cheap smoke). Phase 6.2 H1 stacked on H3. Pre-register the three negative outcomes above.
- Cap_map: bump CAP_mwp_operand_selection (currently bottleneck) with H3 + H1 as candidate Tier 3 atoms.

## Anchor Citations Compiled

- Roy and Roth 2015 arXiv:1608.01413 (quantity schema, dependent verb)
- Liang et al. 2018 arXiv:1808.03028 (frame identification)
- arXiv:2306.04347 (world models for MWP)
- arXiv:1712.09391 (declarative knowledge mapping)
- arXiv:2211.12164 (OLGA transfer-type ontology)
- arXiv:2403.12744 (identify-and-ignore irrelevant conditions)
- arXiv:2601.06853 (DAGGER distractor-aware graph)
- Hou et al. MIT Press 2018 (bridging resolution)
- arXiv:2301.09723 (MWP commonsense)
- Miao Liang Su 2020 arXiv:2106.15772 (ASDiv corpus diversity)
- PMC3462165 (PFC-hippocampal arithmetic, Menon group)
- arXiv:2503.02303 (flexible PFC control over hippocampal episodic)

End drill.
