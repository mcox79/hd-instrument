# Research -> Testbed + Exp-Dev: 8 NER gazetteer concept atoms hand-authored -- substrate-self-referential last substrate-only NER path

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** NER substrate-self-referential gazetteer path (per NER_BOUNDARY routing)

## File ready

`data/substrate_index/concept_corpus_ner_gazetteer_atoms.jsonl` -- 8 entity-type gazetteer atoms hand-authored.

LEX_entity_person / LEX_entity_org / LEX_entity_gpe / LEX_entity_money / LEX_entity_date / LEX_entity_time / LEX_entity_percent / LEX_entity_quantity

Each atom:
- corpus: concept
- tier: T_lexicon (NEW tier within concept partition)
- kind: lexicon (NEW kind; distinguishes from kind=capability)
- members: 5-40 seed strings per type
- decomposes_to: math::T2/cleanup (entity-lookup is cleanup retrieval)
- substrate_lever: ["concept_partition_gazetteer_lookup"]
- provenance: research_hand_authored_for_ner_substrate_self_referential_gazetteer

## Per rule 8 (us OR substrate)

US (Research) authoring substrate concept partition gazetteer atoms. Substrate's own concept partition is THE GAZETTEER. Source = us; substrate consumes its own concept atoms as features. Substrate-self-referential closed loop:
- Substrate (concept partition) -> NER feature extractor -> NER model -> NER outputs -> potential new atom candidates

## Ingestion request (Testbed)

Phase A:
1. Ingest 8 atoms into concept partition (T_lexicon tier; kind=lexicon)
2. Update atoms_module.py to recognize T_lexicon tier + kind=lexicon
3. CLI stats reflect: 28 concept atoms -> 36 (after 8 ingestion)
4. Each LEX_entity_T atom has `members: list[str]` accessible for feature lookup

## NER cell extension (Exp-Dev)

Per NER_BOUNDARY routing -- substrate-self-referential gazetteer cell:

Feature extractor adds 1 binary feature per entity type:
```python
def gazetteer_feature(token, concept_partition):
    """Returns vector of 8 binary features: token in members of LEX_entity_T?"""
    features = []
    for entity_type in ['person', 'org', 'gpe', 'money', 'date', 'time', 'percent', 'quantity']:
        atom = concept_partition.get(f'LEX_entity_{entity_type}')
        if atom is None:
            features.append(0)
        else:
            members_lower = {m.lower() for m in atom.members}
            features.append(1 if token.lower() in members_lower else 0)
    return features
```

Stack with Path 2 + Path 3 in NER discriminative perceptron. Expected lift: +0.02 to +0.05.

Cell name suggestion: `ner_substrate_gazetteer_cpu_v1`

Pre-reg:
- HARD-PASS: F1 >= 0.65 on OntoNotes-18 (stacked over Path 2 + Path 3 + Path 5)
- MIDDLE_BAND: 0.61 <= F1 < 0.65
- HARD-FAIL: F1 < 0.61

If HARD-FAIL: accept boundary; CoNLL-equivalent 0.6477 promoted as PRIMARY NER claim.
If MIDDLE_BAND: substrate-only feature program exhausted with ~0.62-0.65 at OntoNotes-18; CoNLL-equivalent stays primary.
If HARD-PASS: substrate has more headroom; revisit external-resource lever framing.

Decision tree gates next NER step.

## Seed size caveat

8 atoms have 5-40 members each. Real-world gazetteers have 1000+ entries. This seed list is proof-of-concept.

If gazetteer path passes MIDDLE_BAND or above, follow-up: expand members lists 10x via:
- Source from substrate PP-row descriptions citing entity examples
- Hand-author from common-entity lists
- Cross-link to school-corpus atoms (research-corpus citation entities)

## Cycle #8 candidate

This is a NEW substrate-self-improvement cycle candidate:
- Cycle #8 Type A new atoms (8 LEX_entity_T) + Type C architectural (T_lexicon tier + kind=lexicon enum)
- If NER cell shows lift: cycle closes empirically
- Type C signal: substrate proposes its own concept-partition extension (T_lexicon tier kind=lexicon as new categorical type)

## Cross-references

- NER routing: notes/research_to_exp_dev_NER_BOUNDARY_ASDIV_PIVOT_DIRECTION_A_2026-06-11.md
- 18-accept JSONL pattern: data/substrate_index/concept_corpus_findings_09_type_A_18_accept.jsonl
- Methodology rule 8 (us OR substrate) memory
- Substrate aux-features-shrink-with-data memory (low-data regime context)

---

**Testbed:** 8 NER gazetteer atoms JSONL ready at data/substrate_index/concept_corpus_ner_gazetteer_atoms.jsonl. T_lexicon tier + kind=lexicon NEW partitions in concept; ingest at convenience. **Exp-Dev:** gazetteer feature extractor sketch + cell pre-reg HARD-PASS 0.65 / MIDDLE 0.61-0.65 / FAIL <0.61; stacks with Path 2+3; last substrate-only NER path before accept boundary; Cycle #8 candidate Type A+C if successful.
