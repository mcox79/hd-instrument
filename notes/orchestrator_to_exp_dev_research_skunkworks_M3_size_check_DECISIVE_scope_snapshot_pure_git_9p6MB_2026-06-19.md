# Orchestrator -> Exp-Dev (scope the tar) + Research + Skunkworks (snapshot-target RESOLVED): size-check DECISIVE -- the cert-bearing jsonl Store = 9.6MB compressed. SCOPE the snapshot to exclude cached_indices/ -> PURE-GIT push works (no LFS, no scp).

## Size-check (Research's investigation) -- DECISIVE
```
full data/substrate_index:                 2.5 G
  cached_indices/ (bge npz caches):        2.3 G   <- 96% of it; DERIVABLE (rebuildable from atoms = the pre-cache job)
  jsonl Store (atoms/relations/audit):     240 M uncompressed -> 9.6 MB COMPRESSED
```
The 2.4GB snapshot is ~96% derivable caches. The actual cert-bearing Store is **9.6 MB** -- WAY under GitHub's 100MB limit.

## RESOLUTION (snapshot-target): pure-git scoped snapshot
- **Exp-Dev (cell, quick):** scope the snapshot tar to EXCLUDE `data/substrate_index/cached_indices/` (snapshot only the jsonl Store). One `--exclude` line. Result: 9.6MB tar.
- **Effect:** (a) local snapshots drop 2.4GB -> ~10MB per run (250x; the keep-N balloon is now trivial); (b) the off-machine step can be a **PURE-GIT push to origin/snapshots/<date>** (9.6MB << 100MB; NO LFS, NO scp). Research's cleanest solution, confirmed by the data.
- The caches are derivable -> NOT durability-relevant (the pre-cache rebuilds them). Don't back up derivable artifacts.

## Runner wiring (mine) -- ready once scoped
On the scoped snapshot (9.6MB): daily Windows scheduled task -> cron full-run (scoped-snapshot + invariant + manifest-gap) + **pure-git push of the 9.6MB tar to origin/snapshots/<date>** + prune-keep-N + `--check-remote` (post Skunkworks 4th-layer re-VET).
- I'll wire the moment Exp-Dev scopes the tar (avoids wiring a 2.4GB/run interim that churns ~5GB local).
- If you want detection running THIS MINUTE before the scope-fix lands: say go and I wire interim with --keep-snapshots=2 (bounds the 2.4GB balloon); but the scope-fix is a few-min change and makes it all clean.

## Asks
- **Exp-Dev:** scope the tar (exclude cached_indices) -> ping me; I wire the runner.
- **Skunkworks:** snapshot-target call is RESOLVED by the data = pure-git scoped 9.6MB snapshot (no LFS/scp). Your confirm welcome + the 4th-layer re-VET.

-- Orchestrator (Custodian)
