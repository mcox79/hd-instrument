"""What landed, how it turned out, and whether we could ever check it again.

OWNER, ANSWERING Q115 (2026-08-23): *"I think you should def make it a requirement for new
experiments, but I'd go back through the 275 older ones one at a time -- we need to know what those
are and how they turned out. You can decide whether each one wants a rerun 1 by 1."*

This is the inventory half. It enumerates every landed result, pairs it with the cell that produced
it, and reports three things per row: **the verdict**, **whether a re-run would genuinely recompute
or merely replay a checkpoint**, and **how load-bearing the result is**. That is what "know what
those are and how they turned out" needs before anyone decides which deserve a re-run.

THREE MEASUREMENT RULES THIS FILE OBEYS, EACH BECAUSE THE OPPOSITE WAS DONE HERE AND WAS WRONG:

  1. **A MENTION IS NOT A USE.** Coverage was once reported at 87 cells by searching for the helper's
     NAME; a strict check found 43. This matches the ASSIGNMENT (`OUTPUT_DIR = helper(...)`), so a
     helper named in a docstring, a comment, or an unrelated call does not count.
  2. **THE DIRECTORY NAME IS NOT THE CELL NAME.** 19 of 423 landed directories lack the `exp_`
     prefix their cell carries. Both spellings are tried, and the count of unmatched dirs is
     REPORTED rather than silently dropped -- a row we cannot pair is a gap in the inventory, not a
     zero.
  3. **PRINT THE RATE BESIDE THE TOTAL.** Every count here is shown as a share of a named
     denominator, because the recurring error in this repo is comparing two totals drawn from
     different-sized populations.

RUN:
    python tools/reproducibility_inventory.py                 # the summary
    python tools/reproducibility_inventory.py --list          # every replaying cell, worst first
    python tools/reproducibility_inventory.py --csv out.csv   # the full table for triage
    python tools/reproducibility_inventory.py --self-test
"""
import argparse
import ast
import csv
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# THE HELPERS THAT MAKE A RE-RUN GENUINE. Both spellings; `get_output_dir` is the older one.
HELPERS = ("fresh_run_output_dir", "get_output_dir")

# A cell that never names an output directory writes nowhere we track; it is not "replaying".
HAS_OUTPUT = re.compile(r"^\s*OUTPUT_DIR\s*=", re.M)


