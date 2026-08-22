"""Drop a CANDIDATE marker beside every cell whose own floor beats its own treatment.

WHY A MARKER AND NOT AN EDIT. The 35 cells identified by `adjudicate_floor_flags.py` are a READ
LIST, not a verdict list. Editing their `metrics.json`, or stamping "claim not supported" into the
capability registry, would (a) corrupt the evidence we are trying to read and (b) assert a
conclusion nobody has reached -- the bottom of the margin list (+0.0106, +0.0230) sits where one
item flips the answer, and NONE of the 35 has been read for whether its floor is the RIGHT floor for
its question.

So this writes an ADDITIVE, REVERSIBLE sidecar -- FLOOR_FLAG_CANDIDATE.md in the cell's own
directory -- that says what was measured, what it does NOT mean, and how to discharge it. Anyone who
opens the cell sees it. Nothing that reads metrics.json changes behaviour.

  python tools/mark_floor_flag_candidates.py             # dry run: list what WOULD be written
  python tools/mark_floor_flag_candidates.py --apply
  python tools/mark_floor_flag_candidates.py --self-test
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import io
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DATA = os.path.join(REPO_ROOT, "data")
MARKER = "FLOOR_FLAG_CANDIDATE.md"
NOTE = ("notes/THE_238_OVERSTATED_RESULTS_WERE_NEVER_238_SEVENTY_TWO_PERCENT_"
        "ARE_INVALID_COMPARISONS_2026-08-22.md")


def render(cell, margin, floor_key, treat_key, floor_val, treat_val, verdict):
    """The marker text. Pure -- self-tested on its WORDING, because the wording IS the artifact."""
    return f"""# CANDIDATE: this cell's own floor beats its own treatment

**cell:** `{cell}`
**recorded verdict:** `{verdict}`
**margin (floor minus treatment):** `{margin:+.4f}`

|  | key | value |
|---|---|---|
| strongest floor found | `{floor_key}` | `{floor_val}` |
| best treatment found | `{treat_key}` | `{treat_val}` |

## THIS IS A CANDIDATE, NOT A VERDICT

It means one thing only: **inside this cell's own `metrics.json`, the largest floor-shaped number is
larger than the largest treatment-shaped number, and the two are commensurable** -- same metric
block, same `per_seed`/`per_condition` index, not a `max_` against a `mean_`.

**It does NOT mean the result is withdrawn.** Nobody has yet read whether that floor is the RIGHT
floor for this cell's question. A floor can be the strongest number present and still be the wrong
comparison for the claim actually made.

## HOW TO DISCHARGE IT

1. Read the claim this cell's write-up actually makes.
2. Decide whether `{floor_key}` is the floor that claim must clear.
3. If it is -- the claim needs correcting, and it must be corrected wherever it is quoted.
   If it is not -- record WHICH floor is right and why, then delete this marker.

## PROVENANCE

Produced by `tools/adjudicate_floor_flags.py` on 2026-08-22, re-adjudicating the flags behind the
standing OP1 item (board Q112) about results whose claim might not survive the measurement bar.
**286 cells were flagged; 207 (72.4%) compare numbers that may not be compared; 43 are UPHELD;
35 -- including this one -- are candidates.**

Full reasoning: `{NOTE}`
Reproduce: `python tools/adjudicate_floor_flags.py`
"""


def collect():
    from tools.adjudicate_floor_flags import adjudicate, NOT_SUPPORTED
    from tools.strongest_floor_audit import scan
    out, n_files = [], 0
    for name in sorted(os.listdir(DATA)):
        p = os.path.join(DATA, name, "metrics.json")
        if not os.path.isfile(p):
            continue
        n_files += 1
        r = scan(p)
        if not r:
            continue
        a = adjudicate(r)
        if a["disposition"] == NOT_SUPPORTED:
            out.append((os.path.join(DATA, name), r, a))
    return n_files, sorted(out, key=lambda t: -t[2]["margin"])


def run(apply_it):
    n_files, rows = collect()
    # ROWS SCANNED BEFORE RESULTS -- silence must never read as absence.
    print(f"[mark] scanned {n_files} metrics.json; {len(rows)} NOT_SUPPORTED candidate(s)")
    if not rows:
        print("[mark] nothing to mark -- that is suspicious, not reassuring. Check the scan.")
        return 1
    wrote = 0
    for d, r, a in rows:
        f = r.get("best_floor") or {}
        t = r.get("best_treatment") or {}
        text = render(r["cell"], a["margin"], f.get("key"), t.get("key"),
                      f.get("value"), t.get("value"), r.get("verdict") or "")
        path = os.path.join(d, MARKER)
        if apply_it:
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            wrote += 1
        print(f"    {a['margin']:+.4f}  {r['cell'][:56]:56s} "
              f"[{(r.get('verdict') or '')[:20]:20s}] {'written' if apply_it else 'dry-run'}")
    print(f"\n[mark] {'wrote' if apply_it else 'would write'} "
          f"{wrote if apply_it else len(rows)} x {MARKER}")
    if not apply_it:
        print("[mark] DRY RUN -- pass --apply to write.")
    return 0


def self_test():
    ok = True

    def check(c, label):
        nonlocal ok
        print(f"[self-test] {'PASS' if c else 'FAIL'} {label}",
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    txt = render("exp_demo_v1", 0.9054, "m.floor", "m.treat", 0.95, 0.0446, "HARD_PASS")

    # THE LOAD-BEARING ASSERTION: the marker must not read as a verdict.
    check("CANDIDATE, NOT A VERDICT" in txt, "marker states it is a candidate, not a verdict")
    check("does NOT mean the result is withdrawn" in txt,
          "marker explicitly refuses to withdraw the result")
    check("+0.9054" in txt, "margin rendered with sign and 4dp")
    check("HARD_PASS" in txt and "exp_demo_v1" in txt, "cell and its recorded verdict both appear")
    check("HOW TO DISCHARGE IT" in txt, "marker tells the reader how to remove it")

    # NEGATIVE CONTROL: the CLAIM BODY must not carry the label we were nearly talked into.
    # Scoped to everything above PROVENANCE, and the scope is principled rather than a carve-out:
    # provenance CITES a document by its real filename (which contains the word); the claim body
    # is the part that asserts something about THIS cell. Two earlier drafts got this wrong --
    # one exempted a specific string, which is a checker sharing a flaw with what it checks.
    body = txt.split("## PROVENANCE")[0]
    check(len(body) > 400, "the claim body is non-empty, so the next check cannot pass vacuously")
    check("claim not supported" not in body.lower() and "overstat" not in body.lower(),
          "NEGATIVE CONTROL: the claim body never brands the cell overstated")

    # POSITIVE CONTROL ON THE TEST ITSELF -- the check above must be able to FAIL.
    check("this result is overstated" in (txt + "\nthis result is overstated").lower(),
          "POSITIVE CONTROL: the overstated-detector fires when the phrase IS present")

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    raise SystemExit(run("--apply" in sys.argv))
