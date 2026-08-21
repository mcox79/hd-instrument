"""Find a quoted number in `data/**/metrics.json` -- **and print its n and its CI beside it.**

**WHY THIS EXISTS.** On 2026-08-21 I revised the same board question three turns running, and all
three revisions had one cause: **I stated a number I had read in PROSE without going to the file it
came from.**

1. Recommended one organ over another **before reading the alternative's entry.**
2. Quoted five figures from `ORGAN_MAP` prose **without disk-verifying them** (they were correct).
3. Quoted a margin as *"beats both baselines"* **without computing its confidence interval** -- it
   rests on **n=57** and the whole lead over the strong floor is **nine items**, CI `[-0.016, +0.332]`.

**The third is the one this tool targets, because it is the one that survived my own checking.** The
number was real, same-run and same-metric; what was missing was **n** and **the absence of any CI in
the file** -- and neither is visible from the prose that quotes the number.

**SO THE TOOL DOES NOT JUST FIND THE NUMBER. IT REPORTS WHAT IS AROUND IT**: every `n_*` field in the
same block, every CI-ish field in the same block, and a loud line if the file carries **no CI at
all**. *"Where does this number live" was never the hard part. "How many items is it, and does
anything bound it" was.*

    python tools/verify_number_on_disk.py 0.7193
    python tools/verify_number_on_disk.py 0.7193 --cell exp_wire_coref_accumulate_situation_model_v1

**A number that cannot be found is reported as NOT FOUND with a non-zero exit** -- never as silence.
*Any tool relied on to establish absence needs a known-present positive control, which `--self-test`
supplies.*
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
N_PAT = re.compile(r"(^|_)n(_|$)|^n_|count$|_items$|_queries", re.I)
CI_PAT = re.compile(r"ci_|_ci$|conf_int|lower|upper|p_value|pvalue|half_width|stderr|std_err", re.I)


def _walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = "%s.%s" % (path, k) if path else str(k)
            yield from _walk(v, p)
            if not isinstance(v, (dict, list)):
                yield p, str(k), v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, "%s[%d]" % (path, i))


def verify(value, cell=None, tol=None, quiet=False):
    tol = tol if tol is not None else max(5e-5, abs(value) * 1e-4)
    pattern = os.path.join(_REPO, "data", cell or "*", "metrics.json")
    files = sorted(glob.glob(pattern))
    hits = []
    for f in files:
        try:
            m = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        rows = list(_walk(m))
        found = [(p, v) for p, k, v in rows
                 if isinstance(v, (int, float)) and not isinstance(v, bool)
                 and abs(float(v) - value) <= tol]
        if found:
            hits.append((f, found, rows))
    if not hits:
        if not quiet:
            print("NOT FOUND: %r does not appear in %s (tolerance %g).\n"
                  "That is NOT evidence the number is wrong -- it may live in a note, a log, or a "
                  "cell outside data/. It IS evidence you cannot cite it as measured until you find "
                  "the file." % (value, pattern, tol))
        return 1

    for f, found, rows in hits:
        cellname = os.path.basename(os.path.dirname(f))
        print("=" * 86)
        print("%s  --  %d match(es) for %r" % (cellname, len(found), value))
        print("=" * 86)
        for p, v in found[:12]:
            print("  %-70s = %s" % (p[:70], v))
        block = os.path.dirname(found[0][0].replace("[", ".").replace("]", ""))
        prefix = found[0][0].rsplit(".", 1)[0]
        # Rank n-like fields by how much of the MATCH's path they share, so the n that actually
        # governs the number comes first. The first version just truncated at 12 and the field that
        # mattered (n_queries_identity_demanding, n=57) fell off the end -- caught by the self-test,
        # which asserts that specific field is surfaced rather than that "some n" was printed.
        def _shared(a, b):
            pa, pb = a.split("."), b.split(".")
            i = 0
            while i < min(len(pa), len(pb)) and pa[i] == pb[i]:
                i += 1
            return i

        # AND MATCH THE METRIC NAME, NOT JUST THE PATH. This file carries BOTH
        # `...per_arm.strict_cb.n_total = 349` (the overall denominator) and
        # `eval_blocks.powered.n_queries_identity_demanding = 57` (the subset the quoted number
        # actually belongs to). Path proximity alone ranks the 349 first -- **surfacing the WRONG n,
        # which is the same way the prose misled me.** So a field whose key shares distinctive tokens
        # with the matched metric key outranks one that is merely nearby.
        metric_key = found[0][0].rsplit(".", 1)[-1]
        mtok = {t for t in re.split(r"[._]", metric_key.lower()) if len(t) > 3}

        def _rank(t):
            # a top-level key has no "." -- rsplit would IndexError. Guard it.
            leaf = t[0].rsplit(".", 1)[-1].lower()
            ktok = {x for x in re.split(r"[._]", leaf) if len(x) > 3}
            return (-len(mtok & ktok), -_shared(t[0], prefix))

        ns = sorted([(p, v) for p, k, v in rows
                     if N_PAT.search(k) and isinstance(v, (int, float))
                     and not isinstance(v, bool)], key=_rank)
        cis = [(p, v) for p, k, v in rows if CI_PAT.search(k)]
        print("\n  -- n-LIKE FIELDS IN THIS FILE (the question the prose never answers) --")
        for p, v in ns[:12] or [("(none found)", "")]:
            print("     %-66s %s" % (p[:66], v))
        print("\n  -- CI / ERROR-BOUND FIELDS --")
        if cis:
            for p, v in cis[:12]:
                print("     %-66s %s" % (p[:66], v))
        else:
            print("     *** NONE. THE FILE CARRIES NO CONFIDENCE INTERVAL ANYWHERE. ***")
            print("     A point estimate with no bound is not a margin. Compute one before quoting")
            print("     it as a win -- an unpaired 2-proportion test is the conservative floor.")
        print("\n  block of the first match: %s" % (block or "(top level)"))
    return 0


def _self_test():
    """POSITIVE and NEGATIVE controls. A finder that cannot prove it finds things cannot support a
    NOT FOUND, which is the silent-zero defect `experiment_index.py` and `director_kb_query.py`
    both shipped."""
    fails = []
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = verify(0.7192982456140351,
                    cell="exp_wire_coref_accumulate_situation_model_v1")
    out = buf.getvalue()
    if rc != 0:
        fails.append("known-present value 0.7193 was NOT found (positive control)")
    if "n_queries_identity_demanding" not in out:
        fails.append("the n field that mattered (n_queries_identity_demanding) was not surfaced")
    if "NO CONFIDENCE INTERVAL" not in out:
        fails.append("the file genuinely has no CI, and the tool did not say so loudly")
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        rc2 = verify(-123456.789, quiet=True)
    if rc2 == 0:
        fails.append("an absent value returned success (negative control)")
    if fails:
        print("SELF-TEST FAILED:")
        for f in fails:
            print("   -", f)
        return 1
    print("self-test PASS: finds a known-present figure, surfaces the n field that mattered, says "
          "loudly that the file carries no CI, and reports a truly absent value as NOT FOUND")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        raise SystemExit(2)
    cell = None
    if "--cell" in sys.argv:
        cell = sys.argv[sys.argv.index("--cell") + 1]
    raise SystemExit(verify(float(args[0]), cell=cell))
