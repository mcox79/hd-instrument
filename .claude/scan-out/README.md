# .claude/scan-out/ -- fragment convention

Each fire-and-forget scan agent (literature scan, codebase survey, "read a bunch of things and
report") writes its FULL findings here as one JSON file, then returns ONE LINE to whoever
dispatched it ("wrote 41 findings."). The dispatcher's context absorbs a dozen short strings
instead of a dozen 2000-4000 word reports. Full detail is not lost -- it is on disk, one file
per scan, and `python tools/scan_out_collect.py` reads the directory and assembles every
fragment into a single note.

**Nothing in this directory except this README is durable or tracked.** `*.json` fragments are
gitignored (see `.gitignore`) and are working data for the current session/night, not a
permanent record -- if a finding needs to survive, promote it into a `notes/*.md` write-up the
same way a scratch script gets promoted into `tools/` (see `scratch/README.md` for the parallel
convention). Retention: `python tools/scan_out_collect.py --clear --yes [--older-than-days N]`.

## Schema (v1)

One JSON object per file, filename `<agent-name-or-slug>.json`:

```json
{
  "agent": "scan",
  "task": "one-line description of what was scanned",
  "timestamp": "2026-08-14T23:05:00Z",
  "findings": [
    {
      "claim": "the finding, one sentence if possible",
      "evidence": "ESTABLISHED",
      "source": "optional: file path / URL / commit hash",
      "detail": "optional: supporting quote, number, context"
    }
  ],
  "summary": "optional 1-3 sentence rollup"
}
```

Required: `agent`, `task`, `timestamp` (UTC ISO-8601), `findings` (list, may be empty). Each
finding requires `claim` and `evidence`. `source` / `detail` / top-level `summary` are optional.

## Evidence tags (this project's literature discipline, applied to every claim)

| tag | meaning |
|---|---|
| `ESTABLISHED` | multiple independent sources, or independently reproduced this session |
| `CONTESTED` | sources disagree, or the claim is argued but not settled |
| `SINGLE-STUDY` | one source, not independently corroborated |
| `FAILED-REPLICATION` | an attempt to reproduce/re-verify the claim did NOT hold |

A finding with a missing or off-list `evidence` value is not rejected by the collector -- it is
assembled and flagged inline (`[UNTAGGED]` / `[INVALID-TAG:<value>]`) so the omission is visible
to the reader of the assembled note rather than silently dropped. The write-time discipline
(always tag) is enforced by the scan agent's brief and by `.claude/agents/scan.md`, not by a
hard schema rejection here -- a scan that forgot to tag one claim should still get its other 40
findings through.

## Usage

```
python tools/scan_out_collect.py                    # assemble every fragment, print to stdout
python tools/scan_out_collect.py --out notes/x.md    # assemble, write to a file
python tools/scan_out_collect.py --clear             # dry-run retention
python tools/scan_out_collect.py --clear --yes --older-than-days 3
python tools/scan_out_collect.py --self-test         # guard + schema self-test
```

Full docstring with the guard-pattern rationale: `tools/scan_out_collect.py` (module docstring).
Landed 2026-08-14 per owner directive on subagent fan-out; see
`notes/subagent_fanout_pattern_2026-08-14.md` for the full design + verified/unverified claims.
