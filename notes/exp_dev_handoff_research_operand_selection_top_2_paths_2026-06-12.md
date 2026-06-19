# Research -> Exp-Dev (HANDOFF): Operand-selection drill TOP-2 paths recommended for cell -- Path 1 SRL + Path 5 hippocampal schema retrieval

**From:** Research  **Date:** 2026-06-12 (Day 3 evening)
**Re:** 2x deep drill on operand-selection mechanism class COMPLETE; top-2 ranked paths handed off

## TL;DR

Drill landed [[notes/research_drill_substrate_operand_selection_mwp_2x_2026-06-12.md]]. 5 substrate-only operand-selection paths identified; top-2 ranked for parallel cell:

| Rank | Path | P_deflated | Cost | Signal | Brain analogue |
|---|---|---|---|---|---|
| 1 | **SRL over Tier-A POS/NER** | 0.55 | medium 3-5d | HIGH +0.10-0.18 lift | prefrontal top-down attention + ventral-stream verb-argument |
| 2 | **Hippocampal schema retrieval via solution-history** | 0.45 | cheap 1-2d | MED-HIGH +0.06-0.12 lift | Tse 2007 schema integration + vMPFC-hippocampal |

Held in reserve: Path 3 coref+entity-state (P 0.50; fallback if SRL fails on single-sentence ASDiv); Path 4 theta-gamma slot-filler (P 0.40 cheap brain-direct); Path 5 DRT (P 0.35 heavy multi-week deferred).

Pre-registered fail-band: cell PASSES if EITHER path lifts +0.06 over 0.39 baseline; HARD-PASS +0.10; FAIL if both <0.04.

## Path 1: SRL over Tier-A (RECOMMENDED PRIMARY)

Mechanism: PropBank-style ARG0/ARG1/ARGM-LOC role labels for each verb-headed clause; numbers bound to ARG roles via HRR (operand = bind(verb, arg_role, number_vec)); operand-selection becomes ARG-role retrieval via cleanup.

Substrate impl: substrate POS + NER feed count-NB / perceptron SRL labeler (Tier-A precedent); bind(verb_HRR, role_HRR, number_HRR) per clause; query at op-time via unbind(question_verb, target_role).

Anchors:
- Marcheggiani & Titov 2017 "Encoding Sentences with GCN for SRL" EMNLP
- He et al. 2017 "Deep Semantic Role Labeling with Self-Attention"
- Roy & Roth 2015 quantity-extraction in MWP

Discriminating signal HIGH: ASDiv operand-selection failures dominated by "which number goes with which agent/recipient/location"; SRL directly addresses.

Cost medium: CoNLL-2005 SRL data ingestion + perceptron training (substrate-classical Tier-A precedent) + HRR binding wiring.

## Path 5: Hippocampal schema retrieval (RECOMMENDED SECONDARY)

Mechanism: substrate solution-history (existing partition) stores prior MWP scenarios as schema vectors; new problem retrieves k-nearest schema via cleanup; schema provides operand-role template; perceptron op-selector inherits operand bindings from retrieved schema.

Substrate impl: solution-history partition + retrieved-schema HRR -> bind operand-role slots to current numbers via cleanup transfer; reuses existing substrate-as-self-extending-engine infrastructure per [[substrate-as-self-extending-engine-4-3x-growth-2026-06-12]].

Anchors:
- Tse et al. 2007 "Schemas and Memory Consolidation" Science
- Gilboa & Marlatte 2017 "Neurobiology of Schemas and Schema-Mediated Memory" Trends Cog Sci
- Schlichting & Preston 2017 "Memory integration: neural mechanisms and implications"

Discriminating signal MED-HIGH: ASDiv has high schema-repetition across age-grade; failure mode = novel schemas miss retrieval.

Cost cheap: 1-2 days; solution-history already present + Tier-3 cleanup primitive + per-cap schema retrieval already wired.

## Complementary failure modes (why both)

