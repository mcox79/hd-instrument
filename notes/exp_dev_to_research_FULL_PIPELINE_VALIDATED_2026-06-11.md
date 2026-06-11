# Exp-Dev -> Research: FULL substrate-NL pipeline validated piece-by-piece; Phase-4 integration is the only open question

## Every pipeline stage now PASSES individually (substrate-only)
| Stage | Mechanism | Result | Tested on |
|---|---|---|---|
| Phase 1 Extraction | slot-filling (HMM+context) + intent (NB) | slot-F1 0.87 / intent 0.85 (Tier A) | ATIS gold |
| Phase 2 Schema retrieval | substrate cleanup over Tier-2 schema bundles | 0.967 (RT-1) | 20-schema representative |
| Phase 3 Reasoning routing | substrate-as-classifier over 6 reasoning classes | routing 0.967 / answer 0.892 | Drill-B oracle |
| Reasoning primitives | PP-343/348/360/291/307/275 | 0.9-1.0 | validated |

The substrate-only NL->structure->reason->solve PIPELINE ARCHITECTURE is validated component-by-component. dep-parser SKIPPED
(slot-filling 0.87 >= 0.85). Two new Tier-A NL capabilities this session (POS tagging, intent classification).

## The single open question: PHASE 4 end-to-end integration on REAL NOISY TEXT
Every stage passes on gold/clean/representative inputs. The honest gap (my word-problem gate, acc 0.023): do the stages
COMPOSE on real messy text? Real hendrycks MATH / HumanEval inputs are noisy (the routing/schema signatures are embedded in
messy NL, not clean keyword lists). Phase 4 (~1 day) is the genuine test: run real MATH level-1 + HumanEval-LIGHT through
extraction -> schema -> routing -> primitive end-to-end. Target: MATH level-1 accuracy >= 0.20, HumanEval-LIGHT pass@1 >= 0.30.

This is the decisive integration: if the validated pieces compose on real text, substrate-only math/code SOLVING is grounded;
if the 0.023 gap persists end-to-end, the composition on noisy real input is the genuine boundary (where LLM front-end may help).

## Recommendation
Phase 4 integration is the next substantial build (~1 day). I've validated all the pieces; the composition on real text is
the remaining question. Building Phase 4 next as a focused effort. RT-1 caveat: representative 20-schema subset; full 114 +
real text would need the 2-stage domain-route-then-schema refinement.

## Cross-ref (this session's pipeline notes)
- slot-filling skip-dep-parser: SLOT_FILLING_085_SKIP_DEPPARSER
- intent Tier A: INTENT_TIER_A_PLUS_V2_SUPERSEDES
- routing oracle: REASONING_ROUTING_PASS
- RT-1: data/exp_schema_retrieval_rt1_cpu_v1/metrics.json
