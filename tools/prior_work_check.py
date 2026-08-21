"""The FOUR prior-work reads, in one command, with counts -- so silence is distinguishable from absence.

**WHY THIS EXISTS: THE RULE FAILED TWICE IN ONE DAY, AND BOTH TIMES THE ARCHIVE HELD THE ANSWER.**

1. **2026-08-21 morning** -- I cited `ORGAN_MAP`'s F5 math row all session and never read line 1440 in
   the same file: *"F5/F6 -- queue behind step 4"*, under a heading reading *"recorded so it is not
   started by accident."*
2. **2026-08-21 evening** -- I built a subsumption diagnostic and reported `SUBSUMED`. The
   2026-08-19 spoke diagnostic had **already caught the exact discriminator error I made** and
   recorded the fix: *"AT independence and BELOW independence mean OPPOSITE things for
   buildability... the correct discriminator is the UNION GAIN."* On the right discriminator the
   verdict is **PARTIAL**, not subsumed. **I built, then checked.**

`CLAUDE.md` already says to query both archives *"and quote the counts"*, and `ORGAN_MAP`'s
corrections make it three. **A fourth was added after testing whether this tool would have caught
the failure it was built for -- IT WOULD NOT: the diagnostic that corrected me lives in a `scratch/`
script cited from a note, and `experiment_index.py` returns 0 of 8,836 cells for "union gain",
correctly, because it was never a cell.** **Three reads spread across three tools is a habit; a habit is not a
guard.** *Same escalation as `rank_with_ties.py`, `replication_gate.py` and `organ_map_cite.py`.*

    python tools/prior_work_check.py "subsumed" "union gain"
    python tools/prior_work_check.py --organ F5 "coherence monitor"

**IT NEVER REPORTS A BARE ZERO.** Each source prints how many rows it SCANNED alongside how many it
matched, because a tool that can return zero without proving it can return non-zero is not a
prior-work check -- the silent-zero defect `director_kb_query.py` shipped and `experiment_index.py`
shipped after it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PY = os.path.join(_REPO, ".venv", "Scripts", "python.exe")
REGISTRY = os.path.join(_REPO, "data", "capability_registry.jsonl")


def _run(args, timeout=600):
    try:
        r = subprocess.run([PY] + args, cwd=_REPO, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return r.stdout or ""
    except Exception as exc:
        return "[FAILED TO RUN: %s]" % exc


def read_results_archive(keywords):
    """READ 2: has this question already been ANSWERED? The one I skipped."""
    print("=" * 88)
    print("READ 2 of 3 -- HAS THE QUESTION ALREADY BEEN ANSWERED?  (tools/experiment_index.py)")
    print("=" * 88)
    total = 0
    for kw in keywords:
        out = _run([os.path.join("tools", "experiment_index.py"), "query", kw])
        scanned = re.search(r"scanned ([\d,]+) indexed cells", out)
        m = re.search(r"(\d+) matching cells \((\d+) landed\)", out)
        n, landed = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
        total += n
        print("\n  %-28s -> %d matching, %d landed   (scanned %s)"
              % ('"%s"' % kw, n, landed, scanned.group(1) if scanned else "?"))
        for line in out.split("\n"):
            if line.startswith("LANDED") or line.strip().startswith("verdict:"):
                print("     " + line.strip()[:120])
    return total


def read_capability_registry(keywords):
    """READ 1: does the tool already EXIST?"""
    print("\n" + "=" * 88)
    print("READ 1 of 3 -- DOES THE TOOL ALREADY EXIST?  (data/capability_registry.jsonl)")
    print("=" * 88)
    if not os.path.exists(REGISTRY):
        print("  registry MISSING at %s -- that is a broken read, not an empty one" % REGISTRY)
        return 0
    rows, hits = 0, []
    with open(REGISTRY, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows += 1
            low = line.lower()
            if any(k.lower() in low for k in keywords):
                try:
                    d = json.loads(line)
                    hits.append((d.get("id", "?"), d.get("gate_decision", "?"),
                                 d.get("pipeline_status", "?")))
                except Exception:
                    hits.append((line[:60], "?", "?"))
    print("  scanned %d registry rows, %d match" % (rows, len(hits)))
    for i, g, ps in hits[:14]:
        print("     %-52s gate=%-6s %s" % (str(i)[:52], g, ps))
    if len(hits) > 14:
        print("     ... and %d more" % (len(hits) - 14))
    return len(hits)


def read_organ_map(organ):
    """READ 3: have we already been WRONG about this mechanism?"""
    print("\n" + "=" * 88)
    print("READ 3 of 3 -- HAVE WE ALREADY BEEN WRONG ABOUT THIS?  (tools/organ_map_cite.py)")
    print("=" * 88)
    if not organ:
        print("  no --organ given. **THIS READ WAS NOT PERFORMED.** If the work touches a brain")
        print("  mechanism, re-run with --organ <ID>; ORGAN_MAP's corrections and SCHEDULING are")
        print("  invisible to the other two archives, and that is exactly what was missed on F5.")
        return None
    out = _run([os.path.join("tools", "organ_map_cite.py"), organ])
    keep = False
    for line in out.split("\n"):
        if "CONSTRAINT LINE" in line or "no scheduling" in line:
            keep = True
        if keep and line.strip():
            print("  " + line.rstrip()[:150])
        if keep and line.startswith("--- the organ"):
            break
    return out.count("CONSTRAINT LINE")


def read_notes(keywords):
    """READ 4: is the answer in a NOTE rather than an indexed cell?

    **ADDED BECAUSE I TESTED WHETHER THIS TOOL WOULD HAVE CAUGHT THE FAILURE IT WAS BUILT FOR, AND
    IT WOULD NOT.** The 2026-08-19 diagnostic that corrected my subsumption discriminator lives in a
    `scratch/` script referenced from a STATUS archive -- **`experiment_index.py` returns 0 of 8,836
    cells for "union gain"**, correctly, because it was never a cell. **A large share of this
    project's findings live in notes, and the three-read rule is blind to all of them.**"""
    import glob
    print("")
    print("=" * 88)
    print("READ 4 of 4 -- IS THE ANSWER IN A NOTE RATHER THAN A CELL?  (notes/*.md)")
    print("=" * 88)
    files = sorted(glob.glob(os.path.join(_REPO, "notes", "*.md")))
    hits, scanned = [], 0
    for f in files:
        try:
            t = open(f, encoding="utf-8").read()
        except Exception:
            continue
        scanned += 1
        low = t.lower()
        for k in keywords:
            if k.lower() in low:
                i = low.index(k.lower())
                line = " ".join(t[max(0, i - 90):i + 110].split())
                hits.append((os.path.basename(f), k, line))
                break
    print("  scanned %d notes, %d contain a keyword" % (scanned, len(hits)))
    for f, k, line in hits[:10]:
        print("     %-64s [%s]" % (f[:64], k))
        print("        ...%s..." % line.encode("ascii", "replace").decode()[:150])
    if len(hits) > 10:
        print("     ... and %d more" % (len(hits) - 10))
    return len(hits)


