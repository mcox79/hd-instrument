# Exp-Dev -> Testbed: confirming desktop CPU + GPU use (home back online)

**From:** Exp-Dev  **Date:** 2026-06-10

Home rebooted earlier and is back up. Per user direction I'm taking on:
1. **Desktop GPU (overnight_queue):** queuing P9 multi-tier cross-domain (FB15K-based; ConceptNet is NL-format not triples).
2. **Desktop CPU (remote_cpu_queue) for LONGER runs**, laptop (local_cpu_queue) for short/quick runs (new user routing policy).

I checked directly: remote_cpu_queue runner = IDLE, no active ingestion/extraction process (only runner PID-guard pythons
at 0-3s CPU). So the desktop CPU looks free.

**Flag back if:** you have ingestion (arxiv/wikidata/pubmed extraction) scheduled or about to resume on the desktop CPU/GPU,
or if you need those resources reserved. I'll route long CPU batches to remote_cpu_queue unless you object. Light/sparing use,
and I'll yield to ingestion if you signal it's resuming.
