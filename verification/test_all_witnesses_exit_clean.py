#!/usr/bin/env python3
"""Collected driver: every verify_*/witness_* file in verification/ must exit 0.

WHY THIS EXISTS (notes/uncollected_witness_audit_2026-08-13.md). pyproject.toml sets
`python_files = ["test_*.py"]`, so the 27 `verify_*.py` / `witness_*.py` files in this
directory have NEVER been collected by certification at any commit since the 2026-05-16
scaffold. 9 of the 27 fail when actually executed.

Widening the glob does NOT fix it: only 9 of the 27 expose any collectable test function,
and those 9 all currently PASS. The other 18 keep their real work behind
`if __name__ == "__main__":`, which pytest never executes -- and all 9 currently-failing
witnesses are in that group. The config change would add 53 passing tests and still run
zero of the real failures: a second false-green.

This driver is named `test_*` so it IS collected, and it runs each witness as a SUBPROCESS
so the `__main__` body actually executes. Exit code 0 is the contract.

Deliberately contains NO skip, NO xfail, and NO allowlist. Quarantining a failure would recreate
exactly the false-green this file exists to remove.

STATUS UPDATED 2026-08-22 -- THE EXPECTED REDNESS IS GONE. This docstring read "It is EXPECTED to be
RED (9 failures) on `main` as of 2026-08-13. That redness is the point." Measured today by running
all 32 `verify_*`/`witness_*` files as subprocesses: **32/32 exit 0**. The 9 failures have been fixed
in the nine days since. Leaving the old text would mislead in the OPPOSITE direction -- a reader
seeing green would conclude the driver was broken.

READ THE PERSISTED RESULTS BEFORE RE-RUNNING: this file takes >550s (it runs every witness), and it
writes one JSON per witness to `data/witness_exit_status/` with `returncode`, `secs`, `timed_out` and
`run_utc`. Those files answer "which witness failed" in a second.

AND THEY ARE THE ONLY LIVE PROGRESS SIGNAL WHILE IT RUNS. Under pytest, this file's stdout is
BUFFERED -- a full-suite run sat at 28 bytes of output for minutes while it was working perfectly.
Judging progress from that output reads as a hang. The per-witness JSONs are written and closed one
at a time, so `ls -t data/witness_exit_status/` shows exactly where the run has reached. This is the
project's standing rule -- observe the ARTIFACT the process produces, never a proxy for it -- applied
to its own certification run, and it is recorded here because a buffered progress line plus a
15-minute runtime is precisely the shape that gets a healthy run killed.

AND BEWARE `rc=143` WITH `timed_out=False`: that is SIGTERM -- the witness was KILLED EXTERNALLY, not
a failure. On 2026-08-22 two such rows (22.5s and 0.46s, against a 600s cap) were produced purely by
an outer `timeout` killing this driver mid-flight, and were briefly mistaken for a real failure. A
genuine timeout sets `timed_out=True`; anything else with rc=143 is the harness, not the witness.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

VERIFICATION_DIR = Path(__file__).resolve().parent
ROOT = VERIFICATION_DIR.parent

# Per-witness exit status is persisted here so other tooling (notably
# tools/capability_registry_audit.py's `witness_failing` field) can read the newest
# real result instead of re-running ~8 minutes of witnesses inline. One small JSON per
# witness: no lock contention, no shared-file race, atomic replace per file.
RESULTS_DIR = ROOT / "data" / "witness_exit_status"

# Witness naming convention. Discovery is a GLOB, never a hardcoded list -- a hardcoded
# list is how a new witness silently escapes collection again.
WITNESS_GLOBS = ("verify_*.py", "witness_*.py")

# Support modules in verification/ that are NOT witnesses and are correctly uncollected:
#   __init__.py           -- package marker, no assertions
#   run_certification.py  -- the certification RUNNER (shells pytest; running it from
#                            inside pytest would recurse)
#   oracle.py             -- shared closed-form oracle helpers, imported by witnesses
#   theory.py             -- shared closed-form theory helpers, imported by witnesses
# None of them match WITNESS_GLOBS, so they are excluded structurally rather than by an
# exception list. NON_WITNESS_SUPPORT_MODULES is asserted against below so that a future
# rename (e.g. `verify_helpers.py`) cannot quietly become a "failing witness".
NON_WITNESS_SUPPORT_MODULES = frozenset(
    {"__init__.py", "run_certification.py", "oracle.py", "theory.py"}
)

# Two witnesses legitimately need ~94s and ~151s (verify_import_graph_scans_all_source_dirs,
# verify_integration_health_import_graph). A 120s cap produced FALSE timeouts in the audit.
PER_WITNESS_TIMEOUT_S = 600

# A silent discovery regression (glob typo, directory move, rename convention change) would
# make this file pass VACUOUSLY with zero parametrized cases -- the exact failure mode being
# fixed. 25 is a floor below the 27 on disk at 2026-08-13, leaving room for deletions while
# still failing loudly on a collapse to zero.
MIN_EXPECTED_WITNESSES = 25

_VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


def _interpreter() -> str:
    """.venv interpreter if present (the one certification and the audit both used)."""
    return str(_VENV_PYTHON) if _VENV_PYTHON.exists() else sys.executable


def discover_witnesses() -> list[Path]:
    """Every verification/verify_*.py + witness_*.py, sorted, deterministic."""
    found: set[Path] = set()
    for pattern in WITNESS_GLOBS:
        found.update(VERIFICATION_DIR.glob(pattern))
    return sorted(p for p in found if p.is_file() and p.name not in NON_WITNESS_SUPPORT_MODULES)


WITNESSES = discover_witnesses()
WITNESS_IDS = [p.name for p in WITNESSES]


def test_discovery_is_not_vacuous() -> None:
    """Self-check: a glob/rename change that discovers ~nothing must FAIL, not pass silently."""
    assert len(WITNESSES) >= MIN_EXPECTED_WITNESSES, (
        f"witness discovery found only {len(WITNESSES)} file(s) under {VERIFICATION_DIR} "
        f"matching {list(WITNESS_GLOBS)}; expected >= {MIN_EXPECTED_WITNESSES}. "
        "Either witnesses were deleted or the naming convention changed and this driver "
        "has stopped covering them. Found: " + ", ".join(WITNESS_IDS)
    )


def test_support_modules_are_not_witnesses() -> None:
    """The 4 support modules must never be picked up as witnesses."""
    names = set(WITNESS_IDS)
    overlap = names & set(NON_WITNESS_SUPPORT_MODULES)
    assert not overlap, f"support module(s) misclassified as witnesses: {sorted(overlap)}"


@pytest.mark.parametrize("witness", WITNESSES, ids=WITNESS_IDS)
def test_witness_exits_clean(witness: Path) -> None:
    """Run one witness as a subprocess from the repo root; require exit code 0.

    One test id per witness -- an aggregate pass/fail would hide WHICH witness broke.
    """
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = "1"
    env["OPENBLAS_NUM_THREADS"] = "1"

    cmd = [_interpreter(), str(witness)]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=PER_WITNESS_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        tail = _tail(_decode(exc.stdout), _decode(exc.stderr))
        _persist(witness, returncode=None, timed_out=True, secs=time.time() - t0, tail=tail)
        # A timeout is a FAILURE, never a skip: a witness that hangs is not a witness
        # that holds.
        pytest.fail(
            f"{witness.name} TIMED OUT after {PER_WITNESS_TIMEOUT_S}s "
            f"(cmd: {' '.join(cmd)})\n--- last output ---\n{tail}",
            pytrace=False,
        )

    tail = _tail(proc.stdout, proc.stderr)
    _persist(witness, returncode=proc.returncode, timed_out=False,
             secs=time.time() - t0, tail=tail)

    if proc.returncode != 0:
        pytest.fail(
            f"{witness.name} exited {proc.returncode} (expected 0)\n"
            f"cmd: {' '.join(cmd)}\n--- last 20 lines of output ---\n{tail}",
            pytrace=False,
        )


def _persist(witness: Path, returncode, timed_out: bool, secs: float, tail: str) -> None:
    """Write this witness's result to data/witness_exit_status/<name>.json. Best-effort:
    a persistence failure must never turn a passing witness red."""
    try:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "witness": witness.name,
            "path": f"verification/{witness.name}",
            "returncode": returncode,
            "timed_out": bool(timed_out),
            "passed": (returncode == 0) and not timed_out,
            "secs": round(secs, 2),
            "timeout_s": PER_WITNESS_TIMEOUT_S,
            "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tail": tail[-2000:],
            "driver": "verification/test_all_witnesses_exit_clean.py",
        }
        dest = RESULTS_DIR / f"{witness.stem}.json"
        tmp = dest.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp, dest)
    except OSError:
        pass


def _decode(raw) -> str:
    if raw is None:
        return ""
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="replace")
    return str(raw)


def _tail(stdout: str, stderr: str, n_lines: int = 20) -> str:
    """Last ~n_lines of the witness's output -- a red test that does not say WHY costs
    more than it saves."""
    combined = (stdout or "") + (("\n" + stderr) if stderr else "")
    lines = [ln for ln in combined.splitlines() if ln.strip()]
    if not lines:
        return "(no output)"
    return "\n".join(lines[-n_lines:])
