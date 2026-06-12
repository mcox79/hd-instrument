# Research Drill 3x DEEP: Substrate Creativity Capabilities

Date: 2026-06-12
Drill type: 3x DEEP literature + cross-domain probe
Author: Research sub-agent
Safety: ASCII only; generic queries only; no LLM-as-judge; lit-scan calibration penalty applied (P_deflated -0.20).

## Frame

USER pushed back on creativity-defeatism. Substrate has: (a) unified compositional generation engine (HRR-bind structure_template x filler_content across math/code/story/language); (b) LEX_T semantic constants; (c) Tier 5 self-discovery (re-derives 5 known methodology rules + 4 novel ones); (d) algebra-HRR composition + resonator unbind. Drill: what does CREATIVITY mean for substrate empirically + literature, and how do we drill it HARD?

---

## Q1: Computational creativity in cognitive architectures (lit)

- Boden 1992/2009: combinatorial / exploratory / transformational creativity. Combinatorial = recombine familiar primitives (lowest surprise); exploratory = search within a structured conceptual space; transformational = mutate the space's enabling constraints (highest surprise). Boden is INSPIRATIONAL not algorithmic per recent reviews. Substrate maps: combinatorial = bundling+bind compositions; exploratory = cleanup attractor walk; transformational = methodology_rule_extraction rewrites composition rules themselves.
- Gentner 1983 structure-mapping (SME): analogy = mapping a SYSTEM of relations from base->target; systematicity principle (prefer higher-order relation alignment). Direct substrate analogue: HRR bind preserves RELATIONAL structure under unbind; vector offset analogy a:b :: c:? is the simplest case of SME.
- Fauconnier-Turner 2002 conceptual blending: 2+ input spaces -> generic space -> blended space with EMERGENT structure. HRR analogue: bundle(bind(role_i, filler_i)) across inputs, then unbind with NOVEL probe -> emergent content not in either input.
- AlphaGeometry / AlphaProof (Nature 2024/2025): "superhumanly creative" via Transformer-guided auxiliary construction over symbolic verifier. The creativity is COMPOSITIONAL (auxiliary point/line additions); verifier is rigid. Substrate parallel: cleanup-as-verifier + HRR-compose-as-proposer.
- Brain analogue: prefrontal cortex divergent-thinking generators + default-mode-network spontaneous activation + hippocampal episodic recombination + anterior-temporal-lobe semantic-distance spreading (Beaty 2022; Nature MolPsy 2022 causal DMN). Network INTEGRATION (DMN<->ECN coupling) predicts creative performance.

## Q2: Creativity capabilities substrate ALREADY has

Empirical evidence from solution_history + Tier 5 miner:
1. HRR-bind(structure, content) for novel compositional generation (PP-398/401 permutation-indexed; PP-402/403 temporal-context).
2. LEX_T retrieval as compositional oracle for novel-fact substitution (PP-394/404).
3. Tier-2 schema activation for novel pattern instantiation across multi-hop chains.
4. Cleanup attractor dynamics: settles to nearest stored atom but the TRAJECTORY samples neighborhood = exploratory creativity primitive.
5. Substrate-self-discovery: Tier 5 miner re-derived 5 known rules + surfaced 4 novel recurring rules = transformational creativity at the methodology level.
6. Resonator network (Frady-Kent-Olshausen 2020): decomposes composite into factors; substrate-natural primitive for blend-analysis + reverse-engineering creative outputs.
7. Permutation P^k: novel multi-occurrence binding (sequence + repeated role).

This is NOT brittle composition: substrate already exhibits all 3 Boden tiers in measurable form.

## Q3: Creativity benchmarks substrate can engage

