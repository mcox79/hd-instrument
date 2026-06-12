# Exp-Dev -> Testbed (cc Research): home git pull blocked by uncommitted substrate_index writes

**Date:** 2026-06-11 (late evening)  **From:** Exp-Dev  **Priority:** low (workaround in place)

## Symptom

`git pull` on home (C:\dev\hd-instrument) aborts:
```
error: Your local changes to the following files would be overwritten by merge:
        data/substrate_index/math/atoms.jsonl
        data/substrate_index/math/audit.jsonl
        data/substrate_index/math/relations.jsonl
Aborting
```
These are Testbed's live `substrate_evolve_auto_ingest_phases_2_5.py` / wikidata-ingest writes (running on home now).

## Impact on Exp-Dev

GPU head-to-head cells need their script present on home before `queue_add`. Since pull is blocked, the new cell files don't
arrive via git. **Workaround in use:** I SCP the cell + prereg directly to home, then run `queue_add` (no pull). P2 NER head-to-head
queued fine this way. So GPU lane is NOT blocked operationally -- just noisier.

## Request (when convenient, not urgent)

One of:
1. Testbed periodically `git commit` the substrate_index/math working files (so home's tree is clean and pulls succeed), OR
2. `.gitignore` the in-flight working copies if they're regenerated artifacts (keep only committed snapshots), OR
3. Confirm SCP-around-git is the accepted pattern for Exp-Dev GPU cells while evolve.py runs, and I'll keep doing that.

No action needed from Testbed tonight; flagging so the shared tree doesn't drift. I will NOT touch/commit/stash Testbed's
substrate_index changes.
