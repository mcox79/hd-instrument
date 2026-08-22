#!/usr/bin/env python
"""Paste a number you are about to quote. Get back the caveats that sit beside it.

WHY THIS EXISTS. On 2026-08-21 I quoted a number past its own source's stated limits THREE TIMES in
one night, and each time the limit was written down, close by, in the artifact I was reading:

  1. `0.2449` and the shuffled null band -- taken from a cell whose `scope_disclaimer` reads *"The
     item population is the SimLex+WordSim word list... These are NOT instrument numbers and may not
     be quoted as such."* I quoted them as instrument numbers.
  2. `0.4750` -- quoted as evidence that context helps identification. Its own note says, two
     paragraphs down, *"0.4750 is inflated by self-reference"*. A third arm later showed the word
     ALONE beats it.
  3. `3.5x` for technical writing grounding better -- real, but MEANINGFUL-OR-RELATED COMBINED, n=17,
     one scorer, and the source note's limits read *"MEANINGFUL counts are 1 and 2, and both CIs
     touch zero."*

**THE COMMON SHAPE: THE NUMBER TRAVELLED AND ITS CAVEAT DID NOT.** Headlines are memorable and
limits sections are not, so a number lifted from a headline arrives stripped of the thing that
constrains it.

WHAT THIS DOES. Finds every note and every cell metrics file containing the literal you pass, then
prints, for each hit, the caveat-bearing lines NEAREST that number -- plus any `scope_disclaimer` or
`limits` field verbatim. It does not judge; it shows you what the source said next to what you are
about to repeat.

    python tools/cite_check.py 0.4750
    python tools/cite_check.py "3.5x" --window 40
    python tools/cite_check.py --self-test

NOT A SEARCH TOOL. `experiment_index.py` answers "has this been done"; this answers "what did the
place I got this number from say about it". Absence of caveats is reported as NOT evidence there are
none.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caveat vocabulary, taken from the three real misses plus the repo's standing measurement bar.
CAVEAT = re.compile(
    r"scope_disclaimer|may not be quoted|NOT instrument numbers|do not quote|DO NOT READ|"
    r"inflated|crosses zero|spans zero|touch(es)? zero|not distinguishable|NOT SEPARATED|"
    r"underpowered|single scorer|one scorer|no second witness|LIMIT|CAVEAT|"
    r"WITHDRAWN|SUPERSEDED|CORRECTED|artifact|confound|"
    r"\bn ?= ?\d{1,3}\b|not the average|NOT a claim|I am NOT claiming|what this is not",
    re.I)


def _hits(literal: str) -> list[str]:
    """Files containing the literal, in PURE PYTHON.

    NOT `rg`: it is not on PATH for a subprocess in this environment (the editor provides it to the
    shell, `which rg` finds nothing), so shelling out returned ZERO FILES SILENTLY -- which read as
    "no caveats exist" rather than "the search never ran". My negative control passed vacuously
    through it, because a broken search and a genuinely absent literal look identical. Hence the
    SEARCH POSITIVE CONTROL in the self-test below.

    SCOPE IS BOUNDED ON PURPOSE. `notes/*.md` plus `data/*/metrics.json` only. The first draft
    scanned all of `data/`, which CLAUDE.md records as ~26 GB; one metrics file per cell is the part
    that carries `scope_disclaimer`.
    """
    lit = literal.encode("utf-8")
    out = []
    for path in glob.glob(os.path.join(REPO, "notes", "*.md")):
        try:
            with open(path, "rb") as fh:
                if lit in fh.read():
                    out.append(os.path.relpath(path, REPO).replace("\\", "/"))
        except OSError:
            continue
    for path in glob.glob(os.path.join(REPO, "data", "*", "metrics.json")):
        try:
            with open(path, "rb") as fh:
                if lit in fh.read():
                    out.append(os.path.relpath(path, REPO).replace("\\", "/"))
        except OSError:
            continue
    return out


# Files this tool could not open. A caveat tool that silently skips a file reports "no caveats"
# about a file it never read. That is the shape of the 2026-08-22 substrate incident: a helper
# swallowed an AttributeError, returned a DIFFERENT quantity, and produced a table that agreed with
# itself. Silence must be distinguishable from breakage, so unreadable files are COUNTED and
# REPORTED rather than skipped.
UNREADABLE: list = []


def _note_caveats(path: str, literal: str, window: int) -> list[tuple]:
    try:
        lines = open(os.path.join(REPO, path), encoding="utf-8", errors="replace").read().splitlines()
    except OSError as e:
        UNREADABLE.append((path, "%s: %s" % (type(e).__name__, e)))
        return []
    idx = [i for i, ln in enumerate(lines) if literal in ln]
    out, seen = [], set()
    for i in idx:
        for j in range(max(0, i - window), min(len(lines), i + window + 1)):
            ln = lines[j].strip()
            if j not in seen and ln and CAVEAT.search(ln):
                seen.add(j)
                out.append((j + 1, ln[:300]))
    return out


def _metrics_scope(path: str) -> list[tuple]:
    """`scope_disclaimer` / `limits` fields anywhere in a metrics file, verbatim."""
    try:
        d = json.load(open(os.path.join(REPO, path), encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        UNREADABLE.append((path, "%s: %s" % (type(e).__name__, e)))
        return []
    found = []

    def walk(o, pre=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if re.fullmatch(r"scope_disclaimer|limits?|caveats?|disclaimer", k, re.I):
                    found.append((pre + "." + k, str(v)[:600]))
                walk(v, pre + "." + k)
        elif isinstance(o, list):
            for x in o[:20]:
                walk(x, pre)
    walk(d)
    return found


def _printable(s: str) -> str:
    """Make a source line safe for THIS stdout, which on Windows is cp1252, not utf-8.

    Measured 2026-08-22: this tool died with `UnicodeEncodeError` on a caveat line containing an
    emoji -- AFTER printing one caveat and BEFORE printing the rest. **A tool whose job is to show
    you what you are about to quote past, failing halfway with a traceback, hands you a PARTIAL
    caveat list.** Silently dropping the rest is the exact shape of the failures this tool exists to
    catch.

    Not fixed by reconfiguring stdout: that mutates global state for every importer, which this repo
    already has a documented incident about (`hdlab.reading_grounding_loop` rewriting `sys.stdout`
    process-wide). Sanitising the STRING keeps the blast radius at one line.
    """
    enc = (getattr(sys.stdout, "encoding", None) or "utf-8")
    try:
        s.encode(enc)
        return s
    except (UnicodeEncodeError, LookupError):
        return s.encode(enc, errors="replace").decode(enc, errors="replace")


def report(literal: str, window: int = 25) -> int:
    files = _hits(literal)
    bar = "=" * 88
    print(bar)
    print(f"WHAT THE SOURCES SAY BESIDE {literal!r} -- READ BEFORE QUOTING IT")
    print(bar)
    if not files:
        print(f"\nNo file under notes/ or data/ contains the literal {literal!r}.")
        print("If you are about to quote it anyway, you do not have a source for it.")
        return 0
    n_cav = 0
    for f in sorted(files)[:25]:
        if f.endswith(".json"):
            sc = _metrics_scope(f)
            if sc:
                n_cav += 1
                print(f"\n*** {f} -- SCOPE FIELDS ***")
                for k, v in sc[:4]:
                    print(f"    {k}: {v}")
        else:
            cav = _note_caveats(f, literal, window)
            if cav:
                n_cav += 1
                print(f"\n*** {f} -- {len(cav)} CAVEAT LINE(S) NEAR THE NUMBER ***")
                for lineno, ln in cav[:8]:
                    print(f"    L{lineno}: {_printable(ln)}")
    print(f"\n{len(files)} file(s) contain it; {n_cav} carry caveats near it.")
    if UNREADABLE:
        print(f"!! {len(UNREADABLE)} file(s) COULD NOT BE READ -- their caveats are NOT in that count")
        for pth, err in UNREADABLE[:6]:
            print(f"     {pth}: {err}")
        print("   Silence from an unreadable file is not absence of caveats.")
    if not n_cav:
        print("NO CAVEATS FOUND IS NOT EVIDENCE THERE ARE NONE -- it means none matched this")
        print("tool's vocabulary within the window. Widen with --window, and read the source.")
    return 1 if n_cav else 0


def _self_test() -> int:
    ok = True

    # POSITIVE CONTROLS: the two real misses from 2026-08-21, not fixtures.
    for lit, want, label in (
        ("0.4750", r"self-reference|inflated",
         "the two-jobs note's 'inflated by self-reference' caveat"),
        ("0.2449", r"scope|not.*instrument|population|word list",
         "the power-extension cell's scope disclaimer"),
    ):
        files = _hits(lit)
        blob = ""
        for f in files[:25]:
            if f.endswith(".json"):
                blob += " ".join(v for _k, v in _metrics_scope(f))
            else:
                blob += " ".join(ln for _i, ln in _note_caveats(f, lit, 25))
        if re.search(want, blob, re.I):
            print(f"[self-test] PASS: {lit} surfaces {label}")
        else:
            print(f"[self-test] FAIL: {lit} did NOT surface {label} "
                  f"({len(files)} file(s), {len(blob)} chars of caveat)")
            ok = False

    # SEARCH POSITIVE CONTROL, AND IT IS NOT OPTIONAL. Without it the negative control below
    # passes whenever the search is BROKEN, which is exactly what happened on the first run: the
    # rg subprocess could not start, every query returned zero files, and "an invented literal
    # matched nothing" reported PASS. A control that cannot tell absence from breakage is not one.
    probe = _hits("0.1549")
    if probe:
        print(f"[self-test] PASS: the search itself works ({len(probe)} file(s) for a known literal)")
    else:
        print("[self-test] FAIL: the SEARCH is broken -- every result below is meaningless")
        ok = False

    # ENCODING REGRESSION. Measured 2026-08-22: this tool died with UnicodeEncodeError on a caveat
    # line containing an emoji, AFTER printing one caveat and BEFORE the rest -- handing back a
    # PARTIAL caveat list plus a traceback. A caveat tool that stops halfway is worse than one that
    # refuses, because the output still looks like an answer.
    _emoji_line = "L1: \U0001F53B WITHDRAWN -- the caveat that used to crash this printer"
    try:
        out = _printable(_emoji_line)
        out.encode(getattr(sys.stdout, "encoding", None) or "utf-8")
        print("[self-test] PASS: a caveat line with non-cp1252 characters is printable")
    except UnicodeEncodeError:
        print("[self-test] FAIL: _printable did not make the line safe for this stdout")
        ok = False
    if _printable("plain ascii caveat") != "plain ascii caveat":
        print("[self-test] FAIL: _printable altered an ASCII line -- it must be a no-op there")
        ok = False

    # NEGATIVE CONTROL: a literal nobody has written must report nothing, loudly.
    if not _hits("0.9182734655zzz"):
        print("[self-test] PASS: an unsourced literal returns no files (no cry-wolf)")
    else:
        print("[self-test] FAIL: an invented literal matched something")
        ok = False

    print("[self-test] " + ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return _self_test()
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    win = 25
    if "--window" in argv:
        try:
            win = int(argv[argv.index("--window") + 1])
        except (IndexError, ValueError):
            pass
    return report(args[0], win)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
