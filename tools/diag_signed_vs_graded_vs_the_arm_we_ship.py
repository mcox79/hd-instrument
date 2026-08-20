"""THE ARM WE ACTUALLY SHIP HAS NEVER BEEN MEASURED. Measure it against the two that were.

THE SITUATION, established today by runtime call-counting and archive reading:
  `exp_graded_divisive_comparator_v1` measured TWO PURE configurations --
      R_LIVE  = signed query x signed anchors  -> 0.6395
      R_BASE  = graded query x graded anchors  -> 0.69975   (delta +0.0602)
      floors: scramble 0.4953 / 0.5065, frequency 0.4800; positive control self-retrieval 0.9133.
  **We run NEITHER.** `GRADED_COMPARATOR` flipped True on 2026-08-14, AFTER that cell, so the
  ANCHORS are graded -- but the QUERY is still signed, because `canonicalize` line 776 hardcodes
  `np.sign(new_raw_sum)` and takes **451 of 451** live selection calls (`canonicalize_fast`, the
  only graded-query door, takes 0).

**SO THE SHIPPED CONFIGURATION IS SIGNED-QUERY x GRADED-ANCHORS, AND NO CELL HAS SCORED IT.** The
code's own docstring calls exactly that combination the worst of the three:
    "a graded field read by a signed query is worse than either, because the query's magnitudes
     are exactly what the field's magnitudes are being compared to."
That is an assertion in a comment. This turns it into a measurement.

THE TASK is the synonym-rank task already built and running today: among all anchors, where does a
KNOWN-CORRECT synonym of the target land? It is a meaning task, it uses the substrate's own vectors,
and it has floors that already work.

FOUR ARMS -- three configurations plus the floor that matters:
  BOTH_SIGNED   sign(query) . sign(anchor)     -- R_LIVE's configuration
  SHIPPED       sign(query) . raw(anchor)      -- *** WHAT WE ACTUALLY RUN, never measured ***
  BOTH_GRADED   raw(query)  . raw(anchor)      -- R_BASE's configuration
  UNIFORM       a random rank                  -- the trivial floor
*The frequency floor is carried by the sibling run on the same items; it is not repeated here
because this comparison is WITHIN the substrate's own representation -- one variable, the
quantisation, exactly as the original cell varied it.*

GUARDS:
  * POSITIVE CONTROL: with the query set to an anchor's own vector, every arm must rank that anchor
    first. If an arm cannot do that, its ranks mean nothing.
  * every arm scored on the SAME items, same anchors, same seeds -- paired throughout.
  * the shipped arm is constructed to match line 776 exactly (`np.sign` of the raw sum, self
    excluded), not a tidier version of it.

PRE-COMMITTED READINGS:
  SHIPPED worse than BOTH_GRADED and worse than BOTH_SIGNED -> **the docstring is right and we run
      the worst of three.** A one-line change to `canonicalize` recovers it, and the archive already
      carries the floors and the positive control for the graded arm. This would be the cheapest
      real win available.
  SHIPPED ~ BOTH_GRADED -> the signed query costs nothing HERE; the docstring's warning does not
      bite on this task. Say so, and stop citing it.
  SHIPPED better than both -> the mixed form is fine and the concern is closed. Report it plainly;
      an unexpected result on a one-variable sweep is still a result.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from nltk.corpus import wordnet as wn  # noqa: E402

from hdlab.substrate import Substrate  # noqa: E402

SEEDS = (7, 101, 20260819)
CORPUS = os.environ.get("DIAG_CORPUS", "simplewiki")
N_READ = int(os.environ.get("DIAG_N_READ", "8000"))
ARMS = ("BOTH_SIGNED", "SHIPPED", "BOTH_GRADED", "UNIFORM")


def synonyms(w):
    out = set()
    try:
        for s in wn.synsets((w or "").lower()):
            for lem in s.lemma_names():
                out.add(lem.lower().replace("_", " "))
    except Exception:
        pass
    out.discard((w or "").lower())
    return out


def _cos_rows(q, M):
    qn = np.linalg.norm(q)
    Mn = np.linalg.norm(M, axis=1)
    ok = Mn > 1e-12
    out = np.full(M.shape[0], -2.0)
    if qn > 1e-12:
        out[ok] = (M[ok] @ q) / (Mn[ok] * qn)
    return out


def score(arm, raw_q, mat, sgn_mat, rng, n):
    if arm == "UNIFORM":
        return None
    q = np.sign(raw_q) if arm in ("BOTH_SIGNED", "SHIPPED") else raw_q
    M = sgn_mat if arm == "BOTH_SIGNED" else mat
    return _cos_rows(q, M)


def _selftest(mat, sgn_mat):
    """Every arm must rank an anchor first when handed that anchor's own vector."""
    rng = np.random.default_rng(0)
    i = 3
    for arm in ("BOTH_SIGNED", "SHIPPED", "BOTH_GRADED"):
        c = score(arm, mat[i].copy(), mat, sgn_mat, rng, mat.shape[0])
        assert int(np.argmax(c)) == i, "%s failed the self-retrieval control" % arm
    print("selftest: all three arms self-retrieve an anchor from its own vector", flush=True)


