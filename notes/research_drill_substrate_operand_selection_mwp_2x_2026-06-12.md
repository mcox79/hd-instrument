# Research Drill: Substrate Operand-Selection Mechanism Class for MWP Comprehension (2x DEEP)

Date: 2026-06-12
Type: Literature scan + cross-domain probe
Bottleneck: ASDiv 1-op operand-selection plateau 0.34-0.39 across 3 substrate mechanism classes (discriminative perceptron / world-model schema-simulation / BMA ensemble); op-mapping solved, operand selection is COMPREHENSION-bound (which numbers + scenario semantics).

Lit-scan calibration penalty: P_deflated by 0.15-0.25 applied. Novel-synthesis cap 0.50.

## Path 1: Semantic Role Labeling (SRL) over substrate Tier-A POS/NER

1. Mechanism: PropBank-style ARG0/ARG1/ARGM-LOC role-labels for each verb-headed clause; numbers bound to ARG-roles via HRR (operand = bind(verb, arg_role, number_vec)); operand-selection becomes ARG-role retrieval via cleanup.
2. Brain analogue: prefrontal top-down attention selecting role-relevant operands; ventral-stream verb-argument structure.
3. Anchors: Marcheggiani & Titov 2017 "Encoding Sentences with GCN for SRL" EMNLP; He et al. 2017 "Deep Semantic Role Labeling with Self-Attention"; Roy & Roth 2015 quantity-extraction in MWP.
4. Substrate impl: substrate POS + NER feed a count-NB / perceptron SRL labeler (Tier-A precedent); bind(verb_HRR, role_HRR, number_HRR) per clause; query at op-time via unbind(question_verb, target_role).
5. Discriminating signal: HIGH. ASDiv operand-selection failures are dominated by "which number goes with which agent/recipient/location"; SRL directly addresses this. Estimated lift +0.10-0.18 over 0.34-0.39 baseline.
6. Cost: medium (3-5 days; CoNLL-2005 SRL data ingestion + perceptron training + HRR binding wiring).
7. P_deflated: 0.55 (high lit confidence + strong substrate-fit + on-priority for comprehension; capped by lit-calibration penalty).

## Path 2: Coreference Resolution + Entity-State Tracking

1. Mechanism: cluster coreferent mentions (the apples / them / they) into entity HRR vectors; maintain per-entity quantity-state slot updated by verb-action (gave -> subtract from giver, add to receiver); operand-selection queries entity-state at question-time.
2. Brain analogue: hippocampal episodic entity tracking + binding-pool working-memory updates.
3. Anchors: Roy & Roth 2018 "Mapping to Declarative Knowledge for Word Problem Solving" TACL; Toshniwal et al. 2022 "Efficient and Interpretable Neural Models for Entity Tracking" EMNLP; Lee et al. 2017 end-to-end neural coref EMNLP.
4. Substrate impl: NER mentions -> cleanup-clustered entity HRR (substrate already has cluster primitive); per-entity "quantity slot" = scalar bound to entity_HRR via fhrr_bind; verb-triggered slot updates via Tier-2 substrate-classical transition table.
5. Discriminating signal: HIGH for multi-sentence ASDiv (pronouns + repeated noun phrases); operand-selection failures concentrated in entity-confusion. Estimated lift +0.08-0.15.
6. Cost: medium (3-5 days; OntoNotes coref subset + entity-state tracking module).
7. P_deflated: 0.50 (strong fit but ASDiv 1-op sometimes single-sentence so entity-tracking partial; lit-calibration cap).

## Path 3: Discourse Representation Theory (DRT) discourse referents

1. Mechanism: build DRS (discourse representation structure) per problem; each number introduces a discourse referent + conditions (owner/location/time); operand-selection = DRS query matching question conditions.
2. Brain analogue: hippocampal-VMPFC premise integration for logical reasoning (multimodal imaging shows hippocampus active during premise integration).
3. Anchors: Kamp & Reyle 1993 "From Discourse to Logic" Springer; Ravichander et al. 2019 "EQUATE: Benchmark for Quantitative Reasoning in NLI" CoNLL; van Eijck & Kamp 1997 chapter.
4. Substrate impl: each number -> referent HRR; conditions = bind(referent, attribute_role, value_HRR) stacked in superposition (FHRR bundling); question -> conditional unbind chain.
5. Discriminating signal: MEDIUM-HIGH. DRT is semantics-complete but ingestion is corpus-heavy; addresses scenario-semantics gap directly.
6. Cost: heavy (multi-week; DRT parser ingestion or weak-label DRS from Tier-A primitives).
7. P_deflated: 0.35 (heavy cost penalty + no substrate-precedent DRT parser; high theoretical fit but corpus-expensive).

