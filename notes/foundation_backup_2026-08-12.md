# Foundation backup — 2026-08-12

Backs up `data/foundation/` growth artifacts off the single disk they lived on.
`data/foundation/` is gitignored (`data/*/**` in `.gitignore`), so before this,
these directories existed in exactly one place: this machine's working tree.

## What was backed up

| Store | Uncompressed | Compressed (.tar.gz) | SHA256 |
|---|---|---|---|
| `data/foundation/reading_grounding_v1/` | 22M | 16,287,086 B | `b61f6ab296202bfd539671c04ef7fed3c93531751ecead159c0218ea9d0aec93` |
| `data/foundation/reading_grounding_v2_qualityfix/` | 23M | 13,290,009 B | `d422edefd03195be5f167253242378ce0e2b87bff4745b4c91b640257d3df4dd` |
| `data/foundation/reading_grounding_v3_definitional/` | 1.5M | 204,940 B | `065ee70c864285d87b2aac1640c4bcad27dcc784d53438c8a346f40991aec26b` |

Originals were read-only inputs to `tar` — nothing under `data/foundation/` was
modified, moved, or deleted.

## Destination 1: remote (marsh@home)

- **Host:** `marsh@home`, an SSH alias resolved via `/c/Windows/System32/drivers/etc/hosts`
  (`100.91.12.42 home.tail37031e.ts.net home` — a Tailscale IP; the same
  `SSH_TARGET="marsh@home"` used by `tools/orchestrator/queue_add.sh` and
  `tools/orchestrator/remote_state.py`, so this is the same GPU/CPU runner box
  the dispatch tooling already targets, not a new host).
- **Reachability verified before transfer:** `ssh marsh@home "echo REMOTE_OK && hostname && whoami"`
  returned `REMOTE_OK` / `Home` / `home\marsh`.
- **Remote path:** `C:/dev/hd-instrument/data/backups/foundation_2026-08-12/`
  (a new subdir under the remote repo's `data/`, kept separate from the
  runner's live queue/experiment data so it can't be mistaken for active state).
- **Checksum verification:** `certutil -hashfile <file> SHA256` run remotely on
  all three `.tar.gz` files, compared byte-for-byte against the local
  `sha256sum` output above. **All three matched exactly.**

## Destination 2: git (origin)

- **Tracked path chosen:** `backups/foundation/2026-08-12/` — a top-level
  `backups/` directory, NOT under `data/` (which is blanket-gitignored via
  `data/*` + `data/*/**` per DECISION 220). Verified not excluded:
  `git check-ignore -v backups/foundation/2026-08-12/reading_grounding_v1_2026-08-12.tar.gz`
  exits 1 (not ignored). The live `data/foundation/` dirs remain untracked and
  ungrown-in-git, as intended — only these dated snapshots are tracked, so
  history grows by one bounded commit per backup event, not by every run.
- **Commit:** `a37b8abeb` on branch `dataprep/mcguffey-graded-corpus`, path-scoped
  (`git commit -- backups/foundation/2026-08-12/`; no `git add -A`, no other
  modified files in the working tree were touched — there were many unrelated
  dirty `data/*/metrics.json` files present from other in-flight work).
- **Size added to repo:** 4 files, ~29.8MB total (16,287,086 + 13,290,009 +
  204,940 + 339 bytes) — under the 50MB caution threshold, so it was pushed.
- **Push:** `git push origin dataprep/mcguffey-graded-corpus` →
  `00e7c4221..a37b8abeb dataprep/mcguffey-graded-corpus -> dataprep/mcguffey-graded-corpus`,
  confirmed present via `git ls-tree -r origin/dataprep/mcguffey-graded-corpus --name-only`.

## What is NOT backed up (so nobody assumes more coverage than exists)

