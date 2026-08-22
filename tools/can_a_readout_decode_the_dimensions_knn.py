"""THE STRONGER TEST: can a NEIGHBOUR READ-OUT decode each norm dimension from the text space?

WHY THIS EXISTS, AND WHY IT RUNS BEFORE ANY WRITE-UP. The pairwise companion script
(which_norm_dimensions_can_text_recover.py) found near-zero alignment between text similarity and
similarity along each norm dimension. THAT TEST CAN ONLY SEE A MONOTONE PAIRWISE RELATION. A
dimension encoded in a SUBSPACE, or non-monotonically, reads zero there while being perfectly
decodable. Publishing that as "text does not carry this" would be exactly the narrow-implementation-
failure-generalised-to-impossible trap this project has already been caught by.

THE READ-OUT, which is the standard way to ask "is attribute A decodable from space S":
  for each word w:  predict z_d(w) = mean of z_d over w's K nearest neighbours in the text space,
                    with w ITSELF EXCLUDED (leave-one-out -- otherwise the answer is in the query)
  score = Spearman(predicted, actual) across words
This is strictly more powerful than pairwise alignment: it pools K neighbours, so it survives a
dimension being carried by a neighbourhood rather than by every pair.

NULL: shuffle the word->value map and re-run the SAME read-out. Recomputed per dimension.
POSITIVE CONTROL: concreteness, again. If it does not decode here it does not decode anywhere and
nothing else on the table may be read.
LEAK CHECK PRINTED: the self-exclusion is asserted, and the count of neighbours actually used is
printed -- a read-out that silently included the word itself would score near 1.0 and look like a
triumph, which is the empty-representation failure in a new costume.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import csv
import math
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.reading_grounding_loop import (        # noqa: E402
    CTX_D, content_words, context_vector_masked, normalize_lemma,
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from which_norm_dimensions_can_text_recover import (   # noqa: E402
    AFFECT, CONTROL, MAX_VOCAB, N_SENT, SEED, SENSORIMOTOR, _load_norms, _pearson, _rank,
    _sentences,
)

K = 25


def main() -> int:
    print("reading the shelf ...", flush=True)
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
        pre = len(vocab)
        vocab = sorted(np.random.default_rng(SEED).choice(vocab, size=MAX_VOCAB,
                                                          replace=False).tolist())
        print(f"VOCAB {MAX_VOCAB} (dropped {pre - MAX_VOCAB}; same seed as the pairwise run)",
              flush=True)
    n = len(vocab)

    print("building OURS profiles ...", flush=True)
    ours = np.zeros((n, CTX_D), dtype=np.float64)
    for i, lem in enumerate(vocab):
        acc = np.zeros(CTX_D, dtype=np.float64)
        for s in by_lemma[lem][:N_SENT]:
            acc += context_vector_masked(s, lem)
        ours[i] = acc

    print("building IDF profiles ...", flush=True)
    ctx_index: dict[str, int] = {}
    rows: list[collections.Counter] = []
    for lem in vocab:
        c: collections.Counter = collections.Counter()
        for s in by_lemma[lem][:N_SENT]:
            for w in content_words(s):
                cw = normalize_lemma(w)
                if cw == lem:
                    continue
                if cw not in ctx_index:
                    ctx_index[cw] = len(ctx_index)
                c[ctx_index[cw]] += 1
        rows.append(c)
    df = np.zeros(len(ctx_index), dtype=np.float64)
    for c in rows:
        for k in c:
            df[k] += 1
    idfw = np.log(n / np.maximum(df, 1.0))
    idf = np.zeros((n, len(ctx_index)), dtype=np.float32)
    for i, c in enumerate(rows):
        for k, v in c.items():
            idf[i, k] = v * idfw[k]

    def unit(m):
        return m / np.maximum(np.linalg.norm(m, axis=1, keepdims=True), 1e-12)

    arms = {"OURS": unit(ours).astype(np.float32), "IDF": unit(idf)}

    neigh = {}
    for name, M in arms.items():
        S = M @ M.T
        np.fill_diagonal(S, -np.inf)          # LEAVE-ONE-OUT, enforced not assumed
        nb = np.argpartition(-S, K, axis=1)[:, :K]
        assert not (nb == np.arange(n)[:, None]).any(), f"{name}: SELF LEAKED INTO ITS OWN NEIGHBOURS"
        neigh[name] = nb
        print(f"  {name}: {K} neighbours/word, self-exclusion asserted, "
              f"mean top-1 cos {float(np.max(np.where(np.isfinite(S), S, -1), axis=1).mean()):.4f}",
              flush=True)
        del S

    rng = np.random.default_rng(SEED)
    dims = CONTROL + SENSORIMOTOR + AFFECT
    print()
    print(f"{'dimension':<16}{'OURS':>9}{'null95':>9}{'IDF':>9}{'null95':>9}  group")
    print("-" * 62)
    out = []
    for dim in dims:
        z = np.array([normed[l][dim] for l in vocab], dtype=np.float64)
        z = (z - z.mean()) / (z.std() + 1e-12)
        rz = _rank(z)
        res = {}
        for name, nb in neigh.items():
            pred = z[nb].mean(axis=1)
            res[name] = _pearson(_rank(pred), rz)
            nulls = []
            for _ in range(100):
                zs = z[rng.permutation(n)]
                nulls.append(abs(_pearson(_rank(zs[nb].mean(axis=1)), _rank(zs))))
            res[name + "_null"] = float(np.percentile(nulls, 95))
        grp = "AFFECT" if dim in AFFECT else ("**CONTROL**" if dim in CONTROL else "sensorimotor")
        print(f"{dim:<16}{res['OURS']:>9.4f}{res['OURS_null']:>9.4f}"
              f"{res['IDF']:>9.4f}{res['IDF_null']:>9.4f}  {grp}")
        out.append((dim, res["OURS"], res["OURS_null"], res["IDF"], res["IDF_null"], grp))

    print()
    for label, ai, ni in (("OURS", 1, 2), ("IDF", 3, 4)):
        aff = [r[ai] for r in out if r[5] == "AFFECT"]
        sen = [r[ai] for r in out if r[5] == "sensorimotor"]
        cl = [r[0] for r in out if r[ai] > r[ni]]
        print(f"{label}: mean AFFECT {np.mean(aff):+.4f} | mean sensorimotor {np.mean(sen):+.4f} "
              f"| clears null: {len(cl)}/{len(out)}")
        print(f"      clearing: {cl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
