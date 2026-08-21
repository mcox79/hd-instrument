"""Are the 11,930 refusals PRODUCED BY THE READ, or were they already in the foundation on disk?

THE CLAIM BEING CHECKED. Tonight's probe reported, after reading with two loaded foundations:

    v1 (4322 anchors)        refusals=525    [TAUTOLOGY_NO_ANCHOR 488]
    v2_qualityfix (1415)     refusals=11930  [TAUTOLOGY_NO_ANCHOR 11777]

and I wrote that a quality-filtered foundation refusing **22x more often** is *"either the most
informative thing in that run or a second bug."*

**BUT `state.refusals` IS A PERSISTED LIST THAT TRAVELS WITH THE FOUNDATION.** It is not a counter
that starts at zero when you begin reading. So the 22x may be a property of the SAVED STATE rather
than anything the read did -- **the same error as attributing an accumulated quantity to an
intervention, which is what has gone wrong three times tonight in three different disguises.**

**THIS SCRIPT DOES NOT READ ANYTHING.** It loads each foundation and counts, so any refusal it sees
existed before a single sentence was processed. *No read = no possible contribution from reading =
the number is unambiguous.*
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

ARMS = [("data/foundation/reading_grounding_v1", "v1", 525),
        ("data/foundation/reading_grounding_v2_qualityfix", "v2_qualityfix", 11930)]


def main():
    from hdlab import foundation_persistence as fp

    print("%-16s %10s %12s %12s %10s" % ("foundation", "anchors", "REFUSALS", "reported", "from read"))
    print("-" * 66)
    for d, label, reported_after_read in ARMS:
        if not os.path.isdir(d):
            print("%-16s  MISSING" % label)
            continue
        st = fp.load_foundation(d)
        n_anchor = len(st.space.anchors())
        ref = list(getattr(st, "refusals", []) or [])
        at_load = len(ref)
        print("%-16s %10d %12d %12d %10d"
              % (label, n_anchor, at_load, reported_after_read, reported_after_read - at_load))
        c = collections.Counter(x.get("reason", "?") for x in ref)
        for reason, n in c.most_common(3):
            print("        %-30s %6d  (%.1f%% of the arm's refusals at load)"
                  % (reason, n, 100.0 * n / max(1, at_load)))
    print()
    print("READ THE 'from read' COLUMN. If it is small relative to 'REFUSALS', the 22x asymmetry")
    print("is a property of the SAVED FOUNDATION and says nothing about what reading did.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
