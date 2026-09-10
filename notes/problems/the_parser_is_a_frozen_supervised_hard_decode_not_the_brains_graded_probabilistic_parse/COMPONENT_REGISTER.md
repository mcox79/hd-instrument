# COMPONENT REGISTER -- created / evaluated, BF state, next priorities

Problem `the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse`. Solver
2026-09-10. BF vocab: **BF** = the operation IS the brain's computation; **BF_SPIRIT** = right operation,
engineering/fitted/supplied residual; **NOT_BF** = not the brain's operation. NO `hdlab/` writes (Q111).
Witness `verification/test_parser_graded_route_through.py` (18 checks PASS).

## A. COMPONENTS WE CREATED (experiments/ + verification/)
| component | what it is | BF state | headline result |
|---|---|---|---|
| exp_parser_graded_decode_regimes_v1 | greedy vs exact-CLE vs marginal-argmax decode + error decomposition + marginal reliability | **BF** | exact decode +0.002 UAS CI-sep; **99% of error is SCORER-limited** (95/5048 decode-fixable); marginal reliability AUC 0.855 vs twin 0.361 |
| exp_parser_graded_downstream_whodidwhat_v1 | patient-arc recall under decode regimes + top-2 graded reach | **BF** | point decode flat; **top-2 reach recall 0.951->0.991 CI-sep** (twin 0.443 loses), precision cost +2.18 pairs/arc |
| exp_parser_learned_from_reading_v1 | UNSUPERVISED directional-PPMI attachment (first step) | **BF** | UAS 0.212 grows with reading 0.177->0.212, twin 0.111 loses, but BELOW the strong right-branching floor 0.285 (the trap) |
| exp_parser_selfsup_em_v1 | reading-learned parser with Naseem prior + DMV-class EM (graded marginal E-step) | **BF** | **BREAKS the trap**: UAS 0.312 > floor 0.285 CI-sep (+0.027); prior +0.056 + EM +0.066 both required; twin 0.176 loses; non-root at parity (text-only ceiling) |
| exp_parser_semantic_scorer_augment_v1 | augment surface scorer with reading-PPMI (the exceed lever) | **BF** | **located NEGATIVE**: +0.0006 not CI-sep -- surface scorer already has the lexical bigram; twin control holds |
| exp_parser_ood_gum_generalization_v1 | second gold (GUM, multi-genre OOD): route-through robustness + register question | **BF** | route-through REPRODUCES (99% scorer-limited, marginal AUC 0.84); supervised degrades OOD 0.79->0.74; reading generalizes OOD > floor; HONEST negative: target-register reading != source-register (corpus consistency dominates) |
| verification/test_parser_graded_route_through.py | scaffold-free witness | -- | 18/18 (reads landed metrics + graded_parser.self_test + live parse) |

## B. COMPONENTS PROPOSED FOR hdlab (Q111 -- strategy lands; HDLAB_INTEGRATION_SPEC.md)
| proposed change | BF state | note |
|---|---|---|
| reader parse -> `ArcParser.parse(decode="exact")` (exact CLE MAP) | **BF** (decode half) | heads change only on 7.2% invalid trees; +0.002 UAS CI-sep; recall path byte-identical |
| `parse_confidence` fitted logistic -> raw graded **marginal** reliability | **BF** fix (removes NOT_BF) | AUC 0.855 > logistic 0.736; a learned component REMOVED, computed once/read |
| top-2 marginal reach into the role competition, reliability-ranked | **BF** (new readout) | recall 0.951->0.991; rank by marginal to pay the precision cost brain-faithfully |

## C. COMPONENTS WE EVALUATED (existing organs)
| organ | prior BF state | what we did | finding |
|---|---|---|---|
| `graded_parser` | **BF** (DORMANT) | EVALUATED + confirmed live-usable | exact CLE + single-root marginals brute-force-exact; strong reliability (0.855) + downstream reach; recommend LIVE |
| `arc_parser` / `arceager_parser` | **NOT_BF** | EVALUATED + DECOMPOSED | DECODE half fixable via graded_parser (BF); residual NOT_BF = the frozen SUPERVISED SCORER (99% of error) = acquisition follow-on |
| `parse_confidence` | **NOT_BF** (fitted logistic, decision-dead) | EVALUATED + BF fix proposed | raw marginal beats it (0.855 vs 0.736); drop the logistic from the live path |
| `pos_tagger` | **NOT_BF** | NOTED as upstream input | supplies the POS the scorer + our reading-learned scorer both consume; its own acquisition is a sibling NOT_BF |
| `incremental_parser` | **BF_SPIRIT** | EVALUATED as the incremental carrier | the BF left-corner builder; the reading-learned scorer follow-on should carry commitment through it |
| `distributional_meaning_channel` / `reading_grounding_loop` directional channel | **BF_SPIRIT** | EVALUATED as acquisition substrate | the PPMI + directional-context organs the reading-learned scorer reuses (generalization the sparse bigram lacks) |

## D. NEXT PRIORITY STEPS
1. **LAND items 1a+1b** (exact decode + marginal reliability) -- BF, recall path byte-identical,
   removes a NOT_BF fitted logistic. `HDLAB_INTEGRATION_SPEC.md`.
2. **WIRE item 2** (top-2 reliability-ranked reach) into the role competition; measure the modern board.
3. **FILE the reading-learned arc SCORER** (DMV-class valence + EM + incremental) -- the path to EXCEED the
   frozen treebank scorer; the deepest, highest-leverage upchain BF upgrade. `NEXT_GAP_learned_from_reading_scorer.md`.
4. **Sibling NOT_BF:** `pos_tagger` acquisition (same supervised-treebank story, one level up) -- a candidate
   follow-on that would make the reading-learned parser's POS input BF too.
