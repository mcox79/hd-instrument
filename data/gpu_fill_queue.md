# GPU fill queue (standing; pre-validated quick cells for GPU idle gaps)

**Purpose:** when GPU goes idle and a cell-author would take minutes to pre-dispatch (smoke + Fix #17 timing), fire one of these PRE-VALIDATED cells instead. Wall budget ≤10min each. Updated when GPU-runnable cells land or revivals queue up.

## Invariant

Every entry here must already have:
1. Cell file on disk + committed to origin/main
2. Recent smoke that PASSED on GPU (within last 30 days)
3. GPU util verified ≥50% in smoke (Fix #24)
4. Pre-reg note on disk
5. Wall estimate ≤10min total (3 seeds)

If any of those go stale, REMOVE the entry rather than firing it blindly.

## Active candidates (none yet pre-validated)

Authoring pending — populate as cells qualify. Don't add aspirational entries.

## Pipeline notes

When firing from this queue:
- Run `python tools/predispatch_check.py <anchor>` first (Fix #26)
- Re-verify cell + smoke + prereg paths still exist
- Dispatch via standard handoff file or queue_add.sh
- Update this file's wall-clock fired/landed log below

## Fired/landed log

| Anchor | Wall (s) | Verdict | Notes |
|---|---|---|---|
| (none yet) | | | |
