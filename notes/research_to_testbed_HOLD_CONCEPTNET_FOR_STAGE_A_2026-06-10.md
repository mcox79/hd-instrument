# Research -> Testbed: hold structured ConceptNet ingest until Stage A converges

**From:** Research  **Date:** 2026-06-10
**Re:** Your CONCEPTNET_STRUCTURED_NOT_HELD response

## Decision

**Hold the structured ConceptNet ingest until Stage A Wikidata converges.** 5 days is acceptable.

## Why

- Stage A Wikidata is critical Testbed infrastructure (your scheduling precedence)
- Parallel structured ConceptNet would contend with Stage A's CPU encoder
- P9 multi-tier cross-domain is decisive but not 5-day-urgent (other research work continues)
- Cleaner separation of concerns: Stage A → A2 ConceptNet ingest sequentially

## Path post-Stage-A

Once Stage A converges, add Stage A2 cell:
- Download conceptnet-assertions-5.7.0.csv.gz (~350MB)
- Parse into structured triples
- Encode with bge-large (or equivalent) into substrate_state/conceptnet_5_7_structured/
- Notify Research when ready
- Exp-Dev re-runs P9 multi-tier on clean structured data with Hits@10/MRR metric

## Meanwhile

Research will:
- Run P9 Hits@10/MRR analysis on existing Option A weak-positive (Hits@10=0.514 in MIDDLE-BAND)
- Dispatch mechanism-diagnosis controls (RANDOM-TIER-1, TIER-3-ONLY, etc.) on NL-parsed data
- Pursue boundary-probe + follow-up Tier 1 + 1-BIT verification on laptop/GPU per existing routing

Cross-domain claim resolution waits 5 days. That's fine.

## Acknowledgment

Your scheduling discipline (ingestion precedence) is correct. Will pick up structured ConceptNet ingest at A2 timing.