rows = []
for seed in SEEDS:
    sub = Substrate(seed=seed)
    total = 0
    while total < N_READ:
        r = sub.read(corpus=CORPUS, n_sentences=min(800, N_READ - total), batch=50,
                     max_patches=1, consolidate_every=200)
        if r.n_sentences == 0:
            break
        total += r.n_sentences

    space = sub.state.space
    anchors, mat = space.anchor_matrix()
    if len(anchors) < 50:
        print("seed %s: only %d anchors -- skipped" % (seed, len(anchors)), flush=True)
        continue
    mat = np.asarray(mat, dtype=np.float64)
    sgn_mat = np.sign(mat)
    pos = {a: i for i, a in enumerate(anchors)}
    if seed == SEEDS[0]:
        _selftest(mat, sgn_mat)

    rng = np.random.default_rng(seed)
    res = {a: [] for a in ARMS}
    sums = getattr(space, "_sums", {})
    for lemma in sorted(sums):
        present = [a for a in synonyms(lemma) if a in pos and a != lemma]
        if not present:
            continue
        raw_q = np.asarray(sums[lemma], dtype=np.float64)
        for arm in ARMS:
            if arm == "UNIFORM":
                res[arm].append(int(rng.integers(1, len(anchors) + 1)))
                continue
            c = score(arm, raw_q, mat, sgn_mat, rng, len(anchors))
            if lemma in pos:
                c[pos[lemma]] = -2.0
            res[arm].append(min(int(np.sum(c > c[pos[a]])) + 1 for a in present))

    if len(res["SHIPPED"]) < 30:
        print("seed %s: only %d scorable words -- skipped" % (seed, len(res["SHIPPED"])), flush=True)
        continue
    rows.append({"seed": seed, "n_anchors": len(anchors),
                 **{a: res[a] for a in ARMS}})
    print("seed %-9s anchors %4d words %4d | " % (seed, len(anchors), len(res["SHIPPED"]))
          + "  ".join("%s %6.1f" % (a, np.median(res[a])) for a in ARMS), flush=True)

if len(rows) < 2:
    print("\nfewer than 2 usable seeds -- NO VERDICT")
    raise SystemExit(0)
with open(os.path.join(_REPO, "scratch", "quantisation_arms.json"), "w", encoding="utf-8") as fh:
    json.dump(rows, fh, indent=1)

rng = np.random.default_rng(0)


def paired(a, b):
    d = np.concatenate([np.asarray(r[a], float) - np.asarray(r[b], float) for r in rows])
    bb = np.array([np.median(d[rng.integers(0, d.size, d.size)]) for _ in range(4000)])
    lo, hi = np.percentile(bb, [2.5, 97.5])
    sep = not (lo <= 0 <= hi)
    print("   %-30s %+8.1f  95%% CI [%+.1f, %+.1f]  %s"
          % ("%s - %s" % (a, b), np.median(d), lo, hi, "SEPARATED" if sep else "not separated"))
    return float(np.median(d)), sep


print("\n" + "=" * 78)
print("POOLED PAIRED (negative = the FIRST arm ranks the correct synonym BETTER):")
d_sg, s_sg = paired("SHIPPED", "BOTH_GRADED")
d_ss, s_ss = paired("SHIPPED", "BOTH_SIGNED")
d_gs, s_gs = paired("BOTH_GRADED", "BOTH_SIGNED")
paired("SHIPPED", "UNIFORM")

print()
if s_sg and d_sg > 0:
    print("VERDICT: **THE ARM WE SHIP IS WORSE THAN THE FULLY GRADED ONE** (%+.1f ranks). The" % d_sg)
    print("docstring's warning is now a measurement, not an assertion. `canonicalize` line 776")
    print("quantises the query against a graded field; removing that one `np.sign` is the change.")
    if s_ss and d_ss > 0:
        print("AND it is worse than the fully SIGNED arm too -- the worst of the three, exactly as")
        print("the docstring predicted. VET before changing the live path.")
elif not s_sg:
    print("VERDICT: **THE SIGNED QUERY COSTS NOTHING ON THIS TASK.** SHIPPED ties BOTH_GRADED, so")
    print("the docstring's warning does not bite here. Stop citing it as a live defect.")
else:
    print("VERDICT: **THE MIXED FORM IS BETTER**, which nobody predicted. Report it plainly and")
    print("do not change the live path on the strength of a docstring that this contradicts.")
