#!/usr/bin/env python
"""ARM / DISARM the Stop-hook continuation loop. One command each way.

WHY A FILE AND NOT AN ENV VAR: the owner has to be able to stop this instantly, possibly from a
phone, possibly hours later, possibly after the session that armed it is gone. An env var lives
in a process the owner cannot reach. A file on disk is reachable from a text editor, from another
session, and from this tool.

WHY NOT "DELETE A FLAG FILE" (the obvious design, and it is WRONG HERE): every deletion command
in this environment is auto-denied (`Bash(rm -f:*)`, `Bash(rm -r:*)`,
`PowerShell(Remove-Item:*)` are all in `permissions.deny`; a 2026-08-13 audit found 31 of 31
auto-denies contained a deletion token). A disarm that requires a delete is a disarm that fails
exactly when it is needed. So DISARM IS A WRITE, never a delete.

THREE WAYS TO DISARM, in order of convenience. All are one step.
  1. `python tools/autoloop.py disarm`
  2. open `data/hook_state/autoloop.json` in any editor, set `"armed": false`, save
  3. delete or corrupt the file by any means -- absent/unparseable/anything-but-exactly-true
     reads as DISARMED. The fail-safe direction is OFF.

STATE FILE `data/hook_state/autoloop.json`:
  {
    "armed":             bool,        false unless EXACTLY boolean true. Fail-safe: OFF.
    "max_continuations": int | str,   per-session cap on Stop-hook continuations.
                                      0 / "unlimited" / "none" / -1  ==  NO LIMIT.
                                      This is GUARD 2 of the Stop hook. It is a VISIBLE SETTING,
                                      not a deleted safety: the hook prints "continuation N/M"
                                      (or "N/unlimited") into every single block reason, so an
                                      uncapped run announces itself on every turn.
    "armed_at":          str | null,  UTC ISO-8601
    "armed_by":          str | null,  free text, whoever/whatever armed it
    "sessions":          [str] | absent,
                                      SESSION ALLOWLIST. ABSENT or EMPTY == every session (this
                                      is the legacy behaviour and is preserved exactly). When
                                      non-empty, ONLY those session keys are driven by the loop.
                                      See session_allowed().
    "note":              str
  }

SESSION SCOPING (added 2026-08-22). Before this, `armed` was GLOBAL: arming the loop in one
session drove the Stop hook in EVERY session on this repo, including a solver session doing
bounded work that nobody wanted continued. The allowlist fixes that without changing the
fail-safe: absent/empty still means "all", so an existing state file behaves as it always did.

  COUPLING, BOTH SIDES (CLAUDE.md "a doc parsed by code is coupled to it"):
  `data/hooks/staging/stop_hook.py` reads this via `session_allowed(session)` at its autoloop
  gate and at its continuation-chain gate. If the field name changes here, change it there in
  the same commit.

CAP PRECEDENCE (resolve_cap): env `HD_STOP_HOOK_HARD_CAP` > this file > built-in default 10.
The env var is kept because it predates this file and something may still set it.

USAGE
  python tools/autoloop.py status
  python tools/autoloop.py arm [--max N | --max unlimited] [--by NAME]
  python tools/autoloop.py disarm
  python tools/autoloop.py set-cap <N|unlimited>
  python tools/autoloop.py self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
# HD_AUTOLOOP_STATE exists so the Stop hook's end-to-end self-test can point a REAL subprocess run
# of the hook at a throwaway state file. It is NOT an arming mechanism and NOT a supported way to
# run the loop: the hook reports the path it actually used in every block reason, so a redirected
# state file is visible, never silent.
DEFAULT_STATE = Path(os.environ.get("HD_AUTOLOOP_STATE")
                     or (REPO_ROOT / "data" / "hook_state" / "autoloop.json"))

DEFAULT_CAP = 10                      # the value GUARD 2 has always used
UNLIMITED_TOKENS = {"unlimited", "none", "no", "off", "inf", "infinite", ""}
ENV_CAP = "HD_STOP_HOOK_HARD_CAP"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state(path: Path = DEFAULT_STATE) -> dict:
    """Never raises. Anything unreadable reads as DISARMED."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return data
    except (OSError, json.JSONDecodeError, ValueError, UnicodeDecodeError):
        return {}


def is_armed(path: Path = DEFAULT_STATE) -> bool:
    """ARMED only when `armed` is EXACTLY boolean true. A string "true", a 1, a missing file, a
    truncated write, a half-saved editor buffer -- all DISARMED. Fail-safe is OFF."""
    return load_state(path).get("armed") is True


