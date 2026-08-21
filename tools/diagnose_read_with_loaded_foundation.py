"""Re-run of "the decisive test: read with a loaded foundation" -- THE FIRST RUN MEASURED NOTHING.

WHAT THE FIRST RUN REPORTED, and it looked like a clean, decisive double null:

    v1 (4322 anchors)    anchors 4322 -> 4454 after 1540 sents | GROUNDED(last)=0 | refusals=525
    v2_qualityfix (1415) anchors 1415 -> 1506 after 1600 sents | GROUNDED(last)=0 | refusals=11930

*** BOTH ZEROS ARE ARTIFACTS OF THE PROBE, NOT MEASUREMENTS. TWO SEPARATE DEFECTS. ***

**1. THE CORPUS WAS EXHAUSTED AND THE LAST READ CONSUMED ZERO SENTENCES.** The probe asked for
`3 x 1200 = 3600` sentences and the totals came back **1540** and **1600** -- i.e. 1200 + 340 + 0
and 1200 + 400 + 0. **`GROUNDED(last)` was read off a `read()` call that processed NO TEXT**, so it
could only ever have been 0. `hdlab/substrate.py:949`, the repo's OWN self-test, asserts exactly
this -- `assert res.n_sentences > 0, "read() consumed no sentences"` -- and my probe omitted it.

**2. IT REPORTED ONE THIRD OF THE EXPERIMENT.** `tot` accumulated `n_sentences` across all three
calls, but the printed grounded count came from `r`, **the last call only**. The grounded counts
from the first two calls -- the ones that actually read text -- were computed and thrown away.

*This is the standing rule verbatim: **A NULL THAT IS EXACTLY ZERO IS A REACHABILITY FAILURE, NOT A
RESULT.** Two independent bugs both drove the headline to exactly 0.0, and the agreement between
the two arms made it look like a robust finding rather than a broken instrument.*

THE CORRECTED PROBE: one read per arm sized to what the corpus actually holds, per-call sentence
AND grounded counts printed, a hard guard that refuses to report a number from a zero-sentence read,
and refusal reasons broken out as a DELTA so they are attributable to this read.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

ARMS = [("data/foundation/reading_grounding_v1", "v1"),
        ("data/foundation/reading_grounding_v2_qualityfix", "v2_qualityfix")]
BUDGET = int(os.environ.get("DIAG_BUDGET", "1200"))


def main():
    import hdlab.substrate as S
    from hdlab import foundation_persistence as fp

    for d, label in ARMS:
        print("\n" + "=" * 78)
        print("ARM %s   foundation=%s" % (label, d))
        print("=" * 78)
        if not os.path.isdir(d):
            print("  MISSING foundation directory -- arm not run")
            continue
        sub = S.Substrate()
        sub.state = fp.load_foundation(d)          # read-only load
        a0 = len(sub.state.space.anchors())
        ref0 = len(getattr(sub.state, "refusals", []))

        res = sub.read(n_sentences=BUDGET)

        # THE GUARD THE FIRST RUN LACKED. A grounded count from a zero-sentence read is not a null.
        if res.n_sentences <= 0:
            print("  READ CONSUMED 0 SENTENCES -- corpus exhausted or unavailable.")
            print("  NO NUMBER IS REPORTABLE FROM THIS ARM. (This is what silently produced the")
            print("  original GROUNDED(last)=0.)")
            continue

        a1 = len(sub.state.space.anchors())
        ref = getattr(sub.state, "refusals", [])
        delta = ref[ref0:]                          # attributable to THIS read, not the foundation
        c = collections.Counter(x.get("reason", "?") for x in delta)

        print("  sentences read      %d  (requested %d)%s"
              % (res.n_sentences, BUDGET,
                 "   <-- SHORT: corpus exhausted mid-read" if res.n_sentences < BUDGET else ""))
        print("  anchors             %d -> %d   (+%d)" % (a0, a1, a1 - a0))
        print("  n_grounded          %d   (cumulative within this read)" % res.n_grounded)
        print("  grounded / sentence %.4f" % (res.n_grounded / res.n_sentences))
        print("  refusals THIS read  %d   (foundation already carried %d)" % (len(delta), ref0))
        for reason, n in c.most_common(5):
            print("      %-28s %6d  (%.1f per sentence)" % (reason, n, n / res.n_sentences))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
