"""HOW FEW LABELLED WORDS DOES PROPAGATION NEED? -- the seed-size sweep.

WHY THIS EXISTS. The neighbour read-out (can_a_readout_decode_the_dimensions_knn.py) decodes all 15
norm dimensions from reading-derived neighbourhoods, but it uses the TRUE values of 25 neighbours.
That shows the space is ORGANISED, not that we can produce a value unaided. THE QUESTION THAT TURNS
IT INTO AN ARCHITECTURE IS: how many words must be labelled before the rest come free?

IT ALSO CONNECTS TO WORK ALREADY ON DISK (read before building, per the standing rule):
  notes/A_REAL_DISTANCE_TO_FRONTIER_IS_COMPUTABLE_...  -- a graded "is this word within reach"
      measure exists, built from whether a word's COMPANY is already understood. It passed three
      kill-tests and needed a >=30-neighbour floor to stop tiny neighbourhoods scoring a perfect 1.0.
  notes/THE_GAP_SIGNAL_IS_MEMBERSHIP_NOT_DISTANCE_...  -- the organ we HAVE answers yes/no, and
      agrees with a plain membership test 98.75% of the time.
  notes/SYNTHESIS_the_hop_distance_body_of_work_...    -- the 11x lift came from MORE KINDS OF STEP,
      not more steps; and a separate arm found a real wall that is not a data-density problem.
⚠️ THOSE USE CO-OCCURRENCE NEIGHBOURS ("words appearing alongside it"). THIS USES PROFILE-SIMILARITY
NEIGHBOURS (words used in similar contexts -- second order). DIFFERENT NEIGHBOURHOODS, DO NOT CONFLATE.

DESIGN, and the one thing that makes seed sizes comparable:
  THE HELD-OUT SET IS FIXED (1,000 words) AND IDENTICAL AT EVERY SEED SIZE. Seeds are drawn from the
  disjoint remainder. If the evaluation population moved with the seed size the curve would be
  uninterpretable -- that is the "queries grew with the depth" error already made once tonight.
  DRAWS: 5 independent seed draws per size, because a single draw is a single-seed result.
  NULL: shuffle the seed words' labels; recomputed per (size, dimension, arm).

REPORTED ALONGSIDE, because it is the owner's own question in this space: MEAN SIMILARITY TO THE
NEAREST SEED -- the graded distance to the grounded frontier, in the reading-derived space.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hdlab.reading_grounding_loop import (        # noqa: E402
    CTX_D, content_words, context_vector_masked, normalize_lemma,
)
from which_norm_dimensions_can_text_recover import (   # noqa: E402
    AFFECT, CONTROL, MAX_VOCAB, N_SENT, SEED, SENSORIMOTOR, _load_norms, _pearson, _rank,
    _sentences,
)

N_HELDOUT = 1000
SIZES = [25, 50, 100, 200, 400, 800, 1600, 2000]
N_DRAWS = 5
N_NULL = 30
KMAX = 25


def main() -> int:
    sents = _sentences()
    print(f"corpus sentences: {len(sents)}", flush=True)
    norms = _load_norms()
    need = set(SENSORIMOTOR) | set(AFFECT) | set(CONTROL)
    normed = {w: v for w, v in norms.items() if need <= set(v)}

    by_lemma: dict[str, list[str]] = collections.defaultdict(list)
    for s in sents:
        for w in set(content_words(s)):
            lem = normalize_lemma(w)
            if len(lem) > 2 and len(by_lemma[lem]) < N_SENT:
                by_lemma[lem].append(s)

    vocab = sorted(l for l, ss in by_lemma.items() if len(ss) >= N_SENT and l in normed)
    if len(vocab) > MAX_VOCAB:
        vocab = sorted(np.random.default_rng(SEED).choice(vocab, size=MAX_VOCAB,
                                                          replace=False).tolist())
    n = len(vocab)
    print(f"vocab {n}", flush=True)

    print("building profiles ...", flush=True)
    ours = np.zeros((n, CTX_D), dtype=np.float64)
    for i, lem in enumerate(vocab):
        acc = np.zeros(CTX_D, dtype=np.float64)
        for s in by_lemma[lem][:N_SENT]:
            acc += context_vector_masked(s, lem)
        ours[i] = acc

    ctx_index: dict[str, int] = {}
    rows: list[collections.Counter] = []
    for lem in vocab:
        c: collections.Counter = collections.Counter()
        for s in by_lemma[lem][:N_SENT]:
            for w in content_words(s):
                cw = normalize_lemma(w)
                if cw != lem:
                    c[ctx_index.setdefault(cw, len(ctx_index))] += 1
        rows.append(c)
    df = np.zeros(len(ctx_index))
    for c in rows:
        for k in c:
            df[k] += 1
    idfw = np.log(n / np.maximum(df, 1.0))
    idf = np.zeros((n, len(ctx_index)), dtype=np.float32)
    for i, c in enumerate(rows):
        for k, v in c.items():
            idf[i, k] = v * idfw[k]

    def unit(m):
        return (m / np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-12)).astype(np.float32)

    arms = {"OURS": unit(ours), "IDF": unit(idf)}

    rng = np.random.default_rng(SEED)
    perm = rng.permutation(n)
    held, pool = perm[:N_HELDOUT], perm[N_HELDOUT:]
    assert not (set(held.tolist()) & set(pool.tolist())), "HELD-OUT AND POOL OVERLAP"
    print(f"held-out {len(held)} FIXED at every seed size; pool {len(pool)}", flush=True)

    dims = CONTROL + ["Valence"]
    allz = {d: None for d in (CONTROL + SENSORIMOTOR + AFFECT)}
    for d in allz:
        z = np.array([normed[l][d] for l in vocab], dtype=np.float64)
        allz[d] = (z - z.mean()) / (z.std() + 1e-12)

    print()
    hdr = f"{'arm':<6}{'seeds':>7}{'nearest':>9}" + "".join(f"{d[:11]:>12}" for d in dims) + f"{'MEAN15':>9}{'null95':>9}"
    print(hdr)
    print("-" * len(hdr))
    for arm, M in arms.items():
        for size in SIZES:
            if size > len(pool):
                continue
            k = min(KMAX, size)
            per_dim = collections.defaultdict(list)
            mean15, nulls, nearest = [], [], []
            for draw in range(N_DRAWS):
                seeds = np.random.default_rng(1000 + draw).choice(pool, size=size, replace=False)
                S = M[held] @ M[seeds].T                     # held-out x seeds only
                nb = np.argpartition(-S, k - 1, axis=1)[:, :k] if k < size else np.tile(
                    np.arange(size), (len(held), 1))
                nearest.append(float(S.max(axis=1).mean()))
                ds = []
                for d in allz:
                    zs = allz[d][seeds]
                    pred = zs[nb].mean(axis=1)
                    r = _pearson(_rank(pred), _rank(allz[d][held]))
                    ds.append(r)
                    if d in dims:
                        per_dim[d].append(r)
                mean15.append(float(np.mean(ds)))
                nl = []
                for _ in range(N_NULL):
                    zs = allz["Concreteness"][seeds][np.random.default_rng(
                        7 * draw + _ + 1).permutation(size)]
                    nl.append(abs(_pearson(_rank(zs[nb].mean(axis=1)),
                                           _rank(allz["Concreteness"][held]))))
                nulls.append(float(np.percentile(nl, 95)))
            cells = "".join(f"{np.mean(per_dim[d]):>12.4f}" for d in dims)
            print(f"{arm:<6}{size:>7}{np.mean(nearest):>9.4f}{cells}"
                  f"{np.mean(mean15):>9.4f}{np.mean(nulls):>9.4f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
