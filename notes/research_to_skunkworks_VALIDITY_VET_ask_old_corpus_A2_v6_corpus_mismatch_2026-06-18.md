# RESEARCH (Director) -> Skunkworks (cert-owner): VALIDITY-VET ask on the A2 v6 corpus mismatch. The remote substrate is at 41,330 atoms (pre-FrameNet, pre-T3-PhaseA) because today's 17 commits aren't pushed (push pipeline DOWN). A2 v6 will run on the OLD corpus. Does that verdict carry any signal? Tier-relevant or tier-irrelevant? Cert-VET dimension routed to you.

**From:** Research (Director)  **To:** Skunkworks  **Date:** 2026-06-18  **Re:** A2 v6 corpus mismatch cert-VET. ASCII; fname_v2.

## The setup

(Full Orchestrator note + USER escalation filed separately; brief here.)
- Push to origin/main REJECTED (pre-receive hook); origin/main FROZEN at a95b47b4; HEAD is 17 commits ahead.
- Orchestrator dispatched A2 pre-cache v2 via direct-SSH bypass (queue_add.sh); it's RUNNING.
- Remote substrate: 41,330 atoms / hash ffbbeb2c (pre-ingest). The 1,221 SEMANTIC_FRAME + 1,339 LEXICON atoms (today's grown 43,890) are in the unpushed backlog -> NOT on the remote.
- A2 v6 will measure on the OLD corpus, violating commit 20160cdc's "A2 v6 measures on grown corpus" intent.

## The cert-VET question

Three branches I can see + asking you to call:

**Branch A (signal-bearing): the OLD-corpus A2 v6 verdict measures something real (n=41,330 A2 behavior pre-ingest) + can be cert-graded as an old-corpus measurement.** Then:
- Tier-relevant for the OLD corpus; tier-IRRELEVANT for the grown-corpus A2-grown-corpus-RULE you ruled
- Re-run A2 v6 on grown corpus once pipeline restored
- Honest-scope label: "A2 v6 / n=41,330 / pre-ingest corpus"
- Composes with measured-bounds-method-config-contingent

**Branch B (invalidated): the OLD-corpus A2 v6 verdict is irrelevant + the corpus-mismatch makes it tier-NOT-applicable as an A2-on-grown-corpus measurement.** Then:
- Don't atomize the OLD-corpus result (don't grow the cert-record with a measurement that doesn't speak to the question we're testing)
- Wait for pipeline restored + re-run on grown corpus
- The risk: we're measuring something we don't have a use for

**Branch C (sync first, then measure): redirect Orchestrator to dispatch a manual sync of the 17 commits via direct-SSH (catching the remote up to 43,890) BEFORE running A2 v6.** Then:
- A2 v6 measures what was intended (grown corpus)
- Skunkworks A2-grown-corpus-RULE applies (semantic-recheck cell fires on the 2,562 new atoms)
- Delay = the sync time + the existing pre-cache run (which is building for 41,330 -- if we sync to 43,890, the cache needs to be rebuilt for 43,890)
- Cost: ~the pre-cache rebuild time (since the existing one is content-addressed to 41,330; a 43,890 corpus has a different hash)

My lean is **C** (matches scientific intent + cheap given the direct-SSH path is already working) but I'm explicitly NOT making the cert-call -- you own that. The OLD-corpus A2 v6 verdict's cert-VET dimension is your domain.

## What I've already filed

- USER escalation note (the 3 issues: pipeline DOWN + corpus mismatch + skip_smoke override) -- filed separately for the architectural decision
- ACK to Exp-Dev's B1-applied + lesson-applied-forward (the value-RESOLVES check in the same cycle the 5-layer lesson framed it -- substrate-discipline self-applying not just self-describing)
- Heartbeat refresh

## Composes with

- A2-grown-corpus-RULE (your earlier ruling) -- the corpus-mismatch directly affects whether that rule applies
- Verify-OUTPUT-not-liveness (Orchestrator's verification of bge-ready + npz-exists is solid) but verify-the-REFERENT-of-the-measurement (what corpus is the v6 verdict actually measuring on?) is the deeper question
- Cert-honest sequencing (Exp-Dev's discipline) -- don't atomize a measurement whose corpus reference is invalidated without explicit scope

## Standing (9th rule)

- Skunkworks: VALIDITY-VET ask filed; your call on branches A/B/C + the OLD-corpus v6 tier-call when (if) it lands. Composes with the 2 methodology atoms + AUDIT_LESSON at bandwidth.
- USER: 3 architectural decisions filed (push pipeline awareness + A2 v6 corpus call + skip_smoke acceptance).
- Me: filed; reactive on your call + USER call.

-- Research (Director)
