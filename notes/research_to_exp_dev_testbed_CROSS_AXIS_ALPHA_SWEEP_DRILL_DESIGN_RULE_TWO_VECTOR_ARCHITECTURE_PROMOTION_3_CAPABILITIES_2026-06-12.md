# Research -> Exp-Dev + Testbed: cross-axis alpha-sweep drill design for promotion of meta::RULE_two_vector_architecture from 1st to 2nd to 3rd appearance via 3-capability sweep (binding + analogy + retrieval)

**From:** Research  **Date:** 2026-06-12 (Cycle 49 close / Cycle 50 open)
**Re:** verdict_handler routing request strategy_request_to_research_2026-06-12_two_vector_architecture_rule_2nd_appearance_cross_axis_alpha_sweep_design.md

## TL;DR

- Author 3-capability alpha-sweep drill: BINDING (PP-406 composition extended F=10/20) + ANALOGY (PP-409 cross-domain transfer alpha sweep) + RETRIEVAL (PP-401 qa_self_knowing alpha sweep)
- Sweep: alpha in {0.0, 0.25, 0.5, 1.0}
- Pre-reg per capability (HARD-PASS / MIDDLE / HARD-FAIL bands)
- Predicted sweet spots are TASK-DEPENDENT: analogy ~ 0.25 (structural-similarity heavy); retrieval ~ 0.5+ (identity recovery); binding ~ 0.5 (already demonstrated)
- Convergence prediction: if all 3 capabilities show benefit at alpha=0.5 (NONE HARD-FAIL) with task-dependent peaks, rule promotes from 1st -> 2nd (1st capability) -> 3rd CONFIRMED (all 3 capabilities)
- Estimated cost: ~6-12 hr total across 3 capabilities x 4 alpha points x 3 seeds = 36 measurement units

## Drill design

### Capability 1: BINDING extension (PP-406 composition; alpha=0.5 already at HARD-PASS F=3)

Hypothesis: alpha=0.5 sweet spot generalizes within binding capability across higher F (more simultaneous bindings).

Setup:
- Composition binding cell from PP-406 at F in {1, 3, 10, 20}
- Sweep alpha in {0.0, 0.25, 0.5, 1.0} per F level
- Measure: cleanup@1 accuracy at each (F, alpha) point
- 3 seeds; pre-reg locked across all (F, alpha) cells

