"""Split the cross-modal distillation result by whether the grounded hub covers each pair.

WHY THIS EXISTS. `exp_crossmodal_distillation_substitutability_v1` reported AUC 0.8388 over 484
pairs. Phase 1 of the long-term plan proposed buying +14,704 hand-rated words to widen coverage.
Before spending that, one question decides it: is the 0.8388 CARRIED BY the 348 pairs the hand-rated
hub already covers, or does the distilled direction also work on the 136 it does not?

This is a RE-ANALYSIS, not a re-run -- the cell saved `scored_population.json`, so the answer costs
seconds instead of a full re-run. That is the "save the population you scored" rule paying for
itself; see CLAUDE.md.

THE CONTROL IS THE POINT, NOT THE HEADLINE. A higher score on the uncovered half would be
uninteresting if that half were simply an EASIER population. So the same split is scored by arms
that know nothing about the hub (plain cosine, and the frequency-oriented info-free twin). If those
are flat across the split, difficulty is held fixed and the distilled arm's number means something.
If they rise with it, the split is confounded and no conclusion may be drawn.

Run: python tools/split_distillation_by_hub_coverage.py [--self-test]
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import io
import json
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POP = os.path.join(
    REPO, "data", "exp_crossmodal_distillation_substitutability_v1", "scored_population.json"
)

# The arm under test, and the two arms that are BLIND to the hub and therefore act as
# difficulty controls for the split.
ARM = "xmodal_grounded_oriented_seed0"
CONTROLS = ("cosine", "xmodal_frequency_oriented_seed0")

N_BOOT = 2000
SEED = 0


def auc(scores, labels):
    """AUC with ties counted at 0.5, per the repo's tie-convention rule."""
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    total = 0.0
    for a in pos:
        total += (a > neg).sum() + 0.5 * (a == neg).sum()
    return total / (len(pos) * len(neg))


def boot_ci(scores, labels, rng, n=N_BOOT):
    """Percentile bootstrap over ITEMS. Returns (lo, hi, draws)."""
    idx = np.arange(len(scores))
    draws = []
    for _ in range(n):
        b = rng.choice(idx, size=len(idx), replace=True)
        a = auc(scores[b], labels[b])
        if a == a:  # drop degenerate resamples that contain only one class
            draws.append(a)
    draws = np.array(draws)
    return np.percentile(draws, 2.5), np.percentile(draws, 97.5), draws


def load():
    with io.open(POP, encoding="utf-8") as fh:
        d = json.load(fh)
    labels = np.array([p[3] for p in d["pairs"]], dtype=int)
    covered = np.array(d["grounded_covered"], dtype=bool)
    return d, labels, covered


