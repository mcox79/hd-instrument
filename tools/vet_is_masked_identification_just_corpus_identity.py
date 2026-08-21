"""Is the masked arm's above-chance identification about the WORD, or about the SOURCE TEXT?

WHY THIS EXISTS. tools/vet_two_jobs_selfreference_share.py measured MASKED hit@1 = 0.0972 against a
chance of 0.0167 -- about 5.8x chance, on a corpus mix spanning Alice in Wonderland, ARC, Little
Women, McGuffey readers and more. A lemma's sentences are NOT drawn uniformly from that mix: a word
like "rabbit" comes overwhelmingly from one book. So a context vector could "identify the lemma"
purely by identifying the BOOK its sentences came from, which is topic/register similarity and not
word meaning at all.

THIS PROJECT HAS ALREADY BEEN BITTEN BY EXACTLY THIS. A foraging probe's headline was withdrawn on
2026-08-21 when the arms turned out to differ 7.6x in which register they read, under a 1.2x effect.
The rule that came out of it -- measure the baseline before the intervention, even when it obviously
must be zero -- is what this script does for my own number before anyone quotes it.

THE CONTROL: a predictor that knows ONLY which corpus each sentence came from, and nothing else.
It assigns every query to the lemma whose corpus-distribution is closest. If that scores near 0.0972,
the masked arm's signal is corpus identity wearing a lemma's name.

REPORTS, NEVER ASSERTS. The output is three numbers side by side; the reading is left to the reader.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import collections
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.reading_grounding_loop import (        # noqa: E402
    content_words, context_vector_masked, normalize_lemma,
)

N_LEMMAS = 60
N_SENT = 41
SEED = 7


def _tagged_sentences(limit: int = 60000) -> list[tuple[str, str]]:
    """(sentence, corpus_name) -- the tag is the whole point of this diagnostic."""
    from hdlab.corpus_registry import CorpusRegistry
    reg = CorpusRegistry()
    out: list[tuple[str, str]] = []
    for name in reg.readable_names():
        h = reg.handles.get(name)
        if h is None:
            continue
        try:
            pool = h.pool()
        except Exception as exc:
            print(f"  [{name}] pool() failed: {type(exc).__name__}: {exc}", flush=True)
            continue
        for s in pool:
            if 40 < len(s) < 400:
                out.append((s, name))
            if len(out) >= limit:
                return out
    return out


def main() -> int:
    # context_vector_masked takes `graded=None` = "follow the module switch", changed
    # 2026-08-14. A number produced under one switch state cannot be compared to one
    # produced under the other, so the state is PRINTED rather than remembered.
    import hdlab.reading_grounding_loop as _rgl
    print(f"CONFIG: GRADED_COMPARATOR={_rgl.GRADED_COMPARATOR}  CTX_D={_rgl.CTX_D}  "
          f"HD_GRADED_COMPARATOR={os.environ.get('HD_GRADED_COMPARATOR', '(unset)')}", flush=True)
    tagged = _tagged_sentences()
    print(f"corpus sentences: {len(tagged)}", flush=True)
    if len(tagged) < 5000:
        print("REFUSING: too few sentences -- not the population the number came from.")
        return 2

    by_lemma: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for s, src in tagged:
        for w in set(content_words(s)):
            lem = normalize_lemma(w)
            if len(lem) > 2 and len(by_lemma[lem]) < N_SENT:
                by_lemma[lem].append((s, src))

    eligible = sorted(k for k, v in by_lemma.items() if len(v) >= N_SENT)
    if len(eligible) < N_LEMMAS:
        print("REFUSING: fewer than 60 eligible lemmas.")
        return 2
    def _max_share(lem: str) -> float:
        srcs = [src for _s, src in by_lemma[lem][:N_SENT]]
        return collections.Counter(srcs).most_common(1)[0][1] / len(srcs)

    balanced = "--balanced" in sys.argv
    if balanced:
        # THE RE-RUN THE FIRST PASS ASKED FOR. Selecting the most source-SPREAD lemmas shrinks the
        # confound at the source instead of trying to subtract it afterwards: if a lemma's sentences
        # come from many books, "which book" stops being an answer to "which word".
        # This is a BIASED SAMPLE BY CONSTRUCTION and says so -- it is the subset of vocabulary that
        # appears across many registers, which is not the average word. It answers "is there word
        # signal once the confound is removed", NOT "how well does the arm do on our vocabulary".
        ranked = sorted(eligible, key=_max_share)
        lemmas = sorted(ranked[:N_LEMMAS])
        print("MODE: --balanced (lemmas chosen for the WIDEST spread across source texts)")
    else:
        rng = np.random.default_rng(SEED)
        lemmas = sorted(rng.choice(eligible, size=N_LEMMAS, replace=False).tolist())
        print("MODE: random lemma sample (pass --balanced for the confound-reduced re-run)")

    # -- HOW CONCENTRATED IS EACH LEMMA IN ONE SOURCE? The confound's own size. ------------
    shares = []
    for l in lemmas:
        srcs = [src for _s, src in by_lemma[l][:N_SENT]]
        top = collections.Counter(srcs).most_common(1)[0][1]
        shares.append(top / len(srcs))
    shares_arr = np.array(shares)
    print(f"\nlargest-single-corpus share per lemma: "
          f"median {np.median(shares_arr):.3f}  mean {shares_arr.mean():.3f}  "
          f"min {shares_arr.min():.3f}  max {shares_arr.max():.3f}")
    print(f"lemmas drawn >=90% from ONE corpus: {(shares_arr >= 0.9).sum()} of {len(lemmas)}")

    sources = sorted({src for l in lemmas for _s, src in by_lemma[l][:N_SENT]})
    sidx = {s: i for i, s in enumerate(sources)}
    print(f"distinct source corpora in play: {len(sources)}")

    # -- ARM 1: the real masked arm. ------------------------------------------------------
    # -- ARM 2: CORPUS-ONLY. A one-hot of the source, nothing else. ------------------------
    def corpus_vec(src: str) -> np.ndarray:
        v = np.zeros(len(sources), dtype=float)
        v[sidx[src]] = 1.0
        return v

    def score(vec_of, per_lemma=None) -> float:
        vecs = {l: [vec_of(s, src, l) for s, src in by_lemma[l][:N_SENT]] for l in lemmas}
        sums = {l: np.sum(vecs[l], axis=0) for l in lemmas}
        hit = tot = 0
        for l in lemmas:
            for q in vecs[l]:
                qn = np.linalg.norm(q)
                if qn == 0:
                    continue
                best, best_c = None, -2.0
                for m in lemmas:
                    prof = sums[m] - (q if m == l else 0)
                    pn = np.linalg.norm(prof)
                    if pn == 0:
                        continue
                    c = float(np.dot(q, prof) / (qn * pn))
                    if c > best_c:
                        best_c, best = c, m
                tot += 1
                ok = int(best == l)
                hit += ok
                if per_lemma is not None:
                    per_lemma.setdefault(l, []).append(ok)
        return hit / max(1, tot)

    pm: dict = {}
    pc: dict = {}
    masked = score(lambda s, src, l: context_vector_masked(s, l), pm)
    corpus_only = score(lambda s, src, l: corpus_vec(src), pc)

    # SCRAMBLE FLOOR, and it doubles as a POSITIVE CONTROL ON THE HARNESS ITSELF. Each query keeps a
    # real masked context vector but is scored against a lemma pool whose membership is shuffled, so
    # the word-to-context correspondence is destroyed while every other property -- vector
    # dimensionality, profile sizes, tie structure, the leave-one-out subtraction -- is untouched.
    # It MUST land at chance. If it does not, the scorer is finding structure that is not there and
    # no number above means anything. An arm that cannot produce a null cannot produce a result.
    rs = np.random.default_rng(23)
    real = {l: [context_vector_masked(s, l) for s, _src in by_lemma[l][:N_SENT]] for l in lemmas}
    flat = [(l, v) for l in lemmas for v in real[l]]
    perm = rs.permutation(len(flat))
    shuffled: dict = {l: [] for l in lemmas}
    for i, (lem, _v) in enumerate(flat):
        shuffled[lem].append(flat[perm[i]][1])
    ssums = {l: np.sum(shuffled[l], axis=0) for l in lemmas}
    shit = stot = 0
    for l in lemmas:
        for q in shuffled[l]:
            qn = np.linalg.norm(q)
            if qn == 0:
                continue
            best, best_c = None, -2.0
            for m in lemmas:
                prof = ssums[m] - (q if m == l else 0)
                pn = np.linalg.norm(prof)
                if pn == 0:
                    continue
                c = float(np.dot(q, prof) / (qn * pn))
                if c > best_c:
                    best_c, best = c, m
            stot += 1
            shit += int(best == l)
    scramble = shit / max(1, stot)
    print(f"SCRAMBLE floor (word-to-context correspondence destroyed): {scramble:.4f} "
          f"[must be ~chance {1.0 / N_LEMMAS:.4f}]")

    # PAIRED DIFFERENCE WITH A CI, BOOTSTRAPPED OVER LEMMAS -- the clustering unit. Queries inside
    # one lemma share its sentences and its source mix, so resampling QUERIES would understate the
    # width badly. The measurement bar requires a half-width beside every margin.
    keys = sorted(set(pm) & set(pc))
    per_lemma_diff = np.array([np.mean(pm[k]) - np.mean(pc[k]) for k in keys])
    rb = np.random.default_rng(11)
    boot = np.array([per_lemma_diff[rb.integers(0, len(per_lemma_diff), len(per_lemma_diff))].mean()
                     for _ in range(4000)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print("")
    print(f"MASKED - CORPUS_ONLY, per-lemma paired: {per_lemma_diff.mean():+.4f}  "
          f"95% CI [{lo:+.4f}, {hi:+.4f}]  (bootstrap over {len(keys)} lemmas, half-width "
          f"{(hi - lo) / 2:.4f})")
    print(f"  lemmas where masked beats corpus-only: "
          f"{int((per_lemma_diff > 0).sum())} of {len(per_lemma_diff)}")
    print(f"  CI EXCLUDES ZERO: {bool(lo > 0 or hi < 0)}")

    print(f"\nchance                    {1.0 / N_LEMMAS:.4f}")
    print(f"CORPUS-ONLY (knows only the source text)   {corpus_only:.4f}")
    print(f"MASKED      (the real arm)                 {masked:.4f}")
    # THE VERDICT IS GATED ON THE CI, NOT ON THE POINT DIFFERENCE.
    # The first version of this block read `masked > corpus_only` and printed "so it carries
    # something the source tag does not". Its own bootstrap, printed four lines above, says
    # [-0.0419, +0.0764] -- a half-width nearly three times the effect. Reading a point estimate as
    # a finding while the interval spans zero is the exact error the measurement bar's "a width is
    # not an effect" rule exists to stop, and I shipped it in the tool written to enforce that rule.
    print("")
    separated = lo > 0 or hi < 0
    if not separated:
        print("=> NOT SEPARATED FROM SOURCE-TEXT IDENTITY.")
        print(f"   The masked arm leads corpus-identity by {masked - corpus_only:+.4f}, but the")
        print(f"   95% CI is [{lo:+.4f}, {hi:+.4f}] and spans zero, so this run cannot tell the two")
        print("   apart. 0.0972 vs chance 0.0167 must NOT be quoted as word-specific signal:")
        print(f"   a predictor knowing ONLY the source text already reaches {corpus_only:.4f}.")
    elif corpus_only >= masked:
        print("=> KNOWING ONLY WHICH BOOK THE SENTENCE CAME FROM MATCHES OR BEATS THE REAL ARM.")
        print("   The masked arm's above-chance score is not evidence about word meaning.")
    else:
        print(f"=> the masked arm beats corpus-identity by {masked - corpus_only:+.4f} with a CI "
              f"excluding zero, so it carries something the source tag does not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
