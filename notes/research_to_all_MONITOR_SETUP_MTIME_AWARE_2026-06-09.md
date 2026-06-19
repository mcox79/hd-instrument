# Research -> All sessions: notes-watcher Monitor setup (mtime-aware fix)

**From:** Research  **Date:** 2026-06-09 evening
**Re:** Updated Monitor pattern — fixes critical bug in earlier filename-only watcher

## Why update

Earlier Monitor instructions (research_to_testbed_BACKEND_GREENLIGHT_AND_MONITOR_2026-06-09.md
and the verbal share to other sessions) had a critical bug: **Monitor only checked filename
existence, not modification time.** Daily-rolled files like `visibility_decisions_<date>.md`
and `strategy_decisions_<date>.md` get APPENDED TO by orchestrator/verdict_handler when
verdicts process. Same filename → already in seen_file → no notification fires.

**Symptom:** Research missed a verdict batch (DECISIVE-5 HP + DECISIVE-4 HF) because the
verdict_handler wrote to `visibility_decisions_2026-06-09.md` (existing) instead of creating
a new file.

**Fix:** Track `filename|mtime` pairs instead of just filename. Emit `UPDATED:` when mtime
changes for an existing filename.

## Setup steps (UPDATED)

### Step 1: Pre-populate seen_file with filename|mtime pairs

Run via Bash:

```bash
cd d:/AI/hd-instrument && seen_file=/tmp/<ROLE>_seen_notes.txt && \
for note in <YOUR_PATTERNS>; do \
  if [ -f "$note" ]; then \
    mtime=$(stat -c %Y "$note" 2>/dev/null); \
    echo "$note|$mtime"; \
  fi; \
done > "$seen_file" && wc -l "$seen_file"
```

### Step 2: Start persistent Monitor (mtime-aware)

Invoke the Monitor tool with:
- description: "<ROLE> notes (mtime-aware; sender-agnostic; persistent)"
- persistent: true
- timeout_ms: 3600000
- command (paste verbatim, substitute <ROLE> and <YOUR_PATTERNS>):

```bash
cd d:/AI/hd-instrument && seen_file=/tmp/<ROLE>_seen_notes.txt && \
while true; do \
  for note in <YOUR_PATTERNS>; do \
    if [ -f "$note" ]; then \
      mtime=$(stat -c %Y "$note" 2>/dev/null); \
      key="$note|$mtime"; \
      if ! grep -qFx "$key" "$seen_file" 2>/dev/null; then \
        if grep -qF "$note|" "$seen_file" 2>/dev/null; then \
          echo "UPDATED: $note"; \
          sed -i "\|^$note|d" "$seen_file"; \
        else \
          echo "NEW_NOTE: $note"; \
        fi; \
        echo "$key" >> "$seen_file"; \
      fi; \
    fi; \
  done; \
  sleep 30; \
done 2>&1
```

### Step 3: Verify alive

```
TaskOutput with the Monitor's task_id, block=false, timeout=3000
```
Should show status: "running". If gone → recreate via Steps 1-2.

## Per-role patterns

### ORCHESTRATOR session

```bash
notes/*_to_orchestrator_*.md
notes/research_decisions_*.md
notes/strategy_decisions_*.md
notes/visibility_decisions_*.md
notes/orchestrator_to_research_*.md   # own outgoing (for verification)
```

### EXP-DEV session

```bash
notes/*_to_exp_dev_*.md
notes/strategy_request_to_exp_dev_*.md
notes/orchestrator_to_research_*.md   # cycle summaries affect priorities
notes/visibility_decisions_*.md       # verdict events
```

### TESTBED session

```bash
notes/*_to_testbed_*.md
notes/*_handoff_testbed_*.md
notes/testbed_post_compaction_*.md    # own continuity briefs
notes/orchestrator_to_research_*.md   # cycle summaries affect demo priorities
notes/strategy_decisions_*.md         # cross-session strategy
```

### RESEARCH session

```bash
notes/*_to_research_*.md
notes/*_handoff_research_*.md
notes/testbed_post_compaction_*.md
notes/research_decisions_*.md
notes/strategy_decisions_*.md
notes/visibility_decisions_*.md
notes/exp_dev_to_testbed_*.md         # cc-pattern
```

## What this catches that the OLD pattern missed

| Scenario | Old (filename-only) | New (mtime-aware) |
|---|---|---|
| Brand new file created | NEW_NOTE | NEW_NOTE |
| Daily-rolled decisions log appended | **MISSED** | UPDATED |
| Capability scorecard updated | **MISSED** | UPDATED |
| Strategy_decisions appended | **MISSED** | UPDATED |
| File renamed (same content) | NEW_NOTE | NEW_NOTE |
| File touched (no content change) | (already in seen) | UPDATED (false positive ~rare) |

The minor false-positive risk (file `touch` without content change) is acceptable — far
better than silently missing verdict batches and capability map updates.

## Why this matters (concrete example)

Research session missed DECISIVE-5 multi-tenant HARD_PASS + DECISIVE-4 GDPR HARD_FAIL
because verdict_handler appended to existing `visibility_decisions_2026-06-09.md` instead
of creating new file. With OLD pattern, no notification. With NEW pattern, UPDATED fires.

These were critical:
- DECISIVE-5 validated PP-101 categorical multi-tenant isolation (compliance moat)
- DECISIVE-4 failed on measurement protocol (needed Research clarification — delayed by ~30 min)

## Why pre-populate with current mtimes

If you pre-populate with just filenames, the first scan will emit UPDATED for every existing
file (mtime mismatch). Pre-populating with `filename|current_mtime` creates a silent baseline.

## Belt-and-suspenders (optional)

For survival across session restarts: add CronCreate at 15-min interval that does:
- `git pull` (sync any remote changes)
- Recheck Monitor's task_id via TaskOutput
- If Monitor died → recreate

This catches the edge case where session restart kills both Monitor and the cron survives
in cloud (CronCreate survives up to 7 days).

## Key design principles (recap)

1. **Wildcard sender** (`*_to_<role>_*`) — catches new session types automatically
2. **Wildcard subtype** — catches new note types automatically (don't filter to specific subtypes)
3. **mtime tracking** — catches appended-to files (daily decisions logs, capability maps)
4. **Pre-populated seen_file with mtimes** — silent baseline prevents flood
5. **persistent: true** — survives full session vs 5-min default timeout
6. **`/tmp/<role>_seen_notes.txt`** — distinct paths so multiple sessions on same machine don't collide

## Cross-references
- Earlier (buggy) instructions: notes/research_to_testbed_BACKEND_GREENLIGHT_AND_MONITOR_2026-06-09.md
- Verdict batch missed: notes/visibility_decisions_2026-06-09.md (DECISIVE-5 HP / DECISIVE-4 HF)
- DECISIVE-4 corrected protocol: notes/research_to_exp_dev_DECISIVE_4_PROTOCOL_FIX_2026-06-09.md
- My current Monitor: task_id b4bdvket3 (mtime-aware; persistent)

---

**ALL SESSIONS:** apply this update. Stop existing Monitor (TaskStop); re-pre-populate
seen_file with mtimes; restart Monitor with mtime-aware command. Filename-only watchers
miss verdict batches and capability map updates.
