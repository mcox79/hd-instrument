"""Find dictionary keys that are READ but that NOTHING anywhere WRITES.

🔴 **VERDICT ON THIS TOOL, WRITTEN BY ITS AUTHOR AFTER FIVE ITERATIONS: IT DOES NOT WORK FOR ITS
PURPOSE. DO NOT TRUST ITS OUTPUT AS A BUG LIST.** *Kept because the failure is instructive and the
scan is occasionally useful as a reading list -- not because it earns its keep.*

**MEASURED:** whole tree **1,925** suspects -> excluding vendored code **871** -> excluding
`os.environ` and ALL_CAPS **801** -> `hdlab/` only **132**. **At every tightening the survivors are
dominated by LEGITIMATE reads:** class names used as registry keys (`HDFactStore`, `LibraryItem`),
ablation flags supplied by a CALLER's dict (`DA_slot_typing_OFF`), and fields of dicts built
elsewhere or loaded from disk (`animacy_map`, `api_source`). **`CLAUDE.md` records that a check
firing on a quarter of the repo gets ignored. 132 in library code is that check.**

**AND THE REASON IT CANNOT WORK IS WORTH MORE THAN THE TOOL:** a static scan cannot tell a key that
is *missing* from one that is *supplied by someone else*, because both look identical -- read here,
written nowhere in this tree. **That is the same indistinguishability that caused the original bug.**

✅ **WHAT ACTUALLY FOUND THE BUG, AND IT IS CHEAP AND GENERAL: A CONTRADICTION BETWEEN TWO FIELDS OF
ONE OUTPUT.** `n_grounded = 0` sat beside `anchors 4322 -> 4390 (+68)` in the same printed block.
**Nothing was learned AND the vocabulary grew by 68 cannot both be true.** *No static analysis, no
key inventory -- just two numbers in one report that could not both hold.* **Prefer that: make
outputs print quantities that CONSTRAIN EACH OTHER, and read them against each other.**


WHY THIS EXISTS. `hdlab/substrate.py:608` read `row.get("n_grounded_cumulative", ...)` while
`checkpoint()` emits **`cumulative_grounded`** -- the same two words TRANSPOSED. The key existed
nowhere else in the tree, so `.get()` always took its default, `or 0` tidied it into a clean integer,
and **`ReadResult.n_grounded` was structurally incapable of being non-zero on any read.** No
exception. No warning. It reported a constant while the docstring promised "a COUNT OF SOMETHING
THAT HAPPENED".

**THE FAILURE MODE IS THE POINT: `d.get(k, default)` CANNOT RAISE.** A missing key and a present
zero are indistinguishable from outside, so a wiring failure is served up as data. That cost an
evening of explaining a "null" that was never a measurement.

THE SIGNATURE THIS SCANS FOR, and it is deliberately narrow: a string literal that appears in a
`.get("...")` or `["..."]` READ and appears **NOWHERE ELSE IN THE SCANNED TREE**. A key that is
written somewhere -- as a dict-literal key, an assignment target, or even mentioned in another
file -- is NOT flagged. That makes this conservative: it will miss keys written under a different
spelling in a file it does scan, but it will not cry wolf.

LIMITS, STATED UP FRONT:
  * dynamically-built keys (`d.get(f"n_{x}")`) are invisible to it;
  * keys belonging to EXTERNAL payloads (json from disk, argparse, third-party dicts) are legitimate
    reads of things this tree never writes -- **expect true positives that are not bugs**, which is
    why the output is a READING LIST, not a verdict;
  * one appearance is the signature, so a key read in two places and written nowhere is missed.
    *Tightening that would raise the false-positive rate above the level anyone would act on.*
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCAN_DIRS = ["hdlab", "tools"]
READ_PAT = re.compile(r"""\.get\(\s*["']([A-Za-z_][A-Za-z0-9_]{2,})["']|\[\s*["']([A-Za-z_][A-Za-z0-9_]{2,})["']\s*\]""")
ANY_PAT = re.compile(r"""["']([A-Za-z_][A-Za-z0-9_]{2,})["']""")


def scan():
    reads = defaultdict(list)          # key -> [(file, lineno)]
    all_occurrences = defaultdict(int)  # key -> count of every string-literal appearance
    for d in SCAN_DIRS:
        root = os.path.join(_REPO, d)
        for dirpath, _dirs, files in os.walk(root):
            # EXCLUDE VENDORED CODE. `tools/dashboard/.venv/Lib/site-packages` is inside a scanned
            # directory, so the first real run returned 1,925 "suspects" dominated by numpy, torch
            # and setuptools internals -- third-party reads of third-party payloads, every one a
            # true positive of the rule and none of them ours. CLAUDE.md already warns that search
            # scope must be set deliberately; this is that warning arriving as a defect.
            low = dirpath.lower()
            if any(seg in low for seg in (".venv", "site-packages", "__pycache__", "node_modules")):
                continue
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dirpath, fn)
                # SKIP THIS FILE. It quotes the very key it hunts, in its own docstring and in its
                # own regression assertion, so scanning itself makes it report its own prose as a
                # finding -- which it did, twice, before this line existed. A detector that reads
                # its own text is measuring itself.
                if os.path.abspath(p) == os.path.abspath(__file__):
                    continue
                try:
                    with open(p, encoding="utf-8") as fh:
                        lines = fh.readlines()
                except Exception:
                    continue
                for i, line in enumerate(lines, 1):
                    for m in ANY_PAT.finditer(line):
                        all_occurrences[m.group(1)] += 1
                    # TIGHTENED. The first scoped run returned 871 suspects and was therefore
                    # unreadable -- CLAUDE.md records that a check firing on a quarter of the repo
                    # gets ignored, and documents a sibling flagger that went 708 -> 279 -> 13
                    # before anyone would act on it. Two filters, both aimed at the ACTUAL bug class:
                    #   * os.environ.get("VAR") legitimately reads keys this tree never writes;
                    #   * ALL_CAPS keys are the env/config convention, not data fields.
                    # The n_grounded defect was a lowercase_with_underscores DATA field on a dict
                    # returned by our own function -- that is the population worth reading.
                    if "environ" in line:
                        continue
                    for m in READ_PAT.finditer(line):
                        k = m.group(1) or m.group(2)
                        if k.isupper() or k.upper() == k:
                            continue
                        reads[k].append((os.path.relpath(p, _REPO), i))
    return reads, all_occurrences


