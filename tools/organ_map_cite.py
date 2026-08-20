"""Cite an organ from `ORGAN_MAP.md` **with every constraint attached** -- you cannot get just the row.

**WHY THIS IS A TOOL AND NOT A RULE.** The rule already exists, twice:

- After the divisive-normalisation incident: *"the prior-work check before proposing a BRAIN
  MECHANISM is THREE reads -- registry, `experiment_index.py`, AND `ORGAN_MAP`'s corrections; grep
  the whole file, not the row you cite."*
- In its own words: *"Quoting one section of a document is not reading it."*

**BOTH TIMES THE RULE WAS WRITTEN DOWN, AND BOTH TIMES I THEN VIOLATED IT ON THE SAME FILE.**
2026-08-20 I quoted §2 to justify divisive normalisation while §3 said *"do not re-propose"* it, with
an analytic impossibility proof. 2026-08-21 I quoted F5's `BRAIN'S MATH` row (line 989) all session
and never read line 1440 -- **"F5/F6 -- queue behind step 4"** -- in the same file, under a heading
whose stated purpose is *"recorded so it is not started by accident."*

**Every other recurring failure in this repo got moved out of prose and into a function**
(`rank_with_ties.py` for tie conventions, `replication_gate.py` for single-seed wins, the STATUS
size guard in the session hook). This is that move for organ citation: **there is no call signature
that returns the math row alone.**

    python tools/organ_map_cite.py F5
    python tools/organ_map_cite.py E3 --verbose

**IT PRINTS, ALWAYS:** the organ's own entry; every OTHER line in the file naming it (scheduling,
phase gates, step lists, corrections, retractions); and the file's standing prohibitions. If the
organ appears in a "do not" or "queue behind" or "not started" line, that is shown ABOVE the entry,
not below it.
"""
from __future__ import annotations

import os
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORGAN_MAP = os.path.join(_REPO, "notes", "ORGAN_MAP.md")

# A hit on any of these makes a line a CONSTRAINT rather than description. Deliberately broad: a
# false constraint costs one line of reading, a missed one costs a build.
CONSTRAINT = re.compile(
    r"do not re-propose|do not\b|never\b|queue behind|queue it as|not started|blocked behind|"
    r"strictly (?:before|after)|presupposes|declined|superseded|retract|corrected|stale|"
    r"phase b|does not count|not scheduled|by accident|before its|gated|must not",
    re.I)


def cite(organ, verbose=False):
    if not os.path.exists(ORGAN_MAP):
        print("ORGAN_MAP.md not found at %s" % ORGAN_MAP)
        return 2
    lines = open(ORGAN_MAP, encoding="utf-8").read().split("\n")
    pat = re.compile(r"(?<![A-Za-z0-9])%s(?![0-9])" % re.escape(organ))
    hits = [(i, ln) for i, ln in enumerate(lines) if pat.search(ln)]
    if not hits:
        print("%s: NO MENTION in ORGAN_MAP.md. That is not evidence the organ is unconstrained -- "
              "it is evidence the ID is wrong or the map does not cover it." % organ)
        return 1

    # the organ's own entry = from its bolded heading line to the next bolded heading
    head = next((i for i, ln in hits if ln.strip().startswith("**%s " % organ)
                 or ln.strip().startswith("**%s —" % organ)), None)
    entry = []
    if head is not None:
        j = head + 1
        while j < len(lines) and not re.match(r"^\*\*[A-Z]\d+ ", lines[j].strip()):
            entry.append(lines[j])
            j += 1

    constraints = [(i, ln) for i, ln in hits
                   if CONSTRAINT.search(ln) and (head is None or not (head <= i < head + len(entry) + 1))]
    others = [(i, ln) for i, ln in hits
              if (i, ln) not in constraints and (head is None or i != head)
              and (head is None or not (head <= i < head + len(entry) + 1))]

    def show(ln):
        return ln.strip().encode("ascii", "replace").decode("ascii")

    print("=" * 88)
    print("ORGAN_MAP CITATION FOR %s -- CONSTRAINTS FIRST, BY DESIGN" % organ)
    print("=" * 88)
    if constraints:
        print("\n*** %d CONSTRAINT LINE(S). READ THESE BEFORE THE ENTRY. ***" % len(constraints))
        for i, ln in constraints:
            print("  L%-5d %s" % (i + 1, show(ln)[:400]))
    else:
        print("\n(no scheduling / prohibition / correction line mentions %s -- but see the standing "
              "prohibitions below)" % organ)

    if head is not None:
        print("\n--- the organ's own entry (L%d) ---" % (head + 1))
        print("  %s" % show(lines[head])[:300])
        for ln in entry if verbose else entry[:12]:
            if ln.strip():
                print("  %s" % show(ln)[:300])
        if not verbose and len(entry) > 12:
            print("  ... %d more lines (--verbose)" % (len(entry) - 12))

    if others:
        print("\n--- %d other mention(s) ---" % len(others))
        for i, ln in (others if verbose else others[:10]):
            print("  L%-5d %s" % (i + 1, show(ln)[:300]))
        if not verbose and len(others) > 10:
            print("  ... %d more (--verbose)" % (len(others) - 10))

    print("\n--- file-wide standing prohibitions (apply regardless of organ) ---")
    for i, ln in enumerate(lines):
        if re.search(r"do not re-propose|is not started by accident|No organ enters Phase B", ln, re.I):
            print("  L%-5d %s" % (i + 1, show(ln)[:300]))
    print("\nREMINDER: this is ONE of the three reads. Also run "
          "`tools/experiment_index.py query \"<kw>\"` (has the question been ANSWERED) and check "
          "`data/capability_registry.jsonl` (does the tool already exist).")
    return 0


def _self_test():
    """The tool must SURFACE the constraint that was missed, or it is decoration."""
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        cite("F5")
    out = buf.getvalue()
    fails = []
    if "queue behind step 4" not in out:
        fails.append("F5 citation did not surface 'queue behind step 4' -- the exact line missed "
                     "on 2026-08-21, which is the whole reason this tool exists")
    if out.index("CONSTRAINT LINE") > out.index("ORGAN_MAP CITATION"):
        pass  # ordering is fine
    if "own entry" in out and out.index("CONSTRAINT LINE") > out.index("own entry"):
        fails.append("constraints printed AFTER the entry; they must come first")
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        rc = cite("ZZ99")
    if rc == 0 or "NO MENTION" not in buf2.getvalue():
        fails.append("an unknown organ id did not report NO MENTION / non-zero")
    if fails:
        print("SELF-TEST FAILED:")
        for f in fails:
            print("   -", f)
        return 1
    print("self-test PASS: F5's 'queue behind step 4' is surfaced, constraints print before the "
          "entry, and an unknown id reports NO MENTION rather than silence")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(cite(sys.argv[1].upper(), verbose="--verbose" in sys.argv))