def routes_through_helper(src):
    """Does this cell actually CALL one of the helpers? Parsed, not pattern-matched.

    🔻 **THIS WAS A REGEX AND THE REGEX WAS WRONG, IN THE DIRECTION THAT INVENTS A CRISIS.** It
    required the module-level form `OUTPUT_DIR = get_output_dir(...)`, and reported that **2 of
    4,908** landed results could be re-run -- against a recorded 21%. The cells it missed use the
    far commoner shape:

        out_dir = get_output_dir(ANCHOR_NAME)        # a LOCAL, lowercase, inside a function

    Which variable receives the path is irrelevant to whether the redirect fires; only the CALL
    matters. Matching on an assignment target encoded an assumption about naming that most of the
    repo does not follow, and would have had me report a catastrophe to the owner.

    An AST walk fixes both halves at once: a call is a call wherever it appears and whatever it is
    assigned to, and a helper named in a comment or docstring is not a Call node at all -- so the
    mention-is-not-a-use rule is enforced by the parser instead of by me remembering it.

    Falls back to a call-shaped regex only when the file does not parse (a cell mid-edit), and such
    files are counted separately rather than silently treated as unrouted.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return bool(re.search(r"\b(?:%s)\s*\(" % "|".join(HELPERS), src)), True
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = getattr(f, "id", None) or getattr(f, "attr", None)
        if name in HELPERS:
            return True, False
    return False, False

VERDICT_KEYS = ("final_verdict", "verdict", "primary_verdict", "verdict_msg")

# Verdicts that assert something. A result nobody leans on is a cheaper re-run decision than one
# the plan quotes, so this drives the triage ordering rather than any notion of quality.
STRONG = ("HARD_PASS", "PASS", "HOLD", "CONFIRMED")


def _read(path):
    try:
        return io.open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def cell_for(dir_name, repo=REPO):
    """Find the cell that produced a landed directory. Tries both spellings -- see rule 2."""
    cands = ["experiments/%s.py" % dir_name, "experiments/exp_%s.py" % dir_name]
    if dir_name.startswith("exp_"):
        cands.append("experiments/%s.py" % dir_name[4:])
    for c in cands:
        if os.path.exists(os.path.join(repo, c)):
            return c
    return None


def verdict_of(metrics_path):
    """First verdict-shaped key that is present. Enumerated, not guessed.

    `status` used to be first in this list and matched 0 of 7,878 files; `primary_verdict` was
    absent from it and was the only verdict on 1. Both errors came from writing the list from
    memory instead of reading the files.
    """
    try:
        d = json.load(io.open(metrics_path, encoding="utf-8"))
    except Exception:
        return "UNREADABLE"
    if not isinstance(d, dict):
        return "UNREADABLE"
    for k in VERDICT_KEYS:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return "NO_VERDICT_FIELD"


def scan(repo=REPO):
    """One row per landed result. Never raises on a bad file -- it reports it as a row."""
    rows, unmatched = [], []
    for mp in sorted(glob.glob(os.path.join(repo, "data", "*", "metrics.json"))):
        d = os.path.basename(os.path.dirname(mp))
        cell = cell_for(d, repo)
        if cell is None:
            unmatched.append(d)
            continue
        src = _read(os.path.join(repo, cell))
        routed, unparsed = routes_through_helper(src)
        rows.append({
            "dir": d,
            "cell": cell,
            "verdict": verdict_of(mp),
            "reproducible": routed,
            "unparsed": unparsed,
            "has_output_dir": bool(HAS_OUTPUT.search(src)),
            "bytes": os.path.getsize(mp),
        })
    return rows, unmatched


def summarise(rows, unmatched):
    n = len(rows)
    if not n:
        return {"n": 0}
    repro = [r for r in rows if r["reproducible"]]
    replay = [r for r in rows if not r["reproducible"]]
    strong_replay = [r for r in replay if any(s in r["verdict"].upper() for s in STRONG)]
    return {
        "n": n,
        "unmatched": len(unmatched),
        "reproducible": len(repro),
        "reproducible_pct": 100.0 * len(repro) / n,
        "replaying": len(replay),
        "replaying_pct": 100.0 * len(replay) / n,
        "strong_replaying": len(strong_replay),
        "strong_replaying_pct": 100.0 * len(strong_replay) / n,
    }


WRITES_RESULTS = re.compile(r"\bwrite_metrics\s*\(|metrics\.json", re.I)


def check_new_cells(paths, repo=REPO):
    """THE Q115 REQUIREMENT: a NEW cell that writes results must route through the helper.

    OWNER, 2026-08-23: *"I think you should def make it a requirement for new experiments."*

    SCOPED DELIBERATELY NARROWLY, because the owner scoped it narrowly. This applies ONLY to files
    being ADDED, and only to ones that actually write a result. It says nothing about the 1,413
    existing cells that replay -- those are the inventory's job and the owner asked for them to be
    handled one at a time, not blocked en masse. A rule that fired on the backlog would be switched
    off within a day, and a rule that is switched off protects nothing.

    Returns a list of (path, reason) for cells that must be fixed. Empty means clear.
    """
    bad = []
    for p in paths:
        rel = p.replace("\\", "/")
        if not rel.startswith("experiments/") or not rel.endswith(".py"):
            continue
        if os.path.basename(rel).startswith("_"):
            continue                      # harness/support modules, not cells
        src = _read(os.path.join(repo, rel))
        if not src or not WRITES_RESULTS.search(src):
            continue                      # writes no result -- nothing to make reproducible
        routed, unparsed = routes_through_helper(src)
        if unparsed:
            bad.append((rel, "does not parse, so it cannot be checked"))
        elif not routed:
            bad.append((rel, "writes a result without calling %s" % " or ".join(HELPERS)))
    return bad


def _self_test():
    ok = True

    def chk(label, cond):
        nonlocal ok
        print("[self-test] %-62s %s" % (label, "PASS" if cond else "FAIL"))
        ok = ok and bool(cond)

    # RULE 1, BOTH WAYS -- and the LOCAL-VARIABLE arm is the one the regex got wrong.
    def R(s):
        return routes_through_helper(s)[0]

    chk("a module-level OUTPUT_DIR assignment COUNTS",
        R("OUTPUT_DIR = fresh_run_output_dir(os.path.join(R, C))"))
    chk("A LOCAL lowercase out_dir INSIDE A FUNCTION COUNTS (the regex missed these)",
        R("def main():\n    out_dir = get_output_dir(ANCHOR_NAME)\n    return out_dir"))
    chk("...and so does a call whose result is not assigned at all",
        R("def main():\n    write(get_output_dir(CELL))"))
    chk("a helper named in a COMMENT does not count",
        not R("# use fresh_run_output_dir here one day\nOUTPUT_DIR = 'data/x'"))
    chk("a helper named in a DOCSTRING does not count",
        not R('"""call get_output_dir() first."""\nOUTPUT_DIR = "data/x"'))
    chk("a helper named as a bare NAME but never called does not count",
        not R("fn = get_output_dir\nOUTPUT_DIR = 'data/x'"))
    chk("a bare assignment does not count",
        not R("OUTPUT_DIR = os.path.join(REPO, 'data', CELL)"))
    chk("an unparseable file is FLAGGED rather than silently counted as unrouted",
        routes_through_helper("def broken(:\n  out = get_output_dir(X)")[1])

    # RULE 2, BOTH WAYS.
    chk("a dir whose cell carries the exp_ prefix resolves",
        cell_for("stated_entity_fate_reading_extractor_v2_highprecision") is not None
        or cell_for("exp_stated_entity_fate_reading_extractor_v2_highprecision") is not None)
    chk("an invented dir resolves to nothing", cell_for("zzq_not_a_real_cell_9182") is None)

    # verdict_of, both ways
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "m.json")
        io.open(p, "w", encoding="utf-8").write(json.dumps({"primary_verdict": "HARD_PASS"}))
        chk("primary_verdict is found (it was missing from the list once)",
            verdict_of(p) == "HARD_PASS")
        io.open(p, "w", encoding="utf-8").write(json.dumps({"unrelated": 1}))
        chk("a file with no verdict SAYS so rather than reading as a pass",
            verdict_of(p) == "NO_VERDICT_FIELD")
        io.open(p, "w", encoding="utf-8").write("{not json")
        chk("an unreadable file is reported, not skipped", verdict_of(p) == "UNREADABLE")

    # THE Q115 GATE, BOTH WAYS. A gate never seen to fire is not a gate.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "experiments"))

        def write(name, body):
            io.open(os.path.join(td, "experiments", name), "w", encoding="utf-8").write(body)
            return "experiments/" + name

        good = write("exp_ok_v1.py",
                     "from x import get_output_dir\n"
                     "def m():\n"
                     "    d = get_output_dir('a')\n"
                     "    open(d + '/metrics.json', 'w')\n")
        bad = write("exp_bad_v1.py",
                    "def m():\n"
                    "    open('data/x/metrics.json', 'w')\n")
        nores = write("exp_noresult_v1.py",
                      "def m():\n"
                      "    return 1\n")
        helper = write("_support.py",
                       "def m():\n"
                       "    open('data/x/metrics.json', 'w')\n")

        chk("Q115 gate ACCEPTS a new cell that routes through the helper",
            check_new_cells([good], repo=td) == [])
        chk("Q115 gate REFUSES a new cell that writes a result without it",
            len(check_new_cells([bad], repo=td)) == 1)
        chk("Q115 gate ignores a new cell that writes NO result",
            check_new_cells([nores], repo=td) == [])
        chk("Q115 gate ignores harness modules (leading underscore)",
            check_new_cells([helper], repo=td) == [])
        chk("Q115 gate ignores files outside experiments/",
            check_new_cells(["tools/whatever.py"], repo=td) == [])

    rows, unmatched = scan()
    s = summarise(rows, unmatched)
    chk("the real repo yields a non-empty inventory", s.get("n", 0) > 100)
    chk("shares sum to the whole", abs(s["reproducible_pct"] + s["replaying_pct"] - 100.0) < 1e-6)
    print("[self-test] RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true", help="every replaying cell, load-bearing first")
    ap.add_argument("--csv", help="write the full table for triage")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--check-new", nargs="*", metavar="PATH",
                    help="Q115 gate: refuse NEW cells that write a result without the helper")
    a = ap.parse_args(argv)
    if a.self_test:
        return _self_test()

    if a.check_new is not None:
        bad = check_new_cells(a.check_new)
        for rel, why in bad:
            print("[q115] %s -- %s" % (rel, why))
        if bad:
            print("")
            print("COMMIT REFUSED: %d new experiment(s) would not be re-runnable." % len(bad))
            print("  A re-run of these would REPLAY a saved answer, so 'I re-ran it and got the")
            print("  same thing' would prove nothing -- which is the whole point of the check.")
            print("  FIX: import and call the shared helper, e.g.")
            print("      from experiments._seed_checkpoint import get_output_dir")
            print("      out_dir = get_output_dir(ANCHOR_NAME)")
            print("  This is the owner's Q115 ruling (2026-08-23), and it applies to NEW cells only.")
            print("  Bypass with --no-verify if you must, and say so in the message.")
        return 1 if bad else 0

    rows, unmatched = scan()
    s = summarise(rows, unmatched)
    if not s["n"]:
        print("no landed results found -- that is a finding, not an empty report")
        return 1

    print("LANDED RESULTS: %d  (+%d directories whose cell could not be found, NOT counted below)"
          % (s["n"], s["unmatched"]))
    print("  can be genuinely re-run : %4d  (%.1f%% of %d)"
          % (s["reproducible"], s["reproducible_pct"], s["n"]))
    print("  would only replay       : %4d  (%.1f%% of %d)"
          % (s["replaying"], s["replaying_pct"], s["n"]))
    print("  ...and assert a result  : %4d  (%.1f%% of %d)  <-- TRIAGE THESE FIRST"
          % (s["strong_replaying"], s["strong_replaying_pct"], s["n"]))

    if a.list:
        replay = [r for r in rows if not r["reproducible"]]
        replay.sort(key=lambda r: (not any(x in r["verdict"].upper() for x in STRONG), r["dir"]))
        print()
        print("  %-58s %s" % ("CELL", "HOW IT TURNED OUT"))
        for r in replay:
            print("  %-58s %s" % (r["dir"][:58], r["verdict"][:70]))

    if a.csv:
        with io.open(a.csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print("\nwrote %s (%d rows)" % (a.csv, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
