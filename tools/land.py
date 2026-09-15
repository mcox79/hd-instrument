"""tools/land.py -- ONE record in, every file a landing needs written out.

The strategy session used to hand-edit 6-8 files per landing (the integration ledger, the
scorecard, the live "how we're doing" doc, the problem's SOLVED.md, sometimes the retired-claims
file, the STATUS.md handoff, the build-plan head line, and an Updates-tab post) plus a
path-limited git commit. This tool takes ONE JSON record and performs every one of those writes,
in the same order and the same shape the strategy session used by hand this week (see
notes/INTEGRATION_LEDGER.md rows dated 2026-09-15 and the STATUS.md / BUILD_PLAN_post_audit
diffs for the pattern this file copies).

Usage:
    python tools/land.py --record <path.json> [--dry-run] [--commit] [--repo <dir>]

--dry-run   prints every change as a unified diff and writes nothing.
--commit    after all the doc writes (and, in real-repo mode, the Updates-tab post and the
            parser-smoke check), makes ONE path-limited git commit of record["files"] plus the
            doc files this run actually touched.
--repo      write against a different repo root (used by the test to point at a temporary copy;
            NEVER pass this at a real landing). Whenever --repo resolves to something other than
            this file's own repo, the tool is in TEMP MODE: the Updates-tab post, the parser-smoke
            check, and the git commit are all skipped (no git, no owner_updates, no other-repo
            side effects) -- only the doc-file writes happen.

Every write is idempotent: a re-run with the same record touches nothing (each writer checks
whether its exact text is already present before adding it), so re-landing the same record is
always safe.

Plain-language fields (ledger.text, ledger.leads, scorecard_plain, livedoc_plain, status_line,
plan_head_line, integrated_mark, retired, updates.text) are written VERBATIM -- the strategy
session owns the wording; this tool only owns placement, timestamps and file mechanics.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

CO_AUTHORED_BY = "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def repo_root() -> Path:
    """This file lives at <repo>/tools/land.py."""
    return Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------------------------
# record + timestamp handling
# --------------------------------------------------------------------------------------------

def load_record(path: Path) -> dict:
    rec = json.loads(path.read_text(encoding="utf-8"))
    if "slug" not in rec:
        raise ValueError("record needs a 'slug' (the notes/problems/<slug> folder)")
    if "pri" not in rec:
        raise ValueError("record needs a 'pri'")
    return rec


def resolve_time(record: dict, now: Optional[datetime] = None) -> datetime:
    """Timestamps come from the clock unless the record gives 'time'."""
    now = now or datetime.now()
    t = record.get("time")
    if not t:
        return now
    t = str(t).strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%H:%M"):
        try:
            parsed = datetime.strptime(t, fmt)
        except ValueError:
            continue
        if fmt == "%H:%M":
            return now.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
        return parsed
    raise ValueError("record['time'] must look like 'YYYY-MM-DD HH:MM' or 'HH:MM', got %r" % t)


# --------------------------------------------------------------------------------------------
# small idempotent text-editing primitives
# --------------------------------------------------------------------------------------------

def _ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def append_line_if_absent(text: str, new_line: str) -> str:
    """Append new_line as its own physical line at EOF, unless it is already a line in text."""
    if new_line in text.splitlines():
        return text
    text = _ensure_trailing_newline(text) if text else ""
    return text + new_line + "\n"


def append_paragraph_if_absent(text: str, new_para: str) -> str:
    """Append new_para at EOF (blank line before it), unless it already occurs in text."""
    if new_para in text:
        return text
    text = _ensure_trailing_newline(text)
    if text and not text.endswith("\n\n"):
        text += "\n"
    return text + new_para + "\n"


def insert_after_heading_if_absent(text: str, heading: str, new_line: str) -> str:
    """Insert new_line as the new FIRST line right after an exact heading line, unless
    new_line already occurs somewhere in text."""
    if new_line in text.splitlines():
        return text
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln == heading:
            lines[i + 1:i + 1] = [new_line]
            out = "\n".join(lines)
            return _ensure_trailing_newline(out)
    raise ValueError("heading %r not found" % heading)


def insert_after_first_heading_block(text: str, new_line: str) -> str:
    """For BUILD_PLAN-style files: line 0 is a '# ' heading, line 1 is blank, then the
    existing top entry. Insert new_line + a blank line right after that first blank line,
    unless new_line already occurs somewhere in text."""
    if new_line in text.splitlines():
        return text
    lines = text.splitlines()
    if not lines or not lines[0].startswith("#"):
        raise ValueError("expected the file to start with a '# ' heading")
    blank_i = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "":
            blank_i = i
            break
    if blank_i is None:
        # no blank line yet (e.g. a brand-new file with just the heading) -- add one
        lines.append("")
        blank_i = len(lines) - 1
    insert_at = blank_i + 1
    lines[insert_at:insert_at] = [new_line, ""]
    out = "\n".join(lines)
    return _ensure_trailing_newline(out)


_DATED_BLOCK_RE = re.compile(r"^\*\*\d")


def prepend_to_first_dated_block(text: str, new_text: str) -> str:
    """STATUS.md is a sequence of blank-line-separated blocks; the pinned callout at the very
    top does not start with a digit right after '**' (e.g. '**LOCATED, NOT YET FIXED...'), the
    first real dated block does (e.g. '**07:33 (09-14): ...'). Prepend new_text to the very
    start of that first dated block, unless it is already there."""
    blocks = text.split("\n\n")
    for i, block in enumerate(blocks):
        if _DATED_BLOCK_RE.match(block.lstrip()):
            if block.startswith(new_text):
                return text
            blocks[i] = new_text + " " + block
            return "\n\n".join(blocks)
    raise ValueError("no dated block (a paragraph starting \"**<digit>\") found in STATUS.md")


# --------------------------------------------------------------------------------------------
# one Change per target file
# --------------------------------------------------------------------------------------------

@dataclass
class Change:
    rel_path: str
    apply: Callable[[str], str]
    note: str = ""


def build_changes(record: dict, when: datetime) -> list[Change]:
    date_iso = when.strftime("%Y-%m-%d")
    time_hm = when.strftime("%H:%M")
    day_no_zero = str(when.day)
    mon_abbr = when.strftime("%b")

    changes: list[Change] = []

    # 1. INTEGRATION_LEDGER.md -- append one pipe-table row at EOF.
    ledger = record["ledger"]
    ledger_row = "| %s %s local | %s | %s | %s |" % (
        date_iso, time_hm, ledger["text"], ledger.get("status", ""), ledger.get("leads", ""),
    )
    changes.append(Change(
        "notes/INTEGRATION_LEDGER.md",
        lambda t: append_line_if_absent(t, ledger_row),
        "append the landing's ledger row",
    ))

    # 2. SCORECARD.md -- new first bullet under '## WHAT CHANGED LATELY'.
    scorecard_bullet = "- **%s %s, %s.** %s" % (day_no_zero, mon_abbr, time_hm, record["scorecard_plain"])
    changes.append(Change(
        "notes/SCORECARD.md",
        lambda t: insert_after_heading_if_absent(t, "## WHAT CHANGED LATELY", scorecard_bullet),
        "new scorecard bullet",
    ))

    # 3. HOW_WE_ARE_DOING.md -- new first bullet under '## WHAT MOVED THIS WEEK'.
    livedoc_bullet = "- %s -- %s" % (date_iso, record["livedoc_plain"])
    changes.append(Change(
        "notes/HOW_WE_ARE_DOING.md",
        lambda t: insert_after_heading_if_absent(t, "## WHAT MOVED THIS WEEK", livedoc_bullet),
        "new live-doc bullet",
    ))

    # 4. notes/problems/<slug>/SOLVED.md -- append the INTEGRATED mark paragraph.
    integrated_para = "INTEGRATED_BY_STRATEGY %s %s local -- %s" % (
        date_iso, time_hm, record["integrated_mark"],
    )
    changes.append(Change(
        "notes/problems/%s/SOLVED.md" % record["slug"],
        lambda t: append_paragraph_if_absent(t, integrated_para),
        "append the INTEGRATED_BY_STRATEGY mark",
    ))

    # 5. reference_retired_claims_never_requote.md -- optional.
    if record.get("retired"):
        retired_line = "- %s %s: %s" % (date_iso, time_hm, record["retired"])
        changes.append(Change(
            "notes/reference_retired_claims_never_requote.md",
            lambda t: append_line_if_absent(t, retired_line),
            "append a retired-claim line",
        ))

    # 6. STATUS.md -- prepend the (fully-formed, verbatim) status line to the top of the
    #    first dated block.
    status_line = record["status_line"]
    changes.append(Change(
        "notes/STATUS.md",
        lambda t: prepend_to_first_dated_block(t, status_line),
        "prepend the STATUS line",
    ))

    # 7. BUILD_PLAN_post_audit_2026-08-19.md -- insert the (fully-formed, verbatim) plan-head
    #    line right after the file's first heading block.
    plan_head_line = record["plan_head_line"]
    changes.append(Change(
        "notes/BUILD_PLAN_post_audit_2026-08-19.md",
        lambda t: insert_after_first_heading_block(t, plan_head_line),
        "insert the plan head line",
    ))

    return changes


# --------------------------------------------------------------------------------------------
# apply / dry-run
# --------------------------------------------------------------------------------------------

@dataclass
class Result:
    changed_files: list[str] = field(default_factory=list)
    unchanged_files: list[str] = field(default_factory=list)


def run_changes(repo: Path, changes: list[Change], dry_run: bool) -> Result:
    result = Result()
    for ch in changes:
        target = repo / ch.rel_path
        old_text = target.read_text(encoding="utf-8") if target.is_file() else ""
        new_text = ch.apply(old_text)
        if new_text == old_text:
            result.unchanged_files.append(ch.rel_path)
            print("[land] %-55s  no change (already present) -- %s" % (ch.rel_path, ch.note))
            continue
        result.changed_files.append(ch.rel_path)
        if dry_run:
            print("[land] --- diff: %s (%s) ---" % (ch.rel_path, ch.note))
            import difflib
            diff = difflib.unified_diff(
                old_text.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile="a/%s" % ch.rel_path, tofile="b/%s" % ch.rel_path,
            )
            sys.stdout.writelines(diff)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(new_text, encoding="utf-8", newline="\n")
            print("[land] %-55s  written -- %s" % (ch.rel_path, ch.note))
    return result


# --------------------------------------------------------------------------------------------
# real-repo-only side effects: Updates-tab post, parser-smoke, git commit
# --------------------------------------------------------------------------------------------

def is_temp_mode(repo: Path) -> bool:
    return repo.resolve() != repo_root().resolve()


def post_owner_update(repo: Path, record: dict) -> None:
    upd = record.get("updates")
    if not upd:
        return
    cmd = [sys.executable, str(repo / "tools" / "owner_updates.py"), "post", upd["kind"], upd["text"]]
    print("[land] $ %s" % " ".join(cmd))
    subprocess.run(cmd, cwd=str(repo), check=True)


def parser_smoke(repo: Path) -> None:
    cmd = [sys.executable, str(repo / "tools" / "scorecard_gui.py"), "--parser-smoke"]
    print("[land] $ %s" % " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True)
    print(proc.stdout)
    if proc.returncode != 0 or "PASS" not in proc.stdout:
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError("tools/scorecard_gui.py --parser-smoke did not print PASS")


def git_commit(repo: Path, record: dict, changed_files: list[str]) -> None:
    files = list(dict.fromkeys(list(record.get("files", [])) + changed_files))
    if not files:
        print("[land] nothing to commit")
        return
    message = record["commit_title"].rstrip() + "\n\n" + CO_AUTHORED_BY + "\n"
    add_cmd = ["git", "add", "-f"] + files
    print("[land] $ %s" % " ".join(add_cmd))
    subprocess.run(add_cmd, cwd=str(repo), check=True)
    commit_cmd = ["git", "commit", "-m", message, "--"] + files
    print("[land] $ git commit -m <message> -- %s" % " ".join(files))
    subprocess.run(commit_cmd, cwd=str(repo), check=True)


# --------------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--record", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--repo", type=Path, default=None)
    args = ap.parse_args(argv)

    repo = (args.repo.resolve() if args.repo else repo_root())
    record = load_record(args.record)
    when = resolve_time(record)
    temp = is_temp_mode(repo)

    print("[land] pri %s / %s -- repo=%s%s" % (
        record["pri"], record["slug"], repo, "  [TEMP MODE]" if temp else "",
    ))
    if record.get("witness_smoke") is not None:
        print("[land] witness_smoke=%r (informational; this tool never runs witnesses or a board)"
              % record["witness_smoke"])

    changes = build_changes(record, when)
    result = run_changes(repo, changes, dry_run=args.dry_run)

    if args.dry_run:
        print("[land] DRY RUN -- nothing written")
        return 0

    if temp:
        print("[land] TEMP MODE (--repo points away from this tool's own repo): "
              "skipping the Updates-tab post, the parser-smoke check, and any git commit")
        return 0

    post_owner_update(repo, record)
    parser_smoke(repo)

    if args.commit:
        git_commit(repo, record, result.changed_files)
    else:
        print("[land] --commit not given -- doc files written, nothing committed")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
