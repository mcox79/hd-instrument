#!/usr/bin/env python
"""Before you cite a function, print the CORRECTIONS its own docstring already carries.

WHY THIS EXISTS. On 2026-08-21, three separate times in one night, I quoted a claim about this
codebase while the correction to that claim sat in the docstring of the very thing I was quoting:

  1. `_make_definitional_gate` -- I called the definitional wire unwired and quoted its 64% as
     evidence. Its docstring carries THREE numbered corrections dated 2026-08-20 saying it IS live,
     that what ships is the phrase and not the head, and that the 64% is under a STANDING
     PROHIBITION against exactly the comparison I made.
  2. ORGAN_MAP entry A1 (VWFA) -- I told the owner on the board that the gain from wiring the form
     organs was "genuinely untested". The entry's heading is `NO LONGER UNTESTED`.
  3. A power-extension cell -- I reported an "unexpected" finding its own `arms_clearing` field
     already recorded.

CLAUDE.md already documents a FOURTH instance predating tonight: `_make_definitional_gate`'s
docstring once asserted "it is NOT on the live reading path", which was faithfully quoting an
accounting method that structurally could not see a lazy import, and that module is now responsible
for 212 of 402 banked facts.

THE GAP THIS FILLS. `experiment_index.py` prints `!! CORRECTION ON THIS CELL` for cells. ORGAN_MAP
has `organ_map_cite.py`, which prints corrections BEFORE the entry. NOTHING did that for CODE, which
is where three of tonight's four instances lived.

WHY A LOOKUP AND NOT A LINTER. Measured before writing a line of it: 159 of 4,183 docstrings in
hdlab/ and tools/ carry a correction marker -- 3.8%. That is low enough to be a signal, where an
earlier proposal on this repo was abandoned at a 48.5% base rate because a flag firing on half the
archive is not a flag. But 159 broadcast warnings would still be noise, so this is TARGETED: you ask
about the symbol you are about to rely on, exactly like organ_map_cite.py.

    python tools/symbol_corrections.py _make_definitional_gate
    python tools/symbol_corrections.py canonicalize_fast --full
    python tools/symbol_corrections.py --self-test

EXIT CODE IS 1 WHEN CORRECTIONS EXIST, so it can gate a script. Absence of a hit is NOT evidence the
symbol is uncorrected -- it means no marker matched THIS pattern list, and it says so.
"""
from __future__ import annotations

import ast
import glob
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Deliberately narrow. Every phrase here was taken from a docstring that ACTUALLY corrected
# something in this repo, not invented -- the same rule that took an earlier detector from 3,990
# false positives down to 53.
MARKERS = re.compile(
    r"CORRECTED|CORRECTION|SUPERSEDED|NO LONGER TRUE|NO LONGER UNTESTED|WITHDRAWN|RETRACTED|"
    r"THIS IS WRONG|WAS WRONG|IS NOT TRUE|DO NOT RE-PROPOSE|DO NOT PROPOSE|STANDING PROHIBITION|"
    r"DEFAULT CHANGED|BUT ALL THREE|HAVE MOVED|"
    # THE REPO'S OWN CONVENTION FOR "this was measured, not assumed", and it carries the most
    # expensive note in the codebase: substrate.read's "MEASURED 2026-08-19: readable is sorted,
    # so every read() began at alice_in_wonderland ... 25 of 28 corpora were NEVER OPENED ...
    # looked exactly like a learning ceiling." None of the phrases above match that line.
    # WIDENING MEASURED BEFORE IT WAS ADDED, per the rule that killed an earlier detector at a
    # 48.5% base rate: this family alone hits 0.22% of symbols and takes the union from
    # 2.75% to 2.92%, comfortably under this tool's own 10% self-test ceiling.
    r"MEASURED \d{4}-\d{2}-\d{2}",
    re.I)

SEARCH_GLOBS = ("hdlab/**/*.py", "tools/*.py", "verification/*.py")


def _iter_symbols():
    """(file, symbol, lineno, docstring) for every documented symbol in the search scope."""
    seen = set()
    for pat in SEARCH_GLOBS:
        for f in sorted(glob.glob(os.path.join(REPO, pat), recursive=True)):
            if f in seen:
                continue
            seen.add(f)
            try:
                src = open(f, encoding="utf-8").read()
                tree = ast.parse(src)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            rel = os.path.relpath(f, REPO).replace("\\", "/")
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    doc = ast.get_docstring(node) or ""
                    end = getattr(node, "end_lineno", node.lineno) or node.lineno
                    yield rel, node.name, node.lineno, doc, end
                elif isinstance(node, ast.Module):
                    doc = ast.get_docstring(node) or ""
                    yield rel, "<module>", 1, doc, 0


def _inline_comment_corrections(path: str, lo: int, hi: int) -> list[str]:
    """Correction-bearing INLINE COMMENTS inside a symbol's line range.

    ADDED 2026-08-21, AFTER THIS TOOL MISSED THE MOST EXPENSIVE INSTANCE IN THE REPO.
    `substrate.read` carries no correction in its docstring. It carries one in a comment:
    *"readable is sorted, so every read() began at alice_in_wonderland ... 25 of 28 corpora --
    113,649 sentences -- were NEVER OPENED. That produced a grounding curve that plateaued at 180
    terms and looked exactly like a learning ceiling."* A docstring-only scan cannot see that, and
    it is exactly the class of note this tool exists to surface -- I hit the SAME bug in my own
    diagnostics two days later.
    """
    try:
        src = open(os.path.join(REPO, path), encoding="utf-8").read().splitlines()
    except OSError:
        return []
    out = []
    for ln in src[max(0, lo - 1):hi]:
        st = ln.strip()
        if st.startswith("#") and MARKERS.search(st):
            out.append(st.lstrip("# ").rstrip())
    return out


