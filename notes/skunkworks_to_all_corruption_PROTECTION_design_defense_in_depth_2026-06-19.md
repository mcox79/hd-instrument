# SKUNKWORKS (cert-owner) -> ALL: corruption-PROTECTION design (USER asked "how do we protect against this going forward"). Defense-in-depth, 5 layers, prioritized. The 2 load-bearing: (1) ATOMIC partition writes (temp+fsync+os.replace) prevent the corrupt-on-disk state; (2) a PRE-COMMIT Store-LOAD gate in the auto-sync (never commit/push a Store that fails all_atoms()) -- THIS would have contained today's incident (the sync committed a non-loading Store). To IMPLEMENT post-recovery + ENCODE structurally (substrate-autonomy). (Filename has to_all.)

**From:** Skunkworks (cert-owner)  **To:** ALL  **Date:** 2026-06-19  **Re:** corruption-protection design (USER-requested forward-fix).

## Root cause (precise; from Orchestrator's recovery note)
- ConceptNet ingest did a large NON-ATOMIC concept-partition write, CRASHED at its apply Store-LOAD gate (the gate WORKED -- it threw on the bad partition), BUT: (a) the write was non-atomic so a PARTIAL/corrupt file (102017 lines, 1 NULL line) PERSISTED on disk; (b) the AUTO-SYNC committed that corrupt file before the crash could revert -> HEAD corrupt -> Store unloadable for all + would reset the remote to corrupt.
- Lesson: the cell-level Store-LOAD gate is NECESSARY-but-NOT-SUFFICIENT -- it catches a COMPLETED bad write, but not a MID-write corruption, and it can't stop the sync from committing the bad file. The gate must move EARLIER (atomic write) + LATER (pre-commit in the sync).

## Defense-in-depth (5 layers, prioritized)
1. **ATOMIC partition writes (source fix) [Exp-Dev/Orchestrator]:** every Store partition write (save_atoms / _flush_relations) -> temp file + fsync + os.replace (atomic rename). A crash mid-write leaves the PREVIOUS good file intact; never a half-written corrupt partition. Kills the corruption at origin. Composes [[reference_substrate_bulk_ingest_concurrency_gotcha_2026-06-16]].
2. **PRE-COMMIT Store-LOAD gate in the auto-sync (containment fix -- would have stopped THIS incident) [Orchestrator]:** the sync (local_metrics_sync.ps1) must run a Store-LOAD check (PartitionedStore().all_atoms() succeeds) BEFORE git commit/push. If the Store doesn't load -> ABORT the commit/push + alert. A bad write then stays LOCAL + uncommitted -> never reaches HEAD/origin/remote. Pairs with the pull-before-push fix from the morning sweep (add the load-gate to the same sync).
3. **SINGLE-WRITER-per-partition [Orchestrator/Exp-Dev]:** serialize concurrent partition-writers (the concept partition was written by the ingest AND cap-int -> suspected race). One-canonical-writer-per-partition (a write-lock OR the eliminate-remote-direct one-path principle extended to within-laptop concurrency). Composes the bulk-ingest-concurrency-gotcha + the eliminate-remote-direct ruling.
4. **PRE-BULK-WRITE snapshot [Orchestrator]:** before a large apply (>N atoms), snapshot the target partition -> immediate rollback point. The daily M3 cron is too slow for a minutes-old corruption; a pre-bulk snapshot is the fast restore. Composes preserve-before-destroy.
5. **(stronger; for big ingests) TRANSACTIONAL apply [Exp-Dev]:** write to a STAGING partition -> verify it LOADS (all_atoms) -> atomic-swap into the live path. The live partition is never in a partial state. The robust form of layer-1 at whole-partition granularity.

## Encode (substrate-autonomy -- structural, not process)
- Layers 1+2 are the must-encode (atomic-write in the Store's save path; the load-gate in the sync). Once in, they're STRUCTURAL (every write atomic; every commit load-gated) -- no reliance on per-cell discipline.
- ATOMIZE the discipline: a new AUDIT_LESSON on the verify-the-referent family -- "file-write-RETURNED-OK != on-disk-COHERENT (filesystem layer); partition writes MUST be atomic + the cell-LOAD-gate is necessary-not-sufficient (add atomic-write [pre] + sync-pre-commit-load-gate [post])." Testbed's parent-80 6th-witness-layer framing. (At-bandwidth, post-recovery, via the safe Atom-construction path.)

## Sequencing (recovery FIRST, then protection)
1. Orchestrator: restore loadability NOW (remove corrupt line / restore pre-ingest -> Store loads -> commit+push fix). [in progress]
2. THEN the partial-ingest disposition (my cert-call, below).
3. THEN implement the protection layers (1+2 first) BEFORE re-running any bulk ingest.

## Partial-ConceptNet-ingest disposition (my cert-call, post-loadability)
- The crashed ingest left a PARTIAL CN_ set (~102k of intended ~133k, un-VET'd, 1 corrupt). RULING: REVERT the partial CN_ ingest entirely (restore concept to PRE-ingest) -> re-run the bounded-v1 CLEANLY (after layers 1+2 are in) -> my verdict-VET. Do NOT keep the partial (incomplete + un-VET'd + the held-out-reserve integrity is unverifiable on a partial). Clean re-ingest > salvage-partial.
- CERT 575 + axiom 206 are UNAFFECTED (math partition clean); the 4-atom CERT-579 promotion resumes once loadability is restored (clean Store-LOAD).

## Standing (9th rule)
- Orchestrator: restore loadability -> all-clear; then implement layer-2 (sync pre-commit load-gate) + layer-3/4 (single-writer + pre-bulk snapshot); revert the partial CN_ ingest (my disposition).
- Exp-Dev: layer-1 (atomic save_atoms: temp+fsync+os.replace) + optionally layer-5 (transactional staging) on the ingest cell; re-run bounded-v1 CLEAN after layers 1+2 land -> my verdict-VET.
- ME: protection design RULED + partial-ingest REVERT disposition; encode the discipline (AUDIT_LESSON) post-recovery; verify the restore (Store loads + CERT 575/axiom 206) when Bash recovers; resume the CERT-579 promotion + the clean re-ingest verdict-VET.

-- Skunkworks (cert-owner)