- `data/foundation/reading_grounding_v1_post_bootstrap_control_copy/` (8.0M) — not requested, not copied.
- `data/foundation/reading_grounding_v1_smoke/` (5.5M) — not requested, not copied.
- `data/foundation/reading_grounding_v1_smoke_post_bootstrap_control_copy/` (5.0M) — not requested, not copied.
- `data/foundation/reading_grounding_v2_qualityfix_smoke/` (7.5M) — not requested, not copied.
- Only `main` was never touched — the commit/push happened on
  `dataprep/mcguffey-graded-corpus` (the checked-out branch at task time).
  If `origin/main` needs this snapshot too, it must be cherry-picked or merged
  separately; it is not there yet.
- No third copy exists anywhere else (no cloud storage, no second remote host).
  If `marsh@home` and this machine are both lost before a `git fetch`/`git pull`
  elsewhere, only GitHub's copy of the git-pushed branch survives.
- The remote backup at `marsh@home` is a **snapshot at commit time**, dated
  `2026-08-12` — it will NOT auto-update if `data/foundation/` grows further;
  this procedure must be re-run for future growth.

## Restore procedure

### From git (any machine with this repo cloned)

```bash
git fetch origin dataprep/mcguffey-graded-corpus
git checkout origin/dataprep/mcguffey-graded-corpus -- backups/foundation/2026-08-12/
cd /path/to/hd-instrument
mkdir -p data/foundation
tar -xzf backups/foundation/2026-08-12/reading_grounding_v1_2026-08-12.tar.gz -C data/foundation
tar -xzf backups/foundation/2026-08-12/reading_grounding_v2_qualityfix_2026-08-12.tar.gz -C data/foundation
tar -xzf backups/foundation/2026-08-12/reading_grounding_v3_definitional_2026-08-12.tar.gz -C data/foundation
# verify:
sha256sum backups/foundation/2026-08-12/*.tar.gz
# compare against backups/foundation/2026-08-12/SHA256SUMS.txt (must match VERBATIM)
```

### From remote (marsh@home)

```bash
mkdir -p /tmp/foundation_restore
scp "marsh@home:C:/dev/hd-instrument/data/backups/foundation_2026-08-12/*.tar.gz" /tmp/foundation_restore/
scp "marsh@home:C:/dev/hd-instrument/data/backups/foundation_2026-08-12/SHA256SUMS.txt" /tmp/foundation_restore/
cd /tmp/foundation_restore && sha256sum -c SHA256SUMS.txt   # must report OK for all 3
mkdir -p /path/to/hd-instrument/data/foundation
tar -xzf reading_grounding_v1_2026-08-12.tar.gz -C /path/to/hd-instrument/data/foundation
tar -xzf reading_grounding_v2_qualityfix_2026-08-12.tar.gz -C /path/to/hd-instrument/data/foundation
tar -xzf reading_grounding_v3_definitional_2026-08-12.tar.gz -C /path/to/hd-instrument/data/foundation
```

## Verified vs assumed

**Verified (evidence in this doc/session):**
- `marsh@home` reachability, before any transfer (`echo REMOTE_OK` round-trip).
- Byte-identical checksums between local tar.gz and the remote copy (`sha256sum` vs `certutil -hashfile`, all 3 files, exact match).
- The git commit is on `origin` (`git ls-tree` against `origin/dataprep/mcguffey-graded-corpus` shows all 4 files present).
- `backups/` is not gitignored (`git check-ignore` exit 1).
- Total pushed size (~29.8MB) is under the 50MB stop-and-report threshold, so the push was safe to make without escalation.

**Assumed, not verified this session:**
- That `tar -xzf` round-trips these archives back to byte-identical directory
  contents (never extracted-and-diffed a restore in this session — only the
  compressed `.tar.gz` file hashes were checked end-to-end, not a full
  extract-and-compare of the original directory tree).
- That GitHub's stored blob for the pushed commit is durable long-term
  (standard GitHub-hosting assumption, not independently re-fetched and reverified in this session).
- That `marsh@home` disk retention policy keeps `data/backups/foundation_2026-08-12/`
  indefinitely (no cleanup cron was checked for that path).