def session_allowed(session: str, path: Path = DEFAULT_STATE) -> bool:
    """Is THIS session driven by the loop? Absent/empty allowlist == every session (legacy).

    READ BY: data/hooks/staging/stop_hook.py (autoloop gate + continuation-chain gate).
    Fail-safe note: this widens nothing. `armed` is still checked separately and independently,
    so a junk state file is DISARMED before this function is ever consulted.
    """
    raw = load_state(path).get("sessions")
    if not isinstance(raw, list) or not raw:
        return True                       # legacy / unscoped: drive everything
    return str(session) in {str(s) for s in raw}


def _parse_cap(value) -> int | None:
    """Return an int cap, or None for unlimited. None is also returned for junk -- but only from
    the FILE, never from the built-in default, so junk can never silently uncap a disarmed run
    (see resolve_cap)."""
    if value is None:
        return DEFAULT_CAP
    if isinstance(value, bool):
        return DEFAULT_CAP
    if isinstance(value, int):
        return None if value <= 0 else value
    s = str(value).strip().casefold()
    if s in UNLIMITED_TOKENS:
        return None
    try:
        n = int(s)
    except ValueError:
        return DEFAULT_CAP
    return None if n <= 0 else n


def resolve_cap(path: Path = DEFAULT_STATE, env: dict | None = None) -> int | None:
    """The single cap resolution used by the Stop hook's GUARD 2.
    Returns an int (cap) or None (unlimited). Precedence: env > file > DEFAULT_CAP."""
    env = os.environ if env is None else env
    raw = env.get(ENV_CAP)
    if raw is not None and str(raw).strip() != "":
        return _parse_cap(raw)
    state = load_state(path)
    if "max_continuations" in state:
        return _parse_cap(state.get("max_continuations"))
    return DEFAULT_CAP


def cap_label(cap: int | None) -> str:
    return "unlimited" if cap is None else str(cap)


def _write(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=2)
        fh.write("\n")
    os.replace(str(tmp), str(path))


def arm(max_continuations, by: str, path: Path = DEFAULT_STATE,
        sessions: list | None = None) -> dict:
    """Arm the loop. `sessions=None` clears the allowlist (drive EVERY session -- the legacy
    behaviour of a bare `arm`). A non-empty list scopes the loop to exactly those session keys."""
    state = load_state(path)
    state.update({
        "armed": True,
        "max_continuations": max_continuations,
        "armed_at": _now(),
        "armed_by": by,
        "note": ("The Stop hook will keep this session going. DISARM WITH: "
                 "python tools/autoloop.py disarm   (or set armed=false here and save)."),
    })
    if sessions:
        state["sessions"] = [str(s) for s in sessions]
    else:
        state.pop("sessions", None)       # explicit: a bare arm() means EVERY session
    _write(path, state)
    return state


def disarm(path: Path = DEFAULT_STATE) -> dict:
    """A WRITE, not a delete -- deletes are auto-denied in this environment."""
    state = load_state(path)
    state.update({"armed": False, "disarmed_at": _now(),
                  "note": "DISARMED. The Stop hook will not force continuations."})
    _write(path, state)
    return state


def set_cap(value, path: Path = DEFAULT_STATE) -> dict:
    state = load_state(path)
    state.setdefault("armed", False)
    state["max_continuations"] = value
    _write(path, state)
    return state


def status_line(path: Path = DEFAULT_STATE) -> str:
    armed = is_armed(path)
    cap = resolve_cap(path)
    src = "env " + ENV_CAP if os.environ.get(ENV_CAP) else (
        "file" if "max_continuations" in load_state(path) else "built-in default")
    return (f"autoloop: {'ARMED' if armed else 'DISARMED'} | "
            f"max_continuations={cap_label(cap)} (from {src}) | state={path}")


# ---------------------------------------------------------------------------

