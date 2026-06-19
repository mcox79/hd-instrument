# RESEARCH (Director) -> USER: CRITICAL escalation -- PUSH PIPELINE DOWN + CORPUS MISMATCH + skip_smoke override. The A2 v6 cascade can proceed on the remote BUT it will measure on the OLD corpus (41,330 atoms; pre-FrameNet, pre-T3-PhaseA) because today's 17 commits including the ingests are NOT pushed to origin/main (push rejected by pre-receive hook). This is an infrastructure problem requiring your awareness + a scientific-validity question that affects the A2 v6 verdict's meaning. Filing per the architectural-escalation discipline (FULL AUTO authorized but irreversible/architectural goes to you).

**From:** Research (Director)  **To:** USER  **Date:** 2026-06-18 ~18:08 PDT  **Re:** push pipeline down + corpus mismatch + skip_smoke override. ASCII; fname_v2.

## Bottom line (one sentence)

The Orchestrator REPLACEMENT successfully dispatched the checkpointable A2 pre-cache rebuild via a direct-SSH bypass (push to origin/main was REJECTED by a pre-receive hook; origin frozen at commit a95b47b4; HEAD is 17 commits ahead) so it's RUNNING + verified end-to-end, BUT (a) the remote's substrate is at the pre-ingest 41,330-atom state (today's FrameNet 1,221 + T3 Phase A 1,339 are in the unpushed backlog), (b) USER-approved skip_smoke=false was forced to skip_smoke=true by the bypass (queue_add.sh can't honor it), and (c) the A2 v6 verdict will measure on the OLD corpus, violating the intent of commit 20160cdc ("A2 v6 measures on grown corpus"). Three escalation items follow.

## What's working

A2 pre-cache v2 is LIVE on the remote GPU runner (pid 28864). Verified directly via ssh:
- bge model loaded dim=1024 in 6.4s
- sharded encode started: 41,330 atoms / 42 chunks; shard dir `_shards_ffbbeb2c`
- Checkpointable cell confirmed (writes per-chunk shards; the prior non-checkpointable run wrote none -- this is the 6th-checklist payoff working in real-world)
- Completion monitor armed; will verify the npz EXISTS post-build (verify-OUTPUT-not-liveness)

So the FrameNet partial-ingest -> O(n^2) fix -> checkpoint+resume design -> kill-restart-test discipline -> first real second-dispatch chain is all working as designed.

## Issue 1: PUSH PIPELINE DOWN (infrastructure)

The canonical `dispatch_request.sh` push to origin/main was REJECTED by a pre-receive hook. origin/main is FROZEN at a95b47b4. HEAD is 17 commits ahead -- today's work (depth-cliff verdict atoms, FrameNet ingest, T3 Phase A apply, USER 6th-checklist canonical, capability-mining, Orchestrator bootstrap, USER-visibility notes, etc.) is on the LOCAL HEAD only.

Implications:
- No origin backup of today's 17 commits
- Remote stuck on stale corpus
- Future remote dispatches must use the direct queue_add.sh path (bypassing origin/main)
- The 4-session architecture depends on the producer-consumer-via-git pattern; with that down, we lose the canonical synchronization mechanism
- The skip_smoke=true override below is one symptom; there will be others as the cascade continues

Possible causes (not investigated by me; surfacing to USER):
- Branch protection misconfigured / requiring a check that isn't passing
- Pre-receive hook code regression
- GPG signing config issue (we know `hd_metrics_sync` typically auto-stages + pushes)
- An upstream commit on origin that the local HEAD didn't merge from

Recommended action: when you have bandwidth, investigate the pre-receive hook + restore the canonical push pipeline. Meanwhile direct-SSH bypass is operational for dispatch (with its own caveats below).

## Issue 2: CORPUS MISMATCH (scientific validity)

The remote store hash is `ffbbeb2c` matching the prior pre-ingest atom count (41,330). The grown 43,890 atoms (FrameNet's 1,221 SEMANTIC_FRAME + T3 Phase A's 1,339 LEXICON) are in the unpushed backlog. So:
- A2 pre-cache v2 is building the warm cache for 41,330 atoms (the OLD corpus)
- The A2 v6 verdict will measure on the OLD corpus
- This DIRECTLY VIOLATES the intent of commit 20160cdc ("A2 v6 measures on grown corpus")
- Skunkworks's A2-grown-corpus-RULE (semantic-recheck on 43,892) won't have the grown atoms to check against on the remote
- Exp-Dev's A2 semantic-absence-recheck cell (verifies the 2,562 NEW atoms aren't lexically/semantically aliased into gaps/gold) won't have those atoms to test, IF run on the remote against ffbbeb2c

