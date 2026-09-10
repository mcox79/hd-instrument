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
| exp_parser_graded_reliability_gated_patient_v1 | reliability-gated top-2 competition (closes the precision caveat) | **BF** | naive top-2 F1 collapses 0.418->0.269; **reliability-GATED net-beats hard head F1 CI-sep (+0.0036)**; twin 0.141 loses -- the brain-faithful readout is net-positive |
| exp_parser_learned_from_reading_v1 | UNSUPERVISED directional-PPMI attachment (first step) | **BF** | UAS 0.212 grows with reading 0.177->0.212, twin 0.111 loses, but BELOW the strong right-branching floor 0.285 (the trap) |
| exp_parser_selfsup_em_v1 | reading-learned parser with Naseem prior + DMV-class EM (graded marginal E-step) | **BF** | BREAKS the trap: UAS 0.312 > floor 0.285 CI-sep; prior +0.056 + EM +0.066 both required; twin loses. (NOTE: this config had a noisy lexical term ON; the clean POS-only number is 0.463 -- see the scorer-fix cell) |
| exp_parser_readlearned_scorer_fix_v1 | PROTOTYPE the surface-perceptron fix: distributed vs sparse lexical + POS+prior+EM | **BF** | clean reading-learned scorer **UAS 0.463 (non-root 0.443) beats floor on BOTH**, recovers 36% of floor->supervised gap; **REFUTES distributed-generalization hypothesis** (lexical HURTS -0.151; attachment is POS-structural, Klein-Manning); twin loses; 0.319 below supervised = text-only ceiling |
| exp_parser_dmv_valence_v1 | ATTACK the scorer wall with DMV VALENCE (real projective Eisner + EM, brute-force-verified) | **BF** | **LOCATED NEGATIVE**: valence UAS 0.322 <=10 / 0.221 full, BELOW arc-factored 0.463 -- valence NOT the lever (structural prior + soft EM already exceed POS-DMV); projectivity ceiling 0.979 (2.1% non-proj) |
| exp_parser_chain_vs_brain_eval_v1 | consolidated per-step CHAIN-vs-BRAIN evaluation (reads all landed metrics) | **BF** (synthesis) | one authoritative table: decode BF/done, scorer HYBRID at text-only ceiling, POS fixable; signal loss SCORER 20.7>>POS 3.0>>DECODE 0.2 |
| exp_parser_dmv_softem_v1 | the FAITHFUL soft-EM DMV (exact inside-outside, brute-verified Z+marginals+counts) | **BF** | fair test of the valence negative: soft-EM DMV 0.20-0.25 (even below Viterbi-EM) -- EM optimizes likelihood not accuracy; valence CONFIRMED not the lever |
| exp_parser_supervised_advantage_decomp_v1 | decompose the 0.463->0.782 wall by deprel/distance/POS-pair | **BF** (diagnostic) | wall = ~half CONVENTION (punct 0.15->0.64, case, cop, cc -- not brain-relevant) + half meaning (nsubj, nmod); content-only gap 0.267 |
| exp_parser_bf_structural_attack_v1 | TACKLE the nsubj wall with the BF Now-or-Never left-corner organ | **BF** | **WIN**: nsubj recall 0.565->0.714 (+0.149, ~half the gap; twin 0.633 loses), content UAS +0.012 -- reuse a proven BF organ, no new mechanism |
| exp_parser_grounded_ppattach_v1 | attack the last piece (nmod/PP) with grounded event knowledge (GEK) | **BF** | **LOCATED NEGATIVE**: grounded GEK 0.443 < recency 0.556 (covered-only 0.260); PP-attach is locality-dominated + GEK over-attaches to verbs (wrong signal for noun-modifier nmod) -- grounding is NOT the lever |
| exp_parser_fully_bf_chain_v1 | reading-learned POS induction (immediate-context PPMI-SVD k-means) + the FULLY-BF chain end-to-end (zero gold) | **BF** | POS induction many-to-one 0.323 (WEAK impl; Brown ~0.6-0.7); fully-BF chain COMPOUNDS (induced-POS UAS 0.034 << gold-POS 0.267) -- POS-induction quality is the binding constraint on a zero-gold chain |
| exp_parser_bf_tokenizer_v1 | BF tokenizer upgrade: Saffran transitional-probability segmentation from reading | **BF** | boundary F1 0.639 > over-segment floor 0.386, twin loses; ~0 chain loss on spaced English (mechanism prototyped) |
| exp_parser_brown_pos_bf_chain_v1 | BROWN clustering (MI-maximizing exchange, verified) = the RIGHT POS induction + fully-BF chain re-run | **BF** | **DID IT RIGHT**: many-to-one **0.745** (vs easy k-means 0.323; supervised 0.944); F monotonic + incremental delta verified == full; UNBLOCKS fully-BF chain 0.034->0.238 (7x); residual = 20% POS error compounds + scorer ceiling |
| exp_parser_bootstrap_pos_parse_v1 | OPP-1: bootstrap POS<->parse (re-induce categories from dependency context, iterate) | **BF** | **LOCATED NEGATIVE**: drifts -- dep-context categories from a weak (0.24) parse are WORSE (0.51<0.745); no gain. Compounding not closable by bootstrapping from a weak text-only parse |
| exp_parser_richer_bf_scorer_v1 | OPP-2: full incremental left-corner STRUCTURE (Now-or-Never) into the reading scorer | **BF** | **WIN**: verb-arg recall 0.627->0.740 (+0.113), UAS 0.464->0.472, content 0.478->0.493; twin loses -- STRUCTURE is the lever distributional stats lacked |
| exp_parser_hybrid_foundation_v1 | OPP-3: hybrid = frozen treebank foundation + register-general BF structure cue (in-domain + OOD) | **BF** | **LOCATED NEGATIVE**: 0 gain in-domain (0.7825) AND OOD (0.7408) -- the structure cue is redundant with the strong supervised scorer; OOD loss is lexical/register, not structural |
| exp_parser_deviation_chase_v1 | TOP-DOWN deviation chase: decompose the POS-link loss (decode vs acquisition vs ambiguity) | **BF** (diagnostic) | POS-link loss is 100% ACQUISITION (hard-decode costs 0.0002 ~ BF-equivalent, peaked posterior); 87% of mistags confident-wrong (OOD coverage), 13% ambiguity. Ledger: `DEVIATION_LEDGER.md` |
| exp_parser_grounded_thematic_fit_v1 | the grounded lever done RIGHT: thematic-fit (verb->argument-TYPE, McRae/Ferretti) for verb-object attachment | **BF** | **LOCATED NEGATIVE (2nd grounded)**: thematic-fit beats its twin (0.464>0.408, real signal) but FAR below recency (0.682) -- attachment is locality-dominated; text-derived grounding HURTS. Grounded-from-text lever CLOSED; missing input = PERCEPTUAL grounding |
| exp_parser_worldmodel_arbitration_v1 | test the WORLD MODEL the brain's way: syntax proposes, world model arbitrates ONLY uncertain arcs | **BF** | **LOCATED NEGATIVE (3rd) + the unifying insight**: selective WM arbitration +0.0007 (negligible, twin ties); uniform HURTS (0.742). Only 1.3% of tokens are uncertain but 21% of heads wrong -> errors are CONFIDENT (supervised acquisition); NO arbitration can reach them. WM-rescorer is not the lever |
| exp_parser_coarse_class_coherence_v1 | test the owner's coref-win mechanism (coarse WordNet-supersense class coherence) for the PARSER | **BF** | **LOCATED NEGATIVE (4th semantic) + CORRECTION**: coarse-class coherence added to attachment HURTS (best weight 0; twin 0.25). It won on COREF but does NOT transfer to parse attachment -> DIFFERENT losses need DIFFERENT mechanisms; "generative model" was over-claimed; the parser wants STRUCTURE (OPP-2), coref wants focus+coarse-class |
| exp_parser_structure_optimize_v1 | push the structure win + NEW coordination-parallelism cue (Coordinate Structure); optimize the combined structural parse | **BF** | **WIN**: coordination parallelism lifts cc/conj recall 0.078->0.218 (+0.14, twin loses); optimized (verb-arg + coord, complementary) UAS 0.464->0.476, verb-arg 0.627->0.728. Two complementary BF structural levers |
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
| `graded_competition` | **BF** (pinned) | EVALUATED as the readout host | the reliability-weighted competition (Lewis-Vasishth) that hosts the reliability-gated top-2 selection; already the substrate's discrete->graded operation -- the wire point for LAND item 2 |
| `distributional_meaning_channel` / `reading_grounding_loop` directional channel | **BF_SPIRIT** | EVALUATED as acquisition substrate | the PPMI + directional-context organs the reading-learned scorer reuses (generalization the sparse bigram lacks) |

## D. NEXT PRIORITY STEPS
1. **LAND items 1a+1b** (exact decode + marginal reliability) -- BF, recall path byte-identical,
   removes a NOT_BF fitted logistic. `HDLAB_INTEGRATION_SPEC.md`.
2. **WIRE item 2** (top-2 reliability-ranked reach) into the role competition; measure the modern board.
3. **FILE the reading-learned arc SCORER** (DMV-class valence + EM + incremental) -- the path to EXCEED the
   frozen treebank scorer; the deepest, highest-leverage upchain BF upgrade. `NEXT_GAP_learned_from_reading_scorer.md`.
4. **Sibling NOT_BF:** `pos_tagger` acquisition (same supervised-treebank story, one level up) -- a candidate
   follow-on that would make the reading-learned parser's POS input BF too.
