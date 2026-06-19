#!/usr/bin/env python3
"""
Pre-commit validator for substrate_capability_map.md (PROT-008).

Catches mechanical violations of PROT-004 + PROT-006 + PROT-007 before
they land in cap_map. Designed to be called by Strategy's per-cycle
slash command before any cap_map atomic write.

Exits 0 if all checks pass; non-zero (with explicit reasons) if any
invariant fails.

Usage (run from project root):
    python tools/validate_capmap_commit.py

Exit codes:
    0 = all checks pass
    1 = ❌ closure row missing rehab request file reference
    2 = referenced rehab request file does not exist on disk
    3 = cap_map version-table entry has no matching history.md block
    4 = file structure error (cap_map or history missing)
    5 = invariant-class violation (printed to stderr)
    6 = PROT-009: cap_map staged without paired strategy_decisions entry

Designed for v1 mechanical catches:
    - Catches v62-class overcloses (closure without rescue sketches/file)
    - Catches v65 Bet E-class overcloses (claim without evidence file)
    - Catches PROT-007 sequencing violations (orphan cap_map entry)
    - Catches PROT-009 decision-log-gap violations (when invoked with
      --staged-files)

Does NOT catch (deferred to Strategy judgment):
    - v60-class scope errors (closure inventory vs active rescue paths)
    - v65 Bet B-class seed-variance misreads
    - Multi-probe quality (Strategy + Research review)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CAP_MAP = REPO_ROOT / "notes" / "substrate_capability_map.md"
CAP_MAP_HISTORY = REPO_ROOT / "notes" / "substrate_capability_map_history.md"
NOTES_DIR = REPO_ROOT / "notes"

# Pattern: any row line that contains a closure marker.
# Matches both bare ❌ and "❌ PROVISIONAL" variants.
CLOSURE_ROW_PATTERN = re.compile(r"❌")

# Pattern: a rehab request file reference inside a row.
# Strategy convention: strategy_request_to_research_<bet>_rehab_<date>.md
REHAB_REF_PATTERN = re.compile(
    r"strategy_request_to_research_[A-Za-z0-9_]+_rehab_\d{4}-\d{2}-\d{2}\.md"
)

# Pattern: version-table entries at the bottom of cap_map.
# Conventional format: | vN | YYYY-MM-DD HH:MM | summary | trigger | history ref |
VERSION_TABLE_ROW = re.compile(
    r"^\|\s*v(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2}[^|]*)\|"
)


def fail(code: int, message: str, *, hint: str | None = None) -> None:
    """Print a validation failure and exit non-zero."""
    print(f"VALIDATOR FAIL [exit {code}]: {message}", file=sys.stderr)
    if hint:
        print(f"  hint: {hint}", file=sys.stderr)
    sys.exit(code)


def check_files_exist() -> tuple[str, str]:
    """Confirm both cap_map files exist and return their contents."""
    if not CAP_MAP.exists():
        fail(4, f"cap_map missing: {CAP_MAP}",
             hint="Strategy must atomic-write cap_map before validation.")
    if not CAP_MAP_HISTORY.exists():
        fail(4, f"history file missing: {CAP_MAP_HISTORY}",
             hint=("PROT-007 requires substrate_capability_map_history.md to "
                   "exist alongside cap_map.md. Run the one-time restructure "
                   "first."))
    return CAP_MAP.read_text(encoding="utf-8"), CAP_MAP_HISTORY.read_text(encoding="utf-8")


STATE_MARKERS = ("✅", "🟢", "🟡", "🔬", "⚪", "❌")

# Grandfather markers: explicit annotations Strategy can add to a row
# to mark a pre-PROT-004 closure that has its own audit trail and
# doesn't need a current rehab request file.
GRANDFATHER_MARKERS = ("pre-PROT-004", "grandfathered", "pre-rehab-discipline")


def _is_capability_table_row(line: str) -> bool:
    """Heuristic: is this line a real capability-state table row?"""
    # Must be a markdown table row with enough columns.
    if line.count("|") < 4:
        return False
    # Skip header separators.
    if "---" in line:
        return False
    # Skip tally rows that show ALL state markers in one line
    # (e.g., "| Section | ✅ | 🟢 | 🟡 | 🔬 | ⚪ | ❌ |").
    marker_count = sum(line.count(m) for m in STATE_MARKERS)
    if marker_count >= 4:
        return False
    return True


def _is_history_block_heading(line: str) -> bool:
    """Detect '## vN update' style headings that should have been moved
    to substrate_capability_map_history.md (PROT-007)."""
    stripped = line.strip().lower()
    if not stripped.startswith("##"):
        return False
    # Match either '## vN' or '## YYYY-MM-DD ... vN update'.
    if re.search(r"\bv\d+\b\s*update", stripped):
        return True
    if re.match(r"##\s*v\d+\b", stripped):
        return True
    return False


def check_closures_have_rehab_files(cap_map_text: str) -> None:
    """
    PROT-004 + PROT-006: every ❌ closure capability-row must reference
    a rehab request file that exists on disk, or carry a grandfather
    marker for pre-PROT-004 closures.

    Skips:
        - Recently-retracted / CANNOT sections (historical closures)
        - Tally rows showing all state markers
        - Bullet-list legend definitions
        - Lines inside ## vN update history blocks (should have been
          moved to history.md per PROT-007)
        - Non-table prose containing ❌
    """
    in_excluded_section = False
    in_history_block = False
    failures: list[tuple[int, str, str]] = []
    history_block_count = 0

    for lineno, line in enumerate(cap_map_text.splitlines(), start=1):
        stripped = line.strip()

        # Track section headings.
        if stripped.startswith("## ") or stripped.startswith("# "):
            heading = stripped.lower()
            in_excluded_section = (
                "recently retracted" in heading
                or "recently closed" in heading
                or heading.startswith("## 2. cannot")
                or "cannot" in heading
            )
            in_history_block = _is_history_block_heading(line)
            if in_history_block:
                history_block_count += 1

        if in_excluded_section or in_history_block:
            continue

        if not CLOSURE_ROW_PATTERN.search(line):
            continue

        if not _is_capability_table_row(line):
            continue

        # Real capability row with ❌. Check for rehab file or grandfather.
        if any(marker in line for marker in GRANDFATHER_MARKERS):
            continue  # explicitly grandfathered

        refs = REHAB_REF_PATTERN.findall(line)
        if not refs:
            failures.append((lineno, "no rehab request file referenced", line.rstrip()))
            continue

        # Confirm the referenced file exists on disk.
        for ref in refs:
            ref_path = NOTES_DIR / ref
            if not ref_path.exists():
                failures.append(
                    (lineno, f"referenced rehab file does not exist: {ref}", line.rstrip())
                )

    if history_block_count > 0:
        print(
            f"VALIDATOR WARN: cap_map.md contains {history_block_count} version-"
            f"update history block(s) ('## vN update'). PROT-007 expects these "
            f"in substrate_capability_map_history.md. Move them on next commit.",
            file=sys.stderr,
        )

    if not failures:
        return

    for lineno, reason, content in failures:
        print(
            f"  cap_map.md:{lineno}: {reason}\n    line: {content[:140]}",
            file=sys.stderr,
        )

    fail(
        1 if any("no rehab" in r for _, r, _ in failures) else 2,
        f"{len(failures)} ❌-closure capability row(s) violate PROT-004/006 rehab discipline.",
        hint=(
            "Each ❌ closure must reference an existing "
            "strategy_request_to_research_<bet>_rehab_<date>.md file, or be "
            "tagged 'pre-PROT-004' / 'grandfathered' / 'pre-rehab-discipline' "
            "in the row text. File the request file BEFORE the cap_map commit "
            "(PROT-006 sequencing)."
        ),
    )


def check_version_table_history_sync(cap_map_text: str, history_text: str) -> None:
    """
    PROT-007: every cap_map version-table entry must have a matching
    history.md block. The version-table is at the bottom of cap_map;
    history.md contains the full prose blocks per version.
    """
    cap_versions = set()
    for line in cap_map_text.splitlines():
        m = VERSION_TABLE_ROW.match(line)
        if m:
            cap_versions.add(int(m.group(1)))

    if not cap_versions:
        # No version table found — could mean cap_map hasn't been
        # restructured under PROT-007 yet. Soft-warn rather than fail.
        print(
            "VALIDATOR WARN: no version table found in cap_map.md. "
            "If PROT-007 restructure is complete, the table is missing.",
            file=sys.stderr,
        )
        return

    history_versions = set()
    for line in history_text.splitlines():
        # Conventional history block header: "## vN — ..." or "## vN update — ..."
        m = re.match(r"^##\s*v(\d+)\b", line)
        if m:
            history_versions.add(int(m.group(1)))

    missing_in_history = cap_versions - history_versions
    if missing_in_history:
        versions_str = ", ".join(f"v{v}" for v in sorted(missing_in_history))
        fail(
            3,
            f"cap_map version-table entries with no matching history.md block: {versions_str}",
            hint=(
                "PROT-007 requires atomic two-file commits. For each version "
                "added to cap_map's version table, the matching '## vN — ...' "
                "block must appear in substrate_capability_map_history.md."
            ),
        )


def check_decision_log_paired(staged_files: list[str] | None, exempt: bool) -> None:
    """
    PROT-009: cap_map commits must include a paired strategy_decisions
    entry in the same commit. Catches the recurring decision-log-gap
    pattern where Strategy commits cap_map updates atomically (PROT-007)
    but skips the decision-log entry under verdict-batch tempo.

    Only fires when --staged-files is provided. If not provided, this
    check is silently skipped (allows ad-hoc cap_map validation without
    requiring full git context).

    Exempt via --exempt-prot-009 flag for legitimate PROT-007 hygiene
    commits (pure mechanical file-restructure with no capability state
    change). Strategy explicitly tags these.
    """
    if staged_files is None:
        return

    if exempt:
        print(
            "VALIDATOR INFO: PROT-009 check skipped (--exempt-prot-009).",
            file=sys.stderr,
        )
        return

    # Normalize paths: accept both "notes/foo.md" and absolute paths.
    normalized = {Path(f).as_posix().lower() for f in staged_files}

    def matches(path_fragment: str) -> bool:
        return any(path_fragment.lower() in p for p in normalized)

    cap_map_changed = matches("notes/substrate_capability_map.md")
    decision_log_changed = matches("notes/strategy_decisions_")

    if cap_map_changed and not decision_log_changed:
        fail(
            6,
            "PROT-009 violation: cap_map staged without paired strategy_decisions entry.",
            hint=(
                "PROT-009 requires Strategy decision-log entry paired "
                "with any cap_map version commit. Add a cycle N entry to "
                "notes/strategy_decisions_<date>.md and re-stage, OR pass "
                "--exempt-prot-009 if this is a PROT-007 mechanical-restructure "
                "commit with no capability state change."
            ),
        )


def check_provisional_tag_present(cap_map_text: str) -> None:
    """
    PROT-004: ❌ closures with active rehab paths should carry the
    PROVISIONAL tag in the row text. Soft check — warn but don't fail —
    because some closures are intentionally structural (no rehab path).
    """
    warns: list[tuple[int, str]] = []
    in_recently_retracted = False
    in_cannot_section = False

    for lineno, line in enumerate(cap_map_text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("# "):
            heading = stripped.lower()
            in_recently_retracted = (
                "recently retracted" in heading or "recently closed" in heading
            )
            in_cannot_section = "cannot" in heading

        if in_recently_retracted or in_cannot_section:
            continue

        if not CLOSURE_ROW_PATTERN.search(line):
            continue

        if not REHAB_REF_PATTERN.search(line):
            continue  # Already failed by check_closures_have_rehab_files

        if "PROVISIONAL" not in line.upper():
            warns.append((lineno, line.strip()[:120]))

    for lineno, content in warns:
        print(
            f"VALIDATOR WARN cap_map.md:{lineno}: ❌ row with rehab file but no "
            f"PROVISIONAL tag.\n    line: {content}",
            file=sys.stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress success message; only print on failure."
    )
    parser.add_argument(
        "--staged-files",
        nargs="+",
        default=None,
        help=(
            "List of files staged in current commit (for PROT-009 check). "
            "Get via: git diff --cached --name-only. If omitted, PROT-009 "
            "check is skipped."
        ),
    )
    parser.add_argument(
        "--exempt-prot-009",
        action="store_true",
        help=(
            "Exempt this commit from PROT-009 (decision-log pairing). "
            "Use for legitimate PROT-007 mechanical-restructure commits "
            "with no capability state change."
        ),
    )
    args = parser.parse_args()

    cap_map_text, history_text = check_files_exist()

    check_closures_have_rehab_files(cap_map_text)
    check_version_table_history_sync(cap_map_text, history_text)
    check_provisional_tag_present(cap_map_text)
    check_decision_log_paired(args.staged_files, args.exempt_prot_009)

    if not args.quiet:
        print("VALIDATOR OK: cap_map invariants satisfied (PROT-004 + 006 + 007 + 009).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
