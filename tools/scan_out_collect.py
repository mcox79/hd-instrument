#!/usr/bin/env python
"""Assemble .claude/scan-out/ fragments into one note; retire the fragment convention's litter.

WHY THIS EXISTS (2026-08-14, notes/agent_usage_practices_audit_2026-08-14.md): background scan
agents (literature scans, codebase surveys) were returning 2000-4000 word reports straight into
the main conversation -- the same attention tax as a same-turn-continuation violation, arriving
by a slower route. The fix: each scan writes its FULL findings to a fragment file here and
returns ONE LINE ("wrote 41 findings.") to whoever dispatched it. This tool reads the directory
and assembles the fragments into a single note, so the full detail still exists on disk and is
still readable in one pass -- it just never floods the dispatcher's context token-by-token.

FRAGMENT SCHEMA (v1), one JSON object per file, filename `<agent-name-or-slug>.json`:

{
  "agent":     str,   REQUIRED -- the dispatched agent's name/subagent_type (e.g. "scan",
                       "hdi_research"). Identifies who wrote this fragment.
  "task":      str,   REQUIRED -- one-line description of what was scanned/asked.
  "timestamp": str,   REQUIRED -- UTC ISO-8601 ("2026-08-14T23:05:00Z"), when the scan
                       finished (not when the file was written -- a retried write should keep
                       the original scan's completion time if the finding didn't change).
  "findings": [       REQUIRED, list (may be empty -- an empty scan is still a valid report).
    {
      "claim":    str,           REQUIRED -- the finding itself, one sentence if possible.
      "evidence": str,           REQUIRED -- one of the four literature-discipline tags below.
      "source":   str,           OPTIONAL -- file path / URL / commit hash the claim rests on.
      "detail":   str            OPTIONAL -- supporting detail, quotes, numbers.
    }, ...
  ],
  "summary":   str    OPTIONAL -- 1-3 sentence rollup, if the scan has one worth surfacing
                       before a reader opens the assembled note.
}

Evidence tags (this project's literature discipline, applied to every claim, not just lit-scan
claims -- a codebase-scan claim like "no caller sets this flag" gets the same rigor):
  ESTABLISHED        -- multiple independent sources / directly reproduced this session.
  CONTESTED           -- sources disagree, or the claim is argued but not settled.
  SINGLE-STUDY         -- one source, not independently corroborated.
  FAILED-REPLICATION  -- an attempt to reproduce/re-verify the claim did NOT hold.

A fragment missing `evidence` on a finding, or using a tag outside the four above, is not
rejected (the collector still assembles it) but is flagged inline as `[UNTAGGED]` /
`[INVALID-TAG:<value>]` in the assembled note -- the write-time discipline is enforced by
convention (spelled out in the scan agent's brief and in `.claude/agents/scan.md`), the
read-time discipline is enforced by making the omission visible rather than silently dropping
the tag column.

USAGE
  python tools/scan_out_collect.py                    # assemble, print to stdout
  python tools/scan_out_collect.py --out notes/x.md    # assemble, write to a file
  python tools/scan_out_collect.py --clear             # dry-run: list fragments that would go
  python tools/scan_out_collect.py --clear --yes       # actually delete assembled fragments
  python tools/scan_out_collect.py --clear --yes --older-than-days 3   # retention window
  python tools/scan_out_collect.py --self-test

GUARD (same pattern as tools/clear_scratch.py, deliberately copied not reinvented): every
delete target is resolved to a real path and checked to be strictly INSIDE the canonical
scan-out root, and the root itself is never a valid delete target. `--_disable_guard` exists
only so --self-test can prove the guard is load-bearing (the disabled-guard run must fail the
same assertions the enabled run passes).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCAN_OUT = REPO_ROOT / ".claude" / "scan-out"

VALID_TAGS = {"ESTABLISHED", "CONTESTED", "SINGLE-STUDY", "FAILED-REPLICATION"}
REQUIRED_FRAGMENT_KEYS = ("agent", "task", "timestamp", "findings")
REQUIRED_FINDING_KEYS = ("claim", "evidence")

# Set to False by --_disable_guard (self-test only) to prove the guard is load-bearing.
GUARD_ENABLED = True


class GuardViolation(Exception):
    """Raised when a delete target resolves outside the scan-out root."""


def _real(p: Path) -> Path:
    """Fully-resolved absolute path with symlinks followed."""
    return Path(os.path.realpath(str(p)))


def assert_under_root(target: Path, root: Path) -> None:
    """Refuse any target whose real path is not strictly inside the real scan-out root."""
    if not GUARD_ENABLED:
        return
    rt, rr = _real(target), _real(root)
    if rt == rr:
        raise GuardViolation(f"refusing to remove the scan-out root itself: {rt}")
    try:
        rt.relative_to(rr)
    except ValueError:
        raise GuardViolation(f"refusing target outside scan-out root: {rt} (root={rr})") from None


# ---------------------------------------------------------------------------
# Reading / assembling fragments
# ---------------------------------------------------------------------------

def load_fragments(root: Path) -> list[tuple[Path, dict | None, str | None]]:
    """Read every *.json in root (non-recursive). Returns (path, parsed_or_None, error_or_None)."""
    root = Path(root)
    if not root.is_dir():
        return []
    out = []
    for p in sorted(root.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            out.append((p, data, None))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            out.append((p, None, f"{type(e).__name__}: {e}"))
    return out


def validate_fragment(data: dict) -> list[str]:
    """Return a list of validation problems (empty = clean). Never raises."""
    problems = []
    if not isinstance(data, dict):
        return [f"fragment is not a JSON object (got {type(data).__name__})"]
    for key in REQUIRED_FRAGMENT_KEYS:
        if key not in data:
            problems.append(f"missing required key '{key}'")
    findings = data.get("findings")
    if findings is not None and not isinstance(findings, list):
        problems.append("'findings' is present but not a list")
    elif isinstance(findings, list):
        for i, f in enumerate(findings):
            if not isinstance(f, dict):
                problems.append(f"findings[{i}] is not an object")
                continue
            for key in REQUIRED_FINDING_KEYS:
                if key not in f:
                    problems.append(f"findings[{i}] missing required key '{key}'")
    return problems


def _tag_label(evidence) -> str:
    if evidence is None:
        return "[UNTAGGED]"
    if evidence not in VALID_TAGS:
        return f"[INVALID-TAG:{evidence}]"
    return f"[{evidence}]"


def assemble(root: Path) -> str:
    """Build one markdown note from every fragment currently in root."""
    fragments = load_fragments(root)
    lines = [
        f"# Scan-out assembly -- {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        f"Source directory: `{_real(root)}`  |  fragments found: {len(fragments)}",
        "",
    ]
    if not fragments:
        lines.append("(no fragments present)")
        return "\n".join(lines) + "\n"

    tag_counts: dict[str, int] = {}
    for path, data, err in fragments:
        lines.append(f"## {path.name}")
        if err is not None:
            lines.append(f"**UNREADABLE**: {err}")
            lines.append("")
            continue
        # 2026-08-18: a fragment whose top level is a LIST (or anything but an object) used to
        # crash the whole collector here with "'list' object has no attribute 'get'", so ONE
        # malformed fragment made EVERY other fragment uncollectable -- and because the Stop
        # hook's scan-out gate fires on "fragment present, not collected", it re-fired forever.
        # Degrade per-fragment instead: report the shape, keep going.
        if not isinstance(data, dict):
            lines.append(f"**MALFORMED**: top level is `{type(data).__name__}`, expected an "
                         f"object. Fragment skipped; the rest of this report is unaffected.")
            if isinstance(data, list):
                lines.append(f"- it holds {len(data)} item(s); "
                             f"first item type `{type(data[0]).__name__ if data else 'n/a'}`")
            lines.append("")
            continue
        problems = validate_fragment(data)
        if problems:
            lines.append("**SCHEMA WARNINGS:**")
            for p in problems:
                lines.append(f"- {p}")
        agent = data.get("agent", "?")
        task = data.get("task", "?")
        ts = data.get("timestamp", "?")
        lines.append(f"- agent: `{agent}`  |  task: {task}  |  timestamp: {ts}")
        summary = data.get("summary")
        if summary:
            lines.append(f"- summary: {summary}")
        findings = data.get("findings") or []
        lines.append(f"- findings: {len(findings)}")
        for f in findings:
            if not isinstance(f, dict):
                lines.append(f"  - (malformed finding: {f!r})")
                continue
            tag = _tag_label(f.get("evidence"))
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            claim = f.get("claim", "(no claim text)")
            src = f.get("source")
            detail = f.get("detail")
            row = f"  - {tag} {claim}"
            if src:
                row += f" (source: {src})"
            lines.append(row)
            if detail:
                lines.append(f"    {detail}")
        lines.append("")

    lines.append("## Evidence-tag rollup")
    for tag in sorted(tag_counts):
        lines.append(f"- {tag}: {tag_counts[tag]}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Retention / clear
# ---------------------------------------------------------------------------

def entries(root: Path) -> list[Path]:
    """Immediate *.json children of root, sorted deterministically. README.md etc. untouched."""
    if not root.is_dir():
        return []
    return sorted(root.glob("*.json"))


def clear(root: Path, apply: bool, older_than_days: float) -> int:
    """Dry-run list (apply=False) or delete (apply=True) fragment files older than the cutoff."""
    root = Path(root)
    if GUARD_ENABLED and _real(root) != _real(DEFAULT_SCAN_OUT):
        raise GuardViolation(f"root {_real(root)} is not the scan-out root {_real(DEFAULT_SCAN_OUT)}")
    if not root.is_dir():
        print(f"[scan_out_collect] nothing to do: {root} does not exist", file=sys.stderr)
        return 0

    now = datetime.now(timezone.utc).timestamp()
    cutoff_secs = older_than_days * 86400
    n = 0
    for child in entries(root):
        assert_under_root(child, DEFAULT_SCAN_OUT)
        age = now - child.stat().st_mtime
        if age < cutoff_secs:
            continue
        if apply:
            child.unlink()
            print(f"  removed  {child.name}  (age {age/3600:.1f}h)")
        else:
            print(f"  would remove {child.name}  (age {age/3600:.1f}h)")
        n += 1
    verb = "removed" if apply else "would remove"
    print(f"[scan_out_collect] {verb} {n} fragment(s) under {root} (older-than-days={older_than_days})")
    if not apply and n:
        print("[scan_out_collect] dry run. re-run with --clear --yes to actually delete.")
    return n


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test() -> int:
    ok = True

    # --- guard: refuse a target outside scan-out/ ---
    outside = Path(tempfile.mkdtemp(prefix="scan_out_selftest_"))
    victim = outside / "must_survive.json"
    victim.write_text('{"agent": "x"}', encoding="utf-8")
    try:
        clear(outside, apply=True, older_than_days=0)
    except GuardViolation as e:
        print(f"[self-test] PASS guard refused out-of-tree root: {e}")
    else:
        print("[self-test] FAIL guard did NOT refuse an out-of-tree root", file=sys.stderr)
        ok = False
    if not victim.exists():
        print("[self-test] FAIL victim file was deleted", file=sys.stderr)
        ok = False
    else:
        print("[self-test] PASS victim file survived")

    # --- guard: refuse the scan-out root itself as a delete target ---
    try:
        assert_under_root(DEFAULT_SCAN_OUT, DEFAULT_SCAN_OUT)
    except GuardViolation as e:
        print(f"[self-test] PASS guard refused root-itself: {e}")
    else:
        print("[self-test] FAIL guard allowed removing the scan-out root", file=sys.stderr)
        ok = False

    # --- guard: accepts a legitimate child ---
    try:
        assert_under_root(DEFAULT_SCAN_OUT / "probe.json", DEFAULT_SCAN_OUT)
        print("[self-test] PASS guard accepts a legitimate scan-out child")
    except GuardViolation as e:
        print(f"[self-test] FAIL guard refused a legitimate child: {e}", file=sys.stderr)
        ok = False

    # --- negative control: with the guard disabled, the out-of-tree refusal must NOT happen ---
    global GUARD_ENABLED
    GUARD_ENABLED = False
    outside2 = Path(tempfile.mkdtemp(prefix="scan_out_selftest_negctrl_"))
    victim2 = outside2 / "would_be_deleted.json"
    victim2.write_text('{"agent": "x"}', encoding="utf-8")
    # Pin mtime to an unambiguous 1h-old timestamp. Without this, `clear()`'s age filter
    # (`age = now - mtime; skip if age < cutoff_secs`) races write_text()'s file-close mtime
    # against this test's own datetime.now() call microseconds later -- on ~1/3 of runs the
    # two clock reads land close enough that `age` comes out slightly negative (observed as
    # low as -4.8e-07s), which skips the delete and fails this check for a reason that has
    # nothing to do with the guard. older_than_days=0 alone does not make this deterministic;
    # the fixture's age must be unambiguously >= the cutoff, not merely non-negative.
    old_ts = datetime.now(timezone.utc).timestamp() - 3600
    os.utime(victim2, (old_ts, old_ts))
    try:
        clear(outside2, apply=True, older_than_days=0)
        if not victim2.exists():
            print("[self-test] PASS negative control: disabled guard DID allow the delete "
                  "(proves the guard, not something else, was doing the refusing above)")
        else:
            print("[self-test] FAIL negative control: disabled guard still refused (guard "
                  "may be a no-op, or clear() has an independent check)", file=sys.stderr)
            ok = False
    except GuardViolation:
        print("[self-test] FAIL negative control: guard still raised with GUARD_ENABLED=False",
              file=sys.stderr)
        ok = False
    finally:
        GUARD_ENABLED = True

    # --- round trip: write a real fragment into a temp scan-out-shaped dir, assemble it ---
    tmp_root = Path(tempfile.mkdtemp(prefix="scan_out_selftest_roundtrip_"))
    frag = tmp_root / "probe_agent.json"
    frag.write_text(json.dumps({
        "agent": "probe_agent",
        "task": "self-test round trip",
        "timestamp": "2026-08-14T00:00:00Z",
        "findings": [
            {"claim": "guard refuses out-of-tree targets", "evidence": "ESTABLISHED",
             "source": "this self-test"},
            {"claim": "an untagged finding still renders", "source": "this self-test"},
        ],
        "summary": "round-trip probe",
    }), encoding="utf-8")
    note = assemble(tmp_root)
    checks = [
        ("probe_agent.json" in note, "assembled note names the fragment file"),
        ("[ESTABLISHED]" in note, "assembled note carries the ESTABLISHED tag"),
        ("[UNTAGGED]" in note, "assembled note flags the untagged finding"),
        ("self-test round trip" in note, "assembled note carries the task text"),
    ]
    for passed, label in checks:
        if passed:
            print(f"[self-test] PASS {label}")
        else:
            print(f"[self-test] FAIL {label}", file=sys.stderr)
            ok = False

    # --- malformed JSON is reported, not raised ---
    bad = tmp_root / "broken.json"
    bad.write_text("{not valid json", encoding="utf-8")
    note2 = assemble(tmp_root)
    if "UNREADABLE" in note2:
        print("[self-test] PASS malformed fragment reported as UNREADABLE, not raised")
    else:
        print("[self-test] FAIL malformed fragment did not surface as UNREADABLE", file=sys.stderr)
        ok = False

    print(f"[self-test] leftover temp dirs (not auto-removed, by design): {outside}, {outside2}, {tmp_root}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=str(DEFAULT_SCAN_OUT), help="scan-out root (default: <repo>/.claude/scan-out)")
    ap.add_argument("--out", default=None, help="write assembled note here instead of stdout")
    ap.add_argument("--clear", action="store_true", help="retention mode: remove fragment files instead of assembling")
    ap.add_argument("--yes", action="store_true", help="with --clear, actually delete (default is dry-run)")
    ap.add_argument("--older-than-days", type=float, default=0.0, help="with --clear, only remove fragments older than this many days (default 0 = all)")
    ap.add_argument("--self-test", action="store_true", help="prove the guard + schema handling")
    ap.add_argument("--_disable_guard", action="store_true", help="self-test only: disable the guard to confirm the self-test then FAILS")
    args = ap.parse_args(argv)

    if args._disable_guard:
        global GUARD_ENABLED
        GUARD_ENABLED = False
        print("[scan_out_collect] WARNING guard DISABLED (self-test negative control)")

    if args.self_test:
        return self_test()

    root = Path(args.dir)

    if args.clear:
        try:
            clear(root, apply=args.yes, older_than_days=args.older_than_days)
        except GuardViolation as e:
            print(f"[scan_out_collect] REFUSED: {e}", file=sys.stderr)
            return 2
        return 0

    note = assemble(root)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(note, encoding="utf-8")
        print(f"[scan_out_collect] wrote assembled note to {out_path}")
    else:
        # Windows consoles default to cp1252; fragments carry non-ASCII (>=, arrows,
        # Greek from lit-scans). Never let an encoding fault lose an assembled note --
        # this crashed the Stop-hook collect path on 2026-08-14.
        try:
            print(note)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(note.encode("utf-8", errors="replace"))
            sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
