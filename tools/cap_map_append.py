"""cap_map_append.py -- Targeted cap_map sub-property appends + version bump.

PURPOSE
-------
For HP-dominant verdict batches, the common cap_map mutation is:
  1. Append 1-N sub-property bullets to existing capability rows
  2. Bump the version header
That's it. No row creation, no row deletion, no BAND-LIFT mechanics.

Today verdict_handler reads the full cap_map (~675KB / 7700 lines) into context
to do this. That's a heavy token cost for what's structurally a few-line edit.

This helper takes a list of pending appends and applies them with surgical
diff-style edits — no full read into LLM context, no parse, no rewrite.

MEDIUM-RISK ROLLOUT (per efficiency_rollout_2026-06-02.md item #5)
------------------------------------------------------------------
First 3 runs: SHADOW MODE.
  1. verdict_handler still does the full read/write as today (authoritative path).
  2. ALSO emits `data/cap_map_pending_appends.jsonl` with what it would have
     appended.
  3. THIS HELPER applies the pending appends to a *shadow copy* of cap_map.
  4. After verdict_handler commits, compare authoritative cap_map vs shadow.
  5. If diff is clean for 3 cycles in a row, promote: verdict_handler stops
     doing full read/write and this helper becomes the authoritative path.

USAGE
-----
    # Verdict_handler emits this file with a list of pending appends:
    #   data/cap_map_pending_appends.jsonl
    # One JSONL entry per pending append, schema:
    #   {"row_match": str (regex matching a row's header line),
    #    "subprop_marker": str (regex matching the "Sub-properties:" or similar
    #      line WITHIN the row's section),
    #    "bullet": str (new bullet text; will be prefixed with "  - "),
    #    "version_target": str (e.g. "v347")}

    python tools/cap_map_append.py \\
        --pending data/cap_map_pending_appends.jsonl \\
        --cap-map notes/substrate_capability_map.md \\
        [--shadow data/substrate_capability_map.shadow.md]   # shadow mode
        [--apply]                                            # without --apply: dry-run

GUARANTEES
----------
- Atomic write (.tmp + rename)
- Refuses to apply if pending file has structural problems
- Backup cap_map to data/cap_map_backups/<timestamp>.md before write
- No edits outside the target row's section
- Version bump: replaces single "cap_map v<N>" line in header
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_CAP_MAP = REPO / "notes" / "substrate_capability_map.md"
DEFAULT_PENDING = REPO / "data" / "cap_map_pending_appends.jsonl"
BACKUPS_DIR = REPO / "data" / "cap_map_backups"


def fail(msg: str, exit_code: int = 1) -> None:
    print(f"GATE_FAIL: {msg}", file=sys.stderr)
    sys.exit(exit_code)


def load_pending(pending_path: Path) -> list[dict]:
    if not pending_path.exists():
        return []
    entries = []
    for i, line in enumerate(pending_path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            fail(f"pending file line {i} not valid JSON: {e}")
        for required in ("row_match", "subprop_marker", "bullet", "version_target"):
            if required not in obj:
                fail(f"pending file line {i} missing field '{required}'")
        entries.append(obj)
    return entries


def find_row_section(lines: list[str], row_match: str) -> tuple[int, int]:
    """Find start and end line indices of the row matched by row_match.

    Row sections are delimited by markdown headers ##, ###, or table rows.
    Returns (start_idx, end_idx_exclusive).
    """
    pat = re.compile(row_match)
    start = None
    for i, line in enumerate(lines):
        if pat.search(line):
            start = i
            break
    if start is None:
        return (-1, -1)
    # End: next markdown header at same-or-higher level, or EOF
    # Heuristic: if start line begins with "##", scan for next "##"
    start_header_level = 0
    m = re.match(r"^(#+)", lines[start])
    if m:
        start_header_level = len(m.group(1))
    end = len(lines)
    if start_header_level > 0:
        for i in range(start + 1, len(lines)):
            m2 = re.match(r"^(#+)", lines[i])
            if m2 and len(m2.group(1)) <= start_header_level:
                end = i
                break
    else:
        # Non-header anchor: end at next blank line followed by header, or 50 lines
        end = min(start + 50, len(lines))
    return (start, end)


def append_bullet(
    lines: list[str], start: int, end: int, subprop_marker: str, bullet: str
) -> bool:
    """Append `  - {bullet}` immediately after the line matching subprop_marker
    within [start, end). Returns True on success.
    """
    pat = re.compile(subprop_marker)
    for i in range(start, end):
        if pat.search(lines[i]):
            insert_at = i + 1
            # Skip past existing bullets
            while insert_at < end and lines[insert_at].lstrip().startswith("-"):
                insert_at += 1
            lines.insert(insert_at, f"  - {bullet}")
            return True
    return False


def bump_version(lines: list[str], version_target: str) -> bool:
    """Replace the cap_map version on its header line.

    Targets a line of form: 'cap_map v<NUMBER>' or '# ... v<NUMBER>' or
    'capability map v<NUMBER>'. Replaces the version-token with version_target.
    """
    pat = re.compile(r"(cap[_ ]?map.*?|capability map.*?)v\d+", re.IGNORECASE)
    for i, line in enumerate(lines):
        if pat.search(line):
            lines[i] = pat.sub(rf"\g<1>{version_target}", line)
            return True
    return False


def main() -> None:
    p = argparse.ArgumentParser(description="Append sub-properties + bump cap_map version")
    p.add_argument("--pending", type=Path, default=DEFAULT_PENDING,
                   help="Pending appends JSONL file")
    p.add_argument("--cap-map", type=Path, default=DEFAULT_CAP_MAP,
                   help="cap_map markdown file to edit")
    p.add_argument("--shadow", type=Path, default=None,
                   help="Shadow mode: write to this path instead of cap-map")
    p.add_argument("--apply", action="store_true",
                   help="Without --apply, do a dry-run (no write)")
    args = p.parse_args()

    if not args.cap_map.exists():
        fail(f"cap_map not found: {args.cap_map}")

    entries = load_pending(args.pending)
    if not entries:
        print(f"[cap_map_append] no pending entries in {args.pending}; nothing to do")
        return

    lines = args.cap_map.read_text(encoding="utf-8").splitlines()
    n_applied = 0
    n_failed = 0
    applied_summary = []

    for entry in entries:
        start, end = find_row_section(lines, entry["row_match"])
        if start < 0:
            print(f"[cap_map_append] SKIP: no row matched '{entry['row_match']}'",
                  file=sys.stderr)
            n_failed += 1
            continue
        ok = append_bullet(lines, start, end, entry["subprop_marker"], entry["bullet"])
        if not ok:
            print(f"[cap_map_append] SKIP: subprop marker '{entry['subprop_marker']}' "
                  f"not found in row [{start},{end})", file=sys.stderr)
            n_failed += 1
            continue
        n_applied += 1
        applied_summary.append((entry["row_match"], entry["bullet"][:60]))

    # Version bump: use highest version_target seen
    target_versions = sorted({e["version_target"] for e in entries})
    if not target_versions:
        fail("no version_target supplied")
    final_version = target_versions[-1]
    if not bump_version(lines, final_version):
        fail(f"could not find version line to bump to {final_version}")

    out_path = args.shadow if args.shadow else args.cap_map
    if not args.apply:
        print(f"[cap_map_append] DRY-RUN: {n_applied} appends OK, {n_failed} failed; "
              f"target={out_path}; version -> {final_version}")
        for row, bullet in applied_summary:
            print(f"  + {row}: {bullet}...")
        return

    # Real apply: backup + atomic write
    if not args.shadow:
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        backup_path = BACKUPS_DIR / f"cap_map_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.md"
        shutil.copy2(args.cap_map, backup_path)
        print(f"[cap_map_append] backup -> {backup_path}")

    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    tmp_path.replace(out_path)

    # Clear pending file on success (only if writing to authoritative cap_map)
    if not args.shadow and args.pending.exists():
        args.pending.unlink()

    print(f"[cap_map_append] APPLIED: {n_applied} bullets + version -> {final_version}; "
          f"wrote {out_path}")


if __name__ == "__main__":
    main()