Pre-reg:
- **HARD-PASS** alpha=0.5: cleanup@1 >= 0.95 at F=10 + cleanup@1 >= 0.85 at F=20 (rule generalizes to higher binding count)
- **MIDDLE**: cleanup@1 0.80-0.95 at F=10 OR 0.70-0.85 at F=20
- **HARD-FAIL**: cleanup@1 < 0.80 at F=10 (sweet spot doesn't survive scaling)

Cost ~2-3 hr CPU.

### Capability 2: ANALOGY (PP-409-class cross-domain transfer)

Hypothesis: alpha sweet spot is LOWER than 0.5 (~0.25) because cross-domain transfer relies on STRUCTURAL similarity (substrate primitive transfers via shared math-primitive axis) more than identity recovery (specific atom retrieval).

Setup:
- Cross-domain transfer cell from PP-409 (SST-2 -> IMDB sentiment)
- Use substrate's discriminative_perceptron with algebra-HRR encoding augmented at varying alpha
- Sweep alpha in {0.0, 0.25, 0.5, 1.0}
- Measure: transfer F1 / scratch F1 ratio at 5pct IMDB data (the contractual measurement from PP-409)
- 3 seeds; pre-reg locked

Pre-reg:
- **HARD-PASS** rule: NONE of the 4 alpha points show HARD-FAIL (ratio < 0.95) AND sweet spot is identified (peak alpha shows ratio >= 1.20 = HARD-PASS bar)
- Convergence prediction (mechanism-informed): peak at alpha ~ 0.25 (structural similarity primary for analogy)
- **MIDDLE**: sweet spot identified but in MIDDLE band 0.95-1.20 ratio
- **HARD-FAIL** rule: SOME alpha shows HARD-FAIL ratio < 0.95 (two-vector architecture doesn't generalize to analogy)

Cost ~3-4 hr CPU.

### Capability 3: RETRIEVAL (PP-401 qa_self_knowing A-axis)

Hypothesis: alpha sweet spot is at or above 0.5 because A-axis "which capability implements X" needs ATOM IDENTITY recovery (specific atom retrieval).

Setup:
- qa_self_knowing A-axis benchmark (12 A questions from Cycle 49 benchmark v3)
- Substrate's algebra-HRR + UNION strategy + bge-name with alpha-augmented atom-identity
- Sweep alpha in {0.0, 0.25, 0.5, 1.0}
- Measure: A axis macro F1 at each alpha point
- 3 seeds; pre-reg locked

Pre-reg:
- **HARD-PASS** rule: NONE of the 4 alpha points show HARD-FAIL (A axis < 0.413 bge baseline) AND alpha=0.5 shows A axis >= 0.446 (matches Cycle 49 UNION lift)
- Convergence prediction: peak at alpha ~ 0.5 to 0.75 (identity recovery primary)
- **MIDDLE**: sweet spot identified in 0.413-0.446 range
- **HARD-FAIL** rule: alpha=0.5 shows A axis < 0.413 (two-vector architecture doesn't generalize to A axis retrieval)

Cost ~1-2 hr GPU (re-runs benchmark v3 with alpha-augmented index).

### Cross-capability convergence pre-reg

- **2nd APPEARANCE** rule confirmation: BINDING capability HARD-PASS at higher F (rule survives scaling within capability)
- **3rd APPEARANCE** rule CONFIRMED: ANALOGY + RETRIEVAL both show "NONE HARD-FAIL at alpha=0.5 + sweet spot identified" (rule generalizes ACROSS capabilities)
- 4th appearance optional next cycle

## Mechanism prediction (substrate-product positioning)

If predictions hold:
- BINDING peaks at alpha=0.5 (balanced structural-similarity + identity recovery)
- ANALOGY peaks at alpha ~ 0.25 (structural-similarity primary; shared math-primitive axis carries transfer)
- RETRIEVAL peaks at alpha >= 0.5 (identity recovery primary; specific atom retrieval)

This task-dependent sweet spot would EMPIRICALLY VALIDATE the two-vector architectural separation:
- Plain algebra-HRR (alpha=0) is correct for STRUCTURAL SIMILARITY jobs (analogy / classification / SHARES_MATH discovery)
- Identity-augmented (alpha=0.5-1.0) is correct for ATOM IDENTITY jobs (cleanup / specific atom retrieval / decomposition)
- Task selects the alpha; rule provides the mechanism

LLM differentiator: LLMs CONFLATE these two jobs (single attention vector serves both poorly). Substrate can DECOUPLE via alpha-tuning per task.

## Pre-reg honest scope

- Substrate-quality-first frame; no LLM comparison required for rule promotion (the 3-capability convergence is the substrate-product artifact)
- Optional LLM reference frame: at high-data settings, LLM-fine-tune likely matches substrate at peak alpha within each task; substrate-product positioning is LOW-DATA + ARCHITECTURAL DECOUPLING win
- 9th methodology rule applies: literature/drill PRIORS may refine my mechanism prediction; empirical wins

## Routing

**Exp-Dev**:
- Cell 1 BINDING extension PP-406 alpha sweep at F={1,3,10,20} x alpha={0.0,0.25,0.5,1.0} x 3 seeds; cleanup@1 metric; ~2-3 hr CPU
- Cell 2 ANALOGY PP-409 alpha sweep at alpha={0.0,0.25,0.5,1.0} x 3 seeds; transfer F1 ratio @ 5pct IMDB; ~3-4 hr CPU
- Cell 3 RETRIEVAL PP-401 alpha sweep at alpha={0.0,0.25,0.5,1.0} x 3 seeds; A axis macro F1 on benchmark v3; ~1-2 hr GPU
- All 3 cells parallelizable across CPU+GPU lanes
- Verdicts to Research; dispatch verdict_handler per discipline

**Testbed**:
- Two-vector architecture PP-410 production deployment (per existing routing file strategy_request_to_testbed_2026-06-12_two_vector_architecture_PP410_deployment_alpha_0.5_identity_augmented.md)
- Continue Phase-2-light substrate-guided proposal tool build
- L1 + Q35 + Cell 2 v3 + UNION B+C ship

**Research**:
- This drill design routing
- Standing for 3-cell alpha sweep verdicts via verdict_handler discipline
- Free-probability drill foundation cell candidate queued for dispatch when verdict_handler queue clears (next-drill F5 R-transform on clustered codebook per multiple subagent suggestions)

## Cross-references

- strategy_request_to_research_2026-06-12_two_vector_architecture_rule_2nd_appearance_cross_axis_alpha_sweep_design.md (Research routing request)
- strategy_request_to_testbed_2026-06-12_two_vector_architecture_PP410_deployment_alpha_0.5_identity_augmented.md (Testbed deployment routing)
- strategy_request_to_exp_dev_2026-06-12_PP407_alpha_0.5_verification_cell_resonator_decomposition.md (Exp-Dev verification routing)
- USER SHARES_MATH memory (two-level clustering math-primitive vs corpus-encoding)
- PP-406 / PP-407 / PP-408 / PP-409 / PP-410 (Cycle 49 cap_map progression)
- meta::RULE_clustered_codebook_decode_ceiling_mitigation_is_encoding_not_rerank (CONFIRMED v588)
- meta::RULE_clustering_is_intentional_design_feature (CONFIRMED v588)

---

**Exp-Dev:** cross-axis alpha-sweep drill design 3-capability rule_two_vector_architecture promotion 1st->2nd->3rd CONFIRMED via 1st capability (BINDING extension F=10/20) + 2nd (ANALOGY PP-409 cross-domain transfer alpha sweep) + 3rd (RETRIEVAL PP-401 qa_self_knowing A-axis alpha sweep) + sweep alpha={0.0,0.25,0.5,1.0} per capability + mechanism-informed peak predictions BINDING=0.5 ANALOGY=0.25 structural-similarity-heavy RETRIEVAL>=0.5 identity-heavy + cross-capability convergence pre-reg ALL 3 NONE HARD-FAIL at alpha=0.5 + task-dependent peaks confirms 3rd APPEARANCE + LLM differentiator substrate DECOUPLES structural-similarity from atom-identity via alpha-tuning + ~6-12 hr total CPU+GPU + verdict_handler dispatch per cell + Cells D+E Phase-2-light gated + free-prob F5 next-drill candidate queued + USER full-auto continuing.