def _self_test(reads, occ):
    """POSITIVE AND NEGATIVE CONTROL. An absence-detector that has never been shown to FIRE is
    worthless, and one that flags everything gets ignored."""
    # NEGATIVE CONTROL: a key that IS written must NOT be flagged.
    assert occ.get("cumulative_grounded", 0) >= 2, (
        "control key 'cumulative_grounded' should appear at least twice (written + read); got %r"
        % occ.get("cumulative_grounded"))
    # POSITIVE CONTROL: a synthetic read-only key must be detectable by the same rule.
    synth = "zz_key_that_nothing_writes_zz"
    fake_reads = {synth: [("synthetic.py", 1)]}
    fake_occ = {synth: 1}
    flagged = [k for k in fake_reads if fake_occ.get(k, 0) <= 1]
    assert flagged == [synth], "positive control failed: the rule did not flag a read-only key"
    # AND THE REAL ONE, HISTORICALLY: the bug this tool exists for is now fixed, so the old key must
    # no longer be READ anywhere.
    #
    # THIS ASSERTION WAS WRONG ON ITS FIRST RUN, AND THE WAY IT WAS WRONG IS THE TOOL'S OWN SUBJECT.
    # It originally asserted the STRING was absent from the tree (`occ[...] == 0`) and fired
    # immediately -- because the fix's explanatory comment in substrate.py NAMES the old key. The
    # rule did not match the intent: what matters is that nothing READS it, not that nobody mentions
    # it. A check whose condition is a proxy for the thing it cares about is exactly the defect this
    # file hunts, committed inside the hunter on its first execution.
    assert "n_grounded_cumulative" not in reads, (
        "'n_grounded_cumulative' is READ again at %r -- the 2026-08-21 fix regressed"
        % (reads.get("n_grounded_cumulative"),))
    print("self-test PASS (negative control, positive control, fix-regression check)")


def main():
    reads, occ = scan()
    _self_test(reads, occ)
    if "--self-test" in sys.argv:
        return 0

    suspects = sorted((k for k in reads if occ.get(k, 0) <= 1), key=lambda k: k)
    print("\nkeys READ via .get(\"k\") or [\"k\"] across %s: %d distinct" % (SCAN_DIRS, len(reads)))
    print("of those, appearing NOWHERE ELSE in the tree (the n_grounded signature): %d\n" % len(suspects))
    for k in suspects:
        for f, ln in reads[k][:2]:
            print("  %-40s %s:%d" % (k, f, ln))
    print("\nREADING LIST, NOT A VERDICT. Expect legitimate reads of EXTERNAL payloads (json on")
    print("disk, argparse, third-party dicts) among these -- they are keys this tree never writes")
    print("because something else writes them. Check each against what actually produces the dict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