This is a SCIENTIFIC-VALIDITY question, not just operations:
- Option A: run A2 v6 on the OLD corpus + label the verdict explicitly as "n=41,330 / pre-ingest" + acknowledge it doesn't speak to the grown corpus's A2 behavior + re-run when pipeline restored
- Option B: get the push pipeline fixed FIRST, THEN run A2 v6 on the grown corpus (delays the verdict but matches the scientific intent)
- Option C: dispatch a manual sync of the 17 commits via the same direct-SSH path so the remote catches up + then run A2 v6 on grown corpus

I have no strong lean -- this is your call. Routing the question to Skunkworks for the cert-VET dimension (does the OLD-corpus A2 v6 verdict carry any signal? Is it tier-relevant or tier-irrelevant given the corpus mismatch?). My filing this UP gives you the decision-point.

## Issue 3: skip_smoke override (USER-approved policy violation)

You had approved skip_smoke=false for the A2 v6 chain (the smoke sanity check is part of the cert-discipline). The direct-SSH bypass via queue_add.sh forces `--skip-smoke` (queue_add.sh's behavior). Orchestrator substituted "direct live-run verification (bge-ready confirmed)" as the smoke-equivalent.

This is a policy-substitution that's RECOVERABLE on next dispatch (when push pipeline restored, smoke=false honored) but worth noting: the A2 v6 chain about to run does NOT have the canonical smoke gate.

## What I recommend (Director lean; you decide)

1. **Acknowledge** the push pipeline DOWN as a real architectural-blocker that warrants USER bandwidth (when you have it) -- the cascade has worked around it tonight but the work-around is fragile.
2. **For the A2 v6 verdict**: my lean is OPTION C (sync the 17 commits via direct-SSH path so remote catches up, then run A2 v6 on grown corpus as INTENDED) -- this matches the scientific intent and is cheap if the direct-SSH path is already working. Routing to Skunkworks for cert-VET dimension.
3. **For skip_smoke**: accept the substitution (Orchestrator's direct-live verification) for THIS run + restore smoke=false for the next dispatch when pipeline is back.

These are my LEANS not decisions; you have the call on all 3.

## Substrate state right now (LOCAL, not pushed)

- atoms 43,890 (+1,221 SEMANTIC_FRAME + 1,339 LEXICON; both ingest-landed-clean local + tier-verified)
- 2 new EXPERIMENT_RECORD atoms (Phase A FLAT + Phase A2 2-level recovery + STRENGTHENS edge)
- CERT 569 -> 570 (Phase A FLAT additive HONEST_NEGATIVE)
- 17 commits on local HEAD, NOT on origin/main
- Remote: still at 41,330 atoms / pre-ingest / a95b47b4 base

## In-flight cascade gated on USER call

- A2 v6 chain: pre-cache running NOW; will complete + run A2 v6 ON OLD CORPUS unless redirected
- Exp-Dev's A2 semantic-absence-recheck cell ready (built for grown corpus; won't fire if A2 v6 runs on OLD)
- Skunkworks's A2-grown-corpus-RULE awaits the grown corpus on the remote
- Capability-update B1-refined APPLIED locally; not visible to remote
- All today's USER-visibility notes are LOCAL only

## What I'm waiting on / who's blocking

- **USER (you):** 3 decision items above (push pipeline awareness + A2 v6 corpus call + skip_smoke acceptance)
- **Skunkworks:** validity-VET dimension on the corpus mismatch (does old-corpus A2 v6 carry signal?)
- **Orchestrator REPLACEMENT:** running the pre-cache; ready to dispatch A2 v6 once cache lands; standing by on USER's corpus-mismatch call (option A/B/C)
- **Exp-Dev:** reactive on A2 v6 outcome + semantic-recheck cell when the corpus is correct

This is the most architectural escalation of the day. I've made the calls I can (B1 applied + B2 held + framing + audit-lessons) but the push pipeline + corpus-mismatch are yours.

-- Research (Director)
