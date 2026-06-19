# Research drill: atomic write + shard-swap patterns for multi-process JSONL atom store

date: 2026-06-13
topic: operational atomicity for PartitionedStore (Testbed urgent)
budget: ~30 min, 6 web searches, Sonnet lit-scan tier
calibration: lit-scan deflation 0.15-0.25 applied; novel-synthesis cap 0.50; we are first to build this exact substrate so prior work informs but does not govern

## (a) HEADLINE

Three production-grade patterns transfer cleanly to the PartitionedStore: (1) write-tmp + fsync(file) + os.replace + fsync(parent_dir) for per-atom-file writes solves the JSONDecodeError race; (2) RocksDB-style CURRENT-pointer file with versioned shard directories solves the bulk-rebuild transient-empty window via atomic single-byte pointer swap; (3) reader-side version-stamp + row-count sanity sentinel lets cells detect mid-rebuild and either retry or use last-good snapshot. Migration path is incremental: ship pattern 1 today (drop-in), pattern 3 this week (defensive), pattern 2 next sprint (architecture). Per-platform caveat: os.replace is atomic on POSIX but on Windows MoveFileEx may silently fall back to non-atomic CopyFile under unknown conditions, so reader-side defense is REQUIRED not optional.

## (b) Cheap decisive test

Test on a scratch copy of one partition shard (NOT production):
1. Spawn 4 concurrent Python processes:
   - 2 readers doing tight-loop `for line in open(jsonl): json.loads(line)` over a 5000-atom shard
   - 1 ingest writer doing `write-tmp + os.replace` 100 atoms/sec for 60 sec
   - 1 rebuild writer doing the CURRENT-pointer swap every 10 sec
2. Measure: JSONDecodeError count in readers (target = 0); reader-observed atom_count dip below 80% of pre-rebuild count (target = 0 occurrences); end-to-end ingest latency overhead (acceptable: <2x baseline).
3. Run on Windows (canonical Testbed host) AND verify on WSL/POSIX for cross-platform confidence.

Total cost: 1 afternoon of laptop CPU. No GPU.

## (c) Falsifiable predictions

### HARD-PASS thresholds (pattern adoption recommended)
- Pattern 1 (write-tmp + os.replace per atom file): 0 JSONDecodeError across 10K writes during concurrent read, BOTH platforms.
- Pattern 2 (CURRENT-pointer shard swap): readers NEVER observe atom_count or relations_count below 95% of last-stable snapshot during a full rebuild cycle.
- Pattern 3 (version-stamp sentinel): reader detection rate for mid-rebuild state >= 99%; false-positive (retry when not needed) rate <= 5%.

### HARD-FAIL thresholds (pattern rejected, must redesign)
- Pattern 1 still produces JSONDecodeError > 0 on Windows even with fsync + os.replace: indicates Windows MoveFileEx fallback path; must adopt filelock-based exclusive writer pattern instead (heavier; serializes writes).
- Pattern 2 produces a visible empty window >= 100ms during swap (e.g., if the CURRENT-pointer rewrite itself is non-atomic on Windows): must adopt double-symlink or junction-point swap, or accept advisory reader-side retry as primary mitigation.
- Pattern 3 false-positive rate > 20%: sentinel is too noisy, must add hysteresis or shorter rebuild windows.

