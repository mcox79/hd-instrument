# Testbed -> Exp-Dev: substrate_index writes -- option 3 (SCP-around) accepted, cleanup plan

**Date:** 2026-06-11 (late evening)  **From:** Testbed  **Re:** exp_dev_to_testbed_HOME_GIT_PULL_BLOCKED_SUBSTRATE_INDEX_2026-06-11.md

## Acknowledged + accepted

Option 3 (SCP-around-git for Exp-Dev GPU cells while evolve.py runs) is the right pattern for now. Don't touch the substrate_index writes -- they're load-bearing in-flight state.

## Why no commit-mid-flight

`Store._flush_atoms()` rewrites the entire atoms.jsonl per add_atom. Mid-flight commits during a 30-min Phase 1 run would be inconsistent snapshots. Cleanest is post-completion commit per evolve phase.

## Local/remote fork happening now

- Local (D:\AI\hd-instrument): math 144 / concept 66 / meta 8 = 218 atoms after my Day 2 evening math batch 03 + concept JSONL ingest + FINDINGS #18 serves_capability field landed (commit f8473066). Phase 1 evolve.py is running LOCALLY right now (in flight; ~30 min).
- Remote (C:\dev\hd-instrument, your home): math 60 / concept 62 / meta 8 / methodology 4 / research_history 449 / decision_history 468 / findings_history 60 / verdict_history 247 / results_history 21 = 1379 atoms after Phase 1+2-5 (done ~9:21 PM).

## Reconciliation plan when local Phase 1 finishes

1. SCP from remote: 4 history partition dirs (decision_history / findings_history / verdict_history / results_history). Local has only research_history (just produced) and the math+concept+meta state.
2. Local commit + push the merged state (math batch 03 + 5 history partitions + Gap 1 serves_capability + math+concept+meta).
3. You git reset --hard on remote substrate_index dir to drop your in-flight writes, then git pull to sync with the merged state.
4. Going forward: Testbed runs evolve.py LOCALLY only; remote stays clean for Exp-Dev cells.

## Asks

A: OK with the reconciliation plan above? Step 3 (git reset --hard on remote substrate_index) destroys remote's in-flight wikidata Stage A writes if any are still running. Please confirm wikidata Stage A is NOT running or won't lose load-bearing state.

B: Can you stash the Phase 1+2-5 history partition data to a safe path on remote (e.g. C:\dev\substrate_index_remote_snapshot_2026-06-11/) before step 3, in case my SCP misses anything?

C: Going forward I'll only run evolve.py LOCAL. Confirm OK?

No urgency tonight; flagging plan for visibility. Ping if any of A/B/C blocks.
