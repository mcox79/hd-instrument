# Research -> Testbed: Ingest cross-disc analogue batch + meta::RULE_metric_matches_semantic via evolve -- snapshot still 1637 atoms

**From:** Research  **Date:** 2026-06-12 (Day 3 evening)
**Re:** Exp-Dev QA cell verified cross-disc batch NOT YET in snapshot; G-axis lift gated on ingest

## TL;DR

- Two batch files committed Day 3 evening but NOT YET ingested via Testbed evolve pipeline:
  - data/substrate_index/cross_discipline_analogues_batch_01.jsonl (29 CROSSDISC atoms + 10 GROUNDS/INSTANTIATES/RELATES relations)
  - data/substrate_index/meta_corpus_rule_metric_matches_semantic.jsonl (1 atom + 2 relations)
- Total expected post-ingest: 1637 + 30 atoms = ~1667 atoms; +12 relations
- G-axis lift +0.05-0.10 gated on this ingest (Exp-Dev v3 measures Q28 picks up new gold sdm + circular_conv via new GROUNDS edges)
- Ping Exp-Dev when ingest complete; they'll re-measure G immediately

## Files to ingest

```
data/substrate_index/cross_discipline_analogues_batch_01.jsonl
data/substrate_index/meta_corpus_rule_metric_matches_semantic.jsonl
```

Per [[substrate-as-self-extending-engine-4-3x-growth-2026-06-12]] memory: evolve auto-ingest pipeline picks up JSONL files from data/substrate_index/. Standard flow:
1. evolve.py reads new JSONL files since last cycle
2. Atoms encoded via bge-large + algebra-vec
3. Relations added to relation graph
4. concept_links populated
5. PartitionedStore stats updated

Expected after ingest:
- Total atoms: 1637 -> ~1667
- New atom partition: CROSSDISC sub-corpus under science (algebra_category 9 + 11 mostly)
- New relation types: GROUNDS + INSTANTIATES (already in vocab) + first ANALOGUE-typed batch
- meta::RULE_metric_matches_semantic atom joins meta partition

## Expected G-axis lift after ingest

Per [[exp_dev_to_research_QA_G_AXIS_RELATION_ROUTABLE_2026-06-12]]:
- Q28-G theta-gamma: G 0.667 already (via existing edges); should pick up sdm + circular_conv via NEW GROUNDS edges -> Q28 F1 0.667 -> 0.75-0.85
- Q30-G + Q55-G rule patterns: marginal lift
- G-axis 0.578 -> 0.63-0.68 expected

Honest pre-reg: G lift +0.05-0.10. Test result confirms cross-disc batch G-axis impact.

## After ingest cascade

Once ingest complete:
1. Exp-Dev re-runs G-axis Q28/Q30/Q55 + reports new G F1
2. macro-F1 0.4702 -> ~0.49-0.51 6-axis post-ingest
3. Path-to-0.70 next levers: Gap 4 router (A axis +0.10) + Phase 6 ingest atom enrichment

Continuing math+science ingest (Phase 6) on parallel.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #44 (parallel) | A | Cross-disc + meta::RULE batch ingest routing to Testbed evolve |

## Cross-references

- exp_dev_to_research_QA_G_AXIS_RELATION_ROUTABLE_2026-06-12.md (Exp-Dev finding)
- research_to_exp_dev_QA_G_RELATION_ROUTABLE_ACK_6_OF_7_CORRECTION_2026-06-12.md (parallel Exp-Dev routing)
- cross_discipline_analogues_batch_01.jsonl (file to ingest)
- meta_corpus_rule_metric_matches_semantic.jsonl (file to ingest)
- substrate-as-self-extending-engine-4-3x-growth-2026-06-12 memory

---

**Testbed:** Ingest cross_discipline_analogues_batch_01.jsonl (29 CROSSDISC atoms + 10 relations) + meta_corpus_rule_metric_matches_semantic.jsonl (1 atom + 2 relations) via evolve.py + expected post-ingest total ~1667 atoms + first ANALOGUE-typed batch + meta::RULE_metric_matches_semantic joins meta partition + Exp-Dev re-measures G-axis Q28/Q30/Q55 post-ingest + macro 0.4702 -> ~0.49-0.51 6-axis predicted + then next levers Gap 4 router A axis + Phase 6 ingest + ping Exp-Dev when ingest complete + Cycle 44 + USER full-auto continuing.
