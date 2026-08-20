"""What is wrong with the dashboard? Read the diagnostics log and say so in plain words.

    python tools/gui_health.py            # summary
    python tools/gui_health.py --tail 20  # the raw recent records too

WHY THIS EXISTS. The owner reported the window freezing three times. The first two investigations
ended with "I cannot tell you why" -- no crash output, no hung process, nothing left behind to
diagnose from. `status_gui.py` now appends a JSON line for every UI stall, every collect and every
exception; this reads them back. **A log nobody can read is not evidence, it is a second thing to
investigate**, so this prints conclusions, not records.

WHAT COUNTS AS A PROBLEM, and the thresholds are stated rather than implied:
  UI STALL    any work over 250 ms on the drawing thread -- a hitch the owner can SEE. These are
              the freezes. A stall of several seconds is the window going white.
  COLLECT     the background gather. Slow is not a freeze (it runs off-thread) but a collect longer
              than the 20 s refresh interval means refreshes are overlapping, which is its own bug.
  METRICS SCAN the data/ walk. It was ON the UI thread until 2026-08-20 and measured 6.91 s over
              8,155 directories; it is a daemon thread now, so a large number here is EXPECTED and
              harmless. It is reported anyway, because the day it moves back on-thread this is the
              number that says so.
  ERRORS      collector exceptions, with the traceback kept in the log.
"""
import collections
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
LOG = _REPO / "data" / "hook_state" / "status_gui_diag.jsonl"
UI_STALL_MS = 250
REFRESH_MS = 20000


def _pct(vals, p):
    if not vals:
        return 0.0
    s = sorted(vals)
    return s[min(len(s) - 1, int(round(p / 100.0 * (len(s) - 1))))]


def main(argv):
    tail = 0
    if "--tail" in argv:
        i = argv.index("--tail")
        tail = int(argv[i + 1]) if i + 1 < len(argv) else 20

    if not LOG.exists():
        print("No diagnostics log yet at %s" % LOG)
        print("It is written by tools/status_gui.py. If the dashboard has been running and this is")
        print("still missing, THAT is the finding -- the logger itself is not reaching the disk.")
        return 1

    recs = []
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                recs.append(json.loads(line))
            except ValueError:
                pass
    if not recs:
        print("Diagnostics log exists but is empty: %s" % LOG)
        return 1

    by = collections.Counter(r.get("event") for r in recs)
    span = (recs[-1].get("t", 0) - recs[0].get("t", 0)) / 60.0
    print("%d records over %.1f minutes -- %s" % (len(recs), span, dict(by.most_common())))
    print()

    stalls = [r for r in recs if r.get("event") == "ui_stall"]
    if stalls:
        ms = [r.get("ms", 0) for r in stalls]
        print("FREEZES: %d stall(s) over %d ms on the drawing thread." % (len(stalls), UI_STALL_MS))
        print("   worst %.1fs | median %.0fms | most recent %.0fms"
              % (max(ms) / 1000.0, _pct(ms, 50), ms[-1]))
        worst = max(stalls, key=lambda r: r.get("ms", 0))
        detail = {k: v for k, v in worst.items() if k.endswith("_ms")}
        if detail:
            print("   the worst one breaks down as: %s" % detail)
        print("   ^ THIS IS WHAT THE OWNER SEES AS THE WINDOW HANGING.")
    else:
        print("FREEZES: none recorded. No work over %d ms has run on the drawing thread."
              % UI_STALL_MS)
    print()

    col = [r.get("ms", 0) for r in recs if r.get("event") == "collect"]
    if col:
        over = sum(1 for m in col if m > REFRESH_MS)
        print("BACKGROUND GATHER: %d run(s), median %.0fms, worst %.1fs"
              % (len(col), _pct(col, 50), max(col) / 1000.0))
        if over:
            print("   ⚠ %d run(s) took longer than the %ds refresh interval -- refreshes are"
                  % (over, REFRESH_MS // 1000))
            print("     overlapping. Slow here does NOT freeze the window, but it is its own bug.")
        else:
            print("   fits inside the %ds refresh interval." % (REFRESH_MS // 1000))
    print()

    scan = [r.get("ms", 0) for r in recs if r.get("event") == "metrics_scan"]
    if scan:
        print("data/ SCAN (off-thread since 2026-08-20): %d run(s), worst %.1fs over %s dirs"
              % (len(scan), max(scan) / 1000.0, recs[-1].get("dirs", "?")))
        print("   Large is EXPECTED and harmless here. It froze the window when it ran on-thread.")
    print()

    errs = [r for r in recs if str(r.get("event", "")).endswith("_error")]
    if errs:
        print("ERRORS: %d" % len(errs))
        for r in errs[-3:]:
            print("   %s: %s" % (r.get("event"), str(r.get("err"))[:140]))
        print("   (full tracebacks are in the log)")
    else:
        print("ERRORS: none recorded.")

    if tail:
        print("\n--- last %d records ---" % tail)
        for r in recs[-tail:]:
            print("   %s" % json.dumps(r, default=str)[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
