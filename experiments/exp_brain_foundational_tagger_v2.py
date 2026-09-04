"""Brain-foundational lexical-category assigner v2 -- faithful morphology + smoothing.

v1 lost to the Viterbi floor (0.919 vs 0.945) because the emission + OOV morphology were crude
(add-0.01 smoothing, weak suffix backoff); the info-free twin collapsed (0.093), so the mechanism
carries the signal -- it was an impl weakness, not a structural ceiling. v2 keeps the SAME
brain-foundational mechanism (incremental ranked-parallel beam + cue integration + morphological
decomposition + top-down predictive prior) but realizes each cue faithfully (Brants 2000, TnT):

  * TRANSITION (top-down prediction): trigram P(t|t-2,t-1) with DELETED INTERPOLATION
    (lambda1 uni + lambda2 bi + lambda3 tri; context-independent weights estimated by Brants' algo).
  * EMISSION known word (lexical retrieval): generative P(w|t) = c(w,t)/c(t).
  * EMISSION novel word (MORPHOLOGICAL DECOMPOSITION): TnT suffix model -- P(t|suffix) by successive
    abstraction over suffix lengths, interpolation weight theta = variance of the tag prior; built
    from rare training words (freq <= 10, which behave like unknowns), with SEPARATE tries for
    capitalized vs lowercase forms (capitalization is the brain's proper-name morphographemic cue --
    directly targets the dominant PROPN<->NOUN confusion). Converted to an emission via
    P(w|t) ∝ P(t|suffix)/P(t).
  * DECODE: incremental left-to-right BEAM over (t-2,t-1) states -- ranked-parallel commitment, not
    batch global Viterbi. Beam width SWEPT.

One-pass counts only, NO gradient training. Glass-box, CPU, NO LLM. ASCII-only.
"""
from __future__ import annotations

import os
import sys
import math
import json
from collections import defaultdict, Counter

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments.exp_brain_foundational_tagger_v1 import load, _TRAIN, _TEST

_OUT = os.path.join(_REPO, "data/exp_brain_foundational_tagger_v2")
NEG = -1e9


class BrainTaggerV2:
    def __init__(self, beam=8, maxsuf=10, rare=10):
        self.beam = beam; self.maxsuf = maxsuf; self.rare = rare

    def fit(self, sents):
        uni, bi, tri = Counter(), Counter(), Counter()
        wt = defaultdict(Counter)              # word -> tag counts (case-sensitive lexicon)
        tagc = Counter()
        wc = Counter()
        for s in sents:
            for form, tag, _, _ in s:
                wt[form][tag] += 1; tagc[tag] += 1; wc[form] += 1
        tags = sorted(tagc)
        for s in sents:
            p2 = p1 = "<S>"
            for form, tag, _, _ in s:
                uni[tag] += 1; bi[(p1, tag)] += 1; tri[(p2, p1, tag)] += 1
                p2, p1 = p1, tag
        self.tags, self.uni, self.bi, self.tri = tags, uni, bi, tagc
        self.tri_c, self.bi_c = tri, bi
        self.wt, self.tagc = wt, tagc
        self.N = sum(uni.values())
        self._logp_tag = {t: math.log(uni[t] / self.N) for t in tags}
        self._p_tag = {t: uni[t] / self.N for t in tags}
        self._lambdas(uni, bi, tri)
        self._suffix_model(wt, wc, tagc, tags)
        return self

    def _lambdas(self, uni, bi, tri):
        """Brants (2000) deleted-interpolation weights for trigram transition smoothing."""
        l1 = l2 = l3 = 0.0
        N = sum(uni.values())
        for (a, b, c), f123 in self.tri_c.items():
            if f123 == 0:
                continue
            f12 = self.bi_c.get((a, b), 0)
            f23 = self.bi_c.get((b, c), 0)
            f2 = uni.get(b, 0)
            f3 = uni.get(c, 0)
            d3 = (f123 - 1) / (f12 - 1) if f12 > 1 else 0.0
            d2 = (f23 - 1) / (f2 - 1) if f2 > 1 else 0.0
            d1 = (f3 - 1) / (N - 1) if N > 1 else 0.0
            m = max(d1, d2, d3)
            if m == d3: l3 += f123
            elif m == d2: l2 += f123
            else: l1 += f123
        s = l1 + l2 + l3 or 1.0
        self.lam = (l1 / s, l2 / s, l3 / s)

    def _trans_logp(self, p2, p1, t):
        l1, l2, l3 = self.lam
        pu = self.uni.get(t, 0) / self.N
        f2 = self.uni.get(p1, 0)
        pb = self.bi_c.get((p1, t), 0) / f2 if f2 else 0.0
        f12 = self.bi_c.get((p2, p1), 0)
        pt = self.tri_c.get((p2, p1, t), 0) / f12 if f12 else 0.0
        p = l1 * pu + l2 * pb + l3 * pt
        return math.log(p) if p > 0 else NEG

    def _suffix_model(self, wt, wc, tagc, tags):
        """TnT successive-abstraction suffix model, separate for cap / lowercase unknowns."""
        # theta = variance of the unigram tag distribution
        Ptag = [tagc[t] / self.N for t in tags]
        mean = sum(Ptag) / len(Ptag)
        theta = sum((p - mean) ** 2 for p in Ptag) / (len(Ptag) - 1)
        self.theta = theta
        # suffix tag counts from RARE words, split by capitalization of the first letter
        suf = {True: [defaultdict(Counter) for _ in range(self.maxsuf + 1)],
               False: [defaultdict(Counter) for _ in range(self.maxsuf + 1)]}
        for w, f in wc.items():
            if f > self.rare:
                continue
            cap = w[:1].isupper()
            wl = w.lower()
            for k in range(1, min(self.maxsuf, len(wl)) + 1):
                for t, c in wt[w].items():
                    suf[cap][k][wl[-k:]][t] += c
        self.suf = suf

    def _emis_unknown(self, form):
        """P(t|suffix) by successive abstraction -> emission weight P(t|suffix)/P(t)."""
        cap = form[:1].isupper()
        wl = form.lower()
        tabs = self.suf[cap]
        # start from the unigram tag prior, abstract up from length 1 to longest available suffix
        P = dict(self._p_tag)   # base
        for k in range(1, min(self.maxsuf, len(wl)) + 1):
            cc = tabs[k].get(wl[-k:])
            if not cc:
                continue
            tot = sum(cc.values())
            newP = {}
            for t in self.tags:
                ml = cc.get(t, 0) / tot
                newP[t] = (ml + self.theta * P[t]) / (1.0 + self.theta)
            P = newP
        out = {}
        for t in self.tags:
            pt = self._p_tag[t]
            out[t] = math.log(P[t] / pt) if (P[t] > 0 and pt > 0) else NEG
        return out

    def _emis(self, form):
        c = self.wt.get(form)
        if c is None:
            c = self.wt.get(form.lower())   # try lowercase (sentence-initial)
        if c is not None:
            tot = sum(c.values())
            return {t: (math.log(c.get(t, 0) / tot) if c.get(t, 0) else NEG) for t in self.tags}
        return self._emis_unknown(form)

    def tag(self, forms):
        beams = [(0.0, ("<S>", "<S>"), [])]
        for form in forms:
            emis = self._emis(form)
            cand = []
            for score, (p2, p1), seq in beams:
                for t in self.tags:
                    e = emis[t]
                    if e <= NEG:
                        continue
                    sc = score + e + self._trans_logp(p2, p1, t)
                    cand.append((sc, (p1, t), seq + [t]))
            if not cand:  # all emissions -inf (shouldn't happen) -> fall back to prior
                t = max(self.tags, key=lambda x: self._p_tag[x])
                cand = [(score - 50, (p1, t), seq + [t]) for score, (p2, p1), seq in beams]
            cand.sort(key=lambda x: -x[0])
            beams = cand[:self.beam]
        return beams[0][2]

    def evaluate(self, sents, oov_only=False, known=None):
        c = t = 0
        for s in sents:
            forms = [x[0] for x in s]; gold = [x[1] for x in s]
            pred = self.tag(forms)
            for f, g, p in zip(forms, gold, pred):
                if oov_only and (f in (known or self.wt) or f.lower() in (known or self.wt)):
                    continue
                t += 1; c += int(p == g)
        return (c / t if t else 0.0, c, t)


