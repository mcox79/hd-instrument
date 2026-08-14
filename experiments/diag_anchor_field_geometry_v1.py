"""DIAGNOSTIC PROBE (geometry only, NO task accuracy -- accuracy is reserved for the
pre-registered cell so bands are not set after seeing the discriminator).

Question: what does the cascade of sign() binarizations do to the anchor field's geometry?
  context_vector: sign(sum of word random-index vectors)      <- binarization #1 (per sentence)
  ConceptSpace.anchor_matrix: sign(sum of sentence vectors)   <- binarization #2 (per concept)
  canonicalize_fast: cos(sign(query), sign(anchor))           <- binarization #3 (query)

Measures, on the SAME profile pool the landed cell used:
  (a) shared-component dominance: ||field mean|| / mean ||anchor||
  (b) participation ratio / top-PC variance share of the anchor field
  (c) mean pairwise anchor cosine (a floor on how separable ANY two concepts are)
under four transforms: SIGN (live), GRADED, GRADED+CENTER, GRADED+ZNORM (divisive normalisation).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import hashlib
import pickle
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from hdlab.grounding_acquisition_loop import content_words          # noqa: E402
from hdlab.reading_grounding_loop import CTX_D, normalize_lemma     # noqa: E402

CACHE = os.path.join(REPO, "data", "exp_context_conditioned_near_neighbour_v1_cache",
                     "corpus_assets_b12e14604e346f01.pkl")
N_PROFILE = 70
N_WORDS = 400

_WV = {}


def wv(w, d=CTX_D):
    v = _WV.get(w)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(w.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
        v = np.random.default_rng(seed).choice([-1.0, 1.0], size=d)
        _WV[w] = v
    return v


def ctx_graded(sentence, drop, d=CTX_D):
    """Raw graded sum -- hdlab.context_vector WITHOUT the terminal sign()."""
    words = [w for w in content_words(sentence) if normalize_lemma(w) not in drop]
    if not words:
        return np.zeros(d)
    acc = np.zeros(d)
    for w in words:
        acc += wv(w, d)
    return acc


def ctx_sign(sentence, drop, d=CTX_D):
    a = ctx_graded(sentence, drop, d)
    if not a.any():
        return np.zeros(d)
    o = np.sign(a)
    o[o == 0] = 1.0
    return o


def seed_for(key):
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 32)


def main():
    with open(CACHE, "rb") as f:
        a = pickle.load(f)
    buckets = a["buckets"]
    words = sorted(buckets)[:N_WORDS]
    print("words=%d (of %d)" % (len(words), len(buckets)))

    # BYTE-IDENTITY CHECK against hdlab's own context_vector (this probe must not fork it).
    from hdlab.grounding_acquisition_loop import context_vector
    for w in words[:5]:
        for s in buckets[w][:2]:
            assert np.array_equal(ctx_sign(s, set()), context_vector(s, d=CTX_D)), "FORKED"
    print("byte-identity vs hdlab.context_vector: OK")

    A_sign = np.zeros((len(words), CTX_D))
    A_grad = np.zeros((len(words), CTX_D))
    for i, w in enumerate(words):
        s = list(buckets[w])
        np.random.default_rng(seed_for("split|" + w)).shuffle(s)
        prof = s[:N_PROFILE]
        acc_s = np.zeros(CTX_D)
        acc_g = np.zeros(CTX_D)
        drop = {normalize_lemma(w)}
        for sent in prof:
            acc_s += ctx_sign(sent, drop)
            acc_g += ctx_graded(sent, drop)
        A_sign[i] = np.sign(acc_s)          # exactly ConceptSpace.anchor_matrix
        A_grad[i] = acc_g

    def report(name, M):
        norms = np.linalg.norm(M, axis=1)
        keep = norms > 1e-9
        M = M[keep]
        norms = norms[keep]
        U = M / norms[:, None]
        mu = M.mean(axis=0)
        shared = np.linalg.norm(mu) / norms.mean()
        C = U @ U.T
        iu = np.triu_indices(len(U), 1)
        pw = C[iu]
        ev = np.linalg.eigvalsh(np.cov(M.T))[::-1]
        ev = np.clip(ev, 0, None)
        pr = (ev.sum() ** 2) / max((ev ** 2).sum(), 1e-30)
        print("%-16s ||mean||/||anchor||=%.4f  top1_var=%.4f top5_var=%.4f  PR=%.1f  "
              "pairwise cos mean=%.4f sd=%.4f p99=%.4f"
              % (name, shared, ev[0] / ev.sum(), ev[:5].sum() / ev.sum(), pr,
                 pw.mean(), pw.std(), np.percentile(pw, 99)))

    report("SIGN(live)", A_sign)
    report("GRADED", A_grad)
    report("GRAD+CENTER", A_grad - A_grad.mean(axis=0))
    Z = (A_grad - A_grad.mean(axis=0)) / (A_grad.std(axis=0) + 1e-9)
    report("GRAD+ZNORM", Z)
    Zs = (A_sign - A_sign.mean(axis=0)) / (A_sign.std(axis=0) + 1e-9)
    report("SIGN+ZNORM", Zs)

    # how much magnitude information does sign() destroy at the anchor stage?
    acc_mag = np.abs(A_grad)
    print("\nanchor-sum |value| distribution (graded): p50=%.1f p90=%.1f max=%.1f  "
          "frac dims with |sum| < 0.1*p90 = %.4f"
          % (np.percentile(acc_mag, 50), np.percentile(acc_mag, 90), acc_mag.max(),
             float((acc_mag < 0.1 * np.percentile(acc_mag, 90)).mean())))


if __name__ == "__main__":
    main()