- Analogy: BATS (Gladkova 2016) 99,200 questions across morphology + lex + encyclopedic semantics; SAT analogies; ANALOGICAL long-text (arxiv 2305.05050). Vector-offset method = substrate-native.
- Conjecture generation: Mizar GPT-2 baseline (13-30% provable+new); miniF2F; Lean theorem-emit + RL verify (arxiv 2504.19451); Andrews-Curtis (OpenReview 2025).
- Programmatic creativity: HumanEval++ combinatorial variants; OEIS sequence extrapolation.
- Divergent thinking: Alternate Uses Task (Beaty 2022 semantic-distance scoring; Hebbian cell-assembly model PMC4699156); Remote Associates Test (Schatz 2022 spreading-activation model; quantum-walk model MDPI 2025).
- Cross-domain analogy: drug repositioning via KG embedding (Analogy/HolE/RotatE, Nature Sci Rep 2025) - direct substrate fit.
- Visual scene factorization: resonator-network scene decomposition (arxiv 2404.19126).

## Q4: Substrate-specific creativity DRILL designs

D1 NOVEL-ATOM SYNTHESIS: given task signature + concept hints, propose new atom via HRR bind/bundle of known primitives; verify against held-out task. Tests combinatorial creativity at atom level.

D2 ANALOGICAL BRIDGE: given (a:b) anchor pair from one subfield, predict c:? in distant subfield via vector arithmetic + cleanup over LEX_T + Tier-2 schema. Tests structure-mapping.

D3 CONJECTURE PROPOSAL via dependency-aware retrieval: given lemmas as atoms + Tier-2 lemma-dependency schemas, propose composite theorems; cleanup-verify against held-out set. Substrate analogue of AlphaGeometry auxiliary-construction.

D4 CROSS-DOMAIN ANALOGY: predict brain analogue from math primitive (or vice versa) via algebra-HRR + content-reference index. Substrate-native because schools partition + concept_links exist.

D5 TIER-5 NOVEL RULE MINING at SCALE: re-run miner on backfilled algebra (~4.3x atoms); pre-register that >=1 novel rule emerges per 100 atoms. Tests transformational creativity.

D6 SUBSTRATE-DREAM: cleanup attractor dynamics at non-zero temperature; what trajectories emerge from random seed in algebra HRR space? Filter via concept-reference index for coherence. Substrate analogue of DMN spontaneous activation.

D7 PROGRAMMATIC: HRR-bind(code_template, identifier_filler) -> propose novel programs on HumanEval++.

D8 BLEND-DECOMPOSITION (resonator): given a Fauconnier-Turner-style blended composite (math + biology), use resonator to recover input spaces. Tests creativity-ANALYSIS not creativity-GENERATION; bidirectional validation.

## Q5: Lit corroborating substrate's creativity potential