def self_test() -> int:
    import tempfile
    ok = True

    def check(cond, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if cond else 'FAIL'} {label}",
              file=sys.stdout if cond else sys.stderr)
        if not cond:
            ok = False

    td = Path(tempfile.mkdtemp(prefix="autoloop_selftest_"))
    p = td / "autoloop.json"
    env: dict = {}

    check(not is_armed(p), "a MISSING state file reads as DISARMED (fail-safe default)")
    check(resolve_cap(p, env) == DEFAULT_CAP, f"missing file -> default cap {DEFAULT_CAP}")

    arm(0, "self-test", p)
    check(is_armed(p), "arm() arms")
    check(resolve_cap(p, env) is None, "max_continuations=0 means UNLIMITED")
    check(cap_label(resolve_cap(p, env)) == "unlimited", "unlimited renders as 'unlimited'")

    set_cap(25, p)
    check(resolve_cap(p, env) == 25, "set-cap 25 takes effect")
    set_cap("unlimited", p)
    check(resolve_cap(p, env) is None, "the string 'unlimited' means unlimited")

    disarm(p)
    check(not is_armed(p), "disarm() disarms")
    check(json.loads(p.read_text(encoding="utf-8"))["armed"] is False,
          "disarm WRITES armed=false (does not delete -- deletes are auto-denied here)")
    check(resolve_cap(p, env) is None, "the cap setting survives a disarm (it is a setting)")

    # Fail-safe: everything that is not exactly boolean true is DISARMED.
    for junk in ('{"armed": "true"}', '{"armed": 1}', '{"armed": "yes"}',
                 '{"armed": tru', 'not json at all', '', '[]', '{}'):
        p.write_text(junk, encoding="utf-8")
        if is_armed(p):
            check(False, f"junk state {junk!r:24} must read DISARMED")
            break
    else:
        check(True, "every non-boolean-true / corrupt / truncated state reads DISARMED")

    # A corrupt file must NOT uncap anything either.
    p.write_text("not json at all", encoding="utf-8")
    check(resolve_cap(p, env) == DEFAULT_CAP,
          "a corrupt state file falls back to the DEFAULT cap, never to unlimited")
    p.write_text('{"armed": true, "max_continuations": "banana"}', encoding="utf-8")
    check(resolve_cap(p, env) == DEFAULT_CAP,
          "a junk cap value falls back to the DEFAULT cap, never to unlimited")

    # --- SESSION ALLOWLIST, with a POSITIVE control on BOTH sides -------------------------------
    # The failure this prevents, measured 2026-08-22: `armed` was global, so a strategy session
    # arming the loop also drove a solver session doing bounded work nobody wanted continued.
    arm(5, "self-test", p)
    check(session_allowed("anySession", p) and session_allowed("otherSession", p),
          "no allowlist -> EVERY session is driven (legacy behaviour preserved)")

    arm(5, "self-test", p, sessions=["strategyKey"])
    check(session_allowed("strategyKey", p),
          "POSITIVE CONTROL: the allowlisted session IS driven")
    check(not session_allowed("auto_7c6e8deae7", p),
          "NEGATIVE CONTROL: a non-allowlisted session (the solver) is NOT driven")
    check(is_armed(p), "scoping does not disarm -- `armed` is still true")

    arm(5, "self-test", p)                       # bare arm clears the allowlist again
    check("sessions" not in load_state(p), "a bare arm() CLEARS the allowlist")
    check(session_allowed("auto_7c6e8deae7", p), "...and everything is driven again")

    # A junk allowlist must not lock everyone out AND must not be silently trusted.
    p.write_text('{"armed": true, "sessions": "strategyKey"}', encoding="utf-8")
    check(session_allowed("anything", p),
          "a NON-LIST allowlist falls back to 'all', never to 'nobody' (a lockout is a silent stop)")

    # env beats file
    arm(5, "self-test", p)
    check(resolve_cap(p, {ENV_CAP: "3"}) == 3, "env HD_STOP_HOOK_HARD_CAP overrides the file")
    check(resolve_cap(p, {ENV_CAP: "0"}) is None, "env 0 means unlimited")
    check(resolve_cap(p, {ENV_CAP: ""}) == 5, "an EMPTY env var is ignored, file wins")

    disarm(p)
    print(f"[self-test] leftover temp dir (not auto-removed, by design): {td}")
    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_arm = sub.add_parser("arm")
    p_arm.add_argument("--max", default="unlimited",
                       help="cap on continuations per session; 0 or 'unlimited' for no limit "
                            "(default: unlimited, per the owner's 'no limit' directive)")
    p_arm.add_argument("--by", default="unspecified")
    p_arm.add_argument("--session", action="append", default=None, metavar="KEY",
                       help="scope the loop to this session key (repeatable). Omit to drive "
                            "EVERY session, which is the legacy behaviour.")
    sub.add_parser("disarm")
    sub.add_parser("status")
    p_cap = sub.add_parser("set-cap")
    p_cap.add_argument("value")
    sub.add_parser("self-test")

    args = ap.parse_args(argv)
    p = Path(args.state)

    if args.cmd == "self-test":
        return self_test()
    if args.cmd == "status":
        print(status_line(p))
        return 0
    if args.cmd == "arm":
        raw = args.max
        try:
            raw = int(raw)
        except ValueError:
            pass
        arm(raw, args.by, p, sessions=args.session)
        print(status_line(p))
        if args.session:
            print(f"[autoloop] SCOPED to session(s): {', '.join(args.session)} "
                  f"-- no other session is driven.")
        else:
            print("[autoloop] UNSCOPED: EVERY session on this repo is driven.")
        print("[autoloop] ARMED. Stop it any time with: python tools/autoloop.py disarm")
        return 0
    if args.cmd == "disarm":
        disarm(p)
        print(status_line(p))
        print("[autoloop] DISARMED.")
        return 0
    if args.cmd == "set-cap":
        raw = args.value
        try:
            raw = int(raw)
        except ValueError:
            pass
        set_cap(raw, p)
        print(status_line(p))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
