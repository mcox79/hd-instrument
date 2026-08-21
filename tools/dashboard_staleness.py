"""WHICH DASHBOARD PANELS ARE LYING ABOUT BEING CURRENT? -- report, and optionally stamp.

OWNER, 2026-08-21 (COMMENTARY): "there are a lot of very old and not updated tabs in the gui - can
we refresh and /or clean it up?"

DIAGNOSIS. They are stale because their WRITERS WERE RETIRED AND NOTHING TOOK OVER. `data/
fleet_status_NOW.md` calls itself "overwritten by Testbed each cycle" and carries "Last update:
2026-06-30"; grep finds no tool in tools/ that writes it at all. The same is true of the queue and
waiting-on panels. They are relics of the 4-session fleet architecture, which is DEAD (CLAUDE.md /
memory: "4-session model DEAD; agent-spawn only").

WHY STAMPING RATHER THAN DELETING. The harm is not that the files exist -- it is that a panel titled
`fleet_status_NOW` reads as NOW when its content is from June. A banner fixes exactly that harm, is
reversible, and destroys nothing. Deleting a directory of the owner's working files unattended is
not this tool's call; see the standing rule against bundling deletions with real work.

The banner is IDEMPOTENT: re-running replaces the existing banner rather than stacking a second one,
so this can be run on a schedule without the files growing a stack of notices.

Usage:
    python tools/dashboard_staleness.py                 # report only, changes nothing
    python tools/dashboard_staleness.py --apply         # stamp panels over the threshold
    python tools/dashboard_staleness.py --days 45       # change the threshold
    python tools/dashboard_staleness.py --self-test
"""
import argparse
import datetime
import glob
import os
import re
import sys
import time

MARK_OPEN = "<!-- STALENESS-BANNER -->"
MARK_CLOSE = "<!-- /STALENESS-BANNER -->"
DEFAULT_DAYS = 30

# Panels that NAME THEMSELVES as live state. A stale one of these actively misleads; a stale
# document that never claimed to be current (a plan, a README) merely ages.
CLAIMS_TO_BE_CURRENT = re.compile(
    r"(_now|inflight|status|queue|waiting_on|questions|responses|latest|instructions)", re.I)


def panels(root="data"):
    return sorted(glob.glob(os.path.join(root, "*.md")))


def age_days(path):
    return (time.time() - os.path.getmtime(path)) / 86400.0


def strip_banner(text):
    if MARK_OPEN not in text:
        return text
    head, _, rest = text.partition(MARK_OPEN)
    _, _, tail = rest.partition(MARK_CLOSE)
    return (head + tail).lstrip("\n")


def banner_for(path, days):
    stamp = datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
    return (f"{MARK_OPEN}\n"
            f"> # ⚠️ STALE PANEL -- LAST WRITTEN {stamp} ({days:.0f} DAYS AGO). NOT CURRENT STATE.\n"
            f"> **Nothing writes this file any more.** It is a relic of the retired 4-session fleet\n"
            f"> architecture. Read `notes/STATUS.md` and `notes/BUILD_PLAN_post_audit_2026-08-19.md`\n"
            f"> for current state, and `notes/BOARD.md` for anything waiting on you.\n"
            f"> *Banner stamped by `tools/dashboard_staleness.py`; re-running replaces it rather\n"
            f"> than stacking another. Delete the marker pair to remove it.*\n"
            f"{MARK_CLOSE}\n\n")


def run(threshold=DEFAULT_DAYS, apply=False, root="data"):
    rows, stamped = [], 0
    for p in panels(root):
        a = age_days(p)
        claims = bool(CLAIMS_TO_BE_CURRENT.search(os.path.basename(p)))
        rows.append((a, p, claims))
    rows.sort(reverse=True)
    print(f"{'days':>6} {'claims-current':>15}  panel")
    for a, p, claims in rows:
        flag = "YES <-- misleads" if claims else "no"
        print(f"{a:>6.0f} {flag:>15}  {p}")
    print()
    targets = [(a, p) for a, p, c in rows if c and a >= threshold]
    print(f"{len(targets)} panel(s) both CLAIM to be current and are >= {threshold} days stale.")
    if not apply:
        print("(report only -- pass --apply to stamp them)")
        return 0
    for a, p in targets:
        with open(p, encoding="utf-8") as fh:
            text = fh.read()
        mtime = os.path.getmtime(p)                       # preserve: the age IS the evidence
        new = banner_for(p, a) + strip_banner(text)
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(new)
        os.utime(p, (mtime, mtime))
        stamped += 1
        print(f"  stamped {p}")
    print(f"stamped {stamped} panel(s); mtimes preserved so the reported age stays honest.")
    return 0


def _self_test():
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "fleet_status_NOW.md")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# FLEET STATUS\n\nbody line\n")
        old = time.time() - 60 * 86400
        os.utime(p, (old, old))
        run(threshold=30, apply=True, root=td)
        t1 = open(p, encoding="utf-8").read()
        if MARK_OPEN in t1 and "body line" in t1:
            print("[self-test] PASS banner applied and the original content survives")
        else:
            print("[self-test] FAIL banner or content missing")
            ok = False
        # IDEMPOTENT: a second run must not stack a second banner.
        run(threshold=30, apply=True, root=td)
        t2 = open(p, encoding="utf-8").read()
        if t2.count(MARK_OPEN) == 1:
            print("[self-test] PASS re-running replaces the banner, never stacks it")
        else:
            print(f"[self-test] FAIL banner stacked {t2.count(MARK_OPEN)}x")
            ok = False
        if abs(os.path.getmtime(p) - old) < 2:
            print("[self-test] PASS mtime preserved, so the reported age stays honest")
        else:
            print("[self-test] FAIL stamping reset the mtime -- the file would look fresh")
            ok = False
        # A FRESH panel must NOT be stamped, or the banner is cry-wolf.
        q = os.path.join(td, "inflight_status.md")
        with open(q, "w", encoding="utf-8") as fh:
            fh.write("# fresh\n")
        run(threshold=30, apply=True, root=td)
        if MARK_OPEN not in open(q, encoding="utf-8").read():
            print("[self-test] PASS a fresh panel is left alone")
        else:
            print("[self-test] FAIL stamped a fresh panel")
            ok = False
        # A stale panel that never CLAIMED to be current must also be left alone.
        r = os.path.join(td, "research_master_plan.md")
        with open(r, "w", encoding="utf-8") as fh:
            fh.write("# a plan, not a status\n")
        os.utime(r, (old, old))
        run(threshold=30, apply=True, root=td)
        if MARK_OPEN not in open(r, encoding="utf-8").read():
            print("[self-test] PASS a stale PLAN is left alone (it never claimed to be current)")
        else:
            print("[self-test] FAIL stamped a document that never claimed to be live state")
            ok = False
    print("[self-test] " + ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--days", type=float, default=DEFAULT_DAYS)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return _self_test()
    return run(a.days, a.apply)


if __name__ == "__main__":
    sys.exit(main())
