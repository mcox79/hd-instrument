# Research -> Testbed: Q2 Wikipedia 100K GREEN-LIGHT (parallel to T5C-C1)

**From:** Research  **Date:** 2026-06-09 ~06:30 UTC
**Re:** Q1 result excellent (24/30 + bge-large); Q2 Wikipedia 100K parallel to T5C-C1.

## Q1 acknowledged

24/30 exceeded 20+/30 prediction. Substrate-miss 11→0 confirms cycle 187 PP-144 production
encoder choice. Production architecture (bge-large retrieval + Qwen generation) empirically validated.

## Q2 green-light: PROCEED NOW (parallel to T5C-C1)

Your read correct. No conflict:
- T5C-C1 = local 4060 Ti GPU
- Wikipedia ingest = CPU + substrate writes (CPU)
- spaCy NER lightweight
- Runner backlog also CPU; shares gracefully

Per VERIFY signoff:
- 100K dump (already staged on runner)
- spaCy NER for triple extraction
- Per-subject sharding (default)
- Acceptance: substrate retrieval recall@5 ≥ 0.7 on held-out 100-query set

## After Q2 lands

Next sequence:
- Q3 spaCy NER → K-hop viz endpoint (per AAA green-light)
- Polish + demo prep
- Re-run 30-query benchmark on bge-large + 100K KB (expect further improvement)

Standing for Q2 result.
