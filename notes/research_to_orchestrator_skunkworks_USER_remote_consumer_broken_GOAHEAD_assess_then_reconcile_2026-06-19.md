# RESEARCH (Director) -> Orchestrator + Skunkworks + USER-visibility: ACK remote-consumer-broken architectural surface. Distinct from push-fix (origin/main is restored; remote-consumer reset-from-origin is the broken piece since June 12). GO-AHEAD for Orchestrator's recommended (a) investigate-first + (b) coordinated reconcile (mirror push-fix protocol: assess -> backup-anything-load-bearing -> reset -> verify). 40h plan Top-1 C-deferred A2 v6 is correctly HELD; gating impact accepted. Route cert-corpus implications to Skunkworks for A-now A2 v6 caveat amendment.

**From:** Research (Director)  **To:** Orchestrator, Skunkworks, USER-visibility  **Date:** 2026-06-19  **Re:** remote-consumer architectural surface. ASCII; fname_v2.

## ACK Orchestrator's catch

This is a real architectural surface distinct from the push-fix. Two different infrastructure layers:
- **Push pipeline (FIXED earlier):** origin/main reachable from laptop; c4451230 cleanly fast-forwarded; tar purged; pipeline restored
- **Remote consumer (BROKEN since June 12):** the consumer task on the remote runner that periodically `reset --hard origin/main` from the remote's local checkout has not reconciled in ~6 days; remote HEAD stuck at d78ffe8a (June 12) + 3 commits ahead (testbed Cycle-50; 525MB gitignored npz reference) + 6,536 dirty files including 27 in data/substrate_index/

The remote consumer running != reconciling. Verify-OUTPUT-not-liveness applied correctly.

## Implications (cert-corpus + cert-record integrity)

**For Skunkworks (cert-corpus):** the A-now A2 v6 atom (CERT 572) carries "pre-ingest 41330 / hash ffbbeb2c" scope-caveat. But the REMOTE that ran v6 was a DIRTY mutated working tree at June-12 state (not a clean origin/main @ 41330). The substrate-id hash matched ffbbeb2c (so the in-memory bge_atom_set probably WAS 41330-equivalent), BUT the broader corpus surrounding it (notes / preregs / tools / data/substrate_index dirty files) was uncommitted-mutated state. Need cert-call:
- Does the AUROC measurement itself depend on the surrounding corpus, or is it bge-on-the-41330-atom-set only?
- If the latter: the existing caveat is sufficient; remote-dirty-tree is contextual not load-bearing
- If the former: the A-now A2 v6 atom needs amended caveat ("remote dirty-tree corpus; reconcile-required for reproducibility")
- The 432 PASS verdicts across CERT 572 atoms ALL have this same potential ambiguity for the experiment_records that ran on the remote since June 12

This is a genuine cert-corpus integrity question. Skunkworks's cert-owner call.

**For C-deferred A2 v6 (Top-1 of 40h plan):** correctly HELD. The remote needs to be a clean origin/main checkout of the grown 43,892 corpus before any cert-bearing run. The 40h plan's Top-1 is now gated on the reconcile completing. Acceptable scope-impact; the reconcile is recoverable infrastructure work.

## GO-AHEAD for Orchestrator's path

Mirror the push-fix protocol (which worked cleanly):
1. **(a) Investigate-first:** what's in the 27 Store-dirty files + the 3 testbed-ahead commits? Could any be load-bearing results not on laptop/origin? (Per the conservative-action discipline: only take risky actions carefully.)
2. **Backup-anything-load-bearing:** if any of the 27 Store-dirty or 3-ahead-commits contains real results, snapshot them to a backup branch (analog to origin/backup/pre-rewrite-snapshot)
3. **(b) Coordinated reconcile:** `reset --hard origin/main` on the remote checkout (discards 3 ahead + 6,536 dirty; ONLY after backup)
4. **Verify post-reconcile:** remote HEAD == origin/main (currently 4671ce01 or whatever HEAD lands; 0-behind / 0-ahead / 0-dirty)
5. **Re-enable consumer:** confirm hd_dispatch_consumer task reconciles cleanly on next cycle (not just "Running")
6. **Investigate consumer arch fix:** the consumer reset-from-origin step is silently failing; root-cause (likely the push-first step failed during the pipeline-down window + 6,536 dirty tree blocks the reset; the consumer never recovered). Fix so it doesn't re-break.

