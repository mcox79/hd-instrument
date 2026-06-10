# exp_dev hand-off -- research: cross-domain analogy negative 2x

**Filed:** 2026-06-10 by research sub-agent (Sonnet).

**Trigger:** STRETCH4-2 HARD_FAIL. RotatE-style learned relation geometry achieves 0.899 Hits@1 within-domain but only 0.244 cross-domain (10-shot, held-out relations). Research note diagnoses the mechanism failure and identifies 5 engineering anchors that address the gap. See notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md for full findings.

**Pause state:** Check data/orchestrator_paused.flag before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS and POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL implementation. Research provides only the WHAT and WHY -- not the HOW.

---

## Anchor candidates (rank-ordered; exp_dev picks across queues)

### 1. CONEPTNET-RELATION-DECOMPOSITION (cheapest decisive gate)
- Anchor pointer: notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md Level 4.7 + ANCHOR-3
- Substrate-product reading: ConceptNet's 34 universal relation types are already ingested (testbed pipeline, 458K facts). Encoding domain-specific relations as superpositions of ConceptNet types tests whether universal-vocabulary constraint improves cross-domain Hits@1 above the 0.244 baseline. If it does, the substrate has a direct path to cross-domain analogy via ConceptNet anchoring without GPU training.
- Tier hint: LOCAL CPU or REMOTE CPU (uses existing ConceptNet data, no re-training, 1-2 hours)
- Why now: cheapest test; uses already-available data; directly tests the lowest-cost cross-domain mechanism

### 2. STRUCTURAL-ALIGNMENT-CROSS-DOMAIN-ORACLE (upper-bound oracle)
- Anchor pointer: notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md Level 3.1 + ANCHOR-4
- Substrate-product reading: A minimal SME-style structural alignment between two schema-distinct KG subgraphs (pure Python) sets the empirical upper bound on cross-domain analogy accuracy. If structural alignment achieves 0.60+ where embedding arithmetic gives 0.244, this defines the performance ceiling and provides the justification for building a structural alignment layer as a product capability.
- Tier hint: LOCAL CPU (pure Python graph matching, no GPU, 1-2 hours)
- Why now: defines the feasibility ceiling before investing in ANCHOR-2 GPU training; if oracle < 0.40 the benchmark design is wrong

### 3. FEW-SHOT-KGE-META-LEARNER (direct mechanism fix)
- Anchor pointer: notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md Level 4.3 + ANCHOR-2
- Substrate-product reading: GMatching (Xiong et al. 2018) or FSRL trains a meta-learner that infers relation semantics from K example triples. Directly addresses the 10-shot failure mode. If Hits@1 from 10 shots reaches > 0.50 (vs 0.244 baseline), the few-shot path is the primary fix for cross-domain transfer.
- Tier hint: REMOTE GPU (6-12 hours; train meta-learner on FB15K-237 with held-out relations as meta-test)
- Why now: highest-impact fix if it works; should run AFTER anchors 1 and 2 confirm the structural alignment ceiling

### 4. MULTI-DOMAIN-KGE-TRAINING (highest-scale test)
- Anchor pointer: notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md Level 4.1 + ANCHOR-1
- Substrate-product reading: Training a single KGE model jointly on FB15K-237 + Wikidata5M-100K + ConceptNet-100K tests whether shared semantic content factorizes into shared geometry. Expected cross-domain improvement: 0.30-0.50 range. If it reaches 0.50, multi-domain training is sufficient; if it does not, the bottleneck is entity-geometry co-adaptation not data sparsity.
- Tier hint: REMOTE GPU (4-8 hours; requires entity alignment preprocessing)
- Why now: tests the highest-scale hypothesis but is also the most expensive; run after anchors 1-3 narrow the mechanism

### 5. RELTYPE-VECTOR-SEPARATION (substrate-native test)
- Anchor pointer: notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md Level 4.6 + ANCHOR-5
- Substrate-product reading: Modify the substrate encoding to keep relation-type vectors (universal primitives) separate from entity-instance binding. Tests whether analogy inference using relation-type vectors alone achieves better cross-domain transfer than full RotatE (0.244). This is the substrate-native implementation of the universal-primitive hypothesis -- directly testable in the HD computing framework without KGE training.
- Tier hint: LOCAL CPU or REMOTE CPU (2-4 hours; modifies substrate encoding layer, no GPU needed)
- Why now: tests cross-domain in the substrate's own architecture, not in an external KGE model; most directly informs whether the substrate's encoding can be extended to support cross-domain analogy

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_cross_domain_analogy_negative_2x_2026-06-10.md
- Within-domain baseline (0.899): data/exp_STRETCH4-2/metrics.json (or equivalent anchor path)
- ConceptNet data (458K facts): testbed pipeline output; see notes/testbed_post_compaction_brief_2026-06-09_overnight_chain.md
- Prior cross-domain round 5 (glass-phase + effective-interaction anchors): notes/research_drill_cross_domain_round5_2026-06-07.md
- Prior exp_dev handoff (round 5): notes/exp_dev_handoff_research_cross_domain_round5_2026-06-07.md
- Production recipe (locked): notes/orchestrator_post_compaction_brief.md
- Field advisor: tools/orchestrator/research_field_advisor.py

---

## Contract

exp_dev owns ALL implementation decisions: anchor names, N/M/K sweeps, seed counts, threshold bands, queue routing, ETA. Research provides only the WHAT and WHY -- not the HOW.

## Autonomy declaration

exp_dev may freely pick from the 5 anchors above in any order consistent with queue state and pause flag. Anchor 1 (ConceptNet decomposition) and Anchor 2 (structural alignment oracle) are recommended first because they are CPU-only and cheap. Anchor 3 (few-shot meta-learner) and Anchor 4 (multi-domain training) require GPU and should wait for the oracle to confirm the performance ceiling. Anchor 5 (reltype vector separation) is substrate-native and can run in parallel with any of the others.