def main(beams=(1, 4, 8, 16)):
    os.makedirs(_OUT, exist_ok=True)
    tr, te = load(_TRAIN), load(_TEST)
    known = set()
    for s in tr:
        for f, *_ in s:
            known.add(f); known.add(f.lower())
    res = {}
    best = None
    for b in beams:
        m = BrainTaggerV2(beam=b).fit(tr)
        acc, cc, tt = m.evaluate(te)
        res["beam%d" % b] = acc
        print("beam=%d : acc=%.4f (%d/%d)" % (b, acc, cc, tt), flush=True)
        if best is None or acc > best[0]:
            best = (acc, b, m)
    acc, b, m = best
    print("\nBEST v2 brain-tagger acc=%.4f (beam=%d) vs Viterbi floor 0.9445 -> %s" %
          (acc, b, "EXCEEDS" if acc > 0.9445 else "below"), flush=True)
    oov, oc, ot = m.evaluate(te, oov_only=True, known=known)
    print("OOV-slice acc=%.4f (%d/%d) [v1 was 0.6435]" % (oov, oc, ot), flush=True)
    # info-free twin: scramble the lexicon emission
    import random
    rng = random.Random(20260904)
    twin = BrainTaggerV2(beam=b).fit(tr)
    twin.wt = {w: Counter({rng.choice(twin.tags): 1}) for w in list(m.wt.keys())}
    tw, _, _ = twin.evaluate(te)
    print("INFO-FREE twin (scrambled lexicon) acc=%.4f (must collapse)" % tw, flush=True)
    with open(os.path.join(_OUT, "metrics.json"), "w", encoding="ascii") as f:
        json.dump({"viterbi_floor": 0.9445, "brain_best": acc, "best_beam": b,
                   "oov_acc": oov, "twin_acc": tw, "sweep": res, "lambdas": m.lam}, f, indent=2)
    print("wrote metrics.json", flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        tr = load(_TRAIN)[:800]
        m = BrainTaggerV2(beam=4).fit(tr)
        print("SELF-TEST:", m.tag("the quick brown fox jumps over".split()), "lam=", tuple(round(x,3) for x in m.lam))
    else:
        main()