def main(argv):
    organ = None
    if "--organ" in argv:
        i = argv.index("--organ")
        organ = argv[i + 1].upper()
        argv = argv[:i] + argv[i + 2:]
    keywords = [a for a in argv if not a.startswith("--")]
    if not keywords and not organ:
        print(__doc__)
        return 2
    print("PRIOR-WORK CHECK for %s%s\n" % (", ".join('"%s"' % k for k in keywords) or "(no keywords)",
                                           " [organ %s]" % organ if organ else ""))
    n_reg = read_capability_registry(keywords) if keywords else 0
    n_res = read_results_archive(keywords) if keywords else 0
    n_notes = read_notes(keywords) if keywords else 0
    read_organ_map(organ)
    print("\n" + "=" * 88)
    print("SUMMARY: registry %d, results archive %d, NOTES %d%s"
          % (n_reg, n_res, n_notes, "" if organ else ", ORGAN_MAP READ **NOT PERFORMED**"))
    print("**A zero here is only meaningful because each read printed what it SCANNED.**")
    print("Now quote these counts in whatever you write -- 'I checked' is not a prior-work check.")
    print("=" * 88)
    return 0


def _self_test():
    """POSITIVE control: a term known to be present must come back non-zero from BOTH archives.
    A finder that cannot prove it finds things cannot support an absence claim."""
    import io
    from contextlib import redirect_stdout
    fails = []
    buf = io.StringIO()
    with redirect_stdout(buf):
        n = read_capability_registry(["definitional"])
    if not n:
        fails.append("registry read returned 0 for a known-present term ('definitional')")
    if "scanned" not in buf.getvalue():
        fails.append("registry read did not print what it scanned -- a bare zero would be unreadable")
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        r = read_organ_map(None)
    if r is not None or "NOT PERFORMED" not in buf2.getvalue():
        fails.append("omitting --organ must say the read was NOT PERFORMED, not pass silently")
    if fails:
        print("SELF-TEST FAILED:")
        for f in fails:
            print("   -", f)
        return 1
    print("self-test PASS: the registry read finds a known-present term and prints its scan count, "
          "and a missing --organ is reported as NOT PERFORMED rather than passing silently")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    raise SystemExit(main(sys.argv[1:]))
