"""THE WELL-POWERED QUESTION: not "did we pick the right word" but "HOW CLOSE DID IT COME?"

WHY THE PREVIOUS FORM WAS WORTHLESS. Last run reported that where a correct synonym was in the
anchor pool we chose something else **775 of 775 times**. It means nothing: a correct synonym is
typically ONE word in a 334-2,744 word pool, so a RANDOM picker is expected to score 0.44 and 0.16
hits and P(zero | random) is 0.64 and 0.85. A binary hit on a 1-in-2,744 event cannot distinguish
good selection from chance no matter how many facts it runs on.

**RANK FIXES THAT.** Where the correct synonym LANDS among all anchors is continuous, uses every
opportunity rather than only the wins, and has an obvious null: if selection carries no lexical
information the correct synonym sits at a uniformly random rank, median = n_anchors / 2.

SCORED WITH THE SUBSTRATE'S OWN SELECTION, NOT A SCORER I INVENTED. `canonicalize` computes
`np.sign(new_raw_sum)` against `space.bundle(anchor)` under `_cos`. This reproduces that exactly --
including the **sign-quantisation of the QUERY**, which is live even though the anchors stay graded
(reading_grounding_loop.py:776). Inventing a cleaner scorer here would measure a system we do not
run.

ARMS -- three, because "better than chance" is not a claim on its own:
  SUBSTRATE   rank of the best correct synonym under the substrate's own cosine
  FREQUENCY   rank of the same synonym when anchors are ordered by corpus frequency alone,
              **cue-blind** -- the floor that has beaten every arm in this project
  UNIFORM     a random rank, drawn per item -- the trivial floor

⚠️ APPROXIMATION, STATED BECAUSE IT MATTERS: anchors accumulate as reading proceeds, so the pool at
each word's ACTUAL grounding moment was smaller than the final pool used here. The store keeps no
per-moment snapshot. This makes every arm's task HARDER (a bigger pool to rank within) but it makes
it harder EQUALLY for all three, so the COMPARISON stands even though the absolute ranks are
pessimistic.

⚖️ WordNet identifies which anchors are true synonyms. It is a DIAGNOSTIC on the item set; it scores
nothing and appears in no arm.

PRE-COMMITTED READINGS:
  SUBSTRATE far better than UNIFORM and better than FREQUENCY -> selection DOES carry lexical
      meaning; it is losing on the last step, not blind. That makes this a tuning problem and names
      the target.
  SUBSTRATE better than UNIFORM but NOT better than FREQUENCY -> **what looks like meaning is the
      frequency backbone measured this morning.** Consistent with the confirmed frequency bias, and
      it would mean selection carries no lexical information BEYOND how common a word is.
  SUBSTRATE indistinguishable from UNIFORM -> selection has NO relationship to lexical meaning at
      all. The sharpest statement of the problem available, and it closes the tuning route.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from nltk.corpus import wordnet as wn  # noqa: E402

from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402
from hdlab.substrate import Substrate  # noqa: E402

SEEDS = (7, 101, 20260819)
CORPUS = os.environ.get("DIAG_CORPUS", "simplewiki")
N_READ = int(os.environ.get("DIAG_N_READ", "8000"))


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
    """cosine of q against every row of M -- the same quantity `_cos` computes, vectorised."""
    qn = np.linalg.norm(q)
    Mn = np.linalg.norm(M, axis=1)
    ok = Mn > 1e-12
    out = np.full(M.shape[0], -2.0)
    if qn > 1e-12:
        out[ok] = (M[ok] @ q) / (Mn[ok] * qn)
    return out


def _selftest_scorer():
    """The scorer must rank an IDENTICAL row first. Without this, 'ranks are at chance' could mean
    the scorer is broken rather than the substrate."""
    rng = np.random.default_rng(0)
    M = rng.normal(size=(50, 32))
    q = M[7].copy()
    r = _cos_rows(q, M)
    assert int(np.argmax(r)) == 7, "scorer does not rank an identical row first"
    print("selftest scorer: identical row ranks 1st", flush=True)


_selftest_scorer()

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
    pos = {a: i for i, a in enumerate(anchors)}

    # cue-blind frequency ordering over the SAME anchors
    freq = collections.Counter()
    for s in sub.state.sentence_pool:
        freq.update(content_lemmas(s))
    forder = np.argsort([-freq.get(a, 0) for a in anchors])
    frank = np.empty(len(anchors), dtype=np.int64)
    frank[forder] = np.arange(len(anchors))

    rng = np.random.default_rng(seed)
    sub_r, frq_r, uni_r = [], [], []
    sums = getattr(space, "_sums", {})
    for lemma in sorted(sums):
        syn = synonyms(lemma)
        present = [a for a in syn if a in pos and a != lemma]
        if not present:
            continue
        q = np.sign(np.asarray(sums[lemma], dtype=np.float64))   # THE LIVE PATH quantises the query
        c = _cos_rows(q, mat)
        if lemma in pos:
            c[pos[lemma]] = -2.0                                  # canonicalize excludes itself
        # rank of the BEST-PLACED correct synonym (1 = the substrate would have chosen it)
        best = min(int(np.sum(c > c[pos[a]])) + 1 for a in present)
        sub_r.append(best)
        frq_r.append(min(int(frank[pos[a]]) + 1 for a in present))
        uni_r.append(int(rng.integers(1, len(anchors) + 1)))

    if len(sub_r) < 30:
        print("seed %s: only %d scorable words -- skipped" % (seed, len(sub_r)), flush=True)
        continue
    rows.append({"seed": seed, "n_anchors": len(anchors), "SUBSTRATE": sub_r,
                 "FREQUENCY": frq_r, "UNIFORM": uni_r})
    print("seed %-9s anchors %4d | words with a synonym present %4d | median rank: "
          "SUBSTRATE %6.1f  FREQUENCY %6.1f  UNIFORM %6.1f"
          % (seed, len(anchors), len(sub_r), np.median(sub_r), np.median(frq_r), np.median(uni_r)),
          flush=True)

if len(rows) < 2:
    print("\nfewer than 2 usable seeds -- NO VERDICT")
    raise SystemExit(0)
with open(os.path.join(_REPO, "scratch", "synonym_rank.json"), "w", encoding="utf-8") as fh:
    json.dump(rows, fh, indent=1)

rng = np.random.default_rng(0)


def paired(a, b):
    d = np.concatenate([np.asarray(r[a], float) - np.asarray(r[b], float) for r in rows])
    bb = np.array([np.median(d[rng.integers(0, d.size, d.size)]) for _ in range(4000)])
    lo, hi = np.percentile(bb, [2.5, 97.5])
    sep = not (lo <= 0 <= hi)
    print("   %-24s %+8.1f  95%% CI [%+.1f, %+.1f]  %s"
          % ("%s - %s" % (a, b), np.median(d), lo, hi, "SEPARATED" if sep else "not separated"))
    return float(np.median(d)), sep


print("\n" + "=" * 78)
print("POOLED PAIRED (negative = the FIRST arm ranks the correct synonym BETTER):")
d_su, s_su = paired("SUBSTRATE", "UNIFORM")
d_sf, s_sf = paired("SUBSTRATE", "FREQUENCY")
d_fu, s_fu = paired("FREQUENCY", "UNIFORM")

print()
if not (s_su and d_su < 0):
    print("VERDICT: **SELECTION HAS NO RELATIONSHIP TO LEXICAL MEANING.** The correct synonym sits")
    print("at a chance rank among the anchors. This is the sharpest statement of the problem we")
    print("have: the failure is not that selection is mistuned, it is that the quantity being")
    print("maximised carries no information about what the word means. Tuning cannot reach it.")
elif s_sf and d_sf < 0:
    print("VERDICT: **SELECTION CARRIES REAL LEXICAL MEANING** -- better than chance AND better than")
    print("the cue-blind frequency floor. It is losing on the final step, not blind. That makes")
    print("this a tuning problem and names the target. VET before acting.")
else:
    print("VERDICT: **WHAT LOOKS LIKE MEANING IS THE FREQUENCY BACKBONE.** Better than chance but")
    print("NOT better than a cue-blind frequency ordering -- so selection carries no lexical")
    print("information BEYOND how common a word is. That is exactly consistent with the frequency")
    print("bias confirmed on two stores, and it says the hub is a frequency code end to end.")