## Path 4: Theta-gamma slot-filler binding for operand-role assignment

1. Mechanism: theta-cycle = problem clause; gamma-subcycle = role slot (agent/patient/quantity/recipient); each gamma slot binds one operand-role pair via HRR; question-time readout retrieves bound slots.
2. Brain analogue: theta-gamma phase-amplitude coupling for ordered slot binding (Lisman-Jensen model); hippocampal CA1 evidence.
3. Anchors: Heusser et al. 2016 "Episodic sequence memory is supported by a theta-gamma phase code" Nat Neurosci; Lisman & Jensen 2013 "The Theta-Gamma Neural Code" Neuron; Bahramisharif et al. 2018 theta-gamma binding Sci Rep.
4. Substrate impl: substrate HRR superposition with positional roles indexed by gamma-slot HRR vectors (existing primitive); clauses = theta-cycle = separate FHRR shards; cleanup retrieves slot-filler bindings. Pure substrate-native, brain-direct.
5. Discriminating signal: MEDIUM. Tight brain-substrate map but slot-count is ad-hoc; risks over-engineering vs SRL which uses linguistic ground truth.
6. Cost: cheap (1-2 days; substrate HRR primitives + slot-vector codebook already exist).
7. P_deflated: 0.40 (substrate-fit ceiling high + cheap; brain-plausibility strong; uncertain on signal magnitude without linguistic anchor).

## Path 5: Hippocampal schema integration via solution-history scenario retrieval

1. Mechanism: substrate solution-history (existing partition) stores prior MWP scenarios as schema vectors; new problem retrieves k-nearest schema via cleanup; schema provides operand-role template; perceptron op-selector inherits operand bindings from retrieved schema.
2. Brain analogue: hippocampal schema integration scaffolding new memories on existing schemas (Tse et al. 2007 schema-effect; vMPFC-hippocampal interaction).
3. Anchors: Tse et al. 2007 "Schemas and Memory Consolidation" Science; Gilboa & Marlatte 2017 "Neurobiology of Schemas and Schema-Mediated Memory" Trends Cog Sci; Schlichting & Preston 2017 "Memory integration: neural mechanisms and implications".
4. Substrate impl: solution-history partition + retrieved-schema HRR -> bind operand-role slots to current numbers via cleanup transfer; reuses existing substrate-as-self-extending-engine infrastructure.
5. Discriminating signal: MEDIUM-HIGH for ASDiv (high schema-repetition across age-grade problems); failure mode = novel schemas miss retrieval. Estimated lift +0.06-0.12.
6. Cost: cheap (1-2 days; solution-history already present + Tier-3 cleanup primitive + per-cap schema retrieval already wired).
7. P_deflated: 0.45 (cheap + substrate-precedent strong via self-extending engine; lit-calibration deflates predicted lift).

## Ranking

| Rank | Path | P_deflated | Cost | Signal |
|------|------|-----------|------|--------|
| 1 | SRL over Tier-A | 0.55 | medium | HIGH |
| 2 | Hippocampal schema retrieval | 0.45 | cheap | MED-HIGH |
| 3 | Coreference + entity-state | 0.50 | medium | HIGH |
| 4 | Theta-gamma slot-filler | 0.40 | cheap | MEDIUM |
| 5 | DRT discourse referents | 0.35 | heavy | MED-HIGH |

## Recommendation for Exp-Dev cell

TOP-2 (parallel cell):
- Path 1 (SRL): highest P_deflated + directly addresses ASDiv operand-confusion failure mode; substrate-classical Tier-A precedent (POS/NER 0.9+) supports SRL labeler trainability.
- Path 5 (schema retrieval): cheapest + reuses substrate self-extending engine infrastructure; rapid signal in 1-2 days; if it fails fast, redirects budget to Path 3 (coref) without disturbing Path 1.

Rationale: Path 1 hits the COMPREHENSION root cause with linguistic ground truth; Path 5 hits SCENARIO-SEMANTICS via substrate's own structural memory. Complementary failure modes -> non-redundant cell. Path 3 (coref) held in reserve as fallback if SRL labeler fails on single-sentence ASDiv subset.

Pre-registered fail-band: cell PASSES if either path lifts operand-selection accuracy +0.06 over 0.39 baseline; HARD-PASS if +0.10; FAIL if both <0.04.
