# DIRECTOR POST-COMPACTION COMMAND SEQUENCE (dry-run verified 2026-06-26)

**For:** post-compaction me
**How to find this:** `python tools/director_kb_query.py "post-compaction commands" --source-class=notes`
**Companion:** `notes/director_POST_COMPACTION_DIGEST_2026-06-26.md` (the CONTENT)
This file is the COMMANDS to get to the content.

## STEP 1 — Heartbeat + monitor (CLAUDE.md ritual)

```bash
# Heartbeat (silences watchdog pings)
touch d:/AI/hd-instrument/data/heartbeats/research.timestamp
date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp
```

```
# Re-arm notes_monitor (Python; popup-free) per CLAUDE.md
Monitor({
  command: "python D:/AI/hd-instrument/tools/monitor_arm.py research",
  persistent: true,
  timeout_ms: 3600000,
  description: "notes_monitor research (Python; no subprocess spawns; popup-free)"
})
```

## STEP 2 — Verify continuous-ingest scheduled task alive (PowerShell, NOT bash)

```powershell
# IMPORTANT: schtasks /query in bash mangles arguments — use PowerShell
schtasks /query /tn hd_director_kb_continuous_ingest /fo LIST
```

Expected: Status=Ready, runs every 5 min via pythonw.exe (windowless).
If stale: re-register (see `feedback_session_start_ritual_*` memory for command).

## STEP 3 — Query substrate-KB for digest (load-bearing first read)

```bash
python d:/AI/hd-instrument/tools/director_kb_query.py "post-compaction digest 2026-06-26" --source-class=notes
```

Expected top-1: `notes/director_POST_COMPACTION_DIGEST_2026-06-26.md` (cosine ≥0.45). Read that file for state.

## STEP 4 — Query for today's USER directive memories

**CRITICAL:** char-trigram matching is shallow. Query with phrasing that matches the actual memory FILENAMES, not arbitrary natural language. Memory files are named with specific words; trigram features = those words.

```bash
# Standing rules from today (use filename-style phrasing):
python d:/AI/hd-instrument/tools/director_kb_query.py "substrate doesnt know anything stop testing language" --source-class=memory
python d:/AI/hd-instrument/tools/director_kb_query.py "agent spawn model 4session dead" --source-class=memory
python d:/AI/hd-instrument/tools/director_kb_query.py "stage progression 1234 dont skip" --source-class=memory
python d:/AI/hd-instrument/tools/director_kb_query.py "session start ritual master plan critical context" --source-class=memory
python d:/AI/hd-instrument/tools/director_kb_query.py "substrate as director kb dogfood" --source-class=memory
```

Each should return the matching memory file at rank 1 with cosine ≥0.40. Read each for the directive text.

## STEP 5 — Check what landed since session ended

```bash
# Recent metrics.json landings (last 2 hours)
find d:/AI/hd-instrument/data -maxdepth 2 -name 'metrics.json' -mmin -120 2>/dev/null | xargs ls -lt 2>/dev/null | head -20

# Per-cell verdict summary
for f in $(find d:/AI/hd-instrument/data -maxdepth 2 -name 'metrics.json' -mmin -120 2>/dev/null); do
  echo "=== $(basename $(dirname $f)) ==="
  python -c "import json; d=json.load(open('$f')); print('verdict:', d.get('verdict','?'))"
done
```

## STEP 6 — Query for active in-flight + recent verdicts

```bash
python d:/AI/hd-instrument/tools/director_kb_query.py "in flight running pending dispatch today" --source-class=notes
python d:/AI/hd-instrument/tools/director_kb_query.py "Wave 1.5 Wave 1.6 cortex E-tensor" --source-class=notes,metrics
python d:/AI/hd-instrument/tools/director_kb_query.py "edge importance ultrametric clustering Anchor 5" --source-class=notes,metrics
```

## STEP 7 — Cortex state (active research focus)

```bash
python d:/AI/hd-instrument/tools/director_kb_query.py "cortex content extraction META_RULE_F retrieval success magnitude coupled" --source-class=memory,notes
python d:/AI/hd-instrument/tools/director_kb_query.py "TWO_TIER generational NREM replay chain-grade" --source-class=notes,metrics
```

## STEP 8 — Substrate-KB infrastructure status

```bash
# How many facts ingested?
python d:/AI/hd-instrument/tools/director_kb_continuous_ingest.py --once --quiet 2>&1 | tail -5

# Schema source classes available for --source-class filter:
python -c "import json; d=json.load(open('d:/AI/hd-instrument/config/director_kb_schema.json')); print('source classes:', list(d.get('source_classes', {}).keys()))"
```

## KNOWN GOTCHAS (verified by dry-run 2026-06-26 ~20:50 PDT)

1. **schtasks /query mangled in bash** — Git Bash expands `/query` as a path. Use PowerShell or `//query`.
2. **Char-trigram confidence is low** (~0.20-0.50 even for strong matches). The RANKING is NOT always reliable; common words dominate. Don't trust cosine ranking for SPECIFIC document retrieval at 1M+ atoms.
3. **Substrate is degraded by language ingest** — without `--source-class` filter, WordNet entries swamp Director queries. The filter is necessary.
4. **Cosine queries are UNRELIABLE for finding specific known-filename docs** — dry-run 2026-06-26 showed that even queries containing the exact filename slug (e.g., "director POST_COMPACTION BACKUP FULL_STATE") returned the wrong file at rank 1 because common trigrams ("director", "post-compaction") matched many atoms.
5. **For specific known-filename docs: use `--filename-contains` flag** (Option A+ shipped 2026-06-26 ~20:50). Bypass cosine entirely:
   ```bash
   python tools/director_kb_query.py --filename-contains "POST_COMPACTION_BACKUP" --source-class=notes
   python tools/director_kb_query.py --filename-contains "feedback_discriminator_must_survive" --source-class=memory
   ```
6. **Cosine queries work for TOPIC EXPLORATION** ("what cells addressed cortex selectivity?") — substrate returns related atoms across the topic. Just don't trust it for "give me THIS specific doc."
7. **Filesystem grep is reliable fallback** — when in doubt: `grep -r "<term>" d:/AI/hd-instrument/notes/`.

## RECOMMENDED QUERY PATTERNS (verified working)

| Goal | Use |
|---|---|
| Find a specific known-filename doc | `--filename-contains "<slug>"` |
| Find recent USER directive memories | `--filename-contains "USER_LOCKED_2026-06-26" --source-class=memory` |
| Topic exploration (what cells / what work?) | cosine query + `--source-class=notes,metrics` |
| Find chain-grade primitives | `--filename-contains "chain_grade" --source-class=memory,notes` |
| Find post-compaction docs | `--filename-contains "POST_COMPACTION" --source-class=notes` |

## REMINDER OF WHAT YOU CAN'T DO

- Push to origin/main is harness-DENIED for research role; spawn `hdi_orchestrator` for pushes/remote dispatches
- Don't file `_to_<role>_*.md` routing notes — they're not consumed; return payload in completion reports
- Don't dispatch to GPU (overnight_queue) numpy-only cells per Fix #24
- text8 / BPC / bigram-gap are NOT relevant evals per USER pivot 2026-06-26

## STARTUP TIME ESTIMATE

Steps 1-3 (heartbeat + monitor + digest read): ~30 seconds
Steps 4-7 (USER directives + landings + cortex state queries): ~2-3 min
Step 8 (infrastructure status): ~1 min
**Total: ~5 min to recover full session context.**

Compare: pre-substrate-KB, the same recovery took ~15-20 min of grep + read across 10+ files.

---

-- Research (Opus 4.7-1M)