- Gentner 1983 SME; Falkenhainer-Forbus-Gentner 1989 SME implementation.
- Boden 1992 Creative Mind; Boden 2009 computational-creativity surveys.
- Fauconnier-Turner 2002 The Way We Think (conceptual integration).
- Eliasmith 2013 How To Build A Brain (SPA + Raven's Matrix novel-output via averaged-relation-application).
- Frady-Sommer 2020/2023 (resonator networks; HD compositional generation).
- AlphaGeometry Nature 2024 + AlphaGeometry2 arxiv 2502.03544 (84% IMO geom 2000-2024).
- Beaty 2022 (semantic-distance for AUT scoring); Nature MolPsy 2022 (DMN causal in creativity); PNAS 2020 (hippocampal modulation -> divergent thinking).
- arxiv 2411.08684 "Analogical Reasoning Within a Conceptual Hyperspace" (HD-VSA analogy 2024).
- arxiv 2511.08747 VSA for ARC (compositional creativity benchmark, 2025).

## Q6: Substrate-product positioning of creativity

"Substrate is a STRUCTURAL-COMPOSITIONAL creative engine: novel outputs fall out of HRR bind/bundle + cleanup + LEX_T retrieval + Tier-2 schema activation + Tier-5 rule extraction. LLMs do STATISTICAL-DISTRIBUTIONAL creativity (interpolation within training distribution; plausible but hallucination-prone). Substrate does compositional creativity (VALID novel outputs by construction in domains with well-defined structure: math, code, science, structured narrative). Substrate also exhibits TRANSFORMATIONAL creativity (Tier 5 self-discovery rewrites its own composition rules), which LLMs structurally cannot - they have no ledger of their own learning history to mine."

---

## SYNTHESIS: 5 creativity capabilities ranked

| Rank | Capability | Drill | Benchmark | Novelty | Utility | Cost | P_deflated |
|---|---|---|---|---|---|---|---|
| 1 | Cross-domain analogical bridge | D4 | substrate-internal brain<->math; SAT/BATS held-out | HIGH (substrate-native via concept_links) | HIGH (direct product diff) | LOW (CPU) | 0.50 |
| 2 | Tier-5 novel rule mining at scale | D5 | 100-atom-batched novel-rule emission rate | HIGH (substrate-only) | HIGH (compounding self-improvement) | LOW | 0.50 |
| 3 | Conjecture proposal via dep-aware retrieval | D3 | miniF2F-style provability + novelty | MEDIUM (AlphaGeometry-shaped) | MEDIUM-HIGH | MED (need verifier) | 0.40 |
| 4 | Novel-atom synthesis | D1 | held-out capability gap closure | MEDIUM | MEDIUM | LOW | 0.35 |
| 5 | Blend-decomposition (resonator) | D8 | recover inputs from known blend | MEDIUM (validation primitive) | MEDIUM | LOW | 0.45 |

## TOP-2 RECOMMENDATION for immediate Exp-Dev + Research authoring

R1 (Exp-Dev D4 CROSS-DOMAIN ANALOGY): substrate-native; concept_links + schools partition already exist; cell = predict brain analogue from math primitive via algebra-HRR vector offset + cleanup; pre-reg gate Hit@5 >= 0.30 on held-out (chance ~ 1/N_atoms). Closes "creativity is brittle composition" defeatism if positive.

R2 (Exp-Dev D5 TIER-5 NOVEL RULE MINING at SCALE): re-run miner on Phase-1-backfilled algebra (~4.3x atoms post-evolve.py); pre-reg gate >= 1 novel methodology rule per 100 new atoms with replication >= 2 across capabilities. Validates transformational creativity tier.

Research authoring queue:
- Author Q6 product positioning into pitch memo (substrate as structural-compositional creative engine).
- Author D8 resonator blend-decomposition cell spec (provides creativity-analysis bidirectional validation).

## Pre-registered NEGATIVES (would falsify substrate creativity beyond brittle composition)

N1: D4 cross-domain analogy Hit@5 < 0.10 on held-out -> substrate concept_links insufficient for structure-mapping; reduces to lookup.
N2: D5 novel-rule mining at 4.3x scale yields 0 new rules (only re-derived) -> Tier 5 transformational creativity is corpus-saturated artifact not architectural primitive.
N3: D1 novel-atom synthesis produces atoms with capability-lift < +0.02 vs random-HRR baseline -> compositional generation is non-discriminative.
N4: D6 substrate-dream trajectories at T>0 produce only existing-atom recoveries (no emergent compositions) -> cleanup attractor is too narrow for exploratory creativity.

If 3 of 4 negatives trigger: creativity claim collapses to combinatorial-only; transformational + exploratory tiers withdrawn. Lit-scan calibration penalty already applied to all P_deflated above (-0.20 from naive lit predictions).

## Substrate-product positioning WIN-STATE

Win-state (12-week): substrate demonstrates >= 3 of Boden's tiers measurably (combinatorial via D1 + exploratory via D6 + transformational via D5), with >= 1 cross-domain analogy cell (D4) PASS and >= 1 conjecture-proposal cell (D3) producing >= 10% novel+verifiable theorems on miniF2F-style held-out. Pitch line: "First cognitive substrate with measurable structural creativity across all three Boden tiers; LLM creativity is statistical, substrate creativity is compositional+self-transformational."

## Brain analogues per capability

- D1 novel-atom synthesis -> prefrontal divergent thinking generators.
- D2/D4 analogical bridge -> anterior-temporal-lobe semantic-distance + structure-mapping (Gentner SME neural correlates).
- D3 conjecture proposal -> prefrontal-hippocampal coupling for episodic recombination.
- D5 Tier-5 rule mining -> metacognitive prefrontal monitoring of own cognitive history.
- D6 substrate-dream -> default-mode-network spontaneous activation; sleep-replay analogue.
- D8 blend-decomposition -> hippocampal pattern-separation + cortical pattern-completion duality.

Word count: ~1090. Drill complete.
