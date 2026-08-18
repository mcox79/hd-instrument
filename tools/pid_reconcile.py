"""Reconcile scratch/*.pid files against real OS process state.

WHY THIS EXISTS (2026-08-16 incident). Detached runs launched via PowerShell Start-Process
write a PID file at startup and never touch it again. A PID file is a BIRTH CERTIFICATE, not a
pulse -- so nothing on disk distinguished:

  (a) still running,   (b) finished cleanly hours ago,   (c) crashed 16 seconds after launch.

The default assumption was always (a). On 2026-08-16 all 39 pid files pointed at dead
processes, and agent briefs asserted three of them were LIVE RUNS not to disturb for hours.
The truth was mixed and the blindness cut BOTH ways: them_v2_full and fpb_full had FINISHED
(results sat unread on disk while the fleet waited for them), and selbridge_full2 had crashed
in 16s with an IndexError -- twice, because the first crash was never read before the relaunch.

Under-reacting to a crash and over-reacting to a completed run are the same defect: no liveness
signal. This tool supplies one.

THE PID-REUSE TRAP (this is why "does the PID exist" is not enough). Windows recycles PIDs
aggressively. During the 2026-08-16 audit a naive existence check reported selext_full.pid
(PID 18312, written 11:57:34) as ALIVE -- but PID 18312 was a landing_notifier child started
at 22:04:01 that had merely inherited the number. A reconciler that reports a dead run as live
is worse than none, because it launders a stale claim as a fresh measurement. Liveness here
therefore requires ALL THREE of:

  1. the PID exists AND has not exited (GetExitCodeProcess != STILL_ACTIVE means dead), and
  2. the process's CREATION TIME is not materially LATER than the pid file's mtime
     (a process born after its own pid file was written is a different process), and
  3. -- reported, not enforced -- the sibling log's freshness, so a wedged run is visible too.

No subprocess is spawned: liveness comes from ctypes OpenProcess/GetProcessTimes directly.
That is deliberate. This runs inside the SessionStart hook, and shelling out to
tasklist/wmic/Get-CimInstance would both cost seconds and flash console windows (the
CREATE_NO_WINDOW popup class of bug). One ctypes call per pid file is microseconds.

Usage:
    python tools/pid_reconcile.py                 # human-readable table, all pid files
    python tools/pid_reconcile.py --hook          # 1-6 compact lines for the SessionStart hook
    python tools/pid_reconcile.py --json          # machine-readable, for the GUI/dashboard
    python tools/pid_reconcile.py --self-test     # proves the PID-reuse guard actually guards
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
SCRATCH = REPO / 'scratch'
REPORT = REPO / 'data' / 'pid_reconcile_report.json'

# A process whose creation time is later than its own pid file's mtime by more than this is a
# DIFFERENT process that inherited the number. Tolerance covers clock granularity and the gap
# between spawn and the pid file actually landing on disk; it is deliberately small, because
# the failure it prevents (a dead run reported LIVE) is worse than the one it causes (a live
# run reported STALE_PID_REUSE, which is loud and self-correcting).
REUSE_TOLERANCE_SEC = 120.0

# Only pid files younger than this raise the DEAD-BUT-CLAIMED-LIVE alarm. Older ones are
# counted but not shouted about -- scratch/ is never swept, so ancient pid files are expected
# debris and alarming on them would train the reader to ignore the alarm.
DEFAULT_ALARM_AGE_DAYS = 2.0

# Completion markers. THIS LIST IS A COUPLING to the experiment harness's output format --
# see CLAUDE.md "A doc parsed by code is coupled to it". If a cell prints a new kind of
# finishing line, add it here or that cell will be misreported as dead-but-unfinished.
#
# Measured 2026-08-16, NOT assumed: the project uses at least THREE completion conventions,
# and an earlier version of this file keyed on '[done]' alone. That single-marker version
# misclassified 18 COMPLETED runs as DEAD_BUT_CLAIMED_LIVE -- including syn_full ('WROTE
# ...metrics.json'), tcc_full ('[run] WROTE ...results_full.json'), sro_cell1 ('WROTE
# ...cell1.json'), px2_full ('VERDICT: ...') and perirhinal_full ('WROTE ...metrics.json').
# An over-firing alarm is not a safe default here: 24 alarms teaches the reader to skip the
# block, which reproduces the exact blindness this tool exists to remove.
# A FOURTH convention turned up on re-check: some cells end with a terminal JSON summary
# object instead of any prose line -- v1b_full closes with {"verdict": "NO_ASSET_CLEARS_..."}
# and _relsupply_thematic with a stats block whose last key is "elapsed_s". Both were false
# alarms until these two keys were added.
#
# SAFETY PROPERTY that makes a slightly-loose list acceptable: a crash marker is checked
# independently and OUTRANKS a done marker into DEAD_COMPLETED_WITH_ERRORS, which still
# alarms. So a done-marker false-positive on a crashed run cannot silence the crash.
# Treat DEAD_BUT_CLAIMED_LIVE as "no marker I recognise" -- a prompt to LOOK, not a verdict.
DONE_MARKERS = ('[done]', 'WROTE ', 'VERDICT:', '"verdict"', '"elapsed_s"')
CRASH_MARKERS = ('Traceback (most recent call last)',)

LOG_SUFFIXES = ('.out', '.log', '.err')
TAIL_BYTES = 8192

STATE_LIVE = 'LIVE'
STATE_COMPLETED = 'DEAD_COMPLETED'
STATE_COMPLETED_ERR = 'DEAD_COMPLETED_WITH_ERRORS'
STATE_CRASHED = 'DEAD_CRASHED'
STATE_CLAIMED_LIVE = 'DEAD_BUT_CLAIMED_LIVE'
STATE_NO_EVIDENCE = 'DEAD_NO_LOG_EVIDENCE'
STATE_REUSE = 'DEAD_PID_REUSED'
STATE_BAD = 'UNREADABLE_PID_FILE'

# States that mean "a human should look at this". DEAD_NO_LOG_EVIDENCE is deliberately NOT
# here: an empty or absent log proves nothing either way, and most such pid files are old
# debris (scratch/ is never swept). Claiming an alarm on absence-of-evidence is the
# "an absence claim requires an enumeration, not a search" error in operational clothing.
ALARM_STATES = (STATE_CLAIMED_LIVE, STATE_CRASHED, STATE_COMPLETED_ERR, STATE_REUSE)
ALL_STATES = (STATE_LIVE, STATE_COMPLETED, STATE_COMPLETED_ERR, STATE_CRASHED,
              STATE_CLAIMED_LIVE, STATE_NO_EVIDENCE, STATE_REUSE, STATE_BAD)


# ---------------------------------------------------------------------------------------
# liveness (ctypes; no subprocess, no popup)
# ---------------------------------------------------------------------------------------
_STILL_ACTIVE = 259
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def _win_proc_create_time(pid: int) -> Optional[float]:
    """Unix timestamp of the process's creation, or None if it is not running.

    None means genuinely-not-running: either OpenProcess failed (no such pid) or the process
    has an exit code other than STILL_ACTIVE (a terminated process whose handle is still held
    open by something -- the classic 'zombie' that a bare existence check counts as alive).
    """
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    k32.GetProcessTimes.restype = wintypes.BOOL
    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k32.GetExitCodeProcess.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = [wintypes.HANDLE]

    h = k32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return None
    try:
        code = wintypes.DWORD()
        if k32.GetExitCodeProcess(h, ctypes.byref(code)) and code.value != _STILL_ACTIVE:
            return None
        creation = wintypes.FILETIME()
        exit_ft, kernel_ft, user_ft = (wintypes.FILETIME() for _ in range(3))
        if not k32.GetProcessTimes(h, ctypes.byref(creation), ctypes.byref(exit_ft),
                                   ctypes.byref(kernel_ft), ctypes.byref(user_ft)):
            # Running, but we cannot read its clock (happens for processes at a higher
            # integrity level). Report alive with an unknown birth time rather than guessing.
            return float('nan')
        ticks = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        return (ticks - 116444736000000000) / 1e7
    finally:
        k32.CloseHandle(h)


def _posix_proc_create_time(pid: int) -> Optional[float]:
    """POSIX fallback so this module stays importable and self-testable off Windows."""
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return None
    try:
        return Path(f'/proc/{pid}').stat().st_ctime
    except OSError:
        return float('nan')


def proc_create_time(pid: int) -> Optional[float]:
    """Creation timestamp if the pid is running, else None. NaN = running, birth time unknown."""
    if pid <= 0:
        return None
    try:
        if sys.platform == 'win32':
            return _win_proc_create_time(pid)
        return _posix_proc_create_time(pid)
    except Exception:
        # A liveness probe must never be the thing that breaks a session start.
        return None


# ---------------------------------------------------------------------------------------
# log reading
# ---------------------------------------------------------------------------------------
def _tail(path: Path, nbytes: int = TAIL_BYTES) -> str:
    try:
        size = path.stat().st_size
        with path.open('rb') as fh:
            if size > nbytes:
                fh.seek(size - nbytes)
            return fh.read().decode('utf-8', errors='replace')
    except OSError:
        return ''


def classify_logs(stem: str, scratch: Path) -> Dict[str, object]:
    """Look at the sibling logs and say whether the run finished, crashed, or said nothing."""
    found: List[str] = []
    done = False
    crashed = False
    newest = 0.0
    nbytes = 0
    for suf in LOG_SUFFIXES:
        p = scratch / (stem + suf)
        if not p.exists():
            continue
        found.append(p.name)
        try:
            st = p.stat()
            newest = max(newest, st.st_mtime)
            nbytes += st.st_size
        except OSError:
            pass
        text = _tail(p)
        if any(m in text for m in DONE_MARKERS):
            done = True
        if any(m in text for m in CRASH_MARKERS):
            crashed = True
    return {'logs': found, 'log_bytes': nbytes, 'done_marker': done,
            'crash_marker': crashed, 'log_mtime': newest or None}


# ---------------------------------------------------------------------------------------
# reconcile
# ---------------------------------------------------------------------------------------
def reconcile(scratch: Path = SCRATCH, alarm_age_days: float = DEFAULT_ALARM_AGE_DAYS,
              now: Optional[float] = None) -> Dict[str, object]:
    now = time.time() if now is None else now
    rows: List[Dict[str, object]] = []

    pid_files = sorted(scratch.glob('*.pid')) if scratch.is_dir() else []
    for pf in pid_files:
        try:
            mtime = pf.stat().st_mtime
            raw = pf.read_text(encoding='utf-8', errors='replace').strip()
        except OSError as exc:
            rows.append({'name': pf.name, 'state': STATE_BAD, 'detail': str(exc)})
            continue

        # Parse STRICTLY. The audit's own first pass mangled a trailing newline into extra
        # digits (re-writing non-digits to '0' turned "26776\r\n" into a different number) and
        # produced a phantom live process. Take the first run of digits and nothing else.
        digits = ''
        for ch in raw:
            if ch.isdigit():
                digits += ch
            elif digits:
                break
        if not digits:
            rows.append({'name': pf.name, 'state': STATE_BAD,
                         'detail': f'no pid in {raw!r}'})
            continue
        pid = int(digits)

        created = proc_create_time(pid)
        info = classify_logs(pf.stem, scratch)
        age_days = (now - mtime) / 86400.0

        if created is None:
            running = False
            reused = False
        else:
            running = True
            # NaN creation time = alive but unreadable clock; do not accuse it of reuse.
            reused = (created == created) and (created > mtime + REUSE_TOLERANCE_SEC)

        if running and not reused:
            state = STATE_LIVE
        elif running and reused:
            state = STATE_REUSE
        elif info['done_marker'] and info['crash_marker']:
            # Both. Do NOT quietly call this a success: a run can print a traceback and still
            # write a metrics file, and which one matters is a judgement for a human.
            state = STATE_COMPLETED_ERR
        elif info['done_marker']:
            state = STATE_COMPLETED
        elif info['crash_marker']:
            state = STATE_CRASHED
        elif not info['log_bytes']:
            state = STATE_NO_EVIDENCE
        else:
            state = STATE_CLAIMED_LIVE

        rows.append({
            'name': pf.name, 'stem': pf.stem, 'pid': pid,
            'pidfile_mtime': mtime, 'age_days': round(age_days, 3),
            'proc_create_time': None if created is None else (
                None if created != created else created),
            'state': state, 'recent': age_days <= alarm_age_days, **info,
        })

    def _count(st: str) -> int:
        return sum(1 for r in rows if r.get('state') == st)

    alarms = [r for r in rows if r.get('state') in ALARM_STATES and r.get('recent')]
    alarms.sort(key=lambda r: r.get('pidfile_mtime') or 0, reverse=True)
    return {
        'generated': now,
        'scratch': str(scratch),
        'n_pid_files': len(rows),
        'counts': {s: _count(s) for s in ALL_STATES},
        'alarms': alarms,
        'rows': rows,
    }


# ---------------------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------------------
def render_hook(rep: Dict[str, object]) -> str:
    """Compact block for the SessionStart hook. Bounded output: never more than ~8 lines."""
    c = rep['counts']  # type: ignore[index]
    alarms = rep['alarms']  # type: ignore[index]
    head = (f"[pid-reconcile] {rep['n_pid_files']} pid files | "
            f"live={c[STATE_LIVE]} done={c[STATE_COMPLETED]} "
            f"crashed={c[STATE_CRASHED]} stopped-midway={c[STATE_CLAIMED_LIVE]} "
            f"no-log={c[STATE_NO_EVIDENCE]} pid-reused={c[STATE_REUSE]}")
    if not alarms:
        return head + ("\n    no recent run is dead-but-claimed-live"
                       "\n    (a pid file is a birth certificate, not a pulse -- LIVE above is"
                       " the only count that means still running)")
    lines = [head,
             f"    {len(alarms)} RECENT RUN(S) DEAD WITHOUT FINISHING <-- do not describe these as live"]
    for r in alarms[:5]:
        hrs = float(r['age_days']) * 24.0  # type: ignore[arg-type]
        lines.append(f"    {r['state']:<26} {r['stem']} (pid {r['pid']}, {hrs:.1f}h ago)")
    if len(alarms) > 5:
        lines.append(f"    ... and {len(alarms) - 5} more (python tools/pid_reconcile.py)")
    return '\n'.join(lines)


def render_table(rep: Dict[str, object]) -> str:
    rows = sorted(rep['rows'], key=lambda r: r.get('pidfile_mtime') or 0)  # type: ignore[index]
    out = [f"{'state':<22} {'pid':>7}  {'age':>8}  name",
           '-' * 78]
    for r in rows:
        if r.get('state') == STATE_BAD:
            out.append(f"{STATE_BAD:<22} {'-':>7}  {'-':>8}  {r['name']}  ({r.get('detail')})")
            continue
        age_h = float(r['age_days']) * 24.0  # type: ignore[arg-type]
        out.append(f"{r['state']:<22} {r['pid']:>7}  {age_h:>7.1f}h  {r['stem']}")
    c = rep['counts']  # type: ignore[index]
    out.append('-' * 78)
    out.append('  '.join(f'{k}={v}' for k, v in c.items()))  # type: ignore[union-attr]
    return '\n'.join(out)


# ---------------------------------------------------------------------------------------
# self-test -- the guard is the whole point, so prove it
# ---------------------------------------------------------------------------------------
def _self_test() -> int:
    """Prove the three properties that make this tool trustworthy, using FIXTURES in a
    tempdir. Never reads the real scratch/. The PID-reuse case is tested against THIS
    process's own live pid, which is by construction older than a pid file we write now --
    exactly the shape of the 2026-08-16 false-alive."""
    import tempfile
    ok = True
    me = os.getpid()

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)

        # 1. PID REUSE: a LIVE pid whose process predates the pid file by more than the
        #    tolerance must NOT be reported LIVE. This is the exact false-alive that made a
        #    dead 11:57 run look alive because a 22:04 process inherited its number.
        (d / 'reused.pid').write_text(f'{me}\n', encoding='utf-8')
        old = time.time() - 6 * 3600
        os.utime(d / 'reused.pid', (old, old))
        rep = reconcile(d)
        st = {r['stem']: r['state'] for r in rep['rows']}  # type: ignore[index]
        if st.get('reused') == STATE_REUSE:
            print('[self-test] PASS: live-but-older-than-its-pid-file is caught as PID reuse')
        else:
            print(f"[self-test] FAIL: pid reuse not caught, got {st.get('reused')!r}")
            ok = False

        # 2. A genuinely live run (pid file written now, process already running) is LIVE.
        (d / 'genuine.pid').write_text(f'{me}\n', encoding='utf-8')
        rep = reconcile(d)
        st = {r['stem']: r['state'] for r in rep['rows']}  # type: ignore[index]
        if st.get('genuine') == STATE_LIVE:
            print('[self-test] PASS: a genuinely-live pid is reported LIVE')
        else:
            print(f"[self-test] FAIL: live pid misreported as {st.get('genuine')!r}")
            ok = False

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        # 3. Outcome classification for DEAD pids: completed vs crashed vs silent.
        #    PID 0 is never a real process, so all three are guaranteed dead.
        (d / 'fin.pid').write_text('0\n', encoding='utf-8')
        (d / 'fin.out').write_text('working\n[done] wrote metrics.json (12.0s)\n', encoding='utf-8')
        (d / 'boom.pid').write_text('0\n', encoding='utf-8')
        (d / 'boom.err').write_text('Traceback (most recent call last):\nIndexError: x\n',
                                    encoding='utf-8')
        (d / 'silent.pid').write_text('0\n', encoding='utf-8')
        (d / 'silent.out').write_text('starting up\n', encoding='utf-8')
        # 4. A pid file with a trailing CRLF must parse as the SAME pid, not a mangled one.
        (d / 'crlf.pid').write_text('0\r\n', encoding='utf-8')
        # 5. The OTHER two real completion conventions must count as finished. Keying on
        #    '[done]' alone misread 18 finished runs as unfinished on 2026-08-16.
        (d / 'wrote.pid').write_text('0\n', encoding='utf-8')
        (d / 'wrote.out').write_text('WROTE D:\\x\\metrics.json\n', encoding='utf-8')
        (d / 'verdict.pid').write_text('0\n', encoding='utf-8')
        (d / 'verdict.out').write_text('VERDICT: SOMETHING_CLEARS_THE_FLOOR\n', encoding='utf-8')
        # 6. No log at all is absence of evidence, NOT evidence of a stopped run.
        (d / 'nolog.pid').write_text('0\n', encoding='utf-8')
        # 7. Finished AND traceback must be flagged separately, never quietly called success.
        (d / 'both.pid').write_text('0\n', encoding='utf-8')
        (d / 'both.out').write_text('Traceback (most recent call last):\nE\n[done] ok\n',
                                    encoding='utf-8')

        rep = reconcile(d)
        st = {r['stem']: r['state'] for r in rep['rows']}  # type: ignore[index]
        pids = {r['stem']: r.get('pid') for r in rep['rows']}  # type: ignore[index]
        for stem, want in (('fin', STATE_COMPLETED), ('boom', STATE_CRASHED),
                           ('silent', STATE_CLAIMED_LIVE), ('wrote', STATE_COMPLETED),
                           ('verdict', STATE_COMPLETED), ('nolog', STATE_NO_EVIDENCE),
                           ('both', STATE_COMPLETED_ERR)):
            if st.get(stem) == want:
                print(f'[self-test] PASS: {stem} classified {want}')
            else:
                print(f'[self-test] FAIL: {stem} expected {want}, got {st.get(stem)!r}')
                ok = False
        if pids.get('crlf') == 0:
            print('[self-test] PASS: trailing CRLF does not corrupt the parsed pid')
        else:
            print(f"[self-test] FAIL: CRLF pid parsed as {pids.get('crlf')!r}, expected 0")
            ok = False

        alarm_stems = {a['stem'] for a in rep['alarms']}  # type: ignore[index]
        want_in = {'boom', 'silent', 'both'}
        want_out = {'fin', 'wrote', 'verdict', 'nolog'}
        if want_in <= alarm_stems and not (want_out & alarm_stems):
            print('[self-test] PASS: alarms cover crashed/stopped/mixed, and exclude '
                  'all 3 completion conventions + the no-evidence case')
        else:
            print(f'[self-test] FAIL: alarm set was {alarm_stems}')
            ok = False

    print(f"[self-test] {'ALL PASS' if ok else 'FAILED'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--hook', action='store_true', help='compact bounded output for SessionStart')
    ap.add_argument('--json', action='store_true', help='machine-readable report to stdout')
    ap.add_argument('--self-test', action='store_true', help='prove the guards')
    ap.add_argument('--alarm-age-days', type=float, default=DEFAULT_ALARM_AGE_DAYS)
    ap.add_argument('--scratch', default=str(SCRATCH))
    ap.add_argument('--no-write', action='store_true', help='do not persist the json report')
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    rep = reconcile(Path(args.scratch), alarm_age_days=args.alarm_age_days)

    # Persist for the GUI/dashboard (owned by a sibling) to read without rescanning.
    if not args.no_write:
        try:
            REPORT.parent.mkdir(parents=True, exist_ok=True)
            tmp = REPORT.with_suffix('.json.tmp')
            tmp.write_text(json.dumps(rep, indent=1), encoding='utf-8')
            os.replace(tmp, REPORT)
        except OSError:
            pass  # reporting must never be fatal

    if args.json:
        print(json.dumps(rep, indent=1))
    elif args.hook:
        print(render_hook(rep))
    else:
        print(render_table(rep))

    # Exit 0 always: this is an OBSERVATION, and a nonzero exit inside the hook would read as
    # a broken probe rather than as a finding.
    return 0


if __name__ == '__main__':
    sys.exit(main())