def corrections_for(symbol: str) -> list[tuple]:
    """(file, symbol, lineno, [correction lines], doc) for every symbol whose name matches.

    EXACT NAME MATCH FIRST. Substring is the fallback and it is genuinely noisy on short names --
    `read` matched `readout`, `read-out` and two unrelated atomize scripts before this was added.
    """
    want = symbol.strip().lower()
    exact, loose = [], []
    for rel, name, lineno, doc, end in _iter_symbols():
        hay = rel.lower() if name == "<module>" else name.lower()
        lines = [ln.strip() for ln in doc.splitlines() if MARKERS.search(ln)]
        lines += _inline_comment_corrections(rel, lineno, end)
        if not lines:
            continue
        rec = (rel, name, lineno, lines, doc)
        if hay == want or (name != "<module>" and name.lower() == want):
            exact.append(rec)
        elif want in hay:
            loose.append(rec)
    return exact if exact else loose


def report(symbol: str, full: bool = False) -> int:
    hits = corrections_for(symbol)
    bar = "=" * 88
    print(bar)
    print(f"CORRECTIONS CARRIED BY {symbol.upper()}'S OWN DOCSTRING -- READ BEFORE CITING IT")
    print(bar)
    if not hits:
        print(f"\nNo correction marker found for {symbol!r} in hdlab/, tools/ or verification/.")
        print("THAT IS NOT EVIDENCE THE SYMBOL IS UNCORRECTED. It means no phrase in this tool's")
        print("marker list appeared in its docstring. Corrections written in other words, or kept")
        print("outside the docstring, are invisible here -- read the source, and check")
        print("  python tools/organ_map_cite.py <ORGAN_ID>        (the brain-reference corrections)")
        print("  python tools/experiment_index.py query \"<kw>\"    (the results archive)")
        return 0
    for rel, name, lineno, lines, doc in hits:
        print(f"\n*** {rel}:{lineno}  {name}  -- {len(lines)} CORRECTION LINE(S) ***")
        for ln in lines:
            print(f"    {ln}")
        if full:
            print("\n    ---- FULL DOCSTRING ----")
            for ln in doc.splitlines():
                print(f"    {ln}")
    print(f"\n{len(hits)} symbol(s) carry corrections. Quoting one of these without reading the")
    print("lines above is the exact failure this tool was built for (three instances 2026-08-21).")
    return 1


def _self_test() -> int:
    ok = True

    # POSITIVE CONTROL, AND IT IS THE REAL INCIDENT, NOT A FIXTURE. This docstring's three numbered
    # corrections are what cost the most on 2026-08-21.
    hits = corrections_for("_make_definitional_gate")
    if hits and any("reading_grounding_loop" in h[0] for h in hits):
        n = sum(len(h[3]) for h in hits)
        print(f"[self-test] PASS: _make_definitional_gate's corrections are found ({n} line(s))")
    else:
        print(f"[self-test] FAIL: the incident docstring was NOT found (hits={len(hits)})")
        ok = False

    # ...and it must surface the SUBSTANCE, not merely match a word.
    body = " ".join(ln for h in hits for ln in h[3]).upper()
    if "MOVED" in body or "CORRECTION" in body:
        print("[self-test] PASS: and the surfaced lines carry the correction itself")
    else:
        print(f"[self-test] FAIL: matched but surfaced nothing substantive: {body[:160]!r}")
        ok = False

    # THE INLINE-COMMENT REGRESSION. This tool MISSED this case on its first version, twice: once
    # because it read docstrings only, and again because its markers did not cover the repo's
    # "MEASURED <date>" convention. It is the most expensive correction in the codebase -- a shelf
    # the reader could not reach, which looked exactly like a learning ceiling.
    rd = corrections_for("read")
    if any(h[0].endswith("substrate.py") for h in rd):
        print("[self-test] PASS: substrate.read's INLINE-COMMENT correction is found")
    else:
        print(f"[self-test] FAIL: substrate.read's inline correction still missed "
              f"(hits: {[h[0] for h in rd][:4]})")
        ok = False

    # NEGATIVE CONTROL. A guard that fires on everything gets ignored -- this repo abandoned a
    # ceiling detector at a 48.5% base rate for exactly that reason.
    absent = corrections_for("zzz_no_such_symbol_anywhere")
    if not absent:
        print("[self-test] PASS: an unknown symbol returns nothing (no cry-wolf)")
    else:
        print(f"[self-test] FAIL: unknown symbol returned {len(absent)} hit(s)")
        ok = False

    # THE BASE RATE IS PART OF THE CONTRACT. If a future edit widens MARKERS until most docstrings
    # match, this tool becomes the thing it was built not to be, and the test says so.
    tot = marked = 0
    for _rel, _name, _lineno, doc, _end in _iter_symbols():
        tot += 1
        if MARKERS.search(doc):
            marked += 1
    rate = marked / max(1, tot)
    if rate < 0.10:
        print(f"[self-test] PASS: base rate {marked}/{tot} = {rate:.1%} is under the 10% ceiling")
    else:
        print(f"[self-test] FAIL: base rate {marked}/{tot} = {rate:.1%} -- too broad to be a signal")
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
    return report(args[0], full="--full" in argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
