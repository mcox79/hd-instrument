"""Turn the floor audit's FLAGS into per-cell VERDICTS -- and refuse to do so where it cannot.

WHY THIS EXISTS. `tools/strongest_floor_audit.py` prints, in its own output, "A READ LIST, NOT A
VERDICT". That caution was then carried into a standing operator decision (OP1) as though the flag
count WERE a count of overstated results: *"238 results whose claim does not survive the standard"*.
Owner ruling 2026-08-22: *"re adjudicate them I think - you can do it fast, and then put this behind
us."*

WHAT THE RE-ADJUDICATION FOUND, and it inverts the premise. The audit locates the largest
floor-shaped number and the largest treatment-shaped number ANYWHERE in a nested metrics.json and
compares them. It does not check that the two are commensurable. Measured on all 286 flags:
**207 (72.4%) pair numbers that this project's own rule forbids comparing** -- a different
per_seed/per_condition index, a different top-level metric block, or a max_ statistic against a
mean_ one. One flagged row compares a REJECT RATE against an ACCURACY. Another compares condition
5's floor to condition 0's treatment.

So the honest disposition has FOUR outcomes, not two:

  INADMISSIBLE_COMPARISON  the two numbers are not commensurable. NOT evidence of an overstatement
                           and NOT evidence against one -- the flag simply does not bear on it.
  SELF_DECLARED_FAILURE    the cell already calls itself a failure. Nothing to withdraw.
  UPHELD                   the treatment beats the STRONGEST floor. The write-up quoted a WEAKER
                           floor, which is a bookkeeping defect, not an overstatement.
  NOT_SUPPORTED            the cell's own strongest floor BEATS its own best treatment, on a
                           comparison that is actually valid. THIS is the real read list.

IT STILL DOES NOT READ THE SCIENCE. A NOT_SUPPORTED row is a CANDIDATE that needs a human read --
especially near the bottom of the margin list, where one item flips the answer. This tool bounds
the problem; it does not close it.

Usage:
    python tools/adjudicate_floor_flags.py              # counts + the NOT_SUPPORTED list
    python tools/adjudicate_floor_flags.py --self-test
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DATA = os.path.join(REPO_ROOT, "data")

INADMISSIBLE = "INADMISSIBLE_COMPARISON"
SELF_FAIL = "SELF_DECLARED_FAILURE"
UPHELD = "UPHELD"
NOT_SUPPORTED = "NOT_SUPPORTED"


def _key(x):
    return x.get("key", "") if isinstance(x, dict) else ""


def _val(x):
    return x.get("value") if isinstance(x, dict) else None


def _indices(path):
    return re.findall(r"\[(\d+)\]", path or "")


def _block(path):
    return (path or "").split(".")[0].split("[")[0]


def why_inadmissible(floor_key, treat_key):
    """Return the reasons these two numbers may not be compared. Empty list == comparable."""
    reasons = []
    fi, ti = _indices(floor_key), _indices(treat_key)
    if (fi or ti) and fi != ti:
        reasons.append("different per_seed/per_condition index")
    if _block(floor_key) != _block(treat_key):
        reasons.append("different top-level metric block")
    if ("max_" in (floor_key or "")) != ("max_" in (treat_key or "")):
        reasons.append("max_ statistic compared against a non-max_ one")
    return reasons


def adjudicate(hit):
    """One flagged cell -> {disposition, margin, reasons}. Pure; no I/O."""
    fk, tk = _key(hit.get("best_floor")), _key(hit.get("best_treatment"))
    fv, tv = _val(hit.get("best_floor")), _val(hit.get("best_treatment"))
    reasons = why_inadmissible(fk, tk)
    if reasons:
        return {"disposition": INADMISSIBLE, "margin": None, "reasons": reasons}
    if "FAIL" in (hit.get("verdict") or "").upper():
        return {"disposition": SELF_FAIL, "margin": None, "reasons": ["cell declares itself failed"]}
    if fv is None or tv is None:
        return {"disposition": INADMISSIBLE, "margin": None,
                "reasons": ["a side has no numeric value"]}
    margin = fv - tv                      # >0 means the FLOOR beat the treatment
    return {"disposition": (NOT_SUPPORTED if margin > 0 else UPHELD),
            "margin": margin, "reasons": []}


def run():
    from tools.strongest_floor_audit import scan            # IMPORT, never reimplement
    hits, n_files = [], 0
    for name in sorted(os.listdir(DATA)):
        p = os.path.join(DATA, name, "metrics.json")
        if not os.path.isfile(p):
            continue
        n_files += 1
        r = scan(p)
        if r:
            hits.append(r)
    rows = [(h, adjudicate(h)) for h in hits]
    # ROWS SCANNED BEFORE RESULTS -- silence must never read as absence.
    print(f"[adjudicate] scanned {n_files} metrics.json; {len(hits)} flagged by the floor audit")
    counts = {}
    for _, a in rows:
        counts[a["disposition"]] = counts.get(a["disposition"], 0) + 1
    n = max(1, len(rows))
    for k in (INADMISSIBLE, SELF_FAIL, UPHELD, NOT_SUPPORTED):
        c = counts.get(k, 0)
        print(f"    {k:24s} {c:4d}  ({100 * c / n:.1f}%)")
    why = {}
    for _, a in rows:
        for r in a["reasons"]:
            why[r] = why.get(r, 0) + 1
    if why:
        print("\n  why the inadmissible ones are inadmissible (a cell can have more than one):")
        for r, c in sorted(why.items(), key=lambda kv: -kv[1]):
            print(f"    {c:4d}  {r}")
    ns = sorted([(h, a) for h, a in rows if a["disposition"] == NOT_SUPPORTED],
                key=lambda t: -t[1]["margin"])
    print(f"\n  THE REAL READ LIST -- {len(ns)} cell(s) whose own floor beats their own treatment.")
    print("  A CANDIDATE, NOT A VERDICT: the small margins at the bottom need a human read.\n")
    for h, a in ns:
        print(f"    {a['margin']:+.4f}  {h['cell'][:62]:62s} [{(h.get('verdict') or '')[:26]}]")
    return 0


def self_test():
    ok = True

    def check(c, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if c else 'FAIL'} {label}",
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    def hit(fk, fv, tk, tv, verdict="HARD_PASS"):
        return {"cell": "demo", "verdict": verdict,
                "best_floor": {"key": fk, "value": fv},
                "best_treatment": {"key": tk, "value": tv}}

    # THE REAL SHAPES, taken from actual flagged rows on 2026-08-22.
    a = adjudicate(hit("per_condition[5].floors.no_coref.c_overwrite", 0.85,
                       "per_condition[0].ref_type.a_name_maintenance", 1.0))
    check(a["disposition"] == INADMISSIBLE and "index" in a["reasons"][0],
          "condition 5's floor vs condition 0's treatment -> INADMISSIBLE")

    b = adjudicate(hit("mean_acc_strong.RANDOMIZED_LOOKUP", 1.0,
                       "mean_reject_rate_gated_badsource", 1.0))
    check(b["disposition"] == INADMISSIBLE,
          "an accuracy compared against a REJECT RATE -> INADMISSIBLE")

    c = adjudicate(hit("stats.SHUFFLED.max_err_gap", 0.90, "stats.LOC.mean_err_gap", 0.05))
    check(c["disposition"] == INADMISSIBLE and any("max_" in r for r in c["reasons"]),
          "a max_ statistic vs a mean_ one -> INADMISSIBLE")

    # THE TWO THAT MUST STILL GET A VERDICT -- or this tool would excuse everything.
    d = adjudicate(hit("m.floor", 0.80, "m.treatment", 0.20))
    check(d["disposition"] == NOT_SUPPORTED and abs(d["margin"] - 0.60) < 1e-9,
          "POSITIVE CONTROL: a valid comparison the floor WINS -> NOT_SUPPORTED, margin +0.60")

    e = adjudicate(hit("m.floor", 0.20, "m.treatment", 0.80))
    check(e["disposition"] == UPHELD,
          "POSITIVE CONTROL: a valid comparison the treatment wins -> UPHELD")

    f = adjudicate(hit("m.floor", 0.80, "m.treatment", 0.20, verdict="HARD_FAIL_X"))
    check(f["disposition"] == SELF_FAIL,
          "a cell that already declares itself failed is not re-litigated")

    # NEGATIVE CONTROL: same block, same index, no max_ -> nothing to complain about.
    check(why_inadmissible("per_seed[0].a.floor", "per_seed[0].a.treat") == [],
          "NEGATIVE CONTROL: a commensurable pair is NOT flagged inadmissible")

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test() if "--self-test" in sys.argv else run())
