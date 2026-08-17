#!/usr/bin/env python
"""WHAT CLAIMS TO BE RUNNING -- the `scratch/*.pid` files, checked against the OS. DISPLAY ONLY.

WHY THIS EXISTS (owner, 2026-08-16): the status window's RUNNING panel listed only processes it
could SEE (`tools/local_exp_scan.py` enumerates live `python.exe` via WMIC). Anything that had died
simply vanished from the panel -- while its `scratch/<name>.pid` file stayed on disk and kept being
quoted as live. On the night this was written all 39 pid files pointed at DEAD processes, three of
them cited as live in every agent brief for hours, and one of them was the status dashboard itself.

    A STALE RUNNING IS WORSE THAN NO PANEL, BECAUSE IT IS READ AS EVIDENCE.

So the panel now shows the CLAIM and the OS's answer side by side, and a claim whose process is gone
gets its own loud state: DEAD BUT CLAIMED LIVE. An absence is never silent.

THIS FILE IS DISPLAY ONLY. It reads; it never writes, never deletes a pid file, and never signals a
process. Reconciling / cleaning up the pid files is a separate job with a separate owner.

HOW LIVENESS IS DECIDED, and why not the obvious way:
  * NOT `os.kill(pid, 0)`. On Windows that is not a no-op probe -- CPython implements `os.kill` via
    `TerminateProcess`, so the "harmless" liveness check would KILL the process it asked about.
    That would be a catastrophic bug in a monitoring tool.
  * NOT a subprocess (`tasklist`, `wmic`, PowerShell). Each one costs a console window under this
    project's windowless mandate, and this runs on every 20 s refresh across 39 files.
  * `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `GetExitCodeProcess`, in-process via ctypes.
    Handle refused with ERROR_INVALID_PARAMETER (87) -> the pid does not exist -> DEAD.
    Handle refused with ERROR_ACCESS_DENIED (5)      -> it exists, owned by someone else -> ALIVE.
    Handle opens and the exit code is STILL_ACTIVE   -> ALIVE. Any other exit code -> DEAD.
  * PID REUSE IS NOT IGNORED. A pid can be alive and belong to something else entirely, so a claim
    is only called OURS when that pid is also one of the python experiment processes the live scan
    found. Alive-but-unrecognised is reported as its own state, never as a running experiment.

  python tools/status_pidclaims.py            # human-readable
  python tools/status_pidclaims.py --json
  python tools/status_pidclaims.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRATCH = Path(os.environ.get("HD_SCRATCH_DIR") or (REPO / "scratch"))

# States, in the order the panel should worry about them.
DEAD_CLAIMED = "DEAD BUT CLAIMED LIVE"
RUNNING_OURS = "RUNNING"
ALIVE_FOREIGN = "ALIVE, BUT NOT ONE OF OUR EXPERIMENTS"
UNREADABLE = "PID FILE UNREADABLE"

_STILL_ACTIVE = 259
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_ERROR_ACCESS_DENIED = 5
_ERROR_INVALID_PARAMETER = 87

MAX_CLAIMS = 200          # a bound, so a pathological scratch/ cannot wedge a 20 s refresh


def _pid_alive(pid: int) -> tuple[bool | None, str]:
    """(alive, how_we_know). None means genuinely undetermined -- never guessed as either."""
    if pid <= 0:
        return False, "a pid of zero or less cannot name a process"
    if os.name != "nt":                                   # pragma: no cover - this repo is Windows
        try:
            os.kill(pid, 0)                               # POSIX: signal 0 really is a probe
            return True, "signal 0 was accepted (POSIX)"
        except ProcessLookupError:
            return False, "no such process (POSIX)"
        except PermissionError:
            return True, "the process exists but is owned by another user (POSIX)"
        except OSError as exc:
            return None, f"probe failed: {exc}"
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        handle = k32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            err = ctypes.get_last_error()
            if err == _ERROR_INVALID_PARAMETER:
                return False, "the operating system has no process with this number"
            if err == _ERROR_ACCESS_DENIED:
                return True, "the process exists but belongs to another account"
            return None, f"could not ask about it (windows error {err})"
        try:
            code = wintypes.DWORD()
            ok = k32.GetExitCodeProcess(handle, ctypes.byref(code))
            if not ok:
                return None, f"could not read its exit code (windows error "
                f"{ctypes.get_last_error()})"
            if code.value == _STILL_ACTIVE:
                return True, "the operating system reports it as still running"
            return False, f"it has already exited (exit code {code.value})"
        finally:
            k32.CloseHandle(handle)
    except Exception as exc:                              # pragma: no cover - never wedge a panel
        return None, f"the liveness check itself failed ({type(exc).__name__}: {exc})"


def _read_pid(path: Path) -> tuple[int | None, str]:
    """The integer in a .pid file. Tolerates the UTF-8 BOM PowerShell's `Out-File` writes -- three
    of the live files start with one, and a parser that chokes on it would report a DEAD process as
    UNREADABLE, which is a different and less useful thing to say."""
    try:
        raw = path.read_text(encoding="utf-8-sig", errors="replace").strip()
    except OSError as exc:
        return None, f"could not be read ({exc})"
    if not raw:
        return None, "the file is empty"
    head = raw.splitlines()[0].strip().lstrip("﻿")
    try:
        return int(head), ""
    except ValueError:
        return None, f"does not contain a process number (it starts {head[:40]!r})"


def _companions(path: Path) -> list[str]:
    """The .out / .err / .log files written beside a pid file, newest first. These are the resume
    evidence when a detached run dies, so the panel names them rather than making the reader guess."""
    out = []
    for suffix in (".out", ".err", ".log"):
        p = path.with_suffix(suffix)
        try:
            st = p.stat()
        except OSError:
            continue
        out.append({"path": str(p), "name": p.name, "bytes": st.st_size,
                    "mtime": st.st_mtime, "age_s": round(time.time() - st.st_mtime, 1)})
    out.sort(key=lambda d: -d["mtime"])
    return out


def scan_claims(live_pids: set | None = None, scratch: Path | None = None) -> dict:
    """Every `scratch/*.pid` claim, with the OS's verdict on it.

    `live_pids` is the set of process ids the live experiment scan actually found (both the venv
    shim and the real interpreter). It is what separates "our run is up" from "that number now
    belongs to something else"; pass None and every alive pid is reported as unrecognised rather
    than silently credited to us."""
    d = Path(scratch) if scratch else SCRATCH
    live = set(live_pids or ())
    if not d.is_dir():
        return {"status": "NO_SCRATCH_DIR", "detail": f"{d} does not exist", "claims": [],
                "n_claims": 0, "n_dead": 0, "n_running": 0, "n_foreign": 0, "n_unknown": 0,
                "path": str(d)}
    try:
        files = sorted((e for e in os.scandir(d) if e.is_file() and e.name.endswith(".pid")),
                       key=lambda e: -e.stat().st_mtime)[:MAX_CLAIMS]
    except OSError as exc:
        return {"status": "ERROR", "detail": f"{d} could not be listed ({exc})", "claims": [],
                "n_claims": 0, "n_dead": 0, "n_running": 0, "n_foreign": 0, "n_unknown": 0,
                "path": str(d)}

    now = time.time()
    claims = []
    for e in files:
        p = Path(e.path)
        try:
            claimed_at = e.stat().st_mtime
        except OSError:
            claimed_at = None
        pid, why_not = _read_pid(p)
        row = {
            "name": p.stem,
            "pid": pid,
            "pid_file": str(p),
            "claimed_at": claimed_at,
            "claimed_age_s": round(now - claimed_at, 1) if claimed_at else None,
            "logs": _companions(p),
        }
        if pid is None:
            row.update({"state": UNREADABLE, "alive": None, "basis": why_not})
            claims.append(row)
            continue
        alive, basis = _pid_alive(pid)
        row["alive"] = alive
        row["basis"] = basis
        if alive is None:
            row["state"] = "UNKNOWN"
        elif not alive:
            row["state"] = DEAD_CLAIMED
        elif pid in live:
            row["state"] = RUNNING_OURS
        else:
            row["state"] = ALIVE_FOREIGN
        claims.append(row)

    # Loudest first: a wrong claim is the thing this panel exists to surface.
    order = {DEAD_CLAIMED: 0, "UNKNOWN": 1, UNREADABLE: 2, ALIVE_FOREIGN: 3, RUNNING_OURS: 4}
    claims.sort(key=lambda r: (order.get(r["state"], 9), -(r.get("claimed_at") or 0)))
    n = lambda s: sum(1 for r in claims if r["state"] == s)  # noqa: E731
    return {
        "status": "OK",
        "path": str(d),
        "claims": claims,
        "n_claims": len(claims),
        "n_dead": n(DEAD_CLAIMED),
        "n_running": n(RUNNING_OURS),
        "n_foreign": n(ALIVE_FOREIGN),
        "n_unknown": n("UNKNOWN") + n(UNREADABLE),
        "live_pids_known": bool(live),
        "headline": _headline(claims, bool(live)),
    }


def _headline(claims: list, live_known: bool) -> str:
    """One plain sentence the panel can put above the table."""
    if not claims:
        return "No process claims a run on this machine."
    dead = sum(1 for r in claims if r["state"] == DEAD_CLAIMED)
    running = sum(1 for r in claims if r["state"] == RUNNING_OURS)
    other = len(claims) - dead - running
    bits = [f"{len(claims)} run(s) left a claim on this machine"]
    if running:
        bits.append(f"{running} really are running")
    if dead:
        bits.append(f"{dead} SAY they are running and the process is GONE -- do not read those as "
                    f"evidence that work is in flight")
    if other:
        bits.append(f"{other} could not be confirmed either way")
    if not live_known:
        bits.append("the live process list was unavailable this tick, so a running claim is "
                    "reported as unconfirmed rather than as ours")
    return "; ".join(bits) + "."


# ---------------------------------------------------------------------------

def render_text(s: dict) -> str:
    if s.get("status") != "OK":
        return f"WHAT CLAIMS TO BE RUNNING: {s.get('status')} -- {s.get('detail')}"
    L = [f"WHAT CLAIMS TO BE RUNNING ({s['path']})", "  " + str(s.get("headline"))]
    for r in s["claims"]:
        age = r.get("claimed_age_s")
        age_s = f"{age / 3600:.1f}h ago" if isinstance(age, (int, float)) else "unknown"
        L.append(f"  [{r['state']:<34}] {r['name']:<40} pid={r.get('pid')}  claimed {age_s}")
        L.append(f"      {r.get('basis', '')}")
        for lg in r.get("logs") or []:
            L.append(f"      log: {lg['name']} ({lg['bytes']} bytes, "
                     f"{lg['age_s'] / 3600:.1f}h old)")
    return "\n".join(L)


def self_test() -> int:
    """Every property that matters, against a throwaway scratch dir. Nothing real is read or
    written, and NOTHING IS EVER SIGNALLED -- the liveness probe is asserted to be non-destructive
    by checking it against this very process, which must survive being asked about."""
    import subprocess
    import tempfile
    ok = True

    def check(cond, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    td = Path(tempfile.mkdtemp(prefix="pidclaims_selftest_"))

    # 1. THE PROBE MUST NOT KILL. Ask about ourselves twice and still be here.
    me = os.getpid()
    alive, basis = _pid_alive(me)
    check(alive is True, f"our own process is reported ALIVE ({basis})")
    alive2, _ = _pid_alive(me)
    check(alive2 is True, "and asking a second time did not terminate it -- the probe is READ-ONLY")

    # 2. A process that really has exited must read DEAD, not UNKNOWN.
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    dead_pid = p.pid
    alive3, basis3 = _pid_alive(dead_pid)
    check(alive3 is False, f"a process that has exited reads DEAD ({basis3})")

    # 3. End to end over a fixture scratch dir, including the PowerShell BOM.
    (td / "alive_run.pid").write_text(str(me), encoding="utf-8")
    (td / "dead_run.pid").write_bytes(("﻿" + str(dead_pid)).encode("utf-8"))
    (td / "dead_run.err").write_text("a traceback would live here", encoding="utf-8")
    (td / "garbage.pid").write_text("not a number at all", encoding="utf-8")
    (td / "empty.pid").write_text("", encoding="utf-8")

    s = scan_claims(live_pids={me}, scratch=td)
    by = {r["name"]: r for r in s["claims"]}
    check(s["status"] == "OK" and s["n_claims"] == 4, f"all four claims parsed ({s['n_claims']})")
    check(by["alive_run"]["state"] == RUNNING_OURS,
          f"a live pid we recognise reads RUNNING ({by['alive_run']['state']})")
    check(by["dead_run"]["state"] == DEAD_CLAIMED,
          f"a dead pid reads '{DEAD_CLAIMED}' ({by['dead_run']['state']})")
    check(by["dead_run"]["pid"] == dead_pid,
          f"the UTF-8 BOM PowerShell writes does not break the parse "
          f"(got {by['dead_run']['pid']!r}, wanted {dead_pid})")
    check(any(lg["name"] == "dead_run.err" for lg in by["dead_run"]["logs"]),
          "the dead run's log file is named, because it is the only evidence left")
    check(by["garbage"]["state"] == UNREADABLE and by["empty"]["state"] == UNREADABLE,
          "an unparseable pid file says so rather than being reported as dead")
    check(s["claims"][0]["state"] == DEAD_CLAIMED,
          f"the loudest state sorts FIRST ({s['claims'][0]['state']})")
    check("GONE" in s["headline"], f"the headline says it plainly ({s['headline']!r})")

    # 4. PID REUSE: alive, but not one of ours.
    s2 = scan_claims(live_pids=set(), scratch=td)
    by2 = {r["name"]: r for r in s2["claims"]}
    check(by2["alive_run"]["state"] == ALIVE_FOREIGN,
          f"an alive pid we do NOT recognise is not credited to us "
          f"({by2['alive_run']['state']})")

    # 5. Degradation: a missing directory is a stated state, never a crash and never an empty OK.
    s3 = scan_claims(live_pids={me}, scratch=td / "nope")
    check(s3["status"] == "NO_SCRATCH_DIR" and s3["claims"] == [],
          f"an absent scratch dir is reported, not invented ({s3['status']})")

    # 6. And it is fast enough for a 20 s refresh over the real directory.
    t0 = time.time()
    real = scan_claims(live_pids=set())
    dt = time.time() - t0
    check(dt < 2.0, f"the real scratch dir scans in {dt*1000:.0f} ms "
                    f"({real.get('n_claims')} claims)")

    print(f"[self-test] temp dir left in place by design: {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="pid-file claims, checked against the OS")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    s = scan_claims()
    print(json.dumps(s, indent=2, default=str) if args.json else render_text(s))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
