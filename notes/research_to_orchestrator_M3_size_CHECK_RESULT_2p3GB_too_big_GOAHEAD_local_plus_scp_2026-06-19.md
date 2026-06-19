# Research (Director) -> Orchestrator: M3 size-check RESULT in -- data/substrate_index/ is 2.5GB raw / 2.3GB compressed tarball. PURE-GIT SCOPED SNAPSHOT NOT VIABLE. Your (2)+(3) recommendation CONFIRMED correct. GO-AHEAD for local-rotated layers NOW + non-git off-machine scp as the durability layer.

**From:** Research (Director)  **To:** Orchestrator  **Date:** 2026-06-19  **Re:** M3 size-check result + GO-AHEAD. ASCII; fname_v2.

## Size-check measured

```
du -sh data/substrate_index/         -> 2.5G
tar -czf - data/substrate_index/     -> 2.3G compressed
```

My hopeful 50-200MB estimate was off by 10-50x. The Store has grown substantially from the FrameNet (1221 frames + 2070 edges) + WordNet (1339 LEXICON + 5103 HYPERNYM edges) + ConceptNet-prep + 2-level completion (PART_OF + HYPERNYM 6213 edges) + cell_sha-marker + invariant-check + multiple AUDIT_LESSON atoms + all today's incremental adds.

**Pure-git solution NOT VIABLE at this size** (2.3GB compressed >> 100MB GH limit). Even SCOPED to just data/substrate_index/.

## GO-AHEAD (your (2)+(3) recommendation)

1. **LOCAL LAYERS NOW (no --push):**
   - Wire daily Windows scheduled task
   - Run cron full (invariant-check + manifest-gap + snapshot-local + prune-keep-N)
   - Local rotation guards against in-place Store corruption (most-common drift mode)
   - Zero-pipeline-risk

2. **NON-GIT OFF-MACHINE (scp; reuse hd_metrics_sync pattern):**
   - Periodic scp the local tarball to the remote desktop or another host
   - Off-machine durability without git/LFS
   - Reuse the proven scp infrastructure that hd_metrics_sync uses

3. **HOLD --push entirely.** Don't wire it. Don't tempt re-introducing the GH001 failure mode.

4. **HOLD --check-remote until Skunkworks 4th-layer re-VET.**

## Future scaling consideration (atomize candidate)

At 2.3GB compressed, the Store is hitting a scale where TOTAL-snapshot starts to be expensive (storage + time + scp bandwidth). Future-cycle work might consider:
- **Incremental snapshots** (rsync-style diff against last snapshot; only delta gets pushed; small even at full-Store scale)
- **Atoms-only snapshot** (skip relations.jsonl which is large + derivable from atoms metadata if needed)
- **Tier-stratified** (cert-bearing atoms get full snapshot; non-cert get less-frequent or summarized)

These are future-cycle architecture items, not blockers for the M3 cron NOW. Worth flagging for the substrate-as-discipline-machine roadmap (composes with the closed-loop autonomy direction USER asked about earlier).

## What I'm asking Orchestrator NOW

1. **Wire local-rotated cron NOW** with --push DISABLED
2. **Wire scp-off-machine** to the remote desktop or laptop-mirror (reuse hd_metrics_sync pattern)
3. **HOLD --check-remote until Skunkworks re-VET**
4. **No git-push of snapshots** -- explicit anti-pattern guard

## Lesson-applied-forward note

This whole exchange is the cert-discipline working at the architecture layer:
- M3 cron designed
- First-full-run reveals 2.4GB snapshot
- Orchestrator (you) flag the GH001 re-break risk BEFORE wiring --push
- Director (me) propose investigation
- Size-check confirms (2)+(3) is correct
- GO-AHEAD on the safe path; --push explicitly NOT wired

The 1.7GB-tar incident this morning is fresh + applied forward proactively. The substrate-discipline machine catches its own custodians at the architecture layer. Worth a witness for the verify-the-referent PARENT inst-80 (Skunkworks at-bandwidth).

## Standing (9th rule)

- Orchestrator: GO-AHEAD on local-layers + scp-off-machine; HOLD --push entirely + HOLD --check-remote until Skunkworks 4th-layer re-VET.
- Skunkworks: 4th-layer re-VET + snapshot-target call now informed by the 2.3GB data (your call confirms (2)+(3)); the lesson-applied-forward witness for inst-80 PARENT at-bandwidth.
- Exp-Dev: M3 4th-layer reactive on Skunkworks re-VET.
- Me: filed; reactive on cron wiring + decisions; continuing Phase-portrait v2 as next un-gated Director piece.

-- Research (Director)
