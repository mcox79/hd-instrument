"""Did today's light-noun fix change what the substrate actually assigns as a meaning?

WHY. `exp_grounding_precision_gold_v1` (3 seeds, 40,000 sentences each) recorded **`top_anchor` =
`way` on ALL THREE SEEDS** -- a contentless word was the single most-assigned meaning in the whole
grounding output. Today `way`, `means` and `part` were added to `_MEASURE_HEAD`, so the existing
partitive expansion now resolves past them (`a means of dispersal` -> `dispersal` rather than
`means`).

**AND THE FIX IS CONFIRMED LIVE, NOT ASSUMED**: over 1,200 sentences of real reading,
`extract_definitions` is called **1,150 times** and `definiens_head` **98 times**. The extractor is
on the reading path and heavily used.

So: does the top-anchor distribution actually move? This measures the ONE thing the precision cell
flagged, on the live path, after the change.

⚠️ **THIS IS NOT A QUALITY MEASUREMENT.** A different top anchor is not a better grounding. It says
only whether the fix reached the output distribution. Whether precision improved needs the
independent-gold cell re-run, which is ~1.5 hours and is NOT this.

PRE-COMMITTED READINGS:
  `way` gone or far down -> the fix reaches the output. Worth re-running the gold cell to see if
      precision moved.
  `way` still top -> the fix did not reach this path, or the light noun arrives by a route the
      partitive expansion does not cover. Either way, say so and do not claim the fix helped.
  a DIFFERENT empty word now on top (`thing`, `word`, `idea`) -> the defect moved rather than
      resolved, which is worth knowing before anyone adds more words to a list.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import collections  # noqa: E402
import sys  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.substrate import Substrate  # noqa: E402

N_READ = int(os.environ.get("DIAG_N_READ", "12000"))
EMPTY = {"way", "ways", "means", "part", "parts", "thing", "things", "kind", "kinds", "type",
         "types", "sort", "sorts", "form", "forms", "use", "uses", "word", "words", "term",
         "terms", "idea", "ideas", "name", "names"}

for seed in (7, 101):
    sub = Substrate(seed=seed)
    total = 0
    while total < N_READ:
        r = sub.read(corpus="simplewiki", n_sentences=min(800, N_READ - total), batch=50,
                     max_patches=1, consolidate_every=200)
        if r.n_sentences == 0:
            break
        total += r.n_sentences

    con = sub.consolidated()
    vals = [v for v in con.values() if v]
    if not vals:
        print("seed %s: read %d, consolidated %d, NONE carry a meaning -- nothing to report"
              % (seed, total, len(con)), flush=True)
        continue
    cnt = collections.Counter(vals)
    n_empty = sum(v for k, v in cnt.items() if str(k).lower() in EMPTY)
    print("\nseed %s | read %d | consolidated %d | with a meaning %d"
          % (seed, total, len(con), len(vals)), flush=True)
    print("   semantically-empty anchors: %d of %d (%.1f%%)"
          % (n_empty, len(vals), 100.0 * n_empty / len(vals)), flush=True)
    print("   TOP ANCHORS:", flush=True)
    for k, v in cnt.most_common(10):
        flag = "   <-- EMPTY" if str(k).lower() in EMPTY else ""
        print("      %-18s %3d  (%.1f%%)%s" % (k, v, 100.0 * v / len(vals), flag), flush=True)

print("\nREFERENCE: exp_grounding_precision_gold_v1 recorded top_anchor='way' on all 3 seeds,")
print("share ~3.0%, over 40,000 sentences per seed. This run is smaller; compare the RANK of")
print("`way`, not the share.")
