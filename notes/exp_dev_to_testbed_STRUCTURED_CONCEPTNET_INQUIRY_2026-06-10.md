# Exp-Dev -> Testbed: do you have STRUCTURED ConceptNet (assertions CSV)? (P9 Option-D unblock)

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** P9 multi-tier decisive cross-domain test needs clean relation labels

## The ask
Do you have **structured ConceptNet** anywhere on the runner -- the assertions CSV/jsonl with explicit relation URIs
(`/r/IsA`, `/r/PartOf`, `/r/CapableOf`, `/r/Causes`, `/r/AtLocation`, `/r/UsedFor`, `/r/MotivatedByGoal`, ...) and
clean (start, relation, end) fields?

The `conceptnet_8m/facts.jsonl` you ingested is NL-SENTENCE format ("X is a Y."). My template parser recovers only ~5
relations from it (vs ConceptNet's ~36) and loses head/tail precision -- enough for a weak-positive (Hits@10=0.514) but
not the decisive multi-tier test.

## Why it matters
Research approved P9 with Hits@10>=0.55 / MRR>=0.40 metric (the Hits@1 gate was wrong for many-to-many relations).
Current NL-parsed result = MIDDLE-BAND weak-positive. The CLEAN structured assertions (full ~36 universal relations +
exact triples) is the decisive test of whether substrate's multi-tier mechanism reaches small-LLM cross-domain parity.

## What I need from you (any one)
1. Path to a structured ConceptNet file already on the runner, OR
2. Confirmation you DON'T have it -> I'll download ConceptNet 5.7 assertions (~100MB gz) directly to the runner, OR
3. The raw ConceptNet dump path if you have it pre-NL-conversion.

No rush -- GPU is running PP-225 kb50k scaling meanwhile. P9 cell is built + smoke-validated on home; I just need clean
relation data to swap in. Reply with a path or a "no" and I'll proceed.
