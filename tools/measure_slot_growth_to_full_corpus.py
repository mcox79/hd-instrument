"""What does slot count actually COST at the largest scale we can read? -- the open capacity question.

**THE ONLY VERSION OF "CAPACITY" THE EVIDENCE LEAVES OPEN.** Three sleep proposals died to three
cheap measurements: the cascade defends shared slots and ours are private; the cold-storage tiering
is already built and merely unwired; and there are no duplicates to consolidate. **All of that was
measured at 4,096 sentences.** The Heaps exponent `beta = 0.589` **does not saturate**, so the honest
remaining question is what the count costs two orders of magnitude up -- **a pathology that appears
only there would have been invisible.**

**THIS MEASURES RATHER THAN EXTRAPOLATES, AS FAR AS THE DISK ALLOWS.** 325,798 sentences are
readable across all corpora -- within an order of magnitude of 10^6. Slot COUNT needs only lemma
extraction, not vector accumulation, so the full stream is affordable where the accumulating run was
not.

⚠️ **AND THE DISTINCTION IS STATED IN THE OUTPUT**: everything up to the largest read is MEASURED;
anything beyond it is EXTRAPOLATION from a fitted exponent and is labelled as such. *Extrapolating a
power law two decades past your data is exactly how a comfortable number gets manufactured.*
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import math  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)


def main():
    from hdlab.corpus_registry import CorpusRegistry
    from hdlab.reading_grounding_loop import CTX_D, content_lemmas

    bytes_per_slot = CTX_D * 8            # float64 accumulator, as ConceptSpace stores it
    reg = CorpusRegistry()
    names = sorted(reg.readable_names())
    seen, rows, n = set(), [], 0
    marks, k = [], 1
    while k <= 400000:
        marks.append(k)
        k *= 2
    marks = set(marks)

    for nm in names:
        h = reg.handles[nm]
        try:
            pool = h.pool()
        except Exception:
            continue
        for s in pool:
            n += 1
            seen.update(content_lemmas(s))
            if n in marks:
                rows.append((n, len(seen)))
        print("  ...%-30s cumulative %7d sentences, %7d slots" % (nm, n, len(seen)), flush=True)
    rows.append((n, len(seen)))

    print("\n" + "=" * 76)
    print("MEASURED -- all %d readable sentences on disk" % n)
    print("=" * 76)
    print("%12s %10s %12s %12s" % ("sentences", "slots", "slots/sent", "accum. size"))
    for a, b in rows:
        print("%12d %10d %12.3f %10.1f MB" % (a, b, b / a, b * bytes_per_slot / 1e6))

    # fit beta on the last decade only -- the early curve is dominated by function words
    tail = [(a, b) for a, b in rows if a >= rows[-1][0] / 12]
    (n1, a1), (n2, a2) = tail[0], tail[-1]
    beta = math.log(a2 / a1) / math.log(n2 / n1)
    print("\nHeaps exponent over the last decade of DATA: beta = %.3f" % beta)
    print("  (measured from %d->%d sentences, %d->%d slots)" % (n1, n2, a1, a2))

    print("\n" + "=" * 76)
    print("EXTRAPOLATION -- NOT MEASURED. Power law fitted above, projected forward.")
    print("=" * 76)
    for target in (10 ** 6, 10 ** 7):
        proj = a2 * (target / n2) ** beta
        print("  %,d sentences -> ~%s slots, ~%.1f GB"
              .replace("%,d", "%d") % (target, "{:,}".format(int(proj)),
                                       proj * bytes_per_slot / 1e9))
    print("\n**THE EXTRAPOLATION IS THE WEAKEST NUMBER HERE and is labelled so deliberately.**")
    print("A power law fitted over one decade and projected across two more is a guess with a")
    print("straight line through it. The MEASURED column is the finding; the projection is a")
    print("planning aid, and the honest way to improve it is to read more, not to fit harder.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
