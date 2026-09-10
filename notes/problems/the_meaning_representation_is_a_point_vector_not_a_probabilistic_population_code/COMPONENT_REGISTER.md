# COMPONENT REGISTER -- what we created / upgraded / evaluated, BF state, and next priorities

Problem: `the_meaning_representation_is_a_point_vector_not_a_probabilistic_population_code`. Solver session, 2026-09-10.
BF vocabulary: **BF** = the operation IS the brain's computation (pinned / defensible computational-level; params
swept). **BF_SPIRIT** = right operation, engineering/fitted/supplied residual. **NOT_BF** = not the brain's operation.
Witness: `verification/test_ppc_meaning_representation.py` (57/57). NO `hdlab/` writes (Q111): components below marked
PROPOSED are for the strategy session to land.

## A. COMPONENTS WE CREATED (all in experiments/ + verification/; each carries a machine-checkable `__bf_status__`)
| component (experiments/*.py) | what it is | BF state | headline result |
|---|---|---|---|
| exp_ppc_precision_tracks_correctness_v1 | precision = accumulated-evidence GAIN (Ma/Pouget) | **BF** | gain->correctness rho 0.22 CI-sep above the point-vector peakedness baseline; curated-channel gain does NOT track (experience-quantity signature) |
| exp_ppc_fusion_v1 | gain-weighted PPC-additive fusion vs equal/peak/fitted | **BF** | LOCATED NEGATIVE: equal-weight is at the reweighting ceiling (a fitted weight fails too); gain matches fitted with no fit |
| exp_ppc_no_regression_v1 | recall-path byte-identity invariants | **BF** | uniform-gain == equal-weight bit-identical; recall read unchanged |
| exp_ppc_grow_by_reading_v1 | precision earned by reading | **BF** | DEP MRR rises with reading; calibration present |
| exp_ppc_selective_prediction_v1 | gain as reliability for deferral | **BF** | directional (raises accuracy at reduced coverage) |
| exp_all_bf_upstream_trace_v1 | parser-free directional SEQ channel + top-down loss trace | **BF** | SEQ matches the NOT_BF-parser channel at no cost; loss localised to exposure |
| exp_bf_learned_channel_landing_v1 | the landable parser-free channel | **BF** | {G,SEQ,CM} ties the parser chain; uniform is the correct gain for a supplied channel |
| exp_ppc_second_gold_powerup_v1 | SimLex+SimVerb robustness | **BF** | item 1 CI-sep on TWO golds, parser + parser-free |
| exp_ppc_grow_to_strength_v1 | grow-by-reading to ceiling (1.5M lines) | **BF** | SEQ 0.07->0.16 (~80% of ontology) by reading alone; raw-gain precision saturates (log form is the fix) |
| exp_ppc_reliability_deferral_v1 | convergent-cue agreement reliability | **BF** | unanimous agreement doubles accuracy but sparse at 3 cues |
| exp_ppc_population_reliability_v1 | PHASE-DIAGRAM move: dense population-consensus reliability | **BF** | deferral beats random CI-sep (+0.049 @ N=30) -- the reader CAN tell when a read is reliable |
| exp_meaning_depth_gap_v1 | diagnostic: relation-blindness of learned meaning | **BF_SPIRIT** | syn-vs-antonym AUC: learned 0.51-0.53, only supplied WordNet 0.87; channels diverse not redundant |
| exp_valence_polarity_meaning_channel_v1 | fix layer 1: affective valence polarity | **BF** | syn-vs-antonym AUC 0.535 -> 0.75 WITHOUT WordNet, CI-sep, twin collapses |
| exp_directional_consequence_channel_v1 | fix layer 2a: path-direction signature | **BF** | separates SCALAR converses (increase/decrease -0.78, open/close -0.54); fails transfer converses |
| exp_role_asymmetry_converse_channel_v1 | layer 2b drill-through of the transfer wall | **BF** | adjacency role-asymmetry INSUFFICIENT -> transfer converses need role-BOUND heads (parsing+binding) |
| exp_ppc_all_v1 | orchestration driver (caches the shared parse) | **BF_SPIRIT** | runs the four PPC cells over one parse |
| verification/test_ppc_meaning_representation.py | scaffold-free witness | -- | 57/57 (disk facts + landed metrics) |

## B. COMPONENTS PROPOSED FOR hdlab (Q111 -- strategy lands; `HDLAB_INTEGRATION_SPEC.md`)
| proposed component | BF state | note |
|---|---|---|
| parser-free directional learned channel = `ConceptSpace` ROUTE-B store + DIRECTIONAL typing + existing PPMI | **BF** (new) | reuse of existing organs + order-coding enhancement; removes the NOT_BF parser at no accuracy cost |
| AFFECTIVE-VALENCE dimension (reuse `affect_lexicon`+Warriner) added to the meaning representation | **BF** (new dim) | un-blinds antonymy (AUC 0.535->0.75); the affective spoke grounded_similarity omits |
| `convergent_cue_reader.w` -> intrinsic per-query GAIN RATIO (saturating/log form) | **BF** fix of a NOT_BF item | eliminates the fitted OUR-INVENTION weight |
| population-consensus RELIABILITY -> gain-based deferral on the read path | **BF** (new) | CI-sep deferral (+0.049) |

## C. COMPONENTS WE UPGRADED / EVALUATED (existing organs)
| organ | prior BF state | what we did | finding |
|---|---|---|---|
| `pos_tagger` + `arceager_parser` | **NOT_BF** (frozen supervised, hard-decode) | EVALUATED + ROUTED AROUND | no longer required by the meaning chain -- the parser-free SEQ channel matches it |
| `reading_grounding_loop.ConceptSpace` (ROUTE-B store) | **BF_SPIRIT** | REUSED (proposed directional-typed feed) | its co-occurrence store is an unordered BAG; directional typing turns it into an identity channel |
| `grounded_similarity` | **BF_SPIRIT** | EVALUATED | relation-blind on antonymy (AUC 0.51); OMITS the affective (VAD) dimension we add; cosine discards signed magnitude |
| `conceptual_meaning` (WordNet CM) | **BF_SPIRIT** (supplied) | EVALUATED | the only channel discriminating antonymy (0.87) but SUPPLIED; its gain anti-tracks correctness |
| `convergent_cue_reader` | **BF_SPIRIT**; its `w` = NOT_BF (fitted) | EVALUATED + BF fix proposed | the fitted `w` is the named OUR-INVENTION; gain ratio replaces it |
| `distributional_meaning_channel` | **BF_SPIRIT** | EVALUATED (reuse its PPMI) | existing PPMI organ; tuned to substitutability, not the similarity read |
| `affect_lexicon` | **BF_SPIRIT** | REUSED | supplies the valence dimension (Osgood/Russell/Barrett core affect) |
| `cleanup_family` / attractor (recall path) | **BF** | CONFIRMED UNTOUCHED | recall/recognition byte-identical under the proposed change |
| `predictive_world_model`, `generalized_event_knowledge`, `consequence_learning_loop`, `predictive_reader`, `incremental_parser` | **BF_SPIRIT** | EVALUATED as machinery for the next layers | the generative-consequence + role-binding organs the antonym residual needs; not yet wired to word meaning |

## D. NEXT PRIORITY STEPS (highest value first)
1. **LAND the 3 net-positive items (Q111)** -- parser-free directional channel; the affective-valence dimension
   (a CI-sep antonymy capability); replace `convergent_cue_reader.w` with the intrinsic gain ratio + wire
   population-consensus deferral. All BF, all reuse; recall path byte-identical. `HDLAB_INTEGRATION_SPEC.md`.
2. **FILE the generative ROLE-BINDING meaning channel** (transfer converses buy/sell) -- the deepest gap, wall
   researched to the bottom: needs role-bound argument heads (reuse `incremental_parser` + FHRR binding +
   `predictive_reader`/`situation_reader`), NOT co-occurrence. `NEXT_GAP...md` §5c. This is the substrate's named
   generative-world-model main event; the transfer-converse residual proves similarity cannot reach it.
3. **GROW the learned channel by reading to parity** -- SEQ was still rising at 1.5M lines (0.16 vs ontology 0.20);
   parser-free reading is cheap. Closes the exposure gap and lets the earned-gain precision turn on.
4. **END-TO-END live grounding-coverage measurement** -- the one number not yet taken (I measured the sense-
   assignment ranking through the live read, not the holistic live-loop coverage). Strategy's wiring domain.
