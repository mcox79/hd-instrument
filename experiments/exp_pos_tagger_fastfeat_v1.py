"""BYTE-IDENTICAL speed optimization for the POS tagger's per-call Viterbi + feature assembly.

Problem: optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost.
The profile (exp_pos_tagger_profile_v1) shows ~70% of the tag cost is EMISSION-MATRIX construction:
`pos_features` is called n_tok * n_tags times (per token, PER TAG), each rebuilding ~22 feature
strings, then `sum(weights.get(f, 0.0) for f in feats)`. But EVERY emission feature is `<base>~<tag>`
where <base> is TAG-INDEPENDENT -- so the base set is computed n_tags-times redundantly, and the
`base + "~" + tag` string is rebuilt every time. The transition matrix (TM) + start vector (SV) are
also rebuilt per sentence though they are CONSTANT given the model.

Mechanism (output-preserving), reusing P8's parser pattern adapted to the DICT weight structure:
  (1) PRECOMPUTE TM (n_tags x n_tags) and SV (n_tags) ONCE from the model (constant). Byte-identical.
  (2) SPLIT the weights dict ONCE into per-tag emission dicts Wtag[k]: base -> weight
      (rsplit('~',1); tt: keys are transitions). Byte-identical: Wtag[k].get(base,0.0) ==
      weights.get(base+'~'+tag_k, 0.0) exactly.
  (3) Build each token's tag-INDEPENDENT base list ONCE (in the EXACT order pos_features emits),
      then score emissions. Two BYTE-IDENTICAL variants:
        A. per-tag dict.get:  em[i,k] = sum(Wtag[k].get(b,0.0) for b in bases_i)
        C. sparse per-lane:   collect the PRESENT weights per lane in base order, em[i,k]=sum(perlane[k])
           -- skips the (default-0.0) missing gets. Byte-identical because adding 0.0 is a no-op in the
           Neumaier compensated sum CPython 3.12 uses, so sum(present-in-base-order)==sum(full).
      >> KEY REALIZATION: an earlier variant B used a plain `row[k] += w` loop and gave byte-identical
         TAGS but a ~1e-15-different emission matrix -- because CPython 3.12's built-in sum() is
         COMPENSATED (Neumaier), not left-to-right. Byte-identity therefore REQUIRES routing the final
         reduction through the same sum() the stock path uses; A and C do, plain-loop B does not. <<
  (4) DP (Viterbi V/bp + backtrace) is the STOCK numpy code verbatim, fed the fast em + precomputed
      TM/SV -> identical V, bp, argmax tie-breaking (np.argmax = first-max) -> identical tags.

The tagging MODEL, feature TEMPLATE, and Viterbi decode are UNCHANGED (PINNED, brain-foundational --
Kuperberg-Jaeger 2016 graded cue-based category assignment). Only the OUR-INVENTION implementation of
sparse feature scoring changes. NO LLM, numpy + pure-python, no new dependency. ASCII-only.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import time
import json

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
import experiments.exp_pos_tagger_profile_v1 as P

_POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_OUT = os.path.join(_REPO, "data/exp_pos_tagger_fastfeat_v1")


# ------------------------------------------------------------------ base builder
def token_bases(obs, i):
    """The TAG-INDEPENDENT part of pos_features(obs,i,tag), in the EXACT emit order (drop the ~tag).

    Mirrors hdlab.pos_tagger.pos_features line-for-line: b, w:, (suf/pre 1..4), cap, hasdig, hyph,
    pw:/BOS, nw:/EOS. Preserving order => identical feature strings when re-suffixed with ~tag =>
    identical dict values in identical sum order => byte-identical emission scores.
    """
    w = obs[i]
    wl = w.lower()
    bases = ["b", "w:" + wl]
    L = len(wl)
    for k in (1, 2, 3, 4):
        if L >= k:
            bases.append("suf%d:%s" % (k, wl[-k:]))
            bases.append("pre%d:%s" % (k, wl[:k]))
    if w[:1].isupper():
        bases.append("cap")
    if any(c.isdigit() for c in w):
        bases.append("hasdig")
    if "-" in w:
        bases.append("hyph")
    if i > 0:
        bases.append("pw:" + obs[i - 1].lower())
    else:
        bases.append("BOS")
    if i + 1 < len(obs):
        bases.append("nw:" + obs[i + 1].lower())
    else:
        bases.append("EOS")
    return bases


class FastTagger:
    """Byte-identical fast wrapper over a loaded PosTagger. Two emission variants (A=per-tag dict,
    B=sparse accumulate); DP is the stock numpy Viterbi verbatim."""

    def __init__(self, tagger, variant="B"):
        self.tags = list(tagger.tags)
        self.n_tags = len(self.tags)
        self.tag_index = {t: i for i, t in enumerate(self.tags)}
        self.variant = variant
        W = tagger._perc.weights
        # (2) per-tag emission dicts  +  base_contrib for sparse accumulation
        self.Wtag = [dict() for _ in range(self.n_tags)]
        self.base_contrib = {}                       # base -> list[(tag_idx, weight)]
        ti = self.tag_index
        for key, val in W.items():
            if key.startswith("tt:"):
                continue
            base, tag = key.rsplit("~", 1)
            k = ti[tag]
            self.Wtag[k][base] = val
            self.base_contrib.setdefault(base, []).append((k, val))
        # (1) precompute TM / SV once (constant given the model)
        self.TM = np.array([[W.get("tt:" + self.tags[j] + "~" + self.tags[k], 0.0)
                             for k in range(self.n_tags)] for j in range(self.n_tags)])
        self.SV = np.array([W.get("tt:<S>~" + self.tags[k], 0.0) for k in range(self.n_tags)])

    # (3) emission matrix -- two byte-identical variants
    def _em_A(self, obs, n):
        nt = self.n_tags
        Wt = self.Wtag
        em = np.empty((n, nt))
        for i in range(n):
            b = token_bases(obs, i)
            row = em[i]
            for k in range(nt):
                g = Wt[k].get
                row[k] = sum(g(x, 0.0) for x in b)
        return em

    def _em_C(self, obs, n):
        """Sparse per-lane: collect present weights per lane IN BASE ORDER, then sum() each (compensated,
        matching stock). Byte-identical: dropping the 0.0-default terms is a no-op in Neumaier sum.
        The per-lane lists are allocated ONCE per sentence and cleared per token (reuse avoids realloc)."""
        nt = self.n_tags
        bc = self.base_contrib
        perlane = [[] for _ in range(nt)]
        em = np.empty((n, nt))
        for i in range(n):
            for lst in perlane:
                lst.clear()
            for base in token_bases(obs, i):
                c = bc.get(base)
                if c is not None:
                    for k, w in c:
                        perlane[k].append(w)
            row = em[i]
            for k in range(nt):
                row[k] = sum(perlane[k])   # sum([]) == 0 -> +0.0, matching stock's all-0.0 lane
        return em

    def _emission(self, obs, n):
        return self._em_C(obs, n) if self.variant == "C" else self._em_A(obs, n)

    # (4) DP: verbatim stock numpy Viterbi with precomputed TM/SV
    def tag(self, tokens):
        obs = list(tokens)
        n = len(obs)
        if n == 0:
            return []
        em = self._emission(obs, n)
        TM, SV = self.TM, self.SV
        nt = self.n_tags
        V = np.empty((n, nt))
        bp = np.zeros((n, nt), dtype=int)
        V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM
            bp[i] = np.argmax(cand, axis=0)
            V[i] = cand[bp[i], np.arange(nt)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1):
            seq.append(int(bp[i][seq[-1]]))
        seq.reverse()
        return [self.tags[k] for k in seq]


def _stock_em(tagger, obs):
    """The stock emission matrix, exactly as hdlab.perceptron._viterbi builds it (for em-equality)."""
    from hdlab.pos_tagger import pos_features
    W = tagger._perc.weights
    tags = tagger.tags
    n = len(obs)
    return np.array([[sum(W.get(f, 0.0) for f in pos_features(obs, i, tags[k]))
                      for k in range(len(tags))] for i in range(n)])


def identity_check(tagger, fast, sents):
    """Return (tag_mismatch_sents, em_mismatch_sents, n_tok, n_tag_tok_wrong)."""
    tag_mis = em_mis = tok_wrong = ntok = 0
    for toks in sents:
        g = tagger.tag(toks)
        f = fast.tag(toks)
        ntok += len(toks)
        if g != f:
            tag_mis += 1
            tok_wrong += sum(1 for a, b in zip(g, f) if a != b)
        if not np.array_equal(_stock_em(tagger, toks), fast._emission(list(toks), len(toks))):
            em_mis += 1
    return tag_mis, em_mis, ntok, tok_wrong


def time_it(fn, sents, reps):
    fn(sents[0])
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for toks in sents:
            fn(toks)
        ts.append(time.perf_counter() - t0)
    ts.sort()
    return ts[len(ts) // 2]


def main(n=250, reps=7):
    os.makedirs(_OUT, exist_ok=True)
    tagger = PosTagger.load(_POS_ASSET)
    sents = P.load_sentences(n)
    ntok = sum(len(t) for t in sents)
    fastA = FastTagger(tagger, "A")
    fastC = FastTagger(tagger, "C")

    tmA, emA, _, twA = identity_check(tagger, fastA, sents)
    tmC, emC, _, twC = identity_check(tagger, fastC, sents)
    print("BYTE-IDENTITY (n=%d sents, %d tok):" % (len(sents), ntok), flush=True)
    print("  variant A (per-tag full-sum): tag-mismatch sents=%d  em-mismatch sents=%d  tok-wrong=%d"
          % (tmA, emA, twA), flush=True)
    print("  variant C (sparse per-lane) : tag-mismatch sents=%d  em-mismatch sents=%d  tok-wrong=%d"
          % (tmC, emC, twC), flush=True)

    # interleaved median timing (fair on a noisy shared box)
    t_stock = time_it(tagger.tag, sents, reps)
    t_A = time_it(fastA.tag, sents, reps)
    t_C = time_it(fastC.tag, sents, reps)
    print("\nWARM tag (median of %d, %d sents / %d tok):" % (reps, len(sents), ntok), flush=True)
    print("  STOCK   : %.3fs  (%.0f tok/s)" % (t_stock, ntok / t_stock), flush=True)
    print("  FAST A  : %.3fs  (%.0f tok/s)  speedup %.2fx" % (t_A, ntok / t_A, t_stock / t_A), flush=True)
    print("  FAST C  : %.3fs  (%.0f tok/s)  speedup %.2fx" % (t_C, ntok / t_C, t_stock / t_C), flush=True)

    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"n_sents": len(sents), "n_tok": ntok, "reps": reps,
                   "byte_identity": {"A": {"tag_mismatch": tmA, "em_mismatch": emA, "tok_wrong": twA},
                                     "C": {"tag_mismatch": tmC, "em_mismatch": emC, "tok_wrong": twC}},
                   "stock_s": t_stock, "fastA_s": t_A, "fastC_s": t_C,
                   "speedup_A": t_stock / t_A, "speedup_C": t_stock / t_C}, f, indent=2)
    print("wrote metrics.json", flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=250)
    ap.add_argument("--reps", type=int, default=7)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        tg = PosTagger.load(_POS_ASSET)
        ss = P.load_sentences(12)
        for var in ("A", "C"):
            ft = FastTagger(tg, var)
            tm, em, _, tw = identity_check(tg, ft, ss)
            assert tm == 0 and em == 0 and tw == 0, ("mismatch", var, tm, em, tw)
        print("SELF-TEST PASS: fast tagger A+C byte-identical (tags + emission matrix) on 12 sents")
    else:
        main(a.n, a.reps)
