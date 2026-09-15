"""verification/test_land_tool.py -- tests tools/land.py against a TEMPORARY COPY of the six
notes files it edits + a fake problem folder. Never touches the live repo's notes/ files.

Runnable two ways:
    pytest verification/test_land_tool.py
    python verification/test_land_tool.py         (calls main() below)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LAND = REPO / "tools" / "land.py"

SIX_FILES = [
    "notes/INTEGRATION_LEDGER.md",
    "notes/SCORECARD.md",
    "notes/HOW_WE_ARE_DOING.md",
    "notes/STATUS.md",
    "notes/BUILD_PLAN_post_audit_2026-08-19.md",
    "notes/reference_retired_claims_never_requote.md",
]

FAKE_SLUG = "land_tool_test_fixture_do_not_use"
SOLVED_REL = "notes/problems/%s/SOLVED.md" % FAKE_SLUG


def _make_temp_repo(root: Path) -> Path:
    """Copy the six live notes files + a fake problem folder into root/repo. This is the
    ONLY thing this test ever reads from the live repo; it never writes to any of them."""
    repo = root / "repo"
    for rel in SIX_FILES:
        src = REPO / rel
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    solved = repo / SOLVED_REL
    solved.parent.mkdir(parents=True, exist_ok=True)
    solved.write_text(
        "# fake problem, for the land-tool test only\n\nA solver wrote this up.\n",
        encoding="utf-8", newline="\n",
    )
    return repo


def _record() -> dict:
    return {
        "pri": 9999,
        "slug": FAKE_SLUG,
        "commit_title": "test: land tool fixture landing",
        "time": "2026-09-15 12:34",
        "ledger": {
            "text": "LAND TOOL TEST fixture row -- safe to ignore",
            "status": "TEST",
            "leads": "none",
        },
        "scorecard_plain": "Land tool test bullet -- safe to ignore.",
        "livedoc_plain": "Land tool test bullet -- safe to ignore.",
        "status_line": "**12:34 LAND TOOL TEST pri 9999 (deadbeef): fixture entry -- safe to ignore.**",
        "plan_head_line": "> # \U0001F7E2 **2026-09-15 12:34 (LAND TOOL TEST): fixture entry -- safe to ignore.**",
        "integrated_mark": "fixture mark written by the land-tool test -- safe to ignore.",
        "retired": "'land tool test figure' -- fixture, safe to ignore.",
        "updates": {"kind": "IMPROVEMENT", "text": "land tool test update -- safe to ignore"},
        "files": ["tools/land.py"],
        "witness_smoke": True,
    }


def _write_record(root: Path, record: dict) -> Path:
    p = root / "record.json"
    p.write_text(json.dumps(record), encoding="utf-8")
    return p


def _run(record_path: Path, repo: Path, *extra: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(LAND), "--record", str(record_path), "--repo", str(repo)] + list(extra)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


def _all_targets(repo: Path) -> list[Path]:
    return [repo / rel for rel in SIX_FILES] + [repo / SOLVED_REL]


# --------------------------------------------------------------------------------------------
# test bodies (each takes a plain tmp_path so they run under pytest OR standalone)
# --------------------------------------------------------------------------------------------

def _check_dry_run_writes_nothing(tmp_path: Path) -> None:
    repo = _make_temp_repo(tmp_path)
    before = {p: p.read_bytes() for p in _all_targets(repo)}
    record_path = _write_record(tmp_path, _record())

    proc = _run(record_path, repo, "--dry-run")
    assert proc.returncode == 0, proc.stderr
    assert "DRY RUN" in proc.stdout
    for rel in SIX_FILES + [SOLVED_REL]:
        assert ("diff: %s" % rel) in proc.stdout, "missing a diff header for %s\n%s" % (rel, proc.stdout)

    after = {p: p.read_bytes() for p in _all_targets(repo)}
    assert before == after, "a --dry-run must write nothing"
    assert not (repo / "notes" / "UPDATES_FOR_OWNER.md").exists()
    assert not (repo / ".git").exists()


def _check_real_run_adds_one_correctly_placed_line_each(tmp_path: Path) -> None:
    repo = _make_temp_repo(tmp_path)
    record = _record()
    record_path = _write_record(tmp_path, record)

    proc = _run(record_path, repo)
    assert proc.returncode == 0, proc.stderr
    assert "TEMP MODE" in proc.stdout

    # 1. ledger: exactly one new row, as the last non-blank line, in the exact pipe shape.
    ledger_lines = [l for l in (repo / "notes/INTEGRATION_LEDGER.md").read_text(encoding="utf-8").splitlines() if l.strip()]
    expected_row = "| 2026-09-15 12:34 local | LAND TOOL TEST fixture row -- safe to ignore | TEST | none |"
    assert ledger_lines[-1] == expected_row
    assert ledger_lines.count(expected_row) == 1

    # 2. scorecard: exactly one new bullet, immediately under the heading.
    sc_lines = (repo / "notes/SCORECARD.md").read_text(encoding="utf-8").splitlines()
    heading_i = sc_lines.index("## WHAT CHANGED LATELY")
    expected_bullet = "- **15 Sep, 12:34.** Land tool test bullet -- safe to ignore."
    assert sc_lines[heading_i + 1] == expected_bullet
    assert sc_lines.count(expected_bullet) == 1

    # 3. live doc: exactly one new bullet, immediately under the heading.
    hwd_lines = (repo / "notes/HOW_WE_ARE_DOING.md").read_text(encoding="utf-8").splitlines()
    heading_i = hwd_lines.index("## WHAT MOVED THIS WEEK")
    expected_hwd_bullet = "- 2026-09-15 -- Land tool test bullet -- safe to ignore."
    assert hwd_lines[heading_i + 1] == expected_hwd_bullet
    assert hwd_lines.count(expected_hwd_bullet) == 1

    # 4. SOLVED.md: the INTEGRATED mark is appended once, after the original content.
    solved_text = (repo / SOLVED_REL).read_text(encoding="utf-8")
    expected_mark = ("INTEGRATED_BY_STRATEGY 2026-09-15 12:34 local -- "
                      "fixture mark written by the land-tool test -- safe to ignore.")
    assert solved_text.count(expected_mark) == 1
    assert solved_text.index("A solver wrote this up.") < solved_text.index(expected_mark)

    # 5. retired-claims: exactly one new line, appended at EOF.
    retired_lines = [l for l in (repo / "notes/reference_retired_claims_never_requote.md").read_text(encoding="utf-8").splitlines() if l.strip()]
    expected_retired = "- 2026-09-15 12:34: 'land tool test figure' -- fixture, safe to ignore."
    assert retired_lines[-1] == expected_retired
    assert retired_lines.count(expected_retired) == 1

    # 6. STATUS.md: the status line sits at the very front of the first dated block, not the
    #    pinned 'LOCATED, NOT YET FIXED' callout above it.
    status_text = (repo / "notes/STATUS.md").read_text(encoding="utf-8")
    blocks = status_text.split("\n\n")
    located_block = next(b for b in blocks if b.lstrip().startswith("**LOCATED"))
    dated_block = next(b for b in blocks if b.lstrip().startswith("**12:34 LAND TOOL TEST"))
    assert dated_block.startswith(record["status_line"])
    assert status_text.index(located_block) < status_text.index(dated_block)
    assert status_text.count(record["status_line"]) == 1

    # 7. BUILD_PLAN: the new head line sits right after the file's opening heading + blank line.
    plan_lines = (repo / "notes/BUILD_PLAN_post_audit_2026-08-19.md").read_text(encoding="utf-8").splitlines()
    assert plan_lines[0].startswith("# BUILD PLAN")
    assert plan_lines[1] == ""
    assert plan_lines[2] == record["plan_head_line"]
    assert plan_lines[3] == ""
    assert plan_lines.count(record["plan_head_line"]) == 1

    # Updates post and commit are skipped in temp mode: no git, no owner_updates file, no commit.
    assert not (repo / "notes" / "UPDATES_FOR_OWNER.md").exists()
    assert not (repo / ".git").exists()
    assert "[land] $" not in proc.stdout, "temp mode must never shell out (git / owner_updates)"

    return repo, record_path  # handed to the idempotency check


def _check_second_run_is_idempotent(tmp_path: Path) -> None:
    repo, record_path = _check_real_run_adds_one_correctly_placed_line_each(tmp_path)
    snapshot = {p: p.read_bytes() for p in _all_targets(repo)}

    proc = _run(record_path, repo)
    assert proc.returncode == 0, proc.stderr
    for rel in SIX_FILES + [SOLVED_REL]:
        assert ("%s" % rel) in proc.stdout and "no change" in proc.stdout, proc.stdout

    after = {p: p.read_bytes() for p in _all_targets(repo)}
    assert snapshot == after, "a re-run with the same record must not duplicate anything"


def _check_commit_flag_is_still_inert_in_temp_mode(tmp_path: Path) -> None:
    repo = _make_temp_repo(tmp_path)
    record_path = _write_record(tmp_path, _record())
    proc = _run(record_path, repo, "--commit")
    assert proc.returncode == 0, proc.stderr
    assert "TEMP MODE" in proc.stdout
    assert not (repo / ".git").exists()


# --------------------------------------------------------------------------------------------
# pytest entry points
# --------------------------------------------------------------------------------------------

def test_dry_run_writes_nothing(tmp_path):
    _check_dry_run_writes_nothing(tmp_path)


def test_real_run_adds_one_correctly_placed_line_each(tmp_path):
    _check_real_run_adds_one_correctly_placed_line_each(tmp_path)


def test_second_run_is_idempotent(tmp_path):
    _check_second_run_is_idempotent(tmp_path)


def test_commit_flag_is_inert_in_temp_mode(tmp_path):
    _check_commit_flag_is_still_inert_in_temp_mode(tmp_path)


# --------------------------------------------------------------------------------------------
# standalone entry point
# --------------------------------------------------------------------------------------------

def main() -> int:
    checks = [
        _check_dry_run_writes_nothing,
        _check_real_run_adds_one_correctly_placed_line_each,
        _check_second_run_is_idempotent,
        _check_commit_flag_is_still_inert_in_temp_mode,
    ]
    failed = 0
    for check in checks:
        with tempfile.TemporaryDirectory() as td:
            try:
                check(Path(td))
                print("PASS: %s" % check.__name__)
            except Exception as e:  # noqa: BLE001
                failed += 1
                print("FAIL: %s -- %s: %s" % (check.__name__, type(e).__name__, e))
    print("%d/%d passed" % (len(checks) - failed, len(checks)))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
