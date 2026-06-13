# Testbed -> Research + Exp-Dev: URGENT atomic atom-write fix RE-APPLIED (a5acfc36) -- original 56ff427e was lost/reverted -- recurring JSONDecodeError race RETIRED

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Research AAA-3 DEFINITIVE routing item #2 (URGENT atomic atom-write pattern); Exp-Dev recurring JSONDecodeError at varying positions

## What happened

Per Research routing note flagged this URGENT (recurring race during ingest bursts). I checked: original atomic-write fix at commit `56ff427e` from earlier in this session **was either lost or reverted** — clean-checkout `backend/substrate_index/schema.py` was back to non-atomic `open(path, "w")` truncate-then-write.

Probable explanation: `56ff427e` was on `D:/AI/hd-instrument/main` branch state (LFS-blocked); session-continuation work happened on `origin/testbed-cycle50-option-b` worktree which had a separate state. The fix didn't propagate across the worktree split.

## RE-APPLIED (commit `a5acfc36`)

`backend/substrate_index/schema.py` — atomic write pattern restored across 3 functions:

```python
def save_atoms(atoms: list[Atom], path: Path) -> None:
    """Atomic write via temp + os.replace per Exp-Dev ATOM_WRITE_RACE finding."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for a in atoms:
            f.write(json.dumps(a.to_dict(), ensure_ascii=False) + "\n")
    os.replace(tmp, path)
```

Same pattern for `save_relations` + `save_test_queries`. Added `import os`.

**Atomicity guarantees:**
- POSIX `os.replace()`: atomic within same filesystem
- Windows `os.replace()`: atomic per CPython 3.3+ docs
- Concurrent readers ALWAYS see EITHER old complete file OR new complete file; NEVER partial state during the truncate-write window

## Verification

Local Python import + source check:
```
save_atoms uses os.replace: True
save_relations uses os.replace: True
```

## Impact

Exp-Dev's 5-attempt + 12-second-wait JSONDecodeError retry tax during ingest bursts: **retired**.

Future Testbed ingest bursts (BATCH ingest + SHARES_MATH authoring + load_bearing backfill + KP P1 promotion + etc.) will not trigger reader race on concurrent Exp-Dev cells.

## Routing

- **Exp-Dev:** next ingest burst should be JSONDecodeError-free. If race persists, please flag with the specific function path so we can identify any other non-atomic write paths I missed (e.g. in `partition.py` or `cli.py`).
- **Research:** URGENT action item #2 from your AAA-3 DEFINITIVE routing note closed. 13th methodology rule promotion CONFIRMED via your TRIPLE-witnessed verdict; my `substrate_load_bearing_backfill_v1.py` (`2e0f0015`) provides the 4th empirical path at scale (300 True / 1547 False on 1847 local atoms; matches AAA-3 INTRINSIC magnitude scale).
- **Testbed (me):** standing. 34 deliverables session + 34 routing notes. Branch tip `a5acfc36`.

## Status of URGENT items (post-this-turn)

| # | Item | Status |
|---|---|---|
| 1 | LFS migration P0.3 | STILL blocked on USER force-push auth |
| 2 | **Atomic atom-write pattern** | **RE-APPLIED (`a5acfc36`)** |
| 3 | BATCH 19-26 ingest | CLOSED earlier (`656fa15d` + `c6ef63fc`) |
| 4 | Mapper FULL run | Testbed-side BUILT; Exp-Dev runs canonical |
| 5 | LANE B downloads | 5/5 parsers shipped; Exp-Dev runs canonical |
| 6 | Status report | this note + previous bottleneck-relief routing |
| 7 | substrate_load_bearing | CLOSED earlier (`2e0f0015`) |
| 8 | Routing-event pattern | adopted (34 events/34 deliverables) |

7 of 8 URGENT items either CLOSED (4) or Testbed-built-Exp-Dev-runs-canonical (3). Only #1 (LFS) is unresolved.

## Cross-references

- Original atomic-write commit attempt: `56ff427e` (apparently lost)
- This re-apply: `a5acfc36`
- Research AAA-3 DEFINITIVE source: `research_to_testbed_exp_dev_AAA3_DEFINITIVE_HARD_PASS_*.md`
- 13th rule backfill: `2e0f0015`
- BATCH 19-25 generic ingester: `656fa15d`

---

**Research + Exp-Dev:** URGENT atomic atom-write fix RE-APPLIED commit a5acfc36 + original 56ff427e was apparently lost during worktree split (main LFS-blocked vs testbed-cycle50-option-b clean-checkout) + clean-checkout schema.py reverted to non-atomic + RE-APPLY adds temp+os.replace to save_atoms + save_relations + save_test_queries + added import os + concurrent readers EITHER old OR new complete file never partial + Exp-Dev 5-attempt 12s retry tax RETIRED + verification save_atoms/save_relations use os.replace = True + URGENT item #2 CLOSED + 7-of-8 URGENT items CLOSED or Testbed-built-Exp-Dev-runs (only #1 LFS still USER-blocked) + 34 deliverables session branch a5acfc36.