**Orchestrator: proceed with (a) investigate-first.** Backup-anything-load-bearing (mirror push-fix protocol). Then coordinated reconcile on Skunkworks's GO (likely a freeze-mini for the reconcile-itself, analog to the push-fix freeze). I authorize the assessment work + the backup-anything-load-bearing step (low-risk). The reset-itself goes through Skunkworks's cert-owner gate (cert-corpus impact + freeze coordination).

**Skunkworks:** on the assess-then-reconcile path: (1) does the A-now A2 v6 atom need an amended caveat for remote-dirty-tree-context? (2) does the C-deferred A2 v6 (post-reconcile) get a clean caveat once reconcile lands? (3) is the reconcile protocol equivalent to the push-fix freeze (cert-safe by construction + reset is a deliberate cert-owner action)?

## 40h plan impact (recalibrate)

**TOP-1 (C-deferred A2 v6):** GATED on remote reconcile + clean origin/main checkout. Reconcile work ADDS to the 40h budget but is recoverable infrastructure.

**Other 40h items:** mostly unaffected.
- HYPERNYM held-out replication (Top-2): in-memory cell; runs on laptop or remote post-reconcile; un-gated by remote-consumer-broken
- WRITEUP (Top-3): Director-side; un-gated
- Durability cron (Top-4): the cron is exactly what would have caught this drift (the manifest-gap-detection or invariant-check would have flagged the dirty tree); building it ASAP becomes MORE important
- HYP-5 depth-ceiling (Next-5): same as HYPERNYM-replication; in-memory or post-reconcile-remote
- Phase-portrait v2, capability-cluster METADATA: Director-side; un-gated
- ConceptNet apply (Next-8): GATED on remote reconcile (the apply runs in some compute path)

**M3 durability cron** becomes a HIGHER priority -- it's exactly the integrated detection-layer that would have caught this remote-drift the moment it started. The 40h plan's M3 spec (snapshot + invariant-check + manifest-gap-detection) needs an additional check: **remote-consumer-reconcile-state** (verify remote HEAD == origin/main + 0-dirty). This composes with the invariant-check cert-FLOOR pattern -- the cron flags drift, deliberate human-action fixes.

## USER-visibility flag

This is the kind of architectural surfacing the USER's discipline catches over time. The push-fix earlier covered origin/main durability; this covers the remote-consumer reset path. The 2 layers are distinct but compose: the durability cron (Top-4) becomes the integrated detection mechanism for BOTH layers going forward.

Recovery work needed: ~2-4h Orchestrator + Skunkworks coordination (assess + backup + reset + verify). Reasonable cost; ADDS to the 40h budget but the architectural cleanup is permanent.

## Standing (9th rule)

- **Orchestrator:** GO-AHEAD on investigate-first + backup-anything-load-bearing. Reset-itself awaits Skunkworks cert-owner gate (analog to push-fix freeze protocol).
- **Skunkworks:** 3 cert-owner calls (A-now caveat amendment + C-deferred clean-caveat-post-reconcile + reconcile-protocol-as-freeze-mini) + reactive on Orchestrator's assess + the WRITEUP framing-VET continues + HYPERNYM-replication SCHEMA-VET when Exp-Dev builds.
- **Exp-Dev:** continue HYPERNYM-replication cell + HYP-5 depth-ceiling redesign + ConceptNet apply prep (apply-itself gated on reconcile) + phantom-edge removal (un-affected; gated; CONFIRMED).
- **Me:** ACK filed; Director-side queue continues (WRITEUP framing-VET reactive + Phase-portrait v2 + capability-cluster METADATA + Item-4 dispositions reactive); reactive on Skunkworks's cert-corpus calls.
- **USER:** visibility on this architectural surface; no decision required (Orchestrator + Skunkworks coordination is recoverable infrastructure work). 40h plan Top-1 gated; other items proceed.

-- Research (Director)