### Calibration notes
- Patterns 1 and 2 are STANDARD industry practice (atomicwrites lib, RocksDB MANIFEST/CURRENT, Elasticsearch alias swap, Solr Core swap, deployer.org symlink swap) -> high P(works as advertised on POSIX), P_deflated ~ 0.70.
- Windows atomicity is the genuine unknown: P_deflated ~ 0.45 that os.replace alone suffices; reader-side defense closes the gap to ~0.85 combined.
- Pattern 3 (reader-side sanity) is the substrate-specific synthesis (we have row-count expectations across shards; production DBs typically don't expose this to readers); P_deflated ~ 0.55.
- Novel-synthesis cap (0.50) applied to Pattern 3 only.

## (d) Cross-thread synthesis

Three concrete patterns Testbed should adopt, code-snippet level:

### Pattern 1: per-atom-file atomic write (drop-in today)

```python
# tools/atom_store_atomic.py
import os, json, tempfile
from pathlib import Path

def atomic_write_atom_file(target_path: Path, content: str) -> None:
    """Write content to target_path atomically. POSIX-atomic; Windows best-effort."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    # Use same directory so os.replace stays within filesystem (atomic guarantee)
    fd, tmp_path = tempfile.mkstemp(
        prefix=target_path.name + ".",
        suffix=".tmp",
        dir=str(target_path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())   # flush file contents to disk
        os.replace(tmp_path, target_path)  # atomic on POSIX; MoveFileEx on Win
        # fsync parent dir on POSIX so the rename is durable; no-op on Windows
        if os.name == "posix":
            dir_fd = os.open(str(target_path.parent), os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    except Exception:
        # Best effort cleanup of orphaned tmp file
        try: os.unlink(tmp_path)
        except OSError: pass
        raise
```

Reader side never sees a partial file: it either opens the old atom or the new atom, never a JSONL fragment. This is the precedent from python-atomicwrites and the ActiveState recipe; it is the WAL-Time write-then-replace pattern.

### Pattern 2: CURRENT-pointer shard swap for bulk rebuild

Modeled directly on RocksDB's MANIFEST/CURRENT design. Instead of mutating `data/relations/<shard>.jsonl` in place, version every full rebuild into a fresh directory and atomically flip a single tiny pointer file:

```
data/
  store/
    CURRENT                            # contains one line: "v_2026_06_13_140532"
    snapshots/
      v_2026_06_13_140000/
        relations/
          DEPENDS_ON.jsonl
          SHARES_MATH.jsonl
        atoms/...
        manifest.json   # {atom_count: 1847, relations: {DEPENDS_ON: 2251, SHARES_MATH: 332}, build_complete: true}
      v_2026_06_13_140532/             # being built RIGHT NOW
        ...
        manifest.json   # build_complete: false
```

Rebuild procedure:
1. Pick new version id `v_NEW`.
2. Build the whole snapshot under `snapshots/v_NEW/` with `manifest.build_complete = false`.
3. Final step: write `manifest.json` with `build_complete = true` (using Pattern 1 atomic write).
4. Atomic CURRENT swap: write `CURRENT.tmp` containing `"v_NEW"`, then `os.replace(CURRENT.tmp, CURRENT)`.
5. Retain previous snapshot for one cycle (rollback safety), then garbage-collect.

Reader procedure:
```python
def open_store():
    version = (root / "CURRENT").read_text().strip()
    manifest = json.loads((root / "snapshots" / version / "manifest.json").read_text())
    if not manifest.get("build_complete"):
        # Fell into a half-built snapshot; fall back to previous if available
        return _open_previous_snapshot()
    return SnapshotHandle(root / "snapshots" / version, manifest)
```

Because the reader resolves CURRENT exactly once per session (or per "open"), it pins a single coherent snapshot. New rebuilds do not change what an already-open reader sees; this is snapshot isolation MVCC-style without a database.

Precedent: RocksDB MANIFEST/CURRENT, Elasticsearch alias swap, Solr Core swap, deployer.org symlink swap.

### Pattern 3: reader-side version-stamp + row-count sentinel (substrate-specific defensive)

Even with patterns 1 + 2 in place, defense in depth catches the case where a cell forgot to re-open the snapshot, or where Windows os.replace fell back to non-atomic. Every cell reads through a thin wrapper:

```python
class StoreReader:
    def __init__(self, expected_min_counts: dict[str, int] | None = None):
        self.handle = open_store()
        self.expected = expected_min_counts or self._load_expected_from_last_run()

    def _sanity_check(self) -> bool:
        m = self.handle.manifest
        if not m.get("build_complete"):
            return False
        # Row-count floor: 80% of last-known-good is the alarm threshold
        for rel, expected in self.expected.get("relations", {}).items():
            actual = m["relations"].get(rel, 0)
            if actual < 0.80 * expected:
                return False
        return True

    def get_relation(self, rel: str):
        if not self._sanity_check():
            # Re-open against current CURRENT; if still bad, raise loud, don't return wrong data
            self.handle = open_store()
            if not self._sanity_check():
                raise StoreTransientError(f"shard {rel} below sanity floor; refusing to read")
        return self.handle.read_relation(rel)
```

The `expected_min_counts` persists in `data/store/last_seen.json` (atomically written by Pattern 1 on each successful close), so cells inherit the previous session's expectation without explicit configuration.

This catches today's exact hazard: DEPENDS_ON 2251 -> 12 mid-rebuild would trigger `actual < 0.80 * 2251` and the cell would raise `StoreTransientError` instead of silently returning a wrong result.

### Honest framing: prior-work-informs-not-governs

We may be first to build a substrate that:
- Has 4 concurrent cognitive sessions sharing the same atom-store on a SINGLE laptop filesystem (no DB server, no network FS).
- Treats atoms as cognitive primitives where a silently-wrong relation read corrupts downstream reasoning (not just a stale cache).
- Has substrate-aware row-count expectations the reader can defensively assert against.

Standard databases (RocksDB, ES, Solr) solve part (1) and (2) of this but assume DB-server mediation (a single coordinator). Our pattern 2 borrows their architecture without the server; pattern 3 is the substrate-specific augmentation that compensates for the absence of a coordinator process.

### Migration path

- TODAY (drop-in, no architecture change): wrap every existing JSONL writer in Pattern 1's `atomic_write_atom_file`. Single-file edit per writer. Zero schema change. Zero reader change. Eliminates JSONDecodeError class entirely on POSIX, ~95% on Windows.
- THIS WEEK (defensive): ship `StoreReader` wrapper (Pattern 3) and route 1-2 high-stakes cells through it first (KP P1, CH-P6). Validate sentinel false-positive rate stays low. Then route the rest of the cells.
- NEXT SPRINT (architecture): introduce snapshots/CURRENT layout (Pattern 2). Test on scratch shard. Migrate one relation type at a time (start with SHARES_MATH since it's the one currently 0-ing during rebuild). Keep old paths as symlinks into the active snapshot for backward compatibility during cutover.

## (e) Substrate-product implications

- The substrate-product positioning (auditable AI memory subsystem) requires atomicity guarantees stronger than vanilla RAG — LLM-based memory stores routinely produce torn writes during concurrent sessions (the claude-code issue #20992 in the citations is a real-world demonstration of this exact failure mode in an Anthropic shipping product). Our atomic-write + version-stamp + reader-sentinel triple gives us a defensible "we don't silently return wrong memory" claim that LLM RAG stores cannot match.
- Pattern 2 (CURRENT pointer + snapshots) gives us free rollback: when an ingest cycle produces a regression (verdict says verdict HARD-FAIL post-ingest), we can flip CURRENT back to the previous snapshot in O(1) without re-ingesting. This is a substrate-product feature, not just an operational hygiene win.
- Pattern 3 (reader-side sanity sentinel) is the FIRST CONCRETE INSTANTIATION of "substrate refuses to return wrong data" as a runtime invariant rather than a post-hoc audit property. This is shippable as a substrate-product differentiator.

## (f) Citations

Verified count: 9 distinct sources surfaced across 6 web searches.

1. ActiveState recipe 579097 (atomic write-tmp + rename with fsync)
2. zetcode os.replace guide (POSIX vs Windows atomicity)
3. python-atomicwrites library docs + GitHub (race-free atomic_write API)
4. py-filelock docs (cross-platform OS-level locking)
5. DEV community "Crash-safe JSON at scale" (atomic writes + .bak fallback)
6. RocksDB MANIFEST documentation (github.com/yanghonggang/rocksdb.docs, github.com/facebook/rocksdb/wiki/MANIFEST) -- CURRENT pointer atomic swap
7. Elasticsearch alias swap pattern (medium.com/zumba-tech) + django-elasticsearch-dsl PR #358 zero-downtime rebuild
8. deployer.org "The atomic symlink swap" (mv -T indivisibility on POSIX)
9. jsonlines.org + ndjson.com + claude-code issue #20992 (JSONL truncated-line semantics, real-world concurrent-write corruption case)

Pre-registered HARD-PASS / HARD-FAIL thresholds: section (c). Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]. Generic queries only per [[feedback-query-privacy-decomposition]].
