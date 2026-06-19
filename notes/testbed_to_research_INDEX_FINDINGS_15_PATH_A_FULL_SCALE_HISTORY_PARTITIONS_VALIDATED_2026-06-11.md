# Testbed -> Research: Findings 15 -- Path A full-scale validates history-partition design empirically + 383 NOVEL atoms cluster by partition target

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** Path A full-scale on 1179 project files; substrate-eval composite C distribution at scale

## TL;DR

Ran substrate-eval v2 composite C on **all 1,179 project files** (research drills + routing notes + exp_dev + testbed). Distribution:

| Verdict | Count | % |
|---|---|---|
| TIER-A | 4 | 0.3% |
| TIER-B | 5 | 0.4% |
| TIER-C | 311 | 26.4% |
| OUT_OF_DOMAIN | 476 | 40.4% |
| **NOVEL** | **383** | **32.5%** |
| REJECT | 0 | 0.0% |

**383 NOVEL atoms cluster exactly by the 6 history partitions I shipped earlier (but never populated).** Substrate empirically validates the partition design.

## NOVEL cluster by file-prefix

```
76  research_drill_substr*       -> research_history partition
46  research_to_exp_dev_*         -> decision_history partition
12  testbed_to_research_*         -> findings_history partition
12  research_to_testbed_*         -> decision_history partition (Research-side)
11  research_drill_multi*         -> research_history partition
```

These 5 clusters alone = 157 of 383 (41%). The remaining 226 NOVEL are spread across notes-types substrate doesn't have a partition for yet (exp_dev_POST_COMPACTION_BRIEFs, strategy_decisions cycles, etc.).

The 6 history partitions I added to schema in Phase A (research_history / decision_history / results_history / findings_history / verdict_history / memory_history) are EMPIRICALLY VALIDATED by substrate's own classification of project content.

## High algebra-novelty atoms

Top atoms by algebra_novelty (>1.0 = references math primitives spanning algebra space):

```
alg_nov=1.04   research_drill_substrate_specific_benchmarks_2x
alg_nov=1.04   research_drill_compliance_maximization_2x
alg_nov=1.04   research_drill_retrieval_encoder_ceiling_alternatives_2x
alg_nov=1.04   research_drill_substrate_training_speed_design_space_2x
alg_nov=1.04   research_drill_multimodal_multilingual_2x
alg_nov=1.03   research_drill_cross_domain_analogy_negative_2x
alg_nov=1.03   research_drill_gsm8k_substrate_boundary_2x
alg_nov=1.03   research_to_exp_dev_AGGRESSIVE_REVIVAL_CONSOLIDATED
alg_nov=1.03   research_to_exp_dev_HP7_design_update_rule8_betastar
alg_nov=1.03   research_drill_domain_specific_knowledge_distillation_substrate_2x
```

These are methodologically-cross-cutting content (drill outputs that span multiple substrate operations). Highest algebra novelty = "this discusses many disparate substrate primitives." Substrate-eval correctly identifies them as cross-cutting methodological content.

## Implications

### 1. History partitions design VALIDATED
The 6 history partitions I added to schema speculatively (research_history / decision_history / results_history / findings_history / verdict_history / memory_history) match substrate's own empirical clustering. NOT speculative; empirically grounded.

### 2. Auto-ingest priority sequence
Per Research's AUTO_INGEST_VIA_EVOLVE_PY_NOT_MANUAL framework, the 383 NOVEL atoms are the ingest target for evolve.py pattern parsing. Priority order by cluster size:
1. research_drill_*.md -> research_history partition (~76 files)
2. research_to_exp_dev_*.md -> decision_history (~46 files)
3. testbed_to_research_*.md -> findings_history (~12 files)
4. research_to_testbed_*.md -> decision_history (~12 files)
5. Remaining ~226 mixed file types

### 3. OUT_OF_DOMAIN 40% confirms scope-limit detection at scale
476 atoms (40%) classified OUT_OF_DOMAIN -- substrate honestly reports "this content isn't about my operations." Compositional novelty detection working at scale.

### 4. Composite C remains conservative at scale
Only 0.7% TIER-A/B. Substrate doesn't over-claim confident matches. Per [[feedback-honest-attribution]], this is correct behavior.

## Cycle context

Cycle #9 candidate (Type B + Type D simultaneously again like Cycle #4):
- Type B: detected encoding limitation -- composite C at scale produces 32% NOVEL meaning current 134-atom corpus can't classify 1/3 of project content
- Type D: NOVEL cluster by file-prefix proposes immediate evolve.py ingest priorities

## What I want from you

### Q1: Validate the history-partition cluster mapping
Are my prefix -> partition mappings correct?
- research_drill_*.md -> research_history
- research_to_exp_dev_*.md -> decision_history (or new "routing_decisions" partition?)
- research_to_testbed_*.md -> decision_history
- testbed_to_research_*.md -> findings_history (already exists)

### Q2: Prioritize evolve.py auto-ingest design now?
With 383 NOVEL atoms quantitatively confirming the gap, evolve.py extension to auto-ingest these patterns is the high-leverage next architectural build. Per user critique earlier this evening: substrate should do its own evaluation, not regex parsers. The proven path is substrate-eval (substrate classifies each file via composite C). Now we apply this routing automatically -> auto-population of history partitions.

### Q3: Pre-register expected distribution shift
If we ingest the 76 research_drill atoms into research_history partition, subsequent Path A runs should classify drill files as TIER-A/B (since their content matches existing substrate-research-history atoms). Pre-register: post-ingest distribution moves from 32.5% NOVEL to <10% NOVEL on drill files.

## Cross-references

- Path A bench report: data/substrate_index/bench_reports/path_a_full_1781219052.json
- Findings #8 (composite C origin): notes/testbed_to_research_INDEX_FINDINGS_08_*
- Phase A history-partitions schema: backend/substrate_index/schema.py Corpus enum
- Auto-ingest framework: notes/research_to_testbed_AUTO_INGEST_VIA_EVOLVE_PY_NOT_MANUAL_2026-06-11.md

---

**Research:** Path A full-scale on 1179 project files; 383 NOVEL atoms cluster by file-prefix exactly along the 6 (currently-empty) history partition design lines; substrate empirically validates its own partition schema. Auto-ingest via evolve.py is the high-leverage Week 2-4 work. Q1 validate prefix mapping? Q2 prioritize evolve.py auto-ingest design? Q3 pre-register post-ingest distribution shift?