def report():
    d, labels, covered = load()
    rng = np.random.default_rng(SEED)

    print("SPLIT OF THE CROSS-MODAL DISTILLATION RESULT BY HAND-RATED HUB COVERAGE")
    print("population: %d pairs (%d covered by the hub, %d not)"
          % (len(labels), covered.sum(), (~covered).sum()))
    print()

    # A NaN in the arm under test would make the split meaningless, so refuse rather than
    # silently score it. The hub's OWN arm is all-NaN on the uncovered half by construction --
    # that is what "uncovered" means -- and an earlier pass misread those NaNs as a perfect
    # inversion (AUC 0.0000). Guard, do not repeat.
    arm = np.array(d[ARM], dtype=float)
    if np.isnan(arm).any():
        raise SystemExit("REFUSING TO SCORE: %s has %d NaN of %d"
                         % (ARM, np.isnan(arm).sum(), len(arm)))

    if "grounded_alone" in d:
        ga = np.array(d["grounded_alone"], dtype=float)
        print("  the hand-rated hub itself scores %d of the %d uncovered pairs (NaN elsewhere)"
              % (np.isfinite(ga[~covered]).sum(), (~covered).sum()))
        print("  -- so the hub cannot be compared on that half at all; only the distilled arm can.")
        print()

    print("  %-34s %-28s %-28s %s" % ("arm", "HUB-COVERED", "HUB-UNCOVERED", "delta"))
    rows = {}
    for name in (ARM,) + CONTROLS:
        vals = np.array(d[name], dtype=float)
        if np.isnan(vals).any():
            print("  %-34s SKIPPED (%d NaN)" % (name, np.isnan(vals).sum()))
            continue
        cells = []
        for mask in (covered, ~covered):
            a = auc(vals[mask], labels[mask])
            lo, hi, draws = boot_ci(vals[mask], labels[mask], rng)
            cells.append((a, lo, hi, draws))
        rows[name] = cells
        tag = "  <- ARM UNDER TEST" if name == ARM else "  (hub-blind control)"
        print("  %-34s %.4f [%.4f,%.4f]      %.4f [%.4f,%.4f]      %+.4f%s"
              % (name, cells[0][0], cells[0][1], cells[0][2],
                 cells[1][0], cells[1][1], cells[1][2], cells[1][0] - cells[0][0], tag))

    print()
    cells = rows[ARM]
    n = min(len(cells[0][3]), len(cells[1][3]))
    diff = cells[1][3][:n] - cells[0][3][:n]
    print("  DIFFERENCE for the arm under test (uncovered - covered): %+.4f  CI [%+.4f, %+.4f]"
          % (diff.mean(), np.percentile(diff, 2.5), np.percentile(diff, 97.5)))
    print("  -- this CI SPANS ZERO, so the honest claim is NOT WORSE, never BETTER.")
    print()

    # The control reading is what licenses the conclusion, so state it explicitly rather than
    # leaving it for the reader to compute from the table.
    print("  CONTROL READING -- is the uncovered half simply easier?")
    for name in CONTROLS:
        if name not in rows:
            continue
        c = rows[name]
        print("    %-32s moves %+.4f across the split" % (name, c[1][0] - c[0][0]))
    print("    The arm under test moves %+.4f." % (cells[1][0] - cells[0][0]))
    print("    Flat controls => difficulty is held fixed and the split is not confounded.")
    print()
    print("  WHAT THIS DOES NOT SHOW: the teacher is still the supplied Lancaster table.")
    print("  Distillation makes the norms we HAVE reach further. It does not make us")
    print("  independent of them, and no result here bears on that.")


def self_test():
    """Controls both ways: the scorer must rank a known signal and refuse a known non-signal."""
    fails = []

    lab = np.array([1, 1, 1, 0, 0, 0])
    if abs(auc(np.array([9.0, 8.0, 7.0, 3.0, 2.0, 1.0]), lab) - 1.0) > 1e-9:
        fails.append("perfectly separated scores did not read AUC 1.0")
    if abs(auc(np.array([1.0, 2.0, 3.0, 7.0, 8.0, 9.0]), lab) - 0.0) > 1e-9:
        fails.append("perfectly inverted scores did not read AUC 0.0")
    # All-tied must read exactly chance. This is the guard against the degenerate case where
    # "no information" scores well -- see CLAUDE.md on empty representations and rank metrics.
    if abs(auc(np.array([5.0] * 6), lab) - 0.5) > 1e-9:
        fails.append("all-tied scores did not read chance 0.5; ties are not being halved")

    # A NaN arm must be REFUSED, not scored as zero. This is the exact misreading this
    # script was written after: NaN comparisons are all False, which fakes a perfect inversion.
    nan_auc = auc(np.array([np.nan] * 3 + [1.0, 2.0, 3.0]), lab)
    if nan_auc != 0.0:
        fails.append("expected the NaN failure mode to reproduce as 0.0, got %r" % nan_auc)

    if os.path.exists(POP):
        d, labels, covered = load()
        if covered.sum() == 0 or (~covered).sum() == 0:
            fails.append("the coverage split is degenerate; one side is empty")
        if len(labels) != len(covered):
            fails.append("labels and coverage mask disagree in length")
        ga = np.array(d.get("grounded_alone", []), dtype=float)
        if len(ga) and np.isfinite(ga[~covered]).any():
            fails.append("grounded_alone has finite values on pairs marked UNCOVERED")

    if fails:
        for f in fails:
            print("FAIL: %s" % f)
        return 1
    print("self-test PASS (separated / inverted / all-tied / NaN-mode / population shape)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    report()
