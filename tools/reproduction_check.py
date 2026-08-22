"""A RE-RUN THAT REPLAYED ITS CHECKPOINTS IS NOT A REPRODUCTION. This refuses to let you call it one.

WHY THIS EXISTS. `notes/RESUMABILITY_DEFEATS_REPRODUCTION_CHECKING_2026-08-22.md` recorded the hazard
on ONE cell: re-running a landed cell finished in `elapsed 0.0s` with five resume-and-skip lines, and
**the verdict line and every number came back identical without any work being done.** The author's
own words: *"I would have reported verified and reproduces exactly on the strength of the verdict line
alone, which is what a verification step exists to prevent."*

The note filed the harness fix (a `--fresh-units` flag) for a decision rather than making it, and
**built no detector**, so for a day the only thing standing between a no-op and a "reproduced" was
whether a human happened to read the elapsed time. That is a caution written as prose, and this repo
has measured what happens to those.

ARCHIVE SCALE, measured here rather than assumed (`--census`): **399 of 7,868 landed cells (5.1%)
carry a non-empty `units.jsonl`, so re-running any of them replays instead of recomputing.** A further
18 dirs have units and no `metrics.json`. **Zero unit files are empty**, so there is no benign subset.

WHAT THIS DOES NOT DO. It cannot make a cell recompute -- that is the harness change, and forcing it
by deleting checkpoints is separately forbidden here. It tells you what a re-run WOULD be, and
classifies one you already ran. **It casts no doubt on any landed number; it bears only on whether
anyone has verified it.**

Usage:
    python tools/reproduction_check.py --census            # how much of the archive would replay
    python tools/reproduction_check.py <output_dir>        # would a re-run of THIS cell replay?
    python tools/reproduction_check.py --self-test
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DATA = os.path.join(REPO_ROOT, "data")

REPLAYED = "REPLAYED_NOT_A_REPRODUCTION"
RECOMPUTED = "RECOMPUTED"
PARTIAL = "PARTIAL_REPLAY"
INDETERMINATE = "INDETERMINATE_NO_BEFORE_SNAPSHOT"


def unit_count(output_dir: str) -> int:
    """Number of durably recorded units. 0 means a re-run would recompute from scratch."""
    p = os.path.join(output_dir, "units.jsonl")
    if not os.path.isfile(p):
        return 0
    n = 0
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def would_replay(output_dir: str):
    """(bool, n_units) -- would re-running this cell skip work it has already done?"""
    n = unit_count(output_dir)
    return (n > 0, n)


class ReproductionVerdict:
    """Carries WHY, so a caller cannot reduce it to a boolean by accident.

    There is deliberately no `__bool__` and no attribute called `reproduced`. The whole failure this
    guards against is a person reading one line and concluding "verified", so the object refuses to
    offer that line.
    """

    def __init__(self, status, units_before, units_after, elapsed_s=None):
        self.status = status
        self.units_before = units_before
        self.units_after = units_after
        self.units_computed = (None if units_after is None or units_before is None
                               else units_after - units_before)
        self.elapsed_s = elapsed_s

    def __bool__(self):
        raise TypeError(
            "ReproductionVerdict has no truth value -- read .status. A re-run that replayed its "
            "checkpoints returns identical numbers without doing any work, so 'it passed' is "
            "exactly the reading this guard exists to prevent.")

    def __repr__(self):
        return ("ReproductionVerdict(status=%s, units %s->%s, computed=%s, elapsed=%s)"
                % (self.status, self.units_before, self.units_after,
                   self.units_computed, self.elapsed_s))

    def is_evidence_of_reproduction(self) -> bool:
        """The ONLY affirmative accessor, and it is named so a reader cannot mistake its scope."""
        return self.status == RECOMPUTED


def classify_run(units_before, units_after, elapsed_s=None) -> ReproductionVerdict:
    """Classify a re-run you have already performed. Pure; no I/O.

    `units_before` MUST be captured before the run. Without it nothing can be concluded -- which is
    the honest answer, not a failure of this tool.
    """
    if units_before is None or units_after is None:
        return ReproductionVerdict(INDETERMINATE, units_before, units_after, elapsed_s)
    computed = units_after - units_before
    if units_before > 0 and computed <= 0:
        return ReproductionVerdict(REPLAYED, units_before, units_after, elapsed_s)
    if units_before > 0 and computed > 0:
        return ReproductionVerdict(PARTIAL, units_before, units_after, elapsed_s)
    return ReproductionVerdict(RECOMPUTED, units_before, units_after, elapsed_s)


def census(data_dir: str = DATA):
    """(landed, would_replay_and_landed, units_no_metrics). Enumerated from disk, not a registry."""
    landed = replay_landed = orphan_units = 0
    rows = []
    for name in sorted(os.listdir(data_dir)):
        d = os.path.join(data_dir, name)
        if not os.path.isdir(d):
            continue
        has_metrics = os.path.isfile(os.path.join(d, "metrics.json"))
        n = unit_count(d)
        if has_metrics:
            landed += 1
        if n > 0 and has_metrics:
            replay_landed += 1
            rows.append((name, n))
        elif n > 0:
            orphan_units += 1
    return landed, replay_landed, orphan_units, rows


def run(argv):
    if "--census" in argv:
        landed, replay_landed, orphan, rows = census()
        # COUNTS BEFORE RESULTS -- silence must never read as absence.
        print("[reproduction-check] %d landed cells scanned" % landed)
        print("  %d (%.1f%%) carry checkpoint units, so RE-RUNNING THEM REPLAYS rather than recomputes"
              % (replay_landed, 100.0 * replay_landed / max(1, landed)))
        print("  %d dirs carry units with NO metrics.json (never landed)" % orphan)
        print("\n  the 10 largest, by units that would be skipped:")
        for name, n in sorted(rows, key=lambda r: -r[1])[:10]:
            print("    %6d  %s" % (n, name[:70]))
        print("\n  A REPLAY REPRODUCES EVERY NUMBER WITHOUT DOING ANY WORK. None of this casts doubt")
        print("  on the landed values -- only on whether re-running one verifies them.")
        return 0
    targets = [a for a in argv if not a.startswith("--")]
    if not targets:
        print(__doc__.strip().splitlines()[-4])
        return 2
    for t in targets:
        d = t if os.path.isdir(t) else os.path.join(DATA, t)
        if not os.path.isdir(d):
            print("  %-50s NO SUCH DIR" % t)
            continue
        rep, n = would_replay(d)
        print("  %-50s %s (%d units on disk)"
              % (os.path.basename(d), "WOULD REPLAY -- a re-run proves nothing" if rep
                 else "would recompute", n))
    return 0


def self_test():
    import json
    import tempfile
    ok = True

    def check(c, label):
        nonlocal ok
        print("[self-test] %s %s" % ("PASS" if c else "FAIL", label),
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    # THE REAL FAILURE: units already present, run computes nothing, returns identical numbers.
    v = classify_run(units_before=5, units_after=5, elapsed_s=0.0)
    check(v.status == REPLAYED, "5 units in, 5 out, 0.0s -> REPLAYED_NOT_A_REPRODUCTION")

    # NEGATIVE CONTROL: a genuine fresh recompute must NOT be flagged, or the guard cries wolf.
    check(classify_run(0, 5, 61.0).status == RECOMPUTED,
          "NEGATIVE CONTROL: a fresh dir that computed 5 units -> RECOMPUTED")
    check(classify_run(2, 5, 30.0).status == PARTIAL, "resumed midway -> PARTIAL_REPLAY")
    check(classify_run(None, 5).status == INDETERMINATE,
          "no before-snapshot -> INDETERMINATE, not a pass")

    # THE VERDICT MUST NOT COLLAPSE TO A BOOLEAN -- that collapse IS the incident.
    try:
        bool(classify_run(5, 5, 0.0))
        check(False, "bool(verdict) should have raised")
    except TypeError:
        check(True, "bool(verdict) raises -- it cannot be read as 'it passed'")
    check(classify_run(5, 5, 0.0).is_evidence_of_reproduction() is False,
          "a replay is NOT evidence of reproduction")
    check(classify_run(0, 5, 9.0).is_evidence_of_reproduction() is True,
          "a real recompute IS evidence of reproduction")

    # CONTRACT TEST AGAINST REAL DATA, not fixtures -- a fabricated units.jsonl would certify a
    # format I invented. This reads whatever is actually on disk today.
    landed, replay_landed, orphan, rows = census()
    check(landed > 1000, "census sees the real archive (%d landed)" % landed)
    check(replay_landed > 0,
          "POSITIVE CONTROL: at least one real landed cell would replay (%d do)" % replay_landed)
    if rows:
        name, n = rows[0]
        d = os.path.join(DATA, name)
        rep, k = would_replay(d)
        check(rep and k == n, "a real cell dir (%s) reports WOULD REPLAY with %d units" % (name, k))
        # and its units.jsonl really is the format exp_checkpoint writes
        with open(os.path.join(d, "units.jsonl"), encoding="utf-8", errors="replace") as f:
            first = json.loads(next(l for l in f if l.strip()))
        check(isinstance(first, dict), "real units.jsonl lines parse as dicts")

    # NEGATIVE CONTROL on the filesystem side: an empty dir must not be flagged.
    with tempfile.TemporaryDirectory() as td:
        rep, n = would_replay(td)
        check((not rep) and n == 0, "NEGATIVE CONTROL: an empty dir does NOT report a replay")

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test() if "--self-test" in sys.argv else run(sys.argv[1:]))
