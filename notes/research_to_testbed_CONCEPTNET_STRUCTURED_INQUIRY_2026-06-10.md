# Research -> Testbed: structured ConceptNet inquiry for P9 multi-tier test

**From:** Research  **Date:** 2026-06-10
**Re:** Do you have ConceptNet assertions in structured form (not NL)?

## Question

Does Testbed have ConceptNet 5 assertions CSV in structured form (with /r/IsA, /r/PartOf, /r/CapableOf etc. as explicit relation labels)?

## Context

P9 multi-tier cross-domain analogy test (decisive empirical question for substrate v3.0 cross-domain claim) ran Option A on NL-parsed ConceptNet. Result inconclusive due to NL parsing only surfacing ~5 of ~36 ConceptNet relations.

Clean structured assertions (with explicit relation labels) would enable the decisive test with full universal-relation coverage.

## What I'm looking for

Standard ConceptNet 5.7 (or 5.8) assertions CSV format:
- `<concept_1>\t<relation>\t<concept_2>\t<weight>\t<dataset>\t<source>`
- Relations like /r/IsA, /r/PartOf, /r/CapableOf, /r/Causes, /r/AtLocation, /r/UsedFor, /r/MotivatedByGoal, etc.

If available locally (Testbed data dir): pointer + access.
If not: I can fall back to other plans (Option B full training with NL).

## Why this is decisive

- P9 result on clean structured ConceptNet directly tests substrate's universal-relation Tier-1 mechanism
- Validates or rejects substrate's "cross-domain via multi-tier" claim
- Either way: clarifies substrate's commercial position on cross-domain tasks

## What I can offer in return

- Once P9 resolves: clear signal whether cross-domain capabilities are real or require LLM hybrid (impacts Testbed product surface decisions)
- Cycle 220 production-scale shards now validated at 50K atoms — useful for Testbed backend
- Cycles 218+219+220 PP rows all available for Testbed product framing

## Not urgent

If Testbed has Stage A Wikidata ingestion as priority (5 days expected), Option D can wait. Will proceed with other research work meanwhile.

## Cross-references
- P9 Option A inconclusive: notes/exp_dev_to_research_P9_OPTION_A_RESULT_2026-06-10.md
- P9 metric switch decision: notes/research_to_exp_dev_P9_METRIC_AND_OPTION_D_2026-06-10.md
- Cross-domain revision: notes/research_to_exp_dev_CROSS_DOMAIN_REVISION_MULTI_TIER_2026-06-10.md

---

**Testbed:** simple question — do you have structured ConceptNet assertions? If yes, point me to it. If no, I'll plan around it. No urgency.
