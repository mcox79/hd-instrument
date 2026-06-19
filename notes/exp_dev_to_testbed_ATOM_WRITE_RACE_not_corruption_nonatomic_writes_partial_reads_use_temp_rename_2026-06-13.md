# exp_dev -> testbed: the "corrupt atom" is a CONCURRENT-WRITE RACE (non-atomic atom writes), NOT data corruption. Concurrent readers hit partial-write states. Fix = atomic write (temp + os.replace) and/or reader retry.

**From:** exp_dev  **Date:** 2026-06-13. Per USER: share the corrupt-atom finding with testbed.

## Evidence it is a RACE, not corruption
- Reading atoms on the desktop (PartitionedStore.all_atoms()) fails with json.JSONDecodeError "Unterminated string" --
  but at a DIFFERENT position each run: first char 144, then char 861. A genuinely-corrupt file would fail at the SAME spot.
- A standalone full scan of data/substrate_index/**/*.json* found **0 corrupt files** -- i.e., when not being written, every
  file is valid JSON. The failures only happen when a read coincides with a write.
- Testbed is actively backfilling atoms right now (BATCH_01/02 algebra + serves_capability, seen on the bus). The error is
  "line 1 column N" = a SINGLE-LINE JSON file being rewritten; a reader catches it mid-rewrite (truncated) -> Unterminated string.

## Diagnosis
Atom (or index) files are written NON-ATOMICALLY: the writer truncates + rewrites in place, so any concurrent reader can see a
partial file. With 4 sessions + a producer + experiments all reading the substrate, this race surfaces intermittently and breaks
ANY desktop cell that loads atoms (it broke my F4 Cell B; I ran it on the laptop's copy instead).

## Recommended fix (testbed owns the substrate write path)
1. **Atomic writes**: write to a temp file in the same dir, then os.replace(tmp, final) (atomic rename on Windows/NTFS via
   os.replace). Readers then always see either the old or the new complete file, never a partial.
2. **And/or reader retry**: wrap atom-load json parsing in a retry (e.g., 3x with 50ms backoff) to tolerate any residual race.
3. Lower-priority: a write lock around the substrate store (the runners already use msvcrt locks for the queue; the atom store
   could reuse that).

## Impact / ask
- Until fixed, desktop experiments that read atoms fail intermittently (laptop reads are usually fine since fewer concurrent
  writers there). exp_dev workaround = run atom-reading numpy cells on the laptop's clean copy.
- Please make the atom/index writes atomic (temp + os.replace). This is the root cause, not "corrupt data needing re-sync."
