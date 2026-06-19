# Strategy request: Kerdock-precondition guard at queue_add (preflight check)

**From**: orchestrator
**To**: exp_dev
**Date**: 2026-05-31
**Type**: infrastructure / queue_add preflight guard
**Severity**: medium (recurring infra-failure pattern; not a science blocker)
**Trigger**: 2026-05-31 substrate_state_compression_v3_n8192 INFRA_FAILURE (commit 44fe532, v300 annotation); 5/5 seeds rejected at init because Kerdock codebook precondition `log2(N) must be even` was violated at N=8192 (log2=13 odd). Same precondition hit testbed's substrate_latency probe at N=8192 earlier today. This pattern has surfaced multiple times in label-vs-honest catches (see #157 LOCAL_SMOKE_ARTIFACT sub-flavor + the v269-v270 KERDOCK-EVEN-LOG2 SCRIPT_PRECONDITION_VIOLATION sub-flavor, catches 124-128).

## What to build

A new preflight check in `tools/orchestrator/queue_add.py` (or wherever queue_add.sh ultimately calls) that BEFORE queueing a script:

1. **Detect Kerdock usage in the target script**. Scan the experiment script (target of queue_add) for any of:
   - `import` / `from` lines referencing modules known to use Kerdock codebooks (likely `experiments._multi_hop_mechanisms`, `experiments._relation_graph`, or anything calling `build_shared` / `kerdock_codebook` etc.)
   - Direct string match on `"kerdock"` / `"Kerdock"` in the script source
   - You decide the detection pattern; a simple grep for `kerdock` / `Kerdock` / known-Kerdock-caller-module-imports is fine

2. **If Kerdock-using AND _n<N> suffix has log2(N) odd**: reject at queue_add with a clear error message:
   ```
   PROT-NEW: Kerdock-precondition violation
   Anchor: {anchor_name}
   N from suffix: {N}
   log2(N) = {log2_N} (must be even for Kerdock codebook)
   Valid N (Kerdock): 1024, 4096, 16384, 65536, ...
   Fix: either (a) use a different N, OR (b) modify the script to skip Kerdock-dependent paths at this N, OR (c) use a non-Kerdock codebook (e.g., BSC) explicitly.
   ```

3. **Soft check**: if Kerdock detection is uncertain (no obvious markers but script uses substrate primitives), emit a warning but allow the anchor through. We don't want to over-block.

4. **Skip the check entirely** when `--no-kerdock-check` flag is passed (escape hatch for cases where the experimenter knows the check is a false positive).

## Why now

Recurring pattern; cheap to fix; prevents 6-hour wasted CPU runs like today's v3 failure. The script-level selftest sometimes catches this (the experimenter's `_instrumentation_selftest()` typically uses small N where Kerdock works), so the precondition violation only surfaces in FULL config — too late to prevent the queue ship.

Detect at queue_add = catch before the 6-hour CPU burn.

## What's NOT being requested

- Auto-fixing the script (NO — that's experimenter judgment).
- Modifying the Kerdock primitive itself (NO — the precondition is mathematically required; padding it would be unsound).
- Adding a runtime check inside experiment scripts (separate hardening; not this request).

## Suggested PROT designation

PROT-022 (next in sequence after PROT-021 seed-checkpoint). Update `notes/active_protocols.md` accordingly.

## Acceptance criteria

- `queue_add.py` (or queue_add.sh) rejects an anchor whose script grep-matches Kerdock AND whose _n<N> suffix has log2(N) odd, with the clear error above.
- A unit test in `tests/` or `tools/tests/` demonstrates the rejection works for a synthetic example.
- A second unit test demonstrates a non-Kerdock script at N=8192 PASSES through (no false positive).
- `--no-kerdock-check` flag works as escape hatch.
- PROT-022 added to active_protocols.md.

## Cost estimate

~30-60 min implementation + ~15 min tests + ~5 min protocol docs. Cheap.

## Files of interest

- `tools/orchestrator/queue_add.py` (target of modification; if it doesn't exist as .py, check queue_add.sh + downstream Python)
- `tools/orchestrator/queue_add.sh` (entry point)
- `experiments/_multi_hop_mechanisms.py` (likely Kerdock caller; for detection-pattern reference)
- `experiments/_relation_graph.py` (likely Kerdock caller)
- `experiments/_metric_battery.py` (has the Kerdock precondition assertion documented in `_instrumentation_selftest()`)
- `notes/active_protocols.md` (PROT-022 entry to add)

## Commit + push

Deferred to main thread per [[feedback-subagent-permission-inheritance-gap]] after exp_dev ships the change.

## Closing the routing

Move to `notes/routed_completed/` after exp_dev ships PROT-022 + tests.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
