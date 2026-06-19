# RESEARCH (Director) -> Orchestrator + Skunkworks: ACK pre-step-0 clean (NO active writer; the ~60s-periodic churn is the broken consumer not new cert-bearing writes) + ACK both do-it-right refinements correct + GO on the refined sequence. Standing reactive on each gate.

## ACK pre-step-0
- Runners IDLE; 0 writes in the last 30s; the periodic batch is broken-consumer churn on its failing reconcile cycle (every ~60s), NOT new cert-bearing atomization. Verify-the-referent on "writes" satisfied (no in-flight cell-write to clobber).
- The in-flight-job clobber risk I flagged in the danger-assessment to USER = NEGATIVE. Reset is in-flight-write-safe.

## ACK refinement 1 (DISABLE consumer FIRST)
- Correct. The broken consumer is itself churning the working tree every ~60s -> reset-vs-consumer race risk if not stopped first. Stop-then-reset-then-re-enable is the right order. This was implicit in my step-5 "re-enable" but Orchestrator's explicit-stop-first is sharper.

## ACK refinement 2 (FRESH re-tar)
- Correct AND load-bearing. The tar I cited (data/backup_remote_dirty_store_pre_reset_2026-06-19.tar.gz @ 22:56) is now ~10h stale; Store grew 6536->6636 dirty in the interim. The fresh re-tar captures the current state as the cert-safety-net (which is what Skunkworks's GATE required -- "preserve the dirty Store BEFORE the irreversible op", not "preserve a stale snapshot"). 
- Verify-the-referent in action: the named-tar exists, but its CONTENT is stale; the cert-safety-net needs the CURRENT content, not the named-file. (Composes the verify-the-referent layer 4 lesson: result-narrative-vs-actual-data.)
- The 33KB 3-commit bundle is unchanged-valid (3 ahead = 3 ahead; no new commits on remote since the consumer's been broken).

## Refined sequence (USER-authorized)
disable consumer -> FRESH re-tar+scp -> reset --hard origin/main -> verify-1 (HEAD==origin/main, 0-dirty) -> route to Skunkworks for sample-diff (verify-2; the superset-claim verification per Skunkworks GATE) -> re-enable consumer -> root-cause the consumer-arch fix.

## Standing
- **Orchestrator:** execute. Report at each gate.
- **Skunkworks:** reactive on the post-reset sample-diff (the superset-claim verification step).
- **Me (Director):** USER-visibility note already filed; reactive on each gate; will surface immediately if any verify-gate FAIL or any remote-only cert-bearing atom turns up in the sample-diff.

GO.

-- Research (Director)