Per substrate-quality-first: paths are non-redundant.
- Path 1 SRL addresses COMPREHENSION root cause via linguistic ground truth
- Path 5 schema retrieval addresses SCENARIO-SEMANTICS via substrate structural memory
- If Path 1 fails on single-sentence ASDiv (SRL labels not enough), Path 5 still has hippocampal schema lever
- If Path 5 fails on novel schemas, Path 1 still has linguistic ARG decomposition

Parallel cell rather than sequential.

## Pre-registered fail-band

| Outcome | Either-path lift over 0.39 baseline | Action |
|---|---|---|
| HARD-PASS | +0.10 | substrate-product positioning win; corpus + comprehension primitives |
| MIDDLE | +0.06 to +0.10 | partial win; pivot or augment |
| HARD-FAIL | <0.04 both paths | corpus-deficiency confirmed at operand level (4th independent angle) -> wait Phase 6 |

Per [[substrate-mwp-triangulation-corpus-bound-3rd-confirmation-2026-06-12]] memory: if BOTH paths FAIL, 4th triangulation = corpus-deficiency confirmed (not architectural ceiling). Honest negative IS evidence per refined brain-can-do-it rule.

## Recommended cell sequencing

1. **Path 5 first (cheap; 1-2 days)**: solution-history schema retrieval gates fast empirical signal. If >+0.06 lift = momentum + Path 1 SRL deferred to Phase 6 (richer corpus).
2. **Path 1 second (medium; 3-5 days)**: only if Path 5 < +0.06 lift OR if you want parallel coverage.
3. Path 3 coref fallback if Path 1 fails on single-sentence subset.

Sequencing rule: cheap-first per substrate-classical-NL methodology.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #43 (drill close) | C | 2x drill operand-selection 5 paths + top-2 ranked + hand-off to Exp-Dev |

## Cross-references

- Drill: notes/research_drill_substrate_operand_selection_mwp_2x_2026-06-12.md (full report)
- substrate-mwp-triangulation-corpus-bound-3rd-confirmation-2026-06-12 memory
- substrate-mwp-comprehension-blind-spot-corpus-limited-2026-06-12 memory
- substrate-as-self-extending-engine-4-3x-growth-2026-06-12 (Path 5 substrate-precedent)
- substrate-classical-NLP-methods-outperform-phasor-2026-06-11 (Path 1 Tier-A precedent)
- substrate-non-unique-role-binding-resolved-permutation-P-k-2026-06-12 (E3 P^k applies if multi-occurrence operand)

---

**Exp-Dev:** 2x deep drill operand-selection COMPLETE TOP-2 paths handed off + Path 1 SRL over Tier-A POS+NER P_deflated 0.55 medium 3-5d HIGH signal +0.10-0.18 lift PropBank ARG0/ARG1/ARGM-LOC role labels HRR bind(verb,role,number) operand-selection = ARG-role retrieval cleanup substrate-classical Tier-A precedent + Path 5 hippocampal schema retrieval via solution-history P_deflated 0.45 cheap 1-2d MED-HIGH signal +0.06-0.12 lift solution-history existing partition + cleanup transfer + substrate-as-self-extending-engine infrastructure + reserve Path 3 coref entity-state P 0.50 fallback single-sentence + Path 4 theta-gamma cheap brain-direct + Path 5 DRT heavy deferred + pre-reg HP +0.10 MID +0.06 FAIL <0.04 both + recommended SEQUENCE Path 5 cheap-first 1-2 days then Path 1 SRL if needed + complementary failure modes Path 1 COMPREHENSION linguistic Path 5 SCENARIO-SEMANTICS structural memory + per-brain-can-do-it triangulation rule if BOTH FAIL = 4th angle corpus-deficiency confirmed Phase 6 + Cycle 43 close + USER full-auto continuing alongside 7-axis re-measure with cross-disc batch (Cycle 42 close) recommendation.
